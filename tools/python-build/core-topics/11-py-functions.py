# Core Python 4.1: functions and arguments. Follows PCEP-30-02 section 4.1 (defining and invoking your own
# functions and generators, the return keyword, returning results, the None keyword) and 4.2 (parameters vs
# arguments, positional, keyword and mixed argument passing, default parameter values) and PCAP-31-03 (positional-only
# and keyword-only parameters, *args and **kwargs), checked against the Python 3.14 tutorial section 4.8 and the
# language reference section 8.7 "Function definitions".
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-functions')
K = Kit()

K.code('basic', r'''
def greet(name):              # name is a parameter
    print("Hello,", name)

greet("Asha")                 # "Asha" is an argument
greet("Ravi")

def area(width, height):
    return width * height     # send a value back to the caller

room = area(4, 5)
print("room:", room, "m2")
print("two rooms:", area(4, 5) + area(3, 3), "m2")
''')

K.code('ret', r'''
def show_double(x):
    print(x * 2)          # prints, returns nothing

def double(x):
    return x * 2          # returns, prints nothing

a = show_double(5)
b = double(5)
print("a is", a, "and b is", b)

def grade(mark):
    if mark >= 90:
        return "A"        # return also leaves the function at once
    if mark >= 75:
        return "B"
    return "C"

print(grade(95), grade(80), grade(40))

def min_max(items):
    return min(items), max(items)     # one tuple, two values

low, high = min_max([7, 2, 9])
print(low, high)
''')

K.code('args', r'''
def describe(name, age, city="Pune"):
    print(f"{name} is {age} and lives in {city}")

describe("Asha", 21)                       # positional, city uses its default
describe("Ravi", 23, "Delhi")              # all positional
describe(age=30, name="Meera")             # keyword: any order
describe("John", city="Goa", age=40)       # positional first, then keyword
# describe(name="Sara", 25) would be a SyntaxError: the whole file would not run
''')

K.code('star', r'''
def total(*numbers):               # any number of positional arguments
    print("numbers is", numbers)   # a tuple
    result = 0
    for n in numbers:
        result += n
    return result

print(total(), total(5), total(1, 2, 3, 4))

def profile(name, **details):      # any number of keyword arguments
    print(name, details)           # a dict

profile("Asha", age=21, city="Pune")

def order(item, *, qty=1, gift=False):     # after * every parameter is keyword-only
    return f"{qty} x {item}{' (gift)' if gift else ''}"

print(order("pen", qty=3, gift=True))

def power(base, exp, /):           # before / every parameter is positional-only
    return base ** exp

print(power(2, 10))
try:
    power(base=2, exp=10)
except TypeError as err:
    print("TypeError:", err)
''')

K.code('unpackcall', r'''
def move(x, y, speed):
    print(f"to ({x}, {y}) at {speed} km/h")

point = [3, 7]
move(*point, 40)                  # * spreads a list into positional arguments

settings = {"speed": 60, "y": 2, "x": 1}
move(**settings)                  # ** spreads a dict into keyword arguments

numbers = [4, 9, 1]
print(max(*numbers), max(numbers))
print(*numbers, sep=" | ")
''')

K.code('mutdef', r'''
def add_bad(item, bag=[]):        # the default list is made ONCE, when def runs
    bag.append(item)
    return bag

print(add_bad("pen"))
print(add_bad("ink"))             # the same list again!

def add_good(item, bag=None):     # the usual fix
    if bag is None:
        bag = []                  # a new list on every call
    bag.append(item)
    return bag

print(add_good("pen"))
print(add_good("ink"))
print(add_bad.__defaults__)
''')

K.code('doc', r'''
def bmi(weight_kg: float, height_m: float) -> float:
    """Return the body mass index: weight divided by height squared.

    weight_kg is in kilograms and height_m in metres.
    """
    return round(weight_kg / height_m ** 2, 1)

print(bmi(70, 1.75))
print(bmi.__doc__.splitlines()[0])
print(bmi.__annotations__)           # hints are stored, but never checked when the program runs
''')

K.code('objects', r'''
def shout(text):
    return text.upper() + "!"

def whisper(text):
    return text.lower() + "..."

speak = shout                 # a function is an object: give it another name
print(speak("hi"), speak is shout)

def apply_twice(func, value): # and pass it to another function
    return func(func(value))

print(apply_twice(whisper, "HELLO"))
print(apply_twice(lambda n: n * 3, 2))

tools = {"loud": shout, "soft": whisper}   # or store it in a dict
print(tools["soft"]("Good Night"))
print(type(shout), shout.__name__)
''')

