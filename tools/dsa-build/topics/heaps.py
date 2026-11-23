# Heaps in depth: sift up and sift down, building a heap in O(n), heap sort, top k with a small heap,
# merging k sorted lists, the running median with two heaps, and scheduling with a heap of end times.
from kit4 import Topic

t = Topic()

# a small binary heap for the JavaScript and TypeScript programs, which have no heap built in
JS_HEAP = r'''
class Heap {
  constructor(less) { this.a = []; this.less = less; }   // less(x, y) is true when x should come out first
  get size() { return this.a.length; }
  peek() { return this.a[0]; }
  push(x) {
    const a = this.a;
    a.push(x);
    let i = a.length - 1;
    while (i > 0) {                                        // sift up
      const p = (i - 1) >> 1;
      if (!this.less(a[i], a[p])) break;
      [a[i], a[p]] = [a[p], a[i]];
      i = p;
    }
  }
  pop() {
    const a = this.a, top = a[0], last = a.pop();
    if (a.length) {
      a[0] = last;
      let i = 0;
      for (;;) {                                           // sift down
        const l = 2 * i + 1, r = l + 1;
        let s = i;
        if (l < a.length && this.less(a[l], a[s])) s = l;
        if (r < a.length && this.less(a[r], a[s])) s = r;
        if (s === i) break;
        [a[i], a[s]] = [a[s], a[i]];
        i = s;
      }
    }
    return top;
  }
}
'''

TS_HEAP = r'''
class Heap<T> {
  a: T[] = [];
  less: (x: T, y: T) => boolean;                           // true when x should come out first
  constructor(less: (x: T, y: T) => boolean) { this.less = less; }
  get size(): number { return this.a.length; }
  peek(): T { return this.a[0]; }
  push(x: T): void {
    const a = this.a;
    a.push(x);
    let i = a.length - 1;
    while (i > 0) {                                        // sift up
      const p = (i - 1) >> 1;
      if (!this.less(a[i], a[p])) break;
      [a[i], a[p]] = [a[p], a[i]];
      i = p;
    }
  }
  pop(): T {
    const a = this.a, top = a[0], last = a.pop() as T;
    if (a.length) {
      a[0] = last;
      let i = 0;
      for (;;) {                                           // sift down
        const l = 2 * i + 1, r = l + 1;
        let s = i;
        if (l < a.length && this.less(a[l], a[s])) s = l;
        if (r < a.length && this.less(a[r], a[s])) s = r;
        if (s === i) break;
        [a[i], a[s]] = [a[s], a[i]];
        i = s;
      }
    }
    return top;
  }
}
'''

# ---------------------------------------------------------------- lesson programs
t.code('sift', py=r'''
class MinHeap:
    def __init__(self):
        self.a = []

    def push(self, x):
        a = self.a
        a.append(x)                           # add at the end of the last level
        i = len(a) - 1
        while i > 0 and a[(i - 1) // 2] > a[i]:
            p = (i - 1) // 2
            a[i], a[p] = a[p], a[i]           # sift up: swap with a bigger parent
            i = p

    def pop(self):
        a = self.a
        top = a[0]
        last = a.pop()
        if a:
            a[0] = last                       # the last leaf jumps to the root
            i = 0
            while True:
                l, r, s = 2 * i + 1, 2 * i + 2, i
                if l < len(a) and a[l] < a[s]:
                    s = l
                if r < len(a) and a[r] < a[s]:
                    s = r
                if s == i:
                    break                     # both children are bigger: it has settled
                a[i], a[s] = a[s], a[i]       # sift down: swap with the smaller child
                i = s
        return top


h = MinHeap()
for x in [5, 3, 8, 1, 9, 2]:
    h.push(x)
    print("push", x, " heap:", " ".join(map(str, h.a)))
while h.a:
    x = h.pop()
    print("pop ", x, " heap:", " ".join(map(str, h.a)))
''', js=r'''
class MinHeap {
  constructor() { this.a = []; }
  push(x) {
    const a = this.a;
    a.push(x);                                // add at the end of the last level
    let i = a.length - 1;
    while (i > 0 && a[Math.floor((i - 1) / 2)] > a[i]) {
      const p = Math.floor((i - 1) / 2);
      [a[i], a[p]] = [a[p], a[i]];            // sift up: swap with a bigger parent
      i = p;
    }
  }
  pop() {
    const a = this.a, top = a[0], last = a.pop();
    if (a.length) {
      a[0] = last;                            // the last leaf jumps to the root
      let i = 0;
      while (true) {
        const l = 2 * i + 1, r = 2 * i + 2;
        let s = i;
        if (l < a.length && a[l] < a[s]) s = l;
        if (r < a.length && a[r] < a[s]) s = r;
        if (s === i) break;                   // both children are bigger: it has settled
        [a[i], a[s]] = [a[s], a[i]];          // sift down: swap with the smaller child
        i = s;
      }
    }
    return top;
  }
}

const h = new MinHeap();
for (const x of [5, 3, 8, 1, 9, 2]) {
  h.push(x);
  console.log("push", x, " heap:", h.a.join(" "));
}
while (h.a.length) {
  const x = h.pop();
  console.log("pop ", x, " heap:", h.a.join(" "));
}
''', java=r'''
import java.util.*;

public class SiftUpDown {
    static List<Integer> a = new ArrayList<>();

    static void swap(int i, int j) { int t = a.get(i); a.set(i, a.get(j)); a.set(j, t); }

    static void push(int x) {
        a.add(x);                                        // add at the end of the last level
        int i = a.size() - 1;
        while (i > 0 && a.get((i - 1) / 2) > a.get(i)) {
            int p = (i - 1) / 2;
            swap(i, p);                                  // sift up: swap with a bigger parent
            i = p;
        }
    }

    static int pop() {
        int top = a.get(0);
        int last = a.remove(a.size() - 1);
        if (!a.isEmpty()) {
            a.set(0, last);                              // the last leaf jumps to the root
            int i = 0;
            while (true) {
                int l = 2 * i + 1, r = 2 * i + 2, s = i;
                if (l < a.size() && a.get(l) < a.get(s)) s = l;
                if (r < a.size() && a.get(r) < a.get(s)) s = r;
                if (s == i) break;                       // both children are bigger: it has settled
                swap(i, s);                              // sift down: swap with the smaller child
                i = s;
            }
        }
        return top;
    }

    static String show() {
        StringJoiner sj = new StringJoiner(" ");
        for (int x : a) sj.add(String.valueOf(x));
        return sj.toString();
    }

    public static void main(String[] args) {
        for (int x : new int[]{5, 3, 8, 1, 9, 2}) {
            push(x);
            System.out.println("push " + x + "  heap: " + show());
        }
        while (!a.isEmpty()) {
            int x = pop();
            System.out.println("pop  " + x + "  heap: " + show());
        }
    }
}
''', ts=r'''
class MinHeap {
  a: number[] = [];
  push(x: number): void {
    const a = this.a;
    a.push(x);                                // add at the end of the last level
    let i = a.length - 1;
    while (i > 0 && a[Math.floor((i - 1) / 2)] > a[i]) {
      const p = Math.floor((i - 1) / 2);
      [a[i], a[p]] = [a[p], a[i]];            // sift up: swap with a bigger parent
      i = p;
    }
  }
  pop(): number {
    const a = this.a, top = a[0], last = a.pop() as number;
    if (a.length) {
      a[0] = last;                            // the last leaf jumps to the root
      let i = 0;
      while (true) {
        const l = 2 * i + 1, r = 2 * i + 2;
        let s = i;
        if (l < a.length && a[l] < a[s]) s = l;
        if (r < a.length && a[r] < a[s]) s = r;
        if (s === i) break;                   // both children are bigger: it has settled
        [a[i], a[s]] = [a[s], a[i]];          // sift down: swap with the smaller child
        i = s;
      }
    }
    return top;
  }
}

const h = new MinHeap();
for (const x of [5, 3, 8, 1, 9, 2]) {
  h.push(x);
  console.log("push", x, " heap:", h.a.join(" "));
}
while (h.a.length) {
  const x = h.pop();
  console.log("pop ", x, " heap:", h.a.join(" "));
}
''')

t.code('heapify', py=r'''
swaps = 0


def sift_down(a, i, n):
    global swaps
    while True:
        l, r, s = 2 * i + 1, 2 * i + 2, i
        if l < n and a[l] < a[s]:
            s = l
        if r < n and a[r] < a[s]:
            s = r
        if s == i:
            return
        a[i], a[s] = a[s], a[i]
        swaps += 1
        i = s


def build_heap(vals):
    a = vals[:]
    for i in range(len(a) // 2 - 1, -1, -1):   # last parent first, leaves are heaps already
        sift_down(a, i, len(a))
    return a


def push_one_by_one(vals):
    global swaps
    a = []
    for x in vals:
        a.append(x)
        i = len(a) - 1
        while i > 0 and a[(i - 1) // 2] > a[i]:
            p = (i - 1) // 2
            a[i], a[p] = a[p], a[i]
            swaps += 1
            i = p
    return a


print("bottom up heap of 7..1:", " ".join(map(str, build_heap(list(range(7, 0, -1))))))
for n in (7, 15, 1023):
    vals = list(range(n, 0, -1))
    swaps = 0
    build_heap(vals)
    bottom_up = swaps
    swaps = 0
    push_one_by_one(vals)
    print("n =", n, " bottom up swaps:", bottom_up, " push one by one swaps:", swaps)
''', js=r'''
let swaps = 0;

function siftDown(a, i, n) {
  while (true) {
    const l = 2 * i + 1, r = 2 * i + 2;
    let s = i;
    if (l < n && a[l] < a[s]) s = l;
    if (r < n && a[r] < a[s]) s = r;
    if (s === i) return;
    [a[i], a[s]] = [a[s], a[i]];
    swaps++;
    i = s;
  }
}

function buildHeap(vals) {
  const a = [...vals];
  for (let i = Math.floor(a.length / 2) - 1; i >= 0; i--) siftDown(a, i, a.length);   // last parent first
  return a;
}

function pushOneByOne(vals) {
  const a = [];
  for (const x of vals) {
    a.push(x);
    let i = a.length - 1;
    while (i > 0 && a[Math.floor((i - 1) / 2)] > a[i]) {
      const p = Math.floor((i - 1) / 2);
      [a[i], a[p]] = [a[p], a[i]];
      swaps++;
      i = p;
    }
  }
  return a;
}

const down = n => Array.from({ length: n }, (_, i) => n - i);
console.log("bottom up heap of 7..1:", buildHeap(down(7)).join(" "));
for (const n of [7, 15, 1023]) {
  swaps = 0;
  buildHeap(down(n));
  const bottomUp = swaps;
  swaps = 0;
  pushOneByOne(down(n));
  console.log("n =", n, " bottom up swaps:", bottomUp, " push one by one swaps:", swaps);
}
''', java=r'''
import java.util.*;

public class BuildHeap {
    static int swaps = 0;

    static void siftDown(int[] a, int i, int n) {
        while (true) {
            int l = 2 * i + 1, r = 2 * i + 2, s = i;
            if (l < n && a[l] < a[s]) s = l;
            if (r < n && a[r] < a[s]) s = r;
            if (s == i) return;
            int t = a[i]; a[i] = a[s]; a[s] = t;
            swaps++;
            i = s;
        }
    }

    static int[] buildHeap(int[] vals) {
        int[] a = vals.clone();
        for (int i = a.length / 2 - 1; i >= 0; i--) siftDown(a, i, a.length);   // last parent first
        return a;
    }

    static int[] pushOneByOne(int[] vals) {
        int[] a = new int[vals.length];
        for (int n = 0; n < vals.length; n++) {
            a[n] = vals[n];
            int i = n;
            while (i > 0 && a[(i - 1) / 2] > a[i]) {
                int p = (i - 1) / 2;
                int t = a[i]; a[i] = a[p]; a[p] = t;
                swaps++;
                i = p;
            }
        }
        return a;
    }

    static int[] down(int n) {
        int[] v = new int[n];
        for (int i = 0; i < n; i++) v[i] = n - i;
        return v;
    }

    public static void main(String[] args) {
        StringJoiner sj = new StringJoiner(" ");
        for (int x : buildHeap(down(7))) sj.add(String.valueOf(x));
        System.out.println("bottom up heap of 7..1: " + sj);
        for (int n : new int[]{7, 15, 1023}) {
            swaps = 0;
            buildHeap(down(n));
            int bottomUp = swaps;
            swaps = 0;
            pushOneByOne(down(n));
            System.out.println("n = " + n + "  bottom up swaps: " + bottomUp + "  push one by one swaps: " + swaps);
        }
    }
}
''', ts=r'''
let swaps = 0;

function siftDown(a: number[], i: number, n: number): void {
  while (true) {
    const l = 2 * i + 1, r = 2 * i + 2;
    let s = i;
    if (l < n && a[l] < a[s]) s = l;
    if (r < n && a[r] < a[s]) s = r;
    if (s === i) return;
    [a[i], a[s]] = [a[s], a[i]];
    swaps++;
    i = s;
  }
}

function buildHeap(vals: number[]): number[] {
  const a = [...vals];
  for (let i = Math.floor(a.length / 2) - 1; i >= 0; i--) siftDown(a, i, a.length);   // last parent first
  return a;
}

function pushOneByOne(vals: number[]): number[] {
  const a: number[] = [];
  for (const x of vals) {
    a.push(x);
    let i = a.length - 1;
    while (i > 0 && a[Math.floor((i - 1) / 2)] > a[i]) {
      const p = Math.floor((i - 1) / 2);
      [a[i], a[p]] = [a[p], a[i]];
      swaps++;
      i = p;
    }
  }
  return a;
}

const down = (n: number): number[] => Array.from({ length: n }, (_, i) => n - i);
console.log("bottom up heap of 7..1:", buildHeap(down(7)).join(" "));
for (const n of [7, 15, 1023]) {
  swaps = 0;
  buildHeap(down(n));
  const bottomUp = swaps;
  swaps = 0;
  pushOneByOne(down(n));
  console.log("n =", n, " bottom up swaps:", bottomUp, " push one by one swaps:", swaps);
}
''')

