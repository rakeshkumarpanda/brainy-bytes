# Chapter 14: Taylor series, Newton's method, matrix calculus, automatic differentiation (forward and reverse),
# vanishing and exploding gradients, convexity with Jensen's inequality, and numerical stability
# (finite difference checks, log-sum-exp).
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz, deep

K = Kit()

# ---------------------------------------------------------------- programs
K.code('taylor_exp', py=r'''
import math


def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


for label, x in [("0.5", 0.5), ("2", 2.0)]:
    exact = math.exp(x)
    print(f"e^{label} = {f(exact)}")
    term, total = 1.0, 0.0
    for n in range(7):
        if n > 0:
            term *= x / n                 # x^n / n! built from the previous term
        total += term
        print(f"   order {n}: {f(total)}, error {f(exact - total)}")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

for (const [label, x] of [["0.5", 0.5], ["2", 2]]) {
  const exact = Math.exp(x);
  console.log(`e^${label} = ${f(exact)}`);
  let term = 1, total = 0;
  for (let n = 0; n < 7; n++) {
    if (n > 0) term *= x / n;             // x^n / n! built from the previous term
    total += term;
    console.log(`   order ${n}: ${f(total)}, error ${f(exact - total)}`);
  }
}
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

const cases: [string, number][] = [["0.5", 0.5], ["2", 2]];
for (const [label, x] of cases) {
  const exact: number = Math.exp(x);
  console.log(`e^${label} = ${f(exact)}`);
  let term = 1, total = 0;
  for (let n = 0; n < 7; n++) {
    if (n > 0) term *= x / n;             // x^n / n! built from the previous term
    total += term;
    console.log(`   order ${n}: ${f(total)}, error ${f(exact - total)}`);
  }
}
''', java=r'''
public class TaylorExp {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    public static void main(String[] args) {
        String[] labels = {"0.5", "2"};
        double[] xs = {0.5, 2.0};
        for (int c = 0; c < 2; c++) {
            double x = xs[c], exact = Math.exp(x);
            System.out.println("e^" + labels[c] + " = " + f(exact));
            double term = 1, total = 0;
            for (int n = 0; n < 7; n++) {
                if (n > 0) term *= x / n;     // x^n / n! built from the previous term
                total += term;
                System.out.println("   order " + n + ": " + f(total) + ", error " + f(exact - total));
            }
        }
    }
}
''')

K.code('newton', py=r'''
import math


def f(v):
    return f"{0.0 if abs(v) < 5e-11 else v:.10f}"


# 1. a root: solve x^2 - 2 = 0, so x becomes the square root of 2
x = 1.0
for k in range(1, 6):
    x = x - (x * x - 2) / (2 * x)         # jump to where the tangent line hits zero
    print(f"root step {k}: x = {f(x)}, error = {f(x - math.sqrt(2))}")

# 2. a minimum: g(x) = e^x - 2x, so g'(x) = e^x - 2 and g''(x) = e^x
x = 0.0
for k in range(1, 6):
    x = x - (math.exp(x) - 2) / math.exp(x)   # Newton on the slope: x - g'(x) / g''(x)
    print(f"min step {k}: x = {f(x)}")
print(f"exact minimum at ln 2 = {f(math.log(2))}")
''', js=r'''
const f = v => (Math.abs(v) < 5e-11 ? 0 : v).toFixed(10);

// 1. a root: solve x^2 - 2 = 0, so x becomes the square root of 2
let x = 1;
for (let k = 1; k < 6; k++) {
  x = x - (x * x - 2) / (2 * x);          // jump to where the tangent line hits zero
  console.log(`root step ${k}: x = ${f(x)}, error = ${f(x - Math.sqrt(2))}`);
}

// 2. a minimum: g(x) = e^x - 2x, so g'(x) = e^x - 2 and g''(x) = e^x
x = 0;
for (let k = 1; k < 6; k++) {
  x = x - (Math.exp(x) - 2) / Math.exp(x);   // Newton on the slope: x - g'(x) / g''(x)
  console.log(`min step ${k}: x = ${f(x)}`);
}
console.log(`exact minimum at ln 2 = ${f(Math.log(2))}`);
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-11 ? 0 : v).toFixed(10);

// 1. a root: solve x^2 - 2 = 0, so x becomes the square root of 2
let x: number = 1;
for (let k = 1; k < 6; k++) {
  x = x - (x * x - 2) / (2 * x);          // jump to where the tangent line hits zero
  console.log(`root step ${k}: x = ${f(x)}, error = ${f(x - Math.sqrt(2))}`);
}

// 2. a minimum: g(x) = e^x - 2x, so g'(x) = e^x - 2 and g''(x) = e^x
x = 0;
for (let k = 1; k < 6; k++) {
  x = x - (Math.exp(x) - 2) / Math.exp(x);   // Newton on the slope: x - g'(x) / g''(x)
  console.log(`min step ${k}: x = ${f(x)}`);
}
console.log(`exact minimum at ln 2 = ${f(Math.log(2))}`);
''', java=r'''
public class NewtonSteps {
    static String f(double v) {
        return String.format("%.10f", Math.abs(v) < 5e-11 ? 0.0 : v);
    }

    public static void main(String[] args) {
        // 1. a root: solve x^2 - 2 = 0, so x becomes the square root of 2
        double x = 1;
        for (int k = 1; k < 6; k++) {
            x = x - (x * x - 2) / (2 * x);    // jump to where the tangent line hits zero
            System.out.println("root step " + k + ": x = " + f(x) + ", error = " + f(x - Math.sqrt(2)));
        }
        // 2. a minimum: g(x) = e^x - 2x, so g'(x) = e^x - 2 and g''(x) = e^x
        x = 0;
        for (int k = 1; k < 6; k++) {
            x = x - (Math.exp(x) - 2) / Math.exp(x);   // Newton on the slope: x - g'(x) / g''(x)
            System.out.println("min step " + k + ": x = " + f(x));
        }
        System.out.println("exact minimum at ln 2 = " + f(Math.log(2)));
    }
}
''')

K.code('mat_grad', py=r'''
def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


def numeric_grad(fun, x, h=1e-5):         # central differences, one coordinate at a time
    g = []
    for i in range(len(x)):
        up = x[:]
        dn = x[:]
        up[i] += h
        dn[i] -= h
        g.append((fun(up) - fun(dn)) / (2 * h))
    return g


A = [[2, 1], [0, 3]]                      # not symmetric on purpose


def quad(x):                              # x^T A x
    return sum(x[i] * A[i][j] * x[j] for i in range(2) for j in range(2))


x = [1.0, 2.0]
rule = [sum((A[i][j] + A[j][i]) * x[j] for j in range(2)) for i in range(2)]   # (A + A^T) x
num = numeric_grad(quad, x)
print(f"x^T A x: rule (A + A^T)x = [{f(rule[0])}, {f(rule[1])}], numeric = [{f(num[0])}, {f(num[1])}]")

X = [[1, 1], [1, 2], [1, 3]]
y = [1, 2, 2]


def loss(w):                              # ||Xw - y||^2
    return sum((X[i][0] * w[0] + X[i][1] * w[1] - y[i]) ** 2 for i in range(3))


w = [0.0, 1.0]
r = [X[i][0] * w[0] + X[i][1] * w[1] - y[i] for i in range(3)]
rule = [2 * sum(X[i][j] * r[i] for i in range(3)) for j in range(2)]          # 2 X^T (Xw - y)
num = numeric_grad(loss, w)
print(f"least squares: rule 2X^T(Xw - y) = [{f(rule[0])}, {f(rule[1])}], numeric = [{f(num[0])}, {f(num[1])}]")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

function numericGrad(fun, x, h = 1e-5) {  // central differences, one coordinate at a time
  return x.map((_, i) => {
    const up = x.slice(), dn = x.slice();
    up[i] += h;
    dn[i] -= h;
    return (fun(up) - fun(dn)) / (2 * h);
  });
}

const A = [[2, 1], [0, 3]];               // not symmetric on purpose
const quad = x => { let s = 0; for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) s += x[i] * A[i][j] * x[j]; return s; };
const x = [1, 2];
let rule = [0, 1].map(i => (A[i][0] + A[0][i]) * x[0] + (A[i][1] + A[1][i]) * x[1]);   // (A + A^T) x
let num = numericGrad(quad, x);
console.log(`x^T A x: rule (A + A^T)x = [${f(rule[0])}, ${f(rule[1])}], numeric = [${f(num[0])}, ${f(num[1])}]`);

const X = [[1, 1], [1, 2], [1, 3]];
const y = [1, 2, 2];
const loss = w => X.reduce((s, row, i) => s + (row[0] * w[0] + row[1] * w[1] - y[i]) ** 2, 0);   // ||Xw - y||^2
const w = [0, 1];
const r = X.map((row, i) => row[0] * w[0] + row[1] * w[1] - y[i]);
rule = [0, 1].map(j => 2 * X.reduce((s, row, i) => s + row[j] * r[i], 0));          // 2 X^T (Xw - y)
num = numericGrad(loss, w);
console.log(`least squares: rule 2X^T(Xw - y) = [${f(rule[0])}, ${f(rule[1])}], numeric = [${f(num[0])}, ${f(num[1])}]`);
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

function numericGrad(fun: (v: number[]) => number, x: number[], h: number = 1e-5): number[] {
  return x.map((_, i) => {                // central differences, one coordinate at a time
    const up = x.slice(), dn = x.slice();
    up[i] += h;
    dn[i] -= h;
    return (fun(up) - fun(dn)) / (2 * h);
  });
}

const A: number[][] = [[2, 1], [0, 3]];   // not symmetric on purpose
const quad = (x: number[]): number => { let s = 0; for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) s += x[i] * A[i][j] * x[j]; return s; };
const x: number[] = [1, 2];
let rule: number[] = [0, 1].map(i => (A[i][0] + A[0][i]) * x[0] + (A[i][1] + A[1][i]) * x[1]);   // (A + A^T) x
let num: number[] = numericGrad(quad, x);
console.log(`x^T A x: rule (A + A^T)x = [${f(rule[0])}, ${f(rule[1])}], numeric = [${f(num[0])}, ${f(num[1])}]`);

const X: number[][] = [[1, 1], [1, 2], [1, 3]];
const y: number[] = [1, 2, 2];
const loss = (w: number[]): number => X.reduce((s, row, i) => s + (row[0] * w[0] + row[1] * w[1] - y[i]) ** 2, 0);   // ||Xw - y||^2
const w: number[] = [0, 1];
const r: number[] = X.map((row, i) => row[0] * w[0] + row[1] * w[1] - y[i]);
rule = [0, 1].map(j => 2 * X.reduce((s, row, i) => s + row[j] * r[i], 0));          // 2 X^T (Xw - y)
num = numericGrad(loss, w);
console.log(`least squares: rule 2X^T(Xw - y) = [${f(rule[0])}, ${f(rule[1])}], numeric = [${f(num[0])}, ${f(num[1])}]`);
''', java=r'''
import java.util.function.Function;

public class MatGrad {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    static double[] numericGrad(Function<double[], Double> fun, double[] x, double h) {
        double[] g = new double[x.length];    // central differences, one coordinate at a time
        for (int i = 0; i < x.length; i++) {
            double[] up = x.clone(), dn = x.clone();
            up[i] += h;
            dn[i] -= h;
            g[i] = (fun.apply(up) - fun.apply(dn)) / (2 * h);
        }
        return g;
    }

    public static void main(String[] args) {
        double[][] A = {{2, 1}, {0, 3}};      // not symmetric on purpose
        Function<double[], Double> quad = v -> {
            double s = 0;
            for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) s += v[i] * A[i][j] * v[j];
            return s;
        };
        double[] x = {1, 2};
        double[] rule = new double[2];
        for (int i = 0; i < 2; i++) rule[i] = (A[i][0] + A[0][i]) * x[0] + (A[i][1] + A[1][i]) * x[1];   // (A + A^T) x
        double[] num = numericGrad(quad, x, 1e-5);
        System.out.println("x^T A x: rule (A + A^T)x = [" + f(rule[0]) + ", " + f(rule[1]) + "], numeric = [" + f(num[0]) + ", " + f(num[1]) + "]");

        double[][] X = {{1, 1}, {1, 2}, {1, 3}};
        double[] y = {1, 2, 2};
        Function<double[], Double> loss = w -> {   // ||Xw - y||^2
            double s = 0;
            for (int i = 0; i < 3; i++) s += Math.pow(X[i][0] * w[0] + X[i][1] * w[1] - y[i], 2);
            return s;
        };
        double[] w = {0, 1};
        double[] r = new double[3];
        for (int i = 0; i < 3; i++) r[i] = X[i][0] * w[0] + X[i][1] * w[1] - y[i];
        for (int j = 0; j < 2; j++) {
            double s = 0;
            for (int i = 0; i < 3; i++) s += X[i][j] * r[i];
            rule[j] = 2 * s;                  // 2 X^T (Xw - y)
        }
        num = numericGrad(loss, w, 1e-5);
        System.out.println("least squares: rule 2X^T(Xw - y) = [" + f(rule[0]) + ", " + f(rule[1]) + "], numeric = [" + f(num[0]) + ", " + f(num[1]) + "]");
    }
}
''')

K.code('dual_numbers', py=r'''
import math


def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


# a dual number (value, slope) carries a derivative along with every value
def add(p, q):
    return (p[0] + q[0], p[1] + q[1])


def mul(p, q):                            # product rule
    return (p[0] * q[0], p[0] * q[1] + p[1] * q[0])


def dsin(p):                              # chain rule: (sin u)' = cos u times u'
    return (math.sin(p[0]), math.cos(p[0]) * p[1])


def num(c):                               # a plain number has slope 0
    return (c, 0.0)


x = (2.0, 1.0)                            # the seed: dx/dx = 1
y = add(mul(mul(x, x), dsin(x)), mul(num(3.0), x))     # x^2 sin x + 3x
print(f"f(2) = {f(y[0])}")
print(f"f'(2) from dual numbers = {f(y[1])}")
print(f"f'(2) from the rules    = {f(2 * 2 * math.sin(2) + 4 * math.cos(2) + 3)}")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

// a dual number [value, slope] carries a derivative along with every value
const add = (p, q) => [p[0] + q[0], p[1] + q[1]];
const mul = (p, q) => [p[0] * q[0], p[0] * q[1] + p[1] * q[0]];   // product rule
const dsin = p => [Math.sin(p[0]), Math.cos(p[0]) * p[1]];        // chain rule: (sin u)' = cos u times u'
const num = c => [c, 0];                  // a plain number has slope 0

const x = [2, 1];                         // the seed: dx/dx = 1
const y = add(mul(mul(x, x), dsin(x)), mul(num(3), x));     // x^2 sin x + 3x
console.log(`f(2) = ${f(y[0])}`);
console.log(`f'(2) from dual numbers = ${f(y[1])}`);
console.log(`f'(2) from the rules    = ${f(2 * 2 * Math.sin(2) + 4 * Math.cos(2) + 3)}`);
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

// a dual number [value, slope] carries a derivative along with every value
type Dual = [number, number];
const add = (p: Dual, q: Dual): Dual => [p[0] + q[0], p[1] + q[1]];
const mul = (p: Dual, q: Dual): Dual => [p[0] * q[0], p[0] * q[1] + p[1] * q[0]];   // product rule
const dsin = (p: Dual): Dual => [Math.sin(p[0]), Math.cos(p[0]) * p[1]];        // chain rule: (sin u)' = cos u times u'
const num = (c: number): Dual => [c, 0];  // a plain number has slope 0

const x: Dual = [2, 1];                   // the seed: dx/dx = 1
const y: Dual = add(mul(mul(x, x), dsin(x)), mul(num(3), x));     // x^2 sin x + 3x
console.log(`f(2) = ${f(y[0])}`);
console.log(`f'(2) from dual numbers = ${f(y[1])}`);
console.log(`f'(2) from the rules    = ${f(2 * 2 * Math.sin(2) + 4 * Math.cos(2) + 3)}`);
''', java=r'''
public class DualNumbers {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    // a dual number {value, slope} carries a derivative along with every value
    static double[] add(double[] p, double[] q) { return new double[]{p[0] + q[0], p[1] + q[1]}; }
    static double[] mul(double[] p, double[] q) { return new double[]{p[0] * q[0], p[0] * q[1] + p[1] * q[0]}; }   // product rule
    static double[] dsin(double[] p) { return new double[]{Math.sin(p[0]), Math.cos(p[0]) * p[1]}; }   // chain rule
    static double[] num(double c) { return new double[]{c, 0}; }   // a plain number has slope 0

    public static void main(String[] args) {
        double[] x = {2, 1};                  // the seed: dx/dx = 1
        double[] y = add(mul(mul(x, x), dsin(x)), mul(num(3), x));     // x^2 sin x + 3x
        System.out.println("f(2) = " + f(y[0]));
        System.out.println("f'(2) from dual numbers = " + f(y[1]));
        System.out.println("f'(2) from the rules    = " + f(2 * 2 * Math.sin(2) + 4 * Math.cos(2) + 3));
    }
}
''')

