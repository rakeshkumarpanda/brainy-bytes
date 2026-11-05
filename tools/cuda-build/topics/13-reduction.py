# Chapter 5.1: Parallel reduction. Source: lecture 3 and 4 (adding things up serial against tree), lecture 10
# (block reductions and atomics), lecture 12 (reduction activity per step, barrier inside an if), workbook 3.3, 10.2
# and 12.1.
# Beyond the lecture: warp shuffle reductions with __shfl_down_sync, thread coarsening, and the order of float sums.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu, nb

K = Kit()

RED = r'''
#include <cstdio>

// Sum of n floats. Each block reduces 2 x blockDim values, then one atomicAdd per block.
__global__ void blockSum(const float *in, float *total, int n) {
    extern __shared__ float s[];
    int t = threadIdx.x;
    int i = blockIdx.x * blockDim.x * 2 + t;
    float v = 0.0f;
    if (i < n) v += in[i];
    if (i + blockDim.x < n) v += in[i + blockDim.x];   // each thread adds two values first
    s[t] = v;
    __syncthreads();
    for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (t < stride) s[t] += s[t + stride];          // sequential addressing: no bank conflicts
        __syncthreads();                                // outside the if: every thread reaches it
    }
    if (t == 0) atomicAdd(total, s[0]);                 // one atomic per block
}

int main() {
    const int n = 1 << 20, B = 256;
    float *d, *dt, h = 0.0f;
    cudaMalloc(&d, n * sizeof(float));
    cudaMalloc(&dt, sizeof(float));
    float *ones = new float[n];
    for (int k = 0; k < n; ++k) ones[k] = 1.0f;
    cudaMemcpy(d, ones, n * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemset(dt, 0, sizeof(float));
    int blocks = (n + 2 * B - 1) / (2 * B);
    blockSum<<<blocks, B, B * sizeof(float)>>>(d, dt, n);
    cudaMemcpy(&h, dt, sizeof(float), cudaMemcpyDeviceToHost);
    printf("sum = %.0f using %d blocks\n", h, blocks);
    delete[] ones; cudaFree(d); cudaFree(dt);
    return 0;
}
'''

SHFL = r'''
// Warp level sum with shuffles: no shared memory, no __syncthreads inside a warp
__inline__ __device__ float warpSum(float v) {
    for (int off = 16; off > 0; off >>= 1)
        v += __shfl_down_sync(0xffffffff, v, off);   // read v from lane + off
    return v;                                        // lane 0 holds the warp total
}

__global__ void sumShfl(const float *in, float *total, int n) {
    __shared__ float warpTotals[32];
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    float v = (i < n) ? in[i] : 0.0f;
    v = warpSum(v);
    int lane = threadIdx.x % 32, w = threadIdx.x / 32;
    if (lane == 0) warpTotals[w] = v;
    __syncthreads();
    if (w == 0) {
        v = (lane < blockDim.x / 32) ? warpTotals[lane] : 0.0f;
        v = warpSum(v);
        if (lane == 0) atomicAdd(total, v);
    }
}
'''

BAD = r'''
// WRONG: the barrier sits inside the if, so threads with t >= stride never reach it
__global__ void badSum(float *s) {
    int t = threadIdx.x;
    for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (t < stride) {
            s[t] += s[t + stride];
            __syncthreads();      // undefined behaviour: not all threads of the block arrive
        }
    }
}
'''

K.code('tree', r'''
# Tree reduction with sequential addressing on 8 numbers
a = [3, 1, 4, 1, 5, 9, 2, 6]
n = len(a)
stride = n // 2
level = 0
while stride > 0:
    level += 1
    for t in range(stride):          # threads t < stride work
        a[t] += a[t + stride]
    print("level", level, "stride", stride, "->", a[:stride])
    stride //= 2
print("sum =", a[0])
''')

K.code('activity', r'''
# How many threads and warps work at each level of a 1024 thread tree
B = 1024
active_total = lanes_used = 0
s = B // 2
while s >= 1:
    warps = (s + 31) // 32
    print(f"stride {s:4d}: {s:4d} threads, {warps:2d} warps, split: {s < 32}")
    active_total += s
    lanes_used += warps * 32
    s //= 2
print("lane efficiency", round(100 * active_total / lanes_used, 1), "%")
''')

