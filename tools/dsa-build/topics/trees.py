# Trees: vocabulary and recursion, traversals, binary search trees, deletion,
# balance, heaps and tries.

CODES = {}


def C(key, py, js, java):
    CODES[key] = {'py': py, 'js': js, 'java': java}


PY_NODE = r'''
class Node:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
'''

PY_FROM = r'''

def from_list(vals):
    # build a tree from level order values, None marks a missing child
    root = Node(vals[0])
    queue = deque([root])
    i = 1
    while i < len(vals):
        node = queue.popleft()
        if vals[i] is not None:
            node.left = Node(vals[i])
            queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = Node(vals[i])
            queue.append(node.right)
        i += 1
    return root
'''

JS_NODE = r'''
class Node {
  constructor(val, left = null, right = null) {
    this.val = val;
    this.left = left;
    this.right = right;
  }
}
'''

JS_FROM = r'''
// build a tree from level order values, null marks a missing child
function fromList(vals) {
  const root = new Node(vals[0]);
  const queue = [root];
  let head = 0, i = 1;
  while (i < vals.length) {
    const node = queue[head++];
    if (vals[i] !== null) { node.left = new Node(vals[i]); queue.push(node.left); }
    i++;
    if (i < vals.length && vals[i] !== null) { node.right = new Node(vals[i]); queue.push(node.right); }
    i++;
  }
  return root;
}
'''

JAVA_NODE = r'''
    static class Node {
        int val;
        Node left, right;
        Node(int val) { this.val = val; }
        Node(int val, Node left, Node right) { this.val = val; this.left = left; this.right = right; }
    }
'''

JAVA_FROM = r'''
    // build a tree from level order values, null marks a missing child
    static Node fromList(Integer... vals) {
        Node root = new Node(vals[0]);
        ArrayDeque<Node> queue = new ArrayDeque<>();
        queue.add(root);
        int i = 1;
        while (i < vals.length) {
            Node node = queue.poll();
            if (vals[i] != null) { node.left = new Node(vals[i]); queue.add(node.left); }
            i++;
            if (i < vals.length && vals[i] != null) { node.right = new Node(vals[i]); queue.add(node.right); }
            i++;
        }
        return root;
    }
'''

JAVA_JOIN = r'''
    static String join(List<Integer> xs) {
        StringBuilder sb = new StringBuilder();
        for (int x : xs) {
            if (sb.length() > 0) sb.append(" ");
            sb.append(x);
        }
        return sb.toString();
    }
'''


def jv(name, body, imports='', helpers=(JAVA_NODE,)):
    return f'{imports}public class {name} {{{"".join(helpers)}\n{body}}}\n'


# ---------------------------------------------------------------- lesson programs
C('tree_basics', py=PY_NODE + r'''

def size(node):
    if node is None:
        return 0
    return 1 + size(node.left) + size(node.right)


def height(node):
    if node is None:
        return 0                      # an empty tree has no levels
    return 1 + max(height(node.left), height(node.right))


def leaves(node, out):
    if node is None:
        return
    if node.left is None and node.right is None:
        out.append(node.val)          # no children, so this is a leaf
    leaves(node.left, out)
    leaves(node.right, out)


#        1
#      /   \
#     2     3
#    / \     \
#   4   5     6
root = Node(1, Node(2, Node(4), Node(5)), Node(3, None, Node(6)))
print("size", size(root))
print("height", height(root))
found = []
leaves(root, found)
print("leaves", " ".join(str(v) for v in found))
''', js=JS_NODE + r'''
function size(node) {
  if (node === null) return 0;
  return 1 + size(node.left) + size(node.right);
}

function height(node) {
  if (node === null) return 0;        // an empty tree has no levels
  return 1 + Math.max(height(node.left), height(node.right));
}

function leaves(node, out) {
  if (node === null) return;
  if (node.left === null && node.right === null) out.push(node.val);  // no children, so this is a leaf
  leaves(node.left, out);
  leaves(node.right, out);
}

//        1
//      /   \
//     2     3
//    / \     \
//   4   5     6
const root = new Node(1, new Node(2, new Node(4), new Node(5)), new Node(3, null, new Node(6)));
console.log("size", size(root));
console.log("height", height(root));
const found = [];
leaves(root, found);
console.log("leaves", found.join(" "));
''', java=jv('TreeBasics', r'''
    static int size(Node node) {
        if (node == null) return 0;
        return 1 + size(node.left) + size(node.right);
    }

    static int height(Node node) {
        if (node == null) return 0;     // an empty tree has no levels
        return 1 + Math.max(height(node.left), height(node.right));
    }

    static void leaves(Node node, List<Integer> out) {
        if (node == null) return;
        if (node.left == null && node.right == null) out.add(node.val);  // no children, so this is a leaf
        leaves(node.left, out);
        leaves(node.right, out);
    }

    public static void main(String[] args) {
        //        1
        //      /   \
        //     2     3
        //    / \     \
        //   4   5     6
        Node root = new Node(1, new Node(2, new Node(4), new Node(5)), new Node(3, null, new Node(6)));
        System.out.println("size " + size(root));
        System.out.println("height " + height(root));
        List<Integer> found = new ArrayList<>();
        leaves(root, found);
        System.out.println("leaves " + join(found));
    }
''', 'import java.util.ArrayList;\nimport java.util.List;\n\n', (JAVA_NODE, JAVA_JOIN)))

C('traversals', py=PY_NODE + r'''

def preorder(node, out):
    if node is None:
        return
    out.append(node.val)              # node first
    preorder(node.left, out)
    preorder(node.right, out)


def inorder(node, out):
    if node is None:
        return
    inorder(node.left, out)
    out.append(node.val)              # node between its subtrees
    inorder(node.right, out)


def postorder(node, out):
    if node is None:
        return
    postorder(node.left, out)
    postorder(node.right, out)
    out.append(node.val)              # node last


root = Node(1, Node(2, Node(4), Node(5)), Node(3, None, Node(6)))
for name, walk in [("preorder", preorder), ("inorder", inorder), ("postorder", postorder)]:
    out = []
    walk(root, out)
    print(name, " ".join(str(v) for v in out))
''', js=JS_NODE + r'''
function preorder(node, out) {
  if (node === null) return;
  out.push(node.val);                 // node first
  preorder(node.left, out);
  preorder(node.right, out);
}

function inorder(node, out) {
  if (node === null) return;
  inorder(node.left, out);
  out.push(node.val);                 // node between its subtrees
  inorder(node.right, out);
}

function postorder(node, out) {
  if (node === null) return;
  postorder(node.left, out);
  postorder(node.right, out);
  out.push(node.val);                 // node last
}

const root = new Node(1, new Node(2, new Node(4), new Node(5)), new Node(3, null, new Node(6)));
for (const [name, walk] of [["preorder", preorder], ["inorder", inorder], ["postorder", postorder]]) {
  const out = [];
  walk(root, out);
  console.log(name, out.join(" "));
}
''', java=jv('Traversals', r'''
    static void preorder(Node node, List<Integer> out) {
        if (node == null) return;
        out.add(node.val);              // node first
        preorder(node.left, out);
        preorder(node.right, out);
    }

    static void inorder(Node node, List<Integer> out) {
        if (node == null) return;
        inorder(node.left, out);
        out.add(node.val);              // node between its subtrees
        inorder(node.right, out);
    }

    static void postorder(Node node, List<Integer> out) {
        if (node == null) return;
        postorder(node.left, out);
        postorder(node.right, out);
        out.add(node.val);              // node last
    }

    public static void main(String[] args) {
        Node root = new Node(1, new Node(2, new Node(4), new Node(5)), new Node(3, null, new Node(6)));
        List<Integer> out = new ArrayList<>();
        preorder(root, out);
        System.out.println("preorder " + join(out));
        out.clear();
        inorder(root, out);
        System.out.println("inorder " + join(out));
        out.clear();
        postorder(root, out);
        System.out.println("postorder " + join(out));
    }
''', 'import java.util.ArrayList;\nimport java.util.List;\n\n', (JAVA_NODE, JAVA_JOIN)))

C('level_order', py=r'''
from collections import deque
''' + PY_NODE + r'''

def level_order(root):
    queue = deque([root])
    level = 0
    while queue:
        row = []
        for _ in range(len(queue)):   # exactly the nodes of this level
            node = queue.popleft()
            row.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        print("level", level, ":", " ".join(str(v) for v in row))
        level += 1


root = Node(1, Node(2, Node(4), Node(5)), Node(3, None, Node(6)))
level_order(root)
''', js=JS_NODE + r'''
function levelOrder(root) {
  let queue = [root];
  let level = 0;
  while (queue.length > 0) {
    const next = [];
    const row = [];
    for (const node of queue) {        // exactly the nodes of this level
      row.push(node.val);
      if (node.left) next.push(node.left);
      if (node.right) next.push(node.right);
    }
    console.log("level", level, ":", row.join(" "));
    queue = next;
    level++;
  }
}

const root = new Node(1, new Node(2, new Node(4), new Node(5)), new Node(3, null, new Node(6)));
levelOrder(root);
''', java=jv('LevelOrder', r'''
    static void levelOrder(Node root) {
        ArrayDeque<Node> queue = new ArrayDeque<>();
        queue.add(root);
        int level = 0;
        while (!queue.isEmpty()) {
            StringBuilder row = new StringBuilder();
            int count = queue.size();
            for (int k = 0; k < count; k++) {   // exactly the nodes of this level
                Node node = queue.poll();
                if (row.length() > 0) row.append(" ");
                row.append(node.val);
                if (node.left != null) queue.add(node.left);
                if (node.right != null) queue.add(node.right);
            }
            System.out.println("level " + level + " : " + row);
            level++;
        }
    }

    public static void main(String[] args) {
        Node root = new Node(1, new Node(2, new Node(4), new Node(5)), new Node(3, null, new Node(6)));
        levelOrder(root);
    }
''', 'import java.util.ArrayDeque;\n\n'))

C('bst_ops', py=PY_NODE + r'''

def insert(node, val):
    if node is None:
        return Node(val)              # an empty spot: the new value lives here
    if val < node.val:
        node.left = insert(node.left, val)
    else:
        node.right = insert(node.right, val)
    return node


def search(node, val):
    path = []
    while node is not None:
        path.append(node.val)
        if val == node.val:
            return path, True
        node = node.left if val < node.val else node.right   # throw away one side
    return path, False


def inorder(node, out):
    if node:
        inorder(node.left, out)
        out.append(node.val)
        inorder(node.right, out)


root = None
for v in [8, 3, 10, 1, 6, 14, 4, 7, 13]:
    root = insert(root, v)

out = []
inorder(root, out)
print("sorted", " ".join(str(v) for v in out))
for target in [6, 5]:
    path, ok = search(root, target)
    print("search", target, ":", " ".join(str(v) for v in path), "found" if ok else "missing")

lo = root
while lo.left:
    lo = lo.left                      # the smallest value is all the way left
hi = root
while hi.right:
    hi = hi.right                     # the largest is all the way right
print("min", lo.val, "max", hi.val)
''', js=JS_NODE + r'''
function insert(node, val) {
  if (node === null) return new Node(val);   // an empty spot: the new value lives here
  if (val < node.val) node.left = insert(node.left, val);
  else node.right = insert(node.right, val);
  return node;
}

function search(node, val) {
  const path = [];
  while (node !== null) {
    path.push(node.val);
    if (val === node.val) return [path, true];
    node = val < node.val ? node.left : node.right;  // throw away one side
  }
  return [path, false];
}

function inorder(node, out) {
  if (node) {
    inorder(node.left, out);
    out.push(node.val);
    inorder(node.right, out);
  }
}

let root = null;
for (const v of [8, 3, 10, 1, 6, 14, 4, 7, 13]) root = insert(root, v);

const out = [];
inorder(root, out);
console.log("sorted", out.join(" "));
for (const target of [6, 5]) {
  const [path, ok] = search(root, target);
  console.log("search", target, ":", path.join(" "), ok ? "found" : "missing");
}

let lo = root;
while (lo.left) lo = lo.left;         // the smallest value is all the way left
let hi = root;
while (hi.right) hi = hi.right;       // the largest is all the way right
console.log("min", lo.val, "max", hi.val);
''', java=jv('BstOps', r'''
    static Node insert(Node node, int val) {
        if (node == null) return new Node(val);   // an empty spot: the new value lives here
        if (val < node.val) node.left = insert(node.left, val);
        else node.right = insert(node.right, val);
        return node;
    }

    static boolean search(Node node, int val, List<Integer> path) {
        while (node != null) {
            path.add(node.val);
            if (val == node.val) return true;
            node = val < node.val ? node.left : node.right;  // throw away one side
        }
        return false;
    }

    static void inorder(Node node, List<Integer> out) {
        if (node != null) {
            inorder(node.left, out);
            out.add(node.val);
            inorder(node.right, out);
        }
    }

    public static void main(String[] args) {
        Node root = null;
        for (int v : new int[]{8, 3, 10, 1, 6, 14, 4, 7, 13}) root = insert(root, v);

        List<Integer> out = new ArrayList<>();
        inorder(root, out);
        System.out.println("sorted " + join(out));
        for (int target : new int[]{6, 5}) {
            List<Integer> path = new ArrayList<>();
            boolean ok = search(root, target, path);
            System.out.println("search " + target + " : " + join(path) + (ok ? " found" : " missing"));
        }

        Node lo = root;
        while (lo.left != null) lo = lo.left;     // the smallest value is all the way left
        Node hi = root;
        while (hi.right != null) hi = hi.right;   // the largest is all the way right
        System.out.println("min " + lo.val + " max " + hi.val);
    }
''', 'import java.util.ArrayList;\nimport java.util.List;\n\n', (JAVA_NODE, JAVA_JOIN)))

