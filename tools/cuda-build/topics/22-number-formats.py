# Chapter 8.1: Low precision numbers and quantisation. Source: lecture 9 (slides 2 to 5: math limited and memory
# limited layers, slides 10, 11 and 19: formats, the bits formula, which format when, quantisation named in class,
# slide 17: wider accumulator), workbook 9.3 and P9.1.6. Corrections from the notes: slide 11's bars are illustrative,
# and TF32 is not a storage format. Beyond the lecture: zero point and per channel scales, and FP8 scaling factors.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

QUANT = r'''
#include <cuda_fp16.h>
#include <cuda_bf16.h>
#include <cstdint>

__global__ void quantise(const float *w, int8_t *q, int n, float s) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        float r = rintf(w[i] / s);                 // round to the nearest integer
        r = fminf(fmaxf(r, -127.0f), 127.0f);      // clip to the INT8 range
        q[i] = (int8_t)r;
    }
}

__global__ void dequantise(const int8_t *q, float *w, int n, float s) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) w[i] = s * q[i];
}

__global__ void to_16bit(const float *x, __half *h, __nv_bfloat16 *b, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        h[i] = __float2half(x[i]);                 // FP16: 5 exponent bits, 10 mantissa bits
        b[i] = __float2bfloat16(x[i]);             // BF16: 8 exponent bits, 7 mantissa bits
    }
}
'''

K.code('half', r'''
# Store numbers in FP16 and BF16 and read them back
import struct
def fp16(x):
    return struct.unpack('e', struct.pack('e', x))[0]
def bf16(x):
    b = struct.unpack('>I', struct.pack('>f', x))[0]
    b = (b + 0x7FFF + ((b >> 16) & 1)) & 0xFFFF0000    # round to nearest even, keep top 16 bits
    return struct.unpack('>f', struct.pack('>I', b))[0]
for x in (3.14159265, 300.7, 0.1):
    print(x, " FP16:", fp16(x), " BF16:", bf16(x))
print("largest FP16:", fp16(65504.0))
print("2048 + 1 in FP16:", fp16(fp16(2048.0) + 1.0))
''')

K.code('quant', r'''
# Symmetric INT8 quantisation of weights in the range -R to R
R, qmax = 1.0, 127
s = R / qmax
print("scale s =", round(s, 6))
for x in (0.3, -0.8, 1.0, -0.05):
    q = max(-qmax, min(qmax, round(x / s)))
    back = q * s
    print(x, "-> q =", q, "-> back", round(back, 4), " error", round(abs(back - x), 4))
''')

K.lesson('why', 'Why use fewer bits?', f'''
<p>A neural network is a chain of layers. Lecture 9 splits them into two families.</p>
{table(['Family', 'Examples', 'Time goes into', 'Tensor cores help?'], [
    ['Math limited', 'convolution, fully connected, recurrent', 'calculating', 'a lot'],
    ['Memory limited', 'bias add, normalisation, ReLU, dropout', 'moving numbers', 'not at all']])}
<p>Fewer bits per number help both. The memory limited layers move half the bytes in FP16 and a quarter in INT8. The math limited layers get faster hardware: a tensor core does many more 16 bit multiplies than 32 bit ones in the same time.</p>
<p>It works because networks forgive small errors. In class the example was accuracy falling from 92 to 91 percent, which is fine, against 92 to 82 percent, which is not. Scientific codes, such as nuclear or biological simulations, cannot accept that and stay in FP64.</p>
{fxs(
    fx('Fewer bytes, higher intensity', 'AI = FLOPs ÷ bytes', 'Halve the bytes and the arithmetic intensity doubles. Batch 1 FC layer: AI ≈ 1 in FP16, ≈ 2 with INT8 weights.', key=True))}
''', kw=['low precision', 'math limited', 'memory limited', 'bytes per number', 'accuracy', 'FP64 science'])

