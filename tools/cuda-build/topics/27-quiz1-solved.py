# Chapter 10.1: Quiz 1 solved step by step. Source: the Quiz 1 paper (10 questions) with the official answers, and
# Rakesh's worked solutions. Every answer below was recomputed. Q1 uses the per SM reading of the question (4 FMA per
# cycle per SM), the only reading that lands in an option. Variants of each question follow for practice.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

Q2 = r'''
__global__ void matMulNaive(const float *A, const float *B, float *C, int N) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    if (row < N && col < N) {
        float sum = 0.0f;
        for (int k = 0; k < N; k++) {
            sum += A[row * N + k] * B[k * N + col];
        }
        C[row * N + col] = sum;
    }
}
'''

Q4 = r'''
__global__ void matMul(const float *A, const float *B, float *C, int N) {
    __shared__ float tileA[16][16];
    __shared__ float tileB[16][16];
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    float sum = 0.0f;
    for (int k = 0; k < N / 16; k++) {
        tileA[threadIdx.y][threadIdx.x] = A[row * N + (k * 16 + threadIdx.x)];
        tileB[threadIdx.y][threadIdx.x] = B[(k * 16 + threadIdx.y) * N + col];
        __syncthreads();                  // missing in the quiz: statement a becomes false
        for (int t = 0; t < 16; t++) {
            sum += tileA[threadIdx.y][t] * tileB[t][threadIdx.x];
        }
        __syncthreads();                  // missing in the quiz: statement b becomes false
    }
    C[row * N + col] = sum;
}
'''

Q5 = r'''
__global__ void ValUpdate(float *A, float *B, int width, int height) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int y = blockIdx.y * blockDim.y + threadIdx.y;
    if (x < width && y < height) {
        float val = A[y * width + x];     // a warp reads 32 neighbours: 1 segment
        B[x * height + y] = val;          // a warp writes 2048 floats apart: 32 segments
    }
}
'''

K.code('answers', r'''
# Recompute every Quiz 1 answer
print("Q1:", 4 * 2 * 1.5, "GFLOPS per SM  -> option 2")
N, threads = 1024, 16 * 16
print("Q2:", threads * 2 * N)
print("Q3:", (N // 16) * threads * 2)
print("Q5:", 32, "segments (each thread lands", 2048 * 4, "bytes from its neighbour)")
A = [[1, 2, 1, 0], [0, 1, 3, 1], [2, 0, 1, 2], [1, 1, 0, 1]]
x = [1, 2, 3, 4]
print("Q7:", sum(A[2][j] * x[j] for j in range(4)))
print("Q9:", sum(t for t in range(32) if t % 4 == 1))
print("Q10:", (1 << 20) // 256 * (256 // 32))
''')

K.lesson('paper', 'The paper and the answers', f'''
<p>Quiz 1 had 10 questions on the first half of the course. The official answers, recomputed below, are:</p>
{table(['Q', 'Topic', 'Answer', 'Chapter'], [
    ['1', 'peak FP32 throughput of one SM', '2 (12 GFLOPS)', '1.1, 4.2'],
    ['2', 'global loads per block, naive matmul', '524,288', '5.2'],
    ['3', 'global loads per block, tiled matmul', '32,768', '5.2'],
    ['4', 'races in a tiled kernel without barriers', '3 (both true)', '5.2, 7.2'],
    ['5', '128 byte segments for a transposed store', '32', '3.2'],
    ['6', 'return type of a kernel', '5 (__global__ void)', '1.4'],
    ['7', 'trace a matrix vector kernel', '13', '2.1'],
    ['8', 'memory visible to all SMs for the whole run', '1 (global memory)', '3.1'],
    ['9', 'sum of thread ids in a divergent branch', '120', '6.1'],
    ['10', 'warps launched', '32,768', '2.3']])}
{code('answers')}
''', kw=['Quiz 1', 'answers', 'exam'])

