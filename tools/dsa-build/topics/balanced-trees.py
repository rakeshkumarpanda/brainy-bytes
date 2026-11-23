# Balanced and disk trees: why balance matters, rotations and AVL trees, left leaning red black trees,
# B trees and B+ trees for disks and databases, and the ordered maps built on them in each language.
from kit4 import Topic

t = Topic()

# ---------------------------------------------------------------- lesson programs
t.code('chain', py=r'''
class Node:
    def __init__(self, key):
        self.key, self.left, self.right, self.h = key, None, None, 1


def plain_insert(root, key):                  # an ordinary BST insert, written as a loop
    node = Node(key)
    if root is None:
        return node
    cur = root
    while True:
        if key < cur.key:
            if cur.left is None:
                cur.left = node
                return root
            cur = cur.left
        else:
            if cur.right is None:
                cur.right = node
                return root
            cur = cur.right


def height(root):                             # count levels with a queue, no deep recursion
    levels, level = 0, [root] if root else []
    while level:
        levels += 1
        level = [c for n in level for c in (n.left, n.right) if c]
    return levels


def h(n):
    return n.h if n else 0


def fix(n):
    n.h = 1 + max(h(n.left), h(n.right))


def rotate_right(y):
    x = y.left
    y.left, x.right = x.right, y
    fix(y)
    fix(x)
    return x


def rotate_left(x):
    y = x.right
    x.right, y.left = y.left, x
    fix(x)
    fix(y)
    return y


def avl_insert(n, key):
    if n is None:
        return Node(key)
    if key < n.key:
        n.left = avl_insert(n.left, key)
    else:
        n.right = avl_insert(n.right, key)
    fix(n)
    balance = h(n.left) - h(n.right)
    if balance > 1:                           # left side too tall
        if key >= n.left.key:
            n.left = rotate_left(n.left)
        return rotate_right(n)
    if balance < -1:                          # right side too tall
        if key < n.right.key:
            n.right = rotate_right(n.right)
        return rotate_left(n)
    return n


for n in (7, 15, 100, 1000):
    plain = avl = None
    for k in range(1, n + 1):                 # keys arrive already sorted: the worst case
        plain = plain_insert(plain, k)
        avl = avl_insert(avl, k)
    print(n, "sorted keys:  plain BST height", height(plain), "  AVL height", height(avl))
''', js=r'''
class Node {
  constructor(key) { this.key = key; this.left = null; this.right = null; this.h = 1; }
}

function plainInsert(root, key) {            // an ordinary BST insert, written as a loop
  const node = new Node(key);
  if (root === null) return node;
  let cur = root;
  while (true) {
    if (key < cur.key) {
      if (cur.left === null) { cur.left = node; return root; }
      cur = cur.left;
    } else {
      if (cur.right === null) { cur.right = node; return root; }
      cur = cur.right;
    }
  }
}

function height(root) {                      // count levels with a queue, no deep recursion
  let levels = 0, level = root ? [root] : [];
  while (level.length) {
    levels++;
    level = level.flatMap(n => [n.left, n.right]).filter(c => c);
  }
  return levels;
}

const h = n => (n ? n.h : 0);
const fix = n => { n.h = 1 + Math.max(h(n.left), h(n.right)); };

function rotateRight(y) {
  const x = y.left;
  y.left = x.right; x.right = y;
  fix(y); fix(x);
  return x;
}

function rotateLeft(x) {
  const y = x.right;
  x.right = y.left; y.left = x;
  fix(x); fix(y);
  return y;
}

function avlInsert(n, key) {
  if (n === null) return new Node(key);
  if (key < n.key) n.left = avlInsert(n.left, key);
  else n.right = avlInsert(n.right, key);
  fix(n);
  const balance = h(n.left) - h(n.right);
  if (balance > 1) {                         // left side too tall
    if (key >= n.left.key) n.left = rotateLeft(n.left);
    return rotateRight(n);
  }
  if (balance < -1) {                        // right side too tall
    if (key < n.right.key) n.right = rotateRight(n.right);
    return rotateLeft(n);
  }
  return n;
}

for (const n of [7, 15, 100, 1000]) {
  let plain = null, avl = null;
  for (let k = 1; k <= n; k++) {             // keys arrive already sorted: the worst case
    plain = plainInsert(plain, k);
    avl = avlInsert(avl, k);
  }
  console.log(n, "sorted keys:  plain BST height", height(plain), "  AVL height", height(avl));
}
''', java=r'''
import java.util.*;

public class ChainVsAVL {
    static class Node {
        int key, h = 1;
        Node left, right;
        Node(int k) { key = k; }
    }

    static Node plainInsert(Node root, int key) {        // an ordinary BST insert, written as a loop
        Node node = new Node(key);
        if (root == null) return node;
        Node cur = root;
        while (true) {
            if (key < cur.key) {
                if (cur.left == null) { cur.left = node; return root; }
                cur = cur.left;
            } else {
                if (cur.right == null) { cur.right = node; return root; }
                cur = cur.right;
            }
        }
    }

    static int height(Node root) {                       // count levels with a queue, no deep recursion
        int levels = 0;
        List<Node> level = new ArrayList<>();
        if (root != null) level.add(root);
        while (!level.isEmpty()) {
            levels++;
            List<Node> next = new ArrayList<>();
            for (Node n : level) {
                if (n.left != null) next.add(n.left);
                if (n.right != null) next.add(n.right);
            }
            level = next;
        }
        return levels;
    }

    static int h(Node n) { return n == null ? 0 : n.h; }
    static void fix(Node n) { n.h = 1 + Math.max(h(n.left), h(n.right)); }

    static Node rotateRight(Node y) {
        Node x = y.left;
        y.left = x.right; x.right = y;
        fix(y); fix(x);
        return x;
    }

    static Node rotateLeft(Node x) {
        Node y = x.right;
        x.right = y.left; y.left = x;
        fix(x); fix(y);
        return y;
    }

    static Node avlInsert(Node n, int key) {
        if (n == null) return new Node(key);
        if (key < n.key) n.left = avlInsert(n.left, key);
        else n.right = avlInsert(n.right, key);
        fix(n);
        int balance = h(n.left) - h(n.right);
        if (balance > 1) {                               // left side too tall
            if (key >= n.left.key) n.left = rotateLeft(n.left);
            return rotateRight(n);
        }
        if (balance < -1) {                              // right side too tall
            if (key < n.right.key) n.right = rotateRight(n.right);
            return rotateLeft(n);
        }
        return n;
    }

    public static void main(String[] args) {
        for (int n : new int[]{7, 15, 100, 1000}) {
            Node plain = null, avl = null;
            for (int k = 1; k <= n; k++) {               // keys arrive already sorted: the worst case
                plain = plainInsert(plain, k);
                avl = avlInsert(avl, k);
            }
            System.out.println(n + " sorted keys:  plain BST height " + height(plain) + "   AVL height " + height(avl));
        }
    }
}
''', ts=r'''
class TNode {
  key: number;
  left: TNode | null = null;
  right: TNode | null = null;
  h = 1;
  constructor(key: number) { this.key = key; }
}

function plainInsert(root: TNode | null, key: number): TNode {   // an ordinary BST insert, written as a loop
  const node = new TNode(key);
  if (root === null) return node;
  let cur: TNode = root;
  while (true) {
    if (key < cur.key) {
      if (cur.left === null) { cur.left = node; return root; }
      cur = cur.left;
    } else {
      if (cur.right === null) { cur.right = node; return root; }
      cur = cur.right;
    }
  }
}

function height(root: TNode | null): number {   // count levels with a queue, no deep recursion
  let levels = 0, level: TNode[] = root ? [root] : [];
  while (level.length) {
    levels++;
    level = level.flatMap(n => [n.left, n.right]).filter((c): c is TNode => c !== null);
  }
  return levels;
}

const h = (n: TNode | null): number => (n ? n.h : 0);
const fix = (n: TNode): void => { n.h = 1 + Math.max(h(n.left), h(n.right)); };

function rotateRight(y: TNode): TNode {
  const x = y.left as TNode;
  y.left = x.right; x.right = y;
  fix(y); fix(x);
  return x;
}

function rotateLeft(x: TNode): TNode {
  const y = x.right as TNode;
  x.right = y.left; y.left = x;
  fix(x); fix(y);
  return y;
}

function avlInsert(n: TNode | null, key: number): TNode {
  if (n === null) return new TNode(key);
  if (key < n.key) n.left = avlInsert(n.left, key);
  else n.right = avlInsert(n.right, key);
  fix(n);
  const balance = h(n.left) - h(n.right);
  if (balance > 1) {                         // left side too tall
    if (key >= (n.left as TNode).key) n.left = rotateLeft(n.left as TNode);
    return rotateRight(n);
  }
  if (balance < -1) {                        // right side too tall
    if (key < (n.right as TNode).key) n.right = rotateRight(n.right as TNode);
    return rotateLeft(n);
  }
  return n;
}

for (const n of [7, 15, 100, 1000]) {
  let plain: TNode | null = null, avl: TNode | null = null;
  for (let k = 1; k <= n; k++) {             // keys arrive already sorted: the worst case
    plain = plainInsert(plain, k);
    avl = avlInsert(avl, k);
  }
  console.log(n, "sorted keys:  plain BST height", height(plain), "  AVL height", height(avl));
}
''')

t.code('avl', py=r'''
class Node:
    def __init__(self, key):
        self.key, self.left, self.right, self.h = key, None, None, 1


log = []


def h(n):
    return n.h if n else 0


def fix(n):
    n.h = 1 + max(h(n.left), h(n.right))


def rotate_right(y):                          # y's left child x moves up, y becomes x's right child
    x = y.left
    y.left, x.right = x.right, y
    fix(y)
    fix(x)
    return x


def rotate_left(x):                           # the mirror image
    y = x.right
    x.right, y.left = y.left, x
    fix(x)
    fix(y)
    return y


def insert(n, key):
    if n is None:
        return Node(key)
    if key < n.key:
        n.left = insert(n.left, key)
    else:
        n.right = insert(n.right, key)
    fix(n)
    balance = h(n.left) - h(n.right)          # must stay -1, 0 or +1
    if balance > 1 and key < n.left.key:
        log.append(f"LL at {n.key}: rotate right")
        return rotate_right(n)
    if balance < -1 and key >= n.right.key:
        log.append(f"RR at {n.key}: rotate left")
        return rotate_left(n)
    if balance > 1:
        log.append(f"LR at {n.key}: rotate left, then right")
        n.left = rotate_left(n.left)
        return rotate_right(n)
    if balance < -1:
        log.append(f"RL at {n.key}: rotate right, then left")
        n.right = rotate_right(n.right)
        return rotate_left(n)
    return n


def levels(root):
    out, level = [], [root]
    while level:
        out.append(" ".join(str(n.key) for n in level))
        level = [c for n in level for c in (n.left, n.right) if c]
    return " | ".join(out)


root = None
for key in [10, 20, 30, 40, 50, 25]:
    log.clear()
    root = insert(root, key)
    print("insert", key, "->", "; ".join(log) or "still balanced", " levels:", levels(root))
''', js=r'''
class Node {
  constructor(key) { this.key = key; this.left = null; this.right = null; this.h = 1; }
}

const log = [];
const h = n => (n ? n.h : 0);
const fix = n => { n.h = 1 + Math.max(h(n.left), h(n.right)); };

function rotateRight(y) {                    // y's left child x moves up, y becomes x's right child
  const x = y.left;
  y.left = x.right; x.right = y;
  fix(y); fix(x);
  return x;
}

function rotateLeft(x) {                     // the mirror image
  const y = x.right;
  x.right = y.left; y.left = x;
  fix(x); fix(y);
  return y;
}

function insert(n, key) {
  if (n === null) return new Node(key);
  if (key < n.key) n.left = insert(n.left, key);
  else n.right = insert(n.right, key);
  fix(n);
  const balance = h(n.left) - h(n.right);   // must stay -1, 0 or +1
  if (balance > 1 && key < n.left.key) { log.push(`LL at ${n.key}: rotate right`); return rotateRight(n); }
  if (balance < -1 && key >= n.right.key) { log.push(`RR at ${n.key}: rotate left`); return rotateLeft(n); }
  if (balance > 1) { log.push(`LR at ${n.key}: rotate left, then right`); n.left = rotateLeft(n.left); return rotateRight(n); }
  if (balance < -1) { log.push(`RL at ${n.key}: rotate right, then left`); n.right = rotateRight(n.right); return rotateLeft(n); }
  return n;
}

function levels(root) {
  const out = [];
  let level = [root];
  while (level.length) {
    out.push(level.map(n => n.key).join(" "));
    level = level.flatMap(n => [n.left, n.right]).filter(c => c);
  }
  return out.join(" | ");
}

let root = null;
for (const key of [10, 20, 30, 40, 50, 25]) {
  log.length = 0;
  root = insert(root, key);
  console.log("insert", key, "->", log.join("; ") || "still balanced", " levels:", levels(root));
}
''', java=r'''
import java.util.*;

public class AVLTree {
    static class Node {
        int key, h = 1;
        Node left, right;
        Node(int k) { key = k; }
    }

    static List<String> log = new ArrayList<>();

    static int h(Node n) { return n == null ? 0 : n.h; }
    static void fix(Node n) { n.h = 1 + Math.max(h(n.left), h(n.right)); }

    static Node rotateRight(Node y) {                    // y's left child x moves up, y becomes x's right child
        Node x = y.left;
        y.left = x.right; x.right = y;
        fix(y); fix(x);
        return x;
    }

    static Node rotateLeft(Node x) {                     // the mirror image
        Node y = x.right;
        x.right = y.left; y.left = x;
        fix(x); fix(y);
        return y;
    }

    static Node insert(Node n, int key) {
        if (n == null) return new Node(key);
        if (key < n.key) n.left = insert(n.left, key);
        else n.right = insert(n.right, key);
        fix(n);
        int balance = h(n.left) - h(n.right);           // must stay -1, 0 or +1
        if (balance > 1 && key < n.left.key) { log.add("LL at " + n.key + ": rotate right"); return rotateRight(n); }
        if (balance < -1 && key >= n.right.key) { log.add("RR at " + n.key + ": rotate left"); return rotateLeft(n); }
        if (balance > 1) { log.add("LR at " + n.key + ": rotate left, then right"); n.left = rotateLeft(n.left); return rotateRight(n); }
        if (balance < -1) { log.add("RL at " + n.key + ": rotate right, then left"); n.right = rotateRight(n.right); return rotateLeft(n); }
        return n;
    }

    static String levels(Node root) {
        List<String> out = new ArrayList<>();
        List<Node> level = new ArrayList<>(List.of(root));
        while (!level.isEmpty()) {
            StringJoiner sj = new StringJoiner(" ");
            List<Node> next = new ArrayList<>();
            for (Node n : level) {
                sj.add(String.valueOf(n.key));
                if (n.left != null) next.add(n.left);
                if (n.right != null) next.add(n.right);
            }
            out.add(sj.toString());
            level = next;
        }
        return String.join(" | ", out);
    }

    public static void main(String[] args) {
        Node root = null;
        for (int key : new int[]{10, 20, 30, 40, 50, 25}) {
            log.clear();
            root = insert(root, key);
            String what = log.isEmpty() ? "still balanced" : String.join("; ", log);
            System.out.println("insert " + key + " -> " + what + "  levels: " + levels(root));
        }
    }
}
''', ts=r'''
class TNode {
  key: number;
  left: TNode | null = null;
  right: TNode | null = null;
  h = 1;
  constructor(key: number) { this.key = key; }
}

const log: string[] = [];
const h = (n: TNode | null): number => (n ? n.h : 0);
const fix = (n: TNode): void => { n.h = 1 + Math.max(h(n.left), h(n.right)); };

function rotateRight(y: TNode): TNode {        // y's left child x moves up, y becomes x's right child
  const x = y.left as TNode;
  y.left = x.right; x.right = y;
  fix(y); fix(x);
  return x;
}

function rotateLeft(x: TNode): TNode {         // the mirror image
  const y = x.right as TNode;
  x.right = y.left; y.left = x;
  fix(x); fix(y);
  return y;
}

function insert(n: TNode | null, key: number): TNode {
  if (n === null) return new TNode(key);
  if (key < n.key) n.left = insert(n.left, key);
  else n.right = insert(n.right, key);
  fix(n);
  const balance = h(n.left) - h(n.right);   // must stay -1, 0 or +1
  if (balance > 1 && key < (n.left as TNode).key) { log.push(`LL at ${n.key}: rotate right`); return rotateRight(n); }
  if (balance < -1 && key >= (n.right as TNode).key) { log.push(`RR at ${n.key}: rotate left`); return rotateLeft(n); }
  if (balance > 1) { log.push(`LR at ${n.key}: rotate left, then right`); n.left = rotateLeft(n.left as TNode); return rotateRight(n); }
  if (balance < -1) { log.push(`RL at ${n.key}: rotate right, then left`); n.right = rotateRight(n.right as TNode); return rotateLeft(n); }
  return n;
}

function levels(root: TNode): string {
  const out: string[] = [];
  let level: TNode[] = [root];
  while (level.length) {
    out.push(level.map(n => n.key).join(" "));
    level = level.flatMap(n => [n.left, n.right]).filter((c): c is TNode => c !== null);
  }
  return out.join(" | ");
}

let root: TNode | null = null;
for (const key of [10, 20, 30, 40, 50, 25]) {
  log.length = 0;
  root = insert(root, key);
  console.log("insert", key, "->", log.join("; ") || "still balanced", " levels:", levels(root));
}
''')