C('bst_delete', py=PY_NODE + r'''

def insert(node, val):
    if node is None:
        return Node(val)
    if val < node.val:
        node.left = insert(node.left, val)
    else:
        node.right = insert(node.right, val)
    return node


def delete(node, val):
    if node is None:
        return None
    if val < node.val:
        node.left = delete(node.left, val)
    elif val > node.val:
        node.right = delete(node.right, val)
    else:
        if node.left is None:
            return node.right         # zero or one child: lift the child up
        if node.right is None:
            return node.left
        succ = node.right             # two children: smallest value on the right
        while succ.left is not None:
            succ = succ.left
        node.val = succ.val           # copy it here, then delete it down there
        node.right = delete(node.right, succ.val)
    return node


def inorder(node, out):
    if node:
        inorder(node.left, out)
        out.append(node.val)
        inorder(node.right, out)


root = None
for v in [8, 3, 10, 1, 6, 14, 4, 7, 13]:
    root = insert(root, v)

for v in [3, 1, 10]:                  # two children, a leaf, one child
    root = delete(root, v)
    out = []
    inorder(root, out)
    print("delete", v, "->", " ".join(str(x) for x in out))
print("root", root.val, "left", root.left.val, "right", root.right.val)
''', js=JS_NODE + r'''
function insert(node, val) {
  if (node === null) return new Node(val);
  if (val < node.val) node.left = insert(node.left, val);
  else node.right = insert(node.right, val);
  return node;
}

function remove(node, val) {
  if (node === null) return null;
  if (val < node.val) node.left = remove(node.left, val);
  else if (val > node.val) node.right = remove(node.right, val);
  else {
    if (node.left === null) return node.right;   // zero or one child: lift the child up
    if (node.right === null) return node.left;
    let succ = node.right;                       // two children: smallest value on the right
    while (succ.left !== null) succ = succ.left;
    node.val = succ.val;                         // copy it here, then delete it down there
    node.right = remove(node.right, succ.val);
  }
  return node;
}

function inorder(node, out) {
  if (node) {
    inorder(node.left, out);
    out.push(node.val);
    inorder(node.right, out);
  }
}

let root = null;
for (const v of [8, 3, 10, 1, 6, 14, 4, 7, 13]) root = insert(root, v);

for (const v of [3, 1, 10]) {         // two children, a leaf, one child
  root = remove(root, v);
  const out = [];
  inorder(root, out);
  console.log("delete", v, "->", out.join(" "));
}
console.log("root", root.val, "left", root.left.val, "right", root.right.val);
''', java=jv('BstDelete', r'''
    static Node insert(Node node, int val) {
        if (node == null) return new Node(val);
        if (val < node.val) node.left = insert(node.left, val);
        else node.right = insert(node.right, val);
        return node;
    }

    static Node delete(Node node, int val) {
        if (node == null) return null;
        if (val < node.val) node.left = delete(node.left, val);
        else if (val > node.val) node.right = delete(node.right, val);
        else {
            if (node.left == null) return node.right;   // zero or one child: lift the child up
            if (node.right == null) return node.left;
            Node succ = node.right;                     // two children: smallest value on the right
            while (succ.left != null) succ = succ.left;
            node.val = succ.val;                        // copy it here, then delete it down there
            node.right = delete(node.right, succ.val);
        }
        return node;
    }

    static void inorder(Node node, List<Integer> out) {
        if (node != null) {
            inorder(node.left, out);
            out.add(node.val);
            inorder(node.right, out);
        }
    }

    public static void main(String[] args) {
        Node root = null;
        for (int v : new int[]{8, 3, 10, 1, 6, 14, 4, 7, 13}) root = insert(root, v);

        for (int v : new int[]{3, 1, 10}) {     // two children, a leaf, one child
            root = delete(root, v);
            List<Integer> out = new ArrayList<>();
            inorder(root, out);
            System.out.println("delete " + v + " -> " + join(out));
        }
        System.out.println("root " + root.val + " left " + root.left.val + " right " + root.right.val);
    }
''', 'import java.util.ArrayList;\nimport java.util.List;\n\n', (JAVA_NODE, JAVA_JOIN)))

C('build_balanced', py=PY_NODE + r'''

def insert(node, val):
    if node is None:
        return Node(val)
    if val < node.val:
        node.left = insert(node.left, val)
    else:
        node.right = insert(node.right, val)
    return node


def height(node):
    if node is None:
        return 0
    return 1 + max(height(node.left), height(node.right))


def from_sorted(vals, lo, hi):
    if lo > hi:
        return None
    mid = (lo + hi) // 2              # the middle value becomes the root
    return Node(vals[mid], from_sorted(vals, lo, mid - 1), from_sorted(vals, mid + 1, hi))


def preorder(node, out):
    if node:
        out.append(node.val)
        preorder(node.left, out)
        preorder(node.right, out)


vals = [1, 2, 3, 4, 5, 6, 7]
chain = None
for v in vals:
    chain = insert(chain, v)          # sorted input makes every node a right child
print("inserted in sorted order: height", height(chain))
good = from_sorted(vals, 0, len(vals) - 1)
print("built from the middle: height", height(good))
out = []
preorder(good, out)
print("preorder", " ".join(str(v) for v in out))
''', js=JS_NODE + r'''
function insert(node, val) {
  if (node === null) return new Node(val);
  if (val < node.val) node.left = insert(node.left, val);
  else node.right = insert(node.right, val);
  return node;
}

function height(node) {
  if (node === null) return 0;
  return 1 + Math.max(height(node.left), height(node.right));
}

function fromSorted(vals, lo, hi) {
  if (lo > hi) return null;
  const mid = Math.floor((lo + hi) / 2);   // the middle value becomes the root
  return new Node(vals[mid], fromSorted(vals, lo, mid - 1), fromSorted(vals, mid + 1, hi));
}

function preorder(node, out) {
  if (node) {
    out.push(node.val);
    preorder(node.left, out);
    preorder(node.right, out);
  }
}

const vals = [1, 2, 3, 4, 5, 6, 7];
let chain = null;
for (const v of vals) chain = insert(chain, v);   // sorted input makes every node a right child
console.log("inserted in sorted order: height", height(chain));
const good = fromSorted(vals, 0, vals.length - 1);
console.log("built from the middle: height", height(good));
const out = [];
preorder(good, out);
console.log("preorder", out.join(" "));
''', java=jv('BuildBalanced', r'''
    static Node insert(Node node, int val) {
        if (node == null) return new Node(val);
        if (val < node.val) node.left = insert(node.left, val);
        else node.right = insert(node.right, val);
        return node;
    }

    static int height(Node node) {
        if (node == null) return 0;
        return 1 + Math.max(height(node.left), height(node.right));
    }

    static Node fromSorted(int[] vals, int lo, int hi) {
        if (lo > hi) return null;
        int mid = (lo + hi) / 2;               // the middle value becomes the root
        return new Node(vals[mid], fromSorted(vals, lo, mid - 1), fromSorted(vals, mid + 1, hi));
    }

    static void preorder(Node node, List<Integer> out) {
        if (node != null) {
            out.add(node.val);
            preorder(node.left, out);
            preorder(node.right, out);
        }
    }

    public static void main(String[] args) {
        int[] vals = {1, 2, 3, 4, 5, 6, 7};
        Node chain = null;
        for (int v : vals) chain = insert(chain, v);  // sorted input makes every node a right child
        System.out.println("inserted in sorted order: height " + height(chain));
        Node good = fromSorted(vals, 0, vals.length - 1);
        System.out.println("built from the middle: height " + height(good));
        List<Integer> out = new ArrayList<>();
        preorder(good, out);
        System.out.println("preorder " + join(out));
    }
''', 'import java.util.ArrayList;\nimport java.util.List;\n\n', (JAVA_NODE, JAVA_JOIN)))

C('heap_array', py=r'''
heap = []


def push(x):
    heap.append(x)                    # add at the end, then bubble up
    i = len(heap) - 1
    while i > 0:
        parent = (i - 1) // 2
        if heap[parent] <= heap[i]:
            break
        heap[parent], heap[i] = heap[i], heap[parent]
        i = parent


def pop():
    top = heap[0]
    last = heap.pop()
    if heap:
        heap[0] = last                # move the last item to the root, then sink it
        i = 0
        while True:
            small = i
            for c in (2 * i + 1, 2 * i + 2):
                if c < len(heap) and heap[c] < heap[small]:
                    small = c
            if small == i:
                break
            heap[small], heap[i] = heap[i], heap[small]
            i = small
    return top


for x in [5, 3, 8, 1, 9, 2]:
    push(x)
print("heap", " ".join(str(v) for v in heap))
out = []
while heap:
    out.append(pop())
print("pops", " ".join(str(v) for v in out))
''', js=r'''
const heap = [];

function push(x) {
  heap.push(x);                       // add at the end, then bubble up
  let i = heap.length - 1;
  while (i > 0) {
    const parent = Math.floor((i - 1) / 2);
    if (heap[parent] <= heap[i]) break;
    [heap[parent], heap[i]] = [heap[i], heap[parent]];
    i = parent;
  }
}

function pop() {
  const top = heap[0];
  const last = heap.pop();
  if (heap.length > 0) {
    heap[0] = last;                   // move the last item to the root, then sink it
    let i = 0;
    while (true) {
      let small = i;
      for (const c of [2 * i + 1, 2 * i + 2]) {
        if (c < heap.length && heap[c] < heap[small]) small = c;
      }
      if (small === i) break;
      [heap[small], heap[i]] = [heap[i], heap[small]];
      i = small;
    }
  }
  return top;
}

for (const x of [5, 3, 8, 1, 9, 2]) push(x);
console.log("heap", heap.join(" "));
const out = [];
while (heap.length > 0) out.push(pop());
console.log("pops", out.join(" "));
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class HeapArray {
    static List<Integer> heap = new ArrayList<>();

    static void swap(int a, int b) {
        int t = heap.get(a);
        heap.set(a, heap.get(b));
        heap.set(b, t);
    }

    static void push(int x) {
        heap.add(x);                        // add at the end, then bubble up
        int i = heap.size() - 1;
        while (i > 0) {
            int parent = (i - 1) / 2;
            if (heap.get(parent) <= heap.get(i)) break;
            swap(parent, i);
            i = parent;
        }
    }

    static int pop() {
        int top = heap.get(0);
        int last = heap.remove(heap.size() - 1);
        if (!heap.isEmpty()) {
            heap.set(0, last);              // move the last item to the root, then sink it
            int i = 0;
            while (true) {
                int small = i;
                for (int c : new int[]{2 * i + 1, 2 * i + 2}) {
                    if (c < heap.size() && heap.get(c) < heap.get(small)) small = c;
                }
                if (small == i) break;
                swap(small, i);
                i = small;
            }
        }
        return top;
    }

    static String join(List<Integer> xs) {
        StringBuilder sb = new StringBuilder();
        for (int x : xs) {
            if (sb.length() > 0) sb.append(" ");
            sb.append(x);
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        for (int x : new int[]{5, 3, 8, 1, 9, 2}) push(x);
        System.out.println("heap " + join(heap));
        List<Integer> out = new ArrayList<>();
        while (!heap.isEmpty()) out.add(pop());
        System.out.println("pops " + join(out));
    }
}
''')

C('trie', py=r'''
class TrieNode:
    def __init__(self):
        self.children = {}            # letter -> TrieNode
        self.word = False             # does a word end here


root = TrieNode()


def insert(word):
    node = root
    for ch in word:
        if ch not in node.children:
            node.children[ch] = TrieNode()
        node = node.children[ch]
    node.word = True


def walk(prefix):
    node = root
    for ch in prefix:
        if ch not in node.children:
            return None
        node = node.children[ch]
    return node


def collect(node, prefix, out):
    if node.word:
        out.append(prefix)
    for ch in sorted(node.children):  # alphabetical order
        collect(node.children[ch], prefix + ch, out)


for w in ["car", "cart", "care", "cat", "dog"]:
    insert(w)

for w in ["car", "ca"]:
    node = walk(w)
    print("search", w, "true" if node is not None and node.word else "false")
out = []
collect(walk("ca"), "ca", out)
print("prefix ca:", len(out), "words")
out = []
collect(walk("car"), "car", out)
print("words starting with car:", " ".join(out))
''', js=r'''
class TrieNode {
  constructor() {
    this.children = {};               // letter -> TrieNode
    this.word = false;                // does a word end here
  }
}

const root = new TrieNode();

function insert(word) {
  let node = root;
  for (const ch of word) {
    if (!(ch in node.children)) node.children[ch] = new TrieNode();
    node = node.children[ch];
  }
  node.word = true;
}

function walk(prefix) {
  let node = root;
  for (const ch of prefix) {
    if (!(ch in node.children)) return null;
    node = node.children[ch];
  }
  return node;
}

function collect(node, prefix, out) {
  if (node.word) out.push(prefix);
  for (const ch of Object.keys(node.children).sort()) {  // alphabetical order
    collect(node.children[ch], prefix + ch, out);
  }
}

for (const w of ["car", "cart", "care", "cat", "dog"]) insert(w);

for (const w of ["car", "ca"]) {
  const node = walk(w);
  console.log("search", w, node !== null && node.word ? "true" : "false");
}
let out = [];
collect(walk("ca"), "ca", out);
console.log("prefix ca:", out.length, "words");
out = [];
collect(walk("car"), "car", out);
console.log("words starting with car:", out.join(" "));
''', java=r'''
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class Trie {
    static class TrieNode {
        Map<Character, TrieNode> children = new TreeMap<>();  // letter -> TrieNode, kept sorted
        boolean word;                                         // does a word end here
    }

    static TrieNode root = new TrieNode();

    static void insert(String word) {
        TrieNode node = root;
        for (char ch : word.toCharArray()) {
            if (!node.children.containsKey(ch)) node.children.put(ch, new TrieNode());
            node = node.children.get(ch);
        }
        node.word = true;
    }

    static TrieNode walk(String prefix) {
        TrieNode node = root;
        for (char ch : prefix.toCharArray()) {
            if (!node.children.containsKey(ch)) return null;
            node = node.children.get(ch);
        }
        return node;
    }

    static void collect(TrieNode node, String prefix, List<String> out) {
        if (node.word) out.add(prefix);
        for (char ch : node.children.keySet()) {               // alphabetical order
            collect(node.children.get(ch), prefix + ch, out);
        }
    }

    public static void main(String[] args) {
        for (String w : new String[]{"car", "cart", "care", "cat", "dog"}) insert(w);

        for (String w : new String[]{"car", "ca"}) {
            TrieNode node = walk(w);
            System.out.println("search " + w + " " + (node != null && node.word ? "true" : "false"));
        }
        List<String> out = new ArrayList<>();
        collect(walk("ca"), "ca", out);
        System.out.println("prefix ca: " + out.size() + " words");
        out = new ArrayList<>();
        collect(walk("car"), "car", out);
        System.out.println("words starting with car: " + String.join(" ", out));
    }
}
''')

