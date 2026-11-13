# 3.2 Features: encoding, scaling, engineering and selection
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


# ================================================================== task 1: One hot encode a list
# Write one_hot(values) that returns a list of rows. The columns are the different values in sorted
# order, and each row has 1 in the column of its value and 0 elsewhere.
# Hint: First find the sorted categories with sorted(set(values)). Then, for each value, make a row
# of 0s with a 1 where the category matches.

def one_hot(values):
    # your code here
    pass


# ================================================================== task 2: Standardise a list
# Write standardise(values) that returns (x − mean) / std for every value, rounded to 2 decimals.
# Use the population std (divide by n). If the std is 0, return a list of zeros.
# Hint: Compute the mean, then the std, then transform each value. Guard against a std of 0.

def standardise(values):
    # your code here
    pass


# ================================================================== task 3: Min max scale with training values
# Write minmax_scale(train, test). Learn the min and max from train only, then return the scaled
# test values (x − min) / (max − min), rounded to 2 decimals. Test values may fall outside 0 to 1.
# Hint: Use min(train) and max(train). Never look at the test values when you learn the scale.

def minmax_scale(train, test):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: One hot encode a list", [('one_hot(["b", "a", "b"])', [[0, 1], [1, 0], [0, 1]]), ('one_hot(["Pune", "Delhi", "Mumbai"])', [[0, 0, 1], [1, 0, 0], [0, 1, 0]])]))
    results.append(check("Task 2: Standardise a list", [('standardise([2, 4, 6])', [-1.22, 0.0, 1.22]), ('standardise([5, 5])', [0, 0]), ('standardise([10, 20])', [-1.0, 1.0])]))
    results.append(check("Task 3: Min max scale with training values", [('minmax_scale([10, 20, 30], [15, 30])', [0.25, 1.0]), ('minmax_scale([0, 100], [50, 120, -10])', [0.5, 1.2, -0.1])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