K.lesson('formats', 'How a float is stored, and the formats side by side', f'''
<p>Every floating point number has a sign bit, E exponent bits and M mantissa bits.</p>
{fxs(
    fx('Value of a normal number', 'x = (−1)<sup>s</sup> × 1.m<sub>1</sub>m<sub>2</sub>…m<sub>M</sub> (binary) × 2<sup>e − bias</sup>', 'The leading 1 is not stored, so M bits give M + 1 bits of precision.', key=True),
    fx('Bias', 'bias = 2<sup>E − 1</sup> − 1', '5 bits: 15. 8 bits: 127. 11 bits: 1023.', key=True),
    fx('Gap after 1.0', 'ε = 2<sup>−M</sup>', 'FP32 1.2 × 10⁻⁷, FP16 9.8 × 10⁻⁴, BF16 7.8 × 10⁻³.'),
    fx('Decimal digits', '≈ (M + 1) × log<sub>10</sub> 2 ≈ 0.3 (M + 1)', 'FP32 about 7, FP16 about 3, BF16 about 2.4.'))}
{table(['Format', 'E', 'M', 'Largest', 'Gap after 1.0', 'Digits'], [
    ['FP64', '11', '52', '1.8 × 10³⁰⁸', '2.2 × 10⁻¹⁶', '16'],
    ['FP32', '8', '23', '3.4 × 10³⁸', '1.2 × 10⁻⁷', '7.2'],
    ['TF32', '8', '10', '3.4 × 10³⁸', '9.8 × 10⁻⁴', '3.3'],
    ['FP16', '5', '10', '65,504', '9.8 × 10⁻⁴', '3.3'],
    ['BF16', '8', '7', '3.4 × 10³⁸', '7.8 × 10⁻³', '2.4'],
    ['FP8 E4M3', '4', '3', '448', '0.125', 'about 1'],
    ['FP8 E5M2', '5', '2', '57,344', '0.25', 'under 1']])}
<p>Exponent bits give <b>range</b>: each extra bit doubles how many powers of two are available. Mantissa bits give <b>detail</b>: they split each interval such as [1, 2) into 2<sup>M</sup> equal steps. Type any number below and see what each format keeps.</p>
{viz('formats')}
{steps('π in FP16', [
    '3.14159 = 1.5708 × 2¹.',
    'Sign 0. Exponent 1 + 15 = 16 = 10000₂.',
    'Mantissa: keep 10 bits of 0.5708, which is 1001001000₂.',
    'Value 1.5703125 × 2 = 3.140625.',
    eq('3.140625, about 3 correct digits (FP32 gives 3.1415927)')])}
{code('half')}
''', kw=['IEEE 754', 'sign', 'exponent', 'mantissa', 'bias', 'epsilon', 'FP16', 'BF16', 'TF32', 'FP8', 'range', 'precision'])

K.lesson('which', 'Which format when, and why the sum stays wide', f'''
{table(['Format', 'Used for', 'Watch out for'], [
    ['FP32', 'master weights in training, science, anything delicate', 'slow on tensor cores'],
    ['TF32', 'FP32 code on Ampere and later, about 8 times faster on an A100', 'not a storage format: memory still holds FP32'],
    ['FP16', 'inference, training with loss scaling', 'tiny range: gradients underflow, 70,000 overflows'],
    ['BF16', 'the default for training large models', 'only about 2 to 3 digits'],
    ['FP8, FP4', 'Hopper and Blackwell training and inference', 'needs a scale factor per tensor or per block'],
    ['INT8, INT4', 'inference after quantisation', 'needs a scale factor, accuracy must be checked']])}
<p>TF32 keeps FP32 in memory. The tensor core rounds the inputs to 10 mantissa bits inside, multiplies, and adds the results in FP32. The professor joked that it should have been called TF19, since it uses 1 + 8 + 10 bits.</p>
<p><b>Mixed precision.</b> A and B are stored in a narrow format, but the running sum is kept in FP32. Why it matters: add 1 to an FP16 sum again and again. Once the sum reaches 2048, the gap between FP16 numbers is 2, so 2048 + 1 rounds back to 2048 and the sum stops growing.</p>
{steps('FP16 versus FP32 accumulator (dot product of 4096 FP16 numbers, from the notes)', [
    'True answer −18.16.',
    'FP16 accumulator: −18.36, error 0.20.',
    'FP32 accumulator: error 0.000026.',
    eq('About 7600 times smaller error with the wide accumulator')])}
{note('Loss scaling for FP16 training: multiply the loss by a large number such as 1024 before back propagation so that small gradients do not round to 0, then divide the gradients by the same number. BF16 has the range of FP32 and does not need it.', 'tip')}
{note('Slide 11\'s bars (TF32, FP16 and BF16 at 4 times, FP8 at 8, FP4 at 16) are labelled illustrative. On an A100, TF32 is 8 times and FP16 16 times the FP32 CUDA core rate. Always use the data sheet of the GPU in front of you.', 'exam')}
''', kw=['TF32', 'FP16', 'BF16', 'loss scaling', 'mixed precision', 'accumulator', 'FP8', 'INT8'])

