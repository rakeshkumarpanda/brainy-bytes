# 4.2 Validation: honest estimates of performance
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


# ================================================================== task 1: K fold indices
# Write kfold_indices(n, k) that returns the validation indices of each fold, in order, without
# shuffling. The first n % k folds get one extra row, as in scikit-learn.
# Why it works: Shuffle the rows first when they are sorted, or the folds will be lopsided.

def kfold_indices(n, k):
    folds = []
    start = 0
    for i in range(k):
        size = n // k + (1 if i < n % k else 0)
        folds.append(list(range(start, start + size)))
        start = start + size
    return folds


# ================================================================== task 2: Mean and spread of fold scores
# Write cv_summary(scores) that returns (mean, standard deviation) of the fold scores, dividing by
# the number of folds, each rounded to 4 decimals.
# Why it works: This matches numpy.std, which divides by k by default.

import math


def cv_summary(scores):
    k = len(scores)
    mean = sum(scores) / k
    var = sum((s - mean) ** 2 for s in scores) / k
    return (round(mean, 4), round(math.sqrt(var), 4))


# ================================================================== task 3: Time series splits
# Write time_splits(n, n_splits) that returns a list of (train_end, val_end) pairs like
# TimeSeriesSplit. Each validation block has n // (n_splits + 1) rows. Split i (from 1) trains on
# rows 0 to train_end and validates on train_end to val_end, with train_end = n − (n_splits − i + 1)
# × block.
# Why it works: The first test matches the program’s TimeSeriesSplit output: train on days 0 to 3,
# validate on days 4 and 5.

def time_splits(n, n_splits):
    block = n // (n_splits + 1)
    out = []
    for i in range(1, n_splits + 1):
        train_end = n - (n_splits - i + 1) * block
        out.append((train_end, train_end + block))
    return out


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: K fold indices", [('kfold_indices(10, 3)', [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]), ('kfold_indices(4, 4)', [[0], [1], [2], [3]]), ('kfold_indices(7, 2)', [[0, 1, 2, 3], [4, 5, 6]])]))
    results.append(check("Task 2: Mean and spread of fold scores", [('cv_summary([0.9, 0.8, 0.85, 0.95, 0.9])', (0.88, 0.051)), ('cv_summary([1.0, 1.0])', (1.0, 0.0)), ('cv_summary([0.5, 0.7])', (0.6, 0.1))]))
    results.append(check("Task 3: Time series splits", [('time_splits(12, 4)', [(4, 6), (6, 8), (8, 10), (10, 12)]), ('time_splits(10, 4)', [(2, 4), (4, 6), (6, 8), (8, 10)]), ('time_splits(6, 2)', [(2, 4), (4, 6)])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
