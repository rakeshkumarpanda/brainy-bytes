# Chapter 4.1: Floating point numbers. Source: lecture 2 (IEEE 754 named), lecture 5 (slide 2: binary fractions,
# 34.625, 5.6, the add and subtract homework, reduced precision formats, FMA counted as 2 FLOPs), workbook 5.1.
# Correction: the lecture 5 notes write 1.00101 (binary) = 1.5625, the right value is 1.15625 = 37/32 (workbook P5.1.1).
# Beyond the lecture: rounding to nearest even, machine epsilon, special values, FMA rounding once, and Kahan sums.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

FMA = r'''
#include <cstdio>
#include <cmath>

__global__ void fmaDemo(float *out, float a, float b, float c) {
    out[0] = __fmul_rn(a, b) + c;      // multiply, round, then add and round again
    out[1] = fmaf(a, b, c);            // fused: a * b + c with a single rounding
}

int main() {
    float *d, h[2];
    cudaMalloc(&d, 2 * sizeof(float));
    float a = 1.0f + 1.0f / 4096, c = -(1.0f + 1.0f / 2048);
    fmaDemo<<<1, 1>>>(d, a, a, c);
    cudaMemcpy(h, d, sizeof(h), cudaMemcpyDeviceToHost);
    printf("separate: %.10g\nfused:    %.10g\n", h[0], h[1]);
    cudaFree(d);
    return 0;
}
'''

K.code('enc', r'''
# Encode a float by hand and compare with the real bits
import struct
def fields(x):
    w = struct.unpack('>I', struct.pack('>f', x))[0]
    return w >> 31, (w >> 23) & 0xFF, w & 0x7FFFFF, hex(w)
for x in [6.75, -0.375, 34.625, 5.6]:
    s, e, m, h = fields(x)
    stored = struct.unpack('>f', struct.pack('>f', x))[0]
    print(x, "sign", s, "exp", e, "(2^%d)" % (e - 127), h, "stored", repr(stored))
''')

K.code('order', r'''
# Floating point addition is not associative
big = 1e20
print((big + -big) + 3.14)     # 3.14
print(big + (-big + 3.14))     # 0.0: 3.14 vanished when added to -1e20
# adding 0.1 ten times
s = 0.0
for _ in range(10):
    s += 0.1
print(s, s == 1.0)
''')

K.lesson('format', 'Sign, exponent and mantissa', f'''
<p>A float is stored like scientific notation in base 2: a sign, a power of two, and the digits after the point. The leading 1 is not stored, which buys one extra bit for free.</p>
{fxs(
    fx('IEEE-754 value', 'value = (−1)<sup>S</sup> × 1.<i>f</i> × 2<sup><i>E</i> − bias</sup>', 'bias = 127 for float (8 exponent bits), 1023 for double (11 bits).', key=True),
    fx('Binary fraction', '0.b₁b₂b₃… = b₁ × ½ + b₂ × ¼ + b₃ × ⅛ + …', '1.00101₂ = 1 + ⅛ + 1/32 = 1.15625.'),
    fx('Exact or not', 'a decimal fraction is exact in binary only if its denominator is a power of 2', '0.625 = 5/8 is exact. 0.6 = 3/5 repeats for ever.'))}
{table(['Format', 'Sign', 'Exponent', 'Mantissa', 'About this many decimal digits'], [
    ['FP64 double', '1', '11', '52', '16'], ['FP32 float', '1', '8', '23', '7'], ['TF32 (tensor cores)', '1', '8', '10', '3'],
    ['BF16', '1', '8', '7', '2 to 3'], ['FP16 half', '1', '5', '10', '3']])}
{viz('ieee')}
{note('The lecture 5 notes give 1.00101₂ = 1.5625. Adding the bits gives 1 + 0.125 + 0.03125 = 1.15625 = 37/32, which is the value the workbook uses.', 'warn')}
''', kw=['IEEE-754', 'sign', 'exponent', 'bias', 'mantissa', 'hidden bit', 'FP32', 'FP64', 'BF16', 'FP16', 'TF32'])

