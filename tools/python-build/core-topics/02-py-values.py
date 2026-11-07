# Core Python 1.2: variables, literals, data types, numeral systems and type conversion. Follows PCEP-30-02
# section 1.3 (literals, variables, numeral systems, naming conventions) and part of 1.4 (data types, type casting).
# Facts checked against the Python 3.14 documentation: Built-in Types, Lexical analysis (integer, float and
# imaginary literals, underscores in literals from PEP 515), the data model (identity, type, value) and sys.int_info.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, show, term, lc, leet, files, grow, leet_items

chapter('py-values')
K = Kit()

K.code('names', r'''
age = 25            # the name age now points to the int object 25
my_age = age        # a second name for the SAME object
print(age, my_age)
print(id(age) == id(my_age))   # True: one object, two names

age = age + 1       # a NEW object 26 is made, and age moves to it
print(age, my_age)  # my_age still points to 25
print(id(age) == id(my_age))   # False now
''')

K.code('value_types', r'''
values = [42, 3.14, 2 + 3j, "Asha", True, None, 1_000_000, 0b1010, 0o17, 0xFF, 1.5e3]
for v in values:
    print(repr(v).ljust(12), type(v).__name__)
''')

K.code('bases', r'''
n = 156
print(bin(n), oct(n), hex(n))        # number to text in base 2, 8, 16
print(int("10011100", 2))            # text in base 2 back to a number
print(int("9c", 16), int("0o234", 0)) # base 0 reads the prefix
print(0b1111 + 0x10)                 # literals in any base are just ints
print(f"{n:b} {n:o} {n:x} {n:#X}")   # format codes do the same
''')

K.code('casting', r'''
print(int("42") + 1)        # text to whole number
print(float("3.5") * 2)     # text to decimal number
print(int(3.99))            # int() cuts off the decimals, it does not round
print(int(-3.99))           # cuts towards zero: -3
print(round(3.99), round(2.5), round(3.5))   # round() goes to the even number on a tie
print(str(7) + "7")         # number to text, then join
print(bool(0), bool(7), bool(""), bool("0"), bool([]))
print(float("inf") > 10**100)
try:
    int("3.5")
except ValueError as error:
    print("ValueError:", error)
''')

K.code('bigint', r'''
import sys
big = 2 ** 100
print(big)
print(len(str(big)), "digits")
print(sys.maxsize)                 # the largest index a list can have, not a limit on int
print(sys.int_info.bits_per_digit) # CPython stores big ints in chunks of 30 bits
print((2 ** 64).bit_length())
''')

K.code('naming', r'''
import keyword
names = ["total", "total_price", "_hidden", "price2", "2price", "class", "Total", "my-name", "año"]
for name in names:
    ok = name.isidentifier() and not keyword.iskeyword(name)
    print(name.ljust(12), "valid" if ok else "NOT valid")
''')

K.code('swap', r'''
a, b = 5, 9          # two names at once (tuple unpacking)
a, b = b, a          # swap without a third variable
print(a, b)
x = y = z = 0        # chained assignment: three names, one object
print(x, y, z)
count = 10
count += 5           # same as count = count + 5
count *= 2
print(count)
''')

K.lesson('idea', 'What a variable really is', f'''
{src('Python 3.14 Language Reference, section 3.1 (objects, values and types), and PCEP-30-02 section 1.3.')}
<p>In maths class, x = 5 means "x is equal to 5". In Python, <code>x = 5</code> is an <b>action</b>: "make the value 5, and stick the label x on it".</p>
{wwh('A <b>variable</b> is a <b>name</b> that points to an <b>object</b>. Every object has three things: an identity (where it lives, id()), a type (what kind of thing it is, type()) and a value.',
     'Programs need to remember things: a price, a name, a score. Names let us refer to values again later without typing them again, and let the value change while the name stays the same.',
     'The assignment <code>name = expression</code> first works out the right side, which gives an object. Then it binds (sticks) the name on the left to that object. The old object is not changed.')}
{scene('name tags at a party', '<p>Think of objects as people at a party and names as sticky name tags. <code>age = 25</code> puts the tag "age" on the person 25. <code>my_age = age</code> puts a second tag on the same person. <code>age = age + 1</code> does not change that person into 26. It finds the person 26 and moves the "age" tag over. my_age is still stuck on 25.</p>')}
{viz('pynames')}
{run('names')}
{note('In Python a variable has no type of its own. The object has the type. The same name can point to an int now and to a str later. This is called dynamic typing.', 'tip')}
''', kw=['variable', 'name', 'object', 'binding', 'assignment', 'id', 'type', 'value', 'dynamic typing'])

