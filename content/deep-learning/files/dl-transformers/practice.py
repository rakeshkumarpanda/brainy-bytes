# 2.3 Attention and transformers
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
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


# ================================================================== task 1: A stable softmax
# Write softmax_weights(scores) that returns softmax of the list, subtracting the maximum first for
# stability, each rounded to 4 decimals.
# Hint: Subtract the largest score, exponentiate, and divide by the sum.

def softmax_weights(scores):
    # your code here
    pass


# ================================================================== task 2: Attention for one query
# Write attend(query, keys, values) that computes scaled dot product attention for one query: scores
# q · k / √d, softmax, then the weighted sum of the value vectors, each entry rounded to 4 decimals.
# Hint: Score each key, scale by the root of the dimension, softmax the scores, and blend the values
# with those weights.

def attend(query, keys, values):
    # your code here
    pass


# ================================================================== task 3: A causal mask
# Write causal_mask(n) that returns an n × n list of lists with 1 where position i may attend to
# position j (j ≤ i) and 0 elsewhere.
# Hint: Row i allows columns 0 to i and blocks the rest.

def causal_mask(n):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A stable softmax", [('softmax_weights([0.0, 0.0])', [0.5, 0.5]), ('softmax_weights([1.0, 2.0, 3.0])', [0.09, 0.2447, 0.6652]), ('softmax_weights([1000.0, 1000.0, 1000.0, 1000.0])', [0.25, 0.25, 0.25, 0.25])]))
    results.append(check("Task 2: Attention for one query", [('attend([1, 0], [[1, 0], [0, 1]], [[1, 0], [0, 1]])', [0.6698, 0.3302]), ('attend([0, 0], [[1, 0], [0, 1]], [[2, 4], [4, 2]])', [3.0, 3.0]), ('attend([2, 2], [[1, 1], [-1, -1], [0, 0]], [[1.0], [0.0], [0.5]])', [0.9689])]))
    results.append(check("Task 3: A causal mask", [('causal_mask(3)', [[1, 0, 0], [1, 1, 0], [1, 1, 1]]), ('causal_mask(1)', [[1]])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
