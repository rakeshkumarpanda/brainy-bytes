# Dynamic programming 1: overlapping subproblems and memoisation, bottom up tables, take or skip in a line,
# coin change done right, grid paths and the 0/1 knapsack.
from kit4 import Topic

t = Topic()

# ---------------------------------------------------------------- lesson programs
t.code('fib', py=r'''
calls = 0


def fib_plain(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib_plain(n - 1) + fib_plain(n - 2)


def fib_memo(n, memo):
    global calls
    calls += 1
    if n < 2:
        return n
    if n not in memo:                         # solve each n once, then reuse the answer
        memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]


for n in (5, 10):
    calls = 0
    a = fib_plain(n)
    plain_calls = calls
    calls = 0
    fib_memo(n, {})
    print(f"fib({n}) = {a}: plain recursion makes {plain_calls} calls, with a memo only {calls}")
calls = 0
big = fib_memo(50, {})
print(f"fib(50) = {big} with a memo after {calls} calls")
''', js=r'''
let calls = 0;

function fibPlain(n) {
  calls++;
  if (n < 2) return n;
  return fibPlain(n - 1) + fibPlain(n - 2);
}

function fibMemo(n, memo) {
  calls++;
  if (n < 2) return n;
  if (!memo.has(n)) memo.set(n, fibMemo(n - 1, memo) + fibMemo(n - 2, memo));   // solve each n once, then reuse
  return memo.get(n);
}

for (const n of [5, 10]) {
  calls = 0;
  const a = fibPlain(n);
  const plainCalls = calls;
  calls = 0;
  fibMemo(n, new Map());
  console.log(`fib(${n}) = ${a}: plain recursion makes ${plainCalls} calls, with a memo only ${calls}`);
}
calls = 0;
const big = fibMemo(50, new Map());
console.log(`fib(50) = ${big} with a memo after ${calls} calls`);
''', java=r'''
import java.util.*;

public class Fib {
    static int calls = 0;

    static long fibPlain(int n) {
        calls++;
        if (n < 2) return n;
        return fibPlain(n - 1) + fibPlain(n - 2);
    }

    static long fibMemo(int n, Map<Integer, Long> memo) {
        calls++;
        if (n < 2) return n;
        if (!memo.containsKey(n)) memo.put(n, fibMemo(n - 1, memo) + fibMemo(n - 2, memo));   // solve each n once, then reuse
        return memo.get(n);
    }

    public static void main(String[] args) {
        for (int n : new int[]{5, 10}) {
            calls = 0;
            long a = fibPlain(n);
            int plainCalls = calls;
            calls = 0;
            fibMemo(n, new HashMap<>());
            System.out.println("fib(" + n + ") = " + a + ": plain recursion makes " + plainCalls + " calls, with a memo only " + calls);
        }
        calls = 0;
        long big = fibMemo(50, new HashMap<>());
        System.out.println("fib(50) = " + big + " with a memo after " + calls + " calls");
    }
}
''', ts=r'''
let calls = 0;

function fibPlain(n: number): number {
  calls++;
  if (n < 2) return n;
  return fibPlain(n - 1) + fibPlain(n - 2);
}

function fibMemo(n: number, memo: Map<number, number>): number {
  calls++;
  if (n < 2) return n;
  if (!memo.has(n)) memo.set(n, fibMemo(n - 1, memo) + fibMemo(n - 2, memo));   // solve each n once, then reuse
  return memo.get(n) as number;
}

for (const n of [5, 10]) {
  calls = 0;
  const a = fibPlain(n);
  const plainCalls = calls;
  calls = 0;
  fibMemo(n, new Map());
  console.log(`fib(${n}) = ${a}: plain recursion makes ${plainCalls} calls, with a memo only ${calls}`);
}
calls = 0;
const big = fibMemo(50, new Map());
console.log(`fib(50) = ${big} with a memo after ${calls} calls`);
''')

t.code('stairs', py=r'''
def count_ways(n, steps):
    ways = [0] * (n + 1)
    ways[0] = 1                               # one way to climb no stairs: do nothing
    for i in range(1, n + 1):
        for s in steps:                       # the last move was a jump of s stairs
            if s <= i:
                ways[i] += ways[i - s]
    return ways


for steps in ([1, 2], [1, 2, 3]):
    print(f"jumps {steps}: ways for 0 to 6 stairs {count_ways(6, steps)}")
''', js=r'''
function countWays(n, steps) {
  const ways = new Array(n + 1).fill(0);
  ways[0] = 1;                                // one way to climb no stairs: do nothing
  for (let i = 1; i <= n; i++) {
    for (const s of steps) {                  // the last move was a jump of s stairs
      if (s <= i) ways[i] += ways[i - s];
    }
  }
  return ways;
}

for (const steps of [[1, 2], [1, 2, 3]]) {
  console.log(`jumps [${steps.join(", ")}]: ways for 0 to 6 stairs [${countWays(6, steps).join(", ")}]`);
}
''', java=r'''
import java.util.*;

public class Stairs {
    static int[] countWays(int n, int[] steps) {
        int[] ways = new int[n + 1];
        ways[0] = 1;                              // one way to climb no stairs: do nothing
        for (int i = 1; i <= n; i++)
            for (int s : steps)                   // the last move was a jump of s stairs
                if (s <= i) ways[i] += ways[i - s];
        return ways;
    }

    public static void main(String[] args) {
        for (int[] steps : new int[][]{{1, 2}, {1, 2, 3}})
            System.out.println("jumps " + Arrays.toString(steps) + ": ways for 0 to 6 stairs " + Arrays.toString(countWays(6, steps)));
    }
}
''', ts=r'''
function countWays(n: number, steps: number[]): number[] {
  const ways: number[] = new Array(n + 1).fill(0);
  ways[0] = 1;                                // one way to climb no stairs: do nothing
  for (let i = 1; i <= n; i++) {
    for (const s of steps) {                  // the last move was a jump of s stairs
      if (s <= i) ways[i] += ways[i - s];
    }
  }
  return ways;
}

for (const steps of [[1, 2], [1, 2, 3]]) {
  console.log(`jumps [${steps.join(", ")}]: ways for 0 to 6 stairs [${countWays(6, steps).join(", ")}]`);
}
''')

t.code('robber', py=r'''
def rob(houses):
    best = []                                 # best[i]: the most money from houses 0 to i
    for i, money in enumerate(houses):
        take = money + (best[i - 2] if i >= 2 else 0)
        skip = best[i - 1] if i >= 1 else 0
        best.append(max(take, skip))
    picked, i = [], len(houses) - 1           # walk back to see which houses were robbed
    while i >= 0:
        if i == 0 or best[i] != best[i - 1]:
            picked.append(i)
            i -= 2
        else:
            i -= 1
    return best, picked[::-1]


for houses in ([2, 7, 9, 3, 1], [6, 1, 2, 10, 4]):
    best, picked = rob(houses)
    print(f"houses {houses}: best so far {best}, rob houses {picked} for {best[-1]}")
''', js=r'''
function rob(houses) {
  const best = [];                            // best[i]: the most money from houses 0 to i
  houses.forEach((money, i) => {
    const take = money + (i >= 2 ? best[i - 2] : 0);
    const skip = i >= 1 ? best[i - 1] : 0;
    best.push(Math.max(take, skip));
  });
  const picked = [];                          // walk back to see which houses were robbed
  let i = houses.length - 1;
  while (i >= 0) {
    if (i === 0 || best[i] !== best[i - 1]) { picked.push(i); i -= 2; }
    else i -= 1;
  }
  return [best, picked.reverse()];
}

for (const houses of [[2, 7, 9, 3, 1], [6, 1, 2, 10, 4]]) {
  const [best, picked] = rob(houses);
  console.log(`houses [${houses.join(", ")}]: best so far [${best.join(", ")}], rob houses [${picked.join(", ")}] for ${best[best.length - 1]}`);
}
''', java=r'''
import java.util.*;

public class Robber {
    public static void main(String[] args) {
        for (int[] houses : new int[][]{{2, 7, 9, 3, 1}, {6, 1, 2, 10, 4}}) {
            int n = houses.length;
            int[] best = new int[n];              // best[i]: the most money from houses 0 to i
            for (int i = 0; i < n; i++) {
                int take = houses[i] + (i >= 2 ? best[i - 2] : 0);
                int skip = i >= 1 ? best[i - 1] : 0;
                best[i] = Math.max(take, skip);
            }
            List<Integer> picked = new ArrayList<>();   // walk back to see which houses were robbed
            int i = n - 1;
            while (i >= 0) {
                if (i == 0 || best[i] != best[i - 1]) { picked.add(i); i -= 2; }
                else i -= 1;
            }
            Collections.reverse(picked);
            System.out.println("houses " + Arrays.toString(houses) + ": best so far " + Arrays.toString(best) + ", rob houses " + picked + " for " + best[n - 1]);
        }
    }
}
''', ts=r'''
function rob(houses: number[]): [number[], number[]] {
  const best: number[] = [];                  // best[i]: the most money from houses 0 to i
  houses.forEach((money, i) => {
    const take = money + (i >= 2 ? best[i - 2] : 0);
    const skip = i >= 1 ? best[i - 1] : 0;
    best.push(Math.max(take, skip));
  });
  const picked: number[] = [];                // walk back to see which houses were robbed
  let i = houses.length - 1;
  while (i >= 0) {
    if (i === 0 || best[i] !== best[i - 1]) { picked.push(i); i -= 2; }
    else i -= 1;
  }
  return [best, picked.reverse()];
}

for (const houses of [[2, 7, 9, 3, 1], [6, 1, 2, 10, 4]]) {
  const [best, picked] = rob(houses);
  console.log(`houses [${houses.join(", ")}]: best so far [${best.join(", ")}], rob houses [${picked.join(", ")}] for ${best[best.length - 1]}`);
}
''')

