# Core Python 7.1: exam practice. Revises the whole core part in the shape of the Python Institute exams PCEP-30-02
# and PCAP-31-03 (exam facts and block weights from pythoninstitute.org/pcep-30-02, /pcep-30-02-exam-syllabus,
# /pcap-31-03 and /pcap-31-03-exam-syllabus, read 2026-11-07, plus the newer PCEP-30-03 and PCAP-31-04 pages).
# Every question is an original practice question written for this course. Every answer was printed by a real run.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items, show

chapter('py-core-exam')
K = Kit()


def answers(title, body):
    return f'<details class="deep"><summary>{title}</summary><div class="deep-b">{body}</div></details>'


PAPER_A = r'''
print("Q1", -2 ** 2, 2 ** 3 ** 2)
print("Q2", 7 // -2, -7 % 3, 7 % -3)
print("Q3", 0.1 + 0.2 == 0.3, round(2.5), round(3.5))
print("Q4", 1 < 2 < 3, 3 > 2 > 1 == 1)

x = 0
while x < 10:
    x += 3
else:
    print("Q5 done", x)

for i in range(3):
    if i == 1:
        break
else:
    print("no break")
print("Q6 i is", i)

print("Q7", int("1F", 16), 0o17, 0b101, 1_000)
print("Q8", bool("False"), bool(""), bool([0]), bool(0.0))
print("Q9", "ab" * 3, "5" + "5", 5 + 5)
print("Q10", end=" ")
print("a", "b", sep="-", end="!\n")
'''

PAPER_B = r'''
a = [1, 2, 3]
b = a
b += [4]
print("Q1", a)

t = (1, 2, 3)
u = t
u += (4,)
print("Q2", t, u)

grid = [[0] * 3] * 3
grid[0][0] = 1
print("Q3", grid)

nums = [1, 2, 3, 4]
print("Q4", nums[::-2], nums[-1:0:-1], nums[10:])

d = {"a": 1, "b": 2}
d["a"] = 3
print("Q5", list(d), d.get("z", 0), len(d))

s = "python"
print("Q6", s[1:4], s[-3:], s.find("z"), s.upper()[0])

one = (1,)
two = (1)
print("Q7", type(one).__name__, type(two).__name__)
print("Q8", {1, 2, 2, 3} | {3, 4}, {1, 2} & {2, 3})

x = [3, 1, 2]
y = x.sort()
print("Q9", x, y)

keys = {True: "a", 1: "b", 1.0: "c"}
print("Q10", len(keys), keys)
'''

PAPER_C = r'''
def f(a, b=2, *args, c, **kw):
    return a, b, args, c, kw
print("Q1", f(1, 3, 4, 5, c=6, d=7))

def add(item, items=[]):
    items.append(item)
    return items
add(1)
print("Q2", add(2))

x = 10
def g():
    print(x)
    x = 5
try:
    g()
except NameError as err:
    print("Q3", type(err).__name__)

funcs = [lambda: i for i in range(3)]
print("Q4", [fn() for fn in funcs])

def h():
    try:
        return "try"
    finally:
        print("Q5 finally runs")
print("Q5", h())

try:
    int("x")
except ValueError:
    print("Q6 V")
except Exception:
    print("Q6 E")
else:
    print("Q6 else")
finally:
    print("Q6 fin")

def nothing():
    pass
print("Q7", nothing())

try:
    raise KeyError("k")
except LookupError as err:
    print("Q8", type(err).__name__, err)

print("Q9", list(map(lambda n: n * 2, filter(lambda n: n % 2, range(6)))))

def outer():
    n = 0
    def inner():
        nonlocal n
        n += 1
        return n
    return inner
counter = outer()
counter()
print("Q10", counter())
'''

PAPER_D = r'''
class A:
    x = 1
a = A()
a.x = 2
print("Q1", A.x, a.x, "x" in a.__dict__)

class B:
    def __init__(self):
        self.__secret = 1
b = B()
print("Q2", hasattr(b, "__secret"), hasattr(b, "_B__secret"))

class P:
    def f(self):
        return "P"
class Q(P):
    def f(self):
        return "Q" + super().f()
print("Q3", Q().f(), isinstance(Q(), P), issubclass(P, Q))

print("Q4", "abc" < "abd", "Z" < "a", "10" < "9", ord("A"), chr(97))
print("Q5", "a,b,,c".split(","), " x  y ".split(), "-".join("abc"))
print("Q6", "Hello".center(9, "*"), "abc def".title(), "ab".isalpha(), "12".isdigit())

import math
print("Q7", math.floor(-2.5), math.ceil(-2.5), math.trunc(-2.5), math.sqrt(16))
print("Q8", __name__)

class C:
    def __str__(self):
        return "C!"
print("Q9", C(), str(C()) + "?", f"{C()}")

gen = (n * n for n in range(4))
print("Q10", next(gen), sum(gen))
print("Q11", [n for n in range(10) if n % 3 == 0], {n: n * n for n in range(3)})

def make(k):
    return lambda v: v * k
triple = make(3)
print("Q12", triple(4), make(2)("ab"))

class Base:
    def __init__(self):
        self.name = "base"
class Child(Base):
    def __init__(self):
        pass
try:
    print(Child().name)
except AttributeError as err:
    print("Q13", type(err).__name__)
'''

K.code('paper_a', PAPER_A)
K.code('paper_b', PAPER_B)
K.code('paper_c', PAPER_C)
K.code('paper_d', PAPER_D)

