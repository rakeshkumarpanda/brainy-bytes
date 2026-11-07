# Advanced Python 1.4: exceptions in depth, copying and serialisation. Follows PCPP-32-101 block 1 (exceptions:
# chaining, __context__ and __cause__, the traceback attribute, the copy module: shallow and deep copies, object
# persistence with pickle and shelve), checked against the Python 3.14 tutorial chapter 8 (errors and exceptions,
# exception groups and notes), PEP 3134 (chaining), PEP 654 (exception groups and except*), PEP 678 (add_note), and
# the traceback, warnings, copy, pickle and shelve documentation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-errors-copy')
K = Kit()

K.code('hierarchy', r'''
class ShopError(Exception):
    """The parent of every error this shop raises."""


class OutOfStock(ShopError):
    def __init__(self, item, wanted, left):
        super().__init__(f"{item}: wanted {wanted}, only {left} left")
        self.item = item
        self.left = left


class PaymentFailed(ShopError):
    pass


def buy(item, wanted):
    stock = {"pen": 3, "book": 0}
    if stock[item] < wanted:
        raise OutOfStock(item, wanted, stock[item])
    return "bought"


for item, n in [("pen", 2), ("pen", 5), ("book", 1)]:
    try:
        print(buy(item, n))
    except OutOfStock as err:
        print("OutOfStock:", err, "| left:", err.left, "| args:", err.args)
    except ShopError:
        print("some other shop problem")
''')

K.code('chain', r'''
def load_age(text):
    try:
        return int(text)
    except ValueError as err:
        raise RuntimeError("bad age in the form") from err     # explicit chaining


try:
    load_age("abc")
except RuntimeError as err:
    print("caught:", err)
    print("cause:", repr(err.__cause__))
    print("suppress context?", err.__suppress_context__)


try:
    try:
        {}["missing"]
    except KeyError:
        1 / 0                                  # an error while handling an error
except ZeroDivisionError as err:
    print("context:", repr(err.__context__))   # implicit chaining
    print("cause:", err.__cause__)


try:
    try:
        int("x")
    except ValueError:
        raise LookupError("not found") from None   # hide the original
except LookupError as err:
    print("from None:", err.__cause__, err.__suppress_context__)
''')

K.code('tracebacks', r'''
import traceback


def level3():
    return 10 / 0


def level2():
    return level3()


def level1():
    return level2()


try:
    level1()
except ZeroDivisionError as err:
    for frame in traceback.extract_tb(err.__traceback__):
        print(frame.name, "line", frame.lineno, ":", frame.line)
    print(traceback.format_exception_only(err)[-1].strip())
    print(type(err.__traceback__).__name__)
''')

K.code('notes', r'''
def parse_row(number, row):
    try:
        name, age = row.split(",")
        return name, int(age)
    except ValueError as err:
        err.add_note(f"while reading row {number}: {row!r}")   # Python 3.11+
        raise


try:
    for number, row in enumerate(["Asha,30", "Ravi,thirty"], start=1):
        print(parse_row(number, row))
except ValueError as err:
    print("ValueError:", err)
    print("notes:", err.__notes__)
''')

K.code('groups', r'''
def check(user):
    problems = []
    if not user.get("name"):
        problems.append(ValueError("name is empty"))
    if user.get("age", 0) < 0:
        problems.append(ValueError("age is negative"))
    if "@" not in user.get("email", ""):
        problems.append(TypeError("email has no @"))
    if problems:
        raise ExceptionGroup("the form has errors", problems)   # report them ALL at once
    return "ok"


try:
    check({"name": "", "age": -1, "email": "asha.example.com"})
except* ValueError as group:                   # except* handles part of a group
    for err in group.exceptions:
        print("value problem:", err)
except* TypeError as group:
    for err in group.exceptions:
        print("type problem:", err)

print(check({"name": "Asha", "age": 30, "email": "a@b.in"}))
''')

K.code('warn', r'''
import warnings


def old_area(w, h):
    warnings.warn("old_area is deprecated, use area", DeprecationWarning, stacklevel=2)
    return w * h


with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")            # show every warning, even repeated ones
    print(old_area(3, 4))
    print(len(caught), caught[0].category.__name__, str(caught[0].message))

warnings.simplefilter("error")                 # turn warnings into exceptions
try:
    old_area(1, 1)
except DeprecationWarning as err:
    print("now an error:", err)
''')

