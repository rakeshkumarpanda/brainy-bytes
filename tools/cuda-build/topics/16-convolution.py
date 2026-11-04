# Chapter 5.4: Convolution and Sobel. Source: lecture 4 (Sobel edge detection on the GPU, Lena and kid benchmarks,
# the 8K frame), lecture 8 (convolution sizes, by hand examples, the sharpen slide, halo tiles, constant memory for
# the filter), workbook 4.1, 4.2, 8.1, 8.2 and 8.3.
# Correction: lecture 8 sharpens the pixel 30 at (2, 1) to 35. With top 25, bottom 35, left 20 and right 40 the result
# is 5 × 30 − 120 = 30 (workbook P8.2.4).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

SOBEL = r'''
#include <cstdlib>

__constant__ int GX[9] = {-1, 0, 1, -2, 0, 2, -1, 0, 1};
__constant__ int GY[9] = {-1, -2, -1, 0, 0, 0, 1, 2, 1};

__global__ void sobel(const unsigned char *in, unsigned char *out, int w, int h) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int y = blockIdx.y * blockDim.y + threadIdx.y;
    if (x < 1 || y < 1 || x >= w - 1 || y >= h - 1) return;
    int sx = 0, sy = 0;
    for (int dy = -1; dy <= 1; ++dy)
        for (int dx = -1; dx <= 1; ++dx) {
            int p = in[(y + dy) * w + (x + dx)];
            int k = (dy + 1) * 3 + (dx + 1);
            sx += GX[k] * p;
            sy += GY[k] * p;
        }
    int m = abs(sx) + abs(sy);              // M1 = |Sx| + |Sy|, cheaper than a square root
    out[y * w + x] = m > 255 ? 255 : m;     // clamp to the 8 bit range
}
'''

TILED = r'''
#define BS 16
#define R 1

__constant__ float W[(2 * R + 1) * (2 * R + 1)];

// Each block loads a (BS + 2R) x (BS + 2R) tile, then computes BS x BS outputs
__global__ void convTiled(const float *in, float *out, int w, int h) {
    __shared__ float tile[BS + 2 * R][BS + 2 * R];
    int ox = blockIdx.x * BS, oy = blockIdx.y * BS;          // top left output of this block
    for (int i = threadIdx.y; i < BS + 2 * R; i += BS)
        for (int j = threadIdx.x; j < BS + 2 * R; j += BS) {
            int gx = ox + j - R, gy = oy + i - R;
            tile[i][j] = (gx >= 0 && gy >= 0 && gx < w && gy < h) ? in[gy * w + gx] : 0.0f;
        }
    __syncthreads();
    int x = ox + threadIdx.x, y = oy + threadIdx.y;
    if (x >= w || y >= h) return;
    float s = 0.0f;
    for (int a = 0; a <= 2 * R; ++a)
        for (int b = 0; b <= 2 * R; ++b)
            s += W[a * (2 * R + 1) + b] * tile[threadIdx.y + a][threadIdx.x + b];
    out[y * w + x] = s;
}
'''

K.code('sobel', r'''
# Sobel on one 3 x 3 patch: Sx, Sy, M1 = |Sx| + |Sy|, clamp to 255
GX = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
GY = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
def sobel(p):
    sx = sum(GX[i][j] * p[i][j] for i in range(3) for j in range(3))
    sy = sum(GY[i][j] * p[i][j] for i in range(3) for j in range(3))
    return sx, sy, min(255, abs(sx) + abs(sy))
print(sobel([[0, 0, 255]] * 3))
print(sobel([[10, 20, 30]] * 3))
print(sobel([[50, 60, 70], [50, 60, 70], [90, 100, 110]]))
''')

K.code('sizes', r'''
# Output size and work of a convolution layer
def out_size(W, K, P=0, S=1):
    return (W + 2 * P - K) // S + 1
print("AlexNet layer 1:", out_size(227, 11, 0, 4))
o = out_size(227, 11, 0, 4)
print("multiply-adds:", o * o * 96 * 11 * 11 * 3)
print("224, 3x3, pad 1, stride 2:", out_size(224, 3, 1, 2))
''')

