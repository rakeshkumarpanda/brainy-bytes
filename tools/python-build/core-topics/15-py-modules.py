# Core Python 5.2: modules and packages. Follows PCAP-31-03 section 1 (importing and using modules: import variants,
# dir(), sys.path, the math, random and platform modules, creating modules and packages, __init__.py, __pycache__,
# __name__, private names, pip and PyPI), checked against the Python 3.14 tutorial chapter 6 "Modules", the language
# reference chapter 5 "The import system", and the pip and venv documentation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items, term, show

chapter('py-modules')
K = Kit()

K.code('imports', r'''
import math                       # the whole module, used as math.name
print(math.sqrt(16), math.pi)

from math import factorial, tau   # just some names, used without math.
print(factorial(5), tau)

import statistics as st           # a short alias
print(st.mean([2, 4, 9]))

from math import sqrt as root     # an alias for one name
print(root(81))

names = [n for n in dir(math) if not n.startswith("_")]
print(len(names), "public names in math, for example", names[:6])
''')

K.code('mathmod', r'''
import math

print(math.ceil(4.2), math.floor(4.8), math.trunc(-4.8), round(4.5))
print(math.floor(-4.2), math.ceil(-4.2))
print(math.sqrt(2), math.isqrt(20), math.hypot(3, 4))
print(math.factorial(6), math.comb(5, 2), math.perm(5, 2))
print(math.gcd(84, 36), math.lcm(4, 6))
print(math.log(math.e), math.log10(1000), math.log2(1024), math.log(8, 2))
print(math.sin(math.pi / 2), math.degrees(math.pi), math.radians(180))
print(0.1 + 0.2 == 0.3, math.isclose(0.1 + 0.2, 0.3))
print(math.inf > 10 ** 100, math.isnan(math.nan))
''')

K.code('randmod', r'''
import random

random.seed(42)                     # the same seed gives the same "random" numbers
print(random.random())              # a float from 0.0 up to (not including) 1.0
print(random.randint(1, 6))         # a whole number from 1 to 6, both included
print(random.choice(["a", "b", "c"]))
print(random.sample(range(10), 3))  # 3 different items

cards = list(range(1, 11))
random.shuffle(cards)               # changes the list in place
print(cards)
print(random.randrange(0, 100, 10)) # like range: 0, 10, ..., 90
print(round(random.uniform(1.5, 2.5), 3))
''')

K.code('platmod', r'''
import platform, sys

print(platform.system())                 # Linux, Windows, Darwin (macOS), or Emscripten in a browser
print(platform.python_implementation())  # CPython, PyPy ...
print(platform.python_version_tuple()[:2])
print(sys.version_info >= (3, 10))
print(type(sys.path), len(sys.path) > 0)
''')

K.code('makemod', r'''
import os, sys, tempfile, importlib

folder = tempfile.mkdtemp()                       # a folder only for this demo
with open(os.path.join(folder, "shapes.py"), "w") as f:
    f.write('print("loading shapes, __name__ is", __name__)\n'
            'PI = 3.14159\n'
            'def area(r):\n'
            '    return PI * r * r\n')

sys.path.insert(0, folder)        # tell Python to look in that folder too

import shapes                     # runs shapes.py once
import shapes                     # already in sys.modules: nothing is printed
print(shapes.area(2), shapes.PI)
print("shapes" in sys.modules, os.path.basename(shapes.__file__))
importlib.reload(shapes)          # run the file again on purpose
''')

K.code('package', r'''
import os, sys, tempfile

root = tempfile.mkdtemp()
pkg = os.path.join(root, "geometry")
os.makedirs(pkg)
files = {
    "__init__.py": 'print("geometry package loaded")\n'
                   'from .circle import area\n'           # a relative import
                   '__all__ = ["area", "circle", "square"]\n',
    "circle.py": 'import math\n'
                 'def area(r):\n'
                 '    return round(math.pi * r * r, 2)\n',
    "square.py": 'def area(side):\n'
                 '    return side * side\n',
}
for name, text in files.items():
    with open(os.path.join(pkg, name), "w") as f:
        f.write(text)
sys.path.insert(0, root)

import geometry                    # runs geometry/__init__.py
print(geometry.area(1))            # the circle area, re-exported by __init__.py
from geometry import square        # a submodule
print(square.area(3))
import geometry.circle as c
print(c.area(2), c.__name__)
''')

