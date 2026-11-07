# Core Python 3.2: lists. Follows PCEP-30-02 section 3.1 (lists: constructing vectors, indexing and slicing, the
# len() function, list methods append(), insert(), index(), del, iterating through lists with the for loop,
# initializing loops, in and not in operators, list comprehensions, copying and cloning, lists in lists: matrices and
# cubes) and section 3.1's sorting (the bubble sort), checked against the Python 3.14 tutorial section 5.1 and the
# CPython 3.14 source of listobject.c for the growth rule.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-lists')
K = Kit()

K.code('make', r'''
marks = [72, 45, 91, 38]
mixed = ["Asha", 21, 5.8, True]     # a list can hold any types
empty = []
letters = list("abc")               # list() turns any iterable into a list
numbers = list(range(1, 6))
print(marks, mixed, empty, letters, numbers)
print(len(marks), marks[0], marks[-1], marks[1:3])
print(91 in marks, 50 not in marks)
print(min(marks), max(marks), sum(marks), sum(marks) / len(marks))
''')

K.code('change', r'''
fruits = ["apple", "mango"]
fruits.append("banana")          # add one item at the end
print(fruits)
fruits.insert(1, "kiwi")         # add at position 1, the rest move right
print(fruits)
fruits.extend(["fig", "plum"])   # add every item of another list
print(fruits)
fruits[0] = "grape"              # replace one item
print(fruits)
fruits[1:3] = ["lime"]           # replace a slice, the list can shrink
print(fruits)
''')

K.code('remove', r'''
nums = [10, 20, 30, 20, 40]
nums.remove(20)          # removes the first 20 only
print(nums)
last = nums.pop()        # removes and returns the last item
print(last, nums)
first = nums.pop(0)      # removes and returns the item at index 0
print(first, nums)
del nums[0]              # del removes by index and returns nothing
print(nums)
nums.clear()
print(nums)
try:
    nums.remove(99)
except ValueError as err:
    print("ValueError:", err)
''')

K.code('search', r'''
colours = ["red", "green", "blue", "green"]
print(colours.index("green"))      # first position
print(colours.count("green"))      # how many times
print("pink" in colours)
try:
    colours.index("pink")
except ValueError as err:
    print("ValueError:", err)
''')

K.code('sort', r'''
nums = [5, 2, 9, 1, 7]
nums.sort()                      # changes the list, returns None
print(nums)
nums.sort(reverse=True)
print(nums)

words = ["banana", "Apple", "cherry", "fig"]
print(sorted(words))                    # new list, upper case first
print(sorted(words, key=str.lower))     # ignore case
print(sorted(words, key=len))           # shortest first, ties keep their order
print(words)                            # sorted() did not change words

result = nums.sort()
print(result)                           # a common mistake: sort() gives None
nums.reverse()
print(nums)
''')

K.code('alias', r'''
a = [1, 2, 3]
b = a            # b is another name for the same list
b.append(4)
print(a, b, a is b)

c = a[:]         # a copy (also a.copy() or list(a))
c.append(5)
print(a, c, a is c, a == c)

def add_item(items):
    items.append("new")      # changes the caller's list

shop = ["milk"]
add_item(shop)
print(shop)
''')

K.code('deep', r'''
import copy

grid = [[1, 2], [3, 4]]
shallow = grid.copy()          # new outer list, same inner lists
deep = copy.deepcopy(grid)     # copies everything
grid[0][0] = 99
print(shallow)                 # changed too
print(deep)                    # safe

bad = [[0] * 3] * 3            # three names for one inner list
bad[0][0] = 1
print(bad)
good = [[0] * 3 for _ in range(3)]
good[0][0] = 1
print(good)
''')

K.code('matrix', r'''
matrix = [
    [1, 2, 3],
    [4, 5, 6],
]
print(matrix[1][2])            # row 1, column 2
for row in matrix:
    for value in row:
        print(value, end=" ")
    print()

rows = len(matrix)
cols = len(matrix[0])
turned = []                    # transpose: rows become columns
for c in range(cols):
    new_row = []
    for r in range(rows):
        new_row.append(matrix[r][c])
    turned.append(new_row)
print(turned)
''')

K.code('bubble', r'''
def bubble_sort(items):
    items = items[:]                 # work on a copy
    n = len(items)
    for done in range(n - 1):
        swapped = False
        for i in range(n - 1 - done):
            if items[i] > items[i + 1]:
                items[i], items[i + 1] = items[i + 1], items[i]
                swapped = True
        print("after pass", done + 1, items)
        if not swapped:              # already sorted, stop early
            break
    return items

print(bubble_sort([5, 1, 4, 2, 8]))
''')

