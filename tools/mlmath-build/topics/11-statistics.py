# Chapter 11: descriptive statistics, sampling and standard error, confidence intervals, hypothesis tests and
# p-values, A/B tests, maximum likelihood, linear regression with R², and the bias and variance trade-off.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz

K = Kit()

ERF_PY = '''
def erf(x):                               # Abramowitz and Stegun 7.1.26, accurate to about 0.0000001
    sign = 1 if x >= 0 else -1
    x = abs(x)
    t = 1 / (1 + 0.3275911 * x)
    poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))))
    return sign * (1 - poly * exp(-x * x))


def phi(z):                               # P(Z <= z) for the standard normal
    return 0.5 * (1 + erf(z / sqrt(2)))
'''
ERF_JS = '''
function erf(x) {                         // Abramowitz and Stegun 7.1.26, accurate to about 0.0000001
  const sign = x >= 0 ? 1 : -1;
  x = Math.abs(x);
  const t = 1 / (1 + 0.3275911 * x);
  const poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
  return sign * (1 - poly * Math.exp(-x * x));
}

const phi = z => 0.5 * (1 + erf(z / Math.sqrt(2)));   // P(Z <= z) for the standard normal
'''
ERF_TS = '''
function erf(x: number): number {         // Abramowitz and Stegun 7.1.26, accurate to about 0.0000001
  const sign: number = x >= 0 ? 1 : -1;
  x = Math.abs(x);
  const t: number = 1 / (1 + 0.3275911 * x);
  const poly: number = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
  return sign * (1 - poly * Math.exp(-x * x));
}

const phi = (z: number): number => 0.5 * (1 + erf(z / Math.sqrt(2)));   // P(Z <= z) for the standard normal
'''
ERF_JAVA = '''
    static double erf(double x) {             // Abramowitz and Stegun 7.1.26, accurate to about 0.0000001
        double sign = x >= 0 ? 1 : -1;
        x = Math.abs(x);
        double t = 1 / (1 + 0.3275911 * x);
        double poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
        return sign * (1 - poly * Math.exp(-x * x));
    }

    static double phi(double z) {             // P(Z <= z) for the standard normal
        return 0.5 * (1 + erf(z / Math.sqrt(2)));
    }
'''

# ---------------------------------------------------------------- programs
K.code('describe', py=r'''
from math import sqrt

minutes = [22, 25, 21, 24, 23, 25, 60]    # commute times for one week, one day had a breakdown
n = len(minutes)
data = sorted(minutes)
mean = sum(data) / n
median = data[n // 2] if n % 2 == 1 else (data[n // 2 - 1] + data[n // 2]) / 2
mode = max(data, key=data.count)          # the value that appears most often
var = sum((x - mean) ** 2 for x in data) / (n - 1)   # sample variance divides by n - 1
print(f"sorted: {data}")
print(f"mean {mean:.2f}, median {median}, mode {mode}, range {data[-1] - data[0]}")
print(f"sample SD {sqrt(var):.2f}")
calm = data[:-1]                          # drop the breakdown day
m2 = sum(calm) / len(calm)
print(f"without 60: mean {m2:.2f}, SD {sqrt(sum((x - m2) ** 2 for x in calm) / (len(calm) - 1)):.2f}")
''', js=r'''
const minutes = [22, 25, 21, 24, 23, 25, 60];   // commute times for one week, one day had a breakdown
const n = minutes.length;
const data = [...minutes].sort((a, b) => a - b);
const mean = data.reduce((s, x) => s + x, 0) / n;
const median = n % 2 === 1 ? data[Math.floor(n / 2)] : (data[n / 2 - 1] + data[n / 2]) / 2;
const count = x => data.filter(v => v === x).length;
const mode = data.reduce((best, x) => (count(x) > count(best) ? x : best), data[0]);   // the value that appears most often
const variance = data.reduce((s, x) => s + (x - mean) ** 2, 0) / (n - 1);   // sample variance divides by n - 1
console.log(`sorted: [${data.join(", ")}]`);
console.log(`mean ${mean.toFixed(2)}, median ${median}, mode ${mode}, range ${data[n - 1] - data[0]}`);
console.log(`sample SD ${Math.sqrt(variance).toFixed(2)}`);
const calm = data.slice(0, -1);           // drop the breakdown day
const m2 = calm.reduce((s, x) => s + x, 0) / calm.length;
console.log(`without 60: mean ${m2.toFixed(2)}, SD ${Math.sqrt(calm.reduce((s, x) => s + (x - m2) ** 2, 0) / (calm.length - 1)).toFixed(2)}`);
''', ts=r'''
const minutes: number[] = [22, 25, 21, 24, 23, 25, 60];   // commute times for one week, one day had a breakdown
const n: number = minutes.length;
const data: number[] = [...minutes].sort((a, b) => a - b);
const mean: number = data.reduce((s, x) => s + x, 0) / n;
const median: number = n % 2 === 1 ? data[Math.floor(n / 2)] : (data[n / 2 - 1] + data[n / 2]) / 2;
const count = (x: number): number => data.filter(v => v === x).length;
const mode: number = data.reduce((best, x) => (count(x) > count(best) ? x : best), data[0]);   // the value that appears most often
const variance: number = data.reduce((s, x) => s + (x - mean) ** 2, 0) / (n - 1);   // sample variance divides by n - 1
console.log(`sorted: [${data.join(", ")}]`);
console.log(`mean ${mean.toFixed(2)}, median ${median}, mode ${mode}, range ${data[n - 1] - data[0]}`);
console.log(`sample SD ${Math.sqrt(variance).toFixed(2)}`);
const calm: number[] = data.slice(0, -1); // drop the breakdown day
const m2: number = calm.reduce((s, x) => s + x, 0) / calm.length;
console.log(`without 60: mean ${m2.toFixed(2)}, SD ${Math.sqrt(calm.reduce((s, x) => s + (x - m2) ** 2, 0) / (calm.length - 1)).toFixed(2)}`);
''', java=r'''
import java.util.Arrays;

public class Describe {
    public static void main(String[] args) {
        int[] data = {22, 25, 21, 24, 23, 25, 60};   // commute times for one week, one day had a breakdown
        int n = data.length;
        Arrays.sort(data);
        double mean = 0;
        for (int x : data) mean += (double) x / n;
        int median = data[n / 2];                 // n is odd here, so the middle value
        int mode = data[0], best = 0;
        for (int x : data) {                      // the value that appears most often
            int c = 0;
            for (int v : data) if (v == x) c++;
            if (c > best) { best = c; mode = x; }
        }
        double var = 0;
        for (int x : data) var += (x - mean) * (x - mean) / (n - 1);   // sample variance divides by n - 1
        System.out.println("sorted: " + Arrays.toString(data));
        System.out.println(String.format("mean %.2f, median %d, mode %d, range %d", mean, median, mode, data[n - 1] - data[0]));
        System.out.println(String.format("sample SD %.2f", Math.sqrt(var)));
        double m2 = 0, v2 = 0;                    // drop the breakdown day
        for (int i = 0; i < n - 1; i++) m2 += (double) data[i] / (n - 1);
        for (int i = 0; i < n - 1; i++) v2 += (data[i] - m2) * (data[i] - m2) / (n - 2);
        System.out.println(String.format("without 60: mean %.2f, SD %.2f", m2, Math.sqrt(v2)));
    }
}
''')

K.code('confidence', py=r'''
from math import sqrt

n, mean, s = 36, 18.2, 2.4                # 36 phones: average battery life 18.2 hours, sample SD 2.4
se = s / sqrt(n)                          # standard error of the mean
print(f"standard error = {s} / sqrt({n}) = {se:.2f}")
for level, z in ((90, 1.645), (95, 1.96), (99, 2.576)):
    margin = z * se
    print(f"{level}% interval: {mean} +/- {margin:.3f} = [{mean - margin:.2f}, {mean + margin:.2f}]")
''', js=r'''
const n = 36, mean = 18.2, s = 2.4;       // 36 phones: average battery life 18.2 hours, sample SD 2.4
const se = s / Math.sqrt(n);              // standard error of the mean
console.log(`standard error = ${s} / sqrt(${n}) = ${se.toFixed(2)}`);
for (const [level, z] of [[90, 1.645], [95, 1.96], [99, 2.576]]) {
  const margin = z * se;
  console.log(`${level}% interval: ${mean} +/- ${margin.toFixed(3)} = [${(mean - margin).toFixed(2)}, ${(mean + margin).toFixed(2)}]`);
}
''', ts=r'''
const n: number = 36, mean: number = 18.2, s: number = 2.4;   // 36 phones: average battery life 18.2 hours, sample SD 2.4
const se: number = s / Math.sqrt(n);      // standard error of the mean
console.log(`standard error = ${s} / sqrt(${n}) = ${se.toFixed(2)}`);
for (const [level, z] of [[90, 1.645], [95, 1.96], [99, 2.576]] as [number, number][]) {
  const margin: number = z * se;
  console.log(`${level}% interval: ${mean} +/- ${margin.toFixed(3)} = [${(mean - margin).toFixed(2)}, ${(mean + margin).toFixed(2)}]`);
}
''', java=r'''
public class Confidence {
    public static void main(String[] args) {
        int n = 36;
        double mean = 18.2, s = 2.4;              // 36 phones: average battery life 18.2 hours, sample SD 2.4
        double se = s / Math.sqrt(n);             // standard error of the mean
        System.out.println(String.format("standard error = %s / sqrt(%d) = %.2f", s, n, se));
        int[] levels = {90, 95, 99};
        double[] zs = {1.645, 1.96, 2.576};
        for (int i = 0; i < 3; i++) {
            double margin = zs[i] * se;
            System.out.println(String.format("%d%% interval: %s +/- %.3f = [%.2f, %.2f]", levels[i], mean, margin, mean - margin, mean + margin));
        }
    }
}
''')

K.code('ab_test', py=r'''
from math import exp, sqrt
''' + ERF_PY + r'''

visitors_a, buys_a = 2000, 200            # old page
visitors_b, buys_b = 2000, 250            # new page
pa, pb = buys_a / visitors_a, buys_b / visitors_b
pooled = (buys_a + buys_b) / (visitors_a + visitors_b)   # the shared rate if the pages were really the same
se = sqrt(pooled * (1 - pooled) * (1 / visitors_a + 1 / visitors_b))
z = (pb - pa) / se                        # how many standard errors apart the two rates are
p_value = 2 * (1 - phi(abs(z)))           # two sided: a difference this big in either direction
print(f"A converts {pa:.4f}, B converts {pb:.4f}, lift {pb - pa:.4f}")
print(f"pooled rate {pooled:.4f}, standard error {se:.5f}")
print(f"z = {z:.3f}, p-value = {p_value:.4f}")
print("significant at 5%" if p_value < 0.05 else "not significant at 5%")
''', js=ERF_JS + r'''
const visitorsA = 2000, buysA = 200;      // old page
const visitorsB = 2000, buysB = 250;      // new page
const pa = buysA / visitorsA, pb = buysB / visitorsB;
const pooled = (buysA + buysB) / (visitorsA + visitorsB);   // the shared rate if the pages were really the same
const se = Math.sqrt(pooled * (1 - pooled) * (1 / visitorsA + 1 / visitorsB));
const z = (pb - pa) / se;                 // how many standard errors apart the two rates are
const pValue = 2 * (1 - phi(Math.abs(z)));   // two sided: a difference this big in either direction
console.log(`A converts ${pa.toFixed(4)}, B converts ${pb.toFixed(4)}, lift ${(pb - pa).toFixed(4)}`);
console.log(`pooled rate ${pooled.toFixed(4)}, standard error ${se.toFixed(5)}`);
console.log(`z = ${z.toFixed(3)}, p-value = ${pValue.toFixed(4)}`);
console.log(pValue < 0.05 ? "significant at 5%" : "not significant at 5%");
''', ts=ERF_TS + r'''
const visitorsA: number = 2000, buysA: number = 200;   // old page
const visitorsB: number = 2000, buysB: number = 250;   // new page
const pa: number = buysA / visitorsA, pb: number = buysB / visitorsB;
const pooled: number = (buysA + buysB) / (visitorsA + visitorsB);   // the shared rate if the pages were really the same
const se: number = Math.sqrt(pooled * (1 - pooled) * (1 / visitorsA + 1 / visitorsB));
const z: number = (pb - pa) / se;         // how many standard errors apart the two rates are
const pValue: number = 2 * (1 - phi(Math.abs(z)));   // two sided: a difference this big in either direction
console.log(`A converts ${pa.toFixed(4)}, B converts ${pb.toFixed(4)}, lift ${(pb - pa).toFixed(4)}`);
console.log(`pooled rate ${pooled.toFixed(4)}, standard error ${se.toFixed(5)}`);
console.log(`z = ${z.toFixed(3)}, p-value = ${pValue.toFixed(4)}`);
console.log(pValue < 0.05 ? "significant at 5%" : "not significant at 5%");
''', java=r'''
public class AbTest {''' + ERF_JAVA + r'''
    public static void main(String[] args) {
        int visitorsA = 2000, buysA = 200;        // old page
        int visitorsB = 2000, buysB = 250;        // new page
        double pa = (double) buysA / visitorsA, pb = (double) buysB / visitorsB;
        double pooled = (double) (buysA + buysB) / (visitorsA + visitorsB);   // the shared rate if the pages were really the same
        double se = Math.sqrt(pooled * (1 - pooled) * (1.0 / visitorsA + 1.0 / visitorsB));
        double z = (pb - pa) / se;                // how many standard errors apart the two rates are
        double pValue = 2 * (1 - phi(Math.abs(z)));   // two sided: a difference this big in either direction
        System.out.println(String.format("A converts %.4f, B converts %.4f, lift %.4f", pa, pb, pb - pa));
        System.out.println(String.format("pooled rate %.4f, standard error %.5f", pooled, se));
        System.out.println(String.format("z = %.3f, p-value = %.4f", z, pValue));
        System.out.println(pValue < 0.05 ? "significant at 5%" : "not significant at 5%");
    }
}
''')

