# 1.2 Hierarchical clustering and DBSCAN
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


# ================================================================== 1971. Find if Path Exists in Graph (Easy)
# https://leetcode.com/problems/find-if-path-exists-in-graph/
# Pattern: Union find or a flood fill from the source
# Idea: Join the two ends of every edge with union find, then check whether source and destination
# have the same root. Being in the same connected group is how DBSCAN decides that two core points
# share a cluster.

def valid_path(n, edges, source, destination):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        parent[find(a)] = find(b)
    return find(source) == find(destination)


# ================================================================== 990. Satisfiability of Equality Equations (Medium)
# https://leetcode.com/problems/satisfiability-of-equality-equations/
# Pattern: Merge all equalities first, then test the inequalities
# Idea: Put every pair joined by == into the same group with union find. Then each != must link two
# different groups, or the equations contradict each other.

def equations_possible(equations):
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for e in equations:
        if e[1] == "=":
            parent[find(e[0])] = find(e[3])
    return all(find(e[0]) != find(e[3]) for e in equations if e[1] == "!")


# ================================================================== 684. Redundant Connection (Medium)
# https://leetcode.com/problems/redundant-connection/
# Pattern: The first edge that joins two nodes already in one group
# Idea: Add the edges in order with union find. An edge whose two ends already share a root closes a
# cycle, so it is the answer. Kruskal’s minimum spanning tree, and so single linkage clustering,
# skip exactly these edges.

def find_redundant_connection(edges):
    parent = list(range(len(edges) + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            return [a, b]
        parent[ra] = rb
    return []


# ================================================================== 1319. Number of Operations to Make Network Connected (Medium)
# https://leetcode.com/problems/number-of-operations-to-make-network-connected/
# Pattern: Count the groups, then count the spare cables
# Idea: n computers need at least n − 1 cables, otherwise the answer is −1. With enough cables,
# joining g separate groups takes g − 1 moves.

def make_connected(n, connections):
    if len(connections) < n - 1:
        return -1
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    groups = n
    for a, b in connections:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            groups = groups - 1
    return groups - 1


# ================================================================== 721. Accounts Merge (Medium)
# https://leetcode.com/problems/accounts-merge/
# Pattern: Union the emails inside each account
# Idea: Every email is a node. Join all emails of one account. Emails that end up with the same root
# belong to one person. This is clustering by shared links, just as DBSCAN joins clusters through
# shared core points.

def accounts_merge(accounts):
    parent, owner = {}, {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for acc in accounts:
        name, first = acc[0], acc[1]
        for email in acc[1:]:
            owner[email] = name
            parent[find(email)] = find(first)
    groups = {}
    for email in owner:
        groups.setdefault(find(email), []).append(email)
    return sorted([owner[g[0]]] + sorted(g) for g in groups.values())


# ================================================================== 827. Making A Large Island (Hard)
# https://leetcode.com/problems/making-a-large-island/
# Pattern: Label every island with its size, then try each water cell
# Idea: Flood fill each island and store its size under a new id. For each water cell, add 1 to the
# sizes of the distinct islands around it. One changed cell can bridge two groups, which is exactly
# how single linkage chains clusters together.

def largest_island(grid):
    n = len(grid)
    size = {}
    label = [[0] * n for _ in range(n)]
    next_id = 2
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 1 and label[r][c] == 0:
                stack = [(r, c)]
                label[r][c] = next_id
                count = 0
                while stack:
                    i, j = stack.pop()
                    count = count + 1
                    for a, b in [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]:
                        if 0 <= a < n and 0 <= b < n and grid[a][b] == 1 and label[a][b] == 0:
                            label[a][b] = next_id
                            stack.append((a, b))
                size[next_id] = count
                next_id = next_id + 1
    best = max(size.values(), default=0)
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 0:
                ids = set()
                for a, b in [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]:
                    if 0 <= a < n and 0 <= b < n and label[a][b]:
                        ids.add(label[a][b])
                best = max(best, 1 + sum(size[i] for i in ids))
    return best


if __name__ == "__main__":
    results = []
    results.append(check("1971. Find if Path Exists in Graph", [('valid_path(3, [[0, 1], [1, 2], [2, 0]], 0, 2)', True), ('valid_path(6, [[0, 1], [0, 2], [3, 5], [5, 4], [4, 3]], 0, 5)', False)]))
    results.append(check("990. Satisfiability of Equality Equations", [('equations_possible(["a==b", "b!=a"])', False), ('equations_possible(["a==b", "b==c", "a==c"])', True), ('equations_possible(["a==b", "b!=c", "c==a"])', False)]))
    results.append(check("684. Redundant Connection", [('find_redundant_connection([[1, 2], [1, 3], [2, 3]])', [2, 3]), ('find_redundant_connection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]])', [1, 4])]))
    results.append(check("1319. Number of Operations to Make Network Connected", [('make_connected(4, [[0, 1], [0, 2], [1, 2]])', 1), ('make_connected(6, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3]])', 2), ('make_connected(6, [[0, 1], [0, 2], [0, 3], [1, 2]])', -1)]))
    results.append(check("721. Accounts Merge", [('accounts_merge([["John", "johnsmith@mail.com", "john_newyork@mail.com"], ["John", "johnsmith@mail.com", "john00@mail.com"], ["Mary", "mary@mail.com"], ["John", "johnnybravo@mail.com"]])', [['John', 'john00@mail.com', 'john_newyork@mail.com', 'johnsmith@mail.com'], ['John', 'johnnybravo@mail.com'], ['Mary', 'mary@mail.com']])]))
    results.append(check("827. Making A Large Island", [('largest_island([[1, 0], [0, 1]])', 3), ('largest_island([[1, 1], [1, 0]])', 4), ('largest_island([[1, 1], [1, 1]])', 4)]))
    if all(results):
        print("Every solution passes its tests.")
