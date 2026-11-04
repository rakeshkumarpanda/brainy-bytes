# Chapter 8.3: How fast matmul kernels are built. Source: the matmul blog recommended in lecture 9 (Aleksa Gordic,
# "Inside NVIDIA GPUs: Anatomy of high performance matmul kernels") as explained in the L9 to L12 notes: the H100
# machine, memory hierarchy, speed of light and throttling, PTX and SASS, the naive kernel and the 13 times access order
# effect, the H100 roofline, tile intensity, warp tiling, TMA, swizzling, wgmma, pipelines and the performance ladder.
# Workbook 9.4.4, 9.4.5 and 9.8. Correction from the notes: the ridge is about 378 with the numbers used (the blog
# quotes about 410 with slightly different specs).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

NAIVE = r'''
__global__ void matmul_fast_order(const float *A, const float *B, float *C, int N) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;     // neighbouring threads take neighbouring columns
    if (row < N && col < N) {
        float acc = 0.0f;
        for (int k = 0; k < N; ++k)
            acc += A[row * N + k] * B[k * N + col];       // B along a row: coalesced
        C[row * N + col] = acc;
    }
}

__global__ void matmul_slow_order(const float *A, const float *B, float *C, int N) {
    int row = blockIdx.x * blockDim.x + threadIdx.x;     // neighbouring threads take neighbouring rows
    int col = blockIdx.y * blockDim.y + threadIdx.y;
    if (row < N && col < N) {
        float acc = 0.0f;
        for (int k = 0; k < N; ++k)
            acc += A[row * N + k] * B[k * N + col];       // A with a stride of N: not coalesced
        C[row * N + col] = acc;
    }
}
'''

THREADTILE = r'''
// Inner loop of a thread tile: each thread keeps TM x TN results in registers
template <int TM, int TN>
__device__ void thread_tile(const float *As, const float *Bs, float acc[TM][TN],
                            int ty, int tx, int BK, int BM, int BN) {
    float a[TM], b[TN];
    for (int k = 0; k < BK; ++k) {
        for (int i = 0; i < TM; ++i) a[i] = As[k * BM + ty * TM + i];   // A is stored transposed in shared memory
        for (int j = 0; j < TN; ++j) b[j] = Bs[k * BN + tx * TN + j];
        for (int i = 0; i < TM; ++i)
            for (int j = 0; j < TN; ++j)
                acc[i][j] += a[i] * b[j];                               // TM x TN FMAs from TM + TN loads
    }
}
'''

SWIZZLE = r'''
// 128 byte swizzle: XOR the row within a group of 8 rows (bits 7 to 9) into the 16 byte chunk index (bits 4 to 6)
__device__ __forceinline__ unsigned swizzle128(unsigned byte_offset) {
    unsigned row8 = (byte_offset >> 7) & 7;
    return byte_offset ^ (row8 << 4);
}
'''

K.code('tiles', r'''
# Arithmetic intensity of a BM x BN output tile with b bytes per number
def tile_ai(bm, bn, b):
    return 2 / b * bm * bn / (bm + bn)
for bm, bn, b in ((32, 32, 4), (64, 64, 4), (128, 128, 4), (128, 256, 4), (128, 128, 2)):
    ai = tile_ai(bm, bn, b)
    print(bm, "x", bn, "bytes", b, " AI", round(ai, 1), " reach at 2 TB/s:", round(ai * 2, 1), "TFLOP/s")
print("BF16 ridge:", 756 / 2.0, " square tile needed:", 2 * 756 / 2.0)
''')

K.code('naive', r'''
# The naive kernel on an H100 PCIe (114 SMs), N = 4096, 32 x 32 threads per block
N, sms = 4096, 114
blocks = (N // 32) ** 2
per_sm = min(65536 // (32 * 1024), 2048 // 1024)    # register limit and thread limit
waves = blocks / (sms * per_sm)
flops = 2 * N ** 3
print("blocks:", blocks, " per SM:", per_sm, " waves:", round(waves, 1))
print("time at 3171 GFLOP/s:", round(flops / 3171e9 * 1000), "ms")
print("time at  243 GFLOP/s:", round(flops / 243e9 * 1000), "ms")
''')

