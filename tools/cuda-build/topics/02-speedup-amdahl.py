# Chapter 1.2: speedup, end to end GPU time and Amdahl's law. Source: lecture 1 (battery simulation table, Amdahl's
# law derivation), lecture 3 notes 14.4, lecture 5 quiz (1 percent serial on 61 cores), workbook sections 1.3 and 1.4.
# Beyond the lecture: Gustafson's law (weak scaling) and strong against weak scaling.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('amdahl', r'''
# Amdahl's law: S(N) = 1 / ((1 - P) + P / N)
def speedup(P, N):
    return 1 / ((1 - P) + P / N)

def parallel_fraction(S, N):        # working backwards from a measured speedup
    return (1 - 1 / S) / (1 - 1 / N)

for P in [0.5, 0.9, 0.99]:
    row = [round(speedup(P, N), 2) for N in [4, 16, 256, 4096]]
    print(f"P = {P}: {row}   ceiling {round(1 / (1 - P), 1)}")
print("6x on 16 processors means P =", round(parallel_fraction(6, 16), 3))
print("1% serial on 61 cores:", speedup(0.99, 61))
''')

K.code('endtoend', r'''
# Is the GPU worth it once copies over PCIe are counted?
def copy_ms(bytes_, gb_per_s):
    return bytes_ / (gb_per_s * 1e9) * 1000

grid = 1024 * 1024 * 4          # one float grid in bytes
steps, gpu_step, cpu_step, pcie = 100, 0.05, 9.0, 12
once = copy_ms(grid, pcie) + steps * gpu_step + copy_ms(grid, pcie)
every = steps * (copy_ms(grid, pcie) + gpu_step + copy_ms(grid, pcie))
cpu = steps * cpu_step
print(f"copy once : {once:7.2f} ms, speedup {cpu / once:6.1f}x")
print(f"copy every: {every:7.2f} ms, speedup {cpu / every:6.1f}x")
''')

K.lesson('speedup', 'Speedup and the trip over PCIe', f'''
{fxs(
    fx('Speedup', '<i>S</i> = old time ÷ new time', 'S = 10 means the new version is ten times faster. With FPS, use new FPS ÷ old FPS.', key=True),
    fx('Total GPU time', '<i>T</i><sub>GPU</sub> = <i>T</i><sub>copy in</sub> + <i>T</i><sub>kernel</sub> + <i>T</i><sub>copy out</sub>', 'The GPU is worth it only if T<sub>GPU</sub> &lt; T<sub>CPU</sub>.', key=True),
    fx('Copy time', '<i>T</i><sub>copy</sub> = bytes ÷ bandwidth', 'PCIe 3.0 x16 gives about 12 to 16 GB/s in practice. 12 GB/s = 12 × 10⁹ bytes per second.'))}
<p>The GPU has its own memory. Data lives in the CPU\'s memory first, so it must travel over the PCIe bus to the GPU, and results must travel back. That trip can cost more than the computing.</p>
{scene('a calculator friend across town', '<p>Your friend adds numbers 100 times faster than you, but lives a 30 minute bus ride away. For one sum you do it yourself. For ten thousand sums you take the bus. The bus ride is the PCIe copy.</p>')}
{viz('pcie')}
{table(['Grid', 'CPU (ms)', 'GPU (ms)', 'Shared GPU (ms)', 'GPU speedup'], [
    ['256 × 256', '51.55', '0.48', '0.53', '107.76'], ['512 × 512', '236.54', '1.48', '1.87', '160.28'],
    ['1024 × 1024', '906.35', '5.34', '6.13', '169.79'], ['2048 × 2048', '3593.75', '17.75', '16.32', '202.44']])}