K.code('copying', r'''
import copy

a = [[1, 2], [3, 4]]
b = a                                          # same object
c = a.copy()                                   # shallow: new outer, shared inner
d = copy.deepcopy(a)                           # deep: everything new

c[0].append(9)
c.append([5])
print(a)
print(c)
print(d)
print(b is a, c is a, c[0] is a[0], d[0] is a[0])

prices = {"pen": [10, 12], "ink": [5]}
shallow = dict(prices)                         # also shallow: dict(), list(), [:], copy.copy
shallow["pen"].append(15)
print(prices["pen"])

loop = [1, 2]
loop.append(loop)                              # a list that contains itself
twin = copy.deepcopy(loop)                     # deepcopy remembers what it already copied
print(twin[2] is twin, twin[2] is loop)
''')

K.code('customcopy', r'''
import copy


class Document:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages
        self.cache = {"rendered": True}

    def __copy__(self):                        # used by copy.copy
        new = Document(self.title, self.pages)
        new.cache = {}                         # never share a cache
        return new

    def __deepcopy__(self, memo):              # used by copy.deepcopy
        new = Document(self.title, copy.deepcopy(self.pages, memo))
        new.cache = {}
        return new


doc = Document("Notes", ["p1", "p2"])
s = copy.copy(doc)
d = copy.deepcopy(doc)
print(s.pages is doc.pages, d.pages is doc.pages, s.cache, d.cache)
''')

K.code('pickling', r'''
import pickle, os, tempfile
from dataclasses import dataclass


@dataclass
class Player:
    name: str
    level: int
    items: list


hero = Player("Asha", 7, ["sword", "map"])
data = pickle.dumps(hero)                      # object -> bytes
print(type(data).__name__, len(data), data[:2])
back = pickle.loads(data)                      # bytes -> a NEW equal object
print(back, back == hero, back is hero)

path = os.path.join(tempfile.mkdtemp(), "save.pkl")
with open(path, "wb") as f:                    # binary mode
    pickle.dump({"hero": hero, "score": 980}, f)
with open(path, "rb") as f:
    game = pickle.load(f)
print(game["score"], game["hero"].items)

try:
    pickle.dumps(lambda x: x)                  # lambdas cannot be pickled
except (pickle.PicklingError, AttributeError) as err:
    print(type(err).__name__)
print(pickle.HIGHEST_PROTOCOL, pickle.DEFAULT_PROTOCOL)
''')

K.code('shelf', r'''
import shelve, os, tempfile

path = os.path.join(tempfile.mkdtemp(), "contacts")

with shelve.open(path) as db:                  # a dict that lives on disk
    db["asha"] = {"phone": "98100", "tags": ["family"]}
    db["ravi"] = {"phone": "98200", "tags": []}

with shelve.open(path) as db:                  # open again later: still there
    print(sorted(db.keys()))
    print(db["asha"]["phone"])
    entry = db["ravi"]
    entry["tags"].append("work")               # change a copy...
    db["ravi"] = entry                         # ...and store it back
    print(db["ravi"]["tags"], "ravi" in db, len(db))
''')

K.lesson('idea', 'Exceptions, copies and saved objects', f'''
{src('Python 3.14 tutorial chapter 8, PEP 3134, PEP 654, PEP 678, and the traceback, warnings, copy, pickle and shelve documentation, plus PCPP-32-101 block 1.')}
{wwh('This chapter goes deeper into three things every real program needs: <b>exceptions</b> that carry their full story (their own types, causes, notes and groups), <b>copies</b> of objects that do or do not share their insides, and <b>serialisation</b>, turning objects into bytes so they can be saved and loaded later with pickle and shelve.',
     'In a big program a bare "ValueError" says little. You need to know what went wrong, where, and what caused it. Copying is a classic source of bugs: changing a "copy" that secretly shares data with the original. And objects vanish when the program ends unless you save them.',
     'Custom exception classes form a family you can catch at any level. raise ... from ... links a new error to its cause. add_note and ExceptionGroup add context and report many errors at once. copy.copy and copy.deepcopy decide how deep a copy goes. pickle.dumps turns almost any object into bytes and pickle.loads rebuilds it.')}
{run('hierarchy')}
{note('Give your package one base exception (ShopError) and children for each problem. Callers can then catch one specific error, or everything from your package with one except.', 'tip')}
''', kw=['custom exception', 'exception hierarchy', 'serialisation', 'copy', 'pickle', 'err.args'])