K.lesson('machine', 'The H100 and its speed of light', f'''
<p>The blog that lecture 9 recommends builds a matmul for the H100 step by step. First, the machine.</p>
{table(['Part', 'H100 SXM5'], [
    ['SMs', '132 (the full chip has 144, some are switched off)'],
    ['Each SM', '4 quadrants, each with a warp scheduler, FP32 units, a tensor core and load and store units'],
    ['Warps issuing per clock', '4 per SM (one per quadrant), out of up to 64 resident'],
    ['Registers', '64K 32 bit registers per SM'],
    ['Shared memory and L1', 'up to 228 KB per SM, the same SRAM split by configuration'],
    ['L2', '50 MB, shared by all SMs'],
    ['HBM3', '80 GB at about 3.35 TB/s']])}
<p>Only 4 warps per SM issue in a given clock, but 64 can wait their turn. The extra warps hide memory latency, as in the scheduling chapter. A block should have at least 4 warps so all four schedulers have work.</p>
<p>Why the memory pyramid exists: SRAM (registers, caches) needs 6 transistors per bit, so it is fast but small. DRAM needs one transistor and one capacitor per bit, so it is dense, cheap and slow. Opening a DRAM row is the expensive part, and reading neighbouring columns of an open row is cheap. That is the physical reason for coalescing.</p>
{viz('memhier')}
{steps('Workbook 9.4: H100 SXM5 BF16 peak', [
    'Tensor cores: 132 × 4 = 528.',
    'Each does 512 BF16 FMAs = 1024 FLOPs per clock.',
    '528 × 1024 × 1.83 × 10⁹.',
    eq('≈ 989 TFLOP/s')])}
{note('Under a heavy matmul the H100 reaches its 700 W power limit and lowers its clock. At 1.5 GHz the peak is 989 × 1.5 ÷ 1.83 ≈ 811 TFLOP/s, so a kernel at 750 TFLOP/s is at about 92.5 percent of what is reachable.', 'tip')}
''', kw=['H100', 'SM quadrants', 'resident warps', 'memory hierarchy', 'SRAM', 'DRAM', 'speed of light', 'power throttling'])

K.lesson('naive', 'The naive kernel and a 13 times lesson', f'''
<p>One thread per output, blocks of 32 × 32 threads, N = 4096. The only difference between the two kernels below is which index the x thread number feeds.</p>
{cu('naive.cu', NAIVE, {3: 'Threads next to each other in a warp take columns next to each other.', 7: 'B[k * N + col] is read at consecutive addresses across the warp, and A[row * N + k] is the same address for the whole warp: both are cheap.', 8: 'The writes to C are consecutive too.', 13: 'Now neighbouring threads take neighbouring rows.', 18: 'A[row * N + k] jumps N floats between neighbouring threads, so every thread needs its own memory sector.'})}
{viz('coalesce')}
{code('naive')}
{table(['Kernel', 'Measured on H100', 'Time for 2 × 4096³ FLOPs'], [
    ['x feeds the column (coalesced)', '3171 GFLOP/s', '43 ms'],
    ['x feeds the row (uncoalesced)', '243 GFLOP/s', '565 ms, 13 times slower']])}
<p>One line of index arithmetic costs 13 times. The rule from the coalescing chapter: what matters is what <b>neighbouring threads</b> read at the same moment, not what one thread reads over time.</p>
{deep('Tile quantisation and PTX against SASS', '<p>A 33 × 33 matrix with 32 × 32 tiles needs 2 × 2 tiles: 4096 threads for 1089 outputs, so 73 percent of threads do nothing. In the SASS of the naive kernel, ptxas unrolled the loop 16 times and moved all loads to the top so they overlap with the FMAs. Researchers have gained 15 percent by rewriting SASS by hand to avoid bank conflicts.</p>')}
''', kw=['naive matmul', 'coalescing', 'index order', '3171 GFLOP/s', '243 GFLOP/s', 'tile quantisation', 'SASS'])

