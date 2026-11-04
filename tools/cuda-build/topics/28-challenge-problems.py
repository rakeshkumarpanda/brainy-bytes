# Chapter 10.2: Challenge problems. Original multi step problems written in the style of the hardest exam and
# homework questions of well known parallel computing courses (for example UIUC ECE 408 and its textbook by Kirk and Hwu,
# Stanford CS149, CMU 15-418, and the GPU and HPC courses of the IITs and IISc). They are not copied from those courses.
# Every number was recomputed in Python. Hardware limits used: A100 (CC 8.0) 65,536 registers, 2048 threads, 32 blocks,
# up to 164 KB shared memory per SM with 1 KB reserved per block.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

K.code('check', r'''
# Recompute the answers of this chapter
r = 989 / 3.35
import math
# AI = n B / (n + 2B) > r  gives  B > r n / (n - 2r)
print("P1 H100 batch:", math.floor(r * 4096 / (4096 - 2 * r)) + 1)
r2 = 312 / 1.555
print("P1 1024 layer on A100:", math.floor(r2 * 1024 / (1024 - 2 * r2)) + 1)
blocks = min(65536 // (40 * 256), 2048 // 256, 32, 164 // (20 + 1))
print("P2 blocks:", blocks, " occupancy:", blocks * 8 / 64)
print("P4 Hillis-Steele adds:", 1024 * 10 - 1023, " Blelloch adds:", 2 * 1023)
print("P5 BM + BN limit:", 48 * 1024 // (2 * 32 * 4))
print("P6 divergence efficiency:", round((8 * 20 + 24 * 10) / (32 * 30), 3))
print("P7 Amdahl:", round(1 / (0.05 + 0.95 / 1024), 2), " Gustafson:", round(0.05 + 0.95 * 1024, 2))
''')

K.lesson('intro', 'How to use these problems', f'''
<p>These problems are harder than the chapter exercises. Each one joins two or three ideas, the way graduate exams do. They are original problems written in the style of courses such as UIUC ECE 408, Stanford CS149 and CMU 15-418, not copies of their papers.</p>
<p>Try each problem on paper first. Then open the steps. Use the widget to check your picture. The code below recomputes every answer on this page.</p>
{code('check')}
''', kw=['challenge', 'exam style', 'graduate level'])

K.lesson('p1', 'Problem 1: when does batching pay off?', f'''
<p><b>Problem.</b> (a) An H100 SXM does 989 TFLOP/s in BF16 and moves 3.35 TB/s. From which batch is a 4096 × 4096 fully connected layer math limited? (b) Repeat for a 1024 × 1024 layer on an A100 (312 TFLOP/s, 1.555 TB/s). (c) Explain why the smaller layer needs a bigger batch.</p>
{steps('Solution (a)', [
    'Ridge = 989 ÷ 3.35 = 295.2 FLOP/byte.',
    'Need 4096 B ÷ (4096 + 2B) > 295.2.',
    '(4096 − 590.4) B > 295.2 × 4096, so B > 344.9.',
    eq('B ≥ 345')])}
{steps('Solution (b) and (c)', [
    'For an n × n layer, AI = n B ÷ (n + 2B). With n = 1024 and ridge 200.6: 1024 B > 200.6 (1024 + 2B).',
    '622.7 B > 205,455, so B > 329.9.',
    'Fewer weights means less reuse to spread the activation traffic over.',
    eq('B ≥ 330 for the 1024 layer, against 223 for the 4096 layer')])}
{viz('roofline')}
''', kw=['batch threshold', 'H100', 'arithmetic intensity', 'FC layer'])

