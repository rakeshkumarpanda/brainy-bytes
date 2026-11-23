# Divide and conquer: divide, conquer, combine, counting inversions with merge sort, the master theorem,
# quickselect, maximum subarray, the closest pair of points and Karatsuba multiplication.
from kit4 import Topic

t = Topic()

# ---------------------------------------------------------------- lesson programs
t.code('dcmax', py=r'''
calls = 0


def biggest(a, lo, hi):
    global calls
    calls += 1
    if lo == hi:
        return a[lo]                          # one number: it is the biggest of itself
    mid = (lo + hi) // 2                      # divide into two halves
    left = biggest(a, lo, mid)                # conquer each half
    right = biggest(a, mid + 1, hi)
    return left if left >= right else right   # combine the two answers


nums = [3, 8, 1, 9, 4, 7, 2, 6]
print("max", biggest(nums, 0, len(nums) - 1), "after", calls, "calls")
''', js=r'''
let calls = 0;

function biggest(a, lo, hi) {
  calls++;
  if (lo === hi) return a[lo];               // one number: it is the biggest of itself
  const mid = Math.floor((lo + hi) / 2);     // divide into two halves
  const left = biggest(a, lo, mid);          // conquer each half
  const right = biggest(a, mid + 1, hi);
  return left >= right ? left : right;       // combine the two answers
}

const nums = [3, 8, 1, 9, 4, 7, 2, 6];
console.log("max", biggest(nums, 0, nums.length - 1), "after", calls, "calls");
''', java=r'''
public class Biggest {
    static int calls = 0;

    static int biggest(int[] a, int lo, int hi) {
        calls++;
        if (lo == hi) return a[lo];                  // one number: it is the biggest of itself
        int mid = (lo + hi) / 2;                     // divide into two halves
        int left = biggest(a, lo, mid);              // conquer each half
        int right = biggest(a, mid + 1, hi);
        return left >= right ? left : right;         // combine the two answers
    }

    public static void main(String[] args) {
        int[] nums = {3, 8, 1, 9, 4, 7, 2, 6};
        int m = biggest(nums, 0, nums.length - 1);
        System.out.println("max " + m + " after " + calls + " calls");
    }
}
''', ts=r'''
let calls = 0;

function biggest(a: number[], lo: number, hi: number): number {
  calls++;
  if (lo === hi) return a[lo];               // one number: it is the biggest of itself
  const mid = Math.floor((lo + hi) / 2);     // divide into two halves
  const left = biggest(a, lo, mid);          // conquer each half
  const right = biggest(a, mid + 1, hi);
  return left >= right ? left : right;       // combine the two answers
}

const nums = [3, 8, 1, 9, 4, 7, 2, 6];
console.log("max", biggest(nums, 0, nums.length - 1), "after", calls, "calls");
''')

t.code('inversions', py=r'''
def sort_count(a):
    """Return the sorted list and how many pairs i < j have a[i] > a[j]."""
    if len(a) <= 1:
        return a, 0
    mid = len(a) // 2
    left, x = sort_count(a[:mid])
    right, y = sort_count(a[mid:])
    merged, i, j, cross = [], 0, 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
            cross += len(left) - i            # right[j] jumps over every left item still waiting
    merged += left[i:] + right[j:]
    return merged, x + y + cross


def brute(a):
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])


for a in ([8, 4, 2, 1], [3, 1, 2, 5, 4], [1, 2, 3, 4, 5], [6, 5, 4, 3, 2, 1]):
    s, c = sort_count(a)
    print(" ".join(map(str, a)), " inversions", c, " brute force", brute(a))
''', js=r'''
function sortCount(a) {
  if (a.length <= 1) return [a, 0];
  const mid = Math.floor(a.length / 2);
  const [left, x] = sortCount(a.slice(0, mid));
  const [right, y] = sortCount(a.slice(mid));
  const merged = [];
  let i = 0, j = 0, cross = 0;
  while (i < left.length && j < right.length) {
    if (left[i] <= right[j]) merged.push(left[i++]);
    else {
      merged.push(right[j++]);
      cross += left.length - i;              // right[j] jumps over every left item still waiting
    }
  }
  return [merged.concat(left.slice(i), right.slice(j)), x + y + cross];
}

function brute(a) {
  let c = 0;
  for (let i = 0; i < a.length; i++) for (let j = i + 1; j < a.length; j++) if (a[i] > a[j]) c++;
  return c;
}

for (const a of [[8, 4, 2, 1], [3, 1, 2, 5, 4], [1, 2, 3, 4, 5], [6, 5, 4, 3, 2, 1]]) {
  console.log(a.join(" "), " inversions", sortCount(a)[1], " brute force", brute(a));
}
''', java=r'''
import java.util.*;

public class Inversions {
    static long count;

    static int[] sortCount(int[] a) {
        if (a.length <= 1) return a;
        int mid = a.length / 2;
        int[] left = sortCount(Arrays.copyOfRange(a, 0, mid));
        int[] right = sortCount(Arrays.copyOfRange(a, mid, a.length));
        int[] merged = new int[a.length];
        int i = 0, j = 0, k = 0;
        while (i < left.length && j < right.length) {
            if (left[i] <= right[j]) merged[k++] = left[i++];
            else {
                merged[k++] = right[j++];
                count += left.length - i;            // right[j] jumps over every left item still waiting
            }
        }
        while (i < left.length) merged[k++] = left[i++];
        while (j < right.length) merged[k++] = right[j++];
        return merged;
    }

    static int brute(int[] a) {
        int c = 0;
        for (int i = 0; i < a.length; i++) for (int j = i + 1; j < a.length; j++) if (a[i] > a[j]) c++;
        return c;
    }

    public static void main(String[] args) {
        int[][] tests = {{8, 4, 2, 1}, {3, 1, 2, 5, 4}, {1, 2, 3, 4, 5}, {6, 5, 4, 3, 2, 1}};
        for (int[] a : tests) {
            count = 0;
            sortCount(a);
            StringBuilder sb = new StringBuilder();
            for (int x : a) sb.append(sb.length() > 0 ? " " : "").append(x);
            System.out.println(sb + "  inversions " + count + "  brute force " + brute(a));
        }
    }
}
''', ts=r'''
function sortCount(a: number[]): [number[], number] {
  if (a.length <= 1) return [a, 0];
  const mid = Math.floor(a.length / 2);
  const [left, x] = sortCount(a.slice(0, mid));
  const [right, y] = sortCount(a.slice(mid));
  const merged: number[] = [];
  let i = 0, j = 0, cross = 0;
  while (i < left.length && j < right.length) {
    if (left[i] <= right[j]) merged.push(left[i++]);
    else {
      merged.push(right[j++]);
      cross += left.length - i;              // right[j] jumps over every left item still waiting
    }
  }
  return [merged.concat(left.slice(i), right.slice(j)), x + y + cross];
}

function brute(a: number[]): number {
  let c = 0;
  for (let i = 0; i < a.length; i++) for (let j = i + 1; j < a.length; j++) if (a[i] > a[j]) c++;
  return c;
}

for (const a of [[8, 4, 2, 1], [3, 1, 2, 5, 4], [1, 2, 3, 4, 5], [6, 5, 4, 3, 2, 1]]) {
  console.log(a.join(" "), " inversions", sortCount(a)[1], " brute force", brute(a));
}
''')

t.code('master', py=r'''
def merge_sort_work(n):        # T(n) = 2 T(n/2) + n
    return 1 if n == 1 else 2 * merge_sort_work(n // 2) + n


def binary_search_work(n):     # T(n) = T(n/2) + 1
    return 1 if n == 1 else binary_search_work(n // 2) + 1


def karatsuba_mults(n):        # M(n) = 3 M(n/2)
    return 1 if n == 1 else 3 * karatsuba_mults(n // 2)


def school_mults(n):           # M(n) = 4 M(n/2), the same as n * n
    return 1 if n == 1 else 4 * school_mults(n // 2)


print("n | merge sort | binary search | karatsuba | schoolbook")
n = 1
while n <= 1024:
    print(n, "|", merge_sort_work(n), "|", binary_search_work(n), "|", karatsuba_mults(n), "|", school_mults(n))
    n *= 4
''', js=r'''
const mergeSortWork = n => (n === 1 ? 1 : 2 * mergeSortWork(Math.floor(n / 2)) + n);      // T(n) = 2 T(n/2) + n
const binarySearchWork = n => (n === 1 ? 1 : binarySearchWork(Math.floor(n / 2)) + 1);   // T(n) = T(n/2) + 1
const karatsubaMults = n => (n === 1 ? 1 : 3 * karatsubaMults(Math.floor(n / 2)));       // M(n) = 3 M(n/2)
const schoolMults = n => (n === 1 ? 1 : 4 * schoolMults(Math.floor(n / 2)));             // M(n) = 4 M(n/2)

console.log("n | merge sort | binary search | karatsuba | schoolbook");
for (let n = 1; n <= 1024; n *= 4) {
  console.log(n, "|", mergeSortWork(n), "|", binarySearchWork(n), "|", karatsubaMults(n), "|", schoolMults(n));
}
''', java=r'''
public class MasterTheorem {
    static long mergeSortWork(long n) { return n == 1 ? 1 : 2 * mergeSortWork(n / 2) + n; }      // T(n) = 2 T(n/2) + n
    static long binarySearchWork(long n) { return n == 1 ? 1 : binarySearchWork(n / 2) + 1; }  // T(n) = T(n/2) + 1
    static long karatsubaMults(long n) { return n == 1 ? 1 : 3 * karatsubaMults(n / 2); }      // M(n) = 3 M(n/2)
    static long schoolMults(long n) { return n == 1 ? 1 : 4 * schoolMults(n / 2); }            // M(n) = 4 M(n/2)

    public static void main(String[] args) {
        System.out.println("n | merge sort | binary search | karatsuba | schoolbook");
        for (long n = 1; n <= 1024; n *= 4) {
            System.out.println(n + " | " + mergeSortWork(n) + " | " + binarySearchWork(n) + " | " + karatsubaMults(n) + " | " + schoolMults(n));
        }
    }
}
''', ts=r'''
const mergeSortWork = (n: number): number => (n === 1 ? 1 : 2 * mergeSortWork(Math.floor(n / 2)) + n);      // T(n) = 2 T(n/2) + n
const binarySearchWork = (n: number): number => (n === 1 ? 1 : binarySearchWork(Math.floor(n / 2)) + 1);   // T(n) = T(n/2) + 1
const karatsubaMults = (n: number): number => (n === 1 ? 1 : 3 * karatsubaMults(Math.floor(n / 2)));       // M(n) = 3 M(n/2)
const schoolMults = (n: number): number => (n === 1 ? 1 : 4 * schoolMults(Math.floor(n / 2)));             // M(n) = 4 M(n/2)

console.log("n | merge sort | binary search | karatsuba | schoolbook");
for (let n = 1; n <= 1024; n *= 4) {
  console.log(n, "|", mergeSortWork(n), "|", binarySearchWork(n), "|", karatsubaMults(n), "|", schoolMults(n));
}
''')

t.code('qselect', py=r'''
def quickselect(nums, k):
    """k-th smallest, counting from 0, without sorting everything."""
    a = nums[:]
    lo, hi = 0, len(a) - 1
    while True:
        pivot, store = a[hi], lo
        for i in range(lo, hi):               # partition: smaller values to the left
            if a[i] < pivot:
                a[i], a[store] = a[store], a[i]
                store += 1
        a[store], a[hi] = a[hi], a[store]     # the pivot lands in its final place
        if store == k:
            return a[store]
        if store < k:
            lo = store + 1                    # keep only the side that holds k
        else:
            hi = store - 1


nums = [7, 2, 9, 4, 1, 8, 3]
print("sorted would be", " ".join(map(str, sorted(nums))))
print("quickselect k = 0..6:", " ".join(str(quickselect(nums, k)) for k in range(len(nums))))
print("median", quickselect(nums, len(nums) // 2))
''', js=r'''
function quickselect(nums, k) {
  const a = [...nums];
  let lo = 0, hi = a.length - 1;
  while (true) {
    const pivot = a[hi];
    let store = lo;
    for (let i = lo; i < hi; i++) {          // partition: smaller values to the left
      if (a[i] < pivot) {
        [a[i], a[store]] = [a[store], a[i]];
        store++;
      }
    }
    [a[store], a[hi]] = [a[hi], a[store]];   // the pivot lands in its final place
    if (store === k) return a[store];
    if (store < k) lo = store + 1;           // keep only the side that holds k
    else hi = store - 1;
  }
}

const nums = [7, 2, 9, 4, 1, 8, 3];
console.log("sorted would be", [...nums].sort((x, y) => x - y).join(" "));
console.log("quickselect k = 0..6:", nums.map((_, k) => quickselect(nums, k)).join(" "));
console.log("median", quickselect(nums, Math.floor(nums.length / 2)));
''', java=r'''
import java.util.*;

public class QuickSelect {
    static int quickselect(int[] nums, int k) {
        int[] a = nums.clone();
        int lo = 0, hi = a.length - 1;
        while (true) {
            int pivot = a[hi], store = lo;
            for (int i = lo; i < hi; i++) {          // partition: smaller values to the left
                if (a[i] < pivot) {
                    int t = a[i]; a[i] = a[store]; a[store] = t;
                    store++;
                }
            }
            int t = a[store]; a[store] = a[hi]; a[hi] = t;   // the pivot lands in its final place
            if (store == k) return a[store];
            if (store < k) lo = store + 1;           // keep only the side that holds k
            else hi = store - 1;
        }
    }

    public static void main(String[] args) {
        int[] nums = {7, 2, 9, 4, 1, 8, 3};
        int[] s = nums.clone();
        Arrays.sort(s);
        StringBuilder a = new StringBuilder(), b = new StringBuilder();
        for (int x : s) a.append(a.length() > 0 ? " " : "").append(x);
        for (int k = 0; k < nums.length; k++) b.append(k > 0 ? " " : "").append(quickselect(nums, k));
        System.out.println("sorted would be " + a);
        System.out.println("quickselect k = 0..6: " + b);
        System.out.println("median " + quickselect(nums, nums.length / 2));
    }
}
''', ts=r'''
function quickselect(nums: number[], k: number): number {
  const a = [...nums];
  let lo = 0, hi = a.length - 1;
  while (true) {
    const pivot = a[hi];
    let store = lo;
    for (let i = lo; i < hi; i++) {          // partition: smaller values to the left
      if (a[i] < pivot) {
        [a[i], a[store]] = [a[store], a[i]];
        store++;
      }
    }
    [a[store], a[hi]] = [a[hi], a[store]];   // the pivot lands in its final place
    if (store === k) return a[store];
    if (store < k) lo = store + 1;           // keep only the side that holds k
    else hi = store - 1;
  }
}

const nums = [7, 2, 9, 4, 1, 8, 3];
console.log("sorted would be", [...nums].sort((x, y) => x - y).join(" "));
console.log("quickselect k = 0..6:", nums.map((_, k) => quickselect(nums, k)).join(" "));
console.log("median", quickselect(nums, Math.floor(nums.length / 2)));
''')

