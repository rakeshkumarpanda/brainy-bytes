# Chapter 10: random variables, PMF, PDF and CDF, expectation and variance, the Bernoulli, binomial and
# Poisson distributions, the normal distribution and z-scores, the central limit theorem, and covariance.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz

K = Kit()

# ---------------------------------------------------------------- programs
K.code('expectation', py=r'''
from math import sqrt

faces = [1, 2, 3, 4, 5, 6]
p = 1 / 6                                 # a fair die: every face has the same chance
mean = sum(x * p for x in faces)          # E[X] = sum of value times chance
var = sum((x - mean) ** 2 * p for x in faces)   # Var(X) = average squared distance from the mean
print(f"E[X]   = {mean:.4f}")
print(f"Var(X) = {var:.4f}")
print(f"SD(X)  = {sqrt(var):.4f}")
# a game: pay 2 to play, win 10 if you roll a six
profit = {8: 1 / 6, -2: 5 / 6}            # net result and its chance
e_profit = sum(v * q for v, q in profit.items())
print(f"expected profit per game = {e_profit:.4f}")
print(f"after 600 games expect about {600 * e_profit:.2f}")
''', js=r'''
const faces = [1, 2, 3, 4, 5, 6];
const p = 1 / 6;                          // a fair die: every face has the same chance
const mean = faces.reduce((s, x) => s + x * p, 0);   // E[X] = sum of value times chance
const variance = faces.reduce((s, x) => s + (x - mean) ** 2 * p, 0);   // average squared distance from the mean
console.log(`E[X]   = ${mean.toFixed(4)}`);
console.log(`Var(X) = ${variance.toFixed(4)}`);
console.log(`SD(X)  = ${Math.sqrt(variance).toFixed(4)}`);
// a game: pay 2 to play, win 10 if you roll a six
const profit = [[8, 1 / 6], [-2, 5 / 6]]; // net result and its chance
const eProfit = profit.reduce((s, [v, q]) => s + v * q, 0);
console.log(`expected profit per game = ${eProfit.toFixed(4)}`);
console.log(`after 600 games expect about ${(600 * eProfit).toFixed(2)}`);
''', ts=r'''
const faces: number[] = [1, 2, 3, 4, 5, 6];
const p: number = 1 / 6;                  // a fair die: every face has the same chance
const mean: number = faces.reduce((s, x) => s + x * p, 0);   // E[X] = sum of value times chance
const variance: number = faces.reduce((s, x) => s + (x - mean) ** 2 * p, 0);   // average squared distance from the mean
console.log(`E[X]   = ${mean.toFixed(4)}`);
console.log(`Var(X) = ${variance.toFixed(4)}`);
console.log(`SD(X)  = ${Math.sqrt(variance).toFixed(4)}`);
// a game: pay 2 to play, win 10 if you roll a six
const profit: [number, number][] = [[8, 1 / 6], [-2, 5 / 6]];   // net result and its chance
const eProfit: number = profit.reduce((s, [v, q]) => s + v * q, 0);
console.log(`expected profit per game = ${eProfit.toFixed(4)}`);
console.log(`after 600 games expect about ${(600 * eProfit).toFixed(2)}`);
''', java=r'''
public class Expectation {
    public static void main(String[] args) {
        int[] faces = {1, 2, 3, 4, 5, 6};
        double p = 1.0 / 6;                       // a fair die: every face has the same chance
        double mean = 0;
        for (int x : faces) mean += x * p;        // E[X] = sum of value times chance
        double var = 0;
        for (int x : faces) var += (x - mean) * (x - mean) * p;   // average squared distance from the mean
        System.out.println(String.format("E[X]   = %.4f", mean));
        System.out.println(String.format("Var(X) = %.4f", var));
        System.out.println(String.format("SD(X)  = %.4f", Math.sqrt(var)));
        // a game: pay 2 to play, win 10 if you roll a six
        double[][] profit = {{8, 1.0 / 6}, {-2, 5.0 / 6}};   // net result and its chance
        double eProfit = 0;
        for (double[] vq : profit) eProfit += vq[0] * vq[1];
        System.out.println(String.format("expected profit per game = %.4f", eProfit));
        System.out.println(String.format("after 600 games expect about %.2f", 600 * eProfit));
    }
}
''')

K.code('binomial', py=r'''
from math import comb, sqrt

n, p = 10, 0.5                            # 10 fair coin flips, count the heads
for k in range(n + 1):
    pk = comb(n, k) * p ** k * (1 - p) ** (n - k)   # number of ways times the chance of one way
    bar = "#" * int(pk * 50 + 0.5)        # a text bar chart
    print(f"P(X = {k:2}) = {pk:.4f} |{bar}")
print(f"mean = n p = {n * p:.2f}, variance = n p (1 - p) = {n * p * (1 - p):.2f}, SD = {sqrt(n * p * (1 - p)):.4f}")
''', js=r'''
function comb(n, k) {                     // multiply and divide step by step to stay exact
  let r = 1;
  for (let i = 1; i <= k; i++) r = r * (n - k + i) / i;
  return Math.round(r);
}

const n = 10, p = 0.5;                    // 10 fair coin flips, count the heads
for (let k = 0; k <= n; k++) {
  const pk = comb(n, k) * p ** k * (1 - p) ** (n - k);   // number of ways times the chance of one way
  const bar = "#".repeat(Math.floor(pk * 50 + 0.5));     // a text bar chart
  console.log(`P(X = ${String(k).padStart(2)}) = ${pk.toFixed(4)} |${bar}`);
}
console.log(`mean = n p = ${(n * p).toFixed(2)}, variance = n p (1 - p) = ${(n * p * (1 - p)).toFixed(2)}, SD = ${Math.sqrt(n * p * (1 - p)).toFixed(4)}`);
''', ts=r'''
function comb(n: number, k: number): number {   // multiply and divide step by step to stay exact
  let r: number = 1;
  for (let i = 1; i <= k; i++) r = r * (n - k + i) / i;
  return Math.round(r);
}

const n: number = 10, p: number = 0.5;    // 10 fair coin flips, count the heads
for (let k = 0; k <= n; k++) {
  const pk: number = comb(n, k) * p ** k * (1 - p) ** (n - k);   // number of ways times the chance of one way
  const bar: string = "#".repeat(Math.floor(pk * 50 + 0.5));     // a text bar chart
  console.log(`P(X = ${String(k).padStart(2)}) = ${pk.toFixed(4)} |${bar}`);
}
console.log(`mean = n p = ${(n * p).toFixed(2)}, variance = n p (1 - p) = ${(n * p * (1 - p)).toFixed(2)}, SD = ${Math.sqrt(n * p * (1 - p)).toFixed(4)}`);
''', java=r'''
public class Binomial {
    static long comb(int n, int k) {          // multiply and divide step by step to stay exact
        long r = 1;
        for (int i = 1; i <= k; i++) r = r * (n - k + i) / i;
        return r;
    }

    public static void main(String[] args) {
        int n = 10;
        double p = 0.5;                           // 10 fair coin flips, count the heads
        for (int k = 0; k <= n; k++) {
            double pk = comb(n, k) * Math.pow(p, k) * Math.pow(1 - p, n - k);   // number of ways times the chance of one way
            String bar = "#".repeat((int) Math.floor(pk * 50 + 0.5));           // a text bar chart
            System.out.println(String.format("P(X = %2d) = %.4f |%s", k, pk, bar));
        }
        System.out.println(String.format("mean = n p = %.2f, variance = n p (1 - p) = %.2f, SD = %.4f", n * p, n * p * (1 - p), Math.sqrt(n * p * (1 - p))));
    }
}
''')

K.code('normal', py=r'''
from math import exp, pi, sqrt


def erf(x):                               # a very accurate formula (Abramowitz and Stegun 7.1.26)
    sign = 1 if x >= 0 else -1
    x = abs(x)
    t = 1 / (1 + 0.3275911 * x)
    poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))))
    return sign * (1 - poly * exp(-x * x))


def cdf(x, mu, sigma):                    # P(X <= x) for a normal distribution
    return 0.5 * (1 + erf((x - mu) / (sigma * sqrt(2))))


def pdf(x, mu, sigma):                    # the height of the bell curve
    return exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / (sigma * sqrt(2 * pi))


for k in (1, 2, 3):
    print(f"within {k} SD of the mean: {cdf(k, 0, 1) - cdf(-k, 0, 1):.4f}")
mu, sigma = 170, 8                        # adult heights in cm
print(f"height of the curve at the mean: {pdf(mu, mu, sigma):.4f}")
print(f"z-score of 186 cm: {(186 - mu) / sigma:.2f}")
print(f"P(taller than 180 cm) = {1 - cdf(180, mu, sigma):.4f}")
''', js=r'''
function erf(x) {                         // a very accurate formula (Abramowitz and Stegun 7.1.26)
  const sign = x >= 0 ? 1 : -1;
  x = Math.abs(x);
  const t = 1 / (1 + 0.3275911 * x);
  const poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
  return sign * (1 - poly * Math.exp(-x * x));
}

function cdf(x, mu, sigma) {              // P(X <= x) for a normal distribution
  return 0.5 * (1 + erf((x - mu) / (sigma * Math.sqrt(2))));
}

function pdf(x, mu, sigma) {              // the height of the bell curve
  return Math.exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / (sigma * Math.sqrt(2 * Math.PI));
}

for (const k of [1, 2, 3]) {
  console.log(`within ${k} SD of the mean: ${(cdf(k, 0, 1) - cdf(-k, 0, 1)).toFixed(4)}`);
}
const mu = 170, sigma = 8;                // adult heights in cm
console.log(`height of the curve at the mean: ${pdf(mu, mu, sigma).toFixed(4)}`);
console.log(`z-score of 186 cm: ${((186 - mu) / sigma).toFixed(2)}`);
console.log(`P(taller than 180 cm) = ${(1 - cdf(180, mu, sigma)).toFixed(4)}`);
''', ts=r'''
function erf(x: number): number {         // a very accurate formula (Abramowitz and Stegun 7.1.26)
  const sign: number = x >= 0 ? 1 : -1;
  x = Math.abs(x);
  const t: number = 1 / (1 + 0.3275911 * x);
  const poly: number = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
  return sign * (1 - poly * Math.exp(-x * x));
}

function cdf(x: number, mu: number, sigma: number): number {   // P(X <= x) for a normal distribution
  return 0.5 * (1 + erf((x - mu) / (sigma * Math.sqrt(2))));
}

function pdf(x: number, mu: number, sigma: number): number {   // the height of the bell curve
  return Math.exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / (sigma * Math.sqrt(2 * Math.PI));
}

for (const k of [1, 2, 3]) {
  console.log(`within ${k} SD of the mean: ${(cdf(k, 0, 1) - cdf(-k, 0, 1)).toFixed(4)}`);
}
const mu: number = 170, sigma: number = 8;   // adult heights in cm
console.log(`height of the curve at the mean: ${pdf(mu, mu, sigma).toFixed(4)}`);
console.log(`z-score of 186 cm: ${((186 - mu) / sigma).toFixed(2)}`);
console.log(`P(taller than 180 cm) = ${(1 - cdf(180, mu, sigma)).toFixed(4)}`);
''', java=r'''
public class Normal {
    static double erf(double x) {             // a very accurate formula (Abramowitz and Stegun 7.1.26)
        double sign = x >= 0 ? 1 : -1;
        x = Math.abs(x);
        double t = 1 / (1 + 0.3275911 * x);
        double poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
        return sign * (1 - poly * Math.exp(-x * x));
    }

    static double cdf(double x, double mu, double sigma) {   // P(X <= x) for a normal distribution
        return 0.5 * (1 + erf((x - mu) / (sigma * Math.sqrt(2))));
    }

    static double pdf(double x, double mu, double sigma) {   // the height of the bell curve
        return Math.exp(-((x - mu) * (x - mu)) / (2 * sigma * sigma)) / (sigma * Math.sqrt(2 * Math.PI));
    }

    public static void main(String[] args) {
        for (int k = 1; k <= 3; k++) {
            System.out.println(String.format("within %d SD of the mean: %.4f", k, cdf(k, 0, 1) - cdf(-k, 0, 1)));
        }
        double mu = 170, sigma = 8;               // adult heights in cm
        System.out.println(String.format("height of the curve at the mean: %.4f", pdf(mu, mu, sigma)));
        System.out.println(String.format("z-score of 186 cm: %.2f", (186 - mu) / sigma));
        System.out.println(String.format("P(taller than 180 cm) = %.4f", 1 - cdf(180, mu, sigma)));
    }
}
''')

