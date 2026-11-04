# Chapter 5.2: Tiled matrix multiplication. Source: lecture 5 and 6 (tiling, phases, loads per thread, 2n³ ÷ T),
# lecture 7 and 8 (ragged edges with n not a multiple of T, slide 8's "Width²" correction), Quiz 1 questions 2, 3 and
# 4 with Rakesh's worked solutions, workbook 6.1 and 7.1.
# Correction: lecture 7 slide 8 says the plain kernel reads Width² values. Each of the Width² threads reads 2 × Width,
# so the total is 2 × Width³ (2048 times more for Width = 1024, workbook P7.1.4).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

NAIVE = r'''
__global__ void matMulNaive(const float *A, const float *B, float *C, int N) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    if (row < N && col < N) {
        float sum = 0.0f;
        for (int k = 0; k < N; k++)
            sum += A[row * N + k] * B[k * N + col];   // 2 global loads per multiply-add
        C[row * N + col] = sum;
    }
}
'''

TILED = r'''
#define T 16

// Works for any N: tiles that hang over the edge are padded with zeros
__global__ void matMulTiled(const float *A, const float *B, float *C, int N) {
    __shared__ float As[T][T];
    __shared__ float Bs[T][T];
    int tx = threadIdx.x, ty = threadIdx.y;
    int row = blockIdx.y * T + ty;
    int col = blockIdx.x * T + tx;
    float sum = 0.0f;
    for (int p = 0; p < (N + T - 1) / T; ++p) {
        int ka = p * T + tx, kb = p * T + ty;
        As[ty][tx] = (row < N && ka < N) ? A[row * N + ka] : 0.0f;
        Bs[ty][tx] = (kb < N && col < N) ? B[kb * N + col] : 0.0f;
        __syncthreads();                    // tile fully loaded before anyone reads it
        for (int k = 0; k < T; ++k)
            sum += As[ty][k] * Bs[k][tx];
        __syncthreads();                    // everyone done before the next phase overwrites it
    }
    if (row < N && col < N) C[row * N + col] = sum;
}
'''

Q4 = r'''
// Quiz 1 question 4: the tiled kernel WITHOUT barriers (wrong on purpose)
__global__ void matMul(const float *A, const float *B, float *C, int N) {
    __shared__ float tileA[16][16];
    __shared__ float tileB[16][16];
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    float sum = 0.0f;
    for (int k = 0; k < N / 16; k++) {
        tileA[threadIdx.y][threadIdx.x] = A[row * N + (k * 16 + threadIdx.x)];
        tileB[threadIdx.y][threadIdx.x] = B[(k * 16 + threadIdx.y) * N + col];
        for (int t = 0; t < 16; t++)
            sum += tileA[threadIdx.y][t] * tileB[t][threadIdx.x];
    }
    C[row * N + col] = sum;
}
'''

K.code('loads', r'''
# Global loads per block and in total, plain against tiled (Quiz 1 Q2 and Q3)
import math
N, T = 1024, 16
threads = T * T
plain_per_thread = 2 * N
tiled_per_thread = 2 * math.ceil(N / T)
print("plain per block:", threads * plain_per_thread)     # Q2
print("tiled per block:", threads * tiled_per_thread)     # Q3
print("saving factor:", plain_per_thread // tiled_per_thread)
print("total plain:", 2 * N ** 3, "total tiled:", 2 * N ** 3 // T)
''')

K.code('ragged', r'''
# Ragged edges: n not a multiple of T
import math
def tiles(n, T):
    nb = math.ceil(n / T)
    threads = nb * nb * T * T
    return {"phases": nb, "blocks": nb * nb, "threads": threads, "idle": threads - n * n,
            "reads tiled": 2 * n * n * nb, "reads plain": 2 * n ** 3}
print(tiles(5, 4))
print(tiles(33, 32))
''')

