# 2.1 Logistic regression: probabilities for classification
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


# ================================================================== 1822. Sign of the Product of an Array (Easy)
# https://leetcode.com/problems/sign-of-the-product-of-an-array/
# Pattern: Decide the sign without the big number
# Idea: A 0 makes the product 0. Otherwise only the count of negative numbers matters: odd gives −1,
# even gives 1. A classifier also only needs the sign of its score.

def array_sign(nums):
    negatives = 0
    for x in nums:
        if x == 0:
            return 0
        if x < 0:
            negatives = negatives + 1
    if negatives % 2 == 1:
        return -1
    return 1


# ================================================================== 1608. Special Array With X Elements Greater Than or Equal X (Easy)
# https://leetcode.com/problems/special-array-with-x-elements-greater-than-or-equal-x/
# Pattern: Search for a threshold
# Idea: Try every threshold x from 0 to n and count how many numbers are at least x. Exactly x of
# them means x is the answer.

def special_array(nums):
    for x in range(len(nums) + 1):
        count = 0
        for v in nums:
            if v >= x:
                count = count + 1
        if count == x:
            return x
    return -1


# ================================================================== 2389. Longest Subsequence With Limited Sum (Easy)
# https://leetcode.com/problems/longest-subsequence-with-limited-sum/
# Pattern: Prefix sums and a threshold per query
# Idea: Take the smallest numbers first. Sort, build prefix sums, and for each query binary search
# how many prefix sums stay at or under it.

from bisect import bisect_right


def answer_queries(nums, queries):
    s = sorted(nums)
    prefix = []
    total = 0
    for x in s:
        total = total + x
        prefix.append(total)
    return [bisect_right(prefix, q) for q in queries]


# ================================================================== 1385. Find the Distance Value Between Two Arrays (Easy)
# https://leetcode.com/problems/find-the-distance-value-between-two-arrays/
# Pattern: Nearest neighbour check with a threshold
# Idea: Sort arr2. For each x in arr1, binary search the closest values in arr2. Count x when even
# the closest one is more than d away.

from bisect import bisect_left


def find_the_distance_value(arr1, arr2, d):
    s = sorted(arr2)
    count = 0
    for x in arr1:
        i = bisect_left(s, x)
        ok = True
        if i < len(s) and s[i] - x <= d:
            ok = False
        if i > 0 and x - s[i - 1] <= d:
            ok = False
        if ok:
            count = count + 1
    return count


# ================================================================== 2300. Successful Pairs of Spells and Potions (Medium)
# https://leetcode.com/problems/successful-pairs-of-spells-and-potions/
# Pattern: Binary search for the decision boundary
# Idea: Sort the potions. For a spell s, a potion works when s × potion ≥ success, so find the first
# potion at least ceil(success / s). Everything to its right succeeds, like points past a decision
# boundary.

from bisect import bisect_left


def successful_pairs(spells, potions, success):
    s = sorted(potions)
    result = []
    for spell in spells:
        need = (success + spell - 1) // spell
        i = bisect_left(s, need)
        result.append(len(s) - i)
    return result


# ================================================================== 1300. Sum of Mutated Array Closest to Target (Medium)
# https://leetcode.com/problems/sum-of-mutated-array-closest-to-target/
# Pattern: Choose a threshold that minimises an error
# Idea: Capping every number at v gives a sum that grows with v. Binary search the largest v whose
# capped sum is at most the target, then compare v and v + 1 and keep the one with the smaller error
# (smaller v on a tie).

def capped_sum(arr, v):
    total = 0
    for x in arr:
        total = total + min(x, v)
    return total


def find_best_value(arr, target):
    low = 0
    high = max(arr)
    while low < high:
        mid = (low + high + 1) // 2
        if capped_sum(arr, mid) <= target:
            low = mid
        else:
            high = mid - 1
    if abs(capped_sum(arr, low + 1) - target) < abs(capped_sum(arr, low) - target):
        return low + 1
    return low


if __name__ == "__main__":
    results = []
    results.append(check("1822. Sign of the Product of an Array", [('array_sign([-1, -2, -3, -4, 3, 2, 1])', 1), ('array_sign([1, 5, 0, 2, -3])', 0), ('array_sign([-1, 1, -1, 1, -1])', -1)]))
    results.append(check("1608. Special Array With X Elements Greater Than or Equal X", [('special_array([3, 5])', 2), ('special_array([0, 0])', -1), ('special_array([0, 4, 3, 0, 4])', 3)]))
    results.append(check("2389. Longest Subsequence With Limited Sum", [('answer_queries([4, 5, 2, 1], [3, 10, 21])', [2, 3, 4]), ('answer_queries([2, 3, 4, 5], [1])', [0])]))
    results.append(check("1385. Find the Distance Value Between Two Arrays", [('find_the_distance_value([4, 5, 8], [10, 9, 1, 8], 2)', 2), ('find_the_distance_value([1, 4, 2, 3], [-4, -3, 6, 10, 20, 30], 3)', 2)]))
    results.append(check("2300. Successful Pairs of Spells and Potions", [('successful_pairs([5, 1, 3], [1, 2, 3, 4, 5], 7)', [4, 0, 3]), ('successful_pairs([3, 1, 2], [8, 5, 8], 16)', [2, 0, 2])]))
    results.append(check("1300. Sum of Mutated Array Closest to Target", [('find_best_value([4, 9, 3], 10)', 3), ('find_best_value([2, 3, 5], 10)', 5), ('find_best_value([60864, 25176, 27249, 21296, 20204], 56803)', 11361)]))
    if all(results):
        print("Every solution passes its tests.")
