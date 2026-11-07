# Core Python 1.1: what a program is, how Python runs it, the first program, print(), keywords, comments,
# indentation and the three kinds of errors. Follows PCEP-30-02 section 1.1 and 1.2 (interpreter, compiler, lexis,
# syntax, semantics, keywords, instructions, indentation, comments) and 1.5 (print with sep and end).
# Facts checked against the Python 3.14 documentation (keyword module, print(), the tutorial chapters 2 and 3) and
# PEP 8 and PEP 20.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, show, term, lc, leet, files, grow, leet_items

chapter('py-start')
K = Kit()

K.code('hello', r'''
# My first Python program
print("Hello, world!")
print("I am learning Python.")
print(2 + 3)
''')

K.code('sepend', r'''
# sep goes between the values, end goes after the last one
print("Asha", "Ravi", "Meera")
print("Asha", "Ravi", "Meera", sep=", ")
print("2026", "11", "07", sep="-")
print("Loading", end="")
print("...", end="")
print(" done")
print()                     # an empty print() prints just a new line
print("price:", 40, "rupees", sep=" | ")
''')

K.code('keywords', r'''
import keyword

print("Python has", len(keyword.kwlist), "keywords:")
print(keyword.kwlist)
print("Soft keywords:", keyword.softkwlist)
print("Is 'class' a keyword?", keyword.iskeyword("class"))
print("Is 'print' a keyword?", keyword.iskeyword("print"))
''')

K.code('indent', r'''
# Indentation (spaces at the start of a line) shows which lines belong together
marks = 72
if marks >= 40:
    print("You passed")         # inside the if, 4 spaces
    print("Well done")          # also inside the if
print("This line always runs")  # back to no spaces, outside the if
''')

K.code('errors', r'''
# compile() checks the grammar of some code without running it.
# We use it here so that this program itself does not stop.
good = 'print("Hi")'
bad = 'print("Hi"'

for source in [good, bad]:
    try:
        compile(source, "test.py", "exec")
        print(source, " -> the grammar is fine")
    except SyntaxError as error:
        print(source, " -> SyntaxError:", error.msg)

# A runtime error only happens when the line runs
try:
    print(10 / 0)
except ZeroDivisionError as error:
    print("Runtime error:", error)
''')

K.code('zen', r'''
# The Zen of Python (PEP 20): 19 short rules for writing good Python
import this
''')

K.code('count', r'''
# How many characters does a print() write? Count them, then check with len()
values = ["Total", 3, "apples"]
sep = " "
end = "\n"

text = sep.join(str(v) for v in values) + end
by_formula = sum(len(str(v)) for v in values) + (len(values) - 1) * len(sep) + len(end)
print(repr(text))
print("len(text) =", len(text))
print("formula   =", by_formula)
''')

K.lesson('idea', 'What a program is', f'''
{src('Python 3.14 tutorial, chapters 1 to 3, and the PCEP-30-02 syllabus, section 1.1.')}
<p>A computer is very fast but it has no common sense. It does exactly what it is told, one small step at a time. A <b>program</b> is a list of those steps, written down so that the computer can follow them.</p>
{scene('a recipe in the kitchen', '<p>A recipe says: boil water, add rice, wait 15 minutes, switch off the stove. A cook follows the steps in order. If a step is missing ("add rice" is not written), the rice never goes in. If a step is wrong ("wait 150 minutes"), the cook still follows it and the rice burns. A computer is a cook who follows every line exactly, even a silly one.</p>')}
{wwh('A program is a set of instructions written in a <b>programming language</b>. Python is one such language. Its instructions look close to plain English, for example <code>print("Hello")</code>.',
     'The chip inside a computer only understands <b>machine code</b>: long rows of 0s and 1s. People cannot write large programs in 0s and 1s without mistakes, so we write in a language people can read, and let a tool translate it.',
     'You write the steps in a text file that ends in <code>.py</code>. A program called the <b>Python interpreter</b> reads the file, checks it, translates it, and runs it line by line from the top.')}
<h3>Three words every programmer uses</h3>
{table(['Word', 'Meaning', 'In everyday language'], [
    ['Lexis', 'The words and symbols a language allows (print, if, +, "text")', 'The vocabulary of English'],
    ['Syntax', 'The grammar rules: how words may be put together', '"I rice eat" breaks English grammar'],
    ['Semantics', 'What a correct sentence means', '"The stone ate the rice" has good grammar but makes no sense']])}
<p>Python is popular because its lexis is small, its syntax is clean, and the same code runs on Windows, macOS, Linux, phones and even inside a web browser. It is used for websites (Instagram is built on Django), data science, artificial intelligence, test automation and small scripts that save people hours of boring work.</p>
''', kw=['program', 'instructions', 'programming language', 'machine code', 'lexis', 'syntax', 'semantics', 'why Python'])