K.lesson('naive', 'The plain kernel and its traffic', f'''
<p>One thread computes one element of C = A × B. It walks along a row of A and down a column of B, so it loads 2N values from global memory to do N multiply-adds. Every value of A is loaded N times in total, once by each thread in its row of C.</p>
{cu('matmul_naive.cu', NAIVE, {2: 'y picks the row of C, x picks the column, as in chapter 2.2.', 7: 'A[row × N + k] walks along a row. B[k × N + col] walks down a column, but neighbouring threads have neighbouring col, so that read is coalesced across the warp.', 8: 'One store per thread.'})}
{fxs(
    fx('Loads per thread (plain)', '2<i>N</i>', 'N from A and N from B.', key=True),
    fx('Loads per block (plain)', 'threads per block × 2<i>N</i>', 'Quiz 1 Q2: 256 × 2048 = 524,288.', key=True),
    fx('Total loads (plain)', '2<i>N</i>³', 'Not N² as lecture 7 slide 8 says. For N = 1024 that is 2048 times more.'))}
{note('Lecture 7 slide 8 states the plain kernel reads Width² values. Each of the Width² threads reads 2 × Width values, so the total is 2 × Width³.', 'warn')}
''', kw=['naive matmul', 'loads per thread', 'Quiz 1 question 2', '2N³', 'slide 8 correction'])

K.lesson('tiles', 'Tiles in shared memory', f'''
<p>A block of T × T threads computes a T × T tile of C. In each <b>phase</b> it loads one T × T tile of A and one of B into shared memory, each thread loading one value of each. Then every thread does T multiply-adds from shared memory. Each loaded value is used T times.</p>
{viz('tilemm')}
{fxs(
    fx('Phases', 'phases = ⌈<i>N</i> ÷ <i>T</i>⌉', 'N = 1024, T = 16: 64 phases.', key=True),
    fx('Loads per thread (tiled)', '2 × ⌈<i>N</i> ÷ <i>T</i>⌉', 'One A value and one B value per phase.', key=True),
    fx('Total loads (tiled)', '2<i>N</i>²⌈<i>N</i> ÷ <i>T</i>⌉ = 2<i>N</i>³ ÷ <i>T</i> when T divides N', 'Global traffic drops by a factor of T.', key=True),
    fx('Arithmetic intensity', 'AI ≈ <i>T</i> ÷ 4 (float)', 'Plain matmul has 0.25. T = 16 gives 4.'))}
{steps('Quiz 1 Q3: N = 1024, 16 × 16 tiles, loads per block', [
    '256 threads per block, 64 phases.',
    'Each thread loads 1 value of A and 1 of B per phase: 2 × 64 = 128.',
    '256 × 128.',
    eq('32,768 loads per block, 16 times fewer than 524,288')])}
{code('loads')}
''', kw=['tiling', 'phases', 'shared memory tile', 'Quiz 1 question 3', 'reuse', 'AI T/4'])

K.lesson('sync', 'Two barriers per phase: Quiz 1 question 4', f'''
<p>The tiled loop needs two <code>__syncthreads()</code> per phase. The first makes sure the whole tile is in shared memory before anyone reads it. The second makes sure everyone has finished reading before the next phase overwrites it.</p>
{cu('quiz1_q4.cu', Q4, {9: 'Each thread writes one element of each tile.', 12: 'Thread (5, 10) reads tileA[10][t] for t = 0 to 15, including tileA[10][3], which thread (3, 10) writes. Without a barrier it may read before that write.', 13: 'No barrier here either, so a fast thread can start the next phase and overwrite tileB while slower threads still read it.'})}
{steps('Rakesh\'s worked solution', [
    'Statement a: thread (5, 10) can start the inner loop before thread (5, 3) has written its value. With no barrier nothing stops it, so a can happen: true.',
    'Statement b: thread (3, 12) can overwrite tileB[3][12] for the next k while another thread is still reading it. Also possible: true.',
    eq('Both true: answer 3. The fix is the two barriers in matmul_tiled.cu')])}
{cu('matmul_tiled.cu', TILED, {4: 'This version also handles N that is not a multiple of T.', 11: '⌈N ÷ T⌉ phases.', 13: 'Out of range elements are loaded as 0, so they add nothing to the sum.', 15: 'Barrier 1: the tile must be complete before it is read (statement a).', 18: 'Barrier 2: nobody may overwrite the tile while others still read it (statement b).', 20: 'Only threads inside C write their result.'})}
''', kw=['__syncthreads', 'two barriers', 'Quiz 1 question 4', 'race', 'read after write', 'write after read'])

