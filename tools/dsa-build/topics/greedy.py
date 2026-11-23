# Greedy algorithms: the greedy choice and when it fails, interval scheduling, the fractional knapsack,
# Huffman codes, removing digits with a stack, and shortest job first with an exchange argument.
from kit4 import Topic

t = Topic()

# a small binary heap for the JavaScript and TypeScript programs, which have no heap built in (same as the Heaps chapter)
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
t.code('coins', py=r'''
def greedy_coins(amount, coins):
    used = []
    for c in sorted(coins, reverse=True):     # always grab the biggest coin that still fits
        while amount >= c:
            amount -= c
            used.append(c)
    return used


def fewest_coins(amount, coins):              # the true answer, by trying every amount from 0 up
    best = [0] + [None] * amount
    for a in range(1, amount + 1):
        options = [best[a - c] for c in coins if c <= a and best[a - c] is not None]
        best[a] = min(options) + 1 if options else None
    return best[amount]


for amount, coins in ((63, [1, 5, 10, 25]), (6, [1, 3, 4]), (30, [1, 10, 25])):
    g = greedy_coins(amount, coins)
    print(f"amount {amount} with {coins}: greedy {len(g)} coins {g}, fewest possible {fewest_coins(amount, coins)}")
''', js=r'''
function greedyCoins(amount, coins) {
  const used = [];
  for (const c of [...coins].sort((x, y) => y - x)) {   // always grab the biggest coin that still fits
    while (amount >= c) { amount -= c; used.push(c); }
  }
  return used;
}

function fewestCoins(amount, coins) {         // the true answer, by trying every amount from 0 up
  const best = [0, ...new Array(amount).fill(null)];
  for (let a = 1; a <= amount; a++) {
    const options = coins.filter(c => c <= a && best[a - c] !== null).map(c => best[a - c]);
    best[a] = options.length ? Math.min(...options) + 1 : null;
  }
  return best[amount];
}

for (const [amount, coins] of [[63, [1, 5, 10, 25]], [6, [1, 3, 4]], [30, [1, 10, 25]]]) {
  const g = greedyCoins(amount, coins);
  console.log(`amount ${amount} with [${coins.join(", ")}]: greedy ${g.length} coins [${g.join(", ")}], fewest possible ${fewestCoins(amount, coins)}`);
}
''', java=r'''
import java.util.*;

public class Coins {
    static List<Integer> greedyCoins(int amount, int[] coins) {
        List<Integer> used = new ArrayList<>();
        int[] c = coins.clone();
        Arrays.sort(c);
        for (int i = c.length - 1; i >= 0; i--) {           // always grab the biggest coin that still fits
            while (amount >= c[i]) { amount -= c[i]; used.add(c[i]); }
        }
        return used;
    }

    static int fewestCoins(int amount, int[] coins) {      // the true answer, by trying every amount from 0 up
        int[] best = new int[amount + 1];
        Arrays.fill(best, -1);
        best[0] = 0;
        for (int a = 1; a <= amount; a++)
            for (int c : coins)
                if (c <= a && best[a - c] != -1 && (best[a] == -1 || best[a - c] + 1 < best[a])) best[a] = best[a - c] + 1;
        return best[amount];
    }

    public static void main(String[] args) {
        int[][] coinSets = {{1, 5, 10, 25}, {1, 3, 4}, {1, 10, 25}};
        int[] amounts = {63, 6, 30};
        for (int k = 0; k < 3; k++) {
            List<Integer> g = greedyCoins(amounts[k], coinSets[k]);
            System.out.println("amount " + amounts[k] + " with " + Arrays.toString(coinSets[k]) + ": greedy " + g.size() + " coins " + g + ", fewest possible " + fewestCoins(amounts[k], coinSets[k]));
        }
    }
}
''', ts=r'''
function greedyCoins(amount: number, coins: number[]): number[] {
  const used: number[] = [];
  for (const c of [...coins].sort((x, y) => y - x)) {   // always grab the biggest coin that still fits
    while (amount >= c) { amount -= c; used.push(c); }
  }
  return used;
}

function fewestCoins(amount: number, coins: number[]): number | null {   // the true answer, trying every amount from 0 up
  const best: (number | null)[] = [0, ...new Array(amount).fill(null)];
  for (let a = 1; a <= amount; a++) {
    const options = coins.filter(c => c <= a && best[a - c] !== null).map(c => best[a - c] as number);
    best[a] = options.length ? Math.min(...options) + 1 : null;
  }
  return best[amount];
}

const cases: [number, number[]][] = [[63, [1, 5, 10, 25]], [6, [1, 3, 4]], [30, [1, 10, 25]]];
for (const [amount, coins] of cases) {
  const g = greedyCoins(amount, coins);
  console.log(`amount ${amount} with [${coins.join(", ")}]: greedy ${g.length} coins [${g.join(", ")}], fewest possible ${fewestCoins(amount, coins)}`);
}
''')

t.code('activity', py=r'''
def pick_activities(acts):
    chosen, free_at = [], 0
    for name, start, end in sorted(acts, key=lambda a: a[2]):   # the one that finishes first goes first
        if start >= free_at:                  # it starts after the last chosen one ends
            chosen.append(name)
            free_at = end
    return chosen


acts = [("yoga", 1, 4), ("chess", 3, 5), ("swim", 0, 6), ("art", 5, 7),
        ("code", 3, 9), ("piano", 5, 9), ("run", 6, 10), ("film", 8, 11), ("quiz", 8, 12), ("dance", 2, 14), ("tea", 12, 16)]
picked = pick_activities(acts)
print("chosen:", " ".join(picked))
print(len(picked), "activities, the most that fit without overlapping")
''', js=r'''
function pickActivities(acts) {
  const chosen = [];
  let freeAt = 0;
  for (const [name, start, end] of [...acts].sort((a, b) => a[2] - b[2])) {   // the one that finishes first goes first
    if (start >= freeAt) { chosen.push(name); freeAt = end; }   // it starts after the last chosen one ends
  }
  return chosen;
}

const acts = [["yoga", 1, 4], ["chess", 3, 5], ["swim", 0, 6], ["art", 5, 7],
              ["code", 3, 9], ["piano", 5, 9], ["run", 6, 10], ["film", 8, 11], ["quiz", 8, 12], ["dance", 2, 14], ["tea", 12, 16]];
const picked = pickActivities(acts);
console.log("chosen:", picked.join(" "));
console.log(picked.length, "activities, the most that fit without overlapping");
''', java=r'''
import java.util.*;

public class Activities {
    record Act(String name, int start, int end) {}

    static List<String> pickActivities(List<Act> acts) {
        List<Act> sorted = new ArrayList<>(acts);
        sorted.sort(Comparator.comparingInt(Act::end));          // the one that finishes first goes first
        List<String> chosen = new ArrayList<>();
        int freeAt = 0;
        for (Act a : sorted) {
            if (a.start() >= freeAt) { chosen.add(a.name()); freeAt = a.end(); }   // it starts after the last chosen one ends
        }
        return chosen;
    }

    public static void main(String[] args) {
        List<Act> acts = List.of(new Act("yoga", 1, 4), new Act("chess", 3, 5), new Act("swim", 0, 6), new Act("art", 5, 7),
                new Act("code", 3, 9), new Act("piano", 5, 9), new Act("run", 6, 10), new Act("film", 8, 11), new Act("quiz", 8, 12), new Act("dance", 2, 14), new Act("tea", 12, 16));
        List<String> picked = pickActivities(acts);
        System.out.println("chosen: " + String.join(" ", picked));
        System.out.println(picked.size() + " activities, the most that fit without overlapping");
    }
}
''', ts=r'''
type Act = [string, number, number];

function pickActivities(acts: Act[]): string[] {
  const chosen: string[] = [];
  let freeAt = 0;
  for (const [title, start, end] of [...acts].sort((a, b) => a[2] - b[2])) {   // the one that finishes first goes first
    if (start >= freeAt) { chosen.push(title); freeAt = end; }   // it starts after the last chosen one ends
  }
  return chosen;
}

const acts: Act[] = [["yoga", 1, 4], ["chess", 3, 5], ["swim", 0, 6], ["art", 5, 7],
                     ["code", 3, 9], ["piano", 5, 9], ["run", 6, 10], ["film", 8, 11], ["quiz", 8, 12], ["dance", 2, 14], ["tea", 12, 16]];
const picked = pickActivities(acts);
console.log("chosen:", picked.join(" "));
console.log(picked.length, "activities, the most that fit without overlapping");
''')

t.code('fractional', py=r'''
def fractional_knapsack(items, capacity):
    total = 0.0
    for name, value, weight in sorted(items, key=lambda it: it[1] / it[2], reverse=True):   # best value per kg first
        take = min(weight, capacity)
        total += value * take / weight
        capacity -= take
        print(f"take {take} of {weight} kg of {name}, worth {value * take / weight:.1f}")
        if capacity == 0:
            break
    return total


items = [("gold", 60, 10), ("silver", 100, 20), ("bronze", 120, 30)]
print(f"best total: {fractional_knapsack(items, 50):.1f}")
print("if items cannot be cut: greedy by value per kg takes gold + silver = 160, but silver + bronze = 220")
''', js=r'''
function fractionalKnapsack(items, capacity) {
  let total = 0;
  for (const [name, value, weight] of [...items].sort((a, b) => b[1] / b[2] - a[1] / a[2])) {   // best value per kg first
    const take = Math.min(weight, capacity);
    total += value * take / weight;
    capacity -= take;
    console.log(`take ${take} of ${weight} kg of ${name}, worth ${(value * take / weight).toFixed(1)}`);
    if (capacity === 0) break;
  }
  return total;
}

const items = [["gold", 60, 10], ["silver", 100, 20], ["bronze", 120, 30]];
console.log(`best total: ${fractionalKnapsack(items, 50).toFixed(1)}`);
console.log("if items cannot be cut: greedy by value per kg takes gold + silver = 160, but silver + bronze = 220");
''', java=r'''
import java.util.*;

public class FractionalKnapsack {
    record Item(String name, int value, int weight) {}

    static double fractionalKnapsack(List<Item> items, int capacity) {
        List<Item> sorted = new ArrayList<>(items);
        sorted.sort((a, b) -> Double.compare((double) b.value() / b.weight(), (double) a.value() / a.weight()));   // best value per kg first
        double total = 0;
        for (Item it : sorted) {
            int take = Math.min(it.weight(), capacity);
            double worth = (double) it.value() * take / it.weight();
            total += worth;
            capacity -= take;
            System.out.println("take " + take + " of " + it.weight() + " kg of " + it.name() + ", worth " + String.format("%.1f", worth));
            if (capacity == 0) break;
        }
        return total;
    }

    public static void main(String[] args) {
        List<Item> items = List.of(new Item("gold", 60, 10), new Item("silver", 100, 20), new Item("bronze", 120, 30));
        System.out.println("best total: " + String.format("%.1f", fractionalKnapsack(items, 50)));
        System.out.println("if items cannot be cut: greedy by value per kg takes gold + silver = 160, but silver + bronze = 220");
    }
}
''', ts=r'''
type Item = [string, number, number];

function fractionalKnapsack(items: Item[], capacity: number): number {
  let total = 0;
  for (const [title, value, weight] of [...items].sort((a, b) => b[1] / b[2] - a[1] / a[2])) {   // best value per kg first
    const take = Math.min(weight, capacity);
    total += value * take / weight;
    capacity -= take;
    console.log(`take ${take} of ${weight} kg of ${title}, worth ${(value * take / weight).toFixed(1)}`);
    if (capacity === 0) break;
  }
  return total;
}

const items: Item[] = [["gold", 60, 10], ["silver", 100, 20], ["bronze", 120, 30]];
console.log(`best total: ${fractionalKnapsack(items, 50).toFixed(1)}`);
console.log("if items cannot be cut: greedy by value per kg takes gold + silver = 160, but silver + bronze = 220");
''')

