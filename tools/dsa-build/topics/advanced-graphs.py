# Advanced graphs: negative edges with Bellman-Ford, all pairs with Floyd-Warshall, strongly connected components,
# bridges and articulation points, maximum flow, A* search, and Euler paths with Hierholzer's algorithm.
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
t.code('bellman', py=r'''
INF = 10**9                                   # stands for "not reached yet"
NAMES = "s t x y z"


def show(dist):
    return " ".join("inf" if d == INF else str(d) for d in dist)


def bellman_ford(n, edges, src):
    dist = [INF] * n
    dist[src] = 0
    for rnd in range(1, n):                   # n - 1 rounds are always enough
        changed = False
        for u, v, w in edges:                 # relax every edge once per round
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break                             # nothing improved, so every distance is final
        print("after round", rnd, ":", show(dist))
    for u, v, w in edges:                     # one extra check: any improvement means a negative cycle
        if dist[u] != INF and dist[u] + w < dist[v]:
            return None
    return dist


edges = [(1, 2, 5), (1, 3, 8), (1, 4, -4), (2, 1, -2), (3, 2, -3),
         (3, 4, 9), (4, 2, 7), (4, 0, 2), (0, 1, 6), (0, 3, 7)]
print("nodes", NAMES)
print("final", show(bellman_ford(5, edges, 0)))
loop = [(0, 1, 1), (1, 2, -1), (2, 1, -1)]
print("second graph:", "negative cycle found" if bellman_ford(3, loop, 0) is None else "no negative cycle")
''', js=r'''
const INF = 1e9;                              // stands for "not reached yet"
const NAMES = "s t x y z";

const show = dist => dist.map(d => (d === INF ? "inf" : d)).join(" ");

function bellmanFord(n, edges, src) {
  const dist = new Array(n).fill(INF);
  dist[src] = 0;
  for (let rnd = 1; rnd < n; rnd++) {         // n - 1 rounds are always enough
    let changed = false;
    for (const [u, v, w] of edges) {          // relax every edge once per round
      if (dist[u] !== INF && dist[u] + w < dist[v]) { dist[v] = dist[u] + w; changed = true; }
    }
    if (!changed) break;                      // nothing improved, so every distance is final
    console.log("after round", rnd, ":", show(dist));
  }
  for (const [u, v, w] of edges)              // one extra check: any improvement means a negative cycle
    if (dist[u] !== INF && dist[u] + w < dist[v]) return null;
  return dist;
}

const edges = [[1, 2, 5], [1, 3, 8], [1, 4, -4], [2, 1, -2], [3, 2, -3],
               [3, 4, 9], [4, 2, 7], [4, 0, 2], [0, 1, 6], [0, 3, 7]];
console.log("nodes", NAMES);
console.log("final", show(bellmanFord(5, edges, 0)));
const loop = [[0, 1, 1], [1, 2, -1], [2, 1, -1]];
console.log("second graph:", bellmanFord(3, loop, 0) === null ? "negative cycle found" : "no negative cycle");
''', java=r'''
import java.util.*;

public class BellmanFord {
    static final int INF = 1_000_000_000;      // stands for "not reached yet"

    static String show(int[] dist) {
        StringJoiner sj = new StringJoiner(" ");
        for (int d : dist) sj.add(d == INF ? "inf" : String.valueOf(d));
        return sj.toString();
    }

    static int[] bellmanFord(int n, int[][] edges, int src) {
        int[] dist = new int[n];
        Arrays.fill(dist, INF);
        dist[src] = 0;
        for (int rnd = 1; rnd < n; rnd++) {           // n - 1 rounds are always enough
            boolean changed = false;
            for (int[] e : edges) {                    // relax every edge once per round
                if (dist[e[0]] != INF && dist[e[0]] + e[2] < dist[e[1]]) { dist[e[1]] = dist[e[0]] + e[2]; changed = true; }
            }
            if (!changed) break;                       // nothing improved, so every distance is final
            System.out.println("after round " + rnd + " : " + show(dist));
        }
        for (int[] e : edges)                          // one extra check: any improvement means a negative cycle
            if (dist[e[0]] != INF && dist[e[0]] + e[2] < dist[e[1]]) return null;
        return dist;
    }

    public static void main(String[] args) {
        int[][] edges = {{1, 2, 5}, {1, 3, 8}, {1, 4, -4}, {2, 1, -2}, {3, 2, -3},
                         {3, 4, 9}, {4, 2, 7}, {4, 0, 2}, {0, 1, 6}, {0, 3, 7}};
        System.out.println("nodes s t x y z");
        System.out.println("final " + show(bellmanFord(5, edges, 0)));
        int[][] loop = {{0, 1, 1}, {1, 2, -1}, {2, 1, -1}};
        System.out.println("second graph: " + (bellmanFord(3, loop, 0) == null ? "negative cycle found" : "no negative cycle"));
    }
}
''', ts=r'''
const INF = 1e9;                              // stands for "not reached yet"
const NAMES = "s t x y z";
type Edge = [number, number, number];

const show = (dist: number[]): string => dist.map(d => (d === INF ? "inf" : String(d))).join(" ");

function bellmanFord(n: number, edges: Edge[], src: number): number[] | null {
  const dist: number[] = new Array(n).fill(INF);
  dist[src] = 0;
  for (let rnd = 1; rnd < n; rnd++) {         // n - 1 rounds are always enough
    let changed = false;
    for (const [u, v, w] of edges) {          // relax every edge once per round
      if (dist[u] !== INF && dist[u] + w < dist[v]) { dist[v] = dist[u] + w; changed = true; }
    }
    if (!changed) break;                      // nothing improved, so every distance is final
    console.log("after round", rnd, ":", show(dist));
  }
  for (const [u, v, w] of edges)              // one extra check: any improvement means a negative cycle
    if (dist[u] !== INF && dist[u] + w < dist[v]) return null;
  return dist;
}

const edges: Edge[] = [[1, 2, 5], [1, 3, 8], [1, 4, -4], [2, 1, -2], [3, 2, -3],
                       [3, 4, 9], [4, 2, 7], [4, 0, 2], [0, 1, 6], [0, 3, 7]];
console.log("nodes", NAMES);
console.log("final", show(bellmanFord(5, edges, 0)!));
const loop: Edge[] = [[0, 1, 1], [1, 2, -1], [2, 1, -1]];
console.log("second graph:", bellmanFord(3, loop, 0) === null ? "negative cycle found" : "no negative cycle");
''')

t.code('floyd', py=r'''
INF = 10**9


def floyd_warshall(n, edges):
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    nxt = [[j if i == j else -1 for j in range(n)] for i in range(n)]   # first step on the best path
    for u, v, w in edges:
        d[u][v] = w
        nxt[u][v] = v
    for k in range(n):                        # allow k as a stop in the middle
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
                    nxt[i][j] = nxt[i][k]
    return d, nxt


def path(nxt, i, j):
    p = [i]
    while i != j:
        i = nxt[i][j]
        p.append(i)
    return p


edges = [(0, 1, 3), (0, 3, 7), (1, 0, 8), (1, 2, 2), (2, 0, 5), (2, 3, 1), (3, 0, 2)]
d, nxt = floyd_warshall(4, edges)
for i, row in enumerate(d):
    print("from", i, ":", " ".join(str(x) for x in row))
print("best path 1 to 0:", " -> ".join(map(str, path(nxt, 1, 0))), " cost", d[1][0])
''', js=r'''
const INF = 1e9;

function floydWarshall(n, edges) {
  const d = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 0 : INF)));
  const nxt = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? j : -1)));   // first step on the best path
  for (const [u, v, w] of edges) { d[u][v] = w; nxt[u][v] = v; }
  for (let k = 0; k < n; k++)                 // allow k as a stop in the middle
    for (let i = 0; i < n; i++)
      for (let j = 0; j < n; j++)
        if (d[i][k] + d[k][j] < d[i][j]) { d[i][j] = d[i][k] + d[k][j]; nxt[i][j] = nxt[i][k]; }
  return [d, nxt];
}

function path(nxt, i, j) {
  const p = [i];
  while (i !== j) { i = nxt[i][j]; p.push(i); }
  return p;
}

const edges = [[0, 1, 3], [0, 3, 7], [1, 0, 8], [1, 2, 2], [2, 0, 5], [2, 3, 1], [3, 0, 2]];
const [d, nxt] = floydWarshall(4, edges);
d.forEach((row, i) => console.log("from", i, ":", row.join(" ")));
console.log("best path 1 to 0:", path(nxt, 1, 0).join(" -> "), " cost", d[1][0]);
''', java=r'''
import java.util.*;

public class FloydWarshall {
    static final int INF = 1_000_000_000;

    public static void main(String[] args) {
        int n = 4;
        int[][] edges = {{0, 1, 3}, {0, 3, 7}, {1, 0, 8}, {1, 2, 2}, {2, 0, 5}, {2, 3, 1}, {3, 0, 2}};
        int[][] d = new int[n][n], nxt = new int[n][n];               // nxt: first step on the best path
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) { d[i][j] = i == j ? 0 : INF; nxt[i][j] = i == j ? j : -1; }
        for (int[] e : edges) { d[e[0]][e[1]] = e[2]; nxt[e[0]][e[1]] = e[1]; }
        for (int k = 0; k < n; k++)                                   // allow k as a stop in the middle
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    if (d[i][k] + d[k][j] < d[i][j]) { d[i][j] = d[i][k] + d[k][j]; nxt[i][j] = nxt[i][k]; }
        for (int i = 0; i < n; i++) {
            StringJoiner sj = new StringJoiner(" ");
            for (int x : d[i]) sj.add(String.valueOf(x));
            System.out.println("from " + i + " : " + sj);
        }
        StringJoiner p = new StringJoiner(" -> ");
        int i = 1;
        p.add("1");
        while (i != 0) { i = nxt[i][0]; p.add(String.valueOf(i)); }
        System.out.println("best path 1 to 0: " + p + "  cost " + d[1][0]);
    }
}
''', ts=r'''
const INF = 1e9;
type Edge = [number, number, number];

function floydWarshall(n: number, edges: Edge[]): [number[][], number[][]] {
  const d: number[][] = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 0 : INF)));
  const nxt: number[][] = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? j : -1)));   // first step on the best path
  for (const [u, v, w] of edges) { d[u][v] = w; nxt[u][v] = v; }
  for (let k = 0; k < n; k++)                 // allow k as a stop in the middle
    for (let i = 0; i < n; i++)
      for (let j = 0; j < n; j++)
        if (d[i][k] + d[k][j] < d[i][j]) { d[i][j] = d[i][k] + d[k][j]; nxt[i][j] = nxt[i][k]; }
  return [d, nxt];
}

function path(nxt: number[][], i: number, j: number): number[] {
  const p = [i];
  while (i !== j) { i = nxt[i][j]; p.push(i); }
  return p;
}

const edges: Edge[] = [[0, 1, 3], [0, 3, 7], [1, 0, 8], [1, 2, 2], [2, 0, 5], [2, 3, 1], [3, 0, 2]];
const [d, nxt] = floydWarshall(4, edges);
d.forEach((row, i) => console.log("from", i, ":", row.join(" ")));
console.log("best path 1 to 0:", path(nxt, 1, 0).join(" -> "), " cost", d[1][0]);
''')

t.code('scc', py=r'''
def kosaraju(n, edges):
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]             # every edge turned around
    for u, v in edges:
        adj[u].append(v)
        radj[v].append(u)
    seen, order = [False] * n, []

    def dfs1(u):                              # pass 1: record nodes as they finish
        seen[u] = True
        for v in adj[u]:
            if not seen[v]:
                dfs1(v)
        order.append(u)

    for u in range(n):
        if not seen[u]:
            dfs1(u)
    comp = [-1] * n

    def dfs2(u, c):                           # pass 2: on the reversed graph, latest finisher first
        comp[u] = c
        for v in radj[u]:
            if comp[v] == -1:
                dfs2(v, c)

    groups = []
    for u in reversed(order):
        if comp[u] == -1:
            dfs2(u, len(groups))
            groups.append(sorted(x for x in range(n) if comp[x] == len(groups)))
    return order, groups


edges = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3), (6, 5), (6, 7), (7, 6)]
order, groups = kosaraju(8, edges)
print("finish order:", " ".join(map(str, order)))
for g in groups:
    print("component:", " ".join(map(str, g)))
print(len(groups), "strongly connected components")
''', js=r'''
function kosaraju(n, edges) {
  const adj = Array.from({ length: n }, () => []);
  const radj = Array.from({ length: n }, () => []);   // every edge turned around
  for (const [u, v] of edges) { adj[u].push(v); radj[v].push(u); }
  const seen = new Array(n).fill(false), order = [];
  const dfs1 = u => {                         // pass 1: record nodes as they finish
    seen[u] = true;
    for (const v of adj[u]) if (!seen[v]) dfs1(v);
    order.push(u);
  };
  for (let u = 0; u < n; u++) if (!seen[u]) dfs1(u);
  const comp = new Array(n).fill(-1), groups = [];
  const dfs2 = (u, c) => {                    // pass 2: on the reversed graph, latest finisher first
    comp[u] = c;
    for (const v of radj[u]) if (comp[v] === -1) dfs2(v, c);
  };
  for (const u of [...order].reverse()) {
    if (comp[u] !== -1) continue;
    dfs2(u, groups.length);
    groups.push([...Array(n).keys()].filter(x => comp[x] === groups.length));
  }
  return [order, groups];
}

const edges = [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 5], [5, 3], [6, 5], [6, 7], [7, 6]];
const [order, groups] = kosaraju(8, edges);
console.log("finish order:", order.join(" "));
for (const g of groups) console.log("component:", g.join(" "));
console.log(groups.length, "strongly connected components");
''', java=r'''
import java.util.*;

public class Kosaraju {
    static List<List<Integer>> adj = new ArrayList<>(), radj = new ArrayList<>();
    static boolean[] seen;
    static int[] comp;
    static List<Integer> order = new ArrayList<>();

    static void dfs1(int u) {                       // pass 1: record nodes as they finish
        seen[u] = true;
        for (int v : adj.get(u)) if (!seen[v]) dfs1(v);
        order.add(u);
    }

    static void dfs2(int u, int c) {                // pass 2: on the reversed graph, latest finisher first
        comp[u] = c;
        for (int v : radj.get(u)) if (comp[v] == -1) dfs2(v, c);
    }

    public static void main(String[] args) {
        int n = 8;
        int[][] edges = {{0, 1}, {1, 2}, {2, 0}, {2, 3}, {3, 4}, {4, 5}, {5, 3}, {6, 5}, {6, 7}, {7, 6}};
        for (int i = 0; i < n; i++) { adj.add(new ArrayList<>()); radj.add(new ArrayList<>()); }
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); radj.get(e[1]).add(e[0]); }   // radj: every edge turned around
        seen = new boolean[n];
        for (int u = 0; u < n; u++) if (!seen[u]) dfs1(u);
        comp = new int[n];
        Arrays.fill(comp, -1);
        int count = 0;
        StringJoiner fin = new StringJoiner(" ");
        for (int u : order) fin.add(String.valueOf(u));
        System.out.println("finish order: " + fin);
        for (int k = order.size() - 1; k >= 0; k--) {
            int u = order.get(k);
            if (comp[u] != -1) continue;
            dfs2(u, count);
            StringJoiner sj = new StringJoiner(" ");
            for (int x = 0; x < n; x++) if (comp[x] == count) sj.add(String.valueOf(x));
            System.out.println("component: " + sj);
            count++;
        }
        System.out.println(count + " strongly connected components");
    }
}
''', ts=r'''
function kosaraju(n: number, edges: [number, number][]): [number[], number[][]] {
  const adj: number[][] = Array.from({ length: n }, () => []);
  const radj: number[][] = Array.from({ length: n }, () => []);   // every edge turned around
  for (const [u, v] of edges) { adj[u].push(v); radj[v].push(u); }
  const seen: boolean[] = new Array(n).fill(false), order: number[] = [];
  const dfs1 = (u: number): void => {         // pass 1: record nodes as they finish
    seen[u] = true;
    for (const v of adj[u]) if (!seen[v]) dfs1(v);
    order.push(u);
  };
  for (let u = 0; u < n; u++) if (!seen[u]) dfs1(u);
  const comp: number[] = new Array(n).fill(-1), groups: number[][] = [];
  const dfs2 = (u: number, c: number): void => {   // pass 2: on the reversed graph, latest finisher first
    comp[u] = c;
    for (const v of radj[u]) if (comp[v] === -1) dfs2(v, c);
  };
  for (const u of [...order].reverse()) {
    if (comp[u] !== -1) continue;
    dfs2(u, groups.length);
    groups.push([...Array(n).keys()].filter(x => comp[x] === groups.length));
  }
  return [order, groups];
}

const edges: [number, number][] = [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 5], [5, 3], [6, 5], [6, 7], [7, 6]];
const [order, groups] = kosaraju(8, edges);
console.log("finish order:", order.join(" "));
for (const g of groups) console.log("component:", g.join(" "));
console.log(groups.length, "strongly connected components");
''')