K.lesson('tree', 'From a serial loop to a tree', f'''
<p>Adding n numbers with one adder takes n − 1 steps, one after another. With many threads we can add pairs at the same time: n/2 sums, then n/4, and so on, until one value is left. That needs only log₂ n levels.</p>
{fxs(
    fx('Levels', 'levels = ⌈log₂ n⌉', '1024 numbers need 10 levels instead of 1023 serial additions.', key=True),
    fx('Additions', 'total additions = n − 1', 'The tree does the same work, it only runs it in parallel.', key=True),
    fx('Barriers', 'barriers = 1 (after loading) + levels', 'A 1024 thread tree uses 11 __syncthreads().'))}
{viz('reduce')}
{code('tree')}
{scene('a knockout tournament', '<p>64 teams play a knockout. In round one 32 matches happen at the same time, then 16, 8, 4, 2 and 1. Six rounds find the winner, even though 63 matches are played in total. A tree reduction is a knockout where each match adds two numbers.</p>')}
''', kw=['reduction', 'tree', 'log2 n', 'serial sum', 'levels', 'barriers'])

K.lesson('warps', 'Which threads work: divergence and the barrier bug', f'''
<p>The pairing decides how many warps split. With <b>interleaved</b> pairing (thread t works if t mod 2s = 0) the working threads are spread out, so every warp keeps some idle lanes. With <b>sequential</b> pairing (thread t works if t &lt; s) the working threads sit together, so whole warps finish and only the last 5 levels (s = 16 to 1) split a warp.</p>
{code('activity')}
{steps('Workbook 12.1 worked example: 1024 threads, first stride 512, barrier inside the if', [
    'At stride 512 threads 0 to 511 work: warps 0 to 15 fully busy, warps 16 to 31 fully idle. No warp splits at this level.',
    'But the __syncthreads() is inside if (t < stride), so threads 512 to 1023 never reach it.',
    'The CUDA rules say every thread of the block must reach the same barrier, otherwise the behaviour is undefined.',
    eq('Move the barrier out of the if')])}
{cu('bad_sum.cu', BAD, {5: 'Only threads with t below stride enter this block.', 7: 'A barrier that some threads skip can hang the block or let threads race ahead.'})}
''', kw=['interleaved', 'sequential addressing', 'split warp', 'divergence', 'barrier inside if', 'lane efficiency'])

K.lesson('grid', 'Beyond one block: launches and atomics', f'''
<p>A block can only sum its own values. For a big array each block writes one partial sum. Then either a second launch adds the partial sums, or each block adds its result to the total with one <code>atomicAdd</code>.</p>
{fxs(
    fx('Launches without atomics', 'repeat: n ← ⌈n ÷ B⌉ until n = 1', '1,000,000 numbers with B = 256: 3907, then 16, then 1, so 3 launches.'),
    fx('Atomics needed', 'one per block = ⌈n ÷ B⌉', '2²⁰ numbers with B = 1024: 1024 atomics instead of 1,048,576.', key=True))}
{cu('block_sum.cu', RED, {5: 'Dynamic shared memory, one float per thread, size given by the third launch value.', 10: 'Thread coarsening: each thread adds two inputs before the tree, so half as many blocks are needed.', 14: 'Sequential addressing: the active threads stay packed at the front.', 15: 'The barrier is outside the if, so every thread reaches it every level.', 17: 'One atomicAdd per block makes the final total without a second launch.', 30: 'Each block covers 2 × 256 = 512 values.'}, out='sum = 1048576 using 2048 blocks')}
''', kw=['partial sums', 'second launch', 'atomicAdd', 'thread coarsening', 'grid reduction'])

K.lesson('shfl', 'Warp shuffles: the modern way', f'''
<p>Inside one warp, threads can read each other\'s registers directly with <code>__shfl_down_sync</code>. No shared memory and no barrier are needed, because the 32 lanes of a warp step together when the mask names them all.</p>
{cu('warp_sum.cu', SHFL, {3: 'Offsets 16, 8, 4, 2, 1: five steps for 32 lanes.', 4: 'Lane i adds the value held by lane i + off. The mask 0xffffffff says all 32 lanes take part.', 14: 'After warpSum, lane 0 of each warp holds that warp\'s total.', 17: 'Warp 0 then reduces the (at most 32) warp totals the same way.'})}
{note('Floating point addition is not associative (chapter 4.1), so the tree order gives a slightly different float sum from a CPU loop. Compare with a tolerance.', 'tip')}
{deep('CUB and Thrust', '<p>For production code, cub::DeviceReduce::Sum and thrust::reduce choose the block size, coarsening and shuffles for you and are tuned for each GPU. Writing your own is how you learn what they do.</p>')}
{nb('04-parallel-reduction.ipynb', 'Notebook: parallel reduction', 'Atomic sum, interleaved tree and sequential tree, all checked against NumPy.')}
''', kw=['warp shuffle', '__shfl_down_sync', 'mask', 'CUB', 'Thrust'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Adding numbers in pairs, then pairs of sums, finishes in a few rounds, like a knockout tournament.</p>',
    '<p>log₂ n levels, n − 1 additions, barriers outside ifs, sequential addressing, one atomic per block, shuffles inside warps.</p>',
    '<p>The classic NVIDIA reduction sequence: interleaved, sequential addressing, first add during load, unroll the last warp, complete unrolling, many elements per thread. Each step removes a bottleneck and the last versions reach close to full memory bandwidth.</p>',
    '<p>A reduction reads every byte once with AI near 0.25, so it is memory bound. The target is the bandwidth roof. Decoupled look back (Merrill and Garland) does single pass scans and reductions across the whole grid.</p>')}
