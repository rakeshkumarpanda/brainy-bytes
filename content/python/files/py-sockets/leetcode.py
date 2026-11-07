# 1.2 Sockets, TCP and UDP: under HTTP
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


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


# ================================================================== 190. Reverse Bits (Easy)
# https://leetcode.com/problems/reverse-bits/
# Pattern: Take the last bit, push it in from the right
# Idea: Byte order and bit order matter on the wire. Take the lowest bit of n 32 times and add it to
# the result from the other end.

def reverse_bits(n):
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result


# ================================================================== 1971. Find if Path Exists in Graph (Easy)
# https://leetcode.com/problems/find-if-path-exists-in-graph/
# Pattern: Breadth first search from the source
# Idea: Can a packet get from one computer to another? Keep a set of visited computers and a queue
# of computers to visit.

from collections import deque


def valid_path(n, edges, source, destination):
    links = {node: [] for node in range(n)}
    for a, b in edges:
        links[a].append(b)
        links[b].append(a)
    seen = {source}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        if node == destination:
            return True
        for other in links[node]:
            if other not in seen:
                seen.add(other)
                queue.append(other)
    return False


# ================================================================== 2073. Time Needed to Buy Tickets (Easy)
# https://leetcode.com/problems/time-needed-to-buy-tickets/
# Pattern: Count what each person buys before k is done
# Idea: A queue served in turns, like a server that sends one piece to each client in turn. People
# before k buy at most tickets[k], people after k at most tickets[k] minus 1.

def time_required_to_buy(tickets, k):
    total = 0
    for i, wanted in enumerate(tickets):
        if i <= k:
            total += min(wanted, tickets[k])
        else:
            total += min(wanted, tickets[k] - 1)
    return total


# ================================================================== 743. Network Delay Time (Medium)
# https://leetcode.com/problems/network-delay-time/
# Pattern: Dijkstra with a heap
# Idea: A signal spreads from computer k over links with delays. Dijkstra finds the fastest time to
# each computer, and the answer is the slowest of those.

import heapq


def network_delay_time(times, n, k):
    links = {node: [] for node in range(1, n + 1)}
    for a, b, delay in times:
        links[a].append((b, delay))
    best = {}
    heap = [(0, k)]
    while heap:
        time, node = heapq.heappop(heap)
        if node in best:
            continue
        best[node] = time
        for other, delay in links[node]:
            if other not in best:
                heapq.heappush(heap, (time + delay, other))
    return max(best.values()) if len(best) == n else -1


# ================================================================== 1319. Number of Operations to Make Network Connected (Medium)
# https://leetcode.com/problems/number-of-operations-to-make-network-connected/
# Pattern: Union find counts the groups
# Idea: You need at least n minus 1 cables. If there are enough, the answer is the number of
# separate groups minus 1.

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
        root_a, root_b = find(a), find(b)
        if root_a != root_b:
            parent[root_a] = root_b
            groups -= 1
    return groups - 1


# ================================================================== 1514. Path with Maximum Probability (Medium)
# https://leetcode.com/problems/path-with-maximum-probability/
# Pattern: Dijkstra on the largest product
# Idea: Each link delivers a packet with some probability. Use a heap of negative probabilities so
# the most likely path comes out first.

import heapq


def max_probability(n, edges, succ_prob, start, end):
    links = {node: [] for node in range(n)}
    for (a, b), p in zip(edges, succ_prob):
        links[a].append((b, p))
        links[b].append((a, p))
    done = set()
    heap = [(-1.0, start)]
    while heap:
        neg_p, node = heapq.heappop(heap)
        if node == end:
            return -neg_p
        if node in done:
            continue
        done.add(node)
        for other, p in links[node]:
            if other not in done:
                heapq.heappush(heap, (neg_p * p, other))
    return 0.0


# ================================================================== 787. Cheapest Flights Within K Stops (Medium)
# https://leetcode.com/problems/cheapest-flights-within-k-stops/
# Pattern: Bellman Ford for k + 1 rounds
# Idea: Like a packet with a hop limit (TTL). Each round allows one more flight. Copy the prices
# first so one round uses only one more flight.

def find_cheapest_price(n, flights, src, dst, k):
    INF = float("inf")
    price = [INF] * n
    price[src] = 0
    for _ in range(k + 1):
        new_price = price[:]
        for a, b, cost in flights:
            if price[a] + cost < new_price[b]:
                new_price[b] = price[a] + cost
        price = new_price
    return price[dst] if price[dst] < INF else -1


# ================================================================== 1615. Maximal Network Rank (Medium)
# https://leetcode.com/problems/maximal-network-rank/
# Pattern: Degrees of both cities, minus 1 if they are linked
# Idea: The rank of two cities is the number of roads touching either one. Try every pair and do not
# count a shared road twice.

def maximal_network_rank(n, roads):
    degree = [0] * n
    linked = set()
    for a, b in roads:
        degree[a] += 1
        degree[b] += 1
        linked.add((a, b))
        linked.add((b, a))
    best = 0
    for a in range(n):
        for b in range(a + 1, n):
            rank = degree[a] + degree[b] - (1 if (a, b) in linked else 0)
            best = max(best, rank)
    return best


