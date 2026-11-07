# Advanced Python 2.2: itertools, functools and operator. Checked against the Python 3.14 documentation of the
# itertools module (including the recipes section), functools (reduce, partial, singledispatch, lru_cache), the
# operator module (itemgetter, attrgetter, methodcaller) and math.comb and math.perm. Extends PCAP-31-03 block 5
# (lambda, map, filter, closures) toward PCPP-32-101 good practice.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-itertools')
K = Kit()

K.code('endless', r'''
from itertools import count, cycle, repeat, islice

ticket = count(start=100, step=5)              # 100, 105, 110, ... for ever
print(next(ticket), next(ticket), next(ticket))

players = cycle(["Asha", "Ravi", "Meera"])     # go round and round
turns = []
for turn in range(5):
    turns.append(next(players))
print(turns)

print(list(repeat("-", 3)))
print(list(map(pow, [2, 3, 4], repeat(2))))    # repeat feeds the same value to map
print(list(zip(count(1), "abc")))              # numbering without enumerate
print(list(islice(count(), 2, 12, 3)))         # start 2, stop before 12, step 3
''')

K.code('filtering', r'''
from itertools import takewhile, dropwhile, compress, filterfalse

temps = [21, 23, 26, 31, 29, 24, 33]
print(list(takewhile(lambda t: t < 30, temps)))   # stop at the first hot day
print(list(dropwhile(lambda t: t < 30, temps)))   # skip until the first hot day
print(list(filter(lambda t: t < 30, temps)))      # check every single item
print(list(filterfalse(lambda t: t < 30, temps)))

days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
present = [1, 0, 1, 1, 0]
print(list(compress(days, present)))              # keep where the mask is true
''')

K.code('combining', r'''
from itertools import chain, zip_longest, pairwise, batched, starmap, accumulate, tee
import operator

print(list(chain([1, 2], (3, 4), "ab")))
print(list(chain.from_iterable([[1, 2], [3], []])))
print(list(zip_longest("abc", [1, 2], fillvalue="-")))
print(list(pairwise([10, 13, 19, 20])))        # neighbours: (a, b), (b, c), ...
print(list(batched(range(7), 3)))              # groups of 3 (Python 3.12 and later)
print(list(starmap(operator.mul, [(2, 5), (3, 4)])))
print(list(accumulate([3, 1, 4, 1, 5])))       # running totals
print(list(accumulate([3, 1, 4, 1, 5], max)))  # running maximum
print(list(accumulate([1, 2, 3, 4], operator.mul, initial=1)))
first, second = tee(iter([1, 2, 3]))           # two independent copies of one iterator
print(list(first), list(second))
''')

K.code('grouping', r'''
from itertools import groupby

runs = []
for key, group in groupby("aaabccdd"):
    runs.append((key, len(list(group))))
print(runs)

orders = [("tea", 10), ("coffee", 25), ("tea", 12), ("juice", 30), ("coffee", 20)]
print([name for name, group in groupby(orders, key=lambda o: o[0])])   # NOT sorted

orders.sort(key=lambda o: o[0])                # sort by the same key first
for name, group in groupby(orders, key=lambda o: o[0]):
    amounts = [amount for item, amount in group]
    print(name, amounts, sum(amounts))
''')

K.code('combos', long=True, src=r'''
from itertools import product, permutations, combinations, combinations_with_replacement
import math

items = "ABC"
print(["".join(t) for t in product(items, repeat=2)])
print(["".join(t) for t in permutations(items, 2)])
print(["".join(t) for t in combinations(items, 2)])
print(["".join(t) for t in combinations_with_replacement(items, 2)])
print(3 ** 2, math.perm(3, 2), math.comb(3, 2), math.comb(3 + 2 - 1, 2))

sizes = ["S", "M"]
colours = ["red", "blue", "black"]
shirts = list(product(sizes, colours))         # replaces two nested for loops
print(len(shirts), shirts[:2])

pins = 0
for p in product("0123456789", repeat=4):
    if len(set(p)) == 4:                       # no digit used twice
        pins += 1
print(pins, math.perm(10, 4))
''')

K.code('functools_demo', r'''
from functools import reduce, partial, singledispatch, lru_cache
import operator

print(reduce(operator.add, [1, 2, 3, 4]))      # ((1 + 2) + 3) + 4
print(reduce(lambda total, word: total + len(word), ["hi", "you"], 0))
print(reduce(max, [3, 9, 2]))


def power(base, exponent):
    return base ** exponent


square = partial(power, exponent=2)            # fix one argument, get a new function
cube = partial(power, exponent=3)
print(square(5), cube(2), square.func.__name__, square.keywords)
from_binary = partial(int, base=2)
print(from_binary("1011"))


@singledispatch                                # choose a version by the type of the first argument
def describe(value):
    return "something"


@describe.register
def _(value: int):
    return "an int, " + str(value * 2) + " when doubled"


@describe.register
def _(value: list):
    return "a list of " + str(len(value))


print(describe(21), "|", describe([1, 2]), "|", describe(2.5))


@lru_cache(maxsize=2)
def slow_square(n):
    return n * n


for n in [1, 2, 1, 3, 1]:
    slow_square(n)
print(slow_square.cache_info())
''')

