# Hashing and hash tables: hash functions, buckets, chaining, open addressing, load factor and resizing,
# everyday hash map patterns, good and bad hash functions, and hashing in real systems.
from kit4 import Topic

t = Topic()

POLY_PY = '''def poly_hash(word):
    h = 0
    for ch in word:
        h = (h * 31 + ord(ch)) % 1000003   # mix in each letter, keep the number small
    return h
'''
POLY_JS = '''function polyHash(word) {
  let h = 0;
  for (const ch of word) {
    h = (h * 31 + ch.charCodeAt(0)) % 1000003;  // mix in each letter, keep the number small
  }
  return h;
}
'''
POLY_TS = POLY_JS.replace('polyHash(word)', 'polyHash(word: string): number')
POLY_JAVA = '''    static int polyHash(String word) {
        int h = 0;
        for (char ch : word.toCharArray()) {
            h = (h * 31 + ch) % 1000003;          // mix in each letter, keep the number small
        }
        return h;
    }
'''

# ---------------------------------------------------------------- lesson programs
t.code('hash_fn', py=POLY_PY + r'''

for w in ["cat", "act", "dog", "tac"]:
    h = poly_hash(w)
    print(w, "hash", h, "-> bucket", h % 10)   # squeeze the big number into 10 buckets
''', js=POLY_JS + r'''
for (const w of ["cat", "act", "dog", "tac"]) {
  const h = polyHash(w);
  console.log(w, "hash", h, "-> bucket", h % 10);  // squeeze the big number into 10 buckets
}
''', java=r'''
public class HashFn {
''' + POLY_JAVA + r'''
    public static void main(String[] args) {
        for (String w : new String[]{"cat", "act", "dog", "tac"}) {
            int h = polyHash(w);
            System.out.println(w + " hash " + h + " -> bucket " + (h % 10));  // squeeze into 10 buckets
        }
    }
}
''', ts=POLY_TS + r'''
for (const w of ["cat", "act", "dog", "tac"]) {
  const h: number = polyHash(w);
  console.log(w, "hash", h, "-> bucket", h % 10);  // squeeze the big number into 10 buckets
}
''')

t.code('chaining', py=POLY_PY + r'''

class ChainMap:
    def __init__(self, m):
        self.buckets = [[] for _ in range(m)]   # every bucket is a little list of [key, value]

    def put(self, key, value):
        b = self.buckets[poly_hash(key) % len(self.buckets)]
        for pair in b:
            if pair[0] == key:
                pair[1] = value                  # the key is already there, so update it
                return
        b.append([key, value])                   # a new key joins the chain

    def get(self, key):
        for k, v in self.buckets[poly_hash(key) % len(self.buckets)]:
            if k == key:
                return v
        return "missing"                         # not in its bucket, so not anywhere


m = ChainMap(4)
for k, v in [("apple", 3), ("banana", 5), ("cherry", 7), ("date", 9), ("apple", 4)]:
    m.put(k, v)
for i, b in enumerate(m.buckets):
    print("bucket", i, ":", " ".join(k + "=" + str(v) for k, v in b))
print("banana", m.get("banana"), "fig", m.get("fig"))
''', js=POLY_JS + r'''
class ChainMap {
  constructor(m) {
    this.buckets = Array.from({ length: m }, () => []);  // every bucket is a little list of [key, value]
  }
  put(key, value) {
    const b = this.buckets[polyHash(key) % this.buckets.length];
    for (const pair of b) {
      if (pair[0] === key) { pair[1] = value; return; }  // the key is already there, so update it
    }
    b.push([key, value]);                                 // a new key joins the chain
  }
  get(key) {
    for (const [k, v] of this.buckets[polyHash(key) % this.buckets.length]) {
      if (k === key) return v;
    }
    return "missing";                                     // not in its bucket, so not anywhere
  }
}

const m = new ChainMap(4);
for (const [k, v] of [["apple", 3], ["banana", 5], ["cherry", 7], ["date", 9], ["apple", 4]]) m.put(k, v);
m.buckets.forEach((b, i) => console.log("bucket", i, ":", b.map(([k, v]) => k + "=" + v).join(" ")));
console.log("banana", m.get("banana"), "fig", m.get("fig"));
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class Chaining {
''' + POLY_JAVA + r'''
    static List<List<Object[]>> buckets = new ArrayList<>();   // every bucket is a little list of {key, value}

    static void put(String key, int value) {
        List<Object[]> b = buckets.get(polyHash(key) % buckets.size());
        for (Object[] pair : b) {
            if (pair[0].equals(key)) { pair[1] = value; return; }   // the key is already there, so update it
        }
        b.add(new Object[]{key, value});                            // a new key joins the chain
    }

    static String get(String key) {
        for (Object[] pair : buckets.get(polyHash(key) % buckets.size())) {
            if (pair[0].equals(key)) return String.valueOf(pair[1]);
        }
        return "missing";                                           // not in its bucket, so not anywhere
    }

    public static void main(String[] args) {
        for (int i = 0; i < 4; i++) buckets.add(new ArrayList<>());
        String[] ks = {"apple", "banana", "cherry", "date", "apple"};
        int[] vs = {3, 5, 7, 9, 4};
        for (int i = 0; i < ks.length; i++) put(ks[i], vs[i]);
        for (int i = 0; i < buckets.size(); i++) {
            List<String> items = new ArrayList<>();
            for (Object[] p : buckets.get(i)) items.add(p[0] + "=" + p[1]);
            System.out.println("bucket " + i + " : " + String.join(" ", items));
        }
        System.out.println("banana " + get("banana") + " fig " + get("fig"));
    }
}
''', ts=POLY_TS + r'''
class ChainMap {
  buckets: Array<Array<[string, number]>>;
  constructor(m: number) {
    this.buckets = Array.from({ length: m }, () => []);  // every bucket is a little list of [key, value]
  }
  put(key: string, value: number): void {
    const b = this.buckets[polyHash(key) % this.buckets.length];
    for (const pair of b) {
      if (pair[0] === key) { pair[1] = value; return; }  // the key is already there, so update it
    }
    b.push([key, value]);                                 // a new key joins the chain
  }
  get(key: string): number | string {
    for (const [k, v] of this.buckets[polyHash(key) % this.buckets.length]) {
      if (k === key) return v;
    }
    return "missing";                                     // not in its bucket, so not anywhere
  }
}

const m = new ChainMap(4);
const data: Array<[string, number]> = [["apple", 3], ["banana", 5], ["cherry", 7], ["date", 9], ["apple", 4]];
for (const [k, v] of data) m.put(k, v);
m.buckets.forEach((b, i) => console.log("bucket", i, ":", b.map(([k, v]) => k + "=" + v).join(" ")));
console.log("banana", m.get("banana"), "fig", m.get("fig"));
''')

t.code('probing', py=r'''
M = 7
table = [None] * M


def insert(key):
    i, probes = key % M, 1
    while table[i] is not None:      # taken, so step to the next slot
        i = (i + 1) % M              # wrap around at the end
        probes += 1
    table[i] = key
    return probes


def find(key):
    i, probes = key % M, 1
    while table[i] is not None:
        if table[i] == key:
            return "found after " + str(probes) + " probes"
        i = (i + 1) % M
        probes += 1
    return "missing after " + str(probes) + " probes"   # an empty slot ends the search


for k in [10, 17, 24, 5, 3]:
    print("insert", k, "probes", insert(k))
print(" ".join("_" if x is None else str(x) for x in table))
print("24", find(24))
print("31", find(31))
''', js=r'''
const M = 7;
const table = new Array(M).fill(null);

function insert(key) {
  let i = key % M, probes = 1;
  while (table[i] !== null) {        // taken, so step to the next slot
    i = (i + 1) % M;                 // wrap around at the end
    probes++;
  }
  table[i] = key;
  return probes;
}

function find(key) {
  let i = key % M, probes = 1;
  while (table[i] !== null) {
    if (table[i] === key) return "found after " + probes + " probes";
    i = (i + 1) % M;
    probes++;
  }
  return "missing after " + probes + " probes";  // an empty slot ends the search
}

for (const k of [10, 17, 24, 5, 3]) console.log("insert", k, "probes", insert(k));
console.log(table.map(x => (x === null ? "_" : String(x))).join(" "));
console.log("24", find(24));
console.log("31", find(31));
''', java=r'''
public class Probing {
    static final int M = 7;
    static Integer[] table = new Integer[M];

    static int insert(int key) {
        int i = key % M, probes = 1;
        while (table[i] != null) {           // taken, so step to the next slot
            i = (i + 1) % M;                 // wrap around at the end
            probes++;
        }
        table[i] = key;
        return probes;
    }

    static String find(int key) {
        int i = key % M, probes = 1;
        while (table[i] != null) {
            if (table[i] == key) return "found after " + probes + " probes";
            i = (i + 1) % M;
            probes++;
        }
        return "missing after " + probes + " probes";  // an empty slot ends the search
    }

    public static void main(String[] args) {
        for (int k : new int[]{10, 17, 24, 5, 3}) System.out.println("insert " + k + " probes " + insert(k));
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < M; i++) sb.append(i > 0 ? " " : "").append(table[i] == null ? "_" : String.valueOf(table[i]));
        System.out.println(sb);
        System.out.println("24 " + find(24));
        System.out.println("31 " + find(31));
    }
}
''', ts=r'''
const M = 7;
const table: Array<number | null> = new Array(M).fill(null);

function insert(key: number): number {
  let i = key % M, probes = 1;
  while (table[i] !== null) {        // taken, so step to the next slot
    i = (i + 1) % M;                 // wrap around at the end
    probes++;
  }
  table[i] = key;
  return probes;
}

function find(key: number): string {
  let i = key % M, probes = 1;
  while (table[i] !== null) {
    if (table[i] === key) return "found after " + probes + " probes";
    i = (i + 1) % M;
    probes++;
  }
  return "missing after " + probes + " probes";  // an empty slot ends the search
}

for (const k of [10, 17, 24, 5, 3]) console.log("insert", k, "probes", insert(k));
console.log(table.map(x => (x === null ? "_" : String(x))).join(" "));
console.log("24", find(24));
console.log("31", find(31));
''')

t.code('resize', py=r'''
capacity, size, moved = 4, 0, 0
for key in range(1, 21):
    size += 1
    if size / capacity > 0.75:        # too crowded: chains or probe runs get long
        moved += size                 # every key must be placed again in the bigger table
        print("size", size, "grows", capacity, "->", capacity * 2)
        capacity *= 2
print("final capacity", capacity, "keys moved in total", moved)
''', js=r'''
let capacity = 4, size = 0, moved = 0;
for (let key = 1; key <= 20; key++) {
  size++;
  if (size / capacity > 0.75) {      // too crowded: chains or probe runs get long
    moved += size;                   // every key must be placed again in the bigger table
    console.log("size", size, "grows", capacity, "->", capacity * 2);
    capacity *= 2;
  }
}
console.log("final capacity", capacity, "keys moved in total", moved);
''', java=r'''
public class Resize {
    public static void main(String[] args) {
        int capacity = 4, size = 0, moved = 0;
        for (int key = 1; key <= 20; key++) {
            size++;
            if ((double) size / capacity > 0.75) {   // too crowded: chains or probe runs get long
                moved += size;                       // every key must be placed again in the bigger table
                System.out.println("size " + size + " grows " + capacity + " -> " + capacity * 2);
                capacity *= 2;
            }
        }
        System.out.println("final capacity " + capacity + " keys moved in total " + moved);
    }
}
''', ts=r'''
let capacity: number = 4, size: number = 0, moved: number = 0;
for (let key = 1; key <= 20; key++) {
  size++;
  if (size / capacity > 0.75) {      // too crowded: chains or probe runs get long
    moved += size;                   // every key must be placed again in the bigger table
    console.log("size", size, "grows", capacity, "->", capacity * 2);
    capacity *= 2;
  }
}
console.log("final capacity", capacity, "keys moved in total", moved);
''')

