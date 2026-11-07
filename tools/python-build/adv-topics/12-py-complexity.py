# Advanced Python 4.1: complexity, timing and profiling. Checked against the Python 3.14 documentation of timeit,
# cProfile and pstats, tracemalloc, sys.getsizeof and functools.lru_cache, and the TimeComplexity page of the
# Python wiki for the cost of list, dict, set and deque operations. The timeit and cProfile terminal outputs below
# are real runs with CPython 3.14 (your times will differ, the shape will not).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items, show, term

chapter('py-complexity')
K = Kit()

K.code('counting', r'''
def linear_search(items, target):
    steps = 0
    for item in items:
        steps += 1
        if item == target:
            break
    return steps


def binary_search(items, target):
    steps = 0
    low = 0
    high = len(items) - 1
    while low <= high:
        steps += 1
        middle = (low + high) // 2
        if items[middle] == target:
            break
        if items[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return steps


def count_pairs(items):
    steps = 0
    for a in items:
        for b in items:
            steps += 1
    return steps


print("n      linear  binary  pairs")
for n in [10, 100, 1000]:
    data = list(range(n))
    target = n - 1                             # the last item: the worst case for linear search
    print(f"{n:<6} {linear_search(data, target):<7} {binary_search(data, target):<7} {count_pairs(data)}")
''', long=True)

K.code('timing', r'''
import timeit

numbers = list(range(100_000))
number_set = set(numbers)

list_time = timeit.timeit(lambda: 99_999 in numbers, number=200)
set_time = timeit.timeit(lambda: 99_999 in number_set, number=200)
print("set lookup is faster:", set_time < list_time)
print("more than 100 times faster:", list_time > 100 * set_time)

# repeat() runs the whole test several times. Keep the smallest time: it has the least noise.
times = timeit.repeat("sum(range(1000))", repeat=5, number=1000)
print("timings:", len(times))
best = min(times)
print("best per call is under 1 second:", best / 1000 < 1)
''', long=True)

K.code('profiling', r'''
import cProfile
import pstats


def slow_unique(items):
    result = []
    for item in items:
        if item not in result:                 # a list search inside a loop: O(n * k)
            result.append(item)
    return result


def fast_unique(items):
    return list(dict.fromkeys(items))          # one dict lookup per item: O(n)


def main():
    data = [i % 500 for i in range(5000)]
    return slow_unique(data) == fast_unique(data)


profiler = cProfile.Profile()
profiler.enable()
same = main()
profiler.disable()
print("same answer:", same)

stats = pstats.Stats(profiler)
rows = []
for (filename, line, name), (cc, ncalls, tottime, cumtime, callers) in stats.stats.items():
    if name in ("main", "slow_unique", "fast_unique"):
        rows.append((cumtime, name, ncalls))
rows.sort(reverse=True)
for cumtime, name, ncalls in rows:
    print(f"{name:<12} called {ncalls} time")
print("the slow part is", rows[1][1])
''', long=True)

K.code('memory', r'''
import sys
import tracemalloc

squares_list = [n * n for n in range(100_000)]
squares_gen = (n * n for n in range(100_000))
print("the list is over 100 KB:", sys.getsizeof(squares_list) > 100_000)
print("the generator is under 1 KB:", sys.getsizeof(squares_gen) < 1_000)
print("same total:", sum(squares_gen) == sum(squares_list))


def peak_memory(func):
    tracemalloc.start()
    func()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


list_peak = peak_memory(lambda: sum([n * n for n in range(100_000)]))
gen_peak = peak_memory(lambda: sum(n * n for n in range(100_000)))
print("the list needs over 10 times more memory:", list_peak > 10 * gen_peak)
numbers = [1, 2, 3]
size_before = sys.getsizeof(numbers)
numbers[0] = 10 ** 50                          # a far bigger number in the same slot
print("same size:", sys.getsizeof(numbers) == size_before)   # shallow: the items are not counted
''', long=True)

K.code('amortized', r'''
class DynamicArray:
    """A list that doubles its space when it is full, like Python's list does (Python grows by less)."""

    def __init__(self):
        self.capacity = 1
        self.size = 0
        self.slots = [None]
        self.copies = 0

    def append(self, value):
        if self.size == self.capacity:         # full: get twice the space and copy everything
            self.capacity = self.capacity * 2
            new_slots = [None] * self.capacity
            for i in range(self.size):
                new_slots[i] = self.slots[i]
                self.copies += 1
            self.slots = new_slots
        self.slots[self.size] = value
        self.size += 1


array = DynamicArray()
for n in range(1, 1025):
    array.append(n)
    if n in (1, 2, 4, 8, 64, 1024):
        print(f"{n:>5} items  capacity {array.capacity:>5}  copies {array.copies:>5}  per append {array.copies / n:.2f}")
''', long=True)

K.code('memo', r'''
from functools import lru_cache

calls = 0


def fib_slow(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)


print(fib_slow(20), "with", calls, "calls")

calls = 0


@lru_cache(maxsize=None)
def fib_fast(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib_fast(n - 1) + fib_fast(n - 2)


print(fib_fast(20), "with", calls, "calls")
print(fib_fast.cache_info())
''', long=True)

DEDUPE = '''def slow_unique(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def fast_unique(items):
    return list(dict.fromkeys(items))


def main():
    data = [i % 2000 for i in range(20_000)]
    slow = slow_unique(data)
    fast = fast_unique(data)
    print(len(slow), len(fast), slow == fast)


main()'''

