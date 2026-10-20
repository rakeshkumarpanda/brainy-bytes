# Graphs: representations, breadth first and depth first search, topological
# order, Dijkstra, minimum spanning trees with union find, and grids.

CODES = {}


def C(key, py, js, java):
    CODES[key] = {'py': py, 'js': js, 'java': java}


# ---------------------------------------------------------------- lesson programs
C('graph_repr', py=r'''
n = 5
edges = [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4)]

adj = [[] for _ in range(n)]          # adjacency list: one list of neighbours per vertex
matrix = [[0] * n for _ in range(n)]  # adjacency matrix: n by n grid of 0 and 1
for a, b in edges:
    adj[a].append(b)
    adj[b].append(a)                  # undirected, so store both directions
    matrix[a][b] = matrix[b][a] = 1

print("adjacency list")
for v in range(n):
    print(" ", v, ":", " ".join(str(w) for w in adj[v]))
print("adjacency matrix")
for row in matrix:
    print(" ", " ".join(str(x) for x in row))
print("degree of 2:", len(adj[2]))
print("is 1 next to 3?", "yes" if matrix[1][3] else "no")
''', js=r'''
const n = 5;
const edges = [[0, 1], [0, 2], [1, 2], [2, 3], [3, 4]];

const adj = Array.from({ length: n }, () => []);                    // adjacency list: one list of neighbours per vertex
const matrix = Array.from({ length: n }, () => new Array(n).fill(0));  // adjacency matrix: n by n grid of 0 and 1
for (const [a, b] of edges) {
  adj[a].push(b);
  adj[b].push(a);                     // undirected, so store both directions
  matrix[a][b] = matrix[b][a] = 1;
}

console.log("adjacency list");
for (let v = 0; v < n; v++) console.log(" ", v, ":", adj[v].join(" "));
console.log("adjacency matrix");
for (const row of matrix) console.log(" ", row.join(" "));
console.log("degree of 2:", adj[2].length);
console.log("is 1 next to 3?", matrix[1][3] ? "yes" : "no");
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class GraphRepr {
    static String join(List<Integer> xs) {
        StringBuilder sb = new StringBuilder();
        for (int x : xs) {
            if (sb.length() > 0) sb.append(" ");
            sb.append(x);
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        int n = 5;
        int[][] edges = {{0, 1}, {0, 2}, {1, 2}, {2, 3}, {3, 4}};

        List<List<Integer>> adj = new ArrayList<>();   // adjacency list: one list of neighbours per vertex
        for (int v = 0; v < n; v++) adj.add(new ArrayList<>());
        int[][] matrix = new int[n][n];                // adjacency matrix: n by n grid of 0 and 1
        for (int[] e : edges) {
            adj.get(e[0]).add(e[1]);
            adj.get(e[1]).add(e[0]);                   // undirected, so store both directions
            matrix[e[0]][e[1]] = matrix[e[1]][e[0]] = 1;
        }

        System.out.println("adjacency list");
        for (int v = 0; v < n; v++) System.out.println("  " + v + " : " + join(adj.get(v)));
        System.out.println("adjacency matrix");
        for (int[] row : matrix) {
            StringBuilder sb = new StringBuilder();
            for (int x : row) sb.append(sb.length() > 0 ? " " : "").append(x);
            System.out.println("  " + sb);
        }
        System.out.println("degree of 2: " + adj.get(2).size());
        System.out.println("is 1 next to 3? " + (matrix[1][3] == 1 ? "yes" : "no"));
    }
}
''')

C('bfs', py=r'''
from collections import deque

n = 7
edges = [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 5), (5, 6)]
adj = [[] for _ in range(n)]
for a, b in edges:
    adj[a].append(b)
    adj[b].append(a)

dist = [-1] * n                       # -1 means not discovered yet
parent = [-1] * n
dist[0] = 0
queue = deque([0])
order = []
while queue:
    v = queue.popleft()
    order.append(v)
    for w in adj[v]:
        if dist[w] == -1:             # first time we see w is along a shortest path
            dist[w] = dist[v] + 1
            parent[w] = v
            queue.append(w)

print("order", " ".join(str(v) for v in order))
print("dist ", " ".join(str(d) for d in dist))
path, v = [], 6
while v != -1:
    path.append(v)
    v = parent[v]                     # walk back from the target to the start
print("path to 6:", " ".join(str(v) for v in reversed(path)))
''', js=r'''
const n = 7;
const edges = [[0, 1], [0, 2], [1, 3], [2, 4], [3, 5], [4, 5], [5, 6]];
const adj = Array.from({ length: n }, () => []);
for (const [a, b] of edges) {
  adj[a].push(b);
  adj[b].push(a);
}

const dist = new Array(n).fill(-1);   // -1 means not discovered yet
const parent = new Array(n).fill(-1);
dist[0] = 0;
const queue = [0];
let head = 0;
const order = [];
while (head < queue.length) {
  const v = queue[head++];
  order.push(v);
  for (const w of adj[v]) {
    if (dist[w] === -1) {             // first time we see w is along a shortest path
      dist[w] = dist[v] + 1;
      parent[w] = v;
      queue.push(w);
    }
  }
}

console.log("order", order.join(" "));
console.log("dist ", dist.join(" "));
const path = [];
for (let v = 6; v !== -1; v = parent[v]) path.push(v);   // walk back from the target to the start
console.log("path to 6:", path.reverse().join(" "));
''', java=r'''
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Bfs {
    public static void main(String[] args) {
        int n = 7;
        int[][] edges = {{0, 1}, {0, 2}, {1, 3}, {2, 4}, {3, 5}, {4, 5}, {5, 6}};
        List<List<Integer>> adj = new ArrayList<>();
        for (int v = 0; v < n; v++) adj.add(new ArrayList<>());
        for (int[] e : edges) {
            adj.get(e[0]).add(e[1]);
            adj.get(e[1]).add(e[0]);
        }

        int[] dist = new int[n];
        int[] parent = new int[n];
        Arrays.fill(dist, -1);              // -1 means not discovered yet
        Arrays.fill(parent, -1);
        dist[0] = 0;
        ArrayDeque<Integer> queue = new ArrayDeque<>();
        queue.add(0);
        StringBuilder order = new StringBuilder();
        while (!queue.isEmpty()) {
            int v = queue.poll();
            order.append(order.length() > 0 ? " " : "").append(v);
            for (int w : adj.get(v)) {
                if (dist[w] == -1) {        // first time we see w is along a shortest path
                    dist[w] = dist[v] + 1;
                    parent[w] = v;
                    queue.add(w);
                }
            }
        }

        System.out.println("order " + order);
        StringBuilder ds = new StringBuilder();
        for (int d : dist) ds.append(ds.length() > 0 ? " " : "").append(d);
        System.out.println("dist  " + ds);
        List<Integer> path = new ArrayList<>();
        for (int v = 6; v != -1; v = parent[v]) path.add(0, v);   // walk back from the target to the start
        StringBuilder ps = new StringBuilder();
        for (int v : path) ps.append(ps.length() > 0 ? " " : "").append(v);
        System.out.println("path to 6: " + ps);
    }
}
''')

C('dfs_components', py=r'''
n = 8
edges = [(0, 1), (1, 2), (3, 4), (5, 6), (6, 7), (5, 7)]
adj = [[] for _ in range(n)]
for a, b in edges:
    adj[a].append(b)
    adj[b].append(a)

seen = [False] * n


def dfs(v, comp):
    seen[v] = True
    comp.append(v)
    for w in adj[v]:
        if not seen[w]:
            dfs(w, comp)              # go as deep as possible before backing up


count = 0
for v in range(n):
    if not seen[v]:                   # an unseen vertex starts a new component
        count += 1
        comp = []
        dfs(v, comp)
        print("component", count, ":", " ".join(str(x) for x in comp))
print("components:", count)
''', js=r'''
const n = 8;
const edges = [[0, 1], [1, 2], [3, 4], [5, 6], [6, 7], [5, 7]];
const adj = Array.from({ length: n }, () => []);
for (const [a, b] of edges) {
  adj[a].push(b);
  adj[b].push(a);
}

const seen = new Array(n).fill(false);

function dfs(v, comp) {
  seen[v] = true;
  comp.push(v);
  for (const w of adj[v]) {
    if (!seen[w]) dfs(w, comp);       // go as deep as possible before backing up
  }
}

let count = 0;
for (let v = 0; v < n; v++) {
  if (!seen[v]) {                     // an unseen vertex starts a new component
    count++;
    const comp = [];
    dfs(v, comp);
    console.log("component", count, ":", comp.join(" "));
  }
}
console.log("components:", count);
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class DfsComponents {
    static List<List<Integer>> adj = new ArrayList<>();
    static boolean[] seen;

    static void dfs(int v, List<Integer> comp) {
        seen[v] = true;
        comp.add(v);
        for (int w : adj.get(v)) {
            if (!seen[w]) dfs(w, comp);     // go as deep as possible before backing up
        }
    }

    public static void main(String[] args) {
        int n = 8;
        int[][] edges = {{0, 1}, {1, 2}, {3, 4}, {5, 6}, {6, 7}, {5, 7}};
        for (int v = 0; v < n; v++) adj.add(new ArrayList<>());
        for (int[] e : edges) {
            adj.get(e[0]).add(e[1]);
            adj.get(e[1]).add(e[0]);
        }
        seen = new boolean[n];

        int count = 0;
        for (int v = 0; v < n; v++) {
            if (!seen[v]) {                 // an unseen vertex starts a new component
                count++;
                List<Integer> comp = new ArrayList<>();
                dfs(v, comp);
                StringBuilder sb = new StringBuilder();
                for (int x : comp) sb.append(sb.length() > 0 ? " " : "").append(x);
                System.out.println("component " + count + " : " + sb);
            }
        }
        System.out.println("components: " + count);
    }
}
''')

C('topo_sort', py=r'''
from collections import deque

names = ["underwear", "pants", "shirt", "belt", "tie", "jacket", "socks", "shoes"]
before = [(0, 1), (1, 7), (1, 3), (2, 3), (2, 4), (4, 5), (3, 5), (6, 7)]   # a must come before b

n = len(names)
adj = [[] for _ in range(n)]
indeg = [0] * n                       # how many things must happen first
for a, b in before:
    adj[a].append(b)
    indeg[b] += 1

queue = deque(v for v in range(n) if indeg[v] == 0)
order = []
while queue:
    v = queue.popleft()
    order.append(names[v])
    for w in adj[v]:
        indeg[w] -= 1                 # one requirement of w is now done
        if indeg[w] == 0:
            queue.append(w)

print("order:", " ".join(order))
print("no cycle" if len(order) == n else "cycle found")
''', js=r'''
const names = ["underwear", "pants", "shirt", "belt", "tie", "jacket", "socks", "shoes"];
const before = [[0, 1], [1, 7], [1, 3], [2, 3], [2, 4], [4, 5], [3, 5], [6, 7]];   // a must come before b

const n = names.length;
const adj = Array.from({ length: n }, () => []);
const indeg = new Array(n).fill(0);   // how many things must happen first
for (const [a, b] of before) {
  adj[a].push(b);
  indeg[b]++;
}

const queue = [];
for (let v = 0; v < n; v++) if (indeg[v] === 0) queue.push(v);
let head = 0;
const order = [];
while (head < queue.length) {
  const v = queue[head++];
  order.push(names[v]);
  for (const w of adj[v]) {
    indeg[w]--;                       // one requirement of w is now done
    if (indeg[w] === 0) queue.push(w);
  }
}

console.log("order:", order.join(" "));
console.log(order.length === n ? "no cycle" : "cycle found");
''', java=r'''
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;

public class TopoSort {
    public static void main(String[] args) {
        String[] names = {"underwear", "pants", "shirt", "belt", "tie", "jacket", "socks", "shoes"};
        int[][] before = {{0, 1}, {1, 7}, {1, 3}, {2, 3}, {2, 4}, {4, 5}, {3, 5}, {6, 7}};   // a must come before b

        int n = names.length;
        List<List<Integer>> adj = new ArrayList<>();
        for (int v = 0; v < n; v++) adj.add(new ArrayList<>());
        int[] indeg = new int[n];           // how many things must happen first
        for (int[] e : before) {
            adj.get(e[0]).add(e[1]);
            indeg[e[1]]++;
        }

        ArrayDeque<Integer> queue = new ArrayDeque<>();
        for (int v = 0; v < n; v++) if (indeg[v] == 0) queue.add(v);
        List<String> order = new ArrayList<>();
        while (!queue.isEmpty()) {
            int v = queue.poll();
            order.add(names[v]);
            for (int w : adj.get(v)) {
                indeg[w]--;                 // one requirement of w is now done
                if (indeg[w] == 0) queue.add(w);
            }
        }

        System.out.println("order: " + String.join(" ", order));
        System.out.println(order.size() == n ? "no cycle" : "cycle found");
    }
}
''')

