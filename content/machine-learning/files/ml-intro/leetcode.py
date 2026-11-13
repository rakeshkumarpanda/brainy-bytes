# 1.1 What machine learning is: learning from examples
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


# ================================================================== 1491. Average Salary Excluding the Minimum and Maximum Salary (Easy)
# https://leetcode.com/problems/average-salary-excluding-the-minimum-and-maximum-salary/
# Pattern: Robust average
# Idea: Add everything, then take away the smallest and the largest before you divide by n − 2.
# Dropping extreme values is how a trimmed mean protects a model from outliers.

def average(salary):
    total = 0
    smallest = salary[0]
    largest = salary[0]
    for s in salary:
        total = total + s
        if s < smallest:
            smallest = s
        if s > largest:
            largest = s
    return (total - smallest - largest) / (len(salary) - 2)


# ================================================================== 643. Maximum Average Subarray I (Easy)
# https://leetcode.com/problems/maximum-average-subarray-i/
# Pattern: Sliding window (a moving average)
# Idea: Keep the sum of the last k numbers. Add the new number and take away the one that leaves the
# window. This is how a moving average feature is computed fast.

def find_max_average(nums, k):
    window = 0
    for i in range(k):
        window = window + nums[i]
    best = window
    for i in range(k, len(nums)):
        window = window + nums[i] - nums[i - k]
        if window > best:
            best = window
    return best / k


# ================================================================== 1502. Can Make Arithmetic Progression From Sequence (Easy)
# https://leetcode.com/problems/can-make-arithmetic-progression-from-sequence/
# Pattern: Sort, then check one constant step
# Idea: After sorting, every gap must be the same. A sequence like this fits a straight line
# exactly, the simplest pattern a model can learn.

def can_make_arithmetic_progression(arr):
    arr = sorted(arr)
    step = arr[1] - arr[0]
    for i in range(2, len(arr)):
        if arr[i] - arr[i - 1] != step:
            return False
    return True


# ================================================================== 896. Monotonic Array (Easy)
# https://leetcode.com/problems/monotonic-array/
# Pattern: One pass with two flags
# Idea: Keep two flags, "can still be going up" and "can still be going down". Any drop clears the
# first, any rise clears the second. Checking a trend like this is a common data sanity check.

def is_monotonic(nums):
    going_up = True
    going_down = True
    for i in range(1, len(nums)):
        if nums[i] < nums[i - 1]:
            going_up = False
        if nums[i] > nums[i - 1]:
            going_down = False
    return going_up or going_down


# ================================================================== 1984. Minimum Difference Between Highest and Lowest of K Scores (Easy)
# https://leetcode.com/problems/minimum-difference-between-highest-and-lowest-of-k-scores/
# Pattern: Sort, then slide a window of size k
# Idea: After sorting, the best k scores sit next to each other. Check every window of k neighbours
# and keep the smallest spread.

def minimum_difference(nums, k):
    nums = sorted(nums)
    best = nums[k - 1] - nums[0]
    for i in range(1, len(nums) - k + 1):
        spread = nums[i + k - 1] - nums[i]
        if spread < best:
            best = spread
    return best


# ================================================================== 2148. Count Elements With Strictly Smaller and Greater Elements (Easy)
# https://leetcode.com/problems/count-elements-with-strictly-smaller-and-greater-elements/
# Pattern: Find min and max, then count
# Idea: An element counts when it is not the minimum and not the maximum. Finding the range of a
# feature is the first step of scaling it.

def count_elements(nums):
    smallest = min(nums)
    largest = max(nums)
    count = 0
    for x in nums:
        if smallest < x < largest:
            count = count + 1
    return count


if __name__ == "__main__":
    results = []
    results.append(check("1491. Average Salary Excluding the Minimum and Maximum Salary", [('average([4000, 3000, 1000, 2000])', 2500.0), ('average([1000, 2000, 3000])', 2000.0)]))
    results.append(check("643. Maximum Average Subarray I", [('find_max_average([1, 12, -5, -6, 50, 3], 4)', 12.75), ('find_max_average([5], 1)', 5.0)]))
    results.append(check("1502. Can Make Arithmetic Progression From Sequence", [('can_make_arithmetic_progression([3, 5, 1])', True), ('can_make_arithmetic_progression([1, 2, 4])', False)]))
    results.append(check("896. Monotonic Array", [('is_monotonic([1, 2, 2, 3])', True), ('is_monotonic([6, 5, 4, 4])', True), ('is_monotonic([1, 3, 2])', False)]))
    results.append(check("1984. Minimum Difference Between Highest and Lowest of K Scores", [('minimum_difference([90], 1)', 0), ('minimum_difference([9, 4, 1, 7], 2)', 2)]))
    results.append(check("2148. Count Elements With Strictly Smaller and Greater Elements", [('count_elements([11, 7, 2, 15])', 2), ('count_elements([-3, 3, 3, 90])', 2)]))
    if all(results):
        print("Every solution passes its tests.")
