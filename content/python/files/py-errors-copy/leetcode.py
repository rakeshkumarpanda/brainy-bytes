# 1.4 Exceptions in depth, copying and serialisation
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


# ================================================================== 138. Copy List with Random Pointer (Medium)
# https://leetcode.com/problems/copy-list-with-random-pointer/
# Pattern: Deep copy with a memo dict
# Idea: Map every old node to its new copy in a dict, exactly like copy.deepcopy does with its memo.
# Then set next and random from the map.

class RandomNode:
    def __init__(self, x, next=None, random=None):
        self.val = x
        self.next = next
        self.random = random


def copy_random_list(head):
    if head is None:
        return None
    new_of = {}
    node = head
    while node:
        new_of[node] = RandomNode(node.val)
        node = node.next
    node = head
    while node:
        new_of[node].next = new_of.get(node.next)
        new_of[node].random = new_of.get(node.random)
        node = node.next
    return new_of[head]


def build_random_list(pairs):
    nodes = [RandomNode(v) for v, r in pairs]
    for i in range(len(nodes)):
        nodes[i].next = nodes[i + 1] if i + 1 < len(nodes) else None
        nodes[i].random = nodes[pairs[i][1]] if pairs[i][1] is not None else None
    return nodes[0] if nodes else None


def dump_random_list(head):
    nodes = []
    while head:
        nodes.append(head)
        head = head.next
    return [[n.val, nodes.index(n.random) if n.random else None] for n in nodes]


# ================================================================== 133. Clone Graph (Medium)
# https://leetcode.com/problems/clone-graph/
# Pattern: DFS with a memo, like deepcopy
# Idea: Copy a node, remember the copy, then copy its neighbours. The memo stops the copy from
# looping forever around cycles.

class GraphNode:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


def clone_graph(node):
    copies = {}

    def clone(n):
        if n in copies:
            return copies[n]
        twin = GraphNode(n.val)
        copies[n] = twin
        for m in n.neighbors:
            twin.neighbors.append(clone(m))
        return twin
    return clone(node) if node else None


def build_graph(adj):
    nodes = [GraphNode(i + 1) for i in range(len(adj))]
    for i, nbrs in enumerate(adj):
        nodes[i].neighbors = [nodes[j - 1] for j in nbrs]
    return nodes[0]


def dump_graph(start):
    seen, order = {start.val: start}, [start]
    for node in order:
        for m in node.neighbors:
            if m.val not in seen:
                seen[m.val] = m
                order.append(m)
    return [[m.val for m in seen[v].neighbors] for v in sorted(seen)]


# ================================================================== 297. Serialize and Deserialize Binary Tree (Hard)
# https://leetcode.com/problems/serialize-and-deserialize-binary-tree/
# Pattern: Preorder with markers
# Idea: Write the tree in preorder with # for an empty child. Read it back with an iterator,
# building the left subtree before the right. This is pickling by hand.

class Codec:
    def serialize(self, root):
        parts = []

        def walk(node):
            if node is None:
                parts.append("#")
                return
            parts.append(str(node.val))
            walk(node.left)
            walk(node.right)
        walk(root)
        return ",".join(parts)

    def deserialize(self, data):
        tokens = iter(data.split(","))

        def build():
            token = next(tokens)
            if token == "#":
                return None
            node = TreeNode(int(token))
            node.left = build()
            node.right = build()
            return node
        return build()


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


def tree_to_list(root):
    """The level order list of a tree, without trailing None values (helper for the tests)."""
    out, queue = [], [root]
    while queue:
        node = queue.pop(0)
        if node is None:
            out.append(None)
        else:
            out.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


# ================================================================== 449. Serialize and Deserialize BST (Medium)
# https://leetcode.com/problems/serialize-and-deserialize-bst/
# Pattern: Preorder values and bounds
# Idea: A BST is fixed by its preorder alone. Rebuild it by giving each value a range (low, high) it
# must fit in.