t.code('huffman', py=r'''
import heapq


def huffman_codes(freq):
    heap, uid = [], 0
    for ch in sorted(freq):                   # each letter starts as a tiny tree of its own
        heap.append((freq[ch], uid, ch))
        uid += 1
    heapq.heapify(heap)
    while len(heap) > 1:                      # join the two rarest trees, again and again
        f1, _, left = heapq.heappop(heap)
        f2, _, right = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, uid, (left, right)))
        uid += 1
    codes = {}

    def walk(node, code):                     # left adds a 0, right adds a 1
        if isinstance(node, str):
            codes[node] = code or "0"
        else:
            walk(node[0], code + "0")
            walk(node[1], code + "1")

    walk(heap[0][2], "")
    return codes


freq = {"a": 5, "b": 9, "c": 12, "d": 13, "e": 16, "f": 45}
codes = huffman_codes(freq)
for ch in sorted(codes):
    print(ch, freq[ch], codes[ch])
print("total bits:", sum(freq[ch] * len(codes[ch]) for ch in freq), " fixed 3 bit codes would need", 3 * sum(freq.values()))
''', js=JS_HEAP + r'''
function huffmanCodes(freq) {
  const heap = new Heap((x, y) => x[0] !== y[0] ? x[0] < y[0] : x[1] < y[1]);   // by count, then by age
  let uid = 0;
  for (const ch of Object.keys(freq).sort()) heap.push([freq[ch], uid++, ch]);   // each letter starts as its own tree
  while (heap.size > 1) {                     // join the two rarest trees, again and again
    const [f1, , left] = heap.pop();
    const [f2, , right] = heap.pop();
    heap.push([f1 + f2, uid++, [left, right]]);
  }
  const codes = {};
  const walk = (node, code) => {              // left adds a 0, right adds a 1
    if (typeof node === "string") codes[node] = code || "0";
    else { walk(node[0], code + "0"); walk(node[1], code + "1"); }
  };
  walk(heap.peek()[2], "");
  return codes;
}

const freq = { a: 5, b: 9, c: 12, d: 13, e: 16, f: 45 };
const codes = huffmanCodes(freq);
for (const ch of Object.keys(codes).sort()) console.log(ch, freq[ch], codes[ch]);
const bits = Object.keys(freq).reduce((s, ch) => s + freq[ch] * codes[ch].length, 0);
console.log("total bits:", bits, " fixed 3 bit codes would need", 3 * Object.values(freq).reduce((s, x) => s + x, 0));
''', java=r'''
import java.util.*;

public class Huffman {
    static class HNode {
        int freq, id;
        char ch;
        HNode left, right;
        HNode(int f, int i, char c, HNode l, HNode r) { freq = f; id = i; ch = c; left = l; right = r; }
    }

    static void walk(HNode node, String code, Map<Character, String> codes) {   // left adds a 0, right adds a 1
        if (node.left == null) { codes.put(node.ch, code.isEmpty() ? "0" : code); return; }
        walk(node.left, code + "0", codes);
        walk(node.right, code + "1", codes);
    }

    public static void main(String[] args) {
        TreeMap<Character, Integer> freq = new TreeMap<>(Map.of('a', 5, 'b', 9, 'c', 12, 'd', 13, 'e', 16, 'f', 45));
        PriorityQueue<HNode> heap = new PriorityQueue<>((x, y) -> x.freq != y.freq ? x.freq - y.freq : x.id - y.id);   // by count, then age
        int uid = 0;
        for (var e : freq.entrySet()) heap.add(new HNode(e.getValue(), uid++, e.getKey(), null, null));   // each letter is its own tree
        while (heap.size() > 1) {                                  // join the two rarest trees, again and again
            HNode left = heap.poll(), right = heap.poll();
            heap.add(new HNode(left.freq + right.freq, uid++, ' ', left, right));
        }
        Map<Character, String> codes = new TreeMap<>();
        walk(heap.peek(), "", codes);
        int bits = 0, all = 0;
        for (var e : codes.entrySet()) {
            System.out.println(e.getKey() + " " + freq.get(e.getKey()) + " " + e.getValue());
            bits += freq.get(e.getKey()) * e.getValue().length();
            all += freq.get(e.getKey());
        }
        System.out.println("total bits: " + bits + "  fixed 3 bit codes would need " + 3 * all);
    }
}
''', ts=TS_HEAP + r'''
type Tree = string | [Tree, Tree];

function huffmanCodes(freq: Record<string, number>): Record<string, string> {
  const heap = new Heap<[number, number, Tree]>((x, y) => x[0] !== y[0] ? x[0] < y[0] : x[1] < y[1]);   // by count, then by age
  let uid = 0;
  for (const ch of Object.keys(freq).sort()) heap.push([freq[ch], uid++, ch]);   // each letter starts as its own tree
  while (heap.size > 1) {                     // join the two rarest trees, again and again
    const [f1, , left] = heap.pop();
    const [f2, , right] = heap.pop();
    heap.push([f1 + f2, uid++, [left, right]]);
  }
  const codes: Record<string, string> = {};
  const walk = (node: Tree, code: string): void => {   // left adds a 0, right adds a 1
    if (typeof node === "string") codes[node] = code || "0";
    else { walk(node[0], code + "0"); walk(node[1], code + "1"); }
  };
  walk(heap.peek()[2], "");
  return codes;
}

const freq: Record<string, number> = { a: 5, b: 9, c: 12, d: 13, e: 16, f: 45 };
const codes = huffmanCodes(freq);
for (const ch of Object.keys(codes).sort()) console.log(ch, freq[ch], codes[ch]);
const bits = Object.keys(freq).reduce((s, ch) => s + freq[ch] * codes[ch].length, 0);
console.log("total bits:", bits, " fixed 3 bit codes would need", 3 * Object.values(freq).reduce((s, x) => s + x, 0));
''')

t.code('digits', py=r'''
def remove_k_digits(num, k):
    stack = []
    for d in num:
        while k and stack and stack[-1] > d:  # a bigger digit in front of a smaller one: drop it
            stack.pop()
            k -= 1
        stack.append(d)
    if k:
        stack = stack[:-k]                    # still digits to drop: the end is the biggest part
    return "".join(stack).lstrip("0") or "0"


for num, k in (("1432219", 3), ("10200", 1), ("10", 2), ("12345", 2)):
    print(f"{num} remove {k} -> {remove_k_digits(num, k)}")
''', js=r'''
function removeKdigits(num, k) {
  const stack = [];
  for (const d of num) {
    while (k && stack.length && stack[stack.length - 1] > d) { stack.pop(); k--; }   // a bigger digit in front: drop it
    stack.push(d);
  }
  if (k) stack.splice(stack.length - k, k);   // still digits to drop: the end is the biggest part
  return stack.join("").replace(/^0+/, "") || "0";
}

for (const [num, k] of [["1432219", 3], ["10200", 1], ["10", 2], ["12345", 2]])
  console.log(`${num} remove ${k} -> ${removeKdigits(num, k)}`);
''', java=r'''
public class RemoveKDigits {
    static String removeKdigits(String num, int k) {
        StringBuilder stack = new StringBuilder();
        for (char d : num.toCharArray()) {
            while (k > 0 && stack.length() > 0 && stack.charAt(stack.length() - 1) > d) {   // a bigger digit in front: drop it
                stack.deleteCharAt(stack.length() - 1);
                k--;
            }
            stack.append(d);
        }
        stack.setLength(stack.length() - k);       // still digits to drop: the end is the biggest part
        int i = 0;
        while (i < stack.length() && stack.charAt(i) == '0') i++;
        String out = stack.substring(i);
        return out.isEmpty() ? "0" : out;
    }

    public static void main(String[] args) {
        String[] nums = {"1432219", "10200", "10", "12345"};
        int[] ks = {3, 1, 2, 2};
        for (int i = 0; i < nums.length; i++) System.out.println(nums[i] + " remove " + ks[i] + " -> " + removeKdigits(nums[i], ks[i]));
    }
}
''', ts=r'''
function removeKdigits(num: string, k: number): string {
  const stack: string[] = [];
  for (const d of num) {
    while (k && stack.length && stack[stack.length - 1] > d) { stack.pop(); k--; }   // a bigger digit in front: drop it
    stack.push(d);
  }
  if (k) stack.splice(stack.length - k, k);   // still digits to drop: the end is the biggest part
  return stack.join("").replace(/^0+/, "") || "0";
}

const tests: [string, number][] = [["1432219", 3], ["10200", 1], ["10", 2], ["12345", 2]];
for (const [num, k] of tests) console.log(`${num} remove ${k} -> ${removeKdigits(num, k)}`);
''')

t.code('sjf', py=r'''
def total_wait(durations):
    wait, clock = 0, 0
    for d in durations:
        wait += clock                         # this job waited for everything before it
        clock += d
    return wait


jobs = [6, 2, 8, 3]
print("given order", jobs, "total waiting", total_wait(jobs))
print("shortest first", sorted(jobs), "total waiting", total_wait(sorted(jobs)))
a, b = 6, 2
print(f"swap one pair: {a} before {b} adds {a} to the wait, {b} before {a} adds only {b}")
''', js=r'''
function totalWait(durations) {
  let wait = 0, clock = 0;
  for (const d of durations) { wait += clock; clock += d; }   // this job waited for everything before it
  return wait;
}

const jobs = [6, 2, 8, 3];
const fmt = a => `[${a.join(", ")}]`;
console.log("given order", fmt(jobs), "total waiting", totalWait(jobs));
const sorted = [...jobs].sort((x, y) => x - y);
console.log("shortest first", fmt(sorted), "total waiting", totalWait(sorted));
const a = 6, b = 2;
console.log(`swap one pair: ${a} before ${b} adds ${a} to the wait, ${b} before ${a} adds only ${b}`);
''', java=r'''
import java.util.*;

public class ShortestJobFirst {
    static int totalWait(int[] durations) {
        int wait = 0, clock = 0;
        for (int d : durations) { wait += clock; clock += d; }   // this job waited for everything before it
        return wait;
    }

    public static void main(String[] args) {
        int[] jobs = {6, 2, 8, 3};
        System.out.println("given order " + Arrays.toString(jobs) + " total waiting " + totalWait(jobs));
        int[] sorted = jobs.clone();
        Arrays.sort(sorted);
        System.out.println("shortest first " + Arrays.toString(sorted) + " total waiting " + totalWait(sorted));
        int a = 6, b = 2;
        System.out.println("swap one pair: " + a + " before " + b + " adds " + a + " to the wait, " + b + " before " + a + " adds only " + b);
    }
}
''', ts=r'''
function totalWait(durations: number[]): number {
  let wait = 0, clock = 0;
  for (const d of durations) { wait += clock; clock += d; }   // this job waited for everything before it
  return wait;
}

const jobs = [6, 2, 8, 3];
const fmt = (a: number[]): string => `[${a.join(", ")}]`;
console.log("given order", fmt(jobs), "total waiting", totalWait(jobs));
const sorted = [...jobs].sort((x, y) => x - y);
console.log("shortest first", fmt(sorted), "total waiting", totalWait(sorted));
const a = 6, b = 2;
console.log(`swap one pair: ${a} before ${b} adds ${a} to the wait, ${b} before ${a} adds only ${b}`);
''')