t.code('bridges', py=r'''
def bridges_and_cut_points(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    disc, low = [-1] * n, [0] * n             # discovery time, and the earliest time reachable from below
    bridges, cuts = [], set()
    timer = [0]

    def dfs(u, parent):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        children = 0
        for v in adj[u]:
            if v == parent:
                continue
            if disc[v] != -1:                 # a back edge to an ancestor
                low[u] = min(low[u], disc[v])
                continue
            children += 1
            dfs(v, u)
            low[u] = min(low[u], low[v])
            if low[v] > disc[u]:
                bridges.append((u, v))        # v's subtree cannot climb back above u
            if parent != -1 and low[v] >= disc[u]:
                cuts.add(u)
        if parent == -1 and children > 1:
            cuts.add(u)                       # a root with two separate subtrees

    dfs(0, -1)
    return disc, low, bridges, sorted(cuts)


edges = [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4), (4, 5), (5, 3), (4, 6)]
disc, low, bridges, cuts = bridges_and_cut_points(7, edges)
print("disc:", " ".join(map(str, disc)))
print("low: ", " ".join(map(str, low)))
print("bridges:", " ".join(f"{u}-{v}" for u, v in bridges))
print("articulation points:", " ".join(map(str, cuts)))
''', js=r'''
function bridgesAndCutPoints(n, edges) {
  const adj = Array.from({ length: n }, () => []);
  for (const [u, v] of edges) { adj[u].push(v); adj[v].push(u); }
  const disc = new Array(n).fill(-1), low = new Array(n).fill(0);   // discovery time, earliest time reachable from below
  const bridges = [], cuts = new Set();
  let timer = 0;
  const dfs = (u, parent) => {
    disc[u] = low[u] = timer++;
    let children = 0;
    for (const v of adj[u]) {
      if (v === parent) continue;
      if (disc[v] !== -1) { low[u] = Math.min(low[u], disc[v]); continue; }   // a back edge to an ancestor
      children++;
      dfs(v, u);
      low[u] = Math.min(low[u], low[v]);
      if (low[v] > disc[u]) bridges.push([u, v]);          // v's subtree cannot climb back above u
      if (parent !== -1 && low[v] >= disc[u]) cuts.add(u);
    }
    if (parent === -1 && children > 1) cuts.add(u);        // a root with two separate subtrees
  };
  dfs(0, -1);
  return [disc, low, bridges, [...cuts].sort((a, b) => a - b)];
}

const edges = [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4], [4, 5], [5, 3], [4, 6]];
const [disc, low, bridges, cuts] = bridgesAndCutPoints(7, edges);
console.log("disc:", disc.join(" "));
console.log("low: ", low.join(" "));
console.log("bridges:", bridges.map(([u, v]) => `${u}-${v}`).join(" "));
console.log("articulation points:", cuts.join(" "));
''', java=r'''
import java.util.*;

public class Bridges {
    static List<List<Integer>> adj = new ArrayList<>();
    static int[] disc, low;                          // discovery time, earliest time reachable from below
    static int timer = 0;
    static List<String> bridges = new ArrayList<>();
    static TreeSet<Integer> cuts = new TreeSet<>();

    static void dfs(int u, int parent) {
        disc[u] = low[u] = timer++;
        int children = 0;
        for (int v : adj.get(u)) {
            if (v == parent) continue;
            if (disc[v] != -1) { low[u] = Math.min(low[u], disc[v]); continue; }   // a back edge to an ancestor
            children++;
            dfs(v, u);
            low[u] = Math.min(low[u], low[v]);
            if (low[v] > disc[u]) bridges.add(u + "-" + v);           // v's subtree cannot climb back above u
            if (parent != -1 && low[v] >= disc[u]) cuts.add(u);
        }
        if (parent == -1 && children > 1) cuts.add(u);                // a root with two separate subtrees
    }

    static String join(int[] a) {
        StringJoiner sj = new StringJoiner(" ");
        for (int x : a) sj.add(String.valueOf(x));
        return sj.toString();
    }

    public static void main(String[] args) {
        int n = 7;
        int[][] edges = {{0, 1}, {1, 2}, {2, 0}, {1, 3}, {3, 4}, {4, 5}, {5, 3}, {4, 6}};
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); }
        disc = new int[n];
        low = new int[n];
        Arrays.fill(disc, -1);
        dfs(0, -1);
        System.out.println("disc: " + join(disc));
        System.out.println("low:  " + join(low));
        System.out.println("bridges: " + String.join(" ", bridges));
        StringJoiner sj = new StringJoiner(" ");
        for (int c : cuts) sj.add(String.valueOf(c));
        System.out.println("articulation points: " + sj);
    }
}
''', ts=r'''
function bridgesAndCutPoints(n: number, edges: [number, number][]): [number[], number[], [number, number][], number[]] {
  const adj: number[][] = Array.from({ length: n }, () => []);
  for (const [u, v] of edges) { adj[u].push(v); adj[v].push(u); }
  const disc: number[] = new Array(n).fill(-1), low: number[] = new Array(n).fill(0);   // discovery time, earliest time reachable from below
  const bridges: [number, number][] = [], cuts = new Set<number>();
  let timer = 0;
  const dfs = (u: number, parent: number): void => {
    disc[u] = low[u] = timer++;
    let children = 0;
    for (const v of adj[u]) {
      if (v === parent) continue;
      if (disc[v] !== -1) { low[u] = Math.min(low[u], disc[v]); continue; }   // a back edge to an ancestor
      children++;
      dfs(v, u);
      low[u] = Math.min(low[u], low[v]);
      if (low[v] > disc[u]) bridges.push([u, v]);          // v's subtree cannot climb back above u
      if (parent !== -1 && low[v] >= disc[u]) cuts.add(u);
    }
    if (parent === -1 && children > 1) cuts.add(u);        // a root with two separate subtrees
  };
  dfs(0, -1);
  return [disc, low, bridges, [...cuts].sort((a, b) => a - b)];
}

const edges: [number, number][] = [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4], [4, 5], [5, 3], [4, 6]];
const [disc, low, bridges, cuts] = bridgesAndCutPoints(7, edges);
console.log("disc:", disc.join(" "));
console.log("low: ", low.join(" "));
console.log("bridges:", bridges.map(([u, v]) => `${u}-${v}`).join(" "));
console.log("articulation points:", cuts.join(" "));
''')

t.code('flow', py=r'''
INF = 10**9


def max_flow(cap, s, t):
    n, total = len(cap), 0
    while True:
        parent = [-1] * n                     # breadth first search for the shortest path with spare capacity
        parent[s] = s
        queue = [s]
        for u in queue:
            for v in range(n):
                if parent[v] == -1 and cap[u][v] > 0:
                    parent[v] = u
                    queue.append(v)
        if parent[t] == -1:
            break                             # no path left: the flow is maximum
        path, v, push = [t], t, INF
        while v != s:                         # the smallest spare capacity on the path
            push = min(push, cap[parent[v]][v])
            v = parent[v]
            path.append(v)
        v = t
        while v != s:                         # use it up, and allow it to be undone later
            u = parent[v]
            cap[u][v] -= push
            cap[v][u] += push
            v = u
        total += push
        print("path", " -> ".join(map(str, reversed(path))), " pushes", push)
    reach = [s]                               # what the source can still reach is one side of a minimum cut
    for u in reach:
        for v in range(n):
            if cap[u][v] > 0 and v not in reach:
                reach.append(v)
    return total, sorted(reach)


cap = [[0] * 6 for _ in range(6)]
for u, v, c in [(0, 1, 16), (0, 2, 13), (1, 3, 12), (2, 1, 4), (2, 4, 14),
                (3, 2, 9), (3, 5, 20), (4, 3, 7), (4, 5, 4)]:
    cap[u][v] = c
total, side = max_flow(cap, 0, 5)
print("maximum flow:", total)
print("minimum cut: source side", " ".join(map(str, side)))
''', js=r'''
function maxFlow(cap, s, t) {
  const n = cap.length;
  let total = 0;
  for (;;) {
    const parent = new Array(n).fill(-1);     // breadth first search for the shortest path with spare capacity
    parent[s] = s;
    const queue = [s];
    for (let q = 0; q < queue.length; q++) {
      const u = queue[q];
      for (let v = 0; v < n; v++) if (parent[v] === -1 && cap[u][v] > 0) { parent[v] = u; queue.push(v); }
    }
    if (parent[t] === -1) break;              // no path left: the flow is maximum
    const path = [t];
    let v = t, push = Infinity;
    while (v !== s) { push = Math.min(push, cap[parent[v]][v]); v = parent[v]; path.push(v); }   // the smallest spare capacity
    for (v = t; v !== s; v = parent[v]) { cap[parent[v]][v] -= push; cap[v][parent[v]] += push; }   // use it, allow undoing it
    total += push;
    console.log("path", path.reverse().join(" -> "), " pushes", push);
  }
  const reach = [s];                          // what the source can still reach is one side of a minimum cut
  for (let q = 0; q < reach.length; q++)
    for (let v = 0; v < n; v++) if (cap[reach[q]][v] > 0 && !reach.includes(v)) reach.push(v);
  return [total, reach.sort((a, b) => a - b)];
}

const cap = Array.from({ length: 6 }, () => new Array(6).fill(0));
for (const [u, v, c] of [[0, 1, 16], [0, 2, 13], [1, 3, 12], [2, 1, 4], [2, 4, 14],
                         [3, 2, 9], [3, 5, 20], [4, 3, 7], [4, 5, 4]]) cap[u][v] = c;
const [total, side] = maxFlow(cap, 0, 5);
console.log("maximum flow:", total);
console.log("minimum cut: source side", side.join(" "));
''', java=r'''
import java.util.*;

public class MaxFlow {
    static int total = 0;

    static List<Integer> maxFlow(int[][] cap, int s, int t) {
        int n = cap.length;
        while (true) {
            int[] parent = new int[n];                     // breadth first search for the shortest path with spare capacity
            Arrays.fill(parent, -1);
            parent[s] = s;
            List<Integer> queue = new ArrayList<>(List.of(s));
            for (int q = 0; q < queue.size(); q++) {
                int u = queue.get(q);
                for (int v = 0; v < n; v++) if (parent[v] == -1 && cap[u][v] > 0) { parent[v] = u; queue.add(v); }
            }
            if (parent[t] == -1) break;                    // no path left: the flow is maximum
            List<Integer> path = new ArrayList<>(List.of(t));
            int v = t, push = Integer.MAX_VALUE;
            while (v != s) { push = Math.min(push, cap[parent[v]][v]); v = parent[v]; path.add(v); }   // the smallest spare capacity
            for (v = t; v != s; v = parent[v]) { cap[parent[v]][v] -= push; cap[v][parent[v]] += push; }   // use it, allow undoing it
            total += push;
            Collections.reverse(path);
            StringJoiner sj = new StringJoiner(" -> ");
            for (int x : path) sj.add(String.valueOf(x));
            System.out.println("path " + sj + "  pushes " + push);
        }
        List<Integer> reach = new ArrayList<>(List.of(s));  // what the source can still reach is one side of a minimum cut
        for (int q = 0; q < reach.size(); q++)
            for (int v = 0; v < n; v++) if (cap[reach.get(q)][v] > 0 && !reach.contains(v)) reach.add(v);
        Collections.sort(reach);
        return reach;
    }

    public static void main(String[] args) {
        int[][] cap = new int[6][6];
        int[][] edges = {{0, 1, 16}, {0, 2, 13}, {1, 3, 12}, {2, 1, 4}, {2, 4, 14},
                         {3, 2, 9}, {3, 5, 20}, {4, 3, 7}, {4, 5, 4}};
        for (int[] e : edges) cap[e[0]][e[1]] = e[2];
        List<Integer> side = maxFlow(cap, 0, 5);
        System.out.println("maximum flow: " + total);
        StringJoiner sj = new StringJoiner(" ");
        for (int x : side) sj.add(String.valueOf(x));
        System.out.println("minimum cut: source side " + sj);
    }
}
''', ts=r'''
function maxFlow(cap: number[][], s: number, t: number): [number, number[]] {
  const n = cap.length;
  let total = 0;
  for (;;) {
    const parent: number[] = new Array(n).fill(-1);   // breadth first search for the shortest path with spare capacity
    parent[s] = s;
    const queue = [s];
    for (let q = 0; q < queue.length; q++) {
      const u = queue[q];
      for (let v = 0; v < n; v++) if (parent[v] === -1 && cap[u][v] > 0) { parent[v] = u; queue.push(v); }
    }
    if (parent[t] === -1) break;              // no path left: the flow is maximum
    const path = [t];
    let v = t, push = Infinity;
    while (v !== s) { push = Math.min(push, cap[parent[v]][v]); v = parent[v]; path.push(v); }   // the smallest spare capacity
    for (v = t; v !== s; v = parent[v]) { cap[parent[v]][v] -= push; cap[v][parent[v]] += push; }   // use it, allow undoing it
    total += push;
    console.log("path", path.reverse().join(" -> "), " pushes", push);
  }
  const reach = [s];                          // what the source can still reach is one side of a minimum cut
  for (let q = 0; q < reach.length; q++)
    for (let v = 0; v < n; v++) if (cap[reach[q]][v] > 0 && !reach.includes(v)) reach.push(v);
  return [total, reach.sort((a, b) => a - b)];
}

const cap: number[][] = Array.from({ length: 6 }, () => new Array(6).fill(0));
const pipes: [number, number, number][] = [[0, 1, 16], [0, 2, 13], [1, 3, 12], [2, 1, 4], [2, 4, 14],
                                           [3, 2, 9], [3, 5, 20], [4, 3, 7], [4, 5, 4]];
for (const [u, v, c] of pipes) cap[u][v] = c;
const [total, side] = maxFlow(cap, 0, 5);
console.log("maximum flow:", total);
console.log("minimum cut: source side", side.join(" "));
''')

t.code('astar', py=r'''
GRID = ["S...#....",
        ".##.#.##.",
        "..#...#..",
        "#.###.#.#",
        "....#....",
        ".##...##G"]


def search(use_h):
    R, C = len(GRID), len(GRID[0])
    cells = "".join(GRID)
    start, goal = cells.index("S"), cells.index("G")
    h = lambda i: abs(i // C - goal // C) + abs(i % C - goal % C) if use_h else 0   # Manhattan distance
    g, parent, closed, open_list = {start: 0}, {}, set(), [start]
    expanded = 0
    while open_list:
        best = open_list[0]                   # the open cell with the smallest (g + h, h, index)
        for i in open_list:
            if (g[i] + h(i), h(i), i) < (g[best] + h(best), h(best), best):
                best = i
        open_list.remove(best)
        closed.add(best)
        expanded += 1
        if best == goal:
            break
        r, c = divmod(best, C)
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            nb = nr * C + nc
            if 0 <= nr < R and 0 <= nc < C and cells[nb] != "#" and nb not in closed:
                if nb not in g or g[best] + 1 < g[nb]:
                    if nb not in g:
                        open_list.append(nb)
                    g[nb] = g[best] + 1
                    parent[nb] = best
    path, v = [], goal
    while v != start:
        path.append(v)
        v = parent[v]
    return g[goal], expanded, set(path)


steps, plain, _ = search(False)
steps2, smart, path = search(True)
print("Dijkstra: path length", steps, " cells expanded", plain)
print("A*:       path length", steps2, " cells expanded", smart)
C = len(GRID[0])
for r, row in enumerate(GRID):
    print("".join("*" if r * C + c in path and ch == "." else ch for c, ch in enumerate(row)))
''', js=r'''
const GRID = ["S...#....",
              ".##.#.##.",
              "..#...#..",
              "#.###.#.#",
              "....#....",
              ".##...##G"];

function search(useH) {
  const R = GRID.length, C = GRID[0].length, cells = GRID.join("");
  const start = cells.indexOf("S"), goal = cells.indexOf("G");
  const h = i => (useH ? Math.abs(Math.floor(i / C) - Math.floor(goal / C)) + Math.abs((i % C) - (goal % C)) : 0);   // Manhattan distance
  const g = new Map([[start, 0]]), parent = new Map(), closed = new Set();
  let openList = [start], expanded = 0;
  const key = i => [g.get(i) + h(i), h(i), i];
  const less = (a, b) => a[0] !== b[0] ? a[0] < b[0] : a[1] !== b[1] ? a[1] < b[1] : a[2] < b[2];
  while (openList.length) {
    let best = openList[0];                   // the open cell with the smallest (g + h, h, index)
    for (const i of openList) if (less(key(i), key(best))) best = i;
    openList = openList.filter(i => i !== best);
    closed.add(best);
    expanded++;
    if (best === goal) break;
    const r = Math.floor(best / C), c = best % C;
    for (const [nr, nc] of [[r - 1, c], [r + 1, c], [r, c - 1], [r, c + 1]]) {
      const nb = nr * C + nc;
      if (nr >= 0 && nr < R && nc >= 0 && nc < C && cells[nb] !== "#" && !closed.has(nb)) {
        if (!g.has(nb) || g.get(best) + 1 < g.get(nb)) {
          if (!g.has(nb)) openList.push(nb);
          g.set(nb, g.get(best) + 1);
          parent.set(nb, best);
        }
      }
    }
  }
  const path = new Set();
  for (let v = goal; v !== start; v = parent.get(v)) path.add(v);
  return [g.get(goal), expanded, path];
}

const [steps, plain] = search(false);
const [steps2, smart, path] = search(true);
console.log("Dijkstra: path length", steps, " cells expanded", plain);
console.log("A*:       path length", steps2, " cells expanded", smart);
const C = GRID[0].length;
GRID.forEach((row, r) => console.log([...row].map((ch, c) => (path.has(r * C + c) && ch === "." ? "*" : ch)).join("")));
''', java=r'''
import java.util.*;

public class AStar {
    static final String[] GRID = {"S...#....",
                                  ".##.#.##.",
                                  "..#...#..",
                                  "#.###.#.#",
                                  "....#....",
                                  ".##...##G"};
    static final int R = GRID.length, C = GRID[0].length();
    static String cells = String.join("", GRID);
    static int start = cells.indexOf('S'), goal = cells.indexOf('G');
    static Set<Integer> path = new HashSet<>();

    static int h(int i, boolean useH) {                    // Manhattan distance
        return useH ? Math.abs(i / C - goal / C) + Math.abs(i % C - goal % C) : 0;
    }

    static int[] search(boolean useH) {
        Map<Integer, Integer> g = new HashMap<>(), parent = new HashMap<>();
        Set<Integer> closed = new HashSet<>();
        List<Integer> open = new ArrayList<>(List.of(start));
        g.put(start, 0);
        int expanded = 0;
        while (!open.isEmpty()) {
            int best = open.get(0);                        // the open cell with the smallest (g + h, h, index)
            for (int i : open) {
                int fi = g.get(i) + h(i, useH), fb = g.get(best) + h(best, useH);
                if (fi < fb || (fi == fb && (h(i, useH) < h(best, useH) || (h(i, useH) == h(best, useH) && i < best)))) best = i;
            }
            open.remove(Integer.valueOf(best));
            closed.add(best);
            expanded++;
            if (best == goal) break;
            int r = best / C, c = best % C;
            int[][] around = {{r - 1, c}, {r + 1, c}, {r, c - 1}, {r, c + 1}};
            for (int[] p : around) {
                int nr = p[0], nc = p[1], nb = nr * C + nc;
                if (nr >= 0 && nr < R && nc >= 0 && nc < C && cells.charAt(nb) != '#' && !closed.contains(nb)) {
                    if (!g.containsKey(nb) || g.get(best) + 1 < g.get(nb)) {
                        if (!g.containsKey(nb)) open.add(nb);
                        g.put(nb, g.get(best) + 1);
                        parent.put(nb, best);
                    }
                }
            }
        }
        path.clear();
        for (int v = goal; v != start; v = parent.get(v)) path.add(v);
        return new int[]{g.get(goal), expanded};
    }

    public static void main(String[] args) {
        int[] a = search(false), b = search(true);
        System.out.println("Dijkstra: path length " + a[0] + "  cells expanded " + a[1]);
        System.out.println("A*:       path length " + b[0] + "  cells expanded " + b[1]);
        for (int r = 0; r < R; r++) {
            StringBuilder sb = new StringBuilder();
            for (int c = 0; c < C; c++) {
                char ch = GRID[r].charAt(c);
                sb.append(path.contains(r * C + c) && ch == '.' ? '*' : ch);
            }
            System.out.println(sb);
        }
    }
}
''', ts=r'''
const GRID: string[] = ["S...#....",
                        ".##.#.##.",
                        "..#...#..",
                        "#.###.#.#",
                        "....#....",
                        ".##...##G"];

function search(useH: boolean): [number, number, Set<number>] {
  const R = GRID.length, C = GRID[0].length, cells = GRID.join("");
  const start = cells.indexOf("S"), goal = cells.indexOf("G");
  const h = (i: number): number => (useH ? Math.abs(Math.floor(i / C) - Math.floor(goal / C)) + Math.abs((i % C) - (goal % C)) : 0);   // Manhattan distance
  const g = new Map<number, number>([[start, 0]]), parent = new Map<number, number>(), closed = new Set<number>();
  let openList: number[] = [start], expanded = 0;
  const key = (i: number): number[] => [g.get(i)! + h(i), h(i), i];
  const less = (a: number[], b: number[]): boolean => a[0] !== b[0] ? a[0] < b[0] : a[1] !== b[1] ? a[1] < b[1] : a[2] < b[2];
  while (openList.length) {
    let best = openList[0];                   // the open cell with the smallest (g + h, h, index)
    for (const i of openList) if (less(key(i), key(best))) best = i;
    openList = openList.filter(i => i !== best);
    closed.add(best);
    expanded++;
    if (best === goal) break;
    const r = Math.floor(best / C), c = best % C;
    for (const [nr, nc] of [[r - 1, c], [r + 1, c], [r, c - 1], [r, c + 1]]) {
      const nb = nr * C + nc;
      if (nr >= 0 && nr < R && nc >= 0 && nc < C && cells[nb] !== "#" && !closed.has(nb)) {
        if (!g.has(nb) || g.get(best)! + 1 < g.get(nb)!) {
          if (!g.has(nb)) openList.push(nb);
          g.set(nb, g.get(best)! + 1);
          parent.set(nb, best);
        }
      }
    }
  }
  const path = new Set<number>();
  for (let v = goal; v !== start; v = parent.get(v)!) path.add(v);
  return [g.get(goal)!, expanded, path];
}

const [steps, plain] = search(false);
const [steps2, smart, path] = search(true);
console.log("Dijkstra: path length", steps, " cells expanded", plain);
console.log("A*:       path length", steps2, " cells expanded", smart);
const COLS = GRID[0].length;
GRID.forEach((row, r) => console.log([...row].map((ch, c) => (path.has(r * COLS + c) && ch === "." ? "*" : ch)).join("")));
''')