K.code('clt', py=r'''
from math import sqrt

dist = [0.0] + [1 / 6] * 6                # dist[s] = chance that the dice add up to s (one die to start)
for n in range(1, 5):
    if n > 1:
        new = [0.0] * (len(dist) + 6)
        for s in range(len(dist)):        # add one more die to every total so far
            for face in range(1, 7):
                new[s + face] += dist[s] / 6
        dist = new
    mean = sum(s / n * dist[s] for s in range(len(dist)))   # the average of n dice is total / n
    sd = sqrt(sum((s / n - mean) ** 2 * dist[s] for s in range(len(dist))))
    near = sum(dist[s] for s in range(len(dist)) if 3 <= s / n <= 4)
    print(f"average of {n} dice: mean {mean:.2f}, SD {sd:.4f}, P(3 <= average <= 4) = {near:.4f}")
''', js=r'''
let dist = [0, 1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6];   // dist[s] = chance that the dice add up to s (one die to start)
for (let n = 1; n <= 4; n++) {
  if (n > 1) {
    const next = new Array(dist.length + 6).fill(0);
    for (let s = 0; s < dist.length; s++) {   // add one more die to every total so far
      for (let face = 1; face <= 6; face++) {
        next[s + face] += dist[s] / 6;
      }
    }
    dist = next;
  }
  const mean = dist.reduce((acc, q, s) => acc + s / n * q, 0);   // the average of n dice is total / n
  const sd = Math.sqrt(dist.reduce((acc, q, s) => acc + (s / n - mean) ** 2 * q, 0));
  const near = dist.reduce((acc, q, s) => acc + (s / n >= 3 && s / n <= 4 ? q : 0), 0);
  console.log(`average of ${n} dice: mean ${mean.toFixed(2)}, SD ${sd.toFixed(4)}, P(3 <= average <= 4) = ${near.toFixed(4)}`);
}
''', ts=r'''
let dist: number[] = [0, 1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6];   // dist[s] = chance that the dice add up to s (one die to start)
for (let n = 1; n <= 4; n++) {
  if (n > 1) {
    const next: number[] = new Array(dist.length + 6).fill(0);
    for (let s = 0; s < dist.length; s++) {   // add one more die to every total so far
      for (let face = 1; face <= 6; face++) {
        next[s + face] += dist[s] / 6;
      }
    }
    dist = next;
  }
  const mean: number = dist.reduce((acc, q, s) => acc + s / n * q, 0);   // the average of n dice is total / n
  const sd: number = Math.sqrt(dist.reduce((acc, q, s) => acc + (s / n - mean) ** 2 * q, 0));
  const near: number = dist.reduce((acc, q, s) => acc + (s / n >= 3 && s / n <= 4 ? q : 0), 0);
  console.log(`average of ${n} dice: mean ${mean.toFixed(2)}, SD ${sd.toFixed(4)}, P(3 <= average <= 4) = ${near.toFixed(4)}`);
}
''', java=r'''
public class CentralLimit {
    public static void main(String[] args) {
        double[] dist = {0, 1.0 / 6, 1.0 / 6, 1.0 / 6, 1.0 / 6, 1.0 / 6, 1.0 / 6};   // dist[s] = chance the dice add up to s
        for (int n = 1; n <= 4; n++) {
            if (n > 1) {
                double[] next = new double[dist.length + 6];
                for (int s = 0; s < dist.length; s++) {   // add one more die to every total so far
                    for (int face = 1; face <= 6; face++) {
                        next[s + face] += dist[s] / 6;
                    }
                }
                dist = next;
            }
            double mean = 0, sq = 0, near = 0;
            for (int s = 0; s < dist.length; s++) mean += (double) s / n * dist[s];   // the average of n dice is total / n
            for (int s = 0; s < dist.length; s++) sq += Math.pow((double) s / n - mean, 2) * dist[s];
            for (int s = 0; s < dist.length; s++) if ((double) s / n >= 3 && (double) s / n <= 4) near += dist[s];
            System.out.println(String.format("average of %d dice: mean %.2f, SD %.4f, P(3 <= average <= 4) = %.4f", n, mean, Math.sqrt(sq), near));
        }
    }
}
''')

K.code('covariance', py=r'''
from math import sqrt

hours = [1, 2, 3, 4, 5, 6]                # hours studied
score = [52, 55, 61, 66, 70, 78]          # test score
n = len(hours)
mx, my = sum(hours) / n, sum(score) / n
cov = sum((x - mx) * (y - my) for x, y in zip(hours, score)) / (n - 1)   # do they move together?
sx = sqrt(sum((x - mx) ** 2 for x in hours) / (n - 1))
sy = sqrt(sum((y - my) ** 2 for y in score) / (n - 1))
print(f"mean hours {mx:.2f}, mean score {my:.2f}")
print(f"covariance  = {cov:.2f}")
print(f"correlation = {cov / (sx * sy):.4f}")
print(f"each extra hour adds about {cov / sx ** 2:.2f} points")
''', js=r'''
const hours = [1, 2, 3, 4, 5, 6];         // hours studied
const score = [52, 55, 61, 66, 70, 78];   // test score
const n = hours.length;
const mx = hours.reduce((s, v) => s + v, 0) / n, my = score.reduce((s, v) => s + v, 0) / n;
const cov = hours.reduce((s, x, i) => s + (x - mx) * (score[i] - my), 0) / (n - 1);   // do they move together?
const sx = Math.sqrt(hours.reduce((s, x) => s + (x - mx) ** 2, 0) / (n - 1));
const sy = Math.sqrt(score.reduce((s, y) => s + (y - my) ** 2, 0) / (n - 1));
console.log(`mean hours ${mx.toFixed(2)}, mean score ${my.toFixed(2)}`);
console.log(`covariance  = ${cov.toFixed(2)}`);
console.log(`correlation = ${(cov / (sx * sy)).toFixed(4)}`);
console.log(`each extra hour adds about ${(cov / sx ** 2).toFixed(2)} points`);
''', ts=r'''
const hours: number[] = [1, 2, 3, 4, 5, 6];        // hours studied
const score: number[] = [52, 55, 61, 66, 70, 78];  // test score
const n: number = hours.length;
const mx: number = hours.reduce((s, v) => s + v, 0) / n, my: number = score.reduce((s, v) => s + v, 0) / n;
const cov: number = hours.reduce((s, x, i) => s + (x - mx) * (score[i] - my), 0) / (n - 1);   // do they move together?
const sx: number = Math.sqrt(hours.reduce((s, x) => s + (x - mx) ** 2, 0) / (n - 1));
const sy: number = Math.sqrt(score.reduce((s, y) => s + (y - my) ** 2, 0) / (n - 1));
console.log(`mean hours ${mx.toFixed(2)}, mean score ${my.toFixed(2)}`);
console.log(`covariance  = ${cov.toFixed(2)}`);
console.log(`correlation = ${(cov / (sx * sy)).toFixed(4)}`);
console.log(`each extra hour adds about ${(cov / sx ** 2).toFixed(2)} points`);
''', java=r'''
public class Covariance {
    public static void main(String[] args) {
        double[] hours = {1, 2, 3, 4, 5, 6};          // hours studied
        double[] score = {52, 55, 61, 66, 70, 78};    // test score
        int n = hours.length;
        double mx = 0, my = 0;
        for (int i = 0; i < n; i++) { mx += hours[i] / n; my += score[i] / n; }
        double cov = 0, vx = 0, vy = 0;
        for (int i = 0; i < n; i++) {
            cov += (hours[i] - mx) * (score[i] - my) / (n - 1);   // do they move together?
            vx += (hours[i] - mx) * (hours[i] - mx) / (n - 1);
            vy += (score[i] - my) * (score[i] - my) / (n - 1);
        }
        double sx = Math.sqrt(vx), sy = Math.sqrt(vy);
        System.out.println(String.format("mean hours %.2f, mean score %.2f", mx, my));
        System.out.println(String.format("covariance  = %.2f", cov));
        System.out.println(String.format("correlation = %.4f", cov / (sx * sy)));
        System.out.println(String.format("each extra hour adds about %.2f points", cov / (sx * sx)));
    }
}
''')

K.code('p_raffle', py=r'''
from math import sqrt

tickets, price = 1000, 5                  # 1000 tickets sold at 5 each
prizes = [1000, 500, 500, 100, 100, 100, 100, 100]   # each prize goes to one ticket
e_prize = sum(prizes) / tickets           # every prize has a 1 in 1000 chance of being yours
e_square = sum(v * v for v in prizes) / tickets
print(f"expected prize per ticket  = {e_prize:.2f}")
print(f"expected profit per ticket = {e_prize - price:.2f}")
print(f"SD of the prize            = {sqrt(e_square - e_prize ** 2):.2f}")
print(f"the organiser keeps {tickets * price - sum(prizes)} whatever happens")
''', js=r'''
const tickets = 1000, price = 5;          // 1000 tickets sold at 5 each
const prizes = [1000, 500, 500, 100, 100, 100, 100, 100];   // each prize goes to one ticket
const total = prizes.reduce((s, v) => s + v, 0);
const ePrize = total / tickets;           // every prize has a 1 in 1000 chance of being yours
const eSquare = prizes.reduce((s, v) => s + v * v, 0) / tickets;
console.log(`expected prize per ticket  = ${ePrize.toFixed(2)}`);
console.log(`expected profit per ticket = ${(ePrize - price).toFixed(2)}`);
console.log(`SD of the prize            = ${Math.sqrt(eSquare - ePrize ** 2).toFixed(2)}`);
console.log(`the organiser keeps ${tickets * price - total} whatever happens`);
''', ts=r'''
const tickets: number = 1000, price: number = 5;   // 1000 tickets sold at 5 each
const prizes: number[] = [1000, 500, 500, 100, 100, 100, 100, 100];   // each prize goes to one ticket
const total: number = prizes.reduce((s, v) => s + v, 0);
const ePrize: number = total / tickets;   // every prize has a 1 in 1000 chance of being yours
const eSquare: number = prizes.reduce((s, v) => s + v * v, 0) / tickets;
console.log(`expected prize per ticket  = ${ePrize.toFixed(2)}`);
console.log(`expected profit per ticket = ${(ePrize - price).toFixed(2)}`);
console.log(`SD of the prize            = ${Math.sqrt(eSquare - ePrize ** 2).toFixed(2)}`);
console.log(`the organiser keeps ${tickets * price - total} whatever happens`);
''', java=r'''
public class PracticeRaffle {
    public static void main(String[] args) {
        int tickets = 1000, price = 5;            // 1000 tickets sold at 5 each
        int[] prizes = {1000, 500, 500, 100, 100, 100, 100, 100};   // each prize goes to one ticket
        int total = 0;
        double square = 0;
        for (int v : prizes) { total += v; square += (double) v * v; }
        double ePrize = (double) total / tickets; // every prize has a 1 in 1000 chance of being yours
        double eSquare = square / tickets;
        System.out.println(String.format("expected prize per ticket  = %.2f", ePrize));
        System.out.println(String.format("expected profit per ticket = %.2f", ePrize - price));
        System.out.println(String.format("SD of the prize            = %.2f", Math.sqrt(eSquare - ePrize * ePrize)));
        System.out.println("the organiser keeps " + (tickets * price - total) + " whatever happens");
    }
}
''')