K.code('reverse_mode', py=r'''
import math


def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


# forward pass: f(x, y) = x * y + sin(x), every step written down (the "tape")
x, y = 2.0, 3.0
v1 = x * y
v2 = math.sin(x)
out = v1 + v2
print(f"forward: v1 = x*y = {f(v1)}, v2 = sin x = {f(v2)}, f = {f(out)}")

# backward pass: start with df/df = 1 and walk the tape in reverse
g_out = 1.0
g_v1 = g_out * 1                          # f = v1 + v2
g_v2 = g_out * 1
g_x = g_v1 * y                            # v1 = x * y
g_y = g_v1 * x
g_x += g_v2 * math.cos(x)                 # v2 = sin x, and x was used twice so the parts add
print(f"backward: df/dv1 = {f(g_v1)}, df/dv2 = {f(g_v2)}")
print(f"gradient: df/dx = {f(g_x)}, df/dy = {f(g_y)}")
print(f"check: y + cos x = {f(y + math.cos(x))}, x = {f(x)}")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

// forward pass: f(x, y) = x * y + sin(x), every step written down (the "tape")
const x = 2, y = 3;
const v1 = x * y;
const v2 = Math.sin(x);
const out = v1 + v2;
console.log(`forward: v1 = x*y = ${f(v1)}, v2 = sin x = ${f(v2)}, f = ${f(out)}`);

// backward pass: start with df/df = 1 and walk the tape in reverse
const gOut = 1;
const gV1 = gOut * 1;                     // f = v1 + v2
const gV2 = gOut * 1;
let gX = gV1 * y;                         // v1 = x * y
const gY = gV1 * x;
gX += gV2 * Math.cos(x);                  // v2 = sin x, and x was used twice so the parts add
console.log(`backward: df/dv1 = ${f(gV1)}, df/dv2 = ${f(gV2)}`);
console.log(`gradient: df/dx = ${f(gX)}, df/dy = ${f(gY)}`);
console.log(`check: y + cos x = ${f(y + Math.cos(x))}, x = ${f(x)}`);
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

// forward pass: f(x, y) = x * y + sin(x), every step written down (the "tape")
const x: number = 2, y: number = 3;
const v1: number = x * y;
const v2: number = Math.sin(x);
const out: number = v1 + v2;
console.log(`forward: v1 = x*y = ${f(v1)}, v2 = sin x = ${f(v2)}, f = ${f(out)}`);

// backward pass: start with df/df = 1 and walk the tape in reverse
const gOut: number = 1;
const gV1: number = gOut * 1;             // f = v1 + v2
const gV2: number = gOut * 1;
let gX: number = gV1 * y;                 // v1 = x * y
const gY: number = gV1 * x;
gX += gV2 * Math.cos(x);                  // v2 = sin x, and x was used twice so the parts add
console.log(`backward: df/dv1 = ${f(gV1)}, df/dv2 = ${f(gV2)}`);
console.log(`gradient: df/dx = ${f(gX)}, df/dy = ${f(gY)}`);
console.log(`check: y + cos x = ${f(y + Math.cos(x))}, x = ${f(x)}`);
''', java=r'''
public class ReverseMode {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    public static void main(String[] args) {
        // forward pass: f(x, y) = x * y + sin(x), every step written down (the "tape")
        double x = 2, y = 3;
        double v1 = x * y;
        double v2 = Math.sin(x);
        double out = v1 + v2;
        System.out.println("forward: v1 = x*y = " + f(v1) + ", v2 = sin x = " + f(v2) + ", f = " + f(out));
        // backward pass: start with df/df = 1 and walk the tape in reverse
        double gOut = 1;
        double gV1 = gOut * 1;                // f = v1 + v2
        double gV2 = gOut * 1;
        double gX = gV1 * y;                  // v1 = x * y
        double gY = gV1 * x;
        gX += gV2 * Math.cos(x);              // v2 = sin x, and x was used twice so the parts add
        System.out.println("backward: df/dv1 = " + f(gV1) + ", df/dv2 = " + f(gV2));
        System.out.println("gradient: df/dx = " + f(gX) + ", df/dy = " + f(gY));
        System.out.println("check: y + cos x = " + f(y + Math.cos(x)) + ", x = " + f(x));
    }
}
''')

K.code('vanishing', py=r'''
import math


def sci(v):                               # 0.000123 -> 1.23e-4, the same in every language
    if v == 0:
        return "0"
    k = math.floor(math.log10(abs(v)))
    p = 1.0
    for _ in range(abs(k)):
        p *= 10
    m = v * p if k < 0 else v / p
    s = f"{m:.2f}"
    if s == "10.00":                      # 9.997 rounds up, so move to the next power
        s = "1.00"
        k += 1
    return f"{s}e{k}"


# the gradient reaching the first layer is a product of one factor per layer:
# factor = (slope of the activation) x (weight)
cases = [("sigmoid, w = 1", 0.25 * 1), ("sigmoid, w = 4", 0.25 * 4), ("tanh, w = 1.5", 1.0 * 1.5), ("ReLU, w = 0.6", 1.0 * 0.6)]
for name, factor in cases:
    g = 1.0
    out = []
    for layer in range(1, 21):
        g *= factor
        if layer in (5, 10, 20):
            out.append(f"{layer} layers {sci(g)}")
    print(f"{name}: " + ", ".join(out))
''', js=r'''
function sci(v) {                         // 0.000123 -> 1.23e-4, the same in every language
  if (v === 0) return "0";
  let k = Math.floor(Math.log10(Math.abs(v)));
  let p = 1;
  for (let i = 0; i < Math.abs(k); i++) p *= 10;
  const m = k < 0 ? v * p : v / p;
  let s = m.toFixed(2);
  if (s === "10.00") {                    // 9.997 rounds up, so move to the next power
    s = "1.00";
    k += 1;
  }
  return `${s}e${k}`;
}

// the gradient reaching the first layer is a product of one factor per layer:
// factor = (slope of the activation) x (weight)
const cases = [["sigmoid, w = 1", 0.25 * 1], ["sigmoid, w = 4", 0.25 * 4], ["tanh, w = 1.5", 1.0 * 1.5], ["ReLU, w = 0.6", 1.0 * 0.6]];
for (const [name, factor] of cases) {
  let g = 1;
  const out = [];
  for (let layer = 1; layer <= 20; layer++) {
    g *= factor;
    if (layer === 5 || layer === 10 || layer === 20) out.push(`${layer} layers ${sci(g)}`);
  }
  console.log(`${name}: ` + out.join(", "));
}
''', ts=r'''
function sci(v: number): string {         // 0.000123 -> 1.23e-4, the same in every language
  if (v === 0) return "0";
  let k: number = Math.floor(Math.log10(Math.abs(v)));
  let p = 1;
  for (let i = 0; i < Math.abs(k); i++) p *= 10;
  const m: number = k < 0 ? v * p : v / p;
  let s: string = m.toFixed(2);
  if (s === "10.00") {                    // 9.997 rounds up, so move to the next power
    s = "1.00";
    k += 1;
  }
  return `${s}e${k}`;
}

// the gradient reaching the first layer is a product of one factor per layer:
// factor = (slope of the activation) x (weight)
const cases: [string, number][] = [["sigmoid, w = 1", 0.25 * 1], ["sigmoid, w = 4", 0.25 * 4], ["tanh, w = 1.5", 1.0 * 1.5], ["ReLU, w = 0.6", 1.0 * 0.6]];
for (const [name, factor] of cases) {
  let g = 1;
  const out: string[] = [];
  for (let layer = 1; layer <= 20; layer++) {
    g *= factor;
    if (layer === 5 || layer === 10 || layer === 20) out.push(`${layer} layers ${sci(g)}`);
  }
  console.log(`${name}: ` + out.join(", "));
}
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class Vanishing {
    static String sci(double v) {             // 0.000123 -> 1.23e-4, the same in every language
        if (v == 0) return "0";
        int k = (int) Math.floor(Math.log10(Math.abs(v)));
        double p = 1;
        for (int i = 0; i < Math.abs(k); i++) p *= 10;
        double m = k < 0 ? v * p : v / p;
        String s = String.format("%.2f", m);
        if (s.equals("10.00")) {              // 9.997 rounds up, so move to the next power
            s = "1.00";
            k += 1;
        }
        return s + "e" + k;
    }

    public static void main(String[] args) {
        // the gradient reaching the first layer is a product of one factor per layer:
        // factor = (slope of the activation) x (weight)
        String[] names = {"sigmoid, w = 1", "sigmoid, w = 4", "tanh, w = 1.5", "ReLU, w = 0.6"};
        double[] factors = {0.25 * 1, 0.25 * 4, 1.0 * 1.5, 1.0 * 0.6};
        for (int c = 0; c < names.length; c++) {
            double g = 1;
            List<String> out = new ArrayList<>();
            for (int layer = 1; layer <= 20; layer++) {
                g *= factors[c];
                if (layer == 5 || layer == 10 || layer == 20) out.add(layer + " layers " + sci(g));
            }
            System.out.println(names[c] + ": " + String.join(", ", out));
        }
    }
}
''')

K.code('jensen', py=r'''
import math


def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


xs = [1.0, 2.0, 6.0]
mean = sum(xs) / len(xs)
for name, fun in [("x^2", lambda t: t * t), ("e^x", math.exp), ("ln x", math.log)]:
    f_of_mean = fun(mean)                 # the function at the average
    mean_of_f = sum(fun(t) for t in xs) / len(xs)   # the average of the function
    print(f"{name}: f(mean) = {f(f_of_mean)}, mean of f = {f(mean_of_f)}, gap = {f(mean_of_f - f_of_mean)}")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

const xs = [1, 2, 6];
const mean = xs.reduce((a, b) => a + b, 0) / xs.length;
for (const [name, fun] of [["x^2", t => t * t], ["e^x", Math.exp], ["ln x", Math.log]]) {
  const fOfMean = fun(mean);              // the function at the average
  const meanOfF = xs.reduce((a, t) => a + fun(t), 0) / xs.length;   // the average of the function
  console.log(`${name}: f(mean) = ${f(fOfMean)}, mean of f = ${f(meanOfF)}, gap = ${f(meanOfF - fOfMean)}`);
}
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

const xs: number[] = [1, 2, 6];
const mean: number = xs.reduce((a, b) => a + b, 0) / xs.length;
const funs: [string, (t: number) => number][] = [["x^2", t => t * t], ["e^x", Math.exp], ["ln x", Math.log]];
for (const [name, fun] of funs) {
  const fOfMean: number = fun(mean);      // the function at the average
  const meanOfF: number = xs.reduce((a, t) => a + fun(t), 0) / xs.length;   // the average of the function
  console.log(`${name}: f(mean) = ${f(fOfMean)}, mean of f = ${f(meanOfF)}, gap = ${f(meanOfF - fOfMean)}`);
}
''', java=r'''
public class Jensen {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    static double apply(int k, double t) {
        if (k == 0) return t * t;
        if (k == 1) return Math.exp(t);
        return Math.log(t);
    }

    public static void main(String[] args) {
        double[] xs = {1, 2, 6};
        double mean = (xs[0] + xs[1] + xs[2]) / xs.length;
        String[] names = {"x^2", "e^x", "ln x"};
        for (int k = 0; k < 3; k++) {
            double fOfMean = apply(k, mean);  // the function at the average
            double s = 0;
            for (double t : xs) s += apply(k, t);
            double meanOfF = s / xs.length;   // the average of the function
            System.out.println(names[k] + ": f(mean) = " + f(fOfMean) + ", mean of f = " + f(meanOfF) + ", gap = " + f(meanOfF - fOfMean));
        }
    }
}
''')

K.code('logsumexp', py=r'''
import math


def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


z = [1000.0, 1001.0, 1002.0]              # large scores, as a model can easily produce
try:
    total = sum(math.exp(v) for v in z)
    print(f"naive sum of e^z = {total}")
except OverflowError:
    print("naive sum of e^z: overflow")

m = max(z)                                # the trick: take the biggest score out first
shifted = [math.exp(v - m) for v in z]    # every exponent is now 0 or below
s = sum(shifted)
print(f"log-sum-exp = {f(m + math.log(s))}")
print(f"softmax = [{', '.join(f(e / s) for e in shifted)}]")
print(f"log softmax = [{', '.join(f(v - m - math.log(s)) for v in z)}]")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

const z = [1000, 1001, 1002];             // large scores, as a model can easily produce
const total = z.reduce((a, v) => a + Math.exp(v), 0);
if (!isFinite(total)) console.log("naive sum of e^z: overflow");
else console.log(`naive sum of e^z = ${total}`);

const m = Math.max(...z);                 // the trick: take the biggest score out first
const shifted = z.map(v => Math.exp(v - m));   // every exponent is now 0 or below
const s = shifted.reduce((a, b) => a + b, 0);
console.log(`log-sum-exp = ${f(m + Math.log(s))}`);
console.log(`softmax = [${shifted.map(e => f(e / s)).join(", ")}]`);
console.log(`log softmax = [${z.map(v => f(v - m - Math.log(s))).join(", ")}]`);
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

const z: number[] = [1000, 1001, 1002];   // large scores, as a model can easily produce
const total: number = z.reduce((a, v) => a + Math.exp(v), 0);
if (!isFinite(total)) console.log("naive sum of e^z: overflow");
else console.log(`naive sum of e^z = ${total}`);

const m: number = Math.max(...z);         // the trick: take the biggest score out first
const shifted: number[] = z.map(v => Math.exp(v - m));   // every exponent is now 0 or below
const s: number = shifted.reduce((a, b) => a + b, 0);
console.log(`log-sum-exp = ${f(m + Math.log(s))}`);
console.log(`softmax = [${shifted.map(e => f(e / s)).join(", ")}]`);
console.log(`log softmax = [${z.map(v => f(v - m - Math.log(s))).join(", ")}]`);
''', java=r'''
public class LogSumExp {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    public static void main(String[] args) {
        double[] z = {1000, 1001, 1002};      // large scores, as a model can easily produce
        double total = 0;
        for (double v : z) total += Math.exp(v);
        if (Double.isInfinite(total)) System.out.println("naive sum of e^z: overflow");
        else System.out.println("naive sum of e^z = " + total);

        double m = Math.max(z[0], Math.max(z[1], z[2]));   // the trick: take the biggest score out first
        double[] shifted = new double[3];
        double s = 0;
        for (int i = 0; i < 3; i++) {
            shifted[i] = Math.exp(z[i] - m); // every exponent is now 0 or below
            s += shifted[i];
        }
        System.out.println("log-sum-exp = " + f(m + Math.log(s)));
        System.out.println("softmax = [" + f(shifted[0] / s) + ", " + f(shifted[1] / s) + ", " + f(shifted[2] / s) + "]");
        System.out.println("log softmax = [" + f(z[0] - m - Math.log(s)) + ", " + f(z[1] - m - Math.log(s)) + ", " + f(z[2] - m - Math.log(s)) + "]");
    }
}
''')

