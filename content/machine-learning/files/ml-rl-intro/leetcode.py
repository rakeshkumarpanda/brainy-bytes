# 1.1 Agents, rewards and returns
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


# ================================================================== 657. Robot Return to Origin (Easy)
# https://leetcode.com/problems/robot-return-to-origin/
# Pattern: Count moves in each direction
# Idea: The robot is back at the start when right moves equal left moves and up moves equal down
# moves. Tracking where actions take the agent is the job of an environment’s step function.

def judge_circle(moves):
    x = moves.count("R") - moves.count("L")
    y = moves.count("U") - moves.count("D")
    return x == 0 and y == 0


# ================================================================== 70. Climbing Stairs (Easy)
# https://leetcode.com/problems/climbing-stairs/
# Pattern: Ways to reach step n = ways to reach n − 1 + ways to reach n − 2
# Idea: Build the answer from smaller ones and keep only the last two numbers. The same idea of
# reusing the answer from the next step gives returns backwards: Gt = r + γ Gt+1.

def climb_stairs(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# ================================================================== 874. Walking Robot Simulation (Medium)
# https://leetcode.com/problems/walking-robot-simulation/
# Pattern: Simulate one square at a time and check a set of obstacles
# Idea: Keep a direction index into lists of x and y steps, turn by changing the index, and move one
# square at a time unless the next square is blocked. Track the largest squared distance. Writing a
# faithful step by step simulator is the first job in any RL project.

def robot_sim(commands, obstacles):
    blocked = set(map(tuple, obstacles))
    dx, dy = [0, 1, 0, -1], [1, 0, -1, 0]
    x = y = d = best = 0
    for c in commands:
        if c == -2:
            d = (d + 3) % 4
        elif c == -1:
            d = (d + 1) % 4
        else:
            for _ in range(c):
                if (x + dx[d], y + dy[d]) in blocked:
                    break
                x, y = x + dx[d], y + dy[d]
                best = max(best, x * x + y * y)
    return best


# ================================================================== 2400. Number of Ways to Reach a Position After Exactly k Steps (Medium)
# https://leetcode.com/problems/number-of-ways-to-reach-a-position-after-exactly-k-steps/
# Pattern: Count how many of the k steps must go right
# Idea: If the distance is d, you need (k + d) / 2 steps right and the rest left, and the parity
# must match. The answer is a binomial coefficient. Walks on a line are the corridor of this
# chapter.

def number_of_ways(start_pos, end_pos, k):
    MOD = 10 ** 9 + 7
    d = abs(end_pos - start_pos)
    if d > k or (k - d) % 2:
        return 0
    right = (k + d) // 2
    ways = 1
    for i in range(right):
        ways = ways * (k - i) // (i + 1)
    return ways % MOD


# ================================================================== 576. Out of Boundary Paths (Medium)
# https://leetcode.com/problems/out-of-boundary-paths/
# Pattern: Spread path counts one move at a time
# Idea: Keep the number of ways to stand on each cell after each move. Every move that leaves the
# grid adds its count to the answer. Pushing counts (or probabilities) forward step by step is how
# the distribution of states under a policy is computed.

def find_paths(m, n, max_move, start_row, start_column):
    MOD = 10 ** 9 + 7
    count = {(start_row, start_column): 1}
    out = 0
    for _ in range(max_move):
        nxt = {}
        for (r, c), w in count.items():
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < m and 0 <= nc < n:
                    nxt[(nr, nc)] = (nxt.get((nr, nc), 0) + w) % MOD
                else:
                    out = (out + w) % MOD
        count = nxt
    return out


# ================================================================== 1269. Number of Ways to Stay in the Same Place After Some Steps (Hard)
# https://leetcode.com/problems/number-of-ways-to-stay-in-the-same-place-after-some-steps/
# Pattern: Dynamic programming over position, capped at steps / 2 + 1 cells
# Idea: Each step you may go left, go right or stay. Keep the number of ways to be at each position.
# You can never usefully go further than steps / 2 cells, which keeps the array small even when the
# corridor is huge.

def num_ways_stay(steps, arr_len):
    MOD = 10 ** 9 + 7
    width = min(arr_len, steps // 2 + 1)
    ways = [1] + [0] * (width - 1)
    for _ in range(steps):
        nxt = [0] * width
        for i in range(width):
            total = ways[i]
            if i > 0:
                total += ways[i - 1]
            if i + 1 < width:
                total += ways[i + 1]
            nxt[i] = total % MOD
        ways = nxt
    return ways[0]


if __name__ == "__main__":
    results = []
    results.append(check("657. Robot Return to Origin", [('judge_circle("UD")', True), ('judge_circle("LL")', False)]))
    results.append(check("70. Climbing Stairs", [('climb_stairs(2)', 2), ('climb_stairs(3)', 3), ('climb_stairs(10)', 89)]))
    results.append(check("874. Walking Robot Simulation", [('robot_sim([4, -1, 3], [])', 25), ('robot_sim([4, -1, 4, -2, 4], [[2, 4]])', 65), ('robot_sim([6, -1, -1, 6], [])', 36)]))
    results.append(check("2400. Number of Ways to Reach a Position After Exactly k Steps", [('number_of_ways(1, 2, 3)', 3), ('number_of_ways(2, 5, 10)', 0)]))
    results.append(check("576. Out of Boundary Paths", [('find_paths(2, 2, 2, 0, 0)', 6), ('find_paths(1, 3, 3, 0, 1)', 12)]))
    results.append(check("1269. Number of Ways to Stay in the Same Place After Some Steps", [('num_ways_stay(3, 2)', 4), ('num_ways_stay(2, 4)', 2), ('num_ways_stay(4, 2)', 8), ('num_ways_stay(27, 7)', 127784505)]))
    if all(results):
        print("Every solution passes its tests.")
