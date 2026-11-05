# Chapter 10.3: Exam revision. A one page formula sheet in three groups, every slide correction found while writing the
# subject (each one is explained in its own chapter), the traps that cost marks, and mixed problems with fresh numbers.
# T4 figures used: 40 SMs, 64 FP32 cores per SM, 1.59 GHz boost, 320 GB/s, 1024 threads and 16 blocks per SM (CC 7.5).
# Every number below was recomputed in Python (see the code cell).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

K.code('mixed', r'''
import math
peak = 40 * 64 * 2 * 1.59            # T4 FP32 GFLOP/s
print("T4 peak:", round(peak, 1), " ridge:", round(peak / 320, 2))
print("blur naive and cached:", 17 / 40 * 320, 17 / 8 * 320)
n, B = 1_000_000, 256
blocks = math.ceil(n / B)
print("blocks:", blocks, " idle:", blocks * B - n, " warps:", blocks * B // 32,
      " waves:", math.ceil(blocks / (40 * (1024 // B))))
print("reduction adds:", 2048 * 511, " plus atomics:", 2048)
print("Amdahl 80 percent at 50x:", round(1 / (0.2 + 0.8 / 50), 2))
''')

K.lesson('plan', 'How to revise in one week', f'''
<p>This chapter collects the whole subject on a few screens. Use it the week before the exam, after you have worked through the chapters.</p>
{table(['Day', 'What to do', 'Chapters'], [
    ['1', 'Speed and limits: speedup, Amdahl, peak, roofline. Redo the formula cards below from memory.', '1.1 to 1.3, 4.2'],
    ['2', 'Threads: indexing forwards and backwards, warps, occupancy. Do the launch problem below by hand.', '2.1 to 2.4'],
    ['3', 'Memory: hierarchy, coalescing, banks, tiling. Draw one warp and count sectors.', '3.1 to 3.3, 5.2'],
    ['4', 'Patterns: reduction, stencils, convolution, scan, histogram.', '5.1 to 5.5'],
    ['5', 'Concurrency: divergence, streams, races, locks, barriers, atomics.', '6.1 to 7.2'],
    ['6', 'Modern GPUs: number formats, tensor cores, fast matmul, tools.', '4.1, 8.1 to 9.2'],
    ['7', 'Quiz 1 again under time, then three challenge problems.', '10.1, 10.2'],
])}
{note('Most lost marks come from counting the wrong thing: threads instead of warps, loads per thread instead of per block, bytes one way instead of both. Write the unit next to every number.', 'exam')}
<p>The code below recomputes the mixed problems at the end of this chapter.</p>
{code('mixed')}
''', kw=['revision plan', 'exam', 'one week'])

K.lesson('limits', 'Formula sheet 1: speed and limits', f'''
{fxs(
    fx('Speedup and efficiency', 'S = T<sub>old</sub> ÷ T<sub>new</sub>, &nbsp; E = S ÷ N', 'Count copy in, kernel and copy out in T<sub>new</sub>.', key=True),
    fx('Amdahl (fixed problem)', 'S(N) = 1 ÷ ((1 − P) + P ÷ N), &nbsp; ceiling 1 ÷ (1 − P)', 'P is the parallel fraction of the old time.', key=True),
    fx('Gustafson (problem grows)', 'S(N) = (1 − P) + P N', 'Weak scaling: the parallel work grows with N.'),
    fx('Peak FLOP/s', 'peak = SMs × cores per SM × 2 × clock', 'The 2 is one FMA per core per cycle.', key=True),
    fx("Little's law", 'in flight = latency × throughput', 'Warps needed = in flight ÷ 32. Bytes in flight = bandwidth × latency.'),
    fx('Arithmetic intensity', 'AI = FLOPs ÷ bytes moved', 'Count bytes read and written.', key=True),
    fx('Roofline', 'attainable = min(peak, AI × bandwidth), &nbsp; ridge = peak ÷ bandwidth', 'Left of the ridge: memory bound. Right: compute bound.', key=True),
    fx('Time bound', 't ≥ max(FLOPs ÷ peak, bytes ÷ bandwidth)', 'The larger term tells you what to fix.'),
)}
{viz('amdahl')}
{viz('roofline')}
''', kw=['formula sheet', 'speedup', 'Amdahl', 'Gustafson', 'peak', 'roofline', 'ridge'])

