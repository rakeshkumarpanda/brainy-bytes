# 2.1 Linear algebra for ML: vectors, distances and matrices
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


# ================================================================== task 1: Euclidean distance by hand
# Write euclidean(u, v) that returns the straight line distance between two lists of numbers of the
# same length, rounded to 3 decimals. Do not use NumPy.
# Why it works: k nearest neighbours calls this function for every stored example. NumPy does the
# same with np.linalg.norm(u - v).

def euclidean(u, v):
    total = 0
    for a, b in zip(u, v):
        total = total + (a - b) ** 2
    return round(total ** 0.5, 3)


# ================================================================== task 2: Cosine similarity by hand
# Write cosine(u, v) that returns the cosine similarity of two non zero lists of the same length,
# rounded to 3 decimals.
# Why it works: Search engines and recommendation systems compare embedding vectors with exactly
# this formula.

def cosine(u, v):
    dot = 0
    size_u = 0
    size_v = 0
    for a, b in zip(u, v):
        dot = dot + a * b
        size_u = size_u + a * a
        size_v = size_v + b * b
    return round(dot / (size_u ** 0.5 * size_v ** 0.5), 3)


# ================================================================== task 3: Matrix times vector
# Write mat_vec(M, v) that returns M times v as a list: one dot product of each row of M with v.
# Why it works: A linear model applied to a whole dataset is this function with M = X and v = w.
# NumPy writes it as M @ v.

def mat_vec(M, v):
    result = []
    for row in M:
        total = 0
        for a, b in zip(row, v):
            total = total + a * b
        result.append(total)
    return result


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Euclidean distance by hand", [('euclidean([0, 0], [3, 4])', 5.0), ('euclidean([1, 2, 2], [3, 5, 8])', 7.0), ('euclidean([1, 1], [2, 2])', 1.414)]))
    results.append(check("Task 2: Cosine similarity by hand", [('cosine([1, 2], [2, 4])', 1.0), ('cosine([1, 0], [0, 1])', 0.0), ('cosine([1, 0], [1, 1])', 0.707), ('cosine([1, 1], [-1, -1])', -1.0)]))
    results.append(check("Task 3: Matrix times vector", [('mat_vec([[2, 1], [0, 1]], [1, 2])', [4, 2]), ('mat_vec([[1, 0], [0, 1]], [7, 9])', [7, 9]), ('mat_vec([[1, 2, 3]], [1, 1, 1])', [6])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
