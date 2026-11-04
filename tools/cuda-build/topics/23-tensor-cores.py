# Chapter 8.2: Tensor cores, GEMM and WMMA. Source: lecture 9 (slide 4: computation against communication,
# slides 6 and 7: arithmetic intensity of a fully connected layer, slides 8 and 9: GEMM and implicit GEMM, slides 12 to
# 15: tensor cores and their peaks, slides 16 to 19: WMMA, slides 20 and 21: Ampere, slide 22: warp granularity and wave
# quantisation), workbook 9.1, 9.2, 9.4, 9.5 and 9.6. Correction from the notes: in real kernels the C tile lives in
# registers, not shared memory as slide 16 says. Beyond the lecture: the complete runnable WMMA kernel, tile and wave
# fixes such as stream-K.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

WMMA = r'''
#include <mma.h>
#include <cuda_fp16.h>
using namespace nvcuda;
const int WM = 16, WN = 16, WK = 16;                         // shape of one mma_sync

__global__ void wmma_gemm(const half *A, const half *B, float *C, int M, int N, int K) {
    int warpM = (blockIdx.x * blockDim.x + threadIdx.x) / 32;  // tile row owned by this warp
    int warpN = blockIdx.y * blockDim.y + threadIdx.y;         // tile column
    if (warpM * WM >= M || warpN * WN >= N) return;            // the whole warp leaves together

    wmma::fragment<wmma::matrix_a, WM, WN, WK, half, wmma::row_major> a_frag;
    wmma::fragment<wmma::matrix_b, WM, WN, WK, half, wmma::col_major> b_frag;
    wmma::fragment<wmma::accumulator, WM, WN, WK, float> c_frag;
    wmma::fill_fragment(c_frag, 0.0f);

    for (int k = 0; k < K; k += WK) {                           // walk along K
        const half *a_tile = A + (warpM * WM) * K + k;          // A row major, leading dimension K
        const half *b_tile = B + (warpN * WN) * K + k;          // B column major, leading dimension K
        wmma::load_matrix_sync(a_frag, a_tile, K);
        wmma::load_matrix_sync(b_frag, b_tile, K);
        wmma::mma_sync(c_frag, a_frag, b_frag, c_frag);         // c += a * b on the tensor cores
    }
    float *c_tile = C + (warpM * WM) * N + warpN * WN;
    wmma::store_matrix_sync(c_tile, c_frag, N, wmma::mem_row_major);
}

void launch(const half *A, const half *B, float *C, int M, int N, int K) {
    dim3 block(128, 4);                                         // 4 warps along x, 4 along y
    dim3 grid((M / 16 + 3) / 4, (N / 16 + 3) / 4);
    wmma_gemm<<<grid, block>>>(A, B, C, M, N, K);
}
'''

K.code('fc', r'''
# Arithmetic intensity of a 4096 x 4096 fully connected layer in FP16
def ai(nin, nout, batch):
    flops = 2 * nin * nout * batch
    bytes_ = 2 * (nin * batch + nin * nout + nout * batch)
    return flops / bytes_
ridge = 312e12 / 1.555e12              # A100 FP16 tensor cores against HBM
print("A100 ridge:", round(ridge, 1), "FLOP/byte")
for b in (1, 32, 222, 223, 512):
    print("batch", b, " AI", round(ai(4096, 4096, b), 1))
''')

K.code('peaks', r'''
# Where the tensor core peak numbers come from: SMs x TCs x FMAs per clock x 2 x clock
def peak(sms, tcs, fmas, ghz):
    return sms * tcs * fmas * 2 * ghz / 1000      # TFLOP/s
print("V100 FP16:", round(peak(80, 8, 64, 1.53), 1))
print("A100 FP16:", round(peak(108, 4, 256, 1.41), 1))
print("A100 TF32:", round(peak(108, 4, 128, 1.41), 1))
print("T4   FP16:", round(peak(40, 8, 64, 1.59), 1))
print("H100 BF16:", round(peak(132, 4, 512, 1.83), 1))
''')