K.code('bugs', r'''
# Bug 1: changing a list while looping over it
nums = [2, 4, 5, 6]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)
print("bug 1:", nums)
nums = [2, 4, 5, 6]
print("fix 1:", [n for n in nums if n % 2 != 0])

# Bug 2: a string method does not change the string
name = "asha"
name.upper()
print("bug 2:", name)
name = name.upper()
print("fix 2:", name)

# Bug 3: a function that forgets return
def area(w, h):
    w * h
print("bug 3:", area(3, 4))
def area(w, h):
    return w * h
print("fix 3:", area(3, 4))

# Bug 4: a broad except before a narrow one
def parse(text):
    try:
        return int(text)
    except Exception:
        return "something went wrong"
    except ValueError:                      # never reached
        return "not a number"
print("bug 4:", parse("x"))
def parse(text):
    try:
        return int(text)
    except ValueError:
        return "not a number"
print("fix 4:", parse("x"))

# Bug 5: input() always gives a str
typed = "7"                                 # what input() would return
print("bug 5:", typed * 2)
print("fix 5:", int(typed) * 2)

# Bug 6: a built in name used as a variable
list = [1, 2, 3]
try:
    list("abc")
except TypeError as err:
    print("bug 6:", err)
del list                                    # removes the shadow, the built in is back
print("fix 6:", list("abc"))
''')

K.lesson('map', 'The exams and how to use this chapter', f'''
{src('pythoninstitute.org pages for PCEP-30-02, PCAP-31-03 and their syllabi, plus the pages for the newer PCEP-30-03 and PCAP-31-04, read on 7 November 2026.')}
<p>This chapter teaches nothing new. It revises the whole core part in the shape of the two Python Institute exams, with four practice papers, a bug hunt, the traps examiners love, a mock quiz and timed problems. Every question was written for this course, and every answer below was printed by a real run of Python 3.14.</p>
{table(['', 'PCEP-30-02 (entry)', 'PCAP-31-03 (associate)'], [
    ['Questions', '30', '40'],
    ['Time', '40 minutes, plus 5 for the agreement and tutorial', '65 minutes, plus 10 for the agreement and tutorial'],
    ['Pass mark', '70 % overall', '70 % overall'],
    ['Question types', 'Single and multiple choice, drag and drop, gap fill, sort, code fill, code insertion', 'Single and multiple choice, plus interactive and scenario items'],
    ['Blocks and weights', 'Fundamentals 18 %, control flow 29 %, data collections 25 %, functions and exceptions 28 %', 'Modules and packages 12 %, exceptions 14 %, strings 18 %, object oriented programming 34 %, miscellaneous (comprehensions, lambdas, closures, files) 22 %'],
    ['Chapters here', '1.1 to 4.3 and 5.1', '3.1, 4.1 to 6.2']])}
{note('The Python Institute has announced newer versions, PCEP-30-03 (35 questions, 50 minutes, 70 %) and PCAP-31-04 (42 questions, 65 minutes, 72 %), released on 31 October 2026. The skills tested are the same core Python, but check which version your voucher is for before you book.', 'warn')}
{table(['Paper', 'Covers', 'Lesson'], [
    ['A', 'Operators, numbers, loops, booleans, print', '2'],
    ['B', 'Lists, tuples, slices, dicts, sets, strings', '3'],
    ['C', 'Arguments, defaults, scope, closures, exceptions', '4'],
    ['D', 'Classes, inheritance, strings, modules, generators', '5']])}
{note('Cover the answers, write down what you think each line prints, then open the answers. A wrong guess tells you exactly which chapter to reread.', 'tip')}
''', kw=['PCEP', 'PCAP', 'exam', 'certification', 'Python Institute', 'pass mark', 'syllabus', 'revision'])

K.lesson('paper_a', 'Paper A: fundamentals and control flow', f'''
{show('Paper A: what does each line print', PAPER_A)}
{answers('Open the answers for paper A', table(['Q', 'Output', 'Why (chapter)'], [
    ['1', '-4 512', '** binds tighter than the minus sign, so -2 ** 2 is -(2 ** 2). ** groups from the right: 2 ** 9 (1.3)'],
    ['2', '-4 2 -2', '// rounds down (towards minus infinity). The result of % takes the sign of the divisor (1.3)'],
    ['3', 'False 2 4', '0.1 and 0.2 are not exact in binary. round() goes to the even neighbour on a tie (1.2)'],
    ['4', 'True True', 'Chained comparisons mean 3 &gt; 2 and 2 &gt; 1 and 1 == 1 (1.3)'],
    ['5', 'done 12', 'The loop ends normally when x reaches 12, so the else block runs (2.2)'],
    ['6', 'i is 1', 'break skips the else block. The loop variable keeps its last value (2.2)'],
    ['7', '31 15 5 1000', 'int(text, 16) reads hexadecimal. 0o is octal, 0b is binary, _ is only for reading (1.2)'],
    ['8', 'True False True False', 'Any non empty string is true, even "False". [0] is a non empty list (1.2)'],
    ['9', 'ababab 55 10', '* repeats a string, + joins strings, + adds numbers (1.2)'],
    ['10', 'a-b!', 'sep goes between the values, end replaces the new line (1.4)']]) + run('paper_a'))}
''', kw=['predict output', 'operator precedence', 'floor division', 'modulo sign', 'round half even', 'while else', 'for else', 'truthiness'])

