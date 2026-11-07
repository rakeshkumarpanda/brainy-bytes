# Core Python 1.3: operators and expressions. Follows PCEP-30-02 section 1.4 (numeric, string, assignment,
# unary and binary operators, priorities and binding, bitwise, Boolean and relational operators, float accuracy).
# Facts checked against the Python 3.14 Language Reference, chapter 6 (expressions, operator precedence table),
# the math module documentation and IEEE 754 binary64.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-operators')
K = Kit()

K.code('arith', r'''
a, b = 17, 5
print("a + b  =", a + b)
print("a - b  =", a - b)
print("a * b  =", a * b)
print("a / b  =", a / b)     # true division: always a float
print("a // b =", a // b)    # floor division: round down
print("a % b  =", a % b)     # remainder
print("a ** b =", a ** b)    # power
print("divmod =", divmod(a, b))   # (quotient, remainder) together
''')

K.code('floor', r'''
# Floor division rounds DOWN (towards minus infinity), and % follows the divisor's sign
for a, b in [(7, 2), (-7, 2), (7, -2), (-7, -2)]:
    q, r = a // b, a % b
    print(f"{a:3} // {b:2} = {q:3}   {a:3} % {b:2} = {r:3}   check: {q} * {b} + {r} = {q * b + r}")
''')

K.code('precedence', r'''
print(2 + 3 * 4)        # * before +        -> 14
print((2 + 3) * 4)      # brackets first    -> 20
print(-2 ** 2)          # ** before unary - -> -4
print((-2) ** 2)        #                   -> 4
print(2 ** 3 ** 2)      # ** from the right -> 512
print(100 / 10 / 5)     # / from the left   -> 2.0
print(7 - 4 - 2)        # - from the left   -> 1
''')

K.code('compare', r'''
x = 7
print(x > 5, x == 7, x != 7)
print(1 < x < 10)            # chained: means 1 < x and x < 10
print(3 == 3.0)              # different types, same value
print("apple" < "banana")    # text compares letter by letter
print("Zebra" < "apple")     # capital letters come first (Unicode order)
print(0.1 + 0.2 == 0.3)      # float rounding!
import math
print(math.isclose(0.1 + 0.2, 0.3))
''')

K.code('logic', r'''
age, has_ticket = 20, False
print(age >= 18 and has_ticket)      # both must be True
print(age >= 18 or has_ticket)       # one is enough
print(not has_ticket)

# and / or return one of their operands, not always True or False
print(0 or "default")                # first truthy value
print("Asha" and "Ravi")             # last value if all are truthy
print([] and 1 / 0)                  # short circuit: 1 / 0 never runs
name = ""
print(name or "Guest")               # a common pattern for a default
''')

K.code('bitwise', r'''
a, b = 12, 10
print(f"a = {a:04b}, b = {b:04b}")
print(f"a & b  = {a & b:04b} = {a & b}")
print(f"a | b  = {a | b:04b} = {a | b}")
print(f"a ^ b  = {a ^ b:04b} = {a ^ b}")
print("~a     =", ~a)             # always -a - 1
print("a << 2 =", a << 2)         # a * 4
print("a >> 2 =", a >> 2)         # a // 4
print("is 13 odd?", 13 & 1 == 1)
''')

K.code('floats', r'''
from decimal import Decimal
from fractions import Fraction
import math

print(0.1 + 0.2)
print(Decimal(0.1))               # the exact value stored for 0.1
print(Decimal("0.1") + Decimal("0.2"))
print(Fraction(1, 10) + Fraction(2, 10))
print(round(2.675, 2))            # 2.675 is stored as 2.67499...
print(math.floor(-2.5), math.ceil(-2.5), math.trunc(-2.5))
print(1e308 * 10, -1e308 * 10)    # too big: inf
print(math.sqrt(2) ** 2 == 2, math.isclose(math.sqrt(2) ** 2, 2))
''')

K.code('strops', r'''
print("ab" + "cd")        # join (concatenate)
print("ha" * 3)           # repeat
print("-" * 20)
print("py" in "python")   # membership
print(len("hello"))
total = 0
total += 5                # augmented assignment
total *= 3
total -= 1
print(total)
''')

