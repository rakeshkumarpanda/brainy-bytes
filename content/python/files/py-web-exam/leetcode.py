# 6.2 Web revision exam: HTTP, Flask, Django, FastAPI and security
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


# ================================================================== 1629. Slowest Key (Easy)
# https://leetcode.com/problems/slowest-key/
# Pattern: One pass over the gaps between times
# Idea: Like finding the slowest request in an access log: each duration is the gap to the previous
# time. Keep the longest, and on a tie the larger letter.

def slowest_key(release_times, keys_pressed):
    best_time, best_key = release_times[0], keys_pressed[0]
    for i in range(1, len(release_times)):
        took = release_times[i] - release_times[i - 1]
        if (took, keys_pressed[i]) > (best_time, best_key):
            best_time, best_key = took, keys_pressed[i]
    return best_key


# ================================================================== 1701. Average Waiting Time (Medium)
# https://leetcode.com/problems/average-waiting-time/
# Pattern: Simulate one worker with a clock
# Idea: One server handles requests in the order they arrive. The clock is the time the server
# becomes free. A request starts at max(clock, arrival), and its waiting time is the finish time
# minus the arrival.

def average_waiting_time(customers):
    clock = 0
    waited = 0
    for arrival, work in customers:
        clock = max(clock, arrival) + work
        waited += clock - arrival
    return waited / len(customers)


# ================================================================== 210. Course Schedule II (Medium)
# https://leetcode.com/problems/course-schedule-ii/
# Pattern: Topological sort with in-degrees (Kahn)
# Idea: The same problem as running database migrations or loading apps in dependency order. Start
# with every item that depends on nothing, and each time one is done, lower the count of the items
# waiting for it. A cycle leaves items behind, so the answer is empty.

from collections import deque


def find_order(num_courses, prerequisites):
    waiting = [0] * num_courses
    unlocks = [[] for _ in range(num_courses)]
    for course, before in prerequisites:
        waiting[course] += 1
        unlocks[before].append(course)
    ready = deque(c for c in range(num_courses) if waiting[c] == 0)
    order = []
    while ready:
        c = ready.popleft()
        order.append(c)
        for nxt in unlocks[c]:
            waiting[nxt] -= 1
            if waiting[nxt] == 0:
                ready.append(nxt)
    return order if len(order) == num_courses else []


# ================================================================== 399. Evaluate Division (Medium)
# https://leetcode.com/problems/evaluate-division/
# Pattern: A weighted graph and a search
# Idea: Like a currency API that only knows some rates: a / b = 2 is an edge from a to b with weight
# 2 and from b to a with 0.5. A query multiplies the weights along any path, or gives -1.0 when
# there is none.

def calc_equation(equations, values, queries):
    graph = {}
    for (a, b), v in zip(equations, values):
        graph.setdefault(a, {})[b] = v
        graph.setdefault(b, {})[a] = 1 / v

    def search(start, goal):
        if start not in graph or goal not in graph:
            return -1.0
        stack, seen = [(start, 1.0)], {start}
        while stack:
            node, product = stack.pop()
            if node == goal:
                return product
            for nxt, w in graph[node].items():
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append((nxt, product * w))
        return -1.0

    return [search(a, b) for a, b in queries]


# ================================================================== 1942. The Number of the Smallest Unoccupied Chair (Medium)
# https://leetcode.com/problems/the-number-of-the-smallest-unoccupied-chair/
# Pattern: Two heaps: free chairs and busy chairs by leaving time
# Idea: This is exactly how a connection pool hands out the lowest free connection number. Go
# through arrivals in time order, first free every chair whose guest has left, then give the
# smallest free one.

import heapq


def smallest_chair(times, target_friend):
    order = sorted(range(len(times)), key=lambda i: times[i][0])
    free = list(range(len(times)))
    busy = []
    for i in order:
        arrive, leave = times[i]
        while busy and busy[0][0] <= arrive:
            heapq.heappush(free, heapq.heappop(busy)[1])
        chair = heapq.heappop(free)
        if i == target_friend:
            return chair
        heapq.heappush(busy, (leave, chair))


# ================================================================== 1438. Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit (Medium)
# https://leetcode.com/problems/longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit/
# Pattern: Sliding window with a max deque and a min deque
# Idea: Like finding the longest stretch where response times stayed within a band. Two deques keep
# the window's maximum and minimum in O(1). When max minus min is too big, move the left edge.

from collections import deque


def longest_subarray(nums, limit):
    high, low = deque(), deque()
    left = best = 0
    for right, x in enumerate(nums):
        while high and high[-1] < x:
            high.pop()
        high.append(x)
        while low and low[-1] > x:
            low.pop()
        low.append(x)
        while high[0] - low[0] > limit:
            if nums[left] == high[0]:
                high.popleft()
            if nums[left] == low[0]:
                low.popleft()
            left += 1
        best = max(best, right - left + 1)
    return best


# ================================================================== 752. Open the Lock (Medium)
# https://leetcode.com/problems/open-the-lock/
# Pattern: Breadth first search over 10,000 states
# Idea: A 4 digit lock has only 104 codes, which is why short codes need attempt limits. BFS from
# 0000 turns one wheel up or down at each step and skips the dead ends, so the first time it reaches
# the target is the fewest turns.

from collections import deque


def open_lock(deadends, target):
    dead = set(deadends)
    if "0000" in dead:
        return -1
    queue, seen = deque([("0000", 0)]), {"0000"}
    while queue:
        code, turns = queue.popleft()
        if code == target:
            return turns
        for i in range(4):
            d = int(code[i])
            for nd in ((d + 1) % 10, (d - 1) % 10):
                nxt = code[:i] + str(nd) + code[i + 1:]
                if nxt not in seen and nxt not in dead:
                    seen.add(nxt)
                    queue.append((nxt, turns + 1))
    return -1