''', kw=['ladder', 'unroll last warp', 'bandwidth bound', 'decoupled look back'])

K.quiz('e', 'Levels to add 1024 numbers with a tree', ['10', '32', '512', '1023'], 0, 'log₂ 1024.', '10.')
K.quiz('e', 'Total additions in a tree for n numbers', ['log₂ n', 'n − 1', 'n²', 'n ÷ 2'], 1, 'Same as serial.', 'n − 1.')
K.quiz('e', '[3, 1, 4, 1, 5, 9, 2, 6] sums to', ['29', '30', '31', '32'], 2, 'Add them.', '31.')
K.quiz('m', 'Why is the barrier needed between levels?', ['To free memory', 'A thread reads a partner\'s value that must be written first', 'To speed up', 'It is not needed'], 1,
       'Data dependency.', 'Level k+1 reads results of level k.')
K.quiz('m', 'Sequential addressing is better than interleaved because', ['It uses fewer threads in total', 'Active threads are packed, so fewer warps split and no bank conflicts', 'It needs no barriers', 'It uses atomics'], 1,
       'Packing.', 'Whole warps become idle together.')
K.quiz('m', 'N = 1,000,000, B = 256, no atomics. Launches?', ['1', '2', '3', '4'], 2, '3907 → 16 → 1.', '3 launches.')
K.quiz('m', 'Barriers in a 1024 thread tree', ['10', '11', '32', '1024'], 1, '1 + 10.', '11.')
K.quiz('h', 'A __syncthreads() inside if (t < stride) is', ['Fine', 'Undefined behaviour: not all threads reach it', 'Faster', 'Needed'], 1,
       'All must arrive.', 'Move it out of the if.')
K.quiz('h', 'From which level of a 1024 tree do fewer than 32 threads work?', ['Level 1', 'Level 5', 'Level 6', 'Level 10'], 2, 'Stride 16.', 'Level 6 has 16 threads.')
K.quiz('h', '__shfl_down_sync(0xffffffff, v, 4) gives lane 3', ['Its own v', 'Lane 7\'s v', 'Lane 0\'s v', 'The warp sum'], 1, 'lane + 4.', 'Lane 7.')
K.quiz('x', 'Lane efficiency of the 1024 thread sequential tree', ['50 percent', 'About 89 percent', '100 percent', 'About 10 percent'], 1,
       '1023 active of 1152 lanes.', 'Warps that run at stride 16 to 1 are part full.')
K.quiz('x', 'Atomics for 2²⁰ numbers with 1024 thread blocks, one per block', ['1', '1024', '1,048,576', '20'], 1, '2²⁰ ÷ 2¹⁰.', '1024.')

K.calc('e', 'Levels and additions for B = 256? (give additions)', '255', 'n − 1.',
       ['Levels log₂ 256 = 8.', 'Additions 256 − 1.', eq('8 levels, 255 additions')], check=255)
K.calc('e', 'Add [2, 7, 1, 8] with a tree.', '18', 'Stride 2 then 1.',
       ['Stride 2: [2 + 1, 7 + 8] = [3, 15].', 'Stride 1: 3 + 15.', eq('18')], check=18)
K.calc('e', 'Threads working at level 1, 5 and 10 of a 1024 tree: give level 5.', '32', '1024 ÷ 2⁵.',
       ['Level 1: 512.', 'Level 5: 1024 ÷ 32.', eq('32 (level 10: 1)')], check=1024 // 32)
K.calc('m', 'N = 1000. Levels? ', '10', '⌈log₂ 1000⌉.',
       ['2⁹ = 512 < 1000.', '2¹⁰ = 1024 ≥ 1000.', eq('10 levels, 999 real additions')], check=10)
K.calc('m', 'Average share of threads working over the 10 levels of a 1024 tree, percent? (nearest whole)', '10', 'Sum of active ÷ (10 × 1024).',
       ['512 + 256 + … + 1 = 1023.', '1023 ÷ 10,240.', eq('≈ 10 percent')], check=round(100 * 1023 / 10240), tol=0.5)
K.calc('m', 'B = 512: how many levels split a warp (fewer than 32 active)?', '5', 'Strides 16, 8, 4, 2, 1.',
       ['9 levels: strides 256 down to 1.', 'Below 32: 16, 8, 4, 2, 1.', eq('5 split levels')], check=5)
K.calc('m', '2²⁰ numbers, 1024 thread blocks. Blocks in the first launch?', '1024', '2²⁰ ÷ 2¹⁰.',
       ['1,048,576 ÷ 1024.', '= 1024 partial sums.', eq('1024 blocks, then one more block: 20 levels in 2 launches')], check=1024)
K.calc('h', 'Lane efficiency of the 1024 tree in percent? (one decimal)', '88.8', 'Active ÷ lanes in active warps.',
       ['Active 1023.', 'Lanes: 5 levels with s ≥ 32 use 512 + 256 + 128 + 64 + 32 = 992 lanes, plus 5 split levels × 32 = 160. Total 1152.', eq('1023 ÷ 1152 = 88.8 percent')], check=100 * 1023 / 1152, tol=0.05)
K.calc('h', 'Share of threads working at level 6 of a 1024 tree, percent? (one decimal)', '1.6', '16 ÷ 1024.',
       ['Level 6: stride 16.', '16 ÷ 1024 = 0.0156.', eq('1.6 percent')], check=100 * 16 / 1024, tol=0.05)
K.calc('x', '256 threads each add 4 numbers first, then a tree. Steps to sum 1024 numbers?', '11', '3 serial adds + 8 levels.',
       ['Each thread adds 4 values: 3 steps.', 'Tree over 256: 8 levels.', eq('11 steps with a quarter of the threads')], check=3 + 8)
K.calc('x', 'Shuffle steps to sum one warp?', '5', 'Offsets 16, 8, 4, 2, 1.',
       ['32 lanes.', 'log₂ 32.', eq('5 shuffles')], check=5)

K.assign('treesum', 'e', 'Tree reduction',
         '<p>Write <code>tree_sum(a)</code> for a list whose length is a power of two. Use sequential addressing (stride n/2, n/4, … 1). Return <code>[total, levels]</code>.</p>',
         '''