K.code('mle', py=r'''
from math import log

heads, flips = 7, 10                      # the data: 7 heads in 10 flips
best_p, best_ll = 0, -1e9
for i in range(1, 10):
    p = i / 10                            # try p = 0.1, 0.2, ..., 0.9
    ll = heads * log(p) + (flips - heads) * log(1 - p)   # log-likelihood of the data
    print(f"p = {p:.1f}: log L = {ll:.4f}")
    if ll > best_ll:
        best_p, best_ll = p, ll
print(f"best guess on the grid: p = {best_p:.1f}")
print(f"formula heads / flips = {heads / flips:.1f}")
''', js=r'''
const heads = 7, flips = 10;              // the data: 7 heads in 10 flips
let bestP = 0, bestLL = -1e9;
for (let i = 1; i <= 9; i++) {
  const p = i / 10;                       // try p = 0.1, 0.2, ..., 0.9
  const ll = heads * Math.log(p) + (flips - heads) * Math.log(1 - p);   // log-likelihood of the data
  console.log(`p = ${p.toFixed(1)}: log L = ${ll.toFixed(4)}`);
  if (ll > bestLL) {
    bestP = p;
    bestLL = ll;
  }
}
console.log(`best guess on the grid: p = ${bestP.toFixed(1)}`);
console.log(`formula heads / flips = ${(heads / flips).toFixed(1)}`);
''', ts=r'''
const heads: number = 7, flips: number = 10;   // the data: 7 heads in 10 flips
let bestP: number = 0, bestLL: number = -1e9;
for (let i = 1; i <= 9; i++) {
  const p: number = i / 10;               // try p = 0.1, 0.2, ..., 0.9
  const ll: number = heads * Math.log(p) + (flips - heads) * Math.log(1 - p);   // log-likelihood of the data
  console.log(`p = ${p.toFixed(1)}: log L = ${ll.toFixed(4)}`);
  if (ll > bestLL) {
    bestP = p;
    bestLL = ll;
  }
}
console.log(`best guess on the grid: p = ${bestP.toFixed(1)}`);
console.log(`formula heads / flips = ${(heads / flips).toFixed(1)}`);
''', java=r'''
public class MaxLikelihood {
    public static void main(String[] args) {
        int heads = 7, flips = 10;                // the data: 7 heads in 10 flips
        double bestP = 0, bestLL = -1e9;
        for (int i = 1; i <= 9; i++) {
            double p = i / 10.0;                  // try p = 0.1, 0.2, ..., 0.9
            double ll = heads * Math.log(p) + (flips - heads) * Math.log(1 - p);   // log-likelihood of the data
            System.out.println(String.format("p = %.1f: log L = %.4f", p, ll));
            if (ll > bestLL) {
                bestP = p;
                bestLL = ll;
            }
        }
        System.out.println(String.format("best guess on the grid: p = %.1f", bestP));
        System.out.println(String.format("formula heads / flips = %.1f", (double) heads / flips));
    }
}
''')

K.code('regression', py=r'''
hours = [1, 2, 3, 4, 5, 6]
score = [52, 55, 61, 66, 70, 78]
n = len(hours)
mx, my = sum(hours) / n, sum(score) / n
sxy = sum((x - mx) * (y - my) for x, y in zip(hours, score))
sxx = sum((x - mx) ** 2 for x in hours)
slope = sxy / sxx                         # least squares slope = covariance / variance of x
intercept = my - slope * mx               # the line passes through the point of means
print(f"score = {intercept:.2f} + {slope:.2f} x hours")
ss_res, ss_tot = 0, 0
for x, y in zip(hours, score):
    pred = intercept + slope * x
    ss_res += (y - pred) ** 2             # what the line misses
    ss_tot += (y - my) ** 2               # total spread around the mean
    print(f"x = {x}: actual {y}, predicted {pred:.2f}, residual {y - pred + 0.0:.2f}")
print(f"R^2 = 1 - {ss_res:.2f} / {ss_tot:.2f} = {1 - ss_res / ss_tot:.4f}")
''', js=r'''
const hours = [1, 2, 3, 4, 5, 6];
const score = [52, 55, 61, 66, 70, 78];
const n = hours.length;
const mx = hours.reduce((s, v) => s + v, 0) / n, my = score.reduce((s, v) => s + v, 0) / n;
const sxy = hours.reduce((s, x, i) => s + (x - mx) * (score[i] - my), 0);
const sxx = hours.reduce((s, x) => s + (x - mx) ** 2, 0);
const slope = sxy / sxx;                  // least squares slope = covariance / variance of x
const intercept = my - slope * mx;        // the line passes through the point of means
console.log(`score = ${intercept.toFixed(2)} + ${slope.toFixed(2)} x hours`);
let ssRes = 0, ssTot = 0;
hours.forEach((x, i) => {
  const y = score[i], pred = intercept + slope * x;
  ssRes += (y - pred) ** 2;               // what the line misses
  ssTot += (y - my) ** 2;                 // total spread around the mean
  console.log(`x = ${x}: actual ${y}, predicted ${pred.toFixed(2)}, residual ${(y - pred).toFixed(2)}`);
});
console.log(`R^2 = 1 - ${ssRes.toFixed(2)} / ${ssTot.toFixed(2)} = ${(1 - ssRes / ssTot).toFixed(4)}`);
''', ts=r'''
const hours: number[] = [1, 2, 3, 4, 5, 6];
const score: number[] = [52, 55, 61, 66, 70, 78];
const n: number = hours.length;
const mx: number = hours.reduce((s, v) => s + v, 0) / n, my: number = score.reduce((s, v) => s + v, 0) / n;
const sxy: number = hours.reduce((s, x, i) => s + (x - mx) * (score[i] - my), 0);
const sxx: number = hours.reduce((s, x) => s + (x - mx) ** 2, 0);
const slope: number = sxy / sxx;          // least squares slope = covariance / variance of x
const intercept: number = my - slope * mx;   // the line passes through the point of means
console.log(`score = ${intercept.toFixed(2)} + ${slope.toFixed(2)} x hours`);
let ssRes: number = 0, ssTot: number = 0;
hours.forEach((x, i) => {
  const y: number = score[i], pred: number = intercept + slope * x;
  ssRes += (y - pred) ** 2;               // what the line misses
  ssTot += (y - my) ** 2;                 // total spread around the mean
  console.log(`x = ${x}: actual ${y}, predicted ${pred.toFixed(2)}, residual ${(y - pred).toFixed(2)}`);
});
console.log(`R^2 = 1 - ${ssRes.toFixed(2)} / ${ssTot.toFixed(2)} = ${(1 - ssRes / ssTot).toFixed(4)}`);
''', java=r'''
public class Regression {
    public static void main(String[] args) {
        int[] hours = {1, 2, 3, 4, 5, 6};
        int[] score = {52, 55, 61, 66, 70, 78};
        int n = hours.length;
        double mx = 0, my = 0;
        for (int i = 0; i < n; i++) { mx += (double) hours[i] / n; my += (double) score[i] / n; }
        double sxy = 0, sxx = 0;
        for (int i = 0; i < n; i++) { sxy += (hours[i] - mx) * (score[i] - my); sxx += (hours[i] - mx) * (hours[i] - mx); }
        double slope = sxy / sxx;                 // least squares slope = covariance / variance of x
        double intercept = my - slope * mx;       // the line passes through the point of means
        System.out.println(String.format("score = %.2f + %.2f x hours", intercept, slope));
        double ssRes = 0, ssTot = 0;
        for (int i = 0; i < n; i++) {
            double pred = intercept + slope * hours[i];
            ssRes += (score[i] - pred) * (score[i] - pred);   // what the line misses
            ssTot += (score[i] - my) * (score[i] - my);       // total spread around the mean
            System.out.println(String.format("x = %d: actual %d, predicted %.2f, residual %.2f", hours[i], score[i], pred, score[i] - pred));
        }
        System.out.println(String.format("R^2 = 1 - %.2f / %.2f = %.4f", ssRes, ssTot, 1 - ssRes / ssTot));
    }
}
''')

K.code('p_outlier', py=r'''
def median(v):                            # v must already be sorted
    m = len(v) // 2
    return v[m] if len(v) % 2 == 1 else (v[m - 1] + v[m]) / 2


data = sorted([15, 12, 18, 45, 14, 16, 19, 15])   # delivery times in minutes
half = len(data) // 2
q1, q3 = median(data[:half]), median(data[-half:])   # medians of the lower and upper halves
iqr = q3 - q1
low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr          # Tukey fences
print(f"mean {sum(data) / len(data):.2f}, median {median(data):.1f}")
print(f"Q1 {q1:.1f}, Q3 {q3:.1f}, IQR {iqr:.1f}")
print(f"fences {low:.1f} and {high:.1f}")
print("outliers:", ", ".join(str(x) for x in data if x < low or x > high))
''', js=r'''
function median(v) {                      // v must already be sorted
  const m = Math.floor(v.length / 2);
  return v.length % 2 === 1 ? v[m] : (v[m - 1] + v[m]) / 2;
}

const data = [15, 12, 18, 45, 14, 16, 19, 15].sort((a, b) => a - b);   // delivery times in minutes
const half = Math.floor(data.length / 2);
const q1 = median(data.slice(0, half)), q3 = median(data.slice(-half));   // medians of the lower and upper halves
const iqr = q3 - q1;
const low = q1 - 1.5 * iqr, high = q3 + 1.5 * iqr;   // Tukey fences
console.log(`mean ${(data.reduce((s, x) => s + x, 0) / data.length).toFixed(2)}, median ${median(data).toFixed(1)}`);
console.log(`Q1 ${q1.toFixed(1)}, Q3 ${q3.toFixed(1)}, IQR ${iqr.toFixed(1)}`);
console.log(`fences ${low.toFixed(1)} and ${high.toFixed(1)}`);
console.log("outliers:", data.filter(x => x < low || x > high).join(", "));
''', ts=r'''
function median(v: number[]): number {    // v must already be sorted
  const m: number = Math.floor(v.length / 2);
  return v.length % 2 === 1 ? v[m] : (v[m - 1] + v[m]) / 2;
}

const data: number[] = [15, 12, 18, 45, 14, 16, 19, 15].sort((a, b) => a - b);   // delivery times in minutes
const half: number = Math.floor(data.length / 2);
const q1: number = median(data.slice(0, half)), q3: number = median(data.slice(-half));   // medians of the lower and upper halves
const iqr: number = q3 - q1;
const low: number = q1 - 1.5 * iqr, high: number = q3 + 1.5 * iqr;   // Tukey fences
console.log(`mean ${(data.reduce((s, x) => s + x, 0) / data.length).toFixed(2)}, median ${median(data).toFixed(1)}`);
console.log(`Q1 ${q1.toFixed(1)}, Q3 ${q3.toFixed(1)}, IQR ${iqr.toFixed(1)}`);
console.log(`fences ${low.toFixed(1)} and ${high.toFixed(1)}`);
console.log("outliers:", data.filter(x => x < low || x > high).join(", "));
''', java=r'''
import java.util.Arrays;

public class PracticeOutlier {
    static double median(int[] v) {           // v must already be sorted
        int m = v.length / 2;
        return v.length % 2 == 1 ? v[m] : (v[m - 1] + v[m]) / 2.0;
    }

    public static void main(String[] args) {
        int[] data = {15, 12, 18, 45, 14, 16, 19, 15};   // delivery times in minutes
        Arrays.sort(data);
        int half = data.length / 2;
        double q1 = median(Arrays.copyOfRange(data, 0, half));   // medians of the lower and upper halves
        double q3 = median(Arrays.copyOfRange(data, data.length - half, data.length));
        double iqr = q3 - q1;
        double low = q1 - 1.5 * iqr, high = q3 + 1.5 * iqr;      // Tukey fences
        double sum = 0;
        for (int x : data) sum += x;
        System.out.println(String.format("mean %.2f, median %.1f", sum / data.length, median(data)));
        System.out.println(String.format("Q1 %.1f, Q3 %.1f, IQR %.1f", q1, q3, iqr));
        System.out.println(String.format("fences %.1f and %.1f", low, high));
        StringBuilder out = new StringBuilder();
        for (int x : data) if (x < low || x > high) out.append(out.length() > 0 ? ", " : "").append(x);
        System.out.println("outliers: " + out);
    }
}
''')

