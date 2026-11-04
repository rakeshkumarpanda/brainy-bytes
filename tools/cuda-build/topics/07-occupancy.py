# Chapter 2.4: Occupancy. Source: lecture 2 (thread and block limits per SM), lecture 7 and 8 (register limited
# occupancy, rounding registers to 256 per warp, __launch_bounds__), lecture 9 to 12 (the occupancy calculator
# screenshot, shared memory limits), workbook 2.3, 7.5 and 9.7.
# Beyond the lecture: cudaOccupancyMaxActiveBlocksPerMultiprocessor and cudaOccupancyMaxPotentialBlockSize, and why
# full occupancy is not always the fastest choice.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

OCCAPI = r'''
#include <cstdio>
#define CHECK(x) do { cudaError_t e = (x); if (e != cudaSuccess) { \
    printf("CUDA error %s at line %d\n", cudaGetErrorString(e), __LINE__); return 1; } } while (0)

__global__ void scale(float *y, const float *x, float a, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = a * x[i];
}

int main() {
    cudaDeviceProp p;
    CHECK(cudaGetDeviceProperties(&p, 0));
    int blocks = 0;
    CHECK(cudaOccupancyMaxActiveBlocksPerMultiprocessor(&blocks, scale, 256, 0));
    int warps = blocks * 256 / 32;
    int maxWarps = p.maxThreadsPerMultiProcessor / 32;
    printf("%d blocks of 256 per SM, occupancy %.1f%%\n", blocks, 100.0 * warps / maxWarps);

    int minGrid = 0, best = 0;
    CHECK(cudaOccupancyMaxPotentialBlockSize(&minGrid, &best, scale, 0, 0));
    printf("suggested block size %d, at least %d blocks\n", best, minGrid);
    return 0;
}
'''

BOUNDS = r'''
// Ask the compiler to keep registers low enough for 4 blocks of 256 threads per SM
__global__ void __launch_bounds__(256, 4)
heavy(float *out, const float *in, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    float a = in[i], s = 0.0f;
    for (int k = 1; k <= 8; ++k) s += a / k;
    out[i] = s;
}
'''

K.code('occ', r'''
# Occupancy of one SM: four limits, the smallest wins
import math
def occupancy(b, regs, smem, max_warps=64, max_blocks=32, reg_file=65536, smem_sm=167936, reserve=1024):
    wpb = math.ceil(b / 32)                       # warps per block
    by_warps = max_warps // wpb
    per_warp = math.ceil(regs * 32 / 256) * 256    # registers are handed out in chunks of 256 per warp
    by_regs = (reg_file // per_warp) // wpb
    by_smem = smem_sm // (smem + reserve) if smem else 10**9
    blocks = min(by_warps, max_blocks, by_regs, by_smem)
    return blocks, 100 * blocks * wpb / max_warps
print("A100 256 threads 32 regs :", occupancy(256, 32, 0))
print("A100 256 threads 40 regs :", occupancy(256, 40, 0))
print("A100 256 threads 37 regs :", occupancy(256, 37, 0))
print("A100 1024 threads 48 regs:", occupancy(1024, 48, 0))
''')

K.code('limits', r'''
# Only threads and blocks (lecture SM: 1024 threads, 32 warps, 8 blocks)
for b in [32, 64, 128, 256, 512, 1024]:
    wpb = b // 32
    blocks = min(32 // wpb, 8)
    print(f"{b:5d} threads: {blocks} blocks, {blocks * wpb:2d} warps, {100 * blocks * wpb / 32:5.1f}%")
''')

K.lesson('what', 'What occupancy means', f'''
<p>Chapter 2.3 showed that an SM hides waiting by switching between warps. <b>Occupancy</b> says how many warps an SM really holds compared with the most it could hold.</p>
{fxs(
    fx('Occupancy', 'occupancy = active warps per SM ÷ maximum warps per SM', 'A100: maximum 64 warps (2048 threads). 48 active warps is 75 percent.', key=True),
    fx('Blocks that fit', 'blocks = min(warp limit, block limit, register limit, shared memory limit)', 'Every resource must fit at the same time, so the tightest one decides.', key=True))}
{table(['GPU (compute capability)', 'Max threads', 'Max warps', 'Max blocks', 'Registers', 'Shared memory per SM'], [
    ['Fermi (2.0)', '1536', '48', '8', '32,768', '48 KB'],
    ['T4 (7.5)', '1024', '32', '16', '65,536', '64 KB'],
    ['A100 (8.0)', '2048', '64', '32', '65,536', 'up to 164 KB'],
    ['RTX 30xx (8.6)', '1536', '48', '16', '65,536', 'up to 100 KB'],
    ['H100 (9.0)', '2048', '64', '32', '65,536', 'up to 228 KB']])}
{scene('a cinema with four rules', '<p>A cinema lets in a group only if there are enough seats, the group count is under the limit, the snack counter has enough cups and the car park has space. The hall may have empty seats but still turn groups away because the car park is full. The SM works the same way.</p>')}
''', kw=['occupancy', 'active warps', 'max warps', 'compute capability', 'SM limits'])