K.lesson('q1', 'Q1, Q6 and Q8: peak, kernels and memory', f'''
<p><b>Q1.</b> 80 SMs, 64 cores each, 1.5 GHz, and "every cycle each SM achieves the peak of 4 FMA operations per cycle". Peak of one SM?</p>
{steps('Q1', [
    'Read the SM statement: one SM does 4 FMA per cycle.',
    'Each FMA = 2 FLOPs, so 8 FLOPs per cycle.',
    '8 × 1.5 × 10⁹ = 12 × 10⁹.',
    eq('12 GFLOPS, inside 10.5 to 12.5: answer 2')])}
{note('The other reading, 4 FMA per core, gives 64 × 4 × 2 × 1.5 = 768 GFLOPS per SM, which matches no option. When a question gives two numbers for the same thing, use the one that describes exactly what is asked (here the SM) and check the options.', 'exam')}
{viz('peak')}
<p><b>Q6.</b> A kernel is marked <code>__global__</code> and must return <code>void</code>: the CPU launches it and continues at once, so there is nobody waiting to receive a value. Results go back through memory. Answer 5.</p>
{table(['Qualifier', 'Runs on', 'Called from'], [
    ['__global__', 'GPU', 'CPU (a launch), must return void'],
    ['__device__', 'GPU', 'GPU code only, any return type'],
    ['__host__', 'CPU', 'CPU (the default)'],
    ['__shared__', 'not a function: a variable in shared memory', '']])}
<p><b>Q8.</b> Global memory is reachable by every SM and keeps its contents until freed or the program ends. Shared memory belongs to one block, and L1 and L2 are caches, not places you allocate. Answer 1.</p>
{viz('memhier')}
''', kw=['Q1', 'peak throughput', 'FMA', 'Q6', '__global__ void', 'Q8', 'global memory'])

K.lesson('q2', 'Q2 to Q4: loads and races in matrix multiply', f'''
{cu('q2_naive.cu', Q2, {7: 'Each pass of the loop loads one A and one B value from global memory.', 9: 'One store per thread.'})}
{steps('Q2: N = 1024, blocks of 16 × 16', [
    'Each thread runs the loop N = 1024 times.',
    'Each pass loads 2 values: 2048 loads per thread.',
    '256 threads per block.',
    eq('256 × 2048 = 524,288 loads per block')])}
{steps('Q3: tiled with 16 × 16 tiles', [
    'The k loop runs N ÷ 16 = 64 phases.',
    'In each phase every thread loads 1 value of A and 1 of B into shared memory.',
    '64 × 256 × 2.',
    eq('32,768 loads per block, 16 times fewer')])}
{viz('tilemm')}
<p><b>Q4.</b> The quiz kernel loads tiles and computes, with no barrier at all.</p>
{cu('q4_fixed.cu', Q4, {8: 'Each thread writes one element of each tile.', 10: 'Without this barrier a thread can start reading tileA[5][3] before thread (5, 3) wrote it. Statement a is true in the quiz.', 14: 'Without this barrier a fast thread starts the next phase and overwrites tileB while slower threads still read it. Statement b is true.'})}
{note('Answer 3: both statements are true for the quiz code, because it has no __syncthreads. The fixed version above needs one barrier after loading and one after computing.', 'exam')}
''', kw=['Q2', 'Q3', 'naive matmul loads', 'tiled matmul loads', 'Q4', '__syncthreads', 'race'])

K.lesson('q5', 'Q5: segments for a transposed store', f'''
{cu('q5.cu', Q5, {5: 'Threads of one warp have x = 0 to 31 and the same y: 32 consecutive floats = 128 bytes = 1 segment.', 6: 'The same threads write B[x × 2048 + y]: neighbours are 2048 floats = 8192 bytes apart, so each one needs its own segment.'})}
{steps('Q5', [
    'A warp is 32 threads with consecutive x and one y.',
    'Store address for thread x: (x × 2048 + y) × 4 bytes.',
    'Neighbouring threads are 8192 bytes apart, far more than 128.',
    eq('32 segments for one warp store')])}
{viz('coalesce')}
<p>The fix is the transpose trick of chapter 3.2: read a tile into shared memory, then write it out row by row, so both the read and the write are coalesced.</p>
''', kw=['Q5', 'coalescing', 'segments', 'transpose', 'column major'])

K.lesson('q7', 'Q7, Q9 and Q10: tracing, divergence and warps', f'''
<p><b>Q7.</b> One thread per row of y = A x. Thread 2 owns row 2.</p>
{viz('matvec')}
<p><b>Q9.</b> With <code>if (tid % 4 == 1)</code>, branch A is taken by tids 1, 5, 9, …, 29.</p>
{steps('Q9', [
    'The tids form 1 + 4k for k = 0 to 7: 8 terms.',
    'Sum of an arithmetic series = terms × (first + last) ÷ 2.',
    '8 × (1 + 29) ÷ 2.',
    eq('120')])}
{viz('diverge')}
<p><b>Q10.</b> N = 2²⁰ threads in blocks of 256.</p>
{steps('Q10', [
    'Blocks = (2²⁰ + 255) ÷ 256 = 4096.',
    'Warps per block = 256 ÷ 32 = 8.',
    '4096 × 8.',
    eq('32,768 warps (the latencies in the question are not needed)')])}
{viz('launch1d')}
''', kw=['Q7', 'matrix vector', 'Q9', 'divergence', 'arithmetic series', 'Q10', 'warps launched'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Read each question twice, then draw one warp or one thread. Most quiz questions are about counting the right thing.</p>',
    '<p>Peak = units × 2 × clock. Naive matmul loads 2N per thread, tiled 2N ÷ T. Segments: look at neighbouring threads. Kernels return void. Warps = blocks × ⌈threads ÷ 32⌉.</p>',
    '<p>Check each answer two ways: by formula and by a tiny Python loop, as in the code above.</p>',
    '<p>The same counting is how researchers model kernels before writing them: count loads, bytes and FLOPs, then place the kernel on the roofline.</p>')}