K.code('private', r'''
import os, sys, tempfile

folder = tempfile.mkdtemp()
with open(os.path.join(folder, "tools.py"), "w") as f:
    f.write('__all__ = ["slug"]\n'
            'def slug(text):\n'
            '    return _clean(text).replace(" ", "-")\n'
            'def _clean(text):\n'
            '    return text.strip().lower()\n'
            'def shout(text):\n'
            '    return text.upper()\n')
sys.path.insert(0, folder)

from tools import *               # takes only the names in __all__
print(slug("  Hello World "))
print("shout" in dir(), "_clean" in dir())
import tools
print(tools._clean(" Still Reachable "))   # _ means "please do not use", not "locked"
''')

K.code('mainguard', r'''
def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32

def main():
    for c in [0, 37, 100]:
        print(c, "C is", celsius_to_fahrenheit(c), "F")

print("__name__ is", repr(__name__))
if __name__ == "__main__":     # True when this file is run, False when it is imported
    main()
''')

K.code('stdlib', r'''
from datetime import date, timedelta
from collections import Counter
import json, os.path, statistics, string

exam = date(2026, 12, 1)
print(exam.strftime("%A %d %B %Y"), (exam - date(2026, 11, 7)).days, "days to go")
print(exam + timedelta(weeks=2))
print(Counter("mississippi").most_common(2))
print(json.dumps({"name": "Asha", "marks": [90, 85]}))
print(os.path.join("data", "2026", "marks.csv"), os.path.splitext("photo.jpeg"))
print(statistics.median([3, 1, 4, 1, 5]), statistics.mode([3, 1, 4, 1, 5]))
print(string.ascii_lowercase[:5], string.digits)
''')

K.lesson('idea', 'Modules: code in many files', f'''
{src('Python 3.14 tutorial chapter 6, language reference chapter 5 "The import system", PCAP-31-03 section 1.')}
{wwh('A <b>module</b> is a .py file whose functions, classes and variables other programs can use. A <b>package</b> is a folder of modules. <b>import</b> loads a module and gives you a name to reach what is inside.',
     'One huge file is hard to read, test and share. Modules split a program into parts with clear jobs, let many programs reuse the same code, and give you the standard library: more than 200 modules for maths, dates, files, the web and much more, already installed. pip adds over half a million more from PyPI.',
     'import name checks a cache (sys.modules). If the module is not loaded yet, Python searches the folders in sys.path, runs the file once from top to bottom in a new module object, stores it in the cache and binds the name. Later imports reuse the cached module.')}
{scene('a toolbox with labelled drawers', '<p>A carpenter does not carry every tool in one heap. There is a drawer for measuring tools, one for saws, one for drills. "import math" opens the measuring drawer. "from math import sqrt" takes out just the one tool you need. The standard library is the toolbox that comes with Python, and pip is the shop where you buy new drawers.</p>')}
{run('imports')}
''', kw=['module', 'package', 'import', 'standard library', 'reuse'])

K.lesson('forms', 'Every way to write import', f'''
{table(['Form', 'Binds', 'Use as'], [
    ['import math', 'math', 'math.sqrt(2)'],
    ['import math as m', 'm', 'm.sqrt(2)'],
    ['from math import sqrt, pi', 'sqrt and pi', 'sqrt(2)'],
    ['from math import sqrt as root', 'root', 'root(2)'],
    ['from math import *', 'every public name (or those in __all__)', 'sqrt(2), pi, ... (avoid in real code)'],
    ['import os.path', 'os (and loads os.path)', 'os.path.join(...)'],
    ['from . import circle', 'circle, from the same package', 'circle.area(1) (relative import, inside packages only)']])}
{versus('import module or from module import name', ['', 'import math', 'from math import sqrt'], [
    ['Where a name comes from', 'Clear: math.sqrt', 'You must look at the top of the file'],
    ['Name clashes', 'None: math.log and your own log can live together', 'Possible: a later def log replaces the imported one'],
    ['Typing', 'Longer', 'Shorter']],
    'import the module for most code. Import single names when you use them very often and the name is clear, and never use import * outside the interactive prompt.')}
''', kw=['import forms', 'from import', 'alias', 'import star', 'relative import', 'namespace'])