K.code('p_poll', py=r'''
from math import ceil, sqrt

n, yes = 1000, 540                        # 540 of 1000 people say yes
p = yes / n
se = sqrt(p * (1 - p) / n)                # standard error of a proportion
margin = 1.96 * se                        # 95% margin of error
print(f"estimate {p:.2f}, standard error {se:.5f}")
print(f"95% interval [{p - margin:.4f}, {p + margin:.4f}]")
print("majority?", "yes, the whole interval is above 0.5" if p - margin > 0.5 else "not sure")
need = ceil(1.96 ** 2 * 0.25 / 0.02 ** 2) # people needed for +/- 2% in the worst case p = 0.5
print(f"people needed for +/- 2%: {need}")
''', js=r'''
const n = 1000, yes = 540;                // 540 of 1000 people say yes
const p = yes / n;
const se = Math.sqrt(p * (1 - p) / n);    // standard error of a proportion
const margin = 1.96 * se;                 // 95% margin of error
console.log(`estimate ${p.toFixed(2)}, standard error ${se.toFixed(5)}`);
console.log(`95% interval [${(p - margin).toFixed(4)}, ${(p + margin).toFixed(4)}]`);
console.log("majority?", p - margin > 0.5 ? "yes, the whole interval is above 0.5" : "not sure");
const need = Math.ceil(1.96 ** 2 * 0.25 / 0.02 ** 2);   // people needed for +/- 2% in the worst case p = 0.5
console.log(`people needed for +/- 2%: ${need}`);
''', ts=r'''
const n: number = 1000, yes: number = 540;   // 540 of 1000 people say yes
const p: number = yes / n;
const se: number = Math.sqrt(p * (1 - p) / n);   // standard error of a proportion
const margin: number = 1.96 * se;         // 95% margin of error
console.log(`estimate ${p.toFixed(2)}, standard error ${se.toFixed(5)}`);
console.log(`95% interval [${(p - margin).toFixed(4)}, ${(p + margin).toFixed(4)}]`);
console.log("majority?", p - margin > 0.5 ? "yes, the whole interval is above 0.5" : "not sure");
const need: number = Math.ceil(1.96 ** 2 * 0.25 / 0.02 ** 2);   // people needed for +/- 2% in the worst case p = 0.5
console.log(`people needed for +/- 2%: ${need}`);
''', java=r'''
public class PracticePoll {
    public static void main(String[] args) {
        int n = 1000, yes = 540;                  // 540 of 1000 people say yes
        double p = (double) yes / n;
        double se = Math.sqrt(p * (1 - p) / n);   // standard error of a proportion
        double margin = 1.96 * se;                // 95% margin of error
        System.out.println(String.format("estimate %.2f, standard error %.5f", p, se));
        System.out.println(String.format("95%% interval [%.4f, %.4f]", p - margin, p + margin));
        System.out.println("majority? " + (p - margin > 0.5 ? "yes, the whole interval is above 0.5" : "not sure"));
        long need = (long) Math.ceil(Math.pow(1.96, 2) * 0.25 / Math.pow(0.02, 2));   // worst case p = 0.5
        System.out.println("people needed for +/- 2%: " + need);
    }
}
''')

K.code('p_ztest', py=r'''
from math import exp, sqrt
''' + ERF_PY + r'''

mu0, sigma = 250, 4                       # the machine should pour 250 ml, with SD 4 ml
n, xbar = 16, 248                         # 16 cups averaged 248 ml
se = sigma / sqrt(n)
z = (xbar - mu0) / se
p_value = 2 * phi(-abs(z))                # two sided test
print(f"standard error {se:.2f}, z = {z:.2f}")
print(f"p-value = {p_value:.4f}")
for alpha in (0.05, 0.01):
    verdict = "reject" if p_value < alpha else "keep"
    print(f"at alpha = {alpha}: {verdict} the claim that the mean is 250 ml")
''', js=ERF_JS + r'''
const mu0 = 250, sigma = 4;               // the machine should pour 250 ml, with SD 4 ml
const n = 16, xbar = 248;                 // 16 cups averaged 248 ml
const se = sigma / Math.sqrt(n);
const z = (xbar - mu0) / se;
const pValue = 2 * phi(-Math.abs(z));     // two sided test
console.log(`standard error ${se.toFixed(2)}, z = ${z.toFixed(2)}`);
console.log(`p-value = ${pValue.toFixed(4)}`);
for (const alpha of [0.05, 0.01]) {
  const verdict = pValue < alpha ? "reject" : "keep";
  console.log(`at alpha = ${alpha}: ${verdict} the claim that the mean is 250 ml`);
}
''', ts=ERF_TS + r'''
const mu0: number = 250, sigma: number = 4;   // the machine should pour 250 ml, with SD 4 ml
const n: number = 16, xbar: number = 248;     // 16 cups averaged 248 ml
const se: number = sigma / Math.sqrt(n);
const z: number = (xbar - mu0) / se;
const pValue: number = 2 * phi(-Math.abs(z));   // two sided test
console.log(`standard error ${se.toFixed(2)}, z = ${z.toFixed(2)}`);
console.log(`p-value = ${pValue.toFixed(4)}`);
for (const alpha of [0.05, 0.01]) {
  const verdict: string = pValue < alpha ? "reject" : "keep";
  console.log(`at alpha = ${alpha}: ${verdict} the claim that the mean is 250 ml`);
}
''', java=r'''
public class PracticeZTest {''' + ERF_JAVA + r'''
    public static void main(String[] args) {
        double mu0 = 250, sigma = 4;              // the machine should pour 250 ml, with SD 4 ml
        int n = 16;
        double xbar = 248;                        // 16 cups averaged 248 ml
        double se = sigma / Math.sqrt(n);
        double z = (xbar - mu0) / se;
        double pValue = 2 * phi(-Math.abs(z));    // two sided test
        System.out.println(String.format("standard error %.2f, z = %.2f", se, z));
        System.out.println(String.format("p-value = %.4f", pValue));
        for (double alpha : new double[]{0.05, 0.01}) {
            String verdict = pValue < alpha ? "reject" : "keep";
            System.out.println("at alpha = " + alpha + ": " + verdict + " the claim that the mean is 250 ml");
        }
    }
}
''')