# ---------------------------------------------------------------- LeetCode practice programs
t.code('p_cookies', py=r'''
def find_content_children(g, s):
    g, s = sorted(g), sorted(s)
    child = 0
    for cookie in s:                          # smallest cookies first
        if child < len(g) and cookie >= g[child]:
            child += 1                        # the least greedy child left is happy with it
    return child


print(find_content_children([1, 2, 3], [1, 1]))
print(find_content_children([1, 2], [1, 2, 3]))
''', js=r'''
function findContentChildren(g, s) {
  g = [...g].sort((a, b) => a - b);
  s = [...s].sort((a, b) => a - b);
  let child = 0;
  for (const cookie of s)                     // smallest cookies first
    if (child < g.length && cookie >= g[child]) child++;   // the least greedy child left is happy with it
  return child;
}

console.log(findContentChildren([1, 2, 3], [1, 1]));
console.log(findContentChildren([1, 2], [1, 2, 3]));
''', java=r'''
import java.util.*;

public class AssignCookies {
    static int findContentChildren(int[] g, int[] s) {
        int[] gg = g.clone(), ss = s.clone();
        Arrays.sort(gg);
        Arrays.sort(ss);
        int child = 0;
        for (int cookie : ss)                                 // smallest cookies first
            if (child < gg.length && cookie >= gg[child]) child++;   // the least greedy child left is happy with it
        return child;
    }

    public static void main(String[] args) {
        System.out.println(findContentChildren(new int[]{1, 2, 3}, new int[]{1, 1}));
        System.out.println(findContentChildren(new int[]{1, 2}, new int[]{1, 2, 3}));
    }
}
''', ts=r'''
function findContentChildren(g: number[], s: number[]): number {
  const gg = [...g].sort((a, b) => a - b), ss = [...s].sort((a, b) => a - b);
  let child = 0;
  for (const cookie of ss)                    // smallest cookies first
    if (child < gg.length && cookie >= gg[child]) child++;   // the least greedy child left is happy with it
  return child;
}

console.log(findContentChildren([1, 2, 3], [1, 1]));
console.log(findContentChildren([1, 2], [1, 2, 3]));
''')

t.code('p_lemonade', py=r'''
def lemonade_change(bills):
    fives = tens = 0
    for b in bills:
        if b == 5:
            fives += 1
        elif b == 10:
            if not fives:
                return False
            fives, tens = fives - 1, tens + 1
        elif tens and fives:                  # for 20, give a 10 first: fives are more useful later
            tens, fives = tens - 1, fives - 1
        elif fives >= 3:
            fives -= 3
        else:
            return False
    return True


print("true" if lemonade_change([5, 5, 5, 10, 20]) else "false")
print("true" if lemonade_change([5, 5, 10, 10, 20]) else "false")
''', js=r'''
function lemonadeChange(bills) {
  let fives = 0, tens = 0;
  for (const b of bills) {
    if (b === 5) fives++;
    else if (b === 10) { if (!fives) return false; fives--; tens++; }
    else if (tens && fives) { tens--; fives--; }   // for 20, give a 10 first: fives are more useful later
    else if (fives >= 3) fives -= 3;
    else return false;
  }
  return true;
}

console.log(lemonadeChange([5, 5, 5, 10, 20]));
console.log(lemonadeChange([5, 5, 10, 10, 20]));
''', java=r'''
public class LemonadeChange {
    static boolean lemonadeChange(int[] bills) {
        int fives = 0, tens = 0;
        for (int b : bills) {
            if (b == 5) fives++;
            else if (b == 10) { if (fives == 0) return false; fives--; tens++; }
            else if (tens > 0 && fives > 0) { tens--; fives--; }   // for 20, give a 10 first: fives are more useful later
            else if (fives >= 3) fives -= 3;
            else return false;
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println(lemonadeChange(new int[]{5, 5, 5, 10, 20}));
        System.out.println(lemonadeChange(new int[]{5, 5, 10, 10, 20}));
    }
}
''', ts=r'''
function lemonadeChange(bills: number[]): boolean {
  let fives = 0, tens = 0;
  for (const b of bills) {
    if (b === 5) fives++;
    else if (b === 10) { if (!fives) return false; fives--; tens++; }
    else if (tens && fives) { tens--; fives--; }   // for 20, give a 10 first: fives are more useful later
    else if (fives >= 3) fives -= 3;
    else return false;
  }
  return true;
}

console.log(lemonadeChange([5, 5, 5, 10, 20]));
console.log(lemonadeChange([5, 5, 10, 10, 20]));
''')

t.code('p_jump', py=r'''
def can_jump(nums):
    reach = 0                                 # the farthest index we can get to so far
    for i, n in enumerate(nums):
        if i > reach:
            return False                      # this index is beyond anything we can reach
        reach = max(reach, i + n)
    return True


print("true" if can_jump([2, 3, 1, 1, 4]) else "false")
print("true" if can_jump([3, 2, 1, 0, 4]) else "false")
''', js=r'''
function canJump(nums) {
  let reach = 0;                              // the farthest index we can get to so far
  for (let i = 0; i < nums.length; i++) {
    if (i > reach) return false;              // this index is beyond anything we can reach
    reach = Math.max(reach, i + nums[i]);
  }
  return true;
}

console.log(canJump([2, 3, 1, 1, 4]));
console.log(canJump([3, 2, 1, 0, 4]));
''', java=r'''
public class JumpGame {
    static boolean canJump(int[] nums) {
        int reach = 0;                                 // the farthest index we can get to so far
        for (int i = 0; i < nums.length; i++) {
            if (i > reach) return false;               // this index is beyond anything we can reach
            reach = Math.max(reach, i + nums[i]);
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println(canJump(new int[]{2, 3, 1, 1, 4}));
        System.out.println(canJump(new int[]{3, 2, 1, 0, 4}));
    }
}
''', ts=r'''
function canJump(nums: number[]): boolean {
  let reach = 0;                              // the farthest index we can get to so far
  for (let i = 0; i < nums.length; i++) {
    if (i > reach) return false;              // this index is beyond anything we can reach
    reach = Math.max(reach, i + nums[i]);
  }
  return true;
}

console.log(canJump([2, 3, 1, 1, 4]));
console.log(canJump([3, 2, 1, 0, 4]));
''')

t.code('p_overlap', py=r'''
def erase_overlap_intervals(intervals):
    removed, end = 0, float("-inf")
    for s, e in sorted(intervals, key=lambda x: x[1]):   # keep the interval that ends first
        if s >= end:
            end = e
        else:
            removed += 1                      # it overlaps the last kept one, so drop it
    return removed


print(erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]]))
print(erase_overlap_intervals([[1, 2], [1, 2], [1, 2]]))
print(erase_overlap_intervals([[1, 2], [2, 3]]))
''', js=r'''
function eraseOverlapIntervals(intervals) {
  let removed = 0, end = -Infinity;
  for (const [s, e] of [...intervals].sort((a, b) => a[1] - b[1])) {   // keep the interval that ends first
    if (s >= end) end = e;
    else removed++;                           // it overlaps the last kept one, so drop it
  }
  return removed;
}

console.log(eraseOverlapIntervals([[1, 2], [2, 3], [3, 4], [1, 3]]));
console.log(eraseOverlapIntervals([[1, 2], [1, 2], [1, 2]]));
console.log(eraseOverlapIntervals([[1, 2], [2, 3]]));
''', java=r'''
import java.util.*;

public class NonOverlapping {
    static int eraseOverlapIntervals(int[][] intervals) {
        int[][] iv = intervals.clone();
        Arrays.sort(iv, (a, b) -> Integer.compare(a[1], b[1]));    // keep the interval that ends first
        int removed = 0;
        long end = Long.MIN_VALUE;
        for (int[] x : iv) {
            if (x[0] >= end) end = x[1];
            else removed++;                                       // it overlaps the last kept one, so drop it
        }
        return removed;
    }

    public static void main(String[] args) {
        System.out.println(eraseOverlapIntervals(new int[][]{{1, 2}, {2, 3}, {3, 4}, {1, 3}}));
        System.out.println(eraseOverlapIntervals(new int[][]{{1, 2}, {1, 2}, {1, 2}}));
        System.out.println(eraseOverlapIntervals(new int[][]{{1, 2}, {2, 3}}));
    }
}
''', ts=r'''
function eraseOverlapIntervals(intervals: number[][]): number {
  let removed = 0, end = -Infinity;
  for (const [s, e] of [...intervals].sort((a, b) => a[1] - b[1])) {   // keep the interval that ends first
    if (s >= end) end = e;
    else removed++;                           // it overlaps the last kept one, so drop it
  }
  return removed;
}

console.log(eraseOverlapIntervals([[1, 2], [2, 3], [3, 4], [1, 3]]));
console.log(eraseOverlapIntervals([[1, 2], [1, 2], [1, 2]]));
console.log(eraseOverlapIntervals([[1, 2], [2, 3]]));
''')

t.code('p_gas', py=r'''
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1                             # not enough fuel in total, from anywhere
    start, tank = 0, 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:                          # we cannot reach i + 1 from start, nor from anything in between
            start, tank = i + 1, 0
    return start


print(can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]))
print(can_complete_circuit([2, 3, 4], [3, 4, 3]))
''', js=r'''
function canCompleteCircuit(gas, cost) {
  const sum = a => a.reduce((s, x) => s + x, 0);
  if (sum(gas) < sum(cost)) return -1;        // not enough fuel in total, from anywhere
  let start = 0, tank = 0;
  for (let i = 0; i < gas.length; i++) {
    tank += gas[i] - cost[i];
    if (tank < 0) { start = i + 1; tank = 0; }   // i + 1 cannot be reached from start or anything in between
  }
  return start;
}

console.log(canCompleteCircuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]));
console.log(canCompleteCircuit([2, 3, 4], [3, 4, 3]));
''', java=r'''
public class GasStation {
    static int canCompleteCircuit(int[] gas, int[] cost) {
        int total = 0, start = 0, tank = 0;
        for (int i = 0; i < gas.length; i++) {
            total += gas[i] - cost[i];
            tank += gas[i] - cost[i];
            if (tank < 0) { start = i + 1; tank = 0; }   // i + 1 cannot be reached from start or anything in between
        }
        return total < 0 ? -1 : start;                    // not enough fuel in total, from anywhere
    }

    public static void main(String[] args) {
        System.out.println(canCompleteCircuit(new int[]{1, 2, 3, 4, 5}, new int[]{3, 4, 5, 1, 2}));
        System.out.println(canCompleteCircuit(new int[]{2, 3, 4}, new int[]{3, 4, 3}));
    }
}
''', ts=r'''
function canCompleteCircuit(gas: number[], cost: number[]): number {
  const sum = (a: number[]): number => a.reduce((s, x) => s + x, 0);
  if (sum(gas) < sum(cost)) return -1;        // not enough fuel in total, from anywhere
  let start = 0, tank = 0;
  for (let i = 0; i < gas.length; i++) {
    tank += gas[i] - cost[i];
    if (tank < 0) { start = i + 1; tank = 0; }   // i + 1 cannot be reached from start or anything in between
  }
  return start;
}

console.log(canCompleteCircuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]));
console.log(canCompleteCircuit([2, 3, 4], [3, 4, 3]));
''')

