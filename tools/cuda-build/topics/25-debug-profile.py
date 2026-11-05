# Chapter 9.1: Debugging and profiling CUDA code. Source: lecture 12 (slides 3 to 6: printf and compute-sanitizer,
# slides 11 to 16: cuda-gdb, slides 17 to 23: Visual Profiler, Nsight Systems, Nsight Compute and the example report),
# lecture 7 (slides 2 and 4: PTX and SASS), workbook 12.2. Correction from the notes: slide 6 says threads 0 to 21 write
# out of bounds, but all 32 do (indices 10 to 41). Beyond the lecture: a CUDA_CHECK macro, CUDA_LAUNCH_BLOCKING, the
# PTX on this page is real compiler output for the kernel shown.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu, sh, flow, nb

K = Kit()

CHECK = r'''
#include <cstdio>
#include <cstdlib>

#define CUDA_CHECK(call)                                                   \
    do {                                                                   \
        cudaError_t err = (call);                                          \
        if (err != cudaSuccess) {                                          \
            fprintf(stderr, "CUDA error %s at %s:%d\n",                    \
                    cudaGetErrorString(err), __FILE__, __LINE__);          \
            exit(1);                                                       \
        }                                                                  \
    } while (0)

__global__ void badAccess(int *data) {
    int i = threadIdx.x;
    data[i + 10] = i;                                 // writes data[10] to data[41]
    if (i < 2) printf("thread %d writes index %d\n", i, i + 10);
}

int main() {
    int *d;
    CUDA_CHECK(cudaMalloc(&d, 10 * sizeof(int)));     // valid indices 0 to 9 only
    badAccess<<<1, 32>>>(d);
    CUDA_CHECK(cudaGetLastError());                   // errors in the launch itself
    CUDA_CHECK(cudaDeviceSynchronize());              // errors while the kernel ran
    CUDA_CHECK(cudaFree(d));
    return 0;
}
'''

GDBBUG = r'''
#define N 64

__global__ void boundsBugAdd(const int *a, const int *b, int *c) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    c[x + 1] = a[x] + b[x];            // bug: writes one element too far
}

__global__ void boundsFixedAdd(const int *a, const int *b, int *c) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    if (x < N) c[x] = a[x] + b[x];     // fixed index and a guard
}
'''

VECADD = r'''
__global__ void vecAdd(const float *a, const float *b, float *c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) c[i] = a[i] + b[i];
}
'''

PTX = r'''
.visible .entry _Z6vecAddPKfS0_Pfi(
	.param .u64 _Z6vecAddPKfS0_Pfi_param_0,
	.param .u64 _Z6vecAddPKfS0_Pfi_param_1,
	.param .u64 _Z6vecAddPKfS0_Pfi_param_2,
	.param .u32 _Z6vecAddPKfS0_Pfi_param_3
)
{
	.reg .pred 	%p<2>;
	.reg .b32 	%r<6>;
	.reg .f32 	%f<4>;
	.reg .b64 	%rd<11>;

	ld.param.u32 	%r1, [_Z6vecAddPKfS0_Pfi_param_3];
	mov.u32 	%r2, %ctaid.x;
	mov.u32 	%r3, %ntid.x;
	mov.u32 	%r4, %tid.x;
	mad.lo.s32 	%r5, %r2, %r3, %r4;
	setp.ge.s32 	%p1, %r5, %r1;
	@%p1 bra 	$L__BB0_2;
	ld.param.u64 	%rd4, [_Z6vecAddPKfS0_Pfi_param_0];
	ld.param.u64 	%rd5, [_Z6vecAddPKfS0_Pfi_param_2];
	cvta.to.global.u64 	%rd6, %rd5;
	ld.param.u64 	%rd7, [_Z6vecAddPKfS0_Pfi_param_1];
	cvta.to.global.u64 	%rd8, %rd7;
	cvta.to.global.u64 	%rd9, %rd4;
	mul.wide.s32 	%rd10, %r5, 4;
	add.s64 	%rd1, %rd6, %rd10;
	add.s64 	%rd2, %rd8, %rd10;
	add.s64 	%rd3, %rd9, %rd10;
	ld.global.f32 	%f1, [%rd3];
	ld.global.f32 	%f2, [%rd2];
	add.f32 	%f3, %f1, %f2;
	st.global.f32 	[%rd1], %f3;
$L__BB0_2:
	ret;
}
'''

