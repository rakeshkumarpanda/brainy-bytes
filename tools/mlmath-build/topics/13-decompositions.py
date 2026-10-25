# Chapter 13: orthogonal vectors and orthonormal bases, Gram Schmidt and QR, quadratic forms and positive
# definite matrices, LU and Cholesky, least squares as a projection, matrix norms and the condition number,
# and tensors with broadcasting.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz, deep

K = Kit()

# ---------------------------------------------------------------- programs
K.code('orth_coords', py=r'''
def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


q1 = [0.6, 0.8]                           # an orthonormal basis, turned about 53 degrees
q2 = [-0.8, 0.6]
v = [2, 1]
print(f"q1.q1 = {f(dot(q1, q1))}, q2.q2 = {f(dot(q2, q2))}, q1.q2 = {f(dot(q1, q2))}")
c1 = dot(v, q1)                           # coordinates are just dot products
c2 = dot(v, q2)
print(f"coordinates: c1 = {f(c1)}, c2 = {f(c2)}")
back = [c1 * a + c2 * b for a, b in zip(q1, q2)]
print(f"rebuilt v = [{f(back[0])}, {f(back[1])}]")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);

const q1 = [0.6, 0.8];                    // an orthonormal basis, turned about 53 degrees
const q2 = [-0.8, 0.6];
const v = [2, 1];
console.log(`q1.q1 = ${f(dot(q1, q1))}, q2.q2 = ${f(dot(q2, q2))}, q1.q2 = ${f(dot(q1, q2))}`);
const c1 = dot(v, q1);                    // coordinates are just dot products
const c2 = dot(v, q2);
console.log(`coordinates: c1 = ${f(c1)}, c2 = ${f(c2)}`);
const back = q1.map((a, i) => c1 * a + c2 * q2[i]);
console.log(`rebuilt v = [${f(back[0])}, ${f(back[1])}]`);
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);
const dot = (a: number[], b: number[]): number => a.reduce((s, x, i) => s + x * b[i], 0);

const q1: number[] = [0.6, 0.8];          // an orthonormal basis, turned about 53 degrees
const q2: number[] = [-0.8, 0.6];
const v: number[] = [2, 1];
console.log(`q1.q1 = ${f(dot(q1, q1))}, q2.q2 = ${f(dot(q2, q2))}, q1.q2 = ${f(dot(q1, q2))}`);
const c1: number = dot(v, q1);            // coordinates are just dot products
const c2: number = dot(v, q2);
console.log(`coordinates: c1 = ${f(c1)}, c2 = ${f(c2)}`);
const back: number[] = q1.map((a, i) => c1 * a + c2 * q2[i]);
console.log(`rebuilt v = [${f(back[0])}, ${f(back[1])}]`);
''', java=r'''
public class OrthCoords {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    static double dot(double[] a, double[] b) {
        double s = 0;
        for (int i = 0; i < a.length; i++) s += a[i] * b[i];
        return s;
    }

    public static void main(String[] args) {
        double[] q1 = {0.6, 0.8};             // an orthonormal basis, turned about 53 degrees
        double[] q2 = {-0.8, 0.6};
        double[] v = {2, 1};
        System.out.println("q1.q1 = " + f(dot(q1, q1)) + ", q2.q2 = " + f(dot(q2, q2)) + ", q1.q2 = " + f(dot(q1, q2)));
        double c1 = dot(v, q1);               // coordinates are just dot products
        double c2 = dot(v, q2);
        System.out.println("coordinates: c1 = " + f(c1) + ", c2 = " + f(c2));
        double[] back = {c1 * q1[0] + c2 * q2[0], c1 * q1[1] + c2 * q2[1]};
        System.out.println("rebuilt v = [" + f(back[0]) + ", " + f(back[1]) + "]");
    }
}
''')

K.code('gram_schmidt', py=r'''
import math


def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


cols = [[1, 1, 0], [1, 0, 1], [0, 1, 1]]  # the columns a1, a2, a3 of A
Q = []
R = [[0.0] * 3 for _ in range(3)]
for j, a in enumerate(cols):
    u = list(a)
    for i, q in enumerate(Q):
        R[i][j] = dot(q, a)              # how much of a lies along q
        u = [ui - R[i][j] * qi for ui, qi in zip(u, q)]
    R[j][j] = math.sqrt(dot(u, u))       # length of what is left
    Q.append([ui / R[j][j] for ui in u])
    print(f"q{j + 1} = [{', '.join(f(x) for x in Q[j])}]")
for i in range(3):
    print(f"R row {i + 1}: [{', '.join(f(x) for x in R[i])}]")
print(f"q1.q2 = {f(dot(Q[0], Q[1]))}, q1.q3 = {f(dot(Q[0], Q[2]))}, q2.q3 = {f(dot(Q[1], Q[2]))}")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);

const cols = [[1, 1, 0], [1, 0, 1], [0, 1, 1]];   // the columns a1, a2, a3 of A
const Q = [];
const R = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
cols.forEach((a, j) => {
  let u = a.slice();
  Q.forEach((q, i) => {
    R[i][j] = dot(q, a);                  // how much of a lies along q
    u = u.map((ui, k) => ui - R[i][j] * q[k]);
  });
  R[j][j] = Math.sqrt(dot(u, u));         // length of what is left
  Q.push(u.map(ui => ui / R[j][j]));
  console.log(`q${j + 1} = [${Q[j].map(f).join(', ')}]`);
});
for (let i = 0; i < 3; i++) {
  console.log(`R row ${i + 1}: [${R[i].map(f).join(', ')}]`);
}
console.log(`q1.q2 = ${f(dot(Q[0], Q[1]))}, q1.q3 = ${f(dot(Q[0], Q[2]))}, q2.q3 = ${f(dot(Q[1], Q[2]))}`);
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);
const dot = (a: number[], b: number[]): number => a.reduce((s, x, i) => s + x * b[i], 0);

const cols: number[][] = [[1, 1, 0], [1, 0, 1], [0, 1, 1]];   // the columns a1, a2, a3 of A
const Q: number[][] = [];
const R: number[][] = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
cols.forEach((a, j) => {
  let u: number[] = a.slice();
  Q.forEach((q, i) => {
    R[i][j] = dot(q, a);                  // how much of a lies along q
    u = u.map((ui, k) => ui - R[i][j] * q[k]);
  });
  R[j][j] = Math.sqrt(dot(u, u));         // length of what is left
  Q.push(u.map(ui => ui / R[j][j]));
  console.log(`q${j + 1} = [${Q[j].map(f).join(', ')}]`);
});
for (let i = 0; i < 3; i++) {
  console.log(`R row ${i + 1}: [${R[i].map(f).join(', ')}]`);
}
console.log(`q1.q2 = ${f(dot(Q[0], Q[1]))}, q1.q3 = ${f(dot(Q[0], Q[2]))}, q2.q3 = ${f(dot(Q[1], Q[2]))}`);
''', java=r'''
public class GramSchmidt {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    static double dot(double[] a, double[] b) {
        double s = 0;
        for (int i = 0; i < a.length; i++) s += a[i] * b[i];
        return s;
    }

    static String row(double[] r) {
        return "[" + f(r[0]) + ", " + f(r[1]) + ", " + f(r[2]) + "]";
    }

    public static void main(String[] args) {
        double[][] cols = {{1, 1, 0}, {1, 0, 1}, {0, 1, 1}};   // the columns a1, a2, a3 of A
        double[][] Q = new double[3][];
        double[][] R = new double[3][3];
        for (int j = 0; j < 3; j++) {
            double[] u = cols[j].clone();
            for (int i = 0; i < j; i++) {
                R[i][j] = dot(Q[i], cols[j]);     // how much of a lies along q
                for (int k = 0; k < 3; k++) u[k] -= R[i][j] * Q[i][k];
            }
            R[j][j] = Math.sqrt(dot(u, u));       // length of what is left
            Q[j] = new double[3];
            for (int k = 0; k < 3; k++) Q[j][k] = u[k] / R[j][j];
            System.out.println("q" + (j + 1) + " = " + row(Q[j]));
        }
        for (int i = 0; i < 3; i++) System.out.println("R row " + (i + 1) + ": " + row(R[i]));
        System.out.println("q1.q2 = " + f(dot(Q[0], Q[1])) + ", q1.q3 = " + f(dot(Q[0], Q[2])) + ", q2.q3 = " + f(dot(Q[1], Q[2])));
    }
}
''')

K.code('quad_form', py=r'''
def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


def qf(A, x):                             # the quadratic form x^T A x for a 2 x 2 matrix
    return A[0][0] * x[0] * x[0] + 2 * A[0][1] * x[0] * x[1] + A[1][1] * x[1] * x[1]


def kind(A):
    m1 = A[0][0]                          # first leading minor
    m2 = A[0][0] * A[1][1] - A[0][1] * A[1][0]   # second leading minor, the determinant
    if m1 > 0 and m2 > 0:
        return "positive definite (a bowl)"
    if m2 < 0:
        return "indefinite (a saddle)"
    return "not positive definite"


for name, A in [("A", [[2, 1], [1, 3]]), ("B", [[1, 2], [2, 1]])]:
    vals = [qf(A, x) for x in ([1, 0], [0, 1], [1, -1], [1, 1])]
    print(f"{name}: x^T {name} x at [1,0], [0,1], [1,-1], [1,1] = {', '.join(f(v) for v in vals)}")
    print(f"   {kind(A)}")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

function qf(A, x) {                       // the quadratic form x^T A x for a 2 x 2 matrix
  return A[0][0] * x[0] * x[0] + 2 * A[0][1] * x[0] * x[1] + A[1][1] * x[1] * x[1];
}

function kind(A) {
  const m1 = A[0][0];                     // first leading minor
  const m2 = A[0][0] * A[1][1] - A[0][1] * A[1][0];   // second leading minor, the determinant
  if (m1 > 0 && m2 > 0) return "positive definite (a bowl)";
  if (m2 < 0) return "indefinite (a saddle)";
  return "not positive definite";
}

for (const [name, A] of [["A", [[2, 1], [1, 3]]], ["B", [[1, 2], [2, 1]]]]) {
  const vals = [[1, 0], [0, 1], [1, -1], [1, 1]].map(x => qf(A, x));
  console.log(`${name}: x^T ${name} x at [1,0], [0,1], [1,-1], [1,1] = ${vals.map(f).join(', ')}`);
  console.log(`   ${kind(A)}`);
}
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

function qf(A: number[][], x: number[]): number {   // the quadratic form x^T A x for a 2 x 2 matrix
  return A[0][0] * x[0] * x[0] + 2 * A[0][1] * x[0] * x[1] + A[1][1] * x[1] * x[1];
}

function kind(A: number[][]): string {
  const m1: number = A[0][0];             // first leading minor
  const m2: number = A[0][0] * A[1][1] - A[0][1] * A[1][0];   // second leading minor, the determinant
  if (m1 > 0 && m2 > 0) return "positive definite (a bowl)";
  if (m2 < 0) return "indefinite (a saddle)";
  return "not positive definite";
}

const cases: [string, number[][]][] = [["A", [[2, 1], [1, 3]]], ["B", [[1, 2], [2, 1]]]];
for (const [name, A] of cases) {
  const vals: number[] = [[1, 0], [0, 1], [1, -1], [1, 1]].map(x => qf(A, x));
  console.log(`${name}: x^T ${name} x at [1,0], [0,1], [1,-1], [1,1] = ${vals.map(f).join(', ')}`);
  console.log(`   ${kind(A)}`);
}
''', java=r'''
public class QuadForm {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    static double qf(double[][] A, double[] x) {   // the quadratic form x^T A x for a 2 x 2 matrix
        return A[0][0] * x[0] * x[0] + 2 * A[0][1] * x[0] * x[1] + A[1][1] * x[1] * x[1];
    }

    static String kind(double[][] A) {
        double m1 = A[0][0];                  // first leading minor
        double m2 = A[0][0] * A[1][1] - A[0][1] * A[1][0];   // second leading minor, the determinant
        if (m1 > 0 && m2 > 0) return "positive definite (a bowl)";
        if (m2 < 0) return "indefinite (a saddle)";
        return "not positive definite";
    }

    public static void main(String[] args) {
        String[] names = {"A", "B"};
        double[][][] mats = {{{2, 1}, {1, 3}}, {{1, 2}, {2, 1}}};
        double[][] xs = {{1, 0}, {0, 1}, {1, -1}, {1, 1}};
        for (int m = 0; m < 2; m++) {
            StringBuilder sb = new StringBuilder();
            for (int k = 0; k < xs.length; k++) sb.append(k > 0 ? ", " : "").append(f(qf(mats[m], xs[k])));
            System.out.println(names[m] + ": x^T " + names[m] + " x at [1,0], [0,1], [1,-1], [1,1] = " + sb);
            System.out.println("   " + kind(mats[m]));
        }
    }
}
''')

K.code('cholesky', py=r'''
import math


def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


A = [[4, 2, 2], [2, 5, 3], [2, 3, 6]]
b = [8, 10, 11]
n = 3
L = [[0.0] * n for _ in range(n)]
for i in range(n):
    for j in range(i + 1):
        s = sum(L[i][k] * L[j][k] for k in range(j))
        if i == j:
            L[i][j] = math.sqrt(A[i][i] - s)   # diagonal: square root of what is left
        else:
            L[i][j] = (A[i][j] - s) / L[j][j]
for r in L:
    print(f"L row: [{', '.join(f(x) for x in r)}]")
y = [0.0] * n                             # forward: solve L y = b, top to bottom
for i in range(n):
    y[i] = (b[i] - sum(L[i][k] * y[k] for k in range(i))) / L[i][i]
x = [0.0] * n                             # backward: solve L^T x = y, bottom to top
for i in range(n - 1, -1, -1):
    x[i] = (y[i] - sum(L[k][i] * x[k] for k in range(i + 1, n))) / L[i][i]
print(f"y = [{', '.join(f(v) for v in y)}]")
print(f"x = [{', '.join(f(v) for v in x)}]")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

const A = [[4, 2, 2], [2, 5, 3], [2, 3, 6]];
const b = [8, 10, 11];
const n = 3;
const L = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
for (let i = 0; i < n; i++) {
  for (let j = 0; j <= i; j++) {
    let s = 0;
    for (let k = 0; k < j; k++) s += L[i][k] * L[j][k];
    if (i === j) {
      L[i][j] = Math.sqrt(A[i][i] - s);   // diagonal: square root of what is left
    } else {
      L[i][j] = (A[i][j] - s) / L[j][j];
    }
  }
}
for (const r of L) console.log(`L row: [${r.map(f).join(', ')}]`);
const y = [0, 0, 0];                      // forward: solve L y = b, top to bottom
for (let i = 0; i < n; i++) {
  let s = 0;
  for (let k = 0; k < i; k++) s += L[i][k] * y[k];
  y[i] = (b[i] - s) / L[i][i];
}
const x = [0, 0, 0];                      // backward: solve L^T x = y, bottom to top
for (let i = n - 1; i >= 0; i--) {
  let s = 0;
  for (let k = i + 1; k < n; k++) s += L[k][i] * x[k];
  x[i] = (y[i] - s) / L[i][i];
}
console.log(`y = [${y.map(f).join(', ')}]`);
console.log(`x = [${x.map(f).join(', ')}]`);
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

const A: number[][] = [[4, 2, 2], [2, 5, 3], [2, 3, 6]];
const b: number[] = [8, 10, 11];
const n: number = 3;
const L: number[][] = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
for (let i = 0; i < n; i++) {
  for (let j = 0; j <= i; j++) {
    let s = 0;
    for (let k = 0; k < j; k++) s += L[i][k] * L[j][k];
    if (i === j) {
      L[i][j] = Math.sqrt(A[i][i] - s);   // diagonal: square root of what is left
    } else {
      L[i][j] = (A[i][j] - s) / L[j][j];
    }
  }
}
for (const r of L) console.log(`L row: [${r.map(f).join(', ')}]`);
const y: number[] = [0, 0, 0];            // forward: solve L y = b, top to bottom
for (let i = 0; i < n; i++) {
  let s = 0;
  for (let k = 0; k < i; k++) s += L[i][k] * y[k];
  y[i] = (b[i] - s) / L[i][i];
}
const x: number[] = [0, 0, 0];            // backward: solve L^T x = y, bottom to top
for (let i = n - 1; i >= 0; i--) {
  let s = 0;
  for (let k = i + 1; k < n; k++) s += L[k][i] * x[k];
  x[i] = (y[i] - s) / L[i][i];
}
console.log(`y = [${y.map(f).join(', ')}]`);
console.log(`x = [${x.map(f).join(', ')}]`);
''', java=r'''
public class Cholesky {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    static String row(double[] r) {
        return "[" + f(r[0]) + ", " + f(r[1]) + ", " + f(r[2]) + "]";
    }

    public static void main(String[] args) {
        double[][] A = {{4, 2, 2}, {2, 5, 3}, {2, 3, 6}};
        double[] b = {8, 10, 11};
        int n = 3;
        double[][] L = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j <= i; j++) {
                double s = 0;
                for (int k = 0; k < j; k++) s += L[i][k] * L[j][k];
                if (i == j) {
                    L[i][j] = Math.sqrt(A[i][i] - s);   // diagonal: square root of what is left
                } else {
                    L[i][j] = (A[i][j] - s) / L[j][j];
                }
            }
        }
        for (double[] r : L) System.out.println("L row: " + row(r));
        double[] y = new double[n];               // forward: solve L y = b, top to bottom
        for (int i = 0; i < n; i++) {
            double s = 0;
            for (int k = 0; k < i; k++) s += L[i][k] * y[k];
            y[i] = (b[i] - s) / L[i][i];
        }
        double[] x = new double[n];               // backward: solve L^T x = y, bottom to top
        for (int i = n - 1; i >= 0; i--) {
            double s = 0;
            for (int k = i + 1; k < n; k++) s += L[k][i] * x[k];
            x[i] = (y[i] - s) / L[i][i];
        }
        System.out.println("y = " + row(y));
        System.out.println("x = " + row(x));
    }
}
''')