t.code('heapsort', py=r'''
def heap_sort(vals):
    a = vals[:]
    n = len(a)

    def sift_down(i, size):                   # max heap this time: the biggest rises to the root
        while True:
            l, r, big = 2 * i + 1, 2 * i + 2, i
            if l < size and a[l] > a[big]:
                big = l
            if r < size and a[r] > a[big]:
                big = r
            if big == i:
                return
            a[i], a[big] = a[big], a[i]
            i = big

    for i in range(n // 2 - 1, -1, -1):       # 1. build a max heap in O(n)
        sift_down(i, n)
    for end in range(n - 1, 0, -1):           # 2. move the biggest to the end, shrink the heap
        a[0], a[end] = a[end], a[0]
        sift_down(0, end)
    return a


print(" ".join(map(str, heap_sort([7, 2, 9, 4, 1, 8, 3]))))
print(" ".join(map(str, heap_sort([5, 5, 1, 3, 3, 0]))))
''', js=r'''
function heapSort(vals) {
  const a = [...vals], n = a.length;
  function siftDown(i, size) {               // max heap this time: the biggest rises to the root
    while (true) {
      const l = 2 * i + 1, r = 2 * i + 2;
      let big = i;
      if (l < size && a[l] > a[big]) big = l;
      if (r < size && a[r] > a[big]) big = r;
      if (big === i) return;
      [a[i], a[big]] = [a[big], a[i]];
      i = big;
    }
  }
  for (let i = Math.floor(n / 2) - 1; i >= 0; i--) siftDown(i, n);   // 1. build a max heap in O(n)
  for (let end = n - 1; end > 0; end--) {                             // 2. biggest to the end, shrink
    [a[0], a[end]] = [a[end], a[0]];
    siftDown(0, end);
  }
  return a;
}

console.log(heapSort([7, 2, 9, 4, 1, 8, 3]).join(" "));
console.log(heapSort([5, 5, 1, 3, 3, 0]).join(" "));
''', java=r'''
import java.util.*;

public class HeapSort {
    static void siftDown(int[] a, int i, int size) {     // max heap this time: the biggest rises to the root
        while (true) {
            int l = 2 * i + 1, r = 2 * i + 2, big = i;
            if (l < size && a[l] > a[big]) big = l;
            if (r < size && a[r] > a[big]) big = r;
            if (big == i) return;
            int t = a[i]; a[i] = a[big]; a[big] = t;
            i = big;
        }
    }

    static int[] heapSort(int[] vals) {
        int[] a = vals.clone();
        int n = a.length;
        for (int i = n / 2 - 1; i >= 0; i--) siftDown(a, i, n);   // 1. build a max heap in O(n)
        for (int end = n - 1; end > 0; end--) {                    // 2. biggest to the end, shrink
            int t = a[0]; a[0] = a[end]; a[end] = t;
            siftDown(a, 0, end);
        }
        return a;
    }

    static String show(int[] a) {
        StringJoiner sj = new StringJoiner(" ");
        for (int x : a) sj.add(String.valueOf(x));
        return sj.toString();
    }

    public static void main(String[] args) {
        System.out.println(show(heapSort(new int[]{7, 2, 9, 4, 1, 8, 3})));
        System.out.println(show(heapSort(new int[]{5, 5, 1, 3, 3, 0})));
    }
}
''', ts=r'''
function heapSort(vals: number[]): number[] {
  const a = [...vals], n = a.length;
  function siftDown(i: number, size: number): void {   // max heap this time: the biggest rises to the root
    while (true) {
      const l = 2 * i + 1, r = 2 * i + 2;
      let big = i;
      if (l < size && a[l] > a[big]) big = l;
      if (r < size && a[r] > a[big]) big = r;
      if (big === i) return;
      [a[i], a[big]] = [a[big], a[i]];
      i = big;
    }
  }
  for (let i = Math.floor(n / 2) - 1; i >= 0; i--) siftDown(i, n);   // 1. build a max heap in O(n)
  for (let end = n - 1; end > 0; end--) {                             // 2. biggest to the end, shrink
    [a[0], a[end]] = [a[end], a[0]];
    siftDown(0, end);
  }
  return a;
}

console.log(heapSort([7, 2, 9, 4, 1, 8, 3]).join(" "));
console.log(heapSort([5, 5, 1, 3, 3, 0]).join(" "));
''')

t.code('topk', py=r'''
import heapq


def top_k_stream(stream, k):
    heap = []                                 # a min heap that holds the k biggest seen so far
    for x in stream:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:                     # bigger than the smallest of the top k
            heapq.heapreplace(heap, x)        # pop the smallest and push x in one step
        print("after", x, " top", k, ":", " ".join(map(str, sorted(heap, reverse=True))))
    return heap


top_k_stream([5, 1, 9, 3, 7, 2, 8, 6], 3)
''', js=JS_HEAP + r'''
function topKStream(stream, k) {
  const heap = new Heap((x, y) => x < y);    // a min heap that holds the k biggest seen so far
  for (const x of stream) {
    if (heap.size < k) heap.push(x);
    else if (x > heap.peek()) {               // bigger than the smallest of the top k
      heap.pop();
      heap.push(x);
    }
    console.log("after", x, " top", k, ":", [...heap.a].sort((p, q) => q - p).join(" "));
  }
}

topKStream([5, 1, 9, 3, 7, 2, 8, 6], 3);
''', java=r'''
import java.util.*;

public class TopKStream {
    public static void main(String[] args) {
        int k = 3;
        PriorityQueue<Integer> heap = new PriorityQueue<>();   // a min heap that holds the k biggest seen so far
        for (int x : new int[]{5, 1, 9, 3, 7, 2, 8, 6}) {
            if (heap.size() < k) heap.add(x);
            else if (x > heap.peek()) {                        // bigger than the smallest of the top k
                heap.poll();
                heap.add(x);
            }
            List<Integer> top = new ArrayList<>(heap);
            top.sort(Collections.reverseOrder());
            StringJoiner sj = new StringJoiner(" ");
            for (int v : top) sj.add(String.valueOf(v));
            System.out.println("after " + x + "  top " + k + " : " + sj);
        }
    }
}
''', ts=TS_HEAP + r'''
function topKStream(stream: number[], k: number): void {
  const heap = new Heap<number>((x, y) => x < y);   // a min heap that holds the k biggest seen so far
  for (const x of stream) {
    if (heap.size < k) heap.push(x);
    else if (x > heap.peek()) {               // bigger than the smallest of the top k
      heap.pop();
      heap.push(x);
    }
    console.log("after", x, " top", k, ":", [...heap.a].sort((p, q) => q - p).join(" "));
  }
}

topKStream([5, 1, 9, 3, 7, 2, 8, 6], 3);
''')

t.code('kmerge', py=r'''
import heapq


def merge_k(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]   # the head of every list
    heapq.heapify(heap)
    out = []
    while heap:
        val, i, j = heapq.heappop(heap)       # the smallest head among all lists
        out.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))   # its list sends the next value
    return out


print(" ".join(map(str, merge_k([[1, 4, 7], [2, 5, 8], [0, 3, 6, 9]]))))
print(" ".join(map(str, merge_k([[10], [], [1, 2, 3]]))))
''', js=JS_HEAP + r'''
function mergeK(lists) {
  // order by value, then by list number, so ties come out the same way every time
  const heap = new Heap((x, y) => x[0] < y[0] || (x[0] === y[0] && x[1] < y[1]));
  lists.forEach((lst, i) => { if (lst.length) heap.push([lst[0], i, 0]); });   // the head of every list
  const out = [];
  while (heap.size) {
    const [val, i, j] = heap.pop();           // the smallest head among all lists
    out.push(val);
    if (j + 1 < lists[i].length) heap.push([lists[i][j + 1], i, j + 1]);   // its list sends the next value
  }
  return out;
}

console.log(mergeK([[1, 4, 7], [2, 5, 8], [0, 3, 6, 9]]).join(" "));
console.log(mergeK([[10], [], [1, 2, 3]]).join(" "));
''', java=r'''
import java.util.*;

public class MergeK {
    static List<Integer> mergeK(int[][] lists) {
        // entries are {value, list number, index}, ordered by value then list number
        PriorityQueue<int[]> heap = new PriorityQueue<>((x, y) -> x[0] != y[0] ? Integer.compare(x[0], y[0]) : Integer.compare(x[1], y[1]));
        for (int i = 0; i < lists.length; i++) if (lists[i].length > 0) heap.add(new int[]{lists[i][0], i, 0});
        List<Integer> out = new ArrayList<>();
        while (!heap.isEmpty()) {
            int[] e = heap.poll();                       // the smallest head among all lists
            out.add(e[0]);
            int i = e[1], j = e[2];
            if (j + 1 < lists[i].length) heap.add(new int[]{lists[i][j + 1], i, j + 1});   // its list sends the next value
        }
        return out;
    }

    static String show(List<Integer> a) {
        StringJoiner sj = new StringJoiner(" ");
        for (int x : a) sj.add(String.valueOf(x));
        return sj.toString();
    }

    public static void main(String[] args) {
        System.out.println(show(mergeK(new int[][]{{1, 4, 7}, {2, 5, 8}, {0, 3, 6, 9}})));
        System.out.println(show(mergeK(new int[][]{{10}, {}, {1, 2, 3}})));
    }
}
''', ts=TS_HEAP + r'''
type Entry = [number, number, number];   // value, list number, index in that list

function mergeK(lists: number[][]): number[] {
  // order by value, then by list number, so ties come out the same way every time
  const heap = new Heap<Entry>((x, y) => x[0] < y[0] || (x[0] === y[0] && x[1] < y[1]));
  lists.forEach((lst, i) => { if (lst.length) heap.push([lst[0], i, 0]); });   // the head of every list
  const out: number[] = [];
  while (heap.size) {
    const [val, i, j] = heap.pop();           // the smallest head among all lists
    out.push(val);
    if (j + 1 < lists[i].length) heap.push([lists[i][j + 1], i, j + 1]);   // its list sends the next value
  }
  return out;
}

console.log(mergeK([[1, 4, 7], [2, 5, 8], [0, 3, 6, 9]]).join(" "));
console.log(mergeK([[10], [], [1, 2, 3]]).join(" "));
''')

t.code('median', py=r'''
import heapq

low, high = [], []                            # low is a max heap (stored negated), high is a min heap


def add(x):
    if not low or x <= -low[0]:
        heapq.heappush(low, -x)
    else:
        heapq.heappush(high, x)
    if len(low) > len(high) + 1:              # keep the sizes equal, or low one bigger
        heapq.heappush(high, -heapq.heappop(low))
    elif len(high) > len(low):
        heapq.heappush(low, -heapq.heappop(high))


def median():
    if len(low) > len(high):
        return float(-low[0])
    return (-low[0] + high[0]) / 2


for x in [5, 15, 1, 3, 8, 7, 9, 10]:
    add(x)
    print("add", x, " median", f"{median():.1f}")
''', js=JS_HEAP + r'''
const low = new Heap((x, y) => x > y);       // a max heap for the smaller half
const high = new Heap((x, y) => x < y);      // a min heap for the bigger half

function add(x) {
  if (!low.size || x <= low.peek()) low.push(x);
  else high.push(x);
  if (low.size > high.size + 1) high.push(low.pop());   // keep the sizes equal, or low one bigger
  else if (high.size > low.size) low.push(high.pop());
}

const median = () => (low.size > high.size ? low.peek() : (low.peek() + high.peek()) / 2);

for (const x of [5, 15, 1, 3, 8, 7, 9, 10]) {
  add(x);
  console.log("add", x, " median", median().toFixed(1));
}
''', java=r'''
import java.util.*;

public class RunningMedian {
    static PriorityQueue<Integer> low = new PriorityQueue<>(Collections.reverseOrder());   // max heap, smaller half
    static PriorityQueue<Integer> high = new PriorityQueue<>();                            // min heap, bigger half

    static void add(int x) {
        if (low.isEmpty() || x <= low.peek()) low.add(x);
        else high.add(x);
        if (low.size() > high.size() + 1) high.add(low.poll());   // keep the sizes equal, or low one bigger
        else if (high.size() > low.size()) low.add(high.poll());
    }

    static double median() {
        return low.size() > high.size() ? low.peek() : (low.peek() + high.peek()) / 2.0;
    }

    public static void main(String[] args) {
        for (int x : new int[]{5, 15, 1, 3, 8, 7, 9, 10}) {
            add(x);
            System.out.println("add " + x + "  median " + String.format("%.1f", median()));
        }
    }
}
''', ts=TS_HEAP + r'''
const low = new Heap<number>((x, y) => x > y);    // a max heap for the smaller half
const high = new Heap<number>((x, y) => x < y);   // a min heap for the bigger half

function add(x: number): void {
  if (!low.size || x <= low.peek()) low.push(x);
  else high.push(x);
  if (low.size > high.size + 1) high.push(low.pop());   // keep the sizes equal, or low one bigger
  else if (high.size > low.size) low.push(high.pop());
}

const median = (): number => (low.size > high.size ? low.peek() : (low.peek() + high.peek()) / 2);

for (const x of [5, 15, 1, 3, 8, 7, 9, 10]) {
  add(x);
  console.log("add", x, " median", median().toFixed(1));
}
''')