K.lesson('encode', 'Encoding by hand', f'''
{steps('Lecture 5 example: 34.625 as a float', [
    'Integer part: 34 = 100010₂ (32 + 2).',
    'Fraction by doubling: 0.625 → 1.25 (1), 0.25 → 0.5 (0), 0.5 → 1.0 (1), so .101.',
    '34.625 = 100010.101₂ = 1.00010101 × 2⁵.',
    'Exponent field 5 + 127 = 132 = 10000100₂. Mantissa 00010101 followed by zeros.',
    eq('0 10000100 00010101000000000000000 = 0x420A8000')])}
{steps('Why 5.6 is not exact', [
    '0.6 by doubling: 1.2 (1), 0.4 (0), 0.8 (0), 1.6 (1), then 0.6 again, so 0.1001 1001 1001…',
    '5.6 = 1.011001100110… × 2², exponent field 129.',
    'Round to 23 bits: word 0x40B33333.',
    eq('The float holds 5.599999904632568')])}
{code('enc')}
{fxs(fx('Machine epsilon', 'ε = 2<sup>−mantissa bits</sup>', 'FP32: 2⁻²³ ≈ 1.19 × 10⁻⁷. The gap between 1 and the next float. Relative rounding error is at most ε ÷ 2.'))}
''', kw=['encode', '34.625', '5.6', 'rounding', 'machine epsilon', 'hex word'])

K.lesson('arith', 'Adding floats, and why order matters', f'''
<p>To add two floats the hardware lines up the exponents, adds the mantissas, normalises and rounds. Lining up shifts the smaller number right, and bits that fall off the end are lost.</p>
{steps('Homework: 5.75 + 0.375', [
    '5.75 = 101.11₂ = 1.0111 × 2². 0.375 = 0.011₂ = 1.1 × 2⁻².',
    'Align: shift 1.1 right by 2 − (−2) = 4 places, 0.00011 × 2².',
    'Add: 1.01110 + 0.00011 = 1.10001 × 2².',
    eq('110.001₂ = 6.125')])}
{steps('Homework: 6.5 − 4.25', [
    '6.5 = 1.101 × 2², 4.25 = 1.0001 × 2², already aligned.',
    '1.1010 − 1.0001 = 0.1001 × 2².',
    eq('Normalise: 1.001 × 2¹ = 10.01₂ = 2.25')])}
{code('order')}
{note('A GPU reduction adds numbers in a different order from a CPU loop, so float sums can differ in the last digits. That is expected. Compare float results with a tolerance, never with ==.', 'exam')}
{cu('fma.cu', FMA, {5: '__fmul_rn forces a separate multiply that is rounded before the add.', 6: 'fmaf computes a × b + c exactly and rounds once. GPUs do this in one instruction, counted as 2 FLOPs.', 12: 'With a = 1 + 2⁻¹², a² = 1 + 2⁻¹¹ + 2⁻²⁴. The 2⁻²⁴ term is lost by the separate multiply but kept by the FMA.'}, out='separate: 0\nfused:    5.960464478e-08')}
''', kw=['floating point addition', 'alignment', 'not associative', 'tolerance', 'FMA', 'rounding once'])

K.lesson('special', 'Special values and precision on GPUs', f'''
{table(['Exponent field', 'Mantissa', 'Meaning'], [
    ['0', '0', '±0'], ['0', 'not 0', 'subnormal (tiny numbers, no hidden 1)'], ['1 to 254', 'anything', 'normal number'],
    ['255', '0', '±infinity (overflow, 1 ÷ 0)'], ['255', 'not 0', 'NaN (0 ÷ 0, √−1)']])}
<p>Double precision costs more on most GPUs. Fermi did 1 TFLOP/s single and 0.5 TFLOP/s double. Gaming GPUs run FP64 at 1/32 or 1/64 of FP32. Use double where accuracy needs it, for example long sums in scientific codes.</p>
{deep('Kahan summation', '<p>Keep a small correction c of the bits lost at each step: y = x − c, t = s + y, c = (t − s) − y, s = t. The error stops growing with the number of terms. It costs 4 operations per element instead of 1.</p>')}
''', kw=['NaN', 'infinity', 'subnormal', 'double precision cost', 'Kahan summation'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A float is a number in scientific notation with a fixed number of digits. Some numbers, like 0.1, cannot be written exactly, so tiny errors appear.</p>',
    '<p>value = (−1)^S × 1.f × 2^(E − bias). Float 1/8/23, bias 127. Align, add, normalise, round. Order changes sums.</p>',
    '<p>Mixed precision: store in FP16 or BF16, multiply on tensor cores, accumulate in FP32 (chapter 8.1). Watch overflow in FP16 (largest 65,504) and use loss scaling in training.</p>',
    '<p>FP8 (E4M3 and E5M2) on Hopper and FP4 on Blackwell use per block scale factors to keep the range. Deterministic reductions fix the summation order so results repeat bit for bit.</p>')}