C('dijkstra', py=r'''
import heapq

names = "ABCDEF"
roads = [(0, 1, 4), (0, 2, 2), (1, 2, 1), (1, 3, 5), (2, 3, 8), (2, 4, 10), (3, 4, 2), (3, 5, 6), (4, 5, 2)]
n = len(names)
adj = [[] for _ in range(n)]
for a, b, w in roads:
    adj[a].append((b, w))
    adj[b].append((a, w))

INF = 10 ** 9
dist = [INF] * n
prev = [-1] * n
dist[0] = 0
heap = [(0, 0)]                       # (distance so far, vertex)
while heap:
    d, v = heapq.heappop(heap)
    if d > dist[v]:
        continue                      # an old, longer entry: skip it
    for w, cost in adj[v]:
        if d + cost < dist[w]:        # a shorter way to w through v
            dist[w] = d + cost
            prev[w] = v
            heapq.heappush(heap, (dist[w], w))

for v in range(n):
    path, u = [], v
    while u != -1:
        path.append(names[u])
        u = prev[u]
    print(names[v], dist[v], "via", " ".join(reversed(path)))
''', js=r'''
const names = "ABCDEF";
const roads = [[0, 1, 4], [0, 2, 2], [1, 2, 1], [1, 3, 5], [2, 3, 8], [2, 4, 10], [3, 4, 2], [3, 5, 6], [4, 5, 2]];
const n = names.length;
const adj = Array.from({ length: n }, () => []);
for (const [a, b, w] of roads) {
  adj[a].push([b, w]);
  adj[b].push([a, w]);
}

// a small binary heap of [distance, vertex] pairs
const heap = [];
const less = (x, y) => x[0] < y[0] || (x[0] === y[0] && x[1] < y[1]);
function push(item) {
  heap.push(item);
  let i = heap.length - 1;
  while (i > 0 && less(heap[i], heap[(i - 1) >> 1])) {
    [heap[i], heap[(i - 1) >> 1]] = [heap[(i - 1) >> 1], heap[i]];
    i = (i - 1) >> 1;
  }
}
function pop() {
  const top = heap[0], last = heap.pop();
  if (heap.length > 0) {
    heap[0] = last;
    let i = 0;
    while (true) {
      let s = i;
      for (const c of [2 * i + 1, 2 * i + 2]) if (c < heap.length && less(heap[c], heap[s])) s = c;
      if (s === i) break;
      [heap[i], heap[s]] = [heap[s], heap[i]];
      i = s;
    }
  }
  return top;
}

const dist = new Array(n).fill(Infinity);
const prev = new Array(n).fill(-1);
dist[0] = 0;
push([0, 0]);                         // [distance so far, vertex]
while (heap.length > 0) {
  const [d, v] = pop();
  if (d > dist[v]) continue;          // an old, longer entry: skip it
  for (const [w, cost] of adj[v]) {
    if (d + cost < dist[w]) {         // a shorter way to w through v
      dist[w] = d + cost;
      prev[w] = v;
      push([dist[w], w]);
    }
  }
}

for (let v = 0; v < n; v++) {
  const path = [];
  for (let u = v; u !== -1; u = prev[u]) path.push(names[u]);
  console.log(names[v], dist[v], "via", path.reverse().join(" "));
}
''', java=r'''
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;

public class Dijkstra {
    public static void main(String[] args) {
        String names = "ABCDEF";
        int[][] roads = {{0, 1, 4}, {0, 2, 2}, {1, 2, 1}, {1, 3, 5}, {2, 3, 8}, {2, 4, 10}, {3, 4, 2}, {3, 5, 6}, {4, 5, 2}};
        int n = names.length();
        List<List<int[]>> adj = new ArrayList<>();
        for (int v = 0; v < n; v++) adj.add(new ArrayList<>());
        for (int[] r : roads) {
            adj.get(r[0]).add(new int[]{r[1], r[2]});
            adj.get(r[1]).add(new int[]{r[0], r[2]});
        }

        int[] dist = new int[n];
        int[] prev = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        Arrays.fill(prev, -1);
        dist[0] = 0;
        PriorityQueue<int[]> heap = new PriorityQueue<>((x, y) -> x[0] != y[0] ? x[0] - y[0] : x[1] - y[1]);
        heap.add(new int[]{0, 0});          // {distance so far, vertex}
        while (!heap.isEmpty()) {
            int[] top = heap.poll();
            int d = top[0], v = top[1];
            if (d > dist[v]) continue;      // an old, longer entry: skip it
            for (int[] e : adj.get(v)) {
                int w = e[0], cost = e[1];
                if (d + cost < dist[w]) {   // a shorter way to w through v
                    dist[w] = d + cost;
                    prev[w] = v;
                    heap.add(new int[]{dist[w], w});
                }
            }
        }

        for (int v = 0; v < n; v++) {
            List<String> path = new ArrayList<>();
            for (int u = v; u != -1; u = prev[u]) path.add(0, String.valueOf(names.charAt(u)));
            System.out.println(names.charAt(v) + " " + dist[v] + " via " + String.join(" ", path));
        }
    }
}
''')

C('kruskal', py=r'''
names = "ABCDEF"
roads = [(0, 1, 4), (0, 2, 2), (1, 2, 1), (1, 3, 5), (2, 3, 8), (2, 4, 10), (3, 4, 2), (3, 5, 6), (4, 5, 2)]
parent = list(range(len(names)))      # every vertex starts as its own group


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]   # path halving keeps the trees flat
        x = parent[x]
    return x


total = 0
for a, b, w in sorted(roads, key=lambda r: r[2]):   # cheapest roads first
    ra, rb = find(a), find(b)
    if ra == rb:
        print("skip", names[a] + names[b], w, "(would make a cycle)")
        continue
    parent[ra] = rb                   # union: join the two groups
    total += w
    print("take", names[a] + names[b], w)
print("total", total)
''', js=r'''
const names = "ABCDEF";
const roads = [[0, 1, 4], [0, 2, 2], [1, 2, 1], [1, 3, 5], [2, 3, 8], [2, 4, 10], [3, 4, 2], [3, 5, 6], [4, 5, 2]];
const parent = [...names].map((_, i) => i);   // every vertex starts as its own group

function find(x) {
  while (parent[x] !== x) {
    parent[x] = parent[parent[x]];    // path halving keeps the trees flat
    x = parent[x];
  }
  return x;
}

let total = 0;
for (const [a, b, w] of roads.slice().sort((x, y) => x[2] - y[2])) {   // cheapest roads first
  const ra = find(a), rb = find(b);
  if (ra === rb) {
    console.log("skip", names[a] + names[b], w, "(would make a cycle)");
    continue;
  }
  parent[ra] = rb;                    // union: join the two groups
  total += w;
  console.log("take", names[a] + names[b], w);
}
console.log("total", total);
''', java=r'''
import java.util.Arrays;

public class Kruskal {
    static int[] parent;

    static int find(int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];  // path halving keeps the trees flat
            x = parent[x];
        }
        return x;
    }

    public static void main(String[] args) {
        String names = "ABCDEF";
        int[][] roads = {{0, 1, 4}, {0, 2, 2}, {1, 2, 1}, {1, 3, 5}, {2, 3, 8}, {2, 4, 10}, {3, 4, 2}, {3, 5, 6}, {4, 5, 2}};
        parent = new int[names.length()];
        for (int i = 0; i < parent.length; i++) parent[i] = i;   // every vertex starts as its own group

        Arrays.sort(roads, (x, y) -> x[2] - y[2]);              // cheapest roads first
        int total = 0;
        for (int[] r : roads) {
            int ra = find(r[0]), rb = find(r[1]);
            String name = "" + names.charAt(r[0]) + names.charAt(r[1]);
            if (ra == rb) {
                System.out.println("skip " + name + " " + r[2] + " (would make a cycle)");
                continue;
            }
            parent[ra] = rb;                // union: join the two groups
            total += r[2];
            System.out.println("take " + name + " " + r[2]);
        }
        System.out.println("total " + total);
    }
}
''')

C('islands', py=r'''
grid = ["11000",
        "11010",
        "00100",
        "00011"]
rows, cols = len(grid), len(grid[0])
seen = [[False] * cols for _ in range(rows)]

count = 0
for r in range(rows):
    for c in range(cols):
        if grid[r][c] == "1" and not seen[r][c]:
            count += 1                # new land that no earlier island reached
            size = 0
            stack = [(r, c)]
            seen[r][c] = True
            while stack:
                y, x = stack.pop()
                size += 1
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):   # four neighbours
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == "1" and not seen[ny][nx]:
                        seen[ny][nx] = True
                        stack.append((ny, nx))
            print("island", count, "starts at", (r, c), "size", size)
print("islands:", count)
''', js=r'''
const grid = ["11000",
              "11010",
              "00100",
              "00011"];
const rows = grid.length, cols = grid[0].length;
const seen = Array.from({ length: rows }, () => new Array(cols).fill(false));

let count = 0;
for (let r = 0; r < rows; r++) {
  for (let c = 0; c < cols; c++) {
    if (grid[r][c] === "1" && !seen[r][c]) {
      count++;                        // new land that no earlier island reached
      let size = 0;
      const stack = [[r, c]];
      seen[r][c] = true;
      while (stack.length > 0) {
        const [y, x] = stack.pop();
        size++;
        for (const [dy, dx] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {   // four neighbours
          const ny = y + dy, nx = x + dx;
          if (ny >= 0 && ny < rows && nx >= 0 && nx < cols && grid[ny][nx] === "1" && !seen[ny][nx]) {
            seen[ny][nx] = true;
            stack.push([ny, nx]);
          }
        }
      }
      console.log("island", count, "starts at", `(${r}, ${c})`, "size", size);
    }
  }
}
console.log("islands:", count);
''', java=r'''
import java.util.ArrayDeque;

public class Islands {
    public static void main(String[] args) {
        String[] grid = {"11000",
                         "11010",
                         "00100",
                         "00011"};
        int rows = grid.length, cols = grid[0].length();
        boolean[][] seen = new boolean[rows][cols];
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};   // four neighbours

        int count = 0;
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (grid[r].charAt(c) == '1' && !seen[r][c]) {
                    count++;                // new land that no earlier island reached
                    int size = 0;
                    ArrayDeque<int[]> stack = new ArrayDeque<>();
                    stack.push(new int[]{r, c});
                    seen[r][c] = true;
                    while (!stack.isEmpty()) {
                        int[] cell = stack.pop();
                        size++;
                        for (int[] d : dirs) {
                            int ny = cell[0] + d[0], nx = cell[1] + d[1];
                            if (ny >= 0 && ny < rows && nx >= 0 && nx < cols && grid[ny].charAt(nx) == '1' && !seen[ny][nx]) {
                                seen[ny][nx] = true;
                                stack.push(new int[]{ny, nx});
                            }
                        }
                    }
                    System.out.println("island " + count + " starts at (" + r + ", " + c + ") size " + size);
                }
            }
        }
        System.out.println("islands: " + count);
    }
}
''')

# ---------------------------------------------------------------- practice programs
C('p_path_exists', py=r'''
from collections import deque


def path_exists(n, edges, src, dst):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = [False] * n
    seen[src] = True
    queue = deque([src])
    while queue:
        v = queue.popleft()
        if v == dst:
            return True
        for w in adj[v]:
            if not seen[w]:
                seen[w] = True
                queue.append(w)
    return False                      # the whole reachable part was explored


edges = [(0, 1), (0, 2), (3, 5), (5, 4), (4, 3)]
for src, dst in [(0, 2), (0, 5), (3, 4)]:
    print(src, "->", dst, "true" if path_exists(6, edges, src, dst) else "false")
''', js=r'''
function pathExists(n, edges, src, dst) {
  const adj = Array.from({ length: n }, () => []);
  for (const [a, b] of edges) {
    adj[a].push(b);
    adj[b].push(a);
  }
  const seen = new Array(n).fill(false);
  seen[src] = true;
  const queue = [src];
  for (let h = 0; h < queue.length; h++) {
    const v = queue[h];
    if (v === dst) return true;
    for (const w of adj[v]) {
      if (!seen[w]) {
        seen[w] = true;
        queue.push(w);
      }
    }
  }
  return false;                       // the whole reachable part was explored
}

const edges = [[0, 1], [0, 2], [3, 5], [5, 4], [4, 3]];
for (const [src, dst] of [[0, 2], [0, 5], [3, 4]]) {
  console.log(src, "->", dst, pathExists(6, edges, src, dst) ? "true" : "false");
}
''', java=r'''
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;

public class PathExists {
    static boolean pathExists(int n, int[][] edges, int src, int dst) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int v = 0; v < n; v++) adj.add(new ArrayList<>());
        for (int[] e : edges) {
            adj.get(e[0]).add(e[1]);
            adj.get(e[1]).add(e[0]);
        }
        boolean[] seen = new boolean[n];
        seen[src] = true;
        ArrayDeque<Integer> queue = new ArrayDeque<>();
        queue.add(src);
        while (!queue.isEmpty()) {
            int v = queue.poll();
            if (v == dst) return true;
            for (int w : adj.get(v)) {
                if (!seen[w]) {
                    seen[w] = true;
                    queue.add(w);
                }
            }
        }
        return false;                       // the whole reachable part was explored
    }

    public static void main(String[] args) {
        int[][] edges = {{0, 1}, {0, 2}, {3, 5}, {5, 4}, {4, 3}};
        int[][] queries = {{0, 2}, {0, 5}, {3, 4}};
        for (int[] q : queries) {
            System.out.println(q[0] + " -> " + q[1] + " " + (pathExists(6, edges, q[0], q[1]) ? "true" : "false"));
        }
    }
}
''')

C('p_town_judge', py=r'''
def find_judge(n, trust):
    score = [0] * (n + 1)
    for a, b in trust:
        score[a] -= 1                 # trusting someone rules you out
        score[b] += 1                 # being trusted counts towards judge
    for p in range(1, n + 1):
        if score[p] == n - 1:         # trusted by everyone else, trusts nobody
            return p
    return -1


print(find_judge(3, [(1, 3), (2, 3)]))
print(find_judge(3, [(1, 3), (2, 3), (3, 1)]))
print(find_judge(4, [(1, 3), (1, 4), (2, 3), (2, 4), (4, 3)]))
''', js=r'''
function findJudge(n, trust) {
  const score = new Array(n + 1).fill(0);
  for (const [a, b] of trust) {
    score[a]--;                       // trusting someone rules you out
    score[b]++;                       // being trusted counts towards judge
  }
  for (let p = 1; p <= n; p++) {
    if (score[p] === n - 1) return p; // trusted by everyone else, trusts nobody
  }
  return -1;
}

console.log(findJudge(3, [[1, 3], [2, 3]]));
console.log(findJudge(3, [[1, 3], [2, 3], [3, 1]]));
console.log(findJudge(4, [[1, 3], [1, 4], [2, 3], [2, 4], [4, 3]]));
''', java=r'''
public class TownJudge {
    static int findJudge(int n, int[][] trust) {
        int[] score = new int[n + 1];
        for (int[] t : trust) {
            score[t[0]]--;                  // trusting someone rules you out
            score[t[1]]++;                  // being trusted counts towards judge
        }
        for (int p = 1; p <= n; p++) {
            if (score[p] == n - 1) return p;  // trusted by everyone else, trusts nobody
        }
        return -1;
    }

    public static void main(String[] args) {
        System.out.println(findJudge(3, new int[][]{{1, 3}, {2, 3}}));
        System.out.println(findJudge(3, new int[][]{{1, 3}, {2, 3}, {3, 1}}));
        System.out.println(findJudge(4, new int[][]{{1, 3}, {1, 4}, {2, 3}, {2, 4}, {4, 3}}));
    }
}
''')

