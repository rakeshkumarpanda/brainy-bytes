# Advanced Python 3.1: clean code. Follows PCPP-32-101 block 2 (PEP 8 style, PEP 257 docstrings, PEP 20 the Zen of
# Python, coding conventions), checked against the texts of PEP 8, PEP 257, PEP 20, PEP 484 (type hints), PEP 604
# (X | Y), PEP 544 (protocols), PEP 589 (TypedDict), PEP 695 (type parameter syntax), the typing module and doctest
# documentation for Python 3.14. The ruff, black and mypy outputs below are real runs (ruff 0.17.4, black 26.10.1,
# mypy 2.4.1).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items, show, term

chapter('py-style')
K = Kit()

K.code('zen', r'''
import this
''')

K.code('recommend', r'''
class Weird:
    def __eq__(self, other):
        return True                            # claims to equal everything


w = Weird()
print(w == None, w is None)                    # == can be fooled, is cannot

items = []
if not items:                                  # empty things count as false
    print("empty list")
print(bool(""), bool(0), bool([0]), bool(" "))

print(isinstance(True, int), type(True) == int)   # isinstance respects inheritance

name = "report.csv"
print(name.endswith(".csv"), name[-4:] == ".csv")  # say what you mean


def add_item(item, basket=None):               # never use a list as a default
    if basket is None:
        basket = []
    basket.append(item)
    return basket


print(add_item("tea"), add_item("milk"))
''')

K.code('docstrings', r'''
import doctest


def average(numbers):
    """Return the mean of a non empty list of numbers.

    >>> average([2, 4, 6])
    4.0
    >>> average([5])
    5.0
    """
    return sum(numbers) / len(numbers)


class Wallet:
    """A simple wallet that holds money in rupees."""

    def __init__(self, amount=0):
        """Start with amount rupees (0 if not given)."""
        self.amount = amount


print(average.__doc__.splitlines()[0])
print(Wallet.__doc__, "|", Wallet.__init__.__doc__)
print(doctest.testmod())                       # runs the >>> examples above
''')

K.code('hints', r'''
def greet(name: str, times: int = 1) -> str:
    return ("Hello " + name + "! ") * times


def first[T](items: list[T]) -> T:             # a generic function (Python 3.12 and later)
    return items[0]


scores: dict[str, int] = {"asha": 90}
maybe: int | None = None

print(greet("Asha", 2))
print(first([3, 1, 2]), first(["x", "y"]))
print(greet.__annotations__)
print(first("hello"))                          # a str, not a list: Python does not check hints
''')

K.code('typing', r'''
from dataclasses import dataclass
from typing import Callable, Final, Literal, Protocol, TypedDict

MAX_USERS: Final = 100                         # checkers forbid changing a Final name


class Point(TypedDict):                        # the shape of a dict
    x: int
    y: int


type Direction = Literal["up", "down"]         # only these two strings (alias syntax: 3.12+)


def move(p: Point, way: Direction) -> Point:
    step = 1 if way == "up" else -1
    return {"x": p["x"], "y": p["y"] + step}


class Speaker(Protocol):                       # any class with a speak() method fits
    def speak(self) -> str: ...


@dataclass
class Dog:
    name: str

    def speak(self) -> str:
        return self.name + " says woof"


def introduce(s: Speaker) -> str:
    return "Meet: " + s.speak()


def apply(f: Callable[[int], int], value: int) -> int:
    return f(value)


print(move({"x": 0, "y": 0}, "up"))
print(introduce(Dog("Rex")), apply(abs, -7), MAX_USERS)
''')

MESSY = '''import sys, math
def CircleArea( R ):
  if R==None : return 0
  A=math.pi*R**2
  return A'''

SHOP = '''def total(prices: list[float], discount: float = 0.0) -> float:
    return sum(prices) * (1 - discount)


def label(name: str) -> str:
    return name.upper()


print(total([10.0, 20.0], "10%"))
print(label(42))
count: int = "three"'''

