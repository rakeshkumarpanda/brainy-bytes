# 1.2 Backpropagation and automatic differentiation
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
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


# ================================================================== 2236. Root Equals Sum of Children (Easy)
# https://leetcode.com/problems/root-equals-sum-of-children/
# Pattern: Compare the root with the sum of its two children
# Idea: One comparison does it. In a computational graph an add node’s value is exactly the sum of
# its inputs, which is why its gradient passes straight through. Our helper builds the three node
# tree from a list.

class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def check_tree(root):
    return root.val == root.left.val + root.right.val


def root_equals_sum(values):
    root = TreeNode(values[0], TreeNode(values[1]), TreeNode(values[2]))
    return check_tree(root)


# ================================================================== 1376. Time Needed to Inform All Employees (Medium)
# https://leetcode.com/problems/time-needed-to-inform-all-employees/
# Pattern: Recursion from the head down, taking the slowest branch
# Idea: Build the tree of who manages whom. The time for a manager is their inform time plus the
# largest time among their reports. Passing a quantity along every path of a tree and combining at
# each node is the shape of both the forward and the backward pass.

from collections import defaultdict


def num_of_minutes(n, head_id, manager, inform_time):
    children = defaultdict(list)
    for e, m in enumerate(manager):
        if m != -1:
            children[m].append(e)

    def time(e):
        return inform_time[e] + max((time(c) for c in children[e]), default=0)

    return time(head_id)


# ================================================================== 1443. Minimum Time to Collect All Apples in a Tree (Medium)
# https://leetcode.com/problems/minimum-time-to-collect-all-apples-in-a-tree/
# Pattern: Post order: a subtree costs 2 per edge if it holds an apple
# Idea: Search depth first. After visiting a child, add its cost plus 2 for the edge there and back,
# but only if the child’s subtree has an apple. Computing children first and combining their results
# on the way back up is exactly the order of the backward pass.

from collections import defaultdict


def min_time(n, edges, has_apple):
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    def dfs(node, parent):
        total = 0
        for nxt in adj[node]:
            if nxt != parent:
                cost = dfs(nxt, node)
                if cost or has_apple[nxt]:
                    total += cost + 2
        return total

    return dfs(0, -1)


# ================================================================== 2192. All Ancestors of a Node in a Directed Acyclic Graph (Medium)
# https://leetcode.com/problems/all-ancestors-of-a-node-in-a-directed-acyclic-graph/
# Pattern: A node’s ancestors are its parents plus their ancestors, memoised
# Idea: Store each node’s parents and compute ancestors recursively with a cache. In a computational
# graph, a value’s ancestors are everything it depends on, and backpropagation sends gradients to
# exactly those nodes.

from collections import defaultdict
from functools import lru_cache


def get_ancestors(n, edges):
    parents = defaultdict(list)
    for a, b in edges:
        parents[b].append(a)

    @lru_cache(maxsize=None)
    def anc(v):
        out = set()
        for p in parents[v]:
            out.add(p)
            out |= anc(p)
        return frozenset(out)

    return [sorted(anc(v)) for v in range(n)]


# ================================================================== 329. Longest Increasing Path in a Matrix (Hard)
# https://leetcode.com/problems/longest-increasing-path-in-a-matrix/
# Pattern: Depth first search with memoisation over a hidden DAG
# Idea: Moving to a strictly larger neighbour can never loop, so the cells form a directed acyclic
# graph. The best path from a cell is 1 plus the best from any larger neighbour, cached so each cell
# is solved once. Reusing stored results for every node of a DAG is what makes backpropagation cost
# about the same as one forward pass.

from functools import lru_cache


def longest_increasing_path(matrix):
    rows, cols = len(matrix), len(matrix[0])

    @lru_cache(maxsize=None)
    def best(r, c):
        out = 1
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > matrix[r][c]:
                out = max(out, 1 + best(nr, nc))
        return out

    return max(best(r, c) for r in range(rows) for c in range(cols))


if __name__ == "__main__":
    results = []
    results.append(check("2236. Root Equals Sum of Children", [('root_equals_sum([10, 4, 6])', True), ('root_equals_sum([5, 3, 1])', False)]))
    results.append(check("1376. Time Needed to Inform All Employees", [('num_of_minutes(1, 0, [-1], [0])', 0), ('num_of_minutes(6, 2, [2, 2, -1, 2, 2, 2], [0, 0, 1, 0, 0, 0])', 1)]))
    results.append(check("1443. Minimum Time to Collect All Apples in a Tree", [('min_time(7, [[0, 1], [0, 2], [1, 4], [1, 5], [2, 3], [2, 6]], [False, False, True, False, True, True, False])', 8), ('min_time(7, [[0, 1], [0, 2], [1, 4], [1, 5], [2, 3], [2, 6]], [False, False, True, False, False, True, False])', 6), ('min_time(7, [[0, 1], [0, 2], [1, 4], [1, 5], [2, 3], [2, 6]], [False, False, False, False, False, False, False])', 0)]))
    results.append(check("2192. All Ancestors of a Node in a Directed Acyclic Graph", [('get_ancestors(8, [[0, 3], [0, 4], [1, 3], [2, 4], [2, 7], [3, 5], [3, 6], [3, 7], [4, 6]])', [[], [], [], [0, 1], [0, 2], [0, 1, 3], [0, 1, 2, 3, 4], [0, 1, 2, 3]])]))
    results.append(check("329. Longest Increasing Path in a Matrix", [('longest_increasing_path([[9, 9, 4], [6, 6, 8], [2, 1, 1]])', 4), ('longest_increasing_path([[3, 4, 5], [3, 2, 6], [2, 2, 1]])', 4), ('longest_increasing_path([[1]])', 1)]))
    if all(results):
        print("Every solution passes its tests.")
