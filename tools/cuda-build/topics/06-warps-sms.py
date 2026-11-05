# Chapter 2.3: SMs, warps and SIMT. Source: lecture 1 (Fermi SM), lecture 2 (execution model, warps and wasted lanes,
# required parallelism = latency × throughput for Fermi and Kepler, registers per thread), lecture 3 (software to
# hardware mapping and its correction), workbook 2.2, 2.4 and 2.5, Quiz 1 question 10.
# Beyond the lecture: independent thread scheduling since Volta and the warp size constant warpSize.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

WARPID = r'''
#include <cstdio>

__global__ void whoAmI() {
    int t = threadIdx.x + threadIdx.y * blockDim.x;
    int warp = t / warpSize;
    int lane = t % warpSize;
    if (lane == 0)
        printf("block %d: warp %d starts at thread (%d, %d)\n",
               blockIdx.x, warp, threadIdx.x, threadIdx.y);
}

int main() {
    dim3 block(16, 16);
    whoAmI<<<1, block>>>();
    cudaDeviceSynchronize();
    return 0;
}
'''

K.code('warps', r'''
# Warps, lanes and wasted lanes for a few block sizes
import math
for B in [100, 128, 48, 256, 1000]:
    warps = math.ceil(B / 32)
    wasted = 32 * warps - B
    print(f"B={B:5d}: {warps:3d} warps, {wasted:2d} empty lanes, efficiency {100 * B / (32 * warps):5.1f}%")
t = 70
print("thread", t, "is warp", t // 32, "lane", t % 32)
''')

K.code('little', r'''
# Little's law: work in flight = latency x throughput
chips = {"Fermi": (20, 32), "Kepler": (20, 192), "new GPU": (15, 384)}
for name, (latency, ops_per_tick) in chips.items():
    ops = latency * ops_per_tick
    print(f"{name:8s}: {ops:5d} operations in flight = {ops // 32:4d} warps")
# memory version: bytes in flight = bandwidth x latency
bw, lat_ns = 900e9, 400 / 1.4          # 900 GB/s, 400 ticks at 1.4 GHz
print("bytes in flight:", round(bw * lat_ns * 1e-9))
''')

K.lesson('sm', 'Streaming multiprocessors: what really runs your threads', f'''
<p>A GPU is a set of identical <b>streaming multiprocessors</b> (SMs). Each SM has its own cores, registers, schedulers and on chip memory. A kernel\'s blocks are handed out to SMs, and an SM may hold several blocks at once.</p>
{table(['Software (what you write)', 'Hardware (what runs it)', 'Rule'], [
    ['Thread', 'A CUDA core (one lane)', 'Has its own registers and program counter'],
    ['Warp of 32 threads', 'A warp scheduler', 'Issues one instruction for all 32 lanes'],
    ['Block (up to 1024 threads)', 'One SM', 'Stays on that SM until it finishes, shares its shared memory'],
    ['Grid (all blocks of a launch)', 'The whole GPU', 'Blocks spread over all SMs in any order']])}
{note('In class it was said that grids sit inside cores. It is the other way round: a thread runs on a core, a block on one SM, and a grid across all SMs.', 'warn')}
{table(['Fermi SM part (lecture 1)', 'Count', 'Job'], [
    ['CUDA cores', '32', 'Integer and floating point units, one lane each'],
    ['Warp schedulers and dispatch units', '2', 'Two warps can issue at the same time'],
    ['Register file', '32,768 × 32 bit', 'Private variables of every resident thread'],
    ['Load/store units', '16', 'Addresses for 16 threads per clock'],
    ['Special function units', '4', 'sin, cos, reciprocal, square root'],
    ['Shared memory / L1', '64 KB', 'Split 48/16 or 16/48 between shared memory and L1']])}
<p>Fermi had 16 SMs × 32 cores = 512 cores. An A100 has 108 SMs with 64 FP32 cores each, an H100 has 132.</p>
''', kw=['SM', 'streaming multiprocessor', 'Fermi', 'warp scheduler', 'register file', 'SFU', 'load store unit'])

