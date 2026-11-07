# Advanced Python 2.1: iterators and generators. Follows PCAP-31-03 block 5 (generators, iterators, the iterator
# protocol, yield) and PCPP-32-101 good practice on lazy evaluation, checked against the Python 3.14 documentation
# (glossary entries iterable, iterator and generator, the iterator types section of the library reference, the
# yield expressions section of the language reference, inspect.getgeneratorstate), PEP 255 (simple generators),
# PEP 342 (send, throw, close) and PEP 380 (yield from).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-generators')
K = Kit()

K.code('protocol', r'''
nums = [10, 20, 30]
it = iter(nums)                                # ask the list for an iterator
print(type(it).__name__)
print(next(it), next(it), next(it))
try:
    next(it)                                   # nothing is left
except StopIteration:
    print("StopIteration: the iterator is used up")

# what a for loop really does with "hi"
it = iter("hi")
while True:
    try:
        ch = next(it)
    except StopIteration:
        break
    print("got", ch)

print(iter(nums) is iter(nums), iter(it) is it)
print(next(iter([]), "empty"))                 # a default instead of StopIteration
''')

K.code('iterclass', r'''
class Countdown:
    """An ITERATOR: it remembers where it is, so it can be used only once."""

    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


class Shelf:
    """An ITERABLE: every for loop gets a brand new iterator."""

    def __init__(self, books):
        self.books = books

    def __iter__(self):
        return iter(self.books)


c = Countdown(3)
print(list(c), list(c))                        # the second list is empty
s = Shelf(["Maths", "Python"])
print(list(s), list(s))                        # works every time
print(hasattr(c, "__next__"), hasattr(s, "__next__"))
''')

K.code('yieldfn', r'''
import inspect


def countdown(n):
    print("  start")
    while n > 0:
        yield n                                # hand n over and pause here
        n -= 1
    print("  done")


g = countdown(2)                               # nothing printed yet
print(type(g).__name__, inspect.getgeneratorstate(g))
print(next(g))
print(inspect.getgeneratorstate(g))
print(next(g))
print(next(g, "no more"))
print(inspect.getgeneratorstate(g))
print(list(countdown(3)))
''')

K.code('infinite', r'''
from itertools import islice
import sys


def fibonacci():
    a, b = 0, 1
    while True:                                # never ends, and that is fine
        yield a
        a, b = b, a + b


print(list(islice(fibonacci(), 10)))           # take only the first 10
for n in fibonacci():
    if n > 1000:
        print("first above 1000:", n)
        break

squares_list = [n * n for n in range(100_000)]
squares_gen = (n * n for n in range(100_000))
print(sys.getsizeof(squares_list) // 1000, "KB for the list")
print(sys.getsizeof(squares_gen), "bytes for the generator")
''', long=True)

K.code('pipeline', r'''
from itertools import islice

LOG = [
    "INFO start",
    "ERROR disk full",
    "INFO saved",
    "ERROR timeout",
    "WARN slow",
    "ERROR disk full",
]


def read_lines(lines):
    for line in lines:
        print("  read:", line)
        yield line


def only_errors(lines):
    for line in lines:
        if line.startswith("ERROR"):
            yield line


def message(lines):
    for line in lines:
        yield line.split(" ", 1)[1]


steps = message(only_errors(read_lines(LOG)))  # nothing is read yet
print("pipeline built")
print(list(islice(steps, 2)))                  # stop after 2 errors
''')

K.code('yieldfrom', r'''
def flatten(items):
    for item in items:
        if isinstance(item, list):
            yield from flatten(item)           # hand over to a smaller generator
        else:
            yield item


print(list(flatten([1, [2, [3, 4]], [], 5])))


def worker():
    total = 0
    for n in [1, 2, 3]:
        yield n
        total += n
    return total                               # becomes StopIteration.value


def boss():
    result = yield from worker()               # yield from also gives back the return value
    print("worker returned", result)
    yield "boss done"


print(list(boss()))
''')

K.code('send', r'''
def running_average():
    total = 0
    count = 0
    average = None
    while True:
        value = yield average                  # send(v) puts v here
        total += value
        count += 1
        average = total / count


avg = running_average()
next(avg)                                      # "prime" it: run to the first yield
print(avg.send(10), avg.send(20), avg.send(60))


def guarded():
    try:
        while True:
            try:
                yield "working"
            except ValueError as err:
                print("handled inside:", err)
    finally:
        print("cleanup runs on close()")


g = guarded()
print(next(g))
print(g.throw(ValueError("bad value")))        # raise an error AT the paused yield
g.close()                                      # GeneratorExit inside, so finally runs
print(next(g, "closed"))
''')

