# Core Python 1.4: console input and output and string formatting. Follows PCEP-30-02 section 1.5 (print(),
# input(), sep= and end=, int() and float() on input) and adds f-strings, the format specification mini language,
# str.format() and printf style formatting from the Python 3.14 documentation (Input and Output tutorial,
# Format Specification Mini-Language, PEP 498 and PEP 701).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, term, lc, leet, files, grow, leet_items

chapter('py-io')
K = Kit()

K.code('greet', r'''
name = input("What is your name? ")
age = int(input("How old are you? "))
print("Hello,", name)
print("Next year you will be", age + 1)
''', stdin='Asha\n25\n')

K.code('many', r'''
# Several numbers typed on one line, separated by spaces
line = input("Enter three marks: ")
parts = line.split()             # ["78", "91", "64"]
a, b, c = int(parts[0]), int(parts[1]), int(parts[2])
print("Total:", a + b + c)
print("Average:", (a + b + c) / 3)

# The same in one line with map()
x, y = map(int, input("Enter two numbers: ").split())
print(x, "+", y, "=", x + y)
''', stdin='78 91 64\n12 30\n')

K.code('fstr', r'''
name, price, qty = "Notebook", 45.5, 3
print(f"{name} costs {price} rupees")
print(f"{qty} x {price} = {qty * price}")       # any expression works
print(f"{name!r} has {len(name)} letters")       # !r uses repr()
print(f"{price = }")                             # the = shows the expression too
width = 12
print(f"[{name:>{width}}]")                      # a nested value for the width
''')

K.code('spec', r'''
amount = 1234567.891
print(f"{amount:.2f}")       # 2 decimal places
print(f"{amount:,.2f}")      # thousands separator
print(f"{amount:_.0f}")      # underscore separator, no decimals
print(f"{amount:12.1f}|")    # width 12, right aligned (numbers default)
print(f"{'left':<10}|{'mid':^10}|{'right':>10}|")
print(f"{42:05d} {42:+d} {42:b} {255:x} {255:#X}")
print(f"{0.4567:.1%}  {1234.5:e}  {0.000123:.2e}")
print(f"{'Python':*^20}")
''')

K.code('table', r'''
items = [("Pen", 2, 10.0), ("Notebook", 3, 45.5), ("Bag", 1, 799.0)]
print(f"{'Item':<10}{'Qty':>5}{'Price':>10}{'Total':>10}")
print("-" * 35)
grand = 0
for name, qty, price in items:
    total = qty * price
    grand += total
    print(f"{name:<10}{qty:>5}{price:>10.2f}{total:>10.2f}")
print("-" * 35)
print(f"{'Grand total':<25}{grand:>10.2f}")
''')

K.code('old', r'''
name, score = "Ravi", 92.456
print("Name: %s, score: %.1f" % (name, score))            # printf style (oldest)
print("Name: {}, score: {:.1f}".format(name, score))      # str.format (Python 2.6+)
print("Name: {0}, again {0}, score {1:.2f}".format(name, score))
print(f"Name: {name}, score: {score:.1f}")                # f-string (Python 3.6+), the best choice
''')

K.code('robust', r'''
# Ask again until the user types a whole number
answers = iter(["ten", "-3", "12"])   # what the user types, one try at a time

def ask(prompt):
    text = next(answers)              # in a real program: text = input(prompt)
    print(prompt + text)
    return text

while True:
    text = ask("Quantity: ")
    try:
        qty = int(text)
    except ValueError:
        print("  Please type digits only.")
        continue
    if qty <= 0:
        print("  It must be more than zero.")
        continue
    break
print("You ordered", qty)
''')

K.lesson('idea', 'Input and output: how a program talks to people', f'''
{src('Python 3.14 tutorial chapter 7 (Input and Output), the Format Specification Mini-Language, and PCEP-30-02 section 1.5.')}
{wwh('<b>Output</b> is what a program shows (print). <b>Input</b> is what it reads from the user while it runs (input). Together they make the program interactive.',
     'A program that always uses the same numbers is not very useful. Reading input lets one program work for any user, any shop bill, any set of marks.',
     'input(prompt) shows the prompt, waits for the user to press Enter and returns what was typed as <b>text</b>. You convert it with int() or float() before doing maths. print() and f-strings turn values back into neat text.')}
{run('greet')}
{note('The Run button above feeds the typed answers (Asha and 25) for you. On your own computer, Python waits for you to type them.', 'tip')}
{scene('a ticket machine at a metro station', '<p>The machine shows "Choose your station" (output), you press a station (input), it shows the fare (output), you insert money (input) and it prints a ticket (output). Every interactive program, from an ATM to a quiz app, is this loop of asking, reading, working out and showing.</p>')}
''', kw=['input', 'output', 'interactive', 'prompt', 'console', 'standard input', 'standard output'])