K.lesson('p2', 'Problem 2: the occupancy puzzle', f'''
<p><b>Problem.</b> A kernel on an A100 uses 256 threads per block, 40 registers per thread and 20 KB of shared memory per block. Which limit binds, and what is the occupancy? What is the cheapest change that reaches 100 percent?</p>
{steps('Solution', [
    'Registers: 40 × 256 = 10,240 per block. 65,536 ÷ 10,240 = 6.4, so 6 blocks.',
    'Threads: 2048 ÷ 256 = 8 blocks. Block limit: 32.',
    'Shared memory: 20 KB + 1 KB reserved = 21 KB. 164 ÷ 21 = 7.8, so 7 blocks.',
    'The smallest is 6 (registers): 6 × 8 = 48 warps of 64.',
    eq('75 percent, limited by registers')])}
<p>To reach 8 blocks the kernel needs at most 65,536 ÷ (8 × 256) = 32 registers per thread (for example with __launch_bounds__(256, 8)), and at most 164 ÷ 8 − 1 = 19.5 KB of shared memory per block. Forcing registers down can cause spills to local memory, so measure before and after.</p>
{viz('occupancy')}
''', kw=['occupancy', 'registers', 'shared memory', 'launch_bounds', 'A100'])

K.lesson('p3', 'Problem 3: banks, strides and padding', f'''
<p><b>Problem.</b> Thread t of a warp reads <code>s[t × k]</code> from a float array in shared memory (32 banks of 4 bytes). (a) Give the conflict degree for k = 1, 2, 6, 8, 32. (b) Prove the rule. (c) A 32 × 32 tile is read by column. Show why padding each row to 33 floats removes the conflict.</p>
{fxs(
    fx('Conflict degree for stride k', 'degree = gcd(k, 32)', 'Thread t goes to bank (t k) mod 32.', key=True))}
{steps('Solution', [
    'Threads t and u share a bank when (t − u) k is a multiple of 32, which means (t − u) is a multiple of 32 ÷ gcd(k, 32).',
    'So each bank is hit by gcd(k, 32) threads: k = 1 gives 1, k = 2 gives 2, k = 6 gives 2, k = 8 gives 8, k = 32 gives 32.',
    'Column read of a 32 × 32 tile: element (t, c) sits at 32 t + c, stride 32, a 32 way conflict.',
    'With rows of 33: address 33 t + c, stride 33, and gcd(33, 32) = 1.',
    eq('Padding to 33 makes every column read conflict free')])}
{viz('banks')}
''', kw=['bank conflicts', 'gcd', 'stride', 'padding', 'shared memory'])

K.lesson('p4', 'Problem 4: work against steps in scan', f'''
<p><b>Problem.</b> An inclusive scan of n = 1024 values. (a) How many additions do Hillis and Steele and Blelloch each do? (b) How many parallel steps? (c) With 1024 threads, which one finishes first and which one is better on a GPU with far fewer lanes than n?</p>
{fxs(
    fx('Hillis and Steele', 'adds = n log₂ n − (n − 1), steps = log₂ n', 'Step d updates n − 2<sup>d</sup> elements.'),
    fx('Blelloch', 'adds = 2 (n − 1), steps = 2 log₂ n', 'Up sweep then down sweep.', key=True))}
{steps('Solution', [
    'Hillis and Steele: 1024 × 10 − 1023 = 9217 additions in 10 steps.',
    'Blelloch: 2 × 1023 = 2046 additions in 20 steps.',
    'With enough lanes, Hillis and Steele wins on steps.',
    'With few lanes the total work decides, and Blelloch does 4.5 times less.',
    eq('Short arrays in one block: Hillis and Steele. Large arrays: Blelloch, which is work efficient')])}
{viz('scan')}
''', kw=['scan', 'Hillis Steele', 'Blelloch', 'work efficiency', 'span'])