K.lesson('idea', 'What a function is', f'''
{src('Python 3.14 tutorial section 4.8, language reference section 8.7, PCEP-30-02 sections 4.1 and 4.2 and PCAP-31-03.')}
{wwh('A <b>function</b> is a named block of code that does one job. You define it once with <b>def</b> and then <b>call</b> it by name as often as you like, giving it different inputs each time.',
     'Without functions you copy the same lines again and again. When there is a bug, you must fix every copy, and the program becomes long and hard to read. A function lets you write the job once, give it a clear name, test it alone and reuse it everywhere. This idea is called DRY: do not repeat yourself.',
     'def name(parameters): followed by an indented body creates a function object and binds it to the name. A call name(arguments) gives each parameter a value, runs the body, and the call itself becomes the value after <b>return</b>.')}
{scene('a recipe card', '<p>A recipe card for "masala tea" says: take water, milk, tea leaves and sugar, then boil, add, strain. The card is the function definition. Making tea for 2 people or 10 people with less sugar is a call with different arguments. You do not rewrite the card each time, and if you improve the recipe, every future cup gets better.</p>')}
{run('basic')}
{note('A <b>parameter</b> is the name in the def line (name, width). An <b>argument</b> is the value you pass in the call ("Asha", 4). Exams use both words, so learn the difference.', 'exam')}
''', kw=['function', 'def', 'call', 'parameter', 'argument', 'DRY', 'reuse'])

K.lesson('ret', 'return, print and None', f'''
{run('ret')}
{versus('print inside a function or return', ['', 'print(x)', 'return x'], [
    ['What it does', 'Shows x on the screen', 'Gives x back to the code that called the function'],
    ['Can the caller use the value', 'No, it is gone', 'Yes: store it, add it, pass it on'],
    ['The call evaluates to', 'None', 'x'],
    ['Stops the function', 'No', 'Yes, at once']],
    'functions should usually return results and let the caller decide whether to print them. That makes them reusable and testable.')}
{note('A function with no return, or with a bare return, gives back <b>None</b>. That is why a = show_double(5) printed 10 but left a as None.', 'exam')}
''', kw=['return', 'None', 'print vs return', 'early return', 'return multiple values'])

K.lesson('args', 'Positional, keyword and default arguments', f'''
{run('args')}
{table(['Kind of argument', 'Example call', 'Rule'], [
    ['Positional', 'describe("Ravi", 23)', 'Matched by position, left to right'],
    ['Keyword', 'describe(age=30, name="Meera")', 'Matched by name, any order'],
    ['Mixed', 'describe("John", city="Goa", age=40)', 'All positional arguments must come before any keyword argument'],
    ['Default value', 'def describe(..., city="Pune")', 'Used when the caller gives nothing for that parameter']])}
{note('describe(name="Sara", 25) is a SyntaxError: a positional argument may not follow a keyword argument. Python refuses to even start the program.', 'exam')}
''', kw=['positional argument', 'keyword argument', 'default parameter', 'mixed arguments', 'SyntaxError'])

K.lesson('star', '*args, **kwargs, keyword-only and positional-only', f'''
{viz('pyargs')}
{run('star')}
{table(['In the def line', 'Meaning', 'Inside the function it is'], [
    ['a', 'Positional or keyword', 'The value'],
    ['a=1', 'Optional, with a default', 'The value or the default'],
    ['*args', 'Collects extra positional arguments', 'A tuple'],
    ['**kwargs', 'Collects extra keyword arguments', 'A dict'],
    ['* alone', 'Every parameter after it is keyword-only', ''],
    ['/', 'Every parameter before it is positional-only (Python 3.8+)', '']])}
{note('The full order is: positional-only, /, normal, *args (or a bare *), keyword-only, **kwargs. The names args and kwargs are only a habit. What matters is the * and **.', 'tip')}
''', kw=['*args', '**kwargs', 'keyword-only', 'positional-only', 'varargs', 'slash', 'star'])

K.lesson('unpackcall', 'Spreading lists and dicts into a call', f'''
{run('unpackcall')}
{note('In a def line, * and ** <b>collect</b> arguments. In a call, * and ** <b>spread</b> a list or dict out into separate arguments. Same symbols, opposite jobs.', 'exam')}
''', kw=['argument unpacking', 'star in call', 'double star', 'spread'])