K.lesson('idea', 'Operators: the verbs of a program', f'''
{src('Python 3.14 Language Reference, chapter 6 (Expressions), and PCEP-30-02 section 1.4.')}
{wwh('An <b>operator</b> is a symbol that does something with values, called <b>operands</b>. In <code>7 + 2</code> the operator is + and the operands are 7 and 2. A combination of values and operators is an <b>expression</b>, and it always produces a value.',
     'Programs exist to work things out: a bill total, an average, whether a user may log in. Operators are how we tell Python to calculate, compare and decide.',
     'Python reads an expression, decides the order of the operations with fixed priority rules, and works them out one at a time until one value is left.')}
{table(['Group', 'Operators', 'Example', 'Result'], [
    ['Arithmetic', '+ - * / // % **', '17 // 5', '3'],
    ['Comparison', '== != &lt; &lt;= &gt; &gt;=', '3 &lt; 5', 'True'],
    ['Logical', 'and or not', 'True and False', 'False'],
    ['Bitwise', '&amp; | ^ ~ &lt;&lt; &gt;&gt;', '12 &amp; 10', '8'],
    ['Assignment', '= += -= *= /= //= %= **=', 'n += 1', 'n grows by 1'],
    ['Membership', 'in, not in', '"a" in "cat"', 'True'],
    ['Identity', 'is, is not', 'x is None', 'True or False']])}
{note('A unary operator has one operand (-x, not x, ~x). A binary operator has two (a + b). The same symbol - can be either.', 'exam')}
''', kw=['operator', 'operand', 'expression', 'unary', 'binary', 'arithmetic operators', 'comparison operators'])

K.lesson('arith', 'Arithmetic: the seven number operators', f'''
{run('arith')}
{fxs(fx('True division', 'a / b', 'Always gives a float: 6 / 3 = 2.0.'),
     fx('Floor division', 'a // b = &lfloor;a &divide; b&rfloor;', 'Divide, then round down towards minus infinity. 7 // 2 = 3, -7 // 2 = -4.', key=True),
     fx('Remainder (modulo)', 'a % b = a &minus; b &middot; (a // b)', 'Has the same sign as b. -7 % 2 = 1.', key=True),
     fx('The division identity', 'a == (a // b) * b + a % b', 'Always true in Python for b &ne; 0. Use it to check your answers.', key=True))}
{viz('pyprec', e='-7 // 2 + -7 % 2')}
{run('floor')}
{table(['Operand types', '+ - * // % **', '/'], [
    ['int and int', 'int (but int ** negative int is float)', 'float'],
    ['int and float', 'float', 'float'],
    ['bool and int', 'int (True counts as 1)', 'float']])}
{note('C and Java cut integer division towards zero, so -7 / 2 is -3 there. Python floors, so -7 // 2 is -4. Exams love this difference.', 'exam')}
''', kw=['arithmetic', 'true division', 'floor division', 'modulo', 'remainder', 'power', 'divmod', 'negative numbers'])

K.lesson('precedence', 'Which operation goes first', f'''
<p>When an expression has several operators, Python does not just go left to right. It follows a priority list, the same idea as BODMAS or PEMDAS in school maths, with a few Python twists.</p>
{viz('pyprec')}
{table(['Priority (high to low)', 'Operators', 'Direction'], [
    ['1', '( ) brackets', 'innermost first'],
    ['2', '**', 'right to left'],
    ['3', '+x, -x, ~x (unary)', ''],
    ['4', '* / // %', 'left to right'],
    ['5', '+ -', 'left to right'],
    ['6', '&lt;&lt; &gt;&gt;', 'left to right'],
    ['7', '&amp;, then ^, then |', 'left to right'],
    ['8', 'comparisons, in, not in, is, is not', 'chained'],
    ['9', 'not', ''],
    ['10', 'and', ''],
    ['11', 'or', ''],
    ['12', 'if else (conditional expression), lambda, :=', '']])}
{run('precedence')}
{note('-2 ** 2 is -4, not 4. The power is done first, then the minus. Write (-2) ** 2 when you mean minus two squared.', 'warn')}
''', kw=['precedence', 'priority', 'associativity', 'BODMAS', 'PEMDAS', 'right associative', 'power before unary minus'])

