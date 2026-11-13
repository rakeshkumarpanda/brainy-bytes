# 4.2 Validation: honest estimates of performance
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


# ================================================================== 1013. Partition Array Into Three Parts With Equal Sum (Easy)
# https://leetcode.com/problems/partition-array-into-three-parts-with-equal-sum/
# Pattern: Cut whenever a third of the total is reached
# Idea: The total must split into three equal thirds. Walk through, adding to a running sum, and cut
# each time it reaches one third. Like making folds, you split the data into equal parts in order.

def can_three_parts_equal_sum(arr):
    total = sum(arr)
    if total % 3 != 0:
        return False
    target = total // 3
    running = 0
    parts = 0
    for x in arr:
        running = running + x
        if running == target:
            parts = parts + 1
            running = 0
    return parts >= 3


# ================================================================== 189. Rotate Array (Medium)
# https://leetcode.com/problems/rotate-array/
# Pattern: Slice the last k to the front
# Idea: Rotating right by k moves the last k values to the front. Take k modulo the length first.
# Rotating which fold is held out is the heart of cross validation.

def rotate(nums, k):
    k = k % len(nums)
    nums[:] = nums[-k:] + nums[:-k] if k else nums
    return nums


# ================================================================== 1652. Defuse the Bomb (Easy)
# https://leetcode.com/problems/defuse-the-bomb/
# Pattern: A window that wraps around
# Idea: For k > 0 sum the next k values, for k < 0 the previous |k|, wrapping around the end with
# the modulo operator, and 0 for k = 0.

def decrypt(code, k):
    n = len(code)
    out = []
    for i in range(n):
        if k > 0:
            out.append(sum(code[(i + j) % n] for j in range(1, k + 1)))
        elif k < 0:
            out.append(sum(code[(i - j) % n] for j in range(1, -k + 1)))
        else:
            out.append(0)
    return out


# ================================================================== 1343. Number of Sub-arrays of Size K and Average Greater than or Equal to Threshold (Medium)
# https://leetcode.com/problems/number-of-sub-arrays-of-size-k-and-average-greater-than-or-equal-to-threshold/
# Pattern: Slide a fixed window
# Idea: Keep the sum of the current window of k values. Slide it one step by adding the new value
# and removing the oldest. Compare the sum with k times the threshold.

def num_of_subarrays(arr, k, threshold):
    window = sum(arr[:k])
    count = 1 if window >= k * threshold else 0
    for i in range(k, len(arr)):
        window = window + arr[i] - arr[i - k]
        if window >= k * threshold:
            count = count + 1
    return count


# ================================================================== 2090. K Radius Subarray Averages (Medium)
# https://leetcode.com/problems/k-radius-subarray-averages/
# Pattern: A centred sliding window
# Idea: Each answer is the average of the 2k + 1 values centred on that position, or −1 if the
# window does not fit. Slide the window sum as in the last problem and use integer division.

def get_averages(nums, k):
    n = len(nums)
    size = 2 * k + 1
    out = [-1] * n
    if size > n:
        return out
    window = sum(nums[:size])
    out[k] = window // size
    for i in range(size, n):
        window = window + nums[i] - nums[i - size]
        out[i - k] = window // size
    return out


# ================================================================== 1876. Substrings of Size Three with Distinct Characters (Easy)
# https://leetcode.com/problems/substrings-of-size-three-with-distinct-characters/
# Pattern: Check every window of three
# Idea: Look at every window of three letters and count those whose three letters are all different.

def count_good_substrings(s):
    count = 0
    for i in range(len(s) - 2):
        if len(set(s[i:i + 3])) == 3:
            count = count + 1
    return count


if __name__ == "__main__":
    results = []
    results.append(check("1013. Partition Array Into Three Parts With Equal Sum", [('can_three_parts_equal_sum([0, 2, 1, -6, 6, -7, 9, 1, 2, 0, 1])', True), ('can_three_parts_equal_sum([0, 2, 1, -6, 6, 7, 9, -1, 2, 0, 1])', False)]))
    results.append(check("189. Rotate Array", [('rotate([1, 2, 3, 4, 5, 6, 7], 3)', [5, 6, 7, 1, 2, 3, 4]), ('rotate([-1, -100, 3, 99], 2)', [3, 99, -1, -100])]))
    results.append(check("1652. Defuse the Bomb", [('decrypt([5, 7, 1, 4], 3)', [12, 10, 16, 13]), ('decrypt([2, 4, 9, 3], -2)', [12, 5, 6, 13])]))
    results.append(check("1343. Number of Sub-arrays of Size K and Average Greater than or Equal to Threshold", [('num_of_subarrays([2, 2, 2, 2, 5, 5, 5, 8], 3, 4)', 3), ('num_of_subarrays([11, 13, 17, 23, 29, 31, 7, 5, 2, 3], 3, 5)', 6)]))
    results.append(check("2090. K Radius Subarray Averages", [('get_averages([7, 4, 3, 9, 1, 8, 5, 2, 6], 3)', [-1, -1, -1, 5, 4, 4, -1, -1, -1]), ('get_averages([100000], 0)', [100000])]))
    results.append(check("1876. Substrings of Size Three with Distinct Characters", [('count_good_substrings("xyzzaz")', 1), ('count_good_substrings("aababcabc")', 4)]))
    if all(results):
        print("Every solution passes its tests.")
