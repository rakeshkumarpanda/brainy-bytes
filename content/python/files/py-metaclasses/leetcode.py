# 1.5 Metaprogramming: type, class hooks and metaclasses
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


# ================================================================== 211. Design Add and Search Words Data Structure (Medium)
# https://leetcode.com/problems/design-add-and-search-words-data-structure/
# Pattern: A trie of dicts, search with recursion
# Idea: Store each word letter by letter in nested dicts. A dot must try every child, so search with
# a small recursive helper.

class WordDictionary:
    def __init__(self):
        self.root = {}

    def addWord(self, word):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node["$"] = True

    def search(self, word):
        return self.find(self.root, word, 0)

    def find(self, node, word, i):
        if i == len(word):
            return "$" in node
        ch = word[i]
        if ch == ".":
            for key in node:
                if key != "$" and self.find(node[key], word, i + 1):
                    return True
            return False
        return ch in node and self.find(node[ch], word, i + 1)


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 380. Insert Delete GetRandom O(1) (Medium)
# https://leetcode.com/problems/insert-delete-getrandom-o1/
# Pattern: A list plus a dict of positions
# Idea: The list allows a random pick. The dict maps each value to its index. To remove, move the
# last value into the hole and pop.

import random


class RandomizedSet:
    def __init__(self):
        self.values = []
        self.where = {}

    def insert(self, val):
        if val in self.where:
            return False
        self.where[val] = len(self.values)
        self.values.append(val)
        return True

    def remove(self, val):
        if val not in self.where:
            return False
        index = self.where.pop(val)
        last = self.values.pop()
        if index < len(self.values):
            self.values[index] = last
            self.where[last] = index
        return True

    def getRandom(self):
        return random.choice(self.values)


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 2502. Design Memory Allocator (Medium)
# https://leetcode.com/problems/design-memory-allocator/
# Pattern: Scan a list of owners
# Idea: Keep one owner id per memory unit (0 means free). allocate looks for the first run of free
# units that is long enough.

class Allocator:
    def __init__(self, n):
        self.memory = [0] * n

    def allocate(self, size, mID):
        run = 0
        for i in range(len(self.memory)):
            if self.memory[i] == 0:
                run += 1
                if run == size:
                    start = i - size + 1
                    for j in range(start, i + 1):
                        self.memory[j] = mID
                    return start
            else:
                run = 0
        return -1

    def freeMemory(self, mID):
        count = 0
        for i in range(len(self.memory)):
            if self.memory[i] == mID:
                self.memory[i] = 0
                count += 1
        return count


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 2353. Design a Food Rating System (Medium)
# https://leetcode.com/problems/design-a-food-rating-system/
# Pattern: A heap per cuisine with lazy deletion
# Idea: Push (-rating, name) into the heap of the cuisine. When asked, pop entries whose rating is
# out of date before reading the top.

import heapq


class FoodRatings:
    def __init__(self, foods, cuisines, ratings):
        self.rating = {}
        self.cuisine = {}
        self.heaps = {}
        for food, cuisine, rating in zip(foods, cuisines, ratings):
            self.rating[food] = rating
            self.cuisine[food] = cuisine
            heapq.heappush(self.heaps.setdefault(cuisine, []), (-rating, food))

    def changeRating(self, food, newRating):
        self.rating[food] = newRating
        heapq.heappush(self.heaps[self.cuisine[food]], (-newRating, food))

    def highestRated(self, cuisine):
        heap = self.heaps[cuisine]
        while -heap[0][0] != self.rating[heap[0][1]]:
            heapq.heappop(heap)                # an old rating, throw it away
        return heap[0][1]


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 2671. Frequency Tracker (Medium)
# https://leetcode.com/problems/frequency-tracker/
# Pattern: Two counters
# Idea: Count each number, and also count how many numbers have each frequency. Then hasFrequency is
# one dict lookup.

class FrequencyTracker:
    def __init__(self):
        self.count = {}
        self.freq = {}

    def change(self, number, step):
        old = self.count.get(number, 0)
        new = old + step
        if new < 0:
            return
        self.freq[old] = self.freq.get(old, 0) - 1
        self.freq[new] = self.freq.get(new, 0) + 1
        self.count[number] = new

    def add(self, number):
        self.change(number, 1)

    def deleteOne(self, number):
        self.change(number, -1)

    def hasFrequency(self, frequency):
        return self.freq.get(frequency, 0) > 0


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 1993. Operations on Tree (Medium)
# https://leetcode.com/problems/operations-on-tree/
# Pattern: Parents list, children lists, a lock dict
# Idea: lock and unlock check one node. upgrade checks that no ancestor is locked and at least one
# descendant is, then unlocks every descendant.