<p>This is the battery heat simulation from lecture 1. The speedup grows with the grid, because a bigger grid gives the GPU more independent cells to hide its fixed costs. Recomputing from the printed times gives slightly different numbers, for example 906.35 ÷ 5.34 ≈ 169.7, because the slide used more decimals.</p>
{code('endtoend')}
{note('Keep data on the GPU across many kernel launches. Copy in once, run all time steps, copy out once. Copying every step can turn a 158 times speedup into 12 times (workbook P1.3.5).', 'warn')}
''', kw=['speedup', 'PCIe', 'copy time', 'end to end time', 'battery simulation', 'bandwidth'])

K.lesson('amdahl', "Amdahl's law", f'''
<p>Split a program into a part that can run in parallel (fraction P of the time on one processor) and a part that cannot (1 − P). With N processors the parallel part shrinks to P ÷ N, the serial part stays.</p>
{fxs(
    fx("Amdahl's law", '<i>S</i>(<i>N</i>) = 1 ÷ [ (1 − <i>P</i>) + <i>P</i> ÷ <i>N</i> ]', 'P is the parallel fraction measured on one processor, N the number of processors.', key=True),
    fx('The ceiling', '<i>S</i><sub>max</sub> = 1 ÷ (1 − <i>P</i>)', 'Let N grow without limit. 95 percent parallel can never beat 20 times.', key=True),
    fx('Working backwards', '<i>P</i> = (1 − 1/<i>S</i>) ÷ (1 − 1/<i>N</i>)', 'From a measured speedup S on N processors.'),
    fx('Efficiency', '<i>E</i> = <i>S</i> ÷ <i>N</i>', 'How much of each processor is really used.'),
    fx('Speeding up one part s times', '<i>S</i> = 1 ÷ [ (1 − <i>p</i>) + <i>p</i> ÷ <i>s</i> ]', 'The same law for any part p that gets s times faster, for example a kernel.'))}
{viz('amdahl')}
{steps('Derivation in four lines', [
    'Time on one processor: T₁ = (1 − P)T₁ + PT₁.',
    'On N processors only the parallel part is divided: T<sub>N</sub> = (1 − P)T₁ + PT₁ ÷ N.',
    'Speedup S = T₁ ÷ T<sub>N</sub>. The T₁ cancels.',
    eq('S(N) = 1 ÷ [(1 − P) + P ÷ N], and as N → ∞, S → 1 ÷ (1 − P)')])}
{steps('Lecture 5 quiz: 1 percent serial, 61 cores', [
    '1 − P = 0.01 and P ÷ N = 0.99 ÷ 61 ≈ 0.016230.',
    'Denominator 0.01 + 0.016230 = 0.026230.',
    'S = 1 ÷ 0.026230 ≈ 38.125.',
    eq('Efficiency 38.125 ÷ 61 = 62.5 percent. Ceiling 1 ÷ 0.01 = 100')])}
{code('amdahl')}
{scene('cooking for a wedding', '<p>Fifty cooks can chop vegetables together, but the biryani must still simmer for 40 minutes in one pot. Adding cooks shortens the chopping, never the simmering. That 40 minutes is the serial part.</p>')}
{note('P is a fraction of the time on one processor, not a fraction of the lines of code. A tiny loop that runs for 90 percent of the time gives P = 0.9.', 'warn')}
''', kw=["Amdahl's law", 'parallel fraction', 'ceiling', 'efficiency', 'serial part', 'derivation'])

K.lesson('gustafson', "Gustafson's law and scaling (beyond the lecture)", f'''
<p>Amdahl keeps the problem size fixed. In practice people buy a bigger GPU to solve a bigger problem in the same time: a finer heat grid, a larger batch, a longer video. Then the parallel work grows with N while the serial part stays about the same.</p>
{fx("Gustafson's law (scaled speedup)", '<i>S</i><sub>scaled</sub> = <i>N</i> − (1 − <i>P</i>)(<i>N</i> − 1)', 'Here P is the parallel share of the time measured on the N processor run. The speedup grows almost in a straight line with N.', key=True)}
{table(['', 'Strong scaling (Amdahl)', 'Weak scaling (Gustafson)'], [
    ['What is fixed', 'Total problem size', 'Work per processor'],
    ['Question asked', 'How much faster does the same job finish?', 'How much bigger a job fits in the same time?'],
    ['Limit', '1 ÷ (1 − P)', 'Grows with N'],
    ['GPU example', 'One 1024 × 1024 grid on more SMs', 'Grid grows from 1024² to 4096² with a bigger GPU']])}
{steps('Example: P = 0.9 on 64 processors', [
    'Amdahl: S = 1 ÷ (0.1 + 0.9 ÷ 64) = 1 ÷ 0.1140625 ≈ 8.77.',
    'Gustafson: S = 64 − 0.1 × 63 = 64 − 6.3.',
    eq('= 57.7. Both are right. They answer different questions')])}
{note('In an exam, Amdahl is the default unless the question says the problem grows with the number of processors.', 'exam')}
''', kw=["Gustafson's law", 'strong scaling', 'weak scaling', 'scaled speedup'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Extra helpers only speed up the part of a job that can be shared. The part that must be done by one person sets the limit.</p>',
    '<p>S = 1 ÷ ((1 − P) + P ÷ N), ceiling 1 ÷ (1 − P). Count copy in plus kernel plus copy out. Use P = (1 − 1/S) ÷ (1 − 1/N) to measure how parallel a program is.</p>',
    '<p>Amdahl applies to every part of a pipeline: a 10 times faster kernel inside an 8.66 ms frame where the kernel is 1.65 ms gives only about 1.21 times overall (workbook P1.4.7). Profile first, then speed up the biggest part.</p>',
    '<p>Hill and Marty extended Amdahl to multicore chip design (few big cores against many small ones), and asymmetric chips like CPU plus GPU systems follow from it. Overlapping copies with compute (chapter 6.2) and unified memory with prefetching attack the serial copy term directly.</p>')}
{steps('Work it out: the frame that will not speed up (workbook P1.4.7)', [
    'Frame 8.66 ms, kernel 1.65 ms, so p = 1.65 ÷ 8.66 ≈ 0.1905.',
    'Kernel gets s = 10 times faster: S = 1 ÷ (0.8095 + 0.01905).',
    eq('S ≈ 1.21. The copies are the real bottleneck')])}
{deep('break even size for a GPU', '<p>If the CPU takes 2 ns per element and the GPU takes a fixed 50 µs plus 0.2 ns per element, the GPU wins when 2n &gt; 50,000 + 0.2n, so n &gt; 27,778 elements. At 10 million elements the speedup is 20 ms ÷ 2.05 ms ≈ 9.76 (workbook P1.3.6). Every GPU decision has a break even size like this.</p>')}
''', kw=['ladder', 'profile first', 'break even', 'Hill and Marty'])