K.code('report', r'''
# Lecture 12 slide 22 and workbook 12.2: read the numbers of an Nsight Compute report
cycles, mhz, active = 10633, 880, 8132
print("duration from cycles:", round(cycles / mhz, 2), "us")
print("SMs active:", round(100 * active / cycles), "% of the time")
bw = 0.4292 * 320                      # GB/s, T4 peak 320
print("DRAM bandwidth used:", round(bw), "GB/s, bytes moved about", round(bw * 12.06e-6 * 1e9 / 1e6, 2), "MB")
print("launch overhead share:", round(100 * 5 / 12.06), "%")
unfused, fused = 8 * 12.06, 8 * (12.06 - 5) + 5
print("8 kernels fused, gain:", round(unfused / fused, 2), "times")
''')

K.lesson('workflow', 'A workflow for wrong or slow code', f'''
<p>GPU bugs are hard to see. Thousands of threads run at once, errors appear later than the line that caused them, and a wrong write often does not crash. Lecture 12 gives a fixed order of tools.</p>
{flow(('Check every call', 'Wrap each CUDA call in a check and call cudaGetLastError after each launch.'), ('Wrong result?', 'compute-sanitizer first, then printf on a few threads, then cuda-gdb.'), ('Slow?', 'Nsight Systems for the whole timeline, then Nsight Compute on the slowest kernel.'), ('Measure again', 'Change one thing and re-measure.'))}
{cu('bad_mem.cu', CHECK, {4: 'A macro so that every call reports the file and line where it failed.', 6: 'Every CUDA runtime call returns an error code.', 9: 'cudaGetErrorString turns the code into readable text.', 12: 'The do and while (0) wrapper makes the macro behave like one statement.', 16: 'The bug from lecture 12: thread i writes index i + 10.', 17: 'printf works inside kernels. Filter it, or thousands of threads flood the output.', 22: 'Only 10 ints are allocated.', 24: 'Catches errors in the launch itself, such as too many threads per block.', 25: 'Catches errors that happen while the kernel runs. Kernel errors show up only at a synchronising call.'})}
<p>Device printf output is buffered on the GPU and printed at the next synchronisation. The order between threads is not fixed. Setting <code>CUDA_LAUNCH_BLOCKING=1</code> makes every launch synchronous, so an error is reported at the launch that caused it.</p>
{note('This program usually runs without any message. The stray writes land in memory the program happens to own, so nothing crashes. That is exactly why out of bounds bugs are dangerous and why the sanitizer comes first.', 'warn')}
''', kw=['debugging', 'CUDA_CHECK', 'cudaGetLastError', 'cudaDeviceSynchronize', 'printf', 'CUDA_LAUNCH_BLOCKING', 'workflow'])

K.lesson('sanitizer', 'compute-sanitizer', f'''
<p><b>compute-sanitizer</b> runs your program and watches every memory access. It has four tools.</p>
{table(['Tool', 'Finds', 'Example in this course'], [
    ['memcheck (default)', 'out of bounds or misaligned accesses, bad frees, leaks', 'badAccess above'],
    ['racecheck', 'shared memory races (a missing __syncthreads)', 'unsafe_inc in chapter 7.2'],
    ['initcheck', 'reads of global memory that was never written', 'reading cudaMalloc memory before setting it'],
    ['synccheck', 'illegal barriers (a __syncthreads inside a divergent if)', 'the reduction in chapter 5.1']])}
{sh('Run the tools', '''
nvcc -g -lineinfo bad_mem.cu -o bad_mem
compute-sanitizer ./bad_mem
compute-sanitizer --tool racecheck ./unsafe_inc
compute-sanitizer --tool initcheck ./a.out
compute-sanitizer --tool synccheck ./reduce
compute-sanitizer --leak-check full ./a.out
''', out='''========= Invalid __global__ write of size 4 bytes
=========     at badAccess(int *) ... bad_mem.cu:16
=========     by thread (0,0,0) in block (0,0,0)
=========     Address ... is out of bounds
(one report per bad thread, shortened here)''', cap='What memcheck reports (shortened)')}
{viz('oob')}
{note('Slide 6 says threads 0 to 21 write out of bounds. Thread i writes data[i + 10], so even thread 0 writes data[10], one past the end. All 32 threads write out of bounds, to indices 10 to 41.', 'exam')}
''', kw=['compute-sanitizer', 'memcheck', 'racecheck', 'initcheck', 'synccheck', 'out of bounds', 'lineinfo'])