class LockingTree:
    def __init__(self, parent):
        self.parent = parent
        self.children = [[] for i in range(len(parent))]
        for node in range(1, len(parent)):
            self.children[parent[node]].append(node)
        self.locked = {}                       # node: user

    def lock(self, num, user):
        if num in self.locked:
            return False
        self.locked[num] = user
        return True

    def unlock(self, num, user):
        if self.locked.get(num) != user:
            return False
        del self.locked[num]
        return True

    def upgrade(self, num, user):
        node = num
        while node != -1:
            if node in self.locked:
                return False
            node = self.parent[node]
        found = False
        stack = list(self.children[num])
        while stack:
            node = stack.pop()
            if node in self.locked:
                del self.locked[node]
                found = True
            stack.extend(self.children[node])
        if found:
            self.locked[num] = user
        return found


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 1357. Apply Discount Every n Orders (Medium)
# https://leetcode.com/problems/apply-discount-every-n-orders/
# Pattern: A counter and a price dict
# Idea: Count customers. Every n-th bill is multiplied by (100 − discount) / 100.

class Cashier:
    def __init__(self, n, discount, products, prices):
        self.n = n
        self.discount = discount
        self.price = dict(zip(products, prices))
        self.customers = 0

    def getBill(self, product, amount):
        self.customers += 1
        total = 0
        for p, a in zip(product, amount):
            total += self.price[p] * a
        if self.customers % self.n == 0:
            total = total * (100 - self.discount) / 100
        return total


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 1476. Subrectangle Queries (Medium)
# https://leetcode.com/problems/subrectangle-queries/
# Pattern: Keep a list of updates
# Idea: Instead of painting every cell, remember each update. getValue checks the updates from
# newest to oldest and falls back to the original grid.

class SubrectangleQueries:
    def __init__(self, rectangle):
        self.grid = rectangle
        self.updates = []

    def updateSubrectangle(self, row1, col1, row2, col2, newValue):
        self.updates.append((row1, col1, row2, col2, newValue))

    def getValue(self, row, col):
        for r1, c1, r2, c2, value in reversed(self.updates):
            if r1 <= row <= r2 and c1 <= col <= c2:
                return value
        return self.grid[row][col]


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 2166. Design Bitset (Medium)
# https://leetcode.com/problems/design-bitset/
# Pattern: A list of bits plus a flipped flag
# Idea: flip only toggles a flag, so it is O(1). Keep a count of ones and fix it up when flip
# happens.

class Bitset:
    def __init__(self, size):
        self.bits = [0] * size
        self.flipped = False
        self.ones = 0

    def value(self, idx):
        return self.bits[idx] ^ self.flipped

    def fix(self, idx):
        if self.value(idx) == 0:
            self.bits[idx] ^= 1
            self.ones += 1

    def unfix(self, idx):
        if self.value(idx) == 1:
            self.bits[idx] ^= 1
            self.ones -= 1

    def flip(self):
        self.flipped = not self.flipped
        self.ones = len(self.bits) - self.ones

    def all(self):
        return self.ones == len(self.bits)

    def one(self):
        return self.ones > 0

    def count(self):
        return self.ones

    def toString(self):
        text = ""
        for idx in range(len(self.bits)):
            text += str(int(self.value(idx)))
        return text


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 2424. Longest Uploaded Prefix (Medium)
# https://leetcode.com/problems/longest-uploaded-prefix/
# Pattern: A set and a pointer that only moves forward
# Idea: Remember uploaded videos in a set. The prefix pointer moves right while the next video is
# there. Each video is passed once in total.

class LUPrefix:
    def __init__(self, n):
        self.uploaded = set()
        self.prefix = 0

    def upload(self, video):
        self.uploaded.add(video)
        while self.prefix + 1 in self.uploaded:
            self.prefix += 1

    def longest(self):
        return self.prefix


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


