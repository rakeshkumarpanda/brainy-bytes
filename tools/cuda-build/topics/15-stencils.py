# Chapter 5.3: Stencils and halos. Source: lecture 6 (slides 9 to 15: 1-D stencil with halo in shared memory, 2-D
# and 3-D stencils, indexing neighbours, 3-D tile intensity, the heat equation weights), workbook 6.4 and 6.5.
# Correction: lecture 6 slide 14 uses 0.25 for the centre and 0.1 for each of 6 neighbours. Those weights add to 0.85,
# so a constant field of 100 drops to 85 each step. The centre should be 0.4 (workbook P6.5.4).
# Beyond the lecture: the stability limit for explicit heat steps and ping-pong buffers.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu, nb

K = Kit()

ST1D = r'''
#define R 3
#define B 256

// out[i] = sum of in[i - R] .. in[i + R]. The input is padded with R values on each side.
__global__ void stencil1d(const int *in, int *out) {
    __shared__ int tile[B + 2 * R];
    int g = blockIdx.x * B + threadIdx.x + R;   // position in the padded input
    int s = threadIdx.x + R;                    // position in the tile
    tile[s] = in[g];
    if (threadIdx.x < R) {
        tile[s - R] = in[g - R];                // left halo
        tile[s + B] = in[g + B];                // right halo
    }
    __syncthreads();
    int sum = 0;
    for (int k = -R; k <= R; ++k)
        sum += tile[s + k];
    out[g - R] = sum;
}
'''

HEAT3D = r'''
// One explicit step of 3-D heat: Tnew = (1 - 6L) T + L (sum of 6 neighbours)
__global__ void heat3d(const float *T, float *Tn, int N, float L) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int y = blockIdx.y * blockDim.y + threadIdx.y;
    int z = blockIdx.z * blockDim.z + threadIdx.z;
    if (x < 1 || y < 1 || z < 1 || x >= N - 1 || y >= N - 1 || z >= N - 1) return;
    int i = (z * N + y) * N + x;                 // x fastest, then y, then z
    float nb = T[i - 1] + T[i + 1] + T[i - N] + T[i + N] + T[i - N * N] + T[i + N * N];
    Tn[i] = (1.0f - 6.0f * L) * T[i] + L * nb;   // stable only when L <= 1/6
}

void run(float *dA, float *dB, int N, float L, int steps) {
    dim3 blk(8, 8, 8), grd((N + 7) / 8, (N + 7) / 8, (N + 7) / 8);
    for (int s = 0; s < steps; ++s) {
        heat3d<<<grd, blk>>>(dA, dB, N, L);
        float *t = dA; dA = dB; dB = t;         // ping-pong: new becomes old
    }
}
'''

K.code('ai3d', r'''
# 3-D 7 point stencil: arithmetic intensity of a T x T x T tile
for T in [8, 10, 16, 32]:
    inner = (T - 2) ** 3                 # points that produce an output
    ai = 13 * inner / (4 * T ** 3)       # 13 operations each, 4 bytes per loaded point
    halo = (T ** 3 - inner) / T ** 3
    print(f"T={T:2d}: AI {ai:.2f}, halo share {100 * halo:.1f}%")
print("limit for large T: 13/4 =", 13 / 4)
''')

K.code('heat', r'''
# Stability of the explicit heat step in 1-D: centre weight 1 - 2L
def run(L, steps=6):
    T = [0, 0, 0, 100, 0, 0, 0]
    for _ in range(steps):
        T = [0] + [round((1 - 2 * L) * T[i] + L * (T[i - 1] + T[i + 1]), 1) for i in range(1, 6)] + [0]
    return T
print("L = 0.25:", run(0.25))
print("L = 0.75:", run(0.75))     # above 1/2: values flip sign and grow
''')

K.lesson('what', 'What a stencil is', f'''
<p>A <b>stencil</b> updates every point from a fixed pattern of neighbours. Blurs, edge filters, heat and wave simulations, and the Game of Life are all stencils. Every output can be computed at the same time, so one thread per output works well.</p>
{table(['Stencil', 'Points', 'Example'], [
    ['1-D radius R', '2R + 1', 'moving sum, R = 3 gives 7'], ['2-D plus (radius 1)', '5', 'heat in a plate'], ['2-D box radius r', '(2r + 1)²', 'blur, r = 2 gives 25'],
    ['3-D plus (radius 1)', '7', 'heat in a block'], ['3-D box radius 1', '27', 'smoothing a volume']])}
{fxs(
    fx('Neighbours in 2-D', 'N = i − W, S = i + W, W = i − 1, E = i + 1', 'Row major with width W. Pixel (row 10, col 20) of a 640 wide image is 6420.', key=True),
    fx('Neighbours in 3-D', '± 1, ± N, ± N²', 'Index i = (z × N + y) × N + x.', key=True))}
{scene('passing a rumour', '<p>Each pupil in a classroom grid listens to the four pupils next to them and repeats an average of what they heard. After a few rounds the news has spread. Every pupil can listen at the same moment, which is why a GPU suits it.</p>')}
''', kw=['stencil', 'neighbours', '2-D index', '3-D index', '5 point', '7 point', 'box stencil'])