t.code('p_labels', py=r'''
def partition_labels(s):
    last = {ch: i for i, ch in enumerate(s)}  # where each letter appears for the last time
    sizes, start, end = [], 0, 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])              # this part must stretch at least this far
        if i == end:                          # every letter so far ends here: cut
            sizes.append(end - start + 1)
            start = i + 1
    return sizes


print(" ".join(map(str, partition_labels("ababcbacadefegdehijhklij"))))
print(" ".join(map(str, partition_labels("eccbbbbdec"))))
''', js=r'''
function partitionLabels(s) {
  const last = {};
  [...s].forEach((ch, i) => { last[ch] = i; });   // where each letter appears for the last time
  const sizes = [];
  let start = 0, end = 0;
  for (let i = 0; i < s.length; i++) {
    end = Math.max(end, last[s[i]]);          // this part must stretch at least this far
    if (i === end) { sizes.push(end - start + 1); start = i + 1; }   // every letter so far ends here: cut
  }
  return sizes;
}

console.log(partitionLabels("ababcbacadefegdehijhklij").join(" "));
console.log(partitionLabels("eccbbbbdec").join(" "));
''', java=r'''
import java.util.*;

public class PartitionLabels {
    static List<Integer> partitionLabels(String s) {
        int[] last = new int[26];
        for (int i = 0; i < s.length(); i++) last[s.charAt(i) - 'a'] = i;   // where each letter appears for the last time
        List<Integer> sizes = new ArrayList<>();
        int start = 0, end = 0;
        for (int i = 0; i < s.length(); i++) {
            end = Math.max(end, last[s.charAt(i) - 'a']);  // this part must stretch at least this far
            if (i == end) { sizes.add(end - start + 1); start = i + 1; }   // every letter so far ends here: cut
        }
        return sizes;
    }

    static void show(List<Integer> a) {
        StringJoiner sj = new StringJoiner(" ");
        for (int x : a) sj.add(String.valueOf(x));
        System.out.println(sj);
    }

    public static void main(String[] args) {
        show(partitionLabels("ababcbacadefegdehijhklij"));
        show(partitionLabels("eccbbbbdec"));
    }
}
''', ts=r'''
function partitionLabels(s: string): number[] {
  const last: Record<string, number> = {};
  [...s].forEach((ch, i) => { last[ch] = i; });   // where each letter appears for the last time
  const sizes: number[] = [];
  let start = 0, end = 0;
  for (let i = 0; i < s.length; i++) {
    end = Math.max(end, last[s[i]]);          // this part must stretch at least this far
    if (i === end) { sizes.push(end - start + 1); start = i + 1; }   // every letter so far ends here: cut
  }
  return sizes;
}

console.log(partitionLabels("ababcbacadefegdehijhklij").join(" "));
console.log(partitionLabels("eccbbbbdec").join(" "));
''')

t.code('p_candy', py=r'''
def candy(ratings):
    n = len(ratings)
    c = [1] * n                               # everyone gets one to start
    for i in range(1, n):                     # pass 1: beat the left neighbour
        if ratings[i] > ratings[i - 1]:
            c[i] = c[i - 1] + 1
    for i in range(n - 2, -1, -1):            # pass 2: beat the right neighbour too, keeping pass 1
        if ratings[i] > ratings[i + 1]:
            c[i] = max(c[i], c[i + 1] + 1)
    return sum(c)


print(candy([1, 0, 2]))
print(candy([1, 2, 2]))
print(candy([1, 3, 4, 5, 2]))
''', js=r'''
function candy(ratings) {
  const n = ratings.length, c = new Array(n).fill(1);   // everyone gets one to start
  for (let i = 1; i < n; i++) if (ratings[i] > ratings[i - 1]) c[i] = c[i - 1] + 1;   // pass 1: beat the left neighbour
  for (let i = n - 2; i >= 0; i--)            // pass 2: beat the right neighbour too, keeping pass 1
    if (ratings[i] > ratings[i + 1]) c[i] = Math.max(c[i], c[i + 1] + 1);
  return c.reduce((s, x) => s + x, 0);
}

console.log(candy([1, 0, 2]));
console.log(candy([1, 2, 2]));
console.log(candy([1, 3, 4, 5, 2]));
''', java=r'''
import java.util.*;

public class Candy {
    static int candy(int[] ratings) {
        int n = ratings.length;
        int[] c = new int[n];
        Arrays.fill(c, 1);                                     // everyone gets one to start
        for (int i = 1; i < n; i++) if (ratings[i] > ratings[i - 1]) c[i] = c[i - 1] + 1;   // pass 1: beat the left neighbour
        for (int i = n - 2; i >= 0; i--)                       // pass 2: beat the right neighbour too, keeping pass 1
            if (ratings[i] > ratings[i + 1]) c[i] = Math.max(c[i], c[i + 1] + 1);
        int sum = 0;
        for (int x : c) sum += x;
        return sum;
    }

    public static void main(String[] args) {
        System.out.println(candy(new int[]{1, 0, 2}));
        System.out.println(candy(new int[]{1, 2, 2}));
        System.out.println(candy(new int[]{1, 3, 4, 5, 2}));
    }
}
''', ts=r'''
function candy(ratings: number[]): number {
  const n = ratings.length, c: number[] = new Array(n).fill(1);   // everyone gets one to start
  for (let i = 1; i < n; i++) if (ratings[i] > ratings[i - 1]) c[i] = c[i - 1] + 1;   // pass 1: beat the left neighbour
  for (let i = n - 2; i >= 0; i--)            // pass 2: beat the right neighbour too, keeping pass 1
    if (ratings[i] > ratings[i + 1]) c[i] = Math.max(c[i], c[i + 1] + 1);
  return c.reduce((s, x) => s + x, 0);
}

console.log(candy([1, 0, 2]));
console.log(candy([1, 2, 2]));
console.log(candy([1, 3, 4, 5, 2]));
''')

t.code('p_courses3', py=r'''
import heapq


def schedule_course(courses):
    taken, time = [], 0                       # a max heap of the lengths taken, stored as negatives
    for length, last_day in sorted(courses, key=lambda c: c[1]):   # earliest deadline first
        heapq.heappush(taken, -length)
        time += length
        if time > last_day:                   # too late: drop the longest course taken so far
            time += heapq.heappop(taken)
    return len(taken)


print(schedule_course([[100, 200], [200, 1300], [1000, 1250], [2000, 3200]]))
print(schedule_course([[1, 2]]))
print(schedule_course([[3, 2], [4, 3]]))
''', js=JS_HEAP + r'''
function scheduleCourse(courses) {
  const taken = new Heap((a, b) => a > b);    // a max heap of the lengths taken
  let time = 0;
  for (const [length, lastDay] of [...courses].sort((a, b) => a[1] - b[1])) {   // earliest deadline first
    taken.push(length);
    time += length;
    if (time > lastDay) time -= taken.pop();  // too late: drop the longest course taken so far
  }
  return taken.size;
}

console.log(scheduleCourse([[100, 200], [200, 1300], [1000, 1250], [2000, 3200]]));
console.log(scheduleCourse([[1, 2]]));
console.log(scheduleCourse([[3, 2], [4, 3]]));
''', java=r'''
import java.util.*;

public class CourseScheduleIII {
    static int scheduleCourse(int[][] courses) {
        int[][] cs = courses.clone();
        Arrays.sort(cs, (a, b) -> Integer.compare(a[1], b[1]));          // earliest deadline first
        PriorityQueue<Integer> taken = new PriorityQueue<>(Collections.reverseOrder());   // a max heap of lengths taken
        int time = 0;
        for (int[] c : cs) {
            taken.add(c[0]);
            time += c[0];
            if (time > c[1]) time -= taken.poll();                       // too late: drop the longest course so far
        }
        return taken.size();
    }

    public static void main(String[] args) {
        System.out.println(scheduleCourse(new int[][]{{100, 200}, {200, 1300}, {1000, 1250}, {2000, 3200}}));
        System.out.println(scheduleCourse(new int[][]{{1, 2}}));
        System.out.println(scheduleCourse(new int[][]{{3, 2}, {4, 3}}));
    }
}
''', ts=TS_HEAP + r'''
function scheduleCourse(courses: number[][]): number {
  const taken = new Heap<number>((a, b) => a > b);   // a max heap of the lengths taken
  let time = 0;
  for (const [length, lastDay] of [...courses].sort((a, b) => a[1] - b[1])) {   // earliest deadline first
    taken.push(length);
    time += length;
    if (time > lastDay) time -= taken.pop();  // too late: drop the longest course taken so far
  }
  return taken.size;
}

console.log(scheduleCourse([[100, 200], [200, 1300], [1000, 1250], [2000, 3200]]));
console.log(scheduleCourse([[1, 2]]));
console.log(scheduleCourse([[3, 2], [4, 3]]));
''')

t.leet(455, 'e', 'p_cookies', title='Assign Cookies', url='https://leetcode.com/problems/assign-cookies/', diff='Easy',
       statement='<p>Child i is happy with a cookie of size at least g[i]. Each child gets at most one cookie. Return the largest number of happy children.</p>',
       example='g [1,2,3], s [1,1]  →  1\ng [1,2], s [1,2,3]  →  2',
       hint='Give the smallest cookie that works to the least greedy child.',
       approach='<p>Sort both lists. Walk through the cookies from small to large, and give each one to the least greedy child still waiting if it is big enough. A cookie too small for that child is too small for everyone after, so it is skipped. Wasting a big cookie on an easy child can never help.</p>',
       time='O(n log n)', space='O(n) for the sorted copies')
t.leet(860, 'e', 'p_lemonade', title='Lemonade Change', url='https://leetcode.com/problems/lemonade-change/', diff='Easy',
       statement='<p>Lemonade costs 5. Customers pay with 5, 10 or 20 in the given order. You start with no money. Return true if you can give everyone correct change.</p>',
       example='[5,5,5,10,20]   →  true\n[5,5,10,10,20]  →  false',
       hint='When a 20 arrives, which change keeps you safest for later?',
       approach='<p>Count fives and tens. A 10 needs one 5 back. A 20 needs 15 back: give a 10 and a 5 when you can, and only otherwise three 5s. Fives can pay for both kinds of change, so saving them is always at least as good. Twenties are never given as change, so they are not counted.</p>',
       time='O(n)', space='O(1)')
t.leet(55, 'm', 'p_jump',
       statement='<p>nums[i] is the longest jump allowed from index i. Starting at index 0, decide whether you can reach the last index.</p>',
       example='[2,3,1,1,4]  →  true\n[3,2,1,0,4]  →  false',
       hint='Keep the farthest index you can reach so far.',
       approach='<p>Walk from left to right, keeping the farthest reachable index. If the current index is beyond it, you are stuck and the answer is false. Otherwise stretch the reach to i + nums[i]. There is no need to choose which jump to take: knowing how far you could get is enough.</p>',
       time='O(n)', space='O(1)')
t.leet(435, 'm', 'p_overlap',
       statement='<p>Return the smallest number of intervals to remove so that the rest do not overlap. Intervals that only touch at an end do not overlap.</p>',
       example='[[1,2],[2,3],[3,4],[1,3]]  →  1\n[[1,2],[1,2],[1,2]]        →  2\n[[1,2],[2,3]]              →  0',
       hint='Removing the fewest is the same as keeping the most.',
       approach='<p>This is activity selection in disguise. Sort by end, keep each interval that starts at or after the end of the last kept one, and count the rest as removed. Keeping the interval that ends first leaves the most room, which is the same exchange argument as in the lesson.</p>',
       time='O(n log n)', space='O(n) for the sorted copy')
t.leet(134, 'h', 'p_gas',
       statement='<p>Stations on a circle have gas[i] fuel, and driving to the next one costs cost[i]. Return the station to start from to drive all the way round, or −1. The answer is unique if it exists.</p>',
       example='gas [1,2,3,4,5], cost [3,4,5,1,2]  →  3\ngas [2,3,4], cost [3,4,3]          →  −1',
       hint='If the tank goes negative on the way to i + 1, no station between the start and i can be the answer.',
       approach='<p>If the total gas is less than the total cost, no start works. Otherwise drive once round, adding gas minus cost to a tank. When the tank drops below zero before station i + 1, every start from the current one up to i would also fail, since each of them arrives with even less fuel. So jump the start to i + 1 and empty the tank. One pass is enough.</p>',
       time='O(n)', space='O(1)')
t.leet(763, 'h', 'p_labels', title='Partition Labels', url='https://leetcode.com/problems/partition-labels/', diff='Medium',
       statement='<p>Split a string into as many parts as possible so that each letter appears in at most one part. Return the sizes of the parts.</p>',
       example='"ababcbacadefegdehijhklij"  →  9 7 8\n"eccbbbbdec"                →  10',
       hint='First record where each letter appears for the last time.',
       approach='<p>Store the last index of every letter. Walk through the string, stretching the end of the current part to the last index of each letter you meet. When the walk reaches that end, every letter seen so far is finished, so cut there. Cutting as early as possible gives the most parts.</p>',
       time='O(n)', space='O(1), at most 26 letters')