K.lesson('mathmod', 'The math module', f'''
{run('mathmod')}
{table(['Function', 'Does', 'Example'], [
    ['ceil(x), floor(x)', 'Round up, round down to a whole number', 'ceil(4.2) = 5, floor(-4.2) = &minus;5'],
    ['trunc(x)', 'Cut off the fraction, toward zero', 'trunc(&minus;4.8) = &minus;4'],
    ['sqrt(x), isqrt(n)', 'Square root as float, exact whole number square root', 'isqrt(20) = 4'],
    ['hypot(x, y)', 'Length of the hypotenuse, &radic;(x<sup>2</sup> + y<sup>2</sup>)', 'hypot(3, 4) = 5.0'],
    ['factorial, comb, perm', 'n!, C(n, k), P(n, k)', 'comb(5, 2) = 10'],
    ['gcd, lcm', 'Greatest common divisor, least common multiple', 'gcd(84, 36) = 12'],
    ['log, log2, log10, exp', 'Logarithms and e<sup>x</sup>', 'log(8, 2) = 3.0'],
    ['isclose(a, b)', 'Compare floats safely', 'isclose(0.1 + 0.2, 0.3) is True']])}
{note('floor goes down and trunc goes toward zero. They agree for positive numbers and differ for negative ones: floor(&minus;4.8) is &minus;5, trunc(&minus;4.8) is &minus;4. round() is a built-in, not in math, and rounds halves to the even number.', 'exam')}
''', kw=['math module', 'ceil', 'floor', 'trunc', 'sqrt', 'factorial', 'hypot', 'gcd', 'isclose'])

K.lesson('randmod', 'The random module', f'''
{run('randmod')}
{table(['Function', 'Gives'], [
    ['random()', 'A float with 0.0 &le; x &lt; 1.0'],
    ['randint(a, b)', 'A whole number with a &le; n &le; b (b included!)'],
    ['randrange(start, stop, step)', 'Like range: stop is not included'],
    ['choice(seq)', 'One item'],
    ['sample(seq, k)', 'k different items, as a new list'],
    ['shuffle(list)', 'Mixes the list in place and returns None'],
    ['seed(n)', 'Restart the sequence, so results repeat (useful for tests)']])}
{note('random gives <b>pseudo-random</b> numbers from the Mersenne Twister algorithm: good for games and simulations, but predictable. For passwords, tokens and anything secret use the secrets module (secrets.token_hex(16)).', 'warn')}
''', kw=['random module', 'seed', 'randint', 'choice', 'sample', 'shuffle', 'Mersenne Twister', 'secrets'])

K.lesson('platmod', 'platform and sys: where am I running', f'''
{run('platmod')}
{note('The output above came from the build machine. Press Run on this page and platform.system() says Emscripten, because the Python on this page runs inside your browser (Pyodide). The same code gives Windows or Darwin on other computers.', 'tip')}
''', kw=['platform module', 'sys module', 'python_version', 'system', 'implementation'])

K.lesson('makemod', 'Writing your own module', f'''
{viz('pyimport')}
{run('makemod')}
{note('Any file name.py that Python can find is a module called name. Use lower case names with underscores, and never name your file after a standard module: a file called random.py in your folder hides the real random module, and import random gives you your own file.', 'warn')}
{deep('__pycache__', '<p>When a module is imported, CPython compiles it to bytecode and saves it as __pycache__/name.cpython-314.pyc. The next import skips compiling if the .py file has not changed. The main script you run is compiled every time and never cached. You can delete __pycache__ folders safely, and they usually go in .gitignore.</p>')}
''', kw=['own module', 'sys.path', 'sys.modules', 'importlib.reload', '__pycache__', 'pyc', 'shadowing a module'])

K.lesson('package', 'Packages: folders of modules', f'''
{run('package')}
{show('geometry/ (the package built by the program above)', '''geometry/
    __init__.py      runs on "import geometry"
    circle.py        geometry.circle
    square.py        geometry.square''', {1: 'A folder with an __init__.py file is a regular package.', 2: '__init__.py can be empty. Here it prints a line and re-exports area from circle.', 3: 'Inside the package, from .circle import area is a relative import: the dot means "this package".'}, 'text')}
{note('Since Python 3.3 a folder without __init__.py can still be imported as a namespace package, but an __init__.py makes the intent clear and lets you run setup code and choose what the package exports.', 'tip')}
''', kw=['package', '__init__.py', 'submodule', 'relative import', 'namespace package', '__all__'])

K.lesson('private', 'Public and private names, and __all__', f'''
{run('private')}
{table(['Name', 'Meaning by convention'], [
    ['slug', 'Public: part of what the module offers'],
    ['_clean', 'Internal: may change without warning. from module import * skips it'],
    ['__all__', 'The list of names that from module import * takes'],
    ['__name__, __file__, __doc__', 'Set by Python for every module']])}
''', kw=['private name', 'underscore', '__all__', 'public API', 'convention'])

K.lesson('mainguard', 'if __name__ == "__main__"', f'''
{run('mainguard')}
{wwh('Every module has a name in __name__. When you run a file directly, its __name__ is "__main__". When it is imported, __name__ is the module name.',
     'You often want one file to be both a library (functions others import) and a program (code that runs when you start it). Without the check, importing the file would also run the program part.',
     'Put the program part in a main() function and call it under if __name__ == "__main__":. Importing the file then only defines the functions.')}
''', kw=['__name__', '__main__', 'main guard', 'script vs module'])

