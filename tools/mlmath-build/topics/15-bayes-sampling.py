# Chapter 15: joint, marginal and conditional distributions, the multivariate normal and Mahalanobis distance,
# Bayesian inference with conjugate priors (Beta Binomial, MAP versus MLE), Markov chains and stationary
# distributions, Monte Carlo estimation with inverse transform sampling, MCMC with Metropolis, and
# concentration inequalities (Markov, Chebyshev, Hoeffding) with the law of large numbers.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz, deep

K = Kit()

# ---------------------------------------------------------------- programs
K.code('joint_table', py=r'''
def f(v):
    return f"{v:.4f}"


rows = ["sunny", "cloudy", "rainy"]
counts = [[40, 5],                        # columns: no umbrella, umbrella
          [20, 10],
          [5, 20]]
n = sum(sum(r) for r in counts)
joint = [[c / n for c in r] for r in counts]
px = [r[0] + r[1] for r in joint]                         # add across each row
py = [joint[0][j] + joint[1][j] + joint[2][j] for j in range(2)]   # add down each column
for i in range(3):
    print(f"P({rows[i]}) = {f(px[i])}")
print(f"P(umbrella) = {f(py[1])}")
print(f"P(rainy and umbrella) = {f(joint[2][1])}")
print(f"P(umbrella | rainy) = {f(joint[2][1] / px[2])}")
print(f"P(rainy | umbrella) = {f(joint[2][1] / py[1])}")
prod = px[2] * py[1]
print(f"P(rainy) x P(umbrella) = {f(prod)}, so they are {'independent' if abs(prod - joint[2][1]) < 1e-12 else 'dependent'}")
''', js=r'''
const f = v => v.toFixed(4);

const rows = ["sunny", "cloudy", "rainy"];
const counts = [[40, 5],                  // columns: no umbrella, umbrella
                [20, 10],
                [5, 20]];
const n = counts.reduce((s, r) => s + r[0] + r[1], 0);
const joint = counts.map(r => r.map(c => c / n));
const px = joint.map(r => r[0] + r[1]);                  // add across each row
const py = [0, 1].map(j => joint[0][j] + joint[1][j] + joint[2][j]);   // add down each column
for (let i = 0; i < 3; i++) console.log(`P(${rows[i]}) = ${f(px[i])}`);
console.log(`P(umbrella) = ${f(py[1])}`);
console.log(`P(rainy and umbrella) = ${f(joint[2][1])}`);
console.log(`P(umbrella | rainy) = ${f(joint[2][1] / px[2])}`);
console.log(`P(rainy | umbrella) = ${f(joint[2][1] / py[1])}`);
const prod = px[2] * py[1];
console.log(`P(rainy) x P(umbrella) = ${f(prod)}, so they are ${Math.abs(prod - joint[2][1]) < 1e-12 ? "independent" : "dependent"}`);
''', ts=r'''
const f = (v: number): string => v.toFixed(4);

const rows: string[] = ["sunny", "cloudy", "rainy"];
const counts: number[][] = [[40, 5],      // columns: no umbrella, umbrella
                            [20, 10],
                            [5, 20]];
const n: number = counts.reduce((s, r) => s + r[0] + r[1], 0);
const joint: number[][] = counts.map(r => r.map(c => c / n));
const px: number[] = joint.map(r => r[0] + r[1]);        // add across each row
const py: number[] = [0, 1].map(j => joint[0][j] + joint[1][j] + joint[2][j]);   // add down each column
for (let i = 0; i < 3; i++) console.log(`P(${rows[i]}) = ${f(px[i])}`);
console.log(`P(umbrella) = ${f(py[1])}`);
console.log(`P(rainy and umbrella) = ${f(joint[2][1])}`);
console.log(`P(umbrella | rainy) = ${f(joint[2][1] / px[2])}`);
console.log(`P(rainy | umbrella) = ${f(joint[2][1] / py[1])}`);
const prod: number = px[2] * py[1];
console.log(`P(rainy) x P(umbrella) = ${f(prod)}, so they are ${Math.abs(prod - joint[2][1]) < 1e-12 ? "independent" : "dependent"}`);
''', java=r'''
public class JointTable {
    static String f(double v) {
        return String.format("%.4f", v);
    }

    public static void main(String[] args) {
        String[] rows = {"sunny", "cloudy", "rainy"};
        int[][] counts = {{40, 5},            // columns: no umbrella, umbrella
                          {20, 10},
                          {5, 20}};
        int n = 0;
        for (int[] r : counts) n += r[0] + r[1];
        double[][] joint = new double[3][2];
        for (int i = 0; i < 3; i++) for (int j = 0; j < 2; j++) joint[i][j] = (double) counts[i][j] / n;
        double[] px = new double[3], py = new double[2];
        for (int i = 0; i < 3; i++) px[i] = joint[i][0] + joint[i][1];                      // add across each row
        for (int j = 0; j < 2; j++) py[j] = joint[0][j] + joint[1][j] + joint[2][j];        // add down each column
        for (int i = 0; i < 3; i++) System.out.println("P(" + rows[i] + ") = " + f(px[i]));
        System.out.println("P(umbrella) = " + f(py[1]));
        System.out.println("P(rainy and umbrella) = " + f(joint[2][1]));
        System.out.println("P(umbrella | rainy) = " + f(joint[2][1] / px[2]));
        System.out.println("P(rainy | umbrella) = " + f(joint[2][1] / py[1]));
        double prod = px[2] * py[1];
        System.out.println("P(rainy) x P(umbrella) = " + f(prod) + ", so they are " + (Math.abs(prod - joint[2][1]) < 1e-12 ? "independent" : "dependent"));
    }
}
''')

K.code('mahalanobis', py=r'''
import math


def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


S = [[4.0, 2.0], [2.0, 3.0]]              # covariance: x varies more, and x and y rise together
det = S[0][0] * S[1][1] - S[0][1] * S[1][0]
inv = [[S[1][1] / det, -S[0][1] / det], [-S[1][0] / det, S[0][0] / det]]
for name, p in [("a", [2.0, 2.0]), ("b", [2.0, -2.0])]:
    d2 = sum(p[i] * inv[i][j] * p[j] for i in range(2) for j in range(2))   # p^T S^-1 p (the mean is 0)
    print(f"{name} = {p}: Euclidean {f(math.hypot(p[0], p[1]))}, Mahalanobis {f(math.sqrt(d2))}")

l11 = math.sqrt(S[0][0])                  # Cholesky S = L L^T, used to draw samples
l21 = S[1][0] / l11
l22 = math.sqrt(S[1][1] - l21 * l21)
print(f"L = [[{f(l11)}, 0], [{f(l21)}, {f(l22)}]]")
z = [1.0, 0.5]                            # standard normal noise
x = [l11 * z[0], l21 * z[0] + l22 * z[1]] # x = L z has covariance S
print(f"z = [1, 0.5] becomes x = [{f(x[0])}, {f(x[1])}]")
''', js=r'''
const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

const S = [[4, 2], [2, 3]];               // covariance: x varies more, and x and y rise together
const det = S[0][0] * S[1][1] - S[0][1] * S[1][0];
const inv = [[S[1][1] / det, -S[0][1] / det], [-S[1][0] / det, S[0][0] / det]];
for (const [name, p] of [["a", [2, 2]], ["b", [2, -2]]]) {
  let d2 = 0;
  for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) d2 += p[i] * inv[i][j] * p[j];   // p^T S^-1 p (the mean is 0)
  console.log(`${name} = [${p.map(v => v.toFixed(1)).join(", ")}]: Euclidean ${f(Math.hypot(p[0], p[1]))}, Mahalanobis ${f(Math.sqrt(d2))}`);
}

const l11 = Math.sqrt(S[0][0]);           // Cholesky S = L L^T, used to draw samples
const l21 = S[1][0] / l11;
const l22 = Math.sqrt(S[1][1] - l21 * l21);
console.log(`L = [[${f(l11)}, 0], [${f(l21)}, ${f(l22)}]]`);
const z = [1, 0.5];                       // standard normal noise
const x = [l11 * z[0], l21 * z[0] + l22 * z[1]];   // x = L z has covariance S
console.log(`z = [1, 0.5] becomes x = [${f(x[0])}, ${f(x[1])}]`);
''', ts=r'''
const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);

const S: number[][] = [[4, 2], [2, 3]];   // covariance: x varies more, and x and y rise together
const det: number = S[0][0] * S[1][1] - S[0][1] * S[1][0];
const inv: number[][] = [[S[1][1] / det, -S[0][1] / det], [-S[1][0] / det, S[0][0] / det]];
const pts: [string, number[]][] = [["a", [2, 2]], ["b", [2, -2]]];
for (const [name, p] of pts) {
  let d2 = 0;
  for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) d2 += p[i] * inv[i][j] * p[j];   // p^T S^-1 p (the mean is 0)
  console.log(`${name} = [${p.map(v => v.toFixed(1)).join(", ")}]: Euclidean ${f(Math.hypot(p[0], p[1]))}, Mahalanobis ${f(Math.sqrt(d2))}`);
}

const l11: number = Math.sqrt(S[0][0]);   // Cholesky S = L L^T, used to draw samples
const l21: number = S[1][0] / l11;
const l22: number = Math.sqrt(S[1][1] - l21 * l21);
console.log(`L = [[${f(l11)}, 0], [${f(l21)}, ${f(l22)}]]`);
const z: number[] = [1, 0.5];             // standard normal noise
const x: number[] = [l11 * z[0], l21 * z[0] + l22 * z[1]];   // x = L z has covariance S
console.log(`z = [1, 0.5] becomes x = [${f(x[0])}, ${f(x[1])}]`);
''', java=r'''
public class Mahalanobis {
    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    public static void main(String[] args) {
        double[][] S = {{4, 2}, {2, 3}};      // covariance: x varies more, and x and y rise together
        double det = S[0][0] * S[1][1] - S[0][1] * S[1][0];
        double[][] inv = {{S[1][1] / det, -S[0][1] / det}, {-S[1][0] / det, S[0][0] / det}};
        String[] names = {"a", "b"};
        double[][] pts = {{2, 2}, {2, -2}};
        for (int k = 0; k < 2; k++) {
            double[] p = pts[k];
            double d2 = 0;
            for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) d2 += p[i] * inv[i][j] * p[j];   // p^T S^-1 p (the mean is 0)
            System.out.println(names[k] + " = [" + p[0] + ", " + p[1] + "]: Euclidean " + f(Math.hypot(p[0], p[1])) + ", Mahalanobis " + f(Math.sqrt(d2)));
        }
        double l11 = Math.sqrt(S[0][0]);      // Cholesky S = L L^T, used to draw samples
        double l21 = S[1][0] / l11;
        double l22 = Math.sqrt(S[1][1] - l21 * l21);
        System.out.println("L = [[" + f(l11) + ", 0], [" + f(l21) + ", " + f(l22) + "]]");
        double[] z = {1, 0.5};                // standard normal noise
        double[] x = {l11 * z[0], l21 * z[0] + l22 * z[1]};   // x = L z has covariance S
        System.out.println("z = [1, 0.5] becomes x = [" + f(x[0]) + ", " + f(x[1]) + "]");
    }
}
''')

K.code('beta_update', py=r'''
def f(v):
    return f"{v:.4f}"


a, b = 2, 2                               # prior Beta(2, 2): a gentle belief that the coin is fair
flips = "HHTHHHTHHT"
for i, c in enumerate(flips, 1):
    if c == "H":                          # each head adds 1 to a, each tail adds 1 to b
        a += 1
    else:
        b += 1
    if i in (1, 5, 10):
        print(f"after {i} flips: Beta({a}, {b}), mean {f(a / (a + b))}")
heads = flips.count("H")
print(f"MLE = heads / flips = {f(heads / len(flips))}")
print(f"MAP = (a - 1) / (a + b - 2) = {f((a - 1) / (a + b - 2))}")
print(f"posterior mean = a / (a + b) = {f(a / (a + b))}")
''', js=r'''
const f = v => v.toFixed(4);

let a = 2, b = 2;                         // prior Beta(2, 2): a gentle belief that the coin is fair
const flips = "HHTHHHTHHT";
[...flips].forEach((c, k) => {
  const i = k + 1;
  if (c === "H") a += 1;                  // each head adds 1 to a, each tail adds 1 to b
  else b += 1;
  if (i === 1 || i === 5 || i === 10) console.log(`after ${i} flips: Beta(${a}, ${b}), mean ${f(a / (a + b))}`);
});
const heads = [...flips].filter(c => c === "H").length;
console.log(`MLE = heads / flips = ${f(heads / flips.length)}`);
console.log(`MAP = (a - 1) / (a + b - 2) = ${f((a - 1) / (a + b - 2))}`);
console.log(`posterior mean = a / (a + b) = ${f(a / (a + b))}`);
''', ts=r'''
const f = (v: number): string => v.toFixed(4);

let a: number = 2, b: number = 2;         // prior Beta(2, 2): a gentle belief that the coin is fair
const flips: string = "HHTHHHTHHT";
[...flips].forEach((c, k) => {
  const i: number = k + 1;
  if (c === "H") a += 1;                  // each head adds 1 to a, each tail adds 1 to b
  else b += 1;
  if (i === 1 || i === 5 || i === 10) console.log(`after ${i} flips: Beta(${a}, ${b}), mean ${f(a / (a + b))}`);
});
const heads: number = [...flips].filter(c => c === "H").length;
console.log(`MLE = heads / flips = ${f(heads / flips.length)}`);
console.log(`MAP = (a - 1) / (a + b - 2) = ${f((a - 1) / (a + b - 2))}`);
console.log(`posterior mean = a / (a + b) = ${f(a / (a + b))}`);
''', java=r'''
public class BetaUpdate {
    static String f(double v) {
        return String.format("%.4f", v);
    }

    public static void main(String[] args) {
        int a = 2, b = 2;                     // prior Beta(2, 2): a gentle belief that the coin is fair
        String flips = "HHTHHHTHHT";
        int heads = 0;
        for (int k = 0; k < flips.length(); k++) {
            int i = k + 1;
            if (flips.charAt(k) == 'H') {     // each head adds 1 to a, each tail adds 1 to b
                a += 1;
                heads += 1;
            } else {
                b += 1;
            }
            if (i == 1 || i == 5 || i == 10) System.out.println("after " + i + " flips: Beta(" + a + ", " + b + "), mean " + f((double) a / (a + b)));
        }
        System.out.println("MLE = heads / flips = " + f((double) heads / flips.length()));
        System.out.println("MAP = (a - 1) / (a + b - 2) = " + f((double) (a - 1) / (a + b - 2)));
        System.out.println("posterior mean = a / (a + b) = " + f((double) a / (a + b)));
    }
}
''')