K.lesson('idea', 'Big O: how the work grows', f'''
{src('Python 3.14 documentation of timeit, cProfile, pstats, tracemalloc, sys.getsizeof and functools.lru_cache, and the TimeComplexity page of the Python wiki. Terminal outputs are real runs with CPython 3.14.')}
{wwh('<b>Time complexity</b> says how the number of steps of an algorithm grows when the input gets bigger. We write it in <b>Big O</b> notation: O(1), O(log n), O(n), O(n log n), O(n²). <b>Space complexity</b> says the same about memory.',
     'A program that is quick with 100 items can take hours with 1,000,000. Timing it on your laptop does not tell you that, because the time depends on the computer and the data you tried. Big O tells you, before you run anything, how the program will behave when the data grows.',
     'Count the basic steps (a comparison, an addition, a lookup) as a function of n, the size of the input. Keep only the part that grows fastest and drop constant factors: 3n² + 5n + 7 becomes O(n²). Then check with real measurements (timeit) and find the slow part with a profiler (cProfile).')}
{viz('pybigo')}
{run('counting')}
{note('Look at the table: for 1000 items linear search needs 1000 steps, binary search only 10, and comparing every pair needs 1,000,000. The same computer, the same data size, and a 100,000 times difference.', 'tip')}
{table(['Big O', 'Name', 'n = 1000 needs about', 'Typical code'], [
    ['O(1)', 'constant', '1 step', 'd[key], x in a set, list[i], append'],
    ['O(log n)', 'logarithmic', '10 steps', 'binary search, bisect, heap push'],
    ['O(n)', 'linear', '1,000 steps', 'one loop, x in a list, sum, max, copy'],
    ['O(n log n)', 'linearithmic', '10,000 steps', 'sorted(), list.sort()'],
    ['O(n²)', 'quadratic', '1,000,000 steps', 'a loop inside a loop over the same data'],
    ['O(2<sup>n</sup>)', 'exponential', 'more than the atoms in the universe', 'trying every subset, naive recursion']])}
''', kw=['time complexity', 'Big O', 'space complexity', 'O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n^2)', 'growth'])

K.lesson('rules', 'Finding the Big O of code', f'''
{steps('Four rules', [
    '<b>Drop constants.</b> 2n + 10 steps is O(n). Big O is about the shape of the growth, not the exact count.',
    '<b>Keep the biggest term.</b> n² + n is O(n²), because for large n the n² part is almost all the work.',
    '<b>Loops one after another add.</b> A loop over n, then another loop over n: O(n + n) = O(n).',
    '<b>Loops inside loops multiply.</b> A loop over n inside a loop over m: O(n &times; m). Over the same list: O(n²).'])}
{note('Hidden loops count too. x in my_list, my_list.index(x), my_list.remove(x), my_list.insert(0, x), "".join and slicing a[i:j] each walk through items. Putting one of them inside a loop is the most common way Python code becomes quadratic by accident.', 'warn')}
{table(['Operation', 'list', 'dict / set', 'collections.deque'], [
    ['Get or set by index or key', 'O(1)', 'O(1) on average', 'O(n) in the middle, O(1) at the ends'],
    ['x in container', 'O(n)', 'O(1) on average', 'O(n)'],
    ['Add at the end', 'O(1) amortized (append)', 'O(1) on average (d[k] = v, add)', 'O(1) (append)'],
    ['Add or remove at the front', 'O(n) (insert(0, x), pop(0))', 'not ordered by position', 'O(1) (appendleft, popleft)'],
    ['Remove a given value', 'O(n) (remove)', 'O(1) on average (del d[k], discard)', 'O(n)'],
    ['Sort', 'O(n log n)', 'sorted(d) O(n log n)', 'not supported in place'],
    ['Copy, len', 'O(n), O(1)', 'O(n), O(1)', 'O(n), O(1)']])}
{note('Average case versus worst case: a dict lookup is O(1) on average, but if many keys had the same hash it could take O(n). Python adds random salt to str hashes so attackers cannot cause this on purpose. For interviews and exams, dict and set operations are O(1).', 'exam')}
{versus('Checking whether a value is in a collection', ['', 'list', 'set'], [
    ['x in c', 'O(n): looks at items one by one', 'O(1): jumps to the right place with the hash'],
    ['Memory', 'Small', 'About 3 to 4 times more'],
    ['Keeps order and duplicates', 'Yes', 'No'],
    ['Items must be', 'Anything', 'Hashable (no lists or dicts)'],
    ['Best for', 'Data you go through in order', 'Many "is it there" questions']],
    'when you ask "is x there" inside a loop, turn the list into a set once before the loop. That one line often changes O(n²) into O(n).')}
''', kw=['Big O rules', 'drop constants', 'nested loops', 'hidden loops', 'list complexity', 'dict complexity', 'deque', 'average case', 'worst case'])

