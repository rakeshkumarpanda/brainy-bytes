# Core Python 4.3: lambda, map, filter and comprehensions. Follows PCAP-31-03 section 4 (lambda functions, map(),
# filter(), closures, generators and list comprehensions) and PCEP-30-02 list comprehensions, checked against the
# Python 3.14 tutorial sections 4.9.6 and 5.1.3 to 5.1.4, the functional programming HOWTO and the functools and
# operator documentation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-functional')
K = Kit()

K.code('lambda', r'''
square = lambda x: x * x        # a tiny function without a def
print(square(7))

add = lambda a, b=10: a + b     # parameters and defaults work as usual
print(add(1), add(1, 2))

def square_def(x):              # the same thing with def
    return x * x
print(square_def(7), square.__name__, square_def.__name__)

print((lambda word: word[::-1])("level"))    # called at once
''')

K.code('key', r'''
students = [("Asha", 88), ("Ravi", 72), ("Meera", 95), ("John", 72)]

print(sorted(students, key=lambda s: s[1]))                 # by mark
print(sorted(students, key=lambda s: s[1], reverse=True))   # highest first
print(sorted(students, key=lambda s: (-s[1], s[0])))        # mark down, then name up
print(max(students, key=lambda s: s[1]))
print(min(["kiwi", "fig", "banana"], key=len))

from operator import itemgetter
print(sorted(students, key=itemgetter(1, 0)))               # the same as lambda s: (s[1], s[0])
''')

K.code('mapfilter', r'''
prices = [120, 45, 300, 80]

with_tax = map(lambda p: p * 1.18, prices)     # apply a function to every item
print(with_tax)                                # a lazy map object
print([round(p, 2) for p in with_tax])

cheap = filter(lambda p: p < 100, prices)      # keep items where the test is True
print(list(cheap))

print(list(map(str.upper, ["a", "b"])))        # any function works, not only lambdas
print(list(map(lambda a, b: a + b, [1, 2, 3], [10, 20, 30])))   # two lists at once
print(list(filter(None, [0, 1, "", "hi", None, []])))           # None keeps truthy items

from functools import reduce
print(reduce(lambda total, p: total + p, prices, 0))   # fold the list into one value
''')

K.code('listcomp', r'''
nums = [3, 8, 1, 6, 5]

squares = [n * n for n in nums]
evens = [n for n in nums if n % 2 == 0]
labels = ["even" if n % 2 == 0 else "odd" for n in nums]   # if-else goes BEFORE for
print(squares)
print(evens)
print(labels)

words = ["  Apple ", "banana", " Cherry"]
clean = [w.strip().lower() for w in words]
print(clean)
print([len(w) for w in clean if w.startswith(("a", "c"))])
''')

K.code('nestedcomp', r'''
pairs = [(x, y) for x in range(1, 4) for y in "ab"]     # the left for is the outer loop
print(pairs)

matrix = [[1, 2, 3], [4, 5, 6]]
flat = [v for row in matrix for v in row]
print(flat)

transposed = [[row[c] for row in matrix] for c in range(3)]   # a comprehension inside one
print(transposed)

table = [[r * c for c in range(1, 4)] for r in range(1, 4)]
print(table)
''')

K.code('dictset', r'''
words = ["apple", "fig", "banana", "kiwi", "fig"]

lengths = {w: len(w) for w in words}             # dict comprehension
print(lengths)
first_letters = {w[0] for w in words}            # set comprehension
print(sorted(first_letters))
long_words = {w: n for w, n in lengths.items() if n > 3}
print(long_words)
flipped = {n: w for w, n in lengths.items()}     # later words win for equal lengths
print(flipped)
''')

K.code('genexp', long=True, src=r'''
import sys

as_list = [n * n for n in range(10_000)]
as_gen = (n * n for n in range(10_000))        # round brackets: a generator expression
print(sys.getsizeof(as_list) > 50_000, sys.getsizeof(as_gen) < 300)
print(sum(as_gen))                             # values are made one at a time
print(sum(as_gen))                             # a generator can be used only once

print(sum(n * n for n in range(1, 11)))        # no extra brackets needed in a call
print(any(n > 9 for n in [3, 12, 5]), all(n > 0 for n in [3, 12, 5]))
print(max(len(w) for w in ["a", "abc", "ab"]))
''')