K.code('markov_chain', py=r'''
def f(v):
    return f"{v:.4f}"


P = [[0.7, 0.2, 0.1],                     # row = today, column = tomorrow: sunny, cloudy, rainy
     [0.3, 0.4, 0.3],
     [0.2, 0.3, 0.5]]
pi = [1.0, 0.0, 0.0]                      # today is surely sunny
for t in range(1, 51):
    pi = [pi[0] * P[0][j] + pi[1] * P[1][j] + pi[2] * P[2][j] for j in range(3)]   # pi_(t+1) = pi_t P
    if t in (1, 2, 3, 10, 50):
        print(f"day {t}: [{', '.join(f(p) for p in pi)}]")
check = [pi[0] * P[0][j] + pi[1] * P[1][j] + pi[2] * P[2][j] for j in range(3)]
print(f"pi P = [{', '.join(f(p) for p in check)}], unchanged, so pi is stationary")
''', js=r'''
const f = v => v.toFixed(4);

const P = [[0.7, 0.2, 0.1],               // row = today, column = tomorrow: sunny, cloudy, rainy
           [0.3, 0.4, 0.3],
           [0.2, 0.3, 0.5]];
let pi = [1, 0, 0];                       // today is surely sunny
for (let t = 1; t <= 50; t++) {
  pi = [0, 1, 2].map(j => pi[0] * P[0][j] + pi[1] * P[1][j] + pi[2] * P[2][j]);   // pi_(t+1) = pi_t P
  if ([1, 2, 3, 10, 50].includes(t)) console.log(`day ${t}: [${pi.map(f).join(", ")}]`);
}
const check = [0, 1, 2].map(j => pi[0] * P[0][j] + pi[1] * P[1][j] + pi[2] * P[2][j]);
console.log(`pi P = [${check.map(f).join(", ")}], unchanged, so pi is stationary`);
''', ts=r'''
const f = (v: number): string => v.toFixed(4);

const P: number[][] = [[0.7, 0.2, 0.1],   // row = today, column = tomorrow: sunny, cloudy, rainy
                       [0.3, 0.4, 0.3],
                       [0.2, 0.3, 0.5]];
let pi: number[] = [1, 0, 0];             // today is surely sunny
for (let t = 1; t <= 50; t++) {
  pi = [0, 1, 2].map(j => pi[0] * P[0][j] + pi[1] * P[1][j] + pi[2] * P[2][j]);   // pi_(t+1) = pi_t P
  if ([1, 2, 3, 10, 50].includes(t)) console.log(`day ${t}: [${pi.map(f).join(", ")}]`);
}
const check: number[] = [0, 1, 2].map(j => pi[0] * P[0][j] + pi[1] * P[1][j] + pi[2] * P[2][j]);
console.log(`pi P = [${check.map(f).join(", ")}], unchanged, so pi is stationary`);
''', java=r'''
public class MarkovChain {
    static String f(double v) {
        return String.format("%.4f", v);
    }

    static double[] step(double[] pi, double[][] P) {
        double[] next = new double[3];
        for (int j = 0; j < 3; j++) next[j] = pi[0] * P[0][j] + pi[1] * P[1][j] + pi[2] * P[2][j];   // pi_(t+1) = pi_t P
        return next;
    }

    static String show(double[] v) {
        return "[" + f(v[0]) + ", " + f(v[1]) + ", " + f(v[2]) + "]";
    }

    public static void main(String[] args) {
        double[][] P = {{0.7, 0.2, 0.1},      // row = today, column = tomorrow: sunny, cloudy, rainy
                        {0.3, 0.4, 0.3},
                        {0.2, 0.3, 0.5}};
        double[] pi = {1, 0, 0};              // today is surely sunny
        for (int t = 1; t <= 50; t++) {
            pi = step(pi, P);
            if (t == 1 || t == 2 || t == 3 || t == 10 || t == 50) System.out.println("day " + t + ": " + show(pi));
        }
        System.out.println("pi P = " + show(step(pi, P)) + ", unchanged, so pi is stationary");
    }
}
''')

K.code('monte_carlo_int', py=r'''
import math

seed = 2026


def rand():                               # a small repeatable random number maker (Park and Miller)
    global seed
    seed = seed * 16807 % 2147483647
    return seed / 2147483647


def f(v):
    return f"{v:.4f}"


true = math.e - 1                         # the integral of e^x from 0 to 1
total = 0.0
total_sq = 0.0
for i in range(1, 101):
    v = math.exp(rand())                  # f(U) for a uniform U between 0 and 1
    total += v
    total_sq += v * v
    if i in (10, 30, 100):
        mean = total / i
        sd = math.sqrt(total_sq / i - mean * mean)
        print(f"n = {i}: estimate {f(mean)}, error {f(abs(mean - true))}, standard error {f(sd / math.sqrt(i))}")
print(f"true value e - 1 = {f(true)}")
''', js=r'''
let seed = 2026;

function rand() {                         // a small repeatable random number maker (Park and Miller)
  seed = seed * 16807 % 2147483647;
  return seed / 2147483647;
}

const f = v => v.toFixed(4);

const truth = Math.E - 1;                 // the integral of e^x from 0 to 1
let total = 0, totalSq = 0;
for (let i = 1; i <= 100; i++) {
  const v = Math.exp(rand());             // f(U) for a uniform U between 0 and 1
  total += v;
  totalSq += v * v;
  if (i === 10 || i === 30 || i === 100) {
    const mean = total / i;
    const sd = Math.sqrt(totalSq / i - mean * mean);
    console.log(`n = ${i}: estimate ${f(mean)}, error ${f(Math.abs(mean - truth))}, standard error ${f(sd / Math.sqrt(i))}`);
  }
}
console.log(`true value e - 1 = ${f(truth)}`);
''', ts=r'''
let seed: number = 2026;

function rand(): number {                 // a small repeatable random number maker (Park and Miller)
  seed = seed * 16807 % 2147483647;
  return seed / 2147483647;
}

const f = (v: number): string => v.toFixed(4);

const truth: number = Math.E - 1;         // the integral of e^x from 0 to 1
let total = 0, totalSq = 0;
for (let i = 1; i <= 100; i++) {
  const v: number = Math.exp(rand());     // f(U) for a uniform U between 0 and 1
  total += v;
  totalSq += v * v;
  if (i === 10 || i === 30 || i === 100) {
    const mean: number = total / i;
    const sd: number = Math.sqrt(totalSq / i - mean * mean);
    console.log(`n = ${i}: estimate ${f(mean)}, error ${f(Math.abs(mean - truth))}, standard error ${f(sd / Math.sqrt(i))}`);
  }
}
console.log(`true value e - 1 = ${f(truth)}`);
''', java=r'''
public class MonteCarloInt {
    static long seed = 2026;

    static double rand() {                    // a small repeatable random number maker (Park and Miller)
        seed = seed * 16807 % 2147483647;
        return seed / 2147483647.0;
    }

    static String f(double v) {
        return String.format("%.4f", v);
    }

    public static void main(String[] args) {
        double truth = Math.E - 1;            // the integral of e^x from 0 to 1
        double total = 0, totalSq = 0;
        for (int i = 1; i <= 100; i++) {
            double v = Math.exp(rand());      // f(U) for a uniform U between 0 and 1
            total += v;
            totalSq += v * v;
            if (i == 10 || i == 30 || i == 100) {
                double mean = total / i;
                double sd = Math.sqrt(totalSq / i - mean * mean);
                System.out.println("n = " + i + ": estimate " + f(mean) + ", error " + f(Math.abs(mean - truth)) + ", standard error " + f(sd / Math.sqrt(i)));
            }
        }
        System.out.println("true value e - 1 = " + f(truth));
    }
}
''')

K.code('inverse_transform', py=r'''
import math

seed = 2026


def rand():                               # a small repeatable random number maker (Park and Miller)
    global seed
    seed = seed * 16807 % 2147483647
    return seed / 2147483647


def f(v):
    return f"{v:.4f}"


lam = 2.0                                 # an exponential waiting time with rate 2 per hour
n = 100
total = 0.0
below = 0
for i in range(n):
    u = rand()
    x = -math.log(1 - u) / lam            # solve u = F(x) = 1 - e^(-lam x) for x
    if i < 3:
        print(f"u = {f(u)} -> x = {f(x)}")
    total += x
    if x < 0.5:
        below += 1
print(f"sample mean = {f(total / n)}, true mean 1/lambda = {f(1 / lam)}")
print(f"fraction below 0.5 = {f(below / n)}, true F(0.5) = {f(1 - math.exp(-lam * 0.5))}")
''', js=r'''
let seed = 2026;

function rand() {                         // a small repeatable random number maker (Park and Miller)
  seed = seed * 16807 % 2147483647;
  return seed / 2147483647;
}

const f = v => v.toFixed(4);

const lam = 2;                            // an exponential waiting time with rate 2 per hour
const n = 100;
let total = 0, below = 0;
for (let i = 0; i < n; i++) {
  const u = rand();
  const x = -Math.log(1 - u) / lam;       // solve u = F(x) = 1 - e^(-lam x) for x
  if (i < 3) console.log(`u = ${f(u)} -> x = ${f(x)}`);
  total += x;
  if (x < 0.5) below += 1;
}
console.log(`sample mean = ${f(total / n)}, true mean 1/lambda = ${f(1 / lam)}`);
console.log(`fraction below 0.5 = ${f(below / n)}, true F(0.5) = ${f(1 - Math.exp(-lam * 0.5))}`);
''', ts=r'''
let seed: number = 2026;

function rand(): number {                 // a small repeatable random number maker (Park and Miller)
  seed = seed * 16807 % 2147483647;
  return seed / 2147483647;
}

const f = (v: number): string => v.toFixed(4);

const lam: number = 2;                    // an exponential waiting time with rate 2 per hour
const n: number = 100;
let total = 0, below = 0;
for (let i = 0; i < n; i++) {
  const u: number = rand();
  const x: number = -Math.log(1 - u) / lam;   // solve u = F(x) = 1 - e^(-lam x) for x
  if (i < 3) console.log(`u = ${f(u)} -> x = ${f(x)}`);
  total += x;
  if (x < 0.5) below += 1;
}
console.log(`sample mean = ${f(total / n)}, true mean 1/lambda = ${f(1 / lam)}`);
console.log(`fraction below 0.5 = ${f(below / n)}, true F(0.5) = ${f(1 - Math.exp(-lam * 0.5))}`);
''', java=r'''
public class InverseTransform {
    static long seed = 2026;

    static double rand() {                    // a small repeatable random number maker (Park and Miller)
        seed = seed * 16807 % 2147483647;
        return seed / 2147483647.0;
    }

    static String f(double v) {
        return String.format("%.4f", v);
    }

    public static void main(String[] args) {
        double lam = 2;                       // an exponential waiting time with rate 2 per hour
        int n = 100, below = 0;
        double total = 0;
        for (int i = 0; i < n; i++) {
            double u = rand();
            double x = -Math.log(1 - u) / lam;    // solve u = F(x) = 1 - e^(-lam x) for x
            if (i < 3) System.out.println("u = " + f(u) + " -> x = " + f(x));
            total += x;
            if (x < 0.5) below += 1;
        }
        System.out.println("sample mean = " + f(total / n) + ", true mean 1/lambda = " + f(1 / lam));
        System.out.println("fraction below 0.5 = " + f((double) below / n) + ", true F(0.5) = " + f(1 - Math.exp(-lam * 0.5)));
    }
}
''')

K.code('metropolis', py=r'''
import math

seed = 2026


def rand():                               # a small repeatable random number maker (Park and Miller)
    global seed
    seed = seed * 16807 % 2147483647
    return seed / 2147483647


def f(v):
    return f"{0.0 if abs(v) < 5e-5 else v:.4f}"


def target(x):                            # the bell shape of a standard normal, no constant needed
    return math.exp(-x * x / 2)


x = 3.0                                   # a poor starting point on purpose
step = 1.5
accepted = 0
kept = []
for i in range(1, 81):
    proposal = x + step * (2 * rand() - 1)        # try a random nearby point
    if rand() < target(proposal) / target(x):     # always accept uphill, sometimes downhill
        x = proposal
        accepted += 1
    if i > 10:                            # drop the first 10 steps as burn in
        kept.append(x)
mean = sum(kept) / len(kept)
var = sum((v - mean) ** 2 for v in kept) / len(kept)
print(f"acceptance rate = {f(accepted / 80)}")
print(f"sample mean = {f(mean)} (true 0)")
print(f"sample variance = {f(var)} (true 1)")
''', js=r'''
let seed = 2026;

function rand() {                         // a small repeatable random number maker (Park and Miller)
  seed = seed * 16807 % 2147483647;
  return seed / 2147483647;
}

const f = v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);
const target = x => Math.exp(-x * x / 2); // the bell shape of a standard normal, no constant needed

let x = 3;                                // a poor starting point on purpose
const step = 1.5;
let accepted = 0;
const kept = [];
for (let i = 1; i <= 80; i++) {
  const proposal = x + step * (2 * rand() - 1);   // try a random nearby point
  if (rand() < target(proposal) / target(x)) {    // always accept uphill, sometimes downhill
    x = proposal;
    accepted += 1;
  }
  if (i > 10) kept.push(x);               // drop the first 10 steps as burn in
}
const mean = kept.reduce((a, b) => a + b, 0) / kept.length;
const variance = kept.reduce((a, v) => a + (v - mean) ** 2, 0) / kept.length;
console.log(`acceptance rate = ${f(accepted / 80)}`);
console.log(`sample mean = ${f(mean)} (true 0)`);
console.log(`sample variance = ${f(variance)} (true 1)`);
''', ts=r'''
let seed: number = 2026;

function rand(): number {                 // a small repeatable random number maker (Park and Miller)
  seed = seed * 16807 % 2147483647;
  return seed / 2147483647;
}

const f = (v: number): string => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4);
const target = (x: number): number => Math.exp(-x * x / 2);   // the bell shape of a standard normal, no constant needed

let x: number = 3;                        // a poor starting point on purpose
const step: number = 1.5;
let accepted = 0;
const kept: number[] = [];
for (let i = 1; i <= 80; i++) {
  const proposal: number = x + step * (2 * rand() - 1);   // try a random nearby point
  if (rand() < target(proposal) / target(x)) {            // always accept uphill, sometimes downhill
    x = proposal;
    accepted += 1;
  }
  if (i > 10) kept.push(x);               // drop the first 10 steps as burn in
}
const mean: number = kept.reduce((a, b) => a + b, 0) / kept.length;
const variance: number = kept.reduce((a, v) => a + (v - mean) ** 2, 0) / kept.length;
console.log(`acceptance rate = ${f(accepted / 80)}`);
console.log(`sample mean = ${f(mean)} (true 0)`);
console.log(`sample variance = ${f(variance)} (true 1)`);
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class Metropolis {
    static long seed = 2026;

    static double rand() {                    // a small repeatable random number maker (Park and Miller)
        seed = seed * 16807 % 2147483647;
        return seed / 2147483647.0;
    }

    static String f(double v) {
        return String.format("%.4f", Math.abs(v) < 5e-5 ? 0.0 : v);
    }

    static double target(double x) {         // the bell shape of a standard normal, no constant needed
        return Math.exp(-x * x / 2);
    }

    public static void main(String[] args) {
        double x = 3;                         // a poor starting point on purpose
        double step = 1.5;
        int accepted = 0;
        List<Double> kept = new ArrayList<>();
        for (int i = 1; i <= 80; i++) {
            double proposal = x + step * (2 * rand() - 1);   // try a random nearby point
            if (rand() < target(proposal) / target(x)) {     // always accept uphill, sometimes downhill
                x = proposal;
                accepted += 1;
            }
            if (i > 10) kept.add(x);          // drop the first 10 steps as burn in
        }
        double mean = 0;
        for (double v : kept) mean += v;
        mean /= kept.size();
        double variance = 0;
        for (double v : kept) variance += (v - mean) * (v - mean);
        variance /= kept.size();
        System.out.println("acceptance rate = " + f(accepted / 80.0));
        System.out.println("sample mean = " + f(mean) + " (true 0)");
        System.out.println("sample variance = " + f(variance) + " (true 1)");
    }
}
''')