K.code('unpack', r'''
point = [3, 7]
x, y = point                     # unpack two items
print(x, y)
first, *rest = [10, 20, 30, 40]  # star takes the rest as a list
print(first, rest)
*start, last = "python"
print(start, last)
x, y = y, x                      # swap without a third name
print(x, y)
squares = [n * n for n in range(1, 6)]     # a list comprehension (more in Core 4.3)
evens = [n for n in range(10) if n % 2 == 0]
print(squares, evens)
''')

K.code('growth', r'''
import sys
items = []
last_size = sys.getsizeof(items)
print("empty list:", last_size, "bytes")
for i in range(20):
    items.append(i)
    size = sys.getsizeof(items)
    if size != last_size:
        print("after", len(items), "items the list grew to", size, "bytes")
        last_size = size
''')

K.lesson('idea', 'What a list is', f'''
{src('Python 3.14 tutorial section 5.1 and PCEP-30-02 section 3.1.')}
{wwh('A <b>list</b> is an ordered collection of items in square brackets, such as [72, 45, 91]. The items can be of any type and a list can change: you can add, remove and replace items.',
     'With one variable per value, 500 student marks would need 500 names. A list keeps all of them under one name, keeps their order, and lets a loop visit each one. It is the most used collection in Python.',
     'Like a string, each item has an index from 0, and you can slice. Unlike a string, a list is <b>mutable</b>: methods such as append and sort change the list itself. In CPython a list is an array of references to objects, with some spare room at the end so adding is fast.')}
{scene('a shopping list on the fridge', '<p>Your family keeps one shopping list on the fridge. Anyone can add "milk" at the bottom (append), squeeze "eggs" in at the top (insert), cross out "sugar" (remove) or put it in shop order (sort). Everyone looks at the same paper, so a change by one person is seen by all. That last point is exactly how two names for one Python list behave.</p>')}
{run('make')}
''', kw=['list', 'mutable', 'square brackets', 'len', 'min max sum', 'in'])

K.lesson('change', 'Adding and changing items', f'''
{run('change')}
{table(['Method', 'What it does', 'Cost'], [
    ['append(x)', 'Add x at the end', 'O(1) on average'],
    ['insert(i, x)', 'Add x before index i, the rest move right', 'O(n)'],
    ['extend(items)', 'Add every item of another iterable at the end', 'O(k) for k new items'],
    ['items[i] = x', 'Replace one item', 'O(1)'],
    ['items[a:b] = other', 'Replace a slice with any number of items', 'O(n)']])}
{note('append adds one item, even if that item is a list. [1, 2].append([3, 4]) gives [1, 2, [3, 4]]. extend adds the items one by one and gives [1, 2, 3, 4].', 'exam')}
''', kw=['append', 'insert', 'extend', 'replace item', 'slice assignment', 'append vs extend'])

K.lesson('remove', 'Removing items', f'''
{run('remove')}
{table(['Way', 'Removes', 'Gives back', 'If missing'], [
    ['remove(x)', 'The first item equal to x', 'None', 'ValueError'],
    ['pop()', 'The last item', 'The item', 'IndexError on an empty list'],
    ['pop(i)', 'The item at index i', 'The item', 'IndexError'],
    ['del items[i] or del items[a:b]', 'By index or slice', 'Nothing (it is a statement)', 'IndexError for a single index'],
    ['clear()', 'Everything', 'None', 'Never fails']])}
{note('Do not remove items from a list while a for loop is walking over it. The loop skips the item after each removal. Loop over a copy (for x in items[:]) or build a new list instead.', 'warn')}
''', kw=['remove', 'pop', 'del', 'clear', 'ValueError', 'IndexError', 'remove while looping'])

K.lesson('search', 'Finding items', f'''
{run('search')}
{note('x in items checks each item from the left until it finds a match, so it takes O(n) time. For many lookups in a big collection use a set or a dict (Core 3.3 and 3.4), which answer in O(1) on average.', 'tip')}
''', kw=['index', 'count', 'in', 'linear search', 'O(n)'])

K.lesson('sort', 'Sorting: sort() and sorted()', f'''
{run('sort')}
{versus('Two ways to sort', ['', 'items.sort()', 'sorted(items)'], [
    ['Changes the original', 'Yes', 'No'],
    ['Returns', 'None', 'A new list'],
    ['Works on', 'Lists only', 'Any iterable: tuples, strings, sets, dict keys'],
    ['Options', 'key=..., reverse=True', 'key=..., reverse=True']],
    'use sorted() when you want to keep the original, sort() when you do not need it and want to save memory.')}
{deep('Timsort and stability', '<p>Python sorts with Timsort (Powersort since Python 3.11), which finds runs that are already in order and merges them. It takes O(n log n) time in the worst case and O(n) when the data is already sorted. It is <b>stable</b>: items with equal keys keep their old order. That is why sorted(words, key=len) keeps "banana" before "cherry": both have 6 letters and "banana" came first.</p>')}
''', kw=['sort', 'sorted', 'key', 'reverse', 'stable sort', 'Timsort', 'None'])

