# 2.2 Loops: while, for, range, break and continue
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


# ================================================================== 1480. Running Sum of 1d Array (Easy)
# https://leetcode.com/problems/running-sum-of-1d-array/
# Pattern: Accumulator
# Idea: Keep a total. Each turn add the current number and append the total.

def running_sum(nums):
    result = []
    total = 0
    for x in nums:
        total = total + x
        result.append(total)
    return result


# ================================================================== 9. Palindrome Number (Easy)
# https://leetcode.com/problems/palindrome-number/
# Pattern: Digit loop with % and //
# Idea: Negative numbers are not palindromes. Build the reversed number digit by digit and compare.

def is_palindrome(x):
    if x < 0:
        return False
    original = x
    reversed_number = 0
    while x > 0:
        reversed_number = reversed_number * 10 + x % 10
        x = x // 10
    return reversed_number == original


# ================================================================== 1295. Find Numbers with Even Number of Digits (Easy)
# https://leetcode.com/problems/find-numbers-with-even-number-of-digits/
# Pattern: Counter
# Idea: Count the digits of each number with len(str(n)) and count the even ones.

def find_numbers(nums):
    count = 0
    for n in nums:
        if len(str(n)) % 2 == 0:
            count = count + 1
    return count


# ================================================================== 7. Reverse Integer (Medium)
# https://leetcode.com/problems/reverse-integer/
# Pattern: Digit loop and range check
# Idea: Reverse the absolute value with a digit loop, put the sign back, and return 0 if it leaves
# the 32 bit range.

def reverse(x):
    sign = 1
    if x < 0:
        sign = -1
        x = -x
    result = 0
    while x > 0:
        result = result * 10 + x % 10
        x = x // 10
    result = result * sign
    if result < -(2 ** 31) or result > 2 ** 31 - 1:
        return 0
    return result


# ================================================================== 202. Happy Number (Easy)
# https://leetcode.com/problems/happy-number/
# Pattern: while loop with a seen set
# Idea: Replace n by the sum of the squares of its digits. Stop at 1 (happy) or when a number
# repeats (a cycle).

def is_happy(n):
    seen = set()
    while n != 1:
        if n in seen:
            return False
        seen.add(n)
        total = 0
        while n > 0:
            digit = n % 10
            total = total + digit * digit
            n = n // 10
        n = total
    return True


# ================================================================== 1137. N-th Tribonacci Number (Easy)
# https://leetcode.com/problems/n-th-tribonacci-number/
# Pattern: Loop with three running values
# Idea: Keep the last three numbers a, b, c and move them forward n times.

def tribonacci(n):
    a, b, c = 0, 1, 1
    if n == 0:
        return 0
    for _ in range(n - 2):
        a, b, c = b, c, a + b + c
    return c


if __name__ == "__main__":
    results = []
    results.append(check("1480. Running Sum of 1d Array", [('running_sum([1, 2, 3, 4])', [1, 3, 6, 10]), ('running_sum([3, 1, 2, 10, 1])', [3, 4, 6, 16, 17])]))
    results.append(check("9. Palindrome Number", [('is_palindrome(121)', True), ('is_palindrome(-121)', False), ('is_palindrome(10)', False)]))
    results.append(check("1295. Find Numbers with Even Number of Digits", [('find_numbers([12, 345, 2, 6, 7896])', 2), ('find_numbers([555, 901, 482, 1771])', 1)]))
    results.append(check("7. Reverse Integer", [('reverse(123)', 321), ('reverse(-123)', -321), ('reverse(120)', 21), ('reverse(1534236469)', 0)]))
    results.append(check("202. Happy Number", [('is_happy(19)', True), ('is_happy(2)', False)]))
    results.append(check("1137. N-th Tribonacci Number", [('tribonacci(4)', 4), ('tribonacci(25)', 1389537), ('tribonacci(1)', 1)]))
    if all(results):
        print("Every solution passes its tests.")
