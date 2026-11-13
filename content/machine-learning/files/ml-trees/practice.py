# 3.1 Decision trees: a chain of yes or no questions
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


# ================================================================== task 1: Gini impurity
# Write gini(labels) for a list of class labels. Return 1 − Σpk2, rounded to 4 decimals, and 0.0 for
# an empty list.
# Hint: Count each class, then subtract the squared shares from 1.

def gini(labels):
    # your code here
    pass


# ================================================================== task 2: Entropy in bits
# Write entropy(labels) that returns −Σpk log2 pk, rounded to 4 decimals.
# Hint: Count, turn counts into shares, add −p log2 p.

import math


def entropy(labels):
    # your code here
    pass


# ================================================================== task 3: The best cut on one feature
# Write best_cut(xs, ys). xs are numbers, ys are their class labels. Try the midpoint between every
# pair of neighbouring distinct sorted values. Return the cut with the lowest weighted Gini impurity
# (left is x < cut). If two cuts tie, return the smaller one.
# Hint: Sort the distinct values, try each midpoint, and keep the lowest weighted Gini.

def best_cut(xs, ys):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Gini impurity", [('gini(["a", "a", "b", "b"])', 0.5), ('gini(["a", "a", "a"])', 0.0), ('gini(["a", "b", "c"])', 0.6667)]))
    results.append(check("Task 2: Entropy in bits", [('entropy(["y", "y", "n", "n"])', 1.0), ('entropy(["y", "y", "y", "n"])', 0.8113), ('entropy(["a", "a"])', 0.0)]))
    results.append(check("Task 3: The best cut on one feature", [('best_cut([1, 2, 3, 4, 5, 6, 7, 8], ["n", "n", "n", "n", "y", "n", "y", "y"])', 4.5), ('best_cut([1, 2, 6, 7], ["a", "a", "b", "b"])', 4.0), ('best_cut([3, 1, 2], ["b", "a", "b"])', 1.5)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
