# 2.1 Iterators and generators
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


# ================================================================== 94. Binary Tree Inorder Traversal (Easy)
# https://leetcode.com/problems/binary-tree-inorder-traversal/
# Pattern: A recursive generator with yield from
# Idea: Yield everything from the left subtree, then the node, then everything from the right
# subtree.

def inorder(node):
    if node:
        yield from inorder(node.left)
        yield node.val
        yield from inorder(node.right)


def inorder_traversal(root):
    return list(inorder(root))


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values):
    """Build a tree from a level order list like [1, 2, 3, None, 4] (helper for the tests)."""
    if not values:
        return None
    nodes = [None if v is None else TreeNode(v) for v in values]
    kids = nodes[1:]
    k = 0
    for node in nodes:
        if node is not None:
            if k < len(kids):
                node.left = kids[k]
            if k + 1 < len(kids):
                node.right = kids[k + 1]
            k += 2
    return nodes[0]


# ================================================================== 173. Binary Search Tree Iterator (Medium)
# https://leetcode.com/problems/binary-search-tree-iterator/
# Pattern: Keep one generator inside the class
# Idea: An inorder generator of a BST gives the values in sorted order. next takes the next value.
# To answer hasNext, look one value ahead and remember it.

class BSTIterator:
    def __init__(self, root):
        self.values = self.walk(root)
        self.ahead = next(self.values, None)

    def walk(self, node):
        if node:
            yield from self.walk(node.left)
            yield node.val
            yield from self.walk(node.right)

    def next(self):
        value = self.ahead
        self.ahead = next(self.values, None)
        return value

    def hasNext(self):
        return self.ahead is not None


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values):
    """Build a tree from a level order list like [1, 2, 3, None, 4] (helper for the tests)."""
    if not values:
        return None
    nodes = [None if v is None else TreeNode(v) for v in values]
    kids = nodes[1:]
    k = 0
    for node in nodes:
        if node is not None:
            if k < len(kids):
                node.left = kids[k]
            if k + 1 < len(kids):
                node.right = kids[k + 1]
            k += 2
    return nodes[0]


# ================================================================== 1305. All Elements in Two Binary Search Trees (Medium)
# https://leetcode.com/problems/all-elements-in-two-binary-search-trees/
# Pattern: Merge two sorted generators
# Idea: Each BST gives a sorted stream with an inorder generator. heapq.merge joins sorted streams
# lazily, like the merge step of merge sort.

import heapq


def sorted_values(node):
    if node:
        yield from sorted_values(node.left)
        yield node.val
        yield from sorted_values(node.right)


def get_all_elements(root1, root2):
    return list(heapq.merge(sorted_values(root1), sorted_values(root2)))


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values):
    """Build a tree from a level order list like [1, 2, 3, None, 4] (helper for the tests)."""
    if not values:
        return None
    nodes = [None if v is None else TreeNode(v) for v in values]
    kids = nodes[1:]
    k = 0
    for node in nodes:
        if node is not None:
            if k < len(kids):
                node.left = kids[k]
            if k + 1 < len(kids):
                node.right = kids[k + 1]
            k += 2
    return nodes[0]


# ================================================================== 23. Merge k Sorted Lists (Hard)
# https://leetcode.com/problems/merge-k-sorted-lists/
# Pattern: Turn each list into a generator, then heapq.merge
# Idea: A small generator walks one linked list. heapq.merge takes k sorted streams and always hands
# out the smallest next value, using a heap of size k.

import heapq


def walk(node):
    while node:
        yield node.val
        node = node.next


def merge_k_lists(lists):
    dummy = tail = ListNode()
    for value in heapq.merge(*[walk(head) for head in lists]):
        tail.next = ListNode(value)
        tail = tail.next
    return dummy.next


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_list(values):
    """Build a linked list from a Python list (helper for the tests)."""
    head = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head


def list_values(head):
    """The values of a linked list as a Python list (helper for the tests)."""
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


# ================================================================== 77. Combinations (Medium)
# https://leetcode.com/problems/combinations/
# Pattern: A backtracking generator
# Idea: Choose the next number from start to n, yield when k numbers are chosen.
# itertools.combinations does the same in C.

def choose(start, n, k, chosen):
    if len(chosen) == k:
        yield list(chosen)
        return
    for number in range(start, n + 1):
        chosen.append(number)
        yield from choose(number + 1, n, k, chosen)
        chosen.pop()


def combine(n, k):
    return list(choose(1, n, k, []))


# ================================================================== 90. Subsets II (Medium)
# https://leetcode.com/problems/subsets-ii/
# Pattern: Sort, then skip equal neighbours
# Idea: Sort first so equal numbers sit together. At each depth, do not start a branch with the same
# number twice.

def build_subsets(nums, start, chosen):
    yield list(chosen)
    for i in range(start, len(nums)):
        if i > start and nums[i] == nums[i - 1]:
            continue
        chosen.append(nums[i])
        yield from build_subsets(nums, i + 1, chosen)
        chosen.pop()