t.code('coindp', py=r'''
def min_coins(amount, coins):
    NONE = amount + 1                         # more coins than could ever be needed
    best = [0] + [NONE] * amount              # best[a]: the fewest coins that make a
    last = [0] * (amount + 1)                 # the coin added last to reach a
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and best[a - c] + 1 < best[a]:
                best[a] = best[a - c] + 1
                last[a] = c
    if best[amount] == NONE:
        return None
    used = []
    while amount > 0:                         # follow the last coins back to 0
        used.append(last[amount])
        amount -= last[amount]
    return used


def count_ways(amount, coins):
    ways = [1] + [0] * amount                 # coins in the outer loop, so each mix is counted once
    for c in coins:
        for a in range(c, amount + 1):
            ways[a] += ways[a - c]
    return ways[amount]


for amount, coins in ((6, [1, 3, 4]), (30, [1, 10, 25]), (7, [2, 4])):
    used = min_coins(amount, coins)
    print(f"make {amount} with {coins}: " + (f"fewest {len(used)} coins {used}" if used else "impossible"))
print(f"ways to make 5 with [1, 2, 5]: {count_ways(5, [1, 2, 5])}")
''', js=r'''
function minCoins(amount, coins) {
  const NONE = amount + 1;                    // more coins than could ever be needed
  const best = [0, ...new Array(amount).fill(NONE)];   // best[a]: the fewest coins that make a
  const last = new Array(amount + 1).fill(0); // the coin added last to reach a
  for (let a = 1; a <= amount; a++) {
    for (const c of coins) {
      if (c <= a && best[a - c] + 1 < best[a]) { best[a] = best[a - c] + 1; last[a] = c; }
    }
  }
  if (best[amount] === NONE) return null;
  const used = [];
  while (amount > 0) { used.push(last[amount]); amount -= last[amount]; }   // follow the last coins back to 0
  return used;
}

function countWays(amount, coins) {
  const ways = [1, ...new Array(amount).fill(0)];   // coins in the outer loop, so each mix is counted once
  for (const c of coins) {
    for (let a = c; a <= amount; a++) ways[a] += ways[a - c];
  }
  return ways[amount];
}

for (const [amount, coins] of [[6, [1, 3, 4]], [30, [1, 10, 25]], [7, [2, 4]]]) {
  const used = minCoins(amount, coins);
  console.log(`make ${amount} with [${coins.join(", ")}]: ` + (used ? `fewest ${used.length} coins [${used.join(", ")}]` : "impossible"));
}
console.log(`ways to make 5 with [1, 2, 5]: ${countWays(5, [1, 2, 5])}`);
''', java=r'''
import java.util.*;

public class CoinDP {
    static List<Integer> minCoins(int amount, int[] coins) {
        int none = amount + 1;                    // more coins than could ever be needed
        int[] best = new int[amount + 1];         // best[a]: the fewest coins that make a
        int[] last = new int[amount + 1];         // the coin added last to reach a
        Arrays.fill(best, none);
        best[0] = 0;
        for (int a = 1; a <= amount; a++)
            for (int c : coins)
                if (c <= a && best[a - c] + 1 < best[a]) { best[a] = best[a - c] + 1; last[a] = c; }
        if (best[amount] == none) return null;
        List<Integer> used = new ArrayList<>();
        while (amount > 0) { used.add(last[amount]); amount -= last[amount]; }   // follow the last coins back to 0
        return used;
    }

    static int countWays(int amount, int[] coins) {
        int[] ways = new int[amount + 1];         // coins in the outer loop, so each mix is counted once
        ways[0] = 1;
        for (int c : coins)
            for (int a = c; a <= amount; a++) ways[a] += ways[a - c];
        return ways[amount];
    }

    public static void main(String[] args) {
        int[] amounts = {6, 30, 7};
        int[][] coinSets = {{1, 3, 4}, {1, 10, 25}, {2, 4}};
        for (int k = 0; k < 3; k++) {
            List<Integer> used = minCoins(amounts[k], coinSets[k]);
            System.out.println("make " + amounts[k] + " with " + Arrays.toString(coinSets[k]) + ": " + (used != null ? "fewest " + used.size() + " coins " + used : "impossible"));
        }
        System.out.println("ways to make 5 with [1, 2, 5]: " + countWays(5, new int[]{1, 2, 5}));
    }
}
''', ts=r'''
function minCoins(amount: number, coins: number[]): number[] | null {
  const NONE = amount + 1;                    // more coins than could ever be needed
  const best: number[] = [0, ...new Array(amount).fill(NONE)];   // best[a]: the fewest coins that make a
  const last: number[] = new Array(amount + 1).fill(0);          // the coin added last to reach a
  for (let a = 1; a <= amount; a++) {
    for (const c of coins) {
      if (c <= a && best[a - c] + 1 < best[a]) { best[a] = best[a - c] + 1; last[a] = c; }
    }
  }
  if (best[amount] === NONE) return null;
  const used: number[] = [];
  while (amount > 0) { used.push(last[amount]); amount -= last[amount]; }   // follow the last coins back to 0
  return used;
}

function countWays(amount: number, coins: number[]): number {
  const ways: number[] = [1, ...new Array(amount).fill(0)];   // coins in the outer loop, so each mix is counted once
  for (const c of coins) {
    for (let a = c; a <= amount; a++) ways[a] += ways[a - c];
  }
  return ways[amount];
}

const cases: [number, number[]][] = [[6, [1, 3, 4]], [30, [1, 10, 25]], [7, [2, 4]]];
for (const [amount, coins] of cases) {
  const used = minCoins(amount, coins);
  console.log(`make ${amount} with [${coins.join(", ")}]: ` + (used ? `fewest ${used.length} coins [${used.join(", ")}]` : "impossible"));
}
console.log(`ways to make 5 with [1, 2, 5]: ${countWays(5, [1, 2, 5])}`);
''')

t.code('grid', py=r'''
def min_path(grid):
    rows, cols = len(grid), len(grid[0])
    cost = [[0] * cols for _ in range(rows)]  # cost[r][c]: the cheapest walk from the top left to (r, c)
    for r in range(rows):
        for c in range(cols):
            if r == 0 and c == 0:
                cost[r][c] = grid[0][0]
            elif r == 0:
                cost[r][c] = cost[r][c - 1] + grid[r][c]
            elif c == 0:
                cost[r][c] = cost[r - 1][c] + grid[r][c]
            else:
                cost[r][c] = min(cost[r - 1][c], cost[r][c - 1]) + grid[r][c]
    path, r, c = [], rows - 1, cols - 1       # walk back through the cheaper neighbour
    while True:
        path.append(grid[r][c])
        if r == 0 and c == 0:
            break
        if c == 0 or (r > 0 and cost[r - 1][c] <= cost[r][c - 1]):
            r -= 1
        else:
            c -= 1
    return cost, path[::-1]


grid = [[1, 3, 1], [1, 5, 1], [4, 2, 1]]
cost, path = min_path(grid)
for row in cost:
    print(row)
print("cheapest walk " + " + ".join(str(x) for x in path) + f" = {sum(path)}")
''', js=r'''
function minPath(grid) {
  const rows = grid.length, cols = grid[0].length;
  const cost = Array.from({ length: rows }, () => new Array(cols).fill(0));   // cost[r][c]: the cheapest walk to (r, c)
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (r === 0 && c === 0) cost[r][c] = grid[0][0];
      else if (r === 0) cost[r][c] = cost[r][c - 1] + grid[r][c];
      else if (c === 0) cost[r][c] = cost[r - 1][c] + grid[r][c];
      else cost[r][c] = Math.min(cost[r - 1][c], cost[r][c - 1]) + grid[r][c];
    }
  }
  const path = [];                            // walk back through the cheaper neighbour
  let r = rows - 1, c = cols - 1;
  for (;;) {
    path.push(grid[r][c]);
    if (r === 0 && c === 0) break;
    if (c === 0 || (r > 0 && cost[r - 1][c] <= cost[r][c - 1])) r--;
    else c--;
  }
  return [cost, path.reverse()];
}

const grid = [[1, 3, 1], [1, 5, 1], [4, 2, 1]];
const [cost, path] = minPath(grid);
for (const row of cost) console.log(`[${row.join(", ")}]`);
console.log(`cheapest walk ${path.join(" + ")} = ${path.reduce((a, b) => a + b, 0)}`);
''', java=r'''
import java.util.*;

public class GridPath {
    public static void main(String[] args) {
        int[][] grid = {{1, 3, 1}, {1, 5, 1}, {4, 2, 1}};
        int rows = grid.length, cols = grid[0].length;
        int[][] cost = new int[rows][cols];       // cost[r][c]: the cheapest walk from the top left to (r, c)
        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++) {
                if (r == 0 && c == 0) cost[r][c] = grid[0][0];
                else if (r == 0) cost[r][c] = cost[r][c - 1] + grid[r][c];
                else if (c == 0) cost[r][c] = cost[r - 1][c] + grid[r][c];
                else cost[r][c] = Math.min(cost[r - 1][c], cost[r][c - 1]) + grid[r][c];
            }
        List<Integer> path = new ArrayList<>();   // walk back through the cheaper neighbour
        int r = rows - 1, c = cols - 1;
        while (true) {
            path.add(grid[r][c]);
            if (r == 0 && c == 0) break;
            if (c == 0 || (r > 0 && cost[r - 1][c] <= cost[r][c - 1])) r--;
            else c--;
        }
        Collections.reverse(path);
        for (int[] row : cost) System.out.println(Arrays.toString(row));
        StringBuilder sb = new StringBuilder();
        int sum = 0;
        for (int k = 0; k < path.size(); k++) { sb.append(k > 0 ? " + " : "").append(path.get(k)); sum += path.get(k); }
        System.out.println("cheapest walk " + sb + " = " + sum);
    }
}
''', ts=r'''
function minPath(grid: number[][]): [number[][], number[]] {
  const rows = grid.length, cols = grid[0].length;
  const cost: number[][] = Array.from({ length: rows }, () => new Array(cols).fill(0));   // cost[r][c]: the cheapest walk to (r, c)
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (r === 0 && c === 0) cost[r][c] = grid[0][0];
      else if (r === 0) cost[r][c] = cost[r][c - 1] + grid[r][c];
      else if (c === 0) cost[r][c] = cost[r - 1][c] + grid[r][c];
      else cost[r][c] = Math.min(cost[r - 1][c], cost[r][c - 1]) + grid[r][c];
    }
  }
  const path: number[] = [];                  // walk back through the cheaper neighbour
  let r = rows - 1, c = cols - 1;
  for (;;) {
    path.push(grid[r][c]);
    if (r === 0 && c === 0) break;
    if (c === 0 || (r > 0 && cost[r - 1][c] <= cost[r][c - 1])) r--;
    else c--;
  }
  return [cost, path.reverse()];
}

const grid: number[][] = [[1, 3, 1], [1, 5, 1], [4, 2, 1]];
const [cost, path] = minPath(grid);
for (const row of cost) console.log(`[${row.join(", ")}]`);
console.log(`cheapest walk ${path.join(" + ")} = ${path.reduce((a, b) => a + b, 0)}`);
''')

t.code('knapsack', py=r'''
def knapsack(weights, values, cap):
    n = len(weights)
    best = [[0] * (cap + 1) for _ in range(n + 1)]   # best[i][w]: the first i items in a bag of size w
    for i in range(1, n + 1):
        wt, val = weights[i - 1], values[i - 1]
        for w in range(cap + 1):
            best[i][w] = best[i - 1][w]              # leave item i out
            if wt <= w and best[i - 1][w - wt] + val > best[i][w]:
                best[i][w] = best[i - 1][w - wt] + val   # or put it in, if that is worth more
    chosen, w = [], cap                              # walk back up the table
    for i in range(n, 0, -1):
        if best[i][w] != best[i - 1][w]:
            chosen.append(i - 1)
            w -= weights[i - 1]
    return best[n][cap], chosen[::-1]


value, items = knapsack([10, 20, 30], [60, 100, 120], 50)
print(f"bars of 10, 20, 30 kg worth 60, 100, 120 in a 50 kg bag: best {value}, take items {items}")
value, items = knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7)
print(f"weights 1, 3, 4, 5 worth 1, 4, 5, 7 in a bag of 7: best {value}, take items {items}")
''', js=r'''
function knapsack(weights, values, cap) {
  const n = weights.length;
  const best = Array.from({ length: n + 1 }, () => new Array(cap + 1).fill(0));   // best[i][w]: first i items, bag of size w
  for (let i = 1; i <= n; i++) {
    const wt = weights[i - 1], val = values[i - 1];
    for (let w = 0; w <= cap; w++) {
      best[i][w] = best[i - 1][w];                   // leave item i out
      if (wt <= w && best[i - 1][w - wt] + val > best[i][w]) best[i][w] = best[i - 1][w - wt] + val;   // or put it in
    }
  }
  const chosen = [];                                 // walk back up the table
  let w = cap;
  for (let i = n; i > 0; i--) {
    if (best[i][w] !== best[i - 1][w]) { chosen.push(i - 1); w -= weights[i - 1]; }
  }
  return [best[n][cap], chosen.reverse()];
}

let [value, items] = knapsack([10, 20, 30], [60, 100, 120], 50);
console.log(`bars of 10, 20, 30 kg worth 60, 100, 120 in a 50 kg bag: best ${value}, take items [${items.join(", ")}]`);
[value, items] = knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7);
console.log(`weights 1, 3, 4, 5 worth 1, 4, 5, 7 in a bag of 7: best ${value}, take items [${items.join(", ")}]`);
''', java=r'''
import java.util.*;

public class Knapsack {
    static int best;
    static List<Integer> chosen;

    static void knapsack(int[] weights, int[] values, int cap) {
        int n = weights.length;
        int[][] t = new int[n + 1][cap + 1];             // t[i][w]: the first i items in a bag of size w
        for (int i = 1; i <= n; i++) {
            int wt = weights[i - 1], val = values[i - 1];
            for (int w = 0; w <= cap; w++) {
                t[i][w] = t[i - 1][w];                   // leave item i out
                if (wt <= w && t[i - 1][w - wt] + val > t[i][w]) t[i][w] = t[i - 1][w - wt] + val;   // or put it in
            }
        }
        chosen = new ArrayList<>();                      // walk back up the table
        int w = cap;
        for (int i = n; i > 0; i--)
            if (t[i][w] != t[i - 1][w]) { chosen.add(i - 1); w -= weights[i - 1]; }
        Collections.reverse(chosen);
        best = t[n][cap];
    }

    public static void main(String[] args) {
        knapsack(new int[]{10, 20, 30}, new int[]{60, 100, 120}, 50);
        System.out.println("bars of 10, 20, 30 kg worth 60, 100, 120 in a 50 kg bag: best " + best + ", take items " + chosen);
        knapsack(new int[]{1, 3, 4, 5}, new int[]{1, 4, 5, 7}, 7);
        System.out.println("weights 1, 3, 4, 5 worth 1, 4, 5, 7 in a bag of 7: best " + best + ", take items " + chosen);
    }
}
''', ts=r'''
function knapsack(weights: number[], values: number[], cap: number): [number, number[]] {
  const n = weights.length;
  const best: number[][] = Array.from({ length: n + 1 }, () => new Array(cap + 1).fill(0));   // first i items, bag of size w
  for (let i = 1; i <= n; i++) {
    const wt = weights[i - 1], val = values[i - 1];
    for (let w = 0; w <= cap; w++) {
      best[i][w] = best[i - 1][w];                   // leave item i out
      if (wt <= w && best[i - 1][w - wt] + val > best[i][w]) best[i][w] = best[i - 1][w - wt] + val;   // or put it in
    }
  }
  const chosen: number[] = [];                       // walk back up the table
  let w = cap;
  for (let i = n; i > 0; i--) {
    if (best[i][w] !== best[i - 1][w]) { chosen.push(i - 1); w -= weights[i - 1]; }
  }
  return [best[n][cap], chosen.reverse()];
}

let [value, items] = knapsack([10, 20, 30], [60, 100, 120], 50);
console.log(`bars of 10, 20, 30 kg worth 60, 100, 120 in a 50 kg bag: best ${value}, take items [${items.join(", ")}]`);
[value, items] = knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7);
console.log(`weights 1, 3, 4, 5 worth 1, 4, 5, 7 in a bag of 7: best ${value}, take items [${items.join(", ")}]`);
''')

