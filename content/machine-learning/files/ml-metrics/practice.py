# 4.1 Metrics: measuring a model properly
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


# ================================================================== task 1: Precision and recall
# Write precision_recall(actual, predicted) for two lists of 0 and 1. Return a tuple (precision,
# recall), each rounded to 4 decimals. Use 0.0 when a denominator is 0.
# Hint: Count TP, FP and FN, then divide, guarding against zero.

def precision_recall(actual, predicted):
    # your code here
    pass


# ================================================================== task 2: The F beta score
# Write f_beta(precision, recall, beta) that returns (1 + beta2) × P × R / (beta2 × P + R), rounded
# to 4 decimals, and 0.0 when P and R are both 0.
# Hint: Square beta once, then type the formula.

def f_beta(precision, recall, beta):
    # your code here
    pass


# ================================================================== task 3: AUC by counting pairs
# Write auc_pairs(labels, scores). For every pair of one positive and one negative, count 1 if the
# positive scores higher and 0.5 for a tie. Return the count divided by the number of pairs, rounded
# to 4 decimals.
# Hint: Split scores by label, compare every positive with every negative.

def auc_pairs(labels, scores):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Precision and recall", [('precision_recall([1, 1, 1, 1, 0, 0, 0, 0, 0, 0], [1, 1, 1, 0, 1, 0, 0, 0, 0, 0])', (0.75, 0.75)), ('precision_recall([1, 0, 1], [0, 0, 0])', (0.0, 0.0)), ('precision_recall([1, 1, 0], [1, 1, 1])', (0.6667, 1.0))]))
    results.append(check("Task 2: The F beta score", [('f_beta(0.8, 0.5, 1)', 0.6154), ('f_beta(0.8, 0.5, 2)', 0.5405), ('f_beta(0, 0, 1)', 0.0)]))
    results.append(check("Task 3: AUC by counting pairs", [('auc_pairs([0, 0, 1, 0, 1, 1, 0, 1], [0.1, 0.3, 0.35, 0.4, 0.6, 0.7, 0.8, 0.9])', 0.75), ('auc_pairs([1, 0], [0.9, 0.1])', 1.0), ('auc_pairs([1, 0, 1, 0], [0.5, 0.5, 0.2, 0.8])', 0.125)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
