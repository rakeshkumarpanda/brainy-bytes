# Chapter 6.2: Streams, asynchrony and overlap. Source: lecture 4 (slide 11: asynchronous launches, cudaMemcpy
# against cudaMemcpyAsync, the correction about what asynchrony really risks, the two stream Sobel project with pinned
# buffers), lecture 6 (streams and the pipeline speedup), workbook 6.3.
# Beyond the lecture: events for timing and for dependencies between streams, the legacy default stream, and CUDA
# graphs for many small launches.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu, nb

K = Kit()

STREAMS = r'''
#include <cstdio>
#define NS 4

__global__ void scale(float *d, int n, float a) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) d[i] *= a;
}

int main() {
    const int N = 1 << 22, chunk = N / NS;
    const size_t cbytes = chunk * sizeof(float);
    float *h, *d;
    cudaMallocHost(&h, N * sizeof(float));          // pinned: needed for async copies
    cudaMalloc(&d, N * sizeof(float));
    for (int i = 0; i < N; ++i) h[i] = 1.0f;

    cudaStream_t s[NS];
    for (int k = 0; k < NS; ++k) cudaStreamCreate(&s[k]);

    for (int k = 0; k < NS; ++k) {
        int off = k * chunk;
        cudaMemcpyAsync(d + off, h + off, cbytes, cudaMemcpyHostToDevice, s[k]);
        scale<<<(chunk + 255) / 256, 256, 0, s[k]>>>(d + off, chunk, 2.0f);
        cudaMemcpyAsync(h + off, d + off, cbytes, cudaMemcpyDeviceToHost, s[k]);
    }
    cudaDeviceSynchronize();                          // wait for all streams before reading h
    printf("h[0] = %.1f, h[N-1] = %.1f\n", h[0], h[N - 1]);

    for (int k = 0; k < NS; ++k) cudaStreamDestroy(s[k]);
    cudaFreeHost(h); cudaFree(d);
    return 0;
}
'''

EVENTS = r'''
// Make stream b wait for work in stream a, without blocking the CPU
void dependent(cudaStream_t a, cudaStream_t b, float *x, float *y, int n) {
    cudaEvent_t done;
    cudaEventCreateWithFlags(&done, cudaEventDisableTiming);
    cudaMemcpyAsync(y, x, n * sizeof(float), cudaMemcpyDeviceToDevice, a);
    cudaEventRecord(done, a);              // marks the point in stream a
    cudaStreamWaitEvent(b, done, 0);       // later work in b starts only after that point
    cudaEventDestroy(done);
}
'''

K.code('pipe', r'''
# Pipeline speedup: N chunks through 3 stages (copy in, kernel, copy out)
def times(n, a, k, b):
    serial = n * (a + k + b)
    # one engine each way: each stage starts when its input and its unit are free
    h2d = comp = d2h = 0
    for _ in range(n):
        h2d += a
        comp = max(h2d, comp) + k
        d2h = max(comp, d2h) + b
    return serial, d2h, round(serial / d2h, 2)
print("equal, N=4 :", times(4, 1, 1, 1))
print("equal, N=16:", times(16, 1, 1, 1))
print("2, 5, 2 ms, N=10:", times(10, 2, 5, 2))
print("two input copies 174 us, kernel 10, out 87, N=4:", times(4, 174, 10, 87))
''')

K.lesson('async', 'Who waits for whom', f'''
<p>A kernel launch only puts work in a queue and returns at once. The CPU can do other things while the GPU runs. Some calls make the CPU wait.</p>
{table(['Call', 'Blocks the CPU?', 'Notes'], [
    ['kernel<<<g, b>>>()', 'no', 'queued in the default stream'],
    ['cudaMemcpy', 'yes', 'starts after earlier work in the stream, returns when the copy is done'],
    ['cudaMemcpyAsync', 'no', 'needs pinned host memory to really overlap'],
    ['cudaStreamSynchronize(s)', 'yes', 'until stream s is empty'],
    ['cudaDeviceSynchronize()', 'yes', 'until all GPU work is done']])}
<p>Work inside one <b>stream</b> runs in order. Work in different streams may run at the same time, on different engines: the copy engines move data over PCIe while the SMs run kernels.</p>
{note('In class it was said that asynchrony is dangerous because a second kernel could overwrite the first. Work in one stream always runs in order. The real danger is the CPU reading or reusing a host buffer before the GPU has finished with it. Synchronise before reading results.', 'warn')}
''', kw=['asynchronous', 'kernel launch', 'cudaMemcpy', 'cudaMemcpyAsync', 'synchronise', 'default stream'])