K.lesson('mutdef', 'The mutable default trap', f'''
{run('mutdef')}
{wwh('A default value is worked out <b>once</b>, when the def line runs, and kept in the function object (func.__defaults__).',
     'For numbers, strings and None this never matters, because they cannot change. For a list or dict it does: every call that uses the default shares the same object, so changes pile up from one call to the next.',
     'Use None as the default and create a new list inside the function. This is one of the most common Python bugs, and a favourite interview question.')}
''', kw=['mutable default argument', '__defaults__', 'None default', 'common bug'])

K.lesson('doc', 'Docstrings and type hints', f'''
{run('doc')}
{note('A <b>docstring</b> is a string on the first line of the body. help(bmi) and editors show it. <b>Type hints</b> such as height_m: float and -&gt; float tell readers and tools like mypy what you expect, but Python itself does not check them when the program runs (Advanced 3.1).', 'tip')}
''', kw=['docstring', 'help', 'type hints', 'annotations', '__doc__', 'mypy'])

K.lesson('objects', 'Functions are objects too', f'''
{run('objects')}
{note('A function name is just a variable that holds a function object. You can give it another name, store it in a list or dict, and pass it to another function. Functions that take or return functions are called <b>higher-order functions</b>. Core 4.3 uses this with sorted, map, filter and closures.', 'tip')}
''', kw=['first-class function', 'function object', 'higher-order function', 'callback', 'lambda preview'])

K.lesson('versus', 'Kinds of reusable code compared', f'''
{versus('Ways to reuse code', ['', 'Copy and paste', 'Function', 'Method (Core 6.1)', 'Module (Core 5.2)'], [
    ['Defined with', 'Nothing', 'def', 'def inside a class', 'a .py file'],
    ['Fix a bug in', 'Every copy', 'One place', 'One place', 'One place'],
    ['Called as', '', 'name(args)', 'obj.name(args)', 'module.name(args)'],
    ['Best for', 'Never', 'One job', 'A job tied to an object', 'Sharing many functions between programs']],
    'as soon as you write the same few lines twice, turn them into a function.')}
''', kw=['function vs method', 'module', 'reuse', 'refactoring'])

K.lesson('maths', 'Functions in maths and in code', f'''
{fxs(fx('A function maps each input to one output', 'f: X &rarr; Y, x &#8614; f(x)', 'area(width, height) maps each pair of numbers to one number.', key=True),
     fx('Composition', '(f &#8728; g)(x) = f(g(x))', 'apply_twice(f, x) is f(f(x)). len(str(n)) is len &#8728; str.', key=True),
     fx('Idempotent function', 'f(f(x)) = f(x)', 'abs, str.strip and sorted are idempotent: doing them twice changes nothing more.'),
     fx('How many functions from a set of m inputs to n outputs', 'n<sup>m</sup>', 'Each of the m inputs can go to any of the n outputs. From {1, 2, 3} to {a, b}: 2<sup>3</sup> = 8.'),
     fx('Arguments a call may give with p positional parameters, d of them with defaults and no *args', 'between p &minus; d and p positional arguments', 'describe has p = 3, d = 1, so 2 or 3 positional arguments.'))}
{steps('Worked example: what does apply_twice(lambda n: n * 3, 2) return?', [
    'apply_twice(f, v) returns f(f(v)).',
    'Inner call: f(2) = 6.',
    'Outer call: f(6) = 18.',
    eq('(f &#8728; f)(2) = 18')])}
{deep('Pure functions', '<p>A <b>pure</b> function gives the same output for the same input and changes nothing outside itself: no printing, no changing global variables or arguments. area and double are pure, add_bad is not. Pure functions are easy to test, to cache (Core 4.2) and to run in parallel (Advanced 5.1), which is why functional programming prefers them.</p>')}
''', kw=['mathematical function', 'composition', 'idempotent', 'pure function', 'side effects'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>def makes a function, a call runs it, and return gives a value back. A function without return gives None.</p>',
    '<p>Arguments can be positional or keyword, and parameters can have defaults. *args collects extra positional arguments into a tuple and **kwargs collects extra keyword arguments into a dict.</p>',
    '<p>Use / and * to make parameters positional-only or keyword-only, spread arguments with * and **, avoid mutable defaults, and write docstrings and type hints. Functions are objects you can pass around.</p>',
    '<p>Calling a function creates a frame object with its local variables. CPython binds arguments in C (the rules shown in the animation), stores defaults in __defaults__ and __kwdefaults__, and inspect.signature(f).bind(*args, **kwargs) reproduces the same binding in Python. Since 3.11 calls between Python functions avoid creating C stack frames, which made calls much cheaper.</p>')}
{grow('Write a function with parameters, call it and return a value.',
      'Use keyword and default arguments, *args and **kwargs, and return several values as a tuple.',
      'Design clean signatures with / and *, explain the mutable default trap, and use functions as objects.')}
{scene('the API of a payment app', '<p>A payment function might be pay(amount, /, *, to, note="", notify=True). amount must be passed by position, the receiver must be named (to="Asha") so nobody swaps the two numbers by mistake, and note and notify are optional. Good signatures prevent costly mistakes before the code even runs.</p>')}
''', kw=['beginner', 'expert', 'frame', 'inspect.signature', 'API design'])

lc(1342, 'Number of Steps to Reduce a Number to Zero', 'number-of-steps-to-reduce-a-number-to-zero', 'e', 'Loop inside a function', 'While num &gt; 0: halve it if even, else take away 1. Count the steps and return the count.', r'''
def number_of_steps(num):
    steps = 0
    while num > 0:
        if num % 2 == 0:
            num = num // 2
        else:
            num = num - 1
        steps = steps + 1
    return steps
