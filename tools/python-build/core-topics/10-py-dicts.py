# Core Python 3.4: dictionaries. Follows PCEP-30-02 section 3.3 (dictionaries: building, indexing, adding and
# removing keys, iterating through dictionaries and their keys and values, checking the existence of keys, keys(),
# items() and values() methods) and adds counting, grouping, nesting and the hash table behind dict, checked against
# the Python 3.14 tutorial section 5.5, the library reference section "Mapping Types: dict" and CPython dictobject.c.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-dicts')
K = Kit()

K.code('make', r'''
phone = {"Asha": "98450 11111", "Ravi": "99001 22222"}
ages = dict(asha=21, ravi=23)              # keyword style, keys become strings
pairs = dict([("x", 1), ("y", 2)])         # from a list of pairs
empty = {}
print(phone)
print(ages, pairs, empty)
print(phone["Asha"])                       # look up by key
print(len(phone), "Ravi" in phone, "98450 11111" in phone)
''')

K.code('change', r'''
stock = {"apple": 10, "mango": 4}
stock["kiwi"] = 7            # a new key is added
stock["apple"] = 12          # an old key gets a new value
stock["mango"] += 1
print(stock)

del stock["kiwi"]            # remove, KeyError if missing
sold = stock.pop("apple")    # remove and return the value
print(sold, stock)
print(stock.pop("grape", 0)) # a default stops the KeyError
stock.update({"fig": 3, "mango": 9})
print(stock)
print(stock.popitem())       # removes the last added pair
print(stock)
''')

K.code('get', r'''
prices = {"tea": 10, "coffee": 25}
try:
    print(prices["juice"])
except KeyError as err:
    print("KeyError:", err)

print(prices.get("juice"))          # None, no error
print(prices.get("juice", 0))       # your own default
print(prices.setdefault("juice", 15), prices)   # adds it if missing
print(prices.setdefault("tea", 99), prices)     # keeps the old value
''')

K.code('loop', r'''
marks = {"Asha": 88, "Ravi": 72, "Meera": 95}

for name in marks:                 # looping gives the keys
    print(name, end=" ")
print()
for score in marks.values():
    print(score, end=" ")
print()
for name, score in marks.items():  # key and value together
    print(f"{name}: {score}")

print(list(marks.keys()), list(marks.values()))
print(max(marks, key=marks.get))   # the key with the largest value
print(sorted(marks.items(), key=lambda pair: pair[1], reverse=True))
''')

K.code('views', r'''
d = {"a": 1, "b": 2}
keys = d.keys()          # a live view, not a copy
d["c"] = 3
print(keys)              # the view sees the new key
print(keys & {"a", "z"}) # key views work like sets

try:
    for k in d:
        d["new_" + k] = 0    # changing the size while looping
except RuntimeError as err:
    print("RuntimeError:", err)

d = {"a": 1, "b": 2}
for k in list(d):            # loop over a copy of the keys instead
    d["new_" + k] = 0
print(d)
''')

K.code('count', r'''
text = "the cat and the hat and the bat"

counts = {}                     # 1. with if
for word in text.split():
    if word in counts:
        counts[word] += 1
    else:
        counts[word] = 1
print(counts)

counts = {}                     # 2. with get
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
print(counts)

from collections import Counter # 3. with Counter
c = Counter(text.split())
print(c.most_common(2))
print(Counter("banana"))
''')

K.code('group', r'''
words = ["apple", "avocado", "banana", "blueberry", "cherry"]

groups = {}
for w in words:
    first = w[0]
    if first not in groups:
        groups[first] = []
    groups[first].append(w)
print(groups)

from collections import defaultdict
groups = defaultdict(list)      # a missing key starts as an empty list
for w in words:
    groups[w[0]].append(w)
print(dict(groups))
''')

K.code('nested', r'''
student = {
    "name": "Asha",
    "marks": {"maths": 91, "physics": 84},
    "clubs": ["chess", "music"],
}
print(student["marks"]["maths"])
print(student["clubs"][-1])
student["marks"]["chemistry"] = 77
print(student)

import json
text = json.dumps(student)          # to JSON text (Web 2.2 uses this a lot)
print(text)
back = json.loads(text)
print(back == student)
''')