def tree_sum(a):
    # your code here
    pass
''', [("tree_sum([3, 1, 4, 1, 5, 9, 2, 6])", [31, 3]), ("tree_sum([2, 7, 1, 8])", [18, 2]), ("tree_sum([5])", [5, 0])],
         '''
def tree_sum(a):
    a = list(a)
    s = len(a) // 2
    levels = 0
    while s > 0:
        for t in range(s):
            a[t] += a[t + s]
        s //= 2
        levels += 1
    return [a[0], levels]
''', 'Halve the stride each level.', '<p>One element needs no levels.</p>')
K.assign('launches', 'm', 'Launches for a grid reduction',
         '<p>Write <code>launches(n, b)</code>: the number of kernel launches needed when each launch turns n values into ⌈n ÷ b⌉ partial sums, until one value is left.</p>',
         '''
def launches(n, b):
    # your code here
    pass
''', [("launches(1000000, 256)", 3), ("launches(1048576, 1024)", 2), ("launches(100, 256)", 1), ("launches(1, 256)", 0)],
         '''
def launches(n, b):
    k = 0
    while n > 1:
        n = (n + b - 1) // b
        k += 1
    return k
''', 'Repeat the ceiling division.', '<p>A single value needs no launch.</p>')

K.must('Tree', 'log₂ n levels, n − 1 additions, 1 + levels barriers. 1024 → 10 levels, 11 barriers.')
K.must('Pairing', 'Sequential (t < s, s halves) packs active threads: only levels with s < 32 split a warp.')
K.must('Barrier rule', 'Every thread must reach every __syncthreads(). Never put it inside a divergent if.')
K.must('Grid', 'One atomicAdd per block (⌈n/B⌉ atomics) or repeated launches until one value is left.')
K.must('Shuffles', '__shfl_down_sync with offsets 16 to 1 sums a warp in 5 steps without shared memory.')

T = K.topic(
    slug='reduction', topic='reduction', step=(5, 'Parallel patterns', 'gpu-patterns', 'Learn the patterns behind most GPU code: reductions, tiled matrix multiply, stencils, convolution and scans.', 'College'),
    title='Parallel reduction', short='Reduction', badge='5.1', minutes=50,
    lead='Add up millions of numbers in parallel with a tree, keep warps busy with the right pairing, avoid the barrier bug, and finish across blocks with atomics or warp shuffles.',
    desc='Serial against tree sums, levels and additions, interleaved and sequential addressing, split warps and lane efficiency, the barrier inside an if bug, multiple launches, atomics per block, thread coarsening and warp shuffles.',
    summary='Tree reduction, pairing and divergence, barrier rule, grid level reductions, atomics and warp shuffles.',
    keywords=['reduction', 'tree', 'atomicAdd', 'warp shuffle', '__syncthreads', 'divergence'],
    recap='<p>A tree reduction finishes in log₂ n levels. Keep active threads packed, put barriers where every thread reaches them, and use one atomic per block or warp shuffles to finish.</p>')