K.lesson('translate', 'Compiler, interpreter and how Python runs your file', f'''
<p>Code written by people must be translated into something the machine can run. There are two classic ways to translate.</p>
{versus('Two ways to translate a program', ['', 'Compiler', 'Interpreter'], [
    ['How it works', 'Translates the whole program first into a separate machine code file, then you run that file', 'Reads the program and runs it straight away, statement by statement'],
    ['Like', 'Translating a full book into Hindi, printing it, then reading it', 'A live interpreter at a meeting who translates each sentence as it is spoken'],
    ['When errors show', 'Most mistakes are found before anything runs', 'A mistake is found when Python reaches that line (except grammar mistakes, see below)'],
    ['Speed', 'Usually faster to run', 'Usually slower, but you see results at once'],
    ['Examples', 'C, C++, Go, Rust', 'Python, JavaScript in old browsers, shell scripts']],
    'CPython, the standard Python, does a bit of both. It first <b>compiles</b> your file into <b>bytecode</b> (simple instructions for a virtual machine), then its <b>interpreter loop</b> runs that bytecode. Because the compile step comes first, a grammar mistake anywhere in the file stops the program before line 1 runs.')}
{steps('What happens when you type python3 hello.py', [
    'Python opens hello.py and reads the text.',
    'It splits the text into tokens (words, numbers, symbols) and checks the grammar. A grammar mistake here gives a SyntaxError and nothing runs.',
    'It compiles the grammar tree into bytecode, small instructions such as LOAD_CONST and CALL.',
    'The Python virtual machine runs the bytecode from top to bottom. print() sends text to the screen.',
    eq('source code (.py) &rarr; tokens &rarr; syntax tree &rarr; bytecode &rarr; run &rarr; output')])}
{note('Python is often called an interpreted language, but CPython does compile your code to bytecode first. Both words are partly true. The Advanced Python step 7 chapter "How Python runs" opens every one of these stages with an animation.', 'tip')}
{table(['Python implementation', 'Written in', 'Where it is used'], [
    ['CPython', 'C', 'The standard one from python.org. This course uses CPython 3.14'],
    ['PyPy', 'Python (RPython)', 'Has a just in time compiler, often several times faster on long loops'],
    ['MicroPython', 'C', 'Small boards like the Raspberry Pi Pico and ESP32'],
    ['Pyodide', 'CPython compiled to WebAssembly', 'Runs Python inside your web browser. The Run buttons on this page use it']])}
''', kw=['compiler', 'interpreter', 'CPython', 'bytecode', 'virtual machine', 'PyPy', 'MicroPython', 'Pyodide'])