t.leet(135, 'x', 'p_candy', title='Candy', url='https://leetcode.com/problems/candy/', diff='Hard',
       statement='<p>Children stand in a line with ratings. Each child gets at least one candy, and a child with a higher rating than a neighbour gets more than that neighbour. Return the fewest candies in total.</p>',
       example='[1,0,2]      →  5\n[1,2,2]      →  4\n[1,3,4,5,2]  →  11',
       hint='Handle left neighbours in one pass and right neighbours in another.',
       approach='<p>Give everyone 1. Sweep left to right: a child rated higher than the left neighbour gets one more than that neighbour. Sweep right to left: a child rated higher than the right neighbour needs one more than that neighbour, so take the maximum with what pass 1 gave. Each pass only raises a count when a rule forces it, so the total stays as small as possible.</p>',
       time='O(n)', space='O(n)')
t.leet(630, 'x', 'p_courses3',
       statement='<p>Each course has a length and a last day by which it must be finished. You take one course at a time, starting on day 1. Return the most courses you can take.</p>',
       example='[[100,200],[200,1300],[1000,1250],[2000,3200]]  →  3\n[[1,2]]                                         →  1\n[[3,2],[4,3]]                                   →  0',
       hint='Go by deadline. When you run out of time, which course should you give up?',
       approach='<p>Sort courses by last day and take each one in turn, keeping the lengths in a max heap. If the total time passes the current deadline, drop the longest course taken so far. Dropping the longest frees the most time while losing only one course, so the count never gets worse. Python stores negative lengths in <code>heapq</code>, and JavaScript and TypeScript use the small heap class.</p>',
       time='O(n log n)', space='O(n)')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='greedy-choice', emoji='🪙', title='The greedy choice, and when it fails', html='''
<p>A <b>greedy</b> algorithm builds an answer one step at a time, and at every step takes whatever looks best right now. It never goes back to change an earlier choice. That makes greedy code short and fast. The hard part is knowing whether the best choice right now leads to the best answer overall.</p>
<div class="viz" data-viz="pk" data-pk="coins"></div>
<div class="c3" data-k="coins" data-label="Greedy coins against the true fewest coins"></div>
<div class="rule">A greedy algorithm is correct when the problem has the <b>greedy choice property</b>, so some best answer starts with the greedy choice, and <b>optimal substructure</b>, so the rest of a best answer is a best answer to what is left.</div>
<div class="warn">With coins 1, 5, 10 and 25, greedy is always right. With coins 1, 3 and 4, making 6 greedily gives 4 + 1 + 1, but 3 + 3 is better. When greedy fails, dynamic programming is usually the fix.</div>
'''),
    dict(id='intervals', emoji='📅', title='Interval scheduling: finish first', html='''
<p>You have a list of activities with start and end times and one room. What is the largest number that fit without overlapping? The winning rule is simple: <b>sort by end time</b> and keep every activity that starts after the last kept one ends. Try the other rules in the animation and watch them lose.</p>
<div class="viz" data-viz="pk" data-pk="activity"></div>
<div class="c3" data-k="activity" data-label="Activity selection by earliest finish"></div>
<div class="exam">Why it works: take any best schedule. Swap its first activity for the one that finishes earliest. Nothing breaks, because the new one ends even sooner, and the count stays the same. Repeat for the rest.</div>
'''),
    dict(id='fractional-knapsack', emoji='🎒', title='The fractional knapsack', html='''
<p>A bag holds a limited weight, and each item has a value and a weight. If items can be split, like gold dust, the greedy rule is to sort by <b>value per kilo</b> and take the best first, splitting the last item if needed. If items must be taken whole, the same rule can fail badly.</p>
<div class="viz" data-viz="pk" data-pk="fractional"></div>
<div class="c3" data-k="fractional" data-label="Fractional knapsack by value per kilo"></div>
<div class="tw"><table class="jt"><tr><th>Bag of 50 kg</th><th>Greedy by value per kg</th><th>Best possible</th></tr>
<tr><td>Items can be split</td><td class="yes">240</td><td>240</td></tr>
<tr><td>Items must be whole</td><td>160</td><td class="yes">220</td></tr></table></div>
<div class="tip">The whole items version, the 0/1 knapsack, is solved in the Dynamic Programming chapters.</div>
'''),
    dict(id='huffman', emoji='🌳', title='Huffman codes', html='''
<p>To store text in fewer bits, give common letters short codes and rare letters long ones. No code may be the start of another, so the text can be read back without gaps. <b>Huffman's algorithm</b> builds the best such code with a greedy rule: keep joining the two rarest trees until one tree is left. Left edges add a 0 and right edges add a 1.</p>
<div class="viz" data-viz="pk" data-pk="huffman"></div>
<div class="c3" data-k="huffman" data-label="Huffman codes with a min heap"></div>
<div class="exam">For counts a 5, b 9, c 12, d 13, e 16 and f 45, Huffman needs 224 bits where fixed 3 bit codes need 300. The DEFLATE format inside ZIP, gzip and PNG files uses Huffman codes.</div>
'''),
    dict(id='remove-digits', emoji='✂️', title='Greedy with a stack: remove k digits', html='''
<p>Remove k digits from a number to make it as small as possible. The leftmost digits matter most, so walk from the left. Whenever the digit you just kept is <b>bigger than the next one</b>, removing it makes the number smaller. A stack keeps the digits chosen so far and makes popping easy.</p>
<div class="viz" data-viz="pk" data-pk="digits"></div>
<div class="c3" data-k="digits" data-label="Remove k digits with a stack"></div>
<div class="rule">If digits are still left to remove at the end, the kept digits rise from left to right, so drop them from the end. Then strip leading zeros, and return "0" if nothing is left.</div>
'''),
    dict(id='exchange-argument', emoji='🔁', title='Proving greedy right: the exchange argument', html='''
<p>One server must run several jobs, one after another. Every job waits for all jobs before it. To make the total waiting as small as possible, run the <b>shortest job first</b>. The proof is an exchange argument: if a longer job runs right before a shorter one, swapping them lowers the total wait, so the best order has no such pair.</p>
<div class="viz" data-viz="pk" data-pk="sjf"></div>
<div class="c3" data-k="sjf" data-label="Total waiting time in two orders"></div>
<span class="eq">a before b adds a to the wait &nbsp;&nbsp; b before a adds b &nbsp;&nbsp; so put the smaller first</span>
<div class="tip">Dijkstra's shortest paths, Prim's and Kruskal's spanning trees and Huffman codes are all greedy algorithms with proofs like this one.</div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem is solved in the Practice section in Python, JavaScript, Java and TypeScript, with line by line replay. For each one, look for the rule that is always safe to apply first.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>The greedy rule</th></tr>
<tr><td><a href="#lc455">455. Assign Cookies</a></td><td>Easy</td><td>smallest cookie that works</td></tr>
<tr><td><a href="#lc860">860. Lemonade Change</a></td><td>Easy</td><td>give a 10 before three 5s</td></tr>
<tr><td><a href="#lc55">55. Jump Game</a></td><td>Medium</td><td>track the farthest reach</td></tr>
<tr><td><a href="#lc435">435. Non-overlapping Intervals</a></td><td>Medium</td><td>keep the earliest finish</td></tr>
<tr><td><a href="#lc134">134. Gas Station</a></td><td>Hard</td><td>restart after the tank runs dry</td></tr>
<tr><td><a href="#lc763">763. Partition Labels</a></td><td>Hard</td><td>cut as early as possible</td></tr>
<tr><td><a href="#lc135">135. Candy</a></td><td>Expert</td><td>one pass each way</td></tr>
<tr><td><a href="#lc630">630. Course Schedule III</a></td><td>Expert</td><td>drop the longest course</td></tr></table></div>
'''),
]

