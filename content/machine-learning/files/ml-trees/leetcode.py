# 3.1 Decision trees: a chain of yes or no questions
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


# ================================================================== 104. Maximum Depth of Binary Tree (Easy)
# https://leetcode.com/problems/maximum-depth-of-binary-tree/
# Pattern: Depth is one more than the deeper child
# Idea: An empty tree has depth 0. Otherwise the depth is 1 plus the larger depth of the two
# children. This is what max_depth limits in a decision tree.

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build(values):
    # build a tree from a LeetCode style level order list, None means no child
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    while queue and i < len(values):
        node = queue.pop(0)
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i = i + 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i = i + 1
    return root


def max_depth(root):
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


# ================================================================== 112. Path Sum (Easy)
# https://leetcode.com/problems/path-sum/
# Pattern: Subtract as you go down
# Idea: Walk from the root, subtracting each value from the target. At a leaf, check whether what is
# left equals the leaf value. A decision tree prediction is also one root to leaf path.

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build(values):
    # build a tree from a LeetCode style level order list, None means no child
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    while queue and i < len(values):
        node = queue.pop(0)
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i = i + 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i = i + 1
    return root


def has_path_sum(root, target):
    if root is None:
        return False
    if root.left is None and root.right is None:
        return root.val == target
    rest = target - root.val
    return has_path_sum(root.left, rest) or has_path_sum(root.right, rest)


# ================================================================== 102. Binary Tree Level Order Traversal (Medium)
# https://leetcode.com/problems/binary-tree-level-order-traversal/
# Pattern: A queue, one level at a time
# Idea: Keep a queue of the nodes on the current level. Record their values, then replace the queue
# with all their children. This breadth first order is how the animation grows the tree.

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build(values):
    # build a tree from a LeetCode style level order list, None means no child
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    while queue and i < len(values):
        node = queue.pop(0)
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i = i + 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i = i + 1
    return root


def level_order(root):
    if root is None:
        return []
    result = []
    level = [root]
    while level:
        result.append([node.val for node in level])
        nxt = []
        for node in level:
            if node.left:
                nxt.append(node.left)
            if node.right:
                nxt.append(node.right)
        level = nxt
    return result


# ================================================================== 700. Search in a Binary Search Tree (Easy)
# https://leetcode.com/problems/search-in-a-binary-search-tree/
# Pattern: Go left or right by one comparison
# Idea: At each node compare the value: smaller goes left, larger goes right. Each comparison is one
# yes or no question, exactly like a decision tree prediction.

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build(values):
    # build a tree from a LeetCode style level order list, None means no child
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    while queue and i < len(values):
        node = queue.pop(0)
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i = i + 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i = i + 1
    return root


def search_bst(root, val):
    node = root
    while node is not None and node.val != val:
        if val < node.val:
            node = node.left
        else:
            node = node.right
    return node


# ================================================================== 108. Convert Sorted Array to Binary Search Tree (Easy)
# https://leetcode.com/problems/convert-sorted-array-to-binary-search-tree/
# Pattern: Split at the middle
# Idea: Make the middle value the root, then build the left half and the right half the same way.
# Splitting into two balanced halves is what a good first question does.

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build(values):
    # build a tree from a LeetCode style level order list, None means no child
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    while queue and i < len(values):
        node = queue.pop(0)
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i = i + 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i = i + 1
    return root


def sorted_array_to_bst(nums):
    if not nums:
        return None
    mid = len(nums) // 2
    root = TreeNode(nums[mid])
    root.left = sorted_array_to_bst(nums[:mid])
    root.right = sorted_array_to_bst(nums[mid + 1:])
    return root


def inorder(root):
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)


# ================================================================== 257. Binary Tree Paths (Easy)
# https://leetcode.com/problems/binary-tree-paths/
# Pattern: Carry the path down
# Idea: Walk down carrying the path so far. At a leaf, save it. Every root to leaf path of a
# decision tree is one readable rule, such as "petal width > 0.8 and petal width ≤ 1.75 means
# versicolor".

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build(values):
    # build a tree from a LeetCode style level order list, None means no child
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    while queue and i < len(values):
        node = queue.pop(0)
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i = i + 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i = i + 1
    return root


def binary_tree_paths(root):
    paths = []

    def walk(node, path):
        if node is None:
            return
        path = path + [str(node.val)]
        if node.left is None and node.right is None:
            paths.append("->".join(path))
        walk(node.left, path)
        walk(node.right, path)

    walk(root, [])
    return paths


if __name__ == "__main__":
    results = []
    results.append(check("104. Maximum Depth of Binary Tree", [('max_depth(build([3, 9, 20, None, None, 15, 7]))', 3), ('max_depth(build([1, None, 2]))', 2)]))
    results.append(check("112. Path Sum", [('has_path_sum(build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]), 22)', True), ('has_path_sum(build([1, 2, 3]), 5)', False)]))
    results.append(check("102. Binary Tree Level Order Traversal", [('level_order(build([3, 9, 20, None, None, 15, 7]))', [[3], [9, 20], [15, 7]]), ('level_order(build([]))', [])]))
    results.append(check("700. Search in a Binary Search Tree", [('search_bst(build([4, 2, 7, 1, 3]), 2).val', 2), ('search_bst(build([4, 2, 7, 1, 3]), 5) is None', True)]))
    results.append(check("108. Convert Sorted Array to Binary Search Tree", [('inorder(sorted_array_to_bst([-10, -3, 0, 5, 9]))', [-10, -3, 0, 5, 9]), ('sorted_array_to_bst([1, 3]).val', 3)]))
    results.append(check("257. Binary Tree Paths", [('binary_tree_paths(build([1, 2, 3, None, 5]))', ['1->2->5', '1->3']), ('binary_tree_paths(build([1]))', ['1'])]))
    if all(results):
        print("Every solution passes its tests.")