K.lesson('paper_b', 'Paper B: data collections', f'''
{show('Paper B: what does each line print', PAPER_B)}
{answers('Open the answers for paper B', table(['Q', 'Output', 'Why (chapter)'], [
    ['1', '[1, 2, 3, 4]', 'b is the same list as a, and += changes a list in place (3.2)'],
    ['2', '(1, 2, 3) (1, 2, 3, 4)', 'A tuple cannot change, so += builds a new tuple and only u points to it (3.3)'],
    ['3', '[[1, 0, 0], [1, 0, 0], [1, 0, 0]]', '[row] * 3 repeats the SAME inner list three times. Use a comprehension (3.2)'],
    ['4', '[4, 2] [4, 3, 2] []', 'A negative step walks backwards. The stop index is never included. Slices never raise IndexError (3.2)'],
    ['5', "['a', 'b'] 0 2", 'Changing a value keeps the key in its place. get gives the default for a missing key (3.4)'],
    ['6', 'yth hon -1 P', 'Slices stop before the end index. find gives -1 when nothing is found (3.1)'],
    ['7', 'tuple int', 'The comma makes a tuple, not the brackets (3.3)'],
    ['8', '{1, 2, 3, 4} {2}', '| is union, &amp; is intersection, and a set keeps one copy of each value (3.3)'],
    ['9', '[1, 2, 3] None', 'sort changes the list and returns None. sorted would return a new list (3.2)'],
    ['10', "1 {True: 'c'}", 'True == 1 == 1.0 with equal hashes, so they are one key. The first key stays, the last value wins (3.4)']]) + run('paper_b'))}
''', kw=['aliasing', 'list multiplication trap', 'slicing', 'tuple comma', 'sort returns None', 'dict keys True 1'])

K.lesson('paper_c', 'Paper C: functions and exceptions', f'''
{show('Paper C: what does each line print', PAPER_C)}
{answers('Open the answers for paper C', table(['Q', 'Output', 'Why (chapter)'], [
    ['1', "(1, 3, (4, 5), 6, {'d': 7})", 'Positional values fill a and b, the rest go to *args. c is keyword only. Unknown keywords go to **kw (4.1)'],
    ['2', '[1, 2]', 'The default list is made once, when def runs, and shared by every call (4.1)'],
    ['3', 'UnboundLocalError', 'x = 5 anywhere in g makes x local in all of g, so print(x) reads it too early (4.2)'],
    ['4', '[2, 2, 2]', 'Each lambda looks up i when it is called, and by then i is 2 (4.3)'],
    ['5', 'finally runs, then try', 'finally runs before the function really returns (5.1)'],
    ['6', 'V, then fin', 'The first matching except wins. else runs only when no error happened. finally always runs (5.1)'],
    ['7', 'None', 'A function without return gives None (4.1)'],
    ['8', "KeyError 'k'", 'KeyError is a child of LookupError. str of a KeyError shows the key with quotes (5.1)'],
    ['9', '[2, 6, 10]', 'filter keeps 1, 3 and 5 (n % 2 is 1, which is true), map doubles them (4.3)'],
    ['10', '2', 'nonlocal lets inner change n in outer. The closure keeps n between calls (4.2)']]) + run('paper_c'))}
''', kw=['args kwargs', 'keyword only', 'mutable default', 'UnboundLocalError', 'late binding lambda', 'finally', 'nonlocal', 'closure'])

K.lesson('paper_d', 'Paper D: objects, strings and modules', f'''
{show('Paper D: what does each line print', PAPER_D)}
{answers('Open the answers for paper D', table(['Q', 'Output', 'Why (chapter)'], [
    ['1', '1 2 True', 'Assigning through an instance adds an instance attribute and leaves the class alone (6.1)'],
    ['2', 'False True', '__secret is name mangled to _B__secret (6.1)'],
    ['3', 'QP True False', 'super() calls the parent version. A child is an instance of its parent, not the other way round (6.2)'],
    ['4', 'True True True 65 a', 'Strings compare code point by code point. "Z" is 90, "a" is 97, and "1" comes before "9" (3.1)'],
    ['5', "['a', 'b', '', 'c'] ['x', 'y'] a-b-c", 'split(",") keeps empty parts. split() with no argument splits on runs of spaces and drops the ends (3.1)'],
    ['6', '**Hello** Abc Def True True', 'center pads both sides. title capitalises each word (3.1)'],
    ['7', '-3 -2 -2 4.0', 'floor goes down, ceil goes up, trunc cuts towards zero. sqrt always returns a float (5.2)'],
    ['8', '__main__', 'A file run directly gets the name __main__. Imported, it would get its module name (5.2)'],
    ['9', 'C! C!? C!', 'print, str and f-strings all use __str__ (6.1)'],
    ['10', '0 14', 'next takes 0. sum uses what is left: 1 + 4 + 9 (4.3)'],
    ['11', '[0, 3, 6, 9] {0: 0, 1: 1, 2: 4}', 'A list comprehension with if, and a dict comprehension (4.3)'],
    ['12', '12 abab', 'make returns a closure that remembers k. * works on strings too (4.2)'],
    ['13', 'AttributeError', 'Child.__init__ never calls super().__init__(), so name is never set (6.2)']]) + run('paper_d'))}
''', kw=['class attribute', 'name mangling', 'super', 'string comparison', 'split', 'math floor ceil trunc', '__name__', 'generator', 'closure'])

K.lesson('bugs', 'Find the bug', f'''
{run('bugs')}
{steps('Six bugs examiners and interviewers love', [
    '<b>Bug 1.</b> Removing items from a list while a for loop walks it skips the item after each removal, so 4 survives. Build a new list instead (3.2).',
    '<b>Bug 2.</b> Strings never change. upper() returns a new string, which was thrown away. Assign the result (3.1).',
    '<b>Bug 3.</b> The function computes w * h but never returns it, so the caller gets None (4.1).',
    '<b>Bug 4.</b> except Exception catches ValueError first, so the narrow handler can never run. Put specific handlers before general ones (5.1).',
    '<b>Bug 5.</b> input() returns text, and "7" * 2 is "77". Convert with int() first (1.4).',
    '<b>Bug 6.</b> list = [...] hides the built in list, so list("abc") calls a list object and fails. Never use built in names as variables (4.2).'])}
''', kw=['find the bug', 'modify list while iterating', 'string immutable', 'missing return', 'except order', 'input is str', 'shadowing built ins'])

