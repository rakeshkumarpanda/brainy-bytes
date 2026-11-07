# 4.1 Django basics: project, URLs, views, templates, models and admin
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


# ================================================================== 257. Binary Tree Paths (Easy)
# https://leetcode.com/problems/binary-tree-paths/
# Pattern: Depth first search that carries the path so far
# Idea: Like listing every URL of a project whose urls.py files include each other. Walk down the
# tree, add each value to the path, and save the path at every leaf.

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values):
    """Build a tree from a level order list like [1, 2, 3, None, 5] (helper for the tests)."""
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


def binary_tree_paths(root):
    paths = []

    def walk(node, path):
        if node is None:
            return
        path = path + [str(node.val)]
        if node.left is None and node.right is None:
            paths.append("->".join(path))
            return
        walk(node.left, path)
        walk(node.right, path)

    walk(root, [])
    return paths


# ================================================================== 228. Summary Ranges (Easy)
# https://leetcode.com/problems/summary-ranges/
# Pattern: Walk once and close a range when the next number is not one more
# Idea: The admin and paginators show ranges such as 1-3. Keep where the current range starts and
# close it when the numbers stop following each other.

def summary_ranges(nums):
    result = []
    i = 0
    while i < len(nums):
        start = nums[i]
        while i + 1 < len(nums) and nums[i + 1] == nums[i] + 1:
            i += 1
        if nums[i] == start:
            result.append(str(start))
        else:
            result.append(f"{start}->{nums[i]}")
        i += 1
    return result


# ================================================================== 599. Minimum Index Sum of Two Lists (Easy)
# https://leetcode.com/problems/minimum-index-sum-of-two-lists/
# Pattern: A dict from name to position
# Idea: Like joining two lists of favourites in the ORM. Store the positions of the first list in a
# dict, then look up each name of the second list once.

def find_restaurant(list1, list2):
    position = {name: i for i, name in enumerate(list1)}
    best = None
    result = []
    for j, name in enumerate(list2):
        if name in position:
            total = position[name] + j
            if best is None or total < best:
                best = total
                result = [name]
            elif total == best:
                result.append(name)
    return result


# ================================================================== 1441. Build an Array With Stack Operations (Medium)
# https://leetcode.com/problems/build-an-array-with-stack-operations/
# Pattern: Write down the operations, like makemigrations does
# Idea: makemigrations writes a list of operations that turn the old state into the new one. Here:
# read the numbers 1, 2, 3 ... in order, Push each one, and Pop it again when it is not in target.

def build_array(target, n):
    operations = []
    wanted = set(target)
    for number in range(1, target[-1] + 1):
        operations.append("Push")
        if number not in wanted:
            operations.append("Pop")
    return operations


# ================================================================== 1003. Check If Word Is Valid After Substitutions (Medium)
# https://leetcode.com/problems/check-if-word-is-valid-after-substitutions/
# Pattern: A stack, the same way template tags must close
# Idea: A Django template is only valid when every {% block %} has its {% endblock %} in the right
# order. Here "abc" plays that part: push letters and remove "abc" whenever it appears on top.

def is_valid(s):
    stack = []
    for ch in s:
        stack.append(ch)
        if stack[-3:] == ["a", "b", "c"]:
            del stack[-3:]
    return not stack


# ================================================================== 1487. Making File Names Unique (Medium)
# https://leetcode.com/problems/making-file-names-unique/
# Pattern: A dict with the next free number for each name
# Idea: When two users upload photo.jpg, Django storage saves the second one under a new name. Keep
# the next number to try for each name, so no name is checked again and again.

def get_folder_names(names):
    next_number = {}
    result = []
    for name in names:
        if name not in next_number:
            next_number[name] = 1
            result.append(name)
            continue
        k = next_number[name]
        while f"{name}({k})" in next_number:
            k += 1
        new_name = f"{name}({k})"
        next_number[name] = k + 1
        next_number[new_name] = 1
        result.append(new_name)
    return result