t.code('maxsub', py=r'''
def best(a, lo, hi):
    """(sum, start, end) of the best subarray inside a[lo..hi]."""
    if lo == hi:
        return (a[lo], lo, lo)
    mid = (lo + hi) // 2
    left = best(a, lo, mid)                   # best that stays in the left half
    right = best(a, mid + 1, hi)              # best that stays in the right half
    s, lsum, li = 0, None, mid
    for i in range(mid, lo - 1, -1):          # best run ending exactly at mid
        s += a[i]
        if lsum is None or s > lsum:
            lsum, li = s, i
    s, rsum, rj = 0, None, mid + 1
    for j in range(mid + 1, hi + 1):          # best run starting exactly at mid + 1
        s += a[j]
        if rsum is None or s > rsum:
            rsum, rj = s, j
    cross = (lsum + rsum, li, rj)             # the best run that crosses the middle
    top = left
    if right[0] > top[0]:
        top = right
    if cross[0] > top[0]:
        top = cross
    return top


a = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
s, i, j = best(a, 0, len(a) - 1)
print("best sum", s, "from index", i, "to", j, ":", " ".join(map(str, a[i:j + 1])))
s, i, j = best([-3, -1, -2], 0, 2)
print("all negative: best sum", s, "at index", i)
''', js=r'''
function best(a, lo, hi) {
  if (lo === hi) return [a[lo], lo, lo];
  const mid = Math.floor((lo + hi) / 2);
  const left = best(a, lo, mid);             // best that stays in the left half
  const right = best(a, mid + 1, hi);        // best that stays in the right half
  let s = 0, lsum = null, li = mid;
  for (let i = mid; i >= lo; i--) {          // best run ending exactly at mid
    s += a[i];
    if (lsum === null || s > lsum) { lsum = s; li = i; }
  }
  let rsum = null, rj = mid + 1;
  s = 0;
  for (let j = mid + 1; j <= hi; j++) {      // best run starting exactly at mid + 1
    s += a[j];
    if (rsum === null || s > rsum) { rsum = s; rj = j; }
  }
  const cross = [lsum + rsum, li, rj];       // the best run that crosses the middle
  let top = left;
  if (right[0] > top[0]) top = right;
  if (cross[0] > top[0]) top = cross;
  return top;
}

const a = [-2, 1, -3, 4, -1, 2, 1, -5, 4];
const [s, i, j] = best(a, 0, a.length - 1);
console.log("best sum", s, "from index", i, "to", j, ":", a.slice(i, j + 1).join(" "));
const neg = best([-3, -1, -2], 0, 2);
console.log("all negative: best sum", neg[0], "at index", neg[1]);
''', java=r'''
public class MaxSubarrayDC {
    static int[] best(int[] a, int lo, int hi) {
        if (lo == hi) return new int[]{a[lo], lo, lo};
        int mid = (lo + hi) / 2;
        int[] left = best(a, lo, mid);               // best that stays in the left half
        int[] right = best(a, mid + 1, hi);          // best that stays in the right half
        int s = 0, lsum = Integer.MIN_VALUE, li = mid;
        for (int i = mid; i >= lo; i--) {            // best run ending exactly at mid
            s += a[i];
            if (s > lsum) { lsum = s; li = i; }
        }
        int rsum = Integer.MIN_VALUE, rj = mid + 1;
        s = 0;
        for (int j = mid + 1; j <= hi; j++) {        // best run starting exactly at mid + 1
            s += a[j];
            if (s > rsum) { rsum = s; rj = j; }
        }
        int[] cross = {lsum + rsum, li, rj};         // the best run that crosses the middle
        int[] top = left;
        if (right[0] > top[0]) top = right;
        if (cross[0] > top[0]) top = cross;
        return top;
    }

    public static void main(String[] args) {
        int[] a = {-2, 1, -3, 4, -1, 2, 1, -5, 4};
        int[] r = best(a, 0, a.length - 1);
        StringBuilder sb = new StringBuilder();
        for (int k = r[1]; k <= r[2]; k++) sb.append(k > r[1] ? " " : "").append(a[k]);
        System.out.println("best sum " + r[0] + " from index " + r[1] + " to " + r[2] + " : " + sb);
        int[] neg = best(new int[]{-3, -1, -2}, 0, 2);
        System.out.println("all negative: best sum " + neg[0] + " at index " + neg[1]);
    }
}
''', ts=r'''
function best(a: number[], lo: number, hi: number): [number, number, number] {
  if (lo === hi) return [a[lo], lo, lo];
  const mid = Math.floor((lo + hi) / 2);
  const left = best(a, lo, mid);             // best that stays in the left half
  const right = best(a, mid + 1, hi);        // best that stays in the right half
  let s = 0, lsum = -Infinity, li = mid;
  for (let i = mid; i >= lo; i--) {          // best run ending exactly at mid
    s += a[i];
    if (s > lsum) { lsum = s; li = i; }
  }
  let rsum = -Infinity, rj = mid + 1;
  s = 0;
  for (let j = mid + 1; j <= hi; j++) {      // best run starting exactly at mid + 1
    s += a[j];
    if (s > rsum) { rsum = s; rj = j; }
  }
  const cross: [number, number, number] = [lsum + rsum, li, rj];   // the best run that crosses the middle
  let top = left;
  if (right[0] > top[0]) top = right;
  if (cross[0] > top[0]) top = cross;
  return top;
}

const a = [-2, 1, -3, 4, -1, 2, 1, -5, 4];
const [s, i, j] = best(a, 0, a.length - 1);
console.log("best sum", s, "from index", i, "to", j, ":", a.slice(i, j + 1).join(" "));
const neg = best([-3, -1, -2], 0, 2);
console.log("all negative: best sum", neg[0], "at index", neg[1]);
''')

t.code('closest', py=r'''
POINTS = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4), (30, 25), (22, 18)]
checks = 0


def dist2(p, q):                              # squared distance keeps everything in whole numbers
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def brute(ps):
    global checks
    best = None
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            checks += 1
            d = dist2(ps[i], ps[j])
            if best is None or d < best:
                best = d
    return best


def closest(ps):                              # ps is sorted by x
    global checks
    if len(ps) <= 3:
        return brute(ps)
    mid = len(ps) // 2
    mid_x = ps[mid][0]
    d = min(closest(ps[:mid]), closest(ps[mid:]))
    # only points near the dividing line can form a closer pair across it
    strip = sorted([p for p in ps if (p[0] - mid_x) ** 2 < d], key=lambda p: p[1])
    for i in range(len(strip)):
        j = i + 1
        while j < len(strip) and (strip[j][1] - strip[i][1]) ** 2 < d:
            checks += 1
            d = min(d, dist2(strip[i], strip[j]))
            j += 1
    return d


print("divide and conquer: squared distance", closest(sorted(POINTS)), "after", checks, "checks")
checks = 0
print("brute force:        squared distance", brute(POINTS), "after", checks, "checks")
''', js=r'''
const POINTS = [[2, 3], [12, 30], [40, 50], [5, 1], [12, 10], [3, 4], [30, 25], [22, 18]];
let checks = 0;

const dist2 = (p, q) => (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2;   // whole numbers only

function brute(ps) {
  let best = null;
  for (let i = 0; i < ps.length; i++) {
    for (let j = i + 1; j < ps.length; j++) {
      checks++;
      const d = dist2(ps[i], ps[j]);
      if (best === null || d < best) best = d;
    }
  }
  return best;
}

function closest(ps) {                       // ps is sorted by x
  if (ps.length <= 3) return brute(ps);
  const mid = Math.floor(ps.length / 2), midX = ps[mid][0];
  let d = Math.min(closest(ps.slice(0, mid)), closest(ps.slice(mid)));
  // only points near the dividing line can form a closer pair across it
  const strip = ps.filter(p => (p[0] - midX) ** 2 < d).sort((p, q) => p[1] - q[1]);
  for (let i = 0; i < strip.length; i++) {
    for (let j = i + 1; j < strip.length && (strip[j][1] - strip[i][1]) ** 2 < d; j++) {
      checks++;
      d = Math.min(d, dist2(strip[i], strip[j]));
    }
  }
  return d;
}

const byX = [...POINTS].sort((p, q) => p[0] - q[0] || p[1] - q[1]);
console.log("divide and conquer: squared distance", closest(byX), "after", checks, "checks");
checks = 0;
console.log("brute force:        squared distance", brute(POINTS), "after", checks, "checks");
''', java=r'''
import java.util.*;

public class ClosestPair {
    static int checks = 0;

    static int dist2(int[] p, int[] q) {               // whole numbers only
        return (p[0] - q[0]) * (p[0] - q[0]) + (p[1] - q[1]) * (p[1] - q[1]);
    }

    static int brute(List<int[]> ps) {
        int best = Integer.MAX_VALUE;
        for (int i = 0; i < ps.size(); i++) {
            for (int j = i + 1; j < ps.size(); j++) {
                checks++;
                best = Math.min(best, dist2(ps.get(i), ps.get(j)));
            }
        }
        return best;
    }

    static int closest(List<int[]> ps) {               // ps is sorted by x
        if (ps.size() <= 3) return brute(ps);
        int mid = ps.size() / 2, midX = ps.get(mid)[0];
        int d = Math.min(closest(ps.subList(0, mid)), closest(ps.subList(mid, ps.size())));
        // only points near the dividing line can form a closer pair across it
        List<int[]> strip = new ArrayList<>();
        for (int[] p : ps) if ((p[0] - midX) * (p[0] - midX) < d) strip.add(p);
        strip.sort(Comparator.comparingInt(p -> p[1]));
        for (int i = 0; i < strip.size(); i++) {
            for (int j = i + 1; j < strip.size(); j++) {
                int dy = strip.get(j)[1] - strip.get(i)[1];
                if (dy * dy >= d) break;
                checks++;
                d = Math.min(d, dist2(strip.get(i), strip.get(j)));
            }
        }
        return d;
    }

    public static void main(String[] args) {
        int[][] raw = {{2, 3}, {12, 30}, {40, 50}, {5, 1}, {12, 10}, {3, 4}, {30, 25}, {22, 18}};
        List<int[]> pts = new ArrayList<>(Arrays.asList(raw));
        List<int[]> byX = new ArrayList<>(pts);
        byX.sort((p, q) -> p[0] != q[0] ? p[0] - q[0] : p[1] - q[1]);
        int d = closest(byX);
        System.out.println("divide and conquer: squared distance " + d + " after " + checks + " checks");
        checks = 0;
        d = brute(pts);
        System.out.println("brute force:        squared distance " + d + " after " + checks + " checks");
    }
}
''', ts=r'''
type Pt = [number, number];
const POINTS: Pt[] = [[2, 3], [12, 30], [40, 50], [5, 1], [12, 10], [3, 4], [30, 25], [22, 18]];
let checks = 0;

const dist2 = (p: Pt, q: Pt): number => (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2;   // whole numbers only

function brute(ps: Pt[]): number {
  let best = Infinity;
  for (let i = 0; i < ps.length; i++) {
    for (let j = i + 1; j < ps.length; j++) {
      checks++;
      best = Math.min(best, dist2(ps[i], ps[j]));
    }
  }
  return best;
}

function closest(ps: Pt[]): number {         // ps is sorted by x
  if (ps.length <= 3) return brute(ps);
  const mid = Math.floor(ps.length / 2), midX = ps[mid][0];
  let d = Math.min(closest(ps.slice(0, mid)), closest(ps.slice(mid)));
  // only points near the dividing line can form a closer pair across it
  const strip = ps.filter(p => (p[0] - midX) ** 2 < d).sort((p, q) => p[1] - q[1]);
  for (let i = 0; i < strip.length; i++) {
    for (let j = i + 1; j < strip.length && (strip[j][1] - strip[i][1]) ** 2 < d; j++) {
      checks++;
      d = Math.min(d, dist2(strip[i], strip[j]));
    }
  }
  return d;
}

const byX = [...POINTS].sort((p, q) => p[0] - q[0] || p[1] - q[1]);
console.log("divide and conquer: squared distance", closest(byX), "after", checks, "checks");
checks = 0;
console.log("brute force:        squared distance", brute(POINTS), "after", checks, "checks");
''')

t.code('karatsuba', py=r'''
mults = 0


def karatsuba(x, y):
    global mults
    if x < 10 or y < 10:
        mults += 1                            # a one digit multiplication
        return x * y
    m = max(len(str(x)), len(str(y))) // 2
    p = 10 ** m
    a, b = divmod(x, p)                       # x = a * p + b
    c, d = divmod(y, p)                       # y = c * p + d
    ac = karatsuba(a, c)
    bd = karatsuba(b, d)
    middle = karatsuba(a + b, c + d) - ac - bd    # three products instead of four
    return ac * p * p + middle * p + bd


for x, y in ((1234, 5678), (12345678, 87654321)):
    mults = 0
    r = karatsuba(x, y)
    print(x, "x", y, "=", r, " correct:", "yes" if r == x * y else "no", " small multiplications:", mults)
''', js=r'''
let mults = 0;

function karatsuba(x, y) {
  if (x < 10 || y < 10) {
    mults++;                                 // a one digit multiplication
    return x * y;
  }
  const m = Math.floor(Math.max(String(x).length, String(y).length) / 2);
  const p = 10 ** m;
  const a = Math.floor(x / p), b = x % p;    // x = a * p + b
  const c = Math.floor(y / p), d = y % p;    // y = c * p + d
  const ac = karatsuba(a, c);
  const bd = karatsuba(b, d);
  const middle = karatsuba(a + b, c + d) - ac - bd;   // three products instead of four
  return ac * p * p + middle * p + bd;
}

for (const [x, y] of [[1234, 5678], [12345678, 87654321]]) {
  mults = 0;
  const r = karatsuba(x, y);
  console.log(x, "x", y, "=", r, " correct:", BigInt(r) === BigInt(x) * BigInt(y) ? "yes" : "no", " small multiplications:", mults);
}
''', java=r'''
public class Karatsuba {
    static int mults = 0;

    static long karatsuba(long x, long y) {
        if (x < 10 || y < 10) {
            mults++;                                     // a one digit multiplication
            return x * y;
        }
        int m = Math.max(Long.toString(x).length(), Long.toString(y).length()) / 2;
        long p = 1;
        for (int i = 0; i < m; i++) p *= 10;
        long a = x / p, b = x % p;                       // x = a * p + b
        long c = y / p, d = y % p;                       // y = c * p + d
        long ac = karatsuba(a, c);
        long bd = karatsuba(b, d);
        long middle = karatsuba(a + b, c + d) - ac - bd; // three products instead of four
        return ac * p * p + middle * p + bd;
    }

    public static void main(String[] args) {
        long[][] tests = {{1234, 5678}, {12345678, 87654321}};
        for (long[] t : tests) {
            mults = 0;
            long r = karatsuba(t[0], t[1]);
            System.out.println(t[0] + " x " + t[1] + " = " + r + "  correct: " + (r == t[0] * t[1] ? "yes" : "no") + "  small multiplications: " + mults);
        }
    }
}
''', ts=r'''
let mults = 0;

function karatsuba(x: number, y: number): number {
  if (x < 10 || y < 10) {
    mults++;                                 // a one digit multiplication
    return x * y;
  }
  const m = Math.floor(Math.max(String(x).length, String(y).length) / 2);
  const p = 10 ** m;
  const a = Math.floor(x / p), b = x % p;    // x = a * p + b
  const c = Math.floor(y / p), d = y % p;    // y = c * p + d
  const ac = karatsuba(a, c);
  const bd = karatsuba(b, d);
  const middle = karatsuba(a + b, c + d) - ac - bd;   // three products instead of four
  return ac * p * p + middle * p + bd;
}

for (const [x, y] of [[1234, 5678], [12345678, 87654321]]) {
  mults = 0;
  const r = karatsuba(x, y);
  console.log(x, "x", y, "=", r, " correct:", BigInt(r) === BigInt(x) * BigInt(y) ? "yes" : "no", " small multiplications:", mults);
}
''')