t.code('llrb', py=r'''
class Node:
    def __init__(self, key):
        self.key, self.left, self.right, self.red = key, None, None, True   # new nodes are red


def is_red(n):
    return n is not None and n.red


def rotate_left(h):                           # a right leaning red link becomes left leaning
    x = h.right
    h.right, x.left = x.left, h
    x.red, h.red = h.red, True
    return x


def rotate_right(h):                          # two reds in a row on the left: lift the middle one
    x = h.left
    h.left, x.right = x.right, h
    x.red, h.red = h.red, True
    return x


def flip_colors(h):                           # both children red: push the red up one level
    h.red, h.left.red, h.right.red = True, False, False


def insert(h, key):
    if h is None:
        return Node(key)
    if key < h.key:
        h.left = insert(h.left, key)
    elif key > h.key:
        h.right = insert(h.right, key)
    if is_red(h.right) and not is_red(h.left):
        h = rotate_left(h)
    if is_red(h.left) and is_red(h.left.left):
        h = rotate_right(h)
    if is_red(h.left) and is_red(h.right):
        flip_colors(h)
    return h


def put(root, key):
    root = insert(root, key)
    root.red = False                          # the root is always black
    return root


def levels(root):
    out, level = [], [root]
    while level:
        out.append(" ".join(f"{n.key}{'r' if n.red else 'b'}" for n in level))
        level = [c for n in level for c in (n.left, n.right) if c]
    return " | ".join(out)


def height(n):
    return 0 if n is None else 1 + max(height(n.left), height(n.right))


root = None
for key in range(1, 11):                      # sorted input, the worst case for a plain BST
    root = put(root, key)
print("levels (r = red, b = black):", levels(root))
print("height", height(root), "for 10 keys")
''', js=r'''
class Node {
  constructor(key) { this.key = key; this.left = null; this.right = null; this.red = true; }   // new nodes are red
}

const isRed = n => n !== null && n.red;

function rotateLeft(h) {                     // a right leaning red link becomes left leaning
  const x = h.right;
  h.right = x.left; x.left = h;
  x.red = h.red; h.red = true;
  return x;
}

function rotateRight(h) {                    // two reds in a row on the left: lift the middle one
  const x = h.left;
  h.left = x.right; x.right = h;
  x.red = h.red; h.red = true;
  return x;
}

function flipColors(h) {                     // both children red: push the red up one level
  h.red = true; h.left.red = false; h.right.red = false;
}

function insert(h, key) {
  if (h === null) return new Node(key);
  if (key < h.key) h.left = insert(h.left, key);
  else if (key > h.key) h.right = insert(h.right, key);
  if (isRed(h.right) && !isRed(h.left)) h = rotateLeft(h);
  if (isRed(h.left) && isRed(h.left.left)) h = rotateRight(h);
  if (isRed(h.left) && isRed(h.right)) flipColors(h);
  return h;
}

function put(root, key) {
  root = insert(root, key);
  root.red = false;                          // the root is always black
  return root;
}

function levels(root) {
  const out = [];
  let level = [root];
  while (level.length) {
    out.push(level.map(n => n.key + (n.red ? "r" : "b")).join(" "));
    level = level.flatMap(n => [n.left, n.right]).filter(c => c);
  }
  return out.join(" | ");
}

const height = n => (n === null ? 0 : 1 + Math.max(height(n.left), height(n.right)));

let root = null;
for (let key = 1; key <= 10; key++) root = put(root, key);   // sorted input, the worst case for a plain BST
console.log("levels (r = red, b = black):", levels(root));
console.log("height", height(root), "for 10 keys");
''', java=r'''
import java.util.*;

public class LeftLeaningRedBlack {
    static class Node {
        int key;
        Node left, right;
        boolean red = true;                              // new nodes are red
        Node(int k) { key = k; }
    }

    static boolean isRed(Node n) { return n != null && n.red; }

    static Node rotateLeft(Node h) {                     // a right leaning red link becomes left leaning
        Node x = h.right;
        h.right = x.left; x.left = h;
        x.red = h.red; h.red = true;
        return x;
    }

    static Node rotateRight(Node h) {                    // two reds in a row on the left: lift the middle one
        Node x = h.left;
        h.left = x.right; x.right = h;
        x.red = h.red; h.red = true;
        return x;
    }

    static void flipColors(Node h) {                     // both children red: push the red up one level
        h.red = true; h.left.red = false; h.right.red = false;
    }

    static Node insert(Node h, int key) {
        if (h == null) return new Node(key);
        if (key < h.key) h.left = insert(h.left, key);
        else if (key > h.key) h.right = insert(h.right, key);
        if (isRed(h.right) && !isRed(h.left)) h = rotateLeft(h);
        if (isRed(h.left) && isRed(h.left.left)) h = rotateRight(h);
        if (isRed(h.left) && isRed(h.right)) flipColors(h);
        return h;
    }

    static Node put(Node root, int key) {
        root = insert(root, key);
        root.red = false;                                // the root is always black
        return root;
    }

    static String levels(Node root) {
        List<String> out = new ArrayList<>();
        List<Node> level = new ArrayList<>(List.of(root));
        while (!level.isEmpty()) {
            StringJoiner sj = new StringJoiner(" ");
            List<Node> next = new ArrayList<>();
            for (Node n : level) {
                sj.add(n.key + (n.red ? "r" : "b"));
                if (n.left != null) next.add(n.left);
                if (n.right != null) next.add(n.right);
            }
            out.add(sj.toString());
            level = next;
        }
        return String.join(" | ", out);
    }

    static int height(Node n) { return n == null ? 0 : 1 + Math.max(height(n.left), height(n.right)); }

    public static void main(String[] args) {
        Node root = null;
        for (int key = 1; key <= 10; key++) root = put(root, key);   // sorted input, the worst case for a plain BST
        System.out.println("levels (r = red, b = black): " + levels(root));
        System.out.println("height " + height(root) + " for 10 keys");
    }
}
''', ts=r'''
class TNode {
  key: number;
  left: TNode | null = null;
  right: TNode | null = null;
  red = true;                                // new nodes are red
  constructor(key: number) { this.key = key; }
}

const isRed = (n: TNode | null): boolean => n !== null && n.red;

function rotateLeft(h: TNode): TNode {         // a right leaning red link becomes left leaning
  const x = h.right as TNode;
  h.right = x.left; x.left = h;
  x.red = h.red; h.red = true;
  return x;
}

function rotateRight(h: TNode): TNode {        // two reds in a row on the left: lift the middle one
  const x = h.left as TNode;
  h.left = x.right; x.right = h;
  x.red = h.red; h.red = true;
  return x;
}

function flipColors(h: TNode): void {         // both children red: push the red up one level
  h.red = true; (h.left as TNode).red = false; (h.right as TNode).red = false;
}

function insert(h: TNode | null, key: number): TNode {
  if (h === null) return new TNode(key);
  if (key < h.key) h.left = insert(h.left, key);
  else if (key > h.key) h.right = insert(h.right, key);
  if (isRed(h.right) && !isRed(h.left)) h = rotateLeft(h);
  if (isRed(h.left) && isRed((h.left as TNode).left)) h = rotateRight(h);
  if (isRed(h.left) && isRed(h.right)) flipColors(h);
  return h;
}

function put(root: TNode | null, key: number): TNode {
  const r = insert(root, key);
  r.red = false;                             // the root is always black
  return r;
}

function levels(root: TNode): string {
  const out: string[] = [];
  let level: TNode[] = [root];
  while (level.length) {
    out.push(level.map(n => n.key + (n.red ? "r" : "b")).join(" "));
    level = level.flatMap(n => [n.left, n.right]).filter((c): c is TNode => c !== null);
  }
  return out.join(" | ");
}

const height = (n: TNode | null): number => (n === null ? 0 : 1 + Math.max(height(n.left), height(n.right)));

let root: TNode | null = null;
for (let key = 1; key <= 10; key++) root = put(root, key);   // sorted input, the worst case for a plain BST
console.log("levels (r = red, b = black):", levels(root as TNode));
console.log("height", height(root), "for 10 keys");
''')

t.code('btree', py=r'''
T = 2                                         # minimum degree: every node holds 1 to 3 keys


class BNode:
    def __init__(self, leaf):
        self.keys, self.kids, self.leaf = [], [], leaf


splits = 0


def split_child(parent, i):
    global splits
    full = parent.kids[i]
    right = BNode(full.leaf)
    middle = full.keys[T - 1]                 # the middle key moves up into the parent
    right.keys = full.keys[T:]
    full.keys = full.keys[:T - 1]
    if not full.leaf:
        right.kids = full.kids[T:]
        full.kids = full.kids[:T]
    parent.kids.insert(i + 1, right)
    parent.keys.insert(i, middle)
    splits += 1


def insert_nonfull(node, key):
    i = len(node.keys)
    while i > 0 and node.keys[i - 1] > key:
        i -= 1
    if node.leaf:
        node.keys.insert(i, key)              # keys only ever go into leaves
        return
    if len(node.kids[i].keys) == 2 * T - 1:
        split_child(node, i)                  # split a full child before walking into it
        if key > node.keys[i]:
            i += 1
    insert_nonfull(node.kids[i], key)


def insert(root, key):
    if len(root.keys) == 2 * T - 1:           # a full root splits, and the tree grows one level taller
        new_root = BNode(False)
        new_root.kids = [root]
        split_child(new_root, 0)
        root = new_root
    insert_nonfull(root, key)
    return root


def levels(root):
    out, level = [], [root]
    while level:
        out.append(" ".join("[" + " ".join(map(str, n.keys)) + "]" for n in level))
        level = [c for n in level for c in n.kids]
    return "  /  ".join(out)


root = BNode(True)
for key in range(1, 11):
    root = insert(root, key)
    if key in (3, 4, 6, 10):
        print("after", key, ":", levels(root))
print("splits:", splits, " every leaf is on the same level")
''', js=r'''
const T = 2;                                 // minimum degree: every node holds 1 to 3 keys

class BNode {
  constructor(leaf) { this.keys = []; this.kids = []; this.leaf = leaf; }
}

let splits = 0;

function splitChild(parent, i) {
  const full = parent.kids[i], right = new BNode(full.leaf);
  const middle = full.keys[T - 1];           // the middle key moves up into the parent
  right.keys = full.keys.slice(T);
  full.keys = full.keys.slice(0, T - 1);
  if (!full.leaf) {
    right.kids = full.kids.slice(T);
    full.kids = full.kids.slice(0, T);
  }
  parent.kids.splice(i + 1, 0, right);
  parent.keys.splice(i, 0, middle);
  splits++;
}

function insertNonfull(node, key) {
  let i = node.keys.length;
  while (i > 0 && node.keys[i - 1] > key) i--;
  if (node.leaf) {
    node.keys.splice(i, 0, key);             // keys only ever go into leaves
    return;
  }
  if (node.kids[i].keys.length === 2 * T - 1) {
    splitChild(node, i);                     // split a full child before walking into it
    if (key > node.keys[i]) i++;
  }
  insertNonfull(node.kids[i], key);
}

function insert(root, key) {
  if (root.keys.length === 2 * T - 1) {      // a full root splits, and the tree grows one level taller
    const newRoot = new BNode(false);
    newRoot.kids = [root];
    splitChild(newRoot, 0);
    root = newRoot;
  }
  insertNonfull(root, key);
  return root;
}

function levels(root) {
  const out = [];
  let level = [root];
  while (level.length) {
    out.push(level.map(n => "[" + n.keys.join(" ") + "]").join(" "));
    level = level.flatMap(n => n.kids);
  }
  return out.join("  /  ");
}

let root = new BNode(true);
for (let key = 1; key <= 10; key++) {
  root = insert(root, key);
  if ([3, 4, 6, 10].includes(key)) console.log("after", key, ":", levels(root));
}
console.log("splits:", splits, " every leaf is on the same level");
''', java=r'''
import java.util.*;

public class BTreeDemo {
    static final int T = 2;                              // minimum degree: every node holds 1 to 3 keys

    static class BNode {
        List<Integer> keys = new ArrayList<>();
        List<BNode> kids = new ArrayList<>();
        boolean leaf;
        BNode(boolean leaf) { this.leaf = leaf; }
    }

    static int splits = 0;

    static void splitChild(BNode parent, int i) {
        BNode full = parent.kids.get(i), right = new BNode(full.leaf);
        int middle = full.keys.get(T - 1);               // the middle key moves up into the parent
        right.keys = new ArrayList<>(full.keys.subList(T, full.keys.size()));
        full.keys = new ArrayList<>(full.keys.subList(0, T - 1));
        if (!full.leaf) {
            right.kids = new ArrayList<>(full.kids.subList(T, full.kids.size()));
            full.kids = new ArrayList<>(full.kids.subList(0, T));
        }
        parent.kids.add(i + 1, right);
        parent.keys.add(i, middle);
        splits++;
    }

    static void insertNonfull(BNode node, int key) {
        int i = node.keys.size();
        while (i > 0 && node.keys.get(i - 1) > key) i--;
        if (node.leaf) {
            node.keys.add(i, key);                       // keys only ever go into leaves
            return;
        }
        if (node.kids.get(i).keys.size() == 2 * T - 1) {
            splitChild(node, i);                         // split a full child before walking into it
            if (key > node.keys.get(i)) i++;
        }
        insertNonfull(node.kids.get(i), key);
    }

    static BNode insert(BNode root, int key) {
        if (root.keys.size() == 2 * T - 1) {             // a full root splits, and the tree grows one level taller
            BNode newRoot = new BNode(false);
            newRoot.kids.add(root);
            splitChild(newRoot, 0);
            root = newRoot;
        }
        insertNonfull(root, key);
        return root;
    }

    static String levels(BNode root) {
        List<String> out = new ArrayList<>();
        List<BNode> level = new ArrayList<>(List.of(root));
        while (!level.isEmpty()) {
            StringJoiner sj = new StringJoiner(" ");
            List<BNode> next = new ArrayList<>();
            for (BNode n : level) {
                StringJoiner ks = new StringJoiner(" ", "[", "]");
                for (int k : n.keys) ks.add(String.valueOf(k));
                sj.add(ks.toString());
                next.addAll(n.kids);
            }
            out.add(sj.toString());
            level = next;
        }
        return String.join("  /  ", out);
    }

    public static void main(String[] args) {
        BNode root = new BNode(true);
        Set<Integer> show = Set.of(3, 4, 6, 10);
        for (int key = 1; key <= 10; key++) {
            root = insert(root, key);
            if (show.contains(key)) System.out.println("after " + key + " : " + levels(root));
        }
        System.out.println("splits: " + splits + "  every leaf is on the same level");
    }
}
''', ts=r'''
const T = 2;                                 // minimum degree: every node holds 1 to 3 keys

class BNode {
  keys: number[] = [];
  kids: BNode[] = [];
  leaf: boolean;
  constructor(leaf: boolean) { this.leaf = leaf; }
}

let splits = 0;

function splitChild(parent: BNode, i: number): void {
  const full = parent.kids[i], right = new BNode(full.leaf);
  const middle = full.keys[T - 1];           // the middle key moves up into the parent
  right.keys = full.keys.slice(T);
  full.keys = full.keys.slice(0, T - 1);
  if (!full.leaf) {
    right.kids = full.kids.slice(T);
    full.kids = full.kids.slice(0, T);
  }
  parent.kids.splice(i + 1, 0, right);
  parent.keys.splice(i, 0, middle);
  splits++;
}

function insertNonfull(node: BNode, key: number): void {
  let i = node.keys.length;
  while (i > 0 && node.keys[i - 1] > key) i--;
  if (node.leaf) {
    node.keys.splice(i, 0, key);             // keys only ever go into leaves
    return;
  }
  if (node.kids[i].keys.length === 2 * T - 1) {
    splitChild(node, i);                     // split a full child before walking into it
    if (key > node.keys[i]) i++;
  }
  insertNonfull(node.kids[i], key);
}

function insert(root: BNode, key: number): BNode {
  if (root.keys.length === 2 * T - 1) {      // a full root splits, and the tree grows one level taller
    const newRoot = new BNode(false);
    newRoot.kids = [root];
    splitChild(newRoot, 0);
    root = newRoot;
  }
  insertNonfull(root, key);
  return root;
}

function levels(root: BNode): string {
  const out: string[] = [];
  let level: BNode[] = [root];
  while (level.length) {
    out.push(level.map(n => "[" + n.keys.join(" ") + "]").join(" "));
    level = level.flatMap(n => n.kids);
  }
  return out.join("  /  ");
}

let root = new BNode(true);
for (let key = 1; key <= 10; key++) {
  root = insert(root, key);
  if ([3, 4, 6, 10].includes(key)) console.log("after", key, ":", levels(root));
}
console.log("splits:", splits, " every leaf is on the same level");
''')