K.lesson('timing', 'Measuring with timeit', f'''
{run('timing')}
{term(['$ python -m timeit -s "nums = list(range(10_000))" "9_999 in nums"',
       '5000 loops, best of 5: 60.9 usec per loop',
       '$ python -m timeit -s "nums = set(range(10_000))" "9_999 in nums"',
       '10000000 loops, best of 5: 19.4 nsec per loop'], 'timeit from the terminal (real run, CPython 3.14)')}
{note('60.9 microseconds against 19.4 nanoseconds: the set is about 3,000 times faster for 10,000 numbers. -s is the setup, which runs once and is not timed. timeit chooses how many loops to run and reports the best of 5 rounds.', 'tip')}
{table(['Rule for fair timing', 'Why'], [
    ['Use timeit or time.perf_counter, not time.time', 'perf_counter is the most precise clock, and timeit repeats the code many times'],
    ['Take the minimum of several runs', 'Other programs only ever slow a run down, so the fastest run is closest to the truth'],
    ['Time with realistic sizes', 'With 10 items everything is fast. Differences show up with large n'],
    ['Keep setup out of the timed part', 'Building test data is not what you want to measure'],
    ['Compare on the same computer', 'Times are not comparable across machines, ratios are']])}
{versus('Ways to measure time', ['', 'time.time()', 'time.perf_counter()', 'timeit'], [
    ['Precision', 'Can be coarse, and jumps if the clock is changed', 'The best clock available', 'Uses perf_counter'],
    ['Repeats the code', 'No', 'No', 'Yes, many loops, several rounds'],
    ['Best for', 'Dates and times of day', 'Timing one block in a real program', 'Comparing two small pieces of code']],
    'timeit for small comparisons, perf_counter around a step of a real program, and time.time only for the time of day.')}
''', kw=['timeit', 'timeit.repeat', 'python -m timeit', 'perf_counter', 'benchmark', 'fair timing'])

K.lesson('profile', 'Finding the slow part with cProfile', f'''
{run('profiling')}
<p>The same idea from the terminal. This is the file and a real run of <code>python -m cProfile -s cumulative dedupe.py</code>:</p>
{show('dedupe.py', DEDUPE)}
{term(['$ python -m cProfile -s cumulative dedupe.py',
       '2000 2000 True',
       '         2010 function calls in 0.138 seconds',
       '',
       '   Ordered by: cumulative time',
       '',
       '   ncalls  tottime  percall  cumtime  percall filename:lineno(function)',
       '        1    0.000    0.000    0.138    0.138 {built-in method builtins.exec}',
       '        1    0.000    0.000    0.138    0.138 dedupe.py:1(<module>)',
       '        1    0.001    0.001    0.138    0.138 dedupe.py:13(main)',
       '        1    0.136    0.136    0.136    0.136 dedupe.py:1(slow_unique)',
       '        1    0.000    0.000    0.000    0.000 dedupe.py:9(fast_unique)',
       '        1    0.000    0.000    0.000    0.000 {built-in method fromkeys}',
       '     2000    0.000    0.000    0.000    0.000 {method \'append\' of \'list\' objects}'], 'cProfile (real run, first lines)')}
{table(['Column', 'Means'], [
    ['ncalls', 'How many times the function was called'],
    ['tottime', 'Time spent in the function itself, without the functions it calls'],
    ['cumtime', 'Time in the function including everything it calls'],
    ['percall', 'tottime / ncalls and cumtime / ncalls']])}
{note('slow_unique takes 0.136 of the 0.138 seconds, so that is the only function worth fixing. Speeding up anything else could save at most 0.002 seconds. Always profile before you optimise: the slow part is often not where you expect.', 'tip')}
{versus('Profilers', ['', 'cProfile (built in)', 'line_profiler', 'py-spy, Scalene'], [
    ['Shows', 'Time per function', 'Time per line', 'A live sampling of a running program, Scalene also memory'],
    ['Install', 'Nothing', 'pip install line_profiler', 'pip install py-spy or scalene'],
    ['Slows the program', 'Somewhat', 'A lot, only on chosen functions', 'Hardly at all (sampling)'],
    ['Best for', 'Finding the slow function', 'Finding the slow line inside it', 'Programs already running in production']],
    'start with cProfile to find the function, then line_profiler if you need the exact line.')}
''', kw=['cProfile', 'pstats', 'profiling', 'tottime', 'cumtime', 'line_profiler', 'py-spy', 'optimise'])

K.lesson('memory', 'Memory: getsizeof, tracemalloc and generators', f'''
{run('memory')}
{note('sys.getsizeof is shallow. For a list it counts the list and its slots, not the objects inside, which is why a list holding a huge number has the same size as one holding a small number. tracemalloc counts every allocation made while it runs, so it shows the real memory a piece of code needed.', 'exam')}
{table(['Way to save memory', 'How'], [
    ['Generators instead of lists', 'sum(x * x for x in data) makes one value at a time'],
    ['__slots__ in classes with many objects', 'No per object __dict__, often half the memory'],
    ['array.array or NumPy for numbers', 'Raw numbers in one block instead of separate int objects'],
    ['Read files line by line', 'for line in f instead of f.read() or f.readlines()'],
    ['del large objects you no longer need', 'The memory can be reused as soon as nothing refers to it']])}
''', kw=['memory', 'sys.getsizeof', 'tracemalloc', 'generator memory', '__slots__', 'array module', 'space complexity'])