K.lesson('setup', 'Install Python and run your first program', f'''
<p>You can try every example on this page with the <b>Run</b> button, which runs real Python in your browser. To work on your own computer, install Python once.</p>
{steps('Install Python', [
    'Go to python.org/downloads and download the newest Python 3 for your system (Windows, macOS or Linux). On Linux it is often already installed.',
    'On Windows, tick "Add python.exe to PATH" in the installer. This lets you type python in any terminal.',
    'Open a terminal (Command Prompt, PowerShell or Terminal) and type python3 --version (on Windows: python --version or py --version).',
    eq('If you see a version such as Python 3.14.0, Python is ready')])}
{term(['$ python3 --version', 'Python 3.14.6', '$ python3', '>>> 2 + 3', '5', '>>> print("Hello")', 'Hello', '>>> exit()', '$ python3 hello.py', 'Hello, world!'], 'Two ways to run Python')}
{table(['Way to run', 'What it is', 'Good for'], [
    ['Interactive mode (REPL)', 'Type python3 with no file. The prompt &gt;&gt;&gt; waits for one line, runs it and shows the result at once', 'Quick tests, like a calculator'],
    ['Script mode', 'Save lines in a .py file and run python3 file.py', 'Real programs you want to keep and run again'],
    ['An editor or IDE', 'IDLE (comes with Python), VS Code, PyCharm, Thonny', 'Writing, running and debugging bigger programs'],
    ['A notebook', 'Jupyter or Google Colab: code cells and notes in one page', 'Data science and learning']])}
{run('hello')}
{note('In the REPL, typing 2 + 3 shows 5 without print(). In a .py file, nothing appears unless you call print(). Beginners often expect the REPL behaviour inside a file.', 'warn')}
''', kw=['install Python', 'python.org', 'PATH', 'REPL', 'interactive mode', 'script mode', 'IDLE', 'VS Code', 'version'])

K.lesson('print', 'print(): showing results on the screen', f'''
{wwh('print() is a built in <b>function</b>. A function is a named action. You give it values inside the round brackets (called <b>arguments</b>) and it writes them on the screen.',
     'A program that shows nothing is useless to a person. print() is how a program talks back: results, messages, and while learning, what is happening inside.',
     'print() turns each argument into text with str(), joins the texts with <b>sep</b> (a space unless you say otherwise), adds <b>end</b> (a new line unless you say otherwise), and writes the result.')}
{fxs(fx('The full form of print()', 'print(*values, sep=" ", end="&#92;n", file=sys.stdout, flush=False)', 'values: any number of values. sep: text between them. end: text after the last one. file: where to write. flush: write at once.', key=True),
     fx('Characters written by one print()', 'N = &sum; len(str(v<sub>i</sub>)) + (n &minus; 1) &middot; len(sep) + len(end)', 'n values v<sub>1</sub> to v<sub>n</sub>. There are n &minus; 1 gaps between n values.', key=True))}
{viz('pyprint')}
{run('sepend')}
{table(['You write', 'The screen shows'], [
    ['print("A", "B")', 'A B'],
    ['print("A", "B", sep="")', 'AB'],
    ['print("A", end=""), then print("B")', 'AB'],
    ['print("A", "B", sep="-", end="!")', 'A-B!'],
    ['print()', 'an empty line'],
    ['print(3 + 4, "3 + 4")', '7 3 + 4']])}
{note('sep and end must be given by name (keyword arguments). print("A", "B", "-") prints A B - with the dash as a third value, it does not change sep.', 'exam')}
''', kw=['print', 'function', 'argument', 'sep', 'end', 'new line', 'str', 'keyword argument', 'flush'])

