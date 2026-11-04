# Chapter 3.1: The memory hierarchy. Source: lecture 2 (memory hierarchy slide: per thread, per block, global,
# constant, texture), lecture 3 and 4 notes (scope, lifetime and speed table, constant memory explained, why several
# memories, pageable against pinned), Quiz 1 question 8 and Rakesh's worked solution.
# Beyond the lecture: unified memory with prefetch, the L1 and L2 caches as hardware copies, __restrict__ and
# read only loads, and the cost of host to device copies.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu, nb

K = Kit()

CONST = r'''
#include <cstdio>

__constant__ float c_weights[9];          // 36 bytes in constant memory, read only for kernels

__global__ void blur3x3(const float *in, float *out, int w, int h) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int y = blockIdx.y * blockDim.y + threadIdx.y;
    if (x < 1 || y < 1 || x >= w - 1 || y >= h - 1) return;
    float s = 0.0f;
    for (int dy = -1; dy <= 1; ++dy)
        for (int dx = -1; dx <= 1; ++dx)
            s += c_weights[(dy + 1) * 3 + (dx + 1)] * in[(y + dy) * w + (x + dx)];
    out[y * w + x] = s;
}

int main() {
    float h_w[9];
    for (int k = 0; k < 9; ++k) h_w[k] = 1.0f / 9.0f;
    cudaMemcpyToSymbol(c_weights, h_w, sizeof(h_w));
    printf("weights copied to constant memory\n");
    return 0;
}
'''

PINNED = r'''
#include <cstdio>
#include <cstdlib>

int main() {
    const size_t bytes = 256u << 20;               // 256 MB
    float *pageable = (float *)malloc(bytes);
    float *pinned = nullptr;
    cudaMallocHost(&pinned, bytes);                // page locked host memory
    float *d = nullptr;
    cudaMalloc(&d, bytes);

    cudaEvent_t t0, t1;
    cudaEventCreate(&t0); cudaEventCreate(&t1);
    float ms = 0.0f;

    cudaEventRecord(t0);
    cudaMemcpy(d, pageable, bytes, cudaMemcpyHostToDevice);
    cudaEventRecord(t1); cudaEventSynchronize(t1);
    cudaEventElapsedTime(&ms, t0, t1);
    printf("pageable: %.2f GB/s\n", bytes / ms / 1e6);

    cudaEventRecord(t0);
    cudaMemcpy(d, pinned, bytes, cudaMemcpyHostToDevice);
    cudaEventRecord(t1); cudaEventSynchronize(t1);
    cudaEventElapsedTime(&ms, t0, t1);
    printf("pinned:   %.2f GB/s\n", bytes / ms / 1e6);

    cudaFree(d); cudaFreeHost(pinned); free(pageable);
    return 0;
}
'''

UNIFIED = r'''
#include <cstdio>

__global__ void addOne(float *a, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) a[i] += 1.0f;
}

int main() {
    int n = 1 << 20, dev = 0;
    float *a = nullptr;
    cudaMallocManaged(&a, n * sizeof(float));      // one pointer for CPU and GPU
    for (int i = 0; i < n; ++i) a[i] = i;           // pages start on the CPU
    cudaMemPrefetchAsync(a, n * sizeof(float), dev); // move them before the kernel needs them
    addOne<<<(n + 255) / 256, 256>>>(a, n);
    cudaDeviceSynchronize();                        // wait before the CPU reads
    printf("a[10] = %.1f\n", a[10]);
    cudaFree(a);
    return 0;
}
'''

K.code('copy', r'''
# How long does a copy take? time = bytes / bandwidth (+ a small fixed start up cost)
links = {"PCIe 4.0 x8 laptop": 14e9, "PCIe 4.0 x16": 25e9, "GPU DRAM (A100)": 1555e9}
size = 256 * 2**20          # 256 MB
for name, bw in links.items():
    print(f"{name:20s}: {1000 * size / bw:7.2f} ms")
''')