class BSTCodec:  # called Codec on LeetCode
    def serialize(self, root):
        values = []

        def walk(node):
            if node:
                values.append(str(node.val))
                walk(node.left)
                walk(node.right)
        walk(root)
        return " ".join(values)

    def deserialize(self, data):
        values = [int(v) for v in data.split()]
        pos = [0]

        def build(low, high):
            if pos[0] == len(values) or not low < values[pos[0]] < high:
                return None
            node = TreeNode(values[pos[0]])
            pos[0] += 1
            node.left = build(low, node.val)
            node.right = build(node.val, high)
            return node
        return build(float("-inf"), float("inf"))


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


def tree_to_list(root):
    """The level order list of a tree, without trailing None values (helper for the tests)."""
    out, queue = [], [root]
    while queue:
        node = queue.pop(0)
        if node is None:
            out.append(None)
        else:
            out.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


# ================================================================== 535. Encode and Decode TinyURL (Medium)
# https://leetcode.com/problems/encode-and-decode-tinyurl/
# Pattern: A counter and two dicts
# Idea: Give each new long URL the next number as its short code, and remember both directions.

class TinyCodec:  # called Codec on LeetCode
    def __init__(self):
        self.short_of = {}
        self.long_of = {}

    def encode(self, longUrl):
        if longUrl not in self.short_of:
            code = str(len(self.long_of) + 1)
            self.short_of[longUrl] = "http://tinyurl.com/" + code
            self.long_of["http://tinyurl.com/" + code] = longUrl
        return self.short_of[longUrl]

    def decode(self, shortUrl):
        return self.long_of[shortUrl]


# ================================================================== 606. Construct String from Binary Tree (Easy)
# https://leetcode.com/problems/construct-string-from-binary-tree/
# Pattern: Preorder with brackets
# Idea: Write the value, then the left child in brackets, then the right child in brackets. Keep ()
# for a missing left child only when a right child exists.

def tree2str(root):
    if root is None:
        return ""
    text = str(root.val)
    if root.left or root.right:
        text += "(" + tree2str(root.left) + ")"
    if root.right:
        text += "(" + tree2str(root.right) + ")"
    return text


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


def tree_to_list(root):
    """The level order list of a tree, without trailing None values (helper for the tests)."""
    out, queue = [], [root]
    while queue:
        node = queue.pop(0)
        if node is None:
            out.append(None)
        else:
            out.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


# ================================================================== 331. Verify Preorder Serialization of a Binary Tree (Medium)
# https://leetcode.com/problems/verify-preorder-serialization-of-a-binary-tree/
# Pattern: Count open slots
# Idea: Start with one slot. Every token fills a slot, and a number opens two more. The string is
# valid if slots never go below zero and end at zero.

def is_valid_serialization(preorder):
    slots = 1
    for token in preorder.split(","):
        if slots == 0:
            return False
        slots -= 1
        if token != "#":
            slots += 2
    return slots == 0


# ================================================================== 652. Find Duplicate Subtrees (Medium)
# https://leetcode.com/problems/find-duplicate-subtrees/
# Pattern: Serialise every subtree
# Idea: Turn each subtree into a string (its own little pickle). Count the strings and report a root
# the second time its string appears.

def find_duplicate_subtrees(root):
    count = {}
    result = []

    def key(node):
        if node is None:
            return "#"
        k = str(node.val) + "," + key(node.left) + "," + key(node.right)
        count[k] = count.get(k, 0) + 1
        if count[k] == 2:
            result.append(node)
        return k
    key(root)
    return result


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


def tree_to_list(root):
    """The level order list of a tree, without trailing None values (helper for the tests)."""
    out, queue = [], [root]
    while queue:
        node = queue.pop(0)
        if node is None:
            out.append(None)
        else:
            out.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


# ================================================================== 394. Decode String (Medium)
# https://leetcode.com/problems/decode-string/
# Pattern: A stack of unfinished parts
# Idea: Read the text once. A number before [ says how many times to repeat. On [ save the text so
# far and the count on a stack. On ] repeat the inner text and glue it to the saved text. This is
# how a loader rebuilds nested data from a flat string.

