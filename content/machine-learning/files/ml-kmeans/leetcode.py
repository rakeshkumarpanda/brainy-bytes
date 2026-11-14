# 1.1 k-means: grouping points around centres
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


# ================================================================== 200. Number of Islands (Medium)
# https://leetcode.com/problems/number-of-islands/
# Pattern: Flood fill each new piece of land
# Idea: Scan the grid. Each time you meet unvisited land, count an island and visit all land
# connected to it. Each island is a cluster of touching cells.

def num_islands(grid):
    rows, cols = len(grid), len(grid[0])
    seen = set()
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in seen:
                count = count + 1
                stack = [(r, c)]
                seen.add((r, c))
                while stack:
                    i, j = stack.pop()
                    for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        a, b = i + di, j + dj
                        if 0 <= a < rows and 0 <= b < cols and grid[a][b] == "1" and (a, b) not in seen:
                            seen.add((a, b))
                            stack.append((a, b))
    return count


# ================================================================== 695. Max Area of Island (Medium)
# https://leetcode.com/problems/max-area-of-island/
# Pattern: Flood fill and count the cells
# Idea: Visit each island as in the last problem, counting its cells, and keep the largest count.
# The size of each cluster is often the first thing you check after clustering.

def max_area_of_island(grid):
    rows, cols = len(grid), len(grid[0])
    seen = set()
    best = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and (r, c) not in seen:
                size = 0
                stack = [(r, c)]
                seen.add((r, c))
                while stack:
                    i, j = stack.pop()
                    size = size + 1
                    for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        a, b = i + di, j + dj
                        if 0 <= a < rows and 0 <= b < cols and grid[a][b] == 1 and (a, b) not in seen:
                            seen.add((a, b))
                            stack.append((a, b))
                best = max(best, size)
    return best


# ================================================================== 547. Number of Provinces (Medium)
# https://leetcode.com/problems/number-of-provinces/
# Pattern: Union find over the connections
# Idea: Every city starts as its own group. For each connection, merge the two groups. The number of
# groups left is the answer. Single linkage clustering merges groups the same way.

def find_circle_num(is_connected):
    n = len(is_connected)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    groups = n
    for i in range(n):
        for j in range(i + 1, n):
            if is_connected[i][j]:
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b
                    groups = groups - 1
    return groups


# ================================================================== 1029. Two City Scheduling (Medium)
# https://leetcode.com/problems/two-city-scheduling/
# Pattern: Sort by how much city A saves
# Idea: Send everyone to city B, then move the half for whom going to A instead saves the most. Sort
# by cost A minus cost B and send the first half to A. It is an assignment of points to two groups
# at the lowest total cost.

def two_city_sched_cost(costs):
    order = sorted(costs, key=lambda c: c[0] - c[1])
    n = len(costs) // 2
    return sum(c[0] for c in order[:n]) + sum(c[1] for c in order[n:])


# ================================================================== 2033. Minimum Operations to Make a Uni-Value Grid (Medium)
# https://leetcode.com/problems/minimum-operations-to-make-a-uni-value-grid/
# Pattern: Move everything to the median
# Idea: All values must share the same remainder when divided by x, or it is impossible. Then the
# cheapest common value is the median, because the median minimises the total absolute distance,
# just as the mean minimises the squared distance in k-means.

def min_operations(grid, x):
    values = sorted(v for row in grid for v in row)
    if any((v - values[0]) % x for v in values):
        return -1
    median = values[len(values) // 2]
    return sum(abs(v - median) // x for v in values)


# ================================================================== 1478. Allocate Mailboxes (Hard)
# https://leetcode.com/problems/allocate-mailboxes/
# Pattern: One dimensional k medians by dynamic programming
# Idea: Sort the houses. The best single mailbox for a run of houses sits at their median. Then
# dp[j][i] is the least distance for the first i houses with j mailboxes: try every last run. This
# is exact clustering in one dimension, something k-means can only approximate.

def min_distance(houses, k):
    h = sorted(houses)
    n = len(h)
    cost = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            m = h[(i + j) // 2]
            cost[i][j] = sum(abs(h[t] - m) for t in range(i, j + 1))
    INF = float("inf")
    dp = [[INF] * (n + 1) for _ in range(k + 1)]
    dp[0][0] = 0
    for j in range(1, k + 1):
        for i in range(1, n + 1):
            for s in range(i):
                if dp[j - 1][s] < INF:
                    dp[j][i] = min(dp[j][i], dp[j - 1][s] + cost[s][i - 1])
    return dp[k][n]


if __name__ == "__main__":
    results = []
    results.append(check("200. Number of Islands", [('num_islands([["1", "1", "0", "0"], ["1", "1", "0", "0"], ["0", "0", "1", "0"], ["0", "0", "0", "1"]])', 3), ('num_islands([["1", "1", "1"], ["0", "1", "0"], ["1", "1", "1"]])', 1)]))
    results.append(check("695. Max Area of Island", [('max_area_of_island([[0, 0, 1, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 1, 1, 0]])', 4), ('max_area_of_island([[0, 0, 0]])', 0)]))
    results.append(check("547. Number of Provinces", [('find_circle_num([[1, 1, 0], [1, 1, 0], [0, 0, 1]])', 2), ('find_circle_num([[1, 0, 0], [0, 1, 0], [0, 0, 1]])', 3)]))
    results.append(check("1029. Two City Scheduling", [('two_city_sched_cost([[10, 20], [30, 200], [400, 50], [30, 20]])', 110), ('two_city_sched_cost([[259, 770], [448, 54], [926, 667], [184, 139], [840, 118], [577, 469]])', 1859)]))
    results.append(check("2033. Minimum Operations to Make a Uni-Value Grid", [('min_operations([[2, 4], [6, 8]], 2)', 4), ('min_operations([[1, 2], [3, 4]], 2)', -1)]))
    results.append(check("1478. Allocate Mailboxes", [('min_distance([1, 4, 8, 10, 20], 3)', 5), ('min_distance([2, 3, 5, 12, 18], 2)', 9)]))
    if all(results):
        print("Every solution passes its tests.")