K.lesson('inputs', 'input() always returns text', f'''
{viz('pyinput')}
{table(['You want', 'Write', 'User types', 'You get'], [
    ['Text', 'name = input("Name: ")', 'Asha', '"Asha"'],
    ['A whole number', 'n = int(input("N: "))', '42', '42'],
    ['A decimal number', 'x = float(input("X: "))', '3.5', '3.5'],
    ['Several numbers on one line', 'a, b = map(int, input().split())', '4 9', '4 and 9'],
    ['Yes or no', 'ok = input("y/n? ").strip().lower() == "y"', ' Y ', 'True']])}
{run('many')}
{note('input() returns text even when the user types digits. "5" + "5" is "55". Convert first, then calculate.', 'warn')}
''', kw=['input()', 'int(input())', 'float(input())', 'split', 'map', 'strip', 'lower', 'TypeError'])

K.lesson('fstrings', 'f-strings: the modern way to build text', f'''
{wwh('An f-string is a text with an f before the quotes: <code>f"Total: {{total}}"</code>. Anything inside curly brackets is worked out and put into the text.',
     'Joining texts with + and str() is long and easy to get wrong ("Total: " + str(total)). f-strings are shorter, easier to read and also the fastest way.',
     'Python finds each {{...}} field, works out the expression, formats it with the optional spec after a colon, and joins all the pieces.')}
{run('fstr')}
{table(['Inside the brackets', 'Meaning', 'Example', 'Gives'], [
    ['{{x}}', 'The value as str(x)', 'f"{{3 * 4}}"', '12'],
    ['{{x!r}}', 'repr(x), shows quotes on text', 'f"{{\'hi\'!r}}"', "'hi'"],
    ['{{x = }}', 'The expression text, then the value (Python 3.8+)', 'f"{{price = }}"', 'price = 45.5'],
    ['{{x:spec}}', 'Formatted with a format spec', 'f"{{3.14159:.2f}}"', '3.14'],
    ['{{{{ and }}}}', 'A real curly bracket', 'f"{{{{x}}}}"', '{{x}}']])}
{note('Since Python 3.12 (PEP 701) you may reuse the same quotes inside an f-string expression, for example f"{{", ".join(names)}}". Older versions need the other kind of quote inside.', 'tip')}
''', kw=['f-string', 'formatted string literal', 'interpolation', 'repr', 'self documenting expression', 'PEP 498', 'PEP 701'])

K.lesson('spec', 'The format spec: width, alignment, decimals and more', f'''
{viz('pyfmt')}
{fxs(fx('Format spec grammar', '[[fill]align][sign][#][0][width][grouping][.precision][type]', 'Every part is optional, but the order is fixed. align is &lt; &gt; ^ or =.', key=True),
     fx('Common types', 'd (int), f (fixed), e (scientific), % (percent), b o x X (bases), s (text)', 'No type means the same as str() for most values.'))}
{run('spec')}
{run('table')}
{note('.2f rounds the stored binary value, and exact halves go to the even digit: f"{{2.5:.0f}}" gives 2 and f"{{2.675:.2f}}" gives 2.67.', 'exam')}
''', kw=['format spec', 'mini language', 'width', 'align', 'fill', 'precision', 'thousands separator', 'percent', 'scientific notation', 'table output'])

