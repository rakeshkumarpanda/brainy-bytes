# Chapter 2.1: the first CUDA program. Source: lecture 3 (workload execution, the nine step recipe, hello world with
# device code, parallel blocks, the full vector addition program, arbitrary sizes, host and device coordination,
# JIT CUDA from Python with Numba), Quiz 1 question 6 (kernel return type) and question 8 (global memory).
# Beyond the lecture: error checking with cudaGetLastError, compiling with nvcc for a target architecture, and
# unified memory with cudaMallocManaged, checked against the CUDA C++ Programming Guide.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu, sh, nb, flow

K = Kit()

VADD = r'''
#include <cstdio>
#include <cstdlib>
#include <cuda_runtime.h>

#define CHECK(call) do { cudaError_t e = (call); if (e != cudaSuccess) { \
    printf("CUDA error %s at line %d\n", cudaGetErrorString(e), __LINE__); exit(1); } } while (0)

__global__ void add(const float* a, const float* b, float* c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) c[i] = a[i] + b[i];
}

int main() {
    int n = 1000000;
    size_t bytes = n * sizeof(float);
    float *a = (float*)malloc(bytes), *b = (float*)malloc(bytes), *c = (float*)malloc(bytes);
    for (int i = 0; i < n; i++) { a[i] = i; b[i] = 2.0f * i; }

    float *d_a, *d_b, *d_c;
    CHECK(cudaMalloc(&d_a, bytes));
    CHECK(cudaMalloc(&d_b, bytes));
    CHECK(cudaMalloc(&d_c, bytes));
    CHECK(cudaMemcpy(d_a, a, bytes, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(d_b, b, bytes, cudaMemcpyHostToDevice));

    int threads = 256;
    int blocks = (n + threads - 1) / threads;
    add<<<blocks, threads>>>(d_a, d_b, d_c, n);
    CHECK(cudaGetLastError());
    CHECK(cudaMemcpy(c, d_c, bytes, cudaMemcpyDeviceToHost));

    printf("c[10] = %.1f, c[%d] = %.1f\n", c[10], n - 1, c[n - 1]);
    CHECK(cudaFree(d_a)); CHECK(cudaFree(d_b)); CHECK(cudaFree(d_c));
    free(a); free(b); free(c);
    return 0;
}
'''

HELLO = r'''
#include <cstdio>

__global__ void hello() {
    printf("Hello from block %d, thread %d\n", blockIdx.x, threadIdx.x);
}

int main() {
    hello<<<2, 3>>>();
    cudaDeviceSynchronize();
    return 0;
}
'''

MANAGED = r'''
#include <cstdio>

__global__ void scale(float* x, float s, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) x[i] *= s;
}

int main() {
    int n = 1 << 20;
    float* x;
    cudaMallocManaged(&x, n * sizeof(float));
    for (int i = 0; i < n; i++) x[i] = 1.0f;
    scale<<<(n + 255) / 256, 256>>>(x, 3.0f, n);
    cudaDeviceSynchronize();
    printf("x[0] = %.1f\n", x[0]);
    cudaFree(x);
    return 0;
}
'''

K.code('recipe', r'''
# The CUDA recipe, simulated in plain Python: host lists, "device" lists, and a kernel run by every thread
n, threads = 10, 4
a = [i for i in range(n)]
b = [2 * i for i in range(n)]
d_a, d_b = a[:], b[:]                  # cudaMemcpy host to device
d_c = [0] * n                          # cudaMalloc
blocks = (n + threads - 1) // threads  # round up: 3 blocks
for blockIdx in range(blocks):         # on a GPU all of these run at the same time
    for threadIdx in range(threads):
        i = blockIdx * threads + threadIdx
        if i < n:                      # the guard: threads 10 and 11 do nothing
            d_c[i] = d_a[i] + d_b[i]
c = d_c[:]                             # cudaMemcpy device to host
print("blocks", blocks, "threads", blocks * threads)
print(c)
''')

