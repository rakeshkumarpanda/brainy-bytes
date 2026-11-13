# 3.2 Random forests: many trees vote
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


# ================================================================== task 1: Out of bag rows
# Write oob_rows(n, draws). Rows are numbered 1 to n and draws is the list of rows in a bootstrap
# sample. Return the sorted list of rows that were never drawn.
# Hint: Put the draws in a set, then keep every row from 1 to n that is not in it.

def oob_rows(n, draws):
    # your code here
    pass


# ================================================================== task 2: Majority vote
# Write majority_vote(predictions) for a list of class labels from the trees. Return the label with
# the most votes. If several tie, return the smallest label.
# Hint: Count each label, then pick the largest count and the smallest label on ties.

def majority_vote(predictions):
    # your code here
    pass


# ================================================================== task 3: Variance of a forest
# Write forest_variance(rho, sigma2, trees) that returns rho × sigma2 + (1 − rho) × sigma2 / trees,
# rounded to 4 decimals.
# Hint: Type the formula and round.

def forest_variance(rho, sigma2, trees):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Out of bag rows", [('oob_rows(5, [1, 1, 3, 5, 5])', [2, 4]), ('oob_rows(3, [1, 2, 3])', []), ('oob_rows(4, [2, 2, 2, 2])', [1, 3, 4])]))
    results.append(check("Task 2: Majority vote", [('majority_vote(["cat", "dog", "cat"])', 'cat'), ('majority_vote([1, 0, 1, 0])', 0), ('majority_vote([2, 2, 3, 3, 3])', 3)]))
    results.append(check("Task 3: Variance of a forest", [('forest_variance(0, 4, 100)', 0.04), ('forest_variance(0.5, 1, 10)', 0.55), ('forest_variance(0.3, 2, 1)', 2.0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
