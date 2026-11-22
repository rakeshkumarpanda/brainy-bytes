# Backtracking: choose, explore, unchoose, the decision tree, subsets and permutations, pruning with
# combination sum, N-Queens, a small Sudoku solver and searching a word in a grid.
from kit4 import Topic

t = Topic()

# ---------------------------------------------------------------- lesson programs
t.code('maze', py=r'''
MAZE = [".....",
        ".###.",
        ".#...",
        ".#.#.",
        ".###."]
N = len(MAZE)
MOVES = [(1, 0, "D"), (0, 1, "R"), (-1, 0, "U"), (0, -1, "L")]
seen = {(0, 0)}
path = []
backtracks = 0


def walk(r, c):
    global backtracks
    if r == N - 1 and c == N - 1:
        return True                           # reached the cheese
    for dr, dc, step in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < N and 0 <= nc < N and MAZE[nr][nc] == "." and (nr, nc) not in seen:
            seen.add((nr, nc))                # choose: step into the square
            path.append(step)
            if walk(nr, nc):                  # explore from there
                return True
            path.pop()                        # unchoose: step back out
            seen.remove((nr, nc))
    backtracks += 1                           # every way out of here failed
    return False


print("found" if walk(0, 0) else "no way out")
print("path", "".join(path))
print("squares backed out of", backtracks)
''', js=r'''
const MAZE = [".....",
              ".###.",
              ".#...",
              ".#.#.",
              ".###."];
const N = MAZE.length;
const MOVES = [[1, 0, "D"], [0, 1, "R"], [-1, 0, "U"], [0, -1, "L"]];
const seen = new Set(["0,0"]);
const path = [];
let backtracks = 0;

function walk(r, c) {
  if (r === N - 1 && c === N - 1) return true;     // reached the cheese
  for (const [dr, dc, step] of MOVES) {
    const nr = r + dr, nc = c + dc, key = nr + "," + nc;
    if (nr >= 0 && nr < N && nc >= 0 && nc < N && MAZE[nr][nc] === "." && !seen.has(key)) {
      seen.add(key);                               // choose: step into the square
      path.push(step);
      if (walk(nr, nc)) return true;               // explore from there
      path.pop();                                  // unchoose: step back out
      seen.delete(key);
    }
  }
  backtracks++;                                    // every way out of here failed
  return false;
}

console.log(walk(0, 0) ? "found" : "no way out");
console.log("path", path.join(""));
console.log("squares backed out of", backtracks);
''', java=r'''
import java.util.*;

public class Maze {
    static final String[] MAZE = {".....",
                                  ".###.",
                                  ".#...",
                                  ".#.#.",
                                  ".###."};
    static final int N = MAZE.length;
    static final int[][] D = {{1, 0}, {0, 1}, {-1, 0}, {0, -1}};
    static final String STEP = "DRUL";
    static boolean[][] seen = new boolean[N][N];
    static StringBuilder path = new StringBuilder();
    static int backtracks = 0;

    static boolean walk(int r, int c) {
        if (r == N - 1 && c == N - 1) return true;          // reached the cheese
        for (int k = 0; k < 4; k++) {
            int nr = r + D[k][0], nc = c + D[k][1];
            if (nr >= 0 && nr < N && nc >= 0 && nc < N && MAZE[nr].charAt(nc) == '.' && !seen[nr][nc]) {
                seen[nr][nc] = true;                         // choose: step into the square
                path.append(STEP.charAt(k));
                if (walk(nr, nc)) return true;               // explore from there
                path.deleteCharAt(path.length() - 1);        // unchoose: step back out
                seen[nr][nc] = false;
            }
        }
        backtracks++;                                        // every way out of here failed
        return false;
    }

    public static void main(String[] args) {
        seen[0][0] = true;
        System.out.println(walk(0, 0) ? "found" : "no way out");
        System.out.println("path " + path);
        System.out.println("squares backed out of " + backtracks);
    }
}
''', ts=r'''
const MAZE: string[] = [".....",
                        ".###.",
                        ".#...",
                        ".#.#.",
                        ".###."];
const N = MAZE.length;
const MOVES: Array<[number, number, string]> = [[1, 0, "D"], [0, 1, "R"], [-1, 0, "U"], [0, -1, "L"]];
const seen = new Set<string>(["0,0"]);
const path: string[] = [];
let backtracks = 0;

function walk(r: number, c: number): boolean {
  if (r === N - 1 && c === N - 1) return true;     // reached the cheese
  for (const [dr, dc, step] of MOVES) {
    const nr = r + dr, nc = c + dc, key = nr + "," + nc;
    if (nr >= 0 && nr < N && nc >= 0 && nc < N && MAZE[nr][nc] === "." && !seen.has(key)) {
      seen.add(key);                               // choose: step into the square
      path.push(step);
      if (walk(nr, nc)) return true;               // explore from there
      path.pop();                                  // unchoose: step back out
      seen.delete(key);
    }
  }
  backtracks++;                                    // every way out of here failed
  return false;
}

console.log(walk(0, 0) ? "found" : "no way out");
console.log("path", path.join(""));
console.log("squares backed out of", backtracks);
''')

t.code('subsets', py=r'''
def subsets(items):
    result, chosen = [], []

    def go(i):
        if i == len(items):
            result.append(chosen[:])          # a leaf of the decision tree: one finished subset
            return
        chosen.append(items[i])               # choose: take items[i]
        go(i + 1)
        chosen.pop()                          # unchoose
        go(i + 1)                             # the other branch: skip items[i]

    go(0)
    return result


all_sets = subsets(["a", "b", "c"])
print(" ".join("{" + ",".join(s) + "}" for s in all_sets))
print(len(all_sets), "subsets")
''', js=r'''
function subsets(items) {
  const result = [], chosen = [];
  function go(i) {
    if (i === items.length) {
      result.push([...chosen]);             // a leaf of the decision tree: one finished subset
      return;
    }
    chosen.push(items[i]);                  // choose: take items[i]
    go(i + 1);
    chosen.pop();                           // unchoose
    go(i + 1);                              // the other branch: skip items[i]
  }
  go(0);
  return result;
}

const allSets = subsets(["a", "b", "c"]);
console.log(allSets.map(s => "{" + s.join(",") + "}").join(" "));
console.log(allSets.length, "subsets");
''', java=r'''
import java.util.*;

public class Subsets {
    static List<List<String>> result = new ArrayList<>();
    static List<String> chosen = new ArrayList<>();

    static void go(String[] items, int i) {
        if (i == items.length) {
            result.add(new ArrayList<>(chosen));       // a leaf of the decision tree: one finished subset
            return;
        }
        chosen.add(items[i]);                          // choose: take items[i]
        go(items, i + 1);
        chosen.remove(chosen.size() - 1);              // unchoose
        go(items, i + 1);                              // the other branch: skip items[i]
    }

    public static void main(String[] args) {
        go(new String[]{"a", "b", "c"}, 0);
        StringBuilder sb = new StringBuilder();
        for (List<String> s : result) {
            if (sb.length() > 0) sb.append(' ');
            sb.append('{').append(String.join(",", s)).append('}');
        }
        System.out.println(sb);
        System.out.println(result.size() + " subsets");
    }
}
''', ts=r'''
function subsets(items: string[]): string[][] {
  const result: string[][] = [], chosen: string[] = [];
  function go(i: number): void {
    if (i === items.length) {
      result.push([...chosen]);             // a leaf of the decision tree: one finished subset
      return;
    }
    chosen.push(items[i]);                  // choose: take items[i]
    go(i + 1);
    chosen.pop();                           // unchoose
    go(i + 1);                              // the other branch: skip items[i]
  }
  go(0);
  return result;
}

const allSets = subsets(["a", "b", "c"]);
console.log(allSets.map(s => "{" + s.join(",") + "}").join(" "));
console.log(allSets.length, "subsets");
''')

t.code('perms', py=r'''
def permutations(items):
    result, slot, used = [], [], [False] * len(items)

    def go():
        if len(slot) == len(items):
            result.append("".join(slot))      # every slot is filled
            return
        for i, x in enumerate(items):
            if used[i]:
                continue                      # already sitting in an earlier slot
            used[i] = True                    # choose x for this slot
            slot.append(x)
            go()
            slot.pop()                        # unchoose, so the next letter can try this slot
            used[i] = False

    go()
    return result


p = permutations(["a", "b", "c"])
print(" ".join(p))
print(len(p), "orders, which is 3! = 6")
''', js=r'''
function permutations(items) {
  const result = [], slot = [], used = items.map(() => false);
  function go() {
    if (slot.length === items.length) {
      result.push(slot.join(""));           // every slot is filled
      return;
    }
    items.forEach((x, i) => {
      if (used[i]) return;                  // already sitting in an earlier slot
      used[i] = true;                       // choose x for this slot
      slot.push(x);
      go();
      slot.pop();                           // unchoose, so the next letter can try this slot
      used[i] = false;
    });
  }
  go();
  return result;
}

const p = permutations(["a", "b", "c"]);
console.log(p.join(" "));
console.log(p.length, "orders, which is 3! = 6");
''', java=r'''
import java.util.*;

public class Permutations {
    static List<String> result = new ArrayList<>();
    static StringBuilder slot = new StringBuilder();

    static void go(char[] items, boolean[] used) {
        if (slot.length() == items.length) {
            result.add(slot.toString());               // every slot is filled
            return;
        }
        for (int i = 0; i < items.length; i++) {
            if (used[i]) continue;                     // already sitting in an earlier slot
            used[i] = true;                            // choose items[i] for this slot
            slot.append(items[i]);
            go(items, used);
            slot.deleteCharAt(slot.length() - 1);      // unchoose, so the next letter can try this slot
            used[i] = false;
        }
    }

    public static void main(String[] args) {
        char[] items = {'a', 'b', 'c'};
        go(items, new boolean[items.length]);
        System.out.println(String.join(" ", result));
        System.out.println(result.size() + " orders, which is 3! = 6");
    }
}
''', ts=r'''
function permutations(items: string[]): string[] {
  const result: string[] = [], slot: string[] = [], used: boolean[] = items.map(() => false);
  function go(): void {
    if (slot.length === items.length) {
      result.push(slot.join(""));           // every slot is filled
      return;
    }
    items.forEach((x, i) => {
      if (used[i]) return;                  // already sitting in an earlier slot
      used[i] = true;                       // choose x for this slot
      slot.push(x);
      go();
      slot.pop();                           // unchoose, so the next letter can try this slot
      used[i] = false;
    });
  }
  go();
  return result;
}

const p = permutations(["a", "b", "c"]);
console.log(p.join(" "));
console.log(p.length, "orders, which is 3! = 6");
''')

t.code('combsum', py=r'''
tries = 0


def combination_sum(nums, target, prune):
    nums = sorted(nums)
    result, chosen = [], []

    def go(start, left):
        global tries
        if left == 0:
            result.append(chosen[:])
            return
        for i in range(start, len(nums)):
            tries += 1
            if nums[i] > left:
                if prune:
                    break                     # sorted, so every later number is too big as well
                continue
            chosen.append(nums[i])
            go(i, left - nums[i])             # i, not i + 1: a number may be used again
            chosen.pop()

    go(0, target)
    return result


for prune in (False, True):
    tries = 0
    res = combination_sum([2, 3, 6, 7], 7, prune)
    label = "with pruning" if prune else "no pruning  "
    print(label, " | ".join("+".join(map(str, c)) for c in res), " tries", tries)
''', js=r'''
let tries = 0;

function combinationSum(nums, target, prune) {
  nums = [...nums].sort((a, b) => a - b);
  const result = [], chosen = [];
  function go(start, left) {
    if (left === 0) {
      result.push([...chosen]);
      return;
    }
    for (let i = start; i < nums.length; i++) {
      tries++;
      if (nums[i] > left) {
        if (prune) break;                   // sorted, so every later number is too big as well
        continue;
      }
      chosen.push(nums[i]);
      go(i, left - nums[i]);                // i, not i + 1: a number may be used again
      chosen.pop();
    }
  }
  go(0, target);
  return result;
}

for (const prune of [false, true]) {
  tries = 0;
  const res = combinationSum([2, 3, 6, 7], 7, prune);
  const label = prune ? "with pruning" : "no pruning  ";
  console.log(label, res.map(c => c.join("+")).join(" | "), " tries", tries);
}
''', java=r'''
import java.util.*;

public class CombinationSum {
    static int tries = 0;

    static void go(int[] nums, int start, int left, boolean prune, Deque<Integer> chosen, List<String> result) {
        if (left == 0) {
            StringBuilder sb = new StringBuilder();
            for (int x : chosen) sb.append(sb.length() > 0 ? "+" : "").append(x);
            result.add(sb.toString());
            return;
        }
        for (int i = start; i < nums.length; i++) {
            tries++;
            if (nums[i] > left) {
                if (prune) break;                      // sorted, so every later number is too big as well
                continue;
            }
            chosen.addLast(nums[i]);
            go(nums, i, left - nums[i], prune, chosen, result);   // i, not i + 1: a number may be used again
            chosen.removeLast();
        }
    }

    public static void main(String[] args) {
        int[] nums = {2, 3, 6, 7};
        Arrays.sort(nums);
        for (boolean prune : new boolean[]{false, true}) {
            tries = 0;
            List<String> res = new ArrayList<>();
            go(nums, 0, 7, prune, new ArrayDeque<>(), res);
            String label = prune ? "with pruning" : "no pruning  ";
            System.out.println(label + " " + String.join(" | ", res) + "  tries " + tries);
        }
    }
}
''', ts=r'''
let tries = 0;

function combinationSum(input: number[], target: number, prune: boolean): number[][] {
  const nums = [...input].sort((a, b) => a - b);
  const result: number[][] = [], chosen: number[] = [];
  function go(start: number, left: number): void {
    if (left === 0) {
      result.push([...chosen]);
      return;
    }
    for (let i = start; i < nums.length; i++) {
      tries++;
      if (nums[i] > left) {
        if (prune) break;                   // sorted, so every later number is too big as well
        continue;
      }
      chosen.push(nums[i]);
      go(i, left - nums[i]);                // i, not i + 1: a number may be used again
      chosen.pop();
    }
  }
  go(0, target);
  return result;
}

for (const prune of [false, true]) {
  tries = 0;
  const res = combinationSum([2, 3, 6, 7], 7, prune);
  const label = prune ? "with pruning" : "no pruning  ";
  console.log(label, res.map(c => c.join("+")).join(" | "), " tries", tries);
}
''')