# ---------------------------------------------------------------- LeetCode programs
t.code('p_stairs', py=r'''
def climb_stairs(n):
    a, b = 1, 1                               # ways to reach the stair before and the current stair
    for _ in range(n - 1):
        a, b = b, a + b
    return b


for n in (1, 2, 3, 5, 10):
    print(n, climb_stairs(n))
''', js=r'''
function climbStairs(n) {
  let a = 1, b = 1;                           // ways to reach the stair before and the current stair
  for (let k = 0; k < n - 1; k++) [a, b] = [b, a + b];
  return b;
}

for (const n of [1, 2, 3, 5, 10]) console.log(n, climbStairs(n));
''', java=r'''
public class ClimbStairs {
    static int climbStairs(int n) {
        int a = 1, b = 1;                         // ways to reach the stair before and the current stair
        for (int k = 0; k < n - 1; k++) { int c = a + b; a = b; b = c; }
        return b;
    }

    public static void main(String[] args) {
        for (int n : new int[]{1, 2, 3, 5, 10}) System.out.println(n + " " + climbStairs(n));
    }
}
''', ts=r'''
function climbStairs(n: number): number {
  let a = 1, b = 1;                           // ways to reach the stair before and the current stair
  for (let k = 0; k < n - 1; k++) [a, b] = [b, a + b];
  return b;
}

for (const n of [1, 2, 3, 5, 10]) console.log(n, climbStairs(n));
''')

t.code('p_mincost', py=r'''
def min_cost_climbing_stairs(cost):
    a, b = 0, 0                               # cheapest way to stand on stair i - 2 and on stair i - 1
    for i in range(2, len(cost) + 1):
        a, b = b, min(b + cost[i - 1], a + cost[i - 2])
    return b


print(min_cost_climbing_stairs([10, 15, 20]))
print(min_cost_climbing_stairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]))
''', js=r'''
function minCostClimbingStairs(cost) {
  let a = 0, b = 0;                           // cheapest way to stand on stair i - 2 and on stair i - 1
  for (let i = 2; i <= cost.length; i++) [a, b] = [b, Math.min(b + cost[i - 1], a + cost[i - 2])];
  return b;
}

console.log(minCostClimbingStairs([10, 15, 20]));
console.log(minCostClimbingStairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]));
''', java=r'''
public class MinCostStairs {
    static int minCostClimbingStairs(int[] cost) {
        int a = 0, b = 0;                         // cheapest way to stand on stair i - 2 and on stair i - 1
        for (int i = 2; i <= cost.length; i++) {
            int c = Math.min(b + cost[i - 1], a + cost[i - 2]);
            a = b;
            b = c;
        }
        return b;
    }

    public static void main(String[] args) {
        System.out.println(minCostClimbingStairs(new int[]{10, 15, 20}));
        System.out.println(minCostClimbingStairs(new int[]{1, 100, 1, 1, 1, 100, 1, 1, 100, 1}));
    }
}
''', ts=r'''
function minCostClimbingStairs(cost: number[]): number {
  let a = 0, b = 0;                           // cheapest way to stand on stair i - 2 and on stair i - 1
  for (let i = 2; i <= cost.length; i++) [a, b] = [b, Math.min(b + cost[i - 1], a + cost[i - 2])];
  return b;
}

console.log(minCostClimbingStairs([10, 15, 20]));
console.log(minCostClimbingStairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]));
''')

t.code('p_rob', py=r'''
def rob(nums):
    prev, cur = 0, 0                          # the best up to house i - 2 and up to house i - 1
    for x in nums:
        prev, cur = cur, max(cur, prev + x)   # skip this house, or rob it on top of prev
    return cur


print(rob([1, 2, 3, 1]), rob([2, 7, 9, 3, 1]), rob([2, 1, 1, 2]))
''', js=r'''
function rob(nums) {
  let prev = 0, cur = 0;                      // the best up to house i - 2 and up to house i - 1
  for (const x of nums) [prev, cur] = [cur, Math.max(cur, prev + x)];   // skip, or rob on top of prev
  return cur;
}

console.log(rob([1, 2, 3, 1]), rob([2, 7, 9, 3, 1]), rob([2, 1, 1, 2]));
''', java=r'''
public class HouseRobber {
    static int rob(int[] nums) {
        int prev = 0, cur = 0;                    // the best up to house i - 2 and up to house i - 1
        for (int x : nums) {
            int next = Math.max(cur, prev + x);   // skip this house, or rob it on top of prev
            prev = cur;
            cur = next;
        }
        return cur;
    }

    public static void main(String[] args) {
        System.out.println(rob(new int[]{1, 2, 3, 1}) + " " + rob(new int[]{2, 7, 9, 3, 1}) + " " + rob(new int[]{2, 1, 1, 2}));
    }
}
''', ts=r'''
function rob(nums: number[]): number {
  let prev = 0, cur = 0;                      // the best up to house i - 2 and up to house i - 1
  for (const x of nums) [prev, cur] = [cur, Math.max(cur, prev + x)];   // skip, or rob on top of prev
  return cur;
}

console.log(rob([1, 2, 3, 1]), rob([2, 7, 9, 3, 1]), rob([2, 1, 1, 2]));
''')

t.code('p_paths', py=r'''
def unique_paths(m, n):
    row = [1] * n                             # one way to reach each cell of the top row
    for _ in range(m - 1):
        for c in range(1, n):
            row[c] += row[c - 1]              # ways from above (the old row[c]) plus ways from the left
    return row[-1]


print(unique_paths(3, 7), unique_paths(3, 2), unique_paths(10, 10))
''', js=r'''
function uniquePaths(m, n) {
  const row = new Array(n).fill(1);           // one way to reach each cell of the top row
  for (let k = 0; k < m - 1; k++) {
    for (let c = 1; c < n; c++) row[c] += row[c - 1];   // ways from above plus ways from the left
  }
  return row[n - 1];
}

console.log(uniquePaths(3, 7), uniquePaths(3, 2), uniquePaths(10, 10));
''', java=r'''
import java.util.*;

public class UniquePaths {
    static int uniquePaths(int m, int n) {
        int[] row = new int[n];
        Arrays.fill(row, 1);                      // one way to reach each cell of the top row
        for (int k = 0; k < m - 1; k++)
            for (int c = 1; c < n; c++) row[c] += row[c - 1];   // ways from above plus ways from the left
        return row[n - 1];
    }

    public static void main(String[] args) {
        System.out.println(uniquePaths(3, 7) + " " + uniquePaths(3, 2) + " " + uniquePaths(10, 10));
    }
}
''', ts=r'''
function uniquePaths(m: number, n: number): number {
  const row: number[] = new Array(n).fill(1); // one way to reach each cell of the top row
  for (let k = 0; k < m - 1; k++) {
    for (let c = 1; c < n; c++) row[c] += row[c - 1];   // ways from above plus ways from the left
  }
  return row[n - 1];
}

console.log(uniquePaths(3, 7), uniquePaths(3, 2), uniquePaths(10, 10));
''')

t.code('p_coins', py=r'''
def coin_change(coins, amount):
    best = [0] + [amount + 1] * amount        # amount + 1 means "not possible yet"
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                best[a] = min(best[a], best[a - c] + 1)
    return best[amount] if best[amount] <= amount else -1


print(coin_change([1, 2, 5], 11), coin_change([2], 3), coin_change([1], 0), coin_change([1, 3, 4], 6))
''', js=r'''
function coinChange(coins, amount) {
  const best = [0, ...new Array(amount).fill(amount + 1)];   // amount + 1 means "not possible yet"
  for (let a = 1; a <= amount; a++) {
    for (const c of coins) if (c <= a) best[a] = Math.min(best[a], best[a - c] + 1);
  }
  return best[amount] <= amount ? best[amount] : -1;
}

console.log(coinChange([1, 2, 5], 11), coinChange([2], 3), coinChange([1], 0), coinChange([1, 3, 4], 6));
''', java=r'''
import java.util.*;

public class CoinChange {
    static int coinChange(int[] coins, int amount) {
        int[] best = new int[amount + 1];
        Arrays.fill(best, amount + 1);            // amount + 1 means "not possible yet"
        best[0] = 0;
        for (int a = 1; a <= amount; a++)
            for (int c : coins)
                if (c <= a) best[a] = Math.min(best[a], best[a - c] + 1);
        return best[amount] <= amount ? best[amount] : -1;
    }

    public static void main(String[] args) {
        System.out.println(coinChange(new int[]{1, 2, 5}, 11) + " " + coinChange(new int[]{2}, 3) + " " + coinChange(new int[]{1}, 0) + " " + coinChange(new int[]{1, 3, 4}, 6));
    }
}
''', ts=r'''
function coinChange(coins: number[], amount: number): number {
  const best: number[] = [0, ...new Array(amount).fill(amount + 1)];   // amount + 1 means "not possible yet"
  for (let a = 1; a <= amount; a++) {
    for (const c of coins) if (c <= a) best[a] = Math.min(best[a], best[a - c] + 1);
  }
  return best[amount] <= amount ? best[amount] : -1;
}

console.log(coinChange([1, 2, 5], 11), coinChange([2], 3), coinChange([1], 0), coinChange([1, 3, 4], 6));
''')