K.lesson('spaces', 'Five places a value can live', f'''
<p>A GPU has several memories because no memory can be big, fast and visible to everyone all at once. Fast memory sits on the chip and is small. Big memory is far away and slow. CUDA gives you a menu and lets you choose.</p>
{table(['Memory', 'Who sees it', 'Lives for', 'Speed', 'How you get it'], [
    ['Registers', 'one thread', 'the thread', 'about 1 tick', 'any normal local variable'],
    ['Local', 'one thread', 'the thread', 'DRAM speed (cached)', 'big private arrays, spilled registers'],
    ['Shared', 'all threads of one block', 'the block', 'about 20 to 30 ticks', '__shared__'],
    ['Global', 'all threads, all kernels, the host', 'until cudaFree', 'about 400 to 800 ticks', 'cudaMalloc'],
    ['Constant', 'all threads, read only', 'the application', 'fast when the warp reads one address', '__constant__ and cudaMemcpyToSymbol']])}
{viz('memhier')}
{note('Local memory is not near the thread. "Local" means private. It lives in device DRAM and is only cached on chip.', 'warn')}
{scene('a kitchen', '<p>The chopping board in front of a cook is a register: tiny, private, instant. The shared counter of one cooking team is shared memory. The big store room everyone walks to is global memory. The recipe card pinned on the wall that nobody may change is constant memory.</p>')}
''', kw=['registers', 'local memory', 'shared memory', 'global memory', 'constant memory', 'scope', 'lifetime'])

K.lesson('q8', 'Quiz 1 question 8: visible to all SMs, for the whole application', f'''
<p>The question asks which memory every SM can reach directly and which lasts for the whole program. Test each option for both properties.</p>
{steps('Rakesh\'s worked solution', [
    'Shared memory belongs to one block on one SM, so it fails the "all SMs" test.',
    'L1 cache is private to each SM, so it fails too.',
    'L2 cache is shared by all SMs, but it is a cache, not a memory space. You cannot allocate in it and the hardware evicts what it likes.',
    'Global memory is addressed by every thread on every SM, and an allocation lives until cudaFree or program exit.',
    eq('Answer: option 1, global memory')])}
{note('A memory space is something you name and address. A cache is a hardware copy of global data that fills and empties by itself. This difference decides questions like Q8.', 'exam')}
''', kw=['Quiz 1 question 8', 'global memory', 'L2 cache', 'memory space against cache'])

K.lesson('constant', 'Constant memory and caches', f'''
<p>Constant memory holds small read only values such as filter weights. The host writes it before the launch. When all 32 threads of a warp read the <b>same</b> address, one fetch is broadcast to the whole warp. If they read different addresses, the reads are done one after another.</p>
{cu('blur_constant.cu', CONST, {3: '__constant__ puts the array in the 64 KB constant bank. Kernels may read it but never write it.', 12: 'Every thread of the warp reads the same weight at the same loop step, so the broadcast works perfectly.', 18: 'The weights are made on the CPU first.', 19: 'cudaMemcpyToSymbol copies host data into a __constant__ variable by its name.'}, out='weights copied to constant memory')}
{table(['Cache', 'Where', 'What it holds'], [
    ['L1 / texture', 'per SM, shares space with shared memory', 'recent global and local loads'],
    ['Constant cache', 'per SM', 'recent constant memory reads'],
    ['L2', 'one for the whole GPU', 'all traffic to device DRAM (40 MB on an A100)']])}
{deep('read only loads and __restrict__', '<p>Marking pointers <code>const float *__restrict__ in</code> tells the compiler that no other pointer writes the same data, so it may use the read only data path. The function <code>__ldg(&amp;in[i])</code> asks for it directly.</p>')}
''', kw=['constant memory', 'cudaMemcpyToSymbol', 'broadcast', 'L1', 'L2', 'texture cache', '__restrict__', '__ldg'])