K.lesson('pip', 'pip, PyPI and virtual environments', f'''
{term(['$ python3 -m venv .venv               # make a private environment for this project', '$ source .venv/bin/activate          # Windows: .venv\\Scripts\\activate', '(.venv) $ pip install requests       # download from PyPI and install', '(.venv) $ pip list                   # what is installed', '(.venv) $ pip show requests          # version, location, dependencies', '(.venv) $ pip install "flask>=3.0"     # a version rule', '(.venv) $ pip freeze > requirements.txt', '(.venv) $ pip install -r requirements.txt', '(.venv) $ pip uninstall requests', '(.venv) $ deactivate'], 'Installing packages (a typical session)')}
{wwh('<b>PyPI</b> (the Python Package Index, pypi.org) hosts hundreds of thousands of packages. <b>pip</b> downloads and installs them. A <b>virtual environment</b> (venv) is a private folder of packages for one project.',
     'Different projects need different versions: one app needs Django 4, another Django 5. Installing everything into the one system Python causes conflicts and can even break tools of your operating system.',
     'python -m venv .venv makes the folder. Activating it puts its python and pip first on your PATH, so pip install goes into that project only. requirements.txt records exact versions so others can rebuild the same environment.')}
{note('Run pip as python -m pip install ... when you are not sure which Python a plain pip belongs to. Modern projects describe their dependencies in a pyproject.toml file, and tools such as uv and poetry manage environments for you.', 'tip')}
''', kw=['pip', 'PyPI', 'venv', 'virtual environment', 'requirements.txt', 'pip install', 'pip freeze', 'pyproject.toml'])

K.lesson('stdlib', 'A short tour of the standard library', f'''
{run('stdlib')}
{table(['Module', 'For', 'Chapter'], [
    ['math, statistics, random, decimal, fractions', 'Numbers', 'Core 1.3 and here'],
    ['datetime, time, calendar', 'Dates and times', 'Here'],
    ['collections, itertools, functools, heapq, bisect', 'Data structures and iteration', 'Core 3.4, 4.3, Advanced 2.1 and 4.2'],
    ['os, os.path, pathlib, shutil, glob', 'Files and folders', 'Core 5.3'],
    ['json, csv, sqlite3, xml.etree, configparser, logging', 'Data formats and logs', 'Advanced 6.2'],
    ['re', 'Regular expressions', 'Advanced 6.1'],
    ['threading, multiprocessing, asyncio', 'Doing several things at once', 'Advanced 5.1'],
    ['socket, http, urllib', 'Networks and the web', 'Web 1.1 to 1.2'],
    ['unittest, doctest', 'Testing', 'Advanced 3.2'],
    ['tkinter', 'Desktop windows', 'Advanced 6.3']])}
''', kw=['standard library', 'datetime', 'collections', 'json', 'os.path', 'statistics', 'batteries included'])

K.lesson('maths', 'Maths you get from math and random', f'''
{fxs(fx('Combinations and permutations', 'C(n, k) = n! / (k!(n &minus; k)!), P(n, k) = n! / (n &minus; k)!', 'math.comb(5, 2) = 10, math.perm(5, 2) = 20.', key=True),
     fx('Euclid: greatest common divisor', 'gcd(a, b) = gcd(b, a mod b), gcd(a, 0) = a', 'gcd(84, 36) = gcd(36, 12) = gcd(12, 0) = 12. lcm(a, b) = a &times; b / gcd(a, b).', key=True),
     fx('Change of base for logarithms', 'log<sub>b</sub> x = ln x / ln b', 'math.log(8, 2) = 3.0. Floats can make this 2.9999999999999996 for other numbers, so use log2 for base 2.'),
     fx('Expected value of a fair die (randint(1, 6))', 'E = (1 + 2 + ... + 6)/6 = 3.5', 'The mean of many rolls gets close to 3.5 (law of large numbers).'),
     fx('Monte Carlo estimate of &pi;', '&pi; &asymp; 4 &times; (points with x<sup>2</sup> + y<sup>2</sup> &le; 1) / (all points)', 'Random points in a square, counted inside a quarter circle. The error shrinks like 1/&radic;n.'))}
{steps('Worked example: Euclid for gcd(1071, 462)', [
    '1071 mod 462 = 147, so gcd(1071, 462) = gcd(462, 147).',
    '462 mod 147 = 21, so it equals gcd(147, 21).',
    '147 mod 21 = 0, so it equals gcd(21, 0).',
    eq('gcd(1071, 462) = 21, which is what math.gcd(1071, 462) returns')])}
''', kw=['combinations', 'permutations', 'Euclid gcd', 'logarithm base', 'expected value', 'Monte Carlo'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>import math gives you math.sqrt and friends. A .py file you write is a module you can import too.</p>',
    '<p>Know every import form, the math, random and platform modules, packages with __init__.py, private _names, __all__, and if __name__ == "__main__". Install packages with pip inside a venv.</p>',
    '<p>Imports are cached in sys.modules and searched along sys.path. Modules run once. Relative imports work inside packages. Avoid circular imports and file names that hide standard modules. Use secrets, not random, for security.</p>',
    '<p>The import system is built from finders and loaders on sys.meta_path (importlib.machinery), which is how zip files, frozen modules and namespace packages are imported. Python 3.12 removed distutils, and packaging is now described by pyproject.toml (PEP 517, 518, 621) with build back ends such as setuptools and hatchling.</p>')}
{grow('Import a module three ways and use math and random.',
      'Write your own module and package, use __name__ and __all__, and manage packages with pip and venv.',
      'Explain sys.modules, sys.path, finders and loaders, and package a project with pyproject.toml.')}
