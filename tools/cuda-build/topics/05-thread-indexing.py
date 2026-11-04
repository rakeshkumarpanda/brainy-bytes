# Chapter 2.2: thread indexing in 1, 2 and 3 dimensions. Source: lecture 2 (launch configuration, global index),
# lecture 3 (organising blocks, dim3, slides 15 to 16 worked example with its correction, images as matrices,
# matrix vector multiplication), lecture 4 (one thread per pixel), workbook 2.1, 3.1 and 3.2, Quiz 1 question 7.
# Beyond the lecture: grid stride loops and the limits on grid and block sizes, from the CUDA guide.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

GRID2D = r'''
__global__ void invert(unsigned char* img, int width, int height) {
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (col < width && row < height) {
        int idx = row * width + col;
        img[idx] = 255 - img[idx];
    }
}

void launchInvert(unsigned char* d_img, int width, int height) {
    dim3 block(16, 16);
    dim3 grid((width + block.x - 1) / block.x, (height + block.y - 1) / block.y);
    invert<<<grid, block>>>(d_img, width, height);
}
'''

STRIDE = r'''
__global__ void saxpy(int n, float a, const float* x, float* y) {
    for (int i = blockIdx.x * blockDim.x + threadIdx.x; i < n;
         i += blockDim.x * gridDim.x) {
        y[i] = a * x[i] + y[i];
    }
}
'''

MATVEC = r'''
__global__ void matVecMul(const float* A, const float* x, float* y, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
        float sum = 0.0f;
        for (int j = 0; j < N; j++) {
            sum += A[i * N + j] * x[j];
        }
        y[i] = sum;
    }
}
'''

K.code('where', r'''
# Where is global thread g in a 3-D grid of 3-D blocks? (x changes fastest, then y, then z)
def locate(g, grid, block):
    Bx, By, Bz = block
    Gx, Gy, Gz = grid
    per_block = Bx * By * Bz
    b, t = g // per_block, g % per_block          # block number and thread number inside it
    bidx = (b % Gx, (b // Gx) % Gy, b // (Gx * Gy))
    tidx = (t % Bx, (t // Bx) % By, t // (Bx * By))
    return bidx, tidx

print("thread 343 of grid (5,4,1), block (5,5,1):", locate(343, (5, 4, 1), (5, 5, 1)))
print("thread 342:", locate(342, (5, 4, 1), (5, 5, 1)))
print("thread 1000 of grid (4,3,2), block (8,8,1):", locate(1000, (4, 3, 2), (8, 8, 1)))
''')

K.code('matvec', r'''
# Quiz 1 question 7: trace thread i = 2 of the matVecMul kernel
A = [1, 2, 1, 0,  0, 1, 3, 1,  2, 0, 1, 2,  1, 1, 0, 1]   # 4 x 4, row major
x = [1, 2, 3, 4]
N = 4
i = 0 * 4 + 2           # blockIdx.x * blockDim.x + threadIdx.x
s = 0.0
for j in range(N):
    s += A[i * N + j] * x[j]
    print(f"j={j} A[{i * N + j}]={A[i * N + j]} x[{j}]={x[j]} sum={s}")
print("y[2] =", s)
''')

