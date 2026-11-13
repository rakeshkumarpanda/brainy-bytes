# 2.3 Probability and statistics for ML
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


# ================================================================== task 1: Bayes rule for a test result
# Write posterior(prior, sensitivity, false_positive) that returns P(sick | positive) rounded to 3
# decimals. prior is P(sick), sensitivity is P(positive | sick) and false_positive is P(positive |
# healthy).
# Why it works: The bottom line is the total probability of a positive test. Dividing by it makes
# P(sick | +) and P(healthy | +) add up to 1.

def posterior(prior, sensitivity, false_positive):
    top = sensitivity * prior
    evidence = top + false_positive * (1 - prior)
    return round(top / evidence, 3)


# ================================================================== task 2: Mean and standard deviation by hand
# Write mean_std(nums) that returns a list [mean, std], both rounded to 2 decimals. Use the
# population standard deviation (divide by n). Do not use numpy or statistics.
# Why it works: For the sample standard deviation you would divide by n − 1 instead. That is what
# pandas does by default.

def mean_std(nums):
    n = len(nums)
    mean = sum(nums) / n
    total = 0
    for x in nums:
        total = total + (x - mean) ** 2
    std = (total / n) ** 0.5
    return [round(mean, 2), round(std, 2)]


# ================================================================== task 3: Log loss of some predictions
# Write binary_log_loss(labels, probs). labels are 0 or 1 and probs are the predicted chances of 1.
# Return the average of −[y ln p + (1 − y) ln(1 − p)], rounded to 4 decimals. Use math.log.
# Why it works: This is exactly what sklearn.metrics.log_loss computes. It is the negative log
# likelihood of the labels under the model.

import math


def binary_log_loss(labels, probs):
    total = 0
    for y, p in zip(labels, probs):
        if y == 1:
            total = total - math.log(p)
        else:
            total = total - math.log(1 - p)
    return round(total / len(labels), 4)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Bayes rule for a test result", [('posterior(0.01, 0.95, 0.05)', 0.161), ('posterior(0.5, 0.9, 0.1)', 0.9), ('posterior(0.02, 0.9, 0.05)', 0.269)]))
    results.append(check("Task 2: Mean and standard deviation by hand", [('mean_std([2, 4, 6])', [4.0, 1.63]), ('mean_std([5, 5, 5])', [5.0, 0.0]), ('mean_std([1, 2, 3, 4])', [2.5, 1.12])]))
    results.append(check("Task 3: Log loss of some predictions", [('binary_log_loss([1, 0, 1, 1], [0.9, 0.2, 0.6, 0.8])', 0.2656), ('binary_log_loss([1], [0.5])', 0.6931), ('binary_log_loss([0, 1], [0.1, 0.9])', 0.1054)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