K.code('p_samplesize', py=r'''
from math import ceil, sqrt

p1, p2 = 0.10, 0.12                       # today 10% buy, we hope the new page gets 12%
z_alpha, z_power = 1.96, 0.8416           # 5% false alarm rate (two sided) and 80% power
p_bar = (p1 + p2) / 2
spread = z_alpha * sqrt(2 * p_bar * (1 - p_bar)) + z_power * sqrt(p1 * (1 - p1) + p2 * (1 - p2))
n = spread ** 2 / (p2 - p1) ** 2             # visitors needed in EACH group
print(f"visitors per group: {ceil(n)}")
print(f"total visitors: {2 * ceil(n)}")
for lift in (0.01, 0.04):                 # smaller effects need far more data
    q = p1 + lift
    pb = (p1 + q) / 2
    t = z_alpha * sqrt(2 * pb * (1 - pb)) + z_power * sqrt(p1 * (1 - p1) + q * (1 - q))
    print(f"to detect {p1:.2f} -> {q:.2f}: {ceil(t ** 2 / lift ** 2)} per group")
''', js=r'''
const p1 = 0.10, p2 = 0.12;               // today 10% buy, we hope the new page gets 12%
const zAlpha = 1.96, zPower = 0.8416;     // 5% false alarm rate (two sided) and 80% power
const pBar = (p1 + p2) / 2;
const spread = zAlpha * Math.sqrt(2 * pBar * (1 - pBar)) + zPower * Math.sqrt(p1 * (1 - p1) + p2 * (1 - p2));
const n = spread ** 2 / (p2 - p1) ** 2;      // visitors needed in EACH group
console.log(`visitors per group: ${Math.ceil(n)}`);
console.log(`total visitors: ${2 * Math.ceil(n)}`);
for (const lift of [0.01, 0.04]) {        // smaller effects need far more data
  const q = p1 + lift;
  const pb = (p1 + q) / 2;
  const t = zAlpha * Math.sqrt(2 * pb * (1 - pb)) + zPower * Math.sqrt(p1 * (1 - p1) + q * (1 - q));
  console.log(`to detect ${p1.toFixed(2)} -> ${q.toFixed(2)}: ${Math.ceil(t ** 2 / lift ** 2)} per group`);
}
''', ts=r'''
const p1: number = 0.10, p2: number = 0.12;   // today 10% buy, we hope the new page gets 12%
const zAlpha: number = 1.96, zPower: number = 0.8416;   // 5% false alarm rate (two sided) and 80% power
const pBar: number = (p1 + p2) / 2;
const spread: number = zAlpha * Math.sqrt(2 * pBar * (1 - pBar)) + zPower * Math.sqrt(p1 * (1 - p1) + p2 * (1 - p2));
const n: number = spread ** 2 / (p2 - p1) ** 2;   // visitors needed in EACH group
console.log(`visitors per group: ${Math.ceil(n)}`);
console.log(`total visitors: ${2 * Math.ceil(n)}`);
for (const lift of [0.01, 0.04]) {        // smaller effects need far more data
  const q: number = p1 + lift;
  const pb: number = (p1 + q) / 2;
  const t: number = zAlpha * Math.sqrt(2 * pb * (1 - pb)) + zPower * Math.sqrt(p1 * (1 - p1) + q * (1 - q));
  console.log(`to detect ${p1.toFixed(2)} -> ${q.toFixed(2)}: ${Math.ceil(t ** 2 / lift ** 2)} per group`);
}
''', java=r'''
public class PracticeSampleSize {
    public static void main(String[] args) {
        double p1 = 0.10, p2 = 0.12;              // today 10% buy, we hope the new page gets 12%
        double zAlpha = 1.96, zPower = 0.8416;    // 5% false alarm rate (two sided) and 80% power
        double pBar = (p1 + p2) / 2;
        double spread = zAlpha * Math.sqrt(2 * pBar * (1 - pBar)) + zPower * Math.sqrt(p1 * (1 - p1) + p2 * (1 - p2));
        double n = spread * spread / ((p2 - p1) * (p2 - p1));   // visitors needed in EACH group
        System.out.println("visitors per group: " + (long) Math.ceil(n));
        System.out.println("total visitors: " + 2 * (long) Math.ceil(n));
        for (double lift : new double[]{0.01, 0.04}) {   // smaller effects need far more data
            double q = p1 + lift;
            double pb = (p1 + q) / 2;
            double t = zAlpha * Math.sqrt(2 * pb * (1 - pb)) + zPower * Math.sqrt(p1 * (1 - p1) + q * (1 - q));
            System.out.println(String.format("to detect %.2f -> %.2f: %d per group", p1, q, (long) Math.ceil(t * t / (lift * lift))));
        }
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('describe', '📋', 'Describing data: centre, spread and outliers', f'''
<p><b>Statistics</b> turns a pile of numbers into a few that tell the story. The first questions are always: where is the centre, and how spread out is the data?</p>
{fxs(fx('Mean', f'x̄ = {frac("x₁ + x₂ + … + xₙ", "n")}', 'Add everything and share it out equally. Pulled hard by extreme values.'),
         fx('Median', 'the middle value once sorted', 'With an even count, average the two middle values. Barely moved by extreme values.'),
         fx('Mode', 'the most common value', 'The only one that works for categories such as favourite colour.'))}
{fxs(fx('Sample variance and SD', f's² = {frac("Σ (xᵢ − x̄)²", "n − 1")} &nbsp;&nbsp; s = √s²', 'Dividing by n − 1 instead of n corrects for the fact that data sits closer to its own mean than to the true mean (Bessel correction).'),
         fx('Quartiles and IQR', 'IQR = Q3 − Q1', 'Q1 and Q3 are the medians of the lower and upper halves. The middle 50% of the data lies between them.'),
         fx('Outlier fences (Tukey)', 'below Q1 − 1.5 × IQR or above Q3 + 1.5 × IQR', 'A common rule of thumb for flagging values worth a closer look.'))}
{worked('Commute times for a week: 22, 25, 21, 24, 23, 25 and 60 minutes (one day the train broke down).', [
        'Sort: <span class="eq">21, 22, 23, 24, 25, 25, 60</span>',
        'Mean: <span class="eq">200 ÷ 7 ≈ 28.57</span> minutes. Median: the 4th value, <span class="eq">24</span>. Mode: <span class="eq">25</span>',
        'The single 60 dragged the mean up by about 5 minutes, but the median did not move.',
        'Without the 60, the mean is <span class="eq">140 ÷ 6 ≈ 23.33</span> and the SD drops from about <span class="eq">13.94</span> to <span class="eq">1.63</span>.'])}
{code('describe', 'Mean, median, mode and spread')}
{trick('For skewed data such as incomes or house prices, quote the median. The mean is pulled toward the long tail.')}
{life('News reports usually give the median house price, because a handful of mansions would push the mean far above what a typical home costs.')}
''', kw=['descriptive statistics', 'mean', 'median', 'mode', 'variance', 'standard deviation', 'quartile', 'IQR', 'outlier', 'bessel correction']),

    part('sampling', '🎣', 'Samples, bias and standard error', f'''
<p>We rarely measure everyone. The whole group we care about is the <b>population</b>. The part we actually measure is the <b>sample</b>. A number worked out from the sample (such as x̄) is a <b>statistic</b>, and it is our estimate of the population <b>parameter</b> (such as μ).</p>
{table(['', 'Population', 'Sample'], [
        ['size', 'N (often huge)', 'n'],
        ['mean', 'μ (unknown)', 'x̄ (we compute it)'],
        ['SD', 'σ', 's'],
        ['proportion', 'p', 'p̂'],
    ])}
{fxs(fx('Standard error of a mean', f'SE = {frac("s", "√n")}', 'How much x̄ would wobble from sample to sample (Chapter 10).'),
         fx('Standard error of a proportion', f'SE = √({frac("p̂ (1 − p̂)", "n")})', '540 yes out of 1000: √(0.54 × 0.46 ÷ 1000) ≈ 0.0158.'))}
<div class="warn">A bigger sample shrinks random error but does nothing about <b>bias</b>. Polling only people who answer landline phones, or training a face detector only on photos of one group of people, gives a confident answer to the wrong question.</div>
{table(['Kind of bias', 'What goes wrong', 'Example'], [
        ['selection bias', 'the sample is not like the population', 'surveying gym members about exercise habits'],
        ['survivorship bias', 'only the survivors are visible', 'studying only successful startups'],
        ['non-response bias', 'the people who answer differ from those who do not', 'a long email survey'],
        ['measurement bias', 'the tool itself is off', 'a scale that always reads 1 kg heavy'],
    ])}
{ml('Training data is a sample. If it does not look like the data the model will meet in use, accuracy measured on it will be too optimistic. This is called distribution shift, and it is a sampling problem before it is a modelling problem.')}
''', kw=['population', 'sample', 'statistic', 'parameter', 'standard error', 'sampling bias', 'selection bias', 'survivorship bias']),

    part('ci', '📏', 'Confidence intervals', f'''
<p>A single estimate such as "18.2 hours" hides its uncertainty. A <b>confidence interval</b> gives a range: estimate ± margin of error. A 95% confidence interval is built by a method that catches the true value in 95% of samples.</p>
{fx('Confidence interval for a mean', 'x̄ ± z* · SE &nbsp;&nbsp; with &nbsp;&nbsp; z* = 1.645 (90%), 1.96 (95%), 2.576 (99%)', 'For small samples with unknown σ, statisticians use a slightly wider t value instead of z*.')}
{viz('ci')}
{worked('36 phones last on average 18.2 hours with sample SD 2.4 hours. Give a 95% confidence interval.', [
        'Standard error: <span class="eq">SE = 2.4 ÷ √36 = 2.4 ÷ 6 = 0.4</span>',
        'Margin: <span class="eq">1.96 × 0.4 = 0.784</span>',
        'Interval: <span class="eq">18.2 ± 0.784 = [17.42, 18.98]</span> hours',
        'Wanting 99% confidence widens it to <span class="eq">18.2 ± 2.576 × 0.4 = 18.2 ± 1.03</span>. More confidence costs width.'])}
{code('confidence', '90%, 95% and 99% intervals')}
<div class="warn">"95% confident" does not mean there is a 95% chance that μ is inside this particular interval. μ is fixed, the interval is what varies. It means that 95% of intervals made this way catch μ. The animation shows exactly that: about 1 in 20 intervals miss.</div>
{trick('To halve the margin of error, you need four times as many people. That √n again.')}
''', kw=['confidence interval', 'margin of error', 'z star', '95 percent', 'interval estimate', 'coverage']),

    part('tests', '⚖️', 'Hypothesis tests and p-values', f'''
<p>A <b>hypothesis test</b> asks whether the data is surprising enough to doubt a default claim. The default, "nothing special is going on", is the <b>null hypothesis H₀</b>. The claim we are testing for is the <b>alternative H₁</b>.</p>
{fxs(fx('Test statistic (z-test for a mean)', f'z = {frac("x̄ − μ₀", "σ ÷ √n")}', 'How many standard errors the sample mean is from the value the null claims.'),
         fx('p-value', 'p = P(a result at least this extreme | H₀ is true)', 'Small p means the data would be rare if H₀ were true. Reject H₀ when p < α, usually α = 0.05.'))}
{worked('A coffee machine should pour 250 ml (σ = 4 ml). 16 cups average 248 ml. Is the machine off?', [
        'H₀: <span class="eq">μ = 250</span>. H₁: <span class="eq">μ ≠ 250</span> (two sided)',
        'Standard error: <span class="eq">4 ÷ √16 = 4 ÷ 4 = 1</span> ml',
        'Test statistic: <span class="eq">z = (248 − 250) ÷ 1 = −2</span>',
        'Two sided p-value: <span class="eq">2 × P(Z ≤ −2) ≈ 2 × 0.0228 = 0.0455</span>',
        'At α = 0.05, <span class="eq">0.0455 < 0.05</span>, so reject H₀. At the stricter α = 0.01 we would not.'])}
{table(['', 'H₀ really true', 'H₀ really false'], [
        ['<b>Reject H₀</b>', 'Type I error (false positive), chance α', 'correct, chance = power'],
        ['<b>Keep H₀</b>', 'correct', 'Type II error (false negative), chance β'],
    ])}
<div class="warn">A p-value is NOT the probability that H₀ is true. And "not significant" does not prove there is no effect. It only says this data was not enough to tell.</div>
{trick('If p is low, the null must go. But statistically significant is not the same as important: with a million users, a 0.01% difference can be significant and still not worth anything.')}
''', kw=['hypothesis test', 'null hypothesis', 'alternative hypothesis', 'p-value', 'significance level', 'type I error', 'type II error', 'power', 'z test']),

    part('ab', '🆎', 'A/B testing', f'''
<p>An <b>A/B test</b> is a hypothesis test that companies run every day. Visitors are split at random between the current version A and a new version B, and we compare a rate such as the share who buy.</p>
{fxs(fx('Pooled rate', f'p̂ = {frac("buys A + buys B", "visitors A + visitors B")}', 'Under H₀ both pages share one true rate, so we pool the data to estimate it.'),
         fx('Two proportion z-test', f'z = {frac("p̂<sub>B</sub> − p̂<sub>A</sub>", "√(p̂(1 − p̂)(1/n<sub>A</sub> + 1/n<sub>B</sub>))")}', 'Then the p-value comes from the normal curve, as before.'))}
{viz('abtest')}
{worked('Page A: 200 buys from 2000 visitors. Page B: 250 buys from 2000. Is B really better?', [
        'Rates: <span class="eq">p̂A = 0.100</span> and <span class="eq">p̂B = 0.125</span>, a lift of <span class="eq">0.025</span>',
        'Pooled rate: <span class="eq">450 ÷ 4000 = 0.1125</span>',
        'Standard error: <span class="eq">√(0.1125 × 0.8875 × (1/2000 + 1/2000)) ≈ 0.00999</span>',
        '<span class="eq">z = 0.025 ÷ 0.00999 ≈ 2.50</span>, two sided <span class="eq">p ≈ 0.0124</span>',
        'p < 0.05, so the lift is statistically significant. Ship B (if 2.5 points is worth the cost).'])}
{code('ab_test', 'A two proportion z-test')}
<div class="warn">Decide the sample size before the test and do not stop the moment p dips below 0.05. Peeking every day and stopping at the first "win" makes false positives far more common than 5%.</div>
{ml('Comparing two models works the same way. If model B beats model A by one point of accuracy on a test set, a test like this tells you whether that gap is bigger than what random luck in the test set could produce.')}
''', kw=['a/b test', 'conversion rate', 'two proportion z test', 'pooled proportion', 'peeking', 'sample size', 'online experiment']),

    part('mle', '🎯', 'Maximum likelihood estimation', f'''
<p><b>Maximum likelihood</b> answers "which parameter value makes the data we saw most probable?" It is the idea behind how most machine learning models are trained.</p>
{fxs(fx('Likelihood of coin flips', 'L(p) = pʰ (1 − p)ⁿ⁻ʰ', 'h heads out of n flips, if the chance of heads is p.'),
         fx('Log-likelihood', 'ℓ(p) = h log p + (n − h) log(1 − p)', 'Same best p, but sums instead of products: easier calculus, no underflow.'),
         fx('The answer', f'p̂ = {frac("h", "n")}', 'Set the derivative h/p − (n − h)/(1 − p) to 0 and solve.'))}
{viz('mle')}
{worked('7 heads in 10 flips. Show that the best p is 0.7.', [
        'Log-likelihood: <span class="eq">ℓ(p) = 7 log p + 3 log(1 − p)</span>',
        'Derivative: <span class="eq">ℓ′(p) = 7/p − 3/(1 − p)</span>',
        'Set to zero: <span class="eq">7/p = 3/(1 − p)</span>, so <span class="eq">7(1 − p) = 3p</span>, so <span class="eq">7 = 10p</span>',
        '<span class="eq">p̂ = 0.7</span>. The maximum likelihood answer is just the share of heads, as common sense says.'])}
{code('mle', 'Scanning the log-likelihood')}
{table(['Model', 'What maximum likelihood gives'], [
        ['coin (Bernoulli)', 'p̂ = share of successes'],
        ['normal data', 'μ̂ = sample mean, σ̂² = average squared deviation (divides by n)'],
        ['linear regression with normal noise', 'minimise the sum of squared errors (least squares)'],
        ['logistic regression', 'minimise log loss, also called cross entropy (Chapter 12)'],
    ])}
{ml('Training a classifier by minimising cross entropy loss IS maximum likelihood. Every time you call fit, an optimiser like Adam (Chapter 8) climbs a log-likelihood surface just like the one in the animation, only in millions of dimensions.')}
''', kw=['maximum likelihood', 'MLE', 'likelihood', 'log-likelihood', 'estimator', 'cross entropy', 'least squares']),

    part('regress', '📈', 'Regression, R² and the bias and variance trade-off', f'''
<p><b>Linear regression</b> fits the straight line ŷ = a + b x that makes the squared vertical misses (residuals) as small as possible. It is both a statistics tool and the simplest machine learning model.</p>
{fxs(fx('Least squares line', f'b = {frac("Σ (xᵢ − x̄)(yᵢ − ȳ)", "Σ (xᵢ − x̄)²")} &nbsp;&nbsp; a = ȳ − b x̄', 'Slope = covariance ÷ variance of x. The line always passes through the point (x̄, ȳ).'),
         fx('R² (coefficient of determination)', f'R² = 1 − {frac("SS<sub>res</sub>", "SS<sub>tot</sub>")} = 1 − {frac("Σ (yᵢ − ŷᵢ)²", "Σ (yᵢ − ȳ)²")}', 'The share of the variation in y that the line explains. For a straight line fit, R² = r².'))}
{worked('Hours studied 1 to 6, scores 52, 55, 61, 66, 70, 78. Fit the line.', [
        'Means: <span class="eq">x̄ = 3.5</span>, <span class="eq">ȳ ≈ 63.67</span>',
        '<span class="eq">Σ(x − x̄)(y − ȳ) = 90</span> and <span class="eq">Σ(x − x̄)² = 17.5</span>, so <span class="eq">b = 90 ÷ 17.5 ≈ 5.14</span>',
        '<span class="eq">a = 63.67 − 5.14 × 3.5 ≈ 45.67</span>, so <span class="eq">ŷ = 45.67 + 5.14 x</span>',
        'Leftover error <span class="eq">SS<sub>res</sub> ≈ 6.48</span> out of <span class="eq">SS<sub>tot</sub> ≈ 469.33</span>, so <span class="eq">R² ≈ 1 − 0.0138 = 0.986</span>'])}
{code('regression', 'Least squares, residuals and R²')}
{fx('Bias and variance decomposition', 'expected test error = bias² + variance + noise', 'Bias: errors from a model too simple to capture the pattern. Variance: errors from a model so flexible it chases the random quirks of its training sample.')}
{table(['', 'Too simple (high bias)', 'Just right', 'Too flexible (high variance)'], [
        ['training error', 'high', 'low', 'very low'],
        ['test error', 'high', 'low', 'high'],
        ['name', 'underfitting', 'good fit', 'overfitting'],
        ['fix', 'more features, bigger model', 'keep it', 'more data, regularisation, simpler model'],
    ])}
{trick('Always judge a model on data it has never seen. A high R² on the training data alone says little about the future.')}
''', kw=['linear regression', 'least squares', 'residual', 'R squared', 'coefficient of determination', 'bias variance tradeoff', 'overfitting', 'underfitting']),
]

INFO = {
    'title': 'Statistics turns samples into honest conclusions',
    'panels': [
        {'s': [['e', '📋'], ['t', 'mean, median, s', {'b': 1}]], 'h': 'Describe', 't': 'Centre and spread.', 'm': 'Median resists outliers.'},
        {'s': [['e', '📏'], ['t', 'x̄ ± 1.96 SE', {'b': 1}]], 'h': 'Interval', 't': '95% of such intervals catch μ.', 'more': 'Width shrinks with √n.'},
        {'s': [['e', '⚖️'], ['t', 'p < α → reject H₀', {'b': 1}]], 'h': 'Test', 't': 'Is the data surprising?', 'more': 'p is not P(H₀ true).'},
        {'s': [['e', '🎯'], ['t', 'maximise log L', {'b': 1}]], 'h': 'Fit', 't': 'Maximum likelihood.', 'more': 'This is how models train.'},
    ],
    'remember': 'Describe data with the mean or median and the SD or IQR. A sample estimate has standard error s ÷ √n, and a 95% interval is the estimate ± 1.96 SE. A p-value is the chance of data this extreme if H₀ were true. Reject H₀ when p < α. A/B tests compare two rates with a z-test. Maximum likelihood picks the parameter that makes the data most probable. Least squares gives slope = Cov ÷ Var(x), and R² is the share of variance explained.',
}
INFO['panels'][0]['more'] = INFO['panels'][0].pop('m')

REAL = [
    ['🗳️', 'Election polls', 'A poll of about 1000 people has a margin of error near ±3 points, which is why close races are reported as "too close to call".'],
    ['🛒', 'Online shops', 'Large websites run many A/B tests at once on layouts, prices and wording, and keep only the changes that pass a significance test.'],
    ['💊', 'Medicine trials', 'New drugs are approved only after randomised trials show an effect that is both statistically significant and large enough to matter for patients.'],
]

K.say('top', 'Welcome',
      'Statistics turns a sample into honest conclusions about a whole population. You will describe data, catch the true mean with confidence intervals, run hypothesis tests and A/B tests, find parameters by maximum likelihood, and fit a regression line.',
      'Statistics एक sample से पूरी population के बारे में ईमानदार निष्कर्ष निकालता है। आप data का वर्णन करेंगे, confidence intervals से असली mean पकड़ेंगे, hypothesis tests और A/B tests चलाएँगे, maximum likelihood से parameters निकालेंगे, और regression line बनाएँगे।',
      'Statistics sample ನಿಂದ population ಬಗ್ಗೆ ನಿಷ್ಕರ್ಷೆ ಕೊಡುತ್ತದೆ. Confidence intervals, tests, A/B tests, maximum likelihood ಮತ್ತು regression ಕಲಿಯುತ್ತೀರಿ.',
      'Statistics sample ରୁ population ବିଷୟରେ ସିଦ୍ଧାନ୍ତ ଦିଏ। Confidence intervals, tests, A/B tests, maximum likelihood ଓ regression ଶିଖିବେ।',
      'الإحصاء يحوّل العينة إلى استنتاجات صادقة عن المجتمع كله. ستصف البيانات، وتلتقط المتوسط الحقيقي بفترات الثقة، وتجري اختبارات الفرضيات واختبارات A/B، وتجد المعاملات بالأرجحية العظمى، وترسم خط انحدار.',
      'Statistik macht aus einer Stichprobe ehrliche Aussagen über die ganze Grundgesamtheit. Du beschreibst Daten, fängst den wahren Mittelwert mit Konfidenzintervallen, führst Hypothesentests und A/B Tests durch, findest Parameter mit Maximum Likelihood und passt eine Regressionsgerade an.')
K.say('describe', 'Describing data',
      'The mean adds everything and shares it out, the median is the middle value, and the mode is the most common one. One extreme value can drag the mean a long way while the median stays put. The standard deviation and the interquartile range describe the spread.',
      'Mean सब जोड़कर बराबर बाँटता है, median बीच का मान है, और mode सबसे आम मान। एक extreme मान mean को बहुत खींच सकता है जबकि median वहीं रहता है। Standard deviation और interquartile range फैलाव बताते हैं।',
      'Mean ಸರಾಸರಿ, median ಮಧ್ಯದ ಮೌಲ್ಯ, mode ಹೆಚ್ಚು ಬರುವುದು. Outlier mean ಅನ್ನು ಎಳೆಯುತ್ತದೆ, median ಅಲ್ಲ.',
      'Mean ହାରାହାରି, median ମଝି ମୂଲ୍ୟ, mode ଅଧିକ ଆସୁଥିବା। Outlier mean କୁ ଟାଣେ, median କୁ ନୁହେଁ।',
      'المتوسط يجمع كل شيء ويقسمه بالتساوي، والوسيط هو القيمة الوسطى، والمنوال الأكثر تكرارًا. قيمة متطرفة واحدة قد تسحب المتوسط بعيدًا بينما يبقى الوسيط مكانه. والانحراف المعياري والمدى الربيعي يصفان الانتشار.',
      'Der Mittelwert addiert alles und verteilt es gleichmäßig, der Median ist der mittlere Wert, der Modus der häufigste. Ein Ausreißer kann den Mittelwert weit verschieben, während der Median bleibt. Standardabweichung und Interquartilsabstand beschreiben die Streuung.')
K.say('sampling', 'Samples and bias',
      'A sample is the part of the population we measure. Its statistics estimate the population parameters, with a standard error that shrinks as the sample grows. But a bigger sample cannot fix bias. If the sample is not like the population, the answer is confidently wrong.',
      'Sample population का वह हिस्सा है जिसे हम मापते हैं। उसके statistics population parameters का अनुमान देते हैं, और standard error sample बढ़ने पर घटता है। पर बड़ा sample bias ठीक नहीं करता।',
      'Sample population ನ ಭಾಗ. ದೊಡ್ಡ sample ಕೂಡ bias ಸರಿಪಡಿಸುವುದಿಲ್ಲ.',
      'Sample population ର ଅଂଶ। ବଡ଼ sample ମଧ୍ୟ bias ଠିକ୍ କରେ ନାହିଁ।',
      'العينة هي الجزء الذي نقيسه من المجتمع، وإحصاءاتها تقدّر معاملات المجتمع بخطأ معياري يصغر كلما كبرت العينة. لكن العينة الأكبر لا تصلح التحيز، فإن لم تشبه العينة المجتمع كان الجواب خاطئًا بثقة.',
      'Eine Stichprobe ist der Teil der Grundgesamtheit, den wir messen. Ihre Kennzahlen schätzen die Parameter, mit einem Standardfehler, der mit der Größe schrumpft. Eine größere Stichprobe behebt aber keine Verzerrung. Ist sie nicht repräsentativ, ist die Antwort selbstsicher falsch.')
K.say('ci', 'Confidence intervals',
      'A confidence interval is the estimate plus or minus a margin of error. For ninety five percent, the margin is one point nine six standard errors. Watch the animation: about nineteen intervals in twenty catch the true mean, and the misses show up in red.',
      'Confidence interval अनुमान धन या ऋण margin of error है। पंचानवे प्रतिशत के लिए margin एक दशमलव नौ छह standard errors है। Animation देखें: बीस में से लगभग उन्नीस intervals असली mean पकड़ते हैं, और चूकने वाले लाल दिखते हैं।',
      'Confidence interval ಅಂದಾಜು ಪ್ಲಸ್ ಮೈನಸ್ margin. 95% ಗೆ 1.96 standard errors. ಇಪ್ಪತ್ತರಲ್ಲಿ ಸುಮಾರು ಹತ್ತೊಂಬತ್ತು ಹಿಡಿಯುತ್ತವೆ.',
      'Confidence interval ଅନୁମାନ ପ୍ଲସ୍ ମାଇନସ୍ margin। 95% ପାଇଁ 1.96 standard errors। କୋଡ଼ିଏରୁ ପ୍ରାୟ ଉଣେଇଶି ଧରନ୍ତି।',
      'فترة الثقة هي التقدير زائدًا أو ناقصًا هامش الخطأ. ولخمسة وتسعين بالمئة يكون الهامش واحدًا وستة وتسعين بالمئة من الخطأ المعياري. شاهد الحركة: نحو تسع عشرة فترة من كل عشرين تلتقط المتوسط الحقيقي، والفترات المخطئة تظهر بالأحمر.',
      'Ein Konfidenzintervall ist die Schätzung plus oder minus eine Fehlermarge. Für fünfundneunzig Prozent ist die Marge eins Komma neun sechs Standardfehler. Sieh hin: etwa neunzehn von zwanzig Intervallen fangen den wahren Mittelwert, die Fehlschläge erscheinen rot.')
K.say('tests', 'Hypothesis tests',
      'A hypothesis test asks whether the data would be surprising if nothing special were going on. The p value is the chance of a result at least this extreme under the null hypothesis. If it is below the chosen level, usually five percent, we reject the null. A p value is not the chance that the null is true.',
      'Hypothesis test पूछता है कि अगर कुछ खास न हो रहा हो तो क्या data चौंकाने वाला होगा। P value null hypothesis के तहत कम से कम इतने extreme परिणाम की संभावना है। अगर यह चुने गए स्तर से कम है, आमतौर पर पाँच प्रतिशत, तो null reject करते हैं।',
      'Hypothesis test data ಆಶ್ಚರ್ಯಕರವೇ ಎಂದು ಕೇಳುತ್ತದೆ. P value ಐದು ಶೇಕಡಕ್ಕಿಂತ ಕಡಿಮೆ ಇದ್ದರೆ null reject.',
      'Hypothesis test data ଆଶ୍ଚର୍ଯ୍ୟଜନକ କି ପଚାରେ। P value ପାଞ୍ଚ ପ୍ରତିଶତରୁ କମ୍ ହେଲେ null reject।',
      'اختبار الفرضية يسأل هل ستكون البيانات مفاجئة لو لم يحدث شيء مميز. والقيمة الاحتمالية هي فرصة نتيجة بهذا التطرف على الأقل في ظل فرضية العدم. فإن كانت أقل من المستوى المختار، عادة خمسة بالمئة، نرفض العدم. وهي ليست احتمال صحة العدم.',
      'Ein Hypothesentest fragt, ob die Daten überraschend wären, wenn nichts Besonderes los wäre. Der p Wert ist die Chance auf ein mindestens so extremes Ergebnis unter der Nullhypothese. Liegt er unter dem gewählten Niveau, meist fünf Prozent, verwerfen wir die Nullhypothese. Er ist nicht die Wahrscheinlichkeit, dass sie stimmt.')
K.say('ab', 'A B testing',
      'An A B test splits visitors at random between two versions and compares their rates. Pool the data to get the shared rate, divide the difference by its standard error to get z, and read the p value from the normal curve. Move the sliders to see how many visitors a small lift needs.',
      'A B test visitors को random रूप से दो versions में बाँटकर उनकी दरें मिलाता है। Data को pool करके साझा दर निकालें, अंतर को standard error से भाग देकर z पाएँ, और normal curve से p value पढ़ें। Sliders से देखें कि छोटे lift के लिए कितने visitors चाहिए।',
      'A B test visitors ಅನ್ನು ಎರಡು versions ಗೆ ಹಂಚುತ್ತದೆ. Z ಮತ್ತು p value ಲೆಕ್ಕ ಹಾಕಿ.',
      'A B test visitors କୁ ଦୁଇ versions ରେ ବାଣ୍ଟେ। Z ଓ p value ହିସାବ କରନ୍ତୁ।',
      'اختبار A B يوزع الزوار عشوائيًا بين نسختين ويقارن معدليهما. اجمع البيانات لتقدير المعدل المشترك، واقسم الفرق على خطئه المعياري لتحصل على z، ثم اقرأ القيمة الاحتمالية من المنحنى الطبيعي. حرك المنزلقات لترى كم زائرًا يحتاج تحسن صغير.',
      'Ein A B Test teilt Besucher zufällig auf zwei Versionen auf und vergleicht ihre Raten. Fasse die Daten zur gemeinsamen Rate zusammen, teile den Unterschied durch seinen Standardfehler, um z zu erhalten, und lies den p Wert an der Normalverteilung ab. Verschiebe die Regler und sieh, wie viele Besucher ein kleiner Effekt braucht.')
K.say('mle', 'Maximum likelihood',
      'Maximum likelihood picks the parameter that makes the observed data most probable. Work with the log likelihood, because sums are easier than products. For coin flips the answer is simply the share of heads. Press play to climb the curve to its peak.',
      'Maximum likelihood वह parameter चुनता है जिससे देखा गया data सबसे संभावित हो। Log likelihood से काम करें, क्योंकि जोड़ गुणा से आसान है। Coin flips के लिए उत्तर बस heads का हिस्सा है। Play दबाकर curve की चोटी तक चढ़ें।',
      'Maximum likelihood data ಹೆಚ್ಚು ಸಂಭವನೀಯವಾಗುವ parameter ಆರಿಸುತ್ತದೆ. Coin ಗೆ heads ನ ಪಾಲು.',
      'Maximum likelihood data ଅଧିକ ସମ୍ଭାବ୍ୟ ହେଉଥିବା parameter ବାଛେ। Coin ପାଇଁ heads ର ଅଂଶ।',
      'الأرجحية العظمى تختار المعامل الذي يجعل البيانات المرصودة أكثر احتمالًا. اعمل مع لوغاريتم الأرجحية لأن الجمع أسهل من الضرب. ولرميات العملة يكون الجواب ببساطة نسبة الصور. اضغط تشغيل لتصعد المنحنى إلى قمته.',
      'Maximum Likelihood wählt den Parameter, der die beobachteten Daten am wahrscheinlichsten macht. Arbeite mit der Log Likelihood, denn Summen sind leichter als Produkte. Bei Münzwürfen ist die Antwort einfach der Anteil Kopf. Drücke Play und steige auf den Gipfel der Kurve.')
K.say('regress', 'Regression and overfitting',
      'Least squares fits the line that makes the squared misses smallest. The slope is covariance over the variance of x, and R squared is the share of variation the line explains. Too simple a model underfits, too flexible a model overfits, so always test on data the model has not seen.',
      'Least squares वह रेखा बनाता है जिससे वर्ग गलतियाँ सबसे कम हों। Slope covariance बटा x का variance है, और R squared वह हिस्सा है जो रेखा समझाती है। बहुत सरल model underfit, बहुत लचीला overfit करता है, इसलिए नए data पर test करें।',
      'Least squares ವರ್ಗ ದೋಷ ಕಡಿಮೆ ಮಾಡುವ ರೇಖೆ. R squared ವಿವರಿಸಿದ ಪಾಲು. ಹೊಸ data ಮೇಲೆ test ಮಾಡಿ.',
      'Least squares ବର୍ଗ ତ୍ରୁଟି କମ୍ କରୁଥିବା ରେଖା। R squared ବୁଝାଇଥିବା ଅଂଶ। ନୂଆ data ରେ test କରନ୍ତୁ।',
      'المربعات الصغرى ترسم الخط الذي يجعل مربعات الأخطاء أصغر ما يمكن. الميل هو التغاير على تباين x، ومعامل التحديد هو نسبة التباين التي يفسرها الخط. النموذج البسيط جدًا يقصر، والمرن جدًا يفرط في الملاءمة، فاختبر دائمًا على بيانات لم يرها النموذج.',
      'Die Methode der kleinsten Quadrate legt die Gerade mit den kleinsten quadrierten Abweichungen. Die Steigung ist Kovarianz durch Varianz von x, und R Quadrat ist der erklärte Anteil der Streuung. Zu einfache Modelle sind unterangepasst, zu flexible überangepasst, also teste immer mit ungesehenen Daten.')
K.say('practice', 'Practice',
      'Practice time. Find outliers with the interquartile range, read a poll, test a coffee machine, and work out how many visitors an A B test needs.',
      'अभ्यास का समय। Interquartile range से outliers ढूँढें, एक poll पढ़ें, coffee machine का test करें, और A B test के लिए visitors की संख्या निकालें।',
      'ಅಭ್ಯಾಸದ ಸಮಯ. Outliers, poll, coffee machine test ಮತ್ತು A B test sample size.',
      'ଅଭ୍ୟାସ ସମୟ। Outliers, poll, coffee machine test ଓ A B test sample size।',
      'وقت التدريب. اكتشف القيم الشاذة بالمدى الربيعي، واقرأ استطلاعًا، واختبر آلة قهوة، واحسب عدد الزوار الذي يحتاجه اختبار A B.',
      'Zeit zum Üben. Finde Ausreißer mit dem Interquartilsabstand, lies eine Umfrage, teste einen Kaffeeautomaten und berechne, wie viele Besucher ein A B Test braucht.')

# ---------------------------------------------------------------- practice
K.practice('outlier', 'e', 'Spot the outlier', 'p_outlier',
           '<p>Delivery times in minutes: 15, 12, 18, 45, 14, 16, 19, 15. Find the mean, the median, Q1, Q3, the IQR, the outlier fences and any outliers.</p>',
           'mean 19.25, median 15.5\nQ1 14.5, Q3 18.5, IQR 4.0\nfences 8.5 and 24.5\noutliers: 45',
           'Sort first. Q1 is the median of the lower four values and Q3 the median of the upper four.',
           '<p>Sorted: 12, 14, 15, 15, 16, 18, 19, 45. The sum is 154, so the mean is 154 ÷ 8 = 19.25. The median is (15 + 16) ÷ 2 = 15.5. Lower half 12, 14, 15, 15 gives Q1 = 14.5. Upper half 16, 18, 19, 45 gives Q3 = 18.5. IQR = 4, so the fences are 14.5 − 6 = 8.5 and 18.5 + 6 = 24.5. Only 45 lies outside. Notice how it pulls the mean almost 4 minutes above the median.</p>',
           'O(n log n)', 'O(n)')
K.practice('poll', 'm', 'Reading a poll', 'p_poll',
           '<p>540 out of 1000 people support a plan. Give the estimate, its standard error and a 95% confidence interval. Can we say a majority supports it? How many people would a ±2% margin need?</p>',
           'estimate 0.54, standard error 0.01576\n95% interval [0.5091, 0.5709]\nmajority? yes, the whole interval is above 0.5\npeople needed for +/- 2%: 2401',
           'SE of a proportion is √(p̂(1 − p̂) ÷ n). For the sample size, use the worst case p = 0.5.',
           '<p>p̂ = 0.54. SE = √(0.54 × 0.46 ÷ 1000) = √0.0002484 ≈ 0.01576. The margin is 1.96 × 0.01576 ≈ 0.0309, so the interval is 0.54 ± 0.031 = [0.509, 0.571]. Even the bottom of the interval is above 0.5, so a majority is supported at 95% confidence. For a ±2% margin: 1.96 × √(0.25 ÷ n) = 0.02 gives n = 1.96² × 0.25 ÷ 0.02² = 2401 people.</p>',
           'O(1)', 'O(1)')
K.practice('ztest', 'h', 'Is the coffee machine off?', 'p_ztest',
           '<p>A machine should pour 250 ml with SD 4 ml. A sample of 16 cups averages 248 ml. Run a two sided z-test and decide at α = 0.05 and α = 0.01.</p>',
           'standard error 1.00, z = -2.00\np-value = 0.0455\nat alpha = 0.05: reject the claim that the mean is 250 ml\nat alpha = 0.01: keep the claim that the mean is 250 ml',
           'z = (x̄ − μ₀) ÷ (σ ÷ √n). Two sided p-value = 2 × P(Z ≤ −|z|).',
           '<p>SE = 4 ÷ √16 = 1 ml, so z = (248 − 250) ÷ 1 = −2. The chance of a z at least 2 away from 0 in either direction is 2 × 0.02275 ≈ 0.0455. That is below 0.05, so at the usual level we reject the claim. It is above 0.01, so a stricter tester would keep it. The same data can give different verdicts, which is why α must be chosen before looking.</p>',
           'O(1)', 'O(1)')
K.practice('samplesize', 'x', 'How big should an A/B test be?', 'p_samplesize',
           '<p>10% of visitors buy today. You want an A/B test that detects a rise to 12% with α = 0.05 (two sided) and 80% power. How many visitors does each group need? How does that change for lifts of 1 and 4 points?</p>',
           'visitors per group: 3841\ntotal visitors: 7682\nto detect 0.10 -> 0.11: 14751 per group\nto detect 0.10 -> 0.14: 1035 per group',
           'n = (z<sub>α/2</sub> √(2 p̄(1 − p̄)) + z<sub>power</sub> √(p₁(1 − p₁) + p₂(1 − p₂)))² ÷ (p₂ − p₁)² with z values 1.96 and 0.8416.',
           '<p>p̄ = 0.11. First term: 1.96 × √(2 × 0.11 × 0.89) = 1.96 × 0.4425 ≈ 0.8673. Second term: 0.8416 × √(0.09 + 0.1056) = 0.8416 × 0.4423 ≈ 0.3722. Add: 1.2395, square: 1.5364, divide by 0.02² = 0.0004: about 3841 visitors per group. Halving the lift to 1 point needs nearly 4 times as many (14751), and a 4 point lift needs only about 1035. The required sample grows with 1 ÷ (effect size)².</p>',
           'O(1)', 'O(1)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What is the median of 3, 9, 4, 7, 5?', ['5', '5.6', '4', '7'], 0, 'Sort first.', 'Sorted 3, 4, 5, 7, 9: the middle value is 5.')
K.quiz('e', 'Which summary is pulled the most by one extreme value?', ['median', 'mean', 'mode', 'interquartile range'], 1, 'Which one uses every value\'s size?', 'The mean adds every value, so one huge value moves it a lot.')
K.quiz('e', 'What is the mode of 2, 3, 3, 5, 7?', ['3', '4', '5', '2'], 0, 'Most common value.', '3 appears twice, the others once.')
K.quiz('e', 'A sample is…', ['the whole group you care about', 'the part of the population you actually measure', 'the average of the data', 'a type of chart'], 1, 'Population versus sample.', 'We measure a sample to learn about the population.')
K.quiz('m', 'Why does the sample variance divide by n − 1?', ['to make it bigger for no reason', 'data sits closer to its own mean than to the true mean, so dividing by n would underestimate the spread', 'it is a typing mistake', 'to remove outliers'], 1, 'Bessel correction.', 'Using x̄ instead of μ makes the squared deviations a little too small on average, and n − 1 corrects that.')
K.quiz('m', 'Which z value gives a 95% confidence interval?', ['1.645', '1.96', '2.576', '3'], 1, '95% of a normal lies within ±1.96 SD.', '1.645 is for 90% and 2.576 for 99%.')
K.quiz('m', 'A p-value is…', ['the probability the null hypothesis is true', 'the probability of data at least this extreme if the null hypothesis were true', 'the probability the alternative is true', 'the size of the effect'], 1, 'It is computed assuming H₀.', 'It measures how surprising the data is under H₀.')
K.quiz('m', 'A Type I error is…', ['rejecting a null hypothesis that is actually true (a false positive)', 'keeping a null hypothesis that is false', 'a bug in the code', 'a large p-value'], 0, 'False alarm.', 'Its chance is α. Missing a real effect is a Type II error.')
K.quiz('m', 'If you collect 4 times as much data, a confidence interval becomes…', ['half as wide', 'a quarter as wide', 'twice as wide', 'the same width'], 0, 'Width is proportional to 1 ÷ √n.', '√4 = 2, so the width halves.')
K.quiz('h', 'A test gives p = 0.3. What can you conclude?', ['the null hypothesis is proven true', 'there is not enough evidence to reject the null hypothesis', 'the effect size is 0.3', 'there is a 30% chance the alternative is true'], 1, 'Absence of evidence is not evidence of absence.', 'A large p-value means this data cannot tell, not that there is no effect.')
K.quiz('h', 'h heads in n flips. What is the maximum likelihood estimate of p?', ['h ÷ n', 'n ÷ h', '0.5', 'h ÷ (n + 1)'], 0, 'Set the derivative of the log-likelihood to zero.', 'p̂ = h ÷ n, the observed share.')
K.quiz('h', 'A regression has R² = 0.81. This means…', ['81% of the points lie on the line', 'the line explains 81% of the variation in y', 'the slope is 0.81', 'the correlation is 0.81'], 1, 'R² = 1 − SSres ÷ SStot.', 'The correlation would be √0.81 = 0.9 (with the sign of the slope).')
K.quiz('h', 'A model has very low training error but high test error. It is…', ['underfitting (high bias)', 'overfitting (high variance)', 'perfectly fitted', 'using too little data cleaning'], 1, 'It memorised the training data.', 'More data, regularisation or a simpler model usually helps.')
K.quiz('x', 'Why maximise the log-likelihood instead of the likelihood itself?', ['logs turn products into sums, avoid underflow and keep the same best parameter', 'logs always give bigger numbers', 'to make the answer negative', 'the likelihood has no maximum'], 0, 'log is an increasing function.', 'The same p maximises both, and sums of logs are numerically stable.')
K.quiz('x', '20 independent A/B tests are run at α = 0.05 where no change has any real effect. About how many will look significant?', ['0', '1', '5', '20'], 1, '20 × 0.05.', 'This is the multiple testing problem. Corrections such as Bonferroni (use α ÷ 20) guard against it.')
K.quiz('x', 'With normally distributed noise, least squares regression is the same as…', ['maximum likelihood estimation', 'median regression', 'random guessing', 'maximising the residuals'], 0, 'Write down the normal likelihood and take logs.', 'Maximising the normal log-likelihood means minimising the sum of squared residuals.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What is the mean of 4, 8, 6 and 2?', '5', 'Add and divide by how many.', [
    'Add: <span class="eq">4 + 8 + 6 + 2 = 20</span>',
    'Count: <span class="eq">4</span> values',
    '<span class="eq">20 ÷ 4 = 5</span>',
], check=5)
K.calc('e', 'What is the median of 7, 1, 9, 3, 5, 11?', '6', 'Even count: average the middle two.', [
    'Sort: <span class="eq">1, 3, 5, 7, 9, 11</span>',
    'The middle two are <span class="eq">5</span> and <span class="eq">7</span>',
    '<span class="eq">(5 + 7) ÷ 2 = 6</span>',
], check=6)
K.calc('e', 'Commute times 21, 22, 23, 24, 25, 25, 60. What is the range?', '39', 'Largest minus smallest.', [
    'Largest: <span class="eq">60</span>',
    'Smallest: <span class="eq">21</span>',
    '<span class="eq">60 − 21 = 39</span>',
], check=39)
K.calc('e', 'A population has σ = 12. What is the standard error of the mean for samples of 36?', '2', 'SE = σ ÷ √n.', [
    '<span class="eq">√36 = 6</span>',
    '<span class="eq">SE = 12 ÷ 6 = 2</span>',
    'Sample means typically land within about 2 of μ',
], check=2)
K.calc('m', 'Find the sample variance (divide by n − 1) of 2, 4, 4, 4, 5, 5, 7, 9. Give 3 decimal places.', '4.571', 'The mean is 5.', [
    'Mean: <span class="eq">40 ÷ 8 = 5</span>',
    'Squared deviations: <span class="eq">9, 1, 1, 1, 0, 0, 4, 16</span>, total <span class="eq">32</span>',
    'Divide by <span class="eq">n − 1 = 7</span>: <span class="eq">32 ÷ 7 ≈ 4.571</span>',
], check=32 / 7, tol=0.001)
K.calc('m', 'n = 36, sample SD = 2.4. What is the margin of error of a 95% interval for the mean? Give 3 decimal places.', '0.784', 'Margin = 1.96 × SE.', [
    '<span class="eq">SE = 2.4 ÷ √36 = 2.4 ÷ 6 = 0.4</span>',
    '<span class="eq">1.96 × 0.4 = 0.784</span>',
    'The interval is the sample mean <span class="eq">± 0.784</span>',
], check=1.96 * 0.4, tol=0.001)
K.calc('m', 'What is the IQR of 1, 3, 5, 7, 9, 11, 13, 15?', '8', 'Q1 = median of the lower half, Q3 = median of the upper half.', [
    'Lower half <span class="eq">1, 3, 5, 7</span>: <span class="eq">Q1 = (3 + 5) ÷ 2 = 4</span>',
    'Upper half <span class="eq">9, 11, 13, 15</span>: <span class="eq">Q3 = (11 + 13) ÷ 2 = 12</span>',
    '<span class="eq">IQR = 12 − 4 = 8</span>',
], check=8)
K.calc('m', 'x̄ = 248, μ₀ = 250, σ = 4, n = 16. What is the z statistic?', '−2', 'z = (x̄ − μ₀) ÷ (σ ÷ √n).', [
    '<span class="eq">SE = 4 ÷ √16 = 1</span>',
    '<span class="eq">x̄ − μ₀ = 248 − 250 = −2</span>',
    '<span class="eq">z = −2 ÷ 1 = −2</span>',
], check=-2)
K.calc('h', 'A poll finds 54% of 1000 people say yes. What is the 95% margin of error in percentage points? Give 1 decimal place.', '3.1', 'Margin = 1.96 × √(p̂(1 − p̂) ÷ n).', [
    '<span class="eq">0.54 × 0.46 = 0.2484</span>, divided by 1000: <span class="eq">0.0002484</span>',
    'Square root: <span class="eq">SE ≈ 0.01576</span>',
    '<span class="eq">1.96 × 0.01576 ≈ 0.0309</span>, that is about <span class="eq">3.1</span> points',
], check=1.96 * (0.54 * 0.46 / 1000) ** 0.5 * 100, tol=0.05, unit='%')
K.calc('h', 'What is the two sided p-value for z = 1.96? Give 2 decimal places.', '0.05', 'P(Z > 1.96) ≈ 0.025.', [
    'One tail: <span class="eq">P(Z > 1.96) ≈ 0.025</span>',
    'Two sided means both tails: <span class="eq">2 × 0.025</span>',
    '<span class="eq">= 0.05</span>. That is exactly why 1.96 is used for 95%.',
], check=0.05, tol=0.001)
K.calc('h', 'A coin lands heads 7 times in 10 flips. What is the maximum likelihood estimate of p?', '0.7', 'p̂ = heads ÷ flips.', [
    'Log-likelihood: <span class="eq">7 log p + 3 log(1 − p)</span>',
    'Derivative zero: <span class="eq">7/p = 3/(1 − p)</span>, so <span class="eq">10p = 7</span>',
    '<span class="eq">p̂ = 7 ÷ 10 = 0.7</span>',
], check=0.7)
K.calc('h', 'A line leaves SS<sub>res</sub> = 20 while SS<sub>tot</sub> = 200. What is R²?', '0.9', 'R² = 1 − SSres ÷ SStot.', [
    '<span class="eq">20 ÷ 200 = 0.1</span> of the variation is left unexplained',
    '<span class="eq">R² = 1 − 0.1</span>',
    '<span class="eq">= 0.9</span>, so the line explains 90% of the variation',
], check=0.9)
K.calc('x', 'How many people does a poll need for a 95% margin of ±2% in the worst case p = 0.5?', '2401', 'Solve 1.96 × √(0.25 ÷ n) = 0.02.', [
    'Square both sides: <span class="eq">1.96² × 0.25 ÷ n = 0.02²</span>',
    '<span class="eq">n = 3.8416 × 0.25 ÷ 0.0004</span>',
    '<span class="eq">= 0.9604 ÷ 0.0004 = 2401</span> people',
], check=1.96 ** 2 * 0.25 / 0.0004, tol=0.5)
K.calc('x', 'Σ(x − x̄)(y − ȳ) = 90 and Σ(x − x̄)² = 17.5. What is the least squares slope? Give 2 decimal places.', '5.14', 'b = Sxy ÷ Sxx.', [
    '<span class="eq">b = 90 ÷ 17.5</span>',
    '<span class="eq">= 5.142857…</span>',
    'Rounded: <span class="eq">5.14</span> extra points per hour studied',
], check=90 / 17.5, tol=0.005)

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;
  let seed = 777;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  const gauss = () => { const u = Math.max(1e-12, rnd()), v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  const erf = x => {
    const s = x >= 0 ? 1 : -1; x = Math.abs(x);
    const t = 1 / (1 + 0.3275911 * x);
    return s * (1 - t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429)))) * Math.exp(-x * x));
  };
  const Phi = z => 0.5 * (1 + erf(z / Math.SQRT2));
  const npdf = x => Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI);

  /* ----- confidence intervals: how many catch the true mean? ----- */
  W.ci = el => {
    const b = shell(el, 'Catch the true mean', 'The true mean is μ = 50 (dashed line) and σ = 10. Each step draws a new random sample of size n and draws its confidence interval. Green intervals catch μ, red ones miss. Change n and the confidence level and watch the width and the hit rate.');
    b.innerHTML = `<div class="vz-row">${seg('lv', [['80', '80%'], ['90', '90%'], ['95', '95%'], ['99', '99%']], '95')}</div>
      <div class="vz-row">${slider('n', 'sample size n', 4, 100, 25, 1)}</div>
      <div class="mv-wrap"><div class="ci-plot"></div><div class="mv-side"><div class="mv-legend"><span><i class="g"></i>catches μ</span><span><i class="r"></i>misses μ</span></div><div class="mv-read ci-out" aria-live="polite"></div><div class="vz-ctl"><button type="button" class="ci-new">🎲 New samples</button></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const MU = 50, SIG = 10, ROWS = 20;
    const Z = { 80: 1.2816, 90: 1.6449, 95: 1.96, 99: 2.5758 };
    let lv = '95', n = 25, means = [];
    function make() { means = Array.from({ length: ROWS }, () => { let t = 0; for (let i = 0; i < n; i++) t += MU + SIG * gauss(); return t / n; }); P.load(ROWS + 1, 0); }
    function show(t) {
      const half = Z[lv] * SIG / Math.sqrt(n);
      const G = MV.frame(460, 330, [30, 70], [0, ROWS + 1], 30);
      let s = MV.axes(G, { xstep: 5, ystep: 100, labels: false });
      for (let x = 30; x <= 70; x += 10) s += `<text class="mv-tick" x="${G.sx(x).toFixed(1)}" y="${(G.sy(0) + 16).toFixed(1)}" text-anchor="middle">${x}</text>`;
      let hits = 0;
      for (let i = 0; i < t; i++) {
        const m = means[i], lo = m - half, hi = m + half, ok = lo <= MU && MU <= hi, y = ROWS - i;
        if (ok) hits++;
        s += `<line class="mv-v ${ok ? 'g' : 'r'}" x1="${G.sx(Math.max(30, lo)).toFixed(1)}" y1="${G.sy(y).toFixed(1)}" x2="${G.sx(Math.min(70, hi)).toFixed(1)}" y2="${G.sy(y).toFixed(1)}" style="stroke-width:${i === t - 1 ? 4 : 2.5}"/>`;
        s += MV.dot(G, m, y, ok ? 'g' : 'r', 3.5);
      }
      s += MV.line(G, MU, 0, MU, ROWS + 1, 'mv-v k dash');
      $('.ci-plot', b).innerHTML = MV.svg(G, s, 'Confidence intervals');
      const m = t ? means[t - 1] : 0;
      $('.vz-msg', b).innerHTML = t === 0 ? `Press Play to draw ${ROWS} samples of size ${n}.` :
        `Sample ${t}: x̄ = ${MV.num(m, 2)}, interval ${MV.num(m, 2)} ± ${Z[lv]} × 10 ÷ √${n} = [${MV.num(m - half, 2)}, ${MV.num(m + half, 2)}] ${m - half <= MU && MU <= m + half ? 'catches' : 'misses'} μ = 50.`;
      $('.ci-out', b).innerHTML = `margin = z* × σ ÷ √n = ${Z[lv]} × 10 ÷ √${n} = <b>${MV.num(half, 2)}</b><br>caught so far: <b>${hits} of ${t}</b>` + (t ? ` (${MV.num(100 * hits / t, 0)}%)` : '') + `<br>in the long run: ${lv}%`;
    }
    const P = Player($('.vz-p', b), show, 600);
    wireSeg(b, 'lv', v => { lv = v; show(P.i); });
    wireSlider(b, 'n', v => { n = v; make(); });
    $('.ci-new', b).addEventListener('click', make);
    make();
  };

  /* ----- A/B test step by step ----- */
  W.abtest = el => {
    const b = shell(el, 'Run an A/B test', 'Set the number of visitors in each group and the true buying rates of pages A and B. Press Play to walk through the z-test, ending with the p-value as the shaded tails of the normal curve.');
    b.innerHTML = `<div class="vz-row">${slider('n', 'visitors per group', 100, 10000, 2000, 100)}</div>
      <div class="vz-row">${slider('a', 'page A buys %', 1, 30, 10, 0.5)}${slider('bb', 'page B buys %', 1, 30, 12.5, 0.5)}</div>
      <div class="mv-wrap"><div class="ab-plot"></div><div class="mv-side"><div class="mv-read ab-out" aria-live="polite"></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let n = 2000, A = 10, B = 12.5;
    function stats() {
      const ka = Math.round(n * A / 100), kb = Math.round(n * B / 100), pa = ka / n, pb = kb / n, pool = (ka + kb) / (2 * n);
      const se = Math.sqrt(pool * (1 - pool) * (2 / n)), z = se > 0 ? (pb - pa) / se : 0, p = 2 * (1 - Phi(Math.abs(z)));
      return { ka, kb, pa, pb, pool, se, z, p };
    }
    function show(t) {
      const S = stats(), zc = Math.max(-5.5, Math.min(5.5, S.z));
      const G = MV.frame(460, 250, [-6, 6], [0, 0.45], 30);
      let s = MV.axes(G, { xstep: 1, ystep: 1, labels: false });
      for (let x = -6; x <= 6; x += 2) s += `<text class="mv-tick" x="${G.sx(x).toFixed(1)}" y="${(G.sy(0) + 16).toFixed(1)}" text-anchor="middle">${x}</text>`;
      if (t >= 5) s += MV.area(G, npdf, -6, -Math.abs(zc), 'c2') + MV.area(G, npdf, Math.abs(zc), 6, 'c2');
      if (t >= 5) s += MV.line(G, -1.96, 0, -1.96, npdf(1.96) + 0.05, 'mv-v k dash') + MV.line(G, 1.96, 0, 1.96, npdf(1.96) + 0.05, 'mv-v k dash');
      s += MV.curve(G, npdf, '', { n: 300 });
      if (t >= 4) s += MV.line(G, zc, 0, zc, 0.42, 'mv-v p') + MV.text(G, zc, 0.42, `z = ${MV.num(S.z, 2)}`, { dy: -4, anchor: zc > 3 ? 'end' : zc < -3 ? 'start' : 'middle', cls: 'sm' });
      $('.ab-plot', b).innerHTML = MV.svg(G, s, 'Standard normal curve with the test statistic');
      $('.vz-msg', b).innerHTML = [
        `${n} visitors see each page. Press Play to run the test.`,
        `Page A: ${S.ka} of ${n} buy, p̂A = ${MV.num(S.pa, 4)}. Page B: ${S.kb} of ${n} buy, p̂B = ${MV.num(S.pb, 4)}. Observed lift ${MV.num(S.pb - S.pa, 4)}.`,
        `If the pages were truly the same (H₀), the best guess for their shared rate is the pooled rate (${S.ka} + ${S.kb}) ÷ ${2 * n} = ${MV.num(S.pool, 4)}.`,
        `Standard error of the difference: √(${MV.num(S.pool, 4)} × ${MV.num(1 - S.pool, 4)} × (1/${n} + 1/${n})) = ${MV.num(S.se, 5)}.`,
        `z = lift ÷ SE = ${MV.num(S.pb - S.pa, 4)} ÷ ${MV.num(S.se, 5)} = ${MV.num(S.z, 2)}. That is how many standard errors apart the pages are.`,
        `p-value = the orange tails beyond ±${MV.num(Math.abs(S.z), 2)} = ${MV.num(S.p, 4)}. The dashed lines at ±1.96 mark the 5% cut off.`,
        S.p < 0.05 ? `p = ${MV.num(S.p, 4)} < 0.05: the difference is statistically significant.` : `p = ${MV.num(S.p, 4)} ≥ 0.05: not significant. The gap could easily be luck. Try more visitors.`][t];
      $('.ab-out', b).innerHTML = `p̂A = ${MV.num(S.pa, 4)}, p̂B = ${MV.num(S.pb, 4)}<br>pooled = ${MV.num(S.pool, 4)}<br>SE = ${MV.num(S.se, 5)}<br>z = <b>${MV.num(S.z, 3)}</b>, p = <b>${MV.num(S.p, 4)}</b>`;
    }
    const P = Player($('.vz-p', b), show, 1700);
    wireSlider(b, 'n', v => { n = v; show(P.i); });
    wireSlider(b, 'a', v => { A = v; show(P.i); });
    wireSlider(b, 'bb', v => { B = v; show(P.i); });
    P.load(7, 0);
  };

  /* ----- maximum likelihood: climb the log-likelihood ----- */
  W.mle = el => {
    const b = shell(el, 'Climb the likelihood', 'Choose the data and a starting guess for p, the chance of heads. The curve shows how likely the data is for every p (scaled so the top is 1). Press Play to climb: each step moves p half way toward the peak, guided by the slope of the log-likelihood.');
    b.innerHTML = `<div class="vz-row">${seg('d', [['7,10', '7 of 10 heads'], ['70,100', '70 of 100'], ['2,10', '2 of 10']], '7,10')}</div>
      <div class="vz-row">${slider('p0', 'starting guess p', 0.05, 0.95, 0.2, 0.05)}</div>
      <div class="mv-wrap"><div class="ml-plot"></div><div class="mv-side"><div class="mv-read ml-out" aria-live="polite"></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let h = 7, N = 10, p0 = 0.2;
    const STEPS = 8;
    const ll = p => h * Math.log(p) + (N - h) * Math.log(1 - p);
    const rel = p => Math.exp(ll(p) - ll(h / N));
    const path = () => { const ps = [p0]; for (let i = 0; i < STEPS; i++) { const p = ps[ps.length - 1]; ps.push(p + 0.5 * (h / N - p)); } return ps; };
    function show(t) {
      const ps = path(), p = ps[t];
      const G = MV.frame(460, 260, [0, 1], [0, 1.12], 34);
      let s = MV.axes(G, { xstep: 0.1, ystep: 0.25 });
      s += MV.curve(G, rel, '', { n: 400, from: 0.001, to: 0.999 });
      s += MV.line(G, h / N, 0, h / N, 1, 'mv-v k dash');
      for (let i = 0; i < t; i++) s += MV.arrow(G, ps[i], rel(ps[i]), ps[i + 1], rel(ps[i + 1]), 'o');
      s += MV.dot(G, p, rel(p), 'p', 7);
      $('.ml-plot', b).innerHTML = MV.svg(G, s, 'Likelihood curve');
      const slope = h / p - (N - h) / (1 - p);
      $('.vz-msg', b).innerHTML = t === 0 ? `Start at p = ${MV.num(p, 3)}. Slope of the log-likelihood here: ${h}/p − ${N - h}/(1 − p) = ${MV.num(slope, 2)}. ${slope > 0 ? 'Positive, so move right.' : slope < 0 ? 'Negative, so move left.' : 'Zero: already at the top.'}` :
        `Step ${t}: p = ${MV.num(ps[t - 1], 3)} → ${MV.num(p, 3)}. Slope now ${MV.num(slope, 2)}. ${Math.abs(p - h / N) < 0.005 ? 'Almost exactly at the peak p̂ = h ÷ n.' : 'Keep climbing.'}`;
      $('.ml-out', b).innerHTML = `data: ${h} heads in ${N} flips<br>log L(${MV.num(p, 3)}) = ${MV.num(ll(p), 3)}<br>best: p̂ = ${h} ÷ ${N} = <b>${MV.num(h / N, 2)}</b><br>${N === 100 ? 'More data makes the curve much narrower: the estimate is more certain.' : 'Try 70 of 100: same peak, narrower curve.'}`;
    }
    const P = Player($('.vz-p', b), show, 900);
    wireSeg(b, 'd', v => { [h, N] = v.split(',').map(Number); P.load(STEPS + 1, 0); });
    wireSlider(b, 'p0', v => { p0 = v; P.load(STEPS + 1, 0); });
    P.load(STEPS + 1, 0);
  };
})();
'''

CSS = r'''
.ci-new{margin:6px 0}
'''

T = K.topic(
    slug='statistics', topic='statistics', prefix='mm11', short='Statistics', emoji='📈',
    title='Statistics and Inference',
    module=('🎲', 'Probability and statistics', 'probability', 'Chance, distributions and statistics: the maths that lets a model handle uncertainty and judge its own results.'),
    minutes=65,
    lead='Statistics turns a sample into honest conclusions. Describe data with the right summaries, watch confidence intervals catch (or miss) the true mean, run a hypothesis test and an A/B test step by step, climb a likelihood curve to its peak, and fit a regression line while keeping an eye on overfitting.',
    desc='Statistics for machine learning: mean, median, variance and outliers, samples and bias, standard error, confidence intervals, hypothesis tests and p-values, A/B testing, maximum likelihood estimation, linear regression, R² and the bias and variance trade-off.',
    summary='Descriptive statistics and outliers, populations, samples and bias, standard error, confidence intervals, null and alternative hypotheses, p-values, Type I and Type II errors, two proportion z-tests for A/B tests, sample size and power, maximum likelihood estimation, least squares regression, R² and the bias and variance trade-off.',
    keywords=['statistics', 'mean', 'median', 'standard deviation', 'outlier', 'sample', 'bias', 'standard error', 'confidence interval', 'hypothesis test', 'p-value', 'a/b test', 'maximum likelihood', 'linear regression', 'R squared', 'overfitting', 'bias variance'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