K.lesson('one-d', 'The global index in one dimension', f'''
<p>Every thread runs the same kernel code. The only thing that differs is its position, given by four built in variables. Each thread uses them to pick its own piece of data.</p>
{table(['Variable', 'Meaning', 'Range'], [
    ['threadIdx.x/y/z', 'my position inside my block', '0 to blockDim − 1'],
    ['blockIdx.x/y/z', 'my block\'s position inside the grid', '0 to gridDim − 1'],
    ['blockDim.x/y/z', 'size of every block', 'set by the launch, at most 1024 threads in total'],
    ['gridDim.x/y/z', 'number of blocks', 'x up to 2³¹ − 1, y and z up to 65,535']])}
{fxs(
    fx('Global index', '<i>i</i> = blockIdx.x × blockDim.x + threadIdx.x', 'Skip all the full blocks before mine, then step to my seat in my block.', key=True),
    fx('Blocks needed', 'blocks = ⌈<i>N</i> ÷ <i>B</i>⌉ = (<i>N</i> + <i>B</i> − 1) ÷ <i>B</i>', 'Whole number division drops the remainder, so adding B − 1 first rounds up.', key=True),
    fx('Going backwards', 'block = ⌊<i>i</i> ÷ <i>B</i>⌋, thread = <i>i</i> − block × <i>B</i>', 'Which thread handles element i.'),
    fx('Idle threads', 'idle = blocks × <i>B</i> − <i>N</i>', 'They fail the guard and do nothing.'))}
{viz('launch1d')}
{scene('cinema seats', '<p>A cinema has rows of 20 seats. Your ticket says row 3, seat 7. Your seat number counting from the very first seat is 3 × 20 + 7 = 67. Rows are blocks, seats are threads, and 20 is blockDim.</p>')}
{steps('Workbook worked example: 10,000 numbers, blocks of 256', [
    'Blocks = (10,000 + 255) ÷ 256 = 10,255 ÷ 256 = 40 (whole number division).',
    'Threads launched = 40 × 256 = 10,240, so 240 are idle.',
    eq('Thread 10 of block 3 handles i = 3 × 256 + 10 = 778')])}
''', kw=['threadIdx', 'blockIdx', 'blockDim', 'gridDim', 'global index', 'round up', 'idle threads'])

K.lesson('two-d', 'dim3, images and two dimensional grids', f'''
<p>Blocks and grids can be 1-D, 2-D or 3-D. The shape is only a way of numbering. It makes images (2-D) and volumes (3-D) easy to map. A missing dimension counts as 1, so <code>dim3 threads(256)</code> means 256 × 1 × 1.</p>
{fxs(
    fx('Pixels in an image', 'col = blockIdx.x × blockDim.x + threadIdx.x<br>row = blockIdx.y × blockDim.y + threadIdx.y<br>memory position = row × width + col', 'Images are stored row by row (row major). x is the column, y is the row.', key=True),
    fx('Grid for a W × H image', 'grid = (⌈W ÷ B<sub>x</sub>⌉, ⌈H ÷ B<sub>y</sub>⌉)', 'Idle threads = all threads − W × H.'),
    fx('Position to one number (x fastest)', 'thread = t<sub>x</sub> + t<sub>y</sub>B<sub>x</sub> + t<sub>z</sub>B<sub>x</sub>B<sub>y</sub><br>block = b<sub>x</sub> + b<sub>y</sub>G<sub>x</sub> + b<sub>z</sub>G<sub>x</sub>G<sub>y</sub><br>global = block × (threads per block) + thread', 'This is how the hardware lines threads up before cutting them into warps.', key=True))}
{viz('index2d')}
{cu('invert.cu', GRID2D, {2: 'x picks the column. Neighbouring threads in a warp have neighbouring x, so they touch neighbouring bytes in memory (good for speed, chapter 3.2).', 3: 'y picks the row.', 4: 'Two guards, one per dimension. The right and bottom edge blocks can hang over the image.', 5: 'Row major: skip row full rows, then step col places.', 11: '16 × 16 = 256 threads per block, 8 warps.', 12: 'Round up in each dimension separately.'})}
{steps('Workbook worked example: a 1920 × 1080 picture with 16 × 16 blocks', [
    'Across: ⌈1920 ÷ 16⌉ = 120 exactly.',
    'Down: ⌈1080 ÷ 16⌉ = 67.5, rounded up to 68.',
    'Blocks = 120 × 68 = 8160. Threads = 8160 × 256 = 2,088,960.',
    eq('Idle = 2,088,960 − 2,073,600 = 15,360 (the half block row at the bottom)')])}
{note('Using 32 × 8 blocks for 1920 × 1080 wastes nothing (1080 ÷ 8 = 135) and each warp covers one full 32 pixel row. Picking a block shape that divides the image is free speed.', 'tip')}
''', kw=['dim3', '2-D grid', 'image indexing', 'row major', 'col row', 'linear index', 'block shape'])

