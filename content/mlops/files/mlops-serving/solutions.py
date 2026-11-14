# 2.2 Serving models with Flask, FastAPI and Django
# Model solutions. Try practice.py first.
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


# ================================================================== task 1: Validate a request body
# Write validate_features(body) for a /predict route. Return 200 when body is a dict whose features
# value is a list of exactly 4 numbers (int or float, but not True or False). Return 422 otherwise.
# Why it works: FastAPI does all of this from a Pydantic class. Writing it once by hand shows what
# the framework saves you.

def validate_features(body):
    if not isinstance(body, dict):
        return 422
    features = body.get('features')
    if not isinstance(features, list) or len(features) != 4:
        return 422
    for v in features:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return 422
    return 200


# ================================================================== task 2: Size a pool of workers
# Write workers_needed(rps, latency_ms, target=0.75) that returns the smallest whole number of
# workers that keeps each one at or below the target share of its time busy. Use Little’s law: busy
# workers = rps × latency in seconds.
# Why it works: The round before ceil stops a float such as 10.000000000000002 from becoming 11.

import math


def workers_needed(rps, latency_ms, target=0.75):
    busy = rps * latency_ms / 1000
    return math.ceil(round(busy / target, 9))


# ================================================================== task 3: Split a big file into chunks
# Write chunk_sizes(n_rows, size) that returns the list of chunk lengths a batch job reads, as
# pd.read_csv(chunksize=size) would: full chunks of size and a smaller last one if rows remain.
# Why it works: Chunks keep memory flat however big the file is, because only one chunk is in memory
# at a time.

def chunk_sizes(n_rows, size):
    return [min(size, n_rows - start) for start in range(0, n_rows, size)]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Validate a request body", [("validate_features({'features': [5.9, 3.0, 5.1, 1.8]})", 200), ("validate_features({'features': [5.9, 'wide']})", 422), ("validate_features({'features': [1, 2, 3, True]})", 422), ('validate_features([1, 2, 3, 4])', 422), ('validate_features({})', 422)]))
    results.append(check("Task 2: Size a pool of workers", [('workers_needed(300, 25)', 10), ('workers_needed(50, 20)', 2), ('workers_needed(100, 10, 1.0)', 1), ('workers_needed(2000, 30, 0.8)', 75)]))
    results.append(check("Task 3: Split a big file into chunks", [('chunk_sizes(20000, 5000)', [5000, 5000, 5000, 5000]), ('chunk_sizes(12, 5)', [5, 5, 2]), ('chunk_sizes(0, 5)', []), ('chunk_sizes(3, 10)', [3])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
