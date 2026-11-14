# 3.3 Boosting: small trees that fix each other
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


# ================================================================== task 1: A boosted prediction
# Write boost_predict(base, tree_preds, lr). base is the starting constant, tree_preds the
# predictions of each tree for one example. Return base + lr × sum(tree_preds), rounded to 4
# decimals.
# Hint: Start from base and add lr times each tree.

def boost_predict(base, tree_preds, lr):
    # your code here
    pass


# ================================================================== task 2: AdaBoost say
# Write ada_alpha(err) that returns ½ ln((1 − err)/err), rounded to 4 decimals, for 0 < err < 1.
# Hint: One line with math.log.

import math


def ada_alpha(err):
    # your code here
    pass


# ================================================================== task 3: XGBoost leaf weight
# Write leaf_weight(grads, hessians, lam) for the gradients and hessians of the examples in one
# leaf. Return −sum(grads) / (sum(hessians) + lam), rounded to 4 decimals.
# Hint: Sum the gradients and hessians, then apply the formula.

def leaf_weight(grads, hessians, lam):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A boosted prediction", [('boost_predict(10, [4, -2], 0.5)', 11.0), ('boost_predict(0, [1, 1, 1], 0.1)', 0.3), ('boost_predict(2.5, [], 0.3)', 2.5)]))
    results.append(check("Task 2: AdaBoost say", [('ada_alpha(0.25)', 0.5493), ('ada_alpha(0.5)', 0.0), ('ada_alpha(0.1)', 1.0986)]))
    results.append(check("Task 3: XGBoost leaf weight", [('leaf_weight([-1, -3], [3, 3], 2)', 0.5), ('leaf_weight([2, 2], [1, 1], 0)', -2.0), ('leaf_weight([0.5, -0.5], [1, 1], 1)', 0.0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
