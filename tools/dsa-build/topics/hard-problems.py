# Hard problems: P and NP, reductions, approximation, randomized selection, random sampling and Monte Carlo.
from kit4 import Topic

t = Topic()

# ---------------------------------------------------------------- lesson programs
t.code('subsetsum', py=r'''
nums = [3, 34, 4, 12, 5, 2]


def solve(target):                               # try every subset: there are 2**n of them
    n, tries = len(nums), 0
    for mask in range(1 << n):
        tries += 1
        pick = [nums[i] for i in range(n) if mask >> i & 1]
        if sum(pick) == target:
            return pick, tries
    return None, tries


def verify(pick, target):                        # checking a proposed answer is one quick pass
    return sum(pick) == target


print(f"{len(nums)} numbers, {1 << len(nums)} subsets to try")
for target in (9, 30):
    pick, tries = solve(target)
    if pick is None:
        print(f"target {target}: no subset works, {tries} subsets tried")
    else:
        print(f"target {target}: found {pick} after {tries} tries, check: {'true' if verify(pick, target) else 'false'}")
print(f"with 40 numbers: {1 << 40} subsets")
''', js=r'''
const nums = [3, 34, 4, 12, 5, 2];

function solve(target) {                             // try every subset: there are 2**n of them
  const n = nums.length;
  let tries = 0;
  for (let mask = 0; mask < (1 << n); mask++) {
    tries++;
    const pick = nums.filter((_, i) => (mask >> i) & 1);
    if (pick.reduce((s, x) => s + x, 0) === target) return [pick, tries];
  }
  return [null, tries];
}

function verify(pick, target) {                      // checking a proposed answer is one quick pass
  return pick.reduce((s, x) => s + x, 0) === target;
}

console.log(`${nums.length} numbers, ${1 << nums.length} subsets to try`);
for (const target of [9, 30]) {
  const [pick, tries] = solve(target);
  if (pick === null) console.log(`target ${target}: no subset works, ${tries} subsets tried`);
  else console.log(`target ${target}: found [${pick.join(", ")}] after ${tries} tries, check: ${verify(pick, target)}`);
}
console.log(`with 40 numbers: ${2 ** 40} subsets`);
''', java=r'''
import java.util.*;

public class SubsetSum {
    static int[] nums = {3, 34, 4, 12, 5, 2};
    static int tries;

    static List<Integer> solve(int target) {         // try every subset: there are 2**n of them
        int n = nums.length;
        tries = 0;
        for (int mask = 0; mask < (1 << n); mask++) {
            tries++;
            List<Integer> pick = new ArrayList<>();
            int sum = 0;
            for (int i = 0; i < n; i++) if ((mask >> i & 1) == 1) { pick.add(nums[i]); sum += nums[i]; }
            if (sum == target) return pick;
        }
        return null;
    }

    static boolean verify(List<Integer> pick, int target) {   // checking a proposed answer is one quick pass
        int sum = 0;
        for (int x : pick) sum += x;
        return sum == target;
    }

    public static void main(String[] args) {
        System.out.println(nums.length + " numbers, " + (1 << nums.length) + " subsets to try");
        for (int target : new int[]{9, 30}) {
            List<Integer> pick = solve(target);
            if (pick == null) System.out.println("target " + target + ": no subset works, " + tries + " subsets tried");
            else System.out.println("target " + target + ": found " + pick + " after " + tries + " tries, check: " + verify(pick, target));
        }
        System.out.println("with 40 numbers: " + (1L << 40) + " subsets");
    }
}
''', ts=r'''
const nums: number[] = [3, 34, 4, 12, 5, 2];

function solve(target: number): [number[] | null, number] {   // try every subset: there are 2**n of them
  const n = nums.length;
  let tries = 0;
  for (let mask = 0; mask < (1 << n); mask++) {
    tries++;
    const pick = nums.filter((_, i) => (mask >> i) & 1);
    if (pick.reduce((s, x) => s + x, 0) === target) return [pick, tries];
  }
  return [null, tries];
}

function verify(pick: number[], target: number): boolean {   // checking a proposed answer is one quick pass
  return pick.reduce((s, x) => s + x, 0) === target;
}

console.log(`${nums.length} numbers, ${1 << nums.length} subsets to try`);
for (const target of [9, 30]) {
  const [pick, tries] = solve(target);
  if (pick === null) console.log(`target ${target}: no subset works, ${tries} subsets tried`);
  else console.log(`target ${target}: found [${pick.join(", ")}] after ${tries} tries, check: ${verify(pick, target)}`);
}
console.log(`with 40 numbers: ${2 ** 40} subsets`);
''')

t.code('reduction', py=r'''
N = 6
EDGES = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4), (3, 5), (4, 5)]


def independent(mask):                           # no edge has both ends inside the set
    return all(not (mask >> u & 1 and mask >> v & 1) for u, v in EDGES)


def covers(mask):                                # every edge has at least one end inside the set
    return all(mask >> u & 1 or mask >> v & 1 for u, v in EDGES)


best = 0
for mask in range(1 << N):
    if independent(mask) and bin(mask).count("1") > bin(best).count("1"):
        best = mask
cover = (1 << N) - 1 - best                      # the reduction: take every other vertex
ind_list = [v for v in range(N) if best >> v & 1]
cov_list = [v for v in range(N) if cover >> v & 1]
print(f"largest independent set: {ind_list}")
print(f"the other vertices: {cov_list}, a vertex cover: {'true' if covers(cover) else 'false'}")
print(f"{len(ind_list)} + {len(cov_list)} = {N} vertices")
''', js=r'''
const N = 6;
const EDGES = [[0, 1], [0, 2], [1, 2], [1, 3], [2, 4], [3, 4], [3, 5], [4, 5]];

function independent(mask) {                         // no edge has both ends inside the set
  return EDGES.every(([u, v]) => !(((mask >> u) & 1) && ((mask >> v) & 1)));
}

function covers(mask) {                              // every edge has at least one end inside the set
  return EDGES.every(([u, v]) => ((mask >> u) & 1) || ((mask >> v) & 1));
}

const ones = m => { let c = 0; for (; m; m >>= 1) c += m & 1; return c; };
let best = 0;
for (let mask = 0; mask < (1 << N); mask++) {
  if (independent(mask) && ones(mask) > ones(best)) best = mask;
}
const cover = (1 << N) - 1 - best;                   // the reduction: take every other vertex
const indList = [], covList = [];
for (let v = 0; v < N; v++) ((best >> v) & 1 ? indList : covList).push(v);
console.log(`largest independent set: [${indList.join(", ")}]`);
console.log(`the other vertices: [${covList.join(", ")}], a vertex cover: ${covers(cover)}`);
console.log(`${indList.length} + ${covList.length} = ${N} vertices`);
''', java=r'''
import java.util.*;

public class Reduction {
    static final int N = 6;
    static final int[][] EDGES = {{0, 1}, {0, 2}, {1, 2}, {1, 3}, {2, 4}, {3, 4}, {3, 5}, {4, 5}};

    static boolean independent(int mask) {           // no edge has both ends inside the set
        for (int[] e : EDGES) if ((mask >> e[0] & 1) == 1 && (mask >> e[1] & 1) == 1) return false;
        return true;
    }

    static boolean covers(int mask) {                // every edge has at least one end inside the set
        for (int[] e : EDGES) if ((mask >> e[0] & 1) == 0 && (mask >> e[1] & 1) == 0) return false;
        return true;
    }

    public static void main(String[] args) {
        int best = 0;
        for (int mask = 0; mask < (1 << N); mask++) {
            if (independent(mask) && Integer.bitCount(mask) > Integer.bitCount(best)) best = mask;
        }
        int cover = (1 << N) - 1 - best;             // the reduction: take every other vertex
        List<Integer> indList = new ArrayList<>(), covList = new ArrayList<>();
        for (int v = 0; v < N; v++) ((best >> v & 1) == 1 ? indList : covList).add(v);
        System.out.println("largest independent set: " + indList);
        System.out.println("the other vertices: " + covList + ", a vertex cover: " + covers(cover));
        System.out.println(indList.size() + " + " + covList.size() + " = " + N + " vertices");
    }
}
''', ts=r'''
const N = 6;
const EDGES: number[][] = [[0, 1], [0, 2], [1, 2], [1, 3], [2, 4], [3, 4], [3, 5], [4, 5]];

function independent(mask: number): boolean {       // no edge has both ends inside the set
  return EDGES.every(([u, v]) => !(((mask >> u) & 1) && ((mask >> v) & 1)));
}

function covers(mask: number): boolean {            // every edge has at least one end inside the set
  return EDGES.every(([u, v]) => ((mask >> u) & 1) || ((mask >> v) & 1));
}

const ones = (m: number): number => { let c = 0; for (; m; m >>= 1) c += m & 1; return c; };
let best = 0;
for (let mask = 0; mask < (1 << N); mask++) {
  if (independent(mask) && ones(mask) > ones(best)) best = mask;
}
const cover = (1 << N) - 1 - best;                   // the reduction: take every other vertex
const indList: number[] = [], covList: number[] = [];
for (let v = 0; v < N; v++) ((best >> v) & 1 ? indList : covList).push(v);
console.log(`largest independent set: [${indList.join(", ")}]`);
console.log(`the other vertices: [${covList.join(", ")}], a vertex cover: ${covers(cover)}`);
console.log(`${indList.length} + ${covList.length} = ${N} vertices`);
''')

t.code('approxvc', py=r'''
N = 6
EDGES = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4), (3, 5), (4, 5)]


def approx_cover():                              # any edge still uncovered: take both of its ends
    chosen = [False] * N
    for u, v in EDGES:
        if not chosen[u] and not chosen[v]:
            chosen[u] = chosen[v] = True
            print(f"edge {u}-{v} is not covered: take {u} and {v}")
    return [v for v in range(N) if chosen[v]]


def best_cover_size():                           # exact answer by trying every subset, only for checking
    best = N
    for mask in range(1 << N):
        if all(mask >> u & 1 or mask >> v & 1 for u, v in EDGES):
            best = min(best, bin(mask).count("1"))
    return best


cover = approx_cover()
opt = best_cover_size()
print(f"quick cover: {cover}, size {len(cover)}")
print(f"best cover size: {opt}, within 2 times: {'true' if len(cover) <= 2 * opt else 'false'}")
''', js=r'''
const N = 6;
const EDGES = [[0, 1], [0, 2], [1, 2], [1, 3], [2, 4], [3, 4], [3, 5], [4, 5]];

function approxCover() {                             // any edge still uncovered: take both of its ends
  const chosen = new Array(N).fill(false);
  for (const [u, v] of EDGES) {
    if (!chosen[u] && !chosen[v]) {
      chosen[u] = chosen[v] = true;
      console.log(`edge ${u}-${v} is not covered: take ${u} and ${v}`);
    }
  }
  return [...Array(N).keys()].filter(v => chosen[v]);
}

function bestCoverSize() {                           // exact answer by trying every subset, only for checking
  let best = N;
  for (let mask = 0; mask < (1 << N); mask++) {
    if (EDGES.every(([u, v]) => ((mask >> u) & 1) || ((mask >> v) & 1))) {
      let c = 0;
      for (let m = mask; m; m >>= 1) c += m & 1;
      best = Math.min(best, c);
    }
  }
  return best;
}

const cover = approxCover();
const opt = bestCoverSize();
console.log(`quick cover: [${cover.join(", ")}], size ${cover.length}`);
console.log(`best cover size: ${opt}, within 2 times: ${cover.length <= 2 * opt}`);
''', java=r'''
import java.util.*;

public class ApproxCover {
    static final int N = 6;
    static final int[][] EDGES = {{0, 1}, {0, 2}, {1, 2}, {1, 3}, {2, 4}, {3, 4}, {3, 5}, {4, 5}};

    static List<Integer> approxCover() {             // any edge still uncovered: take both of its ends
        boolean[] chosen = new boolean[N];
        for (int[] e : EDGES) {
            int u = e[0], v = e[1];
            if (!chosen[u] && !chosen[v]) {
                chosen[u] = chosen[v] = true;
                System.out.println("edge " + u + "-" + v + " is not covered: take " + u + " and " + v);
            }
        }
        List<Integer> out = new ArrayList<>();
        for (int v = 0; v < N; v++) if (chosen[v]) out.add(v);
        return out;
    }

    static int bestCoverSize() {                     // exact answer by trying every subset, only for checking
        int best = N;
        for (int mask = 0; mask < (1 << N); mask++) {
            boolean ok = true;
            for (int[] e : EDGES) if ((mask >> e[0] & 1) == 0 && (mask >> e[1] & 1) == 0) ok = false;
            if (ok) best = Math.min(best, Integer.bitCount(mask));
        }
        return best;
    }

    public static void main(String[] args) {
        List<Integer> cover = approxCover();
        int opt = bestCoverSize();
        System.out.println("quick cover: " + cover + ", size " + cover.size());
        System.out.println("best cover size: " + opt + ", within 2 times: " + (cover.size() <= 2 * opt));
    }
}
''', ts=r'''
const N = 6;
const EDGES: number[][] = [[0, 1], [0, 2], [1, 2], [1, 3], [2, 4], [3, 4], [3, 5], [4, 5]];

function approxCover(): number[] {                   // any edge still uncovered: take both of its ends
  const chosen: boolean[] = new Array(N).fill(false);
  for (const [u, v] of EDGES) {
    if (!chosen[u] && !chosen[v]) {
      chosen[u] = chosen[v] = true;
      console.log(`edge ${u}-${v} is not covered: take ${u} and ${v}`);
    }
  }
  return [...Array(N).keys()].filter(v => chosen[v]);
}

function bestCoverSize(): number {                   // exact answer by trying every subset, only for checking
  let best = N;
  for (let mask = 0; mask < (1 << N); mask++) {
    if (EDGES.every(([u, v]) => ((mask >> u) & 1) || ((mask >> v) & 1))) {
      let c = 0;
      for (let m = mask; m; m >>= 1) c += m & 1;
      best = Math.min(best, c);
    }
  }
  return best;
}

const cover = approxCover();
const opt = bestCoverSize();
console.log(`quick cover: [${cover.join(", ")}], size ${cover.length}`);
console.log(`best cover size: ${opt}, within 2 times: ${cover.length <= 2 * opt}`);
''')