K.lesson('older', 'Older ways: % formatting and str.format()', f'''
{run('old')}
{versus('Three ways to format text', ['', '% formatting', 'str.format()', 'f-string'], [
    ['Looks like', '"%s is %d" % (name, age)', '"{{}} is {{}}".format(name, age)', 'f"{{name}} is {{age}}"'],
    ['Since', 'Python 1 (copied from C printf)', 'Python 2.6', 'Python 3.6'],
    ['Readability', 'Values far from their places', 'Better, numbered or named fields', 'Best, values sit in place'],
    ['Speed', 'Medium', 'Slowest', 'Fastest'],
    ['Still useful for', 'logging messages: log.info("%s", x)', 'templates stored as data, built before the values exist', 'almost everything else']],
    'use f-strings in new code. Recognise the other two because you will meet them in older code and in exams.')}
''', kw=['percent formatting', 'printf style', 'str.format', 'positional fields', 'logging'])

K.lesson('robust', 'Reading input safely', f'''
<p>Users make typing mistakes. A good program checks the input and asks again instead of crashing with a ValueError.</p>
{run('robust')}
{steps('The ask again pattern', [
    'Loop for ever with while True.',
    'Read the text and try to convert it inside try.',
    'On ValueError, explain the problem and continue (go back to the top of the loop).',
    'If the number is out of range, explain and continue.',
    eq('Only a good value reaches break, which leaves the loop')])}
{note('Loops arrive in Core 2.2 and try/except in Core 5.1. You can use this pattern now and understand every line later.', 'tip')}
''', kw=['input validation', 'try except ValueError', 'while True', 'ask again', 'robust input'])

K.lesson('streams', 'Where input and output really go', f'''
{table(['Stream', 'Python name', 'Normally', 'Used by'], [
    ['Standard input', 'sys.stdin', 'The keyboard', 'input()'],
    ['Standard output', 'sys.stdout', 'The screen', 'print()'],
    ['Standard error', 'sys.stderr', 'The screen, often in red', 'Tracebacks, print(..., file=sys.stderr)']])}
{term(['$ python3 bill.py < answers.txt > result.txt', '$ python3 bill.py | sort', '$ python3 bill.py 2> errors.txt'], 'Redirecting the streams in a terminal')}
{deep('why input() is slow in competitive programming', '<p>input() reads one line at a time and does extra work for the prompt. For a million lines, sys.stdin.readline() or sys.stdin.read().split() is several times faster. Competitive programmers often write input = sys.stdin.readline at the top of their file.</p>')}
''', kw=['stdin', 'stdout', 'stderr', 'redirect', 'pipe', 'sys.stdin.readline'])

K.lesson('maths', 'The maths: widths and rounding', f'''
{fxs(fx('Padding added by a width', 'pad = max(0, width &minus; len(text))', 'Width is a minimum. It never cuts the text.', key=True),
     fx('Centre alignment', 'left = &lfloor;pad / 2&rfloor;, right = pad &minus; left', 'With an odd pad the extra character goes on the right.', key=True),
     fx('Rounding to p places', 'round half to even on the exact binary value', 'f"{{0.125:.2f}}" is 0.12 because 0.125 is exact and 2 is even.'),
     fx('Digits of a number', 'len(str(n)) = &lfloor;log<sub>10</sub> n&rfloor; + 1', 'For a whole number n &gt; 0.'))}
{steps('Worked example: f"{{\'Menu\':*^11}}"', [
    'The text Menu has 4 characters.',
    'pad = 11 &minus; 4 = 7.',
    'left = 7 // 2 = 3, right = 7 &minus; 3 = 4.',
    eq('***Menu****')])}
''', kw=['width', 'padding', 'centre', 'rounding', 'half to even'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>input() asks a question and gives you the answer as text. f-strings let you put values into a sentence.</p>',
    '<p>Convert input with int() or float(), split lines with split(). Use the format spec for width, alignment, decimals and separators. Check input with try and a loop.</p>',
    '<p>f-strings compile to fast bytecode (FORMAT_VALUE, BUILD_STRING). The spec is passed to the value\'s __format__ method, so dates, Decimal and your own classes can define their own codes, for example f"{{today:%d %B %Y}}".</p>',
    '<p>Python 3.14 adds template strings (t-strings, PEP 750): t"..." gives a Template object with the static parts and the values kept apart, so a library can escape values safely for HTML or SQL before joining them.</p>')}
{grow('Read a name and a number, and print a sentence with an f-string.',
      'Format a bill as a neat table and keep asking until the input is valid.',
      'Write __format__ for your own class and explain why t-strings help against injection.')}
{scene('printing a pay slip', '<p>A payroll script reads hours and rate for each worker, works out the pay and prints a pay slip where every column lines up: names left aligned in 15 characters, amounts right aligned with two decimals and thousands separators. This is exactly f"{{name:&lt;15}}{{pay:&gt;12,.2f}}". Without widths, columns zigzag and the slip is hard to check.</p>')}
''', kw=['beginner', 'expert', '__format__', 't-strings', 'PEP 750'])

lc(412, 'Fizz Buzz', 'fizz-buzz', 'e', 'Modulo and building text', 'Check divisible by 15 first, then 3, then 5. Build a list of texts.', r'''
def fizz_buzz(n):
    answer = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            answer.append("FizzBuzz")
        elif i % 3 == 0:
            answer.append("Fizz")
        elif i % 5 == 0:
            answer.append("Buzz")
        else:
            answer.append(str(i))
    return answer