t.code('euler', py=r'''
def euler_circuit(n, edges, start):
    adj = [[] for _ in range(n)]
    indeg, outdeg = [0] * n, [0] * n
    for u, v in edges:
        adj[u].append(v)
        outdeg[u] += 1
        indeg[v] += 1
    for a in adj:
        a.sort()
    if indeg != outdeg:
        return None                           # a circuit needs in degree = out degree everywhere
    used = [0] * n                            # how many edges of each node are used up
    stack, circuit = [start], []
    while stack:
        u = stack[-1]
        if used[u] < len(adj[u]):             # an unused edge: walk along it
            stack.append(adj[u][used[u]])
            used[u] += 1
        else:                                 # stuck: this node is finished, add it to the answer
            circuit.append(stack.pop())
    return circuit[::-1]


edges = [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4), (4, 1)]
route = euler_circuit(5, edges, 0)
print("Euler circuit:", " -> ".join(map(str, route)))
print("uses", len(route) - 1, "of", len(edges), "edges, each exactly once")
print("with one more edge 0 -> 2:", euler_circuit(5, edges + [(0, 2)], 0))
''', js=r'''
function eulerCircuit(n, edges, start) {
  const adj = Array.from({ length: n }, () => []);
  const indeg = new Array(n).fill(0), outdeg = new Array(n).fill(0);
  for (const [u, v] of edges) { adj[u].push(v); outdeg[u]++; indeg[v]++; }
  for (const a of adj) a.sort((x, y) => x - y);
  if (indeg.some((d, i) => d !== outdeg[i])) return null;   // a circuit needs in degree = out degree everywhere
  const used = new Array(n).fill(0);          // how many edges of each node are used up
  const stack = [start], circuit = [];
  while (stack.length) {
    const u = stack[stack.length - 1];
    if (used[u] < adj[u].length) stack.push(adj[u][used[u]++]);   // an unused edge: walk along it
    else circuit.push(stack.pop());           // stuck: this node is finished, add it to the answer
  }
  return circuit.reverse();
}

const edges = [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4], [4, 1]];
const route = eulerCircuit(5, edges, 0);
console.log("Euler circuit:", route.join(" -> "));
console.log("uses", route.length - 1, "of", edges.length, "edges, each exactly once");
console.log("with one more edge 0 -> 2:", eulerCircuit(5, [...edges, [0, 2]], 0) === null ? "None" : "found");
''', java=r'''
import java.util.*;

public class EulerCircuit {
    static List<Integer> eulerCircuit(int n, int[][] edges, int start) {
        List<List<Integer>> adj = new ArrayList<>();
        int[] indeg = new int[n], outdeg = new int[n];
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); outdeg[e[0]]++; indeg[e[1]]++; }
        for (List<Integer> a : adj) Collections.sort(a);
        if (!Arrays.equals(indeg, outdeg)) return null;           // a circuit needs in degree = out degree everywhere
        int[] used = new int[n];                                  // how many edges of each node are used up
        Deque<Integer> stack = new ArrayDeque<>(List.of(start));
        List<Integer> circuit = new ArrayList<>();
        while (!stack.isEmpty()) {
            int u = stack.peek();
            if (used[u] < adj.get(u).size()) stack.push(adj.get(u).get(used[u]++));   // an unused edge: walk along it
            else circuit.add(stack.pop());                        // stuck: this node is finished, add it to the answer
        }
        Collections.reverse(circuit);
        return circuit;
    }

    public static void main(String[] args) {
        int[][] edges = {{0, 1}, {1, 2}, {2, 0}, {1, 3}, {3, 4}, {4, 1}};
        List<Integer> route = eulerCircuit(5, edges, 0);
        StringJoiner sj = new StringJoiner(" -> ");
        for (int x : route) sj.add(String.valueOf(x));
        System.out.println("Euler circuit: " + sj);
        System.out.println("uses " + (route.size() - 1) + " of " + edges.length + " edges, each exactly once");
        int[][] more = Arrays.copyOf(edges, edges.length + 1);
        more[edges.length] = new int[]{0, 2};
        System.out.println("with one more edge 0 -> 2: " + (eulerCircuit(5, more, 0) == null ? "None" : "found"));
    }
}
''', ts=r'''
function eulerCircuit(n: number, edges: [number, number][], start: number): number[] | null {
  const adj: number[][] = Array.from({ length: n }, () => []);
  const indeg: number[] = new Array(n).fill(0), outdeg: number[] = new Array(n).fill(0);
  for (const [u, v] of edges) { adj[u].push(v); outdeg[u]++; indeg[v]++; }
  for (const a of adj) a.sort((x, y) => x - y);
  if (indeg.some((d, i) => d !== outdeg[i])) return null;   // a circuit needs in degree = out degree everywhere
  const used: number[] = new Array(n).fill(0);   // how many edges of each node are used up
  const stack = [start], circuit: number[] = [];
  while (stack.length) {
    const u = stack[stack.length - 1];
    if (used[u] < adj[u].length) stack.push(adj[u][used[u]++]);   // an unused edge: walk along it
    else circuit.push(stack.pop()!);          // stuck: this node is finished, add it to the answer
  }
  return circuit.reverse();
}

const edges: [number, number][] = [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4], [4, 1]];
const route = eulerCircuit(5, edges, 0)!;
console.log("Euler circuit:", route.join(" -> "));
console.log("uses", route.length - 1, "of", edges.length, "edges, each exactly once");
console.log("with one more edge 0 -> 2:", eulerCircuit(5, [...edges, [0, 2]], 0) === null ? "None" : "found");
''')

# ---------------------------------------------------------------- LeetCode practice programs
t.code('p_delay', py=r'''
import heapq


def network_delay_time(times, n, k):
    adj = [[] for _ in range(n + 1)]
    for u, v, w in times:
        adj[u].append((v, w))
    dist = [None] * (n + 1)
    heap = [(0, k)]
    while heap:                               # Dijkstra: settle the closest node not settled yet
        d, u = heapq.heappop(heap)
        if dist[u] is not None:
            continue
        dist[u] = d
        for v, w in adj[u]:
            if dist[v] is None:
                heapq.heappush(heap, (d + w, v))
    if any(x is None for x in dist[1:]):
        return -1                             # some node never hears the signal
    return max(dist[1:])


print(network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2))
print(network_delay_time([[1, 2, 1]], 2, 1))
print(network_delay_time([[1, 2, 1]], 2, 2))
''', js=JS_HEAP + r'''
function networkDelayTime(times, n, k) {
  const adj = Array.from({ length: n + 1 }, () => []);
  for (const [u, v, w] of times) adj[u].push([v, w]);
  const dist = new Array(n + 1).fill(null);
  const heap = new Heap((a, b) => a[0] < b[0]);
  heap.push([0, k]);
  while (heap.size) {                         // Dijkstra: settle the closest node not settled yet
    const [d, u] = heap.pop();
    if (dist[u] !== null) continue;
    dist[u] = d;
    for (const [v, w] of adj[u]) if (dist[v] === null) heap.push([d + w, v]);
  }
  const rest = dist.slice(1);
  return rest.includes(null) ? -1 : Math.max(...rest);   // -1 when some node never hears the signal
}

console.log(networkDelayTime([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2));
console.log(networkDelayTime([[1, 2, 1]], 2, 1));
console.log(networkDelayTime([[1, 2, 1]], 2, 2));
''', java=r'''
import java.util.*;

public class NetworkDelay {
    static int networkDelayTime(int[][] times, int n, int k) {
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i <= n; i++) adj.add(new ArrayList<>());
        for (int[] t : times) adj.get(t[0]).add(new int[]{t[1], t[2]});
        int[] dist = new int[n + 1];
        Arrays.fill(dist, -1);
        PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> a[0] - b[0]);
        heap.add(new int[]{0, k});
        while (!heap.isEmpty()) {                          // Dijkstra: settle the closest node not settled yet
            int[] top = heap.poll();
            int d = top[0], u = top[1];
            if (dist[u] != -1) continue;
            dist[u] = d;
            for (int[] e : adj.get(u)) if (dist[e[0]] == -1) heap.add(new int[]{d + e[1], e[0]});
        }
        int best = 0;
        for (int i = 1; i <= n; i++) {
            if (dist[i] == -1) return -1;                  // some node never hears the signal
            best = Math.max(best, dist[i]);
        }
        return best;
    }

    public static void main(String[] args) {
        System.out.println(networkDelayTime(new int[][]{{2, 1, 1}, {2, 3, 1}, {3, 4, 1}}, 4, 2));
        System.out.println(networkDelayTime(new int[][]{{1, 2, 1}}, 2, 1));
        System.out.println(networkDelayTime(new int[][]{{1, 2, 1}}, 2, 2));
    }
}
''', ts=TS_HEAP + r'''
function networkDelayTime(times: number[][], n: number, k: number): number {
  const adj: [number, number][][] = Array.from({ length: n + 1 }, () => []);
  for (const [u, v, w] of times) adj[u].push([v, w]);
  const dist: (number | null)[] = new Array(n + 1).fill(null);
  const heap = new Heap<[number, number]>((a, b) => a[0] < b[0]);
  heap.push([0, k]);
  while (heap.size) {                         // Dijkstra: settle the closest node not settled yet
    const [d, u] = heap.pop();
    if (dist[u] !== null) continue;
    dist[u] = d;
    for (const [v, w] of adj[u]) if (dist[v] === null) heap.push([d + w, v]);
  }
  const rest = dist.slice(1);
  return rest.includes(null) ? -1 : Math.max(...(rest as number[]));   // -1 when some node never hears the signal
}

console.log(networkDelayTime([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2));
console.log(networkDelayTime([[1, 2, 1]], 2, 1));
console.log(networkDelayTime([[1, 2, 1]], 2, 2));
''')

t.code('p_city', py=r'''
def find_the_city(n, edges, threshold):
    INF = 10**9
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:                     # roads go both ways
        d[u][v] = d[v][u] = w
    for k in range(n):                        # Floyd-Warshall: every pair at once
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    best, fewest = -1, n + 1
    for i in range(n):
        reach = sum(1 for j in range(n) if j != i and d[i][j] <= threshold)
        if reach <= fewest:                   # "<=" lets a bigger city number win a tie
            best, fewest = i, reach
    return best


print(find_the_city(4, [[0, 1, 3], [1, 2, 1], [1, 3, 4], [2, 3, 1]], 4))
print(find_the_city(5, [[0, 1, 2], [0, 4, 8], [1, 2, 3], [1, 4, 2], [2, 3, 1], [3, 4, 1]], 2))
''', js=r'''
function findTheCity(n, edges, threshold) {
  const INF = 1e9;
  const d = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 0 : INF)));
  for (const [u, v, w] of edges) { d[u][v] = w; d[v][u] = w; }   // roads go both ways
  for (let k = 0; k < n; k++)                 // Floyd-Warshall: every pair at once
    for (let i = 0; i < n; i++)
      for (let j = 0; j < n; j++)
        if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
  let best = -1, fewest = n + 1;
  for (let i = 0; i < n; i++) {
    const reach = d[i].filter((x, j) => j !== i && x <= threshold).length;
    if (reach <= fewest) { best = i; fewest = reach; }   // "<=" lets a bigger city number win a tie
  }
  return best;
}

console.log(findTheCity(4, [[0, 1, 3], [1, 2, 1], [1, 3, 4], [2, 3, 1]], 4));
console.log(findTheCity(5, [[0, 1, 2], [0, 4, 8], [1, 2, 3], [1, 4, 2], [2, 3, 1], [3, 4, 1]], 2));
''', java=r'''
import java.util.*;

public class FindTheCity {
    static int findTheCity(int n, int[][] edges, int threshold) {
        final int INF = 1_000_000_000;
        int[][] d = new int[n][n];
        for (int i = 0; i < n; i++) { Arrays.fill(d[i], INF); d[i][i] = 0; }
        for (int[] e : edges) { d[e[0]][e[1]] = e[2]; d[e[1]][e[0]] = e[2]; }   // roads go both ways
        for (int k = 0; k < n; k++)                                  // Floyd-Warshall: every pair at once
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
        int best = -1, fewest = n + 1;
        for (int i = 0; i < n; i++) {
            int reach = 0;
            for (int j = 0; j < n; j++) if (j != i && d[i][j] <= threshold) reach++;
            if (reach <= fewest) { best = i; fewest = reach; }       // "<=" lets a bigger city number win a tie
        }
        return best;
    }

    public static void main(String[] args) {
        System.out.println(findTheCity(4, new int[][]{{0, 1, 3}, {1, 2, 1}, {1, 3, 4}, {2, 3, 1}}, 4));
        System.out.println(findTheCity(5, new int[][]{{0, 1, 2}, {0, 4, 8}, {1, 2, 3}, {1, 4, 2}, {2, 3, 1}, {3, 4, 1}}, 2));
    }
}
''', ts=r'''
function findTheCity(n: number, edges: number[][], threshold: number): number {
  const INF = 1e9;
  const d: number[][] = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 0 : INF)));
  for (const [u, v, w] of edges) { d[u][v] = w; d[v][u] = w; }   // roads go both ways
  for (let k = 0; k < n; k++)                 // Floyd-Warshall: every pair at once
    for (let i = 0; i < n; i++)
      for (let j = 0; j < n; j++)
        if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
  let best = -1, fewest = n + 1;
  for (let i = 0; i < n; i++) {
    const reach = d[i].filter((x, j) => j !== i && x <= threshold).length;
    if (reach <= fewest) { best = i; fewest = reach; }   // "<=" lets a bigger city number win a tie
  }
  return best;
}

console.log(findTheCity(4, [[0, 1, 3], [1, 2, 1], [1, 3, 4], [2, 3, 1]], 4));
console.log(findTheCity(5, [[0, 1, 2], [0, 4, 8], [1, 2, 3], [1, 4, 2], [2, 3, 1], [3, 4, 1]], 2));
''')