K.lesson('idea', 'Clean code: style, docstrings and type hints', f'''
{src('PEP 8, PEP 257, PEP 20, PEP 484, PEP 544, PEP 589, PEP 604, PEP 695, the typing and doctest documentation, and PCPP-32-101 block 2. Tool outputs are real runs of ruff 0.17.4, black 26.10.1 and mypy 2.4.1.')}
{wwh('<b>Clean code</b> is code that other people (and you, in six months) can read quickly and change safely. Python has written rules for it: <b>PEP 8</b> for layout and names, <b>PEP 257</b> for docstrings, <b>PEP 20</b> (the Zen of Python) for the spirit, and <b>type hints</b> (PEP 484) that say what kind of value each name holds.',
     'Code is read far more often than it is written. When every file looks different, readers waste time on layout instead of logic, and small mistakes hide in the mess. Some style rules also prevent real bugs: is None cannot be fooled, a None default avoids a shared list, and a type checker finds a wrong argument before any user does.',
     'You follow the rules by habit and let tools check them: a <b>formatter</b> (black or ruff format) fixes layout automatically, a <b>linter</b> (ruff or flake8) reports problems like unused imports and bad names, and a <b>type checker</b> (mypy or pyright) reads the hints and reports type mistakes without running the code.')}
{viz('pystyle')}
{run('zen')}
{note('The Zen is a set of values, not rules. Lines like "Readability counts", "Explicit is better than implicit" and "Errors should never pass silently" explain WHY PEP 8 and good habits exist.', 'tip')}
''', kw=['clean code', 'PEP 8', 'PEP 257', 'PEP 20', 'Zen of Python', 'readability', 'linter', 'formatter', 'type checker'])

K.lesson('pep8', 'PEP 8: layout and names', f'''
{table(['Rule', 'Do', 'Do not'], [
    ['Indentation', '4 spaces per level', 'Tabs, 2 spaces, or a mix'],
    ['Line length', 'At most 79 characters (72 for comments and docstrings)', 'Lines that need side scrolling'],
    ['Blank lines', '2 around top level functions and classes, 1 between methods', 'None at all, or many'],
    ['Imports', 'One per line, at the top: standard library, then third party, then your own, each group sorted', 'import sys, os in the middle of the file'],
    ['Spaces', 'x = 1, a == b, f(a, b), d["k"]', 'x=1, f( a ,b ), d ["k"]'],
    ['Functions and variables', 'snake_case: circle_area, total_price', 'CircleArea, totalPrice, A'],
    ['Classes', 'CapWords: ShoppingCart', 'shopping_cart'],
    ['Constants', 'UPPER_CASE: MAX_USERS', 'maxUsers'],
    ['Private by convention', '_helper, _cache', '__everything (name mangling, only when needed)'],
    ['Long expressions', 'Break inside brackets, operators at the start of the new line', 'Backslashes at line ends']])}
<p>This is the messy code from the animation, checked by the ruff linter:</p>
{show('messy.py', MESSY)}
{term(['$ ruff check --select E,F,W,N,I --output-format concise messy.py',
       'messy.py:1:1: E401 [*] Multiple imports on one line',
       'messy.py:1:1: I001 [*] Import block is un-sorted or un-formatted',
       'messy.py:1:8: F401 [*] `sys` imported but unused',
       'messy.py:2:5: N802 Function name `CircleArea` should be lowercase',
       'messy.py:2:17: N803 Argument name `R` should be lowercase',
       'messy.py:3:9: E711 Comparison to `None` should be `cond is None`',
       'messy.py:3:14: E701 Multiple statements on one line (colon)',
       'messy.py:4:3: N806 Variable `A` in function should be lowercase',
       'Found 8 errors.',
       '[*] 3 fixable with `--fix` (1 unsafe fix available with `--fix --unsafe-fixes`).'], 'Linting with ruff')}
{term(['$ black --diff messy.py',
       '@@ -1,5 +1,8 @@',
       ' import sys, math',
       '-def CircleArea( R ):',
       '-  if R==None : return 0',
       '-  A=math.pi*R**2',
       '-  return A',
       '+',
       '+',
       '+def CircleArea(R):',
       '+    if R == None:',
       '+        return 0',
       '+    A = math.pi * R**2',
       '+    return A'], 'Formatting with black')}
{note('black fixed the layout but not the names, the unused import or == None: a formatter only moves spaces and line breaks, it never changes meaning. That is why teams use a formatter AND a linter. ruff can do both (ruff format and ruff check).', 'exam')}
''', kw=['PEP 8', 'indentation', 'line length', 'naming conventions', 'snake_case', 'CapWords', 'imports order', 'ruff', 'black', 'flake8'])

K.lesson('recommend', 'Rules that prevent bugs', f'''
{run('recommend')}
{versus('Checking a value', ['', 'x == None', 'x is None', 'if not x'], [
    ['Asks', 'Does x say it equals None (__eq__)?', 'Is x the None object?', 'Is x empty, zero, False or None?'],
    ['Can a class change the answer', 'Yes', 'No', 'Yes, with __bool__ or __len__'],
    ['Right for', 'Never for None', 'Checking for a missing value', 'Checking for "nothing in it"']],
    'use is None for missing values and plain truthiness (if items:) for empty containers. They mean different things: 0 and [] are falsy but not None.')}
{note('PEP 8 also says: use isinstance instead of comparing types, use startswith and endswith instead of slicing, do not compare booleans to True with ==, and keep try blocks small so you only catch the error you expect.', 'tip')}
''', kw=['is None', 'truthiness', 'isinstance', 'endswith', 'mutable default', 'programming recommendations'])