K.lesson('alias', 'Names, aliases and copies', f'''
{viz('pylist')}
{run('alias')}
{wwh('A variable does not hold the list. It holds a <b>reference</b> to the list. b = a gives the same list a second name (an <b>alias</b>).',
     'Copying a big list each time you pass it around would waste time and memory. Sharing is fast and lets a function change a list for its caller.',
     'Use a[:], a.copy() or list(a) when you really want a second, separate list. Use is to check if two names point to the same object, and == to check if two lists have equal items.')}
''', kw=['alias', 'reference', 'copy', 'a[:]', 'is vs ==', 'mutable argument'])

K.lesson('deep', 'Shallow copy, deep copy and lists of lists', f'''
{run('deep')}
{table(['Way', 'New outer list', 'New inner lists'], [
    ['b = a', 'No', 'No'],
    ['a[:], a.copy(), list(a)', 'Yes', 'No (shallow copy)'],
    ['copy.deepcopy(a)', 'Yes', 'Yes, at every level']])}
{note('[[0] * 3] * 3 makes one inner list and three references to it, so changing one row changes all three. Build a grid with a comprehension: [[0] * 3 for _ in range(3)].', 'exam')}
''', kw=['shallow copy', 'deep copy', 'deepcopy', 'nested list', '2D list bug'])

K.lesson('matrix', 'Lists in lists: matrices', f'''
{run('matrix')}
{fxs(fx('Item of a matrix', 'matrix[row][col]', 'The first index picks the row, the second the column.', key=True),
     fx('Transpose', 'T[c][r] = M[r][c]', 'An r &times; c matrix becomes c &times; r.'),
     fx('Number of items', 'rows &times; cols', 'A 3D list (a cube) has rows &times; cols &times; depth items.'))}
''', kw=['matrix', '2D list', 'nested list', 'transpose', 'cube', 'rows columns'])

K.lesson('bubble', 'Bubble sort, step by step', f'''
{run('bubble')}
{wwh('<b>Bubble sort</b> walks through the list and swaps any two neighbours that are in the wrong order. After each pass the largest item left "bubbles" to the end.',
     'It is the easiest sort to understand, which is why the PCEP exam asks about it. It shows the ideas behind every sort: compare, swap, and repeat until nothing is out of order.',
     'Pass k compares n &minus; 1 &minus; k pairs. If a whole pass makes no swap, the list is sorted and we stop.')}
{fxs(fx('Comparisons in the worst case', '(n &minus; 1) + (n &minus; 2) + ... + 1 = n(n &minus; 1)/2', '5 items need at most 10 comparisons, 1,000 items about 500,000. That is O(n<sup>2</sup>).', key=True),
     fx('Best case with the early stop', 'n &minus; 1 comparisons', 'An already sorted list needs one pass.'))}
{note('Never use bubble sort in real code. sorted() is far faster. Learn it to understand sorting and to answer exam questions.', 'tip')}
''', kw=['bubble sort', 'swap', 'pass', 'O(n^2)', 'early stop', 'PCEP sorting'])

K.lesson('unpack', 'Unpacking, swapping and a first look at comprehensions', f'''
{run('unpack')}
{note('The number of names must match the number of items, unless one name has a star. a, b = [1, 2, 3] raises ValueError: too many values to unpack.', 'exam')}
''', kw=['unpacking', 'star unpacking', 'swap', 'list comprehension', 'ValueError too many values'])

K.lesson('growth', 'How CPython makes append fast', f'''
{viz('pygrow')}
{run('growth')}
{wwh('A CPython list keeps a block of memory with more slots than it needs right now. len() is the number of slots in use, and the <b>capacity</b> is the number of slots it has.',
     'If the list grew by exactly one slot on every append, each append would copy every item into new memory: n appends would cost about n<sup>2</sup>/2 copies.',
     'When the list is full, CPython grows the capacity to about 1.125 times the new length plus a little (the rule in listobject.c is new = (n + n // 8 + 6) rounded down to a multiple of 4). Copies happen rarely, so the average cost of one append is O(1). This is called <b>amortised</b> O(1).')}
''', kw=['capacity', 'amortised', 'append O(1)', 'over allocation', 'sys.getsizeof', 'listobject.c'])

