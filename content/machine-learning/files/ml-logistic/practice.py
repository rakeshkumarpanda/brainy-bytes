# 2.1 Logistic regression: probabilities for classification
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


# ================================================================== task 1: The sigmoid
# Write sigmoid(z) that returns 1 / (1 + e−z) rounded to 4 decimals. Use math.exp.
# Hint: One line with math.exp(-z).

import math


def sigmoid(z):
    # your code here
    pass


# ================================================================== task 2: Log loss of a set of predictions
# Write log_loss(labels, probs) that returns the average of −[y ln p + (1 − y) ln(1 − p)], rounded
# to 4 decimals.
# Hint: Add the two terms for each example. Only one of them is non zero because y is 0 or 1.

import math


def log_loss(labels, probs):
    # your code here
    pass


# ================================================================== task 3: Softmax
# Write softmax(scores) that returns the list of probabilities ezj / Σ ez, each rounded to 3
# decimals. Subtract the largest score first so very large scores do not overflow.
# Hint: Find the largest score, subtract it from every score, take exp, and divide by the sum.

import math


def softmax(scores):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The sigmoid", [('sigmoid(0)', 0.5), ('sigmoid(2)', 0.8808), ('sigmoid(-3)', 0.0474)]))
    results.append(check("Task 2: Log loss of a set of predictions", [('log_loss([1, 0], [0.9, 0.1])', 0.1054), ('log_loss([1], [0.5])', 0.6931), ('log_loss([0, 0, 1], [0.2, 0.4, 0.7])', 0.3635)]))
    results.append(check("Task 3: Softmax", [('softmax([2.0, 1.0, 0.1])', [0.659, 0.242, 0.099]), ('softmax([1000, 1000])', [0.5, 0.5]), ('softmax([0, 0, 0, 0])', [0.25, 0.25, 0.25, 0.25])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
