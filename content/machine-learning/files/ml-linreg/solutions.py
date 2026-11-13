# 1.1 Linear regression: fit the best straight line
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


# ================================================================== task 1: Fit a simple regression by hand
# Write fit_line(xs, ys) that returns [intercept, slope] of the least squares line, each rounded to
# 3 decimals. Do not use numpy.
# Why it works: LinearRegression().fit(x.reshape(-1, 1), y) returns the same intercept_ and coef_.

def fit_line(xs, ys):
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    top = 0
    bottom = 0
    for x, y in zip(xs, ys):
        top = top + (x - mean_x) * (y - mean_y)
        bottom = bottom + (x - mean_x) ** 2
    slope = top / bottom
    intercept = mean_y - slope * mean_x
    return [round(intercept, 3), round(slope, 3)]


# ================================================================== task 2: Compute R squared
# Write r_squared(y_true, y_pred) that returns 1 − SSE / SST rounded to 4 decimals.
# Why it works: Predicting the mean every time gives exactly 0, as the second test shows.

def r_squared(y_true, y_pred):
    mean = sum(y_true) / len(y_true)
    sse = 0
    sst = 0
    for t, p in zip(y_true, y_pred):
        sse = sse + (t - p) ** 2
        sst = sst + (t - mean) ** 2
    return round(1 - sse / sst, 4)


# ================================================================== task 3: Gradient descent for a line
# Write gd_line(xs, ys, rate, steps). Start at w = 0 and b = 0. Each step, compute the MSE gradients
# (2/n) Σ(ŷ − y)x and (2/n) Σ(ŷ − y), then update both. Return [w, b] rounded to 3 decimals.
# Why it works: Updating w first and then using the new w to compute the b gradient is a different
# (and slightly wrong) algorithm. Always compute every gradient before changing any weight.

def gd_line(xs, ys, rate, steps):
    n = len(xs)
    w = 0.0
    b = 0.0
    for i in range(steps):
        grad_w = 0.0
        grad_b = 0.0
        for x, y in zip(xs, ys):
            error = w * x + b - y
            grad_w = grad_w + 2 * error * x / n
            grad_b = grad_b + 2 * error / n
        w = w - rate * grad_w
        b = b - rate * grad_b
    return [round(w, 3), round(b, 3)]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Fit a simple regression by hand", [('fit_line([1, 2, 3, 4, 5, 6], [52, 55, 61, 64, 70, 72])', [47.533, 4.229]), ('fit_line([1, 2, 3], [2, 4, 5])', [0.667, 1.5]), ('fit_line([0, 1], [1, 3])', [1.0, 2.0])]))
    results.append(check("Task 2: Compute R squared", [('r_squared([3, 5, 7, 9], [2.5, 5.5, 6, 9.5])', 0.9125), ('r_squared([1, 2, 3], [2, 2, 2])', 0.0), ('r_squared([1, 2, 3], [1, 2, 3])', 1.0)]))
    results.append(check("Task 3: Gradient descent for a line", [('gd_line([1, 2], [2, 4], 0.1, 1)', [1.0, 0.6]), ('gd_line([1, 2, 3, 4], [3, 5, 7, 9], 0.05, 2000)', [2.0, 1.0])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