K.code('higher', r'''
from functools import partial

def make_greeter(greeting):          # a function that returns a function
    return lambda name: f"{greeting}, {name}!"

hello = make_greeter("Hello")
namaste = make_greeter("Namaste")
print(hello("Asha"), namaste("Ravi"))

def compose(f, g):                   # (f o g)(x) = f(g(x))
    return lambda x: f(g(x))

shout_len = compose(len, str.upper)
print(shout_len("python"))

base2 = partial(int, base=2)         # fix some arguments of an existing function
print(base2("1011"), base2("11111111"))

pipeline = [str.strip, str.lower, lambda s: s.replace(" ", "-")]
text = "  Hello World Python "
for step in pipeline:
    text = step(text)
print(text)
''')

K.lesson('idea', 'Functions as values: the functional style', f'''
{src('Python 3.14 tutorial sections 4.9.6 and 5.1.3 to 5.1.4, the Functional Programming HOWTO, and PCAP-31-03 section 4.')}
{wwh('A <b>lambda</b> is a small function written in one expression. <b>map</b> and <b>filter</b> apply a function to every item of a collection. A <b>comprehension</b> builds a new list, dict or set from an old one in a single readable line.',
     'Many jobs are "do something to every item" or "keep the items that pass a test". Writing a full loop with an empty list and append each time is long and hides the idea. These tools say the idea directly: squares of all numbers, prices under 100, names in upper case.',
     'Because functions are objects (Core 4.1), you can hand a small function to sorted, max, map or filter. A comprehension is a loop and an optional if folded into brackets. Python runs it like the loop, but you read it like a sentence.')}
{scene('a mark sheet in a spreadsheet', '<p>A teacher has a column of marks. "Add 5 grace marks to everyone" is map. "Show only students below 40" is filter. "Sort by mark, highest first" is sorted with a key. "Make a new column that says Pass or Fail" is a comprehension with if-else. One line each, and the original column is not changed.</p>')}
{run('lambda')}
''', kw=['lambda', 'functional programming', 'map', 'filter', 'comprehension', 'anonymous function'])

K.lesson('lambda', 'lambda: a function in one expression', f'''
{versus('lambda or def', ['', 'lambda', 'def'], [
    ['Body', 'One expression, its value is returned', 'Any statements, return when you want'],
    ['Name', 'Anonymous (shown as &lt;lambda&gt;)', 'Has a real name for errors and tracebacks'],
    ['Docstring and type hints', 'No', 'Yes'],
    ['Best for', 'A tiny throw away function passed to sorted, max, map', 'Anything you name, reuse or test']],
    'use a lambda only as an argument. If you write name = lambda ..., a def is clearer (PEP 8 says so too).')}
{note('A lambda cannot contain statements such as if blocks, for loops, return or assignment with =. It can contain a conditional expression: lambda n: "even" if n % 2 == 0 else "odd".', 'exam')}
''', kw=['lambda', 'lambda vs def', 'anonymous', 'PEP 8', 'conditional expression'])

K.lesson('key', 'Sorting and choosing with key', f'''
{run('key')}
{note('key is a function that is called once per item. Python sorts by what it returns. To sort by two things, return a tuple: tuples compare item by item. To reverse just one of two numeric keys, make it negative.', 'tip')}
''', kw=['sorted key', 'max key', 'min key', 'sort by two keys', 'itemgetter', 'operator'])

K.lesson('mapfilter', 'map, filter and reduce', f'''
{run('mapfilter')}
{table(['Tool', 'Takes', 'Gives', 'Comprehension version'], [
    ['map(f, items)', 'A function and one or more iterables', 'A lazy iterator of f(x)', '[f(x) for x in items]'],
    ['filter(test, items)', 'A test function (or None) and an iterable', 'A lazy iterator of the x where test(x) is true', '[x for x in items if test(x)]'],
    ['reduce(f, items, start)', 'A function of two values', 'One value', 'A loop with an accumulator, or sum, max, min']])}
{note('map and filter return iterators, not lists. They give each value once, only when asked. Wrap them in list() to see all the values, and do not loop over the same map object twice.', 'warn')}
''', kw=['map', 'filter', 'reduce', 'functools', 'lazy iterator', 'fold'])

