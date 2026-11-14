# 3.3 Boosting: small trees that fix each other
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


# ================================================================== 1480. Running Sum of 1d Array (Easy)
# https://leetcode.com/problems/running-sum-of-1d-array/
# Pattern: Keep adding to a total
# Idea: Each answer is the previous answer plus the next number. A boosted model is built the same
# way: each round adds one more tree to the running total.

def running_sum(nums):
    out = []
    total = 0
    for x in nums:
        total = total + x
        out.append(total)
    return out


# ================================================================== 1732. Find the Highest Altitude (Easy)
# https://leetcode.com/problems/find-the-highest-altitude/
# Pattern: Running total and its maximum
# Idea: Start at altitude 0, add each gain, and remember the highest altitude seen, including the
# start.

def largest_altitude(gain):
    altitude = 0
    best = 0
    for g in gain:
        altitude = altitude + g
        best = max(best, altitude)
    return best


# ================================================================== 1413. Minimum Value to Get Positive Step by Step Sum (Easy)
# https://leetcode.com/problems/minimum-value-to-get-positive-step-by-step-sum/
# Pattern: Fix the lowest point of the running sum
# Idea: Track the lowest running sum. The start value must lift that lowest point to at least 1, so
# the answer is 1 minus the lowest running sum, but never less than 1.

def min_start_value(nums):
    total = 0
    lowest = 0
    for x in nums:
        total = total + x
        lowest = min(lowest, total)
    return 1 - lowest


# ================================================================== 724. Find Pivot Index (Easy)
# https://leetcode.com/problems/find-pivot-index/
# Pattern: Left sum against right sum
# Idea: Compute the total once. Walk left to right keeping the left sum. The right sum is total
# minus left sum minus the current value. The first index where they match is the answer.

def pivot_index(nums):
    total = sum(nums)
    left = 0
    for i, x in enumerate(nums):
        if left == total - left - x:
            return i
        left = left + x
    return -1


# ================================================================== 238. Product of Array Except Self (Medium)
# https://leetcode.com/problems/product-of-array-except-self/
# Pattern: Prefix products times suffix products
# Idea: For each position multiply the product of everything before it by the product of everything
# after it. Two passes, no division.

def product_except_self(nums):
    n = len(nums)
    out = [1] * n
    left = 1
    for i in range(n):
        out[i] = left
        left = left * nums[i]
    right = 1
    for i in range(n - 1, -1, -1):
        out[i] = out[i] * right
        right = right * nums[i]
    return out


# ================================================================== 134. Gas Station (Medium)
# https://leetcode.com/problems/gas-station/
# Pattern: Restart after the running total goes negative
# Idea: If the total gas is less than the total cost, no start works. Otherwise walk once, keeping a
# running tank. When it goes below zero, no station so far can be the start, so restart from the
# next one. Like boosting, every failure tells you where to look next.

def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    start = 0
    tank = 0
    for i in range(len(gas)):
        tank = tank + gas[i] - cost[i]
        if tank < 0:
            start = i + 1
            tank = 0
    return start


if __name__ == "__main__":
    results = []
    results.append(check("1480. Running Sum of 1d Array", [('running_sum([1, 2, 3, 4])', [1, 3, 6, 10]), ('running_sum([3, 1, 2, 10, 1])', [3, 4, 6, 16, 17])]))
    results.append(check("1732. Find the Highest Altitude", [('largest_altitude([-5, 1, 5, 0, -7])', 1), ('largest_altitude([-4, -3, -2, -1, 4, 3, 2])', 0)]))
    results.append(check("1413. Minimum Value to Get Positive Step by Step Sum", [('min_start_value([-3, 2, -3, 4, 2])', 5), ('min_start_value([1, 2])', 1)]))
    results.append(check("724. Find Pivot Index", [('pivot_index([1, 7, 3, 6, 5, 6])', 3), ('pivot_index([1, 2, 3])', -1)]))
    results.append(check("238. Product of Array Except Self", [('product_except_self([1, 2, 3, 4])', [24, 12, 8, 6]), ('product_except_self([-1, 1, 0, -3, 3])', [0, 0, 9, 0, 0])]))
    results.append(check("134. Gas Station", [('can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2])', 3), ('can_complete_circuit([2, 3, 4], [3, 4, 3])', -1)]))
    if all(results):
        print("Every solution passes its tests.")
