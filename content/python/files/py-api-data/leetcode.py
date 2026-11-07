# 2.2 Real API work: pages, retries, limits and validation
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


# ================================================================== 21. Merge Two Sorted Lists (Easy)
# https://leetcode.com/problems/merge-two-sorted-lists/
# Pattern: Walk both lists, always take the smaller head
# Idea: Like merging two sorted pages of results from two APIs. A dummy first node keeps the code
# short.

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def merge_two_lists(list1, list2):
    dummy = ListNode()
    tail = dummy
    while list1 and list2:
        if list1.val <= list2.val:
            tail.next = list1
            list1 = list1.next
        else:
            tail.next = list2
            list2 = list2.next
        tail = tail.next
    tail.next = list1 or list2
    return dummy.next


def build(values):
    head = None
    for value in reversed(values):
        head = ListNode(value, head)
    return head


def to_list(node):
    values = []
    while node:
        values.append(node.val)
        node = node.next
    return values


def merge_lists(a, b):
    return to_list(merge_two_lists(build(a), build(b)))


# ================================================================== 350. Intersection of Two Arrays II (Easy)
# https://leetcode.com/problems/intersection-of-two-arrays-ii/
# Pattern: Counter and the & operator
# Idea: Which ids do two API answers share, counting repeats? Counter(a) & Counter(b) keeps the
# smaller count of each value.

from collections import Counter


def intersect(nums1, nums2):
    common = Counter(nums1) & Counter(nums2)
    return sorted(common.elements())


# ================================================================== 1450. Number of Students Doing Homework at a Given Time (Easy)
# https://leetcode.com/problems/number-of-students-doing-homework-at-a-given-time/
# Pattern: Check each time range
# Idea: Like counting the sessions that were active at a given moment in API logs. A range counts
# when start <= time <= end.

def busy_student(start_time, end_time, query_time):
    return sum(1 for start, end in zip(start_time, end_time) if start <= query_time <= end)


# ================================================================== 703. Kth Largest Element in a Stream (Easy)
# https://leetcode.com/problems/kth-largest-element-in-a-stream/
# Pattern: A min heap of size k
# Idea: Keep only the k largest values seen so far in a heap. Its smallest value is the k-th
# largest, like the slowest of the top k response times.

import heapq


class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = []
        for number in nums:
            self.add(number)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 57. Insert Interval (Medium)
# https://leetcode.com/problems/insert-interval/
# Pattern: Before, overlapping, after
# Idea: Add a time range to a sorted list of ranges. Copy the ranges that end before it, merge the
# ones that overlap, then copy the rest.

def insert(intervals, new_interval):
    start, end = new_interval
    result = []
    i = 0
    while i < len(intervals) and intervals[i][1] < start:
        result.append(intervals[i])
        i += 1
    while i < len(intervals) and intervals[i][0] <= end:
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])
        i += 1
    result.append([start, end])
    result.extend(intervals[i:])
    return result


# ================================================================== 729. My Calendar I (Medium)
# https://leetcode.com/problems/my-calendar-i/
# Pattern: Two ranges overlap when each starts before the other ends
# Idea: A booking API must refuse a slot that overlaps an existing one. [s1, e1) and [s2, e2)
# overlap when s1 < e2 and s2 < e1.

class MyCalendar:
    def __init__(self):
        self.booked = []

    def book(self, start, end):
        for s, e in self.booked:
            if start < e and s < end:
                return False
        self.booked.append((start, end))
        return True


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 731. My Calendar II (Medium)
# https://leetcode.com/problems/my-calendar-ii/
# Pattern: Keep the bookings and the double booked parts
# Idea: Now two bookings may overlap but never three. Keep a list of the parts that are already
# double booked. A new booking that touches one of them must be refused.

class MyCalendarTwo:
    def __init__(self):
        self.booked = []
        self.double = []

    def book(self, start, end):
        for s, e in self.double:
            if start < e and s < end:
                return False
        for s, e in self.booked:
            if start < e and s < end:
                self.double.append((max(start, s), min(end, e)))
        self.booked.append((start, end))
        return True


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 435. Non-overlapping Intervals (Medium)
# https://leetcode.com/problems/non-overlapping-intervals/
# Pattern: Greedy: keep the range that ends first
# Idea: Sort by end time. Keep a range when it starts after the last kept one ends, otherwise remove
# it. Ending early leaves the most room.