t.code('disk', py=r'''
def levels_needed(n, children):
    """Fewest levels so a tree with this many children per node can hold n keys."""
    keys_per_node = children - 1
    levels, capacity, nodes = 0, 0, 1
    while capacity < n:
        levels += 1
        capacity += nodes * keys_per_node     # this level adds nodes × keys per node
        nodes *= children
    return levels


print("keys          | binary tree | B tree, 101 children | disk time at 10 ms per level")
for n in (1_000, 1_000_000, 1_000_000_000):
    b, bt = levels_needed(n, 2), levels_needed(n, 101)
    print(n, "|", b, "|", bt, "|", b * 10, "ms against", bt * 10, "ms")
''', js=r'''
function levelsNeeded(n, children) {         // fewest levels so the tree can hold n keys
  const keysPerNode = children - 1;
  let levels = 0, capacity = 0, nodes = 1;
  while (capacity < n) {
    levels++;
    capacity += nodes * keysPerNode;         // this level adds nodes × keys per node
    nodes *= children;
  }
  return levels;
}

console.log("keys          | binary tree | B tree, 101 children | disk time at 10 ms per level");
for (const n of [1000, 1000000, 1000000000]) {
  const b = levelsNeeded(n, 2), bt = levelsNeeded(n, 101);
  console.log(n, "|", b, "|", bt, "|", b * 10, "ms against", bt * 10, "ms");
}
''', java=r'''
public class DiskLevels {
    static int levelsNeeded(long n, long children) {     // fewest levels so the tree can hold n keys
        long keysPerNode = children - 1, capacity = 0, nodes = 1;
        int levels = 0;
        while (capacity < n) {
            levels++;
            capacity += nodes * keysPerNode;             // this level adds nodes × keys per node
            nodes *= children;
        }
        return levels;
    }

    public static void main(String[] args) {
        System.out.println("keys          | binary tree | B tree, 101 children | disk time at 10 ms per level");
        for (long n : new long[]{1000, 1000000, 1000000000}) {
            int b = levelsNeeded(n, 2), bt = levelsNeeded(n, 101);
            System.out.println(n + " | " + b + " | " + bt + " | " + (b * 10) + " ms against " + (bt * 10) + " ms");
        }
    }
}
''', ts=r'''
function levelsNeeded(n: number, children: number): number {   // fewest levels so the tree can hold n keys
  const keysPerNode = children - 1;
  let levels = 0, capacity = 0, nodes = 1;
  while (capacity < n) {
    levels++;
    capacity += nodes * keysPerNode;         // this level adds nodes × keys per node
    nodes *= children;
  }
  return levels;
}

console.log("keys          | binary tree | B tree, 101 children | disk time at 10 ms per level");
for (const n of [1000, 1000000, 1000000000]) {
  const b = levelsNeeded(n, 2), bt = levelsNeeded(n, 101);
  console.log(n, "|", b, "|", bt, "|", b * 10, "ms against", bt * 10, "ms");
}
''')

t.code('ordered', py=r'''
import bisect

# Python has no built in balanced tree. A sorted list with bisect answers the same questions
# (inserts cost O(n), lookups O(log n)). The sortedcontainers package is the usual upgrade.
keys = [10, 20, 30, 40, 50]


def floor(x):                                 # the biggest key <= x
    i = bisect.bisect_right(keys, x)
    return keys[i - 1] if i else None


def ceiling(x):                               # the smallest key >= x
    i = bisect.bisect_left(keys, x)
    return keys[i] if i < len(keys) else None


def between(lo, hi):                          # every key in [lo, hi], in order
    return keys[bisect.bisect_left(keys, lo):bisect.bisect_right(keys, hi)]


print("floor 25:", floor(25), " ceiling 25:", ceiling(25))
print("floor 5:", floor(5), " ceiling 55:", ceiling(55))
print("keys from 15 to 45:", " ".join(map(str, between(15, 45))))
bisect.insort(keys, 35)
print("after adding 35:", " ".join(map(str, between(15, 45))), " smallest", keys[0], " largest", keys[-1])
''', js=r'''
// JavaScript has no built in balanced tree either. A sorted array with binary search answers
// the same questions (inserts cost O(n), lookups O(log n)).
const keys = [10, 20, 30, 40, 50];

function lowerBound(x) {                     // first index with keys[i] >= x
  let lo = 0, hi = keys.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (keys[mid] < x) lo = mid + 1; else hi = mid;
  }
  return lo;
}
const upperBound = x => lowerBound(x + 1);   // first index with keys[i] > x, for whole numbers

const floor = x => { const i = upperBound(x); return i ? keys[i - 1] : null; };          // biggest key <= x
const ceiling = x => { const i = lowerBound(x); return i < keys.length ? keys[i] : null; }; // smallest key >= x
const between = (lo, hi) => keys.slice(lowerBound(lo), upperBound(hi));                   // keys in [lo, hi]

const show = v => (v === null ? "None" : v);
console.log("floor 25:", show(floor(25)), " ceiling 25:", show(ceiling(25)));
console.log("floor 5:", show(floor(5)), " ceiling 55:", show(ceiling(55)));
console.log("keys from 15 to 45:", between(15, 45).join(" "));
keys.splice(lowerBound(35), 0, 35);
console.log("after adding 35:", between(15, 45).join(" "), " smallest", keys[0], " largest", keys[keys.length - 1]);
''', java=r'''
import java.util.*;

public class OrderedMap {
    public static void main(String[] args) {
        TreeSet<Integer> keys = new TreeSet<>(List.of(10, 20, 30, 40, 50));   // a red black tree inside
        System.out.println("floor 25: " + keys.floor(25) + "  ceiling 25: " + keys.ceiling(25));
        Integer f = keys.floor(5), c = keys.ceiling(55);
        System.out.println("floor 5: " + (f == null ? "None" : f) + "  ceiling 55: " + (c == null ? "None" : c));
        StringJoiner sj = new StringJoiner(" ");
        for (int k : keys.subSet(15, true, 45, true)) sj.add(String.valueOf(k));
        System.out.println("keys from 15 to 45: " + sj);
        keys.add(35);                                    // O(log n), no shifting
        sj = new StringJoiner(" ");
        for (int k : keys.subSet(15, true, 45, true)) sj.add(String.valueOf(k));
        System.out.println("after adding 35: " + sj + "  smallest " + keys.first() + "  largest " + keys.last());
    }
}
''', ts=r'''
// TypeScript has no built in balanced tree either. A sorted array with binary search answers
// the same questions (inserts cost O(n), lookups O(log n)).
const keys: number[] = [10, 20, 30, 40, 50];

function lowerBound(x: number): number {     // first index with keys[i] >= x
  let lo = 0, hi = keys.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (keys[mid] < x) lo = mid + 1; else hi = mid;
  }
  return lo;
}
const upperBound = (x: number): number => lowerBound(x + 1);   // first index with keys[i] > x, for whole numbers

const floor = (x: number): number | null => { const i = upperBound(x); return i ? keys[i - 1] : null; };
const ceiling = (x: number): number | null => { const i = lowerBound(x); return i < keys.length ? keys[i] : null; };
const between = (lo: number, hi: number): number[] => keys.slice(lowerBound(lo), upperBound(hi));

const show = (v: number | null): string | number => (v === null ? "None" : v);
console.log("floor 25:", show(floor(25)), " ceiling 25:", show(ceiling(25)));
console.log("floor 5:", show(floor(5)), " ceiling 55:", show(ceiling(55)));
console.log("keys from 15 to 45:", between(15, 45).join(" "));
keys.splice(lowerBound(35), 0, 35);
console.log("after adding 35:", between(15, 45).join(" "), " smallest", keys[0], " largest", keys[keys.length - 1]);
''')

# ---------------------------------------------------------------- LeetCode practice programs
PY_TREE = r'''
class TreeNode:
    def __init__(self, val):
        self.val, self.left, self.right = val, None, None


def build(vals):                              # level order list with None for a missing child
    if not vals:
        return None
    root = TreeNode(vals[0])
    queue, i = [root], 1
    for node in queue:                        # the queue grows while we walk it
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            queue.append(node.right)
        i += 1
        if i >= len(vals):
            break
    return root
'''
JS_TREE = r'''
class TreeNode {
  constructor(val) { this.val = val; this.left = null; this.right = null; }
}

function build(vals) {                        // level order list with null for a missing child
  if (!vals.length) return null;
  const root = new TreeNode(vals[0]);
  const queue = [root];
  let i = 1;
  for (let q = 0; q < queue.length && i < vals.length; q++) {
    const node = queue[q];
    if (i < vals.length && vals[i] !== null) { node.left = new TreeNode(vals[i]); queue.push(node.left); }
    i++;
    if (i < vals.length && vals[i] !== null) { node.right = new TreeNode(vals[i]); queue.push(node.right); }
    i++;
  }
  return root;
}
'''
TS_TREE = r'''
class TreeNode {
  val: number;
  left: TreeNode | null = null;
  right: TreeNode | null = null;
  constructor(val: number) { this.val = val; }
}

function build(vals: (number | null)[]): TreeNode | null {   // level order list with null for a missing child
  if (!vals.length) return null;
  const root = new TreeNode(vals[0] as number);
  const queue: TreeNode[] = [root];
  let i = 1;
  for (let q = 0; q < queue.length && i < vals.length; q++) {
    const node = queue[q];
    const a = vals[i];
    if (i < vals.length && a !== null) { node.left = new TreeNode(a); queue.push(node.left); }
    i++;
    const b = vals[i];
    if (i < vals.length && b !== null && b !== undefined) { node.right = new TreeNode(b); queue.push(node.right); }
    i++;
  }
  return root;
}
'''
JAVA_TREE = r'''
    static class TreeNode {
        int val;
        TreeNode left, right;
        TreeNode(int v) { val = v; }
    }

    static TreeNode build(Integer[] vals) {          // level order list with null for a missing child
        if (vals.length == 0) return null;
        TreeNode root = new TreeNode(vals[0]);
        List<TreeNode> queue = new ArrayList<>(List.of(root));
        int i = 1;
        for (int q = 0; q < queue.size() && i < vals.length; q++) {
            TreeNode node = queue.get(q);
            if (i < vals.length && vals[i] != null) { node.left = new TreeNode(vals[i]); queue.add(node.left); }
            i++;
            if (i < vals.length && vals[i] != null) { node.right = new TreeNode(vals[i]); queue.add(node.right); }
            i++;
        }
        return root;
    }
'''

t.code('p_isbalanced', py=PY_TREE + r'''

def is_balanced(root):
    def check(node):                          # the height, or -1 as soon as some subtree is unbalanced
        if node is None:
            return 0
        lh = check(node.left)
        if lh == -1:
            return -1
        rh = check(node.right)
        if rh == -1 or abs(lh - rh) > 1:
            return -1
        return 1 + max(lh, rh)
    return check(root) != -1


for vals in ([3, 9, 20, None, None, 15, 7], [1, 2, 2, 3, 3, None, None, 4, 4], []):
    print("true" if is_balanced(build(vals)) else "false")
''', js=JS_TREE + r'''
function isBalanced(root) {
  const check = node => {                     // the height, or -1 as soon as some subtree is unbalanced
    if (node === null) return 0;
    const lh = check(node.left);
    if (lh === -1) return -1;
    const rh = check(node.right);
    if (rh === -1 || Math.abs(lh - rh) > 1) return -1;
    return 1 + Math.max(lh, rh);
  };
  return check(root) !== -1;
}

for (const vals of [[3, 9, 20, null, null, 15, 7], [1, 2, 2, 3, 3, null, null, 4, 4], []])
  console.log(isBalanced(build(vals)));
''', java=r'''
import java.util.*;

public class BalancedTree {''' + JAVA_TREE + r'''
    static int check(TreeNode node) {                // the height, or -1 as soon as some subtree is unbalanced
        if (node == null) return 0;
        int lh = check(node.left);
        if (lh == -1) return -1;
        int rh = check(node.right);
        if (rh == -1 || Math.abs(lh - rh) > 1) return -1;
        return 1 + Math.max(lh, rh);
    }

    static boolean isBalanced(TreeNode root) { return check(root) != -1; }

    public static void main(String[] args) {
        Integer[][] tests = {{3, 9, 20, null, null, 15, 7}, {1, 2, 2, 3, 3, null, null, 4, 4}, {}};
        for (Integer[] vals : tests) System.out.println(isBalanced(build(vals)));
    }
}
''', ts=TS_TREE + r'''
function isBalanced(root: TreeNode | null): boolean {
  const check = (node: TreeNode | null): number => {   // the height, or -1 as soon as some subtree is unbalanced
    if (node === null) return 0;
    const lh = check(node.left);
    if (lh === -1) return -1;
    const rh = check(node.right);
    if (rh === -1 || Math.abs(lh - rh) > 1) return -1;
    return 1 + Math.max(lh, rh);
  };
  return check(root) !== -1;
}

const tests: (number | null)[][] = [[3, 9, 20, null, null, 15, 7], [1, 2, 2, 3, 3, null, null, 4, 4], []];
for (const vals of tests) console.log(isBalanced(build(vals)));
''')

t.code('p_balancebst', py=PY_TREE + r'''

def balance_bst(root):
    keys = []
    def inorder(node):                        # a BST read in order gives its keys sorted
        if node:
            inorder(node.left)
            keys.append(node.val)
            inorder(node.right)
    def make(lo, hi):                         # the middle key becomes the root of keys[lo..hi]
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        node = TreeNode(keys[mid])
        node.left = make(lo, mid - 1)
        node.right = make(mid + 1, hi)
        return node
    inorder(root)
    return make(0, len(keys) - 1)


def levels(root):
    out, row = [], [root]
    while row:
        out.append(" ".join(str(n.val) for n in row))
        row = [c for n in row for c in (n.left, n.right) if c]
    return out


for vals in ([1, None, 2, None, 3, None, 4], [1, None, 2, None, 3, None, 4, None, 5, None, 6, None, 7]):
    before, after = levels(build(vals)), levels(balance_bst(build(vals)))
    print("height", len(before), "->", len(after), " levels:", " | ".join(after))
''', js=JS_TREE + r'''
function balanceBST(root) {
  const keys = [];
  const inorder = node => {                   // a BST read in order gives its keys sorted
    if (!node) return;
    inorder(node.left); keys.push(node.val); inorder(node.right);
  };
  const make = (lo, hi) => {                  // the middle key becomes the root of keys[lo..hi]
    if (lo > hi) return null;
    const mid = (lo + hi) >> 1;
    const node = new TreeNode(keys[mid]);
    node.left = make(lo, mid - 1);
    node.right = make(mid + 1, hi);
    return node;
  };
  inorder(root);
  return make(0, keys.length - 1);
}

function levels(root) {
  const out = [];
  let row = [root];
  while (row.length) {
    out.push(row.map(n => n.val).join(" "));
    row = row.flatMap(n => [n.left, n.right]).filter(c => c);
  }
  return out;
}

for (const vals of [[1, null, 2, null, 3, null, 4], [1, null, 2, null, 3, null, 4, null, 5, null, 6, null, 7]]) {
  const before = levels(build(vals)), after = levels(balanceBST(build(vals)));
  console.log("height", before.length, "->", after.length, " levels:", after.join(" | "));
}
''', java=r'''
import java.util.*;

public class BalanceBST {''' + JAVA_TREE + r'''
    static void inorder(TreeNode node, List<Integer> keys) {   // a BST read in order gives its keys sorted
        if (node == null) return;
        inorder(node.left, keys); keys.add(node.val); inorder(node.right, keys);
    }

    static TreeNode make(List<Integer> keys, int lo, int hi) {   // the middle key becomes the root of keys[lo..hi]
        if (lo > hi) return null;
        int mid = (lo + hi) / 2;
        TreeNode node = new TreeNode(keys.get(mid));
        node.left = make(keys, lo, mid - 1);
        node.right = make(keys, mid + 1, hi);
        return node;
    }

    static TreeNode balanceBST(TreeNode root) {
        List<Integer> keys = new ArrayList<>();
        inorder(root, keys);
        return make(keys, 0, keys.size() - 1);
    }

    static List<String> levels(TreeNode root) {
        List<String> out = new ArrayList<>();
        List<TreeNode> row = new ArrayList<>(List.of(root));
        while (!row.isEmpty()) {
            StringJoiner sj = new StringJoiner(" ");
            List<TreeNode> next = new ArrayList<>();
            for (TreeNode n : row) {
                sj.add(String.valueOf(n.val));
                if (n.left != null) next.add(n.left);
                if (n.right != null) next.add(n.right);
            }
            out.add(sj.toString());
            row = next;
        }
        return out;
    }

    public static void main(String[] args) {
        Integer[][] tests = {{1, null, 2, null, 3, null, 4}, {1, null, 2, null, 3, null, 4, null, 5, null, 6, null, 7}};
        for (Integer[] vals : tests) {
            List<String> before = levels(build(vals)), after = levels(balanceBST(build(vals)));
            System.out.println("height " + before.size() + " -> " + after.size() + "  levels: " + String.join(" | ", after));
        }
    }
}
''', ts=TS_TREE + r'''
function balanceBST(root: TreeNode | null): TreeNode | null {
  const keys: number[] = [];
  const inorder = (node: TreeNode | null): void => {   // a BST read in order gives its keys sorted
    if (!node) return;
    inorder(node.left); keys.push(node.val); inorder(node.right);
  };
  const make = (lo: number, hi: number): TreeNode | null => {   // the middle key becomes the root of keys[lo..hi]
    if (lo > hi) return null;
    const mid = (lo + hi) >> 1;
    const node = new TreeNode(keys[mid]);
    node.left = make(lo, mid - 1);
    node.right = make(mid + 1, hi);
    return node;
  };
  inorder(root);
  return make(0, keys.length - 1);
}

function levels(root: TreeNode | null): string[] {
  const out: string[] = [];
  let row: TreeNode[] = root ? [root] : [];
  while (row.length) {
    out.push(row.map(n => n.val).join(" "));
    row = row.flatMap(n => [n.left, n.right]).filter((c): c is TreeNode => c !== null);
  }
  return out;
}

const tests: (number | null)[][] = [[1, null, 2, null, 3, null, 4], [1, null, 2, null, 3, null, 4, null, 5, null, 6, null, 7]];
for (const vals of tests) {
  const before = levels(build(vals)), after = levels(balanceBST(build(vals)));
  console.log("height", before.length, "->", after.length, " levels:", after.join(" | "));
}
''')