''', [('fizz_buzz(5)', ['1', '2', 'Fizz', '4', 'Buzz']), ('fizz_buzz(15)[-1]', 'FizzBuzz')])
lc(709, 'To Lower Case', 'to-lower-case', 'e', 'Character codes', 'Without lower(): for "A" to "Z" add 32 to the character code with ord() and chr().', r'''
def to_lower_case(s):
    result = ""
    for ch in s:
        if "A" <= ch <= "Z":
            result = result + chr(ord(ch) + 32)
        else:
            result = result + ch
    return result
''', [('to_lower_case("Hello")', 'hello'), ('to_lower_case("LOVELY")', 'lovely')])
lc(1678, 'Goal Parser Interpretation', 'goal-parser-interpretation', 'e', 'Text replace', 'Replace "()" with "o" and then "(al)" with "al".', r'''
def interpret(command):
    return command.replace("()", "o").replace("(al)", "al")
''', [('interpret("G()(al)")', 'Goal'), ('interpret("G()()()()(al)")', 'Gooooal')])
lc(2864, 'Maximum Odd Binary Number', 'maximum-odd-binary-number', 'e', 'Counting and building text', 'Keep one "1" for the end (odd). Put all other 1s at the front, then the 0s.', r'''
def maximum_odd_binary_number(s):
    ones = s.count("1")
    zeros = len(s) - ones
    return "1" * (ones - 1) + "0" * zeros + "1"