K.code('normal_eq', py=r'''
def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


xs = [1, 2, 3, 4]
ys = [2, 3, 5, 6]
n = len(xs)
# normal equations for y = a + b x:  [n, Sx; Sx, Sxx] [a, b] = [Sy, Sxy]
Sx, Sy = sum(xs), sum(ys)
Sxx = sum(x * x for x in xs)
Sxy = sum(x * y for x, y in zip(xs, ys))
det = n * Sxx - Sx * Sx
a = (Sy * Sxx - Sx * Sxy) / det
b = (n * Sxy - Sx * Sy) / det
print(f"best line: y = {f(a)} + {f(b)} x")
r = [y - (a + b * x) for x, y in zip(xs, ys)]
print(f"residuals = [{', '.join(f(v) for v in r)}]")
print(f"sum of squared residuals = {f(sum(v * v for v in r))}")
print(f"X^T r = [{f(sum(r))}, {f(sum(x * v for x, v in zip(xs, r)))}]  (the residual is perpendicular to both columns)")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

const xs = [1, 2, 3, 4];
const ys = [2, 3, 5, 6];
const n = xs.length;
// normal equations for y = a + b x:  [n, Sx; Sx, Sxx] [a, b] = [Sy, Sxy]
const Sx = xs.reduce((s, x) => s + x, 0), Sy = ys.reduce((s, y) => s + y, 0);
const Sxx = xs.reduce((s, x) => s + x * x, 0);
const Sxy = xs.reduce((s, x, i) => s + x * ys[i], 0);
const det = n * Sxx - Sx * Sx;
const a = (Sy * Sxx - Sx * Sxy) / det;
const b = (n * Sxy - Sx * Sy) / det;
console.log(`best line: y = ${f(a)} + ${f(b)} x`);
const r = xs.map((x, i) => ys[i] - (a + b * x));
console.log(`residuals = [${r.map(f).join(', ')}]`);
console.log(`sum of squared residuals = ${f(r.reduce((s, v) => s + v * v, 0))}`);
console.log(`X^T r = [${f(r.reduce((s, v) => s + v, 0))}, ${f(r.reduce((s, v, i) => s + xs[i] * v, 0))}]  (the residual is perpendicular to both columns)`);
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

const xs: number[] = [1, 2, 3, 4];
const ys: number[] = [2, 3, 5, 6];
const n: number = xs.length;
// normal equations for y = a + b x:  [n, Sx; Sx, Sxx] [a, b] = [Sy, Sxy]
const Sx: number = xs.reduce((s, x) => s + x, 0), Sy: number = ys.reduce((s, y) => s + y, 0);
const Sxx: number = xs.reduce((s, x) => s + x * x, 0);
const Sxy: number = xs.reduce((s, x, i) => s + x * ys[i], 0);
const det: number = n * Sxx - Sx * Sx;
const a: number = (Sy * Sxx - Sx * Sxy) / det;
const b: number = (n * Sxy - Sx * Sy) / det;
console.log(`best line: y = ${f(a)} + ${f(b)} x`);
const r: number[] = xs.map((x, i) => ys[i] - (a + b * x));
console.log(`residuals = [${r.map(f).join(', ')}]`);
console.log(`sum of squared residuals = ${f(r.reduce((s, v) => s + v * v, 0))}`);
console.log(`X^T r = [${f(r.reduce((s, v) => s + v, 0))}, ${f(r.reduce((s, v, i) => s + xs[i] * v, 0))}]  (the residual is perpendicular to both columns)`);
''', java=r'''
public class NormalEq {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    public static void main(String[] args) {
        double[] xs = {1, 2, 3, 4};
        double[] ys = {2, 3, 5, 6};
        int n = xs.length;
        // normal equations for y = a + b x:  [n, Sx; Sx, Sxx] [a, b] = [Sy, Sxy]
        double Sx = 0, Sy = 0, Sxx = 0, Sxy = 0;
        for (int i = 0; i < n; i++) {
            Sx += xs[i];
            Sy += ys[i];
            Sxx += xs[i] * xs[i];
            Sxy += xs[i] * ys[i];
        }
        double det = n * Sxx - Sx * Sx;
        double a = (Sy * Sxx - Sx * Sxy) / det;
        double b = (n * Sxy - Sx * Sy) / det;
        System.out.println("best line: y = " + f(a) + " + " + f(b) + " x");
        double[] r = new double[n];
        double sse = 0, s0 = 0, s1 = 0;
        for (int i = 0; i < n; i++) {
            r[i] = ys[i] - (a + b * xs[i]);
            sse += r[i] * r[i];
            s0 += r[i];
            s1 += xs[i] * r[i];
        }
        System.out.println("residuals = [" + f(r[0]) + ", " + f(r[1]) + ", " + f(r[2]) + ", " + f(r[3]) + "]");
        System.out.println("sum of squared residuals = " + f(sse));
        System.out.println("X^T r = [" + f(s0) + ", " + f(s1) + "]  (the residual is perpendicular to both columns)");
    }
}
''')

K.code('cond', py=r'''
import math


def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


def solve(A, b):                          # Cramer rule for a 2 x 2 system
    d = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    return [(b[0] * A[1][1] - A[0][1] * b[1]) / d, (A[0][0] * b[1] - b[0] * A[1][0]) / d]


A = [[1, 1], [1, 1.001]]                  # two nearly identical rows
fro = math.sqrt(sum(v * v for row in A for v in row))
tr = A[0][0] + A[1][1]
det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
gap = math.sqrt(tr * tr - 4 * det)
big, small = (tr + gap) / 2, (tr - gap) / 2   # symmetric, so singular values = eigenvalues here
print(f"Frobenius norm = {f(fro)}, trace = {f(tr)}")
print(f"largest = {f(big)}, smallest = {f(small)}, condition number = {big / small:.0f}")
x1 = solve(A, [2, 2.001])
x2 = solve(A, [2, 2.002])                 # change one number by 0.001
print(f"b = [2, 2.001] gives x = [{f(x1[0])}, {f(x1[1])}]")
print(f"b = [2, 2.002] gives x = [{f(x2[0])}, {f(x2[1])}]")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

function solve(A, b) {                    // Cramer rule for a 2 x 2 system
  const d = A[0][0] * A[1][1] - A[0][1] * A[1][0];
  return [(b[0] * A[1][1] - A[0][1] * b[1]) / d, (A[0][0] * b[1] - b[0] * A[1][0]) / d];
}

const A = [[1, 1], [1, 1.001]];           // two nearly identical rows
const fro = Math.sqrt(A.flat().reduce((s, v) => s + v * v, 0));
const tr = A[0][0] + A[1][1];
const det = A[0][0] * A[1][1] - A[0][1] * A[1][0];
const gap = Math.sqrt(tr * tr - 4 * det);
const big = (tr + gap) / 2, small = (tr - gap) / 2;   // symmetric, so singular values = eigenvalues here
console.log(`Frobenius norm = ${f(fro)}, trace = ${f(tr)}`);
console.log(`largest = ${f(big)}, smallest = ${f(small)}, condition number = ${(big / small).toFixed(0)}`);
const x1 = solve(A, [2, 2.001]);
const x2 = solve(A, [2, 2.002]);          // change one number by 0.001
console.log(`b = [2, 2.001] gives x = [${f(x1[0])}, ${f(x1[1])}]`);
console.log(`b = [2, 2.002] gives x = [${f(x2[0])}, ${f(x2[1])}]`);
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

function solve(A: number[][], b: number[]): number[] {   // Cramer rule for a 2 x 2 system
  const d: number = A[0][0] * A[1][1] - A[0][1] * A[1][0];
  return [(b[0] * A[1][1] - A[0][1] * b[1]) / d, (A[0][0] * b[1] - b[0] * A[1][0]) / d];
}

const A: number[][] = [[1, 1], [1, 1.001]];   // two nearly identical rows
const fro: number = Math.sqrt(A.flat().reduce((s, v) => s + v * v, 0));
const tr: number = A[0][0] + A[1][1];
const det: number = A[0][0] * A[1][1] - A[0][1] * A[1][0];
const gap: number = Math.sqrt(tr * tr - 4 * det);
const big: number = (tr + gap) / 2, small: number = (tr - gap) / 2;   // symmetric, so singular values = eigenvalues here
console.log(`Frobenius norm = ${f(fro)}, trace = ${f(tr)}`);
console.log(`largest = ${f(big)}, smallest = ${f(small)}, condition number = ${(big / small).toFixed(0)}`);
const x1: number[] = solve(A, [2, 2.001]);
const x2: number[] = solve(A, [2, 2.002]);   // change one number by 0.001
console.log(`b = [2, 2.001] gives x = [${f(x1[0])}, ${f(x1[1])}]`);
console.log(`b = [2, 2.002] gives x = [${f(x2[0])}, ${f(x2[1])}]`);
''', java=r'''
public class Cond {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    static double[] solve(double[][] A, double[] b) {   // Cramer rule for a 2 x 2 system
        double d = A[0][0] * A[1][1] - A[0][1] * A[1][0];
        return new double[]{(b[0] * A[1][1] - A[0][1] * b[1]) / d, (A[0][0] * b[1] - b[0] * A[1][0]) / d};
    }

    public static void main(String[] args) {
        double[][] A = {{1, 1}, {1, 1.001}};      // two nearly identical rows
        double fro = Math.sqrt(1 + 1 + 1 + 1.001 * 1.001);
        double tr = A[0][0] + A[1][1];
        double det = A[0][0] * A[1][1] - A[0][1] * A[1][0];
        double gap = Math.sqrt(tr * tr - 4 * det);
        double big = (tr + gap) / 2, small = (tr - gap) / 2;   // symmetric, so singular values = eigenvalues here
        System.out.println("Frobenius norm = " + f(fro) + ", trace = " + f(tr));
        System.out.println("largest = " + f(big) + ", smallest = " + f(small) + ", condition number = " + String.format("%.0f", big / small));
        double[] x1 = solve(A, new double[]{2, 2.001});
        double[] x2 = solve(A, new double[]{2, 2.002});   // change one number by 0.001
        System.out.println("b = [2, 2.001] gives x = [" + f(x1[0]) + ", " + f(x1[1]) + "]");
        System.out.println("b = [2, 2.002] gives x = [" + f(x2[0]) + ", " + f(x2[1]) + "]");
    }
}
''')

K.code('broadcast', py=r'''
def broadcast(a, b):
    out = []
    for i in range(1, max(len(a), len(b)) + 1):   # compare sizes from the right
        x = a[-i] if i <= len(a) else 1
        y = b[-i] if i <= len(b) else 1
        if x != y and x != 1 and y != 1:
            return None                   # sizes clash
        out.insert(0, max(x, y))
    return out


def show(s):
    return "(" + ", ".join(str(v) for v in s) + ")"


pairs = [([3, 1], [1, 4]), ([2, 3], [3]), ([4, 3], [4]), ([32, 10], [10]), ([8, 1, 6, 1], [7, 1, 5])]
for a, b in pairs:
    r = broadcast(a, b)
    print(f"{show(a)} with {show(b)} -> {show(r) if r else 'error: sizes do not match'}")
''', js=r'''
function broadcast(a, b) {
  const out = [];
  for (let i = 1; i <= Math.max(a.length, b.length); i++) {   // compare sizes from the right
    const x = i <= a.length ? a[a.length - i] : 1;
    const y = i <= b.length ? b[b.length - i] : 1;
    if (x !== y && x !== 1 && y !== 1) return null;           // sizes clash
    out.unshift(Math.max(x, y));
  }
  return out;
}

const show = s => "(" + s.join(", ") + ")";

const pairs = [[[3, 1], [1, 4]], [[2, 3], [3]], [[4, 3], [4]], [[32, 10], [10]], [[8, 1, 6, 1], [7, 1, 5]]];
for (const [a, b] of pairs) {
  const r = broadcast(a, b);
  console.log(`${show(a)} with ${show(b)} -> ${r ? show(r) : 'error: sizes do not match'}`);
}
''', ts=r'''
function broadcast(a: number[], b: number[]): number[] | null {
  const out: number[] = [];
  for (let i = 1; i <= Math.max(a.length, b.length); i++) {   // compare sizes from the right
    const x: number = i <= a.length ? a[a.length - i] : 1;
    const y: number = i <= b.length ? b[b.length - i] : 1;
    if (x !== y && x !== 1 && y !== 1) return null;           // sizes clash
    out.unshift(Math.max(x, y));
  }
  return out;
}

const show = (s: number[]): string => "(" + s.join(", ") + ")";

const pairs: [number[], number[]][] = [[[3, 1], [1, 4]], [[2, 3], [3]], [[4, 3], [4]], [[32, 10], [10]], [[8, 1, 6, 1], [7, 1, 5]]];
for (const [a, b] of pairs) {
  const r = broadcast(a, b);
  console.log(`${show(a)} with ${show(b)} -> ${r ? show(r) : 'error: sizes do not match'}`);
}
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class Broadcast {
    static List<Integer> broadcast(int[] a, int[] b) {
        List<Integer> out = new ArrayList<>();
        for (int i = 1; i <= Math.max(a.length, b.length); i++) {   // compare sizes from the right
            int x = i <= a.length ? a[a.length - i] : 1;
            int y = i <= b.length ? b[b.length - i] : 1;
            if (x != y && x != 1 && y != 1) return null;           // sizes clash
            out.add(0, Math.max(x, y));
        }
        return out;
    }

    static String show(int[] s) {
        StringBuilder sb = new StringBuilder("(");
        for (int i = 0; i < s.length; i++) sb.append(i > 0 ? ", " : "").append(s[i]);
        return sb.append(")").toString();
    }

    static String show(List<Integer> s) {
        int[] a = new int[s.size()];
        for (int i = 0; i < a.length; i++) a[i] = s.get(i);
        return show(a);
    }

    public static void main(String[] args) {
        int[][][] pairs = {{{3, 1}, {1, 4}}, {{2, 3}, {3}}, {{4, 3}, {4}}, {{32, 10}, {10}}, {{8, 1, 6, 1}, {7, 1, 5}}};
        for (int[][] p : pairs) {
            List<Integer> r = broadcast(p[0], p[1]);
            System.out.println(show(p[0]) + " with " + show(p[1]) + " -> " + (r != null ? show(r) : "error: sizes do not match"));
        }
    }
}
''')