t.code('p_triangle', py=r'''
def minimum_total(triangle):
    below = triangle[-1][:]                   # the best sums starting from the bottom row
    for r in range(len(triangle) - 2, -1, -1):
        for c in range(r + 1):
            below[c] = triangle[r][c] + min(below[c], below[c + 1])
    return below[0]


print(minimum_total([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]), minimum_total([[-10]]))
''', js=r'''
function minimumTotal(triangle) {
  const below = [...triangle[triangle.length - 1]];   // the best sums starting from the bottom row
  for (let r = triangle.length - 2; r >= 0; r--) {
    for (let c = 0; c <= r; c++) below[c] = triangle[r][c] + Math.min(below[c], below[c + 1]);
  }
  return below[0];
}

console.log(minimumTotal([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]), minimumTotal([[-10]]));
''', java=r'''
public class Triangle {
    static int minimumTotal(int[][] triangle) {
        int[] below = triangle[triangle.length - 1].clone();   // the best sums starting from the bottom row
        for (int r = triangle.length - 2; r >= 0; r--)
            for (int c = 0; c <= r; c++) below[c] = triangle[r][c] + Math.min(below[c], below[c + 1]);
        return below[0];
    }

    public static void main(String[] args) {
        System.out.println(minimumTotal(new int[][]{{2}, {3, 4}, {6, 5, 7}, {4, 1, 8, 3}}) + " " + minimumTotal(new int[][]{{-10}}));
    }
}
''', ts=r'''
function minimumTotal(triangle: number[][]): number {
  const below = [...triangle[triangle.length - 1]];   // the best sums starting from the bottom row
  for (let r = triangle.length - 2; r >= 0; r--) {
    for (let c = 0; c <= r; c++) below[c] = triangle[r][c] + Math.min(below[c], below[c + 1]);
  }
  return below[0];
}

console.log(minimumTotal([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]), minimumTotal([[-10]]));
''')

t.code('p_decode', py=r'''
def num_decodings(s):
    prev, cur = 1, (1 if s[0] != "0" else 0)  # ways to read the first i - 1 and the first i digits
    for i in range(1, len(s)):
        nxt = 0
        if s[i] != "0":
            nxt += cur                        # read s[i] as one letter on its own
        if 10 <= int(s[i - 1:i + 1]) <= 26:
            nxt += prev                       # read s[i - 1] and s[i] together as one letter
        prev, cur = cur, nxt
    return cur


for s in ("12", "226", "06", "11106"):
    print(s, num_decodings(s))
''', js=r'''
function numDecodings(s) {
  let prev = 1, cur = s[0] !== "0" ? 1 : 0;   // ways to read the first i - 1 and the first i digits
  for (let i = 1; i < s.length; i++) {
    let nxt = 0;
    if (s[i] !== "0") nxt += cur;             // read s[i] as one letter on its own
    const two = Number(s.slice(i - 1, i + 1));
    if (two >= 10 && two <= 26) nxt += prev;  // read s[i - 1] and s[i] together as one letter
    [prev, cur] = [cur, nxt];
  }
  return cur;
}

for (const s of ["12", "226", "06", "11106"]) console.log(s, numDecodings(s));
''', java=r'''
public class DecodeWays {
    static int numDecodings(String s) {
        int prev = 1, cur = s.charAt(0) != '0' ? 1 : 0;   // ways to read the first i - 1 and the first i digits
        for (int i = 1; i < s.length(); i++) {
            int nxt = 0;
            if (s.charAt(i) != '0') nxt += cur;           // read s[i] as one letter on its own
            int two = Integer.parseInt(s.substring(i - 1, i + 1));
            if (two >= 10 && two <= 26) nxt += prev;      // read s[i - 1] and s[i] together as one letter
            prev = cur;
            cur = nxt;
        }
        return cur;
    }

    public static void main(String[] args) {
        for (String s : new String[]{"12", "226", "06", "11106"}) System.out.println(s + " " + numDecodings(s));
    }
}
''', ts=r'''
function numDecodings(s: string): number {
  let prev = 1, cur = s[0] !== "0" ? 1 : 0;   // ways to read the first i - 1 and the first i digits
  for (let i = 1; i < s.length; i++) {
    let nxt = 0;
    if (s[i] !== "0") nxt += cur;             // read s[i] as one letter on its own
    const two = Number(s.slice(i - 1, i + 1));
    if (two >= 10 && two <= 26) nxt += prev;  // read s[i - 1] and s[i] together as one letter
    [prev, cur] = [cur, nxt];
  }
  return cur;
}

for (const s of ["12", "226", "06", "11106"]) console.log(s, numDecodings(s));
''')

t.code('p_wordbreak', py=r'''
def word_break(s, word_dict):
    words = set(word_dict)
    ok = [True] + [False] * len(s)            # ok[i]: the first i letters split into dictionary words
    for i in range(1, len(s) + 1):
        for j in range(i):
            if ok[j] and s[j:i] in words:     # a good split up to j, then one word from j to i
                ok[i] = True
                break
    return ok[len(s)]


print("true" if word_break("leetcode", ["leet", "code"]) else "false")
print("true" if word_break("applepenapple", ["apple", "pen"]) else "false")
print("true" if word_break("catsandog", ["cats", "dog", "sand", "and", "cat"]) else "false")
''', js=r'''
function wordBreak(s, wordDict) {
  const words = new Set(wordDict);
  const ok = [true, ...new Array(s.length).fill(false)];   // ok[i]: the first i letters split into words
  for (let i = 1; i <= s.length; i++) {
    for (let j = 0; j < i; j++) {
      if (ok[j] && words.has(s.slice(j, i))) { ok[i] = true; break; }   // a good split up to j, then one word
    }
  }
  return ok[s.length];
}

console.log(wordBreak("leetcode", ["leet", "code"]));
console.log(wordBreak("applepenapple", ["apple", "pen"]));
console.log(wordBreak("catsandog", ["cats", "dog", "sand", "and", "cat"]));
''', java=r'''
import java.util.*;

public class WordBreak {
    static boolean wordBreak(String s, List<String> wordDict) {
        Set<String> words = new HashSet<>(wordDict);
        boolean[] ok = new boolean[s.length() + 1];   // ok[i]: the first i letters split into words
        ok[0] = true;
        for (int i = 1; i <= s.length(); i++)
            for (int j = 0; j < i; j++)
                if (ok[j] && words.contains(s.substring(j, i))) { ok[i] = true; break; }   // a good split, then one word
        return ok[s.length()];
    }

    public static void main(String[] args) {
        System.out.println(wordBreak("leetcode", List.of("leet", "code")));
        System.out.println(wordBreak("applepenapple", List.of("apple", "pen")));
        System.out.println(wordBreak("catsandog", List.of("cats", "dog", "sand", "and", "cat")));
    }
}
''', ts=r'''
function wordBreak(s: string, wordDict: string[]): boolean {
  const words = new Set(wordDict);
  const ok: boolean[] = [true, ...new Array(s.length).fill(false)];   // ok[i]: the first i letters split into words
  for (let i = 1; i <= s.length; i++) {
    for (let j = 0; j < i; j++) {
      if (ok[j] && words.has(s.slice(j, i))) { ok[i] = true; break; }   // a good split up to j, then one word
    }
  }
  return ok[s.length];
}

console.log(wordBreak("leetcode", ["leet", "code"]));
console.log(wordBreak("applepenapple", ["apple", "pen"]));
console.log(wordBreak("catsandog", ["cats", "dog", "sand", "and", "cat"]));
''')

# ---------------------------------------------------------------- practice
t.leet(70, 'e', 'p_stairs',
       statement='<p>You climb a staircase of n stairs, one or two stairs at a time. In how many different ways can you reach the top?</p>',
       example='n = 2   →  2\nn = 3   →  3\nn = 10  →  89',
       hint='The last jump came from stair n − 1 or stair n − 2.',
       approach='<p>The ways to reach stair n are the ways to reach n − 1 plus the ways to reach n − 2, which is the Fibonacci pattern. Only the last two counts are needed, so two variables replace the whole table.</p>',
       time='O(n)', space='O(1)')
t.leet(746, 'e', 'p_mincost',
       statement='<p>cost[i] is the price of stepping on stair i. You may start on stair 0 or 1, and climb one or two stairs each time. Return the cheapest way to get past the last stair.</p>',
       example='[10,15,20]                       →  15\n[1,100,1,1,1,100,1,1,100,1]      →  6',
       hint='To stand on stair i you came from i − 1 or i − 2 and paid for that stair.',
       approach='<p>Let best(i) be the cheapest way to stand on stair i, with best(0) = best(1) = 0. Then best(i) = min(best(i − 1) + cost[i − 1], best(i − 2) + cost[i − 2]). The top is stair n. Keep only the last two values.</p>',
       time='O(n)', space='O(1)')
t.leet(198, 'm', 'p_rob',
       statement='<p>Houses in a row hold some money. Robbing two neighbouring houses sets off the alarm. Return the most money you can take.</p>',
       example='[1,2,3,1]    →  4\n[2,7,9,3,1]  →  12\n[2,1,1,2]    →  4',
       hint='At each house: rob it on top of the best from two houses back, or skip it.',
       approach='<p>This is the take or skip lesson. best(i) = max(best(i − 1), best(i − 2) + nums[i]). Two running values are enough, so the extra space is constant.</p>',
       time='O(n)', space='O(1)')
t.leet(62, 'm', 'p_paths',
       statement='<p>A robot starts at the top left of an m by n grid and moves only right or down. How many different paths reach the bottom right?</p>',
       example='m 3, n 7    →  28\nm 3, n 2    →  3\nm 10, n 10  →  48620',
       hint='Paths to a square = paths to the square above + paths to the square on the left.',
       approach='<p>Every square on the top row and left column has exactly one path. Any other square adds the counts from above and from the left. Filling one row at a time, a single array is enough: before the update row[c] still holds the value from above, and row[c − 1] is already the new value on the left.</p>',
       time='O(m × n)', space='O(n)')
t.leet(322, 'h', 'p_coins',
       statement='<p>Given coin values and an amount, return the fewest coins that add up to the amount, using each coin value as often as you like. Return −1 if it cannot be done.</p>',
       example='[1,2,5], 11  →  3\n[2], 3       →  −1\n[1], 0       →  0',
       hint='The best for amount a is one coin plus the best for a − c, for some coin c.',
       approach='<p>Fill best[a] for every amount from 0 up. best[0] = 0, and best[a] = 1 + min over coins c ≤ a of best[a − c]. The value amount + 1 stands for impossible, since no answer can use more coins than the amount itself. Greedy fails here, as the lesson showed with coins 1, 3 and 4.</p>',
       time='O(amount × number of coins)', space='O(amount)')
t.leet(120, 'h', 'p_triangle',
       statement='<p>Walk from the top of a number triangle to the bottom. From position c in one row you may step to c or c + 1 in the next row. Return the smallest possible sum.</p>',
       example='[[2],[3,4],[6,5,7],[4,1,8,3]]  →  11\n[[-10]]                        →  −10',
       hint='Work upwards from the bottom row.',
       approach='<p>Start with a copy of the bottom row. For each row above, every position adds its own value to the smaller of the two values just below it. When the top is reached, one number is left, and it is the answer. Working from the bottom means every position has exactly two choices and no edge cases.</p>',
       time='O(n²) for n rows', space='O(n)')
t.leet(91, 'x', 'p_decode',
       statement='<p>Letters are coded as 1 for A up to 26 for Z. Given a string of digits, return how many ways it can be read back as letters.</p>',
       example='"12"     →  2   (AB or L)\n"226"    →  3\n"06"     →  0\n"11106"  →  2',
       hint='The last letter used either one digit or two digits.',
       approach='<p>Let ways(i) count the readings of the first i digits. The last digit alone is a letter if it is not 0, adding ways(i − 1). The last two digits are a letter if they form 10 to 26, adding ways(i − 2). Like the stairs, only two earlier values are needed. A 0 can only be read as part of 10 or 20.</p>',
       time='O(n)', space='O(1)')