t.code('queens', py=r'''
def solve(n):
    cols, diag, anti = set(), set(), set()
    place, boards = [], []

    def go(r):
        if r == n:
            boards.append(place[:])           # a queen in every row
            return
        for c in range(n):
            if c in cols or r - c in diag or r + c in anti:
                continue                      # attacked: same column or same diagonal
            cols.add(c); diag.add(r - c); anti.add(r + c)
            place.append(c)
            go(r + 1)
            place.pop()                       # lift the queen and try the next column
            cols.remove(c); diag.remove(r - c); anti.remove(r + c)

    go(0)
    return boards


for n in range(1, 7):
    print(n, "queens:", len(solve(n)), "solutions")
for col in solve(4)[0]:
    print("".join("Q" if c == col else "." for c in range(4)))
''', js=r'''
function solve(n) {
  const cols = new Set(), diag = new Set(), anti = new Set();
  const place = [], boards = [];
  function go(r) {
    if (r === n) {
      boards.push([...place]);              // a queen in every row
      return;
    }
    for (let c = 0; c < n; c++) {
      if (cols.has(c) || diag.has(r - c) || anti.has(r + c)) continue;   // attacked
      cols.add(c); diag.add(r - c); anti.add(r + c);
      place.push(c);
      go(r + 1);
      place.pop();                          // lift the queen and try the next column
      cols.delete(c); diag.delete(r - c); anti.delete(r + c);
    }
  }
  go(0);
  return boards;
}

for (let n = 1; n <= 6; n++) console.log(n, "queens:", solve(n).length, "solutions");
for (const col of solve(4)[0]) {
  let line = "";
  for (let c = 0; c < 4; c++) line += c === col ? "Q" : ".";
  console.log(line);
}
''', java=r'''
import java.util.*;

public class NQueens {
    static List<int[]> boards;
    static boolean[] cols, diag, anti;
    static int[] place;

    static void go(int r, int n) {
        if (r == n) {
            boards.add(place.clone());                 // a queen in every row
            return;
        }
        for (int c = 0; c < n; c++) {
            if (cols[c] || diag[r - c + n] || anti[r + c]) continue;   // attacked
            cols[c] = diag[r - c + n] = anti[r + c] = true;
            place[r] = c;
            go(r + 1, n);
            cols[c] = diag[r - c + n] = anti[r + c] = false;           // lift the queen, try the next column
        }
    }

    static List<int[]> solve(int n) {
        boards = new ArrayList<>();
        cols = new boolean[n];
        diag = new boolean[2 * n + 1];
        anti = new boolean[2 * n];
        place = new int[n];
        go(0, n);
        return boards;
    }

    public static void main(String[] args) {
        for (int n = 1; n <= 6; n++) System.out.println(n + " queens: " + solve(n).size() + " solutions");
        for (int col : solve(4).get(0)) {
            StringBuilder line = new StringBuilder();
            for (int c = 0; c < 4; c++) line.append(c == col ? 'Q' : '.');
            System.out.println(line);
        }
    }
}
''', ts=r'''
function solve(n: number): number[][] {
  const cols = new Set<number>(), diag = new Set<number>(), anti = new Set<number>();
  const place: number[] = [], boards: number[][] = [];
  function go(r: number): void {
    if (r === n) {
      boards.push([...place]);              // a queen in every row
      return;
    }
    for (let c = 0; c < n; c++) {
      if (cols.has(c) || diag.has(r - c) || anti.has(r + c)) continue;   // attacked
      cols.add(c); diag.add(r - c); anti.add(r + c);
      place.push(c);
      go(r + 1);
      place.pop();                          // lift the queen and try the next column
      cols.delete(c); diag.delete(r - c); anti.delete(r + c);
    }
  }
  go(0);
  return boards;
}

for (let n = 1; n <= 6; n++) console.log(n, "queens:", solve(n).length, "solutions");
for (const col of solve(4)[0]) {
  let line = "";
  for (let c = 0; c < 4; c++) line += c === col ? "Q" : ".";
  console.log(line);
}
''')

t.code('sudoku', py=r'''
grid = [[1, 0, 0, 0],
        [0, 0, 3, 0],
        [0, 4, 0, 0],
        [0, 0, 0, 2]]
tries = 0


def ok(r, c, d):
    if d in grid[r] or any(grid[i][c] == d for i in range(4)):
        return False
    br, bc = r // 2 * 2, c // 2 * 2           # top left corner of the 2 by 2 box
    return all(grid[br + i][bc + j] != d for i in range(2) for j in range(2))


def solve():
    global tries
    for r in range(4):
        for c in range(4):
            if grid[r][c] == 0:
                for d in range(1, 5):
                    tries += 1
                    if ok(r, c, d):
                        grid[r][c] = d        # choose
                        if solve():
                            return True
                        grid[r][c] = 0        # unchoose: this digit led to a dead end
                return False                  # no digit fits this square, so go back
    return True                               # no empty square is left


print("solved" if solve() else "no solution", "after", tries, "tries")
for row in grid:
    print(" ".join(map(str, row)))
''', js=r'''
const grid = [[1, 0, 0, 0],
              [0, 0, 3, 0],
              [0, 4, 0, 0],
              [0, 0, 0, 2]];
let tries = 0;

function ok(r, c, d) {
  for (let i = 0; i < 4; i++) if (grid[r][i] === d || grid[i][c] === d) return false;
  const br = Math.floor(r / 2) * 2, bc = Math.floor(c / 2) * 2;   // top left corner of the 2 by 2 box
  for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) if (grid[br + i][bc + j] === d) return false;
  return true;
}

function solve() {
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 4; c++) {
      if (grid[r][c] !== 0) continue;
      for (let d = 1; d <= 4; d++) {
        tries++;
        if (ok(r, c, d)) {
          grid[r][c] = d;                   // choose
          if (solve()) return true;
          grid[r][c] = 0;                   // unchoose: this digit led to a dead end
        }
      }
      return false;                         // no digit fits this square, so go back
    }
  }
  return true;                              // no empty square is left
}

console.log(solve() ? "solved" : "no solution", "after", tries, "tries");
for (const row of grid) console.log(row.join(" "));
''', java=r'''
public class MiniSudoku {
    static int[][] grid = {{1, 0, 0, 0},
                           {0, 0, 3, 0},
                           {0, 4, 0, 0},
                           {0, 0, 0, 2}};
    static int tries = 0;

    static boolean ok(int r, int c, int d) {
        for (int i = 0; i < 4; i++) if (grid[r][i] == d || grid[i][c] == d) return false;
        int br = r / 2 * 2, bc = c / 2 * 2;                     // top left corner of the 2 by 2 box
        for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) if (grid[br + i][bc + j] == d) return false;
        return true;
    }

    static boolean solve() {
        for (int r = 0; r < 4; r++) {
            for (int c = 0; c < 4; c++) {
                if (grid[r][c] != 0) continue;
                for (int d = 1; d <= 4; d++) {
                    tries++;
                    if (ok(r, c, d)) {
                        grid[r][c] = d;                          // choose
                        if (solve()) return true;
                        grid[r][c] = 0;                          // unchoose: this digit led to a dead end
                    }
                }
                return false;                                    // no digit fits this square, so go back
            }
        }
        return true;                                             // no empty square is left
    }

    public static void main(String[] args) {
        System.out.println((solve() ? "solved" : "no solution") + " after " + tries + " tries");
        for (int[] row : grid) {
            StringBuilder sb = new StringBuilder();
            for (int x : row) sb.append(sb.length() > 0 ? " " : "").append(x);
            System.out.println(sb);
        }
    }
}
''', ts=r'''
const grid: number[][] = [[1, 0, 0, 0],
                          [0, 0, 3, 0],
                          [0, 4, 0, 0],
                          [0, 0, 0, 2]];
let tries = 0;

function ok(r: number, c: number, d: number): boolean {
  for (let i = 0; i < 4; i++) if (grid[r][i] === d || grid[i][c] === d) return false;
  const br = Math.floor(r / 2) * 2, bc = Math.floor(c / 2) * 2;   // top left corner of the 2 by 2 box
  for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) if (grid[br + i][bc + j] === d) return false;
  return true;
}

function solve(): boolean {
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 4; c++) {
      if (grid[r][c] !== 0) continue;
      for (let d = 1; d <= 4; d++) {
        tries++;
        if (ok(r, c, d)) {
          grid[r][c] = d;                   // choose
          if (solve()) return true;
          grid[r][c] = 0;                   // unchoose: this digit led to a dead end
        }
      }
      return false;                         // no digit fits this square, so go back
    }
  }
  return true;                              // no empty square is left
}

console.log(solve() ? "solved" : "no solution", "after", tries, "tries");
for (const row of grid) console.log(row.join(" "));
''')

t.code('word', py=r'''
BOARD = ["ABCE",
         "SFCS",
         "ADEE"]


def exist(word):
    rows, cols = len(BOARD), len(BOARD[0])
    used = set()

    def go(r, c, k):
        if k == len(word):
            return True                       # every letter matched
        if not (0 <= r < rows and 0 <= c < cols) or (r, c) in used or BOARD[r][c] != word[k]:
            return False
        used.add((r, c))                      # choose this square for letter k
        found = go(r + 1, c, k + 1) or go(r - 1, c, k + 1) or go(r, c + 1, k + 1) or go(r, c - 1, k + 1)
        used.remove((r, c))                   # free it for other paths
        return found

    return any(go(r, c, 0) for r in range(rows) for c in range(cols))


for w in ["ABCCED", "SEE", "ABCB"]:
    print(w, "yes" if exist(w) else "no")
''', js=r'''
const BOARD = ["ABCE",
               "SFCS",
               "ADEE"];

function exist(word) {
  const rows = BOARD.length, cols = BOARD[0].length;
  const used = new Set();
  function go(r, c, k) {
    if (k === word.length) return true;     // every letter matched
    if (r < 0 || r >= rows || c < 0 || c >= cols || used.has(r + "," + c) || BOARD[r][c] !== word[k]) return false;
    used.add(r + "," + c);                  // choose this square for letter k
    const found = go(r + 1, c, k + 1) || go(r - 1, c, k + 1) || go(r, c + 1, k + 1) || go(r, c - 1, k + 1);
    used.delete(r + "," + c);               // free it for other paths
    return found;
  }
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) if (go(r, c, 0)) return true;
  return false;
}

for (const w of ["ABCCED", "SEE", "ABCB"]) console.log(w, exist(w) ? "yes" : "no");
''', java=r'''
public class WordGrid {
    static final String[] BOARD = {"ABCE",
                                   "SFCS",
                                   "ADEE"};
    static boolean[][] used = new boolean[3][4];

    static boolean go(String word, int r, int c, int k) {
        if (k == word.length()) return true;                     // every letter matched
        if (r < 0 || r >= 3 || c < 0 || c >= 4 || used[r][c] || BOARD[r].charAt(c) != word.charAt(k)) return false;
        used[r][c] = true;                                       // choose this square for letter k
        boolean found = go(word, r + 1, c, k + 1) || go(word, r - 1, c, k + 1) || go(word, r, c + 1, k + 1) || go(word, r, c - 1, k + 1);
        used[r][c] = false;                                      // free it for other paths
        return found;
    }

    static boolean exist(String word) {
        for (int r = 0; r < 3; r++) for (int c = 0; c < 4; c++) if (go(word, r, c, 0)) return true;
        return false;
    }

    public static void main(String[] args) {
        for (String w : new String[]{"ABCCED", "SEE", "ABCB"}) System.out.println(w + " " + (exist(w) ? "yes" : "no"));
    }
}
''', ts=r'''
const BOARD: string[] = ["ABCE",
                         "SFCS",
                         "ADEE"];

function exist(word: string): boolean {
  const rows = BOARD.length, cols = BOARD[0].length;
  const used = new Set<string>();
  function go(r: number, c: number, k: number): boolean {
    if (k === word.length) return true;     // every letter matched
    if (r < 0 || r >= rows || c < 0 || c >= cols || used.has(r + "," + c) || BOARD[r][c] !== word[k]) return false;
    used.add(r + "," + c);                  // choose this square for letter k
    const found = go(r + 1, c, k + 1) || go(r - 1, c, k + 1) || go(r, c + 1, k + 1) || go(r, c - 1, k + 1);
    used.delete(r + "," + c);               // free it for other paths
    return found;
  }
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) if (go(r, c, 0)) return true;
  return false;
}

for (const w of ["ABCCED", "SEE", "ABCB"]) console.log(w, exist(w) ? "yes" : "no");
''')