K.lesson('traps', 'The traps in one table', f'''
{table(['Trap', 'Looks like', 'Really', 'Chapter'], [
    ['Power and minus', '-2 ** 2 is 4', '-4', '1.3'],
    ['Floor division', '-7 // 2 is -3', '-4', '1.3'],
    ['Rounding', 'round(2.5) is 3', '2 (round half to even)', '1.2'],
    ['Integer from text', 'int("3.5") is 3', 'ValueError (use int(float("3.5")))', '1.2'],
    ['Boolean of text', 'bool("False") is False', 'True', '1.2'],
    ['is and ==', 'a is b means equal', 'is means the same object', '1.3'],
    ['Copy', 'b = a copies a list', 'b is another name for the same list', '3.2'],
    ['Nested repeat', '[[0] * 3] * 3 makes 3 rows', 'It makes 3 names for one row', '3.2'],
    ['One item tuple', '(5) is a tuple', 'It is the int 5, write (5,)', '3.3'],
    ['Empty set', '{} is an empty set', 'It is an empty dict, write set()', '3.3'],
    ['sort', 'x = x.sort() sorts', 'x becomes None', '3.2'],
    ['Default argument', 'def f(x=[]) gets a new list each call', 'One list for all calls', '4.1'],
    ['Scope', 'Reading a global inside a function that also assigns it works', 'UnboundLocalError', '4.2'],
    ['Lambda in a loop', 'Each lambda keeps its own i', 'They all see the last i', '4.3'],
    ['else on loops', 'Runs when the loop runs', 'Runs when the loop was not stopped by break', '2.2'],
    ['finally', 'return skips finally', 'finally always runs', '5.1'],
    ['Class attribute', 'obj.x = 1 changes the class', 'It adds an instance attribute', '6.1'],
    ['Forgotten super()', 'Parent attributes exist anyway', 'AttributeError', '6.2']])}
''', kw=['exam traps', 'common mistakes', 'gotchas', 'tricky questions'])

K.lesson('plan', 'Exam technique and a study plan', f'''
{fxs(fx('Time per question', 'minutes &times; 60 / questions', 'PCEP: 40 &times; 60 / 30 = 80 seconds. PCAP: 65 &times; 60 / 40 = 97.5 seconds.', key=True),
     fx('Questions to pass (if every item counts the same)', 'correct needed = ceil(pass mark &times; questions)', 'PCEP: 0.7 &times; 30 = 21. PCAP: 0.7 &times; 40 = 28.', key=True),
     fx('Points by block', 'block share of the exam = block weight', 'Object oriented programming is 34 % of PCAP, more than any other block, so it deserves the most practice.'))}
{steps('A four week plan', [
    'Week 1: chapters 1.1 to 2.2. Do paper A without looking, then reread the chapter behind every wrong answer.',
    'Week 2: chapters 3.1 to 3.4 and paper B. Practise slicing and dict methods until you can predict them instantly.',
    'Week 3: chapters 4.1 to 5.3 and paper C. Write small programs for args, scope, closures and exceptions.',
    'Week 4: chapters 6.1 and 6.2 and paper D, then the mock quiz in the Quiz tab with a timer. Aim for 85 % to leave a safety margin.'])}
{note('In the exam: read the whole snippet before the options, trace it line by line on scratch paper, watch for indentation and for a missing comma or bracket that turns the answer into "the code raises an error". Mark hard questions and come back, every question is worth the same.', 'exam')}
{ladder(
    '<p>PCEP level: predict the output of short programs with operators, loops, lists, dicts, strings, functions and simple try and except.</p>',
    '<p>PCAP level: add modules and packages, the exception tree, string methods, classes, inheritance, comprehensions, lambdas, closures and files.</p>',
    '<p>PCPP level (Advanced part): decorators, the data model, generators, testing, concurrency, design patterns and the standard library in depth.</p>',
    '<p>Expert: explain why each trap happens from the language reference (evaluation order, the data model, the C3 MRO, name binding rules) and spot them in code review before they reach production.</p>')}
''', kw=['exam technique', 'time per question', 'pass mark', 'study plan', 'PCPP'])