K.lesson('versus', 'Lists compared with other collections', f'''
{versus('Which collection to choose', ['', 'list', 'tuple', 'set', 'dict'], [
    ['Order kept', 'Yes', 'Yes', 'No', 'Yes (insertion order)'],
    ['Can change', 'Yes', 'No', 'Yes', 'Yes'],
    ['Repeats allowed', 'Yes', 'Yes', 'No', 'Keys no, values yes'],
    ['Find an item', 'O(n)', 'O(n)', 'O(1) average', 'O(1) average by key'],
    ['Written as', '[1, 2]', '(1, 2)', '{{1, 2}}', '{{"a": 1}}'],
    ['Best for', 'A changing sequence', 'A fixed record', 'Unique items and membership', 'Looking up a value by a key']],
    'start with a list. Switch to a tuple when the data must not change, a set when you test membership often, and a dict when you look things up by name.')}
{table(['Operation', 'Time'], [
    ['items[i], items[i] = x, len, append, pop()', 'O(1)'],
    ['insert(0, x), pop(0), remove(x), x in items, index(x)', 'O(n)'],
    ['sort(), sorted()', 'O(n log n)'],
    ['items[a:b] (copy of k items)', 'O(k)']])}
{note('pop(0) and insert(0, x) move every other item. For a queue that adds at one end and removes at the other, use collections.deque, which does both in O(1) (Advanced 4.2).', 'tip')}
''', kw=['list vs tuple', 'list vs set', 'time complexity', 'deque', 'choose collection'])

K.lesson('maths', 'The maths of lists', f'''
{fxs(fx('Average cost of an append (amortised)', '(n + total copies) / n &lt; a small constant', 'With growth by a factor g &gt; 1 the copies form a geometric series n/g + n/g<sup>2</sup> + ... &lt; n/(g &minus; 1).', key=True),
     fx('Bubble sort comparisons', 'n(n &minus; 1)/2', 'The same sum as the triangle loop of Core 2.2.', key=True),
     fx('Number of slices items[a:b] with a &lt; b', 'C(n + 1, 2) = n(n + 1)/2', 'Choose 2 of the n + 1 cut points.'),
     fx('Mean of a list', 'sum(items) / len(items)', 'Undefined for an empty list: guard against ZeroDivisionError.'),
     fx('Binary search steps on a sorted list', '&lfloor;log<sub>2</sub> n&rfloor; + 1', 'A sorted list of 1,000,000 items needs at most 20 checks with bisect (Advanced 4.2).'))}
{steps('Worked example: total copies for 1,000 appends with doubling', [
    'With doubling, copies happen when the list has 1, 2, 4, 8, ..., 512 items.',
    'The copies add up to 1 + 2 + 4 + ... + 512.',
    eq('2<sup>10</sup> &minus; 1 = 1,023 copies, about 1 per append'),
    'CPython grows by about 1.125 instead of 2, which uses less memory and may copy up to about 8 items per append on average. Still a constant, so still O(1).'])}
''', kw=['amortised analysis', 'geometric series', 'bubble sort maths', 'binary search', 'mean'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A list holds many items in order under one name. Use index and slice to read, append to add, and a for loop to visit every item.</p>',
    '<p>Lists change in place. Know append vs extend, remove vs pop vs del, sort vs sorted, and that b = a shares one list. Copy with a[:].</p>',
    '<p>Copies are shallow unless you use deepcopy. Never build a grid with [[0] * n] * n. Know the cost of each method and choose deque, set or dict when a list is slow.</p>',
    '<p>A CPython list is a dynamic array of PyObject pointers with geometric over allocation, giving amortised O(1) append. Sorting uses an adaptive, stable merge sort (Timsort, with the Powersort merge policy since 3.11). Comparison sorts cannot beat &Omega;(n log n) comparisons in the worst case, because n! orders need log<sub>2</sub>(n!) yes or no answers to tell apart.</p>')}
{grow('Make lists, read items with index and slice, add with append and loop over them.',
      'Use every list method correctly, copy lists safely, work with 2D lists and write bubble sort by hand.',
      'Explain references, shallow and deep copies, the cost of each operation and the amortised analysis of append.')}
''', kw=['beginner', 'expert', 'dynamic array', 'lower bound sorting', 'Powersort'])

lc(1929, 'Concatenation of Array', 'concatenation-of-array', 'e', 'List repetition', 'The answer is the list followed by itself.', r'''
def get_concatenation(nums):
    return nums + nums