K.lesson('conv', 'Convolution: slide, multiply, add', f'''
<p>A 2-D convolution slides a small grid of weights (the filter or kernel) over a picture. At each place it multiplies the weights by the pixels under them and adds the products. One GPU thread computes one output pixel.</p>
{viz('conv2d')}
{fxs(
    fx('Output size', 'out = ⌊(W + 2P − K) ÷ S⌋ + 1', 'W input width, K filter size, P padding, S stride.', key=True),
    fx('"Same" padding', 'P = (K − 1) ÷ 2', '3 × 3 needs 1, 5 × 5 needs 2.'),
    fx('Work', 'multiply-adds = out² × K² × C<sub>in</sub> × C<sub>out</sub>', 'AlexNet layer 1: 55² × 11² × 3 × 96 = 105,415,200.', key=True))}
{code('sizes')}
{note('Lecture 8 sharpens the pixel 30 at (2, 1) to 35. With neighbours 25, 35, 20 and 40 the result is 5 × 30 − 120 = 30. On a smooth slope sharpening changes nothing.', 'warn')}
''', kw=['convolution', 'filter', 'output size', 'padding', 'stride', 'multiply-adds', 'AlexNet'])

K.lesson('sobel', 'Sobel edge detection (lecture 4)', f'''
<p>Sobel uses two 3 × 3 filters. G<sub>x</sub> responds to changes from left to right, G<sub>y</sub> to changes from top to bottom. A flat area gives 0, an edge gives a big value.</p>
{fxs(
    fx('Edge strength', 'M1 = |S<sub>x</sub>| + |S<sub>y</sub>|, M2 = √(S<sub>x</sub>² + S<sub>y</sub>²)', 'M1 is cheaper and is what the lecture code uses. Both are clamped to 255.', key=True))}
{code('sobel')}
{cu('sobel.cu', SOBEL, {3: 'The two filters live in constant memory: every thread reads the same weight at the same moment, so it is broadcast.', 9: 'Border pixels have no full 3 × 3 neighbourhood, so they are skipped.', 13: 'Row major neighbour read. A warp reads 32 neighbouring x values, so it is coalesced.', 18: 'M1 = |Sx| + |Sy|.', 19: 'Clamp because the output is one byte.'})}
{table(['Picture', 'CPU', 'GPU kernel', 'Speedup'], [['Lena 512 × 512', '13.59 ms', '0.188 ms', 'about 72'], ['Kid', '47.27 ms', '0.336 ms', 'about 141'], ['8K frame', 'not given', '1.65 ms (8.66 ms with copies)', 'copies are 81 percent']])}
''', kw=['Sobel', 'Gx', 'Gy', 'M1', 'M2', 'edge detection', 'constant memory', 'Lena'])

K.lesson('tiles', 'Halo tiles for convolution', f'''
<p>Neighbouring outputs share most of their inputs, as with stencils. A block of B × B threads loads a (B + 2r) × (B + 2r) tile into shared memory once, then each thread reads its K × K inputs from the tile.</p>
{fxs(
    fx('Tile side', 'B + 2r, with r = (K − 1) ÷ 2', 'B = 32, 3 × 3: 34 × 34.', key=True),
    fx('Loads per output', '(B + 2r)² ÷ B²', 'Against K² without a tile. B = 16, 5 × 5: 1.5625 against 25.', key=True),
    fx('Saving', '1 − (B + 2r)² ÷ (K² B²)', 'Best possible for large B: 1 − 1/K². 3 × 3 gives 88.9 percent.'))}
{steps('Workbook 8.3: N = 1024, B = 16, 3 × 3', [
    'Plain: 9 reads per output × 1024² = 9,437,184.',
    'Blocks 64 × 64 = 4096, each loads 18 × 18 = 324.',
    'Tiled: 4096 × 324 = 1,327,104.',
    eq('85.9 percent fewer reads')])}
{cu('conv_tiled.cu', TILED, {4: 'Filter weights in constant memory, filled by the host with cudaMemcpyToSymbol.', 8: 'The tile is (BS + 2R) wide, so the block has fewer threads than tile cells.', 10: 'The loops let 16 × 16 threads cover an 18 × 18 tile: some threads load two values.', 13: 'Outside the picture we load 0 (zero padding).', 15: 'All of the tile must be loaded before any thread reads its neighbours.', 21: 'K × K reads from shared memory instead of global memory.'})}
''', kw=['halo tile', 'shared memory', 'loads per output', 'saving', 'zero padding', 'tiled convolution'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Slide a small stamp across a picture, multiply and add at each place. Sobel finds edges by comparing one side with the other.</p>',
    '<p>out = (W + 2P − K)/S + 1. Work out² K² Cin Cout. Tile (B + 2r)², loads per output (B + 2r)²/B². Weights in constant memory.</p>',
    '<p>Deep learning convolutions are turned into matrix multiplies (im2col, chapter 8.2) or use Winograd and FFT methods, so tensor cores can run them. cuDNN picks the fastest algorithm per layer.</p>',
    '<p>Depthwise separable convolutions (chapter 1.3) cut the work by about K² and are memory bound. Implicit GEMM builds the im2col matrix on the fly in shared memory instead of storing it.</p>')}