K.code('merge', r'''
base = {"theme": "light", "size": 12}
user = {"size": 14, "lang": "hi"}

print(base | user)              # new dict, the right side wins (Python 3.9+)
merged = {**base, **user}       # the older way
print(merged)
base |= user                    # update in place
print(base)

squares = {n: n * n for n in range(1, 6)}       # dict comprehension
print(squares)
flipped = {v: k for k, v in squares.items()}
print(flipped)
print(dict.fromkeys(["a", "b"], 0))
print(dict(zip(["x", "y"], [10, 20])))
''')

K.code('keys', r'''
d = {}
d[1] = "int one"
d[1.0] = "float one"     # 1 == 1.0 and hash(1) == hash(1.0): the same key
d[True] = "true"         # True == 1 too
print(d)
print({(1, 2): "tuple key ok"})
try:
    d[[1, 2]] = "list"
except TypeError as err:
    print("TypeError:", err)
print(hash("hi") == hash("hi"), hash(10), hash(-1))
''')

K.code('internals', r'''
import sys
d = {}
last = sys.getsizeof(d)
print("empty dict:", last, "bytes")
for i in range(25):
    d[i] = i
    size = sys.getsizeof(d)
    if size != last:
        print("adding key number", len(d), "grew the dict to", size, "bytes")
        last = size
''')

K.lesson('idea', 'What a dictionary is', f'''
{src('Python 3.14 tutorial section 5.5, the library reference section on dict, and PCEP-30-02 section 3.3.')}
{wwh('A <b>dictionary</b> (type dict) stores <b>key and value pairs</b>. You look a value up by its key, not by a position: phone["Asha"] gives Asha\'s number.',
     'With a list you must remember that Asha is at index 0 and Ravi at 1, and finding someone means checking every item. A dict lets you use a meaningful name as the index and finds it in one step, however many entries there are.',
     'Each key is hashed to a number, and that number picks a slot in a table where the pair is stored. Keys must be unique and hashable. Values can be anything. Since Python 3.7 a dict also remembers the order in which keys were added.')}
{scene('the contacts app on your phone', '<p>Your phone does not ask "which position is Ravi in?". You type the name and it shows the number. Names are keys and numbers are values. Two contacts cannot have exactly the same name, adding a new number for an old name replaces it, and the search is instant even with 2,000 contacts. That is a Python dict.</p>')}
{run('make')}
''', kw=['dictionary', 'dict', 'key', 'value', 'key value pair', 'mapping', 'lookup'])

K.lesson('change', 'Adding, changing and removing', f'''
{run('change')}
{table(['Code', 'Does', 'If the key is missing'], [
    ['d[k] = v', 'Adds k, or replaces its value', 'Adds it'],
    ['del d[k]', 'Removes k', 'KeyError'],
    ['d.pop(k)', 'Removes k and returns its value', 'KeyError'],
    ['d.pop(k, default)', 'Same, with a default', 'Returns default'],
    ['d.popitem()', 'Removes and returns the last added pair', 'KeyError on an empty dict'],
    ['d.update(other)', 'Adds or replaces every pair of other', 'Adds them'],
    ['d.clear()', 'Empties the dict', '']])}
''', kw=['add key', 'update', 'del', 'pop', 'popitem', 'clear', 'KeyError'])

K.lesson('get', 'Safe lookups: get and setdefault', f'''
{run('get')}
{versus('Reading a key that may be missing', ['', 'd[k]', 'd.get(k, default)', 'k in d first'], [
    ['Missing key', 'KeyError', 'Returns default (None if not given)', 'You decide in an if'],
    ['Use when', 'The key must be there and a missing key is a bug', 'A missing key is normal', 'You need different code for the two cases']],
    'use d[k] when the key must exist, so mistakes show up as errors, and get() when a missing key is a normal case.')}
''', kw=['get', 'default value', 'setdefault', 'KeyError', 'in operator'])

K.lesson('loop', 'Looping over a dict', f'''
{run('loop')}
{note('for x in d gives the keys, not the values and not the pairs. Use d.values() for values and d.items() for (key, value) pairs. x in d also checks keys only.', 'exam')}
''', kw=['loop dict', 'keys', 'values', 'items', 'sort by value', 'max by value'])

K.lesson('views', 'Views, and changing a dict while looping', f'''
{run('views')}
{note('keys(), values() and items() return <b>views</b>: windows onto the dict that update by themselves. Adding or removing keys while you loop over a dict raises RuntimeError. Loop over list(d) instead.', 'warn')}
''', kw=['dict view', 'keys view', 'RuntimeError', 'changed size during iteration'])

