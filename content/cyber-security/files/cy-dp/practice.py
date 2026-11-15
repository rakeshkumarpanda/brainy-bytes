# 2.3 Differential privacy
# Practice tasks. Fill in each function, then run this file.
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
# Hint: Check eps first, then divide.

def laplace_scale(sensitivity, eps):
    # your code here
    pass


# ================================================================== task 2: Randomised response estimate
# answers is a list of True and False from the fair coin randomised response survey. Write
# rr_estimate(answers) that returns the estimated true rate 2 × (share of True) − 0.5, clipped to
# the range 0 to 1 (post processing is free), rounded to 4 decimals.
# Hint: sum() counts the True values. Compute the share, apply the formula, then clip with min and
# max.

def rr_estimate(answers):
    # your code here
    pass


# ================================================================== task 3: Privacy budget checker
# queries is a list of (epsilon, group) pairs. Queries with group None touch everyone and add up.
# Queries with a group name touch disjoint groups, and all named group queries together cost only
# their largest epsilon. Write budget_ok(queries, total) that returns the total cost rounded to 4
# decimals if it is at most total, or -1.0 if it is over the budget.
# Hint: Add the None queries, keep the maximum of the named ones, then compare the sum with the
# total.

def budget_ok(queries, total):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Laplace noise scale", [('laplace_scale(1, 0.5)', 2.0), ('laplace_scale(1, 0.1)', 10.0), ('laplace_scale(0.04, 0.5)', 0.08), ('laplace_scale(3, 2)', 1.5)]))
    results.append(check("Task 2: Randomised response estimate", [('rr_estimate([True, True, False, False, False])', 0.3), ('rr_estimate([False, False, False, False])', 0.0), ('rr_estimate([True] * 9 + [False])', 1.0), ('rr_estimate([True, False])', 0.5)]))
    results.append(check("Task 3: Privacy budget checker", [('budget_ok([(0.3, None), (0.3, None), (0.3, None)], 1.0)', 0.9), ('budget_ok([(0.3, None), (0.3, None), (0.3, None), (0.3, None)], 1.0)', -1.0), ('budget_ok([(0.5, "Delhi"), (0.5, "Mumbai"), (0.4, "Pune"), (0.2, None)], 1.0)', 0.7), ('budget_ok([], 1.0)', 0.0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
