from notebooks import md, code

NB = {'file': '01-first-cuda-kernel.ipynb', 'title': 'Your first CUDA kernels',
      'intro': '''
This notebook goes with chapters 2.1 (first CUDA program) and 9.2 (Python on the GPU).
You will add two long lists of numbers on the GPU, first in Python with Numba, then in CUDA C with nvcc.

How to run it: open it in Google Colab, choose Runtime, Change runtime type, T4 GPU, then run the cells from top to bottom.
No GPU at hand? Set the environment variable NUMBA_ENABLE_CUDASIM=1 before the first import. Numba then runs the same
kernels on the CPU in a slow simulator, which is enough to learn the ideas. The CUDA C part needs a real GPU.
''', 'cells': [
    md('## 1. Check that a GPU is there'),
    code('''
!nvidia-smi
''', {1: 'Runs the NVIDIA tool in the shell (the ! sends the line to the shell). It prints the GPU name, its memory and the driver version. If it fails, the runtime has no GPU.'}),
    code('''
import os
import math
import time
import numpy as np
from numba import cuda

SIM = os.environ.get("NUMBA_ENABLE_CUDASIM") == "1"
N = 1_000 if SIM else 10_000_000
print("simulator" if SIM else cuda.get_current_device().name, "| N =", N)
''', {1: 'os lets us read environment variables, which tell us if the simulator is on.',
      2: 'math gives ceil, which we use to work out how many blocks we need.',
      3: 'time lets us measure how long things take on the CPU.',
      4: 'NumPy holds the arrays on the CPU side. Numba works directly with NumPy arrays.',
      5: 'cuda is the part of Numba that compiles Python functions into GPU kernels.',
      7: 'True when the simulator is on. The simulator is slow, so we use a small problem there.',
      8: 'Ten million numbers on a real GPU, one thousand in the simulator.',
      9: 'Prints which device we are on, so you know what the timings below mean.'}),
    md('''
## 2. The kernel

A kernel is a function that every GPU thread runs. Each thread works out its own global index and handles one element.
This is the same formula as in chapter 2.2: global index = blockIdx.x × blockDim.x + threadIdx.x.
'''),
    code('''
@cuda.jit
def vec_add(a, b, c):
    i = cuda.grid(1)
    if i < c.size:
        c[i] = a[i] + b[i]
''', {1: 'Tells Numba to compile the next function for the GPU. It becomes a kernel, like __global__ in CUDA C.',
      2: 'The kernel takes three arrays. A kernel never returns a value, it writes its result into an array.',
      3: 'cuda.grid(1) is the global index of this thread, blockIdx.x * blockDim.x + threadIdx.x, in one call.',
      4: 'The bounds check. We launch whole blocks, so some threads in the last block have no element. They must do nothing.',
      5: 'The real work: one addition per thread. Thread i touches only element i, so no two threads clash.'}),
    md('## 3. Copy, launch, copy back'),
    code('''
a = np.random.rand(N).astype(np.float32)
b = np.random.rand(N).astype(np.float32)
d_a = cuda.to_device(a)
d_b = cuda.to_device(b)
d_c = cuda.device_array_like(a)

threads = 256
blocks = math.ceil(N / threads)
vec_add[blocks, threads](d_a, d_b, d_c)
c = d_c.copy_to_host()

print("blocks:", blocks, "threads per block:", threads, "total threads:", blocks * threads)
print("correct:", np.allclose(c, a + b))
''', {1: 'N random numbers between 0 and 1. float32 because GPUs are fastest in 32 bit floats.',
      2: 'A second input list of the same size.',
      3: 'Copies a from CPU memory to GPU memory (cudaMalloc plus cudaMemcpy host to device in CUDA C).',
      4: 'Copies b to the GPU the same way.',
      5: 'Reserves GPU memory for the result with the same shape and type as a. Nothing is copied, the kernel fills it.',
      7: '256 threads per block, a multiple of the warp size 32 and a common safe choice.',
      8: 'Enough blocks to cover N. Ceil rounds up, so the last block may be partly empty, which the bounds check handles.',
      9: 'The launch. [blocks, threads] is Numba\'s way of writing <<<blocks, threads>>>.',
      10: 'Copies the result back to the CPU. This call also waits for the kernel to finish.',
      12: 'Shows the launch shape. Total threads is a little more than N because of rounding up.',
      13: 'Compares with NumPy on the CPU. allclose allows tiny rounding differences.'}),
    md('''
## 4. Time it honestly

The first launch also compiles the kernel, so we warm up once. A kernel launch returns at once, so we call
cuda.synchronize() before we stop the clock. Otherwise we would time only the launch, not the work.
'''),
    code('''
vec_add[blocks, threads](d_a, d_b, d_c)
cuda.synchronize()
t0 = time.perf_counter()
for _ in range(10):
    vec_add[blocks, threads](d_a, d_b, d_c)
cuda.synchronize()
gpu_ms = (time.perf_counter() - t0) / 10 * 1000

t0 = time.perf_counter()
c_cpu = a + b
cpu_ms = (time.perf_counter() - t0) * 1000

gb = 3 * N * 4 / 1e9
print(f"GPU kernel {gpu_ms:.3f} ms, about {gb / (gpu_ms / 1000):.0f} GB/s")
print(f"NumPy on CPU {cpu_ms:.3f} ms")
''', {1: 'Warm up launch. The first call compiles the kernel, which we do not want to time.',
      2: 'Waits until the GPU is idle, so the clock starts from a clean state.',
      3: 'Start time, from a clock with sub microsecond precision.',
      4: 'Ten launches, so one slow run does not decide the result.',
      5: 'The same launch as before. Launches return before the GPU finishes.',
      6: 'Waits for all ten kernels. Without it we would time only the launches.',
      7: 'Average time per launch in milliseconds.',
      9: 'Start time for the CPU version.',
      10: 'NumPy adds the two lists on the CPU.',
      11: 'CPU time in milliseconds.',
      13: 'Bytes moved per launch: read a and b, write c, 4 bytes each, in gigabytes.',
      14: 'Effective bandwidth = bytes ÷ time. Vector add does almost no maths, so this number is what limits it (chapter 4.2).',
      15: 'The CPU time, for comparison. Note it does not include copies to the GPU, which we did once at the start.'}),
    md('''
## 5. The grid stride loop

A grid stride loop lets a fixed number of threads cover any N. Each thread starts at its index and jumps by the total
number of threads in the grid. This is the pattern from chapter 2.2.
'''),
    code('''
@cuda.jit
def vec_add_stride(a, b, c):
    start = cuda.grid(1)
    stride = cuda.gridsize(1)
    for i in range(start, c.size, stride):
        c[i] = a[i] + b[i]

vec_add_stride[32, 128](d_a, d_b, d_c)
print("stride version correct:", np.allclose(d_c.copy_to_host(), a + b))
''', {1: 'Compile the next function as a kernel.',
      2: 'Same inputs and output as before.',
      3: 'This thread\'s global index, where it starts.',
      4: 'gridsize(1) is blocks × threads per block, the number of threads in the whole grid.',
      5: 'Visit start, start + stride, start + 2 × stride and so on until the end. The loop condition is the bounds check.',
      6: 'Same work as before, now done several times per thread.',
      8: 'Only 32 × 128 = 4096 threads, far fewer than N, and the loop still covers everything.',
      9: 'Check the result against NumPy.'}),
    md('''
## 6. The same program in CUDA C

The cell below writes a file with %%writefile. The next cell compiles it with nvcc and runs it.
CUDA_CHECK stops the program with a clear message when a CUDA call fails (chapter 9.1).
'''),
    code('''
%%writefile vec_add.cu
#include <cstdio>
#include <cstdlib>
#include <cuda_runtime.h>

#define CUDA_CHECK(call) do { cudaError_t e = (call); if (e != cudaSuccess) { \\
    printf("CUDA error %s at %s:%d\\n", cudaGetErrorString(e), __FILE__, __LINE__); exit(1); } } while (0)

__global__ void vecAdd(const float* a, const float* b, float* c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) c[i] = a[i] + b[i];
}

int main() {
    const int n = 1 << 20;
    size_t bytes = n * sizeof(float);
    float *a = (float*)malloc(bytes), *b = (float*)malloc(bytes), *c = (float*)malloc(bytes);
    for (int i = 0; i < n; i++) { a[i] = 1.0f; b[i] = 2.0f; }

    float *da, *db, *dc;
    CUDA_CHECK(cudaMalloc(&da, bytes));
    CUDA_CHECK(cudaMalloc(&db, bytes));
    CUDA_CHECK(cudaMalloc(&dc, bytes));
    CUDA_CHECK(cudaMemcpy(da, a, bytes, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(db, b, bytes, cudaMemcpyHostToDevice));

    int threads = 256, blocks = (n + threads - 1) / threads;
    vecAdd<<<blocks, threads>>>(da, db, dc, n);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaMemcpy(c, dc, bytes, cudaMemcpyDeviceToHost));

    printf("c[0] = %.1f, c[n-1] = %.1f\\n", c[0], c[n - 1]);
    cudaFree(da); cudaFree(db); cudaFree(dc);
    free(a); free(b); free(c);
    return 0;
}
''', {1: 'A notebook command that saves the rest of the cell to the file vec_add.cu instead of running it as Python.',
      2: 'printf, for printing from the host.',
      3: 'malloc, free and exit.',
      4: 'The CUDA runtime API: cudaMalloc, cudaMemcpy and friends. nvcc adds it on its own, we write it to be clear.',
      6: 'A macro that runs a CUDA call and, if it did not return cudaSuccess, prints the error with the file and line.',
      7: 'The second half of the macro. do { } while (0) makes the macro behave like one statement after an if.',
      9: '__global__ marks a kernel: it runs on the GPU and is launched from the CPU. const says the inputs are only read.',
      10: 'The global index of this thread, the same formula that cuda.grid(1) computes in Numba.',
      11: 'Bounds check and the addition, one element per thread.',
      12: 'End of the kernel.',
      14: 'The host program starts here.',
      15: 'n = 2 to the power 20 = 1,048,576 elements.',
      16: 'The size of one array in bytes. size_t is used for sizes because it can hold large values.',
      17: 'Host (CPU) arrays for the two inputs and the output.',
      18: 'Fill the inputs, so every answer should be 3.0.',
      20: 'Pointers that will point into GPU memory.',
      21: 'Reserve GPU memory for a. We pass the address of the pointer so cudaMalloc can fill it in.',
      22: 'Reserve GPU memory for b.',
      23: 'Reserve GPU memory for the result.',
      24: 'Copy a from the CPU to the GPU.',
      25: 'Copy b from the CPU to the GPU.',
      27: '256 threads per block and the rounded up number of blocks. (n + 255) / 256 is ceil in integer maths.',
      28: 'The launch: blocks × threads copies of vecAdd run on the GPU.',
      29: 'A launch returns no error code, so we ask for the last error. This catches a bad launch shape.',
      30: 'Copy the result back. This call waits for the kernel to finish first.',
      32: 'Print the first and last element. Both should be 3.0.',
      33: 'Give the GPU memory back.',
      34: 'Give the CPU memory back.',
      35: 'Return 0 to the shell to say all went well.',
      36: 'End of main.'}),
    code('''
!nvcc -O2 -arch=sm_75 -o vec_add vec_add.cu
!./vec_add
''', {1: 'Compile with nvcc. -arch=sm_75 builds for the T4 GPU in Colab (compute capability 7.5). Use sm_80 for an A100.',
      2: 'Run the program. It should print c[0] = 3.0, c[n-1] = 3.0.'}),
    md('''
## 7. Try these

1. Remove the bounds check in the Numba kernel and set N to a value that is not a multiple of 256. On a real GPU run it under compute-sanitizer to see the out of bounds write (chapter 9.1).
2. Change threads to 32, 64, 128, 512 and 1024 and time each. Explain the result with occupancy (chapter 2.4).
3. Write a kernel for c = 2a + b (SAXPY). Work out its bytes and its FLOPs, then its arithmetic intensity.
'''),
]}