K.lesson('count', 'Counting with a dict', f'''
{run('count')}
{note('Counting is the most common use of a dict. Learn the get(word, 0) + 1 line by heart, then use collections.Counter in real code. Counter also adds, subtracts and finds the most common items.', 'tip')}
''', kw=['counting', 'frequency', 'word count', 'get default', 'Counter', 'most_common'])

K.lesson('group', 'Grouping with a dict of lists', f'''
{run('group')}
{wwh('<b>Grouping</b> puts items into buckets by some property: words by first letter, students by class, orders by date.',
     'Reports and summaries are built from groups: total sales per city, average mark per subject.',
     'Use the property as the key and a list as the value. Create the empty list the first time you see a key (or let defaultdict(list) do it), then append.')}
''', kw=['grouping', 'dict of lists', 'defaultdict', 'bucket', 'collections'])

K.lesson('nested', 'Nested dicts and JSON', f'''
{run('nested')}
{note('A dict of dicts and lists looks exactly like JSON, the text format that web APIs use. json.dumps turns a dict into JSON text and json.loads turns it back. The web part of this subject uses this all the time.', 'tip')}
''', kw=['nested dict', 'JSON', 'json.dumps', 'json.loads', 'record'])

K.lesson('merge', 'Merging, comprehensions and other ways to build', f'''
{run('merge')}
{table(['Way', 'Result'], [
    ['a | b', 'A new dict. For equal keys the value from b wins'],
    ['a |= b or a.update(b)', 'Changes a in place'],
    ['{**a, **b}', 'A new dict, works before Python 3.9'],
    ['{k: v for ...}', 'A dict comprehension'],
    ['dict.fromkeys(keys, value)', 'Every key gets the same value'],
    ['dict(zip(keys, values))', 'Pairs keys and values from two lists']])}
{note('dict.fromkeys(keys, []) gives every key the same list object. Appending to one changes all of them. Use a comprehension {k: [] for k in keys} instead.', 'warn')}
''', kw=['merge dicts', 'union operator', 'update', 'dict comprehension', 'fromkeys', 'zip'])

K.lesson('keys', 'What can be a key', f'''
{run('keys')}
{note('Keys are compared with ==. Because 1 == 1.0 == True and they have the same hash, they are the same key: the dict keeps the first key object and the last value. Use one type for your keys.', 'exam')}
''', kw=['hashable', 'key types', '1 == 1.0', 'True as key', 'TypeError unhashable'])

K.lesson('hash', 'How a dict finds a key in one step', f'''
{viz('pydict')}
{run('internals')}
{wwh('A dict is a <b>hash table</b>. hash(key) gives a whole number, and that number decides where in the table the pair lives.',
     'Looking up a name in a list of a million names may need a million checks. A hash table needs about one or two, so dict lookup, insert and delete take O(1) time on average.',
     'CPython keeps two arrays. A small <b>index table</b> of size 8, 16, 32 ... holds entry numbers. An <b>entries</b> array holds (hash, key, value) in the order you added them, which is why dicts keep insertion order. The slot is hash mod size. If it is taken (a <b>collision</b>), Python probes other slots. When two thirds of the index table is used, the dict grows and every key is placed again.')}
{deep('Why hash(-1) is -2', '<p>Inside CPython, the C function that computes a hash returns &minus;1 to say "an error happened". So no object may have the hash &minus;1, and Python quietly uses &minus;2 for the number &minus;1. String hashes change every time Python starts (hash randomisation, PEP 456), to stop attackers from sending many keys that collide and make a web server slow.</p>')}
''', kw=['hash table', 'hashing', 'collision', 'probing', 'load factor', 'resize', 'compact dict', 'insertion order', 'hash randomisation'])

K.lesson('versus', 'dict compared with list and other mappings', f'''
{versus('Storing marks for 30 students', ['', 'two lists (names, marks)', 'list of pairs', 'dict'], [
    ['Get Ravi\'s mark', 'Find the index in names, then marks[i]: O(n)', 'Loop until the name matches: O(n)', 'marks["Ravi"]: O(1)'],
    ['Add a student', 'Append to both lists and keep them in step', 'Append a pair', 'marks["Zara"] = 80'],
    ['Repeated names', 'Allowed (can be a bug)', 'Allowed', 'Not possible, the key is unique'],
    ['Keeps order', 'Yes', 'Yes', 'Yes (insertion order)']],
    'whenever you find yourself searching a list for a name to get a value, use a dict.')}
{table(['Tool', 'Use it for'], [
    ['dict', 'Any key to value lookup'],
    ['collections.Counter', 'Counting things'],
    ['collections.defaultdict', 'Grouping, when missing keys need a starting value'],
    ['collections.OrderedDict', 'Moving keys to the end (move_to_end), an LRU cache'],
    ['types.MappingProxyType', 'A read only view of a dict']])}
''', kw=['dict vs list', 'Counter', 'defaultdict', 'OrderedDict', 'MappingProxyType'])