K.lesson('ragged', 'Ragged edges and tile size limits', f'''
{steps('Workbook 7.1: n = 5 with 4 × 4 tiles', [
    'Phases and blocks per side: ⌈5 ÷ 4⌉ = 2, so 2 × 2 = 4 blocks.',
    'Threads 4 × 16 = 64, of which 64 − 25 = 39 do no output.',
    'Reads tiled 2 × 25 × 2 = 100, plain 2 × 125 = 250.',
    eq('2.5 times fewer reads')])}
{code('ragged')}
{fxs(
    fx('Shared memory for two tiles', 'bytes = 2 × <i>T</i>² × 4', 'T = 32: 8 KB. 48 KB allows T up to 78.'),
    fx('Thread limit', '<i>T</i>² ≤ 1024', 'So T ≤ 32 when each thread computes one output.'))}
<p>With T = 32 on an A100 (19.5 TFLOP/s, 1555 GB/s) a 4096 matrix still needs about 11 ms for memory and 7 ms for maths: memory bound. Faster kernels give each thread several outputs (chapter 8.3).</p>
''', kw=['ragged edges', 'idle threads', 'zero padding', 'tile size limit', 'shared memory per tile'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Instead of every student walking to the library for every book, a group borrows a shelf of books once, and everyone in the group reads them at the table.</p>',
    '<p>Plain: 2N per thread, 2N³ total. Tiled: 2⌈N/T⌉ per thread, 2N³/T total. Two __syncthreads per phase. T ≤ 32 for one output per thread.</p>',
    '<p>Register tiling: each thread computes a 4 × 4 or 8 × 8 block of C, which raises AI far beyond T/4. Double buffering loads the next tile while computing the current one.</p>',
    '<p>CUTLASS splits the work in a hierarchy: thread block tiles, warp tiles, and tensor core fragments, with cp.async or TMA pipelines. cuBLAS reaches 80 to 90 percent of peak this way.</p>')}
