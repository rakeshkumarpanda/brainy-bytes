# Chapter 9.2: GPU programming from Python. Source: lecture 4 (slide 12: just in time CUDA from Python, Numba, CuPy and
# PyCUDA, the Numba vector add), the L3 and L4 notes' Numba Sobel exercise, the L7 and L8 class answer on Python routes
# (CuPy, Numba, PyCUDA, Triton, PyTorch streams). Beyond the lecture: Numba shared memory, atomics and the CUDA
# simulator, CuPy ElementwiseKernel and RawKernel, Triton masks, PyTorch pinned memory and streams. The Numba listings
# were run in Numba's CUDA simulator. The CuPy, Triton and PyTorch listings follow the official documented APIs.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu, sh, nb

K = Kit()

NUMBA_ADD = r'''
from numba import cuda
import numpy as np

@cuda.jit
def add(a, b, c):
    i = cuda.grid(1)
    if i < c.size:
        c[i] = a[i] + b[i]

n = 1_000_000
a = np.arange(n, dtype=np.float32)
b = 2 * a
d_a, d_b = cuda.to_device(a), cuda.to_device(b)
d_c = cuda.device_array_like(a)
threads = 256
blocks = (n + threads - 1) // threads
add[blocks, threads](d_a, d_b, d_c)
c = d_c.copy_to_host()
print(c[:4])
'''

NUMBA_SUM = r'''
from numba import cuda, float32
import numpy as np

TPB = 256

@cuda.jit
def block_sum(x, out):
    s = cuda.shared.array(TPB, dtype=float32)
    t = cuda.threadIdx.x
    i = cuda.grid(1)
    s[t] = x[i] if i < x.size else 0.0
    cuda.syncthreads()
    stride = TPB // 2
    while stride > 0:
        if t < stride:
            s[t] += s[t + stride]
        cuda.syncthreads()
        stride //= 2
    if t == 0:
        cuda.atomic.add(out, 0, s[0])

n = 1000
d_x = cuda.to_device(np.ones(n, dtype=np.float32))
d_out = cuda.to_device(np.zeros(1, dtype=np.float32))
block_sum[(n + TPB - 1) // TPB, TPB](d_x, d_out)
print(d_out.copy_to_host()[0])
'''

CUPY = r'''
import cupy as cp

x = cp.arange(1_000_000, dtype=cp.float32)
y = 2 * x + 1
total = float(y.sum())

saxpy = cp.ElementwiseKernel(
    'float32 a, float32 x, float32 y', 'float32 z',
    'z = a * x + y', 'saxpy')
z = saxpy(cp.float32(2.0), x, y)

square = cp.RawKernel(r"""
extern "C" __global__ void square(const float *x, float *y, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = x[i] * x[i];
}""", 'square')
out = cp.empty_like(x)
square(((x.size + 255) // 256,), (256,), (x, out, cp.int32(x.size)))
host = cp.asnumpy(out)
'''

TRITON = r'''
import torch
import triton
import triton.language as tl

@triton.jit
def add_kernel(x_ptr, y_ptr, out_ptr, n, BLOCK: tl.constexpr):
    pid = tl.program_id(axis=0)
    offs = pid * BLOCK + tl.arange(0, BLOCK)
    mask = offs < n
    x = tl.load(x_ptr + offs, mask=mask)
    y = tl.load(y_ptr + offs, mask=mask)
    tl.store(out_ptr + offs, x + y, mask=mask)

x = torch.rand(98432, device='cuda')
y = torch.rand(98432, device='cuda')
out = torch.empty_like(x)
grid = (triton.cdiv(x.numel(), 1024),)
add_kernel[grid](x, y, out, x.numel(), BLOCK=1024)
'''

TORCH = r'''
import torch

x = torch.randn(4096, 4096).pin_memory()
s = torch.cuda.Stream()
with torch.cuda.stream(s):
    d = x.to('cuda', non_blocking=True)
    y = (d.half() @ d.half()).float()
torch.cuda.synchronize()
print(y.shape, y.dtype)
'''

K.code('gridmap', r'''
# What cuda.grid(1) returns, written out by hand for 10 elements in blocks of 4
n, threads = 10, 4
blocks = (n + threads - 1) // threads
for b in range(blocks):
    row = []
    for t in range(threads):
        i = b * threads + t                    # cuda.grid(1)
        row.append(str(i) if i < n else "-")   # "-" = the guard skips it
    print("block", b, ":", " ".join(row))
''')