K.lesson('gdb', 'Stepping through a kernel with cuda-gdb', f'''
<p><b>cuda-gdb</b> is the GNU debugger extended to GPUs. You can stop inside a kernel, step line by line, print device variables, and switch the focus to any block, thread, warp or lane. Compile with <code>-g</code> (host) and <code>-G</code> (device). <code>-G</code> turns off most device optimisations, so debug builds are slow.</p>
{cu('bounds_bug.cu', GDBBUG, {4: 'x is the global thread index.', 5: 'The bug: c[x + 1]. The last thread writes one element past the end.', 10: 'The fix: write c[x] and guard with if (x < N), the standard pattern.'})}
{sh('The session from the slides', '''
nvcc -g -G bounds_bug.cu -o bounds_bug
cuda-gdb ./bounds_bug
(cuda-gdb) set cuda break_on_launch application
(cuda-gdb) run
(cuda-gdb) step
(cuda-gdb) p x
(cuda-gdb) cuda block (1,0,0) thread (31,0,0)
(cuda-gdb) step
(cuda-gdb) p x
(cuda-gdb) info cuda threads
''', out='''p x in block 0, thread 0 prints 0
p x in block 1, thread 31 prints 63 (1 × 32 + 31)''', cap='What the two prints show')}
{steps('Workbook 12.2: block 1, thread 31, blockDim 32', [
    'x = 1 × 32 + 31 = 63.',
    'The thread writes c[x + 1] = c[64].',
    'The arrays hold 64 elements: indices 0 to 63.',
    eq('Index 64 is out of bounds')])}
<p>Breakpoints can be set by line (<code>break 6</code>), by file and line, by kernel name (<code>break boundsBugAdd</code>) or on every launch. <code>info cuda warps</code> and <code>info cuda kernels</code> list what is running.</p>
''', kw=['cuda-gdb', 'breakpoint', 'step', 'focus', 'block thread', '-G', 'debug build'])

K.lesson('profile', 'Profiling with Nsight Systems and Nsight Compute', f'''
{table(['Tool', 'Shows', 'Use it'], [
    ['Nsight Systems (nsys)', 'the whole program timeline: CPU, API calls, copies, kernels per stream, NVTX ranges', 'first: which kernel or copy takes the time?'],
    ['Nsight Compute (ncu)', 'one kernel in depth: throughput, occupancy, traffic per memory level, stall reasons, roofline', 'second: why is that kernel slow?'],
    ['compute-sanitizer', 'correctness', 'for wrong results, not speed'],
    ['nvvp, nvprof', 'the old profilers', 'not supported on compute capability 8.0 and newer']])}
{sh('Profile from the command line (works on Colab)', '''
nsys profile --stats=true ./a.out
ncu --kernel-name matrixMul ./a.out
ncu --set full -o mm_report ./a.out
ncu --kernel-name matrixMul python matrix_mul.py
''')}
<p>The lecture reads one report line by line.</p>
{table(['Metric', 'Value', 'Meaning'], [
    ['SM frequency', '880 MHz', 'the profiler locks the clock to the base value'],
    ['Elapsed cycles', '10,633', '10,633 ÷ 880 MHz = 12.08 µs, matching the duration'],
    ['Duration', '12.06 µs', 'a tiny kernel: a launch costs about 5 µs'],
    ['Memory throughput', '44.35 %', 'the busiest memory unit at 44 % of its peak'],
    ['DRAM throughput', '42.92 %', 'of the T4\'s 320 GB/s'],
    ['SM active cycles', '8,132', '8132 ÷ 10,633 = 76 %: SMs idle a quarter of the time'],
    ['Compute (SM) throughput', '36.98 %', 'the busiest compute pipe at 37 %']])}
{viz('diagnose')}
{code('report')}
<p>Stall reasons in Warp State Statistics tell you what the warps wait for: <b>long scoreboard</b> (global memory), <b>barrier</b> (__syncthreads), <b>MIO throttle</b> (shared memory pressure), <b>not selected</b> (another warp was chosen, which is fine). Other tools: CUDA events for timing a region, NVTX to name code ranges in the timeline, nvidia-smi for overall use, power and temperature, and CUPTI, the API all of these are built on.</p>
{nb('10-cuda-c-matmul-profiling.ipynb', 'Notebook: CUDA C matmul and the profilers', 'One .cu file with naive and tiled kernels, events, compute-sanitizer, nsys and ncu.')}
''', kw=['Nsight Systems', 'Nsight Compute', 'nsys', 'ncu', 'latency bound', 'stall reasons', 'NVTX', 'nvidia-smi', 'launch overhead'])