# ================================================================== 2050. Parallel Courses III (Hard)
# https://leetcode.com/problems/parallel-courses-iii/
# Pattern: Longest path in a DAG, in topological order
# Idea: Like a deployment pipeline where jobs run in parallel once their needs are done: a job
# finishes at its own time plus the latest finish among the jobs it waits for. The answer is the
# latest finish of all.

from collections import deque


def minimum_time(n, relations, time):
    waiting = [0] * (n + 1)
    unlocks = [[] for _ in range(n + 1)]
    for before, after in relations:
        unlocks[before].append(after)
        waiting[after] += 1
    start = [0] * (n + 1)
    ready = deque(c for c in range(1, n + 1) if waiting[c] == 0)
    finish = [0] * (n + 1)
    while ready:
        c = ready.popleft()
        finish[c] = start[c] + time[c - 1]
        for nxt in unlocks[c]:
            start[nxt] = max(start[nxt], finish[c])
            waiting[nxt] -= 1
            if waiting[nxt] == 0:
                ready.append(nxt)
    return max(finish)


# ================================================================== 1235. Maximum Profit in Job Scheduling (Hard)
# https://leetcode.com/problems/maximum-profit-in-job-scheduling/
# Pattern: Sort by end time, DP with binary search
# Idea: Like choosing which paid batch jobs a single worker should run. Sort jobs by end time. The
# best profit up to a job is either the best without it, or its profit plus the best among jobs that
# end by its start, found with bisect.

import bisect


def job_scheduling(start_time, end_time, profit):
    jobs = sorted(zip(end_time, start_time, profit))
    ends = [0]
    best = [0]
    for end, start, gain in jobs:
        i = bisect.bisect_right(ends, start) - 1
        value = max(best[-1], best[i] + gain)
        ends.append(end)
        best.append(value)
    return best[-1]


# ================================================================== 630. Course Schedule III (Hard)
# https://leetcode.com/problems/course-schedule-iii/
# Pattern: Greedy by deadline with a max heap of durations
# Idea: Take tasks in order of their deadline. When the total time passes a deadline, drop the
# longest task taken so far, because that frees the most time while keeping the count. A max heap
# (negative numbers in heapq) finds it.

import heapq


def schedule_course(courses):
    taken = []
    total = 0
    for duration, last_day in sorted(courses, key=lambda c: c[1]):
        heapq.heappush(taken, -duration)
        total += duration
        if total > last_day:
            total += heapq.heappop(taken)
    return len(taken)


if __name__ == "__main__":
    results = []
    results.append(check("1629. Slowest Key", [('slowest_key([9, 29, 49, 50], "cbcd")', 'c'), ('slowest_key([12, 23, 36, 46, 62], "spuda")', 'a')]))
    results.append(check("1701. Average Waiting Time", [('average_waiting_time([[1, 2], [2, 5], [4, 3]])', 5.0), ('average_waiting_time([[5, 2], [5, 4], [10, 3], [20, 1]])', 3.25)]))
    results.append(check("210. Course Schedule II", [('find_order(2, [[1, 0]])', [0, 1]), ('find_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]])', [0, 1, 2, 3]), ('find_order(1, [])', [0]), ('find_order(2, [[0, 1], [1, 0]])', [])]))
    results.append(check("399. Evaluate Division", [('calc_equation([["a", "b"], ["b", "c"]], [2.0, 3.0], [["a", "c"], ["b", "a"], ["a", "e"], ["a", "a"], ["x", "x"]])', [6.0, 0.5, -1.0, 1.0, -1.0])]))
    results.append(check("1942. The Number of the Smallest Unoccupied Chair", [('smallest_chair([[1, 4], [2, 3], [4, 6]], 1)', 1), ('smallest_chair([[3, 10], [1, 5], [2, 6]], 0)', 2)]))
    results.append(check("1438. Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit", [('longest_subarray([8, 2, 4, 7], 4)', 2), ('longest_subarray([10, 1, 2, 4, 7, 2], 5)', 4), ('longest_subarray([4, 2, 2, 2, 4, 4, 2, 2], 0)', 3)]))
    results.append(check("752. Open the Lock", [('open_lock(["0201", "0101", "0102", "1212", "2002"], "0202")', 6), ('open_lock(["8888"], "0009")', 1), ('open_lock(["8887", "8889", "8878", "8898", "8788", "8988", "7888", "9888"], "8888")', -1)]))
    results.append(check("2050. Parallel Courses III", [('minimum_time(3, [[1, 3], [2, 3]], [3, 2, 5])', 8), ('minimum_time(5, [[1, 5], [2, 5], [3, 5], [3, 4], [4, 5]], [1, 2, 3, 4, 5])', 12)]))
    results.append(check("1235. Maximum Profit in Job Scheduling", [('job_scheduling([1, 2, 3, 3], [3, 4, 5, 6], [50, 10, 40, 70])', 120), ('job_scheduling([1, 2, 3, 4, 6], [3, 5, 10, 6, 9], [20, 20, 100, 70, 60])', 150), ('job_scheduling([1, 1, 1], [2, 3, 4], [5, 6, 4])', 6)]))
    results.append(check("630. Course Schedule III", [('schedule_course([[100, 200], [200, 1300], [1000, 1250], [2000, 3200]])', 3), ('schedule_course([[1, 2]])', 1), ('schedule_course([[3, 2], [4, 3]])', 0)]))
    if all(results):
        print("Every solution passes its tests.")