# ---------------------------------------------------------------- LeetCode practice programs
t.code('p_comb', py=r'''
def combine(n, k):
    result, cur = [], []

    def go(start):
        if len(cur) == k:
            result.append(cur[:])
            return
        # stop early when too few numbers are left to fill the remaining places
        for x in range(start, n - (k - len(cur)) + 2):
            cur.append(x)
            go(x + 1)                         # later numbers only, so no order repeats
            cur.pop()

    go(1)
    return result


def show(lists):
    return " ".join("[" + ",".join(map(str, x)) + "]" for x in lists)


print(show(combine(4, 2)))
print(show(combine(1, 1)))
print("choose 3 of 5:", len(combine(5, 3)))
''', js=r'''
function combine(n, k) {
  const result = [], cur = [];
  function go(start) {
    if (cur.length === k) {
      result.push([...cur]);
      return;
    }
    // stop early when too few numbers are left to fill the remaining places
    for (let x = start; x <= n - (k - cur.length) + 1; x++) {
      cur.push(x);
      go(x + 1);                            // later numbers only, so no order repeats
      cur.pop();
    }
  }
  go(1);
  return result;
}

const show = lists => lists.map(x => "[" + x.join(",") + "]").join(" ");
console.log(show(combine(4, 2)));
console.log(show(combine(1, 1)));
console.log("choose 3 of 5:", combine(5, 3).length);
''', java=r'''
import java.util.*;

public class Combinations {
    static void go(int n, int k, int start, Deque<Integer> cur, List<List<Integer>> result) {
        if (cur.size() == k) {
            result.add(new ArrayList<>(cur));
            return;
        }
        // stop early when too few numbers are left to fill the remaining places
        for (int x = start; x <= n - (k - cur.size()) + 1; x++) {
            cur.addLast(x);
            go(n, k, x + 1, cur, result);              // later numbers only, so no order repeats
            cur.removeLast();
        }
    }

    static List<List<Integer>> combine(int n, int k) {
        List<List<Integer>> result = new ArrayList<>();
        go(n, k, 1, new ArrayDeque<>(), result);
        return result;
    }

    static String show(List<List<Integer>> lists) {
        StringBuilder sb = new StringBuilder();
        for (List<Integer> x : lists) {
            if (sb.length() > 0) sb.append(' ');
            sb.append(x.toString().replace(" ", ""));
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        System.out.println(show(combine(4, 2)));
        System.out.println(show(combine(1, 1)));
        System.out.println("choose 3 of 5: " + combine(5, 3).size());
    }
}
''', ts=r'''
function combine(n: number, k: number): number[][] {
  const result: number[][] = [], cur: number[] = [];
  function go(start: number): void {
    if (cur.length === k) {
      result.push([...cur]);
      return;
    }
    // stop early when too few numbers are left to fill the remaining places
    for (let x = start; x <= n - (k - cur.length) + 1; x++) {
      cur.push(x);
      go(x + 1);                            // later numbers only, so no order repeats
      cur.pop();
    }
  }
  go(1);
  return result;
}

const show = (lists: number[][]): string => lists.map(x => "[" + x.join(",") + "]").join(" ");
console.log(show(combine(4, 2)));
console.log(show(combine(1, 1)));
console.log("choose 3 of 5:", combine(5, 3).length);
''')

t.code('p_perm', py=r'''
def permute(nums):
    nums = nums[:]
    result = []

    def go(i):
        if i == len(nums):
            result.append(nums[:])
            return
        for j in range(i, len(nums)):
            nums[i], nums[j] = nums[j], nums[i]   # choose: bring nums[j] into position i
            go(i + 1)
            nums[i], nums[j] = nums[j], nums[i]   # unchoose: swap it back

    go(0)
    return result


def show(lists):
    return " ".join("[" + ",".join(map(str, x)) + "]" for x in lists)


print(show(permute([1, 2, 3])))
print(show(permute([0, 1])))
print(show(permute([1])))
''', js=r'''
function permute(input) {
  const nums = [...input], result = [];
  function go(i) {
    if (i === nums.length) {
      result.push([...nums]);
      return;
    }
    for (let j = i; j < nums.length; j++) {
      [nums[i], nums[j]] = [nums[j], nums[i]];   // choose: bring nums[j] into position i
      go(i + 1);
      [nums[i], nums[j]] = [nums[j], nums[i]];   // unchoose: swap it back
    }
  }
  go(0);
  return result;
}

const show = lists => lists.map(x => "[" + x.join(",") + "]").join(" ");
console.log(show(permute([1, 2, 3])));
console.log(show(permute([0, 1])));
console.log(show(permute([1])));
''', java=r'''
import java.util.*;

public class Permute {
    static void swap(int[] a, int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }

    static void go(int[] nums, int i, List<String> result) {
        if (i == nums.length) {
            result.add(Arrays.toString(nums).replace(" ", ""));
            return;
        }
        for (int j = i; j < nums.length; j++) {
            swap(nums, i, j);                          // choose: bring nums[j] into position i
            go(nums, i + 1, result);
            swap(nums, i, j);                          // unchoose: swap it back
        }
    }

    static String permute(int[] nums) {
        List<String> result = new ArrayList<>();
        go(nums.clone(), 0, result);
        return String.join(" ", result);
    }

    public static void main(String[] args) {
        System.out.println(permute(new int[]{1, 2, 3}));
        System.out.println(permute(new int[]{0, 1}));
        System.out.println(permute(new int[]{1}));
    }
}
''', ts=r'''
function permute(input: number[]): number[][] {
  const nums = [...input], result: number[][] = [];
  function go(i: number): void {
    if (i === nums.length) {
      result.push([...nums]);
      return;
    }
    for (let j = i; j < nums.length; j++) {
      [nums[i], nums[j]] = [nums[j], nums[i]];   // choose: bring nums[j] into position i
      go(i + 1);
      [nums[i], nums[j]] = [nums[j], nums[i]];   // unchoose: swap it back
    }
  }
  go(0);
  return result;
}

const show = (lists: number[][]): string => lists.map(x => "[" + x.join(",") + "]").join(" ");
console.log(show(permute([1, 2, 3])));
console.log(show(permute([0, 1])));
console.log(show(permute([1])));
''')

t.code('p_phone', py=r'''
KEYS = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


def letter_combinations(digits):
    if not digits:
        return []
    result = []

    def go(i, cur):
        if i == len(digits):
            result.append(cur)                # one letter picked for every digit
            return
        for ch in KEYS[digits[i]]:            # one branch per letter on this key
            go(i + 1, cur + ch)

    go(0, "")
    return result


for d in ["23", "", "7"]:
    print(repr(d), ":", " ".join(letter_combinations(d)) or "(none)")
''', js=r'''
const KEYS = { "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
               "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz" };

function letterCombinations(digits) {
  if (!digits) return [];
  const result = [];
  function go(i, cur) {
    if (i === digits.length) {
      result.push(cur);                     // one letter picked for every digit
      return;
    }
    for (const ch of KEYS[digits[i]]) go(i + 1, cur + ch);   // one branch per letter on this key
  }
  go(0, "");
  return result;
}

for (const d of ["23", "", "7"]) console.log("'" + d + "'", ":", letterCombinations(d).join(" ") || "(none)");
''', java=r'''
import java.util.*;

public class PhoneLetters {
    static final String[] KEYS = {"", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"};

    static void go(String digits, int i, StringBuilder cur, List<String> result) {
        if (i == digits.length()) {
            result.add(cur.toString());                // one letter picked for every digit
            return;
        }
        for (char ch : KEYS[digits.charAt(i) - '0'].toCharArray()) {   // one branch per letter on this key
            cur.append(ch);
            go(digits, i + 1, cur, result);
            cur.deleteCharAt(cur.length() - 1);
        }
    }

    static List<String> letterCombinations(String digits) {
        List<String> result = new ArrayList<>();
        if (!digits.isEmpty()) go(digits, 0, new StringBuilder(), result);
        return result;
    }

    public static void main(String[] args) {
        for (String d : new String[]{"23", "", "7"}) {
            String out = String.join(" ", letterCombinations(d));
            System.out.println("'" + d + "' : " + (out.isEmpty() ? "(none)" : out));
        }
    }
}
''', ts=r'''
const KEYS: Record<string, string> = { "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
                                       "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz" };

function letterCombinations(digits: string): string[] {
  if (!digits) return [];
  const result: string[] = [];
  function go(i: number, cur: string): void {
    if (i === digits.length) {
      result.push(cur);                     // one letter picked for every digit
      return;
    }
    for (const ch of KEYS[digits[i]]) go(i + 1, cur + ch);   // one branch per letter on this key
  }
  go(0, "");
  return result;
}

for (const d of ["23", "", "7"]) console.log("'" + d + "'", ":", letterCombinations(d).join(" ") || "(none)");
''')

t.code('p_combsum', py=r'''
def combination_sum(candidates, target):
    nums = sorted(candidates)
    result, cur = [], []

    def go(start, left):
        if left == 0:
            result.append(cur[:])
            return
        for i in range(start, len(nums)):
            if nums[i] > left:
                break                         # pruning: the rest are even bigger
            cur.append(nums[i])
            go(i, left - nums[i])             # stay at i: the same number may repeat
            cur.pop()

    go(0, target)
    return result


def show(lists):
    return " ".join("[" + ",".join(map(str, x)) + "]" for x in lists) or "(none)"


print(show(combination_sum([2, 3, 6, 7], 7)))
print(show(combination_sum([2, 3, 5], 8)))
print(show(combination_sum([2], 1)))
''', js=r'''
function combinationSum(candidates, target) {
  const nums = [...candidates].sort((a, b) => a - b);
  const result = [], cur = [];
  function go(start, left) {
    if (left === 0) {
      result.push([...cur]);
      return;
    }
    for (let i = start; i < nums.length; i++) {
      if (nums[i] > left) break;            // pruning: the rest are even bigger
      cur.push(nums[i]);
      go(i, left - nums[i]);                // stay at i: the same number may repeat
      cur.pop();
    }
  }
  go(0, target);
  return result;
}

const show = lists => lists.map(x => "[" + x.join(",") + "]").join(" ") || "(none)";
console.log(show(combinationSum([2, 3, 6, 7], 7)));
console.log(show(combinationSum([2, 3, 5], 8)));
console.log(show(combinationSum([2], 1)));
''', java=r'''
import java.util.*;

public class CombinationSumLC {
    static void go(int[] nums, int start, int left, Deque<Integer> cur, List<String> result) {
        if (left == 0) {
            result.add(cur.toString().replace(" ", ""));
            return;
        }
        for (int i = start; i < nums.length; i++) {
            if (nums[i] > left) break;                 // pruning: the rest are even bigger
            cur.addLast(nums[i]);
            go(nums, i, left - nums[i], cur, result);  // stay at i: the same number may repeat
            cur.removeLast();
        }
    }

    static String combinationSum(int[] candidates, int target) {
        int[] nums = candidates.clone();
        Arrays.sort(nums);
        List<String> result = new ArrayList<>();
        go(nums, 0, target, new ArrayDeque<>(), result);
        return result.isEmpty() ? "(none)" : String.join(" ", result);
    }

    public static void main(String[] args) {
        System.out.println(combinationSum(new int[]{2, 3, 6, 7}, 7));
        System.out.println(combinationSum(new int[]{2, 3, 5}, 8));
        System.out.println(combinationSum(new int[]{2}, 1));
    }
}
''', ts=r'''
function combinationSum(candidates: number[], target: number): number[][] {
  const nums = [...candidates].sort((a, b) => a - b);
  const result: number[][] = [], cur: number[] = [];
  function go(start: number, left: number): void {
    if (left === 0) {
      result.push([...cur]);
      return;
    }
    for (let i = start; i < nums.length; i++) {
      if (nums[i] > left) break;            // pruning: the rest are even bigger
      cur.push(nums[i]);
      go(i, left - nums[i]);                // stay at i: the same number may repeat
      cur.pop();
    }
  }
  go(0, target);
  return result;
}

const show = (lists: number[][]): string => lists.map(x => "[" + x.join(",") + "]").join(" ") || "(none)";
console.log(show(combinationSum([2, 3, 6, 7], 7)));
console.log(show(combinationSum([2, 3, 5], 8)));
console.log(show(combinationSum([2], 1)));
''')

t.code('p_paren', py=r'''
def generate_parenthesis(n):
    result = []

    def go(cur, opened, closed):
        if len(cur) == 2 * n:
            result.append(cur)
            return
        if opened < n:
            go(cur + "(", opened + 1, closed)     # an opening bracket is allowed while some are left
        if closed < opened:
            go(cur + ")", opened, closed + 1)     # a closing bracket only if one is open

    go("", 0, 0)
    return result


print(" ".join(generate_parenthesis(3)))
print(" ".join(generate_parenthesis(1)))
print("n = 4 gives", len(generate_parenthesis(4)), "strings")
''', js=r'''
function generateParenthesis(n) {
  const result = [];
  function go(cur, opened, closed) {
    if (cur.length === 2 * n) {
      result.push(cur);
      return;
    }
    if (opened < n) go(cur + "(", opened + 1, closed);     // an opening bracket is allowed while some are left
    if (closed < opened) go(cur + ")", opened, closed + 1); // a closing bracket only if one is open
  }
  go("", 0, 0);
  return result;
}

console.log(generateParenthesis(3).join(" "));
console.log(generateParenthesis(1).join(" "));
console.log("n = 4 gives", generateParenthesis(4).length, "strings");
''', java=r'''
import java.util.*;

public class Parentheses {
    static void go(int n, String cur, int opened, int closed, List<String> result) {
        if (cur.length() == 2 * n) {
            result.add(cur);
            return;
        }
        if (opened < n) go(n, cur + "(", opened + 1, closed, result);      // an opening bracket while some are left
        if (closed < opened) go(n, cur + ")", opened, closed + 1, result); // a closing bracket only if one is open
    }

    static List<String> generateParenthesis(int n) {
        List<String> result = new ArrayList<>();
        go(n, "", 0, 0, result);
        return result;
    }

    public static void main(String[] args) {
        System.out.println(String.join(" ", generateParenthesis(3)));
        System.out.println(String.join(" ", generateParenthesis(1)));
        System.out.println("n = 4 gives " + generateParenthesis(4).size() + " strings");
    }
}
''', ts=r'''
function generateParenthesis(n: number): string[] {
  const result: string[] = [];
  function go(cur: string, opened: number, closed: number): void {
    if (cur.length === 2 * n) {
      result.push(cur);
      return;
    }
    if (opened < n) go(cur + "(", opened + 1, closed);     // an opening bracket is allowed while some are left
    if (closed < opened) go(cur + ")", opened, closed + 1); // a closing bracket only if one is open
  }
  go("", 0, 0);
  return result;
}

console.log(generateParenthesis(3).join(" "));
console.log(generateParenthesis(1).join(" "));
console.log("n = 4 gives", generateParenthesis(4).length, "strings");
''')