K.lesson('structure', 'Keywords, statements, comments and indentation', f'''
<p>A Python program is made of <b>statements</b>, normally one per line. Some words have a fixed meaning in the language. They are called <b>keywords</b> and you cannot use them as names for your own things.</p>
{run('keywords')}
{table(['Part', 'What it is', 'Example'], [
    ['Keyword', 'A reserved word with a fixed job. Python 3.14 has 35 of them', 'if, else, for, while, def, class, return, True, None'],
    ['Soft keyword', 'A word that is a keyword only in one place, and a normal name everywhere else', 'match, case, type, _'],
    ['Statement', 'One complete instruction', 'price = 120'],
    ['Comment', 'Text after # that Python ignores. It is a note for people', '# add the tax'],
    ['Indentation', 'Spaces at the start of a line. They show which lines belong to a block', '4 spaces under an if'],
    ['Docstring', 'A text in triple quotes at the top of a file or function that explains it', '"""Works out the bill."""']])}
{run('indent')}
{note('Python uses indentation where many languages use curly brackets. Mixing tabs and spaces, or using 3 spaces on one line and 4 on the next, gives IndentationError. PEP 8 says: always 4 spaces.', 'warn')}
{deep('why indentation instead of brackets', '<p>Guido van Rossum took the idea from the ABC language. People already indent code to read it, so making the indentation itself the rule removes a whole class of bugs where the brackets say one thing and the indentation says another. The tokenizer turns a deeper indent into an INDENT token and a shallower one into DEDENT tokens, so the parser sees blocks just as clearly as with brackets.</p>')}
''', kw=['keywords', 'keyword.kwlist', 'soft keywords', 'statement', 'comment', 'indentation', 'IndentationError', 'docstring', 'block'])

K.lesson('errors', 'Three kinds of errors', f'''
<p>Everyone makes mistakes in code, even experts, every day. What matters is knowing which kind of mistake you made, because each kind is found in a different way.</p>
{viz('pyerrors')}
{table(['Kind', 'When Python finds it', 'Example', 'What you see'], [
    ['Syntax error', 'Before anything runs, while checking the grammar of the whole file', 'print("Hi"', 'SyntaxError, and not one line has run'],
    ['Runtime error (exception)', 'Only when the bad line runs', '10 / 0, a misspelt name', 'A traceback. The lines before it have already run'],
    ['Logic error', 'Never. Python cannot know what you meant', 'price + 2 instead of price * 2', 'A wrong answer and no message at all']])}
{run('errors')}
{steps('How to read a traceback', [
    'Read the <b>last line</b> first. It names the error and gives a short reason, for example ZeroDivisionError: division by zero.',
    'Look at the line just above it. It shows the file name, the line number and the code that failed.',
    'Go to that line in your editor and ask: which value was not what I expected?',
    eq('last line = what went wrong, line number = where')])}
''', kw=['syntax error', 'runtime error', 'exception', 'logic error', 'traceback', 'SyntaxError', 'NameError', 'ZeroDivisionError'])

K.lesson('style', 'Writing code other people can read: PEP 8 and PEP 20', f'''
<p>Code is read many more times than it is written. A <b>PEP</b> (Python Enhancement Proposal) is a design document for Python. Two of them are about style.</p>
{table(['PEP 8 rule', 'Good', 'Bad'], [
    ['Indent with 4 spaces', 'four spaces before print', 'a tab, or 2 spaces'],
    ['Variable and function names: lower case with underscores (snake_case)', 'total_price', 'TotalPrice, totalprice'],
    ['Class names: CapWords', 'BankAccount', 'bank_account'],
    ['Constants: all capitals', 'MAX_SIZE = 100', 'maxsize = 100'],
    ['One space around = and + in normal code', 'x = a + b', 'x=a+b'],
    ['Lines no longer than 79 characters', 'short lines', 'one very long line'],
    ['Two blank lines between top level functions', 'a gap you can see', 'everything packed together']])}
{run('zen')}
{note('PCEP asks which names follow PEP 8 conventions. snake_case for variables and functions, CapWords for classes, UPPER_CASE for constants.', 'exam')}
''', kw=['PEP 8', 'PEP 20', 'Zen of Python', 'import this', 'snake_case', 'CapWords', 'style guide', 'readability'])