K.code('lazy', r'''
import random

prices = {"tea": 10, "coffee": 25}
names = prices.keys()                          # a live view, not a copy
prices["juice"] = 30
print(list(names))

pairs = zip("abc", [1, 2, 3])                  # zip is an iterator: used once
print(next(pairs), list(pairs), list(pairs))

r = range(0, 10 ** 12, 7)                      # range is lazy AND can be reused
print(len(r), r[3], 21 in r)

for number, word in enumerate(["x", "y"], start=1):
    print(number, word)

random.seed(4)
rolls = iter(lambda: random.randint(1, 6), 6)  # call again and again until it gives 6
print(list(rolls))
print(list(reversed([1, 2, 3])), list(map(abs, [-1, 2])))
''')

K.lesson('idea', 'Iterators and generators: one value at a time', f'''
{src('Python 3.14 glossary (iterable, iterator, generator), the iterator types and yield expressions documentation, inspect.getgeneratorstate, PEP 255, PEP 342, PEP 380, PCAP-31-03 block 5 and PCPP-32-101.')}
{wwh('An <b>iterable</b> is anything you can loop over: a list, a string, a dict, a file, a range. An <b>iterator</b> is the object that walks through it and hands out the next value each time you call next(). A <b>generator</b> is the easiest way to write your own iterator: a normal function that uses <b>yield</b> instead of return.',
     'Building a full list before you use it costs memory and time. A million lines from a log file, an endless stream of sensor readings or every possible password cannot all sit in memory. Often you also only need the first few results. Iterators make values only when asked, so memory stays small and work stops as soon as you stop asking.',
     'Every for loop calls iter() once to get an iterator and then next() again and again until StopIteration is raised. A generator function returns a generator object. Each next() runs its body until the next yield, hands that value out and pauses, keeping all local variables. The next call continues from exactly that spot.')}
{viz('pygen')}
{run('protocol')}
{note('iter(nums) gave a NEW iterator each time, so the first answer was False. An iterator returns itself from iter(), so the second was True. That is the whole difference: an iterable can make many iterators, an iterator is one walk that can be used once.', 'exam')}
''', kw=['iterable', 'iterator', 'iter', 'next', 'StopIteration', 'for loop', 'lazy', 'generator'])

K.lesson('classes', 'Writing iterators as classes', f'''
{run('iterclass')}
{versus('Iterable or iterator', ['', 'iterable (like Shelf, list)', 'iterator (like Countdown)'], [
    ['Has __iter__', 'Yes, returns a NEW iterator', 'Yes, returns itself'],
    ['Has __next__', 'No', 'Yes'],
    ['Loop over it twice', 'Works both times', 'Second loop gets nothing'],
    ['Remembers a position', 'No', 'Yes'],
    ['Examples', 'list, str, dict, range, set', 'iter(list), zip, map, enumerate, files, generators']],
    'give your own containers an __iter__ that returns a fresh iterator (or is a generator), so people can loop over them as often as they like.')}
{note('Raising StopIteration ends the loop. Do not raise it inside a generator body: since Python 3.7 (PEP 479) it is turned into RuntimeError. In a generator, simply return.', 'warn')}
''', kw=['__iter__', '__next__', 'iterator class', 'iterable class', 'exhausted', 'PEP 479'])

K.lesson('generators', 'Generator functions and yield', f'''
{run('yieldfn')}
{note('A function that contains yield anywhere is a generator function. Calling it runs nothing: the first line, print("start"), only ran at the first next(). After the last value the generator is closed, and list() on a used generator gives an empty list.', 'exam')}
{run('infinite')}
{versus('Three ways to produce a sequence', ['', 'return a list', 'iterator class', 'generator function'], [
    ['Lines of code', 'Few', 'Many (__init__, __iter__, __next__)', 'Few'],
    ['Memory for n items', 'Grows with n', 'Constant', 'Constant'],
    ['Can be endless', 'No', 'Yes', 'Yes'],
    ['Stops work early', 'No, everything is made first', 'Yes', 'Yes'],
    ['Use twice, index, len', 'Yes', 'No', 'No']],
    'use a generator function whenever you want to produce values one by one. Return a list only when the caller really needs all the values at once or needs to index them.')}
''', kw=['yield', 'generator function', 'generator object', 'getgeneratorstate', 'infinite generator', 'fibonacci', 'islice', 'memory'])