K.lesson('three-d', 'Three dimensions, going backwards, and the slide correction', f'''
{steps('Lecture 3 slides 15 to 16: grid 5 × 4 blocks, each block 5 × 5 threads. Where is global thread 343?', [
    'Threads per block = 25. Block number = ⌊343 ÷ 25⌋ = 13, leftover 343 − 325 = 18.',
    'Block 13 in a grid 5 wide: x = 13 mod 5 = 3, y = ⌊13 ÷ 5⌋ = 2. So blockIdx = (3, 2, 0).',
    'Thread 18 in a block 5 wide: x = 18 mod 5 = 3, y = ⌊18 ÷ 5⌋ = 3. So threadIdx = (3, 3, 0).',
    eq('The slide showed threadIdx (2, 3, 0), which is actually thread 342')])}
{code('where')}
{fx('One number to position', 'block = ⌊g ÷ threads per block⌋, leftover = g − block × threads per block<br>x = leftover mod B<sub>x</sub>, y = ⌊leftover ÷ B<sub>x</sub>⌋', 'The same mod and divide works for the block inside the grid.')}
{note('Exams love going backwards. Always divide by the number of threads per block first, then split the leftover with mod and divide, x first.', 'exam')}
{deep('why the x dimension is special', '<p>Warps are cut from the linear thread number t = x + y B<sub>x</sub> + z B<sub>x</sub>B<sub>y</sub>. So a warp holds 32 consecutive x values (or several short rows if B<sub>x</sub> &lt; 32). Make x the dimension that walks along contiguous memory, and keep B<sub>x</sub> a multiple of 32 when you can.</p>')}
''', kw=['3-D indexing', 'going backwards', 'slide correction', 'mod and divide', 'linearisation'])

K.lesson('patterns', 'Grid stride loops and one thread per row', f'''
<p>Two more patterns finish the picture. A <b>grid stride loop</b> lets a fixed size grid cover any N: each thread handles i, then i plus the total number of threads, and so on. It also reuses each thread\'s set up work and lets you launch just enough blocks to fill the GPU.</p>
{cu('saxpy_stride.cu', STRIDE, {2: 'Start at my global index.', 3: 'Jump by the total number of threads in the grid. With 2 blocks of 8, thread 3 handles 3, 19, 35 and so on.', 4: 'SAXPY: y = a x + y, a classic BLAS routine.'})}
<p><b>One thread per output row.</b> Quiz 1 question 7 launches one thread per row of a matrix vector product: thread i computes the dot product of row i of A with x.</p>
{cu('matvec.cu', MATVEC, {2: 'With one block of 4 threads, thread 2 has i = 0 × 4 + 2 = 2.', 6: 'Row i starts at i × N in the flat row major array.', 8: 'One store per thread.'})}
{code('matvec')}
{note('In matVecMul neighbouring threads read A[i × N + j] for the same j, which are N floats apart. That is a strided, uncoalesced read (chapter 3.2). A transposed layout or one warp per row is faster for large N.', 'warn')}
''', kw=['grid stride loop', 'SAXPY', 'matrix vector', 'one thread per row', 'Quiz 1 question 7'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Every worker gets a badge with a team number and a seat number. From these two numbers each worker knows which piece of the job is theirs.</p>',
    '<p>i = blockIdx.x × blockDim.x + threadIdx.x, blocks = (N + B − 1) / B, guard i &lt; N. In 2-D, col from x, row from y, index row × width + col.</p>',
    '<p>The thread to data mapping decides memory efficiency: let threadIdx.x walk contiguous addresses. Grid stride loops decouple the grid from N and are the default style in libraries.</p>',
    '<p>Persistent kernels launch exactly one wave of blocks that pull work from a queue. Hopper adds thread block clusters, a level between block and grid whose blocks can share memory. Index arithmetic in 64 bits matters once tensors exceed 2³¹ elements.</p>')}