K.lesson('host', 'Host memory: pageable, pinned and unified', f'''
<p>Data starts in the CPU\'s RAM. Normal <code>malloc</code> memory is <b>pageable</b>: the operating system may move it. The GPU\'s copy engine cannot read such memory directly, so the driver first copies it into a hidden locked buffer. <b>Pinned</b> (page locked) memory from <code>cudaMallocHost</code> skips that extra copy and is required for copies that overlap with kernels (chapter 6.2).</p>
{fxs(
    fx('Copy time', 't = bytes ÷ bandwidth', 'The PCIe link is far slower than the GPU\'s own DRAM, so copy once and reuse.', key=True),
    fx('Worth sending to the GPU', 't<sub>copy in</sub> + t<sub>kernel</sub> + t<sub>copy out</sub> &lt; t<sub>CPU</sub>', 'From chapter 1.2: count the copies too.'))}
{cu('pinned_vs_pageable.cu', PINNED, {8: 'cudaMallocHost returns page locked memory. Use it for buffers you copy often, and do not lock too much of the RAM.', 12: 'CUDA events time work on the GPU timeline. Elapsed time comes back in milliseconds.', 20: 'bytes ÷ ms ÷ 10⁶ gives GB/s.', 28: 'Every cudaMallocHost needs a cudaFreeHost.'}, out='(typical result: pinned is faster than pageable, how much depends on the machine)')}
{cu('unified.cu', UNIFIED, {11: 'cudaMallocManaged gives one pointer that works on both CPU and GPU. Pages move on demand.', 13: 'Prefetching moves the pages before the kernel starts, so the kernel does not stop on page faults.', 15: 'The CPU must wait before reading results, otherwise it reads old values.'}, out='a[10] = 11.0')}
{code('copy')}
{nb('03-memory-and-timing.ipynb', 'Notebook: copies, pinned memory and honest timing', 'CUDA events, pageable against pinned copies, and Amdahl with the copy time.')}
''', kw=['pageable', 'pinned memory', 'cudaMallocHost', 'unified memory', 'cudaMallocManaged', 'prefetch', 'PCIe', 'copy time'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Close memory is small and fast, far memory is big and slow. Keep the things you use again and again close by.</p>',
    '<p>Registers (thread), shared (block), global (all, host too), constant (all, read only, broadcast), local (private, but in DRAM). Copy time = bytes ÷ bandwidth. Pinned memory is needed for async copies.</p>',
    '<p>A good kernel loads each byte from DRAM once and reuses it many times from registers and shared memory. That is the idea of tiling (chapters 5.2 to 5.4). The roofline (chapter 4.2) turns this into numbers.</p>',
    '<p>Hopper adds distributed shared memory between the blocks of a cluster and the Tensor Memory Accelerator, which copies whole tiles from global to shared memory without using threads.</p>')}