K.lesson('quant', 'Quantisation step by step', f'''
<p>In class the idea was "treat everything from 0.9 to 1.7 as 1". Real quantisation is a straight line map from real numbers to small integers.</p>
{fxs(
    fx('Quantise', 'q = clip(round(x ÷ s) + z, q<sub>min</sub>, q<sub>max</sub>)', 's is the scale, z the zero point.', key=True),
    fx('Bring back', 'x̂ = s × (q − z)', 'The rounding error is at most s ÷ 2 unless the value was clipped.', key=True),
    fx('Symmetric INT8', 's = R ÷ 127, z = 0', 'For values between −R and R.'),
    fx('Asymmetric (UINT8)', 's = (max − min) ÷ 255, z = round(−min ÷ s)', 'For values that are not centred on 0, such as ReLU outputs.'))}
{viz('quant')}
{steps('Workbook 9.3: store 0.3 with R = 1', [
    's = 1 ÷ 127 = 0.007874.',
    '0.3 ÷ 0.007874 = 38.1, round to 38.',
    'Back: 38 × 0.007874 = 0.2992.',
    eq('Error 0.0008, storage 1 byte instead of 4')])}
{code('quant')}
{cu('quantise.cu', QUANT, {5: 'One thread per weight. s is computed once on the host.', 8: 'rintf rounds to the nearest integer, with ties to even.', 9: 'Clip so that a weight outside the range does not wrap around.', 10: 'The integer is stored in a single byte.', 16: 'Dequantise: multiply back by the scale.', 22: 'Conversions to the two 16 bit formats are built in.'})}
{deep('Per channel scales and FP8 scaling', '<p>One scale for a whole tensor is set by its largest value, so small channels get coarse steps. Real systems keep one scale per output channel or per block of 32 to 128 values. FP8 training on Hopper keeps a scale factor per tensor that is updated from the largest values seen recently, so numbers stay inside the 448 limit of E4M3.</p>')}
''', kw=['quantisation', 'scale', 'zero point', 'INT8', 'INT4', 'dequantise', 'clipping', 'per channel'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A format is a ruler. The exponent decides how long it is, the mantissa how fine the marks are. FP16 is short with fine marks, BF16 is very long with coarse marks.</p>',
    '<p>x = (−1)<sup>s</sup> × 1.m × 2<sup>e − bias</sup>. FP16 fails on size, BF16 on detail. Accumulate in FP32. INT8: s = R ÷ 127, q = round(x ÷ s).</p>',
    '<p>Pick the format per tensor: weights INT8 or FP8, activations BF16, sums FP32. Check overflow and underflow with real data. Batch 1 inference gains roughly in proportion to the bytes saved.</p>',
    '<p>Research uses 4 bit weights (GPTQ, AWQ), block scaled FP4 on Blackwell, stochastic rounding for training, and outlier handling such as SmoothQuant.</p>')}
