# 1.1 k-means: grouping points around centres
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


# ================================================================== task 1: The assign step
# Write assign(points, centres) where both are lists of [x, y]. Return a list with the index of the
# nearest centre (smallest squared distance) for each point. On a tie take the lower index.
# Why it works: [1, 7] is 36 from [1, 1] but 26 from [6, 6], so it joins centre 1 even though it
# looks closer to the left group.

def assign(points, centres):
    labels = []
    for px, py in points:
        best = 0
        best_d = None
        for k, (cx, cy) in enumerate(centres):
            d = (px - cx) ** 2 + (py - cy) ** 2
            if best_d is None or d < best_d:
                best, best_d = k, d
        labels.append(best)
    return labels


# ================================================================== task 2: The update step
# Write update(points, labels, k) that returns the k centres, each the mean [x, y] of its points,
# rounded to 4 decimals. A cluster with no points keeps [0.0, 0.0].
# Why it works: scikit-learn instead moves an empty cluster’s centre to a far point, so that no
# cluster stays empty.

def update(points, labels, k):
    centres = []
    for j in range(k):
        mine = [p for p, l in zip(points, labels) if l == j]
        if not mine:
            centres.append([0.0, 0.0])
        else:
            centres.append([round(sum(p[0] for p in mine) / len(mine), 4), round(sum(p[1] for p in mine) / len(mine), 4)])
    return centres


# ================================================================== task 3: Silhouette of one point
# Write silhouette(a, b) where a is the mean distance to the point’s own cluster and b to the
# nearest other cluster. Return (b − a) / max(a, b), rounded to 4 decimals, or 0.0 if both are 0.
# Why it works: A negative value suggests the point would fit better in the other cluster.

def silhouette(a, b):
    if a == 0 and b == 0:
        return 0.0
    return round((b - a) / max(a, b), 4)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The assign step", [('assign([[1, 1], [6, 6], [1, 7]], [[1, 1], [6, 6]])', [0, 1, 1]), ('assign([[0, 0]], [[1, 0], [-1, 0]])', [0]), ('assign([[5, 5], [0, 1]], [[0, 0], [5, 4], [9, 9]])', [1, 0])]))
    results.append(check("Task 2: The update step", [('update([[1, 1], [3, 3], [10, 10]], [0, 0, 1], 2)', [[2.0, 2.0], [10.0, 10.0]]), ('update([[0, 0], [1, 2]], [1, 1], 2)', [[0.0, 0.0], [0.5, 1.0]]), ('update([[1, 2], [2, 4], [3, 6]], [0, 0, 0], 1)', [[2.0, 4.0]])]))
    results.append(check("Task 3: Silhouette of one point", [('silhouette(2, 5)', 0.6), ('silhouette(4, 3)', -0.25), ('silhouette(0, 0)', 0.0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
