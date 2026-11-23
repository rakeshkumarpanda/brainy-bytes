# Special data structures: skip lists, Bloom filters, count-min sketches, sparse tables and square root decomposition.
from kit4 import Topic

t = Topic()

# ---------------------------------------------------------------- lesson programs
t.code('skiplist', py=r'''
MAX_LEVEL = 4
seed = 7


def coin():                                      # a tiny repeatable random generator, so every language agrees
    global seed
    seed = (seed * 75 + 74) % 65537
    return seed % 2


class SkipNode:
    def __init__(self, key, level):
        self.key = key
        self.next = [None] * level               # one forward link per lane


class SkipList:
    def __init__(self):
        self.head = SkipNode(None, MAX_LEVEL)
        self.level = 1

    def insert(self, key):
        update, x = [self.head] * MAX_LEVEL, self.head
        for lv in range(self.level - 1, -1, -1):  # run right along a lane, then drop down
            while x.next[lv] and x.next[lv].key < key:
                x = x.next[lv]
            update[lv] = x
        lvl = 1
        while lvl < MAX_LEVEL and coin():         # heads: the new key also joins the lane above
            lvl += 1
        self.level = max(self.level, lvl)
        node = SkipNode(key, lvl)
        for lv in range(lvl):
            node.next[lv] = update[lv].next[lv]
            update[lv].next[lv] = node

    def search(self, key):
        x, moves = self.head, 0
        for lv in range(self.level - 1, -1, -1):
            while x.next[lv] and x.next[lv].key < key:
                x = x.next[lv]
                moves += 1
        x = x.next[0]
        return x is not None and x.key == key, moves

    def lanes(self):
        out = []
        for lv in range(self.level - 1, -1, -1):
            keys, x = [], self.head.next[lv]
            while x:
                keys.append(x.key)
                x = x.next[lv]
            out.append((lv, keys))
        return out


sl = SkipList()
for k in [3, 6, 7, 9, 12, 19, 17, 26, 21, 25]:
    sl.insert(k)
for lv, keys in sl.lanes():
    print(f"lane {lv}: {keys}")
for k in (19, 5):
    found, moves = sl.search(k)
    print(f"search {k}: {'found' if found else 'not found'}, right moves made: {moves}")
''', js=r'''
const MAX_LEVEL = 4;
let seed = 7;

function coin() {                                    // a tiny repeatable random generator, so every language agrees
  seed = (seed * 75 + 74) % 65537;
  return seed % 2;
}

class SkipNode {
  constructor(key, level) { this.key = key; this.next = new Array(level).fill(null); }   // one link per lane
}

class SkipList {
  constructor() { this.head = new SkipNode(null, MAX_LEVEL); this.level = 1; }

  insert(key) {
    const update = new Array(MAX_LEVEL).fill(this.head);
    let x = this.head;
    for (let lv = this.level - 1; lv >= 0; lv--) {   // run right along a lane, then drop down
      while (x.next[lv] && x.next[lv].key < key) x = x.next[lv];
      update[lv] = x;
    }
    let lvl = 1;
    while (lvl < MAX_LEVEL && coin()) lvl++;         // heads: the new key also joins the lane above
    this.level = Math.max(this.level, lvl);
    const node = new SkipNode(key, lvl);
    for (let lv = 0; lv < lvl; lv++) { node.next[lv] = update[lv].next[lv]; update[lv].next[lv] = node; }
  }

  search(key) {
    let x = this.head, moves = 0;
    for (let lv = this.level - 1; lv >= 0; lv--) {
      while (x.next[lv] && x.next[lv].key < key) { x = x.next[lv]; moves++; }
    }
    x = x.next[0];
    return [x !== null && x.key === key, moves];
  }

  lanes() {
    const out = [];
    for (let lv = this.level - 1; lv >= 0; lv--) {
      const keys = [];
      for (let x = this.head.next[lv]; x; x = x.next[lv]) keys.push(x.key);
      out.push([lv, keys]);
    }
    return out;
  }
}

const sl = new SkipList();
for (const k of [3, 6, 7, 9, 12, 19, 17, 26, 21, 25]) sl.insert(k);
for (const [lv, keys] of sl.lanes()) console.log(`lane ${lv}: [${keys.join(", ")}]`);
for (const k of [19, 5]) {
  const [found, moves] = sl.search(k);
  console.log(`search ${k}: ${found ? "found" : "not found"}, right moves made: ${moves}`);
}
''', java=r'''
import java.util.*;

public class SkipListDemo {
    static final int MAX_LEVEL = 4;
    static int seed = 7;

    static int coin() {                              // a tiny repeatable random generator, so every language agrees
        seed = (seed * 75 + 74) % 65537;
        return seed % 2;
    }

    static class SkipNode {
        int key;
        SkipNode[] next;                             // one forward link per lane
        SkipNode(int key, int level) { this.key = key; next = new SkipNode[level]; }
    }

    static SkipNode head = new SkipNode(Integer.MIN_VALUE, MAX_LEVEL);
    static int level = 1, moves;

    static void insert(int key) {
        SkipNode[] update = new SkipNode[MAX_LEVEL];
        Arrays.fill(update, head);
        SkipNode x = head;
        for (int lv = level - 1; lv >= 0; lv--) {    // run right along a lane, then drop down
            while (x.next[lv] != null && x.next[lv].key < key) x = x.next[lv];
            update[lv] = x;
        }
        int lvl = 1;
        while (lvl < MAX_LEVEL && coin() == 1) lvl++;   // heads: the new key also joins the lane above
        level = Math.max(level, lvl);
        SkipNode node = new SkipNode(key, lvl);
        for (int lv = 0; lv < lvl; lv++) { node.next[lv] = update[lv].next[lv]; update[lv].next[lv] = node; }
    }

    static boolean search(int key) {
        SkipNode x = head;
        moves = 0;
        for (int lv = level - 1; lv >= 0; lv--)
            while (x.next[lv] != null && x.next[lv].key < key) { x = x.next[lv]; moves++; }
        x = x.next[0];
        return x != null && x.key == key;
    }

    public static void main(String[] args) {
        for (int k : new int[]{3, 6, 7, 9, 12, 19, 17, 26, 21, 25}) insert(k);
        for (int lv = level - 1; lv >= 0; lv--) {
            List<Integer> keys = new ArrayList<>();
            for (SkipNode x = head.next[lv]; x != null; x = x.next[lv]) keys.add(x.key);
            System.out.println("lane " + lv + ": " + keys);
        }
        for (int k : new int[]{19, 5}) {
            boolean found = search(k);
            System.out.println("search " + k + ": " + (found ? "found" : "not found") + ", right moves made: " + moves);
        }
    }
}
''', ts=r'''
const MAX_LEVEL = 4;
let seed = 7;

function coin(): number {                            // a tiny repeatable random generator, so every language agrees
  seed = (seed * 75 + 74) % 65537;
  return seed % 2;
}

class SkipNode {
  key: number;
  next: (SkipNode | null)[];                         // one forward link per lane
  constructor(key: number, level: number) { this.key = key; this.next = new Array(level).fill(null); }
}

class SkipList {
  head: SkipNode = new SkipNode(-Infinity, MAX_LEVEL);
  level = 1;

  insert(key: number): void {
    const update: SkipNode[] = new Array(MAX_LEVEL).fill(this.head);
    let x = this.head;
    for (let lv = this.level - 1; lv >= 0; lv--) {   // run right along a lane, then drop down
      while (x.next[lv] && (x.next[lv] as SkipNode).key < key) x = x.next[lv] as SkipNode;
      update[lv] = x;
    }
    let lvl = 1;
    while (lvl < MAX_LEVEL && coin()) lvl++;         // heads: the new key also joins the lane above
    this.level = Math.max(this.level, lvl);
    const node = new SkipNode(key, lvl);
    for (let lv = 0; lv < lvl; lv++) { node.next[lv] = update[lv].next[lv]; update[lv].next[lv] = node; }
  }

  search(key: number): [boolean, number] {
    let x: SkipNode = this.head, moves = 0;
    for (let lv = this.level - 1; lv >= 0; lv--) {
      while (x.next[lv] && (x.next[lv] as SkipNode).key < key) { x = x.next[lv] as SkipNode; moves++; }
    }
    const y = x.next[0];
    return [y !== null && y.key === key, moves];
  }

  lanes(): [number, number[]][] {
    const out: [number, number[]][] = [];
    for (let lv = this.level - 1; lv >= 0; lv--) {
      const keys: number[] = [];
      for (let x = this.head.next[lv]; x; x = x.next[lv]) keys.push(x.key);
      out.push([lv, keys]);
    }
    return out;
  }
}

const sl = new SkipList();
for (const k of [3, 6, 7, 9, 12, 19, 17, 26, 21, 25]) sl.insert(k);
for (const [lv, keys] of sl.lanes()) console.log(`lane ${lv}: [${keys.join(", ")}]`);
for (const k of [19, 5]) {
  const [found, moves] = sl.search(k);
  console.log(`search ${k}: ${found ? "found" : "not found"}, right moves made: ${moves}`);
}
''')

t.code('bloom', py=r'''
M = 32                                           # bits in the filter


def poly_hash(word, base, mod):
    h = 0
    for ch in word:
        h = (h * base + ord(ch)) % mod
    return h


def positions(word):                             # three bit positions made from two hashes
    h1, h2 = poly_hash(word, 31, 1000003), poly_hash(word, 37, 1000033) | 1
    return [(h1 + i * h2) % M for i in range(3)]


bits = [0] * M
for w in ["cat", "dog", "owl", "fox", "bee"]:
    for p in positions(w):
        bits[p] = 1
print(f"bits set: {sum(bits)} of {M}")
for w in ["cat", "hog", "ant"]:
    ps = positions(w)
    verdict = "maybe present" if all(bits[p] for p in ps) else "definitely absent"
    print(f"{w} {ps} {verdict}")
''', js=r'''
const M = 32;                                        // bits in the filter

function polyHash(word, base, mod) {
  let h = 0;
  for (const ch of word) h = (h * base + ch.charCodeAt(0)) % mod;
  return h;
}

function positions(word) {                           // three bit positions made from two hashes
  const h1 = polyHash(word, 31, 1000003), h2 = polyHash(word, 37, 1000033) | 1;
  return [0, 1, 2].map(i => (h1 + i * h2) % M);
}

const bits = new Array(M).fill(0);
for (const w of ["cat", "dog", "owl", "fox", "bee"]) for (const p of positions(w)) bits[p] = 1;
console.log(`bits set: ${bits.reduce((a, b) => a + b, 0)} of ${M}`);
for (const w of ["cat", "hog", "ant"]) {
  const ps = positions(w);
  const verdict = ps.every(p => bits[p]) ? "maybe present" : "definitely absent";
  console.log(`${w} [${ps.join(", ")}] ${verdict}`);
}
''', java=r'''
import java.util.*;

public class BloomFilter {
    static final int M = 32;                         // bits in the filter

    static int polyHash(String word, int base, int mod) {
        long h = 0;
        for (char ch : word.toCharArray()) h = (h * base + ch) % mod;
        return (int) h;
    }

    static int[] positions(String word) {            // three bit positions made from two hashes
        int h1 = polyHash(word, 31, 1000003), h2 = polyHash(word, 37, 1000033) | 1;
        int[] ps = new int[3];
        for (int i = 0; i < 3; i++) ps[i] = (int) ((h1 + (long) i * h2) % M);
        return ps;
    }

    public static void main(String[] args) {
        int[] bits = new int[M];
        for (String w : new String[]{"cat", "dog", "owl", "fox", "bee"}) for (int p : positions(w)) bits[p] = 1;
        int set = 0;
        for (int b : bits) set += b;
        System.out.println("bits set: " + set + " of " + M);
        for (String w : new String[]{"cat", "hog", "ant"}) {
            int[] ps = positions(w);
            boolean all = true;
            for (int p : ps) if (bits[p] == 0) all = false;
            System.out.println(w + " " + Arrays.toString(ps) + " " + (all ? "maybe present" : "definitely absent"));
        }
    }
}
''', ts=r'''
const M = 32;                                        // bits in the filter

function polyHash(word: string, base: number, mod: number): number {
  let h = 0;
  for (const ch of word) h = (h * base + ch.charCodeAt(0)) % mod;
  return h;
}

function positions(word: string): number[] {         // three bit positions made from two hashes
  const h1 = polyHash(word, 31, 1000003), h2 = polyHash(word, 37, 1000033) | 1;
  return [0, 1, 2].map(i => (h1 + i * h2) % M);
}

const bits: number[] = new Array(M).fill(0);
for (const w of ["cat", "dog", "owl", "fox", "bee"]) for (const p of positions(w)) bits[p] = 1;
console.log(`bits set: ${bits.reduce((a, b) => a + b, 0)} of ${M}`);
for (const w of ["cat", "hog", "ant"]) {
  const ps = positions(w);
  const verdict = ps.every(p => bits[p]) ? "maybe present" : "definitely absent";
  console.log(`${w} [${ps.join(", ")}] ${verdict}`);
}
''')