''', kw=['beginner', 'expert', 'meta_path', 'finders and loaders', 'pyproject', 'circular import'])

lc(1979, 'Find Greatest Common Divisor of Array', 'find-greatest-common-divisor-of-array', 'e', 'math.gcd', 'Take the smallest and the largest number and return math.gcd of the two.', r'''
import math


def find_gcd(nums):
    return math.gcd(min(nums), max(nums))
''', [('find_gcd([2, 5, 6, 9, 10])', 2), ('find_gcd([7, 5, 6, 8, 3])', 1), ('find_gcd([3, 3])', 3)])
lc(1071, 'Greatest Common Divisor of Strings', 'greatest-common-divisor-of-strings', 'e', 'math.gcd on lengths', 'If str1 + str2 differs from str2 + str1 there is no answer. Otherwise the answer is the first gcd(len1, len2) characters.', r'''
import math


def gcd_of_strings(str1, str2):
    if str1 + str2 != str2 + str1:
        return ""
    size = math.gcd(len(str1), len(str2))
    return str1[:size]
''', [('gcd_of_strings("ABCABC", "ABC")', 'ABC'), ('gcd_of_strings("ABABAB", "ABAB")', 'AB'), ('gcd_of_strings("LEET", "CODE")', '')])
lc(69, 'Sqrt(x)', 'sqrtx', 'e', 'Binary search (or math.isqrt)', 'Find the largest m with m &times; m &le; x by halving the search range.', r'''
def my_sqrt(x):
    low = 0
    high = x
    answer = 0
    while low <= high:
        mid = (low + high) // 2
        if mid * mid <= x:
            answer = mid
            low = mid + 1
        else:
            high = mid - 1
    return answer
''', [('my_sqrt(4)', 2), ('my_sqrt(8)', 2), ('my_sqrt(0)', 0), ('my_sqrt(2147395599)', 46339)])
lc(367, 'Valid Perfect Square', 'valid-perfect-square', 'e', 'math.isqrt', 'math.isqrt(n) is the exact whole square root rounded down. Square it back and compare.', r'''
import math


def is_perfect_square(num):
    root = math.isqrt(num)
    return root * root == num
''', [('is_perfect_square(16)', True), ('is_perfect_square(14)', False), ('is_perfect_square(1)', True)])
lc(1185, 'Day of the Week', 'day-of-the-week', 'e', 'datetime', 'datetime.date(year, month, day).weekday() gives 0 for Monday. Map it to the names.', r'''
import datetime


def day_of_the_week(day, month, year):
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return names[datetime.date(year, month, day).weekday()]
''', [('day_of_the_week(31, 8, 2019)', 'Saturday'), ('day_of_the_week(18, 7, 1999)', 'Sunday'), ('day_of_the_week(15, 8, 1993)', 'Sunday')])
lc(1360, 'Number of Days Between Two Dates', 'number-of-days-between-two-dates', 'e', 'datetime subtraction', 'Turn both texts into dates with date.fromisoformat and take abs of the difference in days.', r'''
import datetime


def days_between_dates(date1, date2):
    a = datetime.date.fromisoformat(date1)
    b = datetime.date.fromisoformat(date2)
    return abs((a - b).days)
''', [('days_between_dates("2019-06-29", "2019-06-30")', 1), ('days_between_dates("2020-01-15", "2019-12-31")', 15)])
lc(1154, 'Day of the Year', 'day-of-the-year', 'e', 'datetime', 'Subtract 1 January of the same year and add 1.', r'''
import datetime