K.lesson('recipe', 'Host, device and the recipe every program follows', f'''
<p>A CUDA program is an ordinary C++ program that runs on the CPU (the <b>host</b>) and now and then hands a function, called a <b>kernel</b>, to the GPU (the <b>device</b>). Host and device have separate memories, so data must be copied across.</p>
{flow(('Allocate on host', 'malloc or new'), ('Allocate on device', 'cudaMalloc'), ('Copy in', 'cudaMemcpy host to device'), ('Launch', 'kernel&lt;&lt;&lt;blocks, threads&gt;&gt;&gt;'), ('Copy out', 'cudaMemcpy device to host'), ('Free', 'cudaFree and free'))}
{viz('hostflow')}
{table(['Qualifier', 'Runs on', 'Called from', 'Notes'], [
    ['__global__', 'device', 'host (and device with dynamic parallelism)', 'A kernel. Must return void. Launched with &lt;&lt;&lt; &gt;&gt;&gt;'],
    ['__device__', 'device', 'device', 'A helper function used inside kernels. May return any type'],
    ['__host__', 'host', 'host', 'The default for normal functions'],
    ['__host__ __device__', 'both', 'both', 'Compiled twice, handy for small maths helpers']])}
{note('Quiz 1 question 6: the correct kernel signature is __global__ void. A kernel cannot return a value, because thousands of threads run it and the launch returns to the host at once without waiting. Results go back through memory. __shared__ is a memory space, not a function qualifier.', 'exam')}
{code('recipe')}
{scene('posting parcels to a factory', '<p>You (the host) pack raw material into boxes, ship them to a factory (cudaMemcpy), send a work order (the launch), and wait for the finished goods to be shipped back. The factory has thousands of workers, but nothing happens until the material arrives, and you cannot use the goods until they come back.</p>')}
''', kw=['host', 'device', 'kernel', '__global__', '__device__', '__host__', 'cudaMalloc', 'cudaMemcpy', 'recipe'])

K.lesson('vadd', 'The complete vector addition program', f'''
{cu('vector_add.cu', VADD, {
    3: 'The CUDA runtime header: cudaMalloc, cudaMemcpy, cudaFree and the error types. nvcc includes it automatically, but writing it makes the file clearer.',
    5: 'A small macro that checks every CUDA call. Almost every CUDA function returns a cudaError_t. Without checks a failed call goes unnoticed and later results are silently wrong.',
    8: '__global__ marks a kernel: it runs on the GPU, is launched from the host, and must return void. const and pointers to device memory are normal C++.',
    9: 'The global thread index. Each thread computes a different i, so each handles a different element.',
    10: 'The guard. We launch a whole number of blocks, so some threads may have i ≥ n. They must do nothing, or they write past the end of the array.',
    15: 'size_t for byte counts, because large arrays overflow a 32 bit int.',
    16: 'Host memory, allocated with ordinary malloc.',
    20: 'cudaMalloc reserves memory in the GPU\'s global memory and writes the device address into d_a. The host must never dereference d_a.',
    23: 'Copy the input from host to device over PCIe. The last argument names the direction.',
    26: 'Threads per block: a multiple of 32 (a warp). 128 to 512 is a good default.',
    27: 'Blocks needed = ⌈n ÷ threads⌉ using whole number arithmetic. For a million elements that is 3907 blocks.',
    28: 'The launch. &lt;&lt;&lt;blocks, threads&gt;&gt;&gt; is the execution configuration. It returns to the host immediately, the GPU runs in the background.',
    29: 'A launch returns no error code, so ask for it. This catches a bad configuration such as 2000 threads per block.',
    30: 'Copy the result back. This cudaMemcpy waits until the kernel has finished, so it also synchronises.',
    33: 'Give the device memory back. Leaking it in a loop eventually makes cudaMalloc fail.'}, out='c[10] = 30.0, c[999999] = 2999997.0')}
{sh('Compile and run with nvcc', '''
nvcc -O3 -arch=sm_75 vector_add.cu -o vector_add
./vector_add
# on Google Colab, put %%writefile vector_add.cu at the top of a cell, then run !nvcc ... in the next cell
''', 'c[10] = 30.0, c[999999] = 2999997.0')}
<p><b>-arch=sm_75</b> compiles for compute capability 7.5 (a T4). Use sm_80 for an A100, sm_86 for an RTX 30 card, sm_89 for an RTX 40 card. nvcc splits the file: host code goes to the normal C++ compiler, device code becomes PTX (a virtual assembly) and then SASS (the real machine code of that GPU).</p>
{nb('01-first-cuda-kernel.ipynb', 'Notebook: your first CUDA kernels', 'Hello world from the GPU, vector add in CUDA C with error checks, then the same kernel in Python with Numba, timed against NumPy.')}
''', kw=['vector add', 'cudaMalloc', 'cudaMemcpy', 'execution configuration', 'error checking', 'nvcc', 'arch', 'PTX', 'SASS'])