t.code('countmin', py=r'''
W, D = 8, 3                                      # 3 rows of 8 counters
BASES = [31, 37, 41]                             # a different hash for each row


def column(word, row):
    h = 0
    for ch in word:
        h = (h * BASES[row] + ord(ch)) % 1000003
    return h % W


table = [[0] * W for _ in range(D)]
stream = "the cat and the dog and the owl saw the cat".split()
for w in stream:
    for r in range(D):
        table[r][column(w, r)] += 1              # every row counts every word once
for row in table:
    print(row)
for w in ["the", "cat", "owl", "fox"]:
    estimate = min(table[r][column(w, r)] for r in range(D))   # collisions only add, so the smallest is closest
    print(f"{w}: true {stream.count(w)}, estimate {estimate}")
''', js=r'''
const W = 8, D = 3;                                  // 3 rows of 8 counters
const BASES = [31, 37, 41];                          // a different hash for each row

function column(word, row) {
  let h = 0;
  for (const ch of word) h = (h * BASES[row] + ch.charCodeAt(0)) % 1000003;
  return h % W;
}

const table = Array.from({ length: D }, () => new Array(W).fill(0));
const stream = "the cat and the dog and the owl saw the cat".split(" ");
for (const w of stream) for (let r = 0; r < D; r++) table[r][column(w, r)]++;   // every row counts every word once
for (const row of table) console.log(`[${row.join(", ")}]`);
for (const w of ["the", "cat", "owl", "fox"]) {
  let estimate = Infinity;
  for (let r = 0; r < D; r++) estimate = Math.min(estimate, table[r][column(w, r)]);   // the smallest is closest
  console.log(`${w}: true ${stream.filter(x => x === w).length}, estimate ${estimate}`);
}
''', java=r'''
import java.util.*;

public class CountMin {
    static final int W = 8, D = 3;                   // 3 rows of 8 counters
    static final int[] BASES = {31, 37, 41};         // a different hash for each row

    static int column(String word, int row) {
        long h = 0;
        for (char ch : word.toCharArray()) h = (h * BASES[row] + ch) % 1000003;
        return (int) (h % W);
    }

    public static void main(String[] args) {
        int[][] table = new int[D][W];
        String[] stream = "the cat and the dog and the owl saw the cat".split(" ");
        for (String w : stream) for (int r = 0; r < D; r++) table[r][column(w, r)]++;   // every row counts every word once
        for (int[] row : table) System.out.println(Arrays.toString(row));
        for (String w : new String[]{"the", "cat", "owl", "fox"}) {
            int estimate = Integer.MAX_VALUE, actual = 0;
            for (int r = 0; r < D; r++) estimate = Math.min(estimate, table[r][column(w, r)]);   // the smallest is closest
            for (String x : stream) if (x.equals(w)) actual++;
            System.out.println(w + ": true " + actual + ", estimate " + estimate);
        }
    }
}
''', ts=r'''
const W = 8, D = 3;                                  // 3 rows of 8 counters
const BASES = [31, 37, 41];                          // a different hash for each row

function column(word: string, row: number): number {
  let h = 0;
  for (const ch of word) h = (h * BASES[row] + ch.charCodeAt(0)) % 1000003;
  return h % W;
}

const table: number[][] = Array.from({ length: D }, () => new Array(W).fill(0));
const stream = "the cat and the dog and the owl saw the cat".split(" ");
for (const w of stream) for (let r = 0; r < D; r++) table[r][column(w, r)]++;   // every row counts every word once
for (const row of table) console.log(`[${row.join(", ")}]`);
for (const w of ["the", "cat", "owl", "fox"]) {
  let estimate = Infinity;
  for (let r = 0; r < D; r++) estimate = Math.min(estimate, table[r][column(w, r)]);   // the smallest is closest
  console.log(`${w}: true ${stream.filter(x => x === w).length}, estimate ${estimate}`);
}
''')

t.code('sparse', py=r'''
def build(a):
    n = len(a)
    table = [a[:]]                               # table[j][i]: the minimum of the 2**j values from a[i]
    j = 1
    while (1 << j) <= n:
        prev, half = table[-1], 1 << (j - 1)
        table.append([min(prev[i], prev[i + half]) for i in range(n - (1 << j) + 1)])   # two halves
        j += 1
    return table


def query(table, l, r):                          # minimum of a[l..r] from two blocks that may overlap
    j = (r - l + 1).bit_length() - 1
    return min(table[j][l], table[j][r - (1 << j) + 1])


a = [5, 2, 4, 7, 1, 3, 6, 8]
table = build(a)
for j, row in enumerate(table):
    print(f"blocks of {1 << j}: {row}")
for l, r in ((0, 3), (2, 6), (5, 7), (4, 4)):
    print(f"min of a[{l}..{r}] = {query(table, l, r)}")
''', js=r'''
function build(a) {
  const n = a.length, table = [a.slice()];           // table[j][i]: the minimum of the 2**j values from a[i]
  for (let j = 1; (1 << j) <= n; j++) {
    const prev = table[j - 1], half = 1 << (j - 1), row = [];
    for (let i = 0; i + (1 << j) <= n; i++) row.push(Math.min(prev[i], prev[i + half]));   // two halves
    table.push(row);
  }
  return table;
}

function query(table, l, r) {                        // minimum of a[l..r] from two blocks that may overlap
  const j = 31 - Math.clz32(r - l + 1);
  return Math.min(table[j][l], table[j][r - (1 << j) + 1]);
}

const a = [5, 2, 4, 7, 1, 3, 6, 8];
const table = build(a);
table.forEach((row, j) => console.log(`blocks of ${1 << j}: [${row.join(", ")}]`));
for (const [l, r] of [[0, 3], [2, 6], [5, 7], [4, 4]]) console.log(`min of a[${l}..${r}] = ${query(table, l, r)}`);
''', java=r'''
import java.util.*;

public class SparseTable {
    static List<int[]> build(int[] a) {
        int n = a.length;
        List<int[]> table = new ArrayList<>();       // table[j][i]: the minimum of the 2**j values from a[i]
        table.add(a.clone());
        for (int j = 1; (1 << j) <= n; j++) {
            int[] prev = table.get(j - 1), row = new int[n - (1 << j) + 1];
            int half = 1 << (j - 1);
            for (int i = 0; i < row.length; i++) row[i] = Math.min(prev[i], prev[i + half]);   // two halves
            table.add(row);
        }
        return table;
    }

    static int query(List<int[]> table, int l, int r) {   // minimum of a[l..r] from two blocks that may overlap
        int j = 31 - Integer.numberOfLeadingZeros(r - l + 1);
        return Math.min(table.get(j)[l], table.get(j)[r - (1 << j) + 1]);
    }

    public static void main(String[] args) {
        int[] a = {5, 2, 4, 7, 1, 3, 6, 8};
        List<int[]> table = build(a);
        for (int j = 0; j < table.size(); j++) System.out.println("blocks of " + (1 << j) + ": " + Arrays.toString(table.get(j)));
        for (int[] q : new int[][]{{0, 3}, {2, 6}, {5, 7}, {4, 4}}) System.out.println("min of a[" + q[0] + ".." + q[1] + "] = " + query(table, q[0], q[1]));
    }
}
''', ts=r'''
function build(a: number[]): number[][] {
  const n = a.length, table: number[][] = [a.slice()];   // table[j][i]: the minimum of the 2**j values from a[i]
  for (let j = 1; (1 << j) <= n; j++) {
    const prev = table[j - 1], half = 1 << (j - 1), row: number[] = [];
    for (let i = 0; i + (1 << j) <= n; i++) row.push(Math.min(prev[i], prev[i + half]));   // two halves
    table.push(row);
  }
  return table;
}

function query(table: number[][], l: number, r: number): number {   // minimum of a[l..r] from two blocks
  const j = 31 - Math.clz32(r - l + 1);
  return Math.min(table[j][l], table[j][r - (1 << j) + 1]);
}

const a = [5, 2, 4, 7, 1, 3, 6, 8];
const table = build(a);
table.forEach((row, j) => console.log(`blocks of ${1 << j}: [${row.join(", ")}]`));
for (const [l, r] of [[0, 3], [2, 6], [5, 7], [4, 4]]) console.log(`min of a[${l}..${r}] = ${query(table, l, r)}`);
''')

t.code('sqrtdec', py=r'''
import math


class SqrtSum:
    def __init__(self, a):
        self.a = a[:]
        self.size = max(1, math.isqrt(len(a)))   # block size about the square root of n
        self.blocks = [0] * ((len(a) + self.size - 1) // self.size)
        for i, x in enumerate(a):
            self.blocks[i // self.size] += x

    def update(self, i, value):                  # one cell and one block total change
        self.blocks[i // self.size] += value - self.a[i]
        self.a[i] = value

    def query(self, l, r):                       # sum of a[l..r]
        total = 0
        while l <= r and l % self.size:          # loose cells on the left
            total += self.a[l]
            l += 1
        while l + self.size - 1 <= r:            # whole blocks
            total += self.blocks[l // self.size]
            l += self.size
        while l <= r:                            # loose cells on the right
            total += self.a[l]
            l += 1
        return total


s = SqrtSum([3, 1, 4, 1, 5, 9, 2, 6, 5])
print(f"block size {s.size}, block sums {s.blocks}")
print(f"sum of a[1..7] = {s.query(1, 7)}")
s.update(4, 10)
print(f"after a[4] = 10: block sums {s.blocks}, sum of a[1..7] = {s.query(1, 7)}")
''', js=r'''
class SqrtSum {
  constructor(a) {
    this.a = a.slice();
    this.size = Math.max(1, Math.floor(Math.sqrt(a.length)));   // block size about the square root of n
    this.blocks = new Array(Math.ceil(a.length / this.size)).fill(0);
    a.forEach((x, i) => { this.blocks[Math.floor(i / this.size)] += x; });
  }

  update(i, value) {                                 // one cell and one block total change
    this.blocks[Math.floor(i / this.size)] += value - this.a[i];
    this.a[i] = value;
  }

  query(l, r) {                                      // sum of a[l..r]
    let total = 0;
    while (l <= r && l % this.size) total += this.a[l++];                    // loose cells on the left
    while (l + this.size - 1 <= r) { total += this.blocks[Math.floor(l / this.size)]; l += this.size; }   // whole blocks
    while (l <= r) total += this.a[l++];                                     // loose cells on the right
    return total;
  }
}

const s = new SqrtSum([3, 1, 4, 1, 5, 9, 2, 6, 5]);
console.log(`block size ${s.size}, block sums [${s.blocks.join(", ")}]`);
console.log(`sum of a[1..7] = ${s.query(1, 7)}`);
s.update(4, 10);
console.log(`after a[4] = 10: block sums [${s.blocks.join(", ")}], sum of a[1..7] = ${s.query(1, 7)}`);
''', java=r'''
import java.util.*;

public class SqrtDecomposition {
    static int[] a, blocks;
    static int size;

    static void build(int[] values) {
        a = values.clone();
        size = Math.max(1, (int) Math.sqrt(a.length));   // block size about the square root of n
        blocks = new int[(a.length + size - 1) / size];
        for (int i = 0; i < a.length; i++) blocks[i / size] += a[i];
    }

    static void update(int i, int value) {           // one cell and one block total change
        blocks[i / size] += value - a[i];
        a[i] = value;
    }

    static int query(int l, int r) {                 // sum of a[l..r]
        int total = 0;
        while (l <= r && l % size != 0) total += a[l++];                     // loose cells on the left
        while (l + size - 1 <= r) { total += blocks[l / size]; l += size; }  // whole blocks
        while (l <= r) total += a[l++];                                      // loose cells on the right
        return total;
    }

    public static void main(String[] args) {
        build(new int[]{3, 1, 4, 1, 5, 9, 2, 6, 5});
        System.out.println("block size " + size + ", block sums " + Arrays.toString(blocks));
        System.out.println("sum of a[1..7] = " + query(1, 7));
        update(4, 10);
        System.out.println("after a[4] = 10: block sums " + Arrays.toString(blocks) + ", sum of a[1..7] = " + query(1, 7));
    }
}
''', ts=r'''
class SqrtSum {
  a: number[];
  size: number;
  blocks: number[];

  constructor(a: number[]) {
    this.a = a.slice();
    this.size = Math.max(1, Math.floor(Math.sqrt(a.length)));   // block size about the square root of n
    this.blocks = new Array(Math.ceil(a.length / this.size)).fill(0);
    a.forEach((x, i) => { this.blocks[Math.floor(i / this.size)] += x; });
  }

  update(i: number, value: number): void {           // one cell and one block total change
    this.blocks[Math.floor(i / this.size)] += value - this.a[i];
    this.a[i] = value;
  }

  query(l: number, r: number): number {              // sum of a[l..r]
    let total = 0;
    while (l <= r && l % this.size) total += this.a[l++];                    // loose cells on the left
    while (l + this.size - 1 <= r) { total += this.blocks[Math.floor(l / this.size)]; l += this.size; }   // whole blocks
    while (l <= r) total += this.a[l++];                                     // loose cells on the right
    return total;
  }
}

const s = new SqrtSum([3, 1, 4, 1, 5, 9, 2, 6, 5]);
console.log(`block size ${s.size}, block sums [${s.blocks.join(", ")}]`);
console.log(`sum of a[1..7] = ${s.query(1, 7)}`);
s.update(4, 10);
console.log(`after a[4] = 10: block sums [${s.blocks.join(", ")}], sum of a[1..7] = ${s.query(1, 7)}`);
''')

