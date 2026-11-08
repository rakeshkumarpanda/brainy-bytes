# 5.1 Django REST framework: JSON APIs on top of Django
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== 1408. String Matching in an Array (Easy)
# https://leetcode.com/problems/string-matching-in-an-array/
# Pattern: Check each word against the others with in
# Idea: Like the SearchFilter of an API: a word is a match when it appears inside another word. Two
# loops and the in operator are enough for small lists.

def string_matching(words):
    result = []
    for word in words:
        for other in words:
            if other != word and word in other:
                result.append(word)
                break
    return result


# ================================================================== 1207. Unique Number of Occurrences (Easy)
# https://leetcode.com/problems/unique-number-of-occurrences/
# Pattern: Counter, then compare the counts with a set
# Idea: A validation rule in a serializer often counts things. Count each value with Counter, then
# the counts are unique when a set of them has the same size.

from collections import Counter


def unique_occurrences(arr):
    counts = list(Counter(arr).values())
    return len(counts) == len(set(counts))


# ================================================================== 1640. Check Array Formation Through Concatenation (Easy)
# https://leetcode.com/problems/check-array-formation-through-concatenation/
# Pattern: A dict from first number to piece
# Idea: Like joining pages of API results back into one list. Each piece starts with a different
# number, so a dict from first number to piece finds the next piece at once.

def can_form_array(arr, pieces):
    by_first = {piece[0]: piece for piece in pieces}
    i = 0
    while i < len(arr):
        piece = by_first.get(arr[i])
        if piece is None or arr[i:i + len(piece)] != piece:
            return False
        i += len(piece)
    return True


# ================================================================== 911. Online Election (Medium)
# https://leetcode.com/problems/online-election/
# Pattern: Precompute the leader after each vote, then binary search the time
# Idea: Like an API that answers "what was true at time t". Work out the leader after every vote
# once, then each question is a binary search on the times.

import bisect
from collections import defaultdict


class TopVotedCandidate:
    def __init__(self, persons, times):
        self.times = times
        self.leaders = []
        votes = defaultdict(int)
        leader = None
        for person in persons:
            votes[person] += 1
            if leader is None or votes[person] >= votes[leader]:
                leader = person
            self.leaders.append(leader)

    def q(self, t):
        i = bisect.bisect_right(self.times, t) - 1
        return self.leaders[i]


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 2080. Range Frequency Queries (Medium)
# https://leetcode.com/problems/range-frequency-queries/
# Pattern: Positions per value, then two binary searches
# Idea: Like an API filter ?value=4&from=1&to=2. Keep the sorted positions of each value, then count
# the positions inside the range with bisect.

import bisect
from collections import defaultdict


class RangeFreqQuery:
    def __init__(self, arr):
        self.positions = defaultdict(list)
        for i, value in enumerate(arr):
            self.positions[value].append(i)

    def query(self, left, right, value):
        places = self.positions.get(value, [])
        return bisect.bisect_right(places, right) - bisect.bisect_left(places, left)


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 2707. Extra Characters in a String (Medium)
# https://leetcode.com/problems/extra-characters-in-a-string/
# Pattern: Dynamic programming from the end of the string
# Idea: Like splitting a URL into known resource names. best[i] is the fewest extra letters from
# position i. Either skip the letter at i, or jump over a dictionary word that starts at i.

def min_extra_char(s, dictionary):
    words = set(dictionary)
    n = len(s)
    best = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        best[i] = best[i + 1] + 1
        for end in range(i + 1, n + 1):
            if s[i:end] in words:
                best[i] = min(best[i], best[end])
    return best[0]


# ================================================================== 381. Insert Delete GetRandom O(1) - Duplicates allowed (Hard)
# https://leetcode.com/problems/insert-delete-getrandom-o1-duplicates-allowed/
# Pattern: A list plus a dict of index sets, swap with the last item to delete
# Idea: Like a load balancer that picks a random server where some servers count twice. The list
# gives random choice in O(1), the dict of positions finds an item to remove, and swapping with the
# last item keeps removal O(1).

import random
from collections import defaultdict


class RandomizedCollection:
    def __init__(self):
        self.items = []
        self.where = defaultdict(set)

    def insert(self, val):
        self.where[val].add(len(self.items))
        self.items.append(val)
        return len(self.where[val]) == 1

    def remove(self, val):
        if not self.where[val]:
            return False
        i = self.where[val].pop()
        last = self.items[-1]
        self.items[i] = last
        self.where[last].add(i)
        self.where[last].discard(len(self.items) - 1)
        self.items.pop()
        return True

    def getRandom(self):
        return random.choice(self.items)


def random_check():
    """The random part cannot have one fixed answer, so this checks that it only returns stored values."""
    bag = RandomizedCollection()
    for value in [1, 1, 2]:
        bag.insert(value)
    bag.remove(1)
    return sorted(set(bag.getRandom() for _ in range(50)))


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 715. Range Module (Hard)
# https://leetcode.com/problems/range-module/
# Pattern: A sorted list of disjoint intervals
# Idea: Like a cache that remembers which ranges of ids it already fetched from an API. Keep the
# ranges sorted and merged, and use bisect to find the ones that touch a new range.

import bisect