K.code('operators', r'''
from operator import itemgetter, attrgetter, methodcaller
from dataclasses import dataclass

rows = [("Asha", 30, "Pune"), ("Ravi", 25, "Delhi"), ("Meera", 30, "Agra")]
print(sorted(rows, key=itemgetter(1, 0)))      # by age, then by name
name_and_city = itemgetter(0, 2)
print([name_and_city(r) for r in rows])


@dataclass
class Book:
    title: str
    pages: int


books = [Book("Python", 320), Book("Maths", 210)]
print([b.title for b in sorted(books, key=attrgetter("pages"))])
shout = methodcaller("upper")
print(list(map(shout, ["hi", "ok"])))
''')

K.code('recipes', r'''
from collections import deque
from itertools import islice, chain


def sliding_window(iterable, n):
    it = iter(iterable)
    window = deque(islice(it, n - 1), maxlen=n)
    for x in it:
        window.append(x)                       # the oldest value drops off the left
        yield tuple(window)


def unique_everseen(iterable):
    seen = set()
    for item in iterable:
        if item not in seen:
            seen.add(item)
            yield item


def first_true(iterable, default=None, pred=None):
    return next(filter(pred, iterable), default)


print(list(sliding_window([1, 2, 3, 4, 5], 3)))
print(list(unique_everseen("abracadabra")))
print(first_true([0, "", 7, 9]), first_true([0, 0], default="none"))
print(list(chain.from_iterable(zip("abc", "123"))))
''')

K.lesson('idea', 'The iterator toolbox', f'''
{src('Python 3.14 documentation of itertools (with its recipes), functools, operator, math.comb and math.perm.')}
{wwh('<b>itertools</b> is a module of fast building blocks that take iterators and give back new iterators: endless counters, slicing, joining, grouping and every kind of combination. <b>functools</b> has tools that work on functions: reduce, partial, singledispatch and caches. <b>operator</b> gives the + , [ ] and . operators as ready made functions.',
     'Loops that join lists, number items, group rows, try every pair or keep a running total are written again and again, and each hand written loop is a chance for an off by one bug. These modules are tested, written in C, lazy (they keep memory small) and they make the intention clear: product(sizes, colours) says more than two nested loops.',
     'Each itertools function returns an iterator, so the tools snap together: chain them, slice them with islice, feed them to sum or list. functools.partial fixes some arguments of a function, reduce folds a list into one value, and singledispatch picks a version of a function by the type of its argument.')}
{viz('pycombo')}
{run('endless')}
{note('count, cycle and repeat never end on their own. Always stop them: with islice, zip with something finite, takewhile, or a break.', 'warn')}
''', kw=['itertools', 'functools', 'operator', 'count', 'cycle', 'repeat', 'islice', 'lazy'])

K.lesson('filtering', 'Taking and dropping items', f'''
{run('filtering')}
{versus('Picking items from a sequence', ['', 'filter', 'takewhile', 'dropwhile', 'compress'], [
    ['Looks at', 'Every item', 'Items until the test first fails', 'Items until the test first fails', 'Each item and its mask value'],
    ['Keeps', 'Items that pass', 'The front part that passes', 'Everything from the first failure on', 'Items where the mask is true'],
    ['Works on endless input', 'Yes, but never finishes', 'Yes, it stops by itself', 'Yes', 'Yes'],
    ['Typical use', 'Clean a list', 'Read until a blank line', 'Skip a header', 'Apply a yes or no column']],
    'use takewhile when the data is sorted or a stop signal exists. It can stop early, which filter never does.')}
''', kw=['takewhile', 'dropwhile', 'filter', 'filterfalse', 'compress', 'islice'])