K.code('fd_check', py=r'''
import math


def sci(v):                               # 0.000123 -> 1.23e-4, the same in every language
    if v == 0:
        return "0"
    k = math.floor(math.log10(abs(v)))
    p = 1.0
    for _ in range(abs(k)):
        p *= 10
    m = v * p if k < 0 else v / p
    s = f"{m:.2f}"
    if s == "10.00":                      # 9.997 rounds up, so move to the next power
        s = "1.00"
        k += 1
    return f"{s}e{k}"


def cube(x):                              # f(x) = x^3, true slope at x = 1 is exactly 3
    return x * x * x


for k in [1, 2, 4, 6, 8, 10, 12]:
    p = 1
    for _ in range(k):
        p *= 10
    h = 1 / p                             # h = 10^-k
    forward = (cube(1 + h) - cube(1)) / h
    central = (cube(1 + h) - cube(1 - h)) / (2 * h)
    print(f"h = 1e-{k}: forward error {sci(abs(forward - 3))}, central error {sci(abs(central - 3))}")
''', js=r'''
function sci(v) {                         // 0.000123 -> 1.23e-4, the same in every language
  if (v === 0) return "0";
  let k = Math.floor(Math.log10(Math.abs(v)));
  let p = 1;
  for (let i = 0; i < Math.abs(k); i++) p *= 10;
  const m = k < 0 ? v * p : v / p;
  let s = m.toFixed(2);
  if (s === "10.00") {                    // 9.997 rounds up, so move to the next power
    s = "1.00";
    k += 1;
  }
  return `${s}e${k}`;
}

const cube = x => x * x * x;              // f(x) = x^3, true slope at x = 1 is exactly 3

for (const k of [1, 2, 4, 6, 8, 10, 12]) {
  let p = 1;
  for (let i = 0; i < k; i++) p *= 10;
  const h = 1 / p;                        // h = 10^-k
  const forward = (cube(1 + h) - cube(1)) / h;
  const central = (cube(1 + h) - cube(1 - h)) / (2 * h);
  console.log(`h = 1e-${k}: forward error ${sci(Math.abs(forward - 3))}, central error ${sci(Math.abs(central - 3))}`);
}
''', ts=r'''
function sci(v: number): string {         // 0.000123 -> 1.23e-4, the same in every language
  if (v === 0) return "0";
  let k: number = Math.floor(Math.log10(Math.abs(v)));
  let p = 1;
  for (let i = 0; i < Math.abs(k); i++) p *= 10;
  const m: number = k < 0 ? v * p : v / p;
  let s: string = m.toFixed(2);
  if (s === "10.00") {                    // 9.997 rounds up, so move to the next power
    s = "1.00";
    k += 1;
  }
  return `${s}e${k}`;
}

const cube = (x: number): number => x * x * x;   // f(x) = x^3, true slope at x = 1 is exactly 3

for (const k of [1, 2, 4, 6, 8, 10, 12]) {
  let p = 1;
  for (let i = 0; i < k; i++) p *= 10;
  const h: number = 1 / p;                // h = 10^-k
  const forward: number = (cube(1 + h) - cube(1)) / h;
  const central: number = (cube(1 + h) - cube(1 - h)) / (2 * h);
  console.log(`h = 1e-${k}: forward error ${sci(Math.abs(forward - 3))}, central error ${sci(Math.abs(central - 3))}`);
}
''', java=r'''
public class FdCheck {
    static String sci(double v) {             // 0.000123 -> 1.23e-4, the same in every language
        if (v == 0) return "0";
        int k = (int) Math.floor(Math.log10(Math.abs(v)));
        double p = 1;
        for (int i = 0; i < Math.abs(k); i++) p *= 10;
        double m = k < 0 ? v * p : v / p;
        String s = String.format("%.2f", m);
        if (s.equals("10.00")) {              // 9.997 rounds up, so move to the next power
            s = "1.00";
            k += 1;
        }
        return s + "e" + k;
    }

    static double cube(double x) {            // f(x) = x^3, true slope at x = 1 is exactly 3
        return x * x * x;
    }

    public static void main(String[] args) {
        for (int k : new int[]{1, 2, 4, 6, 8, 10, 12}) {
            double p = 1;
            for (int i = 0; i < k; i++) p *= 10;
            double h = 1 / p;                 // h = 10^-k
            double forward = (cube(1 + h) - cube(1)) / h;
            double central = (cube(1 + h) - cube(1 - h)) / (2 * h);
            System.out.println("h = 1e-" + k + ": forward error " + sci(Math.abs(forward - 3)) + ", central error " + sci(Math.abs(central - 3)));
        }
    }
}
''')

# ---- practice programs
K.code('p_taylor_e', py=r'''
import math

total, term, n = 1.0, 1.0, 0              # start with the first term 1/0! = 1
while abs(math.e - total) >= 1e-6:
    n += 1
    term /= n                             # 1/n! from 1/(n-1)!
    total += term
print(f"terms used: {n + 1} (1/0! up to 1/{n}!)")
print(f"sum = {total:.7f}")
print(f"e   = {math.e:.7f}")
''', js=r'''
let total = 1, term = 1, n = 0;           // start with the first term 1/0! = 1
while (Math.abs(Math.E - total) >= 1e-6) {
  n += 1;
  term /= n;                              // 1/n! from 1/(n-1)!
  total += term;
}
console.log(`terms used: ${n + 1} (1/0! up to 1/${n}!)`);
console.log(`sum = ${total.toFixed(7)}`);
console.log(`e   = ${Math.E.toFixed(7)}`);
''', ts=r'''
let total: number = 1, term: number = 1, n: number = 0;   // start with the first term 1/0! = 1
while (Math.abs(Math.E - total) >= 1e-6) {
  n += 1;
  term /= n;                              // 1/n! from 1/(n-1)!
  total += term;
}
console.log(`terms used: ${n + 1} (1/0! up to 1/${n}!)`);
console.log(`sum = ${total.toFixed(7)}`);
console.log(`e   = ${Math.E.toFixed(7)}`);
''', java=r'''
public class PracticeTaylorE {
    public static void main(String[] args) {
        double total = 1, term = 1;           // start with the first term 1/0! = 1
        int n = 0;
        while (Math.abs(Math.E - total) >= 1e-6) {
            n += 1;
            term /= n;                        // 1/n! from 1/(n-1)!
            total += term;
        }
        System.out.println("terms used: " + (n + 1) + " (1/0! up to 1/" + n + "!)");
        System.out.println("sum = " + String.format("%.7f", total));
        System.out.println("e   = " + String.format("%.7f", Math.E));
    }
}
''')

K.code('p_cuberoot', py=r'''
def f(v):
    return f"{v:.10f}"


x = 2.0
nxt = x
for k in range(1, 20):
    nxt = x - (x * x * x - 10) / (3 * x * x)   # Newton step for g(x) = x^3 - 10
    print(f"step {k}: x = {f(nxt)}")
    if abs(nxt - x) < 1e-10:
        break
    x = nxt
print(f"check: x^3 = {f(nxt * nxt * nxt)}")
''', js=r'''
const f = v => v.toFixed(10);

let x = 2;
let nxt = x;
for (let k = 1; k < 20; k++) {
  nxt = x - (x * x * x - 10) / (3 * x * x);   // Newton step for g(x) = x^3 - 10
  console.log(`step ${k}: x = ${f(nxt)}`);
  if (Math.abs(nxt - x) < 1e-10) break;
  x = nxt;
}
console.log(`check: x^3 = ${f(nxt * nxt * nxt)}`);
''', ts=r'''
const f = (v: number): string => v.toFixed(10);

let x: number = 2;
let nxt: number = x;
for (let k = 1; k < 20; k++) {
  nxt = x - (x * x * x - 10) / (3 * x * x);   // Newton step for g(x) = x^3 - 10
  console.log(`step ${k}: x = ${f(nxt)}`);
  if (Math.abs(nxt - x) < 1e-10) break;
  x = nxt;
}
console.log(`check: x^3 = ${f(nxt * nxt * nxt)}`);
''', java=r'''
public class PracticeCubeRoot {
    static String f(double v) {
        return String.format("%.10f", v);
    }

    public static void main(String[] args) {
        double x = 2;
        double nxt = x;
        for (int k = 1; k < 20; k++) {
            nxt = x - (x * x * x - 10) / (3 * x * x);   // Newton step for g(x) = x^3 - 10
            System.out.println("step " + k + ": x = " + f(nxt));
            if (Math.abs(nxt - x) < 1e-10) break;
            x = nxt;
        }
        System.out.println("check: x^3 = " + f(nxt * nxt * nxt));
    }
}
''')

K.code('p_grad_check', py=r'''
import math


def f(v):
    return f"{v:.6f}"


x = [1.0, 2.0]
y = 1.0                                   # the label, +1 or -1
w = [0.3, 0.2]


def loss(w):                              # logistic loss ln(1 + e^(-y w.x))
    z = w[0] * x[0] + w[1] * x[1]
    return math.log(1 + math.exp(-y * z))


z = w[0] * x[0] + w[1] * x[1]
s = 1 / (1 + math.exp(y * z))             # sigmoid(-y z)
analytic = [-y * s * x[0], -y * s * x[1]]
h = 1e-6
numeric = []
for i in range(2):
    up = w[:]
    dn = w[:]
    up[i] += h
    dn[i] -= h
    numeric.append((loss(up) - loss(dn)) / (2 * h))
rel = max(abs(a - b) / max(abs(a), abs(b)) for a, b in zip(analytic, numeric))
print(f"analytic gradient = [{f(analytic[0])}, {f(analytic[1])}]")
print(f"numeric gradient  = [{f(numeric[0])}, {f(numeric[1])}]")
print("gradient check: " + ("PASS" if rel < 1e-6 else "FAIL"))
''', js=r'''
const f = v => v.toFixed(6);

const x = [1, 2];
const y = 1;                              // the label, +1 or -1
const w = [0.3, 0.2];
const loss = w => Math.log(1 + Math.exp(-y * (w[0] * x[0] + w[1] * x[1])));   // logistic loss ln(1 + e^(-y w.x))

const z = w[0] * x[0] + w[1] * x[1];
const s = 1 / (1 + Math.exp(y * z));      // sigmoid(-y z)
const analytic = [-y * s * x[0], -y * s * x[1]];
const h = 1e-6;
const numeric = [0, 1].map(i => {
  const up = w.slice(), dn = w.slice();
  up[i] += h;
  dn[i] -= h;
  return (loss(up) - loss(dn)) / (2 * h);
});
const rel = Math.max(...analytic.map((a, i) => Math.abs(a - numeric[i]) / Math.max(Math.abs(a), Math.abs(numeric[i]))));
console.log(`analytic gradient = [${f(analytic[0])}, ${f(analytic[1])}]`);
console.log(`numeric gradient  = [${f(numeric[0])}, ${f(numeric[1])}]`);
console.log("gradient check: " + (rel < 1e-6 ? "PASS" : "FAIL"));
''', ts=r'''
const f = (v: number): string => v.toFixed(6);

const x: number[] = [1, 2];
const y: number = 1;                      // the label, +1 or -1
const w: number[] = [0.3, 0.2];
const loss = (w: number[]): number => Math.log(1 + Math.exp(-y * (w[0] * x[0] + w[1] * x[1])));   // logistic loss ln(1 + e^(-y w.x))

const z: number = w[0] * x[0] + w[1] * x[1];
const s: number = 1 / (1 + Math.exp(y * z));   // sigmoid(-y z)
const analytic: number[] = [-y * s * x[0], -y * s * x[1]];
const h: number = 1e-6;
const numeric: number[] = [0, 1].map(i => {
  const up = w.slice(), dn = w.slice();
  up[i] += h;
  dn[i] -= h;
  return (loss(up) - loss(dn)) / (2 * h);
});
const rel: number = Math.max(...analytic.map((a, i) => Math.abs(a - numeric[i]) / Math.max(Math.abs(a), Math.abs(numeric[i]))));
console.log(`analytic gradient = [${f(analytic[0])}, ${f(analytic[1])}]`);
console.log(`numeric gradient  = [${f(numeric[0])}, ${f(numeric[1])}]`);
console.log("gradient check: " + (rel < 1e-6 ? "PASS" : "FAIL"));
''', java=r'''
public class PracticeGradCheck {
    static double[] x = {1, 2};
    static double y = 1;                      // the label, +1 or -1

    static String f(double v) {
        return String.format("%.6f", v);
    }

    static double loss(double[] w) {          // logistic loss ln(1 + e^(-y w.x))
        double z = w[0] * x[0] + w[1] * x[1];
        return Math.log(1 + Math.exp(-y * z));
    }

    public static void main(String[] args) {
        double[] w = {0.3, 0.2};
        double z = w[0] * x[0] + w[1] * x[1];
        double s = 1 / (1 + Math.exp(y * z)); // sigmoid(-y z)
        double[] analytic = {-y * s * x[0], -y * s * x[1]};
        double h = 1e-6;
        double[] numeric = new double[2];
        for (int i = 0; i < 2; i++) {
            double[] up = w.clone(), dn = w.clone();
            up[i] += h;
            dn[i] -= h;
            numeric[i] = (loss(up) - loss(dn)) / (2 * h);
        }
        double rel = 0;
        for (int i = 0; i < 2; i++) rel = Math.max(rel, Math.abs(analytic[i] - numeric[i]) / Math.max(Math.abs(analytic[i]), Math.abs(numeric[i])));
        System.out.println("analytic gradient = [" + f(analytic[0]) + ", " + f(analytic[1]) + "]");
        System.out.println("numeric gradient  = [" + f(numeric[0]) + ", " + f(numeric[1]) + "]");
        System.out.println("gradient check: " + (rel < 1e-6 ? "PASS" : "FAIL"));
    }
}
''')