K.lesson('chain', 'Chaining: __cause__ and __context__', f'''
{run('chain')}
{table(['You write', 'Attribute set on the new error', 'Traceback says'], [
    ['raise New() from old', '__cause__ = old', '"The above exception was the direct cause of the following exception"'],
    ['raise New() inside an except block', '__context__ = the error being handled', '"During handling of the above exception, another exception occurred"'],
    ['raise New() from None', '__cause__ = None, __suppress_context__ = True', 'Only the new error']])}
{note('Use raise ... from err when you turn a low level error into a meaningful one, so the original is never lost. Use from None only when the original adds nothing for the reader.', 'exam')}
''', kw=['exception chaining', '__cause__', '__context__', 'raise from', 'from None', '__suppress_context__', 'PEP 3134'])

K.lesson('trace', 'Tracebacks, notes and exception groups', f'''
{run('tracebacks')}
{run('notes')}
{run('groups')}
{versus('Reporting problems', ['', 'raise one exception', 'add_note', 'ExceptionGroup and except*'], [
    ['Since', 'Always', 'Python 3.11', 'Python 3.11'],
    ['Reports', 'The first problem', 'One problem with extra context', 'Many problems at once'],
    ['Caught with', 'except', 'except (notes in err.__notes__)', 'except*, each matching part separately'],
    ['Typical use', 'Most errors', 'Adding the row, file or user while an error passes up', 'Form checks, many parallel tasks (asyncio TaskGroup)']],
    'raise a single exception normally, add notes as it travels up, and group errors when several independent things fail together.')}
''', kw=['traceback', 'extract_tb', '__traceback__', 'add_note', '__notes__', 'ExceptionGroup', 'except*', 'PEP 654', 'PEP 678'])

K.lesson('warn', 'Warnings and assertions', f'''
{run('warn')}
{versus('Signals that something is wrong', ['', 'exception', 'warning', 'assert'], [
    ['Stops the program', 'Yes, unless caught', 'No, by default it prints once', 'Yes (AssertionError)'],
    ['For', 'Errors the caller must handle', 'Old or risky use that still works', 'Checks of your own logic while developing'],
    ['Turned off by', 'Never', 'warnings filters', 'python -O removes every assert'],
    ['Example', 'raise ValueError', 'warnings.warn(..., DeprecationWarning)', 'assert total &gt;= 0']],
    'never use assert to check user input, because -O deletes it.')}
''', kw=['warnings', 'DeprecationWarning', 'catch_warnings', 'simplefilter', 'assert', 'python -O'])

K.lesson('copying', 'Shallow and deep copies', f'''
{viz('pycopy')}
{run('copying')}
{run('customcopy')}
{versus('Three ways to "copy"', ['', 'b = a', 'shallow copy', 'deep copy'], [
    ['Written as', 'b = a', 'a.copy(), a[:], list(a), dict(a), copy.copy(a)', 'copy.deepcopy(a)'],
    ['New outer object', 'No', 'Yes', 'Yes'],
    ['New inner objects', 'No', 'No, shared', 'Yes, all the way down'],
    ['Cost', 'Free', 'O(length)', 'O(every object inside)'],
    ['Safe to change inner items', 'No', 'No', 'Yes']],
    'a shallow copy is enough when the items are immutable (numbers, strings, tuples of those). Use deepcopy for nested mutable data.')}
''', kw=['shallow copy', 'deep copy', 'copy.copy', 'copy.deepcopy', 'memo', '__copy__', '__deepcopy__', 'aliasing'])

K.lesson('pickling', 'pickle and shelve: save objects', f'''
{run('pickling')}
{run('shelf')}
{note('Never unpickle data from a source you do not trust. pickle.loads can run any code the data asks for, so a crafted file can take over your computer. For data from users or the internet use JSON.', 'warn')}
{versus('Saving data', ['', 'json', 'pickle', 'shelve'], [
    ['Format', 'Text, readable by any language', 'Python only bytes', 'A pickle per key in a small database'],
    ['Saves', 'dict, list, str, numbers, bool, None', 'Almost any Python object', 'Almost any object, by string key'],
    ['Safe with untrusted data', 'Yes', 'NO', 'NO'],
    ['Good for', 'APIs, config, data exchange', 'Caches, saving program state, sending objects between Python processes', 'A simple persistent dict']],
    'use JSON to talk to the world, pickle for trusted Python to Python data, and shelve when you want a dict that survives restarts.')}
{note('A shelf returns copies. db["ravi"]["tags"].append("work") changes a copy that is thrown away. Read the value, change it and assign it back (or open with writeback=True).', 'exam')}
''', kw=['pickle', 'dumps', 'loads', 'dump', 'load', 'protocol', 'shelve', 'security', 'json vs pickle', 'writeback'])

