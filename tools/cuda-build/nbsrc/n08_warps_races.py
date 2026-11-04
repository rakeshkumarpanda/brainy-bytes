from notebooks import md, code

NB = {'file': '08-warps-races-atomics.ipynb', 'title': 'Warps, divergence, races and atomics',
      'intro': '''
This notebook goes with chapters 2.3 (warps), 6.1 (divergence), 7.1 (races) and 7.2 (atomics).
You will see a race lose updates, fix it with an atomic, measure the cost of a divergent branch, and sum a warp with
shuffle instructions.

The race and divergence cells need a real GPU to show the effect. The simulator (NUMBA_ENABLE_CUDASIM=1) runs threads
one at a time, so it hides races, and it has no shuffle instructions. The notebook says so where it matters.
''', 'cells': [
    code('''
import os
import time
import numpy as np
from numba import cuda

SIM = os.environ.get("NUMBA_ENABLE_CUDASIM") == "1"
BLOCKS, TPB = (4, 32) if SIM else (1024, 256)
print("threads in the grid:", BLOCKS * TPB)
''', {1: 'The simulator switch.',
      2: 'To time the divergence test.',
      3: 'NumPy.',
      4: 'Numba CUDA.',
      6: 'True in the simulator.',
      7: 'A large grid on a GPU, a tiny one in the simulator.',
      8: 'How many threads will each try to add 1 to the counter.'}),
    md('''
## 1. A race: counter += 1 from many threads

counter[0] += 1 is three steps: read, add, write. Two threads can read the same old value and both write old + 1, so
one update is lost. An atomic add does the three steps as one.
'''),
    code('''
@cuda.jit
def count_plain(counter):
    counter[0] += 1

@cuda.jit
def count_atomic(counter):
    cuda.atomic.add(counter, 0, 1)

for kernel in (count_plain, count_atomic):
    c = cuda.to_device(np.zeros(1, dtype=np.int32))
    kernel[BLOCKS, TPB](c)
    print(f"{kernel.__name__:13s} counted {c.copy_to_host()[0]:>8d} of {BLOCKS * TPB}")
''', {1: 'Compile as a kernel.',
      2: 'The racy version.',
      3: 'Read, add one, write back. Not safe when many threads do it at once.',
      5: 'Compile as a kernel.',
      6: 'The safe version.',
      7: 'The hardware does read, add and write as one step that no other thread can split.',
      9: 'Run both kernels the same way.',
      10: 'A counter that starts at zero.',
      11: 'Every thread in the grid adds one.',
      12: 'On a GPU the plain version counts far fewer than the number of threads. The simulator runs threads one by one, so both look right there.'}),
    md('''
## 2. The cost of divergence

The 32 threads of a warp run one instruction at a time together. If some take the if branch and others the else
branch, the warp runs both branches one after the other with part of its lanes switched off. If the whole warp takes the
same branch, nothing is wasted.
'''),
    code('''
@cuda.jit
def branchy(out, by_warp):
    i = cuda.grid(1)
    key = (i // 32) if by_warp else i
    v = 0.0
    if key % 2 == 0:
        for k in range(200):
            v += k * 0.5
    else:
        for k in range(200):
            v -= k * 0.25
    out[i] = v

out = cuda.device_array(BLOCKS * TPB, dtype=np.float32)
for by_warp in (False, True):
    branchy[BLOCKS, TPB](out, by_warp)
    cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(20):
        branchy[BLOCKS, TPB](out, by_warp)
    cuda.synchronize()
    ms = (time.perf_counter() - t0) / 20 * 1000
    print("split by warp " if by_warp else "split by thread", f"{ms:.3f} ms")
''', {1: 'Compile as a kernel.',
      2: 'out receives a result per thread. by_warp chooses how threads pick a branch.',
      3: 'Global index.',
      4: 'If by_warp, all 32 threads of a warp share the same key. Otherwise neighbours get different keys.',
      5: 'A value to work on.',
      6: 'Even keys take the first branch.',
      7: 'Some real work, 200 steps.',
      8: 'Add.',
      9: 'Odd keys take the second branch.',
      10: 'The same amount of work.',
      11: 'Subtract.',
      12: 'Store, so the compiler cannot skip the work.',
      14: 'Output array, one value per thread.',
      15: 'Try both ways of splitting.',
      16: 'Warm up launch, which compiles the kernel for this argument type.',
      17: 'Wait for it.',
      18: 'Start the clock.',
      19: 'Twenty launches.',
      20: 'Same launch each time.',
      21: 'Wait for all of them.',
      22: 'Average time per launch.',
      23: 'Split by thread should take about twice as long: every warp runs both branches.'}),
    md('''
## 3. Warp shuffle: sum 32 values without shared memory

shfl_down_sync lets a thread read a register of another thread in the same warp. After five steps (offsets 16, 8, 4,
2, 1) lane 0 holds the sum of the warp. No shared memory and no __syncthreads are needed.
This cell needs a real GPU, because the Numba simulator has no shuffle instructions.
'''),
    code('''
@cuda.jit
def warp_sum(x, out):
    i = cuda.grid(1)
    v = x[i]
    offset = 16
    while offset > 0:
        v += cuda.shfl_down_sync(0xFFFFFFFF, v, offset)
        offset //= 2
    if cuda.laneid == 0:
        out[i // 32] = v

if not SIM:
    xs = np.arange(BLOCKS * TPB, dtype=np.float32)
    sums = cuda.device_array(BLOCKS * TPB // 32, dtype=np.float32)
    warp_sum[BLOCKS, TPB](cuda.to_device(xs), sums)
    print("warp sums match:", np.allclose(sums.copy_to_host(), xs.reshape(-1, 32).sum(axis=1)))
else:
    print("skipped: the simulator has no shuffle instructions")
''', {1: 'Compile as a kernel.',
      2: 'x in, out gets one sum per warp.',
      3: 'Global index.',
      4: 'Each lane holds one value in a register.',
      5: 'First step: add the value from 16 lanes further on.',
      6: 'Five steps: 16, 8, 4, 2, 1.',
      7: 'Read v from lane (my lane + offset) and add it. The mask 0xFFFFFFFF says all 32 lanes take part.',
      8: 'Halve the offset.',
      9: 'laneid is this thread\'s position in its warp, 0 to 31. Lane 0 now holds the full sum.',
      10: 'Write one result per warp.',
      12: 'Only on a real GPU.',
      13: 'Numbers 0, 1, 2 and so on, so the sums are easy to check.',
      14: 'One output per warp.',
      15: 'Launch.',
      16: 'Compare with NumPy, which sums each group of 32.',
      17: 'In the simulator.',
      18: 'Say why the cell did nothing.'}),
    md('''
## 4. Try these

1. In branchy, change the key to (i // 16). Predict the time before you run it.
2. Combine the warp sum with one atomic per warp to sum a whole array. Count the atomics for N = 2 to the power 24.
3. Make the race worse or better by changing the number of blocks. Explain the counts you see.
'''),
]}