t.code('rooms', py=r'''
import heapq


def min_rooms(meetings):
    ends = []                                 # a min heap of end times, one per busy room
    for start, end in sorted(meetings):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)      # the earliest room is free again: reuse it
        else:
            heapq.heappush(ends, end)         # every room is busy: open a new one
        print(f"meeting {start}-{end}: rooms busy until", " ".join(map(str, sorted(ends))))
    return len(ends)


print("rooms needed:", min_rooms([(9, 10), (9, 12), (10, 11), (11, 13), (12, 14), (13, 15)]))
''', js=JS_HEAP + r'''
function minRooms(meetings) {
  const ends = new Heap((x, y) => x < y);    // a min heap of end times, one per busy room
  for (const [start, end] of [...meetings].sort((p, q) => p[0] - q[0] || p[1] - q[1])) {
    if (ends.size && ends.peek() <= start) {
      ends.pop();                             // the earliest room is free again: reuse it
      ends.push(end);
    } else ends.push(end);                    // every room is busy: open a new one
    console.log(`meeting ${start}-${end}: rooms busy until`, [...ends.a].sort((p, q) => p - q).join(" "));
  }
  return ends.size;
}

console.log("rooms needed:", minRooms([[9, 10], [9, 12], [10, 11], [11, 13], [12, 14], [13, 15]]));
''', java=r'''
import java.util.*;

public class MeetingRooms {
    static int minRooms(int[][] meetings) {
        int[][] m = meetings.clone();
        Arrays.sort(m, (p, q) -> p[0] != q[0] ? p[0] - q[0] : p[1] - q[1]);
        PriorityQueue<Integer> ends = new PriorityQueue<>();      // a min heap of end times, one per busy room
        for (int[] mt : m) {
            if (!ends.isEmpty() && ends.peek() <= mt[0]) ends.poll();   // the earliest room is free again: reuse it
            ends.add(mt[1]);                                       // or open a new one
            List<Integer> s = new ArrayList<>(ends);
            Collections.sort(s);
            StringJoiner sj = new StringJoiner(" ");
            for (int x : s) sj.add(String.valueOf(x));
            System.out.println("meeting " + mt[0] + "-" + mt[1] + ": rooms busy until " + sj);
        }
        return ends.size();
    }

    public static void main(String[] args) {
        int[][] meetings = {{9, 10}, {9, 12}, {10, 11}, {11, 13}, {12, 14}, {13, 15}};
        System.out.println("rooms needed: " + minRooms(meetings));
    }
}
''', ts=TS_HEAP + r'''
function minRooms(meetings: Array<[number, number]>): number {
  const ends = new Heap<number>((x, y) => x < y);   // a min heap of end times, one per busy room
  for (const [start, end] of [...meetings].sort((p, q) => p[0] - q[0] || p[1] - q[1])) {
    if (ends.size && ends.peek() <= start) {
      ends.pop();                             // the earliest room is free again: reuse it
      ends.push(end);
    } else ends.push(end);                    // every room is busy: open a new one
    console.log(`meeting ${start}-${end}: rooms busy until`, [...ends.a].sort((p, q) => p - q).join(" "));
  }
  return ends.size;
}

console.log("rooms needed:", minRooms([[9, 10], [9, 12], [10, 11], [11, 13], [12, 14], [13, 15]]));
''')

# ---------------------------------------------------------------- LeetCode practice programs
t.code('p_stones', py=r'''
import heapq


def last_stone_weight(stones):
    heap = [-s for s in stones]               # heapq is a min heap, so store negatives for a max heap
    heapq.heapify(heap)
    while len(heap) > 1:
        y = -heapq.heappop(heap)              # the heaviest stone
        x = -heapq.heappop(heap)              # the second heaviest
        if y != x:
            heapq.heappush(heap, -(y - x))    # what is left of the heavier stone goes back
    return -heap[0] if heap else 0


print(last_stone_weight([2, 7, 4, 1, 8, 1]))
print(last_stone_weight([1]))
print(last_stone_weight([3, 3]))
''', js=JS_HEAP + r'''
function lastStoneWeight(stones) {
  const heap = new Heap((x, y) => x > y);    // a max heap
  for (const s of stones) heap.push(s);
  while (heap.size > 1) {
    const y = heap.pop(), x = heap.pop();     // the two heaviest stones
    if (y !== x) heap.push(y - x);            // what is left of the heavier stone goes back
  }
  return heap.size ? heap.peek() : 0;
}

console.log(lastStoneWeight([2, 7, 4, 1, 8, 1]));
console.log(lastStoneWeight([1]));
console.log(lastStoneWeight([3, 3]));
''', java=r'''
import java.util.*;

public class LastStone {
    static int lastStoneWeight(int[] stones) {
        PriorityQueue<Integer> heap = new PriorityQueue<>(Collections.reverseOrder());   // a max heap
        for (int s : stones) heap.add(s);
        while (heap.size() > 1) {
            int y = heap.poll(), x = heap.poll();        // the two heaviest stones
            if (y != x) heap.add(y - x);                 // what is left of the heavier stone goes back
        }
        return heap.isEmpty() ? 0 : heap.peek();
    }

    public static void main(String[] args) {
        System.out.println(lastStoneWeight(new int[]{2, 7, 4, 1, 8, 1}));
        System.out.println(lastStoneWeight(new int[]{1}));
        System.out.println(lastStoneWeight(new int[]{3, 3}));
    }
}
''', ts=TS_HEAP + r'''
function lastStoneWeight(stones: number[]): number {
  const heap = new Heap<number>((x, y) => x > y);   // a max heap
  for (const s of stones) heap.push(s);
  while (heap.size > 1) {
    const y = heap.pop(), x = heap.pop();     // the two heaviest stones
    if (y !== x) heap.push(y - x);            // what is left of the heavier stone goes back
  }
  return heap.size ? heap.peek() : 0;
}

console.log(lastStoneWeight([2, 7, 4, 1, 8, 1]));
console.log(lastStoneWeight([1]));
console.log(lastStoneWeight([3, 3]));
''')

t.code('p_kthstream', py=r'''
import heapq


class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = []                        # a min heap of the k biggest values so far
        for x in nums:
            self.add(x)

    def add(self, val):
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, val)
        elif val > self.heap[0]:
            heapq.heapreplace(self.heap, val)
        return self.heap[0]                   # the smallest of the top k is the k-th largest


kth = KthLargest(3, [4, 5, 8, 2])
print(" ".join(str(kth.add(v)) for v in [3, 5, 10, 9, 4]))
''', js=JS_HEAP + r'''
class KthLargest {
  constructor(k, nums) {
    this.k = k;
    this.heap = new Heap((x, y) => x < y);   // a min heap of the k biggest values so far
    for (const x of nums) this.add(x);
  }
  add(val) {
    if (this.heap.size < this.k) this.heap.push(val);
    else if (val > this.heap.peek()) { this.heap.pop(); this.heap.push(val); }
    return this.heap.peek();                 // the smallest of the top k is the k-th largest
  }
}

const kth = new KthLargest(3, [4, 5, 8, 2]);
console.log([3, 5, 10, 9, 4].map(v => kth.add(v)).join(" "));
''', java=r'''
import java.util.*;

public class KthLargestStream {
    static class KthLargest {
        int k;
        PriorityQueue<Integer> heap = new PriorityQueue<>();   // a min heap of the k biggest values so far

        KthLargest(int k, int[] nums) {
            this.k = k;
            for (int x : nums) add(x);
        }

        int add(int val) {
            if (heap.size() < k) heap.add(val);
            else if (val > heap.peek()) { heap.poll(); heap.add(val); }
            return heap.peek();                                // the smallest of the top k is the k-th largest
        }
    }

    public static void main(String[] args) {
        KthLargest kth = new KthLargest(3, new int[]{4, 5, 8, 2});
        StringJoiner sj = new StringJoiner(" ");
        for (int v : new int[]{3, 5, 10, 9, 4}) sj.add(String.valueOf(kth.add(v)));
        System.out.println(sj);
    }
}
''', ts=TS_HEAP + r'''
class KthLargest {
  k: number;
  heap = new Heap<number>((x, y) => x < y);   // a min heap of the k biggest values so far
  constructor(k: number, nums: number[]) {
    this.k = k;
    for (const x of nums) this.add(x);
  }
  add(val: number): number {
    if (this.heap.size < this.k) this.heap.push(val);
    else if (val > this.heap.peek()) { this.heap.pop(); this.heap.push(val); }
    return this.heap.peek();                 // the smallest of the top k is the k-th largest
  }
}

const kth = new KthLargest(3, [4, 5, 8, 2]);
console.log([3, 5, 10, 9, 4].map(v => kth.add(v)).join(" "));
''')

t.code('p_topfreq', py=r'''
import heapq
from collections import Counter


def top_k_frequent(nums, k):
    heap = []                                 # min heap of (count, value), never bigger than k
    for val, cnt in Counter(nums).items():
        heapq.heappush(heap, (cnt, val))
        if len(heap) > k:
            heapq.heappop(heap)               # drop the least frequent
    return [val for cnt, val in heap]


for nums, k in (([1, 1, 1, 2, 2, 3], 2), ([1], 1), ([4, 1, -1, 2, -1, 2, 3], 2)):
    print(" ".join(map(str, sorted(top_k_frequent(nums, k)))))
''', js=JS_HEAP + r'''
function topKFrequent(nums, k) {
  const count = new Map();
  for (const x of nums) count.set(x, (count.get(x) || 0) + 1);
  // min heap of [count, value], never bigger than k
  const heap = new Heap((p, q) => p[0] < q[0] || (p[0] === q[0] && p[1] < q[1]));
  for (const [val, cnt] of count) {
    heap.push([cnt, val]);
    if (heap.size > k) heap.pop();            // drop the least frequent
  }
  return heap.a.map(e => e[1]);
}

for (const [nums, k] of [[[1, 1, 1, 2, 2, 3], 2], [[1], 1], [[4, 1, -1, 2, -1, 2, 3], 2]]) {
  console.log(topKFrequent(nums, k).sort((x, y) => x - y).join(" "));
}
''', java=r'''
import java.util.*;

public class TopKFrequent {
    static List<Integer> topKFrequent(int[] nums, int k) {
        Map<Integer, Integer> count = new HashMap<>();
        for (int x : nums) count.merge(x, 1, Integer::sum);
        // min heap of {count, value}, never bigger than k
        PriorityQueue<int[]> heap = new PriorityQueue<>((p, q) -> p[0] != q[0] ? p[0] - q[0] : Integer.compare(p[1], q[1]));
        for (Map.Entry<Integer, Integer> e : count.entrySet()) {
            heap.add(new int[]{e.getValue(), e.getKey()});
            if (heap.size() > k) heap.poll();            // drop the least frequent
        }
        List<Integer> out = new ArrayList<>();
        for (int[] e : heap) out.add(e[1]);
        return out;
    }

    public static void main(String[] args) {
        int[][] tests = {{1, 1, 1, 2, 2, 3}, {1}, {4, 1, -1, 2, -1, 2, 3}};
        int[] ks = {2, 1, 2};
        for (int i = 0; i < tests.length; i++) {
            List<Integer> r = topKFrequent(tests[i], ks[i]);
            Collections.sort(r);
            StringJoiner sj = new StringJoiner(" ");
            for (int x : r) sj.add(String.valueOf(x));
            System.out.println(sj);
        }
    }
}
''', ts=TS_HEAP + r'''
function topKFrequent(nums: number[], k: number): number[] {
  const count = new Map<number, number>();
  for (const x of nums) count.set(x, (count.get(x) || 0) + 1);
  // min heap of [count, value], never bigger than k
  const heap = new Heap<[number, number]>((p, q) => p[0] < q[0] || (p[0] === q[0] && p[1] < q[1]));
  for (const [val, cnt] of count) {
    heap.push([cnt, val]);
    if (heap.size > k) heap.pop();            // drop the least frequent
  }
  return heap.a.map(e => e[1]);
}

const tests: Array<[number[], number]> = [[[1, 1, 1, 2, 2, 3], 2], [[1], 1], [[4, 1, -1, 2, -1, 2, 3], 2]];
for (const [nums, k] of tests) console.log(topKFrequent(nums, k).sort((x, y) => x - y).join(" "));
''')

