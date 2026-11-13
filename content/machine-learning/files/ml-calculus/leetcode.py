# 2.2 Calculus for ML: derivatives, gradients and gradient descent
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


# ================================================================== 852. Peak Index in a Mountain Array (Medium)
# https://leetcode.com/problems/peak-index-in-a-mountain-array/
# Pattern: Follow the slope (binary search)
# Idea: Look at the middle. If the next value is bigger, the slope goes up, so the peak is to the
# right. Otherwise it is here or to the left. This is gradient ascent on a list.

def peak_index_in_mountain_array(arr):
    low = 0
    high = len(arr) - 1
    while low < high:
        mid = (low + high) // 2
        if arr[mid] < arr[mid + 1]:
            low = mid + 1
        else:
            high = mid
    return low


# ================================================================== 441. Arranging Coins (Easy)
# https://leetcode.com/problems/arranging-coins/
# Pattern: Binary search on a growing function
# Idea: k full rows need k(k + 1)/2 coins, which grows with k. Binary search for the largest k that
# fits in n.

def arrange_coins(n):
    low = 0
    high = n
    while low < high:
        mid = (low + high + 1) // 2
        if mid * (mid + 1) // 2 <= n:
            low = mid
        else:
            high = mid - 1
    return low


# ================================================================== 633. Sum of Square Numbers (Medium)
# https://leetcode.com/problems/sum-of-square-numbers/
# Pattern: Two pointers on a monotone sum
# Idea: Start with a = 0 and b = the integer square root of c. If a2 + b2 is too small, raise a. If
# too big, lower b.

def judge_square_sum(c):
    a = 0
    b = int(c ** 0.5)
    while b * b > c:
        b = b - 1
    while a <= b:
        total = a * a + b * b
        if total == c:
            return True
        if total < c:
            a = a + 1
        else:
            b = b - 1
    return False


# ================================================================== 1283. Find the Smallest Divisor Given a Threshold (Medium)
# https://leetcode.com/problems/find-the-smallest-divisor-given-a-threshold/
# Pattern: Binary search on the answer
# Idea: A bigger divisor makes the sum of rounded up quotients smaller. Binary search for the
# smallest divisor whose sum is at most the threshold.

def smallest_divisor(nums, threshold):
    low = 1
    high = max(nums)
    while low < high:
        mid = (low + high) // 2
        total = 0
        for x in nums:
            total = total + (x + mid - 1) // mid
        if total <= threshold:
            high = mid
        else:
            low = mid + 1
    return low


# ================================================================== 1011. Capacity To Ship Packages Within D Days (Medium)
# https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/
# Pattern: Binary search on the answer
# Idea: The capacity is at least the heaviest package and at most the total. For a guess, count the
# days needed by filling each day greedily. Fewer days with more capacity: binary search.

def days_needed(weights, capacity):
    days = 1
    load = 0
    for w in weights:
        if load + w > capacity:
            days = days + 1
            load = 0
        load = load + w
    return days


def ship_within_days(weights, days):
    low = max(weights)
    high = sum(weights)
    while low < high:
        mid = (low + high) // 2
        if days_needed(weights, mid) <= days:
            high = mid
        else:
            low = mid + 1
    return low


# ================================================================== 2529. Maximum Count of Positive Integer and Negative Integer (Easy)
# https://leetcode.com/problems/maximum-count-of-positive-integer-and-negative-integer/
# Pattern: Binary search for where the sign changes
# Idea: The list is sorted, so find the first index that is at least 0 and the first index that is
# above 0. The counts follow from those two positions.

def first_index(nums, limit):
    low = 0
    high = len(nums)
    while low < high:
        mid = (low + high) // 2
        if nums[mid] < limit:
            low = mid + 1
        else:
            high = mid
    return low


def maximum_count(nums):
    negatives = first_index(nums, 0)
    positives = len(nums) - first_index(nums, 1)
    return max(negatives, positives)


if __name__ == "__main__":
    results = []
    results.append(check("852. Peak Index in a Mountain Array", [('peak_index_in_mountain_array([0, 1, 0])', 1), ('peak_index_in_mountain_array([0, 2, 1, 0])', 1), ('peak_index_in_mountain_array([0, 10, 5, 2])', 1)]))
    results.append(check("441. Arranging Coins", [('arrange_coins(5)', 2), ('arrange_coins(8)', 3), ('arrange_coins(1)', 1)]))
    results.append(check("633. Sum of Square Numbers", [('judge_square_sum(5)', True), ('judge_square_sum(3)', False), ('judge_square_sum(0)', True)]))
    results.append(check("1283. Find the Smallest Divisor Given a Threshold", [('smallest_divisor([1, 2, 5, 9], 6)', 5), ('smallest_divisor([44, 22, 33, 11, 1], 5)', 44)]))
    results.append(check("1011. Capacity To Ship Packages Within D Days", [('ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5)', 15), ('ship_within_days([3, 2, 2, 4, 1, 4], 3)', 6)]))
    results.append(check("2529. Maximum Count of Positive Integer and Negative Integer", [('maximum_count([-2, -1, -1, 1, 2, 3])', 3), ('maximum_count([-3, -2, -1, 0, 0, 1, 2])', 3), ('maximum_count([5, 20, 66, 1314])', 4)]))
    if all(results):
        print("Every solution passes its tests.")