K.lesson('docstrings', 'Docstrings and doctest (PEP 257)', f'''
{run('docstrings')}
{table(['PEP 257 rule', 'Example'], [
    ['Always triple double quotes', '"""Return the mean."""'],
    ['First line: a short summary that ends with a full stop, written as a command', '"""Return the mean of a list.""", not """Returns the mean"""'],
    ['Longer docstring: summary, blank line, then details', 'Arguments, return value, errors raised, examples'],
    ['Every public module, function, class and method gets one', 'Private helpers may skip it'],
    ['A class docstring says what the class is, __init__ says how to make one', 'See Wallet above']])}
{note('doctest finds >>> lines in docstrings, runs them and compares the output with the next line. TestResults(failed=0, attempted=2) means both examples still work. It keeps documentation honest. Real test suites come in 3.2.', 'tip')}
''', kw=['docstring', 'PEP 257', '__doc__', 'help', 'doctest', 'testmod'])

K.lesson('hints', 'Type hints', f'''
{run('hints')}
{note('Hints are stored in __annotations__ but Python never checks them while running: first("hello") worked although the hint says list. In Python 3.14 annotations are evaluated lazily (PEP 649 and 749), so a hint can even name a class defined later in the file.', 'exam')}
{run('typing')}
{table(['Hint', 'Means'], [
    ['int, str, float, bool, None', 'That exact kind of value'],
    ['list[int], dict[str, int], tuple[int, str], set[str]', 'Containers and what is inside'],
    ['int | None (old: Optional[int])', 'An int or None'],
    ['Callable[[int], str]', 'A function taking an int and returning a str'],
    ['Literal["up", "down"]', 'Only these values'],
    ['TypedDict', 'A dict with known keys and value types'],
    ['Protocol', 'Any class that has these methods (structural, "duck" typing)'],
    ['Final', 'Must not be changed after it is set'],
    ['def f[T](x: list[T]) -> T and type Alias = ...', 'Generics and aliases with the Python 3.12 syntax']])}
{show('shop.py', SHOP)}
{term(['$ mypy shop.py',
       'shop.py:9: error: Argument 2 to "total" has incompatible type "str"; expected "float"  [arg-type]',
       'shop.py:10: error: Argument 1 to "label" has incompatible type "int"; expected "str"  [arg-type]',
       'shop.py:11: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]',
       'Found 3 errors in 1 file (checked 1 source file)'], 'Type checking with mypy')}
{versus('Finding a type mistake', ['', 'no hints', 'hints and mypy', 'checks with isinstance at run time'], [
    ['When it is found', 'When a user hits that line', 'Before the program runs', 'When that line runs'],
    ['Cost while running', 'None', 'None', 'A little on every call'],
    ['Documents the code', 'No', 'Yes', 'Partly'],
    ['Catches every mistake', 'No', 'Most, if hints are complete', 'Only the ones you check']],
    'add hints to public functions and run mypy (or let your editor do it). Keep isinstance checks for data from outside, like user input or JSON.')}
''', kw=['type hints', 'annotations', 'mypy', 'typing', 'Optional', 'Union', 'Callable', 'Protocol', 'TypedDict', 'Literal', 'Final', 'generics', 'PEP 695'])

