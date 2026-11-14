# 3.1 Function approximation and deep Q networks
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


# ================================================================== 703. Kth Largest Element in a Stream (Easy)
# https://leetcode.com/problems/kth-largest-element-in-a-stream/
# Pattern: Keep a min heap of the k largest values
# Idea: Push each new value and pop the smallest whenever the heap holds more than k. The top of the
# heap is then the kth largest. Keeping only the most important items from a stream is what
# prioritised replay does with surprising transitions. Our helper returns the answer after each add.

import heapq


class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = []
        for x in nums:
            self.add(x)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]


def kth_largest_run(k, nums, adds):
    kl = KthLargest(k, nums)
    return [kl.add(v) for v in adds]


# ================================================================== 1046. Last Stone Weight (Easy)
# https://leetcode.com/problems/last-stone-weight/
# Pattern: A max heap: smash the two heaviest each time
# Idea: Python’s heapq is a min heap, so store negative weights. Pop the two largest, push back
# their difference if it is not zero, and repeat. Always taking the biggest first is how prioritised
# replay picks the transitions with the largest TD error.

import heapq


def last_stone_weight(stones):
    heap = [-s for s in stones]
    heapq.heapify(heap)
    while len(heap) > 1:
        a = -heapq.heappop(heap)
        b = -heapq.heappop(heap)
        if a != b:
            heapq.heappush(heap, -(a - b))
    return -heap[0] if heap else 0


# ================================================================== 622. Design Circular Queue (Medium)
# https://leetcode.com/problems/design-circular-queue/
# Pattern: A fixed array with a head index and a count
# Idea: Store items in a list of fixed size. The next free slot is (head + count) mod size. This
# ring buffer is exactly how a DQN replay memory is stored: when it is full, the newest transition
# overwrites the oldest. Our helper runs a list of operations.

class MyCircularQueue:
    def __init__(self, k):
        self.data = [0] * k
        self.head = 0
        self.count = 0

    def enQueue(self, value):
        if self.isFull():
            return False
        self.data[(self.head + self.count) % len(self.data)] = value
        self.count += 1
        return True

    def deQueue(self):
        if self.isEmpty():
            return False
        self.head = (self.head + 1) % len(self.data)
        self.count -= 1
        return True

    def Front(self):
        return -1 if self.isEmpty() else self.data[self.head]

    def Rear(self):
        return -1 if self.isEmpty() else self.data[(self.head + self.count - 1) % len(self.data)]

    def isEmpty(self):
        return self.count == 0

    def isFull(self):
        return self.count == len(self.data)


def circular_run(k, ops):
    q, out = MyCircularQueue(k), []
    for op in ops:
        out.append(getattr(q, op[0])(*op[1:]))
    return out


# ================================================================== 146. LRU Cache (Medium)
# https://leetcode.com/problems/lru-cache/
# Pattern: An ordered dictionary: move used keys to the end, evict from the front
# Idea: OrderedDict keeps keys in order of use. On get or put move the key to the end, and when the
# cache is too big remove the first key, the least recently used. Choosing what to forget when
# memory is full is the same question a replay memory answers, and DQN simply forgets the oldest.
# Our helper runs a list of operations and returns the results of get.

from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.store = OrderedDict()

    def get(self, key):
        if key not in self.store:
            return -1
        self.store.move_to_end(key)
        return self.store[key]

    def put(self, key, value):
        self.store[key] = value
        self.store.move_to_end(key)
        if len(self.store) > self.capacity:
            self.store.popitem(last=False)


def lru_run(capacity, ops):
    cache, out = LRUCache(capacity), []
    for op in ops:
        if op[0] == "get":
            out.append(cache.get(op[1]))
        else:
            cache.put(op[1], op[2])
    return out


# ================================================================== 480. Sliding Window Median (Hard)
# https://leetcode.com/problems/sliding-window-median/
# Pattern: Keep the window sorted and insert and remove with binary search
# Idea: Hold the current window in a sorted list. Use bisect to insert the new value and remove the
# one leaving, then read the middle. Medians of recent results are a robust way to report RL
# progress, because single episodes can be wildly high or low.

import bisect


def median_sliding_window(nums, k):
    window = sorted(nums[:k])
    out = []
    for i in range(k, len(nums) + 1):
        if k % 2:
            out.append(float(window[k // 2]))
        else:
            out.append((window[k // 2 - 1] + window[k // 2]) / 2)
        if i == len(nums):
            break
        window.pop(bisect.bisect_left(window, nums[i - k]))
        bisect.insort(window, nums[i])
    return out


if __name__ == "__main__":
    results = []
    results.append(check("703. Kth Largest Element in a Stream", [('kth_largest_run(3, [4, 5, 8, 2], [3, 5, 10, 9, 4])', [4, 5, 5, 8, 8]), ('kth_largest_run(1, [], [-3, -2, -4, 0, 4])', [-3, -2, -2, 0, 4])]))
    results.append(check("1046. Last Stone Weight", [('last_stone_weight([2, 7, 4, 1, 8, 1])', 1), ('last_stone_weight([1])', 1), ('last_stone_weight([3, 3])', 0)]))
    results.append(check("622. Design Circular Queue", [('circular_run(3, [("enQueue", 1), ("enQueue", 2), ("enQueue", 3), ("enQueue", 4), ("Rear",), ("isFull",), ("deQueue",), ("enQueue", 4), ("Rear",)])', [True, True, True, False, 3, True, True, True, 4])]))
    results.append(check("146. LRU Cache", [('lru_run(2, [("put", 1, 1), ("put", 2, 2), ("get", 1), ("put", 3, 3), ("get", 2), ("put", 4, 4), ("get", 1), ("get", 3), ("get", 4)])', [1, -1, -1, 3, 4])]))
    results.append(check("480. Sliding Window Median", [('median_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)', [1.0, -1.0, -1.0, 3.0, 5.0, 6.0]), ('median_sliding_window([1, 2, 3, 4, 2, 3, 1, 4, 2], 3)', [2.0, 3.0, 3.0, 3.0, 2.0, 3.0, 2.0]), ('median_sliding_window([1, 4, 2, 3], 4)', [2.5])]))
    if all(results):
        print("Every solution passes its tests.")