# ---------------------------------------------------------------- practice programs
PYF = 'from collections import deque\n' + PY_NODE + PY_FROM
JAVA_IMPORTS = 'import java.util.ArrayDeque;\nimport java.util.ArrayList;\nimport java.util.List;\n\n'
JH = (JAVA_NODE, JAVA_FROM, JAVA_JOIN)

C('p_max_depth', py=PYF + r'''

def max_depth(node):
    if node is None:
        return 0
    return 1 + max(max_depth(node.left), max_depth(node.right))


def min_depth(node):
    if node is None:
        return 0
    if node.left is None:             # a missing side is not a leaf, so follow the other
        return 1 + min_depth(node.right)
    if node.right is None:
        return 1 + min_depth(node.left)
    return 1 + min(min_depth(node.left), min_depth(node.right))


for vals in [[3, 9, 20, None, None, 15, 7], [1, None, 2, None, 3]]:
    root = from_list(vals)
    print("max depth", max_depth(root), "min depth", min_depth(root))
''', js=JS_NODE + JS_FROM + r'''
function maxDepth(node) {
  if (node === null) return 0;
  return 1 + Math.max(maxDepth(node.left), maxDepth(node.right));
}

function minDepth(node) {
  if (node === null) return 0;
  if (node.left === null) return 1 + minDepth(node.right);   // a missing side is not a leaf, so follow the other
  if (node.right === null) return 1 + minDepth(node.left);
  return 1 + Math.min(minDepth(node.left), minDepth(node.right));
}

for (const vals of [[3, 9, 20, null, null, 15, 7], [1, null, 2, null, 3]]) {
  const root = fromList(vals);
  console.log("max depth", maxDepth(root), "min depth", minDepth(root));
}
''', java=jv('MaxDepth', r'''
    static int maxDepth(Node node) {
        if (node == null) return 0;
        return 1 + Math.max(maxDepth(node.left), maxDepth(node.right));
    }

    static int minDepth(Node node) {
        if (node == null) return 0;
        if (node.left == null) return 1 + minDepth(node.right);  // a missing side is not a leaf, so follow the other
        if (node.right == null) return 1 + minDepth(node.left);
        return 1 + Math.min(minDepth(node.left), minDepth(node.right));
    }

    public static void main(String[] args) {
        Integer[][] trees = {{3, 9, 20, null, null, 15, 7}, {1, null, 2, null, 3}};
        for (Integer[] vals : trees) {
            Node root = fromList(vals);
            System.out.println("max depth " + maxDepth(root) + " min depth " + minDepth(root));
        }
    }
''', JAVA_IMPORTS, JH))

C('p_invert', py=PYF + r'''

def invert(node):
    if node is None:
        return None
    node.left, node.right = invert(node.right), invert(node.left)   # swap the two subtrees
    return node


def levels(root):
    out, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        out.append(node.val)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return " ".join(str(v) for v in out)


root = from_list([4, 2, 7, 1, 3, 6, 9])
print("before", levels(root))
invert(root)
print("after ", levels(root))
''', js=JS_NODE + JS_FROM + r'''
function invert(node) {
  if (node === null) return null;
  [node.left, node.right] = [invert(node.right), invert(node.left)];  // swap the two subtrees
  return node;
}

function levels(root) {
  const out = [], queue = [root];
  for (let h = 0; h < queue.length; h++) {
    const node = queue[h];
    out.push(node.val);
    if (node.left) queue.push(node.left);
    if (node.right) queue.push(node.right);
  }
  return out.join(" ");
}

const root = fromList([4, 2, 7, 1, 3, 6, 9]);
console.log("before", levels(root));
invert(root);
console.log("after ", levels(root));
''', java=jv('Invert', r'''
    static Node invert(Node node) {
        if (node == null) return null;
        Node left = invert(node.left);
        node.left = invert(node.right);     // swap the two subtrees
        node.right = left;
        return node;
    }

    static String levels(Node root) {
        List<Integer> out = new ArrayList<>();
        ArrayDeque<Node> queue = new ArrayDeque<>();
        queue.add(root);
        while (!queue.isEmpty()) {
            Node node = queue.poll();
            out.add(node.val);
            if (node.left != null) queue.add(node.left);
            if (node.right != null) queue.add(node.right);
        }
        return join(out);
    }

    public static void main(String[] args) {
        Node root = fromList(4, 2, 7, 1, 3, 6, 9);
        System.out.println("before " + levels(root));
        invert(root);
        System.out.println("after  " + levels(root));
    }
''', JAVA_IMPORTS, JH))

C('p_validate', py=PYF + r'''

def is_bst(node, lo=None, hi=None):
    if node is None:
        return True
    if (lo is not None and node.val <= lo) or (hi is not None and node.val >= hi):
        return False                  # outside the range its ancestors allow
    return is_bst(node.left, lo, node.val) and is_bst(node.right, node.val, hi)


for vals in [[5, 3, 8, 1, 4, 7, 9], [5, 3, 8, 1, 6, 7, 9]]:
    print(vals, "valid" if is_bst(from_list(vals)) else "invalid")
''', js=JS_NODE + JS_FROM + r'''
function isBst(node, lo = null, hi = null) {
  if (node === null) return true;
  if ((lo !== null && node.val <= lo) || (hi !== null && node.val >= hi)) return false;  // outside the range its ancestors allow
  return isBst(node.left, lo, node.val) && isBst(node.right, node.val, hi);
}

for (const vals of [[5, 3, 8, 1, 4, 7, 9], [5, 3, 8, 1, 6, 7, 9]]) {
  console.log("[" + vals.join(", ") + "]", isBst(fromList(vals)) ? "valid" : "invalid");
}
''', java=jv('ValidateBst', r'''
    static boolean isBst(Node node, Integer lo, Integer hi) {
        if (node == null) return true;
        if ((lo != null && node.val <= lo) || (hi != null && node.val >= hi)) return false;  // outside the range its ancestors allow
        return isBst(node.left, lo, node.val) && isBst(node.right, node.val, hi);
    }

    public static void main(String[] args) {
        Integer[][] trees = {{5, 3, 8, 1, 4, 7, 9}, {5, 3, 8, 1, 6, 7, 9}};
        for (Integer[] vals : trees) {
            System.out.println(java.util.Arrays.toString(vals) + " " + (isBst(fromList(vals), null, null) ? "valid" : "invalid"));
        }
    }
''', JAVA_IMPORTS, JH))

C('p_path_sum', py=PYF + r'''

def paths(node, target, path, out):
    if node is None:
        return
    path.append(node.val)
    target -= node.val
    if node.left is None and node.right is None and target == 0:
        out.append(" ".join(str(v) for v in path))   # a leaf that hits the target exactly
    paths(node.left, target, path, out)
    paths(node.right, target, path, out)
    path.pop()                        # step back before trying another branch


root = from_list([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1])
found = []
paths(root, 22, [], found)
for p in found:
    print("path", p)
''', js=JS_NODE + JS_FROM + r'''
function paths(node, target, path, out) {
  if (node === null) return;
  path.push(node.val);
  target -= node.val;
  if (node.left === null && node.right === null && target === 0) out.push(path.join(" "));  // a leaf that hits the target exactly
  paths(node.left, target, path, out);
  paths(node.right, target, path, out);
  path.pop();                         // step back before trying another branch
}

const root = fromList([5, 4, 8, 11, null, 13, 4, 7, 2, null, null, 5, 1]);
const found = [];
paths(root, 22, [], found);
for (const p of found) console.log("path", p);
''', java=jv('PathSum', r'''
    static void paths(Node node, int target, List<Integer> path, List<String> out) {
        if (node == null) return;
        path.add(node.val);
        target -= node.val;
        if (node.left == null && node.right == null && target == 0) out.add(join(path));  // a leaf that hits the target exactly
        paths(node.left, target, path, out);
        paths(node.right, target, path, out);
        path.remove(path.size() - 1);       // step back before trying another branch
    }

    public static void main(String[] args) {
        Node root = fromList(5, 4, 8, 11, null, 13, 4, 7, 2, null, null, 5, 1);
        List<String> found = new ArrayList<>();
        paths(root, 22, new ArrayList<>(), found);
        for (String p : found) System.out.println("path " + p);
    }
''', JAVA_IMPORTS, JH))

C('p_lca', py=PYF + r'''

def lca(node, p, q):
    if node is None or node.val == p or node.val == q:
        return node
    left = lca(node.left, p, q)
    right = lca(node.right, p, q)
    if left is not None and right is not None:
        return node                   # p and q sit on different sides of this node
    return left if left is not None else right


root = from_list([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
for p, q in [(5, 1), (5, 4), (7, 8), (6, 4)]:
    print("lca of", p, "and", q, "is", lca(root, p, q).val)
''', js=JS_NODE + JS_FROM + r'''
function lca(node, p, q) {
  if (node === null || node.val === p || node.val === q) return node;
  const left = lca(node.left, p, q);
  const right = lca(node.right, p, q);
  if (left !== null && right !== null) return node;   // p and q sit on different sides of this node
  return left !== null ? left : right;
}

const root = fromList([3, 5, 1, 6, 2, 0, 8, null, null, 7, 4]);
for (const [p, q] of [[5, 1], [5, 4], [7, 8], [6, 4]]) {
  console.log("lca of", p, "and", q, "is", lca(root, p, q).val);
}
''', java=jv('Lca', r'''
    static Node lca(Node node, int p, int q) {
        if (node == null || node.val == p || node.val == q) return node;
        Node left = lca(node.left, p, q);
        Node right = lca(node.right, p, q);
        if (left != null && right != null) return node;   // p and q sit on different sides of this node
        return left != null ? left : right;
    }

    public static void main(String[] args) {
        Node root = fromList(3, 5, 1, 6, 2, 0, 8, null, null, 7, 4);
        int[][] pairs = {{5, 1}, {5, 4}, {7, 8}, {6, 4}};
        for (int[] pq : pairs) {
            System.out.println("lca of " + pq[0] + " and " + pq[1] + " is " + lca(root, pq[0], pq[1]).val);
        }
    }
''', JAVA_IMPORTS, JH))

C('p_serialize', py=PYF + r'''

def serialize(node, out):
    if node is None:
        out.append("#")               # mark the empty spot so the shape is kept
        return
    out.append(str(node.val))
    serialize(node.left, out)
    serialize(node.right, out)


def deserialize(tokens, pos):
    t = tokens[pos[0]]
    pos[0] += 1
    if t == "#":
        return None
    node = Node(int(t))
    node.left = deserialize(tokens, pos)    # same order as serialize: node, left, right
    node.right = deserialize(tokens, pos)
    return node


root = from_list([1, 2, 3, None, None, 4, 5])
out = []
serialize(root, out)
text = ",".join(out)
print("text  ", text)
copy = deserialize(text.split(","), [0])
again = []
serialize(copy, again)
print("again ", ",".join(again))
print("match", "true" if ",".join(again) == text else "false")
''', js=JS_NODE + JS_FROM + r'''
function serialize(node, out) {
  if (node === null) { out.push("#"); return; }   // mark the empty spot so the shape is kept
  out.push(String(node.val));
  serialize(node.left, out);
  serialize(node.right, out);
}

function deserialize(tokens, pos) {
  const t = tokens[pos[0]];
  pos[0]++;
  if (t === "#") return null;
  const node = new Node(Number(t));
  node.left = deserialize(tokens, pos);     // same order as serialize: node, left, right
  node.right = deserialize(tokens, pos);
  return node;
}

const root = fromList([1, 2, 3, null, null, 4, 5]);
const out = [];
serialize(root, out);
const text = out.join(",");
console.log("text  ", text);
const copy = deserialize(text.split(","), [0]);
const again = [];
serialize(copy, again);
console.log("again ", again.join(","));
console.log("match", again.join(",") === text ? "true" : "false");
''', java=jv('Serialize', r'''
    static void serialize(Node node, List<String> out) {
        if (node == null) { out.add("#"); return; }     // mark the empty spot so the shape is kept
        out.add(String.valueOf(node.val));
        serialize(node.left, out);
        serialize(node.right, out);
    }

    static Node deserialize(String[] tokens, int[] pos) {
        String t = tokens[pos[0]];
        pos[0]++;
        if (t.equals("#")) return null;
        Node node = new Node(Integer.parseInt(t));
        node.left = deserialize(tokens, pos);       // same order as serialize: node, left, right
        node.right = deserialize(tokens, pos);
        return node;
    }

    public static void main(String[] args) {
        Node root = fromList(1, 2, 3, null, null, 4, 5);
        List<String> out = new ArrayList<>();
        serialize(root, out);
        String text = String.join(",", out);
        System.out.println("text   " + text);
        Node copy = deserialize(text.split(","), new int[]{0});
        List<String> again = new ArrayList<>();
        serialize(copy, again);
        System.out.println("again  " + String.join(",", again));
        System.out.println("match " + (String.join(",", again).equals(text) ? "true" : "false"));
    }
''', JAVA_IMPORTS, JH))

C('p_diameter', py=PYF + r'''

def diameter(root):
    best = 0

    def height(node):
        nonlocal best
        if node is None:
            return 0
        left = height(node.left)
        right = height(node.right)
        best = max(best, left + right)    # the longest path that bends at this node
        return 1 + max(left, right)

    height(root)
    return best


for vals in [[1, 2, 3, 4, 5], [1, 2, None, 4, 5, 6, None, None, 7]]:
    print("diameter", diameter(from_list(vals)))
''', js=JS_NODE + JS_FROM + r'''
function diameter(root) {
  let best = 0;
  function height(node) {
    if (node === null) return 0;
    const left = height(node.left);
    const right = height(node.right);
    best = Math.max(best, left + right);  // the longest path that bends at this node
    return 1 + Math.max(left, right);
  }
  height(root);
  return best;
}

for (const vals of [[1, 2, 3, 4, 5], [1, 2, null, 4, 5, 6, null, null, 7]]) {
  console.log("diameter", diameter(fromList(vals)));
}
''', java=jv('Diameter', r'''
    static int best;

    static int height(Node node) {
        if (node == null) return 0;
        int left = height(node.left);
        int right = height(node.right);
        best = Math.max(best, left + right);  // the longest path that bends at this node
        return 1 + Math.max(left, right);
    }

    static int diameter(Node root) {
        best = 0;
        height(root);
        return best;
    }

    public static void main(String[] args) {
        Integer[][] trees = {{1, 2, 3, 4, 5}, {1, 2, null, 4, 5, 6, null, null, 7}};
        for (Integer[] vals : trees) System.out.println("diameter " + diameter(fromList(vals)));
    }
''', JAVA_IMPORTS, JH))

