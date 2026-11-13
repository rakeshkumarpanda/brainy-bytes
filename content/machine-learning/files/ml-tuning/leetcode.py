# 4.3 Tuning and calibration
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


# ================================================================== 875. Koko Eating Bananas (Medium)
# https://leetcode.com/problems/koko-eating-bananas/
# Pattern: Binary search on the setting
# Idea: The eating speed is a setting you tune. Faster always works if slower works, so binary
# search the smallest speed that finishes within h hours. Hours at speed k is the sum of the
# ceilings of pile / k.

def min_eating_speed(piles, h):
    lo, hi = 1, max(piles)
    while lo < hi:
        k = (lo + hi) // 2
        hours = sum((p + k - 1) // k for p in piles)
        if hours <= h:
            hi = k
        else:
            lo = k + 1
    return lo


# ================================================================== 69. Sqrt(x) (Easy)
# https://leetcode.com/problems/sqrtx/
# Pattern: Binary search for the largest square below x
# Idea: Search the largest whole number whose square is at most x. Each guess halves the range, like
# halving the candidates in successive halving.

def my_sqrt(x):
    lo, hi = 0, x
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * mid <= x:
            lo = mid
        else:
            hi = mid - 1
    return lo


# ================================================================== 35. Search Insert Position (Easy)
# https://leetcode.com/problems/search-insert-position/
# Pattern: First position not smaller than the target
# Idea: Binary search for the first index whose value is at least the target. That is where it is or
# where it would go.

def search_insert(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


# ================================================================== 162. Find Peak Element (Medium)
# https://leetcode.com/problems/find-peak-element/
# Pattern: Walk uphill with binary search
# Idea: Compare the middle with its right neighbour. If the right is higher, a peak lies to the
# right, otherwise at or to the left. Finding the top of a validation curve is the same search.

def find_peak_element(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo


# ================================================================== 1482. Minimum Number of Days to Make m Bouquets (Medium)
# https://leetcode.com/problems/minimum-number-of-days-to-make-m-bouquets/
# Pattern: Binary search the day, check greedily
# Idea: If m bouquets are possible by day d, they are possible on any later day. Binary search the
# first such day. To check a day, count runs of k adjacent bloomed flowers.

def min_days(bloom_day, m, k):
    if m * k > len(bloom_day):
        return -1

    def bouquets(day):
        made = run = 0
        for b in bloom_day:
            run = run + 1 if b <= day else 0
            if run == k:
                made = made + 1
                run = 0
        return made

    lo, hi = min(bloom_day), max(bloom_day)
    while lo < hi:
        mid = (lo + hi) // 2
        if bouquets(mid) >= m:
            hi = mid
        else:
            lo = mid + 1
    return lo


# ================================================================== 2187. Minimum Time to Complete Trips (Medium)
# https://leetcode.com/problems/minimum-time-to-complete-trips/
# Pattern: Binary search the time
# Idea: In time t, a bus with trip time b makes t // b trips. More time never means fewer trips, so
# binary search the least t that reaches the total.

def minimum_time(time, total_trips):
    lo, hi = 1, min(time) * total_trips
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(mid // t for t in time) >= total_trips:
            hi = mid
        else:
            lo = mid + 1
    return lo


if __name__ == "__main__":
    results = []
    results.append(check("875. Koko Eating Bananas", [('min_eating_speed([3, 6, 7, 11], 8)', 4), ('min_eating_speed([30, 11, 23, 4, 20], 5)', 30)]))
    results.append(check("69. Sqrt(x)", [('my_sqrt(4)', 2), ('my_sqrt(8)', 2)]))
    results.append(check("35. Search Insert Position", [('search_insert([1, 3, 5, 6], 5)', 2), ('search_insert([1, 3, 5, 6], 2)', 1)]))
    results.append(check("162. Find Peak Element", [('find_peak_element([1, 2, 3, 1])', 2), ('find_peak_element([1, 2, 1, 3, 5, 6, 4])', 5)]))
    results.append(check("1482. Minimum Number of Days to Make m Bouquets", [('min_days([1, 10, 3, 10, 2], 3, 1)', 3), ('min_days([1, 10, 3, 10, 2], 3, 2)', -1)]))
    results.append(check("2187. Minimum Time to Complete Trips", [('minimum_time([1, 2, 3], 5)', 3), ('minimum_time([2], 1)', 2)]))
    if all(results):
        print("Every solution passes its tests.")
