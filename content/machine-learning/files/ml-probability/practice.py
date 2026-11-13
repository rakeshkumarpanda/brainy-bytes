# 2.3 Probability and statistics for ML
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


# ================================================================== task 1: Bayes rule for a test result
# Write posterior(prior, sensitivity, false_positive) that returns P(sick | positive) rounded to 3
# decimals. prior is P(sick), sensitivity is P(positive | sick) and false_positive is P(positive |
# healthy).
# Hint: The top is sensitivity × prior. The bottom adds the false positives: false_positive × (1 −
# prior).

def posterior(prior, sensitivity, false_positive):
    # your code here
    pass


# ================================================================== task 2: Mean and standard deviation by hand
# Write mean_std(nums) that returns a list [mean, std], both rounded to 2 decimals. Use the
# population standard deviation (divide by n). Do not use numpy or statistics.
# Hint: First find the mean. Then average the squared distances from it and take the square root.

def mean_std(nums):
    # your code here
    pass


# ================================================================== task 3: Log loss of some predictions
# Write binary_log_loss(labels, probs). labels are 0 or 1 and probs are the predicted chances of 1.
# Return the average of −[y ln p + (1 − y) ln(1 − p)], rounded to 4 decimals. Use math.log.
# Hint: For a 1 label add −ln p. For a 0 label add −ln(1 − p). Divide by the count.

import math


def binary_log_loss(labels, probs):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Bayes rule for a test result", [('posterior(0.01, 0.95, 0.05)', 0.161), ('posterior(0.5, 0.9, 0.1)', 0.9), ('posterior(0.02, 0.9, 0.05)', 0.269)]))
    results.append(check("Task 2: Mean and standard deviation by hand", [('mean_std([2, 4, 6])', [4.0, 1.63]), ('mean_std([5, 5, 5])', [5.0, 0.0]), ('mean_std([1, 2, 3, 4])', [2.5, 1.12])]))
    results.append(check("Task 3: Log loss of some predictions", [('binary_log_loss([1, 0, 1, 1], [0.9, 0.2, 0.6, 0.8])', 0.2656), ('binary_log_loss([1], [0.5])', 0.6931), ('binary_log_loss([0, 1], [0.1, 0.9])', 0.1054)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