K.lesson('combining', 'Joining, pairing and running totals', f'''
{run('combining')}
{table(['Tool', 'What it gives', 'Instead of'], [
    ['chain(a, b, c)', 'All items of a, then b, then c', 'a + b + c, which builds new lists'],
    ['chain.from_iterable(lists)', 'Flattens one level', 'A nested loop'],
    ['zip_longest(a, b, fillvalue=x)', 'Pairs until the LONGEST input ends', 'zip, which stops at the shortest'],
    ['pairwise(xs)', 'Each item with the next one', 'zip(xs, xs[1:])'],
    ['batched(xs, n)', 'Tuples of n items, the last may be shorter', 'Slicing by hand'],
    ['starmap(f, pairs)', 'f(*pair) for each pair', 'A lambda that unpacks'],
    ['accumulate(xs, f, initial=)', 'Running results of f (sum by default)', 'A loop with a total variable'],
    ['tee(it, n)', 'n independent iterators from one', 'list(it), when the data is small']])}
{note('tee keeps every value that one copy has seen and the other has not, so if one copy runs far ahead it can use as much memory as a list. Use it when both copies move at a similar pace.', 'tip')}
''', kw=['chain', 'from_iterable', 'zip_longest', 'pairwise', 'batched', 'starmap', 'accumulate', 'tee', 'prefix sum'])

K.lesson('grouping', 'groupby: runs of equal keys', f'''
{run('grouping')}
{note('groupby only joins items that are NEXT to each other. On unsorted data tea appeared twice. Sort by the same key first, or use a dict (collections.defaultdict(list)) when you cannot sort.', 'warn')}
{versus('Grouping rows', ['', 'sorted then groupby', 'a dict of lists', 'collections.Counter'], [
    ['Needs sorted data', 'Yes', 'No', 'No'],
    ['Memory', 'One group at a time', 'All groups at once', 'One count per key'],
    ['Keeps runs (aaa then b then aa)', 'Yes, on unsorted data', 'No', 'No'],
    ['Best for', 'Run length encoding and data that is already sorted', 'General grouping', 'Counting only']],
    'groupby is perfect for runs and for data that already comes sorted (from a database ORDER BY). Otherwise a dict is simpler.')}
''', kw=['groupby', 'run length', 'sort first', 'defaultdict', 'Counter'])

K.lesson('combos', 'Combinations and permutations', f'''
{run('combos')}
{versus('Trying every choice', ['', 'nested for loops', 'itertools', 'math.comb and math.perm'], [
    ['Number of choices fixed in the code', 'Yes, one loop each', 'No, repeat=r or r is a variable', 'Not needed'],
    ['Gives the actual tuples', 'Yes', 'Yes, lazily', 'No, only the count'],
    ['Speed', 'Python speed', 'C speed', 'Instant'],
    ['Use when', 'Two or three simple loops', 'You need the tuples', 'You only need how many']],
    'count with math.comb or math.perm before you generate. 10 items in every order is 3,628,800 tuples, and 20 items is far too many to ever list.')}
''', kw=['product', 'permutations', 'combinations', 'combinations_with_replacement', 'math.comb', 'math.perm', 'brute force'])

K.lesson('functools', 'functools: reduce, partial, singledispatch and caches', f'''
{run('functools_demo')}
{versus('Making a simpler version of a function', ['', 'partial(power, exponent=2)', 'lambda b: power(b, 2)', 'def square(b)'], [
    ['Code', 'Short', 'Short', 'Longest'],
    ['Shows what it wraps', 'Yes: .func, .args, .keywords', 'No', 'No'],
    ['Can be pickled and sent to another process', 'Yes', 'No', 'Yes'],
    ['Has its own docstring and name', 'No', 'No', 'Yes']],
    'use partial for quick "fix this argument" versions, above all for callbacks and multiprocessing. Write a def when it deserves a name and a docstring.')}
{note('singledispatch chose the int version for 21, the list version for [1, 2] and the base version for 2.5. It looks at the type of the FIRST argument only. For methods use functools.singledispatchmethod.', 'exam')}
{note('lru_cache(maxsize=2) keeps the 2 most recently used answers. Calling 1, 2, 1, 3, 1 gave 2 hits: when 3 arrived, 2 was the least recently used and was thrown away.', 'tip')}
''', kw=['reduce', 'partial', 'singledispatch', 'lru_cache', 'cache_info', 'fold'])

K.lesson('operators', 'operator: itemgetter, attrgetter, methodcaller', f'''
{run('operators')}
{versus('A key function for sorting', ['', 'lambda r: (r[1], r[0])', 'itemgetter(1, 0)'], [
    ['Readable', 'Yes', 'Yes, once you know it'],
    ['Speed', 'Python function call', 'Faster, written in C'],
    ['Works with attributes', 'Yes', 'Use attrgetter("pages")'],
    ['Can be pickled', 'No', 'Yes']],
    'both are fine. itemgetter and attrgetter are a little faster and say clearly "sort by these fields".')}
''', kw=['itemgetter', 'attrgetter', 'methodcaller', 'operator.add', 'operator.mul', 'sort key'])

