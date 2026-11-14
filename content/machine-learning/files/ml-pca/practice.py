# 2.1 Principal component analysis (PCA)
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


# ================================================================== task 1: Centre the columns
# Write centre_columns(rows) that subtracts each column’s mean from every value in that column.
# Return the new rows with values rounded to 4 decimals.
# Hint: Compute the mean of every column first, then subtract.

def centre_columns(rows):
    # your code here
    pass


# ================================================================== task 2: A 2 by 2 covariance matrix
# Write covariance_2d(points) for a list of [x, y]. Return [[var x, cov], [cov, var y]] using n − 1
# in the denominator, rounded to 4 decimals.
# Hint: Centre, then average the products of deviations.

def covariance_2d(points):
    # your code here
    pass


# ================================================================== task 3: Share of the first component
# Write pc1_share(cov) for a symmetric 2 by 2 covariance matrix [[a, b], [b, d]]. Use the formula λ
# = (a + d)/2 ± √(((a − d)/2)2 + b2) and return the larger eigenvalue divided by the sum of both,
# rounded to 4 decimals.
# Hint: Use the closed form for the eigenvalues of a symmetric 2 by 2 matrix.

import math


def pc1_share(cov):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Centre the columns", [('centre_columns([[1, 2], [3, 4]])', [[-1.0, -1.0], [1.0, 1.0]]), ('centre_columns([[2, 0], [4, 0], [6, 3]])', [[-2.0, -1.0], [0.0, -1.0], [2.0, 2.0]])]))
    results.append(check("Task 2: A 2 by 2 covariance matrix", [('covariance_2d([[1, 2], [2, 4], [3, 6]])', [[1.0, 2.0], [2.0, 4.0]]), ('covariance_2d([[0, 0], [2, 0]])', [[2.0, 0.0], [0.0, 0.0]])]))
    results.append(check("Task 3: Share of the first component", [('pc1_share([[1, 2], [2, 4]])', 1.0), ('pc1_share([[2, 0], [0, 2]])', 0.5), ('pc1_share([[3, 1], [1, 3]])', 0.6667)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