K.lesson('threads', 'Formula sheet 2: threads and memory', f'''
{fxs(
    fx('Global index and blocks', 'i = blockIdx.x × blockDim.x + threadIdx.x, &nbsp; blocks = ⌈N ÷ B⌉', 'Guard with i &lt; N. Idle threads = blocks × B − N.', key=True),
    fx('Going backwards', 'block = ⌊g ÷ (B<sub>x</sub>B<sub>y</sub>)⌋, x = r mod B<sub>x</sub>, y = ⌊r ÷ B<sub>x</sub>⌋', 'r is the leftover g − block × B<sub>x</sub>B<sub>y</sub>.'),
    fx('Warps', 'warps per block = ⌈B ÷ 32⌉, &nbsp; lane = t mod 32', 't = x + y B<sub>x</sub> + z B<sub>x</sub>B<sub>y</sub>, x moves fastest.', key=True),
    fx('Occupancy', 'blocks per SM = min(threads, blocks, registers, shared memory limits)', 'Occupancy = active warps ÷ max warps per SM.', key=True),
    fx('Coalescing', 'sectors per warp load = distinct 32 byte pieces touched', 'Floats: stride 1 gives 4 sectors, stride 8 or more gives 32.'),
    fx('Bank conflicts', 'degree = gcd(stride, 32)', 'Same word for all lanes is a broadcast. Pad rows to 33.', key=True),
    fx('Matmul loads', 'naive 2N³, &nbsp; tiled 2N³ ÷ T', 'Per thread 2N against 2N ÷ T. Tile AI in FP32 is T ÷ 4.', key=True),
    fx('Halo tiles', 'loads per output = (B + 2R)<sup>d</sup> ÷ B<sup>d</sup>', 'd is the number of dimensions, R the radius.'),
)}
{viz('launch1d')}
{viz('occupancy')}
{viz('banks')}
''', kw=['formula sheet', 'indexing', 'warps', 'occupancy', 'coalescing', 'banks', 'tiling'])

K.lesson('patterns', 'Formula sheet 3: patterns, concurrency and number formats', f'''
{fxs(
    fx('Reduction tree', 'log₂ B levels, B − 1 additions, 1 + log₂ B barriers', 'One atomic per block joins the blocks.', key=True),
    fx('Scans', 'Hillis and Steele n log₂ n − (n − 1) adds in log₂ n steps, Blelloch 2(n − 1) adds in 2 log₂ n steps', 'Blelloch does less work, Hillis and Steele has fewer steps.', key=True),
    fx('Divergence', 'efficiency = busy lane ticks ÷ (32 × total ticks)', 'Paths inside one warp run one after the other.'),
    fx('Pipeline', 'T = (a + b + c) + (n − 1) × max(a, b, c)', 'Equal stages give speedup 3n ÷ (n + 2).', key=True),
    fx('Waves', 'waves = ⌈blocks ÷ (SMs × blocks per SM)⌉', 'A last wave that is almost empty wastes most of the GPU.'),
    fx('Float value', 'x = (−1)<sup>s</sup> × 1.m × 2<sup>e − bias</sup>, &nbsp; bias = 2<sup>E − 1</sup> − 1', 'FP32 1/8/23, FP16 1/5/10, BF16 1/8/7, TF32 1/8/10.', key=True),
    fx('Symmetric INT8', 's = max|x| ÷ 127, &nbsp; q = round(x ÷ s)', 'Error at most s ÷ 2 unless a value is clipped.'),
    fx('Interleavings', '(n s)! ÷ (s!)<sup>n</sup>', 'n threads with s steps each. Two threads of 3 steps: 20 orders.'),
)}
{viz('reduce')}
{viz('streams')}
{viz('formats')}
''', kw=['formula sheet', 'reduction', 'scan', 'divergence', 'pipeline', 'waves', 'floating point', 'quantisation'])