K.code('p_newton_2d', py=r'''
def f(v):
    return f"{0.0 if abs(v) < 5e-7 else v:.6f}"


def rosen(x, y):                          # the Rosenbrock "banana" function, lowest point at (1, 1)
    return (1 - x) ** 2 + 100 * (y - x * x) ** 2


x, y = -1.2, 1.0
print(f"start: x = {f(x)}, y = {f(y)}, f = {f(rosen(x, y))}")
for k in range(1, 8):
    gx = -2 * (1 - x) - 400 * x * (y - x * x)   # gradient
    gy = 200 * (y - x * x)
    hxx = 2 - 400 * (y - x * x) + 800 * x * x   # Hessian
    hxy = -400 * x
    hyy = 200.0
    det = hxx * hyy - hxy * hxy
    dx = (-gx * hyy + hxy * gy) / det       # solve H d = -g with Cramer's rule
    dy = (-hxx * gy + gx * hxy) / det
    x, y = x + dx, y + dy
    print(f"step {k}: x = {f(x)}, y = {f(y)}, f = {f(rosen(x, y))}")
''', js=r'''
const f = v => (Math.abs(v) < 5e-7 ? 0 : v).toFixed(6);
const rosen = (x, y) => (1 - x) ** 2 + 100 * (y - x * x) ** 2;   // the Rosenbrock "banana" function, lowest point at (1, 1)

let x = -1.2, y = 1;
console.log(`start: x = ${f(x)}, y = ${f(y)}, f = ${f(rosen(x, y))}`);
for (let k = 1; k < 8; k++) {
  const gx = -2 * (1 - x) - 400 * x * (y - x * x);   // gradient
  const gy = 200 * (y - x * x);
  const hxx = 2 - 400 * (y - x * x) + 800 * x * x;   // Hessian
  const hxy = -400 * x;
  const hyy = 200;
  const det = hxx * hyy - hxy * hxy;
  const dx = (-gx * hyy + hxy * gy) / det;           // solve H d = -g with Cramer's rule
  const dy = (-hxx * gy + gx * hxy) / det;
  x += dx;
  y += dy;
  console.log(`step ${k}: x = ${f(x)}, y = ${f(y)}, f = ${f(rosen(x, y))}`);
}
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-7 ? 0 : v).toFixed(6);
const rosen = (x: number, y: number): number => (1 - x) ** 2 + 100 * (y - x * x) ** 2;   // the Rosenbrock "banana" function, lowest point at (1, 1)

let x: number = -1.2, y: number = 1;
console.log(`start: x = ${f(x)}, y = ${f(y)}, f = ${f(rosen(x, y))}`);
for (let k = 1; k < 8; k++) {
  const gx: number = -2 * (1 - x) - 400 * x * (y - x * x);   // gradient
  const gy: number = 200 * (y - x * x);
  const hxx: number = 2 - 400 * (y - x * x) + 800 * x * x;   // Hessian
  const hxy: number = -400 * x;
  const hyy: number = 200;
  const det: number = hxx * hyy - hxy * hxy;
  const dx: number = (-gx * hyy + hxy * gy) / det;           // solve H d = -g with Cramer's rule
  const dy: number = (-hxx * gy + gx * hxy) / det;
  x += dx;
  y += dy;
  console.log(`step ${k}: x = ${f(x)}, y = ${f(y)}, f = ${f(rosen(x, y))}`);
}
''', java=r'''
public class PracticeNewton2D {
    static String f(double v) {
        return String.format("%.6f", Math.abs(v) < 5e-7 ? 0.0 : v);
    }

    static double rosen(double x, double y) { // the Rosenbrock "banana" function, lowest point at (1, 1)
        return (1 - x) * (1 - x) + 100 * (y - x * x) * (y - x * x);
    }

    public static void main(String[] args) {
        double x = -1.2, y = 1;
        System.out.println("start: x = " + f(x) + ", y = " + f(y) + ", f = " + f(rosen(x, y)));
        for (int k = 1; k < 8; k++) {
            double gx = -2 * (1 - x) - 400 * x * (y - x * x);   // gradient
            double gy = 200 * (y - x * x);
            double hxx = 2 - 400 * (y - x * x) + 800 * x * x;   // Hessian
            double hxy = -400 * x;
            double hyy = 200;
            double det = hxx * hyy - hxy * hxy;
            double dx = (-gx * hyy + hxy * gy) / det;           // solve H d = -g with Cramer's rule
            double dy = (-hxx * gy + gx * hxy) / det;
            x += dx;
            y += dy;
            System.out.println("step " + k + ": x = " + f(x) + ", y = " + f(y) + ", f = " + f(rosen(x, y)));
        }
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('taylor', '🪜', 'Taylor series: curves as polynomials', f'''
<p>Computers can only add and multiply. To find e<sup>0.5</sup> or sin 0.3, a calculator uses a polynomial that copies the function very closely near one point. That copy is a <b>Taylor polynomial</b>. The recipe is simple: match the value at the point, then the slope, then the bend, then the rate of change of the bend, and so on. Each matched derivative adds one more term.</p>
{fx('Taylor polynomial around 0 (also called a Maclaurin polynomial)', 'f(x) ≈ f(0) + f′(0) x + ' + frac('f″(0)', '2!') + ' x² + ' + frac('f‴(0)', '3!') + ' x³ + …', 'n! means 1 × 2 × … × n. Around another point a, replace x by (x − a) and the derivatives at 0 by the derivatives at a.')}
{table(['Function', 'Series around 0', 'Works for'], [
        ['eˣ', '1 + x + x²/2! + x³/3! + x⁴/4! + …', 'every x'],
        ['sin x', 'x − x³/3! + x⁵/5! − x⁷/7! + …', 'every x'],
        ['cos x', '1 − x²/2! + x⁴/4! − x⁶/6! + …', 'every x'],
        ['ln(1 + x)', 'x − x²/2 + x³/3 − x⁴/4 + …', '−1 &lt; x ≤ 1 only'],
        ['1 ÷ (1 − x)', '1 + x + x² + x³ + …', '−1 &lt; x &lt; 1 only'],
    ])}
{viz('taylorviz')}
{worked('e^0.5 with four terms', [
        'Order 0: <span class="eq">1</span>',
        'Add x: <span class="eq">1 + 0.5 = 1.5</span>',
        'Add x²/2: <span class="eq">1.5 + 0.125 = 1.625</span>',
        'Add x³/6: <span class="eq">1.625 + 0.0208 = 1.6458</span>',
        'The true value is <span class="eq">1.6487</span>. Four terms already give two correct decimals, and each extra term roughly divides the error by 10 here.'])}
{code('taylor_exp', 'Taylor polynomials of eˣ, order by order, with the error')}
{deep('why the terms shrink, and when they do not', f"""
<p>The n-th term is f⁽ⁿ⁾(0) xⁿ ÷ n!. For eˣ every derivative is 1, so the terms are xⁿ ÷ n!. Factorials grow faster than any power. For x = 2 the terms are 1, 2, 2, 1.33, 0.67, 0.27, 0.09, … They climb a little at first, then fall fast. That is why the series for eˣ, sin x and cos x works for every x, it just needs more terms for larger x.</p>
<p>For ln(1 + x) the terms are xⁿ ÷ n with no factorial to help. When |x| &gt; 1 the powers win and the terms grow, so adding more of them makes the answer worse. The interval where a series works is called its <b>radius of convergence</b>. Try x = 1.5 with ln(1 + x) in the animation and raise n to see the polynomial run away.</p>
<p>The leftover error after the order n polynomial is about the size of the first term you left out. This is <b>Taylor’s remainder</b>: error = f⁽ⁿ⁺¹⁾(c) xⁿ⁺¹ ÷ (n + 1)! for some c between 0 and x. It explains why small x needs few terms.</p>""")}
{ml('Two Taylor orders run through all of machine learning. Order 1 (the tangent line, Chapter 7) is the reason gradient descent works: f(w + Δ) ≈ f(w) + ∇f · Δ, so stepping against the gradient lowers f. Order 2 adds the Hessian, ½ Δᵀ H Δ, and leads to Newton’s method in the next lesson. The GELU activation in transformers is often computed with a tanh based approximation for speed.')}
{life('Your phone’s calculator does not store a table of every sine. It shrinks the angle into a small range, then adds up a handful of polynomial terms, which is fast and accurate to the last digit shown.')}
''', kw=['taylor series', 'maclaurin', 'polynomial approximation', 'factorial', 'radius of convergence', 'remainder', 'linear approximation', 'quadratic approximation']),

    part('newton', '🎯', 'Newton’s method for roots and minimums', f'''
<p>To solve f(x) = 0, Newton’s method draws the tangent line at your current guess and jumps to the point where that line crosses zero. The tangent line is the order 1 Taylor polynomial, so each step solves a simpler, straight line version of the problem.</p>
{fxs(fx('Newton step for a root', 'xₙ₊₁ = xₙ − ' + frac('f(xₙ)', 'f′(xₙ)'), 'Divide the height by the slope to find how far to slide along the tangent.'),
         fx('Newton step for a minimum', 'xₙ₊₁ = xₙ − ' + frac('f′(xₙ)', 'f″(xₙ)'), 'A minimum is a root of the slope f′, so use the same rule on f′. In many dimensions: x ← x − H⁻¹∇f.'))}
{viz('newtonviz')}
{worked('√2 as the root of x² − 2, starting from x₀ = 1', [
        '<span class="eq">x₁ = 1 − (1 − 2) ÷ 2 = 1.5</span>',
        '<span class="eq">x₂ = 1.5 − (2.25 − 2) ÷ 3 = 1.416667</span>',
        '<span class="eq">x₃ = 1.416667 − 0.006944 ÷ 2.833333 = 1.414216</span>',
        'True √2 = <span class="eq">1.414214</span>. The number of correct digits roughly doubles each step: 1, 3, 6, then 12.'])}
{code('newton', 'Newton for √2 and for the lowest point of eˣ − 2x')}
<p>That doubling of correct digits is called <b>quadratic convergence</b>. Gradient descent only gains a fixed number of digits per step, so near the answer Newton is much faster. It has costs, though.</p>
<ul>
<li>It needs the second derivative, or in many dimensions the whole Hessian matrix: n² numbers for n weights. With a million weights that is a trillion numbers.</li>
<li>It can fail. A flat tangent (f′ = 0) sends the next guess to infinity, and some starting points make it jump back and forth forever. The third example in the animation does exactly that.</li>
<li>For minimising, it is attracted to any flat point, including maximums and saddle points, unless the Hessian is positive definite (Chapter 13).</li>
</ul>
{ml('Full Newton is used for small and medium models: logistic regression in statistics packages is fitted by a Newton method called iteratively reweighted least squares. For large models, quasi Newton methods such as L-BFGS build a cheap estimate of the Hessian from recent gradients. Adam’s division by the square root of recent squared gradients is a very rough, diagonal stand in for the curvature.')}
{trick('Newton in one sentence: replace the curve by its tangent (or the bowl by its quadratic), solve that easy problem, repeat.')}
''', kw=['newton method', 'newton raphson', 'root finding', 'quadratic convergence', 'hessian', 'second order optimisation', 'l-bfgs', 'quasi newton']),

    part('matcalc', '🧮', 'Matrix calculus: gradients without index pain', f'''
<p>When a function takes a whole vector or matrix as input, we want its gradient as a vector or matrix of the same shape. Working through every index by hand is slow and error prone, so people learn a short list of rules, just like the derivative table for single numbers.</p>
{table(['Function of x (a vector)', 'Gradient ∇ₓ', 'Single number version'], [
        ['aᵀx', 'a', '(ax)′ = a'],
        ['xᵀx = ‖x‖²', '2x', '(x²)′ = 2x'],
        ['xᵀAx', '(A + Aᵀ)x, which is 2Ax when A is symmetric', '(ax²)′ = 2ax'],
        ['½(x − m)ᵀA(x − m), A symmetric', 'A(x − m)', '(½a(x − m)²)′ = a(x − m)'],
        ['‖Xw − y‖² (as a function of w)', '2Xᵀ(Xw − y)', '((xw − y)²)′ = 2x(xw − y)'],
        ['Wx (vector output)', 'Jacobian is W', '(wx)′ = w'],
    ])}
<p>The gradient of a scalar function lives in the same space as its input and points uphill. The Hessian, the matrix of second derivatives, tells how that gradient changes. For the bowl ½(x − m)ᵀA(x − m) the Hessian is simply A.</p>
{viz('gradbowl')}
{worked('Least squares in one line', [
        'Loss: <span class="eq">L(w) = ‖Xw − y‖²</span>',
        'Gradient by the table: <span class="eq">∇L = 2Xᵀ(Xw − y)</span>',
        'Set it to zero: <span class="eq">XᵀXw = Xᵀy</span>. These are the normal equations of Chapter 13, found here without any picture.',
        'Hessian: <span class="eq">2XᵀX</span>, which is positive semi definite, so this flat point is a minimum.'])}
{code('mat_grad', 'Check two matrix calculus rules against numerical gradients')}
{deep('a safe way to derive any rule', f"""
<p>When you meet a new expression, write the change in output for a tiny change dx and keep only the first order part. For f(x) = xᵀAx: f(x + dx) = xᵀAx + dxᵀAx + xᵀA dx + (tiny). Both middle terms are numbers, and a number equals its own transpose, so xᵀA dx = dxᵀAᵀx. The change is dxᵀ(A + Aᵀ)x, and whatever multiplies dxᵀ is the gradient.</p>
<p>Then always check the shapes. If x has n entries, the gradient must have n entries too. If the shapes do not match, a transpose is missing. Finally check one example numerically, as the program above does. Libraries do this in their own tests.</p>""")}
{ml('Every layer of a neural network is a matrix product followed by an activation. The rules ∂(Wx)/∂x = W and ∂L/∂W = (∂L/∂z) xᵀ are exactly what backpropagation computes for a dense layer. Getting the transposes right is the whole difficulty, and the shape check catches most mistakes.')}
''', kw=['matrix calculus', 'gradient of quadratic form', 'jacobian', 'hessian', 'normal equations', 'shape check', 'vector derivative']),

    part('autodiff', '🤖', 'Automatic differentiation: forward and reverse mode', f'''
<p>There are three ways a computer can find derivatives. <b>Numerical</b> differences, (f(x + h) − f(x)) ÷ h, are easy but slow and slightly inaccurate. <b>Symbolic</b> differentiation, like a computer algebra system, produces exact formulas that can grow huge. <b>Automatic differentiation</b> (autodiff) is the third way. It applies the chain rule to each small operation as the program runs, and it is exact up to rounding.</p>
<p>Any program is a chain of tiny steps: multiply, add, sin, exp. Write each step down as a node in a graph. Each node knows its own local derivative. Autodiff combines those local pieces with the chain rule, and it can do so in two directions.</p>
{table(['', 'Forward mode', 'Reverse mode'], [
        ['direction', 'inputs to output, together with the values', 'values first, then output back to inputs'],
        ['carries', 'the derivative of every node with respect to one input', 'the derivative of the output with respect to every node'],
        ['cost', 'one pass per input', 'one backward pass per output'],
        ['best when', 'few inputs, many outputs', 'many inputs, one output (a loss)'],
        ['also called', 'dual numbers, Jacobian vector product', 'backpropagation, vector Jacobian product'],
    ])}
{viz('adtape')}
{worked('f(x, y) = x·y + sin x at x = 2, y = 3, in reverse mode', [
        'Forward: <span class="eq">v₁ = x·y = 6</span>, <span class="eq">v₂ = sin 2 = 0.9093</span>, <span class="eq">f = 6.9093</span>',
        'Start the walk back with <span class="eq">∂f/∂f = 1</span>. Since f = v₁ + v₂, <span class="eq">∂f/∂v₁ = 1</span> and <span class="eq">∂f/∂v₂ = 1</span>',
        'v₁ = x·y gives <span class="eq">∂f/∂y = 1 × x = 2</span> and a first piece <span class="eq">∂f/∂x ← 1 × y = 3</span>',
        'v₂ = sin x adds <span class="eq">1 × cos 2 = −0.4161</span> to x, because x was used twice',
        'So <span class="eq">∂f/∂x = 2.5839</span> and <span class="eq">∂f/∂y = 2</span>, both from one backward pass.'])}
{code('dual_numbers', 'Forward mode with dual numbers (value, slope)')}
{code('reverse_mode', 'Reverse mode on a written down tape')}
{deep('why deep learning uses reverse mode', f"""
<p>A network has millions of weights (inputs to the loss) and one loss (the output). Forward mode would need one pass per weight, millions of passes. Reverse mode needs one forward pass to compute values and one backward pass, and the backward pass costs only a small multiple of the forward pass. This fact, sometimes called the cheap gradient principle, is why training large networks is possible at all.</p>
<p>The price of reverse mode is memory. The backward pass needs the values from the forward pass, such as x and y for the node x·y, so the whole tape must be kept until the backward pass is done. That is why training uses far more memory than prediction, and why tricks such as gradient checkpointing recompute some values instead of storing them.</p>
<p>When a value is used in two places, its derivative is the <b>sum</b> of the two contributions. Forgetting this is a classic bug in hand written backprop. In PyTorch, calling loss.backward() runs reverse mode over the graph recorded during the forward pass.</p>""")}
{ml('PyTorch, TensorFlow and JAX are autodiff engines with a GPU attached. JAX offers both modes directly: jax.grad uses reverse mode, jax.jvp uses forward mode, and the two can be combined to get Hessian vector products cheaply.')}
''', kw=['automatic differentiation', 'autodiff', 'forward mode', 'reverse mode', 'dual numbers', 'computational graph', 'backpropagation', 'tape', 'jacobian vector product']),

    part('vanish', '📉', 'Vanishing and exploding gradients', f'''
<p>Backpropagation through a deep network multiplies many factors together, one per layer. Each factor is roughly (slope of the activation) × (weight). If those factors are a little below 1, their product shrinks towards 0 and the early layers stop learning. If they are a little above 1, the product blows up and training crashes with huge updates or NaN values.</p>
{fx('Gradient reaching layer 1 of an L layer chain', '∂L/∂h₁ = ∂L/∂h_L × ∏ (σ′(zₖ) wₖ)', 'One factor per layer. 0.9²⁰ ≈ 0.12, 0.5²⁰ ≈ 0.000001, 1.5²⁰ ≈ 3325.')}
{viz('gradflow')}
{worked('Why sigmoid networks struggled', [
        'The sigmoid slope is at most <span class="eq">σ′(0) = 0.25</span>',
        'With weights near 1, each layer multiplies the gradient by at most <span class="eq">0.25</span>',
        'After 10 layers: <span class="eq">0.25¹⁰ ≈ 0.00000095</span>',
        'The first layer receives about one millionth of the signal of the last, so it barely changes.'])}
{code('vanishing', 'The product of 20 per layer factors for four settings')}
{table(['Fix', 'What it does'], [
        ['ReLU and its relatives', 'slope exactly 1 for positive inputs, so the activation does not shrink the signal'],
        ['careful initialisation', 'Xavier (variance 1 ÷ n_in) or He (variance 2 ÷ n_in) keeps the size of signals about the same from layer to layer'],
        ['batch or layer normalisation', 'rescales the values inside the network so they stay in a healthy range'],
        ['residual connections', 'h + F(h) adds a "+1" path, so the gradient can skip layers unchanged'],
        ['gradient clipping', 'caps the gradient length to stop explosions, common in recurrent networks'],
        ['LSTM and GRU gates', 'let a recurrent network keep a memory path whose factor stays near 1'],
    ])}
{ml('The residual connection of ResNets and transformers is the most important of these. Because the derivative of h + F(h) is 1 + F′(h), there is always a path with factor 1, and networks with hundreds of layers train well.')}
{trick('Many numbers multiplied together: slightly below 1 vanishes, slightly above 1 explodes. Keep each factor near 1.')}
''', kw=['vanishing gradient', 'exploding gradient', 'sigmoid derivative', 'relu', 'xavier initialisation', 'he initialisation', 'residual connection', 'gradient clipping', 'batch normalisation']),

    part('convex', '🥣', 'Convexity and Jensen’s inequality', f'''
<p>A function is <b>convex</b> when the straight line (chord) between any two points on its graph never goes below the graph. Think of the shape of a bowl. Convex functions are the friendly ones in optimisation: every local minimum is the global minimum, so gradient descent cannot get trapped.</p>
{fxs(fx('Definition', 'f(t a + (1 − t) b) ≤ t f(a) + (1 − t) f(b) for all t in [0, 1]', 'The curve at the mixed point is at most the mix of the curve values.'),
         fx('Quick tests', 'f″(x) ≥ 0, or in many dimensions a positive semi definite Hessian', 'x², eˣ, |x| and −ln x are convex. ln x and √x are concave (the chord lies below).'))}
{viz('jensenviz')}
<p><b>Jensen’s inequality</b> is the same idea with many points and any weights, in particular the probabilities of a random variable.</p>
{fx('Jensen’s inequality', 'f(E[X]) ≤ E[f(X)] for convex f', 'The function of the average is at most the average of the function. For concave f the sign flips.')}
{worked('Data 1, 2, 6 with f(x) = x²', [
        'Average: <span class="eq">E[X] = 3</span>, so <span class="eq">f(E[X]) = 9</span>',
        'Average of squares: <span class="eq">(1 + 4 + 36) ÷ 3 = 13.667</span>',
        '<span class="eq">9 ≤ 13.667</span> ✓. The gap 4.667 is exactly the variance, so Jensen proves that a variance is never negative.'])}
{code('jensen', 'Jensen’s gap for x², eˣ and ln x')}
{deep('what Jensen proves in machine learning', f"""
<p><b>KL divergence is never negative.</b> −ln is convex, so E[−ln(q ÷ p)] ≥ −ln E[q ÷ p] = −ln 1 = 0, with the expectation under p. This is why cross entropy is always at least the entropy (Chapter 12).</p>
<p><b>The ELBO.</b> Variational autoencoders want ln p(x), which is hard. Since ln is concave, ln E[ratio] ≥ E[ln ratio], which gives a lower bound that can be computed and maximised instead.</p>
<p><b>Which losses are convex.</b> Squared error for linear regression and log loss for logistic regression are convex in the weights, so their training always reaches the best answer. A neural network with a hidden layer is not convex in its weights: swapping two hidden units gives the same function, so there are many equal minimums. In practice, large networks still train well, and their many minimums tend to be about equally good.</p>""")}
{life('Averaging speeds is a Jensen trap. Drive 60 km at 30 km/h and 60 km at 90 km/h. The average of the speeds is 60 km/h, but the trip takes 2 + 0.67 = 2.67 hours for 120 km, an average of 45 km/h. Time is a convex function of speed, so the true average is lower.')}
''', kw=['convex function', 'concave', 'chord', 'jensen inequality', 'global minimum', 'kl divergence non negative', 'elbo', 'second derivative test']),

    part('numerics', '🧯', 'Numerical stability: when maths meets floating point', f'''
<p>Floating point numbers (Chapter 1) have about 16 significant digits in float64 and about 7 in float32. Formulas that are perfect on paper can lose all their accuracy on a computer. Three situations come up again and again in machine learning.</p>
<ol>
<li><b>Overflow:</b> e¹⁰⁰⁰ is bigger than the largest float64 (about 1.8 × 10³⁰⁸), so it becomes infinity, and infinity ÷ infinity is NaN.</li>
<li><b>Catastrophic cancellation:</b> subtracting two nearly equal numbers wipes out the leading digits and leaves mostly rounding noise.</li>
<li><b>Underflow:</b> multiplying many small probabilities gives a number too small to store, which becomes exactly 0. Working with logs and adding them avoids it.</li>
</ol>
{fx('The log-sum-exp trick', 'ln Σ e<sup>zᵢ</sup> = m + ln Σ e<sup>zᵢ − m</sup> with m = max zᵢ', 'Every exponent is now 0 or below, so nothing overflows, and the biggest term is exactly e⁰ = 1, so nothing underflows to a sum of 0.')}
{code('logsumexp', 'Softmax of very large scores, naive and stable')}
<p>Finite differences show both errors at once. The step h in (f(x + h) − f(x)) ÷ h must be small to follow the curve, which is the <b>truncation error</b>, about h. But a tiny h makes f(x + h) − f(x) a cancellation, which is the <b>rounding error</b>, about ε ÷ h, where ε ≈ 2.2 × 10⁻¹⁶. The total is smallest in between.</p>
{viz('fdiffviz')}
{fxs(fx('Forward difference', 'error ≈ h + ε ÷ h, best h ≈ √ε ≈ 10⁻⁸', 'Gives about 8 correct digits at best.'),
         fx('Central difference', '(f(x + h) − f(x − h)) ÷ 2h, error ≈ h² + ε ÷ h, best h ≈ 10⁻⁵', 'Gives about 10 to 11 correct digits.'))}
{code('fd_check', 'Forward and central difference errors for x³ at x = 1')}
{ml('Every deep learning library computes softmax and cross entropy together with the log-sum-exp trick, which is why you should pass raw logits to CrossEntropyLoss rather than probabilities. Gradient checking with central differences is the standard way to test a hand written backward pass. Mixed precision training in float16 multiplies the loss by a large "loss scale" so that small gradients do not underflow to zero.')}
{trick('Never compute e^big directly. Subtract the max first. Never multiply many probabilities. Add their logs.')}
''', kw=['numerical stability', 'overflow', 'underflow', 'catastrophic cancellation', 'log sum exp', 'stable softmax', 'finite difference', 'gradient checking', 'machine epsilon', 'mixed precision']),
]

INFO = {
    'title': 'Approximate, differentiate, stay stable',
    'panels': [
        {'s': [['e', '🪜'], ['t', 'f ≈ Σ f⁽ⁿ⁾xⁿ/n!', {'b': 1}]], 'h': 'Taylor', 't': 'Curves as polynomials.', 'more': 'Order 1 gives gradient descent.'},
        {'s': [['e', '🎯'], ['t', 'x − f/f′', {'b': 1}]], 'h': 'Newton', 't': 'Follow the tangent.', 'more': 'Digits double each step.'},
        {'s': [['e', '🤖'], ['t', 'one pass back', {'b': 1}]], 'h': 'Reverse mode', 't': 'All gradients at once.', 'more': 'This is backprop.'},
        {'s': [['e', '🧯'], ['t', 'subtract max', {'b': 1}]], 'h': 'Stability', 't': 'Log-sum-exp.', 'more': 'No overflow.'},
    ],
    'remember': 'A Taylor polynomial copies a function near a point using its derivatives, and order 1 and 2 give gradient descent and Newton’s method. Newton jumps along the tangent and doubles the correct digits each step but needs the Hessian. Matrix calculus rules such as ∇(xᵀAx) = (A + Aᵀ)x and ∇‖Xw − y‖² = 2Xᵀ(Xw − y) come with a shape check. Reverse mode autodiff gets the gradient for every weight in one backward pass. Products of per layer factors vanish or explode unless kept near 1. Convex functions have one minimum, and Jensen says f(E[X]) ≤ E[f(X)]. Subtract the max before exponentiating.',
}

REAL = [
    ['🧮', 'Calculators and maths libraries', 'Functions such as exp, sin and log in every programming language are computed with carefully tuned polynomial approximations close to Taylor series.'],
    ['🔥', 'PyTorch and JAX', 'Every call to loss.backward() or jax.grad runs reverse mode automatic differentiation over the recorded graph of operations.'],
    ['🏗️', 'Very deep networks', 'Residual connections and careful initialisation let transformers with dozens to hundreds of layers train without vanishing gradients.'],
]

K.say('top', 'Welcome',
      'This chapter shows the calculus that runs inside training code. You will build Taylor polynomials, solve equations with Newton’s method, learn the short list of matrix calculus rules, see how automatic differentiation works in forward and reverse mode, understand vanishing and exploding gradients, use convexity and Jensen’s inequality, and keep calculations stable on a real computer.',
      'यह अध्याय training code के अंदर चलने वाला calculus दिखाता है। Taylor polynomials, Newton method, matrix calculus के नियम, automatic differentiation के forward और reverse mode, vanishing और exploding gradients, convexity और Jensen inequality, और numerical stability सीखेंगे।',
      'ಈ ಅಧ್ಯಾಯ training code ಒಳಗಿನ calculus ತೋರಿಸುತ್ತದೆ. Taylor, Newton, matrix calculus, autodiff, vanishing gradients, convexity ಮತ್ತು numerical stability ಕಲಿಯುತ್ತೀರಿ.',
      'ଏହି ଅଧ୍ୟାୟ training code ଭିତରର calculus ଦେଖାଏ। Taylor, Newton, matrix calculus, autodiff, vanishing gradients, convexity ଓ numerical stability ଶିଖିବେ।',
      'يعرض هذا الفصل حساب التفاضل الذي يعمل داخل برامج التدريب. ستبني كثيرات حدود تايلور، وتحل المعادلات بطريقة نيوتن، وتتعلم قواعد حساب المصفوفات، وترى كيف يعمل الاشتقاق التلقائي، وتفهم تلاشي التدرجات وانفجارها، وتستخدم التحدب ومتباينة ينسن، وتحافظ على استقرار الحسابات.',
      'Dieses Kapitel zeigt die Analysis, die im Trainingscode läuft. Du baust Taylorpolynome, löst Gleichungen mit dem Newtonverfahren, lernst die Regeln der Matrixrechnung, siehst automatisches Differenzieren im Vorwärts und Rückwärtsmodus, verstehst verschwindende und explodierende Gradienten, nutzt Konvexität und die Jensensche Ungleichung und hältst Rechnungen numerisch stabil.')
K.say('taylor', 'Taylor series',
      'A Taylor polynomial copies a function near one point by matching its value, its slope, its bend and so on. Each matched derivative adds one term. For e to the x, sine and cosine the series works for every x. For the log of one plus x it only works between minus one and one.',
      'Taylor polynomial एक बिंदु के पास function की नकल करता है, उसका मान, ढलान और मोड़ मिलाकर। हर मिलाया गया derivative एक term जोड़ता है।',
      'Taylor polynomial ಒಂದು ಬಿಂದುವಿನ ಬಳಿ function ಅನ್ನು ನಕಲು ಮಾಡುತ್ತದೆ. ಪ್ರತಿ derivative ಒಂದು term ಸೇರಿಸುತ್ತದೆ.',
      'Taylor polynomial ଗୋଟିଏ ବିନ୍ଦୁ ପାଖରେ function ର ନକଲ କରେ। ପ୍ରତି derivative ଗୋଟିଏ term ଯୋଡ଼େ।',
      'كثيرة حدود تايلور تنسخ الدالة قرب نقطة بمطابقة قيمتها وميلها وانحنائها، وكل مشتقة مطابقة تضيف حدًا جديدًا.',
      'Ein Taylorpolynom bildet eine Funktion nahe einem Punkt nach, indem es Wert, Steigung, Krümmung und so weiter angleicht. Jede angeglichene Ableitung fügt einen Term hinzu.')
K.say('newton', 'Newton’s method',
      'Newton’s method draws the tangent line at the current guess and jumps to where it crosses zero. Near the answer the number of correct digits roughly doubles every step. For a minimum, apply the same rule to the slope, which needs the second derivative or the Hessian.',
      'Newton method वर्तमान अनुमान पर tangent line खींचकर वहाँ कूदता है जहाँ वह शून्य को काटती है। उत्तर के पास सही अंक हर कदम पर लगभग दोगुने होते हैं।',
      'Newton method tangent line ಎಳೆದು ಅದು ಶೂನ್ಯ ದಾಟುವಲ್ಲಿಗೆ ಜಿಗಿಯುತ್ತದೆ. ಸರಿಯಾದ ಅಂಕಿಗಳು ಪ್ರತಿ ಹೆಜ್ಜೆಗೆ ದ್ವಿಗುಣ.',
      'Newton method tangent line ଟାଣି ଶୂନ୍ୟ କାଟୁଥିବା ସ୍ଥାନକୁ ଡେଇଁଯାଏ। ଠିକ୍ ଅଙ୍କ ପ୍ରତି ପଦରେ ଦୁଇଗୁଣ।',
      'طريقة نيوتن ترسم المماس عند التخمين الحالي وتقفز إلى حيث يقطع الصفر، وقرب الحل يتضاعف عدد الأرقام الصحيحة تقريبًا في كل خطوة.',
      'Das Newtonverfahren zeichnet die Tangente am aktuellen Schätzwert und springt dorthin, wo sie null wird. Nahe der Lösung verdoppelt sich die Zahl der richtigen Stellen ungefähr mit jedem Schritt.')
K.say('matcalc', 'Matrix calculus',
      'A short table of rules replaces index by index work. The gradient of a transpose x is a, the gradient of x transpose A x is A plus A transpose times x, and the gradient of the squared error is two X transpose times the residual. Always check that the shapes match.',
      'कुछ नियम index वाला काम बचाते हैं। a transpose x का gradient a है, x transpose A x का gradient A plus A transpose गुणा x है। हमेशा shapes जाँचें।',
      'ಕೆಲವು ನಿಯಮಗಳು index ಕೆಲಸ ಉಳಿಸುತ್ತವೆ. ಯಾವಾಗಲೂ shapes ಪರಿಶೀಲಿಸಿ.',
      'କିଛି ନିୟମ index କାମ ବଞ୍ଚାଏ। ସବୁବେଳେ shapes ଯାଞ୍ଚ କରନ୍ତୁ।',
      'جدول قصير من القواعد يغني عن العمل بالمؤشرات. تدرج a منقول x هو a، وتدرج x منقول A x هو A زائد منقولها في x. تحقق دائمًا من تطابق الأشكال.',
      'Eine kurze Regeltabelle ersetzt die Arbeit mit Indizes. Der Gradient von a transponiert x ist a, der von x transponiert A x ist A plus A transponiert mal x. Prüfe immer, ob die Formen passen.')
K.say('autodiff', 'Automatic differentiation',
      'Autodiff applies the chain rule to every small step of a program. Forward mode carries a derivative along with each value and needs one pass per input. Reverse mode computes the values first, then walks back once and gets the derivative for every input together. Reverse mode is backpropagation.',
      'Autodiff program के हर छोटे कदम पर chain rule लगाता है। Forward mode हर input के लिए एक pass लेता है। Reverse mode एक बार पीछे चलकर सभी inputs के derivatives देता है। यही backpropagation है।',
      'Autodiff ಪ್ರತಿ ಹೆಜ್ಜೆಗೆ chain rule ಬಳಸುತ್ತದೆ. Reverse mode ಒಂದೇ ಹಿಂದಿನ pass ನಲ್ಲಿ ಎಲ್ಲಾ derivatives ಕೊಡುತ್ತದೆ.',
      'Autodiff ପ୍ରତି ପଦରେ chain rule ଲଗାଏ। Reverse mode ଗୋଟିଏ ପଛ pass ରେ ସବୁ derivatives ଦିଏ।',
      'الاشتقاق التلقائي يطبق قاعدة السلسلة على كل خطوة صغيرة في البرنامج. النمط الأمامي يحتاج تمريرة لكل مدخل، والنمط العكسي يعود مرة واحدة فيعطي مشتقات كل المدخلات معًا، وهو الانتشار العكسي.',
      'Automatisches Differenzieren wendet die Kettenregel auf jeden kleinen Programmschritt an. Der Vorwärtsmodus braucht einen Durchlauf pro Eingabe. Der Rückwärtsmodus geht einmal zurück und liefert alle Ableitungen zusammen. Das ist Backpropagation.')
K.say('vanish', 'Vanishing and exploding gradients',
      'The gradient that reaches an early layer is a product of one factor per layer. Factors a bit below one make it vanish, factors a bit above one make it explode. ReLU, careful initialisation, normalisation and residual connections keep the factors near one.',
      'शुरुआती layer तक पहुँचने वाला gradient हर layer के एक factor का गुणनफल है। एक से थोड़ा कम हो तो gradient गायब, थोड़ा ज़्यादा हो तो विस्फोट।',
      'Gradient ಪ್ರತಿ layer ನ factor ಗಳ ಗುಣಲಬ್ಧ. ಒಂದಕ್ಕಿಂತ ಕಡಿಮೆ ಇದ್ದರೆ ಮಾಯ, ಹೆಚ್ಚಿದ್ದರೆ ಸ್ಫೋಟ.',
      'Gradient ପ୍ରତି layer ର factor ର ଗୁଣଫଳ। ଏକରୁ କମ୍ ହେଲେ ଲୋପ, ଅଧିକ ହେଲେ ବିସ୍ଫୋରଣ।',
      'التدرج الذي يصل إلى طبقة مبكرة هو حاصل ضرب عامل لكل طبقة. العوامل الأصغر قليلًا من واحد تجعله يتلاشى، والأكبر قليلًا تجعله ينفجر.',
      'Der Gradient, der eine frühe Schicht erreicht, ist ein Produkt aus einem Faktor pro Schicht. Etwas unter eins verschwindet er, etwas über eins explodiert er.')
K.say('convex', 'Convexity and Jensen',
      'A convex function has every chord above its graph, so every local minimum is the global minimum. Jensen’s inequality says the function of the average is at most the average of the function. It proves that variance and KL divergence are never negative.',
      'Convex function में हर chord graph के ऊपर होती है, इसलिए हर local minimum global minimum है। Jensen inequality कहती है कि औसत का function, function के औसत से ज़्यादा नहीं होता।',
      'Convex function ನಲ್ಲಿ chord graph ಮೇಲೆ. Jensen inequality: ಸರಾಸರಿಯ function ≤ function ನ ಸರಾಸರಿ.',
      'Convex function ରେ chord graph ଉପରେ। Jensen inequality: ହାରାହାରିର function ≤ function ର ହାରାହାରି।',
      'في الدالة المحدبة يقع كل وتر فوق المنحنى، لذا كل قيمة صغرى محلية هي الصغرى الكلية. ومتباينة ينسن تقول إن الدالة عند المتوسط لا تتجاوز متوسط الدالة.',
      'Bei einer konvexen Funktion liegt jede Sehne über dem Graphen, daher ist jedes lokale Minimum global. Die Jensensche Ungleichung sagt, die Funktion des Mittelwerts ist höchstens der Mittelwert der Funktion.')
K.say('numerics', 'Numerical stability',
      'Floating point numbers keep only about sixteen digits. Large exponentials overflow, nearly equal numbers cancel, and long products of probabilities underflow. Subtract the maximum before exponentiating, add logs instead of multiplying, and pick the finite difference step with care.',
      'Floating point में लगभग सोलह अंक ही रहते हैं। बड़े exponentials overflow होते हैं। Exponent से पहले maximum घटाएँ और probabilities गुणा करने की जगह logs जोड़ें।',
      'Floating point ನಲ್ಲಿ ಸುಮಾರು ಹದಿನಾರು ಅಂಕಿಗಳು. ಮೊದಲು maximum ಕಳೆಯಿರಿ, logs ಕೂಡಿಸಿ.',
      'Floating point ରେ ପ୍ରାୟ ଷୋହଳ ଅଙ୍କ। ପ୍ରଥମେ maximum ବାଦ ଦିଅନ୍ତୁ, logs ଯୋଡ଼ନ୍ତୁ।',
      'الأعداد العشرية تحفظ نحو ستة عشر رقمًا فقط. الأسس الكبيرة تفيض، والأعداد المتقاربة تلغي بعضها. اطرح القيمة العظمى قبل الأس، واجمع اللوغاريتمات بدل ضرب الاحتمالات.',
      'Gleitkommazahlen behalten nur etwa sechzehn Stellen. Große Exponentiale laufen über, fast gleiche Zahlen löschen sich aus. Ziehe vor dem Exponenzieren das Maximum ab und addiere Logarithmen statt Wahrscheinlichkeiten zu multiplizieren.')
K.say('practice', 'Practice',
      'Now practise: count how many Taylor terms give e to six decimals, find a cube root with Newton’s method, check a logistic regression gradient numerically, and run Newton’s method in two dimensions on the banana shaped Rosenbrock function.',
      'अब अभ्यास: e के लिए कितने Taylor terms चाहिए, Newton से cube root, logistic regression के gradient की जाँच, और Rosenbrock function पर दो आयामों में Newton।',
      'ಅಭ್ಯಾಸ: e ಗೆ Taylor terms, Newton ನಿಂದ cube root, gradient check, Rosenbrock ಮೇಲೆ Newton.',
      'ଅଭ୍ୟାସ: e ପାଇଁ Taylor terms, Newton ରେ cube root, gradient check, Rosenbrock ଉପରେ Newton।',
      'تدرب الآن: احسب عدد حدود تايلور اللازمة للعدد e، وأوجد جذرًا تكعيبيًا بطريقة نيوتن، وافحص تدرج الانحدار اللوجستي عدديًا، وطبق نيوتن في بعدين على دالة روزنبروك.',
      'Jetzt üben: zähle die Taylorterme für e auf sechs Stellen, finde eine Kubikwurzel mit Newton, prüfe einen Gradienten der logistischen Regression numerisch und wende Newton in zwei Dimensionen auf die Rosenbrockfunktion an.')

# ---------------------------------------------------------------- practice
K.practice('taylor-e', 'e', 'How many terms does e need?', 'p_taylor_e',
           '<p>Add the terms 1/0! + 1/1! + 1/2! + … one at a time until the sum is within 0.000001 of e. Print how many terms you used.</p>',
           'terms used: 10 (1/0! up to 1/9!)\nsum = 2.7182815\ne   = 2.7182818',
           'Build each term from the previous one: 1/n! = (1/(n − 1)!) ÷ n.',
           '<p>Keep a running term and divide it by n each time, so no factorial is ever computed from scratch. After the 1/8! term the error is still about 0.000003. The 1/9! term (about 0.0000028) brings it to about 0.0000003, below the target. Ten terms give six correct decimals because the factorials grow so quickly.</p>',
           'O(n)', 'O(1)')
K.practice('cuberoot', 'm', 'Cube root with Newton’s method', 'p_cuberoot',
           '<p>Find the cube root of 10 by solving g(x) = x³ − 10 = 0 with Newton’s method from x₀ = 2. Stop when two guesses differ by less than 10⁻¹⁰.</p>',
           'step 1: x = 2.1666666667\nstep 2: x = 2.1545036160\nstep 3: x = 2.1544346922\nstep 4: x = 2.1544346900\nstep 5: x = 2.1544346900\ncheck: x^3 = 10.0000000000',
           'g′(x) = 3x², so the step is x − (x³ − 10) ÷ (3x²).',
           '<p>Starting at 2, the first step gives 2 − (8 − 10) ÷ 12 = 2.1667. The changes then shrink to about 0.012, 0.00007 and 0.000000002, showing the digits doubling. Step 5 changes nothing in the tenth decimal, so the loop stops. The same idea, with a clever first guess, is how many libraries compute cube roots.</p>',
           'O(log digits)', 'O(1)')
K.practice('grad-check', 'h', 'Gradient check for logistic regression', 'p_grad_check',
           '<p>The logistic loss for one example is L(w) = ln(1 + e<sup>−y w·x</sup>) with x = [1, 2], label y = 1 and w = [0.3, 0.2]. Derive the gradient by hand, compute it, then confirm it with central differences.</p>',
           'analytic gradient = [-0.331812, -0.663624]\nnumeric gradient  = [-0.331812, -0.663624]\ngradient check: PASS',
           'By the chain rule, ∇L = −y σ(−y w·x) x, where σ is the sigmoid.',
           '<p>Write u = −y w·x. Then L = ln(1 + eᵘ) and dL/du = eᵘ ÷ (1 + eᵘ) = σ(u). Also ∇u = −y x. So ∇L = −y σ(−y w·x) x. With w·x = 0.7, σ(−0.7) = 0.331812, giving [−0.331812, −0.663624]. The central difference with h = 10⁻⁶ agrees to better than one part in a million, so the check passes. Libraries test their backward passes exactly this way.</p>',
           'O(d) for the rule, O(d²) for the check', 'O(d)')
K.practice('newton-2d', 'x', 'Newton’s method on the Rosenbrock banana', 'p_newton_2d',
           '<p>Minimise f(x, y) = (1 − x)² + 100(y − x²)² from (−1.2, 1). At each step compute the gradient and the 2 × 2 Hessian, solve H d = −∇f, and move to the new point. Print seven steps.</p>',
           'start: x = -1.200000, y = 1.000000, f = 24.200000\nstep 1: x = -1.175281, y = 1.380674, f = 4.731884\nstep 2: x = 0.763115, y = -3.175034, f = 1411.845179\nstep 3: x = 0.763430, y = 0.582825, f = 0.055966\nstep 4: x = 0.999995, y = 0.944027, f = 0.313189\nstep 5: x = 0.999996, y = 0.999991, f = 0.000000\nstep 6: x = 1.000000, y = 1.000000, f = 0.000000\nstep 7: x = 1.000000, y = 1.000000, f = 0.000000',
           'Gradient: (−2(1 − x) − 400x(y − x²), 200(y − x²)). Hessian: [[2 − 400(y − x²) + 800x², −400x], [−400x, 200]].',
           '<p>The Rosenbrock function has a long curved valley, which makes plain gradient descent crawl for thousands of steps. Newton’s method uses the curvature and reaches (1, 1) in about six steps. Notice step 2: f jumps up to about 1400. Pure Newton does not promise that f goes down at every step, it only solves the local quadratic model. Practical solvers add a line search or a trust region to stop such jumps.</p>',
           'O(steps) with a 2 × 2 solve each', 'O(1)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'The order 1 Taylor polynomial of f at a point is…', ['the tangent line', 'a parabola', 'the average of f', 'always zero'], 0, 'Value plus slope times the step.', 'f(a) + f′(a)(x − a) is the tangent line.')
K.quiz('e', 'What is the next term of eˣ ≈ 1 + x + x²/2 + …?', ['x³/3', 'x³/6', 'x³', '3x³'], 1, 'xⁿ ÷ n!', '3! = 6.')
K.quiz('e', 'One Newton step for f(x) = x² − 4 from x₀ = 4 gives…', ['2', '2.5', '3', '4'], 1, 'x − f ÷ f′.', '4 − 12 ÷ 8 = 2.5.')
K.quiz('e', 'Which function is convex?', ['ln x', '√x', 'x²', 'sin x'], 2, 'The chord lies above the curve.', 'x² has second derivative 2, which is positive everywhere.')
K.quiz('m', 'What is the gradient of aᵀx with respect to x?', ['x', 'a', 'aᵀ', 'a·x'], 1, 'Like the derivative of a·x for numbers.', 'Each partial derivative ∂(Σaᵢxᵢ)/∂xⱼ is aⱼ.')
K.quiz('m', 'Which mode of automatic differentiation does backpropagation use?', ['forward mode', 'reverse mode', 'symbolic mode', 'numerical differences'], 1, 'One loss, millions of weights.', 'Reverse mode gets the gradient for every input in one backward pass.')
K.quiz('m', 'The sigmoid slope is at most 0.25. With weights of 1, what is the gradient factor after 3 layers at most?', ['0.75', '0.25', '0.015625', '0.0625'], 2, 'Multiply the per layer factors.', '0.25³ = 0.015625.')
K.quiz('m', 'Jensen’s inequality for a convex f says…', ['f(E[X]) ≥ E[f(X)]', 'f(E[X]) ≤ E[f(X)]', 'f(E[X]) = E[f(X)]', 'E[X] = 0'], 1, 'The chord is above the curve.', 'The function of the average is at most the average of the function.')
K.quiz('m', 'Why subtract the max score before computing softmax?', ['to make the result more accurate on paper', 'to avoid overflow in e^z without changing the answer', 'to make the scores negative for the loss', 'to sort the scores'], 1, 'e¹⁰⁰⁰ is too big for a float.', 'Softmax is unchanged when every score shifts by the same amount.')
K.quiz('h', 'In reverse mode, x is used by two nodes. Its adjoint is…', ['the larger of the two parts', 'the sum of the two parts', 'the product of the two parts', 'only the last part'], 1, 'Multivariable chain rule.', 'All paths from x to the output contribute, so their parts add up.')
K.quiz('h', 'What is the gradient of xᵀAx for a non symmetric A?', ['2Ax', '(A + Aᵀ)x', 'Aᵀx', 'xᵀA'], 1, 'Expand f(x + dx).', 'Both dxᵀAx and xᵀA dx appear, giving (A + Aᵀ)x.')
K.quiz('h', 'Near the answer, Newton’s method has quadratic convergence. This means…', ['the error halves each step', 'the number of correct digits roughly doubles each step', 'it needs exactly two steps', 'it only works for quadratics'], 1, 'Error becomes about error squared.', '0.01 becomes about 0.0001, then 0.00000001.')
K.quiz('h', 'For a forward difference in float64, roughly which step h gives the smallest error?', ['10⁻²', '10⁻⁸', '10⁻¹⁶', '10⁻³⁰⁰'], 1, 'Balance h against ε ÷ h.', 'The best h is about √ε ≈ 1.5 × 10⁻⁸.')
K.quiz('x', 'Why do residual connections help against vanishing gradients?', ['they remove the activation', 'the derivative of h + F(h) is 1 + F′(h), so there is always a path with factor 1', 'they make the weights larger', 'they use forward mode'], 1, 'Differentiate the identity part.', 'The "+1" lets the gradient pass through many layers without shrinking.')
K.quiz('x', 'A function f: ℝ³ → ℝ¹⁰⁰⁰ has 3 inputs and 1000 outputs. Which autodiff mode gets its full Jacobian with fewer passes?', ['reverse mode, 1000 passes', 'forward mode, 3 passes', 'both need 1 pass', 'neither can'], 1, 'Forward costs one pass per input.', 'Three forward passes give all 3 columns of the 1000 × 3 Jacobian.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Use the order 2 Taylor polynomial 1 + x + x²/2 to estimate e^0.2.', '1.22', 'Put x = 0.2 into each term.', [
    '<span class="eq">1</span>',
    '<span class="eq">x = 0.2</span>',
    '<span class="eq">x²/2 = 0.04 ÷ 2 = 0.02</span>, total <span class="eq">1.22</span> (true value 1.2214)',
], check=1 + 0.2 + 0.02)
K.calc('e', 'What is the first entry of the gradient of ‖x‖² at x = [3, 4]?', '6', '∇‖x‖² = 2x.', [
    'Rule: <span class="eq">∇(xᵀx) = 2x</span>',
    '<span class="eq">2 × [3, 4] = [6, 8]</span>',
    'First entry: <span class="eq">6</span>',
], check=6)
K.calc('e', 'One Newton step for x² − 9 = 0 from x₀ = 5. What is x₁?', '3.4', 'x₁ = x₀ − f(x₀) ÷ f′(x₀).', [
    '<span class="eq">f(5) = 25 − 9 = 16</span>',
    '<span class="eq">f′(5) = 10</span>',
    '<span class="eq">x₁ = 5 − 1.6 = 3.4</span>',
], check=3.4)
K.calc('e', 'Each of 3 sigmoid layers multiplies the gradient by 0.25. What fraction of the gradient reaches the first layer?', '0.015625', 'Multiply the three factors.', [
    '<span class="eq">0.25 × 0.25 = 0.0625</span>',
    '<span class="eq">0.0625 × 0.25 = 0.015625</span>',
    'Only about 1.6 % of the signal is left after 3 layers.',
], check=0.25 ** 3)
K.calc('m', 'Estimate sin 0.1 with x − x³/6. Give 5 decimals.', '0.09983', 'x³ = 0.001.', [
    '<span class="eq">x³/6 = 0.001 ÷ 6 = 0.000167</span>',
    '<span class="eq">0.1 − 0.000167 = 0.099833</span>',
    'The true value is 0.0998334, so two terms already give 6 correct decimals.',
], check=0.1 - 0.001 / 6, tol=1e-5)
K.calc('m', 'Minimise f(x) = x² − 4x + 7 with one Newton step from x₀ = 10. Where do you land?', '2', 'x₁ = x₀ − f′(x₀) ÷ f″(x₀).', [
    '<span class="eq">f′(10) = 2 × 10 − 4 = 16</span>',
    '<span class="eq">f″ = 2</span>',
    '<span class="eq">x₁ = 10 − 16 ÷ 2 = 2</span>, the exact minimum. Newton solves any quadratic in one step.',
], check=2)
K.calc('m', 'A = [[1, 2], [0, 3]], x = [1, 1]. What is the second entry of ∇(xᵀAx)?', '8', '∇ = (A + Aᵀ)x.', [
    '<span class="eq">A + Aᵀ = [[2, 2], [2, 6]]</span>',
    '<span class="eq">(A + Aᵀ)x = [2 + 2, 2 + 6] = [4, 8]</span>',
    'Second entry: <span class="eq">8</span>',
], check=8)
K.calc('m', 'Data 2 and 4, f(x) = x². What is the Jensen gap E[f(X)] − f(E[X])?', '1', 'Average of squares minus square of the average.', [
    '<span class="eq">E[X] = 3</span>, so <span class="eq">f(E[X]) = 9</span>',
    '<span class="eq">E[X²] = (4 + 16) ÷ 2 = 10</span>',
    'Gap: <span class="eq">10 − 9 = 1</span>, which is the variance.',
], check=1)
K.calc('h', 'X = [[1, 0], [0, 1], [1, 1]], y = [1, 0, 1], w = [1, 1]. What is the second entry of ∇‖Xw − y‖²?', '4', '∇ = 2Xᵀ(Xw − y).', [
    '<span class="eq">Xw = [1, 1, 2]</span>, residual <span class="eq">r = [0, 1, 1]</span>',
    '<span class="eq">Xᵀr = [0 + 0 + 1, 0 + 1 + 1] = [1, 2]</span>',
    '<span class="eq">2Xᵀr = [2, 4]</span>, second entry <span class="eq">4</span>',
], check=4)
K.calc('h', 'f(x, y) = x·y + y². Using reverse mode at (3, 2), what is ∂f/∂y?', '7', 'y feeds two nodes, so add both parts.', [
    'From x·y: <span class="eq">∂/∂y = x = 3</span>',
    'From y²: <span class="eq">∂/∂y = 2y = 4</span>',
    'Add: <span class="eq">3 + 4 = 7</span>',
], check=7)
K.calc('x', 'Machine epsilon for float64 is about 2.2 × 10⁻¹⁶. A forward difference loses about half the digits. About how many correct digits are left at best?', '8', 'Best h ≈ √ε, error ≈ √ε.', [
    '<span class="eq">√(2.2 × 10⁻¹⁶) ≈ 1.5 × 10⁻⁸</span>',
    'Relative error about <span class="eq">10⁻⁸</span>',
    'So about <span class="eq">8</span> of the 16 digits are correct.',
], check=8)
K.calc('x', 'Compute ln(e¹⁰⁰ + e¹⁰⁰) with the log-sum-exp trick. Give 4 decimals.', '100.6931', 'm = 100, then ln(e⁰ + e⁰).', [
    'Take out the max: <span class="eq">m = 100</span>',
    '<span class="eq">ln(e⁰ + e⁰) = ln 2 = 0.6931</span>',
    'Answer: <span class="eq">100 + 0.6931 = 100.6931</span>',
], check=100.69314718, tol=1e-4)

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;
  const fmt = v => MV.num(Math.abs(v) < 1e-9 ? 0 : v, 3);
  const fact = n => n <= 1 ? 1 : n * fact(n - 1);
  const sup = n => String(n).replace(/-/g, '⁻').replace(/\d/g, d => '⁰¹²³⁴⁵⁶⁷⁸⁹'[d]);
  const setSl = (b, k, v, d = 2) => { $(`[data-sl="${k}"]`, b).value = v; $(`[data-slv="${k}"]`, b).textContent = MV.num(v, d); };

  /* ----- Taylor polynomials closing in on a function ----- */
  W.taylorviz = el => {
    const b = shell(el, 'Taylor polynomials hugging a curve', 'Pick a function, then raise the order n. The orange curve is the Taylor polynomial built at 0. Move x to compare the true value with the approximation. Press Play to add one term at a time.');
    b.innerHTML = `<div class="vz-row">${seg('fn', [['sin', 'sin x'], ['exp', 'eˣ'], ['ln', 'ln(1 + x)']], 'sin')}</div><div class="mv-wrap"><div class="ty-plot"></div><div class="mv-side">${slider('n', 'order n', 0, 12, 3, 1)}${slider('x', 'x', -3, 3, 1.5, 0.1)}<div class="mv-legend"><span><i></i>true function</span><span><i class="o"></i>Taylor polynomial</span></div><div class="mv-read ty-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const FN = {
      sin: { f: Math.sin, c: k => k % 2 ? (k % 4 === 1 ? 1 : -1) / fact(k) : 0, xr: [-6, 6], yr: [-2.5, 2.5], den: k => k + '!', note: 'The series works for every x, larger x just needs more terms.' },
      exp: { f: Math.exp, c: k => 1 / fact(k), xr: [-3, 3], yr: [-2, 12], den: k => k + '!', note: 'The series works for every x.' },
      ln: { f: x => x > -1 ? Math.log(1 + x) : NaN, c: k => k === 0 ? 0 : (k % 2 ? 1 : -1) / k, xr: [-1.5, 2.5], yr: [-3, 2.5], den: k => String(k), note: 'Only works for −1 &lt; x ≤ 1. Past x = 1 more terms make it worse.' },
    };
    const S = { fn: 'sin', n: 3, x: 1.5 };
    const poly = (F, x) => { let s = 0; for (let k = 0; k <= S.n; k++) s += F.c(k) * x ** k; return s; };
    function draw() {
      const F = FN[S.fn], G = MV.frame(440, 320, F.xr, F.yr);
      const x = Math.max(F.xr[0], Math.min(F.xr[1], S.x));
      let s = MV.axes(G, {}) + MV.curve(G, F.f, '') + MV.curve(G, t => poly(F, t), 'c2');
      const tv = F.f(x), pv = poly(F, x);
      s += MV.line(G, x, F.yr[0], x, F.yr[1], 'mv-v k dash');
      if (isFinite(tv) && tv >= F.yr[0] && tv <= F.yr[1]) s += MV.dot(G, x, tv, '', 6);
      if (pv >= F.yr[0] && pv <= F.yr[1]) s += MV.dot(G, x, pv, 'o', 6);
      $('.ty-plot', b).innerHTML = MV.svg(G, s, 'Taylor polynomial and function');
      const terms = [];
      for (let k = 0; k <= S.n; k++) { const c = F.c(k); if (!c) continue; const sign = c < 0 ? ' − ' : terms.length ? ' + ' : ''; terms.push(sign + (k === 0 ? '1' : k === 1 ? 'x' : `x${sup(k)}/${F.den(k)}`)); }
      const shown = terms.length > 5 ? terms.slice(0, 5).join('') + ' + …' : terms.join('') || '0';
      $('.ty-out', b).innerHTML = `p(x) = ${shown}<br>at x = ${fmt(x)}:<br>true value = <b>${isFinite(tv) ? fmt(tv) : 'undefined'}</b><br>polynomial = <b>${fmt(pv)}</b><br>error = <span class="big">${isFinite(tv) ? MV.num(Math.abs(tv - pv), 6) : '?'}</span><br>${F.note}`;
    }
    const P = Player($('.vz-p', b), t => { S.n = t; setSl(b, 'n', t, 0); draw(); }, 900);
    wireSlider(b, 'n', v => { P.pause(); S.n = v; draw(); });
    wireSlider(b, 'x', v => { S.x = v; draw(); });
    wireSeg(b, 'fn', k => { S.fn = k; P.load(13, 3); });
    P.load(13, 3);
  };

  /* ----- Newton's method, one tangent line at a time ----- */
  W.newtonviz = el => {
    const b = shell(el, 'Newton’s method, tangent by tangent', 'Pick a function and a starting point x₀, then press Play. Each step draws the tangent at the current point (orange) and jumps to where it crosses zero. On the third function the guesses bounce back and forth forever.');
    const CASES = {
      sq: { f: x => x * x - 2, d: x => 2 * x, xr: [-0.5, 3.5], yr: [-3, 10], x0: 3, name: 'x² − 2', root: Math.SQRT2 },
      cos: { f: x => Math.cos(x) - x, d: x => -Math.sin(x) - 1, xr: [-1, 3], yr: [-3.5, 2], x0: 2.5, name: 'cos x − x', root: 0.7390851332 },
      cyc: { f: x => x ** 3 - 2 * x + 2, d: x => 3 * x * x - 2, xr: [-2.5, 2], yr: [-4, 6], x0: 0, name: 'x³ − 2x + 2', root: -1.7692923542 },
    };
    b.innerHTML = `<div class="vz-row">${seg('c', [['sq', 'x² − 2'], ['cos', 'cos x − x'], ['cyc', 'x³ − 2x + 2']], 'sq')}</div><div class="mv-wrap"><div class="nw-plot"></div><div class="mv-side">${slider('x0', 'start x₀', -2.5, 3.5, 3, 0.1)}<div class="mv-read nw-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let C = CASES.sq, x0 = 3, st = 0;
    function draw() {
      const G = MV.frame(440, 340, C.xr, C.yr);
      let s = MV.axes(G, {}) + MV.curve(G, C.f, '');
      const xs = [Math.max(C.xr[0], Math.min(C.xr[1], x0))], L = [`f(x) = ${C.name}`];
      let stop = '';
      for (let i = 0; i < st; i++) {
        const x = xs[i], fx = C.f(x), dx = C.d(x);
        if (Math.abs(dx) < 1e-9) { stop = 'The tangent is flat (f′ = 0), so Newton cannot continue.'; break; }
        const nx = x - fx / dx;
        s += MV.line(G, x, fx, nx, 0, 'mv-v o') + MV.line(G, nx, 0, nx, C.f(nx), 'mv-v k dash') + MV.dot(G, x, fx, 'o', 5);
        xs.push(nx);
        if (Math.abs(nx) > 1e6) { stop = 'The guess shot off to a huge value.'; break; }
      }
      const cur = xs[xs.length - 1];
      s += MV.dot(G, cur, 0, 'p', 7);
      $('.nw-plot', b).innerHTML = MV.svg(G, s, 'Newton iterations');
      xs.slice(-6).forEach((x, i, arr) => { const k = xs.length - arr.length + i; L.push(`x${'₀₁₂₃₄₅₆₇₈'[k] || k} = <b>${MV.num(x, 8)}</b>, error ${MV.num(Math.abs(x - C.root), 8)}`); });
      $('.nw-out', b).innerHTML = L.join('<br>') + (stop ? `<br>⚠️ ${stop}` : '') + (st >= 2 && Math.abs(cur - C.root) > 0.1 && !stop ? '<br>⚠️ No progress: the guesses are cycling.' : '');
    }
    const P = Player($('.vz-p', b), t => { st = t; draw(); }, 1100);
    wireSlider(b, 'x0', v => { x0 = v; P.load(8, 0); });
    wireSeg(b, 'c', k => { C = CASES[k]; x0 = C.x0; setSl(b, 'x0', x0, 1); P.load(8, 0); });
    P.load(8, 0);
  };

  /* ----- gradient descent zigzag against one Newton step on a quadratic bowl ----- */
  W.gradbowl = el => {
    const b = shell(el, 'Gradient steps versus one Newton step', 'The bowl is f(x) = ½(x − m)ᵀA(x − m), lowest at m (purple). Drag the start point. Blue is gradient descent with step 1 ÷ λmax, orange is Newton’s method, which uses the Hessian A and lands on m in one step. Make the bowl long and thin with the sliders and watch the blue path zigzag.');
    b.innerHTML = `<div class="mv-wrap"><div class="gb-plot"></div><div class="mv-side">${slider('c', 'coupling c', -0.9, 0.9, 0.6, 0.05)}${slider('d', 'stretch d', 0.2, 4, 3, 0.1)}<div class="mv-legend"><span><i></i>gradient descent</span><span><i class="o"></i>Newton</span></div><div class="mv-read gb-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const G = MV.frame(400, 400, [-3, 3], [-3, 3]);
    const m = [0.5, 0.5], p = [-2.5, 2], S = { c: 0.6, d: 3, t: 25 };
    const host = $('.gb-plot', b);
    host.innerHTML = MV.svg(G, '<g class="gb-g"></g>', 'Gradient descent and Newton on a bowl');
    const svgEl = $('svg', host);
    function draw() {
      const a = 1, c = S.c, d = S.d, det = a * d - c * c;
      const mul = u => [a * u[0] + c * u[1], c * u[0] + d * u[1]];
      let s = MV.axes(G, { labels: false });
      const L = [];
      if (det <= 1e-6) {
        s += MV.dot(G, m[0], m[1], 'p', 6);
        L.push(`det A = ${fmt(det)} ≤ 0: A is not positive definite, so the surface is a saddle or a trough with no single bottom. Lower the coupling.`);
      } else {
        const tr = a + d, g0 = Math.sqrt(tr * tr / 4 - det), lmax = tr / 2 + g0, lmin = tr / 2 - g0, lr = 1 / lmax;
        [0.1, 0.5, 1.5, 3, 6, 10].forEach(lv => {
          const pts = [];
          for (let k = 0; k <= 96; k++) { const th = k / 96 * 2 * Math.PI, u = [Math.cos(th), Math.sin(th)], q = u[0] * mul(u)[0] + u[1] * mul(u)[1], r = Math.sqrt(2 * lv / q); pts.push(G.sx(m[0] + r * u[0]).toFixed(1) + ',' + G.sy(m[1] + r * u[1]).toFixed(1)); }
          s += `<polygon class="mv-cont" style="fill:none" points="${pts.join(' ')}"/>`;
        });
        let x = p.slice(), path = [x.slice()], steps = 0;
        for (let k = 0; k < S.t; k++) { const g = mul([x[0] - m[0], x[1] - m[1]]); x = [x[0] - lr * g[0], x[1] - lr * g[1]]; path.push(x.slice()); }
        let y = p.slice();
        while (steps < 5000 && Math.hypot(y[0] - m[0], y[1] - m[1]) > 0.01) { const g = mul([y[0] - m[0], y[1] - m[1]]); y = [y[0] - lr * g[0], y[1] - lr * g[1]]; steps++; }
        s += `<polyline class="mv-curve" style="fill:none" points="${path.map(q => G.sx(q[0]).toFixed(1) + ',' + G.sy(q[1]).toFixed(1)).join(' ')}"/>`;
        path.forEach(q => { s += MV.dot(G, q[0], q[1], '', 2.5); });
        s += MV.arrow(G, p[0], p[1], m[0], m[1], 'o');
        s += MV.dot(G, m[0], m[1], 'p', 6);
        const g = mul([p[0] - m[0], p[1] - m[1]]);
        L.push(`A = [[1, ${fmt(c)}], [${fmt(c)}, ${fmt(d)}]]`, `gradient at start: A(x − m) = [${fmt(g[0])}, ${fmt(g[1])}]`, `Newton step: −A⁻¹∇f = [${fmt(m[0] - p[0])}, ${fmt(m[1] - p[1])}], lands on m in <b>1</b> step`, `eigenvalues λmax = ${fmt(lmax)}, λmin = ${fmt(lmin)}`, `condition number κ = <b>${fmt(lmax / lmin)}</b>`, `gradient descent needs <span class="big">${steps >= 5000 ? '5000+' : steps}</span> steps to get within 0.01`, `showing the first ${S.t} blue steps`);
      }
      s += `<circle class="mv-pt big mv-drag" data-h="0" cx="${G.sx(p[0])}" cy="${G.sy(p[1])}" r="10"/>`;
      $('.gb-g', svgEl).innerHTML = s;
      $('.gb-out', b).innerHTML = L.join('<br>');
    }
    const snap = v => Math.round(v * 4) / 4;
    MV.drag(svgEl, G, [{ set: (x, y) => { p[0] = snap(x); p[1] = snap(y); } }], draw);
    const P = Player($('.vz-p', b), t => { S.t = t; draw(); }, 400);
    ['c', 'd'].forEach(k => wireSlider(b, k, v => { S[k] = v; draw(); }));
    P.load(26, 25);
  };

  /* ----- forward and reverse mode on a five node graph ----- */
  W.adtape = el => {
    const b = shell(el, 'Automatic differentiation on a tiny graph', 'f(x, y) = x·y + sin x. Choose a mode and press Play. Forward mode carries one derivative forward with every value, so it needs one pass per input. Reverse mode computes the values, then walks back once and gets the derivative for every input together.');
    b.innerHTML = `<div class="vz-row">${seg('m', [['rev', 'reverse mode'], ['fx', 'forward, seed x'], ['fy', 'forward, seed y']], 'rev')}</div><div class="mv-wrap"><div class="ad-plot"></div><div class="mv-side">${slider('x', 'x', -3, 3, 2, 0.1)}${slider('y', 'y', -3, 3, 3, 0.1)}<div class="mv-read ad-out" aria-live="polite"></div></div></div><div class="mv-calc ad-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const S = { m: 'rev', x: 2, y: 3, t: 10 };
    const G = MV.frame(520, 270, [0, 520], [270, 0], 0);
    const POS = { x: [75, 70], y: [75, 200], v2: [265, 70], v1: [265, 200], f: [450, 135] };
    const EDGES = [['x', 'v2'], ['x', 'v1'], ['y', 'v1'], ['v2', 'f'], ['v1', 'f']];
    const FWD = ['x', 'y', 'v1', 'v2', 'f'], BACK = ['f', 'v1', 'v2', 'y', 'x'];
    const LAB = { x: 'x', y: 'y', v1: 'v₁ = x · y', v2: 'v₂ = sin x', f: 'f = v₁ + v₂' };
    const total = () => S.m === 'rev' ? 11 : 6;
    function draw() {
      const { x, y } = S, val = { x, y, v1: x * y, v2: Math.sin(x) }; val.f = val.v1 + val.v2;
      const dx = S.m === 'fx' ? 1 : 0, dy = S.m === 'fy' ? 1 : 0;
      const tan = { x: dx, y: dy, v1: dx * y + x * dy, v2: Math.cos(x) * dx }; tan.f = tan.v1 + tan.v2;
      const adj = { f: 1, v1: 1, v2: 1, y: x, x: y + Math.cos(x) };
      const t = S.t, nv = Math.min(t, 5), na = S.m === 'rev' ? Math.max(0, t - 5) : 0;
      const hasV = k => FWD.indexOf(k) < nv, hasA = k => BACK.indexOf(k) < na;
      const cur = S.m === 'rev' && t > 5 ? BACK[t - 6] : t >= 1 && t <= 5 ? FWD[t - 1] : null;
      let s = '';
      EDGES.forEach(([u, v]) => {
        const A = POS[u], B = POS[v], back = S.m === 'rev' && cur === u && t > 5 && hasA(v);
        s += back ? MV.arrow(G, B[0] - 62, B[1], A[0] + 62, A[1], 'o') : MV.arrow(G, A[0] + 62, A[1], B[0] - 62, B[1], 'k');
      });
      FWD.forEach(k => {
        const [cx, cy] = POS[k], on = k === cur, done = hasV(k);
        s += `<rect class="ad-node ${on ? 'on' : done ? 'done' : ''}" x="${cx - 62}" y="${cy - 31}" width="124" height="62" rx="10"/>`;
        s += `<text class="mv-lab" x="${cx}" y="${cy - 11}" text-anchor="middle">${LAB[k]}</text>`;
        if (done) s += `<text class="mv-lab sm" x="${cx}" y="${cy + 6}" text-anchor="middle">value ${fmt(val[k])}</text>`;
        if (S.m !== 'rev' && done) s += `<text class="mv-lab sm" x="${cx}" y="${cy + 22}" text-anchor="middle">d/d${S.m === 'fx' ? 'x' : 'y'} ${fmt(tan[k])}</text>`;
        if (S.m === 'rev' && hasA(k)) s += `<text class="mv-lab sm" x="${cx}" y="${cy + 22}" text-anchor="middle">∂f/∂${k === 'v1' ? 'v₁' : k === 'v2' ? 'v₂' : k} ${fmt(adj[k])}</text>`;
      });
      $('.ad-plot', b).innerHTML = MV.svg(G, s, 'Computational graph');
      const MSG = {
        x: 'Read the input x.', y: 'Read the input y.', v1: 'Compute v₁ = x · y.', v2: 'Compute v₂ = sin x.', f: 'Compute f = v₁ + v₂. The forward pass is done.',
      };
      const AMSG = {
        f: 'Start the walk back with ∂f/∂f = 1.', v1: 'f = v₁ + v₂, so ∂f/∂v₁ = 1.', v2: 'Also ∂f/∂v₂ = 1.',
        y: `v₁ = x · y, so ∂f/∂y = ∂f/∂v₁ × x = ${fmt(x)}.`, x: `x feeds two nodes, so its parts add: ∂f/∂v₁ × y + ∂f/∂v₂ × cos x = ${fmt(y)} ${Math.cos(x) < 0 ? '−' : '+'} ${fmt(Math.abs(Math.cos(x)))} = ${fmt(adj.x)}.`,
      };
      let msg = t === 0 ? 'Nothing computed yet. Press Play.' : cur && t <= 5 ? MSG[cur] : AMSG[cur];
      if (S.m !== 'rev' && t >= 1) msg += ` Each node also carries its slope with respect to ${S.m === 'fx' ? 'x' : 'y'}, by the product and chain rules.`;
      $('.ad-msg', b).innerHTML = `<span class="t">step ${t}</span> ${msg}`;
      const L = [`f = <b>${fmt(val.f)}</b>`, `exact: ∂f/∂x = y + cos x = <b>${fmt(adj.x)}</b>`, `exact: ∂f/∂y = x = <b>${fmt(x)}</b>`];
      L.push(S.m === 'rev' ? 'Reverse mode: 1 forward pass + 1 backward pass gives both.' : `Forward mode: this pass gives only ∂f/∂${S.m === 'fx' ? 'x' : 'y'}. A second pass is needed for the other one.`);
      $('.ad-out', b).innerHTML = L.join('<br>');
    }
    const P = Player($('.vz-p', b), t => { S.t = t; draw(); }, 1300);
    ['x', 'y'].forEach(k => wireSlider(b, k, v => { S[k] = v; draw(); }));
    wireSeg(b, 'm', k => { S.m = k; P.load(total(), total() - 1); });
    P.load(11, 10);
  };

  /* ----- gradient size layer by layer on a log scale ----- */
  W.gradflow = el => {
    const b = shell(el, 'Gradients through 20 layers', 'Each layer multiplies the gradient by (slope of the activation at z) × (weight w). Bars show the size reaching each layer on a log scale, so each grid line is 10 000 times bigger or smaller. Press Play to sweep w.');
    b.innerHTML = `<div class="vz-row">${seg('act', [['sig', 'sigmoid'], ['tanh', 'tanh'], ['relu', 'ReLU']], 'sig')}</div><div class="mv-wrap"><div class="gf-plot"></div><div class="mv-side">${slider('w', 'weight w', 0.2, 5, 1, 0.1)}${slider('z', 'input z of each unit', -4, 4, 0, 0.5)}<div class="mv-read gf-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const S = { act: 'sig', w: 1, z: 0 };
    const G = MV.frame(440, 300, [0, 21], [-12, 6], 40);
    const slope = () => { const z = S.z; if (S.act === 'sig') { const q = 1 / (1 + Math.exp(-z)); return q * (1 - q); } if (S.act === 'tanh') { const q = Math.tanh(z); return 1 - q * q; } return z >= 0 ? 1 : 0; };
    const sci = v => v === 0 ? '0' : v.toExponential(2).replace('e', ' × 10^').replace('^+', '^').replace(/\^(-?\d+)/, (_, e) => sup(e));
    function draw() {
      const fac = slope() * S.w;
      let s = MV.axes(G, { labels: false, xstep: 5, ystep: 4 }), g = 1;
      for (let L = 1; L <= 20; L++) {
        g *= fac;
        const lg = g > 0 ? Math.max(-12, Math.min(6, Math.log10(g))) : -12;
        const y0 = G.sy(0), y1 = G.sy(lg);
        s += `<rect class="mv-bar ${lg < -0.5 ? '' : lg > 0.5 ? 'o' : 'g'}" x="${(G.sx(L) - 6).toFixed(1)}" y="${Math.min(y0, y1).toFixed(1)}" width="12" height="${Math.max(1, Math.abs(y1 - y0)).toFixed(1)}" rx="2"/>`;
      }
      [-8, -4, 0, 4].forEach(v => { s += MV.text(G, 0, v, '10' + sup(v), { dx: -4, dy: 4, anchor: 'end', cls: 'sm' }); });
      [1, 5, 10, 15, 20].forEach(L => { s += MV.text(G, L, -12, String(L), { dy: 15, anchor: 'middle', cls: 'sm' }); });
      $('.gf-plot', b).innerHTML = MV.svg(G, s, 'Gradient size per layer');
      const at = n => sci(Math.pow(fac, n));
      const verdict = fac < 0.9 ? '📉 vanishing: the early layers barely learn' : fac > 1.1 ? '💥 exploding: updates blow up' : '✅ healthy: the factor is close to 1';
      $('.gf-out', b).innerHTML = `slope at z = ${fmt(S.z)}: <b>${fmt(slope())}</b><br>factor per layer = slope × w = <b>${fmt(fac)}</b><br>after 5 layers: ${at(5)}<br>after 10 layers: ${at(10)}<br>after 20 layers: <span class="big">${at(20)}</span><br>${verdict}<br>layer number along the bottom`;
    }
    const P = Player($('.vz-p', b), t => { S.w = Math.round((0.2 + t * 0.2) * 10) / 10; setSl(b, 'w', S.w, 1); draw(); }, 450);
    wireSlider(b, 'w', v => { P.pause(); S.w = v; draw(); });
    wireSlider(b, 'z', v => { S.z = v; draw(); });
    wireSeg(b, 'act', k => { S.act = k; draw(); });
    P.load(25, 4);
  };

  /* ----- Jensen: the chord sits above a convex curve ----- */
  W.jensenviz = el => {
    const b = shell(el, 'Jensen’s inequality: the chord sits above', 'Drag the two blue points along the curve and move the weight t. The purple dot mixes the two curve values (it lies on the chord). The green dot is the curve at the mixed x. For a convex curve purple is never below green. Press Play to slide t.');
    const FN = {
      sq: { f: x => x * x, xr: [-3, 3], yr: [-1, 9], a: -2, b: 2.5, name: 'x²', kind: 'convex' },
      exp: { f: Math.exp, xr: [-2, 2.5], yr: [-1, 12], a: -1.5, b: 2.2, name: 'eˣ', kind: 'convex' },
      log: { f: x => Math.log(x), xr: [0.1, 6], yr: [-2.5, 2.2], a: 0.3, b: 5, name: 'ln x', kind: 'concave' },
      sin: { f: Math.sin, xr: [-1, 7], yr: [-1.5, 1.5], a: 0.5, b: 5.5, name: 'sin x', kind: 'neither' },
    };
    b.innerHTML = `<div class="vz-row">${seg('fn', [['sq', 'x²'], ['exp', 'eˣ'], ['log', 'ln x'], ['sin', 'sin x']], 'sq')}</div><div class="mv-wrap"><div class="jn-plot"></div><div class="mv-side">${slider('t', 'weight t', 0, 1, 0.5, 0.05)}<div class="mv-read jn-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let F = FN.sq, A = F.a, B = F.b, t = 0.5, G, svgEl;
    function mount() {
      G = MV.frame(420, 340, F.xr, F.yr);
      const host = $('.jn-plot', b);
      host.innerHTML = MV.svg(G, '<g class="jn-g"></g>', 'Chord above a curve');
      svgEl = $('svg', host);
      MV.drag(svgEl, G, [{ set: x => { A = x; } }, { set: x => { B = x; } }], draw);
    }
    function draw() {
      const xm = t * A + (1 - t) * B, chord = t * F.f(A) + (1 - t) * F.f(B), curve = F.f(xm), gap = chord - curve;
      let s = MV.axes(G, {}) + MV.curve(G, F.f, '') + MV.line(G, A, F.f(A), B, F.f(B), 'mv-v p');
      s += MV.line(G, xm, curve, xm, chord, 'mv-v k dash') + MV.dot(G, xm, curve, 'g', 6) + MV.dot(G, xm, chord, 'p', 6);
      s += `<circle class="mv-pt big mv-drag" data-h="0" cx="${G.sx(A)}" cy="${G.sy(F.f(A))}" r="9"/><circle class="mv-pt big mv-drag" data-h="1" cx="${G.sx(B)}" cy="${G.sy(F.f(B))}" r="9"/>`;
      $('.jn-g', svgEl).innerHTML = s;
      const msg = F.kind === 'convex' ? 'Convex: the gap is never negative.' : F.kind === 'concave' ? 'Concave: the chord is below, so the sign flips.' : 'Neither: the gap changes sign as you drag.';
      $('.jn-out', b).innerHTML = `f(x) = ${F.name}<br>a = ${fmt(A)}, b = ${fmt(B)}<br>mixed x = t a + (1 − t) b = <b>${fmt(xm)}</b><br>curve at mixed x (green) = <b>${fmt(curve)}</b><br>mix of values (purple) = <b>${fmt(chord)}</b><br>gap = purple − green = <span class="big">${fmt(gap)}</span><br>${msg}`;
    }
    const P = Player($('.vz-p', b), k => { t = k / 20; setSl(b, 't', t); draw(); }, 300);
    wireSlider(b, 't', v => { P.pause(); t = v; draw(); });
    wireSeg(b, 'fn', k => { F = FN[k]; A = F.a; B = F.b; mount(); draw(); });
    mount();
    P.load(21, 10);
  };

  /* ----- finite difference error against step size, both axes logarithmic ----- */
  W.fdiffviz = el => {
    const b = shell(el, 'Finite differences: the best step size', 'The slope of f at x = 1 is estimated with a step h. A big step misses the curve (truncation error), a tiny step drowns in rounding error. Both axes are logarithmic. Move h or press Play to shrink it.');
    const FN = { sin: { f: Math.sin, d: Math.cos(1) }, exp: { f: Math.exp, d: Math.E }, cube: { f: x => x * x * x, d: 3 } };
    b.innerHTML = `<div class="vz-row">${seg('fn', [['sin', 'sin x'], ['exp', 'eˣ'], ['cube', 'x³']], 'sin')}</div><div class="mv-wrap"><div class="fd-plot"></div><div class="mv-side">${slider('k', 'log₁₀ h', -15, -1, -4, 0.5)}<div class="mv-legend"><span><i></i>forward difference</span><span><i class="o"></i>central difference</span></div><div class="mv-read fd-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const S = { fn: 'sin', k: -4 };
    const G = MV.frame(440, 320, [-16, 0], [-16, 1], 40);
    function errs(h) {
      const F = FN[S.fn], fw = (F.f(1 + h) - F.f(1)) / h, ce = (F.f(1 + h) - F.f(1 - h)) / (2 * h);
      return { fw, ce, ef: Math.abs(fw - F.d), ec: Math.abs(ce - F.d) };
    }
    const lg = v => Math.log10(Math.max(v, 1e-16));
    function draw() {
      let s = MV.axes(G, { labels: false, xstep: 4, ystep: 4 });
      s += MV.curve(G, k => lg(errs(Math.pow(10, k)).ef), '', { n: 400 }) + MV.curve(G, k => lg(errs(Math.pow(10, k)).ec), 'c2', { n: 400 });
      const h = Math.pow(10, S.k), E = errs(h);
      s += MV.line(G, S.k, -16, S.k, 1, 'mv-v k dash') + MV.dot(G, S.k, lg(E.ef), '', 6) + MV.dot(G, S.k, lg(E.ec), 'o', 6);
      [-12, -8, -4, 0].forEach(v => { s += MV.text(G, v, -16, '10' + sup(v), { dy: 16, anchor: 'middle', cls: 'sm' }); s += MV.text(G, -16, v, '10' + sup(v), { dx: -4, dy: 4, anchor: 'end', cls: 'sm' }); });
      $('.fd-plot', b).innerHTML = MV.svg(G, s, 'Error against step size');
      const e = v => v === 0 ? '0' : v.toExponential(1);
      $('.fd-out', b).innerHTML = `h = 10${sup(S.k)}<br>true slope = <b>${MV.num(FN[S.fn].d, 10)}</b><br>forward = ${MV.num(E.fw, 10)}, error <b>${e(E.ef)}</b><br>central = ${MV.num(E.ce, 10)}, error <b>${e(E.ec)}</b><br>across: step h, up: error<br>best forward h ≈ 10⁻⁸, best central h ≈ 10⁻⁵`;
    }
    const P = Player($('.vz-p', b), t => { S.k = -1 - t * 0.5; setSl(b, 'k', S.k, 1); draw(); }, 350);
    wireSlider(b, 'k', v => { P.pause(); S.k = v; draw(); });
    wireSeg(b, 'fn', k => { S.fn = k; draw(); });
    P.load(29, 6);
  };
})();
'''

CSS = r'''
.ty-plot .mv-svg,.nw-plot .mv-svg,.gb-plot .mv-svg,.jn-plot .mv-svg{max-height:420px}
.ad-node{fill:var(--surface); stroke:var(--line); stroke-width:1.5}
.ad-node.done{stroke:var(--accent); stroke-width:2}
.ad-node.on{stroke:var(--orange); stroke-width:3}
'''

T = K.topic(
    slug='taylor-autodiff', topic='taylor-autodiff', prefix='mm14', short='Taylor and autodiff', emoji='🧠',
    title='Taylor Series, Newton’s Method and Automatic Differentiation',
    module=('🚀', 'Advanced maths for ML', 'advanced', 'The next level: matrix factorisations and tensors, Taylor series, Newton’s method and automatic differentiation, and Bayesian inference with sampling.'),
    minutes=60, added='2026-10-24',
    lead='See the calculus that runs inside training code. Approximate functions with Taylor polynomials, solve and minimise with Newton’s method, use matrix calculus rules with a shape check, watch automatic differentiation run forward and backward, understand vanishing and exploding gradients, use convexity and Jensen’s inequality, and keep numbers stable on a real computer.',
    desc='Advanced calculus for machine learning: Taylor and Maclaurin series with the remainder, Newton’s method for roots and minimums, matrix calculus rules, forward and reverse mode automatic differentiation, vanishing and exploding gradients, convexity and Jensen’s inequality, numerical stability with log-sum-exp and finite difference gradient checks.',
    summary='Taylor polynomials and radius of convergence, Newton’s method and quadratic convergence, the Hessian and quasi Newton methods, gradients of aᵀx, xᵀAx and ‖Xw − y‖², forward mode with dual numbers and reverse mode with a tape, why backpropagation is reverse mode, vanishing and exploding gradients with initialisation, normalisation and residual connections, convex functions and Jensen’s inequality with KL divergence, overflow, underflow, cancellation, log-sum-exp and gradient checking.',
    keywords=['taylor series', 'maclaurin', 'newton method', 'quadratic convergence', 'hessian', 'matrix calculus', 'automatic differentiation', 'forward mode', 'reverse mode', 'dual numbers', 'backpropagation', 'vanishing gradient', 'exploding gradient', 'convex', 'jensen inequality', 'log sum exp', 'gradient checking', 'numerical stability'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