# ---------------------------------------------------------------- LeetCode programs
t.code('p_rangesum', py=r'''
class NumArray:
    def __init__(self, nums):
        self.pre = [0]                           # pre[i]: the sum of the first i numbers
        for x in nums:
            self.pre.append(self.pre[-1] + x)

    def sum_range(self, left, right):
        return self.pre[right + 1] - self.pre[left]


na = NumArray([-2, 0, 3, -5, 2, -1])
print(na.sum_range(0, 2), na.sum_range(2, 5), na.sum_range(0, 5))
''', js=r'''
class NumArray {
  constructor(nums) {
    this.pre = [0];                                  // pre[i]: the sum of the first i numbers
    for (const x of nums) this.pre.push(this.pre[this.pre.length - 1] + x);
  }
  sumRange(left, right) { return this.pre[right + 1] - this.pre[left]; }
}

const na = new NumArray([-2, 0, 3, -5, 2, -1]);
console.log(na.sumRange(0, 2), na.sumRange(2, 5), na.sumRange(0, 5));
''', java=r'''
public class RangeSumQuery {
    static int[] pre;

    static void numArray(int[] nums) {
        pre = new int[nums.length + 1];              // pre[i]: the sum of the first i numbers
        for (int i = 0; i < nums.length; i++) pre[i + 1] = pre[i] + nums[i];
    }

    static int sumRange(int left, int right) { return pre[right + 1] - pre[left]; }

    public static void main(String[] args) {
        numArray(new int[]{-2, 0, 3, -5, 2, -1});
        System.out.println(sumRange(0, 2) + " " + sumRange(2, 5) + " " + sumRange(0, 5));
    }
}
''', ts=r'''
class NumArray {
  pre: number[] = [0];                               // pre[i]: the sum of the first i numbers
  constructor(nums: number[]) {
    for (const x of nums) this.pre.push(this.pre[this.pre.length - 1] + x);
  }
  sumRange(left: number, right: number): number { return this.pre[right + 1] - this.pre[left]; }
}

const na = new NumArray([-2, 0, 3, -5, 2, -1]);
console.log(na.sumRange(0, 2), na.sumRange(2, 5), na.sumRange(0, 5));
''')

t.code('p_hashset', py=r'''
class MyHashSet:
    SIZE = 1009                                  # a prime number of buckets

    def __init__(self):
        self.buckets = [[] for _ in range(self.SIZE)]

    def add(self, key):
        b = self.buckets[key % self.SIZE]
        if key not in b:
            b.append(key)

    def remove(self, key):
        b = self.buckets[key % self.SIZE]
        if key in b:
            b.remove(key)

    def contains(self, key):
        return key in self.buckets[key % self.SIZE]


s = MyHashSet()
s.add(1)
s.add(2)
s.add(1010)                                      # 1010 lands in the same bucket as 1
print("true" if s.contains(1) else "false", "true" if s.contains(3) else "false")
s.remove(2)
print("true" if s.contains(2) else "false", "true" if s.contains(1010) else "false")
''', js=r'''
class MyHashSet {
  constructor() { this.SIZE = 1009; this.buckets = Array.from({ length: this.SIZE }, () => []); }   // a prime number of buckets
  add(key) { const b = this.buckets[key % this.SIZE]; if (!b.includes(key)) b.push(key); }
  remove(key) { const b = this.buckets[key % this.SIZE], i = b.indexOf(key); if (i >= 0) b.splice(i, 1); }
  contains(key) { return this.buckets[key % this.SIZE].includes(key); }
}

const s = new MyHashSet();
s.add(1);
s.add(2);
s.add(1010);                                         // 1010 lands in the same bucket as 1
console.log(s.contains(1), s.contains(3));
s.remove(2);
console.log(s.contains(2), s.contains(1010));
''', java=r'''
import java.util.*;

public class MyHashSet {
    static final int SIZE = 1009;                    // a prime number of buckets
    static List<List<Integer>> buckets = new ArrayList<>();

    static void add(int key) { List<Integer> b = buckets.get(key % SIZE); if (!b.contains(key)) b.add(key); }
    static void remove(int key) { buckets.get(key % SIZE).remove(Integer.valueOf(key)); }
    static boolean contains(int key) { return buckets.get(key % SIZE).contains(key); }

    public static void main(String[] args) {
        for (int i = 0; i < SIZE; i++) buckets.add(new LinkedList<>());
        add(1);
        add(2);
        add(1010);                                   // 1010 lands in the same bucket as 1
        System.out.println(contains(1) + " " + contains(3));
        remove(2);
        System.out.println(contains(2) + " " + contains(1010));
    }
}
''', ts=r'''
class MyHashSet {
  SIZE = 1009;                                       // a prime number of buckets
  buckets: number[][] = Array.from({ length: 1009 }, () => []);
  add(key: number): void { const b = this.buckets[key % this.SIZE]; if (!b.includes(key)) b.push(key); }
  remove(key: number): void { const b = this.buckets[key % this.SIZE], i = b.indexOf(key); if (i >= 0) b.splice(i, 1); }
  contains(key: number): boolean { return this.buckets[key % this.SIZE].includes(key); }
}

const s = new MyHashSet();
s.add(1);
s.add(2);
s.add(1010);                                         // 1010 lands in the same bucket as 1
console.log(s.contains(1), s.contains(3));
s.remove(2);
console.log(s.contains(2), s.contains(1010));
''')

t.code('p_rangemut', py=r'''
import math


class NumArray:
    def __init__(self, nums):
        self.a = nums[:]
        self.size = max(1, math.isqrt(len(nums)))
        self.blocks = [0] * ((len(nums) + self.size - 1) // self.size)
        for i, x in enumerate(nums):
            self.blocks[i // self.size] += x

    def update(self, index, val):
        self.blocks[index // self.size] += val - self.a[index]
        self.a[index] = val

    def sum_range(self, left, right):
        total = 0
        while left <= right and left % self.size:            # loose cells, then whole blocks, then loose cells
            total, left = total + self.a[left], left + 1
        while left + self.size - 1 <= right:
            total, left = total + self.blocks[left // self.size], left + self.size
        while left <= right:
            total, left = total + self.a[left], left + 1
        return total


na = NumArray([1, 3, 5])
print(na.sum_range(0, 2))
na.update(1, 2)
print(na.sum_range(0, 2))
nb = NumArray([2, 4, 6, 8, 10, 12, 14])
print(nb.sum_range(1, 5))
''', js=r'''
class NumArray {
  constructor(nums) {
    this.a = nums.slice();
    this.size = Math.max(1, Math.floor(Math.sqrt(nums.length)));
    this.blocks = new Array(Math.ceil(nums.length / this.size)).fill(0);
    nums.forEach((x, i) => { this.blocks[Math.floor(i / this.size)] += x; });
  }
  update(index, val) { this.blocks[Math.floor(index / this.size)] += val - this.a[index]; this.a[index] = val; }
  sumRange(left, right) {
    let total = 0;
    while (left <= right && left % this.size) total += this.a[left++];   // loose cells, whole blocks, loose cells
    while (left + this.size - 1 <= right) { total += this.blocks[Math.floor(left / this.size)]; left += this.size; }
    while (left <= right) total += this.a[left++];
    return total;
  }
}

const na = new NumArray([1, 3, 5]);
console.log(na.sumRange(0, 2));
na.update(1, 2);
console.log(na.sumRange(0, 2));
const nb = new NumArray([2, 4, 6, 8, 10, 12, 14]);
console.log(nb.sumRange(1, 5));
''', java=r'''
public class RangeSumMutable {
    int[] a, blocks;
    int size;

    RangeSumMutable(int[] nums) {
        a = nums.clone();
        size = Math.max(1, (int) Math.sqrt(nums.length));
        blocks = new int[(nums.length + size - 1) / size];
        for (int i = 0; i < nums.length; i++) blocks[i / size] += nums[i];
    }

    void update(int index, int val) { blocks[index / size] += val - a[index]; a[index] = val; }

    int sumRange(int left, int right) {
        int total = 0;
        while (left <= right && left % size != 0) total += a[left++];       // loose cells, whole blocks, loose cells
        while (left + size - 1 <= right) { total += blocks[left / size]; left += size; }
        while (left <= right) total += a[left++];
        return total;
    }

    public static void main(String[] args) {
        RangeSumMutable na = new RangeSumMutable(new int[]{1, 3, 5});
        System.out.println(na.sumRange(0, 2));
        na.update(1, 2);
        System.out.println(na.sumRange(0, 2));
        RangeSumMutable nb = new RangeSumMutable(new int[]{2, 4, 6, 8, 10, 12, 14});
        System.out.println(nb.sumRange(1, 5));
    }
}
''', ts=r'''
class NumArray {
  a: number[];
  size: number;
  blocks: number[];
  constructor(nums: number[]) {
    this.a = nums.slice();
    this.size = Math.max(1, Math.floor(Math.sqrt(nums.length)));
    this.blocks = new Array(Math.ceil(nums.length / this.size)).fill(0);
    nums.forEach((x, i) => { this.blocks[Math.floor(i / this.size)] += x; });
  }
  update(index: number, val: number): void { this.blocks[Math.floor(index / this.size)] += val - this.a[index]; this.a[index] = val; }
  sumRange(left: number, right: number): number {
    let total = 0;
    while (left <= right && left % this.size) total += this.a[left++];   // loose cells, whole blocks, loose cells
    while (left + this.size - 1 <= right) { total += this.blocks[Math.floor(left / this.size)]; left += this.size; }
    while (left <= right) total += this.a[left++];
    return total;
  }
}

const na = new NumArray([1, 3, 5]);
console.log(na.sumRange(0, 2));
na.update(1, 2);
console.log(na.sumRange(0, 2));
const nb = new NumArray([2, 4, 6, 8, 10, 12, 14]);
console.log(nb.sumRange(1, 5));
''')

t.code('p_rangefreq', py=r'''
from bisect import bisect_left, bisect_right


class RangeFreqQuery:
    def __init__(self, arr):
        self.where = {}                          # value -> sorted list of its positions
        for i, x in enumerate(arr):
            self.where.setdefault(x, []).append(i)

    def query(self, left, right, value):
        pos = self.where.get(value, [])
        return bisect_right(pos, right) - bisect_left(pos, left)   # positions inside [left, right]


q = RangeFreqQuery([12, 33, 4, 56, 22, 2, 34, 33, 22, 12, 34, 56])
print(q.query(1, 2, 4), q.query(0, 11, 33), q.query(0, 11, 99), q.query(4, 9, 22))
''', js=r'''
class RangeFreqQuery {
  constructor(arr) {
    this.where = new Map();                          // value -> sorted list of its positions
    arr.forEach((x, i) => { if (!this.where.has(x)) this.where.set(x, []); this.where.get(x).push(i); });
  }
  static lower(a, x) { let lo = 0, hi = a.length; while (lo < hi) { const m = (lo + hi) >> 1; if (a[m] < x) lo = m + 1; else hi = m; } return lo; }
  query(left, right, value) {
    const pos = this.where.get(value) || [];
    return RangeFreqQuery.lower(pos, right + 1) - RangeFreqQuery.lower(pos, left);   // positions inside [left, right]
  }
}

const q = new RangeFreqQuery([12, 33, 4, 56, 22, 2, 34, 33, 22, 12, 34, 56]);
console.log(q.query(1, 2, 4), q.query(0, 11, 33), q.query(0, 11, 99), q.query(4, 9, 22));
''', java=r'''
import java.util.*;

public class RangeFreqQuery {
    Map<Integer, List<Integer>> where = new HashMap<>();   // value -> sorted list of its positions

    RangeFreqQuery(int[] arr) {
        for (int i = 0; i < arr.length; i++) where.computeIfAbsent(arr[i], k -> new ArrayList<>()).add(i);
    }

    static int lower(List<Integer> a, int x) {
        int lo = 0, hi = a.size();
        while (lo < hi) { int m = (lo + hi) >> 1; if (a.get(m) < x) lo = m + 1; else hi = m; }
        return lo;
    }

    int query(int left, int right, int value) {
        List<Integer> pos = where.getOrDefault(value, List.of());
        return lower(pos, right + 1) - lower(pos, left);   // positions inside [left, right]
    }

    public static void main(String[] args) {
        RangeFreqQuery q = new RangeFreqQuery(new int[]{12, 33, 4, 56, 22, 2, 34, 33, 22, 12, 34, 56});
        System.out.println(q.query(1, 2, 4) + " " + q.query(0, 11, 33) + " " + q.query(0, 11, 99) + " " + q.query(4, 9, 22));
    }
}
''', ts=r'''
class RangeFreqQuery {
  where = new Map<number, number[]>();               // value -> sorted list of its positions
  constructor(arr: number[]) {
    arr.forEach((x, i) => { if (!this.where.has(x)) this.where.set(x, []); (this.where.get(x) as number[]).push(i); });
  }
  static lower(a: number[], x: number): number { let lo = 0, hi = a.length; while (lo < hi) { const m = (lo + hi) >> 1; if (a[m] < x) lo = m + 1; else hi = m; } return lo; }
  query(left: number, right: number, value: number): number {
    const pos = this.where.get(value) || [];
    return RangeFreqQuery.lower(pos, right + 1) - RangeFreqQuery.lower(pos, left);   // positions inside [left, right]
  }
}

const q = new RangeFreqQuery([12, 33, 4, 56, 22, 2, 34, 33, 22, 12, 34, 56]);
console.log(q.query(1, 2, 4), q.query(0, 11, 33), q.query(0, 11, 99), q.query(4, 9, 22));
''')