K.lesson('maths', 'The maths: counting what print() writes', f'''
<p>Being exact about small things is the habit that makes a good programmer. Here we count exactly how many characters a print() writes.</p>
{fxs(fx('Characters from one print()', 'N = L + (n &minus; 1) &middot; s + e', 'L = total length of all values as text, n = number of values, s = len(sep), e = len(end).', key=True),
     fx('Bytes in a plain English text file', 'bytes = characters', 'Each English letter, digit, space and new line is 1 byte in UTF-8. Letters from other scripts can take 2 to 4 bytes (Core 3.1).'))}
{steps('Worked example: print("Total", 3, "apples")', [
    'The values as text are "Total" (5), "3" (1) and "apples" (6). L = 5 + 1 + 6 = 12.',
    'There are n = 3 values, so n &minus; 1 = 2 gaps. sep is one space, s = 1, so the gaps add 2.',
    'end is one new line, e = 1.',
    eq('N = 12 + 2 &times; 1 + 1 = 15 characters')])}
{run('count')}
{steps('Worked example: print("2026", "11", "07", sep="-", end="")', [
    'L = 4 + 2 + 2 = 8.',
    'Two gaps of one dash: 2.',
    'end is empty: 0.',
    eq('N = 8 + 2 + 0 = 10, the text 2026-11-07')])}
''', kw=['count characters', 'len', 'sep length', 'end length', 'bytes'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A program is a recipe for the computer. Python reads your recipe from top to bottom and does each step. print() is how it shows you the result.</p>',
    '<p>CPython compiles a .py file to bytecode and runs it on a stack based virtual machine. Grammar is checked for the whole file first (SyntaxError), while exceptions happen only when a line runs. print() calls str() on each argument and writes sep.join(texts) + end to sys.stdout.</p>',
    '<p>sys.stdout is a buffered text stream. When it is a terminal it is line buffered, so print("x", end="") may not appear until a new line is written or flush=True is passed. When output goes to a file or a pipe it is block buffered, which is why progress messages sometimes appear late in logs.</p>',
    '<p>The grammar of Python is a PEG grammar (PEP 617, since 3.9), and the tokenizer produces INDENT and DEDENT tokens from leading white space. Error messages improved a lot in 3.10 to 3.14 ("Did you mean: price?"), based on research on helping novices read errors.</p>',
    'One idea, four depths')}
{grow('Write and run a .py file, use print() with sep and end, and read the last line of a traceback.',
      'Know the difference between compile time and run time, follow PEP 8 names, and use the REPL to test small ideas.',
      'Explain bytecode, output buffering and flush, and why a SyntaxError on line 50 stops line 1 from running.')}
{scene('a shop bill printed at the counter', '<p>The billing machine at a shop runs a small program. It prints the shop name, then each item and price with a fixed gap (that is sep), then a line of dashes and the total (each print ends with a new line, that is end). If the programmer types + instead of * for quantity times price, the machine prints a wrong bill with no error. That is a logic error, and it is why shops test the machine with a known bill before using it.</p>')}
''', kw=['beginner', 'expert', 'buffering', 'flush', 'PEG grammar'])

lc(2235, 'Add Two Integers', 'add-two-integers', 'e', 'Arithmetic', 'Return num1 + num2. The point is to get used to a function that returns a value instead of printing it.', r'''
def sum_two(num1, num2):
    # LeetCode calls this method sum. We use sum_two so we do not hide the built in sum().
    return num1 + num2
''', [('sum_two(12, 5)', 17), ('sum_two(-10, 4)', -6)])
lc(2469, 'Convert the Temperature', 'convert-the-temperature', 'e', 'Formula', 'Kelvin = Celsius + 273.15 and Fahrenheit = Celsius &times; 1.80 + 32.00. Return both in a list.', r'''
def convert_temperature(celsius):
    kelvin = celsius + 273.15
    fahrenheit = celsius * 1.80 + 32.00
    return [round(kelvin, 5), round(fahrenheit, 5)]