K.lesson('warps', 'Warps, lanes and SIMT', f'''
<p>The SM does not schedule single threads. It schedules <b>warps</b>: 32 threads with consecutive linear thread numbers. All lanes of a warp execute the same instruction at the same time on their own data. NVIDIA calls this SIMT, single instruction, multiple threads.</p>
{fxs(
    fx('Warps per block', 'warps = ⌈<i>B</i> ÷ 32⌉', 'A part full warp still takes 32 lanes.', key=True),
    fx('Warp and lane of thread t', 'warp = ⌊<i>t</i> ÷ 32⌋, lane = <i>t</i> − 32 × warp', 'For 2-D blocks first compute t = x + y × B<sub>x</sub>.', key=True),
    fx('Wasted lanes', 'wasted = 32 × warps − <i>B</i><br>efficiency = <i>B</i> ÷ (32 × warps)', 'Use block sizes that are multiples of 32.'))}
{viz('warps')}
{scene('a school trip in 32 seat buses', '<p>The school hires buses with exactly 32 seats. 100 children need 4 buses, and the last bus leaves with only 4 children and 28 empty seats. The fuel cost is the same for a full bus. Choosing 96 or 128 children per trip wastes nothing.</p>')}
{cu('who_am_i.cu', WARPID, {4: 'Linear thread number inside the block, x fastest. This is the order the hardware uses to cut warps.', 5: 'warpSize is a built in constant, 32 on every NVIDIA GPU so far.', 7: 'Only lane 0 of each warp prints, so we see one line per warp.', 13: 'A 16 × 16 block has 256 threads, so 8 warps of two rows each.'}, out='block 0: warp 0 starts at thread (0, 0)\nblock 0: warp 1 starts at thread (0, 2)\n... (8 lines, warp w starts at row 2w)')}
{code('warps')}
{deep('independent thread scheduling (Volta and later)', '<p>Since Volta each thread has its own program counter, so threads of a diverged warp can interleave and even wait for each other. The warp still issues one instruction at a time for its active lanes, so divergence still costs time (chapter 6.1), and code that relies on all 32 lanes being in step must say so with __syncwarp().</p>')}
''', kw=['warp', 'lane', 'SIMT', 'warpSize', 'wasted lanes', 'efficiency', '2-D warps', 'independent thread scheduling'])

K.lesson('little', "Hiding latency: Little's law", f'''
<p>A GPU core waits about 20 ticks for an arithmetic result and several hundred ticks for global memory. It does not stall. Each tick the warp scheduler picks another warp that is ready and issues its instruction. The cost of switching is zero, because every warp keeps its registers on the SM all the time.</p>
{fxs(
    fx("Little's law", 'jobs in flight = latency (ticks) × throughput (jobs per tick)', 'To keep a pipe full you need as many jobs inside it as its length times its width.', key=True),
    fx('In warps', 'warps in flight = (latency × operations per tick) ÷ 32', 'One warp instruction is 32 operations.'),
    fx('Memory version', 'bytes in flight = bandwidth × latency', 'To use all the bandwidth, this many bytes must be on the way at every moment.'))}
{viz('littles')}
{steps('Workbook worked example: Fermi against Kepler', [
    'Fermi: latency 20 ticks, 32 operations per tick. In flight 20 × 32 = 640 operations = 20 warps.',
    'Kepler: latency 20 ticks, 192 operations per tick. In flight 20 × 192 = 3840 operations = 120 warps.',
    eq('Kepler needs 6 times more parallel work to stay busy')])}
{code('little')}
{scene('a pizza oven', '<p>A pizza bakes for 8 minutes and the chef can slide in one pizza per minute. To keep the oven always working, there must be 8 pizzas inside at any moment. With only 4 orders the chef stands idle half the time. Warps are the pizzas.</p>')}
{note('Latency hiding needs either many warps (thread level parallelism) or several independent instructions inside each warp (instruction level parallelism). Two independent loads per warp halve the warps needed.', 'tip')}
''', kw=["Little's law", 'latency hiding', 'warps in flight', 'Fermi', 'Kepler', 'bytes in flight', 'ILP'])

