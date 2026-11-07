# Advanced Python 4.2: collections, heapq and bisect. Checked against the Python 3.14 documentation of the
# collections module (Counter, deque, namedtuple, OrderedDict, ChainMap, defaultdict), heapq (including the
# max-heap functions heappush_max, heappop_max and heapify_max that are new in 3.14) and bisect (key= since 3.10).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items, show, term

chapter('py-collections')
K = Kit()

K.code('counting', r'''
from collections import Counter

votes = Counter(["tea", "coffee", "tea", "juice", "tea", "coffee"])
print(votes)
print(votes["tea"], votes["water"])            # a missing key counts as 0, no KeyError
print(votes.most_common(2))
print(votes.total())                           # the sum of all counts (Python 3.10+)

monday = Counter(apples=3, pears=1)
tuesday = Counter(apples=1, plums=2)
print(monday + tuesday)                        # add the counts
print(monday - tuesday)                        # subtract, and drop counts of 0 or less
print(monday & tuesday)                        # the smaller count of each item
print(monday | tuesday)                        # the bigger count of each item
print(sorted((monday + tuesday).elements()))   # each item repeated by its count
print(Counter("listen") == Counter("silent"))  # same letters, same counts: an anagram
''')

K.code('queues', r'''
from collections import deque

line = deque(["Ann", "Ben"])
line.append("Cat")                             # join at the back
line.appendleft("VIP")                         # go straight to the front
print(line)
print(line.popleft(), line.pop(), line)        # O(1) at both ends
line.rotate(1)                                 # move the last item to the front
print(line)

recent = deque(maxlen=3)                       # keeps only the last 3 items
for page in ["home", "shop", "cart", "pay", "done"]:
    recent.append(page)
print(list(recent))


def shortest_path(graph, start, goal):
    """Breadth first search: visit places in order of distance, with a deque as the queue."""
    queue = deque([[start]])
    seen = {start}
    while queue:
        path = queue.popleft()
        place = path[-1]
        if place == goal:
            return path
        for next_place in graph[place]:
            if next_place not in seen:
                seen.add(next_place)
                queue.append(path + [next_place])
    return None


roads = {"A": ["B", "C"], "B": ["D"], "C": ["D", "E"], "D": ["F"], "E": ["F"], "F": []}
print(shortest_path(roads, "A", "F"))
''')

K.code('records', r'''
from collections import ChainMap, OrderedDict, defaultdict, namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p, p.x, p[1])
x, y = p                                       # still a tuple: unpacking and indexing work
print(p._replace(x=10), p._asdict(), Point._fields)

cache = OrderedDict()
for key in ["a", "b", "c"]:
    cache[key] = key.upper()
cache.move_to_end("a")                         # "a" was just used: make it the newest
print(list(cache))
print(cache.popitem(last=False))               # remove the oldest: the heart of an LRU cache

defaults = {"theme": "light", "lang": "en", "size": 12}
user = {"theme": "dark"}
settings = ChainMap(user, defaults)            # look in user first, then in defaults
print(settings["theme"], settings["lang"], len(settings))


def tree():
    return defaultdict(tree)                   # a dict that makes nested dicts when needed


menu = tree()
menu["drinks"]["hot"]["tea"] = 2
print(menu["drinks"]["hot"]["tea"], list(menu["drinks"]))
''')

K.code('heaps', r'''
import heapq

heap = []
for x in [5, 3, 8, 1, 9, 2]:
    heapq.heappush(heap, x)
print(heap)                                    # heap order, not sorted order
print(heapq.heappop(heap), heap)

numbers = [7, 2, 9, 4, 1]
heapq.heapify(numbers)                         # turn a list into a heap in O(n)
print(numbers[0])

scores = {"ana": 88, "bo": 95, "cy": 70, "di": 91}
print(heapq.nlargest(2, scores, key=scores.get))
print(heapq.nsmallest(2, [5, 1, 4, 2]))

tasks = []
heapq.heappush(tasks, (2, "write report"))
heapq.heappush(tasks, (1, "fix the server"))
heapq.heappush(tasks, (3, "lunch"))
while tasks:
    priority, task = heapq.heappop(tasks)      # tuples compare by their first item first
    print(priority, task)

print(list(heapq.merge([1, 4, 9], [2, 3, 10])))   # merge sorted lists lazily

biggest = [3, 8, 5]
heapq.heapify_max(biggest)                     # a max-heap (Python 3.14+)
print(heapq.heappop_max(biggest))
old_way = [-x for x in [3, 8, 5]]              # before 3.14: store negative numbers
heapq.heapify(old_way)
print(-heapq.heappop(old_way))
''')