lc(11, 'Container With Most Water', 'container-with-most-water', 'm', 'Two pointers', 'Start at both ends. The area is width times the shorter wall. Move the shorter wall inwards, because only that can make the area bigger.', r'''
def max_area(height):
    left = 0
    right = len(height) - 1
    best = 0
    while left < right:
        area = (right - left) * min(height[left], height[right])
        best = max(best, area)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best
''', [('max_area([1, 8, 6, 2, 5, 4, 8, 3, 7])', 49), ('max_area([1, 1])', 1)])
lc(12, 'Integer to Roman', 'integer-to-roman', 'm', 'Greedy table', 'Walk a table from 1000 (M) down to 1 (I), including 900, 400, 90, 40, 9 and 4. Take each value as many times as it fits.', r'''
def int_to_roman(num):
    table = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
             (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    result = ""
    for value, letters in table:
        while num >= value:
            result = result + letters
            num = num - value
    return result
''', [('int_to_roman(3749)', 'MMMDCCXLIX'), ('int_to_roman(58)', 'LVIII'), ('int_to_roman(1994)', 'MCMXCIV')])
lc(15, '3Sum', '3sum', 'm', 'Sort, then two pointers', 'Sort the list. For each first number, look for two more with two pointers. Skip equal neighbours so no triple repeats.', r'''
def three_sum(nums):
    nums = sorted(nums)
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        left = i + 1
        right = len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                right -= 1
    return result
''', [('three_sum([-1, 0, 1, 2, -1, -4])', [[-1, -1, 2], [-1, 0, 1]]), ('three_sum([0, 1, 1])', []), ('three_sum([0, 0, 0])', [[0, 0, 0]])])
lc(17, 'Letter Combinations of a Phone Number', 'letter-combinations-of-a-phone-number', 'm', 'Grow the list digit by digit', 'Start with [""] and, for every digit, add each of its letters to every string made so far.', r'''
def letter_combinations(digits):
    if digits == "":
        return []
    keys = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    result = [""]
    for digit in digits:
        result = [start + letter for start in result for letter in keys[digit]]
    return result
''', [('letter_combinations("23")', ['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf']), ('letter_combinations("")', []), ('letter_combinations("2")', ['a', 'b', 'c'])])
lc(36, 'Valid Sudoku', 'valid-sudoku', 'm', 'Sets for rows, columns and boxes', 'Keep a set for each row, column and 3 by 3 box. A digit seen twice in any of them makes the board invalid. The box number is (r // 3) * 3 + c // 3.', r'''
def is_valid_sudoku(board):
    rows = [set() for i in range(9)]
    cols = [set() for i in range(9)]
    boxes = [set() for i in range(9)]
    for r in range(9):
        for c in range(9):
            value = board[r][c]
            if value == ".":
                continue
            b = (r // 3) * 3 + c // 3
            if value in rows[r] or value in cols[c] or value in boxes[b]:
                return False
            rows[r].add(value)
            cols[c].add(value)
            boxes[b].add(value)
    return True


def make_board(top_left):
    # a board that is empty except for the first row given as a string
    board = [["."] * 9 for i in range(9)]
    for c in range(len(top_left)):
        board[0][c] = top_left[c]
    return board
''', [('is_valid_sudoku(make_board("53..7...."))', True), ('is_valid_sudoku(make_board("53..7...5"))', False)])
lc(38, 'Count and Say', 'count-and-say', 'm', 'Describe the previous term', 'Read the previous string in runs of equal digits and write the run length followed by the digit.', r'''
def count_and_say(n):
    term = "1"
    for step in range(n - 1):
        new = ""
        i = 0
        while i < len(term):
            j = i
            while j < len(term) and term[j] == term[i]:
                j += 1
            new = new + str(j - i) + term[i]
            i = j
        term = new
    return term
''', [('count_and_say(1)', '1'), ('count_and_say(4)', '1211'), ('count_and_say(6)', '312211')])
lc(56, 'Merge Intervals', 'merge-intervals', 'm', 'Sort by start', 'Sort the intervals by start. If the next one starts before the last merged one ends, stretch the end, otherwise start a new interval.', r'''
def merge(intervals):
    result = []
    for start, end in sorted(intervals):
        if result and start <= result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result
''', [('merge([[1, 3], [2, 6], [8, 10], [15, 18]])', [[1, 6], [8, 10], [15, 18]]), ('merge([[1, 4], [4, 5]])', [[1, 5]])])
lc(67, 'Add Binary', 'add-binary', 'e', 'Add from the right with a carry', 'Walk both strings from the end, add the digits and the carry, write total % 2 and carry total // 2.', r'''
def add_binary(a, b):
    i = len(a) - 1
    j = len(b) - 1
    carry = 0
    result = ""
    while i >= 0 or j >= 0 or carry:
        total = carry
        if i >= 0:
            total += int(a[i])
            i -= 1
        if j >= 0:
            total += int(b[j])
            j -= 1
        result = str(total % 2) + result
        carry = total // 2
    return result
''', [('add_binary("11", "1")', '100'), ('add_binary("1010", "1011")', '10101')])
lc(238, 'Product of Array Except Self', 'product-of-array-except-self', 'm', 'Products from the left and from the right', 'answer[i] is the product of everything left of i times everything right of i. Two passes, no division.', r'''
def product_except_self(nums):
    n = len(nums)
    answer = [1] * n
    left = 1
    for i in range(n):
        answer[i] = left
        left = left * nums[i]
    right = 1
    for i in range(n - 1, -1, -1):
        answer[i] = answer[i] * right
        right = right * nums[i]
    return answer
''', [('product_except_self([1, 2, 3, 4])', [24, 12, 8, 6]), ('product_except_self([-1, 1, 0, -3, 3])', [0, 0, 9, 0, 0])])
lc(448, 'Find All Numbers Disappeared in an Array', 'find-all-numbers-disappeared-in-an-array', 'e', 'Set difference', 'The numbers should be 1 to n. Put the list in a set and keep the numbers from 1 to n that are not in it.', r'''
def find_disappeared_numbers(nums):
    seen = set(nums)
    return [n for n in range(1, len(nums) + 1) if n not in seen]
''', [('find_disappeared_numbers([4, 3, 2, 7, 8, 2, 3, 1])', [5, 6]), ('find_disappeared_numbers([1, 1])', [2])])

