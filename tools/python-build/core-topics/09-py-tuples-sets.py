# Core Python 3.3: tuples and sets. Follows PCEP-30-02 section 3.2 (tuples: indexing, slicing, building, immutability,
# tuples vs lists: similarities and differences, lists inside tuples and tuples inside lists) and adds sets, which
# PCAP-31-03 expects, checked against the Python 3.14 tutorial sections 5.3 and 5.4 and the library reference
# section "Set Types: set, frozenset".
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-tuples-sets')
K = Kit()

K.code('tuple', r'''
point = (3, 7)
colours = ("red", "green", "blue")
one = (5,)            # a tuple with one item needs the comma
not_tuple = (5)       # just the number 5 in brackets
empty = ()
packed = 1, 2, 3      # brackets are optional: the commas make the tuple
print(point, colours, one, not_tuple, empty, packed)
print(type(one), type(not_tuple))
print(colours[0], colours[-1], colours[1:])
print(len(colours), "green" in colours, colours.index("blue"), (1, 2, 1).count(1))
print((1, 2) + (3,), (0,) * 4)
''')

K.code('tupimm', r'''
days = ("Mon", "Tue", "Wed")
try:
    days[0] = "Sun"
except TypeError as err:
    print("TypeError:", err)

# A tuple cannot change, but a list inside it can
record = ("Asha", [80, 90])
record[1].append(75)
print(record)

days = days + ("Thu",)     # this builds a new tuple and moves the name
print(days)
''')

K.code('unpack', r'''
def min_max(numbers):
    return min(numbers), max(numbers)     # returns one tuple

low, high = min_max([4, 9, 1, 7])         # unpack it into two names
print(low, high)

students = [("Asha", 88), ("Ravi", 72), ("Meera", 95)]
for name, score in students:              # unpack in the loop
    print(name, score)

best = max(students, key=lambda pair: pair[1])
print("best:", best)
print(sorted(students, key=lambda pair: pair[1], reverse=True))

a, b = 1, 2
a, b = b, a        # swap: the right side is packed into a tuple first
print(a, b)
''')

K.code('tupkey', r'''
# Tuples can be dict keys and set items, lists cannot
distance = {("Delhi", "Agra"): 233, ("Mumbai", "Pune"): 149}
print(distance[("Delhi", "Agra")])

seen = {(0, 0), (1, 2)}
print((1, 2) in seen)

try:
    bad = {[1, 2]: "x"}
except TypeError as err:
    print("TypeError:", err)

print(hash((1, 2)) == hash((1, 2)))
''')

K.code('named', r'''
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p, p.x, p.y, p[0])
print((p.x ** 2 + p.y ** 2) ** 0.5)
x, y = p                # still a tuple, so it unpacks
print(x + y)
print(p._replace(x=10)) # a new tuple, p is unchanged
''')

K.code('set', r'''
langs = {"python", "java", "python", "go"}
print(langs, len(langs))        # the repeat is gone, order is not fixed

empty = set()                   # {} would make an empty dict
print(type(empty), type({}))

nums = set([3, 1, 3, 2, 1])
print(nums)
print(set("banana"))

langs.add("rust")
langs.discard("cobol")          # no error if missing
langs.remove("java")            # KeyError if missing
print(sorted(langs))
print("go" in langs)
''')

K.code('setops', r'''
python_class = {"Asha", "Ravi", "Meera", "John"}
java_class = {"Ravi", "John", "Sara"}

print(python_class | java_class)      # union: in either class
print(python_class & java_class)      # intersection: in both
print(python_class - java_class)      # difference: only Python
print(python_class ^ java_class)      # symmetric difference: in exactly one

print({"Ravi", "John"} <= java_class)            # subset
print(python_class >= {"Asha"})                  # superset
print(python_class.isdisjoint({"Zara", "Leo"}))  # nothing in common
print(python_class.union(["Leo"]))               # the methods take any iterable
''')

