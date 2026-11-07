# 8.1 Exam practice: PCPP1 style papers
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


# ================================================================== 304. Range Sum Query 2D - Immutable (Medium)
# https://leetcode.com/problems/range-sum-query-2d-immutable/
# Pattern: A class with a table of prefix sums
# Idea: Build sums[r + 1][c + 1] = the total of the rectangle from (0, 0) to (r, c) once in
# __init__. Any rectangle is then four lookups.

class NumMatrix:
    def __init__(self, matrix):
        rows = len(matrix)
        cols = len(matrix[0])
        self.sums = [[0] * (cols + 1) for _ in range(rows + 1)]
        for r in range(rows):
            for c in range(cols):
                self.sums[r + 1][c + 1] = matrix[r][c] + self.sums[r][c + 1] + self.sums[r + 1][c] - self.sums[r][c]

    def sumRegion(self, row1, col1, row2, col2):
        s = self.sums
        return s[row2 + 1][col2 + 1] - s[row1][col2 + 1] - s[row2 + 1][col1] + s[row1][col1]


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 438. Find All Anagrams in a String (Medium)
# https://leetcode.com/problems/find-all-anagrams-in-a-string/
# Pattern: A sliding window of Counters
# Idea: Keep a Counter of the last len(p) letters. Add the new letter, remove the oldest, and
# compare with the Counter of p.

from collections import Counter


def find_anagrams(s, p):
    need = Counter(p)
    window = Counter()
    found = []
    for i, ch in enumerate(s):
        window[ch] += 1
        if i >= len(p):
            old = s[i - len(p)]
            window[old] -= 1
            if window[old] == 0:
                del window[old]
        if window == need:
            found.append(i - len(p) + 1)
    return found


# ================================================================== 39. Combination Sum (Medium)
# https://leetcode.com/problems/combination-sum/
# Pattern: A recursive generator
# Idea: A generator yields each combination as soon as it is found. Pass the start index so a number
# is never used before a smaller one, which avoids repeats.

def combination_sum(candidates, target):
    candidates = sorted(candidates)

    def search(start, left, chosen):
        if left == 0:
            yield list(chosen)
            return
        for i in range(start, len(candidates)):
            if candidates[i] > left:
                break
            chosen.append(candidates[i])
            yield from search(i, left - candidates[i], chosen)
            chosen.pop()

    return list(search(0, target, []))


# ================================================================== 131. Palindrome Partitioning (Medium)
# https://leetcode.com/problems/palindrome-partitioning/
# Pattern: yield from for every first piece
# Idea: Try every palindrome as the first piece, then partition the rest the same way. A generator
# with yield from keeps the code short.

def partition(s):
    def cuts(rest):
        if not rest:
            yield []
            return
        for end in range(1, len(rest) + 1):
            piece = rest[:end]
            if piece == piece[::-1]:
                for tail in cuts(rest[end:]):
                    yield [piece] + tail

    return list(cuts(s))


# ================================================================== 1143. Longest Common Subsequence (Medium)
# https://leetcode.com/problems/longest-common-subsequence/
# Pattern: Recursion with lru_cache
# Idea: best(i, j) compares text1[i:] and text2[j:]. Equal letters add 1, otherwise skip one letter
# on either side. functools.cache stores every answer.

from functools import cache


def longest_common_subsequence(text1, text2):
    @cache
    def best(i, j):
        if i == len(text1) or j == len(text2):
            return 0
        if text1[i] == text2[j]:
            return 1 + best(i + 1, j + 1)
        return max(best(i + 1, j), best(i, j + 1))

    return best(0, 0)


# ================================================================== 221. Maximal Square (Medium)
# https://leetcode.com/problems/maximal-square/
# Pattern: Grow squares from three neighbours
# Idea: size[r][c] is the side of the biggest all "1" square ending at (r, c): 1 + the smallest of
# the sizes above, to the left and diagonal.

