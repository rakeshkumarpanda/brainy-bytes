# 4.3 lambda, map, filter and comprehensions
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


# ================================================================== 977. Squares of a Sorted Array (Easy)
# https://leetcode.com/problems/squares-of-a-sorted-array/
# Pattern: Comprehension and sorted
# Idea: Square every number with a comprehension, then sort. (A two pointer version does it in
# O(n).)

def sorted_squares(nums):
    return sorted([x * x for x in nums])


# ================================================================== 867. Transpose Matrix (Easy)
# https://leetcode.com/problems/transpose-matrix/
# Pattern: Nested comprehension
# Idea: Row c of the answer is column c of the matrix.

def transpose(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    return [[matrix[r][c] for r in range(rows)] for c in range(cols)]


# ================================================================== 1572. Matrix Diagonal Sum (Easy)
# https://leetcode.com/problems/matrix-diagonal-sum/
# Pattern: Generator expression with sum
# Idea: Add mat[i][i] and mat[i][n − 1 − i]. When n is odd the middle cell was added twice.

def diagonal_sum(mat):
    n = len(mat)
    total = sum(mat[i][i] + mat[i][n - 1 - i] for i in range(n))
    if n % 2 == 1:
        total = total - mat[n // 2][n // 2]
    return total


# ================================================================== 2942. Find Words Containing Character (Easy)
# https://leetcode.com/problems/find-words-containing-character/
# Pattern: Comprehension with enumerate
# Idea: Keep the index i of every word that contains x.

def find_words_containing(words, x):
    return [i for i, word in enumerate(words) if x in word]


# ================================================================== 1748. Sum of Unique Elements (Easy)
# https://leetcode.com/problems/sum-of-unique-elements/
# Pattern: Count, then sum with a filter
# Idea: Count each value, then add the values whose count is 1.

def sum_of_unique(nums):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    return sum(x for x, c in counts.items() if c == 1)


# ================================================================== 1913. Maximum Product Difference Between Two Pairs (Easy)
# https://leetcode.com/problems/maximum-product-difference-between-two-pairs/
# Pattern: sorted
# Idea: Biggest two times each other, minus smallest two times each other.

def max_product_difference(nums):
    s = sorted(nums)
    return s[-1] * s[-2] - s[0] * s[1]


# ================================================================== 1636. Sort Array by Increasing Frequency (Easy)
# https://leetcode.com/problems/sort-array-by-increasing-frequency/
# Pattern: sorted with a tuple key
# Idea: Sort by (count, −value): rarer numbers first, and for equal counts the bigger number first.

def frequency_sort(nums):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    return sorted(nums, key=lambda x: (counts[x], -x))


# ================================================================== 451. Sort Characters By Frequency (Medium)
# https://leetcode.com/problems/sort-characters-by-frequency/
# Pattern: Count, sort by count, join
# Idea: Count each letter, sort the letters by count from high to low, and repeat each one count
# times.

def frequency_sort_text(s):
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    order = sorted(counts, key=lambda ch: (-counts[ch], ch))
    return "".join(ch * counts[ch] for ch in order)


# ================================================================== 791. Custom Sort String (Medium)
# https://leetcode.com/problems/custom-sort-string/
# Pattern: sorted with a dict key
# Idea: Give each letter of order its position. Letters not in order can go anywhere, here at the
# end.

def custom_sort_string(order, s):
    rank = {ch: i for i, ch in enumerate(order)}
    return "".join(sorted(s, key=lambda ch: rank.get(ch, len(order))))


# ================================================================== 179. Largest Number (Medium)
# https://leetcode.com/problems/largest-number/
# Pattern: Custom comparison with cmp_to_key
# Idea: Put a before b when a + b is bigger than b + a as text. Join, and turn "000" into "0".

from functools import cmp_to_key


def compare(a, b):
    if a + b > b + a:
        return -1
    if a + b < b + a:
        return 1
    return 0


def largest_number(nums):
    words = [str(n) for n in nums]
    words.sort(key=cmp_to_key(compare))
    result = "".join(words)
    if result[0] == "0":
        return "0"
    return result


if __name__ == "__main__":
    results = []
    results.append(check("977. Squares of a Sorted Array", [('sorted_squares([-4, -1, 0, 3, 10])', [0, 1, 9, 16, 100]), ('sorted_squares([-7, -3, 2, 3, 11])', [4, 9, 9, 49, 121])]))
    results.append(check("867. Transpose Matrix", [('transpose([[1, 2, 3], [4, 5, 6], [7, 8, 9]])', [[1, 4, 7], [2, 5, 8], [3, 6, 9]]), ('transpose([[1, 2, 3], [4, 5, 6]])', [[1, 4], [2, 5], [3, 6]])]))
    results.append(check("1572. Matrix Diagonal Sum", [('diagonal_sum([[1, 2, 3], [4, 5, 6], [7, 8, 9]])', 25), ('diagonal_sum([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]])', 8), ('diagonal_sum([[5]])', 5)]))
    results.append(check("2942. Find Words Containing Character", [('find_words_containing(["leet", "code"], "e")', [0, 1]), ('find_words_containing(["abc", "bcd", "aaaa", "cbc"], "a")', [0, 2]), ('find_words_containing(["abc"], "z")', [])]))
    results.append(check("1748. Sum of Unique Elements", [('sum_of_unique([1, 2, 3, 2])', 4), ('sum_of_unique([1, 1, 1, 1, 1])', 0), ('sum_of_unique([1, 2, 3, 4, 5])', 15)]))
    results.append(check("1913. Maximum Product Difference Between Two Pairs", [('max_product_difference([5, 6, 2, 7, 4])', 34), ('max_product_difference([4, 2, 5, 9, 7, 4, 8])', 64)]))
    results.append(check("1636. Sort Array by Increasing Frequency", [('frequency_sort([1, 1, 2, 2, 2, 3])', [3, 1, 1, 2, 2, 2]), ('frequency_sort([2, 3, 1, 3, 2])', [1, 3, 3, 2, 2]), ('frequency_sort([-1, 1, -6, 4, 5, -6, 1, 4, 1])', [5, -1, 4, 4, -6, -6, 1, 1, 1])]))
    results.append(check("451. Sort Characters By Frequency", [('frequency_sort_text("tree")', 'eert'), ('frequency_sort_text("cccaaa")', 'aaaccc'), ('frequency_sort_text("Aabb")', 'bbAa')]))
    results.append(check("791. Custom Sort String", [('custom_sort_string("cba", "abcd")', 'cbad'), ('custom_sort_string("bcafg", "abcd")', 'bcad')]))
    results.append(check("179. Largest Number", [('largest_number([10, 2])', '210'), ('largest_number([3, 30, 34, 5, 9])', '9534330'), ('largest_number([0, 0])', '0')]))
    if all(results):
        print("Every solution passes its tests.")