''', [('number_of_steps(14)', 6), ('number_of_steps(8)', 4), ('number_of_steps(123)', 12)])
lc(1920, 'Build Array from Permutation', 'build-array-from-permutation', 'e', 'Index into a list', 'ans[i] is nums[nums[i]]. Build a new list and return it.', r'''
def build_array(nums):
    ans = []
    for i in range(len(nums)):
        ans.append(nums[nums[i]])
    return ans
''', [('build_array([0, 2, 1, 5, 3, 4])', [0, 1, 2, 4, 5, 3]), ('build_array([5, 0, 1, 2, 3, 4])', [4, 5, 0, 1, 2, 3])])
lc(1470, 'Shuffle the Array', 'shuffle-the-array', 'e', 'Two halves side by side', 'Walk i from 0 to n &minus; 1 and add nums[i] then nums[i + n].', r'''
def shuffle(nums, n):
    result = []
    for i in range(n):
        result.append(nums[i])
        result.append(nums[i + n])
    return result
''', [('shuffle([2, 5, 1, 3, 4, 7], 3)', [2, 3, 5, 4, 1, 7]), ('shuffle([1, 1, 2, 2], 2)', [1, 2, 1, 2])])
lc(2011, 'Final Value of Variable After Performing Operations', 'final-value-of-variable-after-performing-operations', 'e', 'A helper decides plus or minus', 'Every operation contains either "++" or "--". Add 1 or take away 1.', r'''
def final_value_after_operations(operations):
    x = 0
    for op in operations:
        if "+" in op:
            x = x + 1
        else:
            x = x - 1
    return x
''', [('final_value_after_operations(["--X", "X++", "X++"])', 1), ('final_value_after_operations(["++X", "++X", "X++"])', 3)])
lc(1365, 'How Many Numbers Are Smaller Than the Current Number', 'how-many-numbers-are-smaller-than-the-current-number', 'e', 'Helper function per item', 'Write a small helper that counts the numbers smaller than x, then call it for every item.', r'''
def count_smaller(nums, x):
    count = 0
    for y in nums:
        if y < x:
            count = count + 1
    return count


def smaller_numbers_than_current(nums):
    result = []
    for x in nums:
        result.append(count_smaller(nums, x))
    return result
''', [('smaller_numbers_than_current([8, 1, 2, 2, 3])', [4, 0, 1, 1, 3]), ('smaller_numbers_than_current([7, 7, 7])', [0, 0, 0])])
lc(1431, 'Kids With the Greatest Number of Candies', 'kids-with-the-greatest-number-of-candies', 'e', 'Find the max once', 'Work out max(candies) once. Kid i can be the greatest if candies[i] + extra reaches it.', r'''
def kids_with_candies(candies, extra_candies):
    best = max(candies)
    result = []
    for c in candies:
        result.append(c + extra_candies >= best)
    return result