K.lesson('ptx', 'Reading PTX and SASS', f'''
<p>nvcc compiles device code in two stages. <b>PTX</b> is a virtual assembly for an imaginary GPU with unlimited registers. It is readable and stable across generations. <b>SASS</b> is the real machine code of one GPU generation, produced from PTX by ptxas or by the driver at run time.</p>
{cu('vec_add.cu', VECADD, {2: 'The global index: blockIdx.x × blockDim.x + threadIdx.x.', 3: 'Guard, two loads, one add, one store.'})}
<p>Below is real PTX that a CUDA compiler (clang) produced for this kernel for sm_80. nvcc output looks very similar. Find each part of the C++ line in it.</p>
{cu('vec_add.ptx', PTX, {13: 'Load the parameter n.', 14: '%ctaid.x is blockIdx.x (CTA = cooperative thread array, the hardware name for a block).', 15: '%ntid.x is blockDim.x.', 16: '%tid.x is threadIdx.x.', 17: 'One multiply add builds the global index i.', 18: 'Set a predicate: is i ≥ n?', 19: 'If so, jump to the end. This is the if (i < n) guard.', 26: 'i × 4 bytes, widened to a 64 bit offset.', 30: 'Load a[i] from global memory.', 31: 'Load b[i].', 32: 'The one useful instruction: the add.', 33: 'Store c[i].'}, check=False, lang='ptx')}
{table(['SASS', 'Meaning'], [
    ['S2R R0, SR_CTAID.X', 'read a special register (blockIdx.x)'],
    ['IMAD', 'integer multiply add, for example the global index or an address'],
    ['LDG.E', 'load from global memory with a 64 bit address'],
    ['FADD, FFMA', 'float add, fused multiply add'],
    ['STG.E', 'store to global memory'],
    ['ISETP, @P0 BRA', 'compare into a predicate, then a branch taken only where the predicate holds']])}
{sh('See PTX and SASS yourself', '''
nvcc -ptx -arch=sm_75 mat_mul.cu
nvcc -cubin -arch=sm_75 mat_mul.cu
nvdisasm mat_mul.cubin
cuobjdump -sass ./mm
''')}
{note('Lecture 7 showed the PTX of the naive matmul: two ld.global loads for every mad. Global loads cost hundreds of cycles, the multiply add only a few. That is the case for tiling and shared memory, read straight from the compiler output.', 'tip')}
''', kw=['PTX', 'SASS', 'ptxas', 'nvdisasm', 'cuobjdump', 'ld.global', 'LDG', 'predicate', 'JIT'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A smoke alarm (CUDA_CHECK), a camera that watches every door (compute-sanitizer), a pause button (cuda-gdb) and a stopwatch with a map (Nsight).</p>',
    '<p>Check every call. memcheck, racecheck, initcheck, synccheck. cuda-gdb with -g -G. nsys for the timeline, ncu for one kernel. Under 60 % on both units means latency bound.</p>',
    '<p>Build with -lineinfo so Nsight Compute maps hot spots to source lines without -G. Use NVTX ranges. Compare against the roofline in ncu.</p>',
    '<p>CUPTI lets you build your own tools. Research profilers attribute stalls to source lines and suggest fixes. Performance regression tests run ncu metrics in continuous integration.</p>')}