K.lesson('pipelines', 'Generator pipelines', f'''
{run('pipeline')}
{note('Building the pipeline read nothing. Asking for 2 errors read only 4 lines and never touched "WARN slow" or the last line. Each value travels through all three stages before the next line is read. Unix pipes such as grep | cut | head work the same way.', 'tip')}
{versus('Processing a big file', ['', 'read everything into lists', 'a generator pipeline'], [
    ['Memory', 'The whole file, maybe gigabytes', 'One line at a time'],
    ['First result appears', 'After the whole file is read', 'Right away'],
    ['Stopping early', 'Too late, the work is done', 'No extra work'],
    ['Code', 'One big loop with many ifs', 'Small reusable stages']],
    'chain small generators. Each stage does one job, can be tested alone and reused in another pipeline.')}
''', kw=['pipeline', 'lazy evaluation', 'chaining generators', 'log processing', 'streaming'])

K.lesson('delegation', 'yield from, send, throw and close', f'''
{run('yieldfrom')}
{note('yield from other passes every value of other straight to whoever is asking, and when other finishes, its return value becomes the value of the yield from expression. It is the clean way to split a big generator into smaller ones, and it handles send and throw for you too.', 'tip')}
{run('send')}
{table(['Method', 'What it does'], [
    ['next(g)', 'Run to the next yield and return the value it yields'],
    ['g.send(v)', 'Resume, and make the paused yield expression evaluate to v. The first call must be next(g) or g.send(None)'],
    ['g.throw(exc)', 'Raise exc at the paused yield. The generator may catch it and go on'],
    ['g.close()', 'Raise GeneratorExit at the paused yield so finally blocks run, then mark it closed']])}
{deep('Generators as coroutines', '<p>PEP 342 turned yield into an expression so generators could receive values, which made them simple coroutines. Early asyncio was built on yield from. Modern code uses async def and await (Advanced 5.2), which are coroutines designed for this job, but they follow the same idea of pausing and resuming a function.</p>')}
''', kw=['yield from', 'delegation', 'send', 'throw', 'close', 'GeneratorExit', 'coroutine', 'return value'])

K.lesson('lazy', 'Lazy tools you already use', f'''
{run('lazy')}
{table(['Built in', 'Lazy?', 'Use more than once?'], [
    ['range', 'Yes, works out each value from start, step and index', 'Yes, it is a sequence'],
    ['dict.keys(), values(), items()', 'Yes, live views of the dict', 'Yes'],
    ['zip, map, filter, enumerate, reversed', 'Yes, iterators', 'No'],
    ['open(...) file objects', 'Yes, one line per next()', 'No, unless you seek(0)'],
    ['iter(function, sentinel)', 'Calls function until it returns sentinel', 'No'],
    ['sorted, list, tuple, sum', 'No, they use up the whole input', 'They return a value']])}
{note('A common bug: saving map(...) or zip(...) in a variable, looping over it once for a check, and then finding it empty the second time. Wrap it in list(...) if you need it twice.', 'warn')}
''', kw=['range', 'dict views', 'zip', 'map', 'enumerate', 'reversed', 'iter sentinel', 'lazy built ins'])