t.code('p_prob', py=r'''
import heapq


def max_probability(n, edges, succ_prob, start, end):
    adj = [[] for _ in range(n)]
    for (u, v), p in zip(edges, succ_prob):
        adj[u].append((v, p))
        adj[v].append((u, p))
    best = [0.0] * n
    best[start] = 1.0
    heap = [(-1.0, start)]                    # a max heap by probability, stored as negatives
    while heap:
        p, u = heapq.heappop(heap)
        p = -p
        if u == end:
            return p                          # the first time we pop the end, it is the best
        if p < best[u]:
            continue
        for v, q in adj[u]:
            if p * q > best[v]:               # multiplying probabilities only ever makes them smaller
                best[v] = p * q
                heapq.heappush(heap, (-best[v], v))
    return 0.0


print(f"{max_probability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.2], 0, 2):.5f}")
print(f"{max_probability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.3], 0, 2):.5f}")
print(f"{max_probability(3, [[0, 1]], [0.5], 0, 2):.5f}")
''', js=JS_HEAP + r'''
function maxProbability(n, edges, succProb, start, end) {
  const adj = Array.from({ length: n }, () => []);
  edges.forEach(([u, v], i) => { adj[u].push([v, succProb[i]]); adj[v].push([u, succProb[i]]); });
  const best = new Array(n).fill(0);
  best[start] = 1;
  const heap = new Heap((a, b) => a[0] > b[0]);   // a max heap by probability
  heap.push([1, start]);
  while (heap.size) {
    const [p, u] = heap.pop();
    if (u === end) return p;                  // the first time we pop the end, it is the best
    if (p < best[u]) continue;
    for (const [v, q] of adj[u])
      if (p * q > best[v]) { best[v] = p * q; heap.push([best[v], v]); }   // products only ever get smaller
  }
  return 0;
}

console.log(maxProbability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.2], 0, 2).toFixed(5));
console.log(maxProbability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.3], 0, 2).toFixed(5));
console.log(maxProbability(3, [[0, 1]], [0.5], 0, 2).toFixed(5));
''', java=r'''
import java.util.*;

public class MaxProbability {
    static double maxProbability(int n, int[][] edges, double[] succProb, int start, int end) {
        List<List<double[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int i = 0; i < edges.length; i++) {
            adj.get(edges[i][0]).add(new double[]{edges[i][1], succProb[i]});
            adj.get(edges[i][1]).add(new double[]{edges[i][0], succProb[i]});
        }
        double[] best = new double[n];
        best[start] = 1;
        PriorityQueue<double[]> heap = new PriorityQueue<>((a, b) -> Double.compare(b[0], a[0]));   // a max heap by probability
        heap.add(new double[]{1, start});
        while (!heap.isEmpty()) {
            double[] top = heap.poll();
            double p = top[0];
            int u = (int) top[1];
            if (u == end) return p;                        // the first time we pop the end, it is the best
            if (p < best[u]) continue;
            for (double[] e : adj.get(u)) {
                int v = (int) e[0];
                if (p * e[1] > best[v]) { best[v] = p * e[1]; heap.add(new double[]{best[v], v}); }   // products only get smaller
            }
        }
        return 0;
    }

    public static void main(String[] args) {
        System.out.println(String.format("%.5f", maxProbability(3, new int[][]{{0, 1}, {1, 2}, {0, 2}}, new double[]{0.5, 0.5, 0.2}, 0, 2)));
        System.out.println(String.format("%.5f", maxProbability(3, new int[][]{{0, 1}, {1, 2}, {0, 2}}, new double[]{0.5, 0.5, 0.3}, 0, 2)));
        System.out.println(String.format("%.5f", maxProbability(3, new int[][]{{0, 1}}, new double[]{0.5}, 0, 2)));
    }
}
''', ts=TS_HEAP + r'''
function maxProbability(n: number, edges: number[][], succProb: number[], start: number, end: number): number {
  const adj: [number, number][][] = Array.from({ length: n }, () => []);
  edges.forEach(([u, v], i) => { adj[u].push([v, succProb[i]]); adj[v].push([u, succProb[i]]); });
  const best: number[] = new Array(n).fill(0);
  best[start] = 1;
  const heap = new Heap<[number, number]>((a, b) => a[0] > b[0]);   // a max heap by probability
  heap.push([1, start]);
  while (heap.size) {
    const [p, u] = heap.pop();
    if (u === end) return p;                  // the first time we pop the end, it is the best
    if (p < best[u]) continue;
    for (const [v, q] of adj[u])
      if (p * q > best[v]) { best[v] = p * q; heap.push([best[v], v]); }   // products only ever get smaller
  }
  return 0;
}

console.log(maxProbability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.2], 0, 2).toFixed(5));
console.log(maxProbability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.3], 0, 2).toFixed(5));
console.log(maxProbability(3, [[0, 1]], [0.5], 0, 2).toFixed(5));
''')

t.code('p_courses', py=r'''
def check_if_prerequisite(num_courses, prerequisites, queries):
    n = num_courses
    reach = [[False] * n for _ in range(n)]   # reach[a][b]: a must come before b
    for a, b in prerequisites:
        reach[a][b] = True
    for k in range(n):                        # Floyd-Warshall with "and" and "or" instead of "+" and "min"
        for i in range(n):
            if reach[i][k]:
                for j in range(n):
                    if reach[k][j]:
                        reach[i][j] = True
    return [reach[a][b] for a, b in queries]


for n, pre, qs in ((2, [[1, 0]], [[0, 1], [1, 0]]), (3, [[1, 2], [1, 0], [2, 0]], [[1, 0], [1, 2]])):
    print(" ".join("true" if x else "false" for x in check_if_prerequisite(n, pre, qs)))
''', js=r'''
function checkIfPrerequisite(numCourses, prerequisites, queries) {
  const n = numCourses;
  const reach = Array.from({ length: n }, () => new Array(n).fill(false));   // reach[a][b]: a must come before b
  for (const [a, b] of prerequisites) reach[a][b] = true;
  for (let k = 0; k < n; k++)                 // Floyd-Warshall with "and" and "or" instead of "+" and "min"
    for (let i = 0; i < n; i++)
      if (reach[i][k])
        for (let j = 0; j < n; j++) if (reach[k][j]) reach[i][j] = true;
  return queries.map(([a, b]) => reach[a][b]);
}

for (const [n, pre, qs] of [[2, [[1, 0]], [[0, 1], [1, 0]]], [3, [[1, 2], [1, 0], [2, 0]], [[1, 0], [1, 2]]]])
  console.log(checkIfPrerequisite(n, pre, qs).join(" "));
''', java=r'''
import java.util.*;

public class CourseScheduleIV {
    static List<Boolean> checkIfPrerequisite(int n, int[][] prerequisites, int[][] queries) {
        boolean[][] reach = new boolean[n][n];             // reach[a][b]: a must come before b
        for (int[] p : prerequisites) reach[p[0]][p[1]] = true;
        for (int k = 0; k < n; k++)                        // Floyd-Warshall with "and" and "or" instead of "+" and "min"
            for (int i = 0; i < n; i++)
                if (reach[i][k])
                    for (int j = 0; j < n; j++) if (reach[k][j]) reach[i][j] = true;
        List<Boolean> out = new ArrayList<>();
        for (int[] q : queries) out.add(reach[q[0]][q[1]]);
        return out;
    }

    static void show(List<Boolean> a) {
        StringJoiner sj = new StringJoiner(" ");
        for (boolean b : a) sj.add(String.valueOf(b));
        System.out.println(sj);
    }

    public static void main(String[] args) {
        show(checkIfPrerequisite(2, new int[][]{{1, 0}}, new int[][]{{0, 1}, {1, 0}}));
        show(checkIfPrerequisite(3, new int[][]{{1, 2}, {1, 0}, {2, 0}}, new int[][]{{1, 0}, {1, 2}}));
    }
}
''', ts=r'''
function checkIfPrerequisite(numCourses: number, prerequisites: number[][], queries: number[][]): boolean[] {
  const n = numCourses;
  const reach: boolean[][] = Array.from({ length: n }, () => new Array(n).fill(false));   // reach[a][b]: a must come before b
  for (const [a, b] of prerequisites) reach[a][b] = true;
  for (let k = 0; k < n; k++)                 // Floyd-Warshall with "and" and "or" instead of "+" and "min"
    for (let i = 0; i < n; i++)
      if (reach[i][k])
        for (let j = 0; j < n; j++) if (reach[k][j]) reach[i][j] = true;
  return queries.map(([a, b]) => reach[a][b]);
}

const cases: [number, number[][], number[][]][] = [[2, [[1, 0]], [[0, 1], [1, 0]]], [3, [[1, 2], [1, 0], [2, 0]], [[1, 0], [1, 2]]]];
for (const [n, pre, qs] of cases) console.log(checkIfPrerequisite(n, pre, qs).join(" "));
''')

t.code('p_effort', py=r'''
import heapq


def minimum_effort_path(heights):
    R, C = len(heights), len(heights[0])
    best = [[float("inf")] * C for _ in range(R)]
    best[0][0] = 0
    heap = [(0, 0, 0)]                        # (effort so far, row, column)
    while heap:
        e, r, c = heapq.heappop(heap)
        if (r, c) == (R - 1, C - 1):
            return e
        if e > best[r][c]:
            continue
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C:
                ne = max(e, abs(heights[nr][nc] - heights[r][c]))   # a path costs its single biggest step
                if ne < best[nr][nc]:
                    best[nr][nc] = ne
                    heapq.heappush(heap, (ne, nr, nc))
    return 0


print(minimum_effort_path([[1, 2, 2], [3, 8, 2], [5, 3, 5]]))
print(minimum_effort_path([[1, 2, 3], [3, 8, 4], [5, 3, 5]]))
print(minimum_effort_path([[1, 2, 1, 1, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1], [1, 1, 1, 2, 1]]))
''', js=JS_HEAP + r'''
function minimumEffortPath(heights) {
  const R = heights.length, C = heights[0].length;
  const best = Array.from({ length: R }, () => new Array(C).fill(Infinity));
  best[0][0] = 0;
  const heap = new Heap((a, b) => a[0] < b[0]);   // [effort so far, row, column]
  heap.push([0, 0, 0]);
  while (heap.size) {
    const [e, r, c] = heap.pop();
    if (r === R - 1 && c === C - 1) return e;
    if (e > best[r][c]) continue;
    for (const [nr, nc] of [[r + 1, c], [r - 1, c], [r, c + 1], [r, c - 1]]) {
      if (nr < 0 || nr >= R || nc < 0 || nc >= C) continue;
      const ne = Math.max(e, Math.abs(heights[nr][nc] - heights[r][c]));   // a path costs its single biggest step
      if (ne < best[nr][nc]) { best[nr][nc] = ne; heap.push([ne, nr, nc]); }
    }
  }
  return 0;
}

console.log(minimumEffortPath([[1, 2, 2], [3, 8, 2], [5, 3, 5]]));
console.log(minimumEffortPath([[1, 2, 3], [3, 8, 4], [5, 3, 5]]));
console.log(minimumEffortPath([[1, 2, 1, 1, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1], [1, 1, 1, 2, 1]]));
''', java=r'''
import java.util.*;

public class MinimumEffort {
    static int minimumEffortPath(int[][] heights) {
        int R = heights.length, C = heights[0].length;
        int[][] best = new int[R][C];
        for (int[] row : best) Arrays.fill(row, Integer.MAX_VALUE);
        best[0][0] = 0;
        PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> a[0] - b[0]);   // {effort so far, row, column}
        heap.add(new int[]{0, 0, 0});
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!heap.isEmpty()) {
            int[] top = heap.poll();
            int e = top[0], r = top[1], c = top[2];
            if (r == R - 1 && c == C - 1) return e;
            if (e > best[r][c]) continue;
            for (int[] d : dirs) {
                int nr = r + d[0], nc = c + d[1];
                if (nr < 0 || nr >= R || nc < 0 || nc >= C) continue;
                int ne = Math.max(e, Math.abs(heights[nr][nc] - heights[r][c]));   // a path costs its single biggest step
                if (ne < best[nr][nc]) { best[nr][nc] = ne; heap.add(new int[]{ne, nr, nc}); }
            }
        }
        return 0;
    }

    public static void main(String[] args) {
        System.out.println(minimumEffortPath(new int[][]{{1, 2, 2}, {3, 8, 2}, {5, 3, 5}}));
        System.out.println(minimumEffortPath(new int[][]{{1, 2, 3}, {3, 8, 4}, {5, 3, 5}}));
        System.out.println(minimumEffortPath(new int[][]{{1, 2, 1, 1, 1}, {1, 2, 1, 2, 1}, {1, 2, 1, 2, 1}, {1, 2, 1, 2, 1}, {1, 1, 1, 2, 1}}));
    }
}
''', ts=TS_HEAP + r'''
function minimumEffortPath(heights: number[][]): number {
  const R = heights.length, C = heights[0].length;
  const best: number[][] = Array.from({ length: R }, () => new Array(C).fill(Infinity));
  best[0][0] = 0;
  const heap = new Heap<[number, number, number]>((a, b) => a[0] < b[0]);   // [effort so far, row, column]
  heap.push([0, 0, 0]);
  while (heap.size) {
    const [e, r, c] = heap.pop();
    if (r === R - 1 && c === C - 1) return e;
    if (e > best[r][c]) continue;
    for (const [nr, nc] of [[r + 1, c], [r - 1, c], [r, c + 1], [r, c - 1]]) {
      if (nr < 0 || nr >= R || nc < 0 || nc >= C) continue;
      const ne = Math.max(e, Math.abs(heights[nr][nc] - heights[r][c]));   // a path costs its single biggest step
      if (ne < best[nr][nc]) { best[nr][nc] = ne; heap.push([ne, nr, nc]); }
    }
  }
  return 0;
}

console.log(minimumEffortPath([[1, 2, 2], [3, 8, 2], [5, 3, 5]]));
console.log(minimumEffortPath([[1, 2, 3], [3, 8, 4], [5, 3, 5]]));
console.log(minimumEffortPath([[1, 2, 1, 1, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1], [1, 1, 1, 2, 1]]));
''')

t.code('p_itinerary', py=r'''
from collections import defaultdict


def find_itinerary(tickets):
    adj = defaultdict(list)
    for a, b in sorted(tickets, reverse=True):
        adj[a].append(b)                      # reverse order, so pop() gives the smallest airport first
    stack, route = ["JFK"], []
    while stack:                              # Hierholzer: walk until stuck, then write the airport down
        while adj[stack[-1]]:
            stack.append(adj[stack[-1]].pop())
        route.append(stack.pop())
    return route[::-1]


print(" ".join(find_itinerary([["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]])))
print(" ".join(find_itinerary([["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]])))
''', js=r'''
function findItinerary(tickets) {
  const adj = new Map();
  const sorted = [...tickets].sort((x, y) => (x[0] + x[1] < y[0] + y[1] ? 1 : -1));   // reverse order
  for (const [a, b] of sorted) {
    if (!adj.has(a)) adj.set(a, []);
    adj.get(a).push(b);                       // so pop() gives the smallest airport first
  }
  const stack = ["JFK"], route = [];
  while (stack.length) {                      // Hierholzer: walk until stuck, then write the airport down
    let next = adj.get(stack[stack.length - 1]);
    while (next && next.length) {
      stack.push(next.pop());
      next = adj.get(stack[stack.length - 1]);
    }
    route.push(stack.pop());
  }
  return route.reverse();
}

console.log(findItinerary([["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]]).join(" "));
console.log(findItinerary([["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]]).join(" "));
''', java=r'''
import java.util.*;

public class Itinerary {
    static List<String> findItinerary(String[][] tickets) {
        Map<String, PriorityQueue<String>> adj = new HashMap<>();      // each airport's destinations, smallest first
        for (String[] t : tickets) adj.computeIfAbsent(t[0], k -> new PriorityQueue<>()).add(t[1]);
        Deque<String> stack = new ArrayDeque<>(List.of("JFK"));
        LinkedList<String> route = new LinkedList<>();
        while (!stack.isEmpty()) {                                   // Hierholzer: walk until stuck, then write the airport down
            PriorityQueue<String> next = adj.get(stack.peek());
            while (next != null && !next.isEmpty()) {
                stack.push(next.poll());
                next = adj.get(stack.peek());
            }
            route.addFirst(stack.pop());
        }
        return route;
    }

    public static void main(String[] args) {
        System.out.println(String.join(" ", findItinerary(new String[][]{{"MUC", "LHR"}, {"JFK", "MUC"}, {"SFO", "SJC"}, {"LHR", "SFO"}})));
        System.out.println(String.join(" ", findItinerary(new String[][]{{"JFK", "SFO"}, {"JFK", "ATL"}, {"SFO", "ATL"}, {"ATL", "JFK"}, {"ATL", "SFO"}})));
    }
}
''', ts=r'''
function findItinerary(tickets: string[][]): string[] {
  const adj = new Map<string, string[]>();
  const sorted = [...tickets].sort((x, y) => (x[0] + x[1] < y[0] + y[1] ? 1 : -1));   // reverse order
  for (const [a, b] of sorted) {
    if (!adj.has(a)) adj.set(a, []);
    adj.get(a)!.push(b);                      // so pop() gives the smallest airport first
  }
  const stack = ["JFK"], route: string[] = [];
  while (stack.length) {                      // Hierholzer: walk until stuck, then write the airport down
    let next = adj.get(stack[stack.length - 1]);
    while (next && next.length) {
      stack.push(next.pop()!);
      next = adj.get(stack[stack.length - 1]);
    }
    route.push(stack.pop()!);
  }
  return route.reverse();
}

console.log(findItinerary([["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]]).join(" "));
console.log(findItinerary([["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]]).join(" "));
''')

