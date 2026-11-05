# Chapter 1.3: the first two GPU workloads of the course. Source: lecture 1 (battery heat simulation: PDE, finite
# difference rule, why it is parallel; image recognition pipeline and the inference study, MobileNet and depthwise
# separable convolution), lecture 6 (stability of the explicit heat update), workbook sections 1.5 and 1.6.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

K.code('rod', r'''
# 1-D heat rod with fixed ends: T_new[i] = T[i] + a*(T[i-1] + T[i+1] - 2*T[i])
T = [0, 0, 100, 0, 0]
a = 0.25
for step in range(2):
    new = T[:]                       # a second buffer: read old, write new
    for i in range(1, len(T) - 1):   # the ends stay fixed
        new[i] = T[i] + a * (T[i - 1] + T[i + 1] - 2 * T[i])
    T = new
    print("after step", step + 1, T)
''')

K.code('convcount', r'''
# Multiplications of a normal and a depthwise separable convolution
def normal(H, W, cin, cout, k):
    return H * W * cin * cout * k * k
def separable(H, W, cin, cout, k):
    depthwise = H * W * cin * k * k     # one k x k filter per input channel
    pointwise = H * W * cin * cout      # 1 x 1 convolution mixes the channels
    return depthwise + pointwise

n, s = normal(32, 32, 64, 128, 3), separable(32, 32, 64, 128, 3)
print("normal   ", n)
print("separable", s)
print("ratio    ", round(s / n, 4), "=", round((9 + 128) / (9 * 128), 4))
''')

HEAT = r'''
// One time step of the 2-D heat simulation. One thread updates one cell.
__global__ void heatStep(const float* Told, float* Tnew, int n,
                         float alpha, float betaQ) {
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (row < 1 || col < 1 || row >= n - 1 || col >= n - 1) return;
    int i = row * n + col;
    float lap = Told[i - n] + Told[i + n] + Told[i - 1] + Told[i + 1]
              - 4.0f * Told[i];
    Tnew[i] = Told[i] + alpha * lap + betaQ;
}
'''

K.lesson('heat', 'Workload 1: a battery heat simulation', f'''
<p>Engineers who design cooling for electric scooter and car batteries need to know how heat spreads through a battery pack. Lecture 1 showed a student project that simulated this on a CPU and a GPU.</p>
{fx('The heat equation', '∂<i>T</i>/∂<i>t</i> = α (∂²<i>T</i>/∂<i>x</i>² + ∂²<i>T</i>/∂<i>y</i>²) + <i>Q</i>', 'T is temperature, α the thermal diffusivity (how fast heat spreads), Q the heat the battery makes itself.')}
{fxs(
    fx('2-D update rule (5 points)', '<i>T</i><sup>new</sup> = <i>T</i> + α (up + down + left + right − 4<i>T</i>) + β<i>Q</i>', 'New temperature = old temperature + heat from the four neighbours + heat made inside.', key=True),
    fx('1-D version', '<i>T</i><sup>new</sup> = <i>T</i> + α (left + right − 2<i>T</i>) + β<i>Q</i>', 'The same idea along a rod.'),
    fx('How much work', 'cells = height × width<br>updates = cells × time steps', 'A 1024 × 1024 grid has 1,048,576 cells per step.'))}
<p>The bracket is the finite difference version of the second derivative (the Laplacian). It says how much hotter or colder the four neighbours are than the cell itself. If all neighbours equal the cell, nothing changes.</p>
{viz('heat')}
{steps('Worked example from the workbook', [
    'A cell at 25 degrees has neighbours up 20, down 30, left 25, right 35. α = 0.1 and βQ = 0.5.',
    'Neighbour sum = 20 + 30 + 25 + 35 = 110. Four times the cell = 100.',
    'Difference 110 − 100 = 10, times α = 1.',
    eq('T<sup>new</sup> = 25 + 1 + 0.5 = 26.5 degrees')])}
<p><b>Why this is perfect GPU work.</b> Each cell needs only its own old value and four neighbours. No cell depends on another cell\'s new value in the same step. So one thread per cell can update the whole grid at once.</p>
{cu('heat_step.cu', HEAT, {2: 'Two separate grids: every thread reads old values and writes new ones, so no thread reads a value that another thread has already changed in this step.', 4: 'Each thread works out which column it owns. Chapter 2.2 explains this formula.', 6: 'Border cells are held fixed. Threads outside the grid or on the border do nothing.', 8: 'The 2-D grid is stored row by row in 1-D memory, so the cell above is n places back and the one below n places ahead.', 9: 'The four neighbours minus four times the cell: the discrete Laplacian.', 10: 'The update rule from the lecture.'}, title='preview of chapter 2')}
{code('rod')}
{note('A GPU heat code must keep two buffers. If threads wrote into the same grid they read from, some would read a neighbour\'s new value and some its old value, and the answer would depend on timing.', 'warn')}
{deep('stability: why α must be small', '<p>Rewrite the 2-D rule as T<sup>new</sup> = (1 − 4α)T + α(sum of neighbours). Every weight must be zero or positive or the scheme amplifies errors. So 1 − 4α ≥ 0, α ≤ 0.25 in 2-D (and α ≤ 0.5 in 1-D, α ≤ 1/6 in 3-D). With α = 0.3 the centre weight is −0.2 and the simulation blows up. This is the explicit scheme stability limit, and in physical units α Δt ÷ h² must stay below the same bound.</p>')}
''', kw=['heat equation', 'finite difference', 'update rule', 'Laplacian', 'stencil', 'two buffers', 'stability'])

