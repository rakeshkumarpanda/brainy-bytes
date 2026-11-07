# 2.2 itertools, functools and operator
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


# ================================================================== 303. Range Sum Query - Immutable (Easy)
# https://leetcode.com/problems/range-sum-query-immutable/
# Pattern: Prefix sums with accumulate
# Idea: Build P = accumulate(nums, initial=0) once. Then the sum from left to right is P[right + 1]
# − P[left], one subtraction per query.

from itertools import accumulate


class NumArray:
    def __init__(self, nums):
        self.prefix = list(accumulate(nums, initial=0))

    def sumRange(self, left, right):
        return self.prefix[right + 1] - self.prefix[left]


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 1732. Find the Highest Altitude (Easy)
# https://leetcode.com/problems/find-the-highest-altitude/
# Pattern: Running totals, then max
# Idea: The altitudes are the running totals of gain starting from 0, which is accumulate(gain,
# initial=0).

from itertools import accumulate


def largest_altitude(gain):
    return max(accumulate(gain, initial=0))


# ================================================================== 1310. XOR Queries of a Subarray (Medium)
# https://leetcode.com/problems/xor-queries-of-a-subarray/
# Pattern: Prefix XOR with accumulate
# Idea: XOR works like a sum that undoes itself: P[r + 1] ^ P[l] is the XOR of arr[l] to arr[r].

from itertools import accumulate
import operator


def xor_queries(arr, queries):
    prefix = list(accumulate(arr, operator.xor, initial=0))
    answers = []
    for left, right in queries:
        answers.append(prefix[right + 1] ^ prefix[left])
    return answers


# ================================================================== 1313. Decompress Run-Length Encoded List (Easy)
# https://leetcode.com/problems/decompress-run-length-encoded-list/
# Pattern: batched, repeat and chain
# Idea: Read the list two numbers at a time with batched. Each pair (freq, val) becomes repeat(val,
# freq). chain joins them.

from itertools import batched, chain, repeat


def decompress_rle_list(nums):
    parts = []
    for freq, val in batched(nums, 2):
        parts.append(repeat(val, freq))
    return list(chain.from_iterable(parts))


# ================================================================== 443. String Compression (Medium)
# https://leetcode.com/problems/string-compression/
# Pattern: groupby gives the runs
# Idea: Each run of the same letter becomes the letter plus its count (only if the count is above
# 1). Write the result back into chars and return its length.

from itertools import groupby


def compress_chars(chars):
    result = []
    for letter, group in groupby(chars):
        size = len(list(group))
        result.append(letter)
        if size > 1:
            result.extend(str(size))
    chars[:] = result
    return len(result)


# ================================================================== 1446. Consecutive Characters (Easy)
# https://leetcode.com/problems/consecutive-characters/
# Pattern: Longest run with groupby
# Idea: groupby splits the text into runs of one letter. The answer is the length of the longest
# run.

from itertools import groupby


def max_power(s):
    best = 0
    for letter, group in groupby(s):
        best = max(best, len(list(group)))
    return best


# ================================================================== 830. Positions of Large Groups (Easy)
# https://leetcode.com/problems/positions-of-large-groups/
# Pattern: groupby over enumerate
# Idea: Group (index, letter) pairs by the letter. The first and last index of each group give its
# interval. Keep groups of 3 or more.

from itertools import groupby


def large_group_positions(s):
    result = []
    for letter, group in groupby(enumerate(s), key=lambda pair: pair[1]):
        positions = [index for index, ch in group]
        if len(positions) >= 3:
            result.append([positions[0], positions[-1]])
    return result


# ================================================================== 784. Letter Case Permutation (Medium)
# https://leetcode.com/problems/letter-case-permutation/
# Pattern: product of choices per character
# Idea: A letter has two choices (lower, upper), a digit has one. product of all the choices gives
# every string.

from itertools import product


def letter_case_permutation(s):
    choices = []
    for ch in s:
        if ch.isalpha():
            choices.append((ch.lower(), ch.upper()))
        else:
            choices.append((ch,))
    return ["".join(t) for t in product(*choices)]


# ================================================================== 47. Permutations II (Medium)
# https://leetcode.com/problems/permutations-ii/
# Pattern: permutations, then remove repeats
# Idea: permutations treats equal numbers as different positions, so it repeats some orders. A set
# removes the repeats. Fine for small inputs, backtracking with a counter is faster.

from itertools import permutations


def permute_unique(nums):
    return [list(p) for p in sorted(set(permutations(nums)))]


# ================================================================== 1588. Sum of All Odd Length Subarrays (Easy)
# https://leetcode.com/problems/sum-of-all-odd-length-subarrays/
# Pattern: Prefix sums, then every odd window
# Idea: With prefix sums each subarray sum is one subtraction. Try every start and every odd length.

from itertools import accumulate


def sum_odd_length_subarrays(arr):
    prefix = list(accumulate(arr, initial=0))
    total = 0
    for start in range(len(arr)):
        for end in range(start + 1, len(arr) + 1, 2):
            total += prefix[end] - prefix[start]
    return total


if __name__ == "__main__":
    results = []
    results.append(check("303. Range Sum Query - Immutable", [('play(NumArray, ["NumArray", "sumRange", "sumRange", "sumRange"], [[[-2, 0, 3, -5, 2, -1]], [0, 2], [2, 5], [0, 5]])', [None, 1, -1, -3])]))
    results.append(check("1732. Find the Highest Altitude", [('largest_altitude([-5, 1, 5, 0, -7])', 1), ('largest_altitude([-4, -3, -2, -1, 4, 3, 2])', 0)]))
    results.append(check("1310. XOR Queries of a Subarray", [('xor_queries([1, 3, 4, 8], [[0, 1], [1, 2], [0, 3], [3, 3]])', [2, 7, 14, 8])]))
    results.append(check("1313. Decompress Run-Length Encoded List", [('decompress_rle_list([1, 2, 3, 4])', [2, 4, 4, 4]), ('decompress_rle_list([1, 1, 2, 3])', [1, 3, 3])]))
    results.append(check("443. String Compression", [('(lambda c: (compress_chars(c), c))(list("aabbccc"))', [6, ['a', '2', 'b', '2', 'c', '3']]), ('(lambda c: (compress_chars(c), c))(list("abbbbbbbbbbbb"))', [4, ['a', 'b', '1', '2']])]))
    results.append(check("1446. Consecutive Characters", [('max_power("leetcode")', 2), ('max_power("abbcccddddeeeeedcba")', 5)]))
    results.append(check("830. Positions of Large Groups", [('large_group_positions("abbxxxxzzy")', [[3, 6]]), ('large_group_positions("abcdddeeeeaabbbcd")', [[3, 5], [6, 9], [12, 14]])]))
    results.append(check("784. Letter Case Permutation", [('sorted(letter_case_permutation("a1b2"))', ['A1B2', 'A1b2', 'a1B2', 'a1b2']), ('letter_case_permutation("3z4")', ['3z4', '3Z4'])]))
    results.append(check("47. Permutations II", [('permute_unique([1, 1, 2])', [[1, 1, 2], [1, 2, 1], [2, 1, 1]]), ('len(permute_unique([1, 2, 3]))', 6)]))
    results.append(check("1588. Sum of All Odd Length Subarrays", [('sum_odd_length_subarrays([1, 4, 2, 5, 3])', 58), ('sum_odd_length_subarrays([1, 2])', 3)]))
    if all(results):
        print("Every solution passes its tests.")
