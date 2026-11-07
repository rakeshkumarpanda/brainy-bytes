# Advanced Python 8.1: exam practice for the PCPP1 level. Revises the whole Advanced part in the shape of the Python
# Institute PCPP-32-101 exam. The official pages (pythoninstitute.org/pcpp1) could not be opened from the build
# machine on 2026-11-07 (the proxy refused the site), so the exam facts come from two training providers that agree
# (lumifywork.com/en-au/certifications/pcpp1 and open-exam-prep.com/practice/pcpp1, read 2026-11-07), and the page
# tells the reader to check the official page. Block weights were not confirmed, so they are not shown.
# Every question is an original practice question written for this course. Every answer was printed by a real run.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items, show

chapter('py-adv-exam')
K = Kit()


def answers(title, body):
    return f'<details class="deep"><summary>{title}</summary><div class="deep-b">{body}</div></details>'


PAPER_A = r'''
class V:
    def __init__(self, x):
        self.x = x

    def __add__(self, other):
        return V(self.x + other.x)

    def __eq__(self, other):
        return self.x == other.x

    def __repr__(self):
        return f"V({self.x})"


print("Q1", V(1) + V(2), V(1) == V(1), V(1) is V(1))
try:
    print({V(1)})
except TypeError as err:
    print("Q2", type(err).__name__)


class A:
    def who(self):
        return "A"


class B(A):
    def who(self):
        return "B" + super().who()


class C(A):
    def who(self):
        return "C" + super().who()


class D(B, C):
    pass


print("Q3", D().who(), [k.__name__ for k in D.__mro__])


class Counter:
    count = 0

    def __init__(self):
        Counter.count += 1

    @classmethod
    def made(cls):
        return cls.count

    @staticmethod
    def hello():
        return "hi"


Counter()
Counter()
print("Q4", Counter.made(), Counter.hello())


class Temp:
    def __init__(self):
        self._c = 0

    @property
    def c(self):
        return self._c

    @c.setter
    def c(self, value):
        if value < -273.15:
            raise ValueError("too cold")
        self._c = value


t = Temp()
t.c = 25
try:
    t.c = -300
except ValueError as err:
    print("Q5", t.c, err)

from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self):
        ...


try:
    Shape()
except TypeError:
    print("Q6 cannot make a Shape")


def double(fn):
    def wrapper(*args):
        return fn(*args) * 2
    return wrapper


@double
def five():
    return 5


print("Q7", five(), five.__name__)


def repeat(n):
    def decorator(fn):
        def wrapper():
            return [fn() for _ in range(n)]
        return wrapper
    return decorator


@repeat(3)
def letter():
    return "x"


print("Q8", letter())


class Meta(type):
    def __new__(mcs, name, bases, namespace):
        namespace["tag"] = name.lower()
        return super().__new__(mcs, name, bases, namespace)


class Thing(metaclass=Meta):
    pass


print("Q9", Thing.tag, type(Thing).__name__, type(type).__name__)


class Slim:
    __slots__ = ("a",)


s = Slim()
s.a = 1
try:
    s.b = 2
except AttributeError:
    print("Q10", hasattr(s, "__dict__"))

import copy

data = [[1, 2], [3]]
shallow = copy.copy(data)
deep = copy.deepcopy(data)
data[0].append(9)
print("Q11", shallow[0], deep[0], shallow is data, shallow[0] is data[0])
'''

PAPER_B = r'''
def gen():
    print("start")
    yield 1
    print("middle")
    yield 2


g = gen()
print("Q1 made")
print("Q1", next(g))
print("Q1", list(g))


def count(n):
    x = yield n
    print("got", x)
    yield x * 2


c = count(5)
print("Q2", next(c), c.send(10))


def inner():
    yield 1
    yield 2
    return "done"


def outer():
    result = yield from inner()
    yield result


print("Q3", list(outer()))

it = iter([1, 2, 3])
print("Q4", 2 in it, list(it))

import itertools

print("Q5", list(itertools.islice(itertools.count(10, 5), 3)), list(itertools.accumulate([1, 2, 3])))
print("Q6", list(itertools.chain("ab", [1])), [k for k, grp in itertools.groupby("aabbba")], len(list(itertools.combinations(range(5), 2))))

from contextlib import contextmanager


@contextmanager
def tag(name):
    print(f"<{name}>")
    try:
        yield name.upper()
    finally:
        print(f"</{name}>")


with tag("b") as t:
    print("Q7", t)


class Quiet:
    def __enter__(self):
        return self

    def __exit__(self, kind, value, tb):
        print("Q8 exit saw", kind.__name__)
        return True


with Quiet():
    1 / 0
print("Q8 after the with block")

try:
    try:
        {}["k"]
    except KeyError as err:
        raise ValueError("bad") from err
except ValueError as err:
    print("Q9", type(err.__cause__).__name__, err.__suppress_context__)

try:
    raise ExceptionGroup("many", [ValueError("a"), TypeError("b"), ValueError("c")])
except* ValueError as group:
    print("Q10 V", len(group.exceptions))
except* TypeError as group:
    print("Q10 T", len(group.exceptions))
'''

PAPER_C = r'''
import csv
import heapq
import io
import json
import re
import sqlite3
from collections import Counter, defaultdict, deque, namedtuple

print("Q1", re.findall(r"\d+", "a1b22c333"), re.sub(r"(\w+)@(\w+)", r"\2 at \1", "ann@home"))
print("Q2", re.match(r"b", "abc"), bool(re.search(r"b", "abc")), re.fullmatch(r"a.c", "abc") is not None)
print("Q3", re.findall(r"<.+>", "<a><b>"), re.findall(r"<.+?>", "<a><b>"))
print("Q4", json.dumps({"b": (1, 2), "a": None}, sort_keys=True), json.loads("[1, 2.0, true]"))
rows = list(csv.reader(io.StringIO('x,"y, z",3\n')))
print("Q5", rows, type(rows[0][2]).__name__)
print("Q6", Counter("banana").most_common(2), dict(defaultdict(int, a=1)))
d = deque([1, 2, 3], maxlen=3)
d.append(4)
d.appendleft(0)
print("Q7", list(d))
nums = [5, 1, 4, 2]
heapq.heapify(nums)
print("Q8", nums[0], heapq.nsmallest(2, [5, 1, 4, 2]), heapq.heappop(nums), nums)
Point = namedtuple("Point", "x y")
p = Point(1, 2)
print("Q9", p.x + p[1], p._replace(x=9), p._asdict())
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE t (n INTEGER)")
db.executemany("INSERT INTO t VALUES (?)", [(3,), (1,), (2,)])
print("Q10", db.execute("SELECT COUNT(*), MAX(n), SUM(n) FROM t").fetchone())
'''