def day_of_year(date):
    d = datetime.date.fromisoformat(date)
    return (d - datetime.date(d.year, 1, 1)).days + 1
''', [('day_of_year("2019-01-09")', 9), ('day_of_year("2019-02-10")', 41), ('day_of_year("2020-12-31")', 366)])
lc(172, 'Factorial Trailing Zeroes', 'factorial-trailing-zeroes', 'm', 'Count factors of 5', 'Each trailing zero needs a 10 = 2 &times; 5, and 5s are rarer. Add n // 5 + n // 25 + n // 125 + ...', r'''
def trailing_zeroes(n):
    count = 0
    power = 5
    while power <= n:
        count = count + n // power
        power = power * 5
    return count
''', [('trailing_zeroes(3)', 0), ('trailing_zeroes(5)', 1), ('trailing_zeroes(100)', 24), ('trailing_zeroes(0)', 0)])
lc(384, 'Shuffle an Array', 'shuffle-an-array', 'm', 'random and the Fisher Yates shuffle', 'Keep a copy of the original. To shuffle, swap item i with a random item from i to the end.', r'''
import random


class Shuffler:  # called Solution on LeetCode
    def __init__(self, nums):
        self.original = nums[:]

    def reset(self):
        return self.original[:]

    def shuffle(self):
        items = self.original[:]
        for i in range(len(items)):
            j = random.randint(i, len(items) - 1)
            items[i], items[j] = items[j], items[i]
        return items
''', [('sorted(Shuffler([1, 2, 3]).shuffle())', [1, 2, 3]), ('Shuffler([1, 2, 3]).reset()', [1, 2, 3]), ('len(Shuffler([5, 6]).shuffle())', 2)])
lc(528, 'Random Pick with Weight', 'random-pick-with-weight', 'm', 'Prefix sums, random and bisect', 'Build running totals. Pick a random number up to the total and find its slot with bisect.', r'''
import bisect
import random


class WeightedPicker:  # called Solution on LeetCode, with pickIndex
    def __init__(self, w):
        self.totals = []
        running = 0
        for weight in w:
            running = running + weight
            self.totals.append(running)

    def pick_index(self):
        target = random.randint(1, self.totals[-1])
        return bisect.bisect_left(self.totals, target)