K.lesson('maths', 'The maths: memory, early stopping and counting', f'''
{fxs(fx('Memory of a list against a generator', 'list: about 8n bytes of pointers plus the items, generator: a constant (about 200 bytes)', '100,000 squares: the list needs about 800 KB of pointers, the generator stays near 200 bytes.', key=True),
     fx('Work done by a lazy search', 'items read = position of the first match (k), not n', 'Looking for the first even square above 50 in 1, 2, 3, ... reads 8 numbers and stops (8 &times; 8 = 64).', key=True),
     fx('Running average after k values', 'average<sub>k</sub> = (x<sub>1</sub> + x<sub>2</sub> + ... + x<sub>k</sub>) / k', 'After 10, 20 and 60: (10 + 20 + 60) / 3 = 30.'),
     fx('Number of next() calls to see StopIteration', 'values + 1', 'countdown(4) gives 4 values, and the 5th call raises StopIteration.'),
     fx('Subsets and combinations (LeetCode 77 and 90)', 'subsets = 2<sup>n</sup>, combinations of k from n = n! / (k! (n &minus; k)!)', 'From 5 numbers choose 2: 5! / (2! &times; 3!) = 10.'),
     fx('A pipeline of s stages over n items', 'time grows with n &times; s, memory with s only', '10<sup>6</sup> lines through 4 stages: 4 &times; 10<sup>6</sup> stage steps, but only 4 paused generators in memory.'))}
{steps('Worked example: how many lines does the error pipeline read for the first 2 errors?', [
    'Line 1 is INFO: read, dropped.',
    'Line 2 is ERROR: read, passed on, first result.',
    'Line 3 is INFO: read, dropped. Line 4 is ERROR: read, second result, and islice stops asking.',
    eq('4 lines read out of 6')])}
''', kw=['memory', 'early stopping', 'running average', 'combinations', 'subsets', 'pipeline cost'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Loop over lists, strings, dicts and files. Use iter() and next() by hand, and know that StopIteration ends a for loop.</p>',
    '<p>Write generator functions with yield, use them in for loops and with list(), sum() and islice(), and write iterator classes with __iter__ and __next__.</p>',
    '<p>Build generator pipelines, use yield from to delegate and collect return values, and control generators with send, throw and close.</p>',
    '<p>A generator object keeps a suspended frame: its local variables, its position (the last instruction) and its block stack. yield from forwards send and throw to the inner generator. PEP 479 turns StopIteration inside a generator into RuntimeError. These same suspended frames are what async def coroutines are built on.</p>')}
{grow('Use the iterator protocol.', 'Write generators and pipelines.', 'Control and combine generators, and explain suspended frames.')}
''', kw=['beginner', 'expert', 'suspended frame', 'PEP 479'])

TREE = '''

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values):
    """Build a tree from a level order list like [1, 2, 3, None, 4] (helper for the tests)."""
    if not values:
        return None
    nodes = [None if v is None else TreeNode(v) for v in values]
    kids = nodes[1:]
    k = 0
    for node in nodes:
        if node is not None:
            if k < len(kids):
                node.left = kids[k]
            if k + 1 < len(kids):
                node.right = kids[k + 1]
            k += 2
    return nodes[0]
'''

LIST = '''

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_list(values):
    """Build a linked list from a Python list (helper for the tests)."""
    head = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head


def list_values(head):
    """The values of a linked list as a Python list (helper for the tests)."""
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out
'''

lc(94, 'Binary Tree Inorder Traversal', 'binary-tree-inorder-traversal', 'e', 'A recursive generator with yield from', 'Yield everything from the left subtree, then the node, then everything from the right subtree.', r'''
def inorder(node):
    if node:
        yield from inorder(node.left)
        yield node.val
        yield from inorder(node.right)


def inorder_traversal(root):
    return list(inorder(root))
''' + TREE, [('inorder_traversal(build_tree([1, None, 2, 3]))', [1, 3, 2]), ('inorder_traversal(build_tree([]))', [])])
lc(173, 'Binary Search Tree Iterator', 'binary-search-tree-iterator', 'm', 'Keep one generator inside the class', 'An inorder generator of a BST gives the values in sorted order. next takes the next value. To answer hasNext, look one value ahead and remember it.', r'''
class BSTIterator:
    def __init__(self, root):
        self.values = self.walk(root)
        self.ahead = next(self.values, None)

    def walk(self, node):
        if node:
            yield from self.walk(node.left)
            yield node.val
            yield from self.walk(node.right)

    def next(self):
        value = self.ahead
        self.ahead = next(self.values, None)
        return value

    def hasNext(self):
        return self.ahead is not None
''' + TREE, [('(lambda it: [it.next(), it.next(), it.hasNext(), it.next(), it.hasNext(), it.next(), it.hasNext(), it.next(), it.hasNext()])(BSTIterator(build_tree([7, 3, 15, None, None, 9, 20])))', [3, 7, True, 9, True, 15, True, 20, False])])
lc(1305, 'All Elements in Two Binary Search Trees', 'all-elements-in-two-binary-search-trees', 'm', 'Merge two sorted generators', 'Each BST gives a sorted stream with an inorder generator. heapq.merge joins sorted streams lazily, like the merge step of merge sort.', r'''
import heapq


def sorted_values(node):
    if node:
        yield from sorted_values(node.left)
        yield node.val
        yield from sorted_values(node.right)


def get_all_elements(root1, root2):
    return list(heapq.merge(sorted_values(root1), sorted_values(root2)))
''' + TREE, [('get_all_elements(build_tree([2, 1, 4]), build_tree([1, 0, 3]))', [0, 1, 1, 2, 3, 4]), ('get_all_elements(build_tree([1, None, 8]), build_tree([8, 1]))', [1, 1, 8, 8])])
lc(23, 'Merge k Sorted Lists', 'merge-k-sorted-lists', 'h', 'Turn each list into a generator, then heapq.merge', 'A small generator walks one linked list. heapq.merge takes k sorted streams and always hands out the smallest next value, using a heap of size k.', r'''
import heapq


def walk(node):
    while node:
        yield node.val
        node = node.next