# ---- practice programs
K.code('p_orth_check', py=r'''
import math


def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def check(name, vs):
    print(f"{name}:")
    ok = True
    for i in range(len(vs)):
        for j in range(i, len(vs)):
            want = 1 if i == j else 0     # length 1 with itself, 0 with the others
            got = dot(vs[i], vs[j])
            if abs(got - want) > 1e-9:
                ok = False
                print(f"   v{i + 1}.v{j + 1} = {f(got)}, should be {want}")
    print(f"   result: {'orthonormal' if ok else 'not orthonormal'}")


s = 1 / math.sqrt(2)
check("set 1", [[s, s, 0], [-s, s, 0], [0, 0, 1]])
check("set 2", [[1, 0, 0], [1, 1, 0], [0, 0, 2]])
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);

function check(name, vs) {
  console.log(`${name}:`);
  let ok = true;
  for (let i = 0; i < vs.length; i++) {
    for (let j = i; j < vs.length; j++) {
      const want = i === j ? 1 : 0;      // length 1 with itself, 0 with the others
      const got = dot(vs[i], vs[j]);
      if (Math.abs(got - want) > 1e-9) {
        ok = false;
        console.log(`   v${i + 1}.v${j + 1} = ${f(got)}, should be ${want}`);
      }
    }
  }
  console.log(`   result: ${ok ? 'orthonormal' : 'not orthonormal'}`);
}

const s = 1 / Math.sqrt(2);
check("set 1", [[s, s, 0], [-s, s, 0], [0, 0, 1]]);
check("set 2", [[1, 0, 0], [1, 1, 0], [0, 0, 2]]);
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);
const dot = (a: number[], b: number[]): number => a.reduce((s, x, i) => s + x * b[i], 0);

function check(name: string, vs: number[][]): void {
  console.log(`${name}:`);
  let ok = true;
  for (let i = 0; i < vs.length; i++) {
    for (let j = i; j < vs.length; j++) {
      const want: number = i === j ? 1 : 0;   // length 1 with itself, 0 with the others
      const got: number = dot(vs[i], vs[j]);
      if (Math.abs(got - want) > 1e-9) {
        ok = false;
        console.log(`   v${i + 1}.v${j + 1} = ${f(got)}, should be ${want}`);
      }
    }
  }
  console.log(`   result: ${ok ? 'orthonormal' : 'not orthonormal'}`);
}

const s: number = 1 / Math.sqrt(2);
check("set 1", [[s, s, 0], [-s, s, 0], [0, 0, 1]]);
check("set 2", [[1, 0, 0], [1, 1, 0], [0, 0, 2]]);
''', java=r'''
public class PracticeOrth {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    static double dot(double[] a, double[] b) {
        double s = 0;
        for (int i = 0; i < a.length; i++) s += a[i] * b[i];
        return s;
    }

    static void check(String name, double[][] vs) {
        System.out.println(name + ":");
        boolean ok = true;
        for (int i = 0; i < vs.length; i++) {
            for (int j = i; j < vs.length; j++) {
                int want = i == j ? 1 : 0;        // length 1 with itself, 0 with the others
                double got = dot(vs[i], vs[j]);
                if (Math.abs(got - want) > 1e-9) {
                    ok = false;
                    System.out.println("   v" + (i + 1) + ".v" + (j + 1) + " = " + f(got) + ", should be " + want);
                }
            }
        }
        System.out.println("   result: " + (ok ? "orthonormal" : "not orthonormal"));
    }

    public static void main(String[] args) {
        double s = 1 / Math.sqrt(2);
        check("set 1", new double[][]{{s, s, 0}, {-s, s, 0}, {0, 0, 1}});
        check("set 2", new double[][]{{1, 0, 0}, {1, 1, 0}, {0, 0, 2}});
    }
}
''')

K.code('p_qr_line', py=r'''
import math


def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


xs = [0, 1, 2]
ys = [1, 3, 4]
c1 = [1, 1, 1]                            # column of ones for the intercept
c2 = list(xs)                             # column of inputs
r11 = math.sqrt(dot(c1, c1))
q1 = [v / r11 for v in c1]
r12 = dot(q1, c2)
u = [a - r12 * b for a, b in zip(c2, q1)]
r22 = math.sqrt(dot(u, u))
q2 = [v / r22 for v in u]
z1, z2 = dot(q1, ys), dot(q2, ys)         # Q^T y
slope = z2 / r22                          # back substitution on R beta = Q^T y
icpt = (z1 - r12 * slope) / r11
print(f"R = [[{f(r11)}, {f(r12)}], [0, {f(r22)}]]")
print(f"Q^T y = [{f(z1)}, {f(z2)}]")
print(f"intercept = {f(icpt)}, slope = {f(slope)}")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);

const xs = [0, 1, 2];
const ys = [1, 3, 4];
const c1 = [1, 1, 1];                     // column of ones for the intercept
const c2 = xs.slice();                    // column of inputs
const r11 = Math.sqrt(dot(c1, c1));
const q1 = c1.map(v => v / r11);
const r12 = dot(q1, c2);
const u = c2.map((a, i) => a - r12 * q1[i]);
const r22 = Math.sqrt(dot(u, u));
const q2 = u.map(v => v / r22);
const z1 = dot(q1, ys), z2 = dot(q2, ys); // Q^T y
const slope = z2 / r22;                   // back substitution on R beta = Q^T y
const icpt = (z1 - r12 * slope) / r11;
console.log(`R = [[${f(r11)}, ${f(r12)}], [0, ${f(r22)}]]`);
console.log(`Q^T y = [${f(z1)}, ${f(z2)}]`);
console.log(`intercept = ${f(icpt)}, slope = ${f(slope)}`);
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);
const dot = (a: number[], b: number[]): number => a.reduce((s, x, i) => s + x * b[i], 0);

const xs: number[] = [0, 1, 2];
const ys: number[] = [1, 3, 4];
const c1: number[] = [1, 1, 1];           // column of ones for the intercept
const c2: number[] = xs.slice();          // column of inputs
const r11: number = Math.sqrt(dot(c1, c1));
const q1: number[] = c1.map(v => v / r11);
const r12: number = dot(q1, c2);
const u: number[] = c2.map((a, i) => a - r12 * q1[i]);
const r22: number = Math.sqrt(dot(u, u));
const q2: number[] = u.map(v => v / r22);
const z1: number = dot(q1, ys), z2: number = dot(q2, ys);   // Q^T y
const slope: number = z2 / r22;           // back substitution on R beta = Q^T y
const icpt: number = (z1 - r12 * slope) / r11;
console.log(`R = [[${f(r11)}, ${f(r12)}], [0, ${f(r22)}]]`);
console.log(`Q^T y = [${f(z1)}, ${f(z2)}]`);
console.log(`intercept = ${f(icpt)}, slope = ${f(slope)}`);
''', java=r'''
public class PracticeQrLine {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    static double dot(double[] a, double[] b) {
        double s = 0;
        for (int i = 0; i < a.length; i++) s += a[i] * b[i];
        return s;
    }

    public static void main(String[] args) {
        double[] xs = {0, 1, 2};
        double[] ys = {1, 3, 4};
        double[] c1 = {1, 1, 1};                  // column of ones for the intercept
        double[] c2 = xs.clone();                 // column of inputs
        double r11 = Math.sqrt(dot(c1, c1));
        double[] q1 = new double[3], u = new double[3], q2 = new double[3];
        for (int i = 0; i < 3; i++) q1[i] = c1[i] / r11;
        double r12 = dot(q1, c2);
        for (int i = 0; i < 3; i++) u[i] = c2[i] - r12 * q1[i];
        double r22 = Math.sqrt(dot(u, u));
        for (int i = 0; i < 3; i++) q2[i] = u[i] / r22;
        double z1 = dot(q1, ys), z2 = dot(q2, ys);   // Q^T y
        double slope = z2 / r22;                  // back substitution on R beta = Q^T y
        double icpt = (z1 - r12 * slope) / r11;
        System.out.println("R = [[" + f(r11) + ", " + f(r12) + "], [0, " + f(r22) + "]]");
        System.out.println("Q^T y = [" + f(z1) + ", " + f(z2) + "]");
        System.out.println("intercept = " + f(icpt) + ", slope = " + f(slope));
    }
}
''')

K.code('p_posdef', py=r'''
def det(M):                               # determinant by expanding along the first row
    if len(M) == 1:
        return M[0][0]
    total = 0
    for j in range(len(M)):
        minor = [row[:j] + row[j + 1:] for row in M[1:]]
        total += (-1) ** j * M[0][j] * det(minor)
    return total


def test(name, A):
    minors = [det([row[:k] for row in A[:k]]) for k in range(1, len(A) + 1)]
    verdict = "positive definite" if all(m > 0 for m in minors) else "not positive definite"
    print(f"{name}: leading minors {minors} -> {verdict}")


test("A", [[2, -1, 0], [-1, 2, -1], [0, -1, 2]])
test("B", [[1, 2, 0], [2, 1, 0], [0, 0, 3]])
''', js=r'''
function det(M) {                         // determinant by expanding along the first row
  if (M.length === 1) return M[0][0];
  let total = 0;
  for (let j = 0; j < M.length; j++) {
    const minor = M.slice(1).map(row => row.filter((_, k) => k !== j));
    total += (j % 2 === 0 ? 1 : -1) * M[0][j] * det(minor);
  }
  return total;
}

function test(name, A) {
  const minors = [];
  for (let k = 1; k <= A.length; k++) minors.push(det(A.slice(0, k).map(row => row.slice(0, k))));
  const verdict = minors.every(m => m > 0) ? "positive definite" : "not positive definite";
  console.log(`${name}: leading minors [${minors.join(", ")}] -> ${verdict}`);
}

test("A", [[2, -1, 0], [-1, 2, -1], [0, -1, 2]]);
test("B", [[1, 2, 0], [2, 1, 0], [0, 0, 3]]);
''', ts=r'''
function det(M: number[][]): number {     // determinant by expanding along the first row
  if (M.length === 1) return M[0][0];
  let total = 0;
  for (let j = 0; j < M.length; j++) {
    const minor: number[][] = M.slice(1).map(row => row.filter((_, k) => k !== j));
    total += (j % 2 === 0 ? 1 : -1) * M[0][j] * det(minor);
  }
  return total;
}

function test(name: string, A: number[][]): void {
  const minors: number[] = [];
  for (let k = 1; k <= A.length; k++) minors.push(det(A.slice(0, k).map(row => row.slice(0, k))));
  const verdict: string = minors.every(m => m > 0) ? "positive definite" : "not positive definite";
  console.log(`${name}: leading minors [${minors.join(", ")}] -> ${verdict}`);
}

test("A", [[2, -1, 0], [-1, 2, -1], [0, -1, 2]]);
test("B", [[1, 2, 0], [2, 1, 0], [0, 0, 3]]);
''', java=r'''
public class PracticePosDef {
    static int det(int[][] M) {               // determinant by expanding along the first row
        int n = M.length;
        if (n == 1) return M[0][0];
        int total = 0;
        for (int j = 0; j < n; j++) {
            int[][] minor = new int[n - 1][n - 1];
            for (int r = 1; r < n; r++) {
                int c2 = 0;
                for (int c = 0; c < n; c++) if (c != j) minor[r - 1][c2++] = M[r][c];
            }
            total += (j % 2 == 0 ? 1 : -1) * M[0][j] * det(minor);
        }
        return total;
    }

    static void test(String name, int[][] A) {
        StringBuilder sb = new StringBuilder("[");
        boolean pd = true;
        for (int k = 1; k <= A.length; k++) {
            int[][] sub = new int[k][k];
            for (int r = 0; r < k; r++) for (int c = 0; c < k; c++) sub[r][c] = A[r][c];
            int m = det(sub);
            if (m <= 0) pd = false;
            sb.append(k > 1 ? ", " : "").append(m);
        }
        System.out.println(name + ": leading minors " + sb + "] -> " + (pd ? "positive definite" : "not positive definite"));
    }

    public static void main(String[] args) {
        test("A", new int[][]{{2, -1, 0}, {-1, 2, -1}, {0, -1, 2}});
        test("B", new int[][]{{1, 2, 0}, {2, 1, 0}, {0, 0, 3}});
    }
}
''')