K.lesson('threads', 'Limit 1 and 2: threads and blocks', f'''
<p>An SM holds at most a fixed number of warps and a fixed number of blocks. Small blocks run into the block limit long before the warps are used up.</p>
{steps('Workbook worked example: 1024 threads, 32 warps, 8 blocks per SM, 16 × 16 blocks', [
    'A block has 256 threads = 8 warps.',
    'Warp limit: 32 ÷ 8 = 4 blocks. Block limit: 8 blocks.',
    'The smaller is 4 blocks, so 4 × 8 = 32 warps.',
    eq('occupancy = 32 ÷ 32 = 100 percent')])}
{steps('Small blocks on the same SM (P2.3.3)', [
    'A 64 thread block is 2 warps.',
    'Warp limit 32 ÷ 2 = 16 blocks, block limit 8.',
    '8 blocks × 2 warps = 16 warps.',
    eq('16 ÷ 32 = 50 percent: the block limit bites')])}
{code('limits')}
{fxs(fx('Smallest block for full occupancy', '<i>B</i><sub>min</sub> = max threads per SM ÷ max blocks per SM', 'A100: 2048 ÷ 32 = 64 threads. Anything smaller cannot reach 100 percent.'))}
''', kw=['block limit', 'warp limit', 'small blocks', 'smallest block size'])

K.lesson('regs', 'Limit 3: registers, with rounding', f'''
<p>Registers are not handed out one by one. On recent GPUs each warp receives registers in chunks of 256, so the per warp count is rounded up.</p>
{fxs(
    fx('Registers per warp', 'per warp = ⌈(r × 32) ÷ 256⌉ × 256', 'r = registers per thread. 37 registers give 1184, rounded up to 1280, the same as 40.', key=True),
    fx('Register limit in blocks', 'blocks = ⌊⌊65,536 ÷ per warp⌋ ÷ warps per block⌋', 'First whole warps, then whole blocks.', key=True))}
{viz('occupancy')}
{steps('Workbook worked example 7.5: A100, 256 threads, 40 registers', [
    '40 × 32 = 1280 registers per warp (already a multiple of 256).',
    '65,536 ÷ 1280 = 51.2, so 51 warps.',
    '51 ÷ 8 warps per block = 6.4, so 6 blocks = 48 warps.',
    eq('48 ÷ 64 = 75 percent')])}
{cu('bounds.cu', BOUNDS, {2: '__launch_bounds__(max threads per block, min blocks per SM) tells the compiler how you will launch the kernel.', 3: 'With 256 threads and 4 blocks the SM needs 1024 threads, so the compiler caps each thread at 65,536 ÷ 1024 = 64 registers.', 7: 'A small loop. If a kernel needed more registers than the cap, the compiler would spill to local memory.'})}
{note('The flag -maxrregcount=N caps registers for every kernel in a file. __launch_bounds__ is better because it is per kernel and says why.', 'tip')}
''', kw=['registers per warp', 'rounding to 256', '__launch_bounds__', 'maxrregcount', 'register limited occupancy'])