C('p_bipartite', py=r'''
from collections import deque


def two_colour(adj):
    colour = [-1] * len(adj)
    for start in range(len(adj)):
        if colour[start] != -1:
            continue
        colour[start] = 0
        queue = deque([start])
        while queue:
            v = queue.popleft()
            for w in adj[v]:
                if colour[w] == -1:
                    colour[w] = 1 - colour[v]   # neighbours get the other colour
                    queue.append(w)
                elif colour[w] == colour[v]:
                    return None               # two neighbours share a colour
    return colour


for adj in [[[1, 3], [0, 2], [1, 3], [0, 2]], [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]]:
    c = two_colour(adj)
    print("bipartite, colours " + " ".join(str(x) for x in c) if c else "not bipartite")
''', js=r'''
function twoColour(adj) {
  const colour = new Array(adj.length).fill(-1);
  for (let start = 0; start < adj.length; start++) {
    if (colour[start] !== -1) continue;
    colour[start] = 0;
    const queue = [start];
    for (let h = 0; h < queue.length; h++) {
      const v = queue[h];
      for (const w of adj[v]) {
        if (colour[w] === -1) {
          colour[w] = 1 - colour[v];  // neighbours get the other colour
          queue.push(w);
        } else if (colour[w] === colour[v]) {
          return null;                // two neighbours share a colour
        }
      }
    }
  }
  return colour;
}

for (const adj of [[[1, 3], [0, 2], [1, 3], [0, 2]], [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]]) {
  const c = twoColour(adj);
  console.log(c ? "bipartite, colours " + c.join(" ") : "not bipartite");
}
''', java=r'''
import java.util.ArrayDeque;
import java.util.Arrays;

public class Bipartite {
    static int[] twoColour(int[][] adj) {
        int[] colour = new int[adj.length];
        Arrays.fill(colour, -1);
        for (int start = 0; start < adj.length; start++) {
            if (colour[start] != -1) continue;
            colour[start] = 0;
            ArrayDeque<Integer> queue = new ArrayDeque<>();
            queue.add(start);
            while (!queue.isEmpty()) {
                int v = queue.poll();
                for (int w : adj[v]) {
                    if (colour[w] == -1) {
                        colour[w] = 1 - colour[v];   // neighbours get the other colour
                        queue.add(w);
                    } else if (colour[w] == colour[v]) {
                        return null;                 // two neighbours share a colour
                    }
                }
            }
        }
        return colour;
    }

    public static void main(String[] args) {
        int[][][] graphs = {{{1, 3}, {0, 2}, {1, 3}, {0, 2}}, {{1, 2, 3}, {0, 2}, {0, 1, 3}, {0, 2}}};
        for (int[][] adj : graphs) {
            int[] c = twoColour(adj);
            if (c == null) {
                System.out.println("not bipartite");
            } else {
                StringBuilder sb = new StringBuilder();
                for (int x : c) sb.append(sb.length() > 0 ? " " : "").append(x);
                System.out.println("bipartite, colours " + sb);
            }
        }
    }
}
''')

C('p_rotting', py=r'''
from collections import deque


def minutes_to_rot(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c, 0))   # every rotten orange starts at once
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    while queue:
        r, c, t = queue.popleft()
        minutes = max(minutes, t)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2
                fresh -= 1
                queue.append((nr, nc, t + 1))
    return minutes if fresh == 0 else -1


print(minutes_to_rot([[2, 1, 1], [1, 1, 0], [0, 1, 1]]))
print(minutes_to_rot([[2, 1, 1], [0, 1, 1], [1, 0, 1]]))
''', js=r'''
function minutesToRot(grid) {
  const rows = grid.length, cols = grid[0].length;
  const queue = [];
  let fresh = 0;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (grid[r][c] === 2) queue.push([r, c, 0]);   // every rotten orange starts at once
      else if (grid[r][c] === 1) fresh++;
    }
  }
  let minutes = 0;
  for (let h = 0; h < queue.length; h++) {
    const [r, c, t] = queue[h];
    minutes = Math.max(minutes, t);
    for (const [dr, dc] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const nr = r + dr, nc = c + dc;
      if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] === 1) {
        grid[nr][nc] = 2;
        fresh--;
        queue.push([nr, nc, t + 1]);
      }
    }
  }
  return fresh === 0 ? minutes : -1;
}

console.log(minutesToRot([[2, 1, 1], [1, 1, 0], [0, 1, 1]]));
console.log(minutesToRot([[2, 1, 1], [0, 1, 1], [1, 0, 1]]));
''', java=r'''
import java.util.ArrayDeque;

public class Rotting {
    static int minutesToRot(int[][] grid) {
        int rows = grid.length, cols = grid[0].length;
        ArrayDeque<int[]> queue = new ArrayDeque<>();
        int fresh = 0;
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (grid[r][c] == 2) queue.add(new int[]{r, c, 0});   // every rotten orange starts at once
                else if (grid[r][c] == 1) fresh++;
            }
        }
        int minutes = 0;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!queue.isEmpty()) {
            int[] cur = queue.poll();
            minutes = Math.max(minutes, cur[2]);
            for (int[] d : dirs) {
                int nr = cur[0] + d[0], nc = cur[1] + d[1];
                if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] == 1) {
                    grid[nr][nc] = 2;
                    fresh--;
                    queue.add(new int[]{nr, nc, cur[2] + 1});
                }
            }
        }
        return fresh == 0 ? minutes : -1;
    }

    public static void main(String[] args) {
        System.out.println(minutesToRot(new int[][]{{2, 1, 1}, {1, 1, 0}, {0, 1, 1}}));
        System.out.println(minutesToRot(new int[][]{{2, 1, 1}, {0, 1, 1}, {1, 0, 1}}));
    }
}
''')

C('p_word_ladder', py=r'''
from collections import deque


def one_apart(a, b):
    diff = 0
    for x, y in zip(a, b):
        if x != y:
            diff += 1
    return diff == 1                  # an edge joins words that differ in one letter


def ladder(begin, end, words):
    parent = {begin: None}
    queue = deque([begin])
    while queue:
        w = queue.popleft()
        if w == end:
            path = []
            while w is not None:
                path.append(w)
                w = parent[w]
            return path[::-1]
        for nxt in words:
            if nxt not in parent and one_apart(w, nxt):
                parent[nxt] = w       # first time seen, so along a shortest ladder
                queue.append(nxt)
    return []


for words in [["hot", "dot", "dog", "lot", "log", "cog"], ["hot", "dot", "dog", "lot", "log"]]:
    path = ladder("hit", "cog", words)
    print("length", len(path), ":", " ".join(path) if path else "no ladder")
''', js=r'''
function oneApart(a, b) {
  let diff = 0;
  for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) diff++;
  return diff === 1;                  // an edge joins words that differ in one letter
}

function ladder(begin, end, words) {
  const parent = new Map([[begin, null]]);
  const queue = [begin];
  for (let h = 0; h < queue.length; h++) {
    let w = queue[h];
    if (w === end) {
      const path = [];
      while (w !== null) {
        path.push(w);
        w = parent.get(w);
      }
      return path.reverse();
    }
    for (const nxt of words) {
      if (!parent.has(nxt) && oneApart(w, nxt)) {
        parent.set(nxt, w);           // first time seen, so along a shortest ladder
        queue.push(nxt);
      }
    }
  }
  return [];
}

for (const words of [["hot", "dot", "dog", "lot", "log", "cog"], ["hot", "dot", "dog", "lot", "log"]]) {
  const path = ladder("hit", "cog", words);
  console.log("length", path.length, ":", path.length ? path.join(" ") : "no ladder");
}
''', java=r'''
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class WordLadder {
    static boolean oneApart(String a, String b) {
        int diff = 0;
        for (int i = 0; i < a.length(); i++) if (a.charAt(i) != b.charAt(i)) diff++;
        return diff == 1;                   // an edge joins words that differ in one letter
    }

    static List<String> ladder(String begin, String end, List<String> words) {
        Map<String, String> parent = new HashMap<>();
        parent.put(begin, null);
        ArrayDeque<String> queue = new ArrayDeque<>();
        queue.add(begin);
        while (!queue.isEmpty()) {
            String w = queue.poll();
            if (w.equals(end)) {
                List<String> path = new ArrayList<>();
                while (w != null) {
                    path.add(w);
                    w = parent.get(w);
                }
                Collections.reverse(path);
                return path;
            }
            for (String nxt : words) {
                if (!parent.containsKey(nxt) && oneApart(w, nxt)) {
                    parent.put(nxt, w);     // first time seen, so along a shortest ladder
                    queue.add(nxt);
                }
            }
        }
        return new ArrayList<>();
    }

    public static void main(String[] args) {
        List<List<String>> tests = List.of(List.of("hot", "dot", "dog", "lot", "log", "cog"), List.of("hot", "dot", "dog", "lot", "log"));
        for (List<String> words : tests) {
            List<String> path = ladder("hit", "cog", words);
            System.out.println("length " + path.size() + " : " + (path.isEmpty() ? "no ladder" : String.join(" ", path)));
        }
    }
}
''')

C('p_redundant', py=r'''
def redundant(edges):
    parent = list(range(len(edges) + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            return (a, b)             # a and b were already connected: this edge closes a cycle
        parent[ra] = rb
    return None


print(redundant([(1, 2), (1, 3), (2, 3)]))
print(redundant([(1, 2), (2, 3), (3, 4), (1, 4), (1, 5)]))
''', js=r'''
function redundant(edges) {
  const parent = Array.from({ length: edges.length + 1 }, (_, i) => i);
  const find = x => {
    while (parent[x] !== x) {
      parent[x] = parent[parent[x]];
      x = parent[x];
    }
    return x;
  };
  for (const [a, b] of edges) {
    const ra = find(a), rb = find(b);
    if (ra === rb) return `(${a}, ${b})`;   // a and b were already connected: this edge closes a cycle
    parent[ra] = rb;
  }
  return null;
}

console.log(redundant([[1, 2], [1, 3], [2, 3]]));
console.log(redundant([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]));
''', java=r'''
public class Redundant {
    static int[] parent;

    static int find(int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    }

    static String redundant(int[][] edges) {
        parent = new int[edges.length + 1];
        for (int i = 0; i < parent.length; i++) parent[i] = i;
        for (int[] e : edges) {
            int ra = find(e[0]), rb = find(e[1]);
            if (ra == rb) return "(" + e[0] + ", " + e[1] + ")";   // a and b were already connected: this edge closes a cycle
            parent[ra] = rb;
        }
        return null;
    }

    public static void main(String[] args) {
        System.out.println(redundant(new int[][]{{1, 2}, {1, 3}, {2, 3}}));
        System.out.println(redundant(new int[][]{{1, 2}, {2, 3}, {3, 4}, {1, 4}, {1, 5}}));
    }
}
''')

C('p_cheapest_flights', py=r'''
def cheapest(n, flights, src, dst, k):
    INF = float("inf")
    cost = [INF] * n
    cost[src] = 0
    for _ in range(k + 1):            # at most k stops means at most k + 1 flights
        nxt = cost[:]                 # read last round, write this round
        for a, b, price in flights:
            if cost[a] + price < nxt[b]:
                nxt[b] = cost[a] + price
        cost = nxt
    return cost[dst] if cost[dst] != INF else -1


flights = [(0, 1, 100), (1, 2, 100), (2, 0, 100), (1, 3, 600), (2, 3, 200)]
for k in [0, 1, 2]:
    print("stops", k, "cost", cheapest(4, flights, 0, 3, k))
''', js=r'''
function cheapest(n, flights, src, dst, k) {
  let cost = new Array(n).fill(Infinity);
  cost[src] = 0;
  for (let round = 0; round <= k; round++) {   // at most k stops means at most k + 1 flights
    const nxt = cost.slice();                   // read last round, write this round
    for (const [a, b, price] of flights) {
      if (cost[a] + price < nxt[b]) nxt[b] = cost[a] + price;
    }
    cost = nxt;
  }
  return cost[dst] !== Infinity ? cost[dst] : -1;
}

const flights = [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]];
for (const k of [0, 1, 2]) console.log("stops", k, "cost", cheapest(4, flights, 0, 3, k));
''', java=r'''
import java.util.Arrays;

public class CheapestFlights {
    static int cheapest(int n, int[][] flights, int src, int dst, int k) {
        final int INF = Integer.MAX_VALUE / 2;
        int[] cost = new int[n];
        Arrays.fill(cost, INF);
        cost[src] = 0;
        for (int round = 0; round <= k; round++) {   // at most k stops means at most k + 1 flights
            int[] nxt = cost.clone();                 // read last round, write this round
            for (int[] f : flights) {
                if (cost[f[0]] + f[2] < nxt[f[1]]) nxt[f[1]] = cost[f[0]] + f[2];
            }
            cost = nxt;
        }
        return cost[dst] != INF ? cost[dst] : -1;
    }

    public static void main(String[] args) {
        int[][] flights = {{0, 1, 100}, {1, 2, 100}, {2, 0, 100}, {1, 3, 600}, {2, 3, 200}};
        for (int k = 0; k <= 2; k++) System.out.println("stops " + k + " cost " + cheapest(4, flights, 0, 3, k));
    }
}
''')

