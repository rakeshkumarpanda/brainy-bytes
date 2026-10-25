# Chapter 5: eigenvalues and eigenvectors, the characteristic equation, diagonalisation, power iteration,
# singular value decomposition, low rank approximation and principal component analysis.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz, vec, mat, deep

K = Kit()

# ---------------------------------------------------------------- programs
K.code('eig2', py=r'''
import math

A = [[2, 1],
     [1, 2]]
a, b = A[0]
c, d = A[1]
tr = a + d                            # trace: add the diagonal
det = a * d - b * c
print(f"trace = {tr}, det = {det}")
disc = tr * tr - 4 * det              # from  lambda^2 - trace * lambda + det = 0
for lam in [(tr + math.sqrt(disc)) / 2, (tr - math.sqrt(disc)) / 2]:
    v = [b, lam - a]                  # solves (A - lambda I) v = 0 when b is not 0
    Av = [a * v[0] + b * v[1], c * v[0] + d * v[1]]
    print(f"lambda = {lam:.2f}: v = [{v[0]:.2f}, {v[1]:.2f}], Av = [{Av[0]:.2f}, {Av[1]:.2f}]")
''', js=r'''
const A = [[2, 1],
           [1, 2]];
const [a, b] = A[0];
const [c, d] = A[1];
const tr = a + d;                     // trace: add the diagonal
const det = a * d - b * c;
console.log(`trace = ${tr}, det = ${det}`);
const disc = tr * tr - 4 * det;       // from  lambda^2 - trace * lambda + det = 0
for (const lam of [(tr + Math.sqrt(disc)) / 2, (tr - Math.sqrt(disc)) / 2]) {
  const v = [b, lam - a];             // solves (A - lambda I) v = 0 when b is not 0
  const Av = [a * v[0] + b * v[1], c * v[0] + d * v[1]];
  console.log(`lambda = ${lam.toFixed(2)}: v = [${v[0].toFixed(2)}, ${v[1].toFixed(2)}], Av = [${Av[0].toFixed(2)}, ${Av[1].toFixed(2)}]`);
}
''', ts=r'''
const A: number[][] = [[2, 1],
                       [1, 2]];
const [a, b] = A[0];
const [c, d] = A[1];
const tr: number = a + d;             // trace: add the diagonal
const det: number = a * d - b * c;
console.log(`trace = ${tr}, det = ${det}`);
const disc: number = tr * tr - 4 * det;   // from  lambda^2 - trace * lambda + det = 0
for (const lam of [(tr + Math.sqrt(disc)) / 2, (tr - Math.sqrt(disc)) / 2]) {
  const v: number[] = [b, lam - a];   // solves (A - lambda I) v = 0 when b is not 0
  const Av: number[] = [a * v[0] + b * v[1], c * v[0] + d * v[1]];
  console.log(`lambda = ${lam.toFixed(2)}: v = [${v[0].toFixed(2)}, ${v[1].toFixed(2)}], Av = [${Av[0].toFixed(2)}, ${Av[1].toFixed(2)}]`);
}
''', java=r'''
public class Eig2 {
    public static void main(String[] args) {
        double[][] A = {{2, 1},
                        {1, 2}};
        double a = A[0][0], b = A[0][1], c = A[1][0], d = A[1][1];
        int tr = (int) (a + d);                     // trace: add the diagonal
        int det = (int) (a * d - b * c);
        System.out.println("trace = " + tr + ", det = " + det);
        double disc = tr * tr - 4 * det;            // from  lambda^2 - trace * lambda + det = 0
        double[] lams = {(tr + Math.sqrt(disc)) / 2, (tr - Math.sqrt(disc)) / 2};
        for (double lam : lams) {
            double[] v = {b, lam - a};              // solves (A - lambda I) v = 0 when b is not 0
            double[] Av = {a * v[0] + b * v[1], c * v[0] + d * v[1]};
            System.out.println(String.format("lambda = %.2f: v = [%.2f, %.2f], Av = [%.2f, %.2f]", lam, v[0], v[1], Av[0], Av[1]));
        }
    }
}
''')

K.code('power', py=r'''
import math

A = [[2, 1],
     [1, 2]]
v = [1.0, 0.0]                        # any starting guess that is not zero
for step in range(1, 7):
    w = [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]]
    n = math.sqrt(w[0] ** 2 + w[1] ** 2)
    v = [w[0] / n, w[1] / n]          # multiply by A, then shrink back to length 1
    Av = [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]]
    lam = v[0] * Av[0] + v[1] * Av[1]  # how much A stretches v
    print(f"step {step}: v = [{v[0]:.4f}, {v[1]:.4f}], estimate = {lam:.4f}")
''', js=r'''
const A = [[2, 1],
           [1, 2]];
let v = [1, 0];                       // any starting guess that is not zero
for (let step = 1; step <= 6; step++) {
  const w = [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]];
  const n = Math.hypot(w[0], w[1]);
  v = [w[0] / n, w[1] / n];           // multiply by A, then shrink back to length 1
  const Av = [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]];
  const lam = v[0] * Av[0] + v[1] * Av[1];   // how much A stretches v
  console.log(`step ${step}: v = [${v[0].toFixed(4)}, ${v[1].toFixed(4)}], estimate = ${lam.toFixed(4)}`);
}
''', ts=r'''
const A: number[][] = [[2, 1],
                       [1, 2]];
let v: number[] = [1, 0];             // any starting guess that is not zero
for (let step = 1; step <= 6; step++) {
  const w: number[] = [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]];
  const n: number = Math.hypot(w[0], w[1]);
  v = [w[0] / n, w[1] / n];           // multiply by A, then shrink back to length 1
  const Av: number[] = [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]];
  const lam: number = v[0] * Av[0] + v[1] * Av[1];   // how much A stretches v
  console.log(`step ${step}: v = [${v[0].toFixed(4)}, ${v[1].toFixed(4)}], estimate = ${lam.toFixed(4)}`);
}
''', java=r'''
public class PowerIteration {
    public static void main(String[] args) {
        double[][] A = {{2, 1},
                        {1, 2}};
        double[] v = {1, 0};                       // any starting guess that is not zero
        for (int step = 1; step <= 6; step++) {
            double[] w = {A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]};
            double n = Math.hypot(w[0], w[1]);
            v = new double[]{w[0] / n, w[1] / n};   // multiply by A, then shrink back to length 1
            double[] Av = {A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]};
            double lam = v[0] * Av[0] + v[1] * Av[1];   // how much A stretches v
            System.out.println(String.format("step %d: v = [%.4f, %.4f], estimate = %.4f", step, v[0], v[1], lam));
        }
    }
}
''')

K.code('svd2', py=r'''
import math

A = [[3, 0],
     [4, 5]]
# step 1: the eigenvalues of A^T A are the squared singular values
AtA = [[sum(A[k][i] * A[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
print("A^T A =", AtA)
tr = AtA[0][0] + AtA[1][1]
det = AtA[0][0] * AtA[1][1] - AtA[0][1] * AtA[1][0]
gap = math.sqrt(tr * tr / 4 - det)
s1, s2 = math.sqrt(tr / 2 + gap), math.sqrt(tr / 2 - gap)
print(f"singular values: {s1:.4f} and {s2:.4f}")
# step 2: v1 is the matching eigenvector of A^T A, and u1 = A v1 / s1
v = [AtA[0][1], s1 * s1 - AtA[0][0]]
n = math.hypot(v[0], v[1])
v1 = [v[0] / n, v[1] / n]
u1 = [(A[0][0] * v1[0] + A[0][1] * v1[1]) / s1, (A[1][0] * v1[0] + A[1][1] * v1[1]) / s1]
print(f"v1 = [{v1[0]:.4f}, {v1[1]:.4f}], u1 = [{u1[0]:.4f}, {u1[1]:.4f}]")
# step 3: the best rank 1 copy of A is s1 * u1 * v1^T
A1 = [[s1 * u1[i] * v1[j] for j in range(2)] for i in range(2)]
err = math.sqrt(sum((A[i][j] - A1[i][j]) ** 2 for i in range(2) for j in range(2)))
print(f"rank 1 copy = [[{A1[0][0]:.2f}, {A1[0][1]:.2f}], [{A1[1][0]:.2f}, {A1[1][1]:.2f}]]")
print(f"error = {err:.4f}, the same as s2")
''', js=r'''
const A = [[3, 0],
           [4, 5]];
// step 1: the eigenvalues of A^T A are the squared singular values
const AtA = [0, 1].map(i => [0, 1].map(j => A[0][i] * A[0][j] + A[1][i] * A[1][j]));
console.log("A^T A =", "[" + AtA.map(r => "[" + r.join(", ") + "]").join(", ") + "]");
const tr = AtA[0][0] + AtA[1][1];
const det = AtA[0][0] * AtA[1][1] - AtA[0][1] * AtA[1][0];
const gap = Math.sqrt(tr * tr / 4 - det);
const s1 = Math.sqrt(tr / 2 + gap), s2 = Math.sqrt(tr / 2 - gap);
console.log(`singular values: ${s1.toFixed(4)} and ${s2.toFixed(4)}`);
// step 2: v1 is the matching eigenvector of A^T A, and u1 = A v1 / s1
const v = [AtA[0][1], s1 * s1 - AtA[0][0]];
const n = Math.hypot(v[0], v[1]);
const v1 = [v[0] / n, v[1] / n];
const u1 = [(A[0][0] * v1[0] + A[0][1] * v1[1]) / s1, (A[1][0] * v1[0] + A[1][1] * v1[1]) / s1];
console.log(`v1 = [${v1[0].toFixed(4)}, ${v1[1].toFixed(4)}], u1 = [${u1[0].toFixed(4)}, ${u1[1].toFixed(4)}]`);
// step 3: the best rank 1 copy of A is s1 * u1 * v1^T
const A1 = [0, 1].map(i => [0, 1].map(j => s1 * u1[i] * v1[j]));
let sq = 0;
for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) sq += (A[i][j] - A1[i][j]) ** 2;
console.log(`rank 1 copy = [[${A1[0][0].toFixed(2)}, ${A1[0][1].toFixed(2)}], [${A1[1][0].toFixed(2)}, ${A1[1][1].toFixed(2)}]]`);
console.log(`error = ${Math.sqrt(sq).toFixed(4)}, the same as s2`);
''', ts=r'''
const A: number[][] = [[3, 0],
                       [4, 5]];
// step 1: the eigenvalues of A^T A are the squared singular values
const AtA: number[][] = [0, 1].map(i => [0, 1].map(j => A[0][i] * A[0][j] + A[1][i] * A[1][j]));
console.log("A^T A =", "[" + AtA.map(r => "[" + r.join(", ") + "]").join(", ") + "]");
const tr: number = AtA[0][0] + AtA[1][1];
const det: number = AtA[0][0] * AtA[1][1] - AtA[0][1] * AtA[1][0];
const gap: number = Math.sqrt(tr * tr / 4 - det);
const s1: number = Math.sqrt(tr / 2 + gap), s2: number = Math.sqrt(tr / 2 - gap);
console.log(`singular values: ${s1.toFixed(4)} and ${s2.toFixed(4)}`);
// step 2: v1 is the matching eigenvector of A^T A, and u1 = A v1 / s1
const v: number[] = [AtA[0][1], s1 * s1 - AtA[0][0]];
const n: number = Math.hypot(v[0], v[1]);
const v1: number[] = [v[0] / n, v[1] / n];
const u1: number[] = [(A[0][0] * v1[0] + A[0][1] * v1[1]) / s1, (A[1][0] * v1[0] + A[1][1] * v1[1]) / s1];
console.log(`v1 = [${v1[0].toFixed(4)}, ${v1[1].toFixed(4)}], u1 = [${u1[0].toFixed(4)}, ${u1[1].toFixed(4)}]`);
// step 3: the best rank 1 copy of A is s1 * u1 * v1^T
const A1: number[][] = [0, 1].map(i => [0, 1].map(j => s1 * u1[i] * v1[j]));
let sq: number = 0;
for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) sq += (A[i][j] - A1[i][j]) ** 2;
console.log(`rank 1 copy = [[${A1[0][0].toFixed(2)}, ${A1[0][1].toFixed(2)}], [${A1[1][0].toFixed(2)}, ${A1[1][1].toFixed(2)}]]`);
console.log(`error = ${Math.sqrt(sq).toFixed(4)}, the same as s2`);
''', java=r'''
public class Svd2 {
    public static void main(String[] args) {
        int[][] A = {{3, 0},
                     {4, 5}};
        // step 1: the eigenvalues of A^T A are the squared singular values
        int[][] AtA = new int[2][2];
        for (int i = 0; i < 2; i++)
            for (int j = 0; j < 2; j++)
                AtA[i][j] = A[0][i] * A[0][j] + A[1][i] * A[1][j];
        System.out.println("A^T A = " + java.util.Arrays.deepToString(AtA));
        double tr = AtA[0][0] + AtA[1][1];
        double det = AtA[0][0] * AtA[1][1] - AtA[0][1] * AtA[1][0];
        double gap = Math.sqrt(tr * tr / 4 - det);
        double s1 = Math.sqrt(tr / 2 + gap), s2 = Math.sqrt(tr / 2 - gap);
        System.out.println(String.format("singular values: %.4f and %.4f", s1, s2));
        // step 2: v1 is the matching eigenvector of A^T A, and u1 = A v1 / s1
        double[] v = {AtA[0][1], s1 * s1 - AtA[0][0]};
        double n = Math.hypot(v[0], v[1]);
        double[] v1 = {v[0] / n, v[1] / n};
        double[] u1 = {(A[0][0] * v1[0] + A[0][1] * v1[1]) / s1, (A[1][0] * v1[0] + A[1][1] * v1[1]) / s1};
        System.out.println(String.format("v1 = [%.4f, %.4f], u1 = [%.4f, %.4f]", v1[0], v1[1], u1[0], u1[1]));
        // step 3: the best rank 1 copy of A is s1 * u1 * v1^T
        double[][] A1 = new double[2][2];
        double sq = 0;
        for (int i = 0; i < 2; i++)
            for (int j = 0; j < 2; j++) {
                A1[i][j] = s1 * u1[i] * v1[j];
                sq += (A[i][j] - A1[i][j]) * (A[i][j] - A1[i][j]);
            }
        System.out.println(String.format("rank 1 copy = [[%.2f, %.2f], [%.2f, %.2f]]", A1[0][0], A1[0][1], A1[1][0], A1[1][1]));
        System.out.println(String.format("error = %.4f, the same as s2", Math.sqrt(sq)));
    }
}
''')