''', kw=['ladder', 'register tiling', 'double buffering', 'CUTLASS', 'cuBLAS'])

K.quiz('e', 'Loads per thread in the plain kernel', ['N', '2N', 'N²', '2'], 1, 'Row of A and column of B.', '2N.')
K.quiz('e', 'Each loaded value in a T × T tile is used', ['Once', 'T times', 'T² times', 'N times'], 1, 'Reuse.', 'T threads use it.')
K.quiz('e', 'Phases for N = 1024, T = 16', ['16', '64', '1024', '256'], 1, 'N ÷ T.', '64.')
K.quiz('m', 'Quiz 1 Q2: loads per block, plain, N = 1024, 16 × 16', ['32,768', '262,144', '524,288', '2,048'], 2, '256 × 2048.', '524,288.')
K.quiz('m', 'Quiz 1 Q3: loads per block, tiled', ['32,768', '65,536', '16,384', '524,288'], 0, '256 × 128.', '32,768.')
K.quiz('m', 'Why the second __syncthreads()?', ['To start the kernel', 'So no thread overwrites a tile still being read', 'To load faster', 'It is optional'], 1, 'Write after read.', 'Next phase overwrites the tile.')
K.quiz('m', 'Total loads tiled for n = 512, T = 16', ['16,777,216', '268,435,456', '524,288', '1,048,576'], 0, '2n³ ÷ T.', '2 × 512³ ÷ 16.')
K.quiz('h', 'Quiz 1 Q4 answer (a and b without barriers)', ['1', '2', '3', '4'], 2, 'Both can happen.', 'Both true.')
K.quiz('h', 'n = 33 with 32 × 32 tiles. Share of idle threads', ['3 percent', 'About 73 percent', '50 percent', '0'], 1, '4 blocks, 4096 threads, 1089 outputs.', '3007 ÷ 4096 ≈ 73.4 percent.')
K.quiz('h', 'Largest T for one output per thread', ['16', '32', '64', '78'], 1, 'T² ≤ 1024.', '32.')
K.quiz('x', 'Lecture 7 slide 8 says plain reads = Width². For Width = 1024 the true total is', ['Same', '2048 times more', '1024 times less', '2 times more'], 1, '2W³ ÷ W².', '2W = 2048.')
K.quiz('x', 'n = 4096, T = 32 on an A100. Bound by', ['Maths (7 ms)', 'Memory (about 11 ms)', 'Neither', 'PCIe'], 1, 'Bytes 2n³/T × 4.', '4096³ × 2 ÷ 32 × 4 bytes ÷ 1555 GB/s ≈ 11 ms against 7 ms of maths.')

K.calc('e', 'n = 1024, T = 32. Loads per thread tiled?', '64', '2 × n ÷ T.',
       ['Phases 1024 ÷ 32 = 32.', '2 per phase.', eq('64 (plain 2048)')], check=2 * 1024 // 32)
K.calc('e', 'n = 6 with 2 × 2 tiles. Blocks?', '9', '3 per side.',
       ['Phases ⌈6 ÷ 2⌉ = 3.', 'Blocks 3 × 3.', eq('9 blocks')], check=9)
K.calc('e', 'Quiz 1 Q2: loads per block, plain?', '524288', '256 × 2 × 1024.',
       ['256 threads.', '2048 loads each.', eq('524,288')], check=256 * 2048)
K.calc('m', 'Quiz 1 Q3: loads per block, tiled?', '32768', '256 × 2 × 64.',
       ['64 phases.', '2 loads per phase per thread = 128.', eq('256 × 128 = 32,768')], check=256 * 128)
K.calc('m', 'n = 4, T = 2 (slide 21). Total loads?', '64', '2n³ ÷ T.',
       ['4 blocks × 4 threads × 2 phases × 2 loads.', '= 64.', eq('Check: 2 × 64 ÷ 2 = 64')], check=2 * 4 ** 3 // 2)
K.calc('m', 'n = 1000, T = 16. Tiled reads?', '126000000', '2n²⌈n/T⌉.',
       ['⌈1000 ÷ 16⌉ = 63 phases.', '2 × 10⁶ × 63.', eq('126,000,000 (about 15.9 times fewer than 2 × 10⁹)')], check=2 * 1000 ** 2 * 63)
K.calc('m', 'Largest T allowed by 48 KB of shared memory for two float tiles?', '78', '8T² ≤ 49,152.',
       ['T² ≤ 6144.', '√6144 ≈ 78.4.', eq('T = 78 (but threads limit T to 32)')], check=int((49152 / 8) ** 0.5))
K.calc('h', 'n = 5, 4 × 4 tiles. Idle threads?', '39', '64 − 25.',
       ['2 × 2 blocks of 16 threads = 64.', 'Outputs 25.', eq('39 idle')], check=64 - 25)
K.calc('h', 'n = 33, 32 × 32 tiles. Idle share in percent? (one decimal)', '73.4', '4096 threads.',
       ['4 blocks × 1024 = 4096 threads.', 'Outputs 33² = 1089, idle 3007.', eq('3007 ÷ 4096 = 73.4 percent')], check=100 * (4096 - 1089) / 4096, tol=0.05)
K.calc('h', 'T = 32 on the 530 GFLOP/s, 177 GB/s device: AI = T ÷ 4. Attainable GFLOP/s?', '530', 'min(530, 8 × 177).',
       ['AI 8.', '8 × 177 = 1416 > 530.', eq('530 GFLOP/s, compute bound')], check=min(530, 8 * 177))
K.calc('x', 'n = 4096, T = 32, A100: memory time in ms (one decimal)?', '11.0', 'bytes = 2n³ ÷ T × 4.',
       ['Loads 2 × 4096³ ÷ 32 = 4.295 × 10⁹ floats.', '× 4 bytes = 1.718 × 10¹⁰ bytes ÷ 1555 GB/s.', eq('≈ 11.0 ms (maths ≈ 7.0 ms)')], check=2 * 4096 ** 3 / 32 * 4 / 1555e9 * 1000, tol=0.05)

K.assign('tiledloads', 'e', 'Loads per block',
         '<p>Write <code>loads(N, T, tiled)</code>: global loads of A and B for one T × T block computing a T × T tile of C, plain or tiled.</p>',
         '''