C('p_bridges', py=r'''
def bridges(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    disc = [-1] * n                   # when each vertex was discovered
    low = [0] * n                     # earliest discovery time reachable from its subtree
    out = []
    timer = [0]

    def dfs(v, parent):
        disc[v] = low[v] = timer[0]
        timer[0] += 1
        for w in adj[v]:
            if w == parent:
                continue
            if disc[w] == -1:
                dfs(w, v)
                low[v] = min(low[v], low[w])
                if low[w] > disc[v]:  # w's subtree cannot climb back above v
                    out.append((v, w))
            else:
                low[v] = min(low[v], disc[w])   # a back edge to an ancestor

    dfs(0, -1)
    return out


for n, edges in [(4, [(0, 1), (1, 2), (2, 0), (1, 3)]),
                 (7, [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4), (4, 5), (5, 3), (5, 6)])]:
    print("bridges:", " ".join(f"{a}-{b}" for a, b in bridges(n, edges)))
''', js=r'''
function bridges(n, edges) {
  const adj = Array.from({ length: n }, () => []);
  for (const [a, b] of edges) {
    adj[a].push(b);
    adj[b].push(a);
  }
  const disc = new Array(n).fill(-1);  // when each vertex was discovered
  const low = new Array(n).fill(0);    // earliest discovery time reachable from its subtree
  const out = [];
  let timer = 0;

  function dfs(v, parent) {
    disc[v] = low[v] = timer++;
    for (const w of adj[v]) {
      if (w === parent) continue;
      if (disc[w] === -1) {
        dfs(w, v);
        low[v] = Math.min(low[v], low[w]);
        if (low[w] > disc[v]) out.push(`${v}-${w}`);   // w's subtree cannot climb back above v
      } else {
        low[v] = Math.min(low[v], disc[w]);            // a back edge to an ancestor
      }
    }
  }

  dfs(0, -1);
  return out;
}

for (const [n, edges] of [[4, [[0, 1], [1, 2], [2, 0], [1, 3]]],
                          [7, [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4], [4, 5], [5, 3], [5, 6]]]]) {
  console.log("bridges:", bridges(n, edges).join(" "));
}
''', java=r'''
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Bridges {
    static List<List<Integer>> adj;
    static int[] disc, low;
    static int timer;
    static List<String> out;

    static void dfs(int v, int parent) {
        disc[v] = low[v] = timer++;
        for (int w : adj.get(v)) {
            if (w == parent) continue;
            if (disc[w] == -1) {
                dfs(w, v);
                low[v] = Math.min(low[v], low[w]);
                if (low[w] > disc[v]) out.add(v + "-" + w);   // w's subtree cannot climb back above v
            } else {
                low[v] = Math.min(low[v], disc[w]);           // a back edge to an ancestor
            }
        }
    }

    static List<String> bridges(int n, int[][] edges) {
        adj = new ArrayList<>();
        for (int v = 0; v < n; v++) adj.add(new ArrayList<>());
        for (int[] e : edges) {
            adj.get(e[0]).add(e[1]);
            adj.get(e[1]).add(e[0]);
        }
        disc = new int[n];          // when each vertex was discovered
        low = new int[n];           // earliest discovery time reachable from its subtree
        Arrays.fill(disc, -1);
        timer = 0;
        out = new ArrayList<>();
        dfs(0, -1);
        return out;
    }

    public static void main(String[] args) {
        System.out.println("bridges: " + String.join(" ", bridges(4, new int[][]{{0, 1}, {1, 2}, {2, 0}, {1, 3}})));
        System.out.println("bridges: " + String.join(" ", bridges(7, new int[][]{{0, 1}, {1, 2}, {2, 0}, {1, 3}, {3, 4}, {4, 5}, {5, 3}, {5, 6}})));
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    dict(id='what-is', emoji='🕸️', title='What a graph is', html='''
<p>A <b>graph</b> is a set of <b>vertices</b> (also called nodes) joined by <b>edges</b>. Unlike a tree, a graph has no root and may contain loops, so you can walk in a circle and come back to where you started. Road maps, friendships, flight routes, web links and computer networks are all graphs.</p>
<div class="grid2">
<div class="box"><h4>↔️ Undirected or directed</h4><p>A friendship goes both ways, so it is an undirected edge. "A follows B" goes one way, so it is a directed edge, drawn with an arrow.</p></div>
<div class="box"><h4>⚖️ Weighted</h4><p>An edge can carry a number such as a distance, a price or a travel time. Shortest path algorithms add these weights up.</p></div>
</div>
<p>Programs store a graph in one of two ways.</p>
<div class="tw"><table class="jt"><tr><th></th><th>Adjacency list</th><th>Adjacency matrix</th></tr>
<tr><td>Idea</td><td>for each vertex, a list of its neighbours</td><td>a V × V grid with 1 where an edge exists</td></tr>
<tr><td>Memory</td><td class="yes">O(V + E)</td><td>O(V²)</td></tr>
<tr><td>Is u next to v?</td><td>O(degree of u)</td><td class="yes">O(1)</td></tr>
<tr><td>Visit all neighbours of u</td><td class="yes">O(degree of u)</td><td>O(V)</td></tr>
<tr><td>Best for</td><td>sparse graphs, which is most real graphs</td><td>small or very dense graphs</td></tr>
</table></div>
<div class="c3" data-k="graph_repr" data-label="The same graph as a list and as a matrix"></div>
<div class="grid2">
<div class="box"><h4>🤝 Handshakes</h4><p>Each undirected edge adds 1 to the degree of both of its ends.</p><span class="eq">sum of all degrees = 2E</span></div>
<div class="box"><h4>🔢 Most possible edges</h4><p>A simple undirected graph with V vertices has at most</p><span class="eq">E ≤ V(V − 1) / 2</span></div>
</div>
'''),
    dict(id='bfs', emoji='🌊', title='Breadth first search', html='''
<p><b>Breadth first search</b> (BFS) explores a graph in rings. It visits the start, then every vertex one edge away, then every vertex two edges away, and so on. A <b>queue</b> keeps the discovered vertices in order, and a <b>seen</b> mark stops any vertex from being added twice.</p>
<div class="viz" data-viz="search"></div>
<div class="c3" data-k="bfs" data-label="BFS distances and a shortest path"></div>
<div class="rule">In a graph without weights, the first time BFS reaches a vertex is along a shortest path. Remember the parent of each vertex and you can walk the path back.</div>
<p>Every vertex enters the queue once and every edge is looked at once from each end, so BFS takes</p>
<span class="eq">O(V + E)</span>
'''),
    dict(id='dfs', emoji='🧗', title='Depth first search', html='''
<p><b>Depth first search</b> (DFS) follows one path as far as it can go, then backs up to the last vertex with an unexplored neighbour and tries again. Recursion gives it a stack for free. Switch the animation above to DFS to compare the two orders.</p>
<div class="c3" data-k="dfs_components" data-label="Counting connected components with DFS"></div>
<div class="tw"><table class="jt"><tr><th></th><th>BFS</th><th>DFS</th></tr>
<tr><td>Helper structure</td><td>queue</td><td>stack or recursion</td></tr>
<tr><td>Explores</td><td>ring by ring</td><td>one deep path at a time</td></tr>
<tr><td>Shortest path without weights</td><td class="yes">yes</td><td>no</td></tr>
<tr><td>Good for</td><td>fewest steps, nearest first</td><td>components, cycles, mazes, topological order</td></tr>
<tr><td>Time</td><td>O(V + E)</td><td>O(V + E)</td></tr>
</table></div>
<div class="warn">Deep recursion can overflow the call stack on a graph with hundreds of thousands of vertices in a line. Python stops at about 1000 levels by default. For large inputs, write DFS with your own stack.</div>
'''),
    dict(id='topo', emoji='👕', title='Topological order', html='''
<p>Some tasks must happen before others: socks before shoes, a course before the next course, a library before the program that uses it. Draw an arrow from each task to the task that depends on it, and you get a <b>directed acyclic graph</b> (DAG). A <b>topological order</b> lists every task so that all arrows point forwards.</p>
<div class="viz" data-viz="topo"></div>
<p><b>Kahn's algorithm</b> counts how many arrows point into each vertex (its in-degree). Every vertex with in-degree 0 is ready. Take a ready vertex, add it to the order, and remove its outgoing arrows, which may make new vertices ready.</p>
<div class="c3" data-k="topo_sort" data-label="Getting dressed in a valid order"></div>
<div class="exam">If the order ends up shorter than the number of vertices, some vertices never became ready. That only happens when the graph has a <b>cycle</b>, so Kahn's algorithm is also a cycle detector.</div>
'''),
    dict(id='dijkstra', emoji='🗺️', title="Dijkstra's shortest paths", html='''
<p>When edges have weights, the path with the fewest edges is not always the cheapest. <b>Dijkstra's algorithm</b> grows a set of settled vertices whose shortest distance is final. Each round it settles the closest unsettled vertex, then tries to improve each neighbour through it. Trying to improve a neighbour is called <b>relaxing</b> an edge.</p>
<span class="eq">if dist[v] + w &lt; dist[u] then dist[u] = dist[v] + w</span>
<div class="viz" data-viz="dijk"></div>
<div class="c3" data-k="dijkstra" data-label="Dijkstra with a priority queue"></div>
<p>With a binary heap as the priority queue, the running time is</p>
<span class="eq">O((V + E) log V)</span>
<div class="warn">Dijkstra needs weights that are zero or positive. A negative edge can make a settled distance wrong. For negative weights use Bellman-Ford, which relaxes every edge V − 1 times in O(V · E).</div>
'''),
    dict(id='mst', emoji='🔌', title='Minimum spanning trees and union find', html='''
<p>A town wants to connect every house to the network with the least cable. A <b>spanning tree</b> connects all V vertices with exactly V − 1 edges and no cycle. The <b>minimum spanning tree</b> (MST) is the one with the smallest total weight.</p>
<p><b>Kruskal's algorithm</b> sorts the edges from cheapest to most expensive and takes each one unless it would close a cycle. To check that quickly it uses <b>union find</b>: every vertex points towards a leader of its group, <code>find</code> follows the pointers to the leader, and <code>union</code> joins two groups by pointing one leader at the other.</p>
<div class="c3" data-k="kruskal" data-label="Kruskal's algorithm with union find"></div>
<div class="tw"><table class="jt"><tr><th>Step</th><th>Cost</th></tr>
<tr><td>sort the edges</td><td>O(E log E)</td></tr>
<tr><td>find and union, with path compression</td><td class="yes">almost O(1) each</td></tr>
<tr><td>total</td><td>O(E log E)</td></tr>
</table></div>
<div class="tip">Union find also answers "are these two computers on the same network?" and "which edge closes a cycle?" without a full search.</div>
'''),
    dict(id='grids', emoji='🏝️', title='Grids are graphs too', html='''
<p>Many puzzles hide a graph inside a grid. Every cell is a vertex, and it is joined to its four neighbours up, down, left and right. You never build an adjacency list. You compute the neighbours with small offsets and check that they stay inside the grid.</p>
<div class="viz" data-viz="grid"></div>
<div class="c3" data-k="islands" data-label="Counting islands with a flood fill"></div>
<div class="rule">Scan every cell. When you find land that has not been seen, it starts a new island, and a BFS or DFS flood marks the whole island so it is never counted again. Each cell is handled a constant number of times, so the total is O(rows × cols).</div>
'''),
]

INFO = {
    'title': 'Dots and lines everywhere',
    'panels': [
        {'s': [['e', '🕸️'], ['t', 'vertices + edges', {'b': 1}]], 'h': 'Graph', 't': 'Things, and the links between them.', 'more': 'Maps, friendships, flights and web pages are all graphs.'},
        {'s': [['e', '🌊'], ['c', [0, 1, 1, 2], {'hl': {0: 'ok'}, 'p': {0: 'start'}}]], 'h': 'BFS', 't': 'Explore ring by ring with a queue.', 'more': 'The first visit to a vertex is along a shortest path when edges have no weights.'},
        {'s': [['e', '👕'], ['t', 'socks → shoes', {'b': 1}]], 'h': 'Topological order', 't': 'Do every task after the tasks it needs.', 'more': 'Build systems, course plans and spreadsheets all sort their dependencies this way.'},
        {'s': [['e', '🗺️'], ['t', 'settle the closest first', {'b': 1}]], 'h': 'Dijkstra', 't': 'Cheapest routes with weighted edges.', 'more': 'A priority queue always hands back the nearest unsettled place.'},
    ],
    'remember': 'Store graphs as adjacency lists. BFS for fewest steps, DFS for exploring and ordering, Dijkstra for weighted shortest paths, union find for connecting groups.',
}

REAL = [
    ['🧭', 'Navigation apps', 'Roads are weighted edges between junctions. Route planners run Dijkstra and faster relatives such as A* to find the quickest way home.'],
    ['👥', 'Friend suggestions', 'People you may know are often two edges away: friends of your friends. That is one extra ring of a breadth first search.'],
    ['📦', 'Installing software', 'Package managers sort libraries topologically so every dependency is installed before the package that needs it, and they report a cycle when two packages need each other.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome',
     'en': 'Welcome to graphs. A graph is a set of vertices joined by edges, and it can model roads, friendships, networks and plans. You will store graphs, explore them with breadth first and depth first search, order tasks, find shortest paths and connect everything with the least cost.',
     'hi': 'Graphs में आपका स्वागत है। Graph vertices का समूह है जो edges से जुड़े होते हैं, और यह सड़कों, दोस्तियों, networks और योजनाओं को दर्शा सकता है। आप graphs को store करेंगे, breadth first और depth first search से उन्हें खोजेंगे, कामों को क्रम देंगे, सबसे छोटे रास्ते ढूँढेंगे और सबसे कम लागत में सब कुछ जोड़ेंगे।',
     'kn': 'Graphs ಗೆ ಸ್ವಾಗತ. Graph ಎಂದರೆ edges ನಿಂದ ಜೋಡಿಸಿದ vertices ಗಳ ಗುಂಪು, ಇದು ರಸ್ತೆಗಳು, ಸ್ನೇಹಗಳು, networks ಮತ್ತು ಯೋಜನೆಗಳನ್ನು ಪ್ರತಿನಿಧಿಸಬಲ್ಲದು. ನೀವು graphs store ಮಾಡುತ್ತೀರಿ, breadth first ಮತ್ತು depth first search ನಿಂದ ಅನ್ವೇಷಿಸುತ್ತೀರಿ, ಕೆಲಸಗಳನ್ನು ಕ್ರಮಗೊಳಿಸುತ್ತೀರಿ, ಅತಿ ಚಿಕ್ಕ ದಾರಿಗಳನ್ನು ಹುಡುಕುತ್ತೀರಿ ಮತ್ತು ಕಡಿಮೆ ವೆಚ್ಚದಲ್ಲಿ ಎಲ್ಲವನ್ನೂ ಜೋಡಿಸುತ್ತೀರಿ.',
     'or': 'Graphs କୁ ସ୍ୱାଗତ। Graph ହେଉଛି edges ଦ୍ୱାରା ଯୋଡ଼ା vertices ର ସମୂହ, ଏବଂ ଏହା ରାସ୍ତା, ବନ୍ଧୁତା, networks ଓ ଯୋଜନାକୁ ଦର୍ଶାଇପାରେ। ଆପଣ graphs store କରିବେ, breadth first ଓ depth first search ରେ ଖୋଜିବେ, କାମକୁ କ୍ରମ ଦେବେ, ସବୁଠୁ ଛୋଟ ରାସ୍ତା ଖୋଜିବେ ଏବଂ କମ୍ ଖର୍ଚ୍ଚରେ ସବୁକିଛି ଯୋଡ଼ିବେ।',
     'ar': 'مرحبًا بك في الرسوم البيانية. الرسم البياني مجموعة رؤوس تربطها حواف، ويمكنه تمثيل الطرق والصداقات والشبكات والخطط. ستخزن الرسوم وتستكشفها بالبحث بالعرض والبحث بالعمق، وترتب المهام، وتجد أقصر الطرق، وتربط كل شيء بأقل تكلفة.',
     'de': 'Willkommen bei Graphen. Ein Graph ist eine Menge von Knoten, die durch Kanten verbunden sind, und kann Straßen, Freundschaften, Netzwerke und Pläne abbilden. Du speicherst Graphen, erkundest sie mit Breiten und Tiefensuche, ordnest Aufgaben, findest kürzeste Wege und verbindest alles mit den geringsten Kosten.'},
    {'id': 'what-is', 'h': 'What a graph is',
     'en': 'Edges can be undirected, like friendships, or directed, like follows. They can also carry weights such as distances. Most programs store a graph as an adjacency list, which keeps a list of neighbours for every vertex and uses memory proportional to vertices plus edges.',
     'hi': 'Edges undirected हो सकते हैं, जैसे दोस्ती, या directed, जैसे follow करना। उन पर दूरी जैसे weights भी हो सकते हैं। ज़्यादातर programs graph को adjacency list में रखते हैं, जो हर vertex के पड़ोसियों की सूची रखती है और vertices और edges के अनुपात में memory लेती है।',
     'kn': 'Edges undirected ಆಗಿರಬಹುದು, ಸ್ನೇಹದಂತೆ, ಅಥವಾ directed, follow ಮಾಡುವಂತೆ. ದೂರದಂತಹ weights ಕೂಡ ಇರಬಹುದು. ಹೆಚ್ಚಿನ programs graph ಅನ್ನು adjacency list ಆಗಿ ಇಡುತ್ತವೆ, ಅದು ಪ್ರತಿ vertex ನ ನೆರೆಹೊರೆಯವರ ಪಟ್ಟಿ ಇಡುತ್ತದೆ ಮತ್ತು vertices ಮತ್ತು edges ಗೆ ಅನುಗುಣವಾದ memory ಬಳಸುತ್ತದೆ.',
     'or': 'Edges undirected ହୋଇପାରେ, ବନ୍ଧୁତା ପରି, କିମ୍ବା directed, follow କରିବା ପରି। ସେଥିରେ ଦୂରତା ପରି weights ମଧ୍ୟ ରହିପାରେ। ଅଧିକାଂଶ programs graph କୁ adjacency list ରେ ରଖନ୍ତି, ଯାହା ପ୍ରତ୍ୟେକ vertex ର ପଡ଼ୋଶୀଙ୍କ ତାଲିକା ରଖେ ଓ vertices ଓ edges ଅନୁପାତରେ memory ନିଏ।',
     'ar': 'قد تكون الحواف غير موجهة مثل الصداقة، أو موجهة مثل المتابعة. وقد تحمل أوزانًا مثل المسافات. معظم البرامج تخزن الرسم كقائمة تجاور، تحفظ لكل رأس قائمة جيرانه وتستهلك ذاكرة تتناسب مع عدد الرؤوس والحواف.',
     'de': 'Kanten können ungerichtet sein wie Freundschaften oder gerichtet wie Folgen. Sie können auch Gewichte wie Entfernungen tragen. Die meisten Programme speichern einen Graphen als Adjazenzliste, die für jeden Knoten seine Nachbarn auflistet und Speicher proportional zu Knoten plus Kanten braucht.'},
    {'id': 'bfs', 'h': 'Breadth first search',
     'en': 'Breadth first search explores in rings around the start, using a queue. In a graph without weights, the first time it reaches a vertex is along a shortest path. Remember each parent and you can rebuild the path.',
     'hi': 'Breadth first search शुरुआत के चारों ओर छल्लों में खोजता है और queue इस्तेमाल करता है। बिना weights वाले graph में किसी vertex तक पहली बार पहुँचना सबसे छोटे रास्ते से होता है। हर parent याद रखें तो रास्ता फिर से बना सकते हैं।',
     'kn': 'Breadth first search ಆರಂಭದ ಸುತ್ತ ಉಂಗುರಗಳಂತೆ queue ಬಳಸಿ ಅನ್ವೇಷಿಸುತ್ತದೆ. Weights ಇಲ್ಲದ graph ನಲ್ಲಿ ಒಂದು vertex ಅನ್ನು ಮೊದಲ ಬಾರಿ ತಲುಪುವುದು ಅತಿ ಚಿಕ್ಕ ದಾರಿಯಲ್ಲಿ. ಪ್ರತಿ parent ನೆನಪಿಟ್ಟರೆ ದಾರಿಯನ್ನು ಮತ್ತೆ ಕಟ್ಟಬಹುದು.',
     'or': 'Breadth first search ଆରମ୍ଭ ଚାରିପଟେ ବଳୟ ଭଳି queue ବ୍ୟବହାର କରି ଖୋଜେ। Weights ନଥିବା graph ରେ ଗୋଟିଏ vertex କୁ ପ୍ରଥମ ଥର ପହଞ୍ଚିବା ସବୁଠୁ ଛୋଟ ରାସ୍ତାରେ ହୁଏ। ପ୍ରତ୍ୟେକ parent ମନେ ରଖିଲେ ରାସ୍ତା ପୁଣି ତିଆରି କରିହେବ।',
     'ar': 'البحث بالعرض يستكشف في حلقات حول نقطة البداية مستخدمًا طابورًا. في رسم بلا أوزان تكون أول مرة يصل فيها إلى رأس على طول أقصر طريق. احفظ أب كل رأس وستستطيع إعادة بناء الطريق.',
     'de': 'Die Breitensuche erkundet in Ringen um den Start und nutzt eine Warteschlange. In einem Graphen ohne Gewichte erreicht sie jeden Knoten zuerst über einen kürzesten Weg. Merkt man sich jeden Vorgänger, kann man den Weg rekonstruieren.'},
    {'id': 'dfs', 'h': 'Depth first search',
     'en': 'Depth first search follows one path as deep as it can, then backs up and tries the next branch. Recursion provides the stack. It counts connected components, finds cycles and solves mazes, also in linear time.',
     'hi': 'Depth first search एक रास्ते पर जितना गहरा हो सके जाता है, फिर पीछे लौटकर अगली शाखा आज़माता है। Recursion stack देता है। यह connected components गिनता है, cycles ढूँढता है और भूलभुलैया हल करता है, वह भी linear समय में।',
     'kn': 'Depth first search ಒಂದು ದಾರಿಯಲ್ಲಿ ಸಾಧ್ಯವಾದಷ್ಟು ಆಳಕ್ಕೆ ಹೋಗಿ, ನಂತರ ಹಿಂದಿರುಗಿ ಮುಂದಿನ ಕವಲು ಪ್ರಯತ್ನಿಸುತ್ತದೆ. Recursion stack ಕೊಡುತ್ತದೆ. ಇದು connected components ಎಣಿಸುತ್ತದೆ, cycles ಹುಡುಕುತ್ತದೆ ಮತ್ತು maze ಪರಿಹರಿಸುತ್ತದೆ, linear ಸಮಯದಲ್ಲಿ.',
     'or': 'Depth first search ଗୋଟିଏ ରାସ୍ତାରେ ଯେତେ ଗଭୀର ସମ୍ଭବ ଯାଏ, ତା’ପରେ ଫେରି ପରବର୍ତ୍ତୀ ଶାଖା ଚେଷ୍ଟା କରେ। Recursion stack ଦିଏ। ଏହା connected components ଗଣେ, cycles ଖୋଜେ ଓ maze ସମାଧାନ କରେ, linear ସମୟରେ।',
     'ar': 'البحث بالعمق يتبع طريقًا واحدًا إلى أعمق نقطة ممكنة، ثم يعود ويجرب الفرع التالي. والتعاود يوفر المكدس. يعد المكونات المتصلة ويجد الدورات ويحل المتاهات، في زمن خطي أيضًا.',
     'de': 'Die Tiefensuche folgt einem Pfad so tief wie möglich, geht dann zurück und probiert den nächsten Zweig. Die Rekursion liefert den Stapel. Sie zählt Zusammenhangskomponenten, findet Zyklen und löst Labyrinthe, ebenfalls in linearer Zeit.'},
    {'id': 'topo', 'h': 'Topological order',
     'en': 'A topological order lists tasks so that every task comes after everything it depends on. Kahn\'s algorithm repeatedly takes a task with no remaining requirements. If some tasks never become ready, the graph has a cycle.',
     'hi': 'Topological order कामों को ऐसे क्रम में रखता है कि हर काम अपनी सभी ज़रूरतों के बाद आए। Kahn का algorithm बार बार ऐसा काम लेता है जिसकी कोई ज़रूरत बाकी नहीं। अगर कुछ काम कभी तैयार नहीं होते, तो graph में cycle है।',
     'kn': 'Topological order ಪ್ರತಿ ಕೆಲಸವು ಅದು ಅವಲಂಬಿಸಿದ ಎಲ್ಲದರ ನಂತರ ಬರುವಂತೆ ಕೆಲಸಗಳನ್ನು ಪಟ್ಟಿ ಮಾಡುತ್ತದೆ. Kahn ನ algorithm ಯಾವುದೇ ಬಾಕಿ ಅಗತ್ಯವಿಲ್ಲದ ಕೆಲಸವನ್ನು ಪದೇ ಪದೇ ತೆಗೆದುಕೊಳ್ಳುತ್ತದೆ. ಕೆಲವು ಕೆಲಸಗಳು ಎಂದಿಗೂ ಸಿದ್ಧವಾಗದಿದ್ದರೆ graph ನಲ್ಲಿ cycle ಇದೆ.',
     'or': 'Topological order କାମଗୁଡ଼ିକୁ ଏପରି ତାଲିକା କରେ ଯେ ପ୍ରତ୍ୟେକ କାମ ତା’ର ସମସ୍ତ ଆବଶ୍ୟକତା ପରେ ଆସେ। Kahn ଙ୍କ algorithm ବାରମ୍ବାର ଏପରି କାମ ନିଏ ଯାହାର କୌଣସି ଆବଶ୍ୟକତା ବାକି ନାହିଁ। କିଛି କାମ କେବେ ପ୍ରସ୍ତୁତ ନହେଲେ graph ରେ cycle ଅଛି।',
     'ar': 'الترتيب الطوبولوجي يسرد المهام بحيث تأتي كل مهمة بعد كل ما تعتمد عليه. خوارزمية كان تأخذ مرارًا مهمة لم يبق لها أي متطلب. وإذا لم تصبح بعض المهام جاهزة أبدًا ففي الرسم دورة.',
     'de': 'Eine topologische Ordnung listet Aufgaben so, dass jede nach allem kommt, wovon sie abhängt. Kahns Algorithmus nimmt immer wieder eine Aufgabe ohne offene Voraussetzungen. Werden manche Aufgaben nie bereit, enthält der Graph einen Zyklus.'},
    {'id': 'dijkstra', 'h': 'Dijkstra',
     'en': 'Dijkstra\'s algorithm settles the closest unsettled vertex each round and relaxes its edges, improving any neighbour it can reach more cheaply. A priority queue finds the closest vertex quickly. It needs weights that are not negative.',
     'hi': 'Dijkstra का algorithm हर दौर में सबसे पास वाले unsettled vertex को settle करता है और उसके edges को relax करता है, यानी जिस पड़ोसी तक सस्ते में पहुँच सके उसे सुधारता है। Priority queue सबसे पास वाला vertex जल्दी देती है। Weights negative नहीं होने चाहिए।',
     'kn': 'Dijkstra ನ algorithm ಪ್ರತಿ ಸುತ್ತಿನಲ್ಲಿ ಅತಿ ಹತ್ತಿರದ unsettled vertex ಅನ್ನು settle ಮಾಡಿ ಅದರ edges ಅನ್ನು relax ಮಾಡುತ್ತದೆ, ಅಗ್ಗವಾಗಿ ತಲುಪಬಹುದಾದ ನೆರೆಯನ್ನು ಸುಧಾರಿಸುತ್ತದೆ. Priority queue ಅತಿ ಹತ್ತಿರದ vertex ಅನ್ನು ಬೇಗ ಕೊಡುತ್ತದೆ. Weights negative ಆಗಿರಬಾರದು.',
     'or': 'Dijkstra ଙ୍କ algorithm ପ୍ରତ୍ୟେକ ରାଉଣ୍ଡରେ ସବୁଠୁ ପାଖ unsettled vertex କୁ settle କରେ ଓ ତା’ର edges relax କରେ, ଯେଉଁ ପଡ଼ୋଶୀକୁ ଶସ୍ତାରେ ପହଞ୍ଚିହେବ ତାକୁ ଉନ୍ନତ କରେ। Priority queue ସବୁଠୁ ପାଖ vertex ଶୀଘ୍ର ଦିଏ। Weights negative ହେବା ଉଚିତ ନୁହେଁ।',
     'ar': 'خوارزمية ديكسترا تثبت في كل جولة أقرب رأس غير مثبت، ثم ترخي حوافه فتحسن أي جار يمكن الوصول إليه بتكلفة أقل. طابور الأولوية يعطي أقرب رأس بسرعة. ويجب ألا تكون الأوزان سالبة.',
     'de': 'Dijkstras Algorithmus legt in jeder Runde den nächsten offenen Knoten fest und entspannt seine Kanten, er verbessert also jeden Nachbarn, der so günstiger erreichbar ist. Eine Prioritätswarteschlange findet den nächsten Knoten schnell. Die Gewichte dürfen nicht negativ sein.'},
    {'id': 'mst', 'h': 'Minimum spanning trees',
     'en': 'A minimum spanning tree connects every vertex with the smallest total weight. Kruskal\'s algorithm takes the cheapest edges first and skips any edge that would close a cycle. Union find tells it in almost constant time whether two vertices are already connected.',
     'hi': 'Minimum spanning tree हर vertex को सबसे कम कुल weight से जोड़ता है। Kruskal का algorithm सबसे सस्ते edges पहले लेता है और cycle बनाने वाले edge को छोड़ देता है। Union find लगभग स्थिर समय में बताता है कि दो vertices पहले से जुड़े हैं या नहीं।',
     'kn': 'Minimum spanning tree ಪ್ರತಿ vertex ಅನ್ನು ಅತಿ ಕಡಿಮೆ ಒಟ್ಟು weight ನಲ್ಲಿ ಜೋಡಿಸುತ್ತದೆ. Kruskal ನ algorithm ಅಗ್ಗದ edges ಮೊದಲು ತೆಗೆದುಕೊಂಡು cycle ಮಾಡುವ edge ಅನ್ನು ಬಿಡುತ್ತದೆ. ಎರಡು vertices ಈಗಾಗಲೇ ಜೋಡಣೆಯಾಗಿವೆಯೇ ಎಂದು union find ಬಹುತೇಕ ಸ್ಥಿರ ಸಮಯದಲ್ಲಿ ಹೇಳುತ್ತದೆ.',
     'or': 'Minimum spanning tree ପ୍ରତ୍ୟେକ vertex କୁ ସବୁଠୁ କମ୍ ମୋଟ weight ରେ ଯୋଡ଼େ। Kruskal ଙ୍କ algorithm ସବୁଠୁ ଶସ୍ତା edges ପ୍ରଥମେ ନିଏ ଓ cycle କରୁଥିବା edge ଛାଡ଼ିଦିଏ। ଦୁଇ vertices ପୂର୍ବରୁ ଯୋଡ଼ା କି ନାହିଁ union find ପ୍ରାୟ ସ୍ଥିର ସମୟରେ କହେ।',
     'ar': 'شجرة الامتداد الصغرى تربط كل الرؤوس بأقل وزن إجمالي. خوارزمية كروسكال تأخذ الحواف الأرخص أولًا وتتجاوز أي حافة تغلق دورة. وتخبرها بنية الاتحاد والبحث في زمن شبه ثابت هل رأسان متصلان من قبل.',
     'de': 'Ein minimaler Spannbaum verbindet alle Knoten mit dem kleinsten Gesamtgewicht. Kruskals Algorithmus nimmt die billigsten Kanten zuerst und überspringt jede Kante, die einen Zyklus schließen würde. Union Find sagt in fast konstanter Zeit, ob zwei Knoten schon verbunden sind.'},
    {'id': 'grids', 'h': 'Grids',
     'en': 'A grid is a graph where every cell is joined to its four neighbours. To count islands, scan every cell, and whenever you meet unseen land, flood the whole island with a search so it is counted only once.',
     'hi': 'Grid ऐसा graph है जिसमें हर cell अपने चार पड़ोसियों से जुड़ा होता है। Islands गिनने के लिए हर cell देखें, और जब भी अनदेखी ज़मीन मिले, पूरे island को search से भर दें ताकि वह एक ही बार गिना जाए।',
     'kn': 'Grid ಎಂದರೆ ಪ್ರತಿ cell ತನ್ನ ನಾಲ್ಕು ನೆರೆಯವರೊಂದಿಗೆ ಜೋಡಿಸಿದ graph. Islands ಎಣಿಸಲು ಪ್ರತಿ cell ಪರಿಶೀಲಿಸಿ, ನೋಡದ ಭೂಮಿ ಸಿಕ್ಕಾಗಲೆಲ್ಲಾ ಇಡೀ island ಅನ್ನು search ಮೂಲಕ ತುಂಬಿಸಿ, ಆಗ ಅದು ಒಮ್ಮೆ ಮಾತ್ರ ಎಣಿಕೆಯಾಗುತ್ತದೆ.',
     'or': 'Grid ହେଉଛି ଏପରି graph ଯେଉଁଠି ପ୍ରତ୍ୟେକ cell ତା’ର ଚାରି ପଡ଼ୋଶୀ ସହ ଯୋଡ଼ା। Islands ଗଣିବାକୁ ପ୍ରତ୍ୟେକ cell ଦେଖନ୍ତୁ, ଏବଂ ଯେତେବେଳେ ନଦେଖା ଜମି ମିଳେ, ପୂରା island କୁ search ରେ ଭରନ୍ତୁ ଯାହାଦ୍ୱାରା ଏହା ଥରେ ମାତ୍ର ଗଣାହୁଏ।',
     'ar': 'الشبكة رسم بياني تتصل فيه كل خلية بجيرانها الأربعة. لعد الجزر افحص كل خلية، وكلما وجدت أرضًا لم ترها أغرق الجزيرة كلها ببحث حتى لا تعد إلا مرة واحدة.',
     'de': 'Ein Gitter ist ein Graph, in dem jede Zelle mit ihren vier Nachbarn verbunden ist. Um Inseln zu zählen, prüft man jede Zelle, und wann immer man auf ungesehenes Land trifft, flutet man die ganze Insel mit einer Suche, damit sie nur einmal gezählt wird.'},
    {'id': 'practice', 'h': 'Practice',
     'en': 'Time to practise. For each problem, first decide what the vertices and edges are. Then ask whether you need fewest steps, an order, the cheapest route or groups. That tells you whether to reach for BFS, DFS, Dijkstra or union find.',
     'hi': 'अब अभ्यास का समय है। हर सवाल में पहले तय करें कि vertices और edges क्या हैं। फिर पूछें कि आपको सबसे कम कदम, एक क्रम, सबसे सस्ता रास्ता या समूह चाहिए। इससे पता चलता है कि BFS, DFS, Dijkstra या union find में से क्या चुनें।',
     'kn': 'ಈಗ ಅಭ್ಯಾಸದ ಸಮಯ. ಪ್ರತಿ ಸಮಸ್ಯೆಯಲ್ಲಿ ಮೊದಲು vertices ಮತ್ತು edges ಯಾವುವು ಎಂದು ನಿರ್ಧರಿಸಿ. ನಂತರ ಕಡಿಮೆ ಹೆಜ್ಜೆಗಳು, ಒಂದು ಕ್ರಮ, ಅಗ್ಗದ ದಾರಿ ಅಥವಾ ಗುಂಪುಗಳು ಬೇಕೇ ಎಂದು ಕೇಳಿ. ಅದು BFS, DFS, Dijkstra ಅಥವಾ union find ಯಾವುದು ಎಂದು ಹೇಳುತ್ತದೆ.',
     'or': 'ଏବେ ଅଭ୍ୟାସର ସମୟ। ପ୍ରତ୍ୟେକ ସମସ୍ୟାରେ ପ୍ରଥମେ ସ୍ଥିର କରନ୍ତୁ vertices ଓ edges କ’ଣ। ତା’ପରେ ପଚାରନ୍ତୁ ଆପଣଙ୍କୁ ସବୁଠୁ କମ୍ ପାଦ, ଗୋଟିଏ କ୍ରମ, ସବୁଠୁ ଶସ୍ତା ରାସ୍ତା ନା ଗୋଷ୍ଠୀ ଦରକାର। ଏହା କହେ BFS, DFS, Dijkstra ନା union find ବାଛିବେ।',
     'ar': 'حان وقت التدريب. في كل مسألة حدد أولًا ما الرؤوس وما الحواف. ثم اسأل هل تحتاج أقل عدد من الخطوات أم ترتيبًا أم أرخص طريق أم مجموعات. هذا يخبرك هل تختار البحث بالعرض أم بالعمق أم ديكسترا أم الاتحاد والبحث.',
     'de': 'Zeit zum Üben. Lege bei jeder Aufgabe zuerst fest, was die Knoten und Kanten sind. Frag dich dann, ob du die wenigsten Schritte, eine Reihenfolge, den günstigsten Weg oder Gruppen brauchst. Das sagt dir, ob Breitensuche, Tiefensuche, Dijkstra oder Union Find passt.'},
]

PRACTICE = [
    {'id': 'path-exists', 'lv': 'e', 'title': 'Is there a path', 'code': 'p_path_exists',
     'statement': '<p>Given an undirected graph with n vertices and a list of edges, decide whether you can travel from a source vertex to a destination vertex.</p>',
     'example': 'n = 6, edges: 0-1, 0-2, 3-5, 5-4, 4-3\n0 -> 2  true\n0 -> 5  false',
     'hint': 'Start a search at the source and see whether it ever reaches the destination.',
     'approach': '<p>Build an adjacency list and run BFS from the source with a seen array. Return true as soon as the destination comes out of the queue. If the queue empties first, the destination is in another component.</p>',
     'time': 'O(V + E)', 'space': 'O(V + E)'},
    {'id': 'town-judge', 'lv': 'e', 'title': 'Find the town judge', 'code': 'p_town_judge',
     'statement': '<p>In a town of n people, the judge trusts nobody and is trusted by everybody else. Given pairs (a, b) meaning a trusts b, return the judge or −1.</p>',
     'example': 'n = 3, trust: 1→3, 2→3        →  3\nn = 3, trust: 1→3, 2→3, 3→1   →  −1',
     'hint': 'Each trust is a directed edge. Look at how many arrows go into and out of each person.',
     'approach': '<p>Give every person a score of in-degree minus out-degree. Only the judge can reach n − 1, because that needs every other person to trust them and them to trust nobody.</p>',
     'time': 'O(n + E)', 'space': 'O(n)'},
    {'id': 'bipartite', 'lv': 'm', 'title': 'Split into two teams', 'code': 'p_bipartite',
     'statement': '<p>Can the vertices be coloured with two colours so that every edge joins two different colours? Such a graph is called bipartite.</p>',
     'example': 'square 0-1-2-3-0           →  bipartite, colours 0 1 0 1\nsquare plus the diagonal 0-2  →  not bipartite',
     'hint': 'Once one vertex has a colour, every neighbour is forced to take the other colour.',
     'approach': '<p>BFS from every uncoloured vertex. Give each new neighbour the opposite colour. If an already coloured neighbour has the same colour as the current vertex, the graph has an odd cycle and cannot be split.</p>',
     'time': 'O(V + E)', 'space': 'O(V)'},
    {'id': 'rotting-oranges', 'lv': 'm', 'title': 'Rotting oranges', 'code': 'p_rotting',
     'statement': '<p>In a grid, 2 is a rotten orange, 1 is a fresh orange and 0 is empty. Every minute, each rotten orange rots its fresh neighbours up, down, left and right. Return the minutes until no fresh orange is left, or −1 if some can never rot.</p>',
     'example': '[[2,1,1],[1,1,0],[0,1,1]]  →  4\n[[2,1,1],[0,1,1],[1,0,1]]  →  −1',
     'hint': 'All rotten oranges spread at the same time. Start the search from all of them at once.',
     'approach': '<p>Multi source BFS. Put every rotten orange in the queue with time 0. Each fresh neighbour becomes rotten with time + 1. Count fresh oranges, and if any remain at the end, return −1.</p>',
     'time': 'O(rows × cols)', 'space': 'O(rows × cols)'},
    {'id': 'word-ladder', 'lv': 'h', 'title': 'Word ladder', 'code': 'p_word_ladder',
     'statement': '<p>Change one letter at a time to turn a start word into an end word. Every word along the way must be in the word list. Return the shortest ladder.</p>',
     'example': 'hit → cog, words: hot dot dog lot log cog\nOutput: length 5 : hit hot dot dog cog',
     'hint': 'Words are vertices. Two words share an edge when they differ in exactly one letter.',
     'approach': '<p>BFS from the start word. The neighbours of a word are the unseen words in the list that differ from it in exactly one letter. Store each parent, and when the end word comes out of the queue, walk the parents back. For very large lists, generating all one letter changes and looking them up in a hash set is faster.</p>',
     'time': 'O(N² · L)', 'space': 'O(N · L)'},
    {'id': 'redundant-connection', 'lv': 'h', 'title': 'The edge that makes a cycle', 'code': 'p_redundant',
     'statement': '<p>A tree had one extra edge added to it. Given the edges in order, return the first edge that creates a cycle.</p>',
     'example': '[(1,2), (1,3), (2,3)]                 →  (2, 3)\n[(1,2), (2,3), (3,4), (1,4), (1,5)]   →  (1, 4)',
     'hint': 'An edge closes a cycle exactly when its two ends are already connected.',
     'approach': '<p>Union find. For each edge, find the leaders of both ends. If they match, this edge is the redundant one. Otherwise union the two groups and continue.</p>',
     'time': 'O(E · α(V)), almost O(E)', 'space': 'O(V)'},
    {'id': 'cheapest-flights', 'lv': 'x', 'title': 'Cheapest flight with at most k stops', 'code': 'p_cheapest_flights',
     'statement': '<p>Flights are directed edges with prices. Find the cheapest price from src to dst using at most k stops in between, or −1.</p>',
     'example': 'flights: 0→1 100, 1→2 100, 2→0 100, 1→3 600, 2→3 200\nk = 0  →  −1    k = 1  →  700    k = 2  →  400',
     'hint': 'Plain Dijkstra ignores the stop limit. Count flights instead: k stops means at most k + 1 flights.',
     'approach': '<p>Bellman-Ford limited to k + 1 rounds. Each round relaxes every flight, reading costs from the previous round and writing to a copy, so a single round never chains two flights.</p>',
     'time': 'O(k · E)', 'space': 'O(V)'},
    {'id': 'bridges', 'lv': 'x', 'title': 'Critical connections', 'code': 'p_bridges',
     'statement': '<p>A bridge is an edge whose removal splits the network into two parts. List all bridges of a connected undirected graph.</p>',
     'example': 'edges: 0-1, 1-2, 2-0, 1-3                         →  1-3\nedges: two triangles joined by 1-3, plus 5-6   →  5-6 1-3',
     'hint': 'During DFS, record when each vertex is discovered and the earliest vertex its subtree can reach with one back edge.',
     'approach': '<p>Tarjan\'s algorithm. low[v] is the smallest discovery time reachable from v\'s subtree. After exploring a child w, if low[w] is greater than disc[v], nothing below w climbs back above v, so v-w is a bridge.</p>',
     'time': 'O(V + E)', 'space': 'O(V + E)'},
]

QUIZ = [
    {'lv': 'e', 'q': 'What are the two parts of a graph?', 'o': ['Roots and leaves', 'Vertices and edges', 'Keys and values', 'Rows and columns'], 'a': 1, 'hint': 'Dots and the lines between them.', 'why': 'Vertices are the things, and edges are the links between them.'},
    {'lv': 'e', 'q': '"A follows B" on a social app is best modelled as which kind of edge?', 'o': ['Undirected', 'Directed', 'Weighted only', 'A loop'], 'a': 1, 'hint': 'B does not have to follow A back.', 'why': 'The link goes one way, so it is a directed edge from A to B.'},
    {'lv': 'e', 'q': 'Which structure does breadth first search use?', 'o': ['Stack', 'Queue', 'Hash map only', 'Binary search tree'], 'a': 1, 'hint': 'Vertices found first are explored first.', 'why': 'First in, first out keeps the rings in order.'},
    {'lv': 'e', 'q': 'An undirected graph has 4 edges. What is the sum of all degrees?', 'o': ['4', '6', '8', '16'], 'a': 2, 'hint': 'Each edge touches two vertices.', 'why': '<span class="eq">sum of degrees = 2E = 2 × 4 = 8</span>'},
    {'lv': 'm', 'q': 'How much memory does an adjacency list use?', 'o': ['O(V)', 'O(E)', 'O(V + E)', 'O(V²)'], 'a': 2, 'hint': 'One list per vertex, one entry per edge end.', 'why': 'There are V lists and 2E entries for an undirected graph, so O(V + E).'},
    {'lv': 'm', 'q': 'In a graph without weights, which search finds the path with the fewest edges?', 'o': ['DFS', 'BFS', 'Both always', 'Neither'], 'a': 1, 'hint': 'Think rings around the start.', 'why': 'BFS reaches every vertex at distance d before any vertex at distance d + 1.'},
    {'lv': 'm', 'q': 'What does Kahn\'s algorithm need to find a topological order?', 'o': ['A weighted graph', 'A directed graph with no cycles', 'An undirected tree', 'A complete graph'], 'a': 1, 'hint': 'Arrows must all be able to point forwards.', 'why': 'With a cycle, no vertex in it ever reaches in-degree 0.'},
    {'lv': 'm', 'q': 'How many edges does a spanning tree of a connected graph with 10 vertices have?', 'o': ['9', '10', '11', '45'], 'a': 0, 'hint': 'It is a tree.', 'why': '<span class="eq">V − 1 = 10 − 1 = 9</span>'},
    {'lv': 'h', 'q': 'Why can Dijkstra give wrong answers with negative edge weights?', 'o': ['It runs forever', 'A settled vertex might later be reached more cheaply', 'It cannot store negative numbers', 'The heap breaks'], 'a': 1, 'hint': 'Dijkstra never revisits a settled vertex.', 'why': 'It assumes longer paths can only get longer, which a negative edge breaks.'},
    {'lv': 'h', 'q': 'What is the running time of Dijkstra with a binary heap?', 'o': ['O(V + E)', 'O((V + E) log V)', 'O(V · E)', 'O(V³)'], 'a': 1, 'hint': 'Each edge may push into the heap.', 'why': 'Up to E pushes and pops, each O(log V), plus V vertices.'},
    {'lv': 'h', 'q': 'How many edges can a simple undirected graph with 6 vertices have at most?', 'o': ['12', '15', '30', '36'], 'a': 1, 'hint': 'Every pair of vertices at most once.', 'why': '<span class="eq">6 × 5 / 2 = 15</span>'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'adj = {0: [1, 2], 1: [3], 2: [3], 3: []}\nseen, order = set(), []\ndef dfs(v):\n    seen.add(v)\n    order.append(v)\n    for w in adj[v]:\n        if w not in seen:\n            dfs(w)\ndfs(0)\nprint(order)', 'o': ['[0, 1, 2, 3]', '[0, 1, 3, 2]', '[0, 2, 3, 1]', '[3, 1, 2, 0]'], 'a': 1, 'hint': 'DFS goes as deep as it can before trying 2.', 'why': 'From 0 it goes to 1, then 3, backs up to 0, and only then visits 2.'},
    {'lv': 'x', 'q': 'Kruskal\'s algorithm considers an edge whose two ends already have the same union find leader. What happens?', 'o': ['It is added', 'It is skipped because it would close a cycle', 'The algorithm restarts', 'The leaders swap'], 'a': 1, 'hint': 'Same leader means already connected.', 'why': 'Adding an edge inside one group always creates a cycle, which a tree cannot have.'},
    {'lv': 'x', 'q': 'An adjacency matrix for 100,000 vertices stores one byte per cell. Roughly how much memory is that?', 'o': ['100 KB', '10 MB', '10 GB', '1 TB'], 'a': 2, 'hint': 'Square the number of vertices.', 'why': '<span class="eq">100,000² = 10¹⁰ bytes ≈ 10 GB</span> An adjacency list for a sparse graph is far smaller.'},
    {'lv': 'x', 'q': 'Which algorithm finds shortest paths when some edge weights are negative but there is no negative cycle?', 'o': ['BFS', 'Dijkstra', 'Bellman-Ford', 'Kruskal'], 'a': 2, 'hint': 'It relaxes every edge again and again.', 'why': 'Bellman-Ford relaxes all edges V − 1 times, which handles negative edges in O(V · E).'},
    {'lv': 'x', 'q': 'In Tarjan\'s bridge algorithm, edge v-w (w a child of v in the DFS) is a bridge exactly when…', 'o': ['low[w] > disc[v]', 'low[w] < disc[v]', 'disc[w] = disc[v]', 'w is a leaf'], 'a': 0, 'hint': 'Can anything below w reach v or higher without this edge?', 'why': 'If even the earliest vertex reachable from w\'s subtree comes after v, removing v-w cuts that subtree off.'},
]

CALC = [
    {'lv': 'e', 'q': 'A road network has 7 towns and 9 two way roads. What is the sum of the degrees of all towns?', 'ans': '18', 'hint': 'sum of degrees = 2E', 'steps': ['<span class="eq">2 × 9 = 18</span>']},
    {'lv': 'e', 'q': 'How many entries does an adjacency matrix for 12 vertices have?', 'ans': '144', 'hint': 'It is a V by V grid.', 'steps': ['<span class="eq">12 × 12 = 144</span>']},
    {'lv': 'm', 'q': 'In the BFS lesson graph (edges 0-1, 0-2, 1-3, 2-4, 3-5, 4-5, 5-6), what is the distance from 0 to 6?', 'ans': '4', 'hint': 'Count rings: which vertices are 1 away, 2 away, and so on.', 'steps': ['1 away: 1, 2', '2 away: 3, 4', '3 away: 5', '4 away: 6, so the distance is <span class="eq">4</span>']},
    {'lv': 'm', 'q': 'What is the largest number of edges in a simple undirected graph with 8 vertices?', 'ans': '28', 'hint': 'E ≤ V(V − 1) / 2', 'steps': ['<span class="eq">8 × 7 / 2 = 28</span>']},
    {'lv': 'h', 'q': 'Roads: A-B 4, A-C 2, B-C 1, B-D 5, C-D 8. What is the shortest distance from A to D?', 'ans': '8', 'hint': 'Going straight to B is not the cheapest way to B.', 'steps': ['A to C costs 2, then C to B costs 1, so B is at <span class="eq">2 + 1 = 3</span>', 'B to D adds 5: <span class="eq">3 + 5 = 8</span>', 'C to D directly would be <span class="eq">2 + 8 = 10</span>, which is worse.']},
    {'lv': 'h', 'q': 'A directed graph has these in-degrees: A 0, B 1, C 2, D 0, E 1. How many vertices are ready at the very start of Kahn\'s algorithm?', 'ans': '2', 'hint': 'Ready means in-degree 0.', 'steps': ['A and D have in-degree 0.', 'So <span class="eq">2</span> vertices are ready.']},
    {'lv': 'x', 'q': 'What is the total weight of the minimum spanning tree for A-B 4, A-C 2, B-C 1, B-D 5, C-D 8, C-E 10, D-E 2, D-F 6, E-F 2?', 'ans': '12', 'hint': 'Sort by weight and skip edges that close a cycle.', 'steps': ['Take B-C 1, A-C 2, D-E 2, E-F 2.', 'Skip A-B 4, because A and B are already joined through C.', 'Take B-D 5 to join the two groups.', '<span class="eq">1 + 2 + 2 + 2 + 5 = 12</span>']},
    {'lv': 'x', 'q': 'A grid has 300 rows and 400 columns. About how many neighbour checks does a full flood fill make in the worst case?', 'ans': '480000', 'alt': ['480,000', '4.8e5'], 'hint': 'Every cell checks its 4 neighbours once.', 'steps': ['<span class="eq">300 × 400 = 120,000</span> cells', '<span class="eq">120,000 × 4 = 480,000</span> checks']},
]

VIZ_JS = r'''
(() => {
  const { esc, $, shell, seg, wireSeg, Player, cell } = VIZ.kit;
  const W = VIZ.widgets;
  const plates = (a, hl = {}) => `<div class="vz-stack">${a.map((v, k) => `<div class="vz-plate ${hl[k] || ''}">${esc(v)}${k === a.length - 1 ? '<small>top</small>' : ''}</div>`).join('')}</div>`;

  /* draw a graph. G = { nodes: [{x, y, t}], edges: [[a, b, w]], dir, w, h, box }
     ncls(i) is a vertex class, ecls(k) an edge class, opt.sub(i) a small label under a vertex */
  function svgGraph(G, ncls = () => '', ecls = () => '', opt = {}) {
    const R = 20, bw = G.box || 0, bh = 30;
    const reach = (ux, uy) => bw ? Math.min(bw / 2 / Math.max(Math.abs(ux), 1e-6), bh / 2 / Math.max(Math.abs(uy), 1e-6)) : R;
    let es = '', ws = '', ns = '';
    G.edges.forEach((e, k) => {
      const [a, b, w] = e, A = G.nodes[a], B = G.nodes[b], c = ecls(k, e);
      const dx = B.x - A.x, dy = B.y - A.y, len = Math.hypot(dx, dy), ux = dx / len, uy = dy / len;
      const r = reach(ux, uy), tip = G.dir ? 9 : 0;
      const x1 = A.x + ux * r, y1 = A.y + uy * r, x2 = B.x - ux * (r + tip), y2 = B.y - uy * (r + tip);
      es += `<line class="vz-edge ${c}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`;
      if (G.dir) {
        const tx = B.x - ux * r, ty = B.y - uy * r, px = -uy * 5.5, py = ux * 5.5;
        es += `<polygon class="vz-ah ${c}" points="${tx},${ty} ${x2 + px},${y2 + py} ${x2 - px},${y2 - py}"/>`;
      }
      if (w !== undefined) {
        const mx = (A.x + B.x) / 2, my = (A.y + B.y) / 2;
        ws += `<g class="vz-wt ${c}"><rect x="${mx - 13}" y="${my - 11}" width="26" height="22" rx="6"/><text x="${mx}" y="${my + 4.5}">${esc(w)}</text></g>`;
      }
    });
    G.nodes.forEach((n, i) => {
      const shape = bw ? `<rect x="${n.x - bw / 2}" y="${n.y - bh / 2}" width="${bw}" height="${bh}" rx="10"/>` : `<circle cx="${n.x}" cy="${n.y}" r="${R}"/>`;
      const sub = opt.sub ? opt.sub(i) : '';
      const ly = n.y + (bw ? bh / 2 : R) + 15, sw = String(sub).length * 7 + 12;
      const tag = sub !== '' ? `<g class="vz-sb"><rect class="vz-pill" x="${n.x - sw / 2}" y="${ly - 11}" width="${sw}" height="15" rx="7"/><text class="vz-ret" x="${n.x}" y="${ly}">${esc(sub)}</text></g>` : '';
      ns += `<g class="vz-tn ${ncls(i)}">${shape}<text x="${n.x}" y="${n.y + 4.5}">${esc(n.t)}</text>${tag}</g>`;
    });
    return `<div class="vz-scroll"><svg class="vz-svg" viewBox="0 0 ${G.w} ${G.h}" style="min-width:${Math.min(G.w, 420)}px; max-width:${G.w}px; margin:0 auto" role="img" aria-label="Graph diagram">${es}${ws}${ns}</svg></div>`;
  }

  /* ======================= BFS versus DFS ======================= */
  W.search = el => {
    const b = shell(el, 'Breadth first versus depth first', 'Both searches start at 0 on the same graph. Yellow is the vertex being explored, blue vertices are waiting, green are finished. Highlighted edges show how each vertex was first reached.');
    b.innerHTML = `<div class="vz-row">${seg('m', [['bfs', '🌊 BFS with a queue'], ['dfs', '🧗 DFS with recursion']], 'bfs')}</div>
      <div class="vz-two"><div><h4 class="vz-fh">Queue</h4><div class="vz-aux"></div></div><div><div class="vz-tree vz-g"></div></div></div>
      <h4>Visit order</h4><div class="vz-scroll"><div class="vz-cells vz-big vz-out"></div></div>
      <div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const G = { w: 560, h: 290, nodes: [[60, 145], [170, 60], [170, 230], [290, 40], [300, 145], [290, 250], [420, 100], [500, 220]].map(([x, y], i) => ({ x, y, t: i })),
      edges: [[0, 1], [0, 2], [1, 3], [1, 4], [2, 4], [2, 5], [3, 6], [4, 6], [5, 7], [6, 7]] };
    const adj = G.nodes.map(() => []);
    G.edges.forEach(([a, c], k) => { adj[a].push([c, k]); adj[c].push([a, k]); });
    let mode = 'bfs', steps = [];
    const P = Player($('.vz-p', b), show, 950);
    function build() {
      steps = [];
      const seen = new Set([0]), tree = new Set(), done = [], dist = { 0: 0 };
      if (mode === 'bfs') {
        const q = [0];
        steps.push({ cur: -1, wait: [0], done: [], tree: [], dist: { ...dist }, msg: 'Mark 0 as seen and put it in the queue.' });
        while (q.length) {
          const v = q.shift(), fresh = [];
          for (const [w, k] of adj[v]) if (!seen.has(w)) { seen.add(w); tree.add(k); q.push(w); fresh.push(w); dist[w] = dist[v] + 1; }
          done.push(v);
          steps.push({ cur: v, wait: q.slice(), done: done.slice(), tree: [...tree], dist: { ...dist }, msg: `Take ${v} from the front (distance ${dist[v]}). ${fresh.length ? `New neighbours ${fresh.join(', ')} are marked seen and join the back at distance ${dist[v] + 1}.` : 'All its neighbours were already seen.'}` });
        }
      } else {
        const stack = [];
        const go = v => {
          seen.add(v); stack.push(v); done.push(v);
          steps.push({ cur: v, wait: stack.slice(), done: done.slice(), tree: [...tree], msg: `Visit ${v}.` });
          for (const [w, k] of adj[v]) {
            if (!seen.has(w)) {
              tree.add(k);
              go(w);
              steps.push({ cur: v, wait: stack.slice(), done: done.slice(), tree: [...tree], msg: `Back at ${v}. Look for another unseen neighbour.` });
            }
          }
          stack.pop();
          const up = stack[stack.length - 1];
          steps.push({ cur: up === undefined ? -1 : up, wait: stack.slice(), done: done.slice(), tree: [...tree], fin: v, msg: `Every neighbour of ${v} is seen, so ${v} returns${up === undefined ? ' and the search is over' : ` to ${up}`}.` });
        };
        steps.push({ cur: -1, wait: [], done: [], tree: [], msg: 'Call dfs(0).' });
        go(0);
        steps[steps.length - 1].msg += ` Order: <b>${done.join(' ')}</b>`;
        // drop the "back at" step that repeats right before a return
        steps = steps.filter((s, i) => !(s.msg.startsWith('Back at') && steps[i + 1] && steps[i + 1].fin === s.cur));
      }
      if (mode === 'bfs') steps[steps.length - 1].msg += ` The queue is empty. Order: <b>${done.join(' ')}</b>`;
      $('.vz-fh', b).textContent = mode === 'bfs' ? 'Queue (front on the left)' : 'Call stack';
      P.load(steps.length);
    }
    function show(k) {
      const s = steps[k], tree = new Set(s.tree);
      const finished = new Set(mode === 'bfs' ? s.done : s.done.filter(v => !s.wait.includes(v)));
      $('.vz-g', b).innerHTML = svgGraph(G, i => i === s.cur ? 'hl' : finished.has(i) ? 'ok' : s.wait.includes(i) ? 'mv' : '', e => tree.has(e) ? 'on' : '', { sub: mode === 'bfs' ? i => s.dist[i] !== undefined ? `d=${s.dist[i]}` : '' : undefined });
      $('.vz-out', b).innerHTML = s.done.map((v, i) => cell(v, v === s.cur ? 'hl' : 'ok', i + 1)).join('') || '<span class="vz-note">nothing visited yet</span>';
      $('.vz-aux', b).innerHTML = mode === 'bfs'
        ? `<div class="vz-cells vz-big">${s.wait.map(v => cell(v, 'sel')).join('') || '<span class="vz-note">empty</span>'}</div>`
        : plates(s.wait.map(v => `dfs(${v})`));
      $('.vz-msg', b).innerHTML = s.msg;
    }
    wireSeg(b, 'm', v => { mode = v; build(); });
    build();
  };

  /* ======================= Kahn's topological order ======================= */
  W.topo = el => {
    const b = shell(el, "Kahn's algorithm gets you dressed", 'Arrows point from what must come first. The number under each item is how many arrows still point into it. Items at 0 are ready.');
    b.innerHTML = `<div class="vz-tree vz-g"></div><div class="vz-two"><div><h4>Ready queue</h4><div class="vz-scroll"><div class="vz-cells vz-q"></div></div></div><div><h4>Order so far</h4><div class="vz-scroll"><div class="vz-cells vz-out"></div></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const names = ['underwear', 'pants', 'shirt', 'belt', 'tie', 'jacket', 'socks', 'shoes'];
    const pos = [[70, 45], [240, 45], [70, 155], [410, 110], [240, 200], [580, 155], [70, 265], [410, 265]];
    const G = { w: 650, h: 300, box: 96, dir: true, nodes: pos.map(([x, y], i) => ({ x, y, t: names[i] })),
      edges: [[0, 1], [1, 7], [1, 3], [2, 3], [2, 4], [4, 5], [3, 5], [6, 7]] };
    const steps = [], indeg = names.map(() => 0);
    G.edges.forEach(([, t]) => indeg[t]++);
    const q = [], order = [], used = new Set();
    names.forEach((_, v) => { if (!indeg[v]) q.push(v); });
    steps.push({ cur: -1, deg: indeg.slice(), q: q.slice(), order: [], used: [], msg: `Count the arrows into each item. ${q.map(v => names[v]).join(', ')} have none, so they start in the queue.` });
    while (q.length) {
      const v = q.shift(), freed = [];
      order.push(v);
      G.edges.forEach(([a, t], k) => { if (a === v) { used.add(k); if (--indeg[t] === 0) { q.push(t); freed.push(names[t]); } } });
      steps.push({ cur: v, deg: indeg.slice(), q: q.slice(), order: order.slice(), used: [...used], msg: `Put on <b>${names[v]}</b> and remove its arrows.${freed.length ? ` ${freed.join(' and ')} ${freed.length > 1 ? 'are' : 'is'} now ready.` : ''}` });
    }
    steps.push({ cur: -1, deg: indeg.slice(), q: [], order: order.slice(), used: [...used], msg: `All ${names.length} items are placed and every arrow points forwards. No cycle.` });
    const P = Player($('.vz-p', b), show, 1000);
    function show(k) {
      const s = steps[k], used = new Set(s.used), placed = new Set(s.order);
      $('.vz-g', b).innerHTML = svgGraph(G, i => i === s.cur ? 'hl' : placed.has(i) ? 'ok' : s.q.includes(i) ? 'mv' : '', e => used.has(e) ? 'gone' : '', { sub: i => placed.has(i) ? '' : `in ${s.deg[i]}` });
      $('.vz-q', b).innerHTML = s.q.map(v => cell(names[v], 'sel')).join('') || '<span class="vz-note">empty</span>';
      $('.vz-out', b).innerHTML = s.order.map((v, i) => cell(names[v], v === s.cur ? 'hl' : 'ok', i + 1)).join('') || '<span class="vz-note">nothing yet</span>';
      $('.vz-msg', b).innerHTML = s.msg;
    }
    P.load(steps.length);
  };

  /* ======================= Dijkstra step by step ======================= */
  W.dijk = el => {
    const b = shell(el, "Dijkstra's algorithm from A", 'Each round settles the closest unsettled town, then relaxes its roads. The number under each town is its best distance so far.');
    b.innerHTML = `<div class="vz-tree vz-g"></div><h4>Priority queue (smallest first)</h4><div class="vz-scroll"><div class="vz-cells vz-pq"></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const names = 'ABCDEF';
    const G = { w: 580, h: 300, nodes: [[60, 150], [200, 60], [200, 240], [380, 60], [380, 240], [520, 150]].map(([x, y], i) => ({ x, y, t: names[i] })),
      edges: [[0, 1, 4], [0, 2, 2], [1, 2, 1], [1, 3, 5], [2, 3, 8], [2, 4, 10], [3, 4, 2], [3, 5, 6], [4, 5, 2]] };
    const n = names.length, dist = Array(n).fill(Infinity), prev = Array(n).fill(-1), via = Array(n).fill(-1), done = new Set();
    const fmt = d => d === Infinity ? '∞' : d;
    const steps = [];
    let pq = [[0, 0]];
    dist[0] = 0;
    const snap = (cur, edge, msg) => steps.push({ cur, edge, dist: dist.slice(), via: via.slice(), done: [...done], pq: pq.slice(), msg });
    snap(-1, -1, 'Start: A is at distance 0, every other town at ∞. A goes into the priority queue.');
    while (pq.length) {
      pq.sort((x, y) => x[0] - y[0] || x[1] - y[1]);
      const [d, v] = pq.shift();
      if (done.has(v)) { snap(v, -1, `Pop ${names[v]} at ${d}, but ${names[v]} is already settled with ${dist[v]}. Skip this old entry.`); continue; }
      done.add(v);
      snap(v, -1, `Pop the smallest entry: ${names[v]} at ${d}. ${names[v]} is now <b>settled</b>, no shorter way can exist.`);
      G.edges.forEach(([a, c, w], k) => {
        if (a !== v && c !== v) return;
        const u = a === v ? c : a;
        if (done.has(u)) return;
        if (d + w < dist[u]) {
          const old = dist[u];
          dist[u] = d + w; prev[u] = v; via[u] = k; pq.push([dist[u], u]);
          snap(v, k, `Road ${names[v]}${names[u]} costs ${w}: ${d} + ${w} = ${d + w} &lt; ${fmt(old)}, so ${names[u]} improves to <b>${d + w}</b>.`);
        } else {
          snap(v, k, `Road ${names[v]}${names[u]} costs ${w}: ${d} + ${w} = ${d + w}, not better than ${dist[u]}. No change.`);
        }
      });
    }
    snap(-1, -1, 'The queue is empty. Every distance is final, and the green roads form the shortest path tree from A.');
    const P = Player($('.vz-p', b), show, 1100);
    function show(k) {
      const s = steps[k], tree = new Set(s.via.filter(x => x >= 0)), done = new Set(s.done);
      $('.vz-g', b).innerHTML = svgGraph(G, i => i === s.cur ? 'hl' : done.has(i) ? 'ok' : s.dist[i] < Infinity ? 'mv' : '', e => e === s.edge ? 'on' : tree.has(e) ? 'tree' : '', { sub: i => fmt(s.dist[i]) });
      $('.vz-pq', b).innerHTML = s.pq.slice().sort((x, y) => x[0] - y[0] || x[1] - y[1]).map(([d, v]) => cell(`${names[v]} ${d}`, 'sel')).join('') || '<span class="vz-note">empty</span>';
      $('.vz-msg', b).innerHTML = s.msg;
    }
    P.load(steps.length);
  };

  /* ======================= islands on a grid ======================= */
  W.grid = el => {
    const b = shell(el, 'Counting islands with a flood fill', 'Orange cells are land. Click any cell to switch it between land and water, then press Play. Each island gets its own colour.');
    b.innerHTML = `<div class="vz-gg"></div><div class="vz-note vz-cnt2"></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const R = 6, Cn = 9;
    const start = ['110000110', '110100100', '000100000', '011000011', '001000010', '000011000'];
    let land = start.map(r => [...r].map(ch => ch === '1'));
    let steps = [];
    const P = Player($('.vz-p', b), show, 420);
    const gg = $('.vz-gg', b);
    gg.style.gridTemplateColumns = `repeat(${Cn}, 34px)`;
    function build() {
      steps = [];
      const lab = land.map(r => r.map(() => -1));
      const snap = (cur, msg, count) => steps.push({ cur, lab: lab.map(r => r.slice()), msg, count });
      let count = 0;
      snap(null, 'Scan the grid row by row, looking for land that is not in any island yet.', 0);
      for (let r = 0; r < R; r++) for (let c = 0; c < Cn; c++) {
        if (!land[r][c] || lab[r][c] >= 0) continue;
        const id = count++;
        lab[r][c] = id;
        const queue = [[r, c]];
        snap([r, c], `Unseen land at row ${r}, column ${c}. Island <b>${id + 1}</b> starts here. Flood it with BFS.`, count);
        for (let h = 0; h < queue.length; h++) {
          const [y, x] = queue[h];
          for (const [dy, dx] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
            const ny = y + dy, nx = x + dx;
            if (ny >= 0 && ny < R && nx >= 0 && nx < Cn && land[ny][nx] && lab[ny][nx] < 0) {
              lab[ny][nx] = id; queue.push([ny, nx]);
              snap([ny, nx], `Land next to (${y}, ${x}) joins island ${id + 1}.`, count);
            }
          }
        }
      }
      snap(null, `Scan finished. The grid has <b>${count}</b> island${count === 1 ? '' : 's'}. Each cell was handled once.`, count);
      P.load(steps.length);
    }
    function show(k) {
      const s = steps[k];
      gg.innerHTML = land.map((row, r) => row.map((isLand, c) => {
        const id = s.lab[r][c];
        const cls = id >= 0 ? `i${id % 6}` : isLand ? 'land' : '';
        const cur = s.cur && s.cur[0] === r && s.cur[1] === c ? ' cur' : '';
        return `<button type="button" class="vz-gc ${cls}${cur}" data-r="${r}" data-c="${c}" aria-label="Row ${r}, column ${c}, ${isLand ? 'land' : 'water'}">${id >= 0 ? id + 1 : ''}</button>`;
      }).join('')).join('');
      $('.vz-cnt2', b).innerHTML = `Islands found: <b>${s.count}</b>`;
      $('.vz-msg', b).innerHTML = s.msg;
    }
    gg.addEventListener('click', e => {
      const t = e.target.closest('.vz-gc');
      if (!t) return;
      const r = +t.dataset.r, c = +t.dataset.c;
      land[r][c] = !land[r][c];
      build();
    });
    build();
  };
})();
'''

CSS = r'''
.vz-aux .vz-stack{margin:0}
.vz-tn .vz-sb rect.vz-pill{fill:var(--surface); stroke:none; opacity:.92}
.vz-ah{fill:var(--box-line)}
.vz-ah.on{fill:var(--accent)}
.vz-ah.gone,.vz-edge.gone{opacity:.15}
.vz-edge.tree{stroke:var(--ok-line); stroke-width:3.2}
.vz-wt rect{fill:var(--surface); stroke:var(--line); stroke-width:1.2}
.vz-wt text{font:700 12px var(--font-mono); fill:var(--ink); text-anchor:middle}
.vz-wt.on rect{stroke:var(--accent); stroke-width:2}
.vz-wt.tree rect{stroke:var(--ok-line)}
.vz-tn rect + text{font-size:12px}
.vz-q .vz-cell,.vz-out .vz-cell{padding:0 8px}
.vz-gg{display:grid; gap:4px; justify-content:center; margin:8px 0}
.vz-gc{width:34px; height:34px; border-radius:7px; border:1.5px solid var(--box-line); background:var(--box); color:var(--box-ink); font:700 12px var(--font-mono); cursor:pointer; padding:0; transition:background .2s, border-color .2s}
.vz-gc.land{background:var(--piv); border-color:var(--piv-line)}
.vz-gc.i0{background:var(--ok); border-color:var(--ok-line)}
.vz-gc.i1{background:var(--sel); border-color:var(--sel-line)}
.vz-gc.i2{background:var(--win); border-color:var(--win-line)}
.vz-gc.i3{background:var(--mv); border-color:var(--mv-line)}
.vz-gc.i4{background:var(--hl); border-color:var(--hl-line)}
.vz-gc.i5{background:var(--bad); border-color:var(--bad-line)}
.vz-gc.cur{outline:3px solid var(--accent); outline-offset:1px}
.vz-cnt2{text-align:center}
'''

T = {
    'slug': 'graphs', 'title': 'Graphs', 'short': 'Graphs', 'emoji': '🕸️', 'topic': 'graphs', 'prefix': 'dsag',
    'module': ('🌳', 'Trees and graphs'),
    'lead': 'Graphs model anything made of things and links: roads, friendships, networks and plans. This page shows how to store a graph, explore it with breadth first and depth first search, put tasks in a valid order, find the cheapest routes with Dijkstra, connect everything with a minimum spanning tree, and treat grids as graphs.',
    'desc': 'Graphs in DSA: adjacency lists and matrices, BFS and DFS, connected components, topological sort, Dijkstra shortest paths, Kruskal minimum spanning trees with union find, and grid flood fill, with code in Python, JavaScript and Java.',
    'minutes': 16,
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'practice': PRACTICE, 'quiz': QUIZ, 'calc': CALC,
    'viz': VIZ_JS, 'css': CSS,
    'prev': ('trees', 'trees', '🌲 Trees'),
    'next': None,
}
