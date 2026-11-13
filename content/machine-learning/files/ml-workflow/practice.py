# 1.2 The machine learning project: from a question to a working model
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


# ================================================================== task 1: Split a list into train and test
# Write split_list(items, test_fraction) that returns a pair (train, test). The test part is the
# LAST round(len(items) × test_fraction) items, and the train part is everything before it. Do not
# shuffle.
# Hint: Work out how many test items there are with round(), then slice the list at len(items) minus
# that number.

def split_list(items, test_fraction):
    # your code here
    pass


# ================================================================== task 2: A stratified split by hand
# Write stratified_test_indices(labels, test_fraction). For each different label, take the positions
# (indices) of that label in order and put the LAST round(count × test_fraction) of them in the test
# set. Return the sorted list of test indices.
# Hint: Group the indices by label in a dict of lists. For each group, slice off the last part.
# Watch out: places[-0:] is the whole list, so skip groups with n_test = 0.

def stratified_test_indices(labels, test_fraction):
    # your code here
    pass


# ================================================================== task 3: How sure is a test accuracy?
# Write accuracy_range(correct, total) that returns a list [low, high]: the accuracy p = correct /
# total minus and plus two standard errors, where SE = √(p(1 − p) / total). Round both numbers to 3
# decimals.
# Hint: Find p first, then the standard error with ** 0.5 for the square root, then subtract and add
# 2 × SE.

def accuracy_range(correct, total):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Split a list into train and test", [('split_list([1, 2, 3, 4, 5], 0.4)', [[1, 2, 3], [4, 5]]), ('split_list(list(range(10)), 0.2)', [[0, 1, 2, 3, 4, 5, 6, 7], [8, 9]]), ('split_list(["a", "b"], 0.5)', [['a'], ['b']])]))
    results.append(check("Task 2: A stratified split by hand", [('stratified_test_indices([0, 0, 0, 0, 1, 1], 0.5)', [2, 3, 5]), ('stratified_test_indices(["a", "b", "a", "b", "a", "b", "a", "b"], 0.25)', [6, 7]), ('stratified_test_indices([1, 1, 1], 0.0)', [])]))
    results.append(check("Task 3: How sure is a test accuracy?", [('accuracy_range(90, 100)', [0.84, 0.96]), ('accuracy_range(160, 200)', [0.743, 0.857]), ('accuracy_range(50, 50)', [1.0, 1.0])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