K.lesson('tiles', 'Tiles: more work per byte', f'''
<p>The naive kernel has an arithmetic intensity of 0.25 (2 FLOPs per 8 bytes loaded). It reaches 3.17 TFLOP/s only because the caches serve repeated loads. To get further, each block keeps a tile of A and of B in shared memory and reuses them.</p>
{fxs(
    fx('Intensity of a BM × BN tile', 'AI = (2 ÷ b) × B<sub>M</sub>B<sub>N</sub> ÷ (B<sub>M</sub> + B<sub>N</sub>)', 'b = bytes per number. BK cancels, so only the tile shape matters.', key=True),
    fx('Square is best', 'B<sub>M</sub> + B<sub>N</sub> ≥ 2√(B<sub>M</sub>B<sub>N</sub>)', 'For a fixed area the sum is smallest when B<sub>M</sub> = B<sub>N</sub> (AM-GM).'),
    fx('Square FP32 tile T × T', 'AI = T ÷ 4', '32 × 32: 8. 128 × 128: 32. BF16 doubles these: AI = T ÷ 2.', key=True))}
{viz('tileai')}
{code('tiles')}
<p><b>Thread tiling.</b> The same idea one level down: each thread keeps a TM × TN block of results in registers. Per k step it loads TM + TN numbers from shared memory and does TM × TN FMAs.</p>
{cu('thread_tile.cu', THREADTILE, {2: 'TM and TN are fixed at compile time so the arrays stay in registers.', 7: 'A is stored transposed in shared memory so these reads are contiguous and can use 128 bit loads.', 9: 'An outer product of a column of A and a row of B.', 11: 'TM × TN FMAs for TM + TN loads. 8 × 8 gives 64 FMAs for 16 loads.'})}
<p>The blog's best kernel before tensor cores uses 128 × 128 block tiles with BK = 16, thread tiles of results in registers, 128 bit loads, and two __syncthreads() per k step. This is warp tiling. It reaches about 32 TFLOP/s on the H100, the best the plain FP32 cores manage in the blog, and far below what tensor cores offer.</p>
{note('With the numbers used here (756 TFLOP/s BF16 on the PCIe card, 2.0 TB/s) the ridge is about 378 FLOP/byte. The blog quotes about 410 with slightly different specs. Either way a kernel needs hundreds of FLOPs per DRAM byte, so tiles must also be reused through L2 and shared memory.', 'exam')}
''', kw=['tiling', 'tile intensity', 'AM-GM', 'square tile', 'thread tiling', 'warp tiling', 'register blocking', 'H100 roofline'])

K.lesson('hopper', 'Hopper tricks: TMA, swizzling, wgmma, pipelines', f'''
<p><b>TMA</b> (tensor memory accelerator) is a copy engine inside each SM. One thread asks it to move a whole 64 × 64 tile from global to shared memory. A barrier in shared memory counts the bytes that arrive, so the waiting threads continue only when the whole tile has landed.</p>
<p><b>Swizzling</b> solves bank conflicts. A 128 byte row is 8 chunks of 16 bytes, and each chunk covers 4 banks. Reading one column of 8 rows hits the same 4 banks 8 times. Store chunk c of row r in slot c XOR r instead, and the column spreads over all 8 slots.</p>
{viz('swizzle')}
{cu('swizzle.cu', SWIZZLE, {3: 'Bits 7 to 9 of the byte offset give the row inside a group of 8 rows of 128 bytes.', 4: 'XOR the row into bits 4 to 6, the index of the 16 byte chunk. Applying it twice gives back the original offset.'})}
{steps('Worked XOR example', [
    'Row 5, chunk 2: 010 XOR 101 = 111 = 7, stored in slot 7.',
    'Row 5, chunk 7: 111 XOR 101 = 010 = 2.',
    'So chunks 2 and 7 of row 5 swap places.',
    eq('XOR with a fixed value is its own inverse')])}
<p><b>wgmma.</b> On Hopper a warp group (4 warps, 128 threads) issues asynchronous tensor core instructions of shape m64nNk16. A 64 × 64 output needs four m64n64k16 calls for K = 64, and the accumulator is spread as 64 × 64 ÷ 128 = 32 FP32 registers per thread.</p>
<p><b>Producer and consumer pipeline.</b> One warp group only issues TMA loads into a ring of shared memory buffers. One or two other warp groups only run tensor core maths. Two barriers per buffer (full and empty) keep them in step. This is the stream overlap idea from chapter 6.2, inside one SM.</p>
{table(['Trick', 'What it fixes'], [
    ['Persistent kernel', 'one long lived block per SM loops over tiles, so stores overlap the next loads and no wave is half empty'],
    ['Hilbert curve order of tiles', 'neighbouring SMs use the same strips of A and B, so L2 hits go up'],
    ['Thread block clusters and multicast', '2 SMs share loaded tiles through distributed shared memory'],
    ['Two consumer warp groups', 'a 128 × 256 tile without running out of registers']])}
''', kw=['TMA', 'swizzle', 'XOR', 'bank conflicts', 'wgmma', 'warp group', 'producer consumer', 'mbarrier', 'persistent kernel', 'Hilbert curve', 'clusters'])