t.code('p_closest', py=r'''
import heapq


def k_closest(points, k):
    heap = []                                 # max heap by distance (negated), at most k points
    for x, y in points:
        heapq.heappush(heap, (-(x * x + y * y), x, y))
        if len(heap) > k:
            heapq.heappop(heap)               # throw out the farthest of the k + 1
    return sorted([(x, y) for d, x, y in heap], key=lambda p: (p[0] ** 2 + p[1] ** 2, p))


for pts, k in (([(1, 3), (-2, 2)], 1), ([(3, 3), (5, -1), (-2, 4)], 2), ([(0, 1), (1, 0), (2, 2), (-1, 0)], 3)):
    print(" ".join(f"[{x},{y}]" for x, y in k_closest(pts, k)))
''', js=JS_HEAP + r'''
const d2 = p => p[0] * p[0] + p[1] * p[1];

function kClosest(points, k) {
  // max heap by distance, ties by x then y, at most k points
  const far = (p, q) => d2(p) > d2(q) || (d2(p) === d2(q) && (p[0] > q[0] || (p[0] === q[0] && p[1] > q[1])));
  const heap = new Heap(far);
  for (const p of points) {
    heap.push(p);
    if (heap.size > k) heap.pop();            // throw out the farthest of the k + 1
  }
  return [...heap.a].sort((p, q) => d2(p) - d2(q) || p[0] - q[0] || p[1] - q[1]);
}

for (const [pts, k] of [[[[1, 3], [-2, 2]], 1], [[[3, 3], [5, -1], [-2, 4]], 2], [[[0, 1], [1, 0], [2, 2], [-1, 0]], 3]]) {
  console.log(kClosest(pts, k).map(p => `[${p[0]},${p[1]}]`).join(" "));
}
''', java=r'''
import java.util.*;

public class KClosest {
    static int d2(int[] p) { return p[0] * p[0] + p[1] * p[1]; }

    static int cmp(int[] p, int[] q) {                  // by distance, then x, then y
        if (d2(p) != d2(q)) return Integer.compare(d2(p), d2(q));
        if (p[0] != q[0]) return Integer.compare(p[0], q[0]);
        return Integer.compare(p[1], q[1]);
    }

    static List<int[]> kClosest(int[][] points, int k) {
        PriorityQueue<int[]> heap = new PriorityQueue<>((p, q) -> cmp(q, p));   // max heap, at most k points
        for (int[] p : points) {
            heap.add(p);
            if (heap.size() > k) heap.poll();            // throw out the farthest of the k + 1
        }
        List<int[]> out = new ArrayList<>(heap);
        out.sort(KClosest::cmp);
        return out;
    }

    public static void main(String[] args) {
        int[][][] tests = {{{1, 3}, {-2, 2}}, {{3, 3}, {5, -1}, {-2, 4}}, {{0, 1}, {1, 0}, {2, 2}, {-1, 0}}};
        int[] ks = {1, 2, 3};
        for (int i = 0; i < tests.length; i++) {
            StringJoiner sj = new StringJoiner(" ");
            for (int[] p : kClosest(tests[i], ks[i])) sj.add("[" + p[0] + "," + p[1] + "]");
            System.out.println(sj);
        }
    }
}
''', ts=TS_HEAP + r'''
type P = [number, number];
const d2 = (p: P): number => p[0] * p[0] + p[1] * p[1];

function kClosest(points: P[], k: number): P[] {
  // max heap by distance, ties by x then y, at most k points
  const far = (p: P, q: P): boolean => d2(p) > d2(q) || (d2(p) === d2(q) && (p[0] > q[0] || (p[0] === q[0] && p[1] > q[1])));
  const heap = new Heap<P>(far);
  for (const p of points) {
    heap.push(p);
    if (heap.size > k) heap.pop();            // throw out the farthest of the k + 1
  }
  return [...heap.a].sort((p, q) => d2(p) - d2(q) || p[0] - q[0] || p[1] - q[1]);
}

const tests: Array<[P[], number]> = [[[[1, 3], [-2, 2]], 1], [[[3, 3], [5, -1], [-2, 4]], 2], [[[0, 1], [1, 0], [2, 2], [-1, 0]], 3]];
for (const [pts, k] of tests) console.log(kClosest(pts, k).map(p => `[${p[0]},${p[1]}]`).join(" "));
''')

t.code('p_mergek', py=r'''
import heapq


class ListNode:
    def __init__(self, val, next=None):
        self.val, self.next = val, next


def merge_k_lists(lists):
    heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
    heapq.heapify(heap)                       # the list number breaks ties, so nodes are never compared
    dummy = tail = ListNode(0)
    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
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


for case in ([[1, 4, 5], [1, 3, 4], [2, 6]], [], [[]]):
    print(show(merge_k_lists([build(v) for v in case])))
''', js=JS_HEAP + r'''
class ListNode {
  constructor(val, next = null) {
    this.val = val;
    this.next = next;
  }
}

function mergeKLists(lists) {
  const heap = new Heap((p, q) => p[0] < q[0] || (p[0] === q[0] && p[1] < q[1]));   // [value, list number, node]
  lists.forEach((node, i) => { if (node) heap.push([node.val, i, node]); });
  const dummy = new ListNode(0);
  let tail = dummy;
  while (heap.size) {
    const [, i, node] = heap.pop();
    tail.next = node;
    tail = node;
    if (node.next) heap.push([node.next.val, i, node.next]);
  }
  return dummy.next;
}

const build = vals => vals.reduceRight((head, v) => new ListNode(v, head), null);
const show = node => { const out = []; for (; node; node = node.next) out.push(node.val); return out.join(" ") || "(empty)"; };

for (const c of [[[1, 4, 5], [1, 3, 4], [2, 6]], [], [[]]]) console.log(show(mergeKLists(c.map(build))));
''', java=r'''
import java.util.*;

public class MergeKLists {
    static class ListNode {
        int val;
        ListNode next;
        ListNode(int v, ListNode n) { val = v; next = n; }
    }

    static ListNode mergeKLists(ListNode[] lists) {
        PriorityQueue<ListNode> heap = new PriorityQueue<>((p, q) -> Integer.compare(p.val, q.val));
        for (ListNode n : lists) if (n != null) heap.add(n);
        ListNode dummy = new ListNode(0, null), tail = dummy;
        while (!heap.isEmpty()) {
            ListNode node = heap.poll();                 // the smallest head among all lists
            tail.next = node;
            tail = node;
            if (node.next != null) heap.add(node.next);
        }
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
        int[][][] cases = {{{1, 4, 5}, {1, 3, 4}, {2, 6}}, {}, {{}}};
        for (int[][] c : cases) {
            ListNode[] lists = new ListNode[c.length];
            for (int i = 0; i < c.length; i++) lists[i] = build(c[i]);
            System.out.println(show(mergeKLists(lists)));
        }
    }
}
''', ts=TS_HEAP + r'''
class ListNode {
  val: number;
  next: ListNode | null;
  constructor(val: number, next: ListNode | null = null) {
    this.val = val;
    this.next = next;
  }
}

type Item = [number, number, ListNode];   // value, list number, node

function mergeKLists(lists: Array<ListNode | null>): ListNode | null {
  const heap = new Heap<Item>((p, q) => p[0] < q[0] || (p[0] === q[0] && p[1] < q[1]));
  lists.forEach((node, i) => { if (node) heap.push([node.val, i, node]); });
  const dummy = new ListNode(0);
  let tail = dummy;
  while (heap.size) {
    const [, i, node] = heap.pop();
    tail.next = node;
    tail = node;
    if (node.next) heap.push([node.next.val, i, node.next]);
  }
  return dummy.next;
}

const build = (vals: number[]): ListNode | null => vals.reduceRight<ListNode | null>((head, v) => new ListNode(v, head), null);
const show = (node: ListNode | null): string => { const out: number[] = []; for (; node; node = node.next) out.push(node.val); return out.join(" ") || "(empty)"; };

const cases: number[][][] = [[[1, 4, 5], [1, 3, 4], [2, 6]], [], [[]]];
for (const c of cases) console.log(show(mergeKLists(c.map(build))));
''')

t.code('p_cpu', py=r'''
import heapq


def get_order(tasks):
    order = sorted(range(len(tasks)), key=lambda i: (tasks[i][0], i))   # by arrival time
    ready, result, time, k = [], [], 0, 0
    while len(result) < len(tasks):
        if not ready and time < tasks[order[k]][0]:
            time = tasks[order[k]][0]         # the CPU is idle: jump to the next arrival
        while k < len(order) and tasks[order[k]][0] <= time:
            i = order[k]
            heapq.heappush(ready, (tasks[i][1], i))   # shortest job first, then smallest index
            k += 1
        length, i = heapq.heappop(ready)
        time += length
        result.append(i)
    return result


print(" ".join(map(str, get_order([[1, 2], [2, 4], [3, 2], [4, 1]]))))
print(" ".join(map(str, get_order([[7, 10], [7, 12], [7, 5], [7, 4], [7, 2]]))))
''', js=JS_HEAP + r'''
function getOrder(tasks) {
  const order = tasks.map((_, i) => i).sort((a, b) => tasks[a][0] - tasks[b][0] || a - b);   // by arrival time
  const ready = new Heap((p, q) => p[0] < q[0] || (p[0] === q[0] && p[1] < q[1]));        // [length, index]
  const result = [];
  let time = 0, k = 0;
  while (result.length < tasks.length) {
    if (!ready.size && time < tasks[order[k]][0]) time = tasks[order[k]][0];   // idle: jump ahead
    while (k < order.length && tasks[order[k]][0] <= time) {
      const i = order[k++];
      ready.push([tasks[i][1], i]);           // shortest job first, then smallest index
    }
    const [len, i] = ready.pop();
    time += len;
    result.push(i);
  }
  return result;
}

console.log(getOrder([[1, 2], [2, 4], [3, 2], [4, 1]]).join(" "));
console.log(getOrder([[7, 10], [7, 12], [7, 5], [7, 4], [7, 2]]).join(" "));
''', java=r'''
import java.util.*;

public class SingleThreadedCPU {
    static int[] getOrder(int[][] tasks) {
        Integer[] order = new Integer[tasks.length];
        for (int i = 0; i < tasks.length; i++) order[i] = i;
        Arrays.sort(order, (a, b) -> tasks[a][0] != tasks[b][0] ? tasks[a][0] - tasks[b][0] : a - b);   // by arrival
        PriorityQueue<int[]> ready = new PriorityQueue<>((p, q) -> p[0] != q[0] ? p[0] - q[0] : p[1] - q[1]);   // {length, index}
        int[] result = new int[tasks.length];
        long time = 0;
        int k = 0, done = 0;
        while (done < tasks.length) {
            if (ready.isEmpty() && time < tasks[order[k]][0]) time = tasks[order[k]][0];   // idle: jump ahead
            while (k < order.length && tasks[order[k]][0] <= time) {
                int i = order[k++];
                ready.add(new int[]{tasks[i][1], i});    // shortest job first, then smallest index
            }
            int[] job = ready.poll();
            time += job[0];
            result[done++] = job[1];
        }
        return result;
    }

    static String show(int[] a) {
        StringJoiner sj = new StringJoiner(" ");
        for (int x : a) sj.add(String.valueOf(x));
        return sj.toString();
    }

    public static void main(String[] args) {
        System.out.println(show(getOrder(new int[][]{{1, 2}, {2, 4}, {3, 2}, {4, 1}})));
        System.out.println(show(getOrder(new int[][]{{7, 10}, {7, 12}, {7, 5}, {7, 4}, {7, 2}})));
    }
}
''', ts=TS_HEAP + r'''
function getOrder(tasks: number[][]): number[] {
  const order = tasks.map((_, i) => i).sort((a, b) => tasks[a][0] - tasks[b][0] || a - b);   // by arrival time
  const ready = new Heap<[number, number]>((p, q) => p[0] < q[0] || (p[0] === q[0] && p[1] < q[1]));   // [length, index]
  const result: number[] = [];
  let time = 0, k = 0;
  while (result.length < tasks.length) {
    if (!ready.size && time < tasks[order[k]][0]) time = tasks[order[k]][0];   // idle: jump ahead
    while (k < order.length && tasks[order[k]][0] <= time) {
      const i = order[k++];
      ready.push([tasks[i][1], i]);           // shortest job first, then smallest index
    }
    const [len, i] = ready.pop();
    time += len;
    result.push(i);
  }
  return result;
}

console.log(getOrder([[1, 2], [2, 4], [3, 2], [4, 1]]).join(" "));
console.log(getOrder([[7, 10], [7, 12], [7, 5], [7, 4], [7, 2]]).join(" "));
''')

t.code('p_medianfinder', py=r'''
import heapq


class MedianFinder:
    def __init__(self):
        self.low, self.high = [], []          # max heap (negated) for the small half, min heap for the big half

    def add_num(self, num):
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))   # the biggest of low moves to high
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))   # rebalance: low keeps the extra one

    def find_median(self):
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2


mf = MedianFinder()
out = []
for x in [1, 2, 3, 10, -4, 7]:
    mf.add_num(x)
    out.append(f"{mf.find_median():.1f}")
print(" ".join(out))
''', js=JS_HEAP + r'''
class MedianFinder {
  constructor() {
    this.low = new Heap((x, y) => x > y);    // max heap for the small half
    this.high = new Heap((x, y) => x < y);   // min heap for the big half
  }
  addNum(num) {
    this.low.push(num);
    this.high.push(this.low.pop());          // the biggest of low moves to high
    if (this.high.size > this.low.size) this.low.push(this.high.pop());   // low keeps the extra one
  }
  findMedian() {
    return this.low.size > this.high.size ? this.low.peek() : (this.low.peek() + this.high.peek()) / 2;
  }
}

const mf = new MedianFinder();
const out = [];
for (const x of [1, 2, 3, 10, -4, 7]) {
  mf.addNum(x);
  out.push(mf.findMedian().toFixed(1));
}
console.log(out.join(" "));
''', java=r'''
import java.util.*;

public class MedianFinderDemo {
    static class MedianFinder {
        PriorityQueue<Integer> low = new PriorityQueue<>(Collections.reverseOrder());   // max heap, small half
        PriorityQueue<Integer> high = new PriorityQueue<>();                            // min heap, big half

        void addNum(int num) {
            low.add(num);
            high.add(low.poll());                        // the biggest of low moves to high
            if (high.size() > low.size()) low.add(high.poll());   // low keeps the extra one
        }

        double findMedian() {
            return low.size() > high.size() ? low.peek() : (low.peek() + high.peek()) / 2.0;
        }
    }

    public static void main(String[] args) {
        MedianFinder mf = new MedianFinder();
        StringJoiner sj = new StringJoiner(" ");
        for (int x : new int[]{1, 2, 3, 10, -4, 7}) {
            mf.addNum(x);
            sj.add(String.format("%.1f", mf.findMedian()));
        }
        System.out.println(sj);
    }
}
''', ts=TS_HEAP + r'''
class MedianFinder {
  low = new Heap<number>((x, y) => x > y);    // max heap for the small half
  high = new Heap<number>((x, y) => x < y);   // min heap for the big half
  addNum(num: number): void {
    this.low.push(num);
    this.high.push(this.low.pop());          // the biggest of low moves to high
    if (this.high.size > this.low.size) this.low.push(this.high.pop());   // low keeps the extra one
  }
  findMedian(): number {
    return this.low.size > this.high.size ? this.low.peek() : (this.low.peek() + this.high.peek()) / 2;
  }
}

const mf = new MedianFinder();
const out: string[] = [];
for (const x of [1, 2, 3, 10, -4, 7]) {
  mf.addNum(x);
  out.push(mf.findMedian().toFixed(1));
}
console.log(out.join(" "));
''')