t.code('p_swim', py=r'''
import heapq


def swim_in_water(grid):
    n = len(grid)
    seen = {(0, 0)}
    heap = [(grid[0][0], 0, 0)]               # (highest cell on the way so far, row, column)
    while heap:
        t, r, c = heapq.heappop(heap)         # always step into the lowest cell we can see
        if (r, c) == (n - 1, n - 1):
            return t
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in seen:
                seen.add((nr, nc))
                heapq.heappush(heap, (max(t, grid[nr][nc]), nr, nc))
    return -1


print(swim_in_water([[0, 2], [1, 3]]))
print(swim_in_water([[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16], [11, 17, 18, 19, 20], [10, 9, 8, 7, 6]]))
''', js=JS_HEAP + r'''
function swimInWater(grid) {
  const n = grid.length;
  const seen = new Set([0]);
  const heap = new Heap((a, b) => a[0] < b[0]);   // [highest cell on the way so far, row, column]
  heap.push([grid[0][0], 0, 0]);
  while (heap.size) {
    const [t, r, c] = heap.pop();             // always step into the lowest cell we can see
    if (r === n - 1 && c === n - 1) return t;
    for (const [nr, nc] of [[r + 1, c], [r - 1, c], [r, c + 1], [r, c - 1]]) {
      if (nr >= 0 && nr < n && nc >= 0 && nc < n && !seen.has(nr * n + nc)) {
        seen.add(nr * n + nc);
        heap.push([Math.max(t, grid[nr][nc]), nr, nc]);
      }
    }
  }
  return -1;
}

console.log(swimInWater([[0, 2], [1, 3]]));
console.log(swimInWater([[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16], [11, 17, 18, 19, 20], [10, 9, 8, 7, 6]]));
''', java=r'''
import java.util.*;

public class SwimInWater {
    static int swimInWater(int[][] grid) {
        int n = grid.length;
        boolean[][] seen = new boolean[n][n];
        seen[0][0] = true;
        PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> a[0] - b[0]);   // {highest cell so far, row, column}
        heap.add(new int[]{grid[0][0], 0, 0});
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!heap.isEmpty()) {
            int[] top = heap.poll();                       // always step into the lowest cell we can see
            int t = top[0], r = top[1], c = top[2];
            if (r == n - 1 && c == n - 1) return t;
            for (int[] d : dirs) {
                int nr = r + d[0], nc = c + d[1];
                if (nr >= 0 && nr < n && nc >= 0 && nc < n && !seen[nr][nc]) {
                    seen[nr][nc] = true;
                    heap.add(new int[]{Math.max(t, grid[nr][nc]), nr, nc});
                }
            }
        }
        return -1;
    }

    public static void main(String[] args) {
        System.out.println(swimInWater(new int[][]{{0, 2}, {1, 3}}));
        System.out.println(swimInWater(new int[][]{{0, 1, 2, 3, 4}, {24, 23, 22, 21, 5}, {12, 13, 14, 15, 16}, {11, 17, 18, 19, 20}, {10, 9, 8, 7, 6}}));
    }
}
''', ts=TS_HEAP + r'''
function swimInWater(grid: number[][]): number {
  const n = grid.length;
  const seen = new Set<number>([0]);
  const heap = new Heap<[number, number, number]>((a, b) => a[0] < b[0]);   // [highest cell on the way so far, row, column]
  heap.push([grid[0][0], 0, 0]);
  while (heap.size) {
    const [t, r, c] = heap.pop();             // always step into the lowest cell we can see
    if (r === n - 1 && c === n - 1) return t;
    for (const [nr, nc] of [[r + 1, c], [r - 1, c], [r, c + 1], [r, c - 1]]) {
      if (nr >= 0 && nr < n && nc >= 0 && nc < n && !seen.has(nr * n + nc)) {
        seen.add(nr * n + nc);
        heap.push([Math.max(t, grid[nr][nc]), nr, nc]);
      }
    }
  }
  return -1;
}

console.log(swimInWater([[0, 2], [1, 3]]));
console.log(swimInWater([[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16], [11, 17, 18, 19, 20], [10, 9, 8, 7, 6]]));
''')

t.code('p_signs', py=r'''
from collections import deque


def min_cost(grid):
    R, C = len(grid), len(grid[0])
    moves = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}   # the sign in each cell: right, left, down, up
    cost = [[float("inf")] * C for _ in range(R)]
    cost[0][0] = 0
    dq = deque([(0, 0)])
    while dq:                                 # 0-1 BFS: free moves go to the front, paid moves to the back
        r, c = dq.popleft()
        for sign, (dr, dc) in moves.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C:
                w = 0 if grid[r][c] == sign else 1          # following the sign is free, changing it costs 1
                if cost[r][c] + w < cost[nr][nc]:
                    cost[nr][nc] = cost[r][c] + w
                    if w == 0:
                        dq.appendleft((nr, nc))
                    else:
                        dq.append((nr, nc))
    return cost[R - 1][C - 1]


print(min_cost([[1, 1, 1, 1], [2, 2, 2, 2], [1, 1, 1, 1], [2, 2, 2, 2]]))
print(min_cost([[1, 1, 3], [3, 2, 2], [1, 1, 4]]))
print(min_cost([[1, 2], [4, 3]]))
''', js=r'''
function minCost(grid) {
  const R = grid.length, C = grid[0].length;
  const moves = [[1, 0, 1], [2, 0, -1], [3, 1, 0], [4, -1, 0]];   // the sign in each cell: right, left, down, up
  const cost = Array.from({ length: R }, () => new Array(C).fill(Infinity));
  cost[0][0] = 0;
  const dq = [[0, 0]];
  while (dq.length) {                         // 0-1 BFS: free moves go to the front, paid moves to the back
    const [r, c] = dq.shift();
    for (const [sign, dr, dc] of moves) {
      const nr = r + dr, nc = c + dc;
      if (nr < 0 || nr >= R || nc < 0 || nc >= C) continue;
      const w = grid[r][c] === sign ? 0 : 1;  // following the sign is free, changing it costs 1
      if (cost[r][c] + w < cost[nr][nc]) {
        cost[nr][nc] = cost[r][c] + w;
        if (w === 0) dq.unshift([nr, nc]); else dq.push([nr, nc]);
      }
    }
  }
  return cost[R - 1][C - 1];
}

console.log(minCost([[1, 1, 1, 1], [2, 2, 2, 2], [1, 1, 1, 1], [2, 2, 2, 2]]));
console.log(minCost([[1, 1, 3], [3, 2, 2], [1, 1, 4]]));
console.log(minCost([[1, 2], [4, 3]]));
''', java=r'''
import java.util.*;

public class MinCostSigns {
    static int minCost(int[][] grid) {
        int R = grid.length, C = grid[0].length;
        int[][] moves = {{1, 0, 1}, {2, 0, -1}, {3, 1, 0}, {4, -1, 0}};   // the sign in each cell: right, left, down, up
        int[][] cost = new int[R][C];
        for (int[] row : cost) Arrays.fill(row, Integer.MAX_VALUE);
        cost[0][0] = 0;
        Deque<int[]> dq = new ArrayDeque<>();
        dq.add(new int[]{0, 0});
        while (!dq.isEmpty()) {                            // 0-1 BFS: free moves go to the front, paid moves to the back
            int[] cur = dq.pollFirst();
            int r = cur[0], c = cur[1];
            for (int[] m : moves) {
                int nr = r + m[1], nc = c + m[2];
                if (nr < 0 || nr >= R || nc < 0 || nc >= C) continue;
                int w = grid[r][c] == m[0] ? 0 : 1;        // following the sign is free, changing it costs 1
                if (cost[r][c] + w < cost[nr][nc]) {
                    cost[nr][nc] = cost[r][c] + w;
                    if (w == 0) dq.addFirst(new int[]{nr, nc}); else dq.addLast(new int[]{nr, nc});
                }
            }
        }
        return cost[R - 1][C - 1];
    }

    public static void main(String[] args) {
        System.out.println(minCost(new int[][]{{1, 1, 1, 1}, {2, 2, 2, 2}, {1, 1, 1, 1}, {2, 2, 2, 2}}));
        System.out.println(minCost(new int[][]{{1, 1, 3}, {3, 2, 2}, {1, 1, 4}}));
        System.out.println(minCost(new int[][]{{1, 2}, {4, 3}}));
    }
}
''', ts=r'''
function minCost(grid: number[][]): number {
  const R = grid.length, C = grid[0].length;
  const moves: [number, number, number][] = [[1, 0, 1], [2, 0, -1], [3, 1, 0], [4, -1, 0]];   // right, left, down, up
  const cost: number[][] = Array.from({ length: R }, () => new Array(C).fill(Infinity));
  cost[0][0] = 0;
  const dq: [number, number][] = [[0, 0]];
  while (dq.length) {                         // 0-1 BFS: free moves go to the front, paid moves to the back
    const [r, c] = dq.shift()!;
    for (const [sign, dr, dc] of moves) {
      const nr = r + dr, nc = c + dc;
      if (nr < 0 || nr >= R || nc < 0 || nc >= C) continue;
      const w = grid[r][c] === sign ? 0 : 1;  // following the sign is free, changing it costs 1
      if (cost[r][c] + w < cost[nr][nc]) {
        cost[nr][nc] = cost[r][c] + w;
        if (w === 0) dq.unshift([nr, nc]); else dq.push([nr, nc]);
      }
    }
  }
  return cost[R - 1][C - 1];
}

console.log(minCost([[1, 1, 1, 1], [2, 2, 2, 2], [1, 1, 1, 1], [2, 2, 2, 2]]));
console.log(minCost([[1, 1, 3], [3, 2, 2], [1, 1, 4]]));
console.log(minCost([[1, 2], [4, 3]]));
''')

t.leet(743, 'e', 'p_delay',
       statement='<p>A signal starts at node k and travels along directed edges with travel times. Return how long until every node has received it, or −1 if some node never does.</p>',
       example='times [[2,1,1],[2,3,1],[3,4,1]], n 4, k 2  →  2\n[[1,2,1]], n 2, k 1                        →  1\n[[1,2,1]], n 2, k 2                        →  −1',
       hint='The answer is the largest shortest distance from k.',
       approach='<p>Run Dijkstra from k with a min heap of (time, node). The first time a node is popped, its time is final. When the heap is empty, any node without a time is unreachable, so the answer is −1. Otherwise the answer is the biggest time. Every weight is positive here, so Bellman-Ford is not needed, but it would also work in O(V E).</p>',
       time='O(E log V)', space='O(V + E)')
t.leet(1334, 'e', 'p_city',
       statement='<p>Cities are joined by two way roads with lengths. For each city, count the other cities within the distance threshold. Return the city with the fewest, and the biggest number on a tie.</p>',
       example='n 4, [[0,1,3],[1,2,1],[1,3,4],[2,3,1]], threshold 4  →  3\nn 5, six roads, threshold 2                         →  0',
       hint='You need the distance between every pair of cities.',
       approach='<p>With at most 100 cities, Floyd-Warshall fits easily. Fill the matrix with the roads in both directions, run the three loops, then count for each city how many others are within the threshold. Walking the cities in order and keeping the city when its count is less than or equal to the best so far gives the biggest number on a tie.</p>',
       time='O(n³)', space='O(n²)')
t.leet(1514, 'm', 'p_prob',
       statement='<p>Each undirected edge succeeds with some probability. Return the highest probability of getting from start to end, or 0 if there is no path.</p>',
       example='probs 0.5, 0.5, 0.2  →  0.25000\nprobs 0.5, 0.5, 0.3  →  0.30000\nno path               →  0.00000',
       hint='Multiplying by a number at most 1 never makes a path better, just like adding a positive weight.',
       approach='<p>This is Dijkstra turned upside down. Keep the best probability for each node and a max heap. Pop the node with the highest probability, and try to improve its neighbours by multiplying with the edge probability. Because every factor is at most 1, a popped node can never improve later, which is the same reason Dijkstra works for positive weights. The answers are printed with five decimals so every language shows the same text.</p>',
       time='O(E log V)', space='O(V + E)')
t.leet(1462, 'm', 'p_courses', title='Course Schedule IV', url='https://leetcode.com/problems/course-schedule-iv/', diff='Medium',
       statement='<p>Given direct prerequisite pairs, answer queries of the form: must course a be taken before course b, directly or through a chain?</p>',
       example='n 2, [[1,0]], queries [[0,1],[1,0]]                 →  false true\nn 3, [[1,2],[1,0],[2,0]], queries [[1,0],[1,2]]     →  true true',
       hint='Which pairs can reach which? Compute it once for all pairs.',
       approach='<p>Build a reachability matrix and run Floyd-Warshall with logic instead of numbers: i reaches j if i already reaches j, or i reaches k and k reaches j. This is called the transitive closure. With at most 100 courses the three loops are cheap, and each query is then a single lookup.</p>',
       time='O(n³ + q)', space='O(n²)')
t.leet(1631, 'h', 'p_effort',
       statement='<p>Walk from the top left to the bottom right of a height map. The effort of a route is its single biggest height difference between neighbouring cells. Return the smallest possible effort.</p>',
       example='[[1,2,2],[3,8,2],[5,3,5]]   →  2\n[[1,2,3],[3,8,4],[5,3,5]]   →  1\na flat corridor of 1s      →  0',
       hint='Dijkstra still works if the cost of a path is a maximum instead of a sum.',
       approach='<p>Treat each cell as a node. The cost of stepping to a neighbour is max(current effort, height difference). That cost never goes down along a path, so Dijkstra with a min heap pops each cell at its best effort. The first time the bottom right corner is popped, its effort is the answer.</p>',
       time='O(R C log(R C))', space='O(R C)')
t.leet(332, 'h', 'p_itinerary', title='Reconstruct Itinerary', url='https://leetcode.com/problems/reconstruct-itinerary/', diff='Hard',
       statement='<p>Use every plane ticket exactly once, starting from JFK. If several itineraries work, return the one that comes first in alphabetical order.</p>',
       example='MUC-LHR, JFK-MUC, SFO-SJC, LHR-SFO          →  JFK MUC LHR SFO SJC\nJFK-SFO, JFK-ATL, SFO-ATL, ATL-JFK, ATL-SFO  →  JFK ATL JFK SFO ATL SFO',
       hint='Using every edge exactly once is an Euler path.',
       approach='<p>Run Hierholzer\'s algorithm. Keep each airport\'s destinations so the smallest comes out first. Walk from JFK taking the smallest unused ticket each time. When an airport has no tickets left, it is finished, so pop it onto the answer. The answer comes out backwards, so reverse it at the end. Getting stuck early is safe because the stuck part is spliced in at the right place automatically.</p>',
       time='O(E log E)', space='O(E)')
t.leet(778, 'x', 'p_swim', title='Swim in Rising Water', url='https://leetcode.com/problems/swim-in-rising-water/', diff='Hard',
       statement='<p>Cell (i, j) has height grid[i][j]. At time t the water level is t, and you can swim between neighbouring cells whose heights are both at most t. Return the least time to get from the top left to the bottom right.</p>',
       example='[[0,2],[1,3]]           →  3\nthe 5 × 5 spiral grid  →  16',
       hint='The time needed for a route is the highest cell on it.',
       approach='<p>Always step into the lowest cell you can currently see. A min heap holds the frontier cells keyed by the highest cell on the way to them. Each pop is the cheapest cell to reach next, exactly as in Dijkstra with a maximum instead of a sum. When the bottom right corner is popped, its key is the answer.</p>',
       time='O(n² log n)', space='O(n²)')