t.code('p_windowmax', py=r'''
from collections import deque


def max_sliding_window(nums, k):
    dq, out = deque(), []                        # indexes whose values only go down from front to back
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()                             # a smaller value before x can never be a maximum again
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()                         # the front slid out of the window
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out


print(max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3))
print(max_sliding_window([1], 1))
print(max_sliding_window([9, 8, 7, 6, 5], 2))
''', js=r'''
function maxSlidingWindow(nums, k) {
  const dq = [], out = [];                           // indexes whose values only go down from front to back
  let head = 0;
  nums.forEach((x, i) => {
    while (dq.length > head && nums[dq[dq.length - 1]] <= x) dq.pop();   // a smaller value before x is never a maximum again
    dq.push(i);
    if (dq[head] <= i - k) head++;                   // the front slid out of the window
    if (i >= k - 1) out.push(nums[dq[head]]);
  });
  return out;
}

for (const [nums, k] of [[[1, 3, -1, -3, 5, 3, 6, 7], 3], [[1], 1], [[9, 8, 7, 6, 5], 2]]) console.log(`[${maxSlidingWindow(nums, k).join(", ")}]`);
''', java=r'''
import java.util.*;

public class SlidingWindowMax {
    static List<Integer> maxSlidingWindow(int[] nums, int k) {
        ArrayDeque<Integer> dq = new ArrayDeque<>(); // indexes whose values only go down from front to back
        List<Integer> out = new ArrayList<>();
        for (int i = 0; i < nums.length; i++) {
            while (!dq.isEmpty() && nums[dq.peekLast()] <= nums[i]) dq.pollLast();   // never a maximum again
            dq.addLast(i);
            if (dq.peekFirst() <= i - k) dq.pollFirst();   // the front slid out of the window
            if (i >= k - 1) out.add(nums[dq.peekFirst()]);
        }
        return out;
    }

    public static void main(String[] args) {
        System.out.println(maxSlidingWindow(new int[]{1, 3, -1, -3, 5, 3, 6, 7}, 3));
        System.out.println(maxSlidingWindow(new int[]{1}, 1));
        System.out.println(maxSlidingWindow(new int[]{9, 8, 7, 6, 5}, 2));
    }
}
''', ts=r'''
function maxSlidingWindow(nums: number[], k: number): number[] {
  const dq: number[] = [], out: number[] = [];       // indexes whose values only go down from front to back
  let head = 0;
  nums.forEach((x, i) => {
    while (dq.length > head && nums[dq[dq.length - 1]] <= x) dq.pop();   // a smaller value before x is never a maximum again
    dq.push(i);
    if (dq[head] <= i - k) head++;                   // the front slid out of the window
    if (i >= k - 1) out.push(nums[dq[head]]);
  });
  return out;
}

const tests: [number[], number][] = [[[1, 3, -1, -3, 5, 3, 6, 7], 3], [[1], 1], [[9, 8, 7, 6, 5], 2]];
for (const [nums, k] of tests) console.log(`[${maxSlidingWindow(nums, k).join(", ")}]`);
''')

t.code('p_lru', py=r'''
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.data = OrderedDict()                # oldest use at the front, newest at the back

    def get(self, key):
        if key not in self.data:
            return -1
        self.data.move_to_end(key)               # just used, so it becomes the newest
        return self.data[key]

    def put(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.cap:
            self.data.popitem(last=False)        # throw out the least recently used


c = LRUCache(2)
c.put(1, 1)
c.put(2, 2)
print(c.get(1))
c.put(3, 3)                                      # 2 is the least recently used, so it goes
print(c.get(2))
c.put(4, 4)                                      # now 1 goes
print(c.get(1), c.get(3), c.get(4))
''', js=r'''
class LRUCache {
  constructor(capacity) { this.cap = capacity; this.data = new Map(); }   // a Map keeps insertion order: oldest first
  get(key) {
    if (!this.data.has(key)) return -1;
    const v = this.data.get(key);
    this.data.delete(key);
    this.data.set(key, v);                           // just used, so it becomes the newest
    return v;
  }
  put(key, value) {
    this.data.delete(key);
    this.data.set(key, value);
    if (this.data.size > this.cap) this.data.delete(this.data.keys().next().value);   // throw out the least recently used
  }
}

const c = new LRUCache(2);
c.put(1, 1);
c.put(2, 2);
console.log(c.get(1));
c.put(3, 3);                                         // 2 is the least recently used, so it goes
console.log(c.get(2));
c.put(4, 4);                                         // now 1 goes
console.log(c.get(1), c.get(3), c.get(4));
''', java=r'''
import java.util.*;

public class LRUCache extends LinkedHashMap<Integer, Integer> {
    final int cap;

    LRUCache(int capacity) {
        super(16, 0.75f, true);                      // true: order by most recent access
        cap = capacity;
    }

    int get(int key) { return getOrDefault(key, -1); }

    void put(int key, int value) { super.put(key, value); }

    @Override
    protected boolean removeEldestEntry(Map.Entry<Integer, Integer> eldest) {
        return size() > cap;                         // throw out the least recently used
    }

    public static void main(String[] args) {
        LRUCache c = new LRUCache(2);
        c.put(1, 1);
        c.put(2, 2);
        System.out.println(c.get(1));
        c.put(3, 3);                                 // 2 is the least recently used, so it goes
        System.out.println(c.get(2));
        c.put(4, 4);                                 // now 1 goes
        System.out.println(c.get(1) + " " + c.get(3) + " " + c.get(4));
    }
}
''', ts=r'''
class LRUCache {
  cap: number;
  data = new Map<number, number>();                  // a Map keeps insertion order: oldest first
  constructor(capacity: number) { this.cap = capacity; }
  get(key: number): number {
    if (!this.data.has(key)) return -1;
    const v = this.data.get(key) as number;
    this.data.delete(key);
    this.data.set(key, v);                           // just used, so it becomes the newest
    return v;
  }
  put(key: number, value: number): void {
    this.data.delete(key);
    this.data.set(key, value);
    if (this.data.size > this.cap) this.data.delete(this.data.keys().next().value as number);   // drop the least recently used
  }
}

const c = new LRUCache(2);
c.put(1, 1);
c.put(2, 2);
console.log(c.get(1));
c.put(3, 3);                                         // 2 is the least recently used, so it goes
console.log(c.get(2));
c.put(4, 4);                                         // now 1 goes
console.log(c.get(1), c.get(3), c.get(4));
''')

t.code('p_skiplist', py=r'''
seed = 1


def coin():                                      # repeatable coin flips, so the run is the same every time
    global seed
    seed = (seed * 75 + 74) % 65537
    return seed % 2


class Node:
    def __init__(self, val, level):
        self.val, self.next = val, [None] * level


class Skiplist:
    LEVELS = 8

    def __init__(self):
        self.head = Node(-1, self.LEVELS)

    def _path(self, target):                     # the last node before target on every lane
        path, x = [None] * self.LEVELS, self.head
        for lv in range(self.LEVELS - 1, -1, -1):
            while x.next[lv] and x.next[lv].val < target:
                x = x.next[lv]
            path[lv] = x
        return path

    def search(self, target):
        nxt = self._path(target)[0].next[0]
        return nxt is not None and nxt.val == target

    def add(self, num):
        path, lvl = self._path(num), 1
        while lvl < self.LEVELS and coin():
            lvl += 1
        node = Node(num, lvl)
        for lv in range(lvl):
            node.next[lv], path[lv].next[lv] = path[lv].next[lv], node

    def erase(self, num):
        path = self._path(num)
        node = path[0].next[0]
        if node is None or node.val != num:
            return False
        for lv in range(len(node.next)):
            path[lv].next[lv] = node.next[lv]    # unhook it from every lane it is on
        return True


sk = Skiplist()
for n in (1, 2, 3):
    sk.add(n)
results = [sk.search(0)]
sk.add(4)
results += [sk.search(1), sk.erase(0), sk.erase(1), sk.search(1)]
print(" ".join("true" if r else "false" for r in results))
''', js=r'''
let seed = 1;

function coin() {                                    // repeatable coin flips, so the run is the same every time
  seed = (seed * 75 + 74) % 65537;
  return seed % 2;
}

class SkipNode {
  constructor(val, level) { this.val = val; this.next = new Array(level).fill(null); }
}

class Skiplist {
  constructor() { this.LEVELS = 8; this.head = new SkipNode(-1, this.LEVELS); }
  path(target) {                                     // the last node before target on every lane
    const path = new Array(this.LEVELS);
    let x = this.head;
    for (let lv = this.LEVELS - 1; lv >= 0; lv--) {
      while (x.next[lv] && x.next[lv].val < target) x = x.next[lv];
      path[lv] = x;
    }
    return path;
  }
  search(target) { const nxt = this.path(target)[0].next[0]; return nxt !== null && nxt.val === target; }
  add(num) {
    const path = this.path(num);
    let lvl = 1;
    while (lvl < this.LEVELS && coin()) lvl++;
    const node = new SkipNode(num, lvl);
    for (let lv = 0; lv < lvl; lv++) { node.next[lv] = path[lv].next[lv]; path[lv].next[lv] = node; }
  }
  erase(num) {
    const path = this.path(num), node = path[0].next[0];
    if (node === null || node.val !== num) return false;
    for (let lv = 0; lv < node.next.length; lv++) path[lv].next[lv] = node.next[lv];   // unhook it from every lane
    return true;
  }
}

const sk = new Skiplist();
for (const n of [1, 2, 3]) sk.add(n);
const results = [sk.search(0)];
sk.add(4);
results.push(sk.search(1), sk.erase(0), sk.erase(1), sk.search(1));
console.log(results.join(" "));
''', java=r'''
import java.util.*;

public class Skiplist {
    static int seed = 1;

    static int coin() {                              // repeatable coin flips, so the run is the same every time
        seed = (seed * 75 + 74) % 65537;
        return seed % 2;
    }

    static class SkipNode {
        int val;
        SkipNode[] next;
        SkipNode(int val, int level) { this.val = val; next = new SkipNode[level]; }
    }

    static final int LEVELS = 8;
    SkipNode head = new SkipNode(-1, LEVELS);

    SkipNode[] path(int target) {                    // the last node before target on every lane
        SkipNode[] path = new SkipNode[LEVELS];
        SkipNode x = head;
        for (int lv = LEVELS - 1; lv >= 0; lv--) {
            while (x.next[lv] != null && x.next[lv].val < target) x = x.next[lv];
            path[lv] = x;
        }
        return path;
    }

    boolean search(int target) { SkipNode nxt = path(target)[0].next[0]; return nxt != null && nxt.val == target; }

    void add(int num) {
        SkipNode[] path = path(num);
        int lvl = 1;
        while (lvl < LEVELS && coin() == 1) lvl++;
        SkipNode node = new SkipNode(num, lvl);
        for (int lv = 0; lv < lvl; lv++) { node.next[lv] = path[lv].next[lv]; path[lv].next[lv] = node; }
    }

    boolean erase(int num) {
        SkipNode[] path = path(num);
        SkipNode node = path[0].next[0];
        if (node == null || node.val != num) return false;
        for (int lv = 0; lv < node.next.length; lv++) path[lv].next[lv] = node.next[lv];   // unhook it from every lane
        return true;
    }

    public static void main(String[] args) {
        Skiplist sk = new Skiplist();
        for (int n : new int[]{1, 2, 3}) sk.add(n);
        List<String> results = new ArrayList<>();
        results.add(String.valueOf(sk.search(0)));
        sk.add(4);
        results.add(String.valueOf(sk.search(1)));
        results.add(String.valueOf(sk.erase(0)));
        results.add(String.valueOf(sk.erase(1)));
        results.add(String.valueOf(sk.search(1)));
        System.out.println(String.join(" ", results));
    }
}
''', ts=r'''
let seed = 1;

function coin(): number {                            // repeatable coin flips, so the run is the same every time
  seed = (seed * 75 + 74) % 65537;
  return seed % 2;
}

class SkipNode {
  val: number;
  next: (SkipNode | null)[];
  constructor(val: number, level: number) { this.val = val; this.next = new Array(level).fill(null); }
}

class Skiplist {
  LEVELS = 8;
  head = new SkipNode(-1, 8);
  path(target: number): SkipNode[] {                 // the last node before target on every lane
    const path: SkipNode[] = new Array(this.LEVELS);
    let x = this.head;
    for (let lv = this.LEVELS - 1; lv >= 0; lv--) {
      while (x.next[lv] && (x.next[lv] as SkipNode).val < target) x = x.next[lv] as SkipNode;
      path[lv] = x;
    }
    return path;
  }
  search(target: number): boolean { const nxt = this.path(target)[0].next[0]; return nxt !== null && nxt.val === target; }
  add(num: number): void {
    const path = this.path(num);
    let lvl = 1;
    while (lvl < this.LEVELS && coin()) lvl++;
    const node = new SkipNode(num, lvl);
    for (let lv = 0; lv < lvl; lv++) { node.next[lv] = path[lv].next[lv]; path[lv].next[lv] = node; }
  }
  erase(num: number): boolean {
    const path = this.path(num), node = path[0].next[0];
    if (node === null || node.val !== num) return false;
    for (let lv = 0; lv < node.next.length; lv++) path[lv].next[lv] = node.next[lv];   // unhook it from every lane
    return true;
  }
}

const sk = new Skiplist();
for (const n of [1, 2, 3]) sk.add(n);
const results: boolean[] = [sk.search(0)];
sk.add(4);
results.push(sk.search(1), sk.erase(0), sk.erase(1), sk.search(1));
console.log(results.join(" "));
''')