K.lesson('p5', 'Problem 5: choose the tile under a budget', f'''
<p><b>Problem.</b> A FP32 matmul block keeps a BM × 32 strip of A and a 32 × BN strip of B in shared memory, double buffered, within 48 KB. (a) What is the largest BM + BN? (b) Which square tile maximises AI, and what AI does it reach? (c) At 2 TB/s, what speed can it reach from DRAM traffic alone?</p>
{steps('Solution', [
    'Shared memory = 2 buffers × (BM + BN) × 32 × 4 bytes ≤ 49,152.',
    'So BM + BN ≤ 192.',
    'For a fixed sum, BM × BN is largest when BM = BN = 96.',
    'AI = (2 ÷ 4) × 96 × 96 ÷ 192 = 24 FLOP/byte.',
    eq('24 × 2 TB/s = 48 TFLOP/s ceiling from DRAM traffic')])}
<p>In practice tiles are powers of two (64 or 128) for simple indexing, so 64 × 128 (AI 21.3) or a smaller BK are chosen. That is the kind of trade off the matmul ladder makes at every step.</p>
{viz('tileai')}
''', kw=['tile size', 'shared memory budget', 'double buffering', 'arithmetic intensity'])

K.lesson('p6', 'Problem 6: divergence, overlap and scaling', f'''
<p><b>Problem A.</b> In one warp, threads with tid &lt; 8 run path A of 20 instructions, the others path B of 10. What is the warp time and the lane efficiency? How would you rearrange the data to remove the loss?</p>
{steps('Solution A', [
    'Both paths run one after the other: 20 + 10 = 30 instruction slots.',
    'Useful lane slots: 8 × 20 + 24 × 10 = 400.',
    'Available: 32 × 30 = 960.',
    eq('41.7 percent. Sort or group the work so each warp takes one path')])}
<p><b>Problem B.</b> 8 chunks pass through copy in (4 ms), kernel (6 ms) and copy out (2 ms), one engine each. Serial and overlapped time?</p>
{steps('Solution B', [
    'Serial: 8 × 12 = 96 ms.',
    'The kernel is the slowest stage: 4 ms to fill, 8 × 6 ms of kernels, 2 ms to drain.',
    '4 + 48 + 2 = 54 ms.',
    eq('Speedup 96 ÷ 54 ≈ 1.78')])}
<p><b>Problem C.</b> A program is 95 percent parallel. What speedup do Amdahl and Gustafson predict on 1024 cores, and why do they differ?</p>
{steps('Solution C', [
    'Amdahl (fixed problem): 1 ÷ (0.05 + 0.95 ÷ 1024) = 19.6.',
    'Gustafson (problem grows with the machine): 0.05 + 0.95 × 1024 = 972.9.',
    'Amdahl keeps the work fixed, so the serial 5 percent dominates.',
    eq('Gustafson grows the parallel part, which is how GPUs are really used')])}
{viz('diverge')}
{viz('streams')}
{viz('amdahl')}
''', kw=['divergence', 'lane efficiency', 'pipeline', 'Amdahl', 'Gustafson'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Hard problems are several easy ones joined together. Find the pieces first.</p>',
    '<p>Write down the limit formulas you need: ridge, occupancy, gcd for banks, scan work, tile AI, pipeline time, Amdahl.</p>',
    '<p>Always check with a second method: a small Python loop, a widget, or a limiting case such as n = 1.</p>',
    '<p>Research papers on GPU kernels are built from exactly these models, then confirmed with Nsight measurements.</p>')}
