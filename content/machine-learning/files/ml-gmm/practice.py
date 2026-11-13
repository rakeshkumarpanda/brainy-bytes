# 1.3 Gaussian mixture models and EM
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


# ================================================================== task 1: The bell curve
# Write normal_pdf(x, mean, sd) that returns the normal density exp(−(x − mean)2 / (2 sd2)) / (sd
# √(2π)), rounded to 4 decimals.
# Hint: Translate the formula directly with math.exp, math.sqrt and math.pi.

import math


def normal_pdf(x, mean, sd):
    # your code here
    pass


# ================================================================== task 2: The E step for one value
# Write responsibilities(x, means, sds, weights) for a 1D mixture. Return the list of probabilities
# that each component produced x, each rounded to 4 decimals.
# Hint: Weight times density for each component, then divide by the sum.

import math


def responsibilities(x, means, sds, weights):
    # your code here
    pass


# ================================================================== task 3: The M step for weights and means
# Write m_step(xs, resp). xs is a list of values and resp[i] is the list of responsibilities of
# value i for each component. Return [weights, means], two lists rounded to 4 decimals, where weight
# k = Nk / n and mean k = Σ rik xi / Nk.
# Hint: For each component add up its responsibilities, then take the weighted mean.

def m_step(xs, resp):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The bell curve", [('normal_pdf(0, 0, 1)', 0.3989), ('normal_pdf(1, 0, 1)', 0.242), ('normal_pdf(5, 5, 2)', 0.1995)]))
    results.append(check("Task 2: The E step for one value", [('responsibilities(0, [0, 0], [1, 1], [0.5, 0.5])', [0.5, 0.5]), ('responsibilities(0, [0, 4], [1, 1], [0.5, 0.5])', [0.9997, 0.0003]), ('responsibilities(2, [0, 4], [1, 1], [0.25, 0.75])', [0.25, 0.75])]))
    results.append(check("Task 3: The M step for weights and means", [('m_step([1, 2, 9, 10], [[1, 0], [1, 0], [0, 1], [0, 1]])', [[0.5, 0.5], [1.5, 9.5]]), ('m_step([0, 10], [[0.5, 0.5], [0.5, 0.5]])', [[0.5, 0.5], [5.0, 5.0]]), ('m_step([0, 4], [[0.75, 0.25], [0.25, 0.75]])', [[0.5, 0.5], [1.0, 3.0]])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