K.lesson('maths', 'The maths: retries, copies and sizes', f'''
{fxs(fx('Chance that k independent attempts all fail', 'P(all fail) = p<sup>k</sup>, P(success) = 1 &minus; p<sup>k</sup>', 'A call fails 20 % of the time. With 3 attempts: 1 &minus; 0.2<sup>3</sup> = 99.2 % success.', key=True),
     fx('Objects created by copies of an n by m nested list', 'shallow: 1 list. deep: 1 + n lists', 'For [[1, 2], [3, 4]]: shallow makes 1 new list, deep makes 3. The ints are immutable and shared either way.', key=True),
     fx('Attempts needed for a target', 'k &ge; log(1 &minus; target) / log(p)', 'p = 0.2, target 99.99 %: k &ge; log(0.0001) / log(0.2) &asymp; 5.7, so 6 attempts.'),
     fx('Expected attempts until success', 'E = 1 / (1 &minus; p)', 'p = 0.2: 1.25 attempts on average.'))}
{steps('Worked example: success chance with 3 attempts at p = 0.2', [
    'All three fail: 0.2 &times; 0.2 &times; 0.2 = 0.008.',
    'So at least one succeeds with 1 &minus; 0.008.',
    eq('0.992, which is 99.2 %')])}
''', kw=['probability of failure', 'retries', 'geometric distribution', 'copy cost', 'expected attempts'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Write your own exception class, and know that b = a does not copy while a.copy() and copy.deepcopy(a) do.</p>',
    '<p>Build an exception hierarchy, chain with raise from, read tracebacks, choose shallow or deep copies, and save objects with pickle and shelve.</p>',
    '<p>Use add_note, ExceptionGroup and except*, warnings filters, __copy__ and __deepcopy__, and know the pickle security risk and when JSON is the right tool.</p>',
    '<p>pickle stores a program for a small stack machine: classes are saved by import path and rebuilt with __reduce__, __getstate__ and __setstate__, which is both why pickle can rebuild almost anything and why loading it can run arbitrary code. Protocol 5 (PEP 574) adds out of band buffers for large data.</p>')}
{grow('Raise and catch your own exceptions, copy lists safely.',
      'Chain exceptions, choose the right copy, pickle and shelve objects.',
      'Use exception groups and notes, customise copying and pickling, explain the pickle VM.')}
''', kw=['beginner', 'expert', '__reduce__', '__getstate__', 'PEP 574', 'pickle protocol'])

TREE = '''

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
'''

lc(138, 'Copy List with Random Pointer', 'copy-list-with-random-pointer', 'm', 'Deep copy with a memo dict', 'Map every old node to its new copy in a dict, exactly like copy.deepcopy does with its memo. Then set next and random from the map.', r'''
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
''', [('(lambda h: (dump_random_list(copy_random_list(h)), copy_random_list(h) is not h))(build_random_list([[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]))', [[[7, None], [13, 0], [11, 4], [10, 2], [1, 0]], True])])
lc(133, 'Clone Graph', 'clone-graph', 'm', 'DFS with a memo, like deepcopy', 'Copy a node, remember the copy, then copy its neighbours. The memo stops the copy from looping forever around cycles.', r'''
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
''', [('(lambda g: (dump_graph(clone_graph(g)), clone_graph(g) is not g))(build_graph([[2, 4], [1, 3], [2, 4], [1, 3]]))', [[[2, 4], [1, 3], [2, 4], [1, 3]], True])])
lc(297, 'Serialize and Deserialize Binary Tree', 'serialize-and-deserialize-binary-tree', 'h', 'Preorder with markers', 'Write the tree in preorder with # for an empty child. Read it back with an iterator, building the left subtree before the right. This is pickling by hand.', r'''
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
''' + TREE, [('tree_to_list(Codec().deserialize(Codec().serialize(build_tree([1, 2, 3, None, None, 4, 5]))))', [1, 2, 3, None, None, 4, 5]), ('Codec().serialize(build_tree([1, 2]))', '1,2,#,#,#')])
lc(449, 'Serialize and Deserialize BST', 'serialize-and-deserialize-bst', 'm', 'Preorder values and bounds', 'A BST is fixed by its preorder alone. Rebuild it by giving each value a range (low, high) it must fit in.', r'''
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
''' + TREE, [('tree_to_list(BSTCodec().deserialize(BSTCodec().serialize(build_tree([2, 1, 3]))))', [2, 1, 3]), ('BSTCodec().serialize(build_tree([5, 3, 8, 1, 4]))', '5 3 1 4 8')])
lc(535, 'Encode and Decode TinyURL', 'encode-and-decode-tinyurl', 'm', 'A counter and two dicts', 'Give each new long URL the next number as its short code, and remember both directions.', r'''
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
''', [('(lambda c: c.decode(c.encode("https://leetcode.com/problems/design-tinyurl")))(TinyCodec())', 'https://leetcode.com/problems/design-tinyurl'), ('(lambda c: (c.encode("a"), c.encode("b"), c.encode("a")))(TinyCodec())', ['http://tinyurl.com/1', 'http://tinyurl.com/2', 'http://tinyurl.com/1'])])
lc(606, 'Construct String from Binary Tree', 'construct-string-from-binary-tree', 'e', 'Preorder with brackets', 'Write the value, then the left child in brackets, then the right child in brackets. Keep () for a missing left child only when a right child exists.', r'''
def tree2str(root):
    if root is None:
        return ""
    text = str(root.val)
    if root.left or root.right:
        text += "(" + tree2str(root.left) + ")"
    if root.right:
        text += "(" + tree2str(root.right) + ")"
    return text