K.code('dedupe', r'''
orders = ["tea", "coffee", "tea", "juice", "coffee", "tea"]

print(len(set(orders)), "different drinks")
print(sorted(set(orders)))

# set() loses the order. dict.fromkeys keeps the first time each item appears
print(list(dict.fromkeys(orders)))

# The same with a loop and a set of seen items
unique = []
seen = set()
for item in orders:
    if item not in seen:
        seen.add(item)
        unique.append(item)
print(unique)
''')

K.code('speed', r'''
import time

big_list = list(range(1_000_000))
big_set = set(big_list)

start = time.perf_counter()
for _ in range(20):
    999_999 in big_list
list_time = time.perf_counter() - start

start = time.perf_counter()
for _ in range(20):
    999_999 in big_set
set_time = time.perf_counter() - start

print("the list search is more than 100 times slower:", list_time > 100 * set_time)
''')

K.code('frozen', r'''
vowels = frozenset("aeiou")
print(vowels, "e" in vowels)
try:
    vowels.add("y")
except AttributeError as err:
    print("AttributeError:", err)

groups = {frozenset({"a", "b"}), frozenset({"b", "a"})}   # equal sets, so one item
print(len(groups))
squares = {n * n for n in range(-3, 4)}                   # a set comprehension
print(sorted(squares))
''')

K.lesson('idea', 'Two new collections: tuples and sets', f'''
{src('Python 3.14 tutorial sections 5.3 and 5.4, the library reference section on set and frozenset, and PCEP-30-02 section 3.2.')}
{wwh('A <b>tuple</b> is an ordered sequence like a list, written with round brackets, that can never change. A <b>set</b> is a collection with no order and no repeats, written with curly brackets.',
     'A list is great for data that changes. But some data should not change (a date, a point on a map, a row from a database), and sometimes you only care whether something is present, not where. Tuples protect fixed data. Sets remove repeats and answer "is it in here?" almost instantly.',
     'A tuple is a fixed array of references, so it is a little smaller and faster than a list and can be used as a dict key. A set is a hash table (like a dict without values), so adding, removing and the in test take O(1) on average.')}
{scene('a train seat and a guest list', '<p>Your train seat is (coach "B2", seat 34). That pair must not change after booking: it is a tuple. A wedding guest list written by two families has many names twice. Turn both lists into sets, take the union, and every guest appears once. To find the guests both families invited, take the intersection.</p>')}
''', kw=['tuple', 'set', 'immutable', 'unique', 'hash table'])

K.lesson('tuple', 'Making and using tuples', f'''
{run('tuple')}
{note('The comma makes a tuple, not the brackets. (5) is the number 5. (5,) is a tuple with one item. This is a favourite exam trick.', 'exam')}
{table(['You can', 'Example'], [
    ['Index and slice', 't[0], t[-1], t[1:]'],
    ['Join and repeat', '(1, 2) + (3,), (0,) * 4'],
    ['Search', 'x in t, t.index(x), t.count(x)'],
    ['Loop and unpack', 'for a, b in pairs, x, y = point'],
    ['Not: append, remove, sort, item assignment', 'Use sorted(t) to get a sorted list']])}
''', kw=['tuple', 'one item tuple', 'comma', 'tuple methods', 'count', 'index'])

K.lesson('tupimm', 'What "cannot change" means', f'''
{run('tupimm')}
{note('A tuple holds references. You cannot change which objects it holds, but if one of them is a list, that list can still change. Such a tuple is not hashable, so it cannot be a dict key.', 'warn')}
''', kw=['immutable', 'tuple with list', 'TypeError', 'new tuple'])

K.lesson('unpack', 'Packing, unpacking and returning many values', f'''
{run('unpack')}
{wwh('<b>Packing</b> puts several values into one tuple: t = 1, 2, 3. <b>Unpacking</b> takes them out into names: a, b, c = t.',
     'A function can return only one object. Returning a tuple lets it give back several results at once, and unpacking gives each result a clear name.',
     'Python evaluates the right side fully first, packs it into a tuple, then assigns each item to the names on the left in order. That is why a, b = b, a swaps safely.')}
''', kw=['packing', 'unpacking', 'return multiple values', 'swap', 'list of tuples', 'sort by key'])

