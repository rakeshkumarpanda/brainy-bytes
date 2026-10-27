# Chapter 4: matrices, matrix multiplication, transformations, determinant and inverse,
# solving systems with elimination, rank and the normal equations.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz, vec, mat, deep

K = Kit()

JS_SHOW = 'const show = m => "[" + m.map(r => "[" + r.join(", ") + "]").join(", ") + "]";'
TS_SHOW = 'const show = (m: number[][]): string => "[" + m.map(r => "[" + r.join(", ") + "]").join(", ") + "]";'

# ---------------------------------------------------------------- programs
K.code('mat_basics', py=r'''
A = [[1, 2, 3],
     [4, 5, 6]]                       # 2 rows, 3 columns
B = [[10, 20, 30],
     [40, 50, 60]]
rows, cols = len(A), len(A[0])
print("shape of A:", rows, "x", cols)
print("A[1][2] =", A[1][2])          # row 2, column 3 when counting from 1
S = [[A[i][j] + B[i][j] for j in range(cols)] for i in range(rows)]
print("A + B =", S)
D = [[3 * A[i][j] for j in range(cols)] for i in range(rows)]
print("3A =", D)
At = [[A[i][j] for i in range(rows)] for j in range(cols)]   # rows become columns
print("A transposed =", At)
''', js=r'''
const A = [[1, 2, 3],
           [4, 5, 6]];                // 2 rows, 3 columns
const B = [[10, 20, 30],
           [40, 50, 60]];
const rows = A.length, cols = A[0].length;
''' + JS_SHOW + r'''
console.log("shape of A:", rows, "x", cols);
console.log("A[1][2] =", A[1][2]);   // row 2, column 3 when counting from 1
const S = A.map((r, i) => r.map((v, j) => v + B[i][j]));
console.log("A + B =", show(S));
const D = A.map(r => r.map(v => 3 * v));
console.log("3A =", show(D));
const At = A[0].map((_, j) => A.map(r => r[j]));   // rows become columns
console.log("A transposed =", show(At));
''', ts=r'''
const A: number[][] = [[1, 2, 3],
                       [4, 5, 6]];    // 2 rows, 3 columns
const B: number[][] = [[10, 20, 30],
                       [40, 50, 60]];
const rows: number = A.length, cols: number = A[0].length;
''' + TS_SHOW + r'''
console.log("shape of A:", rows, "x", cols);
console.log("A[1][2] =", A[1][2]);   // row 2, column 3 when counting from 1
const S: number[][] = A.map((r, i) => r.map((v, j) => v + B[i][j]));
console.log("A + B =", show(S));
const D: number[][] = A.map(r => r.map(v => 3 * v));
console.log("3A =", show(D));
const At: number[][] = A[0].map((_, j) => A.map(r => r[j]));   // rows become columns
console.log("A transposed =", show(At));
''', java=r'''
import java.util.Arrays;

public class MatBasics {
    public static void main(String[] args) {
        int[][] A = {{1, 2, 3},
                     {4, 5, 6}};            // 2 rows, 3 columns
        int[][] B = {{10, 20, 30},
                     {40, 50, 60}};
        int rows = A.length, cols = A[0].length;
        System.out.println("shape of A: " + rows + " x " + cols);
        System.out.println("A[1][2] = " + A[1][2]);   // row 2, column 3 when counting from 1
        int[][] S = new int[rows][cols], D = new int[rows][cols], At = new int[cols][rows];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                S[i][j] = A[i][j] + B[i][j];
                D[i][j] = 3 * A[i][j];
                At[j][i] = A[i][j];                   // rows become columns
            }
        }
        System.out.println("A + B = " + Arrays.deepToString(S));
        System.out.println("3A = " + Arrays.deepToString(D));
        System.out.println("A transposed = " + Arrays.deepToString(At));
    }
}
''')

K.code('matmul', py=r'''
def matmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    assert len(A[0]) == m, "inner sizes must match"
    C = [[0] * p for _ in range(n)]
    for i in range(n):                # each row of A
        for j in range(p):            # each column of B
            for k in range(m):        # walk along both together
                C[i][j] += A[i][k] * B[k][j]
    return C


A = [[1, 2],
     [3, 4]]
B = [[5, 6],
     [7, 8]]
print("AB =", matmul(A, B))
print("BA =", matmul(B, A))
''', js=r'''
function matmul(A, B) {
  const n = A.length, m = B.length, p = B[0].length;
  if (A[0].length !== m) throw new Error("inner sizes must match");
  const C = Array.from({ length: n }, () => new Array(p).fill(0));
  for (let i = 0; i < n; i++) {       // each row of A
    for (let j = 0; j < p; j++) {     // each column of B
      for (let k = 0; k < m; k++) {   // walk along both together
        C[i][j] += A[i][k] * B[k][j];
      }
    }
  }
  return C;
}

''' + JS_SHOW + r'''
const A = [[1, 2],
           [3, 4]];
const B = [[5, 6],
           [7, 8]];
console.log("AB =", show(matmul(A, B)));
console.log("BA =", show(matmul(B, A)));
''', ts=r'''
function matmul(A: number[][], B: number[][]): number[][] {
  const n: number = A.length, m: number = B.length, p: number = B[0].length;
  if (A[0].length !== m) throw new Error("inner sizes must match");
  const C: number[][] = Array.from({ length: n }, () => new Array<number>(p).fill(0));
  for (let i = 0; i < n; i++) {       // each row of A
    for (let j = 0; j < p; j++) {     // each column of B
      for (let k = 0; k < m; k++) {   // walk along both together
        C[i][j] += A[i][k] * B[k][j];
      }
    }
  }
  return C;
}

''' + TS_SHOW + r'''
const A: number[][] = [[1, 2],
                       [3, 4]];
const B: number[][] = [[5, 6],
                       [7, 8]];
console.log("AB =", show(matmul(A, B)));
console.log("BA =", show(matmul(B, A)));
''', java=r'''
import java.util.Arrays;

public class MatMul {
    static int[][] matmul(int[][] A, int[][] B) {
        int n = A.length, m = B.length, p = B[0].length;
        if (A[0].length != m) throw new IllegalArgumentException("inner sizes must match");
        int[][] C = new int[n][p];
        for (int i = 0; i < n; i++) {           // each row of A
            for (int j = 0; j < p; j++) {       // each column of B
                for (int k = 0; k < m; k++) {   // walk along both together
                    C[i][j] += A[i][k] * B[k][j];
                }
            }
        }
        return C;
    }

    public static void main(String[] args) {
        int[][] A = {{1, 2},
                     {3, 4}};
        int[][] B = {{5, 6},
                     {7, 8}};
        System.out.println("AB = " + Arrays.deepToString(matmul(A, B)));
        System.out.println("BA = " + Arrays.deepToString(matmul(B, A)));
    }
}
''')

K.code('layer', py=r'''
# one dense layer: 3 inputs -> 2 outputs, then ReLU
W = [[0.2, -0.5, 1.0],
     [1.5, 0.3, -0.4]]
b = [0.1, -0.2]
x = [2.0, 1.0, 3.0]
z = []
for i in range(len(W)):
    s = b[i]
    for j in range(len(x)):
        s += W[i][j] * x[j]          # row i of W dotted with x
    z.append(s)
a = [max(0.0, v) for v in z]
print("z = Wx + b =", [f"{v:.2f}" for v in z])
print("ReLU(z)    =", [f"{v:.2f}" for v in a])
''', js=r'''
// one dense layer: 3 inputs -> 2 outputs, then ReLU
const W = [[0.2, -0.5, 1.0],
           [1.5, 0.3, -0.4]];
const b = [0.1, -0.2];
const x = [2.0, 1.0, 3.0];
const z = [];
for (let i = 0; i < W.length; i++) {
  let s = b[i];
  for (let j = 0; j < x.length; j++) {
    s += W[i][j] * x[j];             // row i of W dotted with x
  }
  z.push(s);
}
const a = z.map(v => Math.max(0, v));
const f = v => "[" + v.map(t => `'${t.toFixed(2)}'`).join(", ") + "]";
console.log("z = Wx + b =", f(z));
console.log("ReLU(z)    =", f(a));
''', ts=r'''
// one dense layer: 3 inputs -> 2 outputs, then ReLU
const W: number[][] = [[0.2, -0.5, 1.0],
                       [1.5, 0.3, -0.4]];
const b: number[] = [0.1, -0.2];
const x: number[] = [2.0, 1.0, 3.0];
const z: number[] = [];
for (let i = 0; i < W.length; i++) {
  let s: number = b[i];
  for (let j = 0; j < x.length; j++) {
    s += W[i][j] * x[j];             // row i of W dotted with x
  }
  z.push(s);
}
const a: number[] = z.map(v => Math.max(0, v));
const f = (v: number[]): string => "[" + v.map(t => `'${t.toFixed(2)}'`).join(", ") + "]";
console.log("z = Wx + b =", f(z));
console.log("ReLU(z)    =", f(a));
''', java=r'''
public class Layer {
    static String f(double[] v) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < v.length; i++) sb.append(i > 0 ? ", " : "").append("'").append(String.format("%.2f", v[i])).append("'");
        return sb.append("]").toString();
    }

    public static void main(String[] args) {
        // one dense layer: 3 inputs -> 2 outputs, then ReLU
        double[][] W = {{0.2, -0.5, 1.0},
                        {1.5, 0.3, -0.4}};
        double[] b = {0.1, -0.2};
        double[] x = {2.0, 1.0, 3.0};
        double[] z = new double[W.length], a = new double[W.length];
        for (int i = 0; i < W.length; i++) {
            double s = b[i];
            for (int j = 0; j < x.length; j++) {
                s += W[i][j] * x[j];             // row i of W dotted with x
            }
            z[i] = s;
            a[i] = Math.max(0.0, s);
        }
        System.out.println("z = Wx + b = " + f(z));
        System.out.println("ReLU(z)    = " + f(a));
    }
}
''')

K.code('inverse', py=r'''
A = [[4, 7],
     [2, 6]]
a, b = A[0]
c, d = A[1]
det = a * d - b * c                   # how much A scales area
print("det =", det)
inv = [[d / det, -b / det],
       [-c / det, a / det]]           # swap a and d, negate b and c, divide by det
def r2(m):                            # two decimals, and -0.00 shown as 0.00
    return "[" + ", ".join("[" + ", ".join(f"{round(v, 2) + 0.0:.2f}" for v in row) + "]" for row in m) + "]"
print("inverse =", r2(inv))
I = [[sum(A[i][k] * inv[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
print("A times inverse =", r2(I))
''', js=r'''
const A = [[4, 7],
           [2, 6]];
const [a, b] = A[0];
const [c, d] = A[1];
const det = a * d - b * c;            // how much A scales area
console.log("det =", det);
const inv = [[d / det, -b / det],
             [-c / det, a / det]];    // swap a and d, negate b and c, divide by det
const r2 = m => "[" + m.map(r => "[" + r.map(v => (Math.round(v * 100) / 100 + 0).toFixed(2)).join(", ") + "]").join(", ") + "]";
console.log("inverse =", r2(inv));
const I = [0, 1].map(i => [0, 1].map(j => A[i][0] * inv[0][j] + A[i][1] * inv[1][j]));
console.log("A times inverse =", r2(I));
''', ts=r'''
const A: number[][] = [[4, 7],
                       [2, 6]];
const [a, b] = A[0];
const [c, d] = A[1];
const det: number = a * d - b * c;    // how much A scales area
console.log("det =", det);
const inv: number[][] = [[d / det, -b / det],
                         [-c / det, a / det]];   // swap a and d, negate b and c, divide by det
const r2 = (m: number[][]): string => "[" + m.map(r => "[" + r.map(v => (Math.round(v * 100) / 100 + 0).toFixed(2)).join(", ") + "]").join(", ") + "]";
console.log("inverse =", r2(inv));
const I: number[][] = [0, 1].map(i => [0, 1].map(j => A[i][0] * inv[0][j] + A[i][1] * inv[1][j]));
console.log("A times inverse =", r2(I));
''', java=r'''
public class Inverse {
    static String r2(double[][] m) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < m.length; i++) {
            sb.append(i > 0 ? ", [" : "[");
            for (int j = 0; j < m[i].length; j++) sb.append(j > 0 ? ", " : "").append(String.format("%.2f", Math.round(m[i][j] * 100) / 100.0 + 0.0));
            sb.append("]");
        }
        return sb.append("]").toString();
    }

    public static void main(String[] args) {
        double[][] A = {{4, 7},
                        {2, 6}};
        double a = A[0][0], b = A[0][1], c = A[1][0], d = A[1][1];
        int det = (int) (a * d - b * c);          // how much A scales area
        System.out.println("det = " + det);
        double[][] inv = {{d / det, -b / det},
                          {-c / det, a / det}};   // swap a and d, negate b and c, divide by det
        System.out.println("inverse = " + r2(inv));
        double[][] I = new double[2][2];
        for (int i = 0; i < 2; i++)
            for (int j = 0; j < 2; j++)
                I[i][j] = A[i][0] * inv[0][j] + A[i][1] * inv[1][j];
        System.out.println("A times inverse = " + r2(I));
    }
}
''')