''', [('maximum_odd_binary_number("010")', '001'), ('maximum_odd_binary_number("0101")', '1001')])

K.lesson('leetcode', 'LeetCode practice', leet(), kw=['LeetCode', 'fizz buzz', 'to lower case'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>input(prompt)</b> shows the prompt, waits for Enter and returns <b>text</b>. Use int() or float() before doing maths.',
    'Several values on one line: a, b = map(int, input().split()).',
    '<b>f-strings</b> put values into text: f"{{name}} is {{age}}". {{x!r}} uses repr, {{x = }} shows the expression too.',
    'Format spec: [[fill]align][sign][#][0][width][grouping][.precision][type], for example {{amount:&gt;12,.2f}}.',
    'Width is a minimum, centre puts the extra pad on the right, rounding goes half to even on the stored value.',
    '% formatting and str.format() are older. Know them, but use f-strings in new code.',
    'Check input in a loop with try and except ValueError, so typing mistakes do not crash the program.'],
    'Core 2.1 makes decisions with if, elif, else and match.')}
{files('Three tasks: format a price line, centre a title by hand, and parse a line of numbers.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What type does input() return?', ['int', 'str', 'float', 'It depends on what is typed'], 1, 'Always the same.', 'input() always returns text.')
K.quiz('e', 'name = "Asha". What does f"Hi {name}!" give?', ['Hi {name}!', 'Hi Asha!', 'Hi name!', 'An error'], 1, 'The brackets are filled in.', 'The f makes Python put the value of name in place.')
K.quiz('e', 'What does f"{3.14159:.2f}" give?', ['3.14', '3.1', '3.14159', '3.15'], 0, 'Two decimal places.', '.2f keeps two digits after the point.')
K.quiz('m', 'The user types 5. What does input() + input() print if both answers are 5?', ['10', '55', 'TypeError', '5 5'], 1, 'Text plus text.', '"5" + "5" joins the texts.')
K.quiz('m', 'What does f"{42:05d}" give?', ['42000', '00042', '   42', '42   '], 1, 'Zero padding.', 'Width 5, padded with zeros on the left.')
K.quiz('m', 'What does f"{\'ab\':^6}" give?', ['"ab    "', '"  ab  "', '"    ab"', '" ab   "'], 1, 'Centre.', 'pad = 4, 2 on each side.')
K.quiz('m', 'What does "%s scored %d" % ("Ravi", 9.8) give?', ['Ravi scored 9.8', 'Ravi scored 9', 'Ravi scored 10', 'TypeError'], 1, '%d is a whole number.', '%d turns 9.8 into 9 by cutting off the decimals.')
K.quiz('h', 'What does f"{2.5:.0f}" give?', ['3', '2', '2.5', '3.0'], 1, 'Half to even.', '2.5 is exact, and the tie goes to the even number 2.')
K.quiz('h', 'What does f"{1234567:,}" give?', ['1234567', '1,234,567', '1.234.567', '12,34,567'], 1, 'Grouping.', 'A comma every three digits from the right.')
K.quiz('h', 'What does print(f"{x = }") show when x = 7?', ['7', 'x = 7', '{x = 7}', 'x=7'], 1, 'The = specifier.', 'It shows the expression text, then the value, keeping the spaces.')
K.quiz('x', 'In the style of a UC Berkeley CS61A question: what is len(f"{-3.14159:+010.2f}")?', ['8', '10', '11', '6'], 1, 'Width is the full length.', 'The result is -000003.14, exactly 10 characters, with = alignment padding after the sign.')
K.quiz('x', 'In the style of an ETH Zurich exam: a, b = map(int, input().split()) and the user types "1 2 3". What happens?', ['a = 1, b = 2', 'a = 1, b = 23', 'ValueError: too many values to unpack', 'TypeError'], 2, 'Three values, two names.', 'map gives 3 values but only 2 names wait for them.')

K.calc('e', 'Characters in f"{7:4d}"?', '4', 'Width 4.', ['7 has 1 character.', 'Width 4 adds 3 spaces.', eq('4')], check=len(f'{7:4d}'))
K.calc('e', 'How many decimal digits does f"{1/3:.5f}" show after the point?', '5', '.5f.', ['.5 means 5 digits.', 'f means fixed point.', eq('0.33333 has 5')], check=5)
K.calc('e', 'Padding added to "cat" with width 10?', '7', 'width &minus; len.', ['len("cat") = 3.', '10 &minus; 3.', eq('7')], check=7)
K.calc('m', 'Left padding when centring "Menu" in width 11?', '3', '&lfloor;pad / 2&rfloor;.', ['pad = 11 &minus; 4 = 7.', '7 // 2 = 3.', eq('3 on the left, 4 on the right')], check=3)
K.calc('m', 'Length of f"{1234567.891:,.2f}"?', '12', '1,234,567.89.', ['Digits before the point: 7, plus 2 commas = 9.', 'Point and 2 decimals: 3.', eq('12')], check=len(f'{1234567.891:,.2f}'))
K.calc('m', 'What number does f"{0.4567:.1%}" show (without the % sign)?', '45.7', '&times; 100, 1 decimal.', ['0.4567 &times; 100 = 45.67.', 'One decimal place.', eq('45.7')], check=45.7)
K.calc('m', 'Length of the header line f"{\'Item\':<10}{\'Qty\':>5}{\'Price\':>10}{\'Total\':>10}"?', '35', 'Widths add up.', ['10 + 5 = 15.', '15 + 10 + 10.', eq('35')], check=35)
K.calc('h', 'The user types "78 91 64". What is the average printed with :.2f?', '77.67', 'Sum 233.', ['78 + 91 + 64 = 233.', '233 / 3 = 77.666...', eq('77.67')], check=round(233 / 3, 2))
K.calc('h', 'How many characters does f"{255:#010b}" have?', '10', 'Width includes the 0b prefix.', ['255 in binary is 11111111 (8 digits).', 'With 0b that is 10 characters.', eq('width 10 adds nothing: 0b11111111')], check=len(f'{255:#010b}'))
K.calc('x', 'In the style of a Cambridge Part IA problem: a report prints n numbers, each with f"{x:>8.2f}" and one space after. How many characters for n = 25, without the final new line?', '225', '9 per number.', ['Each number takes 8 characters.', 'Plus 1 space: 9.', eq('25 &times; 9 = 225')], check=225)

K.assign('price', 'e', 'One line of a bill',
         '<p>Write <code>bill_line(item, qty, price)</code> that returns the item left aligned in 10 characters, qty right aligned in 4, and qty &times; price right aligned in 10 with 2 decimals. Use one f-string.</p>',
         '''
