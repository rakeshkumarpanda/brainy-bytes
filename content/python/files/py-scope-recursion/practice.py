# 4.2 Scope and recursion: LEGB, closures and the call stack
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


# ================================================================== task 1: Running total closure
# Write make_adder() that returns a function add(x). Each call add(x) adds x to a running total kept
# inside the closure and returns the new total. Two adders must not share a total.
# Hint: Keep total in make_adder. The inner function needs nonlocal total before it assigns to it.

def make_adder():
    # your code here
    pass


# ================================================================== task 2: Recursive digit sum
# Write digit_sum(n) for n ≥ 0 using recursion, not loops or str(). The sum of the digits of n is
# the last digit plus the digit sum of n // 10.
# Hint: Base case: a one digit number is its own sum. Recursive case: n % 10 + digit_sum(n // 10).

def digit_sum(n):
    # your code here
    pass


# ================================================================== task 3: Flatten a list of any depth
# Write deep_flatten(items) that returns a flat list of every non list value in items, in order,
# however deeply the lists are nested. [1, [2, [3, [4]]], 5] gives [1, 2, 3, 4, 5].
# Hint: Loop over the items. A list item is flattened by a recursive call, any other item is
# appended.

def deep_flatten(items):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Running total closure", [('(lambda a: (a(5), a(10), a(1)))(make_adder())', (5, 15, 16)), ('(lambda a, b: (a(1), b(1), a(1)))(make_adder(), make_adder())', (1, 1, 2))]))
    results.append(check("Task 2: Recursive digit sum", [('digit_sum(0)', 0), ('digit_sum(7)', 7), ('digit_sum(90731)', 20), ('digit_sum(999999)', 54)]))
    results.append(check("Task 3: Flatten a list of any depth", [('deep_flatten([1, [2, [3, [4]]], 5])', [1, 2, 3, 4, 5]), ('deep_flatten([])', []), ('deep_flatten([[[]], ["a"]])', ['a'])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