K.lesson('fclayer', 'When is a layer limited by maths?', f'''
<p>Lecture 9 starts with a simple test. Work out how long the maths takes and how long the data takes. The slower one sets the pace.</p>
{fxs(
    fx('Time for maths and for data', 'T<sub>math</sub> = ops ÷ BW<sub>math</sub>,  T<sub>mem</sub> = bytes ÷ BW<sub>mem</sub>', 'With overlap, the larger one decides the speed.'),
    fx('Math limited when', 'ops ÷ bytes  >  BW<sub>math</sub> ÷ BW<sub>mem</sub>', 'Left: the arithmetic intensity of the operation. Right: the ops per byte ratio of the GPU, the ridge point of the roofline.', key=True))}
<p>A fully connected layer computes Y = WX. W is N<sub>out</sub> × N<sub>in</sub>, X is N<sub>in</sub> × B, Y is N<sub>out</sub> × B.</p>
{fxs(
    fx('Work', 'ops = 2 N<sub>in</sub> N<sub>out</sub> B', 'Each output is a dot product of length N<sub>in</sub>: one multiply and one add per term.'),
    fx('Bytes in FP16', 'bytes = 2 (N<sub>in</sub> B + N<sub>in</sub> N<sub>out</sub> + N<sub>out</sub> B)', 'Read X, read W, write Y.'),
    fx('4096 × 4096 layer', 'AI = 4096 B ÷ (4096 + 2B)', 'Batch 1 gives about 1. The limit for a huge batch is 2048.', key=True))}
{steps('A100: from which batch is the layer math limited?', [
    'Ridge = 312 × 10¹² ÷ 1.555 × 10¹² ≈ 201 FLOP/byte.',
    'Need 4096 B ÷ (4096 + 2B) > 201.',
    '4096 B > 823,296 + 402 B, so 3694 B > 823,296.',
    eq('B > 222.9, so from a batch of 223')])}
{viz('roofline')}
{code('fc')}
<p>This is why a chatbot answering one user at a time is limited by memory bandwidth (batch 1, AI about 1), and why serving systems batch many users together and shrink weights to 8 or 4 bits. Training uses big batches and runs where tensor cores shine.</p>
''', kw=['arithmetic intensity', 'fully connected', 'batch size', 'ridge point', 'ops per byte', 'LLM inference', 'memory bound'])

K.lesson('gemm', 'Everything is a matrix multiply', f'''
<p><b>GEMM</b> (general matrix multiply) computes C ← αAB + βC with A of size M × K, B of size K × N and C of size M × N. It costs 2MNK FLOPs.</p>
{table(['Layer', 'M', 'N', 'K'], [
    ['Fully connected', 'output features', 'batch', 'input features'],
    ['Convolution (implicit GEMM)', 'output channels', 'batch × output height × output width', 'input channels × filter height × filter width'],
    ['Attention', 'sequence', 'sequence or head size', 'head size or sequence']])}
<p>A convolution becomes a GEMM by cutting out every window of the picture and laying it out as a row. This is called <b>im2col</b>. Step through the worked example from the notes.</p>
{viz('im2col')}
{steps('Workbook 9.2: RGB 224 × 224, 64 filters of 3 × 3, padding 1', [
    'M = 64 output channels.',
    'N = 224 × 224 = 50,176 output pixels.',
    'K = 3 × 3 × 3 = 27.',
    eq('FLOPs = 2 × 64 × 50,176 × 27 = 173,408,256')])}
{note('im2col copies each pixel into up to 9 rows, so the matrix is 9 times bigger than the picture. Libraries such as cuDNN never build it in memory. They compute the addresses on the fly, which is why it is called implicit GEMM.', 'tip')}
''', kw=['GEMM', '2MNK', 'im2col', 'implicit GEMM', 'convolution as matmul', 'attention'])