K.lesson('recipes', 'Recipes built from the tools', f'''
{run('recipes')}
{note('The itertools documentation ends with a long list of recipes like these: sliding_window, unique_everseen, first_true, roundrobin, partition and more. The third party package more-itertools has all of them ready to install with pip.', 'tip')}
''', kw=['recipes', 'sliding_window', 'deque', 'unique_everseen', 'first_true', 'more-itertools'])

K.lesson('maths', 'The maths: counting, prefix sums and folds', f'''
{fxs(fx('product(items, repeat=r)', 'n<sup>r</sup>', '3 items, r = 2: 3<sup>2</sup> = 9 tuples.', key=True),
     fx('permutations(items, r)', 'P(n, r) = n! / (n &minus; r)!', '4 items, r = 2: 24 / 2 = 12.', key=True),
     fx('combinations(items, r)', 'C(n, r) = n! / (r! (n &minus; r)!)', '4 items, r = 2: 24 / (2 &times; 2) = 6.', key=True),
     fx('combinations_with_replacement(items, r)', 'C(n + r &minus; 1, r)', '3 items, r = 2: C(4, 2) = 6.'),
     fx("Pascal's rule", 'C(n, r) = C(n &minus; 1, r &minus; 1) + C(n &minus; 1, r)', 'C(4, 2) = C(3, 1) + C(3, 2) = 3 + 3 = 6: tuples with the first item, plus tuples without it.'),
     fx('Prefix sums with accumulate', 'P = accumulate(a, initial=0), sum of a[i] to a[j] = P[j + 1] &minus; P[i]', 'a = [3, 1, 4, 1, 5], P = [0, 3, 4, 8, 9, 14], a[1] + a[2] + a[3] = 9 &minus; 3 = 6.', key=True),
     fx('reduce is a left fold', 'reduce(f, [a, b, c]) = f(f(a, b), c)', 'reduce(operator.sub, [10, 3, 2]) = (10 &minus; 3) &minus; 2 = 5.'))}
{steps('Worked example: 4 digit PINs with no digit used twice', [
    'The first digit has 10 choices.',
    'The second has 9 left, the third 8 and the fourth 7.',
    'This is P(10, 4) = 10! / 6!.',
    eq('10 &times; 9 &times; 8 &times; 7 = 5040, the same as the brute force count')])}
''', kw=['permutations formula', 'combinations formula', 'stars and bars', "Pascal's rule", 'prefix sum', 'left fold'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Use count, cycle, repeat and islice, chain lists together and keep running totals with accumulate.</p>',
    '<p>Use product, permutations and combinations, group with sorted then groupby, and sort with itemgetter and attrgetter.</p>',
    '<p>Use partial, reduce, singledispatch and lru_cache, and build your own tools such as sliding_window from the recipes.</p>',
    '<p>Know the costs: combinatoric tools grow like n<sup>r</sup> or n!, tee buffers the gap between its copies, groupby shares one underlying iterator so each group must be used before the next. Choose between generating and counting with math.comb, and use prefix sums to answer range queries in O(1).</p>')}
{grow('Use the endless and joining tools.', 'Group, combine and sort with key functions.', 'Build recipes and reason about their cost.')}
''', kw=['beginner', 'expert', 'complexity', 'tee memory'])

PLAY = '''

def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results
'''

lc(303, 'Range Sum Query - Immutable', 'range-sum-query-immutable', 'e', 'Prefix sums with accumulate', 'Build P = accumulate(nums, initial=0) once. Then the sum from left to right is P[right + 1] &minus; P[left], one subtraction per query.', r'''
from itertools import accumulate


class NumArray:
    def __init__(self, nums):
        self.prefix = list(accumulate(nums, initial=0))

    def sumRange(self, left, right):
        return self.prefix[right + 1] - self.prefix[left]
''' + PLAY, [('play(NumArray, ["NumArray", "sumRange", "sumRange", "sumRange"], [[[-2, 0, 3, -5, 2, -1]], [0, 2], [2, 5], [0, 5]])', [None, 1, -1, -3])])
lc(1732, 'Find the Highest Altitude', 'find-the-highest-altitude', 'e', 'Running totals, then max', 'The altitudes are the running totals of gain starting from 0, which is accumulate(gain, initial=0).', r'''
from itertools import accumulate


def largest_altitude(gain):
    return max(accumulate(gain, initial=0))
''', [('largest_altitude([-5, 1, 5, 0, -7])', 1), ('largest_altitude([-4, -3, -2, -1, 4, 3, 2])', 0)])
lc(1310, 'XOR Queries of a Subarray', 'xor-queries-of-a-subarray', 'm', 'Prefix XOR with accumulate', 'XOR works like a sum that undoes itself: P[r + 1] ^ P[l] is the XOR of arr[l] to arr[r].', r'''
from itertools import accumulate
import operator


