# 6.1 Classes and objects: attributes, methods, self and encapsulation
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


# ================================================================== 155. Min Stack (Medium)
# https://leetcode.com/problems/min-stack/
# Pattern: Keep a second stack of minimums
# Idea: Next to the normal stack, keep a stack whose top is always the smallest value so far. Push
# to it when the new value is not bigger.

class MinStack:
    # LeetCode names the methods getMin and so on, so we keep their names
    def __init__(self):
        self.items = []
        self.mins = []          # mins[-1] is always the smallest value in the stack

    def push(self, val):
        self.items.append(val)
        if not self.mins or val <= self.mins[-1]:
            self.mins.append(val)

    def pop(self):
        val = self.items.pop()
        if val == self.mins[-1]:
            self.mins.pop()

    def top(self):
        return self.items[-1]

    def getMin(self):
        return self.mins[-1]


# ================================================================== 232. Implement Queue using Stacks (Easy)
# https://leetcode.com/problems/implement-queue-using-stacks/
# Pattern: Two stacks
# Idea: Push onto an inbox stack. To pop, pour the inbox into an outbox stack (which reverses it)
# only when the outbox is empty.

class MyQueue:
    def __init__(self):
        self.inbox = []
        self.outbox = []

    def push(self, x):
        self.inbox.append(x)

    def move(self):
        if not self.outbox:
            while self.inbox:
                self.outbox.append(self.inbox.pop())

    def pop(self):
        self.move()
        return self.outbox.pop()

    def peek(self):
        self.move()
        return self.outbox[-1]

    def empty(self):
        return not self.inbox and not self.outbox


# ================================================================== 225. Implement Stack using Queues (Easy)
# https://leetcode.com/problems/implement-stack-using-queues/
# Pattern: Rotate one queue
# Idea: After adding x to the back, move every older item from the front to the back, so x is at the
# front.

from collections import deque


class MyStack:
    def __init__(self):
        self.queue = deque()

    def push(self, x):
        self.queue.append(x)
        for i in range(len(self.queue) - 1):
            self.queue.append(self.queue.popleft())

    def pop(self):
        return self.queue.popleft()

    def top(self):
        return self.queue[0]

    def empty(self):
        return len(self.queue) == 0


# ================================================================== 705. Design HashSet (Easy)
# https://leetcode.com/problems/design-hashset/
# Pattern: Buckets of lists
# Idea: Keep 1,000 small lists. A key goes in bucket key % 1000, so each search looks at only one
# short list.

class MyHashSet:
    def __init__(self):
        self.size = 1000
        self.buckets = [[] for i in range(self.size)]

    def add(self, key):
        bucket = self.buckets[key % self.size]
        if key not in bucket:
            bucket.append(key)

    def remove(self, key):
        bucket = self.buckets[key % self.size]
        if key in bucket:
            bucket.remove(key)

    def contains(self, key):
        return key in self.buckets[key % self.size]


# ================================================================== 706. Design HashMap (Easy)
# https://leetcode.com/problems/design-hashmap/
# Pattern: Buckets of key and value pairs
# Idea: Like the hash set, but each bucket holds [key, value] pairs. put updates a pair or adds one.

class MyHashMap:
    def __init__(self):
        self.size = 1000
        self.buckets = [[] for i in range(self.size)]

    def put(self, key, value):
        bucket = self.buckets[key % self.size]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])

    def get(self, key):
        for pair in self.buckets[key % self.size]:
            if pair[0] == key:
                return pair[1]
        return -1

    def remove(self, key):
        bucket = self.buckets[key % self.size]
        for i in range(len(bucket)):
            if bucket[i][0] == key:
                bucket.pop(i)
                return


# ================================================================== 1603. Design Parking System (Easy)
# https://leetcode.com/problems/design-parking-system/
# Pattern: One counter per car type
# Idea: Store the free spaces in a list indexed by car type. A car parks only if its counter is
# above zero.

class ParkingSystem:
    def __init__(self, big, medium, small):
        self.free = [0, big, medium, small]     # index 1 is big, 2 is medium, 3 is small

    def addCar(self, carType):
        if self.free[carType] == 0:
            return False
        self.free[carType] -= 1
        return True


# ================================================================== 1472. Design Browser History (Medium)
# https://leetcode.com/problems/design-browser-history/
# Pattern: A list and a position
# Idea: Keep the pages in a list and the index of the current page. visit cuts off the forward
# pages, back and forward move the index within limits.

class BrowserHistory:
    def __init__(self, homepage):
        self.pages = [homepage]
        self.current = 0

    def visit(self, url):
        self.pages = self.pages[:self.current + 1]     # forward history is cleared
        self.pages.append(url)
        self.current += 1

    def back(self, steps):
        self.current = max(0, self.current - steps)
        return self.pages[self.current]

    def forward(self, steps):
        self.current = min(len(self.pages) - 1, self.current + steps)
        return self.pages[self.current]


# ================================================================== 622. Design Circular Queue (Medium)
# https://leetcode.com/problems/design-circular-queue/
# Pattern: Fixed list, head index and count
# Idea: The back of the queue is at (head + count) % k. Moving the head with % k makes the list wrap
# around.