t.leet(1368, 'x', 'p_signs', title='Minimum Cost to Make at Least One Valid Path in a Grid', url='https://leetcode.com/problems/minimum-cost-to-make-at-least-one-valid-path-in-a-grid/', diff='Hard',
       statement='<p>Each cell has a sign pointing right, left, down or up (1 to 4). Following a sign is free. Changing a sign costs 1. Return the least cost to make a path from the top left to the bottom right.</p>',
       example='[[1,1,1,1],[2,2,2,2],[1,1,1,1],[2,2,2,2]]  →  3\n[[1,1,3],[3,2,2],[1,1,4]]                  →  0\n[[1,2],[4,3]]                              →  1',
       hint='Every move costs 0 or 1. There is a faster tool than a heap for that.',
       approach='<p>Use 0-1 BFS with a double ended queue. A move that follows the sign costs 0, so the next cell goes to the front. A move against the sign costs 1, so it goes to the back. The queue then always holds cells in order of cost, like Dijkstra, without any heap. Java uses <code>ArrayDeque</code>, Python <code>collections.deque</code>, and the JavaScript version uses an array with <code>unshift</code>, which is fine for small grids.</p>',
       time='O(R C)', space='O(R C)')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='bellman-ford', emoji='➖', title='Negative edges and Bellman-Ford', html='''
<p>Dijkstra settles a node for good the moment it is popped. That is only safe when every edge is positive. With a negative edge, a longer detour can turn out cheaper, and Dijkstra never looks back. <b>Bellman-Ford</b> is slower but patient: it relaxes every edge, again and again, for n − 1 rounds.</p>
<div class="viz" data-viz="pk" data-pk="bellman"></div>
<div class="c3" data-k="bellman" data-label="Bellman-Ford with an early stop and a cycle check"></div>
<span class="eq">relax(u, v, w): if dist[u] + w &lt; dist[v] then dist[v] = dist[u] + w</span>
<div class="rule">A shortest path uses at most n − 1 edges, so n − 1 rounds are enough. If a distance still drops in one extra round, the graph has a negative cycle and no shortest path exists.</div>
<div class="exam">Bellman-Ford costs O(V E). Network routers that use the distance vector idea, such as the old RIP protocol, share distances with their neighbours in the same way.</div>
'''),
    dict(id='floyd-warshall', emoji='🗺️', title='All pairs with Floyd-Warshall', html='''
<p>Sometimes you need the distance between every pair of places, like a road atlas table. <b>Floyd-Warshall</b> fills an n × n matrix with three nested loops. In round k, every pair i, j asks one question: is going through node k shorter than what I have?</p>
<div class="viz" data-viz="pk" data-pk="floyd"></div>
<div class="c3" data-k="floyd" data-label="Floyd-Warshall with path reconstruction"></div>
<span class="eq">d[i][j] = min(d[i][j], d[i][k] + d[k][j]) &nbsp; for k, then i, then j</span>
<div class="tip">It handles negative edges too. A negative number on the diagonal at the end means a negative cycle. Swapping + and min for "and" and "or" gives reachability, which LeetCode 1462 uses.</div>
'''),
    dict(id='scc', emoji='🫧', title='Strongly connected components', html='''
<p>In a directed graph, a <b>strongly connected component</b> is a largest group of nodes where every node can reach every other node. <b>Kosaraju\'s algorithm</b> finds them with two depth first searches. Pass 1 records the order in which nodes finish. Pass 2 reverses every edge and starts from the latest finisher. Each search in pass 2 stays trapped inside exactly one component.</p>
<div class="viz" data-viz="pk" data-pk="scc"></div>
<div class="c3" data-k="scc" data-label="Kosaraju in two passes"></div>
<div class="exam">Squashing each component into one node always leaves a graph with no cycles. Compilers use this to find groups of modules that depend on each other, and 2-SAT solvers use it to decide whether a set of rules can all hold.</div>
'''),
    dict(id='bridges', emoji='🌉', title='Bridges and articulation points', html='''
<p>A <b>bridge</b> is an edge whose removal splits the graph in two. An <b>articulation point</b>, or cut point, is a node whose removal does. One depth first search finds both. Each node gets a discovery time d, and a low value l: the smallest discovery time its subtree can reach with one back edge.</p>
<div class="viz" data-viz="pk" data-pk="bridges"></div>
<div class="c3" data-k="bridges" data-label="Tarjan\'s low link method"></div>
<div class="tw"><table class="jt"><tr><th>Test after visiting child v of u</th><th>Meaning</th></tr>
<tr><td>l[v] &gt; d[u]</td><td>the edge u-v is a bridge</td></tr>
<tr><td>l[v] ≥ d[u], u is not the root</td><td>u is a cut point</td></tr>
<tr><td>the root has 2 or more children</td><td>the root is a cut point</td></tr></table></div>
<div class="tip">The Graphs chapter practice problem Critical Connections asks for exactly these bridges.</div>
'''),
    dict(id='max-flow', emoji='🚰', title='Maximum flow and minimum cut', html='''
<p>Each pipe has a capacity. How much water per second can flow from the source s to the sink t? <b>Edmonds-Karp</b> repeats one step: find the shortest path from s to t where every pipe still has room, and push as much as the tightest pipe allows. Pushing also opens a reverse pipe, so a later path can take back flow that was badly placed.</p>
<div class="viz" data-viz="pk" data-pk="flow"></div>
<div class="c3" data-k="flow" data-label="Edmonds-Karp with the minimum cut"></div>
<div class="rule">Max flow equals min cut. When no path is left, the nodes still reachable from s form one side of a cut, and the full pipes crossing it add up to exactly the maximum flow.</div>
<div class="exam">Edmonds-Karp costs O(V E²). Matching students to projects or workers to jobs is a flow problem: one unit of capacity per person and per job.</div>
'''),
    dict(id='a-star', emoji='⭐', title='A* search: Dijkstra with a sense of direction', html='''
<p>Dijkstra spreads out evenly in every direction. <b>A*</b> adds a guess h of the distance still to go, and always expands the open node with the smallest f = g + h, where g is the distance travelled so far. On a grid with four moves, the Manhattan distance is a good guess.</p>
<div class="viz" data-viz="pk" data-pk="astar"></div>
<div class="c3" data-k="astar" data-label="A* and Dijkstra on the same grid"></div>
<span class="eq">f(n) = g(n) + h(n) &nbsp;&nbsp; Manhattan h = |row − goal row| + |col − goal col|</span>
<div class="warn">The guess must never overestimate the real distance. If it does, A* can return a path that is not the shortest. With h = 0, A* is exactly Dijkstra.</div>
'''),
    dict(id='euler', emoji='✏️', title='Euler paths with Hierholzer', html='''
<p>An <b>Euler circuit</b> uses every edge exactly once and returns to the start. Leonhard Euler asked this about the seven bridges of Königsberg in 1736. In a directed graph it exists when every node has in degree equal to out degree and all edges belong to one connected piece. <b>Hierholzer\'s algorithm</b> walks unused edges until it gets stuck, writes the stuck node down, steps back, and continues. The answer comes out reversed.</p>
<div class="viz" data-viz="pk" data-pk="euler"></div>
<div class="c3" data-k="euler" data-label="Hierholzer with a stack"></div>
<div class="exam">An Euler path, which may end somewhere else, needs one node with out − in = 1 as the start and one with in − out = 1 as the end. LeetCode 332 Reconstruct Itinerary is this problem with airport names.</div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem is solved in the Practice section in Python, JavaScript, Java and TypeScript, with line by line replay. JavaScript and TypeScript use the same small heap class as the Heaps chapter.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>The graph idea</th></tr>
<tr><td><a href="#lc743">743. Network Delay Time</a></td><td>Easy</td><td>single source shortest paths</td></tr>
<tr><td><a href="#lc1334">1334. Find the City With the Smallest Number of Neighbors at a Threshold Distance</a></td><td>Easy</td><td>Floyd-Warshall</td></tr>
<tr><td><a href="#lc1514">1514. Path with Maximum Probability</a></td><td>Medium</td><td>Dijkstra with products</td></tr>
<tr><td><a href="#lc1462">1462. Course Schedule IV</a></td><td>Medium</td><td>reachability for all pairs</td></tr>
<tr><td><a href="#lc1631">1631. Path With Minimum Effort</a></td><td>Hard</td><td>Dijkstra with a maximum</td></tr>
<tr><td><a href="#lc332">332. Reconstruct Itinerary</a></td><td>Hard</td><td>Euler path with Hierholzer</td></tr>
<tr><td><a href="#lc778">778. Swim in Rising Water</a></td><td>Expert</td><td>always the lowest next cell</td></tr>
<tr><td><a href="#lc1368">1368. Minimum Cost to Make at Least One Valid Path in a Grid</a></td><td>Expert</td><td>0-1 BFS with a deque</td></tr></table></div>
'''),
]