K.lesson('routes', 'Five ways to reach the GPU from Python', f'''
<p>The course writes CUDA C++ because it shows threads, shared memory and streams directly. The same ideas are available from Python, at different levels.</p>
{table(['Library', 'You write', 'Good for'], [
    ['CuPy', 'NumPy style arrays on the GPU, plus element wise and raw CUDA kernels', 'speeding up NumPy code with almost no change'],
    ['Numba', 'kernels in Python with @cuda.jit, cuda.grid, shared arrays, atomics', 'learning CUDA from Python, custom kernels'],
    ['PyCUDA', 'CUDA C source strings, driver level control', 'full control from Python'],
    ['Triton', 'block level kernels, the compiler handles threads and tiling', 'fast custom deep learning kernels (used by PyTorch)'],
    ['PyTorch', 'tensors, torch.cuda streams, pinned memory', 'deep learning, and most real GPU work in Python']])}
<p>All of them compile <b>just in time</b>: the kernel is built at run time for the GPU that is actually present.</p>
''', kw=['Python', 'CuPy', 'Numba', 'PyCUDA', 'Triton', 'PyTorch', 'JIT'])

K.lesson('numba', 'Numba: CUDA kernels written in Python', f'''
<p>Every CUDA C idea has a Numba twin.</p>
{table(['CUDA C', 'Numba'], [
    ['__global__ void add(...)', '@cuda.jit above a Python function'],
    ['blockIdx.x * blockDim.x + threadIdx.x', 'cuda.grid(1)'],
    ['cudaMalloc + cudaMemcpy host to device', 'cuda.to_device(a)'],
    ['cudaMalloc only', 'cuda.device_array_like(a)'],
    ['add<<<blocks, threads>>>(...)', 'add[blocks, threads](...)'],
    ['cudaMemcpy device to host', 'd_c.copy_to_host()'],
    ['__shared__ float s[256]', 'cuda.shared.array(256, dtype=float32)'],
    ['__syncthreads()', 'cuda.syncthreads()'],
    ['atomicAdd(&out[0], v)', 'cuda.atomic.add(out, 0, v)']])}
{viz('launch1d')}
{code('gridmap')}
{cu('numba_add.py', NUMBA_ADD, {4: 'Compile this function for the GPU the first time it is called.', 6: 'The global index, the same as blockIdx.x × blockDim.x + threadIdx.x.', 7: 'The same guard as in CUDA C, because the last block may stick out.', 13: 'Copy to the GPU: cudaMalloc plus cudaMemcpy.', 14: 'Allocate on the GPU only, no copy.', 16: 'Ceiling division gives enough blocks.', 17: 'The launch: square brackets play the role of the triple angle brackets.', 18: 'Copy back. This waits for the kernel to finish.'}, check=False, lang='python', out='[0. 3. 6. 9.]')}
<p>Shared memory, barriers and atomics work the same way. This block sum is the reduction of chapter 5.1 in Python.</p>
{cu('numba_sum.py', NUMBA_SUM, {8: 'A shared array, one per block, sized at compile time.', 11: 'Threads past the end load 0, the identity for addition.', 12: 'Everyone must finish loading before anyone reads a neighbour.', 14: 'The tree: halve the stride each round.', 17: 'The barrier is outside the if, so every thread reaches it.', 20: 'One atomic per block adds the block total to the result.'}, check=False, lang='python', out='1000.0')}
{sh('Test without a GPU: Numba\'s CUDA simulator', '''
NUMBA_ENABLE_CUDASIM=1 python numba_sum.py
''', out='1000.0')}
{note('The simulator runs each GPU thread as a Python thread on the CPU. It is very slow but lets you test and debug kernels, including with print and pdb, on any laptop. The listings above were checked this way.', 'tip')}
{nb('01-first-cuda-kernel.ipynb', 'Notebook: your first CUDA kernels', 'Vector add in CUDA C and in Numba, with every line explained.')}
''', kw=['Numba', '@cuda.jit', 'cuda.grid', 'to_device', 'copy_to_host', 'shared array', 'syncthreads', 'atomic', 'simulator'])

K.lesson('cupy', 'CuPy: NumPy on the GPU', f'''
<p>CuPy arrays live in GPU memory and support most of NumPy. Each operation launches a ready made kernel. When you need something special, write it as an element wise expression or as raw CUDA C.</p>
{cu('cupy_demo.py', CUPY, {3: 'Created directly in GPU memory.', 4: 'Each operator launches an element wise kernel (two here: multiply, then add).', 5: 'The sum runs on the GPU. float() copies the single number back to the CPU.', 7: 'An element wise kernel from a one line C expression: inputs, output, body, name.', 12: 'Raw CUDA C, compiled at run time. The same kernel you would write in a .cu file.', 18: 'Launch with a grid tuple, a block tuple and the arguments.', 19: 'Copy the result back as a NumPy array.'}, check=False, lang='python')}
{note('Every separate operation reads and writes the whole array. 2 * x + 1 is two passes over memory. cp.fuse or an ElementwiseKernel does it in one pass, which matters because element wise work is memory bound.', 'tip')}
''', kw=['CuPy', 'ElementwiseKernel', 'RawKernel', 'asnumpy', 'kernel fusion', 'memory bound'])

