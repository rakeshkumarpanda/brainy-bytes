# 1.2 Polynomial regression and regularisation: ridge, lasso, elastic net
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


# ================================================================== 2333. Minimum Sum of Squared Difference (Medium)
# https://leetcode.com/problems/minimum-sum-of-squared-difference/
# Pattern: Shrink the largest values first (like an L2 penalty)
# Idea: Only the gaps |a − b| matter, and you have k1 + k2 unit decreases. A squared sum falls
# fastest when you cut the biggest gaps, so bring every gap above some level down to that level
# (binary search the level), then spend what is left one by one.

def min_sum_square_diff(nums1, nums2, k1, k2):
    diffs = [abs(a - b) for a, b in zip(nums1, nums2)]
    k = k1 + k2
    if sum(diffs) <= k:
        return 0
    low = 0
    high = max(diffs)
    while low < high:
        mid = (low + high) // 2
        need = sum(d - mid for d in diffs if d > mid)
        if need <= k:
            high = mid
        else:
            low = mid + 1
    level = low
    left = k - sum(d - level for d in diffs if d > level)
    total = 0
    for d in diffs:
        v = min(d, level)
        if v == level and left > 0 and level > 0:
            v = v - 1
            left = left - 1
        total = total + v * v
    return total


# ================================================================== 1685. Sum of Absolute Differences in a Sorted Array (Medium)
# https://leetcode.com/problems/sum-of-absolute-differences-in-a-sorted-array/
# Pattern: L1 distances with prefix sums
# Idea: For position i, numbers on the left are smaller and numbers on the right are larger. With
# prefix sums, the left part is i × x minus their sum and the right part is their sum minus count ×
# x.

def get_sum_absolute_differences(nums):
    n = len(nums)
    total = sum(nums)
    left_sum = 0
    result = []
    for i in range(n):
        x = nums[i]
        right_sum = total - left_sum - x
        result.append(i * x - left_sum + right_sum - (n - 1 - i) * x)
        left_sum = left_sum + x
    return result


# ================================================================== 2602. Minimum Operations to Make All Array Elements Equal (Medium)
# https://leetcode.com/problems/minimum-operations-to-make-all-array-elements-equal/
# Pattern: L1 cost per query with prefix sums and binary search
# Idea: Sort once and build prefix sums. For a query q, binary search how many numbers are below q.
# The cost is (count below × q − their sum) plus (sum above − count above × q).

from bisect import bisect_left


def min_operations(nums, queries):
    s = sorted(nums)
    prefix = [0]
    for x in s:
        prefix.append(prefix[-1] + x)
    n = len(s)
    answer = []
    for q in queries:
        i = bisect_left(s, q)
        below = q * i - prefix[i]
        above = (prefix[n] - prefix[i]) - q * (n - i)
        answer.append(below + above)
    return answer


# ================================================================== 1838. Frequency of the Most Frequent Element (Medium)
# https://leetcode.com/problems/frequency-of-the-most-frequent-element/
# Pattern: A budget constraint with a sliding window
# Idea: Sort. For a window ending at nums[r], raising every number to nums[r] costs nums[r] × size −
# window sum. Shrink the window from the left while the cost is over the budget k. Like a penalty
# budget, k limits how far the values may move.

def max_frequency(nums, k):
    s = sorted(nums)
    left = 0
    window = 0
    best = 0
    for right in range(len(s)):
        window = window + s[right]
        while s[right] * (right - left + 1) - window > k:
            window = window - s[left]
            left = left + 1
        best = max(best, right - left + 1)
    return best


# ================================================================== 1802. Maximum Value at a Given Index in a Bounded Array (Medium)
# https://leetcode.com/problems/maximum-value-at-a-given-index-in-a-bounded-array/
# Pattern: Binary search under a sum budget
# Idea: The cheapest array with value v at index falls by 1 per step on both sides and never goes
# below 1. Its sum grows with v, so binary search the largest v whose minimum sum fits in maxSum.

def side_sum(peak, length):
    # sum of peak - 1, peak - 2, ... over length cells, never below 1
    if peak - 1 >= length:
        top = peak - 1
        bottom = peak - length
        return (top + bottom) * length // 2
    ones = length - (peak - 1)
    return (peak - 1) * peak // 2 + ones


def max_value(n, index, max_sum):
    low = 1
    high = max_sum
    while low < high:
        mid = (low + high + 1) // 2
        total = mid + side_sum(mid, index) + side_sum(mid, n - index - 1)
        if total <= max_sum:
            low = mid
        else:
            high = mid - 1
    return low


# ================================================================== 1049. Last Stone Weight II (Medium)
# https://leetcode.com/problems/last-stone-weight-ii/
# Pattern: Pick signs to make a sum as close to 0 as possible
# Idea: Smashing stones is the same as giving each stone a + or − sign. Split them into two groups
# with sums as equal as possible: find all reachable subset sums up to half the total.

def last_stone_weight_ii(stones):
    total = sum(stones)
    reachable = {0}
    for s in stones:
        reachable = reachable | {r + s for r in reachable if r + s <= total // 2}
    return total - 2 * max(reachable)


if __name__ == "__main__":
    results = []
    results.append(check("2333. Minimum Sum of Squared Difference", [('min_sum_square_diff([1, 2, 3, 4], [2, 10, 20, 19], 0, 0)', 579), ('min_sum_square_diff([1, 4, 10, 12], [5, 8, 6, 9], 1, 1)', 43)]))
    results.append(check("1685. Sum of Absolute Differences in a Sorted Array", [('get_sum_absolute_differences([2, 3, 5])', [4, 3, 5]), ('get_sum_absolute_differences([1, 4, 6, 8, 10])', [24, 15, 13, 15, 21])]))
    results.append(check("2602. Minimum Operations to Make All Array Elements Equal", [('min_operations([3, 1, 6, 8], [1, 5])', [14, 10]), ('min_operations([2, 9, 6, 3], [10])', [20])]))
    results.append(check("1838. Frequency of the Most Frequent Element", [('max_frequency([1, 2, 4], 5)', 3), ('max_frequency([1, 4, 8, 13], 5)', 2), ('max_frequency([3, 9, 6], 2)', 1)]))
    results.append(check("1802. Maximum Value at a Given Index in a Bounded Array", [('max_value(4, 2, 6)', 2), ('max_value(6, 1, 10)', 3)]))
    results.append(check("1049. Last Stone Weight II", [('last_stone_weight_ii([2, 7, 4, 1, 8, 1])', 1), ('last_stone_weight_ii([31, 26, 33, 21, 40])', 5)]))
    if all(results):
        print("Every solution passes its tests.")