K.code('p_freethrow', py=r'''
from math import comb, sqrt

n, p = 5, 0.7                             # 5 free throws, each one scores with chance 0.7


def binom(k):                             # P(exactly k baskets)
    return comb(n, k) * p ** k * (1 - p) ** (n - k)


print(f"P(exactly 3)  = {binom(3):.4f}")
print(f"P(at least 4) = {binom(4) + binom(5):.4f}")
print(f"P(at least 1) = {1 - binom(0):.4f}")
print(f"mean = {n * p:.2f}, SD = {sqrt(n * p * (1 - p)):.4f}")
''', js=r'''
function comb(n, k) {
  let r = 1;
  for (let i = 1; i <= k; i++) r = r * (n - k + i) / i;
  return Math.round(r);
}

const n = 5, p = 0.7;                     // 5 free throws, each one scores with chance 0.7
const binom = k => comb(n, k) * p ** k * (1 - p) ** (n - k);   // P(exactly k baskets)

console.log(`P(exactly 3)  = ${binom(3).toFixed(4)}`);
console.log(`P(at least 4) = ${(binom(4) + binom(5)).toFixed(4)}`);
console.log(`P(at least 1) = ${(1 - binom(0)).toFixed(4)}`);
console.log(`mean = ${(n * p).toFixed(2)}, SD = ${Math.sqrt(n * p * (1 - p)).toFixed(4)}`);
''', ts=r'''
function comb(n: number, k: number): number {
  let r: number = 1;
  for (let i = 1; i <= k; i++) r = r * (n - k + i) / i;
  return Math.round(r);
}

const n: number = 5, p: number = 0.7;     // 5 free throws, each one scores with chance 0.7
const binom = (k: number): number => comb(n, k) * p ** k * (1 - p) ** (n - k);   // P(exactly k baskets)

console.log(`P(exactly 3)  = ${binom(3).toFixed(4)}`);
console.log(`P(at least 4) = ${(binom(4) + binom(5)).toFixed(4)}`);
console.log(`P(at least 1) = ${(1 - binom(0)).toFixed(4)}`);
console.log(`mean = ${(n * p).toFixed(2)}, SD = ${Math.sqrt(n * p * (1 - p)).toFixed(4)}`);
''', java=r'''
public class PracticeFreeThrow {
    static int n = 5;
    static double p = 0.7;                    // 5 free throws, each one scores with chance 0.7

    static long comb(int n, int k) {
        long r = 1;
        for (int i = 1; i <= k; i++) r = r * (n - k + i) / i;
        return r;
    }

    static double binom(int k) {              // P(exactly k baskets)
        return comb(n, k) * Math.pow(p, k) * Math.pow(1 - p, n - k);
    }

    public static void main(String[] args) {
        System.out.println(String.format("P(exactly 3)  = %.4f", binom(3)));
        System.out.println(String.format("P(at least 4) = %.4f", binom(4) + binom(5)));
        System.out.println(String.format("P(at least 1) = %.4f", 1 - binom(0)));
        System.out.println(String.format("mean = %.2f, SD = %.4f", n * p, Math.sqrt(n * p * (1 - p))));
    }
}
''')

K.code('p_poisson', py=r'''
from math import exp, factorial

lam = 3                                   # on average 3 calls arrive per hour


def poisson(k):                           # P(exactly k calls in an hour)
    return exp(-lam) * lam ** k / factorial(k)


print(f"P(no calls)        = {poisson(0):.4f}")
print(f"P(exactly 2 calls) = {poisson(2):.4f}")
print(f"P(at least 1 call) = {1 - poisson(0):.4f}")
up_to_5 = sum(poisson(k) for k in range(6))
print(f"P(more than 5)     = {1 - up_to_5:.4f}")
''', js=r'''
const lam = 3;                            // on average 3 calls arrive per hour
const factorial = k => (k <= 1 ? 1 : k * factorial(k - 1));
const poisson = k => Math.exp(-lam) * lam ** k / factorial(k);   // P(exactly k calls in an hour)

console.log(`P(no calls)        = ${poisson(0).toFixed(4)}`);
console.log(`P(exactly 2 calls) = ${poisson(2).toFixed(4)}`);
console.log(`P(at least 1 call) = ${(1 - poisson(0)).toFixed(4)}`);
let upTo5 = 0;
for (let k = 0; k <= 5; k++) upTo5 += poisson(k);
console.log(`P(more than 5)     = ${(1 - upTo5).toFixed(4)}`);
''', ts=r'''
const lam: number = 3;                    // on average 3 calls arrive per hour
const factorial = (k: number): number => (k <= 1 ? 1 : k * factorial(k - 1));
const poisson = (k: number): number => Math.exp(-lam) * lam ** k / factorial(k);   // P(exactly k calls in an hour)

console.log(`P(no calls)        = ${poisson(0).toFixed(4)}`);
console.log(`P(exactly 2 calls) = ${poisson(2).toFixed(4)}`);
console.log(`P(at least 1 call) = ${(1 - poisson(0)).toFixed(4)}`);
let upTo5: number = 0;
for (let k = 0; k <= 5; k++) upTo5 += poisson(k);
console.log(`P(more than 5)     = ${(1 - upTo5).toFixed(4)}`);
''', java=r'''
public class PracticePoisson {
    static double lam = 3;                    // on average 3 calls arrive per hour

    static double factorial(int k) {
        return k <= 1 ? 1 : k * factorial(k - 1);
    }

    static double poisson(int k) {            // P(exactly k calls in an hour)
        return Math.exp(-lam) * Math.pow(lam, k) / factorial(k);
    }

    public static void main(String[] args) {
        System.out.println(String.format("P(no calls)        = %.4f", poisson(0)));
        System.out.println(String.format("P(exactly 2 calls) = %.4f", poisson(2)));
        System.out.println(String.format("P(at least 1 call) = %.4f", 1 - poisson(0)));
        double upTo5 = 0;
        for (int k = 0; k <= 5; k++) upTo5 += poisson(k);
        System.out.println(String.format("P(more than 5)     = %.4f", 1 - upTo5));
    }
}
''')