K.code('sorted_lists', r'''
import bisect

scores = [10, 20, 20, 30, 40]
print(bisect.bisect_left(scores, 20), bisect.bisect_right(scores, 20))
bisect.insort(scores, 25)                      # insert and stay sorted
print(scores)


def grade(mark):
    limits = [50, 60, 70, 80]                  # where D, C, B and A start
    letters = "FDCBA"
    return letters[bisect.bisect_right(limits, mark)]


print([grade(m) for m in [33, 50, 69, 70, 95]])


def count_between(sorted_items, low, high):
    """How many items are from low to high, in O(log n)."""
    return bisect.bisect_right(sorted_items, high) - bisect.bisect_left(sorted_items, low)


ages = [12, 15, 18, 18, 21, 30, 45]
print(count_between(ages, 18, 30))

people = [("ann", 31), ("bo", 25), ("cy", 40)]
people.sort(key=lambda person: person[1])
index = bisect.bisect_left(people, 30, key=lambda person: person[1])   # key= since Python 3.10
print(index, people[index])
''')

K.lesson('idea', 'The right container for the job', f'''
{src('Python 3.14 documentation of collections, heapq and bisect.')}
{wwh('The <b>collections</b> module adds containers that do one job better than a plain list or dict: <b>Counter</b> for counting, <b>deque</b> for queues, <b>namedtuple</b> for small records, <b>OrderedDict</b> and <b>ChainMap</b> for special dicts, and <b>defaultdict</b> for missing keys. <b>heapq</b> turns a list into a priority queue and <b>bisect</b> searches and inserts in a sorted list.',
     'Chapter 4.1 showed that the wrong container makes code slow: list.pop(0) is O(n), finding the smallest of a changing list again and again is O(n) each time, and searching a sorted list item by item wastes its order. These tools make those jobs O(1) or O(log n), and the code shorter and clearer too.',
     'Each one is written in C and tested by millions of programs. You import it and use it like a normal list or dict: deque has append and pop at both ends, Counter is a dict of counts, heapq is a set of functions that keep any list in heap order, and bisect uses binary search.')}
{table(['You need to', 'Use', 'Speed of the key operation'], [
    ['Count things', 'collections.Counter', 'O(1) per item'],
    ['Group things by a key', 'collections.defaultdict(list)', 'O(1) per item'],
    ['Add and remove at both ends (a queue)', 'collections.deque', 'O(1) at each end'],
    ['Keep only the last n items', 'deque(maxlen=n)', 'O(1), old items drop off'],
    ['A small read only record with names', 'namedtuple or a frozen dataclass', 'Same as a tuple'],
    ['Always get the smallest (or largest) item', 'heapq', 'O(log n) push and pop, O(1) peek'],
    ['The k largest or smallest of many', 'heapq.nlargest, heapq.nsmallest', 'O(n log k)'],
    ['Search or insert in a sorted list', 'bisect', 'O(log n) search, O(n) insert'],
    ['Look through several dicts in order', 'collections.ChainMap', 'O(number of dicts)']])}
''', kw=['collections', 'Counter', 'deque', 'namedtuple', 'OrderedDict', 'ChainMap', 'defaultdict', 'heapq', 'bisect', 'choosing a container'])

K.lesson('counter', 'Counter: counting made easy', f'''
{run('counting')}
{note('Counter is a dict subclass, so everything a dict can do works too. Unlike a dict, a missing key gives 0 instead of KeyError. most_common(k) returns the k most common items with their counts, and items with the same count keep the order in which they were first seen.', 'tip')}
{table(['Counter operation', 'Result'], [
    ['c + d', 'Adds counts, keeps only positive ones'], ['c - d', 'Subtracts counts, keeps only positive ones'],
    ['c &amp; d', 'The smaller count of each item (intersection)'], ['c | d', 'The bigger count of each item (union)'],
    ['c.update(items), c.subtract(items)', 'Change counts in place (subtract can go below 0)'],
    ['c.elements()', 'Each item repeated count times'], ['c.total()', 'Sum of all counts (3.10+)']])}
''', kw=['Counter', 'most_common', 'total', 'elements', 'multiset', 'anagram', 'counting'])

K.lesson('deque', 'deque: a fast queue with two ends', f'''
{run('queues')}
{note('A deque (say "deck") is a double ended queue. Adding and removing at either end is O(1). A list does the same at the end, but list.insert(0, x) and list.pop(0) must shift every other item, which is O(n).', 'exam')}
{note('Breadth first search (BFS) always takes the oldest path from the front of the queue and adds new paths at the back. That is why it finds the path with the fewest steps first, and why it needs a deque, not a list.', 'tip')}
{versus('A queue (first in, first out)', ['', 'list with pop(0)', 'collections.deque', 'queue.Queue'], [
    ['Remove from the front', 'O(n)', 'O(1)', 'O(1)'],
    ['Index in the middle', 'O(1)', 'O(n)', 'Not supported'],
    ['Safe between threads', 'No', 'append and popleft are thread safe', 'Yes, with blocking get and put'],
    ['Best for', 'Stacks and arrays', 'Queues, BFS, sliding windows, last n items', 'Passing work between threads (step 5)']],
    'use deque for queues inside one program and queue.Queue to pass work between threads.')}
''', kw=['deque', 'appendleft', 'popleft', 'rotate', 'maxlen', 'queue', 'BFS', 'breadth first search', 'sliding window'])