K.lesson('tc', 'Tensor cores and where their speed comes from', f'''
<p>A <b>tensor core</b> computes a whole small matrix product D = A × B + C in one operation. On Volta each tensor core does a 4 × 4 × 4 product per clock: 64 fused multiply adds, where an ordinary CUDA core does 1.</p>
{fxs(
    fx('Peak of the tensor cores', 'peak = SMs × tensor cores per SM × FMAs per clock × 2 × clock', 'An FMA counts as 2 FLOPs.', key=True))}
{table(['GPU', 'SMs × TCs', 'FMAs per clock', 'Clock', 'Peak'], [
    ['V100 FP16', '80 × 8', '64', '1.53 GHz', '125 TFLOP/s'],
    ['T4 FP16', '40 × 8', '64', '1.59 GHz', '65 TFLOP/s (FP32: 8.1)'],
    ['A100 FP16 / BF16', '108 × 4', '256', '1.41 GHz', '312 TFLOP/s'],
    ['A100 TF32', '108 × 4', '128', '1.41 GHz', '156 TFLOP/s (FP32 CUDA cores: 19.5)'],
    ['H100 SXM BF16', '132 × 4', '512', '1.83 GHz', '989 TFLOP/s']])}
{code('peaks')}
<p>On an A100, FP16 tensor cores are 16 times the FP32 CUDA cores. About 8 times comes from the hardware (TF32 against FP32) and 2 times from the narrower numbers. Both happen together.</p>
{note('Real kernels rarely see the data sheet peak. Under a heavy matmul an H100 hits its 700 W power limit and lowers its clock, so 750 TFLOP/s may be closer to what is reachable than 750 ÷ 989 = 76 percent suggests.', 'tip')}
{deep('What Ampere added', '<p>BF16, TF32 and FP64 on tensor cores. cp.async copies global memory straight into shared memory while the SM keeps computing, which allows deep pipelines. Structured sparsity: if 2 of every 4 weights are zero, tensor cores can skip them for up to 2 times the speed. Libraries: cuBLAS, cuDNN, CUTLASS, cuSPARSE, cuFFT.</p>')}
''', kw=['tensor core', 'D = AB + C', 'FMA', 'peak TFLOP/s', 'V100', 'A100', 'H100', 'T4', 'TF32', 'structured sparsity', 'cp.async'])