''', [('kids_with_candies([2, 3, 5, 1, 3], 3)', [True, True, True, False, True]), ('kids_with_candies([4, 2, 1, 1, 2], 1)', [True, False, False, False, False])])
lc(2652, 'Sum Multiples', 'sum-multiples', 'e', 'Small test function', 'Add every number from 1 to n that divides by 3, 5 or 7.', r'''
def sum_of_multiples(n):
    total = 0
    for i in range(1, n + 1):
        if i % 3 == 0 or i % 5 == 0 or i % 7 == 0:
            total = total + i
    return total
''', [('sum_of_multiples(7)', 21), ('sum_of_multiples(10)', 40), ('sum_of_multiples(9)', 30)])
lc(1323, 'Maximum 69 Number', 'maximum-69-number', 'e', 'Change the first 6', 'Turn the number into text, replace the first 6 with a 9, and turn it back.', r'''
def maximum_69_number(num):
    text = str(num)
    return int(text.replace("6", "9", 1))
''', [('maximum_69_number(9669)', 9969), ('maximum_69_number(9996)', 9999), ('maximum_69_number(9999)', 9999)])
lc(2160, 'Minimum Sum of Four Digit Number After Splitting Digits', 'minimum-sum-of-four-digit-number-after-splitting-digits', 'e', 'Sort the digits', 'Sort the 4 digits a &le; b &le; c &le; d. The best split is (10a + c) + (10b + d).', r'''
def minimum_sum(num):
    d = sorted(str(num))
    return int(d[0] + d[2]) + int(d[1] + d[3])
''', [('minimum_sum(2932)', 52), ('minimum_sum(4009)', 13)])
lc(1641, 'Count Sorted Vowel Strings', 'count-sorted-vowel-strings', 'm', 'Maths in a function', 'A sorted string of length n over 5 vowels is a choice of n items from 5 with repeats: C(n + 4, 4).', r'''
def count_vowel_strings(n):
    return (n + 1) * (n + 2) * (n + 3) * (n + 4) // 24