t.code('quickselect', py=r'''
seed = 3


def rand(n):                                     # a tiny repeatable random generator, so every language agrees
    global seed
    seed = (seed * 75 + 74) % 65537
    return seed % n


def quickselect(a, k):                           # the k-th smallest value, k counted from 1
    lo, hi = 0, len(a) - 1
    while True:
        p = lo + rand(hi - lo + 1)               # a random pivot
        a[p], a[hi] = a[hi], a[p]
        pivot, store = a[hi], lo
        for i in range(lo, hi):                  # smaller values move to the left part
            if a[i] < pivot:
                a[i], a[store] = a[store], a[i]
                store += 1
        a[store], a[hi] = a[hi], a[store]
        print(f"pivot {pivot} lands at index {store}: {a[lo:hi + 1]}")
        if store == k - 1:
            return a[store]
        if store < k - 1:                        # keep only the side that holds the answer
            lo = store + 1
        else:
            hi = store - 1


a = [7, 2, 9, 4, 1, 8, 3, 6, 5]
print(f"4th smallest: {quickselect(a[:], 4)}")
print(f"7th smallest: {quickselect(a[:], 7)}")
''', js=r'''
let seed = 3;

function rand(n) {                                   // a tiny repeatable random generator, so every language agrees
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

function quickselect(a, k) {                         // the k-th smallest value, k counted from 1
  let lo = 0, hi = a.length - 1;
  while (true) {
    const p = lo + rand(hi - lo + 1);                // a random pivot
    [a[p], a[hi]] = [a[hi], a[p]];
    const pivot = a[hi];
    let store = lo;
    for (let i = lo; i < hi; i++) {                  // smaller values move to the left part
      if (a[i] < pivot) {
        [a[i], a[store]] = [a[store], a[i]];
        store++;
      }
    }
    [a[store], a[hi]] = [a[hi], a[store]];
    console.log(`pivot ${pivot} lands at index ${store}: [${a.slice(lo, hi + 1).join(", ")}]`);
    if (store === k - 1) return a[store];
    if (store < k - 1) lo = store + 1;               // keep only the side that holds the answer
    else hi = store - 1;
  }
}

const a = [7, 2, 9, 4, 1, 8, 3, 6, 5];
console.log(`4th smallest: ${quickselect(a.slice(), 4)}`);
console.log(`7th smallest: ${quickselect(a.slice(), 7)}`);
''', java=r'''
import java.util.*;

public class QuickSelect {
    static int seed = 3;

    static int rand(int n) {                         // a tiny repeatable random generator, so every language agrees
        seed = (seed * 75 + 74) % 65537;
        return seed % n;
    }

    static void swap(int[] a, int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }

    static int quickselect(int[] a, int k) {         // the k-th smallest value, k counted from 1
        int lo = 0, hi = a.length - 1;
        while (true) {
            int p = lo + rand(hi - lo + 1);          // a random pivot
            swap(a, p, hi);
            int pivot = a[hi], store = lo;
            for (int i = lo; i < hi; i++) {          // smaller values move to the left part
                if (a[i] < pivot) {
                    swap(a, i, store);
                    store++;
                }
            }
            swap(a, store, hi);
            System.out.println("pivot " + pivot + " lands at index " + store + ": " + Arrays.toString(Arrays.copyOfRange(a, lo, hi + 1)));
            if (store == k - 1) return a[store];
            if (store < k - 1) lo = store + 1;       // keep only the side that holds the answer
            else hi = store - 1;
        }
    }

    public static void main(String[] args) {
        int[] a = {7, 2, 9, 4, 1, 8, 3, 6, 5};
        System.out.println("4th smallest: " + quickselect(a.clone(), 4));
        System.out.println("7th smallest: " + quickselect(a.clone(), 7));
    }
}
''', ts=r'''
let seed = 3;

function rand(n: number): number {                   // a tiny repeatable random generator, so every language agrees
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

function quickselect(a: number[], k: number): number {   // the k-th smallest value, k counted from 1
  let lo = 0, hi = a.length - 1;
  while (true) {
    const p = lo + rand(hi - lo + 1);                // a random pivot
    [a[p], a[hi]] = [a[hi], a[p]];
    const pivot = a[hi];
    let store = lo;
    for (let i = lo; i < hi; i++) {                  // smaller values move to the left part
      if (a[i] < pivot) {
        [a[i], a[store]] = [a[store], a[i]];
        store++;
      }
    }
    [a[store], a[hi]] = [a[hi], a[store]];
    console.log(`pivot ${pivot} lands at index ${store}: [${a.slice(lo, hi + 1).join(", ")}]`);
    if (store === k - 1) return a[store];
    if (store < k - 1) lo = store + 1;               // keep only the side that holds the answer
    else hi = store - 1;
  }
}

const a = [7, 2, 9, 4, 1, 8, 3, 6, 5];
console.log(`4th smallest: ${quickselect(a.slice(), 4)}`);
console.log(`7th smallest: ${quickselect(a.slice(), 7)}`);
''')

t.code('reservoir', py=r'''
seed = 5


def rand(n):                                     # a tiny repeatable random generator, so every language agrees
    global seed
    seed = (seed * 75 + 74) % 65537
    return seed % n


def reservoir(stream, k):                        # keep k items from a stream of unknown length
    keep = stream[:k]
    for i in range(k, len(stream)):
        j = rand(i + 1)                          # a number from 0 to i
        if j < k:                                # item i stays with chance k / (i + 1)
            keep[j] = stream[i]
    return keep


print(f"3 kept from 1 to 10: {reservoir(list(range(1, 11)), 3)}")
counts = [0] * 5
for _ in range(5000):
    counts[reservoir([0, 1, 2, 3, 4], 1)[0]] += 1
print(f"5000 runs keeping 1 of 5: {counts}")
''', js=r'''
let seed = 5;

function rand(n) {                                   // a tiny repeatable random generator, so every language agrees
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

function reservoir(stream, k) {                      // keep k items from a stream of unknown length
  const keep = stream.slice(0, k);
  for (let i = k; i < stream.length; i++) {
    const j = rand(i + 1);                           // a number from 0 to i
    if (j < k) keep[j] = stream[i];                  // item i stays with chance k / (i + 1)
  }
  return keep;
}

console.log(`3 kept from 1 to 10: [${reservoir([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3).join(", ")}]`);
const counts = [0, 0, 0, 0, 0];
for (let r = 0; r < 5000; r++) counts[reservoir([0, 1, 2, 3, 4], 1)[0]]++;
console.log(`5000 runs keeping 1 of 5: [${counts.join(", ")}]`);
''', java=r'''
import java.util.*;

public class Reservoir {
    static int seed = 5;

    static int rand(int n) {                         // a tiny repeatable random generator, so every language agrees
        seed = (seed * 75 + 74) % 65537;
        return seed % n;
    }

    static int[] reservoir(int[] stream, int k) {    // keep k items from a stream of unknown length
        int[] keep = Arrays.copyOf(stream, k);
        for (int i = k; i < stream.length; i++) {
            int j = rand(i + 1);                     // a number from 0 to i
            if (j < k) keep[j] = stream[i];          // item i stays with chance k / (i + 1)
        }
        return keep;
    }

    public static void main(String[] args) {
        System.out.println("3 kept from 1 to 10: " + Arrays.toString(reservoir(new int[]{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, 3)));
        int[] counts = new int[5];
        for (int r = 0; r < 5000; r++) counts[reservoir(new int[]{0, 1, 2, 3, 4}, 1)[0]]++;
        System.out.println("5000 runs keeping 1 of 5: " + Arrays.toString(counts));
    }
}
''', ts=r'''
let seed = 5;

function rand(n: number): number {                   // a tiny repeatable random generator, so every language agrees
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

function reservoir(stream: number[], k: number): number[] {   // keep k items from a stream of unknown length
  const keep = stream.slice(0, k);
  for (let i = k; i < stream.length; i++) {
    const j = rand(i + 1);                           // a number from 0 to i
    if (j < k) keep[j] = stream[i];                  // item i stays with chance k / (i + 1)
  }
  return keep;
}

console.log(`3 kept from 1 to 10: [${reservoir([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3).join(", ")}]`);
const counts: number[] = [0, 0, 0, 0, 0];
for (let r = 0; r < 5000; r++) counts[reservoir([0, 1, 2, 3, 4], 1)[0]]++;
console.log(`5000 runs keeping 1 of 5: [${counts.join(", ")}]`);
''')

t.code('montecarlo', py=r'''
seed = 11


def rand(n):                                     # a tiny repeatable random generator, so every language agrees
    global seed
    seed = (seed * 75 + 74) % 65537
    return seed % n


N, R = 10000, 1000                               # 10000 random points in a 1000 by 1000 square
inside = 0
for _ in range(N):
    x, y = rand(R), rand(R)
    if x * x + y * y < R * R:                    # inside the quarter circle of radius R
        inside += 1
print(f"{inside} of {N} points fell inside the quarter circle")
print(f"pi is about 4 * {inside} / {N} = {4 * inside / N:.4f}")
''', js=r'''
let seed = 11;

function rand(n) {                                   // a tiny repeatable random generator, so every language agrees
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

const N = 10000, R = 1000;                           // 10000 random points in a 1000 by 1000 square
let inside = 0;
for (let i = 0; i < N; i++) {
  const x = rand(R), y = rand(R);
  if (x * x + y * y < R * R) inside++;               // inside the quarter circle of radius R
}
console.log(`${inside} of ${N} points fell inside the quarter circle`);
console.log(`pi is about 4 * ${inside} / ${N} = ${(4 * inside / N).toFixed(4)}`);
''', java=r'''
public class MonteCarlo {
    static int seed = 11;

    static int rand(int n) {                         // a tiny repeatable random generator, so every language agrees
        seed = (seed * 75 + 74) % 65537;
        return seed % n;
    }

    public static void main(String[] args) {
        int N = 10000, R = 1000;                     // 10000 random points in a 1000 by 1000 square
        int inside = 0;
        for (int i = 0; i < N; i++) {
            int x = rand(R), y = rand(R);
            if (x * x + y * y < R * R) inside++;     // inside the quarter circle of radius R
        }
        System.out.println(inside + " of " + N + " points fell inside the quarter circle");
        System.out.println("pi is about 4 * " + inside + " / " + N + " = " + String.format("%.4f", 4.0 * inside / N));
    }
}
''', ts=r'''
let seed = 11;

function rand(n: number): number {                   // a tiny repeatable random generator, so every language agrees
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

const N = 10000, R = 1000;                           // 10000 random points in a 1000 by 1000 square
let inside = 0;
for (let i = 0; i < N; i++) {
  const x = rand(R), y = rand(R);
  if (x * x + y * y < R * R) inside++;               // inside the quarter circle of radius R
}
console.log(`${inside} of ${N} points fell inside the quarter circle`);
console.log(`pi is about 4 * ${inside} / ${N} = ${(4 * inside / N).toFixed(4)}`);
''')