K.lesson('records', 'namedtuple, OrderedDict, ChainMap and defaultdict', f'''
{run('records')}
{versus('Small records', ['', 'tuple', 'namedtuple', 'dataclass', 'dict'], [
    ['Fields by name', 'No, only p[0]', 'Yes, p.x', 'Yes, p.x', 'Yes, p["x"]'],
    ['Can change', 'No', 'No (use _replace)', 'Yes, unless frozen=True', 'Yes'],
    ['Memory', 'Smallest', 'Same as a tuple', 'More, unless slots=True', 'Most'],
    ['Methods and defaults', 'No', 'defaults=, few methods', 'Yes, any', 'No'],
    ['Best for', 'Two or three values that go together', 'Read only rows, like CSV lines', 'Objects with behaviour', 'Data whose keys are not known in advance']],
    'namedtuple for light read only records, dataclass when you need methods, defaults or changes.')}
{note('Since Python 3.7 every dict keeps insertion order. OrderedDict still has extras: move_to_end(key), popitem(last=False) for the oldest item, and == compares order too. That makes it the classic tool for an LRU cache.', 'exam')}
{note('ChainMap does not copy anything. It searches the dicts one after another, so a change to user is seen at once. Writes go to the first dict only. It is how Python looks up names: locals, then globals, then builtins.', 'tip')}
''', kw=['namedtuple', '_replace', '_asdict', 'OrderedDict', 'move_to_end', 'LRU', 'ChainMap', 'defaultdict', 'nested defaultdict', 'dataclass vs namedtuple'])

K.lesson('heap', 'heapq: a priority queue in a list', f'''
{viz('pyheap')}
{run('heaps')}
{note('A heap is a list where every item is smaller than or equal to its two children: heap[i] &le; heap[2i + 1] and heap[i] &le; heap[2i + 2]. So heap[0] is always the smallest. The rest is NOT sorted. heappush and heappop are O(log n), heapify is O(n), and looking at heap[0] is O(1).', 'exam')}
{note('Put tuples like (priority, count, task) in a heap. Tuples compare item by item, so the priority decides first. The count (from itertools.count()) breaks ties, so two tasks with the same priority never have to be compared, which would fail for objects that cannot be compared.', 'tip')}
{versus('Getting the smallest item many times', ['', 'min(list) each time', 'Keep the list sorted', 'heapq'], [
    ['Add an item', 'O(1)', 'O(n) (insort shifts items)', 'O(log n)'],
    ['Take the smallest', 'O(n)', 'O(1) from the end of a reverse sorted list', 'O(log n)'],
    ['Good when', 'You ask only once or twice', 'You rarely add, often read in order', 'You keep adding and taking, as in a scheduler or Dijkstra']],
    'a heap is the best all round choice when items keep arriving and you keep taking the most urgent one.')}
''', kw=['heapq', 'heap', 'priority queue', 'heappush', 'heappop', 'heapify', 'nlargest', 'nsmallest', 'merge', 'max heap', 'heappush_max'])

K.lesson('bisect', 'bisect: binary search in a sorted list', f'''
{run('sorted_lists')}
{table(['Function', 'Returns'], [
    ['bisect_left(a, x)', 'The first index where x could go: before any equal items'],
    ['bisect_right(a, x) (also bisect)', 'The index after the last item equal to x'],
    ['insort(a, x)', 'Puts x into a, keeping it sorted (search O(log n), insert O(n))'],
    ['key=func (3.10+)', 'Compare func(item) instead of the item, without building a new list']])}
{note('bisect_right(a, x) &minus; bisect_left(a, x) is how many times x appears. Counting values in a range or looking up which band a number falls into (grades, tax brackets, prices) are classic uses.', 'tip')}
{deep('Sorted containers for big data', '<p>insort is O(n) because a list must shift items. For millions of inserts the third party package sortedcontainers (SortedList) keeps O(log n) inserts. In the standard library, a heap is the tool when you only ever need the smallest item.</p>')}
''', kw=['bisect', 'bisect_left', 'bisect_right', 'insort', 'binary search', 'key', 'grade lookup', 'range count', 'sortedcontainers'])