K.lesson('tupkey', 'Tuples as keys, and named tuples', f'''
{run('tupkey')}
{run('named')}
{note('A named tuple gives each position a name, so p.x is clearer than p[0]. For records with many fields or that need to change, use a dataclass (Advanced 1.3).', 'tip')}
''', kw=['hashable', 'dict key', 'namedtuple', 'collections', 'record'])

K.lesson('versus1', 'Tuple or list', f'''
{versus('Tuple compared with list', ['', 'tuple', 'list'], [
    ['Brackets', '( )', '[ ]'],
    ['Can change', 'No', 'Yes'],
    ['Hashable (dict key, set item)', 'Yes, if every item is hashable', 'No'],
    ['Memory for (1, 2, 3)', '72 bytes on CPython 3.14', '88 bytes'],
    ['Methods', 'count, index', 'about 11, including append and sort'],
    ['Meaning', 'A fixed record: (name, age), (x, y)', 'Many items of the same kind that grows or shrinks']],
    'use a tuple when the size and the items should stay the same, and a list when you will add, remove or sort.')}
''', kw=['tuple vs list', 'memory', 'hashable', 'record'])

K.lesson('set', 'Making sets and changing them', f'''
{run('set')}
{table(['Method', 'Does', 'If the item is missing'], [
    ['add(x)', 'Adds x (nothing happens if it is already there)', ''],
    ['remove(x)', 'Removes x', 'KeyError'],
    ['discard(x)', 'Removes x', 'Nothing happens'],
    ['pop()', 'Removes and returns some item (you cannot choose which)', 'KeyError on an empty set'],
    ['update(items)', 'Adds every item of an iterable', ''],
    ['clear()', 'Empties the set', '']])}
{note('{} is an empty dict, not an empty set. Write set() for an empty set. Also, a set can only hold hashable items: numbers, strings, tuples of them, but not lists or other sets.', 'exam')}
''', kw=['set', 'set()', 'add', 'remove', 'discard', 'pop', 'empty set', 'hashable'])

K.lesson('setops', 'Union, intersection, difference', f'''
{viz('pyset')}
{run('setops')}
{table(['Operator', 'Method', 'Means'], [
    ['A | B', 'A.union(B)', 'In A or B or both'],
    ['A &amp; B', 'A.intersection(B)', 'In both'],
    ['A &minus; B', 'A.difference(B)', 'In A but not in B'],
    ['A ^ B', 'A.symmetric_difference(B)', 'In exactly one of them'],
    ['A &lt;= B', 'A.issubset(B)', 'Every item of A is in B'],
    ['A &lt; B', '', 'Subset and not equal'],
    ['', 'A.isdisjoint(B)', 'No item in common']])}
{note('The operators need two sets. The methods accept any iterable, so A.union([1, 2]) works but A | [1, 2] raises TypeError.', 'exam')}
''', kw=['union', 'intersection', 'difference', 'symmetric difference', 'subset', 'superset', 'disjoint', 'Venn diagram'])

K.lesson('dedupe', 'Removing duplicates', f'''
{run('dedupe')}
{note('set(items) is the fastest way to remove repeats, but the order is lost. If order matters, use list(dict.fromkeys(items)), which keeps the first time each item appears.', 'tip')}
''', kw=['remove duplicates', 'unique', 'dict.fromkeys', 'keep order', 'seen set'])

K.lesson('speed', 'Why sets are fast', f'''
{run('speed')}
{wwh('A set stores each item in a table at a place worked out from the item hash, a number made from its value.',
     'To check x in a list, Python may have to look at every item. With a million items that is a million checks.',
     'To check x in a set, Python works out hash(x), jumps straight to that place in the table and looks at one or a few slots. The number of checks stays about the same for 10 items or 10 million items: O(1) on average. Core 3.4 shows the hash table step by step with the dict animation.')}
{versus('Checking membership', ['', 'x in list', 'x in set'], [
    ['Average time', 'O(n)', 'O(1)'],
    ['Keeps order and repeats', 'Yes', 'No'],
    ['Items must be', 'Anything', 'Hashable'],
    ['Extra memory', 'Less', 'More (the table has empty slots)']],
    'turn a list into a set once if you will check membership many times.')}
''', kw=['hash', 'O(1) membership', 'performance', 'hash table', 'list vs set'])