K.lesson('wmma', 'Programming tensor cores with WMMA', f'''
<p><b>WMMA</b> (warp matrix multiply accumulate) lets the 32 threads of a warp work together on one 16 × 16 × 16 product. Each thread holds a piece of each matrix in its registers, called a <b>fragment</b>. Which piece is not specified, so code must never rely on it.</p>
{viz('wmma')}
{cu('wmma_gemm.cu', WMMA, {1: 'The WMMA API lives in the mma.h header, in the namespace nvcuda::wmma.', 4: 'The fixed shape of one tensor core operation.', 6: 'Inputs in half (FP16), output in float (FP32): mixed precision.', 7: 'Each warp, not each thread, owns one 16 × 16 output tile. Dividing the x index by 32 numbers the warps.', 9: 'All 32 threads of a warp must take part in every WMMA call, so out of range warps leave as a whole.', 11: 'The A tile fragment, stored row major.', 13: 'The FP32 accumulator fragment, spread over the 32 threads\' registers.', 14: 'Start the accumulator at 0. This is C in D = AB + C.', 16: 'March along K, 16 at a time. This is the tiling loop of the matmul chapter.', 17: 'Top left corner of the current A tile. The last argument of load_matrix_sync is the leading dimension.', 19: 'The warp loads the A tile into its fragment together.', 21: 'One call: 16³ = 4096 multiply adds = 8192 FLOPs on the tensor cores.', 24: 'Write the finished tile back to C in row major order.', 28: '128 × 4 threads = 16 warps = 16 output tiles per block.'})}
{steps('Workbook 9.5: M = N = K = 4096, one warp per 16 × 16 tile', [
    'Tiles: (4096 ÷ 16)² = 65,536.',
    'Steps along K: 4096 ÷ 16 = 256.',
    'Calls: 65,536 × 256 = 16,777,216.',
    eq('16,777,216 × 8192 = 137,438,953,472 = 2 × 4096³ FLOPs')])}
<p>Real kernels give each block a bigger tile. In the slide a block of 8 warps computes a 128 × 128 tile: 2048 outputs per warp, 8 WMMA tiles per warp, and 64 FP32 accumulators per thread. Strips of A and B pass through shared memory, while the C tile stays in registers until the end.</p>
{note('Slide 16 says shared memory is used for the matrix C. In real kernels such as CUTLASS, C stays in registers during the main loop and only passes through shared memory when it is written out at the end.', 'exam')}
{table(['Level', 'What you write'], [
    ['Libraries', 'cuBLAS (cublasGemmEx), cuDNN, PyTorch with FP16, BF16 or allow_tf32'],
    ['Templates', 'CUTLASS and CuTe'],
    ['WMMA', 'the API above: portable and simple'],
    ['PTX mma.sync', 'warp level with exact register layouts (Ampere)'],
    ['PTX wgmma', 'Hopper: 4 warps issue asynchronous tensor core work fed by TMA']])}
''', kw=['WMMA', 'fragment', 'mma_sync', 'load_matrix_sync', 'store_matrix_sync', 'warp tile', 'CUTLASS', 'cuBLAS', 'wgmma'])

K.lesson('waves', 'Staircases: warp granularity and wave quantisation', f'''
<p>Two effects make time jump in steps instead of growing smoothly.</p>
{fxs(
    fx('Warp granularity', 'lane efficiency = T ÷ (32 ⌈T ÷ 32⌉)', '33 threads need 2 warps: 51.6 percent of lanes used. 65 threads: 67.7 percent.'),
    fx('Waves', 'waves = ⌈blocks ÷ (blocks per SM × SMs)⌉', 'One wave fills every SM once.', key=True),
    fx('Wave efficiency', 'n ÷ (W × ⌈n ÷ W⌉), with W = blocks per wave', '217 blocks on an A100: 217 ÷ 324 = 67 percent.', key=True))}
{viz('waves')}
{steps('Workbook 9.6: 4096 × 4096 output on an A100, 216 blocks per wave', [
    '128 × 128 tiles: 32 × 32 = 1024 blocks, ⌈1024 ÷ 216⌉ = 5 waves.',
    'Efficiency 1024 ÷ 1080 = 94.8 percent.',
    '128 × 256 tiles: 512 blocks, ⌈512 ÷ 216⌉ = 3 waves, 512 ÷ 648 = 79.0 percent.',
    eq('The bigger tile does more work per byte but wastes more of the last wave')])}
{note('Fixes: sizes that are multiples of 32 threads and of the wave size, a tile size that divides the problem evenly, persistent kernels, or stream-K, which splits the leftover work along K across the idle SMs (as CUTLASS does). The same effect exists on AMD GPUs.', 'tip')}
''', kw=['warp granularity', 'wave quantisation', 'waves', 'tail effect', 'stream-K', 'persistent kernel'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>An ordinary core is a person with a calculator doing one a × b + c at a time. A tensor core is a machine that multiplies two small grids of numbers in one go.</p>',
    '<p>Math limited when AI > peak ÷ bandwidth. FC layer: AI = 4096B ÷ (4096 + 2B), math limited on an A100 from batch 223. Peak = SMs × TCs × FMAs × 2 × clock. One mma_sync = 8192 FLOPs.</p>',
    '<p>Use cuBLAS or CUTLASS first. For your own kernel: 128 × 128 block tiles, warps of 16 × 16 fragments, FP32 accumulators, sizes that divide into full waves. Check tensor core use in Nsight Compute.</p>',
    '<p>Hopper wgmma with TMA and warp specialisation, Blackwell tcgen05 with tensor memory, FlashAttention fusing softmax into the GEMM, and stream-K scheduling are the current research frontier.</p>')}