K.lesson('compare', 'Comparisons and the trouble with floats', f'''
{run('compare')}
{viz('pyfloat')}
{fxs(fx('Safe float comparison', '|a &minus; b| &le; max(rel &middot; max(|a|, |b|), abs_tol)', 'This is math.isclose(a, b). The default rel is 1e-09 and abs_tol is 0.', key=True),
     fx('Machine epsilon', '&epsilon; = 2<sup>&minus;52</sup> &asymp; 2.22 &times; 10<sup>&minus;16</sup>', 'The gap between 1.0 and the next float. sys.float_info.epsilon.'))}
{versus('Three ways to hold decimal numbers', ['', 'float', 'decimal.Decimal', 'fractions.Fraction'], [
    ['Stores', 'base 2, 53 bits', 'base 10, as many digits as you set', 'an exact top and bottom number'],
    ['0.1 + 0.2 == 0.3', 'False', 'True (with Decimal("0.1"))', 'True'],
    ['Speed', 'Fastest, done by the chip', 'Slower', 'Slowest'],
    ['Use for', 'Science, graphics, machine learning', 'Money and bills', 'Exact maths with ratios']],
    'use float by default, Decimal for money, and never test floats with == when the values come from calculations.')}
''', kw=['comparison', 'chained comparison', 'float precision', '0.1 + 0.2', 'math.isclose', 'epsilon', 'Decimal', 'Fraction', 'IEEE 754'])

K.lesson('logic', 'Logical operators and short circuit', f'''
{table(['a', 'b', 'a and b', 'a or b', 'not a'], [
    ['True', 'True', 'True', 'True', 'False'],
    ['True', 'False', 'False', 'True', 'False'],
    ['False', 'True', 'False', 'True', 'True'],
    ['False', 'False', 'False', 'False', 'True']])}
{run('logic')}
{steps('How and and or really work', [
    'a and b: look at a. If a is falsy (False, 0, "", [], None), the answer is a and b is never looked at.',
    'Otherwise the answer is b.',
    'a or b: look at a. If a is truthy, the answer is a and b is skipped. Otherwise the answer is b.',
    eq('Skipping the right side is called short circuit evaluation')])}
{viz('pyprec', e='5 > 9 and 1 / 0 > 1')}
{note('not has a higher priority than and, and and is higher than or. So True or False and False is True or (False and False) = True.', 'exam')}
''', kw=['and', 'or', 'not', 'truth table', 'short circuit', 'truthy', 'falsy', 'default value'])

K.lesson('bits', 'Bitwise operators', f'''
{viz('pybits')}
{run('bitwise')}
{fxs(fx('Bitwise not', '~x = &minus;x &minus; 1', 'Python ints act like two\'s complement numbers with endless bits.', key=True),
     fx('Shifts', 'x &lt;&lt; k = x &middot; 2<sup>k</sup>,  x &gt;&gt; k = x // 2<sup>k</sup>', 'Shifting is a fast way to multiply or divide by powers of 2.', key=True),
     fx('Useful tricks', 'x &amp; 1 (odd?), x &amp; (x &minus; 1) == 0 (power of 2?), x ^ x == 0', 'Used in LeetCode problems such as Single Number and Power of Two.'))}
{scene('file permissions on Linux', '<p>Read, write and run permissions are three bits: 4, 2 and 1. 7 (111) means all three, 5 (101) means read and run. A program checks "can this user write?" with perm &amp; 2 != 0. Python\'s os and stat modules use exactly these bitwise operators.</p>')}
''', kw=['bitwise', 'and', 'or', 'xor', 'not', 'shift', 'two\'s complement', 'bit tricks', 'permissions'])

K.lesson('more', 'Text operators and assignment shortcuts', f'''
{run('strops')}
{table(['Operator', 'With text', 'Example'], [
    ['+', 'Joins two texts', '"ab" + "cd" is "abcd"'],
    ['*', 'Repeats a text a whole number of times', '"ha" * 3 is "hahaha"'],
    ['in', 'Is one text inside another?', '"py" in "python" is True'],
    ['== &lt; &gt;', 'Compare letter by letter by Unicode number', '"Zebra" &lt; "apple" is True']])}
{note('"5" + 5 is a TypeError. Python never turns a number into text by itself. Use str(5) or an f-string.', 'warn')}
''', kw=['string concatenation', 'repetition', 'in', 'augmented assignment', '+=', 'TypeError'])