K.lesson('ladder', 'The performance ladder', f'''
<p>Each step fixes one bottleneck. Step through the numbers reported in the blog for BF16 on an H100.</p>
{viz('mmladder')}
<p>The biggest jump, from 32 to 317 TFLOP/s, is simply using tensor cores fed by TMA. Everything after that keeps the tensor cores busy: bigger tiles (higher AI), overlap (pipelines), no idle SMs (persistent kernels), better cache reuse (clusters, Hilbert order) and cheaper waiting (faster barriers). The final 764 TFLOP/s is about 77 percent of the 989 peak, on par with cuBLAS.</p>
{table(['Course idea', 'Where it shows up in the ladder'], [
    ['Coalescing (3.2)', 'the 13 times gap of the naive kernel'],
    ['Shared memory and banks (3.3)', 'tiles and swizzling'],
    ['Tiled matmul (5.2)', 'block tiles, warp tiles, thread tiles'],
    ['Occupancy and waves (2.4, 8.2)', 'persistent kernels'],
    ['Streams and overlap (6.2)', 'producer and consumer pipelines'],
    ['Barriers (7.2)', 'mbarrier and faster barriers'],
    ['Tensor cores (8.2)', 'the 10 times jump']])}
''', kw=['performance ladder', 'cuBLAS', '764 TFLOP/s', 'optimisation steps', 'summary of the course'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Build the fastest kitchen: first stop the waiter running back and forth (coalescing), then keep ingredients on the counter (tiles), then hire the stamping machine (tensor cores), then make sure it never waits (pipelines).</p>',
    '<p>Naive coalesced 43 ms, uncoalesced 565 ms. Tile AI = (2 ÷ b) B<sub>M</sub>B<sub>N</sub> ÷ (B<sub>M</sub> + B<sub>N</sub>). H100 BF16 peak 989, ridge about 378. Swizzle slot = chunk XOR row.</p>',
    '<p>Profile each step in Nsight Compute: memory throughput, bank conflicts, tensor core utilisation, stall reasons. Change one thing at a time and keep the numbers.</p>',
    '<p>CUTLASS 3 and CuTe describe layouts and swizzles as algebra. ThunderKittens, Triton and FlashAttention 3 apply the same Hopper tricks. Blackwell moves accumulators into tensor memory with tcgen05.</p>')}
