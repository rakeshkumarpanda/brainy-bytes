# 1.2 The MLOps lifecycle and reproducible projects
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


# ================================================================== task 1: A data fingerprint
# Write data_fingerprint(rows) that returns the first 12 characters of the SHA-256 hash of
# repr(rows) encoded as UTF-8. Use hashlib.
# Hint: hashlib.sha256 takes bytes, so encode the repr text, then take hexdigest()[:12].

import hashlib


def data_fingerprint(rows):
    # your code here
    pass


# ================================================================== task 2: Pick the best run
# Write best_run(runs, metric, higher_is_better). runs is a list of dictionaries with a 'name' and
# metric values. Return the name of the run with the best value of metric. If two are equal, keep
# the first.
# Hint: Keep the best so far and replace it only when a later run is strictly better in the right
# direction.

def best_run(runs, metric, higher_is_better):
    # your code here
    pass


# ================================================================== task 3: Mean and spread over seeds
# Write seed_spread(scores) that returns [mean, std] of the scores, using the population standard
# deviation (divide by n), both rounded to 4 decimals.
# Hint: Average the scores, then take the square root of the average squared distance from that
# mean.

def seed_spread(scores):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A data fingerprint", [('data_fingerprint([[1, 2], [3, 4]])', '1e258794ed04'), ('data_fingerprint([[1, 2], [3, 5]])', '23f12147ee03'), ('data_fingerprint([])', '4f53cda18c2b')]))
    results.append(check("Task 2: Pick the best run", [("best_run([{'name': 'a', 'acc': 0.95}, {'name': 'b', 'acc': 0.97}], 'acc', True)", 'b'), ("best_run([{'name': 'a', 'rmse': 3.1}, {'name': 'b', 'rmse': 2.4}, {'name': 'c', 'rmse': 2.4}], 'rmse', False)", 'b'), ("best_run([{'name': 'x', 'acc': 0.9}], 'acc', True)", 'x')]))
    results.append(check("Task 3: Mean and spread over seeds", [('seed_spread([0.9, 0.8, 1.0, 0.8, 0.9])', [0.88, 0.0748]), ('seed_spread([0.5, 0.5])', [0.5, 0.0]), ('seed_spread([1.0, 0.0])', [0.5, 0.5])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
