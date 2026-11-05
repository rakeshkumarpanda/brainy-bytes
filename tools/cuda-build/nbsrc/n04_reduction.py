from notebooks import md, code

NB = {'file': '04-parallel-reduction.ipynb', 'title': 'Parallel reduction: summing a million numbers',
      'intro': '''
This notebook goes with chapter 5.1 (reduction) and chapter 7.2 (atomics).
You will add up a long list three ways: one atomic add per element, a tree inside each block in shared memory,
and the same tree with sequential addressing. Each version is checked against NumPy.

Run it in Google Colab with a T4 GPU, or with NUMBA_ENABLE_CUDASIM=1 to step through it slowly on the CPU.
''', 'cells': [
    code('''
import os
import numpy as np
from numba import cuda, float32

SIM = os.environ.get("NUMBA_ENABLE_CUDASIM") == "1"
N = 2_000 if SIM else 1 << 24
TPB = 128 if SIM else 256
x = np.random.default_rng(1).random(N).astype(np.float32)
d_x = cuda.to_device(x)
expected = x.astype(np.float64).sum()
print("N =", N, "threads per block =", TPB, "exact sum =", round(expected, 3))
''', {1: 'The simulator switch.',
      2: 'NumPy for the input and the check.',
      3: 'float32 is the type we use for the shared memory array.',
      5: 'True in the simulator.',
      6: '16.7 million numbers on a GPU, 2000 in the simulator.',
      7: 'Threads per block. The tree below needs a power of two.',
      8: 'Random numbers between 0 and 1 with a fixed seed.',
      9: 'Copy them to the GPU once. Every version reads the same data.',
      10: 'The sum in 64 bit floats on the CPU, our reference.',
      11: 'Prints the setup.'}),
    md('''
## 1. Version A: one atomic add per element

Every thread adds its number to one global total with an atomic add. The answer is right, but all the atomics
hit the same address, so the hardware does them one after another. N additions in a row is the slow serial sum again.
'''),
    code('''
@cuda.jit
def sum_atomic(x, out):
    i = cuda.grid(1)
    if i < x.size:
        cuda.atomic.add(out, 0, x[i])

out = cuda.to_device(np.zeros(1, dtype=np.float32))
sum_atomic[(N + TPB - 1) // TPB, TPB](d_x, out)
print("atomic sum:", out.copy_to_host()[0])
''', {1: 'Compile as a kernel.',
      2: 'x is the input, out is a one element array that holds the total.',
      3: 'Global index.',
      4: 'Bounds check.',
      5: 'Read, add and write out[0] as one step that no other thread can split. Without atomic, updates would be lost (chapter 7.1).',
      7: 'A one element array set to zero on the GPU.',
      8: 'Launch enough blocks to cover N.',
      9: 'Copy the total back. It may differ from NumPy in the last digits because float additions happen in a different order.'}),
    md('''
## 2. Version B: a tree in shared memory

Each block loads its numbers into shared memory, then halves the number of active threads each step:
stride 1, 2, 4 and so on. After log2(TPB) steps thread 0 holds the block\'s sum and adds it to the total with one
atomic. That is N ÷ TPB atomics instead of N.

This first tree uses interleaved addressing (thread t works if t is a multiple of 2 × stride). It is correct, but
active threads are spread over all warps, so most warps diverge.
'''),
    code('''
@cuda.jit
def sum_tree_interleaved(x, out):
    s = cuda.shared.array(TPB, float32)
    t = cuda.threadIdx.x
    i = cuda.grid(1)
    s[t] = x[i] if i < x.size else 0.0
    cuda.syncthreads()
    stride = 1
    while stride < TPB:
        if t % (2 * stride) == 0:
            s[t] += s[t + stride]
        cuda.syncthreads()
        stride *= 2
    if t == 0:
        cuda.atomic.add(out, 0, s[0])
''', {1: 'Compile as a kernel.',
      2: 'Same inputs as before.',
      3: 'A shared memory array with one slot per thread. It is shared by the block and much faster than global memory.',
      4: 'This thread\'s index inside the block.',
      5: 'Global index, for reading x.',
      6: 'Load one number. Threads past the end load 0, which does not change the sum.',
      7: 'Wait until every thread has loaded, before anyone reads a neighbour\'s slot.',
      8: 'The first step adds neighbours 1 apart.',
      9: 'Repeat until the stride reaches the block size.',
      10: 'Only threads at multiples of 2 × stride work in this step.',
      11: 'Add the partner\'s partial sum into my slot.',
      12: 'Every thread waits here, active or not, so the next step sees the finished values. It must not be inside the if.',
      13: 'Double the stride: 1, 2, 4, 8 and so on.',
      14: 'After the loop, slot 0 holds the sum of the whole block.',
      15: 'One atomic per block adds it to the grand total.'}),
    code('''
out = cuda.to_device(np.zeros(1, dtype=np.float32))
sum_tree_interleaved[(N + TPB - 1) // TPB, TPB](d_x, out)
print("tree sum (interleaved):", out.copy_to_host()[0])
''', {1: 'Reset the total to zero.',
      2: 'Launch one block per TPB numbers.',
      3: 'Print the result.'}),
    md('''
## 3. Version C: sequential addressing

Turn the loop around. Start with stride = TPB ÷ 2 and let the first stride threads work. Now the active threads
are packed into the first warps, so whole warps either all work or all rest. There is no divergence until fewer
than 32 threads are active, and the shared memory reads hit different banks.
'''),
    code('''
@cuda.jit
def sum_tree_sequential(x, out):
    s = cuda.shared.array(TPB, float32)
    t = cuda.threadIdx.x
    i = cuda.grid(1)
    s[t] = x[i] if i < x.size else 0.0
    cuda.syncthreads()
    stride = TPB // 2
    while stride > 0:
        if t < stride:
            s[t] += s[t + stride]
        cuda.syncthreads()
        stride //= 2
    if t == 0:
        cuda.atomic.add(out, 0, s[0])

out = cuda.to_device(np.zeros(1, dtype=np.float32))
sum_tree_sequential[(N + TPB - 1) // TPB, TPB](d_x, out)
got = out.copy_to_host()[0]
print("tree sum (sequential):", got, " relative error:", abs(got - expected) / expected)
''', {1: 'Compile as a kernel.',
      2: 'Same inputs.',
      3: 'Shared memory, one slot per thread.',
      4: 'Thread index in the block.',
      5: 'Global index.',
      6: 'Load one number, or 0 past the end.',
      7: 'Wait for all loads.',
      8: 'Start with half the block: thread t adds slot t + TPB ÷ 2.',
      9: 'Continue down to stride 1.',
      10: 'The first stride threads work. They sit next to each other, so whole warps are either busy or idle.',
      11: 'Add the partner from the upper half.',
      12: 'Wait for the step to finish, outside the if.',
      13: 'Halve the stride.',
      14: 'Thread 0 now holds the block sum.',
      15: 'One atomic per block.',
      17: 'Reset the total.',
      18: 'Launch.',
      19: 'Copy the total back.',
      20: 'The relative error should be around 1e-6 or smaller, the normal rounding of 32 bit floats (chapter 4.1).'}),
    md('''
## 4. Count the work

For a block of B threads the tree takes log2(B) steps and B − 1 additions in total, the same work as a serial sum
but in log2(B) steps instead of B − 1. With B = 256: 8 steps, 255 additions.
'''),
    code('''
import math
B = 256
print("steps:", int(math.log2(B)), " additions:", B - 1, " atomics for N = 2^24:", (1 << 24) // B)
''', {1: 'math.log2 gives the number of halving steps.',
      2: 'One block of 256 threads.',
      3: 'Steps, total additions per block, and how many atomics the tree versions need for 16.7 million numbers.'}),
    md('''
## 5. Try these

1. Time all three versions on a GPU. Explain the order with atomics, divergence and bank conflicts.
2. Move the cuda.syncthreads() inside the if in version C. What can go wrong, and why may it still look right sometimes?
3. Let each thread first add 8 numbers with a grid stride loop before the tree. Count the atomics and the steps now.
'''),
]}