# ---------------------------------------------------------------- LeetCode programs
t.code('p_shuffle', py=r'''
seed = 2


def rand(n):                                     # repeatable random numbers, so the run is the same every time
    global seed
    seed = (seed * 75 + 74) % 65537
    return seed % n


class Solution:
    def __init__(self, nums):
        self.orig, self.a = nums[:], nums[:]

    def reset(self):
        self.a = self.orig[:]
        return self.a

    def shuffle(self):                           # Fisher-Yates: fill the end with a random unused value
        a = self.a
        for i in range(len(a) - 1, 0, -1):
            j = rand(i + 1)                      # any position from 0 to i
            a[i], a[j] = a[j], a[i]
        return a


s = Solution([1, 2, 3])
print(s.shuffle())
print(s.reset())
print(s.shuffle())
first = [0, 0, 0]
for _ in range(3000):
    first[s.shuffle()[0] - 1] += 1
print(f"which value came first in 3000 shuffles: {first}")
''', js=r'''
let seed = 2;

function rand(n) {                                   // repeatable random numbers, so the run is the same every time
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

class Solution {
  constructor(nums) {
    this.orig = nums.slice();
    this.a = nums.slice();
  }
  reset() {
    this.a = this.orig.slice();
    return this.a;
  }
  shuffle() {                                        // Fisher-Yates: fill the end with a random unused value
    const a = this.a;
    for (let i = a.length - 1; i > 0; i--) {
      const j = rand(i + 1);                         // any position from 0 to i
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }
}

const s = new Solution([1, 2, 3]);
console.log(`[${s.shuffle().join(", ")}]`);
console.log(`[${s.reset().join(", ")}]`);
console.log(`[${s.shuffle().join(", ")}]`);
const first = [0, 0, 0];
for (let r = 0; r < 3000; r++) first[s.shuffle()[0] - 1]++;
console.log(`which value came first in 3000 shuffles: [${first.join(", ")}]`);
''', java=r'''
import java.util.*;

public class ShuffleArray {
    static int seed = 2;

    static int rand(int n) {                         // repeatable random numbers, so the run is the same every time
        seed = (seed * 75 + 74) % 65537;
        return seed % n;
    }

    int[] orig, a;

    ShuffleArray(int[] nums) {
        orig = nums.clone();
        a = nums.clone();
    }

    int[] reset() {
        a = orig.clone();
        return a;
    }

    int[] shuffle() {                                // Fisher-Yates: fill the end with a random unused value
        for (int i = a.length - 1; i > 0; i--) {
            int j = rand(i + 1);                     // any position from 0 to i
            int t = a[i]; a[i] = a[j]; a[j] = t;
        }
        return a;
    }

    public static void main(String[] args) {
        ShuffleArray s = new ShuffleArray(new int[]{1, 2, 3});
        System.out.println(Arrays.toString(s.shuffle()));
        System.out.println(Arrays.toString(s.reset()));
        System.out.println(Arrays.toString(s.shuffle()));
        int[] first = new int[3];
        for (int r = 0; r < 3000; r++) first[s.shuffle()[0] - 1]++;
        System.out.println("which value came first in 3000 shuffles: " + Arrays.toString(first));
    }
}
''', ts=r'''
let seed = 2;

function rand(n: number): number {                   // repeatable random numbers, so the run is the same every time
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

class Solution {
  orig: number[];
  a: number[];
  constructor(nums: number[]) {
    this.orig = nums.slice();
    this.a = nums.slice();
  }
  reset(): number[] {
    this.a = this.orig.slice();
    return this.a;
  }
  shuffle(): number[] {                              // Fisher-Yates: fill the end with a random unused value
    const a = this.a;
    for (let i = a.length - 1; i > 0; i--) {
      const j = rand(i + 1);                         // any position from 0 to i
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }
}

const s = new Solution([1, 2, 3]);
console.log(`[${s.shuffle().join(", ")}]`);
console.log(`[${s.reset().join(", ")}]`);
console.log(`[${s.shuffle().join(", ")}]`);
const first: number[] = [0, 0, 0];
for (let r = 0; r < 3000; r++) first[s.shuffle()[0] - 1]++;
console.log(`which value came first in 3000 shuffles: [${first.join(", ")}]`);
''')

t.code('p_pickindex', py=r'''
seed = 4


def rand(n):                                     # repeatable random numbers, so the run is the same every time
    global seed
    seed = (seed * 75 + 74) % 65537
    return seed % n


class Solution:
    def __init__(self, nums):
        self.nums = nums

    def pick(self, target):                      # reservoir sampling over the matches
        chosen, seen = -1, 0
        for i, x in enumerate(self.nums):
            if x == target:
                seen += 1
                if rand(seen) == 0:              # keep this match with chance 1 / seen
                    chosen = i
        return chosen


s = Solution([1, 2, 3, 3, 3])
counts = [0, 0, 0]
for _ in range(3000):
    counts[s.pick(3) - 2] += 1
print(f"pick(3) 3000 times, indexes 2, 3, 4: {counts}")
print(f"pick(1): {s.pick(1)}")
''', js=r'''
let seed = 4;

function rand(n) {                                   // repeatable random numbers, so the run is the same every time
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

class Solution {
  constructor(nums) {
    this.nums = nums;
  }
  pick(target) {                                     // reservoir sampling over the matches
    let chosen = -1, seen = 0;
    this.nums.forEach((x, i) => {
      if (x === target) {
        seen++;
        if (rand(seen) === 0) chosen = i;            // keep this match with chance 1 / seen
      }
    });
    return chosen;
  }
}

const s = new Solution([1, 2, 3, 3, 3]);
const counts = [0, 0, 0];
for (let r = 0; r < 3000; r++) counts[s.pick(3) - 2]++;
console.log(`pick(3) 3000 times, indexes 2, 3, 4: [${counts.join(", ")}]`);
console.log(`pick(1): ${s.pick(1)}`);
''', java=r'''
import java.util.*;

public class RandomPickIndex {
    static int seed = 4;

    static int rand(int n) {                         // repeatable random numbers, so the run is the same every time
        seed = (seed * 75 + 74) % 65537;
        return seed % n;
    }

    int[] nums;

    RandomPickIndex(int[] nums) {
        this.nums = nums;
    }

    int pick(int target) {                           // reservoir sampling over the matches
        int chosen = -1, seen = 0;
        for (int i = 0; i < nums.length; i++) {
            if (nums[i] == target) {
                seen++;
                if (rand(seen) == 0) chosen = i;     // keep this match with chance 1 / seen
            }
        }
        return chosen;
    }

    public static void main(String[] args) {
        RandomPickIndex s = new RandomPickIndex(new int[]{1, 2, 3, 3, 3});
        int[] counts = new int[3];
        for (int r = 0; r < 3000; r++) counts[s.pick(3) - 2]++;
        System.out.println("pick(3) 3000 times, indexes 2, 3, 4: " + Arrays.toString(counts));
        System.out.println("pick(1): " + s.pick(1));
    }
}
''', ts=r'''
let seed = 4;

function rand(n: number): number {                   // repeatable random numbers, so the run is the same every time
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

class Solution {
  nums: number[];
  constructor(nums: number[]) {
    this.nums = nums;
  }
  pick(target: number): number {                     // reservoir sampling over the matches
    let chosen = -1, seen = 0;
    this.nums.forEach((x, i) => {
      if (x === target) {
        seen++;
        if (rand(seen) === 0) chosen = i;            // keep this match with chance 1 / seen
      }
    });
    return chosen;
  }
}

const s = new Solution([1, 2, 3, 3, 3]);
const counts: number[] = [0, 0, 0];
for (let r = 0; r < 3000; r++) counts[s.pick(3) - 2]++;
console.log(`pick(3) 3000 times, indexes 2, 3, 4: [${counts.join(", ")}]`);
console.log(`pick(1): ${s.pick(1)}`);
''')

t.code('p_weight', py=r'''
seed = 6


def rand(n):                                     # repeatable random numbers, so the run is the same every time
    global seed
    seed = (seed * 75 + 74) % 65537
    return seed % n


class Solution:
    def __init__(self, w):
        self.pre, total = [], 0
        for x in w:                              # running totals: index i owns the numbers up to pre[i]
            total += x
            self.pre.append(total)

    def pick_index(self):
        r = rand(self.pre[-1]) + 1               # a number from 1 to the total weight
        lo, hi = 0, len(self.pre) - 1
        while lo < hi:                           # the first running total that reaches r
            mid = (lo + hi) // 2
            if self.pre[mid] < r:
                lo = mid + 1
            else:
                hi = mid
        return lo


for w, runs in (([1, 3], 4000), ([2, 5, 3], 5000)):
    s = Solution(w)
    counts = [0] * len(w)
    for _ in range(runs):
        counts[s.pick_index()] += 1
    print(f"weights {w}, {runs} picks: {counts}")
''', js=r'''
let seed = 6;

function rand(n) {                                   // repeatable random numbers, so the run is the same every time
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

class Solution {
  constructor(w) {
    this.pre = [];
    let total = 0;
    for (const x of w) {                             // running totals: index i owns the numbers up to pre[i]
      total += x;
      this.pre.push(total);
    }
  }
  pickIndex() {
    const r = rand(this.pre[this.pre.length - 1]) + 1;   // a number from 1 to the total weight
    let lo = 0, hi = this.pre.length - 1;
    while (lo < hi) {                                // the first running total that reaches r
      const mid = (lo + hi) >> 1;
      if (this.pre[mid] < r) lo = mid + 1;
      else hi = mid;
    }
    return lo;
  }
}

for (const [w, runs] of [[[1, 3], 4000], [[2, 5, 3], 5000]]) {
  const s = new Solution(w);
  const counts = new Array(w.length).fill(0);
  for (let r = 0; r < runs; r++) counts[s.pickIndex()]++;
  console.log(`weights [${w.join(", ")}], ${runs} picks: [${counts.join(", ")}]`);
}
''', java=r'''
import java.util.*;

public class RandomPickWeight {
    static int seed = 6;

    static int rand(int n) {                         // repeatable random numbers, so the run is the same every time
        seed = (seed * 75 + 74) % 65537;
        return seed % n;
    }

    int[] pre;

    RandomPickWeight(int[] w) {
        pre = new int[w.length];
        int total = 0;
        for (int i = 0; i < w.length; i++) {         // running totals: index i owns the numbers up to pre[i]
            total += w[i];
            pre[i] = total;
        }
    }

    int pickIndex() {
        int r = rand(pre[pre.length - 1]) + 1;       // a number from 1 to the total weight
        int lo = 0, hi = pre.length - 1;
        while (lo < hi) {                            // the first running total that reaches r
            int mid = (lo + hi) / 2;
            if (pre[mid] < r) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }

    public static void main(String[] args) {
        int[][] ws = {{1, 3}, {2, 5, 3}};
        int[] runs = {4000, 5000};
        for (int t = 0; t < 2; t++) {
            RandomPickWeight s = new RandomPickWeight(ws[t]);
            int[] counts = new int[ws[t].length];
            for (int r = 0; r < runs[t]; r++) counts[s.pickIndex()]++;
            System.out.println("weights " + Arrays.toString(ws[t]) + ", " + runs[t] + " picks: " + Arrays.toString(counts));
        }
    }
}
''', ts=r'''
let seed = 6;

function rand(n: number): number {                   // repeatable random numbers, so the run is the same every time
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

class Solution {
  pre: number[];
  constructor(w: number[]) {
    this.pre = [];
    let total = 0;
    for (const x of w) {                             // running totals: index i owns the numbers up to pre[i]
      total += x;
      this.pre.push(total);
    }
  }
  pickIndex(): number {
    const r = rand(this.pre[this.pre.length - 1]) + 1;   // a number from 1 to the total weight
    let lo = 0, hi = this.pre.length - 1;
    while (lo < hi) {                                // the first running total that reaches r
      const mid = (lo + hi) >> 1;
      if (this.pre[mid] < r) lo = mid + 1;
      else hi = mid;
    }
    return lo;
  }
}

const tests: [number[], number][] = [[[1, 3], 4000], [[2, 5, 3], 5000]];
for (const [w, runs] of tests) {
  const s = new Solution(w);
  const counts: number[] = new Array(w.length).fill(0);
  for (let r = 0; r < runs; r++) counts[s.pickIndex()]++;
  console.log(`weights [${w.join(", ")}], ${runs} picks: [${counts.join(", ")}]`);
}
''')

t.code('p_rand10', py=r'''
seed = 8
calls = 0


def rand7():                                     # the only random tool allowed: 1 to 7, each equally likely
    global seed, calls
    calls += 1
    seed = (seed * 75 + 74) % 65537
    return seed % 7 + 1


def rand10():
    while True:
        v = (rand7() - 1) * 7 + rand7()          # 1 to 49, each equally likely
        if v <= 40:                              # 40 values split evenly into 10 groups of 4
            return 1 + (v - 1) % 10
                                                 # 41 to 49 would make some answers more likely, so roll again


counts = [0] * 10
for _ in range(10000):
    counts[rand10() - 1] += 1
print(f"10000 calls, values 1 to 10: {counts}")
print(f"rand7 was called {calls} times")
''', js=r'''
let seed = 8, calls = 0;

function rand7() {                                   // the only random tool allowed: 1 to 7, each equally likely
  calls++;
  seed = (seed * 75 + 74) % 65537;
  return seed % 7 + 1;
}

function rand10() {
  while (true) {
    const v = (rand7() - 1) * 7 + rand7();           // 1 to 49, each equally likely
    if (v <= 40) return 1 + (v - 1) % 10;            // 40 values split evenly into 10 groups of 4
  }                                                  // 41 to 49 would make some answers more likely, so roll again
}

const counts = new Array(10).fill(0);
for (let r = 0; r < 10000; r++) counts[rand10() - 1]++;
console.log(`10000 calls, values 1 to 10: [${counts.join(", ")}]`);
console.log(`rand7 was called ${calls} times`);
''', java=r'''
import java.util.*;

public class Rand10 {
    static int seed = 8, calls = 0;

    static int rand7() {                             // the only random tool allowed: 1 to 7, each equally likely
        calls++;
        seed = (seed * 75 + 74) % 65537;
        return seed % 7 + 1;
    }

    static int rand10() {
        while (true) {
            int v = (rand7() - 1) * 7 + rand7();     // 1 to 49, each equally likely
            if (v <= 40) return 1 + (v - 1) % 10;    // 40 values split evenly into 10 groups of 4
        }                                            // 41 to 49 would make some answers more likely, so roll again
    }

    public static void main(String[] args) {
        int[] counts = new int[10];
        for (int r = 0; r < 10000; r++) counts[rand10() - 1]++;
        System.out.println("10000 calls, values 1 to 10: " + Arrays.toString(counts));
        System.out.println("rand7 was called " + calls + " times");
    }
}
''', ts=r'''
let seed = 8, calls = 0;

function rand7(): number {                           // the only random tool allowed: 1 to 7, each equally likely
  calls++;
  seed = (seed * 75 + 74) % 65537;
  return seed % 7 + 1;
}

function rand10(): number {
  while (true) {
    const v = (rand7() - 1) * 7 + rand7();           // 1 to 49, each equally likely
    if (v <= 40) return 1 + (v - 1) % 10;            // 40 values split evenly into 10 groups of 4
  }                                                  // 41 to 49 would make some answers more likely, so roll again
}

const counts: number[] = new Array(10).fill(0);
for (let r = 0; r < 10000; r++) counts[rand10() - 1]++;
console.log(`10000 calls, values 1 to 10: [${counts.join(", ")}]`);
console.log(`rand7 was called ${calls} times`);
''')