''', [('get_concatenation([1, 2, 1])', [1, 2, 1, 1, 2, 1]), ('get_concatenation([5])', [5, 5])])
lc(66, 'Plus One', 'plus-one', 'e', 'Walk from the right with a carry', 'Start at the last digit. A 9 becomes 0 and the carry moves left. If every digit was 9, put a 1 in front.', r'''
def plus_one(digits):
    digits = digits[:]
    i = len(digits) - 1
    while i >= 0:
        if digits[i] < 9:
            digits[i] = digits[i] + 1
            return digits
        digits[i] = 0
        i = i - 1
    return [1] + digits
''', [('plus_one([1, 2, 3])', [1, 2, 4]), ('plus_one([9, 9])', [1, 0, 0]), ('plus_one([0])', [1])])
lc(27, 'Remove Element', 'remove-element', 'e', 'Two pointers (read and write)', 'Keep a write position. Copy every item that is not val to the write position. Return how many you kept.', r'''
def remove_element(nums, val):
    write = 0
    for read in range(len(nums)):
        if nums[read] != val:
            nums[write] = nums[read]
            write = write + 1
    return write
''', [('remove_element([3, 2, 2, 3], 3)', 2), ('remove_element([0, 1, 2, 2, 3, 0, 4, 2], 2)', 5)])
lc(26, 'Remove Duplicates from Sorted Array', 'remove-duplicates-from-sorted-array', 'e', 'Two pointers', 'The list is sorted, so repeats sit next to each other. Write an item only when it differs from the last one written.', r'''
def remove_duplicates(nums):
    if not nums:
        return 0
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[write - 1]:
            nums[write] = nums[read]
            write = write + 1
    return write
''', [('remove_duplicates([1, 1, 2])', 2), ('remove_duplicates([0, 0, 1, 1, 1, 2, 2, 3, 3, 4])', 5)])
lc(283, 'Move Zeroes', 'move-zeroes', 'e', 'Two pointers', 'Move every non zero item forward to a write position, then fill the rest with zeros.', r'''
def move_zeroes(nums):
    write = 0
    for x in nums:
        if x != 0:
            nums[write] = x
            write = write + 1
    for i in range(write, len(nums)):
        nums[i] = 0
    return nums
''', [('move_zeroes([0, 1, 0, 3, 12])', [1, 3, 12, 0, 0]), ('move_zeroes([0])', [0])])
lc(121, 'Best Time to Buy and Sell Stock', 'best-time-to-buy-and-sell-stock', 'e', 'Running minimum', 'Keep the lowest price so far. Each day, check the profit if you sold today.', r'''
def max_profit(prices):
    lowest = prices[0]
    best = 0
    for price in prices:
        if price < lowest:
            lowest = price
        if price - lowest > best:
            best = price - lowest
    return best
''', [('max_profit([7, 1, 5, 3, 6, 4])', 5), ('max_profit([7, 6, 4, 3, 1])', 0)])
lc(88, 'Merge Sorted Array', 'merge-sorted-array', 'e', 'Three pointers from the back', 'Fill nums1 from its end. Each time place the bigger of the two last items.', r'''
def merge(nums1, m, nums2, n):
    i = m - 1
    j = n - 1
    k = m + n - 1
    while j >= 0:
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[k] = nums1[i]
            i = i - 1
        else:
            nums1[k] = nums2[j]
            j = j - 1
        k = k - 1
    return nums1
''', [('merge([1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3)', [1, 2, 2, 3, 5, 6]), ('merge([0], 0, [1], 1)', [1])])
lc(118, "Pascal's Triangle", 'pascals-triangle', 'e', 'Build each row from the one above', 'Each row starts and ends with 1. Every inner number is the sum of the two numbers above it.', r'''
def generate(num_rows):
    triangle = []
    for r in range(num_rows):
        row = [1] * (r + 1)
        for c in range(1, r):
            row[c] = triangle[r - 1][c - 1] + triangle[r - 1][c]
        triangle.append(row)
    return triangle
''', [('generate(5)', [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]]), ('generate(1)', [[1]])])
lc(189, 'Rotate Array', 'rotate-array', 'm', 'Three reversals', 'Reverse the whole list, then reverse the first k items and the rest. Use k % n first.', r'''
def reverse_part(nums, left, right):
    while left < right:
        nums[left], nums[right] = nums[right], nums[left]
        left = left + 1
        right = right - 1


def rotate(nums, k):
    n = len(nums)
    k = k % n
    reverse_part(nums, 0, n - 1)
    reverse_part(nums, 0, k - 1)
    reverse_part(nums, k, n - 1)
    return nums