K.lesson('amortized', 'Amortized cost and trading memory for time', f'''
{run('amortized')}
{note('Most appends cost one step. Now and then the array is full and must copy everything, which costs n steps. But because the space doubles each time, the copies add up to less than n in total, so the average (amortized) cost per append stays about 1. That is why list.append is called O(1) amortized.', 'tip')}
{run('memo')}
{note('fib_slow(20) makes 21,891 calls because it works out the same values again and again. With lru_cache each value from 0 to 20 is computed once: 21 calls. We spend a little memory (21 stored answers) to save a huge amount of time, which is the idea behind dynamic programming.', 'tip')}
{versus('Making code faster', ['', 'A better algorithm or data structure', 'Caching (lru_cache, a dict)', 'Small tweaks (local variables, fewer function calls)'], [
    ['Typical gain', '10 to 1,000,000 times', 'Big when the same inputs repeat', '10 % to 2 times'],
    ['Cost', 'Thinking', 'Memory, and care with changing data', 'Harder to read code'],
    ['When', 'First', 'When profiling shows repeated work', 'Last, and only in the hot spot']],
    'fix the Big O first. A better algorithm beats any amount of tuning.')}
''', kw=['amortized', 'dynamic array', 'list.append O(1)', 'lru_cache', 'memoization', 'dynamic programming', 'space time trade off'])

K.lesson('maths', 'The maths behind Big O', f'''
{fxs(fx('Definition of Big O', 'f(n) = O(g(n)) if there are numbers c &gt; 0 and n<sub>0</sub> with f(n) &le; c &middot; g(n) for every n &ge; n<sub>0</sub>', '3n + 5 = O(n): take c = 4 and n<sub>0</sub> = 5, since 3n + 5 &le; 4n when n &ge; 5.', key=True),
     fx('Big Omega and Big Theta', '&Omega;(g) is a lower bound, &Theta;(g) means both O(g) and &Omega;(g)', 'Comparison sorting is &Omega;(n log n): no comparison sort can do better.'),
     fx('Sum of a loop inside a loop', '1 + 2 + ... + n = n(n + 1) / 2 = O(n²)', 'Comparing each item with the ones after it: 1000 items give 499,500 comparisons.', key=True),
     fx('Geometric sum (doubling)', '1 + 2 + 4 + ... + n = 2n &minus; 1 &lt; 2n', 'Copies for 1024 appends with doubling: 1 + 2 + ... + 512 = 1023, about 1 per append.', key=True),
     fx('Halving', 'steps = &lfloor;log<sub>2</sub> n&rfloor; + 1', 'Binary search in 1,000,000 sorted items: at most 20 steps.'),
     fx('Master theorem', 'T(n) = a&middot;T(n/b) + O(n<sup>d</sup>) gives O(n<sup>d</sup>) if d &gt; log<sub>b</sub> a, O(n<sup>d</sup> log n) if d = log<sub>b</sub> a, O(n<sup>log<sub>b</sub> a</sup>) if d &lt; log<sub>b</sub> a', 'Merge sort: a = 2, b = 2, d = 1. log<sub>2</sub> 2 = 1 = d, so O(n log n).', key=True),
     fx('Time estimate', 'seconds &asymp; steps / (about 10<sup>7</sup> simple Python steps per second)', 'n = 10<sup>5</sup> with O(n²) is 10<sup>10</sup> steps: about 1000 s. With O(n log n) it is 1.7 &times; 10<sup>6</sup>: about 0.17 s.'))}
{steps('Worked example: is this fast enough for 100,000 items?', [
    'The code compares every pair: n(n &minus; 1) / 2 comparisons.',
    'n = 100,000 gives 100,000 &times; 99,999 / 2 = 4,999,950,000, about 5 &times; 10<sup>9</sup>.',
    'At about 10<sup>7</sup> simple steps per second in Python: 5 &times; 10<sup>9</sup> / 10<sup>7</sup> = 500 seconds.',
    'Sorting first (n log<sub>2</sub> n &asymp; 100,000 &times; 17 = 1.7 &times; 10<sup>6</sup>) and then one scan takes well under a second.',
    eq('O(n²): about 8 minutes. O(n log n): under 1 second')])}
{deep('Why log n has no base in Big O', '<p>log<sub>2</sub> n = log<sub>10</sub> n / log<sub>10</sub> 2, so logs with different bases differ only by a constant factor, and Big O drops constant factors. O(log<sub>2</sub> n), O(ln n) and O(log<sub>10</sub> n) are the same class.</p>')}
''', kw=['Big O definition', 'Big Omega', 'Big Theta', 'arithmetic series', 'geometric series', 'master theorem', 'logarithm', 'time estimate'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Know O(1), O(n) and O(n²), see that a loop inside a loop is slow, and use a set for "is it there" questions.</p>',
    '<p>Work out the Big O of functions with the four rules, know the costs of list, dict, set and deque operations, measure with timeit and find the slow function with cProfile.</p>',
    '<p>Use amortized analysis, the master theorem and recurrences, measure memory with tracemalloc, and trade memory for time with caching and dynamic programming.</p>',
    '<p>Reason about lower bounds (&Omega;(n log n) for comparison sorting), cache misses and memory layout, hash collision attacks, sampling profilers in production, and when C extensions, NumPy or PyPy change the constants.</p>')}
{grow('Spot slow loops and pick the right container.', 'Analyse, measure and profile.', 'Prove bounds and tune real systems.')}
''', kw=['beginner', 'expert', 'lower bound', 'cache', 'PyPy', 'NumPy'])

lc(219, 'Contains Duplicate II', 'contains-duplicate-ii', 'e', 'Remember the last index of each value', 'A dict from value to its last index answers "where did I see this before" in O(1), so one pass is enough: O(n) instead of comparing all pairs.', r'''
def contains_nearby_duplicate(nums, k):
    last_index = {}
    for i, value in enumerate(nums):
        if value in last_index and i - last_index[value] <= k:
            return True
        last_index[value] = i
    return False
