# Chapter 4.2: FLOPs, bandwidth, arithmetic intensity and the roofline. Source: lecture 5 (slides 3 to 7: FLOP
# counting, computation against communication, bandwidth and arithmetic intensity, the roofline), lecture 4
# (benchmark numbers), workbook 3.4, 4.3, 4.4, 5.2, 5.3 and 5.4.
# Beyond the lecture: measuring achieved bandwidth with events, and the hierarchical roofline (L1, L2, DRAM roofs).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

BW = r'''
#include <cstdio>

__global__ void saxpy(int n, float a, const float *x, float *y) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = a * x[i] + y[i];          // 2 FLOPs, 12 bytes (read x, read y, write y)
}

int main() {
    const int n = 1 << 26;
    float *x, *y;
    cudaMalloc(&x, n * sizeof(float));
    cudaMalloc(&y, n * sizeof(float));
    cudaMemset(x, 0, n * sizeof(float));
    cudaMemset(y, 0, n * sizeof(float));
    cudaEvent_t t0, t1;
    cudaEventCreate(&t0); cudaEventCreate(&t1);
    cudaEventRecord(t0);
    saxpy<<<(n + 255) / 256, 256>>>(n, 2.0f, x, y);
    cudaEventRecord(t1);
    cudaEventSynchronize(t1);
    float ms = 0;
    cudaEventElapsedTime(&ms, t0, t1);
    double bytes = 12.0 * n, flops = 2.0 * n;
    printf("bandwidth %.1f GB/s, %.1f GFLOP/s, AI %.3f\n", bytes / ms / 1e6, flops / ms / 1e6, flops / bytes);
    cudaFree(x); cudaFree(y);
    return 0;
}
'''

K.code('roof', r'''
# Roofline: attainable = min(peak, AI x bandwidth)
gpus = {"Fermi": (1000, 144), "A100": (19500, 1555)}
kernels = {"SAXPY": 2 / 12, "naive matmul": 0.25, "tiled T=16": 4.0, "big GEMM": 50.0}
for g, (P, B) in gpus.items():
    print(g, "ridge", round(P / B, 2), "FLOP/byte")
    for k, ai in kernels.items():
        att = min(P, ai * B)
        kind = "memory" if ai < P / B else "compute"
        print(f"  {k:13s} AI {ai:6.3f}: {att:8.1f} GFLOP/s ({kind} bound)")
''')

K.code('flops', r'''
# FLOPs of common kernels
n = 1024
print("matmul n=1024:", 2 * n ** 3, "FLOPs")
print("5x5 filter, 1020x1020 outputs:", 2 * 25 * 1020 * 1020)
# A100 FP32 peak: 108 SMs x 64 cores x 2 FLOPs x 1.41 GHz
print("A100 peak GFLOP/s:", round(108 * 64 * 2 * 1.41, 1))
print("4096^3 matmul at peak (ms):", round(2 * 4096 ** 3 / 19.5e12 * 1000, 2))
''')

K.lesson('flops', 'Counting the work: FLOPs', f'''
<p>A <b>FLOP</b> is one floating point operation: an add, a multiply, or half of an FMA. FLOP/s (or FLOPS) is a rate. The lecture warned that slides mix the two, so always check the unit.</p>
{fxs(
    fx('Matrix multiply n × n', 'FLOPs = 2<i>n</i>³', 'Each of n² outputs needs n multiplies and n adds.', key=True),
    fx('Filter k × k', 'FLOPs = 2<i>k</i>² × outputs', 'A 5 × 5 filter on 1020 × 1020 outputs: 52,020,000.'),
    fx('Peak of a GPU', 'peak = SMs × cores per SM × 2 (FMA) × clock', 'A100: 108 × 64 × 2 × 1.41 GHz ≈ 19.5 TFLOP/s.', key=True),
    fx('Efficiency', 'achieved ÷ peak', 'A simple kernel at 3171 GFLOP/s on an H100 with about 51,000 is about 6.2 percent.'))}
{code('flops')}
{steps('Lecture 5: mul_add loop', ['x = a × x + b runs 50 times.', 'Each iteration is 2 FLOPs.', eq('100 FLOPs per call. In 1 second that is 100 FLOP/s')])}
''', kw=['FLOP', 'FLOP/s', 'FLOPs of matmul', 'peak', 'efficiency', 'FMA'])