K.lesson('maths', 'The maths: heap indexes, heights and costs', f'''
{fxs(fx('Heap indexes', 'parent(i) = (i &minus; 1) // 2, children 2i + 1 and 2i + 2', 'Index 4 has parent 1 and children 9 and 10.', key=True),
     fx('Height of a heap', 'h = &lfloor;log<sub>2</sub> n&rfloor;', '1,000,000 items: 19 levels below the top, so a push makes at most 19 swaps.', key=True),
     fx('heapify is O(n)', 'work &le; &sum; (n / 2<sup>h+1</sup>) &middot; h &lt; n', 'Most items are near the bottom and move only a little, so the total is less than n swaps.'),
     fx('Top k with a heap', 'O(n log k) instead of O(n log n) for a full sort', 'k = 10 of n = 10<sup>6</sup>: about 3.3 &times; 10<sup>6</sup> steps against 2 &times; 10<sup>7</sup>.', key=True),
     fx('Binary search', 'comparisons &le; &lceil;log<sub>2</sub>(n + 1)&rceil;', '1000 sorted items: at most 10 comparisons.'),
     fx('Front removals from a list', 'shifts = (n &minus; 1) + (n &minus; 2) + ... + 1 = n(n &minus; 1) / 2', 'Emptying 10,000 items with pop(0): about 5 &times; 10<sup>7</sup> shifts. With deque.popleft: 0.'))}
{steps('Worked example: the top 3 of 1,000,000 scores', [
    'Sorting: n log<sub>2</sub> n &asymp; 10<sup>6</sup> &times; 20 = 2 &times; 10<sup>7</sup> comparisons.',
    'heapq.nlargest(3, scores) keeps a heap of only 3 items while it reads all the scores.',
    'Each score costs at most log<sub>2</sub> 3 &asymp; 1.6 steps: about 1.6 &times; 10<sup>6</sup> in total.',
    eq('Over 10 times less work, and only 3 items in memory')])}
''', kw=['heap index', 'heap height', 'heapify O(n)', 'top k', 'binary search', 'log n', 'deque cost'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Count with Counter, group with defaultdict(list), and use deque for a queue.</p>',
    '<p>Use Counter arithmetic, deque(maxlen), namedtuple, OrderedDict for LRU, heapq for priority queues and top k, and bisect for sorted lookups.</p>',
    '<p>Explain heap order and its index maths, heapify in O(n), BFS with a deque, two heap medians, monotonic deques for sliding windows and patience sorting with bisect.</p>',
    '<p>Choose between heaps, balanced trees and skip lists, build indexed priority queues with lazy deletion, use heapq.merge for external sorting of data bigger than memory, and know where the C code of these modules gives its speed.</p>')}
{grow('Count, group and queue.', 'Prioritise, search and keep records.', 'Design data structure algorithms.')}
''', kw=['beginner', 'expert', 'monotonic deque', 'two heaps', 'external sort', 'lazy deletion'])

PLAY = '''

def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results
'''

lc(1046, 'Last Stone Weight', 'last-stone-weight', 'e', 'A max-heap with negative numbers', 'Always smash the two heaviest stones. heapq is a min-heap, so store &minus;weight. (Python 3.14 also has heappop_max, but LeetCode may run an older Python.)', r'''
import heapq


def last_stone_weight(stones):
    heap = [-s for s in stones]
    heapq.heapify(heap)
    while len(heap) > 1:
        first = -heapq.heappop(heap)
        second = -heapq.heappop(heap)
        if first != second:
            heapq.heappush(heap, -(first - second))
    return -heap[0] if heap else 0
''', [('last_stone_weight([2, 7, 4, 1, 8, 1])', 1), ('last_stone_weight([1])', 1), ('last_stone_weight([3, 3])', 0)])
lc(1351, 'Count Negative Numbers in a Sorted Matrix', 'count-negative-numbers-in-a-sorted-matrix', 'e', 'bisect on each row', 'Each row goes down from left to right. With key=lambda v: &minus;v it goes up, so bisect finds where the negatives start in O(log n) per row.', r'''
import bisect


def count_negatives(grid):
    total = 0
    for row in grid:
        start = bisect.bisect_right(row, 0, key=lambda v: -v)
        total += len(row) - start
    return total
''', [('count_negatives([[4, 3, 2, -1], [3, 2, 1, -1], [1, 1, -1, -2], [-1, -1, -2, -3]])', 8), ('count_negatives([[3, 2], [1, 0]])', 0)])
lc(215, 'Kth Largest Element in an Array', 'kth-largest-element-in-an-array', 'm', 'A min-heap of size k', 'Keep the k largest numbers seen so far in a min-heap. Its top is the kth largest. O(n log k) time and O(k) memory.', r'''
import heapq


def find_kth_largest(nums, k):
    heap = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]
