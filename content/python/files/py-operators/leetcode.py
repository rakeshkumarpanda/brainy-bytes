# 1.3 Operators, expressions and the order Python works them out
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


# ================================================================== 1009. Complement of Base 10 Integer (Easy)
# https://leetcode.com/problems/complement-of-base-10-integer/
# Pattern: Bitwise xor with a mask
# Idea: Make a mask of 1s as long as n in binary, (1 << n.bit_length()) - 1, then n ^ mask flips
# every bit. n = 0 gives 1.

def bitwise_complement(n):
    if n == 0:
        return 1
    mask = (1 << n.bit_length()) - 1
    return n ^ mask


# ================================================================== 231. Power of Two (Easy)
# https://leetcode.com/problems/power-of-two/
# Pattern: Bit trick
# Idea: A power of two has exactly one 1 bit, so n & (n - 1) removes it and leaves 0. n must be
# above 0.

def is_power_of_two(n):
    return n > 0 and n & (n - 1) == 0


# ================================================================== 258. Add Digits (Easy)
# https://leetcode.com/problems/add-digits/
# Pattern: Maths (digital root)
# Idea: Without a loop: 0 stays 0, otherwise the answer is 1 + (num - 1) % 9.

def add_digits(num):
    if num == 0:
        return 0
    return 1 + (num - 1) % 9


# ================================================================== 461. Hamming Distance (Easy)
# https://leetcode.com/problems/hamming-distance/
# Pattern: xor then count bits
# Idea: x ^ y has a 1 exactly where the bits differ. Count the 1s.

def hamming_distance(x, y):
    return bin(x ^ y).count("1")


# ================================================================== 29. Divide Two Integers (Medium)
# https://leetcode.com/problems/divide-two-integers/
# Pattern: Shifts and truncation
# Idea: Work with absolute values. Subtract the biggest divisor << k that fits, add 1 << k to the
# answer. LeetCode truncates towards zero and clamps to 32 bits.

def divide(dividend, divisor):
    negative = (dividend < 0) != (divisor < 0)
    a = abs(dividend)
    b = abs(divisor)
    answer = 0
    while a >= b:
        shift = 0
        while a >= (b << (shift + 1)):
            shift = shift + 1
        a = a - (b << shift)
        answer = answer + (1 << shift)
    if negative:
        answer = -answer
    biggest = 2 ** 31 - 1
    smallest = -(2 ** 31)
    if answer > biggest:
        return biggest
    if answer < smallest:
        return smallest
    return answer


if __name__ == "__main__":
    results = []
    results.append(check("1009. Complement of Base 10 Integer", [('bitwise_complement(5)', 2), ('bitwise_complement(7)', 0), ('bitwise_complement(10)', 5), ('bitwise_complement(0)', 1)]))
    results.append(check("231. Power of Two", [('is_power_of_two(1)', True), ('is_power_of_two(16)', True), ('is_power_of_two(3)', False), ('is_power_of_two(0)', False)]))
    results.append(check("258. Add Digits", [('add_digits(38)', 2), ('add_digits(0)', 0), ('add_digits(9)', 9)]))
    results.append(check("461. Hamming Distance", [('hamming_distance(1, 4)', 2), ('hamming_distance(3, 1)', 1)]))
    results.append(check("29. Divide Two Integers", [('divide(10, 3)', 3), ('divide(7, -3)', -2), ('divide(-2147483648, -1)', 2147483647)]))
    if all(results):
        print("Every solution passes its tests.")