def merge_k_lists(lists):
    dummy = tail = ListNode()
    for value in heapq.merge(*[walk(head) for head in lists]):
        tail.next = ListNode(value)
        tail = tail.next
    return dummy.next
''' + LIST, [('list_values(merge_k_lists([build_list([1, 4, 5]), build_list([1, 3, 4]), build_list([2, 6])]))', [1, 1, 2, 3, 4, 4, 5, 6]), ('list_values(merge_k_lists([]))', [])])
lc(77, 'Combinations', 'combinations', 'm', 'A backtracking generator', 'Choose the next number from start to n, yield when k numbers are chosen. itertools.combinations does the same in C.', r'''
def choose(start, n, k, chosen):
    if len(chosen) == k:
        yield list(chosen)
        return
    for number in range(start, n + 1):
        chosen.append(number)
        yield from choose(number + 1, n, k, chosen)
        chosen.pop()


def combine(n, k):
    return list(choose(1, n, k, []))
''', [('combine(4, 2)', [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]), ('combine(1, 1)', [[1]])])
lc(90, 'Subsets II', 'subsets-ii', 'm', 'Sort, then skip equal neighbours', 'Sort first so equal numbers sit together. At each depth, do not start a branch with the same number twice.', r'''
def build_subsets(nums, start, chosen):
    yield list(chosen)
    for i in range(start, len(nums)):
        if i > start and nums[i] == nums[i - 1]:
            continue
        chosen.append(nums[i])
        yield from build_subsets(nums, i + 1, chosen)
        chosen.pop()


def subsets_with_dup(nums):
    return list(build_subsets(sorted(nums), 0, []))
''', [('subsets_with_dup([1, 2, 2])', [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]), ('subsets_with_dup([0])', [[], [0]])])
lc(216, 'Combination Sum III', 'combination-sum-iii', 'm', 'Filter a combinations stream', 'Every answer is a set of k different digits from 1 to 9. Generate the combinations lazily and keep the ones whose sum is n.', r'''
from itertools import combinations


def combination_sum3(k, n):
    result = []
    for combo in combinations(range(1, 10), k):
        if sum(combo) == n:
            result.append(list(combo))
    return result
''', [('combination_sum3(3, 7)', [[1, 2, 4]]), ('combination_sum3(3, 9)', [[1, 2, 6], [1, 3, 5], [2, 3, 4]]), ('combination_sum3(4, 1)', [])])
lc(401, 'Binary Watch', 'binary-watch', 'e', 'Loop over every time, count the lit bits', 'There are only 12 &times; 60 times. For each one count the 1 bits of the hour and the minute with bin(x).count("1").', r'''
def times_with_leds(turned_on):
    for hour in range(12):
        for minute in range(60):
            if bin(hour).count("1") + bin(minute).count("1") == turned_on:
                yield str(hour) + ":" + str(minute).zfill(2)


def read_binary_watch(turnedOn):
    return list(times_with_leds(turnedOn))
''', [('read_binary_watch(1)', ['0:01', '0:02', '0:04', '0:08', '0:16', '0:32', '1:00', '2:00', '4:00', '8:00']), ('read_binary_watch(9)', [])])
lc(1415, 'The k-th Lexicographical String of All Happy Strings of Length n', 'the-k-th-lexicographical-string-of-all-happy-strings-of-length-n', 'm', 'Generate in order, stop at k', 'A generator makes happy strings in alphabetical order. islice jumps to the k-th one without building the rest.', r'''
from itertools import islice


def happy(n, text):
    if len(text) == n:
        yield text
        return
    for ch in "abc":
        if not text or text[-1] != ch:
            yield from happy(n, text + ch)


def get_happy_string(n, k):
    return next(islice(happy(n, ""), k - 1, None), "")
''', [('get_happy_string(1, 3)', 'c'), ('get_happy_string(1, 4)', ''), ('get_happy_string(3, 9)', 'cab')])
lc(119, "Pascal's Triangle II", 'pascals-triangle-ii', 'e', 'A generator of rows', 'Each row is made from the one before: add neighbours and put 1 at both ends. Yield rows one by one and keep the one you need.', r'''
def pascal_rows():
    row = [1]
    while True:
        yield row
        middle = []
        for i in range(len(row) - 1):
            middle.append(row[i] + row[i + 1])
        row = [1] + middle + [1]


def get_row(rowIndex):
    for index, row in enumerate(pascal_rows()):
        if index == rowIndex:
            return row
