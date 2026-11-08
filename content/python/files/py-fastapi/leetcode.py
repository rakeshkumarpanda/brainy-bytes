# 5.2 FastAPI: fast, typed APIs with automatic docs
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


# ================================================================== 1122. Relative Sort Array (Easy)
# https://leetcode.com/problems/relative-sort-array/
# Pattern: Sort with a key: (position in the order, value)
# Idea: Like an API that lists fields in a fixed order and the rest A to Z after them. A dict gives
# each wanted value its position, and the sort key puts the others at the end.

def relative_sort_array(arr1, arr2):
    rank = {value: i for i, value in enumerate(arr2)}
    return sorted(arr1, key=lambda value: (rank.get(value, len(arr2)), value))


# ================================================================== 1200. Minimum Absolute Difference (Easy)
# https://leetcode.com/problems/minimum-absolute-difference/
# Pattern: Sort, then only neighbours matter
# Idea: After sorting, the closest pair is always next to each other, so one pass finds the smallest
# gap and the pairs that have it.

def minimum_abs_difference(arr):
    arr = sorted(arr)
    best = min(b - a for a, b in zip(arr, arr[1:]))
    return [[a, b] for a, b in zip(arr, arr[1:]) if b - a == best]


# ================================================================== 1287. Element Appearing More Than 25% In Sorted Array (Easy)
# https://leetcode.com/problems/element-appearing-more-than-25-in-sorted-array/
# Pattern: Compare with the item a quarter further on
# Idea: In a sorted list a value that fills more than a quarter must still be there a quarter of the
# length later. One loop, no counting.

def find_special_integer(arr):
    step = len(arr) // 4
    for i in range(len(arr) - step):
        if arr[i] == arr[i + step]:
            return arr[i]
    return arr[0]


# ================================================================== 1013. Partition Array Into Three Parts With Equal Sum (Easy)
# https://leetcode.com/problems/partition-array-into-three-parts-with-equal-sum/
# Pattern: Walk once and count parts that reach a third
# Idea: The total must split into three equal parts. Add numbers from the left and count each time
# the running sum reaches one third, then start again.

def can_three_parts_equal_sum(arr):
    total = sum(arr)
    if total % 3 != 0:
        return False
    target = total // 3
    parts = 0
    running = 0
    for value in arr:
        running += value
        if running == target:
            parts += 1
            running = 0
    return parts >= 3


# ================================================================== 1237. Find Positive Integer Solution for a Given Equation (Medium)
# https://leetcode.com/problems/find-positive-integer-solution-for-a-given-equation/
# Pattern: Two pointers on a function you can only call
# Idea: You can only call the hidden function f(x, y), like a remote API that you want to call as
# few times as possible. f grows with x and with y, so start at x = 1 and y = 1000 and move one of
# them each call.

class CustomFunction:
    """Stands in for LeetCode's hidden function. Each id is one increasing formula."""
    FORMULAS = {1: lambda x, y: x + y, 2: lambda x, y: x * y}

    def __init__(self, function_id):
        self.f = self.FORMULAS[function_id]
        self.calls = 0

    def f_call(self, x, y):
        self.calls += 1
        return self.f(x, y)


def find_solution(custom, z):
    result = []
    x, y = 1, 1000
    while x <= 1000 and y >= 1:
        value = custom.f_call(x, y)
        if value == z:
            result.append([x, y])
            x += 1
            y -= 1
        elif value < z:
            x += 1
        else:
            y -= 1
    return result


# ================================================================== 2069. Walking Robot Simulation II (Medium)
# https://leetcode.com/problems/walking-robot-simulation-ii/
# Pattern: Moves wrap around the border, so use the remainder
# Idea: The robot only walks around the edge of the grid. One full lap is a fixed number of steps,
# so a huge step count shrinks to steps % lap, like a cursor that wraps around.

class Robot:
    MOVES = {"East": (1, 0, "North"), "North": (0, 1, "West"), "West": (-1, 0, "South"), "South": (0, -1, "East")}

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.facing = "East"
        self.lap = 2 * (width + height) - 4

    def step(self, num):
        num %= self.lap
        if num == 0:
            num = self.lap                  # a full lap ends facing a new way at the start corner
        while num > 0:
            dx, dy, turn = self.MOVES[self.facing]
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                self.x, self.y = nx, ny
                num -= 1
            else:
                self.facing = turn

    def getPos(self):
        return [self.x, self.y]

    def getDir(self):
        return self.facing


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 1801. Number of Orders in the Backlog (Medium)
# https://leetcode.com/problems/number-of-orders-in-the-backlog/
# Pattern: Two heaps: highest buy and lowest sell
# Idea: An order book API: a buy matches the cheapest sell, a sell matches the highest buy. A min
# heap of sells and a max heap of buys (negated prices) give the best match at once.

