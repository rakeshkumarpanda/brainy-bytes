# 2.3 Attention and transformers
# Model solutions. Try practice.py first.
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
# Why it works: The last test would overflow without subtracting the maximum, because e1000 is too
# large for a float.

import math


def softmax_weights(scores):
    m = max(scores)
    e = [math.exp(s - m) for s in scores]
    total = sum(e)
    return [round(v / total, 4) for v in e]


# ================================================================== task 2: Attention for one query
# Write attend(query, keys, values) that computes scaled dot product attention for one query: scores
# q · k / √d, softmax, then the weighted sum of the value vectors, each entry rounded to 4 decimals.
# Why it works: The second test shows that a zero query gives equal weights, so attention returns
# the plain average of the values.

import math


def attend(query, keys, values):
    d = len(query)
    scores = [sum(q * k for q, k in zip(query, key)) / math.sqrt(d) for key in keys]
    m = max(scores)
    e = [math.exp(s - m) for s in scores]
    w = [v / sum(e) for v in e]
    return [round(sum(w[j] * values[j][i] for j in range(len(values))), 4) for i in range(len(values[0]))]


# ================================================================== task 3: A causal mask
# Write causal_mask(n) that returns an n × n list of lists with 1 where position i may attend to
# position j (j ≤ i) and 0 elsewhere.
# Why it works: In practice the zeros are turned into −∞ added to the scores before softmax, so
# blocked positions get weight 0.

def causal_mask(n):
    return [[1 if j <= i else 0 for j in range(n)] for i in range(n)]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A stable softmax", [('softmax_weights([0.0, 0.0])', [0.5, 0.5]), ('softmax_weights([1.0, 2.0, 3.0])', [0.09, 0.2447, 0.6652]), ('softmax_weights([1000.0, 1000.0, 1000.0, 1000.0])', [0.25, 0.25, 0.25, 0.25])]))
    results.append(check("Task 2: Attention for one query", [('attend([1, 0], [[1, 0], [0, 1]], [[1, 0], [0, 1]])', [0.6698, 0.3302]), ('attend([0, 0], [[1, 0], [0, 1]], [[2, 4], [4, 2]])', [3.0, 3.0]), ('attend([2, 2], [[1, 1], [-1, -1], [0, 0]], [[1.0], [0.0], [0.5]])', [0.9689])]))
    results.append(check("Task 3: A causal mask", [('causal_mask(3)', [[1, 0, 0], [1, 1, 0], [1, 1, 1]]), ('causal_mask(1)', [[1]])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
