# 4.1 Metrics: measuring a model properly
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


# ================================================================== 1512. Number of Good Pairs (Easy)
# https://leetcode.com/problems/number-of-good-pairs/
# Pattern: Count pairs with a running tally
# Idea: Each new value forms a good pair with every earlier equal value. Keep a count per value and
# add it before increasing it. AUC is also a count of pairs.

def num_identical_pairs(nums):
    seen = {}
    pairs = 0
    for x in nums:
        pairs = pairs + seen.get(x, 0)
        seen[x] = seen.get(x, 0) + 1
    return pairs


# ================================================================== 1365. How Many Numbers Are Smaller Than the Current Number (Easy)
# https://leetcode.com/problems/how-many-numbers-are-smaller-than-the-current-number/
# Pattern: Sort once, read the first position
# Idea: After sorting, the first position of a value equals how many values are smaller. That rank
# is exactly what AUC compares between positives and negatives.

def smaller_numbers_than_current(nums):
    order = sorted(nums)
    first = {}
    for i, v in enumerate(order):
        if v not in first:
            first[v] = i
    return [first[v] for v in nums]


# ================================================================== 1051. Height Checker (Easy)
# https://leetcode.com/problems/height-checker/
# Pattern: Compare with the sorted order
# Idea: Sort a copy and count the positions where the original differs. It is an error count between
# what is and what should be, like comparing predictions with labels.

def height_checker(heights):
    expected = sorted(heights)
    wrong = 0
    for a, b in zip(heights, expected):
        if a != b:
            wrong = wrong + 1
    return wrong


# ================================================================== 2006. Count Number of Pairs With Absolute Difference K (Easy)
# https://leetcode.com/problems/count-number-of-pairs-with-absolute-difference-k/
# Pattern: Look back for x minus k and x plus k
# Idea: Keep counts of values seen so far. Each new value pairs with every earlier value equal to x
# − k or x + k.

def count_k_difference(nums, k):
    seen = {}
    pairs = 0
    for x in nums:
        pairs = pairs + seen.get(x - k, 0) + seen.get(x + k, 0)
        seen[x] = seen.get(x, 0) + 1
    return pairs


# ================================================================== 977. Squares of a Sorted Array (Easy)
# https://leetcode.com/problems/squares-of-a-sorted-array/
# Pattern: Two pointers from both ends
# Idea: The largest square is at one of the two ends. Compare the ends, place the bigger square at
# the back of the answer, and move that pointer inward. Squared errors are why RMSE punishes large
# misses.

def sorted_squares(nums):
    out = [0] * len(nums)
    left = 0
    right = len(nums) - 1
    for pos in range(len(nums) - 1, -1, -1):
        if abs(nums[left]) > abs(nums[right]):
            out[pos] = nums[left] ** 2
            left = left + 1
        else:
            out[pos] = nums[right] ** 2
            right = right - 1
    return out


# ================================================================== 1200. Minimum Absolute Difference (Easy)
# https://leetcode.com/problems/minimum-absolute-difference/
# Pattern: Sort, then look at neighbours
# Idea: After sorting, the smallest absolute difference is between neighbours. Find it, then collect
# every neighbouring pair with that difference.

def minimum_abs_difference(arr):
    s = sorted(arr)
    best = min(s[i] - s[i - 1] for i in range(1, len(s)))
    return [[s[i - 1], s[i]] for i in range(1, len(s)) if s[i] - s[i - 1] == best]


if __name__ == "__main__":
    results = []
    results.append(check("1512. Number of Good Pairs", [('num_identical_pairs([1, 2, 3, 1, 1, 3])', 4), ('num_identical_pairs([1, 2, 3])', 0)]))
    results.append(check("1365. How Many Numbers Are Smaller Than the Current Number", [('smaller_numbers_than_current([8, 1, 2, 2, 3])', [4, 0, 1, 1, 3]), ('smaller_numbers_than_current([7, 7, 7, 7])', [0, 0, 0, 0])]))
    results.append(check("1051. Height Checker", [('height_checker([1, 1, 4, 2, 1, 3])', 3), ('height_checker([5, 1, 2, 3, 4])', 5)]))
    results.append(check("2006. Count Number of Pairs With Absolute Difference K", [('count_k_difference([1, 2, 2, 1], 1)', 4), ('count_k_difference([3, 2, 1, 5, 4], 2)', 3)]))
    results.append(check("977. Squares of a Sorted Array", [('sorted_squares([-4, -1, 0, 3, 10])', [0, 1, 9, 16, 100]), ('sorted_squares([-7, -3, 2, 3, 11])', [4, 9, 9, 49, 121])]))
    results.append(check("1200. Minimum Absolute Difference", [('minimum_abs_difference([4, 2, 1, 3])', [[1, 2], [2, 3], [3, 4]]), ('minimum_abs_difference([1, 3, 6, 10, 15])', [[1, 3]])]))
    if all(results):
        print("Every solution passes its tests.")