K.code('p_chain_cost', py=r'''
def cost(m, n, p):                        # multiplications for (m x n) times (n x p)
    return m * n * p


A, B, C = (10, 100), (100, 5), (5, 50)
left = cost(A[0], A[1], B[1]) + cost(A[0], B[1], C[1])     # (AB)C
right = cost(B[0], B[1], C[1]) + cost(A[0], A[1], C[1])    # A(BC)
print(f"(AB)C needs {left} multiplications")
print(f"A(BC) needs {right} multiplications")
print(f"the better order is {right // left} times cheaper")
''', js=r'''
const cost = (m, n, p) => m * n * p;      // multiplications for (m x n) times (n x p)

const A = [10, 100], B = [100, 5], C = [5, 50];
const left = cost(A[0], A[1], B[1]) + cost(A[0], B[1], C[1]);     // (AB)C
const right = cost(B[0], B[1], C[1]) + cost(A[0], A[1], C[1]);    // A(BC)
console.log(`(AB)C needs ${left} multiplications`);
console.log(`A(BC) needs ${right} multiplications`);
console.log(`the better order is ${Math.floor(right / left)} times cheaper`);
''', ts=r'''
const cost = (m: number, n: number, p: number): number => m * n * p;   // multiplications for (m x n) times (n x p)

const A: number[] = [10, 100], B: number[] = [100, 5], C: number[] = [5, 50];
const left: number = cost(A[0], A[1], B[1]) + cost(A[0], B[1], C[1]);     // (AB)C
const right: number = cost(B[0], B[1], C[1]) + cost(A[0], A[1], C[1]);    // A(BC)
console.log(`(AB)C needs ${left} multiplications`);
console.log(`A(BC) needs ${right} multiplications`);
console.log(`the better order is ${Math.floor(right / left)} times cheaper`);
''', java=r'''
public class PracticeChainCost {
    static int cost(int m, int n, int p) {    // multiplications for (m x n) times (n x p)
        return m * n * p;
    }

    public static void main(String[] args) {
        int[] A = {10, 100}, B = {100, 5}, C = {5, 50};
        int left = cost(A[0], A[1], B[1]) + cost(A[0], B[1], C[1]);     // (AB)C
        int right = cost(B[0], B[1], C[1]) + cost(A[0], A[1], C[1]);    // A(BC)
        System.out.println("(AB)C needs " + left + " multiplications");
        System.out.println("A(BC) needs " + right + " multiplications");
        System.out.println("the better order is " + (right / left) + " times cheaper");
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('orth', '📐', 'Orthogonal vectors and orthonormal bases', f'''
<p>Two vectors are <b>orthogonal</b> when they meet at a right angle, which happens exactly when their dot product is 0 (Chapter 3). A set of vectors that are all orthogonal to each other <b>and</b> all have length 1 is called <b>orthonormal</b>. The usual x and y axes, [1, 0] and [0, 1], are the most familiar orthonormal pair, but any pair of perpendicular unit arrows works just as well, for example [0.6, 0.8] and [−0.8, 0.6].</p>
{fx('Orthonormal', 'qᵢ · qⱼ = 1 if i = j, and 0 if i ≠ j', 'Each vector has length 1, and different vectors are perpendicular. Put them as columns of a matrix Q and this says QᵀQ = I.')}
<p>Orthonormal bases are popular for one big reason: finding coordinates becomes trivial. In an ordinary basis you must solve a system of equations to find how much of each building block you need. In an orthonormal basis you just take dot products.</p>
{fxs(fx('Coordinates in an orthonormal basis', 'cᵢ = v · qᵢ', 'How much of qᵢ is in v. No equations to solve.'),
         fx('Rebuilding the vector', 'v = c₁q₁ + c₂q₂ + … + cₙqₙ', 'Add the pieces back together.'))}
{worked('Coordinates of v = [2, 1] in the basis q₁ = [0.6, 0.8], q₂ = [−0.8, 0.6]', [
        'Check the basis: <span class="eq">q₁ · q₁ = 0.36 + 0.64 = 1</span>, <span class="eq">q₂ · q₂ = 1</span>, <span class="eq">q₁ · q₂ = −0.48 + 0.48 = 0</span> ✓',
        'First coordinate: <span class="eq">c₁ = v · q₁ = 1.2 + 0.8 = 2</span>',
        'Second coordinate: <span class="eq">c₂ = v · q₂ = −1.6 + 0.6 = −1</span>',
        'Rebuild: <span class="eq">2 × [0.6, 0.8] − 1 × [−0.8, 0.6] = [1.2 + 0.8, 1.6 − 0.6] = [2, 1]</span> ✓'])}
{viz('orthbasis')}
{code('orth_coords', 'Coordinates by dot products, then rebuild the vector')}
<p>An <b>orthogonal matrix</b> Q has orthonormal columns. It only rotates or reflects, so it never changes lengths or angles: ‖Qx‖ = ‖x‖. Its inverse is simply its transpose, Q⁻¹ = Qᵀ, which is the cheapest inverse there is.</p>
{ml('PCA directions, the U and V of the SVD (Chapter 5) and the eigenvectors of any symmetric matrix are orthonormal. That is why projecting data onto principal components is just a matrix multiplication by Vᵀ. Some neural networks also start their weight matrices as random orthogonal matrices, so that signals keep their size as they pass through many layers.')}
{life('North and east on a map are an orthonormal pair. "3 km north and 4 km east" never mixes the two directions, so each number can be read on its own. A street grid that runs at a slant to north is just a rotated orthonormal basis.')}
''', kw=['orthogonal', 'orthonormal', 'orthonormal basis', 'orthogonal matrix', 'perpendicular', 'coordinates', 'Q transpose Q']),

    part('gram', '🧹', 'Gram Schmidt and the QR decomposition', f'''
<p>Most real bases are not orthonormal. The <b>Gram Schmidt process</b> turns any set of independent vectors into an orthonormal set that spans exactly the same space. The idea is the projection of Chapter 3, used again and again: take each new vector, remove the parts that point along the directions you already have, and stretch what is left to length 1.</p>
<ol>
<li>q₁ = a₁ ÷ ‖a₁‖. The first direction is just a₁, made unit length.</li>
<li>u₂ = a₂ − (a₂ · q₁)q₁. Remove from a₂ its shadow on q₁. What remains is perpendicular to q₁.</li>
<li>q₂ = u₂ ÷ ‖u₂‖. Make it unit length.</li>
<li>For a₃, remove its shadows on q₁ <b>and</b> q₂, then normalise. And so on.</li>
</ol>
{viz('gramschmidt')}
<p>Keep a record of every shadow length and every length you divided by, and you get the <b>QR decomposition</b>: A = QR, where Q has orthonormal columns and R is upper triangular. Entry rᵢⱼ is the shadow length qᵢ · aⱼ, and the diagonal rⱼⱼ is the length of what was left.</p>
{fx('QR decomposition', 'A = Q R', 'Q: orthonormal columns (QᵀQ = I). R: upper triangular, holding the dot products and lengths found during Gram Schmidt.')}
{worked('Gram Schmidt on a₁ = [3, 4], a₂ = [1, 3]', [
        '‖a₁‖ = <span class="eq">5</span>, so <span class="eq">q₁ = [0.6, 0.8]</span> and <span class="eq">r₁₁ = 5</span>',
        'Shadow of a₂ on q₁: <span class="eq">r₁₂ = a₂ · q₁ = 0.6 + 2.4 = 3</span>',
        'Remove it: <span class="eq">u₂ = [1, 3] − 3 × [0.6, 0.8] = [−0.8, 0.6]</span>',
        'Its length: <span class="eq">r₂₂ = 1</span>, so <span class="eq">q₂ = [−0.8, 0.6]</span>',
        'So <span class="eq">Q = [[0.6, −0.8], [0.8, 0.6]]</span> and <span class="eq">R = [[5, 3], [0, 1]]</span>. Check: QR gives back [[3, 1], [4, 3]] ✓'])}
{code('gram_schmidt', 'Gram Schmidt on three vectors, printing Q and R')}
{ml('Least squares regression is solved much more accurately with QR than with the normal equations. From Xβ = y and X = QR you get Rβ = Qᵀy, a triangular system solved by back substitution, without ever forming XᵀX (which squares the condition number). This is what numerical libraries do under the hood.')}
{trick('Gram Schmidt in four words: project, subtract, normalise, repeat.')}
''', kw=['gram schmidt', 'qr decomposition', 'orthonormalise', 'projection', 'upper triangular', 'least squares qr']),

    part('posdef', '🥣', 'Quadratic forms and positive definite matrices', f'''
<p>A <b>quadratic form</b> is the matrix version of ax². For a symmetric matrix A and a vector x, the number xᵀAx is a sum of squares and cross terms. In two dimensions it is a surface over the plane, and its shape is decided by A.</p>
{fx('Quadratic form in 2D', 'xᵀAx with A = [[a, b], [b, c]] gives a x₁² + 2b x₁x₂ + c x₂²', 'It is the curvature part of every smooth function near a flat point, which is why the Hessian (Chapter 7) is a quadratic form.')}
{table(['Name', 'Rule for every x ≠ 0', 'Eigenvalues', 'Shape of xᵀAx'], [
        ['positive definite', 'xᵀAx &gt; 0', 'all positive', 'a bowl with one lowest point'],
        ['positive semi definite', 'xᵀAx ≥ 0', 'all ≥ 0', 'a bowl or a flat bottomed trough'],
        ['indefinite', 'positive for some x, negative for others', 'mixed signs', 'a saddle'],
        ['negative definite', 'xᵀAx &lt; 0', 'all negative', 'an upside down bowl'],
    ])}
{viz('quadform')}
<p>Checking every x is impossible, so we use shortcuts. For a symmetric matrix, these tests all agree.</p>
<ul>
<li><b>Eigenvalues:</b> all positive.</li>
<li><b>Leading minors (Sylvester’s test):</b> the determinants of the top left 1 × 1, 2 × 2, 3 × 3 … corners are all positive.</li>
<li><b>Cholesky:</b> the factorisation of the next lesson succeeds without ever taking the square root of a negative number.</li>
</ul>
{worked('Is A = [[2, 1], [1, 3]] positive definite?', [
        'First leading minor: <span class="eq">2 &gt; 0</span>',
        'Second leading minor: <span class="eq">det A = 2 × 3 − 1 × 1 = 5 &gt; 0</span>',
        'Both positive, so yes. Its eigenvalues are <span class="eq">(5 ± √5) ÷ 2 ≈ 3.618</span> and <span class="eq">1.382</span>, both positive ✓',
        'Spot check: x = [1, −1] gives <span class="eq">2 − 2 + 3 = 3 &gt; 0</span>'])}
{code('quad_form', 'Two quadratic forms: a bowl and a saddle')}
{ml('Every covariance matrix is positive semi definite, because xᵀΣx is the variance of the combined feature x · X, and a variance can never be negative. A loss whose Hessian is positive definite everywhere is strictly convex and has exactly one minimum, so gradient descent cannot get stuck.')}
''', kw=['quadratic form', 'positive definite', 'positive semi definite', 'indefinite', 'sylvester test', 'leading minors', 'hessian', 'covariance matrix']),

    part('lu', '🧩', 'LU and Cholesky: solving systems fast', f'''
<p>Gaussian elimination (Chapter 4) secretly builds a factorisation. Record the multipliers you used to clear each column, put them in a lower triangular matrix L with 1s on the diagonal, and keep the staircase you ended with as an upper triangular matrix U. Then <b>A = LU</b>.</p>
{fxs(fx('LU decomposition', 'A = L U', 'L: lower triangular, the multipliers of elimination. U: upper triangular, the staircase. Often rows are swapped first for accuracy, giving PA = LU.'),
         fx('Cholesky decomposition', 'A = L Lᵀ', 'Only for symmetric positive definite A. L is lower triangular with positive diagonal. Twice as fast as LU and very stable.'))}
<p>The factorisation pays off when you solve many systems with the same A. Once A is factorised, solving Ax = b for a new b is two quick triangular solves: first Ly = b from the top down (forward substitution), then Ux = y from the bottom up (back substitution). Factorising costs about n³ ÷ 3 steps, but each new right hand side costs only about n². With a thousand right hand sides, that saving is enormous.</p>
{viz('lusteps')}
{worked('Cholesky of A = [[4, 2, 2], [2, 5, 3], [2, 3, 6]]', [
        '<span class="eq">l₁₁ = √4 = 2</span>, then <span class="eq">l₂₁ = 2 ÷ 2 = 1</span>, <span class="eq">l₃₁ = 2 ÷ 2 = 1</span>',
        '<span class="eq">l₂₂ = √(5 − 1²) = 2</span>, then <span class="eq">l₃₂ = (3 − 1 × 1) ÷ 2 = 1</span>',
        '<span class="eq">l₃₃ = √(6 − 1² − 1²) = 2</span>',
        'So <span class="eq">L = [[2, 0, 0], [1, 2, 0], [1, 1, 2]]</span>. Multiply L by Lᵀ to get A back.',
        'Solve Ax = [8, 10, 11]: forward gives <span class="eq">y = [4, 3, 2]</span>, backward gives <span class="eq">x = [1, 1, 1]</span>'])}
{code('cholesky', 'Cholesky factorisation, then two triangular solves')}
{ml('Gaussian processes, a popular Bayesian model, need to solve with a big covariance matrix again and again, and they always use its Cholesky factor. Sampling from a multivariate normal (Chapter 15) also uses Cholesky: if z is standard normal noise, then μ + Lz has covariance LLᵀ = Σ.')}
''', kw=['lu decomposition', 'cholesky', 'forward substitution', 'back substitution', 'triangular', 'factorisation', 'gaussian process']),

    part('lstsq', '📏', 'Least squares as a projection', f'''
<p>When there are more equations than unknowns, as with 1000 houses and 3 weights, Xβ = y has no exact answer. Least squares picks the β whose predictions Xβ are as close as possible to y. There is a beautiful picture behind it. All possible prediction vectors Xβ form a flat space (the column space of X). The best one is the <b>projection</b> of y onto that space, the point directly "below" y. The leftover, the residual r = y − Xβ, is perpendicular to every column of X.</p>
{fx('The residual is perpendicular to every column', 'Xᵀ(y − Xβ) = 0 &nbsp; ⟹ &nbsp; XᵀXβ = Xᵀy', 'These are the normal equations. "Normal" is an old word for perpendicular.')}
{viz('lsq')}
{worked('Fit y = a + bx to (1, 2), (2, 3), (3, 5), (4, 6)', [
        'Means: <span class="eq">x̄ = 2.5</span>, <span class="eq">ȳ = 4</span>',
        'Slope: <span class="eq">b = Σ(x − x̄)(y − ȳ) ÷ Σ(x − x̄)² = 7 ÷ 5 = 1.4</span>',
        'Intercept: <span class="eq">a = ȳ − b x̄ = 4 − 3.5 = 0.5</span>',
        'Residuals: <span class="eq">[0.1, −0.3, 0.3, −0.1]</span>. They add to 0 and Σ x r = 0.1 − 0.6 + 0.9 − 0.4 = 0, so r is perpendicular to both columns of X ✓',
        'Sum of squared residuals: <span class="eq">0.01 + 0.09 + 0.09 + 0.01 = 0.2</span>, the smallest possible for any straight line.'])}
{code('normal_eq', 'Least squares by the normal equations, with the perpendicular check')}
{fx('Pseudo inverse', 'β = X⁺ y with X⁺ = (XᵀX)⁻¹Xᵀ when the columns are independent', 'For any X, the SVD gives X⁺ = VΣ⁺Uᵀ, which also works when columns are dependent. NumPy calls it pinv.')}
{life('A satellite navigation receiver hears more satellites than it strictly needs. The extra equations disagree slightly because of noise, so it finds the position by least squares, the point that disagrees least with all of them together.')}
''', kw=['least squares', 'projection', 'column space', 'normal equations', 'residual', 'pseudo inverse', 'linear regression geometry']),

    part('norms', '🎚️', 'Matrix norms, trace and the condition number', f'''
<p>Vectors have lengths (Chapter 3). Matrices need a size too, for regularising weight matrices, for measuring how far apart two matrices are, and for judging how sensitive a problem is. There are a few standard choices.</p>
{table(['Measure', 'Formula', 'Meaning'], [
        ['Frobenius norm', '‖A‖_F = √(Σ aᵢⱼ²)', 'treat the matrix as one long vector. Weight decay uses its square'],
        ['spectral norm', '‖A‖₂ = σmax', 'the most the matrix can stretch any unit vector'],
        ['trace', 'tr(A) = Σ aᵢᵢ = Σ λᵢ', 'sum of the diagonal, also the sum of the eigenvalues'],
        ['condition number', 'κ(A) = σmax ÷ σmin', 'how much small input errors can be amplified'],
    ])}
<p>The picture: a matrix turns the unit circle into an ellipse (Chapter 5). The longest half axis is σmax and the shortest is σmin. A round ellipse means every direction is treated alike and κ is close to 1. A thin, needle like ellipse means one direction is almost crushed, κ is huge, and solving Ax = b becomes very sensitive.</p>
{viz('condviz')}
{worked('A nearly singular system', [
        'A = <span class="eq">[[1, 1], [1, 1.001]]</span>. The two rows are almost the same equation.',
        'With b = [2, 2.001] the answer is <span class="eq">x = [1, 1]</span>',
        'Change one number in b by only 0.001, to [2, 2.002], and the answer jumps to <span class="eq">x = [0, 2]</span>',
        'The condition number is about <span class="eq">4002</span>, so an error in the data can be amplified about four thousand times.'])}
{code('cond', 'Frobenius norm, trace, condition number and a tiny change with a big effect')}
{fx('Rule of thumb for lost digits', 'digits lost ≈ log₁₀ κ', 'With κ = 10⁸ and float64 (about 16 digits), only about 8 digits of the answer can be trusted. With float32 (7 digits), none can.')}
{ml('Spectral normalisation divides a layer’s weight matrix by its largest singular value so that the layer can never stretch its input by more than 1. It is widely used to stabilise the training of GANs. The Frobenius norm of the weights is exactly what L2 weight decay penalises.')}
''', kw=['matrix norm', 'frobenius norm', 'spectral norm', 'trace', 'condition number', 'ill conditioned', 'singular values', 'spectral normalisation']),

    part('tensors', '🧊', 'Tensors, shapes and broadcasting', f'''
<p>A <b>tensor</b> in machine learning code is simply an array with any number of directions, called axes or dimensions. A number is a 0D tensor, a vector is 1D, a matrix is 2D, and so on. The <b>shape</b> lists the size along each axis.</p>
{table(['Data', 'Typical shape', 'Axes read left to right'], [
        ['one number (a loss)', '()', 'nothing'],
        ['a batch of feature vectors', '(32, 20)', 'examples, features'],
        ['a batch of colour images (PyTorch order)', '(32, 3, 224, 224)', 'examples, colour channels, height, width'],
        ['a batch of sentences after embedding', '(16, 128, 768)', 'sentences, tokens, embedding numbers'],
        ['attention scores in a transformer', '(16, 12, 128, 128)', 'sentences, heads, query token, key token'],
    ])}
<p><b>Broadcasting</b> is the rule that lets you combine tensors of different shapes without copying data by hand. Line the shapes up from the right. Two sizes are compatible when they are equal or when one of them is 1. A size 1 axis is stretched (repeated) to match the other one. A missing axis on the left counts as size 1.</p>
{viz('bcast')}
{worked('Shapes (8, 1, 6, 1) and (7, 1, 5)', [
        'Line them up from the right: <span class="eq">(8, 1, 6, 1)</span> over <span class="eq">( _, 7, 1, 5)</span>',
        'Last axis: 1 and 5, one is 1, so the result is <span class="eq">5</span>',
        'Next: 6 and 1, so <span class="eq">6</span>. Next: 1 and 7, so <span class="eq">7</span>',
        'First: 8 and missing (treated as 1), so <span class="eq">8</span>',
        'Result shape: <span class="eq">(8, 7, 6, 5)</span>'])}
{code('broadcast', 'The broadcasting rule written out by hand')}
{ml('Adding a bias to a batch, Z = XW + b with Z of shape (32, 10) and b of shape (10,), works by broadcasting b down all 32 rows. Normalising images by subtracting a per channel mean of shape (3, 1, 1) from a batch of shape (32, 3, 224, 224) is broadcasting too. Many silent bugs come from a shape like (32, 1) meeting (32,) and quietly becoming (32, 32).')}
{trick('Read shapes from the right, and say "equal or one" for each pair. If any pair fails that test, the operation is an error.')}
''', kw=['tensor', 'shape', 'axis', 'broadcasting', 'batch dimension', 'numpy', 'pytorch', 'shape mismatch']),
]

INFO = {
    'title': 'Factorise, then everything is easier',
    'panels': [
        {'s': [['e', '📐'], ['t', 'QᵀQ = I', {'b': 1}]], 'h': 'Orthonormal', 't': 'Perpendicular unit vectors.', 'more': 'Coordinates are dot products.'},
        {'s': [['e', '🧹'], ['t', 'A = QR', {'b': 1}]], 'h': 'Gram Schmidt', 't': 'Project, subtract, normalise.', 'more': 'Stable least squares.'},
        {'s': [['e', '🥣'], ['t', 'xᵀAx &gt; 0', {'b': 1}]], 'h': 'Positive definite', 't': 'A bowl with one bottom.', 'more': 'All eigenvalues positive.'},
        {'s': [['e', '🧊'], ['t', 'equal or 1', {'b': 1}]], 'h': 'Broadcasting', 't': 'Line shapes up from the right.', 'more': 'Size 1 axes stretch.'},
    ],
    'remember': 'Orthonormal vectors make coordinates simple dot products and Q⁻¹ = Qᵀ. Gram Schmidt builds them and gives A = QR. A symmetric matrix is positive definite when all its eigenvalues (or leading minors) are positive, and then A = LLᵀ by Cholesky. Least squares projects y onto the column space, so the residual is perpendicular to every column. The condition number σmax ÷ σmin says how many digits you may lose. Broadcasting lines shapes up from the right and stretches size 1 axes.',
}

REAL = [
    ['🛰️', 'Navigation', 'Phone navigation solves an over determined least squares problem every second to turn many satellite signals into one position.'],
    ['🌦️', 'Weather forecasts', 'Forecast centres combine millions of observations with physics models using huge least squares problems that rely on Cholesky style factorisations.'],
    ['🖼️', 'Deep learning frameworks', 'Every PyTorch and NumPy program depends on broadcasting rules, and many training bugs are shape mistakes found by reading shapes from the right.'],
]

K.say('top', 'Welcome',
      'This chapter takes linear algebra to the level used inside real libraries. You will build orthonormal bases with Gram Schmidt, factorise matrices with QR, LU and Cholesky, see least squares as a projection, measure how fragile a problem is with the condition number, and learn the broadcasting rules that every tensor library follows.',
      'यह अध्याय linear algebra को असली libraries के स्तर तक ले जाता है। Gram Schmidt से orthonormal basis, QR, LU और Cholesky से matrix को तोड़ना, least squares को projection की तरह देखना, condition number और tensors की broadcasting सीखेंगे।',
      'ಈ ಅಧ್ಯಾಯ linear algebra ಅನ್ನು ನಿಜವಾದ libraries ಮಟ್ಟಕ್ಕೆ ಕೊಂಡೊಯ್ಯುತ್ತದೆ. Gram Schmidt, QR, LU, Cholesky, least squares, condition number ಮತ್ತು broadcasting ಕಲಿಯುತ್ತೀರಿ.',
      'ଏହି ଅଧ୍ୟାୟ linear algebra କୁ ପ୍ରକୃତ libraries ସ୍ତରକୁ ନିଏ। Gram Schmidt, QR, LU, Cholesky, least squares, condition number ଓ broadcasting ଶିଖିବେ।',
      'يأخذ هذا الفصل الجبر الخطي إلى المستوى المستخدم داخل المكتبات الحقيقية. ستبني قواعد متعامدة بطريقة غرام شميت، وتفكك المصفوفات بطرق QR وLU وتشوليسكي، وترى المربعات الصغرى كإسقاط، وتقيس حساسية المسألة برقم الحالة، وتتعلم قواعد البث في المصفوفات متعددة الأبعاد.',
      'Dieses Kapitel bringt lineare Algebra auf das Niveau echter Bibliotheken. Du baust Orthonormalbasen mit Gram Schmidt, zerlegst Matrizen mit QR, LU und Cholesky, siehst kleinste Quadrate als Projektion, misst mit der Konditionszahl, wie empfindlich ein Problem ist, und lernst die Broadcasting Regeln jeder Tensorbibliothek.')
K.say('orth', 'Orthonormal bases',
      'Orthonormal vectors have length one and meet at right angles. In such a basis, finding coordinates needs no equations at all. Each coordinate is just a dot product. A matrix with orthonormal columns only rotates or reflects, and its inverse is its transpose.',
      'Orthonormal vectors की लंबाई एक होती है और वे समकोण पर मिलते हैं। ऐसे basis में हर coordinate बस एक dot product है। ऐसी matrix का inverse उसका transpose है।',
      'Orthonormal vectors ಉದ್ದ ಒಂದು ಮತ್ತು ಲಂಬವಾಗಿರುತ್ತವೆ. ಪ್ರತಿ coordinate ಒಂದು dot product. Inverse ಎಂದರೆ transpose.',
      'Orthonormal vectors ର ଲମ୍ବ ଏକ ଓ ସମକୋଣରେ ମିଳନ୍ତି। ପ୍ରତି coordinate ଗୋଟିଏ dot product। Inverse ହେଉଛି transpose।',
      'المتجهات المتعامدة المعيارية طولها واحد وتلتقي بزوايا قائمة. في مثل هذه القاعدة كل إحداثي هو مجرد ضرب نقطي، ومعكوس المصفوفة هو منقولها.',
      'Orthonormale Vektoren haben die Länge eins und stehen senkrecht aufeinander. In so einer Basis ist jede Koordinate einfach ein Skalarprodukt, und die Inverse der Matrix ist ihre Transponierte.')
K.say('gram', 'Gram Schmidt and QR',
      'Gram Schmidt takes each vector, removes its shadows on the directions already found, and stretches what is left to length one. Recording the shadow lengths gives A equals Q times R, the factorisation used to solve least squares accurately.',
      'Gram Schmidt हर vector से पहले मिली दिशाओं पर उसकी छाया हटाता है और बचे हिस्से को लंबाई एक देता है। छाया की लंबाइयाँ लिखने से A बराबर Q गुणा R मिलता है।',
      'Gram Schmidt ಪ್ರತಿ vector ನಿಂದ ನೆರಳು ತೆಗೆದು ಉದ್ದ ಒಂದು ಮಾಡುತ್ತದೆ. ಇದರಿಂದ A ಸಮ Q ಗುಣಿಸು R.',
      'Gram Schmidt ପ୍ରତି vector ରୁ ଛାଇ ବାହାର କରି ଲମ୍ବ ଏକ କରେ। ଏଥିରୁ A ସମାନ Q ଗୁଣନ R।',
      'تأخذ طريقة غرام شميت كل متجه وتزيل ظلاله على الاتجاهات السابقة ثم تجعل الباقي بطول واحد. وتسجيل أطوال الظلال يعطي A يساوي Q في R.',
      'Gram Schmidt nimmt jeden Vektor, entfernt seine Schatten auf die schon gefundenen Richtungen und streckt den Rest auf Länge eins. Die Schattenlängen ergeben A gleich Q mal R.')
K.say('posdef', 'Positive definite matrices',
      'The quadratic form x transpose A x is the matrix version of a x squared. If it is positive for every non zero x, the matrix is positive definite and the surface is a bowl with one lowest point. Check it with eigenvalues or with leading minors.',
      'Quadratic form x transpose A x, a x squared का matrix रूप है। अगर यह हर x के लिए धनात्मक है तो matrix positive definite है और सतह एक कटोरा है।',
      'x transpose A x ಎಲ್ಲಾ x ಗೆ ಧನಾತ್ಮಕವಾದರೆ matrix positive definite, ಮೇಲ್ಮೈ ಒಂದು ಬಟ್ಟಲು.',
      'x transpose A x ସବୁ x ପାଇଁ ଧନାତ୍ମକ ହେଲେ matrix positive definite, ପୃଷ୍ଠ ଗୋଟିଏ ବାଟି।',
      'الصيغة التربيعية x منقول A x هي نسخة المصفوفة من a x تربيع. إذا كانت موجبة لكل x غير صفري فالمصفوفة موجبة التعريف والسطح وعاء له قاع واحد.',
      'Die quadratische Form x transponiert A x ist die Matrixversion von a x Quadrat. Ist sie für jedes x ungleich null positiv, ist die Matrix positiv definit und die Fläche eine Schüssel mit einem tiefsten Punkt.')
K.say('lu', 'LU and Cholesky',
      'Elimination secretly builds A equals L times U. Cholesky is the special version A equals L times L transpose for positive definite matrices. Once you have the factors, every new right hand side is solved with two fast triangular passes.',
      'Elimination चुपके से A बराबर L गुणा U बनाता है। Positive definite matrix के लिए Cholesky A बराबर L गुणा L transpose देता है। फिर हर नया सवाल दो तेज़ triangular कदमों में हल होता है।',
      'Elimination ನಿಂದ A ಸಮ L ಗುಣಿಸು U. Cholesky ಯಲ್ಲಿ A ಸಮ L ಗುಣಿಸು L transpose.',
      'Elimination ରୁ A ସମାନ L ଗୁଣନ U। Cholesky ରେ A ସମାନ L ଗୁଣନ L transpose।',
      'الحذف يبني سرًا A يساوي L في U. وتشوليسكي هي الحالة الخاصة A يساوي L في منقول L للمصفوفات موجبة التعريف. بعدها يُحل كل طرف أيمن جديد بخطوتين مثلثيتين سريعتين.',
      'Die Elimination baut heimlich A gleich L mal U. Cholesky ist der Spezialfall A gleich L mal L transponiert für positiv definite Matrizen. Danach löst man jede neue rechte Seite mit zwei schnellen Dreiecksschritten.')
K.say('lstsq', 'Least squares',
      'With more equations than unknowns there is no exact answer, so least squares projects y onto the space of possible predictions. The residual is perpendicular to every column of X, which gives the normal equations.',
      'जब समीकरण अज्ञात से ज़्यादा हों तो least squares y को संभव predictions के space पर project करता है। Residual X के हर column पर लंबवत होता है।',
      'Least squares y ಅನ್ನು predictions space ಮೇಲೆ project ಮಾಡುತ್ತದೆ. Residual ಪ್ರತಿ column ಗೆ ಲಂಬ.',
      'Least squares y କୁ predictions space ଉପରେ project କରେ। Residual ପ୍ରତି column କୁ ଲମ୍ବ।',
      'حين تكون المعادلات أكثر من المجاهيل لا يوجد حل دقيق، فتسقط المربعات الصغرى y على فضاء التنبؤات الممكنة، ويكون الباقي عموديًا على كل عمود في X.',
      'Mit mehr Gleichungen als Unbekannten gibt es keine exakte Lösung, also projiziert die Methode der kleinsten Quadrate y auf den Raum der möglichen Vorhersagen. Das Residuum steht senkrecht auf jeder Spalte von X.')
K.say('norms', 'Norms and condition number',
      'The Frobenius norm treats a matrix as one long vector. The spectral norm is its biggest stretch. The condition number, biggest stretch divided by smallest, tells how much tiny errors in the data can be blown up in the answer.',
      'Frobenius norm matrix को एक लंबा vector मानता है। Spectral norm सबसे बड़ा खिंचाव है। Condition number बताता है कि data की छोटी गलती जवाब में कितनी बढ़ सकती है।',
      'Frobenius norm, spectral norm ಮತ್ತು condition number. ಸಣ್ಣ ದೋಷ ಉತ್ತರದಲ್ಲಿ ಎಷ್ಟು ದೊಡ್ಡದಾಗಬಹುದು ಎಂದು ಹೇಳುತ್ತದೆ.',
      'Frobenius norm, spectral norm ଓ condition number। ଛୋଟ ଭୁଲ ଉତ୍ତରରେ କେତେ ବଢ଼ିପାରେ।',
      'معيار فروبينيوس يعامل المصفوفة كمتجه طويل، والمعيار الطيفي هو أكبر تمدد، ورقم الحالة يخبرك كم يمكن أن تتضخم الأخطاء الصغيرة في الجواب.',
      'Die Frobeniusnorm behandelt eine Matrix wie einen langen Vektor. Die Spektralnorm ist ihre größte Streckung. Die Konditionszahl sagt, wie stark kleine Datenfehler in der Antwort verstärkt werden können.')
K.say('tensors', 'Tensors and broadcasting',
      'A tensor is an array with any number of axes, and its shape lists their sizes. Broadcasting lines shapes up from the right. Each pair of sizes must be equal or one of them must be one, and size one axes are stretched to match.',
      'Tensor कई axes वाला array है और shape उनके आकार बताता है। Broadcasting में shapes को दाईं ओर से मिलाते हैं। हर जोड़ी बराबर हो या उनमें एक, एक हो।',
      'Tensor ಅನೇಕ axes ಇರುವ array. Broadcasting ನಲ್ಲಿ shapes ಬಲದಿಂದ ಹೋಲಿಸಿ, ಸಮ ಅಥವಾ ಒಂದು.',
      'Tensor ଅନେକ axes ଥିବା array। Broadcasting ରେ shapes ଡାହାଣରୁ ମିଳାନ୍ତୁ, ସମାନ କିମ୍ବା ଏକ।',
      'الموتر مصفوفة بأي عدد من المحاور، وشكله يذكر أحجامها. في البث نرصف الأشكال من اليمين، ويجب أن يتساوى كل زوج أو يكون أحدهما واحدًا.',
      'Ein Tensor ist ein Array mit beliebig vielen Achsen, seine Form nennt ihre Größen. Beim Broadcasting richtet man Formen von rechts aus. Jedes Paar muss gleich sein oder eine Größe muss eins sein.')
K.say('practice', 'Practice',
      'Now practise: check whether a set of vectors is orthonormal, fit a line with QR, test matrices for positive definiteness with leading minors, and find the cheapest order to multiply a chain of matrices.',
      'अब अभ्यास: vectors orthonormal हैं या नहीं, QR से line fit, leading minors से positive definite की जाँच, और matrices की श्रृंखला को सबसे सस्ते क्रम में गुणा करना।',
      'ಅಭ್ಯಾಸ: orthonormal ಪರೀಕ್ಷೆ, QR ನಿಂದ line fit, positive definite ಪರೀಕ್ಷೆ, matrix chain ಕ್ರಮ.',
      'ଅଭ୍ୟାସ: orthonormal ପରୀକ୍ଷା, QR ରେ line fit, positive definite ପରୀକ୍ଷା, matrix chain କ୍ରମ।',
      'تدرب الآن: افحص هل المتجهات متعامدة معيارية، وارسم خطًا بطريقة QR، واختبر المصفوفات بالمحددات الرئيسية، وجد أرخص ترتيب لضرب سلسلة مصفوفات.',
      'Jetzt üben: prüfe, ob Vektoren orthonormal sind, passe eine Gerade mit QR an, teste Matrizen mit Hauptminoren auf positive Definitheit und finde die billigste Reihenfolge für ein Matrixprodukt.')

# ---------------------------------------------------------------- practice
K.practice('orth-check', 'e', 'Is this set orthonormal?', 'p_orth_check',
           '<p>Write a function that checks whether a list of vectors is orthonormal by testing every pair of dot products. Try it on {{[1/√2, 1/√2, 0], [−1/√2, 1/√2, 0], [0, 0, 1]}} and on {{[1, 0, 0], [1, 1, 0], [0, 0, 2]}}.</p>',
           'set 1:\n   result: orthonormal\nset 2:\n   v1.v2 = 1.0000, should be 0\n   v2.v2 = 2.0000, should be 1\n   v3.v3 = 4.0000, should be 1\n   result: not orthonormal',
           'Each vector dotted with itself must give 1, and dotted with any other must give 0.',
           '<p>Loop over every pair (i, j) with j ≥ i. The wanted value is 1 when i = j and 0 otherwise. Compare with a small tolerance because 1/√2 is rounded. Set 1 is a 45° rotation of the x and y axes plus the z axis, so it passes. Set 2 fails three ways: [1, 0, 0] and [1, 1, 0] are not perpendicular, [1, 1, 0] has length √2, and [0, 0, 2] has length 2. Normalising would fix the lengths, and Gram Schmidt would fix the angle.</p>',
           'O(n² d)', 'O(1)')
K.practice('qr-line', 'm', 'Fit a line with QR', 'p_qr_line',
           '<p>Fit y = a + bx to the points (0, 1), (1, 3) and (2, 4) using Gram Schmidt on the two columns of X = [[1, 0], [1, 1], [1, 2]], then solve Rβ = Qᵀy by back substitution.</p>',
           'R = [[1.7321, 1.7321], [0, 1.4142]]\nQ^T y = [4.6188, 2.1213]\nintercept = 1.1667, slope = 1.5000',
           'r₁₁ = ‖[1, 1, 1]‖ = √3. Then remove the shadow of the x column on q₁.',
           '<p>q₁ = [1, 1, 1] ÷ √3, r₁₂ = q₁ · [0, 1, 2] = 3 ÷ √3 = √3. The leftover u = [0, 1, 2] − [1, 1, 1] = [−1, 0, 1] has length √2, so r₂₂ = √2. Then Qᵀy = [8 ÷ √3, 3 ÷ √2]. Back substitution: slope = (3 ÷ √2) ÷ √2 = 1.5, intercept = (8 ÷ √3 − √3 × 1.5) ÷ √3 = 8 ÷ 3 − 1.5 ≈ 1.1667. This matches the formula b = covariance ÷ variance from Chapter 11, but QR never formed XᵀX.</p>',
           'O(n k²)', 'O(n k)')
K.practice('posdef', 'h', 'Sylvester’s test for positive definiteness', 'p_posdef',
           '<p>Compute the leading principal minors (the determinants of the top left 1 × 1, 2 × 2 and 3 × 3 corners) of A = [[2, −1, 0], [−1, 2, −1], [0, −1, 2]] and B = [[1, 2, 0], [2, 1, 0], [0, 0, 3]], and decide which is positive definite.</p>',
           'A: leading minors [2, 3, 4] -> positive definite\nB: leading minors [1, -3, -9] -> not positive definite',
           'A symmetric matrix is positive definite exactly when every leading minor is positive.',
           '<p>For A the minors are 2, then 2 × 2 − (−1)(−1) = 3, then det A = 4, all positive. This matrix appears in physics and in smoothing problems as the "second difference" matrix. For B the second minor is 1 × 1 − 2 × 2 = −3, negative, so B is indefinite: x = [1, −1, 0] gives xᵀBx = 1 − 4 + 1 = −2. One negative minor is enough to stop.</p>',
           'O(n⁴) with this simple determinant', 'O(n²)')
K.practice('chain-cost', 'x', 'The cheapest order for a chain of products', 'p_chain_cost',
           '<p>A is 10 × 100, B is 100 × 5 and C is 5 × 50. Matrix multiplication is associative, so (AB)C = A(BC). Count the multiplications each order needs.</p>',
           '(AB)C needs 7500 multiplications\nA(BC) needs 75000 multiplications\nthe better order is 10 times cheaper',
           'An (m × n) times (n × p) product costs m × n × p multiplications.',
           '<p>(AB) is 10 × 100 × 5 = 5000 and gives a 10 × 5 matrix. Times C costs 10 × 5 × 50 = 2500. Total 7500. The other way, (BC) costs 100 × 5 × 50 = 25000 and gives 100 × 50, then A times that costs 10 × 100 × 50 = 50000. Total 75000. Same answer, ten times the work. Deep learning libraries such as einsum optimisers choose the order of tensor contractions for exactly this reason, and the classic dynamic programming algorithm finds the best order for long chains.</p>',
           'O(1) here, O(k³) for a chain of k matrices', 'O(k²)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Two vectors are orthogonal when…', ['their lengths are equal', 'their dot product is 0', 'they point the same way', 'their sum is 0'], 1, 'Right angle.', 'a · b = ‖a‖‖b‖cos 90° = 0.')
K.quiz('e', 'What does QᵀQ = I say about the columns of Q?', ['they are all equal', 'they are orthonormal', 'they add up to zero', 'they are positive'], 1, 'Entry (i, j) of QᵀQ is qᵢ · qⱼ.', 'Diagonal 1 means unit length, off diagonal 0 means perpendicular.')
K.quiz('e', 'Shapes (3, 1) and (1, 4) are broadcast together. What is the result shape?', ['(3, 4)', '(1, 1)', 'error', '(4, 3)'], 0, 'Equal or one, from the right.', '1 stretches to 4 and 1 stretches to 3.')
K.quiz('e', 'In an orthonormal basis, how do you find the coordinate of v along q₁?', ['solve a system of equations', 'take the dot product v · q₁', 'divide v by q₁', 'take the cross product'], 1, 'No equations needed.', 'cᵢ = v · qᵢ.')
K.quiz('m', 'In A = QR from Gram Schmidt, what kind of matrix is R?', ['diagonal', 'upper triangular', 'orthogonal', 'symmetric'], 1, 'Each new vector only uses the directions found before it.', 'rᵢⱼ = qᵢ · aⱼ is zero when i > j.')
K.quiz('m', 'A symmetric 2 × 2 matrix has eigenvalues 3 and −1. The quadratic form xᵀAx is…', ['a bowl', 'a saddle', 'an upside down bowl', 'flat'], 1, 'Mixed signs.', 'Positive in one direction, negative in another: indefinite.')
K.quiz('m', 'Which matrices have a Cholesky factorisation A = LLᵀ?', ['every square matrix', 'symmetric positive definite matrices', 'only diagonal matrices', 'only orthogonal matrices'], 1, 'Square roots of positive numbers.', 'The diagonal steps take square roots that must stay positive.')
K.quiz('m', 'In least squares, the residual y − Xβ is…', ['zero', 'perpendicular to every column of X', 'parallel to y', 'always positive'], 1, 'Projection.', 'Xᵀ(y − Xβ) = 0 are the normal equations.')
K.quiz('m', 'What is the Frobenius norm of [[3, 0], [0, 4]]?', ['7', '5', '12', '25'], 1, 'Square root of the sum of squares.', '√(9 + 16) = 5.')
K.quiz('h', 'A matrix has singular values 100 and 0.1. What is its condition number?', ['10', '100', '1000', '0.001'], 2, 'σmax ÷ σmin.', '100 ÷ 0.1 = 1000, so about 3 digits of accuracy can be lost.')
K.quiz('h', 'Why do libraries prefer QR over the normal equations XᵀXβ = Xᵀy?', ['QR is always faster', 'forming XᵀX squares the condition number and loses accuracy', 'the normal equations give a different answer', 'QR needs no square roots'], 1, 'κ(XᵀX) = κ(X)².', 'QR solves Rβ = Qᵀy and keeps the conditioning of X itself.')
K.quiz('h', 'Shapes (32, 1) and (32,) are added. What happens?', ['error', '(32,) as intended', '(32, 32), which is often a silent bug', '(1, 32)'], 2, 'Line them up from the right: (32, 1) over ( _, 32).', 'The 1 stretches to 32 and the missing axis becomes 32, giving a 32 × 32 result.')
K.quiz('h', 'Leading minors of a symmetric matrix are 2, 3 and −1. It is…', ['positive definite', 'not positive definite', 'orthogonal', 'singular'], 1, 'Sylvester’s test.', 'Every leading minor must be positive. One negative is enough to fail.')
K.quiz('x', 'Q is orthogonal. What is ‖Qx‖ compared with ‖x‖?', ['twice as long', 'the same', 'always 1', 'it depends on x'], 1, '‖Qx‖² = xᵀQᵀQx.', 'QᵀQ = I, so ‖Qx‖² = xᵀx = ‖x‖². Rotations keep lengths.')
K.quiz('x', 'Solving Ax = b for 1000 different b with the same 500 × 500 A, what is the smart plan?', ['invert A 1000 times', 'factorise A once (LU or Cholesky), then do two triangular solves per b', 'use Gram Schmidt on b', 'transpose A'], 1, 'Factorising costs about n³ ÷ 3, a solve about n².', 'One factorisation plus 1000 cheap solves beats 1000 eliminations by a wide margin.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Are [2, −1] and [1, 2] orthogonal? Give their dot product.', '0', 'Multiply matching parts and add.', [
    '<span class="eq">2 × 1 = 2</span>',
    '<span class="eq">(−1) × 2 = −2</span>',
    'Sum: <span class="eq">2 − 2 = 0</span>, so yes, they are orthogonal.',
], check=0)
K.calc('e', 'q₁ = [0.6, 0.8] is a unit vector. What is the coordinate of v = [5, 5] along q₁?', '7', 'c = v · q₁.', [
    '<span class="eq">5 × 0.6 = 3</span>',
    '<span class="eq">5 × 0.8 = 4</span>',
    'Add: <span class="eq">3 + 4 = 7</span>',
], check=7)
K.calc('e', 'What is the Frobenius norm of [[1, 2], [2, 4]]?', '5', 'Square every entry, add, take the square root.', [
    'Squares: <span class="eq">1, 4, 4, 16</span>',
    'Sum: <span class="eq">25</span>',
    '<span class="eq">√25 = 5</span>',
], check=5)
K.calc('e', 'Broadcast (5, 1, 3) with (4, 3). How many numbers does the result hold?', '60', 'Find the result shape first.', [
    'Line up from the right: <span class="eq">(5, 1, 3)</span> over <span class="eq">( _, 4, 3)</span>',
    'Result shape: <span class="eq">(5, 4, 3)</span>',
    'Count: <span class="eq">5 × 4 × 3 = 60</span>',
], check=60)
K.calc('m', 'Gram Schmidt step: q₁ = [1, 0] and a₂ = [3, 4]. What is the length r₂₂ of what is left after removing the shadow on q₁?', '4', 'u₂ = a₂ − (a₂ · q₁) q₁.', [
    'Shadow length: <span class="eq">a₂ · q₁ = 3</span>',
    'Remove it: <span class="eq">u₂ = [3, 4] − 3 × [1, 0] = [0, 4]</span>',
    'Length: <span class="eq">‖[0, 4]‖ = 4</span>',
], check=4)
K.calc('m', 'Is [[4, 2], [2, 1]] positive definite? Give its second leading minor.', '0', 'det of the whole 2 × 2.', [
    'First minor: <span class="eq">4 &gt; 0</span>',
    'Second minor: <span class="eq">4 × 1 − 2 × 2 = 0</span>',
    'Zero is not positive, so it is only positive SEMI definite. x = [1, −2] gives xᵀAx = 0.',
], check=0)
K.calc('m', 'Evaluate xᵀAx for A = [[2, 1], [1, 3]] and x = [1, 2].', '18', 'a x₁² + 2b x₁x₂ + c x₂².', [
    '<span class="eq">2 × 1² = 2</span>',
    '<span class="eq">2 × 1 × 1 × 2 = 4</span>',
    '<span class="eq">3 × 2² = 12</span>, total <span class="eq">2 + 4 + 12 = 18</span>',
], check=18)
K.calc('m', 'Cholesky of [[9, 3], [3, 5]]: what is l₂₂?', '2', 'l₁₁ = √9, l₂₁ = 3 ÷ l₁₁, l₂₂ = √(5 − l₂₁²).', [
    '<span class="eq">l₁₁ = 3</span>',
    '<span class="eq">l₂₁ = 3 ÷ 3 = 1</span>',
    '<span class="eq">l₂₂ = √(5 − 1) = 2</span>',
], check=2)
K.calc('h', 'Least squares line through (0, 0), (1, 1), (2, 1). What is the slope?', '0.5', 'b = Σ(x − x̄)(y − ȳ) ÷ Σ(x − x̄)².', [
    'Means: <span class="eq">x̄ = 1</span>, <span class="eq">ȳ = 2 ÷ 3</span>',
    'Top: <span class="eq">(−1)(−2/3) + 0 + (1)(1/3) = 2/3 + 1/3 = 1</span>',
    'Bottom: <span class="eq">1 + 0 + 1 = 2</span>, so slope <span class="eq">1 ÷ 2 = 0.5</span>',
], check=0.5)
K.calc('h', 'A symmetric matrix has eigenvalues 8 and 0.002. What is its condition number?', '4000', 'For a symmetric matrix the singular values are the absolute eigenvalues.', [
    '<span class="eq">σmax = 8</span>, <span class="eq">σmin = 0.002</span>',
    '<span class="eq">κ = 8 ÷ 0.002 = 4000</span>',
    'About log₁₀ 4000 ≈ 3.6 digits of accuracy may be lost.',
], check=4000)
K.calc('x', 'How many multiplications does A(BC) need if A is 2 × 50, B is 50 × 40 and C is 40 × 1?', '2100', 'Cost of (m × n)(n × p) is m n p.', [
    'BC: <span class="eq">50 × 40 × 1 = 2000</span>, giving 50 × 1',
    'A(BC): <span class="eq">2 × 50 × 1 = 100</span>',
    'Total: <span class="eq">2100</span>. The order (AB)C would need 4000 + 80 = 4080.',
], check=2100)
K.calc('x', 'Q = [[0.6, −0.8], [0.8, 0.6]] and x = [3, 4]. What is ‖Qx‖?', '5', 'Orthogonal matrices keep lengths.', [
    'Qx = <span class="eq">[1.8 − 3.2, 2.4 + 2.4] = [−1.4, 4.8]</span>',
    '‖Qx‖ = <span class="eq">√(1.96 + 23.04) = √25 = 5</span>',
    'Same as ‖x‖ = √(9 + 16) = 5, as promised.',
], check=5)

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;
  const fmt = v => MV.num(Math.abs(v) < 1e-9 ? 0 : v, 3);

  /* ----- coordinates in a rotated orthonormal basis ----- */
  W.orthbasis = el => {
    const b = shell(el, 'Coordinates in a turned basis', 'q₁ (blue) and q₂ (green) are perpendicular unit arrows turned by θ. Drag the orange tip of v. Its coordinates are the shadow lengths v · q₁ and v · q₂. Press Play to turn the basis.');
    b.innerHTML = `<div class="mv-wrap"><div class="ob-plot"></div><div class="mv-side">${slider('th', 'turn θ°', 0, 90, 53, 1)}<div class="mv-read ob-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const G = MV.frame(420, 420, [-4, 4], [-4, 4]);
    const v = [2, 1];
    let th = 53;
    const host = $('.ob-plot', b);
    host.innerHTML = MV.svg(G, '<g class="ob-g"></g>', 'Rotated basis');
    const svgEl = $('svg', host);
    function draw() {
      const t = th * Math.PI / 180, q1 = [Math.cos(t), Math.sin(t)], q2 = [-Math.sin(t), Math.cos(t)];
      const c1 = v[0] * q1[0] + v[1] * q1[1], c2 = v[0] * q2[0] + v[1] * q2[1];
      let s = MV.axes(G, { labels: false });
      s += MV.line(G, -5 * q1[0], -5 * q1[1], 5 * q1[0], 5 * q1[1], 'mv-v a dash') + MV.line(G, -5 * q2[0], -5 * q2[1], 5 * q2[0], 5 * q2[1], 'mv-v g dash');
      s += MV.line(G, v[0], v[1], c1 * q1[0], c1 * q1[1], 'mv-v k dash') + MV.line(G, v[0], v[1], c2 * q2[0], c2 * q2[1], 'mv-v k dash');
      s += MV.arrow(G, 0, 0, c1 * q1[0], c1 * q1[1], 'a') + MV.arrow(G, 0, 0, c2 * q2[0], c2 * q2[1], 'g');
      s += MV.arrow(G, 0, 0, q1[0], q1[1], 'a') + MV.arrow(G, 0, 0, q2[0], q2[1], 'g') + MV.arrow(G, 0, 0, v[0], v[1], 'o');
      s += `<circle class="mv-pt o big mv-drag" data-h="0" cx="${G.sx(v[0])}" cy="${G.sy(v[1])}" r="10"/>`;
      $('.ob-g', svgEl).innerHTML = s;
      $('.ob-out', b).innerHTML = `q₁ = [${fmt(q1[0])}, ${fmt(q1[1])}], q₂ = [${fmt(q2[0])}, ${fmt(q2[1])}]<br>q₁ · q₂ = <b>${fmt(q1[0] * q2[0] + q1[1] * q2[1])}</b><br>v = [${fmt(v[0])}, ${fmt(v[1])}]<br>c₁ = v · q₁ = <b>${fmt(c1)}</b><br>c₂ = v · q₂ = <b>${fmt(c2)}</b><br>c₁² + c₂² = ${fmt(c1 * c1 + c2 * c2)} = ‖v‖² (length is kept)`;
    }
    const snap = x => Math.round(x * 4) / 4;
    MV.drag(svgEl, G, [{ set: (x, y) => { v[0] = snap(x); v[1] = snap(y); } }], draw);
    const P = Player($('.vz-p', b), t => { th = t * 5; $('[data-sl="th"]', b).value = th; $('[data-slv="th"]', b).textContent = th; draw(); }, 350);
    wireSlider(b, 'th', x => { P.pause(); th = x; draw(); });
    th = 53; draw();
    P.load(19, 0); th = 53; $('[data-sl="th"]', b).value = 53; $('[data-slv="th"]', b).textContent = 53; draw();
  };

  /* ----- Gram Schmidt in two dimensions, one move at a time ----- */
  W.gramschmidt = el => {
    const b = shell(el, 'Gram Schmidt, one move at a time', 'Drag the tips of a₁ (blue) and a₂ (orange), then press Play. Watch q₁ appear, the shadow of a₂ get removed, and q₂ come out perpendicular.');
    b.innerHTML = `<div class="mv-wrap"><div class="gs-plot"></div><div class="mv-side"><div class="mv-read gs-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const G = MV.frame(420, 420, [-5, 5], [-5, 5]);
    const a1 = [3, 1], a2 = [1, 3];
    let st = 5;
    const host = $('.gs-plot', b);
    host.innerHTML = MV.svg(G, '<g class="gs-g"></g>', 'Gram Schmidt');
    const svgEl = $('svg', host);
    function draw() {
      const n1 = Math.hypot(...a1) || 1, q1 = [a1[0] / n1, a1[1] / n1], r12 = a2[0] * q1[0] + a2[1] * q1[1];
      const sh = [r12 * q1[0], r12 * q1[1]], u = [a2[0] - sh[0], a2[1] - sh[1]], n2 = Math.hypot(...u), q2 = n2 > 1e-9 ? [u[0] / n2, u[1] / n2] : [0, 0];
      let s = MV.axes(G, { labels: false });
      s += `<circle cx="${G.sx(0)}" cy="${G.sy(0)}" r="${G.sx(1) - G.sx(0)}" class="mv-cont"/>`;
      s += MV.arrow(G, 0, 0, a1[0], a1[1], 'a') + MV.arrow(G, 0, 0, a2[0], a2[1], 'o');
      const L = ['a₁ = [' + fmt(a1[0]) + ', ' + fmt(a1[1]) + '], a₂ = [' + fmt(a2[0]) + ', ' + fmt(a2[1]) + ']'];
      if (st >= 1) { s += MV.arrow(G, 0, 0, q1[0], q1[1], 'p'); L.push(`1. q₁ = a₁ ÷ ${fmt(n1)} = <b>[${fmt(q1[0])}, ${fmt(q1[1])}]</b>`); }
      if (st >= 2) { s += MV.line(G, -6 * q1[0], -6 * q1[1], 6 * q1[0], 6 * q1[1], 'mv-v k dash') + MV.arrow(G, 0, 0, sh[0], sh[1], 'k') + MV.line(G, a2[0], a2[1], sh[0], sh[1], 'mv-v r dash'); L.push(`2. shadow of a₂ on q₁: r₁₂ = a₂ · q₁ = <b>${fmt(r12)}</b>`); }
      if (st >= 3) { s += MV.arrow(G, 0, 0, u[0], u[1], 'r'); L.push(`3. u₂ = a₂ − ${fmt(r12)} q₁ = <b>[${fmt(u[0])}, ${fmt(u[1])}]</b>`); }
      if (st >= 4) { s += MV.arrow(G, 0, 0, q2[0], q2[1], 'g'); L.push(n2 > 1e-9 ? `4. q₂ = u₂ ÷ ${fmt(n2)} = <b>[${fmt(q2[0])}, ${fmt(q2[1])}]</b>` : '4. u₂ is zero: a₂ lies on the line of a₁, so they are dependent.'); }
      if (st >= 5 && n2 > 1e-9) L.push(`5. check q₁ · q₂ = <b>${fmt(q1[0] * q2[0] + q1[1] * q2[1])}</b><br>R = [[${fmt(n1)}, ${fmt(r12)}], [0, ${fmt(n2)}]]`);
      s += `<circle class="mv-pt big mv-drag" data-h="0" cx="${G.sx(a1[0])}" cy="${G.sy(a1[1])}" r="10"/><circle class="mv-pt o big mv-drag" data-h="1" cx="${G.sx(a2[0])}" cy="${G.sy(a2[1])}" r="10"/>`;
      $('.gs-g', svgEl).innerHTML = s;
      $('.gs-out', b).innerHTML = L.join('<br>');
    }
    const snap = x => Math.round(x * 2) / 2;
    MV.drag(svgEl, G, [{ set: (x, y) => { a1[0] = snap(x); a1[1] = snap(y); } }, { set: (x, y) => { a2[0] = snap(x); a2[1] = snap(y); } }], draw);
    const P = Player($('.vz-p', b), t => { st = t; draw(); }, 1200);
    P.load(6, 5);
  };

  /* ----- the shape of xᵀAx for a symmetric 2 × 2 matrix ----- */
  W.quadform = el => {
    const b = shell(el, 'Bowl, trough or saddle', 'The colour shows xᵀAx for A = [[a, b], [b, c]]: warm for positive, cool for negative, with contour lines. Press Play to raise the cross term b and watch the bowl turn into a saddle.');
    b.innerHTML = `<div class="mv-wrap"><div class="qf-plot"></div><div class="mv-side">${slider('a', 'a', -3, 3, 2, 0.25)}${slider('b', 'b', -3, 3, 1, 0.25)}${slider('c', 'c', -3, 3, 3, 0.25)}<div class="mv-read qf-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const M = { a: 2, b: 1, c: 3 };
    const G = MV.frame(380, 380, [-2, 2], [-2, 2], 14);
    function draw() {
      const { a, b: bb, c } = M, f = (x, y) => a * x * x + 2 * bb * x * y + c * y * y;
      let s = '', N = 38, h = 4 / N;
      for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
        const x = -2 + (i + 0.5) * h, y = -2 + (j + 0.5) * h, v = f(x, y), o = Math.min(0.85, Math.abs(v) / 12 + 0.06);
        s += `<rect x="${G.sx(x - h / 2).toFixed(1)}" y="${G.sy(y + h / 2).toFixed(1)}" width="${(G.sx(h) - G.sx(0) + 0.6).toFixed(1)}" height="${(G.sy(0) - G.sy(h) + 0.6).toFixed(1)}" style="fill:var(${v >= 0 ? '--orange' : '--accent'});opacity:${o.toFixed(2)}"/>`;
      }
      const tr = a + c, dt = a * c - bb * bb, r = Math.sqrt(Math.max(0, tr * tr / 4 - dt)), l1 = tr / 2 + r, l2 = tr / 2 - r;
      [1, 3, 6].forEach(lv => [lv, -lv].forEach(L => {
        const pts = [];
        for (let k = 0; k <= 160; k++) { const t = k / 160 * 2 * Math.PI, d = [Math.cos(t), Math.sin(t)], q = f(d[0], d[1]); if (q * L > 0) { const rr = Math.sqrt(L / q); if (rr < 3) pts.push(G.sx(rr * d[0]).toFixed(1) + ',' + G.sy(rr * d[1]).toFixed(1)); else if (pts.length) { s += `<polyline class="mv-cont" points="${pts.join(' ')}"/>`; pts.length = 0; } } else if (pts.length) { s += `<polyline class="mv-cont" points="${pts.join(' ')}"/>`; pts.length = 0; } }
        if (pts.length) s += `<polyline class="mv-cont" points="${pts.join(' ')}"/>`;
      }));
      s += MV.axes(G, { labels: false, xl: 'x₁', yl: 'x₂' });
      $('.qf-plot', b).innerHTML = MV.svg(G, s, 'Heat map of a quadratic form');
      const kind = l2 > 1e-9 ? '🥣 positive definite: a bowl' : l2 > -1e-9 && l1 > 1e-9 ? '🛶 positive semi definite: a trough' : l1 < -1e-9 ? '⛰️ negative definite: an upside down bowl' : l1 > 1e-9 && l2 < -1e-9 ? '🐎 indefinite: a saddle' : 'flat or a downward trough';
      $('.qf-out', b).innerHTML = `xᵀAx = ${fmt(a)}x₁² + ${fmt(2 * bb)}x₁x₂ + ${fmt(c)}x₂²<br>leading minors: <b>${fmt(a)}</b> and <b>${fmt(dt)}</b><br>eigenvalues: <b>${fmt(l1)}</b> and <b>${fmt(l2)}</b><br>${kind}`;
    }
    const P = Player($('.vz-p', b), t => { M.b = t * 0.25; $('[data-sl="b"]', b).value = M.b; $('[data-slv="b"]', b).textContent = MV.num(M.b); draw(); }, 500);
    ['a', 'b', 'c'].forEach(k => wireSlider(b, k, v => { P.pause(); M[k] = v; draw(); }));
    P.load(13, 4);
  };

  /* ----- LU: elimination that writes its multipliers into L ----- */
  W.lusteps = el => {
    const b = shell(el, 'Elimination that remembers: A = LU', 'Edit A if you like, then press Play. Each step clears one number below the diagonal of U and writes the multiplier it used into L.');
    const start = [[2, 1, 1], [4, 3, 3], [8, 7, 9]];
    b.innerHTML = `<div class="mv-mm"><div><div class="mv-mgrid lu-a" style="grid-template-columns:repeat(3,auto)">${start.map((r, i) => r.map((v, j) => `<div class="mv-c"><input type="number" value="${v}" data-i="${i}" data-j="${j}" aria-label="A row ${i + 1} column ${j + 1}"></div>`).join('')).join('')}</div><span class="lbl">A</span></div><span class="op">=</span><div><div class="mv-mgrid lu-l" style="grid-template-columns:repeat(3,auto)"></div><span class="lbl">L</span></div><span class="op">×</span><div><div class="mv-mgrid lu-u" style="grid-template-columns:repeat(3,auto)"></div><span class="lbl">U</span></div></div><div class="mv-calc lu-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let frames = [];
    function plan() {
      const U = start.map(r => r.slice());
      b.querySelectorAll('.lu-a input').forEach(inp => { U[+inp.dataset.i][+inp.dataset.j] = +inp.value || 0; });
      const L = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
      const snap = (m, hl) => ({ L: L.map(r => r.slice()), U: U.map(r => r.slice()), m, hl });
      frames = [snap('Start: L is the identity and U is a copy of A.', null)];
      for (let c = 0; c < 2; c++) {
        if (Math.abs(U[c][c]) < 1e-12) { frames.push(snap(`The pivot in column ${c + 1} is 0, so this A needs a row swap first (PA = LU). Try other numbers.`, null)); P.load(frames.length, 0); return; }
        for (let r = c + 1; r < 3; r++) {
          const f = U[r][c] / U[c][c];
          for (let k = c; k < 3; k++) U[r][k] -= f * U[c][k];
          L[r][c] = f;
          frames.push(snap(`Row ${r + 1} of U minus ${fmt(f)} × row ${c + 1}. Write ${fmt(f)} into L at row ${r + 1}, column ${c + 1}.`, [r, c]));
        }
      }
      frames.push(snap('Done. L holds every multiplier and U is upper triangular. Multiply L by U to get A back.', null));
      P.load(frames.length, 0);
    }
    function show(t) {
      const F = frames[t], cell = (M, i, j, tri) => `<div class="mv-c ${F.hl && F.hl[0] === i && F.hl[1] === j ? 'hl' : tri ? 'ok' : ''}">${fmt(M[i][j])}</div>`;
      let l = '', u = '';
      for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) { l += cell(F.L, i, j, false); u += cell(F.U, i, j, j < i); }
      $('.lu-l', b).innerHTML = l; $('.lu-u', b).innerHTML = u;
      $('.lu-msg', b).innerHTML = `<span class="t">step ${t}</span> ${F.m}`;
    }
    const P = Player($('.vz-p', b), show, 1400);
    b.querySelectorAll('.lu-a input').forEach(inp => inp.addEventListener('change', plan));
    plan();
  };

  /* ----- least squares line with draggable points and residual squares ----- */
  W.lsq = el => {
    const b = shell(el, 'Least squares, squares and all', 'Drag any point. Press Play to build the fit: the mean point, the best line, the residuals, and the squares whose total area least squares makes as small as possible.');
    b.innerHTML = `<div class="mv-wrap"><div class="ls2-plot"></div><div class="mv-side"><div class="mv-read ls2-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const G = MV.frame(420, 380, [0, 6], [0, 7]);
    const P0 = [[1, 2], [2, 3], [3, 5], [4, 6], [5, 5.5]];
    let st = 4;
    const host = $('.ls2-plot', b);
    host.innerHTML = MV.svg(G, '<g class="ls2-g"></g>', 'Least squares fit');
    const svgEl = $('svg', host);
    function draw() {
      const n = P0.length, mx = P0.reduce((a, p) => a + p[0], 0) / n, my = P0.reduce((a, p) => a + p[1], 0) / n;
      let sxy = 0, sxx = 0; P0.forEach(p => { sxy += (p[0] - mx) * (p[1] - my); sxx += (p[0] - mx) ** 2; });
      const bb = sxx > 1e-9 ? sxy / sxx : 0, a = my - bb * mx;
      let s = MV.axes(G, { xstep: 1, ystep: 1, labels: false }), sse = 0, sr = 0, sxr = 0;
      const unit = G.sx(1) - G.sx(0), unitY = G.sy(0) - G.sy(1);
      P0.forEach(p => { const r = p[1] - (a + bb * p[0]); sse += r * r; sr += r; sxr += p[0] * r; if (st >= 4) { const side = Math.abs(r); s += `<rect class="mv-fill c2" x="${G.sx(p[0])}" y="${G.sy(Math.max(p[1], a + bb * p[0]))}" width="${side * unitY}" height="${side * unitY}"/>`; } });
      if (st >= 2) s += MV.curve(G, x => a + bb * x, 'c4');
      if (st >= 3) P0.forEach(p => { s += MV.line(G, p[0], p[1], p[0], a + bb * p[0], 'mv-res'); });
      if (st >= 1) s += MV.dot(G, mx, my, 'p', 6) + MV.text(G, mx, my, '(x̄, ȳ)', { dx: 8, dy: 16, cls: 'sm' });
      P0.forEach((p, i) => { s += `<circle class="mv-pt big mv-drag" data-h="${i}" cx="${G.sx(p[0])}" cy="${G.sy(p[1])}" r="9"/>`; });
      $('.ls2-g', svgEl).innerHTML = s;
      const L = [`${n} points`];
      if (st >= 1) L.push(`mean point (${fmt(mx)}, ${fmt(my)})`);
      if (st >= 2) L.push(`best line: y = <b>${fmt(a)}</b> + <b>${fmt(bb)}</b>x, always through the mean point`);
      if (st >= 3) L.push(`residuals add to <b>${fmt(sr)}</b> and Σ x·r = <b>${fmt(sxr)}</b>: perpendicular to both columns of X`);
      if (st >= 4) L.push(`total area of the squares (SSE) = <span class="big">${fmt(sse)}</span>`);
      $('.ls2-out', b).innerHTML = L.join('<br>') + (unit ? '' : '');
    }
    const snap = x => Math.round(x * 4) / 4;
    MV.drag(svgEl, G, P0.map(p => ({ set: (x, y) => { p[0] = snap(x); p[1] = snap(y); } })), draw);
    const P = Player($('.vz-p', b), t => { st = t; draw(); }, 1200);
    P.load(5, 4);
  };

  /* ----- the unit circle becomes an ellipse: singular values and κ ----- */
  W.condviz = el => {
    const b = shell(el, 'How round is the ellipse', 'The matrix [[a, b], [c, d]] turns the unit circle (dashed) into the ellipse. Its longest and shortest half axes are σmax and σmin. Press Play to squash the matrix towards singular and watch κ explode.');
    b.innerHTML = `<div class="mv-wrap"><div class="cv-plot"></div><div class="mv-side">${slider('a', 'a', -3, 3, 2, 0.1)}${slider('b', 'b', -3, 3, 1, 0.1)}${slider('c', 'c', -3, 3, 1, 0.1)}${slider('d', 'd', -3, 3, 2, 0.1)}<div class="mv-read cv-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const M = { a: 2, b: 1, c: 1, d: 2 };
    const G = MV.frame(400, 400, [-4, 4], [-4, 4]);
    function draw() {
      const { a, b: bb, c, d } = M;
      const p = a * a + c * c, q = a * bb + c * d, r = bb * bb + d * d, tr = p + r, dt = p * r - q * q, g = Math.sqrt(Math.max(0, tr * tr / 4 - dt));
      const s1 = Math.sqrt(tr / 2 + g), s2 = Math.sqrt(Math.max(0, tr / 2 - g)), fro = Math.sqrt(a * a + bb * bb + c * c + d * d);
      let s = MV.axes(G, { xstep: 1, ystep: 1, labels: false });
      s += `<circle cx="${G.sx(0)}" cy="${G.sy(0)}" r="${G.sx(1) - G.sx(0)}" class="mv-cont" style="stroke-dasharray:4 4"/>`;
      const pts = []; for (let k = 0; k <= 120; k++) { const t = k / 120 * 2 * Math.PI, x = Math.cos(t), y = Math.sin(t); pts.push(G.sx(a * x + bb * y).toFixed(1) + ',' + G.sy(c * x + d * y).toFixed(1)); }
      s += `<polygon class="mv-poly" points="${pts.join(' ')}"/>`;
      const ang = Math.atan2(tr / 2 + g - p, q || 1e-12), v1 = [Math.cos(ang), Math.sin(ang)], v2 = [-v1[1], v1[0]];
      const A = x => [a * x[0] + bb * x[1], c * x[0] + d * x[1]], u1 = A(v1), u2 = A(v2);
      s += MV.arrow(G, 0, 0, u1[0], u1[1], 'o') + MV.arrow(G, 0, 0, u2[0], u2[1], 'g');
      $('.cv-plot', b).innerHTML = MV.svg(G, s, 'Unit circle mapped to an ellipse');
      const k = s2 > 1e-9 ? s1 / s2 : Infinity;
      $('.cv-out', b).innerHTML = `σmax = <b>${fmt(s1)}</b> (orange), σmin = <b>${fmt(s2)}</b> (green)<br>spectral norm = σmax = ${fmt(s1)}<br>Frobenius norm = √(σmax² + σmin²) = ${fmt(fro)}<br>trace = a + d = ${fmt(a + d)}<br>condition number κ = <span class="big">${isFinite(k) ? (k > 1e4 ? k.toExponential(2) : fmt(k)) : '∞'}</span><br>` +
        (!isFinite(k) || k > 1e3 ? '⚠️ Ill conditioned: tiny input errors can be hugely amplified.' : k < 3 ? '✅ Well conditioned: nearly round.' : 'Moderately stretched.');
    }
    const P = Player($('.vz-p', b), t => { M.a = 2; M.b = 1; M.c = 1; M.d = 2 - t * 0.15; ['a', 'b', 'c', 'd'].forEach(k => { $(`[data-sl="${k}"]`, b).value = M[k]; $(`[data-slv="${k}"]`, b).textContent = MV.num(M[k]); }); draw(); }, 500);
    ['a', 'b', 'c', 'd'].forEach(k => wireSlider(b, k, v => { P.pause(); M[k] = v; draw(); }));
    P.load(11, 0);
  };

  /* ----- broadcasting two small arrays, step by step ----- */
  W.bcast = el => {
    const b = shell(el, 'Broadcasting, step by step', 'Pick two shapes and press Play. The shapes are lined up from the right, each pair is checked, size 1 axes are stretched (faded copies), and the arrays are added.');
    const CASES = {
      col_row: { A: [[1], [2], [3]], B: [[10, 20, 30, 40]] },
      mat_row: { A: [[1, 2, 3], [4, 5, 6]], B: [100, 200, 300] },
      bad: { A: [[1, 2, 3], [4, 5, 6], [7, 8, 9], [1, 1, 1]], B: [1, 2, 3, 4] },
      scalar: { A: [[1, 2], [3, 4]], B: [10] },
    };
    b.innerHTML = `<div class="vz-row">${seg('c', [['col_row', '(3, 1) + (1, 4)'], ['mat_row', '(2, 3) + (3,)'], ['bad', '(4, 3) + (4,)'], ['scalar', '(2, 2) + (1,)']], 'col_row')}</div><div class="bc-host"></div><div class="mv-calc bc-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let C = CASES.col_row;
    const shape = x => Array.isArray(x[0]) ? [x.length, x[0].length] : [x.length];
    const as2 = x => Array.isArray(x[0]) ? x : [x];
    const grid = (M, R, Cc, cls) => `<div class="mv-mgrid" style="grid-template-columns:repeat(${Cc},auto)">${Array.from({ length: R }, (_, i) => Array.from({ length: Cc }, (_, j) => { const r = M.length === 1 ? 0 : i, c = M[0].length === 1 ? 0 : j, stretched = (M.length === 1 && i > 0) || (M[0].length === 1 && j > 0); return `<div class="mv-c ${cls} ${stretched ? 'bc-copy' : ''}">${M[r] !== undefined && M[r][c] !== undefined ? M[r][c] : ''}</div>`; }).join('')).join('')}</div>`;
    function show(t) {
      const sa = shape(C.A), sb = shape(C.B), n = Math.max(sa.length, sb.length);
      const pa = Array(n - sa.length).fill('_').concat(sa), pb = Array(n - sb.length).fill('_').concat(sb);
      const res = [], why = []; let ok = true;
      for (let i = n - 1; i >= 0; i--) { const x = pa[i] === '_' ? 1 : pa[i], y = pb[i] === '_' ? 1 : pb[i]; if (x !== y && x !== 1 && y !== 1) { ok = false; why.unshift(`${pa[i]} vs ${pb[i]}: ✗ clash`); } else { res.unshift(Math.max(x, y)); why.unshift(`${pa[i]} vs ${pb[i]}: ✓ ${Math.max(x, y)}`); } }
      const A2 = as2(C.A), B2 = as2(C.B);
      const R = ok ? (res.length === 2 ? res[0] : 1) : 0, Cc = ok ? res[res.length - 1] : 0;
      let h = `<div class="mv-mm"><div>${grid(A2, A2.length, A2[0].length, '')}<span class="lbl">A ${JSON.stringify(sa).replace(/[\[\]]/g, m => m === '[' ? '(' : ')')}</span></div><span class="op">+</span><div>${grid(B2, B2.length, B2[0].length, 'sel')}<span class="lbl">B ${'(' + sb.join(', ') + (sb.length === 1 ? ',' : '') + ')'}</span></div></div>`;
      if (t >= 2 && ok) h += `<div class="mv-mm"><div>${grid(A2, R, Cc, '')}<span class="lbl">A stretched</span></div><span class="op">+</span><div>${grid(B2, R, Cc, 'sel')}<span class="lbl">B stretched</span></div>${t >= 3 ? `<span class="op">=</span><div><div class="mv-mgrid" style="grid-template-columns:repeat(${Cc},auto)">${Array.from({ length: R }, (_, i) => Array.from({ length: Cc }, (_, j) => `<div class="mv-c ok">${A2[A2.length === 1 ? 0 : i][A2[0].length === 1 ? 0 : j] + B2[B2.length === 1 ? 0 : i][B2[0].length === 1 ? 0 : j]}</div>`).join('')).join('')}</div><span class="lbl">result (${res.join(', ')})</span></div>` : ''}</div>`;
      $('.bc-host', b).innerHTML = h;
      const msgs = [`Line the shapes up from the right: (${pa.join(', ')}) over (${pb.join(', ')}).`, `Check each pair: ${why.join(' · ')}`, ok ? `Stretch the size 1 axes. Faded cells are copies, no new memory is used.` : `A pair clashes, so this is an error. Neither size is 1, nothing can stretch.`, ok ? `Add matching cells. Result shape (${res.join(', ')}).` : 'Fix: reshape B to (4, 1) so it lines up with the rows instead.'];
      $('.bc-msg', b).innerHTML = msgs.slice(0, t + 1).map((m, i) => `<span class="t">${i + 1}.</span> ${m}`).join('<br>');
    }
    const P = Player($('.vz-p', b), show, 1300);
    wireSeg(b, 'c', k => { C = CASES[k]; P.load(4, 0); });
    P.load(4, 3);
  };
})();
'''

CSS = r'''
.qf-plot .mv-svg,.cv-plot .mv-svg,.ob-plot .mv-svg,.gs-plot .mv-svg{max-height:420px}
.bc-copy{opacity:.45; border-style:dashed}
.lu-a .mv-c,.lu-l .mv-c,.lu-u .mv-c{min-width:44px}
@media (max-width:560px){ .lu-a .mv-c,.lu-l .mv-c,.lu-u .mv-c{min-width:34px; font-size:12.5px} .lu-a .mv-c input{width:32px} }
'''

T = K.topic(
    slug='decompositions', topic='decompositions', prefix='mm13', short='Decompositions', emoji='🧱',
    title='Orthogonality, Matrix Decompositions and Tensors',
    module=('🚀', 'Advanced maths for ML', 'advanced', 'The next level: matrix factorisations and tensors, Taylor series, Newton’s method and automatic differentiation, and Bayesian inference with sampling.'),
    minutes=60, added='2026-10-24',
    lead='Take linear algebra to the level real libraries use. Build orthonormal bases with Gram Schmidt, factorise matrices with QR, LU and Cholesky, see least squares as a projection, measure how fragile a problem is with the condition number, and master the shape and broadcasting rules of tensors.',
    desc='Advanced linear algebra for machine learning: orthogonal and orthonormal bases, Gram Schmidt and QR, quadratic forms and positive definite matrices, LU and Cholesky decompositions, least squares as projection and the pseudo inverse, matrix norms, trace and condition number, tensors and broadcasting.',
    summary='Orthonormal bases and orthogonal matrices, Gram Schmidt and A = QR, quadratic forms, positive definite and indefinite matrices with Sylvester’s test, LU and Cholesky with forward and back substitution, least squares as a projection with the normal equations and the pseudo inverse, Frobenius and spectral norms, trace, condition number and lost digits, tensor shapes and broadcasting.',
    keywords=['orthonormal', 'orthogonal matrix', 'gram schmidt', 'qr decomposition', 'quadratic form', 'positive definite', 'cholesky', 'lu decomposition', 'least squares', 'normal equations', 'pseudo inverse', 'frobenius norm', 'spectral norm', 'condition number', 'tensor', 'broadcasting'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