class RangeModule:
    def __init__(self):
        self.edges = []                      # [start1, end1, start2, end2, ...] sorted, half open ranges

    def addRange(self, left, right):
        i = bisect.bisect_left(self.edges, left)
        j = bisect.bisect_right(self.edges, right)
        middle = []
        if i % 2 == 0:
            middle.append(left)
        if j % 2 == 0:
            middle.append(right)
        self.edges[i:j] = middle

    def queryRange(self, left, right):
        i = bisect.bisect_right(self.edges, left)
        j = bisect.bisect_left(self.edges, right)
        return i == j and i % 2 == 1

    def removeRange(self, left, right):
        i = bisect.bisect_left(self.edges, left)
        j = bisect.bisect_right(self.edges, right)
        middle = []
        if i % 2 == 1:
            middle.append(left)
        if j % 2 == 1:
            middle.append(right)
        self.edges[i:j] = middle


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 2276. Count Integers in Intervals (Hard)
# https://leetcode.com/problems/count-integers-in-intervals/
# Pattern: Merge intervals as they arrive and keep a running total
# Idea: Like counting how many ids a set of API keys may read. Keep disjoint intervals sorted by
# start, merge every new one with the ones it touches, and update the total on the way.

import bisect


class CountIntervals:
    def __init__(self):
        self.starts = []
        self.ends = []
        self.total = 0

    def add(self, left, right):
        i = bisect.bisect_left(self.ends, left)          # the first interval that ends at or after left
        while i < len(self.starts) and self.starts[i] <= right:
            left = min(left, self.starts[i])
            right = max(right, self.ends[i])
            self.total -= self.ends[i] - self.starts[i] + 1
            del self.starts[i]
            del self.ends[i]
        self.starts.insert(i, left)
        self.ends.insert(i, right)
        self.total += right - left + 1

    def count(self):
        return self.total


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 1622. Fancy Sequence (Hard)
# https://leetcode.com/problems/fancy-sequence/
# Pattern: Store one lazy formula a × x + b for every value
# Idea: Like update(price=F("price") * 2 + 1) for every row at once: never touch each value. Keep
# one global formula and store each new value "undone" with the modular inverse, so the formula
# applies to it correctly later.

MOD = 10 ** 9 + 7


class Fancy:
    def __init__(self):
        self.values = []
        self.mul = 1                         # every real value = stored * mul + add
        self.add = 0

    def append(self, val):
        inverse = pow(self.mul, MOD - 2, MOD)            # Fermat: mul ** (MOD - 2) is 1 / mul
        self.values.append((val - self.add) * inverse % MOD)

    def addAll(self, inc):
        self.add = (self.add + inc) % MOD

    def multAll(self, m):
        self.mul = self.mul * m % MOD
        self.add = self.add * m % MOD

    def getIndex(self, idx):
        if idx >= len(self.values):
            return -1
        return (self.values[idx] * self.mul + self.add) % MOD


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


if __name__ == "__main__":
    results = []
    results.append(check("1408. String Matching in an Array", [('string_matching(["mass", "as", "hero", "superhero"])', ['as', 'hero']), ('string_matching(["leetcode", "et", "code"])', ['et', 'code']), ('string_matching(["blue", "green", "bu"])', [])]))
    results.append(check("1207. Unique Number of Occurrences", [('unique_occurrences([1, 2, 2, 1, 1, 3])', True), ('unique_occurrences([1, 2])', False), ('unique_occurrences([-3, 0, 1, -3, 1, 1, 1, -3, 10, 0])', True)]))
    results.append(check("1640. Check Array Formation Through Concatenation", [('can_form_array([15, 88], [[88], [15]])', True), ('can_form_array([49, 18, 16], [[16, 18, 49]])', False), ('can_form_array([91, 4, 64, 78], [[78], [4, 64], [91]])', True)]))
    results.append(check("911. Online Election", [('play(TopVotedCandidate, ["TopVotedCandidate", "q", "q", "q", "q", "q", "q"], [[[0, 1, 1, 0, 0, 1, 0], [0, 5, 10, 15, 20, 25, 30]], [3], [12], [25], [15], [24], [8]])', [None, 0, 1, 1, 0, 0, 1])]))
    results.append(check("2080. Range Frequency Queries", [('play(RangeFreqQuery, ["RangeFreqQuery", "query", "query"], [[[12, 33, 4, 56, 22, 2, 34, 33, 22, 12, 34, 56]], [1, 2, 4], [0, 11, 33]])', [None, 1, 2])]))
    results.append(check("2707. Extra Characters in a String", [('min_extra_char("leetscode", ["leet", "code", "leetcode"])', 1), ('min_extra_char("sayhelloworld", ["hello", "world"])', 3)]))
    results.append(check("381. Insert Delete GetRandom O(1) - Duplicates allowed", [('play(RandomizedCollection, ["RandomizedCollection", "insert", "insert", "insert", "remove", "remove", "remove"], [[], [1], [1], [2], [1], [1], [1]])', [None, True, False, True, True, True, False]), ('random_check()', [1, 2])]))
    results.append(check("715. Range Module", [('play(RangeModule, ["RangeModule", "addRange", "removeRange", "queryRange", "queryRange", "queryRange"], [[], [10, 20], [14, 16], [10, 14], [13, 15], [16, 17]])', [None, None, None, True, False, True])]))
    results.append(check("2276. Count Integers in Intervals", [('play(CountIntervals, ["CountIntervals", "add", "add", "count", "add", "count"], [[], [2, 3], [7, 10], [], [5, 8], []])', [None, None, None, 6, None, 8])]))
    results.append(check("1622. Fancy Sequence", [('play(Fancy, ["Fancy", "append", "addAll", "append", "multAll", "getIndex", "addAll", "append", "multAll", "getIndex", "getIndex", "getIndex"], [[], [2], [3], [7], [2], [0], [3], [10], [2], [0], [1], [2]])', [None, None, None, None, None, 10, None, None, None, 26, 34, 20])]))
    if all(results):
        print("Every solution passes its tests.")