K.lesson('maths', 'The maths behind the operators', f'''
{fxs(fx('Euclidean style division in Python', 'a = q &middot; b + r,  q = &lfloor;a/b&rfloor;,  0 &le; r &lt; b (b &gt; 0)', 'For b &lt; 0, b &lt; r &le; 0.', key=True),
     fx('Last digit and dropping it', 'n % 10,  n // 10', 'Used to loop over the digits of a number.', key=True),
     fx('Sum of digits test for 9', 'n % 9 == digit_sum(n) % 9', 'Because 10 % 9 = 1, every place value leaves remainder 1.'),
     fx('Float spacing near x', 'ulp(x) &asymp; |x| &middot; 2<sup>&minus;52</sup>', 'math.ulp(x). Bigger numbers have bigger gaps between floats.'))}
{run('floats')}
{steps('Worked example: -17 // 5 and -17 % 5', [
    '-17 / 5 = -3.4.',
    'Floor (round down) of -3.4 is -4, so -17 // 5 = -4.',
    'r = a &minus; b &middot; q = -17 &minus; 5 &times; (-4) = -17 + 20 = 3.',
    eq('-17 // 5 = -4 and -17 % 5 = 3. Check: -4 &times; 5 + 3 = -17')])}
''', kw=['division algorithm', 'quotient remainder', 'digits', 'ulp', 'decimal', 'fractions'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Operators are like buttons on a calculator. Python presses them in a fixed order: brackets, powers, times and divide, then plus and minus.</p>',
    '<p>// floors and % follows the sign of the divisor, so a == (a // b) * b + a % b always holds. and and or short circuit and return an operand. Floats are binary fractions, so compare them with math.isclose().</p>',
    '<p>Every operator calls a special method: a + b tries a.__add__(b), then b.__radd__(a). Comparisons can be chained because a &lt; b &lt; c compiles to a &lt; b and b &lt; c with b evaluated once. Advanced 1.1 builds your own operators.</p>',
    '<p>IEEE 754 binary64 gives correctly rounded + - * / and sqrt. Python\'s repr uses the shortest round trip algorithm (David Gay), and its int ** int uses binary exponentiation in O(log n) multiplications. Errors in long float sums can be cut with math.fsum (Shewchuk\'s exact summation).</p>')}
{grow('Use + - * / // % ** and comparisons, and add brackets when unsure.',
      'Know floor division with negatives, short circuit, chained comparisons, bit tricks and float pitfalls.',
      'Explain operator dispatch to special methods, IEEE 754 rounding, math.fsum and exponentiation by squaring.')}
{scene('splitting a restaurant bill', '<p>Six friends share a bill of 1,000 rupees. 1000 // 6 = 166 rupees each, and 1000 % 6 = 4 rupees are left over, so four friends pay 167. With floats, 1000 / 6 = 166.666... cannot be paid exactly. Apps that split bills use // and % exactly like this, and Decimal for the money itself.</p>')}
''', kw=['beginner', 'expert', 'operator overloading', 'fsum'])

lc(1009, 'Complement of Base 10 Integer', 'complement-of-base-10-integer', 'e', 'Bitwise xor with a mask', 'Make a mask of 1s as long as n in binary, (1 << n.bit_length()) - 1, then n ^ mask flips every bit. n = 0 gives 1.', r'''
def bitwise_complement(n):
    if n == 0:
        return 1
    mask = (1 << n.bit_length()) - 1
    return n ^ mask
''', [('bitwise_complement(5)', 2), ('bitwise_complement(7)', 0), ('bitwise_complement(10)', 5), ('bitwise_complement(0)', 1)])
lc(231, 'Power of Two', 'power-of-two', 'e', 'Bit trick', 'A power of two has exactly one 1 bit, so n &amp; (n - 1) removes it and leaves 0. n must be above 0.', r'''
def is_power_of_two(n):
    return n > 0 and n & (n - 1) == 0