K.quiz('e', 'Speedup is', ['new time ÷ old time', 'old time ÷ new time', 'old time − new time', 'cores × clock'], 1,
       'Bigger is better.', 'S = old ÷ new. A drop from 10 s to 2 s is a speedup of 5.')
K.quiz('e', 'A program is 95 percent parallel. The most speedup possible is', ['95', '20', '19', 'unlimited'], 1,
       '1 ÷ (1 − P).', '1 ÷ 0.05 = 20.')
K.quiz('e', 'Total GPU time must include', ['Only the kernel', 'Copy in, kernel and copy out', 'Only the copies', 'The CPU time'], 1,
       'The data travels both ways.', 'Data crosses PCIe to the GPU and the result comes back.')
K.quiz('m', 'P = 0.8 on 4 processors gives a speedup of', ['4', '3.2', '2.5', '2'], 2,
       '1 ÷ (0.2 + 0.2).', '1 ÷ 0.4 = 2.5, not 4.')
K.quiz('m', 'Why did the battery simulation speedup grow with grid size?', ['Bigger grids use less memory', 'More independent cells hide the fixed overheads', 'The CPU got slower', 'Copies vanish'], 1,
       'More parallel work.', 'Fixed launch and copy costs are spread over more cells.')
K.quiz('m', 'Efficiency E = S ÷ N for the 61 core quiz (S = 38.125) is about', ['38 percent', '62.5 percent', '100 percent', '1.6 percent'], 1,
       '38.125 ÷ 61.', 'Each core is used 62.5 percent of the time on average.')
K.quiz('m', "Gustafson's law assumes", ['The problem size is fixed', 'The work per processor is fixed, so the problem grows with N', 'No serial part', 'Infinite bandwidth'], 1,
       'Weak scaling.', 'It measures how a bigger problem fits in the same time.')
K.quiz('h', 'A kernel inside a frame becomes 10 times faster but the frame only gets 1.21 times faster. Why?', ['A measuring error', 'The kernel was only 19 percent of the frame, the copies dominate', 'GPUs cannot speed up', 'Warps diverged'], 1,
       "Amdahl on the kernel's share.", 'With p ≈ 0.19 the rest of the frame caps the gain.')
K.quiz('h', 'Copying a grid in and out every time step instead of once', ['Has no effect', 'Multiplies the copy cost by the number of steps and can wipe out the speedup', 'Makes the kernel faster', 'Is required by CUDA'], 1,
       'P1.3.5.', '158 times becomes about 12 times.')
K.quiz('x', 'A measured speedup of 6 on 16 processors means the parallel fraction is about', ['0.375', '0.889', '0.6', '0.95'], 1,
       'P = (1 − 1/S) ÷ (1 − 1/N).', '(1 − 1/6) ÷ (1 − 1/16) = 0.8333 ÷ 0.9375 ≈ 0.889.')
