# 1.2 The machine learning project: from a question to a working model
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn


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


# ================================================================== 905. Sort Array By Parity (Easy)
# https://leetcode.com/problems/sort-array-by-parity/
# Pattern: Partition into two groups
# Idea: Walk once and put even numbers in one list and odd numbers in another, then join them.
# Splitting rows into groups by a rule is what a data split does.

def sort_array_by_parity(nums):
    evens = []
    odds = []
    for x in nums:
        if x % 2 == 0:
            evens.append(x)
        else:
            odds.append(x)
    return evens + odds


# ================================================================== 2161. Partition Array According to Given Pivot (Medium)
# https://leetcode.com/problems/partition-array-according-to-given-pivot/
# Pattern: Stable three way partition
# Idea: Make three lists: smaller than the pivot, equal, and larger, keeping the original order
# inside each. Then join them.

def pivot_array(nums, pivot):
    smaller = []
    equal = []
    larger = []
    for x in nums:
        if x < pivot:
            smaller.append(x)
        elif x == pivot:
            equal.append(x)
        else:
            larger.append(x)
    return smaller + equal + larger


# ================================================================== 2270. Number of Ways to Split Array (Medium)
# https://leetcode.com/problems/number-of-ways-to-split-array/
# Pattern: Prefix sums
# Idea: Keep the sum of the left part as you move the cut. The right sum is the total minus the left
# sum. Count cuts where left is at least right.

def ways_to_split_array(nums):
    total = sum(nums)
    left = 0
    count = 0
    for i in range(len(nums) - 1):
        left = left + nums[i]
        if left >= total - left:
            count = count + 1
    return count


# ================================================================== 2780. Minimum Index of a Valid Split (Medium)
# https://leetcode.com/problems/minimum-index-of-a-valid-split/
# Pattern: Count the dominant value on both sides
# Idea: Find the value that is more than half of the list. Move the cut from left to right and check
# that it is more than half on both sides. This is the idea behind a stratified split: both parts
# keep the same majority.

def minimum_index(nums):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    dominant = nums[0]
    for x in counts:
        if counts[x] > counts[dominant]:
            dominant = x
    total = counts[dominant]
    left = 0
    n = len(nums)
    for i in range(n - 1):
        if nums[i] == dominant:
            left = left + 1
        right = total - left
        if left * 2 > i + 1 and right * 2 > n - i - 1:
            return i
    return -1


# ================================================================== 915. Partition Array into Disjoint Intervals (Medium)
# https://leetcode.com/problems/partition-array-into-disjoint-intervals/
# Pattern: Running max on the left, running min on the right
# Idea: Build the smallest value of every suffix first. Then walk from the left keeping the largest
# value so far. The first cut where left max is at most right min is the answer.

def partition_disjoint(nums):
    n = len(nums)
    right_min = [0] * n
    right_min[n - 1] = nums[n - 1]
    for i in range(n - 2, -1, -1):
        right_min[i] = min(nums[i], right_min[i + 1])
    left_max = nums[0]
    for i in range(n - 1):
        left_max = max(left_max, nums[i])
        if left_max <= right_min[i + 1]:
            return i + 1
    return n


# ================================================================== 384. Shuffle an Array (Medium)
# https://leetcode.com/problems/shuffle-an-array/
# Pattern: Fisher Yates shuffle
# Idea: Go from the last position down. Swap each position with a random position at or before it.
# Every order is equally likely, which is what a fair train and test split needs.

import random


class Solution:
    def __init__(self, nums):
        self.original = nums[:]
        self.nums = nums[:]

    def reset(self):
        self.nums = self.original[:]
        return self.nums

    def shuffle(self):
        items = self.nums[:]
        for i in range(len(items) - 1, 0, -1):
            j = random.randint(0, i)
            items[i], items[j] = items[j], items[i]
        self.nums = items
        return items


def shuffle_check(nums):
    random.seed(1)
    s = Solution(nums)
    mixed = s.shuffle()
    return sorted(mixed) == sorted(nums) and s.reset() == nums


if __name__ == "__main__":
    results = []
    results.append(check("905. Sort Array By Parity", [('sort_array_by_parity([3, 1, 2, 4])', [2, 4, 3, 1]), ('sort_array_by_parity([0])', [0])]))
    results.append(check("2161. Partition Array According to Given Pivot", [('pivot_array([9, 12, 5, 10, 14, 3, 10], 10)', [9, 5, 3, 10, 10, 12, 14]), ('pivot_array([-3, 4, 3, 2], 2)', [-3, 2, 4, 3])]))
    results.append(check("2270. Number of Ways to Split Array", [('ways_to_split_array([10, 4, -8, 7])', 2), ('ways_to_split_array([2, 3, 1, 0])', 2)]))
    results.append(check("2780. Minimum Index of a Valid Split", [('minimum_index([1, 2, 2, 2])', 2), ('minimum_index([2, 1, 3, 1, 1, 1, 7, 1, 2, 1])', 4), ('minimum_index([3, 3, 3, 3, 7, 2, 2])', -1)]))
    results.append(check("915. Partition Array into Disjoint Intervals", [('partition_disjoint([5, 0, 3, 8, 6])', 3), ('partition_disjoint([1, 1, 1, 0, 6, 12])', 4)]))
    results.append(check("384. Shuffle an Array", [('shuffle_check([1, 2, 3])', True), ('shuffle_check([5, 5, 9, 1])', True)]))
    if all(results):
        print("Every solution passes its tests.")