''' + TREE, [('tree2str(build_tree([1, 2, 3, 4]))', '1(2(4))(3)'), ('tree2str(build_tree([1, 2, 3, None, 4]))', '1(2()(4))(3)')])
lc(331, 'Verify Preorder Serialization of a Binary Tree', 'verify-preorder-serialization-of-a-binary-tree', 'm', 'Count open slots', 'Start with one slot. Every token fills a slot, and a number opens two more. The string is valid if slots never go below zero and end at zero.', r'''
def is_valid_serialization(preorder):
    slots = 1
    for token in preorder.split(","):
        if slots == 0:
            return False
        slots -= 1
        if token != "#":
            slots += 2
    return slots == 0
''', [('is_valid_serialization("9,3,4,#,#,1,#,#,2,#,6,#,#")', True), ('is_valid_serialization("1,#")', False), ('is_valid_serialization("9,#,#,1")', False)])
lc(652, 'Find Duplicate Subtrees', 'find-duplicate-subtrees', 'm', 'Serialise every subtree', 'Turn each subtree into a string (its own little pickle). Count the strings and report a root the second time its string appears.', r'''
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
''' + TREE, [('sorted(tree_to_list(n) for n in find_duplicate_subtrees(build_tree([1, 2, 3, 4, None, 2, 4, None, None, 4])))', [[2, 4], [4]])])
lc(394, 'Decode String', 'decode-string', 'm', 'A stack of unfinished parts', 'Read the text once. A number before [ says how many times to repeat. On [ save the text so far and the count on a stack. On ] repeat the inner text and glue it to the saved text. This is how a loader rebuilds nested data from a flat string.', r'''
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
''', [('decode_string("3[a]2[bc]")', 'aaabcbc'), ('decode_string("3[a2[c]]")', 'accaccacc'), ('decode_string("2[abc]3[cd]ef")', 'abcabccdcdcdef')])
lc(1106, 'Parsing A Boolean Expression', 'parsing-a-boolean-expression', 'h', 'A stack of values and operators', 'Push every character except commas. On ) pop the values back to the (, take the operator in front of it, and push the single result. Nested expressions are solved from the inside out.', r'''
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
''', [('parse_bool_expr("&(|(f))")', False), ('parse_bool_expr("|(f,f,f,t)")', True), ('parse_bool_expr("!(&(f,t))")', True), ('parse_bool_expr("t")', True)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Two problems are deep copies done by hand with a memo dict, which is exactly how copy.deepcopy avoids loops. Five are serialisation: turning trees and URLs into strings and back, like pickle. Two rebuild nested structure from a flat string with a stack, which is what any loader does.</p>'), kw=['LeetCode', 'deep copy', 'clone graph', 'serialize tree', 'parsing', 'decode string'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Make one base exception per package and a child per problem. Pass a clear message to super().__init__ and store useful fields.',
    'raise New() from err sets __cause__. Raising inside except sets __context__. from None hides the original.',
    'err.__traceback__ and the traceback module show where an error happened. add_note adds context. ExceptionGroup with except* reports many errors.',
    'Warnings flag old or risky use without stopping. assert checks your own logic and disappears with python -O.',
    'b = a shares everything, a shallow copy shares the inner objects, copy.deepcopy shares nothing and handles loops with a memo.',
    'pickle.dumps and loads turn objects into bytes and back. Never unpickle untrusted data. shelve is a dict on disk that returns copies.'],
    '1.5 finishes Step 1 with metaprogramming: type(), metaclasses, __init_subclass__ and class decorators.')}
{files('Three tasks: an exception hierarchy with chaining, a safe deep copy of a nested config, and saving and loading a high score table with pickle.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which class should your own exceptions usually inherit from?', ['BaseException', 'Exception', 'object', 'Error'], 1, 'Not BaseException.', 'BaseException also covers KeyboardInterrupt and SystemExit, which normal code should not catch.')
K.quiz('e', 'What does b = a do for a list a?', ['Copies the list', 'Makes b a second name for the same list', 'Deep copies it', 'Freezes it'], 1, 'No copy.', 'Assignment only binds a name.')
K.quiz('e', 'Which module saves almost any Python object as bytes?', ['json', 'pickle', 'csv', 'os'], 1, 'Python only format.', 'pickle.dumps returns bytes.')
K.quiz('m', 'What does raise RuntimeError("x") from err set?', ['__context__ only', '__cause__ = err', '__notes__', 'Nothing'], 1, 'Explicit chaining.', 'from err stores err as the direct cause.')
K.quiz('m', 'a = [[1], [2]] and c = a.copy(). Then c[0].append(9). What is a?', ['[[1], [2]]', '[[1, 9], [2]]', '[[1], [2], 9]', 'Error'], 1, 'Shallow.', 'The inner lists are shared by a and c.')
K.quiz('m', 'Which statement handles part of an ExceptionGroup?', ['except', 'except*', 'catch', 'finally'], 1, 'Star.', 'except* matches the exceptions of one type inside a group.')
K.quiz('m', 'Why is pickle.loads on data from the internet dangerous?', ['It is slow', 'It can run arbitrary code chosen by whoever made the data', 'It loses data', 'It only works on Windows'], 1, 'Security.', 'Unpickling can call any importable function.')
K.quiz('m', 'What happens to assert statements when Python runs with -O?', ['They become warnings', 'They are removed', 'They raise SystemExit', 'Nothing'], 1, 'Optimise.', 'Optimised mode strips asserts, so never use them for input checks.')
K.quiz('h', 'An error is raised inside an except block without from. Where does the original go?', ['It is lost', '__context__ of the new error', '__cause__ of the new error', '__notes__'], 1, 'Implicit chaining.', 'Python links it automatically as the context.')
K.quiz('h', 'db = shelve.open(p). db["k"] holds a list. db["k"].append(1), then close and reopen. Is 1 in db["k"]?', ['Yes', 'No, the append changed a temporary copy', 'Error', 'Only with pickle protocol 5'], 1, 'Shelves return copies.', 'Assign the changed value back, or open with writeback=True.')
K.quiz('h', 'loop = [1], then loop.append(loop), then t = copy.deepcopy(loop). What is t[1] is t?', ['False', 'True', 'RecursionError', 'TypeError'], 1, 'The memo.', 'deepcopy remembers copied objects, so the copy refers to itself just like the original.')
K.quiz('x', 'In the style of a CMU 15-213 question: a call fails independently with probability 0.1. What is the smallest number of attempts that gives at least 99.9 % success?', ['2', '3', '4', '10'], 1, '1 &minus; 0.1<sup>k</sup> &ge; 0.999.', '0.1<sup>3</sup> = 0.001, so 3 attempts give exactly 99.9 %.')
K.quiz('x', 'In the style of a Stanford CS 155 (security) exam: an API accepts uploaded game saves and calls pickle.loads on them. What is the right fix?', ['Use a newer pickle protocol', 'Store saves as JSON (or sign them with a secret key) and never unpickle user data', 'Catch all exceptions around loads', 'Compress the data first'], 1, 'Trust boundary.', 'Exceptions and protocols do not stop code execution during loading. Only not unpickling untrusted input does.')

K.calc('e', 'A call fails with probability 0.5. What is the chance in percent that 2 attempts both fail?', '25', '0.5 &times; 0.5.', ['Each attempt fails with 0.5.', 'Independent attempts multiply.', eq('0.25 = 25 %')], check=25)
K.calc('e', 'How many new list objects does copy.copy([[1, 2], [3, 4]]) create?', '1', 'Only the outer list.', ['A shallow copy makes a new outer list.', 'The inner lists are shared.', eq('1')], check=1)
K.calc('e', 'How many new list objects does copy.deepcopy([[1, 2], [3, 4]]) create?', '3', 'Outer plus each inner.', ['1 outer list.', '2 inner lists.', eq('3')], check=3)
K.calc('m', 'p = 0.2 and 3 attempts. Success chance in percent?', '99.2', '1 &minus; p<sup>3</sup>.', ['0.2<sup>3</sup> = 0.008.', '1 &minus; 0.008 = 0.992.', eq('99.2 %')], check=round((1 - 0.2 ** 3) * 100, 1))
K.calc('m', 'Expected number of attempts until success when each attempt fails with p = 0.75.', '4', '1 / (1 &minus; p).', ['1 &minus; 0.75 = 0.25.', '1 / 0.25.', eq('4')], check=1 / (1 - 0.75))
K.calc('m', 'A 100 by 50 nested list (100 inner lists of 50 ints). How many list objects does deepcopy create?', '101', '1 + n.', ['1 outer list.', '100 inner lists. The ints are shared.', eq('101')], check=101)
K.calc('m', 'is_valid_serialization("9,#,#"): what is the slot count at the end?', '0', 'Start at 1.', ['9 uses 1 and adds 2: 2.', 'Each # uses 1: 1, then 0.', eq('0, so it is valid')], check=0)
K.calc('h', 'p = 0.2. Smallest k with 1 &minus; 0.2<sup>k</sup> &ge; 0.9999?', '6', 'k &ge; log(0.0001) / log(0.2).', ['log(0.0001) / log(0.2) &asymp; 5.72.', 'Round up.', eq('6')], check=6)
K.calc('h', 'How long is decode_string("3[a2[c]]")?', '9', 'Inside out.', ['2[c] is cc, so a2[c] is acc (3 characters).', '3[acc] repeats it 3 times.', eq('3 &times; 3 = 9')], check=len('acc' * 3))
K.calc('x', 'In the style of an MIT 6.042 problem: three independent services each fail with probability 0.1, and a request needs all three. What is the chance in percent that a request succeeds, to 1 decimal place?', '72.9', 'All must work.', ['Each works with 0.9.', '0.9<sup>3</sup> = 0.729.', eq('72.9 %')], check=round(0.9 ** 3 * 100, 1))

K.assign('errors', 'm', 'An exception hierarchy with chaining',
         '<p>Write <code>ConfigError(Exception)</code> and a child <code>MissingKey(ConfigError)</code>. Then write <code>get_port(config)</code> that returns int(config["port"]). If the key is missing, raise MissingKey("port") <b>from</b> the KeyError. If the value is not a number, raise ConfigError("port must be a number") from the ValueError. what() is a test helper that returns the error type, its message and the type of its __cause__.</p>',
         '''
