from notebooks import md, code

NB = {'file': '07-streams-overlap.ipynb', 'title': 'Streams: overlap copies with compute',
      'intro': '''
This notebook goes with chapter 6.2 (streams and concurrency).
You will split one big job into chunks, give each chunk its own stream, and let the copy of one chunk overlap with the
kernel of another. Then you will compare the measured time with the pipeline formula: fill + (chunks − 1) × slowest stage + drain.

Overlap needs a real GPU and pinned host memory. In the simulator (NUMBA_ENABLE_CUDASIM=1) the code runs in order and
the result check still works, but the times mean nothing.
''', 'cells': [
    code('''
import os
import time
import numpy as np
from numba import cuda

SIM = os.environ.get("NUMBA_ENABLE_CUDASIM") == "1"
N = 4_096 if SIM else 1 << 26
CHUNKS = 4
h_in = cuda.pinned_array(N, dtype=np.float32)
h_out = cuda.pinned_array(N, dtype=np.float32)
h_in[:] = np.random.default_rng(5).random(N, dtype=np.float32)
print("N =", N, "split into", CHUNKS, "chunks of", N // CHUNKS)
''', {1: 'The simulator switch.',
      2: 'For wall clock timing.',
      3: 'NumPy for the data.',
      4: 'Numba CUDA.',
      6: 'True in the simulator.',
      7: '67 million floats (268 MB) on a GPU.',
      8: 'Number of chunks and streams.',
      9: 'Pinned input. Asynchronous copies only overlap when the host memory is pinned.',
      10: 'Pinned output.',
      11: 'Fill the input with random numbers.',
      12: 'Prints the plan.'}),
    md('''
## 1. A kernel with some real work

We use a kernel that does a few hundred FLOPs per element, so the kernel time is in the same range as the copy time.
That is when overlap helps most.
'''),
    code('''
@cuda.jit
def work(x, y):
    i = cuda.grid(1)
    if i < x.size:
        v = x[i]
        for _ in range(100):
            v = v * 0.999 + 0.001
        y[i] = v

def run_serial():
    d_in = cuda.to_device(h_in)
    d_out = cuda.device_array_like(d_in)
    work[(N + 255) // 256, 256](d_in, d_out)
    d_out.copy_to_host(h_out)
''', {1: 'Compile as a kernel.',
      2: 'x in, y out.',
      3: 'Global index.',
      4: 'Bounds check.',
      5: 'Load the value once into a register.',
      6: 'Repeat a multiply add 100 times, about 200 FLOPs per element, all in registers.',
      7: 'The value slowly moves toward 1.',
      8: 'Store the result.',
      10: 'The plain version: copy everything in, run, copy everything out, one after the other.',
      11: 'Copy the whole input. This call waits until it is done.',
      12: 'Output space on the GPU.',
      13: 'One launch over all N elements.',
      14: 'Copy the result back into the pinned output array. This waits for the kernel first.'}),
    md('''
## 2. The streamed version

Each chunk gets its own stream. Work in one stream runs in order, but different streams may run at the same time.
So while chunk 1 is being copied in, chunk 0 can already be computed.
'''),
    code('''
streams = [cuda.stream() for _ in range(CHUNKS)]
C = N // CHUNKS
d_in = cuda.device_array(N, dtype=np.float32)
d_out = cuda.device_array(N, dtype=np.float32)

def run_streamed():
    for k, s in enumerate(streams):
        lo, hi = k * C, (k + 1) * C
        d_in[lo:hi].copy_to_device(h_in[lo:hi], stream=s)
        work[(C + 255) // 256, 256, s](d_in[lo:hi], d_out[lo:hi])
        d_out[lo:hi].copy_to_host(h_out[lo:hi], stream=s)
    cuda.synchronize()
''', {1: 'One stream per chunk.',
      2: 'Chunk size. N divides evenly by 4 here.',
      3: 'The GPU input array, made once and reused.',
      4: 'The GPU output array.',
      6: 'Queue all the work for all chunks, then wait once at the end.',
      7: 'Chunk k goes to stream s.',
      8: 'The slice of the arrays that belongs to this chunk.',
      9: 'Copy this chunk in, asynchronously in stream s. The call returns at once.',
      10: 'Launch the kernel on this chunk in the same stream. The third launch value is the stream. It starts only after this chunk\'s copy.',
      11: 'Copy this chunk\'s result back in the same stream, after its kernel.',
      12: 'Wait for every stream to finish before we use h_out.'}),
    code('''
def wall_ms(fn, reps=3):
    fn()
    best = 1e9
    for _ in range(reps):
        t0 = time.perf_counter()
        fn()
        cuda.synchronize()
        best = min(best, (time.perf_counter() - t0) * 1000)
    return best

t_serial = wall_ms(run_serial)
ref = h_out.copy()
t_stream = wall_ms(run_streamed)
print("results match:", np.allclose(h_out, ref))
print(f"serial {t_serial:.1f} ms, streamed {t_stream:.1f} ms, speedup {t_serial / max(t_stream, 1e-9):.2f}")
''', {1: 'Best wall clock time of a few runs, in milliseconds.',
      2: 'Warm up, which also compiles the kernel.',
      3: 'Start with a very large best time.',
      4: 'A few timed runs.',
      5: 'Start the clock.',
      6: 'Run the job.',
      7: 'Make sure the GPU is done.',
      8: 'Keep the fastest run.',
      9: 'Return it.',
      11: 'Time the serial version.',
      12: 'Keep its output to compare with.',
      13: 'Time the streamed version.',
      14: 'Both versions must give the same numbers.',
      15: 'The speedup from overlap. On a T4 with 4 chunks it is often around 1.5 to 2.'}),
    md('''
## 3. Compare with the pipeline formula

With three stages (copy in, kernel, copy out) of times a, b, c per chunk and n chunks, the streamed time is about
fill + (n − 1) × slowest + drain = (a + b + c) + (n − 1) × max(a, b, c).
'''),
    code('''
def predict(a, b, c, n):
    return (a + b + c) + (n - 1) * max(a, b, c)

a = b = c = t_serial / 3 / CHUNKS
print(f"if the three stages were equal: predicted {predict(a, b, c, CHUNKS):.1f} ms")
print("chapter 6.2 example, stages 4, 6, 2 ms and 8 chunks:", predict(4, 6, 2, 8), "ms")
''', {1: 'The pipeline formula as a function.',
      2: 'Fill the pipe once, then one slowest stage per remaining chunk.',
      4: 'A rough guess: split the serial time into three equal stages per chunk.',
      5: 'The prediction for that guess. Measure the real stage times with Nsight Systems to do better.',
      6: 'The worked example from the chapter: 12 + 7 × 6 = 54 ms.'}),
    md('''
## 4. Try these

1. Change CHUNKS to 2, 8 and 16. Plot the time against chunks and explain why very many chunks stop helping.
2. Replace the pinned arrays by normal NumPy arrays and run again. Explain the result.
3. Run the streamed version under Nsight Systems (nsys profile python script.py) and find the overlap on the timeline.
'''),
]}
