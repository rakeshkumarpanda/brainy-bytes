# Chapter 3: vectors, adding and scaling, norms and distances, the dot product, cosine similarity,
# projection, and span, independence and basis.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz, vec, mat, deep

K = Kit()

# ---------------------------------------------------------------- programs
K.code('vec_ops', py=r'''
a = [3, 1]
b = [1, 2]
add = [a[i] + b[i] for i in range(len(a))]     # tip to tail
sub = [a[i] - b[i] for i in range(len(a))]
scaled = [2 * v for v in a]                    # stretch by 2
combo = [2 * a[i] - 3 * b[i] for i in range(len(a))]
print("a + b  =", add)
print("a - b  =", sub)
print("2a     =", scaled)
print("2a - 3b =", combo)
''', js=r'''
const a = [3, 1];
const b = [1, 2];
const add = a.map((v, i) => v + b[i]);         // tip to tail
const sub = a.map((v, i) => v - b[i]);
const scaled = a.map(v => 2 * v);              // stretch by 2
const combo = a.map((v, i) => 2 * v - 3 * b[i]);
const show = v => "[" + v.join(", ") + "]";
console.log("a + b  =", show(add));
console.log("a - b  =", show(sub));
console.log("2a     =", show(scaled));
console.log("2a - 3b =", show(combo));
''', ts=r'''
const a: number[] = [3, 1];
const b: number[] = [1, 2];
const add: number[] = a.map((v, i) => v + b[i]);   // tip to tail
const sub: number[] = a.map((v, i) => v - b[i]);
const scaled: number[] = a.map(v => 2 * v);        // stretch by 2
const combo: number[] = a.map((v, i) => 2 * v - 3 * b[i]);
const show = (v: number[]): string => "[" + v.join(", ") + "]";
console.log("a + b  =", show(add));
console.log("a - b  =", show(sub));
console.log("2a     =", show(scaled));
console.log("2a - 3b =", show(combo));
''', java=r'''
import java.util.Arrays;

public class VecOps {
    public static void main(String[] args) {
        int[] a = {3, 1};
        int[] b = {1, 2};
        int[] add = new int[2], sub = new int[2], scaled = new int[2], combo = new int[2];
        for (int i = 0; i < a.length; i++) {
            add[i] = a[i] + b[i];           // tip to tail
            sub[i] = a[i] - b[i];
            scaled[i] = 2 * a[i];           // stretch by 2
            combo[i] = 2 * a[i] - 3 * b[i];
        }
        System.out.println("a + b  = " + Arrays.toString(add));
        System.out.println("a - b  = " + Arrays.toString(sub));
        System.out.println("2a     = " + Arrays.toString(scaled));
        System.out.println("2a - 3b = " + Arrays.toString(combo));
    }
}
''')

K.code('norms', py=r'''
v = [3, -4]
l2 = (v[0] ** 2 + v[1] ** 2) ** 0.5     # straight line length
l1 = abs(v[0]) + abs(v[1])              # city block length
linf = max(abs(v[0]), abs(v[1]))        # biggest single step
print(f"L2 = {l2:.2f}, L1 = {l1:.2f}, Linf = {linf:.2f}")
unit = [x / l2 for x in v]
print(f"unit vector = [{unit[0]:.2f}, {unit[1]:.2f}], its length = {(unit[0] ** 2 + unit[1] ** 2) ** 0.5:.2f}")
p, q = [1, 2], [4, 6]
d = ((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2) ** 0.5
print(f"distance from p to q = {d:.2f}")
''', js=r'''
const v = [3, -4];
const l2 = Math.sqrt(v[0] ** 2 + v[1] ** 2);       // straight line length
const l1 = Math.abs(v[0]) + Math.abs(v[1]);        // city block length
const linf = Math.max(Math.abs(v[0]), Math.abs(v[1]));  // biggest single step
console.log(`L2 = ${l2.toFixed(2)}, L1 = ${l1.toFixed(2)}, Linf = ${linf.toFixed(2)}`);
const unit = v.map(x => x / l2);
console.log(`unit vector = [${unit[0].toFixed(2)}, ${unit[1].toFixed(2)}], its length = ${Math.hypot(...unit).toFixed(2)}`);
const p = [1, 2], q = [4, 6];
const d = Math.sqrt((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2);
console.log(`distance from p to q = ${d.toFixed(2)}`);
''', ts=r'''
const v: number[] = [3, -4];
const l2: number = Math.sqrt(v[0] ** 2 + v[1] ** 2);     // straight line length
const l1: number = Math.abs(v[0]) + Math.abs(v[1]);      // city block length
const linf: number = Math.max(Math.abs(v[0]), Math.abs(v[1]));  // biggest single step
console.log(`L2 = ${l2.toFixed(2)}, L1 = ${l1.toFixed(2)}, Linf = ${linf.toFixed(2)}`);
const unit: number[] = v.map(x => x / l2);
console.log(`unit vector = [${unit[0].toFixed(2)}, ${unit[1].toFixed(2)}], its length = ${Math.hypot(...unit).toFixed(2)}`);
const p: number[] = [1, 2], q: number[] = [4, 6];
const d: number = Math.sqrt((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2);
console.log(`distance from p to q = ${d.toFixed(2)}`);
''', java=r'''
public class Norms {
    public static void main(String[] args) {
        double[] v = {3, -4};
        double l2 = Math.sqrt(v[0] * v[0] + v[1] * v[1]);        // straight line length
        double l1 = Math.abs(v[0]) + Math.abs(v[1]);             // city block length
        double linf = Math.max(Math.abs(v[0]), Math.abs(v[1]));  // biggest single step
        System.out.println(String.format("L2 = %.2f, L1 = %.2f, Linf = %.2f", l2, l1, linf));
        double[] unit = {v[0] / l2, v[1] / l2};
        System.out.println(String.format("unit vector = [%.2f, %.2f], its length = %.2f", unit[0], unit[1], Math.hypot(unit[0], unit[1])));
        double[] p = {1, 2}, q = {4, 6};
        double d = Math.sqrt(Math.pow(q[0] - p[0], 2) + Math.pow(q[1] - p[1], 2));
        System.out.println(String.format("distance from p to q = %.2f", d));
    }
}
''')

K.code('dot', py=r'''
import math

a = [2, 3]
b = [4, -1]
dot = a[0] * b[0] + a[1] * b[1]           # multiply matching parts, add
la = math.sqrt(a[0] ** 2 + a[1] ** 2)
lb = math.sqrt(b[0] ** 2 + b[1] ** 2)
cos = dot / (la * lb)
angle = math.degrees(math.acos(cos))
print("a . b =", dot)
print(f"|a| = {la:.4f}, |b| = {lb:.4f}")
print(f"cos(angle) = {cos:.4f}, angle = {angle:.1f} degrees")
print("perpendicular?", [1, 2][0] * [-2, 1][0] + [1, 2][1] * [-2, 1][1] == 0)
''', js=r'''
const a = [2, 3];
const b = [4, -1];
const dot = a[0] * b[0] + a[1] * b[1];    // multiply matching parts, add
const la = Math.hypot(...a);
const lb = Math.hypot(...b);
const cos = dot / (la * lb);
const angle = Math.acos(cos) * 180 / Math.PI;
console.log("a . b =", dot);
console.log(`|a| = ${la.toFixed(4)}, |b| = ${lb.toFixed(4)}`);
console.log(`cos(angle) = ${cos.toFixed(4)}, angle = ${angle.toFixed(1)} degrees`);
console.log("perpendicular?", 1 * -2 + 2 * 1 === 0 ? "True" : "False");
''', ts=r'''
const a: number[] = [2, 3];
const b: number[] = [4, -1];
const dot: number = a[0] * b[0] + a[1] * b[1];   // multiply matching parts, add
const la: number = Math.hypot(...a);
const lb: number = Math.hypot(...b);
const cos: number = dot / (la * lb);
const angle: number = Math.acos(cos) * 180 / Math.PI;
console.log("a . b =", dot);
console.log(`|a| = ${la.toFixed(4)}, |b| = ${lb.toFixed(4)}`);
console.log(`cos(angle) = ${cos.toFixed(4)}, angle = ${angle.toFixed(1)} degrees`);
console.log("perpendicular?", 1 * -2 + 2 * 1 === 0 ? "True" : "False");
''', java=r'''
public class Dot {
    public static void main(String[] args) {
        double[] a = {2, 3};
        double[] b = {4, -1};
        int dot = (int) (a[0] * b[0] + a[1] * b[1]);   // multiply matching parts, add
        double la = Math.hypot(a[0], a[1]);
        double lb = Math.hypot(b[0], b[1]);
        double cos = dot / (la * lb);
        double angle = Math.toDegrees(Math.acos(cos));
        System.out.println("a . b = " + dot);
        System.out.println(String.format("|a| = %.4f, |b| = %.4f", la, lb));
        System.out.println(String.format("cos(angle) = %.4f, angle = %.1f degrees", cos, angle));
        System.out.println("perpendicular? " + (1 * -2 + 2 * 1 == 0 ? "True" : "False"));
    }
}
''')

K.code('cosine', py=r'''
import math


def cosine(u, v):
    dot = sum(a * b for a, b in zip(u, v))
    nu = math.sqrt(sum(a * a for a in u))
    nv = math.sqrt(sum(b * b for b in v))
    return dot / (nu * nv)


# how much each movie has of [action, comedy, romance]
movies = {"Rocket Race": [9, 2, 1], "Laugh Out": [1, 9, 3], "Love in Goa": [1, 3, 9], "Car Chase 2": [8, 3, 2]}
you = [7, 2, 1]                       # you watched mostly action
for name, m in movies.items():
    print(f"{name:<12} {cosine(you, m):.3f}")
''', js=r'''
function cosine(u, v) {
  const dot = u.reduce((s, a, i) => s + a * v[i], 0);
  const nu = Math.sqrt(u.reduce((s, a) => s + a * a, 0));
  const nv = Math.sqrt(v.reduce((s, b) => s + b * b, 0));
  return dot / (nu * nv);
}

// how much each movie has of [action, comedy, romance]
const movies = { "Rocket Race": [9, 2, 1], "Laugh Out": [1, 9, 3], "Love in Goa": [1, 3, 9], "Car Chase 2": [8, 3, 2] };
const you = [7, 2, 1];                // you watched mostly action
for (const [name, m] of Object.entries(movies)) {
  console.log(`${name.padEnd(12)} ${cosine(you, m).toFixed(3)}`);
}
''', ts=r'''
function cosine(u: number[], v: number[]): number {
  const dot: number = u.reduce((s, a, i) => s + a * v[i], 0);
  const nu: number = Math.sqrt(u.reduce((s, a) => s + a * a, 0));
  const nv: number = Math.sqrt(v.reduce((s, b) => s + b * b, 0));
  return dot / (nu * nv);
}

// how much each movie has of [action, comedy, romance]
const movies: Record<string, number[]> = { "Rocket Race": [9, 2, 1], "Laugh Out": [1, 9, 3], "Love in Goa": [1, 3, 9], "Car Chase 2": [8, 3, 2] };
const you: number[] = [7, 2, 1];      // you watched mostly action
for (const [name, m] of Object.entries(movies)) {
  console.log(`${name.padEnd(12)} ${cosine(you, m).toFixed(3)}`);
}
''', java=r'''
import java.util.LinkedHashMap;
import java.util.Map;

public class Cosine {
    static double cosine(double[] u, double[] v) {
        double dot = 0, nu = 0, nv = 0;
        for (int i = 0; i < u.length; i++) {
            dot += u[i] * v[i];
            nu += u[i] * u[i];
            nv += v[i] * v[i];
        }
        return dot / (Math.sqrt(nu) * Math.sqrt(nv));
    }

    public static void main(String[] args) {
        // how much each movie has of [action, comedy, romance]
        Map<String, double[]> movies = new LinkedHashMap<>();
        movies.put("Rocket Race", new double[]{9, 2, 1});
        movies.put("Laugh Out", new double[]{1, 9, 3});
        movies.put("Love in Goa", new double[]{1, 3, 9});
        movies.put("Car Chase 2", new double[]{8, 3, 2});
        double[] you = {7, 2, 1};             // you watched mostly action
        for (Map.Entry<String, double[]> e : movies.entrySet()) {
            System.out.println(String.format("%-12s %.3f", e.getKey(), cosine(you, e.getValue())));
        }
    }
}
''')