''', kw=['ladder', 'reuse', 'distributed shared memory', 'TMA'])

K.quiz('e', 'A normal local variable like int i lives in', ['Global memory', 'A register', 'Shared memory', 'Constant memory'], 1,
       'Fastest and private.', 'The compiler puts it in a register when it can.')
K.quiz('e', 'Which memory do all threads of one block share?', ['Registers', 'Shared memory', 'Local memory', 'Host RAM'], 1,
       '__shared__.', 'One copy per block.')
K.quiz('e', 'Quiz 1 question 8: visible to all SMs for the whole application', ['Global memory', 'L1 cache', 'L2 cache', 'Shared memory'], 0,
       'Scope and lifetime.', 'Global memory is addressable everywhere and lives until cudaFree.')
K.quiz('m', 'Local memory physically lives in', ['Registers', 'Shared memory', 'Device DRAM', 'The CPU'], 2,
       '"Local" means private.', 'It is in DRAM, cached in L1 and L2.')
K.quiz('m', 'Constant memory is fastest when', ['Each thread reads a different address', 'All threads of a warp read the same address', 'Kernels write it', 'It is larger than 64 KB'], 1,
       'Broadcast.', 'One fetch serves all 32 lanes.')
K.quiz('m', 'Who writes constant memory?', ['Any kernel', 'The host, with cudaMemcpyToSymbol', 'Only block 0', 'The L2 cache'], 1,
       'Read only for kernels.', 'The host fills it before the launch.')
K.quiz('m', 'Why can L2 not be the answer to Q8?', ['It is too small', 'It is a cache, not an addressable memory space', 'It is per SM', 'It is on the CPU'], 1,
       'Space versus cache.', 'You cannot allocate in L2 or rely on data staying there.')
K.quiz('h', 'Why must memory be pinned for cudaMemcpyAsync to overlap with a kernel?', ['Pinned is faster DRAM', 'The copy engine needs pages the OS cannot move, otherwise the driver stages through a buffer', 'It is in the GPU', 'It is not required'], 1,
       'DMA.', 'Pageable memory forces a synchronous staging copy.')
K.quiz('h', 'cudaMemPrefetchAsync on managed memory helps because', ['It frees memory', 'It moves pages to the GPU before the kernel, avoiding page faults during it', 'It compresses data', 'It pins memory'], 1,
       'Page faults.', 'Faulting pages one by one inside a kernel is slow.')
K.quiz('h', 'A kernel declares float tmp[64] and indexes it with a loop variable the compiler cannot unroll. tmp most likely goes to', ['Registers', 'Local memory', 'Shared memory', 'Constant memory'], 1,
       'Registers cannot be indexed at run time.', 'Dynamically indexed arrays usually go to local memory.')
K.quiz('x', 'Each block needs a 4 KB lookup table read with random indices by every thread. Best home?', ['Constant memory', 'Shared memory loaded once per block', 'Local memory', 'Host memory'], 1,
       'Random indices break constant broadcast.', 'Shared memory serves different addresses in parallel across banks.')
K.quiz('x', 'Which pair is the same physical memory?', ['Shared and L1', 'Registers and shared', 'Constant and L2', 'Global and registers'], 0,
       'Carve out.', 'On recent GPUs shared memory and L1 are carved from one on chip SRAM.')

K.calc('e', 'Copy 256 MB over a 16 GB/s link. Time in ms? (one decimal, MB = 2²⁰ bytes, GB = 10⁹)', '16.8', 't = bytes ÷ bandwidth.',
       ['256 × 2²⁰ = 268,435,456 bytes.', '268,435,456 ÷ 16 × 10⁹ = 0.01678 s.', eq('≈ 16.8 ms')], check=1000 * 256 * 2**20 / 16e9, tol=0.05)
K.calc('e', 'A 3 × 3 float filter in constant memory takes how many bytes?', '36', '9 × 4.',
       ['9 weights.', '4 bytes each.', eq('36 bytes')], check=36)
K.calc('e', 'How many floats fit in 64 KB of constant memory?', '16384', '65,536 ÷ 4.',
       ['64 KB = 65,536 bytes.', '÷ 4 bytes.', eq('16,384 floats')], check=65536 // 4)
K.calc('m', 'Kernel 2 ms, two copies of 8 ms each. Share of time spent copying in percent?', '88.9', 'Copies ÷ total.',
       ['Total = 8 + 2 + 8 = 18 ms.', 'Copies 16 ms.', eq('16 ÷ 18 = 88.9 percent')], check=100 * 16 / 18, tol=0.05)
K.calc('m', 'Same data read once from A100 DRAM (1555 GB/s) or once over PCIe at 25 GB/s. How many times faster is DRAM? (one decimal)', '62.2', 'Ratio of bandwidths.',
       ['Time is bytes ÷ bandwidth.', 'Ratio 1555 ÷ 25.', eq('62.2 times')], check=1555 / 25, tol=0.05)
K.calc('m', 'A warp reads 32 different constant addresses. How many serial fetches?', '32', 'No broadcast.',
       ['Constant memory serves one address at a time.', '32 different addresses.', eq('32 fetches (1 if all equal)')], check=32)
K.calc('m', 'A block of 256 threads keeps float tile[256] in shared memory. Bytes per block?', '1024', '256 × 4.',
       ['256 floats.', '4 bytes each.', eq('1024 bytes')], check=1024)
K.calc('h', 'CPU 40 ms. GPU kernel 2 ms, copies 12 ms in and 6 ms out. Speedup including copies?', '2', 'Divide by the full GPU time.',
       ['GPU total = 12 + 2 + 6 = 20 ms.', '40 ÷ 20.', eq('2 times (20 times for the kernel alone)')], check=40 / 20)
K.calc('h', 'Same job, but the data stays on the GPU for 10 kernels (copy once in and once out). Speedup? (one decimal)', '10.5', '10 CPU runs against one GPU pipeline.',
       ['CPU 10 × 40 = 400 ms.', 'GPU: copy in 12 ms once, 10 kernels × 2 ms = 20 ms, copy out 6 ms once, total 38 ms.', eq('400 ÷ 38 = 10.5 times')], check=400 / 38, tol=0.05)
K.calc('x', 'A100 L2 is 40 MB. How many 1024 × 1024 float matrices fit at once?', '10', '4 MB each.',
       ['1024 × 1024 × 4 = 4,194,304 bytes = 4 MiB.', '40 MB ÷ 4 MiB (taking MB = MiB here).', eq('10 matrices')], check=40 // 4)
K.calc('x', 'Unified memory pages are 64 KB. A kernel touches 256 MB of managed data with no prefetch. Page migrations?', '4096', '256 MB ÷ 64 KB.',
       ['256 × 1024 KB = 262,144 KB.', '÷ 64 KB.', eq('4096 migrations (each one a page fault)')], check=256 * 1024 // 64)

K.assign('where', 'e', 'Where does it live?',
         '<p>Write <code>where(decl)</code> that returns one of <code>"register"</code>, <code>"shared"</code>, <code>"global"</code>, <code>"constant"</code> for these declaration styles: a string starting with <code>__shared__</code>, <code>__constant__</code>, containing <code>cudaMalloc</code>, or anything else (a plain local variable).</p>',
         '''
