# 1.3 Markov decision processes and Bellman equations
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


# ================================================================== 509. Fibonacci Number (Easy)
# https://leetcode.com/problems/fibonacci-number/
# Pattern: Each value comes from the two before it
# Idea: Keep only the last two numbers and step forward. A value defined by earlier values is the
# simplest recursion, the same shape as a Bellman equation.

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# ================================================================== 746. Min Cost Climbing Stairs (Easy)
# https://leetcode.com/problems/min-cost-climbing-stairs/
# Pattern: Best cost to reach step i = min of the two ways in
# Idea: The cheapest cost to stand on step i is the cheaper of coming from i − 1 or i − 2, plus that
# step’s cost. Choosing the best of several moves and adding a cost is a Bellman optimality backup
# with costs instead of rewards.

def min_cost_climbing_stairs(cost):
    a = b = 0
    for i in range(2, len(cost) + 1):
        a, b = b, min(b + cost[i - 1], a + cost[i - 2])
    return b


# ================================================================== 64. Minimum Path Sum (Medium)
# https://leetcode.com/problems/minimum-path-sum/
# Pattern: Work backwards from the goal
# Idea: The best total from a cell is its own cost plus the better of the best totals to the right
# and below. Filling the table from the goal backwards is exactly how optimal values are found in a
# deterministic gridworld.

def min_path_sum(grid):
    m, n = len(grid), len(grid[0])
    best = [[0] * n for _ in range(m)]
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if i == m - 1 and j == n - 1:
                best[i][j] = grid[i][j]
            elif i == m - 1:
                best[i][j] = grid[i][j] + best[i][j + 1]
            elif j == n - 1:
                best[i][j] = grid[i][j] + best[i + 1][j]
            else:
                best[i][j] = grid[i][j] + min(best[i + 1][j], best[i][j + 1])
    return best[0][0]


# ================================================================== 120. Triangle (Medium)
# https://leetcode.com/problems/triangle/
# Pattern: Collapse the triangle from the bottom row up
# Idea: Start with the bottom row as the best totals. Each number above adds the smaller of its two
# children. One pass from the bottom gives the answer at the top, in the style of a backward Bellman
# sweep.

def minimum_total(triangle):
    below = triangle[-1][:]
    for row in reversed(triangle[:-1]):
        below = [v + min(below[i], below[i + 1]) for i, v in enumerate(row)]
    return below[0]


# ================================================================== 935. Knight Dialer (Medium)
# https://leetcode.com/problems/knight-dialer/
# Pattern: Count numbers by pushing counts through the knight’s moves
# Idea: Keep how many numbers end on each digit. Each step, every digit passes its count to the
# digits a knight can jump to. This is a Markov chain transition applied n − 1 times, with counts
# instead of probabilities.

def knight_dialer(n):
    MOD = 10 ** 9 + 7
    jumps = {0: [4, 6], 1: [6, 8], 2: [7, 9], 3: [4, 8], 4: [0, 3, 9], 5: [], 6: [0, 1, 7], 7: [2, 6], 8: [1, 3], 9: [2, 4]}
    count = [1] * 10
    for _ in range(n - 1):
        nxt = [0] * 10
        for d in range(10):
            for e in jumps[d]:
                nxt[e] = (nxt[e] + count[d]) % MOD
        count = nxt
    return sum(count) % MOD


# ================================================================== 174. Dungeon Game (Hard)
# https://leetcode.com/problems/dungeon-game/
# Pattern: Go backwards from the princess: health needed on entering each room
# Idea: Forward search fails because the best path depends on what comes later. Instead compute,
# from the goal backwards, the least health needed when entering each room: one less than the
# smaller need of the next rooms minus this room’s value, but at least 1. Backward induction like
# this is how finite horizon MDPs are solved.

def calculate_minimum_hp(dungeon):
    m, n = len(dungeon), len(dungeon[0])
    INF = float("inf")
    need = [[INF] * (n + 1) for _ in range(m + 1)]
    need[m][n - 1] = need[m - 1][n] = 1
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            need[i][j] = max(1, min(need[i + 1][j], need[i][j + 1]) - dungeon[i][j])
    return need[0][0]


if __name__ == "__main__":
    results = []
    results.append(check("509. Fibonacci Number", [('fib(2)', 1), ('fib(4)', 3), ('fib(10)', 55)]))
    results.append(check("746. Min Cost Climbing Stairs", [('min_cost_climbing_stairs([10, 15, 20])', 15), ('min_cost_climbing_stairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1])', 6)]))
    results.append(check("64. Minimum Path Sum", [('min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]])', 7), ('min_path_sum([[1, 2, 3], [4, 5, 6]])', 12)]))
    results.append(check("120. Triangle", [('minimum_total([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]])', 11), ('minimum_total([[-10]])', -10)]))
    results.append(check("935. Knight Dialer", [('knight_dialer(1)', 10), ('knight_dialer(2)', 20), ('knight_dialer(3131)', 136006598)]))
    results.append(check("174. Dungeon Game", [('calculate_minimum_hp([[-2, -3, 3], [-5, -10, 1], [10, 30, -5]])', 7), ('calculate_minimum_hp([[0]])', 1)]))
    if all(results):
        print("Every solution passes its tests.")