def maximal_square(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    size = [[0] * (cols + 1) for _ in range(rows + 1)]
    best = 0
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == "1":
                size[r + 1][c + 1] = 1 + min(size[r][c + 1], size[r + 1][c], size[r][c])
                best = max(best, size[r + 1][c + 1])
    return best * best


# ================================================================== 72. Edit Distance (Medium)
# https://leetcode.com/problems/edit-distance/
# Pattern: A table of smaller answers
# Idea: dist[i][j] is the cost to turn the first i letters of word1 into the first j letters of
# word2. Equal letters cost nothing, otherwise 1 + the best of insert, delete or replace.

def min_distance(word1, word2):
    rows = len(word1) + 1
    cols = len(word2) + 1
    dist = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        dist[i][0] = i
    for j in range(cols):
        dist[0][j] = j
    for i in range(1, rows):
        for j in range(1, cols):
            if word1[i - 1] == word2[j - 1]:
                dist[i][j] = dist[i - 1][j - 1]
            else:
                dist[i][j] = 1 + min(dist[i - 1][j], dist[i][j - 1], dist[i - 1][j - 1])
    return dist[-1][-1]


# ================================================================== 42. Trapping Rain Water (Hard)
# https://leetcode.com/problems/trapping-rain-water/
# Pattern: Two pointers with the highest wall on each side
# Idea: Water above a bar is the lower of the highest walls on its left and right, minus the bar.
# Move the pointer on the lower side, because that side decides the water level.

def trap(height):
    left = 0
    right = len(height) - 1
    left_max = 0
    right_max = 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            left_max = max(left_max, height[left])
            water += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            water += right_max - height[right]
            right -= 1
    return water


# ================================================================== 76. Minimum Window Substring (Hard)
# https://leetcode.com/problems/minimum-window-substring/
# Pattern: Grow the window, then shrink it
# Idea: Move the right end until the window holds every letter of t (count with a Counter). Then
# move the left end while it still does, and remember the shortest window.

from collections import Counter


def min_window(s, t):
    need = Counter(t)
    missing = len(t)
    left = 0
    best = (0, 0)
    for right, ch in enumerate(s, 1):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        if missing == 0:
            while need[s[left]] < 0:
                need[s[left]] += 1
                left += 1
            if best == (0, 0) or right - left < best[1] - best[0]:
                best = (left, right)
            need[s[left]] += 1
            missing += 1
            left += 1
    return s[best[0]:best[1]]


# ================================================================== 460. LFU Cache (Hard)
# https://leetcode.com/problems/lfu-cache/
# Pattern: A dict of OrderedDicts, one per use count
# Idea: Keep the value and the use count of each key, and an OrderedDict of keys for every count.
# Evict the oldest key in the group with the smallest count.

from collections import OrderedDict, defaultdict


class LFUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.values = {}
        self.counts = {}
        self.groups = defaultdict(OrderedDict)
        self.min_count = 0

    def _touch(self, key):
        count = self.counts[key]
        del self.groups[count][key]
        if not self.groups[count]:
            del self.groups[count]
            if self.min_count == count:
                self.min_count += 1
        self.counts[key] = count + 1
        self.groups[count + 1][key] = None

    def get(self, key):
        if key not in self.values:
            return -1
        self._touch(key)
        return self.values[key]

    def put(self, key, value):
        if self.capacity == 0:
            return
        if key in self.values:
            self.values[key] = value
            self._touch(key)
            return
        if len(self.values) >= self.capacity:
            old, _ = self.groups[self.min_count].popitem(last=False)
            if not self.groups[self.min_count]:
                del self.groups[self.min_count]
            del self.values[old]
            del self.counts[old]
        self.values[key] = value
        self.counts[key] = 1
        self.groups[1][key] = None
        self.min_count = 1


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


if __name__ == "__main__":
    results = []
    results.append(check("304. Range Sum Query 2D - Immutable", [('play(NumMatrix, ["NumMatrix", "sumRegion", "sumRegion", "sumRegion"], [[[[3, 0, 1, 4, 2], [5, 6, 3, 2, 1], [1, 2, 0, 1, 5], [4, 1, 0, 1, 7], [1, 0, 3, 0, 5]]], [2, 1, 4, 3], [1, 1, 2, 2], [1, 2, 2, 4]])', [None, 8, 11, 12])]))
    results.append(check("438. Find All Anagrams in a String", [('find_anagrams("cbaebabacd", "abc")', [0, 6]), ('find_anagrams("abab", "ab")', [0, 1, 2])]))
    results.append(check("39. Combination Sum", [('combination_sum([2, 3, 6, 7], 7)', [[2, 2, 3], [7]]), ('combination_sum([2, 3, 5], 8)', [[2, 2, 2, 2], [2, 3, 3], [3, 5]]), ('combination_sum([2], 1)', [])]))
    results.append(check("131. Palindrome Partitioning", [('partition("aab")', [['a', 'a', 'b'], ['aa', 'b']]), ('partition("a")', [['a']])]))
    results.append(check("1143. Longest Common Subsequence", [('longest_common_subsequence("abcde", "ace")', 3), ('longest_common_subsequence("abc", "abc")', 3), ('longest_common_subsequence("abc", "def")', 0)]))
    results.append(check("221. Maximal Square", [('maximal_square([["1", "0", "1", "0", "0"], ["1", "0", "1", "1", "1"], ["1", "1", "1", "1", "1"], ["1", "0", "0", "1", "0"]])', 4), ('maximal_square([["0", "1"], ["1", "0"]])', 1), ('maximal_square([["0"]])', 0)]))
    results.append(check("72. Edit Distance", [('min_distance("horse", "ros")', 3), ('min_distance("intention", "execution")', 5), ('min_distance("", "abc")', 3)]))
    results.append(check("42. Trapping Rain Water", [('trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])', 6), ('trap([4, 2, 0, 3, 2, 5])', 9)]))
    results.append(check("76. Minimum Window Substring", [('min_window("ADOBECODEBANC", "ABC")', 'BANC'), ('min_window("a", "a")', 'a'), ('min_window("a", "aa")', '')]))
    results.append(check("460. LFU Cache", [('play(LFUCache, ["LFUCache", "put", "put", "get", "put", "get", "get", "put", "get", "get", "get"], [[2], [1, 1], [2, 2], [1], [3, 3], [2], [3], [4, 4], [1], [3], [4]])', [None, None, None, 1, None, -1, 3, None, -1, 3, 4])]))
    if all(results):
        print("Every solution passes its tests.")