t.code('patterns', py=r'''
words = "the cat and the hat and the bat".split()
count = {}
for w in words:
    count[w] = count.get(w, 0) + 1        # counting pattern: one dictionary, one pass
print(", ".join(w + " " + str(c) for w, c in count.items()))


def two_sum(nums, target):
    seen = {}                             # value -> index of the numbers already passed
    for i, x in enumerate(nums):
        if target - x in seen:            # the partner was seen earlier
            return [seen[target - x], i]
        seen[x] = i
    return []


print(two_sum([2, 7, 11, 15], 9), two_sum([3, 2, 4], 6))
''', js=r'''
const words = "the cat and the hat and the bat".split(" ");
const count = new Map();
for (const w of words) {
  count.set(w, (count.get(w) || 0) + 1);  // counting pattern: one map, one pass
}
console.log([...count].map(([w, c]) => w + " " + c).join(", "));

function twoSum(nums, target) {
  const seen = new Map();                 // value -> index of the numbers already passed
  for (let i = 0; i < nums.length; i++) {
    const x = nums[i];
    if (seen.has(target - x)) return [seen.get(target - x), i];  // the partner was seen earlier
    seen.set(x, i);
  }
  return [];
}

const show = a => "[" + a.join(", ") + "]";
console.log(show(twoSum([2, 7, 11, 15], 9)), show(twoSum([3, 2, 4], 6)));
''', java=r'''
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Patterns {
    static int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> seen = new HashMap<>();   // value -> index of the numbers already passed
        for (int i = 0; i < nums.length; i++) {
            int x = nums[i];
            if (seen.containsKey(target - x)) return new int[]{seen.get(target - x), i};  // the partner was seen earlier
            seen.put(x, i);
        }
        return new int[0];
    }

    public static void main(String[] args) {
        Map<String, Integer> count = new LinkedHashMap<>();
        for (String w : "the cat and the hat and the bat".split(" ")) {
            count.merge(w, 1, Integer::sum);             // counting pattern: one map, one pass
        }
        List<String> parts = new ArrayList<>();
        for (Map.Entry<String, Integer> e : count.entrySet()) parts.add(e.getKey() + " " + e.getValue());
        System.out.println(String.join(", ", parts));
        int[] a = twoSum(new int[]{2, 7, 11, 15}, 9), b = twoSum(new int[]{3, 2, 4}, 6);
        System.out.println("[" + a[0] + ", " + a[1] + "] [" + b[0] + ", " + b[1] + "]");
    }
}
''', ts=r'''
const words: string[] = "the cat and the hat and the bat".split(" ");
const count = new Map<string, number>();
for (const w of words) {
  count.set(w, (count.get(w) ?? 0) + 1);  // counting pattern: one map, one pass
}
console.log([...count].map(([w, c]) => w + " " + c).join(", "));

function twoSum(nums: number[], target: number): number[] {
  const seen = new Map<number, number>();  // value -> index of the numbers already passed
  for (let i = 0; i < nums.length; i++) {
    const x = nums[i];
    if (seen.has(target - x)) return [seen.get(target - x)!, i];  // the partner was seen earlier
    seen.set(x, i);
  }
  return [];
}

const show = (a: number[]): string => "[" + a.join(", ") + "]";
console.log(show(twoSum([2, 7, 11, 15], 9)), show(twoSum([3, 2, 4], 6)));
''')

t.code('spread', py=POLY_PY + r'''

words = ["sun", "sea", "sky", "star", "salt", "sand", "ship", "shop", "fish", "fog"]
bad = [0] * 8
good = [0] * 8
for w in words:
    bad[ord(w[0]) % 8] += 1           # only looks at the first letter
    good[poly_hash(w) % 8] += 1       # every letter changes the result
print("first letter :", " ".join(str(c) for c in bad), "longest chain", max(bad))
print("whole word   :", " ".join(str(c) for c in good), "longest chain", max(good))
''', js=POLY_JS + r'''
const words = ["sun", "sea", "sky", "star", "salt", "sand", "ship", "shop", "fish", "fog"];
const bad = new Array(8).fill(0), good = new Array(8).fill(0);
for (const w of words) {
  bad[w.charCodeAt(0) % 8]++;         // only looks at the first letter
  good[polyHash(w) % 8]++;            // every letter changes the result
}
console.log("first letter :", bad.join(" "), "longest chain", Math.max(...bad));
console.log("whole word   :", good.join(" "), "longest chain", Math.max(...good));
''', java=r'''
public class Spread {
''' + POLY_JAVA + r'''
    static String join(int[] a) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < a.length; i++) sb.append(i > 0 ? " " : "").append(a[i]);
        return sb.toString();
    }

    static int max(int[] a) {
        int m = 0;
        for (int x : a) m = Math.max(m, x);
        return m;
    }

    public static void main(String[] args) {
        String[] words = {"sun", "sea", "sky", "star", "salt", "sand", "ship", "shop", "fish", "fog"};
        int[] bad = new int[8], good = new int[8];
        for (String w : words) {
            bad[w.charAt(0) % 8]++;           // only looks at the first letter
            good[polyHash(w) % 8]++;          // every letter changes the result
        }
        System.out.println("first letter : " + join(bad) + " longest chain " + max(bad));
        System.out.println("whole word   : " + join(good) + " longest chain " + max(good));
    }
}
''', ts=POLY_TS + r'''
const words: string[] = ["sun", "sea", "sky", "star", "salt", "sand", "ship", "shop", "fish", "fog"];
const bad: number[] = new Array(8).fill(0), good: number[] = new Array(8).fill(0);
for (const w of words) {
  bad[w.charCodeAt(0) % 8]++;         // only looks at the first letter
  good[polyHash(w) % 8]++;            // every letter changes the result
}
console.log("first letter :", bad.join(" "), "longest chain", Math.max(...bad));
console.log("whole word   :", good.join(" "), "longest chain", Math.max(...good));
''')

t.code('memo', py=r'''
calls = 0
cache = {}


def fib(n):
    global calls
    calls += 1
    if n in cache:                    # answered before: one dictionary lookup
        return cache[n]
    result = n if n < 2 else fib(n - 1) + fib(n - 2)
    cache[n] = result                 # remember it for next time
    return result


print("fib(40) =", fib(40), "with", calls, "calls")
calls = 0
print("fib(40) again =", fib(40), "with", calls, "call")
''', js=r'''
let calls = 0;
const cache = new Map();

function fib(n) {
  calls++;
  if (cache.has(n)) return cache.get(n);  // answered before: one map lookup
  const result = n < 2 ? n : fib(n - 1) + fib(n - 2);
  cache.set(n, result);                   // remember it for next time
  return result;
}

console.log("fib(40) =", fib(40), "with", calls, "calls");
calls = 0;
console.log("fib(40) again =", fib(40), "with", calls, "call");
''', java=r'''
import java.util.HashMap;
import java.util.Map;

public class Memo {
    static int calls = 0;
    static Map<Integer, Long> cache = new HashMap<>();

    static long fib(int n) {
        calls++;
        if (cache.containsKey(n)) return cache.get(n);   // answered before: one map lookup
        long result = n < 2 ? n : fib(n - 1) + fib(n - 2);
        cache.put(n, result);                            // remember it for next time
        return result;
    }

    public static void main(String[] args) {
        System.out.println("fib(40) = " + fib(40) + " with " + calls + " calls");
        calls = 0;
        System.out.println("fib(40) again = " + fib(40) + " with " + calls + " call");
    }
}
''', ts=r'''
let calls: number = 0;
const cache = new Map<number, number>();

function fib(n: number): number {
  calls++;
  if (cache.has(n)) return cache.get(n)!;  // answered before: one map lookup
  const result = n < 2 ? n : fib(n - 1) + fib(n - 2);
  cache.set(n, result);                    // remember it for next time
  return result;
}

console.log("fib(40) =", fib(40), "with", calls, "calls");
calls = 0;
console.log("fib(40) again =", fib(40), "with", calls, "call");
''')

# ---------------------------------------------------------------- LeetCode practice programs
YN_PY = 'lambda b: "yes" if b else "no"'
t.code('p_dup', py=r'''
def contains_duplicate(nums):
    seen = set()
    for x in nums:
        if x in seen:                 # met this value before
            return True
        seen.add(x)
    return False


yn = lambda b: "yes" if b else "no"
print(yn(contains_duplicate([1, 2, 3, 1])), yn(contains_duplicate([1, 2, 3, 4])), yn(contains_duplicate([1, 1, 1, 3, 3, 4, 3, 2, 4, 2])))
''', js=r'''
function containsDuplicate(nums) {
  const seen = new Set();
  for (const x of nums) {
    if (seen.has(x)) return true;     // met this value before
    seen.add(x);
  }
  return false;
}

const yn = b => (b ? "yes" : "no");
console.log(yn(containsDuplicate([1, 2, 3, 1])), yn(containsDuplicate([1, 2, 3, 4])), yn(containsDuplicate([1, 1, 1, 3, 3, 4, 3, 2, 4, 2])));
''', java=r'''
import java.util.HashSet;
import java.util.Set;

public class ContainsDuplicate {
    static boolean containsDuplicate(int[] nums) {
        Set<Integer> seen = new HashSet<>();
        for (int x : nums) {
            if (!seen.add(x)) return true;   // add returns false when the value was already there
        }
        return false;
    }

    static String yn(boolean b) { return b ? "yes" : "no"; }

    public static void main(String[] args) {
        System.out.println(yn(containsDuplicate(new int[]{1, 2, 3, 1})) + " " + yn(containsDuplicate(new int[]{1, 2, 3, 4})) + " "
                + yn(containsDuplicate(new int[]{1, 1, 1, 3, 3, 4, 3, 2, 4, 2})));
    }
}
''', ts=r'''
function containsDuplicate(nums: number[]): boolean {
  const seen = new Set<number>();
  for (const x of nums) {
    if (seen.has(x)) return true;     // met this value before
    seen.add(x);
  }
  return false;
}

const yn = (b: boolean): string => (b ? "yes" : "no");
console.log(yn(containsDuplicate([1, 2, 3, 1])), yn(containsDuplicate([1, 2, 3, 4])), yn(containsDuplicate([1, 1, 1, 3, 3, 4, 3, 2, 4, 2])));
''')

t.code('p_iso', py=r'''
def is_isomorphic(s, t):
    to_t, to_s = {}, {}               # one dictionary per direction
    for a, b in zip(s, t):
        if to_t.get(a, b) != b or to_s.get(b, a) != a:
            return False              # a letter would need two different partners
        to_t[a] = b
        to_s[b] = a
    return True


pairs = [("egg", "add"), ("foo", "bar"), ("paper", "title"), ("badc", "baba")]
print(" ".join("yes" if is_isomorphic(s, t) else "no" for s, t in pairs))
''', js=r'''
function isIsomorphic(s, t) {
  const toT = new Map(), toS = new Map();  // one map per direction
  for (let i = 0; i < s.length; i++) {
    const a = s[i], b = t[i];
    if ((toT.has(a) && toT.get(a) !== b) || (toS.has(b) && toS.get(b) !== a)) return false;  // two partners
    toT.set(a, b);
    toS.set(b, a);
  }
  return true;
}

const pairs = [["egg", "add"], ["foo", "bar"], ["paper", "title"], ["badc", "baba"]];
console.log(pairs.map(([s, t]) => (isIsomorphic(s, t) ? "yes" : "no")).join(" "));
''', java=r'''
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Isomorphic {
    static boolean isIsomorphic(String s, String t) {
        Map<Character, Character> toT = new HashMap<>(), toS = new HashMap<>();  // one map per direction
        for (int i = 0; i < s.length(); i++) {
            char a = s.charAt(i), b = t.charAt(i);
            if (toT.getOrDefault(a, b).charValue() != b || toS.getOrDefault(b, a).charValue() != a) return false;  // two partners
            toT.put(a, b);
            toS.put(b, a);
        }
        return true;
    }

    public static void main(String[] args) {
        String[][] pairs = {{"egg", "add"}, {"foo", "bar"}, {"paper", "title"}, {"badc", "baba"}};
        List<String> out = new ArrayList<>();
        for (String[] p : pairs) out.add(isIsomorphic(p[0], p[1]) ? "yes" : "no");
        System.out.println(String.join(" ", out));
    }
}
''', ts=r'''
function isIsomorphic(s: string, t: string): boolean {
  const toT = new Map<string, string>(), toS = new Map<string, string>();  // one map per direction
  for (let i = 0; i < s.length; i++) {
    const a = s[i], b = t[i];
    if ((toT.has(a) && toT.get(a) !== b) || (toS.has(b) && toS.get(b) !== a)) return false;  // two partners
    toT.set(a, b);
    toS.set(b, a);
  }
  return true;
}

const pairs: Array<[string, string]> = [["egg", "add"], ["foo", "bar"], ["paper", "title"], ["badc", "baba"]];
console.log(pairs.map(([s, t]) => (isIsomorphic(s, t) ? "yes" : "no")).join(" "));
''')