''', [('find_kth_largest([3, 2, 1, 5, 6, 4], 2)', 5), ('find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4)', 4)])
lc(973, 'K Closest Points to Origin', 'k-closest-points-to-origin', 'm', 'nsmallest with a key', 'Compare squared distances x² + y² (no square root needed, the order is the same). heapq.nsmallest does it in O(n log k).', r'''
import heapq


def k_closest(points, k):
    return heapq.nsmallest(k, points, key=lambda p: p[0] * p[0] + p[1] * p[1])
''', [('k_closest([[1, 3], [-2, 2]], 1)', [[-2, 2]]), ('sorted(k_closest([[3, 3], [5, -1], [-2, 4]], 2))', [[-2, 4], [3, 3]])])
lc(692, 'Top K Frequent Words', 'top-k-frequent-words', 'm', 'Counter, then sort by two keys', 'Count with Counter. Sort by count going down, then by the word going up for ties: key=(-count, word).', r'''
from collections import Counter


def top_k_frequent_words(words, k):
    counts = Counter(words)
    ordered = sorted(counts, key=lambda word: (-counts[word], word))
    return ordered[:k]
''', [('top_k_frequent_words(["i", "love", "leetcode", "i", "love", "coding"], 2)', ['i', 'love']), ('top_k_frequent_words(["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4)', ['the', 'is', 'sunny', 'day'])])
lc(2300, 'Successful Pairs of Spells and Potions', 'successful-pairs-of-spells-and-potions', 'm', 'Sort once, then bisect for each spell', 'A spell s needs a potion of at least &lceil;success / s&rceil;. Sort the potions and bisect_left gives how many are too weak. O((n + m) log m).', r'''
import bisect


def successful_pairs(spells, potions, success):
    potions = sorted(potions)
    result = []
    for s in spells:
        need = (success + s - 1) // s
        result.append(len(potions) - bisect.bisect_left(potions, need))
    return result
''', [('successful_pairs([5, 1, 3], [1, 2, 3, 4, 5], 7)', [4, 0, 3]), ('successful_pairs([3, 1, 2], [8, 5, 8], 16)', [2, 0, 2])])
lc(300, 'Longest Increasing Subsequence', 'longest-increasing-subsequence', 'm', 'Patience sorting with bisect', 'tails[i] is the smallest last number of an increasing run of length i + 1. Each number replaces the first tail that is not smaller, found with bisect_left. O(n log n).', r'''
import bisect


def length_of_lis(nums):
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
''', [('length_of_lis([10, 9, 2, 5, 3, 7, 101, 18])', 4), ('length_of_lis([0, 1, 0, 3, 2, 3])', 4), ('length_of_lis([7, 7, 7, 7])', 1)])
lc(621, 'Task Scheduler', 'task-scheduler', 'm', 'Count the most common task', 'The most common task (count m) needs m &minus; 1 gaps of n slots after it. Tasks that share that top count fill the last row. The answer is never less than the number of tasks.', r'''
from collections import Counter


def least_interval(tasks, n):
    counts = Counter(tasks)
    top = max(counts.values())
    with_top = sum(1 for c in counts.values() if c == top)
    return max(len(tasks), (top - 1) * (n + 1) + with_top)
''', [('least_interval(["A", "A", "A", "B", "B", "B"], 2)', 8), ('least_interval(["A", "C", "A", "B", "D", "B"], 1)', 6), ('least_interval(["A", "A", "A", "B", "B", "B"], 3)', 10)])
lc(239, 'Sliding Window Maximum', 'sliding-window-maximum', 'h', 'A monotonic deque of indexes', 'Keep indexes whose values go down from front to back. Drop smaller values from the back before adding, and the front once it leaves the window. Each index enters and leaves once: O(n).', r'''
from collections import deque


def max_sliding_window(nums, k):
    window = deque()
    result = []
    for i, x in enumerate(nums):
        while window and nums[window[-1]] <= x:
            window.pop()
        window.append(i)
        if window[0] <= i - k:
            window.popleft()
        if i >= k - 1:
            result.append(nums[window[0]])
    return result
''', [('max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)', [3, 3, 5, 5, 6, 7]), ('max_sliding_window([1], 1)', [1])])
lc(295, 'Find Median from Data Stream', 'find-median-from-data-stream', 'h', 'Two heaps', 'A max-heap (negative numbers) holds the smaller half, a min-heap the bigger half. Keep their sizes equal or the low half one bigger. The median is at the tops.', r'''
import heapq