t.code('p_lfu', py=r'''
from collections import defaultdict, OrderedDict


class LFUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.val, self.freq = {}, {}
        self.groups = defaultdict(OrderedDict)   # use count -> keys with that count, oldest first
        self.low = 0                             # the smallest use count present

    def _touch(self, key):
        f = self.freq[key]
        del self.groups[f][key]
        if not self.groups[f]:
            del self.groups[f]
            if self.low == f:
                self.low += 1
        self.freq[key] = f + 1
        self.groups[f + 1][key] = None

    def get(self, key):
        if key not in self.val:
            return -1
        self._touch(key)
        return self.val[key]

    def put(self, key, value):
        if self.cap == 0:
            return
        if key in self.val:
            self.val[key] = value
            self._touch(key)
            return
        if len(self.val) == self.cap:            # drop the least used, and the oldest among ties
            old, _ = self.groups[self.low].popitem(last=False)
            if not self.groups[self.low]:
                del self.groups[self.low]
            del self.val[old], self.freq[old]
        self.val[key], self.freq[key], self.low = value, 1, 1
        self.groups[1][key] = None


c = LFUCache(2)
c.put(1, 1)
c.put(2, 2)
out = [c.get(1)]
c.put(3, 3)                                      # 2 was used least, so it goes
out += [c.get(2), c.get(3)]
c.put(4, 4)                                      # 1 and 3 were both used twice, 1 is older, so it goes
out += [c.get(1), c.get(3), c.get(4)]
print(*out)
''', js=r'''
class LFUCache {
  constructor(capacity) {
    this.cap = capacity;
    this.val = new Map(); this.freq = new Map();
    this.groups = new Map();                         // use count -> Set of keys, oldest first
    this.low = 0;                                    // the smallest use count present
  }
  touch(key) {
    const f = this.freq.get(key), g = this.groups.get(f);
    g.delete(key);
    if (g.size === 0) { this.groups.delete(f); if (this.low === f) this.low++; }
    this.freq.set(key, f + 1);
    if (!this.groups.has(f + 1)) this.groups.set(f + 1, new Set());
    this.groups.get(f + 1).add(key);
  }
  get(key) {
    if (!this.val.has(key)) return -1;
    this.touch(key);
    return this.val.get(key);
  }
  put(key, value) {
    if (this.cap === 0) return;
    if (this.val.has(key)) { this.val.set(key, value); this.touch(key); return; }
    if (this.val.size === this.cap) {                // drop the least used, and the oldest among ties
      const g = this.groups.get(this.low), old = g.values().next().value;
      g.delete(old);
      if (g.size === 0) this.groups.delete(this.low);
      this.val.delete(old); this.freq.delete(old);
    }
    this.val.set(key, value); this.freq.set(key, 1); this.low = 1;
    if (!this.groups.has(1)) this.groups.set(1, new Set());
    this.groups.get(1).add(key);
  }
}

const c = new LFUCache(2);
c.put(1, 1);
c.put(2, 2);
const out = [c.get(1)];
c.put(3, 3);                                         // 2 was used least, so it goes
out.push(c.get(2), c.get(3));
c.put(4, 4);                                         // 1 and 3 were both used twice, 1 is older, so it goes
out.push(c.get(1), c.get(3), c.get(4));
console.log(out.join(" "));
''', java=r'''
import java.util.*;

public class LFUCache {
    int cap, low = 0;                                // low: the smallest use count present
    Map<Integer, Integer> val = new HashMap<>(), freq = new HashMap<>();
    Map<Integer, LinkedHashSet<Integer>> groups = new HashMap<>();   // use count -> keys, oldest first

    LFUCache(int capacity) { cap = capacity; }

    void touch(int key) {
        int f = freq.get(key);
        LinkedHashSet<Integer> g = groups.get(f);
        g.remove(key);
        if (g.isEmpty()) { groups.remove(f); if (low == f) low++; }
        freq.put(key, f + 1);
        groups.computeIfAbsent(f + 1, k -> new LinkedHashSet<>()).add(key);
    }

    int get(int key) {
        if (!val.containsKey(key)) return -1;
        touch(key);
        return val.get(key);
    }

    void put(int key, int value) {
        if (cap == 0) return;
        if (val.containsKey(key)) { val.put(key, value); touch(key); return; }
        if (val.size() == cap) {                     // drop the least used, and the oldest among ties
            LinkedHashSet<Integer> g = groups.get(low);
            int old = g.iterator().next();
            g.remove(old);
            if (g.isEmpty()) groups.remove(low);
            val.remove(old);
            freq.remove(old);
        }
        val.put(key, value);
        freq.put(key, 1);
        low = 1;
        groups.computeIfAbsent(1, k -> new LinkedHashSet<>()).add(key);
    }

    public static void main(String[] args) {
        LFUCache c = new LFUCache(2);
        c.put(1, 1);
        c.put(2, 2);
        List<Integer> out = new ArrayList<>(List.of(c.get(1)));
        c.put(3, 3);                                 // 2 was used least, so it goes
        out.add(c.get(2));
        out.add(c.get(3));
        c.put(4, 4);                                 // 1 and 3 were both used twice, 1 is older, so it goes
        out.add(c.get(1));
        out.add(c.get(3));
        out.add(c.get(4));
        StringBuilder sb = new StringBuilder();
        for (int k = 0; k < out.size(); k++) sb.append(k > 0 ? " " : "").append(out.get(k));
        System.out.println(sb);
    }
}
''', ts=r'''
class LFUCache {
  cap: number;
  val = new Map<number, number>();
  freq = new Map<number, number>();
  groups = new Map<number, Set<number>>();           // use count -> Set of keys, oldest first
  low = 0;                                           // the smallest use count present
  constructor(capacity: number) { this.cap = capacity; }
  touch(key: number): void {
    const f = this.freq.get(key) as number, g = this.groups.get(f) as Set<number>;
    g.delete(key);
    if (g.size === 0) { this.groups.delete(f); if (this.low === f) this.low++; }
    this.freq.set(key, f + 1);
    if (!this.groups.has(f + 1)) this.groups.set(f + 1, new Set());
    (this.groups.get(f + 1) as Set<number>).add(key);
  }
  get(key: number): number {
    if (!this.val.has(key)) return -1;
    this.touch(key);
    return this.val.get(key) as number;
  }
  put(key: number, value: number): void {
    if (this.cap === 0) return;
    if (this.val.has(key)) { this.val.set(key, value); this.touch(key); return; }
    if (this.val.size === this.cap) {                // drop the least used, and the oldest among ties
      const g = this.groups.get(this.low) as Set<number>, old = g.values().next().value as number;
      g.delete(old);
      if (g.size === 0) this.groups.delete(this.low);
      this.val.delete(old); this.freq.delete(old);
    }
    this.val.set(key, value); this.freq.set(key, 1); this.low = 1;
    if (!this.groups.has(1)) this.groups.set(1, new Set());
    (this.groups.get(1) as Set<number>).add(key);
  }
}

const c = new LFUCache(2);
c.put(1, 1);
c.put(2, 2);
const out: number[] = [c.get(1)];
c.put(3, 3);                                         // 2 was used least, so it goes
out.push(c.get(2), c.get(3));
c.put(4, 4);                                         // 1 and 3 were both used twice, 1 is older, so it goes
out.push(c.get(1), c.get(3), c.get(4));
console.log(out.join(" "));
''')

# ---------------------------------------------------------------- practice
t.leet(303, 'e', 'p_rangesum',
       statement='<p>Build a class over a fixed list of numbers. Each call sumRange(left, right) returns the sum of the numbers from index left to index right.</p>',
       example='nums = [-2, 0, 3, -5, 2, -1]\nsumRange(0, 2)  →  1\nsumRange(2, 5)  →  −1\nsumRange(0, 5)  →  −3',
       hint='Store the running totals once, then every answer is one subtraction.',
       approach='<p>Keep a prefix array where pre[i] is the sum of the first i numbers. The sum from left to right is pre[right + 1] − pre[left]. Building takes one pass and every query takes O(1). The list never changes, so nothing else is needed.</p>',
       time='O(n) to build, O(1) per query', space='O(n)')
t.leet(705, 'e', 'p_hashset',
       statement='<p>Design a hash set without a built in hash table. It must support add, remove and contains for whole number keys.</p>',
       example='add(1), add(2)\ncontains(1)  →  true\ncontains(3)  →  false\nadd(2), remove(2)\ncontains(2)  →  false',
       hint='Pick a prime number of buckets and keep a short list in each one.',
       approach='<p>Use 1009 buckets and send each key to bucket key mod 1009. Each bucket holds a small list, so keys that land in the same bucket, like 1 and 1010, both fit. A Bloom filter uses the same idea of hashing into slots, but it keeps only bits and so it can never remove a key.</p>',
       time='O(1) on average', space='O(buckets + keys)')
t.leet(2080, 'm', 'p_rangefreq',
       statement='<p>Build a class over a list. Each call query(left, right, value) returns how many times value appears between index left and index right.</p>',
       example='arr = [12, 33, 4, 56, 22, 2, 34, 33, 22, 12, 34, 56]\nquery(1, 2, 4)    →  1\nquery(0, 11, 33)  →  2',
       hint='For every value, keep the sorted list of places where it appears.',
       approach='<p>Walk the list once and append each index to the list of its value, so every list is already sorted. For a query, two binary searches find how many of those indexes are at least left and at most right. The difference is the count.</p>',
       time='O(n) to build, O(log n) per query', space='O(n)')
t.leet(307, 'm', 'p_rangemut', title='Range Sum Query - Mutable', url='https://leetcode.com/problems/range-sum-query-mutable/', diff='Medium',
       statement='<p>Like Range Sum Query, but the list can change. update(index, val) sets one number and sumRange(left, right) returns a sum.</p>',
       example='nums = [1, 3, 5]\nsumRange(0, 2)  →  9\nupdate(1, 2)\nsumRange(0, 2)  →  8',
       hint='Prefix sums break on every update. Split the list into blocks of about √n.',
       approach='<p>This is the square root decomposition from the lesson. Keep the total of every block. An update changes one cell and one block total. A sum adds the loose cells at both ends and the whole blocks in the middle, which is at most about 3√n steps. A segment tree or a Fenwick tree does both in O(log n).</p>',
       time='O(1) per update, O(√n) per sum', space='O(n)')
t.leet(146, 'h', 'p_lru',
       statement='<p>Design a cache with a fixed capacity. get returns a value or −1, and put stores a value. When the cache is full, put throws out the key that was used least recently.</p>',
       example='capacity 2\nput(1, 1), put(2, 2), get(1)  →  1\nput(3, 3)                     2 leaves\nget(2)                        →  −1',
       hint='A hash map finds a key in O(1). A list kept in order of use finds the oldest in O(1).',
       approach='<p>Join a hash map to a list ordered by use, with the oldest at the front. Every get or put moves the key to the back. When the cache grows past its capacity, remove the key at the front. An ordered dictionary, or a JavaScript Map, already keeps keys in this order.</p>',
       time='O(1) per call', space='O(capacity)')
t.leet(239, 'h', 'p_windowmax',
       statement='<p>A window of size k slides from the left of the list to the right, one step at a time. Return the biggest number in every window.</p>',
       example='[1, 3, −1, −3, 5, 3, 6, 7], k = 3  →  [3, 3, 5, 5, 6, 7]\n[1], k = 1                          →  [1]',
       hint='A smaller number that comes before a bigger one can never be a maximum again.',
       approach='<p>Keep a deque of indexes whose values go down from front to back. Before adding a new index, pop every smaller or equal value from the back. Drop the front once it slides out of the window. The front is always the maximum. A sparse table also answers each window in O(1), but it needs O(n log n) memory first.</p>',
       time='O(n)', space='O(k)')
t.leet(1206, 'x', 'p_skiplist', title='Design Skiplist', url='https://leetcode.com/problems/design-skiplist/', diff='Hard',
       statement='<p>Design a skip list without any built in library. It must support search, add and erase, and the same number may be added more than once.</p>',
       example='add(1), add(2), add(3)\nsearch(0)  →  false\nadd(4)\nsearch(1)  →  true\nerase(0)   →  false\nerase(1)   →  true\nsearch(1)  →  false',
       hint='Find the last node before the target on every lane, then link or unlink there.',
       approach='<p>Every operation first walks from the top lane down, moving right while the next value is smaller, and records the last node on each lane. Search checks the node after the bottom one. Add flips coins for the height and links the new node after the recorded nodes. Erase unlinks it from every lane where it appears.</p>',
       time='O(log n) expected per call', space='O(n) expected')