# ================================================================== 1048. Longest String Chain (Medium)
# https://leetcode.com/problems/longest-string-chain/
# Pattern: Sort by length, then dynamic programming on a dict
# Idea: Like a migration history where every migration adds one field. Sort the words by length and,
# for each word, try removing one letter to find the best chain that ends just before it.

def longest_str_chain(words):
    best = {}
    for word in sorted(words, key=len):
        best[word] = 1
        for i in range(len(word)):
            shorter = word[:i] + word[i + 1:]
            if shorter in best:
                best[word] = max(best[word], best[shorter] + 1)
    return max(best.values())


# ================================================================== 1912. Design Movie Rental System (Hard)
# https://leetcode.com/problems/design-movie-rental-system/
# Pattern: Sorted lists play the part of ORDER BY with an index
# Idea: This is a small ORM: one table of copies, a query "cheapest 5 shops for a movie" and a
# report "cheapest 5 rented copies". Keep sorted lists of (price, shop) and (price, shop, movie) so
# each query only reads the first 5.

import bisect


class MovieRentingSystem:
    def __init__(self, n, entries):
        self.price = {}
        self.unrented = {}            # movie -> sorted list of (price, shop)
        self.rented = []              # sorted list of (price, shop, movie)
        for shop, movie, price in entries:
            self.price[(shop, movie)] = price
            bisect.insort(self.unrented.setdefault(movie, []), (price, shop))

    def search(self, movie):
        return [shop for price, shop in self.unrented.get(movie, [])[:5]]

    def rent(self, shop, movie):
        price = self.price[(shop, movie)]
        self.unrented[movie].remove((price, shop))
        bisect.insort(self.rented, (price, shop, movie))

    def drop(self, shop, movie):
        price = self.price[(shop, movie)]
        self.rented.remove((price, shop, movie))
        bisect.insort(self.unrented[movie], (price, shop))

    def report(self):
        return [[shop, movie] for price, shop, movie in self.rented[:5]]


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 736. Parse Lisp Expression (Hard)
# https://leetcode.com/problems/parse-lisp-expression/
# Pattern: A recursive parser with a stack of scopes
# Idea: Like the context of a Django template: {% with %} adds names that live only inside its
# block, and inner names hide outer ones. Parse the tokens recursively and pass a new dict of names
# into every let.

def evaluate(expression):
    tokens = expression.replace("(", " ( ").replace(")", " ) ").split()
    pos = 0

    def lookup(name, scopes):
        for scope in reversed(scopes):
            if name in scope:
                return scope[name]
        return 0

    def value_of(token, scopes):
        if token[0] == "-" or token.isdigit():
            return int(token)
        return lookup(token, scopes)

    def parse(scopes):
        nonlocal pos
        if tokens[pos] != "(":
            token = tokens[pos]
            pos += 1
            return value_of(token, scopes)
        pos += 1                                   # skip "("
        word = tokens[pos]
        pos += 1
        if word == "add" or word == "mult":
            first = parse(scopes)
            second = parse(scopes)
            result = first + second if word == "add" else first * second
        else:                                      # let
            scopes = scopes + [{}]
            while True:
                if tokens[pos] == "(" or tokens[pos + 1] == ")":
                    result = parse(scopes)         # the last part is the value of the let
                    break
                name = tokens[pos]
                pos += 1
                scopes[-1][name] = parse(scopes)
        pos += 1                                   # skip ")"
        return result

    return parse([])


# ================================================================== 472. Concatenated Words (Hard)
# https://leetcode.com/problems/concatenated-words/
# Pattern: Word break with a set and memory
# Idea: Like checking that a URL slug such as "redbookshop" is made only of known words. For each
# word, test every cut point and remember which endings were already solved.

from functools import lru_cache


def find_all_concatenated_words_in_a_dict(words):
    known = set(words)
    result = []
    for word in words:
        if not word:
            continue

        @lru_cache(maxsize=None)
        def can_split(start):
            for end in range(start + 1, len(word) + 1):
                part = word[start:end]
                if part in known and part != word:
                    if end == len(word) or can_split(end):
                        return True
            return False

        if can_split(0):
            result.append(word)
    return result