K.lesson('corrections', 'Every slide correction in one table', f'''
<p>While writing this subject every worked example in the notes was recomputed. These are the places where the slides or the class notes say something that does not hold. Each chapter explains the fix in full.</p>
{table(['Where', 'The slide or class said', 'What is right', 'Chapter'], [
    ['Lecture 3, slide 16', 'Global thread 343 has threadIdx (2, 3, 0)', 'It is (3, 3, 0). (2, 3, 0) is thread 342.', '2.2'],
    ['Lecture 3, mapping', 'Grids sit inside cores', 'A thread runs on a core lane, a block on one SM, a grid across the GPU.', '2.3'],
    ['Lecture 4, slide 11', 'Asynchrony is risky because kernels overwrite each other', 'Work in one stream runs in order. The risk is the CPU reading before the GPU is done.', '6.2'],
    ['Lecture 5 notes', '1.00101 in binary = 1.5625', '1.00101 in binary = 1.15625 = 37 ÷ 32.', '4.1'],
    ['Lecture 6, slide 14', 'Heat weights 0.25 centre and 0.1 for 6 neighbours', 'They add to 0.85, so heat leaks away. The centre must be 0.4.', '5.3'],
    ['Lecture 7, slide 6', 'Threads 0 to 21 write out of bounds', 'All 32 threads write out of bounds (indices 10 to 41).', '9.1'],
    ['Lecture 7, slide 8', 'The plain matmul reads Width² values', 'Each of the Width² threads reads 2 × Width, so 2 × Width³ in total.', '5.2'],
    ['Lecture 8', 'Sharpening pixel 30 gives 35', '5 × 30 − (25 + 35 + 20 + 40) = 30.', '5.4'],
    ['Lecture 9, slide 11', 'Bars show exact format speeds', 'The bars are illustrative. TF32 is a compute mode, not a storage format.', '8.1'],
    ['Lecture 9, slide 16', 'The C tile lives in shared memory', 'In real kernels the C tile stays in registers. Only the epilogue uses shared memory.', '8.2'],
    ['Lecture 9 blog numbers', 'Ridge about 410', 'With the numbers used in class the ridge is about 378.', '8.3'],
    ['Lecture 10, slide 8', 'Attempt 2 deadlocks', 'Attempt 2 breaks mutual exclusion. Attempt 3 is the one that deadlocks.', '7.1'],
    ['Lecture 10, class', 'Peterson does not solve the problem', 'Peterson is correct when memory is in order, so on a GPU it needs fences.', '7.1'],
    ['Lecture 11 code', 'critical_kernel is safe as written', 'It can hang before Volta and needs __threadfence. The priority counter skips levels.', '7.2'],
])}
{note('If an exam question copies one of these slides, answer with the right value and add one line saying why. Markers reward the reasoning.', 'exam')}
''', kw=['slide corrections', 'errata', 'lecture notes'])

K.lesson('traps', 'The traps that cost marks', f'''
{table(['Trap', 'Do this instead'], [
    ['Counting threads when the question asks for warps', 'Divide by 32 and round up per block, then multiply by blocks.'],
    ['Loads per thread when the question says per block', 'Multiply by threads per block. Quiz 1 question 2: 256 × 2048 = 524,288.'],
    ['Forgetting the write in bytes moved', 'SAXPY reads x and y and writes y: 12 bytes per element.'],
    ['Taking FMA as 1 FLOP', 'One FMA is 2 FLOPs, a multiply and an add.'],
    ['Putting __syncthreads inside a divergent if', 'Every thread of the block must reach every barrier.'],
    ['Treating occupancy as the goal', 'Enough warps to hide latency is enough. Measure, do not maximise.'],
    ['Reading GB as 2<sup>30</sup> bytes in bandwidth', 'Bandwidth uses 10<sup>9</sup> bytes per GB.'],
    ['Forgetting the reserved 1 KB of shared memory per block', 'On CC 8.x, blocks = ⌊pool ÷ (bytes + 1 KB)⌋.'],
    ['Thinking divergence happens across warps', 'Different warps may take different paths for free. Only lanes inside one warp diverge.'],
    ['Amdahl with N where the question gives a speedup of a part', 'Use 1 ÷ ((1 − p) + p ÷ s) with s the speedup of that part.'],
])}
{viz('diverge')}
''', kw=['common mistakes', 'exam traps', 'units'])

