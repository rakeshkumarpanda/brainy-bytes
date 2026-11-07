# 4.2 Scope and recursion: LEGB, closures and the call stack
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


# ================================================================== 509. Fibonacci Number (Easy)
# https://leetcode.com/problems/fibonacci-number/
# Pattern: Recursion with memo or a loop
# Idea: F(0) = 0, F(1) = 1. Use two names a and b and move them forward n times.

def fib(n):
    a = 0
    b = 1
    for _ in range(n):
        a, b = b, a + b
    return a


# ================================================================== 70. Climbing Stairs (Easy)
# https://leetcode.com/problems/climbing-stairs/
# Pattern: Recurrence ways(n) = ways(n − 1) + ways(n − 2)
# Idea: The last step was 1 or 2 stairs. It is Fibonacci shifted by one.

def climb_stairs(n):
    one_before = 1
    two_before = 1
    for _ in range(n - 1):
        one_before, two_before = one_before + two_before, one_before
    return one_before


# ================================================================== 326. Power of Three (Easy)
# https://leetcode.com/problems/power-of-three/
# Pattern: Divide while you can
# Idea: Keep dividing by 3 while n % 3 == 0. A power of three ends at 1.

def is_power_of_three(n):
    if n <= 0:
        return False
    while n % 3 == 0:
        n = n // 3
    return n == 1


# ================================================================== 342. Power of Four (Easy)
# https://leetcode.com/problems/power-of-four/
# Pattern: Recursive halving
# Idea: Base cases 1 (True) and anything not divisible by 4 (False). Otherwise ask the same question
# for n // 4.

def is_power_of_four(n):
    if n == 1:
        return True
    if n <= 0 or n % 4 != 0:
        return False
    return is_power_of_four(n // 4)


# ================================================================== 1688. Count of Matches in Tournament (Easy)
# https://leetcode.com/problems/count-of-matches-in-tournament/
# Pattern: Recursion, then a maths shortcut
# Idea: Each round plays n // 2 matches and n − n // 2 teams go on. In the end every team but one
# loses once: n − 1 matches.

def number_of_matches(n):
    if n == 1:
        return 0
    return n // 2 + number_of_matches(n - n // 2)


# ================================================================== 50. Pow(x, n) (Medium)
# https://leetcode.com/problems/powx-n/
# Pattern: Fast power by halving
# Idea: xn = (xn/2)2, times x when n is odd. For negative n use 1 / x−n.

def my_pow(x, n):
    if n < 0:
        return 1 / my_pow(x, -n)
    if n == 0:
        return 1.0
    half = my_pow(x, n // 2)
    if n % 2 == 0:
        return half * half
    return half * half * x


# ================================================================== 22. Generate Parentheses (Medium)
# https://leetcode.com/problems/generate-parentheses/
# Pattern: Backtracking
# Idea: Build the text one bracket at a time. Add "(" while you have some left, and ")" only when it
# closes an open one.

def generate_parenthesis(n):
    result = []

    def build(text, opened, closed):
        if len(text) == 2 * n:
            result.append(text)
            return
        if opened < n:
            build(text + "(", opened + 1, closed)
        if closed < opened:
            build(text + ")", opened, closed + 1)

    build("", 0, 0)
    return result


# ================================================================== 46. Permutations (Medium)
# https://leetcode.com/problems/permutations/
# Pattern: Backtracking
# Idea: Pick each unused number for the next place, recurse, then undo the choice.

def permute(nums):
    result = []

    def build(current, unused):
        if not unused:
            result.append(current)
            return
        for i in range(len(unused)):
            build(current + [unused[i]], unused[:i] + unused[i + 1:])

    build([], nums)
    return result


# ================================================================== 78. Subsets (Medium)
# https://leetcode.com/problems/subsets/
# Pattern: Take it or leave it
# Idea: For each number, make two recursive calls: one that takes it and one that skips it.

def subsets(nums):
    result = []

    def build(i, current):
        if i == len(nums):
            result.append(current)
            return
        build(i + 1, current)
        build(i + 1, current + [nums[i]])

    build(0, [])
    return result


# ================================================================== 779. K-th Symbol in Grammar (Medium)
# https://leetcode.com/problems/k-th-symbol-in-grammar/
# Pattern: Recursion on the parent
# Idea: Symbol k of row n comes from symbol (k + 1) // 2 of row n − 1. An odd k copies the parent,
# an even k flips it.

def kth_grammar(n, k):
    if n == 1:
        return 0
    parent = kth_grammar(n - 1, (k + 1) // 2)
    if k % 2 == 1:
        return parent
    return 1 - parent


if __name__ == "__main__":
    results = []
    results.append(check("509. Fibonacci Number", [('fib(2)', 1), ('fib(3)', 2), ('fib(4)', 3), ('fib(30)', 832040)]))
    results.append(check("70. Climbing Stairs", [('climb_stairs(2)', 2), ('climb_stairs(3)', 3), ('climb_stairs(10)', 89)]))
    results.append(check("326. Power of Three", [('is_power_of_three(27)', True), ('is_power_of_three(0)', False), ('is_power_of_three(45)', False), ('is_power_of_three(1)', True)]))
    results.append(check("342. Power of Four", [('is_power_of_four(16)', True), ('is_power_of_four(5)', False), ('is_power_of_four(1)', True), ('is_power_of_four(8)', False)]))
    results.append(check("1688. Count of Matches in Tournament", [('number_of_matches(7)', 6), ('number_of_matches(14)', 13), ('number_of_matches(1)', 0)]))
    results.append(check("50. Pow(x, n)", [('round(my_pow(2.0, 10), 5)', 1024.0), ('round(my_pow(2.1, 3), 5)', 9.261), ('round(my_pow(2.0, -2), 5)', 0.25)]))
    results.append(check("22. Generate Parentheses", [('generate_parenthesis(3)', ['((()))', '(()())', '(())()', '()(())', '()()()']), ('generate_parenthesis(1)', ['()'])]))
    results.append(check("46. Permutations", [('permute([1, 2, 3])', [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]), ('permute([0, 1])', [[0, 1], [1, 0]])]))
    results.append(check("78. Subsets", [('sorted(subsets([1, 2, 3]))', [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]), ('subsets([0])', [[], [0]])]))
    results.append(check("779. K-th Symbol in Grammar", [('kth_grammar(1, 1)', 0), ('kth_grammar(2, 1)', 0), ('kth_grammar(2, 2)', 1), ('kth_grammar(4, 5)', 1)]))
    if all(results):
        print("Every solution passes its tests.")