# ---------------------------------------------------------------- LeetCode practice programs
t.code('p_major', py=r'''
def majority_element(nums):
    def count(x, lo, hi):
        return sum(1 for i in range(lo, hi + 1) if nums[i] == x)

    def go(lo, hi):
        if lo == hi:
            return nums[lo]
        mid = (lo + hi) // 2
        left, right = go(lo, mid), go(mid + 1, hi)
        if left == right:
            return left                       # both halves agree
        # the overall majority must win at least one half, so only these two can be it
        return left if count(left, lo, hi) > count(right, lo, hi) else right

    return go(0, len(nums) - 1)


print(majority_element([3, 2, 3]))
print(majority_element([2, 2, 1, 1, 1, 2, 2]))
print(majority_element([5]))
''', js=r'''
function majorityElement(nums) {
  const count = (x, lo, hi) => { let c = 0; for (let i = lo; i <= hi; i++) if (nums[i] === x) c++; return c; };
  function go(lo, hi) {
    if (lo === hi) return nums[lo];
    const mid = Math.floor((lo + hi) / 2);
    const left = go(lo, mid), right = go(mid + 1, hi);
    if (left === right) return left;         // both halves agree
    // the overall majority must win at least one half, so only these two can be it
    return count(left, lo, hi) > count(right, lo, hi) ? left : right;
  }
  return go(0, nums.length - 1);
}

console.log(majorityElement([3, 2, 3]));
console.log(majorityElement([2, 2, 1, 1, 1, 2, 2]));
console.log(majorityElement([5]));
''', java=r'''
public class MajorityElement {
    static int[] nums;

    static int count(int x, int lo, int hi) {
        int c = 0;
        for (int i = lo; i <= hi; i++) if (nums[i] == x) c++;
        return c;
    }

    static int go(int lo, int hi) {
        if (lo == hi) return nums[lo];
        int mid = (lo + hi) / 2;
        int left = go(lo, mid), right = go(mid + 1, hi);
        if (left == right) return left;                  // both halves agree
        // the overall majority must win at least one half, so only these two can be it
        return count(left, lo, hi) > count(right, lo, hi) ? left : right;
    }

    static int majorityElement(int[] a) {
        nums = a;
        return go(0, a.length - 1);
    }

    public static void main(String[] args) {
        System.out.println(majorityElement(new int[]{3, 2, 3}));
        System.out.println(majorityElement(new int[]{2, 2, 1, 1, 1, 2, 2}));
        System.out.println(majorityElement(new int[]{5}));
    }
}
''', ts=r'''
function majorityElement(nums: number[]): number {
  const count = (x: number, lo: number, hi: number): number => { let c = 0; for (let i = lo; i <= hi; i++) if (nums[i] === x) c++; return c; };
  function go(lo: number, hi: number): number {
    if (lo === hi) return nums[lo];
    const mid = Math.floor((lo + hi) / 2);
    const left = go(lo, mid), right = go(mid + 1, hi);
    if (left === right) return left;         // both halves agree
    // the overall majority must win at least one half, so only these two can be it
    return count(left, lo, hi) > count(right, lo, hi) ? left : right;
  }
  return go(0, nums.length - 1);
}

console.log(majorityElement([3, 2, 3]));
console.log(majorityElement([2, 2, 1, 1, 1, 2, 2]));
console.log(majorityElement([5]));
''')

t.code('p_bst', py=r'''
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def sorted_array_to_bst(nums):
    def build(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2                  # the middle value becomes the root
        return TreeNode(nums[mid], build(lo, mid - 1), build(mid + 1, hi))

    return build(0, len(nums) - 1)


def preorder(node, out):
    if node:
        out.append(str(node.val))
        preorder(node.left, out)
        preorder(node.right, out)
    return out


def height(node):
    return 0 if node is None else 1 + max(height(node.left), height(node.right))


for nums in ([-10, -3, 0, 5, 9], [1, 3], list(range(1, 16))):
    root = sorted_array_to_bst(nums)
    print("preorder", " ".join(preorder(root, [])), " height", height(root))
''', js=r'''
class TreeNode {
  constructor(val, left = null, right = null) {
    this.val = val;
    this.left = left;
    this.right = right;
  }
}

function sortedArrayToBST(nums) {
  function build(lo, hi) {
    if (lo > hi) return null;
    const mid = Math.floor((lo + hi) / 2);   // the middle value becomes the root
    return new TreeNode(nums[mid], build(lo, mid - 1), build(mid + 1, hi));
  }
  return build(0, nums.length - 1);
}

const preorder = (node, out) => { if (node) { out.push(node.val); preorder(node.left, out); preorder(node.right, out); } return out; };
const height = node => (node === null ? 0 : 1 + Math.max(height(node.left), height(node.right)));

for (const nums of [[-10, -3, 0, 5, 9], [1, 3], Array.from({ length: 15 }, (_, i) => i + 1)]) {
  const root = sortedArrayToBST(nums);
  console.log("preorder", preorder(root, []).join(" "), " height", height(root));
}
''', java=r'''
import java.util.*;

public class SortedToBST {
    static class TreeNode {
        int val;
        TreeNode left, right;
        TreeNode(int v, TreeNode l, TreeNode r) { val = v; left = l; right = r; }
    }

    static int[] nums;

    static TreeNode build(int lo, int hi) {
        if (lo > hi) return null;
        int mid = (lo + hi) / 2;                         // the middle value becomes the root
        return new TreeNode(nums[mid], build(lo, mid - 1), build(mid + 1, hi));
    }

    static void preorder(TreeNode n, List<String> out) {
        if (n == null) return;
        out.add(String.valueOf(n.val));
        preorder(n.left, out);
        preorder(n.right, out);
    }

    static int height(TreeNode n) { return n == null ? 0 : 1 + Math.max(height(n.left), height(n.right)); }

    public static void main(String[] args) {
        int[] fifteen = new int[15];
        for (int i = 0; i < 15; i++) fifteen[i] = i + 1;
        for (int[] a : new int[][]{{-10, -3, 0, 5, 9}, {1, 3}, fifteen}) {
            nums = a;
            TreeNode root = build(0, a.length - 1);
            List<String> out = new ArrayList<>();
            preorder(root, out);
            System.out.println("preorder " + String.join(" ", out) + "  height " + height(root));
        }
    }
}
''', ts=r'''
class TreeNode {
  val: number;
  left: TreeNode | null;
  right: TreeNode | null;
  constructor(val: number, left: TreeNode | null = null, right: TreeNode | null = null) {
    this.val = val;
    this.left = left;
    this.right = right;
  }
}

function sortedArrayToBST(nums: number[]): TreeNode | null {
  function build(lo: number, hi: number): TreeNode | null {
    if (lo > hi) return null;
    const mid = Math.floor((lo + hi) / 2);   // the middle value becomes the root
    return new TreeNode(nums[mid], build(lo, mid - 1), build(mid + 1, hi));
  }
  return build(0, nums.length - 1);
}

const preorder = (node: TreeNode | null, out: number[]): number[] => { if (node) { out.push(node.val); preorder(node.left, out); preorder(node.right, out); } return out; };
const height = (node: TreeNode | null): number => (node === null ? 0 : 1 + Math.max(height(node.left), height(node.right)));

for (const nums of [[-10, -3, 0, 5, 9], [1, 3], Array.from({ length: 15 }, (_, i) => i + 1)]) {
  const root = sortedArrayToBST(nums);
  console.log("preorder", preorder(root, []).join(" "), " height", height(root));
}
''')

t.code('p_maxsub', py=r'''
def max_sub_array(nums):
    def go(lo, hi):
        if lo == hi:
            return nums[lo]
        mid = (lo + hi) // 2
        best_left, best_right = go(lo, mid), go(mid + 1, hi)
        s, cross_left = 0, nums[mid]
        for i in range(mid, lo - 1, -1):      # grow leftwards from the middle
            s += nums[i]
            cross_left = max(cross_left, s)
        s, cross_right = 0, nums[mid + 1]
        for j in range(mid + 1, hi + 1):      # grow rightwards from the middle
            s += nums[j]
            cross_right = max(cross_right, s)
        return max(best_left, best_right, cross_left + cross_right)

    return go(0, len(nums) - 1)


def kadane(nums):                             # the O(n) scan, to check the answer
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best


for nums in ([-2, 1, -3, 4, -1, 2, 1, -5, 4], [1], [5, 4, -1, 7, 8], [-3, -1, -2]):
    print(max_sub_array(nums), " Kadane agrees:", "yes" if max_sub_array(nums) == kadane(nums) else "no")
''', js=r'''
function maxSubArray(nums) {
  function go(lo, hi) {
    if (lo === hi) return nums[lo];
    const mid = Math.floor((lo + hi) / 2);
    const bestLeft = go(lo, mid), bestRight = go(mid + 1, hi);
    let s = 0, crossLeft = nums[mid];
    for (let i = mid; i >= lo; i--) { s += nums[i]; crossLeft = Math.max(crossLeft, s); }       // grow leftwards
    s = 0;
    let crossRight = nums[mid + 1];
    for (let j = mid + 1; j <= hi; j++) { s += nums[j]; crossRight = Math.max(crossRight, s); } // grow rightwards
    return Math.max(bestLeft, bestRight, crossLeft + crossRight);
  }
  return go(0, nums.length - 1);
}

function kadane(nums) {                      // the O(n) scan, to check the answer
  let best = nums[0], cur = nums[0];
  for (const x of nums.slice(1)) { cur = Math.max(x, cur + x); best = Math.max(best, cur); }
  return best;
}

for (const nums of [[-2, 1, -3, 4, -1, 2, 1, -5, 4], [1], [5, 4, -1, 7, 8], [-3, -1, -2]]) {
  console.log(maxSubArray(nums), " Kadane agrees:", maxSubArray(nums) === kadane(nums) ? "yes" : "no");
}
''', java=r'''
public class MaxSubArray {
    static int[] nums;

    static int go(int lo, int hi) {
        if (lo == hi) return nums[lo];
        int mid = (lo + hi) / 2;
        int bestLeft = go(lo, mid), bestRight = go(mid + 1, hi);
        int s = 0, crossLeft = nums[mid];
        for (int i = mid; i >= lo; i--) { s += nums[i]; crossLeft = Math.max(crossLeft, s); }        // grow leftwards
        s = 0;
        int crossRight = nums[mid + 1];
        for (int j = mid + 1; j <= hi; j++) { s += nums[j]; crossRight = Math.max(crossRight, s); }  // grow rightwards
        return Math.max(Math.max(bestLeft, bestRight), crossLeft + crossRight);
    }

    static int kadane(int[] a) {                         // the O(n) scan, to check the answer
        int best = a[0], cur = a[0];
        for (int i = 1; i < a.length; i++) { cur = Math.max(a[i], cur + a[i]); best = Math.max(best, cur); }
        return best;
    }

    public static void main(String[] args) {
        int[][] tests = {{-2, 1, -3, 4, -1, 2, 1, -5, 4}, {1}, {5, 4, -1, 7, 8}, {-3, -1, -2}};
        for (int[] a : tests) {
            nums = a;
            int r = go(0, a.length - 1);
            System.out.println(r + "  Kadane agrees: " + (r == kadane(a) ? "yes" : "no"));
        }
    }
}
''', ts=r'''
function maxSubArray(nums: number[]): number {
  function go(lo: number, hi: number): number {
    if (lo === hi) return nums[lo];
    const mid = Math.floor((lo + hi) / 2);
    const bestLeft = go(lo, mid), bestRight = go(mid + 1, hi);
    let s = 0, crossLeft = nums[mid];
    for (let i = mid; i >= lo; i--) { s += nums[i]; crossLeft = Math.max(crossLeft, s); }       // grow leftwards
    s = 0;
    let crossRight = nums[mid + 1];
    for (let j = mid + 1; j <= hi; j++) { s += nums[j]; crossRight = Math.max(crossRight, s); } // grow rightwards
    return Math.max(bestLeft, bestRight, crossLeft + crossRight);
  }
  return go(0, nums.length - 1);
}

function kadane(nums: number[]): number {    // the O(n) scan, to check the answer
  let best = nums[0], cur = nums[0];
  for (const x of nums.slice(1)) { cur = Math.max(x, cur + x); best = Math.max(best, cur); }
  return best;
}

for (const nums of [[-2, 1, -3, 4, -1, 2, 1, -5, 4], [1], [5, 4, -1, 7, 8], [-3, -1, -2]]) {
  console.log(maxSubArray(nums), " Kadane agrees:", maxSubArray(nums) === kadane(nums) ? "yes" : "no");
}
''')

t.code('p_kth', py=r'''
def find_kth_largest(nums, k):
    a = nums[:]
    target = len(a) - k                       # k-th largest = (n - k)-th smallest, from 0
    lo, hi = 0, len(a) - 1
    while True:
        pivot, store = a[hi], lo
        for i in range(lo, hi):
            if a[i] < pivot:
                a[i], a[store] = a[store], a[i]
                store += 1
        a[store], a[hi] = a[hi], a[store]
        if store == target:
            return a[store]
        if store < target:
            lo = store + 1                    # throw away the left part
        else:
            hi = store - 1                    # throw away the right part


print(find_kth_largest([3, 2, 1, 5, 6, 4], 2))
print(find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))
print(find_kth_largest([7], 1))
''', js=r'''
function findKthLargest(nums, k) {
  const a = [...nums], target = a.length - k;   // k-th largest = (n - k)-th smallest, from 0
  let lo = 0, hi = a.length - 1;
  while (true) {
    const pivot = a[hi];
    let store = lo;
    for (let i = lo; i < hi; i++) {
      if (a[i] < pivot) { [a[i], a[store]] = [a[store], a[i]]; store++; }
    }
    [a[store], a[hi]] = [a[hi], a[store]];
    if (store === target) return a[store];
    if (store < target) lo = store + 1;      // throw away the left part
    else hi = store - 1;                     // throw away the right part
  }
}

console.log(findKthLargest([3, 2, 1, 5, 6, 4], 2));
console.log(findKthLargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4));
console.log(findKthLargest([7], 1));
''', java=r'''
public class KthLargest {
    static int findKthLargest(int[] nums, int k) {
        int[] a = nums.clone();
        int target = a.length - k;                       // k-th largest = (n - k)-th smallest, from 0
        int lo = 0, hi = a.length - 1;
        while (true) {
            int pivot = a[hi], store = lo;
            for (int i = lo; i < hi; i++) {
                if (a[i] < pivot) { int t = a[i]; a[i] = a[store]; a[store] = t; store++; }
            }
            int t = a[store]; a[store] = a[hi]; a[hi] = t;
            if (store == target) return a[store];
            if (store < target) lo = store + 1;          // throw away the left part
            else hi = store - 1;                         // throw away the right part
        }
    }

    public static void main(String[] args) {
        System.out.println(findKthLargest(new int[]{3, 2, 1, 5, 6, 4}, 2));
        System.out.println(findKthLargest(new int[]{3, 2, 3, 1, 2, 4, 5, 5, 6}, 4));
        System.out.println(findKthLargest(new int[]{7}, 1));
    }
}
''', ts=r'''
function findKthLargest(nums: number[], k: number): number {
  const a = [...nums], target = a.length - k;   // k-th largest = (n - k)-th smallest, from 0
  let lo = 0, hi = a.length - 1;
  while (true) {
    const pivot = a[hi];
    let store = lo;
    for (let i = lo; i < hi; i++) {
      if (a[i] < pivot) { [a[i], a[store]] = [a[store], a[i]]; store++; }
    }
    [a[store], a[hi]] = [a[hi], a[store]];
    if (store === target) return a[store];
    if (store < target) lo = store + 1;      // throw away the left part
    else hi = store - 1;                     // throw away the right part
  }
}

console.log(findKthLargest([3, 2, 1, 5, 6, 4], 2));
console.log(findKthLargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4));
console.log(findKthLargest([7], 1));
''')

