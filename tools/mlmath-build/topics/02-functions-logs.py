# Chapter 2: functions, straight lines, quadratics, exponentials, logarithms, activation functions,
# composition and inverses.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz, deep

K = Kit()

# ---------------------------------------------------------------- programs
K.code('line_fn', py=r'''
def f(x):
    return 2 * x + 1          # slope 2, intercept 1


for x in [0, 1, 2, 3]:
    print(f"f({x}) = {f(x)}")

# slope from two points (1, 3) and (4, 9)
x1, y1, x2, y2 = 1, 3, 4, 9
m = (y2 - y1) / (x2 - x1)
b = y1 - m * x1
print(f"slope m = {m:.1f}, intercept b = {b:.1f}")
''', js=r'''
function f(x) {
  return 2 * x + 1;           // slope 2, intercept 1
}

for (const x of [0, 1, 2, 3]) {
  console.log(`f(${x}) = ${f(x)}`);
}

// slope from two points (1, 3) and (4, 9)
const [x1, y1, x2, y2] = [1, 3, 4, 9];
const m = (y2 - y1) / (x2 - x1);
const b = y1 - m * x1;
console.log(`slope m = ${m.toFixed(1)}, intercept b = ${b.toFixed(1)}`);
''', ts=r'''
function f(x: number): number {
  return 2 * x + 1;           // slope 2, intercept 1
}

for (const x of [0, 1, 2, 3]) {
  console.log(`f(${x}) = ${f(x)}`);
}

// slope from two points (1, 3) and (4, 9)
const [x1, y1, x2, y2]: number[] = [1, 3, 4, 9];
const m: number = (y2 - y1) / (x2 - x1);
const b: number = y1 - m * x1;
console.log(`slope m = ${m.toFixed(1)}, intercept b = ${b.toFixed(1)}`);
''', java=r'''
public class LineFn {
    static int f(int x) {
        return 2 * x + 1;           // slope 2, intercept 1
    }

    public static void main(String[] args) {
        for (int x : new int[]{0, 1, 2, 3}) {
            System.out.println("f(" + x + ") = " + f(x));
        }
        // slope from two points (1, 3) and (4, 9)
        double x1 = 1, y1 = 3, x2 = 4, y2 = 9;
        double m = (y2 - y1) / (x2 - x1);
        double b = y1 - m * x1;
        System.out.println(String.format("slope m = %.1f, intercept b = %.1f", m, b));
    }
}
''')

K.code('quadratic', py=r'''
import math


def roots(a, b, c):
    d = b * b - 4 * a * c            # the discriminant
    print(f"{a}x^2 + {b}x + {c}: discriminant = {d}")
    if d < 0:
        return []
    r = math.sqrt(d)
    return [(-b - r) / (2 * a), (-b + r) / (2 * a)]


print("roots:", [f"{x:.2f}" for x in roots(1, -5, 6)])
print("roots:", [f"{x:.2f}" for x in roots(1, 2, 5)])
vx = 5 / 2                           # vertex at x = -b / 2a
print(f"lowest point of x^2 - 5x + 6 is at x = {vx:.2f}, y = {vx * vx - 5 * vx + 6:.2f}")
''', js=r'''
function roots(a, b, c) {
  const d = b * b - 4 * a * c;       // the discriminant
  console.log(`${a}x^2 + ${b}x + ${c}: discriminant = ${d}`);
  if (d < 0) return [];
  const r = Math.sqrt(d);
  return [(-b - r) / (2 * a), (-b + r) / (2 * a)];
}

const show = xs => "[" + xs.map(x => `'${x.toFixed(2)}'`).join(", ") + "]";
console.log("roots:", show(roots(1, -5, 6)));
console.log("roots:", show(roots(1, 2, 5)));
const vx = 5 / 2;                    // vertex at x = -b / 2a
console.log(`lowest point of x^2 - 5x + 6 is at x = ${vx.toFixed(2)}, y = ${(vx * vx - 5 * vx + 6).toFixed(2)}`);
''', ts=r'''
function roots(a: number, b: number, c: number): number[] {
  const d: number = b * b - 4 * a * c;  // the discriminant
  console.log(`${a}x^2 + ${b}x + ${c}: discriminant = ${d}`);
  if (d < 0) return [];
  const r: number = Math.sqrt(d);
  return [(-b - r) / (2 * a), (-b + r) / (2 * a)];
}

const show = (xs: number[]): string => "[" + xs.map(x => `'${x.toFixed(2)}'`).join(", ") + "]";
console.log("roots:", show(roots(1, -5, 6)));
console.log("roots:", show(roots(1, 2, 5)));
const vx: number = 5 / 2;            // vertex at x = -b / 2a
console.log(`lowest point of x^2 - 5x + 6 is at x = ${vx.toFixed(2)}, y = ${(vx * vx - 5 * vx + 6).toFixed(2)}`);
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class Quadratic {
    static List<String> roots(int a, int b, int c) {
        int d = b * b - 4 * a * c;          // the discriminant
        System.out.println(a + "x^2 + " + b + "x + " + c + ": discriminant = " + d);
        List<String> out = new ArrayList<>();
        if (d < 0) return out;
        double r = Math.sqrt(d);
        out.add("'" + String.format("%.2f", (-b - r) / (2 * a)) + "'");
        out.add("'" + String.format("%.2f", (-b + r) / (2 * a)) + "'");
        return out;
    }

    public static void main(String[] args) {
        System.out.println("roots: " + roots(1, -5, 6));
        System.out.println("roots: " + roots(1, 2, 5));
        double vx = 5 / 2.0;                // vertex at x = -b / 2a
        System.out.println(String.format("lowest point of x^2 - 5x + 6 is at x = %.2f, y = %.2f", vx, vx * vx - 5 * vx + 6));
    }
}
''')

K.code('euler', py=r'''
# 1 rupee at 100% interest for one year, added n times a year
for n in [1, 2, 12, 365, 1000000]:
    value = (1 + 1 / n) ** n
    print(f"n = {n:>7}: {value:.6f}")
print(f"e       = {2.718281828459045:.6f}")
''', js=r'''
// 1 rupee at 100% interest for one year, added n times a year
for (const n of [1, 2, 12, 365, 1000000]) {
  const value = (1 + 1 / n) ** n;
  console.log(`n = ${String(n).padStart(7)}: ${value.toFixed(6)}`);
}
console.log(`e       = ${Math.E.toFixed(6)}`);
''', ts=r'''
// 1 rupee at 100% interest for one year, added n times a year
for (const n of [1, 2, 12, 365, 1000000]) {
  const value: number = (1 + 1 / n) ** n;
  console.log(`n = ${String(n).padStart(7)}: ${value.toFixed(6)}`);
}
console.log(`e       = ${Math.E.toFixed(6)}`);
''', java=r'''
public class Euler {
    public static void main(String[] args) {
        // 1 rupee at 100% interest for one year, added n times a year
        for (int n : new int[]{1, 2, 12, 365, 1000000}) {
            double value = Math.pow(1 + 1.0 / n, n);
            System.out.println(String.format("n = %7d: %.6f", n, value));
        }
        System.out.println(String.format("e       = %.6f", Math.E));
    }
}
''')

K.code('logs', py=r'''
import math

print(f"log2(8)     = {math.log2(8):.1f}")
print(f"log10(1000) = {math.log10(1000):.1f}")
print(f"ln(e)       = {math.log(math.e):.1f}")
# product rule: log(a*b) = log(a) + log(b)
a, b = 0.2, 0.05
print(f"ln(a*b) = {math.log(a * b):.4f}, ln(a) + ln(b) = {math.log(a) + math.log(b):.4f}")
# change of base: log2(x) = ln(x) / ln(2)
print(f"log2(100) = {math.log(100) / math.log(2):.4f}")
# multiplying many small probabilities underflows, adding their logs does not
p = 1.0
s = 0.0
for _ in range(400):
    p *= 0.1
    s += math.log(0.1)
print("product:", p, "  sum of logs:", round(s, 2))
''', js=r'''
console.log("log2(8)     =", Math.log2(8).toFixed(1));
console.log("log10(1000) =", Math.log10(1000).toFixed(1));
console.log("ln(e)       =", Math.log(Math.E).toFixed(1));
// product rule: log(a*b) = log(a) + log(b)
const a = 0.2, b = 0.05;
console.log(`ln(a*b) = ${Math.log(a * b).toFixed(4)}, ln(a) + ln(b) = ${(Math.log(a) + Math.log(b)).toFixed(4)}`);
// change of base: log2(x) = ln(x) / ln(2)
console.log(`log2(100) = ${(Math.log(100) / Math.log(2)).toFixed(4)}`);
// multiplying many small probabilities underflows, adding their logs does not
let p = 1.0, s = 0.0;
for (let i = 0; i < 400; i++) {
  p *= 0.1;
  s += Math.log(0.1);
}
console.log("product:", p.toFixed(1), "  sum of logs:", +s.toFixed(2));
''', ts=r'''
console.log("log2(8)     =", Math.log2(8).toFixed(1));
console.log("log10(1000) =", Math.log10(1000).toFixed(1));
console.log("ln(e)       =", Math.log(Math.E).toFixed(1));
// product rule: log(a*b) = log(a) + log(b)
const a: number = 0.2, b: number = 0.05;
console.log(`ln(a*b) = ${Math.log(a * b).toFixed(4)}, ln(a) + ln(b) = ${(Math.log(a) + Math.log(b)).toFixed(4)}`);
// change of base: log2(x) = ln(x) / ln(2)
console.log(`log2(100) = ${(Math.log(100) / Math.log(2)).toFixed(4)}`);
// multiplying many small probabilities underflows, adding their logs does not
let p: number = 1.0, s: number = 0.0;
for (let i = 0; i < 400; i++) {
  p *= 0.1;
  s += Math.log(0.1);
}
console.log("product:", p.toFixed(1), "  sum of logs:", +s.toFixed(2));
''', java=r'''
public class Logs {
    static double log2(double x) { return Math.log(x) / Math.log(2); }

    public static void main(String[] args) {
        System.out.println(String.format("log2(8)     = %.1f", log2(8)));
        System.out.println(String.format("log10(1000) = %.1f", Math.log10(1000)));
        System.out.println(String.format("ln(e)       = %.1f", Math.log(Math.E)));
        // product rule: log(a*b) = log(a) + log(b)
        double a = 0.2, b = 0.05;
        System.out.println(String.format("ln(a*b) = %.4f, ln(a) + ln(b) = %.4f", Math.log(a * b), Math.log(a) + Math.log(b)));
        // change of base: log2(x) = ln(x) / ln(2)
        System.out.println(String.format("log2(100) = %.4f", Math.log(100) / Math.log(2)));
        // multiplying many small probabilities underflows, adding their logs does not
        double p = 1.0, s = 0.0;
        for (int i = 0; i < 400; i++) {
            p *= 0.1;
            s += Math.log(0.1);
        }
        System.out.println("product: " + p + "   sum of logs: " + Math.round(s * 100) / 100.0);
    }
}
''')

K.code('activations', py=r'''
import math


def sigmoid(z):
    return 1 / (1 + math.exp(-z))


def relu(z):
    return max(0.0, z)


print("   z  sigmoid    tanh    relu")
for z in [-4, -1, 0, 1, 4]:
    print(f"{z:>4} {sigmoid(z):8.4f} {math.tanh(z):7.4f} {relu(z):7.1f}")
''', js=r'''
const sigmoid = z => 1 / (1 + Math.exp(-z));
const relu = z => Math.max(0, z);

console.log("   z  sigmoid    tanh    relu");
for (const z of [-4, -1, 0, 1, 4]) {
  console.log(`${String(z).padStart(4)} ${sigmoid(z).toFixed(4).padStart(8)} ${Math.tanh(z).toFixed(4).padStart(7)} ${relu(z).toFixed(1).padStart(7)}`);
}
''', ts=r'''
const sigmoid = (z: number): number => 1 / (1 + Math.exp(-z));
const relu = (z: number): number => Math.max(0, z);

console.log("   z  sigmoid    tanh    relu");
for (const z of [-4, -1, 0, 1, 4]) {
  console.log(`${String(z).padStart(4)} ${sigmoid(z).toFixed(4).padStart(8)} ${Math.tanh(z).toFixed(4).padStart(7)} ${relu(z).toFixed(1).padStart(7)}`);
}
''', java=r'''
public class Activations {
    static double sigmoid(double z) { return 1 / (1 + Math.exp(-z)); }

    static double relu(double z) { return Math.max(0.0, z); }

    public static void main(String[] args) {
        System.out.println("   z  sigmoid    tanh    relu");
        for (int z : new int[]{-4, -1, 0, 1, 4}) {
            System.out.println(String.format("%4d %8.4f %7.4f %7.1f", z, sigmoid(z), Math.tanh(z), relu(z)));
        }
    }
}
''')