K.lesson('ai', 'Bandwidth and arithmetic intensity', f'''
<p>Every kernel both computes and moves data. If data cannot arrive fast enough, the cores sit idle however fast they are. The lecture\'s latency numbers for a CPU make the point: register 1 cycle, L1 4, L2 14, L3 75, DRAM 200.</p>
{fxs(
    fx('Bandwidth', 'GB/s = (bytes read + bytes written) ÷ 10⁹ ÷ seconds', 'Count both directions.', key=True),
    fx('Arithmetic intensity', 'AI = FLOPs ÷ bytes moved to or from DRAM', 'Unit FLOP per byte.', key=True),
    fx('SAXPY', 'AI = 2 ÷ 12 ≈ 0.167', 'Read x, read y, write y (3 × 4 bytes) for one multiply and one add. DAXPY is half that.'),
    fx('Matrix multiply', 'no reuse: 2 FLOPs per 2 loads → 0.25 (float), perfect reuse: AI = n ÷ 8 (float) or n ÷ 16 (double)', 'Reuse is what raises AI.'))}
{cu('saxpy_bw.cu', BW, {5: 'Each thread does 2 FLOPs and moves 12 bytes, so AI = 1/6 whatever the GPU.', 22: 'Events time the kernel alone on the GPU timeline.', 27: 'bytes ÷ ms ÷ 10⁶ gives GB/s. Compare it with the data sheet bandwidth to see how close you are.'}, out='(the printed bandwidth depends on the GPU, AI is always 0.167)')}
{table(['Kernel', 'FLOPs per element', 'Bytes per element (float)', 'AI'], [
    ['y = a·x', '1', '8', '0.125'], ['SAXPY y = a·x + y', '2', '12', '0.167'], ['dot product (double)', '2', '16', '0.125'], ['y = x³ + x', '3', '8', '0.375']])}
''', kw=['bandwidth', 'arithmetic intensity', 'SAXPY', 'DAXPY', 'reuse', 'bytes moved'])

K.lesson('roofline', 'The roofline model', f'''
{fxs(
    fx('Attainable speed', 'attainable = min(peak FLOP/s, AI × bandwidth)', 'The lower roof wins.', key=True),
    fx('Ridge point', 'AI<sub>ridge</sub> = peak ÷ bandwidth', 'Left of it a kernel is memory bound, right of it compute bound.', key=True),
    fx('Time', 't ≥ max(FLOPs ÷ peak, bytes ÷ bandwidth)', 'The shortest possible time is set by the slower of the two.'))}
{viz('roofline')}
{steps('Workbook 4.4: 10⁹ FLOPs and 2 × 10⁸ bytes on a 10 TFLOP/s, 500 GB/s GPU', [
    'Maths time 10⁹ ÷ 10¹³ = 0.1 ms.',
    'Memory time 2 × 10⁸ ÷ 5 × 10¹¹ = 0.4 ms.',
    'The memory time is longer, so the kernel takes at least 0.4 ms.',
    eq('Speed 10⁹ ÷ 0.4 ms = 2.5 TFLOP/s, memory bound (AI 5 is below the ridge 20)')])}
{code('roof')}
{note('For a memory bound kernel, doubling the maths units changes nothing. Only more bandwidth or more reuse helps. Doubling Fermi\'s cores gives plain matrix multiply no gain.', 'exam')}
''', kw=['roofline', 'ridge point', 'memory bound', 'compute bound', 'attainable performance'])