K.lesson('halo', 'Halos in shared memory', f'''
<p>Neighbouring outputs share most of their inputs. A block loads its B inputs into shared memory once, plus R extra values on each side called the <b>halo</b>, then every thread reads its 2R + 1 inputs from the fast tile.</p>
{viz('stencil')}
{fxs(
    fx('Tile size', 'B + 2R values', 'R = 3, B = 256: 262.', key=True),
    fx('Global reads per output', '(B + 2R) ÷ B with the tile, 2R + 1 without', 'R = 3, B = 256: 1.023 against 7, about 6.8 times fewer.', key=True))}
{cu('stencil1d.cu', ST1D, {7: 'g skips the R padding values at the start of the input.', 9: 'Every thread loads its own centre value.', 10: 'The first R threads also load the halos, R on the left and R on the right.', 14: 'Wait until the whole tile, halos included, is in shared memory.', 17: 'All 2R + 1 reads come from shared memory.'})}
''', kw=['halo', 'ghost cells', 'shared tile', 'reads per output', '1-D stencil'])

K.lesson('3d', '3-D tiles: why big tiles still stay memory bound', f'''
{fxs(
    fx('Without tiling', 'AI = 13 ÷ 28 ≈ 0.46', '7 multiplies and 6 adds, 7 floats loaded.'),
    fx('With T × T × T tiles', 'AI(T) = 13 × (T − 2)³ ÷ (4T³)', 'Only the inner (T − 2)³ points make outputs.', key=True),
    fx('Halo share', '(T³ − (T − 2)³) ÷ T³', 'T = 8: 57.8 percent of loaded points are border.', key=True))}
{code('ai3d')}
<p>AI can never pass 13 ÷ 4 = 3.25, and T = 8 already uses 512 threads. With one thread per point, a 3-D stencil stays memory bound on every modern GPU. Real codes use 2-D tiles that march through z, keeping three planes in registers.</p>
''', kw=['3-D tile', 'arithmetic intensity', 'halo share', '2.5-D blocking'])

K.lesson('heat', 'The heat equation and stability', f'''
{fxs(
    fx('3-D explicit heat step', 'T<sub>new</sub> = (1 − 6λ) T + λ × (sum of 6 neighbours)', 'λ = α Δt ÷ h². Weights add to 1, so a constant field stays constant.', key=True),
    fx('Stability', 'λ ≤ 1/6 in 3-D, 1/4 in 2-D, 1/2 in 1-D', 'Above it the centre weight is negative and values oscillate and grow.', key=True),
    fx('Largest time step', 'Δt ≤ h² ÷ (6α)', 'α = 0.0001, h = 0.01 gives Δt ≤ 0.167 s.'))}
{note('Lecture 6 slide 14 uses 0.25 for the centre and 0.1 for each of the 6 neighbours. They add to 0.85, so a field of 100 drops to 85 every step. With neighbour weight 0.1 the centre must be 1 − 6 × 0.1 = 0.4.', 'warn')}
{code('heat')}
{cu('heat3d.cu', HEAT3D, {7: 'x is the fastest index, so a warp reads neighbouring x values: coalesced.', 8: 'The six neighbours: x ± 1, y ± 1 (± N) and z ± 1 (± N²).', 9: 'Weights 1 − 6L and L add to 1.', 16: 'Ping-pong: swap the pointers so the new grid becomes the old one. No copy is needed.'})}
{nb('02-thread-indexing-2d.ipynb', 'Notebook: a 3 × 3 stencil on an image', 'The blur kernel in this notebook is a stencil. Count its global reads and compare with a tiled version.')}
''', kw=['heat equation', 'stability', 'CFL', 'lambda', 'ping-pong buffers', 'explicit step'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Each point looks at its neighbours and updates. Load a patch once with a border around it, and let everyone read the patch.</p>',
    '<p>Tile B + 2R, reads (B + 2R)/B against 2R + 1. 3-D AI = 13(T − 2)³/(4T³) ≤ 3.25. Heat stable for λ ≤ 1/6 in 3-D.</p>',
    '<p>2.5-D blocking keeps three z planes in registers and marches up the grid. Temporal blocking does several time steps per load, trading extra halo for less traffic.</p>',
    '<p>Weather, seismic and CFD codes are mostly stencils. Implicit schemes avoid the stability limit by solving a linear system each step, which brings in sparse solvers and multigrid.</p>')}
