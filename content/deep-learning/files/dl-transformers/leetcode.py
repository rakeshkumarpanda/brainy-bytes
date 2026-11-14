# 2.3 Attention and transformers
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
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


# ================================================================== 706. Design HashMap (Easy)
# https://leetcode.com/problems/design-hashmap/
# Pattern: Buckets of key value pairs chosen by key modulo the size
# Idea: Hash each key to a bucket and keep a small list of pairs there. A hash map is hard
# attention: a query matches exactly one key and returns its value. Self attention is the soft
# version, matching every key a little and blending the values. Our helper runs a list of
# operations.

class MyHashMap:
    def __init__(self, size=1009):
        self.buckets = [[] for _ in range(size)]

    def _bucket(self, key):
        return self.buckets[key % len(self.buckets)]

    def put(self, key, value):
        b = self._bucket(key)
        for pair in b:
            if pair[0] == key:
                pair[1] = value
                return
        b.append([key, value])

    def get(self, key):
        for k, v in self._bucket(key):
            if k == key:
                return v
        return -1

    def remove(self, key):
        b = self._bucket(key)
        b[:] = [p for p in b if p[0] != key]


def run_hashmap(ops):
    m, out = MyHashMap(), []
    for op in ops:
        if op[0] == 'put':
            m.put(op[1], op[2])
        elif op[0] == 'get':
            out.append(m.get(op[1]))
        else:
            m.remove(op[1])
    return out


# ================================================================== 208. Implement Trie (Prefix Tree) (Medium)
# https://leetcode.com/problems/implement-trie-prefix-tree/
# Pattern: Nested dictionaries, one level per character, with an end marker
# Idea: Walk one character at a time, creating children as needed. Tokenisers for transformers, such
# as byte pair encoding, look up the longest known piece of text quickly with exactly this
# structure. Our helper inserts words and answers queries.

class Trie:
    def __init__(self):
        self.root = {}

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node['$'] = True

    def search(self, word):
        node = self._walk(word)
        return node is not None and '$' in node

    def startsWith(self, prefix):
        return self._walk(prefix) is not None

    def _walk(self, s):
        node = self.root
        for ch in s:
            if ch not in node:
                return None
            node = node[ch]
        return node


def run_trie(words, queries):
    t = Trie()
    for w in words:
        t.insert(w)
    return [t.search(q) if kind == 'search' else t.startsWith(q) for kind, q in queries]


# ================================================================== 981. Time Based Key-Value Store (Medium)
# https://leetcode.com/problems/time-based-key-value-store/
# Pattern: Keep timestamps sorted per key and binary search the latest one not after t
# Idea: Store each key’s values in time order and use bisect to find the last one at or before the
# query time. Only looking at entries up to the current time is the idea behind the causal mask in a
# GPT style decoder.

import bisect
from collections import defaultdict


class TimeMap:
    def __init__(self):
        self.times = defaultdict(list)
        self.values = defaultdict(list)

    def set(self, key, value, timestamp):
        self.times[key].append(timestamp)
        self.values[key].append(value)

    def get(self, key, timestamp):
        i = bisect.bisect_right(self.times[key], timestamp)
        return self.values[key][i - 1] if i else ''


def run_timemap(ops):
    tm, out = TimeMap(), []
    for op in ops:
        if op[0] == 'set':
            tm.set(*op[1:])
        else:
            out.append(tm.get(*op[1:]))
    return out


# ================================================================== 215. Kth Largest Element in an Array (Medium)
# https://leetcode.com/problems/kth-largest-element-in-an-array/
# Pattern: A min heap of size k keeps the k largest values seen so far
# Idea: Push each value and pop the smallest whenever the heap grows past k. The top of the heap is
# the answer. Top k sampling does this every time a language model picks a token: keep the k most
# likely tokens and sample among them.

import heapq


def find_kth_largest(nums, k):
    heap = []
    for v in nums:
        heapq.heappush(heap, v)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]


# ================================================================== 23. Merge k Sorted Lists (Hard)
# https://leetcode.com/problems/merge-k-sorted-lists/
# Pattern: A heap holds the current head of every list
# Idea: Put the first node of each list in a min heap. Pop the smallest, attach it, and push its
# successor. Beam search for text generation keeps a similar heap of the best partial sequences and
# expands the most promising ones. Our helper builds linked lists from Python lists.

import heapq


class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next


def merge_k_lists(lists):
    heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
    heapq.heapify(heap)
    dummy = tail = ListNode()
    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next


def merge_k_sorted(arrays):
    def build(vals):
        head = None
        for v in reversed(vals):
            head = ListNode(v, head)
        return head
    out, node = [], merge_k_lists([build(a) for a in arrays])
    while node:
        out.append(node.val)
        node = node.next
    return out


if __name__ == "__main__":
    results = []
    results.append(check("706. Design HashMap", [("run_hashmap([('put', 1, 1), ('put', 2, 2), ('get', 1), ('get', 3), ('put', 2, 1), ('get', 2), ('remove', 2), ('get', 2)])", [1, -1, 1, -1])]))
    results.append(check("208. Implement Trie (Prefix Tree)", [("run_trie(['apple'], [('search', 'apple'), ('search', 'app'), ('prefix', 'app')])", [True, False, True])]))
    results.append(check("981. Time Based Key-Value Store", [("run_timemap([('set', 'foo', 'bar', 1), ('get', 'foo', 1), ('get', 'foo', 3), ('set', 'foo', 'bar2', 4), ('get', 'foo', 4), ('get', 'foo', 5), ('get', 'foo', 0)])", ['bar', 'bar', 'bar2', 'bar2', ''])]))
    results.append(check("215. Kth Largest Element in an Array", [('find_kth_largest([3, 2, 1, 5, 6, 4], 2)', 5), ('find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4)', 4)]))
    results.append(check("23. Merge k Sorted Lists", [('merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]])', [1, 1, 2, 3, 4, 4, 5, 6]), ('merge_k_sorted([])', []), ('merge_k_sorted([[]])', [])]))
    if all(results):
        print("Every solution passes its tests.")
