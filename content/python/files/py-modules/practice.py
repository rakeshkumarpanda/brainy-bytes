# 5.2 Modules and packages: import, the standard library and pip
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


# ================================================================== task 1: Dice simulation with a fixed seed
# Write roll_counts(n, seed) that seeds random with seed, rolls a die n times with random.randint(1,
# 6), and returns a list of 6 counts: how often each face 1 to 6 came up.
# Hint: Call random.seed(seed) first. counts[face - 1] += 1 for each roll.

import random

def roll_counts(n, seed):
    # your code here
    pass


# ================================================================== task 2: Import a module by its name
# Write load(name) that imports the module whose name is in the text name and returns it, or returns
# None if no such module exists. Use importlib.import_module and catch ModuleNotFoundError.
# Hint: Put return importlib.import_module(name) in try and return None in except
# ModuleNotFoundError.

import importlib

def load(name):
    # your code here
    pass


# ================================================================== task 3: gcd and lcm of a whole list
# Write gcd_lcm(nums) that returns a tuple (gcd of all numbers, lcm of all numbers) using math.gcd
# only. Use lcm(a, b) = a × b // gcd(a, b).
# Hint: Start both with the first number. Fold the rest in one at a time.

import math

def gcd_lcm(nums):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Dice simulation with a fixed seed", [('sum(roll_counts(600, 1))', 600), ('len(roll_counts(10, 2))', 6), ('roll_counts(5, 7) == roll_counts(5, 7)', True), ('roll_counts(0, 3)', [0, 0, 0, 0, 0, 0])]))
    results.append(check("Task 2: Import a module by its name", [('load("math").sqrt(9)', 3.0), ('load("no_such_module_xyz")', None), ('load("json").__name__', 'json'), ('load("os.path") is __import__("os").path', True)]))
    results.append(check("Task 3: gcd and lcm of a whole list", [('gcd_lcm([12, 18, 24])', (6, 72)), ('gcd_lcm([7])', (7, 7)), ('gcd_lcm([4, 6, 10])', (2, 60))]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
