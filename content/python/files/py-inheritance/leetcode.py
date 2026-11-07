# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
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


# ================================================================== 284. Peeking Iterator (Medium)
# https://leetcode.com/problems/peeking-iterator/
# Pattern: Wrap an object and look one step ahead
# Idea: Keep the next value in an attribute. peek returns it, next returns it and fetches a new one.
# This is composition: the class holds another object.

class ListIterator:
    # LeetCode gives you an iterator with hasNext() and next(). This small class plays that part.
    def __init__(self, nums):
        self.nums = nums
        self.i = 0

    def hasNext(self):
        return self.i < len(self.nums)

    def next(self):
        self.i += 1
        return self.nums[self.i - 1]


class PeekingIterator:
    def __init__(self, iterator):
        self.iterator = iterator
        self.has_ahead = iterator.hasNext()
        self.ahead = iterator.next() if self.has_ahead else None

    def peek(self):
        return self.ahead

    def next(self):
        value = self.ahead
        self.has_ahead = self.iterator.hasNext()
        self.ahead = self.iterator.next() if self.has_ahead else None
        return value

    def hasNext(self):
        return self.has_ahead


# ================================================================== 341. Flatten Nested List Iterator (Medium)
# https://leetcode.com/problems/flatten-nested-list-iterator/
# Pattern: Flatten once with recursion
# Idea: Walk the nested list with a recursive helper and store every integer in a plain list. Then
# next and hasNext only move an index.

class NestedInteger:
    # LeetCode gives you this class. Each one holds either one integer or a list of NestedInteger.
    def __init__(self, value):
        self.value = value

    def isInteger(self):
        return not isinstance(self.value, list)

    def getInteger(self):
        return self.value

    def getList(self):
        return self.value


class NestedIterator:
    def __init__(self, nestedList):
        self.values = []
        self.add_all(nestedList)
        self.i = 0

    def add_all(self, items):
        for item in items:
            if item.isInteger():
                self.values.append(item.getInteger())
            else:
                self.add_all(item.getList())

    def next(self):
        self.i += 1
        return self.values[self.i - 1]

    def hasNext(self):
        return self.i < len(self.values)


def build_nested(data):
    # turns [[1, 1], 2, [1, 1]] into NestedInteger objects for the tests
    if isinstance(data, list):
        return NestedInteger([build_nested(x) for x in data])
    return NestedInteger(data)


def drain(it):
    out = []
    while it.hasNext():
        out.append(it.next())
    return out


# ================================================================== 707. Design Linked List (Medium)
# https://leetcode.com/problems/design-linked-list/
# Pattern: Node objects and a dummy head
# Idea: Each node object holds a value and a link to the next node. A dummy node before the first
# one means adding at index 0 needs no special case.

class LinkedNode:
    def __init__(self, val, next_node=None):
        self.val = val
        self.next = next_node


class MyLinkedList:
    def __init__(self):
        self.dummy = LinkedNode(0)      # a fake node before the real first node
        self.size = 0

    def node_before(self, index):
        node = self.dummy
        for i in range(index):
            node = node.next
        return node

    def get(self, index):
        if index < 0 or index >= self.size:
            return -1
        return self.node_before(index).next.val

    def addAtHead(self, val):
        self.addAtIndex(0, val)

    def addAtTail(self, val):
        self.addAtIndex(self.size, val)

    def addAtIndex(self, index, val):
        if index < 0 or index > self.size:
            return
        before = self.node_before(index)
        before.next = LinkedNode(val, before.next)
        self.size += 1

    def deleteAtIndex(self, index):
        if index < 0 or index >= self.size:
            return
        before = self.node_before(index)
        before.next = before.next.next
        self.size -= 1


# ================================================================== 208. Implement Trie (Prefix Tree) (Medium)
# https://leetcode.com/problems/implement-trie-prefix-tree/
# Pattern: A tree of node objects
# Idea: Each node has a dict of children, one per next letter, and a flag that marks the end of a
# word.

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_word = True

    def find(self, text):
        node = self.root
        for ch in text:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def search(self, word):
        node = self.find(word)
        return node is not None and node.is_word

    def startsWith(self, prefix):
        return self.find(prefix) is not None