K.lesson('maths', 'The maths: complexity, paths and line budgets', f'''
{fxs(fx('Cyclomatic complexity (McCabe)', 'M = E &minus; N + 2 (edges and nodes of the control flow graph) = decision points + 1', 'circle_area has one if, so M = 1 + 1 = 2. ruff rule C901 warns when M is above a limit, often 10.', key=True),
     fx('Paths through k independent if statements', 'paths = 2<sup>k</sup>', '4 separate ifs give 16 paths. Smaller functions keep this testable.', key=True),
     fx('Minimum tests to cover every independent path', 'tests &ge; M', 'A function with M = 6 needs at least 6 tests for basis path coverage.'),
     fx('Characters left on a line', 'room = 79 &minus; indent', 'Code nested 2 levels deep (8 spaces) has 71 characters left.'),
     fx('Spaces of indentation', 'spaces = 4 &times; depth', '3 levels deep: 12 spaces. Deep nesting eats the line budget, a hint to split the function.'))}
{steps('Worked example: the complexity of a grading function', [
    'It has if, elif, elif and else: 3 decisions (else adds none).',
    'It also has a for loop: 1 more decision.',
    'Decisions = 3 + 1 = 4.',
    eq('M = 4 + 1 = 5, so at least 5 tests to cover its paths')])}
''', kw=['cyclomatic complexity', 'McCabe', 'C901', 'paths', 'test cases', 'line length'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Follow the PEP 8 basics: 4 space indents, snake_case names, spaces around operators, one statement per line.</p>',
    '<p>Write PEP 257 docstrings with doctest examples, use is None and truthiness correctly, and run a formatter and a linter.</p>',
    '<p>Add type hints with generics, unions, Callable, Protocol and TypedDict, and run mypy in strict mode.</p>',
    '<p>Configure ruff, black and mypy in pyproject.toml and run them in pre commit hooks and CI. Know the limits: gradual typing, Any, variance of generics (list is invariant, Sequence is covariant), and PEP 649 lazy annotations read through annotationlib.</p>')}
{grow('Write PEP 8 style code.', 'Document and lint it.', 'Type it fully and automate every check.')}
''', kw=['beginner', 'expert', 'pre-commit', 'pyproject.toml', 'variance', 'strict mypy'])

lc(520, 'Detect Capital', 'detect-capital', 'e', 'Three allowed shapes', 'Like a naming rule: all capitals, all small, or only the first letter capital.', r'''
def detect_capital_use(word: str) -> bool:
    """Return True if word is all caps, all lower case, or Capitalised."""
    return word.isupper() or word.islower() or word.istitle()
''', [('detect_capital_use("USA")', True), ('detect_capital_use("FlaG")', False), ('detect_capital_use("leetcode")', True), ('detect_capital_use("Google")', True)])
lc(482, 'License Key Formatting', 'license-key-formatting', 'e', 'Clean, then group from the right', 'Remove dashes, make it upper case, then cut groups of k from the end so only the first group may be shorter.', r'''
def license_key_formatting(s: str, k: int) -> str:
    """Return the key in upper case groups of k, joined by dashes."""
    clean = s.replace("-", "").upper()
    first = len(clean) % k or k
    groups = [clean[:first]]
    for start in range(first, len(clean), k):
        groups.append(clean[start:start + k])
    return "-".join(group for group in groups if group)
''', [('license_key_formatting("5F3Z-2e-9-w", 4)', '5F3Z-2E9W'), ('license_key_formatting("2-5g-3-J", 2)', '2-5G-3J'), ('license_key_formatting("---", 3)', '')])
lc(273, 'Integer to English Words', 'integer-to-english-words', 'h', 'Groups of three digits with clear helper names', 'Split the number into groups of three from the right (ones, Thousand, Million, Billion). Turn each group under 1000 into words with a small helper, and skip groups that are zero.', r'''
BELOW_20 = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
            "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen",
            "Eighteen", "Nineteen"]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
GROUP_NAMES = ["", "Thousand", "Million", "Billion"]


