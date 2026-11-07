# 1.2 Extended arguments, closures and decorators
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


# ================================================================== 746. Min Cost Climbing Stairs (Easy)
# https://leetcode.com/problems/min-cost-climbing-stairs/
# Pattern: Top down with @cache
# Idea: best(i) is the cheapest way to stand past the top from step i: cost[i] + min(best(i + 1),
# best(i + 2)). Start from step 0 or 1.

from functools import cache


def min_cost_climbing_stairs(cost):
    @cache
    def best(i):
        if i >= len(cost):
            return 0
        return cost[i] + min(best(i + 1), best(i + 2))
    return min(best(0), best(1))


# ================================================================== 62. Unique Paths (Medium)
# https://leetcode.com/problems/unique-paths/
# Pattern: Paths from a cell, cached
# Idea: paths(r, c) = paths(r + 1, c) + paths(r, c + 1), and 1 on the last row or column.

from functools import cache


def unique_paths(m, n):
    @cache
    def paths(r, c):
        if r == m - 1 or c == n - 1:
            return 1
        return paths(r + 1, c) + paths(r, c + 1)
    return paths(0, 0)


# ================================================================== 64. Minimum Path Sum (Medium)
# https://leetcode.com/problems/minimum-path-sum/
# Pattern: Cheapest from a cell, cached
# Idea: cost(r, c) is the grid value plus the cheaper of moving down or right.

from functools import cache


def min_path_sum(grid):
    rows, cols = len(grid), len(grid[0])

    @cache
    def cost(r, c):
        if r == rows - 1 and c == cols - 1:
            return grid[r][c]
        options = []
        if r + 1 < rows:
            options.append(cost(r + 1, c))
        if c + 1 < cols:
            options.append(cost(r, c + 1))
        return grid[r][c] + min(options)
    return cost(0, 0)


# ================================================================== 91. Decode Ways (Medium)
# https://leetcode.com/problems/decode-ways/
# Pattern: Ways from a position, cached
# Idea: From position i, take one digit (if not 0) or two digits (if 10 to 26) and add the ways for
# the rest.

from functools import cache


def num_decodings(s):
    @cache
    def ways(i):
        if i == len(s):
            return 1
        if s[i] == "0":
            return 0
        total = ways(i + 1)
        if i + 1 < len(s) and 10 <= int(s[i:i + 2]) <= 26:
            total += ways(i + 2)
        return total
    return ways(0)


# ================================================================== 139. Word Break (Medium)
# https://leetcode.com/problems/word-break/
# Pattern: Can the rest be split, cached
# Idea: From position i, try every dictionary word that matches there and ask the same question for
# the rest.

from functools import cache


def word_break(s, wordDict):
    words = set(wordDict)

    @cache
    def can(i):
        if i == len(s):
            return True
        for j in range(i + 1, len(s) + 1):
            if s[i:j] in words and can(j):
                return True
        return False
    return can(0)


# ================================================================== 198. House Robber (Medium)
# https://leetcode.com/problems/house-robber/
# Pattern: Rob or skip, cached
# Idea: best(i) = max(rob house i and jump two, or skip to i + 1).

from functools import cache


def rob(nums):
    @cache
    def best(i):
        if i >= len(nums):
            return 0
        return max(nums[i] + best(i + 2), best(i + 1))
    return best(0)


# ================================================================== 322. Coin Change (Medium)
# https://leetcode.com/problems/coin-change/
# Pattern: Fewest coins for an amount, cached
# Idea: fewest(a) = 1 + the smallest fewest(a - coin). Use infinity for impossible amounts.

from functools import cache


def coin_change(coins, amount):
    @cache
    def fewest(a):
        if a == 0:
            return 0
        best = float("inf")
        for coin in coins:
            if coin <= a:
                best = min(best, 1 + fewest(a - coin))
        return best
    answer = fewest(amount)
    return -1 if answer == float("inf") else answer


# ================================================================== 343. Integer Break (Medium)
# https://leetcode.com/problems/integer-break/
# Pattern: Best split, cached
# Idea: For each first piece k, either keep the rest whole or break it further: max(k * (n - k), k *
# best(n - k)).

from functools import cache


def integer_break(n):
    @cache
    def best(m):
        result = 0
        for k in range(1, m):
            result = max(result, k * (m - k), k * best(m - k))
        return result
    return best(n)


# ================================================================== 96. Unique Binary Search Trees (Medium)
# https://leetcode.com/problems/unique-binary-search-trees/
# Pattern: Catalan numbers, cached
# Idea: Choose each value as the root. The trees on the left and right are independent, so multiply
# their counts.

from functools import cache


def num_trees(n):
    @cache
    def count(k):
        if k <= 1:
            return 1
        total = 0
        for root in range(1, k + 1):
            total += count(root - 1) * count(k - root)
        return total
    return count(n)


# ================================================================== 494. Target Sum (Medium)
# https://leetcode.com/problems/target-sum/
# Pattern: Ways from (index, total), cached
# Idea: At each number add it or subtract it. Count the ways that land exactly on target.

from functools import cache


def find_target_sum_ways(nums, target):
    @cache
    def ways(i, total):
        if i == len(nums):
            return 1 if total == target else 0
        return ways(i + 1, total + nums[i]) + ways(i + 1, total - nums[i])
    return ways(0, 0)


if __name__ == "__main__":
    results = []
    results.append(check("746. Min Cost Climbing Stairs", [('min_cost_climbing_stairs([10, 15, 20])', 15), ('min_cost_climbing_stairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1])', 6)]))
    results.append(check("62. Unique Paths", [('unique_paths(3, 7)', 28), ('unique_paths(3, 2)', 3)]))
    results.append(check("64. Minimum Path Sum", [('min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]])', 7), ('min_path_sum([[1, 2, 3], [4, 5, 6]])', 12)]))
    results.append(check("91. Decode Ways", [('num_decodings("12")', 2), ('num_decodings("226")', 3), ('num_decodings("06")', 0)]))
    results.append(check("139. Word Break", [('word_break("leetcode", ["leet", "code"])', True), ('word_break("applepenapple", ["apple", "pen"])', True), ('word_break("catsandog", ["cats", "dog", "sand", "and", "cat"])', False)]))
    results.append(check("198. House Robber", [('rob([1, 2, 3, 1])', 4), ('rob([2, 7, 9, 3, 1])', 12)]))
    results.append(check("322. Coin Change", [('coin_change([1, 2, 5], 11)', 3), ('coin_change([2], 3)', -1), ('coin_change([1], 0)', 0)]))
    results.append(check("343. Integer Break", [('integer_break(2)', 1), ('integer_break(10)', 36)]))
    results.append(check("96. Unique Binary Search Trees", [('num_trees(3)', 5), ('num_trees(1)', 1), ('num_trees(5)', 42)]))
    results.append(check("494. Target Sum", [('find_target_sum_ways([1, 1, 1, 1, 1], 3)', 5), ('find_target_sum_ways([1], 1)', 1)]))
    if all(results):
        print("Every solution passes its tests.")