''', [('contains_nearby_duplicate([1, 2, 3, 1], 3)', True), ('contains_nearby_duplicate([1, 0, 1, 1], 1)', True), ('contains_nearby_duplicate([1, 2, 3, 1, 2, 3], 2)', False)])
lc(2006, 'Count Number of Pairs With Absolute Difference K', 'count-number-of-pairs-with-absolute-difference-k', 'e', 'Count what you have seen', 'For each number, the partners seen so far are x &minus; k and x + k. A dict of counts finds them in O(1), so the whole list takes O(n).', r'''
def count_k_difference(nums, k):
    seen = {}
    pairs = 0
    for x in nums:
        pairs += seen.get(x - k, 0) + seen.get(x + k, 0)
        seen[x] = seen.get(x, 0) + 1
    return pairs
''', [('count_k_difference([1, 2, 2, 1], 1)', 4), ('count_k_difference([1, 3], 3)', 0), ('count_k_difference([3, 2, 1, 5, 4], 2)', 3)])
lc(1010, 'Pairs of Songs With Total Durations Divisible by 60', 'pairs-of-songs-with-total-durations-divisible-by-60', 'm', 'Group by remainder', 'Two songs fit when their remainders mod 60 add up to 0 or 60. Count remainders seen so far: O(n) instead of O(n²).', r'''
def num_pairs_divisible_by60(time):
    count = [0] * 60
    pairs = 0
    for t in time:
        r = t % 60
        pairs += count[(60 - r) % 60]
        count[r] += 1
    return pairs
''', [('num_pairs_divisible_by60([30, 20, 150, 100, 40])', 3), ('num_pairs_divisible_by60([60, 60, 60])', 3)])
lc(454, '4Sum II', '4sum-ii', 'm', 'Meet in the middle', 'Trying all four lists is O(n<sup>4</sup>). Count every a + b in a dict (O(n²)), then look up &minus;(c + d) for every pair of the other two lists (O(n²)).', r'''
def four_sum_count(nums1, nums2, nums3, nums4):
    sums = {}
    for a in nums1:
        for b in nums2:
            sums[a + b] = sums.get(a + b, 0) + 1
    total = 0
    for c in nums3:
        for d in nums4:
            total += sums.get(-(c + d), 0)
    return total
''', [('four_sum_count([1, 2], [-2, -1], [-1, 2], [0, 2])', 2), ('four_sum_count([0], [0], [0], [0])', 1)])
lc(974, 'Subarray Sums Divisible by K', 'subarray-sums-divisible-by-k', 'm', 'Prefix sums and remainders', 'A subarray sum is prefix[j] &minus; prefix[i]. It is divisible by k when both prefixes have the same remainder. Count remainders: O(n) instead of trying all O(n²) subarrays.', r'''
def subarrays_div_by_k(nums, k):
    count = {0: 1}
    prefix = 0
    result = 0
    for x in nums:
        prefix = (prefix + x) % k
        result += count.get(prefix, 0)
        count[prefix] = count.get(prefix, 0) + 1
    return result
''', [('subarrays_div_by_k([4, 5, 0, -2, -3, 1], 5)', 7), ('subarrays_div_by_k([5], 9)', 0)])
lc(209, 'Minimum Size Subarray Sum', 'minimum-size-subarray-sum', 'm', 'A sliding window', 'Grow the window on the right, shrink it from the left while the sum is big enough. Each index enters and leaves once, so it is O(n).', r'''
def min_sub_array_len(target, nums):
    best = len(nums) + 1
    total = 0
    left = 0
    for right, x in enumerate(nums):
        total += x
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best > len(nums) else best
''', [('min_sub_array_len(7, [2, 3, 1, 2, 4, 3])', 2), ('min_sub_array_len(4, [1, 4, 4])', 1), ('min_sub_array_len(11, [1, 1, 1, 1, 1, 1, 1, 1])', 0)])
lc(1004, 'Max Consecutive Ones III', 'max-consecutive-ones-iii', 'm', 'A window with at most k zeros', 'Move the right end one step at a time. When the window holds more than k zeros, move the left end until it does not. O(n) time, O(1) memory.', r'''
def longest_ones(nums, k):
    left = 0
    zeros = 0
    best = 0
    for right, x in enumerate(nums):
        if x == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
''', [('longest_ones([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2)', 6), ('longest_ones([0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3)', 10)])
lc(204, 'Count Primes', 'count-primes', 'm', 'Sieve of Eratosthenes', 'Testing each number by division is about O(n &radic;n). The sieve crosses out multiples of each prime starting at p², which is O(n log log n).', r'''
def count_primes(n):
    if n < 3:
        return 0
    is_prime = [True] * n
    is_prime[0] = is_prime[1] = False
    p = 2
    while p * p < n:
        if is_prime[p]:
            for multiple in range(p * p, n, p):
                is_prime[multiple] = False
        p += 1
    return sum(is_prime)
