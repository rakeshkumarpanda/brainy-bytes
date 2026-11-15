# 2.3 Differential privacy
# Model solutions. Try practice.py first.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.


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


# ================================================================== task 1: Laplace noise scale
# Write laplace_scale(sensitivity, eps) that returns b = sensitivity / eps rounded to 4 decimals,
# and raises ValueError when eps is not positive.
# Why it works: ε = 0 would mean infinite noise: perfect privacy and no information at all. Real
# systems refuse it rather than divide by zero.

def laplace_scale(sensitivity, eps):
    if eps <= 0:
        raise ValueError("epsilon must be positive")
    return round(sensitivity / eps, 4)


# ================================================================== task 2: Randomised response estimate
# answers is a list of True and False from the fair coin randomised response survey. Write
# rr_estimate(answers) that returns the estimated true rate 2 × (share of True) − 0.5, clipped to
# the range 0 to 1 (post processing is free), rounded to 4 decimals.
# Why it works: With few answers the raw estimate can fall below 0 or above 1. Clipping after the
# fact costs no privacy, because it never looks at the data again.

def rr_estimate(answers):
    share = sum(answers) / len(answers)
    p = 2 * share - 0.5
    p = min(1.0, max(0.0, p))
    return round(p, 4)


# ================================================================== task 3: Privacy budget checker
# queries is a list of (epsilon, group) pairs. Queries with group None touch everyone and add up.
# Queries with a group name touch disjoint groups, and all named group queries together cost only
# their largest epsilon. Write budget_ok(queries, total) that returns the total cost rounded to 4
# decimals if it is at most total, or -1.0 if it is over the budget.
# Why it works: Real budget managers also record when each query ran and for whom, because a budget
# is a promise to the people in the data, not just a number in code.

def budget_ok(queries, total):
    seq = 0.0
    par = 0.0
    for eps, group in queries:
        if group is None:
            seq += eps
        else:
            par = max(par, eps)
    cost = round(seq + par, 4)
    if cost > total + 1e-9:
        return -1.0
    return cost


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Laplace noise scale", [('laplace_scale(1, 0.5)', 2.0), ('laplace_scale(1, 0.1)', 10.0), ('laplace_scale(0.04, 0.5)', 0.08), ('laplace_scale(3, 2)', 1.5)]))
    results.append(check("Task 2: Randomised response estimate", [('rr_estimate([True, True, False, False, False])', 0.3), ('rr_estimate([False, False, False, False])', 0.0), ('rr_estimate([True] * 9 + [False])', 1.0), ('rr_estimate([True, False])', 0.5)]))
    results.append(check("Task 3: Privacy budget checker", [('budget_ok([(0.3, None), (0.3, None), (0.3, None)], 1.0)', 0.9), ('budget_ok([(0.3, None), (0.3, None), (0.3, None), (0.3, None)], 1.0)', -1.0), ('budget_ok([(0.5, "Delhi"), (0.5, "Mumbai"), (0.4, "Pune"), (0.2, None)], 1.0)', 0.7), ('budget_ok([], 1.0)', 0.0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