def xor_queries(arr, queries):
    prefix = list(accumulate(arr, operator.xor, initial=0))
    answers = []
    for left, right in queries:
        answers.append(prefix[right + 1] ^ prefix[left])
    return answers
''', [('xor_queries([1, 3, 4, 8], [[0, 1], [1, 2], [0, 3], [3, 3]])', [2, 7, 14, 8])])
lc(1313, 'Decompress Run-Length Encoded List', 'decompress-run-length-encoded-list', 'e', 'batched, repeat and chain', 'Read the list two numbers at a time with batched. Each pair (freq, val) becomes repeat(val, freq). chain joins them.', r'''
from itertools import batched, chain, repeat


def decompress_rle_list(nums):
    parts = []
    for freq, val in batched(nums, 2):
        parts.append(repeat(val, freq))
    return list(chain.from_iterable(parts))
''', [('decompress_rle_list([1, 2, 3, 4])', [2, 4, 4, 4]), ('decompress_rle_list([1, 1, 2, 3])', [1, 3, 3])])
lc(443, 'String Compression', 'string-compression', 'm', 'groupby gives the runs', 'Each run of the same letter becomes the letter plus its count (only if the count is above 1). Write the result back into chars and return its length.', r'''
from itertools import groupby


def compress_chars(chars):
    result = []
    for letter, group in groupby(chars):
        size = len(list(group))
        result.append(letter)
        if size > 1:
            result.extend(str(size))
    chars[:] = result
    return len(result)
''', [('(lambda c: (compress_chars(c), c))(list("aabbccc"))', [6, ['a', '2', 'b', '2', 'c', '3']]), ('(lambda c: (compress_chars(c), c))(list("abbbbbbbbbbbb"))', [4, ['a', 'b', '1', '2']])])
lc(1446, 'Consecutive Characters', 'consecutive-characters', 'e', 'Longest run with groupby', 'groupby splits the text into runs of one letter. The answer is the length of the longest run.', r'''
from itertools import groupby


def max_power(s):
    best = 0
    for letter, group in groupby(s):
        best = max(best, len(list(group)))
    return best
''', [('max_power("leetcode")', 2), ('max_power("abbcccddddeeeeedcba")', 5)])
lc(830, 'Positions of Large Groups', 'positions-of-large-groups', 'e', 'groupby over enumerate', 'Group (index, letter) pairs by the letter. The first and last index of each group give its interval. Keep groups of 3 or more.', r'''
from itertools import groupby


def large_group_positions(s):
    result = []
    for letter, group in groupby(enumerate(s), key=lambda pair: pair[1]):
        positions = [index for index, ch in group]
        if len(positions) >= 3:
            result.append([positions[0], positions[-1]])
    return result
''', [('large_group_positions("abbxxxxzzy")', [[3, 6]]), ('large_group_positions("abcdddeeeeaabbbcd")', [[3, 5], [6, 9], [12, 14]])])
lc(784, 'Letter Case Permutation', 'letter-case-permutation', 'm', 'product of choices per character', 'A letter has two choices (lower, upper), a digit has one. product of all the choices gives every string.', r'''
from itertools import product


def letter_case_permutation(s):
    choices = []
    for ch in s:
        if ch.isalpha():
            choices.append((ch.lower(), ch.upper()))
        else:
            choices.append((ch,))
    return ["".join(t) for t in product(*choices)]
''', [('sorted(letter_case_permutation("a1b2"))', ['A1B2', 'A1b2', 'a1B2', 'a1b2']), ('letter_case_permutation("3z4")', ['3z4', '3Z4'])])
lc(47, 'Permutations II', 'permutations-ii', 'm', 'permutations, then remove repeats', 'permutations treats equal numbers as different positions, so it repeats some orders. A set removes the repeats. Fine for small inputs, backtracking with a counter is faster.', r'''
from itertools import permutations


def permute_unique(nums):
    return [list(p) for p in sorted(set(permutations(nums)))]
''', [('permute_unique([1, 1, 2])', [[1, 1, 2], [1, 2, 1], [2, 1, 1]]), ('len(permute_unique([1, 2, 3]))', 6)])
lc(1588, 'Sum of All Odd Length Subarrays', 'sum-of-all-odd-length-subarrays', 'e', 'Prefix sums, then every odd window', 'With prefix sums each subarray sum is one subtraction. Try every start and every odd length.', r'''
from itertools import accumulate


def sum_odd_length_subarrays(arr):
    prefix = list(accumulate(arr, initial=0))
    total = 0
    for start in range(len(arr)):
        for end in range(start + 1, len(arr) + 1, 2):
            total += prefix[end] - prefix[start]
    return total