''', kw=['ladder', 'persistent kernels', 'thread block clusters'])

K.quiz('e', 'blockIdx.x = 7, blockDim.x = 128, threadIdx.x = 45. The global index is', ['180', '941', '896', '52'], 1,
       '7 × 128 + 45.', '896 + 45 = 941.')
K.quiz('e', 'dim3 threads(256) describes', ['256 × 256 threads', '256 × 1 × 1 threads', '3 × 256', 'an error'], 1,
       'Missing dimensions are 1.', 'Only x is given.')
K.quiz('e', 'In a row major image, pixel (row, col) is at', ['col × height + row', 'row × width + col', 'row + col', 'row × col'], 1,
       'Skip full rows.', 'Each row holds width pixels.')
K.quiz('m', 'Element 5000 with 256 thread blocks is handled by', ['Block 19, thread 136', 'Block 20, thread 0', 'Block 19, thread 135', 'Block 5, thread 0'], 0,
       '⌊5000 ÷ 256⌋.', '19 × 256 = 4864, and 5000 − 4864 = 136.')
K.quiz('m', 'A 1000 × 1000 image with 16 × 16 blocks needs a grid of', ['62 × 62', '63 × 63', '64 × 64', '1000 × 1'], 1,
       'Round up 1000 ÷ 16 = 62.5.', '63 blocks each way.')
K.quiz('m', 'In a grid stride loop, i increases by', ['1', 'blockDim.x', 'blockDim.x × gridDim.x', 'gridDim.x'], 2,
       'The total number of threads.', 'Every thread jumps over all other threads\' elements.')
K.quiz('m', 'Quiz 1 question 7: y[2] for row [2, 0, 1, 2] and x = [1, 2, 3, 4] is', ['10', '13', '12', '16'], 1,
       'Dot product.', '2 + 0 + 3 + 8 = 13.')
K.quiz('h', 'Grid 5 × 4, block 5 × 5. Global thread 343 is', ['block (3, 2, 0), thread (2, 3, 0)', 'block (3, 2, 0), thread (3, 3, 0)', 'block (2, 3, 0), thread (3, 3, 0)', 'block (13, 0, 0), thread (18, 0, 0)'], 1,
       'Divide by 25 first.', '343 = 13 × 25 + 18. Block 13 = (3, 2), thread 18 = (3, 3). The slide had a slip.')
K.quiz('h', 'Block size (8, 4, 2), thread (3, 2, 1). Thread number inside the block?', ['51', '27', '35', '13'], 0,
       't = x + y Bx + z Bx By.', '3 + 2 × 8 + 1 × 32 = 51.')
K.quiz('h', 'Why should threadIdx.x move along a row of a row major image?', ['It is required by CUDA', 'Warps hold consecutive x, so their reads hit consecutive addresses (coalesced)', 'It uses fewer registers', 'To avoid the guard'], 1,
       'Warps are cut along x.', 'Consecutive lanes then read consecutive bytes.')
K.quiz('x', 'In a 16 × 16 block, warp 3 holds', ['Row 3', 'Rows 6 and 7', 'Columns 6 and 7', 'Threads 3, 35, 67'], 1,
       'Each warp is two rows of 16.', 'Warp 3 holds linear threads 96 to 127, which are rows 6 and 7.')
K.quiz('x', 'Grid (4, 3, 2), block (8, 8, 1). Global thread 1000 is', ['block (3, 0, 1), thread (0, 5, 0)', 'block (0, 3, 1), thread (5, 0, 0)', 'block (15, 0, 0), thread (40, 0, 0)', 'block (3, 1, 1), thread (0, 0, 0)'], 0,
       '64 threads per block.', '1000 = 15 × 64 + 40. Block 15 = (3, 0, 1) in a 4 × 3 grid, thread 40 = (0, 5, 0).')

K.calc('e', 'blockIdx.x = 3, blockDim.x = 256, threadIdx.x = 10. Global index?', '778', 'Skip 3 blocks.',
       ['3 × 256 = 768.', '768 + 10.', eq('i = 778')], check=3 * 256 + 10)
K.calc('e', 'dim3 anotherOne(10, 54, 32): how many elements?', '17280', 'x × y × z.',
       ['10 × 54 = 540.', '540 × 32.', eq('17,280')], check=10 * 54 * 32)
K.calc('e', 'blockIdx (2, 3), blockDim (16, 16), threadIdx (4, 5), width 1024. Memory position?', '54308', 'col, row, then row × width + col.',
       ['col = 2 × 16 + 4 = 36.', 'row = 3 × 16 + 5 = 53.', eq('53 × 1024 + 36 = 54,308')], check=53 * 1024 + 36)
K.calc('m', 'N = 1,000,000, B = 256. Idle threads?', '192', 'Blocks first.',
       ['Blocks = 3907.', 'Threads 3907 × 256 = 1,000,192.', eq('Idle = 192')], check=3907 * 256 - 10 ** 6)
K.calc('m', 'Element 5000, B = 256. Thread number inside its block?', '136', '5000 − block × 256.',
       ['Block ⌊5000 ÷ 256⌋ = 19.', '19 × 256 = 4864.', eq('5000 − 4864 = 136')], check=5000 - 19 * 256)
K.calc('m', '1920 × 1080 image, 16 × 16 blocks. Idle threads?', '15360', 'Grid 120 × 68.',
       ['Blocks 120 × 68 = 8160.', 'Threads 8160 × 256 = 2,088,960.', eq('2,088,960 − 2,073,600 = 15,360')], check=120 * 68 * 256 - 1920 * 1080)
K.calc('m', 'Grid (4, 3, 2), block (8, 8, 1). blockIdx (1, 2, 1), threadIdx (5, 6, 0). Global number?', '1397', 'Block number × 64 + thread number.',
       ['Block = 1 + 2 × 4 + 1 × 12 = 21.', 'Thread = 5 + 6 × 8 = 53.', eq('21 × 64 + 53 = 1397')], check=21 * 64 + 53)
K.calc('h', '8K image 7680 × 4320 with 16 × 16 blocks. Blocks?', '129600', 'Both divide exactly.',
       ['7680 ÷ 16 = 480.', '4320 ÷ 16 = 270.', eq('480 × 270 = 129,600 blocks, no idle threads')], check=480 * 270)
K.calc('h', '1000 × 1000 picture, 16 × 16 blocks. Idle threads?', '16064', 'Grid 63 × 63.',
       ['Threads 63 × 63 × 256 = 1,016,064.', 'Pixels 1,000,000.', eq('Idle 16,064')], check=63 * 63 * 256 - 10 ** 6)
K.calc('x', 'Grid 5 × 4 blocks of 5 × 5. Thread 343: what is threadIdx.x?', '3', '343 mod 25, then mod 5.',
       ['343 = 13 × 25 + 18.', 'Leftover 18: x = 18 mod 5.', eq('x = 3 (y = 3), not 2 as on the slide')], check=(343 % 25) % 5)
K.calc('x', 'Grid stride loop with 2 blocks of 8 over N = 40. How many elements does thread 3 of block 0 handle?', '3', 'Stride 16.',
       ['Start i = 3.', 'Then 19, 35. Next would be 51 ≥ 40.', eq('3 elements')], check=len(range(3, 40, 16)))

K.assign('locate', 'm', 'From global number to blockIdx and threadIdx',
         '<p>Write <code>locate(g, grid, block)</code> for 3-D grid and block sizes given as tuples. Return <code>[[bx, by, bz], [tx, ty, tz]]</code>, x fastest.</p>',
         '''