''', [('get_row(3)', [1, 3, 3, 1]), ('get_row(0)', [1]), ('get_row(5)', [1, 5, 10, 10, 5, 1])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Every solution here is written with generators: tree walks with yield from, sorted streams joined lazily with heapq.merge, backtracking that yields each answer, and searches that stop at the k-th value with islice.</p>'), kw=['LeetCode', 'generator', 'yield from', 'heapq.merge', 'backtracking', 'islice'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'An iterable can give an iterator with iter(). An iterator gives values with next() and raises StopIteration at the end.',
    'A for loop is iter() once plus next() until StopIteration.',
    'An iterator class has __iter__ returning self and __next__. An iterable class returns a fresh iterator, so it can be looped over many times.',
    'A function with yield returns a generator. Each next() runs to the next yield and pauses, keeping its local variables.',
    'Generators use constant memory, can be endless and stop work early. Chain them into pipelines.',
    'yield from delegates to another generator and returns its return value. send, throw and close control a paused generator.',
    'range and dict views are lazy and reusable. zip, map, filter, enumerate and files are one shot iterators.'],
    '2.2 shows itertools and functools, the standard toolbox for working with iterators.')}
{files('Three tasks: a chunked generator, a reusable FloatRange iterable, and a running average coroutine driven with send.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does iter([1, 2]) return?', ['The list itself', 'A list iterator', 'The number 1', 'A generator function'], 1, 'Ask for an iterator.', 'It returns a new list_iterator object that walks the list.')
K.quiz('e', 'What happens when next() is called on a used up iterator with no default?', ['It returns None', 'It raises StopIteration', 'It starts again', 'It returns -1'], 1, 'The end signal.', 'StopIteration is how an iterator says it is finished.')
K.quiz('e', 'What makes a function a generator function?', ['Its name starts with gen', 'It contains yield', 'It returns a list', 'It uses while True'], 1, 'One keyword.', 'Any yield in the body makes it a generator function.')
K.quiz('m', 'g = countdown(3), where countdown prints "start" on its first line. What is printed by this line alone?', ['start', 'Nothing', '3', 'An error'], 1, 'Calling creates the generator.', 'The body only starts at the first next(g).')
K.quiz('m', 'z = zip("ab", [1, 2]). list(z) is [("a", 1), ("b", 2)]. What is list(z) the second time?', ['The same list', '[]', 'An error', '[("a", 1)]'], 1, 'One shot iterator.', 'zip is an iterator, so it is used up after the first list().')
K.quiz('m', 'Which object can be looped over many times?', ['map(str, [1, 2])', 'range(5)', 'iter([1, 2])', '(x for x in [1, 2])'], 1, 'Lazy but a sequence.', 'range is a sequence. The others are one shot iterators.')
K.quiz('m', 'What does yield from inner() do?', ['Yields the generator object once', 'Yields every value of inner() and evaluates to its return value', 'Calls inner() in a thread', 'Returns from the outer function'], 1, 'Delegation.', 'It passes each value through and gives back the return value at the end.')
K.quiz('m', 'Why must you call next(g) before the first g.send(10)?', ['send needs a warm up of the CPU', 'The generator must be paused at a yield to receive a value', 'next sets the default value', 'You do not need to'], 1, 'Priming.', 'A just created generator is not at a yield yet, so send with a non None value raises TypeError.')
K.quiz('h', 'A generator body raises StopIteration directly in Python 3.14. What does the caller see?', ['A normal end of iteration', 'RuntimeError', 'ValueError', 'Nothing'], 1, 'PEP 479.', 'StopIteration inside a generator is turned into RuntimeError. Use return instead.')
K.quiz('h', 'What does g.close() do to a generator paused inside try/finally?', ['Nothing', 'Raises GeneratorExit at the yield, so the finally block runs', 'Deletes the code', 'Raises StopIteration in the caller'], 1, 'Cleanup.', 'GeneratorExit lets finally blocks and with blocks clean up.')
K.quiz('h', 'In the error pipeline, why were "WARN slow" and the last line never read?', ['They were filtered out', 'islice stopped asking after 2 results, and nothing is read until asked', 'Generators skip lines', 'The list was too short'], 1, 'Pull, not push.', 'Each stage only works when the next stage asks for a value.')
K.quiz('x', 'In the style of an MIT 6.101 exam: which uses constant extra memory for any n?', ['sum([i * i for i in range(n)])', 'sum(i * i for i in range(n))', 'sum(list(map(lambda i: i * i, range(n))))', 'sorted(range(n))[-1]'], 1, 'No list in the middle.', 'Only the generator expression avoids building a list of n items.')
K.quiz('x', 'In the style of a Cambridge Tripos question: f is a generator that yields 1, 2, 3 and then returns 10. What is list(f())?', ['[1, 2, 3, 10]', '[1, 2, 3]', '[10]', 'An error'], 1, 'Where the return value goes.', 'The return value travels in StopIteration.value, which list() ignores. Only yield from collects it.')

K.calc('e', 'How many values does list(countdown(3)) contain?', '3', 'One per yield.', ['n = 3 yields 3.', 'Then 2, then 1.', eq('3 values')], check=3)
K.calc('e', 'What is sum(x * x for x in range(1, 4))?', '14', '1 + 4 + 9.', ['1 &times; 1 = 1.', '2 &times; 2 = 4 and 3 &times; 3 = 9.', eq('1 + 4 + 9 = 14')], check=sum(x * x for x in range(1, 4)))
K.calc('e', 'countdown(4) gives 4 values. On which call of next() is StopIteration raised?', '5', 'Values plus 1.', ['Calls 1 to 4 return 4, 3, 2, 1.', 'The body then ends.', eq('Call 5 raises StopIteration')], check=5)
K.calc('m', 'How many lists does combine(5, 2) return?', '10', '5! / (2! &times; 3!).', ['5! = 120.', '2! &times; 3! = 2 &times; 6 = 12.', eq('120 / 12 = 10')], check=10)
K.calc('m', 'How many subsets does a list of 4 different numbers have?', '16', '2<sup>n</sup>.', ['Each number is in or out: 2 choices.', '4 numbers: 2 &times; 2 &times; 2 &times; 2.', eq('16')], check=2 ** 4)
K.calc('m', 'A lazy search walks 1, 2, 3, ... and stops at the first even number whose square is above 50. How many numbers does it read?', '8', 'Squares of even numbers.', ['2, 4 and 6 give 4, 16 and 36, all at most 50.', '8 gives 64, which is above 50.', eq('8 numbers read (1 to 8)')], check=8)
K.calc('m', 'running_average receives 10, 20 and 60. What does the third send return?', '30', 'Total over count.', ['Total = 10 + 20 + 60 = 90.', 'Count = 3.', eq('90 / 3 = 30')], check=(10 + 20 + 60) / 3)
K.calc('h', 'fibonacci() yields 0, 1, 1, 2, 3, ... How many of its values are below 100?', '12', 'List them.', ['0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89.', 'The next one is 144.', eq('12 values')], check=12)
K.calc('h', 'How many happy strings of length 4 exist? (First letter: 3 choices, each next letter: 2.)', '24', '3 &times; 2<sup>n &minus; 1</sup>.', ['First letter: 3 choices.', 'Each of the other 3 letters: 2 choices, so 2<sup>3</sup> = 8.', eq('3 &times; 8 = 24')], check=3 * 2 ** 3)
K.calc('x', 'In the style of a Princeton COS 226 exam: 10<sup>6</sup> log lines flow through a pipeline of 4 generator stages, each doing one step per line it receives. Only 1 line in 1000 passes the first stage. How many stage steps in total?', '1003000', 'Count each stage.', ['Stage 1 sees all 10<sup>6</sup> lines.', 'Stages 2, 3 and 4 each see 10<sup>6</sup> / 1000 = 1000 lines.', eq('1,000,000 + 3 &times; 1000 = 1,003,000')], check=10 ** 6 + 3 * 1000)

K.assign('chunked', 'e', 'Split items into chunks with a generator',
         '<p>Write a generator function <code>chunked(items, size)</code> that yields lists of <code>size</code> items in order. The last chunk may be shorter. It must work for any iterable, including another generator, and must not build all chunks at once.</p>',
         '''