class ConfigError(Exception):
    pass


def get_port(config):
    # your code here
    pass


def what(func, *args):
    try:
        return func(*args)
    except Exception as err:
        return [type(err).__name__, str(err), type(err.__cause__).__name__]
''', [('get_port({"port": "8080"})', 8080), ('what(get_port, {})', ['MissingKey', 'port', 'KeyError']), ('what(get_port, {"port": "abc"})', ['ConfigError', 'port must be a number', 'ValueError']), ('issubclass(MissingKey, ConfigError)', True)],
         '''
class ConfigError(Exception):
    pass


class MissingKey(ConfigError):
    pass


def get_port(config):
    try:
        text = config["port"]
    except KeyError as err:
        raise MissingKey("port") from err
    try:
        return int(text)
    except ValueError as err:
        raise ConfigError("port must be a number") from err


def what(func, *args):
    try:
        return func(*args)
    except Exception as err:
        return [type(err).__name__, str(err), type(err.__cause__).__name__]
''', 'Two small try blocks: one around config["port"], one around int(text). In each except, raise the new error with from err.', '<p>Callers can catch ConfigError for every config problem, and the original KeyError or ValueError is kept as the cause for debugging.</p>')
K.assign('copyconf', 'e', 'Safe copies of a nested config',
         '<p>Write <code>with_override(config, section, key, value)</code> that returns a NEW config dict with config[section][key] set to value, without changing the original in any way.</p>',
         '''