K.code('pca', py=r'''
import math

xs = [2.5, 0.5, 2.2, 1.9, 3.1, 2.3, 2.0, 1.0, 1.5, 1.1]
ys = [2.4, 0.7, 2.9, 2.2, 3.0, 2.7, 1.6, 1.1, 1.6, 0.9]
n = len(xs)
mx, my = sum(xs) / n, sum(ys) / n                 # step 1: the centre of the cloud
dx = [x - mx for x in xs]
dy = [y - my for y in ys]
sxx = sum(p * p for p in dx) / (n - 1)            # step 2: the covariance matrix
syy = sum(q * q for q in dy) / (n - 1)
sxy = sum(p * q for p, q in zip(dx, dy)) / (n - 1)
print(f"mean = ({mx:.2f}, {my:.2f})")
print(f"covariance = [[{sxx:.4f}, {sxy:.4f}], [{sxy:.4f}, {syy:.4f}]]")
tr, det = sxx + syy, sxx * syy - sxy * sxy        # step 3: its eigenvalues
gap = math.sqrt(tr * tr / 4 - det)
l1, l2 = tr / 2 + gap, tr / 2 - gap
v = [sxy, l1 - sxx]                               # step 4: the direction of PC1
size = math.hypot(v[0], v[1])
pc1 = [v[0] / size, v[1] / size]
print(f"eigenvalues = {l1:.4f} and {l2:.4f}")
print(f"PC1 = [{pc1[0]:.4f}, {pc1[1]:.4f}], explains {100 * l1 / (l1 + l2):.1f}% of the spread")
scores = [p * pc1[0] + q * pc1[1] for p, q in zip(dx, dy)]   # step 5: 2D becomes 1D
print("first 3 points on PC1:", " ".join(f"{s:.3f}" for s in scores[:3]))
''', js=r'''
const xs = [2.5, 0.5, 2.2, 1.9, 3.1, 2.3, 2.0, 1.0, 1.5, 1.1];
const ys = [2.4, 0.7, 2.9, 2.2, 3.0, 2.7, 1.6, 1.1, 1.6, 0.9];
const n = xs.length;
const sum = a => a.reduce((s, t) => s + t, 0);
const mx = sum(xs) / n, my = sum(ys) / n;          // step 1: the centre of the cloud
const dx = xs.map(x => x - mx);
const dy = ys.map(y => y - my);
const sxx = sum(dx.map(p => p * p)) / (n - 1);     // step 2: the covariance matrix
const syy = sum(dy.map(q => q * q)) / (n - 1);
const sxy = sum(dx.map((p, i) => p * dy[i])) / (n - 1);
console.log(`mean = (${mx.toFixed(2)}, ${my.toFixed(2)})`);
console.log(`covariance = [[${sxx.toFixed(4)}, ${sxy.toFixed(4)}], [${sxy.toFixed(4)}, ${syy.toFixed(4)}]]`);
const tr = sxx + syy, det = sxx * syy - sxy * sxy; // step 3: its eigenvalues
const gap = Math.sqrt(tr * tr / 4 - det);
const l1 = tr / 2 + gap, l2 = tr / 2 - gap;
const v = [sxy, l1 - sxx];                         // step 4: the direction of PC1
const size = Math.hypot(v[0], v[1]);
const pc1 = [v[0] / size, v[1] / size];
console.log(`eigenvalues = ${l1.toFixed(4)} and ${l2.toFixed(4)}`);
console.log(`PC1 = [${pc1[0].toFixed(4)}, ${pc1[1].toFixed(4)}], explains ${(100 * l1 / (l1 + l2)).toFixed(1)}% of the spread`);
const scores = dx.map((p, i) => p * pc1[0] + dy[i] * pc1[1]);   // step 5: 2D becomes 1D
console.log("first 3 points on PC1:", scores.slice(0, 3).map(s => s.toFixed(3)).join(" "));
''', ts=r'''
const xs: number[] = [2.5, 0.5, 2.2, 1.9, 3.1, 2.3, 2.0, 1.0, 1.5, 1.1];
const ys: number[] = [2.4, 0.7, 2.9, 2.2, 3.0, 2.7, 1.6, 1.1, 1.6, 0.9];
const n: number = xs.length;
const sum = (a: number[]): number => a.reduce((s, t) => s + t, 0);
const mx: number = sum(xs) / n, my: number = sum(ys) / n;   // step 1: the centre of the cloud
const dx: number[] = xs.map(x => x - mx);
const dy: number[] = ys.map(y => y - my);
const sxx: number = sum(dx.map(p => p * p)) / (n - 1);     // step 2: the covariance matrix
const syy: number = sum(dy.map(q => q * q)) / (n - 1);
const sxy: number = sum(dx.map((p, i) => p * dy[i])) / (n - 1);
console.log(`mean = (${mx.toFixed(2)}, ${my.toFixed(2)})`);
console.log(`covariance = [[${sxx.toFixed(4)}, ${sxy.toFixed(4)}], [${sxy.toFixed(4)}, ${syy.toFixed(4)}]]`);
const tr: number = sxx + syy, det: number = sxx * syy - sxy * sxy;   // step 3: its eigenvalues
const gap: number = Math.sqrt(tr * tr / 4 - det);
const l1: number = tr / 2 + gap, l2: number = tr / 2 - gap;
const v: number[] = [sxy, l1 - sxx];               // step 4: the direction of PC1
const size: number = Math.hypot(v[0], v[1]);
const pc1: number[] = [v[0] / size, v[1] / size];
console.log(`eigenvalues = ${l1.toFixed(4)} and ${l2.toFixed(4)}`);
console.log(`PC1 = [${pc1[0].toFixed(4)}, ${pc1[1].toFixed(4)}], explains ${(100 * l1 / (l1 + l2)).toFixed(1)}% of the spread`);
const scores: number[] = dx.map((p, i) => p * pc1[0] + dy[i] * pc1[1]);   // step 5: 2D becomes 1D
console.log("first 3 points on PC1:", scores.slice(0, 3).map(s => s.toFixed(3)).join(" "));
''', java=r'''
public class Pca {
    public static void main(String[] args) {
        double[] xs = {2.5, 0.5, 2.2, 1.9, 3.1, 2.3, 2.0, 1.0, 1.5, 1.1};
        double[] ys = {2.4, 0.7, 2.9, 2.2, 3.0, 2.7, 1.6, 1.1, 1.6, 0.9};
        int n = xs.length;
        double mx = 0, my = 0;
        for (int i = 0; i < n; i++) { mx += xs[i] / n; my += ys[i] / n; }   // step 1: the centre of the cloud
        double sxx = 0, syy = 0, sxy = 0;
        double[] dx = new double[n], dy = new double[n];
        for (int i = 0; i < n; i++) {
            dx[i] = xs[i] - mx;
            dy[i] = ys[i] - my;
            sxx += dx[i] * dx[i] / (n - 1);                 // step 2: the covariance matrix
            syy += dy[i] * dy[i] / (n - 1);
            sxy += dx[i] * dy[i] / (n - 1);
        }
        System.out.println(String.format("mean = (%.2f, %.2f)", mx, my));
        System.out.println(String.format("covariance = [[%.4f, %.4f], [%.4f, %.4f]]", sxx, sxy, sxy, syy));
        double tr = sxx + syy, det = sxx * syy - sxy * sxy; // step 3: its eigenvalues
        double gap = Math.sqrt(tr * tr / 4 - det);
        double l1 = tr / 2 + gap, l2 = tr / 2 - gap;
        double[] v = {sxy, l1 - sxx};                       // step 4: the direction of PC1
        double size = Math.hypot(v[0], v[1]);
        double[] pc1 = {v[0] / size, v[1] / size};
        System.out.println(String.format("eigenvalues = %.4f and %.4f", l1, l2));
        System.out.println(String.format("PC1 = [%.4f, %.4f], explains %.1f%% of the spread", pc1[0], pc1[1], 100 * l1 / (l1 + l2)));
        StringBuilder sb = new StringBuilder("first 3 points on PC1:");
        for (int i = 0; i < 3; i++) sb.append(String.format(" %.3f", dx[i] * pc1[0] + dy[i] * pc1[1]));   // step 5: 2D becomes 1D
        System.out.println(sb);
    }
}
''')

K.code('p_check', py=r'''
A = [[4, 1],
     [2, 3]]
for v in [[1, 1], [1, -2], [1, 0]]:
    Av = [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]]
    cross = Av[0] * v[1] - Av[1] * v[0]       # 0 exactly when Av lies along v
    if cross == 0:
        print(f"v = {v}: Av = {Av} = {Av[0] // v[0]} times v, an eigenvector")
    else:
        print(f"v = {v}: Av = {Av}, not a multiple of v")
print("trace =", A[0][0] + A[1][1], "= 5 + 2")
print("det =", A[0][0] * A[1][1] - A[0][1] * A[1][0], "= 5 times 2")
''', js=r'''
const A = [[4, 1],
           [2, 3]];
const s = v => "[" + v.join(", ") + "]";
for (const v of [[1, 1], [1, -2], [1, 0]]) {
  const Av = [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]];
  const cross = Av[0] * v[1] - Av[1] * v[0];   // 0 exactly when Av lies along v
  if (cross === 0) {
    console.log(`v = ${s(v)}: Av = ${s(Av)} = ${Av[0] / v[0]} times v, an eigenvector`);
  } else {
    console.log(`v = ${s(v)}: Av = ${s(Av)}, not a multiple of v`);
  }
}
console.log("trace =", A[0][0] + A[1][1], "= 5 + 2");
console.log("det =", A[0][0] * A[1][1] - A[0][1] * A[1][0], "= 5 times 2");
''', ts=r'''
const A: number[][] = [[4, 1],
                       [2, 3]];
const s = (v: number[]): string => "[" + v.join(", ") + "]";
for (const v of [[1, 1], [1, -2], [1, 0]]) {
  const Av: number[] = [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]];
  const cross: number = Av[0] * v[1] - Av[1] * v[0];   // 0 exactly when Av lies along v
  if (cross === 0) {
    console.log(`v = ${s(v)}: Av = ${s(Av)} = ${Av[0] / v[0]} times v, an eigenvector`);
  } else {
    console.log(`v = ${s(v)}: Av = ${s(Av)}, not a multiple of v`);
  }
}
console.log("trace =", A[0][0] + A[1][1], "= 5 + 2");
console.log("det =", A[0][0] * A[1][1] - A[0][1] * A[1][0], "= 5 times 2");
''', java=r'''
import java.util.Arrays;

public class PracticeCheck {
    public static void main(String[] args) {
        int[][] A = {{4, 1},
                     {2, 3}};
        int[][] tests = {{1, 1}, {1, -2}, {1, 0}};
        for (int[] v : tests) {
            int[] Av = {A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]};
            int cross = Av[0] * v[1] - Av[1] * v[0];   // 0 exactly when Av lies along v
            if (cross == 0) {
                System.out.println("v = " + Arrays.toString(v) + ": Av = " + Arrays.toString(Av) + " = " + Av[0] / v[0] + " times v, an eigenvector");
            } else {
                System.out.println("v = " + Arrays.toString(v) + ": Av = " + Arrays.toString(Av) + ", not a multiple of v");
            }
        }
        System.out.println("trace = " + (A[0][0] + A[1][1]) + " = 5 + 2");
        System.out.println("det = " + (A[0][0] * A[1][1] - A[0][1] * A[1][0]) + " = 5 times 2");
    }
}
''')

K.code('p_steady', py=r'''
import math

# each year 10% of city people move to the village and 5% of village people move to the city
T = [[0.90, 0.05],
     [0.10, 0.95]]
tr = T[0][0] + T[1][1]
det = T[0][0] * T[1][1] - T[0][1] * T[1][0]
gap = math.sqrt(tr * tr / 4 - det)
print(f"eigenvalues: {tr / 2 + gap:.2f} and {tr / 2 - gap:.2f}")
v = [T[0][1], 1 - T[0][0]]            # solves (T - I) v = 0, the eigenvector for 1
total = v[0] + v[1]
print(f"steady state: city {1000 * v[0] / total:.1f}, village {1000 * v[1] / total:.1f}")
state = [600.0, 400.0]
for year in range(100):
    state = [T[0][0] * state[0] + T[0][1] * state[1], T[1][0] * state[0] + T[1][1] * state[1]]
print(f"after 100 years: city {state[0]:.1f}, village {state[1]:.1f}")
''', js=r'''
// each year 10% of city people move to the village and 5% of village people move to the city
const T = [[0.90, 0.05],
           [0.10, 0.95]];
const tr = T[0][0] + T[1][1];
const det = T[0][0] * T[1][1] - T[0][1] * T[1][0];
const gap = Math.sqrt(tr * tr / 4 - det);
console.log(`eigenvalues: ${(tr / 2 + gap).toFixed(2)} and ${(tr / 2 - gap).toFixed(2)}`);
const v = [T[0][1], 1 - T[0][0]];     // solves (T - I) v = 0, the eigenvector for 1
const total = v[0] + v[1];
console.log(`steady state: city ${(1000 * v[0] / total).toFixed(1)}, village ${(1000 * v[1] / total).toFixed(1)}`);
let state = [600, 400];
for (let year = 0; year < 100; year++) {
  state = [T[0][0] * state[0] + T[0][1] * state[1], T[1][0] * state[0] + T[1][1] * state[1]];
}
console.log(`after 100 years: city ${state[0].toFixed(1)}, village ${state[1].toFixed(1)}`);
''', ts=r'''
// each year 10% of city people move to the village and 5% of village people move to the city
const T: number[][] = [[0.90, 0.05],
                       [0.10, 0.95]];
const tr: number = T[0][0] + T[1][1];
const det: number = T[0][0] * T[1][1] - T[0][1] * T[1][0];
const gap: number = Math.sqrt(tr * tr / 4 - det);
console.log(`eigenvalues: ${(tr / 2 + gap).toFixed(2)} and ${(tr / 2 - gap).toFixed(2)}`);
const v: number[] = [T[0][1], 1 - T[0][0]];   // solves (T - I) v = 0, the eigenvector for 1
const total: number = v[0] + v[1];
console.log(`steady state: city ${(1000 * v[0] / total).toFixed(1)}, village ${(1000 * v[1] / total).toFixed(1)}`);
let state: number[] = [600, 400];
for (let year = 0; year < 100; year++) {
  state = [T[0][0] * state[0] + T[0][1] * state[1], T[1][0] * state[0] + T[1][1] * state[1]];
}
console.log(`after 100 years: city ${state[0].toFixed(1)}, village ${state[1].toFixed(1)}`);
''', java=r'''
public class PracticeSteady {
    public static void main(String[] args) {
        // each year 10% of city people move to the village and 5% of village people move to the city
        double[][] T = {{0.90, 0.05},
                        {0.10, 0.95}};
        double tr = T[0][0] + T[1][1];
        double det = T[0][0] * T[1][1] - T[0][1] * T[1][0];
        double gap = Math.sqrt(tr * tr / 4 - det);
        System.out.println(String.format("eigenvalues: %.2f and %.2f", tr / 2 + gap, tr / 2 - gap));
        double[] v = {T[0][1], 1 - T[0][0]};      // solves (T - I) v = 0, the eigenvector for 1
        double total = v[0] + v[1];
        System.out.println(String.format("steady state: city %.1f, village %.1f", 1000 * v[0] / total, 1000 * v[1] / total));
        double[] state = {600, 400};
        for (int year = 0; year < 100; year++) {
            state = new double[]{T[0][0] * state[0] + T[0][1] * state[1], T[1][0] * state[0] + T[1][1] * state[1]};
        }
        System.out.println(String.format("after 100 years: city %.1f, village %.1f", state[0], state[1]));
    }
}
''')