K.lesson('bench', 'Reading benchmark numbers (lecture 4 Sobel)', f'''
{table(['Picture', 'CPU (ms)', 'GPU kernel (ms)', 'Speedup'], [['Lena 512 × 512', '13.59', '0.188', 'about 72'], ['Kid', '47.27', '0.336', 'about 141']])}
{steps('8K frame (7680 × 4320, 1 byte per pixel): where does the time go?', [
    'Frame in and out: 2 × 33.2 MB = 66.4 MB. At 13 to 16 GB/s that takes about 4.1 to 5.1 ms.',
    'The kernel itself is 1.65 ms of the 8.66 ms total, about 19 percent.',
    'The kernel moves 66.4 MB in 1.65 ms = 40.2 GB/s, only 15.7 percent of the GPU\'s 256 GB/s.',
    eq('Keep frames on the GPU: about 606 FPS, 5.25 times faster')])}
{deep('hierarchical roofline', '<p>Nsight Compute draws one roof per memory level: L1, L2 and DRAM. A kernel can be far below the DRAM roof but at the L2 roof, which tells you that improving cache reuse, not DRAM traffic, is the next step.</p>')}
''', kw=['benchmark', 'Sobel', 'Lena', '8K', 'copy overhead', 'hierarchical roofline'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A kitchen with very fast cooks but a slow delivery van serves meals at the speed of the van. Only recipes that use each delivered ingredient many times keep the cooks busy.</p>',
    '<p>AI = FLOPs ÷ bytes. Ridge = peak ÷ bandwidth. Attainable = min(peak, AI × B). Below the ridge only bandwidth or reuse helps.</p>',
    '<p>Tiling raises AI by T (chapter 5.2). Fusing kernels removes the bytes of intermediate results. Lower precision halves bytes and raises tensor core peaks, which moves both roofs.</p>',
    '<p>Williams, Waterman and Patterson introduced the roofline in 2009. LLM decoding at batch 1 is deeply memory bound (AI near 1), which is why KV cache compression and speculative decoding matter.</p>')}