t.code('p_near', py=r'''
def contains_nearby_duplicate(nums, k):
    last = {}                          # value -> the last index where it appeared
    for i, x in enumerate(nums):
        if x in last and i - last[x] <= k:
            return True                # the same value again, close enough
        last[x] = i
    return False


yn = lambda b: "yes" if b else "no"
print(yn(contains_nearby_duplicate([1, 2, 3, 1], 3)), yn(contains_nearby_duplicate([1, 0, 1, 1], 1)), yn(contains_nearby_duplicate([1, 2, 3, 1, 2, 3], 2)))
''', js=r'''
function containsNearbyDuplicate(nums, k) {
  const last = new Map();              // value -> the last index where it appeared
  for (let i = 0; i < nums.length; i++) {
    const x = nums[i];
    if (last.has(x) && i - last.get(x) <= k) return true;  // the same value again, close enough
    last.set(x, i);
  }
  return false;
}

const yn = b => (b ? "yes" : "no");
console.log(yn(containsNearbyDuplicate([1, 2, 3, 1], 3)), yn(containsNearbyDuplicate([1, 0, 1, 1], 1)), yn(containsNearbyDuplicate([1, 2, 3, 1, 2, 3], 2)));
''', java=r'''
import java.util.HashMap;
import java.util.Map;

public class NearbyDuplicate {
    static boolean containsNearbyDuplicate(int[] nums, int k) {
        Map<Integer, Integer> last = new HashMap<>();   // value -> the last index where it appeared
        for (int i = 0; i < nums.length; i++) {
            Integer j = last.get(nums[i]);
            if (j != null && i - j <= k) return true;   // the same value again, close enough
            last.put(nums[i], i);
        }
        return false;
    }

    static String yn(boolean b) { return b ? "yes" : "no"; }

    public static void main(String[] args) {
        System.out.println(yn(containsNearbyDuplicate(new int[]{1, 2, 3, 1}, 3)) + " " + yn(containsNearbyDuplicate(new int[]{1, 0, 1, 1}, 1)) + " "
                + yn(containsNearbyDuplicate(new int[]{1, 2, 3, 1, 2, 3}, 2)));
    }
}
''', ts=r'''
function containsNearbyDuplicate(nums: number[], k: number): boolean {
  const last = new Map<number, number>();  // value -> the last index where it appeared
  for (let i = 0; i < nums.length; i++) {
    const x = nums[i];
    const j = last.get(x);
    if (j !== undefined && i - j <= k) return true;  // the same value again, close enough
    last.set(x, i);
  }
  return false;
}

const yn = (b: boolean): string => (b ? "yes" : "no");
console.log(yn(containsNearbyDuplicate([1, 2, 3, 1], 3)), yn(containsNearbyDuplicate([1, 0, 1, 1], 1)), yn(containsNearbyDuplicate([1, 2, 3, 1, 2, 3], 2)));
''')

SUDOKU_ROWS = '''"53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1", "7...2...6", ".6....28.", "...419..5", "....8..79"'''
t.code('p_sudoku', py=r'''
def is_valid_sudoku(board):
    seen = set()
    for r in range(9):
        for c in range(9):
            d = board[r][c]
            if d == ".":
                continue
            keys = ("row", r, d), ("col", c, d), ("box", r // 3, c // 3, d)   # three promises per digit
            if any(k in seen for k in keys):
                return False
            seen.update(keys)
    return True


good = [''' + SUDOKU_ROWS + r''']
bad = ["8" + good[0][1:]] + good[1:]          # an 8 at the top left clashes with the 8 below it
print("yes" if is_valid_sudoku(good) else "no", "yes" if is_valid_sudoku(bad) else "no")
''', js=r'''
function isValidSudoku(board) {
  const seen = new Set();
  for (let r = 0; r < 9; r++) {
    for (let c = 0; c < 9; c++) {
      const d = board[r][c];
      if (d === ".") continue;
      const keys = [`row${r}:${d}`, `col${c}:${d}`, `box${Math.floor(r / 3)}${Math.floor(c / 3)}:${d}`];  // three promises
      if (keys.some(k => seen.has(k))) return false;
      keys.forEach(k => seen.add(k));
    }
  }
  return true;
}

const good = [''' + SUDOKU_ROWS + r'''];
const bad = ["8" + good[0].slice(1), ...good.slice(1)];  // an 8 at the top left clashes with the 8 below it
console.log(isValidSudoku(good) ? "yes" : "no", isValidSudoku(bad) ? "yes" : "no");
''', java=r'''
import java.util.HashSet;
import java.util.Set;

public class ValidSudoku {
    static boolean isValidSudoku(String[] board) {
        Set<String> seen = new HashSet<>();
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                char d = board[r].charAt(c);
                if (d == '.') continue;
                // add returns false when the promise was already made by another cell
                if (!seen.add("row" + r + ":" + d) || !seen.add("col" + c + ":" + d) || !seen.add("box" + r / 3 + c / 3 + ":" + d)) return false;
            }
        }
        return true;
    }

    public static void main(String[] args) {
        String[] good = {''' + SUDOKU_ROWS + r'''};
        String[] bad = good.clone();
        bad[0] = "8" + good[0].substring(1);             // an 8 at the top left clashes with the 8 below it
        System.out.println((isValidSudoku(good) ? "yes" : "no") + " " + (isValidSudoku(bad) ? "yes" : "no"));
    }
}
''', ts=r'''
function isValidSudoku(board: string[]): boolean {
  const seen = new Set<string>();
  for (let r = 0; r < 9; r++) {
    for (let c = 0; c < 9; c++) {
      const d = board[r][c];
      if (d === ".") continue;
      const keys = [`row${r}:${d}`, `col${c}:${d}`, `box${Math.floor(r / 3)}${Math.floor(c / 3)}:${d}`];  // three promises
      if (keys.some(k => seen.has(k))) return false;
      keys.forEach(k => seen.add(k));
    }
  }
  return true;
}

const good: string[] = [''' + SUDOKU_ROWS + r'''];
const bad: string[] = ["8" + good[0].slice(1), ...good.slice(1)];  // an 8 at the top left clashes with the 8 below it
console.log(isValidSudoku(good) ? "yes" : "no", isValidSudoku(bad) ? "yes" : "no");
''')

t.code('p_design', py=r'''
class MyHashMap:
    def __init__(self):
        self.size = 1009                       # a prime number of buckets spreads keys well
        self.buckets = [[] for _ in range(self.size)]

    def put(self, key, value):
        b = self.buckets[key % self.size]
        for pair in b:
            if pair[0] == key:
                pair[1] = value
                return
        b.append([key, value])

    def get(self, key):
        for k, v in self.buckets[key % self.size]:
            if k == key:
                return v
        return -1

    def remove(self, key):
        b = self.buckets[key % self.size]
        self.buckets[key % self.size] = [p for p in b if p[0] != key]


m = MyHashMap()
m.put(1, 1)
m.put(2, 2)
out = [m.get(1), m.get(3)]
m.put(2, 1)
out.append(m.get(2))
m.remove(2)
out.append(m.get(2))
m.put(1010, 7)                                 # 1010 lands in the same bucket as 1
out.append(m.get(1010))
out.append(m.get(1))
print(*out)
''', js=r'''
class MyHashMap {
  constructor() {
    this.size = 1009;                          // a prime number of buckets spreads keys well
    this.buckets = Array.from({ length: this.size }, () => []);
  }
  put(key, value) {
    const b = this.buckets[key % this.size];
    for (const pair of b) if (pair[0] === key) { pair[1] = value; return; }
    b.push([key, value]);
  }
  get(key) {
    for (const [k, v] of this.buckets[key % this.size]) if (k === key) return v;
    return -1;
  }
  remove(key) {
    const i = key % this.size;
    this.buckets[i] = this.buckets[i].filter(p => p[0] !== key);
  }
}

const m = new MyHashMap();
m.put(1, 1);
m.put(2, 2);
const out = [m.get(1), m.get(3)];
m.put(2, 1);
out.push(m.get(2));
m.remove(2);
out.push(m.get(2));
m.put(1010, 7);                                // 1010 lands in the same bucket as 1
out.push(m.get(1010));
out.push(m.get(1));
console.log(out.join(" "));
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class MyHashMap {
    final int size = 1009;                             // a prime number of buckets spreads keys well
    List<List<int[]>> buckets = new ArrayList<>();

    MyHashMap() { for (int i = 0; i < size; i++) buckets.add(new ArrayList<>()); }

    void put(int key, int value) {
        for (int[] p : buckets.get(key % size)) if (p[0] == key) { p[1] = value; return; }
        buckets.get(key % size).add(new int[]{key, value});
    }

    int get(int key) {
        for (int[] p : buckets.get(key % size)) if (p[0] == key) return p[1];
        return -1;
    }

    void remove(int key) {
        buckets.get(key % size).removeIf(p -> p[0] == key);
    }

    public static void main(String[] args) {
        MyHashMap m = new MyHashMap();
        m.put(1, 1);
        m.put(2, 2);
        StringBuilder out = new StringBuilder();
        out.append(m.get(1)).append(" ").append(m.get(3));
        m.put(2, 1);
        out.append(" ").append(m.get(2));
        m.remove(2);
        out.append(" ").append(m.get(2));
        m.put(1010, 7);                                // 1010 lands in the same bucket as 1
        out.append(" ").append(m.get(1010)).append(" ").append(m.get(1));
        System.out.println(out);
    }
}
''', ts=r'''
class MyHashMap {
  size: number = 1009;                         // a prime number of buckets spreads keys well
  buckets: Array<Array<[number, number]>> = Array.from({ length: 1009 }, () => []);
  put(key: number, value: number): void {
    const b = this.buckets[key % this.size];
    for (const pair of b) if (pair[0] === key) { pair[1] = value; return; }
    b.push([key, value]);
  }
  get(key: number): number {
    for (const [k, v] of this.buckets[key % this.size]) if (k === key) return v;
    return -1;
  }
  remove(key: number): void {
    const i = key % this.size;
    this.buckets[i] = this.buckets[i].filter(p => p[0] !== key);
  }
}

const m = new MyHashMap();
m.put(1, 1);
m.put(2, 2);
const out: number[] = [m.get(1), m.get(3)];
m.put(2, 1);
out.push(m.get(2));
m.remove(2);
out.push(m.get(2));
m.put(1010, 7);                                // 1010 lands in the same bucket as 1
out.push(m.get(1010));
out.push(m.get(1));
console.log(out.join(" "));
''')