PAPER_D = r'''
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache, partial, reduce, wraps


@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print("Q1", fib(30), fib.cache_info().misses)

square = partial(pow, exp=2)
print("Q2", square(5), reduce(lambda a, b: a * b, [1, 2, 3, 4]))


def logged(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


@logged
def greet():
    """Say hi."""


print("Q3", greet.__name__, greet.__doc__)


@dataclass(order=True)
class Card:
    rank: int
    suit: str = "hearts"
    tags: list = field(default_factory=list)


print("Q4", Card(2) < Card(3), Card(2), Card(2) == Card(2))


class Color(Enum):
    RED = 1
    GREEN = 2


print("Q5", Color.RED, Color(2).name, Color["RED"].value, len(Color))


def f(a, /, b, *, c):
    return a + b + c


try:
    f(a=1, b=2, c=3)
except TypeError:
    print("Q6 a is positional only")
print("Q6", f(1, b=2, c=3))


def hinted(x: int) -> str:
    return x * 2


print("Q7", hinted(3), hinted.__annotations__)
print("Q8", sorted(["b", "C", "a"]), sorted(["b", "C", "a"], key=str.lower), max([], default=0))
x = [1, 2, 3]
print("Q9", (y := len(x)) > 2, y, *x)
match {"type": "point", "x": 1}:
    case {"type": "point", "x": 0}:
        print("Q10 origin")
    case {"type": "point", "x": x0}:
        print("Q10 x is", x0)
'''

K.code('paper_a', PAPER_A)
K.code('paper_b', PAPER_B)
K.code('paper_c', PAPER_C)
K.code('paper_d', PAPER_D)
K.code('bug_hunt', r'''
# Bug 1: a decorator that forgets to return the result
def timed(fn):
    def wrapper(*args):
        fn(*args)
    return wrapper


@timed
def add(a, b):
    return a + b


print("Bug 1:", add(2, 3))

# Bug 2: a generator used twice
squares = (n * n for n in range(4))
print("Bug 2:", sum(squares), sum(squares))


# Bug 3: __eq__ without __hash__
class Point:
    def __init__(self, x):
        self.x = x

    def __eq__(self, other):
        return self.x == other.x


try:
    print({Point(1)})
except TypeError as err:
    print("Bug 3:", err)


# Bug 4: a class attribute list shared by every object
class Basket:
    items = []

    def add(self, item):
        self.items.append(item)


first = Basket()
second = Basket()
first.add("apple")
print("Bug 4:", second.items)

# Bug 5: catching an error and hiding it
import json


def load(text):
    try:
        return json.loads(text)
    except Exception:
        pass


print("Bug 5:", load("{bad json}"))


# Bug 6: a context manager that swallows every exception
class Safe:
    def __enter__(self):
        return self

    def __exit__(self, *info):
        return True


with Safe():
    total = 1 / 0
print("Bug 6: still running, total exists:", "total" in globals())

# Bug 7: a regular expression without a raw string
import re

print("Bug 7:", re.findall("\bcat\b", "cat concat cat"), re.findall(r"\bcat\b", "cat concat cat"))
''')

PLAY = '''

def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results
'''

K.lesson('map', 'The PCPP1 exam and how to use this chapter', f'''
{src('Exam facts from two training providers that agree (Lumify Work and OpenExamPrep, read on 7 November 2026). The official page pythoninstitute.org/pcpp1 could not be opened when this chapter was written.')}
<p>This chapter teaches nothing new. It revises the whole Advanced part in the shape of the Python Institute PCPP1 exam (code PCPP-32-101), with four practice papers, a bug hunt, the traps, a mock quiz and timed problems. Every question was written for this course, and every answer below was printed by a real run of Python 3.14.</p>
{table(['', 'PCPP1 (PCPP-32-101), as listed by training providers'], [
    ['Questions', '45'],
    ['Time', '65 minutes'],
    ['Pass mark', '70 %'],
    ['Before it', 'PCAP (Certified Associate) is recommended'],
    ['Blocks', 'Advanced object oriented programming. Coding conventions, best practices and standards (PEP 8, PEP 257). GUI programming with tkinter. Network programming (sockets, REST). File processing and the program environment (sqlite3, CSV, XML, logging, configparser).']])}
{note('Check pythoninstitute.org/pcpp1 before you book. Exam versions, prices and weights change, and this page could not confirm them from the official site.', 'warn')}
{table(['Exam block', 'Chapters in this course'], [
    ['Advanced OOP', '1.1 to 1.5 (special methods, decorators, class design, exceptions and copies, metaclasses)'],
    ['Conventions and best practices', '3.1 (style, PEP 8, PEP 257, type hints), 3.2 testing'],
    ['GUI programming', '6.4 tkinter'],
    ['Network programming', 'Web and APIs part (HTTP, sockets, requests, REST)'],
    ['Files and environment', '3.3 logging, 6.2 CSV, JSON, XML and settings, 6.3 sqlite3'],
    ['Extra (not in the exam, used every day)', '2.1 to 2.3 generators, itertools, context managers, 4.1 and 4.2 speed, 5.1 and 5.2 concurrency, 6.1 regex']])}
{table(['Paper', 'Covers', 'Lesson'], [
    ['A', 'Special methods, MRO, class and static methods, properties, ABCs, decorators, metaclasses, slots, copies', '2'],
    ['B', 'Generators, send, yield from, iterators, itertools, context managers, exception chaining and groups', '3'],
    ['C', 'Regular expressions, json, csv, collections, heapq, sqlite3', '4'],
    ['D', 'functools, dataclasses, enum, parameter kinds, type hints, sorting, the walrus, match', '5']])}
{note('Cover the answers, write down what you think each line prints, then open the answers. A wrong guess tells you exactly which chapter to reread.', 'tip')}
''', kw=['PCPP1', 'PCPP-32-101', 'exam', 'certification', 'Python Institute', 'pass mark', 'syllabus', 'revision'])

K.lesson('paper_a', 'Paper A: advanced object oriented programming', f'''
{show('Paper A: what does each line print', PAPER_A)}
{answers('Open the answers for paper A', table(['Q', 'Output', 'Why (chapter)'], [
    ['1', 'V(3) True False', '+ calls __add__, == calls __eq__, but is compares identity: two different objects (1.1)'],
    ['2', 'TypeError', 'A class that defines __eq__ without __hash__ gets __hash__ = None, so its objects cannot go in a set (1.1)'],
    ['3', "BCA ['D', 'B', 'C', 'A', 'object']", 'super() follows the MRO of the object, not the parent of the class. In B it calls C, not A (1.3)'],
    ['4', '2 hi', 'The classmethod gets the class, the staticmethod gets nothing. Both can be called on the class (1.3)'],
    ['5', '25 too cold', 'The setter refused -300 before changing _c, so the old value stays (1.3)'],
    ['6', 'cannot make a Shape', 'A class with an abstract method that is not overridden cannot be instantiated (1.3)'],
    ['7', '10 wrapper', 'The decorator doubles the result. Without functools.wraps the function now reports the name wrapper (1.2)'],
    ['8', "['x', 'x', 'x']", 'repeat(3) runs first and returns the real decorator (1.2)'],
    ['9', 'thing Meta type', 'The metaclass __new__ added tag. The type of a class is its metaclass, and the type of type is type (1.5)'],
    ['10', 'False', '__slots__ removes the per object __dict__, so new attributes are refused (1.3)'],
    ['11', '[1, 2, 9] [1, 2] False True', 'A shallow copy is a new outer list that shares the inner lists. deepcopy copies them too (1.4)']]) + run('paper_a'))}
''', kw=['special methods', '__hash__', 'MRO', 'super', 'classmethod', 'staticmethod', 'property', 'abc', 'decorator', 'metaclass', '__slots__', 'deepcopy'])