K.code('concentration', py=r'''
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


# a fair coin flipped n times: how likely is the share of heads to miss 0.5 by 0.1 or more?
for n in [100, 200]:
    pk = 0.5 ** n                         # P(0 heads), then P(k + 1) = P(k) (n - k) / (k + 1)
    exact = 0.0
    for k in range(n + 1):
        if 5 * abs(2 * k - n) >= n:       # |k/n - 0.5| >= 0.1, tested with whole numbers
            exact += pk
        pk = pk * (n - k) / (k + 1)
    cheb = 0.25 / (n * 0.1 * 0.1)         # variance / (n eps^2)
    hoef = 2 * math.exp(-2 * n * 0.1 * 0.1)
    print(f"n = {n}: exact {sci(exact)}, Chebyshev bound {sci(cheb)}, Hoeffding bound {sci(hoef)}")
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

// a fair coin flipped n times: how likely is the share of heads to miss 0.5 by 0.1 or more?
for (const n of [100, 200]) {
  let pk = 0.5 ** n;                      // P(0 heads), then P(k + 1) = P(k) (n - k) / (k + 1)
  let exact = 0;
  for (let k = 0; k <= n; k++) {
    if (5 * Math.abs(2 * k - n) >= n) exact += pk;   // |k/n - 0.5| >= 0.1, tested with whole numbers
    pk = pk * (n - k) / (k + 1);
  }
  const cheb = 0.25 / (n * 0.1 * 0.1);    // variance / (n eps^2)
  const hoef = 2 * Math.exp(-2 * n * 0.1 * 0.1);
  console.log(`n = ${n}: exact ${sci(exact)}, Chebyshev bound ${sci(cheb)}, Hoeffding bound ${sci(hoef)}`);
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

// a fair coin flipped n times: how likely is the share of heads to miss 0.5 by 0.1 or more?
for (const n of [100, 200]) {
  let pk: number = 0.5 ** n;              // P(0 heads), then P(k + 1) = P(k) (n - k) / (k + 1)
  let exact = 0;
  for (let k = 0; k <= n; k++) {
    if (5 * Math.abs(2 * k - n) >= n) exact += pk;   // |k/n - 0.5| >= 0.1, tested with whole numbers
    pk = pk * (n - k) / (k + 1);
  }
  const cheb: number = 0.25 / (n * 0.1 * 0.1);   // variance / (n eps^2)
  const hoef: number = 2 * Math.exp(-2 * n * 0.1 * 0.1);
  console.log(`n = ${n}: exact ${sci(exact)}, Chebyshev bound ${sci(cheb)}, Hoeffding bound ${sci(hoef)}`);
}
''', java=r'''
public class Concentration {
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
        // a fair coin flipped n times: how likely is the share of heads to miss 0.5 by 0.1 or more?
        for (int n : new int[]{100, 200}) {
            double pk = Math.pow(0.5, n);     // P(0 heads), then P(k + 1) = P(k) (n - k) / (k + 1)
            double exact = 0;
            for (int k = 0; k <= n; k++) {
                if (5 * Math.abs(2 * k - n) >= n) exact += pk;   // |k/n - 0.5| >= 0.1, tested with whole numbers
                pk = pk * (n - k) / (k + 1);
            }
            double cheb = 0.25 / (n * 0.1 * 0.1);   // variance / (n eps^2)
            double hoef = 2 * Math.exp(-2 * n * 0.1 * 0.1);
            System.out.println("n = " + n + ": exact " + sci(exact) + ", Chebyshev bound " + sci(cheb) + ", Hoeffding bound " + sci(hoef));
        }
    }
}
''')

# ---- practice programs
K.code('p_two_state', py=r'''
def f(v):
    return f"{v:.4f}"


a = 0.1                                   # P(sunny -> rainy)
b = 0.5                                   # P(rainy -> sunny)
print(f"formula: pi = [b / (a + b), a / (a + b)] = [{f(b / (a + b))}, {f(a / (a + b))}]")
pi = [0.0, 1.0]                           # start on a rainy day
for t in range(1, 21):
    pi = [pi[0] * (1 - a) + pi[1] * b, pi[0] * a + pi[1] * (1 - b)]
    if t in (1, 2, 5, 20):
        print(f"day {t}: [{f(pi[0])}, {f(pi[1])}]")
''', js=r'''
const f = v => v.toFixed(4);

const a = 0.1;                            // P(sunny -> rainy)
const b = 0.5;                            // P(rainy -> sunny)
console.log(`formula: pi = [b / (a + b), a / (a + b)] = [${f(b / (a + b))}, ${f(a / (a + b))}]`);
let pi = [0, 1];                          // start on a rainy day
for (let t = 1; t <= 20; t++) {
  pi = [pi[0] * (1 - a) + pi[1] * b, pi[0] * a + pi[1] * (1 - b)];
  if ([1, 2, 5, 20].includes(t)) console.log(`day ${t}: [${f(pi[0])}, ${f(pi[1])}]`);
}
''', ts=r'''
const f = (v: number): string => v.toFixed(4);

const a: number = 0.1;                    // P(sunny -> rainy)
const b: number = 0.5;                    // P(rainy -> sunny)
console.log(`formula: pi = [b / (a + b), a / (a + b)] = [${f(b / (a + b))}, ${f(a / (a + b))}]`);
let pi: number[] = [0, 1];                // start on a rainy day
for (let t = 1; t <= 20; t++) {
  pi = [pi[0] * (1 - a) + pi[1] * b, pi[0] * a + pi[1] * (1 - b)];
  if ([1, 2, 5, 20].includes(t)) console.log(`day ${t}: [${f(pi[0])}, ${f(pi[1])}]`);
}
''', java=r'''
public class PracticeTwoState {
    static String f(double v) {
        return String.format("%.4f", v);
    }

    public static void main(String[] args) {
        double a = 0.1;                       // P(sunny -> rainy)
        double b = 0.5;                       // P(rainy -> sunny)
        System.out.println("formula: pi = [b / (a + b), a / (a + b)] = [" + f(b / (a + b)) + ", " + f(a / (a + b)) + "]");
        double[] pi = {0, 1};                 // start on a rainy day
        for (int t = 1; t <= 20; t++) {
            pi = new double[]{pi[0] * (1 - a) + pi[1] * b, pi[0] * a + pi[1] * (1 - b)};
            if (t == 1 || t == 2 || t == 5 || t == 20) System.out.println("day " + t + ": [" + f(pi[0]) + ", " + f(pi[1]) + "]");
        }
    }
}
''')

K.code('p_dice_sim', py=r'''
seed = 2026


def rand():                               # a small repeatable random number maker (Park and Miller)
    global seed
    seed = seed * 16807 % 2147483647
    return seed / 2147483647


def die():
    return int(rand() * 6) + 1            # 1 to 6, each equally likely


hits = 0
for i in range(1, 101):
    if die() + die() >= 10:
        hits += 1
    if i in (10, 50, 100):
        print(f"{i} rolls: estimate {hits / i:.4f}")
print(f"exact: 6 / 36 = {6 / 36:.4f}")
''', js=r'''
let seed = 2026;

function rand() {                         // a small repeatable random number maker (Park and Miller)
  seed = seed * 16807 % 2147483647;
  return seed / 2147483647;
}

const die = () => Math.floor(rand() * 6) + 1;   // 1 to 6, each equally likely

let hits = 0;
for (let i = 1; i <= 100; i++) {
  if (die() + die() >= 10) hits += 1;
  if (i === 10 || i === 50 || i === 100) console.log(`${i} rolls: estimate ${(hits / i).toFixed(4)}`);
}
console.log(`exact: 6 / 36 = ${(6 / 36).toFixed(4)}`);
''', ts=r'''
let seed: number = 2026;

function rand(): number {                 // a small repeatable random number maker (Park and Miller)
  seed = seed * 16807 % 2147483647;
  return seed / 2147483647;
}

const die = (): number => Math.floor(rand() * 6) + 1;   // 1 to 6, each equally likely

let hits = 0;
for (let i = 1; i <= 100; i++) {
  if (die() + die() >= 10) hits += 1;
  if (i === 10 || i === 50 || i === 100) console.log(`${i} rolls: estimate ${(hits / i).toFixed(4)}`);
}
console.log(`exact: 6 / 36 = ${(6 / 36).toFixed(4)}`);
''', java=r'''
public class PracticeDiceSim {
    static long seed = 2026;

    static double rand() {                    // a small repeatable random number maker (Park and Miller)
        seed = seed * 16807 % 2147483647;
        return seed / 2147483647.0;
    }

    static int die() {
        return (int) (rand() * 6) + 1;        // 1 to 6, each equally likely
    }

    public static void main(String[] args) {
        int hits = 0;
        for (int i = 1; i <= 100; i++) {
            if (die() + die() >= 10) hits += 1;
            if (i == 10 || i == 50 || i == 100) System.out.println(i + " rolls: estimate " + String.format("%.4f", (double) hits / i));
        }
        System.out.println("exact: 6 / 36 = " + String.format("%.4f", 6 / 36.0));
    }
}
''')

K.code('p_grid_posterior', py=r'''
def f(v):
    return f"{v:.4f}"


heads, tails = 6, 3
grid = [i / 100 for i in range(101)]      # candidate values of the coin's chance of heads
post = [t ** heads * (1 - t) ** tails for t in grid]   # flat prior times likelihood
z = sum(post)
post = [p / z for p in post]              # make the weights add up to 1
mean = sum(t * p for t, p in zip(grid, post))
best = max(range(101), key=lambda i: post[i])
above = sum(p for t, p in zip(grid, post) if t > 0.5)
print(f"posterior mean = {f(mean)} (exact 7/11 = {f(7 / 11)})")
print(f"MAP = {f(grid[best])} (exact 6/9 = {f(6 / 9)})")
print(f"P(chance of heads > 0.5) = {f(above)}")
''', js=r'''
const f = v => v.toFixed(4);

const heads = 6, tails = 3;
const grid = Array.from({ length: 101 }, (_, i) => i / 100);   // candidate values of the coin's chance of heads
let post = grid.map(t => t ** heads * (1 - t) ** tails);     // flat prior times likelihood
const z = post.reduce((a, b) => a + b, 0);
post = post.map(p => p / z);              // make the weights add up to 1
const mean = grid.reduce((s, t, i) => s + t * post[i], 0);
let best = 0;
for (let i = 1; i <= 100; i++) if (post[i] > post[best]) best = i;
const above = grid.reduce((s, t, i) => s + (t > 0.5 ? post[i] : 0), 0);
console.log(`posterior mean = ${f(mean)} (exact 7/11 = ${f(7 / 11)})`);
console.log(`MAP = ${f(grid[best])} (exact 6/9 = ${f(6 / 9)})`);
console.log(`P(chance of heads > 0.5) = ${f(above)}`);
''', ts=r'''
const f = (v: number): string => v.toFixed(4);

const heads: number = 6, tails: number = 3;
const grid: number[] = Array.from({ length: 101 }, (_, i) => i / 100);   // candidate values of the coin's chance of heads
let post: number[] = grid.map(t => t ** heads * (1 - t) ** tails);     // flat prior times likelihood
const z: number = post.reduce((a, b) => a + b, 0);
post = post.map(p => p / z);              // make the weights add up to 1
const mean: number = grid.reduce((s, t, i) => s + t * post[i], 0);
let best = 0;
for (let i = 1; i <= 100; i++) if (post[i] > post[best]) best = i;
const above: number = grid.reduce((s, t, i) => s + (t > 0.5 ? post[i] : 0), 0);
console.log(`posterior mean = ${f(mean)} (exact 7/11 = ${f(7 / 11)})`);
console.log(`MAP = ${f(grid[best])} (exact 6/9 = ${f(6 / 9)})`);
console.log(`P(chance of heads > 0.5) = ${f(above)}`);
''', java=r'''
public class PracticeGridPosterior {
    static String f(double v) {
        return String.format("%.4f", v);
    }

    public static void main(String[] args) {
        int heads = 6, tails = 3;
        double[] grid = new double[101], post = new double[101];
        double z = 0;
        for (int i = 0; i <= 100; i++) {
            grid[i] = i / 100.0;              // candidate values of the coin's chance of heads
            post[i] = Math.pow(grid[i], heads) * Math.pow(1 - grid[i], tails);   // flat prior times likelihood
            z += post[i];
        }
        double mean = 0, above = 0;
        int best = 0;
        for (int i = 0; i <= 100; i++) {
            post[i] /= z;                     // make the weights add up to 1
            mean += grid[i] * post[i];
            if (post[i] > post[best]) best = i;
            if (grid[i] > 0.5) above += post[i];
        }
        System.out.println("posterior mean = " + f(mean) + " (exact 7/11 = " + f(7 / 11.0) + ")");
        System.out.println("MAP = " + f(grid[best]) + " (exact 6/9 = " + f(6 / 9.0) + ")");
        System.out.println("P(chance of heads > 0.5) = " + f(above));
    }
}
''')