def loads(N, T, tiled):
    # your code here
    pass
''', [("loads(1024, 16, False)", 524288), ("loads(1024, 16, True)", 32768), ("loads(1000, 16, True)", 32256)],
         '''
def loads(N, T, tiled):
    per_thread = 2 * ((N + T - 1) // T) if tiled else 2 * N
    return T * T * per_thread
''', 'Threads per block times loads per thread.', '<p>For N = 1000 there are 63 phases, the last one partly padded with zeros.</p>')
K.assign('mmtile', 'h', 'Tiled matrix multiply in Python',
         '<p>Write <code>matmul_tiled(A, B, T)</code> for square lists of lists of size n (any n). Loop over output tiles and phases like the CUDA kernel, treating values outside the matrix as 0. Return C.</p>',
         '''
def matmul_tiled(A, B, T):
    # your code here
    pass
''', [("matmul_tiled([[1, 2], [3, 4]], [[5, 6], [7, 8]], 1)", [[19, 22], [43, 50]]), ("matmul_tiled([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 2)", [[1, 2, 3], [4, 5, 6], [7, 8, 9]])],
         '''
def matmul_tiled(A, B, T):
    n = len(A)
    C = [[0] * n for _ in range(n)]
    nb = (n + T - 1) // T
    for bi in range(nb):
        for bj in range(nb):
            for p in range(nb):
                for i in range(bi * T, min(n, bi * T + T)):
                    for j in range(bj * T, min(n, bj * T + T)):
                        for k in range(p * T, min(n, p * T + T)):
                            C[i][j] += A[i][k] * B[k][j]
    return C
''', 'Three tile loops, then three element loops limited by n.', '<p>The identity test checks the ragged case n = 3, T = 2.</p>')

K.must('Plain', '2N loads per thread, 2N³ total (not N² as slide 8 says). Q2: 524,288 per block.')
K.must('Tiled', '⌈N/T⌉ phases, 2⌈N/T⌉ loads per thread, 2N³/T total. Q3: 32,768 per block.')
K.must('Barriers', 'Sync after loading the tile and again before the next phase. Q4: without them both a and b happen (answer 3).')
K.must('Ragged', 'Pad out of range loads with 0 and guard the store. n = 5, T = 4: 4 blocks, 39 idle.')
K.must('Limits', 'T² ≤ 1024 threads so T ≤ 32. Shared memory 8T² bytes. AI ≈ T/4.')

T = K.topic(
    slug='tiled-matmul', topic='tiled-matmul', step=(5, 'Parallel patterns', 'gpu-patterns', 'Learn the patterns behind most GPU code: reductions, tiled matrix multiply, stencils, convolution and scans.', 'College'),
    title='Tiled matrix multiplication', short='Tiled matmul', badge='5.2', minutes=55,
    lead='Cut global memory traffic by a factor of T by loading tiles of A and B into shared memory, get the two barriers right, and handle matrices that are not a multiple of the tile size.',
    desc='Plain matmul traffic, Quiz 1 questions 2, 3 and 4, phases and loads per thread, 2N³ ÷ T, the two barriers, ragged edges, tile size limits, and why T = 32 is still memory bound.',
    summary='Plain against tiled loads, Quiz 1 Q2 to Q4, two barriers, ragged edges and tile limits.',
    keywords=['tiled matmul', 'shared memory', 'phases', 'Quiz 1', '__syncthreads', 'ragged edges'],
    recap='<p>Tiling loads each value once per block and reuses it T times, so traffic falls from 2N³ to 2N³/T. Two barriers per phase keep it correct.</p>')