K.lesson('types', 'The basic data types and their literals', f'''
<p>A <b>literal</b> is a value written straight into the code, such as <code>42</code> or <code>"Asha"</code>. Each literal makes an object of a certain type.</p>
{table(['Type', 'What it holds', 'Literals', 'Can it change?'], [
    ['int', 'Whole numbers of any size', '7, -3, 1_000_000, 0b101, 0o17, 0xFF', 'No (immutable)'],
    ['float', 'Numbers with a decimal point, about 15 to 17 correct digits', '3.14, -0.5, 2.0, 1.5e3, 1e-9', 'No'],
    ['complex', 'Numbers with a real and an imaginary part', '2 + 3j, 1j', 'No'],
    ['bool', 'True or False', 'True, False', 'No'],
    ['str', 'Text, any number of characters', '"hi", \'hi\', """many lines"""', 'No'],
    ['NoneType', 'The single value meaning "nothing here"', 'None', 'No']])}
{run('value_types')}
{fxs(fx('Scientific notation', 'a e b = a &times; 10<sup>b</sup>', '1.5e3 = 1.5 &times; 10<sup>3</sup> = 1500.0. The result is always a float.', key=True),
     fx('Underscores in numbers', '1_000_000 == 1000000', 'Since Python 3.6 (PEP 515) underscores can group digits. Python ignores them.'))}
{note('bool is a kind of int: True == 1 and False == 0, so True + True is 2. This surprises many people in exams.', 'exam')}
{deep('why int has no size limit', '<p>In C or Java an int has a fixed number of bits (32 or 64), so very big numbers overflow. CPython stores an int as a list of 30 bit digits and adds more digits when needed, so 2 ** 1000 is exact. The cost: big numbers are slower and use more memory. Since 3.11 CPython limits int to str conversion to 4,300 digits by default (sys.set_int_max_str_digits) to stop denial of service attacks.</p>' + '<p>The code below shows this.</p>')}
{run('bigint')}
''', kw=['data types', 'int', 'float', 'complex', 'bool', 'str', 'None', 'literal', 'scientific notation', 'underscore', 'immutable', 'big integers'])

K.lesson('bases', 'Numeral systems: binary, octal and hexadecimal', f'''
<p>People count in base 10 because we have ten fingers. Computers store everything as 0s and 1s, so programmers often use base 2 and its friends base 8 and base 16, which are short ways to write long rows of bits.</p>
{viz('pybase')}
{table(['Base', 'Digits', 'Python literal', 'Turn into text', 'Example'], [
    ['2 (binary)', '0, 1', '0b1010', 'bin(10)', '0b1010 == 10'],
    ['8 (octal)', '0 to 7', '0o17', 'oct(15)', '0o17 == 15'],
    ['10 (decimal)', '0 to 9', '42', 'str(42)', '42'],
    ['16 (hexadecimal)', '0 to 9, A to F', '0xFF', 'hex(255)', '0xFF == 255']])}
{fxs(fx('Value of a number written in base b', 'value = d<sub>k</sub>b<sup>k</sup> + ... + d<sub>1</sub>b<sup>1</sup> + d<sub>0</sub>b<sup>0</sup>', 'Each digit is multiplied by the base to the power of its position, counting from 0 on the right.', key=True),
     fx('Digits needed in base 2', 'bits(n) = &lfloor;log<sub>2</sub> n&rfloor; + 1', 'For n &gt; 0. Python gives it as n.bit_length(). 156 needs 8 bits.'))}
{run('bases')}
{note('A leading zero is not allowed on a decimal literal in Python 3: 017 is a SyntaxError. Write 0o17 for octal.', 'warn')}
''', kw=['binary', 'octal', 'hexadecimal', 'numeral system', 'bin', 'oct', 'hex', 'int with base', 'bit_length', 'place value'])