K.lesson('triton', 'Triton: think in blocks', f'''
<p>In CUDA you write what one thread does. In <b>Triton</b> you write what one <b>program</b> does to a whole block of elements. The compiler maps the block to threads, vector loads and shared memory. PyTorch uses Triton to generate many of its fused kernels.</p>
{viz('triton')}
{cu('triton_add.py', TRITON, {5: 'Compile this as a Triton kernel. BLOCK is fixed at compile time.', 7: 'Which program this is, like blockIdx.x.', 8: 'BLOCK indices at once, as a vector.', 9: 'The guard, for the whole block in one line.', 10: 'A masked load: lanes past the end are not read.', 12: 'A masked store.', 17: 'Number of programs: the ceiling of n ÷ 1024.'}, check=False, lang='python')}
''', kw=['Triton', 'program_id', 'tl.arange', 'mask', 'tl.load', 'tl.store', 'block level'])

K.lesson('torch', 'PyTorch: streams, pinned memory and tensor cores', f'''
<p>The ideas of chapter 6.2 and 8.1 appear in PyTorch with friendlier names.</p>
{cu('torch_overlap.py', TORCH, {3: 'pin_memory puts the tensor in page locked host memory so the copy can run asynchronously.', 4: 'A CUDA stream: an in order queue on the GPU.', 5: 'Work inside this block goes into stream s.', 6: 'non_blocking=True returns at once, like cudaMemcpyAsync.', 7: 'An FP16 matmul runs on tensor cores, with FP32 accumulation inside.', 8: 'Wait for the GPU before using the result on the CPU.'}, check=False, lang='python')}
{table(['CUDA idea', 'PyTorch'], [
    ['cudaMallocHost', 'tensor.pin_memory()'],
    ['cudaMemcpyAsync', 'tensor.to("cuda", non_blocking=True)'],
    ['cudaStream_t', 'torch.cuda.Stream()'],
    ['cudaDeviceSynchronize', 'torch.cuda.synchronize()'],
    ['TF32 tensor cores', 'torch.backends.cuda.matmul.allow_tf32 = True'],
    ['custom kernel', 'torch.compile (generates Triton) or a C++ extension']])}
{viz('hostflow')}
''', kw=['PyTorch', 'pin_memory', 'non_blocking', 'torch.cuda.Stream', 'synchronize', 'allow_tf32', 'torch.compile'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>CuPy is like swapping a hand saw for a power saw with the same handle: NumPy code, GPU speed. Numba lets you build your own tool. Triton gives you a workshop that sets up the tools for you.</p>',
    '<p>Numba: @cuda.jit, cuda.grid(1), to_device, add[blocks, threads], copy_to_host, shared.array, syncthreads, atomic.add. Triton: program_id, arange, mask, load, store.</p>',
    '<p>Profile Python GPU code with nsys and ncu like any program. Watch for hidden copies between host and device, and for many tiny kernels: fuse them.</p>',
    '<p>torch.compile turns Python models into fused Triton kernels. JAX and XLA do the same from traced programs. Mojo and CUDA Python bring lower level control into Python syntax.</p>')}