t.leet(460, 'x', 'p_lfu',
       statement='<p>Design a cache with a fixed capacity that throws out the key used the fewest times. If several keys share that count, the one used least recently leaves.</p>',
       example='capacity 2\nput(1, 1), put(2, 2)\nget(1)  →  1\nput(3, 3)    2 leaves\nget(2)  →  −1\nget(3)  →  3\nput(4, 4)    1 leaves\nget(1)  →  −1, get(3)  →  3, get(4)  →  4',
       hint='Group the keys by their use count, and remember the smallest count.',
       approach='<p>Keep three maps: key to value, key to use count, and use count to an ordered group of keys, oldest first. Using a key moves it from its group to the next one. The smallest count only grows by 1 when its group empties, and it resets to 1 when a new key arrives. To make room, remove the oldest key in the smallest group.</p>',
       time='O(1) per call', space='O(capacity)')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='skip-list', emoji='🛗', title='Skip lists: express lanes over a linked list', html='''
<p>Searching a sorted linked list means walking it one node at a time. A <b>skip list</b> adds lanes on top. Every key sits in the bottom lane, and a coin flip decides whether it also joins the lane above, then the next, and so on. A search starts in the top lane at the head, moves right while the next key is smaller, and drops down one lane when it would overshoot.</p>
<div class="viz" data-viz="pk" data-pk="skip"></div>
<div class="c3" data-k="skiplist" data-label="Skip list with coin flip lanes"></div>
<span class="eq">with a fair coin: about n ÷ 2<sup>k</sup> keys reach lane k, so there are about log<sub>2</sub> n lanes</span>
<div class="tip">William Pugh described skip lists in 1990. Redis keeps its sorted sets in a skip list, because inserting and deleting only change a few links.</div>
'''),
    dict(id='bloom-filter', emoji='🌸', title='Bloom filters: maybe, or definitely not', html='''
<p>A <b>Bloom filter</b> answers "have I seen this word?" with a row of bits and nothing else. Adding a word sets the bits at a few hash positions. Asking about a word checks those same positions. If any bit is 0, the word was <b>definitely never added</b>. If all of them are 1, the word is <b>maybe present</b>, because other words may have set those bits.</p>
<div class="viz" data-viz="pk" data-pk="bloom"></div>
<div class="c3" data-k="bloom" data-label="Bloom filter with three hash positions"></div>
<span class="eq">false positive chance ≈ ( 1 − e<sup>−kn ÷ m</sup> )<sup>k</sup> &nbsp; for m bits, n words and k hashes</span>
<div class="warn">A plain Bloom filter cannot remove a word. Clearing its bits could also clear bits that another word needs, and then that word would be reported as absent.</div>
'''),
    dict(id='count-min', emoji='🧮', title='Count-min sketch: counting in a small table', html='''
<p>Counting every word in a huge stream needs one counter per distinct word. A <b>count-min sketch</b> uses a small table instead: a few rows of counters, each row with its own hash. Every word adds 1 to one counter in every row. To estimate a count, read the word's counter in each row and take the <b>smallest</b>.</p>
<div class="viz" data-viz="pk" data-pk="countmin"></div>
<div class="c3" data-k="countmin" data-label="Count-min sketch with three rows"></div>
<div class="tw"><table class="jt"><tr><th>Word</th><th>True count</th><th>Estimate</th></tr>
<tr><td>the</td><td>4</td><td>4</td></tr>
<tr><td>cat</td><td>2</td><td>2</td></tr>
<tr><td>owl</td><td>1</td><td>2</td></tr>
<tr><td>fox</td><td>0</td><td>0</td></tr></table></div>
<div class="exam">Collisions only ever add to a counter, so the estimate is never smaller than the true count. More columns make collisions rarer, and more rows make it less likely that every row collides at once.</div>
'''),
    dict(id='sparse-table', emoji='🧱', title='Sparse tables: range minimum in O(1)', html='''
<p>A <b>sparse table</b> answers "what is the smallest value between l and r?" for a list that never changes. Row j stores the minimum of every block of 2<sup>j</sup> values, and each row is built from two halves in the row before. A query picks the biggest power of 2 that fits the range and looks at two blocks: one starting at l and one ending at r.</p>
<div class="viz" data-viz="pk" data-pk="sparse"></div>
<div class="c3" data-k="sparse" data-label="Sparse table for range minimum"></div>
<span class="eq">j = ⌊ log<sub>2</sub>( r − l + 1 ) ⌋ &nbsp;&nbsp; min = min( t[j][l], t[j][r − 2<sup>j</sup> + 1] )</span>
<div class="tip">The two blocks may overlap. That is fine for minimum, maximum and gcd, because counting a value twice does not change the answer. It does not work for sums.</div>
'''),
    dict(id='sqrt-decomposition', emoji='🧩', title='Square root decomposition', html='''
<p>Prefix sums answer a range sum in O(1) but need O(n) work after a change. <b>Square root decomposition</b> finds a middle ground. Cut the list into blocks of about √n cells and keep the total of every block. A query adds the loose cells at both ends and the whole blocks in between. An update changes one cell and one block total.</p>
<div class="viz" data-viz="pk" data-pk="sqrtdec"></div>
<div class="c3" data-k="sqrtdec" data-label="Block sums with point updates"></div>
<div class="tw"><table class="jt"><tr><th>Structure</th><th>Range sum</th><th>Change one value</th></tr>
<tr><td>Prefix sums</td><td>O(1)</td><td>O(n)</td></tr>
<tr><td>Square root blocks</td><td>O(√n)</td><td>O(1)</td></tr>
<tr><td>Segment tree or Fenwick tree</td><td>O(log n)</td><td>O(log n)</td></tr></table></div>
<div class="tip">The same block idea answers harder questions too, such as "how many values below x in this range", by keeping each block sorted.</div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem is solved in the Practice section in Python, JavaScript, Java and TypeScript, with line by line replay. Each one builds a structure that answers its questions faster than a plain list.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>Tool</th></tr>
<tr><td><a href="#lc303">303. Range Sum Query - Immutable</a></td><td>Easy</td><td>prefix sums</td></tr>
<tr><td><a href="#lc705">705. Design HashSet</a></td><td>Easy</td><td>hash buckets</td></tr>
<tr><td><a href="#lc2080">2080. Range Frequency Queries</a></td><td>Medium</td><td>position lists and binary search</td></tr>
<tr><td><a href="#lc307">307. Range Sum Query - Mutable</a></td><td>Medium</td><td>square root decomposition</td></tr>
<tr><td><a href="#lc146">146. LRU Cache</a></td><td>Hard</td><td>hash map with a use ordered list</td></tr>
<tr><td><a href="#lc239">239. Sliding Window Maximum</a></td><td>Hard</td><td>monotonic deque</td></tr>
<tr><td><a href="#lc1206">1206. Design Skiplist</a></td><td>Expert</td><td>skip list</td></tr>
<tr><td><a href="#lc460">460. LFU Cache</a></td><td>Expert</td><td>groups by use count</td></tr></table></div>
'''),
]