K.lesson('registers', 'Registers: the hidden limit', f'''
{fxs(
    fx('Registers per thread', 'registers per thread = registers on the SM ÷ threads on the SM', 'Lecture example: 32K registers for 1024 threads gives 32 each.'),
    fx('Binary K', '32K = 32 × 1024 = 32,768<br>64K = 65,536', 'For registers K means 1024.'),
    fx('Bits to name a register', 'smallest <i>b</i> with 2<sup><i>b</i></sup> ≥ number of registers', 'An instruction names its operands, so 32 registers need 5 bits, 255 need 8.'))}
<p>Every resident thread keeps all its variables in the SM\'s register file, which is fixed when the chip is made (65,536 on recent GPUs). A kernel that needs more registers per thread leaves room for fewer threads, so there are fewer warps to hide latency. If a kernel needs more registers than allowed, the compiler <b>spills</b> them to local memory, which lives in slow DRAM.</p>
{steps('How many threads fit by registers? (workbook P2.5.4)', [
    'The kernel needs 40 registers per thread and the SM has 65,536.',
    '65,536 ÷ 40 = 1638.4 threads.',
    'Threads come in whole warps: 1638 ÷ 32 = 51.2, so 51 warps.',
    eq('51 warps = 1632 threads (the exact allocation rules are in chapter 2.4)')])}
''', kw=['registers per thread', 'register file', 'spilling', 'local memory', 'bits per register'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>The GPU moves threads around in groups of 32, like buses. While one bus waits at a red light, the driver of another bus goes. With enough buses the road is always busy.</p>',
    '<p>warps = ⌈B/32⌉, warp = ⌊t/32⌋, lane = t mod 32. Little: in flight = latency × throughput, divide by 32 for warps. Registers per thread = register file ÷ threads.</p>',
    '<p>Each SM has 4 sub partitions on recent GPUs, each with its own scheduler issuing one warp instruction per tick. Occupancy (chapter 2.4) measures how many warps are resident, and the profiler\'s "stall reasons" say why ready warps are missing.</p>',
    '<p>Volkov showed that high ILP can beat high occupancy: fewer warps with more independent work per thread reach peak bandwidth. Modern GEMM kernels run at low occupancy with large register tiles and asynchronous copies.</p>')}
