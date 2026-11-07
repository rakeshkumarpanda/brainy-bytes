# 4.1 Complexity, timing and profiling
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


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


# ================================================================== 219. Contains Duplicate II (Easy)
# https://leetcode.com/problems/contains-duplicate-ii/
# Pattern: Remember the last index of each value
# Idea: A dict from value to its last index answers "where did I see this before" in O(1), so one
# pass is enough: O(n) instead of comparing all pairs.

def contains_nearby_duplicate(nums, k):
    last_index = {}
    for i, value in enumerate(nums):
        if value in last_index and i - last_index[value] <= k:
            return True
        last_index[value] = i
    return False


# ================================================================== 2006. Count Number of Pairs With Absolute Difference K (Easy)
# https://leetcode.com/problems/count-number-of-pairs-with-absolute-difference-k/
# Pattern: Count what you have seen
# Idea: For each number, the partners seen so far are x − k and x + k. A dict of counts finds them
# in O(1), so the whole list takes O(n).

def count_k_difference(nums, k):
    seen = {}
    pairs = 0
    for x in nums:
        pairs += seen.get(x - k, 0) + seen.get(x + k, 0)
        seen[x] = seen.get(x, 0) + 1
    return pairs


# ================================================================== 1010. Pairs of Songs With Total Durations Divisible by 60 (Medium)
# https://leetcode.com/problems/pairs-of-songs-with-total-durations-divisible-by-60/
# Pattern: Group by remainder
# Idea: Two songs fit when their remainders mod 60 add up to 0 or 60. Count remainders seen so far:
# O(n) instead of O(n²).

def num_pairs_divisible_by60(time):
    count = [0] * 60
    pairs = 0
    for t in time:
        r = t % 60
        pairs += count[(60 - r) % 60]
        count[r] += 1
    return pairs


# ================================================================== 454. 4Sum II (Medium)
# https://leetcode.com/problems/4sum-ii/
# Pattern: Meet in the middle
# Idea: Trying all four lists is O(n4). Count every a + b in a dict (O(n²)), then look up −(c + d)
# for every pair of the other two lists (O(n²)).

def four_sum_count(nums1, nums2, nums3, nums4):
    sums = {}
    for a in nums1:
        for b in nums2:
            sums[a + b] = sums.get(a + b, 0) + 1
    total = 0
    for c in nums3:
        for d in nums4:
            total += sums.get(-(c + d), 0)
    return total


# ================================================================== 974. Subarray Sums Divisible by K (Medium)
# https://leetcode.com/problems/subarray-sums-divisible-by-k/
# Pattern: Prefix sums and remainders
# Idea: A subarray sum is prefix[j] − prefix[i]. It is divisible by k when both prefixes have the
# same remainder. Count remainders: O(n) instead of trying all O(n²) subarrays.

def subarrays_div_by_k(nums, k):
    count = {0: 1}
    prefix = 0
    result = 0
    for x in nums:
        prefix = (prefix + x) % k
        result += count.get(prefix, 0)
        count[prefix] = count.get(prefix, 0) + 1
    return result


# ================================================================== 209. Minimum Size Subarray Sum (Medium)
# https://leetcode.com/problems/minimum-size-subarray-sum/
# Pattern: A sliding window
# Idea: Grow the window on the right, shrink it from the left while the sum is big enough. Each
# index enters and leaves once, so it is O(n).

def min_sub_array_len(target, nums):
    best = len(nums) + 1
    total = 0
    left = 0
    for right, x in enumerate(nums):
        total += x
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best > len(nums) else best


# ================================================================== 1004. Max Consecutive Ones III (Medium)
# https://leetcode.com/problems/max-consecutive-ones-iii/
# Pattern: A window with at most k zeros
# Idea: Move the right end one step at a time. When the window holds more than k zeros, move the
# left end until it does not. O(n) time, O(1) memory.

def longest_ones(nums, k):
    left = 0
    zeros = 0
    best = 0
    for right, x in enumerate(nums):
        if x == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


