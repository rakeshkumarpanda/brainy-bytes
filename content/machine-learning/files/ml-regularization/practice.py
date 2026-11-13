# 1.2 Polynomial regression and regularisation: ridge, lasso, elastic net
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


# ================================================================== task 1: Polynomial features of a list
# Write poly_features(xs, degree) that returns, for every x, the row [x, x2, ..., xdegree] (no
# constant column).
# Hint: Loop over the values, and inside, over the powers 1 to degree.

def poly_features(xs, degree):
    # your code here
    pass


# ================================================================== task 2: Ridge for one feature
# Write ridge_one(xs, ys, alpha) for a model ŷ = w x with no intercept. Return w = Σxy / (Σx2 +
# alpha), rounded to 3 decimals.
# Hint: Add up x times y and x squared, then divide with alpha added below.

def ridge_one(xs, ys, alpha):
    # your code here
    pass


# ================================================================== task 3: The lasso soft threshold
# Write soft_threshold(rho, alpha): return rho − alpha if rho > alpha, rho + alpha if rho < −alpha,
# and 0 otherwise, rounded to 3 decimals. Then write lasso_weights(rhos, alpha) that applies it to a
# list.
# Hint: Three cases: above alpha, below minus alpha, and in between (which gives 0).

def soft_threshold(rho, alpha):
    # your code here
    pass


def lasso_weights(rhos, alpha):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Polynomial features of a list", [('poly_features([2, 3], 3)', [[2, 4, 8], [3, 9, 27]]), ('poly_features([1, -1], 2)', [[1, 1], [-1, 1]])]))
    results.append(check("Task 2: Ridge for one feature", [('ridge_one([1, 2, 3], [2, 4, 6], 0)', 2.0), ('ridge_one([1, 2, 3], [2, 4, 6], 7)', 1.333), ('ridge_one([1, 1], [5, 5], 2)', 2.5)]))
    results.append(check("Task 3: The lasso soft threshold", [('soft_threshold(0.8, 0.3)', 0.5), ('soft_threshold(-0.2, 0.3)', 0), ('lasso_weights([2.0, -1.0, 0.1, -0.05], 0.5)', [1.5, -0.5, 0, 0])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