K.lesson('vision', 'Workload 2: image recognition and convolution cost', f'''
<p>Lecture 1\'s second example was an image recognition pipeline: a camera frame goes through convolution layers, pooling and dense layers to a label. Almost all of the time is spent in convolutions, which are millions of multiply adds that do not depend on each other. That again is GPU work.</p>
{fxs(
    fx('Normal convolution', 'mults = <i>H</i> × <i>W</i> × <i>C</i><sub>in</sub> × <i>C</i><sub>out</sub> × <i>K</i> × <i>K</i>', 'Every output pixel of every output channel looks at a K × K patch of every input channel.', key=True),
    fx('Depthwise separable', 'depthwise = <i>H W C</i><sub>in</sub> <i>K</i>²<br>pointwise = <i>H W C</i><sub>in</sub> <i>C</i><sub>out</sub>', 'First one K × K filter per input channel, then a 1 × 1 convolution that mixes channels. MobileNet uses this.'),
    fx('Saving ratio', 'separable ÷ normal = (<i>K</i>² + <i>C</i><sub>out</sub>) ÷ (<i>K</i>² × <i>C</i><sub>out</sub>)', 'For many output channels this tends to 1 ÷ K², so at most 9 times fewer for 3 × 3 filters.', key=True))}
{viz('sepconv')}
{steps('Worked example: K = 3, 64 to 128 channels, 32 × 32 output', [
    'Normal: 32 × 32 × 64 × 128 × 9 = 75,497,472.',
    'Depthwise: 32 × 32 × 64 × 9 = 589,824.',
    'Pointwise: 32 × 32 × 64 × 128 = 8,388,608.',
    'Separable total = 8,978,432.',
    eq('Ratio = (9 + 128) ÷ (9 × 128) = 137 ÷ 1152 ≈ 0.119, about 8.4 times fewer')])}
{code('convcount')}
{scene('why MobileNet runs on your phone', '<p>Your phone camera can recognise faces and food in real time because networks like MobileNet use depthwise separable convolutions. In the lecture study, MobileNetV2 had more layers than a plain CNN but ran faster, because each layer needs far fewer multiplications.</p>')}
{note('Fewer multiplications does not always mean proportionally faster on a GPU. Depthwise layers do little work per byte loaded, so they are often limited by memory, not maths (chapter 4.2).', 'tip')}
''', kw=['image recognition', 'convolution cost', 'depthwise separable', 'pointwise', 'MobileNet', 'saving ratio'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>To find tomorrow\'s temperature of a spot, look at its neighbours today. Every spot can do this at the same moment, so thousands of helpers can work together.</p>',
    '<p>Explicit finite difference: T<sup>new</sup> = T + α(neighbours − 4T) + βQ, stable for α ≤ 0.25 in 2-D. Convolution cost H W C<sub>in</sub> C<sub>out</sub> K², separable saving (K² + C<sub>out</sub>) ÷ (K² C<sub>out</sub>).</p>',
    '<p>Both workloads are stencils: each output reads a small fixed neighbourhood. Neighbouring threads read overlapping inputs, so loading a tile with a halo into shared memory cuts global reads (chapters 5.3 and 5.4). That is why the "Shared GPU" column of the battery table exists.</p>',
    '<p>Production codes use implicit or multigrid solvers for stiff heat problems, temporal blocking to reuse data across time steps, and for CNNs the convolution is turned into a matrix multiply (im2col) or computed with Winograd or FFT methods on tensor cores.</p>')}
{steps('Work it out: a rod with fixed ends (workbook P1.5.4)', [
    'Start [0, 0, 100, 0, 0], α = 0.25.',
    'Step 1: middle 100 + 0.25(0 + 0 − 200) = 50. Its neighbours 0 + 0.25(0 + 100 − 0) = 25. Rod [0, 25, 50, 25, 0].',
    'Step 2: middle 50 + 0.25(25 + 25 − 100) = 37.5. Neighbours 25 + 0.25(0 + 50 − 50) = 25.',
    eq('[0, 25, 37.5, 25, 0]')])}