K.lesson('overlap', 'Overlapping copies and compute', f'''
<p>Split the data into chunks and give each chunk its own stream. While one chunk computes, the next can be copied in and the previous copied out.</p>
{viz('streams')}
{fxs(
    fx('Serial', 't = N × (t<sub>in</sub> + t<sub>kernel</sub> + t<sub>out</sub>)', 'One stream, nothing overlaps.', key=True),
    fx('Overlapped, equal stages t', 't = (N + 2) × t, speedup 3N ÷ (N + 2)', 'N = 4: 2 times. N = 16: 2.67. Never more than 3 (the number of stages).', key=True),
    fx('Unequal stages', 't ≈ fill + N × slowest stage', 'The slowest stage sets the pace. 2, 5, 2 ms with 10 chunks: 2 + 50 + 2 = 54 ms.'))}
{code('pipe')}
{cu('streams.cu', STREAMS, {13: 'Pinned memory: cudaMemcpyAsync from pageable memory would not overlap.', 18: 'Four independent queues.', 22: 'Each chunk is copied in, scaled and copied out in its own stream, so chunks can overlap.', 23: 'The fourth launch value names the stream.', 26: 'Wait for every stream before the CPU reads h.'}, out='h[0] = 2.0, h[N-1] = 2.0')}
{nb('07-streams-overlap.ipynb', 'Notebook: streams and overlap', 'Chunked copies and kernels on 4 streams, compared with the pipeline formula.')}
''', kw=['streams', 'overlap', 'pipeline', 'chunks', 'copy engines', 'speedup 3N/(N+2)'])

K.lesson('events', 'Events: timing and dependencies', f'''
<p>An <b>event</b> is a marker placed in a stream. It records when the GPU reached that point. Two events give an elapsed time. Another stream can wait for an event without stopping the CPU.</p>
{cu('events.cu', EVENTS, {4: 'DisableTiming makes a lighter event when it is only used for ordering.', 6: 'cudaEventRecord places the marker after the copy in stream a.', 7: 'Work queued in b after this call waits for the marker. The CPU continues straight away.'})}
{deep('CUDA graphs', '<p>Each launch costs a few microseconds of CPU time. For many small kernels, capture the sequence once into a CUDA graph and replay it with one call. The driver then knows all dependencies in advance.</p>')}
{steps('Workbook 6.3: 2²⁰ floats over 4 streams at 12 GB/s', [
    'Chunk = 2²⁰ ÷ 4 = 262,144 floats = 1 MiB.',
    'Blocks of 256: 262,144 ÷ 256 = 1024.',
    'Copy time 1,048,576 bytes ÷ 12 × 10⁹ B/s.',
    eq('≈ 87 µs per chunk copy')])}
''', kw=['events', 'cudaEventRecord', 'cudaStreamWaitEvent', 'timing', 'CUDA graphs'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A laundry with a washer, a dryer and a folding table. While load 2 washes, load 1 dries. Three machines working at once finish many loads almost 3 times faster.</p>',
    '<p>Streams are in order queues. Overlap needs pinned memory and separate streams. Equal stages: (N + 2)t, speedup ≤ 3. Synchronise before reading results.</p>',
    '<p>Check overlap in Nsight Systems: copies and kernels should appear on separate rows at the same time. Watch for implicit syncs from cudaMalloc, cudaFree or the legacy default stream.</p>',
    '<p>Large training jobs overlap gradient all reduce (NCCL) with the backward pass using streams. Programmatic dependent launch on Hopper starts the next kernel before the previous one fully ends.</p>')}