''', [('convert_temperature(36.50)', [309.65, 97.7]), ('convert_temperature(122.11)', [395.26, 251.798])])
lc(2413, 'Smallest Even Multiple', 'smallest-even-multiple', 'e', 'Arithmetic', 'If n is already even, n itself works. If n is odd, the answer is 2 &times; n.', r'''
def smallest_even_multiple(n):
    if n % 2 == 0:
        return n
    return 2 * n
''', [('smallest_even_multiple(5)', 10), ('smallest_even_multiple(6)', 6)])
lc(1108, 'Defanging an IP Address', 'defanging-an-ip-address', 'e', 'String replace', 'Replace every dot with [.] using the string method replace().', r'''
def defang_ip_address(address):
    return address.replace(".", "[.]")
''', [('defang_ip_address("1.1.1.1")', '1[.]1[.]1[.]1'), ('defang_ip_address("255.100.50.0")', '255[.]100[.]50[.]0')])

K.lesson('leetcode', 'LeetCode practice', leet(), kw=['LeetCode', 'practice problems', 'add two integers', 'convert the temperature'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>program</b> is a list of exact instructions. Python is a programming language with a small, readable vocabulary (lexis) and clear grammar (syntax).',
    'A <b>compiler</b> translates the whole program first. An <b>interpreter</b> runs it statement by statement. CPython compiles to bytecode, then interprets the bytecode.',
    'Run Python in the REPL (&gt;&gt;&gt;) for quick tests, or save a .py file and run python3 file.py.',
    '<b>print()</b> calls str() on each value, puts sep (a space) between them and end (a new line) after them. N = L + (n &minus; 1)s + e characters.',
    'Python 3.14 has 35 keywords and 4 soft keywords. Comments start with #. Blocks are shown by indentation of 4 spaces.',
    'Syntax errors stop the program before it starts. Runtime errors stop it at the bad line. Logic errors give wrong answers silently.',
    'PEP 8 is the style guide (snake_case, 4 spaces, 79 characters). PEP 20 is the Zen of Python (import this).'],
    'Core 1.2 looks at variables, values and types: what x = 5 really does inside the computer.')}
{files('Two tasks: build the exact text print() writes, and fix a greeting function.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What does print("A", "B") show?', ['AB', 'A B', 'A,B', '"A" "B"'], 1,
       'The default sep.', 'sep is one space by default.')
K.quiz('e', 'Which file name is a Python program?', ['shop.txt', 'shop.py', 'shop.exe', 'shop.html'], 1,
       'The extension.', 'Python source files end in .py.')
K.quiz('e', 'Which symbol starts a comment in Python?', ['//', '#', '/*', '--'], 1,
       'One symbol.', 'Everything after # on that line is ignored.')
K.quiz('e', 'What does an empty print() do?', ['Nothing', 'Prints the word None', 'Prints a new line', 'Raises an error'], 2,
       'end still happens.', 'With no values, only end (a new line) is written.')
K.quiz('m', 'What does print("x", "y", sep="", end="!") write?', ['x y!', 'xy!', 'xy!&#92;n', 'x y'], 1,
       'Both sep and end changed.', 'No gap between, then ! and no new line.')
K.quiz('m', 'A file has a SyntaxError on its last line. Its first line is print("Start"). What is printed?', ['Start, then the error', 'Only the error', 'Start only', 'Nothing at all, not even an error'], 1,
       'When is grammar checked?', 'The whole file is checked before it runs, so Start is never printed.')
K.quiz('m', 'Which of these is a keyword in Python 3.14?', ['print', 'input', 'None', 'main'], 2,
       'print is a function.', 'None is one of the 35 keywords. print and input are built in functions.')
K.quiz('m', 'Which name follows PEP 8 for a variable?', ['TotalPrice', 'total_price', 'TOTALprice', 'total-price'], 1,
       'snake_case.', 'Lower case with underscores. total-price is not even a valid name.')
K.quiz('h', 'Which statement about CPython is true?', ['It never compiles anything', 'It compiles source to bytecode, then interprets the bytecode', 'It compiles straight to machine code like C', 'It needs a separate compile command first'], 1,
       'Two stages.', 'Source to bytecode, then the virtual machine runs it.')
K.quiz('h', 'print("a", "b", "-") prints', ['a-b', 'a b -', 'a - b', 'an error'], 1,
       'Is "-" a keyword argument?', 'Without sep=, the dash is just a third value.')
K.quiz('h', 'price + 2 was typed instead of price * 2. What kind of error is it?', ['Syntax error', 'Runtime error', 'Logic error', 'No error'], 2,
       'Does Python complain?', 'The code is valid and runs. The answer is wrong, so it is a logic error.')
K.quiz('x', 'In the style of an MIT 6.100L question: how many characters does print(10, 20, 30, sep="&lt;&gt;") write, counting the final new line?', ['10', '11', '13', '14'], 1,
       'N = L + (n &minus; 1)s + e.', 'L = 2 + 2 + 2 = 6. Two gaps of 2 characters add 4. end adds 1. 6 + 4 + 1 = 11.')
K.quiz('x', 'In the style of a Stanford CS106A question: output goes to a file, and the program prints "Working..." with end="" and then runs for a minute. Why may the text not appear in the file during that minute?', ['print() is broken', 'Output to a file is block buffered and is written when the buffer fills, a new line arrives on a terminal, flush=True is passed, or the program ends', 'Files cannot hold text', 'end="" deletes the text'], 1,
       'Buffering.', 'sys.stdout is buffered. Use print(..., flush=True) for progress messages.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many characters does print("Hi") write, counting the new line?', '3', 'L + e.',
       ['"Hi" has 2 characters.', 'One value, so no gaps.', eq('2 + 0 + 1 = 3')], check=3)
K.calc('e', 'Characters written by print("Asha", "Ravi")?', '10', 'Two values, one gap.',
       ['L = 4 + 4 = 8.', 'One gap of 1 space.', eq('8 + 1 + 1 = 10')], check=10)
K.calc('e', 'How many keywords does Python 3.14 have?', '35', 'len(keyword.kwlist).',
       ['Run import keyword.', 'Then len(keyword.kwlist).', eq('35')], check=35)
K.calc('m', 'Characters written by print(1, 22, 333, sep=", ")?', '11', 'sep has 2 characters.',
       ['L = 1 + 2 + 3 = 6.', 'Two gaps of 2: 4.', eq('6 + 4 + 1 = 11')], check=11)
K.calc('m', 'Characters written by print("2026", "11", "07", sep="-", end="")?', '10', 'end is empty.',
       ['L = 8.', 'Two dashes.', eq('8 + 2 + 0 = 10')], check=10)
K.calc('m', 'print(3 + 4, "3 + 4") writes how many characters with the new line?', '8', 'The first value becomes 7.',
       ['3 + 4 is worked out first: 7, one character.', 'The text "3 + 4" has 5 characters.', eq('1 + 5 + 1 gap + 1 end = 8')], check=8)
K.calc('m', 'A program prints 5 lines, each print("ok"). How many characters in total?', '15', 'Each line is 3.',
       ['"ok" is 2 characters plus the new line: 3.', 'Five lines.', eq('5 &times; 3 = 15')], check=15)
K.calc('h', 'print(*range(10), sep="") prints the digits 0 to 9 together. How many characters, with the new line?', '11', '10 digits, empty sep.',
       ['L = 10 single digits = 10.', 'sep is empty, gaps add 0.', eq('10 + 0 + 1 = 11')], check=11)
K.calc('h', 'n values each 3 characters long, sep of 2 characters, end of 1. Find N when n = 20.', '99', 'N = 3n + 2(n &minus; 1) + 1.',
       ['L = 3 &times; 20 = 60.', 'Gaps: 19 &times; 2 = 38.', eq('60 + 38 + 1 = 99')], check=99)
K.calc('x', 'In the style of a CMU 15-112 problem: print(1.5, True, None, sep="|"). How many characters with the new line?', '14', 'str(True) is "True", str(None) is "None".',
       ['"1.5" has 3, "True" 4, "None" 4, so L = 11.', 'Two gaps of 1: 2.', eq('11 + 2 + 1 = 14')], check=14)

# ---------------------------------------------------------------- assignments
K.assign('printed', 'e', 'The exact text print() writes',
         '<p>Write <code>printed(values, sep, end)</code> that returns the exact text print(*values, sep=sep, end=end) would write. values is a list. Turn each value into text with str().</p>',
         '''