class MedianFinder:
    def __init__(self):
        self.low = []                          # max-heap of the smaller half, stored as negatives
        self.high = []                         # min-heap of the bigger half

    def addNum(self, num):
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def findMedian(self):
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2
''' + PLAY, [('play(MedianFinder, ["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"], [[], [1], [2], [], [3], []])', [None, None, None, 1.5, None, 2.0])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Each problem is solved by one tool of this chapter: heaps for the k largest, closest or heaviest items and for a running median, bisect for sorted lookups and the longest increasing subsequence, Counter for frequencies, and a deque for the sliding window maximum.</p>'), kw=['LeetCode', 'heap', 'top k', 'bisect', 'Counter', 'monotonic deque', 'two heaps', 'median'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Counter counts in one line, gives 0 for missing keys, and supports most_common, total and + - &amp; |.',
    'deque adds and removes at both ends in O(1). Use it for queues, BFS and (with maxlen) the last n items.',
    'namedtuple gives read only records with names. OrderedDict has move_to_end and popitem(last=False) for LRU caches. ChainMap layers dicts.',
    'heapq keeps a list in heap order: heap[0] is the smallest, push and pop are O(log n), heapify is O(n). Tuples set priorities.',
    'bisect finds positions in a sorted list in O(log n): bisect_left, bisect_right, insort and key=.'],
    'Step 5 is about doing many things at once: threads, processes and asyncio.')}
{files('Three tasks: the most common words with Counter, the hot potato game with a deque, and the fewest meeting rooms with a heap.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does Counter("banana")["z"] return?', ['KeyError', 'None', '0', '""'], 2, 'Missing keys.', 'A Counter returns 0 for items it has not seen.')
K.quiz('e', 'Which deque method removes an item from the left end?', ['pop()', 'popleft()', 'remove()', 'shift()'], 1, 'left.', 'popleft() takes from the front in O(1).')
K.quiz('e', 'After heapq.heappush is used for every item, which item is at heap[0]?', ['The largest', 'The smallest', 'The last pushed', 'The first pushed'], 1, 'Min-heap.', 'heapq keeps the smallest item at index 0.')
K.quiz('m', 'What is the time of list.pop(0) compared with deque.popleft()?', ['Both O(1)', 'O(n) and O(1)', 'O(1) and O(n)', 'Both O(n)'], 1, 'Shifting.', 'A list must move every other item one place to the left.')
K.quiz('m', 'What does deque(maxlen=3) do when a fourth item is appended?', ['Raises an error', 'Drops the oldest item from the other end', 'Ignores the new item', 'Grows to 4'], 1, 'A fixed window.', 'The item at the opposite end is thrown away.')
K.quiz('m', 'scores = [10, 20, 20, 30]. What is bisect.bisect_right(scores, 20)?', ['1', '2', '3', '4'], 2, 'After the equal items.', 'bisect_right returns the position after the last 20, which is index 3.')
K.quiz('m', 'Why push (priority, count, task) instead of (priority, task) onto a heap?', ['It is faster', 'The count breaks ties, so tasks are never compared with each other', 'heapq needs three items', 'To sort by count'], 1, 'Ties.', 'Equal priorities would compare the tasks, which may not support &lt;.')
K.quiz('m', 'What does Counter(a=3, b=1) - Counter(a=1, b=2) give?', ["Counter({'a': 2, 'b': -1})", "Counter({'a': 2})", "Counter({'a': 4, 'b': 3})", 'An error'], 1, 'Only positive counts stay.', 'The minus operator drops counts that are 0 or less.')
K.quiz('h', 'What is the time to build a heap from a list of n items with heapify?', ['O(n log n)', 'O(n)', 'O(log n)', 'O(n²)'], 1, 'Most nodes are low.', 'The sum of the heights of all nodes is less than n.')
K.quiz('h', 'In a heap stored in a list, where is the parent of the item at index 6?', ['3', '2', '5', '12'], 1, '(i &minus; 1) // 2.', '(6 &minus; 1) // 2 = 2.')
K.quiz('h', 'Which tool gives the 10 largest of 10,000,000 numbers using the least memory and time?', ['sorted(nums)[-10:]', 'heapq.nlargest(10, nums)', 'max() ten times on a copy', 'A set'], 1, 'O(n log k).', 'nlargest keeps only 10 items in a heap while reading the numbers.')
K.quiz('x', 'In the style of a Google interview: what is the time per operation of a running median with two heaps?', ['O(1) add, O(n) median', 'O(log n) add, O(1) median', 'O(n log n) add', 'O(n) for both'], 1, 'Heaps at the tops.', 'Each add moves items between heaps in O(log n). The median is read from the two tops in O(1).')
K.quiz('x', 'In the style of an MIT 6.006 exam: why does BFS with a FIFO queue find a path with the fewest edges?', ['It tries random paths', 'It visits nodes in order of their distance from the start', 'It uses recursion', 'It sorts the edges'], 1, 'Layers.', 'All nodes at distance d leave the queue before any node at distance d + 1, so the first time the goal is reached is by a shortest path.')

K.calc('e', 'Counter("mississippi")["s"] is how much?', '4', 'Count the letter s.', ['m i s s i s s i p p i.', 's appears at 4 places.', eq('4')], check=4)
K.calc('e', 'A deque(maxlen=3) gets 1, 2, 3, 4, 5 appended. What is the sum of what it holds?', '12', 'Only the last 3 stay.', ['It holds 3, 4, 5.', '3 + 4 + 5.', eq('12')], check=3 + 4 + 5)
K.calc('e', 'In a heap list, what are the indexes of the children of index 3? Give the larger one.', '8', '2i + 1 and 2i + 2.', ['2 &times; 3 + 1 = 7.', '2 &times; 3 + 2 = 8.', eq('8')], check=8)
K.calc('m', 'How many levels below the top does a heap of 1,000,000 items have?', '19', '&lfloor;log<sub>2</sub> n&rfloor;.', ['2<sup>19</sup> = 524,288 and 2<sup>20</sup> = 1,048,576.', 'So &lfloor;log<sub>2</sub> 10<sup>6</sup>&rfloor; = 19.', eq('19')], check=19)
K.calc('m', 'How many list shifts does emptying a 1000 item list with pop(0) cause?', '499500', 'n(n &minus; 1) / 2.', ['999 + 998 + ... + 1.', '1000 &times; 999 / 2.', eq('499,500')], check=1000 * 999 // 2)
K.calc('m', 'At most how many comparisons does binary search need in 1000 sorted items?', '10', '&lceil;log<sub>2</sub>(n + 1)&rceil;.', ['log<sub>2</sub> 1001 is about 9.97.', 'Round up.', eq('10')], check=10)
K.calc('m', 'a = [10, 20, 20, 20, 30]. What is bisect_right(a, 20) &minus; bisect_left(a, 20)?', '3', 'How many 20s.', ['bisect_left = 1.', 'bisect_right = 4, 4 &minus; 1.', eq('3')], check=3)
K.calc('h', 'Top 10 of n = 1,048,576 with a heap of size 10. About how many heap steps if each costs log<sub>2</sub> 10 &asymp; 3.32? Give millions, rounded to 1 decimal.', '3.5', 'n &times; log<sub>2</sub> k.', ['1,048,576 &times; 3.32 &asymp; 3,481,272.', 'That is about 3.5 million.', eq('3.5 million, against about 21 million for a full sort')], check=round(1_048_576 * 3.32 / 1_000_000, 1))
K.calc('h', 'Tasks A A A B B B with cooling time n = 2. What is the least number of time slots (LeetCode 621)?', '8', '(top &minus; 1)(n + 1) + tasks with the top count.', ['top = 3, n + 1 = 3.', '(3 &minus; 1) &times; 3 + 2 = 8.', eq('8: A B idle A B idle A B')], check=(3 - 1) * 3 + 2)
K.calc('x', 'In the style of a CMU 15-210 exam: heapify does at most &sum; h &middot; n / 2<sup>h+1</sup> swaps. Using &sum; h / 2<sup>h</sup> = 2, what is the bound as a multiple of n?', '1', 'Pull out n / 2.', ['&sum; h &middot; n / 2<sup>h+1</sup> = (n / 2) &middot; &sum; h / 2<sup>h</sup>.', '= (n / 2) &times; 2.', eq('n, so heapify is O(n)')], check=1)

K.assign('topwords', 'e', 'The most common words',
         '<p>Write <code>top_words(text, k)</code> that returns the k most common words of text as a list of [word, count] pairs, most common first. Make the text lower case and split it on spaces. Use collections.Counter and its most_common method. For equal counts keep the order in which the words first appear.</p>',
         '''