K.lesson('frozen', 'frozenset and set comprehensions', f'''
{run('frozen')}
{note('A frozenset is a set that cannot change. Because it never changes it is hashable, so it can be a dict key or an item of another set.', 'tip')}
''', kw=['frozenset', 'set comprehension', 'hashable set', 'immutable set'])

K.lesson('maths', 'The maths of sets', f'''
{fxs(fx('Size of a union (inclusion and exclusion)', '|A &cup; B| = |A| + |B| &minus; |A &cap; B|', 'The middle part was counted twice, so take it away once.', key=True),
     fx('Three sets', '|A &cup; B &cup; C| = |A| + |B| + |C| &minus; |A &cap; B| &minus; |A &cap; C| &minus; |B &cap; C| + |A &cap; B &cap; C|', 'Add singles, take away pairs, add back the triple.'),
     fx('Symmetric difference', '|A &Delta; B| = |A| + |B| &minus; 2|A &cap; B|', 'A ^ B in Python.'),
     fx('Number of subsets (the power set)', '2<sup>n</sup>', 'Each item is in or out. {1, 2, 3} has 8 subsets.', key=True),
     fx("De Morgan's laws", 'not (A or B) = (not A) and (not B)', 'For sets inside a universe U: U &minus; (A &cup; B) = (U &minus; A) &cap; (U &minus; B).'))}
{steps('Worked example: students in at least one class', [
    '40 students take Python, 30 take Java and 12 take both.',
    'Use |A &cup; B| = |A| + |B| &minus; |A &cap; B|.',
    eq('40 + 30 &minus; 12 = 58 students'),
    'Students in exactly one class: 58 &minus; 12 = 46, which is |A ^ B|.'])}
''', kw=['inclusion exclusion', 'power set', 'subsets', 'De Morgan', 'Venn diagram', 'set theory'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A tuple is a list that cannot change. A set is a bag of unique items with no order.</p>',
    '<p>(5,) is a tuple, (5) is not. Tuples unpack and can be dict keys. Sets give union, intersection and difference, and set() is the empty set.</p>',
    '<p>Hashable means "has a hash that never changes", which needs an immutable value. Sets and dict keys need hashable items. Use a set to turn O(n) membership tests into O(1), and dict.fromkeys to remove repeats while keeping order.</p>',
    '<p>CPython sets use open addressing with a mix of linear and random probing and keep the table at most about 60 percent full. Set algebra is Boolean algebra: union is OR, intersection is AND, and the power set of an n item set has 2<sup>n</sup> members, which is why "try every subset" algorithms take exponential time.</p>')}
{grow('Make tuples and sets, unpack a tuple, and remove duplicates with set().',
      'Return several values, use tuples as keys, and solve problems with |, &amp;, &minus; and ^.',
      'Explain hashability, choose between list, tuple and set by their costs, and use inclusion and exclusion to count.')}