t.leet(139, 'x', 'p_wordbreak',
       statement='<p>Given a string and a list of words, return true if the string can be split into a sequence of words from the list. Words may be used more than once.</p>',
       example='"leetcode", ["leet","code"]                       →  true\n"applepenapple", ["apple","pen"]                  →  true\n"catsandog", ["cats","dog","sand","and","cat"]    →  false',
       hint='ok[i] is true when the first i letters can be split. Which earlier j could lead to i?',
       approach='<p>ok[0] is true, since the empty start needs no words. For each end i, look for a j where ok[j] is true and the letters from j to i form a word. Then ok[i] is true. A set makes each word check quick. The answer is ok[n].</p>',
       time='O(n²) word checks', space='O(n)')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='overlapping-subproblems', emoji='🧠', title='Same question twice? Remember the answer', html='''
<p><b>Dynamic programming</b> solves a big problem by solving smaller versions of it, saving each small answer, and reusing it whenever the same question comes up again. Fibonacci shows why this matters. Plain recursion for fib(n) calls fib(n − 1) and fib(n − 2), and those calls repeat the same work over and over. Watch the red counts grow, then switch on the memo.</p>
<div class="viz" data-viz="pk" data-pk="fibtree"></div>
<div class="c3" data-k="fib" data-label="Fibonacci with and without a memo"></div>
<div class="rule">Dynamic programming fits when a problem has <b>overlapping subproblems</b>, so the same smaller question is asked many times, and <b>optimal substructure</b>, so the best answer is built from best answers to smaller questions.</div>
<span class="eq">fib(n) = fib(n − 1) + fib(n − 2) &nbsp;&nbsp; plain: about 1.6ⁿ calls &nbsp;&nbsp; with a memo: 2n − 1 calls</span>
<div class="tip">Saving answers inside a recursive function is called <b>memoisation</b>, or the top down style. In Python, <code>@functools.cache</code> adds a memo to a function in one line.</div>
'''),
    dict(id='bottom-up', emoji='🐸', title='Fill a table from the bottom up', html='''
<p>Instead of recursing from the top and remembering, you can start from the smallest case and fill a table in order, so every value you need is already there. This is <b>tabulation</b>, or the bottom up style. To count the ways to climb stairs with jumps of 1 or 2, the ways to reach a stair are the ways to reach the two stairs below it, added.</p>
<div class="viz" data-viz="pk" data-pk="stairs"></div>
<div class="c3" data-k="stairs" data-label="Ways to climb the stairs, bottom up"></div>
<div class="exam">Every dynamic programming solution answers four questions. What does one box mean? Which boxes does it depend on? Which boxes are known at the start? In which order are the boxes filled? For the stairs: ways[i], from ways[i − 1] and ways[i − 2], with ways[0] = 1, filled from 1 up to n.</div>
<div class="tip">When a box only needs the last two boxes, two variables can replace the whole table. That turns O(n) space into O(1).</div>
'''),
    dict(id='take-or-skip', emoji='🦹', title='Take it or skip it', html='''
<p>Many problems come down to one decision per item: take it or skip it. A robber walks down a street and cannot rob two neighbouring houses. At each house there are only two choices. Rob it, and add the best from two houses back. Or skip it, and keep the best so far. The larger of the two is the new best.</p>
<div class="viz" data-viz="pk" data-pk="robber"></div>
<div class="c3" data-k="robber" data-label="House robber with the houses picked"></div>
<span class="eq">best(i) = max( best(i − 1), best(i − 2) + money[i] )</span>
<div class="tip">The table gives the best value, not which houses. To recover the choices, walk back from the end and check which option made each box. This walk back works the same way in almost every dynamic programming problem.</div>
'''),
    dict(id='coin-change', emoji='🪙', title='Coin change done right', html='''
<p>In the Greedy chapter, grabbing the biggest coin failed for coins 1, 3 and 4 and the amount 6. Dynamic programming fixes it by solving every amount from 0 up. The best way to make amount a is one coin c plus the best way to make a − c, for whichever coin gives the fewest. Try amounts that cannot be made at all, too.</p>
<div class="viz" data-viz="pk" data-pk="coindp"></div>
<div class="c3" data-k="coindp" data-label="Fewest coins, and the number of ways to pay"></div>
<span class="eq">best(0) = 0 &nbsp;&nbsp; best(a) = 1 + min over coins c ≤ a of best(a − c)</span>
<div class="warn">Counting the ways to pay is a different question. To count each mix of coins once, put the coins in the outer loop. With the amounts in the outer loop, 1 + 2 and 2 + 1 would be counted as two different ways.</div>
'''),
    dict(id='grid-paths', emoji='🗺️', title='Walking across a grid', html='''
<p>Now the table has two dimensions. You walk from the top left square of a grid to the bottom right, moving only right or down, and every square costs its number. A square can only be entered from above or from the left, so its cheapest total is the cheaper of those two totals plus its own cost. Fill the table row by row.</p>
<div class="viz" data-viz="pk" data-pk="grid"></div>
<div class="c3" data-k="grid" data-label="The cheapest walk across a grid"></div>
<span class="eq">cost(r, c) = grid(r, c) + min( cost(r − 1, c), cost(r, c − 1) )</span>
<div class="tip">Change min to a sum and the same table counts the number of paths instead, which is LeetCode 62 in the Practice section.</div>
'''),
    dict(id='knapsack', emoji='🎒', title='The 0/1 knapsack', html='''
<p>In the Greedy chapter, splitting items made the knapsack easy. When every item must be taken whole or left behind, greedy can miss the best answer. The fix is a table with one row per item and one column per bag size. Each box decides one item for one bag: leave it out and copy the box above, or put it in and add its value to the box above that has room for it.</p>
<div class="viz" data-viz="pk" data-pk="knap"></div>
<div class="c3" data-k="knapsack" data-label="0/1 knapsack with the chosen items"></div>
<span class="eq">best(i, w) = max( best(i − 1, w), best(i − 1, w − weight(i)) + value(i) )</span>
<div class="tw"><table class="jt"><tr><th>Bag of 50 kg</th><th>Greedy by value per kg</th><th>Dynamic programming</th></tr>
<tr><td>Gold 10 kg 60, silver 20 kg 100, bronze 30 kg 120</td><td>160</td><td class="yes">220</td></tr></table></div>
<div class="warn">The table has n × W boxes, where W is the bag size. That is fast for small bags. When W is huge, the table gets huge too, which is why the knapsack is still a hard problem in general.</div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem is solved in the Practice section in Python, JavaScript, Java and TypeScript, with line by line replay. For each one, first say what one box of the table means.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>One box means</th></tr>
<tr><td><a href="#lc70">70. Climbing Stairs</a></td><td>Easy</td><td>ways to reach stair i</td></tr>
<tr><td><a href="#lc746">746. Min Cost Climbing Stairs</a></td><td>Easy</td><td>cheapest way to stand on stair i</td></tr>
<tr><td><a href="#lc198">198. House Robber</a></td><td>Medium</td><td>most money from the first i houses</td></tr>
<tr><td><a href="#lc62">62. Unique Paths</a></td><td>Medium</td><td>paths to square (r, c)</td></tr>
<tr><td><a href="#lc322">322. Coin Change</a></td><td>Hard</td><td>fewest coins for amount a</td></tr>
<tr><td><a href="#lc120">120. Triangle</a></td><td>Hard</td><td>best sum from here to the bottom</td></tr>
<tr><td><a href="#lc91">91. Decode Ways</a></td><td>Expert</td><td>readings of the first i digits</td></tr>
<tr><td><a href="#lc139">139. Word Break</a></td><td>Expert</td><td>can the first i letters be split</td></tr></table></div>
'''),
]