''', kw=['ladder', 'torch.compile', 'JAX', 'XLA', 'fusion'])

K.quiz('e', 'In Numba, cuda.grid(1) equals', ['threadIdx.x', 'blockIdx.x', 'blockIdx.x × blockDim.x + threadIdx.x', 'gridDim.x'], 2, 'Global index.', 'One line instead of three.')
K.quiz('e', 'A Numba launch looks like', ['add<<<b, t>>>(...)', 'add[b, t](...)', 'add(b, t)', 'cuda.launch(add)'], 1, 'Square brackets.', 'Blocks first, then threads.')
K.quiz('e', 'CuPy is best described as', ['A debugger', 'NumPy compatible arrays on the GPU', 'A profiler', 'A compiler for C'], 1, 'cp.asarray.', 'Most NumPy calls work.')
K.quiz('e', 'cuda.to_device(a) does', ['Only cudaMalloc', 'cudaMalloc plus a copy to the GPU', 'A kernel launch', 'Frees memory'], 1, 'Allocate and copy.', 'device_array_like only allocates.')
K.quiz('m', 'Numba\'s __syncthreads() is', ['cuda.sync()', 'cuda.syncthreads()', 'numba.barrier()', 'There is none'], 1, 'Same name.', 'cuda.syncthreads().')
K.quiz('m', 'In Triton, the role of if (i < n) is played by', ['A try block', 'The mask passed to tl.load and tl.store', 'program_id', 'BLOCK'], 1, 'Vector guard.', 'mask = offs < n.')
K.quiz('m', 'n = 22, BLOCK = 8. Triton programs', ['2', '3', '8', '22'], 1, 'cdiv(22, 8).', '3, the last with 2 lanes masked.')
K.quiz('m', 'non_blocking=True in tensor.to("cuda") behaves like', ['cudaMemcpy', 'cudaMemcpyAsync', 'cudaMalloc', 'cudaFree'], 1, 'Returns at once.', 'Needs pinned memory to overlap.')
K.quiz('h', 'Why can 2 * x + 1 in CuPy be slower than one fused kernel?', ['It is not', 'Each operation reads and writes the whole array', 'It uses the CPU', 'It uses FP64'], 1, 'Memory passes.', 'Element wise work is memory bound.')
K.quiz('h', 'NUMBA_ENABLE_CUDASIM=1 lets you', ['Run faster', 'Run and debug CUDA kernels on the CPU without a GPU', 'Profile', 'Use tensor cores'], 1, 'Simulator.', 'Slow but works anywhere.')
K.quiz('x', 'Which Python route lets the compiler decide shared memory tiling for you?', ['Numba', 'PyCUDA', 'Triton', 'Raw CuPy kernels'], 2, 'Block level.', 'You write per block, it maps to threads.')
K.quiz('x', 'In the Numba block sum, why must cuda.syncthreads() sit outside the if?', ['Style', 'Every thread of the block must reach every barrier', 'Speed', 'Numba requires it for atomics'], 1, 'Barrier rule.', 'Same as CUDA C.')

K.calc('e', 'n = 1,000,000, 256 threads per block. Blocks?', '3907', 'Ceiling division.',
       ['1,000,000 + 255 = 1,000,255.', '÷ 256 = 3907.2, floor 3907.', eq('3907 blocks')], check=(1000000 + 255) // 256)
K.calc('e', 'Threads launched for those blocks?', '1000192', 'blocks × 256.',
       ['3907 × 256.', '= 1,000,192.', eq('1,000,192 threads, 192 skipped by the guard')], check=3907 * 256)
K.calc('e', 'Triton: n = 98,432, BLOCK = 1024. Programs?', '97', 'cdiv.',
       ['98,432 ÷ 1024 = 96.1.', 'Round up.', eq('97 programs')], check=-(-98432 // 1024))
K.calc('m', 'Lanes masked off in that case?', '896', '97 × 1024 − 98,432.',
       ['97 × 1024 = 99,328.', '− 98,432.', eq('896 lanes')], check=97 * 1024 - 98432)
K.calc('m', 'Numba block sum: n = 1000, TPB = 256. Global atomics?', '4', 'One per block.',
       ['Blocks ⌈1000 ÷ 256⌉ = 4.', 'One atomic each.', eq('4 atomics')], check=4)
K.calc('m', 'Tree steps for TPB = 256?', '8', 'log₂ 256.',
       ['Strides 128, 64, …, 1.', 'That is 8 rounds.', eq('8 steps')], check=8)
K.calc('m', 'y = 2 * x + 1 on 10⁶ float32 as two kernels. Bytes moved in MB? (read and write each pass)', '16', '2 passes × 8 bytes × 10⁶.',
       ['Pass 1 reads x, writes a temporary: 8 MB.', 'Pass 2 reads it, writes y: 8 MB.', eq('16 MB (a fused kernel moves 8)')], check=16)
K.calc('h', 'At 300 GB/s, time for those 16 MB in µs? (nearest whole)', '53', 'bytes ÷ bandwidth.',
       ['16 × 10⁶ ÷ 3 × 10¹¹.', '= 5.33 × 10⁻⁵ s.', eq('≈ 53 µs, 27 µs fused')], check=round(16e6 / 300e9 * 1e6))
K.calc('h', 'Pinned 4096 × 4096 float32 tensor. Size in MiB?', '64', '4096² × 4 bytes.',
       ['16,777,216 × 4 = 67,108,864 bytes.', '÷ 2²⁰.', eq('64 MiB')], check=64)
K.calc('x', 'Copying those 64 MiB at 12 GB/s. Time in ms? (one decimal)', '5.6', 'Divide.',
       ['67,108,864 ÷ 12 × 10⁹.', '= 5.59 × 10⁻³ s.', eq('≈ 5.6 ms')], check=round(67108864 / 12e9 * 1000, 1), tol=0.05)
K.calc('x', 'FP16 matmul of two 4096 × 4096 matrices at 65 TFLOP/s (T4 peak). Time in ms? (two decimals)', '2.11', '2n³ ÷ peak.',
       ['2 × 4096³ = 1.374 × 10¹¹.', '÷ 65 × 10¹².', eq('≈ 2.11 ms at best')], check=round(2 * 4096 ** 3 / 65e12 * 1000, 2), tol=0.005)

K.assign('gridmap', 'e', 'Write cuda.grid(1) by hand',
         '<p>Write <code>grid_ids(n, threads)</code>. Return the list of global indices that pass the guard i &lt; n, in launch order, for blocks of <code>threads</code> threads.</p>',
         '''
