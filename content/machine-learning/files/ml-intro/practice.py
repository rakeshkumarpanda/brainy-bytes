# 1.1 What machine learning is: learning from examples
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


# ================================================================== task 1: Mean squared error by hand
# Write mean_squared_error(y_true, y_pred) that returns the average of the squared differences
# between two lists of the same length.
# Hint: Loop over both lists together with zip. Add (t − p) squared. Divide by the length at the
# end.

def mean_squared_error(y_true, y_pred):
    # your code here
    pass


# ================================================================== task 2: Accuracy by hand
# Write accuracy(y_true, y_pred) that returns the share of positions where the two lists hold the
# same label, as a number between 0 and 1.
# Hint: Count the matches, then divide by how many there are.

def accuracy(y_true, y_pred):
    # your code here
    pass


# ================================================================== task 3: A baseline model: always predict the most common label
# Write most_common_label(labels) that returns the label that appears most often in the training
# labels. When two labels tie, return the one that appears first in the list. This "majority class"
# model is the first baseline every project should beat.
# Hint: Count each label in a dict. Keep the order of first appearance in a list, so ties go to the
# earliest label.

def most_common_label(labels):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Mean squared error by hand", [('mean_squared_error([10, 20, 30], [10, 20, 30])', 0.0), ('mean_squared_error([3, 7], [5, 4])', 6.5), ('mean_squared_error([1], [4])', 9.0)]))
    results.append(check("Task 2: Accuracy by hand", [('accuracy(["a", "b", "a"], ["a", "b", "b"])', 0.6666666666666666), ('accuracy([1, 1, 0, 0], [1, 1, 0, 0])', 1.0), ('accuracy([1, 0], [0, 1])', 0.0)]))
    results.append(check("Task 3: A baseline model: always predict the most common label", [('most_common_label(["ham", "spam", "ham"])', 'ham'), ('most_common_label([1, 0, 0, 1])', 1), ('most_common_label(["cat"])', 'cat')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
