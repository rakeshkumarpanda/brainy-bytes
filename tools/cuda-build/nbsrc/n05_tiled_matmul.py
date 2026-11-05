from notebooks import md, code

NB = {'file': '05-tiled-matmul.ipynb', 'title': 'Matrix multiply: naive and tiled in shared memory',
      'intro': '''
This notebook goes with chapter 5.2 (tiled matrix multiply) and chapter 8.3 (fast matmul).
You will write C = A × B two ways: one thread per output reading straight from global memory, and the tiled
version that loads TILE × TILE blocks into shared memory. You will check both against NumPy and count the global reads.

Run it in Google Colab with a T4 GPU, or with NUMBA_ENABLE_CUDASIM=1 for a small size on the CPU.
''', 'cells': [
    code('''
import os
import math
import time
import numpy as np
from numba import cuda, float32

SIM = os.environ.get("NUMBA_ENABLE_CUDASIM") == "1"
TILE = 8 if SIM else 16
M, K, N = (24, 16, 32) if SIM else (2048, 2048, 2048)
rng = np.random.default_rng(2)
A = rng.random((M, K)).astype(np.float32)
B = rng.random((K, N)).astype(np.float32)
dA, dB = cuda.to_device(A), cuda.to_device(B)
dC = cuda.device_array((M, N), dtype=np.float32)
print(f"A is {M} x {K}, B is {K} x {N}, TILE = {TILE}")
''', {1: 'The simulator switch.',
      2: 'ceil for the grid size.',
      3: 'To time on the CPU side.',
      4: 'NumPy for the inputs and the check.',
      5: 'float32 is the type of the shared memory tiles.',
      7: 'True in the simulator.',
      8: 'Tile width. 16 × 16 = 256 threads per block on a GPU.',
      9: 'Matrix sizes. C will be M × N and each output needs K multiply adds.',
      10: 'Random generator with a fixed seed.',
      11: 'A has M rows and K columns.',
      12: 'B has K rows and N columns.',
      13: 'Copy both to the GPU.',
      14: 'Space for C on the GPU.',
      15: 'Prints the setup.'}),
    md('''
## 1. Naive: one thread per output, everything from global memory

Thread (row, col) reads a whole row of A and a whole column of B. That is 2K global reads for 2K FLOPs,
an arithmetic intensity of 2K FLOPs ÷ 8K bytes = 0.25 FLOP/byte, far below the ridge point of any GPU.
'''),
    code('''
@cuda.jit
def mm_naive(A, B, C):
    col, row = cuda.grid(2)
    if row < C.shape[0] and col < C.shape[1]:
        acc = 0.0
        for k in range(A.shape[1]):
            acc += A[row, k] * B[k, col]
        C[row, col] = acc
''', {1: 'Compile as a kernel.',
      2: 'A, B in, C out.',
      3: 'cuda.grid(2) gives (x, y). x walks along columns, y along rows, so consecutive threads touch consecutive columns of B and C.',
      4: 'Bounds check on both sides.',
      5: 'The running dot product, kept in a register.',
      6: 'Walk along the shared dimension K.',
      7: 'One multiply add. A[row, k] is the same for the whole warp (a broadcast), B[k, col] is coalesced.',
      8: 'Write the finished output once.'}),
    code('''
threads = (TILE, TILE)
blocks = (math.ceil(N / TILE), math.ceil(M / TILE))
mm_naive[blocks, threads](dA, dB, dC)
print("naive correct:", np.allclose(dC.copy_to_host(), A @ B, rtol=1e-4, atol=1e-3))
''', {1: 'Blocks of TILE × TILE threads.',
      2: 'Columns (N) along x and rows (M) along y.',
      3: 'Launch.',
      4: 'Compare with NumPy. The tolerance allows for float32 rounding over K additions.'}),
    md('''
## 2. Tiled: share each load across a whole block

The block loads a TILE × TILE piece of A and of B into shared memory, waits, multiplies the two tiles, waits again,
and moves to the next pair of tiles. Each number loaded from global memory is now used TILE times, so global reads
drop by a factor of TILE.
'''),
    code('''
@cuda.jit
def mm_tiled(A, B, C):
    sA = cuda.shared.array((TILE, TILE), float32)
    sB = cuda.shared.array((TILE, TILE), float32)
    tx = cuda.threadIdx.x
    ty = cuda.threadIdx.y
    col, row = cuda.grid(2)
    acc = 0.0
    for p in range((A.shape[1] + TILE - 1) // TILE):
        ka = p * TILE + tx
        kb = p * TILE + ty
        sA[ty, tx] = A[row, ka] if row < A.shape[0] and ka < A.shape[1] else 0.0
        sB[ty, tx] = B[kb, col] if kb < B.shape[0] and col < B.shape[1] else 0.0
        cuda.syncthreads()
        for k in range(TILE):
            acc += sA[ty, k] * sB[k, tx]
        cuda.syncthreads()
    if row < C.shape[0] and col < C.shape[1]:
        C[row, col] = acc
''', {1: 'Compile as a kernel.',
      2: 'Same inputs and output.',
      3: 'A shared tile of A, visible to every thread in the block.',
      4: 'A shared tile of B.',
      5: 'Column of this thread inside the tile.',
      6: 'Row of this thread inside the tile.',
      7: 'Global output position, as before.',
      8: 'Running sum in a register.',
      9: 'Phase p covers columns p × TILE to p × TILE + TILE − 1 of A (and the same rows of B). Ceil handles a partial last tile.',
      10: 'Which column of A this thread loads in this phase.',
      11: 'Which row of B this thread loads in this phase.',
      12: 'Each thread loads one value of A into the tile, or 0 when it is outside the matrix, so the sum is unchanged.',
      13: 'Each thread loads one value of B the same way.',
      14: 'Wait until the whole tile is loaded. Without it some threads read slots that are not written yet.',
      15: 'TILE multiply adds, all from fast shared memory.',
      16: 'Row ty of the A tile times column tx of the B tile.',
      17: 'Wait before the next phase overwrites the tiles that slower threads may still be reading.',
      18: 'Only threads that own a real output write it. Note that every thread still took part in the loads and barriers above.',
      19: 'Write the result.'}),
    code('''
mm_tiled[blocks, threads](dA, dB, dC)
C = dC.copy_to_host()
print("tiled correct:", np.allclose(C, A @ B, rtol=1e-4, atol=1e-3))

naive_reads = 2 * M * N * K
tiled_reads = naive_reads // TILE
print(f"global reads, naive: {naive_reads:,}   tiled: {tiled_reads:,}   (factor {TILE})")
''', {1: 'Launch with the same grid as the naive kernel.',
      2: 'Copy C back.',
      3: 'Check against NumPy.',
      5: 'Naive: each of the M × N outputs reads K values of A and K of B.',
      6: 'Tiled: every loaded value is used by TILE threads, so reads drop by TILE.',
      7: 'Shows the counts. With TILE = 16 the tiled kernel reads 16 times less from global memory.'}),
    md('''
## 3. Time both on a GPU

Matrix multiply does 2MNK FLOPs. Dividing by the time gives GFLOP/s, which you can compare with the T4 peak of about
8 TFLOP/s in FP32. Neither kernel gets close. Chapter 8.3 shows the next steps: register tiles, vector loads and tensor cores.
'''),
    code('''
def best_ms(kernel, reps=3):
    kernel[blocks, threads](dA, dB, dC)
    cuda.synchronize()
    t = []
    for _ in range(reps):
        t0 = time.perf_counter()
        kernel[blocks, threads](dA, dB, dC)
        cuda.synchronize()
        t.append((time.perf_counter() - t0) * 1000)
    return min(t)

flops = 2 * M * N * K
for name, k in (("naive", mm_naive), ("tiled", mm_tiled)):
    ms = best_ms(k)
    print(f"{name}: {ms:.2f} ms, {flops / ms / 1e6:.1f} GFLOP/s")
''', {1: 'Helper that returns the best of a few timed runs in milliseconds.',
      2: 'Warm up run, which also compiles the kernel.',
      3: 'Wait for the warm up.',
      4: 'A list of times.',
      5: 'Several runs.',
      6: 'Start the clock.',
      7: 'Launch the kernel.',
      8: 'Wait for it to finish before stopping the clock.',
      9: 'Store the time in milliseconds.',
      10: 'The best run is least disturbed by other work on the machine.',
      12: 'Total FLOPs: M × N outputs, each with K multiplies and K adds.',
      13: 'Time both kernels.',
      14: 'Best time for this kernel.',
      15: 'FLOPs ÷ milliseconds ÷ 1e6 = GFLOP/s. In the simulator the numbers are meaningless.'}),
    md('''
## 4. Try these

1. Change TILE to 8 and 32 on a GPU. Explain the timings with shared memory per block and occupancy.
2. Remove the second cuda.syncthreads(). Find a size where the result goes wrong on a GPU, and explain the race.
3. Work out the arithmetic intensity of the tiled kernel for TILE = 16 in FLOP per byte of global traffic.
'''),
]}