t.code('p_4sum', py=r'''
def four_sum_count(a, b, c, d):
    sums = {}
    for x in a:
        for y in b:
            sums[x + y] = sums.get(x + y, 0) + 1   # every sum of the first two lists, with how often
    count = 0
    for x in c:
        for y in d:
            count += sums.get(-(x + y), 0)         # the partner sum that makes zero
    return count


print(four_sum_count([1, 2], [-2, -1], [-1, 2], [0, 2]), four_sum_count([0], [0], [0], [0]))
''', js=r'''
function fourSumCount(a, b, c, d) {
  const sums = new Map();
  for (const x of a) for (const y of b) sums.set(x + y, (sums.get(x + y) || 0) + 1);  // every first half sum
  let count = 0;
  for (const x of c) for (const y of d) count += sums.get(-(x + y)) || 0;            // the partner sum
  return count;
}

console.log(fourSumCount([1, 2], [-2, -1], [-1, 2], [0, 2]), fourSumCount([0], [0], [0], [0]));
''', java=r'''
import java.util.HashMap;
import java.util.Map;

public class FourSumII {
    static int fourSumCount(int[] a, int[] b, int[] c, int[] d) {
        Map<Integer, Integer> sums = new HashMap<>();
        for (int x : a) for (int y : b) sums.merge(x + y, 1, Integer::sum);   // every first half sum
        int count = 0;
        for (int x : c) for (int y : d) count += sums.getOrDefault(-(x + y), 0);  // the partner sum
        return count;
    }

    public static void main(String[] args) {
        System.out.println(fourSumCount(new int[]{1, 2}, new int[]{-2, -1}, new int[]{-1, 2}, new int[]{0, 2}) + " "
                + fourSumCount(new int[]{0}, new int[]{0}, new int[]{0}, new int[]{0}));
    }
}
''', ts=r'''
function fourSumCount(a: number[], b: number[], c: number[], d: number[]): number {
  const sums = new Map<number, number>();
  for (const x of a) for (const y of b) sums.set(x + y, (sums.get(x + y) ?? 0) + 1);  // every first half sum
  let count = 0;
  for (const x of c) for (const y of d) count += sums.get(-(x + y)) ?? 0;            // the partner sum
  return count;
}

console.log(fourSumCount([1, 2], [-2, -1], [-1, 2], [0, 2]), fourSumCount([0], [0], [0], [0]));
''')

t.code('p_consec', py=r'''
def longest_consecutive(nums):
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:            # x starts a run only if x - 1 is missing
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return best


print(longest_consecutive([100, 4, 200, 1, 3, 2]), longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]))
''', js=r'''
function longestConsecutive(nums) {
  const s = new Set(nums);
  let best = 0;
  for (const x of s) {
    if (!s.has(x - 1)) {              // x starts a run only if x - 1 is missing
      let y = x;
      while (s.has(y + 1)) y++;
      best = Math.max(best, y - x + 1);
    }
  }
  return best;
}

console.log(longestConsecutive([100, 4, 200, 1, 3, 2]), longestConsecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]));
''', java=r'''
import java.util.HashSet;
import java.util.Set;

public class LongestConsecutive {
    static int longestConsecutive(int[] nums) {
        Set<Integer> s = new HashSet<>();
        for (int x : nums) s.add(x);
        int best = 0;
        for (int x : s) {
            if (!s.contains(x - 1)) {         // x starts a run only if x - 1 is missing
                int y = x;
                while (s.contains(y + 1)) y++;
                best = Math.max(best, y - x + 1);
            }
        }
        return best;
    }

    public static void main(String[] args) {
        System.out.println(longestConsecutive(new int[]{100, 4, 200, 1, 3, 2}) + " " + longestConsecutive(new int[]{0, 3, 7, 2, 5, 8, 4, 6, 0, 1}));
    }
}
''', ts=r'''
function longestConsecutive(nums: number[]): number {
  const s = new Set<number>(nums);
  let best = 0;
  for (const x of s) {
    if (!s.has(x - 1)) {              // x starts a run only if x - 1 is missing
      let y = x;
      while (s.has(y + 1)) y++;
      best = Math.max(best, y - x + 1);
    }
  }
  return best;
}

console.log(longestConsecutive([100, 4, 200, 1, 3, 2]), longestConsecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]));
''')

t.code('p_randset', py=r'''
import random


class RandomizedSet:
    def __init__(self):
        self.pos = {}                  # value -> its index in the list
        self.items = []

    def insert(self, x):
        if x in self.pos:
            return False
        self.pos[x] = len(self.items)
        self.items.append(x)
        return True

    def remove(self, x):
        if x not in self.pos:
            return False
        i, last = self.pos[x], self.items[-1]
        self.items[i] = last           # move the last item into the hole
        self.pos[last] = i
        self.items.pop()               # removing from the end is O(1)
        del self.pos[x]
        return True

    def get_random(self):
        return random.choice(self.items)


s = RandomizedSet()
tf = lambda b: "true" if b else "false"
print(tf(s.insert(1)), tf(s.remove(2)), tf(s.insert(2)), tf(s.remove(1)), tf(s.insert(2)))
print("random is a member:", "yes" if s.get_random() in s.pos else "no")
''', js=r'''
class RandomizedSet {
  constructor() {
    this.pos = new Map();              // value -> its index in the list
    this.items = [];
  }
  insert(x) {
    if (this.pos.has(x)) return false;
    this.pos.set(x, this.items.length);
    this.items.push(x);
    return true;
  }
  remove(x) {
    if (!this.pos.has(x)) return false;
    const i = this.pos.get(x), last = this.items[this.items.length - 1];
    this.items[i] = last;              // move the last item into the hole
    this.pos.set(last, i);
    this.items.pop();                  // removing from the end is O(1)
    this.pos.delete(x);
    return true;
  }
  getRandom() {
    return this.items[Math.floor(Math.random() * this.items.length)];
  }
}

const s = new RandomizedSet();
console.log(s.insert(1), s.remove(2), s.insert(2), s.remove(1), s.insert(2));
console.log("random is a member:", s.pos.has(s.getRandom()) ? "yes" : "no");
''', java=r'''
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

public class RandomizedSet {
    Map<Integer, Integer> pos = new HashMap<>();     // value -> its index in the list
    List<Integer> items = new ArrayList<>();
    Random rnd = new Random();

    boolean insert(int x) {
        if (pos.containsKey(x)) return false;
        pos.put(x, items.size());
        items.add(x);
        return true;
    }

    boolean remove(int x) {
        if (!pos.containsKey(x)) return false;
        int i = pos.get(x), last = items.get(items.size() - 1);
        items.set(i, last);                          // move the last item into the hole
        pos.put(last, i);
        items.remove(items.size() - 1);              // removing from the end is O(1)
        pos.remove(x);
        return true;
    }

    int getRandom() { return items.get(rnd.nextInt(items.size())); }

    public static void main(String[] args) {
        RandomizedSet s = new RandomizedSet();
        System.out.println(s.insert(1) + " " + s.remove(2) + " " + s.insert(2) + " " + s.remove(1) + " " + s.insert(2));
        System.out.println("random is a member: " + (s.pos.containsKey(s.getRandom()) ? "yes" : "no"));
    }
}
''', ts=r'''
class RandomizedSet {
  pos = new Map<number, number>();     // value -> its index in the list
  items: number[] = [];
  insert(x: number): boolean {
    if (this.pos.has(x)) return false;
    this.pos.set(x, this.items.length);
    this.items.push(x);
    return true;
  }
  remove(x: number): boolean {
    const i = this.pos.get(x);
    if (i === undefined) return false;
    const last = this.items[this.items.length - 1];
    this.items[i] = last;              // move the last item into the hole
    this.pos.set(last, i);
    this.items.pop();                  // removing from the end is O(1)
    this.pos.delete(x);
    return true;
  }
  getRandom(): number {
    return this.items[Math.floor(Math.random() * this.items.length)];
  }
}

const s = new RandomizedSet();
console.log(s.insert(1), s.remove(2), s.insert(2), s.remove(1), s.insert(2));
console.log("random is a member:", s.pos.has(s.getRandom()) ? "yes" : "no");
''')

t.leet(217, 'e', 'p_dup',
       statement='<p>Return yes if any value appears at least twice in the list, and no if every value is distinct.</p>',
       example='[1, 2, 3, 1]                  →  yes\n[1, 2, 3, 4]                  →  no\n[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]  →  yes',
       hint='Remember every value you have met in a set.',
       approach='<p>Walk the list once with a hash set. If a value is already in the set, it is a repeat. Sorting first also works but costs O(n log n). In Java, <code>Set.add</code> returns false for a repeat, which saves a separate lookup.</p>',
       time='O(n) on average', space='O(n)')
t.leet(205, 'e', 'p_iso',
       statement='<p>Two strings are isomorphic when the letters of one can be replaced to get the other, with every letter always mapping to the same letter and no two letters mapping to the same one.</p>',
       example='egg, add      →  yes\nfoo, bar      →  no\npaper, title  →  yes\nbadc, baba    →  no',
       hint='One dictionary is not enough. Think of badc and baba.',
       approach='<p>Keep two maps, one from s to t and one from t to s. A clash in either direction means the answer is no. The second map catches two different letters trying to share one partner.</p>',
       time='O(n)', space='O(alphabet size)')
t.leet(219, 'm', 'p_near',
       statement='<p>Return yes if two equal values sit at most k positions apart in the list.</p>',
       example='[1, 2, 3, 1], k = 3        →  yes\n[1, 0, 1, 1], k = 1        →  yes\n[1, 2, 3, 1, 2, 3], k = 2  →  no',
       hint='For each value you only need the most recent index.',
       approach='<p>Store each value with the last index where it appeared. When it appears again, compare the distance with k, then update the index. A sliding set of the last k values also works.</p>',
       time='O(n)', space='O(n)')
t.leet(36, 'm', 'p_sudoku',
       statement='<p>Check whether a partly filled 9 by 9 Sudoku board breaks any rule: no digit may repeat in a row, a column or a 3 by 3 box. Empty cells are dots. The board does not have to be solvable.</p>',
       example='The LeetCode example board  →  yes\nThe same board with an 8 in the top left corner  →  no',
       hint='Each digit makes three promises: one for its row, one for its column and one for its box.',
       approach='<p>One hash set of strings like <code>row4:8</code>, <code>col0:8</code> and <code>box1,0:8</code>. If any promise is already in the set, the board is invalid. The box index is <code>(r // 3, c // 3)</code>.</p>',
       time='O(81), so O(1)', space='O(81)')
t.leet(706, 'h', 'p_design',
       statement='<p>Build your own hash map for integer keys without using a built in map: <code>put</code>, <code>get</code> (return −1 if missing) and <code>remove</code>.</p>',
       example='put(1,1) put(2,2) get(1) → 1  get(3) → -1\nput(2,1) get(2) → 1  remove(2) get(2) → -1',
       hint='An array of buckets, and each bucket a small list of key and value pairs.',
       approach='<p>Separate chaining with 1009 buckets, a prime so keys spread evenly. The bucket is <code>key % 1009</code>. Each operation scans only one short chain. Keys 1 and 1010 collide on purpose in the test to show the chain at work.</p>',
       time='O(1) on average', space='O(n + buckets)')
t.leet(454, 'h', 'p_4sum',
       statement='<p>Given four lists of the same length, count the ways to pick one number from each list so that the four numbers add up to zero.</p>',
       example='[1,2] [-2,-1] [-1,2] [0,2]  →  2\n[0] [0] [0] [0]            →  1',
       hint='Trying every four way choice is n^4. Split the four lists into two pairs.',
       approach='<p>Meet in the middle. Store every sum of the first two lists in a map with how often it appears. Then for every sum of the last two lists, look up its negative. That turns n<sup>4</sup> into n<sup>2</sup>.</p>',
       time='O(n²)', space='O(n²)')
