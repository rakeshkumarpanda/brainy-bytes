# 2.2 k nearest neighbours: learn from similar examples
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


# ================================================================== task 1: Euclidean distance
# Write euclidean(a, b) for two lists of the same length. Return the distance rounded to 3 decimals.
# Hint: Add up the squared differences, then take the square root.

import math


def euclidean(a, b):
    # your code here
    pass


# ================================================================== task 2: A KNN vote
# Write knn_predict(train, labels, point, k). train is a list of points (lists), labels their
# classes. Return the majority class of the k nearest points by Euclidean distance. On a tie, return
# the class of the single nearest point.
# Hint: Compute every distance, sort, count the labels of the first k, and handle ties with the
# nearest point.

import math


def knn_predict(train, labels, point, k):
    # your code here
    pass


# ================================================================== task 3: KNN regression
# Write knn_regress(xs, ys, x, k) for one feature: return the average y of the k values in xs
# closest to x, rounded to 3 decimals.
# Hint: Sort the (distance, y) pairs and average the first k values of y.

def knn_regress(xs, ys, x, k):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Euclidean distance", [('euclidean([0, 0], [3, 4])', 5.0), ('euclidean([1, 2, 3], [1, 2, 3])', 0.0), ('euclidean([1, 1], [2, 3])', 2.236)]))
    results.append(check("Task 2: A KNN vote", [('knn_predict([[1, 1], [2, 2], [8, 8], [9, 9]], ["A", "A", "B", "B"], [1.5, 1.5], 3)', 'A'), ('knn_predict([[1, 1], [2, 2], [8, 8], [9, 9]], ["A", "A", "B", "B"], [7, 7], 1)', 'B'), ('knn_predict([[0, 0], [10, 10]], ["A", "B"], [4, 4], 2)', 'A')]))
    results.append(check("Task 3: KNN regression", [('knn_regress([1, 2, 3, 10], [10, 12, 17, 50], 2.2, 3)', 13.0), ('knn_regress([0, 5, 10], [0, 50, 100], 9, 1)', 100.0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