''', kw=['ladder', 'im2col', 'Winograd', 'cuDNN', 'implicit GEMM'])

K.quiz('e', 'Output size of a 5 × 5 picture with a 2 × 2 filter, no padding', ['5 × 5', '4 × 4', '3 × 3', '2 × 2'], 1, '5 − 2 + 1.', '4 × 4.')
K.quiz('e', 'Padding that keeps the size for a 3 × 3 filter', ['0', '1', '2', '3'], 1, '(K − 1)/2.', '1.')
K.quiz('e', 'Sobel on a flat picture (all 120) gives', ['120', '255', '0', '1020'], 2, 'No change.', '0: no edge.')
K.quiz('m', 'Rows (0, 0, 255) three times: Sx', ['255', '510', '1020', '0'], 2, '255 × (1 + 2 + 1).', '1020.')
K.quiz('m', 'Rows (10, 20, 30) three times: output', ['20', '40', '80', '255'], 2, 'Sx = 20 × 4.', '80.')
K.quiz('m', 'Why are the Sobel weights put in constant memory?', ['They change often', 'All threads read the same weight at once, so it is broadcast', 'They are large', 'Kernels write them'], 1, 'Uniform reads.', 'Broadcast.')
K.quiz('m', '224 × 224, 3 × 3, padding 1, stride 2. Output', ['224', '222', '112', '111'], 2, '(224 + 2 − 3)/2 + 1.', '112.')
K.quiz('h', 'B = 16, 5 × 5. Loads per output with a tile', ['1.5625', '25', '1.27', '4'], 0, '20² ÷ 16².', '1.5625.')
K.quiz('h', 'Sharpen 30 with neighbours 25, 35, 20, 40 gives', ['35', '30', '25', '150'], 1, '5 × 30 − 120.', '30 (the slide said 35).')
K.quiz('h', 'Best possible saving for a 7 × 7 filter', ['88.9 percent', '98.0 percent', '75 percent', '100 percent'], 1, '1 − 1/49.', '98.0 percent.')
K.quiz('x', '3 × 3 filter: B for at most 1.1 loads per output', ['B ≥ 16', 'B ≥ 32', 'B ≥ 42', 'B ≥ 8'], 2, '(B + 2)²/B² ≤ 1.1.', 'B ≥ 42, more than 32 × 32 threads allow, so each thread must compute several outputs.')
K.quiz('x', 'Rows (50, 60, 70), (50, 60, 70), (90, 100, 110): M1 and M2', ['240 and 178.9', '160 and 80', '240 and 240', '80 and 160'], 0, 'Sx = 80, Sy = 160.', 'M1 = 240, M2 = √(6400 + 25,600) ≈ 178.9.')

K.calc('e', '1024 × 1024, 5 × 5, no padding. Outputs?', '1040400', '1020².',
       ['1024 − 5 + 1 = 1020.', '1020 × 1020.', eq('1,040,400')], check=1020 ** 2)
K.calc('e', 'Radius of a 7 × 7 filter?', '3', '(K − 1)/2.',
       ['7 − 1 = 6.', '÷ 2.', eq('3')], check=3)
K.calc('e', 'Box with rows (1, 1) and (1, 1) on the 1 to 25 picture. First output?', '16', '1 + 2 + 6 + 7.',
       ['Top left 2 × 2 window: 1, 2, 6, 7.', 'Add.', eq('16')], check=16)
K.calc('m', 'Same 1,040,400 outputs at 512 threads per block. Blocks?', '2033', 'Round up.',
       ['1,040,400 ÷ 512 = 2032.03.', 'Round up.', eq('2033 blocks')], check=-(-1040400 // 512))
K.calc('m', 'AlexNet layer 1 multiply-adds?', '105415200', '55² × 121 × 3 × 96.',
       ['Output 55 × 55 = 3025.', '× 11 × 11 × 3 × 96 = 34,848.', eq('105,415,200')], check=55 * 55 * 11 * 11 * 3 * 96)
K.calc('m', 'Bytes for a float tile, B = 16, 7 × 7 filter?', '1936', '(16 + 6)² × 4.',
       ['Tile side 22.', '22² = 484 floats.', eq('1936 bytes')], check=22 * 22 * 4)
K.calc('m', 'Sx and Sy are both 70. Output (M1)?', '140', '|Sx| + |Sy|.',
       ['70 + 70.', 'Below 255.', eq('140')], check=140)
K.calc('h', 'N = 1024, B = 16, 3 × 3: tiled reads?', '1327104', '4096 blocks × 18².',
       ['64 × 64 = 4096 blocks.', '18 × 18 = 324 each.', eq('1,327,104 (85.9 percent saved)')], check=4096 * 324)
K.calc('h', 'Saving in percent for B = 8, 3 × 3? (one decimal)', '82.6', '1 − 10²/(9 × 64).',
       ['Tile 100 loads for 64 outputs.', 'Plain 9 × 64 = 576.', eq('1 − 100/576 = 82.6 percent')], check=100 * (1 - 100 / 576), tol=0.05)
K.calc('h', '3 × 3 same size, 224 × 224, 64 in and 64 out channels. Time at 8 TFLOP/s in ms? (two decimals)', '0.46', 'FLOPs = 2 × MACs.',
       ['MACs 224² × 9 × 64 × 64 = 1,849,688,064.', 'FLOPs 3.70 × 10⁹ ÷ 8 × 10¹².', eq('≈ 0.46 ms')], check=2 * 224 ** 2 * 9 * 64 * 64 / 8e12 * 1000, tol=0.005)
K.calc('x', '8K frame (7680 × 4320) Sobel: multiply-adds per frame in millions? (nearest whole, 18 per output, outputs (W − 2)(H − 2))', '597', '2 filters × 9.',
       ['Outputs 7678 × 4318 = 33,153,604.', '× 18 = 596,764,872.', eq('≈ 597 million')], check=round(7678 * 4318 * 18 / 1e6))

K.assign('conv2', 'm', 'Valid 2-D convolution',
         '<p>Write <code>conv(img, k)</code> for a picture and a square filter (lists of lists), with no padding and stride 1, as used in deep learning (no flipping). Return the output grid.</p>',
         '''