VIZ_JS = r'''
(() => {
  const D = PK.defs;
  const ints = (s, lo, hi, min, max) => { const a = PK.parseList(s); return a && a.length >= lo && a.length <= hi && a.every(x => Number.isInteger(x) && x >= min && x <= max) ? a : null; };
  const pick = a => a[Math.floor(Math.random() * a.length)];
  const pl = (k, w) => k + ' ' + w + (k === 1 ? '' : 's');
  const rnd = (lo, hi) => lo + Math.floor(Math.random() * (hi - lo + 1));

  /* ---------- Fibonacci call tree, with and without a memo ---------- */
  D.fibtree = el => PK.widget(el, {
    title: 'The same question, asked again and again', sub: 'Every circle is one call of fib. Plain recursion works out the same small answers many times. A memo remembers them.',
    inputs: [{ k: 'n', label: 'n', type: 'num', val: 5, min: 2, max: 6, w: 70 }, { k: 'mode', label: 'Mode', type: 'seg', val: 'plain', opts: [['plain', '🐌 Plain recursion'], ['memo', '🧠 With a memo']] }],
    check: v => Number.isInteger(v.n) && v.n >= 2 && v.n <= 6 ? '' : 'Pick n from 2 to 6, so the tree still fits on screen.',
    frames: ({ n, mode }) => {
      const memo = mode === 'memo', kids = {}, arg = {}, events = [];
      let id = 0;
      const seen = new Set();
      (function call(k) {                      /* first pass: build the call tree and the order of events */
        const me = 'c' + id++;
        arg[me] = k;
        kids[me] = [null, null];
        if (k < 2) { events.push(['base', me, k]); return [me, k]; }
        if (memo && seen.has(k)) { events.push(['hit', me, k]); return [me, null]; }
        events.push(['enter', me, k]);
        const [l, a] = call(k - 1), [r, b] = call(k - 2);
        kids[me] = [l, r];
        seen.add(k);
        events.push(['done', me, k]);
        return [me, a + b];
      })(n);
      const fib = [0, 1];
      for (let k = 2; k <= n; k++) fib[k] = fib[k - 1] + fib[k - 2];
      const lay = PK.treeLayout(kids, 'c0', x => arg[x], 600, 240);
      const shown = new Set(), ncls = {}, tag = {}, times = new Array(n + 1).fill(0), memoRow = new Array(n + 1).fill('');
      memoRow[0] = 0; memoRow[1] = 1;
      let calls = 0, saved = 0;
      const pic = () => [
        { t: 'graph', label: 'Calls of fib, the number inside is k in fib(k)', w: 600, h: 240, r: 14, nodes: lay.nodes.filter(x => shown.has(x[0])), edges: lay.edges.filter(e => shown.has(e[0]) && shown.has(e[1])), ncls: Object.assign({}, ncls), tag: Object.assign({}, tag) },
        memo ? { t: 'row', label: 'Memo: fib(k) once it is known', cells: memoRow.slice(), cls: Object.fromEntries(memoRow.map((v, k) => [k, v === '' ? '' : 'yes'])) }
             : { t: 'row', label: 'How many times each fib(k) was worked out', cells: times.slice(), cls: Object.fromEntries(times.map((v, k) => [k, v > 1 ? 'no' : v ? 'look' : ''])) },
      ];
      const F = [{ mood: 'think', msg: `fib(${n}) = fib(${n - 1}) + fib(${n - 2}). Each call may start two more. ${memo ? 'This time a memo keeps every answer.' : 'No memory this time.'}`, vars: { calls: 0 }, layers: pic() }];
      for (const [kind, me, k] of events) {
        Object.keys(ncls).forEach(x => { if (ncls[x] === 'cur') ncls[x] = ''; });
        if (kind === 'done') {
          ncls[me] = 'yes'; tag[me] = '=' + fib[k];
          if (memo) memoRow[k] = fib[k];
          F.push({ mood: 'happy', msg: `fib(${k}) = fib(${k - 1}) + fib(${k - 2}) = ${fib[k - 1]} + ${fib[k - 2]} = <b>${fib[k]}</b>.${memo ? ' Saved in the memo.' : ''}`, vars: { calls, saved }, layers: pic() });
          continue;
        }
        shown.add(me); calls++;
        if (kind === 'base') { times[k]++; ncls[me] = 'yes'; tag[me] = '=' + k; F.push({ mood: 'look', msg: `fib(${k}) = ${k}. A base case, no more calls.`, vars: { calls, saved }, layers: pic() }); }
        else if (kind === 'hit') { saved++; ncls[me] = 'win'; tag[me] = '=' + fib[k]; F.push({ mood: 'wow', fx: 'burst', msg: `fib(${k}) again, but the memo already knows it is ${fib[k]}. No new calls below this one.`, vars: { calls, saved }, layers: pic() }); }
        else { times[k]++; ncls[me] = 'cur'; F.push({ mood: times[k] > 1 && !memo ? 'sad' : 'work', msg: times[k] > 1 && !memo ? `fib(${k}) again. This is time number ${times[k]} it gets worked out from scratch.` : `Call fib(${k}). It needs fib(${k - 1}) and fib(${k - 2}).`, vars: { calls, saved }, layers: pic() }); }
      }
      const plainCalls = (function c(k) { return k < 2 ? 1 : 1 + c(k - 1) + c(k - 2); })(n);
      F.push(memo
        ? { mood: 'wow', fx: 'rain', msg: `fib(${n}) = <b>${fib[n]}</b> after only <b>${calls}</b> calls, against ${plainCalls} without the memo. Each fib(k) was worked out once.`, vars: { calls, saved }, layers: pic() }
        : { mood: 'sad', fx: 'shake', msg: `fib(${n}) = <b>${fib[n]}</b>, but it took <b>${calls}</b> calls, and the red counts show repeated work. Switch on the memo and watch the tree shrink.`, vars: { calls }, layers: pic() });
      return F;
    }
  });

  /* ---------- climbing stairs, filled from the bottom up ---------- */
  D.stairs = el => PK.widget(el, {
    title: 'Hop up the stairs', sub: 'The ways to reach a stair are the ways to reach the stairs you could have jumped from, added up.',
    inputs: [{ k: 'n', label: 'Stairs', type: 'num', val: 6, min: 1, max: 12, w: 70 }, { k: 'jumps', label: 'Jumps', type: 'seg', val: '12', opts: [['12', '🐸 1 or 2'], ['123', '🦘 1, 2 or 3']] }],
    random: () => ({ n: rnd(4, 12), jumps: pick(['12', '123']) }),
    check: v => Number.isInteger(v.n) && v.n >= 1 && v.n <= 12 ? '' : 'Pick 1 to 12 stairs.',
    frames: ({ n, jumps }) => {
      const steps = jumps === '12' ? [1, 2] : [1, 2, 3], ways = new Array(n + 1).fill(''), F = [];
      ways[0] = 1;
      const pic = (i, from) => [
        { t: 'bars', label: 'The staircase, stair 0 is the floor', vals: Array.from({ length: n + 1 }, (_, k) => k + 1), max: n + 1, cls: Object.assign({ [i]: 'cur' }, Object.fromEntries((from || []).map(k => [k, 'look']))) },
        { t: 'row', label: 'Ways to reach each stair', cells: ways.slice(), cls: Object.assign(Object.fromEntries(ways.map((v, k) => [k, v === '' ? '' : 'done'])), Object.fromEntries((from || []).map(k => [k, 'look'])), i >= 0 ? { [i]: 'cur' } : {}), ptr: i >= 0 ? { [i]: '🐸' } : {} },
      ];
      F.push({ mood: 'think', msg: `There is exactly 1 way to stand on the floor: do nothing. Jumps allowed: ${steps.join(', ')}.`, vars: { stair: 0, ways: 1 }, layers: pic(0) });
      for (let i = 1; i <= n; i++) {
        const from = steps.map(s => i - s).filter(k => k >= 0);
        ways[i] = from.reduce((a, k) => a + ways[k], 0);
        F.push({ mood: 'work', msg: `Stair ${i}: the last jump came from stair ${from.join(' or ')}. ${from.length > 1 ? from.map(k => ways[k]).join(' + ') + ' = ' : ''}<b>${pl(ways[i], 'way')}</b>.`, vars: { stair: i, ways: ways[i] }, layers: pic(i, from) });
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `<b>${ways[n]}</b> ways to climb ${n} stairs. Each box was worked out once, from boxes that were already done.`, vars: { ways: ways[n] }, layers: pic(n) });
      return F;
    }
  });

  /* ---------- house robber: take or skip ---------- */
  D.robber = el => PK.widget(el, {
    title: 'Rob the street, never two neighbours', sub: 'For each house: rob it and add the best from two houses back, or skip it and keep the best so far.',
    inputs: [{ k: 'h', label: 'Money in each house', type: 'text', val: '2, 7, 9, 3, 1', w: 200 }],
    random: () => ({ h: Array.from({ length: rnd(5, 8) }, () => rnd(1, 20)).join(', ') }),
    check: v => ints(v.h, 2, 9, 0, 99) ? '' : 'Give 2 to 9 amounts from 0 to 99.',
    frames: ({ h }) => {
      const H = ints(h, 2, 9, 0, 99), n = H.length, best = new Array(n).fill(''), F = [];
      const pic = (cls = {}, bcls = {}, ptr = {}) => [
        { t: 'row', label: 'Houses', cells: H.map(x => '🏠' + x), cls, ptr },
        { t: 'row', label: 'The most money from house 0 up to here', cells: best.slice(), cls: bcls },
      ];
      F.push({ mood: 'think', msg: `${n} houses. Robbing two neighbours sets off the alarm. What is the most you can take?`, vars: {}, layers: pic() });
      for (let i = 0; i < n; i++) {
        const take = H[i] + (i >= 2 ? best[i - 2] : 0), skip = i >= 1 ? best[i - 1] : 0;
        best[i] = Math.max(take, skip);
        const bcls = { [i]: take >= skip ? 'yes' : 'sel' };
        if (i >= 2) bcls[i - 2] = 'look';
        if (i >= 1) bcls[i - 1] = take >= skip ? 'done' : 'look';
        F.push({ mood: take >= skip ? 'happy' : 'look',
          msg: `House ${i}: rob it for ${H[i]}${i >= 2 ? ' + ' + best[i - 2] : ''} = ${take}, or skip it and keep ${skip}. ${take >= skip ? 'Rob it' : 'Skip it'}: best so far <b>${best[i]}</b>.`,
          vars: { take, skip, best: best[i] }, layers: pic({ [i]: 'cur' }, bcls, { [i]: '🦹' }) });
      }
      const picked = [];
      for (let i = n - 1; i >= 0;) { if (i === 0 || best[i] !== best[i - 1]) { picked.push(i); i -= 2; } else i -= 1; }
      const cls = Object.fromEntries(H.map((_, i) => [i, picked.includes(i) ? 'win' : 'done']));
      F.push({ mood: 'look', msg: 'Walk back from the end. Where the best went up, that house was robbed, so jump two houses back. Otherwise step one back.', vars: { best: best[n - 1] }, layers: pic(cls, Object.fromEntries(picked.map(i => [i, 'win']))) });
      F.push({ mood: 'wow', fx: 'rain', msg: `Rob houses ${picked.slice().reverse().join(', ')} for <b>${best[n - 1]}</b>. No two of them are neighbours.`, vars: { loot: best[n - 1] }, layers: pic(cls, Object.fromEntries(picked.map(i => [i, 'win']))) });
      return F;
    }
  });

  /* ---------- coin change, the dynamic programming way ---------- */
  D.coindp = el => PK.widget(el, {
    title: 'Fewest coins, for real this time', sub: 'Work out the best for every amount from 0 up. Each amount adds one coin to an amount already solved.',
    inputs: [{ k: 'coins', label: 'Coins', type: 'text', val: '1, 3, 4', w: 140 }, { k: 'amount', label: 'Amount', type: 'num', val: 6, min: 1, max: 20, w: 70 }],
    random: () => pick([{ coins: '1, 3, 4', amount: 6 }, { coins: '1, 5, 6', amount: 10 }, { coins: '2, 5', amount: rnd(6, 13) }, { coins: '3, 7', amount: rnd(8, 15) }, { coins: '1, 7, 10', amount: 14 }]),
    check: v => ints(v.coins, 1, 4, 1, 20) && Number.isInteger(v.amount) && v.amount >= 1 && v.amount <= 20 ? '' : 'Give one to four coin values from 1 to 20 and an amount from 1 to 20.',
    frames: ({ coins, amount }) => {
      const cs = [...new Set(ints(coins, 1, 4, 1, 20))].sort((a, b) => a - b), best = new Array(amount + 1).fill(''), last = [], F = [];
      best[0] = 0;
      const show = v => v === Infinity ? '✗' : v;
      const pic = (cls = {}, ptr = {}) => [{ t: 'row', label: 'Fewest coins for each amount', cells: best.map(show), cls, ptr }];
      F.push({ mood: 'think', msg: `Coins ${cs.join(', ')}. Amount 0 needs 0 coins. Now fill every amount up to ${amount}.`, vars: {}, layers: pic({ 0: 'yes' }) });
      for (let a = 1; a <= amount; a++) {
        const opts = cs.filter(c => c <= a && best[a - c] !== Infinity);
        const cls = Object.fromEntries(best.map((v, k) => [k, k < a ? 'done' : ''])), ptr = {};
        cs.filter(c => c <= a).forEach(c => { cls[a - c] = 'look'; ptr[a - c] = '+' + c; });
        if (!opts.length) {
          best[a] = Infinity;
          cls[a] = 'no';
          F.push({ mood: 'sad', msg: `${a}: no coin lands on an amount that can be made. ${a} is impossible.`, vars: { amount: a }, layers: pic(cls, ptr) });
          continue;
        }
        let c0 = opts[0];
        for (const c of opts) if (best[a - c] < best[a - c0]) c0 = c;
        best[a] = best[a - c0] + 1;
        last[a] = c0;
        cls[a] = 'cur'; cls[a - c0] = 'yes';
        F.push({ mood: 'work', msg: `${a}: try ${opts.map(c => `${a - c} + coin ${c}`).join(', ')}. Best is ${a - c0} (${pl(best[a - c0], 'coin')}) plus a ${c0}: <b>${pl(best[a], 'coin')}</b>.`, vars: { amount: a, coins: best[a] }, layers: pic(cls, ptr) });
      }
      let g = amount, gc = 0;
      for (const c of cs.slice().reverse()) while (g >= c) { g -= c; gc++; }
      const greedy = g === 0 ? `Greedy biggest coin first would use ${gc}.` : 'Greedy biggest coin first would get stuck.';
      if (best[amount] === Infinity) {
        F.push({ mood: 'sad', fx: 'shake', msg: `No mix of ${cs.join(' and ')} makes ${amount}. Even dynamic programming cannot invent a coin. Try another amount.`, vars: {}, layers: pic({ [amount]: 'no' }) });
        return F;
      }
      const used = [], cls = {};
      for (let a = amount; a > 0; a -= last[a]) { used.push(last[a]); cls[a] = 'win'; }
      cls[0] = 'win';
      F.push({ mood: 'wow', fx: 'rain', msg: `${amount} = <b>${used.join(' + ')}</b>, ${used.length} coin${used.length > 1 ? 's' : ''}. Follow the green boxes back to 0. ${greedy}`, vars: { coins: used.length }, layers: pic(cls) });
      return F;
    }
  });

  /* ---------- cheapest walk across a grid ---------- */
  const GRIDS = { a: [[1, 3, 1], [1, 5, 1], [4, 2, 1]], b: [[1, 2, 5, 1], [3, 9, 1, 2], [4, 1, 1, 9], [8, 6, 1, 1]], c: [[2, 9, 1, 1, 1], [1, 9, 1, 9, 1], [1, 1, 1, 9, 1]] };
  D.grid = el => PK.widget(el, {
    title: 'The cheapest walk', sub: 'Walk from the top left to the bottom right, moving only right or down. Each square costs its number.',
    inputs: [{ k: 'g', label: 'Grid', type: 'seg', val: 'a', opts: [['a', '3 × 3'], ['b', '4 × 4'], ['c', 'Snake']] }],
    frames: ({ g }) => {
      const G = GRIDS[g], R = G.length, C = G[0].length, cost = G.map(r => r.map(() => '')), F = [];
      const pic = (cls = {}) => [
        { t: 'grid', label: 'Cost of each square', rows: G, cls, sq: true },
        { t: 'grid', label: 'Cheapest total to reach each square', rows: cost.map(r => r.slice()), cls, sq: true },
      ];
      F.push({ mood: 'think', msg: 'A square can only be reached from above or from the left, so its best total is the cheaper of those two plus its own cost.', vars: {}, layers: pic({ '0,0': 'cur' }) });
      const filled = {};
      for (let r = 0; r < R; r++) for (let c = 0; c < C; c++) {
        const up = r > 0 ? cost[r - 1][c] : null, left = c > 0 ? cost[r][c - 1] : null;
        const from = up === null ? left : left === null ? up : Math.min(up, left);
        cost[r][c] = (from === null ? 0 : from) + G[r][c];
        const cls = Object.assign({}, filled, { [r + ',' + c]: 'cur' });
        if (up !== null) cls[(r - 1) + ',' + c] = up === from ? 'yes' : 'look';
        if (left !== null) cls[r + ',' + (c - 1)] = left === from && !(up === from && up !== null) ? 'yes' : 'look';
        const how = from === null ? `the start costs ${G[0][0]}` : up !== null && left !== null ? `min(up ${up}, left ${left}) + ${G[r][c]} = <b>${cost[r][c]}</b>` : `${from} + ${G[r][c]} = <b>${cost[r][c]}</b>, only one way in`;
        F.push({ mood: 'work', msg: `Square (${r}, ${c}): ${how}.`, vars: { row: r, col: c, total: cost[r][c] }, layers: pic(cls) });
        filled[r + ',' + c] = 'done';
      }
      const cls = Object.assign({}, filled), path = [];
      for (let r = R - 1, c = C - 1; ;) {
        cls[r + ',' + c] = 'win'; path.push(G[r][c]);
        if (r === 0 && c === 0) break;
        if (c === 0 || (r > 0 && cost[r - 1][c] <= cost[r][c - 1])) r--; else c--;
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `Cheapest walk: <b>${path.reverse().join(' + ')} = ${cost[R - 1][C - 1]}</b>. Walking back through the cheaper neighbour traces it out.`, vars: { total: cost[R - 1][C - 1] }, layers: pic(cls) });
      return F;
    }
  });

  /* ---------- 0/1 knapsack table ---------- */
  const KS = { small: [[1, 3, 4, 5], [1, 4, 5, 7], 7], gems: [[2, 3, 4], [3, 4, 6], 6], trap: [[5, 4, 3], [10, 7, 6], 7] };
  D.knap = el => PK.widget(el, {
    title: 'Pack the bag, whole items only', sub: 'Row i uses the first i items. Each box: leave the item out (the box above), or put it in (above, w kg to the left, plus its value).',
    inputs: [{ k: 's', label: 'Items', type: 'seg', val: 'small', opts: [['small', '🎒 Four items'], ['gems', '💎 Gems'], ['trap', '🪤 Greedy trap']] }],
    frames: ({ s }) => {
      const [W, V, cap] = KS[s], n = W.length, F = [];
      const best = Array.from({ length: n + 1 }, (_, i) => new Array(cap + 1).fill(i === 0 ? 0 : ''));
      const rlab = ['none'].concat(W.map((w, i) => `#${i} ${w}kg=${V[i]}`)), clab = Array.from({ length: cap + 1 }, (_, w) => w);
      const pic = cls => [{ t: 'grid', label: 'Best value: rows add one item at a time (#item weight=value), columns are bag sizes in kg', rows: best.map(r => r.slice()), rlab, clab, cls }];
      const done = {};
      for (let w = 0; w <= cap; w++) done['0,' + w] = 'done';
      F.push({ mood: 'think', msg: `${n} items, a bag of ${cap} kg. With no items the best is 0 everywhere.`, vars: {}, layers: pic(Object.assign({}, done)) });
      for (let i = 1; i <= n; i++) {
        const wt = W[i - 1], val = V[i - 1], cls = Object.assign({}, done);
        for (let w = 0; w < Math.min(wt, cap + 1); w++) { best[i][w] = best[i - 1][w]; cls[i + ',' + w] = 'sel'; }
        F.push({ mood: 'look', msg: `Item ${i - 1} weighs ${wt} kg, so bags under ${wt} kg cannot hold it. They copy the row above.`, vars: { item: i - 1 }, layers: pic(cls) });
        for (let w = 0; w < Math.min(wt, cap + 1); w++) done[i + ',' + w] = 'done';
        for (let w = wt; w <= cap; w++) {
          const out = best[i - 1][w], into = best[i - 1][w - wt] + val;
          best[i][w] = Math.max(out, into);
          const c2 = Object.assign({}, done, { [(i - 1) + ',' + w]: 'look', [(i - 1) + ',' + (w - wt)]: 'look', [i + ',' + w]: into > out ? 'yes' : 'cur' });
          F.push({ mood: into > out ? 'happy' : 'work', msg: `Bag ${w} kg: leave it out for ${out}, or put it in for ${best[i - 1][w - wt]} + ${val} = ${into}. ${into > out ? 'Put it in' : 'Leave it out'}: <b>${best[i][w]}</b>.`, vars: { item: i - 1, bag: w, best: best[i][w] }, layers: pic(c2) });
          done[i + ',' + w] = 'done';
        }
      }
      const cls = Object.assign({}, done), chosen = [];
      let w = cap;
      for (let i = n; i > 0; i--) {
        if (best[i][w] !== best[i - 1][w]) { cls[i + ',' + w] = 'win'; chosen.push(i - 1); w -= W[i - 1]; }
        else cls[i + ',' + w] = 'no';
      }
      chosen.reverse();
      const order = W.map((_, i) => i).sort((a, b) => V[b] / W[b] - V[a] / W[a]);
      let gw = 0, gv = 0;
      for (const i of order) if (gw + W[i] <= cap) { gw += W[i]; gv += V[i]; }
      F.push({ mood: 'wow', fx: 'rain', msg: `Best value <b>${best[n][cap]}</b>: take item${chosen.length > 1 ? 's' : ''} ${chosen.join(' and ')}. Green boxes are where an item went in, walking up from the corner. Greedy by value per kg would get ${gv}${gv < best[n][cap] ? ', which is less' : ', the same here'}.`, vars: { best: best[n][cap] }, layers: pic(cls) });
      return F;
    }
  });
})();
'''