''', kw=['ladder', 'exam strategy'])

K.quiz('e', 'Return type of a __global__ function', ['int', 'float', 'void', 'any'], 2, 'The CPU does not wait.', 'Kernels return void.')
K.quiz('e', 'Memory reachable by all SMs for the whole program', ['Shared', 'Registers', 'Global', 'L1'], 2, 'Device wide.', 'Global memory.')
K.quiz('e', 'One FMA counts as', ['1 FLOP', '2 FLOPs', '4 FLOPs', '0.5 FLOP'], 1, 'Multiply and add.', '2.')
K.quiz('e', 'Warps for 256 threads', ['4', '8', '16', '32'], 1, '256 ÷ 32.', '8.')
K.quiz('m', 'Naive matmul, N = 1024. Global loads per thread', ['1024', '2048', '32', '64'], 1, 'One A and one B per k.', '2048.')
K.quiz('m', 'Tiled with T = 16 cuts global loads by', ['2 times', '16 times', '256 times', 'Not at all'], 1, 'Each value reused 16 times.', '16.')
K.quiz('m', 'Quiz Q4 code: what fixes statement a?', ['atomicAdd', '__syncthreads() after loading the tiles', 'volatile', 'A bigger tile'], 1, 'Barrier before reading.', 'Everyone writes before anyone reads.')
K.quiz('m', 'Thread ids with tid % 4 == 1 in one warp', ['4', '8', '16', '32'], 1, '1, 5, …, 29.', '8.')
K.quiz('h', 'Q5 load from A uses how many 128 byte segments per warp?', ['1', '4', '32', '2048'], 0, '32 floats in a row.', '128 bytes, aligned.')
K.quiz('h', 'Quiz Q4 code: what fixes statement b?', ['A barrier at the end of each phase', 'Removing the loop', 'printf', 'More registers'], 0, 'Wait before overwriting.', 'Second __syncthreads.')
K.quiz('x', 'Q1 with the per core reading (4 FMA per core) gives per SM', ['12 GFLOPS', '96 GFLOPS', '768 GFLOPS', '61 TFLOPS'], 2, '64 × 4 × 2 × 1.5.', 'Outside every option, so the per SM reading is meant.')
K.quiz('x', 'Q5 with blocks of 16 × 16 (a warp covers 2 rows of 16). Store segments per warp', ['32', '16', '8', '2'], 1, 'Pairs y, y + 1 share a segment.', '16.')

K.calc('e', 'Q1: 4 FMA per cycle per SM at 1.5 GHz. GFLOPS?', '12', '4 × 2 × 1.5.',
       ['8 FLOPs per cycle.', '× 1.5 × 10⁹.', eq('12 GFLOPS')], check=12)
K.calc('e', 'Q10: warps for 2²⁰ threads in blocks of 256?', '32768', 'Blocks × 8.',
       ['4096 blocks.', '× 8 warps.', eq('32,768')], check=32768)
K.calc('e', 'Q7 variant: y[0] with the same A and x?', '8', 'Row 0 · x.',
       ['1·1 + 2·2 + 1·3 + 0·4.', '= 8.', eq('8')], check=8)
K.calc('m', 'Q2 variant: naive, N = 512, blocks of 16 × 16. Loads per block?', '262144', '256 × 2 × 512.',
       ['Per thread 1024 loads.', '× 256 threads.', eq('262,144')], check=262144)
K.calc('m', 'Q3 variant: tiled, N = 512, T = 16. Loads per block?', '16384', '32 phases × 512.',
       ['512 ÷ 16 = 32 phases.', '32 × 256 × 2.', eq('16,384')], check=16384)
K.calc('m', 'Q9 variant: sum of tids with tid % 4 == 3?', '136', '3, 7, …, 31.',
       ['8 terms.', '8 × (3 + 31) ÷ 2.', eq('136')], check=136)
K.calc('m', 'Q10 variant: N = 1,000,000, blocks of 256. Warps?', '31256', '3907 × 8.',
       ['Blocks ⌈10⁶ ÷ 256⌉ = 3907.', '× 8.', eq('31,256 warps')], check=31256)
K.calc('h', 'Q1 variant: 128 cores × 1 FMA × 2 × 1.8 GHz. GFLOPS per SM? (one decimal)', '460.8', 'Multiply.',
       ['128 × 2 = 256 FLOPs per cycle.', '× 1.8 × 10⁹.', eq('460.8 GFLOPS')], check=460.8, tol=0.05)
K.calc('h', 'Naive, N = 1024, blocks of 32 × 32. Loads per block?', '2097152', '1024 × 2048.',
       ['1024 threads.', '× 2048 loads each.', eq('2,097,152')], check=2097152)
K.calc('x', 'Q10 variant: 2²⁰ threads in blocks of 100. Warps launched?', '41944', 'Blocks × ⌈100 ÷ 32⌉.',
       ['Blocks ⌈1,048,576 ÷ 100⌉ = 10,486.', 'Each block needs 4 warps (the last one has 4 threads).', eq('41,944 warps')], check=10486 * 4)
K.calc('x', 'Q9 variant: sum of tids with tid % 8 == 0 in one warp?', '48', '0, 8, 16, 24.',
       ['4 terms.', '0 + 8 + 16 + 24.', eq('48')], check=48)

K.assign('matloads', 'e', 'Loads per block for naive and tiled matmul',
         '<p>Write <code>loads(N, B, tiled)</code> for square blocks of B × B threads. Naive: every thread loads 2N values. Tiled with tile B: every thread loads 2 values per phase, N ÷ B phases. Return the total per block.</p>',
         '''