def conv(img, k):
    # your code here
    pass
''', [("conv([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[1, 0], [0, -1]])", [[-4, -4], [-4, -4]]), ("conv([[0, 0, 255]] * 3, [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])", [[1020]])],
         '''
def conv(img, k):
    K = len(k)
    H, W = len(img), len(img[0])
    out = []
    for i in range(H - K + 1):
        row = []
        for j in range(W - K + 1):
            row.append(sum(k[a][b] * img[i + a][j + b] for a in range(K) for b in range(K)))
        out.append(row)
    return out
''', 'Two loops over outputs, two over the filter.', '<p>The second test is Sobel Gx on a sharp edge: 1020.</p>')
K.assign('tileloads', 'e', 'Halo tile loads',
         '<p>Write <code>loads_per_output(B, K)</code>: (B + K − 1)² ÷ B², rounded to 4 decimals.</p>',
         '''
def loads_per_output(B, K):
    # your code here
    pass
''', [("loads_per_output(32, 3)", 1.1289), ("loads_per_output(16, 5)", 1.5625), ("loads_per_output(16, 3)", 1.2656)],
         '''
def loads_per_output(B, K):
    return round((B + K - 1) ** 2 / B ** 2, 4)
''', 'Tile side is B + K − 1.', '<p>Bigger blocks and smaller filters waste less on the halo.</p>')

K.must('Size', 'out = ⌊(W + 2P − K)/S⌋ + 1. Same padding P = (K − 1)/2.')
K.must('Work', 'MACs = out² K² Cin Cout. FLOPs = 2 × MACs.')
K.must('Sobel', 'Gx, Gy 3 × 3. M1 = |Sx| + |Sy| clamped to 255. Weights in constant memory.')
K.must('Tiles', 'Tile (B + 2r)², loads per output (B + 2r)²/B², best saving 1 − 1/K².')
K.must('Correction', 'Sharpening 30 with 25, 35, 20, 40 gives 30, not 35. Smooth slopes do not change.')

T = K.topic(
    slug='convolution', topic='convolution', step=(5, 'Parallel patterns', 'gpu-patterns', 'Learn the patterns behind most GPU code: reductions, tiled matrix multiply, stencils, convolution and scans.', 'College'),
    title='Convolution and Sobel edge detection', short='Convolution', badge='5.4', minutes=50,
    lead='Compute 2-D convolutions by hand and on the GPU, detect edges with Sobel, put the filter in constant memory, and cut global reads with halo tiles.',
    desc='Convolution output size, padding, stride and work, AlexNet layer 1, Sobel Gx and Gy with M1 and M2, the lecture 4 benchmarks, halo tiles and their savings, and the sharpen slide correction.',
    summary='Convolution sizes and work, Sobel, constant memory filters, halo tiles and savings.',
    keywords=['convolution', 'Sobel', 'filter', 'halo tile', 'constant memory', 'padding'],
    recap='<p>Each output is K² multiply-adds. Sobel compares opposite sides. Halo tiles cut reads from K² to about (B + 2r)²/B² per output.</p>')