K.lesson('casting', 'Changing one type into another', f'''
{wwh('Type conversion (casting) makes a <b>new</b> object of another type from a value: int("42") gives the int 42.',
     'Data often arrives as text: from input(), a file, a web form. To do maths with it you must turn it into a number first. To join a number into a message you may need str().',
     'Call the type like a function: int(), float(), str(), bool(), complex(). Each one has rules about what it accepts. When the value does not fit the rules you get ValueError.')}
{table(['Call', 'Result', 'Rule'], [
    ['int("42")', '42', 'Text with only digits (and a sign, spaces around)'],
    ['int(3.99)', '3', 'Cuts towards zero, it does not round'],
    ['int("3.5")', 'ValueError', 'A decimal point in the text is not allowed'],
    ['int("ff", 16)', '255', 'A second argument gives the base'],
    ['float("3.5")', '3.5', 'Also accepts "1e3", "inf", "nan"'],
    ['str(7)', '"7"', 'Anything can become text'],
    ['bool(0), bool("")', 'False', 'Zero and empty things are False'],
    ['bool("0"), bool(" ")', 'True', 'Any non empty text is True, even "0"'],
    ['round(2.5), round(3.5)', '2, 4', 'Ties go to the even number (bankers rounding)']])}
{run('casting')}
{note('int(-3.99) is -3, not -4. int() cuts towards zero. math.floor(-3.99) is -4 because floor goes down.', 'exam')}
''', kw=['type conversion', 'casting', 'int()', 'float()', 'str()', 'bool()', 'ValueError', 'round', 'bankers rounding', 'truthiness'])

K.lesson('naming', 'Naming rules and good names', f'''
{table(['Rule', 'Valid', 'Not valid'], [
    ['Letters, digits and underscores only', 'total_2', 'total-2, total 2'],
    ['Must not start with a digit', 'price2', '2price'],
    ['Must not be a keyword', 'klass, class_', 'class, for, None'],
    ['Case matters', 'Total and total are two different names', ''],
    ['Letters from any language are allowed', 'año, naam', '']])}
{run('naming')}
{versus('Names that help and names that hurt', ['', 'Good', 'Poor'], [
    ['Says what it holds', 'total_price, student_count', 'x, tp, data2'],
    ['Follows PEP 8', 'snake_case for variables', 'TotalPrice for a variable (that style is for classes)'],
    ['Avoids built in names', 'items, values', 'list, str, sum (they hide the built in functions)']],
    'a good name saves a reader from having to guess, so it is worth a few more letters.')}
{note('Naming a variable list or str hides the built in. After list = [1, 2], calling list("abc") fails with TypeError: \'list\' object is not callable.', 'warn')}
''', kw=['naming rules', 'identifier', 'isidentifier', 'case sensitive', 'snake_case', 'shadowing built ins'])

K.lesson('assigning', 'More ways to assign', f'''
{run('swap')}
{table(['Form', 'Meaning'], [
    ['a, b = 1, 2', 'Two names at once. The right side is a tuple that is unpacked'],
    ['a, b = b, a', 'Swap. The right side is worked out fully before any name changes'],
    ['x = y = 0', 'Both names point to the same object 0'],
    ['n += 1', 'Augmented assignment, n = n + 1. Also -=, *=, /=, //=, %=, **='],
    ['total: int = 0', 'A type hint. Python does not check it, tools like mypy do (Advanced 3.1)']])}
{deep('what swap does inside', '<p>a, b = b, a first evaluates b and a and packs them into a temporary tuple, then unpacks the tuple into a and b. CPython optimises the two name case with a SWAP bytecode instruction instead of building a real tuple, but the meaning is the same.</p>')}
''', kw=['multiple assignment', 'unpacking', 'swap', 'chained assignment', 'augmented assignment', 'type hint'])

K.lesson('compare', 'How Python variables compare with other languages', f'''
{versus('Variables in three languages', ['', 'Python', 'C', 'Java'], [
    ['Type belongs to', 'The object (dynamic typing)', 'The variable, fixed when declared', 'The variable, fixed when declared'],
    ['Declare first?', 'No, the first assignment creates the name', 'Yes: <code>int age;</code>', 'Yes: <code>int age;</code>'],
    ['What a variable holds', 'A reference to an object', 'The value itself, in a box of fixed size', 'A value (primitives) or a reference (objects)'],
    ['Int size', 'Unlimited', '32 or 64 bits, can overflow', '32 bits (int) or 64 bits (long)'],
    ['Type errors found', 'When the line runs, or earlier with mypy', 'When compiling', 'When compiling']],
    'Python is quicker to write and change, C and Java catch more mistakes before running. Type hints with mypy give Python some of that safety when a project grows.')}
''', kw=['dynamic typing', 'static typing', 'Python vs Java', 'Python vs C', 'reference'])