def printed(values, sep, end):
    # your code here
    pass
''', [('printed(["Total", 3, "apples"], " ", "\\n")', 'Total 3 apples\n'),
      ('printed(["2026", "11", "07"], "-", "")', '2026-11-07'),
      ('printed([], " ", "\\n")', '\n'),
      ('printed([1.5, True, None], "|", "!")', '1.5|True|None!')],
         '''
def printed(values, sep, end):
    texts = []
    for value in values:
        texts.append(str(value))
    return sep.join(texts) + end
''', 'Make a list of str(value) for each value, join it with sep, then add end.', '<p>This is exactly what print() does inside before it writes to the screen.</p>')
K.assign('greet', 'e', 'Fix the greeting',
         '<p>The starter code has two mistakes. Fix them so that <code>greet(name)</code> returns "Hello, " then the name then "!". For example greet("Asha") returns "Hello, Asha!".</p>',
         '''
def greet(name):
    message = "Hello " + name
    return message
''', [('greet("Asha")', 'Hello, Asha!'), ('greet("Ravi")', 'Hello, Ravi!'), ('greet("")', 'Hello, !')],
         '''
def greet(name):
    message = "Hello, " + name + "!"
    return message
''', 'Compare the text you build with the one you want, character by character: a comma is missing and so is the !.', '<p>Both mistakes are logic errors: the code runs, but the answer is wrong. Tests catch them.</p>')

K.must('Program and language', 'A program is a list of exact instructions. Lexis is the vocabulary, syntax the grammar, semantics the meaning.')
K.must('How CPython runs a file', 'Source is checked and compiled to bytecode, then the virtual machine runs it top to bottom. A SyntaxError anywhere stops everything.')
K.must('print()', 'print(*values, sep=" ", end="&#92;n"). str() on each value, sep between, end after. N = L + (n &minus; 1)s + e.')
K.must('Keywords and blocks', '35 keywords in 3.14, soft keywords match, case, type, _. # starts a comment. Indent blocks with 4 spaces.')
K.must('Three errors', 'Syntax error before running, runtime error at the bad line, logic error never reported.')

T = K.topic(
    slug='py-start', topic='py-start', step=(1, 'Getting started', 'py-c1', 'What a program is, how Python runs it, values, types, operators and input and output.', 'Beginner'),
    title='What a program is and your first Python program', short='First program', badge='1.1', minutes=40,
    lead='Start from zero. Learn what a program is, how a compiler and an interpreter differ and what CPython does with your file, install Python, write your first program, master print() with sep and end, and learn to tell syntax, runtime and logic errors apart.',
    desc='Programs, lexis, syntax and semantics, compilers and interpreters, CPython and bytecode, installing Python, the REPL and scripts, print() with sep and end, keywords, comments, indentation, the three kinds of errors, PEP 8 and PEP 20.',
    summary='Programs, compiler and interpreter, CPython, REPL and scripts, print() with sep and end, keywords, indentation, error kinds, PEP 8.',
    keywords=['first program', 'hello world', 'print', 'sep', 'end', 'interpreter', 'compiler', 'keywords', 'indentation', 'syntax error', 'PEP 8', 'PCEP'],
    recap='<p>A program is exact steps. Python checks the whole file, then runs it top to bottom, and print() shows the results.</p>',
    added='2026-11-07', leet=leet_items())
