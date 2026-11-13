# 1.1 What machine learning is: learning from examples
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


# ================================================================== task 1: Mean squared error by hand
# Write mean_squared_error(y_true, y_pred) that returns the average of the squared differences
# between two lists of the same length.
# Why it works: This is exactly what sklearn.metrics.mean_squared_error does. Squaring keeps every
# gap positive and punishes big mistakes most.

def mean_squared_error(y_true, y_pred):
    total = 0
    for t, p in zip(y_true, y_pred):
        total = total + (t - p) ** 2
    return total / len(y_true)


# ================================================================== task 2: Accuracy by hand
# Write accuracy(y_true, y_pred) that returns the share of positions where the two lists hold the
# same label, as a number between 0 and 1.
# Why it works: Accuracy is easy to read but can mislead when one class is rare. The Supervised
# section shows precision and recall for that case.

def accuracy(y_true, y_pred):
    right = 0
    for t, p in zip(y_true, y_pred):
        if t == p:
            right = right + 1
    return right / len(y_true)


# ================================================================== task 3: A baseline model: always predict the most common label
# Write most_common_label(labels) that returns the label that appears most often in the training
# labels. When two labels tie, return the one that appears first in the list. This "majority class"
# model is the first baseline every project should beat.
# Why it works: If 95 of 100 emails are not spam, this model already gets 95% accuracy without
# learning anything. Any real model must beat it, which is why you always compute a baseline first.

def most_common_label(labels):
    counts = {}
    order = []
    for label in labels:
        if label not in counts:
            counts[label] = 0
            order.append(label)
        counts[label] = counts[label] + 1
    best = order[0]
    for label in order:
        if counts[label] > counts[best]:
            best = label
    return best


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Mean squared error by hand", [('mean_squared_error([10, 20, 30], [10, 20, 30])', 0.0), ('mean_squared_error([3, 7], [5, 4])', 6.5), ('mean_squared_error([1], [4])', 9.0)]))
    results.append(check("Task 2: Accuracy by hand", [('accuracy(["a", "b", "a"], ["a", "b", "b"])', 0.6666666666666666), ('accuracy([1, 1, 0, 0], [1, 1, 0, 0])', 1.0), ('accuracy([1, 0], [0, 1])', 0.0)]))
    results.append(check("Task 3: A baseline model: always predict the most common label", [('most_common_label(["ham", "spam", "ham"])', 'ham'), ('most_common_label([1, 0, 0, 1])', 1), ('most_common_label(["cat"])', 'cat')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