C('p_max_path', py=PYF + r'''

def max_path_sum(root):
    best = root.val

    def gain(node):
        nonlocal best
        if node is None:
            return 0
        left = max(0, gain(node.left))    # a negative branch is better left out
        right = max(0, gain(node.right))
        best = max(best, node.val + left + right)
        return node.val + max(left, right)    # a parent can only continue one way

    gain(root)
    return best


for vals in [[-10, 9, 20, None, None, 15, 7], [2, -1], [-3]]:
    print("max path sum", max_path_sum(from_list(vals)))
''', js=JS_NODE + JS_FROM + r'''
function maxPathSum(root) {
  let best = root.val;
  function gain(node) {
    if (node === null) return 0;
    const left = Math.max(0, gain(node.left));   // a negative branch is better left out
    const right = Math.max(0, gain(node.right));
    best = Math.max(best, node.val + left + right);
    return node.val + Math.max(left, right);     // a parent can only continue one way
  }
  gain(root);
  return best;
}

for (const vals of [[-10, 9, 20, null, null, 15, 7], [2, -1], [-3]]) {
  console.log("max path sum", maxPathSum(fromList(vals)));
}
''', java=jv('MaxPathSum', r'''
    static int best;

    static int gain(Node node) {
        if (node == null) return 0;
        int left = Math.max(0, gain(node.left));    // a negative branch is better left out
        int right = Math.max(0, gain(node.right));
        best = Math.max(best, node.val + left + right);
        return node.val + Math.max(left, right);    // a parent can only continue one way
    }

    static int maxPathSum(Node root) {
        best = root.val;
        gain(root);
        return best;
    }

    public static void main(String[] args) {
        Integer[][] trees = {{-10, 9, 20, null, null, 15, 7}, {2, -1}, {-3}};
        for (Integer[] vals : trees) System.out.println("max path sum " + maxPathSum(fromList(vals)));
    }
''', JAVA_IMPORTS, JH))

# ---------------------------------------------------------------- lesson text
PARTS = [
    dict(id='what-is', emoji='🌲', title='What a tree is', html='''
<p>A <b>tree</b> stores items in a hierarchy. One node at the top is the <b>root</b>. Every other node has exactly one <b>parent</b>, and any node can have <b>children</b> below it. A node with no children is a <b>leaf</b>. Folders on a computer, the parts of a web page and a company org chart are all trees.</p>
<div class="tw"><table class="jt"><tr><th>Word</th><th>Meaning</th><th>In the tree below</th></tr>
<tr><td>root</td><td>the only node with no parent</td><td>1</td></tr>
<tr><td>children</td><td>nodes directly below a node</td><td>2 and 3 are children of 1</td></tr>
<tr><td>leaf</td><td>a node with no children</td><td>4, 5 and 6</td></tr>
<tr><td>depth</td><td>edges from the root down to a node</td><td>depth of 5 is 2</td></tr>
<tr><td>height</td><td>number of levels in the tree</td><td>3</td></tr>
<tr><td>subtree</td><td>a node together with everything below it</td><td>2, 4, 5</td></tr>
</table></div>
<p>In a <b>binary tree</b> every node has at most two children, called <b>left</b> and <b>right</b>. Each node is an object holding a value and two references, just like a linked list node with two next pointers.</p>
<div class="c3" data-k="tree_basics" data-label="Size, height and leaves with recursion"></div>
<div class="rule">Most tree code follows one pattern: handle the empty tree, solve the left subtree, solve the right subtree, then combine the two answers with the current node.</div>
<div class="grid2">
<div class="box"><h4>🔢 Edges</h4><p>Every node except the root hangs from exactly one edge, so a tree with n nodes always has n − 1 edges.</p><span class="eq">edges = n − 1</span></div>
<div class="box"><h4>📏 Levels</h4><p>Level d of a binary tree holds at most 2<sup>d</sup> nodes, so a tree with h full levels holds at most 2<sup>h</sup> − 1 nodes.</p><span class="eq">n ≤ 2<sup>h</sup> − 1</span></div>
</div>
'''),
    dict(id='traversals', emoji='🚶', title='Traversals: visiting every node', html='''
<p>A <b>traversal</b> visits every node once. Depth first traversals go deep before going wide, and differ only in <b>when</b> the node itself is visited compared with its two subtrees.</p>
<div class="tw"><table class="jt"><tr><th>Order</th><th>Rule</th><th>Result for the tree</th><th>Typical use</th></tr>
<tr><td>Preorder</td><td>node, left, right</td><td>1 2 4 5 3 6</td><td>copying or saving a tree</td></tr>
<tr><td>Inorder</td><td>left, node, right</td><td>4 2 5 1 3 6</td><td>sorted output from a search tree</td></tr>
<tr><td>Postorder</td><td>left, right, node</td><td>4 5 2 6 3 1</td><td>deleting a tree, folder sizes</td></tr>
<tr><td>Level order</td><td>row by row with a queue</td><td>1 2 3 4 5 6</td><td>shortest number of steps, printing by level</td></tr>
</table></div>
<div class="viz" data-viz="trav"></div>
<div class="c3" data-k="traversals" data-label="Preorder, inorder and postorder"></div>
<p>Level order cannot use recursion directly, because it jumps between branches. A <b>queue</b> keeps the nodes waiting in the order they were found, which is breadth first search on a tree.</p>
<div class="c3" data-k="level_order" data-label="Level order with a queue"></div>
<div class="tip">Every traversal takes O(n) time. Recursion uses O(h) memory for the call stack, where h is the height. Level order uses memory for the widest level.</div>
'''),
    dict(id='bst', emoji='🔍', title='Binary search trees', html='''
<p>A <b>binary search tree</b> (BST) adds one rule: everything in the left subtree of a node is smaller than the node, and everything in the right subtree is larger. That rule turns every node into a signpost. To find a value, compare and go left or right, throwing away a whole subtree at every step.</p>
<div class="viz" data-viz="bst"></div>
<div class="c3" data-k="bst_ops" data-label="Insert, search, sorted order, minimum and maximum"></div>
<div class="tw"><table class="jt"><tr><th>Operation</th><th>Balanced tree</th><th>Worst case (a chain)</th></tr>
<tr><td>search</td><td class="yes">O(log n)</td><td>O(n)</td></tr>
<tr><td>insert</td><td class="yes">O(log n)</td><td>O(n)</td></tr>
<tr><td>delete</td><td class="yes">O(log n)</td><td>O(n)</td></tr>
<tr><td>sorted listing</td><td class="yes">O(n)</td><td class="yes">O(n)</td></tr>
<tr><td>minimum or maximum</td><td class="yes">O(log n)</td><td>O(n)</td></tr>
</table></div>
<div class="exam">Inorder traversal of a BST always produces the values in sorted order. Exams love asking for it, and it is also the quickest way to check that a tree really is a BST.</div>
'''),
    dict(id='bst-delete', emoji='✂️', title='Deleting from a search tree', html='''
<p>Deleting is the only tricky BST operation, because the tree must keep its ordering rule. First find the node, then handle one of three cases.</p>
<div class="grid2">
<div class="box"><h4>🍃 A leaf</h4><p>Just remove it. Its parent now points to nothing.</p></div>
<div class="box"><h4>☝️ One child</h4><p>Lift the child into the node's place. Everything in that subtree is still on the correct side of the parent.</p></div>
</div>
<div class="box"><h4>✌️ Two children</h4><p>Find the <b>inorder successor</b>: the smallest value in the right subtree, found by going right once and then left as far as possible. Copy that value into the node, then delete the successor from the right subtree. The successor has no left child, so that second delete is always one of the easy cases.</p></div>
<div class="c3" data-k="bst_delete" data-label="Deleting a node with two children, a leaf and one child"></div>
<div class="tip">The inorder predecessor (the largest value in the left subtree) works just as well. Both are the closest values to the one being removed, so the order is kept.</div>
'''),
    dict(id='balance', emoji='⚖️', title='Balance: why shape matters', html='''
<p>A BST is only fast when it is <b>short</b>. Insert values that are already sorted and every new node becomes a right child, so the tree turns into a chain that is no better than a linked list.</p>
<div class="viz" data-viz="shape"></div>
<p>The shortest possible binary tree with n nodes has this height:</p>
<span class="eq">h = ⌈log₂(n + 1)⌉</span>
<p>For a million nodes that is only 20 levels, so a search needs at most 20 comparisons. A chain of a million nodes might need a million.</p>
<div class="c3" data-k="build_balanced" data-label="A chain versus a tree built from the middle"></div>
<div class="tw"><table class="jt"><tr><th>Self balancing tree</th><th>Idea</th><th>Used in</th></tr>
<tr><td>AVL tree</td><td>heights of the two subtrees differ by at most 1, fixed with rotations</td><td>lookup heavy in memory indexes</td></tr>
<tr><td>Red black tree</td><td>colour rules keep the longest path at most twice the shortest</td><td>Java <code>TreeMap</code>, C++ <code>std::map</code></td></tr>
<tr><td>B tree</td><td>many keys per node, all leaves on one level</td><td>databases and file systems</td></tr>
</table></div>
<div class="warn">Python and JavaScript have no built in balanced search tree. For sorted keys in Python, the <code>bisect</code> module on a sorted list or the third party <code>sortedcontainers</code> package is the usual answer.</div>
'''),
    dict(id='heap', emoji='⛰️', title='Heaps: trees inside arrays', html='''
<p>A <b>binary heap</b> is a complete binary tree: every level is full except possibly the last, which fills from the left. In a <b>min heap</b> every parent is smaller than or equal to its children, so the smallest value is always at the root.</p>
<p>Because the tree is complete, it fits in a plain array with no references at all. The node at index i finds its family with arithmetic:</p>
<span class="eq">left = 2i + 1 &nbsp; right = 2i + 2 &nbsp; parent = ⌊(i − 1) / 2⌋</span>
<div class="viz" data-viz="heap"></div>
<div class="c3" data-k="heap_array" data-label="Push and pop on a min heap"></div>
<div class="tw"><table class="jt"><tr><th></th><th>Heap</th><th>Binary search tree</th></tr>
<tr><td>Smallest value</td><td class="yes">O(1) peek</td><td>O(log n)</td></tr>
<tr><td>Insert</td><td class="yes">O(log n)</td><td>O(log n) when balanced</td></tr>
<tr><td>Search any value</td><td>O(n)</td><td class="yes">O(log n) when balanced</td></tr>
<tr><td>Storage</td><td class="yes">one array</td><td>nodes and references</td></tr>
</table></div>
<div class="tip">Python has <code>heapq</code>, Java has <code>PriorityQueue</code>. Heaps power priority queues, heap sort, Dijkstra's shortest paths and finding the top k items.</div>
'''),
    dict(id='trie', emoji='🔤', title='Tries: trees of letters', html='''
<p>A <b>trie</b> (also called a prefix tree) stores words letter by letter. Each edge is one letter, and words that share a beginning share the same path. A flag on a node marks where a complete word ends.</p>
<div class="c3" data-k="trie" data-label="Insert, search and list words by prefix"></div>
<div class="grid2">
<div class="box"><h4>⚡ Speed</h4><p>Searching a word of length L takes O(L) steps, whether the trie holds ten words or ten million.</p></div>
<div class="box"><h4>⌨️ Autocomplete</h4><p>Walk down the typed prefix, then collect every word below that node. Phone keyboards and search boxes do exactly this.</p></div>
</div>
<div class="rule">Choose a trie when the questions are about prefixes. Choose a hash set when you only ever ask whether a whole word exists.</div>
'''),
]

INFO = {
    'title': 'Roots, branches and leaves',
    'panels': [
        {'s': [['e', '🌳'], ['t', 'root → children → leaves', {'b': 1}]], 'h': 'Tree', 't': 'One root, and every other node has one parent.', 'more': 'Folders, web pages and family trees all branch this way.'},
        {'s': [['e', '🔍'], ['c', [3, 8, 10], {'hl': {1: 'hl'}, 'p': {1: 'root'}}]], 'h': 'Search tree', 't': 'Smaller on the left, larger on the right.', 'more': 'Each comparison throws away a whole side, so a balanced tree answers in O(log n).'},
        {'s': [['e', '⛰️'], ['c', [1, 3, 2, 5], {'hl': {0: 'ok'}, 'p': {0: 'min'}}]], 'h': 'Heap', 't': 'The smallest value sits at the top.', 'more': 'A complete tree stored in an array, perfect for priority queues.'},
        {'s': [['e', '🔤'], ['t', 'c → a → r → t', {'b': 1}]], 'h': 'Trie', 't': 'Words share their beginnings.', 'more': 'Autocomplete walks the typed prefix and lists everything below it.'},
    ],
    'remember': 'Trees are recursive: solve the left subtree, solve the right subtree, combine. Keep search trees short, because every operation costs the height.',
}