K.lesson('mixed', 'Mixed problems with fresh numbers', f'''
<p>Each problem joins two or more chapters. The numbers are new, so you cannot remember the answer, you have to work it out.</p>
{steps('Problem A. A T4 has 40 SMs with 64 FP32 cores each at 1.59 GHz and 320 GB/s. A 3 × 3 blur does 9 multiplies and 8 adds per pixel. Is it memory or compute bound, without and with perfect reuse of input pixels?', [
    'Peak = 40 × 64 × 2 × 1.59 = 8140.8 GFLOP/s. Ridge = 8140.8 ÷ 320 = 25.44 FLOP/byte.',
    'Without reuse each pixel reads 9 floats and writes 1: 40 bytes for 17 FLOPs, AI = 0.425. Attainable 0.425 × 320 = 136 GFLOP/s.',
    'With perfect reuse each pixel reads 1 float and writes 1: 8 bytes, AI = 2.125, attainable 680 GFLOP/s.',
    eq('Memory bound either way. Tiling gives up to 5 times, but the ceiling is still 680 of 8141 GFLOP/s')])}
{steps('Problem B. Launch one thread per element for N = 1,000,000 with 256 threads per block on that T4 (1024 threads and 16 blocks per SM). Give the blocks, idle threads, total warps and waves.', [
    'Blocks = ⌈1,000,000 ÷ 256⌉ = 3907. Threads launched = 1,000,192, so 192 are idle.',
    'Warps = 3907 × 8 = 31,256.',
    'Blocks per SM: threads allow 1024 ÷ 256 = 4, the block cap allows 16, so 4. One wave holds 40 × 4 = 160 blocks.',
    eq('Waves = ⌈3907 ÷ 160⌉ = 25, the last one 42 percent full')])}
{steps('Problem C. Sum 2<sup>20</sup> floats with 512 threads per block, a tree in shared memory and one atomic per block. Count blocks, levels, barriers per block and all additions.', [
    'Blocks = 2<sup>20</sup> ÷ 512 = 2048. Levels = log₂ 512 = 9. Barriers = 1 after loading + 9 = 10.',
    'Additions inside blocks = 2048 × 511 = 1,046,528. Atomics = 2048.',
    'Together 1,048,576 = 2<sup>20</sup>, one addition per input value counting the add onto the zero total.',
    eq('Same work as a serial sum, in 9 levels instead of 1,048,575 steps')])}
{steps('Problem D. You sum 4096 ones in FP16. What do you get, and why does a tensor core avoid it?', [
    'FP16 has 10 mantissa bits, so the gap between numbers at 2048 is 2<sup>11 − 10</sup> = 2.',
    '2048 + 1 = 2049 lies halfway, and round to nearest even gives 2048. Every later add is lost.',
    'Tensor cores take FP16 inputs but add in FP32, where the gap at 2048 is far below 1.',
    eq('FP16 sum = 2048, FP32 accumulator = 4096')])}
{steps('Problem E. Copies take 20 percent of a job and the kernel takes 80 percent. You make the kernel 50 times faster. What is the overall speedup, and what should you do next?', [
    'Speedup of a part: 1 ÷ ((1 − p) + p ÷ s) with p = 0.8 and s = 50.',
    '1 ÷ (0.2 + 0.016) = 1 ÷ 0.216 = 4.63.',
    'The copies are now 0.2 ÷ 0.216 = 93 percent of the time.',
    eq('4.63 times. Next: keep data on the GPU or overlap the copies with streams')])}
{viz('peak')}
''', kw=['mixed problems', 'T4', 'roofline', 'waves', 'reduction', 'FP16', 'Amdahl'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A GPU is fast when many small jobs run at once and the data is close by. Almost every formula here counts one of those two things.</p>',
    '<p>For any kernel, write down threads, warps, bytes, FLOPs and the limiting resource. Then pick the formula.</p>',
    '<p>Combine models: roofline for the ceiling, occupancy and Little\'s law for latency hiding, waves for the tail, Amdahl for the copies.</p>',
    '<p>Research on GPU kernels checks these models against Nsight measurements and then attacks the gap, as in the fast matmul ladder of chapter 8.3.</p>')}
