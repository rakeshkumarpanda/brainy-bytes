# 1.3 Operators, expressions and the order Python works them out
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


# ================================================================== task 1: Split a bill
# Write split_bill(total, people) with whole numbers. Everyone pays total // people. The remainder
# is shared one rupee each by the first friends. Return a list of what each person pays, the larger
# amounts first.
# Hint: base = total // people and extra = total % people. The first extra people pay base + 1.

def split_bill(total, people):
    # your code here
    pass


# ================================================================== task 2: Leap year
# Write is_leap(year). A year is a leap year if it divides by 4, except years that divide by 100,
# except again years that divide by 400. Use one expression with and, or and not.
# Hint: Divisible means year % n == 0.

def is_leap(year):
    # your code here
    pass


# ================================================================== task 3: Count the 1 bits without bin()
# Write count_bits(n) for n ≥ 0 that returns how many 1s n has in binary, using only & and >> in a
# loop.
# Hint: n & 1 is the last bit. n >> 1 drops it.

def count_bits(n):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Split a bill", [('split_bill(1000, 6)', [167, 167, 167, 167, 166, 166]), ('split_bill(90, 3)', [30, 30, 30]), ('split_bill(5, 2)', [3, 2])]))
    results.append(check("Task 2: Leap year", [('is_leap(2024)', True), ('is_leap(1900)', False), ('is_leap(2000)', True), ('is_leap(2026)', False)]))
    results.append(check("Task 3: Count the 1 bits without bin()", [('count_bits(0)', 0), ('count_bits(13)', 3), ('count_bits(255)', 8), ('count_bits(1024)', 1)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