import copy


def with_override(config, section, key, value):
    # your code here
    pass
''', [('(lambda c: (with_override(c, "db", "port", 5433)["db"]["port"], c["db"]["port"]))({"db": {"port": 5432}, "debug": False})', [5433, 5432]), ('(lambda c: with_override(c, "db", "host", "x") is c)({"db": {}})', False)],
         '''
import copy


def with_override(config, section, key, value):
    new = copy.deepcopy(config)
    new[section][key] = value
    return new
''', 'A shallow copy would share config["db"], so use copy.deepcopy and change the copy.', '<p>With config.copy() the first test fails: the original port changes too, because the inner dict is shared.</p>')
K.assign('scores', 'm', 'Save a high score table with pickle',
         '<p>Write <code>save_scores(path, scores)</code> that pickles a dict of name to score into the file, and <code>top_scores(path, n)</code> that loads it and returns a list of the n best (name, score) pairs, highest first (ties by name A to Z). If the file does not exist, top_scores returns []. new_path() is a helper.</p>',
         '''
import pickle


def save_scores(path, scores):
    # your code here
    pass


def top_scores(path, n):
    # your code here
    pass


def new_path():
    import os, tempfile
    return os.path.join(tempfile.mkdtemp(), "scores.pkl")
''', [('(lambda p: (save_scores(p, {"asha": 90, "ravi": 75, "meera": 90, "ali": 60}), top_scores(p, 3))[1])(new_path())', [['asha', 90], ['meera', 90], ['ravi', 75]]), ('top_scores(new_path(), 5)', [])],
         '''