K.code('projection', py=r'''
a = [3, 4]          # the vector we cast a shadow of
b = [1, 0]          # the direction of the ground
dot = a[0] * b[0] + a[1] * b[1]
bb = b[0] * b[0] + b[1] * b[1]
k = dot / bb                       # how many copies of b fit in the shadow
proj = [k * b[0], k * b[1]]
rest = [a[0] - proj[0], a[1] - proj[1]]
print("shadow length =", k)
print("projection =", proj)
print("what is left =", rest)
print("left part . b =", rest[0] * b[0] + rest[1] * b[1])
''', js=r'''
const a = [3, 4];   // the vector we cast a shadow of
const b = [1, 0];   // the direction of the ground
const dot = a[0] * b[0] + a[1] * b[1];
const bb = b[0] * b[0] + b[1] * b[1];
const k = dot / bb;                // how many copies of b fit in the shadow
const proj = [k * b[0], k * b[1]];
const rest = [a[0] - proj[0], a[1] - proj[1]];
const f = v => "[" + v.map(x => x.toFixed(1)).join(", ") + "]";
console.log("shadow length =", k.toFixed(1));
console.log("projection =", f(proj));
console.log("what is left =", f(rest));
console.log("left part . b =", (rest[0] * b[0] + rest[1] * b[1]).toFixed(1));
''', ts=r'''
const a: number[] = [3, 4];   // the vector we cast a shadow of
const b: number[] = [1, 0];   // the direction of the ground
const dot: number = a[0] * b[0] + a[1] * b[1];
const bb: number = b[0] * b[0] + b[1] * b[1];
const k: number = dot / bb;              // how many copies of b fit in the shadow
const proj: number[] = [k * b[0], k * b[1]];
const rest: number[] = [a[0] - proj[0], a[1] - proj[1]];
const f = (v: number[]): string => "[" + v.map(x => x.toFixed(1)).join(", ") + "]";
console.log("shadow length =", k.toFixed(1));
console.log("projection =", f(proj));
console.log("what is left =", f(rest));
console.log("left part . b =", (rest[0] * b[0] + rest[1] * b[1]).toFixed(1));
''', java=r'''
import java.util.Arrays;

public class Projection {
    public static void main(String[] args) {
        double[] a = {3, 4};   // the vector we cast a shadow of
        double[] b = {1, 0};   // the direction of the ground
        double dot = a[0] * b[0] + a[1] * b[1];
        double bb = b[0] * b[0] + b[1] * b[1];
        double k = dot / bb;                 // how many copies of b fit in the shadow
        double[] proj = {k * b[0], k * b[1]};
        double[] rest = {a[0] - proj[0], a[1] - proj[1]};
        System.out.println("shadow length = " + k);
        System.out.println("projection = " + Arrays.toString(proj));
        System.out.println("what is left = " + Arrays.toString(rest));
        System.out.println("left part . b = " + (rest[0] * b[0] + rest[1] * b[1]));
    }
}
''')

K.code('independence', py=r'''
def det2(u, v):
    # area of the parallelogram made by u and v (with a sign)
    return u[0] * v[1] - u[1] * v[0]


pairs = [([2, 1], [1, 3]), ([2, 4], [1, 2]), ([1, 0], [0, 1])]
for u, v in pairs:
    d = det2(u, v)
    verdict = "independent, they span the whole plane" if d != 0 else "dependent, they lie on one line"
    print(u, v, "area", d, "->", verdict)
''', js=r'''
function det2(u, v) {
  // area of the parallelogram made by u and v (with a sign)
  return u[0] * v[1] - u[1] * v[0];
}

const pairs = [[[2, 1], [1, 3]], [[2, 4], [1, 2]], [[1, 0], [0, 1]]];
for (const [u, v] of pairs) {
  const d = det2(u, v);
  const verdict = d !== 0 ? "independent, they span the whole plane" : "dependent, they lie on one line";
  console.log(`[${u.join(", ")}] [${v.join(", ")}] area ${d} -> ${verdict}`);
}
''', ts=r'''
function det2(u: number[], v: number[]): number {
  // area of the parallelogram made by u and v (with a sign)
  return u[0] * v[1] - u[1] * v[0];
}

const pairs: number[][][] = [[[2, 1], [1, 3]], [[2, 4], [1, 2]], [[1, 0], [0, 1]]];
for (const [u, v] of pairs) {
  const d: number = det2(u, v);
  const verdict: string = d !== 0 ? "independent, they span the whole plane" : "dependent, they lie on one line";
  console.log(`[${u.join(", ")}] [${v.join(", ")}] area ${d} -> ${verdict}`);
}
''', java=r'''
import java.util.Arrays;

public class Independence {
    static int det2(int[] u, int[] v) {
        // area of the parallelogram made by u and v (with a sign)
        return u[0] * v[1] - u[1] * v[0];
    }

    public static void main(String[] args) {
        int[][][] pairs = {{{2, 1}, {1, 3}}, {{2, 4}, {1, 2}}, {{1, 0}, {0, 1}}};
        for (int[][] p : pairs) {
            int d = det2(p[0], p[1]);
            String verdict = d != 0 ? "independent, they span the whole plane" : "dependent, they lie on one line";
            System.out.println(Arrays.toString(p[0]) + " " + Arrays.toString(p[1]) + " area " + d + " -> " + verdict);
        }
    }
}
''')

# ---------------------------------------------------------------- practice programs
K.code('p_nearest', py=r'''
import math

shops = {"A": [1, 5], "B": [4, 4], "C": [6, 1], "D": [2, 2]}
home = [3, 3]
best, best_d = None, float("inf")
for name, p in shops.items():
    d = math.dist(home, p)                 # straight line distance
    print(f"{name}: {d:.3f}")
    if d < best_d:
        best, best_d = name, d
print("nearest shop:", best)
''', js=r'''
const shops = { A: [1, 5], B: [4, 4], C: [6, 1], D: [2, 2] };
const home = [3, 3];
let best = null, bestD = Infinity;
for (const [name, p] of Object.entries(shops)) {
  const d = Math.hypot(home[0] - p[0], home[1] - p[1]);  // straight line distance
  console.log(`${name}: ${d.toFixed(3)}`);
  if (d < bestD) {
    best = name;
    bestD = d;
  }
}
console.log("nearest shop:", best);
''', ts=r'''
const shops: Record<string, number[]> = { A: [1, 5], B: [4, 4], C: [6, 1], D: [2, 2] };
const home: number[] = [3, 3];
let best: string = "", bestD: number = Infinity;
for (const [name, p] of Object.entries(shops)) {
  const d: number = Math.hypot(home[0] - p[0], home[1] - p[1]);  // straight line distance
  console.log(`${name}: ${d.toFixed(3)}`);
  if (d < bestD) {
    best = name;
    bestD = d;
  }
}
console.log("nearest shop:", best);
''', java=r'''
import java.util.LinkedHashMap;
import java.util.Map;

public class PracticeNearest {
    public static void main(String[] args) {
        Map<String, double[]> shops = new LinkedHashMap<>();
        shops.put("A", new double[]{1, 5});
        shops.put("B", new double[]{4, 4});
        shops.put("C", new double[]{6, 1});
        shops.put("D", new double[]{2, 2});
        double[] home = {3, 3};
        String best = null;
        double bestD = Double.POSITIVE_INFINITY;
        for (Map.Entry<String, double[]> e : shops.entrySet()) {
            double[] p = e.getValue();
            double d = Math.hypot(home[0] - p[0], home[1] - p[1]);  // straight line distance
            System.out.println(String.format("%s: %.3f", e.getKey(), d));
            if (d < bestD) {
                best = e.getKey();
                bestD = d;
            }
        }
        System.out.println("nearest shop: " + best);
    }
}
''')

K.code('p_rank', py=r'''
import math

words = ["goal", "match", "vote", "price"]
docs = {
    "sports news":   [5, 4, 0, 0],
    "election news": [0, 1, 6, 1],
    "market news":   [0, 0, 1, 5],
}
query = [1, 1, 0, 0]                    # the search: "goal match"


def cosine(u, v):
    dot = sum(a * b for a, b in zip(u, v))
    return dot / (math.sqrt(sum(a * a for a in u)) * math.sqrt(sum(b * b for b in v)))


ranked = sorted(docs.items(), key=lambda kv: -cosine(query, kv[1]))
for name, d in ranked:
    print(f"{cosine(query, d):.3f}  {name}")
''', js=r'''
const docs = {
  "sports news": [5, 4, 0, 0],
  "election news": [0, 1, 6, 1],
  "market news": [0, 0, 1, 5],
};
const query = [1, 1, 0, 0];             // the search: "goal match"

function cosine(u, v) {
  const dot = u.reduce((s, a, i) => s + a * v[i], 0);
  return dot / (Math.hypot(...u) * Math.hypot(...v));
}

const ranked = Object.entries(docs).sort((x, y) => cosine(query, y[1]) - cosine(query, x[1]));
for (const [name, d] of ranked) {
  console.log(`${cosine(query, d).toFixed(3)}  ${name}`);
}
''', ts=r'''
const docs: Record<string, number[]> = {
  "sports news": [5, 4, 0, 0],
  "election news": [0, 1, 6, 1],
  "market news": [0, 0, 1, 5],
};
const query: number[] = [1, 1, 0, 0];   // the search: "goal match"

function cosine(u: number[], v: number[]): number {
  const dot: number = u.reduce((s, a, i) => s + a * v[i], 0);
  return dot / (Math.hypot(...u) * Math.hypot(...v));
}

const ranked = Object.entries(docs).sort((x, y) => cosine(query, y[1]) - cosine(query, x[1]));
for (const [name, d] of ranked) {
  console.log(`${cosine(query, d).toFixed(3)}  ${name}`);
}
''', java=r'''
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class PracticeRank {
    static double cosine(double[] u, double[] v) {
        double dot = 0, nu = 0, nv = 0;
        for (int i = 0; i < u.length; i++) {
            dot += u[i] * v[i];
            nu += u[i] * u[i];
            nv += v[i] * v[i];
        }
        return dot / (Math.sqrt(nu) * Math.sqrt(nv));
    }

    public static void main(String[] args) {
        Map<String, double[]> docs = new LinkedHashMap<>();
        docs.put("sports news", new double[]{5, 4, 0, 0});
        docs.put("election news", new double[]{0, 1, 6, 1});
        docs.put("market news", new double[]{0, 0, 1, 5});
        double[] query = {1, 1, 0, 0};      // the search: "goal match"
        List<Map.Entry<String, double[]>> ranked = new ArrayList<>(docs.entrySet());
        ranked.sort((x, y) -> Double.compare(cosine(query, y.getValue()), cosine(query, x.getValue())));
        for (Map.Entry<String, double[]> e : ranked) {
            System.out.println(String.format("%.3f  %s", cosine(query, e.getValue()), e.getKey()));
        }
    }
}
''')

K.code('p_gram', py=r'''
def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


v1 = [3.0, 1.0]
v2 = [2.0, 2.0]
# keep v1, then remove from v2 its shadow on v1
k = dot(v2, v1) / dot(v1, v1)
u2 = [v2[i] - k * v1[i] for i in range(2)]
print(f"u1 = [{v1[0]:.2f}, {v1[1]:.2f}]")
print(f"u2 = [{u2[0]:.2f}, {u2[1]:.2f}]")
print("u1 . u2 is zero:", abs(dot(v1, u2)) < 1e-9)
''', js=r'''
const dot = (u, v) => u.reduce((s, a, i) => s + a * v[i], 0);

const v1 = [3.0, 1.0];
const v2 = [2.0, 2.0];
// keep v1, then remove from v2 its shadow on v1
const k = dot(v2, v1) / dot(v1, v1);
const u2 = v2.map((x, i) => x - k * v1[i]);
console.log(`u1 = [${v1[0].toFixed(2)}, ${v1[1].toFixed(2)}]`);
console.log(`u2 = [${u2[0].toFixed(2)}, ${u2[1].toFixed(2)}]`);
console.log("u1 . u2 is zero:", Math.abs(dot(v1, u2)) < 1e-9 ? "True" : "False");
''', ts=r'''
const dot = (u: number[], v: number[]): number => u.reduce((s, a, i) => s + a * v[i], 0);

const v1: number[] = [3.0, 1.0];
const v2: number[] = [2.0, 2.0];
// keep v1, then remove from v2 its shadow on v1
const k: number = dot(v2, v1) / dot(v1, v1);
const u2: number[] = v2.map((x, i) => x - k * v1[i]);
console.log(`u1 = [${v1[0].toFixed(2)}, ${v1[1].toFixed(2)}]`);
console.log(`u2 = [${u2[0].toFixed(2)}, ${u2[1].toFixed(2)}]`);
console.log("u1 . u2 is zero:", Math.abs(dot(v1, u2)) < 1e-9 ? "True" : "False");
''', java=r'''
public class PracticeGram {
    static double dot(double[] u, double[] v) {
        double s = 0;
        for (int i = 0; i < u.length; i++) s += u[i] * v[i];
        return s;
    }

    public static void main(String[] args) {
        double[] v1 = {3.0, 1.0};
        double[] v2 = {2.0, 2.0};
        // keep v1, then remove from v2 its shadow on v1
        double k = dot(v2, v1) / dot(v1, v1);
        double[] u2 = {v2[0] - k * v1[0], v2[1] - k * v1[1]};
        System.out.println(String.format("u1 = [%.2f, %.2f]", v1[0], v1[1]));
        System.out.println(String.format("u2 = [%.2f, %.2f]", u2[0], u2[1]));
        System.out.println("u1 . u2 is zero: " + (Math.abs(dot(v1, u2)) < 1e-9 ? "True" : "False"));
    }
}
''')

