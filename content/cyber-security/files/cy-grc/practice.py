# 2.3 Governance, risk, compliance and cyber law
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


# ================================================================== task 1: GDPR maximum fine
# Write gdpr_fine(turnover) that returns the maximum fine for a serious breach: the higher of
# 20000000 or 4% of turnover, as a float rounded to 2 decimals.
# Hint: max of the fixed amount and the percentage.

def gdpr_fine(turnover):
    # your code here
    pass


# ================================================================== task 2: Audit sample size
# Write audit_size(error_rate, confidence) that returns the smallest whole n with 1 − (1 −
# error_rate)n ≥ confidence, using math.ceil(math.log(1 - confidence) / math.log(1 - error_rate)) or
# a loop.
# Hint: Increase n one at a time until the chance to catch reaches the confidence.

import math

def audit_size(error_rate, confidence):
    # your code here
    pass


# ================================================================== task 3: Weighted vendor risk score
# weights and scores are dictionaries with the same keys. Write vendor_score(weights, scores) that
# returns the weighted sum rounded to 1 decimal, and raises ValueError if the weights do not add up
# to 1 (allow a difference of 1e-9).
# Hint: Check the weights first, then add weight times score for each key.

def vendor_score(weights, scores):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: GDPR maximum fine", [('gdpr_fine(2000000000)', 80000000.0), ('gdpr_fine(100000000)', 20000000.0), ('gdpr_fine(0)', 20000000.0), ('gdpr_fine(600000000)', 24000000.0)]))
    results.append(check("Task 2: Audit sample size", [('audit_size(0.05, 0.95)', 59), ('audit_size(0.02, 0.99)', 228), ('audit_size(0.1, 0.9)', 22), ('audit_size(0.5, 0.75)', 2)]))
    results.append(check("Task 3: Weighted vendor risk score", [('vendor_score({"a": 0.4, "b": 0.3, "c": 0.3}, {"a": 80, "b": 50, "c": 70})', 68.0), ('vendor_score({"a": 0.5, "b": 0.5}, {"a": 10, "b": 20})', 15.0), ('vendor_score({"a": 1.0}, {"a": 33})', 33.0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