import heapq


def get_number_of_backlog_orders(orders):
    buys = []                                # (-price, amount), so the highest price is on top
    sells = []                               # (price, amount)
    for price, amount, kind in orders:
        if kind == 0:                        # a buy order
            while amount and sells and sells[0][0] <= price:
                sell_price, sell_amount = heapq.heappop(sells)
                used = min(amount, sell_amount)
                amount -= used
                if sell_amount > used:
                    heapq.heappush(sells, (sell_price, sell_amount - used))
            if amount:
                heapq.heappush(buys, (-price, amount))
        else:                                # a sell order
            while amount and buys and -buys[0][0] >= price:
                buy_price, buy_amount = heapq.heappop(buys)
                used = min(amount, buy_amount)
                amount -= used
                if buy_amount > used:
                    heapq.heappush(buys, (buy_price, buy_amount - used))
            if amount:
                heapq.heappush(sells, (price, amount))
    return sum(amount for _, amount in buys + sells) % (10 ** 9 + 7)


# ================================================================== 1032. Stream of Characters (Hard)
# https://leetcode.com/problems/stream-of-characters/
# Pattern: A trie of reversed words, checked from the newest letter
# Idea: Like a WebSocket that gets one letter at a time and must say at once if the latest letters
# end a banned word. Store the words backwards in a trie and walk it from the newest letter back.

class StreamChecker:
    def __init__(self, words):
        self.trie = {}
        self.longest = 0
        for word in words:
            node = self.trie
            for ch in reversed(word):
                node = node.setdefault(ch, {})
            node["$"] = True
            self.longest = max(self.longest, len(word))
        self.recent = []

    def query(self, letter):
        self.recent.append(letter)
        if len(self.recent) > self.longest:
            self.recent.pop(0)
        node = self.trie
        for ch in reversed(self.recent):
            if ch not in node:
                return False
            node = node[ch]
            if "$" in node:
                return True
        return False


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 2642. Design Graph With Shortest Path Calculator (Hard)
# https://leetcode.com/problems/design-graph-with-shortest-path-calculator/
# Pattern: Dijkstra with a heap on every query
# Idea: Like a gateway that finds the cheapest chain of services. Keep the edges in a dict of lists,
# let addEdge append, and run Dijkstra with a heap for each shortestPath question.

import heapq


class Graph:
    def __init__(self, n, edges):
        self.out = {node: [] for node in range(n)}
        for edge in edges:
            self.addEdge(edge)

    def addEdge(self, edge):
        start, end, cost = edge
        self.out[start].append((end, cost))

    def shortestPath(self, node1, node2):
        best = {node1: 0}
        heap = [(0, node1)]
        while heap:
            dist, node = heapq.heappop(heap)
            if node == node2:
                return dist
            if dist > best[node]:
                continue
            for nxt, cost in self.out[node]:
                if dist + cost < best.get(nxt, float("inf")):
                    best[nxt] = dist + cost
                    heapq.heappush(heap, (dist + cost, nxt))
        return -1


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 2286. Booking Concert Tickets in Groups (Hard)
# https://leetcode.com/problems/booking-concert-tickets-in-groups/
# Pattern: A segment tree with the max and the sum of free seats per range
# Idea: A booking API must answer "first row with k free seats together" and "book k scattered
# seats" fast. A segment tree keeps the most free seats in a row and the total free seats for every
# range of rows.

class BookMyShow:
    def __init__(self, n, m):
        self.n = n
        self.m = m
        size = 1
        while size < n:
            size *= 2
        self.size = size
        self.most = [0] * (2 * size)          # the most free seats in one row of the range
        self.total = [0] * (2 * size)         # all free seats of the range
        for row in range(n):
            self.most[size + row] = m
            self.total[size + row] = m
        for i in range(size - 1, 0, -1):
            self.pull(i)
        self.first_free = 0                   # rows before this one are full

    def pull(self, i):
        self.most[i] = max(self.most[2 * i], self.most[2 * i + 1])
        self.total[i] = self.total[2 * i] + self.total[2 * i + 1]

    def set_free(self, row, free):
        i = self.size + row
        self.most[i] = free
        self.total[i] = free
        i //= 2
        while i:
            self.pull(i)
            i //= 2

    def first_row_with(self, k, max_row):
        """The first row up to max_row with at least k free seats, or -1."""
        if self.most[1] < k:
            return -1
        i = 1
        while i < self.size:
            i = 2 * i if self.most[2 * i] >= k else 2 * i + 1
        row = i - self.size
        return row if row <= max_row else -1

    def free_up_to(self, max_row, i=1, low=0, high=None):
        if high is None:
            high = self.size - 1
        if low > max_row:
            return 0
        if high <= max_row:
            return self.total[i]
        middle = (low + high) // 2
        return self.free_up_to(max_row, 2 * i, low, middle) + self.free_up_to(max_row, 2 * i + 1, middle + 1, high)

    def gather(self, k, maxRow):
        row = self.first_row_with(k, maxRow)
        if row == -1:
            return []
        used = self.m - self.most[self.size + row]
        self.set_free(row, self.most[self.size + row] - k)
        return [row, used]

    def scatter(self, k, maxRow):
        if self.free_up_to(maxRow) < k:
            return False
        row = self.first_free
        while k > 0:
            free = self.total[self.size + row]
            take = min(free, k)
            self.set_free(row, free - take)
            k -= take
            if self.total[self.size + row] == 0:
                row += 1
        self.first_free = row
        return True


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