''', [('WeightedPicker([1]).pick_index()', 0), ('WeightedPicker([1, 3]).pick_index() in (0, 1)', True), ('WeightedPicker([1, 3]).totals', [1, 4])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>These problems are easy once you know the right standard module: math for gcd and square roots, datetime for calendars, random and bisect for random picks. Knowing the library is a skill interviewers value.</p>'), kw=['LeetCode', 'math.gcd', 'isqrt', 'datetime', 'random', 'bisect', 'Fisher Yates'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>module</b> is a .py file, a <b>package</b> is a folder of modules (usually with __init__.py).',
    'import math, import math as m, from math import sqrt, from math import sqrt as root. Avoid import *.',
    'import checks <b>sys.modules</b>, searches <b>sys.path</b>, runs the file once and caches it. importlib.reload runs it again.',
    'math: ceil, floor, trunc, sqrt, isqrt, hypot, factorial, comb, gcd, log, isclose. random: random, randint (both ends), randrange, choice, sample, shuffle, seed.',
    'A name starting with _ is private by convention. __all__ lists what import * takes.',
    '__name__ is "__main__" when a file is run directly. Guard the program part with if __name__ == "__main__":.',
    'pip installs packages from PyPI. Use a venv per project and record versions in requirements.txt.'],
    'Core 5.3 reads and writes files: open modes, reading line by line, with, paths, and text vs binary data.')}
{files('Three tasks: a dice simulation with a fixed seed, importing a module by its name, and gcd and lcm of a whole list.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which line lets you call sqrt(2) without math. in front?', ['import math', 'from math import sqrt', 'import sqrt', 'include math'], 1, 'Import the name.', 'from math import sqrt binds sqrt directly.')
K.quiz('e', 'What does math.ceil(4.1) give?', ['4', '5', '4.0', '4.1'], 1, 'Round up.', 'ceil rounds up to 5.')
K.quiz('e', 'Which tool installs packages from PyPI?', ['pyinstall', 'pip', 'import', 'venv'], 1, 'Three letters.', 'pip installs packages.')
K.quiz('m', 'random.randint(1, 3) can return', ['1 and 2 only', '1, 2 and 3', '0, 1 and 2', 'Any float'], 1, 'Both ends.', 'randint includes both a and b.')
K.quiz('m', 'What is __name__ in a file you run directly?', ['The file name', '"__main__"', 'None', '"main"'], 1, 'The main program.', 'The running script is called __main__.')
K.quiz('m', 'A module is imported twice in one program. How many times does its code run?', ['Twice', 'Once', 'Never', 'Depends on the size'], 1, 'Cached.', 'The second import uses sys.modules.')
K.quiz('m', 'What does math.trunc(-3.7) give?', ['-4', '-3', '3', '-3.7'], 1, 'Toward zero.', 'trunc cuts the fraction off: &minus;3.')
K.quiz('m', 'What does from tools import * skip when tools has no __all__?', ['Functions', 'Names starting with _', 'Classes', 'Nothing'], 1, 'Private by convention.', 'Names with a leading underscore are not imported.')
K.quiz('h', 'You save your file as random.py and run import random in it. What happens?', ['You get the standard module', 'You get your own file', 'SyntaxError', 'pip installs random'], 1, 'The script folder is first in sys.path.', 'Your file hides the standard module.')
K.quiz('h', 'Which makes a folder a regular package?', ['A setup.py', 'An __init__.py', 'A __main__.py', 'A requirements.txt'], 1, 'Init.', '__init__.py marks a regular package.')
K.quiz('h', 'Which module should make a password reset token?', ['random', 'secrets', 'math', 'platform'], 1, 'Not predictable.', 'secrets uses the operating system random source.')
K.quiz('x', 'In the style of an MIT 6.042 question: what is math.comb(10, 3) &minus; math.perm(10, 3) / 6?', ['0', '120', '720', '-600'], 0, 'P(n, k) = k! C(n, k).', 'perm(10, 3) = 720 and 720 / 6 = 120 = comb(10, 3), so the result is 0 (as a float, 0.0).')
K.quiz('x', 'In the style of a Stanford CS106A exam: random.seed(1) then a = random.random(), then random.seed(1) then b = random.random(). Is a == b?', ['Always True', 'Always False', 'True half the time', 'Error'], 0, 'Same seed, same sequence.', 'Seeding restarts the pseudo random sequence, so a and b are equal.')

K.calc('e', 'math.floor(-2.5)?', '-3', 'Down, not toward zero.', ['floor goes down the number line.', 'Below &minus;2.5 the next whole number is &minus;3.', eq('-3')], check=-3)
K.calc('e', 'math.hypot(6, 8)?', '10', '&radic;(36 + 64).', ['36 + 64 = 100.', '&radic;100.', eq('10.0')], check=10)
K.calc('e', 'math.comb(6, 2)?', '15', '6 &times; 5 / 2.', ['C(6, 2).', '30 / 2.', eq('15')], check=15)
K.calc('m', 'math.gcd(1071, 462)?', '21', 'Euclid.', ['1071 mod 462 = 147.', '462 mod 147 = 21, 147 mod 21 = 0.', eq('21')], check=21)
K.calc('m', 'math.lcm(4, 6, 10)?', '60', 'Smallest common multiple.', ['lcm(4, 6) = 12.', 'lcm(12, 10) = 60.', eq('60')], check=60)
K.calc('m', 'math.isqrt(99)?', '9', 'Whole root rounded down.', ['9 &times; 9 = 81 &le; 99.', '10 &times; 10 = 100 &gt; 99.', eq('9')], check=9)
K.calc('m', 'Expected value of randint(1, 6).', '3.5', 'Average of 1 to 6.', ['1 + ... + 6 = 21.', '21 / 6.', eq('3.5')], check=3.5)
K.calc('h', 'Trailing zeros of 100!.', '24', '100 // 5 + 100 // 25.', ['100 // 5 = 20.', '100 // 25 = 4, 100 // 125 = 0.', eq('24')], check=24)
K.calc('h', 'math.perm(5, 3)?', '60', '5 &times; 4 &times; 3.', ['P(5, 3) = 5! / 2!.', '120 / 2.', eq('60')], check=60)
K.calc('x', 'In the style of a Putnam style question: how many days after Saturday 7 November 2026 is Saturday 1 January 2028 (use datetime arithmetic)?', '420', 'date(2028, 1, 1) &minus; date(2026, 11, 7).', ['From 7 Nov 2026 to 7 Nov 2027 is 365 days.', 'Then to 1 Jan 2028 is 23 + 31 + 1 = 55 days.', eq('365 + 55 = 420, which is 60 weeks, so it is a Saturday too')], check=420)

K.assign('dice', 'e', 'Dice simulation with a fixed seed',
         '<p>Write <code>roll_counts(n, seed)</code> that seeds random with seed, rolls a die n times with random.randint(1, 6), and returns a list of 6 counts: how often each face 1 to 6 came up.</p>',
         '''
import random

def roll_counts(n, seed):
    # your code here
    pass