K.code('p_metropolis_beta', py=r'''
seed = 2026


def rand():                               # a small repeatable random number maker (Park and Miller)
    global seed
    seed = seed * 16807 % 2147483647
    return seed / 2147483647


def target(t):                            # posterior shape after 6 heads and 3 tails, flat prior
    if t <= 0 or t >= 1:
        return 0.0
    return t ** 6 * (1 - t) ** 3


t = 0.5
accepted = 0
total = 0.0
count = 0
for i in range(1, 61):
    proposal = t + 0.2 * (2 * rand() - 1)
    if rand() * target(t) < target(proposal):   # same as u < target(proposal) / target(t)
        t = proposal
        accepted += 1
    if i > 10:
        total += t
        count += 1
print(f"acceptance rate = {accepted / 60:.4f}")
print(f"estimated posterior mean = {total / count:.4f}")
print(f"exact posterior mean 7/11 = {7 / 11:.4f}")
''', js=r'''
let seed = 2026;

function rand() {                         // a small repeatable random number maker (Park and Miller)
  seed = seed * 16807 % 2147483647;
  return seed / 2147483647;
}

const target = t => (t <= 0 || t >= 1 ? 0 : t ** 6 * (1 - t) ** 3);   // posterior shape after 6 heads and 3 tails, flat prior

let t = 0.5, accepted = 0, total = 0, count = 0;
for (let i = 1; i <= 60; i++) {
  const proposal = t + 0.2 * (2 * rand() - 1);
  if (rand() * target(t) < target(proposal)) {   // same as u < target(proposal) / target(t)
    t = proposal;
    accepted += 1;
  }
  if (i > 10) {
    total += t;
    count += 1;
  }
}
console.log(`acceptance rate = ${(accepted / 60).toFixed(4)}`);
console.log(`estimated posterior mean = ${(total / count).toFixed(4)}`);
console.log(`exact posterior mean 7/11 = ${(7 / 11).toFixed(4)}`);
''', ts=r'''
let seed: number = 2026;

function rand(): number {                 // a small repeatable random number maker (Park and Miller)
  seed = seed * 16807 % 2147483647;
  return seed / 2147483647;
}

const target = (t: number): number => (t <= 0 || t >= 1 ? 0 : t ** 6 * (1 - t) ** 3);   // posterior shape after 6 heads and 3 tails, flat prior

let t: number = 0.5, accepted = 0, total = 0, count = 0;
for (let i = 1; i <= 60; i++) {
  const proposal: number = t + 0.2 * (2 * rand() - 1);
  if (rand() * target(t) < target(proposal)) {   // same as u < target(proposal) / target(t)
    t = proposal;
    accepted += 1;
  }
  if (i > 10) {
    total += t;
    count += 1;
  }
}
console.log(`acceptance rate = ${(accepted / 60).toFixed(4)}`);
console.log(`estimated posterior mean = ${(total / count).toFixed(4)}`);
console.log(`exact posterior mean 7/11 = ${(7 / 11).toFixed(4)}`);
''', java=r'''
public class PracticeMetropolisBeta {
    static long seed = 2026;

    static double rand() {                    // a small repeatable random number maker (Park and Miller)
        seed = seed * 16807 % 2147483647;
        return seed / 2147483647.0;
    }

    static double target(double t) {          // posterior shape after 6 heads and 3 tails, flat prior
        if (t <= 0 || t >= 1) return 0;
        return Math.pow(t, 6) * Math.pow(1 - t, 3);
    }

    public static void main(String[] args) {
        double t = 0.5, total = 0;
        int accepted = 0, count = 0;
        for (int i = 1; i <= 60; i++) {
            double proposal = t + 0.2 * (2 * rand() - 1);
            if (rand() * target(t) < target(proposal)) {   // same as u < target(proposal) / target(t)
                t = proposal;
                accepted += 1;
            }
            if (i > 10) {
                total += t;
                count += 1;
            }
        }
        System.out.println("acceptance rate = " + String.format("%.4f", accepted / 60.0));
        System.out.println("estimated posterior mean = " + String.format("%.4f", total / count));
        System.out.println("exact posterior mean 7/11 = " + String.format("%.4f", 7 / 11.0));
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('joint', '🧩', 'Joint, marginal and conditional distributions', f'''
<p>Real data has several variables at once: the weather and whether people carry umbrellas, a patient’s age and blood pressure, a pixel and its neighbour. The <b>joint distribution</b> P(X, Y) gives the chance of every combination. From it you can get everything else.</p>
{fxs(fx('Marginal (sum out the other variable)', 'P(X = x) = Σ<sub>y</sub> P(X = x, Y = y)', 'Add across a row of the joint table. The name comes from writing these totals in the margin.'),
         fx('Conditional (zoom into one row or column)', 'P(Y = y | X = x) = ' + frac('P(X = x, Y = y)', 'P(X = x)'), 'Keep only the cases where X = x, then rescale so they add to 1.'),
         fx('Independence', 'P(X, Y) = P(X) P(Y) for every cell', 'Knowing X tells you nothing about Y. Then P(Y | X) = P(Y).'))}
{viz('jointgrid')}
{worked('100 days of weather and umbrellas', [
        'Counts: sunny (40 no, 5 yes), cloudy (20 no, 10 yes), rainy (5 no, 20 yes)',
        'Joint: <span class="eq">P(rainy, umbrella) = 20 ÷ 100 = 0.20</span>',
        'Marginals: <span class="eq">P(rainy) = 25 ÷ 100 = 0.25</span>, <span class="eq">P(umbrella) = 35 ÷ 100 = 0.35</span>',
        'Conditional: <span class="eq">P(umbrella | rainy) = 0.20 ÷ 0.25 = 0.80</span>',
        'Independence test: <span class="eq">0.25 × 0.35 = 0.0875 ≠ 0.20</span>, so rain and umbrellas are dependent, as you would expect.'])}
{code('joint_table', 'Marginals, conditionals and an independence check from a table of counts')}
{deep('the chain rule of probability and why it matters', f"""
<p>Rearranging the conditional formula gives the <b>product rule</b>: P(X, Y) = P(X) P(Y | X). Repeating it gives the <b>chain rule of probability</b>: P(x₁, x₂, …, xₙ) = P(x₁) P(x₂ | x₁) P(x₃ | x₁, x₂) ⋯ P(xₙ | x₁, …, xₙ₋₁).</p>
<p>This is exactly how a large language model scores a sentence. It predicts the first word, then the second word given the first, then the third given the first two, and multiplies (in practice, adds the logs of) all those conditional probabilities. Naive Bayes (Chapter 9) is the same chain rule with a bold simplification: it pretends the features are independent once the class is known.</p>
<p>For continuous variables, sums become integrals: p(x) = ∫ p(x, y) dy. The ideas do not change.</p>""")}
{ml('Generative models learn a joint distribution, for example p(image, label) or p(all the words of a text). Discriminative models such as logistic regression learn only the conditional p(label | image). Marginalising, summing out what you do not know, is at the heart of Bayesian inference and of mixture models.')}
''', kw=['joint distribution', 'marginal distribution', 'conditional distribution', 'independence', 'product rule', 'chain rule of probability', 'contingency table']),

    part('mvn', '🥚', 'The multivariate normal and Mahalanobis distance', f'''
<p>The bell curve of Chapter 10 has a version for many variables at once, the <b>multivariate normal</b>. It is described by a mean vector μ (the centre) and a covariance matrix Σ (the spread of each variable and how pairs move together). Its contour lines, the points of equal density, are ellipses. The covariance matrix decides their shape and tilt, and its eigenvectors (Chapter 5) point along the axes of the ellipses.</p>
{fx('Density of a d dimensional normal', 'p(x) = ' + frac('1', '(2π)<sup>d/2</sup> |Σ|<sup>1/2</sup>') + ' exp(−½ (x − μ)ᵀ Σ⁻¹ (x − μ))', 'The part inside exp is minus half the squared Mahalanobis distance. |Σ| is the determinant.')}
{fx('Mahalanobis distance', 'd<sub>M</sub>(x) = √((x − μ)ᵀ Σ⁻¹ (x − μ))', 'Distance measured in standard deviations, taking the shape of the data into account. With Σ = I it is the ordinary distance.')}
{viz('mvnorm')}
{worked('Two points the same distance from the centre', [
        'Σ = <span class="eq">[[4, 2], [2, 3]]</span>, μ = 0. So <span class="eq">det Σ = 8</span> and <span class="eq">Σ⁻¹ = [[3, −2], [−2, 4]] ÷ 8</span>',
        'a = [2, 2]: <span class="eq">(3·4 − 2·2·2·2 + 4·4) ÷ 8 = 12 ÷ 8 = 1.5</span>, so <span class="eq">d<sub>M</sub> = 1.22</span>',
        'b = [2, −2]: <span class="eq">(12 + 16 + 16) ÷ 8 = 5.5</span>, so <span class="eq">d<sub>M</sub> = 2.35</span>',
        'Both are <span class="eq">2.83</span> away in ordinary distance. But x and y usually rise together here, so b, which goes against that pattern, is much more unusual.'])}
{code('mahalanobis', 'Mahalanobis distance and drawing a sample with Cholesky')}
{deep('three facts that make the normal so useful', f"""
<p><b>Linear maps keep it normal.</b> If x ~ N(μ, Σ) then Ax + b ~ N(Aμ + b, AΣAᵀ). That is how samples are drawn: take independent standard normal z and form μ + Lz with LLᵀ = Σ (Cholesky, Chapter 13).</p>
<p><b>Marginals and conditionals stay normal.</b> Any subset of the variables is normal, and so is any subset given the rest. The conditional mean is a straight line in the known values, which is one more reason linear regression is so natural.</p>
<p><b>Zero correlation means independence,</b> but only for jointly normal variables. In general, uncorrelated variables can still depend on each other strongly, for example x and x² when x is symmetric around 0.</p>""")}
{ml('Gaussian discriminant analysis fits one multivariate normal per class. Anomaly detection flags points with a large Mahalanobis distance. Gaussian processes, Kalman filters and the noise in diffusion models are all built on the multivariate normal. The "reparameterisation trick" of variational autoencoders is exactly μ + σz.')}
''', kw=['multivariate normal', 'gaussian', 'covariance matrix', 'mahalanobis distance', 'ellipse', 'cholesky sampling', 'anomaly detection']),

    part('bayes', '🪙', 'Bayesian inference: priors, posteriors and MAP', f'''
<p>Chapter 9 used Bayes’ rule for events. Bayesian inference uses it for an unknown <b>parameter</b>, such as the chance θ that a coin lands heads. Instead of one best guess, you keep a whole distribution of belief over θ and update it with data.</p>
{fx('Bayes’ rule for a parameter', 'p(θ | data) = ' + frac('p(data | θ) · p(θ)', 'p(data)') + ' &nbsp; ∝ &nbsp; likelihood × prior', 'Prior: belief before the data. Likelihood: how well each θ explains the data. Posterior: updated belief. p(data) only rescales.')}
<p>For a coin, a very convenient prior is the <b>Beta distribution</b>, Beta(a, b), whose density is proportional to θ<sup>a − 1</sup>(1 − θ)<sup>b − 1</sup>. You can read a and b as "imaginary heads plus 1" and "imaginary tails plus 1". When the data are h heads and t tails, the posterior is again a Beta. A prior with this property is called <b>conjugate</b>.</p>
{fx('Beta Binomial update', 'Beta(a, b) prior + h heads, t tails → Beta(a + h, b + t) posterior', 'Updating is just counting. The posterior mean is (a + h) ÷ (a + b + h + t).')}
{viz('betaprior')}
{table(['Estimate', 'Rule', 'Beta(2, 2) prior, 7 heads in 10'], [
        ['MLE (maximum likelihood)', 'the θ that makes the data most likely: h ÷ n', '0.700'],
        ['MAP (maximum a posteriori)', 'the peak of the posterior: (a + h − 1) ÷ (a + b + n − 2)', '8 ÷ 12 = 0.667'],
        ['posterior mean', '(a + h) ÷ (a + b + n)', '9 ÷ 14 = 0.643'],
    ])}
{code('beta_update', 'Updating a Beta prior one coin flip at a time')}
{deep('MAP is regularisation in disguise', f"""
<p>Take logs: ln posterior = ln likelihood + ln prior + constant. Maximising the posterior (MAP) is therefore maximising the log likelihood plus a bonus from the prior.</p>
<p>Now put a normal prior on each weight of a model, w ~ N(0, σ²). Its log is −w² ÷ (2σ²) + constant. So MAP with a normal prior is exactly maximum likelihood with an L2 penalty, which is ridge regression or weight decay (Chapter 12). A Laplace prior, proportional to e<sup>−|w| ÷ b</sup>, gives the L1 penalty of lasso. A stronger belief that weights are small (smaller σ) means a stronger penalty.</p>
<p>With lots of data the likelihood dominates and MLE, MAP and the posterior mean all agree. With little data the prior matters, which is when it helps the most.</p>""")}
{ml('Bayesian ideas appear in A/B testing ("the chance B beats A is 94 %"), in spam filters, in Thompson sampling for recommendation systems, and in Bayesian optimisation for tuning hyperparameters. Bayesian neural networks keep a distribution over weights to say how unsure a prediction is.')}
{life('A new restaurant with one 5 star review is not really better than one with 4.6 stars from 2000 reviews. Sensible ranking systems add a prior, some imaginary average reviews, so that a handful of ratings cannot jump to the top.')}
''', kw=['bayesian inference', 'prior', 'likelihood', 'posterior', 'beta distribution', 'conjugate prior', 'map estimate', 'mle', 'credible interval', 'regularisation as prior']),

    part('markov', '🔁', 'Markov chains and stationary distributions', f'''
<p>A <b>Markov chain</b> moves between states at random, and the chance of the next state depends only on the current one, not on the history. Weather from day to day, a shopper moving between web pages and the next word in a very simple text model are common examples.</p>
{fxs(fx('Transition matrix', 'Pᵢⱼ = P(next = j | now = i), each row adds up to 1', 'Row i lists where you can go from state i.'),
         fx('One step for a whole distribution', 'π<sub>t+1</sub> = π<sub>t</sub> P', 'A row vector of probabilities times the matrix.'),
         fx('Stationary distribution', 'π = π P', 'Once reached, the distribution never changes. It is a left eigenvector of P with eigenvalue 1 (Chapter 5).'))}
{viz('markov')}
{worked('Will tomorrow be sunny, two days ahead', [
        'Today is sunny: <span class="eq">π₀ = [1, 0, 0]</span> (sunny, cloudy, rainy)',
        'Day 1 is the first row of P: <span class="eq">[0.7, 0.2, 0.1]</span>',
        'Day 2: <span class="eq">0.7 × [0.7, 0.2, 0.1] + 0.2 × [0.3, 0.4, 0.3] + 0.1 × [0.2, 0.3, 0.5] = [0.57, 0.25, 0.18]</span>',
        'Keep going and it settles at the stationary distribution, about <span class="eq">[0.46, 0.28, 0.26]</span>, whatever the weather was today.'])}
{code('markov_chain', 'Pushing a distribution through a weather chain until it settles')}
<p>A chain settles to one stationary distribution from any start when it is <b>irreducible</b> (every state can reach every other) and <b>aperiodic</b> (it does not cycle on a fixed rhythm). The "cycle" example in the animation fails the second condition and never settles.</p>
{ml('Google’s original PageRank is the stationary distribution of a random surfer who follows links, with a small chance of jumping to a random page so the chain is irreducible. Reinforcement learning is built on Markov decision processes, which are Markov chains with actions and rewards. MCMC, two lessons ahead, designs a chain whose stationary distribution is the distribution you want to sample.')}
''', kw=['markov chain', 'transition matrix', 'stationary distribution', 'steady state', 'pagerank', 'irreducible', 'aperiodic', 'markov property']),

    part('montecarlo', '🎲', 'Monte Carlo and inverse transform sampling', f'''
<p><b>Monte Carlo</b> methods answer questions by simulation. To find an average, a probability or an integral, draw many random samples and average the results. The law of large numbers makes the answer converge, and the central limit theorem (Chapter 11) says how fast.</p>
{fxs(fx('Monte Carlo estimate', 'E[f(X)] ≈ ' + frac('1', 'n') + ' Σ f(xᵢ), with xᵢ drawn from X', 'An integral ∫₀¹ f(x) dx is E[f(U)] for a uniform U.'),
         fx('Its error', 'standard error = σ ÷ √n', 'Four times as many samples halve the error. This holds in any number of dimensions, which is why Monte Carlo wins in high dimensions.'))}
{code('monte_carlo_int', 'Estimating the integral of eˣ from 0 to 1 by averaging')}
<p>Every simulation needs random numbers from the right distribution, but a computer only produces uniform numbers between 0 and 1. <b>Inverse transform sampling</b> converts them. If F is the CDF of the distribution you want, draw u uniformly and return x = F⁻¹(u). Values of x where F climbs steeply catch more of the u values, so they come out more often, exactly as they should.</p>
{fx('Inverse transform', 'x = F⁻¹(u), u ~ Uniform(0, 1)', 'Exponential with rate λ: F(x) = 1 − e<sup>−λx</sup>, so x = −ln(1 − u) ÷ λ.')}
{viz('invsample')}
{code('inverse_transform', 'Exponential waiting times from uniform numbers')}
{deep('when the inverse is not available', f"""
<p>For the normal distribution F⁻¹ has no simple formula. The <b>Box Muller</b> method turns two uniforms into two independent standard normals: √(−2 ln u₁) cos(2π u₂) and √(−2 ln u₁) sin(2π u₂).</p>
<p><b>Rejection sampling</b> works for any density p you can evaluate. Choose an easy proposal q and a constant M with p ≤ M q everywhere. Draw x from q and keep it with probability p(x) ÷ (M q(x)). Kept points follow p exactly, but in high dimensions almost every point gets rejected.</p>
<p><b>Importance sampling</b> keeps every point from q and gives it a weight p(x) ÷ q(x) instead. It is used in reinforcement learning to reuse old experience collected by an older policy.</p>""")}
{ml('Dropout at test time with many forward passes ("Monte Carlo dropout") estimates how unsure a network is. Policy gradient methods in reinforcement learning estimate gradients by averaging over sampled episodes. Diffusion models and VAEs sample noise with the methods of this lesson millions of times during training.')}
''', kw=['monte carlo', 'simulation', 'law of large numbers', 'standard error', 'inverse transform sampling', 'box muller', 'rejection sampling', 'importance sampling']),

    part('mcmc', '⛓️', 'MCMC and the Metropolis algorithm', f'''
<p>Bayesian posteriors are often known only up to a constant: we can compute likelihood × prior, but not p(data), which needs an impossible integral. <b>Markov chain Monte Carlo</b> (MCMC) still produces samples. It builds a Markov chain that wanders through the parameter space and spends time in each region in proportion to its probability. The constant cancels out, so it is never needed.</p>
<ol>
<li>Start somewhere, at x.</li>
<li><b>Propose</b> a random nearby point x′, for example x plus a small random step.</li>
<li>Compute the ratio r = p(x′) ÷ p(x). The unknown constant cancels in this ratio.</li>
<li><b>Accept</b> with probability min(1, r): always move uphill, sometimes move downhill. Otherwise stay at x (and count x again).</li>
<li>Repeat many times, throw away the early "burn in" steps, and treat the rest as samples.</li>
</ol>
{viz('metropolis')}
{worked('One Metropolis step for a standard normal target', [
        'Current point <span class="eq">x = 1</span>, proposal <span class="eq">x′ = 2</span>',
        'Ratio: <span class="eq">r = e<sup>−4/2</sup> ÷ e<sup>−1/2</sup> = e<sup>−1.5</sup> = 0.223</span>',
        'Draw u. If <span class="eq">u &lt; 0.223</span>, move to 2. Otherwise stay at 1 and record 1 again.',
        'A move towards 0 (uphill) would always be accepted.'])}
{code('metropolis', 'Metropolis sampling from a bell curve, starting far away')}
{table(['Step size', 'What happens', 'Fix'], [
        ['too small', 'almost every move is accepted, but the chain creeps and samples are strongly correlated', 'larger steps'],
        ['too large', 'most proposals land in low probability areas and are rejected, so the chain sits still', 'smaller steps'],
        ['about right', 'acceptance roughly 25 % to 50 %, and the chain explores well', 'tune during burn in'],
    ])}
{ml('Probabilistic programming tools such as Stan and PyMC fit Bayesian models with an advanced MCMC method called Hamiltonian Monte Carlo, which uses gradients (from autodiff, Chapter 14) to make long, well aimed proposals. Simulated annealing, Gibbs sampling in topic models and energy based models are close relatives of Metropolis.')}
{trick('Metropolis in five words: propose, compare, accept or stay.')}
''', kw=['mcmc', 'markov chain monte carlo', 'metropolis', 'metropolis hastings', 'burn in', 'acceptance rate', 'proposal', 'hamiltonian monte carlo', 'posterior sampling']),

    part('concentration', '📏', 'Concentration inequalities and the law of large numbers', f'''
<p>The law of large numbers says that the average of many independent samples gets close to the true mean. Concentration inequalities say <b>how close</b>, with a guarantee rather than an approximation. They are the mathematics behind "how much data is enough" and behind the theory of why machine learning generalises.</p>
{table(['Inequality', 'Statement', 'Needs'], [
        ['Markov', 'P(X ≥ a) ≤ E[X] ÷ a', 'X never negative'],
        ['Chebyshev', 'P(|X − μ| ≥ kσ) ≤ 1 ÷ k²', 'a finite variance'],
        ['Chebyshev for an average', 'P(|x̄ − μ| ≥ ε) ≤ σ² ÷ (n ε²)', 'independent samples'],
        ['Hoeffding', 'P(|x̄ − μ| ≥ ε) ≤ 2 e<sup>−2nε²</sup>', 'independent samples between 0 and 1'],
    ])}
{viz('lln')}
{worked('How many coin flips for the share of heads to be within 0.05 of the truth, with 95 % confidence', [
        'Hoeffding: we need <span class="eq">2 e<sup>−2n(0.05)²</sup> ≤ 0.05</span>',
        'So <span class="eq">e<sup>−0.005n</sup> ≤ 0.025</span>, giving <span class="eq">n ≥ ln 40 ÷ 0.005 ≈ 738</span>',
        'Chebyshev with σ² ≤ 0.25 asks for <span class="eq">0.25 ÷ (n × 0.0025) ≤ 0.05</span>, so <span class="eq">n ≥ 2000</span>',
        'The normal approximation of Chapter 11 says about <span class="eq">385</span>. The bounds cost more samples because they are guarantees.'])}
{code('concentration', 'Exact chance of a big miss compared with two guarantees')}
{deep('why this explains learning', f"""
<p>A model’s error on the training set is an average over n examples. Its error on new data is the true mean. Hoeffding says that for one fixed model these are within ε of each other with probability at least 1 − 2e<sup>−2nε²</sup>.</p>
<p>Training picks one model out of many, so the bound has to hold for all of them at once. With k possible models, adding up the failure chances (the union bound) gives probability at most 2k e<sup>−2nε²</sup>. Solving for n shows that the data needed grows with ln k, the logarithm of the number of models. This is the core of PAC learning ("probably approximately correct"), and it is why a richer model family needs more data to avoid overfitting.</p>""")}
{ml('Concentration bounds decide how many users an A/B test needs, how many samples a Monte Carlo estimate needs, and how many rollouts a reinforcement learning agent needs. The ε greedy and UCB rules for multi armed bandits are built directly on Hoeffding’s inequality.')}
''', kw=['law of large numbers', 'concentration inequality', 'markov inequality', 'chebyshev inequality', 'hoeffding inequality', 'union bound', 'pac learning', 'sample size']),
]

INFO = {
    'title': 'Believe, update, sample',
    'panels': [
        {'s': [['e', '🧩'], ['t', 'P(Y | X)', {'b': 1}]], 'h': 'Joint tables', 't': 'Sum out, or zoom in.', 'more': 'Marginals and conditionals.'},
        {'s': [['e', '🪙'], ['t', 'Beta(a + h, b + t)', {'b': 1}]], 'h': 'Bayes', 't': 'Prior × likelihood.', 'more': 'MAP is regularisation.'},
        {'s': [['e', '🔁'], ['t', 'π = πP', {'b': 1}]], 'h': 'Markov chains', 't': 'Settle to a steady state.', 'more': 'PageRank.'},
        {'s': [['e', '⛓️'], ['t', 'accept min(1, r)', {'b': 1}]], 'h': 'MCMC', 't': 'Sample without the constant.', 'more': 'Propose, compare, accept.'},
    ],
    'remember': 'A joint table gives marginals by summing and conditionals by dividing, and independence means every cell is a product of marginals. The multivariate normal has elliptical contours set by Σ, and Mahalanobis distance measures distance in standard deviations. Bayesian inference multiplies prior by likelihood, and with a Beta prior a coin’s posterior is Beta(a + h, b + t). MAP with a normal prior is L2 regularisation. A Markov chain settles to π = πP. Monte Carlo errors shrink like 1 ÷ √n, inverse transform turns uniforms into any distribution, Metropolis samples a posterior without its constant, and Hoeffding guarantees how close an average is.',
}

REAL = [
    ['🔎', 'Search engines', 'PageRank treated the web as a Markov chain and ranked pages by the stationary distribution of a random surfer.'],
    ['💊', 'Medical studies', 'Bayesian trials update the chance that a treatment works as each patient’s result arrives, and can stop early when the evidence is clear.'],
    ['🌍', 'Climate and finance', 'Monte Carlo simulation runs thousands of possible futures to estimate risks that have no simple formula.'],
]

K.say('top', 'Welcome',
      'This chapter is about uncertainty done properly. You will read joint, marginal and conditional distributions from a table, meet the multivariate normal and the Mahalanobis distance, update beliefs with Bayes and conjugate priors, watch Markov chains settle, estimate with Monte Carlo, sample with the Metropolis algorithm, and see how concentration inequalities guarantee how close an average is.',
      'यह अध्याय अनिश्चितता के बारे में है। Joint, marginal और conditional distributions, multivariate normal और Mahalanobis distance, Bayes और conjugate priors, Markov chains, Monte Carlo, Metropolis और concentration inequalities सीखेंगे।',
      'ಈ ಅಧ್ಯಾಯ ಅನಿಶ್ಚಿತತೆಯ ಬಗ್ಗೆ. Joint distributions, multivariate normal, Bayes, Markov chains, Monte Carlo, Metropolis ಮತ್ತು concentration inequalities ಕಲಿಯುತ್ತೀರಿ.',
      'ଏହି ଅଧ୍ୟାୟ ଅନିଶ୍ଚିତତା ବିଷୟରେ। Joint distributions, multivariate normal, Bayes, Markov chains, Monte Carlo, Metropolis ଓ concentration inequalities ଶିଖିବେ।',
      'هذا الفصل عن التعامل الصحيح مع عدم اليقين. ستقرأ التوزيعات المشتركة والهامشية والشرطية من جدول، وتتعرف على التوزيع الطبيعي متعدد المتغيرات ومسافة ماهالانوبيس، وتحدث معتقداتك ببايز، وترى سلاسل ماركوف تستقر، وتقدر بمونت كارلو، وتأخذ عينات بخوارزمية متروبوليس.',
      'In diesem Kapitel geht es um Unsicherheit. Du liest gemeinsame, Rand und bedingte Verteilungen aus einer Tabelle, lernst die mehrdimensionale Normalverteilung und die Mahalanobis Distanz kennen, aktualisierst Überzeugungen mit Bayes, siehst Markovketten sich einpendeln, schätzt mit Monte Carlo und ziehst Stichproben mit dem Metropolis Algorithmus.')
K.say('joint', 'Joint distributions',
      'The joint distribution gives the chance of every combination of values. Add across a row to get a marginal. Divide a cell by its row total to get a conditional. Two variables are independent when every cell equals the product of its two marginals.',
      'Joint distribution हर संयोजन की संभावना देता है। Row को जोड़ने से marginal मिलता है। Cell को row के योग से भाग देने पर conditional मिलता है।',
      'Joint distribution ಪ್ರತಿ ಸಂಯೋಜನೆಯ ಸಂಭವನೀಯತೆ. Row ಕೂಡಿಸಿದರೆ marginal, ಭಾಗಿಸಿದರೆ conditional.',
      'Joint distribution ପ୍ରତି ସଂଯୋଜନର ସମ୍ଭାବନା। Row ଯୋଡ଼ିଲେ marginal, ଭାଗ କଲେ conditional।',
      'التوزيع المشترك يعطي احتمال كل تركيبة من القيم. اجمع الصف لتحصل على الهامشي، واقسم الخلية على مجموع صفها لتحصل على الشرطي.',
      'Die gemeinsame Verteilung gibt die Wahrscheinlichkeit jeder Kombination an. Addiere eine Zeile für die Randverteilung. Teile eine Zelle durch ihre Zeilensumme für die bedingte Verteilung.')
K.say('mvn', 'Multivariate normal',
      'The multivariate normal has a mean vector and a covariance matrix. Its contours are ellipses whose shape comes from the covariance. The Mahalanobis distance measures how far a point is in standard deviations, taking that shape into account.',
      'Multivariate normal का एक mean vector और एक covariance matrix होता है। इसकी contours ellipses हैं। Mahalanobis distance दूरी को standard deviations में मापता है।',
      'Multivariate normal ಗೆ mean vector ಮತ್ತು covariance matrix. Contours ellipses. Mahalanobis distance standard deviations ನಲ್ಲಿ ದೂರ.',
      'Multivariate normal ର mean vector ଓ covariance matrix। Contours ellipses। Mahalanobis distance standard deviations ରେ ଦୂରତା।',
      'للتوزيع الطبيعي متعدد المتغيرات متجه متوسط ومصفوفة تغاير، وخطوط تساويه قطوع ناقصة. مسافة ماهالانوبيس تقيس البعد بوحدات الانحراف المعياري مع مراعاة الشكل.',
      'Die mehrdimensionale Normalverteilung hat einen Mittelwertvektor und eine Kovarianzmatrix. Ihre Höhenlinien sind Ellipsen. Die Mahalanobis Distanz misst den Abstand in Standardabweichungen.')
K.say('bayes', 'Bayesian inference',
      'Bayesian inference multiplies a prior belief by the likelihood of the data to get the posterior. For a coin, a Beta prior updated with h heads and t tails becomes another Beta, so updating is just counting. The peak of the posterior, the MAP estimate, is regularised maximum likelihood.',
      'Bayesian inference prior को likelihood से गुणा करके posterior देता है। Coin के लिए Beta prior, heads और tails गिनकर नया Beta बनता है।',
      'Prior ಗುಣಿಸು likelihood ಸಮ posterior. Beta prior ಗೆ heads ಮತ್ತು tails ಸೇರಿಸಿದರೆ ಹೊಸ Beta.',
      'Prior ଗୁଣନ likelihood ସମାନ posterior। Beta prior ରେ heads ଓ tails ଯୋଡ଼ିଲେ ନୂଆ Beta।',
      'الاستدلال البايزي يضرب الاعتقاد المسبق في احتمال البيانات ليعطي اللاحق. ومع توزيع بيتا المسبق للعملة يصبح التحديث مجرد عد للوجوه والظهور.',
      'Bayessche Inferenz multipliziert die Priori mit der Likelihood und erhält die Posteriori. Bei einer Münze mit Beta Priori ist das Aktualisieren nur Zählen.')
K.say('markov', 'Markov chains',
      'A Markov chain moves between states, and the next step depends only on the current state. Multiplying the distribution by the transition matrix moves it one step. A well behaved chain settles to a stationary distribution, whatever the start.',
      'Markov chain में अगला कदम केवल वर्तमान state पर निर्भर करता है। Distribution को transition matrix से गुणा करने पर एक कदम आगे जाता है।',
      'Markov chain ನಲ್ಲಿ ಮುಂದಿನ ಹೆಜ್ಜೆ ಈಗಿನ state ಮೇಲೆ ಮಾತ್ರ. ಕೊನೆಗೆ stationary distribution.',
      'Markov chain ରେ ପରବର୍ତ୍ତୀ ପଦ କେବଳ ବର୍ତ୍ତମାନ state ଉପରେ। ଶେଷରେ stationary distribution।',
      'في سلسلة ماركوف تعتمد الخطوة التالية على الحالة الحالية فقط. ضرب التوزيع في مصفوفة الانتقال يقدمه خطوة، والسلسلة الجيدة تستقر على توزيع ثابت.',
      'In einer Markovkette hängt der nächste Schritt nur vom aktuellen Zustand ab. Eine gutartige Kette pendelt sich auf eine stationäre Verteilung ein.')
K.say('montecarlo', 'Monte Carlo',
      'Monte Carlo methods estimate averages and integrals by simulation, with an error that shrinks like one over the square root of n. Inverse transform sampling turns uniform random numbers into any distribution by applying the inverse of its CDF.',
      'Monte Carlo simulation से औसत और integral का अनुमान लगाता है। Inverse transform sampling uniform numbers को किसी भी distribution में बदलता है।',
      'Monte Carlo simulation ಮೂಲಕ ಅಂದಾಜು. Inverse transform uniform ಸಂಖ್ಯೆಗಳನ್ನು ಯಾವುದೇ distribution ಗೆ ಬದಲಿಸುತ್ತದೆ.',
      'Monte Carlo simulation ଦ୍ୱାରା ଆକଳନ। Inverse transform uniform ସଂଖ୍ୟାକୁ ଯେକୌଣସି distribution କୁ ବଦଳାଏ।',
      'طرق مونت كارلو تقدر المتوسطات والتكاملات بالمحاكاة، ويقل خطؤها مثل واحد على جذر n. وأخذ العينات بالتحويل العكسي يحول الأعداد المنتظمة إلى أي توزيع.',
      'Monte Carlo Methoden schätzen Mittelwerte und Integrale durch Simulation. Die Inversionsmethode verwandelt gleichverteilte Zahlen in jede gewünschte Verteilung.')
K.say('mcmc', 'MCMC and Metropolis',
      'Metropolis samples a distribution known only up to a constant. Propose a nearby point, compare the two probabilities, and accept the move with probability equal to their ratio, capped at one. Throw away the burn in and keep the rest.',
      'Metropolis एक पास का बिंदु सुझाता है, दोनों probabilities की तुलना करता है और अनुपात की संभावना से move स्वीकार करता है।',
      'Metropolis: ಹತ್ತಿರದ ಬಿಂದು ಸೂಚಿಸಿ, ಹೋಲಿಸಿ, ಅನುಪಾತದ ಸಂಭವನೀಯತೆಯಿಂದ ಒಪ್ಪಿಕೊಳ್ಳಿ.',
      'Metropolis: ପାଖ ବିନ୍ଦୁ ପ୍ରସ୍ତାବ, ତୁଳନା, ଅନୁପାତ ସମ୍ଭାବନାରେ ଗ୍ରହଣ।',
      'خوارزمية متروبوليس تقترح نقطة قريبة وتقارن الاحتمالين وتقبل الانتقال باحتمال يساوي النسبة بحد أقصى واحد.',
      'Metropolis schlägt einen nahen Punkt vor, vergleicht die Wahrscheinlichkeiten und nimmt den Schritt mit der Wahrscheinlichkeit ihres Verhältnisses an.')
K.say('concentration', 'Concentration inequalities',
      'Markov, Chebyshev and Hoeffding inequalities guarantee how unlikely a big miss is. Hoeffding says the chance that an average of n samples misses by more than epsilon falls exponentially with n. This is the maths behind sample sizes and why models generalise.',
      'Chebyshev और Hoeffding बताते हैं कि बड़ी गलती कितनी असंभावित है। Hoeffding के अनुसार यह संभावना n के साथ तेज़ी से घटती है।',
      'Chebyshev ಮತ್ತು Hoeffding ದೊಡ್ಡ ತಪ್ಪಿನ ಸಂಭವನೀಯತೆಗೆ ಮಿತಿ ನೀಡುತ್ತವೆ.',
      'Chebyshev ଓ Hoeffding ବଡ଼ ଭୁଲର ସମ୍ଭାବନାକୁ ସୀମିତ କରନ୍ତି।',
      'متباينات ماركوف وتشيبيشيف وهوفدينغ تضمن مدى ندرة الخطأ الكبير، وتقول هوفدينغ إن هذا الاحتمال يتناقص أسيًا مع عدد العينات.',
      'Die Ungleichungen von Markov, Tschebyschow und Hoeffding garantieren, wie unwahrscheinlich ein großer Fehler ist. Bei Hoeffding fällt diese Wahrscheinlichkeit exponentiell mit n.')
K.say('practice', 'Practice',
      'Now practise: find the steady state of a two state weather chain, estimate a dice probability by simulation, build a grid approximation of a posterior, and sample that posterior with Metropolis.',
      'अब अभ्यास: दो state वाली chain का steady state, simulation से dice की संभावना, grid से posterior, और Metropolis से उसी posterior के samples।',
      'ಅಭ್ಯಾಸ: steady state, dice simulation, grid posterior, Metropolis.',
      'ଅଭ୍ୟାସ: steady state, dice simulation, grid posterior, Metropolis।',
      'تدرب الآن: أوجد الحالة المستقرة لسلسلة بحالتين، وقدر احتمال نرد بالمحاكاة، وابن تقريبًا شبكيًا للاحق، وخذ منه عينات بمتروبوليس.',
      'Jetzt üben: finde den stationären Zustand einer Kette mit zwei Zuständen, schätze eine Würfelwahrscheinlichkeit durch Simulation, nähere eine Posteriori auf einem Gitter an und ziehe Stichproben mit Metropolis.')

# ---------------------------------------------------------------- practice
K.practice('two-state', 'e', 'The steady state of a two state chain', 'p_two_state',
           '<p>A sunny day is followed by rain with chance a = 0.1. A rainy day is followed by sun with chance b = 0.5. Find the long run share of sunny days with the formula, then check it by iterating from a rainy day.</p>',
           'formula: pi = [b / (a + b), a / (a + b)] = [0.8333, 0.1667]\nday 1: [0.5000, 0.5000]\nday 2: [0.7000, 0.3000]\nday 5: [0.8248, 0.1752]\nday 20: [0.8333, 0.1667]',
           'In the steady state the flow from sunny to rainy equals the flow back: π<sub>sunny</sub> a = π<sub>rainy</sub> b.',
           '<p>From π<sub>s</sub> a = π<sub>r</sub> b and π<sub>s</sub> + π<sub>r</sub> = 1 you get π<sub>s</sub> = b ÷ (a + b) = 0.5 ÷ 0.6 = 0.8333. Iterating π ← πP from [0, 1] closes the gap by a factor 1 − a − b = 0.4 each day, so after 20 days it matches to 4 decimals.</p>',
           'O(steps)', 'O(1)')
K.practice('dice-sim', 'm', 'Estimate a dice probability by simulation', 'p_dice_sim',
           '<p>Roll two dice 100 times with a repeatable random number maker and estimate P(sum ≥ 10). Compare with the exact answer.</p>',
           '10 rolls: estimate 0.0000\n50 rolls: estimate 0.1000\n100 rolls: estimate 0.1300\nexact: 6 / 36 = 0.1667',
           'Turn a uniform u into a die with ⌊6u⌋ + 1.',
           '<p>The sums 10, 11 and 12 come from 3 + 2 + 1 = 6 of the 36 equally likely pairs, so the exact answer is 1/6 ≈ 0.1667. The estimate wobbles a lot: 0 after 10 rolls, 0.13 after 100. The standard error √(p(1 − p) ÷ n) is about 0.037 at n = 100, so a miss of 0.037 is normal. To get within 0.01 reliably you would need several thousand rolls.</p>',
           'O(n)', 'O(1)')
K.practice('grid-posterior', 'h', 'A posterior on a grid', 'p_grid_posterior',
           '<p>A coin gives 6 heads and 3 tails. With a flat prior, evaluate the posterior on the grid θ = 0, 0.01, …, 1, normalise it, and report the posterior mean, the MAP and P(θ &gt; 0.5).</p>',
           'posterior mean = 0.6364 (exact 7/11 = 0.6364)\nMAP = 0.6700 (exact 6/9 = 0.6667)\nP(chance of heads > 0.5) = 0.8198',
           'Posterior ∝ θ⁶(1 − θ)³ at each grid point. Divide by the total to make the weights sum to 1.',
           '<p>A grid approximation works for one or two parameters and needs no clever maths: evaluate prior × likelihood everywhere, normalise, and read off any summary. The exact posterior is Beta(7, 4), with mean 7 ÷ 11 ≈ 0.6364 and peak 6 ÷ 9 ≈ 0.6667, and the grid lands on these to about two decimals. With 10 parameters the grid would need 101¹⁰ points, which is why MCMC exists.</p>',
           'O(grid size)', 'O(grid size)')
K.practice('mh-beta', 'x', 'Metropolis on a coin posterior', 'p_metropolis_beta',
           '<p>Sample the same posterior, proportional to θ⁶(1 − θ)³ on (0, 1), with Metropolis: step size 0.2, 60 steps, start at 0.5, burn in 10. Estimate the posterior mean and compare with 7/11.</p>',
           'acceptance rate = 0.6500\nestimated posterior mean = 0.6827\nexact posterior mean 7/11 = 0.6364',
           'Proposals outside (0, 1) have target 0, so they are always rejected.',
           '<p>Writing the test as u × target(θ) &lt; target(θ′) avoids dividing by zero and is the same rule. The chain never needs the normalising constant, the Beta function B(7, 4). With only 50 kept steps the estimate of 0.683 is off by about 0.05. That is Monte Carlo noise, made larger because neighbouring samples of a chain are correlated. Real runs keep thousands of steps, and the error shrinks like 1 ÷ √n.</p>',
           'O(steps)', 'O(1)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'How do you get the marginal P(X = x) from a joint table?', ['multiply the row', 'add up the row for x', 'take the largest cell', 'divide by the column'], 1, 'Sum out the other variable.', 'P(X = x) = Σ<sub>y</sub> P(x, y).')
K.quiz('e', 'X and Y are independent exactly when…', ['P(X, Y) = P(X) + P(Y)', 'P(X, Y) = P(X) P(Y)', 'P(X | Y) = P(Y)', 'X = Y'], 1, 'Product of the marginals.', 'Then also P(X | Y) = P(X).')
K.quiz('e', 'Each row of a Markov transition matrix…', ['adds up to 1', 'adds up to 0', 'is all equal', 'is sorted'], 0, 'Row i lists where you can go from i.', 'You must go somewhere, so the chances add to 1.')
K.quiz('e', 'Monte Carlo error shrinks like…', ['1 ÷ n', '1 ÷ √n', '1 ÷ n²', 'it never shrinks'], 1, 'Standard error.', 'σ ÷ √n: four times the samples, half the error.')
K.quiz('m', 'Prior Beta(1, 1) and you see 3 heads and 1 tail. The posterior is…', ['Beta(3, 1)', 'Beta(4, 2)', 'Beta(2, 4)', 'Beta(1, 1)'], 1, 'Add heads to a and tails to b.', 'Beta(1 + 3, 1 + 1) = Beta(4, 2).')
K.quiz('m', 'MAP with a normal prior on the weights is the same as…', ['L1 regularisation', 'L2 regularisation', 'no regularisation', 'dropout'], 1, 'Take the log of the prior.', 'ln N(0, σ²) = −w² ÷ (2σ²) + constant, an L2 penalty.')
K.quiz('m', 'The Mahalanobis distance with Σ = I equals…', ['the ordinary Euclidean distance', 'zero', 'the variance', 'the determinant'], 0, 'Σ⁻¹ = I.', '√((x − μ)ᵀ(x − μ)) is the usual length.')
K.quiz('m', 'In Metropolis, a proposal with higher target density than the current point is…', ['always accepted', 'always rejected', 'accepted half the time', 'accepted with probability r'], 0, 'min(1, r) with r &gt; 1.', 'Uphill moves are always taken.')
K.quiz('m', 'Inverse transform sampling uses…', ['the PDF', 'the inverse of the CDF', 'the mean', 'the variance'], 1, 'x = F⁻¹(u).', 'A uniform u is pushed through the inverse CDF.')
K.quiz('h', 'Why does MCMC not need p(data), the normalising constant of the posterior?', ['it is always 1', 'it cancels in the ratio p(x′) ÷ p(x)', 'it is estimated first', 'MCMC ignores the likelihood'], 1, 'Look at the acceptance ratio.', 'Both densities share the same constant, so it divides out.')
K.quiz('h', 'A Markov chain alternates A, B, A, B forever with probability 1. It fails which condition?', ['irreducible', 'aperiodic', 'each row adds to 1', 'it has states'], 1, 'It has a fixed rhythm.', 'A periodic chain never settles, even though a stationary distribution [0.5, 0.5] exists.')
K.quiz('h', 'Chebyshev says P(|X − μ| ≥ 3σ) is at most…', ['0.003', '1/9', '1/3', '0.05'], 1, '1 ÷ k².', 'For any distribution with a variance. A normal does much better, about 0.003.')
K.quiz('h', 'With little data, how do MLE and MAP compare?', ['they are always equal', 'MAP is pulled towards the prior', 'MLE is pulled towards the prior', 'MAP ignores the data'], 1, 'The prior acts like imaginary data.', 'With lots of data the two agree.')
K.quiz('x', 'Hoeffding: to halve ε with the same confidence, the number of samples must…', ['double', 'quadruple', 'stay the same', 'increase by 1'], 1, 'n appears with ε² in 2e<sup>−2nε²</sup>.', 'Keeping nε² fixed means n × 4 when ε ÷ 2.')
K.quiz('x', 'Metropolis acceptance rate is 99 % but estimates converge very slowly. The likely cause is…', ['the step size is too small', 'the step size is too large', 'too much burn in', 'the target is normalised'], 0, 'Tiny moves are almost always accepted.', 'The chain creeps, so successive samples are nearly identical.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'P(A and B) = 0.2 and P(B) = 0.4. What is P(A | B)?', '0.5', 'Divide the joint by the marginal of the condition.', [
    '<span class="eq">P(A | B) = P(A, B) ÷ P(B)</span>',
    '<span class="eq">0.2 ÷ 0.4 = 0.5</span>',
    'Half of the B cases are also A cases.',
], check=0.5)
K.calc('e', 'A row of a joint table holds 0.1, 0.15 and 0.05. What is the marginal probability of that row?', '0.3', 'Add across the row.', [
    '<span class="eq">0.1 + 0.15 = 0.25</span>',
    '<span class="eq">0.25 + 0.05 = 0.3</span>',
    'That row’s value happens 30 % of the time.',
], check=0.3)
K.calc('e', 'Prior Beta(2, 2), then 3 heads and 1 tail. What is the posterior mean?', '0.625', 'Posterior Beta(a + h, b + t), mean a ÷ (a + b).', [
    'Posterior: <span class="eq">Beta(5, 3)</span>',
    'Mean: <span class="eq">5 ÷ (5 + 3)</span>',
    '<span class="eq">= 0.625</span>',
], check=0.625)
K.calc('e', 'P = [[0.8, 0.2], [0.4, 0.6]] for (sunny, rainy). Today is sunny. What is P(sunny in two days)?', '0.72', 'Sunny then sunny, or rainy then sunny.', [
    'Sunny, sunny: <span class="eq">0.8 × 0.8 = 0.64</span>',
    'Rainy, sunny: <span class="eq">0.2 × 0.4 = 0.08</span>',
    'Add: <span class="eq">0.72</span>',
], check=0.72)
K.calc('m', 'A score of 130 when the mean is 100 and σ = 15. What is its Mahalanobis distance?', '2', 'In one dimension it is |x − μ| ÷ σ.', [
    '<span class="eq">130 − 100 = 30</span>',
    '<span class="eq">30 ÷ 15 = 2</span>',
    'Two standard deviations above the mean, the same as a z score.',
], check=2)
K.calc('m', 'Posterior Beta(9, 5). What is the MAP estimate? Give 4 decimals.', '0.6667', '(a − 1) ÷ (a + b − 2).', [
    '<span class="eq">a − 1 = 8</span>',
    '<span class="eq">a + b − 2 = 12</span>',
    '<span class="eq">8 ÷ 12 = 0.6667</span>',
], check=8 / 12, tol=1e-4)
K.calc('m', 'Exponential with λ = 2 by inverse transform. u = 0.5 gives which x? Give 4 decimals.', '0.3466', 'x = −ln(1 − u) ÷ λ.', [
    '<span class="eq">1 − u = 0.5</span>',
    '<span class="eq">−ln 0.5 = 0.6931</span>',
    '<span class="eq">0.6931 ÷ 2 = 0.3466</span>, which is the median of this distribution.',
], check=0.34657359, tol=1e-4)
K.calc('m', 'A Monte Carlo estimate averages 400 samples with standard deviation 2. What is its standard error?', '0.1', 'σ ÷ √n.', [
    '<span class="eq">√400 = 20</span>',
    '<span class="eq">2 ÷ 20 = 0.1</span>',
    'About 95 % of such estimates land within 0.2 of the truth.',
], check=0.1)
K.calc('h', 'Two state chain: sunny → rainy with chance 0.2, rainy → sunny with chance 0.4. What share of days is sunny in the long run? Give 4 decimals.', '0.6667', 'π<sub>sunny</sub> = b ÷ (a + b).', [
    'Balance: <span class="eq">π<sub>s</sub> × 0.2 = π<sub>r</sub> × 0.4</span>',
    'So <span class="eq">π<sub>s</sub> = 2π<sub>r</sub></span> and <span class="eq">π<sub>s</sub> + π<sub>r</sub> = 1</span>',
    '<span class="eq">π<sub>s</sub> = 0.4 ÷ 0.6 = 0.6667</span>',
], check=0.4 / 0.6, tol=1e-4)
K.calc('h', 'Chebyshev for an average: σ² = 0.25, n = 100, ε = 0.1. What is the bound on P(|x̄ − μ| ≥ ε)?', '0.25', 'σ² ÷ (n ε²).', [
    '<span class="eq">n ε² = 100 × 0.01 = 1</span>',
    '<span class="eq">0.25 ÷ 1 = 0.25</span>',
    'The exact chance for a fair coin is about 0.057, so the bound is safe but loose.',
], check=0.25)
K.calc('h', 'Metropolis for a standard normal, from x = 1 to x′ = 2. What is the acceptance probability? Give 4 decimals.', '0.2231', 'r = e<sup>−x′²/2</sup> ÷ e<sup>−x²/2</sup>.', [
    '<span class="eq">−x′²/2 + x²/2 = −2 + 0.5 = −1.5</span>',
    '<span class="eq">r = e<sup>−1.5</sup> = 0.2231</span>',
    'Below 1, so accept with probability 0.2231.',
], check=0.22313016, tol=1e-4)
K.calc('x', 'Hoeffding: how many samples guarantee |x̄ − μ| &lt; 0.05 with probability at least 0.95? Round up.', '738', 'Solve 2e<sup>−2nε²</sup> ≤ 0.05.', [
    '<span class="eq">e<sup>−2n × 0.0025</sup> ≤ 0.025</span>',
    '<span class="eq">0.005 n ≥ ln 40 = 3.6889</span>',
    '<span class="eq">n ≥ 737.8</span>, so <span class="eq">738</span> samples',
], check=738)

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;
  const fmt = v => MV.num(Math.abs(v) < 1e-9 ? 0 : v, 3);
  const setSl = (b, k, v, d = 2) => { $(`[data-sl="${k}"]`, b).value = v; $(`[data-slv="${k}"]`, b).textContent = MV.num(v, d); };
  const rng = s => () => { s = s * 16807 % 2147483647; return s / 2147483647; };
  const gauss = r => { const u = r(), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };

  /* ----- a joint table: joint, marginals and conditionals ----- */
  W.jointgrid = el => {
    const b = shell(el, 'Reading a joint table', 'Edit the counts of 100 days if you like. Press Play to step through the four views: the joint table, the marginals in the margins, then two conditionals, each one a single row or column rescaled to add to 1.');
    const R = ['☀️ sunny', '☁️ cloudy', '🌧️ rainy'], Cc = ['no umbrella', '☂️ umbrella'];
    const C0 = [[40, 5], [20, 10], [5, 20]];
    b.innerHTML = `<div class="tw"><table class="jt jg-t"><tr><th></th>${Cc.map(c => `<th>${c}</th>`).join('')}<th>row total</th></tr>${R.map((r, i) => `<tr><th>${r}</th>${[0, 1].map(j => `<td class="jg-c" data-i="${i}" data-j="${j}"><input type="number" min="0" value="${C0[i][j]}" aria-label="${r} ${Cc[j]} count"><div class="jg-p"></div></td>`).join('')}<td class="jg-r" data-i="${i}"></td></tr>`).join('')}<tr><th>column total</th><td class="jg-k" data-j="0"></td><td class="jg-k" data-j="1"></td><td class="jg-n"></td></tr></table></div><div class="mv-calc jg-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let mode = 0;
    function draw() {
      const C = [[0, 0], [0, 0], [0, 0]];
      b.querySelectorAll('.jg-c input').forEach(inp => { const td = inp.closest('td'); C[+td.dataset.i][+td.dataset.j] = Math.max(0, +inp.value || 0); });
      const n = C.flat().reduce((a, v) => a + v, 0) || 1, rs = C.map(r => r[0] + r[1]), cs = [0, 1].map(j => C[0][j] + C[1][j] + C[2][j]);
      b.querySelectorAll('.jg-c').forEach(td => {
        const i = +td.dataset.i, j = +td.dataset.j;
        let v = C[i][j] / n, on = mode === 0;
        if (mode === 2) { on = j === 1; v = cs[1] ? C[i][1] / cs[1] : 0; }
        if (mode === 3) { on = i === 2; v = rs[2] ? C[2][j] / rs[2] : 0; }
        td.classList.toggle('jg-on', on && mode !== 1);
        td.classList.toggle('jg-off', !on && mode !== 1);
        td.style.setProperty('--jg', (on ? Math.min(0.85, v * 1.6) : 0).toFixed(2));
        $('.jg-p', td).textContent = (mode === 1 ? MV.num(C[i][j] / n, 3) : on ? MV.num(v, 3) : '');
      });
      b.querySelectorAll('.jg-r').forEach(td => { const i = +td.dataset.i; td.textContent = MV.num(rs[i] / n, 3); td.classList.toggle('jg-hi', mode === 1); });
      b.querySelectorAll('.jg-k').forEach(td => { const j = +td.dataset.j; td.textContent = MV.num(cs[j] / n, 3); td.classList.toggle('jg-hi', mode === 1); });
      $('.jg-n', b).textContent = `${n} days`;
      const pr = rs[2] / n, pu = cs[1] / n, pj = C[2][1] / n;
      const msgs = [
        `Joint: each count ÷ ${n}. P(rainy, umbrella) = ${C[2][1]} ÷ ${n} = <b>${MV.num(pj, 3)}</b>. All cells add to 1.`,
        `Marginals: add across a row or down a column. P(rainy) = <b>${MV.num(pr, 3)}</b>, P(umbrella) = <b>${MV.num(pu, 3)}</b>.`,
        `Condition on umbrella: keep that column, divide by its total ${cs[1]}. P(rainy | umbrella) = ${C[2][1]} ÷ ${cs[1]} = <b>${MV.num(cs[1] ? C[2][1] / cs[1] : 0, 3)}</b>.`,
        `Condition on rainy: keep that row, divide by its total ${rs[2]}. P(umbrella | rainy) = <b>${MV.num(rs[2] ? C[2][1] / rs[2] : 0, 3)}</b>. Independence would need P(rainy) × P(umbrella) = ${MV.num(pr * pu, 4)} to equal ${MV.num(pj, 4)}: ${Math.abs(pr * pu - pj) < 1e-9 ? 'it does, independent' : 'it does not, dependent'}.`,
      ];
      $('.jg-msg', b).innerHTML = `<span class="t">view ${mode + 1}</span> ${msgs[mode]}`;
    }
    const P = Player($('.vz-p', b), t => { mode = t; draw(); }, 2200);
    b.querySelectorAll('.jg-c input').forEach(inp => inp.addEventListener('input', draw));
    P.load(4, 0);
  };

  /* ----- a 2D normal: ellipses, samples, Mahalanobis distance ----- */
  W.mvnorm = el => {
    const b = shell(el, 'A 2D normal and Mahalanobis distance', 'Set the spreads and the correlation ρ. Dots are 300 samples made with x = Lz (Cholesky). Rings are 1, 2 and 3 Mahalanobis units. Drag the orange point and compare its two distances. Press Play to sweep ρ.');
    b.innerHTML = `<div class="mv-wrap"><div class="mn-plot"></div><div class="mv-side">${slider('sx', 'σx', 0.4, 2.5, 1.6, 0.1)}${slider('sy', 'σy', 0.4, 2.5, 1, 0.1)}${slider('r', 'correlation ρ', -0.95, 0.95, 0.6, 0.05)}<div class="mv-read mn-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const S = { sx: 1.6, sy: 1, r: 0.6 }, q = [2, -1.5];
    const G = MV.frame(400, 400, [-5, 5], [-5, 5]);
    const r0 = rng(77), Z = Array.from({ length: 300 }, () => [gauss(r0), gauss(r0)]);
    const host = $('.mn-plot', b);
    host.innerHTML = MV.svg(G, '<g class="mn-g"></g>', 'Samples of a two dimensional normal');
    const svgEl = $('svg', host);
    function draw() {
      const a = S.sx * S.sx, c = S.r * S.sx * S.sy, d = S.sy * S.sy, det = a * d - c * c;
      const l11 = S.sx, l21 = c / l11, l22 = Math.sqrt(Math.max(0, d - l21 * l21));
      let s = MV.axes(G, { labels: false });
      Z.forEach(z => { const x = l11 * z[0], y = l21 * z[0] + l22 * z[1]; if (Math.abs(x) < 5 && Math.abs(y) < 5) s += MV.dot(G, x, y, 'k', 2); });
      [1, 2, 3].forEach(k => { const pts = []; for (let i = 0; i <= 100; i++) { const t = i / 100 * 2 * Math.PI, z0 = k * Math.cos(t), z1 = k * Math.sin(t); pts.push(G.sx(l11 * z0).toFixed(1) + ',' + G.sy(l21 * z0 + l22 * z1).toFixed(1)); } s += `<polygon class="mv-cont" style="fill:none;stroke-width:${k === 1 ? 2.2 : 1.4}" points="${pts.join(' ')}"/>`; });
      const inv = [[d / det, -c / det], [-c / det, a / det]], dm = Math.sqrt(q[0] * (inv[0][0] * q[0] + inv[0][1] * q[1]) + q[1] * (inv[1][0] * q[0] + inv[1][1] * q[1]));
      s += MV.line(G, 0, 0, q[0], q[1], 'mv-v o dash') + `<circle class="mv-pt o big mv-drag" data-h="0" cx="${G.sx(q[0])}" cy="${G.sy(q[1])}" r="10"/>`;
      $('.mn-g', svgEl).innerHTML = s;
      let inside = 0; Z.forEach(z => { if (z[0] * z[0] + z[1] * z[1] <= 4) inside++; });
      $('.mn-out', b).innerHTML = `Σ = [[${fmt(a)}, ${fmt(c)}], [${fmt(c)}, ${fmt(d)}]]<br>point = [${fmt(q[0])}, ${fmt(q[1])}]<br>Euclidean distance = <b>${fmt(Math.hypot(q[0], q[1]))}</b><br>Mahalanobis distance = <span class="big">${fmt(dm)}</span><br>${dm > 3 ? '⚠️ beyond 3 units: a likely outlier' : dm > 2 ? 'between 2 and 3 units: unusual' : 'within 2 units: typical'}<br>${inside} of 300 samples lie inside ring 2 (theory: 86 %)`;
    }
    const snap = v => Math.round(v * 4) / 4;
    MV.drag(svgEl, G, [{ set: (x, y) => { q[0] = snap(x); q[1] = snap(y); } }], draw);
    const P = Player($('.vz-p', b), t => { S.r = Math.round((-0.9 + t * 0.1) * 100) / 100; setSl(b, 'r', S.r); draw(); }, 450);
    ['sx', 'sy', 'r'].forEach(k => wireSlider(b, k, v => { P.pause(); S[k] = v; draw(); }));
    P.load(19, 15);
  };

  /* ----- Beta prior, likelihood and posterior for a coin ----- */
  W.betaprior = el => {
    const b = shell(el, 'Prior × likelihood = posterior', 'Set the prior Beta(a, b), then add heads and tails, or press Play to flip a coin 20 times one flip at a time. Dashed: prior. Green: likelihood (rescaled). Orange: posterior.');
    b.innerHTML = `<div class="mv-wrap"><div class="bp-plot"></div><div class="mv-side">${slider('a', 'prior a', 0.5, 20, 2, 0.5)}${slider('b', 'prior b', 0.5, 20, 2, 0.5)}${slider('h', 'heads', 0, 40, 7, 1)}${slider('t', 'tails', 0, 40, 3, 1)}<div class="mv-legend"><span><i></i>prior (dashed)</span><span><i class="g"></i>likelihood</span><span><i class="o"></i>posterior</span></div><div class="mv-read bp-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const S = { a: 2, b: 2, h: 7, t: 3 };
    const FLIPS = 'HHTHHHTHHTHTHHHTHHTH';
    const N = 600, xs = Array.from({ length: N + 1 }, (_, i) => (i + 0.5) / (N + 1));
    function dens(a, bb) {
      const lw = xs.map(x => (a - 1) * Math.log(x) + (bb - 1) * Math.log(1 - x)), m = Math.max(...lw);
      const w = lw.map(v => Math.exp(v - m)), z = w.reduce((s, v) => s + v, 0) / (N + 1);
      return w.map(v => v / z);
    }
    function draw() {
      const pr = dens(S.a, S.b), lk = dens(S.h + 1, S.t + 1), po = dens(S.a + S.h, S.b + S.t);
      const top = Math.min(12, Math.max(3, ...po, ...lk.slice(5, -5), ...pr.slice(5, -5)) * 1.1);
      const G = MV.frame(440, 300, [0, 1], [0, top]);
      const line = (arr, cls) => `<polyline class="mv-curve ${cls}" style="fill:none" points="${arr.map((v, i) => G.sx(xs[i]).toFixed(1) + ',' + G.sy(Math.min(top, v)).toFixed(1)).join(' ')}"/>`;
      let s = MV.axes(G, { xstep: 0.1 }) + line(pr, 'dash') + line(lk, 'c3') + line(po, 'c2');
      const A = S.a + S.h, B = S.b + S.t, n = S.h + S.t, mean = A / (A + B), map = A > 1 && B > 1 ? (A - 1) / (A + B - 2) : NaN;
      let cum = 0, lo = 0, hi = 1, gotLo = false;
      for (let i = 0; i <= N; i++) { cum += po[i] / (N + 1); if (!gotLo && cum >= 0.025) { lo = xs[i]; gotLo = true; } if (cum >= 0.975) { hi = xs[i]; break; } }
      s += MV.line(G, lo, 0, lo, top, 'mv-v o dash') + MV.line(G, hi, 0, hi, top, 'mv-v o dash');
      $('.bp-plot', b).innerHTML = MV.svg(G, s, 'Prior, likelihood and posterior');
      $('.bp-out', b).innerHTML = `posterior = Beta(${MV.num(A)}, ${MV.num(B)})<br>MLE = heads ÷ flips = <b>${n ? MV.num(S.h / n, 3) : '?'}</b><br>MAP = <b>${isFinite(map) ? MV.num(map, 3) : 'at an edge'}</b><br>posterior mean = <span class="big">${MV.num(mean, 3)}</span><br>95 % credible interval ≈ [${MV.num(lo, 2)}, ${MV.num(hi, 2)}] (orange dashes)`;
    }
    const P = Player($('.vz-p', b), t => { const f = FLIPS.slice(0, t); S.h = [...f].filter(c => c === 'H').length; S.t = t - S.h; setSl(b, 'h', S.h, 0); setSl(b, 't', S.t, 0); draw(); }, 700);
    ['a', 'b', 'h', 't'].forEach(k => wireSlider(b, k, v => { P.pause(); S[k] = v; draw(); }));
    P.load(21, 10);
  };

  /* ----- a three state Markov chain settling to its stationary distribution ----- */
  W.markov = el => {
    const b = shell(el, 'A Markov chain settling down', 'Pick a chain and a starting day, then press Play. Each step multiplies the probabilities by the transition matrix. The lines show each state’s chance over time, the bars show today.');
    const CH = {
      weather: [[0.7, 0.2, 0.1], [0.3, 0.4, 0.3], [0.2, 0.3, 0.5]],
      sticky: [[0.95, 0.05, 0], [0.05, 0.9, 0.05], [0, 0.05, 0.95]],
      cycle: [[0, 1, 0], [0, 0, 1], [1, 0, 0]],
    };
    const NAMES = ['☀️ sunny', '☁️ cloudy', '🌧️ rainy'], CLS = ['', 'c2', 'c3'], BAR = ['', 'o', 'g'];
    b.innerHTML = `<div class="vz-row">${seg('c', [['weather', 'weather'], ['sticky', 'sticky'], ['cycle', 'cycle']], 'weather')} ${seg('s', [['0', 'start sunny'], ['2', 'start rainy']], '0')}</div><div class="mv-wrap"><div class="mk-plot"></div><div class="mv-side"><div class="mv-legend"><span><i></i>sunny</span><span><i class="o"></i>cloudy</span><span><i class="g"></i>rainy</span></div><div class="mk-mat"></div><div class="mv-read mk-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let P0 = CH.weather, start = 0, T = 0;
    const G = MV.frame(440, 280, [0, 30], [0, 1]);
    function run() {
      let pi = [0, 0, 0]; pi[start] = 1; const hist = [pi];
      for (let t = 0; t < 30; t++) { pi = [0, 1, 2].map(j => pi[0] * P0[0][j] + pi[1] * P0[1][j] + pi[2] * P0[2][j]); hist.push(pi); }
      let st = [1 / 3, 1 / 3, 1 / 3]; for (let k = 0; k < 2000; k++) { const nx = [0, 1, 2].map(j => st[0] * P0[0][j] + st[1] * P0[1][j] + st[2] * P0[2][j]); st = [0, 1, 2].map(j => (st[j] + nx[j]) / 2); }
      return { hist, st };
    }
    function draw() {
      const { hist, st } = run();
      let s = MV.axes(G, { xstep: 5, ystep: 0.25 });
      [0, 1, 2].forEach(k => { s += `<polyline class="mv-curve ${CLS[k]}" style="fill:none" points="${hist.slice(0, T + 1).map((p, t) => G.sx(t).toFixed(1) + ',' + G.sy(p[k]).toFixed(1)).join(' ')}"/>`; s += MV.line(G, 0, st[k], 30, st[k], 'mv-v k dash'); });
      $('.mk-plot', b).innerHTML = MV.svg(G, s, 'Probabilities over time');
      $('.mk-mat', b).innerHTML = `<div class="mv-mgrid" style="grid-template-columns:repeat(3,auto)">${P0.flat().map(v => `<div class="mv-c">${MV.num(v, 2)}</div>`).join('')}</div>`;
      const pi = hist[T];
      $('.mk-out', b).innerHTML = `day ${T}:<br>` + [0, 1, 2].map(k => `${NAMES[k]} <b>${MV.num(pi[k], 3)}</b> <span class="mk-bar ${BAR[k]}" style="width:${Math.round(pi[k] * 90)}px"></span>`).join('<br>') + `<br>stationary (dashed): [${st.map(v => MV.num(v, 3)).join(', ')}]` + (P0 === CH.cycle ? '<br>⚠️ This chain cycles with period 3, so day by day it never settles.' : '');
    }
    const P = Player($('.vz-p', b), t => { T = t; draw(); }, 450);
    wireSeg(b, 'c', k => { P0 = CH[k]; P.load(31, 0); });
    wireSeg(b, 's', k => { start = +k; P.load(31, 0); });
    P.load(31, 30);
  };

  /* ----- inverse transform: uniform u through the inverse CDF ----- */
  W.invsample = el => {
    const b = shell(el, 'Inverse transform sampling', 'Each uniform u (on the vertical axis of the CDF) is carried across to the curve and down to x = F⁻¹(u). Press Play to draw more and more samples. The histogram below fills in the true density.');
    b.innerHTML = `<div class="mv-wrap"><div><div class="is-top"></div><div class="is-bot"></div></div><div class="mv-side">${slider('l', 'rate λ', 0.5, 3, 1.5, 0.1)}<div class="mv-read is-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const COUNTS = [0, 1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000];
    let lam = 1.5, T = 6;
    const r0 = rng(2026), U = Array.from({ length: 5000 }, () => r0());
    function draw() {
      const n = COUNTS[T], X = U.slice(0, n).map(u => -Math.log(1 - u) / lam), xmax = 4;
      const G1 = MV.frame(440, 210, [0, xmax], [0, 1.05]), G2 = MV.frame(440, 210, [0, xmax], [0, lam * 1.15]);
      let s1 = MV.axes(G1, { xstep: 1, ystep: 0.25 }) + MV.curve(G1, x => 1 - Math.exp(-lam * x), '');
      U.slice(Math.max(0, n - 5), n).forEach((u, i, arr) => { const x = -Math.log(1 - u) / lam; if (x <= xmax) { const last = i === arr.length - 1; s1 += MV.line(G1, 0, u, x, u, last ? 'mv-v o' : 'mv-v k dash') + MV.line(G1, x, u, x, 0, last ? 'mv-v o' : 'mv-v k dash') + MV.dot(G1, 0, u, last ? 'o' : 'k', last ? 5 : 3); } });
      const bins = 20, w = xmax / bins, h = Array(bins).fill(0); X.forEach(x => { if (x < xmax) h[Math.floor(x / w)]++; });
      let s2 = MV.axes(G2, { xstep: 1 });
      h.forEach((c, i) => { const d = n ? c / (n * w) : 0, top = Math.min(d, lam * 1.15); s2 += `<rect class="mv-bar o" x="${G2.sx(i * w).toFixed(1)}" y="${G2.sy(top).toFixed(1)}" width="${(G2.sx(w) - G2.sx(0) - 1).toFixed(1)}" height="${(G2.sy(0) - G2.sy(top)).toFixed(1)}"/>`; });
      s2 += MV.curve(G2, x => lam * Math.exp(-lam * x), '');
      $('.is-top', b).innerHTML = MV.svg(G1, s1, 'CDF with uniform draws');
      $('.is-bot', b).innerHTML = MV.svg(G2, s2, 'Histogram of samples and the density');
      const mean = n ? X.reduce((a, v) => a + v, 0) / n : NaN, last = n ? U[n - 1] : NaN;
      $('.is-out', b).innerHTML = `F(x) = 1 − e<sup>−λx</sup>, so x = −ln(1 − u) ÷ λ<br>${n ? `last u = ${MV.num(last, 3)} → x = <b>${MV.num(-Math.log(1 - last) / lam, 3)}</b><br>` : ''}samples: <b>${n}</b><br>sample mean = <span class="big">${n ? MV.num(mean, 3) : '?'}</span><br>true mean 1 ÷ λ = ${MV.num(1 / lam, 3)}<br>top: the CDF, bottom: histogram and density`;
    }
    const P = Player($('.vz-p', b), t => { T = t; draw(); }, 800);
    wireSlider(b, 'l', v => { lam = v; draw(); });
    P.load(COUNTS.length, 6);
  };

  /* ----- Metropolis on a two peaked target ----- */
  W.metropolis = el => {
    const b = shell(el, 'Metropolis on a two peaked target', 'The blue curve is the target. Press Play to run more and more steps. The histogram of visited points should take the target’s shape, and the trace below shows the path. Try a tiny step (stuck in one peak) and a huge step (most moves rejected).');
    b.innerHTML = `<div class="mv-wrap"><div><div class="mh-top"></div><div class="mh-bot"></div></div><div class="mv-side">${slider('s', 'step size', 0.1, 8, 1.5, 0.1)}<div class="mv-read mh-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const COUNTS = [0, 10, 30, 100, 300, 1000, 3000, 10000];
    const tgt = x => 0.5 * Math.exp(-((x + 2) ** 2) / (2 * 0.49)) + 0.5 * Math.exp(-((x - 2) ** 2) / (2 * 0.49));
    const Z = Math.sqrt(2 * Math.PI * 0.49);
    let step = 1.5, T = 5;
    function chain(n) {
      const r = rng(4242); let x = -2, acc = 0; const xs = [x];
      for (let i = 0; i < n; i++) { const p = x + step * (2 * r() - 1); if (r() < tgt(p) / tgt(x)) { x = p; acc++; } xs.push(x); }
      return { xs, acc };
    }
    function draw() {
      const n = COUNTS[T], { xs, acc } = chain(n);
      const G1 = MV.frame(440, 210, [-5, 5], [0, 0.75]);
      const bins = 40, w = 10 / bins, h = Array(bins).fill(0); xs.slice(1).forEach(x => { const k = Math.floor((x + 5) / w); if (k >= 0 && k < bins) h[k]++; });
      let s1 = MV.axes(G1, { xstep: 1, ystep: 0.25 });
      h.forEach((c, i) => { const d = n ? Math.min(0.75, c / (n * w)) : 0; s1 += `<rect class="mv-bar o" x="${G1.sx(-5 + i * w).toFixed(1)}" y="${G1.sy(d).toFixed(1)}" width="${(G1.sx(w) - G1.sx(0) - 1).toFixed(1)}" height="${(G1.sy(0) - G1.sy(d)).toFixed(1)}"/>`; });
      s1 += MV.curve(G1, x => tgt(x) / Z, '');
      const show = xs.slice(-300), G2 = MV.frame(440, 170, [0, Math.max(10, show.length - 1)], [-5, 5]);
      let s2 = MV.axes(G2, { labels: false, ystep: 2 }) + `<polyline class="mv-curve c4" style="fill:none" points="${show.map((x, i) => G2.sx(i).toFixed(1) + ',' + G2.sy(Math.max(-5, Math.min(5, x))).toFixed(1)).join(' ')}"/>`;
      $('.mh-top', b).innerHTML = MV.svg(G1, s1, 'Histogram of samples and target');
      $('.mh-bot', b).innerHTML = MV.svg(G2, s2, 'Trace of the chain');
      const right = n ? xs.slice(1).filter(x => x > 0).length / n : NaN;
      $('.mh-out', b).innerHTML = `steps: <b>${n}</b><br>acceptance rate = <span class="big">${n ? MV.num(acc / n * 100, 1) + ' %' : '?'}</span><br>share of time in the right peak = <b>${n ? MV.num(right * 100, 1) + ' %' : '?'}</b> (target 50 %)<br>top: histogram and target, bottom: last ${show.length - 1} steps of the path<br>` + (step < 0.6 ? '🐌 tiny steps: the chain rarely crosses between the peaks' : step > 5 ? '🧱 huge steps: most proposals are rejected' : 'a reasonable step size');
    }
    const P = Player($('.vz-p', b), t => { T = t; draw(); }, 900);
    wireSlider(b, 's', v => { step = v; draw(); });
    P.load(COUNTS.length, 5);
  };

  /* ----- running averages of coin flips with guarantee bands ----- */
  W.lln = el => {
    const b = shell(el, 'Averages settle, and the bounds say how fast', 'Five people each flip a coin with chance p of heads and track their running share of heads. The bands show 95 % ranges from Chebyshev (purple), Hoeffding (green) and the normal approximation (orange). The horizontal axis is logarithmic, from 1 to 10 000 flips. Press Play to keep flipping.');
    b.innerHTML = `<div class="mv-wrap"><div class="ll-plot"></div><div class="mv-side">${slider('p', 'chance of heads p', 0.1, 0.9, 0.5, 0.05)}<div class="mv-legend"><span><i class="p"></i>Chebyshev</span><span><i class="g"></i>Hoeffding</span><span><i class="o"></i>normal</span></div><div class="mv-read ll-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let p = 0.5, T = 40;
    const NMAX = 10000;
    const r0 = rng(99), U = Array.from({ length: 5 }, () => Array.from({ length: NMAX }, () => r0()));
    const G = MV.frame(440, 320, [0, 4], [0, 1]);
    function draw() {
      const nmax = Math.round(Math.pow(10, T / 10));
      let s = MV.axes(G, { labels: false, xstep: 1, ystep: 0.25 });
      const v = p * (1 - p);
      const band = (fn, cls) => { [1, -1].forEach(sg => { s += MV.curve(G, lx => p + sg * fn(Math.pow(10, lx)), cls, { from: 0, to: 4, n: 200 }); }); };
      band(n => Math.sqrt(v / (0.05 * n)), 'c4');
      band(n => Math.sqrt(Math.log(40) / (2 * n)), 'c3');
      band(n => 1.96 * Math.sqrt(v / n), 'c2');
      s += MV.line(G, 0, p, 4, p, 'mv-v k dash');
      const ends = [];
      U.forEach(us => {
        let h = 0; const pts = [];
        for (let i = 1; i <= nmax; i++) { if (us[i - 1] < p) h++; if (i < 50 || i % Math.ceil(i / 50) === 0 || i === nmax) pts.push(G.sx(Math.log10(i)).toFixed(1) + ',' + G.sy(h / i).toFixed(1)); }
        ends.push(h / nmax);
        s += `<polyline class="mv-curve thin" style="fill:none" points="${pts.join(' ')}"/>`;
      });
      [0, 1, 2, 3, 4].forEach(k => { s += MV.text(G, k, 0, String(Math.pow(10, k)), { dy: 16, anchor: 'middle', cls: 'sm' }); });
      [0.25, 0.5, 0.75].forEach(y => { s += MV.text(G, 0, y, String(y), { dx: -4, dy: 4, anchor: 'end', cls: 'sm' }); });
      $('.ll-plot', b).innerHTML = MV.svg(G, s, 'Running averages with bands');
      $('.ll-out', b).innerHTML = `flips so far: <b>${nmax}</b><br>running shares: ${ends.map(e => MV.num(e, 3)).join(', ')}<br>95 % half widths at n = ${nmax}:<br>Chebyshev ±${MV.num(Math.sqrt(v / (0.05 * nmax)), 3)}<br>Hoeffding ±${MV.num(Math.sqrt(Math.log(40) / (2 * nmax)), 3)}<br>normal ±<b>${MV.num(1.96 * Math.sqrt(v / nmax), 3)}</b><br>The guarantees are wider, but they hold without any approximation.`;
    }
    const P = Player($('.vz-p', b), t => { T = t; draw(); }, 300);
    wireSlider(b, 'p', x => { p = x; draw(); });
    P.load(41, 40);
  };
})();
'''

CSS = r'''
.mn-plot .mv-svg{max-height:420px}
.jg-t td.jg-c{position:relative; background:color-mix(in srgb, var(--accent) calc(var(--jg, 0) * 100%), transparent); transition:background .3s}
.jg-t td.jg-off{opacity:.35}
.jg-t td.jg-hi{outline:2px solid var(--orange); font-weight:800}
.jg-t input{width:56px}
.jg-p{font-weight:800; font-size:13px; min-height:18px}
.mk-mat{margin:4px 0 8px}
.mk-mat .mv-c{min-width:40px; font-size:12.5px}
.mk-bar{display:inline-block; height:8px; border-radius:4px; vertical-align:middle; margin-left:6px; background:var(--accent)}
.mk-bar.o{background:var(--orange)} .mk-bar.g{background:var(--green)}
'''

T = K.topic(
    slug='bayes-sampling', topic='bayes-sampling', prefix='mm15', short='Bayes and sampling', emoji='🎰',
    title='Bayesian Inference, Markov Chains and Sampling',
    module=('🚀', 'Advanced maths for ML', 'advanced', 'The next level: matrix factorisations and tensors, Taylor series, Newton’s method and automatic differentiation, and Bayesian inference with sampling.'),
    minutes=60, added='2026-10-24',
    lead='Handle uncertainty the way modern models do. Read joint, marginal and conditional distributions, measure distance with the multivariate normal, update beliefs with Bayes and conjugate priors, watch Markov chains settle, estimate with Monte Carlo, sample posteriors with Metropolis, and see how concentration inequalities guarantee how close an average is.',
    desc='Probability for advanced machine learning: joint, marginal and conditional distributions, the multivariate normal and Mahalanobis distance, Bayesian inference with Beta Binomial conjugate priors and MAP, Markov chains and stationary distributions, Monte Carlo and inverse transform sampling, MCMC with the Metropolis algorithm, and Markov, Chebyshev and Hoeffding inequalities.',
    summary='Joint tables, marginals by summing, conditionals by dividing, independence and the chain rule of probability, the multivariate normal with Mahalanobis distance and Cholesky sampling, priors, likelihoods and posteriors with the Beta Binomial update, MLE versus MAP and priors as regularisation, transition matrices and stationary distributions with PageRank, Monte Carlo error 1 ÷ √n, inverse transform, rejection and importance sampling, Metropolis with burn in and step size, Markov, Chebyshev and Hoeffding bounds and PAC learning.',
    keywords=['joint distribution', 'marginal', 'conditional', 'multivariate normal', 'mahalanobis', 'bayesian inference', 'prior', 'posterior', 'beta binomial', 'map', 'markov chain', 'stationary distribution', 'pagerank', 'monte carlo', 'inverse transform', 'mcmc', 'metropolis', 'hoeffding', 'chebyshev'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