import pickle


def save_scores(path, scores):
    with open(path, "wb") as f:
        pickle.dump(scores, f)


def top_scores(path, n):
    try:
        with open(path, "rb") as f:
            scores = pickle.load(f)
    except FileNotFoundError:
        return []
    pairs = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return pairs[:n]


def new_path():
    import os, tempfile
    return os.path.join(tempfile.mkdtemp(), "scores.pkl")
''', 'Open with "wb" to dump and "rb" to load. Sort the items with key=lambda item: (-item[1], item[0]).', '<p>The key (-score, name) sorts by score from high to low and breaks ties alphabetically, in one sort.</p>')

K.must('Exception design', 'class AppError(Exception) plus children. super().__init__(message). Catch the child for one problem, the base for all.')
K.must('Chaining', 'raise New() from err sets __cause__. Raising inside except sets __context__. from None hides it. err.__traceback__ has the frames.')
K.must('3.11 tools', 'err.add_note(text) and err.__notes__. ExceptionGroup(msg, [errors]) caught with except* Type.')
K.must('Copies', 'b = a no copy. a.copy(), a[:], list(a), dict(a), copy.copy: shallow. copy.deepcopy: everything, loops handled by memo.')
K.must('Saving objects', 'pickle.dumps/loads (bytes), dump/load (files in "wb"/"rb"). Never unpickle untrusted data. shelve: dict on disk, returns copies.')

T = K.topic(
    slug='py-errors-copy', topic='py-errors-copy', step=(1, 'Advanced object oriented programming', 'py-a1', 'Make classes behave like built in types, then master decorators, class design, exceptions, copying, serialisation and metaclasses.', 'Advanced'),
    title='Exceptions in depth, copying and serialisation', short='Exceptions, copy, pickle', badge='1.4', minutes=80,
    lead='Give errors their full story and keep data safe. Learn exception hierarchies, chaining with raise from, __cause__ and __context__, tracebacks, add_note, exception groups with except*, warnings, shallow and deep copies, custom copying, and saving objects with pickle and shelve.',
    desc='custom exception hierarchies, err.args, raise from, __cause__, __context__, from None, the traceback module and __traceback__, add_note and __notes__, ExceptionGroup and except*, warnings and assert, assignment versus shallow and deep copies, copy.copy and copy.deepcopy with memo, __copy__ and __deepcopy__, pickle dumps, loads, dump and load, protocols, pickle security, shelve, json versus pickle, retry probability.',
    summary='exception hierarchies, chaining, tracebacks, notes, exception groups, warnings, shallow and deep copy, pickle and shelve.',
    keywords=['exception chaining', '__cause__', '__context__', 'traceback', 'add_note', 'ExceptionGroup', 'except*', 'warnings', 'copy', 'deepcopy', 'pickle', 'shelve', 'PCPP'],
    recap='<p>Let errors keep their cause, copy as deep as your data needs, and only unpickle data you trust.</p>',
    added='2026-11-07', leet=leet_items())