''', [('is_power_of_two(1)', True), ('is_power_of_two(16)', True), ('is_power_of_two(3)', False), ('is_power_of_two(0)', False)])
lc(258, 'Add Digits', 'add-digits', 'e', 'Maths (digital root)', 'Without a loop: 0 stays 0, otherwise the answer is 1 + (num - 1) % 9.', r'''
def add_digits(num):
    if num == 0:
        return 0
    return 1 + (num - 1) % 9
''', [('add_digits(38)', 2), ('add_digits(0)', 0), ('add_digits(9)', 9)])
lc(461, 'Hamming Distance', 'hamming-distance', 'e', 'xor then count bits', 'x ^ y has a 1 exactly where the bits differ. Count the 1s.', r'''
def hamming_distance(x, y):
    return bin(x ^ y).count("1")
''', [('hamming_distance(1, 4)', 2), ('hamming_distance(3, 1)', 1)])
lc(29, 'Divide Two Integers', 'divide-two-integers', 'm', 'Shifts and truncation', 'Work with absolute values. Subtract the biggest divisor &lt;&lt; k that fits, add 1 &lt;&lt; k to the answer. LeetCode truncates towards zero and clamps to 32 bits.', r'''
def divide(dividend, divisor):
    negative = (dividend < 0) != (divisor < 0)
    a = abs(dividend)
    b = abs(divisor)
    answer = 0
    while a >= b:
        shift = 0
        while a >= (b << (shift + 1)):
            shift = shift + 1
        a = a - (b << shift)
        answer = answer + (1 << shift)
    if negative:
        answer = -answer
    biggest = 2 ** 31 - 1
    smallest = -(2 ** 31)
    if answer > biggest:
        return biggest
    if answer < smallest:
        return smallest
    return answer