t.leet(128, 'x', 'p_consec',
       statement='<p>Return the length of the longest run of consecutive whole numbers that can be made from the list, in O(n) time. The numbers do not have to be next to each other in the list.</p>',
       example='[100, 4, 200, 1, 3, 2]            →  4   (1, 2, 3, 4)\n[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]    →  9',
       hint='Only start counting from a number whose left neighbour is missing.',
       approach='<p>Put everything in a set. A number x starts a run only when x − 1 is missing. From each start, walk up while the next number exists. Every number is visited by at most one walk, so the total work is O(n) even though there is a loop inside a loop.</p>',
       time='O(n)', space='O(n)')
t.leet(380, 'x', 'p_randset',
       statement='<p>Design a set with <code>insert</code>, <code>remove</code> and <code>getRandom</code>, all in O(1) on average. getRandom must return every current member with equal chance.</p>',
       example='insert(1) true, remove(2) false, insert(2) true,\nremove(1) true, insert(2) false',
       hint='A hash set cannot pick a random member fast, and a list cannot find a value fast. Use both.',
       approach='<p>Keep the values in a list for random picks, and a map from value to list index for fast lookups. To remove, copy the last item into the hole, fix its index in the map, and pop the end of the list. The printed booleans differ only in spelling between languages, so Python prints true and false in lower case here to match.</p>',
       time='O(1) on average', space='O(n)')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='what-is-hashing', emoji='🗄️', title='Hashing: a locker number for every key', html='''
<p>Imagine a school with 100 lockers and a rule that turns any student's name into a locker number. To find Riya's books you do not search all 100 lockers. You run the rule on "Riya" and walk straight to her locker. That rule is a <b>hash function</b>, the locker number is the <b>hash</b>, and the row of lockers is a <b>hash table</b>.</p>
<div class="tw"><table class="jt"><tr><th>Word</th><th>What it means</th></tr>
<tr><td>Key</td><td>what you look things up by, like a name or a phone number</td></tr>
<tr><td>Hash function</td><td>turns a key into a big whole number, always the same number for the same key</td></tr>
<tr><td>Bucket</td><td>one slot of the table, chosen with <code>hash % m</code> for a table of m slots</td></tr>
<tr><td>Collision</td><td>two different keys that land in the same bucket</td></tr></table></div>
<p>A simple and common string hash mixes the letters one by one: <code>h = h × 31 + code of the letter</code>. Java's <code>String.hashCode</code> uses exactly this formula with 32 bit overflow.</p>
<div class="viz" data-viz="pk" data-pk="hashfn"></div>
<div class="c3" data-k="hash_fn" data-label="A polynomial string hash"></div>
<div class="rule">Same key, same hash, every time. Different keys should usually get different hashes, but they are allowed to collide, and with more keys than buckets they must.</div>
'''),
    dict(id='chaining', emoji='⛓️', title='Collisions and separate chaining', html='''
<p>"cat", "act" and "tac" all landed in bucket 2 above. That is a <b>collision</b>. The pigeonhole principle says it cannot be avoided: put 11 letters into 10 boxes and some box gets two. So a hash table needs a plan for sharing.</p>
<p><b>Separate chaining</b> lets every bucket hold a small list. To insert, add the pair to the list of its bucket, or update it if the key is already there. To search, hash the key and scan only that one short list. If the key is not in its own bucket, it is nowhere in the table.</p>
<div class="viz" data-viz="pk" data-pk="chain"></div>
<div class="c3" data-k="chaining" data-label="A tiny hash map with chaining"></div>
<div class="grid2">
<div class="box"><h4>⚡ Average case</h4><p>With n keys spread over m buckets, a chain holds about n / m keys. Keep that ratio small and every operation is <b>O(1) on average</b>.</p></div>
<div class="box"><h4>🐢 Worst case</h4><p>If every key lands in the same bucket, the table becomes one long list and each operation costs <b>O(n)</b>. Java 8 turns a chain of more than 8 entries into a small red black tree to cap the damage at O(log n).</p></div>
</div>
'''),
    dict(id='open-addressing', emoji='🚪', title='Open addressing: find the next free seat', html='''
<p>Another plan keeps one key per slot. If your slot is taken, you <b>probe</b> other slots in a fixed order until you find an empty one, like walking along a row of cinema seats until one is free.</p>
<div class="tw"><table class="jt"><tr><th>Probing</th><th>Slots tried for hash h</th><th>Good and bad</th></tr>
<tr><td>Linear</td><td>h, h + 1, h + 2, ...</td><td>friendly to the CPU cache, but keys bunch into long runs (primary clustering)</td></tr>
<tr><td>Quadratic</td><td>h, h + 1, h + 4, h + 9, ...</td><td>breaks up the runs, may not reach every slot unless the size is chosen carefully</td></tr>
<tr><td>Double hashing</td><td>h, h + g, h + 2g, ... with a second hash g</td><td>the best spread, a little more work per probe</td></tr></table></div>
<div class="viz" data-viz="pk" data-pk="probe"></div>
<div class="c3" data-k="probing" data-label="Linear probing: insert and find"></div>
<div class="warn">Deleting is tricky. Emptying a slot would cut a probe chain and hide keys behind it. Real tables leave a <b>tombstone</b> marker that searches step over and inserts may reuse.</div>
<p>Python's <code>dict</code> uses open addressing with a perturbed probe sequence. Java's <code>HashMap</code> uses chaining.</p>
'''),
    dict(id='load-factor', emoji='🎈', title='Load factor and growing the table', html='''
<p>The <b>load factor</b> is <span class="eq">α = n ÷ m</span>, the number of keys divided by the number of slots. As α rises, chains get longer and probe runs get longer. With linear probing the expected probes for a failed search grow like <span class="eq">½ (1 + 1 ÷ (1 − α)²)</span>, which explodes as α gets close to 1.</p>
<p>So tables <b>resize</b>: when α passes a limit, they allocate about twice as many slots and insert every key again, because <code>hash % m</code> changes when m changes. Java's <code>HashMap</code> grows at 0.75, Python's <code>dict</code> at about two thirds.</p>
<div class="viz" data-viz="pk" data-pk="rehash"></div>
<div class="c3" data-k="resize" data-label="How often does a table grow"></div>
<div class="rule">One resize costs O(n), but doubling makes resizes rare. Spread over all inserts, each insert is still O(1) amortized, the same argument as for dynamic arrays.</div>
'''),
    dict(id='patterns', emoji='🧰', title='Hash maps and sets in everyday code', html='''
<p>You rarely build a hash table yourself. Every language ships one, and a handful of patterns solve a huge share of interview and work problems.</p>
<div class="tw"><table class="jt"><tr><th></th><th>Python</th><th>JavaScript and TypeScript</th><th>Java</th></tr>
<tr><td>Map</td><td><code>dict</code>, <code>Counter</code>, <code>defaultdict</code></td><td><code>Map</code></td><td><code>HashMap</code>, <code>LinkedHashMap</code></td></tr>
<tr><td>Set</td><td><code>set</code></td><td><code>Set</code></td><td><code>HashSet</code></td></tr>
<tr><td>Keeps insertion order</td><td>yes (since 3.7)</td><td>yes</td><td>only <code>LinkedHashMap</code></td></tr></table></div>
<div class="grid2">
<div class="box"><h4>🔢 Count things</h4><p>Word counts, letter counts for anagrams, votes. One pass, one map.</p></div>
<div class="box"><h4>👀 Seen before</h4><p>Duplicates, cycles, visited nodes in a graph. A set answers "have I met this" in O(1).</p></div>
<div class="box"><h4>💞 Find the partner</h4><p>Two sum: for each x, look up target − x among the numbers already passed.</p></div>
<div class="box"><h4>🗂️ Group by a key</h4><p>Group anagrams by their sorted letters, orders by customer, files by size.</p></div>
</div>
<div class="viz" data-viz="pk" data-pk="twosum"></div>
<div class="c3" data-k="patterns" data-label="Counting and two sum"></div>
<div class="warn">In JavaScript a plain object turns every key into a string, so <code>obj[1]</code> and <code>obj["1"]</code> are the same entry. Use <code>Map</code> when keys are numbers or objects.</div>
'''),
    dict(id='good-hash', emoji='🎯', title='Good hash functions, bad ones and attacks', html='''
<p>A good hash function spreads keys evenly and changes a lot when the key changes a little. A lazy one that looks only at the first letter sends "sun", "sea", "sky" and "star" all to the same bucket.</p>
<div class="viz" data-viz="pk" data-pk="spread"></div>
<div class="c3" data-k="spread" data-label="First letter hash versus whole word hash"></div>
<div class="grid2">
<div class="box"><h4>🛡️ Hash flooding</h4><p>In 2011 researchers showed that a web server could be frozen by sending thousands of form fields whose names all collide. Python (since 3.3) and many others now add a random secret to string hashes each time the program starts, so attackers cannot predict the buckets.</p></div>
<div class="box"><h4>🔑 Keys must not change</h4><p>If a key's hash changes after it is stored, the table looks in the wrong bucket and the entry is lost. That is why Python refuses lists as dictionary keys, and why Java objects used as keys must keep <code>equals</code> and <code>hashCode</code> consistent.</p></div>
</div>
<div class="exam">Java contract: if <code>a.equals(b)</code> then <code>a.hashCode() == b.hashCode()</code>. Equal hash codes do not mean equal objects. Override both or neither.</div>
'''),
    dict(id='real-hashing', emoji='🌍', title='Hashing in real systems', html='''
<p>Hash tables are everywhere, and the same idea of a short fingerprint for big data powers many systems you use daily.</p>
<div class="grid2">
<div class="box"><h4>⚡ Caches</h4><p>Websites keep recently computed pages in a map from address to page. Your browser does the same with images. Remembering answers in a map is called memoization, and it turns slow recursive code into fast code.</p></div>
<div class="box"><h4>🔒 Passwords</h4><p>Sites store a slow, salted hash such as bcrypt or Argon2, never the password itself. At login they hash what you type and compare.</p></div>
<div class="box"><h4>🌿 Git</h4><p>Every file and commit is named by a cryptographic hash of its content, so identical files are stored once and any change gives a new name.</p></div>
<div class="box"><h4>🧬 Deduplication</h4><p>Cloud storage hashes uploaded blocks. If a block's hash is already stored, it keeps only a pointer instead of a second copy.</p></div>
</div>
<div class="c3" data-k="memo" data-label="A map as a cache: memoized Fibonacci"></div>
<div class="rule">Cryptographic hashes like SHA-256 are designed so nobody can find two inputs with the same hash. Hash table hashes only need to be fast and well spread.</div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem is solved in the Practice section in Python, JavaScript, Java and TypeScript, with line by line replay. Several already have a Python solution elsewhere on the site, linked from the problem.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>The hashing idea</th></tr>
<tr><td><a href="#lc217">217. Contains Duplicate</a></td><td>Easy</td><td>seen set</td></tr>
<tr><td><a href="#lc205">205. Isomorphic Strings</a></td><td>Easy</td><td>two maps, one per direction</td></tr>
<tr><td><a href="#lc219">219. Contains Duplicate II</a></td><td>Medium</td><td>last index of each value</td></tr>
<tr><td><a href="#lc36">36. Valid Sudoku</a></td><td>Medium</td><td>a set of row, column and box promises</td></tr>
<tr><td><a href="#lc706">706. Design HashMap</a></td><td>Hard</td><td>build chaining yourself</td></tr>
<tr><td><a href="#lc454">454. 4Sum II</a></td><td>Hard</td><td>meet in the middle with a map of sums</td></tr>
<tr><td><a href="#lc128">128. Longest Consecutive Sequence</a></td><td>Expert</td><td>start runs only where x − 1 is missing</td></tr>
<tr><td><a href="#lc380">380. Insert Delete GetRandom O(1)</a></td><td>Expert</td><td>a list plus a map of positions</td></tr></table></div>
'''),
]