''', kw=['ladder', 'mixed precision', 'FP8', 'loss scaling', 'deterministic'])

K.quiz('e', 'How many exponent bits does a float have?', ['5', '8', '11', '23'], 1, '1/8/23.', '8 bits, bias 127.')
K.quiz('e', 'The bias for float is', ['0', '127', '128', '1023'], 1, 'Stored 127 means 2⁰.', '127.')
K.quiz('e', '1.1₂ in decimal', ['1.1', '1.5', '1.25', '3'], 1, '1 + ½.', '1.5.')
K.quiz('m', '1.00101₂ in decimal', ['1.5625', '1.15625', '1.3125', '1.0625'], 1, '1 + ⅛ + 1/32.', '1.15625 = 37/32.')
K.quiz('m', 'Stored exponent of 6.75', ['2', '127', '129', '130'], 2, '1.1011 × 2².', '2 + 127 = 129.')
K.quiz('m', 'Why is 5.6 not exact?', ['Too big', '0.6 = 3/5 has no finite binary form', 'Floats only store integers', 'It is exact'], 1,
       'Denominator not a power of 2.', 'Its binary fraction repeats for ever.')
K.quiz('m', 'An FMA counts as', ['1 FLOP', '2 FLOPs', '3 FLOPs', '0'], 1, 'Multiply and add.', 'Two operations, one instruction.')
K.quiz('h', '(10²⁰ + (−10²⁰)) + 3.14 against 10²⁰ + (−10²⁰ + 3.14) in double', ['Both 3.14', '3.14 and 0', 'Both 0', '0 and 3.14'], 1,
       'Alignment loses 3.14.', 'Floating point addition is not associative.')
K.quiz('h', 'Exponent field all ones and mantissa not zero means', ['Infinity', 'Zero', 'NaN', 'Subnormal'], 2, 'Special value.', 'NaN.')
K.quiz('h', 'BF16 against FP16', ['BF16 has more mantissa bits', 'BF16 keeps FP32\'s 8 exponent bits, so its range matches FP32', 'They are the same', 'FP16 has 8 exponent bits'], 1,
       'Range against precision.', 'BF16 trades precision for FP32 range.')
K.quiz('x', 'Machine epsilon of FP16 (10 mantissa bits)', ['2⁻⁷', '2⁻¹⁰', '2⁻²³', '2⁻⁵'], 1, '2^−mantissa bits.', '≈ 0.000977.')
K.quiz('x', 'Why can a GPU sum of a float array differ from the CPU sum?', ['GPU bug', 'Different addition order with rounding at each step', 'GPUs use integers', 'Cache misses'], 1,
       'Order.', 'Tree order rounds differently from a serial loop.')

K.calc('e', '1.00101₂ in decimal?', '1.15625', 'Add the place values.',
       ['Bits at ⅛ and 1/32.', '1 + 0.125 + 0.03125.', eq('1.15625')], check=1 + 1 / 8 + 1 / 32)
K.calc('e', 'Stored exponent field for 6.75?', '129', '1.1011 × 2².',
       ['6.75 = 110.11₂.', '= 1.1011 × 2².', eq('2 + 127 = 129')], check=129)
K.calc('e', 'Value of the float 0 10000001 01000…0?', '5', 'Exponent 129 − 127.',
       ['Exponent 2.', 'Mantissa 1.01₂ = 1.25.', eq('1.25 × 4 = 5')], check=5)
K.calc('m', '5.75 + 0.375 by the hardware steps?', '6.125', 'Align by 4 places.',
       ['1.0111 × 2² + 0.00011 × 2².', '= 1.10001 × 2².', eq('6.125')], check=6.125)
K.calc('m', '6.5 − 4.25 in binary?', '2.25', 'Already aligned.',
       ['1.1010 − 1.0001 = 0.1001 (× 2²).', 'Normalise to 1.001 × 2¹.', eq('2.25')], check=2.25)
K.calc('m', 'Stored exponent field for −0.375?', '125', '1.1 × 2⁻².',
       ['0.375 = 0.011₂ = 1.1 × 2⁻².', '−2 + 127.', eq('125 (word 0xBEC00000)')], check=125)
K.calc('m', 'Exponent field for 34.625?', '132', '1.00010101 × 2⁵.',
       ['34.625 = 100010.101₂.', '5 + 127.', eq('132')], check=132)
K.calc('h', 'Machine epsilon of FP32 (scientific, 3 significant figures, as a decimal)?', '1.19e-7', '2⁻²³.',
       ['2⁻²³ = 1 ÷ 8,388,608.', '≈ 0.000000119.', eq('1.19 × 10⁻⁷')], check=2 ** -23, tol=1e-9)
K.calc('h', 'Largest finite FP16 value?', '65504', '(2 − 2⁻¹⁰) × 2¹⁵.',
       ['Largest exponent field 30, so 2³⁰⁻¹⁵ = 2¹⁵.', 'Mantissa all ones: 2 − 2⁻¹⁰.', eq('1.9990234 × 32,768 = 65,504')], check=(2 - 2 ** -10) * 2 ** 15)
K.calc('x', 'Fermi: 1000 GFLOP/s single, 500 double. A 2 × 10¹² FLOP job in double takes how many seconds at peak?', '4', 'Double rate.',
       ['500 GFLOP/s = 5 × 10¹¹.', '2 × 10¹² ÷ 5 × 10¹¹.', eq('4 s (2 s in single)')], check=2e12 / 500e9)
K.calc('x', 'FP16 smallest positive normal number as a power of two (give the exponent)?', '-14', 'Exponent field 1.',
       ['Bias 15.', 'Field 1 means 2¹⁻¹⁵.', eq('2⁻¹⁴ ≈ 6.1 × 10⁻⁵')], check=-14)

K.assign('decode', 'm', 'Decode a float word',
         '<p>Write <code>decode(bits)</code> for a 32 character string of 0s and 1s holding a normal float. Return its value.</p>',
         '''
