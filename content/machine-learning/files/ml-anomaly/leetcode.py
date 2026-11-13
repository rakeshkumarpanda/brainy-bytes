# 3.1 Anomaly detection
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


# ================================================================== 136. Single Number (Easy)
# https://leetcode.com/problems/single-number/
# Pattern: XOR cancels every pair
# Idea: XOR all the numbers. Each pair cancels to 0, so the number that appears once is what is
# left. The odd one out stands out because everything else matches.

def single_number(nums):
    result = 0
    for v in nums:
        result = result ^ v
    return result


# ================================================================== 268. Missing Number (Easy)
# https://leetcode.com/problems/missing-number/
# Pattern: Compare the expected sum with the actual sum
# Idea: The numbers 0 to n add up to n(n + 1)/2. Subtract the actual sum and the gap is the missing
# number. Comparing what you expect with what you see is the core of anomaly detection.

def missing_number(nums):
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)


# ================================================================== 219. Contains Duplicate II (Easy)
# https://leetcode.com/problems/contains-duplicate-ii/
# Pattern: Remember where each value was last seen
# Idea: Keep the last index of each value in a dictionary. If a value comes back within k positions,
# answer true. It is the same pattern as flagging a repeated event inside a time window.

def contains_nearby_duplicate(nums, k):
    last = {}
    for i, v in enumerate(nums):
        if v in last and i - last[v] <= k:
            return True
        last[v] = i
    return False


# ================================================================== 287. Find the Duplicate Number (Medium)
# https://leetcode.com/problems/find-the-duplicate-number/
# Pattern: Treat values as next pointers and find the cycle
# Idea: Read nums as a linked list where i points to nums[i]. The duplicate value is where a cycle
# starts. Floyd’s tortoise and hare finds it in O(1) extra memory.

def find_duplicate(nums):
    slow = fast = nums[0]
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow


# ================================================================== 442. Find All Duplicates in an Array (Medium)
# https://leetcode.com/problems/find-all-duplicates-in-an-array/
# Pattern: Mark seen values by flipping signs in place
# Idea: Values are 1 to n, so value v can mark position v − 1 by making it negative. Meeting an
# already negative mark means v is a duplicate. Ours sorts the answer so it can be checked, and
# LeetCode accepts any order.

def find_duplicates(nums):
    nums = list(nums)
    found = []
    for v in nums:
        i = abs(v) - 1
        if nums[i] < 0:
            found.append(abs(v))
        else:
            nums[i] = -nums[i]
    return sorted(found)


# ================================================================== 41. First Missing Positive (Hard)
# https://leetcode.com/problems/first-missing-positive/
# Pattern: Place each value at its own index, then scan
# Idea: Swap each value v in 1 to n into position v − 1. Afterwards the first position i that does
# not hold i + 1 gives the answer. It runs in O(n) time with O(1) extra memory.

def first_missing_positive(nums):
    nums = list(nums)
    n = len(nums)
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            j = nums[i] - 1
            nums[i], nums[j] = nums[j], nums[i]
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    return n + 1


if __name__ == "__main__":
    results = []
    results.append(check("136. Single Number", [('single_number([4, 1, 2, 1, 2])', 4), ('single_number([2, 2, 1])', 1)]))
    results.append(check("268. Missing Number", [('missing_number([3, 0, 1])', 2), ('missing_number([9, 6, 4, 2, 3, 5, 7, 0, 1])', 8)]))
    results.append(check("219. Contains Duplicate II", [('contains_nearby_duplicate([1, 2, 3, 1], 3)', True), ('contains_nearby_duplicate([1, 2, 3, 1, 2, 3], 2)', False)]))
    results.append(check("287. Find the Duplicate Number", [('find_duplicate([1, 3, 4, 2, 2])', 2), ('find_duplicate([3, 1, 3, 4, 2])', 3)]))
    results.append(check("442. Find All Duplicates in an Array", [('find_duplicates([4, 3, 2, 7, 8, 2, 3, 1])', [2, 3]), ('find_duplicates([1, 1, 2])', [1])]))
    results.append(check("41. First Missing Positive", [('first_missing_positive([1, 2, 0])', 3), ('first_missing_positive([3, 4, -1, 1])', 2), ('first_missing_positive([7, 8, 9, 11, 12])', 1)]))
    if all(results):
        print("Every solution passes its tests.")