K.lesson('hello', 'Hello world, asynchronous launches and unified memory', f'''
{cu('hello.cu', HELLO, {4: 'printf works inside a kernel. Output is buffered on the GPU and printed when the host synchronises.', 8: 'Two blocks of three threads: six lines of output.', 9: 'Kernel launches are asynchronous. Without this wait, main could return and the program end before the GPU prints anything.'}, out='Hello from block 0, thread 0\nHello from block 0, thread 1\nHello from block 0, thread 2\nHello from block 1, thread 0\nHello from block 1, thread 1\nHello from block 1, thread 2')}
{note('The order of the six lines is not guaranteed. Blocks may run in any order, so block 1 can print first. Never write code that depends on the order blocks run in.', 'warn')}
{cu('managed.cu', MANAGED, {11: 'cudaMallocManaged gives one pointer that works on both host and device. The driver moves pages to whichever side touches them (unified memory).', 12: 'The host fills the array directly, no cudaMemcpy.', 14: 'Now the wait is essential: the host may not read x until the kernel has finished.'}, title='beyond the lecture: unified memory', out='x[0] = 3.0')}
<p>Unified memory makes the first program shorter, but the copies still happen behind the scenes as page migrations. For speed, explicit copies or <code>cudaMemPrefetchAsync</code> are often better, because you control when the data moves.</p>
{deep('what the launch really does', '<p>The host puts a launch command into a queue (a stream) and returns. The GPU front end takes blocks from the grid and hands each block to an SM that has room. A block stays on its SM until all its threads finish, and the SM runs its threads warp by warp. Blocks are never guaranteed to run in a fixed order or at the same time, which is why blocks may not wait for each other inside a kernel.</p>')}
''', kw=['hello world', 'printf', 'cudaDeviceSynchronize', 'asynchronous launch', 'unified memory', 'cudaMallocManaged', 'block order'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>The CPU is the boss and the GPU is a big team in another building. The boss sends materials, gives the order, waits, and collects the result.</p>',
    '<p>Six steps: cudaMalloc, cudaMemcpy H2D, launch &lt;&lt;&lt;⌈n/B⌉, B&gt;&gt;&gt;, guard if (i &lt; n), cudaMemcpy D2H, cudaFree. Kernels are __global__ void. Check every call.</p>',
    '<p>Launches are asynchronous and ordered within a stream. cudaMemcpy on the default stream synchronises. Errors in a kernel appear at the next synchronising call, so debug builds call cudaDeviceSynchronize after each launch. nvcc compiles device code to PTX and SASS for the -arch you name.</p>',
    '<p>CUDA Graphs record a whole sequence of launches and copies once and replay it with one call, cutting launch overhead. Dynamic parallelism lets kernels launch kernels. Libraries such as cuBLAS, cuDNN and Thrust, and Python front ends like Numba, CuPy and Triton, generate the same kernels for you.</p>')}
{steps('Work it out: how many threads start? (lecture 3 slide 4)', [
    'Kernel1&lt;&lt;&lt;100, 256&gt;&gt;&gt;: 100 × 256 = 25,600 threads.',
    'Kernel2&lt;&lt;&lt;50, 1024&gt;&gt;&gt;: 50 × 1024 = 51,200 threads (the slide is right, 5120 said in class was a slip).',
    eq('Total threads = blocks × threads per block')])}