t.code('p_sortlist', py=r'''
class ListNode:
    def __init__(self, val, next=None):
        self.val, self.next = val, next


def sort_list(head):
    if head is None or head.next is None:
        return head
    slow, fast = head, head.next              # find the middle with slow and fast pointers
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    right = slow.next
    slow.next = None                          # cut the list into two halves
    a, b = sort_list(head), sort_list(right)
    dummy = tail = ListNode(0)
    while a and b:                            # merge two sorted lists
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next


def build(vals):
    head = None
    for v in reversed(vals):
        head = ListNode(v, head)
    return head


def show(node):
    out = []
    while node:
        out.append(str(node.val))
        node = node.next
    return " ".join(out) or "(empty)"


for vals in ([4, 2, 1, 3], [-1, 5, 3, 4, 0], []):
    print(show(sort_list(build(vals))))
''', js=r'''
class ListNode {
  constructor(val, next = null) {
    this.val = val;
    this.next = next;
  }
}

function sortList(head) {
  if (head === null || head.next === null) return head;
  let slow = head, fast = head.next;          // find the middle with slow and fast pointers
  while (fast && fast.next) { slow = slow.next; fast = fast.next.next; }
  const right = slow.next;
  slow.next = null;                           // cut the list into two halves
  let a = sortList(head), b = sortList(right);
  const dummy = new ListNode(0);
  let tail = dummy;
  while (a && b) {                            // merge two sorted lists
    if (a.val <= b.val) { tail.next = a; a = a.next; }
    else { tail.next = b; b = b.next; }
    tail = tail.next;
  }
  tail.next = a || b;
  return dummy.next;
}

const build = vals => vals.reduceRight((head, v) => new ListNode(v, head), null);
const show = node => { const out = []; for (; node; node = node.next) out.push(node.val); return out.join(" ") || "(empty)"; };

for (const vals of [[4, 2, 1, 3], [-1, 5, 3, 4, 0], []]) console.log(show(sortList(build(vals))));
''', java=r'''
import java.util.*;

public class SortList {
    static class ListNode {
        int val;
        ListNode next;
        ListNode(int v, ListNode n) { val = v; next = n; }
    }

    static ListNode sortList(ListNode head) {
        if (head == null || head.next == null) return head;
        ListNode slow = head, fast = head.next;          // find the middle with slow and fast pointers
        while (fast != null && fast.next != null) { slow = slow.next; fast = fast.next.next; }
        ListNode right = slow.next;
        slow.next = null;                                // cut the list into two halves
        ListNode a = sortList(head), b = sortList(right);
        ListNode dummy = new ListNode(0, null), tail = dummy;
        while (a != null && b != null) {                 // merge two sorted lists
            if (a.val <= b.val) { tail.next = a; a = a.next; }
            else { tail.next = b; b = b.next; }
            tail = tail.next;
        }
        tail.next = (a != null) ? a : b;
        return dummy.next;
    }

    static ListNode build(int[] vals) {
        ListNode head = null;
        for (int i = vals.length - 1; i >= 0; i--) head = new ListNode(vals[i], head);
        return head;
    }

    static String show(ListNode n) {
        StringJoiner sj = new StringJoiner(" ");
        for (; n != null; n = n.next) sj.add(String.valueOf(n.val));
        return sj.length() == 0 ? "(empty)" : sj.toString();
    }

    public static void main(String[] args) {
        for (int[] vals : new int[][]{{4, 2, 1, 3}, {-1, 5, 3, 4, 0}, {}}) System.out.println(show(sortList(build(vals))));
    }
}
''', ts=r'''
class ListNode {
  val: number;
  next: ListNode | null;
  constructor(val: number, next: ListNode | null = null) {
    this.val = val;
    this.next = next;
  }
}

function sortList(head: ListNode | null): ListNode | null {
  if (head === null || head.next === null) return head;
  let slow: ListNode = head, fast: ListNode | null = head.next;   // find the middle with slow and fast pointers
  while (fast && fast.next) { slow = slow.next as ListNode; fast = fast.next.next; }
  const right = slow.next;
  slow.next = null;                           // cut the list into two halves
  let a = sortList(head), b = sortList(right);
  const dummy = new ListNode(0);
  let tail = dummy;
  while (a && b) {                            // merge two sorted lists
    if (a.val <= b.val) { tail.next = a; a = a.next; }
    else { tail.next = b; b = b.next; }
    tail = tail.next;
  }
  tail.next = a || b;
  return dummy.next;
}

const build = (vals: number[]): ListNode | null => vals.reduceRight<ListNode | null>((head, v) => new ListNode(v, head), null);
const show = (node: ListNode | null): string => { const out: number[] = []; for (; node; node = node.next) out.push(node.val); return out.join(" ") || "(empty)"; };

for (const vals of [[4, 2, 1, 3], [-1, 5, 3, 4, 0], []]) console.log(show(sortList(build(vals))));
''')

t.code('p_ways', py=r'''
from functools import lru_cache


def diff_ways_to_compute(expression):
    @lru_cache(maxsize=None)
    def go(s):
        results = []
        for i, ch in enumerate(s):
            if ch in "+-*":                   # split at every operator
                for a in go(s[:i]):           # every value of the left side
                    for b in go(s[i + 1:]):   # every value of the right side
                        results.append(a + b if ch == "+" else a - b if ch == "-" else a * b)
        return results or [int(s)]            # no operator: it is a plain number

    return go(expression)


for e in ["2-1-1", "2*3-4*5", "1+2*3"]:
    print(e, ":", " ".join(map(str, sorted(diff_ways_to_compute(e)))))
''', js=r'''
function diffWaysToCompute(expression) {
  const memo = new Map();
  function go(s) {
    if (memo.has(s)) return memo.get(s);
    const results = [];
    for (let i = 0; i < s.length; i++) {
      const ch = s[i];
      if ("+-*".includes(ch)) {               // split at every operator
        for (const a of go(s.slice(0, i))) {  // every value of the left side
          for (const b of go(s.slice(i + 1))) {
            results.push(ch === "+" ? a + b : ch === "-" ? a - b : a * b);
          }
        }
      }
    }
    if (results.length === 0) results.push(Number(s));   // no operator: it is a plain number
    memo.set(s, results);
    return results;
  }
  return go(expression);
}

for (const e of ["2-1-1", "2*3-4*5", "1+2*3"]) {
  console.log(e, ":", [...diffWaysToCompute(e)].sort((x, y) => x - y).join(" "));
}
''', java=r'''
import java.util.*;

public class AddParentheses {
    static Map<String, List<Integer>> memo = new HashMap<>();

    static List<Integer> go(String s) {
        if (memo.containsKey(s)) return memo.get(s);
        List<Integer> results = new ArrayList<>();
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch == '+' || ch == '-' || ch == '*') {        // split at every operator
                for (int a : go(s.substring(0, i))) {        // every value of the left side
                    for (int b : go(s.substring(i + 1))) {
                        results.add(ch == '+' ? a + b : ch == '-' ? a - b : a * b);
                    }
                }
            }
        }
        if (results.isEmpty()) results.add(Integer.parseInt(s));   // no operator: it is a plain number
        memo.put(s, results);
        return results;
    }

    public static void main(String[] args) {
        for (String e : new String[]{"2-1-1", "2*3-4*5", "1+2*3"}) {
            List<Integer> r = new ArrayList<>(go(e));
            Collections.sort(r);
            StringJoiner sj = new StringJoiner(" ");
            for (int x : r) sj.add(String.valueOf(x));
            System.out.println(e + " : " + sj);
        }
    }
}
''', ts=r'''
function diffWaysToCompute(expression: string): number[] {
  const memo = new Map<string, number[]>();
  function go(s: string): number[] {
    const known = memo.get(s);
    if (known) return known;
    const results: number[] = [];
    for (let i = 0; i < s.length; i++) {
      const ch = s[i];
      if ("+-*".includes(ch)) {               // split at every operator
        for (const a of go(s.slice(0, i))) {  // every value of the left side
          for (const b of go(s.slice(i + 1))) {
            results.push(ch === "+" ? a + b : ch === "-" ? a - b : a * b);
          }
        }
      }
    }
    if (results.length === 0) results.push(Number(s));   // no operator: it is a plain number
    memo.set(s, results);
    return results;
  }
  return go(expression);
}

for (const e of ["2-1-1", "2*3-4*5", "1+2*3"]) {
  console.log(e, ":", [...diffWaysToCompute(e)].sort((x, y) => x - y).join(" "));
}
''')

t.code('p_revpairs', py=r'''
def reverse_pairs(nums):
    def go(a):
        if len(a) <= 1:
            return a, 0
        mid = len(a) // 2
        left, x = go(a[:mid])
        right, y = go(a[mid:])
        count, j = 0, 0
        for v in left:                        # both halves are sorted, so j only moves forward
            while j < len(right) and v > 2 * right[j]:
                j += 1
            count += j
        merged, i, k = [], 0, 0
        while i < len(left) and k < len(right):
            if left[i] <= right[k]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[k])
                k += 1
        return merged + left[i:] + right[k:], x + y + count

    return go(nums)[1]


print(reverse_pairs([1, 3, 2, 3, 1]))
print(reverse_pairs([2, 4, 3, 5, 1]))
print(reverse_pairs([2147483647, 2147483647, 2147483647, 2147483647, 2147483647, 2147483647]))
''', js=r'''
function reversePairs(nums) {
  function go(a) {
    if (a.length <= 1) return [a, 0];
    const mid = Math.floor(a.length / 2);
    const [left, x] = go(a.slice(0, mid));
    const [right, y] = go(a.slice(mid));
    let count = 0, j = 0;
    for (const v of left) {                  // both halves are sorted, so j only moves forward
      while (j < right.length && v > 2 * right[j]) j++;
      count += j;
    }
    const merged = [];
    let i = 0, k = 0;
    while (i < left.length && k < right.length) merged.push(left[i] <= right[k] ? left[i++] : right[k++]);
    return [merged.concat(left.slice(i), right.slice(k)), x + y + count];
  }
  return go(nums)[1];
}

console.log(reversePairs([1, 3, 2, 3, 1]));
console.log(reversePairs([2, 4, 3, 5, 1]));
console.log(reversePairs([2147483647, 2147483647, 2147483647, 2147483647, 2147483647, 2147483647]));
''', java=r'''
import java.util.*;

public class ReversePairs {
    static long count;

    static int[] go(int[] a) {
        if (a.length <= 1) return a;
        int mid = a.length / 2;
        int[] left = go(Arrays.copyOfRange(a, 0, mid));
        int[] right = go(Arrays.copyOfRange(a, mid, a.length));
        int j = 0;
        for (int v : left) {                             // both halves are sorted, so j only moves forward
            while (j < right.length && (long) v > 2L * right[j]) j++;   // long avoids overflow
            count += j;
        }
        int[] merged = new int[a.length];
        int i = 0, k = 0, m = 0;
        while (i < left.length && k < right.length) merged[m++] = left[i] <= right[k] ? left[i++] : right[k++];
        while (i < left.length) merged[m++] = left[i++];
        while (k < right.length) merged[m++] = right[k++];
        return merged;
    }

    static long reversePairs(int[] nums) {
        count = 0;
        go(nums);
        return count;
    }

    public static void main(String[] args) {
        System.out.println(reversePairs(new int[]{1, 3, 2, 3, 1}));
        System.out.println(reversePairs(new int[]{2, 4, 3, 5, 1}));
        System.out.println(reversePairs(new int[]{2147483647, 2147483647, 2147483647, 2147483647, 2147483647, 2147483647}));
    }
}
''', ts=r'''
function reversePairs(nums: number[]): number {
  function go(a: number[]): [number[], number] {
    if (a.length <= 1) return [a, 0];
    const mid = Math.floor(a.length / 2);
    const [left, x] = go(a.slice(0, mid));
    const [right, y] = go(a.slice(mid));
    let count = 0, j = 0;
    for (const v of left) {                  // both halves are sorted, so j only moves forward
      while (j < right.length && v > 2 * right[j]) j++;
      count += j;
    }
    const merged: number[] = [];
    let i = 0, k = 0;
    while (i < left.length && k < right.length) merged.push(left[i] <= right[k] ? left[i++] : right[k++]);
    return [merged.concat(left.slice(i), right.slice(k)), x + y + count];
  }
  return go(nums)[1];
}

console.log(reversePairs([1, 3, 2, 3, 1]));
console.log(reversePairs([2, 4, 3, 5, 1]));
console.log(reversePairs([2147483647, 2147483647, 2147483647, 2147483647, 2147483647, 2147483647]));
''')

t.code('p_median', py=r'''
def find_median_sorted_arrays(a, b):
    def kth(i, j, k):
        """k-th smallest (from 1) of a[i:] and b[j:] together."""
        if i == len(a):
            return b[j + k - 1]
        if j == len(b):
            return a[i + k - 1]
        if k == 1:
            return min(a[i], b[j])
        half = k // 2
        ia = min(i + half, len(a)) - 1        # look half way into each array
        jb = min(j + half, len(b)) - 1
        if a[ia] <= b[jb]:
            return kth(ia + 1, j, k - (ia - i + 1))    # those a items are all too small: drop them
        return kth(i, jb + 1, k - (jb - j + 1))        # or drop the b items instead

    n = len(a) + len(b)
    if n % 2 == 1:
        return float(kth(0, 0, n // 2 + 1))
    return (kth(0, 0, n // 2) + kth(0, 0, n // 2 + 1)) / 2


for a, b in (([1, 3], [2]), ([1, 2], [3, 4]), ([], [5]), ([1, 4, 9], [2, 3, 7, 10])):
    print(f"{find_median_sorted_arrays(a, b):.1f}")
''', js=r'''
function findMedianSortedArrays(a, b) {
  function kth(i, j, k) {                    // k-th smallest (from 1) of a[i..] and b[j..] together
    if (i === a.length) return b[j + k - 1];
    if (j === b.length) return a[i + k - 1];
    if (k === 1) return Math.min(a[i], b[j]);
    const half = Math.floor(k / 2);
    const ia = Math.min(i + half, a.length) - 1;   // look half way into each array
    const jb = Math.min(j + half, b.length) - 1;
    if (a[ia] <= b[jb]) return kth(ia + 1, j, k - (ia - i + 1));   // those a items are all too small
    return kth(i, jb + 1, k - (jb - j + 1));                        // or drop the b items instead
  }
  const n = a.length + b.length;
  if (n % 2 === 1) return kth(0, 0, Math.floor(n / 2) + 1);
  return (kth(0, 0, n / 2) + kth(0, 0, n / 2 + 1)) / 2;
}

for (const [a, b] of [[[1, 3], [2]], [[1, 2], [3, 4]], [[], [5]], [[1, 4, 9], [2, 3, 7, 10]]]) {
  console.log(findMedianSortedArrays(a, b).toFixed(1));
}
''', java=r'''
public class MedianTwoArrays {
    static int[] a, b;

    static int kth(int i, int j, int k) {                // k-th smallest (from 1) of a[i..] and b[j..] together
        if (i == a.length) return b[j + k - 1];
        if (j == b.length) return a[i + k - 1];
        if (k == 1) return Math.min(a[i], b[j]);
        int half = k / 2;
        int ia = Math.min(i + half, a.length) - 1;       // look half way into each array
        int jb = Math.min(j + half, b.length) - 1;
        if (a[ia] <= b[jb]) return kth(ia + 1, j, k - (ia - i + 1));   // those a items are all too small
        return kth(i, jb + 1, k - (jb - j + 1));                        // or drop the b items instead
    }

    static double findMedianSortedArrays(int[] x, int[] y) {
        a = x;
        b = y;
        int n = a.length + b.length;
        if (n % 2 == 1) return kth(0, 0, n / 2 + 1);
        return (kth(0, 0, n / 2) + kth(0, 0, n / 2 + 1)) / 2.0;
    }

    public static void main(String[] args) {
        int[][][] tests = {{{1, 3}, {2}}, {{1, 2}, {3, 4}}, {{}, {5}}, {{1, 4, 9}, {2, 3, 7, 10}}};
        for (int[][] t : tests) System.out.println(String.format("%.1f", findMedianSortedArrays(t[0], t[1])));
    }
}
''', ts=r'''
function findMedianSortedArrays(a: number[], b: number[]): number {
  function kth(i: number, j: number, k: number): number {   // k-th smallest (from 1) of a[i..] and b[j..]
    if (i === a.length) return b[j + k - 1];
    if (j === b.length) return a[i + k - 1];
    if (k === 1) return Math.min(a[i], b[j]);
    const half = Math.floor(k / 2);
    const ia = Math.min(i + half, a.length) - 1;   // look half way into each array
    const jb = Math.min(j + half, b.length) - 1;
    if (a[ia] <= b[jb]) return kth(ia + 1, j, k - (ia - i + 1));   // those a items are all too small
    return kth(i, jb + 1, k - (jb - j + 1));                        // or drop the b items instead
  }
  const n = a.length + b.length;
  if (n % 2 === 1) return kth(0, 0, Math.floor(n / 2) + 1);
  return (kth(0, 0, n / 2) + kth(0, 0, n / 2 + 1)) / 2;
}

const tests: Array<[number[], number[]]> = [[[1, 3], [2]], [[1, 2], [3, 4]], [[], [5]], [[1, 4, 9], [2, 3, 7, 10]]];
for (const [a, b] of tests) console.log(findMedianSortedArrays(a, b).toFixed(1));
''')