class MyCircularQueue:
    def __init__(self, k):
        self.data = [0] * k
        self.k = k
        self.head = 0
        self.count = 0

    def enQueue(self, value):
        if self.isFull():
            return False
        tail = (self.head + self.count) % self.k
        self.data[tail] = value
        self.count += 1
        return True

    def deQueue(self):
        if self.isEmpty():
            return False
        self.head = (self.head + 1) % self.k
        self.count -= 1
        return True

    def Front(self):
        if self.isEmpty():
            return -1
        return self.data[self.head]

    def Rear(self):
        if self.isEmpty():
            return -1
        return self.data[(self.head + self.count - 1) % self.k]

    def isEmpty(self):
        return self.count == 0

    def isFull(self):
        return self.count == self.k


# ================================================================== 2043. Simple Bank System (Medium)
# https://leetcode.com/problems/simple-bank-system/
# Pattern: Check, then change
# Idea: Every method first checks that the account numbers exist and the money is there, and only
# then changes the balances.

class Bank:
    def __init__(self, balance):
        self.balance = balance          # account number i is stored at balance[i - 1]

    def valid(self, account):
        return 1 <= account <= len(self.balance)

    def transfer(self, account1, account2, money):
        if not self.valid(account1) or not self.valid(account2):
            return False
        if self.balance[account1 - 1] < money:
            return False
        self.balance[account1 - 1] -= money
        self.balance[account2 - 1] += money
        return True

    def deposit(self, account, money):
        if not self.valid(account):
            return False
        self.balance[account - 1] += money
        return True

    def withdraw(self, account, money):
        if not self.valid(account) or self.balance[account - 1] < money:
            return False
        self.balance[account - 1] -= money
        return True


# ================================================================== 146. LRU Cache (Medium)
# https://leetcode.com/problems/lru-cache/
# Pattern: A dict keeps insertion order
# Idea: Python dicts remember the order keys were added. Move a key to the end when it is used, and
# remove the first key when the cache is full.

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = {}              # oldest key first, newest key last

    def get(self, key):
        if key not in self.data:
            return -1
        value = self.data.pop(key)
        self.data[key] = value      # move it to the newest end
        return value

    def put(self, key, value):
        if key in self.data:
            self.data.pop(key)
        elif len(self.data) == self.capacity:
            oldest = next(iter(self.data))
            self.data.pop(oldest)
        self.data[key] = value


if __name__ == "__main__":
    results = []
    results.append(check("155. Min Stack", [('(lambda s: [s.push(-2), s.push(0), s.push(-3), s.getMin(), s.pop(), s.top(), s.getMin()])(MinStack())', [None, None, None, -3, None, 0, -2])]))
    results.append(check("232. Implement Queue using Stacks", [('(lambda q: [q.push(1), q.push(2), q.peek(), q.pop(), q.empty()])(MyQueue())', [None, None, 1, 1, False])]))
    results.append(check("225. Implement Stack using Queues", [('(lambda s: [s.push(1), s.push(2), s.top(), s.pop(), s.empty()])(MyStack())', [None, None, 2, 2, False])]))
    results.append(check("705. Design HashSet", [('(lambda h: [h.add(1), h.add(2), h.contains(1), h.contains(3), h.add(2), h.contains(2), h.remove(2), h.contains(2)])(MyHashSet())', [None, None, True, False, None, True, None, False])]))
    results.append(check("706. Design HashMap", [('(lambda m: [m.put(1, 1), m.put(2, 2), m.get(1), m.get(3), m.put(2, 1), m.get(2), m.remove(2), m.get(2)])(MyHashMap())', [None, None, 1, -1, None, 1, None, -1]), ('(lambda m: [m.put(1, 5), m.put(1001, 7), m.get(1), m.get(1001)])(MyHashMap())', [None, None, 5, 7])]))
    results.append(check("1603. Design Parking System", [('(lambda p: [p.addCar(1), p.addCar(2), p.addCar(3), p.addCar(1)])(ParkingSystem(1, 1, 0))', [True, True, False, False])]))
    results.append(check("1472. Design Browser History", [('(lambda b: [b.visit("google.com"), b.visit("facebook.com"), b.visit("youtube.com"), b.back(1), b.back(1), b.forward(1), b.visit("linkedin.com"), b.forward(2), b.back(2), b.back(7)])(BrowserHistory("leetcode.com"))', [None, None, None, 'facebook.com', 'google.com', 'facebook.com', None, 'linkedin.com', 'google.com', 'leetcode.com'])]))
    results.append(check("622. Design Circular Queue", [('(lambda q: [q.enQueue(1), q.enQueue(2), q.enQueue(3), q.enQueue(4), q.Rear(), q.isFull(), q.deQueue(), q.enQueue(4), q.Rear()])(MyCircularQueue(3))', [True, True, True, False, 3, True, True, True, 4])]))
    results.append(check("2043. Simple Bank System", [('(lambda b: [b.withdraw(3, 10), b.transfer(5, 1, 20), b.deposit(5, 20), b.transfer(3, 4, 15), b.withdraw(10, 50)])(Bank([10, 100, 20, 50, 30]))', [True, True, True, False, False])]))
    results.append(check("146. LRU Cache", [('(lambda c: [c.put(1, 1), c.put(2, 2), c.get(1), c.put(3, 3), c.get(2), c.put(4, 4), c.get(1), c.get(3), c.get(4)])(LRUCache(2))', [None, None, 1, None, -1, None, -1, 3, 4])]))
    if all(results):
        print("Every solution passes its tests.")
