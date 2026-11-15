# 1.1 Machine learning for security
# Model solutions. Try practice.py first.
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
# Why it works: F1 treats a missed attack and a false alarm as equally bad. When they cost different
# amounts, compare models on cost instead, or use an F beta score.

def f1_score(tp, fp, fn):
    if tp == 0:
        return 0.0
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    return round(2 * precision * recall / (precision + recall), 4)


# ================================================================== task 2: Robust outliers with the median and MAD
# Write robust_outliers(values) that returns the list of indices (from 0) whose modified z score
# 0.6745 (x − median) / MAD has an absolute value above 3.5. Use statistics.median.
# Why it works: If more than half the values are identical the MAD is 0 and the score is undefined.
# Real code then falls back to the mean absolute deviation.

import statistics

def robust_outliers(values):
    med = statistics.median(values)
    mad = statistics.median([abs(x - med) for x in values])
    out = []
    for i, x in enumerate(values):
        if abs(0.6745 * (x - med) / mad) > 3.5:
            out.append(i)
    return out


# ================================================================== task 3: Population stability index
# Write psi_value(expected, actual) for two lists of bin shares that returns Σ (a − e) ln(a / e)
# rounded to 4 decimals.
# Why it works: PSI is a symmetric form of the Kullback Leibler divergence: KL(a || e) + KL(e || a).
# Empty bins make it infinite, so real code adds a tiny value to each share.

import math

def psi_value(expected, actual):
    total = 0.0
    for e, a in zip(expected, actual):
        total += (a - e) * math.log(a / e)
    return round(total, 4)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: F1 score from counts", [('f1_score(3, 2, 2)', 0.6), ('f1_score(4, 4, 1)', 0.6154), ('f1_score(0, 5, 5)', 0.0), ('f1_score(10, 0, 0)', 1.0)]))
    results.append(check("Task 2: Robust outliers with the median and MAD", [('robust_outliers([120, 135, 110, 128, 140, 118, 125, 132, 900, 122, 130, 2400, 127, 119])', [8, 11]), ('robust_outliers([10, 11, 9, 10, 12, 10])', []), ('robust_outliers([5, 6, 5, 7, 6, 50, 5, 6])', [5])]))
    results.append(check("Task 3: Population stability index", [('psi_value([0.10, 0.30, 0.35, 0.20, 0.05], [0.05, 0.15, 0.30, 0.30, 0.20])', 0.3948), ('psi_value([0.5, 0.5], [0.5, 0.5])', 0.0), ('psi_value([0.25, 0.75], [0.5, 0.5])', 0.2747)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
