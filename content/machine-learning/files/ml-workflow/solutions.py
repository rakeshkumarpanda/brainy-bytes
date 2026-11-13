# 1.2 The machine learning project: from a question to a working model
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


# ================================================================== task 1: Split a list into train and test
# Write split_list(items, test_fraction) that returns a pair (train, test). The test part is the
# LAST round(len(items) × test_fraction) items, and the train part is everything before it. Do not
# shuffle.
# Why it works: Taking the last part without shuffling is exactly how a time based split works: the
# most recent rows become the test set. A tuple and a list look the same to the checker, because
# both become a JSON list.

def split_list(items, test_fraction):
    n_test = round(len(items) * test_fraction)
    cut = len(items) - n_test
    return (items[:cut], items[cut:])


# ================================================================== task 2: A stratified split by hand
# Write stratified_test_indices(labels, test_fraction). For each different label, take the positions
# (indices) of that label in order and put the LAST round(count × test_fraction) of them in the test
# set. Return the sorted list of test indices.
# Why it works: Splitting each class separately keeps its share the same in train and test.
# scikit-learn does the same with stratify=y, but it shuffles inside each class first.

def stratified_test_indices(labels, test_fraction):
    positions = {}
    for i, label in enumerate(labels):
        if label not in positions:
            positions[label] = []
        positions[label].append(i)
    test = []
    for label in positions:
        places = positions[label]
        n_test = round(len(places) * test_fraction)
        if n_test > 0:
            test = test + places[-n_test:]
    return sorted(test)


# ================================================================== task 3: How sure is a test accuracy?
# Write accuracy_range(correct, total) that returns a list [low, high]: the accuracy p = correct /
# total minus and plus two standard errors, where SE = √(p(1 − p) / total). Round both numbers to 3
# decimals.
# Why it works: When p is 1.0 the formula says there is no uncertainty, which is too confident for a
# small test set. Better intervals such as the Wilson interval fix this edge case.

def accuracy_range(correct, total):
    p = correct / total
    se = (p * (1 - p) / total) ** 0.5
    return [round(p - 2 * se, 3), round(p + 2 * se, 3)]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Split a list into train and test", [('split_list([1, 2, 3, 4, 5], 0.4)', [[1, 2, 3], [4, 5]]), ('split_list(list(range(10)), 0.2)', [[0, 1, 2, 3, 4, 5, 6, 7], [8, 9]]), ('split_list(["a", "b"], 0.5)', [['a'], ['b']])]))
    results.append(check("Task 2: A stratified split by hand", [('stratified_test_indices([0, 0, 0, 0, 1, 1], 0.5)', [2, 3, 5]), ('stratified_test_indices(["a", "b", "a", "b", "a", "b", "a", "b"], 0.25)', [6, 7]), ('stratified_test_indices([1, 1, 1], 0.0)', [])]))
    results.append(check("Task 3: How sure is a test accuracy?", [('accuracy_range(90, 100)', [0.84, 0.96]), ('accuracy_range(160, 200)', [0.743, 0.857]), ('accuracy_range(50, 50)', [1.0, 1.0])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
