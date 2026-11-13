# 2.4 Support vector machines: the widest street
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn


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


# ================================================================== task 1: Hinge loss
# Write hinge(y, score) where y is +1 or −1. Return max(0, 1 − y × score), rounded to 4 decimals.
# Hint: One line with max.

def hinge(y, score):
    # your code here
    pass


# ================================================================== task 2: Margin width from w
# Write margin_width(w) where w is a list of numbers. Return 2 / |w|, rounded to 4 decimals, where
# |w| is the square root of the sum of squares.
# Hint: Compute the length of w, then divide 2 by it.

import math


def margin_width(w):
    # your code here
    pass


# ================================================================== task 3: RBF kernel value
# Write rbf(x, z, gamma) that returns exp(−gamma × |x − z|2) for two lists of the same length,
# rounded to 4 decimals.
# Hint: Add up the squared differences, multiply by −gamma and take exp.

import math


def rbf(x, z, gamma):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Hinge loss", [('hinge(1, 0.3)', 0.7), ('hinge(-1, 0.5)', 1.5), ('hinge(1, 2)', 0.0)]))
    results.append(check("Task 2: Margin width from w", [('margin_width([3, 4])', 0.4), ('margin_width([0.4, 0.4])', 3.5355), ('margin_width([1, 0, 0])', 2.0)]))
    results.append(check("Task 3: RBF kernel value", [('rbf([0, 0], [1, 1], 0.5)', 0.3679), ('rbf([1, 2], [1, 2], 3)', 1.0), ('rbf([0], [3], 0.1)', 0.4066)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
