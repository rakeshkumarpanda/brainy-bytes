# 1.4 Input, output and formatting text
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


# ================================================================== 412. Fizz Buzz (Easy)
# https://leetcode.com/problems/fizz-buzz/
# Pattern: Modulo and building text
# Idea: Check divisible by 15 first, then 3, then 5. Build a list of texts.

def fizz_buzz(n):
    answer = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            answer.append("FizzBuzz")
        elif i % 3 == 0:
            answer.append("Fizz")
        elif i % 5 == 0:
            answer.append("Buzz")
        else:
            answer.append(str(i))
    return answer


# ================================================================== 709. To Lower Case (Easy)
# https://leetcode.com/problems/to-lower-case/
# Pattern: Character codes
# Idea: Without lower(): for "A" to "Z" add 32 to the character code with ord() and chr().

def to_lower_case(s):
    result = ""
    for ch in s:
        if "A" <= ch <= "Z":
            result = result + chr(ord(ch) + 32)
        else:
            result = result + ch
    return result


# ================================================================== 1678. Goal Parser Interpretation (Easy)
# https://leetcode.com/problems/goal-parser-interpretation/
# Pattern: Text replace
# Idea: Replace "()" with "o" and then "(al)" with "al".

def interpret(command):
    return command.replace("()", "o").replace("(al)", "al")


# ================================================================== 2864. Maximum Odd Binary Number (Easy)
# https://leetcode.com/problems/maximum-odd-binary-number/
# Pattern: Counting and building text
# Idea: Keep one "1" for the end (odd). Put all other 1s at the front, then the 0s.

def maximum_odd_binary_number(s):
    ones = s.count("1")
    zeros = len(s) - ones
    return "1" * (ones - 1) + "0" * zeros + "1"


if __name__ == "__main__":
    results = []
    results.append(check("412. Fizz Buzz", [('fizz_buzz(5)', ['1', '2', 'Fizz', '4', 'Buzz']), ('fizz_buzz(15)[-1]', 'FizzBuzz')]))
    results.append(check("709. To Lower Case", [('to_lower_case("Hello")', 'hello'), ('to_lower_case("LOVELY")', 'lovely')]))
    results.append(check("1678. Goal Parser Interpretation", [('interpret("G()(al)")', 'Goal'), ('interpret("G()()()()(al)")', 'Gooooal')]))
    results.append(check("2864. Maximum Odd Binary Number", [('maximum_odd_binary_number("010")', '001'), ('maximum_odd_binary_number("0101")', '1001')]))
    if all(results):
        print("Every solution passes its tests.")