K.lesson('paper_b', 'Paper B: generators, context managers and exceptions', f'''
{show('Paper B: what does each line print', PAPER_B)}
{answers('Open the answers for paper B', table(['Q', 'Output', 'Why (chapter)'], [
    ['1', 'made, start, 1, middle, [2]', 'Calling a generator function runs nothing. Each next runs to the next yield (2.1)'],
    ['2', 'got 10, then 5 20', 'send(10) resumes the paused yield with the value 10. The print inside runs before the Q2 line can print (2.1)'],
    ['3', "[1, 2, 'done']", 'yield from passes the inner values on and gives back the inner return value (2.1)'],
    ['4', 'True [3]', 'in on an iterator uses it up until it finds 2, so only 3 is left (2.1)'],
    ['5', '[10, 15, 20] [1, 3, 6]', 'count is endless, islice takes 3. accumulate gives running totals (2.2)'],
    ['6', "['a', 'b', 1] ['a', 'b', 'a'] 10", 'groupby groups only NEIGHBOURS that are equal, so a appears twice. 5 choose 2 is 10 (2.2)'],
    ['7', '&lt;b&gt;, B, &lt;/b&gt;', 'The code before yield is the set up, the finally part is the clean up (2.3)'],
    ['8', 'exit saw ZeroDivisionError, after the with block', '__exit__ returning True swallows the exception (2.3)'],
    ['9', 'KeyError True', 'raise ... from err sets __cause__ and hides the automatic context (1.4)'],
    ['10', 'V 2, T 1', 'except* splits the group: each handler gets the matching part (1.4)']]) + run('paper_b'))}
''', kw=['generator', 'send', 'yield from', 'iterator', 'itertools', 'groupby', 'contextmanager', '__exit__', 'raise from', 'ExceptionGroup', 'except*'])

K.lesson('paper_c', 'Paper C: the standard library', f'''
{show('Paper C: what does each line print', PAPER_C)}
{answers('Open the answers for paper C', table(['Q', 'Output', 'Why (chapter)'], [
    ['1', "['1', '22', '333'] home at ann", 'findall returns strings. In the replacement, &#92;2 and &#92;1 are the groups (6.1)'],
    ['2', 'None True True', 'match only tries at the start, search anywhere, fullmatch the whole text (6.1)'],
    ['3', "['&lt;a&gt;&lt;b&gt;'] ['&lt;a&gt;', '&lt;b&gt;']", '.+ is greedy and takes as much as it can, .+? is lazy (6.1)'],
    ['4', '{"a": null, "b": [1, 2]} [1, 2.0, True]', 'None becomes null, tuples become lists, true becomes True (6.2)'],
    ['5', "[['x', 'y, z', '3']] str", 'The quoted field keeps its comma. csv gives every value as a string (6.2)'],
    ['6', "[('a', 3), ('n', 2)] {'a': 1}", 'most_common sorts by count. A defaultdict is a dict (4.2)'],
    ['7', '[0, 2, 3]', 'maxlen=3: append 4 pushes out 1, appendleft 0 pushes out 4 from the right end (4.2)'],
    ['8', '1 [1, 2] 1 [2, 5, 4]', 'heapify puts the smallest first. After heappop the list is still a heap, not sorted (4.2)'],
    ['9', "3 Point(x=9, y=2) {'x': 1, 'y': 2}", 'A namedtuple works by name and by index. _replace makes a new one (4.2)'],
    ['10', '(3, 3, 6)', 'Aggregates give one row: COUNT, MAX and SUM (6.3)']]) + run('paper_c'))}
''', kw=['re', 'match search fullmatch', 'greedy', 'json', 'csv', 'Counter', 'deque', 'heapq', 'namedtuple', 'sqlite3'])

K.lesson('paper_d', 'Paper D: functions, data classes and modern syntax', f'''
{show('Paper D: what does each line print', PAPER_D)}
{answers('Open the answers for paper D', table(['Q', 'Output', 'Why (chapter)'], [
    ['1', '832040 31', 'With the cache every fib(n) from 0 to 30 is worked out once: 31 misses (1.2, 4.1)'],
    ['2', '25 24', 'partial fixes exp=2. reduce multiplies 1 &times; 2 &times; 3 &times; 4 (2.2)'],
    ['3', 'greet Say hi.', 'functools.wraps copies the name and the docstring to the wrapper (1.2)'],
    ['4', "True Card(rank=2, suit='hearts', tags=[]) True", 'order=True compares the fields in order. The dataclass writes __repr__ and __eq__ (1.3)'],
    ['5', 'Color.RED GREEN 1 2', 'Color(2) finds by value, Color["RED"] by name (1.3)'],
    ['6', 'a is positional only, then 6', 'Parameters before / cannot be passed by name. After * they must be (1.2)'],
    ['7', "6 {'x': &lt;class 'int'&gt;, 'return': &lt;class 'str'&gt;}", 'Type hints are not checked when the code runs. Use mypy for that (3.1)'],
    ['8', "['C', 'a', 'b'] ['a', 'b', 'C'] 0", 'Upper case letters sort before lower case ones. key=str.lower ignores case. max needs default= for an empty list'],
    ['9', 'True 3 1 2 3', ':= assigns inside an expression. *x unpacks the list into separate arguments'],
    ['10', 'x is 1', 'The first case needs x == 0. The second captures the value in x0'],
    ]) + run('paper_d'))}
''', kw=['lru_cache', 'partial', 'reduce', 'wraps', 'dataclass', 'Enum', 'positional only', 'keyword only', 'annotations', 'walrus', 'match'])

K.lesson('bugs', 'Find the bug', f'''
{run('bug_hunt')}
{steps('Seven bugs examiners and reviewers love', [
    '<b>Bug 1.</b> The wrapper calls fn but never returns its result, so every decorated function returns None. Write return fn(*args, **kwargs) (1.2).',
    '<b>Bug 2.</b> A generator can be used only once. The second sum sees nothing. Use a list, or make a new generator (2.1).',
    '<b>Bug 3.</b> Defining __eq__ removes __hash__. Add __hash__ based on the same fields, or use @dataclass(frozen=True) (1.1).',
    '<b>Bug 4.</b> items = [] in the class body is ONE list shared by every Basket. Make it in __init__ with self.items = [] (1.3).',
    '<b>Bug 5.</b> except Exception: pass hides the error, and the caller gets None without knowing why. Catch the exact error and log it or raise your own (1.4, 3.3).',
    '<b>Bug 6.</b> __exit__ returning True swallows every exception, so the program goes on with total missing. Return True only for the errors you really handle (2.3).',
    '<b>Bug 7.</b> In a normal string &#92;b is the backspace character, so the pattern never matches. Always write patterns as raw strings r"..." (6.1).'])}
''', kw=['find the bug', 'decorator return', 'generator used twice', 'unhashable', 'shared class attribute', 'swallowed exception', 'raw string regex'])

