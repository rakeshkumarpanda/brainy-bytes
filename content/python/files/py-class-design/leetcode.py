# 1.3 Class design: methods, properties, abstract classes and dataclasses
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


# ================================================================== 1146. Snapshot Array (Medium)
# https://leetcode.com/problems/snapshot-array/
# Pattern: Per index history plus binary search
# Idea: For each index keep a list of (snap id, value) changes. get looks for the last change at or
# before the snap id with bisect.

import bisect


class SnapshotArray:
    def __init__(self, length):
        self.history = [[(-1, 0)] for i in range(length)]
        self.snap_id = 0

    def set(self, index, val):
        changes = self.history[index]
        if changes[-1][0] == self.snap_id:
            changes[-1] = (self.snap_id, val)
        else:
            changes.append((self.snap_id, val))

    def snap(self):
        self.snap_id += 1
        return self.snap_id - 1

    def get(self, index, snap_id):
        changes = self.history[index]
        pos = bisect.bisect_right(changes, (snap_id, float("inf"))) - 1
        return changes[pos][1]


# ================================================================== 981. Time Based Key-Value Store (Medium)
# https://leetcode.com/problems/time-based-key-value-store/
# Pattern: Lists of times per key, bisect
# Idea: Timestamps arrive in increasing order, so each key keeps a sorted list. get finds the last
# time not after the asked time.

import bisect


class TimeMap:
    def __init__(self):
        self.times = {}
        self.values = {}

    def set(self, key, value, timestamp):
        self.times.setdefault(key, []).append(timestamp)
        self.values.setdefault(key, []).append(value)

    def get(self, key, timestamp):
        times = self.times.get(key, [])
        pos = bisect.bisect_right(times, timestamp) - 1
        return self.values[key][pos] if pos >= 0 else ""


# ================================================================== 1797. Design Authentication Manager (Medium)
# https://leetcode.com/problems/design-authentication-manager/
# Pattern: A dict of expiry times
# Idea: Store when each token expires. renew only works while the token is alive. Count the tokens
# that expire after the current time.

class AuthenticationManager:
    def __init__(self, timeToLive):
        self.ttl = timeToLive
        self.expires = {}

    def generate(self, tokenId, currentTime):
        self.expires[tokenId] = currentTime + self.ttl

    def renew(self, tokenId, currentTime):
        if self.expires.get(tokenId, 0) > currentTime:
            self.expires[tokenId] = currentTime + self.ttl

    def countUnexpiredTokens(self, currentTime):
        return sum(1 for t in self.expires.values() if t > currentTime)


# ================================================================== 1500. Design a File Sharing System (Medium)
# https://leetcode.com/problems/design-a-file-sharing-system/
# Pattern: Reuse the smallest free id with a heap
# Idea: Hand out ids from a heap of freed ids first, then new ids. Each user has a set of chunks.

import heapq


class FileSharing:
    def __init__(self, m):
        self.free_ids = []
        self.next_id = 1
        self.owned = {}                        # user id: set of chunks

    def join(self, ownedChunks):
        if self.free_ids:
            user = heapq.heappop(self.free_ids)
        else:
            user = self.next_id
            self.next_id += 1
        self.owned[user] = set(ownedChunks)
        return user

    def leave(self, userID):
        del self.owned[userID]
        heapq.heappush(self.free_ids, userID)

    def request(self, userID, chunkID):
        holders = sorted(u for u, chunks in self.owned.items() if chunkID in chunks)
        if holders:
            self.owned[userID].add(chunkID)
        return holders


# ================================================================== 1244. Design A Leaderboard (Medium)
# https://leetcode.com/problems/design-a-leaderboard/
# Pattern: A dict of scores
# Idea: addScore adds to a player, top sorts the scores and adds the K biggest, reset sets a player
# back to 0.

class Leaderboard:
    def __init__(self):
        self.scores = {}

    def addScore(self, playerId, score):
        self.scores[playerId] = self.scores.get(playerId, 0) + score

    def top(self, K):
        return sum(sorted(self.scores.values(), reverse=True)[:K])

    def reset(self, playerId):
        self.scores[playerId] = 0


# ================================================================== 2526. Find Consecutive Integers from a Data Stream (Medium)
# https://leetcode.com/problems/find-consecutive-integers-from-a-data-stream/
# Pattern: Count the current run
# Idea: Keep how many values in a row have equalled value. consec returns whether that run has
# reached k.

class DataStream:
    def __init__(self, value, k):
        self.value = value
        self.k = k
        self.run = 0

    def consec(self, num):
        if num == self.value:
            self.run += 1
        else:
            self.run = 0
        return self.run >= self.k


# ================================================================== 2296. Design a Text Editor (Hard)
# https://leetcode.com/problems/design-a-text-editor/
# Pattern: Two stacks around the cursor
# Idea: Keep the text left of the cursor and the text right of it (reversed) as two lists. Every
# operation moves characters between them.

class TextEditor:
    def __init__(self):
        self.left = []
        self.right = []                        # reversed: right[-1] is just after the cursor

    def addText(self, text):
        self.left.extend(text)

    def deleteText(self, k):
        count = min(k, len(self.left))
        for i in range(count):
            self.left.pop()
        return count

    def cursorLeft(self, k):
        for i in range(min(k, len(self.left))):
            self.right.append(self.left.pop())
        return "".join(self.left[-10:])

    def cursorRight(self, k):
        for i in range(min(k, len(self.right))):
            self.left.append(self.right.pop())
        return "".join(self.left[-10:])


# ================================================================== 1825. Finding MK Average (Hard)
# https://leetcode.com/problems/finding-mk-average/
# Pattern: Keep the last m values, sort when asked
# Idea: A deque keeps the last m values. To answer, sort them, drop k from each end and average the
# middle. Simple, and fine for small m.

