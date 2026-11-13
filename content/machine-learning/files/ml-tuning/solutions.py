# 4.3 Tuning and calibration
# Model solutions. Try practice.py first.
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


# ================================================================== task 1: Size of a grid
# Write grid_size(param_grid) where param_grid maps each hyperparameter name to a list of values.
# Return the number of combinations.
# Why it works: An empty grid has one combination: the defaults.

def grid_size(param_grid):
    total = 1
    for values in param_grid.values():
        total = total * len(values)
    return total


# ================================================================== task 2: Platt scaling
# Write platt(p, a, b) that returns sigmoid(a × logit(p) + b), where logit(p) = ln(p / (1 − p)) and
# sigmoid(t) = 1 / (1 + e−t), rounded to 4 decimals.
# Why it works: With a = 1 and b = 0 the probability is unchanged. With a < 1 it moves towards 0.5,
# softening an overconfident model.

import math


def platt(p, a, b):
    t = a * math.log(p / (1 - p)) + b
    return round(1 / (1 + math.exp(-t)), 4)


# ================================================================== task 3: Expected calibration error
# Write ece(pred, labels, n_bins). Put each prediction in bin min(int(p × n_bins), n_bins − 1). For
# each non empty bin take |mean prediction − mean label| weighted by the share of examples in the
# bin. Return the sum rounded to 4 decimals.
# Why it works: The second test is perfectly calibrated: 0.8 predicted and 4 of 5 positive.

def ece(pred, labels, n_bins):
    bins = {}
    for p, y in zip(pred, labels):
        b = min(int(p * n_bins), n_bins - 1)
        bins.setdefault(b, []).append((p, y))
    total = 0.0
    for items in bins.values():
        mean_p = sum(p for p, _ in items) / len(items)
        mean_y = sum(y for _, y in items) / len(items)
        total = total + len(items) / len(pred) * abs(mean_p - mean_y)
    return round(total, 4)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Size of a grid", [('grid_size({"C": [0.1, 1, 10, 100], "gamma": [0.001, 0.01, 0.1]})', 12), ('grid_size({"max_depth": [2, 4, 8]})', 3), ('grid_size({})', 1)]))
    results.append(check("Task 2: Platt scaling", [('platt(0.9, 0.5, 0)', 0.75), ('platt(0.5, 2, 0)', 0.5), ('platt(0.2, 1, 0)', 0.2)]))
    results.append(check("Task 3: Expected calibration error", [('ece([0.9, 0.9, 0.1, 0.1], [1, 0, 0, 0], 2)', 0.25), ('ece([0.8, 0.8, 0.8, 0.8, 0.8], [1, 1, 1, 1, 0], 5)', 0.0), ('ece([0.25, 0.75], [0, 1], 2)', 0.25)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