K.lesson('listcomp', 'List comprehensions', f'''
{viz('pycomp')}
{run('listcomp')}
{fxs(fx('List comprehension', '[expression for item in iterable if condition]', 'Read it as: the expression, for each item, but only if the condition holds.', key=True),
     fx('With if-else', '[a if test else b for item in iterable]', 'The if-else is part of the expression, so it comes before for. A filter if comes after.', key=True))}
{note('[n for n in nums if n % 2 == 0 else 0] is a SyntaxError. An if after for only filters and has no else.', 'exam')}
''', kw=['list comprehension', 'filter in comprehension', 'if else in comprehension', 'expression'])

K.lesson('nestedcomp', 'Nested comprehensions', f'''
{run('nestedcomp')}
{note('In [v for row in matrix for v in row] the for clauses are in the same order as nested loops: outer first. A comprehension inside the expression ([[... for c] for r]) builds a list of lists. If it needs more than two for clauses, a normal loop is easier to read.', 'tip')}
''', kw=['nested comprehension', 'flatten', 'transpose', 'matrix comprehension', 'cartesian product'])

K.lesson('dictset', 'Dict and set comprehensions', f'''
{run('dictset')}
{table(['Brackets', 'Builds', 'Example'], [
    ['[ ]', 'list', '[w.upper() for w in words]'],
    ['{ } with key: value', 'dict', '{w: len(w) for w in words}'],
    ['{ } with one value', 'set', '{w[0] for w in words}'],
    ['( )', 'generator (lazy, not a tuple)', '(len(w) for w in words)']])}
''', kw=['dict comprehension', 'set comprehension', 'invert dict', 'brackets'])

K.lesson('genexp', 'Generator expressions: comprehensions without the list', f'''
{run('genexp')}
{versus('List comprehension or generator expression', ['', '[... for ...]', '(... for ...)'], [
    ['Makes', 'The whole list now', 'One value at a time, when asked'],
    ['Memory for a million items', 'Megabytes', 'A couple of hundred bytes'],
    ['Use again', 'Yes, as often as you like', 'No, once only'],
    ['Index, len, slicing', 'Yes', 'No'],
    ['Best for', 'Results you keep or reuse', 'Feeding sum, max, any, all, join, or a for loop once']],
    'when the values go straight into sum, max, any, all or "".join, use a generator expression. Advanced 2.1 shows how generators work.')}
''', kw=['generator expression', 'lazy evaluation', 'memory', 'any', 'all', 'sum'])

K.lesson('higher', 'Higher-order functions, compose and partial', f'''
{run('higher')}
{note('A <b>higher-order function</b> takes a function or returns one: sorted, map, filter, make_greeter, compose and partial are all examples. functools.partial is often clearer than a lambda that only fixes some arguments.', 'tip')}
''', kw=['higher-order function', 'compose', 'functools.partial', 'function factory', 'pipeline'])

K.lesson('versus', 'Loop, comprehension or map', f'''
{versus('Three ways to build squares of the even numbers', ['', 'for loop', 'comprehension', 'map and filter'], [
    ['Code', 'result = [] then for n in nums: if n % 2 == 0: result.append(n * n)', '[n * n for n in nums if n % 2 == 0]', 'list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, nums)))'],
    ['Lines', '4', '1', '1'],
    ['Reads like', 'Instructions', 'A sentence', 'Nested calls, inside out'],
    ['Speed in CPython', 'Slowest', 'Fast', 'Fast with built-in functions, slower with lambdas'],
    ['Good when', 'Several steps, prints, try and except in the body', 'One expression and an optional filter', 'You already have a named function: map(str.upper, words)']],
    'use a comprehension for most transformations, map with an existing function, and a loop when the body needs statements.')}
''', kw=['comprehension vs loop', 'map vs comprehension', 'readability', 'performance'])

