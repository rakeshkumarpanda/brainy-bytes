# 1.2 Hierarchical clustering and DBSCAN
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


# ================================================================== task 1: Single linkage distance
# Write single_link_distance(a, b) where a and b are lists of [x, y] points. Return the smallest
# Euclidean distance between a point of a and a point of b, rounded to 4 decimals.
# Hint: Try every pair and keep the smallest distance.

def single_link_distance(a, b):
    # your code here
    pass


# ================================================================== task 2: Find the core points
# Write core_points(points, eps, min_pts). A point is core when at least min_pts points (counting
# itself) lie within distance eps (less than or equal). Return the indices of the core points in
# increasing order.
# Hint: Count the neighbours of each point, itself included.

def core_points(points, eps, min_pts):
    # your code here
    pass


# ================================================================== task 3: DBSCAN from scratch
# Write dbscan_labels(points, eps, min_pts) that returns a label for every point: −1 for noise, and
# 0, 1, 2 and so on for clusters. Visit points in index order and start a new cluster at each
# unlabelled core point. A border point takes the label of the first cluster that reaches it.
# Hint: Find neighbours, mark core points, then grow each cluster with a queue of core points.

def dbscan_labels(points, eps, min_pts):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Single linkage distance", [('single_link_distance([[0, 0], [1, 0]], [[4, 0], [5, 0]])', 3.0), ('single_link_distance([[0, 0]], [[3, 4]])', 5.0), ('single_link_distance([[0, 0], [0, 2]], [[1, 1]])', 1.4142)]))
    results.append(check("Task 2: Find the core points", [('core_points([[0, 0], [0, 1], [0, 2], [5, 5]], 1, 3)', [1]), ('core_points([[0, 0], [0, 1], [0, 2], [5, 5]], 1, 2)', [0, 1, 2]), ('core_points([[0, 0], [10, 10]], 1, 1)', [0, 1])]))
    results.append(check("Task 3: DBSCAN from scratch", [('dbscan_labels([[0, 0], [0, 1], [0, 2], [5, 5], [5, 6], [5, 7], [9, 0]], 1.0, 2)', [0, 0, 0, 1, 1, 1, -1]), ('dbscan_labels([[0, 0], [0, 1], [0, 2], [3, 0]], 1, 3)', [0, 0, 0, -1]), ('dbscan_labels([[0, 0], [4, 4]], 1, 2)', [-1, -1])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