def decode_string(s):
    stack = []
    text = ""
    count = 0
    for ch in s:
        if ch.isdigit():
            count = count * 10 + int(ch)
        elif ch == "[":
            stack.append((text, count))
            text = ""
            count = 0
        elif ch == "]":
            before, times = stack.pop()
            text = before + text * times
        else:
            text = text + ch
    return text


# ================================================================== 1106. Parsing A Boolean Expression (Hard)
# https://leetcode.com/problems/parsing-a-boolean-expression/
# Pattern: A stack of values and operators
# Idea: Push every character except commas. On ) pop the values back to the (, take the operator in
# front of it, and push the single result. Nested expressions are solved from the inside out.

def parse_bool_expr(expression):
    stack = []
    for ch in expression:
        if ch == ",":
            continue
        if ch != ")":
            stack.append(ch)
            continue
        values = []
        while stack[-1] != "(":
            values.append(stack.pop() == "t")
        stack.pop()                            # the "("
        op = stack.pop()
        if op == "!":
            result = not values[0]
        elif op == "&":
            result = all(values)
        else:
            result = any(values)
        stack.append("t" if result else "f")
    return stack[-1] == "t"


if __name__ == "__main__":
    results = []
    results.append(check("138. Copy List with Random Pointer", [('(lambda h: (dump_random_list(copy_random_list(h)), copy_random_list(h) is not h))(build_random_list([[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]))', [[[7, None], [13, 0], [11, 4], [10, 2], [1, 0]], True])]))
    results.append(check("133. Clone Graph", [('(lambda g: (dump_graph(clone_graph(g)), clone_graph(g) is not g))(build_graph([[2, 4], [1, 3], [2, 4], [1, 3]]))', [[[2, 4], [1, 3], [2, 4], [1, 3]], True])]))
    results.append(check("297. Serialize and Deserialize Binary Tree", [('tree_to_list(Codec().deserialize(Codec().serialize(build_tree([1, 2, 3, None, None, 4, 5]))))', [1, 2, 3, None, None, 4, 5]), ('Codec().serialize(build_tree([1, 2]))', '1,2,#,#,#')]))
    results.append(check("449. Serialize and Deserialize BST", [('tree_to_list(BSTCodec().deserialize(BSTCodec().serialize(build_tree([2, 1, 3]))))', [2, 1, 3]), ('BSTCodec().serialize(build_tree([5, 3, 8, 1, 4]))', '5 3 1 4 8')]))
    results.append(check("535. Encode and Decode TinyURL", [('(lambda c: c.decode(c.encode("https://leetcode.com/problems/design-tinyurl")))(TinyCodec())', 'https://leetcode.com/problems/design-tinyurl'), ('(lambda c: (c.encode("a"), c.encode("b"), c.encode("a")))(TinyCodec())', ['http://tinyurl.com/1', 'http://tinyurl.com/2', 'http://tinyurl.com/1'])]))
    results.append(check("606. Construct String from Binary Tree", [('tree2str(build_tree([1, 2, 3, 4]))', '1(2(4))(3)'), ('tree2str(build_tree([1, 2, 3, None, 4]))', '1(2()(4))(3)')]))
    results.append(check("331. Verify Preorder Serialization of a Binary Tree", [('is_valid_serialization("9,3,4,#,#,1,#,#,2,#,6,#,#")', True), ('is_valid_serialization("1,#")', False), ('is_valid_serialization("9,#,#,1")', False)]))
    results.append(check("652. Find Duplicate Subtrees", [('sorted(tree_to_list(n) for n in find_duplicate_subtrees(build_tree([1, 2, 3, 4, None, 2, 4, None, None, 4])))', [[2, 4], [4]])]))
    results.append(check("394. Decode String", [('decode_string("3[a]2[bc]")', 'aaabcbc'), ('decode_string("3[a2[c]]")', 'accaccacc'), ('decode_string("2[abc]3[cd]ef")', 'abcabccdcdcdef')]))
    results.append(check("1106. Parsing A Boolean Expression", [('parse_bool_expr("&(|(f))")', False), ('parse_bool_expr("|(f,f,f,t)")', True), ('parse_bool_expr("!(&(f,t))")', True), ('parse_bool_expr("t")', True)]))
    if all(results):
        print("Every solution passes its tests.")