K.lesson('maths', 'The maths of hashing', f'''
{fxs(fx('Slot of a key', 'slot = hash(key) mod table size', 'Table sizes are powers of 2, so this is just the last few bits of the hash.', key=True),
     fx('Load factor', '&alpha; = used slots / table size &le; 2/3', 'A CPython dict with 8 slots holds at most 5 keys. The 6th key makes it grow.', key=True),
     fx('New table size', 'smallest power of 2 &ge; 3 &times; (number of keys)', 'When the 6th key arrives, 5 keys are stored: 3 &times; 5 = 15, so the new size is 16.'),
     fx('Expected probes for a lookup that hits (uniform hashing)', 'about (1/&alpha;) ln(1/(1 &minus; &alpha;))', 'At &alpha; = 2/3 this is about 1.6 probes, so lookups stay fast.'),
     fx('Chance that two of k keys share a slot of m (birthday problem)', '1 &minus; e<sup>&minus;k(k &minus; 1)/(2m)</sup>', 'With 23 people and 365 days the chance of a shared birthday is above 50 percent. Collisions are normal, so tables must handle them.'))}
{steps('Worked example: when does a dict grow?', [
    'Start with 8 slots. The limit is 2/3 of 8 = 5.33, so 5 keys fit.',
    'The 6th key finds the table full and it grows to 16 slots (limit 10).',
    'The 11th key grows it to 32 slots (limit 21), and the 22nd key to 64.',
    eq('Growth at keys 6, 11 and 22, which matches the sizes printed by the program above')])}
''', kw=['hash function', 'load factor', 'birthday problem', 'probes', 'power of two', 'resize'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A dict maps keys to values. d[key] reads, d[key] = value writes, and for key in d loops over the keys.</p>',
    '<p>Use get with a default, pop, update and items(). Count with get(k, 0) + 1 and group with a dict of lists. Keys must be hashable and unique.</p>',
    '<p>Use Counter and defaultdict, merge with |, build with comprehensions, never change the size while looping, and know that views are live. A nested dict is JSON.</p>',
    '<p>CPython dicts are compact, ordered hash tables with a separate sparse index and a dense entry array (Raymond Hettinger, Python 3.6), open addressing with perturbed probing, and key sharing between instances of the same class. Hash flooding attacks are why string hashes use SipHash with a random key.</p>')}
{grow('Make a dict, read, add and change values, and loop over keys and items.',
      'Count and group with a dict, use get and setdefault, and work with nested dicts and JSON.',
      'Explain hashing, collisions, load factor and growth, choose Counter, defaultdict or OrderedDict, and reason about the cost of every operation.')}
''', kw=['beginner', 'expert', 'compact dict', 'SipHash', 'key sharing'])

lc(1, 'Two Sum', 'two-sum', 'e', 'Dict of seen values', 'For each number x, the partner is target &minus; x. Keep a dict from value to index of the numbers seen so far.', r'''
def two_sum(nums, target):
    seen = {}
    for i in range(len(nums)):
        need = target - nums[i]
        if need in seen:
            return [seen[need], i]
        seen[nums[i]] = i
    return []
''', [('two_sum([2, 7, 11, 15], 9)', [0, 1]), ('two_sum([3, 2, 4], 6)', [1, 2]), ('two_sum([3, 3], 6)', [0, 1])])
lc(242, 'Valid Anagram', 'valid-anagram', 'e', 'Count letters', 'Two words are anagrams when every letter appears the same number of times.', r'''
def is_anagram(s, t):
    if len(s) != len(t):
        return False
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in t:
        if counts.get(ch, 0) == 0:
            return False
        counts[ch] = counts[ch] - 1
    return True
''', [('is_anagram("anagram", "nagaram")', True), ('is_anagram("rat", "car")', False)])
lc(387, 'First Unique Character in a String', 'first-unique-character-in-a-string', 'e', 'Count, then scan again', 'First count every letter. Then walk the text again and return the first index whose letter count is 1.', r'''
def first_uniq_char(s):
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    for i in range(len(s)):
        if counts[s[i]] == 1:
            return i
    return -1