from collections import Counter


def top_words(text, k):
    counts = Counter(text.split())
    return sorted(counts.items())[:k]
''', [('top_words("the cat and the hat and the bat", 2)', [['the', 3], ['and', 2]]), ('top_words("A a b", 1)', [['a', 2]]), ('top_words("one", 3)', [['one', 1]]), ('top_words("", 2)', [])],
         '''
from collections import Counter


def top_words(text, k):
    counts = Counter(text.lower().split())
    return counts.most_common(k)
''', 'Counter(text.lower().split()).most_common(k) does all of it. most_common keeps first seen order for ties.', '<p>The results are tuples, and the tests compare them as lists because they go through JSON. Counter.most_common uses a heap (heapq.nlargest) when k is given, so it is O(n log k).</p>')
K.assign('potato', 'm', 'The hot potato game',
         '<p>Children stand in a circle (names in order). The potato is passed k times, moving the front child to the back each time, and then the child at the front leaves. Write <code>hot_potato(names, k)</code> that returns the names in the order they leave. Use a deque and its rotate method (rotate(-k) moves k items from the front to the back).</p>',
         '''
from collections import deque


def hot_potato(names, k):
    circle = deque(names)
    order = []
    while circle:
        order.append(circle.popleft())
    return order
''', [('hot_potato(["A", "B", "C", "D"], 1)', ['B', 'D', 'C', 'A']), ('hot_potato(["A", "B", "C", "D"], 0)', ['A', 'B', 'C', 'D']), ('hot_potato(["Ann", "Bo", "Cy"], 2)', ['Cy', 'Ann', 'Bo']), ('hot_potato([], 3)', [])],
         '''