''', kw=['ladder', '2.5-D blocking', 'temporal blocking', 'implicit methods'])

K.quiz('e', 'Points in a 3-D plus stencil of radius 1', ['5', '7', '9', '27'], 1, 'Centre + 6.', '7.')
K.quiz('e', 'The halo is', ['The output', 'Extra inputs around a tile that neighbours need', 'A cache', 'A warp'], 1, 'Border.', 'R values on each side.')
K.quiz('e', '2-D box stencil of radius 2 has', ['9 points', '25 points', '13 points', '5 points'], 1, '(2r + 1)².', '25.')
K.quiz('m', 'R = 3, B = 256. Tile size?', ['256', '259', '262', '263'], 2, 'B + 2R.', '262.')
K.quiz('m', 'Width 640: pixel (row 10, col 20) index', ['6420', '2010', '6400', '640'], 0, 'row × W + col.', '6400 + 20.')
K.quiz('m', 'Why a barrier after loading the tile?', ['To free memory', 'Threads read values loaded by other threads', 'For speed', 'Not needed'], 1, 'Halo is loaded by a few threads.', 'All loads must finish first.')
K.quiz('m', 'Ping-pong buffers are used because', ['They save memory', 'Threads must read only old values while writing new ones', 'They are faster to allocate', 'Of bank conflicts'], 1, 'No mixing.', 'Read old, write new, then swap.')
K.quiz('h', 'AI of a 3-D 7 point stencil tile can never pass', ['0.46', '1.37', '3.25', '13'], 2, 'T → ∞.', '13 ÷ 4.')
K.quiz('h', 'Slide 14 weights (0.25 centre, 0.1 × 6) on a field of 100 give', ['100', '85', '125', '60'], 1, '0.25 + 0.6.', '85: the weights do not add to 1.')
K.quiz('h', 'Largest stable λ for 3-D explicit heat', ['1/2', '1/4', '1/6', '1'], 2, 'Centre 1 − 6λ ≥ 0.', '1/6.')
K.quiz('x', 'Halo share at T = 32 for a 3-D tile', ['5 percent', '17.6 percent', '33 percent', '57.8 percent'], 1, '1 − (30/32)³.', '≈ 17.6 percent.')
K.quiz('x', 'Tile T for AI ≥ 3', ['T ≥ 16', 'T ≥ 32', 'T ≥ 76', 'Never'], 2, '3.25(1 − 2/T)³ ≥ 3.', 'T ≥ 76: impossible with one thread per point.')

K.calc('e', 'Points in a 2-D box of radius 2?', '25', '(2r + 1)².',
       ['2 × 2 + 1 = 5.', '5².', eq('25')], check=25)
K.calc('e', 'Tile size for R = 2, B = 128?', '132', 'B + 2R.',
       ['128 + 4.', '= 132.', eq('132 values')], check=132)
K.calc('e', 'N = 100. Index of (x 4, y 3, z 2) with i = (z × N + y) × N + x?', '20304', 'Expand.',
       ['z × N² = 20,000.', 'y × N = 300, x = 4.', eq('20,304')], check=(2 * 100 + 3) * 100 + 4)
K.calc('m', 'R = 2, B = 128. Reads per output with the tile? (three decimals)', '1.031', '132 ÷ 128.',
       ['Tile 132 values.', '÷ 128 outputs.', eq('1.031 against 5 without')], check=132 / 128, tol=0.0005)
K.calc('m', 'Shared memory bytes for B = 512, R = 4 (ints)?', '2080', '(B + 2R) × 4.',
       ['512 + 8 = 520 ints.', '× 4 bytes.', eq('2080 bytes')], check=520 * 4)
K.calc('m', '3-D tile T = 8. AI? (two decimals)', '1.37', '13 × 6³ ÷ (4 × 8³).',
       ['Inner 216 points × 13 = 2808 operations.', 'Loaded 512 × 4 = 2048 bytes.', eq('2808 ÷ 2048 ≈ 1.37')], check=13 * 216 / 2048, tol=0.005)
K.calc('m', '3-D tile T = 16. AI? (two decimals)', '2.18', '13 × 14³ ÷ (4 × 16³).',
       ['14³ = 2744, × 13 = 35,672.', '16³ × 4 = 16,384.', eq('≈ 2.18')], check=13 * 14 ** 3 / (4 * 16 ** 3), tol=0.005)
K.calc('h', 'Halo share at T = 16 in percent? (one decimal)', '33.0', '1 − (14/16)³.',
       ['(14/16)³ = 0.6699.', '1 − 0.6699.', eq('33.0 percent')], check=100 * (1 - (14 / 16) ** 3), tol=0.05)
K.calc('h', 'α = 0.0001, h = 0.01, 3-D. Largest stable Δt in s? (three decimals)', '0.167', 'h² ÷ (6α).',
       ['h² = 0.0001.', '÷ (6 × 0.0001) = 1/6.', eq('≈ 0.167 s')], check=0.0001 / (6 * 0.0001), tol=0.0005)
K.calc('h', '1,000,000 outputs, R = 3, B = 256: blocks?', '3907', '⌈10⁶ ÷ 256⌉.',
       ['10⁶ ÷ 256 = 3906.25.', 'Round up.', eq('3907 blocks, padded input 1,000,006')], check=-(-1000000 // 256))
K.calc('x', 'Same: total global reads with tiles?', '1023634', 'Blocks × (B + 2R).',
       ['3907 blocks.', '× 262.', eq('1,023,634 reads')], check=3907 * 262)

K.assign('stencil1', 'e', '1-D stencil with zero padding',
         '<p>Write <code>stencil(a, R)</code>: return a list where element i is the sum of a[i − R] to a[i + R], treating values outside the list as 0.</p>',
         '''