t.code('p_calendar', py=r'''
import bisect


class MyCalendar:
    def __init__(self):
        self.starts = []                      # booking starts, kept sorted
        self.ends = []                        # ends[i] belongs to starts[i]

    def book(self, start, end):
        i = bisect.bisect_left(self.starts, start)        # the first booking that starts at or after start
        if i < len(self.starts) and self.starts[i] < end:
            return False                      # the next booking begins before this one ends
        if i > 0 and self.ends[i - 1] > start:
            return False                      # the previous booking is still running at start
        self.starts.insert(i, start)
        self.ends.insert(i, end)
        return True


cal = MyCalendar()
answers = [cal.book(s, e) for s, e in [(10, 20), (15, 25), (20, 30), (5, 10), (25, 26)]]
print(" ".join("true" if a else "false" for a in answers))
''', js=r'''
class MyCalendar {
  constructor() { this.starts = []; this.ends = []; }   // sorted starts, ends[i] belongs to starts[i]

  book(start, end) {
    let lo = 0, hi = this.starts.length;
    while (lo < hi) {                         // the first booking that starts at or after start
      const mid = (lo + hi) >> 1;
      if (this.starts[mid] < start) lo = mid + 1; else hi = mid;
    }
    if (lo < this.starts.length && this.starts[lo] < end) return false;   // the next booking begins before this one ends
    if (lo > 0 && this.ends[lo - 1] > start) return false;              // the previous booking is still running
    this.starts.splice(lo, 0, start);
    this.ends.splice(lo, 0, end);
    return true;
  }
}

const cal = new MyCalendar();
const answers = [[10, 20], [15, 25], [20, 30], [5, 10], [25, 26]].map(([s, e]) => cal.book(s, e));
console.log(answers.join(" "));
''', java=r'''
import java.util.*;

public class MyCalendar {
    TreeMap<Integer, Integer> cal = new TreeMap<>();     // start -> end, a red black tree inside

    boolean book(int start, int end) {
        Map.Entry<Integer, Integer> prev = cal.floorEntry(start);   // the booking that starts at or before start
        if (prev != null && prev.getValue() > start) return false;
        Integer next = cal.ceilingKey(start);                       // the booking that starts at or after start
        if (next != null && next < end) return false;
        cal.put(start, end);
        return true;
    }

    public static void main(String[] args) {
        MyCalendar c = new MyCalendar();
        int[][] asks = {{10, 20}, {15, 25}, {20, 30}, {5, 10}, {25, 26}};
        StringJoiner sj = new StringJoiner(" ");
        for (int[] a : asks) sj.add(String.valueOf(c.book(a[0], a[1])));
        System.out.println(sj);
    }
}
''', ts=r'''
class MyCalendar {
  starts: number[] = [];                      // booking starts, kept sorted
  ends: number[] = [];                        // ends[i] belongs to starts[i]

  book(start: number, end: number): boolean {
    let lo = 0, hi = this.starts.length;
    while (lo < hi) {                         // the first booking that starts at or after start
      const mid = (lo + hi) >> 1;
      if (this.starts[mid] < start) lo = mid + 1; else hi = mid;
    }
    if (lo < this.starts.length && this.starts[lo] < end) return false;   // the next booking begins before this one ends
    if (lo > 0 && this.ends[lo - 1] > start) return false;              // the previous booking is still running
    this.starts.splice(lo, 0, start);
    this.ends.splice(lo, 0, end);
    return true;
  }
}

const cal = new MyCalendar();
const asks: [number, number][] = [[10, 20], [15, 25], [20, 30], [5, 10], [25, 26]];
console.log(asks.map(([s, e]) => cal.book(s, e)).join(" "));
''')

t.code('p_timemap', py=r'''
import bisect


class TimeMap:
    def __init__(self):
        self.times = {}                       # key -> timestamps, sorted because they only grow
        self.values = {}                      # key -> the value stored at each timestamp

    def set(self, key, value, timestamp):
        self.times.setdefault(key, []).append(timestamp)
        self.values.setdefault(key, []).append(value)

    def get(self, key, timestamp):
        ts = self.times.get(key, [])
        i = bisect.bisect_right(ts, timestamp) - 1          # the latest time that is not after timestamp
        return self.values[key][i] if i >= 0 else ""


tm = TimeMap()
tm.set("foo", "bar", 1)
for t in (1, 3):
    print(f'get foo {t}: "{tm.get("foo", t)}"')
tm.set("foo", "bar2", 4)
for t in (4, 5, 0):
    print(f'get foo {t}: "{tm.get("foo", t)}"')
''', js=r'''
class TimeMap {
  constructor() { this.store = new Map(); }   // key -> [timestamps, values], timestamps only grow

  set(key, value, timestamp) {
    if (!this.store.has(key)) this.store.set(key, [[], []]);
    const [ts, vs] = this.store.get(key);
    ts.push(timestamp); vs.push(value);
  }

  get(key, timestamp) {
    const entry = this.store.get(key);
    if (!entry) return "";
    const [ts, vs] = entry;
    let lo = 0, hi = ts.length;
    while (lo < hi) {                         // the first time after timestamp
      const mid = (lo + hi) >> 1;
      if (ts[mid] <= timestamp) lo = mid + 1; else hi = mid;
    }
    return lo > 0 ? vs[lo - 1] : "";          // the one before it is the latest time not after timestamp
  }
}

const tm = new TimeMap();
tm.set("foo", "bar", 1);
for (const t of [1, 3]) console.log(`get foo ${t}: "${tm.get("foo", t)}"`);
tm.set("foo", "bar2", 4);
for (const t of [4, 5, 0]) console.log(`get foo ${t}: "${tm.get("foo", t)}"`);
''', java=r'''
import java.util.*;

public class TimeMap {
    Map<String, TreeMap<Integer, String>> store = new HashMap<>();   // key -> (timestamp -> value)

    void set(String key, String value, int timestamp) {
        store.computeIfAbsent(key, k -> new TreeMap<>()).put(timestamp, value);
    }

    String get(String key, int timestamp) {
        TreeMap<Integer, String> m = store.get(key);
        if (m == null) return "";
        Map.Entry<Integer, String> e = m.floorEntry(timestamp);   // the latest time that is not after timestamp
        return e == null ? "" : e.getValue();
    }

    public static void main(String[] args) {
        TimeMap tm = new TimeMap();
        tm.set("foo", "bar", 1);
        for (int t : new int[]{1, 3}) System.out.println("get foo " + t + ": \"" + tm.get("foo", t) + "\"");
        tm.set("foo", "bar2", 4);
        for (int t : new int[]{4, 5, 0}) System.out.println("get foo " + t + ": \"" + tm.get("foo", t) + "\"");
    }
}
''', ts=r'''
class TimeMap {
  store = new Map<string, [number[], string[]]>();   // key -> [timestamps, values], timestamps only grow

  set(key: string, value: string, timestamp: number): void {
    if (!this.store.has(key)) this.store.set(key, [[], []]);
    const [ts, vs] = this.store.get(key)!;
    ts.push(timestamp); vs.push(value);
  }

  get(key: string, timestamp: number): string {
    const entry = this.store.get(key);
    if (!entry) return "";
    const [ts, vs] = entry;
    let lo = 0, hi = ts.length;
    while (lo < hi) {                         // the first time after timestamp
      const mid = (lo + hi) >> 1;
      if (ts[mid] <= timestamp) lo = mid + 1; else hi = mid;
    }
    return lo > 0 ? vs[lo - 1] : "";          // the one before it is the latest time not after timestamp
  }
}

const tm = new TimeMap();
tm.set("foo", "bar", 1);
for (const t of [1, 3]) console.log(`get foo ${t}: "${tm.get("foo", t)}"`);
tm.set("foo", "bar2", 4);
for (const t of [4, 5, 0]) console.log(`get foo ${t}: "${tm.get("foo", t)}"`);
''')

t.code('p_snapshot', py=r'''
import bisect


class SnapshotArray:
    def __init__(self, length):
        self.snap_id = 0
        self.ids = [[] for _ in range(length)]     # for each index, the snap ids where it changed
        self.vals = [[] for _ in range(length)]    # and the value it had from that snap on

    def set(self, index, val):
        ids, vals = self.ids[index], self.vals[index]
        if ids and ids[-1] == self.snap_id:
            vals[-1] = val                    # several sets before one snap keep only the last
        else:
            ids.append(self.snap_id)
            vals.append(val)

    def snap(self):
        self.snap_id += 1
        return self.snap_id - 1

    def get(self, index, snap_id):
        i = bisect.bisect_right(self.ids[index], snap_id) - 1   # the last change at or before snap_id
        return self.vals[index][i] if i >= 0 else 0


arr = SnapshotArray(3)
arr.set(0, 5)
print("snap", arr.snap())
arr.set(0, 6)
print("get(0, 0) =", arr.get(0, 0))
print("snap", arr.snap())
print("get(0, 1) =", arr.get(0, 1), " get(1, 0) =", arr.get(1, 0))
arr.set(1, 7)
print("snap", arr.snap())
print("get(1, 2) =", arr.get(1, 2), " get(1, 1) =", arr.get(1, 1))
''', js=r'''
class SnapshotArray {
  constructor(length) {
    this.snapId = 0;
    this.ids = Array.from({ length }, () => []);    // for each index, the snap ids where it changed
    this.vals = Array.from({ length }, () => []);   // and the value it had from that snap on
  }

  set(index, val) {
    const ids = this.ids[index], vals = this.vals[index];
    if (ids.length && ids[ids.length - 1] === this.snapId) vals[vals.length - 1] = val;   // keep only the last set
    else { ids.push(this.snapId); vals.push(val); }
  }

  snap() { return this.snapId++; }

  get(index, snapId) {
    const ids = this.ids[index];
    let lo = 0, hi = ids.length;
    while (lo < hi) {                         // the first change after snapId
      const mid = (lo + hi) >> 1;
      if (ids[mid] <= snapId) lo = mid + 1; else hi = mid;
    }
    return lo > 0 ? this.vals[index][lo - 1] : 0;
  }
}

const arr = new SnapshotArray(3);
arr.set(0, 5);
console.log("snap", arr.snap());
arr.set(0, 6);
console.log("get(0, 0) =", arr.get(0, 0));
console.log("snap", arr.snap());
console.log("get(0, 1) =", arr.get(0, 1), " get(1, 0) =", arr.get(1, 0));
arr.set(1, 7);
console.log("snap", arr.snap());
console.log("get(1, 2) =", arr.get(1, 2), " get(1, 1) =", arr.get(1, 1));
''', java=r'''
import java.util.*;

public class SnapshotArray {
    int snapId = 0;
    List<TreeMap<Integer, Integer>> history = new ArrayList<>();   // for each index: snap id -> value

    SnapshotArray(int length) {
        for (int i = 0; i < length; i++) history.add(new TreeMap<>());
    }

    void set(int index, int val) { history.get(index).put(snapId, val); }   // a second set before a snap overwrites

    int snap() { return snapId++; }

    int get(int index, int snap) {
        Map.Entry<Integer, Integer> e = history.get(index).floorEntry(snap);   // the last change at or before snap
        return e == null ? 0 : e.getValue();
    }

    public static void main(String[] args) {
        SnapshotArray arr = new SnapshotArray(3);
        arr.set(0, 5);
        System.out.println("snap " + arr.snap());
        arr.set(0, 6);
        System.out.println("get(0, 0) = " + arr.get(0, 0));
        System.out.println("snap " + arr.snap());
        System.out.println("get(0, 1) = " + arr.get(0, 1) + "  get(1, 0) = " + arr.get(1, 0));
        arr.set(1, 7);
        System.out.println("snap " + arr.snap());
        System.out.println("get(1, 2) = " + arr.get(1, 2) + "  get(1, 1) = " + arr.get(1, 1));
    }
}
''', ts=r'''
class SnapshotArray {
  snapId = 0;
  ids: number[][];                            // for each index, the snap ids where it changed
  vals: number[][];                           // and the value it had from that snap on

  constructor(length: number) {
    this.ids = Array.from({ length }, () => []);
    this.vals = Array.from({ length }, () => []);
  }

  set(index: number, val: number): void {
    const ids = this.ids[index], vals = this.vals[index];
    if (ids.length && ids[ids.length - 1] === this.snapId) vals[vals.length - 1] = val;   // keep only the last set
    else { ids.push(this.snapId); vals.push(val); }
  }

  snap(): number { return this.snapId++; }

  get(index: number, snapId: number): number {
    const ids = this.ids[index];
    let lo = 0, hi = ids.length;
    while (lo < hi) {                         // the first change after snapId
      const mid = (lo + hi) >> 1;
      if (ids[mid] <= snapId) lo = mid + 1; else hi = mid;
    }
    return lo > 0 ? this.vals[index][lo - 1] : 0;
  }
}

const arr = new SnapshotArray(3);
arr.set(0, 5);
console.log("snap", arr.snap());
arr.set(0, 6);
console.log("get(0, 0) =", arr.get(0, 0));
console.log("snap", arr.snap());
console.log("get(0, 1) =", arr.get(0, 1), " get(1, 0) =", arr.get(1, 0));
arr.set(1, 7);
console.log("snap", arr.snap());
console.log("get(1, 2) =", arr.get(1, 2), " get(1, 1) =", arr.get(1, 1));
''')

t.code('p_calendar2', py=r'''
import bisect


class MyCalendarTwo:
    def __init__(self):
        self.keys = []                        # every start or end time, kept sorted
        self.delta = {}                       # time -> change in the number of running bookings

    def add(self, x, d):
        if x not in self.delta:
            bisect.insort(self.keys, x)
            self.delta[x] = 0
        self.delta[x] += d

    def book(self, start, end):
        self.add(start, 1)
        self.add(end, -1)
        running = 0
        for x in self.keys:                   # sweep the times from left to right
            running += self.delta[x]
            if running >= 3:
                self.add(start, -1)           # a triple booking: undo and refuse
                self.add(end, 1)
                return False
        return True


cal = MyCalendarTwo()
asks = [(10, 20), (50, 60), (10, 40), (5, 15), (5, 10), (25, 55)]
print(" ".join("true" if cal.book(s, e) else "false" for s, e in asks))
''', js=r'''
class MyCalendarTwo {
  constructor() { this.keys = []; this.delta = new Map(); }   // sorted times, time -> change in running bookings

  add(x, d) {
    if (!this.delta.has(x)) {
      let lo = 0, hi = this.keys.length;
      while (lo < hi) { const mid = (lo + hi) >> 1; if (this.keys[mid] < x) lo = mid + 1; else hi = mid; }
      this.keys.splice(lo, 0, x);
      this.delta.set(x, 0);
    }
    this.delta.set(x, this.delta.get(x) + d);
  }

  book(start, end) {
    this.add(start, 1);
    this.add(end, -1);
    let running = 0;
    for (const x of this.keys) {              // sweep the times from left to right
      running += this.delta.get(x);
      if (running >= 3) {
        this.add(start, -1); this.add(end, 1);   // a triple booking: undo and refuse
        return false;
      }
    }
    return true;
  }
}

const cal = new MyCalendarTwo();
const asks = [[10, 20], [50, 60], [10, 40], [5, 15], [5, 10], [25, 55]];
console.log(asks.map(([s, e]) => cal.book(s, e)).join(" "));
''', java=r'''
import java.util.*;

public class MyCalendarTwo {
    TreeMap<Integer, Integer> delta = new TreeMap<>();   // time -> change in running bookings, kept in time order

    boolean book(int start, int end) {
        delta.merge(start, 1, Integer::sum);
        delta.merge(end, -1, Integer::sum);
        int running = 0;
        for (int d : delta.values()) {                   // sweep the times from left to right
            running += d;
            if (running >= 3) {
                delta.merge(start, -1, Integer::sum);    // a triple booking: undo and refuse
                delta.merge(end, 1, Integer::sum);
                return false;
            }
        }
        return true;
    }

    public static void main(String[] args) {
        MyCalendarTwo cal = new MyCalendarTwo();
        int[][] asks = {{10, 20}, {50, 60}, {10, 40}, {5, 15}, {5, 10}, {25, 55}};
        StringJoiner sj = new StringJoiner(" ");
        for (int[] a : asks) sj.add(String.valueOf(cal.book(a[0], a[1])));
        System.out.println(sj);
    }
}
''', ts=r'''
class MyCalendarTwo {
  keys: number[] = [];                        // every start or end time, kept sorted
  delta = new Map<number, number>();          // time -> change in the number of running bookings

  add(x: number, d: number): void {
    if (!this.delta.has(x)) {
      let lo = 0, hi = this.keys.length;
      while (lo < hi) { const mid = (lo + hi) >> 1; if (this.keys[mid] < x) lo = mid + 1; else hi = mid; }
      this.keys.splice(lo, 0, x);
      this.delta.set(x, 0);
    }
    this.delta.set(x, this.delta.get(x)! + d);
  }

  book(start: number, end: number): boolean {
    this.add(start, 1);
    this.add(end, -1);
    let running = 0;
    for (const x of this.keys) {              // sweep the times from left to right
      running += this.delta.get(x)!;
      if (running >= 3) {
        this.add(start, -1); this.add(end, 1);   // a triple booking: undo and refuse
        return false;
      }
    }
    return true;
  }
}

const cal = new MyCalendarTwo();
const asks: [number, number][] = [[10, 20], [50, 60], [10, 40], [5, 15], [5, 10], [25, 55]];
console.log(asks.map(([s, e]) => cal.book(s, e)).join(" "));
''')