REAL = [
    ['📁', 'Folders on your computer', 'Every folder holds files and more folders. Finding the size of a folder is a postorder traversal: add up the children first, then the folder itself.'],
    ['🌐', 'Every web page', 'The browser turns HTML into a tree called the DOM. Each tag is a node, and the nested tags inside it are its children.'],
    ['⌨️', 'Phone keyboard suggestions', 'Typing "ca" walks down a trie of words and offers car, cat and care from the branch below.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome',
     'en': 'Welcome to trees. A tree starts at a single root and branches out into children, all the way down to the leaves. You will walk trees in four orders, build fast search trees, see why balance matters, and meet heaps and tries.',
     'hi': 'Trees में आपका स्वागत है। Tree एक root से शुरू होता है और children में बँटता हुआ नीचे leaves तक जाता है। आप trees को चार क्रमों में घूमेंगे, तेज़ search trees बनाएँगे, देखेंगे कि balance क्यों ज़रूरी है, और heaps और tries से मिलेंगे।',
     'kn': 'Trees ಗೆ ಸ್ವಾಗತ. Tree ಒಂದೇ root ನಿಂದ ಆರಂಭವಾಗಿ children ಆಗಿ ಕವಲೊಡೆದು ಕೆಳಗೆ leaves ವರೆಗೆ ಹೋಗುತ್ತದೆ. ನೀವು trees ಅನ್ನು ನಾಲ್ಕು ಕ್ರಮಗಳಲ್ಲಿ ಸುತ್ತುತ್ತೀರಿ, ವೇಗದ search trees ನಿರ್ಮಿಸುತ್ತೀರಿ, balance ಏಕೆ ಮುಖ್ಯ ಎಂದು ನೋಡುತ್ತೀರಿ, ಮತ್ತು heaps ಹಾಗೂ tries ಅನ್ನು ಭೇಟಿಯಾಗುತ್ತೀರಿ.',
     'or': 'Trees କୁ ସ୍ୱାଗତ। Tree ଗୋଟିଏ root ରୁ ଆରମ୍ଭ ହୋଇ children ରେ ବିଭକ୍ତ ହୋଇ ତଳେ leaves ପର୍ଯ୍ୟନ୍ତ ଯାଏ। ଆପଣ trees କୁ ଚାରି କ୍ରମରେ ବୁଲିବେ, ଦ୍ରୁତ search trees ତିଆରି କରିବେ, balance କାହିଁକି ଜରୁରୀ ଦେଖିବେ, ଏବଂ heaps ଓ tries ସହ ପରିଚିତ ହେବେ।',
     'ar': 'مرحبًا بك في الأشجار. تبدأ الشجرة من جذر واحد وتتفرع إلى أبناء حتى تصل إلى الأوراق. ستتجول في الأشجار بأربعة ترتيبات، وتبني أشجار بحث سريعة، وترى لماذا يهم التوازن، وتتعرف على الكومات وأشجار البادئات.',
     'de': 'Willkommen bei Bäumen. Ein Baum beginnt bei einer einzigen Wurzel und verzweigt sich in Kinder bis hinunter zu den Blättern. Du durchläufst Bäume in vier Reihenfolgen, baust schnelle Suchbäume, siehst, warum Balance wichtig ist, und lernst Heaps und Tries kennen.'},
    {'id': 'what-is', 'h': 'What a tree is',
     'en': 'The root is the only node with no parent. Nodes with no children are leaves. In a binary tree every node has at most a left and a right child. Most tree code is recursive: solve the left side, solve the right side, and combine.',
     'hi': 'Root अकेला node है जिसका कोई parent नहीं होता। जिन nodes के children नहीं होते वे leaves हैं। Binary tree में हर node के ज़्यादा से ज़्यादा एक left और एक right child होता है। ज़्यादातर tree code recursive होता है: left हल करो, right हल करो, फिर जोड़ो।',
     'kn': 'Root ಗೆ ಮಾತ್ರ parent ಇರುವುದಿಲ್ಲ. Children ಇಲ್ಲದ nodes ಗಳು leaves. Binary tree ನಲ್ಲಿ ಪ್ರತಿ node ಗೆ ಹೆಚ್ಚೆಂದರೆ ಒಂದು left ಮತ್ತು ಒಂದು right child ಇರುತ್ತದೆ. ಹೆಚ್ಚಿನ tree code recursive: left ಪರಿಹರಿಸಿ, right ಪರಿಹರಿಸಿ, ನಂತರ ಸೇರಿಸಿ.',
     'or': 'Root ହିଁ ଏକମାତ୍ର node ଯାହାର parent ନାହିଁ। ଯେଉଁ nodes ର children ନାହିଁ ସେଗୁଡ଼ିକ leaves। Binary tree ରେ ପ୍ରତ୍ୟେକ node ର ଅଧିକରୁ ଅଧିକ ଗୋଟିଏ left ଓ ଗୋଟିଏ right child ଥାଏ। ଅଧିକାଂଶ tree code recursive: left ସମାଧାନ, right ସମାଧାନ, ତା’ପରେ ଯୋଡ଼ନ୍ତୁ।',
     'ar': 'الجذر هو العقدة الوحيدة التي ليس لها أب. والعقد التي ليس لها أبناء هي الأوراق. في الشجرة الثنائية لكل عقدة ابن أيسر وابن أيمن على الأكثر. ومعظم شيفرات الأشجار تعاودية: حل الجهة اليسرى، ثم اليمنى، ثم اجمع النتيجتين.',
     'de': 'Die Wurzel ist der einzige Knoten ohne Elternknoten. Knoten ohne Kinder sind Blätter. In einem Binärbaum hat jeder Knoten höchstens ein linkes und ein rechtes Kind. Der meiste Baumcode ist rekursiv: links lösen, rechts lösen, dann kombinieren.'},
    {'id': 'traversals', 'h': 'Traversals',
     'en': 'Preorder visits a node before its children, inorder between them, and postorder after them. Level order goes row by row and needs a queue. Every traversal visits each node once, so it takes linear time.',
     'hi': 'Preorder node को उसके children से पहले देखता है, inorder बीच में, और postorder बाद में। Level order पंक्ति दर पंक्ति चलता है और उसे queue चाहिए। हर traversal हर node को एक बार देखता है, इसलिए समय linear है।',
     'kn': 'Preorder node ಅನ್ನು ಅದರ children ಗಿಂತ ಮೊದಲು, inorder ನಡುವೆ, postorder ನಂತರ ಭೇಟಿ ಮಾಡುತ್ತದೆ. Level order ಸಾಲು ಸಾಲಾಗಿ ಹೋಗುತ್ತದೆ ಮತ್ತು queue ಬೇಕು. ಪ್ರತಿ traversal ಪ್ರತಿ node ಅನ್ನು ಒಮ್ಮೆ ಭೇಟಿ ಮಾಡುತ್ತದೆ, ಆದ್ದರಿಂದ linear ಸಮಯ.',
     'or': 'Preorder node କୁ ତା’ର children ପୂର୍ବରୁ ଦେଖେ, inorder ମଝିରେ, postorder ପରେ। Level order ଧାଡ଼ି ଧାଡ଼ି ଚାଲେ ଓ queue ଦରକାର। ପ୍ରତ୍ୟେକ traversal ପ୍ରତ୍ୟେକ node କୁ ଥରେ ଦେଖେ, ତେଣୁ ସମୟ linear।',
     'ar': 'الترتيب القبلي يزور العقدة قبل أبنائها، والترتيب الوسطي بينهما، والترتيب البعدي بعدهما. والترتيب حسب المستوى يسير صفًا صفًا ويحتاج طابورًا. كل طريقة تزور كل عقدة مرة واحدة، فالزمن خطي.',
     'de': 'Preorder besucht einen Knoten vor seinen Kindern, Inorder dazwischen und Postorder danach. Level Order geht Zeile für Zeile und braucht eine Warteschlange. Jeder Durchlauf besucht jeden Knoten einmal, also lineare Zeit.'},
    {'id': 'bst', 'h': 'Binary search trees',
     'en': 'In a binary search tree, smaller values live on the left and larger values on the right. Each comparison throws away one whole side, so searching and inserting cost as much as the height of the tree. Inorder traversal gives the values in sorted order.',
     'hi': 'Binary search tree में छोटे values left में और बड़े values right में रहते हैं। हर तुलना एक पूरी तरफ़ हटा देती है, इसलिए search और insert की लागत tree की height जितनी है। Inorder traversal values को sorted क्रम में देता है।',
     'kn': 'Binary search tree ನಲ್ಲಿ ಸಣ್ಣ values left ನಲ್ಲಿ ಮತ್ತು ದೊಡ್ಡ values right ನಲ್ಲಿ ಇರುತ್ತವೆ. ಪ್ರತಿ ಹೋಲಿಕೆ ಒಂದು ಪೂರ್ಣ ಭಾಗವನ್ನು ಬಿಡುತ್ತದೆ, ಆದ್ದರಿಂದ search ಮತ್ತು insert tree ನ height ನಷ್ಟು ವೆಚ್ಚ. Inorder traversal values ಅನ್ನು sorted ಕ್ರಮದಲ್ಲಿ ಕೊಡುತ್ತದೆ.',
     'or': 'Binary search tree ରେ ଛୋଟ values left ରେ ଓ ବଡ଼ values right ରେ ରହନ୍ତି। ପ୍ରତ୍ୟେକ ତୁଳନା ଗୋଟିଏ ପୂରା ପାର୍ଶ୍ୱ ବାଦ ଦିଏ, ତେଣୁ search ଓ insert ର ଖର୍ଚ୍ଚ tree ର height ସହ ସମାନ। Inorder traversal values କୁ sorted କ୍ରମରେ ଦିଏ।',
     'ar': 'في شجرة البحث الثنائية تكون القيم الأصغر في اليسار والأكبر في اليمين. كل مقارنة تستبعد جهة كاملة، لذلك تكلف عمليتا البحث والإدراج بقدر ارتفاع الشجرة. والترتيب الوسطي يعطي القيم مرتبة.',
     'de': 'In einem binären Suchbaum liegen kleinere Werte links und größere rechts. Jeder Vergleich verwirft eine ganze Seite, also kosten Suchen und Einfügen so viel wie die Höhe des Baums. Inorder liefert die Werte sortiert.'},
    {'id': 'bst-delete', 'h': 'Deleting',
     'en': 'To delete a leaf, just remove it. To delete a node with one child, lift the child into its place. For two children, copy in the smallest value from the right subtree, then delete that value from the right subtree instead.',
     'hi': 'Leaf हटाने के लिए उसे बस निकाल दें। एक child वाले node को हटाने के लिए child को उसकी जगह ले आएँ। दो children हों तो right subtree का सबसे छोटा value कॉपी करें, फिर उस value को right subtree से हटाएँ।',
     'kn': 'Leaf ಅಳಿಸಲು ಅದನ್ನು ತೆಗೆದುಹಾಕಿ. ಒಂದು child ಇರುವ node ಅಳಿಸಲು child ಅನ್ನು ಅದರ ಸ್ಥಾನಕ್ಕೆ ತನ್ನಿ. ಎರಡು children ಇದ್ದರೆ right subtree ನ ಅತಿ ಸಣ್ಣ value ನಕಲಿಸಿ, ನಂತರ ಆ value ಅನ್ನು right subtree ನಿಂದ ಅಳಿಸಿ.',
     'or': 'Leaf ହଟାଇବାକୁ କେବଳ ତାକୁ କାଢ଼ନ୍ତୁ। ଗୋଟିଏ child ଥିବା node ହଟାଇବାକୁ child କୁ ତା’ ସ୍ଥାନକୁ ଆଣନ୍ତୁ। ଦୁଇଟି children ଥିଲେ right subtree ର ସବୁଠୁ ଛୋଟ value କପି କରନ୍ତୁ, ତା’ପରେ ସେହି value କୁ right subtree ରୁ ହଟାନ୍ତୁ।',
     'ar': 'لحذف ورقة يكفي إزالتها. ولحذف عقدة لها ابن واحد ارفع الابن إلى مكانها. وإذا كان لها ابنان فانسخ أصغر قيمة من الشجرة الفرعية اليمنى، ثم احذف تلك القيمة من الشجرة الفرعية اليمنى.',
     'de': 'Ein Blatt wird einfach entfernt. Bei einem Knoten mit einem Kind rückt das Kind an seine Stelle. Bei zwei Kindern kopiert man den kleinsten Wert des rechten Teilbaums hinein und löscht diesen Wert dann im rechten Teilbaum.'},
    {'id': 'balance', 'h': 'Balance',
     'en': 'A search tree is only fast when it is short. Sorted input turns it into a chain as slow as a linked list. A balanced tree with n nodes needs only about log base two of n levels, so a million values fit in twenty levels.',
     'hi': 'Search tree तभी तेज़ है जब वह छोटा हो। Sorted input उसे linked list जैसी धीमी chain बना देता है। n nodes वाले balanced tree को लगभग log base two of n levels चाहिए, इसलिए दस लाख values बीस levels में आ जाते हैं।',
     'kn': 'Search tree ಚಿಕ್ಕದಾಗಿದ್ದಾಗ ಮಾತ್ರ ವೇಗ. Sorted input ಅದನ್ನು linked list ನಷ್ಟು ನಿಧಾನದ chain ಆಗಿಸುತ್ತದೆ. n nodes ಇರುವ balanced tree ಗೆ ಸುಮಾರು log base two of n levels ಸಾಕು, ಆದ್ದರಿಂದ ಹತ್ತು ಲಕ್ಷ values ಇಪ್ಪತ್ತು levels ನಲ್ಲಿ ಹಿಡಿಸುತ್ತವೆ.',
     'or': 'Search tree କେବଳ ଛୋଟ ଥିଲେ ଦ୍ରୁତ। Sorted input ଏହାକୁ linked list ପରି ଧୀର chain କରିଦିଏ। n nodes ଥିବା balanced tree କୁ ପ୍ରାୟ log base two of n levels ଦରକାର, ତେଣୁ ଦଶ ଲକ୍ଷ values କୋଡ଼ିଏ levels ରେ ରହିଯାଏ।',
     'ar': 'شجرة البحث سريعة فقط عندما تكون قصيرة. المدخلات المرتبة تحولها إلى سلسلة بطيئة كالقائمة المترابطة. والشجرة المتوازنة ذات n عقدة تحتاج نحو لوغاريتم n للأساس اثنين من المستويات، فمليون قيمة تكفيها عشرون مستوى.',
     'de': 'Ein Suchbaum ist nur schnell, wenn er niedrig ist. Sortierte Eingaben machen ihn zu einer Kette, so langsam wie eine verkettete Liste. Ein balancierter Baum mit n Knoten braucht nur etwa Logarithmus zur Basis zwei von n Ebenen, also passen eine Million Werte in zwanzig Ebenen.'},
    {'id': 'heap', 'h': 'Heaps',
     'en': 'A min heap keeps the smallest value at the root. It is a complete tree, so it lives in an array where the children of index i sit at two i plus one and two i plus two. Push bubbles up and pop sinks down, both in logarithmic time.',
     'hi': 'Min heap सबसे छोटे value को root पर रखता है। यह complete tree है, इसलिए array में रहता है जहाँ index i के children two i plus one और two i plus two पर होते हैं। Push ऊपर चढ़ाता है और pop नीचे उतारता है, दोनों logarithmic समय में।',
     'kn': 'Min heap ಅತಿ ಸಣ್ಣ value ಅನ್ನು root ನಲ್ಲಿ ಇಡುತ್ತದೆ. ಇದು complete tree, ಆದ್ದರಿಂದ array ನಲ್ಲಿ ಇರುತ್ತದೆ, index i ಯ children two i plus one ಮತ್ತು two i plus two ನಲ್ಲಿ. Push ಮೇಲೆ ಏರಿಸುತ್ತದೆ, pop ಕೆಳಗೆ ಇಳಿಸುತ್ತದೆ, ಎರಡೂ logarithmic ಸಮಯದಲ್ಲಿ.',
     'or': 'Min heap ସବୁଠୁ ଛୋଟ value କୁ root ରେ ରଖେ। ଏହା complete tree, ତେଣୁ array ରେ ରହେ ଯେଉଁଠି index i ର children two i plus one ଓ two i plus two ରେ ଥାନ୍ତି। Push ଉପରକୁ ଉଠାଏ ଓ pop ତଳକୁ ନିଏ, ଦୁହେଁ logarithmic ସମୟରେ।',
     'ar': 'الكومة الصغرى تبقي أصغر قيمة في الجذر. وهي شجرة كاملة، لذلك تعيش في مصفوفة يكون فيها ابنا الموضع i عند اثنين i زائد واحد واثنين i زائد اثنين. الإضافة تصعد بالقيمة والسحب يهبط بها، وكلاهما في زمن لوغاريتمي.',
     'de': 'Ein Min Heap hält den kleinsten Wert an der Wurzel. Er ist ein vollständiger Baum und lebt daher in einem Array, in dem die Kinder von Index i bei zwei i plus eins und zwei i plus zwei liegen. Push steigt auf, Pop sinkt ab, beides in logarithmischer Zeit.'},
    {'id': 'trie', 'h': 'Tries',
     'en': 'A trie stores words letter by letter, and words with the same beginning share a path. Looking up a word costs only its length, which makes tries ideal for autocomplete and prefix questions.',
     'hi': 'Trie शब्दों को अक्षर दर अक्षर रखता है, और एक जैसी शुरुआत वाले शब्द एक ही रास्ता साझा करते हैं। किसी शब्द को खोजने की लागत सिर्फ़ उसकी लंबाई है, इसलिए tries autocomplete और prefix सवालों के लिए आदर्श हैं।',
     'kn': 'Trie ಪದಗಳನ್ನು ಅಕ್ಷರ ಅಕ್ಷರವಾಗಿ ಇಡುತ್ತದೆ, ಒಂದೇ ಆರಂಭದ ಪದಗಳು ಒಂದೇ ದಾರಿಯನ್ನು ಹಂಚಿಕೊಳ್ಳುತ್ತವೆ. ಒಂದು ಪದ ಹುಡುಕಲು ಅದರ ಉದ್ದದಷ್ಟೇ ವೆಚ್ಚ, ಆದ್ದರಿಂದ tries autocomplete ಮತ್ತು prefix ಪ್ರಶ್ನೆಗಳಿಗೆ ಸೂಕ್ತ.',
     'or': 'Trie ଶବ୍ଦଗୁଡ଼ିକୁ ଅକ୍ଷର ଅକ୍ଷର ରଖେ, ଏବଂ ସମାନ ଆରମ୍ଭ ଥିବା ଶବ୍ଦ ଗୋଟିଏ ରାସ୍ତା ବାଣ୍ଟନ୍ତି। ଗୋଟିଏ ଶବ୍ଦ ଖୋଜିବାର ଖର୍ଚ୍ଚ କେବଳ ତା’ର ଲମ୍ବ, ତେଣୁ tries autocomplete ଓ prefix ପ୍ରଶ୍ନ ପାଇଁ ଉପଯୁକ୍ତ।',
     'ar': 'شجرة البادئات تخزن الكلمات حرفًا حرفًا، والكلمات ذات البداية نفسها تتشارك المسار نفسه. البحث عن كلمة يكلف طولها فقط، ولهذا تناسب الإكمال التلقائي وأسئلة البادئات.',
     'de': 'Ein Trie speichert Wörter Buchstabe für Buchstabe, und Wörter mit gleichem Anfang teilen sich einen Pfad. Ein Wort nachzuschlagen kostet nur seine Länge, deshalb eignen sich Tries ideal für Autovervollständigung und Präfixfragen.'},
    {'id': 'practice', 'h': 'Practice',
     'en': 'Time to practise. For each problem, ask what the answer for one node needs from its left and right subtrees. Once you know that, the recursion almost writes itself. Every solution runs in Python, JavaScript and Java.',
     'hi': 'अब अभ्यास का समय है। हर सवाल के लिए पूछें कि एक node के जवाब को उसके left और right subtrees से क्या चाहिए। यह जानते ही recursion लगभग अपने आप लिख जाता है। हर हल Python, JavaScript और Java में चलता है।',
     'kn': 'ಈಗ ಅಭ್ಯಾಸದ ಸಮಯ. ಪ್ರತಿ ಸಮಸ್ಯೆಗೆ ಒಂದು node ನ ಉತ್ತರಕ್ಕೆ ಅದರ left ಮತ್ತು right subtrees ನಿಂದ ಏನು ಬೇಕು ಎಂದು ಕೇಳಿ. ಅದು ತಿಳಿದ ನಂತರ recursion ಬಹುತೇಕ ತಾನೇ ಬರೆಯಲ್ಪಡುತ್ತದೆ. ಪ್ರತಿ ಪರಿಹಾರ Python, JavaScript ಮತ್ತು Java ದಲ್ಲಿ ಚಲಿಸುತ್ತದೆ.',
     'or': 'ଏବେ ଅଭ୍ୟାସର ସମୟ। ପ୍ରତ୍ୟେକ ସମସ୍ୟା ପାଇଁ ପଚାରନ୍ତୁ ଗୋଟିଏ node ର ଉତ୍ତର ପାଇଁ ତା’ର left ଓ right subtrees ରୁ କ’ଣ ଦରକାର। ଏହା ଜାଣିଲେ recursion ପ୍ରାୟ ନିଜେ ଲେଖାହୋଇଯାଏ। ପ୍ରତ୍ୟେକ ସମାଧାନ Python, JavaScript ଓ Java ରେ ଚାଲେ।',
     'ar': 'حان وقت التدريب. في كل مسألة اسأل ماذا تحتاج إجابة العقدة من شجرتيها الفرعيتين اليسرى واليمنى. عندما تعرف ذلك تكاد التعاودية تكتب نفسها. كل حل يعمل بلغات بايثون وجافاسكربت وجافا.',
     'de': 'Zeit zum Üben. Frag dich bei jeder Aufgabe, was die Antwort für einen Knoten von seinem linken und rechten Teilbaum braucht. Sobald du das weißt, schreibt sich die Rekursion fast von selbst. Jede Lösung läuft in Python, JavaScript und Java.'},
]