K.quiz('x', 'With P = 0.99, how many processors give 90 percent of the ceiling of 100?', ['90', '100', '891', '9900'], 2,
       'Solve 1 ÷ (0.01 + 0.99/N) = 90.', '0.01 + 0.99/N = 1/90, so 0.99/N = 0.001111, N = 891.')

K.calc('e', '512 × 512 grid: CPU 236.54 ms, GPU 1.48 ms. Speedup? (one decimal)', '159.8', 'Old ÷ new.',
       ['Old time 236.54 ms.', 'New time 1.48 ms.', eq('236.54 ÷ 1.48 ≈ 159.8 (slide: 160.28)')], check=236.54 / 1.48, tol=0.05)
K.calc('e', 'P = 0.6 and N = 8. Speedup? (two decimals)', '2.11', '1 ÷ (0.4 + 0.075).',
       ['Serial 1 − P = 0.4.', 'Parallel P ÷ N = 0.6 ÷ 8 = 0.075.', eq('S = 1 ÷ 0.475 ≈ 2.11')], check=1 / (0.4 + 0.075), tol=0.005)
K.calc('e', 'Copy 36 MB over PCIe at 12 GB/s. Time in ms?', '3', 'bytes ÷ bandwidth.',
       ['36 MB = 36 × 10⁶ bytes.', '12 GB/s = 12 × 10⁹ bytes per second.', eq('36 × 10⁶ ÷ 12 × 10⁹ = 0.003 s = 3 ms')], check=36e6 / 12e9 * 1000, unit='ms')
K.calc('m', 'CPU 2 ms. GPU: copy in 3 ms, kernel 0.5 ms, copy out 3 ms. End to end speedup? (two decimals)', '0.31', 'Add the three GPU parts.',
       ['T<sub>GPU</sub> = 3 + 0.5 + 3 = 6.5 ms.', 'S = 2 ÷ 6.5.', eq('≈ 0.31, a slowdown, even though the kernel alone is 4 times faster')], check=2 / 6.5, tol=0.005)
K.calc('m', 'A team measures 6 times on 16 processors. Parallel fraction P? (three decimals)', '0.889', 'Work backwards.',
       ['1 − 1/S = 1 − 1/6 = 0.8333.', '1 − 1/N = 1 − 1/16 = 0.9375.', eq('P = 0.8333 ÷ 0.9375 ≈ 0.889')], check=(1 - 1 / 6) / (1 - 1 / 16), tol=0.0005)
K.calc('m', 'P = 0.9 and N = 100. Speedup? (two decimals)', '9.17', 'Close to but below 10.',
       ['Serial 0.1.', 'Parallel 0.9 ÷ 100 = 0.009.', eq('S = 1 ÷ 0.109 ≈ 9.17')], check=1 / 0.109, tol=0.005)
K.calc('m', '1 percent serial on 61 cores. Speedup? (three decimals)', '38.125', 'Lecture 5 quiz.',
       ['Denominator 0.01 + 0.99 ÷ 61.', '= 0.01 + 0.016230 = 0.026230.', eq('S = 38.125')], check=1 / (0.01 + 0.99 / 61), tol=0.0005)
K.calc('h', 'P = 0.99. Smallest N that reaches 90 percent of the ceiling (90 times)?', '891', 'Set S = 90 and solve.',
       ['1 ÷ (0.01 + 0.99/N) = 90 gives 0.01 + 0.99/N = 0.011111.', '0.99/N = 0.001111.', eq('N = 891')], check=round(0.99 / (1 / 90 - 0.01)))
K.calc('h', '90 percent of a job moves to a GPU that runs it 1000 times faster. Overall speedup? (two decimals)', '9.91', 'Amdahl with s = 1000.',
       ['Serial 0.1 stays.', 'Accelerated part 0.9 ÷ 1000 = 0.0009.', eq('S = 1 ÷ 0.1009 ≈ 9.91, never more than 10')], check=1 / 0.1009, tol=0.005)
K.calc('h', 'CPU 2 ns per element. GPU 50 µs fixed plus 0.2 ns per element. Break even size? (whole elements, round up)', '27778', 'Solve 2n = 50,000 + 0.2n.',
       ['1.8n = 50,000 ns.', 'n = 27,777.8.', eq('From about 27,778 elements the GPU is faster')], check=27778)
K.calc('x', 'Gustafson: P = 0.9 measured on 64 processors. Scaled speedup? (one decimal)', '57.7', 'N − (1 − P)(N − 1).',
       ['(1 − P)(N − 1) = 0.1 × 63 = 6.3.', '64 − 6.3.', eq('57.7')], check=64 - 0.1 * 63, tol=0.05)