''', kw=['ladder', 'asynchronous', 'CUDA graphs', 'Numba', 'CuPy', 'Triton'])

K.quiz('e', 'Which qualifier marks a kernel launched from the host?', ['__device__', '__global__', '__shared__', '__host__'], 1,
       'Quiz 1 question 6.', '__global__ functions run on the device and are launched by the host.')
K.quiz('e', 'A kernel must return', ['int', 'float', 'void', 'any type'], 2,
       'Thousands of threads, one launch.', 'Results travel back through device memory, not a return value.')
K.quiz('e', 'cudaMalloc reserves memory', ['On the host', 'In the GPU\'s global memory', 'In shared memory', 'In registers'], 1,
       'Device allocation.', 'It returns a device pointer that only kernels may dereference.')
K.quiz('e', 'add&lt;&lt;&lt;200, 512&gt;&gt;&gt;() starts how many threads?', ['712', '102,400', '200', '512'], 1,
       'Blocks × threads.', '200 × 512 = 102,400.')
K.quiz('m', 'Why is the guard if (i &lt; n) needed?', ['To make it faster', 'The last block may have threads whose i is past the end of the array', 'CUDA needs an if', 'For warps'], 1,
       'Rounding up.', 'We launch ⌈n/B⌉ × B threads, which can exceed n.')
K.quiz('m', 'After a kernel launch the host', ['Waits until the kernel finishes', 'Continues immediately (launches are asynchronous)', 'Crashes', 'Copies data back automatically'], 1,
       'Asynchronous.', 'Only synchronising calls such as cudaMemcpy or cudaDeviceSynchronize wait.')
K.quiz('m', 'Which memory is visible to all SMs and lasts for the whole application? (Quiz 1 question 8)', ['L1 cache', 'Shared memory', 'Global memory', 'Registers'], 2,
       'cudaMalloc gives it.', 'Global memory lives in device DRAM and is visible to every thread of every kernel until freed.')
K.quiz('m', 'A __device__ function can be called from', ['The host only', 'Device code only', 'Anywhere', 'Python only'], 1,
       'Device helper.', 'It is a helper for kernels and other device functions.')
K.quiz('h', 'A kernel launch with 2000 threads per block silently does nothing. How do you find out?', ['It is impossible', 'Call cudaGetLastError right after the launch', 'Use printf on the host', 'Increase blocks'], 1,
       'Launches return no error.', 'The launch fails with an invalid configuration error, which cudaGetLastError reports. The limit is 1024 threads per block.')
K.quiz('h', 'The hello kernel with &lt;&lt;&lt;2, 3&gt;&gt;&gt; prints its six lines', ['Always block 0 first', 'In an order that is not guaranteed between blocks', 'In reverse', 'Only once'], 1,
       'Blocks are independent.', 'The hardware may schedule block 1 before block 0.')
K.quiz('x', 'nvcc -arch=sm_80 means', ['Use 80 threads', 'Generate code for compute capability 8.0 (A100)', 'Use 80 registers', 'Optimise level 80'], 1,
       'Compute capability.', 'sm_XY selects the GPU architecture the SASS is built for.')
K.quiz('x', 'Why is unified memory not always as fast as explicit copies?', ['It uses the CPU to compute', 'Pages migrate on first touch, causing faults and transfers at unplanned moments', 'It is not supported on GPUs', 'It disables caches'], 1,
       'Page migration.', 'Prefetching with cudaMemPrefetchAsync restores control over when data moves.')

K.calc('e', 'Kernel&lt;&lt;&lt;100, 256&gt;&gt;&gt;. Threads started?', '25600', 'Multiply.',
       ['Blocks 100.', 'Threads per block 256.', eq('100 × 256 = 25,600')], check=25600)
K.calc('e', 'n = 1,000,000 floats. Bytes for one array?', '4000000', 'sizeof(float) = 4.',
       ['Each float is 4 bytes.', 'n × 4.', eq('4,000,000 bytes')], check=4_000_000)
K.calc('e', 'n = 1,000,000 with 256 threads per block. Blocks?', '3907', '(n + 255) ÷ 256 whole number division.',
       ['1,000,000 ÷ 256 = 3906.25.', 'Round up.', eq('3907 blocks')], check=-(-1_000_000 // 256))
K.calc('m', 'Same launch. Idle threads in the last block?', '192', 'Launched − n.',
       ['Launched 3907 × 256 = 1,000,192.', 'Minus n = 1,000,000.', eq('192 idle threads')], check=3907 * 256 - 1_000_000)
K.calc('m', 'Vector add of 1,000,000 floats copies a and b in and c out. Total bytes over PCIe?', '12000000', 'Three arrays of 4 MB.',
       ['Two inputs: 8,000,000 bytes.', 'One output: 4,000,000 bytes.', eq('12,000,000 bytes')], check=12_000_000)
K.calc('m', 'Those 12 MB at 12 GB/s. Copy time in ms?', '1', 'bytes ÷ bandwidth.',
       ['12 × 10⁶ ÷ 12 × 10⁹ = 0.001 s.', 'Convert to ms.', eq('1 ms, about as long as the CPU needs to add them')], check=12e6 / 12e9 * 1000)
K.calc('m', 'Kernel2&lt;&lt;&lt;50, 1024&gt;&gt;&gt;. Warps started?', '1600', '1024 threads = 32 warps.',
       ['Threads 50 × 1024 = 51,200.', 'Warps = threads ÷ 32.', eq('51,200 ÷ 32 = 1600')], check=1600)
K.calc('h', 'Quiz 1 question 10: N = 2²⁰, blocks of 256. Blocks launched?', '4096', '(N + 255) ÷ 256.',
       ['N = 1,048,576.', '1,048,576 ÷ 256 = 4096 exactly.', eq('4096 blocks')], check=2 ** 20 // 256)
K.calc('h', 'Same launch. Warps launched?', '32768', '8 warps per block.',
       ['256 ÷ 32 = 8 warps per block.', '4096 × 8.', eq('32,768 warps')], check=4096 * 8)
K.calc('x', 'An int index i = blockIdx.x × blockDim.x + threadIdx.x overflows past 2³¹ − 1. With 1024 threads per block, from which blockIdx.x does it overflow?', '2097152', '2³¹ ÷ 1024.',
       ['int holds up to 2,147,483,647.', '2³¹ ÷ 1024 = 2,097,152.', eq('Block 2,097,152 would start at 2³¹ and overflow, use size_t or long long for huge arrays')], check=2 ** 31 // 1024)

K.assign('blocks', 'e', 'Blocks for a launch',
         '<p>Write <code>blocks_needed(n, threads)</code> using whole number arithmetic only.</p>',
         '''