''', [('rotate([1, 2, 3, 4, 5, 6, 7], 3)', [5, 6, 7, 1, 2, 3, 4]), ('rotate([-1, -100, 3, 99], 2)', [3, 99, -1, -100]), ('rotate([1, 2], 3)', [2, 1])])
lc(75, 'Sort Colors', 'sort-colors', 'm', 'Dutch national flag (three pointers)', 'Keep low, mid and high. A 0 swaps to low, a 2 swaps to high, a 1 just moves mid on.', r'''
def sort_colors(nums):
    low = 0
    mid = 0
    high = len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low = low + 1
            mid = mid + 1
        elif nums[mid] == 1:
            mid = mid + 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high = high - 1
    return nums
''', [('sort_colors([2, 0, 2, 1, 1, 0])', [0, 0, 1, 1, 2, 2]), ('sort_colors([2, 0, 1])', [0, 1, 2])])
lc(48, 'Rotate Image', 'rotate-image', 'm', 'Transpose, then reverse each row', 'Swap matrix[r][c] with matrix[c][r] above the diagonal, then reverse every row.', r'''
def rotate_image(matrix):
    n = len(matrix)
    for r in range(n):
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
    for row in matrix:
        row.reverse()
    return matrix
''', [('rotate_image([[1, 2, 3], [4, 5, 6], [7, 8, 9]])', [[7, 4, 1], [8, 5, 2], [9, 6, 3]])])
lc(54, 'Spiral Matrix', 'spiral-matrix', 'm', 'Shrinking borders', 'Keep top, bottom, left and right borders. Walk right, down, left and up, moving a border in after each side.', r'''
def spiral_order(matrix):
    result = []
    top = 0
    bottom = len(matrix) - 1
    left = 0
    right = len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top = top + 1
        for r in range(top, bottom + 1):
            result.append(matrix[r][right])
        right = right - 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom = bottom - 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left = left + 1
    return result