''', kw=['ladder', 'Nsight Systems', 'implicit sync', 'NCCL', 'overlap communication'])

K.quiz('e', 'A kernel launch', ['Blocks until the kernel ends', 'Returns at once, the work is queued', 'Copies data', 'Frees memory'], 1, 'Asynchronous.', 'The CPU continues.')
K.quiz('e', 'Work inside one stream runs', ['In any order', 'In order', 'Only on the CPU', 'Twice'], 1, 'Queue.', 'First in, first done.')
K.quiz('e', 'cudaMemcpyAsync needs which host memory to overlap', ['Pageable', 'Pinned', 'Shared', 'Constant'], 1, 'Page locked.', 'cudaMallocHost.')
K.quiz('m', '4 chunks, three equal stages. Speedup', ['1.5', '2', '3', '4'], 1, '12t ÷ 6t.', '2 times.')
K.quiz('m', '8 chunks, three equal stages. Speedup', ['2', '2.4', '2.67', '3'], 1, '24 ÷ 10.', '2.4.')
K.quiz('m', 'The real danger of asynchrony is', ['Kernels in one stream overwrite each other', 'The CPU reading results before the GPU is done', 'Copies get slower', 'There is none'], 1, 'Host side.', 'Synchronise first.')
K.quiz('m', 'Stages 2, 5 and 2 ms, 10 chunks. Overlapped time', ['54 ms', '90 ms', '50 ms', '30 ms'], 0, 'Kernel bound.', '2 + 10 × 5 + 2.')
K.quiz('h', 'The speedup with 3 equal stages can never pass', ['2', '3', 'N', 'N + 2'], 1, '3N ÷ (N + 2).', 'Tends to 3.')
K.quiz('h', 'cudaStreamWaitEvent(b, e) blocks', ['The CPU', 'Later work in stream b until e is reached', 'Every stream', 'Nothing'], 1, 'GPU side.', 'The CPU continues.')
K.quiz('h', 'Which call can silently synchronise the device and break overlap?', ['cudaMemcpyAsync', 'cudaMalloc or cudaFree in the loop', 'cudaEventRecord', 'A kernel launch'], 1, 'Allocation.', 'They may wait for all work.')
K.quiz('x', 'Chunks needed to reach 90 percent of the 3 times limit', ['9', '12', '18', '27'], 2, '3N ÷ (N + 2) ≥ 2.7.', 'N ≥ 18.')
K.quiz('x', 'Two input copies of 87 µs, kernel 10 µs, output 87 µs, 4 chunks, one engine each way. Streamed time', ['1084 µs', '793 µs', '696 µs', '361 µs'], 1, 'Input engine is the bottleneck.', '4 × 174 + 10 + 87 = 793.')

K.calc('e', 'N = 8 equal stages. Speedup? (one decimal)', '2.4', '3N ÷ (N + 2).',
       ['24 ÷ 10.', '= 2.4.', eq('2.4 times')], check=24 / 10)
K.calc('e', 'N = 1. Speedup?', '1', 'Nothing to overlap.',
       ['3 ÷ 3.', 'One chunk.', eq('1 (no gain)')], check=1)
K.calc('e', '2²⁰ floats over 4 streams. Floats per chunk?', '262144', '÷ 4.',
       ['1,048,576 ÷ 4.', '= 262,144.', eq('262,144 floats = 1 MiB')], check=262144)
K.calc('m', 'Stages 2, 5, 2 ms, 10 chunks. Serial time?', '90', 'N × sum.',
       ['2 + 5 + 2 = 9.', '× 10.', eq('90 ms (overlapped 54)')], check=90)
K.calc('m', 'Stages 2, 5, 2 ms, 10 chunks. Speedup? (two decimals)', '1.67', '90 ÷ 54.',
       ['Overlapped 2 + 50 + 2 = 54.', '90 ÷ 54.', eq('1.67')], check=round(90 / 54, 2), tol=0.005)
K.calc('m', '1 MiB at 12 GB/s. Copy time in µs? (nearest whole)', '87', 'bytes ÷ bandwidth.',
       ['1,048,576 ÷ 12 × 10⁹ = 8.74 × 10⁻⁵ s.', '= 87.4 µs.', eq('≈ 87 µs')], check=round(1048576 / 12e9 * 1e6))
K.calc('m', 'Blocks of 256 for 262,144 floats?', '1024', 'Divide.',
       ['262,144 ÷ 256.', '= 1024.', eq('1024 blocks')], check=1024)
K.calc('h', 'Serial time for 4 chunks: 2 × 87 in, 10 kernel, 87 out (µs)?', '1084', '4 × 271.',
       ['Per chunk 174 + 10 + 87 = 271.', '× 4.', eq('1084 µs')], check=4 * 271)
K.calc('h', 'Same, streamed with one engine each way (µs)?', '793', 'Input copies back to back.',
       ['Inputs end at 4 × 174 = 696.', 'Last kernel 696 to 706, last output 706 to 793.', eq('793 µs, about 1.37 times')], check=696 + 10 + 87)
K.calc('x', 'Smallest N with 3N ÷ (N + 2) ≥ 2.7?', '18', 'Solve.',
       ['3N ≥ 2.7N + 5.4.', '0.3N ≥ 5.4.', eq('N ≥ 18')], check=18)
K.calc('x', 'Equal stages of 3 ms, 6 chunks. Overlapped time in ms?', '24', '(N + 2) t.',
       ['N + 2 = 8.', '× 3 ms.', eq('24 ms against 54 serial')], check=24)

K.assign('pipeline', 'm', 'Pipeline timer',
         '<p>Write <code>overlapped(n, a, k, b)</code>: total time for n chunks through copy in (a), kernel (k) and copy out (b), one engine per stage, chunks in order. Each stage of a chunk starts when its previous stage is done and its engine is free.</p>',
         '''