t.code('p_nearbydup', py=r'''
import bisect


def contains_nearby_almost_duplicate(nums, index_diff, value_diff):
    window = []                               # the last index_diff values, kept sorted
    for i, x in enumerate(nums):
        j = bisect.bisect_left(window, x - value_diff)      # the smallest value >= x - value_diff
        if j < len(window) and window[j] <= x + value_diff:
            return True                       # it is close enough in value and in position
        bisect.insort(window, x)
        if len(window) > index_diff:
            del window[bisect.bisect_left(window, nums[i - index_diff])]   # too far back now
    return False


for nums, k, v in (([1, 2, 3, 1], 3, 0), ([1, 5, 9, 1, 5, 9], 2, 3), ([1, 5, 9, 13], 1, 4)):
    print("true" if contains_nearby_almost_duplicate(nums, k, v) else "false")
''', js=r'''
function lowerBound(a, x) {                   // the first index with a[i] >= x
  let lo = 0, hi = a.length;
  while (lo < hi) { const mid = (lo + hi) >> 1; if (a[mid] < x) lo = mid + 1; else hi = mid; }
  return lo;
}

function containsNearbyAlmostDuplicate(nums, indexDiff, valueDiff) {
  const window = [];                          // the last indexDiff values, kept sorted
  for (let i = 0; i < nums.length; i++) {
    const x = nums[i];
    const j = lowerBound(window, x - valueDiff);   // the smallest value >= x - valueDiff
    if (j < window.length && window[j] <= x + valueDiff) return true;
    window.splice(lowerBound(window, x), 0, x);
    if (window.length > indexDiff) window.splice(lowerBound(window, nums[i - indexDiff]), 1);   // too far back now
  }
  return false;
}

for (const [nums, k, v] of [[[1, 2, 3, 1], 3, 0], [[1, 5, 9, 1, 5, 9], 2, 3], [[1, 5, 9, 13], 1, 4]])
  console.log(containsNearbyAlmostDuplicate(nums, k, v));
''', java=r'''
import java.util.*;

public class NearbyAlmostDuplicate {
    static boolean containsNearbyAlmostDuplicate(int[] nums, int indexDiff, int valueDiff) {
        TreeSet<Long> window = new TreeSet<>();                  // the last indexDiff values, a red black tree
        for (int i = 0; i < nums.length; i++) {
            long x = nums[i];
            Long c = window.ceiling(x - valueDiff);              // the smallest value >= x - valueDiff
            if (c != null && c <= x + valueDiff) return true;
            window.add(x);
            if (window.size() > indexDiff) window.remove((long) nums[i - indexDiff]);   // too far back now
        }
        return false;
    }

    public static void main(String[] args) {
        System.out.println(containsNearbyAlmostDuplicate(new int[]{1, 2, 3, 1}, 3, 0));
        System.out.println(containsNearbyAlmostDuplicate(new int[]{1, 5, 9, 1, 5, 9}, 2, 3));
        System.out.println(containsNearbyAlmostDuplicate(new int[]{1, 5, 9, 13}, 1, 4));
    }
}
''', ts=r'''
function lowerBound(a: number[], x: number): number {   // the first index with a[i] >= x
  let lo = 0, hi = a.length;
  while (lo < hi) { const mid = (lo + hi) >> 1; if (a[mid] < x) lo = mid + 1; else hi = mid; }
  return lo;
}

function containsNearbyAlmostDuplicate(nums: number[], indexDiff: number, valueDiff: number): boolean {
  const window: number[] = [];                // the last indexDiff values, kept sorted
  for (let i = 0; i < nums.length; i++) {
    const x = nums[i];
    const j = lowerBound(window, x - valueDiff);   // the smallest value >= x - valueDiff
    if (j < window.length && window[j] <= x + valueDiff) return true;
    window.splice(lowerBound(window, x), 0, x);
    if (window.length > indexDiff) window.splice(lowerBound(window, nums[i - indexDiff]), 1);   // too far back now
  }
  return false;
}

const tests: [number[], number, number][] = [[[1, 2, 3, 1], 3, 0], [[1, 5, 9, 1, 5, 9], 2, 3], [[1, 5, 9, 13], 1, 4]];
for (const [nums, k, v] of tests) console.log(containsNearbyAlmostDuplicate(nums, k, v));
''')

t.code('p_intervals', py=r'''
import bisect


class SummaryRanges:
    def __init__(self):
        self.starts = []                      # interval starts, kept sorted
        self.ends = []                        # ends[i] belongs to starts[i]

    def add_num(self, v):
        i = bisect.bisect_right(self.starts, v)   # intervals before i start at or before v
        if i > 0 and self.ends[i - 1] >= v:
            return                            # v is already inside an interval
        join_left = i > 0 and self.ends[i - 1] == v - 1
        join_right = i < len(self.starts) and self.starts[i] == v + 1
        if join_left and join_right:          # v glues two intervals into one
            self.ends[i - 1] = self.ends[i]
            del self.starts[i], self.ends[i]
        elif join_left:
            self.ends[i - 1] = v
        elif join_right:
            self.starts[i] = v
        else:
            self.starts.insert(i, v)
            self.ends.insert(i, v)

    def get_intervals(self):
        return [[s, e] for s, e in zip(self.starts, self.ends)]


sr = SummaryRanges()
for v in (1, 3, 7, 2, 6):
    sr.add_num(v)
    print(f"add {v}:", " ".join(f"[{s},{e}]" for s, e in sr.get_intervals()))
''', js=r'''
class SummaryRanges {
  constructor() { this.starts = []; this.ends = []; }   // sorted starts, ends[i] belongs to starts[i]

  addNum(v) {
    let lo = 0, hi = this.starts.length;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (this.starts[mid] <= v) lo = mid + 1; else hi = mid; }
    const i = lo;                             // intervals before i start at or before v
    if (i > 0 && this.ends[i - 1] >= v) return;   // v is already inside an interval
    const joinLeft = i > 0 && this.ends[i - 1] === v - 1;
    const joinRight = i < this.starts.length && this.starts[i] === v + 1;
    if (joinLeft && joinRight) {              // v glues two intervals into one
      this.ends[i - 1] = this.ends[i];
      this.starts.splice(i, 1); this.ends.splice(i, 1);
    } else if (joinLeft) this.ends[i - 1] = v;
    else if (joinRight) this.starts[i] = v;
    else { this.starts.splice(i, 0, v); this.ends.splice(i, 0, v); }
  }

  getIntervals() { return this.starts.map((s, i) => [s, this.ends[i]]); }
}

const sr = new SummaryRanges();
for (const v of [1, 3, 7, 2, 6]) {
  sr.addNum(v);
  console.log(`add ${v}:`, sr.getIntervals().map(([s, e]) => `[${s},${e}]`).join(" "));
}
''', java=r'''
import java.util.*;

public class SummaryRanges {
    TreeMap<Integer, Integer> map = new TreeMap<>();   // interval start -> end, kept in order

    void addNum(int v) {
        Integer lo = map.floorKey(v);                  // the interval that starts at or before v
        if (lo != null && map.get(lo) >= v) return;    // v is already inside an interval
        boolean joinLeft = lo != null && map.get(lo) == v - 1;
        boolean joinRight = map.containsKey(v + 1);
        if (joinLeft && joinRight) map.put(lo, map.remove(v + 1));   // v glues two intervals into one
        else if (joinLeft) map.put(lo, v);
        else if (joinRight) map.put(v, map.remove(v + 1));
        else map.put(v, v);
    }

    List<int[]> getIntervals() {
        List<int[]> out = new ArrayList<>();
        for (Map.Entry<Integer, Integer> e : map.entrySet()) out.add(new int[]{e.getKey(), e.getValue()});
        return out;
    }

    public static void main(String[] args) {
        SummaryRanges sr = new SummaryRanges();
        for (int v : new int[]{1, 3, 7, 2, 6}) {
            sr.addNum(v);
            StringJoiner sj = new StringJoiner(" ");
            for (int[] p : sr.getIntervals()) sj.add("[" + p[0] + "," + p[1] + "]");
            System.out.println("add " + v + ": " + sj);
        }
    }
}
''', ts=r'''
class SummaryRanges {
  starts: number[] = [];                      // interval starts, kept sorted
  ends: number[] = [];                        // ends[i] belongs to starts[i]

  addNum(v: number): void {
    let lo = 0, hi = this.starts.length;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (this.starts[mid] <= v) lo = mid + 1; else hi = mid; }
    const i = lo;                             // intervals before i start at or before v
    if (i > 0 && this.ends[i - 1] >= v) return;   // v is already inside an interval
    const joinLeft = i > 0 && this.ends[i - 1] === v - 1;
    const joinRight = i < this.starts.length && this.starts[i] === v + 1;
    if (joinLeft && joinRight) {              // v glues two intervals into one
      this.ends[i - 1] = this.ends[i];
      this.starts.splice(i, 1); this.ends.splice(i, 1);
    } else if (joinLeft) this.ends[i - 1] = v;
    else if (joinRight) this.starts[i] = v;
    else { this.starts.splice(i, 0, v); this.ends.splice(i, 0, v); }
  }

  getIntervals(): number[][] { return this.starts.map((s, i) => [s, this.ends[i]]); }
}

const sr = new SummaryRanges();
for (const v of [1, 3, 7, 2, 6]) {
  sr.addNum(v);
  console.log(`add ${v}:`, sr.getIntervals().map(([s, e]) => `[${s},${e}]`).join(" "));
}
''')

t.leet(110, 'e', 'p_isbalanced', title='Balanced Binary Tree', url='https://leetcode.com/problems/balanced-binary-tree/', diff='Easy',
       statement='<p>Given a binary tree, decide whether it is height balanced: at every node, the heights of the left and right subtrees differ by at most one.</p>',
       example='[3,9,20,null,null,15,7]        →  true\n[1,2,2,3,3,null,null,4,4]      →  false\n[]                             →  true',
       hint='Compute heights bottom up, and stop as soon as one subtree fails.',
       approach='<p>Write one helper that returns the height of a subtree, or −1 when the subtree is already unbalanced. A node checks its left side, then its right side, and returns −1 if either failed or if the two heights differ by more than one. Every node is visited once, which is the same check an AVL tree keeps true after every insert.</p>',
       time='O(n)', space='O(h) for the recursion')
t.leet(1382, 'e', 'p_balancebst', title='Balance a Binary Search Tree', url='https://leetcode.com/problems/balance-a-binary-search-tree/', diff='Medium',
       statement='<p>Given a binary search tree, return a balanced search tree with the same keys. Any balanced answer is accepted.</p>',
       example='1 → 2 → 3 → 4 (a chain)     →  2 | 1 3 | 4\nthe chain 1 to 7             →  4 | 2 6 | 1 3 5 7',
       hint='An in order walk gives the keys sorted. Then build from the middle.',
       approach='<p>Read the keys in order into a list, which comes out sorted. Make the middle key the root, build the left half from the keys before it and the right half from the keys after it. Each half is split the same way, so the height becomes about log₂ n. The middle is chosen with <code>(lo + hi) // 2</code> in every language, so all four print the same tree.</p>',
       time='O(n)', space='O(n)')
t.leet(729, 'm', 'p_calendar',
       statement='<p>Build a calendar that accepts a booking [start, end) only if it does not overlap any booking already accepted.</p>',
       example='book(10,20) true, book(15,25) false, book(20,30) true\nbook(5,10) true, book(25,26) false',
       hint='Only two bookings can clash: the one just before the new start and the one just after it.',
       approach='<p>Keep bookings ordered by start. Find the first booking that starts at or after the new start. It clashes if it starts before the new end. The booking before it clashes if it ends after the new start. Java asks its red black <code>TreeMap</code> with <code>floorEntry</code> and <code>ceilingKey</code>, so each booking costs O(log n). Python and JavaScript find the spot with binary search on a sorted list, but inserting into a list still shifts items, O(n).</p>',
       time='O(log n) with TreeMap, O(n) with a sorted list', space='O(n)')
t.leet(981, 'm', 'p_timemap',
       statement='<p>Store values per key with a timestamp. <code>get(key, t)</code> returns the value set at the largest timestamp that is not after t, or an empty string.</p>',
       example='set(foo, bar, 1)\nget(foo, 1) "bar"  get(foo, 3) "bar"\nset(foo, bar2, 4)\nget(foo, 4) "bar2"  get(foo, 5) "bar2"  get(foo, 0) ""',
       hint='This is a floor question: the biggest timestamp that is at most t.',
       approach='<p>The problem promises that timestamps for set only grow, so appending keeps each key\'s list sorted. A get is a binary search for the last timestamp at most t. Java stores a <code>TreeMap</code> per key and calls <code>floorEntry(t)</code>, which is the same floor query the ordered map lesson showed.</p>',
       time='O(1) set, O(log n) get', space='O(n)')
t.leet(1146, 'h', 'p_snapshot',
       statement='<p>Build an array that supports <code>set(index, val)</code>, <code>snap()</code> which returns a snapshot id, and <code>get(index, snap_id)</code> which returns the value at that index when that snapshot was taken.</p>',
       example='SnapshotArray(3), set(0,5), snap() 0, set(0,6), get(0,0) 5',
       hint='Do not copy the whole array per snap. Store only the changes, per index.',
       approach='<p>For each index, keep the snap ids where it changed and the value from then on. Several sets before one snap only keep the last value. A get finds the last change at or before the requested snap id with binary search, and an index that never changed returns 0. Java keeps one <code>TreeMap</code> per index and uses <code>floorEntry</code>.</p>',
       time='O(1) set and snap, O(log s) get', space='O(number of sets)')
t.leet(731, 'h', 'p_calendar2',
       statement='<p>Build a calendar that allows a double booking but refuses any booking that would cause a triple booking.</p>',
       example='book(10,20) true, book(50,60) true, book(10,40) true\nbook(5,15) false, book(5,10) true, book(25,55) true',
       hint='Mark +1 where a booking starts and −1 where it ends, then sweep the times in order.',
       approach='<p>Keep an ordered map from time to the change in running bookings. A new booking adds +1 at its start and −1 at its end. Sweep the times from left to right and add up the changes. If the running count ever reaches 3, undo the two marks and refuse. Java\'s <code>TreeMap</code> keeps the times in order for free. Python and JavaScript keep a sorted list of times next to a hash map.</p>',
       time='O(n) per booking', space='O(n)')
t.leet(220, 'x', 'p_nearbydup', title='Contains Duplicate III', url='https://leetcode.com/problems/contains-duplicate-iii/', diff='Hard',
       statement='<p>Return true if two different indexes i and j exist with |i − j| ≤ indexDiff and |nums[i] − nums[j]| ≤ valueDiff.</p>',
       example='[1,2,3,1], 3, 0          →  true\n[1,5,9,1,5,9], 2, 3      →  false\n[1,5,9,13], 1, 4          →  true',
       hint='Keep the last indexDiff values in an ordered set and ask for a ceiling.',
       approach='<p>Slide a window of the last indexDiff values, kept in order. For each new x, ask for the smallest value in the window that is at least x − valueDiff. If it exists and is at most x + valueDiff, the answer is true. Then add x and drop the value that fell out of the window. Java\'s <code>TreeSet</code> does each step in O(log k) and uses <code>long</code> so x − valueDiff cannot overflow. Python and JavaScript use a sorted list with binary search, where each insert or delete shifts up to k items.</p>',
       time='O(n log k) with TreeSet, O(n k) with a sorted list', space='O(k)')