K.lesson('traps', 'The traps in one table', f'''
{table(['Trap', 'Looks like', 'Really', 'Chapter'], [
    ['__eq__ only', 'Objects still work in sets', 'They become unhashable', '1.1'],
    ['NotImplemented', 'Return False when the type is wrong', 'Return NotImplemented, so Python can try the other side', '1.1'],
    ['super()', 'Calls the parent class', 'Calls the next class in the MRO of the object', '1.3'],
    ['Decorator without wraps', 'Keeps the name and docstring', 'The function is now called wrapper', '1.2'],
    ['Decorator with arguments', '@repeat is enough', '@repeat(3): three levels of functions', '1.2'],
    ['Mutable class attribute', 'Each object has its own list', 'All objects share one list', '1.3'],
    ['Shallow copy', 'copy.copy copies everything', 'Inner objects are shared', '1.4'],
    ['Generator', 'Can be looped over twice', 'It is empty after the first loop', '2.1'],
    ['groupby', 'Groups all equal items', 'Groups only neighbours: sort first', '2.2'],
    ['__exit__ return value', 'Return True to say "done"', 'True swallows the exception', '2.3'],
    ['raise from', 'Same as a plain raise', 'Sets __cause__ and shows "direct cause"', '1.4'],
    ['Type hints', 'Python checks them', 'Only tools such as mypy check them', '3.1'],
    ['Regex without r', '"&#92;d" and r"&#92;d" are the same', 'Some escapes, like &#92;b, change meaning', '6.1'],
    ['pickle', 'Safe like JSON', 'Loading can run code', '6.2'],
    ['sqlite3', 'Changes are saved at once', 'Call commit() or use with conn', '6.3'],
    ['tkinter callback', 'command=f() is right', 'command=f, without brackets', '6.4'],
    ['pack and grid', 'Can be mixed in one parent', 'TclError: use one per parent', '6.4']])}
''', kw=['exam traps', 'common mistakes', 'gotchas', 'tricky questions'])

K.lesson('plan', 'Exam technique and a study plan', f'''
{fxs(fx('Time per question', 'minutes &times; 60 / questions', 'PCPP1 as listed: 65 &times; 60 / 45 &asymp; 87 seconds.', key=True),
     fx('Questions to pass (if every item counts the same)', 'correct needed = ceil(pass mark &times; questions)', '0.7 &times; 45 = 31.5, so 32 correct answers.', key=True),
     fx('Safety margin', 'aim = pass mark + 15 points in practice', 'Practise until you score about 85 %, because exam nerves cost a few points.'))}
{steps('A four week plan', [
    'Week 1: chapters 1.1 to 1.5 and paper A. Write a small class with __repr__, __eq__, __hash__, a property and a decorator from memory.',
    'Week 2: chapters 3.1 to 3.3 (style, testing, logging) and 6.4 tkinter. Build one small window with grid, a variable and an event.',
    'Week 3: chapters 6.1 to 6.3 and the network chapters of the web part, with papers B and C.',
    'Week 4: paper D, the bug hunt, the traps table, then the mock quiz in the Quiz tab with a timer of 87 seconds per question.'])}
{note('In the exam: read the whole snippet first, then the options. Trace it on paper and watch for the answer "the code raises an exception". Mark hard questions and come back, because every question is worth the same.', 'exam')}
{ladder(
    '<p>PCAP level: classes, inheritance, exceptions, modules and strings (the Core part).</p>',
    '<p>PCPP1 level: special methods, decorators, metaclasses, PEP 8 and PEP 257, tkinter, sockets and REST, sqlite3, CSV, XML, logging and configparser.</p>',
    '<p>PCPP2 and job level: design patterns, testing, concurrency, packaging, and frameworks such as Flask and Django from the Web part.</p>',
    '<p>Expert: explain every trap from the language reference and the data model, and spot them in code review before they reach production.</p>')}
''', kw=['exam technique', 'time per question', 'pass mark', 'study plan', 'PCPP2'])