''', kw=['ladder', 'Nsight Compute', 'FlashAttention', 'wgmma', 'Blackwell'])

K.quiz('e', 'A GEMM with sizes M, N, K costs', ['MNK FLOPs', '2MNK FLOPs', 'M + N + K', 'MN'], 1, 'Multiply and add.', 'Two FLOPs per term.')
K.quiz('e', 'A Volta tensor core does per clock', ['1 FMA', 'A 4 × 4 × 4 product: 64 FMAs', '32 FMAs', 'A 16 × 16 × 16 product'], 1, 'Small matrices.', '64 FMAs.')
K.quiz('e', 'In WMMA, one 16 × 16 output tile is owned by', ['One thread', 'One warp', 'One block', 'The grid'], 1, 'Warp level.', 'All 32 threads together.')
K.quiz('e', 'im2col turns a convolution into', ['A reduction', 'A matrix multiply', 'A scan', 'A sort'], 1, 'Windows become rows.', 'Then tensor cores can run it.')
K.quiz('m', '4096 × 4096 FC layer, batch 1. AI about', ['1', '200', '2048', '4096'], 0, '4096 ÷ 4098.', 'Heavily memory limited.')
K.quiz('m', 'A100 FP16. From which batch is the 4096 layer math limited?', ['32', '128', '223', '4096'], 2, 'AI > 201.', '3694 B > 823,296.')
K.quiz('m', 'One mma_sync of 16 × 16 × 16 is how many FLOPs?', ['256', '4096', '8192', '16,384'], 2, '2 × 16³.', '8192.')
K.quiz('m', '217 blocks on 108 SMs, one block each. Waves', ['2', '3', '217', '1'], 1, '⌈217 ÷ 108⌉.', '3 waves, 67 percent busy.')
K.quiz('h', 'Why must out of range warps return as a whole in WMMA?', ['To save power', 'Every WMMA call needs all 32 threads of the warp', 'It is faster', 'To free registers'], 1, 'Warp collective.', 'A partial warp would hang or be undefined.')
K.quiz('h', 'On an A100 the 16 times gain of FP16 tensor cores over FP32 CUDA cores comes from', ['Only narrower numbers', 'About 8 times hardware and 2 times narrower numbers', 'Only higher clock', 'Sparsity'], 1, 'TF32 is 8 times.', 'Both together.')
K.quiz('x', '4096 × 4096 output, 216 blocks per wave. Which tile wastes more of the last wave?', ['128 × 128', '128 × 256', 'Both the same', 'Neither'], 1, '512 ÷ 648 against 1024 ÷ 1080.', '79.0 against 94.8 percent.')
K.quiz('x', 'In real tiled GEMM kernels the C tile lives during the main loop in', ['Global memory', 'Shared memory', 'Registers', 'Constant memory'], 2, 'Correction to slide 16.', 'Only the epilogue uses shared memory.')

K.calc('e', 'FLOPs for M = N = K = 1024? (in millions, nearest whole)', '2147', '2 × 1024³.',
       ['1024³ = 1,073,741,824.', '× 2 = 2,147,483,648.', eq('≈ 2147 million')], check=round(2 * 1024 ** 3 / 1e6))
K.calc('e', 'mma_sync calls for M = N = K = 1024?', '262144', '(1024 ÷ 16)³.',
       ['64 tiles each way.', '64³.', eq('262,144 calls')], check=64 ** 3)
K.calc('e', 'A100 FP16 ridge: 312 TFLOP/s ÷ 1.555 TB/s? (nearest whole)', '201', 'Divide.',
       ['312 ÷ 1.555.', '= 200.6.', eq('≈ 201 FLOP/byte')], check=round(312 / 1.555))
K.calc('m', 'V100: 125 TFLOP/s, 0.9 TB/s. Smallest batch that is math limited for the 4096 layer?', '149', 'AI > 138.9.',
       ['Ridge 125 ÷ 0.9 = 138.9.', '4096 B > 138.9 (4096 + 2B), so 3818.2 B > 568,889.', eq('B ≥ 149')], check=149)
K.calc('m', 'FC layer 1024 inputs, 4096 outputs, batch 256, FP16. AI? (nearest whole)', '195', 'N_in N_out B ÷ (sum).',
       ['Top 1024 × 4096 × 256.', 'Bottom 1024 × 256 + 1024 × 4096 + 4096 × 256 = 5,505,024.', eq('≈ 195 FLOP/byte')],
       check=round(1024 * 4096 * 256 / (1024 * 256 + 1024 * 4096 + 4096 * 256)))
K.calc('m', 'A100: 108 × 4 tensor cores × 256 FMAs × 2 × 1.41 GHz. TFLOP/s? (nearest whole)', '312', 'Multiply.',
       ['108 × 4 × 256 = 110,592 FMAs per clock.', '× 2 × 1.41 × 10⁹.', eq('≈ 312 TFLOP/s')], check=round(108 * 4 * 256 * 2 * 1.41 / 1000))
K.calc('m', '325 blocks on 108 SMs, one each. Efficiency in percent? (one decimal)', '75.2', 'n ÷ (W × waves).',
       ['Waves ⌈325 ÷ 108⌉ = 4.', '325 ÷ 432.', eq('75.2 percent')], check=round(100 * 325 / 432, 1), tol=0.05)
K.calc('h', '33 threads. Lane efficiency in percent? (one decimal)', '51.6', '33 ÷ 64.',
       ['2 warps = 64 lanes.', '33 ÷ 64.', eq('51.6 percent')], check=round(100 * 33 / 64, 1), tol=0.05)
K.calc('h', 'Shortest time for a 4096³ GEMM at 312 TFLOP/s in ms? (two decimals)', '0.44', '2 × 4096³ ÷ peak.',
       ['1.374 × 10¹¹ FLOPs.', '÷ 312 × 10¹².', eq('≈ 0.44 ms')], check=round(2 * 4096 ** 3 / 312e12 * 1000, 2), tol=0.005)
K.calc('x', 'Conv: batch 32, 128 to 256 channels, 3 × 3, 28 × 28 output. GFLOPs? (one decimal)', '14.8', '2MNK.',
       ['M = 256, N = 32 × 784 = 25,088, K = 128 × 9 = 1152.', '2 × 256 × 25,088 × 1152.', eq('≈ 14.8 billion FLOPs, about 47 µs at 312 TFLOP/s')],
       check=round(2 * 256 * 25088 * 1152 / 1e9, 1), tol=0.05)
K.calc('x', '16,384 blocks, 2 per SM on 114 SMs. Number of waves?', '72', '⌈16,384 ÷ 228⌉.',
       ['Wave size 228.', '16,384 ÷ 228 = 71.9.', eq('72 waves, the last 86 percent full')], check=72)

K.assign('fcai', 'e', 'Batch size for a math limited layer',
         '<p>Write <code>min_batch(nin, nout, ridge)</code>: the smallest batch B for which the FP16 fully connected layer has AI = N<sub>in</sub> N<sub>out</sub> B ÷ (N<sub>in</sub> B + N<sub>in</sub> N<sub>out</sub> + N<sub>out</sub> B) greater than ridge. Return -1 if no batch up to 100,000 works.</p>',
         '''