''', kw=['ladder', 'CUTLASS', 'CuTe', 'ThunderKittens', 'FlashAttention 3', 'tcgen05'])

K.quiz('e', 'How many warps per H100 SM can issue an instruction in one clock?', ['1', '4', '32', '64'], 1, 'One per quadrant.', 'Up to 64 can be resident.')
K.quiz('e', 'The naive kernel becomes 13 times slower when', ['The block size changes', 'Neighbouring threads take neighbouring rows instead of columns', 'N doubles', 'FP16 is used'], 1, 'Coalescing.', 'Stride N between threads.')
K.quiz('e', 'A square FP32 tile T × T has AI', ['T', 'T ÷ 2', 'T ÷ 4', '4T'], 2, '2T² ÷ (4 × 2T).', 'T ÷ 4.')
K.quiz('m', 'For a fixed tile area, the best shape is', ['Long and thin', 'Square', 'One row', 'Any'], 1, 'AM-GM.', 'B_M + B_N is smallest when equal.')
K.quiz('m', 'What does TMA do?', ['Runs tensor maths', 'Copies whole tiles between global and shared memory asynchronously', 'Schedules warps', 'Compresses data'], 1, 'Copy engine.', 'Inside each SM.')
K.quiz('m', 'Swizzled slot for row 5, chunk 2', ['2', '5', '7', '3'], 2, '2 XOR 5.', '010 XOR 101 = 111.')
K.quiz('m', 'Biggest single jump in the ladder', ['Hilbert schedule', 'Tensor cores with TMA', 'Async stores', 'Clusters'], 1, '32 to 317.', 'About 10 times.')
K.quiz('h', 'A wgmma warp group is', ['1 warp', '2 warps', '4 warps (128 threads)', '8 warps'], 2, 'Hopper.', '128 threads.')
K.quiz('h', 'Why is DRAM slow and dense while SRAM is fast and small?', ['Different voltages', 'DRAM uses 1 transistor and 1 capacitor per bit, SRAM 6 transistors', 'DRAM is further away only', 'SRAM is magnetic'], 1, 'Cell design.', 'Dense cells are slower to read.')
K.quiz('h', 'Why does the naive kernel reach 3.17 TFLOP/s with a nominal AI of 0.25?', ['Tensor cores', 'L1 and L2 caches serve many repeated loads', 'Measurement error', 'FP16'], 1, 'Reuse.', 'Effective DRAM AI about 1.6.')
K.quiz('x', 'In the producer and consumer pipeline the producer warp group', ['Does all the maths', 'Only issues TMA loads into a ring of buffers', 'Writes C', 'Waits for the CPU'], 1, 'Specialised roles.', 'Consumers only do tensor core maths.')
K.quiz('x', 'A Hilbert curve tile order helps because', ['It reduces FLOPs', 'Neighbouring SMs reuse the same A and B strips from L2', 'It removes barriers', 'It avoids swizzling'], 1, 'Locality.', 'More L2 hits.')

K.calc('e', 'H100: 132 SMs × 4 TCs × 1024 FLOPs per clock × 1.83 GHz. TFLOP/s? (nearest whole)', '989', 'Multiply.',
       ['528 tensor cores.', '528 × 1024 × 1.83 × 10⁹.', eq('≈ 989 TFLOP/s')], check=round(528 * 1024 * 1.83 / 1000))
K.calc('e', '64 × 64 FP32 tile. AI?', '16', 'T ÷ 4.',
       ['2 × 64 × 64 ÷ (4 × 128).', '= 16.', eq('16 FLOP/byte, 32 TFLOP/s at 2 TB/s')], check=16)
K.calc('e', 'Naive kernel, N = 4096, 32 × 32 blocks. Number of blocks?', '16384', '(4096 ÷ 32)².',
       ['128 × 128.', '= 16,384.', eq('16,384 blocks')], check=16384)
K.calc('m', '128 × 256 FP32 tile. AI? (one decimal)', '42.7', '(2 ÷ 4) × 32,768 ÷ 384.',
       ['128 × 256 = 32,768.', '0.5 × 32,768 ÷ 384.', eq('≈ 42.7 FLOP/byte')], check=round(0.5 * 32768 / 384, 1), tol=0.05)
K.calc('m', '764 of 989 TFLOP/s. Percent? (nearest whole)', '77', 'Divide.',
       ['764 ÷ 989 = 0.7725.', '× 100.', eq('≈ 77 percent')], check=round(100 * 764 / 989))
K.calc('m', '2 × 4096³ FLOPs at 3171 GFLOP/s. Time in ms? (nearest whole)', '43', 'Divide.',
       ['1.374 × 10¹¹ ÷ 3.171 × 10¹².', '= 0.0433 s.', eq('≈ 43 ms')], check=round(2 * 4096 ** 3 / 3171e9 * 1000))
K.calc('m', 'BF16 roof 756 TFLOP/s at 2 TB/s. Ridge?', '378', 'Divide.',
       ['756 ÷ 2.', '= 378.', eq('378 FLOP/byte')], check=378)
K.calc('h', 'Square BF16 tile needed to reach AI 378 from memory alone?', '756', 'T ÷ 2 ≥ 378.',
       ['BF16 square tile AI = T ÷ 2.', 'T ≥ 756.', eq('756 × 756, far too big for on chip memory')], check=756)
K.calc('h', 'Throttled to 1.5 GHz, the H100 reaches 750 TFLOP/s. Percent of the throttled peak? (one decimal)', '92.5', '989 × 1.5 ÷ 1.83.',
       ['Throttled peak 810.7 TFLOP/s.', '750 ÷ 810.7.', eq('≈ 92.5 percent')], check=round(100 * 750 / (989 * 1.5 / 1.83), 1), tol=0.05)
K.calc('x', 'wgmma: 64 × 64 FP32 accumulator over 128 threads. Registers per thread?', '32', 'Divide.',
       ['64 × 64 = 4096 values.', '÷ 128 threads.', eq('32 registers each')], check=32)
K.calc('x', '33 × 33 matrix with 32 × 32 tiles. Percent of threads idle? (nearest whole)', '73', '1 − 1089 ÷ 4096.',
       ['4 tiles × 1024 threads = 4096.', 'Only 33² = 1089 outputs.', eq('≈ 73 percent idle')], check=round(100 * (1 - 1089 / 4096)))

K.assign('tileai', 'e', 'Tile intensity',
         '<p>Write <code>tile_ai(bm, bn, b)</code>: the arithmetic intensity (2 ÷ b) × bm × bn ÷ (bm + bn), rounded to two decimals.</p>',
         '''