''', kw=['ladder', 'lineinfo', 'NVTX', 'CUPTI'])

K.quiz('e', 'Which tool comes first when the result is wrong?', ['Nsight Systems', 'compute-sanitizer', 'nvidia-smi', 'nvprof'], 1, 'Correctness.', 'memcheck finds bad accesses.')
K.quiz('e', 'Kernel errors appear at', ['The kernel line', 'The next synchronising call', 'Compile time', 'Never'], 1, 'Launches are asynchronous.', 'Check after cudaDeviceSynchronize.')
K.quiz('e', 'racecheck finds', ['Out of bounds writes', 'Shared memory races', 'Memory leaks', 'Slow kernels'], 1, 'Shared memory.', 'Missing __syncthreads.')
K.quiz('e', 'Which profiler shows the whole program timeline?', ['Nsight Compute', 'Nsight Systems', 'cuda-gdb', 'initcheck'], 1, 'Systems.', 'Compute goes deep on one kernel.')
K.quiz('m', 'Thread i writes data[i + 10], 32 threads, 10 ints. How many bad writes?', ['10', '22', '32', '0'], 2, 'Thread 0 writes index 10.', 'All 32.')
K.quiz('m', 'cuda-gdb: block 1, thread 31, blockDim 32. x =', ['31', '32', '63', '64'], 2, '1 × 32 + 31.', '63.')
K.quiz('m', 'Compiling with -G', ['Speeds up the kernel', 'Adds device debug info and turns off most optimisations', 'Selects the GPU', 'Enables printf'], 1, 'Debug build.', 'Slow but steppable.')
K.quiz('m', 'Compute 37 %, memory 44 %. The kernel is', ['Compute bound', 'Memory bound', 'Latency bound', 'Perfect'], 2, 'Both under 60 %.', 'Warps mostly wait.')
K.quiz('h', 'In PTX, %ctaid.x is', ['threadIdx.x', 'blockIdx.x', 'blockDim.x', 'gridDim.x'], 1, 'CTA is a block.', 'Cooperative thread array id.')
K.quiz('h', 'Stall reason long scoreboard means warps wait for', ['A barrier', 'Global memory loads', 'Another warp', 'The CPU'], 1, 'Scoreboard tracks pending loads.', 'Memory latency.')
K.quiz('x', 'Why can an out of bounds write run silently without the sanitizer?', ['GPUs ignore writes', 'It lands in memory the program happens to own', 'The compiler removes it', 'printf hides it'], 1, 'No crash is not proof.', 'Corrupts other data quietly.')
K.quiz('x', 'Why does PTX matter if the GPU runs SASS?', ['It does not', 'The driver can compile PTX for GPUs that did not exist at build time', 'PTX is faster', 'SASS cannot be stored'], 1, 'Forward compatibility.', 'JIT from PTX.')

K.calc('e', '10,633 cycles at 880 MHz. Duration in µs? (two decimals)', '12.08', 'Divide.',
       ['10,633 ÷ 880 × 10⁶.', '= 1.208 × 10⁻⁵ s.', eq('12.08 µs')], check=round(10633 / 880, 2), tol=0.005)
K.calc('e', '1,000,000 cycles at 1.41 GHz. Time in µs? (nearest whole)', '709', 'Divide.',
       ['10⁶ ÷ 1.41 × 10⁹.', '= 7.09 × 10⁻⁴ s.', eq('≈ 709 µs')], check=round(1e6 / 1.41e9 * 1e6))
K.calc('e', 'Block 1, thread 31, blockDim 32. Global index x?', '63', 'blockIdx × blockDim + threadIdx.',
       ['1 × 32 = 32.', '+ 31.', eq('63')], check=63)
K.calc('m', 'SM active 8132 of 10,633 cycles. Percent? (nearest whole)', '76', 'Divide.',
       ['8132 ÷ 10,633 = 0.765.', '× 100.', eq('≈ 76 percent')], check=round(100 * 8132 / 10633))
K.calc('m', '42.92 % of 320 GB/s. Bandwidth in GB/s? (nearest whole)', '137', 'Multiply.',
       ['0.4292 × 320.', '= 137.3.', eq('≈ 137 GB/s')], check=round(0.4292 * 320))
K.calc('m', 'Bytes moved at 137.3 GB/s for 12.06 µs, in MB? (two decimals)', '1.66', 'Multiply.',
       ['137.3 × 10⁹ × 12.06 × 10⁻⁶.', '= 1.656 × 10⁶ bytes.', eq('≈ 1.66 MB')], check=round(0.4292 * 320e9 * 12.06e-6 / 1e6, 2), tol=0.01)
K.calc('m', '5 µs launch overhead in a 12.06 µs kernel. Percent? (nearest whole)', '41', 'Divide.',
       ['5 ÷ 12.06.', '= 0.415.', eq('≈ 41 percent')], check=round(100 * 5 / 12.06))
K.calc('h', '8 such kernels fused so the 5 µs is paid once. Speedup? (two decimals)', '1.57', 'Unfused ÷ fused.',
       ['Unfused 8 × 12.06 = 96.48 µs.', 'Fused 8 × 7.06 + 5 = 61.48 µs.', eq('≈ 1.57 times')], check=round(96.48 / 61.48, 2), tol=0.005)
K.calc('h', '32 threads write data[i + 10] into 10 ints. Highest index written?', '41', '31 + 10.',
       ['Thread 31 is the last.', '31 + 10.', eq('41')], check=41)
K.calc('x', 'Threads write c[x + 1] for x from 0 to 63 into 64 ints. How many bad writes?', '1', 'Only x = 63.',
       ['Indices written 1 to 64.', 'Only 64 is outside.', eq('1 bad write')], check=1)
K.calc('x', 'Kernel of 12.06 µs: how many such launches fit in one second if run back to back? (nearest thousand)', '83000', '1 ÷ 12.06 µs.',
       ['1 ÷ 12.06 × 10⁻⁶ = 82,919.', 'Round.', eq('≈ 83,000 launches, so overhead dominates tiny kernels')], check=83000, tol=500)

K.assign('oobcount', 'e', 'Count out of bounds writes',
         '<p>Write <code>bad_writes(threads, offset, n)</code>: thread i (0 ≤ i &lt; threads) writes index i + offset into an array of n elements. Return how many writes fall outside 0 to n − 1.</p>',
         '''