''', kw=['ladder', 'kernel fusion', 'Williams', 'LLM decoding'])

K.quiz('e', 'FLOPs to multiply two n × n matrices', ['n²', '2n²', '2n³', 'n³ ÷ 2'], 2, 'n² outputs × 2n.', '2n³.')
K.quiz('e', 'Arithmetic intensity is', ['FLOPs ÷ seconds', 'FLOPs ÷ bytes moved', 'Bytes ÷ seconds', 'Cores × clock'], 1, 'FLOP per byte.', 'Work per byte.')
K.quiz('e', 'The ridge point is', ['peak × bandwidth', 'peak ÷ bandwidth', 'bandwidth ÷ peak', 'AI × peak'], 1, 'Where the roofs meet.', 'peak ÷ bandwidth.')
K.quiz('m', 'AI of SAXPY in float', ['0.083', '0.125', '0.167', '0.25'], 2, '2 ÷ 12.', '≈ 0.167.')
K.quiz('m', 'A kernel left of the ridge is', ['Compute bound', 'Memory bound', 'Latency free', 'Always fast'], 1, 'Below the slope.', 'Bandwidth limits it.')
K.quiz('m', 'Ridge of a 14 TFLOP/s, 900 GB/s GPU', ['1.56', '15.6', '156', '0.064'], 1, '14,000 ÷ 900.', '≈ 15.6.')
K.quiz('m', 'Same GPU, kernel AI 2. Top speed', ['14 TFLOP/s', '1.8 TFLOP/s', '900 GFLOP/s', '28 TFLOP/s'], 1, '2 × 900.', '1800 GFLOP/s.')
K.quiz('h', 'P = 10 TFLOP/s, B = 1 TB/s, AI = 5. Which helps more?', ['Double the maths units', 'Double the bandwidth', 'Both equal', 'Neither'], 1,
       'Ridge 10.', 'AI 5 is memory bound, so bandwidth doubles the speed.')
K.quiz('h', 'Plain matmul (AI 0.25) on an A100 reaches about', ['19.5 TFLOP/s', '389 GFLOP/s', '1555 GFLOP/s', '50 GFLOP/s'], 1, '0.25 × 1555.', '≈ 389, 50 times below peak.')
K.quiz('h', 'Matmul AI with perfect reuse in double', ['n ÷ 4', 'n ÷ 8', 'n ÷ 16', '0.125'], 2, 'The lecture counts 4 matrix transfers of 8n² bytes each.', 'The lecture counts 4 matrix transfers: AI = 2n³ ÷ (4 × 8n²) = n ÷ 16.')
K.quiz('x', 'With AI = n ÷ 8, matmul passes a ridge of 6.94 from n =', ['7', '56', '64', '128'], 1, 'n ÷ 8 ≥ 6.94.', 'n ≥ 55.5, so 56.')
K.quiz('x', 'An AI 1 kernel reaches 800 GFLOP/s on a 1 TB/s GPU. Share of its roof?', ['8 percent', '80 percent', '100 percent', '125 percent'], 1, 'Roof = 1 × 1000.', '800 ÷ 1000.')

K.calc('e', 'FLOPs to multiply two 1024 × 1024 matrices?', '2147483648', '2n³.',
       ['n³ = 1,073,741,824.', '× 2.', eq('2,147,483,648')], check=2 * 1024 ** 3)
K.calc('e', 'Ridge of a 14 TFLOP/s, 900 GB/s GPU (one decimal)?', '15.6', 'Divide.',
       ['14,000 GFLOP/s ÷ 900 GB/s.', '= 15.56.', eq('≈ 15.6 FLOP/byte')], check=14000 / 900, tol=0.05)
K.calc('e', 'A kernel reads 400 MB and writes 200 MB in 2 ms. Bandwidth in GB/s?', '300', 'Count both.',
       ['600 MB total.', '600 MB ÷ 2 ms.', eq('300 GB/s')], check=600e6 / 2e-3 / 1e9)
K.calc('m', 'A100: 108 SMs × 64 cores × 2 × 1.41 GHz. Peak in TFLOP/s? (one decimal)', '19.5', 'Multiply.',
       ['108 × 64 = 6912 cores.', '× 2 × 1.41 × 10⁹ = 1.949 × 10¹³.', eq('≈ 19.5 TFLOP/s')], check=108 * 64 * 2 * 1.41 / 1000, tol=0.05)
K.calc('m', 'Fastest time for a 4096³ matmul at 19.5 TFLOP/s in ms? (two decimals)', '7.05', '2n³ ÷ peak.',
       ['2 × 4096³ = 1.374 × 10¹¹.', '÷ 19.5 × 10¹².', eq('≈ 7.05 ms')], check=2 * 4096 ** 3 / 19.5e12 * 1000, tol=0.005)
K.calc('m', 'A100 19.5 TFLOP/s, 1555 GB/s. AI needed to be compute bound? (one decimal)', '12.5', 'Ridge.',
       ['19,500 ÷ 1555.', '= 12.54.', eq('≈ 12.5 FLOP/byte')], check=19500 / 1555, tol=0.05)
K.calc('m', 'SAXPY on 144 GB/s. GFLOP/s?', '24', 'AI × B.',
       ['AI = 1/6.', '144 ÷ 6.', eq('24 GFLOP/s')], check=144 / 6)
K.calc('h', '10⁹ FLOPs, 2 × 10⁸ bytes, 10 TFLOP/s, 500 GB/s. Shortest time in ms?', '0.4', 'Max of the two times.',
       ['Maths 0.1 ms.', 'Memory 0.4 ms.', eq('0.4 ms, memory bound')], check=max(1e9 / 10e12, 2e8 / 500e9) * 1000)
K.calc('h', 'Fermi ops per float fetched for peak (1000 GFLOP/s, 144 GB/s)? (nearest whole)', '28', 'Ridge × 4 bytes.',
       ['Ridge 1000 ÷ 144 = 6.94 FLOP/byte.', '× 4 bytes per float.', eq('≈ 28 operations per float')], check=1000 / 144 * 4, tol=0.5)
K.calc('h', 'Smallest tile T with AI = T ÷ 4 to reach 530 GFLOP/s on 177 GB/s?', '12', 'T ÷ 4 ≥ 530 ÷ 177.',
       ['Ridge 530 ÷ 177 = 2.99.', 'T ≥ 11.98.', eq('T = 12 (16 in practice, a power of two)')], check=12)
K.calc('x', '8K frame: 66.4 MB moved in 1.65 ms. Share of 256 GB/s in percent? (one decimal)', '15.7', 'Bandwidth first.',
       ['66.4 MB ÷ 1.65 ms = 40.24 GB/s.', '÷ 256.', eq('≈ 15.7 percent')], check=100 * 66.4e6 / 1.65e-3 / 1e9 / 256, tol=0.05)

K.assign('roofcalc', 'e', 'Roofline calculator',
         '<p>Write <code>roof(peak, bw, ai)</code> (GFLOP/s, GB/s, FLOP/byte). Return <code>[attainable, "memory"]</code> or <code>[attainable, "compute"]</code>, attainable rounded to 1 decimal. Exactly at the ridge counts as compute.</p>',
         '''
