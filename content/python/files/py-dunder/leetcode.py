# 1.1 Special methods and operator overloading
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


# ================================================================== 592. Fraction Addition and Subtraction (Medium)
# https://leetcode.com/problems/fraction-addition-and-subtraction/
# Pattern: Parse, add, reduce with gcd
# Idea: Read each signed fraction, add it to a running a/b with (ad + cb) / bd, then divide by the
# gcd.

import math


def fraction_addition(expression):
    top, bottom = 0, 1
    i = 0
    while i < len(expression):
        j = i + 1
        while j < len(expression) and expression[j] not in "+-":
            j += 1
        part = expression[i:j]                 # like "-1/2" or "1/3"
        a, b = part.split("/")
        a, b = int(a), int(b)
        top = top * b + a * bottom
        bottom = bottom * b
        g = math.gcd(top, bottom)
        top, bottom = top // g, bottom // g
        i = j
    return str(top) + "/" + str(bottom)


# ================================================================== 166. Fraction to Recurring Decimal (Medium)
# https://leetcode.com/problems/fraction-to-recurring-decimal/
# Pattern: Long division, remember remainders
# Idea: Do long division. When a remainder comes back, the digits since its first appearance repeat,
# so wrap them in brackets.

def fraction_to_decimal(numerator, denominator):
    if numerator == 0:
        return "0"
    sign = "-" if (numerator < 0) != (denominator < 0) else ""
    n, d = abs(numerator), abs(denominator)
    result = sign + str(n // d)
    rest = n % d
    if rest == 0:
        return result
    digits = ""
    seen = {}                                  # remainder: position in digits
    while rest != 0:
        if rest in seen:
            start = seen[rest]
            return result + "." + digits[:start] + "(" + digits[start:] + ")"
        seen[rest] = len(digits)
        rest = rest * 10
        digits = digits + str(rest // d)
        rest = rest % d
    return result + "." + digits


# ================================================================== 1656. Design an Ordered Stream (Easy)
# https://leetcode.com/problems/design-an-ordered-stream/
# Pattern: A list and a pointer
# Idea: Store each value at its id. After each insert, return the run of filled slots starting at
# the pointer and move the pointer past them.

class OrderedStream:
    def __init__(self, n):
        self.values = [None] * (n + 1)
        self.ptr = 1

    def insert(self, idKey, value):
        self.values[idKey] = value
        chunk = []
        while self.ptr < len(self.values) and self.values[self.ptr] is not None:
            chunk.append(self.values[self.ptr])
            self.ptr += 1
        return chunk


# ================================================================== 1845. Seat Reservation Manager (Medium)
# https://leetcode.com/problems/seat-reservation-manager/
# Pattern: A min heap of free seats
# Idea: Keep the free seats in a heap so the smallest one is always on top.

import heapq


class SeatManager:
    def __init__(self, n):
        self.free = list(range(1, n + 1))      # already a valid heap

    def reserve(self):
        return heapq.heappop(self.free)

    def unreserve(self, seatNumber):
        heapq.heappush(self.free, seatNumber)


# ================================================================== 2336. Smallest Number in Infinite Set (Medium)
# https://leetcode.com/problems/smallest-number-in-infinite-set/
# Pattern: A counter plus a set of returned numbers
# Idea: Numbers from next_new upwards are all present. Numbers added back below it go into a heap
# and a set.

import heapq


class SmallestInfiniteSet:
    def __init__(self):
        self.next_new = 1
        self.back = []                         # heap of numbers added back
        self.back_set = set()

    def popSmallest(self):
        if self.back:
            n = heapq.heappop(self.back)
            self.back_set.remove(n)
            return n
        self.next_new += 1
        return self.next_new - 1

    def addBack(self, num):
        if num < self.next_new and num not in self.back_set:
            heapq.heappush(self.back, num)
            self.back_set.add(num)


# ================================================================== 1381. Design a Stack With Increment Operation (Medium)
# https://leetcode.com/problems/design-a-stack-with-increment-operation/
# Pattern: A list with a size limit
# Idea: push only when there is room. increment adds val to the bottom k items.

class CustomStack:
    def __init__(self, maxSize):
        self.max_size = maxSize
        self.items = []

    def push(self, x):
        if len(self.items) < self.max_size:
            self.items.append(x)

    def pop(self):
        if not self.items:
            return -1
        return self.items.pop()

    def increment(self, k, val):
        for i in range(min(k, len(self.items))):
            self.items[i] += val


# ================================================================== 1286. Iterator for Combination (Medium)
# https://leetcode.com/problems/iterator-for-combination/
# Pattern: Make the combinations up front
# Idea: itertools.combinations gives the combinations in order. Store them and walk through them
# with an index.

from itertools import combinations


class CombinationIterator:
    def __init__(self, characters, combinationLength):
        self.items = ["".join(c) for c in combinations(characters, combinationLength)]
        self.i = 0

    def next(self):
        self.i += 1
        return self.items[self.i - 1]

    def hasNext(self):
        return self.i < len(self.items)


# ================================================================== 900. RLE Iterator (Medium)
# https://leetcode.com/problems/rle-iterator/
# Pattern: Use up counts
# Idea: Walk the pairs (count, value). Take n from the current count, moving to the next pair when
# one runs out.

class RLEIterator:
    def __init__(self, encoding):
        self.encoding = encoding
        self.i = 0

    def next(self, n):
        while self.i < len(self.encoding):
            if n <= self.encoding[self.i]:
                self.encoding[self.i] -= n
                return self.encoding[self.i + 1]
            n -= self.encoding[self.i]
            self.i += 2
        return -1


# ================================================================== 1670. Design Front Middle Back Queue (Medium)
# https://leetcode.com/problems/design-front-middle-back-queue/
# Pattern: A plain list
# Idea: A list with insert and pop at the right index is simple and fast enough for the limits. The
# middle index is len // 2 for push and (len - 1) // 2 for pop.

class FrontMiddleBackQueue:
    def __init__(self):
        self.items = []

    def pushFront(self, val):
        self.items.insert(0, val)

    def pushMiddle(self, val):
        self.items.insert(len(self.items) // 2, val)

    def pushBack(self, val):
        self.items.append(val)

    def popFront(self):
        return self.items.pop(0) if self.items else -1

    def popMiddle(self):
        return self.items.pop((len(self.items) - 1) // 2) if self.items else -1

    def popBack(self):
        return self.items.pop() if self.items else -1


# ================================================================== 2349. Design a Number Container System (Medium)
# https://leetcode.com/problems/design-a-number-container-system/
# Pattern: Dict plus a lazy heap per number
# Idea: Remember the number at each index. For each number keep a heap of indexes and drop stale
# ones when you look at the top.

import heapq


class NumberContainers:
    def __init__(self):
        self.at = {}                           # index: number
        self.heaps = {}                        # number: heap of indexes

    def change(self, index, number):
        self.at[index] = number
        if number not in self.heaps:
            self.heaps[number] = []
        heapq.heappush(self.heaps[number], index)

    def find(self, number):
        heap = self.heaps.get(number, [])
        while heap and self.at[heap[0]] != number:
            heapq.heappop(heap)                # this index now holds another number
        return heap[0] if heap else -1


if __name__ == "__main__":
    results = []
    results.append(check("592. Fraction Addition and Subtraction", [('fraction_addition("-1/2+1/2")', '0/1'), ('fraction_addition("-1/2+1/2+1/3")', '1/3'), ('fraction_addition("1/3-1/2")', '-1/6')]))
    results.append(check("166. Fraction to Recurring Decimal", [('fraction_to_decimal(1, 2)', '0.5'), ('fraction_to_decimal(2, 1)', '2'), ('fraction_to_decimal(4, 333)', '0.(012)'), ('fraction_to_decimal(-50, 8)', '-6.25'), ('fraction_to_decimal(1, 6)', '0.1(6)')]))
    results.append(check("1656. Design an Ordered Stream", [('(lambda s: [s.insert(3, "ccccc"), s.insert(1, "aaaaa"), s.insert(2, "bbbbb"), s.insert(5, "eeeee"), s.insert(4, "ddddd")])(OrderedStream(5))', [[], ['aaaaa'], ['bbbbb', 'ccccc'], [], ['ddddd', 'eeeee']])]))
    results.append(check("1845. Seat Reservation Manager", [('(lambda m: [m.reserve(), m.reserve(), m.unreserve(2), m.reserve(), m.reserve(), m.reserve(), m.reserve(), m.unreserve(5)])(SeatManager(5))', [1, 2, None, 2, 3, 4, 5, None])]))
    results.append(check("2336. Smallest Number in Infinite Set", [('(lambda s: [s.addBack(2), s.popSmallest(), s.popSmallest(), s.popSmallest(), s.addBack(1), s.popSmallest(), s.popSmallest(), s.popSmallest()])(SmallestInfiniteSet())', [None, 1, 2, 3, None, 1, 4, 5])]))
    results.append(check("1381. Design a Stack With Increment Operation", [('(lambda s: [s.push(1), s.push(2), s.pop(), s.push(2), s.push(3), s.push(4), s.increment(5, 100), s.increment(2, 100), s.pop(), s.pop(), s.pop(), s.pop()])(CustomStack(3))', [None, None, 2, None, None, None, None, None, 103, 202, 201, -1])]))
    results.append(check("1286. Iterator for Combination", [('(lambda c: [c.next(), c.hasNext(), c.next(), c.hasNext(), c.next(), c.hasNext()])(CombinationIterator("abc", 2))', ['ab', True, 'ac', True, 'bc', False])]))
    results.append(check("900. RLE Iterator", [('(lambda r: [r.next(2), r.next(1), r.next(1), r.next(2)])(RLEIterator([3, 8, 0, 9, 2, 5]))', [8, 8, 5, -1])]))
    results.append(check("1670. Design Front Middle Back Queue", [('(lambda q: [q.pushFront(1), q.pushBack(2), q.pushMiddle(3), q.pushMiddle(4), q.popFront(), q.popMiddle(), q.popMiddle(), q.popBack(), q.popFront()])(FrontMiddleBackQueue())', [None, None, None, None, 1, 3, 4, 2, -1])]))
    results.append(check("2349. Design a Number Container System", [('(lambda n: [n.find(10), n.change(2, 10), n.change(1, 10), n.change(3, 10), n.change(5, 10), n.find(10), n.change(1, 20), n.find(10)])(NumberContainers())', [-1, None, None, None, None, 1, None, 2])]))
    if all(results):
        print("Every solution passes its tests.")