t.code('p_kth', py=r'''
seed = 9


def rand(n):                                     # repeatable random numbers, so the run is the same every time
    global seed
    seed = (seed * 75 + 74) % 65537
    return seed % n


def find_kth_largest(nums, k):
    a, want = nums[:], len(nums) - k             # the k-th largest sits at index n - k once sorted
    lo, hi = 0, len(a) - 1
    while True:
        p = lo + rand(hi - lo + 1)
        a[p], a[hi] = a[hi], a[p]
        store = lo
        for i in range(lo, hi):                  # partition around a random pivot
            if a[i] < a[hi]:
                a[i], a[store] = a[store], a[i]
                store += 1
        a[store], a[hi] = a[hi], a[store]
        if store == want:
            return a[store]
        if store < want:
            lo = store + 1
        else:
            hi = store - 1


print(find_kth_largest([3, 2, 1, 5, 6, 4], 2))
print(find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))
print(find_kth_largest([7], 1))
''', js=r'''
let seed = 9;

function rand(n) {                                   // repeatable random numbers, so the run is the same every time
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

function findKthLargest(nums, k) {
  const a = nums.slice(), want = nums.length - k;    // the k-th largest sits at index n - k once sorted
  let lo = 0, hi = a.length - 1;
  while (true) {
    const p = lo + rand(hi - lo + 1);
    [a[p], a[hi]] = [a[hi], a[p]];
    let store = lo;
    for (let i = lo; i < hi; i++) {                  // partition around a random pivot
      if (a[i] < a[hi]) {
        [a[i], a[store]] = [a[store], a[i]];
        store++;
      }
    }
    [a[store], a[hi]] = [a[hi], a[store]];
    if (store === want) return a[store];
    if (store < want) lo = store + 1;
    else hi = store - 1;
  }
}

console.log(findKthLargest([3, 2, 1, 5, 6, 4], 2));
console.log(findKthLargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4));
console.log(findKthLargest([7], 1));
''', java=r'''
public class KthLargest {
    static int seed = 9;

    static int rand(int n) {                         // repeatable random numbers, so the run is the same every time
        seed = (seed * 75 + 74) % 65537;
        return seed % n;
    }

    static void swap(int[] a, int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }

    static int findKthLargest(int[] nums, int k) {
        int[] a = nums.clone();
        int want = nums.length - k;                  // the k-th largest sits at index n - k once sorted
        int lo = 0, hi = a.length - 1;
        while (true) {
            int p = lo + rand(hi - lo + 1);
            swap(a, p, hi);
            int store = lo;
            for (int i = lo; i < hi; i++) {          // partition around a random pivot
                if (a[i] < a[hi]) {
                    swap(a, i, store);
                    store++;
                }
            }
            swap(a, store, hi);
            if (store == want) return a[store];
            if (store < want) lo = store + 1;
            else hi = store - 1;
        }
    }

    public static void main(String[] args) {
        System.out.println(findKthLargest(new int[]{3, 2, 1, 5, 6, 4}, 2));
        System.out.println(findKthLargest(new int[]{3, 2, 3, 1, 2, 4, 5, 5, 6}, 4));
        System.out.println(findKthLargest(new int[]{7}, 1));
    }
}
''', ts=r'''
let seed = 9;

function rand(n: number): number {                   // repeatable random numbers, so the run is the same every time
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

function findKthLargest(nums: number[], k: number): number {
  const a = nums.slice(), want = nums.length - k;    // the k-th largest sits at index n - k once sorted
  let lo = 0, hi = a.length - 1;
  while (true) {
    const p = lo + rand(hi - lo + 1);
    [a[p], a[hi]] = [a[hi], a[p]];
    let store = lo;
    for (let i = lo; i < hi; i++) {                  // partition around a random pivot
      if (a[i] < a[hi]) {
        [a[i], a[store]] = [a[store], a[i]];
        store++;
      }
    }
    [a[store], a[hi]] = [a[hi], a[store]];
    if (store === want) return a[store];
    if (store < want) lo = store + 1;
    else hi = store - 1;
  }
}

console.log(findKthLargest([3, 2, 1, 5, 6, 4], 2));
console.log(findKthLargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4));
console.log(findKthLargest([7], 1));
''')

t.code('p_blacklist', py=r'''
seed = 10


def rand(n):                                     # repeatable random numbers, so the run is the same every time
    global seed
    seed = (seed * 75 + 74) % 65537
    return seed % n


class Solution:
    def __init__(self, n, blacklist):
        self.m = n - len(blacklist)              # draw only from 0 to m - 1
        bad, self.remap = set(blacklist), {}
        w = self.m
        for b in sorted(blacklist):
            if b < self.m:                       # a blocked number in the low range points to a free high one
                while w in bad:
                    w += 1
                self.remap[b] = w
                w += 1

    def pick(self):
        r = rand(self.m)
        return self.remap.get(r, r)


s = Solution(7, [2, 3, 5])
print(f"remapped: {sorted(s.remap.items())}")
counts = [0] * 7
for _ in range(4000):
    counts[s.pick()] += 1
print(f"4000 picks, values 0 to 6: {counts}")
''', js=r'''
let seed = 10;

function rand(n) {                                   // repeatable random numbers, so the run is the same every time
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

class Solution {
  constructor(n, blacklist) {
    this.m = n - blacklist.length;                   // draw only from 0 to m - 1
    this.remap = new Map();
    const bad = new Set(blacklist);
    let w = this.m;
    for (const b of blacklist.slice().sort((x, y) => x - y)) {
      if (b < this.m) {                              // a blocked number in the low range points to a free high one
        while (bad.has(w)) w++;
        this.remap.set(b, w);
        w++;
      }
    }
  }
  pick() {
    const r = rand(this.m);
    return this.remap.has(r) ? this.remap.get(r) : r;
  }
}

const s = new Solution(7, [2, 3, 5]);
console.log(`remapped: [${[...s.remap].map(([b, w]) => `(${b}, ${w})`).join(", ")}]`);
const counts = new Array(7).fill(0);
for (let r = 0; r < 4000; r++) counts[s.pick()]++;
console.log(`4000 picks, values 0 to 6: [${counts.join(", ")}]`);
''', java=r'''
import java.util.*;

public class PickBlacklist {
    static int seed = 10;

    static int rand(int n) {                         // repeatable random numbers, so the run is the same every time
        seed = (seed * 75 + 74) % 65537;
        return seed % n;
    }

    int m;
    TreeMap<Integer, Integer> remap = new TreeMap<>();

    PickBlacklist(int n, int[] blacklist) {
        m = n - blacklist.length;                    // draw only from 0 to m - 1
        Set<Integer> bad = new HashSet<>();
        for (int b : blacklist) bad.add(b);
        int[] sorted = blacklist.clone();
        Arrays.sort(sorted);
        int w = m;
        for (int b : sorted) {
            if (b < m) {                             // a blocked number in the low range points to a free high one
                while (bad.contains(w)) w++;
                remap.put(b, w);
                w++;
            }
        }
    }

    int pick() {
        int r = rand(m);
        return remap.getOrDefault(r, r);
    }

    public static void main(String[] args) {
        PickBlacklist s = new PickBlacklist(7, new int[]{2, 3, 5});
        StringJoiner sj = new StringJoiner(", ", "[", "]");
        for (Map.Entry<Integer, Integer> e : s.remap.entrySet()) sj.add("(" + e.getKey() + ", " + e.getValue() + ")");
        System.out.println("remapped: " + sj);
        int[] counts = new int[7];
        for (int r = 0; r < 4000; r++) counts[s.pick()]++;
        System.out.println("4000 picks, values 0 to 6: " + Arrays.toString(counts));
    }
}
''', ts=r'''
let seed = 10;

function rand(n: number): number {                   // repeatable random numbers, so the run is the same every time
  seed = (seed * 75 + 74) % 65537;
  return seed % n;
}

class Solution {
  m: number;
  remap: Map<number, number>;
  constructor(n: number, blacklist: number[]) {
    this.m = n - blacklist.length;                   // draw only from 0 to m - 1
    this.remap = new Map();
    const bad = new Set(blacklist);
    let w = this.m;
    for (const b of blacklist.slice().sort((x, y) => x - y)) {
      if (b < this.m) {                              // a blocked number in the low range points to a free high one
        while (bad.has(w)) w++;
        this.remap.set(b, w);
        w++;
      }
    }
  }
  pick(): number {
    const r = rand(this.m);
    return this.remap.get(r) ?? r;
  }
}

const s = new Solution(7, [2, 3, 5]);
console.log(`remapped: [${[...s.remap].map(([b, w]) => `(${b}, ${w})`).join(", ")}]`);
const counts: number[] = new Array(7).fill(0);
for (let r = 0; r < 4000; r++) counts[s.pick()]++;
console.log(`4000 picks, values 0 to 6: [${counts.join(", ")}]`);
''')

t.code('p_paths3', py=r'''
def unique_paths_iii(grid):
    rows, cols = len(grid), len(grid[0])
    todo, sr, sc = 1, 0, 0                       # cells to step on, counting the start
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                todo += 1
            elif grid[r][c] == 1:
                sr, sc = r, c

    def walk(r, c, left):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] < 0:
            return 0                             # off the grid, a wall, or already on this path
        if grid[r][c] == 2:
            return 1 if left == 0 else 0         # the end only counts once every cell was used
        keep, grid[r][c] = grid[r][c], -2        # mark the cell as part of the path
        total = walk(r + 1, c, left - 1) + walk(r - 1, c, left - 1) + walk(r, c + 1, left - 1) + walk(r, c - 1, left - 1)
        grid[r][c] = keep                        # step back and free the cell
        return total

    return walk(sr, sc, todo)


print(unique_paths_iii([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 2, -1]]))
print(unique_paths_iii([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]]))
print(unique_paths_iii([[0, 1], [2, 0]]))
''', js=r'''
function uniquePathsIII(grid) {
  const rows = grid.length, cols = grid[0].length;
  let todo = 1, sr = 0, sc = 0;                      // cells to step on, counting the start
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (grid[r][c] === 0) todo++;
      else if (grid[r][c] === 1) { sr = r; sc = c; }
    }
  }
  function walk(r, c, left) {
    if (r < 0 || r >= rows || c < 0 || c >= cols || grid[r][c] < 0) return 0;   // off the grid, a wall, or already on this path
    if (grid[r][c] === 2) return left === 0 ? 1 : 0;  // the end only counts once every cell was used
    const keep = grid[r][c];
    grid[r][c] = -2;                                 // mark the cell as part of the path
    const total = walk(r + 1, c, left - 1) + walk(r - 1, c, left - 1) + walk(r, c + 1, left - 1) + walk(r, c - 1, left - 1);
    grid[r][c] = keep;                               // step back and free the cell
    return total;
  }
  return walk(sr, sc, todo);
}

console.log(uniquePathsIII([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 2, -1]]));
console.log(uniquePathsIII([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]]));
console.log(uniquePathsIII([[0, 1], [2, 0]]));
''', java=r'''
public class UniquePaths3 {
    static int[][] grid;
    static int rows, cols;

    static int walk(int r, int c, int left) {
        if (r < 0 || r >= rows || c < 0 || c >= cols || grid[r][c] < 0) return 0;   // off the grid, a wall, or already on this path
        if (grid[r][c] == 2) return left == 0 ? 1 : 0;   // the end only counts once every cell was used
        int keep = grid[r][c];
        grid[r][c] = -2;                             // mark the cell as part of the path
        int total = walk(r + 1, c, left - 1) + walk(r - 1, c, left - 1) + walk(r, c + 1, left - 1) + walk(r, c - 1, left - 1);
        grid[r][c] = keep;                           // step back and free the cell
        return total;
    }

    static int uniquePathsIII(int[][] g) {
        grid = g;
        rows = g.length;
        cols = g[0].length;
        int todo = 1, sr = 0, sc = 0;                // cells to step on, counting the start
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (g[r][c] == 0) todo++;
                else if (g[r][c] == 1) { sr = r; sc = c; }
            }
        }
        return walk(sr, sc, todo);
    }

    public static void main(String[] args) {
        System.out.println(uniquePathsIII(new int[][]{{1, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 2, -1}}));
        System.out.println(uniquePathsIII(new int[][]{{1, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 2}}));
        System.out.println(uniquePathsIII(new int[][]{{0, 1}, {2, 0}}));
    }
}
''', ts=r'''
function uniquePathsIII(grid: number[][]): number {
  const rows = grid.length, cols = grid[0].length;
  let todo = 1, sr = 0, sc = 0;                      // cells to step on, counting the start
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (grid[r][c] === 0) todo++;
      else if (grid[r][c] === 1) { sr = r; sc = c; }
    }
  }
  function walk(r: number, c: number, left: number): number {
    if (r < 0 || r >= rows || c < 0 || c >= cols || grid[r][c] < 0) return 0;   // off the grid, a wall, or already on this path
    if (grid[r][c] === 2) return left === 0 ? 1 : 0;  // the end only counts once every cell was used
    const keep = grid[r][c];
    grid[r][c] = -2;                                 // mark the cell as part of the path
    const total = walk(r + 1, c, left - 1) + walk(r - 1, c, left - 1) + walk(r, c + 1, left - 1) + walk(r, c - 1, left - 1);
    grid[r][c] = keep;                               // step back and free the cell
    return total;
  }
  return walk(sr, sc, todo);
}

console.log(uniquePathsIII([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 2, -1]]));
console.log(uniquePathsIII([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]]));
console.log(uniquePathsIII([[0, 1], [2, 0]]));
''')

