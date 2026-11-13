# 2.1 Linear algebra for ML: vectors, distances and matrices
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
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


# ================================================================== 1266. Minimum Time Visiting All Points (Easy)
# https://leetcode.com/problems/minimum-time-visiting-all-points/
# Pattern: Chebyshev distance
# Idea: Moving diagonally covers one step on both axes at once, so the time between two points is
# the larger of the two gaps, max(|dx|, |dy|). Add it for each pair of neighbours.

def min_time_to_visit_all_points(points):
    total = 0
    for i in range(1, len(points)):
        dx = abs(points[i][0] - points[i - 1][0])
        dy = abs(points[i][1] - points[i - 1][1])
        total = total + max(dx, dy)
    return total


# ================================================================== 1779. Find Nearest Point That Has the Same X or Y Coordinate (Easy)
# https://leetcode.com/problems/find-nearest-point-that-has-the-same-x-or-y-coordinate/
# Pattern: Manhattan distance with a filter
# Idea: Skip points that share neither x nor y. For the rest, compute the Manhattan distance and
# keep the smallest, earliest index on ties.

def nearest_valid_point(x, y, points):
    best_index = -1
    best_distance = None
    for i in range(len(points)):
        px = points[i][0]
        py = points[i][1]
        if px == x or py == y:
            d = abs(px - x) + abs(py - y)
            if best_distance is None or d < best_distance:
                best_distance = d
                best_index = i
    return best_index


# ================================================================== 566. Reshape the Matrix (Easy)
# https://leetcode.com/problems/reshape-the-matrix/
# Pattern: Reshape by flattening (NumPy reshape by hand)
# Idea: If r × c does not equal the number of values, return the original. Otherwise read the values
# row by row and fill the new shape row by row.

def matrix_reshape(mat, r, c):
    values = []
    for row in mat:
        for v in row:
            values.append(v)
    if len(values) != r * c:
        return mat
    result = []
    for i in range(r):
        result.append(values[i * c:(i + 1) * c])
    return result


# ================================================================== 1828. Queries on Number of Points Inside a Circle (Medium)
# https://leetcode.com/problems/queries-on-number-of-points-inside-a-circle/
# Pattern: Euclidean distance without the square root
# Idea: A point is inside when dx2 + dy2 ≤ r2. Comparing squared distances avoids the square root
# and gives the same answer.

def count_points(points, queries):
    answer = []
    for qx, qy, r in queries:
        inside = 0
        for px, py in points:
            if (px - qx) ** 2 + (py - qy) ** 2 <= r * r:
                inside = inside + 1
        answer.append(inside)
    return answer


# ================================================================== 1037. Valid Boomerang (Easy)
# https://leetcode.com/problems/valid-boomerang/
# Pattern: Determinant (cross product) for collinearity
# Idea: Three points lie on one line exactly when the 2 × 2 determinant of the two difference
# vectors is 0. If it is not 0, they form a boomerang.

def is_boomerang(points):
    ax = points[1][0] - points[0][0]
    ay = points[1][1] - points[0][1]
    bx = points[2][0] - points[0][0]
    by = points[2][1] - points[0][1]
    return ax * by - ay * bx != 0


# ================================================================== 1886. Determine Whether Matrix Can Be Obtained By Rotation (Easy)
# https://leetcode.com/problems/determine-whether-matrix-can-be-obtained-by-rotation/
# Pattern: Rotation as transpose plus reverse
# Idea: A quarter turn is the transpose with each row reversed. Try up to four turns and compare
# with the target each time.

def rotate_quarter(mat):
    n = len(mat)
    turned = []
    for c in range(n):
        new_row = []
        for r in range(n - 1, -1, -1):
            new_row.append(mat[r][c])
        turned.append(new_row)
    return turned


def find_rotation(mat, target):
    for turn in range(4):
        if mat == target:
            return True
        mat = rotate_quarter(mat)
    return False


if __name__ == "__main__":
    results = []
    results.append(check("1266. Minimum Time Visiting All Points", [('min_time_to_visit_all_points([[1, 1], [3, 4], [-1, 0]])', 7), ('min_time_to_visit_all_points([[3, 2], [-2, 2]])', 5)]))
    results.append(check("1779. Find Nearest Point That Has the Same X or Y Coordinate", [('nearest_valid_point(3, 4, [[1, 2], [3, 1], [2, 4], [2, 3], [4, 4]])', 2), ('nearest_valid_point(3, 4, [[3, 4]])', 0), ('nearest_valid_point(3, 4, [[2, 3]])', -1)]))
    results.append(check("566. Reshape the Matrix", [('matrix_reshape([[1, 2], [3, 4]], 1, 4)', [[1, 2, 3, 4]]), ('matrix_reshape([[1, 2], [3, 4]], 2, 4)', [[1, 2], [3, 4]])]))
    results.append(check("1828. Queries on Number of Points Inside a Circle", [('count_points([[1, 3], [3, 3], [5, 3], [2, 2]], [[2, 3, 1], [4, 3, 1], [1, 1, 2]])', [3, 2, 2])]))
    results.append(check("1037. Valid Boomerang", [('is_boomerang([[1, 1], [2, 3], [3, 2]])', True), ('is_boomerang([[1, 1], [2, 2], [3, 3]])', False)]))
    results.append(check("1886. Determine Whether Matrix Can Be Obtained By Rotation", [('find_rotation([[0, 1], [1, 0]], [[1, 0], [0, 1]])', True), ('find_rotation([[0, 1], [1, 1]], [[1, 0], [0, 1]])', False)]))
    if all(results):
        print("Every solution passes its tests.")
