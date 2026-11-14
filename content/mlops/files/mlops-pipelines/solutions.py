# 2.1 Pipelines and saving models
# Model solutions. Try practice.py first.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
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


# ================================================================== task 1: Median imputation
# Write impute_median(values) that replaces each None in the list with the median of the other
# values and returns the new list. For an even count, the median is the average of the two middle
# values.
# Why it works: SimpleImputer(strategy='median') does exactly this, and remembers the median from
# fit so new rows get the training median.

def impute_median(values):
    known = sorted(v for v in values if v is not None)
    n = len(known)
    mid = known[n // 2] if n % 2 else (known[n // 2 - 1] + known[n // 2]) / 2
    return [mid if v is None else v for v in values]


# ================================================================== task 2: Scale new values with training statistics
# Write scale_with(train, new) that computes the mean and population standard deviation of train and
# returns the z scores of the values in new, each rounded to 4 decimals.
# Why it works: Using the statistics of the new values instead would make the same customer get a
# different z score depending on who else is in the batch.

import math


def scale_with(train, new):
    mean = sum(train) / len(train)
    std = math.sqrt(sum((v - mean) ** 2 for v in train) / len(train))
    return [round((v - mean) / std + 0.0, 4) for v in new]


# ================================================================== task 3: One hot encoding with unknown categories
# Write one_hot(value, categories) that returns a list with a 1 in the position of value in
# categories and 0 elsewhere. An unknown value gives all zeros.
# Why it works: This is OneHotEncoder with handle_unknown='ignore': the category list comes from
# training, and anything else becomes zeros.

def one_hot(value, categories):
    return [1 if c == value else 0 for c in categories]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Median imputation", [('impute_median([2, 10, None, 30, 18])', [2, 10, 14.0, 30, 18]), ('impute_median([None, 5, 1, 3])', [3, 5, 1, 3]), ('impute_median([7, None])', [7, 7])]))
    results.append(check("Task 2: Scale new values with training statistics", [('scale_with([2, 10, 14, 30, 18], [4, 14.8])', [-1.1662, 0.0]), ('scale_with([0, 2], [1, 3])', [0.0, 2.0])]))
    results.append(check("Task 3: One hot encoding with unknown categories", [("one_hot('plus', ['basic', 'plus', 'premium'])", [0, 1, 0]), ("one_hot('student', ['basic', 'plus', 'premium'])", [0, 0, 0]), ("one_hot('a', ['a'])", [1])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