from collections import deque


class MKAverage:
    def __init__(self, m, k):
        self.m = m
        self.k = k
        self.last = deque()

    def addElement(self, num):
        self.last.append(num)
        if len(self.last) > self.m:
            self.last.popleft()

    def calculateMKAverage(self):
        if len(self.last) < self.m:
            return -1
        middle = sorted(self.last)[self.k:self.m - self.k]
        return sum(middle) // len(middle)


# ================================================================== 2034. Stock Price Fluctuation (Medium)
# https://leetcode.com/problems/stock-price-fluctuation/
# Pattern: Dict plus two lazy heaps
# Idea: Store the price at each time. Push into a max heap and a min heap, and skip heap tops whose
# price was later corrected.

import heapq


class StockPrice:
    def __init__(self):
        self.price_at = {}
        self.latest = 0
        self.low = []
        self.high = []

    def update(self, timestamp, price):
        self.price_at[timestamp] = price
        self.latest = max(self.latest, timestamp)
        heapq.heappush(self.low, (price, timestamp))
        heapq.heappush(self.high, (-price, timestamp))

    def current(self):
        return self.price_at[self.latest]

    def maximum(self):
        while -self.high[0][0] != self.price_at[self.high[0][1]]:
            heapq.heappop(self.high)
        return -self.high[0][0]

    def minimum(self):
        while self.low[0][0] != self.price_at[self.low[0][1]]:
            heapq.heappop(self.low)
        return self.low[0][0]


# ================================================================== 1600. Throne Inheritance (Medium)
# https://leetcode.com/problems/throne-inheritance/
# Pattern: A family tree and a preorder walk
# Idea: Keep each person's children in birth order and a set of the dead. The order of succession is
# a preorder walk that skips the dead.

class ThroneInheritance:
    def __init__(self, kingName):
        self.king = kingName
        self.children = {kingName: []}
        self.dead = set()

    def birth(self, parentName, childName):
        self.children[parentName].append(childName)
        self.children[childName] = []

    def death(self, name):
        self.dead.add(name)

    def getInheritanceOrder(self):
        order = []
        stack = [self.king]
        while stack:
            person = stack.pop()
            if person not in self.dead:
                order.append(person)
            stack.extend(reversed(self.children[person]))
        return order


if __name__ == "__main__":
    results = []
    results.append(check("1146. Snapshot Array", [('(lambda a: [a.set(0, 5), a.snap(), a.set(0, 6), a.get(0, 0)])(SnapshotArray(3))', [None, 0, None, 5])]))
    results.append(check("981. Time Based Key-Value Store", [('(lambda t: [t.set("foo", "bar", 1), t.get("foo", 1), t.get("foo", 3), t.set("foo", "bar2", 4), t.get("foo", 4), t.get("foo", 5), t.get("foo", 0)])(TimeMap())', [None, 'bar', 'bar', None, 'bar2', 'bar2', ''])]))
    results.append(check("1797. Design Authentication Manager", [('(lambda a: [a.renew("aaa", 1), a.generate("aaa", 2), a.countUnexpiredTokens(6), a.generate("bbb", 7), a.renew("aaa", 8), a.renew("bbb", 10), a.countUnexpiredTokens(15)])(AuthenticationManager(5))', [None, None, 1, None, None, None, 0])]))
    results.append(check("1500. Design a File Sharing System", [('(lambda f: [f.join([1, 2]), f.join([2, 3]), f.join([4]), f.request(1, 3), f.request(2, 2), f.leave(1), f.request(2, 1), f.leave(2), f.join([])])(FileSharing(4))', [1, 2, 3, [2], [1, 2], None, [], None, 1])]))
    results.append(check("1244. Design A Leaderboard", [('(lambda b: [b.addScore(1, 73), b.addScore(2, 56), b.addScore(3, 39), b.addScore(4, 51), b.addScore(5, 4), b.top(1), b.reset(1), b.reset(2), b.addScore(2, 51), b.top(3)])(Leaderboard())', [None, None, None, None, None, 73, None, None, None, 141])]))
    results.append(check("2526. Find Consecutive Integers from a Data Stream", [('(lambda d: [d.consec(4), d.consec(4), d.consec(4), d.consec(3)])(DataStream(4, 3))', [False, False, True, False])]))
    results.append(check("2296. Design a Text Editor", [('(lambda e: [e.addText("leetcode"), e.deleteText(4), e.addText("practice"), e.cursorRight(3), e.cursorLeft(8), e.deleteText(10), e.cursorLeft(2), e.cursorRight(6)])(TextEditor())', [None, 4, None, 'etpractice', 'leet', 4, '', 'practi'])]))
    results.append(check("1825. Finding MK Average", [('(lambda a: [a.addElement(3), a.addElement(1), a.calculateMKAverage(), a.addElement(10), a.calculateMKAverage(), a.addElement(5), a.addElement(5), a.addElement(5), a.calculateMKAverage()])(MKAverage(3, 1))', [None, None, -1, None, 3, None, None, None, 5])]))
    results.append(check("2034. Stock Price Fluctuation", [('(lambda s: [s.update(1, 10), s.update(2, 5), s.current(), s.maximum(), s.update(1, 3), s.maximum(), s.update(4, 2), s.minimum()])(StockPrice())', [None, None, 5, 10, None, 5, None, 2])]))
    results.append(check("1600. Throne Inheritance", [('(lambda t: [t.birth("king", "andy"), t.birth("king", "bob"), t.birth("andy", "matthew"), t.death("bob"), t.getInheritanceOrder()])(ThroneInheritance("king"))', [None, None, None, None, ['king', 'andy', 'matthew']])]))
    if all(results):
        print("Every solution passes its tests.")
