from notebooks import md, code

NB = {'file': '03-memory-and-timing.ipynb', 'title': 'Copies, pinned memory and honest timing',
      'intro': '''
This notebook goes with chapters 1.2 (speedup and Amdahl), 3.1 (memory hierarchy) and 6.2 (streams).
You will time copies between CPU and GPU with CUDA events, compare normal (pageable) and pinned host memory,
and see how the copies decide the real speedup of a fast kernel.

Run it in Google Colab with a T4 GPU. In the simulator (NUMBA_ENABLE_CUDASIM=1) the code runs, but the simulator
says its timings are bogus, so only the steps and the checks mean something there.
''', 'cells': [
    code('''
import os
import numpy as np
from numba import cuda

SIM = os.environ.get("NUMBA_ENABLE_CUDASIM") == "1"
N = 1_000 if SIM else 64 * 1024 * 1024
MB = N * 4 / 1e6
print(f"{N} floats = {MB:.0f} MB per array")
''', {1: 'Reads the simulator switch.',
      2: 'NumPy for the host arrays.',
      3: 'The Numba CUDA module.',
      5: 'True in the simulator.',
      6: '64 million floats (256 MB) on a GPU, so copies take long enough to measure well.',
      7: 'Size of one array in megabytes. Each float is 4 bytes.',
      8: 'Prints the size, so the bandwidth numbers below are easy to check by hand.'}),
    md('''
## 1. Timing with CUDA events

A CUDA event is a time stamp that the GPU itself writes when the work before it in the stream is done.
The time between two events is measured on the GPU, so it does not include Python overhead.
'''),
    code('''
def gpu_time(fn, repeat=5):
    start, stop = cuda.event(), cuda.event()
    fn()
    cuda.synchronize()
    start.record()
    for _ in range(repeat):
        fn()
    stop.record()
    stop.synchronize()
    return max(start.elapsed_time(stop) / repeat, 1e-6)
''', {1: 'A helper that runs fn several times and returns the average time in milliseconds.',
      2: 'Two events, one for the start and one for the end.',
      3: 'One warm up run, so the first time costs (compiling, allocating) are not counted.',
      4: 'Wait until the warm up is done.',
      5: 'Put the start time stamp into the stream.',
      6: 'Run the work repeat times.',
      7: 'Each call queues work on the GPU.',
      8: 'Put the stop time stamp after the work.',
      9: 'Wait until the GPU has reached the stop event.',
      10: 'Time between the events in milliseconds, divided by the number of runs. max keeps it above zero, because the simulator reports 0.'}),
    md('''
## 2. Pageable against pinned host memory

Normal NumPy memory is pageable: the operating system may move it. The GPU copy engine can only read memory that
stays put, so the driver first copies pageable data into a hidden pinned buffer. Pinned (page locked) memory skips
that extra copy, which is why it is faster and is needed for copies that overlap with kernels.
'''),
    code('''
h_pageable = np.ones(N, dtype=np.float32)
h_pinned = cuda.pinned_array(N, dtype=np.float32)
h_pinned[:] = 1.0
d_x = cuda.device_array(N, dtype=np.float32)

t_page = gpu_time(lambda: d_x.copy_to_device(h_pageable))
t_pin = gpu_time(lambda: d_x.copy_to_device(h_pinned))
print(f"pageable to GPU: {t_page:.2f} ms = {MB / t_page:.1f} GB/s")
print(f"pinned to GPU:   {t_pin:.2f} ms = {MB / t_pin:.1f} GB/s")
''', {1: 'A normal NumPy array of ones, in pageable memory.',
      2: 'A pinned host array of the same size. Numba asks the driver for page locked memory.',
      3: 'Fill it with ones too, so both copies move the same data.',
      4: 'One GPU array that both copies write into.',
      6: 'Time copying the pageable array to the GPU.',
      7: 'Time copying the pinned array to the GPU.',
      8: 'MB per millisecond is the same number as GB per second, since both are a factor 1000 apart.',
      9: 'Pinned copies on a T4 over PCIe 3.0 x16 usually reach about 12 GB/s, pageable ones less.'}),
    md('''
## 3. A fast kernel and the cost of the copies

SAXPY computes y = a x + y. It does 2 FLOPs per element and moves 12 bytes (read x, read y, write y).
On the GPU it runs at memory speed. The question is how much the copies eat into that.
'''),
    code('''
@cuda.jit
def saxpy(a, x, y):
    i = cuda.grid(1)
    if i < y.size:
        y[i] = a * x[i] + y[i]

d_y = cuda.device_array(N, dtype=np.float32)
threads = 256
blocks = (N + threads - 1) // threads
t_kernel = gpu_time(lambda: saxpy[blocks, threads](np.float32(2.0), d_x, d_y))
print(f"kernel: {t_kernel:.3f} ms, {3 * MB / t_kernel:.0f} GB/s effective")
''', {1: 'Compile as a kernel.',
      2: 'a is a single number, x and y are arrays.',
      3: 'Global thread index.',
      4: 'Bounds check.',
      5: 'One multiply and one add per element. The result goes back into y.',
      7: 'A second GPU array for y.',
      8: '256 threads per block.',
      9: 'Integer ceil of N ÷ 256.',
      10: 'Time the kernel alone. np.float32 makes sure a is passed as a 32 bit float.',
      11: 'Three arrays of MB megabytes move per launch, so this is the effective bandwidth.'}),
    code('''
t_total = 2 * t_pin + t_kernel + t_pin
share = t_kernel / t_total
print(f"copy x in, copy y in, kernel, copy y out: {t_total:.2f} ms")
print(f"the kernel is only {share * 100:.1f} percent of the total")
print("If only the kernel got 100 times faster, Amdahl says the whole job gets at most",
      f"{1 / ((1 - share) + share / 100):.2f} times faster")
''', {1: 'Total time of the whole job: two copies in, the kernel, one copy out. We use the pinned time for every copy.',
      2: 'The fraction of the time spent in the kernel.',
      3: 'The total for one SAXPY with all its copies.',
      4: 'For memory bound work like this, the copies take most of the time.',
      5: 'Amdahl with the copies as the part that does not speed up: 1 ÷ ((1 − p) + p ÷ 100).',
      6: 'This is why real programs keep data on the GPU across many kernels (chapter 1.2).'}),
    md('''
## 4. Try these

1. Run the copy timing for sizes from 4 KB to 256 MB and plot GB/s against size. Explain the low numbers for small copies with the launch and latency cost.
2. Work out the speedup if x and y were already on the GPU and only y came back.
3. Read chapter 6.2 and split the job into 4 chunks on 4 streams. Predict the time with fill + N × slowest stage + drain.
'''),
]}
