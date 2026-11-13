# 2.2 Manifold learning: t-SNE, UMAP, MDS and Isomap
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


# ================================================================== task 1: Stress of a map
# Write raw_stress(d, dz) where d and dz are square distance tables (given and map). Return the sum
# over pairs i < j of (d[i][j] − dz[i][j])2, rounded to 4 decimals.
# Hint: Loop over the upper triangle only, so each pair counts once.

def raw_stress(d, dz):
    # your code here
    pass


# ================================================================== task 2: Distance through a neighbour graph
# Write geodesic(points, k, a, b). Link every point to its k nearest other points (break distance
# ties by lower index), treat links as two way with Euclidean lengths, and return the shortest path
# length from point a to point b rounded to 4 decimals, or −1 if b cannot be reached.
# Hint: Build the k neighbour graph, make it two way, then run Dijkstra.

def geodesic(points, k, a, b):
    # your code here
    pass


# ================================================================== task 3: Perplexity of a distribution
# Write perplexity(probs) that returns 2H, where H = −Σ p log2 p over the non zero probabilities,
# rounded to 4 decimals.
# Hint: Compute the entropy in bits, then raise 2 to it.

import math


def perplexity(probs):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Stress of a map", [('raw_stress([[0, 3], [3, 0]], [[0, 2], [2, 0]])', 1.0), ('raw_stress([[0, 1, 2], [1, 0, 1], [2, 1, 0]], [[0, 1, 1], [1, 0, 1], [1, 1, 0]])', 1.0), ('raw_stress([[0, 5], [5, 0]], [[0, 5], [5, 0]])', 0.0)]))
    results.append(check("Task 2: Distance through a neighbour graph", [('geodesic([[0, 0], [1, 0], [2, 0], [3, 0]], 1, 0, 3)', 3.0), ('geodesic([[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]], 1, 0, 4)', 4.0), ('geodesic([[0, 0], [0, 1], [5, 5], [5, 6]], 1, 0, 3)', -1)]))
    results.append(check("Task 3: Perplexity of a distribution", [('perplexity([0.5, 0.5])', 2.0), ('perplexity([0.25, 0.25, 0.25, 0.25])', 4.0), ('perplexity([1.0])', 1.0), ('perplexity([0.5, 0.25, 0.25])', 2.8284)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