t.leet(352, 'x', 'p_intervals',
       statement='<p>Numbers arrive one by one. After each one, report the numbers seen so far as a list of disjoint intervals.</p>',
       example='add 1  [1,1]\nadd 3  [1,1] [3,3]\nadd 7  [1,1] [3,3] [7,7]\nadd 2  [1,3] [7,7]\nadd 6  [1,3] [6,7]',
       hint='A new number can only touch the interval just before it and the interval just after it.',
       approach='<p>Keep the intervals ordered by start. Find the interval that starts at or before v. If it already covers v, nothing changes. Otherwise check whether v extends the interval on its left, the one on its right, or glues both into one. If it touches neither, it becomes a new interval of its own. Java uses <code>TreeMap.floorKey</code>. Python and JavaScript use binary search on two parallel sorted lists.</p>',
       time='O(log n) with TreeMap, O(n) with sorted lists', space='O(n)')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='why-balance', emoji='⚖️', title='Why balance matters', html='''
<p>The Trees chapter showed that a binary search tree is only fast when it is short. Insert keys that are already sorted and every new key becomes a right child. The tree turns into a chain, and a search walks every node. A <b>self balancing</b> tree does a little extra work after each insert so that its height stays close to log₂ n, whatever order the keys arrive in.</p>
<div class="viz" data-viz="pk" data-pk="chain"></div>
<div class="c3" data-k="chain" data-label="Sorted keys into a plain tree and an AVL tree"></div>
<span class="eq">best possible height = ⌈log₂(n + 1)⌉ &nbsp;&nbsp; 1000 keys → 10 levels</span>
<div class="rule">Search, insert and delete all cost O(height). Keeping the height at O(log n) is the whole point of every tree in this chapter.</div>
'''),
    dict(id='avl', emoji='🔄', title='Rotations and AVL trees', html='''
<p>An <b>AVL tree</b> stores the height of every node. The <b>balance factor</b> is the left height minus the right height, and it must stay at −1, 0 or +1. After an insert, walk back up. The first node that reaches ±2 is fixed with a <b>rotation</b>, which lifts one child up and moves the parent down, while keeping every key in search order.</p>
<div class="viz" data-viz="pk" data-pk="avl"></div>
<div class="c3" data-k="avl" data-label="AVL insert that names each rotation"></div>
<div class="tw"><table class="jt"><tr><th>Case</th><th>The new key went</th><th>Fix</th></tr>
<tr><td>LL</td><td>left, then left</td><td>rotate right at the unbalanced node</td></tr>
<tr><td>RR</td><td>right, then right</td><td>rotate left at the unbalanced node</td></tr>
<tr><td>LR</td><td>left, then right</td><td>rotate left at the child, then right at the node</td></tr>
<tr><td>RL</td><td>right, then left</td><td>rotate right at the child, then left at the node</td></tr></table></div>
<div class="exam">An AVL tree with n keys is never taller than about 1.44 log₂ n. One insert needs at most one single or one double rotation.</div>
'''),
    dict(id='red-black', emoji='🔴', title='Red black trees, the left leaning way', html='''
<p>A <b>red black tree</b> colours each node red or black and keeps two rules. No red node has a red child, and every path from the root down to an empty spot passes the same number of black nodes. Together they keep the longest path at most twice the shortest, so the height is at most 2 log₂(n + 1).</p>
<p>The <b>left leaning</b> version, described by Robert Sedgewick in 2008, adds one more rule: a red link always leans left. Then an insert needs only three small fixes, checked on the way back up.</p>
<div class="viz" data-viz="pk" data-pk="llrb"></div>
<div class="c3" data-k="llrb" data-label="Left leaning red black insert"></div>
<div class="tw"><table class="jt"><tr><th>You see</th><th>Fix</th></tr>
<tr><td>a red right child and a black left child</td><td>rotate left</td></tr>
<tr><td>a red left child whose left child is red too</td><td>rotate right</td></tr>
<tr><td>both children red</td><td>flip colours: children turn black, the node turns red</td></tr></table></div>
<div class="tip">Java's <code>TreeMap</code> and <code>TreeSet</code> are red black trees. Red black trees rotate less often than AVL trees when keys change a lot, which is why libraries tend to pick them.</div>
'''),
    dict(id='b-tree', emoji='🧱', title='B trees: many keys per node', html='''
<p>A <b>B tree</b> lets one node hold many sorted keys and have one more child than it has keys. With minimum degree t, every node except the root holds between t − 1 and 2t − 1 keys. Here t = 2, so each node holds 1 to 3 keys. When a node on the way down is full, it splits: the middle key moves up into the parent. The tree only grows taller when the root splits, so <b>every leaf stays on the same level</b>.</p>
<div class="viz" data-viz="pk" data-pk="btree"></div>
<div class="c3" data-k="btree" data-label="B tree insert with minimum degree 2"></div>
<span class="eq">keys per node: t − 1 … 2t − 1 &nbsp;&nbsp; children per node: t … 2t</span>
<div class="exam">A B tree with t = 2 is also called a 2-3-4 tree. A left leaning red black tree is a binary way of drawing a 2-3 tree, where a red link glues two keys into one node.</div>
'''),
    dict(id='b-plus', emoji='💾', title='B+ trees, disks and databases', html='''
<p>Reading from a disk is slow compared with memory, so the number of nodes read matters more than the work inside a node. A B tree node is sized to fill one disk page, so a node can have hundreds of children and the tree stays only a few levels tall.</p>
<div class="c3" data-k="disk" data-label="How many levels a lookup reads"></div>
<p>Databases mostly use the <b>B+ tree</b> variant. Internal nodes hold only signposts that guide the search. Every real key and record sits in a leaf, and the leaves are linked in order. A range query walks down once, then slides along the leaves without climbing back up.</p>
<div class="viz" data-viz="pk" data-pk="bplus"></div>
<div class="tip">MySQL's InnoDB, PostgreSQL and SQLite all keep their indexes in B tree variants. File systems such as Btrfs, XFS and NTFS use them to find files and blocks.</div>
'''),
    dict(id='ordered', emoji='🗂️', title='Ordered maps in each language', html='''
<p>You rarely write a balanced tree yourself. You use the ordered map or set your language provides, and ask it questions a hash map cannot answer: the smallest key, the biggest key, the <b>floor</b> (biggest key at most x), the <b>ceiling</b> (smallest key at least x), and every key in a range.</p>
<div class="viz" data-viz="pk" data-pk="ordered"></div>
<div class="c3" data-k="ordered" data-label="Floor, ceiling and range queries"></div>
<div class="tw"><table class="jt"><tr><th>Language</th><th>What to use</th><th>Insert</th></tr>
<tr><td>Java</td><td><code>TreeMap</code>, <code>TreeSet</code>: <code>floorKey</code>, <code>ceilingKey</code>, <code>subMap</code></td><td class="yes">O(log n)</td></tr>
<tr><td>Python</td><td>a sorted list with <code>bisect</code>, or the third party <code>sortedcontainers</code></td><td>O(n) shift for a plain list</td></tr>
<tr><td>JavaScript, TypeScript</td><td>a sorted array with your own binary search</td><td>O(n) shift</td></tr></table></div>
<div class="warn">A sorted list answers floor and ceiling in O(log n), but each insert shifts items. That is fine for thousands of keys and slow for millions of changing keys, where a real balanced tree wins.</div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem is solved in the Practice section in Python, JavaScript, Java and TypeScript, with line by line replay. Java uses its red black <code>TreeMap</code> and <code>TreeSet</code>. Python, JavaScript and TypeScript use sorted lists with binary search.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>The ordered idea</th></tr>
<tr><td><a href="#lc110">110. Balanced Binary Tree</a></td><td>Easy</td><td>the AVL height rule</td></tr>
<tr><td><a href="#lc1382">1382. Balance a Binary Search Tree</a></td><td>Easy</td><td>sorted keys, root from the middle</td></tr>
<tr><td><a href="#lc729">729. My Calendar I</a></td><td>Medium</td><td>floor and ceiling of a start time</td></tr>
<tr><td><a href="#lc981">981. Time Based Key-Value Store</a></td><td>Medium</td><td>floor of a timestamp</td></tr>
<tr><td><a href="#lc1146">1146. Snapshot Array</a></td><td>Hard</td><td>floor of a snap id, per index</td></tr>
<tr><td><a href="#lc731">731. My Calendar II</a></td><td>Hard</td><td>an ordered sweep of start and end marks</td></tr>
<tr><td><a href="#lc220">220. Contains Duplicate III</a></td><td>Expert</td><td>a sliding ordered set and a ceiling</td></tr>
<tr><td><a href="#lc352">352. Data Stream as Disjoint Intervals</a></td><td>Expert</td><td>intervals ordered by start</td></tr></table></div>
'''),
]