K.lesson('maths', 'The maths behind comprehensions', f'''
{fxs(fx('Set builder notation', '{ f(x) | x &isin; S, p(x) }', 'Maths wrote "the set of f(x) for x in S where p(x)" long before Python. {f(x) for x in S if p(x)} is the same idea.', key=True),
     fx('map is f applied to each item', 'map(f, [a<sub>1</sub>, ..., a<sub>n</sub>]) = [f(a<sub>1</sub>), ..., f(a<sub>n</sub>)]', 'The length does not change.'),
     fx('reduce is a fold', 'reduce(&oplus;, [a<sub>1</sub>, a<sub>2</sub>, a<sub>3</sub>], s) = ((s &oplus; a<sub>1</sub>) &oplus; a<sub>2</sub>) &oplus; a<sub>3</sub>', 'With + this is the sum, with max it is the maximum.', key=True),
     fx('Size of a comprehension with two for clauses', '|A| &times; |B|', '[(x, y) for x in range(1, 4) for y in "ab"] has 3 &times; 2 = 6 pairs, the Cartesian product A &times; B.'),
     fx('Sum of squares', '1<sup>2</sup> + 2<sup>2</sup> + ... + n<sup>2</sup> = n(n + 1)(2n + 1)/6', 'sum(n * n for n in range(1, 11)) = 10 &times; 11 &times; 21 / 6 = 385.'))}
{steps('Worked example: what is reduce(lambda a, b: a * 10 + b, [4, 0, 7], 0)?', [
    'Start with 0.',
    '0 &times; 10 + 4 = 4.',
    '4 &times; 10 + 0 = 40.',
    eq('40 &times; 10 + 7 = 407'),
    'This fold turns a list of digits into a number.'])}
''', kw=['set builder notation', 'fold', 'Cartesian product', 'sum of squares', 'functional maths'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A lambda is a one line function. [x * 2 for x in items] builds a new list from an old one.</p>',
    '<p>Use key= with sorted, min and max. Filter in a comprehension with if after for, and choose between two values with if-else before for. Build dicts and sets the same way.</p>',
    '<p>map and filter are lazy iterators, reduce folds a list into one value, and generator expressions save memory. Use partial and compose to build functions from functions.</p>',
    '<p>Comprehensions run in their own scope (since Python 3.12 they are inlined for speed, PEP 709, but the loop name still does not leak). Lambdas capture names, not values, so callbacks made in a loop all see the last value unless you bind it with a default argument. These ideas come from the lambda calculus of Alonzo Church (1936) and from languages such as Haskell.</p>')}
{grow('Write a lambda for sorted and a simple list comprehension.',
      'Use map, filter, reduce, dict and set comprehensions and nested comprehensions.',
      'Choose between loops, comprehensions and generator expressions by memory and speed, and build pipelines with higher-order functions.')}
''', kw=['beginner', 'expert', 'PEP 709', 'lambda calculus', 'late binding'])

lc(977, 'Squares of a Sorted Array', 'squares-of-a-sorted-array', 'e', 'Comprehension and sorted', 'Square every number with a comprehension, then sort. (A two pointer version does it in O(n).)', r'''
def sorted_squares(nums):
    return sorted([x * x for x in nums])