''', [('first_uniq_char("leetcode")', 0), ('first_uniq_char("loveleetcode")', 2), ('first_uniq_char("aabb")', -1)])
lc(383, 'Ransom Note', 'ransom-note', 'e', 'Count and spend', 'Count the magazine letters. Each letter of the note uses one up.', r'''
def can_construct(ransom_note, magazine):
    counts = {}
    for ch in magazine:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in ransom_note:
        if counts.get(ch, 0) == 0:
            return False
        counts[ch] = counts[ch] - 1
    return True
''', [('can_construct("a", "b")', False), ('can_construct("aa", "ab")', False), ('can_construct("aa", "aab")', True)])
lc(1512, 'Number of Good Pairs', 'number-of-good-pairs', 'e', 'Count as you go', 'Each new copy of a value makes a pair with every earlier copy, so add the count so far before increasing it.', r'''
def num_identical_pairs(nums):
    counts = {}
    pairs = 0
    for x in nums:
        pairs = pairs + counts.get(x, 0)
        counts[x] = counts.get(x, 0) + 1
    return pairs
''', [('num_identical_pairs([1, 2, 3, 1, 1, 3])', 4), ('num_identical_pairs([1, 1, 1, 1])', 6), ('num_identical_pairs([1, 2, 3])', 0)])
lc(169, 'Majority Element', 'majority-element', 'e', 'Count, or Boyer Moore voting', 'Count each value and return the one seen more than n/2 times. The O(1) memory trick is the Boyer Moore vote.', r'''
def majority_element(nums):
    candidate = None
    votes = 0
    for x in nums:
        if votes == 0:
            candidate = x
        if x == candidate:
            votes = votes + 1
        else:
            votes = votes - 1
    return candidate
''', [('majority_element([3, 2, 3])', 3), ('majority_element([2, 2, 1, 1, 1, 2, 2])', 2)])
lc(205, 'Isomorphic Strings', 'isomorphic-strings', 'e', 'Two dicts, one per direction', 'Each letter of s must always map to the same letter of t, and no two letters may map to the same one.', r'''
def is_isomorphic(s, t):
    s_to_t = {}
    t_to_s = {}
    for a, b in zip(s, t):
        if a in s_to_t and s_to_t[a] != b:
            return False
        if b in t_to_s and t_to_s[b] != a:
            return False
        s_to_t[a] = b
        t_to_s[b] = a
    return True
''', [('is_isomorphic("egg", "add")', True), ('is_isomorphic("foo", "bar")', False), ('is_isomorphic("badc", "baba")', False)])
lc(290, 'Word Pattern', 'word-pattern', 'e', 'Two dicts, one per direction', 'Split the text into words. Then it is Isomorphic Strings with letters on one side and words on the other.', r'''
def word_pattern(pattern, s):
    words = s.split()
    if len(words) != len(pattern):
        return False
    letter_to_word = {}
    word_to_letter = {}
    for letter, word in zip(pattern, words):
        if letter_to_word.get(letter, word) != word:
            return False
        if word_to_letter.get(word, letter) != letter:
            return False
        letter_to_word[letter] = word
        word_to_letter[word] = letter
    return True
''', [('word_pattern("abba", "dog cat cat dog")', True), ('word_pattern("abba", "dog cat cat fish")', False), ('word_pattern("aaaa", "dog cat cat dog")', False)])
lc(49, 'Group Anagrams', 'group-anagrams', 'm', 'Group by a sorted key', 'Anagrams have the same letters in sorted order. Use that sorted text as the dict key and a list of words as the value.', r'''
def group_anagrams(strs):
    groups = {}
    for word in strs:
        key = "".join(sorted(word))
        if key not in groups:
            groups[key] = []
        groups[key].append(word)
    return list(groups.values())
''', [('sorted(sorted(g) for g in group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))', [['ate', 'eat', 'tea'], ['bat'], ['nat', 'tan']]), ('group_anagrams([""])', [['']])])
lc(347, 'Top K Frequent Elements', 'top-k-frequent-elements', 'm', 'Count, then bucket by count', 'Count each number. Put numbers into buckets by their count, then read the buckets from the highest count down.', r'''
def top_k_frequent(nums, k):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    buckets = []
    for _ in range(len(nums) + 1):
        buckets.append([])
    for value, count in counts.items():
        buckets[count].append(value)
    result = []
    for count in range(len(nums), 0, -1):
        for value in buckets[count]:
            result.append(value)
            if len(result) == k:
                return result
    return result