''', kw=['beginner', 'expert', 'hashable', 'open addressing', 'Boolean algebra'])

lc(217, 'Contains Duplicate', 'contains-duplicate', 'e', 'Seen set', 'Add each number to a set. If it is already there, you found a duplicate.', r'''
def contains_duplicate(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False
''', [('contains_duplicate([1, 2, 3, 1])', True), ('contains_duplicate([1, 2, 3, 4])', False)])
lc(349, 'Intersection of Two Arrays', 'intersection-of-two-arrays', 'e', 'Set intersection', 'Turn both lists into sets and take the intersection.', r'''
def intersection(nums1, nums2):
    common = set(nums1) & set(nums2)
    return sorted(common)
''', [('intersection([1, 2, 2, 1], [2, 2])', [2]), ('intersection([4, 9, 5], [9, 4, 9, 8, 4])', [4, 9])])
lc(771, 'Jewels and Stones', 'jewels-and-stones', 'e', 'Set membership', 'Put the jewel letters in a set, then count the stones that are in it.', r'''
def num_jewels_in_stones(jewels, stones):
    jewel_set = set(jewels)
    count = 0
    for stone in stones:
        if stone in jewel_set:
            count = count + 1
    return count
''', [('num_jewels_in_stones("aA", "aAAbbbb")', 3), ('num_jewels_in_stones("z", "ZZ")', 0)])
lc(1832, 'Check if the Sentence Is Pangram', 'check-if-the-sentence-is-pangram', 'e', 'Set size', 'A pangram uses every letter a to z. The set of its letters has 26 items.', r'''
def check_if_pangram(sentence):
    return len(set(sentence)) == 26
''', [('check_if_pangram("thequickbrownfoxjumpsoverthelazydog")', True), ('check_if_pangram("leetcode")', False)])
lc(268, 'Missing Number', 'missing-number', 'e', 'Gauss sum', 'The numbers 0 to n add up to n(n + 1)/2. The missing one is that total minus the sum of the list.', r'''
def missing_number(nums):
    n = len(nums)
    expected = n * (n + 1) // 2
    return expected - sum(nums)
''', [('missing_number([3, 0, 1])', 2), ('missing_number([9, 6, 4, 2, 3, 5, 7, 0, 1])', 8), ('missing_number([0])', 1)])
lc(2215, 'Find the Difference of Two Arrays', 'find-the-difference-of-two-arrays', 'e', 'Set difference', 'A &minus; B and B &minus; A answer the two parts.', r'''
def find_difference(nums1, nums2):
    a = set(nums1)
    b = set(nums2)
    return [sorted(a - b), sorted(b - a)]
''', [('find_difference([1, 2, 3], [2, 4, 6])', [[1, 3], [4, 6]]), ('find_difference([1, 2, 3, 3], [1, 1, 2, 2])', [[3], []])])
lc(1436, 'Destination City', 'destination-city', 'e', 'Set difference', 'The destination is a city that appears as an end but never as a start.', r'''
def dest_city(paths):
    starts = set()
    ends = set()
    for start, end in paths:
        starts.add(start)
        ends.add(end)
    answer = ends - starts
    return answer.pop()
''', [('dest_city([["London", "New York"], ["New York", "Lima"], ["Lima", "Sao Paulo"]])', 'Sao Paulo'), ('dest_city([["A", "Z"]])', 'Z')])
lc(645, 'Set Mismatch', 'set-mismatch', 'e', 'Set and Gauss sum', 'The repeated number is sum(nums) &minus; sum(set(nums)). The missing number is n(n + 1)/2 &minus; sum(set(nums)).', r'''
def find_error_nums(nums):
    n = len(nums)
    unique_sum = sum(set(nums))
    repeated = sum(nums) - unique_sum
    missing = n * (n + 1) // 2 - unique_sum
    return [repeated, missing]
''', [('find_error_nums([1, 2, 2, 4])', [2, 3]), ('find_error_nums([1, 1])', [1, 2])])
lc(3, 'Longest Substring Without Repeating Characters', 'longest-substring-without-repeating-characters', 'm', 'Sliding window with a set', 'Grow the window on the right. While the new letter is already in the window, drop letters from the left.', r'''
def length_of_longest_substring(s):
    window = set()
    left = 0
    best = 0
    for right in range(len(s)):
        while s[right] in window:
            window.remove(s[left])
            left = left + 1
        window.add(s[right])
        if right - left + 1 > best:
            best = right - left + 1
    return best
''', [('length_of_longest_substring("abcabcbb")', 3), ('length_of_longest_substring("bbbbb")', 1), ('length_of_longest_substring("pwwkew")', 3), ('length_of_longest_substring("")', 0)])
lc(128, 'Longest Consecutive Sequence', 'longest-consecutive-sequence', 'm', 'Set, start only at the beginning of a run', 'Put all numbers in a set. Start counting only from x where x &minus; 1 is not in the set, so each run is walked once: O(n).', r'''
def longest_consecutive(nums):
    values = set(nums)
    best = 0
    for x in values:
        if x - 1 not in values:
            length = 1
            while x + length in values:
                length = length + 1
            if length > best:
                best = length
    return best
''', [('longest_consecutive([100, 4, 200, 1, 3, 2])', 4), ('longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1])', 9), ('longest_consecutive([])', 0)])

K.lesson('leetcode', 'LeetCode practice', leet(), kw=['LeetCode', 'contains duplicate', 'intersection', 'pangram', 'missing number', 'sliding window', 'longest consecutive sequence'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>tuple</b> is an ordered sequence that cannot change. The comma makes it: (5,) is a tuple, (5) is an int.',
    'Tuples pack and unpack: return a, b gives a tuple, and x, y = point takes it apart.',
    'Tuples of hashable items can be dict keys and set items. Lists cannot.',
    'A <b>set</b> holds unique hashable items with no order. set() is empty, {} is a dict.',
    'add, remove (KeyError), discard (no error), pop (any item). | union, &amp; both, &minus; only in the first, ^ in exactly one.',
    'x in a set is O(1) on average, x in a list is O(n).',
    '|A &cup; B| = |A| + |B| &minus; |A &cap; B|, and a set of n items has 2<sup>n</sup> subsets.'],
    'Core 3.4 covers dictionaries: key and value pairs, every method, counting and grouping, and the hash table behind them.')}
{files('Three tasks: common friends of two people, the first repeated item, and all subsets of a small set.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is type((5,))?', ['int', 'tuple', 'list', 'set'], 1, 'The comma.', 'A trailing comma makes a one item tuple.')
K.quiz('e', 'What is type((5))?', ['int', 'tuple', 'list', 'set'], 0, 'Brackets only group.', '(5) is the number 5.')
K.quiz('e', 'What is len({1, 1, 2, 2, 3})?', ['5', '3', '2', '1'], 1, 'Repeats vanish.', 'The set is {1, 2, 3}.')
K.quiz('e', 'Which makes an empty set?', ['{}', 'set()', '[]', '()'], 1, '{} is something else.', '{} is an empty dict.')
K.quiz('m', 'What happens with t = (1, 2) then t.append(3)?', ['t is (1, 2, 3)', 'AttributeError', 'TypeError', 'Nothing'], 1, 'Tuples have no append.', "'tuple' object has no attribute 'append'.")
K.quiz('m', 'What is {1, 2, 3} - {2, 3, 4}?', ['{1}', '{4}', '{1, 4}', '{2, 3}'], 0, 'In the first, not the second.', 'Only 1 is in A and not in B.')
K.quiz('m', 'What is {1, 2, 3} ^ {2, 3, 4}?', ['{1}', '{1, 4}', '{2, 3}', '{1, 2, 3, 4}'], 1, 'In exactly one.', '1 is only in A, 4 is only in B.')
K.quiz('m', 'Which can be a set item?', ['[1, 2]', '{1, 2}', '(1, 2)', '{"a": 1}'], 2, 'Hashable only.', 'A tuple of ints is hashable. Lists, sets and dicts are not.')
K.quiz('m', 'What does s.discard(9) do when 9 is not in s?', ['KeyError', 'Nothing', 'Adds 9', 'Returns False and prints'], 1, 'Unlike remove.', 'discard never raises an error.')
K.quiz('h', 'What is t = (1, [2]) then t[1].append(3) then t?', ['TypeError', '(1, [2, 3])', '(1, [2])', '(1, 2, 3)'], 1, 'The list inside can change.', 'The tuple still holds the same list, which now has 3 in it.')
K.quiz('h', 'What is {1, 2} &lt; {1, 2}?', ['True', 'False', 'TypeError', '{1, 2}'], 1, 'Strict subset.', '&lt; needs a proper subset, so equal sets give False. &lt;= gives True.')
K.quiz('x', 'In the style of an MIT 6.042 (Mathematics for Computer Science) question: 100 people, 60 like tea, 50 like coffee, 15 like neither. How many like both?', ['10', '25', '35', '15'], 1, '|T &cup; C| = 85.', '60 + 50 &minus; 85 = 25.')
K.quiz('x', 'In the style of a Cambridge Part IA question: a, *b, c = (1, 2, 3, 4, 5). What is b?', ['(2, 3, 4)', '[2, 3, 4]', '[2, 3]', '2'], 1, 'Star unpacking gives a list.', 'Even from a tuple, the starred name always gets a list.')

K.calc('e', 'len((1, 2) + (3, 4, 5))?', '5', '2 + 3.', ['+ joins tuples.', '2 + 3 items.', eq('5')], check=len((1, 2) + (3, 4, 5)))
K.calc('e', 'len(set("mississippi"))?', '4', 'm, i, s, p.', ['Letters used: m, i, s, p.', 'Repeats vanish.', eq('4')], check=len(set('mississippi')))
K.calc('e', 'How many subsets does {a, b, c, d} have?', '16', '2<sup>n</sup>.', ['n = 4.', '2<sup>4</sup>.', eq('16')], check=2 ** 4)
K.calc('m', '|A &cup; B| when |A| = 40, |B| = 30, |A &cap; B| = 12.', '58', 'Inclusion and exclusion.', ['40 + 30 = 70.', 'Take away 12.', eq('58')], check=40 + 30 - 12)
K.calc('m', '|A ^ B| for the same sets.', '46', '|A| + |B| &minus; 2|A &cap; B|.', ['70 &minus; 24.', 'Or 58 &minus; 12.', eq('46')], check=70 - 24)
K.calc('m', 'len({1, 2, 3} | {3, 4} | {4, 5, 6})?', '6', '1 to 6.', ['Union of all three.', '{1, 2, 3, 4, 5, 6}.', eq('6')], check=len({1, 2, 3} | {3, 4} | {4, 5, 6}))
K.calc('m', 'How many subsets of {1, 2, 3, 4, 5} have exactly 2 items?', '10', 'C(5, 2).', ['Choose 2 from 5.', '5 &times; 4 / 2.', eq('10')], check=5 * 4 // 2)
K.calc('h', 'Three sets: |A| = |B| = |C| = 20, each pair shares 8, all three share 3. Find |A &cup; B &cup; C|.', '39', 'Add, take pairs, add triple.', ['20 + 20 + 20 = 60.', 'Take away 8 &times; 3 = 24.', eq('60 &minus; 24 + 3 = 39')], check=60 - 24 + 3)
K.calc('h', 'Numbers from 1 to 100 that divide by 2 or by 3.', '67', 'Inclusion and exclusion.', ['Divisible by 2: 50. By 3: 33.', 'By both (by 6): 16.', eq('50 + 33 &minus; 16 = 67')], check=len({n for n in range(1, 101) if n % 2 == 0 or n % 3 == 0}))
K.calc('x', 'In the style of a Putnam style counting question: how many numbers from 1 to 1000 are divisible by none of 2, 3 and 5?', '266', 'Inclusion and exclusion with three sets.', ['By 2: 500, by 3: 333, by 5: 200.', 'By 6: 166, by 10: 100, by 15: 66. By 30: 33.', 'Divisible by at least one: 500 + 333 + 200 &minus; 166 &minus; 100 &minus; 66 + 33 = 734.', eq('1000 &minus; 734 = 266')], check=sum(1 for n in range(1, 1001) if n % 2 and n % 3 and n % 5))

K.assign('friends', 'e', 'Common friends',
         '<p>Write <code>common_friends(a, b)</code> where a and b are lists of names. Return a sorted list of the names that are in both, each name once.</p>',
         '''
def common_friends(a, b):
    # your code here
    pass
''', [('common_friends(["Asha", "Ravi", "Asha"], ["Ravi", "John", "Asha"])', ['Asha', 'Ravi']), ('common_friends(["x"], ["y"])', []), ('common_friends([], ["y"])', [])],
         '''
def common_friends(a, b):
    both = set(a) & set(b)
    return sorted(both)
''', 'Turn both lists into sets and use &amp;. Then sorted() gives a list.', '<p>Social networks use exactly this to show "12 mutual friends". With sets it takes O(len(a) + len(b)) time.</p>')
K.assign('firstrep', 'm', 'First repeated item',
         '<p>Write <code>first_repeat(items)</code> that returns the first item that appears for the second time when you read from the left, or None if nothing repeats.</p>',
         '''
def first_repeat(items):
    # your code here
    pass
''', [('first_repeat([3, 1, 4, 1, 3])', 1), ('first_repeat(["a", "b"])', None), ('first_repeat("abca")', 'a')],
         '''
def first_repeat(items):
    seen = set()
    for item in items:
        if item in seen:
            return item
        seen.add(item)
    return None
''', 'Walk left to right with a set of items seen so far. The first item already in the set is the answer.', '<p>In [3, 1, 4, 1, 3] the answer is 1, not 3, because the second 1 comes before the second 3.</p>')
K.assign('subsets', 'h', 'All subsets of a small set',
         '<p>Write <code>all_subsets(items)</code> that takes a list of different items and returns a list of all its subsets, each one as a sorted tuple, and the whole list sorted. [1, 2] gives [(), (1,), (1, 2), (2,)].</p>',
         '''
def all_subsets(items):
    # your code here
    pass
''', [('all_subsets([1, 2])', [(), (1,), (1, 2), (2,)]), ('len(all_subsets([1, 2, 3, 4]))', 16), ('all_subsets([])', [()])],
         '''
def all_subsets(items):
    subsets = [[]]
    for item in items:
        new_ones = []
        for old in subsets:
            new_ones.append(old + [item])
        subsets = subsets + new_ones
    result = []
    for s in subsets:
        result.append(tuple(sorted(s)))
    return sorted(result)
''', 'Start with [[]]. For each item, make a copy of every subset so far with the item added. The count doubles each time.', '<p>The list doubles with every item, which is the 2<sup>n</sup> power set rule. With 30 items there are over a billion subsets, which is why such brute force methods only work for small inputs.</p>')

K.must('Tuples', 'Immutable ordered sequence. (5,) is a tuple, (5) is not. count and index only. Unpack with a, b = t.')
K.must('Hashable', 'Dict keys and set items must be hashable: numbers, strings, tuples of hashables, frozensets. Not lists, sets or dicts.')
K.must('Sets', 'Unique items, no order. set() is empty. add, remove (KeyError), discard (safe), pop (any item).')
K.must('Set algebra', '| union, & intersection, - difference, ^ symmetric difference, <= subset. Methods accept any iterable.')
K.must('Counting', '|A u B| = |A| + |B| - |A n B|. A set of n items has 2^n subsets. x in set is O(1) on average.')

T = K.topic(
    slug='py-tuples-sets', topic='py-tuples-sets', step=(3, 'Data collections', 'py-c3', 'Store and work with many values: strings, lists, tuples, sets and dictionaries.', 'Beginner'),
    title='Tuples and sets: fixed records and unique items', short='Tuples and sets', badge='3.3', minutes=55,
    lead='Learn the two other everyday collections. Tuples hold fixed records, unpack into names and work as dict keys. Sets keep each item once, answer "is it here?" in one step, and do union, intersection and difference like a Venn diagram.',
    desc='tuple literals, the one item tuple, packing and unpacking, returning many values, tuple immutability with mutable items inside, tuples as dict keys, hashability, namedtuple, tuple vs list, set literals and set(), add, remove, discard, pop, union, intersection, difference, symmetric difference, subset and superset, removing duplicates with and without order, why set membership is O(1), frozenset, set comprehensions, inclusion and exclusion and power sets.',
    summary='tuples, packing and unpacking, hashable keys, namedtuple, sets, set algebra, deduplication, O(1) membership, set maths.',
    keywords=['tuple', 'set', 'frozenset', 'unpacking', 'namedtuple', 'hashable', 'union', 'intersection', 'difference', 'Venn diagram', 'PCEP'],
    recap='<p>Use a tuple for a fixed record and a set for unique items and fast membership. Both rely on hashing, which Core 3.4 explains with the dict.</p>',
    added='2026-11-07', leet=leet_items())