def bill_line(item, qty, price):
    # your code here
    pass
''', [('bill_line("Pen", 2, 10)', 'Pen          2     20.00'), ('bill_line("Notebook", 3, 45.5)', 'Notebook     3    136.50')],
         '''
def bill_line(item, qty, price):
    return f"{item:<10}{qty:>4}{qty * price:>10.2f}"
''', 'Three fields: {item:&lt;10}, {qty:&gt;4} and {qty * price:&gt;10.2f}.', '<p>Every line has the same length (24 characters), so a whole bill lines up.</p>')
K.assign('centre', 'm', 'Centre a title by hand',
         '<p>Write <code>centre(text, width, fill)</code> that does the same as f"{text:{fill}^{width}}" but without format specs: work out the padding yourself.</p>',
         '''
def centre(text, width, fill):
    # your code here
    pass
''', [('centre("Menu", 11, "*")', '***Menu****'), ('centre("ab", 6, "-")', '--ab--'), ('centre("long text", 4, "*")', 'long text')],
         '''
def centre(text, width, fill):
    pad = width - len(text)
    if pad <= 0:
        return text
    left = pad // 2
    right = pad - left
    return fill * left + text + fill * right
''', 'pad = width - len(text). left = pad // 2, right = pad - left.', '<p>Python puts the extra character on the right when pad is odd, and so do we.</p>')
K.assign('parse', 'm', 'Read a line of marks',
         '<p>Write <code>marks_report(line)</code>. line holds whole numbers separated by spaces, for example "78 91 64". Return f"Total {{t}}, average {{a:.2f}}". Return "No marks" for an empty or blank line.</p>',
         '''
def marks_report(line):
    # your code here
    pass
''', [('marks_report("78 91 64")', 'Total 233, average 77.67'), ('marks_report("  ")', 'No marks'), ('marks_report("100")', 'Total 100, average 100.00')],
         '''
def marks_report(line):
    parts = line.split()
    if len(parts) == 0:
        return "No marks"
    total = 0
    for p in parts:
        total = total + int(p)
    average = total / len(parts)
    return f"Total {total}, average {average:.2f}"
''', 'split() with no argument splits on any spaces and drops empty pieces.', '<p>This is the same work a program does after reading a line with input().</p>')

K.must('input()', 'Shows a prompt, waits, returns text. Convert with int() or float(). a, b = map(int, input().split()).')
K.must('f-strings', 'f"{expr}", {x!r}, {x = }, {x:spec}. {{ and }} for real brackets.')
K.must('Format spec', '[[fill]align][sign][#][0][width][grouping][.precision][type]. Width is a minimum. .2f rounds half to even.')
K.must('Older formatting', '"%s %d" % (a, b) and "{} {}".format(a, b). Prefer f-strings.')
K.must('Safe input', 'while True + try int(text) except ValueError + range check + break.')

T = K.topic(
    slug='py-io', topic='py-io', step=(1, 'Getting started', 'py-c1', 'What a program is, how Python runs it, values, types, operators and input and output.', 'Beginner'),
    title='Input, output and formatting text', short='Input and output', badge='1.4', minutes=45,
    lead='Make programs that talk with people. Read input and convert it safely, then format output like a pro with f-strings and the format spec: widths, alignment, decimals, separators, percentages and tables.',
    desc='input() returns text, int() and float() on input, split and map, f-strings with !r and =, the format specification mini language, tables with aligned columns, percent formatting and str.format, safe input loops, standard streams and redirection, rounding and widths.',
    summary='input() and conversion, split and map, f-strings, the format spec, tables, older formatting, safe input.',
    keywords=['input', 'output', 'f-string', 'format spec', 'str.format', 'percent formatting', 'split', 'map', 'stdin', 'stdout', 'PCEP'],
    recap='<p>input() gives text, so convert it. f-strings and the format spec turn values into neat, lined up text.</p>',
    added='2026-11-07', leet=leet_items())