K.lesson('maths', 'The maths: place value and conversions', f'''
{fxs(fx('Base b to decimal', 'N = &sum;<sub>i=0</sub><sup>k</sup> d<sub>i</sub> &middot; b<sup>i</sup>', 'd<sub>i</sub> is the digit at position i from the right.', key=True),
     fx('Decimal to base b', 'd<sub>0</sub> = N mod b, N &larr; N // b, repeat', 'The remainders in reverse order are the digits.', key=True),
     fx('Largest number in k bits', '2<sup>k</sup> &minus; 1', '8 bits hold 0 to 255. 16 bits hold 0 to 65,535.'),
     fx('One hex digit', '= 4 bits, one octal digit = 3 bits', 'So 0xFF is 1111 1111 and 0o7 is 111.'))}
{steps('Worked example: 0x2F to decimal', [
    '2F has digits 2 and F. F means 15.',
    'Position 1: 2 &times; 16<sup>1</sup> = 32.',
    'Position 0: 15 &times; 16<sup>0</sup> = 15.',
    eq('32 + 15 = 47')])}
{steps('Worked example: 45 to binary', [
    '45 // 2 = 22 remainder 1. 22 // 2 = 11 remainder 0.',
    '11 // 2 = 5 remainder 1. 5 // 2 = 2 remainder 1.',
    '2 // 2 = 1 remainder 0. 1 // 2 = 0 remainder 1.',
    eq('Read upwards: 101101, so bin(45) is "0b101101"')])}
''', kw=['place value', 'base conversion', 'powers of 2', 'hex digit 4 bits'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A variable is a name tag on a value. You can move the tag to another value at any time.</p>',
    '<p>Every value is an object with an id, a type and a value. Assignment binds a name to an object and never copies it. int, float, str, bool and None are immutable, so "changing" them really makes a new object.</p>',
    '<p>Names live in namespaces (dictionaries such as globals()). CPython caches the small ints from -5 to 256 and some strings, so id() can be equal for equal small values, but code must never rely on that. Use == for value, is only for None.</p>',
    '<p>CPython objects start with a reference count and a type pointer (PyObject header). An int is a PyLongObject with an array of 30 bit digits. Since 3.12 some objects are immortal (their count never changes), which matters for free threaded builds.</p>')}
{grow('Use clear names, know the six basic types and convert text with int() and float().',
      'Explain names and objects, use bin/oct/hex and int(text, base), know why int(3.99) is 3 and round(2.5) is 2.',
      'Explain small int caching, immortal objects, int digit storage and why float has about 15.95 decimal digits of precision.')}
{scene('a bank app reading an amount', '<p>A banking app reads "1,500.75" from a text box. It is text, so the app first removes the comma, then calls float() or better decimal.Decimal() for money, checks it is above zero, and only then adds it to the balance. Forgetting the conversion would join texts ("1500.75" + "100" gives "1500.75100") instead of adding numbers.</p>')}
''', kw=['beginner', 'expert', 'small int cache', 'immortal objects', 'namespace'])

lc(1281, 'Subtract the Product and Sum of Digits of an Integer', 'subtract-the-product-and-sum-of-digits-of-an-integer', 'e', 'Digits with % and //', 'Take the last digit with n % 10 and drop it with n // 10 until n is 0. Keep a product and a sum.', r'''
def subtract_product_and_sum(n):
    product = 1
    total = 0
    while n > 0:
        digit = n % 10
        product = product * digit
        total = total + digit
        n = n // 10
    return product - total
''', [('subtract_product_and_sum(234)', 15), ('subtract_product_and_sum(4421)', 21)])
lc(191, 'Number of 1 Bits', 'number-of-1-bits', 'e', 'Binary', 'bin(n) gives the binary text. Count the "1" characters in it.', r'''
def hamming_weight(n):
    return bin(n).count("1")
''', [('hamming_weight(11)', 3), ('hamming_weight(128)', 1), ('hamming_weight(2147483645)', 30)])
lc(1290, 'Convert Binary Number in a Linked List to Integer', 'convert-binary-number-in-a-linked-list-to-integer', 'e', 'Place value', 'Start with 0. For each bit, value = value * 2 + bit. Here the list is given as a Python list of bits.', r'''
def get_decimal_value(bits):
    # On LeetCode the bits come in a linked list. The idea is the same for a plain list.
    value = 0
    for bit in bits:
        value = value * 2 + bit
    return value