def erase_overlap_intervals(intervals):
    removed = 0
    last_end = float("-inf")
    for start, end in sorted(intervals, key=lambda pair: pair[1]):
        if start >= last_end:
            last_end = end
        else:
            removed += 1
    return removed


# ================================================================== 480. Sliding Window Median (Hard)
# https://leetcode.com/problems/sliding-window-median/
# Pattern: Keep the window sorted with bisect
# Idea: Monitoring shows the median response time of the last k calls. Keep the window sorted:
# insort the new value, remove the old one, and read the middle.

from bisect import bisect_left, insort


def median_sliding_window(nums, k):
    window = sorted(nums[:k])
    medians = []
    for i in range(k, len(nums) + 1):
        if k % 2 == 1:
            medians.append(float(window[k // 2]))
        else:
            medians.append((window[k // 2 - 1] + window[k // 2]) / 2)
        if i == len(nums):
            break
        window.pop(bisect_left(window, nums[i - k]))
        insort(window, nums[i])
    return medians


# ================================================================== 732. My Calendar III (Hard)
# https://leetcode.com/problems/my-calendar-iii/
# Pattern: Sweep line: +1 at a start, −1 at an end
# Idea: How many bookings overlap at the busiest moment? Add +1 at each start and −1 at each end,
# then walk the times in order and keep a running sum.

class MyCalendarThree:
    def __init__(self):
        self.change = {}

    def book(self, startTime, endTime):
        self.change[startTime] = self.change.get(startTime, 0) + 1
        self.change[endTime] = self.change.get(endTime, 0) - 1
        running = 0
        most = 0
        for time in sorted(self.change):
            running += self.change[time]
            most = max(most, running)
        return most


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


if __name__ == "__main__":
    results = []
    results.append(check("21. Merge Two Sorted Lists", [('merge_lists([1, 2, 4], [1, 3, 4])', [1, 1, 2, 3, 4, 4]), ('merge_lists([], [])', []), ('merge_lists([], [0])', [0])]))
    results.append(check("350. Intersection of Two Arrays II", [('intersect([1, 2, 2, 1], [2, 2])', [2, 2]), ('intersect([4, 9, 5], [9, 4, 9, 8, 4])', [4, 9])]))
    results.append(check("1450. Number of Students Doing Homework at a Given Time", [('busy_student([1, 2, 3], [3, 2, 7], 4)', 1), ('busy_student([4], [4], 4)', 1)]))
    results.append(check("703. Kth Largest Element in a Stream", [('play(KthLargest, ["KthLargest", "add", "add", "add", "add", "add"], [[3, [4, 5, 8, 2]], [3], [5], [10], [9], [4]])', [None, 4, 5, 5, 8, 8])]))
    results.append(check("57. Insert Interval", [('insert([[1, 3], [6, 9]], [2, 5])', [[1, 5], [6, 9]]), ('insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8])', [[1, 2], [3, 10], [12, 16]])]))
    results.append(check("729. My Calendar I", [('play(MyCalendar, ["MyCalendar", "book", "book", "book"], [[], [10, 20], [15, 25], [20, 30]])', [None, True, False, True])]))
    results.append(check("731. My Calendar II", [('play(MyCalendarTwo, ["MyCalendarTwo", "book", "book", "book", "book", "book", "book"], [[], [10, 20], [50, 60], [10, 40], [5, 15], [5, 10], [25, 55]])', [None, True, True, True, False, True, True])]))
    results.append(check("435. Non-overlapping Intervals", [('erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]])', 1), ('erase_overlap_intervals([[1, 2], [1, 2], [1, 2]])', 2), ('erase_overlap_intervals([[1, 2], [2, 3]])', 0)]))
    results.append(check("480. Sliding Window Median", [('median_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)', [1.0, -1.0, -1.0, 3.0, 5.0, 6.0]), ('median_sliding_window([1, 2, 3, 4, 2, 3, 1, 4, 2], 3)', [2.0, 3.0, 3.0, 3.0, 2.0, 3.0, 2.0]), ('median_sliding_window([1, 4, 2, 3], 4)', [2.5])]))
    results.append(check("732. My Calendar III", [('play(MyCalendarThree, ["MyCalendarThree", "book", "book", "book", "book", "book", "book"], [[], [10, 20], [50, 60], [10, 40], [5, 15], [5, 10], [25, 55]])', [None, 1, 1, 2, 3, 3, 3])]))
    if all(results):
        print("Every solution passes its tests.")