K.lesson('smem', 'Limit 4: shared memory', f'''
<p>Each block that uses shared memory takes its bytes from the SM\'s pool. On compute capability 8.x the system also reserves 1 KB per block.</p>
{fxs(fx('Shared memory limit', 'blocks = ⌊shared memory per SM ÷ (bytes per block + reserved)⌋', 'CC 8.6: 102,400 bytes per SM, 1024 reserved per block.', key=True))}
{steps('Workbook 9.7: CC 8.6, 256 threads, 32 registers, 32 KB of shared memory', [
    'Warp limit 48 ÷ 8 = 6. Block limit 16. Registers 32 × 32 = 1024 per warp, 64 warps, 8 blocks.',
    'Shared memory: 102,400 ÷ (32,768 + 1024) = 3.03, so 3 blocks.',
    'The smallest limit is 3 blocks = 24 warps.',
    eq('24 ÷ 48 = 50 percent')])}
{cu('occupancy_api.cu', OCCAPI, {14: 'cudaOccupancyMaxActiveBlocksPerMultiprocessor does the same four limit sum for a real kernel on the real GPU.', 13: 'The result lands in blocks. In the call below, the last argument is the dynamic shared memory per block in bytes.', 15: 'Blocks × threads ÷ 32 gives active warps.', 20: 'cudaOccupancyMaxPotentialBlockSize suggests the block size that gives the highest occupancy, and the smallest grid that fills the GPU.'}, out='(on an A100) 8 blocks of 256 per SM, occupancy 100.0%\nsuggested block size 1024, at least 216 blocks')}
{note('The printed numbers above are what this code gives on an A100 by the four limit rule. They were worked out, not measured on a real GPU.', 'tip')}
''', kw=['shared memory limit', 'reserved shared memory', 'occupancy API', 'cudaOccupancyMaxActiveBlocksPerMultiprocessor', 'cudaOccupancyMaxPotentialBlockSize'])

K.lesson('levels', 'Is higher occupancy always faster?', f'''
{code('occ')}
{ladder(
    '<p>The SM is a hall with limited seats, groups, cups and parking. Occupancy is the share of seats in use. More people waiting means less idle time, up to a point.</p>',
    '<p>Blocks = min of four limits. Registers round up to 256 per warp. Shared memory adds 1 KB reserved per block on 8.x. Occupancy = blocks × warps per block ÷ max warps.</p>',
    '<p>Once enough warps hide the latency (Little\'s law), more occupancy gives nothing. A kernel at 50 percent with 4 independent loads per thread can beat one at 100 percent with 1. Measure with Nsight Compute "achieved occupancy", which can be lower than the theory because of tail effects and uneven blocks.</p>',
    '<p>High performance GEMM and attention kernels deliberately run at 12 to 25 percent occupancy: each thread holds a large tile of results in registers, and asynchronous copies (cp.async, TMA) keep memory busy. Occupancy is a means, not the goal.</p>')}
''', kw=['achieved occupancy', 'theoretical occupancy', 'ILP', 'low occupancy kernels'])

K.quiz('e', 'Occupancy is', ['Threads per block', 'Active warps ÷ maximum warps per SM', 'GPU temperature', 'Blocks per grid'], 1,
       'A ratio of warps.', 'It measures how full the SM is with warps.')
K.quiz('e', 'Which limit decides the number of blocks on an SM?', ['The largest', 'The smallest', 'The average', 'Only threads'], 1,
       'All must fit.', 'Every resource must fit at once.')
K.quiz('e', 'A 256 thread block has how many warps?', ['4', '8', '16', '32'], 1, '256 ÷ 32.', '8.')
K.quiz('m', 'SM: 32 warps, 8 blocks. 64 thread blocks give', ['100 percent', '50 percent', '25 percent', '75 percent'], 1,
       '8 blocks × 2 warps.', '16 of 32 warps.')
K.quiz('m', 'On recent GPUs registers per warp are rounded up to a multiple of', ['32', '64', '256', '1024'], 2,
       'Allocation unit.', '37 × 32 = 1184 rounds to 1280.')
K.quiz('m', '__launch_bounds__(256, 4) on an A100 caps registers at', ['32', '64', '128', '255'], 1,
       '65,536 ÷ 1024.', '4 blocks × 256 threads = 1024 threads.')
K.quiz('m', 'Shared memory reserved per block on CC 8.x', ['0', '256 bytes', '1 KB', '4 KB'], 2,
       'Hidden cost.', '1024 bytes per block are reserved by the system.')
K.quiz('h', 'A100, 1024 thread blocks, 48 registers. Occupancy?', ['100 percent', '75 percent', '50 percent', '25 percent'], 2,
       '48 × 32 = 1536 per warp.', '42 warps fit, a block needs 32, so 1 block = 32 of 64 warps.')
K.quiz('h', 'Why can 37 registers give the same occupancy as 40?', ['They cannot', 'Both round up to 1280 registers per warp', 'The compiler adds 3', 'Spilling'], 1,
       'Rounding.', '37 × 32 = 1184 → 1280 = 40 × 32.')
