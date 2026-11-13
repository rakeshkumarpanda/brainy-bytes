# 2.4 Support vector machines: the widest street
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


# ================================================================== 164. Maximum Gap (Medium)
# https://leetcode.com/problems/maximum-gap/
# Pattern: Sort, then find the widest gap
# Idea: The widest gap between neighbouring values appears only after sorting. Sort, then compare
# each pair of neighbours. An SVM in one dimension puts its boundary in the middle of exactly such a
# gap.

def maximum_gap(nums):
    if len(nums) < 2:
        return 0
    s = sorted(nums)
    best = 0
    for i in range(1, len(s)):
        best = max(best, s[i] - s[i - 1])
    return best


# ================================================================== 2078. Two Furthest Houses With Different Colors (Easy)
# https://leetcode.com/problems/two-furthest-houses-with-different-colors/
# Pattern: The answer uses an end
# Idea: The furthest pair with different colours always includes the first or the last house. Scan
# from each end for the furthest house with a different colour.

def max_distance(colors):
    n = len(colors)
    best = 0
    for j in range(n):
        if colors[j] != colors[0]:
            best = max(best, j)
        if colors[j] != colors[n - 1]:
            best = max(best, n - 1 - j)
    return best


# ================================================================== 836. Rectangle Overlap (Easy)
# https://leetcode.com/problems/rectangle-overlap/
# Pattern: Separated on one axis means no overlap
# Idea: Two boxes do not overlap exactly when one is completely to the left, right, above or below
# the other. That is the separating axis idea: if a straight line splits them, they are separable.

def is_rectangle_overlap(rec1, rec2):
    left = rec1[2] <= rec2[0]
    right = rec2[2] <= rec1[0]
    below = rec1[3] <= rec2[1]
    above = rec2[3] <= rec1[1]
    return not (left or right or below or above)


# ================================================================== 593. Valid Square (Medium)
# https://leetcode.com/problems/valid-square/
# Pattern: Count squared distances
# Idea: Compute the 6 squared distances between the 4 points. A square has exactly two different
# values, 4 equal sides and 2 equal diagonals, and none of them is zero. Squared distances are what
# the RBF kernel uses.

def valid_square(p1, p2, p3, p4):
    pts = [p1, p2, p3, p4]
    d = []
    for i in range(4):
        for j in range(i + 1, 4):
            d.append((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2)
    d.sort()
    return d[0] > 0 and d[0] == d[3] and d[4] == d[5] and d[4] == 2 * d[0]


# ================================================================== 2249. Count Lattice Points Inside a Circle (Medium)
# https://leetcode.com/problems/count-lattice-points-inside-a-circle/
# Pattern: Check each grid point against each circle
# Idea: Look at every integer point in the box that holds all circles. A point counts when its
# squared distance to some centre is at most r squared. A circle boundary is what the x squared
# feature lets a linear SVM draw.

def count_lattice_points(circles):
    hits = set()
    for x0, y0, r in circles:
        for x in range(x0 - r, x0 + r + 1):
            for y in range(y0 - r, y0 + r + 1):
                if (x - x0) ** 2 + (y - y0) ** 2 <= r * r:
                    hits.add((x, y))
    return len(hits)


# ================================================================== 812. Largest Triangle Area (Easy)
# https://leetcode.com/problems/largest-triangle-area/
# Pattern: Try every triple with the cross product
# Idea: Try every choice of three points and compute the area with the cross product formula, half
# the absolute value of (x2 − x1)(y3 − y1) − (x3 − x1)(y2 − y1). The sign of the same cross product
# tells which side of a line a point lies on, the core test of any linear classifier.

def largest_triangle_area(points):
    best = 0.0
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                (x1, y1), (x2, y2), (x3, y3) = points[i], points[j], points[k]
                area = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2
                best = max(best, area)
    return best


if __name__ == "__main__":
    results = []
    results.append(check("164. Maximum Gap", [('maximum_gap([3, 6, 9, 1])', 3), ('maximum_gap([10])', 0)]))
    results.append(check("2078. Two Furthest Houses With Different Colors", [('max_distance([1, 1, 1, 6, 1, 1, 1])', 3), ('max_distance([1, 8, 3, 8, 3])', 4)]))
    results.append(check("836. Rectangle Overlap", [('is_rectangle_overlap([0, 0, 2, 2], [1, 1, 3, 3])', True), ('is_rectangle_overlap([0, 0, 1, 1], [1, 0, 2, 1])', False)]))
    results.append(check("593. Valid Square", [('valid_square([0, 0], [1, 1], [1, 0], [0, 1])', True), ('valid_square([0, 0], [1, 1], [1, 0], [0, 12])', False)]))
    results.append(check("2249. Count Lattice Points Inside a Circle", [('count_lattice_points([[2, 2, 1]])', 5), ('count_lattice_points([[2, 2, 2], [3, 4, 1]])', 16)]))
    results.append(check("812. Largest Triangle Area", [('largest_triangle_area([[0, 0], [0, 1], [1, 0], [0, 2], [2, 0]])', 2.0), ('largest_triangle_area([[1, 0], [0, 0], [0, 1]])', 0.5)]))
    if all(results):
        print("Every solution passes its tests.")