K.code('p_knn', py=r'''
import math

# [height cm, weight kg] -> label
data = [([150, 50], "S"), ([155, 55], "S"), ([160, 58], "S"),
        ([175, 75], "L"), ([180, 80], "L"), ([170, 72], "L")]
new = [165, 66]
k = 3
by_distance = sorted(data, key=lambda row: math.dist(row[0], new))
votes = {}
for point, label in by_distance[:k]:
    print(point, label, f"{math.dist(point, new):.2f}")
    votes[label] = votes.get(label, 0) + 1
print("prediction:", max(votes, key=votes.get))
''', js=r'''
// [height cm, weight kg] -> label
const data = [[[150, 50], "S"], [[155, 55], "S"], [[160, 58], "S"],
              [[175, 75], "L"], [[180, 80], "L"], [[170, 72], "L"]];
const pt = [165, 66];
const k = 3;
const dist = p => Math.hypot(p[0] - pt[0], p[1] - pt[1]);
const byDistance = [...data].sort((a, b) => dist(a[0]) - dist(b[0]));
const votes = {};
for (const [point, label] of byDistance.slice(0, k)) {
  console.log(`[${point.join(", ")}] ${label} ${dist(point).toFixed(2)}`);
  votes[label] = (votes[label] || 0) + 1;
}
console.log("prediction:", Object.keys(votes).reduce((a, b) => votes[a] >= votes[b] ? a : b));
''', ts=r'''
// [height cm, weight kg] -> label
const data: [number[], string][] = [[[150, 50], "S"], [[155, 55], "S"], [[160, 58], "S"],
                                    [[175, 75], "L"], [[180, 80], "L"], [[170, 72], "L"]];
const pt: number[] = [165, 66];
const k: number = 3;
const dist = (p: number[]): number => Math.hypot(p[0] - pt[0], p[1] - pt[1]);
const byDistance = [...data].sort((a, b) => dist(a[0]) - dist(b[0]));
const votes: Record<string, number> = {};
for (const [point, label] of byDistance.slice(0, k)) {
  console.log(`[${point.join(", ")}] ${label} ${dist(point).toFixed(2)}`);
  votes[label] = (votes[label] || 0) + 1;
}
console.log("prediction:", Object.keys(votes).reduce((a, b) => votes[a] >= votes[b] ? a : b));
''', java=r'''
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class PracticeKnn {
    public static void main(String[] args) {
        // [height cm, weight kg] -> label
        int[][] pts = {{150, 50}, {155, 55}, {160, 58}, {175, 75}, {180, 80}, {170, 72}};
        String[] labels = {"S", "S", "S", "L", "L", "L"};
        int[] pt = {165, 66};
        int k = 3;
        List<Integer> idx = new ArrayList<>();
        for (int i = 0; i < pts.length; i++) idx.add(i);
        idx.sort((a, b) -> Double.compare(dist(pts[a], pt), dist(pts[b], pt)));
        Map<String, Integer> votes = new LinkedHashMap<>();
        for (int i : idx.subList(0, k)) {
            System.out.println(Arrays.toString(pts[i]) + " " + labels[i] + " " + String.format("%.2f", dist(pts[i], pt)));
            votes.merge(labels[i], 1, Integer::sum);
        }
        String best = null;
        for (String l : votes.keySet()) if (best == null || votes.get(l) > votes.get(best)) best = l;
        System.out.println("prediction: " + best);
    }

    static double dist(int[] a, int[] b) {
        return Math.hypot(a[0] - b[0], a[1] - b[1]);
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('what', '➡️', 'What a vector is', f'''
<p>A <b>vector</b> is an ordered list of numbers. You can picture it in two ways, and both are useful.</p>
<div class="grid2">
<div class="box"><h4>🏹 An arrow</h4><p>v = [3, 2] is an arrow that goes 3 steps right and 2 steps up. It has a <b>length</b> (how far) and a <b>direction</b> (which way). Moving the arrow somewhere else does not change it.</p></div>
<div class="box"><h4>📋 A list of features</h4><p>A flat with 2 bedrooms, 85 square metres and 12 years old is the vector [2, 85, 12]. Each position always means the same thing. That position is called a <b>component</b> or <b>feature</b>.</p></div>
</div>
<p>The number of components is the <b>dimension</b>. [3, 2] lives in 2D, [2, 85, 12] in 3D. A 28 × 28 pixel photo of a digit is a vector with 784 numbers, so it lives in 784 dimensions. We cannot draw that, but every rule in this chapter works the same way there.</p>
{fx('Writing a vector', f'v = [v₁, v₂, ..., vₙ] &nbsp; or as a column &nbsp; {vec(["v₁", "v₂", "⋮", "vₙ"])}', 'Books print vectors in bold (<b>v</b>) or with an arrow on top. ℝⁿ means "all vectors with n real numbers".')}
{life('A GPS location is a vector [latitude, longitude]. A wind forecast is a vector: 20 km/h towards the north east is a length and a direction. A recipe is a vector of amounts [flour, sugar, eggs].')}
{ml('Every example in a dataset is a vector, called a <b>feature vector</b>. Words are turned into vectors called <b>embeddings</b>, where words with similar meaning point in similar directions. The weights of a model are a vector too.')}
''', kw=['vector', 'component', 'feature vector', 'dimension', 'embedding', 'R^n']),

    part('ops', '➕', 'Adding, subtracting and scaling vectors', f'''
<p>Vectors are added part by part: [3, 1] + [1, 2] = [4, 3]. As arrows, put the tail of the second at the tip of the first. The sum goes from the very start to the very end. Multiplying by a number (a <b>scalar</b>) stretches the arrow: 2 × [3, 1] = [6, 2]. A negative scalar flips it round.</p>
{fxs(fx('Addition', 'a + b = [a₁ + b₁, a₂ + b₂, ...]', 'Only for vectors of the same size.'),
         fx('Scalar multiplication', 'k·a = [k·a₁, k·a₂, ...]', 'k &gt; 1 stretches, 0 &lt; k &lt; 1 shrinks, k &lt; 0 flips.'),
         fx('Linear combination', 'c₁·v₁ + c₂·v₂ + ... + cₖ·vₖ', 'Scale several vectors, then add them. This is the most important pattern in linear algebra.'))}
{viz('vec2d', mode='add')}
{code('vec_ops', 'Vector arithmetic part by part')}
{life('A boat heads east at 4 km/h while the river pushes it north at 3 km/h. Its real velocity is [4, 0] + [0, 3] = [4, 3], so it moves at 5 km/h towards the north east. Pilots add wind vectors to plan every flight.')}
{ml('A neuron computes w₁x₁ + w₂x₂ + ... + b, a linear combination of the inputs. In word embeddings the famous example is king − man + woman ≈ queen: vector arithmetic captured a relationship of meaning.')}
''', kw=['vector addition', 'scalar multiplication', 'linear combination', 'tip to tail', 'resultant']),

    part('norm', '📏', 'Length (norm) and distance', f'''
<p>The length of a vector is called its <b>norm</b>. The usual one comes straight from Pythagoras: [3, 4] has length √(3² + 4²) = √25 = 5. There are other useful ways to measure size.</p>
{fxs(fx('L2 norm (Euclidean)', '‖v‖₂ = √(v₁² + v₂² + ... + vₙ²)', 'The straight line, as the crow flies.'),
         fx('L1 norm (Manhattan)', '‖v‖₁ = |v₁| + |v₂| + ... + |vₙ|', 'Walking along city blocks.'),
         fx('Unit vector', f'û = {frac("v", "‖v‖")}', 'Same direction, length exactly 1. This is called normalising.'),
         fx('Distance between points', 'd(p, q) = ‖p − q‖', 'Subtract, then take the length.'))}
{viz('norms')}
{code('norms', 'Three norms, a unit vector and a distance')}
{table(['Norm', 'Value for [3, −4]', 'ML use'], [
        ['L2', '5', 'k nearest neighbours, k means, Ridge (L2) regularisation'],
        ['L1', '7', 'Lasso (L1) regularisation, which pushes weights to exactly zero'],
        ['L∞', '4', 'adversarial examples that change each pixel by at most a tiny amount'],
    ])}
<div class="warn">Distances are only fair when features use similar scales. If one feature is salary in rupees (around 500000) and another is age in years (around 30), salary dominates every distance. Scale the features first, for example to a mean of 0 and a standard deviation of 1.</div>
{trick('A 3, 4, 5 triangle is the easiest Pythagoras check to remember. Its multiples 6, 8, 10 and 30, 40, 50 work too, and so do 5, 12, 13 and 8, 15, 17.')}
''', kw=['norm', 'length', 'magnitude', 'euclidean distance', 'manhattan distance', 'L1', 'L2', 'unit vector', 'normalise', 'feature scaling']),

    part('dot', '✖️', 'The dot product', f'''
<p>The <b>dot product</b> turns two vectors into one number. Multiply matching parts, then add: [2, 3] · [4, −1] = 2 × 4 + 3 × (−1) = 8 − 3 = 5. It also has a meaning in pictures: it measures how much two arrows point the same way.</p>
{fxs(fx('Algebra form', 'a · b = a₁b₁ + a₂b₂ + ... + aₙbₙ = Σ aᵢbᵢ', 'Easy to compute, even in a million dimensions.'),
         fx('Geometry form', 'a · b = ‖a‖ ‖b‖ cos θ', 'θ (theta) is the angle between the arrows.'))}
{table(['Angle θ', 'cos θ', 'Dot product', 'Meaning'], [
        ['0°', '1', 'largest positive', 'same direction'],
        ['less than 90°', 'between 0 and 1', 'positive', 'roughly the same way'],
        ['90°', '0', 'zero', '<b>orthogonal</b> (perpendicular): unrelated'],
        ['more than 90°', 'negative', 'negative', 'roughly opposite'],
        ['180°', '−1', 'most negative', 'exactly opposite'],
    ])}
{viz('vec2d', mode='dot')}
{code('dot', 'Dot product, lengths and the angle between two vectors')}
{worked('Find the angle between a = [1, 2] and b = [3, 1]', [
        'Dot product: <span class="eq">a · b = 1 × 3 + 2 × 1 = 5</span>',
        'Lengths: <span class="eq">‖a‖ = √(1 + 4) = √5</span> and <span class="eq">‖b‖ = √(9 + 1) = √10</span>',
        'Cosine: <span class="eq">cos θ = 5 ÷ (√5 × √10) = 5 ÷ √50 = 5 ÷ 7.071 ≈ 0.7071</span>',
        'Angle: <span class="eq">θ = cos⁻¹(0.7071) = 45°</span>'])}
{ml('Almost every calculation in a neural network is a dot product. A neuron takes the dot product of its weights with the inputs, w · x + b. Attention in transformers takes dot products between "query" and "key" vectors to decide which words to focus on. GPUs are built to do billions of dot products per second.')}
''', kw=['dot product', 'inner product', 'angle between vectors', 'orthogonal', 'perpendicular', 'cos theta', 'attention']),

    part('cosine', '🎬', 'Cosine similarity: how alike are two things', f'''
<p>If you divide the dot product by both lengths, you get cos θ alone. This is <b>cosine similarity</b>. It ignores how long the arrows are and only compares their directions, which makes it perfect for comparing things of different sizes, like a short tweet and a long article about the same topic.</p>
{fx('Cosine similarity', f'cos(a, b) = {frac("a · b", "‖a‖ ‖b‖")}', '1 means same direction, 0 means unrelated, −1 means opposite. For counts, which are never negative, it stays between 0 and 1.')}
{viz('cossim')}
{code('cosine', 'Recommend movies by cosine similarity')}
{life('Streaming apps describe you and every film as vectors of tastes. The films whose vectors point closest to yours are the ones on your "Because you watched" row.')}
{ml('Search engines and chat assistants turn your question and every document into embedding vectors, then fetch the documents with the highest cosine similarity. This is called <b>semantic search</b>, and it is the "retrieval" in retrieval augmented generation (RAG).')}
{trick('Cosine similarity is the dot product of the two unit vectors. Normalise first, then a plain dot product gives the cosine. Vector databases store normalised vectors for exactly this reason.')}
''', kw=['cosine similarity', 'similarity', 'recommendation', 'semantic search', 'embedding', 'RAG']),

    part('proj', '🔦', 'Projection: the shadow of a vector', f'''
<p>Shine a light straight down onto a line. The shadow a vector casts on that line is its <b>projection</b>. It tells you how much of one vector lies along the direction of another.</p>
{fxs(fx('Scalar projection (shadow length)', f'comp_b a = {frac("a · b", "‖b‖")}', 'A signed length. Negative means the shadow points backwards.'),
         fx('Vector projection (the shadow itself)', f'proj_b a = {frac("a · b", "b · b")} b', 'A vector along b. What is left over, a − proj_b a, is perpendicular to b.'))}
{viz('vec2d', mode='proj')}
{code('projection', 'Project [3, 4] onto the x axis')}
{worked('Project a = [2, 3] onto b = [4, 0]', [
        'Dot product: <span class="eq">a · b = 2 × 4 + 3 × 0 = 8</span>',
        'b · b: <span class="eq">4 × 4 + 0 × 0 = 16</span>',
        'Scale factor: <span class="eq">8 ÷ 16 = 0.5</span>',
        'Projection: <span class="eq">0.5 × [4, 0] = [2, 0]</span>',
        'Left over: <span class="eq">[2, 3] − [2, 0] = [0, 3]</span>, and [0, 3] · [4, 0] = 0, so it is perpendicular. ✔'])}
{ml('Linear regression finds the projection of the target vector onto the space spanned by the feature columns. PCA (Chapter 5) projects data onto the few directions that keep the most information.')}
''', kw=['projection', 'vector projection', 'scalar projection', 'shadow', 'orthogonal decomposition']),

    part('span', '🧱', 'Span, independence and basis', f'''
<p>Take all the linear combinations of some vectors. Every point you can reach is called their <b>span</b>. With [1, 0] and [0, 1] you can reach any point in the plane: [5, −2] = 5·[1, 0] − 2·[0, 1].</p>
<div class="grid2">
<div class="box"><h4>✅ Linearly independent</h4><p>No vector in the set can be built from the others. Each one adds a brand new direction. [2, 1] and [1, 3] are independent, and together they span the whole plane.</p></div>
<div class="box"><h4>❌ Linearly dependent</h4><p>At least one is a combination of the others, so it adds nothing new. [2, 4] = 2 × [1, 2], so these two only reach one line.</p></div>
</div>
{fx('Basis and dimension', 'basis = a set of independent vectors that spans the space', 'Every basis of ℝⁿ has exactly n vectors. That number n is the dimension.')}
{code('independence', 'Test two vectors for independence with the parallelogram area')}
{table(['Words', 'Plain meaning'], [
        ['Span', 'everywhere you can reach by scaling and adding'],
        ['Independent', 'no vector is wasted'],
        ['Basis', 'the smallest set of building blocks that reaches everything'],
        ['Dimension', 'how many building blocks a basis needs'],
        ['Orthonormal basis', 'building blocks of length 1 that are all perpendicular, such as [1, 0] and [0, 1]'],
    ])}
{ml('If two features are dependent, for example height in cm and the same height in inches, the model gets no new information and linear regression becomes unstable. This problem is called <b>multicollinearity</b>. The <b>rank</b> of a data matrix (Chapter 4) counts its independent columns.')}
{life('Red, green and blue light form a basis for the colours a screen can show. Every pixel is a linear combination r·red + g·green + b·blue.')}
''', kw=['span', 'linear independence', 'linearly dependent', 'basis', 'dimension', 'orthonormal basis', 'multicollinearity']),
]

INFO = {
    'title': 'Vectors are arrows and lists',
    'panels': [
        {'s': [['e', '🏹'], ['c', [3, 2], {'ix': False}]], 'h': 'An arrow and a list', 't': 'Length plus direction.', 'more': 'Every example in a dataset is a feature vector.'},
        {'s': [['e', '➕'], ['t', '[3, 1] + [1, 2] = [4, 3]', {'b': 1}]], 'h': 'Add tip to tail', 't': 'Part by part.', 'more': 'Linear combinations are the heart of every neuron.'},
        {'s': [['e', '✖️'], ['t', 'a · b = Σ aᵢbᵢ', {'b': 1}]], 'h': 'Dot product', 't': 'Same direction gives a big number.', 'more': 'Zero means perpendicular, negative means opposite.'},
        {'s': [['e', '🎬'], ['b', [0.99, 0.27, 0.25, 0.97]]], 'h': 'Cosine similarity', 't': 'Compare directions only.', 'more': 'Recommendations and semantic search rank by cosine similarity.'},
    ],
    'remember': 'A vector is a list of numbers and an arrow. Add part by part, scale by multiplying. The norm is a length, the dot product measures agreement, cosine similarity compares directions, and a projection is a shadow.',
}

REAL = [
    ['🧭', 'Flying a plane', 'Pilots add the wind vector to the plane velocity vector to find where the plane really goes, and steer a little into the wind to cancel it.'],
    ['🎵', 'Music recommendations', 'Songs and listeners are vectors of features. Songs with the highest cosine similarity to your listening vector are suggested next.'],
    ['🏃', 'Delivery apps', 'The nearest rider is found by the distance between two location vectors, and the route length uses Manhattan style distances along streets.'],
]

K.say('top', 'Welcome',
      'Vectors are where linear algebra begins. A vector is a list of numbers and also an arrow with a length and a direction. You will add and scale vectors, measure their length, and use the dot product and cosine similarity to compare them.',
      'Vectors से linear algebra शुरू होता है। Vector संख्याओं की सूची है और लंबाई व दिशा वाला तीर भी। आप vectors को जोड़ेंगे, scale करेंगे, लंबाई मापेंगे, और dot product व cosine similarity से तुलना करेंगे।',
      'Vectors ನಿಂದ linear algebra ಆರಂಭ. Vector ಸಂಖ್ಯೆಗಳ ಪಟ್ಟಿ ಮತ್ತು ಉದ್ದ ಹಾಗೂ ದಿಕ್ಕು ಇರುವ ಬಾಣ. ನೀವು ಕೂಡಿಸುತ್ತೀರಿ, scale ಮಾಡುತ್ತೀರಿ, ಉದ್ದ ಅಳೆಯುತ್ತೀರಿ, dot product ಮತ್ತು cosine similarity ಬಳಸುತ್ತೀರಿ.',
      'Vectors ରୁ linear algebra ଆରମ୍ଭ। Vector ସଂଖ୍ୟାର ତାଲିକା ଏବଂ ଲମ୍ବ ଓ ଦିଗ ଥିବା ତୀର। ଆପଣ ଯୋଗ, scale, ଲମ୍ବ ମାପ, dot product ଓ cosine similarity ଶିଖିବେ।',
      'المتجهات بداية الجبر الخطي. المتجه قائمة أعداد وهو أيضًا سهم له طول واتجاه. ستجمع المتجهات وتضربها في أعداد وتقيس أطوالها وتقارنها بالضرب النقطي وتشابه جيب التمام.',
      'Mit Vektoren beginnt die lineare Algebra. Ein Vektor ist eine Liste von Zahlen und zugleich ein Pfeil mit Länge und Richtung. Du addierst und skalierst Vektoren, misst ihre Länge und vergleichst sie mit Skalarprodukt und Kosinusähnlichkeit.')
K.say('what', 'What a vector is',
      'A vector is an ordered list of numbers. As an arrow it has a length and a direction. As data it is a feature vector, where each position always means the same thing. The number of positions is the dimension.',
      'Vector संख्याओं की क्रमबद्ध सूची है। तीर के रूप में इसकी लंबाई और दिशा है। Data के रूप में यह feature vector है। Positions की संख्या dimension है।',
      'Vector ಸಂಖ್ಯೆಗಳ ಕ್ರಮಬದ್ಧ ಪಟ್ಟಿ. ಬಾಣವಾಗಿ ಉದ್ದ ಮತ್ತು ದಿಕ್ಕು ಇದೆ. Data ಆಗಿ ಅದು feature vector. ಸ್ಥಾನಗಳ ಸಂಖ್ಯೆ dimension.',
      'Vector ସଂଖ୍ୟାର କ୍ରମବଦ୍ଧ ତାଲିକା। ତୀର ଭାବେ ଏହାର ଲମ୍ବ ଓ ଦିଗ ଅଛି। Data ଭାବେ ଏହା feature vector। ସ୍ଥାନ ସଂଖ୍ୟା dimension।',
      'المتجه قائمة مرتبة من الأعداد. كسهم له طول واتجاه، وكبيانات هو متجه خصائص يعني كل موضع فيه الشيء نفسه دائمًا. عدد المواضع هو البعد.',
      'Ein Vektor ist eine geordnete Liste von Zahlen. Als Pfeil hat er Länge und Richtung, als Daten ist er ein Merkmalsvektor, bei dem jede Stelle immer dasselbe bedeutet. Die Anzahl der Stellen ist die Dimension.')
K.say('ops', 'Vector operations',
      'Add vectors part by part, or as arrows tip to tail. Multiplying by a number stretches, shrinks or flips the arrow. Scaling several vectors and adding them is called a linear combination, and every neuron does exactly that.',
      'Vectors को हिस्सा दर हिस्सा जोड़ें, या तीरों को सिरे से पूँछ तक। संख्या से गुणा करने पर तीर खिंचता, सिकुड़ता या पलटता है। कई vectors को scale करके जोड़ना linear combination है।',
      'Vectors ಅನ್ನು ಭಾಗವಾರು ಕೂಡಿಸಿ, ಅಥವಾ ಬಾಣಗಳನ್ನು ತುದಿಯಿಂದ ಬಾಲಕ್ಕೆ. ಸಂಖ್ಯೆಯಿಂದ ಗುಣಿಸಿದರೆ ಬಾಣ ಉದ್ದವಾಗುತ್ತದೆ ಅಥವಾ ತಿರುಗುತ್ತದೆ. ಇದನ್ನು linear combination ಎನ್ನುತ್ತಾರೆ.',
      'Vectors କୁ ଅଂଶ ଅଂଶ କରି ଯୋଗ କରନ୍ତୁ, କିମ୍ବା ତୀରକୁ ମୁଣ୍ଡରୁ ଲାଞ୍ଜ। ସଂଖ୍ୟାରେ ଗୁଣନ କଲେ ତୀର ଲମ୍ବା ହୁଏ ବା ଓଲଟେ। ଏହାକୁ linear combination କୁହାଯାଏ।',
      'نجمع المتجهات جزءًا بجزء، أو كسهام من الرأس إلى الذيل. والضرب في عدد يمد السهم أو يقلصه أو يقلبه. وتوسيع عدة متجهات ثم جمعها يسمى تركيبًا خطيًا، وهذا ما يفعله كل عصبون.',
      'Vektoren addiert man Stelle für Stelle oder als Pfeile Spitze an Ende. Mit einer Zahl multipliziert wird der Pfeil gestreckt, gestaucht oder umgedreht. Mehrere Vektoren skalieren und addieren heißt Linearkombination, und genau das tut jedes Neuron.')
K.say('norm', 'Norms',
      'The norm is the length of a vector. The L2 norm is the straight line length from Pythagoras, and the L1 norm adds the absolute values like walking city blocks. Dividing by the norm gives a unit vector of length one.',
      'Norm vector की लंबाई है। L2 norm Pythagoras वाली सीधी लंबाई है, और L1 norm absolute values जोड़ता है। Norm से भाग देने पर लंबाई एक वाला unit vector मिलता है।',
      'Norm ಎಂದರೆ vector ನ ಉದ್ದ. L2 norm Pythagoras ನ ನೇರ ಉದ್ದ, L1 norm absolute values ಕೂಡಿಸುತ್ತದೆ. Norm ನಿಂದ ಭಾಗಿಸಿದರೆ unit vector ಸಿಗುತ್ತದೆ.',
      'Norm ହେଉଛି vector ର ଲମ୍ବ। L2 norm Pythagoras ର ସିଧା ଲମ୍ବ, L1 norm absolute values ଯୋଗ କରେ। Norm ରେ ହରଣ କଲେ unit vector ମିଳେ।',
      'المعيار هو طول المتجه. معيار L2 هو الطول المستقيم من فيثاغورس، ومعيار L1 يجمع القيم المطلقة مثل المشي في شوارع المدينة. والقسمة على المعيار تعطي متجه وحدة طوله واحد.',
      'Die Norm ist die Länge eines Vektors. Die L2 Norm ist die gerade Länge nach Pythagoras, die L1 Norm addiert die Beträge wie ein Weg durch Häuserblocks. Teilt man durch die Norm, erhält man einen Einheitsvektor der Länge eins.')
K.say('dot', 'The dot product',
      'The dot product multiplies matching parts and adds them up. It also equals the two lengths times the cosine of the angle between them. A positive result means the arrows agree, zero means they are perpendicular, and negative means they point apart.',
      'Dot product मिलते हिस्सों को गुणा करके जोड़ता है। यह दोनों लंबाइयों गुणा उनके बीच के कोण के cosine के बराबर भी है। Positive मतलब सहमति, शून्य मतलब लंब, negative मतलब विपरीत।',
      'Dot product ಹೊಂದುವ ಭಾಗಗಳನ್ನು ಗುಣಿಸಿ ಕೂಡಿಸುತ್ತದೆ. ಅದು ಎರಡು ಉದ್ದಗಳು ಗುಣಿಸು ಕೋನದ cosine ಗೂ ಸಮ. ಸೊನ್ನೆ ಎಂದರೆ ಲಂಬ.',
      'Dot product ମେଳ ଖାଉଥିବା ଅଂଶ ଗୁଣନ କରି ଯୋଗ କରେ। ଏହା ଦୁଇ ଲମ୍ବ ଗୁଣନ କୋଣର cosine ସହ ସମାନ। ଶୂନ ମାନେ ଲମ୍ବ।',
      'الضرب النقطي يضرب الأجزاء المتقابلة ويجمعها، ويساوي أيضًا حاصل ضرب الطولين في جيب تمام الزاوية بينهما. الموجب يعني اتفاق الاتجاه، والصفر يعني التعامد، والسالب يعني التعاكس.',
      'Das Skalarprodukt multipliziert passende Stellen und addiert sie. Es ist auch das Produkt der beiden Längen mal dem Kosinus des Winkels. Positiv heißt gleiche Richtung, null heißt senkrecht, negativ heißt entgegengesetzt.')
K.say('cosine', 'Cosine similarity',
      'Cosine similarity divides the dot product by both lengths, so it compares only directions. One means the same direction and zero means unrelated. Recommendation systems and semantic search rank results this way.',
      'Cosine similarity dot product को दोनों लंबाइयों से भाग देता है, इसलिए सिर्फ दिशाओं की तुलना करता है। एक मतलब एक ही दिशा, शून्य मतलब असंबंधित। Recommendation और semantic search ऐसे ही rank करते हैं।',
      'Cosine similarity dot product ಅನ್ನು ಎರಡು ಉದ್ದಗಳಿಂದ ಭಾಗಿಸುತ್ತದೆ, ದಿಕ್ಕುಗಳನ್ನು ಮಾತ್ರ ಹೋಲಿಸುತ್ತದೆ. Recommendation ಮತ್ತು semantic search ಹೀಗೆ rank ಮಾಡುತ್ತವೆ.',
      'Cosine similarity dot product କୁ ଦୁଇ ଲମ୍ବରେ ହରଣ କରେ, ତେଣୁ କେବଳ ଦିଗ ତୁଳନା କରେ। Recommendation ଓ semantic search ଏହିପରି rank କରନ୍ତି।',
      'تشابه جيب التمام يقسم الضرب النقطي على الطولين، فيقارن الاتجاهات فقط. الواحد يعني الاتجاه نفسه والصفر يعني لا علاقة. أنظمة التوصية والبحث الدلالي ترتب النتائج بهذه الطريقة.',
      'Die Kosinusähnlichkeit teilt das Skalarprodukt durch beide Längen und vergleicht so nur Richtungen. Eins heißt gleiche Richtung, null heißt unabhängig. Empfehlungssysteme und semantische Suche sortieren so.')
K.say('proj', 'Projection',
      'A projection is the shadow one vector casts on the direction of another. Its length is the dot product divided by the length of the direction. What is left over is perpendicular to that direction.',
      'Projection वह छाया है जो एक vector दूसरे की दिशा पर डालता है। इसकी लंबाई dot product बटा दिशा की लंबाई है। बचा हुआ हिस्सा उस दिशा पर लंब है।',
      'Projection ಎಂದರೆ ಒಂದು vector ಇನ್ನೊಂದರ ದಿಕ್ಕಿನ ಮೇಲೆ ಬೀಳಿಸುವ ನೆರಳು. ಉಳಿದ ಭಾಗ ಆ ದಿಕ್ಕಿಗೆ ಲಂಬ.',
      'Projection ହେଉଛି ଗୋଟିଏ vector ଆରେକର ଦିଗରେ ପକାଉଥିବା ଛାଇ। ବାକି ଅଂଶ ସେହି ଦିଗ ପ୍ରତି ଲମ୍ବ।',
      'الإسقاط هو الظل الذي يلقيه متجه على اتجاه متجه آخر. طوله الضرب النقطي مقسومًا على طول الاتجاه، والجزء الباقي عمودي على ذلك الاتجاه.',
      'Eine Projektion ist der Schatten, den ein Vektor auf die Richtung eines anderen wirft. Ihre Länge ist das Skalarprodukt geteilt durch die Länge der Richtung. Der Rest steht senkrecht darauf.')
K.say('span', 'Span and basis',
      'The span is everywhere you can reach with linear combinations. Vectors are independent when none of them can be built from the others. A basis is the smallest set of independent vectors that reaches everything, and its size is the dimension.',
      'Span वह सब जगह है जहाँ linear combinations से पहुँच सकते हैं। Vectors independent हैं जब कोई भी बाकियों से नहीं बनता। Basis सबसे छोटा independent समूह है जो सब तक पहुँचे।',
      'Span ಎಂದರೆ linear combinations ನಿಂದ ತಲುಪಬಹುದಾದ ಎಲ್ಲ ಸ್ಥಳ. ಯಾವುದನ್ನೂ ಉಳಿದವುಗಳಿಂದ ರಚಿಸಲಾಗದಿದ್ದರೆ independent. Basis ಎಲ್ಲವನ್ನೂ ತಲುಪುವ ಅತಿ ಚಿಕ್ಕ independent ಗುಂಪು.',
      'Span ହେଉଛି linear combinations ରେ ପହଞ୍ଚିପାରୁଥିବା ସବୁ ସ୍ଥାନ। କୌଣସି vector ବାକିରୁ ତିଆରି ନହେଲେ independent। Basis ସବୁଠୁ ଛୋଟ independent ସମୂହ।',
      'الامتداد هو كل مكان نصله بالتراكيب الخطية. تكون المتجهات مستقلة عندما لا يمكن بناء أي منها من البقية. والأساس أصغر مجموعة مستقلة تصل إلى كل شيء، وعددها هو البعد.',
      'Der Spann ist alles, was man mit Linearkombinationen erreicht. Vektoren sind unabhängig, wenn sich keiner aus den anderen bauen lässt. Eine Basis ist die kleinste unabhängige Menge, die alles erreicht, und ihre Größe ist die Dimension.')
K.say('practice', 'Practice',
      'Practice time. Find the nearest shop, rank documents for a search, make two vectors perpendicular, and build a tiny nearest neighbour classifier. Every solution is written in four languages.',
      'अभ्यास का समय। सबसे पास की दुकान खोजें, search के लिए documents को rank करें, दो vectors को लंब बनाएँ, और एक छोटा nearest neighbour classifier बनाएँ।',
      'ಅಭ್ಯಾಸದ ಸಮಯ. ಹತ್ತಿರದ ಅಂಗಡಿ ಹುಡುಕಿ, documents rank ಮಾಡಿ, ಎರಡು vectors ಲಂಬ ಮಾಡಿ, ಸಣ್ಣ nearest neighbour classifier ರಚಿಸಿ.',
      'ଅଭ୍ୟାସ ସମୟ। ନିକଟତମ ଦୋକାନ ଖୋଜନ୍ତୁ, documents rank କରନ୍ତୁ, ଦୁଇ vectors ଲମ୍ବ କରନ୍ତୁ, ଏବଂ ଛୋଟ nearest neighbour classifier ତିଆରି କରନ୍ତୁ।',
      'وقت التدريب. أوجد أقرب متجر، ورتب المستندات لبحث ما، واجعل متجهين متعامدين، وابنِ مصنفًا صغيرًا لأقرب الجيران.',
      'Zeit zum Üben. Finde den nächsten Laden, sortiere Dokumente für eine Suche, mache zwei Vektoren senkrecht und baue einen kleinen Nächste Nachbarn Klassifikator.')

# ---------------------------------------------------------------- practice
K.practice('nearest-shop', 'e', 'Which shop is nearest', 'p_nearest',
           '<p>Home is at [3, 3]. Shops are at A [1, 5], B [4, 4], C [6, 1] and D [2, 2]. Print each straight line distance and the nearest shop.</p>',
           'A: 2.828\nB: 1.414\nC: 3.606\nD: 1.414\nnearest shop: B',
           'Distance is the length of the difference vector.',
           '<p>For each shop compute √((x − 3)² + (y − 3)²) and keep the smallest. B and D are tied at √2 ≈ 1.414, and the loop keeps the first one it meets with the strict test d &lt; best, so B wins. Real systems break ties on purpose, for example by rating.</p>',
           'O(n · d)', 'O(1)')
K.practice('rank-docs', 'm', 'Rank documents for a search', 'p_rank',
           '<p>Three news articles are word count vectors over the words goal, match, vote and price. Rank them for the search "goal match" by cosine similarity.</p>',
           '0.994  sports news\n0.115  election news\n0.000  market news',
           'Turn the query into a vector over the same four words.',
           '<p>The query is [1, 1, 0, 0]. Sports news [5, 4, 0, 0] points almost the same way: (5 + 4) ÷ (√2 × √41) ≈ 0.994. Election news shares only the word match once. Market news shares nothing, so its dot product is 0. This bag of words idea is the ancestor of modern embedding search.</p>',
           'O(n · d + n log n)', 'O(n)')
K.practice('gram-schmidt', 'h', 'Make two vectors perpendicular', 'p_gram',
           '<p>Start with v₁ = [3, 1] and v₂ = [2, 2]. Keep v₁ and replace v₂ by v₂ minus its projection on v₁. Check that the dot product of the result with v₁ is zero, allowing for rounding.</p>',
           'u1 = [3.00, 1.00]\nu2 = [-0.40, 1.20]\nu1 . u2 is zero: True',
           'Projection of v₂ on v₁ is (v₂ · v₁ ÷ v₁ · v₁) v₁.',
           '<p>v₂ · v₁ = 6 + 2 = 8 and v₁ · v₁ = 10, so the shadow is 0.8 × [3, 1] = [2.4, 0.8]. Subtracting leaves [−0.4, 1.2], which is perpendicular to [3, 1] because −1.2 + 1.2 = 0. Repeating this for more vectors is the <b>Gram Schmidt process</b>, the idea behind QR decomposition.</p>',
           'O(d)', 'O(d)')
K.practice('knn', 'x', 'A k nearest neighbours classifier', 'p_knn',
           '<p>Six people are labelled S (small size) or L (large size) from [height, weight]. Classify a new person [165, 66] by a vote among the 3 nearest.</p>',
           '[170, 72] L 7.81\n[160, 58] S 9.43\n[175, 75] L 13.45\nprediction: L',
           'Sort the people by distance to [165, 66], take the first three, count the labels.',
           '<p>k nearest neighbours does no training at all. It stores the data and, for each question, finds the closest examples. Two of the three nearest are L, so the answer is L. Because the distances mix centimetres and kilograms, scaling the features first would make the comparison fairer.</p>',
           'O(n · d + n log n)', 'O(n)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What is [2, 5] + [3, −1]?', ['[5, 4]', '[6, −5]', '[5, 6]', '[−1, 6]'], 0, 'Add matching parts.', '2 + 3 = 5 and 5 + (−1) = 4.')
K.quiz('e', 'What is the length of [6, 8]?', ['14', '10', '48', '100'], 1, 'Pythagoras: √(6² + 8²).', '√(36 + 64) = √100 = 10.')
K.quiz('e', 'What is 3 × [2, −4]?', ['[6, −12]', '[5, −1]', '[6, 12]', '[2, −12]'], 0, 'Multiply every part.', '3 × 2 = 6 and 3 × (−4) = −12.')
K.quiz('e', 'The dot product of two vectors is 0. They are', ['the same', 'opposite', 'perpendicular', 'equal in length'], 2, 'cos 90° = 0.', 'A zero dot product means the angle is 90°, so the vectors are orthogonal.')
K.quiz('e', 'A photo of 28 × 28 grey pixels as a vector has how many components?', ['56', '28', '784', '1568'], 2, 'One number per pixel.', '28 × 28 = 784.')
K.quiz('m', 'What is [1, 2, 3] · [4, 0, −1]?', ['1', '3', '7', '4'], 0, 'Multiply matching parts, then add.', '4 + 0 − 3 = 1.')
K.quiz('m', 'Cosine similarity between [1, 1] and [5, 5] is', ['0', '0.5', '1', '5'], 2, 'Do they point the same way?', '[5, 5] = 5 × [1, 1], same direction, so the cosine is 1. Cosine ignores length.')
K.quiz('m', 'What is the L1 norm of [−3, 4, −1]?', ['8', '0', '√26', '4'], 0, 'Add absolute values.', '3 + 4 + 1 = 8.')
K.quiz('m', 'Which pair is linearly dependent?', ['[1, 0] and [0, 1]', '[2, 3] and [4, 6]', '[1, 2] and [2, 1]', '[1, 1] and [1, −1]'], 1, 'Is one a multiple of the other?', '[4, 6] = 2 × [2, 3], so they lie on one line.')
K.quiz('m', 'Why scale features before using distances?', ['To make the code faster', 'So one large unit feature does not dominate the distance', 'Because distances must be below 1', 'To remove negative numbers'], 1, 'Think of salary next to age.', 'A feature measured in big numbers swamps the rest. Scaling puts all features on a fair footing.')
K.quiz('h', 'The projection of [4, 3] onto [1, 0] is', ['[4, 0]', '[0, 3]', '[4, 3]', '[1, 0]'], 0, 'Projecting onto the x axis keeps only the x part.', '([4, 3] · [1, 0]) ÷ ([1, 0] · [1, 0]) = 4, so 4 × [1, 0] = [4, 0].')
K.quiz('h', 'How many vectors are in any basis of ℝ⁵?', ['4', '5', '10', 'It depends'], 1, 'The dimension equals the size of every basis.', 'All bases of ℝ⁵ have exactly 5 independent vectors.')
K.quiz('h', 'Two unit vectors have dot product 0.5. The angle between them is', ['30°', '45°', '60°', '90°'], 2, 'For unit vectors the dot product is cos θ.', 'cos θ = 0.5 gives θ = 60°.')
K.quiz('x', 'If ‖a‖ = 3, ‖b‖ = 4 and a · b = 0, what is ‖a + b‖?', ['7', '5', '1', '12'], 1, 'Perpendicular vectors make a right angled triangle.', '‖a + b‖² = ‖a‖² + 2 a · b + ‖b‖² = 9 + 0 + 16 = 25, so the length is 5.')
K.quiz('x', 'In attention, a query vector q is compared with key vectors by', ['adding them', 'their dot products', 'their L1 norms', 'subtracting them'], 1, 'Which operation measures agreement?', 'Attention scores are dot products q · k, usually divided by √d and passed through softmax.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Work out 2 × [3, −1] + [1, 4]. Give the second component.', '2', 'Scale first, then add part by part.', [
    'Scale: <span class="eq">2 × [3, −1] = [6, −2]</span>',
    'Add: <span class="eq">[6, −2] + [1, 4] = [6 + 1, −2 + 4] = [7, 2]</span>',
    'The second component is 2.',
], check=2 * -1 + 4)
K.calc('e', 'Find the length of v = [5, 12].', '13', 'Square, add, square root.', [
    'Square each part: <span class="eq">5² = 25 and 12² = 144</span>',
    'Add: <span class="eq">25 + 144 = 169</span>',
    'Square root: <span class="eq">√169 = 13</span>',
    'This is the famous 5, 12, 13 right angled triangle.',
], check=(5 ** 2 + 12 ** 2) ** 0.5)
K.calc('e', 'Compute [3, 2] · [4, 5].', '22', 'Multiply matching parts and add.', [
    'First parts: <span class="eq">3 × 4 = 12</span>',
    'Second parts: <span class="eq">2 × 5 = 10</span>',
    'Add: <span class="eq">12 + 10 = 22</span>',
], check=3 * 4 + 2 * 5)
K.calc('e', 'How far apart are the points (1, 1) and (4, 5)?', '5', 'Subtract to get the difference vector, then find its length.', [
    'Difference: <span class="eq">(4 − 1, 5 − 1) = (3, 4)</span>',
    'Length: <span class="eq">√(3² + 4²) = √(9 + 16) = √25</span>',
    'Distance: <span class="eq">5</span>',
], check=5)
K.calc('m', 'Find the unit vector in the direction of [6, 8]. Give its first component.', '0.6', 'Divide every part by the length.', [
    'Length: <span class="eq">√(36 + 64) = √100 = 10</span>',
    'Divide: <span class="eq">[6 ÷ 10, 8 ÷ 10] = [0.6, 0.8]</span>',
    'Check the new length: √(0.36 + 0.64) = √1 = 1. ✔',
    'The first component is 0.6.',
], check=0.6)
K.calc('m', 'Find the angle in degrees between [1, 0] and [1, 1].', '45', 'cos θ = (a · b) ÷ (‖a‖ ‖b‖).', [
    'Dot product: <span class="eq">1 × 1 + 0 × 1 = 1</span>',
    'Lengths: <span class="eq">‖[1, 0]‖ = 1 and ‖[1, 1]‖ = √2</span>',
    'Cosine: <span class="eq">cos θ = 1 ÷ √2 ≈ 0.7071</span>',
    'Angle: <span class="eq">θ = cos⁻¹(0.7071) = 45°</span>',
], check=45, unit='degrees')
K.calc('m', 'Cosine similarity of [1, 2, 2] and [2, 1, 2]? Give a fraction or a decimal.', '8/9', 'Both vectors have length 3.', [
    'Dot product: <span class="eq">1 × 2 + 2 × 1 + 2 × 2 = 2 + 2 + 4 = 8</span>',
    'Lengths: <span class="eq">√(1 + 4 + 4) = 3</span> for both',
    'Cosine: <span class="eq">8 ÷ (3 × 3) = 8/9 ≈ 0.889</span>',
    'Close to 1, so the two vectors point in almost the same direction.',
], check='8/9', alt=['0.889', '0.8889', '0.89'])
K.calc('m', 'What is the L1 distance (Manhattan) between (2, 7) and (5, 3)?', '7', 'Add the absolute differences of each coordinate.', [
    'x difference: <span class="eq">|5 − 2| = 3</span>',
    'y difference: <span class="eq">|3 − 7| = 4</span>',
    'Add: <span class="eq">3 + 4 = 7</span> blocks',
    'For comparison, the straight line (L2) distance is √(9 + 16) = 5.',
], check=7)
K.calc('h', 'Find the vector projection of a = [3, 4] onto b = [2, 0]. Give its first component.', '3', 'proj = (a · b ÷ b · b) × b.', [
    'a · b: <span class="eq">3 × 2 + 4 × 0 = 6</span>',
    'b · b: <span class="eq">2 × 2 + 0 × 0 = 4</span>',
    'Scale factor: <span class="eq">6 ÷ 4 = 1.5</span>',
    'Projection: <span class="eq">1.5 × [2, 0] = [3, 0]</span>',
    'The first component is 3. The leftover [0, 4] is perpendicular to b.',
], check=3)
K.calc('h', 'For which value of k are [2, k] and [3, −6] perpendicular?', '1', 'Perpendicular means the dot product is 0.', [
    'Dot product: <span class="eq">2 × 3 + k × (−6) = 6 − 6k</span>',
    'Set it to zero: <span class="eq">6 − 6k = 0</span>',
    'Solve: <span class="eq">6k = 6, k = 1</span>',
    'Check: [2, 1] · [3, −6] = 6 − 6 = 0. ✔',
], check=1)
K.calc('h', 'Are [1, 2] and [3, 6] independent? Give the parallelogram area u₁v₂ − u₂v₁.', '0', 'If the area is 0, the vectors lie on one line.', [
    'Area: <span class="eq">1 × 6 − 2 × 3 = 6 − 6 = 0</span>',
    'An area of 0 means the parallelogram is flat.',
    'Indeed [3, 6] = 3 × [1, 2], so the two vectors are dependent and only span a line.',
], check=0)
K.calc('x', 'Write [7, 3] as a·[1, 1] + b·[1, −1]. What is a?', '5', 'Match each component and solve two equations.', [
    'Components: <span class="eq">a + b = 7</span> and <span class="eq">a − b = 3</span>',
    'Add the two equations: <span class="eq">2a = 10, a = 5</span>',
    'Then <span class="eq">b = 7 − 5 = 2</span>',
    'Check: 5·[1, 1] + 2·[1, −1] = [5 + 2, 5 − 2] = [7, 3]. ✔',
    'The numbers 5 and 2 are the coordinates of [7, 3] in this new basis.',
], check=5)
K.calc('x', 'If ‖a‖ = 5, ‖b‖ = 3 and the angle between them is 60°, what is a · b?', '7.5', 'a · b = ‖a‖ ‖b‖ cos θ, and cos 60° = 0.5.', [
    'Use the geometry form: <span class="eq">a · b = ‖a‖ ‖b‖ cos θ</span>',
    'Fill in: <span class="eq">5 × 3 × cos 60°</span>',
    'cos 60° is 0.5: <span class="eq">15 × 0.5 = 7.5</span>',
], check=7.5)

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { $, shell, seg, wireSeg, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;

  /* ----- drag two vectors: add, subtract, scale, dot product, projection ----- */
  W.vec2d = el => {
    const mode0 = el.dataset.mode || 'add';
    const b = shell(el, 'Drag the arrows', 'Drag the blue tip of a and the orange tip of b. Switch what to show, and read the numbers update live.');
    b.innerHTML = `<div class="vz-row">${seg('m', [['add', 'a + b'], ['sub', 'a − b'], ['scale', 'k · a'], ['dot', 'a · b and angle'], ['proj', 'projection of a on b']], mode0)}</div>
      <div class="mv-wrap"><div class="v2-plot"></div><div class="mv-side"><div class="v2-k">${slider('k', 'k', -2, 3, 1.5, 0.1)}</div><div class="mv-read v2-out" aria-live="polite"></div></div></div>`;
    const G = MV.frame(460, 460, [-6, 6], [-6, 6]);
    const A = [3, 2], B = [1, 3];
    let mode = mode0, k = 1.5;
    const host = $('.v2-plot', b);
    host.innerHTML = MV.svg(G, '<g class="v2-g"></g>', 'Two vectors');
    const svgEl = $('svg', host);
    const n = v => MV.num(v, 2), V = v => `[${n(v[0])}, ${n(v[1])}]`;
    function draw() {
      $('.v2-k', b).style.display = mode === 'scale' ? '' : 'none';
      let s = MV.axes(G, { labels: false });
      const out = [];
      const dot = A[0] * B[0] + A[1] * B[1], la = Math.hypot(...A), lb = Math.hypot(...B);
      if (mode === 'add') {
        const S = [A[0] + B[0], A[1] + B[1]];
        s += MV.arrow(G, A[0], A[1], S[0], S[1], 'o', 'dash') + MV.arrow(G, 0, 0, S[0], S[1], 'g');
        out.push(`a + b = ${V(A)} + ${V(B)} = <b>${V(S)}</b>`, 'The dashed orange copy of b starts at the tip of a. The green sum runs from the start to the end.');
      } else if (mode === 'sub') {
        const D = [A[0] - B[0], A[1] - B[1]];
        s += MV.arrow(G, B[0], B[1], A[0], A[1], 'g', 'dash') + MV.arrow(G, 0, 0, D[0], D[1], 'g');
        out.push(`a − b = <b>${V(D)}</b>`, `It is the arrow from the tip of b to the tip of a. Its length ${n(Math.hypot(...D))} is the distance between the two points.`);
      } else if (mode === 'scale') {
        const S = [k * A[0], k * A[1]];
        s += MV.arrow(G, 0, 0, S[0], S[1], 'g');
        out.push(`${n(k)} · a = <b>${V(S)}</b>`, k < 0 ? 'A negative k flips the arrow round.' : k < 1 ? 'k between 0 and 1 shrinks it.' : 'k above 1 stretches it.', `Length ${n(Math.abs(k) * la)} = |k| × ${n(la)}`);
      } else if (mode === 'dot') {
        const ang = Math.acos(Math.max(-1, Math.min(1, dot / (la * lb || 1)))) * 180 / Math.PI;
        const a1 = Math.atan2(A[1], A[0]), a2 = Math.atan2(B[1], B[0]);
        let d = a2 - a1; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI;
        const r = 1.1, pts = [];
        for (let t = 0; t <= 20; t++) { const th = a1 + d * t / 20; pts.push(`${G.sx(r * Math.cos(th))},${G.sy(r * Math.sin(th))}`); }
        s += `<polyline points="${pts.join(' ')}" class="mv-curve c4"/>`;
        out.push(`a · b = ${n(A[0])}×${n(B[0])} + ${n(A[1])}×${n(B[1])} = <span class="big">${n(dot)}</span>`, `‖a‖ = ${n(la)}, ‖b‖ = ${n(lb)}`, `cos θ = ${n(dot / (la * lb || 1))}, θ = <b>${MV.num(ang, 1)}°</b>`,
          Math.abs(dot) < 0.05 ? '⟂ Perpendicular: the dot product is zero.' : dot > 0 ? 'Positive: they point roughly the same way.' : 'Negative: they point roughly apart.');
      } else {
        const bb = B[0] * B[0] + B[1] * B[1] || 1, kk = dot / bb, P = [kk * B[0], kk * B[1]];
        s += MV.curve(G, x => Math.abs(B[0]) < 1e-9 ? NaN : B[1] / B[0] * x, 'thin dash c2');
        s += MV.line(G, A[0], A[1], P[0], P[1]) + MV.arrow(G, 0, 0, P[0], P[1], 'g');
        out.push(`proj of a on b = (${n(dot)} ÷ ${n(bb)}) × b = <b>${V(P)}</b>`, `shadow length = ${n(dot / Math.sqrt(bb))}`, `left over a − proj = ${V([A[0] - P[0], A[1] - P[1]])}, which is perpendicular to b.`);
      }
      s += MV.arrow(G, 0, 0, A[0], A[1], 'a') + MV.arrow(G, 0, 0, B[0], B[1], 'o');
      s += MV.text(G, A[0], A[1], 'a', { dx: 8, dy: -6 }) + MV.text(G, B[0], B[1], 'b', { dx: 8, dy: -6 });
      s += `<circle class="mv-pt big mv-drag" data-h="0" cx="${G.sx(A[0])}" cy="${G.sy(A[1])}" r="10"/><circle class="mv-pt o big mv-drag" data-h="1" cx="${G.sx(B[0])}" cy="${G.sy(B[1])}" r="10"/>`;
      $('.v2-g', svgEl).innerHTML = s;
      $('.v2-out', b).innerHTML = `a = ${V(A)}, b = ${V(B)}<br>` + out.join('<br>');
    }
    const snap = v => Math.round(v * 2) / 2;
    MV.drag(svgEl, G, [{ set: (x, y) => { A[0] = snap(x); A[1] = snap(y); } }, { set: (x, y) => { B[0] = snap(x); B[1] = snap(y); } }], draw);
    wireSeg(b, 'm', v => { mode = v; draw(); });
    wireSlider(b, 'k', v => { k = v; draw(); });
    draw();
  };

  /* ----- the unit circle of each norm ----- */
  W.norms = el => {
    const b = shell(el, 'What "length 1" looks like for each norm', 'Every point on a shape has norm 1. Drag the point and compare its L1, L2 and L∞ lengths.');
    b.innerHTML = `<div class="mv-wrap"><div class="nm-plot"></div><div class="mv-side"><div class="mv-legend"><span><i></i>L2 circle</span><span><i class="o"></i>L1 diamond</span><span><i class="g"></i>L∞ square</span></div><div class="mv-read nm-out" aria-live="polite"></div></div></div>`;
    const G = MV.frame(420, 420, [-2, 2], [-2, 2]);
    const P = [1.2, 0.8];
    const host = $('.nm-plot', b);
    host.innerHTML = MV.svg(G, '<g class="nm-g"></g>', 'Unit shapes of three norms');
    function draw() {
      const circ = [];
      for (let t = 0; t <= 64; t++) circ.push(`${G.sx(Math.cos(t / 32 * Math.PI))},${G.sy(Math.sin(t / 32 * Math.PI))}`);
      let s = MV.axes(G, { xstep: 0.5, ystep: 0.5 });
      s += `<polygon class="mv-poly g" points="${[[1, 1], [-1, 1], [-1, -1], [1, -1]].map(([x, y]) => G.sx(x) + ',' + G.sy(y)).join(' ')}"/>`;
      s += `<polygon class="mv-poly" points="${circ.join(' ')}"/>`;
      s += `<polygon class="mv-poly o" points="${[[1, 0], [0, 1], [-1, 0], [0, -1]].map(([x, y]) => G.sx(x) + ',' + G.sy(y)).join(' ')}"/>`;
      s += MV.arrow(G, 0, 0, P[0], P[1], 'p') + `<circle class="mv-pt p big mv-drag" data-h="0" cx="${G.sx(P[0])}" cy="${G.sy(P[1])}" r="10"/>`;
      $('.nm-g', $('svg', host)).innerHTML = s;
      const l2 = Math.hypot(...P), l1 = Math.abs(P[0]) + Math.abs(P[1]), li = Math.max(Math.abs(P[0]), Math.abs(P[1]));
      $('.nm-out', b).innerHTML = `v = [${MV.num(P[0])}, ${MV.num(P[1])}]<br>L2 = √(${MV.num(P[0])}² + ${MV.num(P[1])}²) = <b>${MV.num(l2, 3)}</b><br>L1 = |${MV.num(P[0])}| + |${MV.num(P[1])}| = <b>${MV.num(l1, 3)}</b><br>L∞ = max = <b>${MV.num(li, 3)}</b><br>Always L∞ ≤ L2 ≤ L1. The pointy corners of the L1 diamond are why L1 regularisation pushes weights to exactly zero.`;
    }
    MV.drag($('svg', host), G, [{ set: (x, y) => { P[0] = Math.round(x * 10) / 10; P[1] = Math.round(y * 10) / 10; } }], draw);
    draw();
  };

  /* ----- your taste vector against four movies ----- */
  W.cossim = el => {
    const b = shell(el, 'A tiny movie recommender', 'Set how much you like action, comedy and romance. The bars show the cosine similarity between your taste vector and each movie.');
    const M = [['🚀 Rocket Race', [9, 2, 1]], ['😂 Laugh Out', [1, 9, 3]], ['💕 Love in Goa', [1, 3, 9]], ['🚗 Car Chase 2', [8, 3, 2]], ['🎭 Rom Com Night', [1, 7, 7]]];
    b.innerHTML = `<div class="mv-wrap"><div class="mv-bars cs-bars"></div><div class="mv-side">${slider('a', '💥 action', 0, 10, 7)}${slider('c', '😂 comedy', 0, 10, 2)}${slider('r', '💕 romance', 0, 10, 1)}<div class="mv-read cs-out" aria-live="polite"></div></div></div>`;
    const you = { a: 7, c: 2, r: 1 };
    const cos = (u, v) => { const d = u.reduce((s, x, i) => s + x * v[i], 0), nu = Math.hypot(...u), nv = Math.hypot(...v); return nu && nv ? d / (nu * nv) : 0; };
    function draw() {
      const u = [you.a, you.c, you.r];
      const sc = M.map(([nm, v]) => [nm, v, cos(u, v)]).sort((x, y) => y[2] - x[2]);
      $('.cs-bars', b).innerHTML = sc.map(([nm, v, c], i) => `<div class="mv-brow" style="grid-template-columns:140px 1fr 56px"><span>${nm}</span><span class="tr"><i class="${i ? '' : 'g'}" style="width:${Math.max(0, c) * 100}%"></i></span><b>${MV.num(c, 3)}</b></div>`).join('');
      $('.cs-out', b).innerHTML = Math.hypot(...u) ? `You = [${u.join(', ')}]<br>Top pick: <b>${sc[0][0]}</b> [${sc[0][1].join(', ')}]<br>Try doubling every slider: the scores do not change, because cosine only compares directions.` : 'Set at least one slider above 0. A zero vector has no direction.';
    }
    ['a', 'c', 'r'].forEach(k => wireSlider(b, k, v => { you[k] = v; draw(); }));
    draw();
  };
})();
'''

CSS = r'''
@media (max-width:560px){ .cossim .mv-brow{grid-template-columns:110px 1fr 50px !important} }
'''

# ---------------------------------------------------------------- deeper explanations and extra animations
# Each lesson above gives the short version. DEEPER adds a slower, fuller explanation (and sometimes an
# animation) to the end of the lesson with the same id.
DEEPER = {
    'what': deep('vectors as they appear in real code and data', f'''
<p>When you start writing machine learning code, vectors show up in a few standard shapes. Knowing their names saves a lot of confusion.</p>
{table(['Kind of vector', 'What it looks like', 'Example'], [
        ['feature vector', 'one number per measured property', '[area 85, rooms 2, age 12] for one flat'],
        ['one hot vector', 'all zeros except a single 1', 'colour "green" out of [red, green, blue] is [0, 1, 0]'],
        ['embedding', 'a few hundred learned numbers, no single one has an obvious meaning', 'a 768 number vector for the word "river"'],
        ['probability vector', 'non negative numbers that add up to 1', 'a classifier output [0.7, 0.2, 0.1]'],
        ['weight vector', 'one learned number per input', 'the slopes of a linear model'],
    ])}
<p>A <b>one hot</b> vector is how a model reads a category. You cannot feed the word "green" into a formula, and numbering colours 1, 2, 3 would wrongly say blue is "bigger" than red. Giving each category its own position with a single 1 keeps every category equally far from every other.</p>
<p>In code, a vector of n numbers usually has <b>shape (n,)</b>. Libraries also talk about a <b>row vector</b> of shape (1, n) and a <b>column vector</b> of shape (n, 1). They hold the same numbers but behave differently in matrix multiplication (Chapter 4), so mixing them up is one of the most common beginner bugs.</p>
{life('A cricket player profile is a vector: [matches, runs, average, strike rate, wickets]. Two players with similar vectors have similar careers, which is exactly how sports apps suggest "players like this one".')}
'''),
    'ops': deep('the average of vectors and sliding between two vectors', f'''
<p>Adding and scaling are enough to build two of the most useful tools in all of machine learning.</p>
{fxs(fx('Centroid (average vector)', f'c = {frac(1, "n")} (v₁ + v₂ + … + vₙ)', 'Add the vectors, then scale by 1 ÷ n. The result sits in the middle of the cloud of points.'),
         fx('Interpolation (lerp)', 'v(t) = (1 − t) a + t b, &nbsp; 0 ≤ t ≤ 1', 't = 0 gives a, t = 1 gives b, t = ½ gives the halfway point. Every point in between lies on the straight segment from a to b.'))}
{worked('Centroid of three customers', [
        'Customers as [age, visits per month]: <span class="eq">[20, 4], [30, 2], [40, 9]</span>',
        'Add them part by part: <span class="eq">[20 + 30 + 40, 4 + 2 + 9] = [90, 15]</span>',
        'Scale by 1 ÷ 3: <span class="eq">[30, 5]</span>',
        'The "typical" customer of this group is 30 years old and visits 5 times a month. k means clustering (a popular grouping method) moves each cluster centre to exactly this average, over and over.'])}
<p>Interpolation is how image generators "morph" one face into another. Each face is a vector of numbers inside the model, and stepping t from 0 to 1 walks along the straight line between them. Every step is a new face that blends the two.</p>
{trick('Vector rules are the same as number rules you already know: a + b = b + a, (a + b) + c = a + (b + c), and k(a + b) = ka + kb. If a step would be fine with ordinary numbers, it is almost always fine with vectors of the same size.')}
'''),
    'norm': deep('the whole family of norms, and when to normalise', f'''
<p>L1 and L2 are two members of one family, the <b>Lp norms</b>. Raise every absolute value to the power p, add, then take the p-th root.</p>
{fx('Lp norm', '‖v‖ₚ = (|v₁|ᵖ + |v₂|ᵖ + … + |vₙ|ᵖ)^(1/p)', 'p = 1 gives Manhattan, p = 2 gives Euclidean, and as p grows huge the biggest component wins, giving L∞ = max |vᵢ|.')}
{worked('All three norms of v = [3, −4, 12]', [
        'L1: <span class="eq">3 + 4 + 12 = 19</span>',
        'L2: <span class="eq">√(9 + 16 + 144) = √169 = 13</span>',
        'L∞: the biggest absolute part, <span class="eq">12</span>',
        'Always <span class="eq">L∞ ≤ L2 ≤ L1</span>: here 12 ≤ 13 ≤ 19. The more evenly the size is spread over the parts, the bigger the gap.'])}
<p>Machine learning often uses the <b>squared</b> L2 norm, ‖v‖² = v₁² + … + vₙ², without the square root. It has the same smallest point, it is cheaper to compute, and its derivative is simply 2v, which makes the calculus in later chapters tidy.</p>
<p><b>When to normalise.</b> Divide a vector by its length when only the direction matters, for example text embeddings for search, where a long document should not win just because it has more words. Do not normalise when the size itself carries meaning, such as a vector of prices or sensor readings.</p>
'''),
    'dot': deep('why the two formulas for the dot product agree', f'''
<p>It is surprising that "multiply and add" gives the same number as "length times length times cos of the angle". Here is why, using only Pythagoras and the law of cosines from school geometry.</p>
{worked('Linking the algebra form and the geometry form', [
        'Draw a, b and the third side a − b of the triangle they make.',
        'Law of cosines: <span class="eq">‖a − b‖² = ‖a‖² + ‖b‖² − 2‖a‖‖b‖cos θ</span>',
        'Expand the left side part by part: <span class="eq">Σ(aᵢ − bᵢ)² = Σaᵢ² + Σbᵢ² − 2Σaᵢbᵢ</span>',
        'That is <span class="eq">‖a‖² + ‖b‖² − 2(a · b)</span>',
        'The two right sides must be equal, so <span class="eq">a · b = ‖a‖‖b‖cos θ</span>'])}
<p>Two more facts make the dot product easy to work with.</p>
<ul>
<li><b>A vector dotted with itself is its squared length:</b> v · v = ‖v‖². So [3, 4] · [3, 4] = 9 + 16 = 25 = 5².</li>
<li><b>It is a weighted sum.</b> If w = [0.5, 2, −1] are weights and x = [4, 1, 3] are inputs, w · x = 2 + 2 − 3 = 1. Each input is counted with its own importance, and a negative weight means "this feature lowers the score".</li>
</ul>
{life('Your shopping bill is a dot product: quantities [2 kg rice, 1 litre oil, 6 eggs] dotted with prices [60, 150, 7] gives 120 + 150 + 42 = 312.')}
'''),
    'cosine': deep('cosine distance, and when cosine and Euclidean disagree', f'''
<p>Many libraries ask for a <b>distance</b>, where smaller means more alike. Cosine similarity is turned into one by subtracting it from 1.</p>
{fx('Cosine distance', '1 − cos(a, b)', '0 for the same direction, 1 for perpendicular, 2 for opposite.')}
{worked('Two documents as word counts', [
        'Words [ball, goal, vote]. Document A = <span class="eq">[3, 2, 0]</span>, document B (twice as long, same topic) = <span class="eq">[6, 4, 0]</span>, document C = <span class="eq">[0, 1, 5]</span>',
        'A · B = <span class="eq">18 + 8 + 0 = 26</span>, ‖A‖ = √13 ≈ 3.606, ‖B‖ = √52 ≈ 7.211, so cos(A, B) = <span class="eq">26 ÷ 26 = 1</span>',
        'A · C = <span class="eq">0 + 2 + 0 = 2</span>, ‖C‖ = √26 ≈ 5.099, so cos(A, C) = <span class="eq">2 ÷ (3.606 × 5.099) ≈ 0.109</span>',
        'Euclidean distance says A is far from B (‖A − B‖ = √13 ≈ 3.61) only because B is longer. Cosine correctly says A and B are about exactly the same topic.'])}
<p>Rule of thumb: use <b>cosine</b> when size is an accident (document length, how many ratings a user gave) and <b>Euclidean</b> when size is real information (two houses with very different areas really are different).</p>
'''),
    'proj': deep('splitting a vector into "along" and "across"', f'''
<p>Projection lets you split any vector a into two pieces that are perpendicular to each other: the part that runs along a direction b, and the part that is left over. This split is used again and again, in regression, in PCA and in the Gram Schmidt method of Chapter 13.</p>
{fx('Decomposition', 'a = proj_b a + (a − proj_b a)', 'The first piece is parallel to b. The second piece is perpendicular to b, so its dot product with b is 0.')}
{worked('Split a = [4, 3] along b = [2, 0]', [
        'a · b = <span class="eq">4 × 2 + 3 × 0 = 8</span> and b · b = <span class="eq">4</span>',
        'proj_b a = <span class="eq">(8 ÷ 4) × [2, 0] = [4, 0]</span>',
        'Left over: <span class="eq">[4, 3] − [4, 0] = [0, 3]</span>',
        'Check it is perpendicular: <span class="eq">[0, 3] · [2, 0] = 0</span> ✓',
        'So a = [4, 0] + [0, 3]: 4 steps along b, 3 steps straight across it.'])}
<p>If b is already a <b>unit</b> vector (length 1), the formula becomes very short: proj_b a = (a · b) b. That is why so many algorithms normalise directions first.</p>
{life('Walking up a slope against the wind, only the part of the wind that blows straight down the slope slows you. The part blowing across the slope just pushes you sideways. That split is a projection.')}
'''),
    'span': deep('drag two vectors and see what they can reach', f'''
<p>The best way to feel span and independence is to play. Below, a and b are the two building blocks. The faint grid shows every point you can reach with whole number amounts of a and b, such as 2a − b. Type a target and the widget works out exactly how much of a and b you need, using the two equation method from Chapter 1.</p>
{viz('span2d')}
<p>Drag b until it lies on the same line as a. The grid collapses onto a single line, the "area number" ad − bc becomes 0, and most targets can no longer be reached. That is linear dependence in one picture: two vectors that only reach a line instead of the whole plane.</p>
{ml('In a dataset, if one column is (almost) a multiple of another, the data matrix behaves like the collapsed grid. The model cannot tell the two features apart, and their weights can swing wildly from one training run to the next. Dropping one of the pair, or adding L2 regularisation, fixes it.')}
'''),
}
for _p in PARTS:
    _p['html'] += DEEPER.get(_p['id'], '')

VIZ_JS += r'''
(() => {
  const { $, shell, Player } = VIZ.kit;
  const W = VIZ.widgets;

  /* ----- span of two draggable vectors, with a target written as x·a + y·b ----- */
  W.span2d = el => {
    const b = shell(el, 'What can a and b reach?', 'Drag the tips of a (blue) and b (orange). Set a target and press Play to build it step by step: first the a part, then the b part.');
    b.innerHTML = `<div class="mv-wrap"><div class="sp-plot"></div><div class="mv-side"><div class="mv-inp">target [<input type="number" class="sp-tx" value="4" step="0.5" aria-label="target x">, <input type="number" class="sp-ty" value="3" step="0.5" aria-label="target y">]</div><div class="mv-read sp-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const G = MV.frame(440, 440, [-6, 6], [-6, 6]);
    const A = [2, 1], B = [-1, 2], T = [4, 3];
    let stage = 2;
    const host = $('.sp-plot', b);
    host.innerHTML = MV.svg(G, '<g class="sp-g"></g>', 'Span of two vectors');
    const svgEl = $('svg', host);
    const n = v => MV.num(v, 2), V = v => `[${n(v[0])}, ${n(v[1])}]`;
    function draw() {
      let s = MV.axes(G, { labels: false });
      const det = A[0] * B[1] - A[1] * B[0];
      for (let i = -6; i <= 6; i++) {
        s += MV.line(G, i * B[0] - 8 * A[0], i * B[1] - 8 * A[1], i * B[0] + 8 * A[0], i * B[1] + 8 * A[1], 'mv-grid');
        s += MV.line(G, i * A[0] - 8 * B[0], i * A[1] - 8 * B[1], i * A[0] + 8 * B[0], i * A[1] + 8 * B[1], 'mv-grid');
      }
      const out = [`a = ${V(A)}, b = ${V(B)}`, `area number ad − bc = <b>${n(det)}</b>`];
      s += MV.dot(G, T[0], T[1], 'r', 6) + MV.text(G, T[0], T[1], 'target', { dx: 8, dy: 14, cls: 'sm' });
      if (Math.abs(det) < 1e-9) {
        out.push('❌ a and b lie on one line (dependent). They only reach that line, not the whole plane.');
        const on = Math.abs(A[0] * T[1] - A[1] * T[0]) < 1e-9 && Math.abs(B[0] * T[1] - B[1] * T[0]) < 1e-9;
        out.push(on ? 'The target happens to lie on that line, so it can be reached in many ways.' : 'The target is off that line, so it cannot be reached.');
      } else {
        const x = (T[0] * B[1] - T[1] * B[0]) / det, y = (A[0] * T[1] - A[1] * T[0]) / det;
        const P = [x * A[0], x * A[1]];
        if (stage >= 1) s += MV.arrow(G, 0, 0, P[0], P[1], 'a', 'dash');
        if (stage >= 2) s += MV.arrow(G, P[0], P[1], T[0], T[1], 'o', 'dash');
        out.push('✅ independent: together they reach every point of the plane.', `target = <b>${n(x)}</b> · a + <b>${n(y)}</b> · b`);
        if (stage >= 1) out.push(`step 1: ${n(x)} · a = ${V(P)}`);
        if (stage >= 2) out.push(`step 2: add ${n(y)} · b = ${V([y * B[0], y * B[1]])} to land on ${V(T)}`);
      }
      s += MV.arrow(G, 0, 0, A[0], A[1], 'a') + MV.arrow(G, 0, 0, B[0], B[1], 'o');
      s += `<circle class="mv-pt big mv-drag" data-h="0" cx="${G.sx(A[0])}" cy="${G.sy(A[1])}" r="10"/><circle class="mv-pt o big mv-drag" data-h="1" cx="${G.sx(B[0])}" cy="${G.sy(B[1])}" r="10"/>`;
      $('.sp-g', svgEl).innerHTML = s;
      $('.sp-out', b).innerHTML = out.join('<br>');
    }
    const snap = v => Math.round(v * 2) / 2;
    MV.drag(svgEl, G, [{ set: (x, y) => { A[0] = snap(x); A[1] = snap(y); } }, { set: (x, y) => { B[0] = snap(x); B[1] = snap(y); } }], draw);
    const P = Player($('.vz-p', b), t => { stage = t; draw(); }, 1100);
    const readT = () => { T[0] = +$('.sp-tx', b).value || 0; T[1] = +$('.sp-ty', b).value || 0; draw(); };
    $('.sp-tx', b).addEventListener('input', readT);
    $('.sp-ty', b).addEventListener('input', readT);
    P.load(3, 2);
  };
})();
'''

T = K.topic(
    slug='vectors', topic='vectors', prefix='mm03', short='Vectors', emoji='➡️',
    title='Vectors',
    module=('🧮', 'Linear algebra', 'linear-algebra', 'Vectors, matrices, eigenvalues, SVD and PCA: the maths that lets a model handle thousands of numbers at once.'),
    minutes=50,
    lead='Vectors are lists of numbers and arrows at the same time. Add and scale them, measure their length, compare them with the dot product and cosine similarity, cast shadows with projections, and learn what span, independence and a basis mean.',
    desc='Vectors for machine learning: addition, scaling, norms, distance, dot product, cosine similarity, projection, span, linear independence and basis.',
    summary='Feature vectors and embeddings, adding and scaling, L1, L2 and L infinity norms, unit vectors and distances, the dot product and the angle between vectors, cosine similarity for recommendations and search, projections, span, independence and basis.',
    keywords=['vector', 'feature vector', 'embedding', 'norm', 'L1 norm', 'L2 norm', 'unit vector', 'euclidean distance', 'dot product', 'cosine similarity', 'projection', 'span', 'linear independence', 'basis', 'k nearest neighbours'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
