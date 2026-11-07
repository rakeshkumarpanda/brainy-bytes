# 4.2 collections, heapq and bisect
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


# ================================================================== 1046. Last Stone Weight (Easy)
# https://leetcode.com/problems/last-stone-weight/
# Pattern: A max-heap with negative numbers
# Idea: Always smash the two heaviest stones. heapq is a min-heap, so store −weight. (Python 3.14
# also has heappop_max, but LeetCode may run an older Python.)

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


# ================================================================== 1351. Count Negative Numbers in a Sorted Matrix (Easy)
# https://leetcode.com/problems/count-negative-numbers-in-a-sorted-matrix/
# Pattern: bisect on each row
# Idea: Each row goes down from left to right. With key=lambda v: −v it goes up, so bisect finds
# where the negatives start in O(log n) per row.

import bisect


def count_negatives(grid):
    total = 0
    for row in grid:
        start = bisect.bisect_right(row, 0, key=lambda v: -v)
        total += len(row) - start
    return total


# ================================================================== 215. Kth Largest Element in an Array (Medium)
# https://leetcode.com/problems/kth-largest-element-in-an-array/
# Pattern: A min-heap of size k
# Idea: Keep the k largest numbers seen so far in a min-heap. Its top is the kth largest. O(n log k)
# time and O(k) memory.

import heapq


def find_kth_largest(nums, k):
    heap = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]


# ================================================================== 973. K Closest Points to Origin (Medium)
# https://leetcode.com/problems/k-closest-points-to-origin/
# Pattern: nsmallest with a key
# Idea: Compare squared distances x² + y² (no square root needed, the order is the same).
# heapq.nsmallest does it in O(n log k).

import heapq


def k_closest(points, k):
    return heapq.nsmallest(k, points, key=lambda p: p[0] * p[0] + p[1] * p[1])


# ================================================================== 692. Top K Frequent Words (Medium)
# https://leetcode.com/problems/top-k-frequent-words/
# Pattern: Counter, then sort by two keys
# Idea: Count with Counter. Sort by count going down, then by the word going up for ties:
# key=(-count, word).

from collections import Counter


def top_k_frequent_words(words, k):
    counts = Counter(words)
    ordered = sorted(counts, key=lambda word: (-counts[word], word))
    return ordered[:k]


# ================================================================== 2300. Successful Pairs of Spells and Potions (Medium)
# https://leetcode.com/problems/successful-pairs-of-spells-and-potions/
# Pattern: Sort once, then bisect for each spell
# Idea: A spell s needs a potion of at least ⌈success / s⌉. Sort the potions and bisect_left gives
# how many are too weak. O((n + m) log m).

import bisect


def successful_pairs(spells, potions, success):
    potions = sorted(potions)
    result = []
    for s in spells:
        need = (success + s - 1) // s
        result.append(len(potions) - bisect.bisect_left(potions, need))
    return result


# ================================================================== 300. Longest Increasing Subsequence (Medium)
# https://leetcode.com/problems/longest-increasing-subsequence/
# Pattern: Patience sorting with bisect
# Idea: tails[i] is the smallest last number of an increasing run of length i + 1. Each number
# replaces the first tail that is not smaller, found with bisect_left. O(n log n).

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


# ================================================================== 621. Task Scheduler (Medium)
# https://leetcode.com/problems/task-scheduler/
# Pattern: Count the most common task
# Idea: The most common task (count m) needs m − 1 gaps of n slots after it. Tasks that share that
# top count fill the last row. The answer is never less than the number of tasks.

from collections import Counter


def least_interval(tasks, n):
    counts = Counter(tasks)
    top = max(counts.values())
    with_top = sum(1 for c in counts.values() if c == top)
    return max(len(tasks), (top - 1) * (n + 1) + with_top)


# ================================================================== 239. Sliding Window Maximum (Hard)
# https://leetcode.com/problems/sliding-window-maximum/
# Pattern: A monotonic deque of indexes
# Idea: Keep indexes whose values go down from front to back. Drop smaller values from the back
# before adding, and the front once it leaves the window. Each index enters and leaves once: O(n).

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


# ================================================================== 295. Find Median from Data Stream (Hard)
# https://leetcode.com/problems/find-median-from-data-stream/
# Pattern: Two heaps
# Idea: A max-heap (negative numbers) holds the smaller half, a min-heap the bigger half. Keep their
# sizes equal or the low half one bigger. The median is at the tops.

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


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


if __name__ == "__main__":
    results = []
    results.append(check("1046. Last Stone Weight", [('last_stone_weight([2, 7, 4, 1, 8, 1])', 1), ('last_stone_weight([1])', 1), ('last_stone_weight([3, 3])', 0)]))
    results.append(check("1351. Count Negative Numbers in a Sorted Matrix", [('count_negatives([[4, 3, 2, -1], [3, 2, 1, -1], [1, 1, -1, -2], [-1, -1, -2, -3]])', 8), ('count_negatives([[3, 2], [1, 0]])', 0)]))
    results.append(check("215. Kth Largest Element in an Array", [('find_kth_largest([3, 2, 1, 5, 6, 4], 2)', 5), ('find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4)', 4)]))
    results.append(check("973. K Closest Points to Origin", [('k_closest([[1, 3], [-2, 2]], 1)', [[-2, 2]]), ('sorted(k_closest([[3, 3], [5, -1], [-2, 4]], 2))', [[-2, 4], [3, 3]])]))
    results.append(check("692. Top K Frequent Words", [('top_k_frequent_words(["i", "love", "leetcode", "i", "love", "coding"], 2)', ['i', 'love']), ('top_k_frequent_words(["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4)', ['the', 'is', 'sunny', 'day'])]))
    results.append(check("2300. Successful Pairs of Spells and Potions", [('successful_pairs([5, 1, 3], [1, 2, 3, 4, 5], 7)', [4, 0, 3]), ('successful_pairs([3, 1, 2], [8, 5, 8], 16)', [2, 0, 2])]))
    results.append(check("300. Longest Increasing Subsequence", [('length_of_lis([10, 9, 2, 5, 3, 7, 101, 18])', 4), ('length_of_lis([0, 1, 0, 3, 2, 3])', 4), ('length_of_lis([7, 7, 7, 7])', 1)]))
    results.append(check("621. Task Scheduler", [('least_interval(["A", "A", "A", "B", "B", "B"], 2)', 8), ('least_interval(["A", "C", "A", "B", "D", "B"], 1)', 6), ('least_interval(["A", "A", "A", "B", "B", "B"], 3)', 10)]))
    results.append(check("239. Sliding Window Maximum", [('max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)', [3, 3, 5, 5, 6, 7]), ('max_sliding_window([1], 1)', [1])]))
    results.append(check("295. Find Median from Data Stream", [('play(MedianFinder, ["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"], [[], [1], [2], [], [3], []])', [None, None, None, 1.5, None, 2.0])]))
    if all(results):
        print("Every solution passes its tests.")