def tile_ai(bm, bn, b):
    # your code here
    pass
''', [("tile_ai(32, 32, 4)", 8.0), ("tile_ai(128, 128, 4)", 32.0), ("tile_ai(128, 256, 4)", 42.67), ("tile_ai(128, 128, 2)", 64.0)],
         '''
def tile_ai(bm, bn, b):
    return round(2 / b * bm * bn / (bm + bn), 2)
''', 'BK cancels out.', '<p>Square tiles and narrower numbers both raise the intensity.</p>')
K.assign('swizzle', 'm', 'Count bank conflicts with and without swizzling',
         '<p>A shared memory tile has 8 rows of 8 chunks. Chunk c of row r is stored in slot c, or in slot c XOR r when swizzled. Write <code>max_conflict(col, swizzled)</code>: the largest number of the 8 rows whose chunk <code>col</code> lands in the same slot.</p>',
         '''
def max_conflict(col, swizzled):
    # your code here
    pass
''', [("max_conflict(0, False)", 8), ("max_conflict(0, True)", 1), ("max_conflict(5, True)", 1), ("max_conflict(3, False)", 8)],
         '''
def max_conflict(col, swizzled):
    hits = [0] * 8
    for r in range(8):
        slot = (col ^ r) if swizzled else col
        hits[slot] += 1
    return max(hits)
''', 'Count how many rows land in each slot.', '<p>XOR with 0 to 7 gives 8 different slots, so every column is spread out.</p>')

K.must('Speed of light', 'H100 SXM BF16: 132 × 4 tensor cores × 1024 FLOPs × 1.83 GHz ≈ 989 TFLOP/s. Power throttling lowers the real ceiling.')
K.must('Naive kernel', 'Coalesced order 3171 GFLOP/s (43 ms), swapped order 243 GFLOP/s (565 ms). 13 times from one index.')
K.must('Tile intensity', 'AI = (2 ÷ b) B_M B_N ÷ (B_M + B_N). Square is best. FP32 T × T: T ÷ 4. BF16: T ÷ 2.')
K.must('Hopper', 'TMA copies tiles, swizzle slot = chunk XOR row, wgmma on 4 warps, producer and consumer warp groups.')
K.must('Ladder', '32 (no tensor cores) to 317 (tensor cores + TMA) to 764 TFLOP/s, about 77 percent of peak.')

T = K.topic(
    slug='fast-matmul', topic='fast-matmul', step=(8, 'Tensor cores and fast matmul', 'gpu-tensor', 'Use narrow number formats, tensor cores and tiling tricks to get close to the peak speed of a modern GPU.', 'Pro'),
    title='How fast matmul kernels are built', short='Fast matmul', badge='8.3', minutes=50,
    lead='Follow a matmul on the H100 from 0.24 to 764 TFLOP/s: coalescing, tiles, tensor cores, TMA, swizzling, wgmma and pipelines, with the maths behind each step.',
    desc='The H100 machine and memory pyramid, the BF16 speed of light and power throttling, the naive kernel and the 13 times index order effect, tile quantisation, tile arithmetic intensity and why square tiles win, thread and warp tiling, TMA, XOR swizzling, wgmma, producer and consumer pipelines, persistent kernels, Hilbert order, clusters and the performance ladder.',
    summary='H100 peak, naive kernel, tile intensity, swizzling, wgmma, pipelines, the ladder.',
    keywords=['matmul', 'H100', 'tiling', 'swizzle', 'TMA', 'wgmma', 'performance ladder'],
    recap='<p>Fast matmul is the whole course in one kernel: coalesce, tile, use tensor cores, avoid bank conflicts with swizzles, and overlap loads with maths until the tensor cores never wait.</p>')
