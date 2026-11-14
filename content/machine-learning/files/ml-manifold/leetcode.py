# 2.2 Manifold learning: t-SNE, UMAP, MDS and Isomap
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


# ================================================================== 1791. Find Center of Star Graph (Easy)
# https://leetcode.com/problems/find-center-of-star-graph/
# Pattern: The centre appears in the first two edges
# Idea: Every edge touches the centre, so the node shared by the first two edges is the answer.
# Reading structure from a list of edges is the first step of every neighbour graph method.

def find_center(edges):
    a, b = edges[0]
    return a if a in edges[1] else b


# ================================================================== 743. Network Delay Time (Medium)
# https://leetcode.com/problems/network-delay-time/
# Pattern: Dijkstra from the source, answer is the largest distance
# Idea: Run Dijkstra’s algorithm with a heap from node k. If some node is never reached the answer
# is −1, otherwise it is the largest shortest path distance. Isomap runs this same search from every
# point.

import heapq


def network_delay_time(times, n, k):
    graph = {}
    for u, v, w in times:
        graph.setdefault(u, []).append((v, w))
    dist = {}
    heap = [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:
            continue
        dist[u] = d
        for v, w in graph.get(u, []):
            if v not in dist:
                heapq.heappush(heap, (d + w, v))
    return max(dist.values()) if len(dist) == n else -1


# ================================================================== 1334. Find the City With the Smallest Number of Neighbors at a Threshold Distance (Medium)
# https://leetcode.com/problems/find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance/
# Pattern: All pairs shortest paths with Floyd and Warshall
# Idea: Fill a distance table, then for every middle city m relax d[i][j] with d[i][m] + d[m][j].
# Count reachable cities within the threshold for each city and keep the smallest count, breaking
# ties by the larger index. Isomap needs exactly this table of all pairs distances.

def find_the_city(n, edges, distance_threshold):
    INF = float("inf")
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
        d[v][u] = min(d[v][u], w)
    for m in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][m] + d[m][j] < d[i][j]:
                    d[i][j] = d[i][m] + d[m][j]
    best, answer = None, -1
    for i in range(n):
        count = sum(1 for j in range(n) if j != i and d[i][j] <= distance_threshold)
        if best is None or count <= best:
            best, answer = count, i
    return answer


# ================================================================== 1514. Path with Maximum Probability (Medium)
# https://leetcode.com/problems/path-with-maximum-probability/
# Pattern: Dijkstra that multiplies probabilities and keeps the largest
# Idea: Use a max heap on probability. Moving along an edge multiplies the probability, which can
# only shrink it, so the first time you pop the end node you have the best path. t-SNE also works
# with neighbour probabilities on a graph.

import heapq


def max_probability(n, edges, succ_prob, start, end):
    graph = [[] for _ in range(n)]
    for (u, v), p in zip(edges, succ_prob):
        graph[u].append((v, p))
        graph[v].append((u, p))
    best = [0.0] * n
    best[start] = 1.0
    heap = [(-1.0, start)]
    while heap:
        neg, u = heapq.heappop(heap)
        if u == end:
            return -neg
        if -neg < best[u]:
            continue
        for v, p in graph[u]:
            if -neg * p > best[v]:
                best[v] = -neg * p
                heapq.heappush(heap, (-best[v], v))
    return 0.0


# ================================================================== 1631. Path With Minimum Effort (Medium)
# https://leetcode.com/problems/path-with-minimum-effort/
# Pattern: Dijkstra where a path costs its biggest step
# Idea: The effort of a path is its largest height difference. Run Dijkstra with that cost: moving
# to a neighbour costs max(current effort, height difference). Paths through a surface that avoid
# big jumps are what manifold methods look for.

import heapq


def minimum_effort_path(heights):
    rows, cols = len(heights), len(heights[0])
    best = [[float("inf")] * cols for _ in range(rows)]
    best[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        e, r, c = heapq.heappop(heap)
        if (r, c) == (rows - 1, cols - 1):
            return e
        if e > best[r][c]:
            continue
        for a, b in [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]:
            if 0 <= a < rows and 0 <= b < cols:
                ne = max(e, abs(heights[a][b] - heights[r][c]))
                if ne < best[a][b]:
                    best[a][b] = ne
                    heapq.heappush(heap, (ne, a, b))
    return 0


# ================================================================== 882. Reachable Nodes In Subdivided Graph (Hard)
# https://leetcode.com/problems/reachable-nodes-in-subdivided-graph/
# Pattern: Dijkstra on the original nodes, then count partial edges
# Idea: An edge with cnt new nodes has length cnt + 1. Run Dijkstra on the original nodes. Count
# every original node within maxMoves. For each edge, the new nodes reached from each end are the
# moves left there, and together they cannot exceed cnt.

import heapq


def reachable_nodes(edges, max_moves, n):
    graph = [[] for _ in range(n)]
    for u, v, cnt in edges:
        graph[u].append((v, cnt + 1))
        graph[v].append((u, cnt + 1))
    dist = [float("inf")] * n
    dist[0] = 0
    heap = [(0, 0)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    total = sum(1 for d in dist if d <= max_moves)
    for u, v, cnt in edges:
        a = max(0, max_moves - dist[u])
        b = max(0, max_moves - dist[v])
        total = total + min(cnt, a + b)
    return total


if __name__ == "__main__":
    results = []
    results.append(check("1791. Find Center of Star Graph", [('find_center([[1, 2], [2, 3], [4, 2]])', 2), ('find_center([[1, 2], [5, 1], [1, 3], [1, 4]])', 1)]))
    results.append(check("743. Network Delay Time", [('network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2)', 2), ('network_delay_time([[1, 2, 1]], 2, 2)', -1)]))
    results.append(check("1334. Find the City With the Smallest Number of Neighbors at a Threshold Distance", [('find_the_city(4, [[0, 1, 3], [1, 2, 1], [1, 3, 4], [2, 3, 1]], 4)', 3), ('find_the_city(5, [[0, 1, 2], [0, 4, 8], [1, 2, 3], [1, 4, 2], [2, 3, 1], [3, 4, 1]], 2)', 0)]))
    results.append(check("1514. Path with Maximum Probability", [('max_probability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.2], 0, 2)', 0.25), ('max_probability(3, [[0, 1]], [0.5], 0, 2)', 0.0)]))
    results.append(check("1631. Path With Minimum Effort", [('minimum_effort_path([[1, 2, 2], [3, 8, 2], [5, 3, 5]])', 2), ('minimum_effort_path([[1, 2, 3], [3, 8, 4], [5, 3, 5]])', 1)]))
    results.append(check("882. Reachable Nodes In Subdivided Graph", [('reachable_nodes([[0, 1, 10], [0, 2, 1], [1, 2, 2]], 6, 3)', 13), ('reachable_nodes([[0, 1, 4], [1, 2, 6], [0, 2, 8], [1, 3, 1]], 10, 4)', 23)]))
    if all(results):
        print("Every solution passes its tests.")