''', kw=['ladder', 'stencil', 'halo', 'im2col', 'Winograd'])

K.quiz('e', 'In the heat rule, what does the bracket (up + down + left + right − 4T) measure?', ['The heat source', 'How different the neighbours are from the cell', 'The time step', 'The grid size'], 1,
       'The Laplacian.', 'If every neighbour equals the cell, the bracket is 0 and nothing changes.')
K.quiz('e', 'How many cells does a 2048 × 2048 grid have?', ['4,096', '4,194,304', '2,048,000', '1,048,576'], 1,
       '2048 squared.', '2048 × 2048 = 4,194,304.')
K.quiz('e', 'Why is the heat update good GPU work?', ['It uses doubles', 'Each cell needs only old values of itself and its neighbours, so all cells update at once', 'It has no loops', 'It is serial'], 1,
       'Independence.', 'No cell waits for another cell\'s new value within a step.')
K.quiz('m', 'Why keep two copies of the grid?', ['To save memory', 'So no thread reads a value another thread already updated in this step', 'For the CPU', 'CUDA requires it'], 1,
       'Read old, write new.', 'Mixing old and new values makes the result depend on thread timing.')
K.quiz('m', 'A grid where every cell is 50 with no heat source after one update is', ['0', '50', '100', '25'], 1,
       'Neighbours equal the cell.', 'The bracket is 0, so the cell stays 50, a handy check.')
K.quiz('m', 'Depthwise separable convolution first', ['Mixes all channels with 1 × 1 filters', 'Filters each input channel separately with K × K, then mixes with 1 × 1', 'Uses no multiplications', 'Pools the image'], 1,
       'Depthwise then pointwise.', 'Spatial filtering per channel, then channel mixing.')
K.quiz('m', 'The saving ratio of a separable 3 × 3 convolution with 256 output channels is about', ['0.5', '0.115', '0.9', '0.01'], 1,
       '(9 + 256) ÷ (9 × 256).', '265 ÷ 2304 ≈ 0.115.')
K.quiz('h', 'The largest safe α for the explicit 2-D heat rule is', ['0.5', '0.25', '1', '1/6'], 1,
       'Centre weight 1 − 4α.', 'All weights must be non negative, so α ≤ 0.25.')
K.quiz('h', 'As C<sub>out</sub> grows very large, a separable 7 × 7 convolution approaches', ['7 times fewer', '49 times fewer', '14 times fewer', 'no saving'], 1,
       'Ratio tends to 1 ÷ K².', '1 ÷ 49 of the work.')
K.quiz('x', 'In the CUDA heat kernel, the cell below (row + 1) in a row major n × n grid is at index', ['i + 1', 'i + n', 'i − n', 'i × n'], 1,
       'One full row ahead.', 'Moving down one row skips n elements.')
K.quiz('x', 'Why can depthwise layers run slower than their FLOP count suggests on a GPU?', ['They need doubles', 'They do little work per byte loaded, so memory bandwidth limits them', 'They cannot be parallel', 'They need atomics'], 1,
       'Arithmetic intensity.', 'Each input is used only K² times per channel, so the layer is memory bound.')

K.calc('e', 'Cells updated per step on a 2048 × 2048 grid?', '4194304', 'Rows × columns.',
       ['2048 rows.', '2048 columns.', eq('2048 × 2048 = 4,194,304')], check=2048 * 2048)
K.calc('e', 'Rod [10, 20, 40], update only the middle with α = 0.2, no heat source.', '22', 'left + right − 2T.',
       ['left + right − 2T = 10 + 40 − 40 = 10.', 'α × 10 = 2.', eq('20 + 2 = 22')], check=20 + 0.2 * (10 + 40 - 40))
K.calc('e', 'Cell 25 with neighbours 20, 30, 25, 35, α = 0.1, βQ = 0.5. New temperature?', '26.5', 'Add the bracket times α and the source.',
       ['Bracket 110 − 100 = 10.', 'α × 10 = 1.', eq('25 + 1 + 0.5 = 26.5')], check=25 + 0.1 * 10 + 0.5)
K.calc('m', '512 × 512 grid, 1000 steps, 8 FLOPs per update. Total FLOPs?', '2097152000', 'cells × steps × 8.',
       ['Cells 262,144.', 'Updates 262,144 × 1000 = 262,144,000.', eq('× 8 = 2,097,152,000 FLOPs')], check=512 * 512 * 1000 * 8)
K.calc('m', 'Two float grids of 1024 × 1024. Bytes of memory?', '8388608', '2 × cells × 4 bytes.',
       ['Cells 1,048,576.', 'One grid 4,194,304 bytes.', eq('Two grids 8,388,608 bytes = 8 MiB')], check=2 * 1024 * 1024 * 4)
K.calc('m', 'Normal 3 × 3 convolution, 56 × 56 output, 64 to 64 channels. Multiplications?', '115605504', 'H W Cin Cout K².',
       ['56 × 56 = 3136.', '3136 × 64 × 64 = 12,845,056.', eq('× 9 = 115,605,504')], check=56 * 56 * 64 * 64 * 9)
K.calc('m', 'Same layer, depthwise separable. Multiplications?', '14651392', 'Depthwise plus pointwise.',
       ['Depthwise 3136 × 64 × 9 = 1,806,336.', 'Pointwise 3136 × 64 × 64 = 12,845,056.', eq('Total 14,651,392 (about 0.127 of normal)')], check=56 * 56 * 64 * 9 + 56 * 56 * 64 * 64)
K.calc('h', 'Saving ratio for a 5 × 5 filter with 32 output channels? (three decimals)', '0.071', '(K² + Cout) ÷ (K² Cout).',
       ['K² = 25.', '(25 + 32) ÷ (25 × 32) = 57 ÷ 800.', eq('≈ 0.071, about 14 times fewer')], check=57 / 800, tol=0.0005)
K.calc('h', 'The normal layer above (115,605,504 multiply adds) on an 8 TFLOP/s GPU. Time in µs? (one decimal)', '28.9', 'FLOPs = 2 × multiply adds.',
       ['FLOPs = 231,211,008.', 'Time = 231,211,008 ÷ 8 × 10¹² s.', eq('≈ 28.9 µs at peak')], check=2 * 115605504 / 8e12 * 1e6, tol=0.05, unit='µs')
K.calc('x', 'Rod [0, 0, 100, 0, 0], fixed ends, α = 0.25. Middle value after two steps?', '37.5', 'Do step 1 fully first.',
       ['Step 1: [0, 25, 50, 25, 0].', 'Step 2 middle: 50 + 0.25(25 + 25 − 100) = 50 − 12.5.', eq('37.5')], check=50 + 0.25 * (25 + 25 - 100))
K.calc('x', 'Largest safe α for the explicit 3-D heat rule (six neighbours)? (four decimals)', '0.1667', 'Centre weight 1 − 6α ≥ 0.',
       ['3-D rule: T<sup>new</sup> = (1 − 6α)T + α × (six neighbours).', 'Need 1 − 6α ≥ 0.', eq('α ≤ 1/6 ≈ 0.1667')], check=1 / 6, tol=0.00005)

K.assign('heat1d', 'm', 'One step of the heat rod',
         '<p>Write <code>heat_step(T, a)</code> that returns a NEW list after one 1-D update with fixed ends and no heat source. Do not change <code>T</code> while you read it.</p>',
         '''