t.leet(169, 'e', 'p_major',
       statement='<p>Return the value that appears more than n ÷ 2 times. Such a value always exists.</p>',
       example='[3,2,3]          →  3\n[2,2,1,1,1,2,2]  →  2',
       hint='If x is the majority of the whole list, it is the majority of at least one half.',
       approach='<p>Find the majority of each half. If both halves agree, that is the answer. If not, count both candidates across the whole range and keep the bigger count. This runs in O(n log n). The Boyer Moore vote in the Python chapter does it in O(n) with O(1) memory, and the hashing chapter does it with a counter.</p>',
       time='O(n log n)', space='O(log n) call stack')
t.leet(108, 'e', 'p_bst',
       statement='<p>Turn a sorted list into a height balanced binary search tree.</p>',
       example='[-10,-3,0,5,9]  →  root 0, preorder 0 -10 -3 5 9\n[1,3]           →  root 1, then 3',
       hint='Which value should be the root so both sides get the same number of nodes?',
       approach='<p>The middle value becomes the root. Everything to its left is smaller, so it builds the left subtree, and everything to its right builds the right subtree. Each half is the same problem again. Because the halves differ in size by at most one, the height is about log₂ n.</p>',
       time='O(n)', space='O(log n) call stack')
t.leet(53, 'm', 'p_maxsub', title='Maximum Subarray', url='https://leetcode.com/problems/maximum-subarray/', diff='Medium',
       statement='<p>Find the largest sum of a non empty run of neighbouring numbers.</p>',
       example='[-2,1,-3,4,-1,2,1,-5,4]  →  6   (4 -1 2 1)\n[5,4,-1,7,8]             →  23',
       hint='The best run is in the left half, in the right half, or crosses the middle.',
       approach='<p>Solve both halves. The crossing run must end at <code>mid</code> and start at <code>mid + 1</code>, so grow one scan left from the middle and one scan right, keeping the best totals. The answer is the largest of the three. This is O(n log n). Kadane\'s scan, shown alongside to check the answer, does it in O(n).</p>',
       time='O(n log n)', space='O(log n)')
t.leet(215, 'm', 'p_kth',
       statement='<p>Return the k-th largest value in an unsorted list, without sorting the whole list.</p>',
       example='[3,2,1,5,6,4], k = 2        →  5\n[3,2,3,1,2,4,5,5,6], k = 4  →  4',
       hint='The k-th largest sits at index n − k once the list is sorted.',
       approach='<p>Quickselect: partition around a pivot so smaller values go left. The pivot then sits at its final index. If that index is n − k, done. Otherwise keep only the side that holds n − k and repeat. On average each round halves the work, so the total is about n + n/2 + n/4 + ... = 2n. A random pivot avoids the O(n²) worst case. Here the last element is the pivot so every run prints the same steps.</p>',
       time='O(n) on average, O(n²) worst case', space='O(1)')
t.leet(148, 'h', 'p_sortlist', title='Sort List', url='https://leetcode.com/problems/sort-list/', diff='Medium',
       statement='<p>Sort a linked list in O(n log n) time.</p>',
       example='4 2 1 3       →  1 2 3 4\n-1 5 3 4 0    →  -1 0 3 4 5\n(empty)       →  (empty)',
       hint='Merge sort suits lists, because merging only relinks nodes.',
       approach='<p>Find the middle with slow and fast pointers, cut the list there, sort both halves recursively, then merge them with a dummy node. Linked lists cannot jump to an index, so quick sort and heap sort are awkward, but merge sort only walks forward.</p>',
       time='O(n log n)', space='O(log n) call stack')
t.leet(241, 'h', 'p_ways', title='Different Ways to Add Parentheses', url='https://leetcode.com/problems/different-ways-to-add-parentheses/', diff='Medium',
       statement='<p>Given an expression with numbers and the operators +, − and *, return every result you can get by adding brackets in different ways.</p>',
       example='2-1-1    →  0 2\n2*3-4*5  →  -34 -14 -10 -10 10',
       hint='Pick the operator that is applied last.',
       approach='<p>Every operator can be the last one applied. Split there, compute all values of the left side and all values of the right side recursively, and combine every pair. A memo on the substring stops the same piece being solved many times. The results here are sorted so all four languages print the same order.</p>',
       time='grows like the Catalan numbers', space='the memo of all pieces')
t.leet(493, 'x', 'p_revpairs', title='Reverse Pairs', url='https://leetcode.com/problems/reverse-pairs/', diff='Hard',
       statement='<p>Count pairs i < j where <code>nums[i] > 2 × nums[j]</code>.</p>',
       example='[1,3,2,3,1]  →  2\n[2,4,3,5,1]  →  3',
       hint='Count inversions with merge sort, but with a different test.',
       approach='<p>Inside merge sort, both halves are already sorted. For each left value, move a pointer through the right half while <code>left > 2 × right</code>. The pointer never moves back, so counting costs O(n) per level. Then merge as usual. In Java use <code>long</code>, because 2 × 2,147,483,647 overflows an int.</p>',
       time='O(n log n)', space='O(n)')
t.leet(4, 'x', 'p_median',
       statement='<p>Two lists are each sorted. Return the median of all their values together in O(log(m + n)) time.</p>',
       example='[1,3] and [2]      →  2.0\n[1,2] and [3,4]    →  2.5',
       hint='Find the k-th smallest, and throw away about k ÷ 2 values each step.',
       approach='<p>To find the k-th smallest, look k ÷ 2 places into each list. The list with the smaller value there cannot hold the answer in that first part, so drop those values and look for a smaller k in what is left. k halves each time, so it takes O(log(m + n)) steps. The median is the middle value, or the average of the two middle values.</p>',
       time='O(log(m + n))', space='O(log(m + n)) call stack')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='divide-conquer-combine', emoji='✂️', title='Divide, conquer, combine', html='''
<p>A huge pile of exam papers is easier to sort with friends. Split the pile in two, give each half to a friend, and when both hand back a sorted half, merge them. Each friend can split their half again. That is <b>divide and conquer</b>: split a problem into smaller copies of itself, solve the copies, and combine their answers.</p>
<div class="grid3">
<div class="box"><h4>✂️ Divide</h4><p>Cut the input into parts, usually two halves.</p></div>
<div class="box"><h4>⚔️ Conquer</h4><p>Solve each part recursively. Tiny parts are base cases.</p></div>
<div class="box"><h4>🧩 Combine</h4><p>Build the answer for the whole from the answers of the parts.</p></div>
</div>
<div class="viz" data-viz="pk" data-pk="split"></div>
<div class="c3" data-k="dcmax" data-label="The biggest number by divide and conquer"></div>
<div class="rule">Backtracking explores choices and undoes them. Divide and conquer splits the input, and the parts never overlap. When parts do overlap, use dynamic programming instead.</div>
'''),
    dict(id='inversions', emoji='🔀', title='Merge sort that counts: inversions', html='''
<p>An <b>inversion</b> is a pair that is out of order: a bigger number before a smaller one. Counting all pairs takes O(n²). Merge sort counts them for free. When a value from the right half is merged before values still waiting in the left half, it jumps over all of them, and each jump is one inversion.</p>
<div class="viz" data-viz="pk" data-pk="inv"></div>
<div class="c3" data-k="inversions" data-label="Counting inversions with merge sort"></div>
<div class="exam">Music apps use inversions to compare two people's rankings of the same songs. Few inversions means similar taste. The Arrays chapter animates plain merge sort and quick sort step by step.</div>
'''),
    dict(id='master-theorem', emoji='📐', title='How fast is it? The master theorem', html='''
<p>A divide and conquer running time looks like <code>T(n) = a · T(n / b) + f(n)</code>: a sub problems, each b times smaller, plus f(n) work to divide and combine. Draw the recursion tree. Level i has a<sup>i</sup> nodes, each of size n / b<sup>i</sup>. Who does most of the work, the root or the leaves, decides the answer.</p>
<div class="tw"><table class="jt"><tr><th>Algorithm</th><th>Recurrence</th><th>Who wins</th><th>Result</th></tr>
<tr><td>Binary search</td><td>T(n / 2) + 1</td><td>every level equal</td><td>O(log n)</td></tr>
<tr><td>Merge sort</td><td>2 T(n / 2) + n</td><td>every level equal</td><td>O(n log n)</td></tr>
<tr><td>Karatsuba</td><td>3 T(n / 2) + n</td><td>the leaves</td><td>O(n<sup>1.585</sup>)</td></tr>
<tr><td>Finding the max</td><td>2 T(n / 2) + 1</td><td>the leaves</td><td>O(n)</td></tr>
<tr><td>Quickselect, average</td><td>T(n / 2) + n</td><td>the root</td><td>O(n)</td></tr></table></div>
<div class="viz" data-viz="pk" data-pk="master"></div>
<div class="c3" data-k="master" data-label="Counting the work level by level"></div>
<div class="rule">Compare a with b<sup>d</sup>, where f(n) = n<sup>d</sup>. Equal means every level does the same work, O(n<sup>d</sup> log n). Bigger means the leaves win, O(n<sup>log<sub>b</sub> a</sup>). Smaller means the root wins, O(n<sup>d</sup>).</div>
'''),
    dict(id='quickselect', emoji='🎯', title='Quickselect: find the k-th without sorting', html='''
<p>To find the median of a list you do not need it fully sorted. Partition around a pivot as in quick sort, so the pivot lands at its final index. If that is the index you want, stop. Otherwise the answer is on one side only, so <b>throw the other side away</b> and repeat. Quick sort recurses into both sides. Quickselect recurses into one.</p>
<div class="viz" data-viz="pk" data-pk="qsel"></div>
<div class="c3" data-k="qselect" data-label="Quickselect with a last element pivot"></div>
<div class="grid2">
<div class="box"><h4>⚡ Average O(n)</h4><p>With a fair pivot the part that is kept halves each round: n + n/2 + n/4 + ... is less than 2n comparisons.</p></div>
<div class="box"><h4>🎲 Pick a random pivot</h4><p>An unlucky pivot every time, like the last element of a sorted list, gives O(n²). A random pivot makes that very unlikely.</p></div>
</div>
'''),
    dict(id='max-subarray', emoji='📈', title='Maximum subarray: the run that crosses the middle', html='''
<p>Which run of neighbouring numbers has the largest sum? Split the list in half. The best run is either entirely in the left half, entirely in the right half, or it <b>crosses the middle</b>. The first two are smaller copies of the problem. The crossing run is easy: grow it left from the middle and right from the middle, keeping the best totals.</p>
<div class="viz" data-viz="pk" data-pk="maxsub"></div>
<div class="c3" data-k="maxsub" data-label="Maximum subarray by divide and conquer"></div>
<div class="exam">This runs in O(n log n). Kadane's scan solves it in O(n) and appears in the LeetCode practice to check the answer. The divide and conquer version still matters, because the same idea powers segment trees, which answer the best run in any range quickly.</div>
'''),
    dict(id='closest-pair', emoji='📍', title='The closest pair of points', html='''
<p>Given points on a map, which two are closest? Checking every pair costs O(n²). Divide and conquer sorts the points by x and splits them with a vertical line. Solve each side, and let d be the smaller answer. A closer pair across the line must have both points within d of the line, in a narrow <b>strip</b>. Sorted by y, each strip point only needs a few neighbours checked.</p>
<div class="viz" data-viz="pk" data-pk="closest"></div>
<div class="c3" data-k="closest" data-label="Closest pair: divide and conquer against brute force"></div>
<div class="grid2">
<div class="box"><h4>🔢 Squared distances</h4><p>Comparing squared distances avoids square roots, so every number stays a whole number and all languages print the same result.</p></div>
<div class="box"><h4>⏱️ O(n log n)</h4><p>A geometry argument shows each strip point has at most 7 useful neighbours, so the strip costs O(n) per level.</p></div>
</div>
'''),
    dict(id='karatsuba', emoji='✖️', title='Karatsuba: multiply with three products, not four', html='''
<p>School multiplication of two n digit numbers takes n² digit products. Split each number in half: x = a · 10<sup>m</sup> + b and y = c · 10<sup>m</sup> + d. Then x · y needs ac, bd and ad + bc. The trick is that <code>(a + b)(c + d) − ac − bd = ad + bc</code>, so <b>three</b> products are enough instead of four.</p>
<div class="viz" data-viz="pk" data-pk="karat"></div>
<div class="c3" data-k="karatsuba" data-label="Karatsuba multiplication with a counter"></div>
<div class="rule">Saving one product out of four sounds small, but it happens at every level: 3<sup>log₂ n</sup> = n<sup>1.585</sup> instead of n². Python uses Karatsuba for very large whole numbers.</div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem is solved in the Practice section in Python, JavaScript, Java and TypeScript, with line by line replay.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>The divide and conquer idea</th></tr>
<tr><td><a href="#lc169">169. Majority Element</a></td><td>Easy</td><td>the winner of a half, or of the other</td></tr>
<tr><td><a href="#lc108">108. Convert Sorted Array to Binary Search Tree</a></td><td>Easy</td><td>the middle becomes the root</td></tr>
<tr><td><a href="#lc53">53. Maximum Subarray</a></td><td>Medium</td><td>left, right or crossing</td></tr>
<tr><td><a href="#lc215">215. Kth Largest Element in an Array</a></td><td>Medium</td><td>quickselect keeps one side</td></tr>
<tr><td><a href="#lc148">148. Sort List</a></td><td>Hard</td><td>merge sort on a linked list</td></tr>
<tr><td><a href="#lc241">241. Different Ways to Add Parentheses</a></td><td>Hard</td><td>split at the last operator</td></tr>
<tr><td><a href="#lc493">493. Reverse Pairs</a></td><td>Expert</td><td>count inside merge sort</td></tr>
<tr><td><a href="#lc4">4. Median of Two Sorted Arrays</a></td><td>Expert</td><td>drop half of k each step</td></tr></table></div>
'''),
]

