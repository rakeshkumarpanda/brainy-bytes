# 3.3 RL in practice: models, offline data and RLHF
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


# ================================================================== 997. Find the Town Judge (Easy)
# https://leetcode.com/problems/find-the-town-judge/
# Pattern: Count trust given and trust received
# Idea: The judge is trusted by everyone else and trusts nobody, so their score of received minus
# given is n − 1. Turning many pairwise statements into one score per person is what a reward model
# does with preference pairs.

def find_judge(n, trust):
    score = [0] * (n + 1)
    for a, b in trust:
        score[a] -= 1
        score[b] += 1
    for person in range(1, n + 1):
        if score[person] == n - 1:
            return person
    return -1


# ================================================================== 207. Course Schedule (Medium)
# https://leetcode.com/problems/course-schedule/
# Pattern: Topological sort: repeatedly take courses with no remaining prerequisites
# Idea: Count each course’s prerequisites and start with those at zero. Taking a course frees the
# courses that depend on it. If some course is never freed, there is a cycle. Ordering steps so that
# each comes after what it needs is the heart of planning.

from collections import deque


def can_finish(num_courses, prerequisites):
    need = [0] * num_courses
    unlocks = [[] for _ in range(num_courses)]
    for course, pre in prerequisites:
        need[course] += 1
        unlocks[pre].append(course)
    q = deque(c for c in range(num_courses) if need[c] == 0)
    done = 0
    while q:
        c = q.popleft()
        done += 1
        for nxt in unlocks[c]:
            need[nxt] -= 1
            if need[nxt] == 0:
                q.append(nxt)
    return done == num_courses


# ================================================================== 2115. Find All Possible Recipes from Given Supplies (Medium)
# https://leetcode.com/problems/find-all-possible-recipes-from-given-supplies/
# Pattern: Topological sort where recipes become supplies
# Idea: Treat each recipe as waiting for its ingredients. When an ingredient becomes available,
# reduce the count of every recipe that needs it, and a recipe with nothing missing becomes a new
# supply. Building complex actions from simpler ones is how hierarchical planners work.

from collections import defaultdict, deque


def find_all_recipes(recipes, ingredients, supplies):
    missing = {r: len(ing) for r, ing in zip(recipes, ingredients)}
    needed_by = defaultdict(list)
    for r, ing in zip(recipes, ingredients):
        for item in ing:
            needed_by[item].append(r)
    q = deque(supplies)
    made = []
    while q:
        item = q.popleft()
        for r in needed_by[item]:
            missing[r] -= 1
            if missing[r] == 0:
                made.append(r)
                q.append(r)
    return sorted(made)


# ================================================================== 1557. Minimum Number of Vertices to Reach All Nodes (Medium)
# https://leetcode.com/problems/minimum-number-of-vertices-to-reach-all-nodes/
# Pattern: Every node with no incoming edge must be a start
# Idea: In a directed acyclic graph, a node nobody points to can only be reached by starting there,
# and those nodes reach everything else. Knowing which states can be reached from which is the first
# question a planner asks of its model.

def find_smallest_set_of_vertices(n, edges):
    has_in = [False] * n
    for _, b in edges:
        has_in[b] = True
    return [v for v in range(n) if not has_in[v]]


# ================================================================== 773. Sliding Puzzle (Hard)
# https://leetcode.com/problems/sliding-puzzle/
# Pattern: Breadth first search over board states
# Idea: Write the 2 by 3 board as a string, find the blank, and swap it with each neighbour to get
# the next states. Breadth first search from the start finds the fewest moves. With an exact model
# of the puzzle, planning by search needs no learning at all.

from collections import deque


def sliding_puzzle(board):
    start = "".join(str(x) for row in board for x in row)
    goal = "123450"
    nbrs = {0: (1, 3), 1: (0, 2, 4), 2: (1, 5), 3: (0, 4), 4: (1, 3, 5), 5: (2, 4)}
    seen = {start}
    q = deque([(start, 0)])
    while q:
        s, d = q.popleft()
        if s == goal:
            return d
        z = s.index("0")
        for k in nbrs[z]:
            t = list(s)
            t[z], t[k] = t[k], t[z]
            t = "".join(t)
            if t not in seen:
                seen.add(t)
                q.append((t, d + 1))
    return -1


if __name__ == "__main__":
    results = []
    results.append(check("997. Find the Town Judge", [('find_judge(2, [[1, 2]])', 2), ('find_judge(3, [[1, 3], [2, 3]])', 3), ('find_judge(3, [[1, 3], [2, 3], [3, 1]])', -1)]))
    results.append(check("207. Course Schedule", [('can_finish(2, [[1, 0]])', True), ('can_finish(2, [[1, 0], [0, 1]])', False), ('can_finish(4, [[1, 0], [2, 1], [3, 2]])', True)]))
    results.append(check("2115. Find All Possible Recipes from Given Supplies", [('find_all_recipes(["bread"], [["yeast", "flour"]], ["yeast", "flour", "corn"])', ['bread']), ('find_all_recipes(["bread", "sandwich"], [["yeast", "flour"], ["bread", "meat"]], ["yeast", "flour", "meat"])', ['bread', 'sandwich']), ('find_all_recipes(["bread"], [["yeast", "flour"]], ["yeast"])', [])]))
    results.append(check("1557. Minimum Number of Vertices to Reach All Nodes", [('find_smallest_set_of_vertices(6, [[0, 1], [0, 2], [2, 5], [3, 4], [4, 2]])', [0, 3]), ('find_smallest_set_of_vertices(5, [[0, 1], [2, 1], [3, 1], [1, 4], [2, 4]])', [0, 2, 3])]))
    results.append(check("773. Sliding Puzzle", [('sliding_puzzle([[1, 2, 3], [4, 0, 5]])', 1), ('sliding_puzzle([[1, 2, 3], [5, 4, 0]])', -1), ('sliding_puzzle([[4, 1, 2], [5, 0, 3]])', 5)]))
    if all(results):
        print("Every solution passes its tests.")