t.code('p_allnodes', py=r'''
from collections import deque


def shortest_path_length(graph):
    n = len(graph)
    full = (1 << n) - 1                          # the mask with every node visited
    seen = [[False] * n for _ in range(1 << n)]  # seen[mask][v]: reached v having visited mask
    q = deque()
    for v in range(n):                           # start from every node at once
        seen[1 << v][v] = True
        q.append((v, 1 << v, 0))
    while q:
        v, mask, d = q.popleft()
        if mask == full:
            return d
        for u in graph[v]:
            nm = mask | 1 << u
            if not seen[nm][u]:
                seen[nm][u] = True
                q.append((u, nm, d + 1))
    return -1


print(shortest_path_length([[1, 2, 3], [0], [0], [0]]))
print(shortest_path_length([[1], [0, 2, 4], [1, 3, 4], [2], [1, 2]]))
print(shortest_path_length([[1], [0]]))
''', js=r'''
function shortestPathLength(graph) {
  const n = graph.length, full = (1 << n) - 1;       // the mask with every node visited
  const seen = Array.from({ length: 1 << n }, () => new Array(n).fill(false));   // seen[mask][v]: reached v having visited mask
  const q = [];
  for (let v = 0; v < n; v++) {                      // start from every node at once
    seen[1 << v][v] = true;
    q.push([v, 1 << v, 0]);
  }
  for (let head = 0; head < q.length; head++) {
    const [v, mask, d] = q[head];
    if (mask === full) return d;
    for (const u of graph[v]) {
      const nm = mask | (1 << u);
      if (!seen[nm][u]) {
        seen[nm][u] = true;
        q.push([u, nm, d + 1]);
      }
    }
  }
  return -1;
}

console.log(shortestPathLength([[1, 2, 3], [0], [0], [0]]));
console.log(shortestPathLength([[1], [0, 2, 4], [1, 3, 4], [2], [1, 2]]));
console.log(shortestPathLength([[1], [0]]));
''', java=r'''
import java.util.*;

public class VisitAllNodes {
    static int shortestPathLength(int[][] graph) {
        int n = graph.length, full = (1 << n) - 1;   // the mask with every node visited
        boolean[][] seen = new boolean[1 << n][n];   // seen[mask][v]: reached v having visited mask
        ArrayDeque<int[]> q = new ArrayDeque<>();
        for (int v = 0; v < n; v++) {                // start from every node at once
            seen[1 << v][v] = true;
            q.add(new int[]{v, 1 << v, 0});
        }
        while (!q.isEmpty()) {
            int[] cur = q.poll();
            int v = cur[0], mask = cur[1], d = cur[2];
            if (mask == full) return d;
            for (int u : graph[v]) {
                int nm = mask | 1 << u;
                if (!seen[nm][u]) {
                    seen[nm][u] = true;
                    q.add(new int[]{u, nm, d + 1});
                }
            }
        }
        return -1;
    }

    public static void main(String[] args) {
        System.out.println(shortestPathLength(new int[][]{{1, 2, 3}, {0}, {0}, {0}}));
        System.out.println(shortestPathLength(new int[][]{{1}, {0, 2, 4}, {1, 3, 4}, {2}, {1, 2}}));
        System.out.println(shortestPathLength(new int[][]{{1}, {0}}));
    }
}
''', ts=r'''
function shortestPathLength(graph: number[][]): number {
  const n = graph.length, full = (1 << n) - 1;       // the mask with every node visited
  const seen: boolean[][] = Array.from({ length: 1 << n }, () => new Array(n).fill(false));   // seen[mask][v]: reached v having visited mask
  const q: number[][] = [];
  for (let v = 0; v < n; v++) {                      // start from every node at once
    seen[1 << v][v] = true;
    q.push([v, 1 << v, 0]);
  }
  for (let head = 0; head < q.length; head++) {
    const [v, mask, d] = q[head];
    if (mask === full) return d;
    for (const u of graph[v]) {
      const nm = mask | (1 << u);
      if (!seen[nm][u]) {
        seen[nm][u] = true;
        q.push([u, nm, d + 1]);
      }
    }
  }
  return -1;
}

console.log(shortestPathLength([[1, 2, 3], [0], [0], [0]]));
console.log(shortestPathLength([[1], [0, 2, 4], [1, 3, 4], [2], [1, 2]]));
console.log(shortestPathLength([[1], [0]]));
''')

# ---------------------------------------------------------------- practice
t.leet(384, 'e', 'p_shuffle',
       statement='<p>Build a class over a list of numbers. shuffle returns a random order where every order is equally likely, and reset returns the original list.</p>',
       example='nums = [1, 2, 3]\nshuffle()  →  any order, such as [2, 1, 3]\nreset()    →  [1, 2, 3]',
       hint='Fill the positions from the back, each with a random value that is not placed yet.',
       approach='<p>This is the Fisher-Yates shuffle. For i from the last index down to 1, pick j at random from 0 to i and swap positions i and j. Each of the n! orders comes out with the same chance, 1 ÷ n!. Swapping with any position from 0 to n − 1 at every step looks similar, but it gives some orders more often than others.</p>',
       time='O(n) per shuffle', space='O(n)')
t.leet(398, 'e', 'p_pickindex',
       statement='<p>Given a list that may hold repeated numbers, pick(target) returns a random index where target appears. Every such index must be equally likely.</p>',
       example='nums = [1, 2, 3, 3, 3]\npick(3)  →  2, 3 or 4, each 1 time in 3\npick(1)  →  0',
       hint='This is reservoir sampling with a reservoir of one.',
       approach='<p>Walk the list and count the matches. At the match number c, replace the chosen index with chance 1 ÷ c. The first match is kept for sure, the second replaces it half the time, and so on. In the end every match has the same chance, and no extra list is stored.</p>',
       time='O(n) per pick', space='O(1)')
t.leet(528, 'm', 'p_weight',
       statement='<p>Given positive weights w, pickIndex returns index i with chance w[i] divided by the sum of all the weights.</p>',
       example='w = [1, 3]\npickIndex()  →  0 about 1 time in 4, 1 about 3 times in 4',
       hint='Lay the weights end to end on a number line and throw a dart.',
       approach='<p>Build running totals, so index i owns the numbers just above the previous total up to its own total. Draw a random number from 1 to the grand total and binary search for the first running total that reaches it. A weight of 3 owns three numbers, so it is picked three times as often as a weight of 1.</p>',
       time='O(n) to build, O(log n) per pick', space='O(n)')
t.leet(215, 'm', 'p_kth',
       statement='<p>Return the k-th largest value in a list, counting repeated values separately, without sorting the whole list.</p>',
       example='[3, 2, 1, 5, 6, 4], k = 2           →  5\n[3, 2, 3, 1, 2, 4, 5, 5, 6], k = 4  →  4',
       hint='The k-th largest sits at index n − k of the sorted list.',
       approach='<p>Run quickselect for index n − k. Pick a random pivot, split the range so smaller values are on its left, and continue only in the side that holds index n − k. With random pivots the expected work is O(n). A min heap of size k also works, in O(n log k).</p>',
       time='O(n) expected', space='O(n) for the copy')
t.leet(470, 'h', 'p_rand10',
       statement='<p>Using only rand7(), which returns 1 to 7 with equal chance, write rand10() that returns 1 to 10 with equal chance.</p>',
       example='rand10()  →  each of 1 to 10, about 1 time in 10',
       hint='Two rolls of rand7 give 49 equally likely results.',
       approach='<p>Two rolls give v = (first − 1) × 7 + second, which is 1 to 49, all equally likely. Keep v only when it is at most 40, and return 1 + (v − 1) mod 10, since 40 splits evenly into 10 groups of 4. For 41 to 49, roll again. A pair is kept 40 times in 49, so on average it takes about 2.45 calls of rand7. The program counted 24756 calls for 10000 numbers.</p>',
       time='O(1) expected', space='O(1)')
t.leet(710, 'h', 'p_blacklist',
       statement='<p>Given n and a blacklist, pick() returns a random number from 0 to n − 1 that is not on the blacklist. Every allowed number must be equally likely, and rand should be called as few times as possible.</p>',
       example='n = 7, blacklist = [2, 3, 5]\npick()  →  0, 1, 4 or 6, each 1 time in 4',
       hint='Draw from the first n − b numbers only, and send each blocked one among them to a free number above.',
       approach='<p>Let m = n − b, where b is the size of the blacklist. Draw r from 0 to m − 1. Before that, give every blacklisted number below m a partner: a free number at m or above. If r is blocked, return its partner instead. There are exactly as many blocked numbers below m as free numbers above, so every allowed number is hit once. Each pick uses one random call.</p>',
       time='O(b log b) to build, O(1) per pick', space='O(b)')
t.leet(980, 'x', 'p_paths3', title='Unique Paths III', url='https://leetcode.com/problems/unique-paths-iii/', diff='Hard',
       statement='<p>A grid has a start 1, an end 2, empty squares 0 and walls −1. Count the walks from start to end that step on every non wall square exactly once, moving up, down, left or right.</p>',
       example='[[1,0,0,0],[0,0,0,0],[0,0,2,−1]]  →  2\n[[1,0,0,0],[0,0,0,0],[0,0,0,2]]   →  4\n[[0,1],[2,0]]                     →  0',
       hint='This is a Hamiltonian path count, so no fast method is known. The grid is small: backtrack.',
       approach='<p>Count the squares that must be visited. Walk from the start, marking each square as used, and try all four directions. Reaching the end only counts when no squares are left. Unmark the square when stepping back. Finding a path through every square is NP-complete in general, which is why the grid in this problem is at most 20 squares.</p>',
       time='exponential in the number of squares', space='O(rows × cols)')