def grid_ids(n, threads):
    # your code here
    pass
''', [("grid_ids(5, 4)", [0, 1, 2, 3, 4]), ("len(grid_ids(1000, 256))", 1000), ("grid_ids(0, 32)", []), ("grid_ids(3, 1)", [0, 1, 2])],
         '''
def grid_ids(n, threads):
    blocks = (n + threads - 1) // threads
    out = []
    for b in range(blocks):
        for t in range(threads):
            i = b * threads + t
            if i < n:
                out.append(i)
    return out
''', 'Loop over blocks, then threads.', '<p>The extra threads of the last block are exactly the ones the guard removes.</p>')
K.assign('tritonmask', 'm', 'Triton offsets and mask',
         '<p>Write <code>program(pid, BLOCK, n)</code>. Return a list of the offsets that program pid touches with the mask true, as Triton computes them: offs = pid × BLOCK + 0 … BLOCK − 1, keep offs &lt; n.</p>',
         '''
def program(pid, BLOCK, n):
    # your code here
    pass
''', [("program(0, 4, 10)", [0, 1, 2, 3]), ("program(2, 4, 10)", [8, 9]), ("program(3, 4, 10)", []), ("len(program(96, 1024, 98432))", 128)],
         '''
def program(pid, BLOCK, n):
    offs = [pid * BLOCK + j for j in range(BLOCK)]
    return [o for o in offs if o < n]
''', 'Build the offsets, then filter with the mask.', '<p>The last test is the final program of the Triton add example: 98,432 − 96 × 1024 = 128 live lanes.</p>')

K.must('Routes', 'CuPy for NumPy code, Numba for kernels in Python, Triton for block level kernels, PyTorch for deep learning. All compile just in time.')
K.must('Numba twins', '@cuda.jit, cuda.grid(1), to_device, device_array_like, add[blocks, threads], copy_to_host, shared.array, syncthreads, atomic.add.')
K.must('Simulator', 'NUMBA_ENABLE_CUDASIM=1 runs kernels on the CPU for testing and debugging.')
K.must('CuPy', 'Each operation is a kernel and a full memory pass. Fuse with ElementwiseKernel or cp.fuse. RawKernel for CUDA C.')
K.must('Triton and PyTorch', 'Triton: program_id, offs, mask, tl.load and tl.store. PyTorch: pin_memory, non_blocking, Stream, synchronize.')

T = K.topic(
    slug='gpu-python', topic='gpu-python', step=(9, 'Tools and Python on the GPU', 'gpu-tools', 'Find bugs and bottlenecks with the CUDA tools, then write GPU code from Python.', 'College'),
    title='GPU programming from Python', short='GPU Python', badge='9.2', minutes=40,
    lead='Write the same kernels from Python: Numba with every CUDA idea one to one, CuPy for NumPy style arrays, Triton for block level kernels, and PyTorch for streams and tensor cores.',
    desc='The five Python routes and just in time compilation, Numba kernels with grid, copies, launches, shared memory, barriers and atomics, the CUDA simulator, CuPy element wise and raw kernels and the cost of separate passes, Triton programs and masks, and PyTorch pinned memory, streams and FP16 matmul.',
    summary='Numba, CuPy, Triton and PyTorch, mapped to CUDA C.',
    keywords=['Numba', 'CuPy', 'Triton', 'PyTorch', 'Python GPU', 'JIT'],
    recap='<p>Every CUDA idea has a Python twin. Numba mirrors CUDA C line by line, CuPy hides kernels behind NumPy, Triton lets you think in blocks, and PyTorch exposes streams and pinned memory.</p>')
