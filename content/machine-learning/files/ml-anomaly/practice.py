# 3.1 Anomaly detection
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


# ================================================================== task 1: Robust scores
# Write robust_scores(values) that returns (x − median) / (1.4826 × MAD) for every value, rounded to
# 2 decimals, where MAD is the median of |x − median|. Use statistics.median.
# Hint: Find the median, then the median of the absolute deviations, then scale.

import statistics


def robust_scores(values):
    # your code here
    pass


# ================================================================== task 2: IQR outliers
# Write iqr_outliers(values) that returns the sorted values below Q1 − 1.5 IQR or above Q3 + 1.5
# IQR. Compute quartiles by linear interpolation on the sorted values, as numpy does: the p-th
# quantile sits at position p × (n − 1).
# Hint: Sort, interpolate the quartiles, then compare with the fences.

def iqr_outliers(values):
    # your code here
    pass


# ================================================================== task 3: Local outlier factor in one dimension
# Write lof_1d(values, k, i) that returns the LOF of values[i], rounded to 3 decimals. Neighbours
# are the k closest other values. k-distance(o) is the distance to o’s k-th neighbour, reach(p, o) =
# max(k-distance(o), |p − o|), lrd(p) = 1 / mean reach(p, o) over p’s neighbours, and LOF(p) = mean
# lrd(o) over p’s neighbours divided by lrd(p).
# Hint: Build every point’s neighbours and k-distance first, then lrd, then the ratio.

def lof_1d(values, k, i):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Robust scores", [('robust_scores([1, 2, 3, 4, 100])', [-1.35, -0.67, 0.0, 0.67, 65.43]), ('robust_scores([10, 12, 14])', [-0.67, 0.0, 0.67])]))
    results.append(check("Task 2: IQR outliers", [('iqr_outliers([1, 2, 3, 4, 5, 6, 7, 8, 9, 100])', [100]), ('iqr_outliers([10, 10, 10, 10])', []), ('iqr_outliers([-50, 1, 2, 3, 4])', [-50])]))
    results.append(check("Task 3: Local outlier factor in one dimension", [('lof_1d([1, 2, 4.4, 7, 15], 2, 4)', 2.48), ('lof_1d([1, 2, 4.4, 7, 15], 2, 1)', 0.923), ('lof_1d([0, 1, 3, 6, 10, 30], 3, 5)', 3.998)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
