# 3.2 Testing: unittest, pytest and mocks
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


# ================================================================== 704. Binary Search (Easy)
# https://leetcode.com/problems/binary-search/
# Pattern: Halve the range each step
# Idea: Keep low and high. Look at the middle. The famous bug is an off by one in the loop
# condition, so test arrays of length 0, 1 and 2.

def search(nums, target):
    low, high = 0, len(nums) - 1
    while low <= high:
        middle = (low + high) // 2
        if nums[middle] == target:
            return middle
        if nums[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1


# ================================================================== 35. Search Insert Position (Easy)
# https://leetcode.com/problems/search-insert-position/
# Pattern: Binary search for the first place not smaller
# Idea: When the loop ends, low is where target belongs. Test before the first item and after the
# last.

def search_insert(nums, target):
    low, high = 0, len(nums)
    while low < high:
        middle = (low + high) // 2
        if nums[middle] < target:
            low = middle + 1
        else:
            high = middle
    return low


# ================================================================== 278. First Bad Version (Easy)
# https://leetcode.com/problems/first-bad-version/
# Pattern: Binary search on a yes or no question
# Idea: Exactly what git bisect does with a failing test. The is_bad check is passed in, so a test
# can give a fake one.

def first_bad_version(n, is_bad):
    low, high = 1, n
    while low < high:
        middle = (low + high) // 2
        if is_bad(middle):
            high = middle
        else:
            low = middle + 1
    return low


def make_is_bad(first_bad):
    """A fake version checker for the tests (LeetCode gives you isBadVersion)."""
    return lambda version: version >= first_bad


# ================================================================== 374. Guess Number Higher or Lower (Easy)
# https://leetcode.com/problems/guess-number-higher-or-lower/
# Pattern: Binary search against an API
# Idea: The guess API answers -1, 1 or 0. In tests we inject a fake API, like a Mock with a side
# effect.

def guess_number(n, guess):
    low, high = 1, n
    while True:
        middle = (low + high) // 2
        answer = guess(middle)
        if answer == 0:
            return middle
        if answer == -1:
            high = middle - 1
        else:
            low = middle + 1


def make_guess(pick):
    """A fake guess API for the tests: -1 means too high, 1 means too low."""
    def guess(number):
        if number > pick:
            return -1
        if number < pick:
            return 1
        return 0
    return guess


# ================================================================== 34. Find First and Last Position of Element in Sorted Array (Medium)
# https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/
# Pattern: Two binary searches
# Idea: Find the first index not smaller than target and the first index bigger than target.
# bisect_left and bisect_right do exactly this.

import bisect


def search_range(nums, target):
    left = bisect.bisect_left(nums, target)
    if left == len(nums) or nums[left] != target:
        return [-1, -1]
    return [left, bisect.bisect_right(nums, target) - 1]


# ================================================================== 162. Find Peak Element (Medium)
# https://leetcode.com/problems/find-peak-element/
# Pattern: Walk uphill with binary search
# Idea: If the middle is lower than its right neighbour, a peak lies to the right. Otherwise it lies
# at the middle or to the left.

def find_peak_element(nums):
    low, high = 0, len(nums) - 1
    while low < high:
        middle = (low + high) // 2
        if nums[middle] < nums[middle + 1]:
            low = middle + 1
        else:
            high = middle
    return low


# ================================================================== 153. Find Minimum in Rotated Sorted Array (Medium)
# https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/
# Pattern: Compare the middle with the right end
# Idea: If the middle is bigger than the last item, the drop (and the minimum) is to the right.

def find_min(nums):
    low, high = 0, len(nums) - 1
    while low < high:
        middle = (low + high) // 2
        if nums[middle] > nums[high]:
            low = middle + 1
        else:
            high = middle
    return nums[low]


# ================================================================== 33. Search in Rotated Sorted Array (Medium)
# https://leetcode.com/problems/search-in-rotated-sorted-array/
# Pattern: One half is always sorted
# Idea: Check which half is in order, then whether target lies inside it. Many edge cases: test a
# rotation at every position.

def search_rotated(nums, target):
    low, high = 0, len(nums) - 1
    while low <= high:
        middle = (low + high) // 2
        if nums[middle] == target:
            return middle
        if nums[low] <= nums[middle]:
            if nums[low] <= target < nums[middle]:
                high = middle - 1
            else:
                low = middle + 1
        else:
            if nums[middle] < target <= nums[high]:
                low = middle + 1
            else:
                high = middle - 1
    return -1


# ================================================================== 875. Koko Eating Bananas (Medium)
# https://leetcode.com/problems/koko-eating-bananas/
# Pattern: Binary search on the answer
# Idea: Try a speed in the middle and count the hours needed. Too slow: go faster. Fast enough: try
# slower.

def min_eating_speed(piles, h):
    low, high = 1, max(piles)
    while low < high:
        speed = (low + high) // 2
        hours = sum((pile + speed - 1) // speed for pile in piles)
        if hours <= h:
            high = speed
        else:
            low = speed + 1
    return low


# ================================================================== 4. Median of Two Sorted Arrays (Hard)
# https://leetcode.com/problems/median-of-two-sorted-arrays/
# Pattern: Binary search the cut in the shorter array
# Idea: Cut both arrays so the left parts hold half of all items and every left item is at most
# every right item. Then the median comes from the four items around the cuts.

def find_median_sorted_arrays(nums1, nums2):
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    m, n = len(nums1), len(nums2)
    half = (m + n + 1) // 2
    low, high = 0, m
    while True:
        i = (low + high) // 2
        j = half - i
        left1 = nums1[i - 1] if i > 0 else float("-inf")
        right1 = nums1[i] if i < m else float("inf")
        left2 = nums2[j - 1] if j > 0 else float("-inf")
        right2 = nums2[j] if j < n else float("inf")
        if left1 <= right2 and left2 <= right1:
            if (m + n) % 2:
                return float(max(left1, left2))
            return (max(left1, left2) + min(right1, right2)) / 2
        if left1 > right2:
            high = i - 1
        else:
            low = i + 1


if __name__ == "__main__":
    results = []
    results.append(check("704. Binary Search", [('search([-1, 0, 3, 5, 9, 12], 9)', 4), ('search([-1, 0, 3, 5, 9, 12], 2)', -1), ('search([], 1)', -1), ('[search([7], 7), search([7], 1)]', [0, -1])]))
    results.append(check("35. Search Insert Position", [('[search_insert([1, 3, 5, 6], t) for t in [5, 2, 7, 0]]', [2, 1, 4, 0])]))
    results.append(check("278. First Bad Version", [('first_bad_version(5, make_is_bad(4))', 4), ('first_bad_version(1, make_is_bad(1))', 1), ('first_bad_version(2126753390, make_is_bad(1702766719))', 1702766719)]))
    results.append(check("374. Guess Number Higher or Lower", [('guess_number(10, make_guess(6))', 6), ('guess_number(1, make_guess(1))', 1), ('guess_number(2, make_guess(2))', 2)]))
    results.append(check("34. Find First and Last Position of Element in Sorted Array", [('search_range([5, 7, 7, 8, 8, 10], 8)', [3, 4]), ('search_range([5, 7, 7, 8, 8, 10], 6)', [-1, -1]), ('search_range([], 0)', [-1, -1])]))
    results.append(check("162. Find Peak Element", [('find_peak_element([1, 2, 3, 1])', 2), ('find_peak_element([1, 2, 1, 3, 5, 6, 4]) in (1, 5)', True)]))
    results.append(check("153. Find Minimum in Rotated Sorted Array", [('find_min([3, 4, 5, 1, 2])', 1), ('find_min([4, 5, 6, 7, 0, 1, 2])', 0), ('find_min([11, 13, 15, 17])', 11)]))
    results.append(check("33. Search in Rotated Sorted Array", [('search_rotated([4, 5, 6, 7, 0, 1, 2], 0)', 4), ('search_rotated([4, 5, 6, 7, 0, 1, 2], 3)', -1), ('search_rotated([1], 0)', -1)]))
    results.append(check("875. Koko Eating Bananas", [('min_eating_speed([3, 6, 7, 11], 8)', 4), ('min_eating_speed([30, 11, 23, 4, 20], 5)', 30), ('min_eating_speed([30, 11, 23, 4, 20], 6)', 23)]))
    results.append(check("4. Median of Two Sorted Arrays", [('find_median_sorted_arrays([1, 3], [2])', 2.0), ('find_median_sorted_arrays([1, 2], [3, 4])', 2.5), ('find_median_sorted_arrays([], [1])', 1.0)]))
    if all(results):
        print("Every solution passes its tests.")