''', [('count_vowel_strings(1)', 5), ('count_vowel_strings(2)', 15), ('count_vowel_strings(33)', 66045)])

K.lesson('leetcode', 'LeetCode practice', leet(), kw=['LeetCode', 'helper function', 'build array', 'shuffle the array', 'count sorted vowel strings'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>def</b> name(parameters): defines a function. name(arguments) calls it.',
    '<b>return</b> sends a value back and leaves the function. No return means the call gives None.',
    'Arguments are matched by position or by name. Positional arguments come first. Defaults make a parameter optional.',
    '*args collects extra positional arguments into a tuple, **kwargs extra keyword arguments into a dict.',
    'After * parameters are keyword-only. Before / they are positional-only.',
    'In a call, *list and **dict spread values out into arguments.',
    'Default values are made once. Use None instead of [] or {} as a default.',
    'Functions are objects: name them, store them and pass them to other functions.'],
    'Core 4.2 explains where names live (scope), global and nonlocal, and functions that call themselves (recursion).')}
{files('Three tasks: a flexible average with *args, a receipt builder with keyword-only options, and a safe append with a None default.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does a function return if it has no return statement?', ['0', 'None', '""', 'An error'], 1, 'Nothing is not a number.', 'A call without return gives None.')
K.quiz('e', 'In def area(w, h):, what are w and h?', ['Arguments', 'Parameters', 'Keywords', 'Modules'], 1, 'Names in the def line.', 'Parameters are the names in the definition. Arguments are the values in the call.')
K.quiz('e', 'Which keyword defines a function?', ['function', 'def', 'fun', 'lambda only'], 1, 'Short for define.', 'def starts a function definition.')
K.quiz('m', 'def f(a, b=3): return a * b. What is f(2)?', ['2', '5', '6', 'Error'], 2, 'b uses its default.', '2 &times; 3 = 6.')
K.quiz('m', 'def f(*x): return len(x). What is f(1, 2, 3)?', ['1', '3', '(1, 2, 3)', 'Error'], 1, 'x is a tuple.', 'x = (1, 2, 3), which has 3 items.')
K.quiz('m', 'def f(**k): return k. What is f(a=1)?', ["{'a': 1}", '(1,)', "['a']", 'Error'], 0, 'A dict.', '**k collects keyword arguments into a dict.')
K.quiz('m', 'Which call is a SyntaxError for def f(a, b):?', ['f(1, 2)', 'f(b=2, a=1)', 'f(a=1, 2)', 'f(1, b=2)'], 2, 'Order of kinds.', 'A positional argument cannot follow a keyword argument.')
K.quiz('m', 'def f(a, *, b): ... Which call works?', ['f(1, 2)', 'f(1, b=2)', 'f(a=1, 2)', 'f()'], 1, 'b is keyword-only.', 'After the bare * you must name b.')
K.quiz('h', 'def f(x, items=[]) has the body items.append(x) and then return items. What is f(1) then f(2)?', ['[1] then [2]', '[1] then [1, 2]', '[1, 2] then [1, 2]', 'Error'], 1, 'The default is made once.', 'Both calls share one list.')
K.quiz('h', 'def f(a, /, b): ... What does f(a=1, b=2) raise?', ['Nothing', 'SyntaxError', 'TypeError', 'NameError'], 2, 'a is positional-only.', 'TypeError: f() got some positional-only arguments passed as keyword arguments.')
K.quiz('h', 'What does print(print("hi")) show?', ['hi', 'hi then None', 'None', 'hi hi'], 1, 'print returns None.', 'The inner print shows hi and returns None, which the outer print shows.')
K.quiz('x', 'In the style of a Stanford CS106A exam: def f(a, b=[]) has the body b = b + [a] and then return b. What are f(1) and then f(2)?', ['[1] and [2]', '[1] and [1, 2]', '[1, 2] and [1, 2]', 'Error'], 0, 'b + [a] makes a new list.', 'b = b + [a] builds a new list and never changes the default, unlike append.')
K.quiz('x', 'In the style of an MIT 6.100L exam: def g(f, x): return f(f(x)). What is g(lambda n: n ** 2, 3)?', ['9', '27', '81', '6'], 2, 'Square twice.', '3<sup>2</sup> = 9, then 9<sup>2</sup> = 81.')

K.calc('e', 'def area(w, h): return w * h. What is area(4, 5) + area(3, 3)?', '29', '20 + 9.', ['area(4, 5) = 20.', 'area(3, 3) = 9.', eq('29')], check=4 * 5 + 3 * 3)
K.calc('e', 'def f(a, b=10): return a + b. What is f(5)?', '15', 'b is 10.', ['a = 5.', 'b uses its default 10.', eq('15')], check=5 + 10)
K.calc('e', 'def total(*n): return sum(n). What is total(1, 2, 3, 4)?', '10', 'n is a tuple.', ['n = (1, 2, 3, 4).', 'sum = 10.', eq('10')], check=10)
K.calc('m', 'def f(a, b, c=0): return a * 100 + b * 10 + c. What is f(c=3, a=1, b=2)?', '123', 'Match by name.', ['a = 1, b = 2, c = 3.', '100 + 20 + 3.', eq('123')], check=123)
K.calc('m', 'How many functions are there from a set of 3 inputs to a set of 2 outputs?', '8', 'n<sup>m</sup>.', ['m = 3 inputs, n = 2 outputs.', '2<sup>3</sup>.', eq('8')], check=2 ** 3)
K.calc('m', 'def g(x): return x * 3. What is g(g(g(1)))?', '27', 'Compose three times.', ['g(1) = 3.', 'g(3) = 9.', eq('g(9) = 27')], check=27)
K.calc('m', 'def f(*a, **k): return len(a) * 10 + len(k). What is f(1, 2, 3, x=1, y=2)?', '32', 'Three positional, two keyword.', ['len(a) = 3.', 'len(k) = 2.', eq('30 + 2 = 32')], check=32)
K.calc('h', 'Count Sorted Vowel Strings: C(n + 4, 4) for n = 3.', '35', '7 &times; 6 &times; 5 &times; 4 / 24.', ['C(7, 4).', '840 / 24.', eq('35')], check=7 * 6 * 5 * 4 // 24)
K.calc('h', 'How many one to one functions are there from a set of 3 inputs to a set of 5 outputs?', '60', '5 &times; 4 &times; 3.', ['The first input has 5 choices.', 'Then 4, then 3.', eq('60')], check=5 * 4 * 3)
K.calc('x', 'In the style of a Cambridge Part IA question: def f(x, acc=[]) has the body acc.append(x) and then return sum(acc). What is f(1) + f(2) + f(3)?', '10', 'The default list grows.', ['f(1): acc = [1], returns 1.', 'f(2): acc = [1, 2], returns 3.', 'f(3): acc = [1, 2, 3], returns 6.', eq('1 + 3 + 6 = 10')], check=10)

K.assign('avg', 'e', 'Average of any number of values',
         '<p>Write <code>average(*values)</code> that returns the mean of all the numbers passed in, rounded to 2 decimal places. With no values, return 0.</p>',
         '''