K.lesson('leetcode', 'LeetCode review set', leet('<p>Ten problems that mix everything in the core part: loops, two pointers, sets, dicts, strings and comprehensions. Try to solve each in under 25 minutes, as you would in a coding interview.</p>'), kw=['LeetCode', 'review', 'two pointers', 'intervals', 'sudoku', 'roman numerals'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'PCEP-30-02: 30 questions, 40 minutes, 70 %. PCAP-31-03: 40 questions, 65 minutes, 70 %. Newer versions started on 31 October 2026.',
    'Operators: ** before unary minus and right to left, // rounds down, % takes the sign of the divisor, round goes to even on ties.',
    'Loops: else runs only without break. Never change a list while looping over it.',
    'Collections: assignment makes aliases, [[0] * 3] * 3 shares one row, (1,) is a tuple, sort returns None, True and 1 are the same dict key.',
    'Functions: mutable defaults are shared, assigning a name makes it local, lambdas in loops bind late, nonlocal changes an enclosing name.',
    'Exceptions: first matching except wins, specific before general, else when no error, finally always.',
    'Objects: instance assignment never changes the class, __x is mangled, call super().__init__().',
    'Technique: about 80 to 98 seconds per question, trace on paper, aim for 85 % in practice.'],
    'The Advanced part goes on to the PCPP level: the data model, decorators, generators, testing, concurrency and the standard library.')}
{files('Three exam style tasks: a marks report from a dict, a Caesar cipher that keeps case and punctuation, and a settings parser that raises ValueError on bad lines.')}
''', kw=['summary', 'recap'])

# ---------------- mock quiz: PCEP style ----------------
K.quiz('e', 'What does print(3 * "ab" + "c") print?', ['ababab c', 'abababc', '3abc', 'TypeError'], 1, 'Repeat, then join.', '* repeats the string, + joins with no space.')
K.quiz('e', 'What is the value of 17 % 5?', ['3', '2', '3.4', '12'], 1, 'Remainder.', '17 = 3 &times; 5 + 2.')
K.quiz('e', 'Which of these is a valid variable name?', ['2nd', 'my-name', '_total', 'class'], 2, 'Letters, digits, underscore, not starting with a digit, not a keyword.', '_total is fine. class is a keyword.')
K.quiz('e', 'What is type(7 / 7)?', ['int', 'float', 'bool', 'str'], 1, 'True division.', '/ always returns a float: 1.0.')
K.quiz('e', 'How many times does print run in for i in range(2, 10, 3)?', ['2', '3', '4', '8'], 1, 'Values 2, 5, 8.', 'range stops before 10, so 2, 5 and 8.')
K.quiz('m', 'What is printed by x = 5, then x += x * 2, then print(x)?', ['10', '15', '20', '25'], 1, 'Right side first.', 'x * 2 is 10, and 5 + 10 is 15.')
K.quiz('m', 'What does print(not 0 or 5 and 0) print?', ['True', 'False', '0', '5'], 0, 'not, then and, then or.', 'not 0 is True. or stops at the first true value and returns it.')
K.quiz('m', 'What is len([1, [2, 3], (4, 5, 6)])?', ['6', '3', '2', '5'], 1, 'Top level items.', 'The list has three items: an int, a list and a tuple.')
K.quiz('m', 'd = {"a": 1}. What does d["b"] do?', ['Returns None', 'Raises KeyError', 'Returns 0', 'Adds "b"'], 1, 'Missing key.', 'Square brackets on a missing key raise KeyError. Use get for a default.')
K.quiz('m', 'What does "Python"[-1::-2] give?', ['"nhy"', '"nohtyP"', '"Pto"', '"nt"'], 0, 'Backwards in steps of 2.', 'From n, every second letter backwards: n, h, y.')
K.quiz('m', 'def f(x): x.append(1). Then a = [] and f(a). What is a?', ['[]', '[1]', 'None', 'Error'], 1, 'Same object.', 'The function changes the very list a points to.')
K.quiz('h', 'What does this print? i = 0, then while i < 3: i += 1, then if i == 2: continue, then print(i, end="")', ['123', '13', '12', '3'], 1, 'continue skips the print.', 'i becomes 1 (printed), 2 (skipped), 3 (printed).')
K.quiz('h', 'Which call raises an error? def f(a, b=1, *, c=2): ...', ['f(1)', 'f(1, 2)', 'f(1, 2, 3)', 'f(1, c=3)'], 2, 'After * only keywords.', 'c is keyword only, so a third positional value has nowhere to go: TypeError.')
K.quiz('h', 'What is the result of try: print(1/0), then except ArithmeticError: print("A"), then except ZeroDivisionError: print("Z")?', ['Z', 'A', 'A then Z', 'Nothing'], 1, 'The first match wins.', 'ZeroDivisionError is a child of ArithmeticError, so the first handler catches it.')
K.quiz('h', 'What does print(list(range(5))[1:-1:2]) print?', ['[1, 3]', '[1, 2, 3]', '[1]', '[0, 2, 4]'], 0, 'Indexes 1 and 3.', 'From index 1 up to (not including) the last, in steps of 2.')

# ---------------- mock quiz: PCAP style ----------------
K.quiz('e', 'What does "a-b-c".split("-", 1) return?', ['["a", "b", "c"]', '["a", "b-c"]', '["a-b", "c"]', '"a"'], 1, 'maxsplit.', 'The second argument limits it to one split.')
K.quiz('e', 'Which statement imports only sqrt from math?', ['import math.sqrt', 'from math import sqrt', 'import sqrt from math', 'using math.sqrt'], 1, 'from ... import.', 'from math import sqrt binds just sqrt.')
K.quiz('e', 'Which method does print(obj) use?', ['__repr__ always', '__str__, or __repr__ if __str__ is missing', '__print__', '__init__'], 1, 'For users.', 'print calls str, which uses __str__ and falls back to __repr__.')
K.quiz('m', 'What does [x * 2 for x in "ab"] give?', ['["aa", "bb"]', '["a2", "b2"]', '[2, 4]', 'TypeError'], 0, 'Strings repeat.', 'Each character is repeated twice.')
K.quiz('m', 'What is the parent class of FileNotFoundError?', ['IOError only', 'OSError', 'LookupError', 'ValueError'], 1, 'Operating system errors.', 'File errors are OSError children (IOError is another name for OSError).')
K.quiz('m', 'A package folder is imported with import shop. Which file runs?', ['shop.py in the folder', 'shop/__init__.py', 'shop/__main__.py', 'Nothing runs'], 1, 'The package file.', 'Importing a regular package runs its __init__.py.')
K.quiz('m', 'class A: pass and class B(A): pass. What is B.__bases__?', ['(A,)', '(object,)', '(A, object)', 'A'], 0, 'Direct parents only.', '__bases__ is a tuple of the direct parents.')
K.quiz('m', 'What does chr(ord("a") + 2) give?', ['"c"', '"b"', '99', '"a2"'], 0, 'Code points.', 'ord("a") is 97, 97 + 2 is 99, chr(99) is "c".')
K.quiz('m', 'f = open("x.txt", "w"). What happens to an existing x.txt?', ['It is kept and added to', 'It is emptied', 'An error is raised', 'It is renamed'], 1, 'Write mode.', '"w" truncates the file.')
K.quiz('h', 'What does sorted(["b", "A", "a", "B"]) return?', ['["A", "a", "B", "b"]', '["A", "B", "a", "b"]', '["a", "A", "b", "B"]', '["a", "b", "A", "B"]'], 1, 'Code points: capitals first.', 'Uppercase letters (65 to 90) come before lowercase (97 to 122).')
K.quiz('h', 'def gen(): yield 1, then yield 2. What is list(gen()) + list(gen())?', ['[1, 2]', '[1, 2, 1, 2]', '[]', 'Error'], 1, 'Two separate generators.', 'Each call makes a fresh generator.')
K.quiz('h', 'class A: def __init__(self): self.v = 1, and class B(A): def __init__(self): super().__init__() then self.v += 1. What is B().v?', ['1', '2', 'AttributeError', 'None'], 1, 'Parent first.', 'super sets v to 1, then B adds 1.')
K.quiz('h', 'What is the output of print(*[1, 2, 3], sep=":")?', ['[1, 2, 3]', '1:2:3', '1 2 3', ':1:2:3'], 1, 'Unpacking.', '* passes the items as separate arguments, and sep goes between them.')
K.quiz('x', 'In the style of a Stanford CS106A final: x = [1, 2, 3], then y = x[:], then y[0] = 9, then z = x, then z[1] = 8. What is print(x, y)?', ['[9, 8, 3] [9, 2, 3]', '[1, 8, 3] [9, 2, 3]', '[1, 2, 3] [9, 2, 3]', '[9, 8, 3] [9, 8, 3]'], 1, 'Slice copies, assignment aliases.', 'y is a copy, z is the same list as x. Only z changes x.')
K.quiz('x', 'In the style of a Cambridge Part IA exam: funcs = [lambda n=i: n * 10 for i in range(3)]. What is [f() for f in funcs]?', ['[20, 20, 20]', '[0, 10, 20]', '[0, 0, 0]', 'TypeError'], 1, 'Defaults are evaluated at def time.', 'n=i stores the current i as a default when each lambda is made, which fixes the late binding trap.')

K.calc('e', 'PCEP-30-02 has 30 questions in 40 minutes. How many seconds per question?', '80', 'Minutes to seconds first.', ['40 &times; 60 = 2,400 seconds.', '2,400 / 30.', eq('80 seconds')], check=40 * 60 // 30)
K.calc('e', 'How many correct answers are needed for 70 % of 30 questions, if every question counts the same?', '21', '0.7 times 30.', ['0.7 &times; 30 = 21.', 'It is a whole number.', eq('21')], check=21)
K.calc('e', 'What is 2 ** 3 ** 2?', '512', 'Right to left.', ['3 ** 2 = 9 first.', '2 ** 9.', eq('512')], check=2 ** 3 ** 2)
K.calc('m', 'What is -7 // 2 + -7 % 2?', '-3', 'Floor, then the remainder with the sign of 2.', ['-7 // 2 = -4 (rounded down).', '-7 % 2 = 1, because -4 &times; 2 + 1 = -7.', eq('-4 + 1 = -3')], check=-7 // 2 + -7 % 2)
K.calc('m', 'PCAP-31-03 has 40 questions in 65 minutes. How many seconds per question?', '97.5', 'Minutes to seconds.', ['65 &times; 60 = 3,900 seconds.', '3,900 / 40.', eq('97.5 seconds')], check=65 * 60 / 40)
K.calc('m', 'The newer PCAP-31-04 needs 72 % of 42 questions. How many correct answers, rounding up, if every question counts the same?', '31', 'Round up.', ['0.72 &times; 42 = 30.24.', 'You cannot answer 0.24 of a question.', eq('31')], check=-(-72 * 42 // 100))
K.calc('m', 'What is len(set("mississippi"))?', '4', 'Distinct letters.', ['The letters used are m, i, s and p.', 'A set keeps one copy of each.', eq('4')], check=len(set("mississippi")))
K.calc('h', 'How many times does the loop body run? i = 1, then while i < 100: i *= 3.', '5', 'Count the values of i before each check.', ['i takes 1, 3, 9, 27, 81 inside the loop.', 'After that i is 243, which stops it.', eq('5 times')], check=5)
K.calc('h', 'What is sum(x for x in range(1, 101) if x % 2 == 0)?', '2550', 'The even numbers 2 to 100.', ['There are 50 even numbers.', 'Their average is (2 + 100) / 2 = 51.', eq('50 &times; 51 = 2,550')], check=sum(x for x in range(1, 101) if x % 2 == 0))
K.calc('x', 'In the style of an MIT 6.100L exam: def f(n): return 1 if n < 2 else f(n - 1) + f(n - 2). How many calls in total does f(5) make, the first one included?', '15', 'calls(n) = 1 + calls(n &minus; 1) + calls(n &minus; 2).', ['calls(0) = calls(1) = 1. calls(2) = 3, calls(3) = 5.', 'calls(4) = 1 + 5 + 3 = 9.', eq('calls(5) = 1 + 9 + 5 = 15')], check=15)

K.assign('report', 'e', 'Marks report',
         '<p>Write <code>report(marks)</code> for a dict of name to mark. Return a tuple of (average rounded to 1 decimal place, the name with the highest mark, a sorted list of the names with marks below 40). For an empty dict return <code>(0, None, [])</code>.</p>',
         '''