VIZ_JS = r'''
(() => {
  const D = PK.defs;
  const LIMIT = 170;
  const okList = (s, lo, hi) => { const a = PK.parseList(s); return a && a.length >= lo && a.length <= hi && a.every(x => Number.isInteger(x) && Math.abs(x) <= 99) ? a : null; };

  /* ---------- split, solve, combine: the biggest number ---------- */
  D.split = el => PK.widget(el, {
    title: 'Split the job, then combine', sub: 'Each box splits its numbers in half and asks two helpers. A single number answers at once. On the way back up, each box keeps the bigger answer.',
    inputs: [{ k: 'nums', label: 'Numbers', type: 'text', val: '3, 8, 1, 9, 4, 7, 2, 6', w: 220 }],
    random: () => ({ nums: Array.from({ length: 4 + Math.floor(Math.random() * 5) }, () => Math.floor(Math.random() * 30)).join(', ') }),
    check: v => okList(v.nums, 2, 8) ? '' : 'Give two to eight whole numbers.',
    frames: ({ nums }) => {
      const a = okList(nums, 2, 8), kids = {}, rng = {}, ans = {}, F = [];
      (function build(id, lo, hi) {
        rng[id] = [lo, hi];
        if (lo < hi) { const m = Math.floor((lo + hi) / 2); kids[id] = [id + 'L', id + 'R']; build(id + 'L', lo, m); build(id + 'R', m + 1, hi); }
      })('n', 0, a.length - 1);
      const W = 540, depth = Math.ceil(Math.log2(a.length)), H = 90 * depth + 70;
      const T = PK.treeLayout(kids, 'n', id => (ans[id] !== undefined ? ans[id] : '?'), W, H);
      const shown = new Set();
      const pic = (cur, cls) => {
        const L = PK.treeLayout(kids, 'n', id => (ans[id] !== undefined ? ans[id] : '?'), W, H);
        const ncls = {}, tag = {};
        shown.forEach(x => { ncls[x] = ans[x] !== undefined ? 'done' : ''; if (kids[x]) tag[x] = a.slice(rng[x][0], rng[x][1] + 1).join(' '); });
        if (cur) ncls[cur] = cls;
        const [lo, hi] = cur ? rng[cur] : [-1, -2];
        return [{ t: 'row', label: 'The numbers', cells: a, cls: Object.fromEntries(a.map((_, i) => [i, i >= lo && i <= hi ? (cls === 'yes' ? 'yes' : 'look') : ''])) },
                { t: 'graph', w: W, h: H, nodes: L.nodes.filter(x => shown.has(x[0])), edges: L.edges.filter(e => shown.has(e[1])), ncls, tag }];
      };
      const go = id => {
        shown.add(id);
        const [lo, hi] = rng[id];
        if (lo === hi) {
          ans[id] = a[lo];
          F.push({ mood: 'happy', msg: `Just one number, ${a[lo]}. That is the base case: it answers ${a[lo]} straight away.`, layers: pic(id, 'cur') });
          return a[lo];
        }
        F.push({ mood: 'look', msg: `Divide: indexes ${lo} to ${hi} split into ${lo} to ${Math.floor((lo + hi) / 2)} and ${Math.floor((lo + hi) / 2) + 1} to ${hi}.`, layers: pic(id, 'look') });
        const l = go(kids[id][0]), r = go(kids[id][1]);
        ans[id] = Math.max(l, r);
        F.push({ mood: 'work', fx: id === 'n' ? 'burst' : '', msg: `Combine: the helpers said ${l} and ${r}. Keep the bigger one, <b>${ans[id]}</b>.`, layers: pic(id, 'yes') });
        return ans[id];
      };
      const m = go('n');
      F.push({ mood: 'wow', fx: 'rain', msg: `The biggest number is <b>${m}</b>. There were ${2 * a.length - 1} boxes: ${a.length} base cases and ${a.length - 1} combine steps, so the work is O(n).`, layers: pic('n', 'yes') });
      return F;
    }
  });

  /* ---------- merge sort that counts inversions ---------- */
  D.inv = el => PK.widget(el, {
    title: 'Count the jumps', sub: 'Merge two sorted halves. When a number from the right half goes first, it jumps over every number still waiting on the left. Each jump is an inversion.',
    inputs: [{ k: 'nums', label: 'Numbers', type: 'text', val: '3, 1, 2, 5, 4', w: 180 }],
    random: () => ({ nums: Array.from({ length: 4 + Math.floor(Math.random() * 3) }, () => 1 + Math.floor(Math.random() * 9)).join(', ') }),
    check: v => okList(v.nums, 2, 7) ? '' : 'Give two to seven whole numbers.',
    frames: ({ nums }) => {
      const a = okList(nums, 2, 7), F = [];
      let total = 0;
      const go = (arr, lo) => {
        if (arr.length <= 1) return arr;
        const mid = Math.floor(arr.length / 2);
        const L = go(arr.slice(0, mid), lo), R = go(arr.slice(mid), lo + mid);
        const merged = [];
        let i = 0, j = 0;
        const pic = (li, rj, cl, cr) => [
          { t: 'row', label: `Left half (from index ${lo})`, cells: L, cls: Object.fromEntries(L.map((_, k) => [k, k < i ? 'done' : k === li ? cl : k > li && cl === 'mv' ? 'mv' : ''])) },
          { t: 'row', label: 'Right half', cells: R, cls: Object.fromEntries(R.map((_, k) => [k, k < j ? 'done' : k === rj ? cr : ''])) },
          { t: 'row', label: 'Merged', cells: merged.length ? merged.slice() : ['empty'], cls: merged.length ? { [merged.length - 1]: 'yes' } : { 0: 'ghost' } }];
        F.push({ mood: 'think', msg: `Merge ${L.join(' ')} with ${R.join(' ')}. Both halves are already sorted.`, vars: { inversions: total }, layers: pic(-1, -1) });
        while (i < L.length && j < R.length) {
          if (L[i] <= R[j]) {
            F.push({ mood: 'look', msg: `${L[i]} ≤ ${R[j]}, so ${L[i]} goes first. No jump.`, vars: { inversions: total }, layers: pic(i, j, 'look', '') });
            merged.push(L[i++]);
          } else {
            const jumps = L.length - i;
            total += jumps;
            F.push({ mood: 'wow', fx: jumps > 1 ? 'burst' : '', msg: `${R[j]} < ${L[i]}! ${R[j]} jumps over ${L.slice(i).join(', ')}: <b>+${jumps}</b> inversion${jumps > 1 ? 's' : ''}.`, vars: { inversions: total }, layers: pic(i, j, 'mv', 'yes') });
            merged.push(R[j++]);
          }
        }
        while (i < L.length) merged.push(L[i++]);
        while (j < R.length) merged.push(R[j++]);
        F.push({ mood: 'work', msg: `Copy what is left. Merged: ${merged.join(' ')}.`, vars: { inversions: total }, layers: pic(-1, -1) });
        return merged;
      };
      const out = go(a, 0);
      let brute = 0;
      for (let i = 0; i < a.length; i++) for (let j = i + 1; j < a.length; j++) if (a[i] > a[j]) brute++;
      F.push({ mood: total ? 'wow' : 'happy', fx: 'rain', msg: `Sorted: ${out.join(' ')}. Total <b>${total}</b> inversion${total === 1 ? '' : 's'}, the same as checking all ${a.length * (a.length - 1) / 2} pairs one by one (${brute}).`, vars: { inversions: total }, layers: [{ t: 'row', label: 'Sorted', cells: out, cls: Object.fromEntries(out.map((_, k) => [k, 'yes'])) }] });
      return F;
    }
  });

  /* ---------- the master theorem, level by level ---------- */
  D.master = el => PK.widget(el, {
    title: 'Who does the work?', sub: 'T(n) = a · T(n / b) + n^d. Each bar is the total work on one level of the recursion tree.',
    inputs: [{ k: 'pre', label: 'Algorithm', type: 'seg', val: 'merge', opts: [['bin', '🔍 Binary search'], ['merge', '🔀 Merge sort'], ['kara', '✖️ Karatsuba'], ['qsel', '🎯 Quickselect']] }],
    frames: ({ pre }) => {
      const P = { bin: [1, 2, 0, 'binary search'], merge: [2, 2, 1, 'merge sort'], kara: [3, 2, 1, 'Karatsuba'], qsel: [1, 2, 1, 'quickselect (average)'] }[pre];
      const [A, B, Dd, name] = P, n = 64, levels = Math.round(Math.log(n) / Math.log(B)), F = [];
      const work = [], nodes = [];
      for (let i = 0; i <= levels; i++) { nodes.push(A ** i); work.push(Math.round(A ** i * (n / B ** i) ** Dd)); }
      const rec = `T(n) = ${A === 1 ? '' : A + ' '}T(n / ${B}) + ${Dd === 0 ? '1' : 'n'}`;
      F.push({ mood: 'think', msg: `${name}: ${rec}. Take n = ${n} and add up the work on each level.`, vars: { a: A, b: B, d: Dd } });
      for (let i = 0; i <= levels; i++) {
        F.push({ mood: 'look', msg: `Level ${i}: ${nodes[i]} sub problem${nodes[i] > 1 ? 's' : ''} of size ${n / B ** i}, work ${nodes[i]} × ${Dd === 0 ? 1 : n / B ** i} = <b>${work[i]}</b>.`, vars: { level: i, 'work so far': work.slice(0, i + 1).reduce((s, x) => s + x, 0) },
          layers: [{ t: 'bars', label: 'Work per level (level 0 is the root)', vals: work.slice(0, i + 1), cls: { [i]: 'look' }, max: Math.max(...work) }] });
      }
      const bd = B ** Dd, total = work.reduce((s, x) => s + x, 0);
      const ex = (Math.log(A) / Math.log(B)).toFixed(3);
      const big = Dd === 0 ? 'O(log n)' : Dd === 1 ? 'O(n log n)' : `O(n<sup>${Dd}</sup> log n)`;
      const verdict = A === bd ? `a = b<sup>d</sup> = ${A}, so every level does the same work. Total ${big}.`
        : A > bd ? `a = ${A} is bigger than b<sup>d</sup> = ${bd}, so the leaves win. Total O(n<sup>${ex}</sup>).`
        : `a = ${A} is smaller than b<sup>d</sup> = ${bd}, so the root wins. Total ${Dd === 1 ? 'O(n)' : `O(n<sup>${Dd}</sup>)`}.`;
      const spoken = A === bd ? `Every level does the same work, so the total is ${Dd === 0 ? 'order log n' : Dd === 1 ? 'order n log n' : 'order n to the ' + Dd + ' log n'}.`
        : A > bd ? `a is bigger than b to the d, so the leaves win, and the total is order n to the power ${ex}.`
        : `a is smaller than b to the d, so the root wins, and the total is order n${Dd === 1 ? '' : ' to the ' + Dd}.`;
      const cls = {};
      work.forEach((w, i) => { cls[i] = A === bd ? 'yes' : A > bd ? (i === levels ? 'yes' : '') : (i === 0 ? 'yes' : ''); });
      F.push({ mood: 'wow', fx: 'burst', msg: `${verdict} All levels add up to ${total}.`, say: `${spoken} All levels add up to ${total}.`, vars: { total },
        layers: [{ t: 'bars', label: 'Work per level', vals: work, cls, max: Math.max(...work) }] });
      return F;
    }
  });

  /* ---------- quickselect ---------- */
  D.qsel = el => PK.widget(el, {
    title: 'Find the k-th smallest', sub: 'Partition around the last number. The pivot lands in its final place. Keep only the side that holds k, and throw the rest away.',
    inputs: [{ k: 'nums', label: 'Numbers', type: 'text', val: '7, 2, 9, 4, 1, 8, 3', w: 190 }, { k: 'k', label: 'k (from 0)', type: 'num', val: 3, min: 0, max: 9 }],
    random: () => { const n = 5 + Math.floor(Math.random() * 3); return { nums: Array.from({ length: n }, () => 1 + Math.floor(Math.random() * 20)).join(', '), k: Math.floor(Math.random() * n) }; },
    check: v => { const a = okList(v.nums, 2, 9); return a && Number.isInteger(v.k) && v.k >= 0 && v.k < a.length ? '' : 'Give two to nine whole numbers and a k from 0 to the last index.'; },
    frames: ({ nums, k }) => {
      const a = okList(nums, 2, 9), F = [];
      let lo = 0, hi = a.length - 1, round = 0;
      const pic = (ex) => {
        const cls = {};
        a.forEach((_, i) => { if (i < lo || i > hi) cls[i] = 'done'; });
        Object.assign(cls, ex.cls || {});
        return [{ t: 'row', label: `Searching indexes ${lo} to ${hi}`, cells: a.slice(), cls, ptr: ex.ptr || {}, tag: { [k]: 'k' } }];
      };
      F.push({ mood: 'think', msg: `Which number would sit at index ${k} if the list were sorted? Let us find out without sorting it.`, layers: pic({}) });
      while (true) {
        round++;
        const pivot = a[hi];
        let store = lo;
        F.push({ mood: 'look', msg: `Round ${round}: the pivot is ${pivot}. Move every number smaller than ${pivot} to the left.`, vars: { round }, layers: pic({ cls: { [hi]: 'piv' }, ptr: { [lo]: 'store' } }) });
        for (let i = lo; i < hi; i++) {
          if (F.length > LIMIT) break;
          if (a[i] < pivot) {
            [a[i], a[store]] = [a[store], a[i]];
            F.push({ mood: 'work', msg: `${a[store]} < ${pivot}: swap it into the left part at index ${store}.`, vars: { round }, layers: pic({ cls: { [hi]: 'piv', [store]: 'yes' }, ptr: { [i]: 'i', [store + 1 <= hi ? store + 1 : hi]: 'store' } }) });
            store++;
          } else {
            F.push({ mood: 'look', msg: `${a[i]} ≥ ${pivot}: leave it on the right.`, vars: { round }, layers: pic({ cls: { [hi]: 'piv', [i]: 'no' }, ptr: { [i]: 'i', [store]: 'store' } }) });
          }
        }
        [a[store], a[hi]] = [a[hi], a[store]];
        if (store === k) {
          F.push({ mood: 'wow', fx: 'burst', msg: `The pivot ${a[store]} lands at index ${store}, which is k! The answer is <b>${a[store]}</b>, found in ${round} round${round > 1 ? 's' : ''}.`, vars: { round }, layers: pic({ cls: { [store]: 'yes' } }) });
          break;
        }
        if (store < k) {
          F.push({ mood: 'happy', msg: `The pivot ${a[store]} lands at index ${store}, left of k. Throw away everything up to ${store}.`, vars: { round }, layers: pic({ cls: { [store]: 'piv' } }) });
          lo = store + 1;
        } else {
          F.push({ mood: 'happy', msg: `The pivot ${a[store]} lands at index ${store}, right of k. Throw away everything from ${store} on.`, vars: { round }, layers: pic({ cls: { [store]: 'piv' } }) });
          hi = store - 1;
        }
        if (F.length > LIMIT) break;
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `Done. Only one side was searched each round, so the work shrank every time. Sorted, the list would be ${[...a].sort((x, y) => x - y).join(' ')}.`, layers: pic({ cls: { [k]: 'yes' } }) });
      return F;
    }
  });

  /* ---------- maximum subarray ---------- */
  D.maxsub = el => PK.widget(el, {
    title: 'Left, right or across', sub: 'For each half, the best run is in the left part, in the right part, or crosses the middle. Pip compares the three.',
    inputs: [{ k: 'nums', label: 'Numbers', type: 'text', val: '-2, 1, -3, 4, -1, 2, 1, -5', w: 230 }],
    random: () => ({ nums: Array.from({ length: 6 + Math.floor(Math.random() * 3) }, () => Math.floor(Math.random() * 13) - 6).join(', ') }),
    check: v => okList(v.nums, 2, 8) ? '' : 'Give two to eight whole numbers, negatives allowed.',
    frames: ({ nums }) => {
      const a = okList(nums, 2, 8), F = [];
      const pic = (lo, hi, mid, run, cls) => {
        const c = {};
        a.forEach((_, i) => { c[i] = i < lo || i > hi ? 'done' : ''; });
        if (run) for (let i = run[0]; i <= run[1]; i++) c[i] = cls;
        return [{ t: 'row', label: `Looking at indexes ${lo} to ${hi}`, cells: a, cls: c, ptr: mid >= 0 ? { [mid]: 'mid' } : {} }];
      };
      const best = (lo, hi) => {
        if (lo === hi) return [a[lo], lo, lo];
        const mid = Math.floor((lo + hi) / 2);
        const L = best(lo, mid), R = best(mid + 1, hi);
        let s = 0, ls = -Infinity, li = mid, rs = -Infinity, rj = mid + 1;
        for (let i = mid; i >= lo; i--) { s += a[i]; if (s > ls) { ls = s; li = i; } }
        s = 0;
        for (let j = mid + 1; j <= hi; j++) { s += a[j]; if (s > rs) { rs = s; rj = j; } }
        const C = [ls + rs, li, rj];
        let top = L, who = 'left';
        if (R[0] > top[0]) { top = R; who = 'right'; }
        if (C[0] > top[0]) { top = C; who = 'crossing'; }
        F.push({ mood: 'look', msg: `Indexes ${lo} to ${hi}. Best on the left: ${L[0]}. Best on the right: ${R[0]}.`, vars: { left: L[0], right: R[0] }, layers: pic(lo, hi, mid, null) });
        F.push({ mood: 'work', msg: `Grow from the middle: ${a.slice(li, mid + 1).join(' ')} | ${a.slice(mid + 1, rj + 1).join(' ')} gives a crossing sum of ${C[0]}.`, vars: { left: L[0], right: R[0], crossing: C[0] }, layers: pic(lo, hi, mid, [li, rj], 'mv') });
        F.push({ mood: who === 'crossing' ? 'wow' : 'happy', fx: who === 'crossing' ? 'burst' : '', msg: `The ${who} run wins with <b>${top[0]}</b>.`, vars: { left: L[0], right: R[0], crossing: C[0] }, layers: pic(lo, hi, mid, [top[1], top[2]], 'yes') });
        return top;
      };
      F.push({ mood: 'think', msg: 'Find the run of neighbours with the biggest sum. Split, solve both halves, then check the run across the middle.', layers: pic(0, a.length - 1, -1, null) });
      const r = best(0, a.length - 1);
      F.push({ mood: 'wow', fx: 'rain', msg: `The best run is ${a.slice(r[1], r[2] + 1).join(' ')}, from index ${r[1]} to ${r[2]}, with sum <b>${r[0]}</b>.`, layers: pic(0, a.length - 1, -1, [r[1], r[2]], 'yes') });
      return F;
    }
  });

  /* ---------- closest pair of points ---------- */
  const PTS = [[2, 3], [12, 30], [40, 50], [5, 1], [12, 10], [3, 4], [30, 25], [22, 18]];
  D.closest = el => PK.widget(el, {
    title: 'The two closest points', sub: 'Sort by x, split with a vertical line, solve each side, then check only the narrow strip around the line.',
    inputs: [{ k: 'set', label: 'Points', type: 'seg', val: 'lesson', opts: [['lesson', '📍 Lesson points'], ['random', '🎲 Random points']] }],
    frames: ({ set }) => {
      const pts = set === 'random' ? Array.from({ length: 9 }, () => [Math.floor(Math.random() * 50), Math.floor(Math.random() * 50)]) : PTS.map(p => p.slice());
      const ids = pts.map((_, i) => 'p' + i), F = [];
      const W = 520, H = 300, X = x => 24 + x * 9.4, Y = y => H - 22 - y * 5.2;
      const nodes = pts.map((p, i) => [ids[i], Math.round(X(p[0])), Math.round(Y(p[1])), '']);
      const d2 = (i, j) => (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2;
      let bestPair = null, checks = 0;
      const pic = (ncls, edges, ecls) => [{ t: 'graph', w: W, h: H, r: 7, nodes, edges: edges || [], ncls, ecls: ecls || {}, tag: Object.fromEntries(pts.map((p, i) => [ids[i], p[0] + ',' + p[1]])) }];
      const order = pts.map((_, i) => i).sort((i, j) => pts[i][0] - pts[j][0] || pts[i][1] - pts[j][1]);
      F.push({ mood: 'think', msg: `${pts.length} points. Brute force would check ${pts.length * (pts.length - 1) / 2} pairs. Let us split instead.`, layers: pic({}) });
      const solve = idx => {
        if (idx.length <= 3) {
          let b = Infinity, bp = null;
          for (let i = 0; i < idx.length; i++) for (let j = i + 1; j < idx.length; j++) { checks++; const v = d2(idx[i], idx[j]); if (v < b) { b = v; bp = [idx[i], idx[j]]; } }
          const nc = Object.fromEntries(idx.map(i => [ids[i], 'cur']));
          F.push({ mood: 'happy', msg: `Only ${idx.length} points here, so check them directly. Closest squared distance ${b}.`, vars: { checks }, layers: pic(nc, [[ids[bp[0]], ids[bp[1]], '']], { [ids[bp[0]] + '-' + ids[bp[1]]]: 'yes' }) });
          return [b, bp];
        }
        const mid = Math.floor(idx.length / 2), midX = pts[idx[mid]][0];
        const nc = {};
        idx.forEach((i, k) => { nc[ids[i]] = k < mid ? 'cur' : 'mv'; });
        F.push({ mood: 'look', msg: `Split these ${idx.length} points at x = ${midX}: ${mid} on the left, ${idx.length - mid} on the right.`, vars: { checks }, layers: pic(nc) });
        const A = solve(idx.slice(0, mid)), B = solve(idx.slice(mid));
        let [d, bp] = A[0] <= B[0] ? A : B;
        const strip = idx.filter(i => (pts[i][0] - midX) ** 2 < d).sort((i, j) => pts[i][1] - pts[j][1]);
        const sc = Object.fromEntries(idx.map(i => [ids[i], strip.includes(i) ? 'look' : 'done']));
        F.push({ mood: 'think', msg: `Best on either side: squared distance ${d}. Only points closer than that to x = ${midX} can do better: ${strip.length} in the strip.`, vars: { checks }, layers: pic(sc, [[ids[bp[0]], ids[bp[1]], '']], { [ids[bp[0]] + '-' + ids[bp[1]]]: 'yes' }) });
        for (let i = 0; i < strip.length; i++) for (let j = i + 1; j < strip.length && (pts[strip[j]][1] - pts[strip[i]][1]) ** 2 < d; j++) {
          checks++;
          const v = d2(strip[i], strip[j]), better = v < d;
          if (better) { d = v; bp = [strip[i], strip[j]]; }
          F.push({ mood: better ? 'wow' : 'look', fx: better ? 'burst' : '', msg: better ? `Across the line: (${pts[strip[i]]}) and (${pts[strip[j]]}) are even closer, squared distance ${v}!` : `Strip check: (${pts[strip[i]]}) and (${pts[strip[j]]}) give ${v}, not better.`, vars: { checks },
            layers: pic(sc, [[ids[strip[i]], ids[strip[j]], '']], { [ids[strip[i]] + '-' + ids[strip[j]]]: better ? 'yes' : 'look' }) });
        }
        return [d, bp];
      };
      const [d, bp] = solve(order);
      bestPair = bp;
      F.push({ mood: 'wow', fx: 'rain', msg: `Closest pair: (${pts[bp[0]]}) and (${pts[bp[1]]}), squared distance <b>${d}</b>, after ${checks} checks instead of ${pts.length * (pts.length - 1) / 2}.`, vars: { checks },
        layers: pic({ [ids[bp[0]]]: 'yes', [ids[bp[1]]]: 'yes' }, [[ids[bp[0]], ids[bp[1]], '']], { [ids[bp[0]] + '-' + ids[bp[1]]]: 'yes' }) });
      return F;
    }
  });

  /* ---------- Karatsuba ---------- */
  D.karat = el => PK.widget(el, {
    title: 'Three products instead of four', sub: 'Split each number into a front half and a back half. Karatsuba needs only ac, bd and (a + b)(c + d).',
    inputs: [{ k: 'x', label: 'x', type: 'num', val: 1234, min: 10, max: 9999, w: 90 }, { k: 'y', label: 'y', type: 'num', val: 5678, min: 10, max: 9999, w: 90 }],
    random: () => ({ x: 1000 + Math.floor(Math.random() * 9000), y: 1000 + Math.floor(Math.random() * 9000) }),
    check: v => [v.x, v.y].every(n => Number.isInteger(n) && n >= 10 && n <= 9999) ? '' : 'Use two whole numbers from 10 to 9999.',
    frames: ({ x, y }) => {
      const m = Math.floor(Math.max(String(x).length, String(y).length) / 2), p = 10 ** m;
      const a = Math.floor(x / p), b = x % p, c = Math.floor(y / p), d = y % p;
      const ac = a * c, bd = b * d, sum = (a + b) * (c + d), mid = sum - ac - bd, r = ac * p * p + mid * p + bd;
      const card = (cells, cls) => ({ t: 'row', label: 'Pieces', cells, cls: cls || {}, idx: false });
      const prod = (done, hl) => ({ t: 'row', label: 'Products', cells: ['ac', 'bd', '(a+b)(c+d)'].map((s, i) => (i < done ? [ac, bd, sum][i] : s)), cls: Object.fromEntries([0, 1, 2].map(i => [i, i < done ? (i === hl ? 'yes' : 'sel') : 'ghost'])), idx: false });
      return [
        { mood: 'think', msg: `Multiply ${x} × ${y}. Split at 10<sup>${m}</sup> = ${p}.`, layers: [card([a, b, c, d].map(String), {})] },
        { mood: 'look', msg: `${x} = ${a} × ${p} + ${b}, so a = ${a}, b = ${b}. ${y} = ${c} × ${p} + ${d}, so c = ${c}, d = ${d}.`, layers: [card(['a ' + a, 'b ' + b, 'c ' + c, 'd ' + d], { 0: 'cur', 1: 'mv', 2: 'cur', 3: 'mv' }), prod(0)] },
        { mood: 'work', msg: `Product 1: ac = ${a} × ${c} = <b>${ac}</b>.`, layers: [card(['a ' + a, 'b ' + b, 'c ' + c, 'd ' + d], { 0: 'look', 2: 'look' }), prod(1, 0)] },
        { mood: 'work', msg: `Product 2: bd = ${b} × ${d} = <b>${bd}</b>.`, layers: [card(['a ' + a, 'b ' + b, 'c ' + c, 'd ' + d], { 1: 'look', 3: 'look' }), prod(2, 1)] },
        { mood: 'work', msg: `Product 3: (a + b)(c + d) = ${a + b} × ${c + d} = <b>${sum}</b>.`, layers: [card(['a ' + a, 'b ' + b, 'c ' + c, 'd ' + d], { 0: 'look', 1: 'look', 2: 'look', 3: 'look' }), prod(3, 2)] },
        { mood: 'wow', fx: 'burst', msg: `The middle part ad + bc = ${sum} − ${ac} − ${bd} = <b>${mid}</b>, with no fourth product!`, layers: [prod(3), { t: 'row', label: 'ad + bc', cells: [mid], cls: { 0: 'yes' }, idx: false }] },
        { mood: 'wow', fx: 'rain', msg: `Combine: ${ac} × ${p * p} + ${mid} × ${p} + ${bd} = <b>${r}</b>. ${r === x * y ? 'Correct!' : ''} Each product is split again the same way, so n digits cost about n<sup>1.585</sup> small products instead of n².`, layers: [{ t: 'row', label: 'Answer', cells: [r], cls: { 0: 'yes' }, idx: false }] },
      ];
    }
  });
})();
'''