def decode(bits):
    # your code here
    pass
''', [("decode('01000000101000000000000000000000')", 5.0), ("decode('10111110110000000000000000000000')", -0.375), ("decode('01000010000010101000000000000000')", 34.625)],
         '''
def decode(bits):
    s = int(bits[0])
    e = int(bits[1:9], 2) - 127
    m = 1 + int(bits[9:], 2) / 2 ** 23
    return (-1) ** s * m * 2 ** e
''', 'Split 1/8/23, remove the bias, add the hidden 1.', '<p>The three tests are the lecture and workbook examples 5.0, −0.375 and 34.625.</p>')
K.assign('fracbin', 'e', 'Fraction to binary by doubling',
         '<p>Write <code>frac_bits(x, n)</code> for 0 ≤ x &lt; 1: return the first <code>n</code> binary digits after the point as a string, using repeated doubling.</p>',
         '''
def frac_bits(x, n):
    # your code here
    pass
''', [("frac_bits(0.625, 3)", "101"), ("frac_bits(0.6, 8)", "10011001"), ("frac_bits(0.375, 4)", "0110")],
         '''
def frac_bits(x, n):
    out = ''
    for _ in range(n):
        x *= 2
        if x >= 1:
            out += '1'
            x -= 1
        else:
            out += '0'
    return out
''', 'Double, write the integer part, keep the rest.', '<p>0.6 shows the repeating 1001 pattern.</p>')

K.must('Format', 'value = (−1)^S × 1.f × 2^(E − bias). Float 1/8/23 bias 127, double 1/11/52 bias 1023.')
K.must('Exact', 'Exact in binary only when the denominator is a power of 2. 5.6 is stored as 5.599999904632568.')
K.must('Add', 'Align exponents, add mantissas, normalise, round. Not associative: compare with a tolerance.')
K.must('FMA', 'a × b + c with one rounding, one instruction, counted as 2 FLOPs.')
K.must('Formats', 'FP16 1/5/10 (max 65,504), BF16 1/8/7, TF32 1/8/10. Epsilon = 2^−mantissa bits.')

T = K.topic(
    slug='floating-point', topic='floating-point', step=(4, 'Numbers and performance limits', 'gpu-perf', 'Understand how GPUs store numbers and how to predict a kernel\'s top speed from FLOPs, bytes and the roofline.', 'College'),
    title='Floating point numbers on the GPU', short='Floating point', badge='4.1', minutes=40,
    lead='See how a decimal number becomes 32 bits, why 5.6 cannot be stored exactly, how floats are added, and why a GPU sum can differ from a CPU sum.',
    desc='IEEE-754 sign, exponent and mantissa, binary fractions, encoding 6.75, 34.625 and 5.6, the add and subtract homework, non associativity, FMA, special values, FP16, BF16 and TF32.',
    summary='IEEE-754 encoding, binary fractions, float addition, non associativity, FMA and reduced precision formats.',
    keywords=['IEEE-754', 'floating point', 'mantissa', 'exponent', 'FMA', 'FP16', 'BF16'],
    recap='<p>A float is sign, biased exponent and mantissa. Most decimals are rounded, addition order matters, and FMA rounds once.</p>')