VIZ_JS = r'''
(() => {
  const D = PK.defs;
  const poly = w => { let h = 0; for (const ch of w) h = (h * 31 + ch.charCodeAt(0)) % 1000003; return h; };

  D.hashfn = el => PK.widget(el, {
    title: 'Turn a word into a locker number', sub: 'Type a word. Pip mixes its letters into one number, then picks one of 10 buckets.',
    inputs: [{ k: 'w', label: 'Word', type: 'text', val: 'cat', w: 160 }],
    random: () => ({ w: ['riya', 'apple', 'tiger', 'mango', 'india', 'stack', 'queue', 'graph'][Math.floor(Math.random() * 8)] }),
    check: v => /^[A-Za-z]{1,10}$/.test(String(v.w).trim()) ? '' : 'Please type one word of 1 to 10 letters, no spaces or digits.',
    frames: ({ w }) => {
      w = String(w).trim();
      const L = w.split(''), F = [{ mood: 'think', msg: `Start with h = 0. For each letter: h = h × 31 + the letter\'s code. Let us mix "${w}".`, vars: { h: 0 }, layers: [{ t: 'row', cells: L, label: 'Letters' }] }];
      let h = 0;
      L.forEach((c, i) => {
        const old = h;
        h = (h * 31 + c.charCodeAt(0)) % 1000003;
        F.push({ mood: 'work', msg: `Letter "${c}" has code ${c.charCodeAt(0)}. h = ${old} × 31 + ${c.charCodeAt(0)} = <b>${h}</b>${old * 31 + c.charCodeAt(0) !== h ? ' after keeping it small with mod 1000003' : ''}.`,
          say: `Letter ${c} has code ${c.charCodeAt(0)}. ${old} times 31 plus ${c.charCodeAt(0)} gives ${h}.`,
          vars: { h }, layers: [{ t: 'row', cells: L, label: 'Letters', cls: Object.fromEntries(L.map((_, j) => [j, j < i ? 'done' : j === i ? 'look' : ''])) }] });
      });
      const b = h % 10;
      F.push({ mood: 'happy', fx: 'burst', msg: `The hash of "${w}" is ${h}. ${h} mod 10 = <b>${b}</b>, so "${w}" lives in bucket ${b}.`, vars: { h, bucket: b },
        layers: [{ t: 'row', label: 'Ten buckets', cells: Array.from({ length: 10 }, (_, i) => i === b ? '🏠' : ''), cls: { [b]: 'yes' } }] });
      return F;
    }
  });

  D.chain = el => PK.widget(el, {
    title: 'Fill the buckets, then go looking', sub: 'Keys that collide share a chain. Then Pip searches for one key, scanning only its own bucket.',
    inputs: [{ k: 'keys', label: 'Keys', type: 'text', val: 'apple, banana, cherry, date, kiwi, lime', w: 280 },
             { k: 'm', label: 'Buckets', type: 'num', val: 4, min: 2, max: 8 }, { k: 'q', label: 'Search for', type: 'text', val: 'kiwi', w: 110 }],
    random: () => ({ q: ['apple', 'fig', 'lime', 'grape', 'date'][Math.floor(Math.random() * 5)] }),
    check: v => { const a = PK.parseList(v.keys, false); return a.length >= 1 && a.length <= 10 && Number.isInteger(v.m) && v.m >= 2 && v.m <= 8 && String(v.q).trim() ? '' : 'Give 1 to 10 keys, 2 to 8 buckets and one key to search.'; },
    frames: ({ keys, m, q }) => {
      const a = [...new Set(PK.parseList(keys, false))], B = Array.from({ length: m }, () => []), F = [];
      q = String(q).trim();
      const snap = (cls = {}, bcls = {}) => ({ t: 'buckets', buckets: B.map(x => x.slice()), cls, bcls, blab: B.map((_, i) => 'b' + i) });
      F.push({ mood: 'think', msg: `${m} empty buckets. Each key goes to bucket hash(key) mod ${m}.`, layers: [snap()] });
      a.forEach(k => {
        const b = poly(k) % m;
        const col = B[b].length > 0;
        B[b].push(k);
        F.push({ mood: col ? 'wow' : 'work', msg: col ? `"${k}" hashes to bucket ${b}, which already holds ${B[b].length - 1} key${B[b].length > 2 ? 's' : ''}. A collision! It simply joins the chain.` : `"${k}" hashes to bucket ${b}. Empty, so it moves right in.`,
          layers: [snap({ [b + ',' + (B[b].length - 1)]: col ? 'mv' : 'yes' }, { [b]: 'look' })] });
      });
      const b = poly(q) % m;
      F.push({ mood: 'look', msg: `Now search for "${q}". Its hash says bucket ${b}, so we ignore every other bucket.`, layers: [snap({}, { [b]: 'look' })] });
      for (let i = 0; i < B[b].length; i++) {
        if (B[b][i] === q) {
          F.push({ mood: 'happy', fx: 'burst', msg: `Compare with "${B[b][i]}": a match! Found "${q}" after looking at only ${i + 1} key${i ? 's' : ''}, not all ${a.length}.`, layers: [snap({ [b + ',' + i]: 'yes' }, { [b]: 'look' })] });
          return F;
        }
        F.push({ mood: 'look', msg: `Compare with "${B[b][i]}": not it. Next in the chain.`, layers: [snap({ [b + ',' + i]: 'no' }, { [b]: 'look' })] });
      }
      F.push({ mood: 'sad', fx: 'shake', msg: `End of bucket ${b}\'s chain and no "${q}". It is not in the map at all. No need to check other buckets, because "${q}" could only ever live here.`, layers: [snap({}, { [b]: 'look' })] });
      return F;
    }
  });

  D.probe = el => PK.widget(el, {
    title: 'Musical chairs: open addressing', sub: 'Each number wants slot key mod m. If it is taken, it tries the next slot by the chosen rule.',
    inputs: [{ k: 'keys', label: 'Keys to insert', type: 'text', val: '10, 17, 24, 5, 3', w: 200 }, { k: 'm', label: 'Slots m', type: 'num', val: 7, min: 3, max: 13 },
             { k: 'how', label: 'Probing', type: 'seg', val: 'lin', opts: [['lin', '➡️ Linear'], ['quad', '🦘 Quadratic']] }],
    random: () => ({ keys: Array.from({ length: 6 }, () => Math.floor(Math.random() * 60)) }),
    check: v => { const a = PK.parseList(v.keys); return a && a.length >= 1 && a.length <= 12 && a.every(x => Number.isInteger(x) && x >= 0) && Number.isInteger(v.m) && v.m >= 3 && v.m <= 13 ? '' : 'Give 1 to 12 whole numbers of 0 or more, and 3 to 13 slots.'; },
    frames: ({ keys, m, how }) => {
      const a = PK.parseList(keys), T = new Array(m).fill(null), F = [];
      const row = (cls = {}, ptr = {}) => ({ t: 'row', label: 'Table slots', cells: T.map(x => x === null ? '' : x), cls: Object.assign(Object.fromEntries(T.map((x, i) => [i, x === null ? 'ghost' : ''])), cls), ptr });
      F.push({ mood: 'think', msg: `${m} empty slots. ${how === 'lin' ? 'Linear probing tries h, h + 1, h + 2 and so on.' : 'Quadratic probing tries h, h + 1, h + 4, h + 9 and so on.'}`, layers: [row()] });
      for (const k of a) {
        const h = k % m;
        let placed = false;
        for (let j = 0; j < m; j++) {
          const i = (h + (how === 'lin' ? j : j * j)) % m;
          if (T[i] === null) {
            T[i] = k;
            F.push({ mood: j ? 'happy' : 'work', fx: j ? 'burst' : '', msg: j ? `Slot ${i} is free. ${k} sits down after ${j + 1} tries.` : `${k} mod ${m} = ${h}. Slot ${h} is free, so ${k} sits right there.`, layers: [row({ [i]: 'yes' }, { [i]: k })] });
            placed = true;
            break;
          }
          F.push({ mood: 'look', msg: `${j === 0 ? `${k} mod ${m} = ${h}. ` : ''}Slot ${i} is taken by ${T[i]}. Try the next one.`, layers: [row({ [i]: 'no' }, { [i]: k })] });
        }
        if (!placed) F.push({ mood: 'sad', fx: 'shake', msg: `${k} tried every reachable slot and found no chair. ${how === 'quad' ? 'Quadratic probing can miss free slots, which is why table sizes are chosen with care.' : 'The table is full. Time to grow it.'}`, layers: [row()] });
      }
      F.push({ mood: 'wow', msg: `All done. Load factor ${a.filter((_, i) => i < m).length} ÷ ${m}. Notice how keys with the same home bunch into runs.`, layers: [row()] });
      return F;
    }
  });

  D.rehash = el => PK.widget(el, {
    title: 'Too crowded? Grow and re-insert', sub: 'Keys go in one by one. When the load factor passes the limit, the table doubles and every key moves to its new slot.',
    inputs: [{ k: 'n', label: 'How many keys', type: 'num', val: 9, min: 2, max: 14 },
             { k: 'lim', label: 'Grow when α passes', type: 'seg', val: '0.75', opts: [['0.5', '0.5'], ['0.75', '0.75'], ['1', '1.0']] }],
    check: v => (Number.isInteger(v.n) && v.n >= 2 && v.n <= 14) ? '' : 'Pick 2 to 14 keys.',
    frames: ({ n, lim }) => {
      lim = +lim;
      const keys = Array.from({ length: n }, (_, i) => (i * 7 + 3) % 50), F = [];
      let cap = 4, T = new Array(cap).fill(null);
      const put = (tab, k) => { let i = k % tab.length; while (tab[i] !== null) i = (i + 1) % tab.length; tab[i] = k; return i; };
      const row = (cls = {}) => ({ t: 'row', id: 't', label: `Table with ${T.length} slots`, cells: T.map(x => x === null ? '' : x), keys: T, cls: Object.assign(Object.fromEntries(T.map((x, i) => [i, x === null ? 'ghost' : ''])), cls), small: T.length > 16 });
      F.push({ mood: 'think', msg: `Start with ${cap} slots. We grow when keys ÷ slots goes above ${lim}.`, layers: [row()] });
      let size = 0;
      for (const k of keys) {
        const i = put(T, k);
        size++;
        const a = size / T.length;
        F.push({ mood: 'work', msg: `Insert ${k} into slot ${i}. Load factor is ${size} ÷ ${T.length} = ${a.toFixed(2)}.`, vars: { keys: size, slots: T.length, 'α': a.toFixed(2) }, layers: [row({ [i]: 'yes' })] });
        if (a > lim) {
          F.push({ mood: 'wow', fx: 'shake', msg: `${a.toFixed(2)} is above ${lim}. Too crowded! Make a table of ${T.length * 2} slots.`, vars: { keys: size, slots: T.length, 'α': a.toFixed(2) }, layers: [row(Object.fromEntries(T.map((x, j) => [j, x === null ? 'ghost' : 'no'])))] });
          const old = T.filter(x => x !== null);
          T = new Array(T.length * 2).fill(null);
          old.forEach(x => put(T, x));
          F.push({ mood: 'happy', fx: 'burst', msg: `Every key is hashed again with mod ${T.length} and slides to its new home. Load factor is now ${(size / T.length).toFixed(2)}.`, vars: { keys: size, slots: T.length, 'α': (size / T.length).toFixed(2) }, layers: [row(Object.fromEntries(T.map((x, j) => [j, x === null ? 'ghost' : 'mv'])))] });
        }
      }
      F.push({ mood: 'happy', msg: `Finished with ${size} keys in ${T.length} slots. Doubling keeps resizes rare, so inserts stay O(1) on average.` });
      return F;
    }
  });

  D.twosum = el => PK.widget(el, {
    title: 'Two sum with a memory', sub: 'Walk the list once. For each number, ask the map whether its partner (target minus it) was already seen.',
    inputs: [{ k: 'nums', label: 'Numbers', type: 'text', val: '2, 7, 11, 15', w: 200 }, { k: 'target', label: 'Target', type: 'num', val: 9, w: 90 }],
    random: () => { const a = Array.from({ length: 6 }, () => Math.floor(Math.random() * 20)); return { nums: a, target: a[1] + a[4] }; },
    check: v => { const a = PK.parseList(v.nums); return a && a.length >= 2 && a.length <= 10 && Number.isFinite(v.target) ? '' : 'Give 2 to 10 numbers and a target.'; },
    frames: ({ nums, target }) => {
      const a = PK.parseList(nums), seen = new Map(), F = [];
      const mapL = (hl) => ({ t: 'buckets', label: 'The map: value → index', buckets: [[...seen].map(([v, i]) => `${v} → ${i}`)], blab: ['seen'], cls: hl !== undefined ? { ['0,' + [...seen.keys()].indexOf(hl)]: 'yes' } : {} });
      F.push({ mood: 'think', msg: `Find two numbers that add up to <b>${target}</b>. The map starts empty.`, layers: [{ t: 'row', cells: a }, mapL()] });
      for (let i = 0; i < a.length; i++) {
        const x = a[i], need = target - x;
        const cls = Object.fromEntries(a.map((_, j) => [j, j < i ? 'done' : j === i ? 'look' : '']));
        if (seen.has(need)) {
          const j = seen.get(need);
          F.push({ mood: 'happy', fx: 'burst', msg: `${x} needs a partner of ${target} − ${x} = ${need}. The map says ${need} was at index ${j}. Found the pair: indexes <b>${j} and ${i}</b>.`,
            layers: [{ t: 'row', cells: a, cls: Object.assign(cls, { [i]: 'yes', [j]: 'yes' }) }, mapL(need)] });
          return F;
        }
        F.push({ mood: 'look', msg: `${x} needs ${need}. Not in the map yet, so remember ${x} at index ${i} and move on.`, vars: { x, need }, layers: [{ t: 'row', cells: a, cls }, mapL()] });
        seen.set(x, i);
      }
      F.push({ mood: 'sad', fx: 'shake', msg: `We reached the end and no pair adds up to ${target}. Pip checked every number exactly once, so this is certain.`, layers: [{ t: 'row', cells: a, cls: Object.fromEntries(a.map((_, j) => [j, 'done'])) }, mapL()] });
      return F;
    }
  });

  D.spread = el => PK.widget(el, {
    title: 'Lazy hash versus good hash', sub: 'Drop words into 8 buckets. Compare a hash that looks only at the first letter with one that mixes every letter.',
    inputs: [{ k: 'words', label: 'Words', type: 'text', val: 'sun, sea, sky, star, salt, sand, ship, shop, fish, fog', w: 320 },
             { k: 'h', label: 'Hash', type: 'seg', val: 'bad', opts: [['bad', '😴 First letter'], ['good', '🌪️ Whole word']] }],
    check: v => { const a = PK.parseList(v.words, false); return a.length >= 2 && a.length <= 16 && a.every(x => /^[A-Za-z]+$/.test(x)) ? '' : 'Give 2 to 16 words made of letters.'; },
    frames: ({ words, h }) => {
      const a = PK.parseList(words, false), cnt = new Array(8).fill(0), F = [];
      F.push({ mood: 'think', msg: h === 'bad' ? 'This hash uses only the code of the first letter, mod 8.' : 'This hash mixes every letter with h × 31 + code, then takes mod 8.', layers: [{ t: 'bars', vals: cnt.slice(), max: a.length }] });
      a.forEach(w => {
        const b = (h === 'bad' ? w.charCodeAt(0) : poly(w)) % 8;
        cnt[b]++;
        F.push({ mood: cnt[b] > 2 ? 'sad' : 'work', msg: `"${w}" goes to bucket ${b}.${cnt[b] > 2 ? ` That bucket now has ${cnt[b]} words. The chain is getting long.` : ''}`, layers: [{ t: 'bars', vals: cnt.slice(), max: a.length, cls: { [b]: cnt[b] > 2 ? 'no' : 'look' } }] });
      });
      const mx = Math.max(...cnt);
      F.push({ mood: mx > Math.ceil(a.length / 8) + 1 ? 'sad' : 'happy', fx: mx > Math.ceil(a.length / 8) + 1 ? 'shake' : 'burst',
        msg: `The longest chain has <b>${mx}</b> words. ${mx > Math.ceil(a.length / 8) + 1 ? 'Lookups in that bucket are slow. Try the other hash.' : 'Nicely spread, so every lookup stays quick.'}`,
        layers: [{ t: 'bars', vals: cnt.slice(), max: a.length, cls: Object.fromEntries(cnt.map((c, i) => [i, c === mx ? 'no' : 'yes'])) }] });
      return F;
    }
  });
})();
'''