''', [('get_decimal_value([1, 0, 1])', 5), ('get_decimal_value([0])', 0), ('get_decimal_value([1, 1, 1, 1])', 15)])
lc(405, 'Convert a Number to Hexadecimal', 'convert-a-number-to-hexadecimal', 'e', 'Base conversion', 'For negative numbers add 2 ** 32 first (two\'s complement). Then repeat: digit = num % 16, num = num // 16.', r'''
def to_hex(num):
    if num == 0:
        return "0"
    if num < 0:
        num = num + 2 ** 32
    digits = "0123456789abcdef"
    result = ""
    while num > 0:
        result = digits[num % 16] + result
        num = num // 16
    return result
''', [('to_hex(26)', '1a'), ('to_hex(-1)', 'ffffffff'), ('to_hex(0)', '0')])
lc(504, 'Base 7', 'base-7', 'e', 'Base conversion', 'Same as base 2 but divide by 7. Handle the sign separately.', r'''
def convert_to_base7(num):
    if num == 0:
        return "0"
    sign = ""
    if num < 0:
        sign = "-"
        num = -num
    result = ""
    while num > 0:
        result = str(num % 7) + result
        num = num // 7
    return sign + result
''', [('convert_to_base7(100)', '202'), ('convert_to_base7(-7)', '-10')])

K.lesson('leetcode', 'LeetCode practice', leet(), kw=['LeetCode', 'number of 1 bits', 'base 7', 'hexadecimal'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>variable</b> is a name bound to an object. Assignment works out the right side, then sticks the name on the result. It never copies.',
    'Every object has an <b>id</b>, a <b>type</b> and a <b>value</b>. The type belongs to the object, not the name (dynamic typing).',
    'Basic types: int (any size), float (about 15 to 17 digits), complex, bool (True == 1), str and None. All of them are immutable.',
    'Literals: 1_000_000, 1.5e3, 0b1010, 0o17, 0xFF. bin(), oct(), hex() give text, int(text, base) reads it back.',
    'Conversions: int() cuts towards zero, round() rounds ties to even, bool() is False only for zero and empty values.',
    'Names: letters, digits, underscores, not starting with a digit, not a keyword, case sensitive. Use snake_case and never name a variable list or str.'],
    'Core 1.3 combines values with operators: + - * / // % **, comparisons, logic and bits.')}
{files('Three tasks: describe a value, convert between bases by hand, and clean a typed amount.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is the type of 3.0?', ['int', 'float', 'str', 'decimal'], 1, 'The decimal point.', 'Any literal with a decimal point is a float.')
K.quiz('e', 'Which name is valid in Python?', ['2nd_place', 'second-place', 'second_place', 'class'], 2, 'Rules for names.', 'Only letters, digits and underscores, not starting with a digit, not a keyword.')
K.quiz('e', 'What does int("42") + 1 give?', ['"421"', '43', '421', 'TypeError'], 1, 'int() makes a number.', 'int("42") is 42 and 42 + 1 is 43.')
K.quiz('e', 'What is 0b101 in decimal?', ['3', '5', '101', '6'], 1, '4 + 0 + 1.', '1 &times; 4 + 0 &times; 2 + 1 &times; 1 = 5.')
K.quiz('m', 'After a = 5, b = a, a = 7, what is b?', ['5', '7', '12', 'An error'], 0, 'Names move, objects stay.', 'b still points to the object 5.')
K.quiz('m', 'What does int(-2.7) give?', ['-3', '-2', '-2.7', '2'], 1, 'Towards zero.', 'int() cuts off the decimal part, so -2.7 becomes -2.')
K.quiz('m', 'What does round(2.5) give in Python 3?', ['3', '2', '2.5', '3.0'], 1, 'Ties to even.', 'Python rounds exact halves to the nearest even number.')
K.quiz('m', 'What is True + True?', ['True', '2', 'TrueTrue', 'An error'], 1, 'bool is an int.', 'True is 1, so 1 + 1 = 2.')
K.quiz('h', 'Which of these is False?', ['bool("0")', 'bool(" ")', 'bool(0.0)', 'bool([0])'], 2, 'Only zero and empty are False.', '0.0 is zero. "0", " " and [0] are not empty.')
K.quiz('h', 'What is hex(255)?', ['"FF"', '"0xff"', '0xFF', '"ff"'], 1, 'hex() gives text with a prefix.', 'hex(255) returns the string "0xff".')
K.quiz('h', 'What does 017 do in Python 3?', ['It is 15', 'It is 17', 'It is a SyntaxError', 'It is 0.17'], 2, 'Leading zeros.', 'Leading zeros on decimal ints are not allowed. Use 0o17.')
K.quiz('x', 'In the style of a Harvard CS50P question: after x = 10**20, what is type(x / 10)?', ['int', 'float', 'decimal', 'long'], 1, 'Which operator?', 'True division / always returns a float, even for huge ints.')
K.quiz('x', 'In the style of an IIT Bombay CS101 viva: why can 2 ** 200 be printed exactly in Python but not in C with a 64 bit long?', ['Python uses floats', 'CPython ints grow by adding more 30 bit digits as needed', 'Python cuts the number', 'C is broken'], 1, 'Arbitrary precision.', 'Python ints have no fixed size. A 64 bit long overflows above 2<sup>63</sup> &minus; 1.')

K.calc('e', 'Convert 0b1101 to decimal.', '13', 'Place values 8, 4, 2, 1.', ['1 &times; 8 = 8, 1 &times; 4 = 4.', '0 &times; 2 = 0, 1 &times; 1 = 1.', eq('8 + 4 + 0 + 1 = 13')], check=0b1101)
K.calc('e', 'Convert 0x1A to decimal.', '26', 'A is 10.', ['1 &times; 16 = 16.', 'A = 10.', eq('16 + 10 = 26')], check=0x1A)
K.calc('e', 'What is 1.5e3 as a number?', '1500', '1.5 &times; 1000.', ['e3 means &times; 10<sup>3</sup>.', '1.5 &times; 1000.', eq('1500.0')], check=1.5e3)
K.calc('m', 'Convert 0o755 to decimal.', '493', 'Powers of 8.', ['7 &times; 64 = 448.', '5 &times; 8 = 40, 5 &times; 1 = 5.', eq('448 + 40 + 5 = 493')], check=0o755)
K.calc('m', 'How many bits does 156 need? (156).bit_length()', '8', '2<sup>7</sup> = 128 &le; 156 &lt; 256.', ['2<sup>7</sup> = 128 and 2<sup>8</sup> = 256.', '128 &le; 156 &lt; 256.', eq('&lfloor;log<sub>2</sub> 156&rfloor; + 1 = 7 + 1 = 8')], check=(156).bit_length())
K.calc('m', 'Largest number that fits in 12 bits?', '4095', '2<sup>12</sup> &minus; 1.', ['2<sup>12</sup> = 4,096.', 'Subtract 1 because we start at 0.', eq('4,095')], check=2 ** 12 - 1)
K.calc('m', 'What is int("ff", 16) + int("11", 2)?', '258', '255 + 3.', ['ff in base 16 = 15 &times; 16 + 15 = 255.', '11 in base 2 = 3.', eq('258')], check=int('ff', 16) + int('11', 2))
K.calc('h', 'How many digits does 2 ** 100 have?', '31', 'log<sub>10</sub>(2) &asymp; 0.30103.', ['100 &times; 0.30103 = 30.103.', 'Digits = &lfloor;30.103&rfloor; + 1.', eq('31')], check=len(str(2 ** 100)))
K.calc('h', 'How many hex digits does a 64 bit number need at most?', '16', 'One hex digit is 4 bits.', ['64 bits.', 'Each hex digit holds 4 bits.', eq('64 / 4 = 16')], check=16)
K.calc('x', 'In the style of an MIT 6.004 problem: a float has a 52 bit fraction plus 1 hidden bit. About how many decimal digits is that? Give log<sub>10</sub>(2<sup>53</sup>) to 2 decimals.', '15.95', '53 &times; 0.30103.', ['53 bits of precision.', 'log<sub>10</sub>(2<sup>53</sup>) = 53 &times; log<sub>10</sub> 2.', eq('53 &times; 0.30103 = 15.95')], check=round(53 * 0.30103, 2), tol=0.01)

K.assign('describe', 'e', 'Describe a value',
         '<p>Write <code>describe(value)</code> that returns a text like "42 is an int". Use type(value).__name__ for the type name and repr(value) for the value.</p>',
         '''