if __name__ == "__main__":
    results = []
    results.append(check("1122. Relative Sort Array", [('relative_sort_array([2, 3, 1, 3, 2, 4, 6, 7, 9, 2, 19], [2, 1, 4, 3, 9, 6])', [2, 2, 2, 1, 4, 3, 3, 9, 6, 7, 19]), ('relative_sort_array([28, 6, 22, 8, 44, 17], [22, 28, 8, 6])', [22, 28, 8, 6, 17, 44])]))
    results.append(check("1200. Minimum Absolute Difference", [('minimum_abs_difference([4, 2, 1, 3])', [[1, 2], [2, 3], [3, 4]]), ('minimum_abs_difference([1, 3, 6, 10, 15])', [[1, 3]]), ('minimum_abs_difference([3, 8, -10, 23, 19, -4, -14, 27])', [[-14, -10], [19, 23], [23, 27]])]))
    results.append(check("1287. Element Appearing More Than 25% In Sorted Array", [('find_special_integer([1, 2, 2, 6, 6, 6, 6, 7, 10])', 6), ('find_special_integer([1, 1])', 1)]))
    results.append(check("1013. Partition Array Into Three Parts With Equal Sum", [('can_three_parts_equal_sum([0, 2, 1, -6, 6, -7, 9, 1, 2, 0, 1])', True), ('can_three_parts_equal_sum([0, 2, 1, -6, 6, 7, 9, -1, 2, 0, 1])', False), ('can_three_parts_equal_sum([3, 3, 6, 5, -2, 2, 5, 1, -9, 4])', True)]))
    results.append(check("1237. Find Positive Integer Solution for a Given Equation", [('find_solution(CustomFunction(1), 5)', [[1, 4], [2, 3], [3, 2], [4, 1]]), ('find_solution(CustomFunction(2), 5)', [[1, 5], [5, 1]]), ('(lambda c: [len(find_solution(c, 5)) > 0, c.calls <= 2000])(CustomFunction(1))', [True, True])]))
    results.append(check("2069. Walking Robot Simulation II", [('play(Robot, ["Robot", "step", "step", "getPos", "getDir", "step", "step", "step", "getPos", "getDir"], [[6, 3], [2], [2], [], [], [2], [1], [4], [], []])', [None, None, None, [4, 0], 'East', None, None, None, [1, 2], 'West'])]))
    results.append(check("1801. Number of Orders in the Backlog", [('get_number_of_backlog_orders([[10, 5, 0], [15, 2, 1], [25, 1, 1], [30, 4, 0]])', 6), ('get_number_of_backlog_orders([[7, 1000000000, 1], [15, 3, 0], [5, 999999995, 0], [5, 1, 1]])', 999999984)]))
    results.append(check("1032. Stream of Characters", [('play(StreamChecker, ["StreamChecker"] + ["query"] * 12, [[["cd", "f", "kl"]]] + [[c] for c in "abcdefghijkl"])', [None, False, False, False, True, False, True, False, False, False, False, False, True])]))
    results.append(check("2642. Design Graph With Shortest Path Calculator", [('play(Graph, ["Graph", "shortestPath", "shortestPath", "addEdge", "shortestPath"], [[4, [[0, 2, 5], [0, 1, 2], [1, 2, 1], [3, 0, 3]]], [3, 2], [0, 3], [[1, 3, 4]], [0, 3]])', [None, 6, -1, None, 6])]))
    results.append(check("2286. Booking Concert Tickets in Groups", [('play(BookMyShow, ["BookMyShow", "gather", "gather", "scatter", "scatter"], [[2, 5], [4, 0], [2, 0], [5, 1], [5, 1]])', [None, [0, 0], [], True, False])]))
    if all(results):
        print("Every solution passes its tests.")