VIZ_JS = r'''
(() => {
  const D = PK.defs;
  const okKeys = (s, lo, hi) => { const a = PK.parseList(s); return a && a.length >= lo && a.length <= hi && a.every(x => Number.isInteger(x) && x >= 0 && x <= 99) && new Set(a).size === a.length ? a : null; };
  const shuffleSome = (n, top) => { const a = []; while (a.length < n) { const x = 1 + Math.floor(Math.random() * top); if (!a.includes(x)) a.push(x); } return a.join(', '); };

  /* ---------- AVL helpers, shared by the chain and AVL widgets ---------- */
  const ht = n => n ? n.h : 0;
  const fix = n => { n.h = 1 + Math.max(ht(n.l), ht(n.r)); return n; };
  const bf = n => ht(n.l) - ht(n.r);
  const rotR = y => { const x = y.l; y.l = x.r; x.r = y; fix(y); return fix(x); };
  const rotL = x => { const y = x.r; x.r = y.l; y.l = x; fix(x); return fix(y); };
  const clone = n => n && { k: n.k, h: n.h, l: clone(n.l), r: clone(n.r), red: n.red };
  const plainInsert = (n, k) => {               /* an ordinary BST insert that only updates heights */
    if (!n) return { k, l: null, r: null, h: 1, red: true };
    if (k < n.k) n.l = plainInsert(n.l, k); else n.r = plainInsert(n.r, k);
    return fix(n);
  };
  const avlInsert = (root, k) => {
    let info = null;
    const go = n => {
      if (!n) return { k, l: null, r: null, h: 1 };
      if (k < n.k) n.l = go(n.l); else n.r = go(n.r);
      fix(n);
      const b = bf(n);
      if (b > 1) {
        if (k < n.l.k) { info = { kind: 'LL', at: n.k, sub: n.l.k }; return rotR(n); }
        info = { kind: 'LR', at: n.k, sub: n.l.k }; n.l = rotL(n.l); return rotR(n);
      }
      if (b < -1) {
        if (k > n.r.k) { info = { kind: 'RR', at: n.k, sub: n.r.k }; return rotL(n); }
        info = { kind: 'RL', at: n.k, sub: n.r.k }; n.r = rotR(n.r); return rotL(n);
      }
      return n;
    };
    return { root: go(root), info };
  };
  const levelsOf = root => { const out = []; let row = root ? [root] : []; while (row.length) { out.push(row); row = row.flatMap(n => [n.l, n.r]).filter(Boolean); } return out; };

  /* a binary tree drawn as a graph: ncls and tags are keyed by the node's key */
  const treePic = (root, label, opt = {}) => {
    if (!root) return { t: 'note', html: 'The tree is empty.' };
    const kids = {}, ncls = {}, tag = {}, ecls = {};
    let depth = 0;
    const walk = (n, d) => {
      if (!n) return;
      depth = Math.max(depth, d + 1);
      const id = 'n' + n.k;
      kids[id] = [n.l ? 'n' + n.l.k : null, n.r ? 'n' + n.r.k : null];
      const c = [opt.rb ? (n.red ? 'rb-r' : 'rb-b') : '', (opt.cls || {})[n.k] || ''].join(' ').trim();
      if (c) ncls[id] = c;
      if (opt.tag) tag[id] = opt.tag(n);
      if (opt.rb) [n.l, n.r].forEach(ch => { if (ch && ch.red) ecls[id + '-n' + ch.k] = 'rb-r'; });
      walk(n.l, d + 1); walk(n.r, d + 1);
    };
    walk(root, 0);
    const W = opt.w || 460, H = 52 * depth + (opt.tag ? 26 : 12);
    const L = PK.treeLayout(kids, 'n' + root.k, id => id.slice(1), W, H);
    return { t: 'graph', label, w: W, h: H, nodes: L.nodes, edges: L.edges, ncls, ecls, tag };
  };
  const sign = b => b > 0 ? '+' + b : b < 0 ? '−' + (-b) : '0';

  /* ---------- a plain BST against an AVL tree ---------- */
  D.chain = el => PK.widget(el, {
    title: 'Sorted keys: chain or bush', sub: 'The same keys go into a plain search tree and into an AVL tree. Watch the heights.',
    inputs: [{ k: 'keys', label: 'Insert in this order', type: 'text', val: '1, 2, 3, 4, 5, 6, 7', w: 220 }],
    random: () => ({ keys: Math.random() < 0.5 ? '1, 2, 3, 4, 5, 6, 7, 8' : shuffleSome(8, 40) }),
    check: v => okKeys(v.keys, 2, 8) ? '' : 'Give two to eight different whole numbers from 0 to 99.',
    frames: ({ keys }) => {
      const ks = okKeys(keys, 2, 8), F = [];
      let plain = null, avl = null;
      for (const k of ks) {
        plain = plainInsert(plain, k);
        avl = avlInsert(avl, k).root;
        const pH = ht(plain), aH = ht(avl);
        F.push({
          mood: pH > aH + 1 ? 'sad' : 'look',
          msg: `Insert ${k}. Plain tree height <b>${pH}</b>, AVL tree height <b>${aH}</b>.${pH > aH + 1 ? ' The plain tree is leaning more and more.' : ''}`,
          vars: { plain: pH, AVL: aH },
          layers: [treePic(plain, 'Plain search tree', { w: 300, cls: { [k]: 'look' } }), treePic(avl, 'AVL tree, rebalanced after every insert', { w: 360, cls: { [k]: 'yes' } })]
        });
      }
      const pH = ht(plain), aH = ht(avl), sorted = ks.every((x, i) => !i || ks[i - 1] < x);
      F.push({
        mood: 'wow', fx: 'rain',
        msg: sorted ? `Sorted input turned the plain tree into a chain of height ${pH}, no better than a linked list. The AVL tree stayed at height ${aH}, close to log₂ n.` : `Plain tree height ${pH}, AVL tree height ${aH}. Random order is kinder to a plain tree, but only an AVL tree promises O(log n) every time.`,
        vars: { plain: pH, AVL: aH },
        layers: [treePic(plain, 'Plain search tree', { w: 300 }), treePic(avl, 'AVL tree', { w: 360, cls: { [avl.k]: 'yes' } })]
      });
      return F;
    }
  });

  /* ---------- AVL rotations ---------- */
  const caseText = {
    LL: (z, y) => `The new key went left of ${z}, then left of ${y}: case <b>LL</b>. One right rotation at ${z} lifts ${y} up.`,
    RR: (z, y) => `The new key went right of ${z}, then right of ${y}: case <b>RR</b>. One left rotation at ${z} lifts ${y} up.`,
    LR: (z, y) => `The new key went left of ${z}, then right of ${y}: case <b>LR</b>. Rotate left at ${y}, then right at ${z}.`,
    RL: (z, y) => `The new key went right of ${z}, then left of ${y}: case <b>RL</b>. Rotate right at ${y}, then left at ${z}.`,
  };
  D.avl = el => PK.widget(el, {
    title: 'AVL rotations', sub: 'Each node shows its balance factor, left height minus right height. A ±2 triggers a rotation.',
    inputs: [{ k: 'keys', label: 'Insert in this order', type: 'text', val: '10, 20, 30, 40, 50, 25', w: 220 }],
    random: () => ({ keys: shuffleSome(7, 60) }),
    check: v => okKeys(v.keys, 1, 9) ? '' : 'Give one to nine different whole numbers from 0 to 99.',
    frames: ({ keys }) => {
      const ks = okKeys(keys, 1, 9), F = [], tag = n => sign(bf(n));
      let root = null, rotations = 0;
      for (const k of ks) {
        const before = plainInsert(clone(root), k);
        const res = avlInsert(root, k);
        root = res.root;
        if (!res.info) {
          F.push({ mood: 'happy', msg: `Insert ${k}. Every balance factor is −1, 0 or +1, so no rotation is needed.`, vars: { rotations }, layers: [treePic(root, 'AVL tree', { tag, cls: { [k]: 'yes' } })] });
          continue;
        }
        const { kind, at, sub } = res.info;
        F.push({ mood: 'think', fx: 'shake', msg: `Insert ${k}. Node ${at} now has balance factor <b>${sign(bf(findNode(before, at)))}</b>. ${caseText[kind](at, sub)}`, vars: { rotations, case: kind }, layers: [treePic(before, 'Before the fix', { tag, cls: { [k]: 'look', [at]: 'no', [sub]: 'cur' } })] });
        rotations += kind.length === 2 && kind[0] !== kind[1] ? 2 : 1;
        F.push({ mood: 'wow', fx: 'burst', msg: `${kind === 'LL' || kind === 'RR' ? 'One rotation' : 'Two rotations'} later the subtree is balanced again and still a valid search tree.`, vars: { rotations, case: kind }, layers: [treePic(root, 'After the rotation', { tag, cls: { [k]: 'yes', [at]: 'mv', [sub]: 'mv' } })] });
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `${ks.length} keys, height <b>${ht(root)}</b>, ${rotations} rotation${rotations === 1 ? '' : 's'}. Levels: ${levelsOf(root).map(r => r.map(n => n.k).join(' ')).join(' | ')}.`, vars: { rotations, height: ht(root) }, layers: [treePic(root, 'Final AVL tree', { tag })] });
      return F;
    }
  });
  const findNode = (n, k) => { while (n && n.k !== k) n = k < n.k ? n.l : n.r; return n; };

  /* ---------- left leaning red black tree ---------- */
  const isRed = n => !!n && n.red;
  const rbRotL = h => { const x = h.r; h.r = x.l; x.l = h; x.red = h.red; h.red = true; return x; };
  const rbRotR = h => { const x = h.l; h.l = x.r; x.r = h; x.red = h.red; h.red = true; return x; };
  const rbPut = (root, k, ops) => {
    const ins = h => {
      if (!h) return { k, l: null, r: null, red: true };
      if (k < h.k) h.l = ins(h.l); else if (k > h.k) h.r = ins(h.r);
      if (isRed(h.r) && !isRed(h.l)) { ops.push(`rotate left at ${h.k}`); h = rbRotL(h); }
      if (isRed(h.l) && isRed(h.l.l)) { ops.push(`rotate right at ${h.k}`); h = rbRotR(h); }
      if (isRed(h.l) && isRed(h.r)) { ops.push(`flip colours at ${h.k}`); h.red = true; h.l.red = false; h.r.red = false; }
      return h;
    };
    const r = ins(root);
    if (r.red) ops.push(`paint the root ${r.k} black`);
    r.red = false;
    return r;
  };
  const blackHeight = n => { let b = 0; while (n) { if (!n.red) b++; n = n.l; } return b; };
  const depthOf = n => n ? 1 + Math.max(depthOf(n.l), depthOf(n.r)) : 0;
  D.llrb = el => PK.widget(el, {
    title: 'Red black tree, left leaning', sub: 'A new key always arrives red. Three small fixes keep red links leaning left and never two in a row.',
    inputs: [{ k: 'keys', label: 'Insert in this order', type: 'text', val: '1, 2, 3, 4, 5, 6, 7, 8, 9, 10', w: 240 }],
    random: () => ({ keys: shuffleSome(9, 60) }),
    check: v => okKeys(v.keys, 1, 12) ? '' : 'Give one to twelve different whole numbers from 0 to 99.',
    frames: ({ keys }) => {
      const ks = okKeys(keys, 1, 12), F = [];
      let root = null;
      for (const k of ks) {
        const before = plainInsert(clone(root), k);
        const ops = [];
        root = rbPut(root, k, ops);
        F.push({ mood: 'look', msg: `Insert ${k} as a <b>red</b> leaf, linked to its parent by a red link.`, vars: { 'black height': blackHeight(root) }, layers: [treePic(before, 'New red leaf', { rb: true, cls: { [k]: 'hl' } })] });
        F.push({
          mood: ops.length ? 'work' : 'happy', fx: ops.some(o => o.startsWith('rotate')) ? 'burst' : undefined,
          msg: ops.length ? `Fixes on the way back up: ${ops.join(', ')}.` : 'No fix needed. The red link already leans left on its own.',
          vars: { 'black height': blackHeight(root), height: depthOf(root) },
          layers: [treePic(root, 'After the fixes', { rb: true, cls: { [k]: 'hl' } })]
        });
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `${ks.length} keys, height <b>${depthOf(root)}</b>. Every path from the root to an empty spot crosses the same ${blackHeight(root)} black links, so no path is more than twice as long as another.`, vars: { 'black height': blackHeight(root), height: depthOf(root) }, layers: [treePic(root, 'Final red black tree', { rb: true })] });
      return F;
    }
  });

  /* ---------- B tree, minimum degree 2 ---------- */
  D.btree = el => PK.widget(el, {
    title: 'B tree insert with splits', sub: 'Each node holds one to three keys. A full node is split on the way down, and only the root split makes the tree taller.',
    inputs: [{ k: 'keys', label: 'Insert in this order', type: 'text', val: '1, 2, 3, 4, 5, 6, 7, 8, 9, 10', w: 240 }],
    random: () => ({ keys: shuffleSome(11, 80) }),
    check: v => okKeys(v.keys, 1, 14) ? '' : 'Give one to fourteen different whole numbers from 0 to 99.',
    frames: ({ keys }) => {
      const ks = okKeys(keys, 1, 14), F = [];
      let root = { keys: [], kids: [] }, splits = 0;
      const pic = (cls = new Map(), hk) => {
        const rows = [];
        let lv = [root];
        while (lv.length) { rows.push(lv); lv = lv.flatMap(n => n.kids); }
        return rows.map((r, d) => ({
          t: 'row', idx: false, label: d === 0 ? (rows.length === 1 ? 'Root, also a leaf' : 'Root') : d === rows.length - 1 ? 'Leaves, all on one level' : `Level ${d + 1}`,
          cells: r.map(n => n.keys.join(' · ') || '·'),
          cls: Object.fromEntries(r.map((n, i) => [i, cls.get(n) || (hk !== undefined && !n.kids.length && n.keys.includes(hk) ? 'yes' : '')]))
        }));
      };
      const split = (parent, i) => {
        const child = parent.kids[i], mid = child.keys[1];
        const right = { keys: child.keys.slice(2), kids: child.kids.slice(2) };
        child.keys = child.keys.slice(0, 1);
        child.kids = child.kids.slice(0, 2);
        parent.keys.splice(i, 0, mid);
        parent.kids.splice(i + 1, 0, right);
        splits++;
        return [mid, child, right];
      };
      for (const k of ks) {
        if (root.keys.length === 3) {
          F.push({ mood: 'think', msg: `Insert ${k}. The root [${root.keys.join(' ')}] is full, so it splits first.`, vars: { splits }, layers: pic(new Map([[root, 'no']])) });
          const top = { keys: [], kids: [root] };
          root = top;
          const [mid, a, b] = split(top, 0);
          F.push({ mood: 'wow', fx: 'burst', msg: `${mid} moves up into a brand new root. The tree just grew one level taller, and it grew at the top.`, vars: { splits }, layers: pic(new Map([[top, 'yes'], [a, 'mv'], [b, 'mv']])) });
        }
        let node = root;
        while (node.kids.length) {
          let i = node.keys.filter(x => x < k).length;
          if (node.kids[i].keys.length === 3) {
            F.push({ mood: 'think', msg: `On the way down to place ${k}, child [${node.kids[i].keys.join(' ')}] is full. Split it before entering.`, vars: { splits }, layers: pic(new Map([[node, 'look'], [node.kids[i], 'no']])) });
            const [mid, a, b] = split(node, i);
            F.push({ mood: 'work', msg: `${mid} moves up into the parent, which had room for it.`, vars: { splits }, layers: pic(new Map([[node, 'yes'], [a, 'mv'], [b, 'mv']])) });
            if (k > node.keys[i]) i++;
          }
          node = node.kids[i];
        }
        node.keys.push(k);
        node.keys.sort((x, y) => x - y);
        F.push({ mood: 'happy', msg: `${k} slides into the leaf [${node.keys.join(' ')}] in sorted order.`, vars: { splits }, layers: pic(new Map(), k) });
      }
      let levels = 0;
      for (let n = root; n; n = n.kids[0]) levels++;
      F.push({ mood: 'wow', fx: 'rain', msg: `${ks.length} keys in ${levels} level${levels === 1 ? '' : 's'} after ${splits} split${splits === 1 ? '' : 's'}. Every leaf sits on the same level, which a B tree always guarantees.`, vars: { splits, levels }, layers: pic() });
      return F;
    }
  });

  /* ---------- B+ tree range scan ---------- */
  D.bplus = el => PK.widget(el, {
    title: 'B+ tree range scan', sub: 'All keys live in the leaves, and the leaves are linked. Walk down once, then slide along.',
    inputs: [{ k: 'keys', label: 'Keys', type: 'text', val: '5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60', w: 260 },
             { k: 'lo', label: 'From', type: 'num', val: 18, min: 0, max: 99, w: 70 }, { k: 'hi', label: 'To', type: 'num', val: 42, min: 0, max: 99, w: 70 }],
    random: () => { const lo = 5 + Math.floor(Math.random() * 30); return { keys: '5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60', lo, hi: lo + 10 + Math.floor(Math.random() * 25) }; },
    check: v => okKeys(v.keys, 4, 18) && Number.isInteger(v.lo) && Number.isInteger(v.hi) && v.lo <= v.hi ? '' : 'Give four to eighteen different whole numbers, and a range where From is not bigger than To.',
    frames: ({ keys, lo, hi }) => {
      const ks = okKeys(keys, 4, 18).slice().sort((a, b) => a - b), F = [];
      const chunk = (a, s) => {                 /* split into groups of at most s, with sizes as even as possible */
        const g = Math.ceil(a.length / s), o = [];
        let i = 0;
        for (let j = 0; j < g; j++) { const n = Math.floor(a.length / g) + (j < a.length % g ? 1 : 0); o.push(a.slice(i, i + n)); i += n; }
        return o;
      };
      const leaves = chunk(ks, 3).map(c => ({ keys: c }));
      const levels = [leaves];
      const minKey = n => n.kids ? minKey(n.kids[0]) : n.keys[0];
      while (levels[0].length > 1) levels.unshift(chunk(levels[0], 3).map(c => ({ kids: c, keys: c.slice(1).map(minKey) })));
      let reads = 0;
      const pic = (hl = new Map(), leafCls = {}, cur) => {
        const out = levels.slice(0, -1).map((lv, d) => ({ t: 'row', idx: false, label: d === 0 ? 'Root: signposts only' : `Level ${d + 1}: signposts`, cells: lv.map(n => n.keys.join(' · ')), cls: Object.fromEntries(lv.map((n, i) => [i, hl.get(n) || ''])) }));
        const cells = [], cls = {};
        leaves.forEach((lf, j) => { cells.push(lf.keys.join(' · ')); cls[cells.length - 1] = hl.get(lf) || ''; if (j < leaves.length - 1) { cells.push('→'); cls[cells.length - 1] = 'lnk'; } });
        out.push({ t: 'row', idx: false, label: 'Leaves, linked left to right', cells, cls });
        if (cur) out.push({ t: 'row', label: 'Keys in this leaf', cells: cur.keys, cls: leafCls, idx: false });
        return out;
      };
      F.push({ mood: 'think', msg: `Find every key from ${lo} to ${hi}. The top levels only hold signposts. Every real key sits in a leaf.`, vars: { 'node reads': reads }, layers: pic() });
      let node = levels[0][0];
      while (node.kids) {
        reads++;
        const i = node.keys.filter(s => s <= lo).length;
        F.push({ mood: 'look', msg: `Signposts [${node.keys.join(' ')}]: ${i === 0 ? `${lo} is below ${node.keys[0]}, so take the first child` : `${lo} ≥ ${node.keys[i - 1]}, so take child ${i + 1}`}.`, vars: { 'node reads': reads }, layers: pic(new Map([[node, 'look']])) });
        node = node.kids[i];
      }
      const found = [];
      let li = leaves.indexOf(node), done = false;
      while (!done && li < leaves.length) {
        const lf = leaves[li];
        reads++;
        const lc = {};
        for (let j = 0; j < lf.keys.length && !done; j++) {
          const x = lf.keys[j];
          if (x < lo) lc[j] = 'done';
          else if (x <= hi) { lc[j] = 'yes'; found.push(x); }
          else { lc[j] = 'no'; done = true; }
        }
        F.push({ mood: found.length ? 'happy' : 'look', msg: done ? `Reached ${lf.keys.find(x => x > hi)}, which is past ${hi}. Stop here.` : `Read this leaf.${found.length ? ' Collected so far: ' + found.join(', ') + '.' : ''}${li < leaves.length - 1 ? ' Follow the link to the next leaf.' : ' That was the last leaf.'}`, vars: { 'node reads': reads, found: found.length }, layers: pic(new Map([[lf, done ? 'no' : 'cur']]), lc, lf) });
        li++;
      }
      F.push(found.length
        ? { mood: 'wow', fx: 'rain', msg: `Found <b>${found.join(', ')}</b> with ${reads} node reads. One walk down plus a slide along the leaves, with no climbing back up.`, vars: { 'node reads': reads, found: found.length }, layers: pic(new Map(leaves.filter(l => l.keys.some(x => x >= lo && x <= hi)).map(l => [l, 'yes']))) }
        : { mood: 'sad', fx: 'shake', msg: `No key falls between ${lo} and ${hi}. The search still cost only ${reads} node reads to be sure.`, vars: { 'node reads': reads, found: 0 }, layers: pic() });
      return F;
    }
  });

  /* ---------- ordered map queries with binary search ---------- */
  D.ordered = el => PK.widget(el, {
    title: 'Floor and ceiling', sub: 'Floor is the biggest key at most x. Ceiling is the smallest key at least x. Binary search finds the spot.',
    inputs: [{ k: 'keys', label: 'Keys', type: 'text', val: '10, 20, 30, 40, 50', w: 200 }, { k: 'x', label: 'x', type: 'num', val: 25, min: 0, max: 99, w: 70 },
             { k: 'op', label: 'Ask for', type: 'seg', val: 'floor', opts: [['floor', '⬇️ Floor'], ['ceiling', '⬆️ Ceiling']] }],
    random: () => ({ keys: shuffleSome(7, 90), x: Math.floor(Math.random() * 100), op: Math.random() < 0.5 ? 'floor' : 'ceiling' }),
    check: v => okKeys(v.keys, 1, 12) && Number.isInteger(v.x) ? '' : 'Give one to twelve different whole numbers and a whole number x.',
    frames: ({ keys, x, op }) => {
      const a = okKeys(keys, 1, 12).slice().sort((p, q) => p - q), F = [];
      const floor = op === 'floor';
      let lo = 0, hi = a.length, steps = 0;
      F.push({ mood: 'think', msg: `The keys are kept sorted, as a balanced tree or a sorted list keeps them. Look for the first key ${floor ? 'bigger than' : 'at least'} ${x}.`, vars: { steps }, layers: [{ t: 'row', label: 'Sorted keys', cells: a, ptr: { 0: 'lo' } }] });
      while (lo < hi) {
        const mid = (lo + hi) >> 1;
        steps++;
        const goRight = floor ? a[mid] <= x : a[mid] < x;
        const cls = {};
        for (let i = 0; i < a.length; i++) if (i < lo || i >= hi) cls[i] = 'done';
        cls[mid] = 'look';
        F.push({ mood: 'look', msg: `Middle key ${a[mid]} ${goRight ? (floor ? '≤' : '<') : (floor ? '>' : '≥')} ${x}, so the answer spot is ${goRight ? 'to the right' : 'here or to the left'}.`, vars: { steps }, layers: [{ t: 'row', label: 'Sorted keys', cells: a, cls, ptr: { [mid]: 'mid' } }] });
        if (goRight) lo = mid + 1; else hi = mid;
      }
      const ans = floor ? lo - 1 : lo;
      const ok = ans >= 0 && ans < a.length;
      const cls = Object.fromEntries(a.map((_, i) => [i, i === ans ? 'yes' : 'done']));
      F.push(ok
        ? { mood: 'wow', fx: 'burst', msg: `The ${op} of ${x} is <b>${a[ans]}</b>, found in ${steps} step${steps === 1 ? '' : 's'}.`, vars: { steps, [op]: a[ans] }, layers: [{ t: 'row', label: 'Sorted keys', cells: a, cls, ptr: { [ans]: op } }] }
        : { mood: 'sad', fx: 'shake', msg: `No key is ${floor ? 'at most' : 'at least'} ${x}. The ${op} does not exist, so Python prints None and Java returns null.`, vars: { steps, [op]: 'none' }, layers: [{ t: 'row', label: 'Sorted keys', cells: a, cls: Object.fromEntries(a.map((_, i) => [i, 'no'])) }] });
      return F;
    }
  });
})();
'''

INFO = {
    'title': 'Short trees stay fast',
    'panels': [
        {'s': [['e', '🔄'], ['t', '|left h − right h| ≤ 1', {'b': 1}]], 'h': 'AVL tree', 't': 'Rotations fix any ±2.', 'more': 'Height at most about 1.44 log₂ n.'},
        {'s': [['e', '🔴'], ['t', 'no red red, equal black', {'b': 1}]], 'h': 'Red black tree', 't': 'Colours limit the longest path.', 'more': 'Height at most 2 log₂(n + 1). Java TreeMap.'},
        {'s': [['e', '🧱'], ['t', 't − 1 … 2t − 1 keys', {'b': 1}]], 'h': 'B tree', 't': 'Wide nodes, few levels.', 'more': 'All leaves on one level. Grows at the root.'},
        {'s': [['e', '💾'], ['t', 'keys in linked leaves', {'b': 1}]], 'h': 'B+ tree', 't': 'Walk down once, slide along.', 'more': 'The index inside most databases.'},
    ],
    'remember': 'Every balanced tree keeps search, insert and delete at O(log n) by limiting the height. In memory you use an ordered map such as Java TreeMap or a sorted list with bisect. On disk the node is sized to a page and the tree becomes a B+ tree.',
}