''', [('count_primes(10)', 4), ('count_primes(0)', 0), ('count_primes(1)', 0), ('count_primes(100)', 25)])
lc(287, 'Find the Duplicate Number', 'find-the-duplicate-number', 'm', 'Treat the list as a linked list', 'Without changing the list and with O(1) memory: i points to nums[i]. The repeated value is where a cycle starts. Floyd\'s slow and fast pointers find it in O(n).', r'''
def find_duplicate_number(nums):
    slow = nums[0]
    fast = nums[0]
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow
''', [('find_duplicate_number([1, 3, 4, 2, 2])', 2), ('find_duplicate_number([3, 1, 3, 4, 2])', 3), ('find_duplicate_number([3, 3, 3, 3, 3])', 3)])
lc(41, 'First Missing Positive', 'first-missing-positive', 'h', 'Use the list itself as the table', 'O(n) time and O(1) extra memory: swap each value v into place v &minus; 1. Then the first place i that does not hold i + 1 gives the answer.', r'''
def first_missing_positive(nums):
    n = len(nums)
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            target = nums[i] - 1
            nums[i], nums[target] = nums[target], nums[i]
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    return n + 1
''', [('first_missing_positive([1, 2, 0])', 3), ('first_missing_positive([3, 4, -1, 1])', 2), ('first_missing_positive([7, 8, 9, 11, 12])', 1)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Every problem here has an easy O(n²) answer that is too slow for the real limits (often n up to 100,000). The downloadable solutions use the ideas of this chapter: a dict or set for O(1) lookups, prefix sums, sliding windows, meet in the middle, a sieve and in place tricks for O(1) memory.</p>'), kw=['LeetCode', 'hash map', 'prefix sum', 'sliding window', 'sieve', 'Floyd cycle', 'meet in the middle'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Big O says how steps grow with n. Drop constants, keep the biggest term. Loops in a row add, loops inside loops multiply.',
    'O(1) dict and set lookups, O(log n) binary search, O(n) one pass, O(n log n) sorting, O(n²) nested loops.',
    'Watch for hidden loops: x in list, remove, insert(0, x) and slicing inside a loop make code quadratic.',
    'Measure with timeit (best of several runs, realistic n). Find the slow function with cProfile before optimising.',
    'getsizeof is shallow. tracemalloc shows real memory. Generators save memory.',
    'list.append is O(1) amortized because space doubles. lru_cache trades memory for time.'],
    'Next you meet the containers that make code fast: collections, heapq and bisect.')}
{files('Three tasks: find a pair with a given sum in one pass, guess the Big O from step counts, and write a caching decorator that counts hits and misses.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is the time complexity of x in my_set?', ['O(n)', 'O(1) on average', 'O(log n)', 'O(n²)'], 1, 'Hashing.', 'A set jumps to the right place using the hash of x.')
K.quiz('e', 'What is the Big O of 3n + 100?', ['O(3n)', 'O(n + 100)', 'O(n)', 'O(1)'], 2, 'Drop constants.', 'Constant factors and smaller terms are dropped.')
K.quiz('e', 'A loop over n items contains another loop over the same n items. What is the Big O?', ['O(n)', 'O(2n)', 'O(n²)', 'O(log n)'], 2, 'Loops inside loops multiply.', 'n &times; n = n².')
K.quiz('m', 'Which list operation is O(n)?', ['my_list[5]', 'my_list.append(x)', 'my_list.insert(0, x)', 'len(my_list)'], 2, 'Every item must move.', 'Inserting at the front shifts all the other items one place.')
K.quiz('m', 'Why does timeit report the best of several runs instead of the average?', ['The best is easier to read', 'Other programs only slow runs down, so the fastest is closest to the real cost', 'The average is always wrong', 'It is a Python bug'], 1, 'Noise only adds time.', 'Background work can only make a run slower, never faster.')
K.quiz('m', 'In cProfile output, what is the difference between tottime and cumtime?', ['There is none', 'tottime excludes the time in functions it calls, cumtime includes it', 'cumtime is per call', 'tottime is in milliseconds'], 1, 'Total versus cumulative.', 'cumtime includes every function called from inside.')
K.quiz('m', 'Why is list.append called O(1) amortized?', ['It never copies', 'Copies happen rarely, and because space grows by a factor the average cost per append stays constant', 'Python uses a linked list', 'It is O(n)'], 1, 'Doubling.', 'The total copying for n appends is less than about 2n.')
K.quiz('m', 'What does sys.getsizeof(my_list) count?', ['The list and every object inside it', 'Only the list object and its slots, not the items', 'Only the items', 'The whole program'], 1, 'Shallow.', 'Use tracemalloc for the full picture.')
K.quiz('h', 'What is the Big O of binary search on a sorted list of n items?', ['O(n)', 'O(log n)', 'O(1)', 'O(n log n)'], 1, 'Halving.', 'Each step throws away half of what is left.')
K.quiz('h', 'By the master theorem, what is T(n) = 2T(n/2) + O(n)?', ['O(n)', 'O(n log n)', 'O(n²)', 'O(log n)'], 1, 'a = 2, b = 2, d = 1.', 'log<sub>2</sub> 2 = 1 = d, so O(n<sup>d</sup> log n) = O(n log n). This is merge sort.')
K.quiz('h', 'fib_slow(n) calls itself twice for every n of at least 2, with no cache. What is its time complexity?', ['O(n)', 'O(n²)', 'Exponential, about O(1.618<sup>n</sup>)', 'O(log n)'], 2, 'The call tree.', 'The number of calls grows like the Fibonacci numbers themselves, roughly 1.618<sup>n</sup>.')
K.quiz('x', 'In the style of an MIT 6.006 exam: which is the tightest lower bound for sorting n items using only comparisons?', ['&Omega;(n)', '&Omega;(n log n)', '&Omega;(n²)', '&Omega;(log n)'], 1, 'Decision trees.', 'There are n! orders and each comparison has 2 outcomes, so at least log<sub>2</sub>(n!) = &Theta;(n log n) comparisons are needed.')
K.quiz('x', 'In the style of a Stanford CS161 exam: what does T(n) = 3T(n/2) + O(n) solve to?', ['O(n log n)', 'O(n<sup>1.585</sup>)', 'O(n²)', 'O(n)'], 1, 'Compare d with log<sub>b</sub> a.', 'log<sub>2</sub> 3 is about 1.585, which is bigger than d = 1, so T(n) = O(n<sup>log<sub>2</sub> 3</sup>). This is Karatsuba multiplication.')

K.calc('e', 'How many steps does linear search need in the worst case for 1000 items?', '1000', 'One step per item.', ['The target is last or missing.', 'Every item is checked.', eq('1000')], check=1000)
K.calc('e', 'How many comparisons does a loop over 10 items inside another loop over the same 10 items make?', '100', 'n &times; n.', ['10 &times; 10.', 'Every pair, including an item with itself.', eq('100')], check=100)
K.calc('e', 'At most how many steps does binary search need for 1024 sorted items?', '11', '&lfloor;log<sub>2</sub> n&rfloor; + 1.', ['log<sub>2</sub> 1024 = 10.', 'Add 1 for the last check.', eq('11')], check=11)
K.calc('m', 'How many comparisons does comparing each of 1000 items with every later item make?', '499500', 'n(n &minus; 1) / 2.', ['1000 &times; 999 = 999,000.', 'Divide by 2.', eq('499,500')], check=1000 * 999 // 2)
K.calc('m', 'With doubling, how many copies do 1024 appends make in total, starting from capacity 1?', '1023', '1 + 2 + 4 + ... + 512.', ['Resizes copy 1, 2, 4, ..., 512 items.', 'That geometric sum is 1024 &minus; 1.', eq('1023')], check=sum(2 ** i for i in range(10)))
K.calc('m', 'An O(n²) program takes 2 seconds for n = 1000. About how many seconds for n = 3000?', '18', 'Tripling n multiplies n² by 9.', ['(3000 / 1000)² = 9.', '2 &times; 9.', eq('18 s')], check=2 * 9)
K.calc('m', 'How many calls does fib_slow(5) make with no cache, counting the first call?', '15', 'calls(n) = 1 + calls(n &minus; 1) + calls(n &minus; 2), with calls(0) = calls(1) = 1.', ['calls(2) = 3, calls(3) = 5, calls(4) = 9.', 'calls(5) = 1 + 9 + 5.', eq('15')], check=15)
K.calc('h', 'About how many seconds do 5 &times; 10<sup>9</sup> simple Python steps take at 10<sup>7</sup> steps per second?', '500', 'Steps / speed.', ['5 &times; 10<sup>9</sup> / 10<sup>7</sup>.', '= 5 &times; 10<sup>2</sup>.', eq('500 s')], check=5 * 10 ** 9 // 10 ** 7)
K.calc('h', 'For n = 1,048,576 (2<sup>20</sup>), how many times more work is O(n) than O(log<sub>2</sub> n)?', '52428.8', 'n / log<sub>2</sub> n.', ['log<sub>2</sub> 2<sup>20</sup> = 20.', '1,048,576 / 20.', eq('52,428.8')], check=2 ** 20 / 20)
K.calc('x', 'In the style of an MIT 6.006 exam: T(n) = 4T(n/2) + O(n). What is the exponent p in T(n) = O(n<sup>p</sup>)?', '2', 'Compare d = 1 with log<sub>2</sub> 4.', ['a = 4, b = 2, so log<sub>b</sub> a = 2.', 'd = 1 &lt; 2, the leaves win.', eq('O(n²), p = 2')], check=2)

K.assign('pairsum', 'e', 'Find a pair with a given sum in one pass',
         '<p>Write <code>has_pair_with_sum(nums, target)</code> that returns True when two <b>different positions</b> in nums add up to target. Do it in O(n) with a set of the numbers seen so far, not with two nested loops. The starter looks fast but has a bug: it can use the same number twice.</p>',
         '''