''', [('sum_odd_length_subarrays([1, 4, 2, 5, 3])', 58), ('sum_odd_length_subarrays([1, 2])', 3)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Four problems are prefix sums with accumulate, three are runs found with groupby, two are generated with product and permutations, and one uses batched, repeat and chain together.</p>'), kw=['LeetCode', 'accumulate', 'prefix sum', 'groupby', 'product', 'permutations'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'count, cycle and repeat are endless: stop them with islice, zip or takewhile.',
    'takewhile and dropwhile cut a sequence at the first failure. filter and compress check every item.',
    'chain joins, zip_longest pairs to the longest, pairwise gives neighbours, batched gives groups, accumulate gives running results.',
    'groupby joins only neighbours with equal keys, so sort by the same key first.',
    'product n<sup>r</sup>, permutations n!/(n &minus; r)!, combinations C(n, r), with replacement C(n + r &minus; 1, r). Count first with math.comb and math.perm.',
    'functools: reduce folds left, partial fixes arguments, singledispatch picks by type, lru_cache keeps recent answers.',
    'operator: itemgetter, attrgetter and methodcaller are fast, clear key functions.'],
    '2.3 covers context managers and the with statement.')}
{files('Three tasks: run length encoding with groupby, a moving average over any iterable, and a value formatter with singledispatch.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does list(islice(count(5), 3)) give?', ['[5, 6, 7]', '[0, 1, 2]', '[5, 5, 5]', 'It never ends'], 0, 'count starts at 5.', 'islice takes the first 3 values of 5, 6, 7, ...')
K.quiz('e', 'How many tuples does permutations("ABC", 2) give?', ['3', '6', '9', '8'], 1, 'Order matters.', '3 &times; 2 = 6.')
K.quiz('e', 'What does list(accumulate([1, 2, 3])) show?', ['[1, 2, 3]', '[1, 3, 6]', '[6]', '[0, 1, 3, 6]'], 1, 'Running totals.', '1, then 1 + 2, then 1 + 2 + 3.')
K.quiz('m', 'Why can groupby("aabaa") give a key "a" twice?', ['It is a bug', 'groupby only joins neighbours with the same key', 'It counts letters', 'It sorts first'], 1, 'Runs.', 'The two runs of a are separated by b.')
K.quiz('m', 'What is the difference between takewhile and filter with the same test?', ['None', 'takewhile stops at the first failing item, filter checks every item', 'filter is lazy, takewhile is not', 'takewhile returns a list'], 1, 'Stopping.', 'takewhile ends the moment the test fails.')
K.quiz('m', 'square = partial(power, exponent=2). What is square(5) when power(b, e) returns b ** e?', ['10', '25', '32', 'An error'], 1, 'exponent is fixed.', 'square(5) is power(5, exponent=2) = 25.')
K.quiz('m', 'What does zip_longest("ab", [1, 2, 3], fillvalue=0) give as its last tuple?', ["('b', 2)", '(0, 3)', "('b', 3)", "(None, 3)"], 1, 'Fill the short one.', 'The string runs out first, so its place is filled with 0.')
K.quiz('m', 'sorted(rows, key=itemgetter(1, 0)) sorts by what?', ['Column 0 then 1', 'Column 1, then column 0 for ties', 'Only column 1', 'Length'], 1, 'Tuple keys.', 'itemgetter(1, 0) returns (row[1], row[0]).')
K.quiz('h', 'With @lru_cache(maxsize=2), calls go 1, 2, 3, 1. How many hits?', ['1', '0', '2', '3'], 1, 'Least recently used is evicted.', 'When 3 arrives, 1 is the least recently used and is dropped, so the last 1 is a miss.')
K.quiz('h', 'What does reduce(operator.sub, [10, 3, 2]) return?', ['5', '9', '-5', '15'], 0, 'Left fold.', '(10 &minus; 3) &minus; 2 = 5.')
K.quiz('h', 'singledispatch has versions for object (the base), int and list. Which is used for True?', ['object', 'int, because bool is a subclass of int', 'list', 'An error'], 1, 'Closest type in the MRO.', 'bool inherits from int, and no bool version was registered.')
K.quiz('x', 'In the style of a Harvard CS 124 exam: you need the number of 5 card hands from 52 cards. What is best?', ['len(list(combinations(range(52), 5)))', 'math.comb(52, 5)', 'A loop over product(range(52), repeat=5)', 'math.perm(52, 5)'], 1, 'Count, do not list.', 'math.comb gives 2,598,960 at once. Listing them is slow and product would even count orders and repeats.')
K.quiz('x', 'In the style of a Caltech CS 1 exam: a, b = tee(it). You read all of a first, then b. How much memory does tee use at most?', ['Constant', 'All values of it, because b has not seen any of them', 'Only the last value', 'None'], 1, 'tee buffers the gap.', 'Values seen by a but not yet by b are stored, which here is everything.')

K.calc('e', 'How many tuples does product("ABC", repeat=2) give?', '9', 'n<sup>r</sup>.', ['n = 3 items.', 'r = 2 places.', eq('3<sup>2</sup> = 9')], check=3 ** 2)
K.calc('e', 'How many tuples does permutations("ABCD", 2) give?', '12', 'n! / (n &minus; r)!.', ['4! = 24.', '(4 &minus; 2)! = 2.', eq('24 / 2 = 12')], check=12)
K.calc('e', 'What is the last value of accumulate([3, 1, 4, 1, 5])?', '14', 'The full sum.', ['Running totals: 3, 4, 8, 9.', 'Add the last 5.', eq('14')], check=sum([3, 1, 4, 1, 5]))
K.calc('m', 'How many tuples does combinations(range(6), 3) give?', '20', 'C(6, 3).', ['6! = 720.', '3! &times; 3! = 36.', eq('720 / 36 = 20')], check=20)
K.calc('m', 'How many tuples does combinations_with_replacement("ABC", 2) give?', '6', 'C(n + r &minus; 1, r).', ['n + r &minus; 1 = 4.', 'C(4, 2) = 4! / (2! &times; 2!).', eq('24 / 4 = 6')], check=6)
K.calc('m', 'How many groups does groupby("aaabccdd") make?', '4', 'Count the runs.', ['aaa is one run.', 'b, cc and dd are three more.', eq('4')], check=4)
K.calc('m', 'a = [3, 1, 4, 1, 5] and P = list(accumulate(a, initial=0)). What is P[4] &minus; P[1]?', '6', 'The sum of a[1] to a[3].', ['P = [0, 3, 4, 8, 9, 14].', 'P[4] = 9 and P[1] = 3.', eq('9 &minus; 3 = 6')], check=9 - 3)
K.calc('h', 'How many 4 digit PINs use no digit twice?', '5040', 'P(10, 4).', ['10 choices, then 9.', 'Then 8, then 7.', eq('10 &times; 9 &times; 8 &times; 7 = 5040')], check=10 * 9 * 8 * 7)
K.calc('h', 'What does reduce(lambda acc, d: acc * 10 + d, [4, 0, 2]) return?', '402', 'Build the number digit by digit.', ['4 &times; 10 + 0 = 40.', '40 &times; 10 + 2 = 402.', eq('402')], check=(4 * 10 + 0) * 10 + 2)
K.calc('x', 'In the style of a Harvard Stat 110 problem: how many ways can you choose 3 scoops from 5 flavours if a flavour may repeat and order does not matter?', '35', 'Stars and bars: C(n + r &minus; 1, r).', ['n = 5, r = 3, so n + r &minus; 1 = 7.', 'C(7, 3) = 7! / (3! &times; 4!).', eq('5040 / 144 = 35')], check=35)

K.assign('rle', 'e', 'Run length encoding with groupby',
         '<p>Write <code>encode(text)</code> that returns a list of (letter, count) tuples for each run, and <code>decode(pairs)</code> that turns such a list back into text. Use groupby for encode.</p>',
         '''
