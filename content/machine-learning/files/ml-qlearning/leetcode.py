# 2.3 SARSA and Q learning
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


# ================================================================== 2373. Largest Local Values in a Matrix (Easy)
# https://leetcode.com/problems/largest-local-values-in-a-matrix/
# Pattern: Take the max of every 3 by 3 block
# Idea: For each top left corner, take the largest of the nine values below and to the right. A max
# over a small neighbourhood is what Q learning computes over the next state’s actions.

def largest_local(grid):
    n = len(grid)
    return [[max(grid[r][c] for r in range(i, i + 3) for c in range(j, j + 3)) for j in range(n - 2)] for i in range(n - 2)]


# ================================================================== 62. Unique Paths (Medium)
# https://leetcode.com/problems/unique-paths/
# Pattern: Paths to a cell = paths from above + paths from the left
# Idea: Keep one row of counts and add the left neighbour into each cell, row after row. Counting
# routes on a grid shows how quickly the number of possible paths grows, which is why RL learns
# values instead of listing paths.

def unique_paths(m, n):
    row = [1] * n
    for _ in range(m - 1):
        for j in range(1, n):
            row[j] += row[j - 1]
    return row[-1]


# ================================================================== 1091. Shortest Path in Binary Matrix (Medium)
# https://leetcode.com/problems/shortest-path-in-binary-matrix/
# Pattern: Breadth first search over 8 directions
# Idea: With equal cost moves, breadth first search finds the shortest path, visiting cells in order
# of distance. Q learning on a grid with −1 per move learns the same distances as negative values,
# but from trial and error instead of a known map.

from collections import deque


def shortest_path_binary_matrix(grid):
    n = len(grid)
    if grid[0][0] or grid[n - 1][n - 1]:
        return -1
    dist = {(0, 0): 1}
    q = deque([(0, 0)])
    while q:
        r, c = q.popleft()
        if (r, c) == (n - 1, n - 1):
            return dist[(r, c)]
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and not grid[nr][nc] and (nr, nc) not in dist:
                    dist[(nr, nc)] = dist[(r, c)] + 1
                    q.append((nr, nc))
    return -1


# ================================================================== 1926. Nearest Exit from Entrance in Maze (Medium)
# https://leetcode.com/problems/nearest-exit-from-entrance-in-maze/
# Pattern: Breadth first search until you reach a border cell other than the entrance
# Idea: Search outward from the entrance and stop at the first open cell on the border. A maze with
# exits is a gridworld: the answer is minus the optimal value of the entrance when each move costs
# 1.

from collections import deque


def nearest_exit(maze, entrance):
    rows, cols = len(maze), len(maze[0])
    start = tuple(entrance)
    seen = {start}
    q = deque([(start, 0)])
    while q:
        (r, c), d = q.popleft()
        if (r, c) != start and (r in (0, rows - 1) or c in (0, cols - 1)):
            return d
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == "." and (nr, nc) not in seen:
                seen.add((nr, nc))
                q.append(((nr, nc), d + 1))
    return -1


# ================================================================== 1293. Shortest Path in a Grid with Obstacles Elimination (Hard)
# https://leetcode.com/problems/shortest-path-in-a-grid-with-obstacles-elimination/
# Pattern: Add the number of eliminations left to the state
# Idea: Position alone is not enough to decide what to do next: you also need to know how many walls
# you can still break. Search over (row, column, eliminations left). Choosing a state that holds
# everything needed for the future is exactly the Markov property from chapter 1.3.

from collections import deque


def shortest_path_elimination(grid, k):
    m, n = len(grid), len(grid[0])
    if k >= m + n - 2:
        return m + n - 2
    seen = {(0, 0, k)}
    q = deque([(0, 0, k, 0)])
    while q:
        r, c, left, d = q.popleft()
        if (r, c) == (m - 1, n - 1):
            return d
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < m and 0 <= nc < n:
                nl = left - grid[nr][nc]
                if nl >= 0 and (nr, nc, nl) not in seen:
                    seen.add((nr, nc, nl))
                    q.append((nr, nc, nl, d + 1))
    return -1


if __name__ == "__main__":
    results = []
    results.append(check("2373. Largest Local Values in a Matrix", [('largest_local([[9, 9, 8, 1], [5, 6, 2, 6], [8, 2, 6, 4], [6, 2, 2, 2]])', [[9, 9], [8, 6]])]))
    results.append(check("62. Unique Paths", [('unique_paths(3, 7)', 28), ('unique_paths(3, 2)', 3)]))
    results.append(check("1091. Shortest Path in Binary Matrix", [('shortest_path_binary_matrix([[0, 1], [1, 0]])', 2), ('shortest_path_binary_matrix([[0, 0, 0], [1, 1, 0], [1, 1, 0]])', 4), ('shortest_path_binary_matrix([[1, 0, 0], [1, 1, 0], [1, 1, 0]])', -1)]))
    results.append(check("1926. Nearest Exit from Entrance in Maze", [('nearest_exit([["+", "+", ".", "+"], [".", ".", ".", "+"], ["+", "+", "+", "."]], [1, 2])', 1), ('nearest_exit([["+", "+", "+"], [".", ".", "."], ["+", "+", "+"]], [1, 0])', 2), ('nearest_exit([[".", "+"]], [0, 0])', -1)]))
    results.append(check("1293. Shortest Path in a Grid with Obstacles Elimination", [('shortest_path_elimination([[0, 0, 0], [1, 1, 0], [0, 0, 0], [0, 1, 1], [0, 0, 0]], 1)', 6), ('shortest_path_elimination([[0, 1, 1], [1, 1, 1], [1, 0, 0]], 1)', -1)]))
    if all(results):
        print("Every solution passes its tests.")