# ================================================================== 641. Design Circular Deque (Medium)
# https://leetcode.com/problems/design-circular-deque/
# Pattern: Fixed list with a moving front
# Idea: Like the circular queue, but the front can also move back by one: (front − 1) % k.

class MyCircularDeque:
    def __init__(self, k):
        self.data = [0] * k
        self.k = k
        self.front = 0
        self.count = 0

    def insertFront(self, value):
        if self.isFull():
            return False
        self.front = (self.front - 1) % self.k
        self.data[self.front] = value
        self.count += 1
        return True

    def insertLast(self, value):
        if self.isFull():
            return False
        self.data[(self.front + self.count) % self.k] = value
        self.count += 1
        return True

    def deleteFront(self):
        if self.isEmpty():
            return False
        self.front = (self.front + 1) % self.k
        self.count -= 1
        return True

    def deleteLast(self):
        if self.isEmpty():
            return False
        self.count -= 1
        return True

    def getFront(self):
        if self.isEmpty():
            return -1
        return self.data[self.front]

    def getRear(self):
        if self.isEmpty():
            return -1
        return self.data[(self.front + self.count - 1) % self.k]

    def isEmpty(self):
        return self.count == 0

    def isFull(self):
        return self.count == self.k


# ================================================================== 933. Number of Recent Calls (Easy)
# https://leetcode.com/problems/number-of-recent-calls/
# Pattern: A queue of times
# Idea: Add each new time to the back. Remove times from the front that are older than t − 3000. The
# length is the answer.

from collections import deque


class RecentCounter:
    def __init__(self):
        self.times = deque()

    def ping(self, t):
        self.times.append(t)
        while self.times[0] < t - 3000:
            self.times.popleft()
        return len(self.times)


# ================================================================== 901. Online Stock Span (Medium)
# https://leetcode.com/problems/online-stock-span/
# Pattern: Stack of price and span pairs
# Idea: Keep a stack of [price, span]. While the top price is not bigger than today, pop it and add
# its span to today.

class StockSpanner:
    def __init__(self):
        self.stack = []        # pairs [price, span], prices going down

    def next(self, price):
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]
        self.stack.append([price, span])
        return span


# ================================================================== 1352. Product of the Last K Numbers (Medium)
# https://leetcode.com/problems/product-of-the-last-k-numbers/
# Pattern: Prefix products, reset at zero
# Idea: Keep running products. The product of the last k is last / products[−k − 1]. A zero clears
# the list, and asking past it gives 0.

class ProductOfNumbers:
    def __init__(self):
        self.products = [1]

    def add(self, num):
        if num == 0:
            self.products = [1]
        else:
            self.products.append(self.products[-1] * num)

    def getProduct(self, k):
        if k >= len(self.products):
            return 0
        return self.products[-1] // self.products[-k - 1]


# ================================================================== 2241. Design an ATM Machine (Medium)
# https://leetcode.com/problems/design-an-atm-machine/
# Pattern: Greedy from the biggest note
# Idea: Store how many of each note there are. To withdraw, take as many big notes as possible, then
# smaller ones. If money is left over, refuse and change nothing.