''', [('sorted_squares([-4, -1, 0, 3, 10])', [0, 1, 9, 16, 100]), ('sorted_squares([-7, -3, 2, 3, 11])', [4, 9, 9, 49, 121])])
lc(867, 'Transpose Matrix', 'transpose-matrix', 'e', 'Nested comprehension', 'Row c of the answer is column c of the matrix.', r'''
def transpose(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    return [[matrix[r][c] for r in range(rows)] for c in range(cols)]
''', [('transpose([[1, 2, 3], [4, 5, 6], [7, 8, 9]])', [[1, 4, 7], [2, 5, 8], [3, 6, 9]]), ('transpose([[1, 2, 3], [4, 5, 6]])', [[1, 4], [2, 5], [3, 6]])])
lc(1572, 'Matrix Diagonal Sum', 'matrix-diagonal-sum', 'e', 'Generator expression with sum', 'Add mat[i][i] and mat[i][n &minus; 1 &minus; i]. When n is odd the middle cell was added twice.', r'''
def diagonal_sum(mat):
    n = len(mat)
    total = sum(mat[i][i] + mat[i][n - 1 - i] for i in range(n))
    if n % 2 == 1:
        total = total - mat[n // 2][n // 2]
    return total
''', [('diagonal_sum([[1, 2, 3], [4, 5, 6], [7, 8, 9]])', 25), ('diagonal_sum([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]])', 8), ('diagonal_sum([[5]])', 5)])
lc(2942, 'Find Words Containing Character', 'find-words-containing-character', 'e', 'Comprehension with enumerate', 'Keep the index i of every word that contains x.', r'''
def find_words_containing(words, x):
    return [i for i, word in enumerate(words) if x in word]
''', [('find_words_containing(["leet", "code"], "e")', [0, 1]), ('find_words_containing(["abc", "bcd", "aaaa", "cbc"], "a")', [0, 2]), ('find_words_containing(["abc"], "z")', [])])
lc(1748, 'Sum of Unique Elements', 'sum-of-unique-elements', 'e', 'Count, then sum with a filter', 'Count each value, then add the values whose count is 1.', r'''
def sum_of_unique(nums):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    return sum(x for x, c in counts.items() if c == 1)
''', [('sum_of_unique([1, 2, 3, 2])', 4), ('sum_of_unique([1, 1, 1, 1, 1])', 0), ('sum_of_unique([1, 2, 3, 4, 5])', 15)])
lc(1913, 'Maximum Product Difference Between Two Pairs', 'maximum-product-difference-between-two-pairs', 'e', 'sorted', 'Biggest two times each other, minus smallest two times each other.', r'''
def max_product_difference(nums):
    s = sorted(nums)
    return s[-1] * s[-2] - s[0] * s[1]
''', [('max_product_difference([5, 6, 2, 7, 4])', 34), ('max_product_difference([4, 2, 5, 9, 7, 4, 8])', 64)])
lc(1636, 'Sort Array by Increasing Frequency', 'sort-array-by-increasing-frequency', 'e', 'sorted with a tuple key', 'Sort by (count, &minus;value): rarer numbers first, and for equal counts the bigger number first.', r'''
def frequency_sort(nums):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    return sorted(nums, key=lambda x: (counts[x], -x))
''', [('frequency_sort([1, 1, 2, 2, 2, 3])', [3, 1, 1, 2, 2, 2]), ('frequency_sort([2, 3, 1, 3, 2])', [1, 3, 3, 2, 2]), ('frequency_sort([-1, 1, -6, 4, 5, -6, 1, 4, 1])', [5, -1, 4, 4, -6, -6, 1, 1, 1])])
lc(451, 'Sort Characters By Frequency', 'sort-characters-by-frequency', 'm', 'Count, sort by count, join', 'Count each letter, sort the letters by count from high to low, and repeat each one count times.', r'''
def frequency_sort_text(s):
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    order = sorted(counts, key=lambda ch: (-counts[ch], ch))
    return "".join(ch * counts[ch] for ch in order)
''', [('frequency_sort_text("tree")', 'eert'), ('frequency_sort_text("cccaaa")', 'aaaccc'), ('frequency_sort_text("Aabb")', 'bbAa')])
lc(791, 'Custom Sort String', 'custom-sort-string', 'm', 'sorted with a dict key', 'Give each letter of order its position. Letters not in order can go anywhere, here at the end.', r'''
def custom_sort_string(order, s):
    rank = {ch: i for i, ch in enumerate(order)}
    return "".join(sorted(s, key=lambda ch: rank.get(ch, len(order))))
''', [('custom_sort_string("cba", "abcd")', 'cbad'), ('custom_sort_string("bcafg", "abcd")', 'bcad')])
lc(179, 'Largest Number', 'largest-number', 'm', 'Custom comparison with cmp_to_key', 'Put a before b when a + b is bigger than b + a as text. Join, and turn "000" into "0".', r'''
from functools import cmp_to_key


def compare(a, b):
    if a + b > b + a:
        return -1
    if a + b < b + a:
        return 1
    return 0


def largest_number(nums):
    words = [str(n) for n in nums]
    words.sort(key=cmp_to_key(compare))
    result = "".join(words)
    if result[0] == "0":
        return "0"
    return result
''', [('largest_number([10, 2])', '210'), ('largest_number([3, 30, 34, 5, 9])', '9534330'), ('largest_number([0, 0])', '0')])

K.lesson('leetcode', 'LeetCode practice', leet(), kw=['LeetCode', 'comprehension', 'sorted key', 'transpose', 'frequency sort', 'largest number', 'cmp_to_key'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>lambda</b> args: expression makes a small anonymous function. Use it as an argument, use def for anything you name.',
    'sorted, min and max take <b>key=</b>, a function called once per item. Return a tuple to sort by several things.',
    '<b>map</b>(f, items) applies f to every item, <b>filter</b>(test, items) keeps the items that pass. Both are lazy. <b>reduce</b> folds a list into one value.',
    'List comprehension: [expr for x in items if test]. if-else goes before for, a filter if after it.',
    'Several for clauses run like nested loops, outer first. Comprehensions also build dicts and sets.',
    'A generator expression (expr for x in items) makes values one at a time and saves memory. It can be used once.',
    'Higher-order functions take or return functions: make_greeter, compose, functools.partial.'],
    'Step 5 is about things going wrong and working with the outside world: exceptions, modules and packages, and files.')}
{files('Three tasks: grade labels with a comprehension, top scorers with sorted and key, and a word length index with a dict comprehension.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does (lambda x: x + 1)(4) give?', ['4', '5', 'A function', 'Error'], 1, 'Called at once.', 'The lambda is called with 4 and returns 5.')
K.quiz('e', 'What is [x * 2 for x in [1, 2, 3]]?', ['[1, 2, 3, 1, 2, 3]', '[2, 4, 6]', '[1, 4, 9]', '6'], 1, 'Double each.', 'Each item is multiplied by 2.')
K.quiz('e', 'What is [x for x in range(6) if x % 2]?', ['[0, 2, 4]', '[1, 3, 5]', '[0, 1, 2, 3, 4, 5]', '[]'], 1, 'Odd numbers are truthy here.', 'x % 2 is 1 (true) for odd x.')
K.quiz('m', 'What does print(map(str, [1, 2])) show?', ["['1', '2']", 'A map object', '12', 'Error'], 1, 'Lazy.', 'map returns an iterator. Use list() to see the values.')
K.quiz('m', 'sorted(["bb", "a", "ccc"], key=len, reverse=True) gives', ['["a", "bb", "ccc"]', '["ccc", "bb", "a"]', '["bb", "a", "ccc"]', '["ccc", "a", "bb"]'], 1, 'Longest first.', 'Sorted by length, highest first.')
K.quiz('m', 'Which is valid?', ['[x if x &gt; 0 for x in a]', '[x for x in a if x &gt; 0 else 0]', '[x if x &gt; 0 else 0 for x in a]', '[for x in a: x]'], 2, 'if-else before for.', 'A conditional expression needs else and goes before for.')
K.quiz('m', 'What is {x % 3 for x in range(10)}?', ['{0, 1, 2}', '{0, 1, 2, 3}', '[0, 1, 2]', '{3}'], 0, 'A set of remainders.', 'Remainders by 3 are only 0, 1 and 2.')
K.quiz('m', 'What is [(a, b) for a in "xy" for b in "12"]?', ["[('x', '1'), ('x', '2'), ('y', '1'), ('y', '2')]", "[('x', '1'), ('y', '2')]", "[('x', '1'), ('y', '1'), ('x', '2'), ('y', '2')]", 'Error'], 0, 'The first for is the outer loop.', 'For each a, b goes through "12".')
K.quiz('h', 'g = (x * x for x in range(3)). What is sum(g) + sum(g)?', ['10', '5', '0', 'Error'], 1, 'A generator runs once.', 'The first sum is 0 + 1 + 4 = 5. The second sum gets nothing, 0.')
K.quiz('h', 'reduce(lambda a, b: a * b, [1, 2, 3, 4]) is', ['10', '24', '4', '1'], 1, 'Multiply all.', '1 &times; 2 &times; 3 &times; 4 = 24.')
K.quiz('h', 'Which can a lambda body contain?', ['A for loop', 'return x', 'x if x &gt; 0 else -x', 'y = x + 1'], 2, 'Expressions only.', 'A conditional expression is an expression. The others are statements.')
K.quiz('x', 'In the style of a Cambridge Part IA question: fs = [lambda x: x * i for i in range(3)]. What is [f(10) for f in fs]?', ['[0, 10, 20]', '[20, 20, 20]', '[0, 0, 0]', '[10, 10, 10]'], 1, 'Late binding.', 'Each lambda reads i when it is called, after the loop ended with i = 2. Write lambda x, i=i: x * i to fix it.')
K.quiz('x', 'In the style of a CMU 15-150 question: what does reduce(lambda acc, x: [x] + acc, [1, 2, 3], []) return?', ['[1, 2, 3]', '[3, 2, 1]', '[[3], [2], [1]]', '6'], 1, 'Each new x goes in front.', '[1], then [2, 1], then [3, 2, 1]: this fold reverses the list.')

K.calc('e', 'len([x for x in range(20) if x % 5 == 0])?', '4', '0, 5, 10, 15.', ['Multiples of 5 below 20.', '0, 5, 10, 15.', eq('4')], check=4)
K.calc('e', 'sum(x * x for x in range(1, 4))?', '14', '1 + 4 + 9.', ['Squares of 1, 2, 3.', '1 + 4 + 9.', eq('14')], check=14)
K.calc('e', 'max(["kiwi", "fig", "banana"], key=len)?', 'banana', 'Longest word.', ['Lengths 4, 3, 6.', 'The largest is 6.', eq('"banana"')], check='banana')
K.calc('m', 'Sum of squares from 1 to 20 with n(n + 1)(2n + 1)/6.', '2870', 'n = 20.', ['20 &times; 21 &times; 41.', '17,220 / 6.', eq('2870')], check=sum(n * n for n in range(1, 21)))
K.calc('m', 'len([(x, y) for x in range(4) for y in range(5)])?', '20', '|A| &times; |B|.', ['4 values of x.', '5 values of y each.', eq('20')], check=20)
K.calc('m', 'len([(x, y) for x in range(4) for y in range(x)])?', '6', '0 + 1 + 2 + 3.', ['y runs x times.', '0 + 1 + 2 + 3.', eq('6')], check=6)
K.calc('m', 'reduce(lambda a, b: a * 10 + b, [2, 0, 2, 6], 0)?', '2026', 'Digits to number.', ['0, 2, 20, 202.', '202 &times; 10 + 6.', eq('2026')], check=2026)
K.calc('h', 'len({w[0] for w in ["apple", "avocado", "berry", "cherry", "corn"]})?', '3', 'First letters.', ['First letters: a, a, b, c, c.', 'A set keeps a, b, c.', eq('3')], check=3)
K.calc('h', 'sum(1 for n in range(1, 101) if n % 3 == 0 or n % 5 == 0)?', '47', '33 + 20 &minus; 6.', ['Multiples of 3: 33. Of 5: 20.', 'Of 15: 6.', eq('33 + 20 &minus; 6 = 47')], check=sum(1 for n in range(1, 101) if n % 3 == 0 or n % 5 == 0))
K.calc('x', 'In the style of a Project Euler problem 6: the square of the sum minus the sum of the squares of 1 to 100.', '25164150', '(n(n + 1)/2)<sup>2</sup> &minus; n(n + 1)(2n + 1)/6.', ['Sum = 5050, squared = 25,502,500.', 'Sum of squares = 338,350.', eq('25,502,500 &minus; 338,350 = 25,164,150')], check=sum(range(101)) ** 2 - sum(n * n for n in range(101)))

K.assign('labels', 'e', 'Pass or fail labels',
         '<p>Write <code>labels(marks)</code> that returns a list with "pass" for each mark of 40 or more and "fail" for the rest, using one list comprehension.</p>',
         '''
def labels(marks):
    # your code here
    pass
''', [('labels([72, 39, 40])', ['pass', 'fail', 'pass']), ('labels([])', [])],
         '''
def labels(marks):
    return ["pass" if m >= 40 else "fail" for m in marks]
''', 'The if-else goes before for: [a if test else b for m in marks].', '<p>The same with map would be list(map(lambda m: "pass" if m &gt;= 40 else "fail", marks)), which is harder to read.</p>')
K.assign('top', 'm', 'Top scorers',
         '<p>Write <code>top_scorers(scores, k)</code>. scores is a dict from name to mark. Return the names of the k best students, best first. Equal marks go in alphabetical order.</p>',
         '''
def top_scorers(scores, k):
    # your code here
    pass
''', [('top_scorers({"Asha": 88, "Ravi": 72, "Meera": 95, "John": 88}, 3)', ['Meera', 'Asha', 'John']), ('top_scorers({"A": 1}, 5)', ['A']), ('top_scorers({}, 2)', [])],
         '''
def top_scorers(scores, k):
    order = sorted(scores, key=lambda name: (-scores[name], name))
    return order[:k]
''', 'Sort the names with key=lambda name: (-scores[name], name), then slice the first k.', '<p>Negating the mark sorts it high to low while the name still sorts A to Z. A slice past the end is safe, so k = 5 with one student just gives one name.</p>')
K.assign('index', 'm', 'Words grouped by length',
         '<p>Write <code>by_length(words)</code> that returns a dict from each word length to a sorted list of the different words with that length. Use comprehensions.</p>',
         '''
def by_length(words):
    # your code here
    pass
''', [('by_length(["fig", "kiwi", "pear", "fig", "plum", "apple"])', {3: ['fig'], 4: ['kiwi', 'pear', 'plum'], 5: ['apple']}), ('by_length([])', {})],
         '''
def by_length(words):
    unique = set(words)
    return {n: sorted(w for w in unique if len(w) == n) for n in {len(w) for w in unique}}
''', 'First make the set of lengths. Then, for each length n, a sorted generator of the words of that length.', '<p>This is short but loops over the words once per length. For big inputs the dict of lists from Core 3.4 is faster.</p>')

K.must('lambda', 'lambda args: expression. One expression, no statements. Best as an argument, def otherwise.')
K.must('key functions', 'sorted/min/max(items, key=f). Tuple keys sort by several fields. -x reverses a number key.')
K.must('map, filter, reduce', 'Lazy iterators: list(map(f, a)), list(filter(test, a)). functools.reduce(f, a, start) folds to one value.')
K.must('Comprehensions', '[expr for x in a if test], [a if t else b for x in s], {k: v for ...}, {x for ...}. Outer for first.')
K.must('Generator expressions', '(expr for x in a): lazy, one use, tiny memory. sum(x*x for x in a), any(...), all(...).')

T = K.topic(
    slug='py-functional', topic='py-functional', step=(4, 'Functions', 'py-c4', 'Write reusable code with def, every kind of argument, scope, recursion, lambda and comprehensions.', 'Intermediate'),
    title='lambda, map, filter and comprehensions', short='Lambda and comprehensions', badge='4.3', minutes=60,
    lead='Write the common jobs on collections in one clear line. Learn lambda, sorting with key, map, filter and reduce, list comprehensions with filters and if-else, nested comprehensions, dict and set comprehensions, generator expressions, and functions that make functions.',
    desc='lambda syntax and limits, lambda vs def, key functions for sorted, min and max, tuple keys, itemgetter, map, filter, reduce, lazy iterators, list comprehensions, filtering and if-else in comprehensions, nested comprehensions, flatten and transpose, dict and set comprehensions, generator expressions and memory, any and all, higher-order functions, compose, functools.partial, set builder notation and folds.',
    summary='lambda, key functions, map, filter, reduce, list, dict and set comprehensions, generator expressions, higher-order functions.',
    keywords=['lambda', 'map', 'filter', 'reduce', 'list comprehension', 'dict comprehension', 'set comprehension', 'generator expression', 'sorted key', 'functools', 'PCAP'],
    recap='<p>Pass small functions with lambda and key, transform with map or a comprehension, keep items with filter or an if, and use a generator expression when the values are used once.</p>',
    added='2026-11-07', leet=leet_items())