t.code('p_palpart', py=r'''
def partition(s):
    result, cur = [], []

    def go(i):
        if i == len(s):
            result.append(cur[:])             # the whole string is cut into palindromes
            return
        for j in range(i + 1, len(s) + 1):
            piece = s[i:j]
            if piece == piece[::-1]:          # only palindrome pieces are worth exploring
                cur.append(piece)
                go(j)
                cur.pop()

    go(0)
    return result


def show(lists):
    return " ".join("[" + ",".join(x) + "]" for x in lists)


print("aab", show(partition("aab")))
print("a", show(partition("a")))
print("racecar has", len(partition("racecar")), "ways")
''', js=r'''
function partition(s) {
  const result = [], cur = [];
  const isPal = t => t === [...t].reverse().join("");
  function go(i) {
    if (i === s.length) {
      result.push([...cur]);                // the whole string is cut into palindromes
      return;
    }
    for (let j = i + 1; j <= s.length; j++) {
      const piece = s.slice(i, j);
      if (isPal(piece)) {                   // only palindrome pieces are worth exploring
        cur.push(piece);
        go(j);
        cur.pop();
      }
    }
  }
  go(0);
  return result;
}

const show = lists => lists.map(x => "[" + x.join(",") + "]").join(" ");
console.log("aab", show(partition("aab")));
console.log("a", show(partition("a")));
console.log("racecar has", partition("racecar").length, "ways");
''', java=r'''
import java.util.*;

public class PalindromeCuts {
    static boolean isPal(String t) {
        return new StringBuilder(t).reverse().toString().equals(t);
    }

    static void go(String s, int i, Deque<String> cur, List<String> result) {
        if (i == s.length()) {
            result.add("[" + String.join(",", cur) + "]");   // the whole string is cut into palindromes
            return;
        }
        for (int j = i + 1; j <= s.length(); j++) {
            String piece = s.substring(i, j);
            if (isPal(piece)) {                            // only palindrome pieces are worth exploring
                cur.addLast(piece);
                go(s, j, cur, result);
                cur.removeLast();
            }
        }
    }

    static List<String> partition(String s) {
        List<String> result = new ArrayList<>();
        go(s, 0, new ArrayDeque<>(), result);
        return result;
    }

    public static void main(String[] args) {
        System.out.println("aab " + String.join(" ", partition("aab")));
        System.out.println("a " + String.join(" ", partition("a")));
        System.out.println("racecar has " + partition("racecar").size() + " ways");
    }
}
''', ts=r'''
function partition(s: string): string[][] {
  const result: string[][] = [], cur: string[] = [];
  const isPal = (t: string): boolean => t === [...t].reverse().join("");
  function go(i: number): void {
    if (i === s.length) {
      result.push([...cur]);                // the whole string is cut into palindromes
      return;
    }
    for (let j = i + 1; j <= s.length; j++) {
      const piece = s.slice(i, j);
      if (isPal(piece)) {                   // only palindrome pieces are worth exploring
        cur.push(piece);
        go(j);
        cur.pop();
      }
    }
  }
  go(0);
  return result;
}

const show = (lists: string[][]): string => lists.map(x => "[" + x.join(",") + "]").join(" ");
console.log("aab", show(partition("aab")));
console.log("a", show(partition("a")));
console.log("racecar has", partition("racecar").length, "ways");
''')

t.code('p_queens', py=r'''
def solve_n_queens(n):
    cols, diag, anti = set(), set(), set()
    board = [["."] * n for _ in range(n)]
    result = []

    def go(r):
        if r == n:
            result.append(["".join(row) for row in board])
            return
        for c in range(n):
            if c in cols or r - c in diag or r + c in anti:
                continue                      # this square is attacked
            cols.add(c); diag.add(r - c); anti.add(r + c)
            board[r][c] = "Q"
            go(r + 1)
            board[r][c] = "."                 # backtrack: remove the queen
            cols.remove(c); diag.remove(r - c); anti.remove(r + c)

    go(0)
    return result


for n in (4, 1):
    for b in solve_n_queens(n):
        print(n, " ".join(b))
''', js=r'''
function solveNQueens(n) {
  const cols = new Set(), diag = new Set(), anti = new Set();
  const board = Array.from({ length: n }, () => Array(n).fill("."));
  const result = [];
  function go(r) {
    if (r === n) {
      result.push(board.map(row => row.join("")));
      return;
    }
    for (let c = 0; c < n; c++) {
      if (cols.has(c) || diag.has(r - c) || anti.has(r + c)) continue;   // this square is attacked
      cols.add(c); diag.add(r - c); anti.add(r + c);
      board[r][c] = "Q";
      go(r + 1);
      board[r][c] = ".";                    // backtrack: remove the queen
      cols.delete(c); diag.delete(r - c); anti.delete(r + c);
    }
  }
  go(0);
  return result;
}

for (const n of [4, 1]) for (const b of solveNQueens(n)) console.log(n, b.join(" "));
''', java=r'''
import java.util.*;

public class NQueensBoards {
    static List<String> result;
    static boolean[] cols, diag, anti;
    static char[][] board;

    static void go(int r, int n) {
        if (r == n) {
            StringBuilder sb = new StringBuilder();
            for (char[] row : board) sb.append(sb.length() > 0 ? " " : "").append(new String(row));
            result.add(sb.toString());
            return;
        }
        for (int c = 0; c < n; c++) {
            if (cols[c] || diag[r - c + n] || anti[r + c]) continue;      // this square is attacked
            cols[c] = diag[r - c + n] = anti[r + c] = true;
            board[r][c] = 'Q';
            go(r + 1, n);
            board[r][c] = '.';                                          // backtrack: remove the queen
            cols[c] = diag[r - c + n] = anti[r + c] = false;
        }
    }

    static List<String> solveNQueens(int n) {
        result = new ArrayList<>();
        cols = new boolean[n];
        diag = new boolean[2 * n + 1];
        anti = new boolean[2 * n];
        board = new char[n][n];
        for (char[] row : board) Arrays.fill(row, '.');
        go(0, n);
        return result;
    }

    public static void main(String[] args) {
        for (int n : new int[]{4, 1}) for (String b : solveNQueens(n)) System.out.println(n + " " + b);
    }
}
''', ts=r'''
function solveNQueens(n: number): string[][] {
  const cols = new Set<number>(), diag = new Set<number>(), anti = new Set<number>();
  const board: string[][] = Array.from({ length: n }, () => Array<string>(n).fill("."));
  const result: string[][] = [];
  function go(r: number): void {
    if (r === n) {
      result.push(board.map(row => row.join("")));
      return;
    }
    for (let c = 0; c < n; c++) {
      if (cols.has(c) || diag.has(r - c) || anti.has(r + c)) continue;   // this square is attacked
      cols.add(c); diag.add(r - c); anti.add(r + c);
      board[r][c] = "Q";
      go(r + 1);
      board[r][c] = ".";                    // backtrack: remove the queen
      cols.delete(c); diag.delete(r - c); anti.delete(r + c);
    }
  }
  go(0);
  return result;
}

for (const n of [4, 1]) for (const b of solveNQueens(n)) console.log(n, b.join(" "));
''')

t.code('p_sudoku', py=r'''
PUZZLE = ["53..7....", "6..195...", ".98....6.",
          "8...6...3", "4..8.3..1", "7...2...6",
          ".6....28.", "...419..5", "....8..79"]


def solve_sudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empty = []
    for r in range(9):
        for c in range(9):
            d = board[r][c]
            if d == ".":
                empty.append((r, c))
            else:
                rows[r].add(d); cols[c].add(d); boxes[r // 3 * 3 + c // 3].add(d)

    def go(k):
        if k == len(empty):
            return True                       # every empty square is filled
        r, c = empty[k]
        b = r // 3 * 3 + c // 3
        for d in "123456789":
            if d in rows[r] or d in cols[c] or d in boxes[b]:
                continue
            board[r][c] = d                   # choose, and mark it in three sets
            rows[r].add(d); cols[c].add(d); boxes[b].add(d)
            if go(k + 1):
                return True
            board[r][c] = "."                 # unchoose
            rows[r].remove(d); cols[c].remove(d); boxes[b].remove(d)
        return False

    go(0)


grid = [list(row) for row in PUZZLE]
solve_sudoku(grid)
for row in grid:
    print("".join(row))
''', js=r'''
const PUZZLE = ["53..7....", "6..195...", ".98....6.",
                "8...6...3", "4..8.3..1", "7...2...6",
                ".6....28.", "...419..5", "....8..79"];

function solveSudoku(board) {
  const rows = Array.from({ length: 9 }, () => new Set());
  const cols = Array.from({ length: 9 }, () => new Set());
  const boxes = Array.from({ length: 9 }, () => new Set());
  const empty = [];
  for (let r = 0; r < 9; r++) for (let c = 0; c < 9; c++) {
    const d = board[r][c];
    if (d === ".") empty.push([r, c]);
    else { rows[r].add(d); cols[c].add(d); boxes[Math.floor(r / 3) * 3 + Math.floor(c / 3)].add(d); }
  }
  function go(k) {
    if (k === empty.length) return true;    // every empty square is filled
    const [r, c] = empty[k], b = Math.floor(r / 3) * 3 + Math.floor(c / 3);
    for (const d of "123456789") {
      if (rows[r].has(d) || cols[c].has(d) || boxes[b].has(d)) continue;
      board[r][c] = d;                      // choose, and mark it in three sets
      rows[r].add(d); cols[c].add(d); boxes[b].add(d);
      if (go(k + 1)) return true;
      board[r][c] = ".";                    // unchoose
      rows[r].delete(d); cols[c].delete(d); boxes[b].delete(d);
    }
    return false;
  }
  go(0);
}

const grid = PUZZLE.map(row => row.split(""));
solveSudoku(grid);
for (const row of grid) console.log(row.join(""));
''', java=r'''
import java.util.*;

public class SudokuSolver {
    static boolean[][] rows = new boolean[9][10], cols = new boolean[9][10], boxes = new boolean[9][10];
    static List<int[]> empty = new ArrayList<>();
    static char[][] board;

    static boolean go(int k) {
        if (k == empty.size()) return true;                      // every empty square is filled
        int r = empty.get(k)[0], c = empty.get(k)[1], b = r / 3 * 3 + c / 3;
        for (int d = 1; d <= 9; d++) {
            if (rows[r][d] || cols[c][d] || boxes[b][d]) continue;
            board[r][c] = (char) ('0' + d);                      // choose, and mark it in three tables
            rows[r][d] = cols[c][d] = boxes[b][d] = true;
            if (go(k + 1)) return true;
            board[r][c] = '.';                                   // unchoose
            rows[r][d] = cols[c][d] = boxes[b][d] = false;
        }
        return false;
    }

    static void solveSudoku(char[][] grid) {
        board = grid;
        for (int r = 0; r < 9; r++) for (int c = 0; c < 9; c++) {
            if (board[r][c] == '.') empty.add(new int[]{r, c});
            else {
                int d = board[r][c] - '0';
                rows[r][d] = cols[c][d] = boxes[r / 3 * 3 + c / 3][d] = true;
            }
        }
        go(0);
    }

    public static void main(String[] args) {
        String[] puzzle = {"53..7....", "6..195...", ".98....6.",
                           "8...6...3", "4..8.3..1", "7...2...6",
                           ".6....28.", "...419..5", "....8..79"};
        char[][] grid = new char[9][];
        for (int i = 0; i < 9; i++) grid[i] = puzzle[i].toCharArray();
        solveSudoku(grid);
        for (char[] row : grid) System.out.println(new String(row));
    }
}
''', ts=r'''
const PUZZLE: string[] = ["53..7....", "6..195...", ".98....6.",
                          "8...6...3", "4..8.3..1", "7...2...6",
                          ".6....28.", "...419..5", "....8..79"];

function solveSudoku(board: string[][]): void {
  const rows = Array.from({ length: 9 }, () => new Set<string>());
  const cols = Array.from({ length: 9 }, () => new Set<string>());
  const boxes = Array.from({ length: 9 }, () => new Set<string>());
  const empty: Array<[number, number]> = [];
  for (let r = 0; r < 9; r++) for (let c = 0; c < 9; c++) {
    const d = board[r][c];
    if (d === ".") empty.push([r, c]);
    else { rows[r].add(d); cols[c].add(d); boxes[Math.floor(r / 3) * 3 + Math.floor(c / 3)].add(d); }
  }
  function go(k: number): boolean {
    if (k === empty.length) return true;    // every empty square is filled
    const [r, c] = empty[k], b = Math.floor(r / 3) * 3 + Math.floor(c / 3);
    for (const d of "123456789") {
      if (rows[r].has(d) || cols[c].has(d) || boxes[b].has(d)) continue;
      board[r][c] = d;                      // choose, and mark it in three sets
      rows[r].add(d); cols[c].add(d); boxes[b].add(d);
      if (go(k + 1)) return true;
      board[r][c] = ".";                    // unchoose
      rows[r].delete(d); cols[c].delete(d); boxes[b].delete(d);
    }
    return false;
  }
  go(0);
}

const grid = PUZZLE.map(row => row.split(""));
solveSudoku(grid);
for (const row of grid) console.log(row.join(""));
''')

t.leet(77, 'e', 'p_comb',
       statement='<p>Return every way to choose k numbers from 1 to n. Order inside a choice does not matter, so [1,2] and [2,1] are the same.</p>',
       example='n = 4, k = 2  →  [1,2] [1,3] [1,4] [2,3] [2,4] [3,4]\nn = 1, k = 1  →  [1]',
       hint='Only pick numbers bigger than the last one you picked.',
       approach='<p>Keep a current list. From <code>start</code> up, add a number, recurse with <code>start = x + 1</code>, then remove it. Picking only bigger numbers makes every choice appear once, in increasing order. The loop stops early when too few numbers remain to fill the k places, which cuts dead branches.</p>',
       time='O(k · C(n, k))', space='O(k) besides the output')
t.leet(46, 'e', 'p_perm',
       statement='<p>Given distinct numbers, return all their orders (permutations).</p>',
       example='[1,2,3]  →  [1,2,3] [1,3,2] [2,1,3] [2,3,1] [3,2,1] [3,1,2]\n[0,1]    →  [0,1] [1,0]',
       hint='Decide position 0 first, then position 1, and so on.',
       approach='<p>For position i, swap each candidate from i to the end into place, recurse on i + 1, and swap back. Swapping back is the unchoose step. It leaves the array exactly as it was, so the next candidate starts clean. The lesson shows the other common style, a <code>used</code> array plus a growing list.</p>',
       time='O(n · n!)', space='O(n) besides the output')