def describe(value):
    # your code here
    pass
''', [('describe(42)', '42 is an int'), ('describe(3.5)', '3.5 is a float'), ('describe("hi")', "'hi' is a str"), ('describe(None)', 'None is a NoneType'), ('describe(True)', 'True is a bool')],
         '''
def describe(value):
    name = type(value).__name__
    if name[0] in "aeiou":
        article = "an"
    else:
        article = "a"
    return repr(value) + " is " + article + " " + name
''', 'Pick "an" when the type name starts with a vowel (int), otherwise "a".', '<p>repr() shows text with quotes, so a reader can tell "42" from 42.</p>')
K.assign('tobase', 'm', 'Convert to any base by hand',
         '<p>Write <code>to_base(n, base)</code> for n &ge; 0 and base from 2 to 16. Return the digits as text without a prefix, using 0 to 9 and lower case a to f. Do not use bin(), oct(), hex() or format().</p>',
         '''
def to_base(n, base):
    # your code here
    pass
''', [('to_base(156, 2)', '10011100'), ('to_base(255, 16)', 'ff'), ('to_base(493, 8)', '755'), ('to_base(0, 2)', '0'), ('to_base(100, 7)', '202')],
         '''
def to_base(n, base):
    digits = "0123456789abcdef"
    if n == 0:
        return "0"
    result = ""
    while n > 0:
        result = digits[n % base] + result
        n = n // base
    return result