PRACTICE = [
    {'id': 'max-depth', 'lv': 'e', 'title': 'Maximum and minimum depth', 'code': 'p_max_depth',
     'statement': '<p>Return the number of levels on the longest path from the root down to a leaf, and on the shortest such path.</p>',
     'example': 'Input: [3, 9, 20, null, null, 15, 7]  →  max 3, min 2\nInput: [1, null, 2, null, 3]          →  max 3, min 3',
     'hint': 'The depth of a tree is one more than the depth of its deeper subtree. Careful with the minimum: a missing child is not a leaf.',
     'approach': '<p>Recurse. The maximum is 1 + max(left, right). For the minimum, if one side is empty you must follow the other side, because only a node with no children ends a path.</p>',
     'time': 'O(n)', 'space': 'O(h)'},
    {'id': 'invert', 'lv': 'e', 'title': 'Mirror a tree', 'code': 'p_invert',
     'statement': '<p>Turn a binary tree into its mirror image, so every left child becomes a right child and the other way round.</p>',
     'example': 'Level order before: 4 2 7 1 3 6 9\nLevel order after:  4 7 2 9 6 3 1',
     'hint': 'Mirroring a tree means mirroring both subtrees and then swapping them.',
     'approach': '<p>Recursively invert the left and right subtrees, then swap the two references. Each node is touched once.</p>',
     'time': 'O(n)', 'space': 'O(h)'},
    {'id': 'validate-bst', 'lv': 'm', 'title': 'Is it a valid search tree', 'code': 'p_validate',
     'statement': '<p>Decide whether a binary tree follows the search tree rule everywhere: every value in a left subtree is smaller than the node, and every value in a right subtree is larger.</p>',
     'example': '[5, 3, 8, 1, 4, 7, 9]  →  valid\n[5, 3, 8, 1, 6, 7, 9]  →  invalid   (6 is in the left subtree of 5)',
     'hint': 'Checking each parent against its own children is not enough. A node must respect every ancestor above it.',
     'approach': '<p>Pass down an allowed range. Going left, the node value becomes the new upper limit. Going right, it becomes the new lower limit. Any value outside its range breaks the rule.</p>',
     'time': 'O(n)', 'space': 'O(h)'},
    {'id': 'path-sum', 'lv': 'm', 'title': 'Root to leaf paths with a given sum', 'code': 'p_path_sum',
     'statement': '<p>List every path from the root to a leaf whose values add up to a target.</p>',
     'example': 'Tree: [5, 4, 8, 11, null, 13, 4, 7, 2, null, null, 5, 1], target 22\nOutput: 5 4 11 2   and   5 8 4 5',
     'hint': 'Carry the remaining target and the current path down the tree. Undo your step when you come back up.',
     'approach': '<p>Depth first search with backtracking. Push the node onto the path and subtract its value. At a leaf, record the path if the remainder is zero. Pop the node before returning so the path is correct for the next branch.</p>',
     'time': 'O(n · h)', 'space': 'O(h)'},
    {'id': 'lca', 'lv': 'h', 'title': 'Lowest common ancestor', 'code': 'p_lca',
     'statement': '<p>Given two values in a binary tree (not a search tree), find the deepest node that has both of them in its subtree. A node counts as its own ancestor.</p>',
     'example': 'Tree: [3, 5, 1, 6, 2, 0, 8, null, null, 7, 4]\nlca(5, 1) = 3   lca(5, 4) = 5   lca(7, 8) = 3',
     'hint': 'Ask each subtree whether it found p or q. The first node that hears "yes" from both sides is the answer.',
     'approach': '<p>Return the node itself if it is null, p or q. Otherwise search both subtrees. If both return something, p and q are split across this node, so it is the answer. If only one side returns something, pass it up.</p>',
     'time': 'O(n)', 'space': 'O(h)'},
    {'id': 'serialize', 'lv': 'h', 'title': 'Save a tree to text and load it back', 'code': 'p_serialize',
     'statement': '<p>Turn a binary tree into a string, then rebuild exactly the same tree from that string.</p>',
     'example': 'Tree: [1, 2, 3, null, null, 4, 5]\nText: 1,2,#,#,3,4,#,#,5,#,#',
     'hint': 'A preorder list alone is ambiguous. Writing a marker for every empty child keeps the shape.',
     'approach': '<p>Write a preorder traversal with # for each null. To rebuild, read tokens in the same order: a number creates a node whose left and right subtrees are read next, and # returns null.</p>',
     'time': 'O(n)', 'space': 'O(n)'},
    {'id': 'diameter', 'lv': 'x', 'title': 'Diameter of a tree', 'code': 'p_diameter',
     'statement': '<p>The diameter is the number of edges on the longest path between any two nodes. The path does not have to pass through the root.</p>',
     'example': '[1, 2, 3, 4, 5]                      →  3   (4 to 2 to 1 to 3)\n[1, 2, null, 4, 5, 6, null, null, 7]  →  4   (6 to 4 to 2 to 5 to 7)',
     'hint': 'Every path has a highest node where it bends. Through that node, its length is the left height plus the right height.',
     'approach': '<p>Compute heights with postorder recursion. At each node, left height + right height is the longest path that bends there. Keep the best value seen in a variable outside the recursion.</p>',
     'time': 'O(n)', 'space': 'O(h)'},
    {'id': 'max-path-sum', 'lv': 'x', 'title': 'Maximum path sum', 'code': 'p_max_path',
     'statement': '<p>Values can be negative. Find the largest sum of values along any path between two nodes. The path needs at least one node.</p>',
     'example': '[-10, 9, 20, null, null, 15, 7]  →  42   (15 + 20 + 7)\n[2, -1]  →  2\n[-3]     →  -3',
     'hint': 'A node can join both of its branches for its own answer, but it can pass only one branch up to its parent.',
     'approach': '<p>Let gain(node) be the best downward path starting at the node. Ignore a branch with negative gain by using max(0, gain). The best path bending at the node is value + left + right, and the node reports value + max(left, right) upward.</p>',
     'time': 'O(n)', 'space': 'O(h)'},
]