K.quiz('h', 'A kernel at 50 percent occupancy runs faster than at 100 percent. A likely reason', ['Impossible', 'More registers per thread give more independent work and no spills', 'The GPU is idle', 'Bank conflicts disappear'], 1,
       'ILP.', 'Enough warps already hide latency, and extra registers remove spills or add ILP.')
K.quiz('x', 'CC 8.6, 1024 thread blocks, 32 registers. Occupancy?', ['100 percent', '66.7 percent', '50 percent', '33.3 percent'], 1,
       'Warp limit.', '48 ÷ 32 = 1 block, 32 of 48 warps.')
K.quiz('x', 'Most shared memory per block that still allows 6 blocks on CC 8.6', ['17,066 bytes', 'About 16,042 bytes', '16,384 bytes', '8192 bytes'], 1,
       'Remember the reserve.', '102,400 ÷ 6 = 17,066, minus 1024 reserved = 16,042.')

K.calc('e', 'SM: 1024 threads, 32 warps, 8 blocks. 128 thread blocks. Occupancy in percent?', '100', 'Warp limit 32 ÷ 4.',
       ['128 threads = 4 warps.', 'Warp limit 8 blocks, block limit 8.', eq('8 × 4 = 32 warps = 100 percent')], check=100 * min(32 // 4, 8) * 4 / 32)
K.calc('e', 'Smallest block size that can reach 100 percent on an A100 (2048 threads, 32 blocks)?', '64', '2048 ÷ 32.',
       ['Each of the 32 blocks must carry 2048 ÷ 32 threads.', '2048 ÷ 32 = 64.', eq('64 threads per block')], check=2048 // 32)
K.calc('e', 'Registers used by a 256 thread block at 32 registers per thread?', '8192', 'Multiply.',
       ['256 × 32.', '= 8192.', eq('One eighth of 65,536')], check=256 * 32)
K.calc('m', 'RTX 4060 SM: 48 warps, 24 blocks. 32 × 32 blocks. Occupancy in percent? (one decimal)', '66.7', '1024 threads = 32 warps.',
       ['Warp limit ⌊48 ÷ 32⌋ = 1 block.', '1 block = 32 warps.', eq('32 ÷ 48 = 66.7 percent')], check=100 * 32 / 48, tol=0.05)
K.calc('m', 'SM: 48 warps, 16 blocks. 64 thread blocks. Occupancy in percent? (one decimal)', '66.7', 'Block limit.',
       ['64 threads = 2 warps.', 'Warp limit 24, block limit 16, so 16 blocks.', eq('32 ÷ 48 = 66.7 percent')], check=100 * 16 * 2 / 48, tol=0.05)
K.calc('m', 'A100, 256 threads, 40 registers. Occupancy in percent?', '75', 'Registers per warp 1280.',
       ['65,536 ÷ 1280 = 51 warps.', '51 ÷ 8 = 6 blocks.', eq('48 ÷ 64 = 75 percent')], check=100 * (65536 // 1280 // 8) * 8 / 64)
K.calc('m', 'CC 8.6, 256 threads, 48 registers. Occupancy in percent? (one decimal)', '83.3', '48 × 32 = 1536.',
       ['65,536 ÷ 1536 = 42 warps.', '42 ÷ 8 = 5 blocks = 40 warps.', eq('40 ÷ 48 = 83.3 percent')], check=100 * (65536 // 1536 // 8) * 8 / 48, tol=0.05)
K.calc('h', 'CC 8.6, 256 threads, 32 registers, 16 KB shared per block. Occupancy in percent? (one decimal)', '83.3', 'Shared memory limit.',
       ['102,400 ÷ (16,384 + 1024) = 5.88.', '5 blocks = 40 warps.', eq('40 ÷ 48 = 83.3 percent')], check=100 * (102400 // (16384 + 1024)) * 8 / 48, tol=0.05)
K.calc('h', 'A100, 256 threads, 37 registers. Occupancy in percent?', '75', 'Round 1184 up.',
       ['37 × 32 = 1184 → 1280.', '65,536 ÷ 1280 = 51 warps → 6 blocks.', eq('48 ÷ 64 = 75 percent')], check=100 * (65536 // 1280 // 8) * 8 / 64)
K.calc('x', 'Most registers per thread for 100 percent on an A100 with 128 thread blocks?', '32', '64 warps must fit.',
       ['65,536 ÷ 64 warps = 1024 registers per warp.', '1024 ÷ 32 lanes = 32.', eq('32 registers per thread')], check=65536 // 64 // 32)
K.calc('x', 'Most shared memory per block (bytes, whole) for 6 blocks on CC 8.6?', '16042', 'Subtract the reserve.',
       ['102,400 ÷ 6 = 17,066.67, so at most 17,066 per block including the reserve.', '17,066 − 1024.', eq('16,042 bytes')], check=102400 // 6 - 1024)

K.assign('occ4', 'm', 'Four limit occupancy calculator',
         '<p>Write <code>occ(b, r, s)</code> for an A100 (64 warps, 32 blocks, 65,536 registers, 167,936 bytes shared, 1024 reserved per block when s &gt; 0). Round registers per warp up to 256. Return <code>[blocks, percent]</code> with percent rounded to one decimal.</p>',
         '''
def occ(b, r, s):
    # your code here
    pass
''', [("occ(256, 32, 0)", [8, 100.0]), ("occ(256, 40, 0)", [6, 75.0]), ("occ(1024, 48, 0)", [1, 50.0]), ("occ(256, 32, 48000)", [3, 37.5])],
         '''
def occ(b, r, s):
    wpb = (b + 31) // 32
    per_warp = (r * 32 + 255) // 256 * 256
    lim = [64 // wpb, 32, 65536 // per_warp // wpb]
    if s > 0:
        lim.append(167936 // (s + 1024))
    blocks = min(lim)
    return [blocks, round(100 * blocks * wpb / 64, 1)]
''', 'Take the minimum of all limits.', '<p>With 48,000 bytes of shared memory only 3 blocks fit, even though registers allow 8.</p>')
K.assign('maxregs', 'h', 'Register budget for a target',
         '<p>Write <code>max_regs(b, blocks)</code>: the most registers per thread (a whole number, at most 255) so that <code>blocks</code> blocks of <code>b</code> threads fit in 65,536 registers, using the 256 per warp rounding.</p>',
         '''
def max_regs(b, blocks):
    # your code here
    pass
''', [("max_regs(256, 4)", 64), ("max_regs(128, 16)", 32), ("max_regs(256, 6)", 40), ("max_regs(32, 1)", 255)],
         '''
def max_regs(b, blocks):
    warps = blocks * ((b + 31) // 32)
    best = 0
    for r in range(1, 256):
        per_warp = (r * 32 + 255) // 256 * 256
        if per_warp * warps <= 65536:
            best = r
    return best
''', 'Try every register count and keep the largest that fits.', '<p>For 6 blocks of 256 threads, 40 registers fit and 41 do not, which is why 40 registers give 75 percent.</p>')

K.must('Occupancy', 'Active warps ÷ max warps per SM. Blocks = min(warp limit, block limit, register limit, shared memory limit).')
K.must('Block limit', 'Small blocks hit the block cap. Smallest block for 100 percent = max threads ÷ max blocks (A100: 64).')
K.must('Registers', 'Per warp = ⌈32r ÷ 256⌉ × 256. Blocks = ⌊⌊65,536 ÷ per warp⌋ ÷ warps per block⌋.')
K.must('Shared memory', 'Blocks = ⌊pool ÷ (bytes + 1 KB reserved)⌋ on CC 8.x.')
K.must('Not the goal', 'Enough warps to hide latency is enough. Measure achieved occupancy in Nsight Compute.')

T = K.topic(
    slug='occupancy', topic='occupancy', step=(2, 'The CUDA programming model', 'gpu-model', 'Write and launch kernels, index threads in 1, 2 and 3 dimensions, and see how warps and SMs run them and how many fit.', 'College'),
    title='Occupancy: how many warps fit on an SM', short='Occupancy', badge='2.4', minutes=45,
    lead='Work out how many blocks fit on one SM from four limits, threads, blocks, registers and shared memory, and learn when chasing 100 percent is not worth it.',
    desc='Occupancy, the four limits, small block traps, register allocation in chunks of 256, __launch_bounds__, shared memory reserve, the occupancy API and calculator, and why low occupancy kernels can be fast.',
    summary='Occupancy from four limits, register rounding, shared memory reserve, launch bounds and the occupancy API.',
    keywords=['occupancy', 'registers', 'shared memory', 'launch bounds', 'occupancy calculator'],
    recap='<p>The smallest of four limits sets the blocks per SM. Registers round up to 256 per warp and shared memory carries a 1 KB reserve. High occupancy helps only until latency is hidden.</p>')