def where(decl):
    # your code here
    pass
''', [("where('__shared__ float t[256];')", "shared"), ("where('__constant__ float w[9];')", "constant"), ("where('cudaMalloc(&d, n);')", "global"), ("where('int i = threadIdx.x;')", "register")],
         '''
def where(decl):
    d = decl.strip()
    if d.startswith('__shared__'):
        return 'shared'
    if d.startswith('__constant__'):
        return 'constant'
    if 'cudaMalloc' in d:
        return 'global'
    return 'register'
''', 'Check the keywords in order.', '<p>Real compilers can also push a local variable to local memory when it is large or indexed at run time.</p>')
K.assign('worth', 'm', 'Is the GPU worth it with copies?',
         '<p>Write <code>speedup(cpu_ms, mb_in, mb_out, kernel_ms, gbps, runs)</code>. The data is copied in once and out once (MB = 10⁶ bytes, GB/s = 10⁹ bytes per second) and the kernel runs <code>runs</code> times, against the CPU running <code>runs</code> times. Return the speedup rounded to 2 decimals.</p>',
         '''
def speedup(cpu_ms, mb_in, mb_out, kernel_ms, gbps, runs):
    # your code here
    pass
''', [("speedup(40, 192, 96, 2, 16, 1)", 2.0), ("speedup(40, 192, 96, 2, 16, 10)", 10.53), ("speedup(5, 400, 400, 1, 25, 1)", 0.15)],
         '''
def speedup(cpu_ms, mb_in, mb_out, kernel_ms, gbps, runs):
    copy_ms = (mb_in + mb_out) * 1e6 / (gbps * 1e9) * 1000
    gpu = copy_ms + kernel_ms * runs
    return round(cpu_ms * runs / gpu, 2)
''', 'Copy time is bytes ÷ bandwidth, counted once.', '<p>Keeping data on the GPU across many kernels is what makes the copies pay off.</p>')

K.must('Spaces', 'Register (thread), local (thread, in DRAM), shared (block), global (all, host, until cudaFree), constant (all, read only).')
K.must('Q8', 'Visible to all SMs for the whole application: global memory. L2 is a cache, not a space.')
K.must('Constant', '64 KB, host writes with cudaMemcpyToSymbol, broadcast when a warp reads one address.')
K.must('Host memory', 'Pageable malloc, pinned cudaMallocHost (needed for async overlap), managed cudaMallocManaged with prefetch.')
K.must('Copies', 'Copy time = bytes ÷ bandwidth. PCIe is far slower than device DRAM. Copy once, reuse many times.')

T = K.topic(
    slug='memory-hierarchy', topic='memory-hierarchy', step=(3, 'GPU memory', 'gpu-memory', 'Learn where data lives, how a warp reads global memory in sectors, and how shared memory banks work.', 'College'),
    title='The GPU memory hierarchy', short='Memory hierarchy', badge='3.1', minutes=45,
    lead='Learn the five places a value can live on a GPU, who can see each one and for how long, and how data gets from the CPU to the GPU.',
    desc='Registers, local, shared, global and constant memory with scope, lifetime and speed, Quiz 1 question 8, constant memory broadcast, L1 and L2 caches, pageable, pinned and unified memory and copy times.',
    summary='Memory spaces, scope and lifetime, constant memory, caches, pinned and unified memory, copy time.',
    keywords=['memory hierarchy', 'registers', 'shared memory', 'global memory', 'constant memory', 'pinned memory', 'unified memory'],
    recap='<p>Fast memory is small and private, big memory is slow and shared. Global memory is the only space every SM sees for the whole program. Pinned memory makes copies faster and lets them overlap.</p>')