def overlapped(n, a, k, b):
    # your code here
    pass
''', [("overlapped(4, 1, 1, 1)", 6), ("overlapped(10, 2, 5, 2)", 54), ("overlapped(4, 174, 10, 87)", 793), ("overlapped(1, 3, 4, 5)", 12)],
         '''
def overlapped(n, a, k, b):
    h2d = comp = d2h = 0
    for _ in range(n):
        h2d += a
        comp = max(h2d, comp) + k
        d2h = max(comp, d2h) + b
    return d2h
''', 'Track when each engine becomes free.', '<p>These are the workbook 6.3 answers.</p>')
K.assign('chunks', 'e', 'Chunks for a target speedup',
         '<p>Write <code>chunks_for(target)</code>: the smallest N with 3N ÷ (N + 2) ≥ target for three equal stages. Return -1 if the target is 3 or more.</p>',
         '''
def chunks_for(target):
    # your code here
    pass
''', [("chunks_for(2)", 4), ("chunks_for(2.7)", 18), ("chunks_for(3)", -1), ("chunks_for(1)", 1)],
         '''
def chunks_for(target):
    if target >= 3:
        return -1
    n = 1
    while 3 * n < target * (n + 2) - 1e-9:
        n += 1
    return n
''', 'Try N = 1, 2, … until it is reached.', '<p>3 can only be approached, never reached.</p>')

K.must('Async', 'Launches and cudaMemcpyAsync return at once. cudaMemcpy and the synchronise calls block the CPU.')
K.must('Streams', 'In order inside a stream, overlap across streams. Async copies need pinned memory.')
K.must('Pipeline', 'Equal stages: (N + 2)t, speedup 3N/(N + 2) < 3. Unequal: fill + N × slowest stage.')
K.must('Danger', 'Not kernels overwriting each other in one stream, but the CPU reading before the GPU is done.')
K.must('Events', 'cudaEventRecord marks a point. ElapsedTime for timing, StreamWaitEvent for cross stream order.')

T = K.topic(
    slug='streams', topic='streams', step=(6, 'Execution and overlap', 'gpu-exec', 'See how branches and warp schedulers decide the speed of a warp, and overlap copies with kernels using streams.', 'College'),
    title='Streams, asynchrony and overlap', short='Streams', badge='6.2', minutes=40,
    lead='Learn which CUDA calls make the CPU wait, split work into streams so copies and kernels run at the same time, and work out the speedup of a pipeline.',
    desc='Asynchronous launches, blocking and non blocking copies, the lecture 4 correction about asynchrony, streams and pinned memory, pipeline speedup 3N/(N + 2), unequal stages, events for timing and dependencies, and CUDA graphs.',
    summary='Async calls, streams, overlap speedup, pinned memory, events and graphs.',
    keywords=['streams', 'cudaMemcpyAsync', 'pinned memory', 'overlap', 'events', 'pipeline'],
    recap='<p>Streams are in order queues that may overlap each other. With pinned memory and chunks, copies hide behind kernels, up to the number of pipeline stages.</p>')