''', [('spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]])', [1, 2, 3, 6, 9, 8, 7, 4, 5]), ('spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])', [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7])])

K.lesson('leetcode', 'LeetCode practice', leet(), kw=['LeetCode', 'two pointers', 'move zeroes', 'best time to buy and sell stock', 'rotate array', 'spiral matrix', "Pascal's triangle"])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>list</b> is an ordered, changeable collection in square brackets. Items can be of any type.',
    'Add with append, insert and extend. Remove with remove (by value), pop and del (by index) and clear.',
    'Find with in, index and count. All three walk the list, so they take O(n).',
    '<b>sort()</b> changes the list and returns None. <b>sorted()</b> returns a new list. Both take key and reverse and are stable.',
    'b = a shares one list. a[:], a.copy() and list(a) make a shallow copy, copy.deepcopy makes a full copy.',
    'Build grids with [[0] * n for _ in range(m)], never [[0] * n] * m.',
    'Bubble sort makes at most n(n &minus; 1)/2 comparisons. append is amortised O(1) because CPython keeps spare room.'],
    'Core 3.3 covers tuples (lists that cannot change) and sets (collections of unique items with fast membership).')}
{files('Three tasks: second largest without sorting, rotate a list by k, and flatten a list of lists.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is [10, 20, 30][-1]?', ['10', '30', '20', 'IndexError'], 1, 'Last item.', '&minus;1 is the last index.')
K.quiz('e', 'Which method adds one item at the end?', ['add()', 'append()', 'insert()', 'push()'], 1, 'Python has no push.', 'append(x) adds x at the end.')
K.quiz('e', 'What is len([1, [2, 3], 4])?', ['4', '3', '2', '5'], 1, 'The inner list is one item.', 'Three items: 1, [2, 3] and 4.')
K.quiz('m', 'a = [1, 2] then a.append([3, 4]). What is a?', ['[1, 2, 3, 4]', '[1, 2, [3, 4]]', '[[1, 2], [3, 4]]', 'Error'], 1, 'append adds one item.', 'The whole list [3, 4] becomes one item.')
K.quiz('m', 'a = [3, 1, 2] then b = a.sort(). What is b?', ['[1, 2, 3]', '[3, 1, 2]', 'None', 'Error'], 2, 'sort() changes in place.', 'sort() returns None.')
K.quiz('m', 'a = [1, 2] then b = a then b.append(3). What is a?', ['[1, 2]', '[1, 2, 3]', '[3]', 'Error'], 1, 'One list, two names.', 'b is an alias of a.')
K.quiz('m', 'a = [1, 2, 3, 2] then a.remove(2). What is a?', ['[1, 3, 2]', '[1, 3]', '[1, 2, 3]', '[1, 2, 3, 2]'], 0, 'First match only.', 'remove deletes the first 2.')
K.quiz('m', 'g = [[0] * 2] * 2 then g[0][0] = 5. What is g?', ['[[5, 0], [0, 0]]', '[[5, 0], [5, 0]]', '[[5, 5], [0, 0]]', 'Error'], 1, 'Both rows are one list.', 'The outer * copies the reference, not the row.')
K.quiz('h', 'How many comparisons does bubble sort make in the worst case for 6 items (no early stop)?', ['36', '15', '30', '6'], 1, 'n(n &minus; 1)/2.', '6 &times; 5 / 2 = 15.')
K.quiz('h', 'What does sorted(["b", "C", "a"]) give?', ['["a", "b", "C"]', '["C", "a", "b"]', '["a", "C", "b"]', '["C", "b", "a"]'], 1, 'Upper case first.', '"C" (67) is less than "a" (97).')
K.quiz('h', 'Which is O(n) on a list of n items?', ['append(x)', 'pop()', 'insert(0, x)', 'items[5]'], 2, 'Who has to move?', 'Every item moves one place right.')
K.quiz('x', 'In the style of a Stanford CS106A exam: a = [1, 2, 3], b = a, a = a + [4], b += [5]. What are a and b?', ['a = [1, 2, 3, 4], b = [1, 2, 3, 5]', 'both [1, 2, 3, 4, 5]', 'a = [1, 2, 3, 4, 5], b = [1, 2, 3, 5]', 'a = [1, 2, 3, 4], b = [1, 2, 3, 4, 5]'], 0, 'a + [4] makes a new list.', 'After a = a + [4], a and b are different lists. b += [5] changes only the old list.')
K.quiz('x', 'In the style of a CMU 15-112 exam: x = [1, 2, 3, 4], then for v in x: x.remove(v). What is x?', ['[]', '[2, 4]', '[1, 3]', '[4]'], 1, 'The loop skips the item after each removal.', 'Remove 1 (index 0), the loop moves to index 1 which is now 3, remove 3. [2, 4] is left.')

K.calc('e', 'len([1, 2, 3] + [4, 5])?', '5', '3 + 2.', ['+ joins lists.', '3 items and 2 items.', eq('5')], check=len([1, 2, 3] + [4, 5]))
K.calc('e', 'sum([72, 45, 91, 38]) / 4?', '61.5', 'Mean.', ['Sum = 246.', '246 / 4.', eq('61.5')], check=sum([72, 45, 91, 38]) / 4)
K.calc('e', 'len([0] * 7)?', '7', 'Repeat 7 times.', ['[0] has 1 item.', '7 copies.', eq('7')], check=len([0] * 7))
K.calc('m', 'Worst case bubble sort comparisons for 10 items?', '45', 'n(n &minus; 1)/2.', ['n = 10.', '10 &times; 9 / 2.', eq('45')], check=10 * 9 // 2)
K.calc('m', 'Number of items in a 3 &times; 4 &times; 5 cube made of nested lists?', '60', 'Multiply.', ['3 layers.', '4 rows and 5 columns each.', eq('60')], check=3 * 4 * 5)
K.calc('m', 'CPython capacity when a list grows to hold 5 items: (5 + 5 // 8 + 6) rounded down to a multiple of 4.', '8', '11 rounded down.', ['5 // 8 = 0.', '5 + 0 + 6 = 11.', eq('11 rounded down to a multiple of 4 is 8')], check=(5 + (5 >> 3) + 6) & ~3)
K.calc('m', 'Copies with doubling for 64 appends: 1 + 2 + 4 + ... + 32.', '63', 'Geometric series.', ['Six terms.', '2<sup>6</sup> &minus; 1.', eq('63')], check=sum(2 ** i for i in range(6)))
K.calc('h', 'Most checks binary search needs for a sorted list of 1,000 items.', '10', '&lfloor;log<sub>2</sub> n&rfloor; + 1.', ['2<sup>9</sup> = 512 &le; 1,000 &lt; 1,024.', '&lfloor;log<sub>2</sub> 1000&rfloor; = 9.', eq('9 + 1 = 10')], check=(1000).bit_length())
K.calc('h', 'How many different orders can 5 different items be in? A comparison sort must tell them apart.', '120', '5!.', ['5 &times; 4 &times; 3 &times; 2 &times; 1.', 'log<sub>2</sub> 120 is about 6.9, so at least 7 comparisons are needed in the worst case.', eq('120')], check=120)
K.calc('x', 'In the style of a Princeton COS 226 question: a list grows by doubling from capacity 1. How many item copies are made in total while appending 1,000 items?', '1023', 'Copies at 1, 2, 4, ..., 512.', ['A resize happens when an append finds the list full at sizes 1, 2, 4, ..., 512.', 'Each resize copies the items already there.', eq('1 + 2 + ... + 512 = 1,023')], check=sum(2 ** i for i in range(10)))

K.assign('second', 'e', 'Second largest without sorting',
         '<p>Write <code>second_largest(nums)</code> that returns the second largest different value in a list with at least two different values. Use one loop and no sort.</p>',
         '''