K.calc('x', '100 steps of a 1024 × 1024 float grid: GPU 0.05 ms per step, PCIe 12 GB/s, copy in and out once. GPU total in ms? (two decimals)', '5.70', 'Two copies of 4,194,304 bytes plus 100 kernels.',
       ['One copy = 4,194,304 ÷ 12 × 10⁹ s ≈ 0.3495 ms.', 'Two copies ≈ 0.699 ms. Kernels 100 × 0.05 = 5 ms.', eq('Total ≈ 5.70 ms against 900 ms on the CPU (about 158 times)')], check=2 * 4194304 / 12e9 * 1000 + 5, tol=0.005)

K.assign('amd', 'e', "Amdahl's law",
         '<p>Write <code>amdahl(P, N)</code> returning the speedup rounded to 3 decimals.</p>',
         '''
def amdahl(P, N):
    # your code here
    pass
''', [("amdahl(0.8, 4)", 2.5), ("amdahl(0.99, 61)", 38.125), ("amdahl(0.9, 100)", 9.174)],
         '''
def amdahl(P, N):
    return round(1 / ((1 - P) + P / N), 3)
''', 'One over serial plus parallel divided by N.', '<p>These are the workbook and lecture 5 numbers.</p>')
K.assign('worth', 'm', 'Is the GPU worth it?',
         '<p>Write <code>gpu_wins(cpu_ms, bytes_in, bytes_out, gbps, kernel_ms)</code> that returns True when copy in + kernel + copy out (in ms) is less than the CPU time.</p>',
         '''
def gpu_wins(cpu_ms, bytes_in, bytes_out, gbps, kernel_ms):
    # your code here
    pass
''', [("gpu_wins(2, 36e6, 36e6, 12, 0.5)", False), ("gpu_wins(900, 4194304, 4194304, 12, 5)", True), ("gpu_wins(1.0, 8e6, 4e6, 12, 0.003)", False)],
         '''
def gpu_wins(cpu_ms, bytes_in, bytes_out, gbps, kernel_ms):
    copy = (bytes_in + bytes_out) / (gbps * 1e9) * 1000
    return copy + kernel_ms < cpu_ms
''', 'Convert bytes ÷ (GB/s × 10⁹) seconds to ms.', '<p>The last test is vector add of a million floats: the copies alone take about 1 ms, so the GPU loses.</p>')

K.must('Speedup', 'S = old ÷ new. Count copy in + kernel + copy out. Copy time = bytes ÷ bandwidth (PCIe about 12 to 16 GB/s).')
K.must("Amdahl", 'S(N) = 1 ÷ ((1 − P) + P/N). Ceiling 1 ÷ (1 − P). Efficiency S ÷ N. Back: P = (1 − 1/S) ÷ (1 − 1/N).')
K.must('Part speedup', 'Speeding a part p by s gives 1 ÷ ((1 − p) + p/s). Speed up the biggest part first.')
K.must("Gustafson", 'Scaled speedup N − (1 − P)(N − 1) when the problem grows with N (weak scaling).')
K.must('Keep data on the GPU', 'Copy once, run many kernels, copy back once. Small jobs have a break even size below which the CPU wins.')

T = K.topic(
    slug='speedup-amdahl', topic='speedup-amdahl', step=(1, 'Why GPUs', 'gpu-why', 'Why a chip with thousands of slow cores beats a few fast ones, how to measure speed, and how much a GPU can ever help.', 'School'),
    title="Speedup, the PCIe trip and Amdahl's law", short='Speedup and Amdahl', badge='1.2', minutes=45,
    lead="Measure speedup honestly with the copies included, then use Amdahl's law to see how much a GPU can ever help, and Gustafson's law for problems that grow.",
    desc="Speedup, copy in, kernel and copy out, the battery simulation table, Amdahl's law with its derivation, ceiling, efficiency and working backwards, the lecture 5 quiz, speeding up one part, break even sizes, and Gustafson's law with strong and weak scaling.",
    summary="Speedup with copies counted, Amdahl's law and its ceiling, working backwards, Gustafson's law, and break even sizes.",
    keywords=['speedup', "Amdahl's law", "Gustafson's law", 'PCIe', 'efficiency', 'strong scaling', 'weak scaling'],
    recap='<p>The serial part of a program and the copies over PCIe limit any GPU speedup. Measure end to end and speed up the biggest part first.</p>')