from itertools import groupby


def encode(text):
    pass


def decode(pairs):
    pass
''', [('encode("aaabcc")', [['a', 3], ['b', 1], ['c', 2]]), ('encode("")', []), ('decode([("x", 2), ("y", 1)])', 'xxy'), ('decode(encode("hello"))', 'hello')],
         '''
from itertools import groupby


def encode(text):
    pairs = []
    for letter, group in groupby(text):
        pairs.append((letter, len(list(group))))
    return pairs


def decode(pairs):
    text = ""
    for letter, count in pairs:
        text = text + letter * count
    return text
''', 'groupby(text) gives (letter, group). len(list(group)) is the run length. decode repeats each letter count times.', '<p>groupby is exactly the right tool here because run length encoding is about neighbours, not totals.</p>')
K.assign('moving', 'm', 'A moving average over any iterable',
         '<p>Write <code>moving_average(values, k)</code> that returns the average of every window of k neighbouring values, each rounded to 2 places. values may be any iterable, even a generator, so loop over it only once. If there are fewer than k values, return [].</p>',
         '''
from collections import deque


def moving_average(values, k):
    values = list(values)
    return [round(sum(values) / k, 2)]
''', [('moving_average([1, 2, 3, 4, 5], 3)', [2.0, 3.0, 4.0]), ('moving_average(iter([10, 20]), 3)', []), ('moving_average((x for x in [2, 4, 6, 8]), 2)', [3.0, 5.0, 7.0]), ('moving_average([5], 1)', [5.0])],
         '''