def second_largest(nums):
    # your code here
    pass
''', [('second_largest([4, 9, 2, 7])', 7), ('second_largest([5, 5, 3])', 3), ('second_largest([-1, -5])', -5)],
         '''
def second_largest(nums):
    first = None
    second = None
    for x in nums:
        if first is None or x > first:
            second = first
            first = x
        elif x != first and (second is None or x > second):
            second = x
    return second
''', 'Keep two names, first and second. A new biggest pushes the old first down to second.', '<p>This is the running maximum pattern from Core 2.2 with one more name. It takes one pass, O(n), while sorting takes O(n log n).</p>')
K.assign('rot', 'm', 'Rotate a list to the right',
         '<p>Write <code>rotate_right(items, k)</code> that returns a new list with every item moved k places to the right, wrapping round. k can be bigger than the length. An empty list gives [].</p>',
         '''
def rotate_right(items, k):
    # your code here
    pass
''', [('rotate_right([1, 2, 3, 4, 5], 2)', [4, 5, 1, 2, 3]), ('rotate_right([1, 2, 3], 4)', [3, 1, 2]), ('rotate_right([], 3)', [])],
         '''
def rotate_right(items, k):
    if not items:
        return []
    k = k % len(items)
    return items[-k:] + items[:-k] if k else items[:]
''', 'Use k % len(items) first. Then the last k items come first: items[-k:] + items[:-k]. Watch out for k = 0.', '<p>When k is 0, items[-0:] is the whole list, so the k = 0 case needs its own branch. LeetCode 189 asks for the same in place.</p>')
K.assign('flat', 'm', 'Flatten a list of lists',
         '<p>Write <code>flatten(rows)</code> that turns a list of lists into one list with every item in order. [[1, 2], [3], []] becomes [1, 2, 3].</p>',
         '''
def flatten(rows):
    # your code here
    pass
''', [('flatten([[1, 2], [3], []])', [1, 2, 3]), ('flatten([])', []), ('flatten([["a"], ["b", "c"]])', ['a', 'b', 'c'])],
         '''
def flatten(rows):
    result = []
    for row in rows:
        for item in row:
            result.append(item)
    return result
''', 'Two loops: one over the rows and one over the items of each row. Append each item to a new list.', '<p>result.extend(row) does the inner loop for you. The one line version is [item for row in rows for item in row] (Core 4.3).</p>')

K.must('Lists', 'Ordered, changeable, any types. Index from 0, slice like strings. len, min, max, sum, in.')
K.must('Add and remove', 'append (one item), extend (many), insert(i, x). remove(x) first match, pop() last, pop(i), del items[i].')
K.must('Sorting', 'sort() changes the list and returns None. sorted() returns a new list. key= and reverse=. Stable.')
K.must('Copies', 'b = a is the same list. a[:] or a.copy() is a shallow copy. copy.deepcopy for nested lists. [[0]*n for _ in range(m)].')
K.must('Costs', 'append, pop(), index access O(1). insert(0), pop(0), in, remove O(n). Bubble sort n(n-1)/2 comparisons.')

T = K.topic(
    slug='py-lists', topic='py-lists', step=(3, 'Data collections', 'py-c3', 'Store and work with many values: strings, lists, tuples, sets and dictionaries.', 'Beginner'),
    title='Lists: storing, changing, sorting and copying', short='Lists', badge='3.2', minutes=65,
    lead='Keep many values in one place and change them. Learn to make lists, add, remove and find items, sort them two ways, understand names and copies, build matrices, write bubble sort by hand and see how CPython makes append fast.',
    desc='list literals, list(), indexing and slicing, append, insert, extend, slice assignment, remove, pop, del, clear, index, count, in, sort and sorted with key and reverse, stable sorting, aliases, shallow and deep copy, nested lists and matrices, bubble sort, unpacking, star unpacking, first list comprehensions, dynamic array growth and amortised O(1) append, time complexity of list operations.',
    summary='list methods, sort vs sorted, aliases and copies, matrices, bubble sort, unpacking, list growth and costs.',
    keywords=['lists', 'list methods', 'append', 'sort', 'sorted', 'copy', 'deepcopy', 'matrix', 'bubble sort', 'mutable', 'amortised', 'PCEP'],
    recap='<p>A list is an ordered, changeable sequence. Change it with its methods, copy it on purpose, sort it with sort or sorted, and know what each operation costs.</p>',
    added='2026-11-07', leet=leet_items())