# ================================================================== 1192. Critical Connections in a Network (Hard)
# https://leetcode.com/problems/critical-connections-in-a-network/
# Pattern: Tarjan: discovery time and lowest reachable time
# Idea: A cable is critical if cutting it splits the network. In a depth first search, the link to a
# child is critical when the child cannot reach back above itself.

def critical_connections(n, connections):
    links = {node: [] for node in range(n)}
    for a, b in connections:
        links[a].append(b)
        links[b].append(a)
    order = [-1] * n
    low = [0] * n
    found = []
    counter = 0
    for root in range(n):
        if order[root] != -1:
            continue
        order[root] = low[root] = counter
        counter += 1
        stack = [(root, -1, iter(links[root]))]
        while stack:
            node, parent, children = stack[-1]
            moved = False
            for child in children:
                if child == parent:
                    continue
                if order[child] == -1:
                    order[child] = low[child] = counter
                    counter += 1
                    stack.append((child, node, iter(links[child])))
                    moved = True
                    break
                low[node] = min(low[node], order[child])
            if moved:
                continue
            stack.pop()
            if parent != -1:
                low[parent] = min(low[parent], low[node])
                if low[node] > order[parent]:
                    found.append(sorted([parent, node]))
    return sorted(found)


# ================================================================== 1579. Remove Max Number of Edges to Keep Graph Fully Traversable (Hard)
# https://leetcode.com/problems/remove-max-number-of-edges-to-keep-graph-fully-traversable/
# Pattern: Two union finds, shared edges first
# Idea: Use the edges both Alice and Bob can use first, then each person's own edges. Every edge
# that joins nothing new can be removed.

class Groups:
    def __init__(self, n):
        self.parent = list(range(n + 1))
        self.count = n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def join(self, a, b):
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False
        self.parent[root_a] = root_b
        self.count -= 1
        return True


def max_num_edges_to_remove(n, edges):
    alice, bob = Groups(n), Groups(n)
    used = 0
    for kind, a, b in edges:
        if kind == 3:
            joined_a = alice.join(a, b)
            joined_b = bob.join(a, b)
            if joined_a or joined_b:
                used += 1
    for kind, a, b in edges:
        if kind == 1 and alice.join(a, b):
            used += 1
        elif kind == 2 and bob.join(a, b):
            used += 1
    if alice.count != 1 or bob.count != 1:
        return -1
    return len(edges) - used


if __name__ == "__main__":
    results = []
    results.append(check("190. Reverse Bits", [('reverse_bits(43261596)', 964176192), ('reverse_bits(4294967293)', 3221225471)]))
    results.append(check("1971. Find if Path Exists in Graph", [('valid_path(3, [[0, 1], [1, 2], [2, 0]], 0, 2)', True), ('valid_path(6, [[0, 1], [0, 2], [3, 5], [5, 4], [4, 3]], 0, 5)', False)]))
    results.append(check("2073. Time Needed to Buy Tickets", [('time_required_to_buy([2, 3, 2], 2)', 6), ('time_required_to_buy([5, 1, 1, 1], 0)', 8)]))
    results.append(check("743. Network Delay Time", [('network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2)', 2), ('network_delay_time([[1, 2, 1]], 2, 1)', 1), ('network_delay_time([[1, 2, 1]], 2, 2)', -1)]))
    results.append(check("1319. Number of Operations to Make Network Connected", [('make_connected(4, [[0, 1], [0, 2], [1, 2]])', 1), ('make_connected(6, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3]])', 2), ('make_connected(6, [[0, 1], [0, 2], [0, 3], [1, 2]])', -1)]))
    results.append(check("1514. Path with Maximum Probability", [('max_probability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.2], 0, 2)', 0.25), ('max_probability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.3], 0, 2)', 0.3), ('max_probability(3, [[0, 1]], [0.5], 0, 2)', 0.0)]))
    results.append(check("787. Cheapest Flights Within K Stops", [('find_cheapest_price(4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1)', 700), ('find_cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1)', 200), ('find_cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0)', 500)]))
    results.append(check("1615. Maximal Network Rank", [('maximal_network_rank(4, [[0, 1], [0, 3], [1, 2], [1, 3]])', 4), ('maximal_network_rank(5, [[0, 1], [0, 3], [1, 2], [1, 3], [2, 3], [2, 4]])', 5), ('maximal_network_rank(8, [[0, 1], [1, 2], [2, 3], [2, 4], [5, 6], [5, 7]])', 5)]))
    results.append(check("1192. Critical Connections in a Network", [('critical_connections(4, [[0, 1], [1, 2], [2, 0], [1, 3]])', [[1, 3]]), ('critical_connections(2, [[0, 1]])', [[0, 1]]), ('critical_connections(5, [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4]])', [[2, 3], [3, 4]])]))
    results.append(check("1579. Remove Max Number of Edges to Keep Graph Fully Traversable", [('max_num_edges_to_remove(4, [[3, 1, 2], [3, 2, 3], [1, 1, 3], [1, 2, 4], [1, 1, 2], [2, 3, 4]])', 2), ('max_num_edges_to_remove(4, [[3, 1, 2], [3, 2, 3], [1, 1, 4], [2, 1, 4]])', 0), ('max_num_edges_to_remove(4, [[3, 2, 3], [1, 1, 2], [2, 3, 4]])', -1)]))
    if all(results):
        print("Every solution passes its tests.")