from collections import deque


def hot_potato(names, k):
    circle = deque(names)
    order = []
    while circle:
        circle.rotate(-k)
        order.append(circle.popleft())
    return order
''', 'Before each popleft, call circle.rotate(-k). Negative numbers rotate to the left, which is the same as passing the potato k times.', '<p>This is the Josephus problem. With a list, moving the front to the back costs O(n) each time. With a deque, rotate(-k) costs O(k) and popleft O(1).</p>')
K.assign('rooms', 'h', 'The fewest meeting rooms',
         '<p>Each meeting is [start, end]. A room is free again at the end time, so a meeting starting at 10 can use a room whose meeting ends at 10. Write <code>min_rooms(meetings)</code> that returns the fewest rooms needed. Sort by start time and keep a heap of the end times of the rooms in use.</p>',
         '''
import heapq


def min_rooms(meetings):
    return len(meetings)
''', [('min_rooms([[0, 30], [5, 10], [15, 20]])', 2), ('min_rooms([[7, 10], [2, 4]])', 1), ('min_rooms([])', 0), ('min_rooms([[1, 5], [2, 6], [3, 7], [5, 8]])', 3), ('min_rooms([[1, 10], [10, 20], [20, 30]])', 1)],
         '''
import heapq


def min_rooms(meetings):
    ends = []
    for start, end in sorted(meetings):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)
    return len(ends)
''', 'Go through meetings by start time. If the earliest ending room (ends[0]) is free by the start, reuse it with heapreplace. Otherwise push a new end time. The heap size is the answer.', '<p>Sorting is O(n log n) and each heap step O(log n), so O(n log n) in total. heapreplace pops the smallest and pushes the new item in one step, which is faster than heappop then heappush.</p>')

K.must('Counter', 'Counter(items), c[x] is 0 if missing, most_common(k), total(), elements(), + - &amp; | on counts.')
K.must('deque', 'append, appendleft, pop, popleft all O(1), rotate(n), deque(maxlen=n). Queues and BFS use popleft.')
K.must('Records', 'namedtuple("P", ["x", "y"]) with _replace, _asdict, _fields. OrderedDict.move_to_end, popitem(last=False). ChainMap(first, fallback). defaultdict(list).')
K.must('heapq', 'heappush, heappop O(log n), heapify O(n), heap[0] smallest, nlargest and nsmallest O(n log k), merge, (priority, count, item), heappush_max in 3.14.')
K.must('bisect', 'bisect_left, bisect_right, insort, key= since 3.10. Range count = right(high) &minus; left(low). Only on sorted lists.')

T = K.topic(
    slug='py-collections', topic='py-collections', step=(4, 'Speed: complexity and smart data structures', 'py-a4', 'Work out how fast code is, measure it, find the slow part, and pick the data structures that make it fast.', 'Advanced'),
    title='collections, heapq and bisect', short='collections, heapq, bisect', badge='4.2', minutes=75,
    lead='Use the containers that make common jobs fast and short. Learn Counter, deque, namedtuple, OrderedDict, ChainMap and defaultdict, priority queues with heapq, and binary search in sorted lists with bisect.',
    desc='collections.Counter (most_common, total, arithmetic), deque (both ends, rotate, maxlen, BFS), namedtuple versus dataclass, OrderedDict and LRU caches, ChainMap, nested defaultdict, heapq (heappush, heappop, heapify, nlargest, nsmallest, merge, priorities, max-heap functions of 3.14), bisect (bisect_left, bisect_right, insort, key), heap index maths, heapify in O(n), top k in O(n log k).',
    summary='Counter, deque, namedtuple, OrderedDict, ChainMap, heapq priority queues and bisect.',
    keywords=['collections', 'Counter', 'deque', 'namedtuple', 'OrderedDict', 'ChainMap', 'defaultdict', 'heapq', 'priority queue', 'bisect', 'binary search'],
    recap='<p>Pick the container that fits the job: Counter to count, deque to queue, heapq to always get the most urgent item, and bisect to search sorted data.</p>',
    added='2026-11-07', leet=leet_items())