def bad_writes(threads, offset, n):
    # your code here
    pass
''', [("bad_writes(32, 10, 10)", 32), ("bad_writes(64, 1, 64)", 1), ("bad_writes(32, 0, 32)", 0), ("bad_writes(20, 5, 15)", 10)],
         '''
def bad_writes(threads, offset, n):
    count = 0
    for i in range(threads):
        if not (0 <= i + offset < n):
            count += 1
    return count
''', 'Loop over the threads and test each index.', '<p>The first test is lecture 12\'s badAccess, the second the cuda-gdb example.</p>')
K.assign('diagnose', 'm', 'Name the limit',
         '<p>Write <code>limit(compute, memory)</code> with throughputs in percent. Return "compute" if compute ≥ 60 and compute ≥ memory, "memory" if memory ≥ 60, and "latency" otherwise.</p>',
         '''
def limit(compute, memory):
    # your code here
    pass
''', [("limit(37, 44)", "latency"), ("limit(20, 88)", "memory"), ("limit(85, 40)", "compute"), ("limit(70, 90)", "memory")],
         '''
def limit(compute, memory):
    if compute >= 60 and compute >= memory:
        return "compute"
    if memory >= 60:
        return "memory"
    return "latency"
''', 'Test compute first, then memory.', '<p>The first test is the slide 22 report.</p>')

K.must('Order of tools', 'Check every call. Wrong: compute-sanitizer, printf, cuda-gdb. Slow: nsys, then ncu on the hot kernel.')
K.must('Sanitizer tools', 'memcheck (bounds), racecheck (shared memory races), initcheck (uninitialised reads), synccheck (bad barriers).')
K.must('cuda-gdb', 'Build with -g -G. set cuda break_on_launch application, cuda block (1,0,0) thread (31,0,0), p x.')
K.must('Reading a report', 'Time = cycles ÷ clock. SM active ÷ elapsed shows idle SMs. Both units under 60 percent: latency bound, read the stall reasons.')
K.must('PTX and SASS', 'PTX is virtual and portable (%ctaid.x, ld.global), SASS is the real code (S2R, LDG, FADD, STG). See them with nvcc -ptx, cuobjdump -sass.')

T = K.topic(
    slug='debug-profile', topic='debug-profile', step=(9, 'Tools and Python on the GPU', 'gpu-tools', 'Find bugs and bottlenecks with the CUDA tools, then write GPU code from Python.', 'College'),
    title='Debugging and profiling CUDA code', short='Debug and profile', badge='9.1', minutes=45,
    lead='Catch errors at the right line, find bad memory accesses with compute-sanitizer, step through a kernel with cuda-gdb, read an Nsight Compute report, and look inside PTX and SASS.',
    desc='A CUDA_CHECK macro and where kernel errors appear, device printf, the four compute-sanitizer tools with the slide 6 correction, a cuda-gdb session on an off by one bug, Nsight Systems against Nsight Compute, the lecture 12 report read line by line, latency bound kernels and stall reasons, and real PTX for vector add.',
    summary='Error checks, compute-sanitizer, cuda-gdb, Nsight, PTX and SASS.',
    keywords=['compute-sanitizer', 'cuda-gdb', 'Nsight Compute', 'Nsight Systems', 'PTX', 'SASS'],
    recap='<p>Check every call, let compute-sanitizer find bad accesses, step with cuda-gdb, then profile: nsys for the timeline, ncu for the slow kernel. Read PTX to see what the compiler did.</p>')