t.leet(17, 'm', 'p_phone',
       statement='<p>Each digit from 2 to 9 sits on a phone key with three or four letters. Return every letter string the digits could spell.</p>',
       example='"23"  →  ad ae af bd be bf cd ce cf\n""    →  (nothing)\n"7"   →  p q r s',
       hint='One level of the tree per digit, one branch per letter on that key.',
       approach='<p>Recurse over the digit position. At position i, loop over the letters of that key, append one, and recurse on i + 1. When i reaches the end, the string is complete. An empty input returns an empty list, not a list with one empty string.</p>',
       time='O(4ⁿ · n)', space='O(n) besides the output')
t.leet(39, 'm', 'p_combsum',
       statement='<p>Given distinct positive numbers and a target, return every combination that adds up to the target. Each number may be used as many times as you like.</p>',
       example='[2,3,6,7], 7  →  [2,2,3] [7]\n[2,3,5], 8    →  [2,2,2,2] [2,3,3] [3,5]\n[2], 1        →  (none)',
       hint='Sort first. Once a number is bigger than what is left, so is every later one.',
       approach='<p>Recurse with <code>(start, left)</code>. Loop from start, and when <code>nums[i] > left</code> break out, because the list is sorted. Otherwise add it and recurse with the same i, since it may repeat, then remove it. Starting at i, never before, stops the same combination appearing in a different order.</p>',
       time='exponential in target ÷ smallest number', space='O(target ÷ smallest number)')
t.leet(22, 'h', 'p_paren',
       statement='<p>Return every string of n pairs of brackets that is correctly balanced.</p>',
       example='n = 3  →  ((())) (()()) (())() ()(()) ()()()\nn = 1  →  ()',
       hint='You may open while some are left, and close only while something is open.',
       approach='<p>Track how many brackets are open and how many are closed. Add <code>(</code> if fewer than n are open. Add <code>)</code> only if closed is less than opened. These two rules prune every unbalanced string before it is built, so each leaf is a valid answer. The count is the Catalan number: 1, 2, 5, 14, 42.</p>',
       time='O(4ⁿ ÷ √n)', space='O(n) besides the output')
t.leet(131, 'h', 'p_palpart',
       statement='<p>Cut a string into pieces so that every piece is a palindrome. Return every such way to cut it.</p>',
       example='aab  →  [a,a,b] [aa,b]\na    →  [a]',
       hint='Choose the first piece, then cut the rest the same way.',
       approach='<p>From position i, try every end j. If <code>s[i:j]</code> is a palindrome, keep it and recurse on j. Pieces that are not palindromes are never explored, which is the pruning. A table of which ranges are palindromes, filled once, makes each check O(1) for long inputs.</p>',
       time='O(n · 2ⁿ)', space='O(n) besides the output')
t.leet(51, 'x', 'p_queens', title='N-Queens', url='https://leetcode.com/problems/n-queens/', diff='Hard',
       statement='<p>Place n queens on an n by n chess board so that no two attack each other, in a row, a column or a diagonal. Return every board.</p>',
       example='n = 4  →  .Q.. ...Q Q... ..Q.\n         ..Q. Q... ...Q .Q..\nn = 1  →  Q',
       hint='One queen per row. Three sets tell you in O(1) if a square is attacked.',
       approach='<p>Place one queen per row, so rows never clash. For columns and diagonals keep three sets: the column c, the diagonal <code>r − c</code> and the anti diagonal <code>r + c</code>. A square is safe if none of its three keys is taken. Place, recurse on the next row, then remove the queen and its keys.</p>',
       time='O(n!) in the worst case', space='O(n²) for the board')
t.leet(37, 'x', 'p_sudoku', title='Sudoku Solver', url='https://leetcode.com/problems/sudoku-solver/', diff='Hard',
       statement='<p>Fill a 9 by 9 Sudoku so that every row, every column and every 3 by 3 box holds the digits 1 to 9 exactly once.</p>',
       example='53..7....      534678912\n6..195...      672195348\n.98....6.  →   198342567\n...            ...',
       hint='List the empty squares. For each one, try the digits that are still free.',
       approach='<p>Keep one set of used digits per row, per column and per box. Walk the list of empty squares. For each, try every digit not in its three sets, place it, mark it and recurse. If no digit fits, return false so the caller tries its next digit. Picking the empty square with the fewest options first makes hard puzzles much faster.</p>',
       time='at most 9 to the number of empty squares, far less in practice', space='O(81)')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='choose-explore-unchoose', emoji='🐭', title='Backtracking: choose, explore, unchoose', html='''
<p>Imagine a mouse in a maze looking for cheese. At every corner it picks a corridor and walks on. If the corridor ends in a wall, it walks back to the last corner and tries the next corridor. That is <b>backtracking</b>: build an answer one choice at a time, and as soon as a choice cannot work, undo it and try another.</p>
<div class="grid3">
<div class="box"><h4>1️⃣ Choose</h4><p>Make one choice and record it: step into a square, put a letter in a seat, place a queen.</p></div>
<div class="box"><h4>2️⃣ Explore</h4><p>Recurse to make the next choice on top of this one.</p></div>
<div class="box"><h4>3️⃣ Unchoose</h4><p>Undo the choice exactly, so the next option starts from a clean state.</p></div>
</div>
<div class="viz" data-viz="pk" data-pk="maze"></div>
<div class="c3" data-k="maze" data-label="A mouse finds the cheese with choose, explore, unchoose"></div>
<div class="rule">Backtracking is recursion plus an undo. Whatever you change before the recursive call, change back after it.</div>
'''),
    dict(id='decision-tree', emoji='🌳', title='The decision tree and all subsets', html='''
<p>Every backtracking run walks a <b>decision tree</b>. Each level is one decision, each branch is one option, and each leaf is a finished answer. For subsets the decision is simple: for every item, <b>take it or leave it</b>. Three items give 2 × 2 × 2 = 8 leaves, one per subset.</p>
<div class="viz" data-viz="pk" data-pk="subtree"></div>
<div class="c3" data-k="subsets" data-label="All subsets with take it or leave it"></div>
<div class="grid2">
<div class="box"><h4>🍃 Leaves are answers</h4><p>A path from the root to a leaf lists the decisions. The number of leaves is the number of answers, here 2<sup>n</sup>.</p></div>
<div class="box"><h4>📏 Depth is memory</h4><p>The recursion is only as deep as the tree, n levels, so the extra memory is O(n) even though the tree has 2<sup>n</sup> leaves.</p></div>
</div>
<div class="exam">The Bit manipulation chapter builds the same 2<sup>n</sup> subsets with a counter and bit masks. Backtracking is the version that lets you stop early, as you will see with pruning.</div>
'''),
    dict(id='permutations', emoji='💺', title='Permutations: every possible order', html='''
<p>To list every order of a, b and c, fill the seats left to right. Seat 1 can take any of the 3 letters, seat 2 any of the 2 still free, seat 3 the last one. That is 3 × 2 × 1 = 3! = 6 orders. A <code>used</code> list remembers which letters already sit somewhere.</p>
<div class="viz" data-viz="pk" data-pk="perms"></div>
<div class="c3" data-k="perms" data-label="Permutations with a used list"></div>
<div class="tw"><table class="jt"><tr><th>Question</th><th>Order matters</th><th>Count for n items</th></tr>
<tr><td>Subsets</td><td>no, and size is free</td><td>2<sup>n</sup></td></tr>
<tr><td>Combinations of size k</td><td>no</td><td>C(n, k) = n! ÷ (k! (n − k)!)</td></tr>
<tr><td>Permutations</td><td>yes</td><td>n!</td></tr></table></div>
'''),
    dict(id='pruning', emoji='✂️', title='Pruning: cut branches that cannot win', html='''
<p>A plain search visits every branch. <b>Pruning</b> spots branches that can never lead to an answer and skips them. In Combination Sum we want numbers that add up to a target. If the numbers are sorted and the next one is already bigger than what is left, every number after it is bigger too, so the whole rest of the loop can be cut.</p>
<div class="viz" data-viz="pk" data-pk="combsum"></div>
<div class="c3" data-k="combsum" data-label="Combination sum with and without pruning"></div>
<div class="grid2">
<div class="box"><h4>✂️ Common pruning rules</h4><p>Stop when the running total passes the target. Stop when too few items are left to finish. Skip a value equal to the one just tried, to avoid duplicate answers.</p></div>
<div class="box"><h4>⏱️ Cost</h4><p>Backtracking is still exponential in the worst case. Good pruning does not change that bound, but in practice it often removes most of the tree.</p></div>
</div>
'''),
    dict(id='n-queens', emoji='👑', title='N-Queens: a board full of rules', html='''
<p>Place n queens on an n by n board so that none can attack another. A queen attacks along its row, its column and both diagonals. Put exactly one queen in each row. For the next row, try each column, skip the attacked squares, and if a row has no safe square left, go back and move the queen in the row above.</p>
<div class="viz" data-viz="pk" data-pk="queens"></div>
<div class="c3" data-k="queens" data-label="Counting N-Queens solutions"></div>
<div class="grid2">
<div class="box"><h4>🧭 Diagonal keys</h4><p>All squares on one diagonal share <code>row − col</code>. All squares on one anti diagonal share <code>row + col</code>. Three sets make the attack test O(1).</p></div>
<div class="box"><h4>🙅 No solution is an answer</h4><p>For 2 and 3 queens the search tries everything and finds nothing. Backtracking then proves there is no solution, which is useful too.</p></div>
</div>
'''),
    dict(id='sudoku', emoji='🔢', title='Sudoku: fill a square, check, go back', html='''
<p>A Sudoku solver is backtracking in its purest form. Find the first empty square, try the digits one by one, and keep the first digit that does not clash with its row, its column or its box. Then solve the rest. If some later square has no digit left, the earlier choice was wrong, so erase it and try the next digit there.</p>
<div class="viz" data-viz="pk" data-pk="sudoku"></div>
<div class="c3" data-k="sudoku" data-label="A 4 by 4 Sudoku solver"></div>
<div class="rule">Check a choice as early as possible. Testing the row, column and box before recursing is the pruning that makes Sudoku fast.</div>
'''),
    dict(id='grid-search', emoji='🔤', title='Searching a grid: word search', html='''
<p>Can the word be traced on a board of letters, moving up, down, left or right, without using a square twice? Start on every square that holds the first letter. From there, step to a neighbour holding the next letter, mark the square as used, and continue. If you get stuck, unmark the square and try another neighbour.</p>
<div class="viz" data-viz="pk" data-pk="word"></div>
<div class="c3" data-k="word" data-label="Word search on a letter grid"></div>
<div class="exam">The unmark step matters. Without it, a square used by one failed path stays blocked, and a later path that needs it would be missed.</div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem is solved in the Practice section in Python, JavaScript, Java and TypeScript, with line by line replay.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>The backtracking idea</th></tr>
<tr><td><a href="#lc77">77. Combinations</a></td><td>Easy</td><td>pick only bigger numbers</td></tr>
<tr><td><a href="#lc46">46. Permutations</a></td><td>Easy</td><td>swap in, recurse, swap back</td></tr>
<tr><td><a href="#lc17">17. Letter Combinations of a Phone Number</a></td><td>Medium</td><td>one level per digit</td></tr>
<tr><td><a href="#lc39">39. Combination Sum</a></td><td>Medium</td><td>sort, then break when too big</td></tr>
<tr><td><a href="#lc22">22. Generate Parentheses</a></td><td>Hard</td><td>two rules prune every bad string</td></tr>
<tr><td><a href="#lc131">131. Palindrome Partitioning</a></td><td>Hard</td><td>choose the first palindrome piece</td></tr>
<tr><td><a href="#lc51">51. N-Queens</a></td><td>Expert</td><td>one queen per row, three sets</td></tr>
<tr><td><a href="#lc37">37. Sudoku Solver</a></td><td>Expert</td><td>try free digits, undo on failure</td></tr></table></div>
'''),
]