import inspect


def chunked(items, size):
    return [list(items)]
''', [('list(chunked(range(7), 3))', [[0, 1, 2], [3, 4, 5], [6]]), ('list(chunked([], 2))', []), ('inspect.isgenerator(chunked([1], 1))', True), ('list(chunked((x * x for x in range(4)), 2))', [[0, 1], [4, 9]])],
         '''
import inspect


def chunked(items, size):
    chunk = []
    for item in items:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
''', 'Collect items in a list. When it reaches size, yield it and start a new list. After the loop, yield what is left if it is not empty.', '<p>Because chunked only loops once over items, it works with generators and endless streams too, which slicing (items[i:i + size]) cannot do.</p>')
K.assign('floatrange', 'm', 'A FloatRange you can loop over again and again',
         '<p>Write a class <code>FloatRange(start, stop, step)</code> that is an iterable (not a one shot iterator): every loop gives start, start + step, start + 2 &times; step, ... while the value is below stop. Work out each value as start + i &times; step so that rounding errors do not add up, and round it to 10 places.</p>',
         '''
class FloatRange:
    def __init__(self, start, stop, step):
        self.start = start
        self.stop = stop
        self.step = step
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += self.step
        return value
''', [('list(FloatRange(0, 1, 0.25))', [0.0, 0.25, 0.5, 0.75]), ('(lambda r: (list(r), list(r)))(FloatRange(0, 3, 1))', [[0, 1, 2], [0, 1, 2]]), ('list(FloatRange(0, 1, 0.1))[-1]', 0.9), ('len(list(FloatRange(5, 5, 1)))', 0)],
         '''