t.code('p_rooms3', py=r'''
import heapq


def most_booked(n, meetings):
    free = list(range(n))                     # free rooms, smallest number first
    busy = []                                 # (time the room is free again, room)
    count = [0] * n
    for start, end in sorted(meetings):
        while busy and busy[0][0] <= start:   # rooms that finished by now become free
            heapq.heappush(free, heapq.heappop(busy)[1])
        if free:
            room = heapq.heappop(free)
            heapq.heappush(busy, (end, room))
        else:                                 # all busy: wait for the room that frees up first
            t_free, room = heapq.heappop(busy)
            heapq.heappush(busy, (t_free + end - start, room))   # the meeting keeps its length
        count[room] += 1
    return count.index(max(count))            # the lowest numbered room among the most booked


print(most_booked(2, [[0, 10], [1, 5], [2, 7], [3, 4]]))
print(most_booked(3, [[1, 20], [2, 10], [3, 5], [4, 9], [6, 8]]))
''', js=JS_HEAP + r'''
function mostBooked(n, meetings) {
  const free = new Heap((x, y) => x < y);    // free rooms, smallest number first
  for (let r = 0; r < n; r++) free.push(r);
  const busy = new Heap((p, q) => p[0] < q[0] || (p[0] === q[0] && p[1] < q[1]));   // [free again at, room]
  const count = Array(n).fill(0);
  for (const [start, end] of [...meetings].sort((p, q) => p[0] - q[0])) {
    while (busy.size && busy.peek()[0] <= start) free.push(busy.pop()[1]);   // finished rooms become free
    let room;
    if (free.size) {
      room = free.pop();
      busy.push([end, room]);
    } else {                                  // all busy: wait for the room that frees up first
      const [tFree, r] = busy.pop();
      room = r;
      busy.push([tFree + end - start, room]); // the meeting keeps its length
    }
    count[room]++;
  }
  return count.indexOf(Math.max(...count));  // the lowest numbered room among the most booked
}

console.log(mostBooked(2, [[0, 10], [1, 5], [2, 7], [3, 4]]));
console.log(mostBooked(3, [[1, 20], [2, 10], [3, 5], [4, 9], [6, 8]]));
''', java=r'''
import java.util.*;

public class MeetingRoomsIII {
    static int mostBooked(int n, int[][] meetings) {
        int[][] m = meetings.clone();
        Arrays.sort(m, (p, q) -> Integer.compare(p[0], q[0]));
        PriorityQueue<Integer> free = new PriorityQueue<>();               // free rooms, smallest number first
        for (int r = 0; r < n; r++) free.add(r);
        PriorityQueue<long[]> busy = new PriorityQueue<>((p, q) -> p[0] != q[0] ? Long.compare(p[0], q[0]) : Long.compare(p[1], q[1]));   // {free again at, room}
        int[] count = new int[n];
        for (int[] mt : m) {
            while (!busy.isEmpty() && busy.peek()[0] <= mt[0]) free.add((int) busy.poll()[1]);   // finished rooms become free
            int room;
            if (!free.isEmpty()) {
                room = free.poll();
                busy.add(new long[]{mt[1], room});
            } else {                                                       // all busy: wait for the first free room
                long[] b = busy.poll();
                room = (int) b[1];
                busy.add(new long[]{b[0] + mt[1] - mt[0], room});          // the meeting keeps its length
            }
            count[room]++;
        }
        int best = 0;
        for (int r = 1; r < n; r++) if (count[r] > count[best]) best = r;  // the lowest numbered room among the most booked
        return best;
    }

    public static void main(String[] args) {
        System.out.println(mostBooked(2, new int[][]{{0, 10}, {1, 5}, {2, 7}, {3, 4}}));
        System.out.println(mostBooked(3, new int[][]{{1, 20}, {2, 10}, {3, 5}, {4, 9}, {6, 8}}));
    }
}
''', ts=TS_HEAP + r'''
function mostBooked(n: number, meetings: number[][]): number {
  const free = new Heap<number>((x, y) => x < y);   // free rooms, smallest number first
  for (let r = 0; r < n; r++) free.push(r);
  const busy = new Heap<[number, number]>((p, q) => p[0] < q[0] || (p[0] === q[0] && p[1] < q[1]));   // [free again at, room]
  const count: number[] = Array(n).fill(0);
  for (const [start, end] of [...meetings].sort((p, q) => p[0] - q[0])) {
    while (busy.size && busy.peek()[0] <= start) free.push(busy.pop()[1]);   // finished rooms become free
    let room: number;
    if (free.size) {
      room = free.pop();
      busy.push([end, room]);
    } else {                                  // all busy: wait for the room that frees up first
      const [tFree, r] = busy.pop();
      room = r;
      busy.push([tFree + end - start, room]); // the meeting keeps its length
    }
    count[room]++;
  }
  return count.indexOf(Math.max(...count));  // the lowest numbered room among the most booked
}

console.log(mostBooked(2, [[0, 10], [1, 5], [2, 7], [3, 4]]));
console.log(mostBooked(3, [[1, 20], [2, 10], [3, 5], [4, 9], [6, 8]]));
''')

t.leet(1046, 'e', 'p_stones',
       statement='<p>Each turn, smash the two heaviest stones together. Equal stones both vanish. Otherwise the heavier one shrinks by the weight of the lighter one. Return the weight of the last stone, or 0.</p>',
       example='[2,7,4,1,8,1]  →  1\n[1]            →  1\n[3,3]          →  0',
       hint='You always need the two biggest values quickly.',
       approach='<p>Keep the stones in a max heap. Pop twice, push the difference back if it is not zero, and repeat until at most one stone is left. Python\'s <code>heapq</code> is a min heap, so it stores negative weights. Java uses <code>PriorityQueue</code> with <code>reverseOrder()</code>.</p>',
       time='O(n log n)', space='O(n)')
t.leet(703, 'e', 'p_kthstream',
       statement='<p>Design a class that keeps receiving numbers and, after each one, returns the k-th largest number seen so far.</p>',
       example='k = 3, start [4,5,8,2]\nadd 3, 5, 10, 9, 4  →  4 5 5 8 8',
       hint='Only the k biggest numbers matter. Which of them is the answer?',
       approach='<p>Keep a min heap of at most k values. A new value smaller than the heap\'s top cannot be in the top k, so ignore it. Otherwise replace the top. The top of the heap is always the smallest of the k largest, which is exactly the k-th largest.</p>',
       time='O(log k) per add', space='O(k)')
t.leet(347, 'm', 'p_topfreq',
       statement='<p>Return the k values that appear most often.</p>',
       example='[1,1,1,2,2,3], k = 2         →  1 2\n[4,1,-1,2,-1,2,3], k = 2     →  -1 2',
       hint='Count first, then keep the k biggest counts.',
       approach='<p>Count every value with a hash map. Push (count, value) pairs into a min heap and pop whenever it grows past k, so the least frequent drops out. That is O(n log k). The Python chapter solves it with buckets by count in O(n).</p>',
       time='O(n log k)', space='O(n)')
t.leet(973, 'm', 'p_closest',
       statement='<p>Return the k points closest to the origin (0, 0).</p>',
       example='[[1,3],[-2,2]], k = 1          →  [-2,2]\n[[3,3],[5,-1],[-2,4]], k = 2    →  [3,3] [-2,4]',
       hint='Keep the k closest so far, and throw out the farthest of them.',
       approach='<p>Use a max heap by squared distance, capped at k points. When it holds k + 1, pop the farthest. Squared distance keeps whole numbers and gives the same order as real distance. The answers here are sorted so every language prints the same line.</p>',
       time='O(n log k)', space='O(k)')
t.leet(23, 'h', 'p_mergek',
       statement='<p>Merge k sorted linked lists into one sorted list.</p>',
       example='[1,4,5], [1,3,4], [2,6]  →  1 1 2 3 4 4 5 6\n[]                       →  (empty)',
       hint='The next node is always the smallest of the k current heads.',
       approach='<p>Put the head of every list in a min heap. Pop the smallest, link it to the result, and push its next node. Each of the N nodes goes in and out of a heap of size k once. Python adds the list number to each tuple, so two equal values never compare the nodes themselves.</p>',
       time='O(N log k)', space='O(k)')
t.leet(1834, 'h', 'p_cpu',
       statement='<p>Tasks arrive at given times with given lengths. A single CPU always picks the shortest ready task, breaking ties by the smaller index. Return the order the tasks run in.</p>',
       example='[[1,2],[2,4],[3,2],[4,1]]          →  0 2 3 1\n[[7,10],[7,12],[7,5],[7,4],[7,2]]  →  4 3 2 0 1',
       hint='Sort by arrival. A heap holds the tasks that have arrived and are waiting.',
       approach='<p>Sort task indexes by arrival time. Keep a clock. Push every task that has arrived by now into a min heap of (length, index). Pop one, run it, and move the clock forward by its length. If the heap is empty, jump the clock to the next arrival.</p>',
       time='O(n log n)', space='O(n)')
t.leet(295, 'x', 'p_medianfinder',
       statement='<p>Design a class that receives numbers one by one and can return the median of all numbers so far at any time.</p>',
       example='add 1, 2      →  median 1.5\nadd 3         →  median 2.0',
       hint='Split the numbers into a smaller half and a bigger half.',
       approach='<p>Keep the smaller half in a max heap and the bigger half in a min heap, with the max heap allowed one extra item. Each new number goes into the max heap, its biggest moves to the min heap, and the sizes are rebalanced. The median is the max heap\'s top, or the average of both tops.</p>',
       time='O(log n) per add, O(1) per median', space='O(n)')
t.leet(2402, 'x', 'p_rooms3',
       statement='<p>n rooms are numbered from 0. Each meeting takes the free room with the smallest number. If none is free, it waits for the room that frees up first and keeps its length. Return the room that held the most meetings.</p>',
       example='n = 2, [[0,10],[1,5],[2,7],[3,4]]          →  0\nn = 3, [[1,20],[2,10],[3,5],[4,9],[6,8]]   →  1',
       hint='Two heaps: free rooms by number, busy rooms by the time they free up.',
       approach='<p>Sort meetings by start. Before each meeting, move every room whose end time has passed back to the free heap. Take the smallest free room, or else pop the busy room that frees first and push it back with the delayed end time. Count meetings per room. Java uses <code>long</code> for times because delays can add up.</p>',
       time='O(m log n)', space='O(n)')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='sift', emoji='⛰️', title='Sift up and sift down, step by step', html='''
<p>The Trees chapter showed that a min heap keeps the smallest value at the root and lives in a plain array. Two moves keep it in order. <b>Sift up</b>: a new value joins at the end and swaps with its parent while the parent is bigger. <b>Sift down</b>: after the root is removed, the last value jumps to the top and swaps with its smaller child until both children are bigger.</p>
<div class="viz" data-viz="pk" data-pk="sift"></div>
<div class="c3" data-k="sift" data-label="A min heap written from scratch"></div>
<span class="eq">left = 2i + 1 &nbsp; right = 2i + 2 &nbsp; parent = ⌊(i − 1) / 2⌋</span>
<div class="rule">A heap of n values has about log₂ n levels, so one push or one pop costs at most O(log n) swaps.</div>
'''),
    dict(id='heapify', emoji='🏗️', title='Building a heap in O(n)', html='''
<p>Pushing n values one by one costs O(n log n). There is a faster way. Put all values in the array as they are. Every leaf is already a tiny heap. Then sift down each parent, <b>starting from the last parent and moving to the root</b>. Most nodes sit near the bottom and move only a step or two, so the total is O(n).</p>
<div class="viz" data-viz="pk" data-pk="heapify"></div>
<div class="c3" data-k="heapify" data-label="Bottom up building against pushing one by one"></div>
<div class="exam">For 1023 values in the worst order, bottom up needs 1013 swaps while pushing one by one needs 8194. Python's <code>heapq.heapify</code> uses the bottom up method.</div>
'''),
    dict(id='heap-sort', emoji='📶', title='Heap sort', html='''
<p>Build a <b>max heap</b> in O(n). The biggest value is now at index 0. Swap it with the last value, treat the array as one shorter, and sift the new root down. The biggest values collect at the end, already in order. Repeat n − 1 times.</p>
<div class="viz" data-viz="pk" data-pk="heapsort"></div>
<div class="c3" data-k="heapsort" data-label="Heap sort in place"></div>
<div class="tw"><table class="jt"><tr><th></th><th>Heap sort</th><th>Merge sort</th><th>Quick sort</th></tr>
<tr><td>Worst case</td><td class="yes">O(n log n)</td><td class="yes">O(n log n)</td><td>O(n²)</td></tr>
<tr><td>Extra memory</td><td class="yes">O(1)</td><td>O(n)</td><td>O(log n)</td></tr>
<tr><td>Stable</td><td>no</td><td class="yes">yes</td><td>no</td></tr></table></div>
'''),
    dict(id='top-k', emoji='🏅', title='Top k with a small heap', html='''
<p>To keep the 3 highest scores from a stream of millions, you do not need to store them all. Keep a <b>min heap of size k</b>. Its root is the smallest of your top k. A new score that is not bigger than the root cannot make the list, so it is ignored at once. A bigger one replaces the root.</p>
<div class="viz" data-viz="pk" data-pk="topk"></div>
<div class="c3" data-k="topk" data-label="The top 3 of a stream"></div>
<div class="rule">For the k largest use a min heap. For the k smallest use a max heap. The root guards the door, and each check costs O(log k).</div>
'''),
    dict(id='k-way-merge', emoji='🔀', title='Merging k sorted lists', html='''
<p>Several sorted lists need to become one sorted list. The next value is always one of the current heads. Put every head in a min heap, pop the smallest, and push the next value from the same list. With N values in k lists, that is O(N log k).</p>
<div class="viz" data-viz="pk" data-pk="kmerge"></div>
<div class="c3" data-k="kmerge" data-label="K way merge with a heap of heads"></div>
<div class="exam">Databases and search engines merge sorted runs from disk this way when the data does not fit in memory. Python ships it as <code>heapq.merge</code>.</div>
'''),
    dict(id='running-median', emoji='⚖️', title='The running median with two heaps', html='''
<p>Numbers keep arriving and you want the median after each one. Split them into two halves. The <b>smaller half</b> lives in a max heap, so its biggest is on top. The <b>bigger half</b> lives in a min heap, so its smallest is on top. Keep the halves the same size, or the smaller half one bigger. The median sits right at the two tops.</p>
<div class="viz" data-viz="pk" data-pk="median"></div>
<div class="c3" data-k="median" data-label="Running median with two heaps"></div>
'''),
    dict(id='scheduling', emoji='🚪', title='Scheduling: how many rooms?', html='''
<p>Meetings have start and end times. How many rooms are needed? Sort the meetings by start. Keep a min heap of the times when each busy room becomes free. For each meeting, if the earliest free time is not after its start, reuse that room. Otherwise open a new one. The heap size at the end is the answer.</p>
<div class="viz" data-viz="pk" data-pk="rooms"></div>
<div class="c3" data-k="rooms" data-label="Minimum meeting rooms with a heap of end times"></div>
<div class="tip">Operating systems, printers and game engines all use priority queues like this to decide what runs next. Dijkstra's shortest paths, in the Advanced graphs chapter, uses one too.</div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem is solved in the Practice section in Python, JavaScript, Java and TypeScript, with line by line replay. JavaScript and TypeScript have no heap built in, so those solutions carry a small heap class of about 30 lines.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>The heap idea</th></tr>
<tr><td><a href="#lc1046">1046. Last Stone Weight</a></td><td>Easy</td><td>a max heap of stones</td></tr>
<tr><td><a href="#lc703">703. Kth Largest Element in a Stream</a></td><td>Easy</td><td>a min heap of size k</td></tr>
<tr><td><a href="#lc347">347. Top K Frequent Elements</a></td><td>Medium</td><td>count, then keep the k biggest counts</td></tr>
<tr><td><a href="#lc973">973. K Closest Points to Origin</a></td><td>Medium</td><td>a max heap throws out the farthest</td></tr>
<tr><td><a href="#lc23">23. Merge k Sorted Lists</a></td><td>Hard</td><td>a heap of list heads</td></tr>
<tr><td><a href="#lc1834">1834. Single-Threaded CPU</a></td><td>Hard</td><td>a heap of ready tasks</td></tr>
<tr><td><a href="#lc295">295. Find Median from Data Stream</a></td><td>Expert</td><td>two heaps, two halves</td></tr>
<tr><td><a href="#lc2402">2402. Meeting Rooms III</a></td><td>Expert</td><td>free rooms and busy rooms</td></tr></table></div>
'''),
]