QUIZ = [
    {'lv': 'e', 'q': 'A tree has 10 nodes. How many edges does it have?', 'o': ['9', '10', '11', '20'], 'a': 0, 'hint': 'Every node except the root hangs from one edge.', 'why': '<span class="eq">edges = n − 1 = 10 − 1 = 9</span>'},
    {'lv': 'e', 'q': 'What is a node with no children called?', 'o': ['Root', 'Leaf', 'Parent', 'Edge'], 'a': 1, 'hint': 'Think of the ends of the branches.', 'why': 'Leaves are the nodes at the bottom with nothing below them.'},
    {'lv': 'e', 'q': 'How many children can a node in a binary tree have at most?', 'o': ['1', '2', '3', 'Any number'], 'a': 1, 'hint': 'Binary means two.', 'why': 'A binary tree node has at most a left child and a right child.'},
    {'lv': 'e', 'q': 'Which traversal of a binary search tree prints the values in sorted order?', 'o': ['Preorder', 'Inorder', 'Postorder', 'Level order'], 'a': 1, 'hint': 'Smaller values are on the left.', 'why': 'Inorder prints the left subtree (smaller), then the node, then the right subtree (larger).'},
    {'lv': 'm', 'q': 'What is the preorder of the tree 1 with children 2 and 3, where 2 has children 4 and 5?', 'o': ['4 2 5 1 3', '1 2 4 5 3', '4 5 2 3 1', '1 2 3 4 5'], 'a': 1, 'hint': 'Node first, then left, then right.', 'why': 'Visit 1, go left to 2, then 4 and 5, then back up and right to 3.'},
    {'lv': 'm', 'q': 'Which structure does level order traversal use?', 'o': ['Stack', 'Queue', 'Hash map', 'Heap'], 'a': 1, 'hint': 'Nodes found first are visited first.', 'why': 'A queue keeps the nodes of one level ahead of the next level, first in, first out.'},
    {'lv': 'm', 'q': 'About how many comparisons does a search need in a balanced BST of one million values?', 'o': ['About 20', 'About 1,000', 'About 500,000', 'About 1,000,000'], 'a': 0, 'hint': 'Each comparison halves what is left.', 'why': '<span class="eq">2²⁰ = 1,048,576 ≥ 1,000,000</span> So about 20 levels are enough.'},
    {'lv': 'm', 'q': 'In a heap stored in an array, what is the parent index of index 9?', 'o': ['3', '4', '5', '8'], 'a': 1, 'hint': 'parent = ⌊(i − 1) / 2⌋', 'why': '<span class="eq">⌊(9 − 1) / 2⌋ = 4</span>'},
    {'lv': 'h', 'q': 'You insert 1, 2, 3, 4, 5 in that order into a plain BST. How many levels does it have?', 'o': ['3', '4', '5', '2'], 'a': 2, 'hint': 'Each new value is the largest so far.', 'why': 'Every value becomes the right child of the previous one, so the tree is a chain of 5 levels.'},
    {'lv': 'h', 'q': 'Deleting a BST node with two children, which value usually replaces it?', 'o': ['Its left child', 'The root', 'The smallest value in its right subtree', 'The largest value in the whole tree'], 'a': 2, 'hint': 'You need the closest larger value.', 'why': 'The inorder successor is larger than everything on the left and smaller than everything else on the right, so the order is kept.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'def h(n):\n    return 0 if n is None else 1 + max(h(n.left), h(n.right))\n\nprint(h(Node(1, Node(2, Node(3)), None)))', 'o': ['1', '2', '3', '0'], 'a': 2, 'hint': 'Count the levels: 1, then 2, then 3.', 'why': 'The nodes form a chain going left, three levels deep.'},
    {'lv': 'h', 'q': 'Why does checking only each node against its own children fail to validate a BST?', 'o': ['It is too slow', 'A deeper node can break the rule with a higher ancestor', 'It misses leaves', 'It only works for heaps'], 'a': 1, 'hint': 'Try 5 with left child 3, and 3 with right child 6.', 'why': '6 is fine for its parent 3 but sits in the left subtree of 5, which breaks the rule.'},
    {'lv': 'x', 'q': 'What is the largest number of nodes in a binary tree with h levels?', 'o': ['2h', 'h²', '2ʰ − 1', '2ʰ⁺¹'], 'a': 2, 'hint': 'Add up 1 + 2 + 4 + … for h levels.', 'why': '<span class="eq">1 + 2 + 4 + … + 2ʰ⁻¹ = 2ʰ − 1</span>'},
    {'lv': 'x', 'q': 'How long does building a heap from n unsorted values take when you sink nodes from the bottom up?', 'o': ['O(n)', 'O(n log n)', 'O(log n)', 'O(n²)'], 'a': 0, 'hint': 'Most nodes are near the bottom and barely move.', 'why': 'Half the nodes are leaves and move 0 steps, a quarter move at most 1, and so on. The total adds up to O(n).'},
    {'lv': 'x', 'q': 'A trie holds a million words. How long does looking up one word of length L take?', 'o': ['O(1)', 'O(L)', 'O(log n)', 'O(n)'], 'a': 1, 'hint': 'You follow one edge per letter.', 'why': 'The number of stored words does not matter. Only the letters of the word you look up do.'},
    {'lv': 'x', 'q': 'An expression tree holds operators in the inner nodes and numbers in the leaves. Which traversal produces postfix notation?', 'o': ['Preorder', 'Inorder', 'Postorder', 'Level order'], 'a': 2, 'hint': 'In postfix, operators come after their operands.', 'why': 'Postorder writes both subtrees (the operands) before the node (the operator).'},
]

CALC = [
    {'lv': 'e', 'q': 'A tree has 12 nodes. How many edges does it have?', 'ans': '11', 'hint': 'edges = n − 1', 'steps': ['<span class="eq">12 − 1 = 11</span>']},
    {'lv': 'e', 'q': 'A perfect binary tree has 4 full levels. How many nodes does it have?', 'ans': '15', 'hint': 'Add the nodes on each level.', 'steps': ['<span class="eq">1 + 2 + 4 + 8 = 15</span>', 'which matches <span class="eq">2⁴ − 1 = 15</span>']},
    {'lv': 'm', 'q': 'In a heap stored in an array, what is the index of the left child of index 5?', 'ans': '11', 'hint': 'left = 2i + 1', 'steps': ['<span class="eq">2 × 5 + 1 = 11</span>']},
    {'lv': 'm', 'q': 'What is the smallest possible number of levels for a binary tree with 100 nodes?', 'ans': '7', 'hint': 'h = ⌈log₂(n + 1)⌉', 'steps': ['<span class="eq">2⁶ − 1 = 63 &lt; 100 ≤ 127 = 2⁷ − 1</span>', 'So at least 7 levels are needed.']},
    {'lv': 'h', 'q': 'A perfect binary tree has 31 nodes. How many of them are leaves?', 'ans': '16', 'hint': 'The last level holds just over half of all nodes.', 'steps': ['31 nodes means 5 levels, since <span class="eq">2⁵ − 1 = 31</span>', 'The last level holds <span class="eq">2⁴ = 16</span> nodes.']},
    {'lv': 'h', 'q': 'Insert 8, 3, 10, 1, 6, 14, 4, 7, 13 into an empty BST. How many nodes are compared when searching for 13?', 'ans': '4', 'hint': 'Follow the path from the root.', 'steps': ['13 &gt; 8, go right to 10', '13 &gt; 10, go right to 14', '13 &lt; 14, go left to 13, found', 'Nodes compared: 8, 10, 14, 13, so <span class="eq">4</span>']},
    {'lv': 'x', 'q': 'How many differently shaped binary search trees can hold the values 1, 2 and 3?', 'ans': '5', 'hint': 'Try each value as the root and count the shapes of each side.', 'steps': ['Root 1: the right side holds 2 and 3 in 2 shapes.', 'Root 2: 1 on the left and 3 on the right, 1 shape.', 'Root 3: the left side holds 1 and 2 in 2 shapes.', '<span class="eq">2 + 1 + 2 = 5</span>, the third Catalan number.']},
    {'lv': 'x', 'q': 'Insert car, cart, care, cat and dog into an empty trie. How many nodes are there, not counting the root?', 'ans': '9', 'hint': 'Shared beginnings share nodes.', 'steps': ['c, a, r are shared by car, cart and care: 3 nodes', 't for cart and e for care: 2 more', 't for cat (under c, a): 1 more', 'd, o, g for dog: 3 more', '<span class="eq">3 + 2 + 1 + 3 = 9</span>']},
]

VIZ_JS = r'''
(() => {
  const { esc, $, shell, seg, wireSeg, Player, Seq, cell } = VIZ.kit;
  const W = VIZ.widgets;
  const rand = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
  const N = (v, l = null, r = null) => ({ v, l, r });
  const plates = (a, hl = {}) => `<div class="vz-stack">${a.map((v, k) => `<div class="vz-plate ${hl[k] || ''}">${esc(v)}${k === a.length - 1 ? '<small>top</small>' : ''}</div>`).join('')}</div>`;

  /* lay a tree out: x by inorder position, y by depth */
  function layout(root) {
    const pos = new Map();
    let x = 0, depth = 0;
    const walk = (n, d) => { if (!n) return; walk(n.l, d + 1); pos.set(n, { x: x++, d }); depth = Math.max(depth, d); walk(n.r, d + 1); };
    walk(root, 0);
    return { pos, cols: x, depth };
  }

  /* draw a tree as SVG. cls(n) is the class of a node, edge(n) the class of the edge into n */
  function svgTree(root, cls = () => '', edge = () => '', opt = {}) {
    if (!root) return '<div class="vz-note">The tree is empty.</div>';
    const L = opt.layout || layout(root);
    const dx = 48, dy = 62, r = 18, pad = 26, padB = opt.sub ? 40 : 26;
    const Wd = Math.max(2 * pad + (L.cols - 1) * dx, 140), Ht = pad + padB + L.depth * dy;
    const P = n => { const p = L.pos.get(n); return [pad + p.x * dx + (Wd - 2 * pad - (L.cols - 1) * dx) / 2, pad + p.d * dy]; };
    let es = '', ns = '';
    const walk = n => {
      if (!n) return;
      const [x, y] = P(n);
      for (const c of [n.l, n.r]) {
        if (c && L.pos.has(c)) { const [cx, cy] = P(c); es += `<line class="vz-edge ${edge(c)}" x1="${x}" y1="${y}" x2="${cx}" y2="${cy}"/>`; }
      }
      ns += `<g class="vz-tn ${cls(n)}"><circle cx="${x}" cy="${y}" r="${r}"/><text x="${x}" y="${y + 5}">${esc(n.v)}</text>${opt.sub ? `<text class="vz-ret" x="${x}" y="${y + r + 15}">${esc(opt.sub(n))}</text>` : ''}</g>`;
      walk(n.l); walk(n.r);
    };
    walk(root);
    return `<div class="vz-scroll"><svg class="vz-svg" viewBox="0 0 ${Wd} ${Ht}" style="max-width:${Wd}px; margin:0 auto" role="img" aria-label="Tree diagram">${es}${ns}</svg></div>`;
  }

  /* ======================= traversal orders ======================= */
  W.trav = el => {
    const b = shell(el, 'Four ways to walk the same tree', 'Pick an order and press Play. Yellow is the node being handled now, green nodes are already visited, blue nodes are waiting.');
    b.innerHTML = `<div class="vz-row">${seg('o', [['pre', 'Preorder'], ['in', 'Inorder'], ['post', 'Postorder'], ['level', 'Level order']], 'pre')}</div>
      <div class="vz-two"><div><h4 class="vz-auxh">Call stack</h4><div class="vz-aux"></div></div><div><h4>Tree</h4><div class="vz-tree"></div></div></div>
      <h4>Visit order</h4><div class="vz-scroll"><div class="vz-cells vz-big vz-out"></div></div>
      <div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const T = N(1, N(2, N(4), N(5)), N(3, null, N(6)));
    const L = layout(T);
    const NAME = { pre: 'Preorder', in: 'Inorder', post: 'Postorder', level: 'Level order' };
    let steps = [], order = 'pre';
    const P = Player($('.vz-p', b), show, 900);
    function build() {
      steps = [];
      const done = [];
      if (order === 'level') {
        const q = [T];
        steps.push({ cur: null, done: [], wait: q.slice(), msg: 'Put the root in the queue.' });
        while (q.length) {
          const n = q.shift();
          done.push(n);
          const kids = [n.l, n.r].filter(Boolean);
          q.push(...kids);
          steps.push({ cur: n, done: done.slice(), wait: q.slice(), msg: `Take ${n.v} from the front of the queue and visit it.${kids.length ? ` Its children ${kids.map(k => k.v).join(' and ')} join the back.` : ' It has no children to add.'}` });
        }
      } else {
        const go = (n, path) => {
          if (!n) return;
          const p = path.concat(n);
          const visit = msg => { done.push(n); steps.push({ cur: n, done: done.slice(), wait: p.slice(), visit: 1, msg }); };
          if (order === 'pre') visit(`Arrive at ${n.v} and visit it at once, before its children.`);
          else steps.push({ cur: n, done: done.slice(), wait: p.slice(), msg: `Arrive at ${n.v}. ${order === 'in' ? 'Its left subtree comes first.' : 'Both subtrees come first.'}` });
          go(n.l, p);
          if (order === 'in') visit(`The left side of ${n.v} is finished, so visit ${n.v}. Now go right.`);
          go(n.r, p);
          if (order === 'post') visit(`Both subtrees of ${n.v} are finished, so visit ${n.v} last.`);
        };
        steps.push({ cur: null, done: [], wait: [], msg: 'Start the recursion at the root.' });
        go(T, []);
      }
      const last = steps[steps.length - 1];
      steps.push({ cur: null, done: last.done, wait: [], msg: `Finished. ${NAME[order]}: <b>${last.done.map(n => n.v).join(' ')}</b>` });
      $('.vz-auxh', b).textContent = order === 'level' ? 'Queue (front on the left)' : 'Call stack';
      P.load(steps.length);
    }
    function show(k) {
      const s = steps[k];
      $('.vz-tree', b).innerHTML = svgTree(T, n => n === s.cur ? 'hl' : s.done.includes(n) ? 'ok' : s.wait.includes(n) ? 'mv' : '', n => order !== 'level' && s.wait.includes(n) ? 'on' : '', { layout: L });
      $('.vz-out', b).innerHTML = s.done.map((n, i) => cell(n.v, n === s.cur && (s.visit || order === 'level') ? 'hl' : 'ok', i + 1)).join('') || '<span class="vz-note">nothing visited yet</span>';
      $('.vz-aux', b).innerHTML = order === 'level'
        ? `<div class="vz-cells vz-big">${s.wait.map(n => cell(n.v, 'sel')).join('') || '<span class="vz-note">empty</span>'}</div>`
        : plates(s.wait.map(n => `visit(${n.v})`));
      $('.vz-msg', b).innerHTML = s.msg;
    }
    wireSeg(b, 'o', v => { order = v; build(); });
    build();
  };

  /* ======================= binary search tree playground ======================= */
  W.bst = el => {
    const b = shell(el, 'Build and search a binary search tree', 'Type a number from 1 to 99, then insert, search or delete it. Smaller values go left, larger values go right.');
    b.innerHTML = `<div class="vz-ops"><input class="vz-num" type="number" min="1" max="99" value="5" aria-label="Value"><button data-op="ins">Insert</button><button data-op="find">Search</button><button data-op="del">Delete</button><button data-op="new">New random tree</button></div><div class="vz-tree"></div><div class="vz-msg" aria-live="polite"></div>`;
    const seq = Seq(), tree = $('.vz-tree', b), msg = $('.vz-msg', b), inp = $('.vz-num', b);
    let root = null;
    const ins = (n, v) => { if (!n) return N(v); if (v < n.v) n.l = ins(n.l, v); else n.r = ins(n.r, v); return n; };
    const del = (n, v) => {
      if (!n) return null;
      if (v < n.v) n.l = del(n.l, v);
      else if (v > n.v) n.r = del(n.r, v);
      else {
        if (!n.l) return n.r;
        if (!n.r) return n.l;
        let s = n.r; while (s.l) s = s.l;
        n.v = s.v; n.r = del(n.r, s.v);
      }
      return n;
    };
    const count = n => n ? 1 + count(n.l) + count(n.r) : 0;
    const draw = (hl = new Map()) => { tree.innerHTML = svgTree(root, n => hl.get(n) || '', n => hl.has(n) ? 'on' : ''); };
    const say = h => { msg.innerHTML = h; };
    const pathTo = v => { const p = []; let n = root; while (n) { p.push(n); if (v === n.v) break; n = v < n.v ? n.l : n.r; } return p; };
    const cmp = (v, n) => v === n.v ? `${v} equals ${n.v}.` : v < n.v ? `${v} &lt; ${n.v}, so go left.` : `${v} &gt; ${n.v}, so go right.`;
    function walk(v, done) {
      const path = pathTo(v);
      const fs = path.map((n, k) => () => { const m = new Map(); path.slice(0, k).forEach(p => m.set(p, 'mv')); m.set(n, 'hl'); draw(m); say(cmp(v, n)); });
      fs.push(() => done(path, path.length && path[path.length - 1].v === v));
      seq.run(fs, 700);
    }
    function fresh(vals) {
      seq.stop(); root = null;
      vals.forEach(v => { root = ins(root, v); });
      draw();
      say(`Inserted ${vals.join(', ')} in that order. Try searching for a value, or inserting a new one.`);
    }
    b.querySelector('.vz-ops').addEventListener('click', e => {
      const op = (e.target.closest('button') || {}).dataset?.op;
      if (!op) return;
      if (op === 'new') {
        const s = new Set(); while (s.size < 8) s.add(rand(1, 99));
        fresh([...s]); return;
      }
      const v = parseInt(inp.value, 10);
      if (!(v >= 1 && v <= 99)) { say('Type a whole number from 1 to 99 first.'); return; }
      if (op === 'ins') {
        if (count(root) >= 15) { say('This demo keeps the tree at 15 nodes or fewer. Delete something first.'); return; }
        walk(v, (path, found) => {
          if (found) { draw(new Map([[path[path.length - 1], 'ok']])); say(`${v} is already in the tree, so nothing changes.`); return; }
          root = ins(root, v);
          const m = new Map(); path.forEach(p => m.set(p, 'mv'));
          m.set(pathTo(v).pop(), 'ok'); draw(m);
          say(`${v} takes the empty spot at the end of the path, after ${path.length} comparison${path.length === 1 ? '' : 's'}.`);
        });
      }
      if (op === 'find') {
        walk(v, (path, found) => {
          const m = new Map(); path.forEach(p => m.set(p, 'mv'));
          if (found) { m.set(path[path.length - 1], 'ok'); draw(m); say(`Found ${v} after ${path.length} comparison${path.length === 1 ? '' : 's'}.`); }
          else { draw(m); say(`Reached an empty spot, so ${v} is not in the tree. That took ${path.length} comparison${path.length === 1 ? '' : 's'}.`); }
        });
      }
      if (op === 'del') {
        walk(v, (path, found) => {
          if (!found) { draw(); say(`${v} is not in the tree, so there is nothing to delete.`); return; }
          const t = path[path.length - 1];
          if (t.l && t.r) {
            let s = t.r; while (s.l) s = s.l;
            draw(new Map([[t, 'hl'], [s, 'ok']]));
            say(`${v} has two children. Its inorder successor is ${s.v}, the smallest value on its right. Copy ${s.v} up, then remove the old ${s.v}.`);
            seq.run([() => {}, () => { root = del(root, v); draw(new Map([[pathTo(s.v).pop(), 'ok']])); say(`${s.v} now sits where ${v} was. The tree is still in order.`); }], 1500);
          } else {
            const kind = !t.l && !t.r ? 'a leaf, so it is simply removed' : `one child, so the child ${(t.l || t.r).v} moves up into its place`;
            root = del(root, v); draw();
            say(`${v} has ${kind}.`);
          }
        });
      }
    });
    fresh([8, 3, 10, 1, 6, 14, 4, 7, 13]);
  };

  /* ======================= insertion order decides the shape ======================= */
  W.shape = el => {
    const b = shell(el, 'Same values, different shapes', 'Both trees receive the values 1 to 7. Only the order of insertion differs. Press Play and compare the heights.');
    b.innerHTML = `<div class="vz-row">${seg('o', [['mid', 'Middle first'], ['rand', 'Random order (press again to shuffle)']], 'mid')}</div>
      <div class="vz-pair"><div><h4>Sorted order: 1 2 3 4 5 6 7</h4><div class="vz-tree vz-ta"></div><div class="vz-note vz-ha"></div></div><div><h4 class="vz-ob"></h4><div class="vz-tree vz-tb"></div><div class="vz-note vz-hb"></div></div></div>
      <div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const ins = (n, v) => { if (!n) return N(v); if (v < n.v) n.l = ins(n.l, v); else n.r = ins(n.r, v); return n; };
    const sorted = [1, 2, 3, 4, 5, 6, 7];
    let other = [4, 2, 6, 1, 3, 5, 7], A, B, LA, LB;
    const P = Player($('.vz-p', b), show, 900);
    function setup() {
      A = null; B = null;
      sorted.forEach(v => { A = ins(A, v); });
      other.forEach(v => { B = ins(B, v); });
      LA = layout(A); LB = layout(B);
      $('.vz-ob', b).textContent = `This order: ${other.join(' ')}`;
      P.load(sorted.length + 1);
    }
    const height = (L, set) => { let h = 0; L.pos.forEach((p, n) => { if (set.has(n.v)) h = Math.max(h, p.d + 1); }); return h; };
    function one(root, L, order, k, host, hhost) {
      const set = new Set(order.slice(0, k)), last = order[k - 1];
      host.innerHTML = svgTree(root, n => !set.has(n.v) ? 'gone' : n.v === last ? 'mv' : 'ok', n => set.has(n.v) ? '' : 'gone', { layout: L });
      const h = height(L, set);
      hhost.innerHTML = `height <b>${h}</b>`;
      return h;
    }
    function show(k) {
      const ha = one(A, LA, sorted, k, $('.vz-ta', b), $('.vz-ha', b));
      const hb = one(B, LB, other, k, $('.vz-tb', b), $('.vz-hb', b));
      $('.vz-msg', b).innerHTML = k === 0 ? 'Both trees start empty.'
        : k < sorted.length ? `Insert ${sorted[k - 1]} on the left and ${other[k - 1]} on the right. Heights so far: ${ha} and ${hb}.`
        : `All 7 values are in. The sorted order built a chain of <b>${ha}</b> levels, as slow as a linked list. The other order needs <b>${hb}</b>${hb === 3 ? ', the minimum, because ⌈log₂(7 + 1)⌉ = 3' : ''}.`;
    }
    wireSeg(b, 'o', v => {
      if (v === 'mid') other = [4, 2, 6, 1, 3, 5, 7];
      else { other = sorted.slice(); for (let i = other.length - 1; i > 0; i--) { const j = rand(0, i); [other[i], other[j]] = [other[j], other[i]]; } }
      setup();
    });
    setup();
  };

  /* ======================= min heap in an array ======================= */
  W.heap = el => {
    const b = shell(el, 'A min heap is a tree stored in an array', 'Push adds at the end and bubbles up. Pop takes the root, moves the last item to the top and lets it sink. The small numbers under the nodes are array indexes.');
    b.innerHTML = `<div class="vz-ops"><button data-op="push">Push a random number</button><button data-op="pop">Pop the minimum</button><button data-op="reset">Reset</button></div><div class="vz-tree"></div><h4>The same heap as an array</h4><div class="vz-scroll"><div class="vz-cells vz-big vz-arr"></div></div><div class="vz-msg" aria-live="polite"></div>`;
    const seq = Seq(), tree = $('.vz-tree', b), arr = $('.vz-arr', b), msg = $('.vz-msg', b);
    const START = [2, 5, 3, 9, 6, 8, 4];
    let a = START.slice();
    function draw(x, hl = {}) {
      const ns = x.map((v, i) => ({ v, i, l: null, r: null }));
      ns.forEach((n, i) => { n.l = ns[2 * i + 1] || null; n.r = ns[2 * i + 2] || null; });
      tree.innerHTML = svgTree(ns[0] || null, n => hl[n.i] || '', n => hl[n.i] ? 'on' : '', { sub: n => n.i });
      arr.innerHTML = x.map((v, i) => cell(v, hl[i] || '', i)).join('') || '<span class="vz-note">empty</span>';
    }
    const play = frames => seq.run(frames.map(f => () => { draw(f.a, f.hl); msg.innerHTML = f.msg; }), 900);
    function push() {
      if (a.length >= 15) { msg.innerHTML = 'This demo stops at 15 items. Pop a few first.'; return; }
      const v = rand(1, 30), x = a.slice(), frames = [];
      x.push(v);
      let i = x.length - 1;
      frames.push({ a: x.slice(), hl: { [i]: 'mv' }, msg: `Add ${v} at index ${i}, the next free spot, so the tree stays complete.` });
      while (i > 0) {
        const p = (i - 1) >> 1;
        if (x[p] <= x[i]) { frames.push({ a: x.slice(), hl: { [p]: 'ok', [i]: 'ok' }, msg: `The parent ${x[p]} at index ${p} is not larger than ${v}. Stop here.` }); break; }
        [x[p], x[i]] = [x[i], x[p]];
        frames.push({ a: x.slice(), hl: { [p]: 'hl', [i]: 'mv' }, msg: `${v} is smaller than its parent at index ${p} = ⌊(${i} − 1) / 2⌋, so they swap.` });
        i = p;
      }
      if (i === 0) frames.push({ a: x.slice(), hl: { 0: 'ok' }, msg: `${v} reached the root. It is the new minimum.` });
      a = x; play(frames);
    }
    function pop() {
      if (!a.length) { msg.innerHTML = 'The heap is empty. Press Push or Reset.'; return; }
      const x = a.slice(), frames = [], top = x[0];
      frames.push({ a: x.slice(), hl: { 0: 'bad' }, msg: `The minimum ${top} is always at the root. Take it out.` });
      const last = x.pop();
      if (x.length) {
        x[0] = last;
        frames.push({ a: x.slice(), hl: { 0: 'mv' }, msg: `Move the last item ${last} to the root. Now it has to sink.` });
        let i = 0;
        while (true) {
          let s = i;
          for (const c of [2 * i + 1, 2 * i + 2]) if (c < x.length && x[c] < x[s]) s = c;
          if (s === i) { frames.push({ a: x.slice(), hl: { [i]: 'ok' }, msg: `${x[i]} is not larger than its children. The heap is in order again.` }); break; }
          [x[s], x[i]] = [x[i], x[s]];
          frames.push({ a: x.slice(), hl: { [i]: 'hl', [s]: 'mv' }, msg: `Swap with the smaller child ${x[i]} at index ${s}.` });
          i = s;
        }
      } else frames.push({ a: [], hl: {}, msg: `Popped ${top}. The heap is now empty.` });
      a = x; play(frames);
    }
    b.querySelector('.vz-ops').addEventListener('click', e => {
      const op = (e.target.closest('button') || {}).dataset?.op;
      if (op === 'push') push();
      if (op === 'pop') pop();
      if (op === 'reset') { seq.stop(); a = START.slice(); draw(a); msg.innerHTML = 'Every parent is smaller than its children, so 2 sits at the root.'; }
    });
    draw(a);
    msg.innerHTML = 'Every parent is smaller than its children, so 2 sits at the root. Press Push or Pop.';
  };
})();
'''

CSS = r'''
.vz-sbox .vz-stack,.vz-aux .vz-stack{margin:0}
.vz-tn.bad circle{fill:var(--bad); stroke:var(--bad-line)}
.vz-tn.sel circle{fill:var(--sel); stroke:var(--sel-line)}
.vz-tn.gone,.vz-edge.gone{opacity:0}
.vz-tn,.vz-edge{transition:opacity .35s}
.vz-num{width:84px; padding:6px 12px; border:1.5px solid var(--line); border-radius:999px; background:var(--surface); color:var(--ink); font:inherit; font-size:14px; font-weight:800}
.vz-pair{display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:8px}
.vz-pair .vz-note{text-align:center; margin-top:4px}
@media (max-width:640px){.vz-pair{grid-template-columns:1fr}}
'''

T = {
    'slug': 'trees', 'title': 'Trees', 'short': 'Trees', 'emoji': '🌲', 'topic': 'trees', 'prefix': 'dsat',
    'module': ('🌳', 'Trees and graphs'),
    'lead': 'Trees organise data as a hierarchy, from one root down to many leaves. This page covers the vocabulary and the recursive pattern behind almost every tree problem, four traversal orders, binary search trees with insert, search and delete, why balance matters, heaps stored in arrays, and tries for words.',
    'desc': 'Trees in DSA: binary trees, preorder, inorder, postorder and level order traversal, binary search trees, deletion, balance and height, binary heaps and tries, with code in Python, JavaScript and Java.',
    'minutes': 15,
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'practice': PRACTICE, 'quiz': QUIZ, 'calc': CALC,
    'viz': VIZ_JS, 'css': CSS,
    'prev': ('stacks-queues', 'stacks-queues', '🥞 Stacks and queues'),
    'next': ('graphs', 'graphs', '🕸️ Graphs'),
}