VIZ_JS = r'''
(() => {
  const D = PK.defs;
  const INF = 1e9;
  const fmt = d => (d >= INF / 2 ? '∞' : String(d));
  const gr = (label, P, edges, o = {}) => ({ t: 'graph', label, w: o.w || 480, h: o.h || 270, dir: o.dir !== false, nodes: P.map(p => [p[0], p[1], p[2], p[3]]), edges, ncls: o.ncls || {}, ecls: o.ecls || {}, tag: o.tag || {} });
  const arrow = ' → ';
  const plus = (a, w) => (w < 0 ? `${a} − ${-w}` : `${a} + ${w}`);

  /* ---------- Bellman-Ford ---------- */
  const BF = {
    clrs: { names: ['s', 't', 'x', 'y', 'z'], pos: [[50, 135], [185, 45], [345, 45], [185, 225], [345, 225]],
            edges: [[1, 2, 5], [1, 3, 8], [1, 4, -4], [2, 1, -2], [3, 2, -3], [3, 4, 9], [4, 2, 7], [4, 0, 2], [0, 1, 6], [0, 3, 7]] },
    cycle: { names: ['s', 'a', 'b'], pos: [[70, 135], [250, 60], [410, 200]], edges: [[0, 1, 1], [1, 2, -1], [2, 1, -1]] },
  };
  D.bellman = el => PK.widget(el, {
    title: 'Bellman-Ford with negative edges', sub: 'Relax every edge, round after round. A change after n − 1 rounds means a negative cycle.',
    inputs: [{ k: 'g', label: 'Graph', type: 'seg', val: 'clrs', opts: [['clrs', '➖ Negative edges'], ['cycle', '🌀 Negative cycle']] }],
    frames: ({ g }) => {
      const G = BF[g], n = G.names.length, N = G.names, F = [];
      const P = G.pos.map((p, i) => [N[i], p[0], p[1]]);
      const E = G.edges.map(([u, v, w]) => [N[u], N[v], w]);
      const dist = new Array(n).fill(INF);
      dist[0] = 0;
      const pic = (ncls = {}, ecls = {}) => [gr('Distances from s under each node', P, E, { ncls, ecls, tag: Object.fromEntries(N.map((x, i) => [x, fmt(dist[i])])) })];
      F.push({ mood: 'think', msg: `Start: s is 0 away from itself and every other node is ∞. There are ${n} nodes, so ${n - 1} rounds are always enough.`, vars: { round: 0 }, layers: pic({ s: 'yes' }) });
      let rounds = 0;
      for (let rnd = 1; rnd < n; rnd++) {
        rounds = rnd;
        let changed = 0;
        for (const [u, v, w] of G.edges) {
          if (dist[u] === INF || dist[u] + w >= dist[v]) continue;
          const old = dist[v];
          dist[v] = dist[u] + w;
          changed++;
          F.push({ mood: w < 0 ? 'wow' : 'work', msg: `Round ${rnd}, edge ${N[u]}${arrow}${N[v]} (${w}): ${plus(dist[u], w)} = <b>${dist[v]}</b>, better than ${fmt(old)}.${w < 0 ? ' A negative edge made a path cheaper.' : ''}`, vars: { round: rnd, improved: changed }, layers: pic({ [N[u]]: 'cur', [N[v]]: 'yes' }, { [N[u] + '-' + N[v]]: 'yes' }) });
        }
        if (!changed) {
          F.push({ mood: 'happy', msg: `Round ${rnd} changed nothing, so every distance is final. Stop early.`, vars: { round: rnd, improved: 0 }, layers: pic() });
          break;
        }
        F.push({ mood: 'look', msg: `Round ${rnd} done: ${changed} distance${changed === 1 ? '' : 's'} improved.`, vars: { round: rnd, improved: changed }, layers: pic() });
      }
      const bad = G.edges.find(([u, v, w]) => dist[u] !== INF && dist[u] + w < dist[v]);
      if (bad) {
        const [u, v, w] = bad;
        F.push({ mood: 'sad', fx: 'shake', msg: `Extra check: edge ${N[u]}${arrow}${N[v]} could still drop to ${dist[u] + w}. After ${n - 1} rounds that is only possible with a <b>negative cycle</b>, where going round again always gets cheaper. No shortest path exists.`, vars: { round: 'check' }, layers: pic({ [N[u]]: 'no', [N[v]]: 'no' }, { [N[u] + '-' + N[v]]: 'no' }) });
      } else {
        F.push({ mood: 'wow', fx: 'rain', msg: `Extra check passed, so there is no negative cycle. Final distances: ${N.map((x, i) => `${x} ${fmt(dist[i])}`).join(', ')}.`, vars: { rounds }, layers: pic(Object.fromEntries(N.map(x => [x, 'yes']))) });
      }
      return F;
    }
  });

  /* ---------- Floyd-Warshall ---------- */
  D.floyd = el => PK.widget(el, {
    title: 'Floyd-Warshall, every pair at once', sub: 'Round k allows node k as a stop in the middle. A cell drops when going through k is shorter.',
    frames: () => {
      const n = 4, F = [], ids = ['0', '1', '2', '3'];
      const P = [['0', 90, 55], ['1', 390, 55], ['2', 390, 215], ['3', 90, 215]];
      const EE = [[0, 1, 3], [0, 3, 7], [1, 0, 8], [1, 2, 2], [2, 0, 5], [2, 3, 1], [3, 0, 2]];
      const E = EE.map(([u, v, w]) => [ids[u], ids[v], w]);
      const d = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 0 : INF)));
      EE.forEach(([u, v, w]) => { d[u][v] = w; });
      const pic = (ncls = {}, cls = {}) => [gr('The roads', P, E, { ncls, h: 260 }),
        { t: 'grid', label: 'Shortest distance from row to column', rows: d.map(r => r.map(fmt)), rlab: ids.map(i => 'from ' + i), clab: ids.map(i => 'to ' + i), cls }];
      F.push({ mood: 'think', msg: 'Start with the direct roads only. ∞ means there is no direct road.', vars: { k: '-' }, layers: pic() });
      let checks = 0, drops = 0;
      for (let k = 0; k < n; k++) {
        const band = {};
        for (let x = 0; x < n; x++) { band[k + ',' + x] = 'cur'; band[x + ',' + k] = 'cur'; }
        F.push({ mood: 'look', msg: `Round ${k}: may a path stop at node ${k} on the way? Row ${k} and column ${k} hold the two halves.`, vars: { k, drops }, layers: pic({ [k]: 'piv' }, band) });
        for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
          checks++;
          if (d[i][k] + d[k][j] < d[i][j]) {
            const old = d[i][j];
            d[i][j] = d[i][k] + d[k][j];
            drops++;
            F.push({ mood: 'wow', fx: 'burst', msg: `${i}${arrow}${k}${arrow}${j} costs ${d[i][k]} + ${d[k][j]} = <b>${d[i][j]}</b>, better than ${fmt(old)}.`, vars: { k, drops }, layers: pic({ [k]: 'piv', [i]: 'look', [j]: 'yes' }, Object.assign({}, band, { [i + ',' + j]: 'yes' })) });
          }
        }
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `Done after ${n} rounds and ${checks} checks, n³ for n = ${n}. Every cell is now the true shortest distance.`, vars: { k: 'done', drops }, layers: pic() });
      return F;
    }
  });

  /* ---------- Kosaraju ---------- */
  D.scc = el => PK.widget(el, {
    title: 'Strongly connected components', sub: 'Pass 1 records finish order. Pass 2 walks the reversed graph, latest finisher first.',
    frames: () => {
      const n = 8, ids = [...Array(n).keys()].map(String), F = [];
      const P = [['0', 50, 70], ['1', 160, 35], ['2', 130, 170], ['3', 245, 110], ['4', 355, 45], ['5', 345, 190], ['6', 450, 220], ['7', 460, 80]];
      const EE = [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 5], [5, 3], [6, 5], [6, 7], [7, 6]];
      const adj = ids.map(() => []), radj = ids.map(() => []);
      EE.forEach(([u, v]) => { adj[u].push(v); radj[v].push(u); });
      const E = EE.map(([u, v]) => [String(u), String(v)]), RE = EE.map(([u, v]) => [String(v), String(u)]);
      const seen = new Array(n).fill(false), order = [], ncls = {};
      const pic = (edges, label, extra = {}) => [gr(label, P, edges, { ncls: Object.assign({}, ncls, extra), w: 500 }), { t: 'row', label: 'Finish order', cells: order.slice(), idx: false }];
      F.push({ mood: 'think', msg: 'A strongly connected component is a group where every node can reach every other. Pass 1: depth first search, writing each node down when it finishes.', vars: { pass: 1 }, layers: pic(E, 'The graph') });
      const dfs1 = u => {
        seen[u] = true;
        ncls[u] = 'look';
        F.push({ mood: 'look', msg: `Visit ${u}.`, vars: { pass: 1 }, layers: pic(E, 'Pass 1 on the graph') });
        for (const v of adj[u]) if (!seen[v]) dfs1(v);
        order.push(u);
        ncls[u] = 'done';
        F.push({ mood: 'work', msg: `${u} has nowhere new to go, so it finishes. Finish order: ${order.join(' ')}.`, vars: { pass: 1 }, layers: pic(E, 'Pass 1 on the graph') });
      };
      for (let u = 0; u < n; u++) if (!seen[u]) dfs1(u);
      ids.forEach(i => { delete ncls[i]; });
      F.push({ mood: 'wow', msg: 'Now turn every edge around. Components stay the same, but the edges that led out of a component now lead into it.', vars: { pass: 2 }, layers: pic(RE, 'Every edge reversed') });
      const comp = new Array(n).fill(-1), pal = ['yes', 'piv', 'mv', 'cur'];
      let c = 0;
      const dfs2 = (u, k) => { comp[u] = k; ncls[u] = pal[k % 4]; for (const v of radj[u]) if (comp[v] === -1) dfs2(v, k); };
      for (const u of [...order].reverse()) {
        if (comp[u] !== -1) continue;
        dfs2(u, c);
        const members = ids.filter(x => comp[x] === c);
        F.push({ mood: 'wow', fx: 'burst', msg: `Start at ${u}, the latest finisher not yet coloured. On the reversed edges it reaches exactly {${members.join(', ')}}: component ${c + 1}.`, vars: { pass: 2, components: c + 1 }, layers: pic(RE, 'Pass 2 on the reversed graph') });
        c++;
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `${c} components. Squash each one into a single dot and the result has no cycles at all.`, vars: { components: c }, layers: pic(E, 'Components on the original graph') });
      return F;
    }
  });

  /* ---------- bridges and articulation points ---------- */
  D.bridges = el => PK.widget(el, {
    title: 'Bridges and cut points', sub: 'Each node gets a discovery time d and a low value l: the earliest time its subtree can climb back to.',
    frames: () => {
      const n = 7, F = [];
      const P = [['0', 55, 55], ['1', 165, 130], ['2', 55, 210], ['3', 285, 130], ['4', 400, 60], ['5', 400, 205], ['6', 500, 60]];
      const EE = [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4], [4, 5], [5, 3], [4, 6]];
      const adj = [...Array(n)].map(() => []);
      EE.forEach(([u, v]) => { adj[u].push(v); adj[v].push(u); });
      const E = EE.map(([u, v]) => [String(u), String(v)]);
      const disc = new Array(n).fill(-1), low = new Array(n).fill(0), ncls = {}, ecls = {}, cuts = new Set(), bridges = [];
      let timer = 0;
      const key = (u, v) => (EE.some(([a, b]) => a === u && b === v) ? `${u}-${v}` : `${v}-${u}`);
      const pic = (extraN = {}) => [gr('Undirected graph, tags show d/l', P, E, { dir: false, w: 530, ncls: Object.assign({}, ncls, extraN), ecls, tag: Object.fromEntries([...Array(n).keys()].filter(i => disc[i] >= 0).map(i => [i, `${disc[i]}/${low[i]}`])) })];
      F.push({ mood: 'think', msg: 'A bridge is an edge whose removal splits the graph. A cut point is a node whose removal does. One depth first search finds them all.', layers: pic() });
      const dfs = (u, parent) => {
        disc[u] = low[u] = timer++;
        ncls[u] = 'look';
        F.push({ mood: 'look', msg: `Visit ${u}: d = l = ${disc[u]}.`, vars: { time: timer }, layers: pic() });
        let kids = 0;
        for (const v of adj[u]) {
          if (v === parent) continue;
          if (disc[v] !== -1) {
            if (disc[v] < low[u]) {
              low[u] = disc[v];
              ecls[key(u, v)] = 'look';
              F.push({ mood: 'wow', msg: `Back edge ${u}-${v} to an earlier node. l[${u}] drops to ${low[u]}.`, vars: { time: timer }, layers: pic() });
            }
            continue;
          }
          kids++;
          ecls[key(u, v)] = 'cur';
          dfs(v, u);
          low[u] = Math.min(low[u], low[v]);
          ncls[u] = 'look';
          if (low[v] > disc[u]) {
            bridges.push(`${u}-${v}`);
            ecls[key(u, v)] = 'no';
            F.push({ mood: 'wow', fx: 'shake', msg: `Back at ${u}: l[${v}] = ${low[v]} is bigger than d[${u}] = ${disc[u]}. Nothing below ${v} can climb back past this edge, so the edge ${u}-${v} is a <b>bridge</b>.`, layers: pic() });
          } else {
            F.push({ mood: 'work', msg: `Back at ${u}: l[${v}] = ${low[v]}, so l[${u}] = ${low[u]}.`, layers: pic() });
          }
          if (parent !== -1 && low[v] >= disc[u] && !cuts.has(u)) {
            cuts.add(u);
            ncls[u] = 'piv';
            F.push({ mood: 'wow', fx: 'burst', msg: `l[${v}] = ${low[v]} ≥ d[${u}] = ${disc[u]}: the part below ${v} only reaches the rest through ${u}. ${u} is a <b>cut point</b>.`, layers: pic() });
          }
        }
        if (!cuts.has(u)) ncls[u] = 'done';
        if (parent === -1 && kids > 1) { cuts.add(u); ncls[u] = 'piv'; }
      };
      dfs(0, -1);
      F.push({ mood: 'wow', fx: 'rain', msg: `Bridges: ${bridges.join(', ')}. Cut points: ${[...cuts].sort((a, b) => a - b).join(', ')}. In a road or power network these are the weak spots.`, layers: pic() });
      return F;
    }
  });

  /* ---------- maximum flow ---------- */
  D.flow = el => PK.widget(el, {
    title: 'Maximum flow, Edmonds-Karp', sub: 'Push water along the shortest path that still has room, until no path is left. Labels show flow / capacity.',
    inputs: [{ k: 'last', label: 'Capacity of v4 → t', type: 'num', val: 4, min: 0, max: 20, w: 80 }],
    random: () => ({ last: Math.floor(Math.random() * 21) }),
    check: v => Number.isInteger(v.last) && v.last >= 0 && v.last <= 20 ? '' : 'Pick a whole number from 0 to 20.',
    frames: ({ last }) => {
      const N = ['s', 'v1', 'v2', 'v3', 'v4', 't'], n = 6, F = [];
      const P = [['s', 40, 140], ['v1', 165, 50], ['v2', 165, 230], ['v3', 325, 50], ['v4', 325, 230], ['t', 450, 140]];
      const EE = [[0, 1, 16], [0, 2, 13], [1, 3, 12], [2, 1, 4], [2, 4, 14], [3, 2, 9], [3, 5, 20], [4, 3, 7], [4, 5, last]];
      const cap = [...Array(n)].map(() => new Array(n).fill(0)), flow = [...Array(n)].map(() => new Array(n).fill(0));
      EE.forEach(([u, v, c]) => { cap[u][v] = c; });
      let total = 0;
      const pic = (ncls = {}, ecls = {}) => [gr('Pipes, flow / capacity', P, EE.map(([u, v, c]) => [N[u], N[v], `${flow[u][v]}/${c}`]), { ncls, ecls })];
      F.push({ mood: 'think', msg: 'Every pipe starts empty. Find a path from s to t where every pipe still has room.', vars: { flow: 0 }, layers: pic({ s: 'cur', t: 'cur' }) });
      for (;;) {
        const par = new Array(n).fill(-1);
        par[0] = 0;
        const q = [0];
        for (let i = 0; i < q.length; i++) for (let v = 0; v < n; v++) if (par[v] === -1 && cap[q[i]][v] > 0) { par[v] = q[i]; q.push(v); }
        if (par[5] === -1) break;
        const path = [5];
        let push = Infinity;
        for (let v = 5; v !== 0; v = par[v]) { push = Math.min(push, cap[par[v]][v]); path.push(par[v]); }
        path.reverse();
        const ek = {}, nk = {};
        for (let i = 0; i + 1 < path.length; i++) { const a = path[i], b = path[i + 1]; ek[(EE.some(e => e[0] === a && e[1] === b) ? N[a] + '-' + N[b] : N[b] + '-' + N[a])] = 'look'; nk[N[a]] = 'look'; }
        nk.t = 'look';
        F.push({ mood: 'look', msg: `Shortest path with room: ${path.map(i => N[i]).join(arrow)}. The tightest pipe has room for <b>${push}</b>.`, vars: { flow: total }, layers: pic(nk, ek) });
        let undo = false;
        for (let v = 5; v !== 0; v = par[v]) {
          const u = par[v];
          cap[u][v] -= push;
          cap[v][u] += push;
          if (flow[v][u] > 0) { flow[v][u] -= push; undo = true; } else flow[u][v] += push;
        }
        total += push;
        Object.keys(ek).forEach(k => { ek[k] = 'yes'; });
        F.push({ mood: 'wow', fx: 'burst', msg: `Push ${push}. Total flow is now <b>${total}</b>.${undo ? ' Part of this path ran against a pipe, which takes back flow sent earlier.' : ''}`, vars: { flow: total }, layers: pic({}, ek) });
      }
      const reach = [0];
      for (let i = 0; i < reach.length; i++) for (let v = 0; v < n; v++) if (cap[reach[i]][v] > 0 && !reach.includes(v)) reach.push(v);
      const nc = {}, ec = {}, cutE = [];
      N.forEach((x, i) => { nc[x] = reach.includes(i) ? 'yes' : 'no'; });
      EE.forEach(([u, v, c]) => { if (reach.includes(u) && !reach.includes(v)) { ec[N[u] + '-' + N[v]] = 'no'; cutE.push(`${N[u]}${arrow}${N[v]} (${c})`); } });
      F.push({ mood: 'wow', fx: 'rain', msg: `No path has room left. Maximum flow = <b>${total}</b>. The full pipes ${cutE.join(', ')} separate the green side from the red side, and they add up to ${total} too: maximum flow equals minimum cut.`, vars: { flow: total }, layers: pic(nc, ec) });
      return F;
    }
  });

  /* ---------- A* search ---------- */
  const MAPS = {
    maze: ['S...#....', '.##.#.##.', '..#...#..', '#.###.#.#', '....#....', '.##...##G'],
    open: ['S........', '.........', '.........', '.........', '.........', '........G'],
  };
  D.astar = el => PK.widget(el, {
    title: 'A* against Dijkstra', sub: 'Both find a shortest path. A* adds a guess of the distance left, so it heads for the goal.',
    inputs: [{ k: 'algo', label: 'Search', type: 'seg', val: 'astar', opts: [['astar', '⭐ A*'], ['dijkstra', '🌊 Dijkstra']] },
             { k: 'map', label: 'Map', type: 'seg', val: 'maze', opts: [['maze', '🧱 Walls'], ['open', '🌾 Open field']] }],
    frames: ({ algo, map }) => {
      const GR = MAPS[map], R = GR.length, C = GR[0].length, cells = GR.join(''), F = [];
      const start = cells.indexOf('S'), goal = cells.indexOf('G'), useH = algo === 'astar';
      const h = i => (useH ? Math.abs(Math.floor(i / C) - Math.floor(goal / C)) + Math.abs((i % C) - (goal % C)) : 0);
      const g = new Map([[start, 0]]), par = new Map(), closed = new Set();
      let openL = [start], expanded = 0;
      const pic = (cur, path = new Set()) => {
        const rows = [], cls = {};
        for (let r = 0; r < R; r++) {
          const row = [];
          for (let c = 0; c < C; c++) {
            const i = r * C + c, ch = cells[i];
            let v = ch === '#' ? '' : ch === '.' ? '' : ch;
            if (ch === '#') cls[r + ',' + c] = 'wall';
            else if (path.has(i)) cls[r + ',' + c] = 'yes';
            else if (i === cur) cls[r + ',' + c] = 'look';
            else if (closed.has(i)) cls[r + ',' + c] = 'cur';
            else if (openL.includes(i)) cls[r + ',' + c] = 'sel';
            if (ch === '.' && g.has(i)) v = String(g.get(i) + h(i));
            row.push(v);
          }
          rows.push(row);
        }
        return [{ t: 'grid', label: useH ? 'Each cell shows f = steps so far + guess left' : 'Each cell shows its distance from S', rows, cls, sq: true }];
      };
      F.push({ mood: 'think', msg: useH ? 'A* picks the open cell with the smallest f = g + h. g is the steps taken, h is the Manhattan distance to G, which never overestimates.' : 'Dijkstra picks the open cell closest to S, and spreads out evenly in every direction.', vars: { expanded: 0 }, layers: pic(-1) });
      while (openL.length) {
        let best = openL[0];
        const key = i => [g.get(i) + h(i), h(i), i];
        const less = (a, b) => a[0] !== b[0] ? a[0] < b[0] : a[1] !== b[1] ? a[1] < b[1] : a[2] < b[2];
        for (const i of openL) if (less(key(i), key(best))) best = i;
        openL = openL.filter(i => i !== best);
        closed.add(best);
        expanded++;
        if (best === goal) break;
        const r = Math.floor(best / C), c = best % C;
        for (const [nr, nc] of [[r - 1, c], [r + 1, c], [r, c - 1], [r, c + 1]]) {
          const nb = nr * C + nc;
          if (nr < 0 || nr >= R || nc < 0 || nc >= C || cells[nb] === '#' || closed.has(nb)) continue;
          if (!g.has(nb) || g.get(best) + 1 < g.get(nb)) { if (!g.has(nb)) openL.push(nb); g.set(nb, g.get(best) + 1); par.set(nb, best); }
        }
        F.push({ mood: 'work', msg: `Expand the cell at row ${r + 1}, column ${c + 1}${useH ? ` (f = ${g.get(best) + h(best)})` : ` (distance ${g.get(best)})`}. Its open neighbours join the frontier.`, vars: { expanded, frontier: openL.length }, layers: pic(best) });
      }
      const path = new Set();
      for (let v = goal; v !== start; v = par.get(v)) if (v !== goal) path.add(v);
      F.push({ mood: 'wow', fx: 'rain', msg: `Reached G in <b>${g.get(goal)}</b> steps after expanding <b>${expanded}</b> cells.${useH ? ' Switch to Dijkstra to see how many more cells it opens.' : ' Switch to A* to see how few cells it needs.'}`, vars: { expanded, steps: g.get(goal) }, layers: pic(-1, path) });
      return F;
    }
  });

  /* ---------- Hierholzer ---------- */
  D.euler = el => PK.widget(el, {
    title: 'Euler circuit with Hierholzer', sub: 'Walk unused edges until stuck. A stuck node is finished and goes on the answer, which comes out backwards.',
    inputs: [{ k: 'g', label: 'Graph', type: 'seg', val: 'ok', opts: [['ok', '✅ Balanced'], ['extra', '➕ One extra edge']] }],
    frames: ({ g }) => {
      const n = 5, F = [], ids = ['0', '1', '2', '3', '4'];
      const P = [['0', 70, 200], ['1', 250, 145], ['2', 150, 45], ['3', 410, 50], ['4', 410, 240]];
      const EE = [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4], [4, 1]].concat(g === 'extra' ? [[0, 2]] : []);
      const E = EE.map(([u, v]) => [String(u), String(v)]);
      const indeg = new Array(n).fill(0), outdeg = new Array(n).fill(0), adj = ids.map(() => []);
      EE.forEach(([u, v]) => { adj[u].push(v); outdeg[u]++; indeg[v]++; });
      adj.forEach(a => a.sort((x, y) => x - y));
      const tag = Object.fromEntries(ids.map((x, i) => [x, `in ${indeg[i]} out ${outdeg[i]}`]));
      const bad = ids.filter((_, i) => indeg[i] !== outdeg[i]);
      if (bad.length) {
        F.push({ mood: 'think', msg: 'Every circuit leaves each node as often as it enters. So first compare in degree and out degree.', layers: [gr('Degrees', P, E, { tag, w: 460 })] });
        F.push({ mood: 'sad', fx: 'shake', msg: `Node${bad.length > 1 ? 's' : ''} ${bad.join(' and ')} ${bad.length > 1 ? 'have' : 'has'} in ≠ out. No Euler circuit can exist, so there is nothing to search. Remove the extra edge to fix it.`, layers: [gr('Degrees', P, E, { tag, w: 460, ncls: Object.fromEntries(bad.map(x => [x, 'no'])) })] });
        return F;
      }
      const used = new Array(n).fill(0), ecls = {}, stack = [0], circuit = [];
      const pic = (ncls = {}) => [gr('Directed graph', P, E, { ecls, ncls, w: 460 }),
        { t: 'row', label: 'Stack, the walk so far', cells: stack.slice(), idx: false, cls: { [stack.length - 1]: 'look' } },
        { t: 'row', label: 'Answer, built backwards', cells: circuit.slice(), idx: false }];
      F.push({ mood: 'think', msg: 'Every node has in degree = out degree, so an Euler circuit exists. Start walking from 0.', layers: [gr('Degrees all match', P, E, { tag, w: 460, ncls: Object.fromEntries(ids.map(x => [x, 'yes'])) })] });
      const done = new Set();
      while (stack.length) {
        const u = stack[stack.length - 1];
        if (used[u] < adj[u].length) {
          const v = adj[u][used[u]++];
          const k = u + '-' + v;                 /* this graph has at most one edge per direction */
          done.add(k);
          Object.keys(ecls).forEach(x => { if (ecls[x] === 'look') ecls[x] = 'done'; });
          ecls[k] = 'look';
          stack.push(v);
          F.push({ mood: 'work', msg: `From ${u}, take the unused edge to ${v}.`, vars: { 'edges used': done.size }, layers: pic({ [v]: 'look' }) });
        } else {
          circuit.push(stack.pop());
          F.push({ mood: 'happy', msg: `${u} has no unused edge left. Pop it onto the answer${stack.length ? `, then step back to ${stack[stack.length - 1]} and look for unused edges there` : ''}.`, vars: { 'edges used': done.size }, layers: pic({ [u]: 'yes' }) });
        }
      }
      Object.keys(ecls).forEach(x => { ecls[x] = 'yes'; });
      F.push({ mood: 'wow', fx: 'rain', msg: `Read the answer backwards: <b>${circuit.slice().reverse().join(arrow)}</b>. All ${EE.length} edges, each used exactly once.`, layers: pic() });
      return F;
    }
  });
})();
'''

INFO = {
    'title': 'The right tool for each graph question',
    'panels': [
        {'s': [['e', '➖'], ['t', 'n − 1 rounds', {'b': 1}]], 'h': 'Bellman-Ford', 't': 'Negative edges, cycle check.', 'more': 'O(V E).'},
        {'s': [['e', '🗺️'], ['t', 'k, i, j loops', {'b': 1}]], 'h': 'Floyd-Warshall', 't': 'Every pair at once.', 'more': 'O(V³) time, O(V²) memory.'},
        {'s': [['e', '🚰'], ['t', 'max flow = min cut', {'b': 1}]], 'h': 'Edmonds-Karp', 't': 'Shortest path with room, again and again.', 'more': 'O(V E²).'},
        {'s': [['e', '⭐'], ['t', 'f = g + h', {'b': 1}]], 'h': 'A*', 't': 'Dijkstra aimed at the goal.', 'more': 'h must never overestimate.'},
    ],
    'remember': 'Positive weights and one source: Dijkstra. Negative weights: Bellman-Ford. Every pair on a small graph: Floyd-Warshall. One known goal and a good guess: A*. Components, bridges and Euler paths all come from depth first search.',
}