def stencil(a, R):
    # your code here
    pass
''', [("stencil([1, 2, 3, 4, 5], 1)", [3, 6, 9, 12, 9]), ("stencil([1, 1, 1, 1], 2)", [3, 4, 4, 3]), ("stencil([5], 3)", [5])],
         '''
def stencil(a, R):
    n = len(a)
    return [sum(a[j] for j in range(i - R, i + R + 1) if 0 <= j < n) for i in range(n)]
''', 'Skip indices outside the list.', '<p>Zero padding gives smaller sums at the ends.</p>')
K.assign('heatstep', 'm', 'One 2-D heat step',
         '<p>Write <code>heat_step(T, lam)</code> for a square grid (list of lists). Border cells stay the same. Inner cells become (1 − 4λ)T + λ(up + down + left + right). Round each value to 4 decimals.</p>',
         '''
def heat_step(T, lam):
    # your code here
    pass
''', [("heat_step([[0, 0, 0], [0, 100, 0], [0, 0, 0]], 0.25)", [[0, 0, 0], [0, 0.0, 0], [0, 0, 0]]), ("heat_step([[10, 10, 10], [10, 10, 10], [10, 10, 10]], 0.2)", [[10, 10, 10], [10, 10.0, 10], [10, 10, 10]])],
         '''
def heat_step(T, lam):
    n = len(T)
    N = [row[:] for row in T]
    for i in range(1, n - 1):
        for j in range(1, n - 1):
            nb = T[i - 1][j] + T[i + 1][j] + T[i][j - 1] + T[i][j + 1]
            N[i][j] = round((1 - 4 * lam) * T[i][j] + lam * nb, 4)
    return N
''', 'Copy the grid, then update only inner cells from the old grid.', '<p>A constant field stays constant because the weights add to 1.</p>')

K.must('Stencil', 'Each output from a fixed neighbour pattern. 2-D: ±1, ±W. 3-D: ±1, ±N, ±N².')
K.must('Halo', 'Tile B + 2R. Reads per output (B + 2R)/B against 2R + 1. Barrier after loading.')
K.must('3-D tiles', 'AI = 13(T − 2)³/(4T³) ≤ 3.25. Halo share 57.8 percent at T = 8. Memory bound.')
K.must('Heat', 'Tnew = (1 − 6λ)T + λΣ6. Weights must add to 1 (slide 14 used 0.25 + 0.6). Stable for λ ≤ 1/6.')
K.must('Ping-pong', 'Read the old grid, write the new grid, swap pointers.')

T = K.topic(
    slug='stencils', topic='stencils', step=(5, 'Parallel patterns', 'gpu-patterns', 'Learn the patterns behind most GPU code: reductions, tiled matrix multiply, stencils, convolution and scans.', 'College'),
    title='Stencils, halos and heat simulation', short='Stencils', badge='5.3', minutes=45,
    lead='Update every point from its neighbours, load each tile once with a halo around it, and keep a heat simulation stable.',
    desc='1-D, 2-D and 3-D stencils, neighbour indexing, halos in shared memory, reads per output, 3-D tile intensity and halo share, the explicit heat step, the slide 14 weight correction, stability and ping-pong buffers.',
    summary='Stencil patterns, halos, reads per output, 3-D tile intensity, heat step stability.',
    keywords=['stencil', 'halo', 'heat equation', 'stability', '3-D', 'shared memory'],
    recap='<p>Load a tile with an R wide halo once and every output reads from shared memory. Heat weights must add to 1 and λ must stay at or below 1/6 in 3-D.</p>')