def subsets_with_dup(nums):
    return list(build_subsets(sorted(nums), 0, []))


# ================================================================== 216. Combination Sum III (Medium)
# https://leetcode.com/problems/combination-sum-iii/
# Pattern: Filter a combinations stream
# Idea: Every answer is a set of k different digits from 1 to 9. Generate the combinations lazily
# and keep the ones whose sum is n.

from itertools import combinations


def combination_sum3(k, n):
    result = []
    for combo in combinations(range(1, 10), k):
        if sum(combo) == n:
            result.append(list(combo))
    return result


# ================================================================== 401. Binary Watch (Easy)
# https://leetcode.com/problems/binary-watch/
# Pattern: Loop over every time, count the lit bits
# Idea: There are only 12 × 60 times. For each one count the 1 bits of the hour and the minute with
# bin(x).count("1").

def times_with_leds(turned_on):
    for hour in range(12):
        for minute in range(60):
            if bin(hour).count("1") + bin(minute).count("1") == turned_on:
                yield str(hour) + ":" + str(minute).zfill(2)


def read_binary_watch(turnedOn):
    return list(times_with_leds(turnedOn))


# ================================================================== 1415. The k-th Lexicographical String of All Happy Strings of Length n (Medium)
# https://leetcode.com/problems/the-k-th-lexicographical-string-of-all-happy-strings-of-length-n/
# Pattern: Generate in order, stop at k
# Idea: A generator makes happy strings in alphabetical order. islice jumps to the k-th one without
# building the rest.

from itertools import islice


def happy(n, text):
    if len(text) == n:
        yield text
        return
    for ch in "abc":
        if not text or text[-1] != ch:
            yield from happy(n, text + ch)


def get_happy_string(n, k):
    return next(islice(happy(n, ""), k - 1, None), "")


# ================================================================== 119. Pascal's Triangle II (Easy)
# https://leetcode.com/problems/pascals-triangle-ii/
# Pattern: A generator of rows
# Idea: Each row is made from the one before: add neighbours and put 1 at both ends. Yield rows one
# by one and keep the one you need.

def pascal_rows():
    row = [1]
    while True:
        yield row
        middle = []
        for i in range(len(row) - 1):
            middle.append(row[i] + row[i + 1])
        row = [1] + middle + [1]


def get_row(rowIndex):
    for index, row in enumerate(pascal_rows()):
        if index == rowIndex:
            return row


if __name__ == "__main__":
    results = []
    results.append(check("94. Binary Tree Inorder Traversal", [('inorder_traversal(build_tree([1, None, 2, 3]))', [1, 3, 2]), ('inorder_traversal(build_tree([]))', [])]))
    results.append(check("173. Binary Search Tree Iterator", [('(lambda it: [it.next(), it.next(), it.hasNext(), it.next(), it.hasNext(), it.next(), it.hasNext(), it.next(), it.hasNext()])(BSTIterator(build_tree([7, 3, 15, None, None, 9, 20])))', [3, 7, True, 9, True, 15, True, 20, False])]))
    results.append(check("1305. All Elements in Two Binary Search Trees", [('get_all_elements(build_tree([2, 1, 4]), build_tree([1, 0, 3]))', [0, 1, 1, 2, 3, 4]), ('get_all_elements(build_tree([1, None, 8]), build_tree([8, 1]))', [1, 1, 8, 8])]))
    results.append(check("23. Merge k Sorted Lists", [('list_values(merge_k_lists([build_list([1, 4, 5]), build_list([1, 3, 4]), build_list([2, 6])]))', [1, 1, 2, 3, 4, 4, 5, 6]), ('list_values(merge_k_lists([]))', [])]))
    results.append(check("77. Combinations", [('combine(4, 2)', [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]), ('combine(1, 1)', [[1]])]))
    results.append(check("90. Subsets II", [('subsets_with_dup([1, 2, 2])', [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]), ('subsets_with_dup([0])', [[], [0]])]))
    results.append(check("216. Combination Sum III", [('combination_sum3(3, 7)', [[1, 2, 4]]), ('combination_sum3(3, 9)', [[1, 2, 6], [1, 3, 5], [2, 3, 4]]), ('combination_sum3(4, 1)', [])]))
    results.append(check("401. Binary Watch", [('read_binary_watch(1)', ['0:01', '0:02', '0:04', '0:08', '0:16', '0:32', '1:00', '2:00', '4:00', '8:00']), ('read_binary_watch(9)', [])]))
    results.append(check("1415. The k-th Lexicographical String of All Happy Strings of Length n", [('get_happy_string(1, 3)', 'c'), ('get_happy_string(1, 4)', ''), ('get_happy_string(3, 9)', 'cab')]))
    results.append(check("119. Pascal's Triangle II", [('get_row(3)', [1, 3, 3, 1]), ('get_row(0)', [1]), ('get_row(5)', [1, 5, 10, 10, 5, 1])]))
    if all(results):
        print("Every solution passes its tests.")