VIZ_JS = r'''
(() => {
  const D = PK.defs;
  const LIMIT = 170;
  const okList = (s, lo, hi) => { const a = PK.parseList(s); return a && a.length >= lo && a.length <= hi && a.every(x => Number.isInteger(x) && Math.abs(x) <= 99) ? a : null; };
  /* the heap drawn twice: as a tree and as the array it really is */
  const heapPic = (a, n, cls = {}, label = 'Heap as a tree') => {
    const kids = {};
    for (let i = 0; i < n; i++) kids['h' + i] = [2 * i + 1 < n ? 'h' + (2 * i + 1) : null, 2 * i + 2 < n ? 'h' + (2 * i + 2) : null];
    const depth = Math.max(1, Math.floor(Math.log2(Math.max(1, n))) + 1), W = 500, H = 64 * depth + 20;
    const L = n ? PK.treeLayout(kids, 'h0', id => a[Number(id.slice(1))], W, H) : { nodes: [], edges: [] };
    const ncls = {};
    Object.entries(cls).forEach(([i, c]) => { if (Number(i) < n) ncls['h' + i] = c; });
    const layers = [];
    if (n) layers.push({ t: 'graph', label, w: W, h: H, nodes: L.nodes, edges: L.edges, ncls });
    layers.push({ t: 'row', label: 'The same heap as an array', cells: a.slice(), cls: Object.fromEntries(a.map((_, i) => [i, cls[i] || (i >= n ? 'yes' : '')])) });
    return layers;
  };

  /* ---------- sift up and sift down ---------- */
  D.sift = el => PK.widget(el, {
    title: 'Push and pop on a min heap', sub: 'A new value climbs while its parent is bigger. After a pop, the last value drops from the root while a child is smaller.',
    inputs: [{ k: 'nums', label: 'Push these', type: 'text', val: '5, 3, 8, 1, 9, 2', w: 180 }, { k: 'pops', label: 'Then pop', type: 'num', val: 2, min: 0, max: 7, w: 70 }],
    random: () => ({ nums: Array.from({ length: 5 + Math.floor(Math.random() * 3) }, () => 1 + Math.floor(Math.random() * 30)).join(', '), pops: 2 }),
    check: v => { const a = okList(v.nums, 1, 7); return a && Number.isInteger(v.pops) && v.pops >= 0 && v.pops <= a.length ? '' : 'Push one to seven whole numbers, and pop at most that many.'; },
    frames: ({ nums, pops }) => {
      const vals = okList(nums, 1, 7), a = [], F = [], out = [];
      const pic = cls => heapPic(a, a.length, cls).concat(out.length ? [{ t: 'row', label: 'Popped in order', cells: out.slice(), cls: { [out.length - 1]: 'yes' } }] : []);
      for (const x of vals) {
        a.push(x);
        let i = a.length - 1;
        F.push({ mood: 'look', msg: `Push ${x}. It joins at the end, index ${i}.`, layers: pic({ [i]: 'look' }) });
        while (i > 0) {
          const p = Math.floor((i - 1) / 2);
          if (a[p] <= a[i]) { F.push({ mood: 'happy', msg: `Parent ${a[p]} ≤ ${a[i]}. ${a[i]} has settled at index ${i}.`, layers: pic({ [i]: 'yes', [p]: 'cur' }) }); break; }
          F.push({ mood: 'work', msg: `Parent ${a[p]} is bigger than ${a[i]}. Swap them: sift up.`, layers: pic({ [i]: 'mv', [p]: 'mv' }) });
          [a[i], a[p]] = [a[p], a[i]];
          i = p;
          if (i === 0) F.push({ mood: 'wow', fx: 'burst', msg: `${a[0]} reached the root. It is the new smallest value.`, layers: pic({ 0: 'yes' }) });
        }
      }
      for (let k = 0; k < pops; k++) {
        const top = a[0], last = a.pop();
        out.push(top);
        if (!a.length) { F.push({ mood: 'happy', msg: `Pop ${top}. The heap is empty now.`, layers: pic({}) }); break; }
        a[0] = last;
        F.push({ mood: 'look', msg: `Pop the root ${top}. The last value ${last} jumps to the root.`, layers: pic({ 0: 'look' }) });
        let i = 0;
        while (true) {
          const l = 2 * i + 1, r = l + 1;
          let s = i;
          if (l < a.length && a[l] < a[s]) s = l;
          if (r < a.length && a[r] < a[s]) s = r;
          if (s === i) { F.push({ mood: 'happy', msg: `No child is smaller than ${a[i]}. It settles at index ${i}.`, layers: pic({ [i]: 'yes' }) }); break; }
          F.push({ mood: 'work', msg: `Child ${a[s]} is the smaller child and smaller than ${a[i]}. Swap: sift down.`, layers: pic({ [i]: 'mv', [s]: 'mv' }) });
          [a[i], a[s]] = [a[s], a[i]];
          i = s;
        }
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `Every push and pop moved along one path from a leaf to the root, about log₂ n levels.${out.length ? ' Popped in order: ' + out.join(', ') + '.' : ''}`, layers: pic({ 0: 'yes' }) });
      return F;
    }
  });

  /* ---------- bottom up heapify ---------- */
  D.heapify = el => PK.widget(el, {
    title: 'Build a heap from the bottom', sub: 'Leaves are already heaps. Sift down each parent, from the last parent back to the root.',
    inputs: [{ k: 'nums', label: 'Numbers', type: 'text', val: '9, 8, 7, 6, 5, 4, 3, 2, 1', w: 210 }],
    random: () => ({ nums: Array.from({ length: 7 + Math.floor(Math.random() * 4) }, () => 1 + Math.floor(Math.random() * 40)).join(', ') }),
    check: v => okList(v.nums, 2, 10) ? '' : 'Give two to ten whole numbers.',
    frames: ({ nums }) => {
      const a = okList(nums, 2, 10), n = a.length, F = [];
      let swaps = 0;
      const last = Math.floor(n / 2) - 1;
      F.push({ mood: 'think', msg: `${n} values, not a heap yet. Indexes ${last + 1} to ${n - 1} are leaves, so start at the last parent, index ${last}.`, vars: { swaps }, layers: heapPic(a, n, {}) });
      for (let i = last; i >= 0; i--) {
        let j = i;
        F.push({ mood: 'look', msg: `Sift down index ${i} (value ${a[i]}).`, vars: { swaps }, layers: heapPic(a, n, { [i]: 'look' }) });
        while (true) {
          const l = 2 * j + 1, r = l + 1;
          let s = j;
          if (l < n && a[l] < a[s]) s = l;
          if (r < n && a[r] < a[s]) s = r;
          if (s === j) break;
          [a[j], a[s]] = [a[s], a[j]];
          swaps++;
          F.push({ mood: 'work', msg: `Swap ${a[s]} down with its smaller child ${a[j]}.`, vars: { swaps }, layers: heapPic(a, n, { [j]: 'mv', [s]: 'mv' }) });
          j = s;
        }
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `A valid min heap after only <b>${swaps}</b> swaps. Nodes near the bottom are many but move little, so the total is O(n).`, vars: { swaps }, layers: heapPic(a, n, { 0: 'yes' }) });
      return F;
    }
  });

  /* ---------- heap sort ---------- */
  D.heapsort = el => PK.widget(el, {
    title: 'Heap sort', sub: 'Build a max heap, then swap the root to the end, shrink the heap and sift down. Green values are in their final place.',
    inputs: [{ k: 'nums', label: 'Numbers', type: 'text', val: '7, 2, 9, 4, 1, 8, 3', w: 200 }],
    random: () => ({ nums: Array.from({ length: 6 + Math.floor(Math.random() * 3) }, () => 1 + Math.floor(Math.random() * 30)).join(', ') }),
    check: v => okList(v.nums, 2, 9) ? '' : 'Give two to nine whole numbers.',
    frames: ({ nums }) => {
      const a = okList(nums, 2, 9), n = a.length, F = [];
      const down = (i, size, quiet) => {
        while (true) {
          const l = 2 * i + 1, r = l + 1;
          let b = i;
          if (l < size && a[l] > a[b]) b = l;
          if (r < size && a[r] > a[b]) b = r;
          if (b === i) return;
          [a[i], a[b]] = [a[b], a[i]];
          if (!quiet && F.length < LIMIT) F.push({ mood: 'work', msg: `${a[b]} is smaller than child ${a[i]}, so they swap.`, layers: heapPic(a, size, { [i]: 'mv', [b]: 'mv' }, 'Max heap part') });
          i = b;
        }
      };
      for (let i = Math.floor(n / 2) - 1; i >= 0; i--) down(i, n, true);
      F.push({ mood: 'think', msg: `Step 1: build a max heap. The biggest value, ${a[0]}, is at the root.`, layers: heapPic(a, n, { 0: 'piv' }, 'Max heap part') });
      for (let end = n - 1; end > 0; end--) {
        [a[0], a[end]] = [a[end], a[0]];
        F.push({ mood: 'happy', msg: `Swap the root ${a[end]} to index ${end}. It is in its final place.`, layers: heapPic(a, end, { [end]: 'yes', 0: 'look' }, 'Max heap part') });
        down(0, end, false);
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `Sorted: ${a.join(' ')}. No extra array was needed, and the worst case is still O(n log n).`, layers: heapPic(a, 0, {}) });
      return F;
    }
  });

  /* ---------- top k of a stream ---------- */
  D.topk = el => PK.widget(el, {
    title: 'Guard the top k', sub: 'A min heap of size k holds the best so far. Its root is the doorkeeper: a newcomer must beat it to get in.',
    inputs: [{ k: 'nums', label: 'Stream', type: 'text', val: '5, 1, 9, 3, 7, 2, 8, 6', w: 190 }, { k: 'k', label: 'k', type: 'num', val: 3, min: 1, max: 5, w: 60 }],
    random: () => ({ nums: Array.from({ length: 8 }, () => 1 + Math.floor(Math.random() * 50)).join(', '), k: 3 }),
    check: v => { const a = okList(v.nums, 1, 10); return a && Number.isInteger(v.k) && v.k >= 1 && v.k <= 5 ? '' : 'Give up to ten numbers and a k from 1 to 5.'; },
    frames: ({ nums, k }) => {
      const s = okList(nums, 1, 10), h = [], F = [];
      const push = x => { h.push(x); let i = h.length - 1; while (i > 0 && h[(i - 1) >> 1] > h[i]) { const p = (i - 1) >> 1; [h[i], h[p]] = [h[p], h[i]]; i = p; } };
      const pop = () => { const top = h[0], last = h.pop(); if (h.length) { h[0] = last; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i; if (l < h.length && h[l] < h[m]) m = l; if (r < h.length && h[r] < h[m]) m = r; if (m === i) break; [h[i], h[m]] = [h[m], h[i]]; i = m; } } return top; };
      const pic = (j, c) => [{ t: 'row', label: 'Stream', cells: s, cls: Object.fromEntries(s.map((_, i) => [i, i < j ? 'done' : i === j ? c : ''])) },
                            { t: 'row', label: `Min heap (root first), size ≤ ${k}`, cells: h.length ? h.slice() : ['empty'], cls: h.length ? { 0: 'piv' } : { 0: 'ghost' } }];
      s.forEach((x, j) => {
        if (h.length < k) { push(x); F.push({ mood: 'happy', msg: `${x}: the heap has room, so it joins.`, layers: pic(j, 'yes') }); }
        else if (x > h[0]) { const out = pop(); push(x); F.push({ mood: 'wow', fx: 'burst', msg: `${x} beats the doorkeeper ${out}! ${out} leaves and ${x} joins.`, layers: pic(j, 'yes') }); }
        else F.push({ mood: 'sad', fx: 'shake', msg: `${x} is not bigger than the doorkeeper ${h[0]}. Not good enough, ignored.`, layers: pic(j, 'no') });
      });
      F.push({ mood: 'wow', fx: 'rain', msg: `Top ${k}: ${[...h].sort((p, q) => q - p).join(', ')}. Memory stayed at ${k} numbers however long the stream was.`, layers: pic(s.length, '') });
      return F;
    }
  });

  /* ---------- k way merge ---------- */
  D.kmerge = el => PK.widget(el, {
    title: 'Merge three sorted lists', sub: 'The heap holds one head from each list. Pop the smallest, then that list sends its next value.',
    inputs: [{ k: 'a', label: 'List A', type: 'text', val: '1, 4, 7', w: 110 }, { k: 'b', label: 'List B', type: 'text', val: '2, 5, 8', w: 110 }, { k: 'c', label: 'List C', type: 'text', val: '0, 3, 6, 9', w: 110 }],
    check: v => [v.a, v.b, v.c].every(x => { const l = okList(x, 1, 5); return l && l.every((y, i) => !i || l[i - 1] <= y); }) ? '' : 'Give each list one to five whole numbers in sorted order.',
    frames: ({ a, b, c }) => {
      const L = [okList(a, 1, 5), okList(b, 1, 5), okList(c, 1, 5)], names = ['A', 'B', 'C'], pos = [0, 0, 0], heap = [], out = [], F = [];
      const less = (p, q) => p[0] < q[0] || (p[0] === q[0] && p[1] < q[1]);
      const push = e => { heap.push(e); let i = heap.length - 1; while (i > 0 && less(heap[i], heap[(i - 1) >> 1])) { const p = (i - 1) >> 1; [heap[i], heap[p]] = [heap[p], heap[i]]; i = p; } };
      const pop = () => { const top = heap[0], last = heap.pop(); if (heap.length) { heap[0] = last; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i; if (l < heap.length && less(heap[l], heap[m])) m = l; if (r < heap.length && less(heap[r], heap[m])) m = r; if (m === i) break; [heap[i], heap[m]] = [heap[m], heap[i]]; i = m; } } return top; };
      const pic = hl => L.map((l, i) => ({ t: 'row', label: 'List ' + names[i], cells: l, small: true, cls: Object.fromEntries(l.map((_, j) => [j, j < pos[i] ? 'done' : j === pos[i] ? (hl === i ? 'look' : 'sel') : ''])) }))
        .concat([{ t: 'row', label: 'Heap of heads (smallest first)', cells: heap.length ? heap.map(e => e[0] + names[e[1]]) : ['empty'], cls: heap.length ? { 0: 'piv' } : { 0: 'ghost' } },
                 { t: 'row', label: 'Merged', cells: out.length ? out.slice() : ['empty'], cls: out.length ? { [out.length - 1]: 'yes' } : { 0: 'ghost' } }]);
      L.forEach((l, i) => push([l[0], i]));
      F.push({ mood: 'think', msg: 'Each list puts its first value into the heap.', layers: pic(-1) });
      while (heap.length) {
        const [v, i] = pop();
        out.push(v);
        pos[i]++;
        if (pos[i] < L[i].length) push([L[i][pos[i]], i]);
        F.push({ mood: 'work', msg: `Pop ${v} from list ${names[i]}. ${pos[i] < L[i].length ? `List ${names[i]} sends ${L[i][pos[i]]}.` : `List ${names[i]} is used up.`}`, layers: pic(i) });
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `Merged ${out.length} values. The heap never held more than 3, so each step cost O(log 3).`, layers: pic(-1) });
      return F;
    }
  });

  /* ---------- running median ---------- */
  D.median = el => PK.widget(el, {
    title: 'Two heaps find the middle', sub: 'Small half in a max heap, big half in a min heap. The median sits at the tops.',
    inputs: [{ k: 'nums', label: 'Numbers arriving', type: 'text', val: '5, 15, 1, 3, 8, 7, 9, 10', w: 210 }],
    random: () => ({ nums: Array.from({ length: 8 }, () => 1 + Math.floor(Math.random() * 40)).join(', ') }),
    check: v => okList(v.nums, 1, 10) ? '' : 'Give one to ten whole numbers.',
    frames: ({ nums }) => {
      const s = okList(nums, 1, 10), low = [], high = [], F = [];
      const med = () => (low.length > high.length ? low[0] : (low[0] + high[0]) / 2);
      const pic = (side) => [{ t: 'row', label: 'Small half (max heap, biggest first)', cells: low.length ? low.slice() : ['empty'], cls: low.length ? { 0: side === 'low' ? 'yes' : 'piv' } : { 0: 'ghost' } },
                             { t: 'row', label: 'Big half (min heap, smallest first)', cells: high.length ? high.slice() : ['empty'], cls: high.length ? { 0: side === 'high' ? 'yes' : 'piv' } : { 0: 'ghost' } }];
      const sortBoth = () => { low.sort((p, q) => q - p); high.sort((p, q) => p - q); };
      for (const x of s) {
        const went = !low.length || x <= low[0] ? 'small' : 'big';
        if (went === 'small') low.push(x); else high.push(x);
        sortBoth();
        F.push({ mood: 'look', msg: `${x} goes into the ${went} half.`, layers: pic(went === 'small' ? 'low' : 'high') });
        if (low.length > high.length + 1) { high.push(low.shift()); sortBoth(); F.push({ mood: 'work', msg: `The small half is too big. Move its top, ${high[0]}, across.`, layers: pic('high') }); }
        else if (high.length > low.length) { low.push(high.shift()); sortBoth(); F.push({ mood: 'work', msg: `The big half is too big. Move its top, ${low[0]}, across.`, layers: pic('low') }); }
        F.push({ mood: 'happy', msg: `Median so far: <b>${med()}</b>.`, vars: { median: med(), count: low.length + high.length }, layers: pic('') });
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `Each number cost O(log n) to place, and the median is always ready at the tops: ${med()}.`, vars: { median: med() }, layers: pic('') });
      return F;
    }
  });

  /* ---------- meeting rooms ---------- */
  D.rooms = el => PK.widget(el, {
    title: 'How many rooms?', sub: 'Meetings sorted by start. The heap holds when each busy room frees up. Reuse the earliest room if it is free in time.',
    inputs: [{ k: 'm', label: 'Meetings (start-end)', type: 'text', val: '9-10, 9-12, 10-11, 11-13, 12-14, 13-15', w: 260 }],
    check: v => { const p = String(v.m).split(/[\s,]+/).filter(Boolean); return p.length >= 1 && p.length <= 8 && p.every(x => /^\d{1,2}-\d{1,2}$/.test(x) && Number(x.split('-')[0]) < Number(x.split('-')[1])) ? '' : 'Write one to eight meetings like 9-10, with start before end.'; },
    frames: ({ m }) => {
      const ms = String(m).split(/[\s,]+/).filter(Boolean).map(x => x.split('-').map(Number)).sort((p, q) => p[0] - q[0] || p[1] - q[1]);
      const ends = [], F = [];
      const pic = (j, c) => [{ t: 'row', label: 'Meetings, sorted by start', cells: ms.map(x => x.join('-')), cls: Object.fromEntries(ms.map((_, i) => [i, i < j ? 'done' : i === j ? c : ''])) },
                            { t: 'row', label: 'Rooms free again at (earliest first)', cells: ends.length ? ends.map(e => '🚪' + e) : ['no rooms yet'], cls: ends.length ? { 0: 'piv' } : { 0: 'ghost' } }];
      ms.forEach(([s0, e0], j) => {
        if (ends.length && ends[0] <= s0) {
          const old = ends.shift(); ends.push(e0); ends.sort((p, q) => p - q);
          F.push({ mood: 'happy', msg: `${s0}-${e0}: the room free at ${old} is free by ${s0}. Reuse it.`, vars: { rooms: ends.length }, layers: pic(j, 'yes') });
        } else {
          const first = ends[0];
          ends.push(e0); ends.sort((p, q) => p - q);
          F.push({ mood: 'sad', fx: ends.length > 1 ? 'shake' : '', msg: `${s0}-${e0}: ${first !== undefined ? `the earliest room frees at ${first}, too late. Open a new room.` : 'no rooms yet, open the first one.'}`, vars: { rooms: ends.length }, layers: pic(j, 'no') });
        }
      });
      F.push({ mood: 'wow', fx: 'rain', msg: `<b>${ends.length}</b> room${ends.length > 1 ? 's are' : ' is'} enough for all ${ms.length} meetings.`, vars: { rooms: ends.length }, layers: pic(ms.length, '') });
      return F;
    }
  });
})();
'''

