# 3.2 Policy gradients, actor critic and PPO
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


# ================================================================== 2016. Maximum Difference Between Increasing Elements (Easy)
# https://leetcode.com/problems/maximum-difference-between-increasing-elements/
# Pattern: Track the smallest value seen so far
# Idea: Walk left to right, keep the minimum so far, and record the largest value minus that minimum
# when it is positive. Comparing a value with a reference level is what an advantage does: it
# compares a return with the baseline.

def maximum_difference(nums):
    best, low = -1, nums[0]
    for x in nums[1:]:
        if x > low:
            best = max(best, x - low)
        low = min(low, x)
    return best


# ================================================================== 55. Jump Game (Medium)
# https://leetcode.com/problems/jump-game/
# Pattern: Keep the furthest index you can reach
# Idea: Scan once, updating the furthest reachable index. If you ever stand beyond it, you are
# stuck. Like the short corridor, whether you can reach the goal depends on which moves are allowed
# in each cell.

def can_jump(nums):
    reach = 0
    for i, n in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + n)
    return True


# ================================================================== 45. Jump Game II (Medium)
# https://leetcode.com/problems/jump-game-ii/
# Pattern: Greedy breadth first search by layers
# Idea: Treat each jump as a layer: from the current range find the furthest next reach, and count a
# jump each time you pass the end of the range. The answer is the shortest number of moves, the same
# as minus the best return when every move costs 1.

def jump(nums):
    jumps, end, far = 0, 0, 0
    for i in range(len(nums) - 1):
        far = max(far, i + nums[i])
        if i == end:
            jumps += 1
            end = far
    return jumps


# ================================================================== 1696. Jump Game VI (Medium)
# https://leetcode.com/problems/jump-game-vi/
# Pattern: Dynamic programming with a sliding window maximum
# Idea: The best score at i is nums[i] plus the best score among the previous k cells. A deque of
# indices with decreasing scores gives that maximum in constant time. Adding the reward now to the
# best value reachable next is a Bellman backup.

from collections import deque


def max_result(nums, k):
    score = [0] * len(nums)
    score[0] = nums[0]
    dq = deque([0])
    for i in range(1, len(nums)):
        while dq[0] < i - k:
            dq.popleft()
        score[i] = nums[i] + score[dq[0]]
        while dq and score[dq[-1]] <= score[i]:
            dq.pop()
        dq.append(i)
    return score[-1]


# ================================================================== 1345. Jump Game IV (Hard)
# https://leetcode.com/problems/jump-game-iv/
# Pattern: Breadth first search, and clear each value’s list after first use
# Idea: From index i you may step to i − 1, i + 1 or any index with the same value. Breadth first
# search finds the fewest steps. Emptying a value’s index list once used stops the search from
# scanning it again. Shortcuts that connect distant states make credit travel fast, which is why the
# same idea appears in options and skills in hierarchical RL.

from collections import defaultdict, deque


def min_jumps(arr):
    n = len(arr)
    same = defaultdict(list)
    for i, v in enumerate(arr):
        same[v].append(i)
    seen = {0}
    q = deque([(0, 0)])
    while q:
        i, d = q.popleft()
        if i == n - 1:
            return d
        for j in same[arr[i]] + [i - 1, i + 1]:
            if 0 <= j < n and j not in seen:
                seen.add(j)
                q.append((j, d + 1))
        same[arr[i]] = []
    return -1


if __name__ == "__main__":
    results = []
    results.append(check("2016. Maximum Difference Between Increasing Elements", [('maximum_difference([7, 1, 5, 4])', 4), ('maximum_difference([9, 4, 3, 2])', -1), ('maximum_difference([1, 5, 2, 10])', 9)]))
    results.append(check("55. Jump Game", [('can_jump([2, 3, 1, 1, 4])', True), ('can_jump([3, 2, 1, 0, 4])', False), ('can_jump([0])', True)]))
    results.append(check("45. Jump Game II", [('jump([2, 3, 1, 1, 4])', 2), ('jump([2, 3, 0, 1, 4])', 2), ('jump([1])', 0)]))
    results.append(check("1696. Jump Game VI", [('max_result([1, -1, -2, 4, -7, 3], 2)', 7), ('max_result([10, -5, -2, 4, 0, 3], 3)', 17), ('max_result([1, -5, -20, 4, -1, 3, -6, -3], 2)', 0)]))
    results.append(check("1345. Jump Game IV", [('min_jumps([100, -23, -23, 404, 100, 23, 23, 23, 3, 404])', 3), ('min_jumps([7])', 0), ('min_jumps([7, 6, 9, 6, 9, 6, 9, 7])', 1)]))
    if all(results):
        print("Every solution passes its tests.")