K.code('gauss', py=r'''
# x + y + z = 6,  2y + 5z = -4,  2x + 5y - z = 27
M = [[1, 1, 1, 6],
     [0, 2, 5, -4],
     [2, 5, -1, 27]]
n = 3
for col in range(n):                       # clear below each pivot
    for row in range(col + 1, n):
        f = M[row][col] / M[col][col]
        M[row] = [M[row][k] - f * M[col][k] for k in range(n + 1)]
x = [0.0] * n
for i in range(n - 1, -1, -1):             # back substitution, last row first
    s = M[i][n] - sum(M[i][k] * x[k] for k in range(i + 1, n))
    x[i] = s / M[i][i]
print("x, y, z =", [round(v, 6) for v in x])
''', js=r'''
// x + y + z = 6,  2y + 5z = -4,  2x + 5y - z = 27
const M = [[1, 1, 1, 6],
           [0, 2, 5, -4],
           [2, 5, -1, 27]];
const n = 3;
for (let col = 0; col < n; col++) {        // clear below each pivot
  for (let row = col + 1; row < n; row++) {
    const f = M[row][col] / M[col][col];
    M[row] = M[row].map((v, k) => v - f * M[col][k]);
  }
}
const x = new Array(n).fill(0);
for (let i = n - 1; i >= 0; i--) {         // back substitution, last row first
  let s = M[i][n];
  for (let k = i + 1; k < n; k++) s -= M[i][k] * x[k];
  x[i] = s / M[i][i];
}
console.log("x, y, z =", "[" + x.map(v => (Math.round(v * 1e6) / 1e6).toFixed(1)).join(", ") + "]");
''', ts=r'''
// x + y + z = 6,  2y + 5z = -4,  2x + 5y - z = 27
const M: number[][] = [[1, 1, 1, 6],
                       [0, 2, 5, -4],
                       [2, 5, -1, 27]];
const n: number = 3;
for (let col = 0; col < n; col++) {        // clear below each pivot
  for (let row = col + 1; row < n; row++) {
    const f: number = M[row][col] / M[col][col];
    M[row] = M[row].map((v, k) => v - f * M[col][k]);
  }
}
const x: number[] = new Array<number>(n).fill(0);
for (let i = n - 1; i >= 0; i--) {         // back substitution, last row first
  let s: number = M[i][n];
  for (let k = i + 1; k < n; k++) s -= M[i][k] * x[k];
  x[i] = s / M[i][i];
}
console.log("x, y, z =", "[" + x.map(v => (Math.round(v * 1e6) / 1e6).toFixed(1)).join(", ") + "]");
''', java=r'''
public class Gauss {
    public static void main(String[] args) {
        // x + y + z = 6,  2y + 5z = -4,  2x + 5y - z = 27
        double[][] M = {{1, 1, 1, 6},
                        {0, 2, 5, -4},
                        {2, 5, -1, 27}};
        int n = 3;
        for (int col = 0; col < n; col++) {            // clear below each pivot
            for (int row = col + 1; row < n; row++) {
                double f = M[row][col] / M[col][col];
                for (int k = 0; k <= n; k++) M[row][k] -= f * M[col][k];
            }
        }
        double[] x = new double[n];
        for (int i = n - 1; i >= 0; i--) {             // back substitution, last row first
            double s = M[i][n];
            for (int k = i + 1; k < n; k++) s -= M[i][k] * x[k];
            x[i] = s / M[i][i];
        }
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < n; i++) sb.append(i > 0 ? ", " : "").append(Math.round(x[i] * 1e6) / 1e6);
        System.out.println("x, y, z = " + sb.append("]"));
    }
}
''')

# ---------------------------------------------------------------- practice programs
K.code('p_shapes', py=r'''
A = [[1, 0, 2],
     [-1, 3, 1]]          # 2 x 3
B = [[3, 1],
     [2, 1],
     [1, 0]]              # 3 x 2
C = [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(2)] for i in range(2)]
print("A is 2x3, B is 3x2, so AB is 2x2:", C)
D = [[sum(B[i][k] * A[k][j] for k in range(2)) for j in range(3)] for i in range(3)]
print("BA is 3x3:", D)
''', js=r'''
const A = [[1, 0, 2],
           [-1, 3, 1]];   // 2 x 3
const B = [[3, 1],
           [2, 1],
           [1, 0]];       // 3 x 2
''' + JS_SHOW + r'''
const C = [0, 1].map(i => [0, 1].map(j => [0, 1, 2].reduce((s, k) => s + A[i][k] * B[k][j], 0)));
console.log("A is 2x3, B is 3x2, so AB is 2x2:", show(C));
const D = [0, 1, 2].map(i => [0, 1, 2].map(j => [0, 1].reduce((s, k) => s + B[i][k] * A[k][j], 0)));
console.log("BA is 3x3:", show(D));
''', ts=r'''
const A: number[][] = [[1, 0, 2],
                       [-1, 3, 1]];   // 2 x 3
const B: number[][] = [[3, 1],
                       [2, 1],
                       [1, 0]];       // 3 x 2
''' + TS_SHOW + r'''
const C: number[][] = [0, 1].map(i => [0, 1].map(j => [0, 1, 2].reduce((s, k) => s + A[i][k] * B[k][j], 0)));
console.log("A is 2x3, B is 3x2, so AB is 2x2:", show(C));
const D: number[][] = [0, 1, 2].map(i => [0, 1, 2].map(j => [0, 1].reduce((s, k) => s + B[i][k] * A[k][j], 0)));
console.log("BA is 3x3:", show(D));
''', java=r'''
import java.util.Arrays;

public class PracticeShapes {
    public static void main(String[] args) {
        int[][] A = {{1, 0, 2},
                     {-1, 3, 1}};   // 2 x 3
        int[][] B = {{3, 1},
                     {2, 1},
                     {1, 0}};       // 3 x 2
        int[][] C = new int[2][2], D = new int[3][3];
        for (int i = 0; i < 2; i++)
            for (int j = 0; j < 2; j++)
                for (int k = 0; k < 3; k++) C[i][j] += A[i][k] * B[k][j];
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
                for (int k = 0; k < 2; k++) D[i][j] += B[i][k] * A[k][j];
        System.out.println("A is 2x3, B is 3x2, so AB is 2x2: " + Arrays.deepToString(C));
        System.out.println("BA is 3x3: " + Arrays.deepToString(D));
    }
}
''')

K.code('p_rotate', py=r'''
import math


def rotate(points, degrees):
    t = math.radians(degrees)
    R = [[math.cos(t), -math.sin(t)],
         [math.sin(t), math.cos(t)]]
    return [[R[0][0] * x + R[0][1] * y, R[1][0] * x + R[1][1] * y] for x, y in points]


square = [[1, 0], [1, 1], [0, 1]]
for deg in [90, 30]:
    out = rotate(square, deg)
    print(deg, "degrees:", " ".join(f"({x:.3f}, {y:.3f})" for x, y in out))
''', js=r'''
function rotate(points, degrees) {
  const t = degrees * Math.PI / 180;
  const R = [[Math.cos(t), -Math.sin(t)],
             [Math.sin(t), Math.cos(t)]];
  return points.map(([x, y]) => [R[0][0] * x + R[0][1] * y, R[1][0] * x + R[1][1] * y]);
}

const square = [[1, 0], [1, 1], [0, 1]];
const fx = v => (Math.abs(v) < 5e-4 ? 0 : v).toFixed(3);
for (const deg of [90, 30]) {
  const out = rotate(square, deg);
  console.log(deg, "degrees:", out.map(([x, y]) => `(${fx(x)}, ${fx(y)})`).join(" "));
}
''', ts=r'''
function rotate(points: number[][], degrees: number): number[][] {
  const t: number = degrees * Math.PI / 180;
  const R: number[][] = [[Math.cos(t), -Math.sin(t)],
                         [Math.sin(t), Math.cos(t)]];
  return points.map(([x, y]) => [R[0][0] * x + R[0][1] * y, R[1][0] * x + R[1][1] * y]);
}

const square: number[][] = [[1, 0], [1, 1], [0, 1]];
const fx = (v: number): string => (Math.abs(v) < 5e-4 ? 0 : v).toFixed(3);
for (const deg of [90, 30]) {
  const out: number[][] = rotate(square, deg);
  console.log(deg, "degrees:", out.map(([x, y]) => `(${fx(x)}, ${fx(y)})`).join(" "));
}
''', java=r'''
public class PracticeRotate {
    static String fx(double v) { return String.format("%.3f", Math.abs(v) < 5e-4 ? 0.0 : v); }

    public static void main(String[] args) {
        double[][] square = {{1, 0}, {1, 1}, {0, 1}};
        for (int deg : new int[]{90, 30}) {
            double t = Math.toRadians(deg);
            double[][] R = {{Math.cos(t), -Math.sin(t)},
                            {Math.sin(t), Math.cos(t)}};
            StringBuilder sb = new StringBuilder();
            for (double[] p : square) {
                double x = R[0][0] * p[0] + R[0][1] * p[1], y = R[1][0] * p[0] + R[1][1] * p[1];
                sb.append(sb.length() > 0 ? " " : "").append("(").append(fx(x)).append(", ").append(fx(y)).append(")");
            }
            System.out.println(deg + " degrees: " + sb);
        }
    }
}
''')

K.code('p_regression', py=r'''
# fit y = w*x + c to points with the normal equations (X^T X) beta = X^T y
xs = [1, 2, 3, 4, 5]
ys = [2.2, 4.1, 6.1, 7.9, 10.2]
n = len(xs)
Sx, Sy = sum(xs), sum(ys)
Sxx = sum(x * x for x in xs)
Sxy = sum(x * y for x, y in zip(xs, ys))
# X^T X = [[Sxx, Sx], [Sx, n]] and X^T y = [Sxy, Sy]
det = Sxx * n - Sx * Sx
w = (n * Sxy - Sx * Sy) / det
c = (Sxx * Sy - Sx * Sxy) / det
print(f"X^T X = [[{Sxx}, {Sx}], [{Sx}, {n}]], det = {det}")
print(f"best line: y = {w:.3f}x + {c:.3f}")
print(f"prediction at x = 6: {w * 6 + c:.3f}")
''', js=r'''
// fit y = w*x + c to points with the normal equations (X^T X) beta = X^T y
const xs = [1, 2, 3, 4, 5];
const ys = [2.2, 4.1, 6.1, 7.9, 10.2];
const n = xs.length;
const Sx = xs.reduce((s, x) => s + x, 0), Sy = ys.reduce((s, y) => s + y, 0);
const Sxx = xs.reduce((s, x) => s + x * x, 0);
const Sxy = xs.reduce((s, x, i) => s + x * ys[i], 0);
// X^T X = [[Sxx, Sx], [Sx, n]] and X^T y = [Sxy, Sy]
const det = Sxx * n - Sx * Sx;
const w = (n * Sxy - Sx * Sy) / det;
const c = (Sxx * Sy - Sx * Sxy) / det;
console.log(`X^T X = [[${Sxx}, ${Sx}], [${Sx}, ${n}]], det = ${det}`);
console.log(`best line: y = ${w.toFixed(3)}x + ${c.toFixed(3)}`);
console.log(`prediction at x = 6: ${(w * 6 + c).toFixed(3)}`);
''', ts=r'''
// fit y = w*x + c to points with the normal equations (X^T X) beta = X^T y
const xs: number[] = [1, 2, 3, 4, 5];
const ys: number[] = [2.2, 4.1, 6.1, 7.9, 10.2];
const n: number = xs.length;
const Sx: number = xs.reduce((s, x) => s + x, 0), Sy: number = ys.reduce((s, y) => s + y, 0);
const Sxx: number = xs.reduce((s, x) => s + x * x, 0);
const Sxy: number = xs.reduce((s, x, i) => s + x * ys[i], 0);
// X^T X = [[Sxx, Sx], [Sx, n]] and X^T y = [Sxy, Sy]
const det: number = Sxx * n - Sx * Sx;
const w: number = (n * Sxy - Sx * Sy) / det;
const c: number = (Sxx * Sy - Sx * Sxy) / det;
console.log(`X^T X = [[${Sxx}, ${Sx}], [${Sx}, ${n}]], det = ${det}`);
console.log(`best line: y = ${w.toFixed(3)}x + ${c.toFixed(3)}`);
console.log(`prediction at x = 6: ${(w * 6 + c).toFixed(3)}`);
''', java=r'''
public class PracticeRegression {
    public static void main(String[] args) {
        // fit y = w*x + c to points with the normal equations (X^T X) beta = X^T y
        int[] xs = {1, 2, 3, 4, 5};
        double[] ys = {2.2, 4.1, 6.1, 7.9, 10.2};
        int n = xs.length, Sx = 0, Sxx = 0;
        double Sy = 0, Sxy = 0;
        for (int i = 0; i < n; i++) {
            Sx += xs[i];
            Sy += ys[i];
            Sxx += xs[i] * xs[i];
            Sxy += xs[i] * ys[i];
        }
        // X^T X = [[Sxx, Sx], [Sx, n]] and X^T y = [Sxy, Sy]
        int det = Sxx * n - Sx * Sx;
        double w = (n * Sxy - Sx * Sy) / det;
        double c = (Sxx * Sy - Sx * Sxy) / det;
        System.out.println("X^T X = [[" + Sxx + ", " + Sx + "], [" + Sx + ", " + n + "]], det = " + det);
        System.out.println(String.format("best line: y = %.3fx + %.3f", w, c));
        System.out.println(String.format("prediction at x = 6: %.3f", w * 6 + c));
    }
}
''')