INFO = {
    'title': 'Split, solve, combine',
    'panels': [
        {'s': [['e', '✂️'], ['t', 'divide → conquer → combine', {'b': 1}]], 'h': 'Divide and conquer', 't': 'Solve smaller copies, then merge the answers.', 'more': 'The parts do not overlap. If they did, dynamic programming would be the better tool.'},
        {'s': [['e', '🔀'], ['t', '+ (left items still waiting)', {'b': 1}]], 'h': 'Inversions', 't': 'Merge sort counts out of order pairs.', 'more': 'O(n log n) instead of checking all n² pairs.'},
        {'s': [['e', '📐'], ['t', 'compare a with bᵈ', {'b': 1}]], 'h': 'Master theorem', 't': 'Root, leaves, or every level equal.', 'more': 'T(n) = a T(n/b) + nᵈ gives nᵈ log n, n^(log_b a) or nᵈ.'},
        {'s': [['e', '✖️'], ['t', '3 products, not 4', {'b': 1}]], 'h': 'Karatsuba', 't': 'One saved product per level.', 'more': 'n^1.585 digit products instead of n².'},
    ],
    'remember': 'Split the input into parts that do not overlap, solve each part the same way, and spend your cleverness on the combine step. The recurrence a T(n/b) + f(n) tells you the running time.',
}