''', [('sum(roll_counts(600, 1))', 600), ('len(roll_counts(10, 2))', 6), ('roll_counts(5, 7) == roll_counts(5, 7)', True), ('roll_counts(0, 3)', [0, 0, 0, 0, 0, 0])],
         '''
import random

def roll_counts(n, seed):
    random.seed(seed)
    counts = [0, 0, 0, 0, 0, 0]
    for _ in range(n):
        face = random.randint(1, 6)
        counts[face - 1] = counts[face - 1] + 1
    return counts
''', 'Call random.seed(seed) first. counts[face - 1] += 1 for each roll.', '<p>With the same seed the counts are always the same, which makes simulations testable. With many rolls each count gets close to n/6.</p>')
K.assign('loadmod', 'm', 'Import a module by its name',
         '<p>Write <code>load(name)</code> that imports the module whose name is in the text name and returns it, or returns None if no such module exists. Use importlib.import_module and catch ModuleNotFoundError.</p>',
         '''
import importlib

def load(name):
    # your code here
    pass
''', [('load("math").sqrt(9)', 3.0), ('load("no_such_module_xyz")', None), ('load("json").__name__', 'json'), ('load("os.path") is __import__("os").path', True)],
         '''
import importlib

def load(name):
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError:
        return None
''', 'Put return importlib.import_module(name) in try and return None in except ModuleNotFoundError.', '<p>Plug in systems use this to load extra modules whose names come from a settings file. ModuleNotFoundError is a child of ImportError, so except ImportError would work too.</p>')
K.assign('gcdlist', 'm', 'gcd and lcm of a whole list',
         '<p>Write <code>gcd_lcm(nums)</code> that returns a tuple (gcd of all numbers, lcm of all numbers) using math.gcd only. Use lcm(a, b) = a &times; b // gcd(a, b).</p>',
         '''
import math

def gcd_lcm(nums):
    # your code here
    pass
''', [('gcd_lcm([12, 18, 24])', (6, 72)), ('gcd_lcm([7])', (7, 7)), ('gcd_lcm([4, 6, 10])', (2, 60))],
         '''
import math

def gcd_lcm(nums):
    g = nums[0]
    l = nums[0]
    for x in nums[1:]:
        g = math.gcd(g, x)
        l = l * x // math.gcd(l, x)
    return g, l
''', 'Start both with the first number. Fold the rest in one at a time.', '<p>This is reduce from Core 4.3 by hand. math.gcd and math.lcm also accept many arguments directly: math.gcd(*nums).</p>')

K.must('import forms', 'import m, import m as a, from m import x, from m import x as y. Avoid import *. Relative: from . import x.')
K.must('How import works', 'Check sys.modules, search sys.path, run the file once, cache it, bind the name. importlib.reload re-runs.')
K.must('math and random', 'ceil, floor, trunc, sqrt, isqrt, hypot, factorial, comb, gcd, log, isclose. randint(a, b) includes b, randrange excludes stop, seed repeats.')
K.must('Packages', 'Folder + __init__.py. _name is private by convention. __all__ controls import *. __pycache__ holds .pyc files.')
K.must('Main guard and pip', 'if __name__ == "__main__": main(). pip install inside a venv. pip freeze > requirements.txt.')

T = K.topic(
    slug='py-modules', topic='py-modules', step=(5, 'Errors, modules and files', 'py-c5', 'Handle errors with exceptions, organise code in modules and packages, and read and write files.', 'Intermediate'),
    title='Modules and packages: import, the standard library and pip', short='Modules and packages', badge='5.2', minutes=60,
    lead='Split code into files and use code others wrote. Learn every form of import and what import really does, the math, random and platform modules, writing your own modules and packages, private names and __all__, the main guard, pip, PyPI and virtual environments, and a tour of the standard library.',
    desc='modules and packages, import forms and aliases, dir(), sys.modules and sys.path, the math module, the random module and seeds, the platform and sys modules, writing a module, importlib.reload, __pycache__, packages and __init__.py, relative imports, private names and __all__, __name__ and the main guard, pip, PyPI, venv, requirements.txt, the standard library, combinations, Euclid and Monte Carlo maths.',
    summary='import forms, sys.modules and sys.path, math, random, platform, own modules and packages, __all__, main guard, pip and venv.',
    keywords=['module', 'package', 'import', 'math', 'random', 'platform', 'sys.path', '__init__.py', '__name__', 'pip', 'venv', 'PyPI', 'PCAP'],
    recap='<p>Modules split code into reusable files and packages group them. Import checks the cache, searches sys.path and runs a module once. pip and venv bring in the rest of the Python world safely.</p>',
    added='2026-11-07', leet=leet_items())
