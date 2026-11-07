# 1.1 What a program is and your first Python program
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


# ================================================================== 2235. Add Two Integers (Easy)
# https://leetcode.com/problems/add-two-integers/
# Pattern: Arithmetic
# Idea: Return num1 + num2. The point is to get used to a function that returns a value instead of
# printing it.

def sum_two(num1, num2):
    # LeetCode calls this method sum. We use sum_two so we do not hide the built in sum().
    return num1 + num2


# ================================================================== 2469. Convert the Temperature (Easy)
# https://leetcode.com/problems/convert-the-temperature/
# Pattern: Formula
# Idea: Kelvin = Celsius + 273.15 and Fahrenheit = Celsius × 1.80 + 32.00. Return both in a list.

def convert_temperature(celsius):
    kelvin = celsius + 273.15
    fahrenheit = celsius * 1.80 + 32.00
    return [round(kelvin, 5), round(fahrenheit, 5)]


# ================================================================== 2413. Smallest Even Multiple (Easy)
# https://leetcode.com/problems/smallest-even-multiple/
# Pattern: Arithmetic
# Idea: If n is already even, n itself works. If n is odd, the answer is 2 × n.

def smallest_even_multiple(n):
    if n % 2 == 0:
        return n
    return 2 * n


# ================================================================== 1108. Defanging an IP Address (Easy)
# https://leetcode.com/problems/defanging-an-ip-address/
# Pattern: String replace
# Idea: Replace every dot with [.] using the string method replace().

def defang_ip_address(address):
    return address.replace(".", "[.]")


if __name__ == "__main__":
    results = []
    results.append(check("2235. Add Two Integers", [('sum_two(12, 5)', 17), ('sum_two(-10, 4)', -6)]))
    results.append(check("2469. Convert the Temperature", [('convert_temperature(36.50)', [309.65, 97.7]), ('convert_temperature(122.11)', [395.26, 251.798])]))
    results.append(check("2413. Smallest Even Multiple", [('smallest_even_multiple(5)', 10), ('smallest_even_multiple(6)', 6)]))
    results.append(check("1108. Defanging an IP Address", [('defang_ip_address("1.1.1.1")', '1[.]1[.]1[.]1'), ('defang_ip_address("255.100.50.0")', '255[.]100[.]50[.]0')]))
    if all(results):
        print("Every solution passes its tests.")
