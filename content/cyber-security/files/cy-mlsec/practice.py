# 1.1 Machine learning for security
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.


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


# ================================================================== task 1: F1 score from counts
# Write f1_score(tp, fp, fn) that returns the F1 score rounded to 4 decimals. Return 0.0 when there
# are no true positives.
# Hint: Compute precision and recall first, then the harmonic mean.

def f1_score(tp, fp, fn):
    # your code here
    pass


# ================================================================== task 2: Robust outliers with the median and MAD
# Write robust_outliers(values) that returns the list of indices (from 0) whose modified z score
# 0.6745 (x − median) / MAD has an absolute value above 3.5. Use statistics.median.
# Hint: Find the median, then the median of the distances from it, then score each value.

import statistics

def robust_outliers(values):
    # your code here
    pass


# ================================================================== task 3: Population stability index
# Write psi_value(expected, actual) for two lists of bin shares that returns Σ (a − e) ln(a / e)
# rounded to 4 decimals.
# Hint: Loop over the bins together with zip and add each term.

import math

def psi_value(expected, actual):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: F1 score from counts", [('f1_score(3, 2, 2)', 0.6), ('f1_score(4, 4, 1)', 0.6154), ('f1_score(0, 5, 5)', 0.0), ('f1_score(10, 0, 0)', 1.0)]))
    results.append(check("Task 2: Robust outliers with the median and MAD", [('robust_outliers([120, 135, 110, 128, 140, 118, 125, 132, 900, 122, 130, 2400, 127, 119])', [8, 11]), ('robust_outliers([10, 11, 9, 10, 12, 10])', []), ('robust_outliers([5, 6, 5, 7, 6, 50, 5, 6])', [5])]))
    results.append(check("Task 3: Population stability index", [('psi_value([0.10, 0.30, 0.35, 0.20, 0.05], [0.05, 0.15, 0.30, 0.30, 0.20])', 0.3948), ('psi_value([0.5, 0.5], [0.5, 0.5])', 0.0), ('psi_value([0.25, 0.75], [0.5, 0.5])', 0.2747)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