''', [('sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2))', [1, 2]), ('top_k_frequent([1], 1)', [1])])
lc(560, 'Subarray Sum Equals K', 'subarray-sum-equals-k', 'm', 'Prefix sums in a dict', 'A part from i to j sums to k when prefix[j] &minus; prefix[i] = k. Count how often each prefix sum has appeared.', r'''
def subarray_sum(nums, k):
    seen = {0: 1}
    total = 0
    count = 0
    for x in nums:
        total = total + x
        count = count + seen.get(total - k, 0)
        seen[total] = seen.get(total, 0) + 1
    return count
''', [('subarray_sum([1, 1, 1], 2)', 2), ('subarray_sum([1, 2, 3], 3)', 2), ('subarray_sum([1, -1, 0], 0)', 3)])

K.lesson('leetcode', 'LeetCode practice', leet(), kw=['LeetCode', 'two sum', 'valid anagram', 'group anagrams', 'top k frequent', 'subarray sum equals k', 'hash map'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>dict</b> maps unique, hashable keys to any values. Write it as {key: value, ...}.',
    'd[k] reads (KeyError if missing), d.get(k, default) reads safely, d[k] = v adds or replaces.',
    'Remove with del, pop and popitem. Merge with update, | and |=.',
    'for k in d gives keys. Use values() and items() for the rest. Views are live, and changing the size while looping is an error.',
    'Count with d[k] = d.get(k, 0) + 1 or Counter. Group with a dict of lists or defaultdict(list).',
    'A dict is a hash table: lookup, insert and delete are O(1) on average. It grows when two thirds full and keeps insertion order.',
    '1, 1.0 and True are the same key. Lists cannot be keys.'],
    'Step 4 starts with functions: def, parameters, return values and every way to pass arguments.')}
{files('Three tasks: a word frequency table, invert a dict that has repeated values, and a tiny inventory with orders.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does d = {"a": 1} then d["b"] = 2 do?', ['Error', 'Adds the key "b"', 'Replaces "a"', 'Nothing'], 1, 'New key.', 'Assigning to a new key adds it.')
K.quiz('e', 'What is {"a": 1, "b": 2}.get("c")?', ['0', 'None', 'KeyError', '""'], 1, 'No default given.', 'get returns None when the key is missing.')
K.quiz('e', 'What does for x in {"a": 1, "b": 2}: print(x) print?', ['1 and 2', 'a and b', 'The pairs', 'Error'], 1, 'Looping gives keys.', 'A dict loop gives its keys.')
K.quiz('m', 'What is len({"a": 1, "a": 2})?', ['2', '1', 'Error', '0'], 1, 'Keys are unique.', 'The second "a" replaces the first value.')
K.quiz('m', 'What is {"a": 1, "a": 2}["a"]?', ['1', '2', '[1, 2]', 'Error'], 1, 'The last one wins.', 'The later value replaces the earlier one.')
K.quiz('m', 'Which cannot be a dict key?', ['"name"', '42', '(1, 2)', '[1, 2]'], 3, 'Hashable only.', 'A list can change, so it is not hashable.')
K.quiz('m', 'What does 2 in {1: 2, 3: 4} give?', ['True', 'False', 'Error', '1'], 1, 'in checks keys.', '2 is a value, not a key.')
K.quiz('m', 'What is {"x": 1} | {"x": 5, "y": 2}?', ['{"x": 1, "y": 2}', '{"x": 5, "y": 2}', 'TypeError', '{"x": 6, "y": 2}'], 1, 'The right side wins.', 'For equal keys the value on the right is kept.')
K.quiz('h', 'What is len({1: "a", 1.0: "b", True: "c"})?', ['3', '1', '2', 'Error'], 1, '1 == 1.0 == True.', 'They are equal and hash the same, so they are one key.')
K.quiz('h', 'd = dict.fromkeys(["a", "b"], []) then d["a"].append(1). What is d["b"]?', ['[]', '[1]', 'None', 'Error'], 1, 'One shared list.', 'fromkeys uses the same list object for every key.')
K.quiz('h', 'A CPython dict starts with 8 slots. Which key added makes it grow for the first time?', ['The 8th', 'The 6th', 'The 5th', 'The 9th'], 1, 'Two thirds of 8.', 'At most 5 keys fit in 8 slots, so the 6th makes it grow.')
K.quiz('x', 'In the style of a Stanford CS106B exam: what is the average time to look up a key in a hash table with a good hash function and a load factor kept below a constant?', ['O(log n)', 'O(1)', 'O(n)', 'O(n log n)'], 1, 'The load factor is bounded.', 'Expected probes depend only on the load factor, not on n.')
K.quiz('x', 'In the style of an MIT 6.006 problem: 23 random keys go into a table of 365 slots. Is a collision more likely than not?', ['No, about 6 percent', 'Yes, just over 50 percent', 'No, it is impossible', 'Yes, about 99 percent'], 1, 'The birthday problem.', '1 &minus; e<sup>&minus;23 &times; 22 / 730</sup> is about 0.50, and the exact value is 0.507.')

K.calc('e', 'len({"a": 1, "b": 2, "c": 3})?', '3', 'Count the keys.', ['Three keys.', 'a, b, c.', eq('3')], check=3)
K.calc('e', 'sum({"a": 10, "b": 20, "c": 5}.values())?', '35', 'Add the values.', ['10 + 20 + 5.', 'values() gives the numbers.', eq('35')], check=35)
K.calc('e', 'Counter("banana")["a"]?', '3', 'Count the a letters.', ['b, a, n, a, n, a.', 'Three a letters.', eq('3')], check='banana'.count('a'))
K.calc('m', 'How many keys fit in a CPython dict of 16 slots before it grows?', '10', '&lfloor;2 &times; 16 / 3&rfloor;.', ['2/3 of 16 = 10.67.', 'Round down.', eq('10')], check=(2 * 16) // 3)
K.calc('m', 'Slot for the key 19 in a table of 8 slots (hash(19) = 19).', '3', '19 mod 8.', ['19 = 2 &times; 8 + 3.', 'Remainder 3.', eq('3')], check=19 % 8)
K.calc('m', 'Good pairs in [1, 1, 1, 1, 2, 2]: pairs i &lt; j with equal values.', '7', 'C(4, 2) + C(2, 2).', ['Four 1s give 4 &times; 3 / 2 = 6.', 'Two 2s give 1.', eq('7')], check=6 + 1)
K.calc('m', 'Number of different keys in {n % 5: n for n in range(100)}.', '5', 'Remainders 0 to 4.', ['n % 5 is one of 0, 1, 2, 3, 4.', 'Repeated keys replace values.', eq('5')], check=len({n % 5: n for n in range(100)}))
K.calc('h', 'Expected hit probes at load factor 2/3: (1/&alpha;) ln(1/(1 &minus; &alpha;)), to 2 decimal places.', '1.65', '1.5 &times; ln 3.', ['1/&alpha; = 1.5.', 'ln(1/(1/3)) = ln 3 = 1.0986.', eq('1.5 &times; 1.0986 = 1.65')], check=round(1.5 * 1.0986122886681098, 2))
K.calc('h', 'Approximate chance (percent, whole number) of at least one collision with 10 keys in 100 slots: 1 &minus; e<sup>&minus;k(k &minus; 1)/(2m)</sup>.', '36', 'k = 10, m = 100.', ['k(k &minus; 1)/(2m) = 90/200 = 0.45.', 'e<sup>&minus;0.45</sup> = 0.638.', eq('1 &minus; 0.638 = 0.362, about 36 percent')], check=round(100 * (1 - 2.718281828459045 ** -0.45)))
K.calc('x', 'In the style of a Carnegie Mellon 15-210 question: a dict grows its index table at keys 6, 11 and 22, starting from 8 slots. How many slots does it have after adding key number 43? (Each growth goes to the next power of 2 that is at least 3 times the keys already stored.)', '128', 'Find the growth points.', ['Growth at 6 (to 16), 11 (to 32), 22 (to 64).', 'A table of 64 holds &lfloor;2 &times; 64/3&rfloor; = 42 keys, so key 43 makes it grow.', '3 &times; 42 = 126, and the next power of 2 is 128.', eq('128 slots')], check=128)

K.assign('freq', 'e', 'Word frequency table',
         '<p>Write <code>word_freq(text)</code> that returns a dict from each lower case word to how many times it appears. Split on spaces with split().</p>',
         '''