''', kw=['ladder', 'GPTQ', 'AWQ', 'FP4', 'stochastic rounding', 'SmoothQuant'])

K.quiz('e', 'Exponent bits decide', ['Precision', 'Range', 'Sign', 'Speed'], 1, 'How big or small.', 'Mantissa bits decide the detail.')
K.quiz('e', 'BF16 has how many exponent bits?', ['5', '7', '8', '10'], 2, 'Same as FP32.', '8, so the same range as FP32.')
K.quiz('e', 'Largest FP16 number', ['32,768', '65,504', '65,536', '3.4 × 10³⁸'], 1, '(2 − 2⁻¹⁰) × 2¹⁵.', '65,504.')
K.quiz('e', 'Which layer is memory limited?', ['Fully connected with a big batch', 'ReLU', 'Convolution', 'Large matmul'], 1, 'One operation per number.', 'ReLU moves data and barely computes.')
K.quiz('m', '300.7 stored in BF16 gives', ['300.75', '300.7', '300', '301'], 2, 'Only 7 mantissa bits.', 'Steps of 2 near 300.')
K.quiz('m', '70,000 stored in FP16 gives', ['70,000', '65,504', 'infinity (overflow)', '0'], 2, 'Above 65,504.', 'Overflow.')
K.quiz('m', 'TF32 is', ['A 19 bit storage format', 'FP32 in memory, rounded to 10 mantissa bits inside the tensor core', 'The same as FP16', 'An integer format'], 1, 'Not stored.', 'Memory still holds FP32.')
K.quiz('m', 'INT8, R = 1. q for 0.3', ['30', '38', '76', '127'], 1, '0.3 ÷ (1 ÷ 127).', '38.1 rounds to 38.')
K.quiz('h', 'Adding 1 to an FP16 sum stops growing at', ['1024', '2048', '4096', '65,504'], 1, 'Gap becomes 2.', '2048 + 1 rounds back to 2048.')
K.quiz('h', 'Why keep the accumulator in FP32?', ['Faster', 'Small products get lost when added to a large narrow sum', 'Required by C++', 'Saves memory'], 1, 'Gap grows with size.', 'Error about 7600 times smaller in the notes.')
K.quiz('x', 'Why is BF16 preferred over FP16 for training large models?', ['More digits', 'FP32 range, so no overflow or underflow and no loss scaling', 'Fewer bits', 'Only GPUs support it'], 1, 'Range beats detail.', 'Training breaks on overflow, not on the third digit.')
K.quiz('x', 'Per channel scales are used because', ['They are faster', 'One large value would make the steps coarse for every other channel', 'They save memory', 'They avoid rounding'], 1, 'Scale follows the largest value.', 'Small channels keep fine steps.')

K.calc('e', 'Bias for 8 exponent bits?', '127', '2^(E − 1) − 1.',
       ['2⁷ = 128.', 'Minus 1.', eq('127')], check=127)
K.calc('e', 'Bias for 5 exponent bits?', '15', '2⁴ − 1.',
       ['16 − 1.', '= 15.', eq('15')], check=15)
K.calc('e', 'Gap after 1.0 in BF16 (M = 7)? (four decimals)', '0.0078', '2⁻⁷.',
       ['1 ÷ 128.', '= 0.0078125.', eq('≈ 0.0078')], check=round(2 ** -7, 4), tol=0.00005)
K.calc('m', 'Largest FP16 number?', '65504', '(2 − 2⁻¹⁰) × 2¹⁵.',
       ['Largest exponent 30 − 15 = 15.', '(2 − 0.000977) × 32,768.', eq('65,504')], check=65504)
K.calc('m', 'INT8 with R = 1. q for 0.3?', '38', 'round(0.3 × 127).',
       ['0.3 × 127 = 38.1.', 'Round.', eq('q = 38')], check=38)
K.calc('m', 'Bring q = 38 back with R = 1. (four decimals)', '0.2992', '38 ÷ 127.',
       ['s = 0.007874.', '38 × s.', eq('0.2992')], check=round(38 / 127, 4), tol=0.00005)
K.calc('m', 'INT8 with R = 2. q for −0.8?', '-51', 'round(−0.8 × 63.5).',
       ['s = 2 ÷ 127 = 0.015748.', '−0.8 ÷ s = −50.8.', eq('q = −51, back −0.8031')], check=-51)
K.calc('h', 'Decimal digits of FP32 (M = 23)? (one decimal)', '7.2', '24 × log₁₀ 2.',
       ['M + 1 = 24 bits.', '24 × 0.30103 = 7.22.', eq('≈ 7.2 digits')], check=round(24 * 0.30103, 1), tol=0.05)
K.calc('h', 'Store 300.7 in FP16. Value?', '300.75', 'Step near 300.',
       ['300.7 is between 256 and 512, so the step is 2⁸ × 2⁻¹⁰ = 0.25.', '300.7 ÷ 0.25 = 1202.8, round to 1203.', eq('1203 × 0.25 = 300.75')], check=300.75)
K.calc('x', 'Batch 1 FC layer 4096 × 4096. AI with INT8 weights and FP16 activations? (one decimal)', '2.0', 'Weights dominate the bytes.',
       ['FLOPs 2 × 4096².', 'Bytes: 4096² weights × 1 + (4096 + 4096) × 2 for input and output.', eq('≈ 2.0 FLOP/byte, twice the FP16 value')],
       check=round(2 * 4096 ** 2 / (4096 ** 2 + 2 * 8192), 1), tol=0.05)
K.calc('x', 'Worst rounding error for INT8 with R = 1 (no clipping)? (five decimals)', '0.00394', 's ÷ 2.',
       ['s = 1 ÷ 127 = 0.007874.', 'Half a step.', eq('≈ 0.00394')], check=round(1 / 127 / 2, 5), tol=0.000005)

K.assign('fmtinfo', 'e', 'Facts about a format',
         '<p>Write <code>fmt_info(E, M)</code> for an IEEE style format with E exponent bits and M mantissa bits. Return a list: the bias, the gap after 1.0, and the largest finite number (2 − 2<sup>−M</sup>) × 2<sup>2<sup>E</sup> − 2 − bias</sup>.</p>',
         '''