def roof(peak, bw, ai):
    # your code here
    pass
''', [("roof(14000, 900, 2)", [1800.0, "memory"]), ("roof(19500, 1555, 0.25)", [388.8, "memory"]), ("roof(1000, 144, 10)", [1000.0, "compute"])],
         '''
def roof(peak, bw, ai):
    att = min(peak, ai * bw)
    kind = 'memory' if ai < peak / bw else 'compute'
    return [round(float(att), 1), kind]
''', 'min of the two roofs.', '<p>The A100 case shows how far plain matrix multiply is from the peak.</p>')
K.assign('aicount', 'm', 'Arithmetic intensity of an element wise kernel',
         '<p>Write <code>ai(flops, reads, writes, size)</code>: FLOPs per element, number of arrays read and written per element, and the element size in bytes. Return the AI rounded to 3 decimals.</p>',
         '''
def ai(flops, reads, writes, size):
    # your code here
    pass
''', [("ai(2, 2, 1, 4)", 0.167), ("ai(2, 2, 1, 8)", 0.083), ("ai(1, 1, 1, 4)", 0.125), ("ai(3, 1, 1, 4)", 0.375)],
         '''
def ai(flops, reads, writes, size):
    return round(flops / ((reads + writes) * size), 3)
''', 'Bytes = (reads + writes) × size.', '<p>These are SAXPY, DAXPY, scale and x³ + x from workbook 3.4.</p>')

K.must('FLOPs', 'Matmul 2n³, k × k filter 2k² per output. Peak = SMs × cores × 2 × clock. FMA = 2 FLOPs.')
K.must('Bandwidth', 'GB/s = (read + written bytes) ÷ 10⁹ ÷ s. Count both directions.')
K.must('AI', 'FLOPs ÷ bytes. SAXPY 1/6, plain matmul 0.25, perfect reuse n/8 float, n/16 double.')
K.must('Roofline', 'Attainable = min(peak, AI × B). Ridge = peak ÷ B. Left memory bound, right compute bound.')
K.must('Time bound', 't ≥ max(FLOPs ÷ peak, bytes ÷ bandwidth). Memory bound kernels gain nothing from more cores.')

T = K.topic(
    slug='roofline', topic='roofline', step=(4, 'Numbers and performance limits', 'gpu-perf', 'Understand how GPUs store numbers and how to predict a kernel\'s top speed from FLOPs, bytes and the roofline.', 'College'),
    title='FLOPs, bandwidth and the roofline', short='Roofline', badge='4.2', minutes=50,
    lead='Count the work and the bytes of a kernel, work out its arithmetic intensity, and use the roofline to predict its top speed and what will make it faster.',
    desc='FLOP counting, GPU peak, efficiency, bandwidth, arithmetic intensity of SAXPY, DAXPY and matmul, the roofline and ridge point, memory and compute bound, benchmark numbers and copy overheads.',
    summary='FLOPs and peak, bandwidth, arithmetic intensity, roofline and ridge point, reading benchmarks.',
    keywords=['FLOPs', 'bandwidth', 'arithmetic intensity', 'roofline', 'ridge point', 'memory bound'],
    recap='<p>A kernel cannot run faster than min(peak, AI × bandwidth). Raise AI with reuse to move right of the ridge.</p>')