lc(304, 'Range Sum Query 2D - Immutable', 'range-sum-query-2d-immutable', 'm', 'A class with a table of prefix sums', 'Build sums[r + 1][c + 1] = the total of the rectangle from (0, 0) to (r, c) once in __init__. Any rectangle is then four lookups.', r'''
class NumMatrix:
    def __init__(self, matrix):
        rows = len(matrix)
        cols = len(matrix[0])
        self.sums = [[0] * (cols + 1) for _ in range(rows + 1)]
        for r in range(rows):
            for c in range(cols):
                self.sums[r + 1][c + 1] = matrix[r][c] + self.sums[r][c + 1] + self.sums[r + 1][c] - self.sums[r][c]

    def sumRegion(self, row1, col1, row2, col2):
        s = self.sums
        return s[row2 + 1][col2 + 1] - s[row1][col2 + 1] - s[row2 + 1][col1] + s[row1][col1]
''' + PLAY, [('play(NumMatrix, ["NumMatrix", "sumRegion", "sumRegion", "sumRegion"], [[[[3, 0, 1, 4, 2], [5, 6, 3, 2, 1], [1, 2, 0, 1, 5], [4, 1, 0, 1, 7], [1, 0, 3, 0, 5]]], [2, 1, 4, 3], [1, 1, 2, 2], [1, 2, 2, 4]])', [None, 8, 11, 12])])
lc(438, 'Find All Anagrams in a String', 'find-all-anagrams-in-a-string', 'm', 'A sliding window of Counters', 'Keep a Counter of the last len(p) letters. Add the new letter, remove the oldest, and compare with the Counter of p.', r'''
from collections import Counter


def find_anagrams(s, p):
    need = Counter(p)
    window = Counter()
    found = []
    for i, ch in enumerate(s):
        window[ch] += 1
        if i >= len(p):
            old = s[i - len(p)]
            window[old] -= 1
            if window[old] == 0:
                del window[old]
        if window == need:
            found.append(i - len(p) + 1)
    return found
''', [('find_anagrams("cbaebabacd", "abc")', [0, 6]), ('find_anagrams("abab", "ab")', [0, 1, 2])])
lc(39, 'Combination Sum', 'combination-sum', 'm', 'A recursive generator', 'A generator yields each combination as soon as it is found. Pass the start index so a number is never used before a smaller one, which avoids repeats.', r'''
def combination_sum(candidates, target):
    candidates = sorted(candidates)

    def search(start, left, chosen):
        if left == 0:
            yield list(chosen)
            return
        for i in range(start, len(candidates)):
            if candidates[i] > left:
                break
            chosen.append(candidates[i])
            yield from search(i, left - candidates[i], chosen)
            chosen.pop()

    return list(search(0, target, []))
''', [('combination_sum([2, 3, 6, 7], 7)', [[2, 2, 3], [7]]), ('combination_sum([2, 3, 5], 8)', [[2, 2, 2, 2], [2, 3, 3], [3, 5]]), ('combination_sum([2], 1)', [])])
lc(131, 'Palindrome Partitioning', 'palindrome-partitioning', 'm', 'yield from for every first piece', 'Try every palindrome as the first piece, then partition the rest the same way. A generator with yield from keeps the code short.', r'''
def partition(s):
    def cuts(rest):
        if not rest:
            yield []
            return
        for end in range(1, len(rest) + 1):
            piece = rest[:end]
            if piece == piece[::-1]:
                for tail in cuts(rest[end:]):
                    yield [piece] + tail

    return list(cuts(s))
''', [('partition("aab")', [['a', 'a', 'b'], ['aa', 'b']]), ('partition("a")', [['a']])])
lc(1143, 'Longest Common Subsequence', 'longest-common-subsequence', 'm', 'Recursion with lru_cache', 'best(i, j) compares text1[i:] and text2[j:]. Equal letters add 1, otherwise skip one letter on either side. functools.cache stores every answer.', r'''
from functools import cache


def longest_common_subsequence(text1, text2):
    @cache
    def best(i, j):
        if i == len(text1) or j == len(text2):
            return 0
        if text1[i] == text2[j]:
            return 1 + best(i + 1, j + 1)
        return max(best(i + 1, j), best(i, j + 1))

    return best(0, 0)
''', [('longest_common_subsequence("abcde", "ace")', 3), ('longest_common_subsequence("abc", "abc")', 3), ('longest_common_subsequence("abc", "def")', 0)])
lc(221, 'Maximal Square', 'maximal-square', 'm', 'Grow squares from three neighbours', 'size[r][c] is the side of the biggest all "1" square ending at (r, c): 1 + the smallest of the sizes above, to the left and diagonal.', r'''
def maximal_square(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    size = [[0] * (cols + 1) for _ in range(rows + 1)]
    best = 0
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == "1":
                size[r + 1][c + 1] = 1 + min(size[r][c + 1], size[r + 1][c], size[r][c])
                best = max(best, size[r + 1][c + 1])
    return best * best
''', [('maximal_square([["1", "0", "1", "0", "0"], ["1", "0", "1", "1", "1"], ["1", "1", "1", "1", "1"], ["1", "0", "0", "1", "0"]])', 4), ('maximal_square([["0", "1"], ["1", "0"]])', 1), ('maximal_square([["0"]])', 0)])
lc(72, 'Edit Distance', 'edit-distance', 'm', 'A table of smaller answers', 'dist[i][j] is the cost to turn the first i letters of word1 into the first j letters of word2. Equal letters cost nothing, otherwise 1 + the best of insert, delete or replace.', r'''
def min_distance(word1, word2):
    rows = len(word1) + 1
    cols = len(word2) + 1
    dist = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        dist[i][0] = i
    for j in range(cols):
        dist[0][j] = j
    for i in range(1, rows):
        for j in range(1, cols):
            if word1[i - 1] == word2[j - 1]:
                dist[i][j] = dist[i - 1][j - 1]
            else:
                dist[i][j] = 1 + min(dist[i - 1][j], dist[i][j - 1], dist[i - 1][j - 1])
    return dist[-1][-1]
''', [('min_distance("horse", "ros")', 3), ('min_distance("intention", "execution")', 5), ('min_distance("", "abc")', 3)])
lc(42, 'Trapping Rain Water', 'trapping-rain-water', 'h', 'Two pointers with the highest wall on each side', 'Water above a bar is the lower of the highest walls on its left and right, minus the bar. Move the pointer on the lower side, because that side decides the water level.', r'''
def trap(height):
    left = 0
    right = len(height) - 1
    left_max = 0
    right_max = 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            left_max = max(left_max, height[left])
            water += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            water += right_max - height[right]
            right -= 1
    return water
''', [('trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])', 6), ('trap([4, 2, 0, 3, 2, 5])', 9)])
lc(76, 'Minimum Window Substring', 'minimum-window-substring', 'h', 'Grow the window, then shrink it', 'Move the right end until the window holds every letter of t (count with a Counter). Then move the left end while it still does, and remember the shortest window.', r'''
from collections import Counter


def min_window(s, t):
    need = Counter(t)
    missing = len(t)
    left = 0
    best = (0, 0)
    for right, ch in enumerate(s, 1):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        if missing == 0:
            while need[s[left]] < 0:
                need[s[left]] += 1
                left += 1
            if best == (0, 0) or right - left < best[1] - best[0]:
                best = (left, right)
            need[s[left]] += 1
            missing += 1
            left += 1
    return s[best[0]:best[1]]
''', [('min_window("ADOBECODEBANC", "ABC")', 'BANC'), ('min_window("a", "a")', 'a'), ('min_window("a", "aa")', '')])
lc(460, 'LFU Cache', 'lfu-cache', 'h', 'A dict of OrderedDicts, one per use count', 'Keep the value and the use count of each key, and an OrderedDict of keys for every count. Evict the oldest key in the group with the smallest count.', r'''
from collections import OrderedDict, defaultdict


class LFUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.values = {}
        self.counts = {}
        self.groups = defaultdict(OrderedDict)
        self.min_count = 0

    def _touch(self, key):
        count = self.counts[key]
        del self.groups[count][key]
        if not self.groups[count]:
            del self.groups[count]
            if self.min_count == count:
                self.min_count += 1
        self.counts[key] = count + 1
        self.groups[count + 1][key] = None

    def get(self, key):
        if key not in self.values:
            return -1
        self._touch(key)
        return self.values[key]

    def put(self, key, value):
        if self.capacity == 0:
            return
        if key in self.values:
            self.values[key] = value
            self._touch(key)
            return
        if len(self.values) >= self.capacity:
            old, _ = self.groups[self.min_count].popitem(last=False)
            if not self.groups[self.min_count]:
                del self.groups[self.min_count]
            del self.values[old]
            del self.counts[old]
        self.values[key] = value
        self.counts[key] = 1
        self.groups[1][key] = None
        self.min_count = 1
''' + PLAY, [('play(LFUCache, ["LFUCache", "put", "put", "get", "put", "get", "get", "put", "get", "get", "get"], [[2], [1, 1], [2, 2], [1], [3, 3], [2], [3], [4, 4], [1], [3], [4]])', [None, None, None, 1, None, -1, 3, None, -1, 3, 4])])