VIZ_JS = r'''
(() => {
  const D = PK.defs;
  const LIMIT = 170;   /* longest story a widget tells before it summarises the rest */

  /* ---------- the mouse in the maze ---------- */
  const MAZES = {
    one: ['.....', '.###.', '.#...', '.#.#.', '.###.'],
    twisty: ['...#.', '##.#.', '.....', '.####', '.....'],
    blocked: ['...#.', '##.#.', '.....', '#####', '.....'],
  };
  D.maze = el => PK.widget(el, {
    title: 'Mouse in a maze', sub: 'The mouse tries down, right, up, left, in that order. A dead end turns red and the mouse steps back.',
    inputs: [{ k: 'm', label: 'Maze', type: 'seg', val: 'twisty', opts: [['one', '🟩 Lesson maze'], ['twisty', '🌀 Twisty'], ['blocked', '🧱 No way out']] }],
    frames: ({ m }) => {
      const M = MAZES[m], N = M.length, F = [];
      const seen = new Set(['0,0']), dead = new Set(), steps = [];
      let backs = 0, cut = false;
      const pic = (r0, c0, hl) => {
        const rows = [], cls = {};
        for (let r = 0; r < N; r++) {
          const row = [];
          for (let c = 0; c < N; c++) {
            const k = r + ',' + c;
            let v = '';
            if (M[r][c] === '#') cls[k] = 'wall';
            else if (dead.has(k)) { cls[k] = 'no'; v = '✗'; }
            else if (seen.has(k)) { cls[k] = 'sel'; v = '·'; }
            if (r === N - 1 && c === N - 1 && !(r === r0 && c === c0)) v = '🧀';
            if (r === r0 && c === c0) { v = '🐭'; cls[k] = hl || 'look'; }
            row.push(v);
          }
          rows.push(row);
        }
        return [{ t: 'grid', rows, cls, sq: true }];
      };
      F.push({ mood: 'think', msg: 'The mouse starts at the top left. The cheese is at the bottom right. Rule: try down, right, up, left, and step back when stuck.', layers: pic(0, 0) });
      const DIRS = [[1, 0, 'down', 'D'], [0, 1, 'right', 'R'], [-1, 0, 'up', 'U'], [0, -1, 'left', 'L']];
      const walk = (r, c) => {
        if (r === N - 1 && c === N - 1) return true;
        for (const [dr, dc, word, ch] of DIRS) {
          if (F.length > LIMIT) { cut = true; return false; }
          const nr = r + dr, nc = c + dc, k = nr + ',' + nc;
          if (nr < 0 || nr >= N || nc < 0 || nc >= N || M[nr][nc] === '#' || seen.has(k)) continue;
          seen.add(k); dead.delete(k); steps.push(ch);
          F.push({ mood: 'look', msg: `Choose: step ${word} into square (${nr}, ${nc}).`, vars: { path: steps.join('') || 'start', 'backed out': backs }, layers: pic(nr, nc) });
          if (walk(nr, nc)) return true;
          if (cut) return false;
          seen.delete(k); steps.pop();
          F.push({ mood: 'work', msg: `Unchoose: back in square (${r}, ${c}). Try the next direction from here.`, vars: { path: steps.join('') || 'start', 'backed out': backs }, layers: pic(r, c) });
        }
        backs++;
        dead.add(r + ',' + c);
        F.push({ mood: 'sad', fx: 'shake', msg: `Dead end at square (${r}, ${c})! Every way out failed, so the mouse marks it and steps back.`, vars: { path: steps.join('') || 'start', 'backed out': backs }, layers: pic(r, c, 'no') });
        return false;
      };
      const ok = walk(0, 0);
      if (cut) F.push({ mood: 'think', msg: 'The search goes on the same way. Press the end button to see the final picture.' });
      else if (ok) F.push({ mood: 'wow', fx: 'rain', msg: `Cheese! The path is <b>${steps.join('')}</b>. On the way the mouse backed out of ${backs} square${backs === 1 ? '' : 's'}.`, vars: { path: steps.join(''), 'backed out': backs }, layers: pic(N - 1, N - 1, 'yes') });
      else F.push({ mood: 'sad', fx: 'shake', msg: 'No way out! The mouse tried every corridor and ended up back at the start. Backtracking has proved there is no path, and that is an answer too.', vars: { path: 'none', 'backed out': backs }, layers: pic(0, 0, 'no') });
      return F;
    }
  });

  /* ---------- take it or leave it: the subset decision tree ---------- */
  D.subtree = el => PK.widget(el, {
    title: 'Take it or leave it', sub: 'For every item the tree branches twice: take it (left) or leave it (right). Every leaf at the bottom is one subset.',
    inputs: [{ k: 'items', label: 'Items', type: 'text', val: 'a, b, c', w: 150 }],
    random: () => ({ items: ['🍎', '🍌', '🍒', '🍇', '🥝'].sort(() => Math.random() - 0.5).slice(0, 2 + Math.floor(Math.random() * 2)).join(', ') }),
    check: v => { const a = PK.parseList(v.items, false); return a.length >= 1 && a.length <= 3 && a.every(x => [...x].length <= 2) && new Set(a).size === a.length ? '' : 'Give one to three different short items, like a, b, c.'; },
    frames: ({ items }) => {
      const a = PK.parseList(items, false), n = a.length, kids = {}, sets = {}, order = [];
      (function build(id, d, chosen) {
        sets[id] = chosen;
        order.push(id);
        if (d < n) { kids[id] = [id + '1', id + '0']; build(id + '1', d + 1, [...chosen, a[d]]); build(id + '0', d + 1, chosen); }
      })('r', 0, []);
      const W = 520, H = 70 * n + 70;
      const T = PK.treeLayout(kids, 'r', id => sets[id].length ? sets[id].join('') : '∅', W, H);
      const elab = e => (e[1].endsWith('1') ? '+' : '−') + a[e[0].length - 1];
      const shown = new Set(), found = [], F = [];
      const pic = (cur, cls) => {
        const ncls = {};
        shown.forEach(x => { ncls[x] = kids[x] ? 'done' : 'yes'; });
        ncls[cur] = cls;
        return [{ t: 'graph', w: W, h: H, nodes: T.nodes.filter(x => shown.has(x[0])), edges: T.edges.filter(e => shown.has(e[1])).map(e => [e[0], e[1], elab(e)]), ncls },
                { t: 'row', label: `Subsets found (${found.length})`, cells: found.length ? found.slice() : ['none yet'], small: true, cls: found.length ? { [found.length - 1]: 'yes' } : { 0: 'ghost' } }];
      };
      order.forEach(id => {
        shown.add(id);
        const d = id.length - 1, s = sets[id].length ? '{' + sets[id].join(', ') + '}' : 'the empty set {}';
        if (!kids[id]) {
          found.push(sets[id].length ? sets[id].join('') : '∅');
          F.push({ mood: 'happy', fx: found.length === 2 ** n ? 'burst' : '', msg: `A leaf: every item is decided. Record ${s}.`, vars: { depth: d }, layers: pic(id, 'yes') });
        } else {
          F.push({ mood: 'look', msg: d === 0 ? `Start with nothing chosen. First decision: take ${a[0]} or leave it.` : `Holding ${s}. Next decision: take ${a[d]} or leave it.`, vars: { depth: d }, layers: pic(id, 'look') });
        }
      });
      F.push({ mood: 'wow', fx: 'rain', msg: `${2 ** n} subsets, because each of the ${n} items doubles the count: 2<sup>${n}</sup> = ${2 ** n}. The recursion was never more than ${n} levels deep.`, layers: pic('r', 'done') });
      return F;
    }
  });

  /* ---------- permutations: fill the seats ---------- */
  D.perms = el => PK.widget(el, {
    title: 'Fill the seats', sub: 'Each seat takes a letter that is still free. When every seat is full, that is one order. Then step back and try the next letter.',
    inputs: [{ k: 'items', label: 'Letters', type: 'text', val: 'a, b, c', w: 150 }],
    random: () => ({ items: ['🐱', '🐶', '🐰', '🦊'].slice(0, 2 + Math.floor(Math.random() * 2)).join(', ') }),
    check: v => { const a = PK.parseList(v.items, false); return a.length >= 1 && a.length <= 4 && new Set(a).size === a.length ? '' : 'Give one to four different letters.'; },
    frames: ({ items }) => {
      const a = PK.parseList(items, false), n = a.length, used = a.map(() => false), slot = [], res = [], F = [];
      const pic = (hi, last) => [
        { t: 'row', label: 'Seats', cells: a.map((_, i) => slot[i] ?? ''), idx: true, cls: Object.fromEntries(a.map((_, i) => [i, i < slot.length ? (i === slot.length - 1 && last ? last : 'sel') : 'ghost'])) },
        { t: 'row', label: 'Letters (faded ones are already seated)', cells: a, cls: Object.fromEntries(a.map((_, i) => [i, i === hi ? 'look' : used[i] ? 'done' : ''])) },
        { t: 'row', label: `Orders found (${res.length})`, cells: res.length ? res.slice() : ['none yet'], small: true, cls: res.length ? { [res.length - 1]: 'yes' } : { 0: 'ghost' } }];
      F.push({ mood: 'think', msg: `${n} seats and ${n} letters. Seat 0 can take any letter, so the search starts with ${a[0]}.`, layers: pic(-1) });
      const go = () => {
        if (slot.length === n) {
          res.push(slot.join(''));
          F.push({ mood: 'happy', fx: n <= 3 || res.length === 1 ? 'burst' : '', msg: `Every seat is full: <b>${slot.join('')}</b> is order number ${res.length}.`, layers: pic(-1, 'yes') });
          return;
        }
        for (let i = 0; i < n; i++) {
          if (used[i]) continue;
          used[i] = true; slot.push(a[i]);
          F.push({ mood: 'look', msg: `Choose: seat ${slot.length - 1} takes ${a[i]}.`, layers: pic(i, 'look') });
          go();
          slot.pop(); used[i] = false;
          F.push({ mood: 'work', msg: `Unchoose: ${a[i]} leaves seat ${slot.length}, so another letter can try it.`, layers: pic(i) });
        }
      };
      go();
      const fact = a.reduce((p, _, i) => p * (i + 1), 1);
      F.push({ mood: 'wow', fx: 'rain', msg: `All <b>${res.length}</b> orders found. That is ${n}! = ${a.map((_, i) => n - i).join(' × ')} = ${fact}.`, layers: pic(-1) });
      return F;
    }
  });

  /* ---------- combination sum with a pruning switch ---------- */
  D.combsum = el => PK.widget(el, {
    title: 'Hit the target', sub: 'Pick numbers (repeats allowed) that add up to the target. With pruning on, a number that is too big stops the whole loop.',
    inputs: [{ k: 'nums', label: 'Numbers', type: 'text', val: '2, 3, 6, 7', w: 140 }, { k: 'target', label: 'Target', type: 'num', val: 7, min: 1, max: 12 },
             { k: 'prune', label: 'Pruning', type: 'seg', val: 'on', opts: [['on', '✂️ On'], ['off', '🐢 Off']] }],
    random: () => ({ nums: [2, 3, 4, 5, 6].sort(() => Math.random() - 0.5).slice(0, 3).sort((x, y) => x - y).join(', '), target: 6 + Math.floor(Math.random() * 4) }),
    check: v => { const a = PK.parseList(v.nums); return a && a.length >= 1 && a.length <= 5 && a.every(x => Number.isInteger(x) && x >= 1 && x <= 12) && new Set(a).size === a.length && Number.isInteger(v.target) && v.target >= 1 && v.target <= 12 ? '' : 'Use one to five different whole numbers from 1 to 12, and a target from 1 to 12.'; },
    frames: ({ nums, target, prune }) => {
      const a = PK.parseList(nums).sort((x, y) => x - y), chosen = [], found = [], F = [];
      let tries = 0, cut = false;
      const pic = (i, cls) => [
        { t: 'row', label: 'Numbers (sorted)', cells: a, cls: i >= 0 ? { [i]: cls } : {} },
        { t: 'row', label: 'Chosen so far', cells: chosen.length ? chosen.slice() : ['empty'], cls: chosen.length ? {} : { 0: 'ghost' } },
        { t: 'row', label: `Answers (${found.length})`, cells: found.length ? found.slice() : ['none yet'], small: true, cls: found.length ? { [found.length - 1]: 'yes' } : { 0: 'ghost' } }];
      const vars = left => ({ 'left to reach': left, tries });
      F.push({ mood: 'think', msg: `Target ${target}. Sorted numbers: ${a.join(', ')}. Pruning is ${prune === 'on' ? 'on' : 'off'}.`, vars: vars(target), layers: pic(-1) });
      const go = (start, left) => {
        if (left === 0) {
          found.push(chosen.join('+'));
          F.push({ mood: 'happy', fx: 'burst', msg: `${chosen.join(' + ')} = ${target}. Found one!`, vars: vars(0), layers: pic(-1) });
          return;
        }
        for (let i = start; i < a.length; i++) {
          if (F.length > LIMIT) { cut = true; return; }
          tries++;
          if (a[i] > left) {
            if (prune === 'on') {
              F.push({ mood: 'sad', fx: 'shake', msg: `${a[i]} is more than the ${left} left. Every number after it is bigger still, so cut the rest of this loop.`, vars: vars(left), layers: pic(i, 'no') });
              break;
            }
            F.push({ mood: 'sad', msg: `${a[i]} is more than the ${left} left. No pruning, so the search still checks the next number.`, vars: vars(left), layers: pic(i, 'no') });
            continue;
          }
          chosen.push(a[i]);
          F.push({ mood: 'look', msg: `Choose ${a[i]}. Now ${left - a[i]} is left.`, vars: vars(left - a[i]), layers: pic(i, 'sel') });
          go(i, left - a[i]);
          if (cut) return;
          chosen.pop();
          F.push({ mood: 'work', msg: `Unchoose ${a[i]}. Back to ${left} left.`, vars: vars(left), layers: pic(i, 'done') });
        }
      };
      go(0, target);
      if (cut) F.push({ mood: 'think', msg: 'The search continues the same way. Try a smaller target to see the whole story.' });
      else F.push({ mood: found.length ? 'wow' : 'sad', fx: found.length ? 'rain' : 'shake', msg: found.length ? `${found.length} answer${found.length > 1 ? 's' : ''} after <b>${tries}</b> tries. Switch pruning ${prune === 'on' ? 'off' : 'on'} and compare the count.` : `No combination reaches ${target}. The search checked every branch in ${tries} tries and came back empty handed.`, vars: vars(0), layers: pic(-1) });
      return F;
    }
  });

  /* ---------- N-Queens ---------- */
  D.queens = el => PK.widget(el, {
    title: 'Queens that do not fight', sub: 'One queen per row. Try the columns left to right, skip attacked squares, and move the queen above when a row has no safe square.',
    inputs: [{ k: 'n', label: 'Board', type: 'seg', val: '4', opts: [['3', '3 × 3'], ['4', '4 × 4'], ['5', '5 × 5']] }],
    frames: ({ n }) => {
      n = Number(n);
      const place = [], F = [];
      const attacker = (r, c) => place.findIndex((pc, pr) => pc === c || pr - pc === r - c || pr + pc === r + c);
      const pic = (r, c, cls, also) => {
        const rows = [], k = {};
        for (let i = 0; i < n; i++) rows.push(Array.from({ length: n }, (_, j) => (place[i] === j ? '👑' : '')));
        place.forEach((pc, pr) => { k[pr + ',' + pc] = 'yes'; });
        if (also !== undefined && also >= 0) k[also + ',' + place[also]] = 'piv';
        if (r !== undefined && r < n) { k[r + ',' + c] = cls; if (cls !== 'yes') rows[r][c] = cls === 'no' ? '✗' : '?'; }
        return [{ t: 'grid', rows, cls: k, sq: true, rlab: Array.from({ length: n }, (_, i) => 'row ' + i) }];
      };
      F.push({ mood: 'think', msg: `${n} queens on a ${n} by ${n} board. Row 0 first.`, layers: pic() });
      const go = r => {
        if (r === n) return true;
        for (let c = 0; c < n; c++) {
          const who = attacker(r, c);
          if (who >= 0) {
            F.push({ mood: 'sad', msg: `Square (${r}, ${c}) is attacked by the queen in row ${who}. Skip it.`, vars: { queens: place.length }, layers: pic(r, c, 'no', who) });
            continue;
          }
          place.push(c);
          F.push({ mood: 'look', msg: `Row ${r}: column ${c} is safe. Place a queen.`, vars: { queens: place.length }, layers: pic(r, c, 'yes') });
          if (go(r + 1)) return true;
          place.pop();
          F.push({ mood: 'work', msg: `Lift the queen from (${r}, ${c}) and try the next column in row ${r}.`, vars: { queens: place.length }, layers: pic(r, c, 'look') });
        }
        F.push({ mood: 'sad', fx: 'shake', msg: `Row ${r} has no safe square! ${r > 0 ? `The queen in row ${r - 1} must move.` : 'There is nothing above to move.'}`, vars: { queens: place.length }, layers: pic() });
        return false;
      };
      if (go(0)) F.push({ mood: 'wow', fx: 'rain', msg: `All ${n} queens are safe! Columns by row: ${place.join(', ')}.`, vars: { queens: n }, layers: pic() });
      else F.push({ mood: 'sad', fx: 'shake', msg: `No way to place ${n} queens on a ${n} by ${n} board. Backtracking tried every choice and proved it. Try 4 × 4.`, vars: { queens: 0 }, layers: pic() });
      return F;
    }
  });

  /* ---------- a 4 by 4 Sudoku ---------- */
  const PUZ = {
    lesson: [[1, 0, 0, 0], [0, 0, 3, 0], [0, 4, 0, 0], [0, 0, 0, 2]],
    tricky: [[0, 0, 0, 3], [0, 0, 0, 0], [0, 0, 0, 0], [2, 0, 0, 0]],
    stuck: [[4, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0], [0, 1, 0, 0]],
  };
  D.sudoku = el => PK.widget(el, {
    title: 'Mini Sudoku', sub: 'Every row, column and 2 by 2 box needs 1, 2, 3 and 4 once. Fill the first empty square, check, and go back on a dead end.',
    inputs: [{ k: 'p', label: 'Puzzle', type: 'seg', val: 'lesson', opts: [['lesson', '🙂 Lesson'], ['tricky', '🤔 Tricky'], ['stuck', '😵 Impossible']] }],
    frames: ({ p }) => {
      const g = PUZ[p].map(r => r.slice()), given = PUZ[p].map(r => r.map(x => x > 0)), F = [];
      let tries = 0, cut = false;
      const clash = (r, c, d) => {
        for (let i = 0; i < 4; i++) { if (g[r][i] === d) return [r, i, 'row']; if (g[i][c] === d) return [i, c, 'column']; }
        const br = Math.floor(r / 2) * 2, bc = Math.floor(c / 2) * 2;
        for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) if (g[br + i][bc + j] === d) return [br + i, bc + j, 'box'];
        return null;
      };
      const pic = (hl = {}, show = {}) => {
        const rows = g.map((row, r) => row.map((x, c) => show[r + ',' + c] ?? (x || ''))), cls = {};
        g.forEach((row, r) => row.forEach((x, c) => { if (given[r][c]) cls[r + ',' + c] = 'cur'; else if (x) cls[r + ',' + c] = 'sel'; }));
        Object.assign(cls, hl);
        return [{ t: 'grid', rows, cls, sq: true }];
      };
      F.push({ mood: 'think', msg: 'Blue squares are given. Pip fills the empty squares from the top left.', layers: pic() });
      const solve = () => {
        for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) {
          if (g[r][c]) continue;
          for (let d = 1; d <= 4; d++) {
            if (F.length > LIMIT) { cut = true; return false; }
            tries++;
            const x = clash(r, c, d);
            if (x) {
              F.push({ mood: 'sad', msg: `${d} in (${r}, ${c})? No, its ${x[2]} already has a ${d}.`, vars: { tries }, layers: pic({ [r + ',' + c]: 'no', [x[0] + ',' + x[1]]: 'piv' }, { [r + ',' + c]: d }) });
              continue;
            }
            g[r][c] = d;
            F.push({ mood: 'look', msg: `${d} fits in (${r}, ${c}). Write it and move on.`, vars: { tries }, layers: pic({ [r + ',' + c]: 'yes' }) });
            if (solve()) return true;
            if (cut) return false;
            g[r][c] = 0;
            F.push({ mood: 'work', msg: `Later squares got stuck, so erase the ${d} in (${r}, ${c}) and try the next digit.`, vars: { tries }, layers: pic({ [r + ',' + c]: 'look' }) });
          }
          F.push({ mood: 'sad', fx: 'shake', msg: `No digit fits in (${r}, ${c})! Go back to the previous square.`, vars: { tries }, layers: pic({ [r + ',' + c]: 'no' }) });
          return false;
        }
        return true;
      };
      const ok = solve();
      if (cut) F.push({ mood: 'think', msg: 'The search goes on the same way. Press the end button to jump to the last step.' });
      else if (ok) F.push({ mood: 'wow', fx: 'rain', msg: `Solved after <b>${tries}</b> tries! Every row, column and box holds 1 to 4.`, vars: { tries }, layers: pic() });
      else F.push({ mood: 'sad', fx: 'shake', msg: `Impossible! After ${tries} tries every option failed. Look at row 0: the 1s in the other rows block every square where a 1 could go.`, vars: { tries }, layers: pic() });
      return F;
    }
  });

  /* ---------- word search ---------- */
  const BOARD = ['ABCE', 'SFCS', 'ADEE'];
  D.word = el => PK.widget(el, {
    title: 'Trace the word', sub: 'Move up, down, left or right, one letter at a time, never reusing a square. Stuck squares are freed again on the way back.',
    inputs: [{ k: 'w', label: 'Word', type: 'text', val: 'ABCCED', w: 130 }],
    random: () => ({ w: ['SEE', 'ABCB', 'ASAD', 'FCSE', 'SFDA', 'BFDE'][Math.floor(Math.random() * 6)] }),
    check: v => /^[A-Za-z]{1,8}$/.test(String(v.w).trim()) ? '' : 'Type a word of one to eight letters.',
    frames: ({ w }) => {
      const word = String(w).trim().toUpperCase(), R = 3, C = 4, used = [], F = [];
      let cut = false;
      const pic = (hl = {}) => {
        const cls = {};
        used.forEach(([r, c]) => { cls[r + ',' + c] = 'sel'; });
        Object.assign(cls, hl);
        return [{ t: 'grid', rows: BOARD.map(s => s.split('')), cls, sq: true }, { t: 'row', label: 'Word', cells: word.split(''), cls: Object.fromEntries(word.split('').map((_, i) => [i, i < used.length ? 'yes' : i === used.length ? 'look' : ''])) }];
      };
      const go = (r, c, k) => {
        if (k === word.length) return true;
        if (F.length > LIMIT) { cut = true; return false; }
        if (r < 0 || r >= R || c < 0 || c >= C || used.some(([a, b]) => a === r && b === c) || BOARD[r][c] !== word[k]) return false;
        used.push([r, c]);
        F.push({ mood: 'look', msg: `${word[k]} found at (${r}, ${c}). Mark it and look around for ${k + 1 < word.length ? word[k + 1] : 'nothing more'}.`, vars: { matched: used.length + ' of ' + word.length }, layers: pic({ [r + ',' + c]: 'look' }) });
        if (go(r + 1, c, k + 1) || go(r - 1, c, k + 1) || go(r, c + 1, k + 1) || go(r, c - 1, k + 1)) return true;
        if (cut) return false;
        used.pop();
        F.push({ mood: 'sad', msg: `No neighbour of (${r}, ${c}) continues the word. Unmark it and step back.`, vars: { matched: used.length + ' of ' + word.length }, layers: pic({ [r + ',' + c]: 'no' }) });
        return false;
      };
      F.push({ mood: 'think', msg: `Looking for ${word}. Pip tries every square that holds ${word[0]} as a start.`, layers: pic() });
      let ok = false;
      for (let r = 0; r < R && !ok && !cut; r++) for (let c = 0; c < C && !ok && !cut; c++) if (BOARD[r][c] === word[0]) ok = go(r, c, 0);
      if (cut) F.push({ mood: 'think', msg: 'The search goes on the same way. Try a shorter word.' });
      else if (ok) F.push({ mood: 'wow', fx: 'burst', msg: `<b>${word}</b> is on the board! The green squares trace it.`, vars: { matched: word.length + ' of ' + word.length }, layers: pic(Object.fromEntries(used.map(([r, c]) => [r + ',' + c, 'yes']))) });
      else F.push({ mood: 'sad', fx: 'shake', msg: `${word} is not on this board. Pip tried every start and every turn. Try SEE or ABCCED.`, vars: { matched: 'no' }, layers: pic() });
      return F;
    }
  });
})();
'''