K.code('compose', py=r'''
import math


def sigmoid(z):
    return 1 / (1 + math.exp(-z))


def logit(p):                     # the inverse of sigmoid
    return math.log(p / (1 - p))


def g(x):
    return 3 * x - 1              # a straight line


for x in [0, 0.5, 1]:
    p = sigmoid(g(x))             # composition: f(g(x))
    print(f"x = {x}: g(x) = {g(x):.1f}, sigmoid(g(x)) = {p:.4f}, logit back = {logit(p):.1f}")
''', js=r'''
const sigmoid = z => 1 / (1 + Math.exp(-z));
const logit = p => Math.log(p / (1 - p));   // the inverse of sigmoid
const g = x => 3 * x - 1;                   // a straight line

for (const x of [0, 0.5, 1]) {
  const p = sigmoid(g(x));                  // composition: f(g(x))
  console.log(`x = ${x}: g(x) = ${g(x).toFixed(1)}, sigmoid(g(x)) = ${p.toFixed(4)}, logit back = ${logit(p).toFixed(1)}`);
}
''', ts=r'''
const sigmoid = (z: number): number => 1 / (1 + Math.exp(-z));
const logit = (p: number): number => Math.log(p / (1 - p));   // the inverse of sigmoid
const g = (x: number): number => 3 * x - 1;                   // a straight line

for (const x of [0, 0.5, 1]) {
  const p: number = sigmoid(g(x));          // composition: f(g(x))
  console.log(`x = ${x}: g(x) = ${g(x).toFixed(1)}, sigmoid(g(x)) = ${p.toFixed(4)}, logit back = ${logit(p).toFixed(1)}`);
}
''', java=r'''
public class Compose {
    static double sigmoid(double z) { return 1 / (1 + Math.exp(-z)); }

    static double logit(double p) { return Math.log(p / (1 - p)); }   // the inverse of sigmoid

    static double g(double x) { return 3 * x - 1; }                   // a straight line

    public static void main(String[] args) {
        for (String xs : new String[]{"0", "0.5", "1"}) {
            double x = Double.parseDouble(xs);
            double p = sigmoid(g(x));               // composition: f(g(x))
            System.out.println(String.format("x = %s: g(x) = %.1f, sigmoid(g(x)) = %.4f, logit back = %.1f", xs, g(x), p, logit(p)));
        }
    }
}
''')

# ---------------------------------------------------------------- practice programs
K.code('p_slope', py=r'''
def line_through(x1, y1, x2, y2):
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    return m, b


m, b = line_through(2, 5, 6, 13)
print(f"y = {m:.1f}x + {b:.1f}")
print(f"at x = 10, y = {m * 10 + b:.1f}")
''', js=r'''
function lineThrough(x1, y1, x2, y2) {
  const m = (y2 - y1) / (x2 - x1);
  const b = y1 - m * x1;
  return [m, b];
}

const [m, b] = lineThrough(2, 5, 6, 13);
console.log(`y = ${m.toFixed(1)}x + ${b.toFixed(1)}`);
console.log(`at x = 10, y = ${(m * 10 + b).toFixed(1)}`);
''', ts=r'''
function lineThrough(x1: number, y1: number, x2: number, y2: number): [number, number] {
  const m: number = (y2 - y1) / (x2 - x1);
  const b: number = y1 - m * x1;
  return [m, b];
}

const [m, b] = lineThrough(2, 5, 6, 13);
console.log(`y = ${m.toFixed(1)}x + ${b.toFixed(1)}`);
console.log(`at x = 10, y = ${(m * 10 + b).toFixed(1)}`);
''', java=r'''
public class PracticeSlope {
    static double[] lineThrough(double x1, double y1, double x2, double y2) {
        double m = (y2 - y1) / (x2 - x1);
        double b = y1 - m * x1;
        return new double[]{m, b};
    }

    public static void main(String[] args) {
        double[] mb = lineThrough(2, 5, 6, 13);
        System.out.println(String.format("y = %.1fx + %.1f", mb[0], mb[1]));
        System.out.println(String.format("at x = 10, y = %.1f", mb[0] * 10 + mb[1]));
    }
}
''')

K.code('p_halflife', py=r'''
import math

# a medicine halves every 6 hours. When does 400 mg fall below 50 mg?
start, target, half = 400, 50, 6
k = math.log(2) / half                 # decay rate per hour
t = math.log(start / target) / k       # solve start * e^(-k t) = target
print(f"rate k = {k:.4f} per hour")
print(f"time   = {t:.1f} hours")
print(f"check  = {start * math.exp(-k * t):.1f} mg")
''', js=r'''
// a medicine halves every 6 hours. When does 400 mg fall below 50 mg?
const start = 400, target = 50, half = 6;
const k = Math.log(2) / half;              // decay rate per hour
const t = Math.log(start / target) / k;    // solve start * e^(-k t) = target
console.log(`rate k = ${k.toFixed(4)} per hour`);
console.log(`time   = ${t.toFixed(1)} hours`);
console.log(`check  = ${(start * Math.exp(-k * t)).toFixed(1)} mg`);
''', ts=r'''
// a medicine halves every 6 hours. When does 400 mg fall below 50 mg?
const start: number = 400, target: number = 50, half: number = 6;
const k: number = Math.log(2) / half;          // decay rate per hour
const t: number = Math.log(start / target) / k;  // solve start * e^(-k t) = target
console.log(`rate k = ${k.toFixed(4)} per hour`);
console.log(`time   = ${t.toFixed(1)} hours`);
console.log(`check  = ${(start * Math.exp(-k * t)).toFixed(1)} mg`);
''', java=r'''
public class PracticeHalfLife {
    public static void main(String[] args) {
        // a medicine halves every 6 hours. When does 400 mg fall below 50 mg?
        double start = 400, target = 50, half = 6;
        double k = Math.log(2) / half;              // decay rate per hour
        double t = Math.log(start / target) / k;    // solve start * e^(-k t) = target
        System.out.println(String.format("rate k = %.4f per hour", k));
        System.out.println(String.format("time   = %.1f hours", t));
        System.out.println(String.format("check  = %.1f mg", start * Math.exp(-k * t)));
    }
}
''')

K.code('p_bisect', py=r'''
import math


def sigmoid(z):
    return 1 / (1 + math.exp(-z))


# find z with sigmoid(z) = 0.9 by halving an interval
lo, hi = 0.0, 10.0
for step in range(30):
    mid = (lo + hi) / 2
    if sigmoid(mid) < 0.9:
        lo = mid                  # answer is to the right
    else:
        hi = mid                  # answer is to the left
print(f"bisection: z = {(lo + hi) / 2:.6f}")
print(f"logit(0.9) = {math.log(0.9 / 0.1):.6f}")
''', js=r'''
const sigmoid = z => 1 / (1 + Math.exp(-z));

// find z with sigmoid(z) = 0.9 by halving an interval
let lo = 0.0, hi = 10.0;
for (let step = 0; step < 30; step++) {
  const mid = (lo + hi) / 2;
  if (sigmoid(mid) < 0.9) {
    lo = mid;                     // answer is to the right
  } else {
    hi = mid;                     // answer is to the left
  }
}
console.log(`bisection: z = ${((lo + hi) / 2).toFixed(6)}`);
console.log(`logit(0.9) = ${Math.log(0.9 / 0.1).toFixed(6)}`);
''', ts=r'''
const sigmoid = (z: number): number => 1 / (1 + Math.exp(-z));

// find z with sigmoid(z) = 0.9 by halving an interval
let lo: number = 0.0, hi: number = 10.0;
for (let step = 0; step < 30; step++) {
  const mid: number = (lo + hi) / 2;
  if (sigmoid(mid) < 0.9) {
    lo = mid;                     // answer is to the right
  } else {
    hi = mid;                     // answer is to the left
  }
}
console.log(`bisection: z = ${((lo + hi) / 2).toFixed(6)}`);
console.log(`logit(0.9) = ${Math.log(0.9 / 0.1).toFixed(6)}`);
''', java=r'''
public class PracticeBisect {
    static double sigmoid(double z) { return 1 / (1 + Math.exp(-z)); }

    public static void main(String[] args) {
        // find z with sigmoid(z) = 0.9 by halving an interval
        double lo = 0.0, hi = 10.0;
        for (int step = 0; step < 30; step++) {
            double mid = (lo + hi) / 2;
            if (sigmoid(mid) < 0.9) {
                lo = mid;                 // answer is to the right
            } else {
                hi = mid;                 // answer is to the left
            }
        }
        System.out.println(String.format("bisection: z = %.6f", (lo + hi) / 2));
        System.out.println(String.format("logit(0.9) = %.6f", Math.log(0.9 / 0.1)));
    }
}
''')