class FloatRange:
    def __init__(self, start, stop, step):
        self.start = start
        self.stop = stop
        self.step = step

    def __iter__(self):
        i = 0
        while True:
            value = round(self.start + i * self.step, 10)
            if value >= self.stop:
                return
            yield value
            i += 1
''', 'Make __iter__ a generator method. Each call of __iter__ then starts a new generator with its own i.', '<p>Writing __iter__ as a generator is the shortest way to make a reusable iterable. Adding 0.1 ten times gives 0.9999999999999999, which is why each value is computed from i instead.</p>')
K.assign('averager', 'h', 'A running average coroutine',
         '<p>Write a generator <code>running_stats()</code> that you prime with next() and then feed numbers with send(). After each number it yields a tuple (count, average), with the average rounded to 2 places. Sending None resets it: count goes back to 0 and it yields (0, None).</p>',
         '''
def running_stats():
    yield
''', [('(lambda g: (next(g), [g.send(v) for v in [10, 20, 60]])[1])(running_stats())', [[1, 10.0], [2, 15.0], [3, 30.0]]), ('(lambda g: (next(g), g.send(5), g.send(None), g.send(7))[1:])(running_stats())', [[1, 5.0], [0, None], [1, 7.0]]), ('(lambda g: (next(g), g.send(1), g.send(2))[2])(running_stats())', [2, 1.5])],
         '''
def running_stats():
    total = 0
    count = 0
    result = None
    while True:
        value = yield result
        if value is None:
            total = 0
            count = 0
            result = (0, None)
        else:
            total += value
            count += 1
            result = (count, round(total / count, 2))
''', 'Keep total and count in local variables. value = yield result both hands out the last answer and receives the next number.', '<p>The local variables survive between sends because the generator frame stays paused, which is exactly what a coroutine is.</p>')

K.must('Iterator protocol', 'iter(x) gives an iterator. next(it) gives a value or raises StopIteration. next(it, default) avoids the error. A for loop does this for you.')
K.must('Iterable versus iterator', 'Iterables (list, range, dict) give a fresh iterator each time. Iterators (zip, map, files, generators) are used up after one pass.')
K.must('Generators', 'A function with yield returns a generator. Nothing runs until next(). It pauses at each yield and keeps its locals. Return ends it.')
K.must('Pipelines and laziness', 'Chain generators: values are made only when asked, memory stays constant, and islice or break stops work early.')
K.must('Advanced control', 'yield from delegates and returns the inner return value. send(v), throw(e), close() (GeneratorExit). Prime with next() before send.')

T = K.topic(
    slug='py-generators', topic='py-generators', step=(2, 'Iterators, generators and context managers', 'py-a2', 'Work with data one value at a time, use the itertools and functools toolbox, and manage resources safely with with.', 'Advanced'),
    title='Iterators and generators', short='Generators', badge='2.1', minutes=75,
    lead='Make values only when they are needed. Learn the iterator protocol behind every for loop, iterable and iterator classes, generator functions with yield, endless generators, generator pipelines, yield from, send, throw and close, and the lazy tools already built into Python.',
    desc='iterables and iterators, iter and next, StopIteration, how a for loop works, __iter__ and __next__, PEP 479, generator functions and yield, inspect.getgeneratorstate, infinite generators with islice, memory of lists and generators, generator pipelines, yield from and return values, send, throw, close and GeneratorExit, range, dict views, zip, map, enumerate, reversed, iter with a sentinel.',
    summary='iterator protocol, iterator classes, yield, pipelines, yield from, send, throw, close, lazy built ins.',
    keywords=['iterator', 'iterable', 'generator', 'yield', 'next', 'StopIteration', 'yield from', 'send', 'pipeline', 'lazy', 'PCAP'],
    recap='<p>Ask for values one at a time: iterators give them, generators make writing iterators easy, and pipelines keep memory flat.</p>',
    added='2026-11-07', leet=leet_items())