INFO = {
    'title': 'The smallest is always on top',
    'panels': [
        {'s': [['e', '⛰️'], ['t', 'parent ≤ children', {'b': 1}]], 'h': 'Min heap', 't': 'A complete tree stored in an array.', 'more': 'Push sifts up, pop sifts down, both O(log n).'},
        {'s': [['e', '🏗️'], ['t', 'last parent → root', {'b': 1}]], 'h': 'Heapify', 't': 'Build a heap in O(n).', 'more': 'Most nodes are near the bottom and barely move.'},
        {'s': [['e', '🏅'], ['t', 'heap of size k', {'b': 1}]], 'h': 'Top k', 't': 'The root guards the door.', 'more': 'Min heap for the k largest, max heap for the k smallest.'},
        {'s': [['e', '⚖️'], ['t', 'max heap | min heap', {'b': 1}]], 'h': 'Two heaps', 't': 'The median sits at the two tops.', 'more': 'Keep the halves balanced after every insert.'},
    ],
    'remember': 'Reach for a heap whenever you repeatedly need the smallest or biggest item while items keep arriving. Push and pop cost O(log n), peeking costs O(1), and building from a list costs O(n).',
}

REAL = [
    ['🚑', 'A hospital emergency room', 'Patients are seen by urgency, not by arrival. The most urgent case is always on top of the priority queue.'],
    ['🏆', 'A live leaderboard', 'A game keeps only the top 10 scores. A new score is compared with the lowest of the ten, exactly like the top k heap.'],
    ['🖥️', 'Your computer choosing what runs next', 'The operating system keeps ready tasks in priority queues and picks the most important one many times a second.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to heaps in depth. A heap always keeps the smallest, or the biggest, value on top. You will watch values sift up and down, build a heap in linear time, sort with a heap, keep the top k of a stream, merge many sorted lists, track a running median with two heaps, and work out how many meeting rooms you need.'},
    {'id': 'sift', 'h': 'Sift up and down', 'en': 'A new value joins at the end of the heap and swaps with its parent while the parent is bigger. That is sift up. When the root is removed, the last value jumps to the top and swaps with its smaller child until both children are bigger. That is sift down. Each move follows one path, so it costs about log n swaps.'},
    {'id': 'heapify', 'h': 'Heapify', 'en': 'To build a heap from a list, do not push values one by one. Leave them in place and sift down every parent, starting from the last parent and ending at the root. Most nodes are near the bottom and move very little, so the whole build costs linear time.'},
    {'id': 'heap-sort', 'h': 'Heap sort', 'en': 'Heap sort builds a max heap, then swaps the biggest value at the root to the end of the array, shrinks the heap by one, and sifts the new root down. Repeat until the heap is empty. It needs no extra memory and is n log n even in the worst case, but it is not stable.'},
    {'id': 'top-k', 'h': 'Top k', 'en': 'To keep the k biggest values of a long stream, keep a min heap of size k. Its root is the smallest of the top k. A new value that is not bigger than the root is ignored at once. A bigger one replaces the root. Memory stays at k values.'},
    {'id': 'k-way-merge', 'h': 'K way merge', 'en': 'To merge several sorted lists, put the first value of each list into a min heap. Pop the smallest, add it to the result, and push the next value from the same list. With n values in k lists, the cost is n log k.'},
    {'id': 'running-median', 'h': 'Running median', 'en': 'Keep the smaller half of the numbers in a max heap and the bigger half in a min heap. After every insert, move one value across if the sizes drift apart. The median is the top of the max heap, or the average of the two tops when both halves are the same size.'},
    {'id': 'scheduling', 'h': 'Scheduling', 'en': 'Sort meetings by start time and keep a min heap of the times when busy rooms become free. If the earliest free time is not after the next meeting starts, reuse that room. Otherwise open a new one. The number of rooms in the heap at the end is the answer.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from last stone weight to meeting rooms three. Each one is solved in Python, JavaScript, Java and TypeScript, and you can replay every solution line by line.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. For each problem, first ask what you need on top of the heap, the smallest or the biggest, and how many items the heap should hold. Then write the code. Open the hint if you are stuck.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'In a min heap, where is the smallest value?', 'o': ['At the last index', 'At the root, index 0', 'In a leaf', 'Anywhere'], 'a': 1, 'hint': 'Every parent is smaller than its children.', 'why': 'Following parents upward always gets smaller, so the root holds the minimum.'},
    {'lv': 'e', 'q': 'What is the index of the left child of index 3?', 'o': ['6', '7', '8', '4'], 'a': 1, 'hint': '2i + 1.', 'why': '2 × 3 + 1 = 7.'},
    {'lv': 'e', 'q': 'What is the parent index of index 10?', 'o': ['5', '4', '3', '9'], 'a': 1, 'hint': '⌊(i − 1) / 2⌋.', 'why': '(10 − 1) / 2 = 4.5, rounded down to 4.'},
    {'lv': 'e', 'q': 'To keep the 5 largest numbers of a stream, which heap do you use?', 'o': ['A max heap of size 5', 'A min heap of size 5', 'A max heap of everything', 'No heap'], 'a': 1, 'hint': 'You need to know the weakest member of the top 5.', 'why': 'The min heap root is the smallest of the top 5, so a newcomer only has to beat it.'},
    {'lv': 'm', 'q': 'How long does building a heap bottom up from n values take?', 'o': ['O(log n)', 'O(n)', 'O(n log n)', 'O(n²)'], 'a': 1, 'hint': 'Most nodes are near the bottom.', 'why': 'Half the nodes are leaves that never move, a quarter move at most one level, and the sum is O(n).'},
    {'lv': 'm', 'q': 'Is heap sort stable?', 'o': ['Yes', 'No', 'Only for integers', 'Only in Java'], 'a': 1, 'hint': 'Swapping the root to the end can jump over equal values.', 'why': 'Long distance swaps can reorder equal keys, so heap sort is not stable.'},
    {'lv': 'm', 'q': 'Python heapq is a min heap. How do you use it as a max heap for numbers?', 'o': ['Pass reverse=True', 'Store negative values', 'Sort the list first', 'Use heapq.maxheap'], 'a': 1, 'hint': 'Flip the order of the numbers.', 'why': 'Pushing −x makes the biggest x the smallest key. Negate again when popping.'},
    {'lv': 'm', 'q': 'Merging k sorted lists with N values in total using a heap costs?', 'o': ['O(N)', 'O(N log k)', 'O(N log N)', 'O(N k)'], 'a': 1, 'hint': 'The heap never holds more than k items.', 'why': 'Each of the N values is pushed and popped once on a heap of size k.'},
    {'lv': 'h', 'q': 'Push 5, 3, 8, 1 into an empty min heap. What does the array look like?', 'o': ['1 3 5 8', '1 3 8 5', '1 5 8 3', '3 1 8 5'], 'a': 1, 'hint': 'Sift up after each push.', 'why': '5 | 3 5 | 3 5 8 | 1 joins at index 3, swaps with 5, then with 3: 1 3 8 5.'},
    {'lv': 'h', 'q': 'In the running median, the small half has 4 values and the big half has 4. What is the median?', 'o': ['The top of the small half', 'The top of the big half', 'The average of both tops', 'The root of a third heap'], 'a': 2, 'hint': 'An even count has two middle values.', 'why': 'The two middle values are the two tops, so the median is their average.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'import heapq\nh = [5, 1, 4]\nheapq.heapify(h)\nheapq.heappush(h, 0)\nprint(heapq.heappop(h), heapq.heappop(h))', 'o': ['0 1', '5 4', '1 0', '0 4'], 'a': 0, 'hint': 'Pops come out smallest first.', 'why': 'The values are 0, 1, 4, 5, so the first two pops are 0 and 1.'},
    {'lv': 'h', 'q': 'Why can a heap not find any value quickly, like a search tree can?', 'o': ['It is too small', 'It only orders parents against children, not left against right', 'It uses an array', 'It can'], 'a': 1, 'hint': 'Is the left subtree smaller than the right?', 'why': 'Siblings have no order, so a value could be in either subtree and a search may visit every node, O(n).'},
    {'lv': 'x', 'q': 'Meeting times [1,4], [2,5], [3,6], [5,7]. How many rooms are needed?', 'o': ['1', '2', '3', '4'], 'a': 2, 'hint': 'Count the most meetings happening at one moment.', 'why': 'At time 3, meetings [1,4], [2,5] and [3,6] all run, so 3 rooms are needed. [5,7] can reuse the room freed at 4.'},
    {'lv': 'x', 'q': 'Single-Threaded CPU sorts by arrival and uses a heap of ready tasks. What is the heap ordered by?', 'o': ['Arrival time', 'Length, then index', 'Index only', 'Length, longest first'], 'a': 1, 'hint': 'The CPU picks the shortest ready task.', 'why': 'Shortest processing time first, ties broken by the smaller index.'},
    {'lv': 'x', 'q': 'Bottom up heapify on 1023 values in descending order makes 1013 swaps. Pushing one by one makes 8194. Why is pushing slower?', 'o': ['Pushing uses more memory', 'Every new value sifts all the way to the root, about log n swaps each', 'Heapify skips values', 'It is not slower'], 'a': 1, 'hint': 'Each new value is the smallest so far.', 'why': 'In descending order each pushed value is a new minimum and climbs to the root, giving about n log n swaps.'},
    {'lv': 'x', 'q': 'A d-ary heap gives each node d children. What happens to the height?', 'o': ['It grows', 'It shrinks to about log_d n', 'It stays log₂ n', 'It becomes n / d'], 'a': 1, 'hint': 'More children per node means fewer levels.', 'why': 'Each level holds d times more nodes, so the height is about log_d n. Sift up gets faster, sift down compares d children per level.'},
]

CALC = [
    {'lv': 'e', 'q': 'What is the index of the right child of index 4?', 'ans': '10', 'hint': '2i + 2.', 'steps': ['<span class="eq">2 × 4 + 2 = 10</span>']},
    {'lv': 'e', 'q': 'A heap holds 15 values. How many levels does it have?', 'ans': '4', 'hint': '1 + 2 + 4 + 8 = 15.', 'steps': ['<span class="eq">⌊log₂ 15⌋ + 1 = 3 + 1 = 4</span>']},
    {'lv': 'm', 'q': 'At most how many swaps does one push make on a heap of 1000 values?', 'ans': '9', 'hint': 'The new value starts at the deepest level.', 'steps': ['A heap of 1001 values has <span class="eq">⌊log₂ 1001⌋ + 1 = 10</span> levels.', 'Climbing from level 10 to the root takes <span class="eq">9</span> swaps.']},
    {'lv': 'm', 'q': 'How many leaves does a heap of 20 values have?', 'ans': '10', 'hint': 'Indexes ⌊n / 2⌋ to n − 1 are leaves.', 'steps': ['Leaves are indexes 10 to 19: <span class="eq">20 − 10 = 10</span>']},
    {'lv': 'h', 'q': 'Bottom up heapify on 15 values starts at which index?', 'ans': '6', 'hint': 'The last parent is ⌊n / 2⌋ − 1.', 'steps': ['<span class="eq">⌊15 / 2⌋ − 1 = 7 − 1 = 6</span>']},
    {'lv': 'h', 'q': 'The running median has seen 5, 15, 1, 3. What is the median?', 'ans': '4', 'hint': 'Sorted: 1 3 5 15.', 'steps': ['Small half 1 3, big half 5 15.', '<span class="eq">(3 + 5) ÷ 2 = 4</span>']},
    {'lv': 'x', 'q': 'Merging 8 sorted lists of 1000 values each with a heap. About how many comparisons, using log₂ 8 per value?', 'ans': '24000', 'hint': 'N log₂ k.', 'steps': ['N = 8000 values, k = 8 lists.', '<span class="eq">8000 × log₂ 8 = 8000 × 3 = 24000</span>']},
    {'lv': 'x', 'q': 'The lesson program builds a heap from 15 values in descending order. How many swaps does bottom up use?', 'ans': '11', 'hint': 'Run the heapify lesson program.', 'steps': ['The output reads: n = 15, bottom up swaps: <span class="eq">11</span>']},
]

TALK = {
    'sift': 'Think of a heap as a company where every boss must be smaller than the people who report to them, and the smallest person of all sits at the very top. When a new person joins, they start at the bottom of the chart, in the next free spot. If they are smaller than their boss, the two swap places. They keep climbing like this until their boss is smaller, or until they reach the top. That climb is called sift up. When the person at the top leaves, the company needs a new top. The trick is to take the person from the last spot at the bottom and put them at the top. Now they are probably too big, so they swap with their smaller assistant, again and again, until both assistants are bigger. That fall is called sift down. Either way, the person only travels along one path, and a heap of a million people has just twenty levels.',
    'heapify': 'Suppose you already have a whole list of numbers and want to turn it into a heap. The obvious way is to push them in one at a time, and each push may climb all the way to the top. There is a cleverer way. Leave the numbers exactly where they are in the array. Notice that every leaf, a node with no children, is already a perfect little heap of one. So start at the last node that has children and sift it down. Then move one step left and do the same, all the way back to the root. Why is this faster? Because half of the nodes are leaves and do not move at all. A quarter of them can move at most one level. Only the root might travel the full height. When you add it all up, the total work is proportional to n, not n log n. Python\'s heapify function works exactly this way.',
    'heap-sort': 'Heap sort turns the heap into a sorting machine. First, build a max heap from the list, so the biggest value sits at the very front. Now swap that biggest value with the last value in the list. The biggest value is now in its final place, at the end. Pretend the list is one item shorter, and sift the new front value down so the heap is fixed again. The next biggest value rises to the front. Swap it into the second last place, shrink the heap again, and repeat. The sorted part grows from the back while the heap shrinks from the front, all inside the same array. That means heap sort needs no extra memory, and it is guaranteed to finish in n log n time even for the worst possible input. The catch is that it can reorder equal values, so it is not stable, and in practice quick sort is usually a little faster.',
    'top-k': 'Imagine a game with millions of players and you want to show the top three scores. Storing every score and sorting them would be wasteful. Instead, keep a tiny min heap that holds only three scores. The smallest of those three sits on top, like a doorkeeper. When a new score arrives, compare it with the doorkeeper. If it is not bigger, it cannot be in the top three, so it is turned away at once. If it is bigger, the doorkeeper is pushed out and the new score joins, and the heap finds its new doorkeeper. Each check costs only about log three steps, and the memory never grows beyond three scores, however long the game runs. It feels backwards at first, but remember the rule: to keep the biggest values, use a min heap. To keep the smallest values, use a max heap. The root is always the weakest member of the club.',
    'k-way-merge': 'Imagine three teachers, each holding a pile of exam papers already sorted by student number. You want one big sorted pile. At every moment, the next paper must be the top paper of one of the three piles. So you only ever need to compare three papers. A min heap holds the top paper from each pile. Pop the smallest one and add it to your big pile. Then that teacher hands you their next paper, which goes into the heap. Repeat until all the piles are empty. The heap never holds more than one paper per pile, so each step is quick even when there are thousands of piles. This is called a k way merge. Databases use it to merge sorted chunks of data that are too big to fit in memory at once, and Python offers it ready made as heapq merge.',
    'running-median': 'Suppose numbers keep arriving one by one, and after each one you must say the median, the value in the middle. Sorting everything again every time would be slow. Here is a lovely trick with two heaps. Picture a see saw. On the left side sits a max heap holding the smaller half of the numbers, with its biggest value on top. On the right side sits a min heap holding the bigger half, with its smallest value on top. The two tops meet right in the middle of the see saw. When a new number arrives, put it on the correct side. If one side becomes too heavy, move its top value across to the other side. Now the median is either the top of the left heap, when it holds one extra number, or the average of the two tops. Each new number costs only log n work, and the median is always ready instantly.',
    'scheduling': 'Picture an office with meetings booked all day, and you have to decide how many meeting rooms the office needs. Sort the meetings by their start time. Keep a min heap that remembers when each busy room will become free, with the earliest time on top. For each meeting, look at the top of the heap. If that room becomes free before or exactly when the meeting starts, the meeting can use it, so replace that room\'s free time with the new meeting\'s end time. If even the earliest room is still busy, you have no choice, and you open a new room. At the end, the number of rooms in the heap is the smallest number that works. Computers use this same idea constantly. Operating systems, print queues and cloud servers all keep priority queues of jobs, and pick whatever should happen next in a fraction of a second.',
    'leetcode': 'The LeetCode problems in this chapter all use a heap in a different way. You start by smashing stones together, always grabbing the two heaviest from a max heap, and by tracking the k-th largest number as a stream flows past. Next you find the most frequent values and the points closest to the origin by keeping a heap of fixed size and throwing out whatever does not belong. The hard problems ask you to merge many sorted linked lists by keeping a heap of their heads, and to simulate a CPU that always runs the shortest waiting task. The expert problems are the two heap median finder, and a tricky meeting room booking system that juggles a heap of free rooms and a heap of busy rooms. JavaScript and TypeScript have no built in heap, so those solutions include a small heap class you can reuse.',
}

T = t.finish({
    'slug': 'heaps', 'title': 'Heaps in Depth', 'short': 'Heaps in depth', 'emoji': '⛰️', 'topic': 'heaps', 'prefix': 'dsaheap',
    'module': ('🌳', 'Trees and graphs'),
    'lead': 'The smallest value always waits on top. Watch values sift up and down, build a heap in linear time, sort with it, guard the top k of a stream, merge sorted lists, track a running median with two heaps and schedule meeting rooms.',
    'desc': 'Heaps in DSA: sift up and sift down, building a heap in O(n), heap sort, top k with a heap, k way merge, the running median with two heaps and scheduling with priority queues, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 22,
    'summary': 'Sift up and sift down, building a heap in O(n), heap sort, top k with a small heap, merging k sorted lists, the running median with two heaps and scheduling meeting rooms. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['heap', 'binary heap', 'min heap', 'max heap', 'priority queue', 'sift up', 'sift down', 'heapify', 'heap sort', 'top k', 'k way merge', 'running median', 'two heaps', 'meeting rooms', 'heapq', 'PriorityQueue'],
    'added': '2026-11-23',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS, 'css': '',
    'prev': ('trees', 'trees', '🌲 Trees'),
    'next': ('balanced-trees', 'balanced-trees', '🔄 Balanced trees'),
})
