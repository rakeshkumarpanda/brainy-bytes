# 1.1 Linear regression: fit the best straight line
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


# ================================================================== task 1: Fit a simple regression by hand
# Write fit_line(xs, ys) that returns [intercept, slope] of the least squares line, each rounded to
# 3 decimals. Do not use numpy.
# Hint: Compute both means, then the two sums. The slope is their ratio, and the intercept is mean_y
# minus slope times mean_x.

def fit_line(xs, ys):
    # your code here
    pass


# ================================================================== task 2: Compute R squared
# Write r_squared(y_true, y_pred) that returns 1 − SSE / SST rounded to 4 decimals.
# Hint: SSE adds (actual − predicted)2. SST adds (actual − mean)2.

def r_squared(y_true, y_pred):
    # your code here
    pass


# ================================================================== task 3: Gradient descent for a line
# Write gd_line(xs, ys, rate, steps). Start at w = 0 and b = 0. Each step, compute the MSE gradients
# (2/n) Σ(ŷ − y)x and (2/n) Σ(ŷ − y), then update both. Return [w, b] rounded to 3 decimals.
# Hint: Compute both gradients using the old w and b, then update both together.

def gd_line(xs, ys, rate, steps):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Fit a simple regression by hand", [('fit_line([1, 2, 3, 4, 5, 6], [52, 55, 61, 64, 70, 72])', [47.533, 4.229]), ('fit_line([1, 2, 3], [2, 4, 5])', [0.667, 1.5]), ('fit_line([0, 1], [1, 3])', [1.0, 2.0])]))
    results.append(check("Task 2: Compute R squared", [('r_squared([3, 5, 7, 9], [2.5, 5.5, 6, 9.5])', 0.9125), ('r_squared([1, 2, 3], [2, 2, 2])', 0.0), ('r_squared([1, 2, 3], [1, 2, 3])', 1.0)]))
    results.append(check("Task 3: Gradient descent for a line", [('gd_line([1, 2], [2, 4], 0.1, 1)', [1.0, 0.6]), ('gd_line([1, 2, 3, 4], [3, 5, 7, 9], 0.05, 2000)', [2.0, 1.0])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