''', [('divide(10, 3)', 3), ('divide(7, -3)', -2), ('divide(-2147483648, -1)', 2147483647)])

K.lesson('leetcode', 'LeetCode practice', leet(), kw=['LeetCode', 'power of two', 'hamming distance', 'add digits', 'divide two integers'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Arithmetic: + - * / // % **. / always gives a float. // rounds down. % takes the sign of the divisor. a == (a // b) * b + a % b.',
    'Priority: brackets, **, unary -, * / // %, + -, shifts, &amp; ^ |, comparisons, not, and, or. ** is right to left, the rest left to right. -2 ** 2 = -4.',
    'Comparisons give True or False and can be chained: 1 &lt; x &lt; 10. Never compare calculated floats with ==, use math.isclose().',
    'and, or short circuit and return one of their operands: name or "Guest".',
    'Bitwise: &amp; | ^ ~ &lt;&lt; &gt;&gt;. ~x = -x - 1, x &lt;&lt; k = x &middot; 2<sup>k</sup>.',
    'Text: + joins, * repeats, in tests membership. "5" + 5 is a TypeError.'],
    'Core 1.4 reads input from the user and formats output with f-strings.')}
{files('Three tasks: split a bill with // and %, check a leap year with logical operators, and count set bits.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is 17 // 5?', ['3.4', '3', '4', '2'], 1, 'Round down.', '17 / 5 = 3.4, rounded down is 3.')
K.quiz('e', 'What is 17 % 5?', ['3', '2', '3.4', '5'], 1, 'Remainder.', '17 = 3 &times; 5 + 2.')
K.quiz('e', 'What is the type of 6 / 3?', ['int', 'float', 'bool', 'str'], 1, 'True division.', '/ always gives a float: 2.0.')
K.quiz('e', 'What is 2 ** 3?', ['6', '8', '9', '5'], 1, 'Power.', '2 &times; 2 &times; 2 = 8.')
K.quiz('m', 'What is -7 // 2?', ['-3', '-4', '-3.5', '3'], 1, 'Towards minus infinity.', '-3.5 rounded down is -4.')
K.quiz('m', 'What is -7 % 3?', ['-1', '2', '1', '-2'], 1, 'Sign of the divisor.', '-7 = -3 &times; 3 + 2.')
K.quiz('m', 'What is 2 + 3 * 4 ** 2?', ['400', '50', '196', '20'], 1, '** then * then +.', '4 ** 2 = 16, 3 &times; 16 = 48, 2 + 48 = 50.')
K.quiz('m', 'What does 0 or "x" give?', ['0', '"x"', 'True', 'False'], 1, 'or returns an operand.', '0 is falsy, so or returns the second value.')
K.quiz('h', 'What is 2 ** 3 ** 2?', ['64', '512', '36', '12'], 1, 'Right to left.', '3 ** 2 = 9, 2 ** 9 = 512.')
K.quiz('h', 'What is ~5?', ['-5', '-6', '4', '6'], 1, '-x - 1.', '~5 = -5 - 1 = -6.')
K.quiz('h', 'What is True or False and False?', ['True', 'False', 'None', 'An error'], 0, 'and is stronger than or.', 'True or (False and False) = True or False = True.')
K.quiz('x', 'In the style of a CMU 15-112 exam: what does print(1 < 2 < 3 > 2 == 2) show?', ['True', 'False', 'An error', '2'], 0, 'Chain every pair.', '1 &lt; 2, 2 &lt; 3, 3 &gt; 2 and 2 == 2 are all True.')
K.quiz('x', 'In the style of an Oxford Prelims question: for which b does a == (a // b) * b + a % b fail in Python?', ['Negative b', 'Float b', 'b = 0 only (it raises ZeroDivisionError)', 'It fails for every negative a'], 2, 'Python defines // and % together.', 'The identity holds for every non zero b, int or float (up to float rounding).')

K.calc('e', 'Work out 23 // 4.', '5', '23 / 4 = 5.75.', ['23 / 4 = 5.75.', 'Round down.', eq('5')], check=23 // 4)
K.calc('e', 'Work out 23 % 4.', '3', '23 &minus; 4 &times; 5.', ['23 // 4 = 5.', '5 &times; 4 = 20.', eq('23 &minus; 20 = 3')], check=23 % 4)
K.calc('e', 'Work out 10 - 4 - 3.', '3', 'Left to right.', ['10 &minus; 4 = 6.', '6 &minus; 3.', eq('3')], check=10 - 4 - 3)
K.calc('m', 'Work out -17 // 5.', '-4', 'Floor of -3.4.', ['-17 / 5 = -3.4.', 'Round down (towards minus infinity).', eq('-4')], check=-17 // 5)
K.calc('m', 'Work out -17 % 5.', '3', 'a &minus; b &middot; (a // b).', ['a // b = -4.', '-17 &minus; 5 &times; (-4) = -17 + 20.', eq('3')], check=-17 % 5)
K.calc('m', 'Work out 12 ^ 10.', '6', '1100 xor 1010.', ['12 = 1100, 10 = 1010.', 'Different bits: 0110.', eq('6')], check=12 ^ 10)
K.calc('m', 'Work out 3 << 4.', '48', '3 &times; 2<sup>4</sup>.', ['2<sup>4</sup> = 16.', '3 &times; 16.', eq('48')], check=3 << 4)
K.calc('h', 'Work out 100 // 7 * 7 + 100 % 7.', '100', 'The division identity.', ['100 // 7 = 14, 14 &times; 7 = 98.', '100 % 7 = 2.', eq('98 + 2 = 100')], check=100 // 7 * 7 + 100 % 7)
K.calc('h', 'Work out 2 + 3 * 4 ** 2 // 5 - -7 % 3.', '9', 'Use the animation to check.', ['4 ** 2 = 16, 3 &times; 16 = 48, 48 // 5 = 9.', '-7 % 3 = 2.', eq('2 + 9 &minus; 2 = 9')], check=2 + 3 * 4 ** 2 // 5 - -7 % 3)
K.calc('x', 'In the style of a Stanford CS103 problem: machine epsilon for a 64 bit float is 2<sup>&minus;52</sup>. Give it in the form a &times; 10<sup>&minus;16</sup>, the value of a to 2 decimals.', '2.22', '2<sup>&minus;52</sup> = 2.220446... &times; 10<sup>&minus;16</sup>.', ['2<sup>10</sup> &asymp; 10<sup>3</sup>, so 2<sup>&minus;52</sup> is near 10<sup>&minus;16</sup>.', 'Exactly 2<sup>&minus;52</sup> = 2.220446049250313e-16.', eq('a = 2.22')], check=round(2 ** -52 / 1e-16, 2), tol=0.005)

K.assign('split', 'e', 'Split a bill',
         '<p>Write <code>split_bill(total, people)</code> with whole numbers. Everyone pays total // people. The remainder is shared one rupee each by the first friends. Return a list of what each person pays, the larger amounts first.</p>',
         '''