def min_batch(nin, nout, ridge):
    # your code here
    pass
''', [("min_batch(4096, 4096, 312 / 1.555)", 223), ("min_batch(4096, 4096, 125 / 0.9)", 149), ("min_batch(4096, 4096, 3000)", -1), ("min_batch(1024, 1024, 1)", 2)],
         '''
def min_batch(nin, nout, ridge):
    for b in range(1, 100001):
        ai = nin * nout * b / (nin * b + nin * nout + nout * b)
        if ai > ridge:
            return b
    return -1
''', 'Try B = 1, 2, 3 and stop at the first that passes.', '<p>The limit for a huge batch is N<sub>in</sub> N<sub>out</sub> ÷ (N<sub>in</sub> + N<sub>out</sub>), 2048 for the 4096 layer, so a ridge of 3000 is never reached.</p>')
K.assign('waveeff', 'm', 'Wave efficiency',
         '<p>Write <code>wave_eff(blocks, sms, per_sm)</code>. Return a list: the number of waves and the efficiency in percent rounded to one decimal.</p>',
         '''
def wave_eff(blocks, sms, per_sm):
    # your code here
    pass
''', [("wave_eff(216, 108, 1)", [2, 100.0]), ("wave_eff(217, 108, 1)", [3, 67.0]), ("wave_eff(115, 114, 1)", [2, 50.4]), ("wave_eff(1024, 108, 2)", [5, 94.8])],
         '''