VIZ_JS = r'''
(() => {
  const D = PK.defs;
  const ints = (s, lo, hi, max) => { const a = PK.parseList(s); return a && a.length >= lo && a.length <= hi && a.every(x => Number.isInteger(x) && x >= 1 && x <= max) ? a : null; };

  /* ---------- greedy coins ---------- */
  const fewest = (amount, coins) => {          /* the true answer, used to judge the greedy result */
    const best = [0], from = [0];
    for (let a = 1; a <= amount; a++) {
      best[a] = Infinity;
      for (const c of coins) if (c <= a && best[a - c] + 1 < best[a]) { best[a] = best[a - c] + 1; from[a] = c; }
    }
    if (best[amount] === Infinity) return null;
    const used = [];
    for (let a = amount; a > 0; a -= from[a]) used.push(from[a]);
    return used.sort((x, y) => y - x);
  };
  D.coins = el => PK.widget(el, {
    title: 'Grab the biggest coin', sub: 'Greedy always takes the biggest coin that still fits. Sometimes that is perfect, sometimes not.',
    inputs: [{ k: 'coins', label: 'Coins', type: 'text', val: '1, 3, 4', w: 150 }, { k: 'amount', label: 'Amount', type: 'num', val: 6, min: 1, max: 99, w: 80 }],
    random: () => [{ coins: '1, 5, 10, 25', amount: 30 + Math.floor(Math.random() * 60) }, { coins: '1, 10, 25', amount: 30 }, { coins: '1, 3, 4', amount: 6 }, { coins: '1, 7, 10', amount: 14 }][Math.floor(Math.random() * 4)],
    check: v => { const c = ints(v.coins, 1, 6, 50); return c && c.includes(1) && Number.isInteger(v.amount) && v.amount >= 1 && v.amount <= 99 ? '' : 'Give one to six coin values up to 50, including 1, and an amount from 1 to 99.'; },
    frames: ({ coins, amount }) => {
      const cs = [...new Set(ints(coins, 1, 6, 50))].sort((a, b) => b - a), F = [], used = [];
      let left = amount;
      const pic = (cur, cls = '') => [{ t: 'row', label: 'Coins, biggest first', cells: cs.map(c => '🪙' + c), cls: cur >= 0 ? { [cur]: cls } : {}, idx: false },
        { t: 'row', label: 'In the hand', cells: used.slice(), idx: false, cls: used.length ? { [used.length - 1]: 'yes' } : {} }];
      F.push({ mood: 'think', msg: `Make ${amount} with as few coins as possible. Greedy rule: take the biggest coin that still fits.`, vars: { left, coins: 0 }, layers: pic(-1) });
      cs.forEach((c, i) => {
        if (c > left) { F.push({ mood: 'look', msg: `${c} is bigger than the ${left} still needed. Skip it.`, vars: { left, coins: used.length }, layers: pic(i, 'no') }); return; }
        while (left >= c) {
          left -= c;
          used.push(c);
          F.push({ mood: 'work', msg: `Take ${c}. ${left} still needed.`, vars: { left, coins: used.length }, layers: pic(i, 'look') });
        }
      });
      const best = fewest(amount, cs);
      if (best.length === used.length) F.push({ mood: 'wow', fx: 'rain', msg: `Greedy used <b>${used.length}</b> coins, and that is the fewest possible. With these coins the greedy choice is safe.`, vars: { coins: used.length }, layers: pic(-1) });
      else F.push({ mood: 'sad', fx: 'shake', msg: `Greedy used ${used.length} coins, but <b>${best.join(' + ')}</b> needs only ${best.length}. Grabbing the biggest coin first was a trap here.`, vars: { greedy: used.length, best: best.length }, layers: pic(-1).concat([{ t: 'row', label: 'The fewest coins', cells: best, idx: false, cls: Object.fromEntries(best.map((_, i) => [i, 'win'])) }]) });
      return F;
    }
  });

  /* ---------- activity selection ---------- */
  const ACTS = [['yoga', 1, 4], ['chess', 3, 5], ['swim', 0, 6], ['art', 5, 7], ['code', 3, 9], ['piano', 5, 9], ['run', 6, 10], ['film', 8, 11], ['quiz', 8, 12], ['dance', 2, 14], ['tea', 12, 16]];
  const RULES = { end: ['earliest finish', a => a[2]], start: ['earliest start', a => a[1]], short: ['shortest first', a => a[2] - a[1]] };
  D.activity = el => PK.widget(el, {
    title: 'Fit the most activities', sub: 'Go through the activities in some order and keep each one that does not clash. The order is everything.',
    inputs: [{ k: 'rule', label: 'Order by', type: 'seg', val: 'end', opts: [['end', '🏁 Earliest finish'], ['start', '🚦 Earliest start'], ['short', '⏱️ Shortest']] }],
    frames: ({ rule }) => {
      const [rname, key] = RULES[rule], F = [], T = 16;
      const order = ACTS.map((a, i) => [a, i]).sort((x, y) => key(x[0]) - key(y[0]) || x[1] - y[1]).map(x => x[0]);
      const state = {}, chosen = [];
      const pic = cur => {
        const rows = ACTS.map(a => Array.from({ length: T }, (_, t) => (t >= a[1] && t < a[2] ? (t === a[1] ? a[0] : '') : null)));
        const cls = {};
        ACTS.forEach((a, r) => { for (let t = a[1]; t < a[2]; t++) cls[r + ',' + t] = a[0] === cur ? 'look' : state[a[0]] || 'sel'; });
        return [{ t: 'grid', label: 'Hours 0 to 15', rows, rlab: ACTS.map(a => a[0]), clab: Array.from({ length: T }, (_, t) => t), cls }];
      };
      F.push({ mood: 'think', msg: `${ACTS.length} activities. Try the rule: <b>${rname}</b>.`, vars: { kept: 0 }, layers: pic() });
      for (const a of order) {
        const clash = chosen.find(b => a[1] < b[2] && b[1] < a[2]);
        if (clash) {
          state[a[0]] = 'done';
          F.push({ mood: 'look', msg: `${a[0]} (${a[1]} to ${a[2]}) clashes with ${clash[0]}. Skip it.`, vars: { kept: chosen.length }, layers: pic(a[0]) });
        } else {
          state[a[0]] = 'yes';
          chosen.push(a);
          F.push({ mood: 'happy', msg: `${a[0]} (${a[1]} to ${a[2]}) fits. Keep it.`, vars: { kept: chosen.length }, layers: pic(a[0]) });
        }
      }
      const best = 4;
      F.push(chosen.length === best && rule === 'end'
        ? { mood: 'wow', fx: 'rain', msg: `<b>${chosen.length}</b> activities: ${chosen.map(a => a[0]).join(', ')}. That is the most possible. Finishing early always leaves the most room for the rest.`, vars: { kept: chosen.length }, layers: pic() }
        : chosen.length === best
        ? { mood: 'happy', msg: `${chosen.length} activities, the most possible, so "${rname}" got lucky here. It is not safe in general: one short activity can sit across two longer ones that would both fit. Only earliest finish is always right.`, vars: { kept: chosen.length }, layers: pic() }
        : { mood: 'sad', fx: 'shake', msg: `Only ${chosen.length} activit${chosen.length === 1 ? 'y' : 'ies'} with "${rname}", but 4 are possible. Try earliest finish.`, vars: { kept: chosen.length, best }, layers: pic() });
      return F;
    }
  });

  /* ---------- fractional knapsack ---------- */
  const ITEMS = [['🥇', 'gold', 60, 10], ['🥈', 'silver', 100, 20], ['🥉', 'bronze', 120, 30]];
  D.fractional = el => PK.widget(el, {
    title: 'Fill the bag by value per kilo', sub: 'Each square of the bag holds 5 kg. Dust can be split, bars cannot.',
    inputs: [{ k: 'cap', label: 'Bag holds (kg)', type: 'num', val: 50, min: 5, max: 60, w: 80 },
             { k: 'mode', label: 'Items are', type: 'seg', val: 'dust', opts: [['dust', '✨ Dust, can be split'], ['bars', '🧱 Bars, all or nothing']] }],
    random: () => ({ cap: 5 * (1 + Math.floor(Math.random() * 12)), mode: Math.random() < 0.5 ? 'dust' : 'bars' }),
    check: v => Number.isInteger(v.cap) && v.cap >= 5 && v.cap <= 60 && v.cap % 5 === 0 ? '' : 'Pick a size from 5 to 60 kg in steps of 5.',
    frames: ({ cap, mode }) => {
      const F = [], bag = [], split = mode === 'dust';
      let left = cap, value = 0;
      const order = ITEMS.slice().sort((a, b) => b[2] / b[3] - a[2] / a[3]);
      const pic = (cur, cls = 'look') => [
        { t: 'row', label: 'Items, best value per kg first', cells: order.map(it => `${it[0]} ${it[3]} kg`), tag: Object.fromEntries(order.map((it, i) => [i, `${it[2] / it[3]} per kg`])), cls: cur >= 0 ? { [cur]: cls } : {}, idx: false },
        { t: 'row', label: `The bag, ${cap} kg`, cells: Array.from({ length: cap / 5 }, (_, i) => bag[i] || ''), cls: Object.fromEntries(bag.map((_, i) => [i, 'yes'])), idx: false, small: true }];
      F.push({ mood: 'think', msg: `Greedy rule: take the item with the best value per kilo first. ${split ? 'Dust can be split.' : 'Bars cannot be split.'}`, vars: { value: 0, 'kg left': left }, layers: pic(-1) });
      order.forEach((it, i) => {
        if (!left) return;
        if (!split && it[3] > left) { F.push({ mood: 'sad', msg: `${it[1]} weighs ${it[3]} kg but only ${left} kg is left, and a bar cannot be cut. Skip it.`, vars: { value, 'kg left': left }, layers: pic(i, 'no') }); return; }
        const take = Math.min(it[3], left), worth = it[2] * take / it[3];
        for (let k = 0; k < take / 5; k++) bag.push(it[0]);
        left -= take;
        value += worth;
        F.push({ mood: 'work', msg: `Take ${take} of ${it[3]} kg of ${it[1]}, worth ${worth}.`, vars: { value, 'kg left': left }, layers: pic(i) });
      });
      if (split) F.push({ mood: 'wow', fx: 'rain', msg: `Total value <b>${value}</b>. When items can be split, this greedy rule is always the best possible.`, vars: { value }, layers: pic(-1) });
      else {
        let best = 0;
        for (let m = 0; m < 8; m++) { let w = 0, v = 0; ITEMS.forEach((it, i) => { if (m >> i & 1) { w += it[3]; v += it[2]; } }); if (w <= cap) best = Math.max(best, v); }
        F.push(best === value
          ? { mood: 'happy', msg: `Total value ${value}, which happens to be the best for a ${cap} kg bag.`, vars: { value, best }, layers: pic(-1) }
          : { mood: 'sad', fx: 'shake', msg: `Greedy got ${value}, but the best whole bars are worth <b>${best}</b>. For all or nothing items, greedy fails. That problem needs dynamic programming.`, vars: { value, best }, layers: pic(-1) });
      }
      return F;
    }
  });

  /* ---------- Huffman codes ---------- */
  D.huffman = el => PK.widget(el, {
    title: 'Build a Huffman tree', sub: 'Always join the two rarest trees. Rare letters sink deep and get long codes, common ones stay short.',
    inputs: [{ k: 'freq', label: 'letter:count', type: 'text', val: 'a:5, b:9, c:12, d:13, e:16, f:45', w: 260 }],
    random: () => { const L = 'abcdefg'.slice(0, 4 + Math.floor(Math.random() * 4)); return { freq: [...L].map(c => `${c}:${1 + Math.floor(Math.random() * 40)}`).join(', ') }; },
    check: v => { const p = String(v.freq).split(',').map(x => x.trim().split(':')); return p.length >= 2 && p.length <= 8 && p.every(q => q.length === 2 && /^[a-z]$/.test(q[0]) && /^\d+$/.test(q[1]) && +q[1] >= 1 && +q[1] <= 99) && new Set(p.map(q => q[0])).size === p.length ? '' : 'Write two to eight pairs like a:5, with different lowercase letters and counts from 1 to 99.'; },
    frames: ({ freq }) => {
      const pairs = String(freq).split(',').map(x => x.trim().split(':')).map(([c, n]) => [c, +n]).sort((a, b) => (a[0] < b[0] ? -1 : 1));
      const F = [];
      let uid = 0;
      let q = pairs.map(([c, n]) => ({ f: n, id: uid++, ch: c }));
      const sortQ = () => q.sort((a, b) => a.f - b.f || a.id - b.id);
      const label = t => (t.ch ? `${t.ch}:${t.f}` : String(t.f));
      const treePic = (root, title, codes) => {
        const kids = {}, ncls = {}, tag = {};
        const walk = t => { kids['t' + t.id] = t.l ? ['t' + t.l.id, 't' + t.r.id] : [null, null]; if (t.ch) { ncls['t' + t.id] = 'yes'; if (codes) tag['t' + t.id] = codes[t.ch]; } if (t.l) { walk(t.l); walk(t.r); } };
        walk(root);
        let depth = 0;
        const dd = (t, d) => { depth = Math.max(depth, d); if (t.l) { dd(t.l, d + 1); dd(t.r, d + 1); } };
        dd(root, 1);
        const H = 54 * depth + 26, L = PK.treeLayout(kids, 't' + root.id, id => { const find = t => (('t' + t.id) === id ? t : t.l && (find(t.l) || find(t.r))); return label(find(root)); }, 460, H);
        return { t: 'graph', label: title, w: 460, h: H, r: 20, nodes: L.nodes, edges: L.edges.map(([a, b]) => [a, b, kids[a][0] === b ? '0' : '1']), ncls, tag };
      };
      sortQ();
      F.push({ mood: 'think', msg: 'Every letter starts as a tiny tree of its own. The queue keeps them ordered by count.', layers: [{ t: 'row', label: 'Queue, rarest first', cells: q.map(label), idx: false }] });
      while (q.length > 1) {
        F.push({ mood: 'look', msg: `The two rarest are ${label(q[0])} and ${label(q[1])}.`, layers: [{ t: 'row', label: 'Queue, rarest first', cells: q.map(label), idx: false, cls: { 0: 'look', 1: 'look' } }] });
        const a = q.shift(), b = q.shift(), m = { f: a.f + b.f, id: uid++, l: a, r: b };
        q.push(m);
        sortQ();
        F.push({ mood: 'work', msg: `Join them under a new node worth ${a.f} + ${b.f} = <b>${m.f}</b>, and put it back in the queue.`, layers: [{ t: 'row', label: 'Queue, rarest first', cells: q.map(label), idx: false, cls: { [q.indexOf(m)]: 'yes' } }, treePic(m, 'The tree just made')] });
      }
      const root = q[0], codes = {};
      const walk = (t, c) => { if (t.ch) codes[t.ch] = c || '0'; else { walk(t.l, c + '0'); walk(t.r, c + '1'); } };
      walk(root, '');
      const bits = pairs.reduce((s, [c, n]) => s + n * codes[c].length, 0), total = pairs.reduce((s, p) => s + p[1], 0);
      const fixed = Math.max(1, Math.ceil(Math.log2(pairs.length)));
      F.push({ mood: 'wow', fx: 'rain', msg: `Codes: ${pairs.map(([c]) => `${c} = ${codes[c]}`).join(', ')}. That is <b>${bits}</b> bits in total, against ${fixed * total} with fixed ${fixed} bit codes.`, vars: { bits, fixed: fixed * total }, layers: [treePic(root, 'Left is 0, right is 1', codes)] });
      return F;
    }
  });

  /* ---------- remove k digits ---------- */
  D.digits = el => PK.widget(el, {
    title: 'Remove k digits, keep the smallest', sub: 'A digit bigger than the one after it should go. A stack remembers what we kept.',
    inputs: [{ k: 'num', label: 'Number', type: 'text', val: '1432219', w: 140 }, { k: 'k', label: 'Remove', type: 'num', val: 3, min: 0, max: 9, w: 70 }],
    random: () => { const n = Array.from({ length: 7 }, () => Math.floor(Math.random() * 10)).join(''); return { num: n, k: 1 + Math.floor(Math.random() * 4) }; },
    check: v => /^\d{1,10}$/.test(String(v.num)) && Number.isInteger(v.k) && v.k >= 0 && v.k <= String(v.num).length ? '' : 'Give up to ten digits, and remove at most that many.',
    frames: ({ num, k }) => {
      const ds = [...String(num)], F = [], stack = [];
      let left = k;
      const pic = (i, scls = {}) => [{ t: 'row', label: 'The number', cells: ds, cls: Object.fromEntries(ds.map((_, j) => [j, j < i ? 'done' : j === i ? 'look' : ''])), idx: false },
        { t: 'stack', label: 'Kept so far', items: stack.slice(), cls: scls }];
      F.push({ mood: 'think', msg: `Remove ${k} digit${k === 1 ? '' : 's'} from ${num} to make the smallest number. The first digits matter most.`, vars: { 'still to remove': left }, layers: pic(-1) });
      ds.forEach((d, i) => {
        while (left && stack.length && stack[stack.length - 1] > d) {
          const top = stack[stack.length - 1];
          F.push({ mood: 'wow', msg: `${top} is bigger than the next digit ${d}. Removing ${top} makes the number smaller.`, vars: { 'still to remove': left }, layers: pic(i, { [stack.length - 1]: 'no' }) });
          stack.pop();
          left--;
        }
        stack.push(d);
        F.push({ mood: 'work', msg: `Keep ${d}.`, vars: { 'still to remove': left }, layers: pic(i, { [stack.length - 1]: 'yes' }) });
      });
      if (left) {
        F.push({ mood: 'look', msg: `The digits now rise from left to right, so the last ${left} are the biggest. Drop them from the end.`, vars: { 'still to remove': left }, layers: pic(ds.length, Object.fromEntries(stack.map((_, j) => [j, j >= stack.length - left ? 'no' : '']))) });
        stack.splice(stack.length - left, left);
      }
      const out = stack.join('').replace(/^0+/, '') || '0';
      F.push({ mood: 'wow', fx: 'rain', msg: `The smallest result is <b>${out}</b>.${out !== stack.join('') && stack.length ? ' Leading zeros are dropped.' : ''}`, layers: pic(ds.length) });
      return F;
    }
  });

  /* ---------- shortest job first ---------- */
  D.sjf = el => PK.widget(el, {
    title: 'Shortest job first', sub: 'Every job waits for all the jobs before it. Put short jobs first and fewer people wait for long ones.',
    inputs: [{ k: 'jobs', label: 'Job lengths', type: 'text', val: '6, 2, 8, 3', w: 160 }, { k: 'order', label: 'Order', type: 'seg', val: 'given', opts: [['given', '📋 As given'], ['short', '⚡ Shortest first']] }],
    random: () => ({ jobs: Array.from({ length: 4 + Math.floor(Math.random() * 3) }, () => 1 + Math.floor(Math.random() * 9)).join(', '), order: 'given' }),
    check: v => ints(v.jobs, 2, 7, 20) ? '' : 'Give two to seven job lengths from 1 to 20.',
    frames: ({ jobs, order }) => {
      const given = ints(jobs, 2, 7, 20), js = order === 'short' ? given.slice().sort((a, b) => a - b) : given.slice(), F = [];
      const waits = [];
      let clock = 0;
      const pic = (cur) => [{ t: 'bars', label: 'Job lengths in running order', vals: js, cls: Object.fromEntries(js.map((_, i) => [i, i < waits.length ? 'yes' : i === cur ? 'look' : ''])) },
        { t: 'row', label: 'How long each job waited', cells: js.map((_, i) => (i < waits.length ? waits[i] : '')), idx: false }];
      F.push({ mood: 'think', msg: order === 'short' ? 'Sort the jobs, shortest first.' : 'Run the jobs in the order given.', vars: { 'total wait': 0 }, layers: pic(-1) });
      js.forEach((d, i) => {
        waits.push(clock);
        F.push({ mood: 'work', msg: `Job ${d} starts at time ${clock}, so it waited ${clock}.`, vars: { 'total wait': waits.reduce((s, x) => s + x, 0) }, layers: pic(i) });
        clock += d;
      });
      const total = waits.reduce((s, x) => s + x, 0);
      let best = 0, c = 0;
      for (const d of given.slice().sort((a, b) => a - b)) { best += c; c += d; }
      F.push(total === best
        ? { mood: 'wow', fx: 'rain', msg: `Total waiting <b>${total}</b>, the smallest possible. Swapping any long job ahead of a shorter one would only add waiting.`, vars: { 'total wait': total }, layers: pic(-1) }
        : { mood: 'sad', fx: 'shake', msg: `Total waiting ${total}. Shortest first would make it only <b>${best}</b>. Try the other order.`, vars: { 'total wait': total, best }, layers: pic(-1) });
      return F;
    }
  });
})();
'''