VIZ_JS = r'''
(() => {
  const D = PK.defs;
  const pick = a => a[Math.floor(Math.random() * a.length)];
  const rnd = (lo, hi) => lo + Math.floor(Math.random() * (hi - lo + 1));

  /* ---------- skip list ---------- */
  const KEYS = [3, 6, 7, 9, 12, 19, 17, 26, 21, 25];
  const skipLevels = () => {                    /* same repeatable coin flips as the lesson program */
    let seed = 7;
    const coin = () => { seed = (seed * 75 + 74) % 65537; return seed % 2; };
    const lv = {};
    for (const k of KEYS) { let l = 1; while (l < 4 && coin()) l++; lv[k] = l; }
    return lv;
  };
  D.skip = el => PK.widget(el, {
    title: 'Take the express lane', sub: 'Each key flips coins to decide how many lanes it joins. Search runs right on the top lane while the next key is still smaller, then drops down.',
    inputs: [{ k: 'x', label: 'Find', type: 'num', val: 19, min: 0, max: 30, w: 70 }],
    random: () => ({ x: pick([19, 25, 5, 12, 21, 30, 3, 14]) }),
    check: v => Number.isInteger(v.x) && v.x >= 0 && v.x <= 30 ? '' : 'Pick a number from 0 to 30.',
    frames: ({ x }) => {
      const lv = skipLevels(), keys = KEYS.slice().sort((a, b) => a - b), top = Math.max(...Object.values(lv)), F = [];
      const rows = [];
      for (let l = top - 1; l >= 0; l--) rows.push(['🏁'].concat(keys.map(k => (lv[k] > l ? k : '—'))));
      const rlab = Array.from({ length: top }, (_, r) => 'lane ' + (top - 1 - r));
      const base = {};
      rows.forEach((row, r) => row.forEach((v, c) => { if (v === '—') base[r + ',' + c] = 'wall'; }));
      const pic = cls => [{ t: 'grid', label: 'Lanes, with the start on the left', rows, rlab, cls: Object.assign({}, base, cls) }];
      F.push({ mood: 'think', msg: `${keys.length} keys. Lane 0 holds every key, and each higher lane holds about half of the lane below. Find ${x}.`, vars: { target: x }, layers: pic({}) });
      let col = 0, moves = 0;
      const trail = {};
      for (let l = top - 1; l >= 0; l--) {
        const r = top - 1 - l;
        trail[r + ',' + col] = 'look';
        while (true) {
          let nc = col + 1;
          while (nc <= keys.length && lv[keys[nc - 1]] <= l) nc++;
          if (nc > keys.length || keys[nc - 1] >= x) {
            F.push({ mood: 'look', msg: nc > keys.length ? `Lane ${l}: nothing further right. Drop down.` : `Lane ${l}: next is ${keys[nc - 1]}, not smaller than ${x}. Drop down.`, vars: { lane: l, moves }, layers: pic(Object.assign({}, trail, { [r + ',' + col]: 'cur' }, nc <= keys.length ? { [r + ',' + nc]: 'no' } : {})) });
            break;
          }
          col = nc; moves++;
          trail[r + ',' + col] = 'look';
          F.push({ mood: 'work', msg: `Lane ${l}: ${keys[col - 1]} is smaller than ${x}, so zoom right to it.`, vars: { lane: l, moves }, layers: pic(Object.assign({}, trail, { [r + ',' + col]: 'cur' })) });
        }
      }
      const found = col < keys.length && keys[col] === x;
      const last = top - 1;
      F.push(found
        ? { mood: 'wow', fx: 'rain', msg: `The next key on lane 0 is <b>${x}</b>. Found after ${moves} move${moves === 1 ? '' : 's'} to the right, against ${keys.indexOf(x) + 1} steps walking lane 0 alone.`, vars: { moves }, layers: pic(Object.assign({}, trail, { [last + ',' + (col + 1)]: 'win' })) }
        : { mood: 'sad', fx: 'shake', msg: `The next key on lane 0 is ${col < keys.length ? keys[col] : 'the end'}, not ${x}. ${x} is not in the list, and the express lanes found that out in ${moves} move${moves === 1 ? '' : 's'}.`, vars: { moves }, layers: pic(trail) });
      return F;
    }
  });

  /* ---------- Bloom filter ---------- */
  const M = 32;
  const ph = (w, b, m) => { let h = 0; for (const ch of w) h = (h * b + ch.charCodeAt(0)) % m; return h; };
  const bpos = w => { const h1 = ph(w, 31, 1000003), h2 = ph(w, 37, 1000033) | 1; return [0, 1, 2].map(i => (h1 + i * h2) % M); };
  D.bloom = el => PK.widget(el, {
    title: 'A set that can say "maybe"', sub: 'Each word switches on 3 bits. A query whose bits are all on says maybe. Any bit off means definitely not.',
    inputs: [{ k: 'q', label: 'Ask about', type: 'text', val: 'hog', w: 100 }],
    random: () => ({ q: pick(['hog', 'cat', 'ant', 'yak', 'his', 'owl', 'emu', 'boo']) }),
    check: v => /^[a-z]{1,8}$/.test(String(v.q).trim().toLowerCase()) ? '' : 'Type a word of 1 to 8 letters.',
    frames: ({ q }) => {
      q = q.trim().toLowerCase();
      const words = ['cat', 'dog', 'owl', 'fox', 'bee'], bits = new Array(M).fill(0), F = [];
      const pic = (cls = {}, ptr = {}) => [{ t: 'row', label: `${M} bits`, cells: bits.slice(), small: true, cls: Object.assign(Object.fromEntries(bits.map((b, i) => [i, b ? 'done' : ''])), cls), ptr }];
      F.push({ mood: 'think', msg: 'An empty filter: all 32 bits are 0. Add five animals.', vars: {}, layers: pic() });
      for (const w of words) {
        const ps = bpos(w);
        ps.forEach(p => { bits[p] = 1; });
        F.push({ mood: 'work', msg: `Add "${w}": hashes point at bits ${ps.join(', ')}. Switch them on.`, vars: { word: w, 'bits on': bits.reduce((a, b) => a + b, 0) }, layers: pic(Object.fromEntries(ps.map(p => [p, 'yes']))) });
      }
      const ps = bpos(q), off = ps.filter(p => !bits[p]), cls = Object.fromEntries(ps.map(p => [p, bits[p] ? 'look' : 'no'])), ptr = Object.fromEntries(ps.map(p => [p, '?']));
      F.push({ mood: 'look', msg: `Ask about "${q}": check bits ${ps.join(', ')}.`, vars: { word: q }, layers: pic(cls, ptr) });
      if (off.length) F.push({ mood: 'happy', msg: `Bit ${off.join(' and ')} is 0, so "${q}" was <b>definitely never added</b>. A Bloom filter never gets a no wrong.`, vars: { word: q }, layers: pic(cls, ptr) });
      else if (words.includes(q)) F.push({ mood: 'wow', fx: 'rain', msg: `All three bits are on: "${q}" is <b>maybe present</b>, and here it really was added.`, vars: { word: q }, layers: pic(Object.fromEntries(ps.map(p => [p, 'win']))) });
      else F.push({ mood: 'sad', fx: 'shake', msg: `All three bits are on, so the filter says <b>maybe</b>, but "${q}" was never added! Other words switched those bits on. That is a false positive, the price of using so little memory.`, vars: { word: q }, layers: pic(Object.fromEntries(ps.map(p => [p, 'piv']))) });
      return F;
    }
  });

  /* ---------- count-min sketch ---------- */
  const W = 8, BASES = [31, 37, 41];
  const cmcol = (w, r) => ph(w, BASES[r], 1000003) % W;
  D.countmin = el => PK.widget(el, {
    title: 'Count a stream in a tiny table', sub: 'Every word adds 1 to one counter in each row. Collisions only add, so the smallest of its counters is the best guess.',
    inputs: [{ k: 'q', label: 'How many', type: 'seg', val: 'owl', opts: [['the', 'the'], ['cat', 'cat'], ['owl', 'owl'], ['fox', 'fox']] }],
    frames: ({ q }) => {
      const stream = 'the cat and the dog and the owl saw the cat'.split(' '), T = [0, 1, 2].map(() => new Array(W).fill(0)), F = [];
      const pic = cls => [{ t: 'grid', label: '3 rows of 8 counters, one hash per row', rows: T.map(r => r.slice()), rlab: ['row 0', 'row 1', 'row 2'], clab: [...Array(W).keys()], cls, sq: true }];
      F.push({ mood: 'think', msg: `Stream: "${stream.join(' ')}". Only 24 counters, however many different words arrive.`, vars: {}, layers: pic({}) });
      stream.forEach((w, i) => {
        const cls = {};
        for (let r = 0; r < 3; r++) { T[r][cmcol(w, r)]++; cls[r + ',' + cmcol(w, r)] = 'yes'; }
        F.push({ mood: 'work', msg: `"${w}": add 1 in column ${[0, 1, 2].map(r => cmcol(w, r)).join(', ')} of rows 0, 1, 2.`, vars: { words: i + 1 }, layers: pic(cls) });
      });
      const vals = [0, 1, 2].map(r => T[r][cmcol(q, r)]), est = Math.min(...vals), truth = stream.filter(x => x === q).length;
      const cls = Object.fromEntries([0, 1, 2].map(r => [r + ',' + cmcol(q, r), T[r][cmcol(q, r)] === est ? 'win' : 'look']));
      F.push({ mood: 'look', msg: `"${q}" points at counters ${vals.join(', ')}. Take the smallest: <b>${est}</b>.`, vars: { estimate: est }, layers: pic(cls) });
      F.push(est === truth
        ? { mood: 'wow', fx: 'rain', msg: `Estimate ${est}, true count ${truth}. Spot on${truth === 0 ? ': it never appeared' : ''}.`, vars: { estimate: est, truth }, layers: pic(cls) }
        : { mood: 'sad', msg: `Estimate ${est}, but the true count is ${truth}. Other words share all its counters, so it is counted too high. A count-min sketch can be too high, never too low.`, vars: { estimate: est, truth }, layers: pic(cls) });
      return F;
    }
  });

  /* ---------- sparse table ---------- */
  D.sparse = el => PK.widget(el, {
    title: 'Minimum of any range in one step', sub: 'Row j stores the minimum of every block of 2^j values. Any range is covered by two blocks of the same size, overlapping is fine.',
    inputs: [{ k: 'l', label: 'From', type: 'num', val: 2, min: 0, max: 7, w: 60 }, { k: 'r', label: 'To', type: 'num', val: 6, min: 0, max: 7, w: 60 }],
    random: () => { const l = rnd(0, 6); return { l, r: rnd(l, 7) }; },
    check: v => Number.isInteger(v.l) && Number.isInteger(v.r) && v.l >= 0 && v.r <= 7 && v.l <= v.r ? '' : 'Pick 0 ≤ from ≤ to ≤ 7.',
    frames: ({ l, r }) => {
      const a = [5, 2, 4, 7, 1, 3, 6, 8], n = a.length, T = [a.slice()], F = [];
      const pic = cls => [
        { t: 'row', label: 'Values', cells: a, cls: Object.fromEntries(a.map((_, i) => [i, i >= l && i <= r ? 'sel' : ''])) },
        { t: 'grid', label: 'Sparse table: row j holds blocks of 2^j', rows: T.map(row => row.concat(new Array(n - row.length).fill(''))), rlab: T.map((_, j) => 'size ' + (1 << j)), clab: [...Array(n).keys()], cls, sq: true },
      ];
      F.push({ mood: 'think', msg: 'Row 0 is the values themselves. Each next row joins two blocks from the row above.', vars: {}, layers: pic({}) });
      for (let j = 1; (1 << j) <= n; j++) {
        const prev = T[j - 1], half = 1 << (j - 1), row = [];
        for (let i = 0; i + (1 << j) <= n; i++) row.push(Math.min(prev[i], prev[i + half]));
        T.push(row);
        F.push({ mood: 'work', msg: `Blocks of ${1 << j}: each is the smaller of two blocks of ${half}. Only ${n * T.length} boxes in all, O(n log n).`, vars: { size: 1 << j }, layers: pic(Object.fromEntries(row.map((_, i) => [j + ',' + i, 'yes']))) });
      }
      const len = r - l + 1, j = 31 - Math.clz32(len), b2 = r - (1 << j) + 1, ans = Math.min(T[j][l], T[j][b2]);
      F.push({ mood: 'look', msg: `Range ${l} to ${r} has ${len} values. The biggest power of 2 that fits is ${1 << j}. Use the block starting at ${l} and the block starting at ${b2}.`, vars: { length: len, block: 1 << j }, layers: pic({ [j + ',' + l]: 'look', [j + ',' + b2]: 'look' }) });
      F.push({ mood: 'wow', fx: 'rain', msg: `min(${T[j][l]}, ${T[j][b2]}) = <b>${ans}</b>. Two lookups, no loop, whatever the range. This works for min and max because counting a value twice does not change the answer.`, vars: { min: ans }, layers: pic({ [j + ',' + l]: T[j][l] === ans ? 'win' : 'look', [j + ',' + b2]: T[j][b2] === ans ? 'win' : 'look' }) });
      return F;
    }
  });

  /* ---------- square root decomposition ---------- */
  D.sqrtdec = el => PK.widget(el, {
    title: 'Chop the array into blocks', sub: 'Keep a total for each block of about √n cells. A range sum adds a few loose cells and a few whole block totals.',
    inputs: [{ k: 'l', label: 'From', type: 'num', val: 1, min: 0, max: 8, w: 60 }, { k: 'r', label: 'To', type: 'num', val: 7, min: 0, max: 8, w: 60 }, { k: 'u', label: 'Then', type: 'seg', val: 'yes', opts: [['yes', 'set a[4] = 10'], ['no', 'no update']] }],
    random: () => { const l = rnd(0, 6); return { l, r: rnd(l, 8), u: pick(['yes', 'no']) }; },
    check: v => Number.isInteger(v.l) && Number.isInteger(v.r) && v.l >= 0 && v.r <= 8 && v.l <= v.r ? '' : 'Pick 0 ≤ from ≤ to ≤ 8.',
    frames: ({ l, r, u }) => {
      const a = [3, 1, 4, 1, 5, 9, 2, 6, 5], S = 3, blocks = [0, 0, 0], F = [];
      a.forEach((x, i) => { blocks[Math.floor(i / S)] += x; });
      const pic = (cls = {}, bcls = {}) => [
        { t: 'row', label: 'Array, in blocks of 3', cells: a.slice(), cls, tag: Object.fromEntries(a.map((_, i) => [i, 'block ' + Math.floor(i / S)])) },
        { t: 'row', label: 'Block totals', cells: blocks.slice(), cls: bcls, idx: false },
      ];
      const query = () => {
        let i = l, total = 0;
        const cls = {}, bcls = {};
        F.push({ mood: 'think', msg: `Sum of a[${l}..${r}].`, vars: { total: 0 }, layers: pic(Object.fromEntries(a.map((_, k) => [k, k >= l && k <= r ? 'sel' : '']))) });
        while (i <= r && i % S) { total += a[i]; cls[i] = 'yes'; i++; }
        if (Object.keys(cls).length) F.push({ mood: 'work', msg: `Loose cells on the left: ${Object.keys(cls).map(k => a[k]).join(' + ')}. Total ${total}.`, vars: { total }, layers: pic(Object.assign({}, cls), Object.assign({}, bcls)) });
        while (i + S - 1 <= r) { total += blocks[i / S]; bcls[i / S] = 'win'; for (let k = i; k < i + S; k++) cls[k] = 'done'; F.push({ mood: 'happy', msg: `Block ${i / S} fits completely: add its total ${blocks[i / S]} in one step. Total ${total}.`, vars: { total }, layers: pic(Object.assign({}, cls), Object.assign({}, bcls)) }); i += S; }
        const right = [];
        while (i <= r) { total += a[i]; cls[i] = 'yes'; right.push(a[i]); i++; }
        if (right.length) F.push({ mood: 'work', msg: `Loose cells on the right: ${right.join(' + ')}. Total ${total}.`, vars: { total }, layers: pic(Object.assign({}, cls), Object.assign({}, bcls)) });
        return total;
      };
      const t1 = query();
      F.push({ mood: 'wow', fx: u === 'yes' ? undefined : 'rain', msg: `Sum = <b>${t1}</b>. At most 2 partial blocks and √n whole blocks, so O(√n) per query.`, vars: { sum: t1 }, layers: pic() });
      if (u === 'yes') {
        blocks[1] += 10 - a[4]; a[4] = 10;
        F.push({ mood: 'work', msg: 'Update a[4] from 5 to 10: change the cell and add 5 to block 1. That is O(1).', vars: {}, layers: pic({ 4: 'mv' }, { 1: 'mv' }) });
        const t2 = query();
        F.push({ mood: 'wow', fx: 'rain', msg: `After the update the sum is <b>${t2}</b>. Prefix sums would need O(n) to update, a sparse table cannot update at all, and blocks handle both in about √n.`, vars: { sum: t2 }, layers: pic() });
      }
      return F;
    }
  });
})();
'''

INFO = {
    'title': 'Trade a little memory or certainty for a lot of speed',
    'panels': [
        {'s': [['e', '🛗'], ['t', 'lanes', {'b': 1}]], 'h': 'Skip list', 't': 'Sorted, with express lanes.', 'more': 'O(log n) expected.'},
        {'s': [['e', '🌸'], ['t', 'bits', {'b': 1}]], 'h': 'Bloom filter', 't': 'Maybe, or definitely not.', 'more': 'No false negatives.'},
        {'s': [['e', '🧮'], ['t', 'min of rows', {'b': 1}]], 'h': 'Count-min', 't': 'Counts in a small table.', 'more': 'Never under the truth.'},
        {'s': [['e', '🧱'], ['t', '2 blocks', {'b': 1}]], 'h': 'Sparse table', 't': 'Range minimum in O(1).', 'more': 'Square root blocks allow updates.'},
    ],
    'remember': 'Each structure gives up something small, a little extra memory, a coin flip or a chance of a wrong maybe, so that its main question can be answered in very few steps.',
}