if __name__ == "__main__":
    results = []
    results.append(check("211. Design Add and Search Words Data Structure", [('play(WordDictionary, ["WordDictionary", "addWord", "addWord", "addWord", "search", "search", "search", "search"], [[], ["bad"], ["dad"], ["mad"], ["pad"], ["bad"], [".ad"], ["b.."]])', [None, None, None, None, False, True, True, True])]))
    results.append(check("380. Insert Delete GetRandom O(1)", [('play(RandomizedSet, ["RandomizedSet", "insert", "remove", "insert", "insert", "remove", "insert"], [[], [1], [2], [2], [1], [1], [2]])', [None, True, False, True, False, True, False]), ('(lambda s: (s.insert(5), s.insert(7), s.remove(5), s.getRandom()))(RandomizedSet())[3]', 7)]))
    results.append(check("2502. Design Memory Allocator", [('play(Allocator, ["Allocator", "allocate", "allocate", "allocate", "freeMemory", "allocate", "allocate", "allocate", "freeMemory", "allocate", "freeMemory"], [[10], [1, 1], [1, 2], [1, 3], [2], [3, 4], [1, 1], [1, 1], [1], [10, 2], [7]])', [None, 0, 1, 2, 1, 3, 1, 6, 3, -1, 0])]))
    results.append(check("2353. Design a Food Rating System", [('play(FoodRatings, ["FoodRatings", "highestRated", "highestRated", "changeRating", "highestRated", "changeRating", "highestRated"], [[["kimchi", "miso", "sushi", "moussaka", "ramen", "bulgogi"], ["korean", "japanese", "japanese", "greek", "japanese", "korean"], [9, 12, 8, 15, 14, 7]], ["korean"], ["japanese"], ["sushi", 16], ["japanese"], ["ramen", 16], ["japanese"]])', [None, 'kimchi', 'ramen', None, 'sushi', None, 'ramen'])]))
    results.append(check("2671. Frequency Tracker", [('play(FrequencyTracker, ["FrequencyTracker", "add", "add", "hasFrequency"], [[], [3], [3], [2]])', [None, None, None, True]), ('play(FrequencyTracker, ["FrequencyTracker", "add", "deleteOne", "hasFrequency"], [[], [1], [1], [1]])', [None, None, None, False])]))
    results.append(check("1993. Operations on Tree", [('play(LockingTree, ["LockingTree", "lock", "unlock", "unlock", "lock", "upgrade", "lock"], [[[-1, 0, 0, 1, 1, 2, 2]], [2, 2], [2, 3], [2, 2], [4, 5], [0, 1], [0, 1]])', [None, True, False, True, True, True, False])]))
    results.append(check("1357. Apply Discount Every n Orders", [('play(Cashier, ["Cashier", "getBill", "getBill", "getBill"], [[3, 50, [1, 2, 3, 4, 5, 6, 7], [100, 200, 300, 400, 300, 200, 100]], [[1, 2], [1, 2]], [[3, 7], [10, 10]], [[1, 2, 3, 4, 5, 6, 7], [1, 1, 1, 1, 1, 1, 1]]])', [None, 500, 4000, 800.0])]))
    results.append(check("1476. Subrectangle Queries", [('play(SubrectangleQueries, ["SubrectangleQueries", "getValue", "updateSubrectangle", "getValue", "getValue", "updateSubrectangle", "getValue", "getValue"], [[[[1, 2, 1], [4, 3, 4], [3, 2, 1], [1, 1, 1]]], [0, 2], [0, 0, 3, 2, 5], [0, 2], [3, 1], [3, 0, 3, 2, 10], [3, 1], [0, 2]])', [None, 1, None, 5, 5, None, 10, 5])]))
    results.append(check("2166. Design Bitset", [('play(Bitset, ["Bitset", "fix", "fix", "flip", "all", "unfix", "flip", "one", "unfix", "count", "toString"], [[5], [3], [1], [], [], [0], [], [], [0], [], []])', [None, None, None, None, False, None, None, True, None, 2, '01010'])]))
    results.append(check("2424. Longest Uploaded Prefix", [('play(LUPrefix, ["LUPrefix", "upload", "longest", "upload", "longest", "upload", "longest"], [[4], [3], [], [1], [], [2], []])', [None, None, 0, None, 1, None, 3])]))
    if all(results):
        print("Every solution passes its tests.")