K.code('p_power', py=r'''
def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


# a city: each year 10% of city people move out, 5% of village people move in
T = [[0.90, 0.05],
     [0.10, 0.95]]
state = [[600], [400]]           # people in city, village (thousands)
for year in range(1, 4):
    state = matmul(T, state)
    print(f"year {year}: city {state[0][0]:.1f}, village {state[1][0]:.1f}")
''', js=r'''
function matmul(A, B) {
  return A.map(row => B[0].map((_, j) => row.reduce((s, v, k) => s + v * B[k][j], 0)));
}

// a city: each year 10% of city people move out, 5% of village people move in
const T = [[0.90, 0.05],
           [0.10, 0.95]];
let state = [[600], [400]];      // people in city, village (thousands)
for (let year = 1; year <= 3; year++) {
  state = matmul(T, state);
  console.log(`year ${year}: city ${state[0][0].toFixed(1)}, village ${state[1][0].toFixed(1)}`);
}
''', ts=r'''
function matmul(A: number[][], B: number[][]): number[][] {
  return A.map(row => B[0].map((_, j) => row.reduce((s, v, k) => s + v * B[k][j], 0)));
}

// a city: each year 10% of city people move out, 5% of village people move in
const T: number[][] = [[0.90, 0.05],
                       [0.10, 0.95]];
let state: number[][] = [[600], [400]];   // people in city, village (thousands)
for (let year = 1; year <= 3; year++) {
  state = matmul(T, state);
  console.log(`year ${year}: city ${state[0][0].toFixed(1)}, village ${state[1][0].toFixed(1)}`);
}
''', java=r'''
public class PracticePower {
    static double[][] matmul(double[][] A, double[][] B) {
        double[][] C = new double[A.length][B[0].length];
        for (int i = 0; i < A.length; i++)
            for (int j = 0; j < B[0].length; j++)
                for (int k = 0; k < B.length; k++) C[i][j] += A[i][k] * B[k][j];
        return C;
    }

    public static void main(String[] args) {
        // a city: each year 10% of city people move out, 5% of village people move in
        double[][] T = {{0.90, 0.05},
                        {0.10, 0.95}};
        double[][] state = {{600}, {400}};   // people in city, village (thousands)
        for (int year = 1; year <= 3; year++) {
            state = matmul(T, state);
            System.out.println(String.format("year %d: city %.1f, village %.1f", year, state[0][0], state[1][0]));
        }
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('what', '🔢', 'What a matrix is', f'''
<p>A <b>matrix</b> is a rectangle of numbers arranged in rows and columns. Its <b>shape</b> is written rows × columns, so a matrix with 2 rows and 3 columns is 2 × 3. The entry in row i and column j is written aᵢⱼ.</p>
<p style="text-align:center">A = {mat([[1, 2, 3], [4, 5, 6]])} &nbsp; is 2 × 3, and a₂₃ = 6</p>
<div class="grid2">
<div class="box"><h4>📊 A dataset</h4><p>Each <b>row</b> is one example (a house, a customer) and each <b>column</b> is one feature (area, age). 1000 houses with 5 features make a 1000 × 5 matrix, usually called X.</p></div>
<div class="box"><h4>🖼️ A picture</h4><p>A grey photo is a matrix of brightness values, one per pixel. A colour photo is three matrices stacked (red, green, blue), which is called a <b>tensor</b>.</p></div>
</div>
{table(['Object', 'Shape', 'Example'], [
        ['Scalar', 'a single number', 'learning rate 0.01'],
        ['Vector', 'n numbers', 'one house [3, 120, 15]'],
        ['Matrix', 'm × n', 'all houses, or the weights of one layer'],
        ['Tensor', 'three or more directions', 'a batch of colour images: 32 × 3 × 224 × 224'],
    ])}
{life('A school timetable, a cinema seating plan and an Excel sheet are all matrices. Row 5, seat 12 is just a₅,₁₂.')}
{ml('In code, NumPy arrays and PyTorch tensors are matrices and their bigger cousins. The single most common bug in machine learning code is a shape mismatch, so always know the shape of every matrix.')}
''', kw=['matrix', 'shape', 'rows', 'columns', 'entry', 'tensor', 'dataset matrix']),

    part('basic', '🧩', 'Adding, scaling and transposing', f'''
<p>Matrices of the <b>same shape</b> add entry by entry. Multiplying by a number scales every entry. The <b>transpose</b> Aᵀ flips a matrix over its diagonal, so rows become columns and a 2 × 3 matrix becomes 3 × 2.</p>
{fxs(fx('Addition', '(A + B)ᵢⱼ = aᵢⱼ + bᵢⱼ', 'Only for equal shapes.'),
         fx('Transpose', '(Aᵀ)ᵢⱼ = aⱼᵢ', f'{mat([[1, 2, 3], [4, 5, 6]])}ᵀ = {mat([[1, 4], [2, 5], [3, 6]])}'),
         fx('Element wise (Hadamard) product', '(A ⊙ B)ᵢⱼ = aᵢⱼ × bᵢⱼ', 'Multiply matching entries. This is NOT matrix multiplication.'))}
{code('mat_basics', 'Shape, indexing, adding, scaling and transposing')}
<div class="exam">In NumPy, <code>A * B</code> is the element wise product and <code>A @ B</code> is matrix multiplication. Mixing them up gives wrong answers without any error message when the shapes happen to fit.</div>
{trick('Transpose twice and you are back where you started: (Aᵀ)ᵀ = A. And for products the order reverses: (AB)ᵀ = BᵀAᵀ, like taking off socks and shoes in the reverse order.')}
''', kw=['matrix addition', 'scalar multiplication', 'transpose', 'hadamard product', 'element wise product']),

    part('matmul', '🎯', 'Matrix multiplication, step by step', f'''
<p>To multiply A by B, each entry of the answer is a <b>dot product</b>: row i of A with column j of B. Walk along the row and down the column together, multiply the pairs, and add.</p>
{fxs(fx('Matrix product', '(AB)ᵢⱼ = Σₖ aᵢₖ bₖⱼ', 'Row i of A dotted with column j of B.'),
         fx('Shape rule', '(m × <b>n</b>) · (<b>n</b> × p) = m × p', 'The inner sizes must match. The outer sizes give the answer shape.'))}
{viz('matmul')}
{worked('Multiply [[1, 2], [3, 4]] by [[5, 6], [7, 8]]', [
        'Top left = row 1 · column 1: <span class="eq">1 × 5 + 2 × 7 = 5 + 14 = 19</span>',
        'Top right = row 1 · column 2: <span class="eq">1 × 6 + 2 × 8 = 6 + 16 = 22</span>',
        'Bottom left = row 2 · column 1: <span class="eq">3 × 5 + 4 × 7 = 15 + 28 = 43</span>',
        'Bottom right = row 2 · column 2: <span class="eq">3 × 6 + 4 × 8 = 18 + 32 = 50</span>',
        f'Answer: {mat([[19, 22], [43, 50]])}'])}
{code('matmul', 'Matrix multiplication with three loops')}
{table(['Property', 'True or false', 'Why it matters'], [
        ['AB = BA', '<b>false</b> in general', 'order matters. The program above shows AB and BA are different'],
        ['(AB)C = A(BC)', 'true (associative)', 'you can group a chain of layers in any way you like'],
        ['A(B + C) = AB + AC', 'true (distributive)', 'used all the time in derivations'],
        ['cost of n × n times n × n', 'about n³ multiplications', 'why big models need GPUs'],
    ])}
{trick('"Row times column, row times column". Put your left index finger on a row of A and your right index finger on a column of B. Move both fingers together, multiplying as you go.')}
{life('A café sells 3 items at fixed prices. A matrix of how many items each branch sold, times the price vector, gives each branch revenue in one step. That is a matrix times a vector.')}
''', kw=['matrix multiplication', 'matmul', 'row times column', 'shape rule', 'not commutative', 'associative']),

    part('transform', '🔄', 'A matrix is a transformation', f'''
<p>Multiplying a vector by a matrix moves it. Every 2 × 2 matrix stretches, squashes, rotates, shears or flips the whole plane, and keeps straight lines straight. That is why it is called a <b>linear transformation</b>.</p>
<p>The columns tell the whole story: the first column is where [1, 0] lands and the second column is where [0, 1] lands. Everything else follows.</p>
{viz('transform')}
{table(['Matrix', 'What it does'], [
        [mat([[2, 0], [0, 2]]), 'scales everything by 2'],
        [mat([[0, -1], [1, 0]]), 'rotates by 90° anticlockwise'],
        [mat([[1, 1], [0, 1]]), 'shears sideways, like pushing the top of a stack of cards'],
        [mat([[1, 0], [0, -1]]), 'reflects in the x axis'],
        [mat([['cos θ', '−sin θ'], ['sin θ', 'cos θ']]), 'rotates by any angle θ'],
    ])}
{code('layer', 'One neural network layer is W x + b')}
{ml('A dense (fully connected) layer computes z = Wx + b, a matrix times a vector, then applies an activation like ReLU. With a batch of 64 inputs stacked as rows of X, the whole batch is done at once: Z = XWᵀ + b. Image augmentation uses rotation and shear matrices to make new training pictures.')}
''', kw=['linear transformation', 'rotation matrix', 'scaling', 'shear', 'reflection', 'dense layer', 'Wx + b']),

    part('inverse', '↩️', 'Identity, determinant and inverse', f'''
<p>The <b>identity matrix</b> I has 1s on its diagonal and 0s elsewhere. It does nothing: AI = IA = A, just like multiplying by 1. The <b>inverse</b> A⁻¹ undoes A: A⁻¹A = I.</p>
{fxs(fx('2 × 2 determinant', f'det {mat([["a", "b"], ["c", "d"]])} = ad − bc', 'How much A scales area. A negative sign means it also flips the plane over.'),
         fx('2 × 2 inverse', f'A⁻¹ = {frac(1, "ad − bc")} {mat([["d", "−b"], ["−c", "a"]])}', 'Swap a and d, change the signs of b and c, divide by the determinant.'))}
{worked('Invert A = [[4, 7], [2, 6]]', [
        'Determinant: <span class="eq">4 × 6 − 7 × 2 = 24 − 14 = 10</span>. Not zero, so the inverse exists.',
        'Swap a and d, negate b and c: <span class="eq">[[6, −7], [−2, 4]]</span>',
        'Divide by 10: <span class="eq">A⁻¹ = [[0.6, −0.7], [−0.2, 0.4]]</span>',
        'Check one entry of A·A⁻¹: row 1 · column 1 = <span class="eq">4 × 0.6 + 7 × (−0.2) = 2.4 − 1.4 = 1</span> ✔'])}
{code('inverse', 'Determinant, inverse and a check')}
<div class="warn">If det A = 0 the matrix squashes the plane flat onto a line or a point. Information is lost, so nothing can undo it. Such a matrix is called <b>singular</b> and has no inverse.</div>
{ml('In practice, code almost never computes an inverse directly, because it is slow and loses accuracy. Libraries solve Ax = b with factorisations instead (np.linalg.solve, or lstsq for regression). Near zero determinants signal nearly duplicate features.')}
''', kw=['identity matrix', 'inverse matrix', 'determinant', 'singular matrix', 'invertible', '2x2 inverse']),

    part('systems', '🧮', 'Solving many equations at once', f'''
<p>A system of linear equations is one matrix equation <b>Ax = b</b>. The matrix A holds the numbers in front of the unknowns, x is the vector of unknowns, and b is the right hand side. <b>Gaussian elimination</b> solves it by clearing numbers below the diagonal, then working backwards.</p>
<p style="text-align:center">x + y + z = 6, &nbsp; 2y + 5z = −4, &nbsp; 2x + 5y − z = 27 &nbsp; ⟺ &nbsp; {mat([[1, 1, 1], [0, 2, 5], [2, 5, -1]])} {vec(['x', 'y', 'z'])} = {vec([6, -4, 27])}</p>
{worked('Gaussian elimination on that system', [
        'Write the augmented matrix: <span class="eq">[1 1 1 | 6], [0 2 5 | −4], [2 5 −1 | 27]</span>',
        'Row 3 minus 2 × row 1 clears its first entry: <span class="eq">[0 3 −3 | 15]</span>',
        'Row 3 minus 1.5 × row 2 clears its second entry: <span class="eq">[0 0 −10.5 | 21]</span>',
        'Back substitute from the bottom: <span class="eq">z = 21 ÷ (−10.5) = −2</span>',
        'Row 2: <span class="eq">2y + 5(−2) = −4 → 2y = 6 → y = 3</span>',
        'Row 1: <span class="eq">x + 3 − 2 = 6 → x = 5</span>. So x = 5, y = 3, z = −2.'])}
{code('gauss', 'Elimination and back substitution')}
{fx('Linear regression in matrix form (normal equations)', 'β = (XᵀX)⁻¹ Xᵀ y', 'X holds the inputs (with a column of 1s for the intercept), y the targets, β the best weights. Practice problem 4 builds this by hand.')}
{life('A chemist balancing a reaction, an engineer finding forces in a bridge and a shop working out prices from receipts all solve Ax = b.')}
''', kw=['system of linear equations', 'Ax = b', 'gaussian elimination', 'back substitution', 'augmented matrix', 'normal equations']),

    part('rank', '🏷️', 'Rank and special matrices', f'''
<p>The <b>rank</b> of a matrix is the number of truly independent columns (or rows, it is always the same number). It says how many dimensions the matrix really uses. A 1000 × 50 data matrix with rank 30 has 20 columns that are combinations of others.</p>
{table(['Special matrix', 'What it looks like', 'Why it is handy'], [
        ['Diagonal', 'non zero entries only on the diagonal', 'multiplying just scales each coordinate'],
        ['Symmetric', 'A = Aᵀ', 'covariance matrices are symmetric, and their eigenvalues are real (Chapter 5)'],
        ['Orthogonal', 'QᵀQ = I', 'rotations and reflections, which keep lengths and angles'],
        ['Triangular', 'zeros above or below the diagonal', 'easy to solve by back substitution'],
        ['Sparse', 'mostly zeros', 'stored and multiplied cheaply, as in recommendation data'],
    ])}
{code('p_power', 'Repeated multiplication: a city and village move people every year')}
{ml('LoRA, a popular way to fine tune large language models, adds a <b>low rank</b> update BA to a huge weight matrix. A rank 8 update to a 4096 × 4096 matrix needs about 65 thousand numbers instead of 16.7 million.')}
{trick('Rank is never more than the smaller of the two sizes. A 3 × 7 matrix has rank at most 3.')}
''', kw=['rank', 'diagonal matrix', 'symmetric matrix', 'orthogonal matrix', 'triangular matrix', 'sparse matrix', 'low rank', 'LoRA', 'markov chain']),
]

INFO = {
    'title': 'Matrices move and mix numbers',
    'panels': [
        {'s': [['e', '📊'], ['g', [[1, 2, 3], [4, 5, 6]]]], 'h': 'A grid of numbers', 't': 'Rows × columns.', 'more': 'Rows are examples, columns are features.'},
        {'s': [['e', '🎯'], ['t', '(AB)ᵢⱼ = row i · column j', {'b': 1}]], 'h': 'Multiply', 't': 'Row times column.', 'more': 'Inner sizes must match: (m × n)(n × p) = m × p.'},
        {'s': [['e', '🔄'], ['t', 'columns = where the axes land', {'b': 1}]], 'h': 'Transform', 't': 'Rotate, stretch, shear.', 'more': 'A neural layer is Wx + b, a transformation plus a shift.'},
        {'s': [['e', '↩️'], ['t', 'A⁻¹A = I', {'b': 1}]], 'h': 'Inverse', 't': 'Undo the matrix.', 'more': 'If det A = 0, information is lost and there is no inverse.'},
    ],
    'remember': 'Shape is rows × columns. Multiply row by column, and the inner sizes must match. AB is usually not BA. A matrix transforms space, its determinant scales area, and only a non zero determinant has an inverse.',
}

REAL = [
    ['🛒', 'Shop bills', 'A table of items bought by each customer times a price vector gives every bill in one matrix multiplication.'],
    ['📸', 'Photo filters', 'Rotating, resizing and skewing a photo multiplies every pixel position by a transformation matrix.'],
    ['🏙️', 'Population moves', 'A matrix of moving rates between city and village, multiplied again each year, predicts the population, which is a Markov chain.'],
]

K.say('top', 'Welcome',
      'Matrices are grids of numbers. A dataset is a matrix and so are the weights of every neural network layer. In this chapter you will multiply matrices step by step, see them transform space, and use them to solve many equations at once.',
      'Matrices संख्याओं के grid हैं। Dataset एक matrix है और हर neural network layer के weights भी। इस अध्याय में आप matrices को कदम दर कदम गुणा करेंगे, उन्हें space बदलते देखेंगे, और कई समीकरण एक साथ हल करेंगे।',
      'Matrices ಸಂಖ್ಯೆಗಳ grid. Dataset ಒಂದು matrix, ಪ್ರತಿ neural network layer ನ weights ಕೂಡ. ಈ ಅಧ್ಯಾಯದಲ್ಲಿ matrices ಅನ್ನು ಹೆಜ್ಜೆ ಹೆಜ್ಜೆಯಾಗಿ ಗುಣಿಸಿ, space ಬದಲಿಸುವುದನ್ನು ನೋಡಿ, ಅನೇಕ ಸಮೀಕರಣಗಳನ್ನು ಬಿಡಿಸುತ್ತೀರಿ.',
      'Matrices ସଂଖ୍ୟାର grid। Dataset ଏକ matrix ଏବଂ ପ୍ରତ୍ୟେକ neural network layer ର weights ମଧ୍ୟ। ଏହି ଅଧ୍ୟାୟରେ matrices ଗୁଣନ, space ପରିବର୍ତ୍ତନ ଓ ଅନେକ ସମୀକରଣ ସମାଧାନ ଶିଖିବେ।',
      'المصفوفات شبكات من الأعداد. مجموعة البيانات مصفوفة، وكذلك أوزان كل طبقة في الشبكة العصبية. في هذا الفصل تضرب المصفوفات خطوة بخطوة، وتراها تحول الفضاء، وتحل بها معادلات كثيرة معًا.',
      'Matrizen sind Zahlengitter. Ein Datensatz ist eine Matrix, ebenso die Gewichte jeder Schicht eines neuronalen Netzes. In diesem Kapitel multiplizierst du Matrizen Schritt für Schritt, siehst, wie sie den Raum verändern, und löst viele Gleichungen auf einmal.')
K.say('what', 'What a matrix is',
      'A matrix is a rectangle of numbers with a shape of rows by columns. In a dataset each row is an example and each column a feature. A picture is a matrix of pixel brightness.',
      'Matrix संख्याओं का आयत है जिसका shape rows गुणा columns है। Dataset में हर row एक example और हर column एक feature है। तस्वीर pixels की brightness का matrix है।',
      'Matrix ಸಂಖ್ಯೆಗಳ ಆಯತ, shape rows ಗುಣಿಸು columns. Dataset ನಲ್ಲಿ ಪ್ರತಿ row ಒಂದು example, ಪ್ರತಿ column ಒಂದು feature.',
      'Matrix ସଂଖ୍ୟାର ଆୟତ, shape rows ଗୁଣନ columns। Dataset ରେ ପ୍ରତ୍ୟେକ row ଏକ example ଓ ପ୍ରତ୍ୟେକ column ଏକ feature।',
      'المصفوفة مستطيل من الأعداد شكله صفوف في أعمدة. في مجموعة البيانات كل صف مثال وكل عمود خاصية، والصورة مصفوفة من سطوع البكسلات.',
      'Eine Matrix ist ein Rechteck aus Zahlen mit der Form Zeilen mal Spalten. In einem Datensatz ist jede Zeile ein Beispiel und jede Spalte ein Merkmal. Ein Bild ist eine Matrix von Pixelhelligkeiten.')
K.say('basic', 'Basic operations',
      'Matrices of the same shape add entry by entry. A number scales every entry. The transpose turns rows into columns. The element wise product is different from matrix multiplication.',
      'एक ही shape के matrices entry दर entry जुड़ते हैं। संख्या हर entry को scale करती है। Transpose rows को columns बनाता है।',
      'ಒಂದೇ shape ನ matrices entry ಪ್ರಕಾರ ಕೂಡುತ್ತವೆ. Transpose rows ಅನ್ನು columns ಮಾಡುತ್ತದೆ.',
      'ସମାନ shape ର matrices entry ଅନୁସାରେ ଯୋଗ ହୁଏ। Transpose rows କୁ columns କରେ।',
      'المصفوفات المتساوية في الشكل تجمع عنصرًا بعنصر، والعدد يضرب كل عنصر، والمنقول يحول الصفوف إلى أعمدة. والضرب عنصرًا بعنصر يختلف عن ضرب المصفوفات.',
      'Matrizen gleicher Form addiert man Eintrag für Eintrag, eine Zahl skaliert jeden Eintrag, und die Transponierte macht Zeilen zu Spalten. Das elementweise Produkt ist etwas anderes als die Matrixmultiplikation.')
K.say('matmul', 'Matrix multiplication',
      'Each entry of a matrix product is a row of the first matrix dotted with a column of the second. The inner sizes must match. Order matters, so A times B is usually not B times A.',
      'Matrix product की हर entry पहले matrix की row और दूसरे के column का dot product है। Inner sizes मेल खाने चाहिए। क्रम मायने रखता है, A गुणा B आमतौर पर B गुणा A नहीं।',
      'Matrix product ನ ಪ್ರತಿ entry ಮೊದಲ matrix ನ row ಮತ್ತು ಎರಡನೆಯದರ column ನ dot product. ಕ್ರಮ ಮುಖ್ಯ.',
      'Matrix product ର ପ୍ରତ୍ୟେକ entry ପ୍ରଥମ matrix ର row ଓ ଦ୍ୱିତୀୟର column ର dot product। କ୍ରମ ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ।',
      'كل عنصر في حاصل ضرب مصفوفتين هو ضرب نقطي لصف من الأولى في عمود من الثانية. يجب أن تتطابق الأبعاد الداخلية، والترتيب مهم.',
      'Jeder Eintrag eines Matrixprodukts ist eine Zeile der ersten Matrix mal eine Spalte der zweiten. Die inneren Größen müssen passen, und die Reihenfolge zählt.')
K.say('transform', 'Transformations',
      'A matrix moves every point of the plane. Its first column is where the x axis arrow lands and its second column is where the y axis arrow lands. A neural network layer is W x plus b, a transformation followed by a shift.',
      'Matrix plane के हर बिंदु को हिलाता है। पहला column बताता है x axis का तीर कहाँ जाता है और दूसरा y axis का। Neural network layer W x जमा b है।',
      'Matrix plane ನ ಪ್ರತಿ ಬಿಂದುವನ್ನು ಸರಿಸುತ್ತದೆ. ಮೊದಲ column x ಅಕ್ಷದ ಬಾಣ ಎಲ್ಲಿ ಬೀಳುತ್ತದೆ, ಎರಡನೆಯದು y ಅಕ್ಷದ್ದು. Layer W x ಸೇರಿಸು b.',
      'Matrix plane ର ପ୍ରତ୍ୟେକ ବିନ୍ଦୁକୁ ଘୁଞ୍ଚାଏ। ପ୍ରଥମ column x ଅକ୍ଷର ତୀର କେଉଁଠି ପଡ଼େ, ଦ୍ୱିତୀୟ y ଅକ୍ଷର। Layer W x ଯୋଗ b।',
      'المصفوفة تحرك كل نقطة في المستوى. عمودها الأول هو مكان وصول سهم محور x، والثاني مكان سهم محور y. وطبقة الشبكة العصبية هي W x زائد b.',
      'Eine Matrix bewegt jeden Punkt der Ebene. Ihre erste Spalte zeigt, wo der x Achsen Pfeil landet, die zweite, wo der y Achsen Pfeil landet. Eine Netzschicht ist W x plus b.')
K.say('inverse', 'Inverse and determinant',
      'The identity matrix does nothing. The inverse undoes a matrix. For a two by two matrix the determinant is a d minus b c, and it measures how much area is scaled. If it is zero, there is no inverse.',
      'Identity matrix कुछ नहीं करता। Inverse matrix को उलट देता है। दो गुणा दो matrix का determinant a d घटा b c है और यह area का scale बताता है। शून्य हो तो inverse नहीं।',
      'Identity matrix ಏನೂ ಮಾಡುವುದಿಲ್ಲ. Inverse matrix ಅನ್ನು ರದ್ದುಗೊಳಿಸುತ್ತದೆ. Determinant a d ಕಳೆ b c. ಸೊನ್ನೆಯಾದರೆ inverse ಇಲ್ಲ.',
      'Identity matrix କିଛି କରେ ନାହିଁ। Inverse matrix କୁ ଓଲଟାଏ। Determinant a d ବିୟୋଗ b c। ଶୂନ ହେଲେ inverse ନାହିଁ।',
      'مصفوفة الوحدة لا تغير شيئًا، والمعكوس يلغي عمل المصفوفة. محدد المصفوفة اثنين في اثنين هو a d ناقص b c ويقيس تغير المساحة، وإذا كان صفرًا فلا معكوس.',
      'Die Einheitsmatrix ändert nichts, die Inverse macht eine Matrix rückgängig. Bei zwei mal zwei ist die Determinante a d minus b c und misst, wie Flächen skaliert werden. Ist sie null, gibt es keine Inverse.')
K.say('systems', 'Solving systems',
      'Many equations at once can be written as A x equals b. Gaussian elimination clears the numbers below the diagonal, then back substitution finds the unknowns from the last row upwards.',
      'कई समीकरण एक साथ A x बराबर b लिखे जा सकते हैं। Gaussian elimination diagonal के नीचे की संख्याएँ हटाता है, फिर back substitution आख़िरी row से ऊपर की ओर unknowns ढूँढता है।',
      'ಅನೇಕ ಸಮೀಕರಣಗಳನ್ನು A x ಸಮ b ಎಂದು ಬರೆಯಬಹುದು. Gaussian elimination ಕರ್ಣದ ಕೆಳಗಿನ ಸಂಖ್ಯೆಗಳನ್ನು ತೆಗೆಯುತ್ತದೆ, ನಂತರ back substitution.',
      'ଅନେକ ସମୀକରଣକୁ A x ସମାନ b ଲେଖାଯାଇପାରେ। Gaussian elimination diagonal ତଳ ସଂଖ୍ୟା ହଟାଏ, ତାପରେ back substitution।',
      'يمكن كتابة معادلات كثيرة معًا على شكل A x يساوي b. حذف غاوس يزيل الأعداد تحت القطر، ثم التعويض العكسي يجد المجاهيل من الصف الأخير صعودًا.',
      'Viele Gleichungen zusammen schreibt man als A x gleich b. Das Gauß Verfahren räumt die Zahlen unter der Diagonale ab, dann findet das Rückwärtseinsetzen die Unbekannten von unten nach oben.')
K.say('rank', 'Rank',
      'The rank counts the truly independent columns of a matrix. Special matrices such as diagonal, symmetric and orthogonal ones are easier to work with. Low rank updates make fine tuning large models cheap.',
      'Rank matrix के सच में independent columns गिनता है। Diagonal, symmetric और orthogonal matrices के साथ काम आसान है। Low rank updates बड़े models की fine tuning सस्ती बनाते हैं।',
      'Rank matrix ನ ನಿಜವಾದ independent columns ಎಣಿಸುತ್ತದೆ. Diagonal, symmetric, orthogonal matrices ಸುಲಭ. Low rank updates fine tuning ಅಗ್ಗ ಮಾಡುತ್ತವೆ.',
      'Rank matrix ର ପ୍ରକୃତ independent columns ଗଣେ। Diagonal, symmetric, orthogonal matrices ସହଜ। Low rank updates fine tuning ଶସ୍ତା କରେ।',
      'الرتبة تعد الأعمدة المستقلة حقًا في المصفوفة. المصفوفات القطرية والمتماثلة والمتعامدة أسهل في التعامل، والتحديثات منخفضة الرتبة تجعل ضبط النماذج الكبيرة رخيصًا.',
      'Der Rang zählt die wirklich unabhängigen Spalten einer Matrix. Diagonale, symmetrische und orthogonale Matrizen sind besonders handlich, und Aktualisierungen mit niedrigem Rang machen das Feinabstimmen großer Modelle günstig.')
K.say('practice', 'Practice',
      'Practice time. Multiply matrices of different shapes, rotate a square, and fit a straight line with the normal equations. Work each one on paper first.',
      'अभ्यास का समय। अलग shapes के matrices गुणा करें, एक square घुमाएँ, और normal equations से सीधी रेखा fit करें।',
      'ಅಭ್ಯಾಸದ ಸಮಯ. ಬೇರೆ shapes ನ matrices ಗುಣಿಸಿ, square ತಿರುಗಿಸಿ, normal equations ಬಳಸಿ ರೇಖೆ fit ಮಾಡಿ.',
      'ଅଭ୍ୟାସ ସମୟ। ଭିନ୍ନ shapes ର matrices ଗୁଣନ କରନ୍ତୁ, square ଘୁରାନ୍ତୁ, normal equations ରେ ରେଖା fit କରନ୍ତୁ।',
      'وقت التدريب. اضرب مصفوفات بأشكال مختلفة، وأدر مربعًا، وطابق خطًا مستقيمًا بالمعادلات الطبيعية.',
      'Zeit zum Üben. Multipliziere Matrizen verschiedener Formen, drehe ein Quadrat und passe eine Gerade mit den Normalgleichungen an.')

# ---------------------------------------------------------------- practice
K.practice('shapes', 'e', 'AB and BA have different shapes', 'p_shapes',
           '<p>A is 2 × 3 and B is 3 × 2. Compute AB and BA and explain why their shapes differ.</p>',
           'A is 2x3, B is 3x2, so AB is 2x2: [[5, 1], [4, 2]]\nBA is 3x3: [[2, 3, 7], [1, 3, 5], [1, 0, 2]]',
           'Use the shape rule (m × n)(n × p) = m × p twice.',
           '<p>For AB the inner sizes are 3 and 3, so it works and gives 2 × 2. For BA the inner sizes are 2 and 2, which gives 3 × 3. Entry (1, 1) of AB is row [1, 0, 2] · column [3, 2, 1] = 3 + 0 + 2 = 5. Not only are AB and BA different, they do not even have the same shape.</p>',
           'O(n · m · p)', 'O(n · p)')
K.practice('rotate', 'm', 'Rotate a square with a matrix', 'p_rotate',
           '<p>Rotate the corners (1, 0), (1, 1) and (0, 1) of a unit square by 90° and by 30° using the rotation matrix [[cos θ, −sin θ], [sin θ, cos θ]].</p>',
           '90 degrees: (0.000, 1.000) (-1.000, 1.000) (-1.000, 0.000)\n30 degrees: (0.866, 0.500) (0.366, 1.366) (-0.500, 0.866)',
           'Convert degrees to radians: θ = degrees × π ÷ 180.',
           '<p>cos 90° = 0 and sin 90° = 1, so the matrix is [[0, −1], [1, 0]] and (x, y) becomes (−y, x). For 30°, cos = 0.866 and sin = 0.5. Rotation matrices are orthogonal: they keep every length. The corner (1, 1) has length √2 ≈ 1.414 before and after, which you can check with 0.366² + 1.366².</p>',
           'O(n)', 'O(n)')
K.practice('markov', 'h', 'Population moves with a matrix power', 'p_power',
           '<p>Each year 10% of city people move to the village and 5% of village people move to the city. Start with 600 thousand in the city and 400 thousand in the village. Multiply by the transition matrix three times.</p>',
           'year 1: city 560.0, village 440.0\nyear 2: city 526.0, village 474.0\nyear 3: city 497.1, village 502.9',
           'Column j of the matrix says where the people of place j go.',
           '<p>The city keeps 90% and gains 5% of the village: 0.9 × 600 + 0.05 × 400 = 560. Each year is one more multiplication, so after n years the state is Tⁿ times the start. The totals always stay 1000 because each column adds to 1. In the long run the numbers settle where T leaves the state unchanged, an <b>eigenvector</b>, which Chapter 5 explains. Google PageRank uses exactly this idea.</p>',
           'O(years · n²)', 'O(n)')
K.practice('normal-eq', 'x', 'Fit a line with the normal equations', 'p_regression',
           '<p>Fit y = wx + c to the points (1, 2.2), (2, 4.1), (3, 6.1), (4, 7.9), (5, 10.2) by solving (XᵀX)β = Xᵀy, where X has a column of x values and a column of 1s.</p>',
           'X^T X = [[55, 15], [15, 5]], det = 50\nbest line: y = 1.980x + 0.160\nprediction at x = 6: 12.040',
           'XᵀX only needs Σx², Σx and n. Xᵀy needs Σxy and Σy.',
           '<p>With X having rows [xᵢ, 1], XᵀX = [[Σx², Σx], [Σx, n]] = [[55, 15], [15, 5]] and Xᵀy = [Σxy, Σy]. Solving the 2 × 2 system with the inverse formula gives w = (nΣxy − ΣxΣy) ÷ det and c = (Σx²Σy − ΣxΣxy) ÷ det. This closed form solution is exactly what scikit learn LinearRegression computes, using a more stable method behind the scenes.</p>',
           'O(n)', 'O(1)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What is the shape of a matrix with 4 rows and 2 columns?', ['2 × 4', '4 × 2', '8', '6'], 1, 'Rows first, then columns.', 'Shape is always rows × columns: 4 × 2.')
K.quiz('e', 'A is 3 × 5. What is the shape of Aᵀ?', ['3 × 5', '5 × 3', '15 × 1', '3 × 3'], 1, 'Transposing swaps rows and columns.', 'Rows become columns, so 5 × 3.')
K.quiz('e', 'Can you multiply a 2 × 3 matrix by a 2 × 3 matrix?', ['Yes, always', 'No, the inner sizes 3 and 2 do not match', 'Yes, the answer is 2 × 3', 'Only if they are equal'], 1, 'Check (m × n)(n × p).', 'The first has 3 columns but the second has 2 rows. Element wise multiplication would work, matrix multiplication does not.')
K.quiz('e', 'What does the identity matrix do to a vector?', ['Doubles it', 'Leaves it unchanged', 'Flips it', 'Makes it zero'], 1, 'It is the matrix version of the number 1.', 'Ix = x for every vector x.')
K.quiz('e', 'In a data matrix X, what does each row usually hold?', ['One feature for all examples', 'One example with all its features', 'The labels', 'The weights'], 1, 'Think of a spreadsheet of houses.', 'By convention each row is one example and each column one feature.')
K.quiz('m', 'What is the determinant of [[3, 1], [4, 2]]?', ['2', '10', '−2', '6'], 0, 'ad − bc.', '3 × 2 − 1 × 4 = 6 − 4 = 2.')
K.quiz('m', 'A is 64 × 128 and B is 128 × 10. What is the shape of AB?', ['64 × 10', '128 × 128', '10 × 64', 'cannot be multiplied'], 0, 'Outer sizes give the answer.', '(64 × 128)(128 × 10) = 64 × 10. This is a batch of 64 inputs going through a layer with 10 outputs.')
K.quiz('m', 'Which matrix rotates the plane by 90° anticlockwise?', ['[[1, 0], [0, 1]]', '[[0, −1], [1, 0]]', '[[0, 1], [1, 0]]', '[[−1, 0], [0, −1]]'], 1, 'Where does [1, 0] go? It should land on [0, 1].', 'The first column [0, 1] is where [1, 0] lands, and the second column [−1, 0] is where [0, 1] lands.')
K.quiz('m', 'Which is always true for square matrices A and B?', ['AB = BA', '(AB)ᵀ = AᵀBᵀ', '(AB)ᵀ = BᵀAᵀ', 'det(A + B) = det A + det B'], 2, 'The order reverses.', 'Transposing a product reverses the order: (AB)ᵀ = BᵀAᵀ.')
K.quiz('m', 'A matrix has determinant 0. Which is true?', ['It is the identity', 'It has no inverse', 'All its entries are 0', 'It rotates the plane'], 1, 'Think of squashing the plane flat.', 'det = 0 means area becomes 0, information is lost, and the matrix is singular.')
K.quiz('h', 'How many multiplications does the plain method use for two n × n matrices?', ['n', 'n²', 'n³', '2ⁿ'], 2, 'n² entries, each a dot product of length n.', 'There are n² answer entries and each needs n multiplications, so n³.')
K.quiz('h', 'What is the rank of [[1, 2], [2, 4]]?', ['0', '1', '2', '4'], 1, 'Is the second row a multiple of the first?', 'Row 2 = 2 × row 1, so only one independent row. Rank 1, and the determinant is 0.')
K.quiz('h', 'For an orthogonal matrix Q, what is Q⁻¹?', ['Q', 'Qᵀ', '−Q', 'it has none'], 1, 'QᵀQ = I.', 'Since QᵀQ = I, the transpose is the inverse. That makes rotations cheap to undo.')
K.quiz('x', 'A layer has a 256 × 784 weight matrix and a bias vector. How many parameters is that?', ['200704', '200960', '1040', '784'], 1, 'Weights plus one bias per output.', '256 × 784 = 200704 weights, plus 256 biases = 200960.')
K.quiz('x', 'Why do libraries solve Ax = b with factorisations instead of computing A⁻¹ first?', ['Inverses do not exist', 'It is faster and more accurate', 'Factorisations give a different answer', 'Inverses only work for 2 × 2'], 1, 'Think about rounding and work.', 'Forming A⁻¹ costs more and magnifies rounding errors. LU or QR factorisation gives the same answer more cheaply and accurately.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Add [[1, 2], [3, 4]] and [[5, 0], [−1, 2]]. What is the bottom right entry?', '6', 'Add matching positions.', [
    'Top row: <span class="eq">[1 + 5, 2 + 0] = [6, 2]</span>',
    'Bottom row: <span class="eq">[3 + (−1), 4 + 2] = [2, 6]</span>',
    'The bottom right entry is 6.',
], check=4 + 2)
K.calc('e', 'What is the entry in row 1, column 2 of [[2, 1], [0, 3]] × [[1, 4], [5, 2]]?', '10', 'Row 1 of the first matrix, column 2 of the second.', [
    'Row 1 of A is <span class="eq">[2, 1]</span>',
    'Column 2 of B is <span class="eq">[4, 2]</span>',
    'Dot product: <span class="eq">2 × 4 + 1 × 2 = 8 + 2 = 10</span>',
], check=2 * 4 + 1 * 2)
K.calc('e', 'Find the determinant of [[5, 2], [3, 4]].', '14', 'ad − bc.', [
    'a = 5, b = 2, c = 3, d = 4.',
    'Multiply the main diagonal: <span class="eq">a × d = 5 × 4 = 20</span>',
    'Multiply the other diagonal: <span class="eq">b × c = 2 × 3 = 6</span>',
    'Subtract: <span class="eq">20 − 6 = 14</span>. So this matrix scales every area by 14.',
], check=5 * 4 - 2 * 3)
K.calc('e', 'Multiply [[1, 2], [3, 4]] by the vector [1, 1]. What is the second component?', '7', 'Each component is a row dotted with the vector.', [
    'First component: <span class="eq">1 × 1 + 2 × 1 = 3</span>',
    'Second component: <span class="eq">3 × 1 + 4 × 1 = 7</span>',
    'Answer: [3, 7]. Multiplying by [1, 1] adds up each row.',
], check=7)
K.calc('m', 'What is the full product [[1, 2], [3, 4]] × [[2, 0], [1, 3]]? Give the sum of all four entries.', '32', 'Find all four entries, then add them.', [
    'Row 1 · column 1: <span class="eq">1 × 2 + 2 × 1 = 4</span>',
    'Row 1 · column 2: <span class="eq">1 × 0 + 2 × 3 = 6</span>',
    'Row 2 · column 1: <span class="eq">3 × 2 + 4 × 1 = 10</span>',
    'Row 2 · column 2: <span class="eq">3 × 0 + 4 × 3 = 12</span>',
    'Product: [[4, 6], [10, 12]]. Sum of entries: <span class="eq">4 + 6 + 10 + 12 = 32</span>',
], check=32, alt=[])
K.calc('m', 'Find the inverse of [[2, 1], [5, 3]]. Give the top right entry.', '-1', 'Determinant first, then swap, negate and divide.', [
    'Determinant: <span class="eq">2 × 3 − 1 × 5 = 6 − 5 = 1</span>',
    'Swap a and d, negate b and c: <span class="eq">[[3, −1], [−5, 2]]</span>',
    'Divide by the determinant 1: nothing changes.',
    'The top right entry is −1. Check: [[2, 1], [5, 3]] × [[3, −1], [−5, 2]] = [[6 − 5, −2 + 2], [15 − 15, −5 + 6]] = I. ✔',
], check=-1, alt=['−1'])
K.calc('m', 'A is 32 × 100, B is 100 × 50 and C is 50 × 10. How many rows and columns does ABC have? Give rows × columns as a single product number.', '320', 'Apply the shape rule twice.', [
    'AB: <span class="eq">(32 × 100)(100 × 50) = 32 × 50</span>',
    '(AB)C: <span class="eq">(32 × 50)(50 × 10) = 32 × 10</span>',
    'So ABC is 32 × 10, which holds <span class="eq">32 × 10 = 320</span> numbers.',
], check=320)
K.calc('m', 'The matrix [[3, 0], [0, 2]] is applied to a 1 by 1 square. What is the area of the result?', '6', 'The determinant is the area scale factor.', [
    'This matrix stretches x by 3 and y by 2.',
    'Determinant: <span class="eq">3 × 2 − 0 × 0 = 6</span>',
    'Area after = area before × det: <span class="eq">1 × 6 = 6</span>',
    'The square becomes a 3 by 2 rectangle, area 6. ✔',
], check=6)
K.calc('h', 'Solve x + 2y = 8 and 3x − y = 3 with the inverse of [[1, 2], [3, −1]]. Give y.', '3', 'det = 1 × (−1) − 2 × 3.', [
    'Determinant: <span class="eq">1 × (−1) − 2 × 3 = −1 − 6 = −7</span>',
    'Inverse: <span class="eq">(1 / −7) × [[−1, −2], [−3, 1]]</span>',
    'Multiply by b = [8, 3]: x = <span class="eq">(−1 × 8 − 2 × 3) ÷ (−7) = −14 ÷ −7 = 2</span>',
    'y = <span class="eq">(−3 × 8 + 1 × 3) ÷ (−7) = −21 ÷ −7 = 3</span>',
    'Check: 2 + 6 = 8 and 6 − 3 = 3. ✔',
], check=3)
K.calc('h', 'A dense layer has W = [[1, −1], [2, 0]], b = [0, −3] and input x = [3, 1]. What is ReLU(Wx + b) summed over both outputs?', '5', 'Wx first, add b, then replace negatives by 0.', [
    'Wx, row 1: <span class="eq">1 × 3 + (−1) × 1 = 2</span>',
    'Wx, row 2: <span class="eq">2 × 3 + 0 × 1 = 6</span>',
    'Add the bias: <span class="eq">[2 + 0, 6 − 3] = [2, 3]</span>',
    'ReLU keeps positives: <span class="eq">[2, 3]</span>',
    'Sum: <span class="eq">2 + 3 = 5</span>',
], check=5)
K.calc('h', 'Use Gaussian elimination on 2x + y = 7 and 4x + 5y = 23. Give x.', '2', 'Subtract 2 × row 1 from row 2.', [
    'Rows: <span class="eq">[2 1 | 7] and [4 5 | 23]</span>',
    'Row 2 − 2 × row 1: <span class="eq">[0 3 | 9]</span>',
    'So <span class="eq">3y = 9, y = 3</span>',
    'Back into row 1: <span class="eq">2x + 3 = 7, x = 2</span>',
], check=2)
K.calc('x', 'What is the determinant of the 3 × 3 matrix [[2, 0, 1], [1, 3, 2], [1, 1, 1]]?', '0', 'Expand along the first row: a(ei − fh) − b(di − fg) + c(dh − eg).', [
    'a = 2 with minor <span class="eq">3 × 1 − 2 × 1 = 1</span>, giving 2 × 1 = 2',
    'b = 0 so its term is <span class="eq">0</span>',
    'c = 1 with minor <span class="eq">1 × 1 − 3 × 1 = −2</span>, giving 1 × (−2) = −2',
    'Combine with signs + − +: <span class="eq">2 − 0 + (−2) = 0</span>',
    'The determinant is 0, so this matrix is singular. It has no inverse. You can see why: row 1 + row 2 = [3, 3, 3], which is exactly 3 × row 3. One row is built from the other two, so the matrix squashes space flat.',
], check=0, alt=[])
K.calc('x', 'With X rows [1, 1], [2, 1], [3, 1] (x and a column of 1s), what is the top left entry of XᵀX?', '14', 'Top left of XᵀX is the sum of the squares of the first column.', [
    'Entry (1, 1) of XᵀX is column 1 dotted with itself.',
    'Column 1 is <span class="eq">[1, 2, 3]</span>',
    'Dot with itself: <span class="eq">1 + 4 + 9 = 14</span>',
    'The full matrix is [[14, 6], [6, 3]], the 6 being Σx and the 3 being n.',
], check=14)

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;

  /* ----- matrix multiplication, one multiply at a time ----- */
  W.matmul = el => {
    const b = shell(el, 'Matrix multiplication, one step at a time', 'Edit any number in A or B, or pick a size. Press Play to watch each row slide across each column.');
    b.innerHTML = `<div class="vz-row">${seg('sz', [['2x2x2', '2×2 · 2×2'], ['2x3x2', '2×3 · 3×2'], ['3x2x3', '3×2 · 2×3'], ['1x3x1', '1×3 · 3×1']], '2x2x2')}</div>
      <div class="mv-mm mm-host"></div><div class="mv-calc mm-calc"></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let A, B, n, m, p, steps = [];
    const P = Player($('.vz-p', b), show, 650);
    const init = { '2x2x2': [[[1, 2], [3, 4]], [[5, 6], [7, 8]]], '2x3x2': [[[1, 0, 2], [-1, 3, 1]], [[3, 1], [2, 1], [1, 0]]], '3x2x3': [[[1, 2], [0, 1], [3, -1]], [[2, 0, 1], [1, 3, 2]]], '1x3x1': [[[2, 3, 4]], [[1], [0], [5]]] };
    const grid = (M, id, rows, cols, edit) => `<div><div class="mv-mgrid" style="grid-template-columns:repeat(${cols}, auto)">${M.flat().map((v, k) => `<div class="mv-c" data-m="${id}" data-i="${Math.floor(k / cols)}" data-j="${k % cols}">${edit ? `<input type="text" inputmode="numeric" value="${v}" aria-label="${id} entry">` : v}</div>`).join('')}</div><span class="lbl">${id} (${rows}×${cols})</span></div>`;
    function load(sz) {
      [A, B] = JSON.parse(JSON.stringify(init[sz]));
      n = A.length; m = B.length; p = B[0].length;
      $('.mm-host', b).innerHTML = grid(A, 'A', n, m, 1) + '<span class="op">×</span>' + grid(B, 'B', m, p, 1) + '<span class="op">=</span>' + grid(Array.from({ length: n }, () => Array(p).fill('?')), 'C', n, p, 0);
      b.querySelectorAll('input').forEach(inp => inp.addEventListener('change', () => {
        const c = inp.parentElement, v = parseFloat(inp.value);
        (c.dataset.m === 'A' ? A : B)[+c.dataset.i][+c.dataset.j] = isFinite(v) ? v : 0; plan();
      }));
      plan();
    }
    function plan() {
      steps = [{}];
      for (let i = 0; i < n; i++) for (let j = 0; j < p; j++) {
        let s = 0; const terms = [];
        for (let k = 0; k < m; k++) { s += A[i][k] * B[k][j]; terms.push(`${A[i][k]}×${B[k][j]}`); steps.push({ i, j, k, terms: [...terms], s }); }
      }
      P.load(steps.length);
    }
    function show(t) {
      const st = steps[t];
      b.querySelectorAll('.mv-c').forEach(c => c.classList.remove('hl', 'sel', 'ok', 'mv'));
      const done = new Map();
      for (let q = 1; q <= t; q++) if (steps[q].k === m - 1) done.set(steps[q].i + ',' + steps[q].j, steps[q].s);
      b.querySelectorAll('[data-m="C"]').forEach(c => { const key = c.dataset.i + ',' + c.dataset.j; c.textContent = done.has(key) ? MV.num(done.get(key), 2) : '?'; if (done.has(key)) c.classList.add('ok'); });
      if (!t) { $('.mm-calc', b).innerHTML = `Inner sizes ${m} and ${m} match, so C will be ${n} × ${p}.`; $('.vz-msg', b).innerHTML = 'Press Play or step forward.'; return; }
      b.querySelectorAll(`[data-m="A"][data-i="${st.i}"]`).forEach(c => c.classList.add('sel'));
      b.querySelectorAll(`[data-m="B"][data-j="${st.j}"]`).forEach(c => c.classList.add('mv'));
      b.querySelector(`[data-m="A"][data-i="${st.i}"][data-j="${st.k}"]`).classList.add('hl');
      b.querySelector(`[data-m="B"][data-i="${st.k}"][data-j="${st.j}"]`).classList.add('hl');
      const cc = b.querySelector(`[data-m="C"][data-i="${st.i}"][data-j="${st.j}"]`);
      cc.classList.add('hl'); cc.textContent = MV.num(st.s, 2);
      $('.mm-calc', b).innerHTML = `C<sub>${st.i + 1}${st.j + 1}</sub> = ${st.terms.join(' + ')} = <span class="t">${MV.num(st.s, 2)}</span>`;
      $('.vz-msg', b).innerHTML = `Row ${st.i + 1} of A meets column ${st.j + 1} of B. Pair ${st.k + 1} of ${m}.`;
    }
    wireSeg(b, 'sz', load);
    load('2x2x2');
  };

  /* ----- a 2x2 matrix transforms the grid ----- */
  W.transform = el => {
    const b = shell(el, 'Watch a matrix transform the plane', 'Pick a preset or type your own matrix. Slide t from 0 to 1 to morph the grid from "nothing" to the full transformation.');
    const PR = { scale: [2, 0, 0, 2], rot: [0, -1, 1, 0], shear: [1, 1, 0, 1], flip: [1, 0, 0, -1], squash: [1, 2, 0.5, 1], mix: [2, 1, 1, 2] };
    b.innerHTML = `<div class="vz-row">${seg('pr', [['scale', 'Scale'], ['rot', 'Rotate 90°'], ['shear', 'Shear'], ['flip', 'Reflect'], ['squash', 'Singular'], ['mix', 'Stretch']], 'shear')}</div>
      <div class="mv-wrap"><div class="tf-plot"></div><div class="mv-side"><div class="mv-inp">a <input type="number" data-e="0" step="0.5"> b <input type="number" data-e="1" step="0.5"></div><div class="mv-inp">c <input type="number" data-e="2" step="0.5"> d <input type="number" data-e="3" step="0.5"></div>${slider('t', 't', 0, 1, 1, 0.05)}<div class="mv-read tf-out" aria-live="polite"></div></div></div>`;
    let M = PR.shear.slice(), t = 1;
    const G = MV.frame(440, 440, [-4, 4], [-4, 4]);
    function setInputs() { b.querySelectorAll('[data-e]').forEach(i => { i.value = M[+i.dataset.e]; }); }
    function draw() {
      const [a, bb, c, d] = M.map((v, k) => (1 - t) * [1, 0, 0, 1][k] + t * v);
      const T = (x, y) => [a * x + bb * y, c * x + d * y];
      let s = MV.axes(G, { labels: false });
      for (let k = -4; k <= 4; k++) {
        const [x1, y1] = T(k, -4), [x2, y2] = T(k, 4), [x3, y3] = T(-4, k), [x4, y4] = T(4, k);
        s += MV.line(G, x1, y1, x2, y2, 'mv-curve thin c4') + MV.line(G, x3, y3, x4, y4, 'mv-curve thin c4');
      }
      const sq = [[0, 0], [1, 0], [1, 1], [0, 1]].map(([x, y]) => T(x, y));
      s += `<polygon class="mv-poly o" points="${sq.map(([x, y]) => G.sx(x) + ',' + G.sy(y)).join(' ')}"/>`;
      const e1 = T(1, 0), e2 = T(0, 1);
      s += MV.arrow(G, 0, 0, e1[0], e1[1], 'g') + MV.arrow(G, 0, 0, e2[0], e2[1], 'r');
      $('.tf-plot', b).innerHTML = MV.svg(G, s, 'A grid transformed by a matrix');
      const det = M[0] * M[3] - M[1] * M[2];
      $('.tf-out', b).innerHTML = `<span style="color:var(--green)">●</span> [1, 0] lands on column 1 = [${MV.num(M[0])}, ${MV.num(M[2])}]<br><span style="color:var(--red)">●</span> [0, 1] lands on column 2 = [${MV.num(M[1])}, ${MV.num(M[3])}]<br>det = ${MV.num(M[0])}×${MV.num(M[3])} − ${MV.num(M[1])}×${MV.num(M[2])} = <b>${MV.num(det)}</b><br>${Math.abs(det) < 1e-9 ? '⚠️ det = 0: the plane is squashed onto a line. No inverse exists.' : det < 0 ? 'Negative det: the plane is flipped over. The orange square has area ' + MV.num(Math.abs(det)) + '.' : 'The orange unit square now has area ' + MV.num(det) + '.'}`;
    }
    b.querySelectorAll('[data-e]').forEach(i => i.addEventListener('input', () => { const v = parseFloat(i.value); M[+i.dataset.e] = isFinite(v) ? v : 0; draw(); }));
    wireSeg(b, 'pr', v => { M = PR[v].slice(); setInputs(); draw(); });
    wireSlider(b, 't', v => { t = v; draw(); });
    setInputs(); draw();
  };
})();
'''

# ---------------------------------------------------------------- deeper explanations and extra animations
# Each lesson above gives the short version. DEEPER adds a slower, fuller explanation (and sometimes an
# animation) to the end of the lesson with the same id.
DEEPER = {
    'what': deep('rows, columns and shapes in code', f'''
<p>Maths books count rows and columns from 1. Python, JavaScript, TypeScript and Java count from 0. So the entry a₂₃ of a book (row 2, column 3) is <code>A[1][2]</code> in code. Keep this "off by one" shift in mind whenever you copy a formula into a program.</p>
{table(['Question', 'Maths', 'NumPy or PyTorch'], [
        ['How big is it?', 'm × n', 'A.shape gives (m, n)'],
        ['One entry', 'aᵢⱼ', 'A[i, j], counting from 0'],
        ['A whole row', 'row i', 'A[i, :] or A[i]'],
        ['A whole column', 'column j', 'A[:, j]'],
        ['Number of examples', 'm (rows of X)', 'X.shape[0], also len(X)'],
    ])}
<p>Deep learning code usually adds one more direction in front, the <b>batch</b>. A batch of 32 grey 28 × 28 images is a tensor of shape (32, 28, 28). A batch of 16 sentences of 128 tokens, each token an embedding of 768 numbers, has shape (16, 128, 768). Reading a shape from left to right tells you the story: how many examples, then how many positions, then how many numbers describe each position.</p>
{trick('Say the shape out loud before you write any matrix code: "X is examples by features, W is features by outputs, so XW is examples by outputs". Most shape bugs disappear with this habit.')}
'''),
    'basic': deep('watch the transpose, and meet symmetric matrices', f'''
<p>The transpose is easier to see than to describe. Every entry swaps its row number with its column number, so entries on the main diagonal (where row = column) stay put and everything else reflects across that diagonal. Press Play to watch it move one entry at a time.</p>
{viz('transpose')}
<p>A matrix that equals its own transpose, A = Aᵀ, is called <b>symmetric</b>. It is a mirror image of itself across the diagonal. Symmetric matrices are everywhere in machine learning because of one simple fact: for <b>any</b> matrix X, the product XᵀX is symmetric.</p>
{worked('XᵀX is always symmetric', [
        'Use the rule for the transpose of a product: <span class="eq">(AB)ᵀ = BᵀAᵀ</span>',
        'Apply it to XᵀX: <span class="eq">(XᵀX)ᵀ = Xᵀ(Xᵀ)ᵀ</span>',
        'Transposing twice gives back the original: <span class="eq">(Xᵀ)ᵀ = X</span>',
        'So <span class="eq">(XᵀX)ᵀ = XᵀX</span>. It equals its own transpose, so it is symmetric.',
        'XᵀX appears in the normal equations of regression and (divided by n − 1) as the covariance matrix of PCA.'])}
{ml('Adding a bias vector to every row of a batch, Z = XW + b, is technically a matrix plus a vector. Libraries allow it by "broadcasting": the vector is copied down every row automatically. Chapter 13 explains the broadcasting rules in detail.')}
'''),
    'matmul': deep('four ways to see the same multiplication', f'''
<p>"Row times column" is the way to compute a product by hand, but there are three other ways to look at the very same answer. Each one makes a different idea in machine learning obvious.</p>
{table(['View', 'What AB is', 'Where it helps'], [
        ['dot products', 'entry (i, j) is row i of A dotted with column j of B', 'computing by hand, attention scores QKᵀ'],
        ['columns', 'column j of AB is A times column j of B', 'a layer applied to many inputs at once'],
        ['rows', 'row i of AB is row i of A times B', 'each example (a row of X) passes through the same weights'],
        ['outer products', 'AB is the sum over k of (column k of A) times (row k of B)', 'low rank ideas such as LoRA and the SVD'],
    ])}
{worked('The columns view with A = [[1, 2], [3, 4]] and x = [5, 6]', [
        'Row view: <span class="eq">[1×5 + 2×6, 3×5 + 4×6] = [17, 39]</span>',
        'Column view: Ax is 5 lots of column 1 plus 6 lots of column 2.',
        '<span class="eq">5 × [1, 3] + 6 × [2, 4] = [5, 15] + [12, 24] = [17, 39]</span>',
        'Same answer. A matrix times a vector is a linear combination of the matrix columns, with the vector giving the amounts.'])}
<p><b>Counting the work.</b> Multiplying an m × n matrix by an n × p matrix needs m × n × p multiplications. A batch of 64 inputs with 1024 features through a layer with 4096 outputs costs 64 × 1024 × 4096 ≈ 268 million multiply and add steps, for just one layer of one batch. That is why GPUs, which do thousands of these at the same time, made deep learning possible.</p>
'''),
    'transform': deep('doing one transformation after another', f'''
<p>If you first apply B and then apply A to a vector, the result is A(Bx) = (AB)x. So <b>one matrix, AB, does both moves at once</b>. Notice the order: the move done first is written on the right, next to x.</p>
{worked('Rotate by 90°, then stretch x by 2', [
        'Rotate: <span class="eq">R = [[0, −1], [1, 0]]</span>. Stretch: <span class="eq">S = [[2, 0], [0, 1]]</span>',
        'Rotate first, then stretch: <span class="eq">SR = [[0, −2], [1, 0]]</span>',
        'Stretch first, then rotate: <span class="eq">RS = [[0, −1], [2, 0]]</span>',
        'Try x = [1, 0]: SR gives <span class="eq">[0, 1]</span>, but RS gives <span class="eq">[0, 2]</span>. Different results, so order matters.'])}
<p>This is exactly why a neural network needs activation functions between its layers. Without them, layer 3 of layer 2 of layer 1 is W₃W₂W₁x, and the product W₃W₂W₁ is a single matrix. Ten layers would collapse into one, which can only rotate, stretch and shear.</p>
{life('Putting on socks and then shoes is a composition. Doing it in the other order gives a very different (and funny) result. Matrix products behave the same way.')}
'''),
    'inverse': deep('the determinant is an area, and why zero means no way back', f'''
<p>Take the unit square with corners (0, 0), (1, 0), (1, 1) and (0, 1). A 2 × 2 matrix moves it into a parallelogram whose sides are the two columns of the matrix. The <b>area of that parallelogram is the determinant</b>. Change the four numbers below and watch the area follow ad − bc. Press Play to slowly squash the matrix down to determinant 0.</p>
{viz('detarea')}
<p>When the determinant reaches 0, the square is flattened onto a line. Many different points land on the same spot, so there is no way to tell where each one came from. That is why a matrix with determinant 0 has no inverse.</p>
{worked('Check an inverse the honest way', [
        'A = <span class="eq">[[4, 7], [2, 6]]</span>, det = <span class="eq">4 × 6 − 7 × 2 = 10</span>',
        'Swap a and d, negate b and c, divide by 10: <span class="eq">A⁻¹ = [[0.6, −0.7], [−0.2, 0.4]]</span>',
        'Multiply to check, first row: <span class="eq">[4 × 0.6 + 7 × (−0.2), 4 × (−0.7) + 7 × 0.4] = [1, 0]</span>',
        'Second row: <span class="eq">[2 × 0.6 + 6 × (−0.2), 2 × (−0.7) + 6 × 0.4] = [0, 1]</span>',
        'We got the identity, so the inverse is right.'])}
{trick('A negative determinant means the parallelogram is flipped over, like looking at the square in a mirror. The size of the area is still |det|.')}
'''),
    'systems': deep('Gaussian elimination, one row operation at a time', f'''
<p>Gaussian elimination only ever uses three moves, and none of them changes the answer of the system: swap two rows, multiply a row by a non zero number, and add a multiple of one row to another. The goal is a staircase of zeros below the diagonal. Then the last equation has one unknown, and you work back up.</p>
<p>Type your own three equations below (or keep the example from the lesson) and press Play to see every row operation and then the back substitution.</p>
{viz('elim')}
{table(['What the last rows look like', 'What it means', 'How many answers'], [
        ['a staircase with no zero on the diagonal', 'every equation adds new information', 'exactly one'],
        ['a row of all zeros = 0', 'one equation repeated another', 'infinitely many'],
        ['a row of zeros = a non zero number', 'the equations contradict each other (0 = 5)', 'none'],
    ])}
{ml('Least squares regression usually has more equations (examples) than unknowns (weights), so there is no exact answer. Instead of elimination on Ax = b, libraries solve the normal equations XᵀXβ = Xᵀy or, more accurately, use the QR or SVD factorisations of Chapter 13 and Chapter 5.')}
'''),
    'rank': deep('finding the rank, and what low rank buys you', f'''
<p>The easiest way to find the rank by hand is elimination: after the staircase is made, <b>the rank is the number of rows that are not all zero</b>. Each surviving row is an independent piece of information.</p>
{worked('Rank of [[1, 2, 3], [2, 4, 6], [1, 0, 1]]', [
        'Row 2 minus 2 × row 1: <span class="eq">[0, 0, 0]</span>. Row 2 was just a copy of row 1, doubled.',
        'Row 3 minus row 1: <span class="eq">[0, −2, −2]</span>',
        'Two rows are not zero: <span class="eq">[1, 2, 3]</span> and <span class="eq">[0, −2, −2]</span>',
        'So the rank is <span class="eq">2</span>. The 3 × 3 matrix really only uses 2 dimensions, and its determinant is 0.'])}
{fx('Rank and the lost directions', 'rank + (number of lost directions) = number of columns', 'A 3 × 3 matrix of rank 2 squashes one whole direction to zero. That lost direction is called the null space.')}
<p><b>Why low rank is useful.</b> A rank r matrix of size m × n can be written as an m × r matrix times an r × n matrix. That needs only r(m + n) numbers instead of m × n. A 1000 × 1000 image of rank 20 needs 20 × 2000 = 40000 numbers instead of a million, 25 times smaller. This idea powers image compression, recommender systems and LoRA fine tuning.</p>
'''),
}
for _p in PARTS:
    _p['html'] += DEEPER.get(_p['id'], '')

VIZ_JS += r'''
(() => {
  const { $, shell, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;
  const fmt = v => MV.num(Math.abs(v) < 1e-9 ? 0 : v, 3);

  /* ----- the transpose, one entry at a time ----- */
  W.transpose = el => {
    const b = shell(el, 'Watch a matrix flip over its diagonal', 'Each step moves one entry from row i, column j of A to row j, column i of Aᵀ. Entries on the diagonal stay where they are.');
    const A = [[1, 2, 3], [4, 5, 6]];
    b.innerHTML = `<div class="mv-mm"><div><div class="mv-mgrid tp-a" style="grid-template-columns:repeat(3,auto)"></div><span class="lbl">A (2 × 3)</span></div><span class="op">→</span><div><div class="mv-mgrid tp-t" style="grid-template-columns:repeat(2,auto)"></div><span class="lbl">Aᵀ (3 × 2)</span></div></div><div class="mv-calc tp-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const order = [];
    for (let i = 0; i < 2; i++) for (let j = 0; j < 3; j++) order.push([i, j]);
    function show(t) {
      let a = '', tt = '';
      for (let i = 0; i < 2; i++) for (let j = 0; j < 3; j++) { const k = i * 3 + j; a += `<div class="mv-c ${k === t - 1 ? 'hl' : k < t - 1 ? 'ok' : ''}">${A[i][j]}</div>`; }
      for (let j = 0; j < 3; j++) for (let i = 0; i < 2; i++) { const k = i * 3 + j; tt += `<div class="mv-c ${k === t - 1 ? 'hl' : ''}">${k < t ? A[i][j] : ''}</div>`; }
      $('.tp-a', b).innerHTML = a; $('.tp-t', b).innerHTML = tt;
      if (!t) { $('.tp-msg', b).innerHTML = 'Press Play. Aᵀ starts empty.'; return; }
      const [i, j] = order[t - 1];
      $('.tp-msg', b).innerHTML = `<span class="t">a${i + 1}${j + 1} = ${A[i][j]}</span> moves from row ${i + 1}, column ${j + 1} to row ${j + 1}, column ${i + 1}` + (i === j ? ' (on the diagonal, so it stays in the same place)' : '') + (t === 6 ? '. Done: rows have become columns.' : '');
    }
    const P = Player($('.vz-p', b), show, 900);
    P.load(7, 0);
  };

  /* ----- determinant as the area of the transformed unit square ----- */
  W.detarea = el => {
    const b = shell(el, 'The determinant is an area', 'The grey square is the unit square. The coloured shape is where the matrix [[a, b], [c, d]] sends it. Its sides are the columns [a, c] and [b, d]. Press Play to squash it down to determinant 0.');
    b.innerHTML = `<div class="mv-wrap"><div class="da-plot"></div><div class="mv-side">${slider('a', 'a', -3, 3, 2, 0.25)}${slider('b', 'b', -3, 3, 1, 0.25)}${slider('c', 'c', -3, 3, 0.5, 0.25)}${slider('d', 'd', -3, 3, 1.5, 0.25)}<div class="mv-read da-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const M = { a: 2, b: 1, c: 0.5, d: 1.5 };
    const G = MV.frame(420, 420, [-4, 4], [-4, 4]);
    function draw() {
      const { a, b: bb, c, d } = M, det = a * d - bb * c;
      const poly = pts => `<polygon class="${det < 0 ? 'mv-poly o' : Math.abs(det) < 1e-9 ? 'mv-poly g' : 'mv-poly'}" points="${pts.map(p => G.sx(p[0]).toFixed(1) + ',' + G.sy(p[1]).toFixed(1)).join(' ')}"/>`;
      let s = MV.axes(G, { xstep: 1, ystep: 1, labels: false });
      s += `<polygon class="mv-poly" style="fill:none;stroke-dasharray:4 4;stroke:var(--ink2)" points="${[[0, 0], [1, 0], [1, 1], [0, 1]].map(p => G.sx(p[0]) + ',' + G.sy(p[1])).join(' ')}"/>`;
      s += poly([[0, 0], [a, c], [a + bb, c + d], [bb, d]]);
      s += MV.arrow(G, 0, 0, a, c, 'a') + MV.arrow(G, 0, 0, bb, d, 'o');
      $('.da-plot', b).innerHTML = MV.svg(G, s, 'Unit square and its image');
      $('.da-out', b).innerHTML = `det = ad − bc = ${fmt(a)} × ${fmt(d)} − ${fmt(bb)} × ${fmt(c)} = <span class="big">${fmt(det)}</span><br>area of the shape = |det| = <b>${fmt(Math.abs(det))}</b><br>` +
        (Math.abs(det) < 1e-9 ? '⚠️ Flattened onto a line. No inverse exists.' : det < 0 ? 'Negative: the square is flipped over as well as stretched.' : 'Positive: stretched but not flipped.') +
        (Math.abs(det) > 1e-9 ? `<br>inverse = (1 ÷ ${fmt(det)}) × [[${fmt(d)}, ${fmt(-bb)}], [${fmt(-c)}, ${fmt(a)}]]` : '');
    }
    const setS = (k, v) => { M[k] = v; $(`[data-sl="${k}"]`, b).value = v; $(`[data-slv="${k}"]`, b).textContent = MV.num(v); };
    const P = Player($('.vz-p', b), t => { setS('a', 2); setS('b', 1); setS('c', 0.5); setS('d', 1.5 - t * 0.125); draw(); }, 450);
    ['a', 'b', 'c', 'd'].forEach(k => wireSlider(b, k, v => { P.pause(); M[k] = v; draw(); }));
    P.load(11, 0);
  };

  /* ----- Gaussian elimination on a 3 × 3 system the reader types ----- */
  W.elim = el => {
    const b = shell(el, 'Gaussian elimination step by step', 'Each row is one equation: the three numbers in front of x, y and z, then the right hand side. Edit any number, then press Play.');
    const start = [[1, 1, 1, 6], [0, 2, 5, -4], [2, 5, -1, 27]];
    b.innerHTML = `<div class="mv-mm"><div class="mv-mgrid el-in" style="grid-template-columns:repeat(4,auto)">${start.map((r, i) => r.map((v, j) => `<div class="mv-c"><input type="number" step="1" value="${v}" data-i="${i}" data-j="${j}" aria-label="row ${i + 1} entry ${j + 1}"></div>`).join('')).join('')}</div><span class="op">→</span><div><div class="mv-mgrid el-out" style="grid-template-columns:repeat(4,auto)"></div><span class="lbl">x · y · z | right side</span></div></div><div class="mv-calc el-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let frames = [];
    function plan() {
      const M = start.map(r => r.slice());
      b.querySelectorAll('.el-in input').forEach(inp => { M[+inp.dataset.i][+inp.dataset.j] = +inp.value || 0; });
      frames = [{ M: M.map(r => r.slice()), msg: 'The starting system, written as an augmented matrix.', hl: -1 }];
      let ok = true;
      for (let c = 0; c < 3 && ok; c++) {
        let p = c;
        while (p < 3 && Math.abs(M[p][c]) < 1e-12) p++;
        if (p === 3) { ok = false; frames.push({ M: M.map(r => r.slice()), msg: `Column ${c + 1} has no non zero number to work with. The equations are not independent, so there is no single answer.`, hl: -1 }); break; }
        if (p !== c) { [M[p], M[c]] = [M[c], M[p]]; frames.push({ M: M.map(r => r.slice()), msg: `Swap row ${c + 1} and row ${p + 1} so the pivot is not 0.`, hl: c }); }
        for (let r = c + 1; r < 3; r++) {
          const f = M[r][c] / M[c][c];
          if (Math.abs(f) < 1e-12) continue;
          for (let k = c; k < 4; k++) M[r][k] -= f * M[c][k];
          frames.push({ M: M.map(rr => rr.slice()), msg: `Row ${r + 1} − (${fmt(f)}) × row ${c + 1} makes a zero below the pivot ${fmt(M[c][c])}.`, hl: r });
        }
      }
      if (ok) {
        const x = [0, 0, 0], names = ['x', 'y', 'z'];
        for (let r = 2; r >= 0; r--) {
          let s = M[r][3];
          for (let k = r + 1; k < 3; k++) s -= M[r][k] * x[k];
          x[r] = s / M[r][r];
          frames.push({ M: M.map(rr => rr.slice()), msg: `Back substitution, row ${r + 1}: ${names[r]} = <b>${fmt(x[r])}</b>`, hl: r });
        }
        frames.push({ M: M.map(rr => rr.slice()), msg: `Answer: x = <b>${fmt(x[0])}</b>, y = <b>${fmt(x[1])}</b>, z = <b>${fmt(x[2])}</b>`, hl: -1 });
      }
      P.load(frames.length, 0);
    }
    function show(t) {
      const F = frames[t];
      $('.el-out', b).innerHTML = F.M.map((r, i) => r.map((v, j) => `<div class="mv-c ${i === F.hl ? 'hl' : j < 3 && j < i && Math.abs(v) < 1e-9 ? 'ok' : ''}">${fmt(v)}</div>`).join('')).join('');
      $('.el-msg', b).innerHTML = `<span class="t">step ${t}</span> ${F.msg}`;
    }
    const P = Player($('.vz-p', b), show, 1300);
    b.querySelectorAll('.el-in input').forEach(inp => inp.addEventListener('change', plan));
    plan();
  };
})();
'''
CSS = r'''
.el-in .mv-c,.el-out .mv-c{min-width:46px}
@media (max-width:560px){ .el-in .mv-c,.el-out .mv-c{min-width:34px; font-size:12.5px} .el-in .mv-c input{width:32px} }
'''

T = K.topic(
    slug='matrices', topic='matrices', prefix='mm04', short='Matrices', emoji='🔢',
    title='Matrices and Matrix Multiplication',
    module=('🧮', 'Linear algebra', 'linear-algebra', 'Vectors, matrices, eigenvalues, SVD and PCA: the maths that lets a model handle thousands of numbers at once.'),
    minutes=55,
    lead='Matrices hold datasets, images and the weights of every layer. Multiply them step by step with an animation you can edit, watch a matrix bend the plane, find determinants and inverses, solve systems with elimination, and fit a regression line with the normal equations.',
    desc='Matrices for machine learning: shape, transpose, matrix multiplication step by step, linear transformations, determinant, inverse, Gaussian elimination, rank and the normal equations.',
    summary='Shapes and data matrices, addition, transpose and the element wise product, matrix multiplication with the shape rule, transformations and the Wx + b layer, identity, determinant and inverse, Gaussian elimination, rank, special matrices and the normal equations for regression.',
    keywords=['matrix', 'matrix multiplication', 'transpose', 'shape', 'linear transformation', 'rotation matrix', 'determinant', 'inverse', 'identity matrix', 'gaussian elimination', 'Ax = b', 'rank', 'normal equations', 'dense layer', 'markov chain'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