K.lesson('leetcode', 'LeetCode review set', leet('<p>Ten problems that use the Advanced part: classes that prepare data once, Counters in a sliding window, recursive generators with yield from, functools.cache, dynamic programming tables, two pointers, and a cache built from OrderedDicts. Try each in under 30 minutes, as in a coding interview.</p>'), kw=['LeetCode', 'review', 'generator', 'cache', 'dynamic programming', 'sliding window', 'OrderedDict'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'PCPP1 (PCPP-32-101) as listed by training providers: 45 questions, 65 minutes, 70 %. Check the official page before you book.',
    'Objects: __eq__ needs a matching __hash__, return NotImplemented for unknown types, super() follows the MRO, wraps keeps the name.',
    'Iteration: generators run only on next, can be used once, send resumes a yield, yield from passes values and the return value.',
    'Context and errors: __exit__ returning True swallows the error, raise from sets __cause__, except* splits exception groups.',
    'Library: raw strings for regex, json changes tuples and keys, csv gives strings, deque maxlen drops from the other end, sqlite3 needs commit.',
    'Technique: about 87 seconds per question, trace on paper, aim for 85 % in practice.'],
    'The Web and APIs part goes on with HTTP, sockets, REST, Flask, Django and FastAPI.')}
{files('Three exam style tasks: a Vector2 class with the right special methods, a retry decorator, and an LRU cache built on OrderedDict.')}
''', kw=['summary', 'recap'])

# ---------------- mock quiz ----------------
K.quiz('e', 'Which special method does len(obj) call?', ['__size__', '__len__', '__count__', '__length__'], 1, 'Double underscores.', 'len() calls type(obj).__len__(obj).')
K.quiz('e', 'Which decorator makes a method receive the class instead of the object?', ['@staticmethod', '@classmethod', '@property', '@abstractmethod'], 1, 'cls.', 'Class methods are often used as alternative constructors.')
K.quiz('e', 'What does PEP 8 recommend for class names?', ['snake_case', 'CapWords (CamelCase)', 'UPPER_CASE', 'lowercase'], 1, 'Like ValueError.', 'Functions and variables use snake_case, constants UPPER_CASE.')
K.quiz('e', 'What is PEP 257 about?', ['Line length', 'Docstrings', 'Type hints', 'Imports'], 1, 'Documentation strings.', 'It says how to write docstrings, for example a one line summary first.')
K.quiz('e', 'Which tkinter call starts the event loop?', ['root.start()', 'root.mainloop()', 'root.loop()', 'root.run()'], 1, 'The main loop.', 'It returns when the window closes.')
K.quiz('e', 'Which module reads and writes comma separated files?', ['json', 'csv', 'pickle', 'shelve'], 1, 'Comma separated values.', 'Open the file with newline="".')
K.quiz('e', 'Which logging level is the most serious of these?', ['INFO', 'WARNING', 'ERROR', 'DEBUG'], 2, 'DEBUG &lt; INFO &lt; WARNING &lt; ERROR &lt; CRITICAL.', 'The default level of the root logger is WARNING.')
K.quiz('e', 'What does a generator function return when you call it?', ['The first value', 'A generator object, and none of its code has run yet', 'A list', 'None'], 1, 'Lazy.', 'next() runs it to the first yield.')
K.quiz('m', 'A class defines __eq__ but not __hash__. What happens with {obj}?', ['It works', 'TypeError: the objects are unhashable', 'It uses id()', 'The set is empty'], 1, '__hash__ becomes None.', 'Add __hash__ based on the same fields as __eq__.')
K.quiz('m', 'In class D(B, C) where B and C both inherit from A, what is D.__mro__?', ['D, B, A, C, object', 'D, B, C, A, object', 'D, C, B, A, object', 'D, A, B, C, object'], 1, 'C3 linearisation.', 'A comes after both of its children.')
K.quiz('m', 'What should __add__ return when it does not know the other type?', ['False', 'None', 'NotImplemented', 'raise TypeError at once'], 2, 'Let Python try the other side.', 'Python then tries __radd__ of the other object, and raises TypeError only if that fails too.')
K.quiz('m', 'Why use functools.wraps in a decorator?', ['It makes the function faster', 'It copies __name__, __doc__ and other details of the wrapped function to the wrapper', 'It caches results', 'It is required by Python'], 1, 'Metadata.', 'Without it, help() and logs show the name wrapper.')
K.quiz('m', 'What does type(type) return?', ['object', 'type', 'class', 'metaclass'], 1, 'type is its own type.', 'type is the default metaclass of every class, including itself.')
K.quiz('m', 'What does copy.copy([[1], [2]]) share with the original?', ['Nothing', 'The inner lists', 'Only the outer list', 'Everything, it is the same object'], 1, 'Shallow.', 'Use copy.deepcopy to copy the inner lists too.')
K.quiz('m', 'What does an __exit__ method that returns True do?', ['Re-raises the exception', 'Suppresses the exception from the with block', 'Closes the file', 'Nothing special'], 1, 'Truthy return.', 'Return a false value (or nothing) to let exceptions continue.')
K.quiz('m', 'In grid, what does columnconfigure(1, weight=1) do?', ['Makes column 1 bold', 'Gives column 1 the extra width when the window grows', 'Hides column 1', 'Sets the width to 1 pixel'], 1, 'Weight shares extra space.', 'Columns with weight 0 keep their natural width.')
K.quiz('m', 'Why use ? placeholders in sqlite3 queries?', ['They are faster to type', 'They stop SQL injection and handle quotes in values', 'They are required for SELECT', 'They sort the result'], 1, 'Values travel separately.', 'Never build SQL with f-strings.')
K.quiz('m', 'Which socket call does a TCP server use to wait for a client?', ['connect()', 'accept()', 'send()', 'close()'], 1, 'Server side: bind, listen, accept.', 'accept() returns a new socket for that client and its address.')
K.quiz('m', 'What HTTP method does a REST API usually use to create a new resource?', ['GET', 'POST', 'DELETE', 'HEAD'], 1, 'Create.', 'GET reads, PUT or PATCH changes, DELETE removes.')
K.quiz('m', 'Which status code means "created"?', ['200', '201', '204', '404'], 1, '2xx is success.', '201 Created, often with a Location header.')
K.quiz('h', 'A generator g first yields 1, stores the value it is sent in x, then yields x + 1. What does print(next(it), it.send(5)) print for it = g()?', ['1 2', '1 6', '1 None', 'TypeError'], 1, 'send resumes the paused yield.', 'x becomes 5, so the next yield gives 6.')
K.quiz('h', 'What does itertools.groupby("aabba") give as keys?', ["['a', 'b']", "['a', 'b', 'a']", "['a', 'a', 'b', 'b', 'a']", "['ab']"], 1, 'Neighbours only.', 'Sort first if you want one group per key.')
K.quiz('h', 'In a metaclass, which method runs when the CLASS is created?', ['__init__ of the class', '__new__ (and __init__) of the metaclass', '__call__ of the metaclass', '__new__ of object'], 1, 'Classes are objects made by their metaclass.', '__call__ of the metaclass runs later, when you make an OBJECT of the class.')
K.quiz('h', 'A tkinter worker thread finished. What is the safe way to update a label?', ['Call label.config from the thread', 'Put the result in a queue and read it in an after() callback in the main thread', 'Call mainloop again', 'Use time.sleep'], 1, 'Tk is not thread safe.', 'Only the main thread touches widgets.')
K.quiz('h', 'What is the difference between raise X from err and raise X inside an except block?', ['None', 'from sets __cause__ (direct cause) and hides the automatic __context__ message', 'from hides X', 'from re-raises err'], 1, 'Explicit chaining.', 'raise X from None removes the chain from the traceback.')
K.quiz('h', 'Which is true about __slots__?', ['It makes classes abstract', 'Objects get no __dict__, use less memory and cannot get new attributes', 'It speeds up imports', 'It is needed for properties'], 1, 'Fixed attributes.', 'Useful for millions of small objects.')
K.quiz('h', 'Why should you not unpickle data from the internet?', ['It is slow', 'Unpickling can run any code the creator of the data chose', 'It loses types', 'It needs a password'], 1, '__reduce__.', 'Use JSON for data from others.')
K.quiz('x', 'In the style of a CMU 15-214 exam: why must a == b imply hash(a) == hash(b)?', ['For speed only', 'Sets and dicts first compare hashes. Equal objects with different hashes would be stored twice and not found again', 'Python checks it at class creation', 'It does not matter'], 1, 'Hash first, then ==.', 'The reverse is not needed: different objects may share a hash.')
K.quiz('x', 'In the style of an MIT 6.031 exam: why is a mutable default argument such as def f(x=[]) a design bug even though it never crashes?', ['It is slow', 'The default is made once when def runs, so state leaks between calls and the function is no longer the same for the same input', 'It breaks type hints', 'Lists cannot be defaults'], 1, 'Hidden shared state.', 'Use x=None and make a new list inside.')
K.quiz('x', 'In the style of a Stanford CS 242 exam: what does the C3 algorithm guarantee for the MRO?', ['Alphabetical order', 'Every class comes before its parents, and the order of the bases in each class statement is kept', 'object comes first', 'Depth first order'], 1, 'Monotonic linearisation.', 'If no such order exists, Python raises TypeError when the class is made.')

K.calc('e', 'PCPP1 as listed: 45 questions in 65 minutes. How many seconds per question, rounded?', '87', '65 &times; 60 / 45.', ['3,900 seconds.', '3,900 / 45 &asymp; 86.7.', eq('87 seconds')], check=round(65 * 60 / 45))
K.calc('e', 'How many correct answers are 70 % of 45 questions, rounding up?', '32', '0.7 &times; 45 = 31.5.', ['31.5 is not a whole answer.', 'Round up.', eq('32')], check=-(-70 * 45 // 100))
K.calc('e', 'How many pairs does itertools.combinations(range(5), 2) give?', '10', '5 &times; 4 / 2.', ['Ordered pairs: 20.', 'Each pair counted twice.', eq('10')], check=5 * 4 // 2)
K.calc('m', 'fib(30) with @lru_cache(maxsize=None): how many cache misses?', '31', 'Each of fib(0) to fib(30) once.', ['Every new n is a miss.', '0 to 30 is 31 values.', eq('31')], check=31)
K.calc('m', 'Naive fib(10) without a cache: how many calls in total, the first one included?', '177', 'calls(n) = 1 + calls(n &minus; 1) + calls(n &minus; 2), calls(0) = calls(1) = 1.', ['calls(2) = 3, calls(3) = 5, calls(4) = 9, calls(5) = 15.', 'calls(6) = 25, calls(7) = 41, calls(8) = 67, calls(9) = 109.', eq('calls(10) = 1 + 109 + 67 = 177')], check=177)
K.calc('m', 'In a heap stored in a list, what is the index of the left child of index 3?', '7', '2i + 1.', ['2 &times; 3 + 1.', 'The right child is 2i + 2 = 8.', eq('7')], check=2 * 3 + 1)
K.calc('m', 'd = deque(maxlen=3), then d.append(n) for n in 1 to 10. What is sum(d)?', '27', 'Only the last 3 stay.', ['8, 9 and 10 are left.', '8 + 9 + 10.', eq('27')], check=8 + 9 + 10)
K.calc('h', 'How many results does itertools.permutations("abcd", 2) give?', '12', '4 &times; 3.', ['4 choices for the first letter.', '3 for the second.', eq('12')], check=4 * 3)
K.calc('h', 'class D(B, C), B(A), C(A). At which index (from 0) is A in D.__mro__?', '3', 'D, B, C, A, object.', ['Index 0 is D.', 'B 1, C 2, A 3.', eq('3')], check=3)
K.calc('x', 'In the style of an MIT 6.006 exam: an LRU cache of size 2 sees the keys 1, 2, 1, 3, 2, 1, 3. How many misses?', '6', 'Simulate, the least recently used key leaves.', ['1 miss, 2 miss, 1 hit, 3 miss (2 leaves).', '2 miss (1 leaves), 1 miss (3 leaves), 3 miss (2 leaves).', eq('6 misses')], check=6)

K.assign('vector2', 'e', 'A Vector2 class with the right special methods',
         '<p>Finish the class <code>Vector2</code>. It already adds vectors, multiplies by a number on the right and prints itself. Add: <code>3 * v</code> (__rmul__), <code>abs(v)</code> for the length (math.hypot), a __hash__ that matches __eq__ so vectors can go in sets, and make __eq__ return NotImplemented when the other object is not a Vector2.</p>',
         '''