def report(marks):
    # your code here
    pass
''', [('report({"Asha": 88, "Ravi": 35, "Meera": 95, "Ali": 20})', [59.5, 'Meera', ['Ali', 'Ravi']]), ('report({})', [0, None, []]), ('report({"Zoe": 40})', [40.0, 'Zoe', []])],
         '''
def report(marks):
    if len(marks) == 0:
        return (0, None, [])
    total = 0
    best = None
    low = []
    for name in marks:
        total = total + marks[name]
        if best is None or marks[name] > marks[best]:
            best = name
        if marks[name] < 40:
            low.append(name)
    return (round(total / len(marks), 1), best, sorted(low))
''', 'Loop once over the names. Keep a running total, the best name so far and a list of low names.', '<p>One loop answers all three questions. This is the shape of many PCEP coding items: a dict, a loop and a few running values.</p>')
K.assign('caesar', 'm', 'Caesar cipher',
         '<p>Write <code>caesar(text, shift)</code> that moves each letter shift places along the alphabet, wrapping from z to a. Keep capitals as capitals and leave every other character unchanged. A negative shift moves backwards.</p>',
         '''
def caesar(text, shift):
    # your code here
    pass
''', [('caesar("abc xyz", 3)', 'def abc'), ('caesar("Hello, World!", 1)', 'Ifmmp, Xpsme!'), ('caesar("def", -3)', 'abc'), ('caesar(caesar("Python 3.14", 7), -7)', 'Python 3.14')],
         '''