''', kw=['ladder', 'summary'])

K.quiz('e', 'Ridge point of a GPU with 8 TFLOP/s and 320 GB/s', ['2.5', '25', '40', '250'], 1, '8000 ÷ 320.', '25 FLOP per byte.')
K.quiz('e', 'Warps in a block of 100 threads', ['3', '4', '100', '1'], 1, 'Round up.', '⌈100 ÷ 32⌉ = 4.')
K.quiz('e', 'Global index of thread 5 in block 3 with 64 threads per block', ['197', '200', '67', '320'], 0, '3 × 64 + 5.', '197.')
K.quiz('m', 'Stride 4 floats in shared memory', ['Conflict free', '2 way', '4 way', '8 way'], 2, 'gcd(4, 32).', '4 way.')
K.quiz('m', 'Lecture 3 slide 16: thread 343 in blocks of 5 × 5 has threadIdx', ['(2, 3, 0)', '(3, 3, 0)', '(3, 2, 0)', '(18, 0, 0)'], 1, '343 − 325 = 18.', 'The slide shows (2, 3, 0), which is thread 342.')
K.quiz('m', 'Heat weights 0.25 centre and 0.1 for 6 neighbours', ['Are correct', 'Leak heat, the centre should be 0.4', 'Should be 0.5', 'Are unstable for any step'], 1, 'Weights must add to 1.', '0.25 + 0.6 = 0.85.')
K.quiz('m', 'Attempt 2 of Dekker breaks', ['Progress', 'Mutual exclusion', 'Nothing', 'Bounded waiting only'], 1, 'Both can enter.', 'The slide calls it a deadlock, which is attempt 3.')
K.quiz('h', 'A T4 runs 3907 blocks of 256 threads with 4 blocks per SM on 40 SMs. Waves', ['24', '25', '98', '4'], 1, '⌈3907 ÷ 160⌉.', '25.')
K.quiz('h', 'Summing 4096 ones in FP16 gives', ['4096', '2048', '4095', 'Infinity'], 1, 'Gap at 2048 is 2.', '2048 + 1 rounds back to 2048.')
K.quiz('h', 'A job with 20 percent copies and an 80 percent kernel made 50 times faster speeds up by', ['50', '4.63', '5', '40'], 1, 'Amdahl for a part.', '1 ÷ 0.216.')
K.quiz('x', 'A 3 × 3 FP32 blur on a T4 with perfect reuse is', ['Compute bound', 'Memory bound at about 680 GFLOP/s', 'Bound by PCIe', 'At the ridge'], 1, 'AI 2.125 against ridge 25.4.', 'Memory bound.')
K.quiz('x', 'In real tiled GEMM kernels the C tile lives during the main loop in', ['Shared memory', 'Registers', 'Global memory', 'Constant memory'], 1, 'Correction to lecture 9 slide 16.', 'Registers.')

K.calc('e', 'T4 FP32 peak in GFLOP/s: 40 SMs, 64 cores, 1.59 GHz (one decimal)?', '8140.8', 'SMs × cores × 2 × clock.',
       ['40 × 64 = 2560 cores.', '× 2 × 1.59.', eq('8140.8 GFLOP/s')], check=8140.8, tol=0.1)
K.calc('e', 'Blocks for N = 1,000,000 with 256 threads?', '3907', 'Round up.',
       ['1,000,000 ÷ 256 = 3906.25.', 'Round up.', eq('3907')], check=3907)
K.calc('e', 'Idle threads in that launch?', '192', 'blocks × B − N.',
       ['3907 × 256 = 1,000,192.', '− 1,000,000.', eq('192')], check=192)
K.calc('m', 'T4 ridge point (two decimals)?', '25.44', 'peak ÷ bandwidth.',
       ['8140.8 ÷ 320.', '= 25.44.', eq('25.44 FLOP/byte')], check=25.44, tol=0.01)
K.calc('m', 'Attainable GFLOP/s of the naive 3 × 3 blur on a T4?', '136', 'AI × bandwidth.',
       ['AI = 17 ÷ 40 = 0.425.', '× 320.', eq('136 GFLOP/s')], check=136)
K.calc('m', 'Barriers per block in a 512 thread tree reduction?', '10', '1 + log₂ 512.',
       ['Load barrier 1.', '9 levels.', eq('10')], check=10)
K.calc('m', 'Interleavings of two threads with 3 steps each?', '20', '6! ÷ (3! 3!).',
       ['720 ÷ 36.', '= 20.', eq('20')], check=20)
K.calc('h', 'Waves for 3907 blocks, 4 blocks per SM, 40 SMs?', '25', '⌈3907 ÷ 160⌉.',
       ['One wave 160 blocks.', '3907 ÷ 160 = 24.4.', eq('25')], check=25)
K.calc('h', 'Overall speedup: 80 percent kernel made 50 times faster (two decimals)?', '4.63', '1 ÷ (0.2 + 0.8 ÷ 50).',
       ['0.8 ÷ 50 = 0.016.', '1 ÷ 0.216.', eq('4.63')], check=4.63, tol=0.01)
K.calc('x', 'Symmetric INT8 scale for values in [−6.35, 6.35]?', '0.05', 's = max|x| ÷ 127.',
       ['6.35 ÷ 127.', '= 0.05.', eq('s = 0.05')], check=0.05, tol=0.0001)

K.assign('ridge', 'm', 'Roofline in one function',
         '<p>Write <code>roofline(peak, bw, flops, nbytes)</code> with peak in GFLOP/s and bw in GB/s. Return [ridge rounded to 2 decimals, "memory" or "compute", attainable GFLOP/s rounded to 1 decimal]. A kernel exactly at the ridge counts as "compute".</p>',
         '''
