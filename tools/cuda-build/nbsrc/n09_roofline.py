from notebooks import md, code

NB = {'file': '09-measure-your-roofline.ipynb', 'title': 'Measure your own roofline',
      'intro': '''
This notebook goes with chapter 4.2 (roofline) and chapter 8.2 (tensor cores and arithmetic intensity).
You will measure the memory bandwidth and the FP32 compute rate of your GPU with two tiny kernels, draw the roofline
with matplotlib, and place three kernels on it by their arithmetic intensity.

Run it in Google Colab with a T4 GPU. In the simulator (NUMBA_ENABLE_CUDASIM=1) the code runs and draws a chart, but
the numbers are not real, so the cell falls back to the published T4 figures there.
''', 'cells': [
    code('''
import os
import time
import numpy as np
from numba import cuda
import matplotlib.pyplot as plt

SIM = os.environ.get("NUMBA_ENABLE_CUDASIM") == "1"
N = 4_096 if SIM else 1 << 26

def best_ms(fn, reps=5):
    fn()
    cuda.synchronize()
    best = 1e9
    for _ in range(reps):
        t0 = time.perf_counter()
        fn()
        cuda.synchronize()
        best = min(best, (time.perf_counter() - t0) * 1000)
    return best
''', {1: 'The simulator switch.',
      2: 'Wall clock timing.',
      3: 'NumPy.',
      4: 'Numba CUDA.',
      5: 'matplotlib draws the chart.',
      7: 'True in the simulator.',
      8: '67 million floats per array on a GPU.',
      10: 'Best of a few runs in milliseconds.',
      11: 'Warm up and compile.',
      12: 'Wait for the warm up.',
      13: 'Start with a very large best.',
      14: 'Timed runs.',
      15: 'Start the clock.',
      16: 'Run.',
      17: 'Wait for the GPU.',
      18: 'Keep the fastest.',
      19: 'Return it.'}),
    md('''
## 1. Bandwidth: a copy kernel

y[i] = x[i] reads 4 bytes and writes 4 bytes per element and does no maths. Its speed is the memory speed.
'''),
    code('''
@cuda.jit
def copy_kernel(x, y):
    i = cuda.grid(1)
    if i < x.size:
        y[i] = x[i]

d_x = cuda.to_device(np.ones(N, dtype=np.float32))
d_y = cuda.device_array_like(d_x)
ms = best_ms(lambda: copy_kernel[(N + 255) // 256, 256](d_x, d_y))
bw = 8 * N / (ms / 1000) / 1e9
print(f"measured bandwidth: {bw:.0f} GB/s")
''', {1: 'Compile as a kernel.',
      2: 'x in, y out.',
      3: 'Global index.',
      4: 'Bounds check.',
      5: 'One read and one write, nothing else.',
      7: 'Input on the GPU.',
      8: 'Output on the GPU.',
      9: 'Time the copy.',
      10: 'Bytes moved (8 per element) ÷ seconds ÷ 1e9 = GB/s.',
      11: 'A T4 is rated at 320 GB/s. A good copy kernel reaches about 80 to 90 percent of that.'}),
    md('''
## 2. Compute: a kernel that is all FMAs

Each thread runs a long loop of fused multiply adds on values in registers. It reads and writes almost nothing, so its
speed is the compute speed. One FMA counts as 2 FLOPs. Four independent chains let the hardware overlap them.
'''),
    code('''
ITERS = 8 if SIM else 4096

@cuda.jit
def fma_kernel(out):
    i = cuda.grid(1)
    a = np.float32(i) * np.float32(1e-9)
    b, c, d = a + np.float32(1), a + np.float32(2), a + np.float32(3)
    for _ in range(ITERS):
        a = a * np.float32(0.9999) + np.float32(0.0001)
        b = b * np.float32(0.9999) + np.float32(0.0001)
        c = c * np.float32(0.9999) + np.float32(0.0001)
        d = d * np.float32(0.9999) + np.float32(0.0001)
    out[i] = a + b + c + d

T = 1024 * 256 if not SIM else 64
d_o = cuda.device_array(T, dtype=np.float32)
ms = best_ms(lambda: fma_kernel[T // 256 if not SIM else 1, min(T, 256)](d_o))
flops = T * ITERS * 4 * 2
peak = flops / (ms / 1000) / 1e9
print(f"measured FP32 rate: {peak:.0f} GFLOP/s")
''', {1: 'Loop length. Long on a GPU, so the loop dominates the time.',
      3: 'Compile as a kernel.',
      4: 'One output per thread, only so the work is not thrown away.',
      5: 'Global index.',
      6: 'A starting value that differs per thread. np.float32 keeps every value in 32 bit floats.',
      7: 'Three more independent values. Independent chains keep the pipelines full.',
      8: 'The work loop.',
      9: 'One FMA: multiply and add in one instruction, 2 FLOPs.',
      10: 'Second chain.',
      11: 'Third chain.',
      12: 'Fourth chain.',
      13: 'Use all four values, so none of the work can be removed by the compiler.',
      15: '262,144 threads on a GPU, enough to fill every SM many times.',
      16: 'Output array.',
      17: 'Time it. 1024 blocks of 256 threads on a GPU.',
      18: 'Total FLOPs: threads × iterations × 4 chains × 2.',
      19: 'GFLOP/s.',
      20: 'A T4 is rated at about 8,100 GFLOP/s in FP32 at its boost clock.'}),
    md('''
## 3. Draw the roofline

Attainable performance = min(peak, bandwidth × AI). The ridge point peak ÷ bandwidth is the arithmetic intensity
where a kernel stops being memory bound.
'''),
    code('''
if SIM:
    bw, peak = 320.0, 8100.0
ridge = peak / bw
ai = np.logspace(-2, 3, 200)
roof = np.minimum(peak, bw * ai)

kernels = {"vector add": 1 / 12, "SAXPY": 2 / 12, "tiled matmul, TILE 16": 4.0}
plt.figure(figsize=(7, 4.5))
plt.loglog(ai, roof, lw=2, label="roofline")
for name, k_ai in kernels.items():
    plt.scatter([k_ai], [min(peak, bw * k_ai)], zorder=3)
    plt.annotate(name, (k_ai, min(peak, bw * k_ai)), textcoords="offset points", xytext=(6, -12))
plt.axvline(ridge, ls="--", c="grey")
plt.xlabel("arithmetic intensity (FLOP per byte)")
plt.ylabel("GFLOP/s")
plt.title(f"Roofline: {bw:.0f} GB/s, {peak:.0f} GFLOP/s, ridge at {ridge:.1f} FLOP/byte")
plt.legend()
plt.show()
''', {1: 'In the simulator our measurements are not real.',
      2: 'So use the published T4 figures instead.',
      3: 'Ridge point in FLOP per byte. About 25 on a T4.',
      4: '200 intensities from 0.01 to 1000 on a log scale.',
      5: 'The roof: the lower of the compute line and the memory line.',
      7: 'Three kernels and their AI. Vector add: 1 FLOP per 12 bytes. SAXPY: 2 per 12. Tiled matmul with TILE 16 in FP32: 2 × 16 ÷ 8 = 4.',
      8: 'A new figure.',
      9: 'Log scale on both axes, as rooflines are always drawn.',
      10: 'Place each kernel.',
      11: 'Its best possible speed is the roof at its AI.',
      12: 'Label the point.',
      13: 'A dashed line at the ridge point.',
      14: 'Axis label.',
      15: 'Axis label.',
      16: 'The title shows the measured numbers.',
      17: 'The legend.',
      18: 'Draw it.'}),
    md('''
## 4. Try these

1. Work out the AI of the naive matmul in notebook 05 and add it to the chart.
2. Repeat the FMA test with float64. The T4 has far fewer FP64 units. Predict the new ridge point first.
3. Use your bandwidth to predict the time of the copy in notebook 03 with pinned memory. Explain the gap with PCIe.
'''),
]}