from collections import deque


def moving_average(values, k):
    window = deque(maxlen=k)
    total = 0
    result = []
    for value in values:
        if len(window) == k:
            total -= window[0]                 # the oldest value is about to drop off
        window.append(value)
        total += value
        if len(window) == k:
            result.append(round(total / k, 2))
    return result
''', 'Keep a deque(maxlen=k) and a running total. Before adding when full, subtract the value that will drop off.', '<p>The running total makes each step O(1), so the whole job is O(n) even for a big k, instead of summing k values every time.</p>')
K.assign('formatter', 'h', 'A value formatter with singledispatch',
         '<p>Write <code>fmt(value)</code> with functools.singledispatch: int gives thousands commas ("1,234"), float gives 2 decimal places ("3.14"), bool gives "yes" or "no", str gives the text in double quotes, list gives "[" + the items formatted and joined by ", " + "]", dict gives "{" + "key: value" pairs sorted by key, joined by ", " + "}" (keys as plain text, values formatted), and anything else gives "?".</p>',
         '''
from functools import singledispatch


def fmt(value):
    return str(value)
''', [('fmt(1234567)', '1,234,567'), ('fmt(3.14159)', '3.14'), ('fmt([1, 2.5, "a"])', '[1, 2.50, "a"]'), ('fmt({"b": 2, "a": True})', '{a: yes, b: 2}'), ('fmt(None)', '?')],
         '''
from functools import singledispatch


@singledispatch
def fmt(value):
    return "?"


@fmt.register
def _(value: int):
    return format(value, ",")


@fmt.register
def _(value: bool):
    return "yes" if value else "no"


@fmt.register
def _(value: float):
    return format(value, ".2f")


@fmt.register
def _(value: str):
    return '"' + value + '"'


@fmt.register
def _(value: list):
    parts = []
    for item in value:
        parts.append(fmt(item))
    return "[" + ", ".join(parts) + "]"


@fmt.register
def _(value: dict):
    parts = []
    for key in sorted(value):
        parts.append(str(key) + ": " + fmt(value[key]))
    return "{" + ", ".join(parts) + "}"
''', 'Decorate a base fmt with @singledispatch that returns "?", then register one version per type. list and dict call fmt again for their items.', '<p>bool needs its own version: without it True would use the int version and print 1. singledispatch picks the closest class in the MRO, and bool is closer than int.</p>')

K.must('Endless and slicing', 'count, cycle, repeat never stop: use islice, zip, takewhile. takewhile/dropwhile cut at the first failure. compress applies a mask.')
K.must('Joining', 'chain, chain.from_iterable, zip_longest(fillvalue=), pairwise, batched, starmap, accumulate(func, initial=), tee.')
K.must('groupby', 'Joins neighbours with equal keys only. Sort by the same key first. Use each group before moving on.')
K.must('Combinatorics', 'product n**r, permutations n!/(n-r)!, combinations C(n,r), with replacement C(n+r-1,r). math.comb and math.perm count without listing.')
K.must('functools and operator', 'reduce (left fold), partial, singledispatch, lru_cache and cache_info. itemgetter, attrgetter, methodcaller as key functions.')

T = K.topic(
    slug='py-itertools', topic='py-itertools', step=(2, 'Iterators, generators and context managers', 'py-a2', 'Work with data one value at a time, use the itertools and functools toolbox, and manage resources safely with with.', 'Advanced'),
    title='itertools, functools and operator', short='itertools and functools', badge='2.2', minutes=75,
    lead='Use the standard toolbox for iterators and functions. Learn endless counters, taking and dropping items, chain, zip_longest, pairwise, batched, accumulate and tee, groupby, product, permutations and combinations with their formulas, reduce, partial, singledispatch, lru_cache and the operator module.',
    desc='count, cycle, repeat, islice, takewhile, dropwhile, filterfalse, compress, chain, chain.from_iterable, zip_longest, pairwise, batched, starmap, accumulate, tee, groupby, product, permutations, combinations, combinations_with_replacement, math.comb and math.perm, prefix sums, functools.reduce, partial, singledispatch, lru_cache and cache_info, operator.itemgetter, attrgetter, methodcaller, itertools recipes.',
    summary='endless iterators, slicing, joining, groupby, combinatorics with formulas, reduce, partial, singledispatch, operator.',
    keywords=['itertools', 'functools', 'operator', 'groupby', 'product', 'permutations', 'combinations', 'accumulate', 'partial', 'reduce', 'singledispatch', 'itemgetter'],
    recap='<p>Snap small tested tools together instead of writing loops by hand, and count before you generate.</p>',
    added='2026-11-07', leet=leet_items())