class ATM:
    def __init__(self):
        self.values = [20, 50, 100, 200, 500]
        self.counts = [0, 0, 0, 0, 0]

    def deposit(self, banknotesCount):
        for i in range(5):
            self.counts[i] += banknotesCount[i]

    def withdraw(self, amount):
        take = [0, 0, 0, 0, 0]
        for i in range(4, -1, -1):
            take[i] = min(self.counts[i], amount // self.values[i])
            amount -= take[i] * self.values[i]
        if amount != 0:
            return [-1]
        for i in range(5):
            self.counts[i] -= take[i]
        return take


# ================================================================== 1396. Design Underground System (Medium)
# https://leetcode.com/problems/design-underground-system/
# Pattern: Two dicts
# Idea: One dict remembers where and when each card checked in. Another adds up total time and trip
# count for each pair of stations.

class UndergroundSystem:
    def __init__(self):
        self.inside = {}       # card id: (station, time)
        self.trips = {}        # (start, end): [total time, count]

    def checkIn(self, id, stationName, t):
        self.inside[id] = (stationName, t)

    def checkOut(self, id, stationName, t):
        start, t0 = self.inside.pop(id)
        key = (start, stationName)
        if key not in self.trips:
            self.trips[key] = [0, 0]
        self.trips[key][0] += t - t0
        self.trips[key][1] += 1

    def getAverageTime(self, startStation, endStation):
        total, count = self.trips[(startStation, endStation)]
        return total / count


if __name__ == "__main__":
    results = []
    results.append(check("284. Peeking Iterator", [('(lambda p: [p.next(), p.peek(), p.next(), p.next(), p.hasNext()])(PeekingIterator(ListIterator([1, 2, 3])))', [1, 2, 2, 3, False])]))
    results.append(check("341. Flatten Nested List Iterator", [('drain(NestedIterator(build_nested([[1, 1], 2, [1, 1]]).getList()))', [1, 1, 2, 1, 1]), ('drain(NestedIterator(build_nested([1, [4, [6]]]).getList()))', [1, 4, 6])]))
    results.append(check("707. Design Linked List", [('(lambda m: [m.addAtHead(1), m.addAtTail(3), m.addAtIndex(1, 2), m.get(1), m.deleteAtIndex(1), m.get(1)])(MyLinkedList())', [None, None, None, 2, None, 3])]))
    results.append(check("208. Implement Trie (Prefix Tree)", [('(lambda t: [t.insert("apple"), t.search("apple"), t.search("app"), t.startsWith("app"), t.insert("app"), t.search("app")])(Trie())', [None, True, False, True, None, True])]))
    results.append(check("641. Design Circular Deque", [('(lambda d: [d.insertLast(1), d.insertLast(2), d.insertFront(3), d.insertFront(4), d.getRear(), d.isFull(), d.deleteLast(), d.insertFront(4), d.getFront()])(MyCircularDeque(3))', [True, True, True, False, 2, True, True, True, 4])]))
    results.append(check("933. Number of Recent Calls", [('(lambda r: [r.ping(1), r.ping(100), r.ping(3001), r.ping(3002)])(RecentCounter())', [1, 2, 3, 3])]))
    results.append(check("901. Online Stock Span", [('(lambda s: [s.next(p) for p in [100, 80, 60, 70, 60, 75, 85]])(StockSpanner())', [1, 1, 1, 2, 1, 4, 6])]))
    results.append(check("1352. Product of the Last K Numbers", [('(lambda p: [p.add(3), p.add(0), p.add(2), p.add(5), p.add(4), p.getProduct(2), p.getProduct(3), p.getProduct(4), p.add(8), p.getProduct(2)])(ProductOfNumbers())', [None, None, None, None, None, 20, 40, 0, None, 32])]))
    results.append(check("2241. Design an ATM Machine", [('(lambda a: [a.deposit([0, 0, 1, 2, 1]), a.withdraw(600), a.deposit([0, 1, 0, 1, 1]), a.withdraw(600), a.withdraw(550)])(ATM())', [None, [0, 0, 1, 0, 1], None, [-1], [0, 1, 0, 0, 1]])]))
    results.append(check("1396. Design Underground System", [('(lambda u: [u.checkIn(45, "Leyton", 3), u.checkIn(32, "Paradise", 8), u.checkIn(27, "Leyton", 10), u.checkOut(45, "Waterloo", 15), u.checkOut(27, "Waterloo", 20), u.checkOut(32, "Cambridge", 22), u.getAverageTime("Paradise", "Cambridge"), u.getAverageTime("Leyton", "Waterloo")])(UndergroundSystem())', [None, None, None, None, None, None, 14.0, 11.0])]))
    if all(results):
        print("Every solution passes its tests.")