''', kw=['ladder', 'sub partitions', 'Volkov', 'ILP vs occupancy'])

K.quiz('e', 'A warp is', ['One thread', '32 threads scheduled together', 'One block', 'An SM'], 1,
       'Lockstep group.', 'The scheduler issues one instruction for 32 lanes at a time.')
K.quiz('e', 'A 256 thread block has how many warps?', ['4', '8', '16', '256'], 1,
       '256 ÷ 32.', '8 warps.')
K.quiz('e', 'A block runs on', ['Many SMs', 'One SM for its whole life', 'The CPU', 'One core'], 1,
       'Blocks never move.', 'All threads of a block share one SM and its shared memory.')
K.quiz('m', 'Thread 95 is in', ['Warp 2, lane 31', 'Warp 3, lane 0', 'Warp 2, lane 30', 'Warp 1, lane 31'], 0,
       '95 ÷ 32.', '2 × 32 = 64, 95 − 64 = 31.')
K.quiz('m', 'A block of 48 threads uses lanes with efficiency', ['100 percent', '75 percent', '50 percent', '48 percent'], 1,
       '2 warps.', '48 ÷ 64 = 75 percent.')
K.quiz('m', 'Why can a GPU switch warps every tick at no cost?', ['It saves registers to memory quickly', 'Every resident warp keeps its registers on the SM all the time', 'Warps share registers', 'It does not switch'], 1,
       'No context save.', 'The large register file holds every resident thread\'s state.')
K.quiz('m', "Little's law: latency 22 ticks, 128 operations per tick needs", ['2816 operations, 88 warps', '150 operations', '22 warps', '128 warps'], 0,
       '22 × 128.', '2816 ÷ 32 = 88 warps.')
K.quiz('h', 'In a 16 × 16 block, thread (x 5, y 3) is', ['Warp 0, lane 53', 'Warp 1, lane 21', 'Warp 3, lane 5', 'Warp 1, lane 5'], 1,
       't = 5 + 3 × 16.', 't = 53, warp 1, lane 21.')
K.quiz('h', 'When a kernel needs more registers than allowed, the compiler', ['Fails', 'Spills variables to local memory in DRAM', 'Uses shared memory', 'Reduces threads per block'], 1,
       'Spilling.', 'Local memory is private but slow, so spills cost speed.')
K.quiz('h', 'An SM holds 48 warps. Latency 20, 128 operations per tick needs 80 warps. A fix is', ['Use smaller blocks', 'Give each warp 2 independent instructions, so 40 warps suffice', 'Lower the clock', 'Add atomics'], 1,
       'ILP.', 'Independent instructions in flight per warp divide the warps needed.')
K.quiz('x', 'Quiz 1 question 10: N = 2²⁰, 256 threads per block. Warps launched?', ['4096', '8192', '32,768', '1,048,576'], 2,
       'Blocks × 8.', '4096 blocks × 8 warps = 32,768.')
K.quiz('x', 'Bits needed to name one of 255 registers in an instruction', ['7', '8', '9', '255'], 1,
       '2⁸ = 256.', '8 bits are the smallest with 2ᵇ ≥ 255.')

K.calc('e', 'A block has 100 threads. Empty lanes?', '28', 'Warps first.',
       ['Warps = ⌈100 ÷ 32⌉ = 4.', 'Lanes 4 × 32 = 128.', eq('128 − 100 = 28 empty')], check=28)
K.calc('e', 'Which lane is thread 70?', '6', '70 − 32 × ⌊70 ÷ 32⌋.',
       ['Warp ⌊70 ÷ 32⌋ = 2.', '2 × 32 = 64.', eq('Lane 70 − 64 = 6')], check=70 % 32)
K.calc('e', 'Fermi: latency 20 ticks, 32 operations per tick. Warps in flight?', '20', 'Little then ÷ 32.',
       ['Operations = 20 × 32 = 640.', 'Warps = 640 ÷ 32.', eq('20 warps')], check=20 * 32 // 32)
K.calc('m', 'Kepler: 20 ticks, 192 operations per tick. Warps in flight?', '120', 'Little.',
       ['20 × 192 = 3840 operations.', '3840 ÷ 32.', eq('120 warps')], check=20 * 192 // 32)
K.calc('m', '100,000 elements in 100 thread blocks. Overall lane efficiency in percent? (one decimal)', '78.1', 'Each block uses 4 warps.',
       ['1000 blocks × 4 warps × 32 lanes = 128,000 lanes.', 'Useful 100,000.', eq('100,000 ÷ 128,000 = 78.1 percent')], check=100 * 100000 / 128000, tol=0.05)
K.calc('m', '96K registers and 1536 threads. Registers per thread?', '64', '98,304 ÷ 1536.',
       ['96K = 96 × 1024 = 98,304.', '98,304 ÷ 1536.', eq('64')], check=96 * 1024 // 1536)
K.calc('m', 'A 256 thread block at 32 registers per thread. Registers per block?', '8192', 'Multiply.',
       ['256 × 32.', 'One eighth of 65,536.', eq('8192')], check=256 * 32)
K.calc('h', 'Memory latency 400 ticks at 1.4 GHz, bandwidth 900 GB/s. Bytes in flight? (nearest whole)', '257143', 'Convert latency to seconds.',
       ['400 ÷ 1.4 GHz ≈ 285.71 ns.', '900 × 10⁹ × 285.71 × 10⁻⁹.', eq('≈ 257,143 bytes (about 64,286 floats)')], check=round(900e9 * 400 / 1.4e9), tol=1)
K.calc('h', 'A kernel needs 40 registers per thread, SM has 65,536. Whole warps that fit?', '51', '÷ 40, then ÷ 32 rounded down.',
       ['65,536 ÷ 40 = 1638.4 threads.', '1638 ÷ 32 = 51.2.', eq('51 warps = 1632 threads')], check=int(65536 / 40) // 32)
K.calc('x', 'New GPU: 384 operations per tick, 15 tick latency. Warps in flight?', '180', 'Little.',
       ['15 × 384 = 5760 operations.', '÷ 32.', eq('180 warps, 50 percent more than Kepler')], check=15 * 384 // 32)
K.calc('x', '64K registers, up to 2048 threads. Largest registers per thread that still allows 2048 threads?', '32', '65,536 ÷ 2048.',
       ['Every thread must fit.', '65,536 ÷ 2048.', eq('32 registers')], check=65536 // 2048)

K.assign('warplane', 'e', 'Warp and lane of a 2-D thread',
         '<p>Write <code>warp_lane(x, y, bx)</code> for a 2-D block of width <code>bx</code>. Return <code>[warp, lane]</code>.</p>',
         '''