INFO = {
    'title': 'Solve each small question once, then reuse it',
    'panels': [
        {'s': [['e', '🧠'], ['t', 'memo', {'b': 1}]], 'h': 'Top down', 't': 'Recursion that remembers.', 'more': 'Easy to write from the formula.'},
        {'s': [['e', '📋'], ['t', 'table', {'b': 1}]], 'h': 'Bottom up', 't': 'Fill boxes from the smallest.', 'more': 'No recursion depth limit.'},
        {'s': [['e', '🦹'], ['t', 'take or skip', {'b': 1}]], 'h': 'One choice per item', 't': 'Max of the two options.', 'more': 'Walk back to see the choices.'},
        {'s': [['e', '🎒'], ['t', 'items × bag size', {'b': 1}]], 'h': '0/1 knapsack', 't': 'A 2D table of decisions.', 'more': 'Beats greedy on whole items.'},
    ],
    'remember': 'Say what one box means, which boxes it depends on, which boxes are known at the start, and the order to fill them. Once those four answers are clear, the code is a loop over the table.',
}

REAL = [
    ['🧬', 'Comparing DNA', 'Biologists line up gene sequences with dynamic programming tables, the same idea as the edit distance in the next chapter.'],
    ['📝', 'Spell checkers and diff tools', 'Suggesting a word or showing the changes between two files means filling a table of the cheapest edits.'],
    ['🚚', 'Loading trucks and budgets', 'Choosing which parcels or projects fit a weight or money limit for the most value is a knapsack problem.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to dynamic programming, part one. The idea is simple: solve each small question once, save the answer, and reuse it. You will watch Fibonacci calls repeat and then shrink with a memo, hop up stairs with a table, rob houses without waking the neighbours, fix the coin problem that greedy got wrong, find the cheapest walk across a grid, and pack a bag with the 0/1 knapsack.'},
    {'id': 'overlapping-subproblems', 'h': 'Overlapping subproblems', 'en': 'Plain recursion for Fibonacci asks the same questions again and again, so the number of calls grows very fast. A memo saves every answer the first time it is worked out. After that, a repeated question is answered at once, and fib of n needs only about two n calls.'},
    {'id': 'bottom-up', 'h': 'Bottom up tables', 'en': 'A bottom up solution starts from the smallest case and fills a table in order, so every value it needs is already known. To count the ways to climb stairs with jumps of one or two, add the ways to reach the two stairs below.'},
    {'id': 'take-or-skip', 'h': 'Take or skip', 'en': 'In house robber, each house gives two choices. Rob it and add the best from two houses back, or skip it and keep the best so far. The larger is the new best. Walking back from the end shows which houses were robbed.'},
    {'id': 'coin-change', 'h': 'Coin change', 'en': 'To make an amount with the fewest coins, solve every smaller amount first. The best for an amount is one coin plus the best for what is left. This finds three plus three for six with coins one, three and four, where greedy used three coins.'},
    {'id': 'grid-paths', 'h': 'Grid paths', 'en': 'When you can only move right or down, a square is reached from above or from the left. Its cheapest total is the cheaper of those two plus its own cost. Fill the grid row by row, then walk back to trace the path.'},
    {'id': 'knapsack', 'h': 'The 0/1 knapsack', 'en': 'For whole items, build a table with one row per item and one column per bag size. Each box either leaves the item out and copies the box above, or puts it in and adds its value to the box above that still has room.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from climbing stairs to breaking a string into dictionary words. Each one is solved in Python, JavaScript, Java and TypeScript, and you can replay every solution line by line.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. For each problem, first say in words what one box of the table means. Then find which earlier boxes it needs. The code usually follows in a few lines. Open the hint if you are stuck.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'What is the main idea of dynamic programming?', 'o': ['Try random answers', 'Solve each smaller question once, save it and reuse it', 'Always take the biggest item', 'Sort the input first'], 'a': 1, 'hint': 'Think of the memo.', 'why': 'Saving answers to repeated subproblems is what makes dynamic programming fast.'},
    {'lv': 'e', 'q': 'What is a memo?', 'o': ['A comment in the code', 'A store of answers already worked out', 'A kind of loop', 'A sorting method'], 'a': 1, 'hint': 'It remembers.', 'why': 'A memo, usually a dictionary or an array, keeps answers so that repeated calls return at once.'},
    {'lv': 'e', 'q': 'With jumps of 1 or 2, how many ways are there to climb 4 stairs?', 'o': ['4', '5', '6', '8'], 'a': 1, 'hint': 'Ways: 1, 1, 2, 3, ...', 'why': 'ways(4) = ways(3) + ways(2) = 3 + 2 = 5.'},
    {'lv': 'e', 'q': 'What is the bottom up style also called?', 'o': ['Memoisation', 'Tabulation', 'Backtracking', 'Hashing'], 'a': 1, 'hint': 'It fills a table.', 'why': 'Tabulation fills a table from the smallest case upwards.'},
    {'lv': 'm', 'q': 'How many calls does plain recursion make for fib(5)?', 'o': ['5', '9', '15', '25'], 'a': 2, 'hint': 'Run the animation without the memo.', 'why': 'calls(n) = 1 + calls(n − 1) + calls(n − 2), which gives 15 for n = 5.'},
    {'lv': 'm', 'q': 'In house robber, which formula gives the best up to house i?', 'o': ['best(i − 1) + money[i]', 'max(best(i − 1), best(i − 2) + money[i])', 'min(best(i − 1), money[i])', 'best(i − 2) + best(i − 1)'], 'a': 1, 'hint': 'Skip it, or rob it on top of two houses back.', 'why': 'Skipping keeps best(i − 1). Robbing adds money[i] to best(i − 2), since the neighbour cannot be robbed.'},
    {'lv': 'm', 'q': 'With coins 1, 3 and 4, what is the fewest number of coins for 6?', 'o': ['1', '2', '3', '6'], 'a': 1, 'hint': 'Greedy says 3. Is there better?', 'why': '3 + 3 uses two coins.'},
    {'lv': 'm', 'q': 'In the grid walk, from which squares can square (r, c) be entered?', 'o': ['Any neighbour', 'Only from above or from the left', 'Only from the right', 'Only diagonally'], 'a': 1, 'hint': 'Moves go right or down.', 'why': 'Moving right enters from the left, and moving down enters from above.'},
    {'lv': 'h', 'q': 'Why put coins in the outer loop when counting the ways to pay?', 'o': ['It is faster', 'So that 1 + 2 and 2 + 1 are counted once, as the same mix', 'So that greedy works', 'It makes no difference'], 'a': 1, 'hint': 'Order of coins in a mix.', 'why': 'With coins outside, each mix is built in one fixed coin order, so it is counted once.'},
    {'lv': 'h', 'q': 'In the 0/1 knapsack table, what does best(i, w) mean?', 'o': ['The weight of item i', 'The best value using the first i items in a bag of w kg', 'The number of items', 'The value per kg'], 'a': 1, 'hint': 'Rows are items, columns are bag sizes.', 'why': 'Each box answers one smaller question: the first i items with w kg of room.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'ways = [1, 1]\nfor i in range(2, 6):\n    ways.append(ways[-1] + ways[-2])\nprint(ways[5])', 'o': ['5', '8', '13', '6'], 'a': 1, 'hint': '1, 1, 2, 3, 5, ...', 'why': 'The list becomes 1 1 2 3 5 8, so ways[5] is 8.'},
    {'lv': 'h', 'q': 'Bars of 10, 20 and 30 kg worth 60, 100 and 120, a bag of 50 kg, whole items only. What is the best value?', 'o': ['160', '180', '220', '240'], 'a': 2, 'hint': 'Greedy gets 160. Try silver and bronze.', 'why': 'Silver and bronze weigh exactly 50 kg and are worth 220.'},
    {'lv': 'x', 'q': 'Fibonacci with a memo makes how many calls for fib(n), n ≥ 1?', 'o': ['n', '2n − 1', 'n²', '2ⁿ'], 'a': 1, 'hint': 'fib(10) used 19.', 'why': 'Each k from 2 to n makes two calls, one of which hits the memo, giving 2n − 1 in total.'},
    {'lv': 'x', 'q': 'How many ways can "226" be decoded?', 'o': ['1', '2', '3', '4'], 'a': 2, 'hint': '2 2 6, 22 6, 2 26.', 'why': 'BBF, VF and BZ, three readings.'},
    {'lv': 'x', 'q': 'Why is the 0/1 knapsack still a hard problem in general?', 'o': ['The table has n × W boxes, and W can be enormous', 'Because it needs sorting', 'Because greedy always works', 'Because it uses recursion'], 'a': 0, 'hint': 'Count the boxes.', 'why': 'The work grows with the bag size W, not just with the number of items, so a huge W makes the table impractical.'},
    {'lv': 'x', 'q': 'Which of these is a sign that dynamic programming may help?', 'o': ['Every subproblem is different', 'The same smaller question is asked many times', 'The input is sorted', 'There is only one item'], 'a': 1, 'hint': 'Look at the red counts in the Fibonacci tree.', 'why': 'Overlapping subproblems are what dynamic programming saves time on.'},
]

CALC = [
    {'lv': 'e', 'q': 'With jumps of 1 or 2, how many ways are there to climb 6 stairs?', 'ans': '13', 'hint': 'Keep adding the last two.', 'steps': ['Ways: 1, 1, 2, 3, 5, 8, 13 for stairs 0 to 6.']},
    {'lv': 'e', 'q': 'House robber with money 2, 7, 9, 3, 1. What is the most you can take?', 'ans': '12', 'hint': 'Best so far: 2, 7, 11, ...', 'steps': ['Best: 2, 7, 11, 11, 12.', 'Rob houses 0, 2 and 4: <span class="eq">2 + 9 + 1 = 12</span>']},
    {'lv': 'm', 'q': 'With jumps of 1, 2 or 3, how many ways are there to climb 5 stairs?', 'ans': '13', 'hint': 'Add the last three.', 'steps': ['Ways: 1, 1, 2, 4, 7, 13 for stairs 0 to 5.', '<span class="eq">7 + 4 + 2 = 13</span>']},
    {'lv': 'm', 'q': 'Coins 1, 5 and 6. What is the fewest number of coins for 10?', 'ans': '2', 'hint': 'Greedy takes 6 first.', 'steps': ['Greedy: 6 + 1 + 1 + 1 + 1, five coins.', '<span class="eq">5 + 5 = 10</span>, two coins.']},
    {'lv': 'h', 'q': 'In how many ways can you pay 5 with coins 1, 2 and 5, counting each mix once?', 'ans': '4', 'hint': 'List them.', 'steps': ['5, 2 + 2 + 1, 2 + 1 + 1 + 1, 1 + 1 + 1 + 1 + 1.', 'Four mixes.']},
    {'lv': 'h', 'q': 'Grid [[1,3,1],[1,5,1],[4,2,1]], moving right or down. What is the cheapest total?', 'ans': '7', 'hint': 'Fill the first row and column first.', 'steps': ['Totals row by row: 1 4 5, 2 7 6, 6 8 7.', 'Path <span class="eq">1 + 3 + 1 + 1 + 1 = 7</span>']},
    {'lv': 'x', 'q': 'How many paths does a robot have from the top left to the bottom right of a 3 by 3 grid, moving right or down?', 'ans': '6', 'hint': 'Add above and left.', 'steps': ['Rows of counts: 1 1 1, 1 2 3, 1 3 6.', 'The bottom right holds 6.']},
    {'lv': 'x', 'q': 'Weights 1, 3, 4, 5 worth 1, 4, 5, 7, a bag of 7, whole items. What is the best value?', 'ans': '9', 'hint': 'Run the knapsack animation.', 'steps': ['The 3 kg and 4 kg items fill 7 kg exactly.', '<span class="eq">4 + 5 = 9</span>, more than 7 + 1 = 8 from the 5 kg and 1 kg items.']},
]

TALK = {
    'overlapping-subproblems': 'Dynamic programming sounds grand, but the idea behind it is plain common sense: never work out the same thing twice. Take the Fibonacci numbers, where each number is the sum of the two before it. A direct recursive function for fib of five calls fib of four and fib of three. But fib of four also calls fib of three, so that work is done twice. Further down, fib of two is worked out three times. In the animation, the red counts show this repeated work, and the total grows very quickly as n grows. Now add a memo, which is simply a dictionary or an array that stores each answer the first time it is found. Before doing any work, the function checks the memo. If the answer is there, it returns at once. With the memo, fib of five needs nine calls instead of fifteen, and fib of fifty needs just ninety nine.',
    'bottom-up': 'A memo works from the top down. You ask for the big answer, and recursion reaches down to the small ones. You can also go the other way. Start with the smallest case, which you know for certain, and fill a table in order, so that every value you need has already been worked out. This is called tabulation, or the bottom up style. Think about climbing stairs, where each jump is one stair or two. How many ways are there to reach stair six? The last jump came either from stair five or from stair four. So the ways to reach stair six are the ways to reach stair five plus the ways to reach stair four. Start with one way to stand on the floor, and fill the boxes one after another. You get one, one, two, three, five, eight, thirteen. Each box is filled once, and the whole job takes a single loop.',
    'take-or-skip': 'Many dynamic programming problems come down to a single decision for each item: take it or skip it. Here is a classic. A robber walks down a street of houses, and each house holds some money. Robbing two houses that stand next to each other sets off the alarm. At each house, the robber has two choices. If they rob this house, they cannot have robbed the house just before, so they add this money to the best total from two houses back. If they skip this house, the best total simply stays the same as before. The new best is the larger of the two. In the example with two, seven, nine, three and one, the best totals grow as two, seven, eleven, eleven and twelve. To find which houses were robbed, walk back from the end. Wherever the best went up, that house was robbed, so jump back two houses and keep going.',
    'coin-change': 'Remember the coin problem from the greedy chapter. With coins of one, three and four, grabbing the biggest coin first made six as four plus one plus one, which is three coins, when three plus three needs only two. Dynamic programming fixes this by being patient. Instead of attacking six directly, it works out the fewest coins for every amount from zero upwards. Zero needs no coins. For any other amount, look at each coin that fits. Using that coin leaves a smaller amount, and its best answer is already in the table. Add one coin to it, and keep the smallest result. For six, using a three leaves three, which needs just one coin, so six needs two. Some amounts cannot be made at all, such as seven with only twos and fours, and the table marks those as impossible. A small change to the loops counts the ways to pay instead.',
    'grid-paths': 'Now the table grows a second dimension. Picture a grid of squares, each with a cost written on it. You start in the top left corner and want to reach the bottom right, moving only right or down, and you pay the cost of every square you step on. What is the cheapest walk? Think about any single square. Because you only move right or down, you must have arrived either from the square above or from the square on the left. So the cheapest total for this square is its own cost plus the cheaper of those two totals. The top row can only be reached from the left, and the left column only from above, so those are easy. Fill the rest row by row. When the bottom right box is filled, you have the answer. To see the actual path, start at the end and keep stepping back to the cheaper neighbour.',
    'knapsack': 'The fractional knapsack from the greedy chapter was easy because items could be cut. Now every item must be taken whole or left behind, and greedy can miss the best answer. Build a table with one row for each item and one column for each bag size, from zero up to the full bag. One box answers a small question: using only the first few items, what is the best value that fits in this size of bag? For each box there are two choices. Leave the item out, and the answer is the box just above. Or put the item in, if it fits. Then its value is added to the box in the row above, moved left by the item weight, because that much room is now used. Keep the larger choice. With bars worth sixty, one hundred and one hundred and twenty, the table finds two hundred and twenty, where greedy found only one hundred and sixty.',
    'leetcode': 'The LeetCode problems in this chapter all follow the same pattern: decide what one box of the table means, then find the boxes it depends on. The easy problems climb stairs, first counting the ways and then finding the cheapest way when every stair has a price. The medium problems rob a street of houses without touching two neighbours, and count the paths a robot can take across a grid. The hard problems make an amount with the fewest coins, and find the smallest sum from the top of a number triangle to the bottom, working upwards from the last row. The expert problems count the ways to decode a string of digits back into letters, where a zero needs special care, and decide whether a string can be broken into dictionary words. Each one is solved in four languages, and you can replay every line.',
}

T = t.finish({
    'slug': 'dynamic-programming', 'title': 'Dynamic Programming 1: Memos and Tables', 'short': 'Dynamic programming 1', 'emoji': '🧠', 'topic': 'dynamic-programming', 'prefix': 'dsadp1',
    'module': ('🧠', 'Greedy and dynamic programming'),
    'lead': 'Never work out the same thing twice. Watch Fibonacci calls repeat and then shrink with a memo, hop up stairs with a table, rob houses without waking the neighbours, fix the coin problem that greedy got wrong, find the cheapest walk across a grid and pack a bag with the 0/1 knapsack.',
    'desc': 'Dynamic programming in DSA, part 1: overlapping subproblems and memoisation, bottom up tabulation, take or skip with house robber, coin change, grid paths and the 0/1 knapsack, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 24,
    'summary': 'Overlapping subproblems and memoisation, bottom up tables with climbing stairs, take or skip with house robber, coin change done right, the cheapest walk across a grid and the 0/1 knapsack with its walk back. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['dynamic programming', 'dp', 'memoization', 'memoisation', 'tabulation', 'top down', 'bottom up', 'overlapping subproblems', 'optimal substructure', 'fibonacci', 'climbing stairs', 'house robber', 'coin change', 'unique paths', 'minimum path sum', '0/1 knapsack', 'decode ways', 'word break'],
    'added': '2026-11-23',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS, 'css': '',
    'prev': ('greedy', 'greedy', '🪙 Greedy algorithms'),
    'next': None,
})