class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __mul__(self, k):
        return Vector2(self.x * k, self.y * k)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"
''', [('repr(Vector2(1, 2) + Vector2(3, 4))', 'Vector2(4, 6)'), ('repr(Vector2(1, 2) * 3)', 'Vector2(3, 6)'), ('repr(3 * Vector2(1, 2))', 'Vector2(3, 6)'), ('abs(Vector2(3, 4))', 5.0), ('len({Vector2(1, 1), Vector2(1, 1), Vector2(2, 1)})', 2), ('Vector2(1, 2) == (1, 2)', False)],
         '''
import math


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __mul__(self, k):
        return Vector2(self.x * k, self.y * k)

    def __rmul__(self, k):
        return self * k

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __eq__(self, other):
        if not isinstance(other, Vector2):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"
''', '3 * v asks int first, which returns NotImplemented, so Python calls v.__rmul__(3). Hash the same fields that __eq__ compares: hash((self.x, self.y)).', '<p>With NotImplemented, Vector2(1, 2) == (1, 2) lets Python try the tuple side and then fall back to identity, which gives False instead of an AttributeError.</p>')
K.assign('retry', 'm', 'A retry decorator',
         '<p>Write <code>retry(times, exceptions=(Exception,))</code>, a decorator with arguments. The decorated function is called up to times times while it raises one of exceptions. After the last failed try, the last error is raised again. Other exceptions are not retried. Keep the name of the function with functools.wraps. The helpers <code>run(times, fails)</code> and <code>run_other()</code> use it on a function that fails a given number of times.</p>',
         '''