def has_pair_with_sum(nums, target):
    seen = set(nums)
    for x in nums:
        if target - x in seen:
            return True
    return False
''', [('has_pair_with_sum([2, 7, 11, 15], 9)', True), ('has_pair_with_sum([3], 6)', False), ('has_pair_with_sum([3, 3], 6)', True), ('has_pair_with_sum([1, 2, 4], 8)', False), ('has_pair_with_sum([], 0)', False)],
         '''
def has_pair_with_sum(nums, target):
    seen = set()
    for x in nums:
        if target - x in seen:
            return True
        seen.add(x)
    return False
''', 'Check target &minus; x against the numbers BEFORE x, then add x. That way x can never pair with itself.', '<p>One pass with a set is O(n) time and O(n) memory. Two nested loops would be O(n²) time and O(1) memory: the classic trade of memory for time.</p>')
K.assign('guess', 'm', 'Guess the Big O from step counts',
         '<p>Write <code>guess_big_o(steps_n, steps_2n)</code>. It gets the step count of an algorithm for some n and for 2n, and returns one of "O(1)", "O(log n)", "O(n)", "O(n^2)" or "O(2^n)". Use the ratio r = steps_2n / steps_n: r at most 1.05 is O(1), under 1.8 is O(log n), under 3 is O(n), under 6 is O(n^2), anything bigger is O(2^n).</p>',
         '''
