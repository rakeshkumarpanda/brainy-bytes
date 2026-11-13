# 3.1 Decision trees: a chain of yes or no questions
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


# ================================================================== task 1: Gini impurity
# Write gini(labels) for a list of class labels. Return 1 − Σpk2, rounded to 4 decimals, and 0.0 for
# an empty list.
# Why it works: Three equal classes give 1 − 3 × (1/3)2 = 0.667.

def gini(labels):
    if not labels:
        return 0.0
    counts = {}
    for c in labels:
        counts[c] = counts.get(c, 0) + 1
    total = 0.0
    for k in counts.values():
        total = total + (k / len(labels)) ** 2
    return round(1 - total, 4)


# ================================================================== task 2: Entropy in bits
# Write entropy(labels) that returns −Σpk log2 pk, rounded to 4 decimals.
# Why it works: A pure group has entropy 0 and a 50/50 group 1 bit.

import math


def entropy(labels):
    counts = {}
    for c in labels:
        counts[c] = counts.get(c, 0) + 1
    h = 0.0
    for k in counts.values():
        p = k / len(labels)
        h = h - p * math.log2(p)
    return round(h, 4) + 0.0


# ================================================================== task 3: The best cut on one feature
# Write best_cut(xs, ys). xs are numbers, ys are their class labels. Try the midpoint between every
# pair of neighbouring distinct sorted values. Return the cut with the lowest weighted Gini impurity
# (left is x < cut). If two cuts tie, return the smaller one.
# Why it works: The first test is the chapter’s hours studied example. The third shows the values do
# not need to be sorted.

def impurity(labels):
    if not labels:
        return 0.0
    counts = {}
    for c in labels:
        counts[c] = counts.get(c, 0) + 1
    return 1 - sum((k / len(labels)) ** 2 for k in counts.values())


def best_cut(xs, ys):
    values = sorted(set(xs))
    best = None
    best_score = None
    for i in range(1, len(values)):
        cut = (values[i - 1] + values[i]) / 2
        left = [ys[j] for j in range(len(xs)) if xs[j] < cut]
        right = [ys[j] for j in range(len(xs)) if xs[j] >= cut]
        score = (len(left) * impurity(left) + len(right) * impurity(right)) / len(xs)
        if best_score is None or score < best_score - 1e-12:
            best = cut
            best_score = score
    return best


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Gini impurity", [('gini(["a", "a", "b", "b"])', 0.5), ('gini(["a", "a", "a"])', 0.0), ('gini(["a", "b", "c"])', 0.6667)]))
    results.append(check("Task 2: Entropy in bits", [('entropy(["y", "y", "n", "n"])', 1.0), ('entropy(["y", "y", "y", "n"])', 0.8113), ('entropy(["a", "a"])', 0.0)]))
    results.append(check("Task 3: The best cut on one feature", [('best_cut([1, 2, 3, 4, 5, 6, 7, 8], ["n", "n", "n", "n", "y", "n", "y", "y"])', 4.5), ('best_cut([1, 2, 6, 7], ["a", "a", "b", "b"])', 4.0), ('best_cut([3, 1, 2], ["b", "a", "b"])', 1.5)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