def locate(g, grid, block):
    # your code here
    pass
''', [("locate(343, (5, 4, 1), (5, 5, 1))", [[3, 2, 0], [3, 3, 0]]), ("locate(1000, (4, 3, 2), (8, 8, 1))", [[3, 0, 1], [0, 5, 0]]), ("locate(778, (40, 1, 1), (256, 1, 1))", [[3, 0, 0], [10, 0, 0]])],
         '''
def locate(g, grid, block):
    Bx, By, Bz = block
    Gx, Gy, Gz = grid
    per = Bx * By * Bz
    b, t = g // per, g % per
    return [[b % Gx, (b // Gx) % Gy, b // (Gx * Gy)], [t % Bx, (t // Bx) % By, t // (Bx * By)]]
''', 'Divide by threads per block first, then split each part with mod and divide.', '<p>The first test is the corrected slide 16 example.</p>')
K.assign('pix', 'e', 'Pixel to memory position',
         '<p>Write <code>pixel_index(bx, by, tx, ty, Bx, By, width)</code> returning row × width + col.</p>',
         '''
def pixel_index(bx, by, tx, ty, Bx, By, width):
    # your code here
    pass
''', [("pixel_index(2, 3, 4, 5, 16, 16, 1024)", 54308), ("pixel_index(0, 0, 0, 0, 16, 16, 640)", 0), ("pixel_index(1, 0, 4, 10, 16, 16, 640)", 6420)],
         '''
def pixel_index(bx, by, tx, ty, Bx, By, width):
    col = bx * Bx + tx
    row = by * By + ty
    return row * width + col
''', 'col from x, row from y.', '<p>The last test is pixel (row 10, col 20) of a 640 wide image.</p>')

K.must('Global index', 'i = blockIdx.x × blockDim.x + threadIdx.x. Blocks = (N + B − 1)/B. Guard i &lt; N. Idle = blocks × B − N.')
K.must('2-D', 'col = bx·Bx + tx, row = by·By + ty, index = row × width + col. Grid = (⌈W/Bx⌉, ⌈H/By⌉), guard both.')
K.must('Linear order', 'thread = tx + ty·Bx + tz·Bx·By (x fastest). Warps are cut from this order.')
K.must('Backwards', 'block = ⌊g ÷ per block⌋, leftover = g mod per block, x = leftover mod Bx, y = ⌊leftover ÷ Bx⌋.')
K.must('Grid stride', 'Start at i = idx, keep going while i &lt; n, and add blockDim.x × gridDim.x each time. A fixed grid then covers any N.')

T = K.topic(
    slug='thread-indexing', topic='thread-indexing', step=(2, 'The CUDA programming model', 'gpu-model', 'Write and launch kernels, index threads in 1, 2 and 3 dimensions, and see how warps and SMs run them and how many fit.', 'College'),
    title='Threads, blocks and grids: indexing in 1-D, 2-D and 3-D', short='Thread indexing', badge='2.2', minutes=50,
    lead='Give every thread its own piece of data: the global index, rounding up, 2-D images, 3-D grids, going backwards from a thread number, and grid stride loops.',
    desc='threadIdx, blockIdx, blockDim and gridDim, the global index and the guard, rounding up and idle threads, dim3, image indexing in row major order, linear thread order, the slide 16 correction, grid stride loops, one thread per row and Quiz 1 question 7.',
    summary='The global index, blocks and idle threads, dim3 and 2-D image indexing, going backwards, grid stride loops and matrix vector per row.',
    keywords=['threadIdx', 'blockIdx', 'blockDim', 'gridDim', 'dim3', 'global index', 'grid stride loop', 'row major'],
    recap='<p>Each thread finds its data from blockIdx, blockDim and threadIdx. Round the grid up, guard the edges, and let x follow contiguous memory.</p>')