REAL = [
    ['🗄️', 'A database index', 'When a query asks for orders between two dates, the database walks down a B+ tree index once and then reads the linked leaves in order.'],
    ['📅', 'A booking system', 'To check a new booking, a calendar only needs the booking just before it and the one just after it, which is a floor and a ceiling query on an ordered map.'],
    ['🐧', 'The Linux kernel', 'The kernel ships its own red black tree library, and its process scheduler uses one to pick the next task to run.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to balanced and disk trees. A search tree is only fast when it is short. In this chapter you will see why sorted input ruins a plain tree, how AVL rotations and red black colours keep a tree short, how B trees pack many keys into one node for disks, how B plus trees power database indexes, and how to use the ordered maps your language already has.'},
    {'id': 'why-balance', 'h': 'Why balance matters', 'en': 'Insert sorted keys into a plain search tree and each one becomes a right child, so the tree becomes a chain as tall as the number of keys. A self balancing tree does a little extra work after each insert and keeps its height close to log n. For a thousand keys that means ten levels instead of a thousand.'},
    {'id': 'avl', 'h': 'AVL trees', 'en': 'An AVL tree keeps the heights of the two subtrees of every node within one of each other. After an insert, walk back up and look for the first node whose balance factor reached plus two or minus two. Name the case from the two steps the new key took: left left, right right, left right or right left. One or two rotations put the subtree back in balance.'},
    {'id': 'red-black', 'h': 'Red black trees', 'en': 'A red black tree colours nodes red or black. No red node may have a red child, and every path down passes the same number of black nodes. In the left leaning version a red link must also lean left. A new key arrives red, and on the way back up there are only three fixes: rotate left, rotate right, or flip the colours.'},
    {'id': 'b-tree', 'h': 'B trees', 'en': 'A B tree node holds several sorted keys and has one more child than keys. When a full node is met on the way down, it splits and its middle key moves up into the parent. The tree only gets taller when the root itself splits, so all the leaves always stay on the same level.'},
    {'id': 'b-plus', 'h': 'B plus trees', 'en': 'On a disk, every node read is slow, so nodes are made as big as a disk page and hold hundreds of keys. A billion keys then fit in about five levels. A B plus tree keeps all real keys in the leaves and links the leaves in order, so a range query walks down once and then slides along the leaves.'},
    {'id': 'ordered', 'h': 'Ordered maps', 'en': 'You rarely write a balanced tree by hand. Java gives you TreeMap and TreeSet, which are red black trees. In Python, JavaScript and TypeScript you can keep a sorted list and use binary search. Ordered maps answer questions a hash map cannot: the floor, the ceiling, the smallest, the biggest, and every key in a range.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from checking whether a tree is balanced to merging a stream of numbers into intervals. Each one is solved in Python, JavaScript, Java and TypeScript, and you can replay every solution line by line.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. For each problem, ask which ordered question it really needs, such as the key just before a value, the key just after it, or every key in a range. Then write the code. Open the hint if you are stuck.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'You insert 1, 2, 3, 4, 5 into a plain binary search tree. What is its height?', 'o': ['2', '3', '5', '1'], 'a': 2, 'hint': 'Each key is bigger than all the ones before it.', 'why': 'Every key becomes the right child of the previous one, so the tree is a chain of 5 levels.'},
    {'lv': 'e', 'q': 'What values can an AVL balance factor take without a rotation?', 'o': ['0 only', '−1, 0 or +1', '−2 to +2', 'Any value'], 'a': 1, 'hint': 'The two subtree heights may differ by at most one.', 'why': 'A balance factor of ±2 or more triggers a rotation.'},
    {'lv': 'e', 'q': 'Which Java class is a red black tree?', 'o': ['HashMap', 'TreeMap', 'ArrayList', 'PriorityQueue'], 'a': 1, 'hint': 'It keeps keys in sorted order.', 'why': 'TreeMap and TreeSet are built on a red black tree.'},
    {'lv': 'e', 'q': 'Where do all the leaves of a B tree sit?', 'o': ['On different levels', 'On the same level', 'Only on the left', 'In the root'], 'a': 1, 'hint': 'The tree only grows at the root.', 'why': 'Splits push keys up, and only a root split adds a level, so every leaf stays at the same depth.'},
    {'lv': 'm', 'q': 'Inserting 10, 20, 30 into an empty AVL tree causes which case?', 'o': ['LL', 'RR', 'LR', 'RL'], 'a': 1, 'hint': 'The new key went right of 10, then right of 20.', 'why': 'Right then right is case RR, fixed by one left rotation at 10.'},
    {'lv': 'm', 'q': 'Inserting 30, 10, 20 into an empty AVL tree causes which case?', 'o': ['LL', 'RR', 'LR', 'RL'], 'a': 2, 'hint': '20 goes left of 30, then right of 10.', 'why': 'Left then right is case LR. Rotate left at 10, then right at 30, and 20 becomes the root.'},
    {'lv': 'm', 'q': 'In a left leaning red black tree, a node has a red right child and a black left child. What is the fix?', 'o': ['Rotate right', 'Rotate left', 'Flip colours', 'Nothing'], 'a': 1, 'hint': 'Red links must lean left.', 'why': 'A rotate left turns the right leaning red link into a left leaning one.'},
    {'lv': 'm', 'q': 'A B tree has minimum degree t = 3. At most how many keys can one node hold?', 'o': ['3', '4', '5', '6'], 'a': 2, 'hint': '2t − 1.', 'why': '2 × 3 − 1 = 5 keys, with up to 6 children.'},
    {'lv': 'h', 'q': 'Why do databases use B+ trees instead of binary trees for indexes?', 'o': ['They use less memory in total', 'Each node read from disk holds many keys, so a lookup reads only a few nodes', 'They never need splits', 'They are easier to code'], 'a': 1, 'hint': 'Count the disk reads.', 'why': 'A disk page holds hundreds of keys, so a billion keys need about five levels instead of thirty.'},
    {'lv': 'h', 'q': 'In a B+ tree, where are the actual records or full keys stored?', 'o': ['In the root', 'In the internal nodes', 'In the leaves', 'In a separate hash table'], 'a': 2, 'hint': 'The upper levels only guide the search.', 'why': 'Internal nodes hold signposts, and every key lives in a leaf. The leaves are linked for range scans.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'import bisect\nkeys = [10, 20, 30, 40]\ni = bisect.bisect_right(keys, 25)\nprint(keys[i - 1], keys[i])', 'o': ['20 30', '30 40', '10 20', '20 20'], 'a': 0, 'hint': 'bisect_right gives the first index with a key bigger than 25.', 'why': 'i = 2. keys[1] = 20 is the floor and keys[2] = 30 is the ceiling.'},
    {'lv': 'h', 'q': 'Every root to empty spot path in a red black tree has 3 black nodes. What is the longest such path possible?', 'o': ['3', '4', '6', '9'], 'a': 2, 'hint': 'Reds cannot sit next to each other.', 'why': 'Reds can at most alternate with the 3 blacks, so the longest path has 6 nodes, twice the shortest.'},
    {'lv': 'x', 'q': 'What is the smallest number of nodes an AVL tree of height 4 can have?', 'o': ['4', '7', '8', '15'], 'a': 1, 'hint': 'N(h) = N(h − 1) + N(h − 2) + 1, with N(1) = 1 and N(2) = 2.', 'why': 'N(3) = 2 + 1 + 1 = 4 and N(4) = 4 + 2 + 1 = 7.'},
    {'lv': 'x', 'q': 'In the B tree lesson with t = 2, inserting 1 to 10 in order causes how many splits?', 'o': ['3', '4', '5', '6'], 'a': 2, 'hint': 'Run the B tree lesson program or the animation.', 'why': 'The program prints splits: 5, with the final levels [4] / [2] [6 8] / [1] [3] [5] [7] [9 10].'},
    {'lv': 'x', 'q': 'Contains Duplicate III keeps a window of the last k values in an ordered set. Which query decides the answer for a new value x?', 'o': ['The maximum of the window', 'The ceiling of x − valueDiff', 'The floor of x + k', 'The size of the window'], 'a': 1, 'hint': 'You want the smallest value that is not too far below x.', 'why': 'If the smallest value at least x − valueDiff is also at most x + valueDiff, a close pair exists.'},
    {'lv': 'x', 'q': 'Why does a sorted Python list make My Calendar I cost O(n) per booking while Java TreeMap costs O(log n)?', 'o': ['bisect is slower than a tree search', 'Inserting into the middle of a list shifts the items after it', 'Python has no binary search', 'TreeMap skips the overlap check'], 'a': 1, 'hint': 'Finding the spot is fast in both. What about putting the key there?', 'why': 'bisect finds the spot in O(log n), but list.insert moves every later item. A balanced tree inserts in O(log n).'},
]

CALC = [
    {'lv': 'e', 'q': 'A node\'s left subtree has height 3 and its right subtree has height 1. What is its balance factor?', 'ans': '2', 'hint': 'Left height minus right height.', 'steps': ['<span class="eq">3 − 1 = 2</span>', 'It is +2, so an AVL tree must rotate here.']},
    {'lv': 'e', 'q': 'What is the smallest possible height of a binary tree with 15 nodes?', 'ans': '4', 'hint': '⌈log₂(n + 1)⌉.', 'steps': ['<span class="eq">⌈log₂ 16⌉ = 4</span>']},
    {'lv': 'm', 'q': 'A B tree has minimum degree t = 3. At most how many children can a node have?', 'ans': '6', 'hint': '2t.', 'steps': ['<span class="eq">2 × 3 = 6</span>']},
    {'lv': 'm', 'q': 'A B tree node has 1000 children. How many levels are needed for 1,000,000 keys?', 'ans': '2', 'hint': 'The smallest L with 1000^L ≥ 1,000,000.', 'steps': ['<span class="eq">1000¹ = 1000 &lt; 1,000,000</span>', '<span class="eq">1000² = 1,000,000 ≥ 1,000,000</span>, so 2 levels.']},
    {'lv': 'h', 'q': 'What is the smallest number of nodes in an AVL tree of height 5?', 'ans': '12', 'hint': 'N(h) = N(h − 1) + N(h − 2) + 1.', 'steps': ['N(1) = 1, N(2) = 2, N(3) = 4, N(4) = 7.', '<span class="eq">N(5) = 7 + 4 + 1 = 12</span>']},
    {'lv': 'h', 'q': 'A red black tree has black height 3. At least how many nodes does it hold?', 'ans': '7', 'hint': 'A subtree of black height b holds at least 2^b − 1 nodes.', 'steps': ['<span class="eq">2³ − 1 = 7</span>']},
    {'lv': 'x', 'q': 'What is the smallest number of nodes in an AVL tree of height 6?', 'ans': '20', 'hint': 'Continue from N(5) = 12 and N(4) = 7.', 'steps': ['<span class="eq">N(6) = 12 + 7 + 1 = 20</span>']},
    {'lv': 'x', 'q': 'The disk lesson program uses 10 ms per level. How many ms does a binary tree lookup in a billion keys take?', 'ans': '300', 'hint': 'Run the disk lesson program. A binary tree needs 30 levels.', 'steps': ['2³⁰ is about 1.07 billion, so 30 levels.', '<span class="eq">30 × 10 = 300 ms</span>, against 50 ms for the B tree with 101 children.']},
]

TALK = {
    'why-balance': 'Let us start with the problem every tree in this chapter solves. A binary search tree is fast because each comparison throws away half of the remaining keys. That only works when the tree is short and bushy. Now insert the keys one, two, three, four and so on, in sorted order. Each new key is bigger than everything already there, so it always goes to the right. After a thousand keys the tree is a thousand levels tall, and finding the last key means checking every single node. That is no better than a linked list. A self balancing tree fixes this. After each insert it checks whether the shape has become lopsided, and if so it moves a few nodes around. For those same thousand sorted keys, an AVL tree ends up only ten levels tall. Run the animation and watch the plain tree lean while the balanced one stays short.',
    'avl': 'An AVL tree is named after its two inventors, Adelson-Velsky and Landis, who described it in 1962. Every node remembers its height. The balance factor of a node is the height of its left subtree minus the height of its right subtree. The rule is simple: every balance factor must be minus one, zero or plus one. After you insert a key, walk back up toward the root. The first node that reaches plus two or minus two needs a fix. Look at the two steps the new key took below that node. Left then left is the LL case, fixed by one right rotation. Right then right is the RR case, fixed by one left rotation. The mixed cases, left right and right left, need two rotations. A rotation only changes three links, so it costs constant time, and the keys stay in search order the whole time.',
    'red-black': 'A red black tree takes a different approach. Instead of storing heights, it paints every node red or black and keeps two rules. A red node never has a red child, and every path from the root down to an empty spot passes the same number of black nodes. Those rules mean the longest path is at most twice the shortest, so the height stays within about two log n. The left leaning version, published by Robert Sedgewick, adds a third rule: red links always lean to the left. That makes insert very short to write. A new key is always added as a red leaf. On the way back up, three checks run at every node. A red right child gets a left rotation. Two reds in a row on the left get a right rotation. Two red children get a colour flip. Finally the root is painted black.',
    'b-tree': 'Binary trees give each node one key and two children. A B tree gives each node many keys and many children. With a minimum degree of two, every node holds one, two or three keys, and a node with three keys has four children. To insert, walk down from the root to a leaf. If you meet a node that is already full, split it before you enter. The middle key moves up into the parent, and the remaining keys become two smaller nodes. Because of this early split, the parent always has room. The leaf at the bottom then takes the new key in sorted order. The only way the tree can get taller is when the root splits, and that adds a level at the top. So every leaf is always on the same level. Watch the animation insert one to ten and count the five splits.',
    'b-plus': 'Why do databases care so much about B trees? Because reading data from a disk is slow compared with reading it from memory, and each node usually lives in its own block on the disk. What matters is how many nodes you read, not how much work you do inside one node. If a node fills a whole disk page, it can hold hundreds of keys. The disk lesson program shows the effect. A billion keys need thirty levels in a binary tree, but only five levels in a B tree with about a hundred children per node. Most databases use the B plus tree version. The upper levels hold only signposts, and every real key lives in a leaf. The leaves are linked from left to right, so a range query, such as all orders from last week, walks down once and then reads the leaves in order.',
    'ordered': 'In everyday code you almost never write an AVL or red black tree yourself. You use the ordered structure your language gives you. In Java that is TreeMap for key value pairs and TreeSet for plain keys. Both are red black trees, and they offer handy methods like floorKey, ceilingKey, firstKey, lastKey and subMap. Python and JavaScript do not have a balanced tree built in. The usual answer is a sorted list together with binary search. In Python the bisect module does the searching for you. Finding a floor or a ceiling is fast, about log n steps. The cost shows up when you insert, because every item after the insert point has to shift. For a few thousand keys that is perfectly fine. For millions of keys that change all the time, a real balanced tree, or the sortedcontainers package in Python, is the better choice.',
    'leetcode': 'The LeetCode problems in this chapter practise both halves of the chapter. You begin by checking whether a tree is balanced, using the same height rule an AVL tree keeps, and by rebuilding a lopsided search tree from its sorted keys. The medium problems are calendar and time based stores, where the whole trick is asking for the booking or timestamp just before or just after a value. The hard problems add snapshots of an array, and a calendar that allows double bookings but refuses triple ones, which you solve by sweeping start and end marks in order. The expert problems slide an ordered window over an array to find nearby values, and merge a stream of numbers into disjoint intervals. Java solves each one with TreeMap or TreeSet. Python, JavaScript and TypeScript use sorted lists with binary search.',
}

T = t.finish({
    'slug': 'balanced-trees', 'title': 'Balanced and Disk Trees', 'short': 'Balanced trees', 'emoji': '🔄', 'topic': 'balanced-trees', 'prefix': 'dsabal',
    'module': ('🌳', 'Trees and graphs'),
    'lead': 'A search tree is only fast when it is short. Watch sorted keys ruin a plain tree, AVL rotations and red black colours keep a tree short, B trees split their way to perfect balance, and a B+ tree scan a range the way a database does.',
    'desc': 'Balanced trees in DSA: why balance matters, AVL rotations, left leaning red black trees, B trees, B+ trees for disks and databases, and ordered maps with floor and ceiling, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 24,
    'summary': 'Why sorted input ruins a plain search tree, AVL rotations, left leaning red black trees, B tree splits, B+ trees and disk levels, and ordered maps with floor, ceiling and range queries. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['balanced tree', 'self balancing', 'AVL tree', 'rotation', 'balance factor', 'red black tree', 'left leaning red black', 'B tree', 'B+ tree', '2-3-4 tree', 'database index', 'TreeMap', 'TreeSet', 'bisect', 'floor', 'ceiling', 'ordered map'],
    'added': '2026-11-23',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS,
    'css': '.pk-row{justify-content:center} .pk-n.rb-r circle{fill:#e5484d; stroke:#a8282d} .pk-n.rb-r text{fill:#fff} .pk-n.rb-b circle{fill:#2b2b33; stroke:#8a8a96} .pk-n.rb-b text{fill:#fff} .pk-e.rb-r{stroke:#e5484d; stroke-width:4.5} .pk-n.hl circle{stroke:var(--accent); stroke-width:5; r:21px} .pk-cell.lnk{border:0; background:none; min-width:18px; padding:0; color:var(--ink2)}',
    'prev': ('heaps', 'heaps', '⛰️ Heaps in depth'),
    'next': ('graphs', 'graphs', '🕸️ Graphs'),
})