K.code('p_power3', py=r'''
import math

C = [[4, 2, 0],
     [2, 3, 1],
     [0, 1, 2]]                       # a 3 x 3 covariance matrix
v = [1.0, 1.0, 1.0]
for step in range(1, 9):
    w = [sum(C[i][j] * v[j] for j in range(3)) for i in range(3)]
    size = math.sqrt(sum(t * t for t in w))
    v = [t / size for t in w]
    Cv = [sum(C[i][j] * v[j] for j in range(3)) for i in range(3)]
    lam = sum(p * q for p, q in zip(v, Cv))
    if step in (1, 2, 4, 8):
        print(f"step {step}: v = [{v[0]:.4f}, {v[1]:.4f}, {v[2]:.4f}], lambda = {lam:.4f}")
print(f"share of the total spread: {100 * lam / (4 + 3 + 2):.1f}%")
''', js=r'''
const C = [[4, 2, 0],
           [2, 3, 1],
           [0, 1, 2]];                // a 3 x 3 covariance matrix
let v = [1, 1, 1], lam = 0;
const mul = u => C.map(row => row.reduce((s, c, j) => s + c * u[j], 0));
for (let step = 1; step <= 8; step++) {
  const w = mul(v);
  const size = Math.hypot(...w);
  v = w.map(t => t / size);
  const Cv = mul(v);
  lam = v.reduce((s, p, i) => s + p * Cv[i], 0);
  if ([1, 2, 4, 8].includes(step)) {
    console.log(`step ${step}: v = [${v.map(t => t.toFixed(4)).join(", ")}], lambda = ${lam.toFixed(4)}`);
  }
}
console.log(`share of the total spread: ${(100 * lam / (4 + 3 + 2)).toFixed(1)}%`);
''', ts=r'''
const C: number[][] = [[4, 2, 0],
                       [2, 3, 1],
                       [0, 1, 2]];    // a 3 x 3 covariance matrix
let v: number[] = [1, 1, 1], lam: number = 0;
const mul = (u: number[]): number[] => C.map(row => row.reduce((s, c, j) => s + c * u[j], 0));
for (let step = 1; step <= 8; step++) {
  const w: number[] = mul(v);
  const size: number = Math.hypot(...w);
  v = w.map(t => t / size);
  const Cv: number[] = mul(v);
  lam = v.reduce((s, p, i) => s + p * Cv[i], 0);
  if ([1, 2, 4, 8].includes(step)) {
    console.log(`step ${step}: v = [${v.map(t => t.toFixed(4)).join(", ")}], lambda = ${lam.toFixed(4)}`);
  }
}
console.log(`share of the total spread: ${(100 * lam / (4 + 3 + 2)).toFixed(1)}%`);
''', java=r'''
public class PracticePower3 {
    static double[] mul(double[][] C, double[] u) {
        double[] r = new double[3];
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++) r[i] += C[i][j] * u[j];
        return r;
    }

    public static void main(String[] args) {
        double[][] C = {{4, 2, 0},
                        {2, 3, 1},
                        {0, 1, 2}};        // a 3 x 3 covariance matrix
        double[] v = {1, 1, 1};
        double lam = 0;
        for (int step = 1; step <= 8; step++) {
            double[] w = mul(C, v);
            double size = Math.sqrt(w[0] * w[0] + w[1] * w[1] + w[2] * w[2]);
            v = new double[]{w[0] / size, w[1] / size, w[2] / size};
            double[] Cv = mul(C, v);
            lam = v[0] * Cv[0] + v[1] * Cv[1] + v[2] * Cv[2];
            if (step == 1 || step == 2 || step == 4 || step == 8) {
                System.out.println(String.format("step %d: v = [%.4f, %.4f, %.4f], lambda = %.4f", step, v[0], v[1], v[2], lam));
            }
        }
        System.out.println(String.format("share of the total spread: %.1f%%", 100 * lam / (4 + 3 + 2)));
    }
}
''')

