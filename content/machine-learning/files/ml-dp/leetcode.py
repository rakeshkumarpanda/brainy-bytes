# 2.1 Dynamic programming: policy and value iteration
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


# ================================================================== 1137. N-th Tribonacci Number (Easy)
# https://leetcode.com/problems/n-th-tribonacci-number/
# Pattern: Carry the last three values forward
# Idea: Each term is the sum of the three before it. Update three variables at once. Carrying a
# small state forward and updating it again and again is what every DP sweep does.

def tribonacci(n):
    a, b, c = 0, 1, 1
    for _ in range(n):
        a, b, c = b, c, a + b + c
    return a


# ================================================================== 118. Pascal's Triangle (Easy)
# https://leetcode.com/problems/pascals-triangle/
# Pattern: Each row comes from the row above
# Idea: Every inner number is the sum of the two numbers above it. Building a new row entirely from
# the previous one is a synchronous sweep: the old values are read, the new ones written.

def generate(num_rows):
    rows = [[1]]
    for _ in range(num_rows - 1):
        prev = rows[-1]
        rows.append([1] + [prev[i] + prev[i + 1] for i in range(len(prev) - 1)] + [1])
    return rows


# ================================================================== 198. House Robber (Medium)
# https://leetcode.com/problems/house-robber/
# Pattern: Two values: best total if you rob this house, and if you skip it
# Idea: At each house choose the better of robbing it (the previous skip total plus its money) or
# skipping it (the better of the two previous totals). A max over two actions at every step is a
# Bellman optimality backup.

def rob(nums):
    take, skip = 0, 0
    for v in nums:
        take, skip = skip + v, max(take, skip)
    return max(take, skip)


# ================================================================== 322. Coin Change (Medium)
# https://leetcode.com/problems/coin-change/
# Pattern: Fewest coins for each amount, built from smaller amounts
# Idea: best[a] is the minimum over coins c of best[a − c] + 1. Each amount is a state, each coin an
# action with cost 1, and the table is filled like value iteration on a deterministic MDP.

def coin_change(coins, amount):
    INF = amount + 1
    best = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and best[a - c] + 1 < best[a]:
                best[a] = best[a - c] + 1
    return best[amount] if best[amount] <= amount else -1


# ================================================================== 787. Cheapest Flights Within K Stops (Medium)
# https://leetcode.com/problems/cheapest-flights-within-k-stops/
# Pattern: Bellman Ford for k + 1 rounds, reading only last round’s costs
# Idea: Run k + 1 rounds of relaxing every flight, but compute each round from a copy of the
# previous costs, so a round adds at most one flight. Bellman Ford is value iteration for shortest
# paths: each round is one sweep of the Bellman backup with costs.

def find_cheapest_price(n, flights, src, dst, k):
    INF = float("inf")
    cost = [INF] * n
    cost[src] = 0
    for _ in range(k + 1):
        new = cost[:]
        for u, v, w in flights:
            if cost[u] + w < new[v]:
                new[v] = cost[u] + w
        cost = new
    return cost[dst] if cost[dst] < INF else -1


# ================================================================== 1463. Cherry Pickup II (Hard)
# https://leetcode.com/problems/cherry-pickup-ii/
# Pattern: State = the two robots’ columns, swept row by row
# Idea: Both robots move down one row at a time, so the state is the pair of columns. For each row,
# every pair of moves (9 of them) updates the best total for the new pair, counting a shared cell
# once. Sweeping a state table forward row by row with a max over joint actions is DP over a joint
# state space.

def cherry_pickup(grid):
    rows, cols = len(grid), len(grid[0])
    NEG = float("-inf")
    best = [[NEG] * cols for _ in range(cols)]
    best[0][cols - 1] = grid[0][0] + (grid[0][cols - 1] if cols > 1 else 0)
    for r in range(1, rows):
        new = [[NEG] * cols for _ in range(cols)]
        for a in range(cols):
            for b in range(cols):
                if best[a][b] == NEG:
                    continue
                for na in (a - 1, a, a + 1):
                    for nb in (b - 1, b, b + 1):
                        if 0 <= na < cols and 0 <= nb < cols:
                            gain = grid[r][na] + (grid[r][nb] if na != nb else 0)
                            if best[a][b] + gain > new[na][nb]:
                                new[na][nb] = best[a][b] + gain
        best = new
    return max(max(row) for row in best)


if __name__ == "__main__":
    results = []
    results.append(check("1137. N-th Tribonacci Number", [('tribonacci(4)', 4), ('tribonacci(25)', 1389537)]))
    results.append(check("118. Pascal's Triangle", [('generate(5)', [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]]), ('generate(1)', [[1]])]))
    results.append(check("198. House Robber", [('rob([1, 2, 3, 1])', 4), ('rob([2, 7, 9, 3, 1])', 12)]))
    results.append(check("322. Coin Change", [('coin_change([1, 2, 5], 11)', 3), ('coin_change([2], 3)', -1), ('coin_change([1], 0)', 0)]))
    results.append(check("787. Cheapest Flights Within K Stops", [('find_cheapest_price(4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1)', 700), ('find_cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1)', 200), ('find_cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0)', 500)]))
    results.append(check("1463. Cherry Pickup II", [('cherry_pickup([[3, 1, 1], [2, 5, 1], [1, 5, 5], [2, 1, 1]])', 24), ('cherry_pickup([[1, 0, 0, 0, 0, 0, 1], [2, 0, 0, 0, 0, 3, 0], [2, 0, 9, 0, 0, 0, 0], [0, 3, 0, 5, 4, 0, 0], [1, 0, 2, 3, 0, 0, 6]])', 28)]))
    if all(results):
        print("Every solution passes its tests.")