def heat_step(T, a):
    # your code here
    pass
''', [("heat_step([0, 0, 100, 0, 0], 0.25)", [0, 25.0, 50.0, 25.0, 0]), ("heat_step([50, 50, 50], 0.2)", [50, 50.0, 50]), ("heat_step([10, 20, 40], 0.2)", [10, 22.0, 40])],
         '''
def heat_step(T, a):
    new = T[:]
    for i in range(1, len(T) - 1):
        new[i] = T[i] + a * (T[i - 1] + T[i + 1] - 2 * T[i])
    return new
''', 'Copy the list first, read from the old one, write into the copy.', '<p>Reading and writing the same list would use a neighbour\'s new value, the bug the GPU code avoids with two buffers.</p>')
K.assign('sep', 'e', 'Convolution saving',
         '<p>Write <code>saving(k, cout)</code> returning separable ÷ normal rounded to 4 decimals.</p>',
         '''
def saving(k, cout):
    # your code here
    pass
''', [("saving(3, 128)", 0.1189), ("saving(3, 256)", 0.115), ("saving(5, 32)", 0.0712)],
         '''
def saving(k, cout):
    return round((k * k + cout) / (k * k * cout), 4)
''', 'The H, W and C<sub>in</sub> cancel out.', '<p>The ratio depends only on K and C<sub>out</sub>.</p>')

K.must('Heat rule', 'T_new = T + α(up + down + left + right − 4T) + βQ. 1-D uses −2T. Updates = cells × steps.')
K.must('Why parallel', 'Each cell needs only old neighbour values, so one thread per cell. Keep two buffers (old and new).')
K.must('Stability', 'Explicit scheme: α ≤ 1/2 in 1-D, 1/4 in 2-D, 1/6 in 3-D, or values blow up.')
K.must('Convolution cost', 'Normal H W Cin Cout K². Separable H W Cin K² + H W Cin Cout. Ratio (K² + Cout) ÷ (K² Cout) → 1/K².')
K.must('Same pattern', 'Heat updates and convolutions are stencils: each output reads a small neighbourhood. Tiling with halos speeds them up later.')

T = K.topic(
    slug='first-workloads', topic='first-workloads', step=(1, 'Why GPUs', 'gpu-why', 'Why a chip with thousands of slow cores beats a few fast ones, how to measure speed, and how much a GPU can ever help.', 'School'),
    title='First GPU workloads: heat simulation and convolution', short='First workloads', badge='1.3', minutes=40,
    lead='Turn the heat equation into an update rule that thousands of threads can run at once, and count the work of normal and depthwise separable convolutions.',
    desc='The battery heat simulation: PDE, finite difference update in 1-D and 2-D, why it is parallel, two buffers, stability limits, a first CUDA kernel, and the image recognition pipeline with normal and depthwise separable convolution counts and MobileNet.',
    summary='The heat simulation update rule and its stability, why it suits a GPU, and normal against depthwise separable convolution cost.',
    keywords=['heat simulation', 'finite difference', 'stencil', 'stability', 'convolution', 'depthwise separable', 'MobileNet'],
    recap='<p>Both workloads compute each output from a small neighbourhood of old values, which is exactly what thousands of GPU threads do well.</p>')