INFO = {
    'title': 'Try, and undo when it fails',
    'panels': [
        {'s': [['e', '🐭'], ['t', 'choose → explore → unchoose', {'b': 1}]], 'h': 'Backtracking', 't': 'Build an answer one choice at a time.', 'more': 'Undo a choice the moment it cannot work, then try the next option.'},
        {'s': [['e', '🌳'], ['t', '2ⁿ subsets, n! orders', {'b': 1}]], 'h': 'Decision tree', 't': 'Levels are decisions, leaves are answers.', 'more': 'The recursion depth is the height of the tree, so memory stays small.'},
        {'s': [['e', '✂️'], ['t', 'too big? stop the loop', {'b': 1}]], 'h': 'Pruning', 't': 'Skip branches that cannot win.', 'more': 'Sorting first often turns a skip into a break.'},
        {'s': [['e', '👑'], ['t', 'col, r − c, r + c', {'b': 1}]], 'h': 'Constraints', 't': 'Check early, fail fast.', 'more': 'Sets of used columns and diagonals, or digits per row, make each check O(1).'},
    ],
    'remember': 'Choose, explore, unchoose. Whatever you change before the recursive call, change back after it. Check each choice as early as possible and prune branches that cannot lead to an answer.',
}

REAL = [
    ['🧩', 'Solving a jigsaw by trial', 'You try a piece in a gap. If the edges do not fit, you take it out and try the next piece. Puzzle solving apps use the same idea.'],
    ['📅', 'Building a school timetable', 'Place one class at a time into a free slot. If a teacher ends up in two rooms at once, move the last class and try again.'],
    ['🔐', 'A forgotten luggage lock code', 'Try digit by digit. Smart lock solvers stop a branch as soon as the first digits are known to be wrong.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to backtracking. Backtracking builds an answer one choice at a time, and the moment a choice cannot work, it undoes it and tries the next one. You will guide a mouse through a maze, draw the decision tree for subsets, fill seats to make permutations, prune a search, place queens on a chess board, solve a small Sudoku and trace words on a letter grid.'},
    {'id': 'choose-explore-unchoose', 'h': 'Choose, explore, unchoose', 'en': 'Every backtracking program has three steps. Choose one option and record it. Explore by recursing to make the next choice. Unchoose by undoing exactly what you changed, so the next option starts clean. The mouse steps into a corridor, walks on, and if it hits a wall, it walks back and tries the next corridor.'},
    {'id': 'decision-tree', 'h': 'Decision tree', 'en': 'A backtracking run walks a decision tree. Each level is one decision and each leaf is a finished answer. For subsets, every item is either taken or left, so three items give eight leaves. The tree has two to the power n leaves, but the recursion is only n levels deep.'},
    {'id': 'permutations', 'h': 'Permutations', 'en': 'To list every order, fill the seats from left to right. Each seat takes a letter that is still free, and a used list remembers which letters are already seated. After a full order is recorded, take the last letter back out and try the next one. Three letters give three factorial, which is six orders.'},
    {'id': 'pruning', 'h': 'Pruning', 'en': 'Pruning skips branches that can never lead to an answer. In combination sum the numbers are sorted, so when one number is already bigger than what is left, every later number is too, and the loop can stop. Switch pruning on and off in the animation and compare the number of tries.'},
    {'id': 'n-queens', 'h': 'N-Queens', 'en': 'Place one queen in each row. For the next row, try each column and skip squares attacked along a column or a diagonal. Squares on one diagonal share row minus column, and squares on the other diagonal share row plus column. If a row has no safe square, move the queen in the row above.'},
    {'id': 'sudoku', 'h': 'Sudoku', 'en': 'A Sudoku solver finds the first empty square and tries each digit. A digit that clashes with its row, column or box is skipped at once. A digit that fits is written down and the solver moves on. If a later square has no digit left, the solver erases the earlier digit and tries the next one.'},
    {'id': 'grid-search', 'h': 'Word search', 'en': 'To trace a word on a letter grid, start on every square holding the first letter. Step to a neighbour holding the next letter and mark the square as used. If no neighbour continues the word, unmark the square and step back. Unmarking matters, because another path may need that square later.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from combinations and permutations up to N-Queens and the Sudoku solver. Each one is solved in Python, JavaScript, Java and TypeScript, and you can replay every solution line by line.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. For each problem, first name the choice made at each level, the moment an answer is complete, and what must be undone. Then write the code. Open the hint if you are stuck.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'What are the three steps of backtracking?', 'o': ['Sort, search, return', 'Choose, explore, unchoose', 'Push, pop, peek', 'Divide, conquer, combine'], 'a': 1, 'hint': 'Make a choice, go deeper, undo it.', 'why': 'Choose an option, recurse to explore, then undo the choice so the next option starts clean.'},
    {'lv': 'e', 'q': 'How many subsets does a set of 4 items have?', 'o': ['8', '12', '16', '24'], 'a': 2, 'hint': 'Each item is taken or left.', 'why': '2⁴ = 16, counting the empty set.'},
    {'lv': 'e', 'q': 'How many orders (permutations) do the letters a, b, c, d have?', 'o': ['16', '24', '12', '4'], 'a': 1, 'hint': '4!', 'why': '4 × 3 × 2 × 1 = 24.'},
    {'lv': 'e', 'q': 'In a decision tree, what is a leaf?', 'o': ['The first choice', 'A finished answer or a dead end', 'The call stack', 'A sorted list'], 'a': 1, 'hint': 'Nothing is left to decide.', 'why': 'At a leaf every decision has been made, so it is either a complete answer or a failed one.'},
    {'lv': 'm', 'q': 'Why must a backtracking function undo its change after the recursive call?', 'o': ['To save memory', 'So the next option starts from the same state', 'To make it a tail call', 'Python requires it'], 'a': 1, 'hint': 'The next loop step reuses the same list.', 'why': 'The shared list or set must look exactly as before, otherwise the next option inherits leftovers from the last one.'},
    {'lv': 'm', 'q': 'Combination Sum with sorted numbers [2, 3, 6, 7] and 4 left to reach. What happens at 6?', 'o': ['Pick it', 'Skip it and try 7', 'Break out of the loop', 'Return the answer'], 'a': 2, 'hint': 'Everything after 6 is bigger.', 'why': '6 is more than 4, and 7 is bigger still, so the rest of the loop is pruned with break.'},
    {'lv': 'm', 'q': 'Two queens at (1, 3) and (2, 2). Do they attack each other?', 'o': ['No', 'Yes, same column', 'Yes, they share the anti diagonal r + c', 'Yes, they share the diagonal r − c'], 'a': 2, 'hint': 'Compute r + c and r − c for both.', 'why': '1 + 3 = 4 and 2 + 2 = 4, so both are on the same anti diagonal.'},
    {'lv': 'm', 'q': 'How deep can the recursion go when listing subsets of n items?', 'o': ['1', 'n', '2ⁿ', 'n!'], 'a': 1, 'hint': 'One level per decision.', 'why': 'There is one decision per item, so the depth is n even though there are 2ⁿ leaves.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'res = []\ndef go(s, n):\n    if len(s) == n:\n        res.append(s)\n        return\n    for ch in "ab":\n        go(s + ch, n)\ngo("", 2)\nprint(res)', 'o': ["['ab', 'ba']", "['aa', 'ab', 'ba', 'bb']", "['a', 'b']", "['aa', 'bb']"], 'a': 1, 'hint': 'Letters may repeat.', 'why': 'Each of the 2 positions takes a or b, giving 2² = 4 strings in order aa, ab, ba, bb.'},
    {'lv': 'h', 'q': 'Generate Parentheses with n = 3. When may you add a closing bracket?', 'o': ['Always', 'When fewer than 3 are closed', 'When closed is less than opened', 'Only at the end'], 'a': 2, 'hint': 'You cannot close something that is not open.', 'why': 'A closing bracket is valid only while some opening bracket is still unmatched.'},
    {'lv': 'h', 'q': 'How many solutions does the 4 queens puzzle have?', 'o': ['0', '1', '2', '4'], 'a': 2, 'hint': 'Run the lesson program.', 'why': 'There are exactly 2, and they are mirror images of each other.'},
    {'lv': 'h', 'q': 'In word search, what goes wrong if you forget to unmark a square on the way back?', 'o': ['Nothing', 'The program crashes', 'A later path that needs the square is wrongly blocked', 'It becomes faster and still correct'], 'a': 2, 'hint': 'The used set is shared by all paths.', 'why': 'The square stays marked, so a different path through it is never tried and a real word can be missed.'},
    {'lv': 'x', 'q': 'Subsets II has duplicates, like [1, 2, 2]. How do you avoid repeated subsets?', 'o': ['Use a set of strings at the end', 'Sort, then skip a value equal to the previous one at the same level', 'Reverse the list', 'It cannot be done'], 'a': 1, 'hint': 'Equal neighbours at the same level make the same branch.', 'why': 'After sorting, choosing the second 2 at a level where the first 2 was just tried builds the same subsets again, so skip it.'},
    {'lv': 'x', 'q': 'Why is N-Queens with one queen per row much faster than trying every placement of n queens on n² squares?', 'o': ['It uses sorting', 'Rows can never clash, and attacked squares are skipped early', 'It uses dynamic programming', 'It is not faster'], 'a': 1, 'hint': 'Count the branches at each level.', 'why': 'Fixing one queen per row reduces the choices to at most n per level, and the attack check prunes most of them.'},
    {'lv': 'x', 'q': 'A Sudoku solver picks the empty square with the fewest legal digits first. Why does this help?', 'o': ['It sorts the board', 'Fewer branches near the root shrink the whole tree', 'It avoids recursion', 'It only works on 4 by 4 boards'], 'a': 1, 'hint': 'A square with one legal digit has no branching at all.', 'why': 'Branching early multiplies every level below. Choosing tight squares first keeps the tree narrow and finds dead ends sooner.'},
    {'lv': 'x', 'q': 'Palindrome Partitioning of a string of n equal letters, like "aaaa". How many ways are there?', 'o': ['n', 'n²', '2ⁿ⁻¹', 'n!'], 'a': 2, 'hint': 'Every gap between letters can be cut or not.', 'why': 'Every piece of equal letters is a palindrome, so each of the n − 1 gaps is cut or not: 2ⁿ⁻¹ ways.'},
]

CALC = [
    {'lv': 'e', 'q': 'How many subsets does a set of 5 items have?', 'ans': '32', 'hint': 'Take it or leave it, 5 times.', 'steps': ['<span class="eq">2⁵ = 32</span>']},
    {'lv': 'e', 'q': 'How many different orders do 5 friends have when standing in a line?', 'ans': '120', 'hint': '5!', 'steps': ['<span class="eq">5 × 4 × 3 × 2 × 1 = 120</span>']},
    {'lv': 'm', 'q': 'How many ways are there to choose 2 numbers out of 1 to 6, ignoring order?', 'ans': '15', 'hint': 'C(6, 2) = 6 × 5 ÷ 2.', 'steps': ['<span class="eq">C(6, 2) = (6 × 5) ÷ (2 × 1) = 15</span>']},
    {'lv': 'm', 'q': 'The digits 2 and 3 are on phone keys with 3 letters each, and 7 has 4 letters. How many strings can "237" spell?', 'ans': '36', 'hint': 'Multiply the letters per key.', 'steps': ['<span class="eq">3 × 3 × 4 = 36</span>']},
    {'lv': 'h', 'q': 'How many balanced strings of 4 pairs of brackets are there?', 'ans': '14', 'hint': 'The Catalan numbers go 1, 1, 2, 5, 14, 42.', 'steps': ['<span class="eq">C₄ = (1 ÷ 5) × C(8, 4) = 70 ÷ 5 = 14</span>']},
    {'lv': 'h', 'q': 'The lesson program counts 5 queens solutions. How many does it print?', 'ans': '10', 'hint': 'Run the N-Queens lesson code.', 'steps': ['The output line reads: 5 queens: <span class="eq">10</span> solutions']},
    {'lv': 'x', 'q': 'A word of 4 letters is traced on a large grid from one start square. The first step can go 4 ways, and every later step 3 ways, because the square you came from is used. At most how many paths are explored?', 'ans': '36', 'hint': 'There are 3 steps after the first letter.', 'steps': ['Step 1: 4 ways. Steps 2 and 3: 3 ways each.', '<span class="eq">4 × 3 × 3 = 36</span> paths at most']},
    {'lv': 'x', 'q': 'How many ways can "aaaaa" be cut into palindromes?', 'ans': '16', 'hint': 'Each of the 4 gaps is cut or not.', 'steps': ['5 letters have 4 gaps.', '<span class="eq">2⁴ = 16</span>']},
]

TALK = {
    'choose-explore-unchoose': 'Picture a little mouse in a maze, trying to reach a piece of cheese. At the first corner it has a choice of corridors. It picks one and walks on. At the next corner it picks again. Sometimes the corridor ends in a solid wall. The mouse does not give up. It walks back to the last corner where it had a choice, and tries a corridor it has not tried yet. If every corridor from that corner fails, it walks back one more corner. This patient habit is called backtracking. In code it has three steps. First you choose an option and write it down. Then you explore, which means you call the same function again to make the next choice. Finally you unchoose, which means you undo exactly what you wrote down, so the next option starts from a clean state. Choose, explore, unchoose. Keep those three words in mind for the whole chapter.',
    'decision-tree': 'Every backtracking search quietly draws a tree of decisions. The first decision sits at the top. Each option becomes a branch, and each branch leads to the next decision. At the very bottom are the leaves, where nothing is left to decide. Let us make every possible group from the letters a, b and c. For the letter a there are two options: take it, or leave it. Then the same two options for b, and again for c. Two times two times two gives eight leaves, and each leaf is one group, from all three letters down to the empty group. That is why a set of n items has two to the power n subsets. Here is the nice part. Even though the tree can be enormous, the computer only ever walks one path from top to bottom at a time. So the memory needed is just the height of the tree, which is n, and not the number of leaves.',
    'permutations': 'Imagine three friends and three seats in a row. How many different ways can they sit? Fill the seats one at a time. The first seat can take any of the three friends. The second seat can take either of the two who are still standing. The last seat takes whoever is left. Three times two times one makes six seating plans. Backtracking lists them all in the same way. A used list remembers who is already sitting. For each seat, the program tries every friend who is still free, sits them down, and moves to the next seat. When every seat is full, it writes down that seating plan. Then comes the unchoose step. The last friend stands up again so that somebody else can try that seat. With four friends there are twenty four plans, and with ten friends there are more than three and a half million, which is why permutations grow so fast.',
    'pruning': 'Imagine you have coins worth two, three, six and seven, and you want to pay exactly seven. You can use a coin more than once. A plain search tries every combination, even silly ones that are obviously too expensive. Pruning means cutting off those hopeless branches early, like a gardener trimming dead branches from a tree. Here is the clever trick. Sort the coins from small to large first. Now suppose you still need to pay four, and the next coin is six. Six is already too much. Every coin after it is even bigger, so there is no point checking them at all. The program simply breaks out of the loop. In this small example pruning cuts the number of tries from twenty seven down to sixteen. On bigger problems the saving is often enormous. Pruning does not change what answers you find. It only saves the work of exploring branches that could never succeed.',
    'n-queens': 'In chess, a queen is the strongest piece. She can attack any square in her row, her column, or along either diagonal. The N Queens puzzle asks you to place n queens on an n by n board so that no queen can attack another. Backtracking solves it neatly. Since two queens in the same row would fight, put exactly one queen in each row. Start with row zero and place a queen in the first safe column. Then move to row one, and try each column, skipping the squares that are under attack. If a row has no safe square at all, the queen in the row above must move to its next safe column. Checking attacks is fast with one small trick. Squares on the same diagonal share the same value of row minus column, and squares on the other diagonal share row plus column. Three sets of numbers then answer every attack question instantly.',
    'sudoku': 'Many people enjoy Sudoku puzzles in newspapers. Every row, every column and every box must contain each digit exactly once. A computer can solve them with backtracking, and it works like a very patient person with a pencil and an eraser. It finds the first empty square and tries the digit one. If one already appears in the same row, column or box, it moves straight on to two, then three, and so on. When a digit fits, it pencils it in and moves to the next empty square. Sometimes a later square has no digit that fits at all. That means an earlier guess was wrong. So the computer rubs out the most recent pencilled digit and tries the next digit in that square. Checking each digit before going deeper is the pruning that keeps the search fast. A clever solver also fills the square with the fewest possible digits first, which keeps the tree of guesses small.',
    'grid-search': 'Word search puzzles hide words in a grid of letters. Here the rule is that you move up, down, left or right, one letter at a time, and you may not use the same square twice. To find the word, backtracking starts on every square that holds the first letter. From that square, it looks at the neighbours for the second letter. If one matches, it marks the current square as used and steps there. Then it looks for the third letter, and so on. If no neighbour holds the next letter, the search is stuck. It unmarks the square it is standing on and steps back to try a different neighbour. That unmarking is easy to forget, and forgetting it causes a sneaky bug. A square used by a failed path would stay blocked forever, and a later path that really needs it would never be found. Board games, maze solvers and puzzle apps all use this same search.',
    'leetcode': 'The LeetCode problems in this chapter grow your backtracking skills one step at a time. You begin by choosing k numbers from one to n, and by listing every order of a few numbers with the swap trick. Next you turn phone digits into every letter string they could spell, and you find coins that add up to a target, cutting the search short with pruning. The hard problems ask you to build every balanced string of brackets, using two simple rules that block every bad string before it is finished, and to cut a word into pieces that each read the same backwards. The expert problems are the famous ones: placing n queens on a chess board without any fights, and solving a full nine by nine Sudoku. Each problem has a hint, a clear explanation and working code in Python, JavaScript, Java and TypeScript that you can replay line by line.',
}

T = t.finish({
    'slug': 'backtracking', 'title': 'Backtracking', 'short': 'Backtracking', 'emoji': '🐭', 'topic': 'backtracking', 'prefix': 'dsabt',
    'module': ('🔁', 'Recursion and smart searching'),
    'lead': 'Build an answer one choice at a time, and undo a choice the moment it cannot work. Guide a mouse through a maze, draw decision trees, list subsets and permutations, prune a search, place N queens, solve a Sudoku and trace words on a grid.',
    'desc': 'Backtracking in DSA: choose, explore and unchoose, decision trees, subsets and permutations, pruning with combination sum, N-Queens, a Sudoku solver and word search, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 22,
    'summary': 'Choose, explore and unchoose, the decision tree, subsets and permutations, pruning, N-Queens, a Sudoku solver and word search on a grid. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['backtracking', 'choose explore unchoose', 'decision tree', 'subsets', 'permutations', 'combinations', 'pruning', 'combination sum', 'n queens', 'sudoku solver', 'word search', 'generate parentheses', 'palindrome partitioning', 'maze', 'constraint satisfaction'],
    'added': '2026-11-22',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS, 'css': '.grid3{display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin:10px 0}',
    'prev': ('recursion', 'recursion', '🪆 Recursion'),
    'next': ('trees', 'trees', '🌲 Trees'),
})