INFO = {
    'title': 'A locker number for every key',
    'panels': [
        {'s': [['e', '🗄️'], ['t', 'bucket = hash(key) mod m', {'b': 1}]], 'h': 'Hashing', 't': 'Jump straight to the right slot.', 'more': 'The same key always gives the same hash, so lookups skip the searching.'},
        {'s': [['e', '⛓️'], ['t', 'cat, act, tac → bucket 2', {'b': 1}]], 'h': 'Collisions', 't': 'Two keys, one bucket.', 'more': 'Chaining keeps a list per bucket. Open addressing probes for the next free slot.'},
        {'s': [['e', '🎈'], ['t', 'α = n ÷ m', {'b': 1}]], 'h': 'Load factor', 't': 'Grow before it gets crowded.', 'more': 'Doubling the table keeps inserts O(1) amortized.'},
        {'s': [['e', '💞'], ['t', 'look up target − x', {'b': 1}]], 'h': 'Patterns', 't': 'Count, seen, partner, group.', 'more': 'Four patterns cover most hash map problems.'},
    ],
    'remember': 'A hash map gives O(1) average lookups by turning keys into bucket numbers. Collisions are normal, a low load factor keeps them cheap, and keys must never change after they are stored.',
}

REAL = [
    ['📱', 'Your phone contacts', 'Typing a name jumps straight to the person, even with thousands of contacts, because the app keeps an index from names to entries instead of scanning them all.'],
    ['🔑', 'Logging in to a website', 'The site never stores your password. It stores a salted, slow hash of it, hashes what you type and compares the two.'],
    ['🛒', 'An online shop cart', 'The cart is a map from product id to quantity. Adding the same item again just bumps the count instead of adding a second line.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to hashing. A hash map lets you find things almost instantly by turning each key into a locker number. You will see how hash functions work, what happens when two keys want the same locker, how tables grow when they get crowded, the everyday patterns that use maps and sets, and how hashing protects passwords and powers caches.'},
    {'id': 'what-is-hashing', 'h': 'Hashing', 'en': 'A hash function turns a key into a big number, always the same number for the same key. Taking that number modulo the table size gives a bucket. To find a key you hash it and go straight to its bucket, without searching the others.'},
    {'id': 'chaining', 'h': 'Chaining', 'en': 'Collisions happen when two keys land in the same bucket, and with more keys than buckets they are certain. Separate chaining keeps a small list in each bucket. A search only scans the list in its own bucket, so on average it is constant time.'},
    {'id': 'open-addressing', 'h': 'Open addressing', 'en': 'Open addressing keeps one key per slot. If the slot is taken, it probes other slots in a fixed order, such as the next slot for linear probing. A search stops at an empty slot. Deleting needs a tombstone marker so that probe chains are not broken.'},
    {'id': 'load-factor', 'h': 'Load factor', 'en': 'The load factor is the number of keys divided by the number of slots. When it passes a limit, such as zero point seven five in Java, the table doubles and every key is inserted again. Resizing is rare, so each insert is still constant time on average.'},
    {'id': 'patterns', 'h': 'Patterns', 'en': 'Most map problems use four patterns: counting things, remembering what you have seen, looking up the partner that completes a pair, and grouping by a key. Python has dict and set, JavaScript and TypeScript have Map and Set, and Java has HashMap and HashSet.'},
    {'id': 'good-hash', 'h': 'Good hashes', 'en': 'A good hash spreads keys evenly. A lazy hash, such as one that only reads the first letter, piles many keys into one bucket and slows everything down. Attackers once used deliberate collisions to freeze web servers, so modern languages add a random secret to string hashes. Keys must never change after they are stored.'},
    {'id': 'real-hashing', 'h': 'Real systems', 'en': 'Hashing is everywhere. Caches map requests to saved answers. Websites store salted password hashes instead of passwords. Git names every file by the hash of its content. Cloud storage spots duplicate blocks by their hashes and keeps only one copy.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from contains duplicate up to insert delete get random in constant time. Each one is solved in Python, JavaScript, Java and TypeScript, and you can replay every solution line by line.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. Try each LeetCode problem on your own first, then open the hint, and only then the full approach and code. Tick the box when you solve one.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'What is the average time to look up a key in a hash map?', 'o': ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)'], 'a': 0, 'hint': 'The hash jumps straight to a bucket.', 'why': 'With a good hash and a low load factor, each bucket holds only a few keys.'},
    {'lv': 'e', 'q': 'What is a collision?', 'o': ['Two keys with the same value', 'Two different keys in the same bucket', 'A key that is missing', 'A table that is full'], 'a': 1, 'hint': 'Think of two students given the same locker.', 'why': 'Different keys can map to the same bucket, and the table must handle it.'},
    {'lv': 'e', 'q': 'Which structure answers "have I seen this value before" fastest?', 'o': ['A sorted array', 'A hash set', 'A linked list', 'A stack'], 'a': 1, 'hint': 'You only need yes or no.', 'why': 'A hash set checks membership in O(1) on average.'},
    {'lv': 'e', 'q': 'A table has 10 slots and 7 keys. What is its load factor?', 'o': ['0.7', '1.43', '3', '70'], 'a': 0, 'hint': 'Keys divided by slots.', 'why': '7 ÷ 10 = 0.7.'},
    {'lv': 'm', 'q': 'Why can a Python list not be a dictionary key?', 'o': ['Lists are too big', 'Lists can change, so their hash would change', 'Lists have no length', 'Only strings can be keys'], 'a': 1, 'hint': 'What happens if the key changes after it is stored?', 'why': 'A changed key would hash to a different bucket and the entry would be lost. Use a tuple instead.'},
    {'lv': 'm', 'q': 'With linear probing in a table of size 7, keys 3, 10 and 17 are inserted in that order. Where does 17 go?', 'o': ['Slot 3', 'Slot 4', 'Slot 5', 'Slot 0'], 'a': 2, 'hint': 'All three have the same home slot.', 'why': '3 takes slot 3, 10 moves to 4, and 17 tries 3 and 4 before settling in 5.'},
    {'lv': 'm', 'q': 'Why does deleting from an open addressing table use a tombstone?', 'o': ['To save memory', 'An empty slot would stop later searches too early', 'To make inserts faster', 'Tombstones are only for chaining'], 'a': 1, 'hint': 'Searches stop at the first empty slot.', 'why': 'Keys placed after the deleted one would become unreachable if the slot looked empty.'},
    {'lv': 'm', 'q': 'At what load factor does Java\'s HashMap grow by default?', 'o': ['0.5', '0.75', '1.0', '2.0'], 'a': 1, 'hint': 'Three quarters full.', 'why': 'The default load factor is 0.75, a balance between memory and speed.'},
    {'lv': 'h', 'q': 'In Java, a.equals(b) is true. What must also be true?', 'o': ['a == b', 'a.hashCode() == b.hashCode()', 'a and b are the same class', 'Nothing else'], 'a': 1, 'hint': 'Equal keys must land in the same bucket.', 'why': 'Otherwise a HashMap would look in the wrong bucket for an equal key.'},
    {'lv': 'h', 'q': 'What does this print in JavaScript?', 'code': 'const o = {};\no[1] = "a";\no["1"] = "b";\nconsole.log(Object.keys(o).length);', 'o': ['0', '1', '2', 'Error'], 'a': 1, 'hint': 'Object keys become strings.', 'why': '1 and "1" are the same property name, so the second assignment overwrites the first.'},
    {'lv': 'h', 'q': 'A table doubles from 4 slots whenever the load factor passes 0.75. After 20 inserts, how many slots does it have?', 'o': ['16', '32', '64', '20'], 'a': 1, 'hint': 'It grows at 4, 7 and 13 keys.', 'why': '4 to 8 at 4 keys, 8 to 16 at 7 keys, 16 to 32 at 13 keys. 20 ÷ 32 is about 0.63, so no more growth.'},
    {'lv': 'h', 'q': 'What is the worst case lookup time in a hash map with chaining and a terrible hash?', 'o': ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'], 'a': 2, 'hint': 'Every key in one bucket.', 'why': 'The table becomes one long list. Java 8 trees the chain to get O(log n) instead.'},
    {'lv': 'x', 'q': 'Why did Python start adding a random secret to string hashes in version 3.3?', 'o': ['To make hashing faster', 'To stop attackers from forcing collisions', 'To save memory', 'To sort dictionaries'], 'a': 1, 'hint': 'Hash flooding.', 'why': 'If attackers know the hash, they can send keys that all collide and freeze the server.'},
    {'lv': 'x', 'q': 'In 4Sum II with lists of length 200, roughly how many map operations does the meet in the middle solution do?', 'o': ['800', '80,000', '1.6 billion', '200'], 'a': 1, 'hint': 'n² for each half.', 'why': '200² = 40,000 inserts plus 40,000 lookups, instead of 200⁴ = 1.6 billion checks.'},
    {'lv': 'x', 'q': 'Longest Consecutive Sequence has a while loop inside a for loop. Why is it still O(n)?', 'o': ['The while loop runs at most once', 'Each number is walked over by only one run', 'The set is sorted', 'It uses binary search'], 'a': 1, 'hint': 'Runs only start where x − 1 is missing.', 'why': 'Every number belongs to exactly one run, and each run is walked once from its start.'},
    {'lv': 'x', 'q': 'With linear probing and load factor 0.9, the expected probes for a failed search are about ½(1 + 1 ÷ (1 − α)²). Roughly how many is that?', 'o': ['2', '10', '50', '100'], 'a': 2, 'hint': '1 − 0.9 = 0.1, and 1 ÷ 0.01 = 100.', 'why': '½ × (1 + 100) ≈ 50, which is why tables grow long before they are full.'},
]