''', kw=['ladder', 'problem solving'])

K.quiz('e', 'Stride 2 reads in shared memory give a conflict of degree', ['1', '2', '16', '32'], 1, 'gcd(2, 32).', '2 way.')
K.quiz('e', 'Blelloch scan of n values does how many additions?', ['n log n', '2(n − 1)', 'n', 'n²'], 1, 'Up and down sweep.', 'Work efficient.')
K.quiz('e', 'Amdahl assumes', ['The problem grows', 'The problem size is fixed', 'No serial part', 'Infinite memory'], 1, 'Fixed size.', 'Gustafson lets it grow.')
K.quiz('m', 'Stride 6 in shared memory', ['Conflict free', '2 way', '6 way', '32 way'], 1, 'gcd(6, 32) = 2.', '2 way.')
K.quiz('m', '40 registers × 256 threads on an A100. Blocks allowed by registers', ['4', '6', '8', '10'], 1, '65,536 ÷ 10,240.', '6.')
K.quiz('m', 'Why pad a 32 × 32 tile to 33 columns?', ['Alignment', 'Column reads become stride 33, gcd 1, no conflict', 'More threads', 'Coalescing'], 1, 'Bank spread.', 'Conflict free columns.')
K.quiz('m', 'Pipeline with stages 4, 6, 2 ms and 8 chunks takes', ['96 ms', '54 ms', '48 ms', '60 ms'], 1, 'Fill + N × slowest + drain.', '54.')
K.quiz('h', 'H100 4096 layer becomes math limited from batch', ['223', '295', '345', '512'], 2, 'Ridge 295.2.', '345.')
K.quiz('h', 'Which scan is better on a GPU with far fewer lanes than n?', ['Hillis and Steele', 'Blelloch', 'Both equal', 'Neither'], 1, 'Total work matters.', 'Blelloch.')
K.quiz('h', 'Forcing registers from 40 to 32 per thread can', ['Never hurt', 'Cause spills to local memory', 'Reduce occupancy', 'Remove shared memory'], 1, 'Fewer registers than needed.', 'Measure both.')
K.quiz('x', '48 KB double buffered, BK = 32, FP32. Best square tile', ['64', '96', '128', '192'], 1, 'BM + BN ≤ 192.', '96 × 96.')
K.quiz('x', 'Warp with 8 lanes on 20 instructions and 24 on 10. Efficiency', ['41.7 %', '50 %', '62.5 %', '75 %'], 0, '400 ÷ 960.', '41.7 percent.')

K.calc('e', 'Conflict degree for stride 8?', '8', 'gcd(8, 32).',
       ['8 divides 32.', 'gcd = 8.', eq('8 way')], check=8)
K.calc('e', 'Blelloch additions for n = 1024?', '2046', '2(n − 1).',
       ['2 × 1023.', '= 2046.', eq('2046')], check=2046)
K.calc('e', 'Serial time: 8 chunks of 4 + 6 + 2 ms?', '96', '8 × 12.',
       ['Per chunk 12 ms.', '× 8.', eq('96 ms')], check=96)
K.calc('m', 'Hillis and Steele additions for n = 1024?', '9217', 'n log n − (n − 1).',
       ['10,240 − 1023.', '= 9217.', eq('9217')], check=9217)
K.calc('m', 'Occupancy in percent: 40 registers, 256 threads, 20 KB shared, A100?', '75', 'Registers bind.',
       ['6 blocks × 8 warps = 48.', '48 ÷ 64.', eq('75 percent')], check=75)
K.calc('m', 'Max registers per thread for 8 blocks of 256 on an A100?', '32', '65,536 ÷ 2048.',
       ['8 × 256 = 2048 threads.', '65,536 ÷ 2048.', eq('32 registers')], check=32)
K.calc('m', 'Overlapped time: 8 chunks of 4, 6, 2 ms?', '54', '4 + 48 + 2.',
       ['Kernel stage binds.', 'Fill 4, drain 2.', eq('54 ms')], check=54)
K.calc('h', 'H100 BF16 989 TFLOP/s, 3.35 TB/s. Smallest math limited batch for the 4096 layer?', '345', 'AI > 295.2.',
       ['3505.6 B > 1,209,139.', 'B > 344.9.', eq('345')], check=345)
K.calc('h', 'Amdahl speedup, 95 percent parallel, 1024 cores? (two decimals)', '19.64', '1 ÷ (0.05 + 0.95 ÷ 1024).',
       ['0.95 ÷ 1024 = 0.000928.', '1 ÷ 0.050928.', eq('≈ 19.64')], check=round(1 / (0.05 + 0.95 / 1024), 2), tol=0.005)
K.calc('x', 'Gustafson speedup for the same case? (one decimal)', '972.9', '0.05 + 0.95 × 1024.',
       ['0.95 × 1024 = 972.8.', '+ 0.05.', eq('≈ 972.9')], check=972.9, tol=0.05)
K.calc('x', 'AI of the best square tile in the 48 KB budget (FP32)?', '24', 'T ÷ 4 with T = 96.',
       ['BM = BN = 96.', '96 ÷ 4.', eq('24 FLOP/byte')], check=24)

K.assign('occ', 'h', 'An occupancy calculator',
         '<p>Write <code>occupancy(threads, regs, smem_kb)</code> for an A100: 65,536 registers, 2048 threads, 32 blocks and 164 KB of shared memory per SM, with 1 KB reserved per block when the block uses shared memory. Return the occupancy as a percentage rounded to one decimal (active warps ÷ 64).</p>',
         '''
