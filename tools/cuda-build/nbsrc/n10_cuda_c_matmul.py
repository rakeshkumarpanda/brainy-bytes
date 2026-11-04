from notebooks import md, code

NB = {'file': '10-cuda-c-matmul-profiling.ipynb', 'title': 'CUDA C: tiled matmul, events, sanitizer and profilers',
      'intro': '''
This notebook goes with chapters 5.2 (tiled matmul), 8.3 (fast matmul) and 9.1 (debugging and profiling).
It is all CUDA C++. You will write one .cu file with a naive and a tiled kernel, time both with CUDA events, check
the answer against the CPU, then run it under compute-sanitizer, Nsight Systems and Nsight Compute.

It needs a real NVIDIA GPU with the CUDA toolkit, for example Google Colab with a T4 GPU.
''', 'cells': [
    code('''
!nvcc --version
!nvidia-smi --query-gpu=name,compute_cap --format=csv
''', {1: 'Shows the version of the CUDA compiler.',
      2: 'Shows the GPU name and its compute capability, which we pass to -arch below (7.5 means sm_75).'}),
    md('''
## 1. The program

The file has a CUDA_CHECK macro, the two kernels, a CPU reference, and a main that times each kernel with events.
'''),
    code('''
%%writefile matmul.cu
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <cuda_runtime.h>

#define CUDA_CHECK(call) do { cudaError_t e = (call); if (e != cudaSuccess) { \\
    printf("CUDA error %s at line %d\\n", cudaGetErrorString(e), __LINE__); exit(1); } } while (0)

constexpr int TILE = 16;

__global__ void mmNaive(const float* A, const float* B, float* C, int n) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    if (row < n && col < n) {
        float acc = 0.0f;
        for (int k = 0; k < n; k++) acc += A[row * n + k] * B[k * n + col];
        C[row * n + col] = acc;
    }
}

__global__ void mmTiled(const float* A, const float* B, float* C, int n) {
    __shared__ float sA[TILE][TILE];
    __shared__ float sB[TILE][TILE];
    int tx = threadIdx.x, ty = threadIdx.y;
    int row = blockIdx.y * TILE + ty, col = blockIdx.x * TILE + tx;
    float acc = 0.0f;
    for (int p = 0; p < (n + TILE - 1) / TILE; p++) {
        int ka = p * TILE + tx, kb = p * TILE + ty;
        sA[ty][tx] = (row < n && ka < n) ? A[row * n + ka] : 0.0f;
        sB[ty][tx] = (kb < n && col < n) ? B[kb * n + col] : 0.0f;
        __syncthreads();
        for (int k = 0; k < TILE; k++) acc += sA[ty][k] * sB[k][tx];
        __syncthreads();
    }
    if (row < n && col < n) C[row * n + col] = acc;
}

void mmCPU(const float* A, const float* B, float* C, int n) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            double acc = 0.0;
            for (int k = 0; k < n; k++) acc += (double)A[i * n + k] * B[k * n + j];
            C[i * n + j] = (float)acc;
        }
}

int main(int argc, char** argv) {
    int n = argc > 1 ? atoi(argv[1]) : 1024;
    size_t bytes = (size_t)n * n * sizeof(float);
    float *A = (float*)malloc(bytes), *B = (float*)malloc(bytes), *C = (float*)malloc(bytes), *R = (float*)malloc(bytes);
    for (int i = 0; i < n * n; i++) { A[i] = (rand() % 100) / 100.0f; B[i] = (rand() % 100) / 100.0f; }
    mmCPU(A, B, R, n);

    float *dA, *dB, *dC;
    CUDA_CHECK(cudaMalloc(&dA, bytes));
    CUDA_CHECK(cudaMalloc(&dB, bytes));
    CUDA_CHECK(cudaMalloc(&dC, bytes));
    CUDA_CHECK(cudaMemcpy(dA, A, bytes, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(dB, B, bytes, cudaMemcpyHostToDevice));

    dim3 block(TILE, TILE), grid((n + TILE - 1) / TILE, (n + TILE - 1) / TILE);
    cudaEvent_t start, stop;
    CUDA_CHECK(cudaEventCreate(&start));
    CUDA_CHECK(cudaEventCreate(&stop));

    for (int v = 0; v < 2; v++) {
        CUDA_CHECK(cudaMemset(dC, 0, bytes));
        CUDA_CHECK(cudaEventRecord(start));
        if (v == 0) mmNaive<<<grid, block>>>(dA, dB, dC, n);
        else mmTiled<<<grid, block>>>(dA, dB, dC, n);
        CUDA_CHECK(cudaGetLastError());
        CUDA_CHECK(cudaEventRecord(stop));
        CUDA_CHECK(cudaEventSynchronize(stop));
        float ms = 0.0f;
        CUDA_CHECK(cudaEventElapsedTime(&ms, start, stop));
        CUDA_CHECK(cudaMemcpy(C, dC, bytes, cudaMemcpyDeviceToHost));
        double maxErr = 0.0;
        for (int i = 0; i < n * n; i++) maxErr = fmax(maxErr, fabs(C[i] - R[i]));
        double gflops = 2.0 * n * n * n / (ms * 1e6);
        printf("%-6s n=%d  %.3f ms  %.1f GFLOP/s  max error %.2e\\n", v == 0 ? "naive" : "tiled", n, ms, gflops, maxErr);
    }

    cudaFree(dA); cudaFree(dB); cudaFree(dC);
    free(A); free(B); free(C); free(R);
    return 0;
}
''', {1: 'Save the rest of the cell as matmul.cu.',
      2: 'printf.',
      3: 'malloc, free, rand, atoi.',
      4: 'fabs and fmax for the error check.',
      5: 'The CUDA runtime API.',
      7: 'If a CUDA call fails, print the error name and the line, and stop.',
      8: 'Second half of the macro. do { } while (0) makes it one statement.',
      10: 'Tile width, known at compile time so the shared arrays can have a fixed size.',
      12: 'The naive kernel. const marks inputs that are only read.',
      13: 'Row of the output this thread computes, from the y part of the index.',
      14: 'Column, from the x part. Consecutive threads get consecutive columns, so B and C accesses coalesce.',
      15: 'Skip threads outside the matrix.',
      16: 'Accumulator in a register.',
      17: 'Dot product of row of A and column of B. Matrices are stored row by row: element (r, c) is at r × n + c.',
      18: 'Write the result once.',
      19: 'End of the if.',
      20: 'End of the kernel.',
      22: 'The tiled kernel.',
      23: 'Shared tile of A, one per block.',
      24: 'Shared tile of B.',
      25: 'Position of the thread inside the tile.',
      26: 'Output position. The same as in the naive kernel.',
      27: 'Accumulator.',
      28: 'One phase per tile along the shared dimension. Ceil covers a partial last tile.',
      29: 'Column of A and row of B this thread loads in this phase.',
      30: 'Load one value of A, or 0 outside the matrix.',
      31: 'Load one value of B, or 0 outside the matrix.',
      32: 'Wait until both tiles are fully loaded.',
      33: 'TILE multiply adds from shared memory.',
      34: 'Wait before the next phase overwrites the tiles.',
      35: 'End of the phase loop.',
      36: 'Write the result if this thread owns a real output.',
      37: 'End of the kernel.',
      39: 'CPU reference, so we know the right answer.',
      40: 'Every row.',
      41: 'Every column.',
      42: 'Sum in double for an accurate reference.',
      43: 'The dot product on the CPU.',
      44: 'Store it as float.',
      45: 'End of the column loop.',
      46: 'End of the function.',
      48: 'main can take the size from the command line, for example ./matmul 512.',
      49: 'Size n, 1024 by default.',
      50: 'Bytes per matrix. The cast to size_t avoids overflow for large n.',
      51: 'Host matrices: two inputs, the GPU result and the CPU reference.',
      52: 'Fill the inputs with values 0.00 to 0.99.',
      53: 'Compute the reference once. For n = 1024 this takes a few seconds on the CPU.',
      55: 'Device pointers.',
      56: 'GPU memory for A.',
      57: 'GPU memory for B.',
      58: 'GPU memory for C.',
      59: 'Copy A to the GPU.',
      60: 'Copy B to the GPU.',
      62: 'TILE × TILE threads per block and enough blocks to cover the n × n output.',
      63: 'Two events to time the kernels on the GPU.',
      64: 'Create the start event.',
      65: 'Create the stop event.',
      67: 'v = 0 runs the naive kernel, v = 1 the tiled one.',
      68: 'Clear C, so a kernel that writes nothing cannot pass the check by accident.',
      69: 'Time stamp before the kernel.',
      70: 'Launch the naive kernel.',
      71: 'Or the tiled kernel.',
      72: 'Catch launch errors such as a bad block size.',
      73: 'Time stamp after the kernel.',
      74: 'Wait until the GPU reaches the stop event.',
      75: 'A float for the time.',
      76: 'Time between the events in milliseconds.',
      77: 'Copy the result back.',
      78: 'Largest difference from the CPU answer.',
      79: 'Compare every element.',
      80: '2n³ FLOPs ÷ (ms × 1e6) = GFLOP/s.',
      81: 'One line per kernel with its time, speed and error. An error around 1e-4 is normal float rounding.',
      82: 'End of the loop.',
      84: 'Free GPU memory.',
      85: 'Free CPU memory.',
      86: 'Success.',
      87: 'End of main.'}),
    code('''
!nvcc -O3 -arch=sm_75 -lineinfo -o matmul matmul.cu
!./matmul 1024
''', {1: 'Compile for the T4 (sm_75). -lineinfo keeps source line numbers so the tools below can point at lines.',
      2: 'Run with n = 1024. The tiled kernel should be clearly faster than the naive one.'}),
    md('''
## 2. compute-sanitizer: find memory bugs

compute-sanitizer runs the program and checks every memory access. It is slow, so we use a small size.
Try it again after removing a bounds check from the kernels.
'''),
    code('''
!compute-sanitizer --tool memcheck ./matmul 100
''', {1: 'memcheck reports out of bounds and misaligned accesses with the kernel, thread and source line. n = 100 is not a multiple of 16, so the bounds checks are tested.'}),
    md('''
## 3. Nsight Systems: the timeline

nsys records every copy and kernel on a timeline. --stats=true prints a summary table, so we do not need the GUI.
'''),
    code('''
!nsys profile --stats=true -o matmul_report ./matmul 1024
''', {1: 'Profiles the whole run. Look at the CUDA GPU Kernel Summary table for the time of mmNaive and mmTiled, and the memory operations table for the copies.'}),
    md('''
## 4. Nsight Compute: inside one kernel

ncu measures one kernel in detail: achieved occupancy, memory throughput, and how busy the SMs are.
On some cloud machines it needs extra permissions and prints ERR_NVGPUCTRPERM. Then run it on your own machine instead.
'''),
    code('''
!ncu --kernel-name mmTiled --launch-count 1 --section SpeedOfLight --section Occupancy ./matmul 1024
''', {1: 'Profile only the first launch of mmTiled. SpeedOfLight shows compute and memory use as a percent of peak, Occupancy shows active warps against the limit.'}),
    md('''
## 5. Try these

1. Change TILE to 32 and recompile. Compare the time and the occupancy that ncu reports.
2. Pad sA to [TILE][TILE + 1]. Does it change the time? Use chapter 3.3 to explain.
3. Make each thread compute 2 outputs in the same column (a 2 × 1 register tile). Measure the GFLOP/s again.
'''),
]}