def average(*values):
    # your code here
    pass
''', [('average(2, 4, 9)', 5.0), ('average()', 0), ('average(1, 2)', 1.5), ('average(1, 1, 2)', 1.33)],
         '''
def average(*values):
    if len(values) == 0:
        return 0
    total = 0
    for v in values:
        total = total + v
    return round(total / len(values), 2)
''', 'values is a tuple. Check len(values) == 0 first to avoid dividing by zero.', '<p>max, min and print all use *args in the same way, which is why you can pass them any number of values.</p>')
K.assign('receipt', 'm', 'Receipt line with keyword-only options',
         '<p>Write <code>receipt(item, price, *, qty=1, discount=0)</code> that returns text like "3 x pen = 27.00". The total is price &times; qty &times; (100 &minus; discount) / 100, with 2 decimals. qty and discount must be keyword-only.</p>',
         '''
def receipt(item, price, qty=1, discount=0):
    # your code here (and fix the signature)
    pass
''', [('receipt("pen", 10, qty=3, discount=10)', '3 x pen = 27.00'), ('receipt("book", 250)', '1 x book = 250.00'), ('receipt.__kwdefaults__', {'qty': 1, 'discount': 0})],
         '''
def receipt(item, price, *, qty=1, discount=0):
    total = price * qty * (100 - discount) / 100
    return f"{qty} x {item} = {total:.2f}"
''', 'Add a bare * after price. Format the total with :.2f.', '<p>__kwdefaults__ holds the defaults of keyword-only parameters, so the test can check that you really used the bare *.</p>')
K.assign('safe', 'm', 'Append without the mutable default trap',
         '<p>Write <code>add_tag(tag, tags=None)</code> that adds tag to the list tags and returns the list. If no list is given, start a new empty list on every call.</p>',
         '''
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags
''', [('add_tag("a")', ['a']), ('(add_tag("x"), add_tag("y"))[1]', ['y']), ('add_tag("c", ["b"])', ['b', 'c'])],
         '''
def add_tag(tag, tags=None):
    if tags is None:
        tags = []
    tags.append(tag)
    return tags
''', 'Use None as the default and make the list inside the function.', '<p>The starter code passes the first test but fails the second, because the two calls share one list.</p>')

K.must('def and return', 'def name(params): body. return value leaves the function. No return gives None. print is not return.')
K.must('Argument kinds', 'Positional by order, keyword by name, positional before keyword. Defaults make parameters optional.')
K.must('Star parameters', '*args tuple of extra positionals, **kwargs dict of extra keywords. Bare * means keyword-only after it, / means positional-only before it.')
K.must('Mutable default', 'Defaults are made once at def time. Use None, then create the list inside.')
K.must('Functions are objects', 'Assign them, store them, pass them: sorted(key=f), map(f, items). Docstring on the first line, type hints are not enforced.')

T = K.topic(
    slug='py-functions', topic='py-functions', step=(4, 'Functions', 'py-c4', 'Write reusable code with def, every kind of argument, scope, recursion, lambda and comprehensions.', 'Intermediate'),
    title='Functions: def, return and every kind of argument', short='Functions', badge='4.1', minutes=65,
    lead='Write a job once and use it everywhere. Learn def and return, the difference between print and return, positional, keyword and default arguments, *args and **kwargs, keyword-only and positional-only parameters, the mutable default trap, docstrings, type hints, and functions as objects.',
    desc='def, calling, parameters and arguments, return and None, return vs print, early return, returning tuples, positional and keyword arguments, defaults, *args, **kwargs, keyword-only and positional-only parameters, argument unpacking with * and **, the mutable default trap, docstrings, type hints, functions as first-class objects, composition and pure functions.',
    summary='def, return, None, argument kinds, *args, **kwargs, / and *, unpacking, mutable defaults, docstrings, first-class functions.',
    keywords=['function', 'def', 'return', 'None', 'arguments', 'parameters', '*args', '**kwargs', 'keyword-only', 'positional-only', 'default argument', 'PCEP', 'PCAP'],
    recap='<p>A function is a named, reusable job. Pass values by position or name, collect extras with * and **, return the result, and never use a list as a default.</p>',
    added='2026-11-07', leet=leet_items())