def loads(N, B, tiled):
    # your code here
    pass
''', [("loads(1024, 16, False)", 524288), ("loads(1024, 16, True)", 32768), ("loads(512, 16, True)", 16384), ("loads(1024, 32, False)", 2097152)],
         '''
def loads(N, B, tiled):
    threads = B * B
    if tiled:
        return threads * 2 * (N // B)
    return threads * 2 * N
''', 'Per thread, then times B².', '<p>The ratio is always B: the tile width.</p>')
K.assign('warpsum', 'm', 'Divergent branch ids and warps',
         '<p>Write <code>branch(mod, r)</code>: the sum of thread ids 0 to 31 with tid % mod == r. Write <code>warps(n, block)</code>: blocks × ⌈block ÷ 32⌉ with enough blocks for n threads. Return both as a list [branch(...), warps(...)] from <code>both(mod, r, n, block)</code>.</p>',
         '''
def both(mod, r, n, block):
    # your code here
    pass
''', [("both(4, 1, 1 << 20, 256)", [120, 32768]), ("both(4, 3, 1000000, 256)", [136, 31256]), ("both(8, 0, 1 << 20, 100)", [48, 41944]), ("both(2, 0, 32, 32)", [240, 1])],
         '''
def both(mod, r, n, block):
    s = sum(t for t in range(32) if t % mod == r)
    blocks = (n + block - 1) // block
    w = blocks * ((block + 31) // 32)
    return [s, w]
''', 'Two ceiling divisions for the warps.', '<p>The first test reproduces Q9 and Q10.</p>')

K.must('Q1', 'Use the statement about the SM: 4 FMA × 2 × 1.5 GHz = 12 GFLOPS, option 2.')
K.must('Q2 and Q3', 'Naive: B² × 2N loads per block (524,288). Tiled: B² × 2 × N/B (32,768).')
K.must('Q4', 'No __syncthreads: both races possible, answer 3. Fix with one barrier after loading and one after computing.')
K.must('Q5 and Q10', 'Column store with stride 2048 floats: 32 segments. Warps = blocks × threads per block ÷ 32 = 32,768.')
K.must('Q6 to Q9', '__global__ void, y[2] = 13, global memory, tids 1 to 29 step 4 sum to 120.')

T = K.topic(
    slug='quiz1-solved', topic='quiz1-solved', step=(10, 'Exam practice', 'gpu-exam', 'Quiz 1 solved, hard problems in the style of top university courses, and a final revision.', 'Pro'),
    title='Quiz 1 solved step by step', short='Quiz 1 solved', badge='10.1', minutes=40,
    lead='All ten Quiz 1 questions worked out with the reasoning, the traps and a widget for each, followed by new variants of every question for practice.',
    desc='Peak throughput of one SM and the two readings of Q1, kernel return types, global memory, global loads in naive and tiled matmul, the missing barriers of Q4, segments for a transposed store, tracing a matrix vector kernel, the sum of divergent thread ids and counting warps.',
    summary='Quiz 1: all ten answers with steps, traps and variants.',
    keywords=['Quiz 1', 'solutions', 'matmul loads', 'segments', 'divergence', 'warps'],
    recap='<p>Quiz 1 is about counting the right thing: FLOPs per cycle, loads per thread, segments per warp, warps per block. Draw one warp, then count.</p>')