REAL = [
    ['🗄️', 'Databases and key value stores', 'Cassandra, LevelDB and RocksDB keep a Bloom filter per data file, so a lookup can skip files that surely do not hold the key.'],
    ['🏁', 'Leaderboards', 'Redis sorted sets use a skip list, so a score update and a rank lookup each take about log n steps.'],
    ['📈', 'Network and traffic monitoring', 'Count-min sketches estimate how often each address or search term appears in a stream far too big to count exactly.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to special data structures. Each one gives up a little memory or a little certainty to answer one question very fast. You will search a skip list with express lanes, test words with a Bloom filter, count words with a count-min sketch, find range minimums with a sparse table, and split a list into square root blocks.'},
    {'id': 'skip-list', 'h': 'Skip list', 'en': 'A skip list is a sorted linked list with extra lanes on top. A coin flip decides how many lanes each key joins. A search starts in the top lane, moves right while the next key is smaller, and drops down a lane before it would overshoot. On average that takes about log n steps.'},
    {'id': 'bloom-filter', 'h': 'Bloom filter', 'en': 'A Bloom filter is a row of bits. Adding a word sets the bits at a few hash positions. If any of those bits is zero when you ask, the word was never added. If all of them are one, the word is only maybe present, because other words can set the same bits.'},
    {'id': 'count-min', 'h': 'Count-min sketch', 'en': 'A count-min sketch keeps a few rows of counters, each with its own hash. Every word adds one to a counter in every row. To estimate a count, read all of its counters and take the smallest. Collisions only add, so the estimate is never below the true count.'},
    {'id': 'sparse-table', 'h': 'Sparse table', 'en': 'A sparse table stores the minimum of every block whose length is a power of two. A query takes the biggest power of two that fits, and compares one block from the left end with one block from the right end. The blocks may overlap, which does no harm for a minimum.'},
    {'id': 'sqrt-decomposition', 'h': 'Square root blocks', 'en': 'Square root decomposition cuts the list into blocks of about the square root of n cells and keeps each block total. A sum adds the loose cells at both ends and the whole blocks between them. An update changes one cell and one total.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from range sums to an LFU cache. Each one is solved in Python, JavaScript, Java and TypeScript, and you can replay every solution line by line.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. For each problem, think about which question must be fast, and which structure answers it: prefix sums, blocks, a deque, a skip list or a pair of maps. Open the hint if you are stuck.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'A Bloom filter says a word is definitely absent. Can that be wrong?', 'o': ['Yes, often', 'No, a word that was added always has all its bits set', 'Only for long words', 'Only when the filter is empty'], 'a': 1, 'hint': 'Adding a word sets its bits, and nothing clears them.', 'why': 'Bits are only ever set, so a word that was added still finds every one of its bits at 1.'},
    {'lv': 'e', 'q': 'Where does a skip list search start?', 'o': ['At the last key', 'At the head, in the top lane', 'In the bottom lane at a random key', 'In the middle'], 'a': 1, 'hint': 'The top lane skips the most keys.', 'why': 'Starting high lets the search skip large stretches, then it drops down to finer lanes.'},
    {'lv': 'e', 'q': 'How does a count-min estimate compare with the true count?', 'o': ['It can be smaller', 'It is never smaller', 'It is always exact', 'It is always double'], 'a': 1, 'hint': 'Collisions only add.', 'why': 'Every counter holds the true count plus whatever other words collided with it.'},
    {'lv': 'e', 'q': 'For a list of 100 values, what block size does square root decomposition use?', 'o': ['2', '10', '50', '100'], 'a': 1, 'hint': 'The square root of 100.', 'why': 'Blocks of about √n, and √100 = 10.'},
    {'lv': 'm', 'q': 'Why may the two blocks of a sparse table query overlap for a minimum?', 'o': ['They never overlap', 'Counting a value twice does not change a minimum', 'The table removes the overlap', 'The overlap is always empty'], 'a': 1, 'hint': 'min(x, x) = x.', 'why': 'Minimum is idempotent, so values in the overlap can be counted twice without harm.'},
    {'lv': 'm', 'q': 'Why can a sparse table not answer range sums with two overlapping blocks?', 'o': ['Sums are too big', 'Values in the overlap would be added twice', 'Sums need sorting', 'It can, the same way'], 'a': 1, 'hint': 'x + x is not x.', 'why': 'For a sum, counting the overlap twice gives a wrong answer.'},
    {'lv': 'm', 'q': 'What is the expected time of a skip list search?', 'o': ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)'], 'a': 1, 'hint': 'About log n lanes, a few moves per lane.', 'why': 'There are about log n lanes, and on average only a couple of moves right happen on each one.'},
    {'lv': 'm', 'q': 'Why can a plain Bloom filter not remove a word?', 'o': ['It has no remove button', 'Clearing its bits could clear bits another word needs', 'Removing is too slow', 'The bits are read only'], 'a': 1, 'hint': 'Two words can share a bit.', 'why': 'If a shared bit is cleared, a word that is still present would be reported as absent.'},
    {'lv': 'h', 'q': 'A sparse table query covers 6 values. What block length does it use?', 'o': ['2', '4', '6', '8'], 'a': 1, 'hint': 'The biggest power of 2 that is at most 6.', 'why': '⌊log₂ 6⌋ = 2, so the blocks have 2² = 4 values and two of them cover all 6.'},
    {'lv': 'h', 'q': 'Why does count-min take the minimum over its rows?', 'o': ['To save memory', 'Each row can only be too high, so the smallest row is closest to the truth', 'To make it random', 'Rows hold different words'], 'a': 1, 'hint': 'Every error is extra.', 'why': 'All rows overcount or count exactly, so the smallest value has the least extra.'},
    {'lv': 'h', 'q': 'With block totals, what does changing one value cost in square root decomposition?', 'o': ['O(1)', 'O(√n)', 'O(n)', 'O(log n)'], 'a': 0, 'hint': 'One cell and one total change.', 'why': 'Set the cell and add the difference to its block total. Nothing else changes.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'a = [4, 6, 1, 5]\npre = [0]\nfor x in a:\n    pre.append(pre[-1] + x)\nprint(pre[4] - pre[1])', 'o': ['12', '16', '11', '10'], 'a': 0, 'hint': 'It is the sum of a[1..3].', 'why': 'pre is [0, 4, 10, 11, 16], and 16 − 4 = 12, which is 6 + 1 + 5.'},
    {'lv': 'x', 'q': 'For m bits and n words, about how many hash positions k keep a Bloom filter\'s false positives lowest?', 'o': ['k = 1', 'k = (m ÷ n) × ln 2', 'k = m', 'k = n'], 'a': 1, 'hint': 'About half the bits should end up set.', 'why': 'That choice leaves roughly half the bits at 1, which gives the lowest false positive rate.'},
    {'lv': 'x', 'q': 'How much memory does a sparse table over n values use?', 'o': ['O(n)', 'O(n log n)', 'O(n²)', 'O(log n)'], 'a': 1, 'hint': 'About log n rows of at most n values.', 'why': 'There is one row for every power of 2 up to n, and each row has at most n entries.'},
    {'lv': 'x', 'q': 'In an LFU cache, two keys have the same smallest use count. Which one leaves?', 'o': ['The bigger key', 'The one used least recently', 'Both', 'A random one'], 'a': 1, 'hint': 'Ties fall back to LRU.', 'why': 'Among keys with the smallest count, the one whose last use is oldest is removed.'},
    {'lv': 'x', 'q': 'With a fair coin, what is the chance that a new key reaches lane 3, counting the bottom lane as lane 0?', 'o': ['1 ÷ 2', '1 ÷ 4', '1 ÷ 8', '1 ÷ 16'], 'a': 2, 'hint': 'It needs three heads in a row.', 'why': 'Each lane above the bottom needs one more head, so lane 3 needs three: (1 ÷ 2)³ = 1 ÷ 8.'},
]

CALC = [
    {'lv': 'e', 'q': 'nums = [-2, 0, 3, -5, 2, -1]. What is the sum from index 2 to index 5?', 'ans': '-1', 'hint': '3 − 5 + 2 − 1.', 'steps': ['<span class="eq">3 + (−5) + 2 + (−1) = −1</span>']},
    {'lv': 'e', 'q': 'A count-min sketch has 3 rows of 8 counters. How many counters is that?', 'ans': '24', 'hint': 'Rows times columns.', 'steps': ['<span class="eq">3 × 8 = 24</span>']},
    {'lv': 'm', 'q': 'How many entries does a sparse table over 8 values hold in total?', 'ans': '21', 'hint': 'Rows for blocks of 1, 2, 4 and 8.', 'steps': ['Blocks of 1: 8 entries. Blocks of 2: 7. Blocks of 4: 5. Blocks of 8: 1.', '<span class="eq">8 + 7 + 5 + 1 = 21</span>']},
    {'lv': 'm', 'q': 'An LRU cache of capacity 2 runs put(1), put(2), get(1), put(3). Which key leaves?', 'ans': '2', 'hint': 'get(1) made key 1 the newest.', 'steps': ['After get(1) the order of use is 2, then 1.', 'put(3) overflows, so the least recently used key 2 leaves.']},
    {'lv': 'h', 'q': 'With a fair coin, about how many lanes does a skip list of 1024 keys have?', 'ans': '10', 'hint': 'log₂ 1024.', 'steps': ['About half the keys reach each next lane.', '<span class="eq">log₂ 1024 = 10</span>']},
    {'lv': 'h', 'q': 'a = [5, 2, 4, 7, 1, 3, 6, 8]. What is the minimum of a[5..7]?', 'ans': '3', 'hint': 'The values are 3, 6 and 8.', 'steps': ['Length 3, so j = 1 and the blocks have 2 values.', '<span class="eq">min( t[1][5], t[1][6] ) = min( 3, 6 ) = 3</span>']},
    {'lv': 'x', 'q': 'A Bloom filter has m = 32 bits, n = 5 words and k = 3 hashes. Roughly what is the false positive chance, as a whole percent?', 'ans': '5', 'hint': '( 1 − e^(−15 ÷ 32) )³.', 'steps': ['<span class="eq">e<sup>−15 ÷ 32</sup> ≈ 0.626</span>', '<span class="eq">( 1 − 0.626 )³ ≈ 0.374³ ≈ 0.052</span>', 'That is about 5 percent.']},
    {'lv': 'x', 'q': 'A list of 10000 values uses square root blocks. At most how many whole blocks does one query add?', 'ans': '100', 'hint': 'The block size is √10000.', 'steps': ['Blocks of 100 cells, so there are 100 blocks.', 'A query can add at most all 100 of them, plus fewer than 200 loose cells.']},
]

TALK = {
    'skip-list': 'A sorted linked list is easy to keep in order, but finding a key means walking it one node at a time. A skip list fixes that with express lanes. Every key lives in the bottom lane. When a key is inserted, we flip a coin. Heads, and the key also joins the lane above. Heads again, and it joins the next lane up, and so on. About half the keys reach lane one, a quarter reach lane two, and so on, so there are about log n lanes. To search, start at the head in the top lane. Move right while the next key is still smaller than the one you want. When the next key would overshoot, drop down one lane and carry on. In the bottom lane, the next node is either your key or proof that it is missing. In the animation, finding nineteen takes only six moves to the right.',
    'bloom-filter': 'Sometimes you only need to know whether you have seen something before, and you have very little memory. A Bloom filter uses just a row of bits, all zero at the start. To add a word, compute a few hash positions for it and set those bits to one. To ask about a word, compute the same positions and look. If even one of those bits is still zero, the word was definitely never added, because adding it would have set that bit. If every bit is one, the answer is maybe, because other words might have set those bits. In the animation, cat is present, ant is definitely absent, and hog is a false positive: its three bits were all set by other words. More bits, or the right number of hashes, make false positives rarer. A plain Bloom filter cannot remove a word, because clearing a bit could break another word.',
    'count-min': 'Imagine counting every search term typed into a busy website. There are far too many different terms to give each one its own counter. A count-min sketch uses a small table instead. It has a few rows, each with a handful of counters and its own hash. When a word arrives, each row hashes it to one counter and adds one. Different words sometimes land on the same counter, which makes that counter too high. To estimate a word\'s count, look up its counter in every row and take the smallest one. A collision can only add to a counter, never subtract, so the estimate is never smaller than the truth. Taking the minimum picks the row with the least extra. In the animation, the and cat are counted exactly, owl is estimated as two instead of one, and fox correctly gets zero.',
    'sparse-table': 'A sparse table answers range minimum questions instantly, as long as the list never changes. Row zero is the list itself. Row one holds the minimum of every pair of neighbours. Row two holds the minimum of every block of four, built by comparing two blocks of two from the row before. Each new row doubles the block length. Now suppose you want the minimum between positions l and r. Find the biggest power of two that fits inside that range. Take one block of that length starting at l, and another ending exactly at r. Together they cover the whole range, though they may overlap in the middle. For a minimum, the overlap does no harm, because seeing a value twice does not change the smallest one. So every query is just two lookups. The same trick works for maximum and greatest common divisor, but not for sums.',
    'sqrt-decomposition': 'Prefix sums answer any range sum in one step, but changing a single value means rewriting every total after it. Square root decomposition sits in the middle. Cut the list into blocks of about the square root of n cells, and store the total of each block. To change one value, update the cell and add the difference to its block total. That is constant time. To find a range sum, walk the loose cells at the left end until you reach a block boundary. Then add whole blocks in one step each while they fit. Finally, walk the loose cells at the right end. There are at most about the square root of n whole blocks, and fewer than two blocks of loose cells. In the animation, the sum from one to seven is twenty eight. After setting position four to ten, only one block total changes, and the same query gives thirty three.',
    'leetcode': 'The LeetCode problems in this chapter each build a structure that makes one kind of question fast. The easy problems answer range sums with a prefix array, and build a hash set from scratch with buckets. The medium problems count how often a value appears in a range, using sorted position lists and binary search, and handle range sums with updates using square root blocks. The hard problems build an LRU cache from a hash map and a list ordered by use, and find the maximum of every sliding window with a deque whose values only go down. The expert problems build a full skip list with search, add and erase, and an LFU cache that groups keys by how often they were used. Each one is solved in four languages, and you can replay every line of every solution.',
}

T = t.finish({
    'slug': 'special-structures', 'title': 'Special Data Structures', 'short': 'Special structures', 'emoji': '🛗', 'topic': 'special-structures', 'prefix': 'dsaspec',
    'module': ('🚀', 'Expert topics'),
    'lead': 'Give up a little memory or a little certainty and answer one question very fast. Search a skip list with express lanes, test words with a Bloom filter, count a stream with a count-min sketch, find range minimums with a sparse table and update sums with square root blocks.',
    'desc': 'Special data structures in DSA: skip lists, Bloom filters, the count-min sketch, sparse tables for range minimum queries and square root decomposition, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 25,
    'summary': 'Skip lists with coin flip lanes, Bloom filters with no false negatives, count-min sketches for streams, sparse tables for O(1) range minimum and square root decomposition for sums with updates. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['skip list', 'skiplist', 'bloom filter', 'false positive', 'count-min sketch', 'probabilistic data structure', 'sparse table', 'range minimum query', 'rmq', 'square root decomposition', 'sqrt decomposition', 'block decomposition', 'lru cache', 'lfu cache', 'monotonic deque'],
    'added': '2026-11-23',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS, 'css': '',
    'prev': ('advanced-strings', 'advanced-strings', '🧵 Advanced strings'),
    'next': ('hard-problems', 'hard-problems', '🎲 Hard problems'),
})
