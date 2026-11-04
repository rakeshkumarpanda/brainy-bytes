from notebooks import md, code

NB = {'file': '06-histogram-and-scan.ipynb', 'title': 'Histograms with atomics and a block scan',
      'intro': '''
This notebook goes with chapter 5.5 (scan and histogram) and chapter 7.2 (privatisation).
You will build a histogram of byte values two ways, with global atomics and with a private copy per block in shared
memory, and then write the work efficient Blelloch scan for one block.

Run it in Google Colab with a T4 GPU, or with NUMBA_ENABLE_CUDASIM=1 for small sizes on the CPU.
''', 'cells': [
    code('''
import os
import numpy as np
from numba import cuda, int32

SIM = os.environ.get("NUMBA_ENABLE_CUDASIM") == "1"
N = 3_000 if SIM else 50_000_000
BINS = 256
TPB = 128 if SIM else 256
data = np.random.default_rng(3).integers(0, BINS, N).astype(np.uint8)
d_data = cuda.to_device(data)
ref = np.bincount(data, minlength=BINS)
print("N =", N, " most common value:", ref.argmax(), "seen", ref.max(), "times")
''', {1: 'The simulator switch.',
      2: 'NumPy for the data and the check.',
      3: 'int32 is the type of the shared memory histogram.',
      5: 'True in the simulator.',
      6: 'Fifty million bytes on a GPU, a few thousand in the simulator.',
      7: 'One bin for each byte value 0 to 255.',
      8: 'Threads per block.',
      9: 'Random bytes with a fixed seed. In a real program this could be the pixels of an image.',
      10: 'Copy the data to the GPU.',
      11: 'NumPy counts how often each value appears. This is our reference.',
      12: 'Prints one fact about the data as a sanity check.'}),
    md('''
## 1. Global atomics

Every thread adds 1 to the bin of its byte. Two threads with the same byte would race on a plain += , so we use an
atomic add. With only 256 bins and millions of threads, many atomics hit the same addresses and wait for each other.
'''),
    code('''
@cuda.jit
def hist_global(data, hist):
    i = cuda.grid(1)
    stride = cuda.gridsize(1)
    while i < data.size:
        cuda.atomic.add(hist, data[i], 1)
        i += stride

hist = cuda.to_device(np.zeros(BINS, dtype=np.int32))
blocks = 30 if SIM else 1024
hist_global[blocks, TPB](d_data, hist)
print("global atomics correct:", np.array_equal(hist.copy_to_host(), ref))
''', {1: 'Compile as a kernel.',
      2: 'data in, hist out.',
      3: 'Start index of this thread.',
      4: 'Total threads in the grid, the jump of the grid stride loop.',
      5: 'Loop over this thread\'s share of the data.',
      6: 'Add 1 to the bin whose number is the byte value. Atomic, so no update is lost.',
      7: 'Jump to this thread\'s next element.',
      9: 'A zeroed histogram on the GPU.',
      10: 'A fixed number of blocks. The grid stride loop covers any N with it.',
      11: 'Launch.',
      12: 'array_equal needs every count to match exactly. Integer atomics give exact results.'}),
    md('''
## 2. Privatisation: one histogram per block in shared memory

Each block counts into its own 256 bins in shared memory, where atomics are much cheaper and only the threads of one
block compete. At the end each block adds its 256 counts to the global histogram, so the global atomics drop from N to
256 per block.
'''),
    code('''
@cuda.jit
def hist_private(data, hist):
    local = cuda.shared.array(BINS, int32)
    t = cuda.threadIdx.x
    for b in range(t, BINS, cuda.blockDim.x):
        local[b] = 0
    cuda.syncthreads()
    i = cuda.grid(1)
    stride = cuda.gridsize(1)
    while i < data.size:
        cuda.atomic.add(local, data[i], 1)
        i += stride
    cuda.syncthreads()
    for b in range(t, BINS, cuda.blockDim.x):
        if local[b] > 0:
            cuda.atomic.add(hist, b, local[b])

hist = cuda.to_device(np.zeros(BINS, dtype=np.int32))
hist_private[blocks, TPB](d_data, hist)
print("private histograms correct:", np.array_equal(hist.copy_to_host(), ref))
print("global atomics: before", N, " after at most", blocks * BINS)
''', {1: 'Compile as a kernel.',
      2: 'Same inputs.',
      3: 'The block\'s own 256 counters in shared memory.',
      4: 'Thread index in the block.',
      5: 'Zero the counters. With 128 threads each thread clears 2 bins, with 256 threads one bin.',
      6: 'Set this bin to zero.',
      7: 'All bins must be zero before anyone counts.',
      8: 'Start index for the grid stride loop.',
      9: 'Jump size.',
      10: 'Loop over this thread\'s elements.',
      11: 'Count into shared memory. Still atomic, because threads of the same block can see the same byte.',
      12: 'Next element.',
      13: 'All counting must finish before the block reads its counters.',
      14: 'Each thread takes a few bins again.',
      15: 'Skip empty bins, which saves atomics.',
      16: 'Add the block\'s count to the global histogram. One atomic per bin per block.',
      18: 'A fresh zeroed histogram.',
      19: 'Launch with the same shape.',
      20: 'Check against NumPy.',
      21: 'The saving in global atomics. On a GPU this is where the speedup comes from.'}),
    md('''
## 3. The Blelloch scan in one block

An exclusive scan turns [3, 1, 7, 0] into [0, 3, 4, 11]: each output is the sum of everything before it.
The up sweep builds partial sums in a tree. Then we put 0 at the root, and the down sweep pushes sums back down.
Total work is 2(n − 1) additions, compared with n log2 n for the simpler Hillis and Steele scan.
'''),
    code('''
SCAN_N = 16 if SIM else 1024

@cuda.jit
def blelloch(x, out):
    s = cuda.shared.array(SCAN_N, int32)
    t = cuda.threadIdx.x
    s[2 * t] = x[2 * t]
    s[2 * t + 1] = x[2 * t + 1]
    offset = 1
    d = SCAN_N // 2
    while d > 0:
        cuda.syncthreads()
        if t < d:
            a = offset * (2 * t + 1) - 1
            b = offset * (2 * t + 2) - 1
            s[b] += s[a]
        offset *= 2
        d //= 2
    if t == 0:
        s[SCAN_N - 1] = 0
    d = 1
    while d < SCAN_N:
        offset //= 2
        cuda.syncthreads()
        if t < d:
            a = offset * (2 * t + 1) - 1
            b = offset * (2 * t + 2) - 1
            tmp = s[a]
            s[a] = s[b]
            s[b] += tmp
        d *= 2
    cuda.syncthreads()
    out[2 * t] = s[2 * t]
    out[2 * t + 1] = s[2 * t + 1]
''', {1: 'Scan size. One block of SCAN_N ÷ 2 threads handles it, each thread owns two values.',
      3: 'Compile as a kernel.',
      4: 'x in, out gets the exclusive scan.',
      5: 'The working array in shared memory.',
      6: 'Thread index.',
      7: 'Each thread loads two values: positions 2t ...',
      8: '... and 2t + 1.',
      9: 'Distance between the two children in the tree. It doubles each level of the up sweep.',
      10: 'Number of working threads on the first level: half the elements.',
      11: 'Up sweep: one level per pass, until one thread is left.',
      12: 'Wait for the previous level (and for the loads on the first pass).',
      13: 'Only the first d threads work on this level.',
      14: 'Index of the left child.',
      15: 'Index of the right child, which becomes the parent.',
      16: 'The parent gets the sum of both children.',
      17: 'Children are twice as far apart on the next level.',
      18: 'Half as many threads work on the next level.',
      19: 'After the up sweep the last slot holds the total.',
      20: 'Replace it by 0, the identity of addition. This is what makes the scan exclusive.',
      21: 'Down sweep: start with one working thread.',
      22: 'Go until every pair has been visited.',
      23: 'Children get closer on each level going down.',
      24: 'Wait for the previous level.',
      25: 'Only d threads work.',
      26: 'Left child index.',
      27: 'Right child index, which holds the value coming down from above.',
      28: 'Keep the left child\'s sum.',
      29: 'The left child gets what came from above.',
      30: 'The right child gets what came from above plus the old left sum.',
      31: 'Twice as many threads on the next level.',
      32: 'Wait for the last level before writing out.',
      33: 'Each thread writes its two results.',
      34: 'Second result.'}),
    code('''
xs = np.random.default_rng(4).integers(0, 10, SCAN_N).astype(np.int32)
d_out = cuda.device_array(SCAN_N, dtype=np.int32)
blelloch[1, SCAN_N // 2](cuda.to_device(xs), d_out)
scan = d_out.copy_to_host()
print("input :", xs[:8], "...")
print("output:", scan[:8], "...")
print("matches NumPy:", np.array_equal(scan, np.concatenate(([0], np.cumsum(xs)[:-1]))))
print("additions: Blelloch", 2 * (SCAN_N - 1), " Hillis and Steele", SCAN_N * int(np.log2(SCAN_N)) - (SCAN_N - 1))
''', {1: 'Small random whole numbers, easy to check by eye.',
      2: 'Space for the result.',
      3: 'One block with SCAN_N ÷ 2 threads.',
      4: 'Copy the result back.',
      5: 'The first inputs.',
      6: 'The first outputs. Each is the sum of all the inputs before it.',
      7: 'The exclusive scan in NumPy: a 0 followed by the running sum without its last value.',
      8: 'Work of the two scans. Hillis and Steele does n log2 n − (n − 1) additions, Blelloch 2(n − 1).'}),
    md('''
## 4. Try these

1. Turn the exclusive scan into an inclusive one with one extra line.
2. Use the scan to do stream compaction: keep only the even numbers of an array, in order.
3. Time hist_global and hist_private on a GPU for data that is all the same byte. Explain why global atomics get much slower.
'''),
]}