def roofline(peak, bw, flops, nbytes):
    # your code here
    pass
''', [("roofline(8140.8, 320, 17, 40)", [25.44, "memory", 136.0]), ("roofline(19500, 1555, 2 * 4096 ** 3, 3 * 4 * 4096 ** 2)", [12.54, "compute", 19500.0]),
      ("roofline(1000, 100, 10, 1)", [10.0, "compute", 1000.0]), ("roofline(8140.8, 320, 2, 12)", [25.44, "memory", 53.3])],
         '''
def roofline(peak, bw, flops, nbytes):
    ai = flops / nbytes
    ridge = peak / bw
    kind = "compute" if ai >= ridge else "memory"
    return [round(ridge, 2), kind, round(float(min(peak, ai * bw)), 1)]
''', 'AI = flops ÷ bytes, compare with peak ÷ bw.', '<p>The second test is a 4096 FP32 matmul on an A100 with each matrix moved once: AI 682.7, far right of the ridge.</p>')
K.assign('launch', 'h', 'Plan a launch',
         '<p>Write <code>launch_plan(n, block, sms, max_threads, max_blocks)</code>. Return [blocks, idle threads, warps per block, waves], where blocks per SM is the smaller of max_threads ÷ block (rounded down) and max_blocks.</p>',
         '''
def launch_plan(n, block, sms, max_threads, max_blocks):
    # your code here
    pass
''', [("launch_plan(1000000, 256, 40, 1024, 16)", [3907, 192, 8, 25]), ("launch_plan(1000, 100, 2, 1024, 16)", [10, 0, 4, 1]),
      ("launch_plan(2048, 32, 1, 2048, 32)", [64, 0, 1, 2]), ("launch_plan(1, 1024, 108, 2048, 32)", [1, 1023, 32, 1])],
         '''
def launch_plan(n, block, sms, max_threads, max_blocks):
    blocks = -(-n // block)
    per_sm = min(max_threads // block, max_blocks)
    waves = -(-blocks // (sms * per_sm))
    return [blocks, blocks * block - n, -(-block // 32), waves]
''', '-(-a // b) is ceil for positive whole numbers.', '<p>The third test hits the block cap: 2048 ÷ 32 = 64 threads allow 64 blocks, but only 32 fit.</p>')

K.must('Three formula groups', 'Speed and limits (Amdahl, peak, roofline), threads and memory (index, warps, occupancy, banks, tiling), patterns (reduction, scan, pipeline, formats).')
K.must('Write the unit', 'Threads or warps, per thread or per block, bytes read and written, FMA = 2 FLOPs, GB = 10⁹ bytes.')
K.must('Slide corrections', 'Thread 343 is (3, 3, 0). Heat centre 0.4. Width³ loads. Sharpen gives 30. Attempt 2 breaks mutual exclusion. C tile in registers.')
K.must('T4 numbers', '40 SMs, 8.14 TFLOP/s FP32, 320 GB/s, ridge 25.4, 1024 threads and 16 blocks per SM.')
K.must('Next step rule', 'Memory bound: reuse data (tiles). Copy bound: keep data on the GPU or overlap. Latency bound: more warps or more independent work.')

T = K.topic(
    slug='exam-revision', topic='exam-revision', step=(10, 'Exam practice', 'gpu-exam', 'Quiz 1 solved, hard problems in the style of top university courses, and a final revision.', 'Pro'),
    title='Exam revision', short='Exam revision', badge='10.3', minutes=45,
    lead='The whole subject on a few screens: a one week plan, three formula sheets, every slide correction, the traps that cost marks, and mixed problems with fresh numbers.',
    desc='A one week revision plan, formula sheets for speed and limits, threads and memory, and patterns and formats, a table of every slide correction, common exam traps, and five mixed problems on a T4 with full steps.',
    summary='Formula sheets, slide corrections, traps and mixed problems.',
    keywords=['revision', 'formula sheet', 'slide corrections', 'exam traps', 'mixed problems'],
    recap='<p>Count the right thing with the right unit, pick the matching formula, and check against a second method. The tables in this chapter list every formula and every correction you need.</p>')
