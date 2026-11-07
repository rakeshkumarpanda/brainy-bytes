# 1.2 Variables, values, types and numeral systems
# Practice tasks. Fill in each function, then run this file.
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


# ================================================================== task 1: Describe a value
# Write describe(value) that returns a text like "42 is an int". Use type(value).__name__ for the
# type name and repr(value) for the value.
# Hint: Pick "an" when the type name starts with a vowel (int), otherwise "a".

def describe(value):
    # your code here
    pass


# ================================================================== task 2: Convert to any base by hand
# Write to_base(n, base) for n ≥ 0 and base from 2 to 16. Return the digits as text without a
# prefix, using 0 to 9 and lower case a to f. Do not use bin(), oct(), hex() or format().
# Hint: Repeat: take n % base as the next digit (on the left), then n = n // base.

def to_base(n, base):
    # your code here
    pass


# ================================================================== task 3: Read a typed amount
# Write read_amount(text). The text may have spaces around it and commas between thousands, for
# example " 1,500.75 ". Return it as a float rounded to 2 places. If the text is not a number,
# return None instead of crashing.
# Hint: strip() removes spaces, replace(",", "") removes commas, and try/except ValueError catches
# bad text.

def read_amount(text):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Describe a value", [('describe(42)', '42 is an int'), ('describe(3.5)', '3.5 is a float'), ('describe("hi")', "'hi' is a str"), ('describe(None)', 'None is a NoneType'), ('describe(True)', 'True is a bool')]))
    results.append(check("Task 2: Convert to any base by hand", [('to_base(156, 2)', '10011100'), ('to_base(255, 16)', 'ff'), ('to_base(493, 8)', '755'), ('to_base(0, 2)', '0'), ('to_base(100, 7)', '202')]))
    results.append(check("Task 3: Read a typed amount", [('read_amount(" 1,500.75 ")', 1500.75), ('read_amount("42")', 42.0), ('read_amount("abc")', None), ('read_amount("2,000,000")', 2000000.0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