REAL = [
    ['📚', 'Sorting a huge stack of exam papers', 'Teachers split the pile, sort each part, and merge the sorted piles. That is merge sort done by people.'],
    ['🗺️', 'Finding the nearest taxi', 'Map apps split the city into regions and only compare taxis near the border of your region, like the closest pair strip.'],
    ['🔢', 'Multiplying huge numbers', 'Python and cryptography libraries use Karatsuba for numbers with hundreds of digits, because three products beat four at every level.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to divide and conquer. You split a problem into smaller copies of itself, solve the copies, and combine their answers. You will count inversions with merge sort, read running times with the master theorem, find the k-th smallest with quickselect, find the best run of numbers, the closest pair of points, and multiply big numbers with Karatsuba.'},
    {'id': 'divide-conquer-combine', 'h': 'Divide, conquer, combine', 'en': 'Divide and conquer has three steps. Divide the input into parts, usually two halves. Conquer each part by solving it the same way, until the parts are tiny. Combine the answers of the parts into the answer for the whole. To find the biggest number, each half reports its biggest and you keep the larger one.'},
    {'id': 'inversions', 'h': 'Inversions', 'en': 'An inversion is a pair of numbers that is out of order. Merge sort counts them while it merges. When a number from the right half is placed before numbers still waiting in the left half, it jumps over all of them, and each jump is one inversion. The total comes out in n log n time.'},
    {'id': 'master-theorem', 'h': 'Master theorem', 'en': 'A divide and conquer running time looks like a times T of n over b, plus n to the power d. Compare a with b to the power d. If they are equal, every level of the tree does the same work and you get n to the d times log n. If a is bigger, the leaves win. If a is smaller, the root wins.'},
    {'id': 'quickselect', 'h': 'Quickselect', 'en': 'Quickselect finds the k-th smallest number without sorting everything. Partition around a pivot so that smaller numbers go left. The pivot lands in its final place. If that place is k, you are done. Otherwise keep only the side that holds k. On average the work halves each round, so the total is linear.'},
    {'id': 'max-subarray', 'h': 'Maximum subarray', 'en': 'The best run of neighbouring numbers is either in the left half, in the right half, or it crosses the middle. The halves are smaller copies of the problem. The crossing run is found by growing left from the middle and right from the middle and keeping the best totals. The answer is the largest of the three.'},
    {'id': 'closest-pair', 'h': 'Closest pair', 'en': 'To find the two closest points, sort them by x and split them with a vertical line. Solve each side and take the smaller distance, d. A closer pair across the line must lie inside a strip of width d around the line, and each strip point only needs a few neighbours checked.'},
    {'id': 'karatsuba', 'h': 'Karatsuba', 'en': 'Split each number into a front half and a back half. The product needs a times c, b times d, and the middle part a d plus b c. Karatsuba gets the middle part from a plus b times c plus d, minus the other two products. Three products instead of four, at every level, gives n to the power one point five eight five.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from majority element and building a balanced tree up to reverse pairs and the median of two sorted arrays. Each one is solved in Python, JavaScript, Java and TypeScript, and you can replay every solution line by line.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. For each problem, first say how you will split the input, what the base case is, and how two answers combine into one. Then write the code. Open the hint if you are stuck.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'What are the three steps of divide and conquer?', 'o': ['Choose, explore, unchoose', 'Divide, conquer, combine', 'Push, pop, peek', 'Sort, search, swap'], 'a': 1, 'hint': 'Split, solve, merge.', 'why': 'Divide the input, conquer each part recursively, combine the answers.'},
    {'lv': 'e', 'q': 'Which of these is a divide and conquer algorithm?', 'o': ['Bubble sort', 'Merge sort', 'Linear search', 'Insertion sort'], 'a': 1, 'hint': 'It splits the list in half.', 'why': 'Merge sort splits, sorts each half recursively and merges them.'},
    {'lv': 'e', 'q': 'How many inversions does 3 1 2 have?', 'o': ['1', '2', '3', '0'], 'a': 1, 'hint': 'List the pairs that are out of order.', 'why': '(3, 1) and (3, 2) are out of order. (1, 2) is fine.'},
    {'lv': 'e', 'q': 'Quickselect keeps searching in how many sides after each partition?', 'o': ['Both', 'One', 'None', 'Three'], 'a': 1, 'hint': 'The answer is only on one side of the pivot.', 'why': 'Unlike quick sort, quickselect throws away the side that cannot hold index k.'},
    {'lv': 'm', 'q': 'Merge sort has T(n) = 2 T(n/2) + n. What is its running time?', 'o': ['O(n)', 'O(n log n)', 'O(n²)', 'O(log n)'], 'a': 1, 'hint': 'a = 2, b = 2, d = 1.', 'why': 'a = b^d = 2, so every level does n work, and there are log₂ n levels.'},
    {'lv': 'm', 'q': 'T(n) = T(n/2) + 1. What is the running time?', 'o': ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)'], 'a': 1, 'hint': 'This is binary search.', 'why': 'One sub problem of half the size with constant work: log₂ n levels of O(1).'},
    {'lv': 'm', 'q': 'In maximum subarray by divide and conquer, where must the crossing run start and end?', 'o': ['Anywhere', 'It must contain both a[mid] and a[mid + 1]', 'At index 0', 'At the last index'], 'a': 1, 'hint': 'It crosses the middle.', 'why': 'A run that crosses the middle includes the last item of the left half and the first item of the right half.'},
    {'lv': 'm', 'q': 'Why does the closest pair code compare squared distances?', 'o': ['It is more accurate', 'It avoids square roots and keeps whole numbers', 'It is required by Python', 'It finds a different pair'], 'a': 1, 'hint': 'Squaring keeps the order of distances.', 'why': 'If d1 < d2 then d1² < d2², so the same pair wins without any square root.'},
    {'lv': 'h', 'q': 'Karatsuba has T(n) = 3 T(n/2) + n. What is its running time?', 'o': ['O(n log n)', 'O(n^1.585)', 'O(n²)', 'O(n³)'], 'a': 1, 'hint': 'a = 3 is bigger than b^d = 2.', 'why': 'The leaves win: n^(log₂ 3) ≈ n^1.585.'},
    {'lv': 'h', 'q': 'Finding the max by splitting in half has T(n) = 2 T(n/2) + 1. What is its running time?', 'o': ['O(log n)', 'O(n)', 'O(n log n)', 'O(1)'], 'a': 1, 'hint': 'a = 2 is bigger than b^d = 1.', 'why': 'The leaves win: n^(log₂ 2) = n. There are n leaves and n − 1 combine steps.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'def f(a):\n    if len(a) == 1:\n        return a[0]\n    m = len(a) // 2\n    return f(a[:m]) + f(a[m:])\n\nprint(f([1, 2, 3, 4, 5]))', 'o': ['5', '15', '10', '120'], 'a': 1, 'hint': 'Each half returns its sum.', 'why': 'It adds the sums of both halves, so the result is 1 + 2 + 3 + 4 + 5 = 15.'},
    {'lv': 'h', 'q': 'When is quickselect O(n²)?', 'o': ['Never', 'When the pivot is always the smallest or biggest value', 'When k is 0', 'When the list has duplicates only'], 'a': 1, 'hint': 'Each round then removes just one item.', 'why': 'A pivot at an extreme removes only itself each round: n + (n − 1) + ... is O(n²). Random pivots make this very unlikely.'},
    {'lv': 'x', 'q': 'How many inversions does the list n, n − 1, ..., 2, 1 have?', 'o': ['n', 'n − 1', 'n(n − 1) / 2', 'n²'], 'a': 2, 'hint': 'Every pair is out of order.', 'why': 'All n(n − 1) / 2 pairs are inversions. For 6 5 4 3 2 1 that is 15.'},
    {'lv': 'x', 'q': 'Strassen multiplies matrices with 7 half size products instead of 8. What is its running time?', 'o': ['O(n³)', 'O(n^2.807)', 'O(n²)', 'O(n² log n)'], 'a': 1, 'hint': 'T(n) = 7 T(n/2) + n².', 'why': 'a = 7 is bigger than b^d = 4, so the leaves win: n^(log₂ 7) ≈ n^2.807.'},
    {'lv': 'x', 'q': 'Why can each strip point in closest pair stop after a few neighbours sorted by y?', 'o': ['The strip is always tiny', 'Points closer than d in y must fit in a small box, and only a few points with distance at least d fit in it', 'Because of sorting', 'It cannot'], 'a': 1, 'hint': 'Points on the same side are at least d apart.', 'why': 'Inside a d by 2d box, points on each side are at least d apart, so at most a handful fit. That keeps the strip work linear.'},
    {'lv': 'x', 'q': 'Median of Two Sorted Arrays drops about k / 2 values each step. How many steps does it take?', 'o': ['O(m + n)', 'O(log(m + n))', 'O(m · n)', 'O(1)'], 'a': 1, 'hint': 'k starts near (m + n) / 2 and halves.', 'why': 'k halves every step, so about log₂ of (m + n) steps are needed.'},
]

CALC = [
    {'lv': 'e', 'q': 'How many inversions does 4 3 2 1 have?', 'ans': '6', 'hint': 'Every pair is out of order.', 'steps': ['<span class="eq">4 × 3 ÷ 2 = 6</span>']},
    {'lv': 'e', 'q': 'Finding the max of 8 numbers by halving, how many boxes (calls) are there?', 'ans': '15', 'hint': '8 leaves and 7 combine steps.', 'steps': ['<span class="eq">2 × 8 − 1 = 15</span>']},
    {'lv': 'm', 'q': 'Merge sort with T(1) = 1 and T(n) = 2 T(n/2) + n. What is T(16)?', 'ans': '80', 'hint': 'T(n) = n log₂ n + n for powers of 2.', 'steps': ['<span class="eq">16 × 4 + 16 = 80</span>', 'The lesson program prints the same value.']},
    {'lv': 'm', 'q': 'How many levels does merge sort have for 1024 items, counting the level of single items?', 'ans': '11', 'hint': 'log₂ 1024 = 10 splits.', 'steps': ['<span class="eq">log₂ 1024 + 1 = 10 + 1 = 11</span>']},
    {'lv': 'h', 'q': 'With M(1) = 1 and M(n) = 3 M(n/2), how many one digit products does Karatsuba need for 64 digit numbers?', 'ans': '729', 'hint': '64 = 2⁶.', 'steps': ['<span class="eq">3⁶ = 729</span>', 'School multiplication needs <span class="eq">64² = 4096</span>.']},
    {'lv': 'h', 'q': 'Brute force closest pair on 8 points checks how many pairs?', 'ans': '28', 'hint': 'n(n − 1) / 2.', 'steps': ['<span class="eq">8 × 7 ÷ 2 = 28</span>']},
    {'lv': 'x', 'q': 'Quickselect with perfect pivots on 1000 items. About how many comparisons in total, rounded to the nearest hundred?', 'ans': '2000', 'hint': 'n + n/2 + n/4 + ... approaches 2n.', 'steps': ['<span class="eq">1000 + 500 + 250 + ... ≈ 2 × 1000 = 2000</span>']},
    {'lv': 'x', 'q': 'For T(n) = 4 T(n/2) + n², what is the exponent of n in the answer, ignoring the log factor?', 'ans': '2', 'hint': 'Compare a = 4 with b^d = 2².', 'steps': ['a = 4 and b<sup>d</sup> = 4 are equal, so every level does n² work.', '<span class="eq">T(n) = O(n² log n)</span>, exponent 2.']},
]

TALK = {
    'divide-conquer-combine': 'Imagine your teacher hands you a pile of one hundred exam papers and asks you to find the highest score. You could look at every paper yourself. Or you could split the pile in two and give each half to a friend. Each friend splits their half again and passes it on, until someone is holding a single paper. That person simply reads the score out. Then the answers travel back. Every helper compares the two scores they receive and passes the higher one up. This way of working is called divide and conquer. Divide means cutting the problem into smaller pieces. Conquer means solving each piece the same way. Combine means joining the answers. The pieces never share any papers, and that is what makes divide and conquer different from dynamic programming. Many of the fastest algorithms you know, such as merge sort, quick sort and binary search, are built on exactly these three steps.',
    'inversions': 'Suppose you and a friend each rank five songs from favourite to least favourite. How similar is your taste? One way to measure it is to count inversions. An inversion is a pair of songs that your friend placed in the opposite order to you. Zero inversions means you agree completely. Checking every pair one by one is slow for long lists. Merge sort can count them almost for free. While merging two sorted halves, look at what happens when a number from the right half is placed before the numbers still waiting in the left half. It jumps over every one of them, and every jump is one inversion. So you add the number of waiting left items to your count. The list gets sorted and the inversions get counted in the same n log n time. Recommendation systems and ranking competitions use this exact idea to compare orderings.',
    'master-theorem': 'How fast is a divide and conquer algorithm? Picture its recursion as a tree. The root is the whole problem. It splits into a smaller problems, each b times smaller, and each of those splits again. On every level there is some work for dividing and combining. Now ask a simple question: which level does most of the work? If every level does about the same amount, like merge sort, you multiply that amount by the number of levels and get n log n. If the number of sub problems grows faster than they shrink, like Karatsuba with three halves, the leaves at the bottom do most of the work. If the work at the root is the biggest, like quickselect, the root alone decides the answer and the rest adds up to less. The master theorem turns this into a rule. Compare a with b to the power d, and read off the answer.',
    'quickselect': 'Imagine a class of thirty students lining up by height, and you only want to know who is exactly in the middle. Do you really need to sort the whole line? No. Pick one student as the pivot and ask everyone shorter to stand on the left and everyone taller on the right. Now the pivot is in exactly the right place. If the pivot is in the middle position, you are done. If the middle is further right, you can forget about everyone on the left and repeat with the right group only. That is quickselect. Quick sort would sort both groups, but quickselect only follows the group that contains the answer. With a fair pivot the group halves each round, so the total work is about twice the length of the list. Picking the pivot at random protects you from very unlucky choices that would make it slow.',
    'max-subarray': 'Imagine a shop that writes down its profit or loss every day. On some days it makes money, on others it loses some. The owner asks: which stretch of days in a row made the most money altogether? Divide and conquer answers it neatly. Split the days into the first half and the second half. The best stretch is either completely in the first half, completely in the second half, or it starts in the first half and ends in the second, crossing the middle. The first two cases are just smaller versions of the same question. For the crossing case, start at the middle and walk left, adding up as you go and remembering the best total. Then do the same walking right. Put the two best totals together. Finally, pick the biggest of the three answers. There is an even faster single scan called Kadane, which the practice problem uses to double check.',
    'closest-pair': 'Picture a map with many taxis on it, and you want to find the two taxis that are nearest to each other. Measuring the distance between every pair works, but with a thousand taxis that is half a million measurements. Divide and conquer does better. Sort the taxis from west to east and draw a line down the middle. Find the closest pair on the left side and the closest pair on the right side. Call the smaller distance d. The only pairs that could be even closer must cross the line, and both taxis must be within d of the line. So you only look at a narrow strip around the line. Sort the strip from south to north, and each taxi only needs to be compared with the next few. Because comparing squared distances gives the same winner, the code never needs a square root, and every number stays a whole number.',
    'karatsuba': 'At school you learned to multiply two four digit numbers by multiplying every digit with every digit, which is sixteen small multiplications. In nineteen sixty, a young student named Anatoly Karatsuba found a shortcut. Split each number into a front half and a back half. Call them a and b for the first number, and c and d for the second. The answer needs a times c, b times d, and the middle part, a times d plus b times c. That looks like four multiplications. Karatsuba noticed that if you multiply a plus b by c plus d, and then subtract the other two products, you get the middle part for free. So three multiplications are enough. Saving one out of four may sound small, but it happens again inside every smaller multiplication. For numbers with thousands of digits it saves a huge amount of work, which is why Python uses it for very large numbers.',
    'leetcode': 'The LeetCode problems in this chapter let you practise splitting problems in half. You start by finding the majority element, the value that appears in more than half of a list, by asking each half for its winner. Then you build a perfectly balanced search tree from a sorted list by making the middle value the root. Next you find the best run of numbers with the left, right and crossing idea, and you find the k-th largest value with quickselect. The hard problems ask you to sort a linked list with merge sort, and to list every result of an expression by trying each operator as the last step. The expert problems count special pairs inside merge sort, and find the median of two sorted lists by throwing away half of the remaining search each step. Each one has a hint, an explanation and code in Python, JavaScript, Java and TypeScript.',
}

T = t.finish({
    'slug': 'divide-and-conquer', 'title': 'Divide and Conquer', 'short': 'Divide and conquer', 'emoji': '✂️', 'topic': 'divide-and-conquer', 'prefix': 'dsadc',
    'module': ('🔁', 'Recursion and smart searching'),
    'lead': 'Split a problem into smaller copies, solve them, and combine the answers. Count inversions with merge sort, read running times with the master theorem, find the k-th smallest with quickselect, and solve the best run, the closest pair of points and fast multiplication.',
    'desc': 'Divide and conquer in DSA: divide, conquer and combine, counting inversions with merge sort, the master theorem, quickselect, maximum subarray, the closest pair of points and Karatsuba multiplication, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 24,
    'summary': 'Divide, conquer and combine, counting inversions with merge sort, the master theorem, quickselect, maximum subarray, the closest pair of points and Karatsuba multiplication. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['divide and conquer', 'merge sort', 'inversions', 'master theorem', 'recurrence', 'quickselect', 'kth smallest', 'maximum subarray', 'closest pair of points', 'karatsuba', 'majority element', 'median of two sorted arrays', 'reverse pairs', 'recursion tree'],
    'added': '2026-11-22',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS, 'css': '.grid3{display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin:10px 0}',
    'prev': ('backtracking', 'backtracking', '🐭 Backtracking'),
    'next': ('trees', 'trees', '🌲 Trees'),
})