t.leet(847, 'x', 'p_allnodes', title='Shortest Path Visiting All Nodes', url='https://leetcode.com/problems/shortest-path-visiting-all-nodes/', diff='Hard',
       statement='<p>Given a connected graph with at most 12 nodes, return the length of the shortest walk that visits every node. You may start and stop anywhere and use edges again.</p>',
       example='[[1,2,3],[0],[0],[0]]            →  4\n[[1],[0,2,4],[1,3,4],[2],[1,2]]  →  4',
       hint='A state is where you stand plus the set of nodes visited so far, written as a bit mask.',
       approach='<p>Run breadth first search over states (node, mask), starting from every node at once with only that node in its mask. The first state whose mask holds every node gives the answer. There are n × 2<sup>n</sup> states, which is fine for 12 nodes and hopeless for 60. That growth is typical of NP-hard problems, as in the TSP lesson of Dynamic programming 2.</p>',
       time='O(n² × 2ⁿ)', space='O(n × 2ⁿ)')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='p-vs-np', emoji='🔐', title='P and NP: easy to check, hard to find', html='''
<p>Some problems have fast methods, like sorting or shortest paths. Computer scientists call this class <b>P</b>: problems solvable in polynomial time, such as n² or n³ steps. Other problems are only known to be fast to <b>check</b>. Given a proposed answer, you can confirm it quickly, but nobody knows how to find one quickly. That class is <b>NP</b>. Subset sum is a classic example: does some group of the numbers add up to the target?</p>
<div class="viz" data-viz="pk" data-pk="subset"></div>
<div class="c3" data-k="subsetsum" data-label="Subset sum: try every subset, then check one answer"></div>
<div class="tw"><table class="jt"><tr><th>Name</th><th>Meaning</th></tr>
<tr><td>P</td><td>Can be solved in polynomial time</td></tr>
<tr><td>NP</td><td>A proposed answer can be checked in polynomial time</td></tr>
<tr><td>NP-hard</td><td>At least as hard as every problem in NP</td></tr>
<tr><td>NP-complete</td><td>In NP and NP-hard, such as SAT, subset sum, vertex cover and Hamiltonian path</td></tr></table></div>
<div class="tip">Whether P equals NP is one of the seven Millennium Prize Problems of the Clay Mathematics Institute, with a prize of one million dollars. Most researchers believe P is not equal to NP, but nobody has proved it.</div>
<div class="exam"><a href="dynamic-programming-2.html#subset-sum">Dynamic programming 2</a> solved subset sum in about n × target steps. That is only fast when the target is small, because the target can have many digits, and each extra digit multiplies the work by 10.</div>
'''),
    dict(id='reductions', emoji='🔁', title='Reductions: one problem dressed as another', html='''
<p>A <b>reduction</b> rewrites one problem as another, so a solver for the second also solves the first. Here is a tiny one. An <b>independent set</b> is a group of vertices with no edge between any two of them. A <b>vertex cover</b> is a group of vertices that touches every edge. Take the vertices left out of an independent set, and you always get a vertex cover.</p>
<div class="viz" data-viz="pk" data-pk="isvc"></div>
<div class="c3" data-k="reduction" data-label="Largest independent set, then flip it into a vertex cover"></div>
<span class="eq">largest independent set + smallest vertex cover = number of vertices</span>
<div class="tip">In 1971 Stephen Cook proved that SAT is NP-complete, and Leonid Levin found the same result on his own. In 1972 Richard Karp used reductions to show that 21 well known problems, including vertex cover, are NP-complete too.</div>
<div class="warn">Direction matters. To show a new problem is hard, reduce a known hard problem to it. Reducing the new problem to a hard one only shows that the new one is no harder.</div>
'''),
    dict(id='approximation', emoji='🎯', title='Approximation: good enough, with a guarantee', html='''
<p>When the exact answer is out of reach, an <b>approximation algorithm</b> runs fast and promises to land within a fixed factor of the best answer. For vertex cover the method is short: walk through the edges, and whenever an edge has no chosen end yet, take <b>both</b> of its ends.</p>
<div class="viz" data-viz="pk" data-pk="approx"></div>
<div class="c3" data-k="approxvc" data-label="Take both ends: a cover at most twice the best"></div>
<div class="exam">Here is the reason for the factor 2. The edges we took both ends of share no vertex. Any cover, even the best one, needs at least one end of each of them. So the best cover has at least as many vertices as we took edges, and we chose exactly two per edge.</div>
<div class="tw"><table class="jt"><tr><th>Problem</th><th>A known guarantee</th></tr>
<tr><td>Vertex cover</td><td>2, by taking both ends</td></tr>
<tr><td>Travelling salesman, when no detour is shorter than the direct road</td><td>1.5, by Christofides' method</td></tr>
<tr><td>Set cover</td><td>about ln n, by greedy</td></tr>
<tr><td>Knapsack</td><td>as close to 1 as you like, with more time</td></tr></table></div>
'''),
    dict(id='randomized-selection', emoji='🎲', title='Randomized algorithms: quickselect', html='''
<p>A <b>randomized algorithm</b> rolls dice while it runs. <b>Quickselect</b> finds the k-th smallest value without sorting. It picks a random pivot, splits the range around it like quicksort, and then keeps only the side that holds the answer. A bad pivot can happen, but random pivots make a long run of bad ones very unlikely.</p>
<div class="viz" data-viz="pk" data-pk="qselect"></div>
<div class="c3" data-k="quickselect" data-label="Quickselect with random pivots"></div>
<span class="eq">expected work ≈ n + n ÷ 2 + n ÷ 4 + … &lt; 2n, so O(n) on average</span>
<div class="tw"><table class="jt"><tr><th>Kind</th><th>Answer</th><th>Running time</th><th>Example</th></tr>
<tr><td>Las Vegas</td><td>Always right</td><td>Random</td><td>Quickselect, quicksort</td></tr>
<tr><td>Monte Carlo</td><td>Probably right</td><td>Fixed</td><td>Miller-Rabin prime test, estimating π</td></tr></table></div>
<div class="tip">The median of medians method picks a pivot that is always good enough, so it runs in O(n) even in the worst case. It is slower in practice, which is why libraries usually choose random pivots.</div>
'''),
    dict(id='random-sampling', emoji='🌊', title='Reservoir sampling and Monte Carlo', html='''
<p><b>Reservoir sampling</b> picks k items fairly from a stream whose length is unknown, using only k slots. Keep the first k items. When item number i arrives, keep it with chance k ÷ i, in place of a random kept item. Every item ends with the same chance, k ÷ n.</p>
<div class="viz" data-viz="pk" data-pk="reservoir"></div>
<div class="c3" data-k="reservoir" data-label="Reservoir sampling, and a check that it is fair"></div>
<p>A <b>Monte Carlo</b> method uses many random tries to estimate a number. Throw random points into a square and count how many land inside the quarter circle. That share is close to π ÷ 4.</p>
<div class="c3" data-k="montecarlo" data-label="Estimating π with random points"></div>
<span class="eq">π ≈ 4 × points inside ÷ all points &nbsp;&nbsp; error shrinks like 1 ÷ √N</span>
<div class="warn">To make an estimate 10 times more accurate, a Monte Carlo method needs about 100 times as many points. Our run of 10000 points gave 3.1352, close to π but not exact.</div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem is solved in the Practice section in Python, JavaScript, Java and TypeScript, with line by line replay. The random ones use a small repeatable dice function, so every language prints the same counts.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>Tool</th></tr>
<tr><td><a href="#lc384">384. Shuffle an Array</a></td><td>Easy</td><td>Fisher-Yates shuffle</td></tr>
<tr><td><a href="#lc398">398. Random Pick Index</a></td><td>Easy</td><td>reservoir sampling</td></tr>
<tr><td><a href="#lc528">528. Random Pick with Weight</a></td><td>Medium</td><td>running totals and binary search</td></tr>
<tr><td><a href="#lc215">215. Kth Largest Element in an Array</a></td><td>Medium</td><td>quickselect</td></tr>
<tr><td><a href="#lc470">470. Implement Rand10() Using Rand7()</a></td><td>Hard</td><td>rejection sampling</td></tr>
<tr><td><a href="#lc710">710. Random Pick with Blacklist</a></td><td>Hard</td><td>remapping blocked numbers</td></tr>
<tr><td><a href="#lc980">980. Unique Paths III</a></td><td>Expert</td><td>backtracking a Hamiltonian path</td></tr>
<tr><td><a href="#lc847">847. Shortest Path Visiting All Nodes</a></td><td>Expert</td><td>breadth first search over bit masks</td></tr></table></div>
'''),
]