INFO = {
    'title': 'Take the best step now, never look back',
    'panels': [
        {'s': [['e', '🪙'], ['t', 'best right now', {'b': 1}]], 'h': 'Greedy choice', 't': 'One step, no regrets.', 'more': 'Correct only when a proof says so.'},
        {'s': [['e', '📅'], ['t', 'sort by end', {'b': 1}]], 'h': 'Intervals', 't': 'Finish first, fit the most.', 'more': 'Exchange argument.'},
        {'s': [['e', '🎒'], ['t', 'value ÷ weight', {'b': 1}]], 'h': 'Fractional knapsack', 't': 'Best per kilo first.', 'more': 'Fails for whole items.'},
        {'s': [['e', '🌳'], ['t', 'join the two rarest', {'b': 1}]], 'h': 'Huffman', 't': 'Short codes for common letters.', 'more': 'Used inside ZIP and PNG.'},
    ],
    'remember': 'Greedy is fast and simple, but it is only right when an exchange argument or a similar proof shows the greedy choice is always safe. If a small example breaks it, switch to dynamic programming.',
}

REAL = [
    ['🗜️', 'ZIP files and PNG images', 'The DEFLATE format inside them packs data with Huffman codes, so common symbols take fewer bits.'],
    ['🖨️', 'Print queues and servers', 'Running short jobs first lowers the average waiting time, which is why many schedulers favour short tasks.'],
    ['🏟️', 'Booking one hall for many events', 'An organiser who always picks the event that ends first fits the most events into the day.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to greedy algorithms. A greedy algorithm takes the best looking step right now and never changes its mind. You will see when that works and when it fails with coins, fit the most activities into a day, fill a bag with gold dust, build Huffman codes, shrink a number with a stack, and prove a greedy rule with an exchange argument.'},
    {'id': 'greedy-choice', 'h': 'The greedy choice', 'en': 'A greedy algorithm makes the choice that looks best at each step and never goes back. With everyday coins like one, five, ten and twenty five, taking the biggest coin first always gives the fewest coins. With coins one, three and four, making six greedily takes three coins, but three plus three takes only two. Greedy needs a proof before you trust it.'},
    {'id': 'intervals', 'h': 'Interval scheduling', 'en': 'To fit the most activities into one room, sort them by end time and keep each one that starts after the last kept activity ends. Finishing early leaves the most room for everything after. Rules like earliest start or shortest first can lose, and the animation lets you try them.'},
    {'id': 'fractional-knapsack', 'h': 'Fractional knapsack', 'en': 'When items can be split, sort them by value per kilo and take the best first, cutting the last item to fill the bag exactly. That greedy rule is always optimal. When items must be taken whole, the same rule can miss the best answer, and dynamic programming is needed instead.'},
    {'id': 'huffman', 'h': 'Huffman codes', 'en': 'Huffman coding gives short codes to common letters and long codes to rare ones. Put every letter in a queue by count. Join the two rarest into a new tree whose count is their sum, and repeat until one tree is left. Going left adds a zero and going right adds a one.'},
    {'id': 'remove-digits', 'h': 'Remove k digits', 'en': 'To remove k digits and keep the smallest number, walk from the left with a stack. Whenever the top of the stack is bigger than the next digit, pop it, because a smaller digit in that position makes the whole number smaller. If removals are left at the end, drop digits from the end.'},
    {'id': 'exchange-argument', 'h': 'Exchange argument', 'en': 'To prove a greedy rule, take any best answer and show that swapping in the greedy choice never makes it worse. For jobs on one server, a longer job just before a shorter one can be swapped to lower the total waiting time. So the best order runs the shortest job first.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from handing out cookies to scheduling courses before their deadlines. Each one is solved in Python, JavaScript, Java and TypeScript, and you can replay every solution line by line.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. For each problem, guess a greedy rule, then try to break it with a tiny example. If you cannot break it, think about why swapping in the greedy choice never hurts. Open the hint if you are stuck.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'What does a greedy algorithm do at each step?', 'o': ['Tries every option', 'Takes the choice that looks best right now and never undoes it', 'Picks at random', 'Goes back to fix old choices'], 'a': 1, 'hint': 'Think of the coin example.', 'why': 'Greedy commits to the locally best choice at each step.'},
    {'lv': 'e', 'q': 'With coins 1, 5, 10 and 25, how many coins does greedy use for 30?', 'o': ['2', '3', '6', '4'], 'a': 0, 'hint': 'Biggest first.', 'why': '25 + 5 = 30, two coins, which is the fewest possible.'},
    {'lv': 'e', 'q': 'For activity selection, which order gives the most activities?', 'o': ['Earliest start', 'Shortest first', 'Earliest finish', 'Latest start'], 'a': 2, 'hint': 'Leave the most room for the rest.', 'why': 'Picking the activity that ends first always leaves the most time for the others.'},
    {'lv': 'e', 'q': 'In the fractional knapsack, how are items ordered?', 'o': ['By weight', 'By value', 'By value per unit of weight', 'By name'], 'a': 2, 'hint': 'Which item gives the most for each kilo of space?', 'why': 'Taking the best value per kilo first fills the bag with the most value.'},
    {'lv': 'm', 'q': 'With coins 1, 3 and 4, greedy makes 6 as 4 + 1 + 1. What is the fewest?', 'o': ['1', '2', '3', '4'], 'a': 1, 'hint': 'Try two equal coins.', 'why': '3 + 3 uses two coins, so greedy is not optimal here.'},
    {'lv': 'm', 'q': 'In Huffman coding, which two trees are joined at each step?', 'o': ['The two most common', 'The two rarest', 'The first two letters', 'Any two'], 'a': 1, 'hint': 'Rare letters should sink deepest.', 'why': 'Joining the two smallest counts pushes rare letters deeper, giving them the longer codes.'},
    {'lv': 'm', 'q': 'Why can no Huffman code be the start of another code?', 'o': ['Because codes are random', 'Because letters sit only at leaves, so no letter is on the path to another', 'Because all codes have the same length', 'They can'], 'a': 1, 'hint': 'Where are the letters in the tree?', 'why': 'Every letter is a leaf, so its path never continues to another letter. That makes the code prefix free.'},
    {'lv': 'm', 'q': 'Jobs of length 5 and 1 run back to back. Which order gives less total waiting?', 'o': ['5 then 1', '1 then 5', 'Both are equal', 'It depends on the clock'], 'a': 1, 'hint': 'The second job waits for the first.', 'why': '1 then 5 makes the second job wait 1. 5 then 1 makes it wait 5.'},
    {'lv': 'h', 'q': 'Remove 3 digits from 1432219 to make the smallest number. What is it?', 'o': ['1219', '1229', '1321', '2219'], 'a': 0, 'hint': 'Pop a digit when the next one is smaller.', 'why': '4, 3 and one 2 are removed, leaving 1219.'},
    {'lv': 'h', 'q': 'Which of these is NOT a greedy algorithm?', 'o': ["Dijkstra's shortest paths", "Kruskal's spanning tree", 'Huffman coding', 'Bellman-Ford with n − 1 rounds'], 'a': 3, 'hint': 'Which one keeps revisiting old answers?', 'why': 'Bellman-Ford relaxes every edge again and again, improving earlier distances. The others commit to one choice at a time.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'acts = [(1, 3), (2, 5), (4, 6), (6, 8)]\nfree, n = 0, 0\nfor s, e in sorted(acts, key=lambda a: a[1]):\n    if s >= free:\n        n, free = n + 1, e\nprint(n)', 'o': ['2', '3', '4', '1'], 'a': 1, 'hint': 'Keep (1, 3), then the next one starting at 3 or later.', 'why': '(1, 3), then (4, 6), then (6, 8). Three activities.'},
    {'lv': 'h', 'q': 'A bag holds 50 kg. Gold 10 kg worth 60, silver 20 kg worth 100, bronze 30 kg worth 120, items whole. What does greedy by value per kg get?', 'o': ['160', '180', '220', '240'], 'a': 0, 'hint': 'Gold and silver fit, bronze does not.', 'why': 'Gold and silver use 30 kg for 160. Bronze no longer fits whole, though silver plus bronze would give 220.'},
    {'lv': 'x', 'q': 'In Gas Station, the tank goes negative on the way from station i to i + 1. Why can the start jump straight to i + 1?', 'o': ['Station i + 1 has the most gas', 'Every start between the old start and i reaches i with even less fuel, so they all fail too', 'It is a guess', 'Because the circle repeats'], 'a': 1, 'hint': 'Starting later means losing the fuel gathered before.', 'why': 'Each skipped start arrived at its own position with a non negative tank. Without that fuel, it would run dry even sooner.'},
    {'lv': 'x', 'q': 'In Course Schedule III, time passes the deadline. Which course is dropped?', 'o': ['The newest one', 'The longest one taken so far', 'The shortest one', 'The one with the earliest deadline'], 'a': 1, 'hint': 'Lose one course but free the most time.', 'why': 'Dropping the longest course frees the most time while the count only drops by one.'},
    {'lv': 'x', 'q': 'Candy ratings [1, 3, 4, 5, 2]. What is the smallest total?', 'o': ['9', '10', '11', '15'], 'a': 2, 'hint': 'Left pass: 1 2 3 4 1. Then fix from the right.', 'why': 'The right pass keeps 1 2 3 4 1, since 5 already has more than 2. Total 11.'},
    {'lv': 'x', 'q': 'Which statement best describes an exchange argument?', 'o': ['Try all orders and pick the best', 'Show that swapping the greedy choice into any best answer never makes it worse', 'Use a heap', 'Sort and hope'], 'a': 1, 'hint': 'It starts from some best answer.', 'why': 'If the greedy choice can always replace part of a best answer, greedy reaches a best answer too.'},
]

CALC = [
    {'lv': 'e', 'q': 'With coins 1, 5, 10 and 25, how many coins does greedy use for 41?', 'ans': '4', 'hint': 'Biggest coin first.', 'steps': ['<span class="eq">41 = 25 + 10 + 5 + 1</span>', 'Four coins.']},
    {'lv': 'e', 'q': 'With coins 1, 3 and 4, how many coins does greedy use for 6?', 'ans': '3', 'hint': 'Take 4 first.', 'steps': ['<span class="eq">6 = 4 + 1 + 1</span>, three coins, although 3 + 3 needs only two.']},
    {'lv': 'm', 'q': 'A bag holds 40 kg. Gold 10 kg worth 60, silver 20 kg worth 100, bronze 30 kg worth 120, items can be split. What is the best value?', 'ans': '200', 'hint': 'Value per kg: 6, 5, 4.', 'steps': ['Gold 10 kg: 60. Silver 20 kg: 100. 10 kg left.', 'Bronze 10 of 30 kg: <span class="eq">120 × 10 ÷ 30 = 40</span>', '<span class="eq">60 + 100 + 40 = 200</span>']},
    {'lv': 'm', 'q': 'Jobs of length 4, 1 and 3 run shortest first. What is the total waiting time?', 'ans': '5', 'hint': 'Order 1, 3, 4.', 'steps': ['Waits: 0, then 1, then 1 + 3 = 4.', '<span class="eq">0 + 1 + 4 = 5</span>']},
    {'lv': 'h', 'q': 'Huffman codes for counts a 1, b 1, c 2. How many bits does the text need in total?', 'ans': '6', 'hint': 'Join a and b first.', 'steps': ['a and b join into 2. Then c (2) and that tree (2) join into 4.', 'c gets a 1 bit code, a and b get 2 bit codes.', '<span class="eq">1 × 2 + 1 × 2 + 2 × 1 = 6</span>']},
    {'lv': 'h', 'q': 'Intervals [1,3], [2,4], [3,5], [4,6]. At most how many fit without overlapping, if touching ends are allowed?', 'ans': '2', 'hint': 'Sort by end and keep greedily.', 'steps': ['Keep [1,3]. [2,4] starts at 2, before 3: skip.', 'Keep [3,5]. [4,6] starts at 4, before 5: skip.', 'Total 2.']},
    {'lv': 'x', 'q': 'What does the Candy solution return for ratings [1, 3, 4, 5, 2]?', 'ans': '11', 'hint': 'Run the practice program.', 'steps': ['Left pass: 1 2 3 4 1.', 'Right pass changes nothing: 5 already has more than 2.', '<span class="eq">1 + 2 + 3 + 4 + 1 = 11</span>']},
    {'lv': 'x', 'q': 'Remove 3 digits from 1432219. What number is left?', 'ans': '1219', 'hint': 'Run the lesson program or the animation.', 'steps': ['Pop 4 before 3, pop 3 before 2, pop 2 before 1.', 'What remains is 1 2 1 9.']},
]

TALK = {
    'greedy-choice': 'A greedy algorithm is the simplest kind of strategy you can imagine. At every step, it looks at the choices in front of it, takes the one that looks best right now, and never changes its mind later. Think of paying a shop with coins. If you have coins of one, five, ten and twenty five, the obvious method is to hand over the biggest coin that still fits, again and again. For these coins, that always gives the fewest coins. But change the coins to one, three and four, and ask for six. Greedy grabs a four, then a one, then another one, which is three coins. Two threes would have been better. So a greedy idea can feel completely natural and still be wrong. Before you trust one, you need a reason why the best looking choice can never spoil the final answer.',
    'intervals': 'Imagine a single hall and a list of events, each with a start time and an end time. You want to fit as many events into the day as possible, with no two at the same time. You could try picking the event that starts first, or the shortest event, but both of those can lose. The rule that always wins is to sort the events by their end time. Take the event that ends first. Then take the next event that starts after it ends, and so on. Why does this work? Suppose someone shows you a perfect schedule. Replace its first event with the one that ends earliest. The new event finishes even sooner, so everything after it still fits, and the count is the same. Repeat this swap down the list, and you turn the perfect schedule into the greedy one.',
    'fractional-knapsack': 'Suppose you can carry fifty kilos, and you find gold dust, silver dust and bronze dust, each with a different value per kilo. Since dust can be split into any amount, the best plan is easy. Sort the items by value per kilo, take all of the most valuable one, then the next, and when the bag is nearly full, take just enough of the next item to fill it exactly. This greedy rule is always the best possible, because any kilo of space spent on a cheaper item could be swapped for a kilo of a more valuable one. Now change the dust into solid bars that you must take whole or leave behind. The same rule can now fail. In the example, greedy takes gold and silver for one hundred and sixty, while silver and bronze together are worth two hundred and twenty. That version needs dynamic programming.',
    'huffman': 'Computers normally store each letter with the same number of bits. Huffman coding saves space by giving common letters short codes and rare letters long codes. The trick is to build a tree. Start with every letter as its own tiny tree, labelled with how often it appears. Put them all in a queue, rarest first. Take the two rarest trees and join them under a new parent whose count is their sum. Put the new tree back in the queue and repeat until only one tree is left. Now read the codes: every step to the left adds a zero and every step to the right adds a one. Rare letters were joined early, so they sit deep and get long codes. Common letters were joined late, so they stay near the top. Because letters only sit at leaves, no code is the start of another, so decoding is never ambiguous.',
    'remove-digits': 'Here is a puzzle. You have a number like one four three two two one nine, and you must remove three digits to make the result as small as possible. The leftmost digits matter most, so focus there. Walk through the digits from left to right, keeping the ones you choose on a stack. Before adding a new digit, look at the top of the stack. If the top digit is bigger than the new digit, removing it makes the number smaller, so pop it, as long as you still have removals left. Then push the new digit. In the example, four is removed because three comes next, three is removed because two comes next, and one of the twos is removed because a one comes next, leaving one two one nine. If removals remain at the end, the kept digits rise from left to right, so drop them from the end.',
    'exchange-argument': 'How do you know a greedy rule is truly correct and not just lucky on your examples? The most common proof is called an exchange argument. Start from any best possible answer, then show that you can swap in the greedy choice without making it worse. Here is a clear example. One server must run several jobs, one after another, and every job waits for all the jobs before it. Suppose a long job runs just before a short job. If you swap the two, the short job waits less by the length of the long job, while the long job waits more only by the length of the short job. The total waiting drops. So in the best order, no long job sits just before a shorter one, which means the jobs run shortest first. Dijkstra, Prim, Kruskal and Huffman are all proved correct in this spirit.',
    'leetcode': 'The LeetCode problems in this chapter each hide a simple rule that is always safe to apply. You begin by matching cookies to children, giving the smallest cookie that works to the least greedy child, and by giving change at a lemonade stand, where saving five dollar bills keeps you safe. The medium problems ask whether you can jump to the end of an array by tracking how far you can reach, and how few intervals to remove, which is activity selection in disguise. The hard problems find where to start a drive around a ring of gas stations, and cut a string into the most parts so that no letter appears in two parts. The expert problems hand out the fewest candies with two passes, and pick the most courses before their deadlines with a heap that drops the longest course when time runs out.',
}

T = t.finish({
    'slug': 'greedy', 'title': 'Greedy Algorithms', 'short': 'Greedy algorithms', 'emoji': '🪙', 'topic': 'greedy', 'prefix': 'dsagreedy',
    'module': ('🧠', 'Greedy and dynamic programming'),
    'lead': 'Take the best looking step and never look back. Watch greedy win and lose with coins, fit the most events into a day, fill a bag with gold dust, build Huffman codes, shrink a number with a stack and prove a rule with a simple swap.',
    'desc': 'Greedy algorithms in DSA: the greedy choice property and when greedy fails, interval scheduling, the fractional knapsack, Huffman coding, remove k digits with a stack and the exchange argument, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 22,
    'summary': 'The greedy choice and when it fails, activity selection by earliest finish, the fractional knapsack, Huffman codes, removing digits with a stack and the exchange argument with shortest job first. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['greedy', 'greedy choice property', 'optimal substructure', 'coin change', 'activity selection', 'interval scheduling', 'fractional knapsack', 'huffman coding', 'prefix code', 'remove k digits', 'monotonic stack', 'exchange argument', 'shortest job first', 'jump game', 'gas station'],
    'added': '2026-11-23',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS, 'css': '',
    'prev': ('advanced-graphs', 'advanced-graphs', '🧭 Advanced graphs'),
    'next': None,
})