def three_digits_to_words(number: int) -> list[str]:
    """Return the words for a number from 0 to 999."""
    words = []
    if number >= 100:
        words += [BELOW_20[number // 100], "Hundred"]
        number = number % 100
    if number >= 20:
        words.append(TENS[number // 10])
        number = number % 10
    if number > 0:
        words.append(BELOW_20[number])
    return words


def number_to_words(num: int) -> str:
    """Return num written in English words, for example 123 is One Hundred Twenty Three."""
    if num == 0:
        return "Zero"
    words = []
    group = 0
    while num > 0:
        part = num % 1000
        if part > 0:
            words = three_digits_to_words(part) + ([GROUP_NAMES[group]] if group else []) + words
        num = num // 1000
        group += 1
    return " ".join(words)
''', [('number_to_words(123)', 'One Hundred Twenty Three'), ('number_to_words(12345)', 'Twelve Thousand Three Hundred Forty Five'), ('number_to_words(1234567)', 'One Million Two Hundred Thirty Four Thousand Five Hundred Sixty Seven'), ('number_to_words(0)', 'Zero'), ('number_to_words(1000010)', 'One Million Ten')])
lc(824, 'Goat Latin', 'goat-latin', 'e', 'Follow the rules word by word', 'Vowel start: add "ma". Otherwise move the first letter to the end and add "ma". Then add one "a" per word position.', r'''
def to_goat_latin(sentence: str) -> str:
    """Return sentence translated into Goat Latin."""
    result = []
    for position, word in enumerate(sentence.split(), start=1):
        if word[0].lower() in "aeiou":
            goat = word + "ma"
        else:
            goat = word[1:] + word[0] + "ma"
        result.append(goat + "a" * position)
    return " ".join(result)
''', [('to_goat_latin("I speak Goat Latin")', 'Imaa peaksmaaa oatGmaaaa atinLmaaaaa')])
lc(1859, 'Sorting the Sentence', 'sorting-the-sentence', 'e', 'Sort by the last character', 'Each word ends with its position. Sort by that digit and remove it.', r'''
def sort_sentence(s: str) -> str:
    """Return the sentence with words put back in order."""
    words = sorted(s.split(), key=lambda word: word[-1])
    return " ".join(word[:-1] for word in words)
''', [('sort_sentence("is2 sentence4 This1 a3")', 'This is a sentence'), ('sort_sentence("Myself2 Me1 I4 and3")', 'Me Myself and I')])
lc(2047, 'Number of Valid Words in a Sentence', 'number-of-valid-words-in-a-sentence', 'e', 'Check each rule, like a linter', 'No digits, at most one hyphen with letters on both sides, at most one punctuation mark and only at the end.', r'''
def is_valid_token(token: str) -> bool:
    """Return True if token follows every rule of the problem."""
    if any(ch.isdigit() for ch in token):
        return False
    if token.count("-") > 1:
        return False
    if "-" in token:
        i = token.index("-")
        if i == 0 or i == len(token) - 1 or not token[i - 1].isalpha() or not token[i + 1].isalpha():
            return False
    marks = [i for i, ch in enumerate(token) if ch in "!.,"]
    return not marks or (len(marks) == 1 and marks[0] == len(token) - 1)


def count_valid_words(sentence: str) -> int:
    """Return how many tokens of sentence are valid words."""
    return sum(1 for token in sentence.split() if is_valid_token(token))
''', [('count_valid_words("cat and  dog")', 3), ('count_valid_words("!this  1-s b8d!")', 0), ('count_valid_words("alice and  bob are playing stone-game10")', 5)])
lc(929, 'Unique Email Addresses', 'unique-email-addresses', 'e', 'Normalise, then count with a set', 'In the local part drop everything after "+" and remove dots. Keep the domain as it is.', r'''
def num_unique_emails(emails: list[str]) -> int:
    """Return how many different addresses actually receive mail."""
    seen = set()
    for email in emails:
        local, domain = email.split("@")
        local = local.split("+")[0].replace(".", "")
        seen.add(local + "@" + domain)
    return len(seen)
''', [('num_unique_emails(["test.email+alex@leetcode.com", "test.e.mail+bob.cathy@leetcode.com", "testemail+david@lee.tcode.com"])', 2)])
lc(1556, 'Thousand Separator', 'thousand-separator', 'e', 'Format with a separator', 'Python can group digits with format(n, ","). LeetCode wants dots, so swap the commas.', r'''
def thousand_separator(n: int) -> str:
    """Return n with a dot between every group of three digits."""
    return format(n, ",").replace(",", ".")
''', [('thousand_separator(987)', '987'), ('thousand_separator(1234)', '1.234'), ('thousand_separator(0)', '0')])
lc(1694, 'Reformat Phone Number', 'reformat-phone-number', 'e', 'Blocks of 3, end with 2 and 2 if 4 are left', 'Keep only digits. Take blocks of 3 while more than 4 remain. Then 4 digits become 2 and 2, otherwise one last block.', r'''
def reformat_number(number: str) -> str:
    """Return the digits of number in blocks of three, never ending with one digit."""
    digits = "".join(ch for ch in number if ch.isdigit())
    blocks = []
    while len(digits) > 4:
        blocks.append(digits[:3])
        digits = digits[3:]
    if len(digits) == 4:
        blocks += [digits[:2], digits[2:]]
    else:
        blocks.append(digits)
    return "-".join(blocks)
''', [('reformat_number("1-23-45 6")', '123-456'), ('reformat_number("123 4-567")', '123-45-67'), ('reformat_number("123 4-5678")', '123-456-78')])
lc(2299, 'Strong Password Checker II', 'strong-password-checker-ii', 'e', 'One check per rule', 'At least 8 characters, a lower case letter, an upper case letter, a digit, a special character, and no two equal characters side by side.', r'''
SPECIAL = "!@#$%^&*()-+"


def strong_password_checker_ii(password: str) -> bool:
    """Return True if password passes every rule."""
    if len(password) < 8:
        return False
    if any(a == b for a, b in zip(password, password[1:])):
        return False
    return (any(ch.islower() for ch in password)
            and any(ch.isupper() for ch in password)
            and any(ch.isdigit() for ch in password)
            and any(ch in SPECIAL for ch in password))
''', [('strong_password_checker_ii("IloveLe3tcode!")', True), ('strong_password_checker_ii("Me+You--IsMyDream")', False), ('strong_password_checker_ii("1aB!")', False)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Every problem is about following written rules for text exactly, which is what a style guide asks of code. The downloadable solutions are written the way this chapter teaches: PEP 8 layout, clear names, a docstring and type hints on every function.</p>'), kw=['LeetCode', 'string rules', 'formatting', 'validation', 'type hints'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'PEP 8: 4 spaces, lines up to 79 characters, 2 blank lines around top level definitions, sorted imports one per line.',
    'Names: snake_case for functions and variables, CapWords for classes, UPPER_CASE for constants.',
    'Use is None, truthiness for empty containers, isinstance, and None instead of a mutable default.',
    'PEP 257: triple double quoted docstrings with a one line summary. doctest runs the examples in them.',
    'Type hints document types and let mypy find mistakes before running. Python itself ignores them.',
    'A formatter fixes layout, a linter finds problems, a type checker finds type mistakes: use all three.'],
    '3.2 is about testing: unittest, pytest, fixtures and mocks.')}
{files('Three tasks: check that a name is a valid PEP 8 function name, read the type hints of a function, and convert CamelCase names to snake_case.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'How many spaces does PEP 8 use for one level of indentation?', ['2', '4', '8', 'A tab'], 1, 'The standard.', 'PEP 8 says 4 spaces per level.')
K.quiz('e', 'Which name follows PEP 8 for a class?', ['shopping_cart', 'ShoppingCart', 'SHOPPING_CART', 'shoppingCart'], 1, 'CapWords.', 'Classes use CapWords. Functions use snake_case.')
K.quiz('e', 'Which is the right way to check that x is missing?', ['x == None', 'x is None', 'x = None', 'None(x)'], 1, 'Identity.', 'None is a single object, so compare with is.')
K.quiz('m', 'What does Python do with a type hint like def f(x: int) when you call f("hi")?', ['Raises TypeError', 'Nothing, hints are not checked at run time', 'Converts "hi" to int', 'Prints a warning'], 1, 'Hints are for tools.', 'Only a type checker such as mypy reports it.')
K.quiz('m', 'In which order does PEP 8 group imports?', ['Your own, third party, standard library', 'Standard library, third party, your own', 'Alphabetical only', 'Any order'], 1, 'From general to specific.', 'Each group is separated by a blank line.')
K.quiz('m', 'What is the difference between a formatter and a linter?', ['None', 'A formatter only changes layout, a linter reports problems such as unused imports and bad names', 'A linter runs the code', 'A formatter checks types'], 1, 'Layout versus problems.', 'black left == None and the bad names untouched, ruff check reported them.')
K.quiz('m', 'What should the first line of a PEP 257 docstring be?', ['The author name', 'A short summary ending with a full stop', 'The list of arguments', 'Empty'], 1, 'One line summary.', 'For example """Return the mean of a list."""')
K.quiz('m', 'Which hint means "an int or None" in modern Python?', ['int or None', 'int | None', 'int & None', 'None[int]'], 1, 'PEP 604.', 'Optional[int] is the older spelling.')
K.quiz('h', 'Why is def add(item, basket=[]): a bug?', ['Lists cannot be defaults', 'The same list is shared by every call that uses the default', 'It is a syntax error', 'basket becomes a tuple'], 1, 'Defaults are made once.', 'The default list is created when def runs, so items pile up across calls. Use None and make a new list inside.')
K.quiz('h', 'A class Speaker(Protocol) has speak(). Dog has speak() but does not inherit from Speaker. Does mypy accept a Dog where a Speaker is expected?', ['No', 'Yes, protocols check the methods, not the parent class', 'Only with register()', 'Only at run time'], 1, 'Structural typing.', 'This is static duck typing (PEP 544).')
K.quiz('h', 'What does doctest.testmod() print when every example passes?', ['Nothing at all', 'TestResults(failed=0, attempted=N) when you print its return value', 'OK', 'The docstrings'], 1, 'It returns a result.', 'testmod is quiet on success and returns a named tuple you can print.')
K.quiz('x', 'In the style of a Berkeley CS 169 exam: a function has cyclomatic complexity 6. What is the minimum number of tests that covers every independent path?', ['1', '3', '6', '64'], 2, 'Basis paths.', 'The number of linearly independent paths equals M.')
K.quiz('x', 'In the style of an Oxford software engineering exam: which line of the Zen of Python argues for raising an error instead of returning a special value like -1?', ['Flat is better than nested', 'Errors should never pass silently', 'Beautiful is better than ugly', 'Namespaces are one honking great idea'], 1, 'Silent failures.', 'A -1 can be used by mistake as a real value. An exception cannot be ignored without saying so.')

K.calc('e', 'A function has 3 decision points. What is its cyclomatic complexity?', '4', 'Decisions + 1.', ['Decisions = 3.', 'Add 1.', eq('M = 4')], check=3 + 1)
K.calc('e', 'How many spaces of indentation does code 3 levels deep have under PEP 8?', '12', '4 per level.', ['Level 1: 4 spaces.', 'Each level adds 4.', eq('3 &times; 4 = 12')], check=12)
K.calc('e', 'Code is indented 8 spaces. How many characters are left for it on a 79 character line?', '71', '79 &minus; indent.', ['Limit: 79.', 'Indent: 8.', eq('79 &minus; 8 = 71')], check=79 - 8)
K.calc('m', 'A control flow graph has 9 edges and 8 nodes. What is M?', '3', 'M = E &minus; N + 2.', ['E = 9, N = 8.', '9 &minus; 8 = 1.', eq('1 + 2 = 3')], check=9 - 8 + 2)
K.calc('m', 'A function has 4 independent if statements. How many paths can run through it?', '16', '2<sup>k</sup>.', ['Each if: taken or not, 2 ways.', '4 ifs: 2 &times; 2 &times; 2 &times; 2.', eq('16')], check=2 ** 4)
K.calc('m', 'A function has if, elif, elif, else and one for loop. What is its cyclomatic complexity?', '5', 'else adds no decision.', ['if, elif, elif: 3 decisions.', 'The for loop: 1 more.', eq('4 + 1 = 5')], check=5)
K.calc('m', 'ruff reported 8 problems and 3 can be fixed automatically. What percentage is that?', '37.5', 'Part over whole.', ['3 / 8 = 0.375.', 'Times 100.', eq('37.5 %')], check=3 / 8 * 100)
K.calc('h', 'A docstring line is indented 4 spaces and has 3 quote marks at each end. How many characters of text fit in the 72 character limit?', '62', 'Subtract indent and quotes.', ['Indent: 4.', 'Quotes: 3 + 3 = 6.', eq('72 &minus; 4 &minus; 6 = 62')], check=72 - 4 - 6)
K.calc('h', 'Splitting a function with M = 9 into three functions of M = 3 each: how many basis path tests are needed in total?', '9', 'Add the parts.', ['Each part needs 3 tests.', '3 parts.', eq('3 &times; 3 = 9, but each test is now small and focused')], check=9)
K.calc('x', 'In the style of a CMU 17-313 exam: a team writes 400 lines a day and reads each line about 10 times. Reading takes 2 seconds a line, and clean style cuts it by 25 %. How many minutes a day does that save?', '33.3', 'Lines read times seconds saved.', ['Line reads per day: 400 &times; 10 = 4000.', 'Seconds saved: 4000 &times; 2 &times; 0.25 = 2000.', eq('2000 / 60 &asymp; 33.3 minutes')], check=round(400 * 10 * 2 * 0.25 / 60, 1))

K.assign('validname', 'e', 'Is it a good PEP 8 function name?',
         '<p>Write <code>is_good_function_name(name)</code>. It returns True only if name is a valid Python identifier, is not a keyword, and is written in lower case snake_case (letters, digits and underscores, no capital letters). Use str.isidentifier and the keyword module.</p>',
         '''
import keyword


def is_good_function_name(name):
    return name.isidentifier()
''', [('is_good_function_name("circle_area")', True), ('is_good_function_name("CircleArea")', False), ('is_good_function_name("2nd_try")', False), ('is_good_function_name("class")', False), ('is_good_function_name("get_v2")', True)],
         '''
import keyword


def is_good_function_name(name):
    if not name.isidentifier():
        return False
    if keyword.iskeyword(name):
        return False
    return name == name.lower()
''', 'Check isidentifier first, then keyword.iskeyword, then compare name with name.lower().', '<p>isidentifier already refuses names that start with a digit or contain spaces or dashes, so three checks are enough.</p>')
K.assign('readhints', 'm', 'Read the type hints of a function',
         '<p>Write <code>hint_names(func)</code> that returns a dict from each annotated parameter name (and "return") to the hint written as text. Classes give their name (int gives "int"), other hints give str(hint) (list[str] gives "list[str]"). Parameters without a hint are left out.</p>',
         '''
def hint_names(func):
    return {}


def sample(a: int, b: list[str], c, d: float = 1.0) -> bool:
    return True


def no_hints(x):
    return x
''', [('hint_names(sample)', {'a': 'int', 'b': 'list[str]', 'd': 'float', 'return': 'bool'}), ('hint_names(no_hints)', {}), ('list(hint_names(sample))[-1]', 'return')],
         '''
def hint_names(func):
    result = {}
    for name, hint in func.__annotations__.items():
        if isinstance(hint, type):
            result[name] = hint.__name__
        else:
            result[name] = str(hint)
    return result


def sample(a: int, b: list[str], c, d: float = 1.0) -> bool:
    return True


def no_hints(x):
    return x
''', 'Loop over func.__annotations__.items(). isinstance(hint, type) is True for plain classes like int.', '<p>list[str] is not a class but a generic alias, which is why it needs str(). For real projects inspect.get_annotations and typing.get_type_hints handle more cases.</p>')
K.assign('snake', 'h', 'Convert CamelCase names to snake_case',
         '<p>Write <code>snake_case(name)</code> that turns CamelCase or mixedCase into snake_case: "CircleArea" gives "circle_area", "getHTTPResponse" gives "get_http_response", "version2Name" gives "version2_name". A name already in snake_case stays the same.</p>',
         '''
def snake_case(name):
    return name.lower()
''', [('snake_case("CircleArea")', 'circle_area'), ('snake_case("getHTTPResponse")', 'get_http_response'), ('snake_case("version2Name")', 'version2_name'), ('snake_case("already_snake")', 'already_snake'), ('snake_case("X")', 'x')],
         '''
def snake_case(name):
    result = ""
    for i in range(len(name)):
        ch = name[i]
        if ch.isupper() and i > 0:
            before = name[i - 1]
            after = name[i + 1] if i + 1 < len(name) else ""
            if before.islower() or before.isdigit() or (before.isupper() and after.islower()):
                result += "_"
        result += ch.lower()
    return result
''', 'Add "_" before a capital letter when the letter before it is lower case or a digit, or when it starts a new word after a run of capitals (the next letter is lower case).', '<p>The tricky case is a run of capitals like HTTP: the underscore goes before the last capital, the one that starts the next word (Response).</p>')

K.must('PEP 8 layout', '4 spaces, 79 characters, 2 blank lines around top level defs, imports one per line grouped stdlib, third party, local.')
K.must('PEP 8 names', 'snake_case functions and variables, CapWords classes, UPPER_CASE constants, _private by convention.')
K.must('Bug preventing habits', 'is None, if items:, isinstance, startswith and endswith, None instead of mutable defaults, small try blocks.')
K.must('Docstrings', 'PEP 257: """One line summary.""" then details. __doc__ and help() read it. doctest runs >>> examples.')
K.must('Type hints and tools', 'list[int], int | None, Callable, Protocol, TypedDict, Literal, Final, def f[T]. Not checked at run time: use mypy, ruff and black.')

T = K.topic(
    slug='py-style', topic='py-style', step=(3, 'Professional code: style, testing and logging', 'py-a3', 'Write code others can read, prove it works with tests, and find problems fast with logging and debugging.', 'Advanced'),
    title='Clean code: PEP 8, docstrings and type hints', short='Style and type hints', badge='3.1', minutes=70,
    lead='Write code that is easy to read and hard to break. Learn the Zen of Python, the PEP 8 layout and naming rules, the habits that prevent bugs, PEP 257 docstrings with doctest, type hints from simple to generic, and the tools that check all of it: ruff, black and mypy.',
    desc='PEP 20, PEP 8 indentation, line length, blank lines, imports, whitespace and names, programming recommendations (is None, truthiness, isinstance, mutable defaults), PEP 257 docstrings, doctest, type hints, __annotations__, list[int], unions, Callable, Literal, TypedDict, Protocol, Final, generics and aliases with PEP 695 syntax, ruff, black, mypy, cyclomatic complexity.',
    summary='Zen of Python, PEP 8 layout and names, bug preventing habits, docstrings, doctest, type hints, ruff, black, mypy.',
    keywords=['PEP 8', 'PEP 257', 'PEP 20', 'type hints', 'mypy', 'ruff', 'black', 'docstring', 'doctest', 'Protocol', 'clean code', 'PCPP'],
    recap='<p>Follow PEP 8 by habit, document with docstrings, add type hints, and let a formatter, a linter and a type checker do the checking.</p>',
    added='2026-11-07', leet=leet_items())
