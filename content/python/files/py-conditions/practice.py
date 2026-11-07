# 2.1 Making decisions: if, elif, else and match
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


# ================================================================== task 1: Cinema ticket price
# Write ticket_price(age, is_student): children under 5 go free (0), people 60 and over pay 100,
# students pay 120, everyone else pays 200. Check in this order.
# Hint: An if, elif, elif, else chain in the order given.

def ticket_price(age, is_student):
    # your code here
    pass


# ================================================================== task 2: Month to season with match
# Write season(month) for month 1 to 12 using match: 12, 1, 2 give "winter", 3 to 5 "spring", 6 to 8
# "summer", 9 to 11 "autumn". Anything else gives "invalid".
# Hint: Use or patterns such as case 12 | 1 | 2:, and case _: at the end.

def season(month):
    # your code here
    pass


# ================================================================== task 3: What kind of triangle
# Write triangle(a, b, c) that returns "invalid" if the sides cannot make a triangle (one side is at
# least the sum of the other two, or a side is not above 0), else "equilateral", "isosceles" or
# "scalene".
# Hint: Check that it is a triangle first, then equilateral before isosceles.

def triangle(a, b, c):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Cinema ticket price", [('ticket_price(3, False)', 0), ('ticket_price(65, True)', 100), ('ticket_price(20, True)', 120), ('ticket_price(30, False)', 200)]))
    results.append(check("Task 2: Month to season with match", [('season(1)', 'winter'), ('season(4)', 'spring'), ('season(7)', 'summer'), ('season(10)', 'autumn'), ('season(13)', 'invalid')]))
    results.append(check("Task 3: What kind of triangle", [('triangle(3, 3, 3)', 'equilateral'), ('triangle(3, 3, 5)', 'isosceles'), ('triangle(3, 4, 5)', 'scalene'), ('triangle(1, 2, 3)', 'invalid'), ('triangle(0, 1, 1)', 'invalid')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
