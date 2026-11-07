# 1.2 Variables, values, types and numeral systems
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


# ================================================================== 1281. Subtract the Product and Sum of Digits of an Integer (Easy)
# https://leetcode.com/problems/subtract-the-product-and-sum-of-digits-of-an-integer/
# Pattern: Digits with % and //
# Idea: Take the last digit with n % 10 and drop it with n // 10 until n is 0. Keep a product and a
# sum.

def subtract_product_and_sum(n):
    product = 1
    total = 0
    while n > 0:
        digit = n % 10
        product = product * digit
        total = total + digit
        n = n // 10
    return product - total


# ================================================================== 191. Number of 1 Bits (Easy)
# https://leetcode.com/problems/number-of-1-bits/
# Pattern: Binary
# Idea: bin(n) gives the binary text. Count the "1" characters in it.

def hamming_weight(n):
    return bin(n).count("1")


# ================================================================== 1290. Convert Binary Number in a Linked List to Integer (Easy)
# https://leetcode.com/problems/convert-binary-number-in-a-linked-list-to-integer/
# Pattern: Place value
# Idea: Start with 0. For each bit, value = value * 2 + bit. Here the list is given as a Python list
# of bits.

def get_decimal_value(bits):
    # On LeetCode the bits come in a linked list. The idea is the same for a plain list.
    value = 0
    for bit in bits:
        value = value * 2 + bit
    return value


# ================================================================== 405. Convert a Number to Hexadecimal (Easy)
# https://leetcode.com/problems/convert-a-number-to-hexadecimal/
# Pattern: Base conversion
# Idea: For negative numbers add 2 ** 32 first (two's complement). Then repeat: digit = num % 16,
# num = num // 16.

def to_hex(num):
    if num == 0:
        return "0"
    if num < 0:
        num = num + 2 ** 32
    digits = "0123456789abcdef"
    result = ""
    while num > 0:
        result = digits[num % 16] + result
        num = num // 16
    return result


# ================================================================== 504. Base 7 (Easy)
# https://leetcode.com/problems/base-7/
# Pattern: Base conversion
# Idea: Same as base 2 but divide by 7. Handle the sign separately.

def convert_to_base7(num):
    if num == 0:
        return "0"
    sign = ""
    if num < 0:
        sign = "-"
        num = -num
    result = ""
    while num > 0:
        result = str(num % 7) + result
        num = num // 7
    return sign + result


if __name__ == "__main__":
    results = []
    results.append(check("1281. Subtract the Product and Sum of Digits of an Integer", [('subtract_product_and_sum(234)', 15), ('subtract_product_and_sum(4421)', 21)]))
    results.append(check("191. Number of 1 Bits", [('hamming_weight(11)', 3), ('hamming_weight(128)', 1), ('hamming_weight(2147483645)', 30)]))
    results.append(check("1290. Convert Binary Number in a Linked List to Integer", [('get_decimal_value([1, 0, 1])', 5), ('get_decimal_value([0])', 0), ('get_decimal_value([1, 1, 1, 1])', 15)]))
    results.append(check("405. Convert a Number to Hexadecimal", [('to_hex(26)', '1a'), ('to_hex(-1)', 'ffffffff'), ('to_hex(0)', '0')]))
    results.append(check("504. Base 7", [('convert_to_base7(100)', '202'), ('convert_to_base7(-7)', '-10')]))
    if all(results):
        print("Every solution passes its tests.")