K.code('p_exam', py=r'''
from math import exp, sqrt


def erf(x):                               # Abramowitz and Stegun 7.1.26
    sign = 1 if x >= 0 else -1
    x = abs(x)
    t = 1 / (1 + 0.3275911 * x)
    poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))))
    return sign * (1 - poly * exp(-x * x))


def cdf(x, mu, sigma):
    return 0.5 * (1 + erf((x - mu) / (sigma * sqrt(2))))


mu, sigma = 70, 10                        # exam scores
print(f"P(score above 85) = {1 - cdf(85, mu, sigma):.4f}")
print(f"a score of 80 beats {100 * cdf(80, mu, sigma):.2f}% of students")
lo, hi = mu, mu + 4 * sigma               # the top 10% cutoff lies somewhere in here
for _ in range(40):                       # binary search: halve the gap each time
    mid = (lo + hi) / 2
    if cdf(mid, mu, sigma) < 0.9:
        lo = mid
    else:
        hi = mid
print(f"top 10% cutoff = {lo:.2f}")
''', js=r'''
function erf(x) {                         // Abramowitz and Stegun 7.1.26
  const sign = x >= 0 ? 1 : -1;
  x = Math.abs(x);
  const t = 1 / (1 + 0.3275911 * x);
  const poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
  return sign * (1 - poly * Math.exp(-x * x));
}

const cdf = (x, mu, sigma) => 0.5 * (1 + erf((x - mu) / (sigma * Math.sqrt(2))));

const mu = 70, sigma = 10;                // exam scores
console.log(`P(score above 85) = ${(1 - cdf(85, mu, sigma)).toFixed(4)}`);
console.log(`a score of 80 beats ${(100 * cdf(80, mu, sigma)).toFixed(2)}% of students`);
let lo = mu, hi = mu + 4 * sigma;         // the top 10% cutoff lies somewhere in here
for (let i = 0; i < 40; i++) {            // binary search: halve the gap each time
  const mid = (lo + hi) / 2;
  if (cdf(mid, mu, sigma) < 0.9) {
    lo = mid;
  } else {
    hi = mid;
  }
}
console.log(`top 10% cutoff = ${lo.toFixed(2)}`);
''', ts=r'''
function erf(x: number): number {         // Abramowitz and Stegun 7.1.26
  const sign: number = x >= 0 ? 1 : -1;
  x = Math.abs(x);
  const t: number = 1 / (1 + 0.3275911 * x);
  const poly: number = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
  return sign * (1 - poly * Math.exp(-x * x));
}

const cdf = (x: number, mu: number, sigma: number): number => 0.5 * (1 + erf((x - mu) / (sigma * Math.sqrt(2))));

const mu: number = 70, sigma: number = 10;   // exam scores
console.log(`P(score above 85) = ${(1 - cdf(85, mu, sigma)).toFixed(4)}`);
console.log(`a score of 80 beats ${(100 * cdf(80, mu, sigma)).toFixed(2)}% of students`);
let lo: number = mu, hi: number = mu + 4 * sigma;   // the top 10% cutoff lies somewhere in here
for (let i = 0; i < 40; i++) {            // binary search: halve the gap each time
  const mid: number = (lo + hi) / 2;
  if (cdf(mid, mu, sigma) < 0.9) {
    lo = mid;
  } else {
    hi = mid;
  }
}
console.log(`top 10% cutoff = ${lo.toFixed(2)}`);
''', java=r'''
public class PracticeExam {
    static double erf(double x) {             // Abramowitz and Stegun 7.1.26
        double sign = x >= 0 ? 1 : -1;
        x = Math.abs(x);
        double t = 1 / (1 + 0.3275911 * x);
        double poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
        return sign * (1 - poly * Math.exp(-x * x));
    }

    static double cdf(double x, double mu, double sigma) {
        return 0.5 * (1 + erf((x - mu) / (sigma * Math.sqrt(2))));
    }

    public static void main(String[] args) {
        double mu = 70, sigma = 10;               // exam scores
        System.out.println(String.format("P(score above 85) = %.4f", 1 - cdf(85, mu, sigma)));
        System.out.println(String.format("a score of 80 beats %.2f%% of students", 100 * cdf(80, mu, sigma)));
        double lo = mu, hi = mu + 4 * sigma;      // the top 10% cutoff lies somewhere in here
        for (int i = 0; i < 40; i++) {            // binary search: halve the gap each time
            double mid = (lo + hi) / 2;
            if (cdf(mid, mu, sigma) < 0.9) {
                lo = mid;
            } else {
                hi = mid;
            }
        }
        System.out.println(String.format("top 10%% cutoff = %.2f", lo));
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('rv', '🎯', 'Random variables, PMF, PDF and CDF', f'''
<p>A <b>random variable</b> is a number that comes out of a chance event: the face of a die, the number of heads in ten flips, or the time until the next bus. We write it with a capital letter such as X, and a value it can take with a small letter such as x.</p>
<p>A <b>discrete</b> random variable takes separate values you can list (0, 1, 2, 3 and so on). A <b>continuous</b> one can take any value in a range, such as 1.73 m or 1.7312 m. The two kinds are described in slightly different ways.</p>
{fxs(fx('PMF (discrete)', 'p(x) = P(X = x) &nbsp; with &nbsp; Σ p(x) = 1', 'Probability mass function: the chance of each exact value. All the bars add up to 1.'),
         fx('PDF (continuous)', 'P(a ≤ X ≤ b) = ∫ₐᵇ f(x) dx &nbsp; with total area 1', 'Probability density function: probability is the AREA under the curve between a and b.'),
         fx('CDF (both)', 'F(x) = P(X ≤ x)', 'Cumulative distribution function: it climbs from 0 on the far left to 1 on the far right and never goes down.'))}
{table(['', 'Discrete', 'Continuous'], [
        ['values', 'a list you can count', 'any number in a range'],
        ['described by', 'PMF: bar heights', 'PDF: a smooth curve'],
        ['probability of one exact value', 'can be above 0', 'always 0'],
        ['probability of a range', 'add the bars', 'area under the curve'],
        ['examples', 'goals in a match, emails per day', 'height, waiting time, temperature'],
    ])}
<div class="warn">For a continuous variable, P(X = exactly 1.5) = 0, because a single point has no width and so no area. Only ranges have probability. That is also why a PDF can be taller than 1: its height is a density, not a probability.</div>
{life('The number of goals in a football match is discrete. The time until the next bus arrives is continuous.')}
''', kw=['random variable', 'discrete', 'continuous', 'pmf', 'pdf', 'cdf', 'probability mass function', 'probability density function', 'cumulative distribution']),

    part('expect', '⚖️', 'Expected value and variance', f'''
<p>The <b>expected value</b> E[X] (also called the mean μ) is the long run average of X if you could repeat the experiment forever. The <b>variance</b> measures how far values usually land from that mean, and the <b>standard deviation</b> σ is its square root, which brings the units back to normal.</p>
{fxs(fx('Expected value', 'E[X] = μ = Σ x · p(x)', 'Each value times its chance, all added up.'),
         fx('Variance', 'Var(X) = E[(X − μ)²] = E[X²] − μ²', 'The average squared distance from the mean. The second form is quicker by hand.'),
         fx('Standard deviation', 'σ = √Var(X)', 'Same units as X, so it is easier to picture.'))}
{worked('A fair die: find E[X], Var(X) and σ.', [
        'Each face has chance 1/6: <span class="eq">E[X] = (1 + 2 + 3 + 4 + 5 + 6) ÷ 6 = 21 ÷ 6 = 3.5</span>',
        'Square each face first: <span class="eq">E[X²] = (1 + 4 + 9 + 16 + 25 + 36) ÷ 6 = 91 ÷ 6 ≈ 15.1667</span>',
        'Subtract the squared mean: <span class="eq">Var(X) = 15.1667 − 3.5² = 15.1667 − 12.25 = 2.9167</span>',
        'Square root: <span class="eq">σ = √2.9167 ≈ 1.708</span>. A roll is usually about 1.7 away from 3.5.'])}
{fxs(fx('Shifting and scaling', 'E[aX + b] = a E[X] + b &nbsp;&nbsp; Var(aX + b) = a² Var(X)', 'Adding b moves the mean but not the spread. Multiplying by a stretches the spread by a.'),
         fx('Adding variables', 'E[X + Y] = E[X] + E[Y] &nbsp;&nbsp; Var(X + Y) = Var(X) + Var(Y)', 'The mean rule is always true. The variance rule needs X and Y to be independent.'))}
{code('expectation', 'Mean, variance and a dice game')}
{trick('The expected value does not have to be a possible result. Nobody ever rolls 3.5, yet 3.5 is where the average of many rolls ends up.')}
{life('Insurance companies and casinos run on expected value. Each single policy or bet is a gamble, but over thousands of them the average is very predictable.')}
''', kw=['expected value', 'mean', 'variance', 'standard deviation', 'E[X]', 'linearity of expectation', 'dice game']),

    part('binomial', '🪙', 'Bernoulli and binomial: counting successes', f'''
<p>A <b>Bernoulli</b> trial has two results: success (1) with chance p or failure (0) with chance 1 − p. A coin toss, a free throw and "did the user click?" are all Bernoulli trials. Repeat n independent Bernoulli trials and count the successes, and you get a <b>binomial</b> random variable.</p>
{fxs(fx('Bernoulli(p)', 'P(X = 1) = p, &nbsp; P(X = 0) = 1 − p', f'Mean p, variance p(1 − p).'),
         fx('Binomial(n, p)', 'P(X = k) = C(n, k) · pᵏ · (1 − p)ⁿ⁻ᵏ', 'C(n, k) counts the ways to place k successes among n tries. pᵏ(1 − p)ⁿ⁻ᵏ is the chance of any one of those ways.'),
         fx('Binomial mean and spread', 'μ = n p &nbsp;&nbsp; σ² = n p (1 − p)', 'Ten fair flips: mean 5 heads, variance 2.5, SD about 1.58.'))}
{viz('binom')}
{worked('What is the chance of exactly 3 heads in 5 fair coin flips?', [
        'Ways to choose which 3 flips are heads: <span class="eq">C(5, 3) = 10</span>',
        'Chance of any one such pattern, like HHHTT: <span class="eq">0.5³ × 0.5² = 0.5⁵ = 1/32</span>',
        'Multiply: <span class="eq">10 × 1/32 = 10/32 = 0.3125</span>',
        'Check: the mean is <span class="eq">n p = 5 × 0.5 = 2.5</span>, so 2 and 3 heads are the most likely counts.'])}
{code('binomial', 'The binomial distribution for 10 coin flips')}
{ml('A classifier that is right 90% of the time is tested on 200 new cases. The number correct is binomial with mean 200 × 0.9 = 180 and SD √(200 × 0.9 × 0.1) = √18 ≈ 4.24. So a score between about 172 and 188 is ordinary luck, not a better or worse model.')}
''', kw=['bernoulli', 'binomial distribution', 'success probability', 'n choose k', 'coin flips', 'number of successes']),

    part('poisson', '📞', 'Poisson, uniform and exponential', f'''
<p>The <b>Poisson</b> distribution counts how many events happen in a fixed stretch of time or space when they arrive at random at an average rate λ (lambda). Calls to a help desk per hour, typos per page and goals per match are classic examples.</p>
{fx('Poisson(λ)', f'P(X = k) = {frac("e<sup>−λ</sup> · λᵏ", "k!")}', 'The mean and the variance are both λ.')}
{worked('A help desk gets 3 calls per hour on average. What is the chance of exactly 2 calls in the next hour?', [
        'Here <span class="eq">λ = 3</span> and <span class="eq">k = 2</span>',
        '<span class="eq">e⁻³ ≈ 0.0498</span> and <span class="eq">3² ÷ 2! = 9 ÷ 2 = 4.5</span>',
        'Multiply: <span class="eq">0.0498 × 4.5 ≈ 0.2240</span>',
        'And no calls at all: <span class="eq">P(X = 0) = e⁻³ ≈ 0.0498</span>, about 1 hour in 20.'])}
{table(['Distribution', 'Type', 'Parameters', 'Mean', 'Variance', 'Typical use'], [
        ['Bernoulli', 'discrete', 'p', 'p', 'p(1 − p)', 'one yes or no'],
        ['Binomial', 'discrete', 'n, p', 'np', 'np(1 − p)', 'successes in n tries'],
        ['Poisson', 'discrete', 'λ', 'λ', 'λ', 'events per hour'],
        ['Uniform', 'continuous', 'a, b', '(a + b) ÷ 2', '(b − a)² ÷ 12', 'a random number in a range'],
        ['Normal', 'continuous', 'μ, σ', 'μ', 'σ²', 'heights, measurement noise'],
        ['Exponential', 'continuous', 'λ', '1 ÷ λ', '1 ÷ λ²', 'waiting time until the next event'],
    ])}
{trick('Poisson is what the binomial becomes when n is huge and p is tiny, with n p = λ. Many people (huge n) each with a tiny chance of calling in this hour (tiny p) gives a Poisson number of calls.')}
{ml('Models that predict counts, such as the number of bike rentals per hour, often use Poisson regression, which assumes the count follows a Poisson distribution whose λ depends on the inputs.')}
''', kw=['poisson distribution', 'lambda', 'rate', 'uniform distribution', 'exponential distribution', 'waiting time', 'count data']),

    part('normal', '🔔', 'The normal distribution and z-scores', f'''
<p>The <b>normal</b> (or Gaussian) distribution is the famous bell curve. It is set by two numbers: the mean μ, which places the centre, and the standard deviation σ, which sets the width. Heights, measurement errors and exam scores are often close to normal.</p>
{fxs(fx('Normal PDF', f'f(x) = {frac("1", "σ √(2π)")} · e<sup>−(x − μ)² ÷ (2σ²)</sup>', 'The curve is symmetric about μ and its peak height is 1 ÷ (σ√(2π)).'),
         fx('z-score', f'z = {frac("x − μ", "σ")}', 'How many standard deviations x is from the mean. Any normal becomes the standard normal N(0, 1) this way.'))}
{viz('normal')}
{table(['Range', 'Share of values', 'Outside the range'], [
        ['μ ± 1σ', '68.27%', 'about 1 in 3'],
        ['μ ± 2σ', '95.45%', 'about 1 in 22'],
        ['μ ± 3σ', '99.73%', 'about 1 in 370'],
    ])}
{worked('Adult heights are normal with μ = 170 cm and σ = 8 cm. How unusual are 186 cm and 180 cm?', [
        'z-score of 186: <span class="eq">(186 − 170) ÷ 8 = 16 ÷ 8 = 2</span>',
        '95.45% lie within 2σ, so 4.55% lie outside, half on each side: <span class="eq">4.55% ÷ 2 ≈ 2.3%</span> are taller than 186 cm',
        'z-score of 180: <span class="eq">(180 − 170) ÷ 8 = 1.25</span>',
        'From a z table, <span class="eq">P(Z ≤ 1.25) ≈ 0.8944</span>, so about <span class="eq">1 − 0.8944 = 0.1056</span>, roughly 10.6%, are taller than 180 cm.'])}
{code('normal', 'Areas under the bell curve')}
{trick('Remember 68, 95, 99.7. Within 1, 2 and 3 standard deviations of the mean you find about 68%, 95% and 99.7% of a normal population.')}
{ml('Standardising a feature means turning every value into its z-score. Then every feature has mean 0 and SD 1, so no feature dominates just because of its units, and gradient descent runs much more smoothly. Neural network weights are also often started with small random normal values.')}
''', kw=['normal distribution', 'gaussian', 'bell curve', 'z-score', 'standard normal', '68 95 99.7 rule', 'standardisation']),

    part('clt', '📊', 'The central limit theorem', f'''
<p>The <b>central limit theorem</b> (CLT) explains why the bell curve is everywhere. Take many independent random values from almost any distribution (it only needs a finite variance), and their average is close to normally distributed. The original shape can be flat, lopsided or just 0 and 1. The average still ends up bell shaped.</p>
{fxs(fx('Central limit theorem', f'X̄ = {frac("X₁ + X₂ + … + Xₙ", "n")} &nbsp; is roughly &nbsp; N(μ, σ² ÷ n)', 'The average has the same centre μ as one value, but a narrower spread.'),
         fx('Standard error', f'SE = {frac("σ", "√n")}', 'The SD of an average of n values. It shrinks as the sample grows.'))}
{viz('clt')}
{worked('One die has σ ≈ 1.708. How spread out is the average of 4 dice? And of 16?', [
        'For n = 4: <span class="eq">SE = 1.708 ÷ √4 = 1.708 ÷ 2 ≈ 0.854</span>',
        'For n = 16: <span class="eq">SE = 1.708 ÷ √16 = 1.708 ÷ 4 ≈ 0.427</span>',
        'Four times as many dice halved the spread. That is the square root at work.',
        'Both averages still centre on <span class="eq">μ = 3.5</span>.'])}
{code('clt', 'The average of more dice clusters closer to 3.5')}
{trick('The √n rule: 4 times more data halves the error, and 100 times more data cuts it to a tenth. Precision gets expensive.')}
{ml('When a model scores 85% accuracy on 400 test cases, the CLT gives the error bar: SE = √(0.85 × 0.15 ÷ 400) ≈ 0.018, so the true accuracy is probably within about 85% ± 3.6%. Mini batch gradients in training are averages too, so they are noisy estimates of the full gradient, and bigger batches make that noise smaller.')}
''', kw=['central limit theorem', 'clt', 'sample mean', 'standard error', 'square root n', 'sampling distribution']),

    part('cov', '🔗', 'Covariance, correlation and distributions in ML', f'''
<p>So far each variable lived alone. <b>Covariance</b> asks whether two variables move together. If X is above its mean when Y is above its mean, the covariance is positive. <b>Correlation</b> rescales covariance to a number between −1 and 1 so it is easy to read.</p>
{fxs(fx('Sample covariance', f'Cov(X, Y) = {frac("Σ (xᵢ − x̄)(yᵢ − ȳ)", "n − 1")}', 'Positive: they rise together. Negative: one rises as the other falls.'),
         fx('Correlation', f'r = {frac("Cov(X, Y)", "s<sub>x</sub> · s<sub>y</sub>")}', 'Always between −1 and 1. r = 1 is a perfect rising straight line.'))}
{code('covariance', 'Hours studied and test scores')}
<div class="warn">Correlation is not causation. Ice cream sales and sunburn are correlated because both rise in hot weather. Also, r only measures straight line relationships: for x = −2, −1, 0, 1, 2 and y = x², r is exactly 0 even though y depends completely on x.</div>
{table(['Distribution or idea', 'Where machine learning uses it'], [
        ['Bernoulli', 'binary labels, and the output of logistic regression (Chapter 12)'],
        ['Categorical', 'multi class labels and the softmax output layer'],
        ['Normal', 'noise in linear regression, weight initialisation, Gaussian naive Bayes'],
        ['Poisson', 'regression on counts such as visits or sales'],
        ['Central limit theorem', 'error bars on accuracy, A/B tests (Chapter 11), noise in mini batch gradients'],
        ['Covariance matrix', 'PCA (Chapter 5) and correlated features'],
    ])}
{trick('Covariance has awkward units (hours × points). Correlation has no units, which is why people quote r instead.')}
''', kw=['covariance', 'correlation', 'pearson r', 'correlation is not causation', 'covariance matrix', 'distributions in machine learning']),
]

INFO = {
    'title': 'A distribution tells you which values are likely',
    'panels': [
        {'s': [['e', '🎯'], ['t', 'PMF, PDF, CDF', {'b': 1}]], 'h': 'Describe', 't': 'Bars for discrete, curves for continuous.', 'more': 'Area under a PDF is probability.'},
        {'s': [['e', '⚖️'], ['t', 'E[X] = Σ x p(x)', {'b': 1}]], 'h': 'Centre and spread', 't': 'Mean and variance.', 'more': 'σ = √Var(X).'},
        {'s': [['e', '🔔'], ['t', 'z = (x − μ) ÷ σ', {'b': 1}]], 'h': 'Bell curve', 't': '68, 95, 99.7.', 'more': 'z-scores put everything on one scale.'},
        {'s': [['e', '📊'], ['t', 'SE = σ ÷ √n', {'b': 1}]], 'h': 'CLT', 't': 'Averages become normal.', 'more': '4 times the data halves the error.'},
    ],
    'remember': 'A random variable is described by its PMF (discrete) or PDF (continuous), and the CDF gives P(X ≤ x). E[X] = Σ x p(x) and Var(X) = E[X²] − μ². Binomial counts successes in n tries (mean np), Poisson counts events at rate λ (mean and variance λ). The normal curve holds 68%, 95% and 99.7% within 1, 2 and 3 σ. The average of n values has SD σ ÷ √n and is close to normal.',
}

REAL = [
    ['🏭', 'Quality control', 'Factories track measurements against the normal curve and investigate anything beyond 3 standard deviations, since only about 3 in 1000 parts land there by chance.'],
    ['📞', 'Call centres', 'Staffing plans use the Poisson distribution of calls per hour to decide how many agents keep waiting times short.'],
    ['🗳️', 'Opinion polls', 'A poll of 1000 people has a margin of error near ±3% because of the central limit theorem and the √n rule.'],
]

K.say('top', 'Welcome',
      'A distribution tells you which values a random quantity is likely to take. You will meet the mean and variance, build binomial bars one at a time, shade areas under the bell curve, and watch averages turn bell shaped by themselves through the central limit theorem.',
      'Distribution बताता है कि कोई random मात्रा कौन से मान ले सकती है। आप mean और variance सीखेंगे, binomial bars एक एक करके बनाएँगे, bell curve के नीचे का क्षेत्र रंगेंगे, और central limit theorem से औसत को bell आकार में बदलते देखेंगे।',
      'Distribution ಯಾವ ಮೌಲ್ಯಗಳು ಸಾಧ್ಯ ಎಂದು ಹೇಳುತ್ತದೆ. Mean, variance, binomial, bell curve ಮತ್ತು central limit theorem ಕಲಿಯುತ್ತೀರಿ.',
      'Distribution କେଉଁ ମୂଲ୍ୟ ସମ୍ଭବ ତାହା କହେ। Mean, variance, binomial, bell curve ଓ central limit theorem ଶିଖିବେ।',
      'التوزيع يخبرك بالقيم التي يرجح أن تأخذها كمية عشوائية. ستتعرف على المتوسط والتباين، وتبني أعمدة ذات الحدين واحدًا تلو الآخر، وتظلل مساحات تحت منحنى الجرس، وترى المتوسطات تأخذ شكل الجرس وحدها بفضل مبرهنة النهاية المركزية.',
      'Eine Verteilung sagt dir, welche Werte eine Zufallsgröße wahrscheinlich annimmt. Du lernst Erwartungswert und Varianz kennen, baust Binomialbalken einzeln auf, färbst Flächen unter der Glockenkurve und siehst, wie Mittelwerte durch den zentralen Grenzwertsatz von selbst glockenförmig werden.')
K.say('rv', 'Random variables',
      'A random variable is a number produced by chance. Discrete ones have values you can list and are described by a probability mass function. Continuous ones can take any value in a range, and probability is the area under the density curve. The cumulative distribution gives the chance of being at most x.',
      'Random variable संयोग से बनी एक संख्या है। Discrete के मान गिने जा सकते हैं और PMF से बताए जाते हैं। Continuous किसी भी मान को ले सकता है, और probability density curve के नीचे का क्षेत्र है। CDF बताता है कि मान x या उससे कम होने की संभावना क्या है।',
      'Random variable ಸಂಯೋಗದಿಂದ ಬರುವ ಸಂಖ್ಯೆ. Discrete ಗೆ PMF, continuous ಗೆ PDF ಕೆಳಗಿನ ಪ್ರದೇಶ. CDF ಎಂದರೆ x ಅಥವಾ ಕಡಿಮೆ ಆಗುವ ಸಾಧ್ಯತೆ.',
      'Random variable ସଂଯୋଗରୁ ଆସୁଥିବା ସଂଖ୍ୟା। Discrete ପାଇଁ PMF, continuous ପାଇଁ PDF ତଳର କ୍ଷେତ୍ର। CDF ମାନେ x କିମ୍ବା କମ୍ ହେବାର ସମ୍ଭାବନା।',
      'المتغير العشوائي عدد ينتج عن الصدفة. المتقطع قيمه قابلة للعد وتصفه دالة الكتلة الاحتمالية. والمتصل يأخذ أي قيمة في مدى، والاحتمال هو المساحة تحت منحنى الكثافة. ودالة التوزيع التراكمي تعطي احتمال ألا تزيد القيمة على x.',
      'Eine Zufallsvariable ist eine Zahl, die der Zufall erzeugt. Diskrete haben aufzählbare Werte und werden durch eine Wahrscheinlichkeitsfunktion beschrieben. Stetige können jeden Wert in einem Bereich annehmen, und die Wahrscheinlichkeit ist die Fläche unter der Dichte. Die Verteilungsfunktion gibt die Chance, höchstens x zu sein.')
K.say('expect', 'Mean and variance',
      'The expected value is the long run average: each value times its chance, added up. The variance is the average squared distance from the mean, and the standard deviation is its square root. A fair die has mean three point five and standard deviation about one point seven.',
      'Expected value लंबे समय का औसत है: हर मान गुणा उसकी संभावना, सब जोड़कर। Variance mean से औसत वर्ग दूरी है, और standard deviation उसका वर्गमूल। Fair die का mean साढ़े तीन और standard deviation लगभग एक दशमलव सात है।',
      'Expected value ದೀರ್ಘಾವಧಿಯ ಸರಾಸರಿ. Variance mean ನಿಂದ ಸರಾಸರಿ ವರ್ಗ ದೂರ, standard deviation ಅದರ ವರ್ಗಮೂಲ.',
      'Expected value ଦୀର୍ଘ ସମୟର ହାରାହାରି। Variance mean ଠାରୁ ହାରାହାରି ବର୍ଗ ଦୂରତା, standard deviation ତାର ବର୍ଗମୂଳ।',
      'القيمة المتوقعة هي المتوسط على المدى الطويل: كل قيمة في احتمالها ثم الجمع. والتباين متوسط مربع البعد عن المتوسط، والانحراف المعياري جذره. حجر النرد العادل متوسطه ثلاثة ونصف وانحرافه نحو واحد وسبعة أعشار.',
      'Der Erwartungswert ist der langfristige Durchschnitt: jeder Wert mal seine Chance, alles addiert. Die Varianz ist der mittlere quadrierte Abstand vom Mittelwert, die Standardabweichung ihre Wurzel. Ein fairer Würfel hat Mittelwert drei Komma fünf und Standardabweichung etwa eins Komma sieben.')
K.say('binomial', 'Binomial',
      'A binomial variable counts successes in n independent tries, each with chance p. The chance of k successes is n choose k, times p to the k, times one minus p to the n minus k. Its mean is n times p. Move the sliders and press play to build the bars one by one.',
      'Binomial variable n स्वतंत्र प्रयासों में सफलताएँ गिनता है, हर एक की संभावना p। k सफलताओं की संभावना n choose k गुणा p की घात k गुणा एक माइनस p की घात n माइनस k है। इसका mean n गुणा p है। Sliders बदलें और play दबाएँ।',
      'Binomial n ಪ್ರಯತ್ನಗಳಲ್ಲಿ ಯಶಸ್ಸುಗಳನ್ನು ಎಣಿಸುತ್ತದೆ. Mean n ಗುಣಿಸು p. Sliders ಬದಲಿಸಿ play ಒತ್ತಿ.',
      'Binomial n ଚେଷ୍ଟାରେ ସଫଳତା ଗଣେ। Mean n ଗୁଣନ p। Sliders ବଦଳାଇ play ଦବାନ୍ତୁ।',
      'متغير ذي الحدين يعد النجاحات في n محاولة مستقلة لكل منها احتمال p. احتمال k نجاحات هو توفيق n على k مضروبًا في p أس k وفي واحد ناقص p أس n ناقص k. ومتوسطه n في p. حرك المنزلقات واضغط تشغيل لبناء الأعمدة.',
      'Eine binomiale Größe zählt Erfolge in n unabhängigen Versuchen mit je Chance p. Die Chance auf k Erfolge ist n über k mal p hoch k mal eins minus p hoch n minus k. Der Mittelwert ist n mal p. Verschiebe die Regler und drücke Play.')
K.say('poisson', 'Poisson and friends',
      'The Poisson distribution counts random events in a fixed time at average rate lambda. Its mean and variance are both lambda. The uniform distribution spreads chance evenly over a range, and the exponential describes the waiting time until the next event.',
      'Poisson distribution तय समय में औसत दर lambda पर होने वाली घटनाएँ गिनता है। इसका mean और variance दोनों lambda हैं। Uniform distribution संभावना को बराबर फैलाता है, और exponential अगली घटना तक का इंतज़ार बताता है।',
      'Poisson ನಿಗದಿತ ಸಮಯದಲ್ಲಿ ಘಟನೆಗಳನ್ನು ಎಣಿಸುತ್ತದೆ. Mean ಮತ್ತು variance ಎರಡೂ lambda.',
      'Poisson ନିର୍ଦ୍ଧାରିତ ସମୟରେ ଘଟଣା ଗଣେ। Mean ଓ variance ଦୁହେଁ lambda।',
      'توزيع بواسون يعد الأحداث العشوائية في زمن محدد بمعدل متوسط لامدا، ومتوسطه وتباينه كلاهما لامدا. والتوزيع المنتظم يوزع الاحتمال بالتساوي على مدى، والأسي يصف زمن الانتظار حتى الحدث التالي.',
      'Die Poissonverteilung zählt zufällige Ereignisse in einer festen Zeit bei mittlerer Rate Lambda. Erwartungswert und Varianz sind beide Lambda. Die Gleichverteilung verteilt die Chance gleichmäßig über einen Bereich, die Exponentialverteilung beschreibt die Wartezeit bis zum nächsten Ereignis.')
K.say('normal', 'The bell curve',
      'The normal distribution is set by its mean and standard deviation. About sixty eight percent of values lie within one standard deviation, ninety five percent within two, and ninety nine point seven percent within three. A z score says how many standard deviations a value is from the mean.',
      'Normal distribution mean और standard deviation से तय होता है। लगभग अड़सठ प्रतिशत मान एक standard deviation के भीतर, पंचानवे प्रतिशत दो के भीतर, और निन्यानवे दशमलव सात प्रतिशत तीन के भीतर होते हैं। Z score बताता है कि मान mean से कितने standard deviations दूर है।',
      'Normal distribution mean ಮತ್ತು standard deviation ನಿಂದ ನಿರ್ಧಾರ. 68, 95, 99.7 ನಿಯಮ. Z score ಎಷ್ಟು standard deviations ದೂರ ಎಂದು ಹೇಳುತ್ತದೆ.',
      'Normal distribution mean ଓ standard deviation ରୁ ସ୍ଥିର। 68, 95, 99.7 ନିୟମ। Z score କେତେ standard deviations ଦୂର ତାହା କହେ।',
      'التوزيع الطبيعي يحدده المتوسط والانحراف المعياري. نحو ثمانية وستين بالمئة من القيم تقع ضمن انحراف معياري واحد، وخمسة وتسعين ضمن اثنين، وتسعة وتسعين وسبعة أعشار ضمن ثلاثة. ودرجة z تقول كم انحرافًا معياريًا تبعد القيمة عن المتوسط.',
      'Die Normalverteilung ist durch Mittelwert und Standardabweichung festgelegt. Etwa achtundsechzig Prozent der Werte liegen innerhalb einer Standardabweichung, fünfundneunzig Prozent innerhalb von zwei und neunundneunzig Komma sieben Prozent innerhalb von drei. Ein z Wert sagt, wie viele Standardabweichungen ein Wert vom Mittelwert entfernt ist.')
K.say('clt', 'Central limit theorem',
      'Average many independent values and the result is close to normal, whatever the starting shape. The average keeps the same centre, but its spread shrinks to sigma divided by the square root of n. Pick a lopsided start, raise n, and watch the bell appear.',
      'कई स्वतंत्र मानों का औसत लें तो परिणाम लगभग normal होता है, शुरुआती आकार चाहे जो हो। औसत का केंद्र वही रहता है, पर फैलाव sigma बटा n का वर्गमूल हो जाता है। टेढ़ा आकार चुनें, n बढ़ाएँ, और bell बनते देखें।',
      'ಹಲವು ಮೌಲ್ಯಗಳ ಸರಾಸರಿ normal ಆಗುತ್ತದೆ. ಹರಡುವಿಕೆ sigma ಭಾಗಿಸು n ನ ವರ್ಗಮೂಲ.',
      'ଅନେକ ମୂଲ୍ୟର ହାରାହାରି normal ହୁଏ। ବିସ୍ତାର sigma ଭାଗ n ର ବର୍ଗମୂଳ।',
      'خذ متوسط قيم مستقلة كثيرة فتحصل على توزيع قريب من الطبيعي مهما كان الشكل الأصلي. يبقى المركز نفسه، لكن الانتشار يصغر إلى سيغما مقسومة على جذر n. اختر شكلًا مائلًا وزد n وشاهد الجرس يظهر.',
      'Mittelst du viele unabhängige Werte, ist das Ergebnis fast normalverteilt, egal welche Form du startest. Die Mitte bleibt gleich, aber die Streuung schrumpft auf Sigma durch Wurzel aus n. Wähle eine schiefe Form, erhöhe n und sieh die Glocke entstehen.')
K.say('cov', 'Covariance and correlation',
      'Covariance says whether two variables move together. Correlation rescales it to lie between minus one and one. Remember that correlation is not causation, and that it only measures straight line patterns.',
      'Covariance बताता है कि दो variables साथ चलते हैं या नहीं। Correlation इसे माइनस एक से एक के बीच ले आता है। याद रखें, correlation causation नहीं है, और यह केवल सीधी रेखा वाले pattern मापता है।',
      'Covariance ಎರಡು variables ಒಟ್ಟಿಗೆ ಚಲಿಸುತ್ತವೆಯೇ ಎಂದು ಹೇಳುತ್ತದೆ. Correlation ಮೈನಸ್ ಒಂದರಿಂದ ಒಂದು.',
      'Covariance ଦୁଇଟି variables ଏକାଠି ଚାଲନ୍ତି କି ନାହିଁ କହେ। Correlation ମାଇନସ୍ ଏକରୁ ଏକ।',
      'التغاير يخبرك هل يتحرك متغيران معًا. والارتباط يعيد قياسه ليقع بين سالب واحد وواحد. وتذكر أن الارتباط ليس سببية، وأنه يقيس الأنماط الخطية فقط.',
      'Die Kovarianz sagt, ob sich zwei Größen gemeinsam bewegen. Die Korrelation skaliert sie auf minus eins bis eins. Denk daran, dass Korrelation keine Kausalität ist und nur geradlinige Muster misst.')
K.say('practice', 'Practice',
      'Practice time. Work out the value of a raffle ticket, free throw chances, help desk calls with Poisson, and exam cutoffs with the normal curve.',
      'अभ्यास का समय। Raffle ticket का मूल्य, free throw की संभावना, Poisson से help desk calls, और normal curve से exam cutoff निकालें।',
      'ಅಭ್ಯಾಸದ ಸಮಯ. Raffle, free throws, Poisson calls ಮತ್ತು exam cutoff.',
      'ଅଭ୍ୟାସ ସମୟ। Raffle, free throws, Poisson calls ଓ exam cutoff।',
      'وقت التدريب. احسب قيمة تذكرة اليانصيب، وفرص الرميات الحرة، ومكالمات مكتب المساعدة ببواسون، وحدود الامتحان بالمنحنى الطبيعي.',
      'Zeit zum Üben. Berechne den Wert eines Tombolaloses, Freiwurfchancen, Anrufe mit Poisson und Prüfungsgrenzen mit der Normalverteilung.')

# ---------------------------------------------------------------- practice
K.practice('raffle', 'e', 'Is a raffle ticket worth it?', 'p_raffle',
           '<p>A raffle sells 1000 tickets at 5 each. The prizes are one of 1000, two of 500 and five of 100, and each prize goes to a different ticket. Find the expected prize and profit per ticket, the SD of the prize, and what the organiser keeps.</p>',
           'expected prize per ticket  = 2.50\nexpected profit per ticket = -2.50\nSD of the prize            = 39.29\nthe organiser keeps 2500 whatever happens',
           'E[prize] = (sum of all prizes) ÷ (number of tickets), because every prize has a 1 in 1000 chance of being yours.',
           '<p>The prizes add up to 1000 + 500 + 500 + 5 × 100 = 2500, so E[prize] = 2500 ÷ 1000 = 2.50. Paying 5 for an expected 2.50 gives an expected profit of −2.50. For the spread, E[prize²] = (1000² + 2 × 500² + 5 × 100²) ÷ 1000 = 1550000 ÷ 1000 = 1550, so Var = 1550 − 2.5² = 1543.75 and SD ≈ 39.29. A huge SD next to a small mean means most tickets win nothing while a few win a lot.</p>',
           'O(prizes)', 'O(1)')
K.practice('freethrow', 'm', 'Free throws', 'p_freethrow',
           '<p>A basketball player scores 70% of free throws. In 5 independent attempts, find P(exactly 3), P(at least 4), P(at least 1), and the mean and SD of the number scored.</p>',
           'P(exactly 3)  = 0.3087\nP(at least 4) = 0.5282\nP(at least 1) = 0.9976\nmean = 3.50, SD = 1.0247',
           'This is Binomial(5, 0.7). For "at least 1" use the complement.',
           '<p>P(3) = C(5, 3) × 0.7³ × 0.3² = 10 × 0.343 × 0.09 = 0.3087. "At least 4" means 4 or 5: 5 × 0.7⁴ × 0.3 + 0.7⁵ = 0.36015 + 0.16807 = 0.5282. "At least 1" is 1 − P(0) = 1 − 0.3⁵ = 1 − 0.00243 = 0.9976. The mean is np = 3.5 and the SD is √(5 × 0.7 × 0.3) = √1.05 ≈ 1.025.</p>',
           'O(n)', 'O(1)')
K.practice('poisson', 'h', 'Calls at the help desk', 'p_poisson',
           '<p>A help desk receives on average 3 calls per hour, at random. Find the chance of no calls, exactly 2 calls, at least 1 call and more than 5 calls in an hour.</p>',
           'P(no calls)        = 0.0498\nP(exactly 2 calls) = 0.2240\nP(at least 1 call) = 0.9502\nP(more than 5)     = 0.0839',
           'Use the Poisson formula with λ = 3. "More than 5" is 1 minus P(0) + P(1) + … + P(5).',
           '<p>P(0) = e⁻³ ≈ 0.0498. P(2) = e⁻³ × 3² ÷ 2! = 0.0498 × 4.5 ≈ 0.2240. At least one call is the complement of none: 1 − 0.0498 = 0.9502. For more than 5, add P(0) to P(5): 0.0498 + 0.1494 + 0.2240 + 0.2240 + 0.1680 + 0.1008 ≈ 0.9161, and 1 − 0.9161 = 0.0839. So in about 1 hour out of 12 the desk gets 6 or more calls, which tells the manager how often extra staff are needed.</p>',
           'O(k)', 'O(1)')
K.practice('exam', 'x', 'Exam cutoffs on the bell curve', 'p_exam',
           '<p>Exam scores are normal with mean 70 and SD 10. Find P(score above 85), the percentile of a score of 80, and the score needed to be in the top 10%.</p>',
           'P(score above 85) = 0.0668\na score of 80 beats 84.13% of students\ntop 10% cutoff = 82.82',
           'Convert to z-scores. For the cutoff, search for the score whose CDF is 0.9.',
           '<p>85 has z = (85 − 70) ÷ 10 = 1.5, and P(Z > 1.5) ≈ 0.0668. 80 has z = 1, and P(Z ≤ 1) ≈ 0.8413, so it beats about 84% of students. For the top 10% we need the z with P(Z ≤ z) = 0.9, which is z ≈ 1.2816, so the cutoff is 70 + 1.2816 × 10 ≈ 82.82. The program finds it by binary search: it keeps halving the interval [70, 110] while checking which side of 0.9 the CDF is on.</p>',
           'O(log(1 ÷ precision))', 'O(1)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which of these is a continuous random variable?', ['the number of heads in 10 flips', 'a person\'s height', 'the number of emails today', 'the face of a die'], 1, 'Can it take any value in a range?', 'Height can be 1.70 m, 1.705 m and everything in between.')
K.quiz('e', 'What is the expected value of one roll of a fair die?', ['3', '3.5', '4', '6'], 1, 'Add the faces and divide by 6.', '21 ÷ 6 = 3.5.')
K.quiz('e', 'The probabilities in a PMF must add up to…', ['0', '0.5', '1', 'any number'], 2, 'Something must happen.', 'All the bars together cover every outcome, so they add to 1.')
K.quiz('e', 'The standard deviation is the ___ of the variance.', ['square', 'square root', 'half', 'double'], 1, 'It brings the units back.', 'σ = √Var(X).')
K.quiz('m', 'A binomial variable has n = 10 and p = 0.3. What is its mean?', ['0.3', '3', '7', '2.1'], 1, 'Mean = n p.', '10 × 0.3 = 3. (2.1 is the variance.)')
K.quiz('m', 'About what share of a normal distribution lies within 2 standard deviations of the mean?', ['68%', '95%', '99.7%', '50%'], 1, '68, 95, 99.7.', 'About 95.45%.')
K.quiz('m', 'Which situation fits a Poisson distribution best?', ['heads in 10 tosses', 'customers arriving in an hour', 'a person\'s height', 'the face of a die'], 1, 'Random events at an average rate.', 'Arrivals in a time window are the classic Poisson case.')
K.quiz('m', 'IQ scores have mean 100 and SD 15. What is the z-score of 130?', ['1', '2', '3', '30'], 1, 'z = (x − μ) ÷ σ.', '(130 − 100) ÷ 15 = 2.')
K.quiz('m', 'Var(2X) equals…', ['2 Var(X)', '4 Var(X)', 'Var(X)', 'Var(X) + 2'], 1, 'Var(aX) = a² Var(X).', 'Doubling every value doubles distances, which squares to 4 times.')
K.quiz('h', 'For a continuous random variable, P(X = exactly 1.5) is…', ['0', 'the PDF value at 1.5', '1', '0.5'], 0, 'A single point has no width.', 'Only intervals have area, so a single exact value has probability 0.')
K.quiz('h', 'The central limit theorem says the average of many independent values…', ['is always exactly normal', 'is approximately normal whatever the original shape (with finite variance)', 'equals the median', 'has the same SD as one value'], 1, 'Think of the CLT animation.', 'The average tends to a normal shape with SD σ ÷ √n.')
K.quiz('h', 'Averaging n independent values shrinks the SD by a factor of…', ['n', '√n', 'n²', '2'], 1, 'Standard error.', 'SE = σ ÷ √n.')
K.quiz('h', 'A correlation of r = 0 means…', ['no relationship of any kind', 'no straight line relationship', 'the variables are independent', 'the covariance is 1'], 1, 'Think of y = x².', 'r only detects straight line patterns. Curved relationships can have r = 0.')
K.quiz('x', 'How can a PDF have a height greater than 1?', ['it never can', 'it is a density: probability is the area under it, not its height', 'probabilities can be above 1', 'only for discrete variables'], 1, 'A narrow tall curve can still have area 1.', 'A normal curve with σ = 0.1 peaks near 3.99, yet its total area is still 1.')
K.quiz('x', 'X and Y are independent. Var(X − Y) equals…', ['Var(X) − Var(Y)', 'Var(X) + Var(Y)', '0', '(Var(X) − Var(Y))²'], 1, 'Var(−Y) = (−1)² Var(Y).', 'Subtracting still adds uncertainty: Var(X − Y) = Var(X) + Var(Y).')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What is the expected value of one roll of a fair die?', '3.5', 'Each face times 1/6, added up.', [
    'Add the faces: <span class="eq">1 + 2 + 3 + 4 + 5 + 6 = 21</span>',
    'Each face has chance <span class="eq">1/6</span>, so multiply the sum by it',
    '<span class="eq">21 × 1/6 = 21 ÷ 6 = 3.5</span>',
], check=3.5)
K.calc('e', 'A spinner gives 1 with chance 0.5, 2 with chance 0.3 and 5 with chance 0.2. What is E[X]?', '2.1', 'Value times chance, then add.', [
    '<span class="eq">1 × 0.5 = 0.5</span>',
    '<span class="eq">2 × 0.3 = 0.6</span> and <span class="eq">5 × 0.2 = 1.0</span>',
    'Add: <span class="eq">0.5 + 0.6 + 1.0 = 2.1</span>',
], check=2.1, tol=1e-9)
K.calc('e', 'A variable has variance 16. What is its standard deviation?', '4', 'Square root.', [
    '<span class="eq">σ = √Var</span>',
    '<span class="eq">√16 = 4</span>',
    'Check: <span class="eq">4 × 4 = 16</span> ✔',
], check=4)
K.calc('e', 'Exam scores have mean 70 and SD 10. What is the z-score of 85?', '1.5', 'z = (x − μ) ÷ σ.', [
    'Distance from the mean: <span class="eq">85 − 70 = 15</span>',
    'Divide by the SD: <span class="eq">15 ÷ 10 = 1.5</span>',
    'So 85 is <span class="eq">1.5</span> standard deviations above the mean',
], check=1.5)
K.calc('m', 'Four fair coins are flipped. What is P(exactly 2 heads)?', '0.375', 'C(4, 2) × 0.5⁴.', [
    'Ways to pick the 2 heads: <span class="eq">C(4, 2) = 6</span>',
    'Chance of any one pattern: <span class="eq">0.5⁴ = 1/16</span>',
    '<span class="eq">6 × 1/16 = 6/16 = 0.375</span>',
], check=0.375)
K.calc('m', 'What is the variance of one fair die roll? Give 4 decimal places.', '2.9167', 'E[X²] − μ².', [
    '<span class="eq">E[X²] = (1 + 4 + 9 + 16 + 25 + 36) ÷ 6 = 91 ÷ 6 ≈ 15.1667</span>',
    '<span class="eq">μ² = 3.5² = 12.25</span>',
    '<span class="eq">Var = 15.1667 − 12.25 = 2.9167</span> (exactly 35/12)',
], check=35 / 12, tol=0.0001)
K.calc('m', 'Binomial with n = 20 and p = 0.25. What is the SD? Give 2 decimal places.', '1.94', 'σ = √(n p (1 − p)).', [
    'Variance: <span class="eq">20 × 0.25 × 0.75 = 3.75</span>',
    'Square root: <span class="eq">√3.75 ≈ 1.936</span>',
    'Rounded: <span class="eq">1.94</span>. The mean is <span class="eq">20 × 0.25 = 5</span>.',
], check=3.75 ** 0.5, tol=0.005)
K.calc('m', 'Pay 2 to roll a die and win 10 on a six. What is the expected profit per game? Give 2 decimal places.', '−0.33', 'Net results: +8 with chance 1/6, −2 with chance 5/6.', [
    'Win: <span class="eq">10 − 2 = 8</span> with chance <span class="eq">1/6</span>, giving <span class="eq">8/6 ≈ 1.333</span>',
    'Lose: <span class="eq">−2</span> with chance <span class="eq">5/6</span>, giving <span class="eq">−10/6 ≈ −1.667</span>',
    'Add: <span class="eq">8/6 − 10/6 = −2/6 ≈ −0.33</span>. You lose about a third per game.',
], check=-1 / 3, tol=0.005)
K.calc('h', 'Calls arrive at an average rate of 2 per hour (Poisson). What is P(no calls in an hour)? Give 4 decimal places.', '0.1353', 'P(0) = e^(−λ).', [
    'Formula with k = 0: <span class="eq">P(0) = e⁻² × 2⁰ ÷ 0!</span>',
    'Both <span class="eq">2⁰</span> and <span class="eq">0!</span> equal 1',
    '<span class="eq">e⁻² ≈ 0.1353</span>',
], check=2.718281828459045 ** -2, tol=0.0001)
K.calc('h', 'Heights are normal with mean 170 cm and SD 8 cm. Roughly what percentage lie between 162 and 178 cm?', '68', 'How many SDs from the mean are 162 and 178?', [
    '<span class="eq">162 = 170 − 8</span> and <span class="eq">178 = 170 + 8</span>',
    'That is the range <span class="eq">μ ± 1σ</span>',
    'The 68, 95, 99.7 rule gives about <span class="eq">68%</span> (more exactly 68.27%)',
], check=68.27, tol=0.5, unit='%')
K.calc('h', 'Three fair dice are rolled and added. What is the variance of the total? Give 2 decimal places.', '8.75', 'Variances of independent variables add.', [
    'One die: <span class="eq">Var = 35/12 ≈ 2.9167</span>',
    'Three independent dice: <span class="eq">3 × 35/12 = 105/12</span>',
    '<span class="eq">105 ÷ 12 = 8.75</span>. The mean total is <span class="eq">3 × 3.5 = 10.5</span>.',
], check=8.75)
K.calc('x', 'A population has SD 10. What is the SD of the average of 25 independent samples?', '2', 'Standard error = σ ÷ √n.', [
    '<span class="eq">√25 = 5</span>',
    '<span class="eq">SE = 10 ÷ 5 = 2</span>',
    'The average is 5 times less spread out than a single value',
], check=2)
K.calc('x', 'Cov(X, Y) = 6, the SD of X is 2 and the SD of Y is 4. What is the correlation r?', '0.75', 'r = Cov ÷ (sx × sy).', [
    'Multiply the SDs: <span class="eq">2 × 4 = 8</span>',
    'Divide: <span class="eq">r = 6 ÷ 8 = 0.75</span>',
    'A fairly strong positive straight line relationship',
], check=0.75)
K.calc('x', 'Exam scores are normal with mean 70 and SD 10. What percentage score above 90? Give 2 decimal places.', '2.28', 'z = 2. 95.45% lie within 2 SD.', [
    'z-score: <span class="eq">(90 − 70) ÷ 10 = 2</span>',
    'Outside ±2σ: <span class="eq">100% − 95.45% = 4.55%</span>',
    'Only the upper half counts: <span class="eq">4.55% ÷ 2 ≈ 2.28%</span>',
], check=2.275, tol=0.01, unit='%')

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;
  let seed = 4242;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  const erf = x => {
    const s = x >= 0 ? 1 : -1; x = Math.abs(x);
    const t = 1 / (1 + 0.3275911 * x);
    return s * (1 - t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429)))) * Math.exp(-x * x));
  };
  const Phi = z => 0.5 * (1 + erf(z / Math.SQRT2));
  const npdf = (x, m, s) => Math.exp(-((x - m) ** 2) / (2 * s * s)) / (s * Math.sqrt(2 * Math.PI));
  const setSl = (b, k, v) => { $(`[data-sl="${k}"]`, b).value = v; $(`[data-slv="${k}"]`, b).textContent = v; };

  /* ----- binomial bars, one k at a time ----- */
  W.binom = el => {
    const b = shell(el, 'Build a binomial distribution', 'Set the number of tries n and the chance of success p. Press Play to work out P(X = k) one bar at a time, while the running total builds the CDF.');
    b.innerHTML = `<div class="vz-row">${slider('n', 'tries n', 1, 30, 10, 1)}${slider('p', 'success chance p', 0.05, 0.95, 0.5, 0.05)}</div>
      <div class="mv-wrap"><div class="bn-plot"></div><div class="mv-side"><div class="mv-legend"><span><i></i>P(X = k)</span><span><i class="o"></i>the bar being worked out</span></div><div class="mv-read bn-out" aria-live="polite"></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let n = 10, p = 0.5;
    const C = (n, k) => { let r = 1; for (let i = 1; i <= k; i++) r = r * (n - k + i) / i; return Math.round(r); };
    const pmf = k => C(n, k) * Math.pow(p, k) * Math.pow(1 - p, n - k);
    function show(t) {
      const P = Array.from({ length: n + 1 }, (_, i) => pmf(i)), k = t - 1;
      const ymax = Math.min(1.05, Math.max(...P) * 1.2);
      const G = MV.frame(460, 290, [-0.8, n + 0.8], [0, ymax], 42);
      let s = MV.axes(G, { xstep: n > 20 ? 5 : n > 10 ? 2 : 1 });
      for (let i = 0; i < t && i <= n; i++) {
        const w = 0.38;
        s += `<rect class="mv-bar ${i === k ? 'o' : ''}" x="${G.sx(i - w).toFixed(1)}" y="${G.sy(P[i]).toFixed(1)}" width="${(G.sx(i + w) - G.sx(i - w)).toFixed(1)}" height="${(G.sy(0) - G.sy(P[i])).toFixed(1)}"/>`;
      }
      s += MV.line(G, n * p, 0, n * p, ymax * 0.93, 'mv-v k dash') + MV.text(G, n * p, ymax * 0.93, 'mean n p', { dy: -6, anchor: 'middle', cls: 'mv-lab sm' });
      $('.bn-plot', b).innerHTML = MV.svg(G, s, 'Binomial bar chart');
      const q = MV.num(1 - p, 2), cum = P.slice(0, Math.max(0, k + 1)).reduce((a, v) => a + v, 0);
      $('.vz-msg', b).innerHTML = t === 0 ? `Press Play to work out the bars from k = 0 up to k = ${n}.` :
        `k = ${k}: P(X = ${k}) = C(${n}, ${k}) × ${MV.num(p, 2)}<sup>${k}</sup> × ${q}<sup>${n - k}</sup> = ${C(n, k)} × ${MV.num(Math.pow(p, k) * Math.pow(1 - p, n - k), 6)} = <b>${MV.num(P[k], 4)}</b>`;
      $('.bn-out', b).innerHTML = `mean n p = ${MV.num(n * p, 2)}<br>SD √(n p (1 − p)) = ${MV.num(Math.sqrt(n * p * (1 - p)), 3)}` +
        (t > 0 ? `<br>running total P(X ≤ ${k}) = <b>${MV.num(cum, 4)}</b>` : '') + (t === n + 1 ? '<br>All bars together add up to 1.' : '');
    }
    const P = Player($('.vz-p', b), show, 700);
    wireSlider(b, 'n', v => { n = v; P.load(n + 2, Math.min(P.i, n + 1)); });
    wireSlider(b, 'p', v => { p = v; show(P.i); });
    P.load(n + 2, 0);
  };

  /* ----- the bell curve with shaded areas ----- */
  W.normal = el => {
    const b = shell(el, 'Areas under the bell curve', 'Move the mean μ and the spread σ. Press Play to shade 1, 2 and 3 standard deviations around the mean, and finally the area to the left of x, which is P(X ≤ x).');
    b.innerHTML = `<div class="vz-row">${slider('mu', 'mean μ', -3, 3, 0, 0.5)}${slider('sg', 'SD σ', 0.5, 3, 1, 0.1)}${slider('x', 'x', -8, 8, 1, 0.5)}</div>
      <div class="mv-wrap"><div class="nm-plot"></div><div class="mv-side"><div class="mv-read nm-out" aria-live="polite"></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let mu = 0, sg = 1, X = 1;
    function show(t) {
      const f = x => npdf(x, mu, sg);
      const G = MV.frame(460, 280, [-8, 8], [0, 0.85], 34);
      let s = MV.axes(G, { xstep: 2, ystep: 0.2, labels: false });
      for (let x = -8; x <= 8; x += 2) s += `<text class="mv-tick" x="${G.sx(x).toFixed(1)}" y="${(G.sy(0) + 16).toFixed(1)}" text-anchor="middle">${x}</text>`;
      const clip = v => Math.max(-8, Math.min(8, v));
      if (t >= 1 && t <= 3) s += MV.area(G, f, clip(mu - t * sg), clip(mu + t * sg), ['', 'c3', 'c4'][t - 1]);
      if (t === 4) s += MV.area(G, f, -8, clip(X), 'c2');
      s += MV.curve(G, f, '', { n: 400 });
      s += MV.line(G, mu, 0, mu, Math.min(0.8, f(mu)), 'mv-v k dash');
      if (t >= 1 && t <= 3) for (const sd of [-t, t]) { const x = mu + sd * sg; if (x > -8 && x < 8) s += MV.line(G, x, 0, x, f(x), 'mv-v g'); }
      if (t === 4) s += MV.dot(G, X, 0, 'o', 6);
      $('.nm-plot', b).innerHTML = MV.svg(G, s, 'Normal curve');
      const share = [0, Phi(1) - Phi(-1), Phi(2) - Phi(-2), Phi(3) - Phi(-3)];
      const z = (X - mu) / sg;
      $('.vz-msg', b).innerHTML = [`The bell curve N(${MV.num(mu, 1)}, ${MV.num(sg, 1)}²). Press Play to shade areas.`,
        `Between μ − σ = ${MV.num(mu - sg, 2)} and μ + σ = ${MV.num(mu + sg, 2)}: ${MV.num(100 * share[1], 2)}% of all values.`,
        `Between μ − 2σ and μ + 2σ: ${MV.num(100 * share[2], 2)}%.`,
        `Between μ − 3σ and μ + 3σ: ${MV.num(100 * share[3], 2)}%. Almost everything.`,
        `Left of x = ${MV.num(X, 1)}: z = (${MV.num(X, 1)} − ${MV.num(mu, 1)}) ÷ ${MV.num(sg, 1)} = ${MV.num(z, 2)}, so P(X ≤ x) = ${MV.num(Phi(z), 4)}.`][t];
      $('.nm-out', b).innerHTML = `peak height 1 ÷ (σ√(2π)) = ${MV.num(1 / (sg * Math.sqrt(2 * Math.PI)), 3)}<br>z-score of x: ${MV.num(z, 2)}<br>P(X ≤ x) = ${MV.num(Phi(z), 4)}<br>The total area is always 1, so a narrow curve must be tall.`;
    }
    const P = Player($('.vz-p', b), show, 1600);
    wireSlider(b, 'mu', v => { mu = v; show(P.i); });
    wireSlider(b, 'sg', v => { sg = v; show(P.i); });
    wireSlider(b, 'x', v => { X = v; show(P.i); });
    P.load(5, 0);
  };

  /* ----- central limit theorem: averages become bell shaped ----- */
  W.clt = el => {
    const b = shell(el, 'Averages become bell shaped', 'Pick a starting shape and a sample size n. Each sample is the average of n random draws. Press Play to collect more and more sample averages and watch their histogram take the shape of the orange bell curve. Set n = 1 to see the starting shape itself.');
    b.innerHTML = `<div class="vz-row">${seg('src', [['die', 'Fair die'], ['skew', 'Skewed'], ['coin', 'Coin (0 or 1)']], 'skew')}</div>
      <div class="vz-row">${slider('n', 'values per average n', 1, 30, 1, 1)}</div>
      <div class="mv-wrap"><div class="cl-plot"></div><div class="mv-side"><div class="mv-legend"><span><i></i>sample averages</span><span><i class="o"></i>normal curve N(μ, σ² ÷ n)</span></div><div class="mv-read cl-out" aria-live="polite"></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const SRC = {
      die: { v: [1, 2, 3, 4, 5, 6], p: [1, 1, 1, 1, 1, 1].map(x => x / 6), name: 'a fair die (flat)' },
      skew: { v: [1, 2, 3, 4, 5, 6], p: [0.4, 0.25, 0.15, 0.1, 0.06, 0.04], name: 'a skewed die (mostly small numbers)' },
      coin: { v: [0, 1], p: [0.5, 0.5], name: 'a coin (only 0 or 1)' },
    };
    const M = 2000, STEPS = 10;
    let src = 'skew', n = 1, means = [];
    const S = () => SRC[src];
    const mu = () => S().v.reduce((a, v, i) => a + v * S().p[i], 0);
    const sd = () => Math.sqrt(S().v.reduce((a, v, i) => a + (v - mu()) ** 2 * S().p[i], 0));
    function draw() { let u = rnd(), i = 0; const s = S(); while (i < s.p.length - 1 && u > s.p[i]) { u -= s.p[i]; i++; } return s.v[i]; }
    function make() { means = Array.from({ length: M }, () => { let t = 0; for (let j = 0; j < n; j++) t += draw(); return t / n; }); P.load(STEPS + 1, 0); }
    function show(t) {
      const k = t === 0 ? 0 : Math.round(M * (t / STEPS) ** 2), used = means.slice(0, k);
      const s0 = S(), lo = s0.v[0], hi = s0.v[s0.v.length - 1], w = 1 / n;
      const cnt = new Map();
      used.forEach(m => { const key = Math.round(m * n); cnt.set(key, (cnt.get(key) || 0) + 1); });
      const m0 = mu(), se = sd() / Math.sqrt(n), peak = npdf(m0, m0, se);
      let hmax = 0; cnt.forEach(c => { hmax = Math.max(hmax, c / (k * w)); });
      const ymax = Math.max(peak, hmax) * 1.12;
      const G = MV.frame(460, 280, [lo - 0.5, hi + 0.5], [0, ymax], 42);
      let s = MV.axes(G, { xstep: src === 'coin' ? 0.25 : 1 });
      cnt.forEach((c, key) => {
        const x = key / n, h = c / (k * w), half = w * 0.45;
        s += `<rect class="mv-bar" x="${G.sx(x - half).toFixed(1)}" y="${G.sy(h).toFixed(1)}" width="${Math.max(1, G.sx(x + half) - G.sx(x - half)).toFixed(1)}" height="${(G.sy(0) - G.sy(h)).toFixed(1)}"/>`;
      });
      s += MV.curve(G, x => npdf(x, m0, se), 'c2', { n: 300 });
      $('.cl-plot', b).innerHTML = MV.svg(G, s, 'Histogram of sample averages');
      const avg = k ? used.reduce((a, v) => a + v, 0) / k : 0;
      const spread = k > 1 ? Math.sqrt(used.reduce((a, v) => a + (v - avg) ** 2, 0) / (k - 1)) : 0;
      $('.vz-msg', b).innerHTML = t === 0 ? `Starting shape: ${s0.name}. Each sample averages ${n} draw${n > 1 ? 's' : ''}. Press Play.` :
        `${k} sample averages so far. ${n === 1 ? 'With n = 1 the bars just copy the starting shape.' : n < 5 ? 'Small n: the shape is already smoothing out.' : 'Larger n: the bars hug the bell curve even though the start was not bell shaped.'}`;
      $('.cl-out', b).innerHTML = `μ = ${MV.num(m0, 3)}, σ = ${MV.num(sd(), 3)}<br>theory: SD of averages σ ÷ √n = ${MV.num(se, 3)}` +
        (k > 1 ? `<br>measured: mean ${MV.num(avg, 3)}, SD ${MV.num(spread, 3)}` : '');
    }
    const P = Player($('.vz-p', b), show, 700);
    wireSeg(b, 'src', v => { src = v; make(); });
    wireSlider(b, 'n', v => { n = v; make(); });
    make();
  };
})();
'''

CSS = r'''
.cl-plot .mv-bar{stroke-width:.5}
'''

T = K.topic(
    slug='distributions', topic='distributions', prefix='mm10', short='Distributions', emoji='🔔',
    title='Random Variables and Distributions',
    module=('🎲', 'Probability and statistics', 'probability', 'Chance, distributions and statistics: the maths that lets a model handle uncertainty and judge its own results.'),
    minutes=60,
    lead='A distribution says which values a random quantity is likely to take. Build binomial bars one at a time, shade areas under the bell curve, watch lopsided data turn bell shaped through the central limit theorem, and measure how two variables move together.',
    desc='Probability distributions for machine learning: random variables, PMF, PDF and CDF, expected value and variance, Bernoulli, binomial, Poisson, uniform, exponential and normal distributions, z-scores, the central limit theorem, covariance and correlation.',
    summary='Discrete and continuous random variables, PMF, PDF and CDF, expected value, variance and standard deviation, the Bernoulli, binomial and Poisson distributions, the normal curve and the 68, 95, 99.7 rule, z-scores, the central limit theorem and standard error, covariance and correlation.',
    keywords=['random variable', 'probability distribution', 'pmf', 'pdf', 'cdf', 'expected value', 'variance', 'standard deviation', 'bernoulli', 'binomial', 'poisson', 'normal distribution', 'gaussian', 'z-score', 'central limit theorem', 'standard error', 'covariance', 'correlation'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