def warp_lane(x, y, bx):
    # your code here
    pass
''', [("warp_lane(5, 3, 16)", [1, 21]), ("warp_lane(70, 0, 100)", [2, 6]), ("warp_lane(0, 6, 16)", [3, 0])],
         '''
def warp_lane(x, y, bx):
    t = x + y * bx
    return [t // 32, t % 32]
''', 'Linear number first.', '<p>Warp 3 of a 16 × 16 block starts at row 6.</p>')
K.assign('inflight', 'm', "Little's law calculator",
         '<p>Write <code>warps_needed(latency, ops_per_tick, ilp=1)</code>: operations in flight ÷ 32, divided by the independent instructions per warp, rounded up.</p>',
         '''
def warps_needed(latency, ops_per_tick, ilp=1):
    # your code here
    pass
''', [("warps_needed(20, 32)", 20), ("warps_needed(20, 192)", 120), ("warps_needed(20, 128, 2)", 40), ("warps_needed(4, 128)", 16)],
         '''
def warps_needed(latency, ops_per_tick, ilp=1):
    ops = latency * ops_per_tick
    warps = (ops + 31) // 32
    return (warps + ilp - 1) // ilp
''', 'Round up both divisions.', '<p>With 2 independent instructions per warp, the 80 warp case drops to 40.</p>')

K.must('Mapping', 'Thread → core lane, warp → scheduler, block → one SM for life, grid → whole GPU.')
K.must('Warps', 'warps = ⌈B/32⌉, warp = ⌊t/32⌋, lane = t mod 32, t = x + y·Bx. Efficiency B ÷ (32 × warps).')
K.must("Little's law", 'In flight = latency × throughput. Warps = that ÷ 32. Bytes in flight = bandwidth × latency.')
K.must('Latency hiding', 'Zero cost warp switching because registers stay on chip. Need many warps or independent instructions.')
K.must('Registers', 'Registers per thread = file ÷ threads. 65,536 on modern SMs. Too many spill to slow local memory.')

T = K.topic(
    slug='warps-sms', topic='warps-sms', step=(2, 'The CUDA programming model', 'gpu-model', 'Write and launch kernels, index threads in 1, 2 and 3 dimensions, and see how warps and SMs run them and how many fit.', 'College'),
    title="SMs, warps and hiding latency", short='Warps and SMs', badge='2.3', minutes=45,
    lead="Look inside an SM, see how blocks are cut into warps of 32, and use Little's law to work out how many warps a GPU needs to hide its latency.",
    desc="The software to hardware mapping and its correction, the Fermi SM, warps, lanes and SIMT, wasted lanes, 2-D blocks into warps, Little's law for Fermi and Kepler, bytes in flight, registers per thread, spilling and naming registers.",
    summary="SM anatomy, warps and lanes, wasted lanes, Little's law and latency hiding, and registers per thread.",
    keywords=['SM', 'warp', 'lane', 'SIMT', "Little's law", 'latency hiding', 'registers', 'Fermi'],
    recap="<p>Warps of 32 are the real unit of execution. The GPU hides latency by always having another warp ready, which needs latency × throughput operations in flight.</p>")