K.code('p_logsum', py=r'''
import math

probs = [0.9, 0.8, 0.95, 0.7, 0.85]   # chance the model gave to each right answer
product = 1.0
for p in probs:
    product *= p
log_sum = sum(math.log(p) for p in probs)
print(f"product of probabilities = {product:.6f}")
print(f"sum of logs              = {log_sum:.6f}")
print(f"e to that sum            = {math.exp(log_sum):.6f}")
print(f"average log loss         = {-log_sum / len(probs):.6f}")
''', js=r'''
const probs = [0.9, 0.8, 0.95, 0.7, 0.85];  // chance the model gave to each right answer
let product = 1.0;
for (const p of probs) product *= p;
const logSum = probs.reduce((s, p) => s + Math.log(p), 0);
console.log(`product of probabilities = ${product.toFixed(6)}`);
console.log(`sum of logs              = ${logSum.toFixed(6)}`);
console.log(`e to that sum            = ${Math.exp(logSum).toFixed(6)}`);
console.log(`average log loss         = ${(-logSum / probs.length).toFixed(6)}`);
''', ts=r'''
const probs: number[] = [0.9, 0.8, 0.95, 0.7, 0.85];  // chance the model gave to each right answer
let product: number = 1.0;
for (const p of probs) product *= p;
const logSum: number = probs.reduce((s, p) => s + Math.log(p), 0);
console.log(`product of probabilities = ${product.toFixed(6)}`);
console.log(`sum of logs              = ${logSum.toFixed(6)}`);
console.log(`e to that sum            = ${Math.exp(logSum).toFixed(6)}`);
console.log(`average log loss         = ${(-logSum / probs.length).toFixed(6)}`);
''', java=r'''
public class PracticeLogSum {
    public static void main(String[] args) {
        double[] probs = {0.9, 0.8, 0.95, 0.7, 0.85};  // chance the model gave to each right answer
        double product = 1.0, logSum = 0.0;
        for (double p : probs) {
            product *= p;
            logSum += Math.log(p);
        }
        System.out.println(String.format("product of probabilities = %.6f", product));
        System.out.println(String.format("sum of logs              = %.6f", logSum));
        System.out.println(String.format("e to that sum            = %.6f", Math.exp(logSum)));
        System.out.println(String.format("average log loss         = %.6f", -logSum / probs.length));
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('functions', '⚙️', 'What a function is', f'''
<p>A <b>function</b> is a machine with one rule: every input gives exactly one output. A vending machine is a function. Press B4 and you always get the same snack. We write the machine as f and its output for input x as f(x), read "f of x".</p>
<div class="grid2">
<div class="box"><h4>📥 Domain</h4><p>All the inputs the machine accepts. √x only accepts x ≥ 0 when we stay with real numbers, and 1 ÷ x refuses x = 0.</p></div>
<div class="box"><h4>📤 Range</h4><p>All the outputs it can produce. x² never gives a negative number, and the sigmoid function only gives values between 0 and 1.</p></div>
</div>
{fx('Function notation', 'f(x) = 2x + 1 &nbsp;⟹&nbsp; f(3) = 2 × 3 + 1 = 7', 'Replace every x in the rule with the input, then work it out.')}
<p>A graph draws every pair (x, f(x)) as a point. If a vertical line ever crosses the curve twice, it is not a function, because one input would have two outputs.</p>
{viz('fnplot')}
{ml('A trained model is a function f(x) = prediction. Its domain is the kind of data it was trained on, which is why a model trained on cat photos gives nonsense for an X ray. The output range is designed on purpose: a price model can output any number, a classifier squeezes its output into 0 to 1.')}
''', kw=['function', 'f(x)', 'domain', 'range', 'graph', 'vertical line test']),

    part('lines', '📈', 'Straight lines: slope and intercept', f'''
<p>The simplest useful function is a straight line. Two numbers describe it completely.</p>
{fxs(fx('Slope intercept form', 'y = m x + b', 'm is the slope (how much y climbs when x goes up by 1) and b is the intercept (the value of y when x = 0).'),
         fx('Slope from two points', f'm = {frac("y₂ − y₁", "x₂ − x₁")} = {frac("rise", "run")}', 'Positive slope climbs, negative slope falls, zero slope is flat.'))}
{viz('line2pt')}
{code('line_fn', 'Evaluate a line and find it from two points')}
{life('A taxi charges 50 to start and 12 per km. The fare is y = 12x + 50. The slope 12 is the price per km and the intercept 50 is the fare before you move at all.')}
{ml('Linear regression is "find the best m and b" for a cloud of points. With many inputs it becomes y = w₁x₁ + w₂x₂ + ... + b, and the slopes are called <b>weights</b> and the intercept is called the <b>bias</b>. Every neuron in a neural network starts with exactly this sum.')}
{trick('Slope is "rise over run", like a staircase: how far up for each step forward. Parallel lines have equal slopes. Perpendicular lines have slopes that multiply to −1.')}
''', kw=['straight line', 'slope', 'intercept', 'y = mx + b', 'gradient of a line', 'weights', 'bias', 'linear regression']),

    part('quadratic', '🪣', 'Quadratics and polynomials', f'''
<p>A <b>quadratic</b> has an x² term: f(x) = ax² + bx + c. Its graph is a <b>parabola</b>, a U shape when a &gt; 0 and an upside down U when a &lt; 0. The bottom (or top) is called the <b>vertex</b>.</p>
{fxs(fx('Quadratic formula', f'x = {frac("−b ± √(b² − 4ac)", "2a")}', 'Gives the roots, where the curve crosses y = 0.'),
         fx('Discriminant', 'D = b² − 4ac', 'D &gt; 0: two roots. D = 0: one root. D &lt; 0: no real roots.'),
         fx('Vertex', f'x = {frac("−b", "2a")}', 'The lowest point when a &gt; 0. This is the minimum we look for in learning.'))}
{worked('Solve x² − 5x + 6 = 0', [
        'Read off a = 1, b = −5, c = 6.',
        'Discriminant: <span class="eq">D = (−5)² − 4 × 1 × 6 = 25 − 24 = 1</span>. It is positive, so there are two roots.',
        '√D = 1, so <span class="eq">x = (5 ± 1) ÷ 2</span>',
        'The two roots are <span class="eq">x = 6 ÷ 2 = 3</span> and <span class="eq">x = 4 ÷ 2 = 2</span>',
        'Check by factorising: x² − 5x + 6 = (x − 2)(x − 3). Each bracket is zero at one root.'])}
{code('quadratic', 'Roots, the discriminant and the vertex')}
<p>A <b>polynomial</b> adds more powers: 4x³ − x + 7 has degree 3. Higher degree means more bends, which lets the curve follow data more closely, sometimes too closely.</p>
{ml('The squared error (y − ŷ)² is a parabola in the prediction ŷ. Its vertex sits exactly at ŷ = y, so "make the error as small as possible" is "find the bottom of the U". Polynomial regression adds x², x³ as extra inputs, and a degree that is too high memorises noise. That is called <b>overfitting</b>.')}
{life('A ball thrown in the air follows a parabola. The vertex is the highest point it reaches, and the roots are where it leaves your hand and where it lands.')}
''', kw=['quadratic', 'parabola', 'vertex', 'roots', 'quadratic formula', 'discriminant', 'polynomial', 'overfitting']),

    part('exponential', '🚀', 'Exponential growth and the number e', f'''
<p>In an <b>exponential function</b> the variable sits in the exponent: f(x) = aˣ. Each step multiplies instead of adding. With a &gt; 1 it grows faster and faster, with 0 &lt; a &lt; 1 it shrinks towards zero but never reaches it.</p>
{table(['x', '0', '1', '2', '3', '4', '10'], [
        ['2x (adding)', '0', '2', '4', '6', '8', '20'],
        ['2ˣ (multiplying)', '1', '2', '4', '8', '16', '1024'],
        ['0.5ˣ (halving)', '1', '0.5', '0.25', '0.125', '0.0625', '0.00098'],
    ])}
<h3>Where e comes from</h3>
<p>Put 1 rupee in a bank that pays 100% a year. Paid once, you get 2. Paid in two halves of 50%, you get 1.5 × 1.5 = 2.25. Paid every day, more still. As the payments get more frequent the amount does not explode. It settles at a special number called <b>e ≈ 2.71828</b>.</p>
{fxs(fx('Euler number', f'e = lim (1 + {frac(1, "n")})ⁿ as n → ∞ ≈ 2.71828', 'Read lim as "the value it settles at when n grows without end".'),
         fx('Natural growth and decay', 'A(t) = A₀ e^(kt)', 'k &gt; 0 grows, k &lt; 0 decays. A₀ is the starting amount.'))}
{code('euler', 'Compound interest settles at e')}
{life('Bacteria in milk double every 20 minutes or so, which is why milk left out on a hot afternoon turns sour within hours. Radioactive carbon decays exponentially, which lets scientists date old bones.')}
{ml('eˣ appears in the sigmoid and softmax functions, in the normal distribution, and in learning rate schedules that decay exponentially. The derivative of eˣ is eˣ itself, which makes the calculus in Chapter 6 very neat.')}
''', kw=['exponential', 'exponential growth', 'decay', 'euler number', 'e', 'compound interest', 'half life']),

    part('logs', '🪵', 'Logarithms: the undo button for powers', f'''
<p>A <b>logarithm</b> answers the question "what power do I need?". Since 2³ = 8, log₂ 8 = 3. Since 10² = 100, log₁₀ 100 = 2. The natural log, ln, uses base e.</p>
{fx('Definition', 'log_b(y) = x &nbsp; means &nbsp; bˣ = y', 'The log is the exponent. ln(x) means log base e, and log₂ counts doublings, or bits.')}
{table(['Rule', 'In symbols', 'Example'], [
        ['Product becomes sum', 'log(ab) = log a + log b', 'log₂(4 × 8) = 2 + 3 = 5'],
        ['Quotient becomes difference', 'log(a ÷ b) = log a − log b', 'log₁₀(1000 ÷ 10) = 3 − 1 = 2'],
        ['Power comes down in front', 'log(aⁿ) = n log a', 'ln(e⁵) = 5'],
        ['Log of 1 is 0', 'log 1 = 0', 'because b⁰ = 1'],
        ['Change of base', f'log_b x = {frac("ln x", "ln b")}', f'log₂ 100 = {frac("4.605", "0.693")} ≈ 6.64'],
    ])}
{code('logs', 'Log rules, and why logs stop tiny numbers vanishing')}
{trick('"Logs turn multiplying into adding". That single sentence explains slide rules, decibels, the Richter scale and why every ML loss for probabilities has a log in it.')}
{life('Sound in decibels is a log scale: 10 dB more means 10 times the power. An earthquake of magnitude 7 shakes about 10 times harder than magnitude 6. Logs squeeze huge ranges into numbers people can handle.')}
{ml('A model gives each correct training answer a probability. The chance of getting all of them is a product of many numbers below 1, which a computer rounds to 0. Taking logs turns the product into a sum, which stays a normal sized number. That is why training minimises the <b>negative log likelihood</b>, also called <b>log loss</b> or <b>cross entropy</b> (Chapter 12).')}
<div class="exam">ln(0) does not exist and ln of a negative number is not real. Code adds a tiny epsilon, as in log(p + 1e-12), so a predicted probability of exactly 0 does not crash training.</div>
''', kw=['logarithm', 'log', 'ln', 'natural log', 'log rules', 'change of base', 'log loss', 'underflow', 'decibel']),

    part('activation', '〰️', 'The S curve and other functions machine learning uses', f'''
<p>Some functions show up in machine learning again and again. They are called <b>activation functions</b> because they decide how strongly a neuron "fires".</p>
{fxs(fx('Sigmoid', f'σ(z) = {frac(1, "1 + e^(−z)")}', 'Squashes any number into (0, 1). σ(0) = 0.5. Used for probabilities of yes or no.'),
         fx('Tanh', f'tanh(z) = {frac("e^z − e^(−z)", "e^z + e^(−z)")}', 'Squashes into (−1, 1) and is centred on 0.'),
         fx('ReLU', 'ReLU(z) = max(0, z)', 'Zero for negatives, unchanged for positives. Fast, and the default in deep networks.'))}
{viz('actplot')}
{code('activations', 'Sigmoid, tanh and ReLU side by side')}
{table(['Function', 'Output range', 'Good for', 'Weak spot'], [
        ['Sigmoid', '0 to 1', 'the last layer of a yes or no classifier', 'flat at both ends, so learning slows down'],
        ['Tanh', '−1 to 1', 'hidden layers in older networks and RNNs', 'also flat at both ends'],
        ['ReLU', '0 to ∞', 'hidden layers of almost every modern network', 'a neuron stuck below 0 stops learning'],
        ['Softmax', '0 to 1, adding to 1', 'choosing one class out of many', 'needs care with large numbers'],
    ])}
{life('A dimmer switch is a sigmoid: turning the knob far to the left keeps the light off, far to the right keeps it fully on, and only the middle part changes the brightness quickly.')}
''', kw=['sigmoid', 'tanh', 'ReLU', 'activation function', 'softmax', 'S curve', 'logistic function']),

    part('compose', '🔗', 'Composing, shifting and inverting functions', f'''
<p><b>Composition</b> feeds one function into another: (f ∘ g)(x) = f(g(x)). Work from the inside out. If g(x) = 3x − 1 and f is the sigmoid, then f(g(1)) = σ(2) ≈ 0.88.</p>
<p>An <b>inverse</b> function undoes another: f⁻¹(f(x)) = x. The square root undoes squaring for x ≥ 0, ln undoes eˣ, and the <b>logit</b> undoes the sigmoid.</p>
{fxs(fx('Composition', '(f ∘ g)(x) = f(g(x))', 'Order matters: f(g(x)) and g(f(x)) are usually different.'),
         fx('Logit, the inverse of sigmoid', f'logit(p) = ln {frac("p", "1 − p")}', 'p ÷ (1 − p) is called the odds. Logit turns a probability back into a score.'))}
{viz('mirror')}
{code('compose', 'A line fed into a sigmoid, then undone by logit')}
{table(['Change to f(x)', 'What the graph does'], [
        ['f(x) + k', 'moves up by k'],
        ['f(x − h)', 'moves right by h'],
        ['a · f(x)', 'stretches up and down by a, and flips if a &lt; 0'],
        ['f(c · x)', 'squeezes sideways by c'],
    ])}
{ml('A neural network is one giant composition: layer 3 of layer 2 of layer 1 of the input. Logistic regression is the composition σ(w · x + b), a sigmoid of a straight line. The chain rule in Chapter 7 is the tool for working with such chains.')}
{trick('The graph of an inverse function is the mirror image of the original in the line y = x. Swap the x and y of every point and you have the inverse.')}
''', kw=['composition', 'inverse function', 'logit', 'odds', 'shift', 'stretch', 'f(g(x))']),
]

INFO = {
    'title': 'Functions are machines',
    'panels': [
        {'s': [['e', '⚙️'], ['t', 'x  →  f  →  f(x)', {'b': 1}]], 'h': 'A function', 't': 'One input, exactly one output.', 'more': 'A trained model is a function from data to predictions.'},
        {'s': [['e', '📈'], ['t', 'y = 12x + 50', {'b': 1}]], 'h': 'A straight line', 't': 'Slope and intercept.', 'more': 'Linear regression learns the slope (weight) and the intercept (bias).'},
        {'s': [['e', '🚀'], ['b', [1, 2, 4, 8, 16, 32]]], 'h': 'Exponential', 't': 'Multiply every step.', 'more': 'Growth with e appears in sigmoid, softmax and the normal curve.'},
        {'s': [['e', '🪵'], ['t', 'log(ab) = log a + log b', {'b': 1}]], 'h': 'Logarithm', 't': 'Undo a power.', 'more': 'Logs turn products of probabilities into sums, which keeps training stable.'},
    ],
    'remember': 'A function gives one output per input. Lines have a slope and an intercept. Exponentials multiply, logs undo them and turn products into sums. Sigmoid squashes any number into a probability.',
}

REAL = [
    ['🚕', 'Taxi fares', 'A fare of 50 plus 12 per km is the line y = 12x + 50. The slope is the price per km and the intercept is the starting charge.'],
    ['💊', 'Medicine in the blood', 'Many medicines halve in the body every few hours. That is exponential decay, and a log tells you how long until the dose falls below a level.'],
    ['🔊', 'Decibels and earthquakes', 'Sound levels and the Richter scale are logarithms, so a tiny step on the scale is a big jump in real energy.'],
]

K.say('top', 'Welcome',
      'This chapter is about functions, the machines that turn an input into an output. You will meet straight lines, parabolas, exponential growth, logarithms and the S shaped sigmoid, which are the shapes machine learning models are built from.',
      'यह अध्याय functions के बारे में है, वे मशीनें जो input को output में बदलती हैं। आप सीधी रेखाएँ, parabola, exponential growth, logarithm और S आकार का sigmoid देखेंगे।',
      'ಈ ಅಧ್ಯಾಯ functions ಬಗ್ಗೆ, input ಅನ್ನು output ಆಗಿ ಬದಲಿಸುವ ಯಂತ್ರಗಳು. ನೇರ ರೇಖೆಗಳು, parabola, exponential growth, logarithm ಮತ್ತು S ಆಕಾರದ sigmoid ನೋಡುತ್ತೀರಿ.',
      'ଏହି ଅଧ୍ୟାୟ functions ବିଷୟରେ, ଯେଉଁ ଯନ୍ତ୍ର input କୁ output ରେ ବଦଳାଏ। ଆପଣ ସିଧା ରେଖା, parabola, exponential growth, logarithm ଓ S ଆକାରର sigmoid ଦେଖିବେ।',
      'هذا الفصل عن الدوال، وهي آلات تحول المدخل إلى مخرج. ستتعرف على الخطوط المستقيمة والقطع المكافئ والنمو الأسي واللوغاريتمات ودالة سيغمويد على شكل حرف S.',
      'In diesem Kapitel geht es um Funktionen, Maschinen, die eine Eingabe in eine Ausgabe verwandeln. Du lernst Geraden, Parabeln, exponentielles Wachstum, Logarithmen und die S förmige Sigmoidfunktion kennen.')
K.say('functions', 'Functions',
      'A function gives exactly one output for every input, like a vending machine. The domain is every input it accepts, and the range is every output it can give.',
      'Function हर input के लिए ठीक एक output देता है, जैसे vending machine। Domain सभी स्वीकार्य inputs हैं और range सभी संभव outputs।',
      'Function ಪ್ರತಿ input ಗೆ ನಿಖರವಾಗಿ ಒಂದು output ನೀಡುತ್ತದೆ, vending machine ಹಾಗೆ. Domain ಎಲ್ಲ inputs, range ಎಲ್ಲ outputs.',
      'Function ପ୍ରତ୍ୟେକ input ପାଇଁ ଠିକ ଗୋଟିଏ output ଦିଏ, vending machine ପରି। Domain ସବୁ inputs ଏବଂ range ସବୁ outputs।',
      'الدالة تعطي مخرجًا واحدًا بالضبط لكل مدخل، مثل آلة البيع. المجال هو كل المدخلات المقبولة، والمدى هو كل المخرجات الممكنة.',
      'Eine Funktion liefert zu jeder Eingabe genau eine Ausgabe, wie ein Snackautomat. Der Definitionsbereich sind alle erlaubten Eingaben, der Wertebereich alle möglichen Ausgaben.')
K.say('lines', 'Lines',
      'A straight line is y equals m x plus b. The slope m is rise over run, and the intercept b is where the line meets the y axis. In machine learning the slope is called a weight and the intercept a bias.',
      'सीधी रेखा y बराबर m x जमा b है। Slope m है rise बटा run, और intercept b वह जगह है जहाँ रेखा y axis से मिलती है। ML में slope को weight और intercept को bias कहते हैं।',
      'ನೇರ ರೇಖೆ y ಸಮ m x ಸೇರಿಸು b. Slope m ಎಂದರೆ rise ಭಾಗಿಸು run, intercept b ರೇಖೆ y ಅಕ್ಷವನ್ನು ಸಂಧಿಸುವ ಸ್ಥಳ. ML ನಲ್ಲಿ slope weight, intercept bias.',
      'ସିଧା ରେଖା y ସମାନ m x ଯୋଗ b। Slope m ହେଉଛି rise ହରଣ run, intercept b ଯେଉଁଠି ରେଖା y ଅକ୍ଷକୁ ଛୁଏଁ। ML ରେ slope କୁ weight ଓ intercept କୁ bias କୁହାଯାଏ।',
      'الخط المستقيم هو y يساوي m x زائد b. الميل m هو الارتفاع على المسافة الأفقية، والمقطع b هو نقطة التقاء الخط بمحور y. في تعلم الآلة يسمى الميل وزنًا والمقطع انحيازًا.',
      'Eine Gerade ist y gleich m x plus b. Die Steigung m ist Anstieg durch Lauf, der Achsenabschnitt b ist der Schnitt mit der y Achse. Im maschinellen Lernen heißt die Steigung Gewicht und der Abschnitt Bias.')
K.say('quadratic', 'Quadratics',
      'A quadratic has an x squared term and draws a U shaped parabola. The quadratic formula gives its roots, the discriminant says how many there are, and the vertex at minus b over two a is the lowest point.',
      'Quadratic में x का वर्ग होता है और यह U आकार का parabola बनाता है। Quadratic formula roots देता है, discriminant बताता है कितने हैं, और vertex सबसे नीचा बिंदु है।',
      'Quadratic ನಲ್ಲಿ x ವರ್ಗ ಇರುತ್ತದೆ, ಅದು U ಆಕಾರದ parabola. Quadratic formula roots ಕೊಡುತ್ತದೆ, discriminant ಎಷ್ಟು ಎಂದು ಹೇಳುತ್ತದೆ, vertex ಅತಿ ಕೆಳಗಿನ ಬಿಂದು.',
      'Quadratic ରେ x ର ବର୍ଗ ଥାଏ ଓ ଏହା U ଆକାରର parabola। Quadratic formula roots ଦିଏ, discriminant କେତେ ଅଛି କହେ, ଏବଂ vertex ସବୁଠୁ ତଳ ବିନ୍ଦୁ।',
      'الدالة التربيعية فيها x مربع وترسم قطعًا مكافئًا على شكل U. القانون العام يعطي الجذور، والمميز يخبر بعددها، والرأس هو أدنى نقطة.',
      'Eine quadratische Funktion hat ein x Quadrat und zeichnet eine U förmige Parabel. Die Mitternachtsformel liefert die Nullstellen, die Diskriminante ihre Anzahl, und der Scheitel ist der tiefste Punkt.')
K.say('exponential', 'Exponentials',
      'An exponential multiplies at every step, so it grows faster and faster or shrinks towards zero. Compounding more and more often settles at the number e, about two point seven one eight.',
      'Exponential हर कदम पर गुणा करता है, इसलिए यह तेज़ी से बढ़ता है या शून्य की ओर घटता है। बार बार compounding करने पर संख्या e पर रुकती है, लगभग दो दशमलव सात एक आठ।',
      'Exponential ಪ್ರತಿ ಹೆಜ್ಜೆಯಲ್ಲಿ ಗುಣಿಸುತ್ತದೆ, ಆದ್ದರಿಂದ ವೇಗವಾಗಿ ಬೆಳೆಯುತ್ತದೆ ಅಥವಾ ಸೊನ್ನೆಯತ್ತ ಕುಗ್ಗುತ್ತದೆ. ಹೆಚ್ಚು ಬಾರಿ compounding ಮಾಡಿದರೆ e ಎಂಬ ಸಂಖ್ಯೆಗೆ ನಿಲ್ಲುತ್ತದೆ.',
      'Exponential ପ୍ରତି ପଦକ୍ଷେପରେ ଗୁଣନ କରେ, ତେଣୁ ଶୀଘ୍ର ବଢ଼େ କିମ୍ବା ଶୂନ ଆଡ଼କୁ କମେ। ବାରମ୍ବାର compounding କଲେ ସଂଖ୍ୟା e ରେ ସ୍ଥିର ହୁଏ।',
      'الدالة الأسية تضرب في كل خطوة، فتنمو أسرع فأسرع أو تتقلص نحو الصفر. والفائدة المركبة المتكررة تستقر عند العدد e، نحو اثنين فاصلة سبعة واحد ثمانية.',
      'Eine Exponentialfunktion multipliziert bei jedem Schritt, wächst also immer schneller oder schrumpft gegen null. Immer häufigeres Verzinsen nähert sich der Zahl e, etwa zwei Komma sieben eins acht.')
K.say('logs', 'Logarithms',
      'A logarithm asks what power you need. Logs turn multiplying into adding, which is why machine learning uses the log of probabilities: a product of many small numbers would round to zero, but a sum of logs stays safe.',
      'Logarithm पूछता है कौन सी घात चाहिए। Logs गुणा को जोड़ में बदलते हैं, इसलिए ML probabilities का log लेता है: बहुत छोटी संख्याओं का गुणा शून्य हो जाता, पर logs का जोड़ सुरक्षित रहता है।',
      'Logarithm ಯಾವ ಘಾತ ಬೇಕು ಎಂದು ಕೇಳುತ್ತದೆ. Logs ಗುಣಾಕಾರವನ್ನು ಕೂಡುವಿಕೆಯಾಗಿ ಬದಲಿಸುತ್ತವೆ, ಆದ್ದರಿಂದ ML probabilities ನ log ಬಳಸುತ್ತದೆ.',
      'Logarithm ପଚାରେ କେଉଁ ଘାତ ଦରକାର। Logs ଗୁଣନକୁ ଯୋଗରେ ବଦଳାନ୍ତି, ତେଣୁ ML probabilities ର log ବ୍ୟବହାର କରେ।',
      'اللوغاريتم يسأل عن الأس المطلوب. اللوغاريتمات تحول الضرب إلى جمع، ولهذا يستخدم تعلم الآلة لوغاريتم الاحتمالات: حاصل ضرب أعداد صغيرة كثيرة يقرب إلى صفر، أما مجموع اللوغاريتمات فيبقى آمنًا.',
      'Ein Logarithmus fragt, welche Potenz man braucht. Logarithmen machen aus Multiplizieren Addieren. Darum nutzt maschinelles Lernen den Logarithmus von Wahrscheinlichkeiten: ein Produkt vieler kleiner Zahlen würde zu null gerundet, eine Summe von Logarithmen bleibt sicher.')
K.say('activation', 'Activation functions',
      'The sigmoid squashes any number into a value between zero and one, tanh squashes into minus one to one, and ReLU keeps positives and turns negatives into zero. These are the activation functions inside neural networks.',
      'Sigmoid किसी भी संख्या को शून्य और एक के बीच दबा देता है, tanh minus एक से एक में, और ReLU positive रखता है और negative को शून्य बनाता है।',
      'Sigmoid ಯಾವುದೇ ಸಂಖ್ಯೆಯನ್ನು ಸೊನ್ನೆ ಮತ್ತು ಒಂದರ ನಡುವೆ ಒತ್ತುತ್ತದೆ, tanh ಮೈನಸ್ ಒಂದು ಮತ್ತು ಒಂದರ ನಡುವೆ, ReLU negative ಅನ್ನು ಸೊನ್ನೆ ಮಾಡುತ್ತದೆ.',
      'Sigmoid ଯେକୌଣସି ସଂଖ୍ୟାକୁ ଶୂନ ଓ ଏକ ମଧ୍ୟରେ ଚାପେ, tanh ମାଇନସ ଏକରୁ ଏକ ମଧ୍ୟରେ, ଏବଂ ReLU negative କୁ ଶୂନ କରେ।',
      'دالة سيغمويد تضغط أي عدد بين صفر وواحد، وتانش بين سالب واحد وواحد، وريلو تبقي الموجب وتجعل السالب صفرًا. هذه دوال التنشيط داخل الشبكات العصبية.',
      'Die Sigmoidfunktion drückt jede Zahl zwischen null und eins, tanh zwischen minus eins und eins, und ReLU behält positive Werte und macht negative zu null. Das sind die Aktivierungsfunktionen in neuronalen Netzen.')
K.say('compose', 'Composition and inverses',
      'Composition feeds one function into another, working from the inside out. An inverse undoes a function, and its graph is the mirror image in the line y equals x. The logit undoes the sigmoid.',
      'Composition एक function को दूसरे में डालता है, अंदर से बाहर। Inverse function को उलट देता है, और उसका graph y बराबर x रेखा में दर्पण छवि है। Logit sigmoid को उलटता है।',
      'Composition ಒಂದು function ಅನ್ನು ಇನ್ನೊಂದರೊಳಗೆ ಹಾಕುತ್ತದೆ, ಒಳಗಿನಿಂದ ಹೊರಗೆ. Inverse function ಅನ್ನು ರದ್ದುಗೊಳಿಸುತ್ತದೆ. Logit sigmoid ಅನ್ನು ರದ್ದುಗೊಳಿಸುತ್ತದೆ.',
      'Composition ଗୋଟିଏ function କୁ ଆରେକରେ ଦିଏ, ଭିତରୁ ବାହାରକୁ। Inverse function କୁ ଓଲଟାଏ। Logit sigmoid କୁ ଓଲଟାଏ।',
      'التركيب يدخل دالة في أخرى من الداخل إلى الخارج. والدالة العكسية تلغي عمل الدالة، ورسمها صورة مرآة في الخط y يساوي x. ودالة لوجيت تعكس سيغمويد.',
      'Verkettung steckt eine Funktion in eine andere, von innen nach außen. Eine Umkehrfunktion macht eine Funktion rückgängig, ihr Graph ist das Spiegelbild an der Geraden y gleich x. Der Logit kehrt die Sigmoidfunktion um.')
K.say('practice', 'Practice',
      'Now practise. Find lines through points, solve decay problems with logs, and find where the sigmoid reaches a target by halving an interval. Try first, then open the hint and the full working.',
      'अब अभ्यास करें। बिंदुओं से रेखा निकालें, logs से decay सवाल हल करें, और interval को आधा करके देखें sigmoid कहाँ लक्ष्य तक पहुँचता है।',
      'ಈಗ ಅಭ್ಯಾಸ ಮಾಡಿ. ಬಿಂದುಗಳ ಮೂಲಕ ರೇಖೆ, logs ಬಳಸಿ decay ಸಮಸ್ಯೆಗಳು, ಮತ್ತು interval ಅರ್ಧ ಮಾಡಿ sigmoid ಗುರಿ ತಲುಪುವ ಸ್ಥಳ ಹುಡುಕಿ.',
      'ଏବେ ଅଭ୍ୟାସ କରନ୍ତୁ। ବିନ୍ଦୁ ଦେଇ ରେଖା, logs ରେ decay ପ୍ରଶ୍ନ, ଏବଂ interval ଅଧା କରି sigmoid କେଉଁଠି ଲକ୍ଷ୍ୟରେ ପହଞ୍ଚେ ଖୋଜନ୍ତୁ।',
      'الآن تدرب. أوجد خطوطًا تمر بنقاط، وحل مسائل التناقص باللوغاريتمات، وابحث أين تصل سيغمويد إلى قيمة معينة بتنصيف الفترة.',
      'Jetzt wird geübt. Finde Geraden durch Punkte, löse Zerfallsaufgaben mit Logarithmen und finde durch Halbieren eines Intervalls, wo die Sigmoidfunktion einen Zielwert erreicht.')

# ---------------------------------------------------------------- practice
K.practice('line-two-points', 'e', 'The line through two points', 'p_slope',
           '<p>Find the line through (2, 5) and (6, 13) in the form y = mx + b, then predict y at x = 10.</p>',
           'y = 2.0x + 1.0\nat x = 10, y = 21.0',
           'Slope is rise over run. Then put one point into y = mx + b to find b.',
           '<p>The rise is 13 − 5 = 8 and the run is 6 − 2 = 4, so m = 8 ÷ 4 = 2. Put (2, 5) into y = 2x + b: 5 = 4 + b, so b = 1. At x = 10, y = 2 × 10 + 1 = 21. A model that predicts outside the range of its data like this is <b>extrapolating</b>, which is risky with real data.</p>',
           'O(1)', 'O(1)')
K.practice('half-life', 'm', 'When does the medicine drop below 50 mg', 'p_halflife',
           '<p>A medicine halves in the body every 6 hours. A patient takes 400 mg. Using A(t) = 400 e^(−kt), find k and the time when 50 mg is left.</p>',
           'rate k = 0.1155 per hour\ntime   = 18.0 hours\ncheck  = 50.0 mg',
           'Halving after 6 hours means e^(−6k) = 1/2. Take ln of both sides.',
           '<p>From e^(−6k) = 0.5 we get −6k = ln 0.5, so k = ln 2 ÷ 6 ≈ 0.1155. Then 400 e^(−kt) = 50 gives e^(−kt) = 1/8, so kt = ln 8 and t = ln 8 ÷ k = 3 ln 2 ÷ (ln 2 ÷ 6) = 18 hours. Common sense check: 400 → 200 → 100 → 50 is three halvings of 6 hours.</p>',
           'O(1)', 'O(1)')
K.practice('log-likelihood', 'h', 'Products of probabilities as sums of logs', 'p_logsum',
           '<p>A model gave the right answers probabilities 0.9, 0.8, 0.95, 0.7 and 0.85. Compute their product, the sum of their natural logs, e to that sum, and the average negative log (the log loss).</p>',
           'product of probabilities = 0.406980\nsum of logs              = -0.899032\ne to that sum            = 0.406980\naverage log loss         = 0.179806',
           'ln(a × b × c) = ln a + ln b + ln c.',
           '<p>The product rule of logs says the sum of the logs equals the log of the product, so e to the sum gives the product back exactly. With thousands of examples the product would underflow to 0, while the sum stays a normal number. Dividing the negative sum by the count gives the average log loss, the number a classifier minimises during training.</p>',
           'O(n)', 'O(1)')
K.practice('invert-sigmoid', 'x', 'Invert the sigmoid by bisection', 'p_bisect',
           '<p>Find z so that σ(z) = 0.9 using only the sigmoid itself: keep an interval [lo, hi] that contains the answer and halve it 30 times. Compare with the exact logit.</p>',
           'bisection: z = 2.197225\nlogit(0.9) = 2.197225',
           'σ always increases. If σ(mid) is too small, the answer is to the right of mid.',
           '<p>Because the sigmoid always increases, comparing σ(mid) with 0.9 tells us which half holds the answer. Each step halves the interval, so after 30 steps it is 10 ÷ 2³⁰ ≈ 10⁻⁸ wide. The exact answer is logit(0.9) = ln(0.9 ÷ 0.1) = ln 9 ≈ 2.1972. Bisection works for any increasing function, even when no formula for the inverse exists.</p>',
           'O(log(1/ε))', 'O(1)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'If f(x) = 3x − 2, what is f(4)?', ['10', '12', '14', '6'], 0, 'Replace x with 4.', '3 × 4 − 2 = 12 − 2 = 10.')
K.quiz('e', 'What is the slope of y = −2x + 7?', ['7', '−2', '2', '−7'], 1, 'In y = mx + b, the slope is m.', 'The number in front of x is −2, so the line falls by 2 for every step to the right.')
K.quiz('e', 'What is log₁₀ 1000?', ['2', '3', '10', '100'], 1, 'How many tens multiply to 1000?', '10 × 10 × 10 = 1000, so the power is 3.')
K.quiz('e', 'What value does the sigmoid give at z = 0?', ['0', '0.5', '1', 'e'], 1, 'e⁰ = 1.', 'σ(0) = 1 ÷ (1 + 1) = 0.5, exactly the middle.')
K.quiz('e', 'What is ReLU(−3)?', ['−3', '0', '3', '1'], 1, 'ReLU = max(0, z).', 'max(0, −3) = 0. ReLU blocks negative values.')
K.quiz('m', 'Which equation has no real roots?', ['x² − 4 = 0', 'x² + 2x + 1 = 0', 'x² + x + 5 = 0', 'x² − 5x + 6 = 0'], 2, 'Check the discriminant b² − 4ac.', 'For x² + x + 5, D = 1 − 20 = −19, which is negative, so the parabola never touches y = 0.')
K.quiz('m', 'ln(a) + ln(b) equals', ['ln(a + b)', 'ln(ab)', 'ln(a) × ln(b)', 'ln(a ÷ b)'], 1, 'Logs turn multiplying into adding.', 'The product rule: ln(ab) = ln a + ln b.')
K.quiz('m', 'A line passes through (0, 4) and (2, 10). What is its equation?', ['y = 3x + 4', 'y = 4x + 3', 'y = 2x + 4', 'y = 3x + 10'], 0, 'The point with x = 0 gives the intercept.', 'Slope (10 − 4) ÷ (2 − 0) = 3, intercept 4, so y = 3x + 4.')
K.quiz('m', 'Why do ML libraries add log probabilities instead of multiplying probabilities?', ['Adding is more accurate for whole numbers', 'A product of many small numbers rounds to zero', 'Logs make the probabilities bigger than 1', 'Multiplication is not allowed on GPUs'], 1, 'Try multiplying 0.1 by itself 400 times.', 'The product underflows to 0.0 in floating point. The sum of logs stays a manageable number such as −921.')
K.quiz('m', 'Where is the vertex of y = 2x² − 8x + 1?', ['x = −2', 'x = 2', 'x = 4', 'x = 8'], 1, 'Vertex at x = −b ÷ 2a.', '−(−8) ÷ (2 × 2) = 8 ÷ 4 = 2.')
K.quiz('h', 'What is logit(0.75)?', ['ln 3', 'ln 0.75', '3', '0.75'], 0, 'logit(p) = ln(p ÷ (1 − p)).', '0.75 ÷ 0.25 = 3, so logit(0.75) = ln 3 ≈ 1.0986.')
K.quiz('h', 'The graph of g(x) = f(x − 3) + 2 is the graph of f moved', ['3 left and 2 up', '3 right and 2 up', '3 right and 2 down', '2 right and 3 up'], 1, 'Subtracting inside the bracket moves right.', 'x − 3 inside moves the graph right by 3, and + 2 outside moves it up by 2.')
K.quiz('h', 'Which activation outputs values centred on zero?', ['Sigmoid', 'ReLU', 'Tanh', 'Step function'], 2, 'Look at the output range.', 'tanh gives values from −1 to 1 with tanh(0) = 0. Sigmoid is centred on 0.5 and ReLU is never negative.')
K.quiz('x', 'If f(x) = eˣ and g(x) = 2x + 1, what is f(g(0))?', ['1', 'e', '2e', 'e²'], 1, 'Inside first: g(0).', 'g(0) = 1, then f(1) = e¹ = e ≈ 2.718.')
K.quiz('x', 'σ(z) = 0.2. What is σ(−z)?', ['0.2', '−0.2', '0.8', '5'], 2, 'The sigmoid has a symmetry: σ(−z) = 1 − σ(z).', '1 − 0.2 = 0.8. The S curve is symmetric about the point (0, 0.5).')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Find the slope of the line through (1, 2) and (5, 14).', '3', 'Slope = rise ÷ run.', [
    'Rise is the change in y: <span class="eq">14 − 2 = 12</span>',
    'Run is the change in x: <span class="eq">5 − 1 = 4</span>',
    'Slope: <span class="eq">m = 12 ÷ 4 = 3</span>',
    'So y climbs 3 for every step of 1 in x.',
], check=(14 - 2) / (5 - 1))
K.calc('e', 'If f(x) = x² − 3x + 2, what is f(5)?', '12', 'Put 5 wherever you see x.', [
    'Replace x with 5: <span class="eq">f(5) = 5² − 3 × 5 + 2</span>',
    'Power first: <span class="eq">5² = 25</span>',
    'Then the multiplication: <span class="eq">3 × 5 = 15</span>',
    'Add and subtract from left to right: <span class="eq">25 − 15 + 2 = 12</span>',
], check=5 ** 2 - 3 * 5 + 2)
K.calc('e', 'What is log₂ 32?', '5', 'How many 2s multiply to make 32?', [
    'Keep doubling from 1: 2, 4, 8, 16, 32.',
    'That took 5 doublings, so <span class="eq">2⁵ = 32</span>',
    'The log is the exponent: <span class="eq">log₂ 32 = 5</span>',
    'In computing this means 32 different values need 5 bits.',
], check=5)
K.calc('e', 'A taxi charges 40 to start plus 15 per km. What does a 6 km ride cost?', '130', 'Use y = 15x + 40.', [
    'The line is <span class="eq">y = 15x + 40</span>, with slope 15 per km and intercept 40.',
    'Put in x = 6: <span class="eq">15 × 6 = 90</span>',
    'Add the starting charge: <span class="eq">90 + 40 = 130</span>',
    'So the ride costs 130.',
], check=15 * 6 + 40)
K.calc('m', 'Solve x² − 7x + 10 = 0 and give the larger root.', '5', 'Use the quadratic formula or find two numbers that multiply to 10 and add to 7.', [
    'a = 1, b = −7, c = 10.',
    'Discriminant: <span class="eq">(−7)² − 4 × 1 × 10 = 49 − 40 = 9</span>, and √9 = 3.',
    'Formula: <span class="eq">x = (7 ± 3) ÷ 2</span>',
    'Roots: <span class="eq">10 ÷ 2 = 5</span> and <span class="eq">4 ÷ 2 = 2</span>',
    'Check: 5 × 2 = 10 and 5 + 2 = 7, so x² − 7x + 10 = (x − 2)(x − 5). The larger root is 5.',
], check=5)
K.calc('m', 'Work out log₃ 81 + log₃ 9 using the log rules.', '6', 'log a + log b = log(ab), or find each log separately.', [
    'Separately: 3⁴ = 81, so <span class="eq">log₃ 81 = 4</span>',
    'And 3² = 9, so <span class="eq">log₃ 9 = 2</span>',
    'Add: <span class="eq">4 + 2 = 6</span>',
    'Rule check: log₃(81 × 9) = log₃ 729, and 3⁶ = 729. Same answer.',
], check=6)
K.calc('m', 'Find σ(2), the sigmoid of 2. Use e² ≈ 7.389 and round to 3 decimals.', '0.881', 'σ(z) = 1 ÷ (1 + e^(−z)), and e^(−2) = 1 ÷ e².', [
    'First e^(−2): <span class="eq">e^(−2) = 1 ÷ 7.389 ≈ 0.1353</span>',
    'Add 1: <span class="eq">1 + 0.1353 = 1.1353</span>',
    'Flip it: <span class="eq">1 ÷ 1.1353 ≈ 0.8808</span>',
    'Rounded: 0.881. A score of 2 means the model is about 88% sure the answer is yes.',
], check=0.881, tol=0.0006)
K.calc('m', 'Money grows by 5% a year. How much is 2000 after 2 years? Give 2 decimals.', '2205', 'Each year multiply by 1.05.', [
    'Growth of 5% means multiply by <span class="eq">1 + 5 ÷ 100 = 1.05</span>',
    'After year 1: <span class="eq">2000 × 1.05 = 2100</span>',
    'After year 2: <span class="eq">2100 × 1.05 = 2205</span>',
    'Formula: 2000 × 1.05² = 2000 × 1.1025 = 2205.00.',
], check=2000 * 1.05 ** 2, alt=['2205.00'], tol=1e-6)
K.calc('h', 'A population of 500 doubles every 3 days. How many days until it reaches 8000?', '12', '8000 ÷ 500 tells you how many times it doubles.', [
    'Growth factor needed: <span class="eq">8000 ÷ 500 = 16</span>',
    'Number of doublings: <span class="eq">log₂ 16 = 4</span> because 2⁴ = 16',
    'Each doubling takes 3 days: <span class="eq">4 × 3 = 12</span> days',
    'Check: 500 → 1000 → 2000 → 4000 → 8000 is four doublings.',
], check=3 * 4)
K.calc('h', 'Solve eˣ = 20. Use ln 20 ≈ 2.9957 and round to 2 decimals.', '3', 'Take the natural log of both sides.', [
    'ln undoes eˣ, so take ln of both sides: <span class="eq">ln(eˣ) = ln 20</span>',
    'The left side is just x: <span class="eq">x = ln 20</span>',
    'Use the value given: <span class="eq">x ≈ 2.9957 ≈ 3.00</span>',
    'Check: e³ ≈ 20.09, which is very close to 20.',
], check=2.9957, tol=0.006, alt=['3.00'])
K.calc('h', 'What is logit(0.8)? Use ln 4 ≈ 1.386 and round to 3 decimals.', '1.386', 'logit(p) = ln(p ÷ (1 − p)).', [
    'Odds: <span class="eq">0.8 ÷ (1 − 0.8) = 0.8 ÷ 0.2 = 4</span>',
    'Log of the odds: <span class="eq">ln 4 ≈ 1.386</span>',
    'So the score that gives probability 0.8 is about 1.386.',
    'Check: σ(1.386) = 1 ÷ (1 + e^(−1.386)) = 1 ÷ (1 + 0.25) = 0.8.',
], check=1.386, tol=0.0006)
K.calc('x', 'A model gives the correct classes probabilities 0.5, 0.25 and 0.125. What is the sum of log₂ of these three numbers?', '-6', 'log₂ of 1/2, 1/4 and 1/8.', [
    '<span class="eq">log₂ 0.5 = log₂ 2⁻¹ = −1</span>',
    '<span class="eq">log₂ 0.25 = log₂ 2⁻² = −2</span>',
    '<span class="eq">log₂ 0.125 = log₂ 2⁻³ = −3</span>',
    'Add: <span class="eq">−1 − 2 − 3 = −6</span>',
    'Check with the product: 0.5 × 0.25 × 0.125 = 1/64 = 2⁻⁶. The sum of logs is the log of the product.',
], check=-6, alt=['−6'])
K.calc('x', 'For logistic regression p = σ(2x − 4), at what x is p exactly 0.5?', '2', 'σ(z) = 0.5 exactly when z = 0.', [
    'The sigmoid equals 0.5 only at <span class="eq">z = 0</span> because σ(0) = 1 ÷ (1 + 1).',
    'So set the inside to zero: <span class="eq">2x − 4 = 0</span>',
    'Solve: <span class="eq">2x = 4, x = 2</span>',
    'This x is the <b>decision boundary</b>: above it the model says yes, below it says no.',
], check=2)

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { esc, $, shell, seg, wireSeg, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;

  /* ----- explore a family of functions with sliders and an x to evaluate ----- */
  W.fnplot = el => {
    const b = shell(el, 'Function explorer', 'Pick a family, move the sliders to change a, b and c, and type an x to read f(x) from the graph.');
    const FAM = {
      line: { t: 'f(x) = a·x + b', f: (x, a, B) => a * x + B, a: [-3, 3, 1, 0.1], b: [-5, 5, 1, 0.5], c: null, y: [-6, 6] },
      quad: { t: 'f(x) = a·x² + b·x + c', f: (x, a, B, c) => a * x * x + B * x + c, a: [-2, 2, 1, 0.1], b: [-4, 4, -2, 0.5], c: [-5, 5, -1, 0.5], y: [-6, 6] },
      exp: { t: 'f(x) = a · bˣ', f: (x, a, B) => a * Math.pow(B, x), a: [0.2, 3, 1, 0.1], b: [0.2, 3, 2, 0.1], c: null, y: [-1, 10] },
      log: { t: 'f(x) = a · ln(x) + b', f: (x, a, B) => x > 0 ? a * Math.log(x) + B : NaN, a: [-3, 3, 1, 0.1], b: [-3, 3, 0, 0.5], c: null, y: [-5, 5] },
      sig: { t: 'f(x) = 1 / (1 + e^(−(a·x + b)))', f: (x, a, B) => 1 / (1 + Math.exp(-(a * x + B))), a: [-4, 4, 1, 0.1], b: [-4, 4, 0, 0.5], c: null, y: [-0.2, 1.2] },
    };
    b.innerHTML = `<div class="vz-row">${seg('fam', [['line', '📈 Line'], ['quad', '🪣 Quadratic'], ['exp', '🚀 Exponential'], ['log', '🪵 Logarithm'], ['sig', '〰️ Sigmoid']], 'line')}</div>
      <div class="mv-wrap"><div class="fp-plot"></div><div class="mv-side"><div class="mv-read fp-rule"></div><div class="fp-sl"></div>
      <div class="mv-inp">x = <input type="number" value="1" step="0.5" aria-label="x value"></div><div class="mv-read fp-out" aria-live="polite"></div></div></div>`;
    let fam = 'line', P = {};
    function sliders() {
      const F = FAM[fam];
      P = { a: F.a[2], b: F.b[2], c: F.c ? F.c[2] : 0 };
      $('.fp-sl', b).innerHTML = ['a', 'b', 'c'].filter(k => F[k]).map(k => slider(k, k, F[k][0], F[k][1], F[k][2], F[k][3])).join('<br>');
      ['a', 'b', 'c'].filter(k => F[k]).forEach(k => wireSlider(b, k, v => { P[k] = v; draw(); }));
      $('.fp-rule', b).innerHTML = `<b>${F.t}</b>`;
      draw();
    }
    function draw() {
      const F = FAM[fam], G = MV.frame(520, 380, [-5, 5], F.y);
      const f = x => F.f(x, P.a, P.b, P.c);
      const x0 = +$('input[type=number]', b).value;
      const y0 = f(x0);
      let s = MV.axes(G, { xl: 'x', yl: 'f(x)' }) + MV.curve(G, f);
      if (isFinite(y0) && y0 >= F.y[0] && y0 <= F.y[1] && x0 >= -5 && x0 <= 5) s += MV.line(G, x0, 0, x0, y0) + MV.line(G, 0, y0, x0, y0) + MV.dot(G, x0, y0, 'o');
      $('.fp-plot', b).innerHTML = MV.svg(G, s, F.t);
      let note = '';
      if (fam === 'quad' && P.a) { const vx = -P.b / (2 * P.a), D = P.b * P.b - 4 * P.a * P.c; note = `Vertex at x = ${MV.num(vx)}. Discriminant ${MV.num(D)}: ${D > 0 ? 'two roots' : D === 0 ? 'one root' : 'no real roots'}.`; }
      if (fam === 'line') note = `Slope ${MV.num(P.a)}: y ${P.a > 0 ? 'climbs' : P.a < 0 ? 'falls' : 'stays flat'} by ${MV.num(Math.abs(P.a))} per step.`;
      if (fam === 'exp') note = P.b > 1 ? 'b above 1: growth.' : P.b < 1 ? 'b below 1: decay towards 0.' : 'b = 1: a flat line.';
      if (fam === 'log') note = 'ln only accepts x above 0, so the curve stops at the y axis.';
      if (fam === 'sig') note = `The middle (f = 0.5) sits at x = ${P.a ? MV.num(-P.b / P.a) : 'nowhere'}. Bigger a makes the S steeper.`;
      $('.fp-out', b).innerHTML = (isFinite(y0) ? `f(${MV.num(x0)}) = <span class="big">${MV.num(y0, 4)}</span>` : `f(${MV.num(x0)}) is not defined`) + `<br>${note}`;
    }
    $('input[type=number]', b).addEventListener('input', draw);
    wireSeg(b, 'fam', v => { fam = v; sliders(); });
    sliders();
  };

  /* ----- drag two points, read the line through them ----- */
  W.line2pt = el => {
    const b = shell(el, 'Drag two points to make a line', 'Drag the orange dots. The slope, the intercept and the equation update as you move them.');
    b.innerHTML = `<div class="mv-wrap"><div class="l2-plot"></div><div class="mv-side"><div class="mv-read l2-out" aria-live="polite"></div></div></div>`;
    const G = MV.frame(520, 380, [-6, 6], [-6, 6]);
    const pts = [[-3, -2], [2, 3]];
    const host = $('.l2-plot', b);
    host.innerHTML = MV.svg(G, '<g class="l2-g"></g>', 'Two points and the line through them');
    const svgEl = $('svg', host);
    function draw() {
      const [[x1, y1], [x2, y2]] = pts;
      let s = MV.axes(G);
      if (Math.abs(x2 - x1) > 1e-6) {
        const m = (y2 - y1) / (x2 - x1), c = y1 - m * x1;
        s += MV.curve(G, x => m * x + c) + MV.line(G, x1, y1, x2, y1) + MV.line(G, x2, y1, x2, y2);
        s += MV.text(G, (x1 + x2) / 2, y1, `run ${MV.num(x2 - x1, 1)}`, { dy: y2 > y1 ? 16 : -8, anchor: 'middle', cls: 'sm' });
        s += MV.text(G, x2, (y1 + y2) / 2, `rise ${MV.num(y2 - y1, 1)}`, { dx: 8, cls: 'sm' });
        $('.l2-out', b).innerHTML = `Points (${MV.num(x1, 1)}, ${MV.num(y1, 1)}) and (${MV.num(x2, 1)}, ${MV.num(y2, 1)})<br>slope m = ${MV.num(y2 - y1, 1)} ÷ ${MV.num(x2 - x1, 1)} = <b>${MV.num(m)}</b><br>intercept b = <b>${MV.num(c)}</b><br><span class="big">y = ${MV.num(m)}x ${c < 0 ? '−' : '+'} ${MV.num(Math.abs(c))}</span>`;
      } else $('.l2-out', b).innerHTML = 'Both points have the same x, so the line is vertical. Its slope is undefined (division by zero), and it is not a function.';
      pts.forEach(([x, y], i) => { s += `<circle class="mv-pt o big mv-drag" data-h="${i}" cx="${G.sx(x)}" cy="${G.sy(y)}" r="11"/>`; });
      $('.l2-g', svgEl).innerHTML = s;
    }
    MV.drag(svgEl, G, pts.map((p, i) => ({ set: (x, y) => { pts[i] = [Math.round(x * 2) / 2, Math.round(y * 2) / 2]; } })), draw);
    draw();
  };

  /* ----- the activation functions on one chart ----- */
  W.actplot = el => {
    const b = shell(el, 'Activation functions side by side', 'Slide z and read off each function. Notice where each one goes flat.');
    b.innerHTML = `<div class="mv-wrap"><div class="ap-plot"></div><div class="mv-side">${slider('z', 'z', -5, 5, 1, 0.1)}<div class="mv-legend"><span><i></i>sigmoid</span><span><i class="o"></i>tanh</span><span><i class="g"></i>ReLU</span></div><div class="mv-read ap-out" aria-live="polite"></div></div></div>`;
    const G = MV.frame(520, 360, [-5, 5], [-1.5, 3]);
    const sg = z => 1 / (1 + Math.exp(-z));
    let z = 1;
    function draw() {
      let s = MV.axes(G) + MV.curve(G, sg) + MV.curve(G, Math.tanh, 'c2') + MV.curve(G, x => Math.max(0, x), 'c3');
      s += MV.line(G, z, -1.5, z, 3) + MV.dot(G, z, sg(z)) + MV.dot(G, z, Math.tanh(z), 'o') + MV.dot(G, z, Math.max(0, z), 'g');
      $('.ap-plot', b).innerHTML = MV.svg(G, s, 'Sigmoid, tanh and ReLU');
      const ds = sg(z) * (1 - sg(z)), dt = 1 - Math.tanh(z) ** 2;
      $('.ap-out', b).innerHTML = `z = <b>${MV.num(z, 1)}</b><br>sigmoid = <b>${MV.num(sg(z), 4)}</b> (slope ${MV.num(ds, 3)})<br>tanh = <b>${MV.num(Math.tanh(z), 4)}</b> (slope ${MV.num(dt, 3)})<br>ReLU = <b>${MV.num(Math.max(0, z), 2)}</b> (slope ${z > 0 ? 1 : 0})<br>${Math.abs(z) > 3 ? '⚠️ Sigmoid and tanh are almost flat here. Learning through them becomes very slow.' : 'In the middle, sigmoid and tanh change quickly.'}`;
    }
    wireSlider(b, 'z', v => { z = v; draw(); });
    draw();
  };

  /* ----- a function and its inverse are mirror images in y = x ----- */
  W.mirror = el => {
    const b = shell(el, 'A function and its inverse are mirror images', 'Pick a pair and slide x. The point (x, f(x)) and its swapped partner (f(x), x) sit on opposite sides of the dashed line y = x.');
    b.innerHTML = `<div class="vz-row">${seg('p', [['exp', 'eˣ and ln x'], ['sq', 'x² and √x'], ['sig', 'sigmoid and logit']], 'exp')}</div>
      <div class="mv-wrap"><div class="mi-plot"></div><div class="mv-side">${slider('x', 'x', -2, 2, 0.5, 0.05)}<div class="mv-read mi-out" aria-live="polite"></div></div></div>`;
    const PAIRS = {
      exp: { f: Math.exp, g: Math.log, r: [-3, 5], dom: [-2, 1.5], fn: 'eˣ', gn: 'ln' },
      sq: { f: x => x * x, g: Math.sqrt, r: [-1, 5], dom: [0, 2], fn: 'x²', gn: '√' },
      sig: { f: x => 1 / (1 + Math.exp(-x)), g: p => Math.log(p / (1 - p)), r: [-4, 4], dom: [-3, 3], fn: 'σ', gn: 'logit' },
    };
    let p = 'exp', x = 0.5;
    function draw() {
      const P = PAIRS[p], G = MV.frame(440, 440, P.r, P.r);
      const xx = Math.max(P.dom[0], Math.min(P.dom[1], x)), y = P.f(xx);
      let s = MV.axes(G) + MV.curve(G, t => t, 'mv-curve thin dash c4') + MV.curve(G, P.f) + MV.curve(G, P.g, 'c2');
      s += MV.line(G, xx, y, y, xx) + MV.dot(G, xx, y) + MV.dot(G, y, xx, 'o');
      $('.mi-plot', b).innerHTML = MV.svg(G, s, 'A function and its inverse');
      $('.mi-out', b).innerHTML = `<span style="color:var(--accent)">●</span> ${P.fn}(${MV.num(xx)}) = <b>${MV.num(y, 4)}</b><br><span style="color:var(--orange)">●</span> ${P.gn}(${MV.num(y, 4)}) = <b>${MV.num(xx, 4)}</b><br>Swapping the two coordinates reflects a point in the line y = x, so the inverse curve is the mirror image.`;
    }
    wireSeg(b, 'p', v => {
      p = v; const s = $('[data-sl="x"]', b), D = PAIRS[v].dom;
      s.min = D[0]; s.max = D[1]; x = Math.max(D[0], Math.min(D[1], x)); s.value = x; $('[data-slv="x"]', b).textContent = x; draw();
    });
    wireSlider(b, 'x', v => { x = v; draw(); });
    const s0 = $('[data-sl="x"]', b); s0.min = -2; s0.max = 1.5;
    draw();
  };
})();
'''

# ---------------------------------------------------------------- deeper explanations and extra animations
# Each lesson above gives the short version. DEEPER adds a slower, fuller explanation (and sometimes an
# animation) to the end of the lesson with the same id.
DEEPER = {
    'functions': deep('piecewise functions and functions you can undo', f'''
<p>Many real rules change their formula part way along. These are <b>piecewise functions</b>: a different rule for each piece of the input. A mobile data plan that is free up to 2 GB and then charges per extra GB is one. So is ReLU, which is 0 for negative inputs and x for positive ones.</p>
{fx('A piecewise function', 'f(x) = 0 if x &lt; 0, and f(x) = x if x ≥ 0', 'This is ReLU. Each piece is simple, and together they make a bend that a neural network can use to build curved shapes.')}
<p>Two more words describe how a function behaves, and both matter later.</p>
{table(['Word', 'Meaning', 'Example', 'Why ML cares'], [
        ['increasing', 'a bigger input always gives a bigger (or equal) output', 'eˣ, the sigmoid, ln x', 'the order of scores is kept, so the biggest logit is still the biggest probability'],
        ['one to one', 'no two inputs share an output', '2x + 1 yes, x² no (since 3² = (−3)² = 9)', 'only one to one functions can be undone exactly, which is why logit can undo sigmoid'],
        ['bounded', 'outputs stay between two fixed numbers', 'sigmoid between 0 and 1', 'good for probabilities, but flat ends slow down learning'],
    ])}
<p>A useful way to think about any model: the input is the question, the function is the "rule of thumb" the model learned, and the output is its answer. Training only changes the rule, never the idea that one input gives one answer.</p>
'''),
    'lines': deep('building a line from what you know, and measuring how far off it is', f'''
<p>There are three common ways to write the same straight line. Pick whichever matches the facts you have.</p>
{table(['Form', 'Formula', 'Use it when you know'], [
        ['slope intercept', 'y = mx + b', 'the slope and where it crosses the y axis'],
        ['point slope', 'y − y₁ = m(x − x₁)', 'the slope and any one point on the line'],
        ['two point', 'm = (y₂ − y₁) ÷ (x₂ − x₁), then point slope', 'two points on the line'],
    ])}
{worked('Line through (2, 7) and (5, 13), then a prediction', [
        'Slope: <span class="eq">m = (13 − 7) ÷ (5 − 2) = 6 ÷ 3 = 2</span>',
        'Point slope with (2, 7): <span class="eq">y − 7 = 2(x − 2)</span>',
        'Tidy up: <span class="eq">y = 2x − 4 + 7 = 2x + 3</span>',
        'Check with the other point: <span class="eq">2 × 5 + 3 = 13</span> ✓',
        'Predict at x = 10: <span class="eq">y = 2 × 10 + 3 = 23</span>'])}
<p>Real data never sits exactly on a line. The vertical gap between a data point and the line, actual minus predicted, is called the <b>residual</b>. A positive residual means the point is above the line (the model guessed too low). Linear regression picks the line that makes the sum of the squared residuals as small as possible, which Chapter 11 works out in full.</p>
{life('A gym membership that costs 1000 to join and 500 a month is the line cost = 500 × months + 1000. After a year you have paid 500 × 12 + 1000 = 7000.')}
'''),
    'quadratic': deep('completing the square, and where the bottom of the U comes from', f'''
<p>The vertex formula x = −b ÷ 2a is not magic. Rewrite the quadratic so the x appears only once, inside a square. This trick is called <b>completing the square</b>.</p>
{worked('Find the lowest point of f(x) = x² − 6x + 11', [
        'Take half of the middle number: half of −6 is −3, and (−3)² = 9.',
        'Add and subtract 9: <span class="eq">x² − 6x + 9 − 9 + 11</span>',
        'The first three terms form a perfect square: <span class="eq">(x − 3)² + 2</span>',
        'A square is never negative, so the smallest it can be is 0, when x = 3.',
        'So the vertex is <span class="eq">(3, 2)</span>. The formula agrees: <span class="eq">x = −(−6) ÷ (2 × 1) = 3</span>'])}
{fx('Vertex form', 'f(x) = a(x − h)² + k', 'The vertex is (h, k). If a &gt; 0 the curve opens upward and k is the lowest value. If a &lt; 0 it opens downward and k is the highest.')}
<p>Play with the three numbers a, b and c below. Watch how a controls the width and direction, how c lifts the whole curve, and how the roots appear and vanish as the discriminant changes sign.</p>
{viz('quadplot')}
{ml('The mean squared error of a one weight model, L(w) = average of (wxᵢ − yᵢ)², expands into a quadratic in w: (average of xᵢ²) w² − 2 (average of xᵢyᵢ) w + (average of yᵢ²). Its vertex gives the best weight directly: w = average of xᵢyᵢ ÷ average of xᵢ². That is linear regression without an intercept, solved by school algebra.')}
'''),
    'exponential': deep('doubling time, half life and the hunt for e', f'''
<p>Exponential change has a fixed <b>doubling time</b> (for growth) or <b>half life</b> (for decay). It does not matter where you start: the time to double from 10 to 20 is the same as from 1000 to 2000.</p>
{fxs(fx('Doubling time', f'T₂ = {frac("ln 2", "k")} ≈ {frac("0.693", "k")}', 'For growth A₀e^(kt). The "rule of 72" says money at r% a year doubles in about 72 ÷ r years.'),
         fx('Half life', f'T½ = {frac("ln 2", "k")} for A₀e^(−kt)', 'Carbon 14 has a half life of about 5730 years, which is how old bones are dated.'))}
<p>Now the hunt for e. Put 1 rupee in a bank that pays 100% interest a year, but split the year into n equal periods. Each period pays 100% ÷ n, so after a year you have (1 + 1/n)ⁿ. Press Play to split the year finer and finer and watch the amount creep up and then settle.</p>
{viz('compound')}
<p>It never passes 2.71828... however often the bank pays. That ceiling is e. It is the natural growth number because <b>eˣ grows at a rate equal to its own size</b>: at every moment its slope equals its height. No other base has that property, which is why calculus and probability formulas are written with e.</p>
{ml('Exponential moving averages in optimisers such as Adam (Chapter 8) give older gradients weights that decay like 0.9, 0.9², 0.9³ and so on. The "memory" of the average is about 1 ÷ (1 − 0.9) = 10 steps.')}
'''),
    'logs': deep('reading log scales and living with tiny probabilities', f'''
<p>On an ordinary scale, equal steps mean equal <b>differences</b>: 0, 10, 20, 30. On a log scale, equal steps mean equal <b>ratios</b>: 1, 10, 100, 1000. That is why log scales show things that span huge ranges, such as earthquake energy, sound, star brightness, the number of COVID cases, or the loss of a model during training.</p>
{viz('logscale')}
<p>Here is the probability problem in real numbers. Suppose a model gives each of 1000 training answers a probability of 0.9. The chance of getting them all is 0.9¹⁰⁰⁰. Work it out with logs: log₁₀(0.9¹⁰⁰⁰) = 1000 × log₁₀ 0.9 = 1000 × (−0.0458) = −45.8, so the product is about 10⁻⁴⁶. A float32 cannot even hold numbers below about 10⁻⁴⁵, so it would be stored as 0. In log form it is simply −45.8, a perfectly ordinary number.</p>
{table(['Probability p', 'ln p', 'Reading'], [
        ['1', '0', 'certain: no penalty'],
        ['0.5', '−0.693', 'a coin flip'],
        ['0.1', '−2.303', 'unlikely'],
        ['0.001', '−6.908', 'very unlikely'],
        ['→ 0', '→ −∞', 'impossible: an infinite penalty'],
    ])}
{trick('Log of a number between 0 and 1 is always negative. That is why losses are written as MINUS log probability, so that the loss is a positive number and smaller is better.')}
'''),
    'activation': deep('newer activations and why a network needs a bend at all', f'''
<p>Suppose every layer of a network were a straight line with no activation. Layer 1 gives 2x + 1, and layer 2 applied to that gives 3(2x + 1) − 4 = 6x − 1, another straight line. However many layers you stack, a composition of linear functions is still linear. The network could never learn a curve. The activation function is the bend that makes depth worth having.</p>
{table(['Activation', 'Formula', 'Where it is used'], [
        ['Leaky ReLU', 'max(0.01x, x)', 'keeps a small slope for negatives so neurons never fully die'],
        ['Softplus', 'ln(1 + eˣ)', 'a smooth ReLU whose slope is the sigmoid'],
        ['GELU', 'x · Φ(x), Φ is the normal CDF', 'BERT, GPT style transformers'],
        ['SiLU (Swish)', 'x · σ(x)', 'many modern networks, and inside the SwiGLU blocks of several large language models'],
    ])}
<p>GELU and SiLU look like ReLU from far away but are smooth near 0 and dip slightly below 0 for small negative inputs. That smoothness tends to make very deep networks train a little better, which is why newer models moved to them.</p>
{worked('Sigmoid by hand at z = 2', [
        '<span class="eq">e⁻² ≈ 0.1353</span>',
        '<span class="eq">1 + 0.1353 = 1.1353</span>',
        '<span class="eq">σ(2) = 1 ÷ 1.1353 ≈ 0.8808</span>',
        'So a score of 2 becomes a probability of about 88%. A score of −2 gives 1 − 0.8808 = 0.1192, by symmetry.'])}
'''),
    'compose': deep('finding an inverse step by step', f'''
<p>To find the inverse of a function, write y = f(x), swap the roles of x and y, and solve for y. Each step is plain algebra from Chapter 1.</p>
{worked('Derive the logit from the sigmoid', [
        'Start with <span class="eq">p = 1 ÷ (1 + e⁻ᶻ)</span>. We want z in terms of p.',
        'Flip both sides: <span class="eq">1 ÷ p = 1 + e⁻ᶻ</span>',
        'Subtract 1: <span class="eq">e⁻ᶻ = (1 − p) ÷ p</span>',
        'Take ln of both sides: <span class="eq">−z = ln((1 − p) ÷ p)</span>',
        'Multiply by −1 (the log of a flipped fraction changes sign): <span class="eq">z = ln(p ÷ (1 − p))</span>. That is the logit.'])}
<p>Only one to one functions have an inverse. x² is not one to one (both 3 and −3 give 9), so we restrict it to x ≥ 0 before saying √x is its inverse. The sigmoid is one to one because it always increases, so every probability strictly between 0 and 1 has exactly one score.</p>
{ml('In logistic regression the logit is linear in the inputs: ln(p ÷ (1 − p)) = w · x + b. So each weight wᵢ says how much the log odds change when feature i grows by 1. A weight of 0.693 doubles the odds, because e^0.693 = 2.')}
'''),
}
for _p in PARTS:
    _p['html'] += DEEPER.get(_p['id'], '')

VIZ_JS += r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;

  /* ----- y = ax² + bx + c with roots, vertex and discriminant ----- */
  W.quadplot = el => {
    const b = shell(el, 'Shape a parabola', 'Move a, b and c. The orange dot is the vertex, green dots are the roots. Press Play to slide c downward and watch the roots appear.');
    b.innerHTML = `<div class="mv-wrap"><div class="qp-plot"></div><div class="mv-side">${slider('a', 'a', -3, 3, 1, 0.1)}${slider('b', 'b', -6, 6, -2, 0.5)}${slider('c', 'c', -8, 8, 4, 0.5)}<div class="mv-read qp-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let A = 1, B = -2, C = 4;
    const G = MV.frame(440, 330, [-6, 6], [-10, 10]);
    function draw() {
      let s = MV.axes(G, { xstep: 2, ystep: 2, xl: 'x', yl: 'y' }) + MV.curve(G, x => A * x * x + B * x + C);
      const D = B * B - 4 * A * C, out = [`y = ${MV.num(A)}x² ${B < 0 ? '−' : '+'} ${MV.num(Math.abs(B))}x ${C < 0 ? '−' : '+'} ${MV.num(Math.abs(C))}`];
      if (Math.abs(A) < 1e-9) out.push('a = 0, so this is a straight line, not a parabola.');
      else {
        const h = -B / (2 * A), k = A * h * h + B * h + C;
        s += MV.dot(G, h, Math.max(-10, Math.min(10, k)), 'o', 7);
        out.push(`vertex x = −b ÷ 2a = <b>${MV.num(h)}</b>, y = <b>${MV.num(k)}</b> (${A > 0 ? 'lowest point' : 'highest point'})`, `discriminant D = b² − 4ac = <b>${MV.num(D)}</b>`);
        if (D > 1e-9) { const r1 = (-B - Math.sqrt(D)) / (2 * A), r2 = (-B + Math.sqrt(D)) / (2 * A); s += MV.dot(G, r1, 0, 'g', 6) + MV.dot(G, r2, 0, 'g', 6); out.push(`D &gt; 0: two roots, x = <b>${MV.num(Math.min(r1, r2))}</b> and <b>${MV.num(Math.max(r1, r2))}</b>`); }
        else if (Math.abs(D) <= 1e-9) { s += MV.dot(G, h, 0, 'g', 6); out.push(`D = 0: one root, x = <b>${MV.num(h)}</b>`); }
        else out.push('D &lt; 0: the curve never touches the x axis, so there are no real roots.');
      }
      $('.qp-plot', b).innerHTML = MV.svg(G, s, 'A parabola');
      $('.qp-out', b).innerHTML = out.join('<br>');
    }
    const setC = v => { C = v; $('[data-sl="c"]', b).value = v; $('[data-slv="c"]', b).textContent = v; };
    const P = Player($('.vz-p', b), t => { setC(4 - t * 0.5); draw(); }, 400);
    wireSlider(b, 'a', v => { A = v; draw(); });
    wireSlider(b, 'b', v => { B = v; draw(); });
    wireSlider(b, 'c', v => { P.pause(); C = v; draw(); });
    P.load(17, 0);
  };

  /* ----- compound interest creeping up to e ----- */
  W.compound = el => {
    const b = shell(el, 'Split the year finer and finer', 'Each step pays interest more often: once a year, twice, monthly, daily, every hour, every minute. Press Play or step through and watch (1 + 1/n)ⁿ settle at e.');
    const NS = [1, 2, 3, 4, 6, 12, 52, 365, 8760, 525600];
    const names = ['once a year', 'twice a year', 'three times', 'every quarter', 'every 2 months', 'every month', 'every week', 'every day', 'every hour', 'every minute'];
    b.innerHTML = `<div class="mv-wrap"><div class="cp-plot"></div><div class="mv-side"><div class="mv-read cp-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const G = MV.frame(440, 300, [0, NS.length + 0.5], [1.8, 2.85]);
    function show(t) {
      let s = MV.axes(G, { labels: false });
      [2, 2.2, 2.4, 2.6, 2.8].forEach(y => { s += MV.text(G, 0, y, MV.num(y, 1), { dx: 2, dy: 4, cls: 'sm' }); });
      s += MV.line(G, 0.3, Math.E, NS.length + 0.5, Math.E, 'mv-v r dash') + MV.text(G, NS.length + 0.4, Math.E, 'e = 2.71828', { dy: -6, anchor: 'end', cls: 'sm' });
      for (let k = 0; k <= t; k++) { const v = (1 + 1 / NS[k]) ** NS[k]; s += `<rect class="mv-bar ${k === t ? 'o' : ''}" x="${G.sx(k + 0.65)}" y="${G.sy(v)}" width="${G.sx(1.3) - G.sx(0.65) - 4}" height="${G.sy(1.8) - G.sy(v)}" rx="4"/>`; }
      $('.cp-plot', b).innerHTML = MV.svg(G, s, 'Amounts approaching e');
      const n = NS[t], v = (1 + 1 / n) ** n;
      $('.cp-out', b).innerHTML = `paid <b>${names[t]}</b><br>n = ${n.toLocaleString('en-US')}<br>each payment adds 1/${n.toLocaleString('en-US')} of the balance<br>amount = (1 + 1/n)ⁿ = <span class="big">${v.toFixed(6)}</span><br>gap to e: ${(Math.E - v).toFixed(6)}`;
    }
    const P = Player($('.vz-p', b), show, 1000);
    P.load(NS.length, 0);
  };

  /* ----- linear scale versus log scale, and the logs of one number ----- */
  W.logscale = el => {
    const b = shell(el, 'Normal scale versus log scale', 'The dots are 1, 10, 100, 1000 and 10000. On a normal scale they crowd at the left. On a log scale they sit evenly. Move the power of 10 to pick x and read its logs in three bases.');
    b.innerHTML = `<div class="vz-row">${seg('sc', [['lin', 'Normal scale'], ['log', 'Log scale']], 'log')}</div><div class="ls-plot"></div><div class="mv-wrap"><div class="mv-side">${slider('x', 'power of 10', 0, 4, 2, 0.05)}</div><div class="mv-read ls-out" aria-live="polite"></div></div><div class="vz-p"></div>`;
    let sc = 'log', e10 = 2;
    function draw() {
      const x = 10 ** e10, Wd = 520, H = 112, L = 30, R = Wd - 30;
      const pos = v => sc === 'log' ? L + Math.log10(v) / 4 * (R - L) : L + v / 10000 * (R - L);
      let s = `<line class="mv-axis" x1="${L}" y1="55" x2="${R}" y2="55"/>`;
      [1, 10, 100, 1000, 10000].forEach(v => { const p = pos(v); s += `<circle class="mv-pt" cx="${p}" cy="55" r="6"/>` + (sc === 'lin' && v < 1000 ? '' : `<text class="mv-tick" x="${p}" y="80" text-anchor="middle">${v.toLocaleString('en-US')}</text>`); });
      if (sc === 'lin') s += `<text class="mv-tick" x="${L - 4}" y="100" text-anchor="start">1, 10, 100 (squashed together)</text>`;
      s += `<circle class="mv-pt o big" cx="${pos(x)}" cy="55" r="8"/><text class="mv-lab" x="${pos(x)}" y="32" text-anchor="middle">x</text>`;
      $('.ls-plot', b).innerHTML = `<svg class="mv-svg" viewBox="0 0 ${Wd} ${H}" role="img" aria-label="Number line">${s}</svg>`;
      $('.ls-out', b).innerHTML = `x = <b>${MV.num(x, 2)}</b><br>log₁₀ x = <b>${MV.num(Math.log10(x), 3)}</b> (powers of 10)<br>log₂ x = <b>${MV.num(Math.log2(x), 3)}</b> (doublings)<br>ln x = <b>${MV.num(Math.log(x), 3)}</b> (base e)<br>ratio check: ln x ÷ log₁₀ x = ${e10 > 0.01 ? MV.num(Math.log(x) / Math.log10(x), 3) : '?'} = ln 10`;
    }
    const P = Player($('.vz-p', b), t => { e10 = t * 0.25; $('[data-sl="x"]', b).value = e10; $('[data-slv="x"]', b).textContent = MV.num(e10); draw(); }, 450);
    wireSeg(b, 'sc', v => { sc = v; draw(); });
    wireSlider(b, 'x', v => { P.pause(); e10 = v; draw(); });
    P.load(17, 8);
  };
})();
'''
CSS = r'''
.ls-plot .mv-svg{max-height:140px}
'''

T = K.topic(
    slug='functions-logs', topic='functions-logs', prefix='mm02', short='Functions and logs', emoji='📈',
    title='Functions, Graphs, Exponents and Logarithms',
    module=('🌱', 'School foundations', 'foundations', 'The school maths every model is written in: numbers, algebra, functions, exponents and logarithms.'),
    minutes=50,
    lead='Functions are the machines models are made of. Learn straight lines, parabolas, exponential growth, the number e, logarithms and the sigmoid, ReLU and tanh activations, with sliders and graphs you can drag.',
    desc='Functions, straight lines, quadratics, exponentials, e, logarithms, sigmoid, tanh, ReLU, composition and inverses for machine learning.',
    summary='Domain and range, slope and intercept, the quadratic formula and the vertex, exponential growth and e, log rules and why ML adds log probabilities, sigmoid, tanh and ReLU, composition, shifts and inverse functions such as logit.',
    keywords=['function', 'graph', 'slope', 'intercept', 'quadratic', 'parabola', 'exponential', 'euler number', 'logarithm', 'ln', 'sigmoid', 'tanh', 'ReLU', 'logit', 'inverse function', 'composition'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