def word_freq(text):
    # your code here
    pass
''', [('word_freq("The cat the hat")', {'the': 2, 'cat': 1, 'hat': 1}), ('word_freq("")', {}), ('word_freq("a a a")', {'a': 3})],
         '''
def word_freq(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts
''', 'Lower case the text first. Then use counts[word] = counts.get(word, 0) + 1.', '<p>This is the core of every search engine index and of the bag of words model in NLP.</p>')
K.assign('invert', 'm', 'Invert a dict with repeated values',
         '<p>Write <code>invert(d)</code> that returns a new dict from each value of d to a sorted list of the keys that had that value. {"a": 1, "b": 2, "c": 1} becomes {1: ["a", "c"], 2: ["b"]}.</p>',
         '''
def invert(d):
    # your code here
    pass
''', [('invert({"a": 1, "b": 2, "c": 1})', {1: ['a', 'c'], 2: ['b']}), ('invert({})', {}), ('invert({"x": "y"})', {'y': ['x']})],
         '''
def invert(d):
    result = {}
    for key, value in d.items():
        if value not in result:
            result[value] = []
        result[value].append(key)
    for value in result:
        result[value].sort()
    return result
''', 'Loop over d.items(). Use the value as the new key and a list as the new value, then sort each list.', '<p>A plain {v: k for k, v in d.items()} loses keys when values repeat. Grouping into lists keeps them all.</p>')
K.assign('shop', 'm', 'A tiny inventory',
         '<p>Write <code>place_order(stock, order)</code>. Both are dicts from item to quantity. If every item of the order is in stock in enough quantity, take the quantities away from stock and return True. Otherwise change nothing and return False. Return the result and stock as a tuple.</p>',
         '''
def place_order(stock, order):
    # your code here
    pass
''', [('place_order({"pen": 5, "ink": 2}, {"pen": 2})', (True, {'pen': 3, 'ink': 2})), ('place_order({"pen": 5}, {"pen": 6})', (False, {'pen': 5})), ('place_order({"pen": 5}, {"cap": 1})', (False, {'pen': 5}))],
         '''
def place_order(stock, order):
    for item, qty in order.items():
        if stock.get(item, 0) < qty:
            return False, stock
    for item, qty in order.items():
        stock[item] = stock[item] - qty
    return True, stock
''', 'Check every item first with stock.get(item, 0). Change the stock only after all checks pass.', '<p>"Check everything, then change everything" keeps the data correct when one item fails. Databases call this a transaction (Advanced 6.2).</p>')

K.must('Dicts', 'Key to value mapping. Keys unique and hashable, values anything. Ordered by insertion since 3.7.')
K.must('Read safely', 'd[k] raises KeyError. d.get(k, default) does not. k in d checks keys only.')
K.must('Change', 'd[k] = v adds or replaces. del d[k], d.pop(k, default), d.popitem() (last added), update, |, |=.')
K.must('Loop', 'for k in d (keys), d.values(), d.items(). Do not add or remove keys while looping, use list(d).')
K.must('Patterns', 'Count: d[k] = d.get(k, 0) + 1 or Counter. Group: dict of lists or defaultdict(list). Two Sum: dict of seen values.')

T = K.topic(
    slug='py-dicts', topic='py-dicts', step=(3, 'Data collections', 'py-c3', 'Store and work with many values: strings, lists, tuples, sets and dictionaries.', 'Beginner'),
    title='Dictionaries: keys, values and hash tables', short='Dictionaries', badge='3.4', minutes=65,
    lead='Look things up by name instead of by position. Learn to make and change dicts, read keys safely, loop over keys, values and items, count and group, nest dicts like JSON, merge them, and see the hash table that finds any key in one step.',
    desc='dict literals and dict(), lookup and KeyError, adding and changing values, del, pop, popitem, update, get and setdefault, looping over keys, values and items, views, RuntimeError when changing size, counting with get and Counter, grouping with defaultdict, nested dicts and JSON, merging with | and update, dict comprehensions, fromkeys, hashable keys and 1 == 1.0 == True, hash tables, collisions, load factor, resizing and the birthday problem.',
    summary='dict basics, get and setdefault, keys values items, counting, grouping, nesting and JSON, merging, hash table internals.',
    keywords=['dictionary', 'dict', 'key value', 'get', 'items', 'Counter', 'defaultdict', 'JSON', 'hash table', 'hashing', 'collision', 'PCEP'],
    recap='<p>A dict finds a value by its key in one step. Count with it, group with it, nest it like JSON, and remember that keys must be hashable and unique.</p>',
    added='2026-11-07', leet=leet_items())