if __name__ == "__main__":
    results = []
    results.append(check("257. Binary Tree Paths", [('binary_tree_paths(build_tree([1, 2, 3, None, 5]))', ['1->2->5', '1->3']), ('binary_tree_paths(build_tree([1]))', ['1'])]))
    results.append(check("228. Summary Ranges", [('summary_ranges([0, 1, 2, 4, 5, 7])', ['0->2', '4->5', '7']), ('summary_ranges([0, 2, 3, 4, 6, 8, 9])', ['0', '2->4', '6', '8->9']), ('summary_ranges([])', [])]))
    results.append(check("599. Minimum Index Sum of Two Lists", [('find_restaurant(["Shogun", "Tapioca Express", "Burger King", "KFC"], ["Piatti", "The Grill at Torrey Pines", "Hungry Hunter Steakhouse", "Shogun"])', ['Shogun']), ('find_restaurant(["Shogun", "Tapioca Express", "Burger King", "KFC"], ["KFC", "Shogun", "Burger King"])', ['Shogun']), ('find_restaurant(["happy", "sad", "good"], ["sad", "happy", "good"])', ['sad', 'happy'])]))
    results.append(check("1441. Build an Array With Stack Operations", [('build_array([1, 3], 3)', ['Push', 'Push', 'Pop', 'Push']), ('build_array([1, 2, 3], 3)', ['Push', 'Push', 'Push']), ('build_array([1, 2], 4)', ['Push', 'Push'])]))
    results.append(check("1003. Check If Word Is Valid After Substitutions", [('is_valid("aabcbc")', True), ('is_valid("abcabcababcc")', True), ('is_valid("abccba")', False)]))
    results.append(check("1487. Making File Names Unique", [('get_folder_names(["pes", "fifa", "gta", "pes(2019)"])', ['pes', 'fifa', 'gta', 'pes(2019)']), ('get_folder_names(["gta", "gta(1)", "gta", "avalon"])', ['gta', 'gta(1)', 'gta(2)', 'avalon']), ('get_folder_names(["onepiece", "onepiece(1)", "onepiece(2)", "onepiece(3)", "onepiece"])', ['onepiece', 'onepiece(1)', 'onepiece(2)', 'onepiece(3)', 'onepiece(4)']), ('get_folder_names(["kaido", "kaido(1)", "kaido", "kaido(1)"])', ['kaido', 'kaido(1)', 'kaido(2)', 'kaido(1)(1)'])]))
    results.append(check("1048. Longest String Chain", [('longest_str_chain(["a", "b", "ba", "bca", "bda", "bdca"])', 4), ('longest_str_chain(["xbc", "pcxbcf", "xb", "cxbc", "pcxbc"])', 5), ('longest_str_chain(["abcd", "dbqca"])', 1)]))
    results.append(check("1912. Design Movie Rental System", [('play(MovieRentingSystem, ["MovieRentingSystem", "search", "rent", "rent", "report", "drop", "search"], [[3, [[0, 1, 5], [0, 2, 6], [0, 3, 7], [1, 1, 4], [1, 2, 7], [2, 1, 5]]], [1], [0, 1], [1, 2], [], [1, 2], [2]])', [None, [1, 0, 2], None, None, [[0, 1], [1, 2]], None, [0, 1]])]))
    results.append(check("736. Parse Lisp Expression", [('evaluate("(let x 2 (mult x (let x 3 y 4 (add x y))))")', 14), ('evaluate("(let x 3 x 2 x)")', 2), ('evaluate("(let x 1 y 2 x (add x y) (add x y))")', 5), ('evaluate("(add 1 -2)")', -1)]))
    results.append(check("472. Concatenated Words", [('sorted(find_all_concatenated_words_in_a_dict(["cat", "cats", "catsdogcats", "dog", "dogcatsdog", "hippopotamuses", "rat", "ratcatdogcat"]))', ['catsdogcats', 'dogcatsdog', 'ratcatdogcat']), ('find_all_concatenated_words_in_a_dict(["cat", "dog", "catdog"])', ['catdog'])]))
    if all(results):
        print("Every solution passes its tests.")
