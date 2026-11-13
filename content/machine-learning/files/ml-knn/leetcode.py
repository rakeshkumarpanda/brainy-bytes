# 2.2 k nearest neighbours: learn from similar examples
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


# ================================================================== 973. K Closest Points to Origin (Medium)
# https://leetcode.com/problems/k-closest-points-to-origin/
# Pattern: Nearest neighbours with a heap
# Idea: Keep a max heap of the k closest points seen so far (store negative squared distances). Push
# each point and pop when the heap grows past k. Squared distance is enough, no square root needed.

import heapq


def k_closest(points, k):
    heap = []
    for x, y in points:
        d = x * x + y * y
        heapq.heappush(heap, (-d, x, y))
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted([[x, y] for d, x, y in heap])


# ================================================================== 658. Find K Closest Elements (Medium)
# https://leetcode.com/problems/find-k-closest-elements/
# Pattern: Binary search for the start of the window
# Idea: The answer is a window of k neighbours in the sorted list. Binary search its left edge: if x
# is closer to arr[mid + k] than to arr[mid], move right.

def find_closest_elements(arr, k, x):
    low = 0
    high = len(arr) - k
    while low < high:
        mid = (low + high) // 2
        if x - arr[mid] > arr[mid + k] - x:
            low = mid + 1
        else:
            high = mid
    return arr[low:low + k]


# ================================================================== 1637. Widest Vertical Area Between Two Points Containing No Points (Easy)
# https://leetcode.com/problems/widest-vertical-area-between-two-points-containing-no-points/
# Pattern: Sort along one axis, then look at neighbours
# Idea: Only x matters. Sort the x values and take the largest gap between neighbouring values.
# Sorting first is also how a k-d tree splits points along one axis.

def max_width_of_vertical_area(points):
    xs = sorted(p[0] for p in points)
    best = 0
    for i in range(1, len(xs)):
        best = max(best, xs[i] - xs[i - 1])
    return best


# ================================================================== 1030. Matrix Cells in Distance Order (Easy)
# https://leetcode.com/problems/matrix-cells-in-distance-order/
# Pattern: Sort by Manhattan distance
# Idea: List every cell and sort by |r − r0| + |c − c0|. This is exactly how KNN orders candidates
# before taking the first k.

def all_cells_dist_order(rows, cols, r_center, c_center):
    cells = []
    for r in range(rows):
        for c in range(cols):
            cells.append([r, c])
    cells.sort(key=lambda cell: abs(cell[0] - r_center) + abs(cell[1] - c_center))
    return cells


# ================================================================== 1584. Min Cost to Connect All Points (Medium)
# https://leetcode.com/problems/min-cost-to-connect-all-points/
# Pattern: Manhattan distances and a minimum spanning tree
# Idea: Grow a tree from point 0. Keep, for every point outside the tree, its cheapest Manhattan
# distance to the tree, and add the cheapest point each round (Prim’s algorithm, O(n2)).

def min_cost_connect_points(points):
    n = len(points)
    in_tree = [False] * n
    cheapest = [float("inf")] * n
    cheapest[0] = 0
    total = 0
    for step in range(n):
        best = -1
        for i in range(n):
            if not in_tree[i] and (best == -1 or cheapest[i] < cheapest[best]):
                best = i
        in_tree[best] = True
        total = total + cheapest[best]
        bx, by = points[best]
        for i in range(n):
            if not in_tree[i]:
                d = abs(points[i][0] - bx) + abs(points[i][1] - by)
                if d < cheapest[i]:
                    cheapest[i] = d
    return total


# ================================================================== 719. Find K-th Smallest Pair Distance (Hard)
# https://leetcode.com/problems/find-k-th-smallest-pair-distance/
# Pattern: Binary search on the distance, count with two pointers
# Idea: Sort. For a guess distance g, count pairs with difference at most g using a sliding window.
# The answer is the smallest g with at least k such pairs.

def smallest_distance_pair(nums, k):
    s = sorted(nums)
    low = 0
    high = s[-1] - s[0]
    while low < high:
        mid = (low + high) // 2
        count = 0
        left = 0
        for right in range(len(s)):
            while s[right] - s[left] > mid:
                left = left + 1
            count = count + right - left
        if count >= k:
            high = mid
        else:
            low = mid + 1
    return low


if __name__ == "__main__":
    results = []
    results.append(check("973. K Closest Points to Origin", [('k_closest([[1, 3], [-2, 2]], 1)', [[-2, 2]]), ('k_closest([[3, 3], [5, -1], [-2, 4]], 2)', [[-2, 4], [3, 3]])]))
    results.append(check("658. Find K Closest Elements", [('find_closest_elements([1, 2, 3, 4, 5], 4, 3)', [1, 2, 3, 4]), ('find_closest_elements([1, 1, 2, 3, 4, 5], 4, -1)', [1, 1, 2, 3])]))
    results.append(check("1637. Widest Vertical Area Between Two Points Containing No Points", [('max_width_of_vertical_area([[8, 7], [9, 9], [7, 4], [9, 7]])', 1), ('max_width_of_vertical_area([[3, 1], [9, 0], [1, 0], [1, 4], [5, 3], [8, 8]])', 3)]))
    results.append(check("1030. Matrix Cells in Distance Order", [('all_cells_dist_order(1, 2, 0, 0)', [[0, 0], [0, 1]]), ('all_cells_dist_order(2, 2, 0, 1)', [[0, 1], [0, 0], [1, 1], [1, 0]])]))
    results.append(check("1584. Min Cost to Connect All Points", [('min_cost_connect_points([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]])', 20), ('min_cost_connect_points([[3, 12], [-2, 5], [-4, 1]])', 18)]))
    results.append(check("719. Find K-th Smallest Pair Distance", [('smallest_distance_pair([1, 3, 1], 1)', 0), ('smallest_distance_pair([1, 1, 1], 2)', 0), ('smallest_distance_pair([1, 6, 1], 3)', 5)]))
    if all(results):
        print("Every solution passes its tests.")