''', 'Repeat: take n % base as the next digit (on the left), then n = n // base.', '<p>This is the repeated division you watched in the animation.</p>')
K.assign('amount', 'm', 'Read a typed amount',
         '<p>Write <code>read_amount(text)</code>. The text may have spaces around it and commas between thousands, for example " 1,500.75 ". Return it as a float rounded to 2 places. If the text is not a number, return None instead of crashing.</p>',
         '''
def read_amount(text):
    # your code here
    pass
''', [('read_amount(" 1,500.75 ")', 1500.75), ('read_amount("42")', 42.0), ('read_amount("abc")', None), ('read_amount("2,000,000")', 2000000.0)],
         '''
def read_amount(text):
    cleaned = text.strip().replace(",", "")
    try:
        number = float(cleaned)
    except ValueError:
        return None
    return round(number, 2)
''', 'strip() removes spaces, replace(",", "") removes commas, and try/except ValueError catches bad text.', '<p>Real apps for money use decimal.Decimal instead of float, but the cleaning steps are the same.</p>')

K.must('Names and objects', 'name = value binds a name to an object. b = a gives a second name to the same object. Objects have id, type, value.')
K.must('Basic types', 'int (unlimited), float (about 15 to 17 digits), complex, bool (subclass of int), str, None. All immutable.')
K.must('Bases', '0b, 0o, 0x literals. bin(), oct(), hex() to text. int(text, base) back. N = sum of d<sub>i</sub> b<sup>i</sup>.')
K.must('Conversions', 'int() cuts towards zero, int("3.5") is ValueError, round() ties to even, bool("0") is True.')
K.must('Naming', 'Letters, digits, _ , no leading digit, no keyword, case sensitive, snake_case, do not shadow built ins.')

T = K.topic(
    slug='py-values', topic='py-values', step=(1, 'Getting started', 'py-c1', 'What a program is, how Python runs it, values, types, operators and input and output.', 'Beginner'),
    title='Variables, values, types and numeral systems', short='Variables and types', badge='1.2', minutes=45,
    lead='Learn what x = 5 really does: names stuck on objects. Meet int, float, complex, bool, str and None, write numbers in binary, octal and hexadecimal, convert between types safely and pick good names.',
    desc='Variables as names bound to objects, id, type and value, literals and the basic types, underscores and scientific notation, binary, octal and hexadecimal, int() with a base, type conversion rules, naming rules and PEP 8, multiple and augmented assignment.',
    summary='Names and objects, the basic types and literals, numeral systems, type conversion, naming rules, multiple assignment.',
    keywords=['variables', 'data types', 'int', 'float', 'bool', 'str', 'None', 'binary', 'hexadecimal', 'octal', 'type conversion', 'casting', 'naming rules'],
    recap='<p>A variable is a name tag on an object. The object carries the type. Convert text to numbers before doing maths.</p>',
    added='2026-11-07', leet=leet_items())