REAL = [
    ['🎮', 'Game characters finding their way', 'Most games move characters with A* on a grid or a navigation mesh, because it finds the shortest route while looking at far fewer cells than Dijkstra.'],
    ['📡', 'Internet routing', 'Routers that use distance vector routing share their distance tables with neighbours and improve them round after round, the same relaxing step as Bellman-Ford.'],
    ['🚚', 'Deliveries and supply chains', 'How many trucks per hour can move from a warehouse to a city over roads with limits is a maximum flow question, and the minimum cut shows the roads that hold everything back.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to advanced graphs. The Graphs chapter covered searching, Dijkstra and spanning trees. Here you will handle negative edges with Bellman Ford, find every pair of distances with Floyd Warshall, group nodes into strongly connected components, spot bridges and cut points, push water through pipes with maximum flow, aim a search at the goal with A star, and use every edge once with Hierholzer.'},
    {'id': 'bellman-ford', 'h': 'Bellman-Ford', 'en': 'Bellman Ford relaxes every edge, round after round. A shortest path never needs more than n minus one edges, so n minus one rounds are always enough. If any distance still drops in one extra round, there is a negative cycle, and no shortest path exists at all.'},
    {'id': 'floyd-warshall', 'h': 'Floyd-Warshall', 'en': 'Floyd Warshall fills a table with the distance between every pair of nodes. In round k, each pair asks whether stopping at node k on the way is shorter than its current best. After n rounds, every cell holds the true shortest distance. It costs n cubed steps, which is fine for a few hundred nodes.'},
    {'id': 'scc', 'h': 'Strongly connected components', 'en': 'A strongly connected component is a group of nodes that can all reach each other. Kosaraju runs one depth first search to record the finish order, reverses every edge, and runs a second search starting from the latest finisher. Each search in the second pass colours exactly one component.'},
    {'id': 'bridges', 'h': 'Bridges', 'en': 'A bridge is an edge that splits the graph when removed, and a cut point is a node that does the same. During one depth first search, each node keeps its discovery time and a low value, the earliest time its subtree can reach with a back edge. If a child cannot reach above its parent, the edge between them is a bridge.'},
    {'id': 'max-flow', 'h': 'Maximum flow', 'en': 'To find the maximum flow, keep finding the shortest path from source to sink where every pipe still has room, and push as much as the tightest pipe allows. Each push also opens a reverse pipe, so later paths can undo bad choices. When no path is left, the full pipes form a minimum cut with the same total.'},
    {'id': 'a-star', 'h': 'A star', 'en': 'A star is Dijkstra with a sense of direction. It adds a guess of the distance left to the distance already travelled, and always expands the cell with the smallest total. As long as the guess never overestimates, the path it finds is still the shortest, and it usually looks at far fewer cells.'},
    {'id': 'euler', 'h': 'Euler circuits', 'en': 'An Euler circuit uses every edge exactly once. In a directed graph, every node must enter as often as it leaves. Hierholzer walks along unused edges until it gets stuck, writes down the stuck node, steps back, and continues. The answer is written backwards, so reverse it at the end.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from network delay time to fixing arrows in a grid. Each one is solved in Python, JavaScript, Java and TypeScript, and you can replay every solution line by line.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. For each problem, first decide what a node is, what an edge is, and how the cost of a path is measured: a sum, a product, or a maximum. That choice tells you which algorithm fits. Open the hint if you are stuck.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'Why can Dijkstra give a wrong answer when a graph has a negative edge?', 'o': ['It runs forever', 'It settles a node for good, but a later negative edge could still make it cheaper', 'It cannot read negative numbers', 'It always works'], 'a': 1, 'hint': 'What does Dijkstra assume about a popped node?', 'why': 'Dijkstra never revisits a popped node, which is only safe when no edge can lower a distance later.'},
    {'lv': 'e', 'q': 'How many rounds does Bellman-Ford need on a graph with 7 nodes?', 'o': ['7', '6', '49', '1'], 'a': 1, 'hint': 'n − 1.', 'why': 'A shortest path uses at most 6 edges, so 6 rounds of relaxing every edge are enough.'},
    {'lv': 'e', 'q': 'What does Floyd-Warshall compute?', 'o': ['One shortest path', 'The shortest distance between every pair of nodes', 'A spanning tree', 'The maximum flow'], 'a': 1, 'hint': 'It fills an n × n table.', 'why': 'After n rounds, cell (i, j) holds the shortest distance from i to j.'},
    {'lv': 'e', 'q': 'With h = 0 for every node, A* behaves like which algorithm?', 'o': ['BFS', 'Dijkstra', 'DFS', 'Bellman-Ford'], 'a': 1, 'hint': 'f = g + 0.', 'why': 'It then always expands the node with the smallest distance so far, exactly like Dijkstra.'},
    {'lv': 'm', 'q': 'Bellman-Ford still improves a distance in an extra round after n − 1 rounds. What does that mean?', 'o': ['The graph is disconnected', 'There is a negative cycle reachable from the source', 'It needs one more round', 'All edges are positive'], 'a': 1, 'hint': 'Shortest paths never need more than n − 1 edges.', 'why': 'Only a cycle with a negative total can keep making paths cheaper forever.'},
    {'lv': 'm', 'q': 'What is the time cost of Floyd-Warshall on n nodes?', 'o': ['O(n)', 'O(n²)', 'O(n³)', 'O(2ⁿ)'], 'a': 2, 'hint': 'Three nested loops over n.', 'why': 'k, i and j each run n times.'},
    {'lv': 'm', 'q': 'In Kosaraju\'s second pass, which node starts each search?', 'o': ['Node 0', 'The latest finisher from pass 1 not yet coloured', 'A random node', 'The node with most edges'], 'a': 1, 'hint': 'Reverse the finish order.', 'why': 'The latest finisher lies in a component with no way out on the reversed graph, so the search stays inside it.'},
    {'lv': 'm', 'q': 'A directed graph has an Euler circuit. What must be true at every node?', 'o': ['In degree is 0', 'In degree equals out degree', 'Out degree is 1', 'In degree is even'], 'a': 1, 'hint': 'A circuit leaves each node as often as it enters.', 'why': 'Each visit uses one edge in and one edge out, and all edges must also be in one connected piece.'},
    {'lv': 'h', 'q': 'In the bridges lesson, why is the edge 1-3 a bridge?', 'o': ['It has the biggest weight', 'l[3] = 3 is bigger than d[1] = 1, so nothing below 3 reaches back above 1', '3 has no children', 'It is the last edge visited'], 'a': 1, 'hint': 'Compare the child\'s low value with the parent\'s discovery time.', 'why': 'The subtree under 3 can only climb back to time 3, so removing the edge 1-3 cuts it off.'},
    {'lv': 'h', 'q': 'When pushing flow, why does Edmonds-Karp add capacity to the reverse pipe?', 'o': ['To double the flow', 'So a later path can cancel flow that was sent the wrong way', 'Pipes are always two way', 'To find the cut faster'], 'a': 1, 'hint': 'An early choice might block a better plan.', 'why': 'The reverse capacity lets a later augmenting path take back flow, which is needed to reach the true maximum.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'INF = 10**9\nd = [[0, 4, INF], [INF, 0, 1], [2, INF, 0]]\nfor k in range(3):\n    for i in range(3):\n        for j in range(3):\n            d[i][j] = min(d[i][j], d[i][k] + d[k][j])\nprint(d[0][2], d[2][1])', 'o': ['5 6', '5 4', 'INF 6', '1 2'], 'a': 0, 'hint': '0 → 1 → 2 and 2 → 0 → 1.', 'why': '0 to 2 costs 4 + 1 = 5. 2 to 1 costs 2 + 4 = 6.'},
    {'lv': 'h', 'q': 'Which heuristic is safe for A* on a grid where you move only up, down, left and right with cost 1?', 'o': ['Twice the Manhattan distance', 'The Manhattan distance', 'The number of walls', 'Always 100'], 'a': 1, 'hint': 'It must never overestimate.', 'why': 'You need at least |Δrow| + |Δcol| moves to reach the goal, so the Manhattan distance never overestimates.'},
    {'lv': 'x', 'q': 'In the flow lesson, which pipes form the minimum cut?', 'o': ['s → v1 and s → v2', 'v1 → v3, v4 → v3 and v4 → t', 'v3 → t only', 'v2 → v4 and v3 → t'], 'a': 1, 'hint': 'Look for full pipes from the reachable side to the rest.', 'why': 'The source side is s, v1, v2, v4. The pipes leaving it are 12 + 7 + 4 = 23, equal to the maximum flow.'},
    {'lv': 'x', 'q': 'Every edge costs 0 or 1. Which method finds shortest paths in O(V + E)?', 'o': ['Floyd-Warshall', '0-1 BFS with a double ended queue', 'Bellman-Ford', 'Plain DFS'], 'a': 1, 'hint': 'Free moves go to the front of the queue.', 'why': 'Pushing 0 cost moves to the front and 1 cost moves to the back keeps the queue sorted by cost without a heap.'},
    {'lv': 'x', 'q': 'Why does Dijkstra still work in Path With Minimum Effort, where a path costs its biggest step?', 'o': ['Because all heights are positive', 'Because max(effort, step) never decreases along a path', 'Because the grid is small', 'It does not work'], 'a': 1, 'hint': 'Dijkstra needs costs that never go down as a path gets longer.', 'why': 'Extending a path can only keep or raise its maximum, so a popped cell can never improve later.'},
    {'lv': 'x', 'q': 'In the A* lesson maze, Dijkstra expands 34 cells and A* expands 14. Both paths have length 13. Why is A* allowed to skip cells?', 'o': ['It uses a smaller grid', 'Cells with g + h above 13 can never be on a shortest path, so A* never needs them', 'It moves diagonally', 'It guesses and may be wrong'], 'a': 1, 'hint': 'h never overestimates.', 'why': 'If g + h already exceeds the best path length, the real cost through that cell is even bigger.'},
]

CALC = [
    {'lv': 'e', 'q': 'At most how many rounds does Bellman-Ford need for 6 nodes?', 'ans': '5', 'hint': 'n − 1.', 'steps': ['<span class="eq">6 − 1 = 5</span>']},
    {'lv': 'e', 'q': 'Floyd-Warshall on 10 nodes makes how many checks of d[i][k] + d[k][j]?', 'ans': '1000', 'hint': 'n³.', 'steps': ['<span class="eq">10 × 10 × 10 = 1000</span>']},
    {'lv': 'm', 'q': 'Edges s → a costs 4, a → b costs −2, s → b costs 3. What is the shortest distance from s to b?', 'ans': '2', 'hint': 'Compare the direct edge with the detour.', 'steps': ['Direct: 3.', 'Detour: <span class="eq">4 + (−2) = 2</span>, which is smaller.']},
    {'lv': 'm', 'q': 'In the Bellman-Ford lesson, what is the final distance to z?', 'ans': '-2', 'hint': 'Run the lesson program or the animation.', 'steps': ['s → y → x → t → z: <span class="eq">7 − 3 − 2 − 4 = −2</span>']},
    {'lv': 'h', 'q': 'Pipes s → a (5), a → t (3), s → b (4), b → t (6). What is the maximum flow?', 'ans': '7', 'hint': 'Each route is limited by its tightest pipe.', 'steps': ['Through a: <span class="eq">min(5, 3) = 3</span>', 'Through b: <span class="eq">min(4, 6) = 4</span>', '<span class="eq">3 + 4 = 7</span>']},
    {'lv': 'h', 'q': 'What is the Manhattan distance from cell (0, 0) to cell (5, 8)?', 'ans': '13', 'hint': '|Δrow| + |Δcol|.', 'steps': ['<span class="eq">5 + 8 = 13</span>', 'That matches the 13 step path in the A* lesson.']},
    {'lv': 'x', 'q': 'Floyd-Warshall on 1000 nodes stores a matrix of 4 byte integers. How many megabytes is that, using 1 MB = 1,000,000 bytes?', 'ans': '4', 'hint': 'n² cells of 4 bytes.', 'steps': ['<span class="eq">1000 × 1000 × 4 = 4,000,000 bytes</span>', '<span class="eq">= 4 MB</span>']},
    {'lv': 'x', 'q': 'How many augmenting paths does the max flow lesson program find?', 'ans': '3', 'hint': 'Count the lines that start with "path".', 'steps': ['12 along s → v1 → v3 → t, 4 along s → v2 → v4 → t, 7 along s → v2 → v4 → v3 → t.', '<span class="eq">12 + 4 + 7 = 23</span> in 3 paths.']},
]

TALK = {
    'bellman-ford': 'Dijkstra is fast because it makes a promise: once a node is taken off the heap, its distance is final. That promise holds only when every edge is positive. Now add a road with a negative cost. Suddenly a longer route can be cheaper than a shorter one, and Dijkstra may already have locked in the wrong answer. Bellman Ford makes no such promise. It simply goes through the whole list of edges and asks, for each one, can this edge make the far end cheaper? It repeats that whole pass again and again. A shortest path can never use more than n minus one edges, so after n minus one rounds every distance must be correct. Then it does one more round as a test. If anything still improves, the graph contains a negative cycle, a loop you could drive round forever, getting cheaper every lap.',
    'floyd-warshall': 'Sometimes you do not want the distances from one place, but from every place to every other place, like the mileage table printed in a road atlas. Floyd Warshall builds that whole table with three nested loops and almost no other code. Start with the direct roads, and infinity wherever there is no road. Then pick node zero and allow it to be a stop in the middle of any trip. For every pair of nodes, check whether going through node zero is shorter than the current best. Then allow node one as a stop as well, and check every pair again. Keep going until every node has had its turn. At the end, each cell of the table holds the true shortest distance. The cost is n cubed steps, so it is perfect for a few hundred nodes, and far too slow for millions.',
    'scc': 'In a one way street network, two places are strongly connected if you can drive from each one to the other. A strongly connected component is a largest group of places where that is true for every pair. Kosaraju finds all of them with two depth first searches. In the first search, write each node down at the moment it finishes, after all its exits have been explored. Then reverse every street. In the second search, start from the node that finished last. Because the streets are reversed, the search cannot escape its own component, so everything it reaches forms exactly one group. Pick the next unvisited node from the finish list and repeat. The neat result is that if you shrink every component down to a single dot, the remaining graph has no cycles, which makes it easy to order and reason about.',
    'bridges': 'Imagine a network of roads, and you want to know which single road, if it were closed, would cut some towns off completely. That road is called a bridge. A town whose closure does the same is called a cut point. Both can be found in one depth first search. Each node gets a discovery time, the moment the search first arrives, and a low value. The low value is the earliest discovery time that the node, or anything below it in the search tree, can reach by jumping along one back edge. After the search returns from a child, compare the child\'s low value with the parent\'s discovery time. If the child cannot reach anything as early as the parent, then the edge between them is the only connection, so it is a bridge. A similar test, with greater than or equal, finds the cut points.',
    'max-flow': 'Picture a network of water pipes from a source to a sink, each pipe with a limit on how much water per second it can carry. How much water can arrive at the sink? Edmonds Karp answers this by repeating one simple step. Use breadth first search to find the shortest path from source to sink where every pipe still has some room. The tightest pipe on that path decides how much you can push. Push that amount, and reduce the room on each pipe. Here is the clever part: every push also creates room in the opposite direction, so a later path is allowed to take back water that was sent somewhere unhelpful. When no path with room remains, you are done. The nodes the source can still reach form one side of a cut, and the full pipes crossing that cut add up to exactly the maximum flow.',
    'a-star': 'Dijkstra explores evenly in every direction around the start. It finds the shortest path, but it wastes effort exploring places behind it. A star gives the search a sense of direction. For every cell it adds two numbers. g is how far you have already travelled from the start. h is a guess of how far is left to the goal. It always expands the cell with the smallest total, g plus h. On a grid where you move up, down, left or right, the Manhattan distance is a great guess: the row difference plus the column difference. The guess must never be bigger than the real distance, or A star might miss the best path. Run the animation with walls and with an open field, and compare how many cells A star and Dijkstra each need to reach the goal.',
    'euler': 'In 1736 the people of Königsberg wondered whether they could walk across each of their seven bridges exactly once. Leonhard Euler proved they could not, and started graph theory along the way. A walk that uses every edge exactly once and ends where it started is called an Euler circuit. In a directed graph, it exists when every node is entered as often as it is left, and all edges belong to one connected piece. Hierholzer\'s algorithm builds one in linear time. Walk along any unused edge, and keep going until you get stuck. A stuck node has no unused edges left, so it is finished and goes onto the answer. Step back to the previous node and continue from there if it still has unused edges. The answer list is built backwards, so reverse it at the end.',
    'leetcode': 'The LeetCode problems in this chapter train you to see which algorithm a problem really needs. You start with network delay time, a classic single source shortest path, and with choosing a city using the all pairs table from Floyd Warshall. The medium problems twist Dijkstra so that probabilities are multiplied instead of distances added, and use Floyd Warshall with true and false to answer which course must come before which. The hard problems measure a path by its single steepest step, and rebuild a flight itinerary that uses every ticket once, which is an Euler path. The expert problems ask how long until the water is high enough to swim across a grid, and how cheaply you can fix the arrows in a grid, solved with a double ended queue. Each one is written in all four languages.',
}

T = t.finish({
    'slug': 'advanced-graphs', 'title': 'Advanced Graphs', 'short': 'Advanced graphs', 'emoji': '🧭', 'topic': 'advanced-graphs', 'prefix': 'dsaadvg',
    'module': ('🌳', 'Trees and graphs'),
    'lead': 'Graphs with negative edges, every pair of distances, one way groups, weak spots, pipes full of water, a search with a sense of direction and a walk over every edge. Each idea comes with a playful animation you can step through.',
    'desc': 'Advanced graph algorithms in DSA: Bellman-Ford, Floyd-Warshall, strongly connected components, bridges and articulation points, maximum flow and minimum cut, A* search and Euler circuits with Hierholzer, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 26,
    'summary': 'Bellman-Ford and negative cycles, Floyd-Warshall for every pair, Kosaraju strongly connected components, bridges and cut points, Edmonds-Karp maximum flow and minimum cut, A* search and Euler circuits with Hierholzer. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['advanced graphs', 'Bellman-Ford', 'negative cycle', 'Floyd-Warshall', 'all pairs shortest path', 'strongly connected components', 'Kosaraju', 'bridges', 'articulation points', 'Tarjan', 'maximum flow', 'minimum cut', 'Edmonds-Karp', 'A* search', 'heuristic', 'Euler circuit', 'Hierholzer', '0-1 BFS'],
    'added': '2026-11-23',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS, 'css': '',
    'prev': ('graphs', 'graphs', '🕸️ Graphs'),
    'next': None,
})