def wave_eff(blocks, sms, per_sm):
    w = sms * per_sm
    waves = -(-blocks // w)
    return [waves, round(100 * blocks / (w * waves), 1)]
''', 'Ceiling division gives the waves.', '<p>The last test is the 128 × 128 tile case of workbook 9.6.</p>')

K.must('Math limited test', 'AI = ops ÷ bytes > peak ÷ bandwidth. A100 FP16 ridge ≈ 201.')
K.must('FC layer', 'AI = N_in N_out B ÷ (N_in B + N_in N_out + N_out B). 4096 layer: 4096B ÷ (4096 + 2B), math limited from batch 223.')
K.must('GEMM', '2MNK FLOPs. Convolution: M = out channels, N = batch × output pixels, K = in channels × filter size (implicit GEMM).')
K.must('Tensor core peak', 'SMs × TCs × FMAs per clock × 2 × clock. V100 125, A100 312, H100 989 TFLOP/s.')
K.must('WMMA', 'One warp per 16 × 16 tile, fragments, load_matrix_sync, mma_sync (8192 FLOPs), store_matrix_sync. FP16 in, FP32 sum.')
K.must('Waves', 'waves = ⌈blocks ÷ (SMs × blocks per SM)⌉, efficiency = n ÷ (W × waves). 217 blocks on 108 SMs: 67 percent.')

T = K.topic(
    slug='tensor-cores', topic='tensor-cores', step=(8, 'Tensor cores and fast matmul', 'gpu-tensor', 'Use narrow number formats, tensor cores and tiling tricks to get close to the peak speed of a modern GPU.', 'Pro'),
    title='Tensor cores, GEMM and WMMA', short='Tensor cores', badge='8.2', minutes=50,
    lead='Find out when a layer is limited by maths or by memory, turn convolutions into matrix multiplies, see where tensor core speed comes from, write a WMMA kernel and avoid half empty waves.',
    desc='The computation against communication test, arithmetic intensity of a fully connected layer and the batch 223 threshold, GEMM and implicit GEMM with im2col, tensor core peaks for V100, T4, A100 and H100, the complete WMMA kernel line by line, block tile organisation, Ampere features, warp granularity and wave quantisation.',
    summary='FC layer intensity, GEMM, im2col, tensor core peaks, WMMA, waves.',
    keywords=['tensor cores', 'WMMA', 'GEMM', 'im2col', 'arithmetic intensity', 'wave quantisation'],
    recap='<p>A layer is math limited when its AI passes the GPU ridge. Every big layer is a GEMM, and tensor cores run GEMMs on 16 × 16 tiles per warp. Choose sizes that fill whole waves.</p>')