VIZ_JS = r'''
(() => {
  const D = PK.defs;
  const pick = a => a[Math.floor(Math.random() * a.length)];
  const rnd = (lo, hi) => lo + Math.floor(Math.random() * (hi - lo + 1));
  const ones = m => { let c = 0; for (; m; m >>= 1) c += m & 1; return c; };
  const lcg = s => n => { s = (s * 75 + 74) % 65537; return s % n; };   /* same repeatable generator as the programs */

  /* ---------- P vs NP: subset sum ---------- */
  const NUMS = [3, 34, 4, 12, 5, 2];
  D.subset = el => PK.widget(el, {
    title: 'Hard to find, easy to check', sub: 'Pick some of the numbers so they add up to the target. Finding a pick means trying subsets one by one. Checking a pick is one quick sum.',
    inputs: [{ k: 'x', label: 'Target', type: 'num', val: 9, min: 1, max: 60, w: 70 }],
    random: () => ({ x: pick([9, 30, 21, 16, 13, 41, 7, 25]) }),
    check: v => Number.isInteger(v.x) && v.x >= 1 && v.x <= 60 ? '' : 'Pick a target from 1 to 60.',
    frames: ({ x }) => {
      const n = NUMS.length, F = [];
      const pic = (cls = {}) => [{ t: 'row', label: 'The numbers', cells: NUMS.slice(), cls }];
      const sel = m => Object.fromEntries(NUMS.map((_, i) => [i, (m >> i) & 1 ? 'look' : '']));
      const sumOf = m => NUMS.reduce((s, v, i) => s + ((m >> i) & 1 ? v : 0), 0);
      F.push({ mood: 'think', msg: `${n} numbers make ${1 << n} possible subsets. Look for one that adds up to ${x}, trying them in order.`, vars: { target: x, tries: 0 }, layers: pic() });
      let found = -1;
      for (let m = 0; m < (1 << n); m++) if (sumOf(m) === x) { found = m; break; }
      const last = found < 0 ? (1 << n) - 1 : found;
      for (let m = 0; m <= last; m++) {
        const shown = m < 8 || m === last;
        if (!shown) {
          if (m === 8) F.push({ mood: 'work', msg: `Tries ${m + 1} to ${last} miss as well. Skipping ahead.`, vars: { target: x, tries: last }, layers: pic() });
          continue;
        }
        const s = sumOf(m), list = NUMS.filter((_, i) => (m >> i) & 1);
        if (m === found) break;
        F.push({ mood: 'look', msg: `Try ${m + 1}: {${list.join(', ')}} adds up to ${s}${s === x ? '' : ', not ' + x}.`, vars: { target: x, tries: m + 1 }, layers: pic(Object.fromEntries(Object.entries(sel(m)).map(([k, v]) => [k, v ? 'no' : '']))) });
      }
      if (found >= 0) {
        const list = NUMS.filter((_, i) => (found >> i) & 1);
        const win = Object.fromEntries(NUMS.map((_, i) => [i, (found >> i) & 1 ? 'win' : '']));
        F.push({ mood: 'wow', fx: 'rain', msg: `Try ${found + 1}: <b>{${list.join(', ')}}</b> adds up to ${x}. Found it!`, vars: { target: x, tries: found + 1 }, layers: pic(win) });
        F.push({ mood: 'happy', msg: `Now hand {${list.join(', ')}} to a friend. They check it with one sum: ${list.join(' + ')} = ${x}. Finding took ${found + 1} tries. Checking took one pass. That gap is what P versus NP is about.`, vars: { tries: found + 1, check: 1 }, layers: pic(win) });
      } else {
        F.push({ mood: 'sad', fx: 'shake', msg: `All ${1 << n} subsets tried, and none adds up to ${x}. Nope, not today! To be sure there is no answer, we had to try every single one.`, vars: { target: x, tries: 1 << n }, layers: pic() });
      }
      F.push({ mood: 'think', msg: `Each extra number doubles the subsets. With 40 numbers there are ${(2 ** 40).toLocaleString('en-US')} of them. Nobody knows a method that is always fast, yet any answer is still quick to check.`, vars: { 'subsets for 40': '2^40' }, layers: pic(found >= 0 ? Object.fromEntries(NUMS.map((_, i) => [i, (found >> i) & 1 ? 'win' : ''])) : {}) });
      return F;
    }
  });

  /* ---------- shared graphs for the vertex cover widgets ---------- */
  const GRAPHS = {
    a: { nodes: [[0, 60, 120, '0'], [1, 170, 40, '1'], [2, 170, 200, '2'], [3, 300, 40, '3'], [4, 300, 200, '4'], [5, 410, 120, '5']], edges: [[0, 1], [0, 2], [1, 2], [1, 3], [2, 4], [3, 4], [3, 5], [4, 5]] },
    b: { nodes: [[0, 235, 30, '0'], [1, 400, 110, '1'], [2, 340, 210, '2'], [3, 130, 210, '3'], [4, 70, 110, '4'], [5, 235, 125, '5']], edges: [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4], [0, 5], [2, 5], [3, 5]] },
  };
  const gpic = (g, label, ncls = {}, ecls = {}, tag = {}) => ({ t: 'graph', label, w: 470, h: 240, r: 18, nodes: g.nodes, edges: g.edges, ncls, ecls, tag });
  const ek = (u, v) => Math.min(u, v) + '-' + Math.max(u, v);
  const bestSet = (g, ok) => {                        /* brute force over every subset, only for these tiny graphs */
    const n = g.nodes.length;
    let best = -1;
    for (let m = 0; m < (1 << n); m++) if (ok(m) && (best < 0 || ok.better(m, best))) best = m;
    return best;
  };
  const isIndep = g => Object.assign(m => g.edges.every(([u, v]) => !(((m >> u) & 1) && ((m >> v) & 1))), { better: (m, b) => ones(m) > ones(b) });
  const isCover = g => Object.assign(m => g.edges.every(([u, v]) => ((m >> u) & 1) || ((m >> v) & 1)), { better: (m, b) => ones(m) < ones(b) });
  const members = (m, n) => Array.from({ length: n }, (_, i) => i).filter(i => (m >> i) & 1);

  /* ---------- reduction: independent set and vertex cover ---------- */
  D.isvc = el => PK.widget(el, {
    title: 'Turn one problem into another', sub: 'An independent set has no edge inside it. A vertex cover touches every edge. The vertices left out of one are always the other.',
    inputs: [{ k: 'g', label: 'Graph', type: 'seg', val: 'a', opts: [['a', 'triangles'], ['b', 'pentagon']] }],
    random: () => ({ g: pick(['a', 'b']) }),
    frames: ({ g: key }) => {
      const g = GRAPHS[key], n = g.nodes.length, F = [];
      const ind = bestSet(g, isIndep(g)), cover = (1 << n) - 1 - ind;
      const I = members(ind, n), C = members(cover, n);
      const base = Object.fromEntries(I.map(v => [v, 'yes']).concat(C.map(v => [v, 'sel'])));
      F.push({ mood: 'think', msg: 'Suppose we already own a solver for the largest independent set. Watch it give us the smallest vertex cover too.', vars: {}, layers: [gpic(g, 'The graph')] });
      F.push({ mood: 'work', msg: `Ask the solver. The largest independent set is <b>{${I.join(', ')}}</b>: no edge joins two of them.`, vars: { independent: I.length }, layers: [gpic(g, 'Green: the independent set', Object.fromEntries(I.map(v => [v, 'yes'])))] });
      F.push({ mood: 'look', msg: `Now flip it. Take every other vertex: {${C.join(', ')}}.`, vars: { independent: I.length, cover: C.length }, layers: [gpic(g, 'Green: independent set, blue: the rest', base)] });
      const ecls = {};
      g.edges.forEach(([u, v], idx) => {
        ecls[ek(u, v)] = 'yes';
        const inC = [u, v].filter(x => (cover >> x) & 1);
        F.push({ mood: 'work', msg: `Edge ${u}-${v}: ${inC.length === 2 ? 'both ends are' : 'end ' + inC[0] + ' is'} in the cover.${idx === 0 ? ' An edge never has both ends in the independent set, so at least one end is always left for the cover.' : ''}`, vars: { cover: C.length }, layers: [gpic(g, 'Green: independent set, blue: the cover', base, Object.assign({}, ecls))] });
      });
      F.push({ mood: 'wow', fx: 'rain', msg: `Every edge is touched, so {${C.join(', ')}} is the smallest vertex cover. ${I.length} + ${C.length} = ${n} vertices. A fast solver for one problem would be a fast solver for the other.`, vars: { independent: I.length, cover: C.length }, layers: [gpic(g, 'Green: independent set, blue: the cover', base, Object.assign({}, ecls))] });
      return F;
    }
  });

  /* ---------- 2-approximation for vertex cover ---------- */
  D.approx = el => PK.widget(el, {
    title: 'Good enough, and fast', sub: 'Walk the edges. If an edge has no chosen end yet, take both ends. The result is never more than twice the best cover.',
    inputs: [{ k: 'g', label: 'Graph', type: 'seg', val: 'a', opts: [['a', 'triangles'], ['b', 'pentagon']] }],
    random: () => ({ g: pick(['a', 'b']) }),
    frames: ({ g: key }) => {
      const g = GRAPHS[key], n = g.nodes.length, F = [], chosen = new Array(n).fill(false), ecls = {}, picked = [];
      const ncls = () => Object.fromEntries(chosen.map((c, v) => [v, c ? 'sel' : '']));
      F.push({ mood: 'think', msg: `${g.edges.length} edges to cover. Go through them in order.`, vars: { chosen: 0 }, layers: [gpic(g, 'Blue: chosen vertices')] });
      g.edges.forEach(([u, v]) => {
        if (!chosen[u] && !chosen[v]) {
          chosen[u] = chosen[v] = true;
          picked.push(u + '-' + v);
          ecls[ek(u, v)] = 'win';
          F.push({ mood: 'work', msg: `Edge ${u}-${v} is not covered. Take both ${u} and ${v}.`, vars: { chosen: chosen.filter(Boolean).length }, layers: [gpic(g, 'Blue: chosen vertices', Object.assign(ncls(), { [u]: 'cur', [v]: 'cur' }), Object.assign({}, ecls))] });
        } else {
          if (!ecls[ek(u, v)]) ecls[ek(u, v)] = 'yes';
          F.push({ mood: 'happy', msg: `Edge ${u}-${v} is already covered by ${chosen[u] ? u : v}. Nothing to do.`, vars: { chosen: chosen.filter(Boolean).length }, layers: [gpic(g, 'Blue: chosen vertices', ncls(), Object.assign({}, ecls, { [ek(u, v)]: 'look' }))] });
        }
      });
      const size = chosen.filter(Boolean).length, opt = bestSet(g, isCover(g)), O = members(opt, n);
      F.push({ mood: 'look', msg: `Quick cover: ${size} vertices. The picked edges ${picked.join(', ')} share no vertex, and any cover needs one end of each, so the best cover has at least ${picked.length}. ${size} is at most 2 × ${picked.length}.`, vars: { quick: size, 'at least': picked.length }, layers: [gpic(g, 'Gold edges: the ones we took both ends of', ncls(), Object.assign({}, ecls))] });
      F.push({ mood: size === O.length ? 'wow' : 'happy', fx: 'rain', msg: `The best cover, found by trying every subset, is <b>{${O.join(', ')}}</b> with ${O.length} vertices. Our quick answer used ${size}, ${size === O.length ? 'a perfect match this time' : 'within twice the best, as promised'}, and it took one pass instead of ${1 << n} tries.`, vars: { quick: size, best: O.length }, layers: [gpic(g, 'Green: a best cover', Object.fromEntries(O.map(v => [v, 'win'])))] });
      return F;
    }
  });

  /* ---------- quickselect ---------- */
  const QA = [7, 2, 9, 4, 1, 8, 3, 6, 5];
  D.qselect = el => PK.widget(el, {
    title: 'Find the k-th smallest without sorting', sub: 'Pick a random pivot, split the range around it, and keep only the side that holds the answer.',
    inputs: [{ k: 'k', label: 'k', type: 'num', val: 4, min: 1, max: 9, w: 60 }],
    random: () => ({ k: rnd(1, 9) }),
    check: v => Number.isInteger(v.k) && v.k >= 1 && v.k <= 9 ? '' : 'Pick k from 1 to 9.',
    frames: ({ k }) => {
      const a = QA.slice(), rand = lcg(3), F = [];
      let lo = 0, hi = a.length - 1, round = 0;
      const out = {};
      const pic = cls => [{ t: 'row', label: 'Values, the answer ends up at index ' + (k - 1), cells: a.slice(), cls: Object.assign({}, out, cls) }];
      F.push({ mood: 'think', msg: `Find the value that would sit at index ${k - 1} if the list were sorted. That is the ${k}${k === 1 ? 'st' : k === 2 ? 'nd' : k === 3 ? 'rd' : 'th'} smallest.`, vars: { k, round: 0 }, layers: pic({}) });
      while (true) {
        round++;
        const p = lo + rand(hi - lo + 1);
        const range = {};
        for (let i = lo; i <= hi; i++) range[i] = 'sel';
        F.push({ mood: 'look', msg: `Round ${round}: the range is ${lo} to ${hi}. The dice pick index ${p}, value ${a[p]}, as the pivot.`, vars: { k, round, pivot: a[p] }, layers: pic(Object.assign(range, { [p]: 'piv' })) });
        [a[p], a[hi]] = [a[hi], a[p]];
        const pivot = a[hi];
        let store = lo;
        for (let i = lo; i < hi; i++) if (a[i] < pivot) { [a[i], a[store]] = [a[store], a[i]]; store++; }
        [a[store], a[hi]] = [a[hi], a[store]];
        const cls = {};
        for (let i = lo; i <= hi; i++) cls[i] = i < store ? 'yes' : i > store ? 'no' : 'piv';
        F.push({ mood: 'work', msg: `Split: smaller values go left, bigger ones go right. Pivot ${pivot} lands at index ${store}, its sorted place.`, vars: { k, round, pivot, at: store }, layers: pic(cls) });
        if (store === k - 1) {
          F.push({ mood: 'wow', fx: 'rain', msg: `Index ${store} is the one we want. The ${k}${k === 1 ? 'st' : k === 2 ? 'nd' : k === 3 ? 'rd' : 'th'} smallest is <b>${pivot}</b>, found in ${round} round${round === 1 ? '' : 's'} without sorting everything.`, vars: { k, rounds: round, answer: pivot }, layers: pic({ [store]: 'win' }) });
          break;
        }
        if (store < k - 1) { for (let i = lo; i <= store; i++) out[i] = 'done'; lo = store + 1; }
        else { for (let i = store; i <= hi; i++) out[i] = 'done'; hi = store - 1; }
        F.push({ mood: 'happy', msg: `We need index ${k - 1}, which is ${store < k - 1 ? 'to the right' : 'to the left'} of ${store}. Throw away the other side. Only ${hi - lo + 1} value${hi === lo ? '' : 's'} left to look at.`, vars: { k, round, left: hi - lo + 1 }, layers: pic({}) });
      }
      return F;
    }
  });

  /* ---------- reservoir sampling ---------- */
  D.reservoir = el => PK.widget(el, {
    title: 'Keep a fair sample from a stream', sub: 'Keep the first k items. Item number i then stays with chance k ÷ i, replacing a random kept item.',
    inputs: [{ k: 'k', label: 'Keep', type: 'seg', val: '3', opts: [['1', '1'], ['2', '2'], ['3', '3']] }, { k: 's', label: 'Dice seed', type: 'num', val: 5, min: 1, max: 999, w: 70 }],
    random: () => ({ k: pick(['1', '2', '3']), s: rnd(1, 999) }),
    check: v => Number.isInteger(v.s) && v.s >= 1 && v.s <= 999 ? '' : 'Pick a seed from 1 to 999.',
    frames: ({ k: ks, s }) => {
      const k = Number(ks), stream = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], rand = lcg(s), keep = stream.slice(0, k), F = [];
      const pic = (scls = {}, kcls = {}) => [
        { t: 'row', label: 'The stream, one item at a time', cells: stream.slice(), cls: scls },
        { t: 'row', label: 'Kept so far', cells: keep.slice(), cls: kcls, idx: true },
      ];
      const past = i => Object.fromEntries(stream.map((_, j) => [j, j < i ? 'done' : '']));
      F.push({ mood: 'think', msg: `Keep the first ${k} item${k === 1 ? '' : 's'}: ${keep.join(', ')}. We do not know how long the stream is.`, vars: { k, seen: k }, layers: pic(past(k), Object.fromEntries(keep.map((_, j) => [j, 'yes']))) });
      for (let i = k; i < stream.length; i++) {
        const j = rand(i + 1);
        if (j < k) {
          const old = keep[j];
          keep[j] = stream[i];
          F.push({ mood: 'work', msg: `Item ${stream[i]}: roll a number from 0 to ${i}. Got ${j}, below ${k}, so ${stream[i]} replaces ${old} in slot ${j}. Chance to stay: ${k} ÷ ${i + 1}.`, vars: { item: stream[i], roll: j }, layers: pic(Object.assign(past(i), { [i]: 'yes' }), { [j]: 'mv' }) });
        } else {
          F.push({ mood: 'look', msg: `Item ${stream[i]}: roll a number from 0 to ${i}. Got ${j}, not below ${k}, so ${stream[i]} waves goodbye and floats past.`, vars: { item: stream[i], roll: j }, layers: pic(Object.assign(past(i), { [i]: 'no' }), {}) });
        }
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `The stream ended. Kept: <b>${keep.join(', ')}</b>. Every one of the 10 items had the same ${k} in 10 chance to end up here, and we used only ${k} slot${k === 1 ? '' : 's'} of memory.`, vars: { k, kept: keep.join(' ') }, layers: pic(past(stream.length), Object.fromEntries(keep.map((_, j) => [j, 'win']))) });
      return F;
    }
  });
})();
'''

INFO = {
    'title': 'When no fast exact method is known',
    'panels': [
        {'s': [['e', '🔐'], ['t', 'check fast', {'b': 1}]], 'h': 'P and NP', 't': 'Checking can be easy.', 'more': 'Finding may not be.'},
        {'s': [['e', '🔁'], ['t', 'rewrite', {'b': 1}]], 'h': 'Reductions', 't': 'One problem as another.', 'more': 'Hardness carries over.'},
        {'s': [['e', '🎯'], ['t', 'within 2×', {'b': 1}]], 'h': 'Approximation', 't': 'Fast, with a promise.', 'more': 'Never far from the best.'},
        {'s': [['e', '🎲'], ['t', 'dice', {'b': 1}]], 'h': 'Randomized', 't': 'Quickselect, sampling.', 'more': 'Fast on average.'},
    ],
    'remember': 'For a hard problem, pick one of three ways out: solve small cases exactly, accept an answer with a proven guarantee, or let random choices make the bad cases very unlikely.',
}

