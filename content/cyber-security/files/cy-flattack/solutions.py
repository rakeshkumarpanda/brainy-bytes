# 2.2 Attacks and defences in federated learning
# Model solutions. Try practice.py first.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.


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


# ================================================================== task 1: Rebuild an input from a gradient
# Write recover_input(grad_row, grad_bias) that returns the input rebuilt from one row of a dense
# layer’s weight gradient and the matching bias gradient: each entry divided by grad_bias, rounded
# to 4 decimals.
# Why it works: This only works for a single example and a layer with a bias. It is a reminder that
# model updates are personal data and need the same care as the data itself.

def recover_input(grad_row, grad_bias):
    out = []
    for g in grad_row:
        out.append(round(g / grad_bias, 4))
    return out


# ================================================================== task 2: Coordinate wise median
# updates is a list of equal length lists. Write coord_median(updates) that returns the median of
# each position, rounded to 4 decimals. Use statistics.median.
# Why it works: The median of each coordinate need not be any client’s actual update. Krum, in the
# next task, always returns a real update instead.

import statistics

def coord_median(updates):
    out = []
    for k in range(len(updates[0])):
        column = [u[k] for u in updates]
        out.append(round(statistics.median(column), 4))
    return out


# ================================================================== task 3: Krum selection
# Write krum_select(updates, f) that returns the index of the update chosen by Krum: for each
# update, add the squared distances to its n − f − 2 nearest other updates, and return the index
# with the smallest total (the first one if there is a tie).
# Why it works: Multi-Krum averages the m best scoring updates instead of taking one, which keeps
# more honest information while staying robust.

def krum_select(updates, f):
    n = len(updates)
    scores = []
    for i, u in enumerate(updates):
        dists = []
        for j, v in enumerate(updates):
            if j != i:
                dists.append(sum((a - b) ** 2 for a, b in zip(u, v)))
        dists.sort()
        scores.append(sum(dists[:n - f - 2]))
    return scores.index(min(scores))


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Rebuild an input from a gradient", [('recover_input([-0.558, -0.062, -0.434, -0.186], -0.62)', [0.9, 0.1, 0.7, 0.3]), ('recover_input([0.2, 0.4], 0.5)', [0.4, 0.8]), ('recover_input([1.5, -3.0, 0.0], 3.0)', [0.5, -1.0, 0.0])]))
    results.append(check("Task 2: Coordinate wise median", [('coord_median([[1.0, 0.5], [1.1, 0.4], [0.9, 0.6], [1.05, 0.55], [0.95, 0.45], [1.2, 0.5], [0.85, 0.5], [-8.0, 9.0], [-8.5, 9.5], [-7.5, 8.5]])', [0.925, 0.525]), ('coord_median([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [100.0, -100.0, 0.0]])', [4.0, 2.0, 3.0]), ('coord_median([[1.0], [2.0], [3.0], [4.0]])', [2.5])]))
    results.append(check("Task 3: Krum selection", [('krum_select([[1.0, 0.5], [1.1, 0.4], [0.9, 0.6], [1.05, 0.55], [0.95, 0.45], [1.2, 0.5], [0.85, 0.5], [-8.0, 9.0], [-8.5, 9.5], [-7.5, 8.5]], 3)', 0), ('krum_select([[0.0], [0.1], [0.2], [5.0], [0.15]], 1)', 4), ('krum_select([[1, 1], [1.2, 0.9], [0.9, 1.1], [10, 10], [1.1, 1.0], [0.95, 1.05], [9, 11]], 2)', 0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