def caesar(text, shift):
    result = ""
    for ch in text:
        if "a" <= ch <= "z":
            result = result + chr((ord(ch) - ord("a") + shift) % 26 + ord("a"))
        elif "A" <= ch <= "Z":
            result = result + chr((ord(ch) - ord("A") + shift) % 26 + ord("A"))
        else:
            result = result + ch
    return result
''', 'Turn a letter into 0 to 25 with ord(ch) &minus; ord("a"), add the shift, take % 26, and turn it back with chr.', '<p>% 26 handles both wrapping and negative shifts, because Python gives a positive remainder for a positive divisor. This is a classic PCAP strings item.</p>')
K.assign('settings', 'm', 'Settings parser',
         '<p>Write <code>parse_settings(text)</code> that reads lines like <code>name = value</code> into a dict. Strip spaces around names and values, skip blank lines and lines that start with <code>#</code>. If a line has no <code>=</code>, raise <code>ValueError</code> with the message <code>"line 3: missing ="</code> (the real line number, counting from 1). raises() is a test helper.</p>',
         '''
def parse_settings(text):
    # your code here
    pass


def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__ + ": " + str(err)
    return None
''', [('parse_settings("host = example.com\\nport=8080\\n")', {'host': 'example.com', 'port': '8080'}), ('parse_settings("# comment\\n\\nmode = fast")', {'mode': 'fast'}), ('raises(parse_settings, "a = 1\\n\\nbroken")', 'ValueError: line 3: missing ='), ('parse_settings("url = a=b")', {'url': 'a=b'})],
         '''
def parse_settings(text):
    settings = {}
    number = 0
    for line in text.split("\\n"):
        number = number + 1
        line = line.strip()
        if line == "" or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError("line " + str(number) + ": missing =")
        name, value = line.split("=", 1)
        settings[name.strip()] = value.strip()
    return settings


def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__ + ": " + str(err)
    return None
''', 'Count lines as you loop. split("=", 1) splits only at the first =, so values may contain = too.', '<p>Raising a clear ValueError with the line number is much kinder than a crash deep inside the program. This mixes strings, dicts and exceptions, the three biggest PCAP blocks after objects.</p>')

K.must('Exam facts', 'PCEP-30-02: 30 questions, 40 min, 70 %. PCAP-31-03: 40 questions, 65 min, 70 %. OOP is 34 % of PCAP.')
K.must('Operator traps', '-2 ** 2 is -4, 2 ** 3 ** 2 is 512, -7 // 2 is -4, -7 % 3 is 2, round(2.5) is 2, 0.1 + 0.2 != 0.3.')
K.must('Collection traps', 'b = a aliases, [[0] * 3] * 3 shares a row, (1,) is a tuple, {} is a dict, sort returns None.')
K.must('Function traps', 'Mutable defaults are shared, assignment makes a name local, lambdas in loops bind late, finally always runs.')
K.must('Object traps', 'obj.x = v never changes the class, __x becomes _Class__x, a child __init__ must call super().__init__().')

T = K.topic(
    slug='py-core-exam', topic='py-core-exam', kind='revision',
    step=(7, 'Exam practice', 'py-c7', 'Practise for the PCEP and PCAP exams with four papers, a bug hunt, the common traps, a mock quiz and timed problems.', 'All levels'),
    title='Exam practice: PCEP and PCAP style papers', short='Core exam practice', badge='7.1', minutes=90,
    lead='Revise the whole core part in the shape of the Python Institute exams: four predict the output papers with real answers, a bug hunt, the traps in one table, exam technique, a mock quiz of 30 questions and timed problems.',
    desc='PCEP-30-02 and PCAP-31-03 facts and block weights, the newer PCEP-30-03 and PCAP-31-04, predict the output papers on operators, loops, collections, functions, exceptions, classes, strings and modules, six classic bugs, a table of exam traps, time per question and pass marks, a four week plan, a mock quiz, worked problems and exam style coding tasks.',
    summary='Four practice papers, a bug hunt, the traps table, exam technique and a mock quiz.',
    keywords=['PCEP', 'PCAP', 'exam practice', 'mock quiz', 'predict output', 'find the bug', 'traps', 'certification', 'revision'],
    recap='<p>Trace every snippet on paper, know the traps by heart and practise under time. The exam rewards careful reading more than clever code.</p>',
    added='2026-11-07', leet=leet_items())