def guess_big_o(steps_n, steps_2n):
    if steps_2n == steps_n:
        return "O(1)"
    return "O(n)"
''', [('guess_big_o(5, 5)', 'O(1)'), ('guess_big_o(10, 11)', 'O(log n)'), ('guess_big_o(100, 200)', 'O(n)'), ('guess_big_o(100, 400)', 'O(n^2)'), ('guess_big_o(1024, 1048576)', 'O(2^n)'), ('guess_big_o(1000, 1040)', 'O(1)')],
         '''
def guess_big_o(steps_n, steps_2n):
    ratio = steps_2n / steps_n
    if ratio <= 1.05:
        return "O(1)"
    if ratio < 1.8:
        return "O(log n)"
    if ratio < 3:
        return "O(n)"
    if ratio < 6:
        return "O(n^2)"
    return "O(2^n)"
''', 'Doubling n: O(1) stays the same, O(log n) adds one step, O(n) doubles, O(n²) multiplies by 4, and O(2<sup>n</sup>) squares the count.', '<p>This "doubling test" is a real technique: time a program at n and 2n and the ratio tells you its growth. Measure at large n, because small inputs hide the shape behind fixed costs.</p>')
K.assign('memo', 'h', 'A caching decorator that counts hits and misses',
         '<p>Write a decorator <code>memo(func)</code> that stores results in a dict keyed by the positional arguments. The wrapper must have two attributes, <code>hits</code> (answer found in the cache) and <code>misses</code> (answer had to be computed), both starting at 0. fib is decorated with it so you can test.</p>',
         '''
def memo(func):
    def wrapper(*args):
        return func(*args)
    wrapper.hits = 0
    wrapper.misses = 0
    return wrapper


@memo
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
''', [('fib(30)', 832040), ('(fib(30), fib.misses)[1]', 31), ('(lambda f: [f(3), f(3), f(4), f.hits, f.misses])(memo(lambda x: x * 2))', [6, 6, 8, 1, 2]), ('(lambda f: [f(2, 3), f(2, 3), f.hits])(memo(pow))', [8, 8, 1])],
         '''
def memo(func):
    cache = {}

    def wrapper(*args):
        if args in cache:
            wrapper.hits += 1
            return cache[args]
        wrapper.misses += 1
        result = func(*args)
        cache[args] = result
        return result

    wrapper.hits = 0
    wrapper.misses = 0
    return wrapper


@memo
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
''', 'Check the cache first and count a hit. Otherwise count a miss, compute, store and return. Each of fib(0) to fib(30) is computed once: 31 misses.', '<p>functools.lru_cache and functools.cache do exactly this, written in C and with cache_info() to show hits and misses. Arguments must be hashable because they are dict keys.</p>')

K.must('Big O', 'Drop constants, keep the biggest term. Loops in a row add, nested loops multiply. O(1) &lt; O(log n) &lt; O(n) &lt; O(n log n) &lt; O(n²) &lt; O(2<sup>n</sup>).')
K.must('Costs', 'list: index O(1), append O(1) amortized, x in list O(n), insert(0)/pop(0) O(n). dict and set: O(1) average. sort O(n log n).')
K.must('Measure', 'timeit (python -m timeit -s setup stmt, best of several runs), time.perf_counter, realistic n.')
K.must('Profile', 'python -m cProfile -s cumulative file.py, tottime vs cumtime, fix only the hot spot. tracemalloc for memory, getsizeof is shallow.')
K.must('Trade offs', 'A better algorithm first. Sets for lookups, lru_cache for repeated work, generators to save memory.')

T = K.topic(
    slug='py-complexity', topic='py-complexity', step=(4, 'Speed: complexity and smart data structures', 'py-a4', 'Work out how fast code is, measure it, find the slow part, and pick the data structures that make it fast.', 'Advanced'),
    title='Complexity, timing and profiling', short='Complexity and profiling', badge='4.1', minutes=75,
    lead='Find out how your code behaves when the data grows. Learn Big O, the cost of list, dict and set operations, measuring with timeit, finding the slow part with cProfile, memory with tracemalloc, amortized cost and caching.',
    desc='time and space complexity, Big O, Big Omega and Big Theta, rules for loops, hidden loops, costs of list, dict, set and deque operations, average and worst case, timeit and perf_counter, cProfile and pstats, tottime and cumtime, line_profiler and py-spy, sys.getsizeof and tracemalloc, amortized analysis of list.append, lru_cache and memoization, the master theorem.',
    summary='Big O, operation costs, timeit, cProfile, memory, amortized cost and caching.',
    keywords=['complexity', 'Big O', 'timeit', 'cProfile', 'profiling', 'tracemalloc', 'amortized', 'lru_cache', 'master theorem', 'performance'],
    recap='<p>Work out the Big O first, measure with timeit, profile before you optimise, and choose the data structure that turns slow loops into fast lookups.</p>',
    added='2026-11-07', leet=leet_items())
