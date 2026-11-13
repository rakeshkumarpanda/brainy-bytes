# 3.2 Random forests: many trees vote
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


# ================================================================== 169. Majority Element (Easy)
# https://leetcode.com/problems/majority-element/
# Pattern: One pass vote counting
# Idea: Boyer and Moore voting: keep a candidate and a count. A matching value adds 1, a different
# value takes 1 away, and at 0 the next value becomes the candidate. The majority always survives,
# just as a forest’s majority survives the noisy trees.

def majority_element(nums):
    candidate = None
    count = 0
    for x in nums:
        if count == 0:
            candidate = x
        if x == candidate:
            count = count + 1
        else:
            count = count - 1
    return candidate


# ================================================================== 229. Majority Element II (Medium)
# https://leetcode.com/problems/majority-element-ii/
# Pattern: Count, then keep values above n/3
# Idea: Count every value and keep those that appear more than n/3 times. At most two values can do
# that. (Boyer and Moore with two candidates does it in constant memory.)

def majority_element_ii(nums):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    return sorted([x for x in counts if counts[x] > len(nums) // 3])


# ================================================================== 1287. Element Appearing More Than 25% In Sorted Array (Easy)
# https://leetcode.com/problems/element-appearing-more-than-25-in-sorted-array/
# Pattern: Compare with the value a quarter further on
# Idea: In a sorted array a value that fills more than a quarter must equal the value n/4 positions
# later. Check each position against that one.

def find_special_integer(arr):
    step = len(arr) // 4
    for i in range(len(arr) - step):
        if arr[i] == arr[i + step]:
            return arr[i]
    return arr[0]


# ================================================================== 347. Top K Frequent Elements (Medium)
# https://leetcode.com/problems/top-k-frequent-elements/
# Pattern: Count, then sort by count
# Idea: Count each value and return the k values with the largest counts. Sorting by count is the
# simple way. Buckets by count make it linear.

def top_k_frequent(nums, k):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    ordered = sorted(counts, key=lambda v: (-counts[v], v))
    return ordered[:k]


# ================================================================== 2404. Most Frequent Even Element (Easy)
# https://leetcode.com/problems/most-frequent-even-element/
# Pattern: Count only the even values
# Idea: Count the even values. Return the one with the largest count, the smallest value when counts
# tie, or −1 when there are no even values.

def most_frequent_even(nums):
    counts = {}
    for x in nums:
        if x % 2 == 0:
            counts[x] = counts.get(x, 0) + 1
    if not counts:
        return -1
    return min(counts, key=lambda v: (-counts[v], v))


# ================================================================== 1394. Find Lucky Integer in an Array (Easy)
# https://leetcode.com/problems/find-lucky-integer-in-an-array/
# Pattern: A value whose count equals itself
# Idea: Count every value. A lucky integer appears exactly as many times as its value. Return the
# largest one, or −1.

def find_lucky(arr):
    counts = {}
    for x in arr:
        counts[x] = counts.get(x, 0) + 1
    best = -1
    for x in counts:
        if counts[x] == x and x > best:
            best = x
    return best


if __name__ == "__main__":
    results = []
    results.append(check("169. Majority Element", [('majority_element([3, 2, 3])', 3), ('majority_element([2, 2, 1, 1, 1, 2, 2])', 2)]))
    results.append(check("229. Majority Element II", [('majority_element_ii([3, 2, 3])', [3]), ('majority_element_ii([1, 2])', [1, 2])]))
    results.append(check("1287. Element Appearing More Than 25% In Sorted Array", [('find_special_integer([1, 2, 2, 6, 6, 6, 6, 7, 10])', 6), ('find_special_integer([1, 1])', 1)]))
    results.append(check("347. Top K Frequent Elements", [('top_k_frequent([1, 1, 1, 2, 2, 3], 2)', [1, 2]), ('top_k_frequent([1], 1)', [1])]))
    results.append(check("2404. Most Frequent Even Element", [('most_frequent_even([0, 1, 2, 2, 4, 4, 1])', 2), ('most_frequent_even([29, 47, 21, 41, 13, 37, 25, 7])', -1)]))
    results.append(check("1394. Find Lucky Integer in an Array", [('find_lucky([2, 2, 3, 4])', 2), ('find_lucky([1, 2, 2, 3, 3, 3])', 3)]))
    if all(results):
        print("Every solution passes its tests.")