CALC = [
    {'lv': 'e', 'q': 'A key hashes to 1234. The table has 10 buckets. Which bucket does it use?', 'ans': '4', 'hint': 'hash mod m.', 'steps': ['<span class="eq">1234 mod 10 = 4</span>']},
    {'lv': 'e', 'q': 'A hash map holds 30 keys in 40 buckets. What is the load factor?', 'ans': '0.75', 'hint': 'n ÷ m.', 'steps': ['<span class="eq">30 ÷ 40 = 0.75</span>']},
    {'lv': 'm', 'q': 'Using h = h × 31 + code, what is the hash of "ab"? The code of a is 97 and of b is 98.', 'ans': '3105', 'hint': 'Start with h = 0.', 'steps': ['After a: <span class="eq">0 × 31 + 97 = 97</span>', 'After b: <span class="eq">97 × 31 + 98 = 3105</span>']},
    {'lv': 'm', 'q': 'Linear probing, table size 5. Insert 7, 12, 2 in order. In which slot does 2 end up?', 'ans': '4', 'hint': 'All three have home slot 2.', 'steps': ['7 goes to slot 2.', '12 finds 2 taken and goes to 3.', '2 finds 2 and 3 taken and goes to <span class="eq">4</span>.']},
    {'lv': 'h', 'q': 'How many different pairs of people are there among 23 people? (This is behind the birthday paradox.)', 'ans': '253', 'hint': 'n(n − 1) ÷ 2.', 'steps': ['<span class="eq">23 × 22 ÷ 2 = 253</span>', 'So many pairs make a shared birthday, a collision, more likely than not.']},
    {'lv': 'h', 'q': 'Quadratic probing in a table of size 11. A key has home slot 9 and the first three slots tried are taken. Which slot is tried fourth?', 'ans': '7', 'hint': 'Tries are h, h + 1, h + 4, h + 9.', 'steps': ['<span class="eq">(9 + 9) mod 11 = 18 mod 11 = 7</span>']},
    {'lv': 'x', 'q': 'A table starts with 8 slots and doubles whenever the load factor goes above 0.75. How many slots does it have after 30 keys?', 'ans': '64', 'hint': 'Find the key counts where keys ÷ slots first goes above 0.75.', 'steps': ['7 ÷ 8 = 0.875, so at 7 keys it grows to 16.', '13 ÷ 16 = 0.8125, so at 13 keys it grows to 32.', '25 ÷ 32 = 0.78, so at 25 keys it grows to 64.', '30 ÷ 64 = 0.47, so it stays at <span class="eq">64</span>.']},
    {'lv': 'x', 'q': 'In Java, what is "Aa".hashCode()? The code of A is 65 and of a is 97.', 'ans': '2112', 'hint': 's[0] × 31 + s[1].', 'steps': ['<span class="eq">65 × 31 + 97 = 2015 + 97 = 2112</span>', '"BB" gives <span class="eq">66 × 31 + 66 = 2112</span> too, a famous collision used in hash flooding attacks.']},
]

TALK = {
    'what-is-hashing': 'Think about a big school with a hundred lockers. If lockers were given out randomly, finding your friend\'s books would mean opening locker after locker. Now imagine a simple rule that turns any name into a locker number. You say the name, apply the rule, and walk straight to the right locker. That rule is a hash function, the number it gives is called the hash, and the row of lockers is the hash table. The rule must be fair and repeatable. The same name must always give the same locker, or you would never find anything again. A popular rule for words goes letter by letter, multiplying the running total by thirty one and adding the code of the next letter. Then the remainder after dividing by the number of lockers tells you which locker to use. Phone contacts, dictionaries in Python and objects in JavaScript all work this way underneath.',
    'chaining': 'Here is the catch. If there are more names than lockers, two names must sometimes share a locker. Even with fewer names it happens surprisingly often, just like two people in a class sharing a birthday. This sharing is called a collision, and it is completely normal. The simplest fix is called chaining. Each locker holds a small list instead of one item. When a new name lands in a locker that is already used, it is simply added to that locker\'s list. When you search, you go to the one locker the rule gives you and look through only that short list. If the name is not in that list, it is not anywhere in the table, so you never need to open the other lockers. As long as the lists stay short, finding anything takes just a moment, no matter how many names there are.',
    'open-addressing': 'There is a second way to deal with collisions, called open addressing. Think of a cinema where your ticket says seat number seven. If someone is already sitting in seat seven, you do not sit on their lap. You move to seat eight, then nine, until you find a free one. That is linear probing. When you later come back to find your friend, you start at their ticket seat and walk along the row until you either find them or reach an empty seat, which means they are not in this cinema. A problem appears when people leave. If you simply empty a seat, someone searching further along might stop too early at that gap. So the seat gets a little sign that says someone used to be here, keep looking. Python dictionaries use this seat hopping idea, while Java hash maps use chaining.',
    'load-factor': 'Imagine a car park. When it is almost empty, you find a space right away. When it is nearly full, you drive around and around looking for one. Hash tables behave the same way. The load factor is how full the table is, the number of keys divided by the number of slots. When it climbs too high, chains get long or probing walks get long, and everything slows down. So a hash table watches its load factor. When it passes a limit, such as three quarters full, it builds a new table about twice as big and moves every key into it. Every key must be placed again, because its locker number depends on the size of the table. Moving everything sounds expensive, but because the table doubles, this happens rarely, and on average each insert still costs only a tiny constant amount of work.',
    'patterns': 'In real code you almost never build a hash table yourself. Python gives you dict and set, JavaScript and TypeScript give you Map and Set, and Java gives you HashMap and HashSet. What matters is knowing a few patterns, because they solve a huge number of problems. The first is counting, like counting how many times each word appears in a story. The second is remembering what you have seen, like spotting a repeated value or a place you already visited. The third is finding a partner. In the famous two sum problem, for every number you ask whether the number that completes the target was already seen. The fourth is grouping, like putting all the anagrams together by sorting their letters. Once you start noticing these four patterns, you will see them in shopping carts, school records, chat apps and almost every interview question.',
    'good-hash': 'Not every hash rule is a good one. Suppose a lazy rule looks only at the first letter of a word. Then sun, sea, sky, star, salt and sand all crowd into the same locker while the others stay empty, and looking anything up becomes slow again. A good rule spreads keys evenly and changes a lot when the word changes even a little. There is also a security story here. In 2011 researchers showed that a web server could be frozen by sending it thousands of carefully chosen names that all landed in the same locker. Languages fought back. Python now mixes a secret random number into its string hashes every time a program starts, so attackers cannot plan the collisions. One more rule matters for you as a programmer. A key must never change after you store it, or the table will look in the wrong locker and your data will seem to vanish.',
    'real-hashing': 'Hashing quietly runs much of the internet. When a website remembers pages it built recently so it can send them again instantly, that memory is a hash map from address to page. When you create an account, a careful website never keeps your actual password. It keeps a special slow hash of it, mixed with a random salt, and at login it hashes what you typed and compares. If hackers steal the database, they get scrambled fingerprints instead of passwords. Git, the tool programmers use to track code, names every file by a hash of its contents, so two identical files are stored only once. Cloud storage services do the same with chunks of your photos and videos. Even in this lesson, the memoized Fibonacci program uses a map to remember answers, turning millions of repeated calculations into just a handful of quick lookups.',
    'leetcode': 'The LeetCode problems in this chapter are the hash map questions interviewers love. You begin with spotting duplicates using a seen set, and checking whether two words follow the same letter pattern using two maps. Then you check a Sudoku board by turning every digit into three promises about its row, its column and its box. Next you build your own hash map from scratch with chaining, just like the one in the lesson, and count four number combinations with the clever meet in the middle trick that turns billions of checks into thousands. Finally you find the longest run of consecutive numbers in one pass, and design a set that can insert, remove and pick a random member, all instantly. Every problem comes with a hint, a full explanation and code in Python, JavaScript, Java and TypeScript that you can play step by step.',
}

T = t.finish({
    'slug': 'hashing', 'title': 'Hashing and Hash Tables', 'short': 'Hashing', 'emoji': '🗄️', 'topic': 'hashing', 'prefix': 'dsahash',
    'module': ('🧱', 'Core building blocks'),
    'lead': 'How can a phone find one contact among thousands without searching? It turns each name into a locker number. Learn hash functions, collisions, chaining and probing, load factors and resizing, the four everyday map patterns, and how hashing guards passwords and powers caches.',
    'desc': 'Hashing and hash tables in DSA: hash functions, buckets and collisions, separate chaining, linear and quadratic probing, load factor and rehashing, hash map and set patterns, good and bad hash functions, hash flooding, and real uses, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 20,
    'summary': 'Hash functions and buckets, collisions with chaining and open addressing, load factor and resizing, the counting, seen, partner and grouping patterns, good and bad hashes, hash flooding, and hashing in caches, passwords and Git. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['hashing', 'hash table', 'hash map', 'hash set', 'hash function', 'collision', 'chaining', 'open addressing', 'linear probing', 'load factor', 'rehashing', 'two sum', 'dict', 'HashMap', 'Map', 'memoization', 'hash flooding'],
    'added': '2026-11-22',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS, 'css': '',
    'prev': ('strings', 'strings', '🔤 Strings'),
    'next': ('linked-lists', 'linked-lists', '🔗 Linked lists'),
})