def occupancy(threads, regs, smem_kb):
    # your code here
    pass
''', [("occupancy(256, 40, 20)", 75.0), ("occupancy(256, 32, 16)", 100.0), ("occupancy(1024, 64, 0)", 50.0), ("occupancy(128, 32, 48)", 18.8)],
         '''
def occupancy(threads, regs, smem_kb):
    warps = (threads + 31) // 32
    b_regs = 65536 // (regs * threads)
    b_thr = 2048 // threads
    b_smem = 32 if smem_kb == 0 else int(164 // (smem_kb + 1))
    blocks = min(b_regs, b_thr, 32, b_smem)
    return round(100 * blocks * warps / 64, 1)
''', 'Compute each limit, take the smallest.', '<p>Real calculators also round register use up per warp. With these inputs the answers do not change.</p>')
K.assign('scanwork', 'm', 'Work of two scans',
         '<p>Write <code>scan_work(n)</code> for n a power of two. Return [Hillis and Steele additions, Blelloch additions, Hillis and Steele steps, Blelloch steps].</p>',
         '''
def scan_work(n):
    # your code here
    pass
''', [("scan_work(1024)", [9217, 2046, 10, 20]), ("scan_work(8)", [17, 14, 3, 6]), ("scan_work(2)", [1, 2, 1, 2]), ("scan_work(16)", [49, 30, 4, 8])],
         '''
def scan_work(n):
    k = n.bit_length() - 1
    hs = sum(n - 2 ** d for d in range(k))
    return [hs, 2 * (n - 1), k, 2 * k]
''', 'Step d of Hillis and Steele updates n − 2^d values.', '<p>Hillis and Steele does more work but fewer steps.</p>')

K.must('Batch threshold', 'n × n layer: AI = nB ÷ (n + 2B). A100 4096: 223. H100 4096: 345. A100 1024: 330.')
K.must('Occupancy', 'Blocks = min(registers, threads, block limit, shared memory). Registers bind at 40 × 256 on an A100: 75 percent.')
K.must('Banks', 'Stride k gives a gcd(k, 32) way conflict. Pad rows to 33 for column reads.')
K.must('Scan work', 'Hillis and Steele n log n − (n − 1) in log n steps. Blelloch 2(n − 1) in 2 log n steps.')
K.must('Tile budget', 'Double buffered FP32 with BK = 32 in 48 KB: BM + BN ≤ 192, best 96 × 96, AI 24.')

T = K.topic(
    slug='challenge-problems', topic='challenge-problems', step=(10, 'Exam practice', 'gpu-exam', 'Quiz 1 solved, hard problems in the style of top university courses, and a final revision.', 'Pro'),
    title='Challenge problems', short='Challenge problems', badge='10.2', minutes=60,
    lead='Hard multi step problems in the style of graduate GPU and parallel computing courses, each with a full worked solution, a widget to check your picture, and code that recomputes every number.',
    desc='Batch thresholds on the H100 and A100, an occupancy puzzle with the register limit, bank conflicts by gcd and padding, work and steps of two scans, choosing a tile under a shared memory budget, divergence efficiency, pipeline overlap, and Amdahl against Gustafson.',
    summary='Hard multi step problems with full solutions.',
    keywords=['challenge', 'hard problems', 'occupancy', 'bank conflicts', 'scan', 'tile size'],
    recap='<p>Hard problems join easy ideas. Find the limit formula for each piece, combine them, and check with a second method.</p>')
