# 2.2 Serving models with Flask, FastAPI and Django
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


# ================================================================== task 1: Validate a request body
# Write validate_features(body) for a /predict route. Return 200 when body is a dict whose features
# value is a list of exactly 4 numbers (int or float, but not True or False). Return 422 otherwise.
# Hint: Check the type of body, then the list and its length, then each value. bool is a subclass of
# int in Python, so test for it first.

def validate_features(body):
    # your code here
    pass


# ================================================================== task 2: Size a pool of workers
# Write workers_needed(rps, latency_ms, target=0.75) that returns the smallest whole number of
# workers that keeps each one at or below the target share of its time busy. Use Little’s law: busy
# workers = rps × latency in seconds.
# Hint: Busy workers is rps times latency in seconds. Divide by the target use and round up.

def workers_needed(rps, latency_ms, target=0.75):
    # your code here
    pass


# ================================================================== task 3: Split a big file into chunks
# Write chunk_sizes(n_rows, size) that returns the list of chunk lengths a batch job reads, as
# pd.read_csv(chunksize=size) would: full chunks of size and a smaller last one if rows remain.
# Hint: Step through the rows in jumps of size. The last chunk holds whatever is left.

def chunk_sizes(n_rows, size):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Validate a request body", [("validate_features({'features': [5.9, 3.0, 5.1, 1.8]})", 200), ("validate_features({'features': [5.9, 'wide']})", 422), ("validate_features({'features': [1, 2, 3, True]})", 422), ('validate_features([1, 2, 3, 4])', 422), ('validate_features({})', 422)]))
    results.append(check("Task 2: Size a pool of workers", [('workers_needed(300, 25)', 10), ('workers_needed(50, 20)', 2), ('workers_needed(100, 10, 1.0)', 1), ('workers_needed(2000, 30, 0.8)', 75)]))
    results.append(check("Task 3: Split a big file into chunks", [('chunk_sizes(20000, 5000)', [5000, 5000, 5000, 5000]), ('chunk_sizes(12, 5)', [5, 5, 2]), ('chunk_sizes(0, 5)', []), ('chunk_sizes(3, 10)', [3])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