def split_bill(total, people):
    # your code here
    pass
''', [('split_bill(1000, 6)', [167, 167, 167, 167, 166, 166]), ('split_bill(90, 3)', [30, 30, 30]), ('split_bill(5, 2)', [3, 2])],
         '''
def split_bill(total, people):
    base = total // people
    extra = total % people
    shares = []
    for i in range(people):
        if i < extra:
            shares.append(base + 1)
        else:
            shares.append(base)
    return shares
''', 'base = total // people and extra = total % people. The first extra people pay base + 1.', '<p>The shares always add up to the total because of the division identity.</p>')
K.assign('leap', 'm', 'Leap year',
         '<p>Write <code>is_leap(year)</code>. A year is a leap year if it divides by 4, except years that divide by 100, except again years that divide by 400. Use one expression with and, or and not.</p>',
         '''
def is_leap(year):
    # your code here
    pass
''', [('is_leap(2024)', True), ('is_leap(1900)', False), ('is_leap(2000)', True), ('is_leap(2026)', False)],
         '''
def is_leap(year):
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
''', 'Divisible means year % n == 0.', '<p>1900 divides by 100 but not by 400, so it is not a leap year. 2000 divides by 400, so it is.</p>')
K.assign('bits', 'm', 'Count the 1 bits without bin()',
         '<p>Write <code>count_bits(n)</code> for n &ge; 0 that returns how many 1s n has in binary, using only &amp; and &gt;&gt; in a loop.</p>',
         '''
def count_bits(n):
    # your code here
    pass
''', [('count_bits(0)', 0), ('count_bits(13)', 3), ('count_bits(255)', 8), ('count_bits(1024)', 1)],
         '''
def count_bits(n):
    count = 0
    while n > 0:
        count = count + (n & 1)
        n = n >> 1
    return count
''', 'n &amp; 1 is the last bit. n &gt;&gt; 1 drops it.', '<p>The loop runs once per bit, so about log<sub>2</sub> n times.</p>')

K.must('Division', '/ gives float. // floors (towards minus infinity). % has the sign of the divisor. a == (a // b) * b + a % b.')
K.must('Priority', 'brackets, **, unary, * / // %, + -, shifts, & ^ |, comparisons, not, and, or. ** right to left. -2 ** 2 = -4.')
K.must('Comparisons', 'Chained 1 < x < 10. Floats: use math.isclose(). 0.1 + 0.2 == 0.3 is False.')
K.must('Logic', 'and, or short circuit and return an operand. not > and > or.')
K.must('Bits', '~x = -x - 1. x << k = x * 2**k. x & 1 tests odd. x & (x - 1) == 0 tests power of 2.')

T = K.topic(
    slug='py-operators', topic='py-operators', step=(1, 'Getting started', 'py-c1', 'What a program is, how Python runs it, values, types, operators and input and output.', 'Beginner'),
    title='Operators, expressions and the order Python works them out', short='Operators', badge='1.3', minutes=50,
    lead='Calculate, compare and decide. Learn the seven arithmetic operators, why -7 // 2 is -4, the full priority list, chained comparisons, short circuit logic, bitwise tricks, and why 0.1 + 0.2 is not 0.3.',
    desc='Arithmetic, true and floor division, modulo with negative numbers, the division identity, operator precedence and associativity, comparison chaining, float precision with IEEE 754, Decimal and Fraction, logical operators and short circuit, bitwise operators and shifts, text operators and augmented assignment.',
    summary='Arithmetic, // and %, precedence, comparisons, float precision, logic and short circuit, bitwise operators.',
    keywords=['operators', 'floor division', 'modulo', 'precedence', 'comparison', 'float precision', 'and or not', 'short circuit', 'bitwise', 'shift'],
    recap='<p>Python works out one operation at a time in a fixed priority order. Know floor division, short circuit and float rounding.</p>',
    added='2026-11-07', leet=leet_items())