def retry(times, exceptions=(Exception,)):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def run(times, fails):
    calls = []

    @retry(times, (ConnectionError,))
    def fetch():
        calls.append(1)
        if len(calls) <= fails:
            raise ConnectionError("server down")
        return "ok"

    try:
        result = fetch()
    except ConnectionError:
        result = "gave up"
    return [result, len(calls), fetch.__name__]


def run_other():
    calls = []

    @retry(5, (ConnectionError,))
    def parse():
        calls.append(1)
        raise ValueError("bad data")

    try:
        parse()
    except ValueError:
        return ["ValueError", len(calls)]
    return ["no error", len(calls)]
''', [('run(3, 0)', ['ok', 1, 'fetch']), ('run(3, 2)', ['ok', 3, 'fetch']), ('run(3, 3)', ['gave up', 3, 'fetch']), ('run_other()', ['ValueError', 1])],
         '''
import functools


def retry(times, exceptions=(Exception,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
        return wrapper
    return decorator


def run(times, fails):
    calls = []

    @retry(times, (ConnectionError,))
    def fetch():
        calls.append(1)
        if len(calls) <= fails:
            raise ConnectionError("server down")
        return "ok"

    try:
        result = fetch()
    except ConnectionError:
        result = "gave up"
    return [result, len(calls), fetch.__name__]


def run_other():
    calls = []

    @retry(5, (ConnectionError,))
    def parse():
        calls.append(1)
        raise ValueError("bad data")

    try:
        parse()
    except ValueError:
        return ["ValueError", len(calls)]
    return ["no error", len(calls)]
''', 'Loop attempt from 1 to times. Return at once on success. In except exceptions, re-raise with a bare raise when it was the last attempt. except accepts a tuple of exception classes.', '<p>Real retry code also waits between tries, often longer each time (exponential backoff, for example 1, 2, 4 seconds), so a busy server gets time to recover.</p>')
K.assign('lru', 'h', 'An LRU cache on OrderedDict',
         '<p>Write the class <code>LRUCache(capacity)</code>. get(key, default=None) returns the value and marks the key as just used. put(key, value) adds or updates a key and marks it as just used. When there are more than capacity keys, the least recently used one leaves. A capacity of 0 stores nothing. len(cache) and key in cache work, and in does NOT count as a use. keys() lists the keys from least to most recently used. Use collections.OrderedDict with move_to_end and popitem(last=False). The helper <code>play_lru(capacity, commands)</code> runs commands.</p>',
         '''
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def put(self, key, value):
        if len(self.data) >= self.capacity:
            oldest = next(iter(self.data))
            del self.data[oldest]
        self.data[key] = value

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def keys(self):
        return list(self.data)


def play_lru(capacity, commands):
    cache = LRUCache(capacity)
    out = []
    for command in commands:
        if command[0] == "put":
            cache.put(command[1], command[2])
        elif command[0] == "get":
            out.append(cache.get(command[1]))
        else:
            out.append(command[1] in cache)
    return [out, cache.keys(), len(cache)]
''', [('play_lru(2, [("put", "a", 1), ("put", "b", 2), ("get", "a"), ("put", "c", 3), ("get", "b")])', [[1, None], ['a', 'c'], 2]), ('play_lru(2, [("put", "a", 1), ("put", "b", 2), ("put", "a", 10), ("get", "a"), ("get", "b")])', [[10, 2], ['a', 'b'], 2]), ('play_lru(1, [("put", "a", 1), ("in", "a"), ("put", "b", 2), ("in", "a"), ("get", "b")])', [[True, False, 2], ['b'], 1]), ('play_lru(0, [("put", "a", 1), ("get", "a")])', [[None], [], 0]), ('play_lru(2, [("put", "a", 1), ("put", "b", 2), ("in", "a"), ("put", "c", 3), ("get", "a")])', [[True, None], ['b', 'c'], 2])],
         '''
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = OrderedDict()

    def get(self, key, default=None):
        if key not in self.data:
            return default
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        if self.capacity <= 0:
            return
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def keys(self):
        return list(self.data)


def play_lru(capacity, commands):
    cache = LRUCache(capacity)
    out = []
    for command in commands:
        if command[0] == "put":
            cache.put(command[1], command[2])
        elif command[0] == "get":
            out.append(cache.get(command[1]))
        else:
            out.append(command[1] in cache)
    return [out, cache.keys(), len(cache)]
''', 'The starter forgets to move a key on get and on update, and crashes with capacity 0. move_to_end(key) marks a key as just used, popitem(last=False) removes the oldest.', '<p>functools.lru_cache works the same way inside: a dict for the lookups plus a linked order of use, so get and put are O(1).</p>')

K.must('Exam facts', 'PCPP1 (PCPP-32-101) as listed by training providers: 45 questions, 65 minutes, 70 %. Confirm on pythoninstitute.org/pcpp1.')
K.must('Object traps', '__eq__ needs __hash__, NotImplemented for unknown types, super() follows the MRO, wraps keeps the name, slots remove __dict__.')
K.must('Iteration traps', 'Generators run lazily and once, send resumes a yield, yield from returns the inner value, groupby needs sorted input.')
K.must('Error traps', '__exit__ True swallows, raise from sets __cause__, except* splits groups, never except Exception: pass.')
K.must('Library traps', 'Raw strings for regex, json makes lists and str keys, csv gives str, commit() in sqlite3, command=f in tkinter.')

T = K.topic(
    slug='py-adv-exam', topic='py-adv-exam', kind='revision',
    step=(8, 'Exam practice', 'py-a8', 'Practise for the PCPP1 exam with four papers, a bug hunt, the traps, a mock quiz and timed problems.', 'All levels'),
    title='Exam practice: PCPP1 style papers', short='Advanced exam practice', badge='8.1', minutes=100,
    lead='Revise the whole Advanced part in the shape of the PCPP1 exam: four predict the output papers with real answers, a bug hunt, the traps in one table, exam technique, a mock quiz of 30 questions and timed problems.',
    desc='PCPP1 (PCPP-32-101) facts as listed by training providers, the exam blocks mapped to chapters, predict the output papers on special methods, MRO, decorators, metaclasses, slots, copies, generators, itertools, context managers, exception chaining and groups, regex, json, csv, collections, heapq, sqlite3, functools, dataclasses, enum and parameter kinds, seven classic bugs, a traps table, time per question, a four week plan, a mock quiz and exam style coding tasks.',
    summary='Four PCPP1 style papers, a bug hunt, the traps table, exam technique and a mock quiz.',
    keywords=['PCPP1', 'PCPP-32-101', 'exam practice', 'mock quiz', 'predict output', 'find the bug', 'traps', 'certification', 'revision'],
    recap='<p>Trace every snippet on paper, know the traps by heart and practise under time. The exam rewards careful reading of advanced features more than clever code.</p>',
    added='2026-11-07', leet=leet_items())