# ================================================================== 204. Count Primes (Medium)
# https://leetcode.com/problems/count-primes/
# Pattern: Sieve of Eratosthenes
# Idea: Testing each number by division is about O(n √n). The sieve crosses out multiples of each
# prime starting at p², which is O(n log log n).

def count_primes(n):
    if n < 3:
        return 0
    is_prime = [True] * n
    is_prime[0] = is_prime[1] = False
    p = 2
    while p * p < n:
        if is_prime[p]:
            for multiple in range(p * p, n, p):
                is_prime[multiple] = False
        p += 1
    return sum(is_prime)


# ================================================================== 287. Find the Duplicate Number (Medium)
# https://leetcode.com/problems/find-the-duplicate-number/
# Pattern: Treat the list as a linked list
# Idea: Without changing the list and with O(1) memory: i points to nums[i]. The repeated value is
# where a cycle starts. Floyd's slow and fast pointers find it in O(n).

def find_duplicate_number(nums):
    slow = nums[0]
    fast = nums[0]
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


# ================================================================== 41. First Missing Positive (Hard)
# https://leetcode.com/problems/first-missing-positive/
# Pattern: Use the list itself as the table
# Idea: O(n) time and O(1) extra memory: swap each value v into place v − 1. Then the first place i
# that does not hold i + 1 gives the answer.

def first_missing_positive(nums):
    n = len(nums)
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            target = nums[i] - 1
            nums[i], nums[target] = nums[target], nums[i]
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    return n + 1


if __name__ == "__main__":
    results = []
    results.append(check("219. Contains Duplicate II", [('contains_nearby_duplicate([1, 2, 3, 1], 3)', True), ('contains_nearby_duplicate([1, 0, 1, 1], 1)', True), ('contains_nearby_duplicate([1, 2, 3, 1, 2, 3], 2)', False)]))
    results.append(check("2006. Count Number of Pairs With Absolute Difference K", [('count_k_difference([1, 2, 2, 1], 1)', 4), ('count_k_difference([1, 3], 3)', 0), ('count_k_difference([3, 2, 1, 5, 4], 2)', 3)]))
    results.append(check("1010. Pairs of Songs With Total Durations Divisible by 60", [('num_pairs_divisible_by60([30, 20, 150, 100, 40])', 3), ('num_pairs_divisible_by60([60, 60, 60])', 3)]))
    results.append(check("454. 4Sum II", [('four_sum_count([1, 2], [-2, -1], [-1, 2], [0, 2])', 2), ('four_sum_count([0], [0], [0], [0])', 1)]))
    results.append(check("974. Subarray Sums Divisible by K", [('subarrays_div_by_k([4, 5, 0, -2, -3, 1], 5)', 7), ('subarrays_div_by_k([5], 9)', 0)]))
    results.append(check("209. Minimum Size Subarray Sum", [('min_sub_array_len(7, [2, 3, 1, 2, 4, 3])', 2), ('min_sub_array_len(4, [1, 4, 4])', 1), ('min_sub_array_len(11, [1, 1, 1, 1, 1, 1, 1, 1])', 0)]))
    results.append(check("1004. Max Consecutive Ones III", [('longest_ones([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2)', 6), ('longest_ones([0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3)', 10)]))
    results.append(check("204. Count Primes", [('count_primes(10)', 4), ('count_primes(0)', 0), ('count_primes(1)', 0), ('count_primes(100)', 25)]))
    results.append(check("287. Find the Duplicate Number", [('find_duplicate_number([1, 3, 4, 2, 2])', 2), ('find_duplicate_number([3, 1, 3, 4, 2])', 3), ('find_duplicate_number([3, 3, 3, 3, 3])', 3)]))
    results.append(check("41. First Missing Positive", [('first_missing_positive([1, 2, 0])', 3), ('first_missing_positive([3, 4, -1, 1])', 2), ('first_missing_positive([7, 8, 9, 11, 12])', 1)]))
    if all(results):
        print("Every solution passes its tests.")
