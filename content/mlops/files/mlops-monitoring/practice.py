# 3.2 Monitoring and drift
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
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


# ================================================================== task 1: PSI from bin shares
# Write psi_bins(p, q) for two lists of bin shares (training p, live q). Replace any share below
# 0.0001 with 0.0001, then return the sum of (q − p) · ln(q / p), rounded to 4 decimals.
# Hint: Clip each share, then add one term per bin.

def psi_bins(p, q):
    # your code here
    pass


# ================================================================== task 2: A nearest rank percentile
# Write percentile(values, pct) using the nearest rank method: sort the values and return the one at
# rank ceil(pct / 100 × n), counting ranks from 1.
# Hint: Sort, compute the rank with ceil, and index from 0.

def percentile(values, pct):
    # your code here
    pass


# ================================================================== task 3: Alert only on sustained drift
# Write sustained_alert(values, threshold, k) that returns True when at least k values in a row are
# at or above threshold.
# Hint: Count the current streak of bad values and reset it on a good one.

def sustained_alert(values, threshold, k):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: PSI from bin shares", [('psi_bins([0.5, 0.5], [0.7, 0.3])', 0.1695), ('psi_bins([0.1, 0.9], [0.1, 0.9])', 0.0), ('psi_bins([0.5, 0.5], [1.0, 0.0])', 4.6043)]))
    results.append(check("Task 2: A nearest rank percentile", [('percentile([20, 18, 300, 19, 21], 50)', 20), ('percentile(list(range(1, 101)), 99)', 99), ('percentile([5], 95)', 5), ('percentile([3, 1, 2, 4], 100)', 4)]))
    results.append(check("Task 3: Alert only on sustained drift", [('sustained_alert([0.1, 0.3, 0.3, 0.3, 0.1], 0.25, 3)', True), ('sustained_alert([0.3, 0.1, 0.3, 0.1, 0.3], 0.25, 2)', False), ('sustained_alert([], 0.25, 1)', False), ('sustained_alert([0.25], 0.25, 1)', True)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