def blocks_needed(n, threads):
    # your code here
    pass
''', [("blocks_needed(1000000, 256)", 3907), ("blocks_needed(1 << 20, 256)", 4096), ("blocks_needed(10, 4)", 3), ("blocks_needed(1, 1024)", 1)],
         '''
def blocks_needed(n, threads):
    return (n + threads - 1) // threads
''', '(n + B − 1) // B.', '<p>This is the same expression every CUDA program uses in its launch.</p>')
K.assign('simulate', 'm', 'Simulate a vector add launch',
         '<p>Write <code>launch_add(a, b, threads)</code> that simulates the CUDA kernel: compute the number of blocks, loop over every block and thread, compute i, apply the guard and fill c. Return c.</p>',
         '''
def launch_add(a, b, threads):
    n = len(a)
    c = [0] * n
    # your code here
    return c
''', [("launch_add([1, 2, 3], [10, 20, 30], 2)", [11, 22, 33]), ("launch_add(list(range(10)), [1] * 10, 4)", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), ("launch_add([5], [5], 32)", [10])],
         '''
def launch_add(a, b, threads):
    n = len(a)
    c = [0] * n
    blocks = (n + threads - 1) // threads
    for bx in range(blocks):
        for tx in range(threads):
            i = bx * threads + tx
            if i < n:
                c[i] = a[i] + b[i]
    return c
''', 'Without the guard, i reaches past the end of the list and Python raises IndexError, like an out of bounds write on the GPU.', '<p>The double loop is what the GPU runs in parallel.</p>')

K.must('Host and device', 'Host = CPU + RAM, device = GPU + its DRAM. Separate memories, so copy with cudaMemcpy (or use unified memory).')
K.must('Recipe', 'cudaMalloc, cudaMemcpy H2D, kernel&lt;&lt;&lt;blocks, threads&gt;&gt;&gt;, cudaMemcpy D2H, cudaFree. blocks = (n + B − 1) / B.')
K.must('Qualifiers', '__global__ void kernel (host launches), __device__ helper (device only), __host__ default. Kernels cannot return values.')
K.must('Guard', 'if (i &lt; n) because the last block can overhang the array.')
K.must('Asynchronous', 'Launch returns at once. cudaMemcpy and cudaDeviceSynchronize wait. Check errors with cudaGetLastError after a launch.')

T = K.topic(
    slug='first-cuda-program', topic='first-cuda-program', step=(2, 'The CUDA programming model', 'gpu-model', 'Write and launch kernels, index threads in 1, 2 and 3 dimensions, and see how warps and SMs run them and how many fit.', 'College'),
    title='Your first CUDA program', short='First CUDA program', badge='2.1', minutes=50,
    lead='Write, compile and run a complete CUDA program: allocate device memory, copy data, launch a kernel, copy back and check every call for errors.',
    desc='Host and device, the six step recipe, function qualifiers and why kernels return void, the complete vector addition program line by line, nvcc and compute capability, hello world from the GPU, asynchronous launches, error checking and unified memory.',
    summary='Host and device, the CUDA recipe, __global__ void kernels, vector add line by line, nvcc, asynchronous launches, error checks and unified memory.',
    keywords=['CUDA', 'kernel', '__global__', 'cudaMalloc', 'cudaMemcpy', 'vector add', 'nvcc', 'unified memory'],
    recap='<p>Every CUDA program allocates device memory, copies data in, launches a kernel over many threads, copies results back and frees the memory.</p>')