K.code('p_lowrank', py=r'''
import math

img = [[9, 9, 8, 1],
       [9, 9, 8, 1],
       [8, 8, 7, 1],
       [1, 1, 1, 1]]                  # a tiny 4 x 4 grey picture
n = len(img)
AtA = [[sum(img[k][i] * img[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
v = [1.0] * n
for _ in range(6):                    # power iteration finds the top right singular vector
    w = [sum(AtA[i][j] * v[j] for j in range(n)) for i in range(n)]
    size = math.sqrt(sum(t * t for t in w))
    v = [t / size for t in w]
Av = [sum(img[i][j] * v[j] for j in range(n)) for i in range(n)]
s1 = math.sqrt(sum(t * t for t in Av))
u = [t / s1 for t in Av]
approx = [[s1 * u[i] * v[j] for j in range(n)] for i in range(n)]
for row in approx:
    print(" ".join(f"{t:5.2f}" for t in row))
total = sum(t * t for row in img for t in row)
err = sum((img[i][j] - approx[i][j]) ** 2 for i in range(n) for j in range(n))
print(f"sigma1 = {s1:.3f}, numbers stored: {2 * n + 1} instead of {n * n}")
print(f"energy kept: {100 * (1 - err / total):.2f}%")
''', js=r'''
const img = [[9, 9, 8, 1],
             [9, 9, 8, 1],
             [8, 8, 7, 1],
             [1, 1, 1, 1]];           // a tiny 4 x 4 grey picture
const n = img.length, idx = [...Array(n).keys()];
const AtA = idx.map(i => idx.map(j => idx.reduce((s, k) => s + img[k][i] * img[k][j], 0)));
let v = new Array(n).fill(1);
for (let it = 0; it < 6; it++) {      // power iteration finds the top right singular vector
  const w = idx.map(i => idx.reduce((s, j) => s + AtA[i][j] * v[j], 0));
  const size = Math.hypot(...w);
  v = w.map(t => t / size);
}
const Av = idx.map(i => idx.reduce((s, j) => s + img[i][j] * v[j], 0));
const s1 = Math.hypot(...Av);
const u = Av.map(t => t / s1);
const approx = idx.map(i => idx.map(j => s1 * u[i] * v[j]));
for (const row of approx) console.log(row.map(t => t.toFixed(2).padStart(5)).join(" "));
let total = 0, err = 0;
for (const i of idx) for (const j of idx) { total += img[i][j] ** 2; err += (img[i][j] - approx[i][j]) ** 2; }
console.log(`sigma1 = ${s1.toFixed(3)}, numbers stored: ${2 * n + 1} instead of ${n * n}`);
console.log(`energy kept: ${(100 * (1 - err / total)).toFixed(2)}%`);
''', ts=r'''
const img: number[][] = [[9, 9, 8, 1],
                         [9, 9, 8, 1],
                         [8, 8, 7, 1],
                         [1, 1, 1, 1]];   // a tiny 4 x 4 grey picture
const n: number = img.length, idx: number[] = [...Array(n).keys()];
const AtA: number[][] = idx.map(i => idx.map(j => idx.reduce((s, k) => s + img[k][i] * img[k][j], 0)));
let v: number[] = new Array<number>(n).fill(1);
for (let it = 0; it < 6; it++) {      // power iteration finds the top right singular vector
  const w: number[] = idx.map(i => idx.reduce((s, j) => s + AtA[i][j] * v[j], 0));
  const size: number = Math.hypot(...w);
  v = w.map(t => t / size);
}
const Av: number[] = idx.map(i => idx.reduce((s, j) => s + img[i][j] * v[j], 0));
const s1: number = Math.hypot(...Av);
const u: number[] = Av.map(t => t / s1);
const approx: number[][] = idx.map(i => idx.map(j => s1 * u[i] * v[j]));
for (const row of approx) console.log(row.map(t => t.toFixed(2).padStart(5)).join(" "));
let total: number = 0, err: number = 0;
for (const i of idx) for (const j of idx) { total += img[i][j] ** 2; err += (img[i][j] - approx[i][j]) ** 2; }
console.log(`sigma1 = ${s1.toFixed(3)}, numbers stored: ${2 * n + 1} instead of ${n * n}`);
console.log(`energy kept: ${(100 * (1 - err / total)).toFixed(2)}%`);
''', java=r'''
public class PracticeLowRank {
    public static void main(String[] args) {
        double[][] img = {{9, 9, 8, 1},
                          {9, 9, 8, 1},
                          {8, 8, 7, 1},
                          {1, 1, 1, 1}};   // a tiny 4 x 4 grey picture
        int n = img.length;
        double[][] AtA = new double[n][n];
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                for (int k = 0; k < n; k++) AtA[i][j] += img[k][i] * img[k][j];
        double[] v = {1, 1, 1, 1};
        for (int it = 0; it < 6; it++) {       // power iteration finds the top right singular vector
            double[] w = new double[n];
            double size = 0;
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) w[i] += AtA[i][j] * v[j];
                size += w[i] * w[i];
            }
            size = Math.sqrt(size);
            for (int i = 0; i < n; i++) v[i] = w[i] / size;
        }
        double[] Av = new double[n];
        double s1 = 0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) Av[i] += img[i][j] * v[j];
            s1 += Av[i] * Av[i];
        }
        s1 = Math.sqrt(s1);
        double total = 0, err = 0;
        for (int i = 0; i < n; i++) {
            StringBuilder sb = new StringBuilder();
            for (int j = 0; j < n; j++) {
                double t = s1 * (Av[i] / s1) * v[j];
                sb.append(j > 0 ? " " : "").append(String.format("%5.2f", t));
                total += img[i][j] * img[i][j];
                err += (img[i][j] - t) * (img[i][j] - t);
            }
            System.out.println(sb);
        }
        System.out.println(String.format("sigma1 = %.3f, numbers stored: %d instead of %d", s1, 2 * n + 1, n * n));
        System.out.println(String.format("energy kept: %.2f%%", 100 * (1 - err / total)));
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('what', '🧭', 'Eigenvectors: the directions a matrix keeps', f'''
<p>Chapter 4 showed that a matrix moves every arrow in the plane. Most arrows get turned to a new direction. A few special arrows only get <b>longer, shorter or flipped</b>, and stay on their own line. These are the <b>eigenvectors</b> of the matrix, and the stretch factor is the <b>eigenvalue</b>, written λ (the Greek letter lambda).</p>
{fx('The eigen equation', 'A v = λ v &nbsp;&nbsp; with v ≠ 0', 'v is the eigenvector (the direction that survives). λ is the eigenvalue (how much it is stretched). λ = 2 doubles v, λ = 0.5 halves it, λ = −1 flips it.')}
{viz('eigen')}
<div class="grid2">
<div class="box"><h4>🔍 How to check one</h4><p>Multiply A by v. If the answer is a plain multiple of v, v is an eigenvector and the multiple is λ. With A = [[2, 1], [1, 2]] and v = [1, 1], Av = [3, 3] = 3 × [1, 1], so λ = 3.</p></div>
<div class="box"><h4>🚫 Not every matrix has real ones</h4><p>A 90° rotation turns every arrow, so no direction is kept. Its eigenvalues are complex numbers, and you will see "no real eigenvectors" in the animation.</p></div>
</div>
{life('Spin a globe. Every point moves except the points on the axis through the poles. That axis is the eigenvector of the spin, with eigenvalue 1, because those points stay exactly where they are.')}
{trick('"Eigen" is German for "own". An eigenvector is a direction the matrix owns, the one it does not turn.')}
''', kw=['eigenvector', 'eigenvalue', 'Av = λv', 'lambda', 'special direction']),

    part('find', '🔎', 'Finding eigenvalues by hand', f'''
<p>Move everything to one side: Av − λv = 0, which is (A − λI)v = 0. A non zero v can only solve this when the matrix A − λI squashes space flat, which means its determinant is zero. That gives an ordinary equation in λ, called the <b>characteristic equation</b>.</p>
{fxs(fx('Characteristic equation', 'det(A − λI) = 0', 'Solve for λ. A 2 × 2 matrix gives a quadratic, a 3 × 3 gives a cubic.'),
         fx('Shortcut for 2 × 2', 'λ² − (trace) λ + det = 0', f'trace = a + d, det = ad − bc. Then λ = {frac("trace ± √(trace² − 4 det)", "2")}'))}
{worked('Eigenvalues and eigenvectors of A = [[2, 1], [1, 2]]', [
        'Trace and determinant: <span class="eq">trace = 2 + 2 = 4</span>, <span class="eq">det = 2 × 2 − 1 × 1 = 3</span>',
        'Characteristic equation: <span class="eq">λ² − 4λ + 3 = 0</span>',
        'Factorise: <span class="eq">(λ − 3)(λ − 1) = 0</span>, so <span class="eq">λ₁ = 3</span> and <span class="eq">λ₂ = 1</span>',
        'For λ = 3: <span class="eq">A − 3I = [[−1, 1], [1, −1]]</span>. The first row says −x + y = 0, so y = x and <span class="eq">v₁ = [1, 1]</span>',
        'For λ = 1: <span class="eq">A − I = [[1, 1], [1, 1]]</span>. The first row says x + y = 0, so <span class="eq">v₂ = [1, −1]</span>',
        'Check: <span class="eq">A[1, −1] = [2 − 1, 1 − 2] = [1, −1] = 1 × v₂</span> ✔'])}
{code('eig2', 'Eigenvalues from the trace and determinant, then each eigenvector')}
<div class="tip">Any multiple of an eigenvector is also an eigenvector. [1, 1], [2, 2] and [−5, −5] all point along the same line. Libraries usually scale it to length 1, so NumPy gives [0.7071, 0.7071] for [1, 1].</div>
{trick('Triangular or diagonal matrix? The eigenvalues are simply the numbers on the diagonal. No equation needed.')}
''', kw=['characteristic equation', 'det(A − λI) = 0', 'trace', 'find eigenvalues', '2x2 eigenvalues']),

    part('props', '🧩', 'Rules that save time', f'''
<p>Eigenvalues come with a handful of rules that let you check your work in seconds and that explain why they are so useful.</p>
{table(['Rule', 'In symbols', 'Example with [[2, 1], [1, 2]]'], [
        ['Sum of eigenvalues = trace', 'λ₁ + λ₂ + … = a₁₁ + a₂₂ + …', '3 + 1 = 4 = 2 + 2'],
        ['Product of eigenvalues = determinant', 'λ₁ × λ₂ × … = det A', '3 × 1 = 3 = det A'],
        ['Powers', 'Aⁿ v = λⁿ v', 'A¹⁰ [1, 1] = 3¹⁰ [1, 1] = 59049 [1, 1]'],
        ['Inverse', 'A⁻¹ v = (1/λ) v', 'eigenvalues of A⁻¹ are 1/3 and 1'],
        ['Symmetric matrix', 'A = Aᵀ gives real λ and perpendicular v', '[1, 1] · [1, −1] = 0'],
    ])}
{fx('Diagonalisation (eigendecomposition)', 'A = P D P⁻¹ &nbsp;&nbsp; and &nbsp;&nbsp; Aⁿ = P Dⁿ P⁻¹', 'P has the eigenvectors as its columns. D is diagonal with the eigenvalues. For a symmetric matrix P is orthogonal, so P⁻¹ = Pᵀ.')}
<p>Why this matters: raising a matrix to the 100th power directly needs 99 matrix multiplications. With A = PDP⁻¹ you just raise each eigenvalue to the 100th power. It also tells the long run story. In a Markov chain the eigenvalue 1 belongs to the <b>steady state</b>, and every smaller eigenvalue fades away as its power shrinks to zero.</p>
{code('p_steady', 'The long run of the city and village model from Chapter 4')}
{ml('Training deep networks: the eigenvalues of the weight matrices decide whether signals blow up (|λ| > 1) or vanish (|λ| < 1) as they pass through many layers. This is the exploding and vanishing gradient problem in recurrent networks.')}
{trick('Two quick checks after finding eigenvalues: do they add up to the trace, and multiply to the determinant? If not, there is an arithmetic slip.')}
''', kw=['trace', 'determinant', 'diagonalisation', 'eigendecomposition', 'PDP⁻¹', 'matrix power', 'steady state', 'symmetric matrix']),

    part('power', '🔁', 'Power iteration and PageRank', f'''
<p>Real matrices have thousands or millions of rows, so nobody solves a characteristic equation. A simple and famous method is <b>power iteration</b>: start with any vector, multiply by A, scale it back to length 1, and repeat. The direction with the biggest |λ| grows fastest, so the vector swings round to the top eigenvector.</p>
{fx('Power iteration', 'v ← A v / ‖A v‖ &nbsp;&nbsp;&nbsp; λ ≈ vᵀ A v', 'The second formula (the Rayleigh quotient) reads off the eigenvalue once v has settled.')}
{worked('Two rounds of power iteration on [[2, 1], [1, 2]] starting from [1, 0]', [
        'Multiply: <span class="eq">A[1, 0] = [2, 1]</span>. Its length is <span class="eq">√(4 + 1) = √5 ≈ 2.236</span>, so v = <span class="eq">[0.894, 0.447]</span>',
        'Estimate: <span class="eq">Av = [2.236, 1.789]</span> and <span class="eq">vᵀAv = 0.894 × 2.236 + 0.447 × 1.789 = 2.80</span>',
        'Multiply again: <span class="eq">A[2, 1] = [5, 4]</span>, length <span class="eq">√41 ≈ 6.403</span>, so v = <span class="eq">[0.781, 0.625]</span>',
        'The estimate rises to about <span class="eq">2.98</span>. The true answer is λ = 3 with direction [0.707, 0.707]. Each round closes the gap by the ratio λ₂/λ₁ = 1/3.'])}
{code('power', 'Power iteration, six rounds')}
<div class="box"><h4>🌐 PageRank in one paragraph</h4><p>The first Google ranking method treated the web as a Markov chain: a surfer clicks a random link on each page. The matrix of click chances has a top eigenvalue of 1, and its eigenvector gives every page a score, the share of time the surfer spends there. Power iteration on billions of pages found it.</p></div>
{ml('Power iteration and its relatives (Lanczos, randomised SVD) are how libraries find the top few eigenvectors of huge matrices for PCA, spectral clustering and graph neural networks without computing all of them.')}
''', kw=['power iteration', 'rayleigh quotient', 'dominant eigenvalue', 'pagerank', 'convergence']),

    part('svd', '🧱', 'Singular value decomposition (SVD)', f'''
<p>Eigenvectors need a square matrix, and even then they might not exist. The <b>SVD</b> works for <b>every</b> matrix of any shape. It says each matrix is three simple moves in a row: a rotation, a stretch along the axes, and another rotation.</p>
{fx('Singular value decomposition', 'A = U Σ Vᵀ', 'For an m × n matrix: U is m × m and orthogonal, Σ is m × n with the singular values σ₁ ≥ σ₂ ≥ … ≥ 0 on its diagonal, and V is n × n and orthogonal.')}
{viz('svdviz')}
{fxs(fx('Where the parts come from', 'σᵢ = √(eigenvalues of AᵀA)', 'The columns of V are the eigenvectors of AᵀA. Then uᵢ = A vᵢ / σᵢ.'),
         fx('Best rank k copy (Eckart and Young)', 'Aₖ = σ₁u₁v₁ᵀ + … + σₖuₖvₖᵀ', 'Keeping the k biggest singular values gives the closest possible rank k matrix. The error is set by the singular values you dropped.'))}
{worked('SVD of A = [[3, 0], [4, 5]]', [
        'Form <span class="eq">AᵀA = [[3·3 + 4·4, 3·0 + 4·5], [0·3 + 5·4, 0·0 + 5·5]] = [[25, 20], [20, 25]]</span>',
        'Its trace is 50 and determinant <span class="eq">625 − 400 = 225</span>, so <span class="eq">λ² − 50λ + 225 = 0</span>, giving λ = 45 and λ = 5',
        'Singular values: <span class="eq">σ₁ = √45 ≈ 6.708</span> and <span class="eq">σ₂ = √5 ≈ 2.236</span>. Check: <span class="eq">σ₁ × σ₂ = √225 = 15 = |det A|</span> ✔',
        'v₁ is the eigenvector of AᵀA for 45: <span class="eq">[1, 1]/√2</span>. Then <span class="eq">u₁ = A v₁ / σ₁ = [3, 9] / √90 ≈ [0.316, 0.949]</span>',
        'Best rank 1 copy: <span class="eq">σ₁u₁v₁ᵀ = [[1.5, 1.5], [4.5, 4.5]]</span>. The leftover error is exactly σ₂ ≈ 2.236.'])}
{code('svd2', 'Singular values, the first singular vectors and a rank 1 copy')}
{table(['Use of SVD', 'What it does'], [
        ['Image compression', 'keep the top k singular values of the picture matrix'],
        ['Recommendations', 'the Netflix Prize matrix of users × films was filled in with low rank factorisations like the SVD'],
        ['Search (latent semantic analysis)', 'SVD of a words × documents table groups words with related meanings'],
        ['Pseudo inverse and least squares', 'A⁺ = V Σ⁺ Uᵀ solves regression even when XᵀX has no inverse'],
    ])}
{trick('Remember "rotate, stretch, rotate". Vᵀ turns the input, Σ stretches along the axes, U turns the result. The circle of all unit inputs always becomes an ellipse whose half axes are the singular values.')}
''', kw=['svd', 'singular value decomposition', 'singular values', 'UΣVᵀ', 'low rank approximation', 'eckart young', 'image compression', 'pseudo inverse']),

    part('pca', '🎯', 'Principal component analysis (PCA)', f'''
<p><b>PCA</b> finds the directions in which your data spreads out the most. Keep the top few and you can describe 100 features with, say, 10 numbers, while keeping most of the information. It is eigenvectors applied to data.</p>
{table(['Step', 'What you do', 'Why'], [
        ['1. Centre', 'subtract the mean of every feature', 'so the cloud sits around the origin'],
        ['2. Covariance', 'C = XᵀX / (n − 1) for the centred X', 'C says how features vary together'],
        ['3. Eigen', 'find the eigenvalues and eigenvectors of C', 'eigenvectors are the principal directions'],
        ['4. Sort and keep', 'order by eigenvalue, keep the top k', 'eigenvalue = variance along that direction'],
        ['5. Project', 'scores = X × (top k eigenvectors)', 'each row becomes k numbers'],
    ])}
{viz('pca')}
{fxs(fx('Covariance of two features', f'cov(x, y) = {frac("Σ (xᵢ − x̄)(yᵢ − ȳ)", "n − 1")}', 'Positive: they rise together. Negative: one rises as the other falls. The diagonal of C holds the variances.'),
         fx('Explained variance ratio', f'share of PC k = {frac("λₖ", "λ₁ + λ₂ + … + λₙ")}', 'Keep enough components to reach about 90 to 95 percent.'))}
{code('pca', 'PCA from scratch on ten 2D points')}
<div class="warn">Scale your features first. If height is in millimetres and weight in tonnes, the millimetre column has a huge variance only because of its unit, and PCA will think it is the most important direction. Standardise each column (subtract the mean, divide by the standard deviation) before PCA.</div>
{ml('In practice PCA is computed with the SVD of the centred data matrix X = UΣVᵀ. The columns of V are the principal directions and the eigenvalues of C are σᵢ² / (n − 1). This is what scikit learn PCA does, and it is more accurate than forming C.')}
{life('A clothing company measures 20 body sizes for each customer. PCA finds that one direction ("overall size") explains most of the spread, and a second ("tall and thin versus short and broad") explains much of the rest. Two numbers now guide the S, M, L sizing.')}
''', kw=['pca', 'principal component analysis', 'covariance matrix', 'explained variance', 'dimensionality reduction', 'standardise', 'scree plot']),

    part('ml', '🤖', 'Where machine learning uses all this', f'''
<p>Eigenvalues and the SVD appear wherever a model needs the "main directions" of something. Here is a quick map, which later chapters revisit.</p>
{table(['Area', 'What the eigen idea gives'], [
        ['Dimensionality reduction', 'PCA compresses features, speeds up training and lets you plot high dimensional data in 2D'],
        ['Optimisation (Chapter 8)', 'the eigenvalues of the Hessian describe the shape of the loss surface. The ratio λmax / λmin, the condition number, says how slow gradient descent will be'],
        ['Spectral clustering', 'eigenvectors of a graph Laplacian split points into groups that ordinary k means misses'],
        ['Recommenders', 'a low rank factorisation of the users × items table predicts missing ratings'],
        ['Large language models', 'LoRA fine tuning adds a low rank update, and SVD is used to compress weight matrices'],
        ['Stability', 'eigenvalues of recurrent weight matrices above 1 make signals explode, below 1 make them vanish'],
    ])}
{fx('Condition number', 'κ(A) = σmax / σmin', 'Large κ means a tiny change in the input can cause a large change in the answer. Near duplicate features make κ huge, which is why ridge regression adds λI to XᵀX.')}
{code('p_lowrank', 'Compressing a tiny picture with one singular value')}
{trick('Big eigenvalue = important direction. Tiny eigenvalue = direction you can usually drop. Zero eigenvalue = a direction the matrix throws away completely.')}
''', kw=['condition number', 'hessian eigenvalues', 'spectral clustering', 'low rank', 'LoRA', 'recommender', 'matrix factorisation']),
]

INFO = {
    'title': 'Eigen, SVD and PCA find the main directions',
    'panels': [
        {'s': [['e', '🧭'], ['t', 'A v = λ v', {'b': 1}]], 'h': 'Eigenvector', 't': 'A direction the matrix keeps.', 'more': 'λ says how much it is stretched.'},
        {'s': [['e', '🔎'], ['t', 'det(A − λI) = 0', {'b': 1}]], 'h': 'Find them', 't': 'Solve the characteristic equation.', 'more': 'Sum of λ = trace, product of λ = det.'},
        {'s': [['e', '🧱'], ['t', 'A = U Σ Vᵀ', {'b': 1}]], 'h': 'SVD', 't': 'Rotate, stretch, rotate.', 'more': 'Works for every matrix. Keep the top σ to compress.'},
        {'s': [['e', '🎯'], ['b', [9, 5, 2, 1]]], 'h': 'PCA', 't': 'Eigenvectors of the covariance.', 'more': 'Keep the components that explain most of the variance.'},
    ],
    'remember': 'An eigenvector keeps its direction: Av = λv. Find λ from det(A − λI) = 0, and check that the eigenvalues add to the trace and multiply to the determinant. SVD writes any matrix as rotate, stretch, rotate. PCA takes the top eigenvectors of the covariance matrix to keep the most spread with the fewest numbers.',
}

REAL = [
    ['🌐', 'Web search ranking', 'PageRank scored web pages with the top eigenvector of the web link matrix, found by power iteration.'],
    ['🖼️', 'Face recognition', 'The "eigenfaces" method ran PCA on thousands of face photos. Each face became a mix of about 100 main face patterns.'],
    ['🎬', 'Film recommendations', 'Teams in the Netflix Prize filled in a huge users × films table with low rank factorisations related to the SVD.'],
]

K.say('top', 'Welcome',
      'Some directions are special for a matrix. It only stretches them and never turns them. These are eigenvectors. In this chapter you will hunt for them with an animation, find them by hand, meet the singular value decomposition, and use both to compress data with principal component analysis.',
      'कुछ दिशाएँ matrix के लिए ख़ास होती हैं। Matrix उन्हें सिर्फ़ खींचता है, घुमाता नहीं। ये eigenvectors हैं। इस अध्याय में आप animation से इन्हें ढूँढेंगे, हाथ से निकालेंगे, singular value decomposition सीखेंगे, और principal component analysis से data छोटा करेंगे।',
      'ಕೆಲವು ದಿಕ್ಕುಗಳು matrix ಗೆ ವಿಶೇಷ. Matrix ಅವನ್ನು ಉದ್ದ ಮಾಡುತ್ತದೆ, ತಿರುಗಿಸುವುದಿಲ್ಲ. ಇವು eigenvectors. ಈ ಅಧ್ಯಾಯದಲ್ಲಿ animation ನಲ್ಲಿ ಹುಡುಕಿ, ಕೈಯಿಂದ ಕಂಡುಹಿಡಿದು, SVD ಮತ್ತು PCA ಕಲಿಯುತ್ತೀರಿ.',
      'କିଛି ଦିଗ matrix ପାଇଁ ବିଶେଷ। Matrix ସେଗୁଡ଼ିକୁ କେବଳ ଲମ୍ବା କରେ, ଘୁରାଏ ନାହିଁ। ଏଗୁଡ଼ିକ eigenvectors। ଏହି ଅଧ୍ୟାୟରେ animation ରେ ଖୋଜି, ହାତରେ ବାହାର କରି, SVD ଓ PCA ଶିଖିବେ।',
      'بعض الاتجاهات خاصة بالنسبة للمصفوفة، فهي تمدها فقط ولا تديرها. هذه هي المتجهات الذاتية. في هذا الفصل تبحث عنها بالرسوم المتحركة، وتجدها باليد، وتتعرف على تحليل القيم المنفردة، وتستخدمهما لضغط البيانات بتحليل المكونات الرئيسية.',
      'Manche Richtungen sind für eine Matrix besonders. Sie werden nur gestreckt, nie gedreht. Das sind Eigenvektoren. In diesem Kapitel suchst du sie mit einer Animation, berechnest sie von Hand, lernst die Singulärwertzerlegung kennen und komprimierst damit Daten mit der Hauptkomponentenanalyse.')
K.say('what', 'Eigenvectors',
      'An eigenvector is an arrow that a matrix only stretches, shrinks or flips. A times v equals lambda times v. Lambda is the eigenvalue, the stretch factor. Drag the arrow in the animation until the two arrows line up.',
      'Eigenvector वह तीर है जिसे matrix सिर्फ़ खींचता, सिकोड़ता या पलटता है। A गुणा v बराबर lambda गुणा v। Lambda eigenvalue है। Animation में तीर खींचें जब तक दोनों तीर एक रेखा पर न आ जाएँ।',
      'Eigenvector ಎಂದರೆ matrix ಕೇವಲ ಉದ್ದ, ಚಿಕ್ಕ ಅಥವಾ ತಿರುಗುಮುರುಗು ಮಾಡುವ ಬಾಣ. A ಗುಣಿಸು v ಸಮ lambda ಗುಣಿಸು v. Lambda eigenvalue.',
      'Eigenvector ହେଉଛି ସେହି ତୀର ଯାହାକୁ matrix କେବଳ ଲମ୍ବା, ଛୋଟ କିମ୍ବା ଓଲଟା କରେ। A ଗୁଣନ v ସମାନ lambda ଗୁଣନ v। Lambda eigenvalue।',
      'المتجه الذاتي سهم تمده المصفوفة أو تقلصه أو تقلبه فقط. A في v يساوي لامدا في v، ولامدا هي القيمة الذاتية. اسحب السهم في الرسم حتى يصطف السهمان.',
      'Ein Eigenvektor ist ein Pfeil, den die Matrix nur streckt, staucht oder umdreht. A mal v gleich Lambda mal v. Lambda ist der Eigenwert. Ziehe den Pfeil in der Animation, bis beide Pfeile auf einer Linie liegen.')
K.say('find', 'Finding eigenvalues',
      'Solve the characteristic equation, the determinant of A minus lambda I equals zero. For a two by two matrix this is lambda squared minus trace times lambda plus determinant equals zero. Then put each lambda back to find its eigenvector.',
      'Characteristic equation हल करें, A घटा lambda I का determinant शून्य। दो गुणा दो matrix के लिए lambda का वर्ग घटा trace गुणा lambda जमा determinant बराबर शून्य। फिर हर lambda से eigenvector निकालें।',
      'Characteristic equation ಬಿಡಿಸಿ, A ಕಳೆ lambda I ನ determinant ಸೊನ್ನೆ. ಎರಡು ಗುಣಿಸು ಎರಡು matrix ಗೆ lambda ವರ್ಗ ಕಳೆ trace ಗುಣಿಸು lambda ಸೇರಿಸು determinant ಸೊನ್ನೆ.',
      'Characteristic equation ସମାଧାନ କରନ୍ତୁ, A ବିୟୋଗ lambda I ର determinant ଶୂନ। ଦୁଇ ଗୁଣନ ଦୁଇ matrix ପାଇଁ lambda ବର୍ଗ ବିୟୋଗ trace ଗୁଣନ lambda ଯୋଗ determinant ଶୂନ।',
      'حل المعادلة المميزة، محدد A ناقص لامدا I يساوي صفرًا. للمصفوفة اثنين في اثنين تصبح لامدا تربيع ناقص الأثر في لامدا زائد المحدد يساوي صفرًا. ثم عوض كل لامدا لتجد متجهها.',
      'Löse die charakteristische Gleichung, die Determinante von A minus Lambda I gleich null. Bei zwei mal zwei ist das Lambda Quadrat minus Spur mal Lambda plus Determinante gleich null. Setze dann jedes Lambda ein, um seinen Eigenvektor zu finden.')
K.say('props', 'Useful rules',
      'The eigenvalues add up to the trace and multiply to the determinant. Powers of a matrix just raise the eigenvalues to that power. A symmetric matrix has real eigenvalues and perpendicular eigenvectors. In a Markov chain the eigenvalue one gives the steady state.',
      'Eigenvalues का जोड़ trace और गुणनफल determinant होता है। Matrix की power में eigenvalues की भी वही power होती है। Symmetric matrix के eigenvalues real और eigenvectors लंब होते हैं। Markov chain में eigenvalue एक steady state देता है।',
      'Eigenvalues ಮೊತ್ತ trace, ಗುಣಲಬ್ಧ determinant. Symmetric matrix ನ eigenvalues real, eigenvectors ಲಂಬ. Markov chain ನಲ್ಲಿ eigenvalue ಒಂದು steady state.',
      'Eigenvalues ର ଯୋଗଫଳ trace, ଗୁଣଫଳ determinant। Symmetric matrix ର eigenvalues real, eigenvectors ଲମ୍ବ। Markov chain ରେ eigenvalue ଏକ steady state।',
      'مجموع القيم الذاتية يساوي الأثر وحاصل ضربها يساوي المحدد. وقوى المصفوفة ترفع القيم الذاتية للقوة نفسها. والمصفوفة المتماثلة قيمها حقيقية ومتجهاتها متعامدة، وفي سلسلة ماركوف القيمة واحد تعطي الحالة المستقرة.',
      'Die Eigenwerte ergeben addiert die Spur und multipliziert die Determinante. Potenzen einer Matrix potenzieren einfach die Eigenwerte. Eine symmetrische Matrix hat reelle Eigenwerte und senkrechte Eigenvektoren. In einer Markow Kette liefert der Eigenwert eins den stabilen Zustand.')
K.say('power', 'Power iteration',
      'Start with any vector, multiply it by the matrix, shrink it back to length one, and repeat. It swings round to the eigenvector with the biggest eigenvalue. Google PageRank found its scores this way.',
      'कोई भी vector लें, matrix से गुणा करें, length एक पर वापस लाएँ, और दोहराएँ। यह सबसे बड़े eigenvalue वाले eigenvector की ओर घूम जाता है। Google PageRank ने ऐसे ही scores निकाले।',
      'ಯಾವುದೇ vector ತೆಗೆದು matrix ನಿಂದ ಗುಣಿಸಿ, length ಒಂದಕ್ಕೆ ಇಳಿಸಿ, ಪುನರಾವರ್ತಿಸಿ. ಅದು ದೊಡ್ಡ eigenvalue ನ eigenvector ಕಡೆ ತಿರುಗುತ್ತದೆ.',
      'ଯେକୌଣସି vector ନେଇ matrix ରେ ଗୁଣନ କରନ୍ତୁ, length ଏକ କରନ୍ତୁ, ପୁନରାବୃତ୍ତି କରନ୍ତୁ। ଏହା ସବୁଠୁ ବଡ଼ eigenvalue ର eigenvector ଆଡ଼କୁ ଘୁରିଯାଏ।',
      'ابدأ بأي متجه، واضربه في المصفوفة، وأعده إلى طول واحد، وكرر. سيدور نحو المتجه الذاتي صاحب أكبر قيمة ذاتية. هكذا وجد ترتيب صفحات غوغل درجاته.',
      'Nimm einen beliebigen Vektor, multipliziere mit der Matrix, bringe ihn auf Länge eins zurück und wiederhole. Er dreht sich zum Eigenvektor mit dem größten Eigenwert. So fand Google PageRank seine Werte.')
K.say('svd', 'Singular value decomposition',
      'Every matrix, of any shape, is a rotation, then a stretch along the axes, then another rotation. A equals U Sigma V transpose. The stretches are the singular values. Keeping only the biggest ones gives the best small copy of the matrix.',
      'हर matrix, किसी भी shape का, एक rotation, फिर axes पर खिंचाव, फिर एक और rotation है। A बराबर U Sigma V transpose। खिंचाव singular values हैं। सबसे बड़े रखने से matrix की सबसे अच्छी छोटी copy मिलती है।',
      'ಯಾವುದೇ matrix ಒಂದು rotation, ನಂತರ axes ಉದ್ದಕ್ಕೂ stretch, ನಂತರ ಇನ್ನೊಂದು rotation. A ಸಮ U Sigma V transpose. ದೊಡ್ಡ singular values ಉಳಿಸಿದರೆ ಉತ್ತಮ ಚಿಕ್ಕ copy.',
      'ପ୍ରତ୍ୟେକ matrix ଏକ rotation, ତାପରେ axes ରେ stretch, ତାପରେ ଆଉ ଏକ rotation। A ସମାନ U Sigma V transpose। ବଡ଼ singular values ରଖିଲେ ଭଲ ଛୋଟ copy ମିଳେ।',
      'كل مصفوفة بأي شكل هي دوران، ثم تمديد على المحاور، ثم دوران آخر. A تساوي U سيغما V منقول. التمديدات هي القيم المنفردة، والإبقاء على أكبرها يعطي أفضل نسخة صغيرة من المصفوفة.',
      'Jede Matrix jeder Form ist eine Drehung, dann eine Streckung entlang der Achsen, dann wieder eine Drehung. A gleich U Sigma V transponiert. Die Streckungen sind die Singulärwerte. Behält man nur die größten, erhält man die beste kleine Kopie der Matrix.')
K.say('pca', 'Principal component analysis',
      'Centre the data, build the covariance matrix, and find its eigenvectors. The eigenvector with the biggest eigenvalue is the direction of most spread. Keep the top few directions to describe the data with fewer numbers. Scale the features first.',
      'Data को centre करें, covariance matrix बनाएँ, और उसके eigenvectors निकालें। सबसे बड़े eigenvalue वाला eigenvector सबसे ज़्यादा फैलाव की दिशा है। ऊपर की कुछ दिशाएँ रखकर data को कम संख्याओं में लिखें। पहले features को scale करें।',
      'Data centre ಮಾಡಿ, covariance matrix ಮಾಡಿ, ಅದರ eigenvectors ಕಂಡುಹಿಡಿಯಿರಿ. ದೊಡ್ಡ eigenvalue ನ ದಿಕ್ಕು ಹೆಚ್ಚು ಹರಡಿದ ದಿಕ್ಕು. ಮೊದಲು features scale ಮಾಡಿ.',
      'Data centre କରନ୍ତୁ, covariance matrix ତିଆରି କରନ୍ତୁ, eigenvectors ବାହାର କରନ୍ତୁ। ବଡ଼ eigenvalue ର ଦିଗ ସବୁଠୁ ଅଧିକ ବିସ୍ତାରର ଦିଗ। ପ୍ରଥମେ features scale କରନ୍ତୁ।',
      'ضع البيانات حول المركز، وابن مصفوفة التغاير، وجد متجهاتها الذاتية. المتجه صاحب أكبر قيمة ذاتية هو اتجاه أكبر انتشار. احتفظ بأهم الاتجاهات لتصف البيانات بأعداد أقل، وقم بتوحيد مقاييس الخصائص أولًا.',
      'Zentriere die Daten, bilde die Kovarianzmatrix und finde ihre Eigenvektoren. Der Eigenvektor mit dem größten Eigenwert zeigt in die Richtung der größten Streuung. Behalte die wichtigsten Richtungen, um die Daten mit weniger Zahlen zu beschreiben. Skaliere die Merkmale vorher.')
K.say('ml', 'Uses in machine learning',
      'Eigenvalues show up in PCA, in the shape of the loss surface, in spectral clustering, in recommenders and in fine tuning large language models. A big eigenvalue marks an important direction, and a tiny one marks a direction you can often drop.',
      'Eigenvalues PCA, loss surface के आकार, spectral clustering, recommenders और बड़े language models की fine tuning में आते हैं। बड़ा eigenvalue ज़रूरी दिशा है, छोटा वह दिशा जिसे अक्सर छोड़ सकते हैं।',
      'Eigenvalues PCA, loss surface, spectral clustering, recommenders ಮತ್ತು fine tuning ನಲ್ಲಿ ಬರುತ್ತವೆ. ದೊಡ್ಡ eigenvalue ಮುಖ್ಯ ದಿಕ್ಕು.',
      'Eigenvalues PCA, loss surface, spectral clustering, recommenders ଓ fine tuning ରେ ଆସେ। ବଡ଼ eigenvalue ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ ଦିଗ।',
      'تظهر القيم الذاتية في تحليل المكونات الرئيسية، وفي شكل سطح الخسارة، والتجميع الطيفي، وأنظمة التوصية، وضبط النماذج اللغوية الكبيرة. القيمة الكبيرة تدل على اتجاه مهم والصغيرة على اتجاه يمكن تركه غالبًا.',
      'Eigenwerte tauchen in der PCA auf, in der Form der Verlustfläche, beim spektralen Clustering, in Empfehlungssystemen und beim Feinabstimmen großer Sprachmodelle. Ein großer Eigenwert markiert eine wichtige Richtung, ein winziger eine, die man oft weglassen kann.')
K.say('practice', 'Practice',
      'Practice time. Check eigenvectors, find the long run of a Markov chain, run power iteration on a three by three matrix, and compress a tiny picture with one singular value.',
      'अभ्यास का समय। Eigenvectors जाँचें, Markov chain का लंबा परिणाम निकालें, तीन गुणा तीन matrix पर power iteration चलाएँ, और एक singular value से छोटी तस्वीर compress करें।',
      'ಅಭ್ಯಾಸದ ಸಮಯ. Eigenvectors ಪರಿಶೀಲಿಸಿ, Markov chain steady state, power iteration, ಮತ್ತು ಒಂದು singular value ನಿಂದ ಚಿತ್ರ compress ಮಾಡಿ.',
      'ଅଭ୍ୟାସ ସମୟ। Eigenvectors ଯାଞ୍ଚ, Markov chain steady state, power iteration, ଓ ଗୋଟିଏ singular value ରେ ଛବି compress କରନ୍ତୁ।',
      'وقت التدريب. تحقق من المتجهات الذاتية، وجد الحالة المستقرة لسلسلة ماركوف، وطبق طريقة القوة على مصفوفة ثلاثة في ثلاثة، واضغط صورة صغيرة بقيمة منفردة واحدة.',
      'Zeit zum Üben. Prüfe Eigenvektoren, finde den Langzeitzustand einer Markow Kette, wende die Potenzmethode auf eine drei mal drei Matrix an und komprimiere ein winziges Bild mit einem Singulärwert.')

# ---------------------------------------------------------------- practice
K.practice('check', 'e', 'Is it an eigenvector?', 'p_check',
           '<p>For A = [[4, 1], [2, 3]], test the vectors [1, 1], [1, −2] and [1, 0]. For each eigenvector found, give its eigenvalue, then confirm the trace and determinant rules.</p>',
           'v = [1, 1]: Av = [5, 5] = 5 times v, an eigenvector\nv = [1, -2]: Av = [2, -4] = 2 times v, an eigenvector\nv = [1, 0]: Av = [4, 2], not a multiple of v\ntrace = 7 = 5 + 2\ndet = 10 = 5 times 2',
           'Av is a multiple of v exactly when the "cross" Av₁v₂ − Av₂v₁ is zero.',
           '<p>Multiply and compare. A[1, 1] = [4 + 1, 2 + 3] = [5, 5], which is 5 × [1, 1]. A[1, −2] = [4 − 2, 2 − 6] = [2, −4], which is 2 × [1, −2]. A[1, 0] = [4, 2] points in a new direction. The two eigenvalues 5 and 2 add to the trace 4 + 3 = 7 and multiply to the determinant 12 − 2 = 10, as the rules promise.</p>',
           'O(1) per vector', 'O(1)')
K.practice('steady', 'm', 'The long run of a Markov chain', 'p_steady',
           '<p>Use the city and village matrix from Chapter 4. Find its eigenvalues, use the eigenvector for eigenvalue 1 to predict the long run split of 1000 thousand people, and confirm it by running 100 years.</p>',
           'eigenvalues: 1.00 and 0.85\nsteady state: city 333.3, village 666.7\nafter 100 years: city 333.3, village 666.7',
           'Solve (T − I)v = 0. The first row says −0.1x + 0.05y = 0.',
           '<p>The trace is 1.85 and the determinant is 0.855 − 0.005 = 0.85, so λ² − 1.85λ + 0.85 = 0 gives λ = 1 and λ = 0.85. For λ = 1, −0.1x + 0.05y = 0 means y = 2x, so the eigenvector is [1, 2]. Scaling it to a total of 1000 gives 333.3 and 666.7. Any start drifts there, because the other part of the state is multiplied by 0.85 each year and 0.85¹⁰⁰ is tiny.</p>',
           'O(1) for the eigenvector', 'O(1)')
K.practice('power3', 'h', 'The top principal direction by power iteration', 'p_power3',
           '<p>C = [[4, 2, 0], [2, 3, 1], [0, 1, 2]] is a covariance matrix of three features. Use power iteration from [1, 1, 1] to find its top eigenvector and eigenvalue, and say what share of the total spread it explains.</p>',
           'step 1: v = [0.6667, 0.6667, 0.3333], lambda = 5.5556\nstep 2: v = [0.7159, 0.6562, 0.2386], lambda = 5.6477\nstep 4: v = [0.7486, 0.6369, 0.1844], lambda = 5.6683\nstep 8: v = [0.7560, 0.6314, 0.1725], lambda = 5.6691\nshare of the total spread: 63.0%',
           'The total spread is the trace 4 + 3 + 2 = 9.',
           '<p>Step 1: C[1, 1, 1] = [6, 6, 3], length 9, so v = [0.667, 0.667, 0.333]. Each round repeats this. The estimate settles at λ₁ ≈ 5.669 within a few rounds, because the next eigenvalue (about 2.476) is well below it. The trace is the sum of all eigenvalues, so this first principal component explains 5.669 ÷ 9 ≈ 63% of the spread. The direction [0.756, 0.631, 0.173] says the first two features carry most of it.</p>',
           'O(steps · n²)', 'O(n)')
K.practice('lowrank', 'x', 'Compress a picture with one singular value', 'p_lowrank',
           '<p>A 4 × 4 grey picture has a bright top left block and a dark border. Find its top singular value with power iteration on AᵀA, rebuild the picture from σ₁u₁v₁ᵀ alone, and report how much of the "energy" (sum of squares) is kept.</p>',
           ' 9.01  9.01  7.98  1.07\n 9.01  9.01  7.98  1.07\n 7.98  7.98  7.06  0.95\n 1.07  1.07  0.95  0.13\nsigma1 = 25.203, numbers stored: 9 instead of 16\nenergy kept: 99.88%',
           'Energy kept = σ₁² ÷ (sum of all squared entries).',
           '<p>Six rounds of power iteration on AᵀA are plenty here, because σ₁ is far bigger than σ₂. They give v₁, then u₁ = Av₁ ÷ σ₁. The rank 1 picture needs only u₁ (4 numbers), v₁ (4 numbers) and σ₁, so 9 numbers instead of 16. For a real 1000 × 1000 photo, keeping 50 singular values stores 50 × 2001 = 100050 numbers instead of a million. The bottom right corner is the weak spot, since one pattern cannot copy both the bright block and the dim border exactly.</p>',
           'O(iterations · n²)', 'O(n²)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Av = λv. What is v called?', ['an eigenvalue', 'an eigenvector', 'a singular value', 'the trace'], 1, 'The vector whose direction survives.', 'v is the eigenvector and the number λ is its eigenvalue.')
K.quiz('e', 'An eigenvector has eigenvalue 2. What does the matrix do to it?', ['turns it by 90°', 'doubles its length and keeps its line', 'halves it', 'makes it zero'], 1, 'Av = 2v.', 'It stays on the same line and becomes twice as long.')
K.quiz('e', 'What are the eigenvalues of the diagonal matrix [[7, 0], [0, 3]]?', ['7 and 3', '10 and 21', '0 and 0', '1 and 1'], 0, 'Diagonal matrices are the easy case.', 'For a diagonal (or triangular) matrix the eigenvalues are the diagonal entries.')
K.quiz('e', 'What does PCA mainly do?', ['adds more features', 'finds the directions of most spread to reduce dimensions', 'sorts the data', 'labels the data'], 1, 'Principal components.', 'PCA keeps the few directions that carry most of the variance.')
K.quiz('m', 'The eigenvalues of a 2 × 2 matrix are 4 and 3. What is its determinant?', ['7', '12', '1', '4'], 1, 'Product of the eigenvalues.', 'det = 4 × 3 = 12. Their sum 7 is the trace.')
K.quiz('m', 'Which equation gives the eigenvalues?', ['A − λ = 0', 'det(A − λI) = 0', 'Av = 0', 'AᵀA = I'], 1, 'A − λI must squash space flat.', 'A non zero v can solve (A − λI)v = 0 only when det(A − λI) = 0.')
K.quiz('m', 'Why must features be standardised before PCA?', ['PCA needs positive numbers', 'a column with big units would dominate the variance', 'to make the data smaller', 'it is not needed'], 1, 'Think millimetres versus kilometres.', 'Variance depends on units, so unscaled columns with big numbers look falsely important.')
K.quiz('m', 'Which matrix has no real eigenvectors?', ['[[2, 0], [0, 5]]', '[[0, −1], [1, 0]]', '[[1, 1], [0, 1]]', '[[2, 1], [1, 2]]'], 1, 'Which one turns every arrow?', 'The 90° rotation moves every direction, so its eigenvalues are complex (±i).')
K.quiz('m', 'A = UΣVᵀ. What are the numbers on the diagonal of Σ?', ['eigenvectors', 'singular values', 'the trace', 'probabilities'], 1, 'Σ is the stretch.', 'Σ holds the singular values σ₁ ≥ σ₂ ≥ … ≥ 0.')
K.quiz('h', 'A symmetric matrix always has…', ['complex eigenvalues', 'real eigenvalues and perpendicular eigenvectors', 'a zero determinant', 'only one eigenvector'], 1, 'Think of covariance matrices.', 'This is the spectral theorem. It is why PCA directions are perpendicular.')
K.quiz('h', 'If A has eigenvalue 3 for v, what does A⁵ do to v?', ['multiplies it by 15', 'multiplies it by 243', 'multiplies it by 3', 'leaves it alone'], 1, 'Aⁿv = λⁿv.', '3⁵ = 243.')
K.quiz('h', 'PCA eigenvalues are 5, 3, 1.5 and 0.5. What share does PC1 explain?', ['50%', '5%', '33%', '62.5%'], 0, 'λ₁ ÷ total.', '5 ÷ (5 + 3 + 1.5 + 0.5) = 5 ÷ 10 = 50%.')
K.quiz('h', 'Power iteration converges slowly when…', ['λ₁ is much bigger than λ₂', 'λ₂ is almost as big as λ₁', 'the matrix is diagonal', 'the start vector is long'], 1, 'Each round shrinks the error by λ₂/λ₁.', 'A ratio close to 1 means each round removes very little of the unwanted direction.')
K.quiz('x', 'How are the singular values of A related to AᵀA?', ['they are its eigenvalues', 'they are the square roots of its eigenvalues', 'they are its diagonal', 'they are unrelated'], 1, 'AᵀA = VΣ²Vᵀ.', 'Since AᵀA = VΣᵀUᵀUΣVᵀ = VΣ²Vᵀ, the eigenvalues of AᵀA are σᵢ².')
K.quiz('x', 'A Hessian at a minimum has eigenvalues 100 and 0.01. What does that tell you about gradient descent?', ['it will be very fast', 'the condition number is 10000, so progress will be slow and zig zag', 'the point is a maximum', 'nothing'], 1, 'Condition number = λmax / λmin.', 'A long narrow valley: the step size must suit the steep direction, so the flat direction crawls. Chapter 8 shows this.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A = [[4, −2], [1, 1]] and v = [2, 1]. Is v an eigenvector? Give its eigenvalue.', '3', 'Compute Av and compare it with v.', [
    'First entry: <span class="eq">4 × 2 + (−2) × 1 = 8 − 2 = 6</span>',
    'Second entry: <span class="eq">1 × 2 + 1 × 1 = 3</span>',
    'So <span class="eq">Av = [6, 3]</span>',
    'Compare: <span class="eq">[6, 3] = 3 × [2, 1]</span>. Yes, v is an eigenvector with eigenvalue 3.',
], check=3)
K.calc('e', 'What is the larger eigenvalue of [[5, 0], [0, −2]]?', '5', 'The matrix is diagonal.', [
    'For a diagonal matrix the eigenvalues are the diagonal entries.',
    'They are <span class="eq">5</span> and <span class="eq">−2</span>.',
    'The eigenvectors are the axes: [1, 0] is stretched by 5 and [0, 1] is flipped and doubled.',
    'The larger one is 5.',
], check=5)
K.calc('e', 'What do the eigenvalues of [[4, 1], [2, 3]] add up to?', '7', 'Sum of eigenvalues = trace.', [
    'The trace is the sum of the diagonal entries.',
    'Diagonal entries: <span class="eq">4</span> and <span class="eq">3</span>',
    'Trace: <span class="eq">4 + 3 = 7</span>',
    'So the eigenvalues add to 7 (they are 5 and 2).',
], check=4 + 3)
K.calc('m', 'Find the larger eigenvalue of [[4, 1], [2, 3]] with the characteristic equation.', '5', 'λ² − (trace)λ + det = 0.', [
    'Trace <span class="eq">= 4 + 3 = 7</span>, determinant <span class="eq">= 4 × 3 − 1 × 2 = 12 − 2 = 10</span>',
    'Equation: <span class="eq">λ² − 7λ + 10 = 0</span>',
    'Find two numbers that multiply to 10 and add to 7: 5 and 2. So <span class="eq">(λ − 5)(λ − 2) = 0</span>',
    'The eigenvalues are 5 and 2. The larger is 5.',
], check=5)
K.calc('m', 'Find the smaller eigenvalue of the symmetric matrix [[6, −2], [−2, 9]].', '5', 'Use the formula λ = (trace ± √(trace² − 4 det)) ÷ 2.', [
    'Trace <span class="eq">= 6 + 9 = 15</span>, determinant <span class="eq">= 6 × 9 − (−2)(−2) = 54 − 4 = 50</span>',
    'Inside the square root: <span class="eq">15² − 4 × 50 = 225 − 200 = 25</span>, and <span class="eq">√25 = 5</span>',
    'So <span class="eq">λ = (15 ± 5) ÷ 2</span>, giving 10 and 5.',
    'The smaller eigenvalue is 5. Check: 10 + 5 = 15 = trace and 10 × 5 = 50 = det ✔',
], check=5)
K.calc('m', 'What is the product of the eigenvalues of [[3, 1], [0, 2]]?', '6', 'Product of eigenvalues = determinant. The matrix is triangular too.', [
    'The matrix is upper triangular, so its eigenvalues are the diagonal entries <span class="eq">3</span> and <span class="eq">2</span>.',
    'Product: <span class="eq">3 × 2 = 6</span>',
    'Check with the determinant: <span class="eq">3 × 2 − 1 × 0 = 6</span> ✔',
], check=6)
K.calc('m', 'A has eigenvalues 2 and 0.5. What is the larger eigenvalue of A³?', '8', 'Aⁿv = λⁿv.', [
    'Each eigenvalue is raised to the same power.',
    '<span class="eq">2³ = 2 × 2 × 2 = 8</span>',
    '<span class="eq">0.5³ = 0.125</span>',
    'The larger is 8. The 0.5 direction keeps shrinking, which is why power iteration ends up on the 2 direction.',
], check=8)
K.calc('m', 'A PCA gives eigenvalues 6, 3 and 1. What percentage of the variance does PC1 explain?', '60', 'Share = λ₁ ÷ sum of all λ.', [
    'Total variance: <span class="eq">6 + 3 + 1 = 10</span>',
    'PC1 share: <span class="eq">6 ÷ 10 = 0.6</span>',
    'As a percentage: <span class="eq">0.6 × 100 = 60%</span>',
], check=60, unit='%')
K.calc('h', 'One step of power iteration on [[2, 1], [1, 2]] from v = [1, 0] gives [2, 1]. What is the Rayleigh quotient vᵀAv ÷ vᵀv for v = [2, 1]?', '2.8', 'Work out Av first, then two dot products.', [
    'Av for v = [2, 1]: <span class="eq">[2 × 2 + 1 × 1, 1 × 2 + 2 × 1] = [5, 4]</span>',
    'Top: <span class="eq">vᵀAv = 2 × 5 + 1 × 4 = 14</span>',
    'Bottom: <span class="eq">vᵀv = 2 × 2 + 1 × 1 = 5</span>',
    'Quotient: <span class="eq">14 ÷ 5 = 2.8</span>. It is already close to the true top eigenvalue 3.',
], check=14 / 5)
K.calc('h', 'What is the largest singular value of A = [[3, 0], [4, 5]]? Give 3 decimal places.', '6.708', 'σ = √(eigenvalue of AᵀA).', [
    'AᵀA: <span class="eq">[[3·3 + 4·4, 3·0 + 4·5], [0·3 + 5·4, 0·0 + 5·5]] = [[25, 20], [20, 25]]</span>',
    'Trace 50, determinant <span class="eq">625 − 400 = 225</span>, so <span class="eq">λ² − 50λ + 225 = 0</span>',
    '<span class="eq">λ = (50 ± √(2500 − 900)) ÷ 2 = (50 ± 40) ÷ 2</span>, giving 45 and 5',
    'Largest singular value: <span class="eq">σ₁ = √45 ≈ 6.708</span>',
], check=45 ** 0.5, tol=0.001)
K.calc('h', 'PCA eigenvalues are 50, 30, 12, 5 and 3. How many components are needed to keep at least 90% of the variance?', '3', 'Add the eigenvalues from the biggest until you pass 90% of the total.', [
    'Total: <span class="eq">50 + 30 + 12 + 5 + 3 = 100</span>',
    'One component: <span class="eq">50 ÷ 100 = 50%</span>. Not enough.',
    'Two components: <span class="eq">(50 + 30) ÷ 100 = 80%</span>. Not enough.',
    'Three components: <span class="eq">(50 + 30 + 12) ÷ 100 = 92%</span>. That passes 90%, so keep 3.',
], check=3)
K.calc('x', 'A 1000 × 800 picture is stored as a rank 50 SVD (50 columns of U, 50 of V and 50 singular values). How many numbers is that?', '90050', 'Each kept component needs one u, one v and one σ.', [
    'Each u has 1000 numbers and each v has 800 numbers.',
    'One component: <span class="eq">1000 + 800 + 1 = 1801</span> numbers',
    'Fifty components: <span class="eq">50 × 1801 = 90050</span>',
    'The full picture has <span class="eq">1000 × 800 = 800000</span> numbers, so this is about 11% of the size.',
], check=50 * (1000 + 800 + 1))
K.calc('x', 'Three points (1, 2), (3, 4), (5, 6). What is the largest eigenvalue of their covariance matrix (divide by n − 1)?', '8', 'Centre, find the variances and covariance, then the eigenvalues.', [
    'Means: <span class="eq">x̄ = 3, ȳ = 4</span>. Centred points: (−2, −2), (0, 0), (2, 2)',
    'var(x) <span class="eq">= (4 + 0 + 4) ÷ 2 = 4</span>, var(y) = 4, cov(x, y) <span class="eq">= (4 + 0 + 4) ÷ 2 = 4</span>',
    'Covariance matrix <span class="eq">C = [[4, 4], [4, 4]]</span>, trace 8, determinant <span class="eq">16 − 16 = 0</span>',
    'Eigenvalues solve <span class="eq">λ² − 8λ = 0</span>, so 8 and 0. All points lie on one line, so PC1 explains 100% of the spread.',
], check=8)
K.calc('x', 'A Markov chain has matrix [[0.8, 0.3], [0.2, 0.7]] (columns add to 1). In the long run, what percentage of time is spent in state 1?', '60', 'Find the eigenvector for eigenvalue 1, then scale it to add to 100%.', [
    'Solve <span class="eq">(T − I)v = 0</span>: the first row is <span class="eq">−0.2x + 0.3y = 0</span>',
    'So <span class="eq">0.2x = 0.3y</span>, which means <span class="eq">x = 1.5y</span>. Take v = [1.5, 1] or [3, 2].',
    'Scale to a total of 1: <span class="eq">3 ÷ (3 + 2) = 0.6</span>',
    'State 1 gets 60% of the time. Check: T[0.6, 0.4] = [0.48 + 0.12, 0.12 + 0.28] = [0.6, 0.4] ✔',
], check=60, unit='%')

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;
  const eig2 = M => {
    const [a, b, c, d] = M, tr = a + d, det = a * d - b * c, disc = tr * tr - 4 * det;
    if (disc < -1e-9) return null;
    const r = Math.sqrt(Math.max(0, disc));
    return [(tr + r) / 2, (tr - r) / 2].map(l => {
      let v = Math.abs(b) > 1e-9 ? [b, l - a] : Math.abs(c) > 1e-9 ? [l - d, c] : (Math.abs(l - a) < 1e-9 ? [1, 0] : [0, 1]);
      const n = Math.hypot(v[0], v[1]) || 1;
      return { l, v: [v[0] / n, v[1] / n] };
    });
  };

  /* ----- drag v, watch Av, find the directions that do not turn ----- */
  W.eigen = el => {
    const b = shell(el, 'Hunt for eigenvectors', 'Drag the purple arrow v, or press Play to sweep it all the way round. The orange arrow is Av. When the two lie on one line, v is an eigenvector.');
    const PR = { sym: [2, 1, 1, 2], diag: [3, 0, 0, 1], shear: [1, 1, 0, 1], rot: [0, -1, 1, 0], neg: [1, 2, 2, 1] };
    b.innerHTML = `<div class="vz-row">${seg('pr', [['sym', '[[2, 1], [1, 2]]'], ['diag', 'Stretch x'], ['shear', 'Shear'], ['rot', 'Rotate 90°'], ['neg', '[[1, 2], [2, 1]]']], 'sym')}</div>
      <div class="mv-wrap"><div class="eg-plot"></div><div class="mv-side"><div class="mv-inp">a <input type="number" data-e="0" step="0.5"> b <input type="number" data-e="1" step="0.5"></div><div class="mv-inp">c <input type="number" data-e="2" step="0.5"> d <input type="number" data-e="3" step="0.5"></div><label class="eg-tg"><input type="checkbox" class="eg-show"> Show the eigen lines</label><div class="mv-read eg-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let M = PR.sym.slice(), v = [1.5, 0.4];
    const G = MV.frame(440, 440, [-5, 5], [-5, 5]);
    const P = Player($('.vz-p', b), t => { const th = t * Math.PI / 36; v = [1.6 * Math.cos(th), 1.6 * Math.sin(th)]; draw(); }, 140);
    $('.eg-plot', b).innerHTML = MV.svg(G, '<g class="eg-g"></g>', 'The arrow v and the arrow Av');
    const svgEl = $('.eg-plot svg', b);
    MV.drag(svgEl, G, [{ set: (x, y) => { v = [Math.round(x * 10) / 10, Math.round(y * 10) / 10]; if (!v[0] && !v[1]) v = [0.1, 0]; } }], () => { P.pause(); draw(); });
    function setInputs() { b.querySelectorAll('[data-e]').forEach(i => { i.value = M[+i.dataset.e]; }); }
    function draw() {
      const Av = [M[0] * v[0] + M[1] * v[1], M[2] * v[0] + M[3] * v[1]];
      const E = eig2(M);
      let s = MV.axes(G, { labels: false });
      if ($('.eg-show', b).checked && E) E.forEach((e, k) => { s += MV.line(G, -6 * e.v[0], -6 * e.v[1], 6 * e.v[0], 6 * e.v[1], 'mv-v ' + (k ? 'g' : 'p') + ' dash'); });
      const cl = (x, y) => { const m = Math.max(Math.abs(x), Math.abs(y)) / 4.8; return m > 1 ? [x / m, y / m] : [x, y]; };
      const A2 = cl(Av[0], Av[1]);
      s += MV.arrow(G, 0, 0, A2[0], A2[1], 'o') + MV.arrow(G, 0, 0, v[0], v[1], 'p');
      s += MV.text(G, A2[0], A2[1], 'Av', { dx: 8, dy: -6 }) + MV.text(G, v[0], v[1], 'v', { dx: 8, dy: 14 });
      s += `<circle class="mv-pt p big mv-drag" data-h="0" cx="${G.sx(v[0])}" cy="${G.sy(v[1])}" r="11"/>`;
      $('.eg-g', svgEl).innerHTML = s;
      const cross = Av[0] * v[1] - Av[1] * v[0], len = Math.hypot(...v) * Math.hypot(...Av);
      const ang = len < 1e-9 ? 0 : Math.asin(Math.max(-1, Math.min(1, cross / len))) * 180 / Math.PI;
      const lam = (Av[0] * v[0] + Av[1] * v[1]) / (v[0] * v[0] + v[1] * v[1]);
      const hit = len < 1e-9 || Math.abs(cross) / len < 0.02;
      $('.eg-out', b).innerHTML = `v = [${MV.num(v[0])}, ${MV.num(v[1])}]<br>Av = [${MV.num(Av[0])}, ${MV.num(Av[1])}]<br>` +
        (hit ? `✅ <b>Same line!</b> Av = ${MV.num(lam)} × v, so v is an eigenvector with λ = ${MV.num(lam)}.` : `Av is turned by ${MV.num(Math.abs(ang), 0)}° away from v's line. Keep looking.`) +
        `<br><br>${E ? 'Eigenvalues: λ₁ = ' + MV.num(E[0].l) + ', λ₂ = ' + MV.num(E[1].l) : '⚠️ No real eigenvectors: this matrix turns every arrow.'}`;
    }
    b.querySelectorAll('[data-e]').forEach(i => i.addEventListener('input', () => { const val = parseFloat(i.value); M[+i.dataset.e] = isFinite(val) ? val : 0; draw(); }));
    $('.eg-show', b).addEventListener('change', draw);
    wireSeg(b, 'pr', k => { M = PR[k].slice(); setInputs(); draw(); });
    setInputs();
    P.load(73, 0);
    v = [1.5, 0.4]; draw();
  };

  /* ----- SVD as rotate, stretch, rotate ----- */
  W.svdviz = el => {
    const b = shell(el, 'SVD: rotate, stretch, rotate', 'Pick a matrix or type one. Press Play to watch the unit circle go through Vᵀ, then Σ, then U, and end up as the ellipse made by A.');
    const PR = { a: [3, 0, 4, 5], b: [2, 1, 1, 2], c: [1, 2, 0, 1], d: [1, -1, 2, 0.5] };
    b.innerHTML = `<div class="vz-row">${seg('pr', [['a', '[[3, 0], [4, 5]]'], ['b', '[[2, 1], [1, 2]]'], ['c', 'Shear'], ['d', 'Mixed']], 'a')}</div>
      <div class="mv-wrap"><div class="sv-plot"></div><div class="mv-side"><div class="mv-inp">a <input type="number" data-e="0" step="0.5"> b <input type="number" data-e="1" step="0.5"></div><div class="mv-inp">c <input type="number" data-e="2" step="0.5"> d <input type="number" data-e="3" step="0.5"></div><div class="mv-read sv-out" aria-live="polite"></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let M = PR.a.slice(), S;
    const N = 12, G = MV.frame(440, 440, [-8, 8], [-8, 8]);
    const rot = t => [Math.cos(t), -Math.sin(t), Math.sin(t), Math.cos(t)];
    const mm = (X, Y) => [X[0] * Y[0] + X[1] * Y[2], X[0] * Y[1] + X[1] * Y[3], X[2] * Y[0] + X[3] * Y[2], X[2] * Y[1] + X[3] * Y[3]];
    function svd() {
      const [a, bb, c, d] = M;
      const AtA = [a * a + c * c, a * bb + c * d, a * bb + c * d, bb * bb + d * d];
      const E = eig2(AtA);
      const s1 = Math.sqrt(Math.max(0, E[0].l)), s2 = Math.sqrt(Math.max(0, E[1].l));
      let v1 = E[0].v, v2 = [-v1[1], v1[0]];
      const th = Math.atan2(v1[1], v1[0]);                 // V is the rotation by th
      const Av1 = [a * v1[0] + bb * v1[1], c * v1[0] + d * v1[1]];
      const u1 = s1 > 1e-9 ? [Av1[0] / s1, Av1[1] / s1] : [1, 0];
      const Av2 = [a * v2[0] + bb * v2[1], c * v2[0] + d * v2[1]];
      const flip = (a * d - bb * c) < 0 ? -1 : 1;         // U may need a mirror
      const ph = Math.atan2(u1[1], u1[0]);
      S = { s1, s2, th, ph, flip, v1, v2, u1, Av2 };
    }
    function mat(t) {
      const q = t / N;
      if (q <= 1) return rot(-S.th * q);
      if (q <= 2) { const r = q - 1; return mm([1 + (S.s1 - 1) * r, 0, 0, 1 + (S.s2 * S.flip - 1) * r], rot(-S.th)); }
      return mm(rot(S.ph * (q - 2)), mm([S.s1, 0, 0, S.s2 * S.flip], rot(-S.th)));
    }
    function show(t) {
      const T = mat(t), ap = (x, y) => [T[0] * x + T[1] * y, T[2] * x + T[3] * y];
      let s = MV.axes(G, { xstep: 2, ystep: 2 });
      const pts = [];
      for (let k = 0; k <= 96; k++) { const g = k / 96 * 2 * Math.PI, p = ap(Math.cos(g), Math.sin(g)); pts.push(G.sx(p[0]).toFixed(1) + ',' + G.sy(p[1]).toFixed(1)); }
      if (t) s += `<polyline class="mv-curve thin dash" points="${(() => { const q = []; for (let k = 0; k <= 96; k++) { const g = k / 96 * 2 * Math.PI; q.push(G.sx(Math.cos(g)).toFixed(1) + ',' + G.sy(Math.sin(g)).toFixed(1)); } return q.join(' '); })()}"/>`;
      s += `<polygon class="mv-poly o" points="${pts.join(' ')}"/>`;
      const e1 = ap(S.v1[0], S.v1[1]), e2 = ap(S.v2[0], S.v2[1]);
      s += MV.arrow(G, 0, 0, e1[0], e1[1], 'p') + MV.arrow(G, 0, 0, e2[0], e2[1], 'g');
      $('.sv-plot', b).innerHTML = MV.svg(G, s, 'The unit circle transformed step by step');
      const st = t === 0 ? 0 : t <= N ? 1 : t <= 2 * N ? 2 : 3;
      $('.vz-msg', b).innerHTML = ['Start: the unit circle. Purple is v₁ and green is v₂, the input directions the SVD picks.',
        'Step 1, Vᵀ: rotate so that v₁ and v₂ lie on the axes. A circle stays a circle.',
        `Step 2, Σ: stretch the x axis by σ₁ = ${MV.num(S.s1)} and the y axis by σ₂ = ${MV.num(S.s2)}${S.flip < 0 ? ' (and flip it, because det A is negative)' : ''}. The circle becomes an ellipse.`,
        'Step 3, U: rotate the ellipse into place. Now purple is A v₁ = σ₁u₁ and green is A v₂ = σ₂u₂, the two half axes.'][st];
    }
    function setup() {
      svd();
      const det = M[0] * M[3] - M[1] * M[2];
      $('.sv-out', b).innerHTML = `σ₁ = <b>${MV.num(S.s1, 3)}</b><br>σ₂ = <b>${MV.num(S.s2, 3)}</b><br>σ₁ × σ₂ = ${MV.num(S.s1 * S.s2, 3)}<br>|det A| = ${MV.num(Math.abs(det), 3)}<br>v₁ = [${MV.num(S.v1[0], 3)}, ${MV.num(S.v1[1], 3)}]<br>u₁ = [${MV.num(S.u1[0], 3)}, ${MV.num(S.u1[1], 3)}]`;
      P.load(3 * N + 1, 0);
    }
    const P = Player($('.vz-p', b), show, 110);
    b.querySelectorAll('[data-e]').forEach(i => i.addEventListener('input', () => { const val = parseFloat(i.value); M[+i.dataset.e] = isFinite(val) ? val : 0; setup(); }));
    wireSeg(b, 'pr', k => { M = PR[k].slice(); b.querySelectorAll('[data-e]').forEach(i => { i.value = M[+i.dataset.e]; }); setup(); });
    b.querySelectorAll('[data-e]').forEach(i => { i.value = M[+i.dataset.e]; });
    setup();
  };

  /* ----- PCA step by step on a cloud you can shape ----- */
  W.pca = el => {
    const b = shell(el, 'PCA step by step', 'Shape the cloud with the sliders, then press Play: centre the data, find the covariance, draw the principal components and squash every point onto PC1. Turn "your line" to see that no other direction keeps more spread.');
    b.innerHTML = `<div class="mv-wrap"><div class="pc-plot"></div><div class="mv-side">${slider('tilt', 'tilt °', 0, 180, 35, 5)}${slider('ratio', 'thinness', 1, 6, 3, 0.5)}${slider('mine', 'your line °', 0, 180, 100, 5)}<div class="mv-read pc-out" aria-live="polite"></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let tilt = 35, ratio = 3, mine = 100, raw = [], t = 0;
    const G = MV.frame(440, 400, [-1, 9], [-1, 8]);
    let seed = 7;
    const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
    const gauss = () => { const u = Math.max(1e-9, rnd()), w = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * w); };
    const base = Array.from({ length: 40 }, () => [gauss(), gauss()]);
    function make() {
      const th = tilt * Math.PI / 180, big = 1.4, small = big / ratio;
      raw = base.map(([p, q]) => [4 + Math.cos(th) * p * big - Math.sin(th) * q * small, 3.5 + Math.sin(th) * p * big + Math.cos(th) * q * small]);
    }
    function stats() {
      const n = raw.length, mx = raw.reduce((s, p) => s + p[0], 0) / n, my = raw.reduce((s, p) => s + p[1], 0) / n;
      let sxx = 0, syy = 0, sxy = 0;
      raw.forEach(([x, y]) => { sxx += (x - mx) ** 2; syy += (y - my) ** 2; sxy += (x - mx) * (y - my); });
      [sxx, syy, sxy] = [sxx / (n - 1), syy / (n - 1), sxy / (n - 1)];
      const E = eig2([sxx, sxy, sxy, syy]);
      return { mx, my, sxx, syy, sxy, E };
    }
    function show(step) {
      t = step;
      const S = stats(), c = [4, 3.5];
      const shift = step >= 1 ? [c[0] - S.mx, c[1] - S.my] : [0, 0];
      const pts = raw.map(([x, y]) => [x + shift[0], y + shift[1]]);
      const pc1 = S.E[0].v, pc2 = S.E[1].v;
      let s = MV.axes(G, { xstep: 1, ystep: 1 });
      if (step >= 1) s += MV.dot(G, c[0], c[1], 'k', 5);
      const mu = mine * Math.PI / 180, md = [Math.cos(mu), Math.sin(mu)];
      const thru = (d, cls) => {          // the part of the line through c that stays inside the frame
        let lo = -1e9, hi = 1e9;
        [[0, G.xr], [1, G.yr]].forEach(([k, r]) => { if (Math.abs(d[k]) > 1e-9) { const t1 = (r[0] - c[k]) / d[k], t2 = (r[1] - c[k]) / d[k]; lo = Math.max(lo, Math.min(t1, t2)); hi = Math.min(hi, Math.max(t1, t2)); } });
        return MV.line(G, c[0] + lo * d[0], c[1] + lo * d[1], c[0] + hi * d[0], c[1] + hi * d[1], cls);
      };
      s += thru(md, 'mv-v r dash');
      if (step >= 3) s += thru(pc1, 'mv-curve thin c2');
      pts.forEach(([x, y]) => {
        if (step >= 4) {
          const d = (x - c[0]) * pc1[0] + (y - c[1]) * pc1[1], px = c[0] + d * pc1[0], py = c[1] + d * pc1[1];
          s += MV.line(G, x, y, px, py, 'mv-res') + MV.dot(G, step >= 5 ? px : x, step >= 5 ? py : y, step >= 5 ? 'o' : '', 4);
          if (step < 5) s += MV.dot(G, px, py, 'o', 3);
        } else s += MV.dot(G, x, y, '', 4);
      });
      if (step >= 3) {
        const a1 = 2 * Math.sqrt(S.E[0].l), a2 = 2 * Math.sqrt(Math.max(0, S.E[1].l));
        s += MV.arrow(G, c[0], c[1], c[0] + a1 * pc1[0], c[1] + a1 * pc1[1], 'p') + MV.arrow(G, c[0], c[1], c[0] + a2 * pc2[0], c[1] + a2 * pc2[1], 'g');
        s += MV.text(G, c[0] + a1 * pc1[0], c[1] + a1 * pc1[1], 'PC1', { dx: 6, dy: -6 }) + MV.text(G, c[0] + a2 * pc2[0], c[1] + a2 * pc2[1], 'PC2', { dx: 6, dy: 14 });
      }
      $('.pc-plot', b).innerHTML = MV.svg(G, s, 'A cloud of points and its principal components');
      const varMine = S.sxx * md[0] ** 2 + 2 * S.sxy * md[0] * md[1] + S.syy * md[1] ** 2, tot = S.sxx + S.syy;
      const pcDeg = ((Math.atan2(pc1[1], pc1[0]) * 180 / Math.PI) + 180) % 180;
      $('.pc-out', b).innerHTML = (step >= 2 ? `C = [[${MV.num(S.sxx)}, ${MV.num(S.sxy)}], [${MV.num(S.sxy)}, ${MV.num(S.syy)}]]<br>` : '') +
        (step >= 3 ? `λ₁ = ${MV.num(S.E[0].l)}, λ₂ = ${MV.num(S.E[1].l)}<br>PC1 explains <b>${MV.num(100 * S.E[0].l / tot, 1)}%</b> (at ${MV.num(pcDeg, 0)}°)<br>` : '') +
        `<span style="color:var(--red)">●</span> your line keeps ${MV.num(100 * varMine / tot, 1)}% of the spread`;
      $('.vz-msg', b).innerHTML = ['The raw data: 40 points. Press Play to run PCA on it.',
        'Step 1: subtract the mean, so the cloud is centred (the black dot).',
        'Step 2: work out the covariance matrix C. Its diagonal is the spread along x and y, the off diagonal is how they move together.',
        'Step 3: the eigenvectors of C are the principal components. Each arrow has length 2√λ, so it shows the spread in that direction.',
        'Step 4: drop every point straight onto the PC1 line. The red dashes are what is thrown away.',
        'Step 5: every point is now one number, its position along PC1. Most of the spread survived.'][step];
    }
    const P = Player($('.vz-p', b), show, 1100);
    wireSlider(b, 'tilt', v => { tilt = v; make(); show(t); });
    wireSlider(b, 'ratio', v => { ratio = v; make(); show(t); });
    wireSlider(b, 'mine', v => { mine = v; show(t); });
    make();
    P.load(6, 0);
  };
})();
'''

CSS = r'''
.eg-tg{display:flex; align-items:center; gap:6px; font-size:14px; font-weight:700; color:var(--ink2); margin:6px 0}
'''

# ---------------------------------------------------------------- deeper explanations and extra animations
# Each lesson above gives the short version. DEEPER adds a slower, fuller explanation (and sometimes an
# animation) to the end of the lesson with the same id.
DEEPER = {
    'find': deep('from eigenvalues to eigenvectors, fully worked', f'''
<p>Finding λ is only half the job. For each λ you then find the direction v by solving (A − λI)v = 0. Here is a full example with no steps skipped.</p>
{worked('Eigenvalues and eigenvectors of A = [[4, 1], [2, 3]]', [
        'trace = <span class="eq">4 + 3 = 7</span>, det = <span class="eq">4 × 3 − 1 × 2 = 10</span>',
        'Characteristic equation: <span class="eq">λ² − 7λ + 10 = 0</span>, which factors as <span class="eq">(λ − 5)(λ − 2) = 0</span>',
        'So <span class="eq">λ₁ = 5</span> and <span class="eq">λ₂ = 2</span>. Check: 5 + 2 = 7 = trace and 5 × 2 = 10 = det ✓',
        'For λ = 5: <span class="eq">A − 5I = [[−1, 1], [2, −2]]</span>. The first row says −v₁ + v₂ = 0, so <span class="eq">v = [1, 1]</span>',
        'For λ = 2: <span class="eq">A − 2I = [[2, 1], [2, 1]]</span>. The row says 2v₁ + v₂ = 0, so <span class="eq">v = [1, −2]</span>',
        'Check: <span class="eq">A[1, −2] = [4 − 2, 2 − 6] = [2, −4] = 2 × [1, −2]</span> ✓'])}
<p>The characteristic equation is a quadratic in λ, so it is a parabola. Its roots, where it crosses zero, are the eigenvalues. Change the matrix below and watch the roots move. When the parabola floats above the axis there are no real roots: the matrix turns every direction, as a rotation does.</p>
{viz('charpoly')}
{trick('The two rows of A − λI are always multiples of each other (that is what det = 0 means). So you only ever need to read one row to find v.')}
'''),
    'power': deep('watch power iteration swing round', f'''
<p>Here is why power iteration works. Write the starting vector as a mix of eigenvectors: x = c₁v₁ + c₂v₂. Multiplying by A k times gives c₁λ₁ᵏv₁ + c₂λ₂ᵏv₂. If |λ₁| is bigger than |λ₂|, the first term grows faster and soon swamps the second. Scaling back to length 1 each time only keeps the numbers from overflowing.</p>
{fx('Speed of power iteration', 'error after k steps ≈ |λ₂ ÷ λ₁|ᵏ', 'With λ₁ = 5 and λ₂ = 2 the error shrinks by 0.4 each step. With λ₁ = 1 and λ₂ = 0.99 it shrinks by only 1% each step, which is very slow.')}
<p>Press Play below. The orange arrow is the current guess. Each step multiplies by A (dashed) and then rescales. The guess swings round onto the blue eigenvector line, and the Rayleigh estimate of λ closes in on the true value.</p>
{viz('poweriter')}
{life('Repeatedly asking "which pages do the important pages link to?" is power iteration. After a few rounds the answer stops changing, and that steady answer is the PageRank score.')}
'''),
    'svd': deep('how much an SVD really saves, and how much it keeps', f'''
<p>Keeping only the top k singular values gives a rank k copy of the matrix. Two simple formulas tell you what that costs and what it keeps.</p>
{fxs(fx('Storage for a rank k copy', 'k × (m + n + 1) numbers', 'k columns of U (m each), k rows of Vᵀ (n each) and k singular values, instead of m × n.'),
         fx('Share of the "energy" kept', f'{frac("σ₁² + … + σₖ²", "σ₁² + … + σᵣ²")}', 'The squared singular values add up to the sum of all squared entries of the matrix. This share says how much of it the copy keeps.'))}
{worked('Compressing an 800 × 600 grey photo', [
        'Full photo: <span class="eq">800 × 600 = 480000</span> numbers',
        'Rank 50 copy: <span class="eq">50 × (800 + 600 + 1) = 70050</span> numbers, about <span class="eq">15%</span> of the original',
        'Suppose the singular values squared add up to 1000 and the top 50 of them add up to 960.',
        'Energy kept: <span class="eq">960 ÷ 1000 = 96%</span>. The picture looks almost the same, and the dropped 4% is mostly fine grain and noise.'])}
<p>Natural data almost always has fast falling singular values. A few directions carry the big structure, and the long tail is noise. That is why "throw away the small singular values" works so well for photos, ratings tables and text.</p>
'''),
    'ml': deep('the condition number in numbers, and how ridge fixes it', f'''
<p>The condition number κ = λmax ÷ λmin of XᵀX says how sensitive regression is to tiny changes in the data. Here is what it looks like when two features are almost copies of each other.</p>
{worked('Two nearly duplicate features', [
        'Suppose XᵀX has eigenvalues <span class="eq">100</span> (the shared direction) and <span class="eq">0.01</span> (the tiny difference between the two features).',
        'Condition number: <span class="eq">κ = 100 ÷ 0.01 = 10000</span>. A 0.01% wobble in the data can move the weights by about 100%.',
        'Ridge regression solves with <span class="eq">XᵀX + λI</span>. Adding λ = 1 adds 1 to every eigenvalue: <span class="eq">101</span> and <span class="eq">1.01</span>',
        'New condition number: <span class="eq">101 ÷ 1.01 = 100</span>, a hundred times better. The weights become stable, at the price of a small bias towards zero.'])}
<p>This is the single most common reason ridge (L2) regularisation is switched on by default in libraries. It is not only about overfitting, it is also about making the maths stable when features overlap.</p>
{table(['Eigenvalue or singular value pattern', 'What it tells you'], [
        ['a few large values, then a sharp drop', 'the data really lives in a low dimensional space, PCA will work well'],
        ['values falling slowly and evenly', 'information is spread out, compression will lose a lot'],
        ['one value close to 0', 'two or more features are nearly dependent, watch out for unstable weights'],
    ])}
'''),
}
for _p in PARTS:
    _p['html'] += DEEPER.get(_p['id'], '')

VIZ_JS += r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;

  /* ----- the characteristic polynomial of a 2 × 2 matrix ----- */
  W.charpoly = el => {
    const b = shell(el, 'Eigenvalues are the roots of a parabola', 'The curve is p(λ) = λ² − (trace)λ + det for the matrix [[a, b], [c, d]]. Green dots are the eigenvalues. Press Play to lower b step by step and watch two real eigenvalues meet and then vanish into complex ones.');
    b.innerHTML = `<div class="mv-wrap"><div class="cpl-plot"></div><div class="mv-side">${slider('a', 'a', -4, 6, 4, 0.5)}${slider('b', 'b', -4, 4, 1, 0.5)}${slider('c', 'c', -4, 4, 2, 0.5)}${slider('d', 'd', -4, 6, 3, 0.5)}<div class="mv-read cpl-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const M = { a: 4, b: 1, c: 2, d: 3 };
    const G = MV.frame(440, 330, [-4, 8], [-8, 12]);
    function draw() {
      const { a, b: bb, c, d } = M, tr = a + d, det = a * d - bb * c, D = tr * tr - 4 * det;
      let s = MV.axes(G, { xstep: 2, ystep: 4, xl: 'λ', yl: 'p(λ)' }) + MV.curve(G, l => l * l - tr * l + det);
      const out = [`trace = ${MV.num(tr)}, det = ${MV.num(det)}`, `p(λ) = λ² − ${MV.num(tr)}λ + ${MV.num(det)}`, `discriminant = trace² − 4 det = <b>${MV.num(D)}</b>`];
      if (D >= -1e-9) {
        const r = Math.sqrt(Math.max(0, D)), l1 = (tr + r) / 2, l2 = (tr - r) / 2;
        s += MV.dot(G, l1, 0, 'g', 7) + MV.dot(G, l2, 0, 'g', 7);
        out.push(`eigenvalues λ = <b>${MV.num(l1)}</b> and <b>${MV.num(l2)}</b>`);
        if (Math.abs(bb) > 1e-9 || Math.abs(a - l1) > 1e-9) { const v = Math.abs(bb) > 1e-9 ? [bb, l1 - a] : [l1 - d, c]; const L = Math.hypot(...v) || 1; out.push(`eigenvector for λ = ${MV.num(l1)}: about [${MV.num(v[0] / L)}, ${MV.num(v[1] / L)}]`); }
      } else out.push('⚠️ No real roots: the eigenvalues are complex. The matrix rotates every direction.', `they are ${MV.num(tr / 2)} ± ${MV.num(Math.sqrt(-D) / 2)}i`);
      $('.cpl-plot', b).innerHTML = MV.svg(G, s, 'Characteristic polynomial');
      $('.cpl-out', b).innerHTML = out.join('<br>');
    }
    const setS = (k, v) => { M[k] = v; $(`[data-sl="${k}"]`, b).value = v; $(`[data-slv="${k}"]`, b).textContent = MV.num(v); };
    const P = Player($('.vz-p', b), t => { setS('a', 4); setS('d', 3); setS('c', 2); setS('b', 1 - t * 0.5); draw(); }, 600);
    ['a', 'b', 'c', 'd'].forEach(k => wireSlider(b, k, v => { P.pause(); M[k] = v; draw(); }));
    P.load(9, 0);
  };

  /* ----- power iteration converging to the top eigenvector ----- */
  W.poweriter = el => {
    const b = shell(el, 'Power iteration, one multiply at a time', 'Pick a matrix and a starting angle. Each step multiplies the orange guess by A, then shrinks it back to length 1. The blue line is the true top eigenvector.');
    const MS = { a: [[4, 1], [2, 3]], s: [[2, 1], [1, 2]], c: [[1, 0.1], [0.1, 0.95]] };
    b.innerHTML = `<div class="vz-row">${seg('m', [['a', '[[4, 1], [2, 3]]'], ['s', '[[2, 1], [1, 2]]'], ['c', 'close eigenvalues']], 'a')}</div><div class="mv-wrap"><div class="pi-plot"></div><div class="mv-side">${slider('ang', 'start angle °', 0, 350, 160, 10)}<div class="mv-read pi-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let A = MS.a, ang = 160, path = [];
    const G = MV.frame(400, 400, [-2.2, 2.2], [-2.2, 2.2]);
    const top = () => { const tr = A[0][0] + A[1][1], det = A[0][0] * A[1][1] - A[0][1] * A[1][0], r = Math.sqrt(tr * tr - 4 * det), l1 = (tr + r) / 2, l2 = (tr - r) / 2; const v = [A[0][1], l1 - A[0][0]], L = Math.hypot(...v); return { l1, l2, v: [v[0] / L, v[1] / L] }; };
    function plan() {
      let x = [Math.cos(ang * Math.PI / 180), Math.sin(ang * Math.PI / 180)];
      path = [{ x, y: null }];
      for (let k = 0; k < 14; k++) { const y = [A[0][0] * x[0] + A[0][1] * x[1], A[1][0] * x[0] + A[1][1] * x[1]], L = Math.hypot(...y); path[path.length - 1].y = y; x = [y[0] / L, y[1] / L]; path.push({ x, y: null }); }
      P.load(path.length, 0);
    }
    function show(t) {
      const T = top(), x = path[t].x;
      let s = MV.axes(G, { labels: false });
      s += `<circle cx="${G.sx(0)}" cy="${G.sy(0)}" r="${G.sx(1) - G.sx(0)}" class="mv-cont"/>`;
      s += MV.line(G, -2.2 * T.v[0], -2.2 * T.v[1], 2.2 * T.v[0], 2.2 * T.v[1], 'mv-v a dash');
      for (let k = 0; k < t; k++) s += MV.dot(G, path[k].x[0], path[k].x[1], 'k', 3);
      const y = [A[0][0] * x[0] + A[0][1] * x[1], A[1][0] * x[0] + A[1][1] * x[1]], sc = Math.min(1, 2 / Math.hypot(...y));
      s += MV.arrow(G, 0, 0, y[0] * sc, y[1] * sc, 'p', 'dash') + MV.arrow(G, 0, 0, x[0], x[1], 'o');
      $('.pi-plot', b).innerHTML = MV.svg(G, s, 'Power iteration');
      const ray = x[0] * y[0] + x[1] * y[1], cosang = Math.abs(x[0] * T.v[0] + x[1] * T.v[1]);
      $('.pi-out', b).innerHTML = `step ${t}<br>guess = [${MV.num(x[0], 3)}, ${MV.num(x[1], 3)}]<br>Rayleigh estimate xᵀAx = <b>${MV.num(ray, 4)}</b><br>true λ₁ = ${MV.num(T.l1, 4)}, λ₂ = ${MV.num(T.l2, 4)}<br>angle to the eigenvector: <b>${MV.num(Math.acos(Math.min(1, cosang)) * 180 / Math.PI, 2)}°</b><br>ratio |λ₂ ÷ λ₁| = ${MV.num(Math.abs(T.l2 / T.l1), 3)}${Math.abs(T.l2 / T.l1) > 0.8 ? ' (slow)' : ''}` + (t ? '' : '<br><small>The purple dashed arrow is A times the guess, shrunk to fit.</small>');
    }
    const P = Player($('.vz-p', b), show, 800);
    wireSeg(b, 'm', v => { A = MS[v]; plan(); });
    wireSlider(b, 'ang', v => { ang = v; plan(); });
    plan();
  };
})();
'''
CSS += r'''
.pi-plot .mv-svg,.cpl-plot .mv-svg{max-height:400px}
'''

T = K.topic(
    slug='eigen-svd-pca', topic='eigen-svd-pca', prefix='mm05', short='Eigen, SVD, PCA', emoji='🧭',
    title='Eigenvalues, SVD and PCA',
    module=('🧮', 'Linear algebra', 'linear-algebra', 'Vectors, matrices, eigenvalues, SVD and PCA: the maths that lets a model handle thousands of numbers at once.'),
    minutes=60,
    lead='Some directions are special for a matrix: it only stretches them. Hunt for these eigenvectors with an animation, find them by hand, watch the SVD turn a circle into an ellipse, and run PCA step by step to squash data into fewer numbers.',
    desc='Eigenvalues and eigenvectors for machine learning: the characteristic equation, trace and determinant rules, diagonalisation, power iteration and PageRank, singular value decomposition, low rank approximation and principal component analysis.',
    summary='Eigenvectors as directions a matrix keeps, the characteristic equation, the trace and determinant checks, diagonalisation and matrix powers, Markov steady states, power iteration and PageRank, SVD as rotate stretch rotate, low rank approximation, PCA step by step, explained variance and the condition number.',
    keywords=['eigenvalue', 'eigenvector', 'characteristic equation', 'trace', 'diagonalisation', 'power iteration', 'pagerank', 'svd', 'singular value decomposition', 'singular values', 'low rank approximation', 'pca', 'principal component analysis', 'covariance matrix', 'explained variance', 'condition number'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