def fmt_info(E, M):
    # your code here
    pass
''', [("fmt_info(5, 10)", [15, 0.0009765625, 65504.0]), ("fmt_info(5, 2)", [15, 0.25, 57344.0]), ("fmt_info(8, 7)[0]", 127), ("fmt_info(8, 7)[1]", 0.0078125)],
         '''
def fmt_info(E, M):
    bias = 2 ** (E - 1) - 1
    gap = 2.0 ** -M
    largest = (2 - 2.0 ** -M) * 2.0 ** (2 ** E - 2 - bias)
    return [bias, gap, largest]
''', 'The largest exponent field is all ones minus one.', '<p>FP16 gives 65,504 and FP8 E5M2 gives 57,344.</p>')
K.assign('quantise', 'm', 'Quantise a list of weights',
         '<p>Write <code>quantise(ws, R, bits)</code>. Use the symmetric scale s = R ÷ q<sub>max</sub> with q<sub>max</sub> = 2<sup>bits − 1</sup> − 1. Round each weight to the nearest integer q and clip it to −q<sub>max</sub> to q<sub>max</sub>. Return the list of q.</p>',
         '''
def quantise(ws, R, bits):
    # your code here
    pass
''', [("quantise([0.3], 1.0, 8)", [38]), ("quantise([-0.8], 2.0, 8)", [-51]), ("quantise([0.3, -0.8, 1.0], 1.0, 4)", [2, -6, 7]), ("quantise([2.5, -3.0], 1.0, 8)", [127, -127])],
         '''
def quantise(ws, R, bits):
    qmax = 2 ** (bits - 1) - 1
    s = R / qmax
    out = []
    for x in ws:
        q = round(x / s)
        out.append(max(-qmax, min(qmax, q)))
    return out
''', 'Compute s once, then round and clip each weight.', '<p>The last test shows clipping: values outside the range stick to the end.</p>')

K.must('The formula', 'x = (−1)^s × 1.m × 2^(e − bias), bias = 2^(E−1) − 1, gap after 1.0 = 2^−M.')
K.must('Range against detail', 'Exponent bits give range, mantissa bits give detail. FP16 overflows at 65,504, BF16 keeps FP32 range with about 2 to 3 digits.')
K.must('Which format', 'FP32 master weights, BF16 training, FP16 with loss scaling, TF32 for FP32 code on tensor cores, INT8 or FP8 for inference.')
K.must('Wide accumulator', 'Narrow inputs, FP32 sums. In FP16, 2048 + 1 = 2048.')
K.must('Quantisation', 'q = round(x ÷ s) + z, x̂ = s(q − z). Symmetric INT8: s = R ÷ 127. Error at most s ÷ 2 unless clipped.')

T = K.topic(
    slug='number-formats', topic='number-formats', step=(8, 'Tensor cores and fast matmul', 'gpu-tensor', 'Use narrow number formats, tensor cores and tiling tricks to get close to the peak speed of a modern GPU.', 'Pro'),
    title='Low precision numbers and quantisation', short='Number formats', badge='8.1', minutes=40,
    lead='Learn how FP32, TF32, FP16, BF16, FP8 and INT8 store a number, what each one loses, why sums stay in FP32, and how to quantise weights to 8 bits.',
    desc='Math limited and memory limited layers, the float formula and bias, range against detail, a six format comparison, TF32, loss scaling, mixed precision accumulation, symmetric and asymmetric quantisation with workbook 9.3, per channel scales and FP8 scaling.',
    summary='Float formats, range and detail, mixed precision, INT8 quantisation.',
    keywords=['FP16', 'BF16', 'TF32', 'FP8', 'INT8', 'quantisation', 'mixed precision'],
    recap='<p>Fewer bits move faster and multiply faster. Exponent bits give range, mantissa bits give detail. Keep sums in FP32, and quantise with a scale so that q = round(x ÷ s).</p>')