REAL = [
    ['🚚', 'Delivery routes', 'Route planners cannot try every order of stops, so they use approximation and clever search to get routes close to the best.'],
    ['🔑', 'Cryptography', 'Internet security relies on problems that are easy to check but believed to be hard to solve, and it uses randomized prime tests to make keys.'],
    ['📊', 'Sampling big data', 'Reservoir sampling keeps a fair random sample of logs or events when the full stream is far too big to store.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to hard problems, the last chapter of the expert step. Some problems have no known fast method. You will see why checking an answer can be easy while finding one is hard, how reductions carry hardness from one problem to another, how approximation gives answers with a guarantee, and how dice make algorithms fast on average.'},
    {'id': 'p-vs-np', 'h': 'P and NP', 'en': 'P is the class of problems we can solve in polynomial time. NP is the class where a proposed answer can be checked in polynomial time. Subset sum is in NP: checking a group of numbers is one sum, but finding one may mean trying every subset. Nobody knows whether P equals NP.'},
    {'id': 'reductions', 'h': 'Reductions', 'en': 'A reduction rewrites one problem as another. The vertices left out of an independent set always form a vertex cover, so a solver for one gives a solver for the other. Reductions like this showed that thousands of problems are equally hard.'},
    {'id': 'approximation', 'h': 'Approximation', 'en': 'An approximation algorithm is fast and promises an answer within a fixed factor of the best. For vertex cover, take both ends of any edge that is not covered yet. The result is never more than twice the size of the best cover.'},
    {'id': 'randomized-selection', 'h': 'Quickselect', 'en': 'Quickselect finds the k-th smallest value with a random pivot. After each split it keeps only the side that holds the answer. On average the work adds up to less than two times n, so it is linear.'},
    {'id': 'random-sampling', 'h': 'Sampling', 'en': 'Reservoir sampling keeps k items from a stream of unknown length. Item number i stays with chance k over i. A Monte Carlo method uses many random tries to estimate a number, such as pi from random points in a square.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from shuffling an array to visiting every node of a graph. Each one is solved in Python, JavaScript, Java and TypeScript, and the random ones use a repeatable dice function so every language prints the same result.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. For each problem, decide whether it needs fair dice, a random pivot, or a full search over a small input. Open the hint if you are stuck.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'What does it mean for a problem to be in NP?', 'o': ['It can never be solved', 'A proposed answer can be checked in polynomial time', 'It needs a random algorithm', 'It is not a problem'], 'a': 1, 'hint': 'Think about checking, not finding.', 'why': 'NP is the class of problems whose answers can be verified quickly.'},
    {'lv': 'e', 'q': 'How many subsets do 6 numbers have?', 'o': ['6', '12', '36', '64'], 'a': 3, 'hint': 'Each number is in or out.', 'why': 'Two choices for each of 6 numbers: 2⁶ = 64.'},
    {'lv': 'e', 'q': 'What does a vertex cover do?', 'o': ['Touches every edge', 'Visits every vertex in a cycle', 'Has no edges inside it', 'Colours the graph'], 'a': 0, 'hint': 'Cover the edges.', 'why': 'Every edge must have at least one end in a vertex cover.'},
    {'lv': 'e', 'q': 'What does quickselect find?', 'o': ['A sorted list', 'The k-th smallest value', 'The sum of the list', 'A random value'], 'a': 1, 'hint': 'Selection, not sorting.', 'why': 'It finds the value that would sit at index k − 1 after sorting, without sorting everything.'},
    {'lv': 'm', 'q': 'Why is subset sum in NP?', 'o': ['It has no answer', 'Adding up a proposed group of numbers is fast', 'It is solved by sorting', 'It uses a hash'], 'a': 1, 'hint': 'Checking a group is one pass.', 'why': 'Given a group, one sum confirms whether it hits the target.'},
    {'lv': 'm', 'q': 'A graph has 6 vertices and its largest independent set has 2. What is the size of its smallest vertex cover?', 'o': ['2', '3', '4', '6'], 'a': 2, 'hint': 'They add up to the number of vertices.', 'why': 'The vertices outside the largest independent set form the smallest cover: 6 − 2 = 4.'},
    {'lv': 'm', 'q': 'The take both ends method returned a cover of 6 vertices. What is the smallest the best cover can be?', 'o': ['1', '2', '3', '6'], 'a': 2, 'hint': 'It took 3 edges.', 'why': 'It took both ends of 3 edges that share no vertex, and any cover needs one end of each, so the best has at least 3.'},
    {'lv': 'm', 'q': 'In reservoir sampling with k = 1, what chance does item number 5 have to replace the kept item?', 'o': ['1 ÷ 2', '1 ÷ 4', '1 ÷ 5', '5 ÷ 10'], 'a': 2, 'hint': 'k ÷ i.', 'why': 'Item i is kept with chance k ÷ i, here 1 ÷ 5.'},
    {'lv': 'h', 'q': 'To prove a new problem X is NP-hard, which way should the reduction go?', 'o': ['From X to a known NP-hard problem', 'From a known NP-hard problem to X', 'Either way', 'No reduction is needed'], 'a': 1, 'hint': 'X must be able to solve the known hard problem.', 'why': 'If a solver for X also solves a known hard problem, then X is at least that hard.'},
    {'lv': 'h', 'q': 'What is the worst case running time of quickselect with random pivots?', 'o': ['O(log n)', 'O(n)', 'O(n log n)', 'O(n²)'], 'a': 3, 'hint': 'The dice can be unlucky every time.', 'why': 'If every pivot is the smallest or biggest value, each round removes only one value. That is very unlikely, so the expected time is O(n).'},
    {'lv': 'h', 'q': 'What kind of randomized algorithm is quickselect?', 'o': ['Monte Carlo: fixed time, maybe wrong', 'Las Vegas: always right, random time', 'Neither', 'Both'], 'a': 1, 'hint': 'Is its answer ever wrong?', 'why': 'Quickselect always returns the right value. Only its running time depends on the dice.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'nums = [2, 5]\ncount = 0\nfor mask in range(1 << len(nums)):\n    total = sum(nums[i] for i in range(2) if mask >> i & 1)\n    if total == 5:\n        count += 1\nprint(count)', 'o': ['0', '1', '2', '4'], 'a': 1, 'hint': 'The subsets are {}, {2}, {5} and {2, 5}.', 'why': 'Only {5} adds up to 5, so the count is 1.'},
    {'lv': 'x', 'q': 'In Rand10 from Rand7, why are the values 41 to 49 thrown away?', 'o': ['They are too big to print', 'Keeping them would make some of 1 to 10 more likely than others', 'They never appear', 'To save time'], 'a': 1, 'hint': '49 does not split evenly into 10 groups.', 'why': '40 values split into 10 groups of 4. Using 41 to 49 too would give 1 to 9 an extra chance.'},
    {'lv': 'x', 'q': 'About how many points does a Monte Carlo estimate need to become 10 times more accurate?', 'o': ['10 times as many', '100 times as many', '2 times as many', '1000 times as many'], 'a': 1, 'hint': 'The error shrinks like 1 ÷ √N.', 'why': 'To divide 1 ÷ √N by 10, N must grow by 10² = 100.'},
    {'lv': 'x', 'q': 'How many states does the breadth first search in Shortest Path Visiting All Nodes have for n nodes?', 'o': ['n', 'n²', 'n × 2ⁿ', 'n!'], 'a': 2, 'hint': 'A node and a set of visited nodes.', 'why': 'There are n places to stand and 2ⁿ possible visited sets.'},
    {'lv': 'x', 'q': 'If someone found a polynomial time method for one NP-complete problem, what would follow?', 'o': ['Nothing else would change', 'Every problem in NP could be solved in polynomial time', 'Only sorting would get faster', 'All problems would become impossible'], 'a': 1, 'hint': 'Every NP problem reduces to an NP-complete one.', 'why': 'Every problem in NP reduces to any NP-complete problem, so a fast method for one gives a fast method for all, and P would equal NP.'},
]

CALC = [
    {'lv': 'e', 'q': 'How many subsets do 10 numbers have?', 'ans': '1024', 'hint': '2 to the power 10.', 'steps': ['<span class="eq">2¹⁰ = 1024</span>']},
    {'lv': 'e', 'q': 'A graph has 6 vertices and a smallest vertex cover of 4. How big is its largest independent set?', 'ans': '2', 'hint': 'They add up to 6.', 'steps': ['<span class="eq">6 − 4 = 2</span>']},
    {'lv': 'm', 'q': 'The take both ends method picked 3 edges. How many vertices are in its cover?', 'ans': '6', 'hint': 'Two per picked edge.', 'steps': ['<span class="eq">2 × 3 = 6</span>', 'The picked edges share no vertex, so no vertex is counted twice.']},
    {'lv': 'm', 'q': 'Weights [1, 3]: out of 4000 picks, about how many should be index 1?', 'ans': '3000', 'hint': 'Index 1 owns 3 of the 4 numbers.', 'steps': ['<span class="eq">4000 × 3 ÷ 4 = 3000</span>', 'The program printed 2993.']},
    {'lv': 'h', 'q': 'With k = 3, what chance does item number 6 have to enter the reservoir? Give the answer as a fraction in lowest terms.', 'ans': '1/2', 'hint': 'k ÷ i.', 'steps': ['<span class="eq">3 ÷ 6 = 1 ÷ 2</span>']},
    {'lv': 'h', 'q': 'In our Monte Carlo run, 7838 of 10000 points fell inside the quarter circle. What is the estimate of π?', 'ans': '3.1352', 'hint': '4 × inside ÷ all.', 'steps': ['<span class="eq">4 × 7838 ÷ 10000 = 3.1352</span>']},
    {'lv': 'x', 'q': 'For Rand10 from Rand7, out of 49 equally likely pairs, how many are kept?', 'ans': '40', 'hint': 'The largest multiple of 10 that fits.', 'steps': ['49 values, and 40 is the largest multiple of 10 that is at most 49.', 'So 40 are kept and 9 cause a new roll.']},
    {'lv': 'x', 'q': 'How many states does the search in Shortest Path Visiting All Nodes have for 12 nodes?', 'ans': '49152', 'hint': 'n × 2ⁿ.', 'steps': ['<span class="eq">12 × 2¹² = 12 × 4096 = 49152</span>']},
]

TALK = {
    'p-vs-np': 'Some problems have fast methods. Sorting a list or finding a shortest path takes a number of steps that grows like a power of n, such as n squared. This class of problems is called P. Other problems have a curious property. If someone hands you an answer, you can check it quickly, but nobody knows how to find an answer quickly. That class is called NP. Subset sum is a good example. The question is whether some group of the numbers adds up exactly to a target. Checking a proposed group is one quick sum. Finding one, as far as anyone knows, may mean trying the subsets one by one, and every extra number doubles how many there are. With forty numbers there are over a trillion. Whether every problem that is easy to check is also easy to solve is the famous P versus NP question, and nobody has answered it yet.',
    'reductions': 'A reduction is a way to dress one problem up as another. If you can turn any question about problem A into a question about problem B, then a fast solver for B would also be a fast solver for A. Here is a small example. An independent set is a group of vertices with no edge between any two of them. A vertex cover is a group of vertices that touches every edge. Take the largest independent set and look at all the other vertices. Every edge has at most one end inside the independent set, so its other end is in the rest. That means the rest is always a vertex cover, and it is the smallest one. So the two problems are really one problem. In nineteen seventy two, Richard Karp used reductions like this to show that twenty one famous problems are all equally hard.',
    'approximation': 'When an exact answer would take too long, we can sometimes settle for an answer that is provably close. An approximation algorithm runs fast and promises that its answer is within a fixed factor of the best possible one. For vertex cover, the method is wonderfully short. Walk through the edges one by one. If an edge already has a chosen end, skip it. If not, choose both of its ends. Here is why the result is at most twice the best. Look at the edges where we chose both ends. No two of them share a vertex, because once a vertex is chosen, every later edge touching it is skipped. Any cover at all, even the best one, needs at least one end of each of those edges. So the best cover has at least as many vertices as we picked edges, and we used exactly two per edge.',
    'randomized-selection': 'Quickselect finds the k-th smallest value in a list without sorting the whole thing. It borrows the split step from quicksort. Pick a pivot, then move every smaller value to its left and every bigger value to its right. Now the pivot sits exactly where it would be in the sorted list. If that is position k minus one, we are done. If the answer lies to the left, throw away the right side, and if it lies to the right, throw away the left side. Then repeat on the part that is left. The dice matter for the pivot. A fixed choice, like always the last value, can be terrible on some inputs. A random pivot lands near the middle most of the time, so the work shrinks quickly, about n, then half of n, then a quarter, adding up to less than two n. The answer is always right, only the time is random.',
    'random-sampling': 'Imagine a stream of items flowing past, and you must keep a fair random sample of k items, without knowing how many will come. Reservoir sampling solves this with only k slots. Keep the first k items. When item number i arrives, roll a number from zero to i minus one. If it is below k, the new item replaces the kept item in that slot. Otherwise it floats past. Item number i stays with chance k over i, and the later replacements balance out, so at the end every item has the same chance, k over n. A Monte Carlo method uses randomness differently. It estimates a number from many random tries. Throw random points into a square, and count how many land inside a quarter circle. That share is close to pi over four. Our ten thousand points gave three point one three five two.',
    'leetcode': 'The LeetCode problems in this chapter are about fair randomness and about searches that grow very fast. The easy problems shuffle an array so every order is equally likely, and pick a random index of a repeated value with reservoir sampling. The medium problems pick an index with chance proportional to its weight, using running totals and binary search, and find the k-th largest value with quickselect. The hard problems build a fair one to ten roll from a one to seven roll by throwing away some results, and pick a random number while skipping a blacklist. The expert problems count paths that visit every square of a grid, and find the shortest walk through every node of a graph by searching over sets of visited nodes. Each one is solved in four languages, and you can replay every line.',
}

T = t.finish({
    'slug': 'hard-problems', 'title': 'Hard Problems and Randomized Algorithms', 'short': 'Hard problems', 'emoji': '🎲', 'topic': 'hard-problems', 'prefix': 'dsahard',
    'module': ('🚀', 'Expert topics'),
    'lead': 'Some problems have no known fast method. See why checking an answer can be easy while finding one is hard, carry hardness from one problem to another with reductions, get answers with a guarantee from approximation, and let dice make algorithms fast on average.',
    'desc': 'Hard problems in DSA: P and NP, NP-complete problems, reductions, approximation algorithms for vertex cover, randomized quickselect, reservoir sampling and Monte Carlo estimation, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 26,
    'summary': 'P and NP with subset sum, the reduction between independent set and vertex cover, a 2-approximation for vertex cover, quickselect with random pivots, reservoir sampling and Monte Carlo estimation of π. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['p vs np', 'np complete', 'np hard', 'reduction', 'subset sum', 'vertex cover', 'independent set', 'approximation algorithm', 'randomized algorithm', 'quickselect', 'las vegas', 'monte carlo', 'reservoir sampling', 'fisher yates shuffle', 'rejection sampling'],
    'added': '2026-11-23',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS, 'css': '',
    'prev': ('special-structures', 'special-structures', '🛗 Special structures'),
    'next': None,
})
