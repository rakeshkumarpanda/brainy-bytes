# Chapter 12: information and entropy, cross entropy and KL divergence, softmax and log-sum-exp, regression
# losses, log loss, L1 and L2 regularisation, and classification metrics up to ROC and AUC.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz, deep

K = Kit()

# ---------------------------------------------------------------- programs
K.code('entropy_kl', py=r'''
from math import log2

p = [0.5, 0.25, 0.25]                     # the real weather: sunny, cloudy, rainy
q = [0.7, 0.2, 0.1]                       # what a forecasting model believes
u = [1 / 3, 1 / 3, 1 / 3]                 # a model that knows nothing


def entropy(a):                           # average surprise, in bits
    return -sum(x * log2(x) for x in a if x > 0)


def cross_entropy(a, b):                  # average surprise when reality is a but you expected b
    return -sum(x * log2(y) for x, y in zip(a, b) if x > 0)


print(f"H(p)          = {entropy(p):.4f} bits")
print(f"H(p, q)       = {cross_entropy(p, q):.4f} bits")
print(f"KL(p || q)    = {cross_entropy(p, q) - entropy(p):.4f} bits")
print(f"KL(p || u)    = {cross_entropy(p, u) - entropy(p):.4f} bits")
print(f"KL(q || p)    = {cross_entropy(q, p) - entropy(q):.4f} bits (not the same: KL is not symmetric)")
''', js=r'''
const p = [0.5, 0.25, 0.25];              // the real weather: sunny, cloudy, rainy
const q = [0.7, 0.2, 0.1];                // what a forecasting model believes
const u = [1 / 3, 1 / 3, 1 / 3];          // a model that knows nothing

function entropy(a) {                     // average surprise, in bits
  return -a.reduce((s, x) => s + (x > 0 ? x * Math.log2(x) : 0), 0);
}

function crossEntropy(a, b) {             // average surprise when reality is a but you expected b
  return -a.reduce((s, x, i) => s + (x > 0 ? x * Math.log2(b[i]) : 0), 0);
}

console.log(`H(p)          = ${entropy(p).toFixed(4)} bits`);
console.log(`H(p, q)       = ${crossEntropy(p, q).toFixed(4)} bits`);
console.log(`KL(p || q)    = ${(crossEntropy(p, q) - entropy(p)).toFixed(4)} bits`);
console.log(`KL(p || u)    = ${(crossEntropy(p, u) - entropy(p)).toFixed(4)} bits`);
console.log(`KL(q || p)    = ${(crossEntropy(q, p) - entropy(q)).toFixed(4)} bits (not the same: KL is not symmetric)`);
''', ts=r'''
const p: number[] = [0.5, 0.25, 0.25];    // the real weather: sunny, cloudy, rainy
const q: number[] = [0.7, 0.2, 0.1];      // what a forecasting model believes
const u: number[] = [1 / 3, 1 / 3, 1 / 3];   // a model that knows nothing

function entropy(a: number[]): number {   // average surprise, in bits
  return -a.reduce((s, x) => s + (x > 0 ? x * Math.log2(x) : 0), 0);
}

function crossEntropy(a: number[], b: number[]): number {   // average surprise when reality is a but you expected b
  return -a.reduce((s, x, i) => s + (x > 0 ? x * Math.log2(b[i]) : 0), 0);
}

console.log(`H(p)          = ${entropy(p).toFixed(4)} bits`);
console.log(`H(p, q)       = ${crossEntropy(p, q).toFixed(4)} bits`);
console.log(`KL(p || q)    = ${(crossEntropy(p, q) - entropy(p)).toFixed(4)} bits`);
console.log(`KL(p || u)    = ${(crossEntropy(p, u) - entropy(p)).toFixed(4)} bits`);
console.log(`KL(q || p)    = ${(crossEntropy(q, p) - entropy(q)).toFixed(4)} bits (not the same: KL is not symmetric)`);
''', java=r'''
public class EntropyKL {
    static double log2(double x) {
        return Math.log(x) / Math.log(2);
    }

    static double entropy(double[] a) {       // average surprise, in bits
        double s = 0;
        for (double x : a) if (x > 0) s -= x * log2(x);
        return s;
    }

    static double crossEntropy(double[] a, double[] b) {   // average surprise when reality is a but you expected b
        double s = 0;
        for (int i = 0; i < a.length; i++) if (a[i] > 0) s -= a[i] * log2(b[i]);
        return s;
    }

    public static void main(String[] args) {
        double[] p = {0.5, 0.25, 0.25};           // the real weather: sunny, cloudy, rainy
        double[] q = {0.7, 0.2, 0.1};             // what a forecasting model believes
        double[] u = {1.0 / 3, 1.0 / 3, 1.0 / 3}; // a model that knows nothing
        System.out.println(String.format("H(p)          = %.4f bits", entropy(p)));
        System.out.println(String.format("H(p, q)       = %.4f bits", crossEntropy(p, q)));
        System.out.println(String.format("KL(p || q)    = %.4f bits", crossEntropy(p, q) - entropy(p)));
        System.out.println(String.format("KL(p || u)    = %.4f bits", crossEntropy(p, u) - entropy(p)));
        System.out.println(String.format("KL(q || p)    = %.4f bits (not the same: KL is not symmetric)", crossEntropy(q, p) - entropy(q)));
    }
}
''')

K.code('softmax', py=r'''
from math import exp, log


def softmax(z, t=1.0):                    # t is the temperature
    m = max(z)                            # subtract the biggest logit so exp never overflows
    e = [exp((v - m) / t) for v in z]
    s = sum(e)
    return [x / s for x in e]


logits = [2.0, 1.0, 0.1]                  # raw scores for cat, dog, bird
for t in (1.0, 0.5, 2.0):
    probs = softmax(logits, t)
    print(f"T = {t}: " + ", ".join(f"{x:.4f}" for x in probs))
probs = softmax(logits)
print(f"loss if the answer is cat:  {-log(probs[0]):.4f}")
print(f"loss if the answer is bird: {-log(probs[2]):.4f}")
''', js=r'''
function softmax(z, t = 1.0) {            // t is the temperature
  const m = Math.max(...z);               // subtract the biggest logit so exp never overflows
  const e = z.map(v => Math.exp((v - m) / t));
  const s = e.reduce((a, x) => a + x, 0);
  return e.map(x => x / s);
}

const logits = [2.0, 1.0, 0.1];           // raw scores for cat, dog, bird
for (const t of [1.0, 0.5, 2.0]) {
  const probs = softmax(logits, t);
  console.log(`T = ${t.toFixed(1)}: ` + probs.map(x => x.toFixed(4)).join(", "));
}
const probs = softmax(logits);
console.log(`loss if the answer is cat:  ${(-Math.log(probs[0])).toFixed(4)}`);
console.log(`loss if the answer is bird: ${(-Math.log(probs[2])).toFixed(4)}`);
''', ts=r'''
function softmax(z: number[], t: number = 1.0): number[] {   // t is the temperature
  const m: number = Math.max(...z);       // subtract the biggest logit so exp never overflows
  const e: number[] = z.map(v => Math.exp((v - m) / t));
  const s: number = e.reduce((a, x) => a + x, 0);
  return e.map(x => x / s);
}

const logits: number[] = [2.0, 1.0, 0.1]; // raw scores for cat, dog, bird
for (const t of [1.0, 0.5, 2.0]) {
  const probs: number[] = softmax(logits, t);
  console.log(`T = ${t.toFixed(1)}: ` + probs.map(x => x.toFixed(4)).join(", "));
}
const probs: number[] = softmax(logits);
console.log(`loss if the answer is cat:  ${(-Math.log(probs[0])).toFixed(4)}`);
console.log(`loss if the answer is bird: ${(-Math.log(probs[2])).toFixed(4)}`);
''', java=r'''
public class Softmax {
    static double[] softmax(double[] z, double t) {   // t is the temperature
        double m = Double.NEGATIVE_INFINITY;
        for (double v : z) m = Math.max(m, v);    // subtract the biggest logit so exp never overflows
        double[] e = new double[z.length];
        double s = 0;
        for (int i = 0; i < z.length; i++) { e[i] = Math.exp((z[i] - m) / t); s += e[i]; }
        for (int i = 0; i < z.length; i++) e[i] /= s;
        return e;
    }

    public static void main(String[] args) {
        double[] logits = {2.0, 1.0, 0.1};        // raw scores for cat, dog, bird
        for (double t : new double[]{1.0, 0.5, 2.0}) {
            double[] probs = softmax(logits, t);
            System.out.println(String.format("T = %.1f: %.4f, %.4f, %.4f", t, probs[0], probs[1], probs[2]));
        }
        double[] probs = softmax(logits, 1.0);
        System.out.println(String.format("loss if the answer is cat:  %.4f", -Math.log(probs[0])));
        System.out.println(String.format("loss if the answer is bird: %.4f", -Math.log(probs[2])));
    }
}
''')

K.code('losses', py=r'''
def losses(y, pred, delta=1.0):
    errs = [a - b for a, b in zip(y, pred)]
    n = len(errs)
    mse = sum(e * e for e in errs) / n    # squares: big misses count a lot
    mae = sum(abs(e) for e in errs) / n   # absolute values: every unit of miss counts the same
    huber = sum(0.5 * e * e if abs(e) <= delta else delta * (abs(e) - 0.5 * delta) for e in errs) / n
    return mse, mae, huber


pred = [2.5, 5, 3, 6, 4.5]
for name, y in (("clean data", [3, 5, 2, 7, 4]), ("one outlier", [3, 5, 2, 27, 4])):
    mse, mae, huber = losses(y, pred)
    print(f"{name}: MSE {mse:.2f}, MAE {mae:.2f}, Huber {huber:.2f}")
''', js=r'''
function losses(y, pred, delta = 1.0) {
  const errs = y.map((a, i) => a - pred[i]);
  const n = errs.length;
  const mse = errs.reduce((s, e) => s + e * e, 0) / n;      // squares: big misses count a lot
  const mae = errs.reduce((s, e) => s + Math.abs(e), 0) / n;   // absolute values: every unit of miss counts the same
  const huber = errs.reduce((s, e) => s + (Math.abs(e) <= delta ? 0.5 * e * e : delta * (Math.abs(e) - 0.5 * delta)), 0) / n;
  return [mse, mae, huber];
}

const pred = [2.5, 5, 3, 6, 4.5];
for (const [name, y] of [["clean data", [3, 5, 2, 7, 4]], ["one outlier", [3, 5, 2, 27, 4]]]) {
  const [mse, mae, huber] = losses(y, pred);
  console.log(`${name}: MSE ${mse.toFixed(2)}, MAE ${mae.toFixed(2)}, Huber ${huber.toFixed(2)}`);
}
''', ts=r'''
function losses(y: number[], pred: number[], delta: number = 1.0): [number, number, number] {
  const errs: number[] = y.map((a, i) => a - pred[i]);
  const n: number = errs.length;
  const mse: number = errs.reduce((s, e) => s + e * e, 0) / n;      // squares: big misses count a lot
  const mae: number = errs.reduce((s, e) => s + Math.abs(e), 0) / n;   // absolute values: every unit of miss counts the same
  const huber: number = errs.reduce((s, e) => s + (Math.abs(e) <= delta ? 0.5 * e * e : delta * (Math.abs(e) - 0.5 * delta)), 0) / n;
  return [mse, mae, huber];
}

const pred: number[] = [2.5, 5, 3, 6, 4.5];
const sets: [string, number[]][] = [["clean data", [3, 5, 2, 7, 4]], ["one outlier", [3, 5, 2, 27, 4]]];
for (const [name, y] of sets) {
  const [mse, mae, huber] = losses(y, pred);
  console.log(`${name}: MSE ${mse.toFixed(2)}, MAE ${mae.toFixed(2)}, Huber ${huber.toFixed(2)}`);
}
''', java=r'''
public class Losses {
    static double[] losses(double[] y, double[] pred, double delta) {
        int n = y.length;
        double mse = 0, mae = 0, huber = 0;
        for (int i = 0; i < n; i++) {
            double e = y[i] - pred[i];
            mse += e * e / n;                     // squares: big misses count a lot
            mae += Math.abs(e) / n;               // absolute values: every unit of miss counts the same
            huber += (Math.abs(e) <= delta ? 0.5 * e * e : delta * (Math.abs(e) - 0.5 * delta)) / n;
        }
        return new double[]{mse, mae, huber};
    }

    public static void main(String[] args) {
        double[] pred = {2.5, 5, 3, 6, 4.5};
        String[] names = {"clean data", "one outlier"};
        double[][] ys = {{3, 5, 2, 7, 4}, {3, 5, 2, 27, 4}};
        for (int k = 0; k < 2; k++) {
            double[] r = losses(ys[k], pred, 1.0);
            System.out.println(String.format("%s: MSE %.2f, MAE %.2f, Huber %.2f", names[k], r[0], r[1], r[2]));
        }
    }
}
''')

K.code('logloss', py=r'''
from math import log

labels = [1, 0, 1, 1, 0]                  # is it spam?
probs = [0.9, 0.2, 0.6, 0.95, 0.4]        # the model's P(spam)
total = 0
for y, p in zip(labels, probs):
    loss = -(y * log(p) + (1 - y) * log(1 - p))   # only one of the two terms is ever switched on
    total += loss
    print(f"y = {y}, p = {p:.2f}: loss {loss:.4f}, gradient p - y = {p - y:+.2f}")
print(f"mean log loss = {total / len(labels):.4f}")
print(f"confidently wrong (y = 1, p = 0.01): loss {-log(0.01):.4f}")
''', js=r'''
const labels = [1, 0, 1, 1, 0];           // is it spam?
const probs = [0.9, 0.2, 0.6, 0.95, 0.4]; // the model's P(spam)
let total = 0;
const signed = v => (v >= 0 ? "+" : "") + v.toFixed(2);
labels.forEach((y, i) => {
  const p = probs[i];
  const loss = -(y * Math.log(p) + (1 - y) * Math.log(1 - p));   // only one of the two terms is ever switched on
  total += loss;
  console.log(`y = ${y}, p = ${p.toFixed(2)}: loss ${loss.toFixed(4)}, gradient p - y = ${signed(p - y)}`);
});
console.log(`mean log loss = ${(total / labels.length).toFixed(4)}`);
console.log(`confidently wrong (y = 1, p = 0.01): loss ${(-Math.log(0.01)).toFixed(4)}`);
''', ts=r'''
const labels: number[] = [1, 0, 1, 1, 0];          // is it spam?
const probs: number[] = [0.9, 0.2, 0.6, 0.95, 0.4];   // the model's P(spam)
let total: number = 0;
const signed = (v: number): string => (v >= 0 ? "+" : "") + v.toFixed(2);
labels.forEach((y, i) => {
  const p: number = probs[i];
  const loss: number = -(y * Math.log(p) + (1 - y) * Math.log(1 - p));   // only one of the two terms is ever switched on
  total += loss;
  console.log(`y = ${y}, p = ${p.toFixed(2)}: loss ${loss.toFixed(4)}, gradient p - y = ${signed(p - y)}`);
});
console.log(`mean log loss = ${(total / labels.length).toFixed(4)}`);
console.log(`confidently wrong (y = 1, p = 0.01): loss ${(-Math.log(0.01)).toFixed(4)}`);
''', java=r'''
public class LogLoss {
    public static void main(String[] args) {
        int[] labels = {1, 0, 1, 1, 0};           // is it spam?
        double[] probs = {0.9, 0.2, 0.6, 0.95, 0.4};   // the model's P(spam)
        double total = 0;
        for (int i = 0; i < labels.length; i++) {
            int y = labels[i];
            double p = probs[i];
            double loss = -(y * Math.log(p) + (1 - y) * Math.log(1 - p));   // only one of the two terms is ever switched on
            total += loss;
            System.out.println(String.format("y = %d, p = %.2f: loss %.4f, gradient p - y = %+.2f", y, p, loss, p - y));
        }
        System.out.println(String.format("mean log loss = %.4f", total / labels.length));
        System.out.println(String.format("confidently wrong (y = 1, p = 0.01): loss %.4f", -Math.log(0.01)));
    }
}
''')

K.code('metrics', py=r'''
labels = [1, 1, 1, 1, 0, 1, 0, 0, 0, 0]   # 1 = really fraud
scores = [0.95, 0.85, 0.7, 0.6, 0.55, 0.45, 0.4, 0.3, 0.2, 0.1]   # the model's fraud score

for threshold in (0.5, 0.3):
    tp = fp = fn = tn = 0
    for y, s in zip(labels, scores):
        flag = s >= threshold             # flag as fraud?
        if flag and y == 1:
            tp += 1
        elif flag:
            fp += 1
        elif y == 1:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp)            # of the flagged, how many were fraud?
    recall = tp / (tp + fn)               # of the fraud, how many did we flag?
    f1 = 2 * precision * recall / (precision + recall)
    print(f"threshold {threshold}: TP {tp}, FP {fp}, FN {fn}, TN {tn}")
    print(f"  accuracy {(tp + tn) / len(labels):.2f}, precision {precision:.4f}, recall {recall:.2f}, F1 {f1:.4f}")
''', js=r'''
const labels = [1, 1, 1, 1, 0, 1, 0, 0, 0, 0];   // 1 = really fraud
const scores = [0.95, 0.85, 0.7, 0.6, 0.55, 0.45, 0.4, 0.3, 0.2, 0.1];   // the model's fraud score

for (const threshold of [0.5, 0.3]) {
  let tp = 0, fp = 0, fn = 0, tn = 0;
  labels.forEach((y, i) => {
    const flag = scores[i] >= threshold;  // flag as fraud?
    if (flag && y === 1) tp += 1;
    else if (flag) fp += 1;
    else if (y === 1) fn += 1;
    else tn += 1;
  });
  const precision = tp / (tp + fp);       // of the flagged, how many were fraud?
  const recall = tp / (tp + fn);          // of the fraud, how many did we flag?
  const f1 = 2 * precision * recall / (precision + recall);
  console.log(`threshold ${threshold}: TP ${tp}, FP ${fp}, FN ${fn}, TN ${tn}`);
  console.log(`  accuracy ${((tp + tn) / labels.length).toFixed(2)}, precision ${precision.toFixed(4)}, recall ${recall.toFixed(2)}, F1 ${f1.toFixed(4)}`);
}
''', ts=r'''
const labels: number[] = [1, 1, 1, 1, 0, 1, 0, 0, 0, 0];   // 1 = really fraud
const scores: number[] = [0.95, 0.85, 0.7, 0.6, 0.55, 0.45, 0.4, 0.3, 0.2, 0.1];   // the model's fraud score

for (const threshold of [0.5, 0.3]) {
  let tp: number = 0, fp: number = 0, fn: number = 0, tn: number = 0;
  labels.forEach((y, i) => {
    const flag: boolean = scores[i] >= threshold;   // flag as fraud?
    if (flag && y === 1) tp += 1;
    else if (flag) fp += 1;
    else if (y === 1) fn += 1;
    else tn += 1;
  });
  const precision: number = tp / (tp + fp);   // of the flagged, how many were fraud?
  const recall: number = tp / (tp + fn);      // of the fraud, how many did we flag?
  const f1: number = 2 * precision * recall / (precision + recall);
  console.log(`threshold ${threshold}: TP ${tp}, FP ${fp}, FN ${fn}, TN ${tn}`);
  console.log(`  accuracy ${((tp + tn) / labels.length).toFixed(2)}, precision ${precision.toFixed(4)}, recall ${recall.toFixed(2)}, F1 ${f1.toFixed(4)}`);
}
''', java=r'''
public class Metrics {
    public static void main(String[] args) {
        int[] labels = {1, 1, 1, 1, 0, 1, 0, 0, 0, 0};   // 1 = really fraud
        double[] scores = {0.95, 0.85, 0.7, 0.6, 0.55, 0.45, 0.4, 0.3, 0.2, 0.1};   // the model's fraud score
        for (double threshold : new double[]{0.5, 0.3}) {
            int tp = 0, fp = 0, fn = 0, tn = 0;
            for (int i = 0; i < labels.length; i++) {
                boolean flag = scores[i] >= threshold;    // flag as fraud?
                if (flag && labels[i] == 1) tp++;
                else if (flag) fp++;
                else if (labels[i] == 1) fn++;
                else tn++;
            }
            double precision = (double) tp / (tp + fp);   // of the flagged, how many were fraud?
            double recall = (double) tp / (tp + fn);      // of the fraud, how many did we flag?
            double f1 = 2 * precision * recall / (precision + recall);
            System.out.println("threshold " + threshold + ": TP " + tp + ", FP " + fp + ", FN " + fn + ", TN " + tn);
            System.out.println(String.format("  accuracy %.2f, precision %.4f, recall %.2f, F1 %.4f", (double) (tp + tn) / labels.length, precision, recall, f1));
        }
    }
}
''')

K.code('p_bits', py=r'''
from math import log2


def entropy(p):
    return -sum(x * log2(x) for x in p if x > 0)


print(f"fair coin:   {entropy([0.5, 0.5]):.4f} bits")
print(f"90/10 coin:  {entropy([0.9, 0.1]):.4f} bits")
print(f"fair die:    {entropy([1 / 6] * 6):.4f} bits")
print(f"loaded die:  {entropy([0.5, 0.1, 0.1, 0.1, 0.1, 0.1]):.4f} bits")
print(f"yes or no questions to find 1 person in a million: {log2(1000000):.2f}")
''', js=r'''
const entropy = p => -p.reduce((s, x) => s + (x > 0 ? x * Math.log2(x) : 0), 0);

console.log(`fair coin:   ${entropy([0.5, 0.5]).toFixed(4)} bits`);
console.log(`90/10 coin:  ${entropy([0.9, 0.1]).toFixed(4)} bits`);
console.log(`fair die:    ${entropy(new Array(6).fill(1 / 6)).toFixed(4)} bits`);
console.log(`loaded die:  ${entropy([0.5, 0.1, 0.1, 0.1, 0.1, 0.1]).toFixed(4)} bits`);
console.log(`yes or no questions to find 1 person in a million: ${Math.log2(1000000).toFixed(2)}`);
''', ts=r'''
const entropy = (p: number[]): number => -p.reduce((s, x) => s + (x > 0 ? x * Math.log2(x) : 0), 0);

console.log(`fair coin:   ${entropy([0.5, 0.5]).toFixed(4)} bits`);
console.log(`90/10 coin:  ${entropy([0.9, 0.1]).toFixed(4)} bits`);
console.log(`fair die:    ${entropy(new Array(6).fill(1 / 6)).toFixed(4)} bits`);
console.log(`loaded die:  ${entropy([0.5, 0.1, 0.1, 0.1, 0.1, 0.1]).toFixed(4)} bits`);
console.log(`yes or no questions to find 1 person in a million: ${Math.log2(1000000).toFixed(2)}`);
''', java=r'''
public class PracticeBits {
    static double entropy(double[] p) {
        double s = 0;
        for (double x : p) if (x > 0) s -= x * Math.log(x) / Math.log(2);
        return s;
    }

    public static void main(String[] args) {
        double d = 1.0 / 6;
        System.out.println(String.format("fair coin:   %.4f bits", entropy(new double[]{0.5, 0.5})));
        System.out.println(String.format("90/10 coin:  %.4f bits", entropy(new double[]{0.9, 0.1})));
        System.out.println(String.format("fair die:    %.4f bits", entropy(new double[]{d, d, d, d, d, d})));
        System.out.println(String.format("loaded die:  %.4f bits", entropy(new double[]{0.5, 0.1, 0.1, 0.1, 0.1, 0.1})));
        System.out.println(String.format("yes or no questions to find 1 person in a million: %.2f", Math.log(1000000) / Math.log(2)));
    }
}
''')

K.code('p_stable', py=r'''
from math import exp, log

z = [1000.0, 1001.0, 1002.0]              # huge logits: exp(1000) is far beyond the largest float
print("largest float is about 1.8e308, exp(1000) would be about 1.97e434, so the naive way fails")
m = max(z)
shifted = [v - m for v in z]              # [-2, -1, 0]: safe to exponentiate
e = [exp(v) for v in shifted]
s = sum(e)
print("softmax:", ", ".join(f"{x / s:.4f}" for x in e))
lse = m + log(s)                          # log-sum-exp computed safely
print(f"log-sum-exp = {lse:.4f}")
print(f"cross entropy if the true class is the first one = {lse - z[0]:.4f}")
''', js=r'''
const z = [1000.0, 1001.0, 1002.0];       // huge logits: exp(1000) is far beyond the largest float
console.log("largest float is about 1.8e308, exp(1000) would be about 1.97e434, so the naive way fails");
const m = Math.max(...z);
const shifted = z.map(v => v - m);        // [-2, -1, 0]: safe to exponentiate
const e = shifted.map(v => Math.exp(v));
const s = e.reduce((a, x) => a + x, 0);
console.log("softmax:", e.map(x => (x / s).toFixed(4)).join(", "));
const lse = m + Math.log(s);              // log-sum-exp computed safely
console.log(`log-sum-exp = ${lse.toFixed(4)}`);
console.log(`cross entropy if the true class is the first one = ${(lse - z[0]).toFixed(4)}`);
''', ts=r'''
const z: number[] = [1000.0, 1001.0, 1002.0];   // huge logits: exp(1000) is far beyond the largest float
console.log("largest float is about 1.8e308, exp(1000) would be about 1.97e434, so the naive way fails");
const m: number = Math.max(...z);
const shifted: number[] = z.map(v => v - m);   // [-2, -1, 0]: safe to exponentiate
const e: number[] = shifted.map(v => Math.exp(v));
const s: number = e.reduce((a, x) => a + x, 0);
console.log("softmax:", e.map(x => (x / s).toFixed(4)).join(", "));
const lse: number = m + Math.log(s);      // log-sum-exp computed safely
console.log(`log-sum-exp = ${lse.toFixed(4)}`);
console.log(`cross entropy if the true class is the first one = ${(lse - z[0]).toFixed(4)}`);
''', java=r'''
public class PracticeStable {
    public static void main(String[] args) {
        double[] z = {1000.0, 1001.0, 1002.0};   // huge logits: exp(1000) is far beyond the largest double
        System.out.println("largest float is about 1.8e308, exp(1000) would be about 1.97e434, so the naive way fails");
        double m = Math.max(z[0], Math.max(z[1], z[2]));
        double[] e = new double[3];
        double s = 0;
        for (int i = 0; i < 3; i++) { e[i] = Math.exp(z[i] - m); s += e[i]; }   // shifted values are safe
        System.out.println(String.format("softmax: %.4f, %.4f, %.4f", e[0] / s, e[1] / s, e[2] / s));
        double lse = m + Math.log(s);             // log-sum-exp computed safely
        System.out.println(String.format("log-sum-exp = %.4f", lse));
        System.out.println(String.format("cross entropy if the true class is the first one = %.4f", lse - z[0]));
    }
}
''')

K.code('p_ridge', py=r'''
x = [1, 2, 3, 4]
y = [2.1, 3.9, 6.2, 7.8]                  # roughly y = 2x
sxy = sum(a * b for a, b in zip(x, y))
sxx = sum(a * a for a in x)
for lam in (0, 1, 10, 100):
    w = sxy / (sxx + lam)                 # ridge: minimise sum of squared errors + lam * w^2
    mse = sum((b - w * a) ** 2 for a, b in zip(x, y)) / len(x)
    print(f"lambda {lam:3}: w = {w:.4f}, training MSE = {mse:.4f}")
''', js=r'''
const x = [1, 2, 3, 4];
const y = [2.1, 3.9, 6.2, 7.8];           // roughly y = 2x
const sxy = x.reduce((s, a, i) => s + a * y[i], 0);
const sxx = x.reduce((s, a) => s + a * a, 0);
for (const lam of [0, 1, 10, 100]) {
  const w = sxy / (sxx + lam);            // ridge: minimise sum of squared errors + lam * w^2
  const mse = x.reduce((s, a, i) => s + (y[i] - w * a) ** 2, 0) / x.length;
  console.log(`lambda ${String(lam).padStart(3)}: w = ${w.toFixed(4)}, training MSE = ${mse.toFixed(4)}`);
}
''', ts=r'''
const x: number[] = [1, 2, 3, 4];
const y: number[] = [2.1, 3.9, 6.2, 7.8]; // roughly y = 2x
const sxy: number = x.reduce((s, a, i) => s + a * y[i], 0);
const sxx: number = x.reduce((s, a) => s + a * a, 0);
for (const lam of [0, 1, 10, 100]) {
  const w: number = sxy / (sxx + lam);    // ridge: minimise sum of squared errors + lam * w^2
  const mse: number = x.reduce((s, a, i) => s + (y[i] - w * a) ** 2, 0) / x.length;
  console.log(`lambda ${String(lam).padStart(3)}: w = ${w.toFixed(4)}, training MSE = ${mse.toFixed(4)}`);
}
''', java=r'''
public class PracticeRidge {
    public static void main(String[] args) {
        double[] x = {1, 2, 3, 4};
        double[] y = {2.1, 3.9, 6.2, 7.8};        // roughly y = 2x
        double sxy = 0, sxx = 0;
        for (int i = 0; i < x.length; i++) { sxy += x[i] * y[i]; sxx += x[i] * x[i]; }
        for (int lam : new int[]{0, 1, 10, 100}) {
            double w = sxy / (sxx + lam);         // ridge: minimise sum of squared errors + lam * w^2
            double mse = 0;
            for (int i = 0; i < x.length; i++) mse += Math.pow(y[i] - w * x[i], 2) / x.length;
            System.out.println(String.format("lambda %3d: w = %.4f, training MSE = %.4f", lam, w, mse));
        }
    }
}
''')

K.code('p_auc', py=r'''
pos = [0.9, 0.8, 0.7, 0.55, 0.4]          # scores of the 5 real positives
neg = [0.6, 0.5, 0.35, 0.3, 0.1]          # scores of the 5 real negatives
wins = 0
for a in pos:                             # AUC = chance a random positive outscores a random negative
    for b in neg:
        wins += 1 if a > b else 0.5 if a == b else 0
print(f"AUC = {wins:g} / {len(pos) * len(neg)} = {wins / (len(pos) * len(neg)):.2f}")
for t in (0.35, 0.5, 0.7):
    tp = sum(1 for s in pos if s >= t)
    fp = sum(1 for s in neg if s >= t)
    precision, recall = tp / (tp + fp), tp / len(pos)
    print(f"threshold {t:.2f}: precision {precision:.3f}, recall {recall:.1f}, F1 {2 * precision * recall / (precision + recall):.3f}")
''', js=r'''
const pos = [0.9, 0.8, 0.7, 0.55, 0.4];   // scores of the 5 real positives
const neg = [0.6, 0.5, 0.35, 0.3, 0.1];   // scores of the 5 real negatives
let wins = 0;
for (const a of pos) {                    // AUC = chance a random positive outscores a random negative
  for (const b of neg) {
    wins += a > b ? 1 : a === b ? 0.5 : 0;
  }
}
console.log(`AUC = ${wins} / ${pos.length * neg.length} = ${(wins / (pos.length * neg.length)).toFixed(2)}`);
for (const t of [0.35, 0.5, 0.7]) {
  const tp = pos.filter(s => s >= t).length;
  const fp = neg.filter(s => s >= t).length;
  const precision = tp / (tp + fp), recall = tp / pos.length;
  console.log(`threshold ${t.toFixed(2)}: precision ${precision.toFixed(3)}, recall ${recall.toFixed(1)}, F1 ${(2 * precision * recall / (precision + recall)).toFixed(3)}`);
}
''', ts=r'''
const pos: number[] = [0.9, 0.8, 0.7, 0.55, 0.4];   // scores of the 5 real positives
const neg: number[] = [0.6, 0.5, 0.35, 0.3, 0.1];   // scores of the 5 real negatives
let wins: number = 0;
for (const a of pos) {                    // AUC = chance a random positive outscores a random negative
  for (const b of neg) {
    wins += a > b ? 1 : a === b ? 0.5 : 0;
  }
}
console.log(`AUC = ${wins} / ${pos.length * neg.length} = ${(wins / (pos.length * neg.length)).toFixed(2)}`);
for (const t of [0.35, 0.5, 0.7]) {
  const tp: number = pos.filter(s => s >= t).length;
  const fp: number = neg.filter(s => s >= t).length;
  const precision: number = tp / (tp + fp), recall: number = tp / pos.length;
  console.log(`threshold ${t.toFixed(2)}: precision ${precision.toFixed(3)}, recall ${recall.toFixed(1)}, F1 ${(2 * precision * recall / (precision + recall)).toFixed(3)}`);
}
''', java=r'''
public class PracticeAuc {
    public static void main(String[] args) {
        double[] pos = {0.9, 0.8, 0.7, 0.55, 0.4};   // scores of the 5 real positives
        double[] neg = {0.6, 0.5, 0.35, 0.3, 0.1};   // scores of the 5 real negatives
        double wins = 0;
        for (double a : pos) {                    // AUC = chance a random positive outscores a random negative
            for (double b : neg) {
                wins += a > b ? 1 : a == b ? 0.5 : 0;
            }
        }
        String w = wins == Math.floor(wins) ? String.valueOf((long) wins) : String.valueOf(wins);
        System.out.println(String.format("AUC = %s / %d = %.2f", w, pos.length * neg.length, wins / (pos.length * neg.length)));
        for (double t : new double[]{0.35, 0.5, 0.7}) {
            int tp = 0, fp = 0;
            for (double s : pos) if (s >= t) tp++;
            for (double s : neg) if (s >= t) fp++;
            double precision = (double) tp / (tp + fp), recall = (double) tp / pos.length;
            System.out.println(String.format("threshold %.2f: precision %.3f, recall %.1f, F1 %.3f", t, precision, recall, 2 * precision * recall / (precision + recall)));
        }
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('entropy', '🔥', 'Information and entropy', f'''
<p>Some news tells you a lot, some tells you almost nothing. "The sun rose today" is no surprise. "It snowed in the Sahara" is a big surprise. <b>Information theory</b> measures surprise with a number, and <b>entropy</b> is the average surprise of a random event.</p>
{fxs(fx('Surprise (information) of an outcome', f'I(x) = log₂ {frac("1", "p(x)")} = −log₂ p(x)', 'Measured in bits. A fair coin flip carries 1 bit. A 1 in 8 event carries 3 bits.'),
         fx('Entropy', 'H(p) = −Σ p(x) log₂ p(x)', 'The average surprise. It is 0 when one outcome is certain and largest when every outcome is equally likely.'))}
{viz('entropy')}
{worked('What is the entropy of a coin that lands heads 90% of the time?', [
        'Surprise of heads: <span class="eq">log₂(1 ÷ 0.9) ≈ 0.152</span> bits. Surprise of tails: <span class="eq">log₂(1 ÷ 0.1) ≈ 3.322</span> bits',
        'Weight each by its chance: <span class="eq">0.9 × 0.152 + 0.1 × 3.322</span>',
        '<span class="eq">= 0.137 + 0.332 ≈ 0.469</span> bits',
        'Less than the fair coin (1 bit), because this coin is usually predictable.'])}
{trick('Entropy counts the yes or no questions you need on average. A fair die needs log₂ 6 ≈ 2.585. Finding one person among a million needs about 20.')}
{ml('Decision trees choose each split to reduce entropy as much as possible. That drop is called information gain.')}
''', kw=['information theory', 'entropy', 'bits', 'surprise', 'self information', 'information gain', 'shannon']),

    part('xent', '🎯', 'Cross entropy and KL divergence', f'''
<p>Suppose reality follows p, but your model believes q. You will be surprised more often than necessary. <b>Cross entropy</b> measures your average surprise, and the extra over the unavoidable entropy is the <b>KL divergence</b>.</p>
{fxs(fx('Cross entropy', 'H(p, q) = −Σ p(x) log q(x)', 'Reality p, belief q. It is smallest when q = p.'),
         fx('KL divergence', f'KL(p ‖ q) = Σ p(x) log {frac("p(x)", "q(x)")} = H(p, q) − H(p)', 'Always ≥ 0, and 0 only when q = p. Not symmetric: KL(p ‖ q) ≠ KL(q ‖ p).'))}
{worked('Real weather: sunny 0.5, cloudy 0.25, rainy 0.25. A model says 0.7, 0.2, 0.1. Measure the mismatch in bits.', [
        'Entropy of reality: <span class="eq">H(p) = 0.5 × 1 + 0.25 × 2 + 0.25 × 2 = 1.5</span> bits',
        'Cross entropy: <span class="eq">−(0.5 log₂ 0.7 + 0.25 log₂ 0.2 + 0.25 log₂ 0.1) ≈ 0.257 + 0.580 + 0.830 = 1.668</span> bits',
        'KL divergence: <span class="eq">1.668 − 1.5 ≈ 0.168</span> bits of wasted surprise per day',
        'A know-nothing model (1/3 each) wastes only <span class="eq">log₂ 3 − 1.5 ≈ 0.085</span> bits. Being confidently wrong about rain costs more.'])}
{code('entropy_kl', 'Entropy, cross entropy and KL divergence')}
{ml('In classification the true label is one-hot (p = 1 for the right class, 0 for the rest), so H(p) = 0 and cross entropy becomes just −log q(right class). Minimising cross entropy and minimising KL divergence are then the same thing. KL also appears in variational autoencoders and in keeping a fine-tuned language model close to its original version.')}
''', kw=['cross entropy', 'kl divergence', 'kullback leibler', 'relative entropy', 'one hot', 'information loss']),

    part('softmax', '🌡️', 'Softmax, temperature and log-sum-exp', f'''
<p>A classifier first produces raw scores called <b>logits</b>, which can be any real numbers. <b>Softmax</b> turns them into probabilities: all positive and adding to 1, with the biggest logit getting the biggest share.</p>
{fxs(fx('Softmax', f'softmax(z)ᵢ = {frac("e<sup>zᵢ ÷ T</sup>", "Σⱼ e<sup>zⱼ ÷ T</sup>")}', 'T is the temperature. T = 1 is normal, small T sharpens the choice, large T flattens it.'),
         fx('Stable computation', 'softmax(z) = softmax(z − max z)', 'Subtracting the same number from every logit changes nothing, but keeps e<sup>z</sup> from overflowing.'),
         fx('Log-sum-exp', 'log Σ e<sup>zⱼ</sup> = m + log Σ e<sup>zⱼ − m</sup>, &nbsp; m = max z', 'Cross entropy loss = log-sum-exp(z) − z<sub>correct</sub>.'))}
{viz('softmax')}
{worked('Logits 2.0, 1.0 and 0.1 for cat, dog and bird. Find the probabilities and the loss if the answer is cat.', [
        'Exponentiate: <span class="eq">e² ≈ 7.389</span>, <span class="eq">e¹ ≈ 2.718</span>, <span class="eq">e⁰·¹ ≈ 1.105</span>',
        'Sum: <span class="eq">7.389 + 2.718 + 1.105 = 11.212</span>',
        'Divide: <span class="eq">0.659, 0.242, 0.099</span>. They add to 1.',
        'Loss for cat: <span class="eq">−ln 0.659 ≈ 0.417</span>. If the answer were bird: <span class="eq">−ln 0.099 ≈ 2.317</span>'])}
{code('softmax', 'Softmax at three temperatures')}
{ml('Language models pick the next word by sampling from a softmax. The "temperature" setting in chatbots is exactly the T in this formula: low T gives safe, repeatable text, high T gives more varied text.')}
''', kw=['softmax', 'logits', 'temperature', 'log sum exp', 'numerical stability', 'overflow', 'multiclass classification']),

    part('losses', '📉', 'Loss functions for regression', f'''
<p>A <b>loss function</b> turns "how wrong was the model?" into one number that training then makes smaller. The choice of loss decides what kind of mistakes the model cares most about.</p>
{fxs(fx('Mean squared error', f'MSE = {frac("1", "n")} Σ (yᵢ − ŷᵢ)²', 'Squares make big misses count a lot. Smooth and easy to differentiate. The best constant prediction is the mean.'),
         fx('Mean absolute error', f'MAE = {frac("1", "n")} Σ |yᵢ − ŷᵢ|', 'Every unit of error counts the same, so outliers matter less. The best constant prediction is the median.'),
         fx('Huber loss', '½ e² when |e| ≤ δ, &nbsp; δ(|e| − ½δ) otherwise', 'Squared for small errors, straight line for big ones: the best of both.'))}
{worked('Predictions 2.5, 5, 3, 6, 4.5 for true values 3, 5, 2, 7, 4. Then one true value becomes 27.', [
        'Errors: <span class="eq">0.5, 0, −1, 1, −0.5</span>. Squares: <span class="eq">0.25, 0, 1, 1, 0.25</span>, so <span class="eq">MSE = 2.5 ÷ 5 = 0.5</span>',
        'Absolute errors add to <span class="eq">3</span>, so <span class="eq">MAE = 0.6</span>',
        'Change 7 to 27: that error becomes <span class="eq">21</span> and its square <span class="eq">441</span>, so <span class="eq">MSE = 88.5</span>',
        'MAE only rises to <span class="eq">4.6</span>. MSE is far more sensitive to the outlier.'])}
{code('losses', 'MSE, MAE and Huber with and without an outlier')}
{table(['Loss', 'Outliers', 'Gradient', 'Typical use'], [
        ['MSE', 'very sensitive', 'smooth, shrinks near 0', 'default for regression'],
        ['MAE', 'robust', 'constant size, kink at 0', 'when outliers are common'],
        ['Huber', 'robust', 'smooth', 'a safe middle ground'],
    ])}
{trick('MSE chases the mean, MAE chases the median. Pick the loss whose "best answer" matches what you want to predict.')}
''', kw=['loss function', 'mean squared error', 'MSE', 'mean absolute error', 'MAE', 'huber loss', 'outliers', 'regression loss']),

    part('logloss', '🪵', 'Log loss for classification', f'''
<p>For a yes or no classifier that outputs a probability p, the standard loss is <b>log loss</b>, also called binary cross entropy. It is the cross entropy from earlier with only two classes.</p>
{fx('Binary cross entropy', 'L = −[ y log p + (1 − y) log(1 − p) ]', 'If y = 1 only −log p counts. If y = 0 only −log(1 − p) counts.')}
{table(['True label y', 'Predicted p', 'Loss'], [
        ['1', '0.9 (confident and right)', '0.105'],
        ['1', '0.6 (unsure but right)', '0.511'],
        ['1', '0.1 (confident and wrong)', '2.303'],
        ['1', '0.01 (very confident and wrong)', '4.605'],
    ])}
{worked('Why does training with log loss feel so simple? Find the gradient for logistic regression, where p = σ(z).', [
        'From Chapter 6: <span class="eq">σ′(z) = p(1 − p)</span>',
        'For y = 1: <span class="eq">dL/dp = −1/p</span>, so <span class="eq">dL/dz = −1/p × p(1 − p) = p − 1</span>',
        'For y = 0: <span class="eq">dL/dp = 1/(1 − p)</span>, so <span class="eq">dL/dz = p</span>',
        'Both cases together: <span class="eq">dL/dz = p − y</span>. The update is simply "prediction minus truth".'])}
{code('logloss', 'Log loss and its gradient')}
<div class="warn">Why not use MSE for classification? With a sigmoid output, MSE gives tiny gradients exactly when the model is confidently wrong, so learning stalls. Log loss punishes confident mistakes hard and keeps the gradient p − y large.</div>
{ml('Minimising log loss is maximum likelihood for a Bernoulli model (Chapter 11). Clipping p to a range such as [10⁻⁷, 1 − 10⁻⁷] stops log 0 from turning into infinity.')}
''', kw=['log loss', 'binary cross entropy', 'logistic regression', 'sigmoid', 'gradient p minus y', 'classification loss']),

    part('reg', '🧲', 'Regularisation: L2 and L1', f'''
<p>A flexible model can fit noise (overfitting, Chapter 11). <b>Regularisation</b> adds a penalty for large weights to the loss, so the model only uses big weights when the data really demands them.</p>
{fxs(fx('L2 (ridge, weight decay)', 'loss + λ Σ wⱼ²', 'Shrinks all weights smoothly toward 0. Rarely makes any weight exactly 0.'),
         fx('L1 (lasso)', 'loss + λ Σ |wⱼ|', 'Pushes some weights to exactly 0, so it also selects features.'),
         fx('One weight ridge solution', f'w = {frac("Σ xᵢ yᵢ", "Σ xᵢ² + λ")}', 'For y ≈ w x with no intercept. Bigger λ makes w smaller.'))}
{worked('x = 1, 2, 3, 4 and y = 2.1, 3.9, 6.2, 7.8. Fit y ≈ w x with λ = 0 and λ = 10.', [
        '<span class="eq">Σxy = 2.1 + 7.8 + 18.6 + 31.2 = 59.7</span> and <span class="eq">Σx² = 1 + 4 + 9 + 16 = 30</span>',
        'No penalty: <span class="eq">w = 59.7 ÷ 30 = 1.99</span>',
        'With λ = 10: <span class="eq">w = 59.7 ÷ 40 ≈ 1.49</span>. The weight shrank.',
        'The training error goes up, but on new noisy data a slightly shrunk model often does better.'])}
{trick('λ is a dial between "trust the data" (λ = 0) and "keep it simple" (large λ). Pick it with a validation set, never with the test set.')}
{ml('Weight decay in neural network optimisers such as AdamW is L2 regularisation. Dropout and early stopping are other ways to regularise.')}
''', kw=['regularisation', 'L2', 'ridge', 'weight decay', 'L1', 'lasso', 'lambda', 'sparsity', 'overfitting']),

    part('metrics', '📊', 'Classification metrics, ROC and AUC', f'''
<p>Accuracy alone can fool you. If 99% of card payments are honest, a model that never flags fraud is 99% accurate and completely useless. The <b>confusion matrix</b> shows what really happened.</p>
{table(['', 'Really positive', 'Really negative'], [
        ['<b>Predicted positive</b>', 'TP (true positive)', 'FP (false positive)'],
        ['<b>Predicted negative</b>', 'FN (false negative)', 'TN (true negative)'],
    ])}
{fxs(fx('Precision', f'{frac("TP", "TP + FP")}', 'Of everything flagged, how much was right? Important when false alarms are costly.'),
         fx('Recall (sensitivity, TPR)', f'{frac("TP", "TP + FN")}', 'Of all real positives, how many did we catch? Important when misses are costly.'),
         fx('F1 score', f'F1 = {frac("2 × precision × recall", "precision + recall")}', 'The harmonic mean, high only when both are high.'))}
{viz('roc')}
{worked('10 payments, threshold 0.5: TP 4, FP 1, FN 1, TN 4. Then lower the threshold to 0.3: TP 5, FP 3, FN 0, TN 2.', [
        'At 0.5: <span class="eq">precision = 4 ÷ 5 = 0.8</span>, <span class="eq">recall = 4 ÷ 5 = 0.8</span>, <span class="eq">F1 = 0.8</span>',
        'At 0.3: <span class="eq">precision = 5 ÷ 8 = 0.625</span>, <span class="eq">recall = 5 ÷ 5 = 1</span>',
        '<span class="eq">F1 = 2 × 0.625 × 1 ÷ 1.625 ≈ 0.769</span>',
        'Lowering the threshold catches every fraud but raises more false alarms. That is the trade-off the ROC curve draws.'])}
{code('metrics', 'Confusion matrix, precision, recall and F1')}
{fx('ROC curve and AUC', 'TPR = TP ÷ (TP + FN) against FPR = FP ÷ (FP + TN) for every threshold', 'AUC is the area under that curve: the chance that a random positive gets a higher score than a random negative. 0.5 is guessing, 1 is perfect.')}
{trick('Precision asks "when I shout fraud, am I right?" Recall asks "did I catch all the fraud?" A doctor screening for cancer wants high recall. A spam filter that must not lose real email wants high precision.')}
''', kw=['confusion matrix', 'accuracy', 'precision', 'recall', 'F1 score', 'ROC curve', 'AUC', 'threshold', 'true positive rate', 'false positive rate', 'imbalanced data']),
]

INFO = {
    'title': 'Losses teach the model, metrics judge it',
    'panels': [
        {'s': [['e', '🔥'], ['t', 'H = −Σ p log p', {'b': 1}]], 'h': 'Entropy', 't': 'Average surprise.', 'more': 'Cross entropy adds the cost of a wrong belief.'},
        {'s': [['e', '🌡️'], ['t', 'eᶻ ÷ Σ eᶻ', {'b': 1}]], 'h': 'Softmax', 't': 'Scores to probabilities.', 'more': 'Subtract the max first.'},
        {'s': [['e', '📉'], ['t', 'MSE, MAE, log loss', {'b': 1}]], 'h': 'Loss', 't': 'What training minimises.', 'more': 'Log loss gradient is p − y.'},
        {'s': [['e', '📊'], ['t', 'precision, recall, AUC', {'b': 1}]], 'h': 'Metrics', 't': 'How good it really is.', 'more': 'Accuracy hides rare classes.'},
    ],
    'remember': 'Surprise is −log₂ p and entropy is the average surprise. Cross entropy H(p, q) = −Σ p log q, and KL = H(p, q) − H(p) ≥ 0. Softmax turns logits into probabilities, computed stably by subtracting the max. MSE punishes big errors, MAE is robust to outliers, log loss punishes confident mistakes and has gradient p − y. L2 shrinks weights, L1 zeros some out. Precision = TP ÷ (TP + FP), recall = TP ÷ (TP + FN), and AUC is the chance a positive outscores a negative.',
}

REAL = [
    ['💬', 'Chatbots', 'Language models are trained by minimising cross entropy on the next word, and their temperature setting is the T inside softmax.'],
    ['💳', 'Fraud detection', 'Banks tune the alert threshold on the precision and recall trade-off, because every false alarm annoys a customer and every miss costs money.'],
    ['🩺', 'Medical screening', 'Screening tests are judged by sensitivity (recall) and AUC, since missing a disease is far worse than an extra follow-up test.'],
]

K.say('top', 'Welcome',
      'This chapter is where the maths meets real models. You will measure surprise with entropy, see how cross entropy and softmax train classifiers, compare loss functions, add regularisation, and judge models with precision, recall and the ROC curve.',
      'इस अध्याय में गणित असली models से मिलता है। आप entropy से आश्चर्य मापेंगे, देखेंगे कि cross entropy और softmax classifiers को कैसे train करते हैं, loss functions की तुलना करेंगे, regularisation जोड़ेंगे, और precision, recall और ROC curve से models को परखेंगे।',
      'ಈ ಅಧ್ಯಾಯದಲ್ಲಿ ಗಣಿತ ನಿಜವಾದ models ಅನ್ನು ಸೇರುತ್ತದೆ. Entropy, cross entropy, softmax, losses, regularisation ಮತ್ತು metrics.',
      'ଏହି ଅଧ୍ୟାୟରେ ଗଣିତ ପ୍ରକୃତ models ସହ ମିଶେ। Entropy, cross entropy, softmax, losses, regularisation ଓ metrics।',
      'في هذا الفصل تلتقي الرياضيات بالنماذج الحقيقية. ستقيس المفاجأة بالإنتروبيا، وترى كيف تدرب الإنتروبيا المتقاطعة ودالة softmax المصنفات، وتقارن دوال الخسارة، وتضيف التنظيم، وتحكم على النماذج بالدقة والاستدعاء ومنحنى ROC.',
      'In diesem Kapitel trifft die Mathematik auf echte Modelle. Du misst Überraschung mit Entropie, siehst, wie Kreuzentropie und Softmax Klassifikatoren trainieren, vergleichst Verlustfunktionen, fügst Regularisierung hinzu und bewertest Modelle mit Präzision, Recall und der ROC Kurve.')
K.say('entropy', 'Entropy',
      'The surprise of an outcome is the log of one over its chance, measured in bits. Entropy is the average surprise. It is zero when the result is certain and largest when every outcome is equally likely. Move the sliders and watch each outcome add its share.',
      'किसी परिणाम का आश्चर्य उसकी संभावना के उल्टे का log है, bits में। Entropy औसत आश्चर्य है। परिणाम निश्चित हो तो यह शून्य है, और सभी परिणाम बराबर हों तो सबसे बड़ा। Sliders बदलें और हर परिणाम का हिस्सा देखें।',
      'ಆಶ್ಚರ್ಯ ಎಂದರೆ ಒಂದು ಭಾಗಿಸು ಸಾಧ್ಯತೆಯ log. Entropy ಸರಾಸರಿ ಆಶ್ಚರ್ಯ.',
      'ଆଶ୍ଚର୍ଯ୍ୟ ମାନେ ଏକ ଭାଗ ସମ୍ଭାବନାର log। Entropy ହାରାହାରି ଆଶ୍ଚର୍ଯ୍ୟ।',
      'مفاجأة نتيجة ما هي لوغاريتم مقلوب احتمالها، وتقاس بالبت. والإنتروبيا هي متوسط المفاجأة، وتساوي صفرًا حين تكون النتيجة مؤكدة، وأكبر ما تكون حين تتساوى كل النتائج. حرك المنزلقات وشاهد كل نتيجة تضيف حصتها.',
      'Die Überraschung eines Ergebnisses ist der Logarithmus von eins durch seine Chance, gemessen in Bit. Entropie ist die mittlere Überraschung. Sie ist null, wenn das Ergebnis sicher ist, und am größten, wenn alle gleich wahrscheinlich sind. Verschiebe die Regler und sieh jeden Anteil.')
K.say('xent', 'Cross entropy and KL',
      'Cross entropy is your average surprise when reality follows p but you believe q. The extra above the true entropy is the KL divergence, which is never negative and is zero only when your belief matches reality. With one hot labels, cross entropy is just minus the log of the probability given to the right answer.',
      'Cross entropy औसत आश्चर्य है जब असलियत p हो पर आप q मानें। सच्ची entropy से ऊपर का अतिरिक्त KL divergence है, जो कभी ऋणात्मक नहीं होता। One hot labels में cross entropy बस सही उत्तर की संभावना का माइनस log है।',
      'Cross entropy p ವಾಸ್ತವ, q ನಂಬಿಕೆ ಇದ್ದಾಗ ಸರಾಸರಿ ಆಶ್ಚರ್ಯ. ಹೆಚ್ಚುವರಿ KL divergence.',
      'Cross entropy p ବାସ୍ତବ, q ବିଶ୍ୱାସ ହେଲେ ହାରାହାରି ଆଶ୍ଚର୍ଯ୍ୟ। ଅତିରିକ୍ତ KL divergence।',
      'الإنتروبيا المتقاطعة هي متوسط مفاجأتك حين يتبع الواقع p وتعتقد أنت q. والزيادة فوق الإنتروبيا الحقيقية هي تباعد KL، ولا يكون سالبًا أبدًا ويساوي صفرًا فقط حين يطابق اعتقادك الواقع. ومع التسميات الأحادية تصبح الإنتروبيا المتقاطعة سالب لوغاريتم احتمال الجواب الصحيح.',
      'Kreuzentropie ist deine mittlere Überraschung, wenn die Wirklichkeit p folgt, du aber q glaubst. Der Überschuss über der wahren Entropie ist die KL Divergenz, nie negativ und nur null, wenn Glaube und Wirklichkeit übereinstimmen. Bei One Hot Labels ist Kreuzentropie einfach minus der Logarithmus der Wahrscheinlichkeit der richtigen Antwort.')
K.say('softmax', 'Softmax',
      'Softmax turns raw scores into probabilities. Exponentiate each score, add them up, and divide. Subtract the biggest score first so nothing overflows. The temperature divides every score: low temperature sharpens the choice, high temperature flattens it. Press play to follow each stage.',
      'Softmax raw scores को probabilities में बदलता है। हर score का exponent लें, जोड़ें, और भाग दें। पहले सबसे बड़ा score घटाएँ ताकि overflow न हो। Temperature हर score को भाग देता है: कम temperature चुनाव को तेज़, ज़्यादा उसे सपाट करता है।',
      'Softmax scores ಅನ್ನು probabilities ಮಾಡುತ್ತದೆ. ಮೊದಲು ದೊಡ್ಡ score ಕಳೆಯಿರಿ. Temperature ಆಯ್ಕೆಯನ್ನು ತೀಕ್ಷ್ಣ ಅಥವಾ ಸಮತಟ್ಟು ಮಾಡುತ್ತದೆ.',
      'Softmax scores କୁ probabilities କରେ। ପ୍ରଥମେ ବଡ଼ score ବିୟୋଗ କରନ୍ତୁ। Temperature ବାଛିବାକୁ ତୀକ୍ଷ୍ଣ କିମ୍ବା ସମତଳ କରେ।',
      'دالة softmax تحول الدرجات الخام إلى احتمالات: ارفع e لكل درجة واجمعها ثم اقسم. اطرح أكبر درجة أولًا حتى لا يحدث فيض. ودرجة الحرارة تقسم كل درجة، فالمنخفضة تحدد الاختيار والمرتفعة تسطحه. اضغط تشغيل لتتبع كل مرحلة.',
      'Softmax macht aus Rohwerten Wahrscheinlichkeiten. Nimm e hoch jeden Wert, addiere und teile. Ziehe zuerst den größten Wert ab, damit nichts überläuft. Die Temperatur teilt jeden Wert: niedrige Temperatur schärft die Wahl, hohe glättet sie. Drücke Play und folge jedem Schritt.')
K.say('losses', 'Regression losses',
      'Mean squared error squares every miss, so big misses dominate. Mean absolute error counts every unit the same, so it shrugs off outliers. Huber loss is squared for small errors and straight for big ones. One wild value can multiply the squared error many times over.',
      'Mean squared error हर गलती का वर्ग करता है, इसलिए बड़ी गलतियाँ हावी होती हैं। Mean absolute error हर इकाई को बराबर गिनता है, इसलिए outliers का असर कम होता है। Huber छोटी गलतियों पर वर्ग और बड़ी पर सीधी रेखा है।',
      'MSE ದೊಡ್ಡ ದೋಷಗಳಿಗೆ ಹೆಚ್ಚು ತೂಕ. MAE outliers ಗೆ ಸ್ಥಿರ. Huber ಎರಡರ ಮಧ್ಯೆ.',
      'MSE ବଡ଼ ତ୍ରୁଟିକୁ ଅଧିକ ଓଜନ ଦିଏ। MAE outliers ପ୍ରତି ସ୍ଥିର। Huber ଦୁଇଟିର ମଝିରେ।',
      'متوسط مربع الخطأ يربع كل خطأ فتطغى الأخطاء الكبيرة. ومتوسط الخطأ المطلق يعد كل وحدة بالتساوي فيتجاهل القيم الشاذة. وخسارة Huber تربيعية للأخطاء الصغيرة وخطية للكبيرة. قيمة شاذة واحدة قد تضاعف الخطأ التربيعي مرات كثيرة.',
      'Der mittlere quadratische Fehler quadriert jeden Fehler, große Fehler dominieren. Der mittlere absolute Fehler zählt jede Einheit gleich und lässt Ausreißer kalt. Der Huber Verlust ist für kleine Fehler quadratisch und für große linear. Ein einziger wilder Wert kann den quadratischen Fehler vervielfachen.')
K.say('logloss', 'Log loss',
      'Log loss is minus the log of the probability the model gave to the true answer. Confident and right costs almost nothing, confident and wrong costs a lot. Its gradient with respect to the score is simply prediction minus truth, which makes training clean and fast.',
      'Log loss सही उत्तर को दी गई संभावना का माइनस log है। आत्मविश्वासी और सही लगभग मुफ़्त, आत्मविश्वासी और गलत बहुत महँगा। Score के सापेक्ष इसका gradient बस prediction माइनस truth है।',
      'Log loss ಸರಿಯಾದ ಉತ್ತರದ ಸಾಧ್ಯತೆಯ ಮೈನಸ್ log. Gradient prediction ಮೈನಸ್ truth.',
      'Log loss ଠିକ୍ ଉତ୍ତରର ସମ୍ଭାବନାର ମାଇନସ୍ log। Gradient prediction ମାଇନସ୍ truth।',
      'خسارة اللوغاريتم هي سالب لوغاريتم الاحتمال الذي أعطاه النموذج للجواب الصحيح. الثقة مع الصواب لا تكلف شيئًا تقريبًا، والثقة مع الخطأ تكلف كثيرًا. وتدرجها بالنسبة للدرجة هو ببساطة التنبؤ ناقص الحقيقة.',
      'Log Loss ist minus der Logarithmus der Wahrscheinlichkeit, die das Modell der richtigen Antwort gab. Sicher und richtig kostet fast nichts, sicher und falsch kostet viel. Der Gradient bezüglich des Werts ist einfach Vorhersage minus Wahrheit.')
K.say('reg', 'Regularisation',
      'Regularisation adds a penalty for large weights. L2 shrinks every weight smoothly, L1 pushes some weights all the way to zero. The strength lambda is a dial between trusting the data and keeping the model simple, and it is chosen with a validation set.',
      'Regularisation बड़े weights पर penalty जोड़ता है। L2 हर weight को धीरे से छोटा करता है, L1 कुछ weights को शून्य तक धकेलता है। Lambda data पर भरोसे और सरल model के बीच का dial है, जिसे validation set से चुनते हैं।',
      'Regularisation ದೊಡ್ಡ weights ಗೆ ದಂಡ. L2 ಕುಗ್ಗಿಸುತ್ತದೆ, L1 ಕೆಲವನ್ನು ಸೊನ್ನೆ ಮಾಡುತ್ತದೆ.',
      'Regularisation ବଡ଼ weights ପାଇଁ ଦଣ୍ଡ। L2 ଛୋଟ କରେ, L1 କିଛିକୁ ଶୂନ କରେ।',
      'التنظيم يضيف عقوبة على الأوزان الكبيرة. L2 يقلص كل وزن بسلاسة، وL1 يدفع بعض الأوزان إلى الصفر تمامًا. وقوة لامدا مفتاح بين الثقة بالبيانات وإبقاء النموذج بسيطًا، وتُختار بمجموعة تحقق.',
      'Regularisierung bestraft große Gewichte. L2 schrumpft jedes Gewicht sanft, L1 drückt manche ganz auf null. Die Stärke Lambda ist ein Regler zwischen Vertrauen in die Daten und einem einfachen Modell und wird mit einem Validierungsdatensatz gewählt.')
K.say('metrics', 'Metrics',
      'Precision asks how many flagged cases were right. Recall asks how many real positives were caught. Moving the threshold trades one for the other, and the ROC curve draws that trade off for every threshold. The area under it is the chance that a random positive outscores a random negative.',
      'Precision पूछता है कि flag किए गए में कितने सही थे। Recall पूछता है कि असली positives में से कितने पकड़े गए। Threshold बदलने से एक के बदले दूसरा मिलता है, और ROC curve हर threshold के लिए यह दिखाता है। उसके नीचे का क्षेत्र AUC है।',
      'Precision flag ಮಾಡಿದವುಗಳಲ್ಲಿ ಸರಿ ಎಷ್ಟು. Recall ನಿಜ positives ನಲ್ಲಿ ಹಿಡಿದದ್ದು ಎಷ್ಟು. ROC curve ಮತ್ತು AUC.',
      'Precision flag କରିଥିବାରୁ କେତେ ଠିକ୍। Recall ପ୍ରକୃତ positives ରୁ କେତେ ଧରାଗଲା। ROC curve ଓ AUC।',
      'الدقة تسأل كم من الحالات المعلّمة كانت صحيحة، والاستدعاء يسأل كم من الإيجابيات الحقيقية التُقطت. تحريك العتبة يبادل أحدهما بالآخر، ومنحنى ROC يرسم هذه المبادلة لكل عتبة، والمساحة تحته هي فرصة أن يتفوق إيجابي عشوائي على سلبي عشوائي.',
      'Präzision fragt, wie viele markierte Fälle stimmten. Recall fragt, wie viele echte Positive gefunden wurden. Die Schwelle tauscht das eine gegen das andere, und die ROC Kurve zeigt diesen Tausch für jede Schwelle. Die Fläche darunter ist die Chance, dass ein zufälliges Positives ein zufälliges Negatives überbietet.')
K.say('practice', 'Practice',
      'Practice time. Count bits of entropy, compute a stable softmax with huge scores, watch ridge regression shrink a weight, and find the AUC by comparing pairs.',
      'अभ्यास का समय। Entropy के bits गिनें, बड़े scores के साथ stable softmax निकालें, ridge regression से weight छोटा होते देखें, और जोड़ियों की तुलना से AUC निकालें।',
      'ಅಭ್ಯಾಸದ ಸಮಯ. Entropy, stable softmax, ridge ಮತ್ತು AUC.',
      'ଅଭ୍ୟାସ ସମୟ। Entropy, stable softmax, ridge ଓ AUC।',
      'وقت التدريب. احسب بتات الإنتروبيا، وطبّق softmax مستقرة على درجات ضخمة، وشاهد انحدار ridge يقلص وزنًا، وجد AUC بمقارنة الأزواج.',
      'Zeit zum Üben. Zähle Entropie Bits, berechne eine stabile Softmax mit riesigen Werten, sieh Ridge Regression ein Gewicht schrumpfen und finde die AUC durch Paarvergleiche.')

# ---------------------------------------------------------------- practice
K.practice('bits', 'e', 'Counting bits', 'p_bits',
           '<p>Find the entropy in bits of a fair coin, a 90/10 coin, a fair die and a die that shows 1 half the time (the other faces 0.1 each). How many yes or no questions does it take to find one person among a million?</p>',
           'fair coin:   1.0000 bits\n90/10 coin:  0.4690 bits\nfair die:    2.5850 bits\nloaded die:  2.1610 bits\nyes or no questions to find 1 person in a million: 19.93',
           'H = −Σ p log₂ p. For n equally likely outcomes it is log₂ n.',
           '<p>A fair coin gives 1 bit. The 90/10 coin gives 0.9 × 0.152 + 0.1 × 3.322 ≈ 0.469 bits. A fair die gives log₂ 6 ≈ 2.585 bits. The loaded die: 0.5 × 1 + 5 × (0.1 × 3.322) = 0.5 + 1.661 = 2.161 bits, less than the fair die because it is more predictable. Finding one of a million equally likely people takes log₂ 1000000 ≈ 19.93, so 20 well chosen questions.</p>',
           'O(outcomes)', 'O(1)')
K.practice('stable', 'm', 'A softmax that does not overflow', 'p_stable',
           '<p>Compute the softmax and the log-sum-exp of the logits 1000, 1001 and 1002, and the cross entropy loss if the true class is the first one. A naive e<sup>1000</sup> overflows, so subtract the maximum first.</p>',
           'largest float is about 1.8e308, exp(1000) would be about 1.97e434, so the naive way fails\nsoftmax: 0.0900, 0.2447, 0.6652\nlog-sum-exp = 1002.4076\ncross entropy if the true class is the first one = 2.4076',
           'Subtracting the same number from every logit does not change the softmax.',
           '<p>Subtract m = 1002 to get −2, −1 and 0. Then e⁻² ≈ 0.1353, e⁻¹ ≈ 0.3679 and e⁰ = 1, which add to 1.5032. Dividing gives 0.0900, 0.2447 and 0.6652. Log-sum-exp = 1002 + ln 1.5032 ≈ 1002.4076. The loss for class 1 is log-sum-exp minus its logit: 1002.4076 − 1000 = 2.4076, which equals −ln 0.0900. Every deep learning library computes cross entropy this way, straight from the logits.</p>',
           'O(classes)', 'O(classes)')
K.practice('ridge', 'h', 'Ridge shrinks the weight', 'p_ridge',
           '<p>Fit y ≈ w x (no intercept) to x = 1, 2, 3, 4 and y = 2.1, 3.9, 6.2, 7.8 with ridge penalty λ = 0, 1, 10 and 100. Report w and the training MSE each time.</p>',
           'lambda   0: w = 1.9900, training MSE = 0.0243\nlambda   1: w = 1.9258, training MSE = 0.0552\nlambda  10: w = 1.4925, training MSE = 1.8805\nlambda 100: w = 0.4592, training MSE = 17.5987',
           'Minimise Σ(yᵢ − w xᵢ)² + λ w². Setting the derivative to 0 gives w = Σxy ÷ (Σx² + λ).',
           '<p>Derivative: −2Σxᵢ(yᵢ − w xᵢ) + 2λw = 0, so w(Σx² + λ) = Σxy and w = 59.7 ÷ (30 + λ). λ = 0 gives 1.99, λ = 1 gives 1.926, λ = 10 gives 1.493 and λ = 100 gives 0.459. The training error always rises as λ grows, because the penalty pulls w away from the best fit. The value of λ is a trade-off, so it is tuned on held out validation data.</p>',
           'O(n)', 'O(1)')
K.practice('auc', 'x', 'AUC by counting pairs', 'p_auc',
           '<p>Positives scored 0.9, 0.8, 0.7, 0.55, 0.4 and negatives scored 0.6, 0.5, 0.35, 0.3, 0.1. Compute the AUC by comparing every positive with every negative, then precision, recall and F1 at thresholds 0.35, 0.5 and 0.7.</p>',
           'AUC = 22 / 25 = 0.88\nthreshold 0.35: precision 0.625, recall 1.0, F1 0.769\nthreshold 0.50: precision 0.667, recall 0.8, F1 0.727\nthreshold 0.70: precision 1.000, recall 0.6, F1 0.750',
           'AUC = (pairs where the positive scores higher + half the ties) ÷ (number of pairs).',
           '<p>There are 5 × 5 = 25 pairs. 0.9, 0.8 and 0.7 beat all 5 negatives (15 wins), 0.55 beats 4 and 0.4 beats 3, giving 22 wins. AUC = 22 ÷ 25 = 0.88. At threshold 0.35 we flag all 5 positives and 3 negatives: precision 5/8, recall 1. At 0.5: 4 positives and 2 negatives, precision 4/6, recall 0.8. At 0.7: 3 positives and no negatives, precision 1, recall 0.6. The best F1 here comes from the lowest threshold, but the right choice depends on what a miss and a false alarm each cost.</p>',
           'O(P × N)', 'O(1)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'How many bits of information does one fair coin flip carry?', ['0', '1', '2', '0.5'], 1, 'log₂ 2.', 'Two equally likely outcomes: log₂ 2 = 1 bit.')
K.quiz('e', 'When is entropy zero?', ['when all outcomes are equally likely', 'when one outcome is certain', 'when there are two outcomes', 'never'], 1, 'No surprise at all.', 'If p = 1 for one outcome, −1 × log 1 = 0.')
K.quiz('e', 'Softmax outputs are…', ['any real numbers', 'positive numbers that add up to 1', 'only 0 or 1', 'negative'], 1, 'They are probabilities.', 'Exponentials are positive and dividing by their sum makes them add to 1.')
K.quiz('e', 'Which loss is most affected by one huge outlier?', ['MAE', 'MSE', 'Huber', 'all equally'], 1, 'Squaring.', 'An error of 20 adds 400 to the squared total but only 20 to the absolute total.')
K.quiz('m', 'Precision is…', ['TP ÷ (TP + FN)', 'TP ÷ (TP + FP)', '(TP + TN) ÷ total', 'FP ÷ (FP + TN)'], 1, 'Of everything flagged…', 'TP ÷ (TP + FN) is recall, and FP ÷ (FP + TN) is the false positive rate.')
K.quiz('m', 'A fraud model never flags anything, and 99% of payments are honest. Its accuracy is…', ['1%', '50%', '99%', '0%'], 2, 'It is right on every honest payment.', '99% accurate yet recall 0. Accuracy hides rare classes.')
K.quiz('m', 'What does raising the softmax temperature T do?', ['makes the largest probability bigger', 'flattens the probabilities toward equal', 'changes which class is largest', 'makes them add to more than 1'], 1, 'Dividing logits by a big T shrinks their differences.', 'Large T gives a flatter, more random distribution, and small T a sharper one.')
K.quiz('m', 'KL(p ‖ q) is zero exactly when…', ['p and q are both uniform', 'q = p', 'q is one-hot', 'p has entropy 1'], 1, 'No wasted surprise.', 'KL ≥ 0, with equality only when the two distributions are equal.')
K.quiz('m', 'The log loss for y = 1 and p = 0.5 is about…', ['0', '0.693', '1', '0.5'], 1, '−ln 0.5.', '−ln 0.5 = ln 2 ≈ 0.693.')
K.quiz('h', 'For logistic regression with log loss, the gradient with respect to the score z is…', ['y − p', 'p − y', 'p(1 − p)', '−log p'], 1, 'Chain rule through the sigmoid.', 'dL/dz = p − y. The sigmoid derivative cancels neatly.')
K.quiz('h', 'Why subtract max(z) before computing softmax?', ['to change the answer', 'to avoid overflow in e^z without changing the result', 'to make the outputs add to 2', 'to remove the largest class'], 1, 'e¹⁰⁰⁰ is too big for a float.', 'softmax(z − c) = softmax(z) for any constant c.')
K.quiz('h', 'Which regularisation tends to set some weights exactly to zero?', ['L2 (ridge)', 'L1 (lasso)', 'neither', 'both equally'], 1, 'The absolute value has a sharp corner at 0.', 'L1 performs feature selection, while L2 only shrinks.')
K.quiz('h', 'An AUC of 0.5 means the model…', ['is perfect', 'ranks positives above negatives no better than chance', 'is always wrong', 'has 50% accuracy at every threshold'], 1, 'Random guessing.', 'AUC = P(random positive scores above random negative). 0.5 is a coin toss.')
K.quiz('x', 'With one-hot labels, minimising cross entropy H(p, q) is the same as minimising…', ['the entropy of q', 'KL(p ‖ q)', 'the MSE', 'the accuracy'], 1, 'H(p, q) = H(p) + KL(p ‖ q).', 'H(p) is fixed (0 for one-hot), so only the KL part can change.')
K.quiz('x', 'Why is MSE a poor loss for a sigmoid classifier?', ['it cannot be computed', 'its gradient becomes tiny when the model is confidently wrong, so learning stalls', 'it is always negative', 'it ignores the labels'], 1, 'The sigmoid derivative p(1 − p) is near 0 at the extremes.', 'Log loss cancels that factor and keeps the gradient p − y large.')
K.quiz('x', 'A cancer screening test should be tuned mainly for…', ['high precision', 'high recall', 'high accuracy', 'a threshold of exactly 0.5'], 1, 'Which mistake is worse here?', 'Missing a cancer (false negative) is far worse than an extra check, so recall comes first.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many bits of surprise does a 1 in 8 event carry?', '3', 'I = log₂(1 ÷ p).', [
    '<span class="eq">1 ÷ p = 1 ÷ (1/8) = 8</span>',
    '<span class="eq">log₂ 8</span> asks "2 to which power is 8?"',
    '<span class="eq">2³ = 8</span>, so the answer is <span class="eq">3</span> bits',
], check=3)
K.calc('e', 'What is the entropy of a fair 4 sided die in bits?', '2', 'n equally likely outcomes give log₂ n.', [
    'Each face has <span class="eq">p = 1/4</span>, surprise <span class="eq">log₂ 4 = 2</span> bits',
    'Average of four equal surprises: <span class="eq">4 × (1/4 × 2)</span>',
    '<span class="eq">= 2</span> bits',
], check=2)
K.calc('e', 'Predictions miss by 1, −2 and 3. What is the MSE?', '4.667', 'Square, add, divide by 3. Give 3 decimal places.', [
    'Squares: <span class="eq">1, 4, 9</span>',
    'Sum: <span class="eq">14</span>',
    '<span class="eq">14 ÷ 3 ≈ 4.667</span>',
], check=14 / 3, tol=0.001)
K.calc('e', 'Predictions miss by 1, −2 and 3. What is the MAE?', '2', 'Absolute values, then average.', [
    'Absolute values: <span class="eq">1, 2, 3</span>',
    'Sum: <span class="eq">6</span>',
    '<span class="eq">6 ÷ 3 = 2</span>',
], check=2)
K.calc('m', 'TP = 40, FP = 10, FN = 20. What is the precision?', '0.8', 'TP ÷ (TP + FP).', [
    'Flagged: <span class="eq">TP + FP = 40 + 10 = 50</span>',
    'Correct among those: <span class="eq">40</span>',
    '<span class="eq">40 ÷ 50 = 0.8</span>',
], check=0.8)
K.calc('m', 'TP = 40, FP = 10, FN = 20. What is the recall? Give 3 decimal places.', '0.667', 'TP ÷ (TP + FN).', [
    'Real positives: <span class="eq">TP + FN = 40 + 20 = 60</span>',
    'Caught: <span class="eq">40</span>',
    '<span class="eq">40 ÷ 60 ≈ 0.667</span>',
], check=40 / 60, tol=0.001)
K.calc('m', 'Precision 0.8 and recall 0.667. What is F1? Give 3 decimal places.', '0.727', '2PR ÷ (P + R).', [
    'Top: <span class="eq">2 × 0.8 × 0.6667 ≈ 1.0667</span>',
    'Bottom: <span class="eq">0.8 + 0.6667 = 1.4667</span>',
    '<span class="eq">1.0667 ÷ 1.4667 ≈ 0.727</span>',
], check=2 * 0.8 * (2 / 3) / (0.8 + 2 / 3), tol=0.001)
K.calc('m', 'The true label is 1 and the model says p = 0.9. What is the log loss (natural log)? Give 3 decimal places.', '0.105', '−ln p.', [
    'Only the y = 1 term is switched on: <span class="eq">L = −ln 0.9</span>',
    '<span class="eq">ln 0.9 ≈ −0.1054</span>',
    '<span class="eq">L ≈ 0.105</span>',
], check=0.10536051565782628, tol=0.001)
K.calc('h', 'Logits 2, 1 and 0.1. What is the softmax probability of the first class? Give 3 decimal places.', '0.659', 'e² ÷ (e² + e¹ + e⁰·¹).', [
    '<span class="eq">e² ≈ 7.389</span>, <span class="eq">e¹ ≈ 2.718</span>, <span class="eq">e⁰·¹ ≈ 1.105</span>',
    'Sum: <span class="eq">11.212</span>',
    '<span class="eq">7.389 ÷ 11.212 ≈ 0.659</span>',
], check=0.6590011388859679, tol=0.001)
K.calc('h', 'Reality p = (0.5, 0.5). A model says q = (0.8, 0.2). What is the cross entropy H(p, q) in bits? Give 3 decimal places.', '1.322', '−Σ p log₂ q.', [
    '<span class="eq">log₂ 0.8 ≈ −0.3219</span> and <span class="eq">log₂ 0.2 ≈ −2.3219</span>',
    '<span class="eq">H = −(0.5 × −0.3219 + 0.5 × −2.3219)</span>',
    '<span class="eq">= 0.1610 + 1.1610 ≈ 1.322</span> bits, more than the 1 bit a perfect model would need',
], check=1.3219, tol=0.001)
K.calc('h', 'With the same p and q, what is KL(p ‖ q) in bits? Give 3 decimal places.', '0.322', 'KL = H(p, q) − H(p).', [
    'Cross entropy from before: <span class="eq">H(p, q) ≈ 1.3219</span>',
    'Entropy of a fair coin: <span class="eq">H(p) = 1</span>',
    '<span class="eq">KL = 1.3219 − 1 ≈ 0.322</span> bits',
], check=0.3219, tol=0.001)
K.calc('x', 'Ridge with one weight: Σxy = 59.7, Σx² = 30, λ = 10. What is w? Give 4 decimal places.', '1.4925', 'w = Σxy ÷ (Σx² + λ).', [
    'Bottom: <span class="eq">30 + 10 = 40</span>',
    '<span class="eq">w = 59.7 ÷ 40</span>',
    '<span class="eq">= 1.4925</span>, down from 1.99 with no penalty',
], check=59.7 / 40, tol=0.00005)
K.calc('x', '4 positives and 4 negatives. In 13 of the 16 positive and negative pairs the positive scores higher, with no ties. What is the AUC? Give 4 decimal places.', '0.8125', 'AUC = wins ÷ pairs.', [
    'Pairs: <span class="eq">4 × 4 = 16</span>',
    'Wins: <span class="eq">13</span>',
    '<span class="eq">13 ÷ 16 = 0.8125</span>',
], check=13 / 16)

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;
  const setSl = (b, k, v) => { $(`[data-sl="${k}"]`, b).value = v; $(`[data-slv="${k}"]`, b).textContent = v; };

  /* ----- entropy: add each outcome's share of surprise ----- */
  W.entropy = el => {
    const b = shell(el, 'Build the entropy', 'Set how likely each of four outcomes is (the weights are scaled to add up to 1) or pick a preset. Press Play to add each outcome\'s contribution p × log₂(1 ÷ p) to the total.');
    b.innerHTML = `<div class="vz-row">${seg('pre', [['fair', 'Fair'], ['skew', 'Skewed'], ['sure', 'Almost certain']], 'skew')}</div>
      <div class="vz-row">${slider('a', 'A', 0, 100, 70, 1)}${slider('b', 'B', 0, 100, 15, 1)}${slider('c', 'C', 0, 100, 10, 1)}${slider('d', 'D', 0, 100, 5, 1)}</div>
      <div class="mv-wrap"><div class="en-plot"></div><div class="mv-side"><div class="mv-legend"><span><i></i>probability</span><span><i class="o"></i>contribution added</span></div><div class="mv-read en-out" aria-live="polite"></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let w = [70, 15, 10, 5];
    const PRE = { fair: [25, 25, 25, 25], skew: [70, 15, 10, 5], sure: [97, 1, 1, 1] };
    const probs = () => { const s = w.reduce((a, v) => a + v, 0) || 1; return w.map(v => v / s); };
    const term = p => (p > 0 ? -p * Math.log2(p) : 0);
    function show(t) {
      const p = probs(), names = ['A', 'B', 'C', 'D'];
      const G = MV.frame(460, 270, [0.3, 4.7], [0, 1.15], 40);
      let s = MV.axes(G, { xstep: 10, ystep: 0.25 });
      p.forEach((v, i) => {
        const x = i + 1, bw = 0.3;
        s += `<rect class="mv-bar" x="${G.sx(x - bw).toFixed(1)}" y="${G.sy(v).toFixed(1)}" width="${(G.sx(x) - G.sx(x - bw)).toFixed(1)}" height="${(G.sy(0) - G.sy(v)).toFixed(1)}"/>`;
        if (i < t) { const c = Math.min(1.1, term(v)); s += `<rect class="mv-bar o" x="${G.sx(x).toFixed(1)}" y="${G.sy(c).toFixed(1)}" width="${(G.sx(x + bw) - G.sx(x)).toFixed(1)}" height="${(G.sy(0) - G.sy(c)).toFixed(1)}"/>`; }
        s += `<text class="mv-tick" x="${G.sx(x).toFixed(1)}" y="${(G.sy(0) + 16).toFixed(1)}" text-anchor="middle">${names[i]}</text>`;
      });
      $('.en-plot', b).innerHTML = MV.svg(G, s, 'Entropy bar chart');
      const run = p.slice(0, t).reduce((a, v) => a + term(v), 0), H = p.reduce((a, v) => a + term(v), 0);
      const k = t - 1;
      $('.vz-msg', b).innerHTML = t === 0 ? 'Blue bars are the probabilities. Press Play to add up the surprise.' :
        p[k] > 0 ? `Outcome ${names[k]}: p = ${MV.num(p[k], 3)}, surprise log₂(1 ÷ ${MV.num(p[k], 3)}) = ${MV.num(Math.log2(1 / p[k]), 3)} bits, contribution ${MV.num(p[k], 3)} × ${MV.num(Math.log2(1 / p[k]), 3)} = <b>${MV.num(term(p[k]), 3)}</b>.` :
        `Outcome ${names[k]} never happens, so it adds nothing.`;
      $('.en-out', b).innerHTML = `running total: <b>${MV.num(run, 3)}</b> bits<br>full entropy H = ${MV.num(H, 3)} bits<br>largest possible for 4 outcomes: log₂ 4 = 2 bits` + (t === 4 ? `<br>${H > 1.9 ? 'Nearly uniform: as unpredictable as 4 outcomes can be.' : H < 0.4 ? 'Nearly certain: very little surprise on average.' : 'In between: some outcomes are favourites.'}` : '');
    }
    const P = Player($('.vz-p', b), show, 1300);
    ['a', 'b', 'c', 'd'].forEach((k, i) => wireSlider(b, k, v => { w[i] = v; show(P.i); }));
    wireSeg(b, 'pre', v => { w = PRE[v].slice(); ['a', 'b', 'c', 'd'].forEach((k, i) => setSl(b, k, w[i])); P.load(5, 0); });
    P.load(5, 0);
  };

  /* ----- softmax stage by stage ----- */
  W.softmax = el => {
    const b = shell(el, 'Softmax step by step', 'Set the three logits (raw scores), the temperature T and the correct class. Press Play to follow the stages: divide by T, subtract the max, exponentiate, divide by the sum, and finally the cross entropy loss.');
    b.innerHTML = `<div class="vz-row">${slider('z1', 'cat logit', -5, 5, 2, 0.1)}${slider('z2', 'dog logit', -5, 5, 1, 0.1)}${slider('z3', 'bird logit', -5, 5, 0.1, 0.1)}</div>
      <div class="vz-row">${slider('T', 'temperature T', 0.2, 5, 1, 0.1)}${seg('y', [['0', 'answer: cat'], ['1', 'dog'], ['2', 'bird']], '0')}</div>
      <div class="mv-wrap"><div class="sm-plot"></div><div class="mv-side"><div class="mv-read sm-out" aria-live="polite"></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let z = [2, 1, 0.1], T = 1, y = 0;
    const names = ['cat', 'dog', 'bird'];
    function stages() {
      const a = z.map(v => v / T), m = Math.max(...a), sh = a.map(v => v - m), e = sh.map(Math.exp), s = e.reduce((x, v) => x + v, 0), p = e.map(v => v / s);
      return { a, m, sh, e, s, p };
    }
    function show(t) {
      const S = stages();
      const vals = [z, S.a, S.sh, S.e, S.p, S.p][t];
      const lo = Math.min(0, ...vals), hi = Math.max(0.0001, ...vals), pad = (hi - lo) * 0.18 || 0.2;
      const G = MV.frame(460, 260, [0.3, 3.7], [lo - (lo < 0 ? pad : 0), hi + pad], 40);
      let s = MV.axes(G, { xstep: 10 });
      vals.forEach((v, i) => {
        const x = i + 1, bw = 0.32, top = Math.max(v, 0), bot = Math.min(v, 0);
        s += `<rect class="mv-bar ${t >= 4 && i === y ? 'o' : ''}" x="${G.sx(x - bw).toFixed(1)}" y="${G.sy(top).toFixed(1)}" width="${(G.sx(x + bw) - G.sx(x - bw)).toFixed(1)}" height="${Math.max(1, G.sy(bot) - G.sy(top)).toFixed(1)}"/>`;
        s += `<text class="mv-tick" x="${G.sx(x).toFixed(1)}" y="${(G.sy(top) - 6).toFixed(1)}" text-anchor="middle">${MV.num(v, 3)}</text>`;
        s += `<text class="mv-tick" x="${G.sx(x).toFixed(1)}" y="${(G.h - 8).toFixed(1)}" text-anchor="middle">${names[i]}</text>`;
      });
      $('.sm-plot', b).innerHTML = MV.svg(G, s, 'Softmax stages');
      const L = -Math.log(S.p[y]);
      $('.vz-msg', b).innerHTML = [
        `Raw logits: ${z.map(v => MV.num(v, 2)).join(', ')}. They can be any numbers, even negative.`,
        `Divide by the temperature T = ${MV.num(T, 1)}: ${S.a.map(v => MV.num(v, 3)).join(', ')}. ${T < 1 ? 'Small T stretches the gaps.' : T > 1 ? 'Large T squeezes the gaps.' : 'T = 1 leaves them unchanged.'}`,
        `Subtract the largest (${MV.num(S.m, 3)}): ${S.sh.map(v => MV.num(v, 3)).join(', ')}. Now the biggest is 0, so e to the power never overflows.`,
        `Exponentiate: ${S.e.map(v => MV.num(v, 4)).join(', ')}. All positive now. Their sum is ${MV.num(S.s, 4)}.`,
        `Divide by the sum: ${S.p.map(v => MV.num(v, 4)).join(', ')}. These are probabilities that add up to 1.`,
        `The answer is ${names[y]}, which got p = ${MV.num(S.p[y], 4)}. Cross entropy loss = −ln ${MV.num(S.p[y], 4)} = <b>${MV.num(L, 4)}</b>.`][t];
      $('.sm-out', b).innerHTML = `probabilities: ${S.p.map((v, i) => `${names[i]} ${MV.num(v, 3)}`).join(', ')}<br>loss for ${names[y]}: <b>${MV.num(L, 3)}</b><br>${S.p[y] === Math.max(...S.p) ? 'The model already favours the right answer.' : 'The model favours the wrong class, so the loss is large.'}`;
    }
    const P = Player($('.vz-p', b), show, 1500);
    ['z1', 'z2', 'z3'].forEach((k, i) => wireSlider(b, k, v => { z[i] = v; show(P.i); }));
    wireSlider(b, 'T', v => { T = v; show(P.i); });
    wireSeg(b, 'y', v => { y = +v; show(P.i); });
    P.load(6, 0);
  };

  /* ----- threshold, confusion matrix and ROC ----- */
  W.roc = el => {
    const b = shell(el, 'Threshold, confusion matrix and ROC', 'Orange dots are real positives and blue dots real negatives, placed by the model score. Everything at or right of the threshold is flagged positive. Drag the threshold or press Play to sweep it from 1 down to 0 and trace the ROC curve.');
    b.innerHTML = `<div class="vz-row">${slider('t', 'threshold', 0, 1, 0.5, 0.01)}${slider('sep', 'how well the model separates', 0, 3, 1.5, 0.1)}</div>
      <div class="mv-wrap"><div><div class="rc-strip"></div><div class="rc-roc"></div></div><div class="mv-side"><div class="mv-read rc-out" aria-live="polite"></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let seed = 99;
    const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
    const gauss = () => Math.sqrt(-2 * Math.log(Math.max(1e-12, rnd()))) * Math.cos(2 * Math.PI * rnd());
    const N = 30, raw = Array.from({ length: 2 * N }, gauss);
    let thr = 0.5, sep = 1.5, sweeping = false;
    const sig = v => 1 / (1 + Math.exp(-v));
    const data = () => raw.map((g, i) => ({ y: i < N ? 1 : 0, s: sig((i < N ? sep / 2 : -sep / 2) + g * 0.9) }));
    function counts(D, t) { let tp = 0, fp = 0, fn = 0, tn = 0; D.forEach(d => { const f = d.s >= t; if (f && d.y) tp++; else if (f) fp++; else if (d.y) fn++; else tn++; }); return { tp, fp, fn, tn }; }
    function rocPts(D) { const ts = [1.01, ...D.map(d => d.s).sort((a, b) => b - a), -0.01]; return ts.map(t => { const c = counts(D, t); return [c.fp / N, c.tp / N]; }); }
    function auc(D) { let w = 0; D.filter(d => d.y).forEach(a => D.filter(d => !d.y).forEach(c => { w += a.s > c.s ? 1 : a.s === c.s ? 0.5 : 0; })); return w / (N * N); }
    function draw(t, upto) {
      const D = data(), c = counts(D, t);
      const G = MV.frame(460, 150, [-0.3, 1], [0, 3], 18);
      let s = `<line class="mv-axis" x1="${G.sx(0)}" y1="${G.sy(0)}" x2="${G.w - G.pad}" y2="${G.sy(0)}"/>`;
      for (let x = 0; x <= 1.001; x += 0.25) s += `<text class="mv-tick" x="${G.sx(x).toFixed(1)}" y="${(G.sy(0) + 15).toFixed(1)}" text-anchor="middle">${MV.num(x, 2)}</text>`;
      D.forEach((d, i) => { const row = d.y ? 2.2 : 0.9, jit = ((i * 37) % 7 - 3) * 0.17; s += MV.dot(G, d.s, row + jit, d.y ? 'o' : 'a', 4.5); });
      s += MV.line(G, t, 0, t, 3, 'mv-v k');
      s += `<text class="mv-lab sm" x="${G.sx(-0.29)}" y="${G.sy(2.2) + 4}">positives</text><text class="mv-lab sm" x="${G.sx(-0.29)}" y="${G.sy(0.9) + 4}">negatives</text>`;
      $('.rc-strip', b).innerHTML = MV.svg(G, s, 'Scores of positives and negatives');
      const R = MV.frame(300, 300, [0, 1], [0, 1], 34);
      let r = MV.axes(R, { xstep: 0.25, ystep: 0.25, xl: 'FPR', yl: 'TPR' });
      r += MV.line(R, 0, 0, 1, 1, 'mv-v k dash');
      const pts = rocPts(D).filter((p, i, arr) => upto === undefined || i === 0 || true);
      const full = `M${pts.map(p => `${R.sx(p[0]).toFixed(1)},${R.sy(p[1]).toFixed(1)}`).join('L')}`;
      const trace = rocPts(D).filter(p => upto === undefined || p[0] <= upto.fpr + 1e-9 && p[1] <= upto.tpr + 1e-9);
      r += `<path class="mv-curve c2 thin dash" d="${full}"/>`;
      if (trace.length) r += `<path class="mv-curve" d="M${trace.map(p => `${R.sx(p[0]).toFixed(1)},${R.sy(p[1]).toFixed(1)}`).join('L')}"/>`;
      r += MV.dot(R, c.fp / N, c.tp / N, 'p', 7);
      $('.rc-roc', b).innerHTML = MV.svg(R, r, 'ROC curve');
      const prec = c.tp + c.fp ? c.tp / (c.tp + c.fp) : 0, rec = c.tp / N, f1 = prec + rec ? 2 * prec * rec / (prec + rec) : 0;
      $('.rc-out', b).innerHTML = `TP ${c.tp}, FP ${c.fp}<br>FN ${c.fn}, TN ${c.tn}<br>precision ${MV.num(prec, 3)}<br>recall (TPR) ${MV.num(rec, 3)}<br>FPR ${MV.num(c.fp / N, 3)}<br>F1 ${MV.num(f1, 3)}<br>AUC <b>${MV.num(auc(D), 3)}</b>`;
      return c;
    }
    function show(i) {
      const t = 1 - i / 10;
      thr = Math.round(t * 100) / 100;
      $('[data-sl="t"]', b).value = thr; $('[data-slv="t"]', b).textContent = thr;
      const c = draw(thr, { fpr: counts(data(), thr).fp / N, tpr: counts(data(), thr).tp / N });
      $('.vz-msg', b).innerHTML = i === 0 ? 'Threshold 1: nothing is flagged, so the ROC point sits at (0, 0). Press Play to lower it.' :
        `Threshold ${MV.num(thr, 2)}: ${c.tp} of ${N} positives caught (TPR ${MV.num(c.tp / N, 2)}) and ${c.fp} of ${N} negatives wrongly flagged (FPR ${MV.num(c.fp / N, 2)}). ${i === 10 ? 'Threshold 0 flags everything: the point reaches (1, 1).' : 'The point moves up and right.'}`;
    }
    const P = Player($('.vz-p', b), show, 900);
    wireSlider(b, 't', v => { thr = v; draw(thr); $('.vz-msg', b).innerHTML = `Threshold ${MV.num(thr, 2)}: the purple dot on the ROC curve is this threshold. Lower it to catch more positives at the cost of more false alarms.`; });
    wireSlider(b, 'sep', v => { sep = v; draw(thr); });
    P.load(11, 5);
  };
})();
'''

CSS = r'''
.rc-roc{max-width:320px; margin:8px auto 0}
'''

# ---------------------------------------------------------------- deeper explanations and extra animations
# Each lesson above gives the short version. DEEPER adds a slower, fuller explanation (and sometimes an
# animation) to the end of the lesson with the same id.
DEEPER = {
    'entropy': deep('information gain and mutual information, worked', f'''
<p>A decision tree asks one question at a time, such as "is income above 50000?". A good question leaves the groups below it purer, with lower entropy. The drop in entropy is the <b>information gain</b>.</p>
{worked('Information gain of one split', [
        'Parent node: 10 customers, 5 bought and 5 did not. Entropy <span class="eq">H = 1 bit</span> (a fair coin).',
        'Split on "visited twice": left gets 4 customers who all bought (<span class="eq">H = 0</span>). Right gets 6 customers, 1 bought and 5 did not.',
        'Right entropy: <span class="eq">−(1/6 log₂ 1/6 + 5/6 log₂ 5/6) ≈ 0.431 + 0.219 = 0.650 bits</span>',
        'Weighted entropy after the split: <span class="eq">0.4 × 0 + 0.6 × 0.650 = 0.390</span>',
        'Information gain: <span class="eq">1 − 0.390 = 0.610 bits</span>. The tree compares this with every other possible question and keeps the biggest.'])}
<p>Information gain is a special case of a more general idea, <b>mutual information</b>. It measures how much knowing one variable reduces your uncertainty about another.</p>
{fx('Mutual information', 'I(X, Y) = H(Y) − H(Y | X) = Σ p(x, y) log [p(x, y) ÷ (p(x) p(y))]', 'It is 0 exactly when X and Y are independent, and it catches curved and non numeric relationships that correlation misses.')}
{ml('Feature selection often ranks features by their mutual information with the label (scikit learn has mutual_info_classif for this). Unlike correlation, it can spot a feature whose effect is U shaped, and it works for categories such as city or device type.')}
'''),
    'xent': deep('cross entropy and KL with real numbers', f'''
{worked('Reality p = [0.7, 0.2, 0.1], model q = [0.5, 0.3, 0.2], natural logs', [
        'Entropy of reality: <span class="eq">H(p) = −(0.7 ln 0.7 + 0.2 ln 0.2 + 0.1 ln 0.1) ≈ 0.802</span>',
        'Cross entropy: <span class="eq">H(p, q) = −(0.7 ln 0.5 + 0.2 ln 0.3 + 0.1 ln 0.2) ≈ 0.887</span>',
        'KL divergence: <span class="eq">0.887 − 0.802 = 0.085</span> nats of extra surprise per outcome',
        'If the model changes q to exactly [0.7, 0.2, 0.1], the cross entropy falls to 0.802 and KL to 0. No q can do better than H(p).'])}
<p>Move the model’s guess q below and watch the three bars. Entropy H(p) never moves, because it belongs to reality. Cross entropy is always at least as big, and the gap between them is the KL divergence. Press Play to let q walk towards p.</p>
{viz('xentbars')}
<p><b>Why KL is not symmetric.</b> KL(p ‖ q) punishes q heavily for giving tiny probability to something p says happens often. KL(q ‖ p) punishes the opposite. Generative models choose between them on purpose: one direction makes a model cover every possible output, the other makes it focus on the most common ones.</p>
'''),
    'losses': deep('compare the losses and their slopes side by side', f'''
<p>The shape of a loss decides how hard the model is pushed by each error. Look at the slope (the gradient) as well as the loss itself. MSE pushes in proportion to the error, so one huge outlier gets a huge push. MAE pushes with the same strength whatever the size of the error. Huber behaves like MSE for small errors and like MAE for big ones, with δ choosing where it switches.</p>
{viz('losscmp')}
{table(['Error e', 'MSE e²', 'MAE |e|', 'Huber, δ = 1'], [
        ['0.5', '0.25', '0.5', '0.125'],
        ['1', '1', '1', '0.5'],
        ['3', '9', '3', '2.5'],
        ['10 (an outlier)', '100', '10', '9.5'],
    ])}
<p>Another useful loss is the <b>quantile (pinball) loss</b>. It charges q × e for under predictions and (1 − q) × |e| for over predictions. With q = 0.9, under predicting costs nine times more, so the model learns the 90th percentile instead of the middle. Delivery apps and energy forecasters use it to predict "safe" upper estimates.</p>
'''),
    'logloss': deep('the loss curve and the famous p − y gradient', f'''
<p>Slide the predicted probability p below. When the true label is 1, the loss −ln p is gentle near p = 1 and shoots up towards infinity as p heads to 0. Being confidently wrong is punished far more than being unsure.</p>
{viz('logloss')}
{worked('Why the gradient is simply p − y', [
        'The model outputs <span class="eq">p = σ(z)</span>, where z is the score (logit).',
        'Loss: <span class="eq">L = −[y ln p + (1 − y) ln(1 − p)]</span>',
        'Slope with respect to p: <span class="eq">∂L/∂p = −y ÷ p + (1 − y) ÷ (1 − p) = (p − y) ÷ (p(1 − p))</span>',
        'Sigmoid slope (Chapter 6): <span class="eq">∂p/∂z = p(1 − p)</span>',
        'Chain rule: <span class="eq">∂L/∂z = (p − y) ÷ (p(1 − p)) × p(1 − p) = p − y</span>. The p(1 − p) cancels completely.'])}
<p>That cancellation is the real reason log loss and sigmoid are always used together. The gradient is just "prediction minus truth", which is large when the model is badly wrong and never gets stuck in the flat ends of the sigmoid. The same thing happens for softmax with cross entropy: the gradient for each class is pᵢ − yᵢ.</p>
'''),
    'reg': deep('why L1 gives exact zeros: the picture', f'''
<p>Regularisation can be seen as a budget on the weights. L2 says the weights must stay inside a circle, w₁² + w₂² ≤ t². L1 says they must stay inside a diamond, |w₁| + |w₂| ≤ t. The best allowed point is where the loss contours (the ellipses) first touch the shape. A diamond has sharp corners sitting exactly on the axes, and the ellipses very often touch at a corner, where one weight is exactly 0. A circle has no corners, so that almost never happens.</p>
{viz('l1l2')}
{table(['Method', 'Penalty', 'Effect'], [
        ['Ridge (L2)', 'λ Σ wⱼ²', 'shrinks all weights smoothly, keeps them all'],
        ['Lasso (L1)', 'λ Σ |wⱼ|', 'sets some weights exactly to 0, choosing features'],
        ['Elastic net', 'λ₁ Σ |wⱼ| + λ₂ Σ wⱼ²', 'a mix: sparse like L1 but stable when features are correlated'],
    ])}
{ml('There is also a probability reading. L2 regularisation is the same as assuming, before seeing data, that each weight comes from a normal distribution centred on 0. L1 is the same as assuming a Laplace distribution, which has a sharp peak at 0. Chapter 15 shows this link through MAP estimation.')}
'''),
    'metrics': deep('choosing the threshold, PR curves and F beta', f'''
<p>A classifier gives a score, and you choose the threshold that turns scores into yes or no. Raising the threshold flags fewer cases: precision usually goes up and recall goes down. There is no single right threshold. It depends on what each kind of mistake costs.</p>
{fx('F beta score', f'F<sub>β</sub> = (1 + β²) × {frac("precision × recall", "β² × precision + recall")}', 'β = 1 gives F1. β = 2 counts recall as more important (screening for disease). β = 0.5 counts precision as more important (spam filtering).')}
{worked('Picking a threshold by cost', [
        'A missed fraud (FN) costs 500. A false alarm (FP) costs 5, the time to check a payment.',
        'Threshold 0.5: <span class="eq">FN = 20</span>, <span class="eq">FP = 100</span>. Cost <span class="eq">20 × 500 + 100 × 5 = 10500</span>',
        'Threshold 0.2: <span class="eq">FN = 8</span>, <span class="eq">FP = 600</span>. Cost <span class="eq">8 × 500 + 600 × 5 = 7000</span>',
        'The lower threshold has worse precision, but costs less overall, so it is the better business choice.'])}
<p>When positives are rare (fraud, rare diseases), a <b>precision recall curve</b> is often more honest than the ROC curve. ROC uses the false positive rate, whose bottom FP + TN is huge when negatives are plentiful, so even many false alarms look like a small rate. Precision shows those false alarms directly.</p>
'''),
}
for _p in PARTS:
    _p['html'] += DEEPER.get(_p['id'], '')

VIZ_JS += r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;

  /* ----- entropy, cross entropy and KL as three bars ----- */
  W.xentbars = el => {
    const b = shell(el, 'Entropy, cross entropy and KL', 'Pick the true distribution p. Move the model’s q₁ and q₂ (q₃ is whatever is left). Press Play to let q walk step by step towards p.');
    const PS = { soft: [0.7, 0.2, 0.1], hot: [1, 0, 0], uni: [1 / 3, 1 / 3, 1 / 3] };
    b.innerHTML = `<div class="vz-row">${seg('p', [['soft', 'p = [0.7, 0.2, 0.1]'], ['hot', 'one hot p = [1, 0, 0]'], ['uni', 'uniform p']], 'soft')}</div><div class="mv-wrap"><div class="xb-plot"></div><div class="mv-side">${slider('q1', 'q₁', 0.01, 0.98, 0.5, 0.01)}${slider('q2', 'q₂', 0.01, 0.98, 0.3, 0.01)}<div class="mv-read xb-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let p = PS.soft, q = [0.5, 0.3, 0.2], start = q.slice();
    const lg = v => v > 0 ? Math.log(v) : 0;
    function draw() {
      q[2] = Math.max(0.01, 1 - q[0] - q[1]); const s3 = q[0] + q[1] + q[2]; const Q = q.map(v => v / s3);
      const H = -p.reduce((a, v) => a + (v > 0 ? v * lg(v) : 0), 0), X = -p.reduce((a, v, i) => a + (v > 0 ? v * Math.log(Q[i]) : 0), 0), K = X - H;
      const G = MV.frame(440, 280, [0, 10], [0, 1.15]);
      let s = MV.axes(G, { labels: false });
      [0, 1, 2].forEach(i => { const x = 0.5 + i * 1.4; s += `<rect class="mv-bar" x="${G.sx(x)}" y="${G.sy(p[i])}" width="${G.sx(0.55) - G.sx(0)}" height="${G.sy(0) - G.sy(p[i])}"/><rect class="mv-bar o" x="${G.sx(x + 0.6)}" y="${G.sy(Q[i])}" width="${G.sx(0.55) - G.sx(0)}" height="${G.sy(0) - G.sy(Q[i])}"/>` + MV.text(G, x + 0.57, 0, 'class ' + (i + 1), { dy: 14, anchor: 'middle', cls: 'sm' }); });
      const top = Math.max(1.2, X * 1.1), bar = (x, v, c, lab) => { const h = v / top; return `<rect class="mv-bar ${c}" x="${G.sx(x)}" y="${G.sy(h)}" width="${G.sx(0.8) - G.sx(0)}" height="${G.sy(0) - G.sy(h)}"/>` + MV.text(G, x + 0.4, 0, lab, { dy: 14, anchor: 'middle', cls: 'sm' }) + MV.text(G, x + 0.4, h, MV.num(v, 3), { dy: -4, anchor: 'middle', cls: 'sm' }); };
      s += MV.line(G, 5.1, 0, 5.1, 1.1, 'mv-v k dash') + bar(5.6, H, '', 'H(p)') + bar(7, X, 'o', 'H(p, q)') + bar(8.4, K, 'g', 'KL');
      $('.xb-plot', b).innerHTML = MV.svg(G, s, 'Distributions and their information measures');
      $('.xb-out', b).innerHTML = `<div class="mv-legend"><span><i></i>p (reality)</span><span><i class="o"></i>q (model)</span></div>q = [${Q.map(v => MV.num(v, 2)).join(', ')}]<br>H(p) = <b>${MV.num(H, 4)}</b><br>H(p, q) = <b>${MV.num(X, 4)}</b><br>KL(p ‖ q) = <span class="big">${MV.num(K, 4)}</span>` + (K < 0.002 ? '<br>✅ q matches p: no extra surprise.' : '');
    }
    const setQ = () => { $('[data-sl="q1"]', b).value = q[0]; $('[data-slv="q1"]', b).textContent = MV.num(q[0]); $('[data-sl="q2"]', b).value = q[1]; $('[data-slv="q2"]', b).textContent = MV.num(q[1]); };
    const P = Player($('.vz-p', b), t => { const f = t / 10, tgt = p.map(v => Math.min(0.98, Math.max(0.01, v))); q[0] = start[0] + (tgt[0] - start[0]) * f; q[1] = start[1] + (tgt[1] - start[1]) * f; setQ(); draw(); }, 500);
    wireSeg(b, 'p', k => { p = PS[k]; start = [q[0], q[1], q[2]]; P.load(11, 0); });
    wireSlider(b, 'q1', v => { P.pause(); q[0] = Math.min(v, 0.99 - q[1]); start = q.slice(); draw(); });
    wireSlider(b, 'q2', v => { P.pause(); q[1] = Math.min(v, 0.99 - q[0]); start = q.slice(); draw(); });
    P.load(11, 0);
  };

  /* ----- MSE, MAE and Huber, as losses or as gradients ----- */
  W.losscmp = el => {
    const b = shell(el, 'Three losses and how hard they push', 'Switch between the loss and its gradient. Move δ to change where Huber switches from squared to straight. Press Play to slide the error e outwards.');
    b.innerHTML = `<div class="vz-row">${seg('v', [['loss', 'Loss'], ['grad', 'Gradient (push)']], 'loss')}</div><div class="mv-wrap"><div class="lo-plot"></div><div class="mv-side">${slider('d', 'Huber δ', 0.25, 3, 1, 0.25)}${slider('e', 'error e', -4, 4, 2, 0.1)}<div class="mv-legend"><span><i></i>MSE</span><span><i class="o"></i>MAE</span><span><i class="g"></i>Huber</span></div><div class="mv-read lo-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let view = 'loss', d = 1, e = 2;
    const L = { mse: x => x * x, mae: x => Math.abs(x), hub: x => Math.abs(x) <= d ? 0.5 * x * x : d * (Math.abs(x) - 0.5 * d) };
    const D = { mse: x => 2 * x, mae: x => Math.sign(x), hub: x => Math.abs(x) <= d ? x : d * Math.sign(x) };
    function draw() {
      const F = view === 'loss' ? L : D, G = view === 'loss' ? MV.frame(440, 300, [-4, 4], [-0.5, 8]) : MV.frame(440, 300, [-4, 4], [-8, 8]);
      let s = MV.axes(G, { xstep: 1, ystep: 2, xl: 'e', yl: view === 'loss' ? 'loss' : 'gradient' }) + MV.curve(G, F.mse) + MV.curve(G, F.mae, 'c2') + MV.curve(G, F.hub, 'c3');
      s += MV.line(G, e, G.yr[0], e, G.yr[1], 'mv-v k dash');
      ['mse', 'mae', 'hub'].forEach((k, i) => { const y = F[k](e); if (y >= G.yr[0] && y <= G.yr[1]) s += MV.dot(G, e, y, ['', 'o', 'g'][i], 5); });
      $('.lo-plot', b).innerHTML = MV.svg(G, s, 'Loss curves');
      const f = v => MV.num(v, 3);
      $('.lo-out', b).innerHTML = `e = <b>${f(e)}</b><br>MSE: loss ${f(L.mse(e))}, push ${f(D.mse(e))}<br>MAE: loss ${f(L.mae(e))}, push ${f(D.mae(e))}<br>Huber: loss ${f(L.hub(e))}, push ${f(D.hub(e))}<br>` + (Math.abs(e) > d ? 'Beyond δ, Huber pushes with a fixed strength δ, like MAE.' : 'Inside δ, Huber behaves like half of MSE.');
    }
    const P = Player($('.vz-p', b), t => { e = t * 0.25; $('[data-sl="e"]', b).value = e; $('[data-slv="e"]', b).textContent = MV.num(e); draw(); }, 300);
    wireSeg(b, 'v', k => { view = k; draw(); });
    wireSlider(b, 'd', v => { d = v; draw(); });
    wireSlider(b, 'e', v => { P.pause(); e = v; draw(); });
    P.load(17, 8);
  };

  /* ----- log loss against the predicted probability ----- */
  W.logloss = el => {
    const b = shell(el, 'Log loss for one prediction', 'Choose the true label and move the predicted probability p of class 1. Press Play to sweep p from very wrong to very right.');
    b.innerHTML = `<div class="vz-row">${seg('y', [['1', 'true label y = 1'], ['0', 'true label y = 0']], '1')}</div><div class="mv-wrap"><div class="ll-plot"></div><div class="mv-side">${slider('p', 'predicted p', 0.01, 0.99, 0.6, 0.01)}<div class="mv-read ll-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let y = 1, p = 0.6;
    const G = MV.frame(440, 300, [0, 1], [0, 5]);
    function draw() {
      const f = y === 1 ? (x => -Math.log(x)) : (x => -Math.log(1 - x));
      let s = MV.axes(G, { xstep: 0.1, ystep: 1, xl: 'p', yl: 'loss' }) + MV.curve(G, f, '', { from: 0.005, to: 0.995 }) + MV.curve(G, y === 1 ? (x => -Math.log(1 - x)) : (x => -Math.log(x)), 'thin dash c4', { from: 0.005, to: 0.995 });
      const L = f(p);
      s += MV.dot(G, p, Math.min(5, L), 'o', 7);
      $('.ll-plot', b).innerHTML = MV.svg(G, s, 'Log loss curve');
      $('.ll-out', b).innerHTML = `y = ${y}, p = <b>${MV.num(p, 2)}</b><br>loss = ${y === 1 ? '−ln p' : '−ln(1 − p)'} = <span class="big">${MV.num(L, 3)}</span><br>gradient with respect to the logit: p − y = <b>${MV.num(p - y, 2)}</b><br>` +
        (L > 2 ? '🚨 Confident and wrong: a very large loss.' : L < 0.2 ? '✅ Confident and right: tiny loss.' : 'Unsure: a moderate loss.') + '<br><small>The dashed curve is the loss for the other label.</small>';
    }
    const P = Player($('.vz-p', b), t => { p = y === 1 ? 0.01 + t * 0.07 : 0.99 - t * 0.07; $('[data-sl="p"]', b).value = p; $('[data-slv="p"]', b).textContent = MV.num(p); draw(); }, 400);
    wireSeg(b, 'y', k => { y = +k; draw(); });
    wireSlider(b, 'p', v => { P.pause(); p = v; draw(); });
    P.load(15, 8);
  };

  /* ----- L1 diamond versus L2 circle against loss ellipses ----- */
  W.l1l2 = el => {
    const b = shell(el, 'L1 diamond versus L2 circle', 'The ellipses are contours of the loss, whose best point (purple) is where the model would go with no penalty. The shaded shape is the weight budget. The orange dot is the best point inside the budget. Press Play to shrink the budget.');
    b.innerHTML = `<div class="vz-row">${seg('k', [['l1', 'L1 (diamond)'], ['l2', 'L2 (circle)']], 'l1')}</div><div class="mv-wrap"><div class="lr-plot"></div><div class="mv-side">${slider('t', 'budget t', 0.2, 3.5, 1.5, 0.1)}${slider('cx', 'best w₁ without penalty', -3, 3, 2.5, 0.1)}${slider('cy', 'best w₂ without penalty', -3, 3, 1, 0.1)}<div class="mv-read lr-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let kind = 'l1', t = 1.5, c = [2.5, 1];
    const A = [[1, 0.6], [0.6, 2]];
    const loss = (x, y) => { const dx = x - c[0], dy = y - c[1]; return A[0][0] * dx * dx + 2 * A[0][1] * dx * dy + A[1][1] * dy * dy; };
    const G = MV.frame(400, 400, [-4, 4], [-4, 4]);
    function best() {
      const inside = kind === 'l1' ? Math.abs(c[0]) + Math.abs(c[1]) <= t : Math.hypot(c[0], c[1]) <= t;
      if (inside) return c.slice();
      let bp = null, bl = Infinity;
      for (let i = 0; i < 4000; i++) {
        const a = i / 4000 * 2 * Math.PI; let x, y;
        if (kind === 'l2') { x = t * Math.cos(a); y = t * Math.sin(a); }
        else { const u = i / 1000, q = Math.floor(u), f = u - q, P0 = [[t, 0], [0, t], [-t, 0], [0, -t]][q], P1 = [[0, t], [-t, 0], [0, -t], [t, 0]][q]; x = P0[0] + (P1[0] - P0[0]) * f; y = P0[1] + (P1[1] - P0[1]) * f; }
        const l = loss(x, y); if (l < bl) { bl = l; bp = [x, y]; }
      }
      return bp;
    }
    function draw() {
      let s = MV.axes(G, { xstep: 1, ystep: 1, labels: false, xl: 'w₁', yl: 'w₂' });
      const shape = kind === 'l1' ? `<polygon class="mv-poly g" points="${[[t, 0], [0, t], [-t, 0], [0, -t]].map(p => G.sx(p[0]) + ',' + G.sy(p[1])).join(' ')}"/>` : `<circle class="mv-poly g" cx="${G.sx(0)}" cy="${G.sy(0)}" r="${G.sx(t) - G.sx(0)}"/>`;
      s += shape;
      const ev = (() => { const tr = A[0][0] + A[1][1], dt = A[0][0] * A[1][1] - A[0][1] ** 2, r = Math.sqrt(tr * tr / 4 - dt), l1 = tr / 2 + r, l2 = tr / 2 - r, ang = Math.atan2(l1 - A[0][0], A[0][1]); return { l1, l2, ang }; })();
      [0.5, 2, 4.5, 8, 12.5, 18].forEach(lv => { const pts = []; for (let k = 0; k <= 80; k++) { const th = k / 80 * 2 * Math.PI, u = Math.sqrt(lv / ev.l1) * Math.cos(th), v = Math.sqrt(lv / ev.l2) * Math.sin(th); const x = c[0] + u * Math.cos(ev.ang) - v * Math.sin(ev.ang), y = c[1] + u * Math.sin(ev.ang) + v * Math.cos(ev.ang); pts.push(G.sx(x).toFixed(1) + ',' + G.sy(y).toFixed(1)); } s += `<polyline class="mv-cont" points="${pts.join(' ')}"/>`; });
      const w = best();
      s += MV.dot(G, c[0], c[1], 'p', 6) + MV.dot(G, w[0], w[1], 'o', 7);
      $('.lr-plot', b).innerHTML = MV.svg(G, s, 'Constraint shapes and loss contours');
      const z = v => Math.abs(v) < 0.02;
      $('.lr-out', b).innerHTML = `${kind === 'l1' ? '|w₁| + |w₂| ≤ ' : '√(w₁² + w₂²) ≤ '}${MV.num(t)}<br>best weights inside the budget: <b>[${MV.num(z(w[0]) ? 0 : w[0], 2)}, ${MV.num(z(w[1]) ? 0 : w[1], 2)}]</b><br>` +
        (z(w[0]) || z(w[1]) ? '✂️ One weight is exactly 0: that feature has been switched off.' : 'Both weights are non zero, just shrunk towards 0.');
    }
    const P = Player($('.vz-p', b), k => { t = 3.5 - k * 0.3; $('[data-sl="t"]', b).value = t; $('[data-slv="t"]', b).textContent = MV.num(t); draw(); }, 600);
    wireSeg(b, 'k', v => { kind = v; draw(); });
    wireSlider(b, 't', v => { P.pause(); t = v; draw(); });
    wireSlider(b, 'cx', v => { c[0] = v; draw(); });
    wireSlider(b, 'cy', v => { c[1] = v; draw(); });
    P.load(12, 7);
  };
})();
'''
CSS += r'''
.lr-plot .mv-svg{max-height:420px}
'''

T = K.topic(
    slug='loss-metrics', topic='loss-metrics', prefix='mm12', short='Losses and metrics', emoji='🎯',
    title='Entropy, Loss Functions and Metrics',
    module=('🤖', 'Maths inside ML models', 'models', 'Entropy, loss functions, regularisation and evaluation metrics: where all the earlier maths meets real models.'),
    minutes=60,
    lead='This is where the maths meets real models. Measure surprise with entropy, see how cross entropy and softmax train classifiers, compare MSE, MAE and log loss, shrink weights with regularisation, and judge a model with precision, recall and the ROC curve.',
    desc='Information theory and evaluation for machine learning: entropy, cross entropy, KL divergence, softmax and log-sum-exp, MSE, MAE and Huber loss, log loss, L1 and L2 regularisation, confusion matrix, precision, recall, F1, ROC and AUC.',
    summary='Surprise and entropy in bits, cross entropy and KL divergence, softmax with temperature and the log-sum-exp trick, regression losses and outliers, binary cross entropy and its p − y gradient, ridge and lasso regularisation, and classification metrics from the confusion matrix to ROC and AUC.',
    keywords=['entropy', 'information theory', 'cross entropy', 'kl divergence', 'softmax', 'temperature', 'log sum exp', 'loss function', 'mse', 'mae', 'huber', 'log loss', 'regularisation', 'ridge', 'lasso', 'precision', 'recall', 'f1', 'roc', 'auc'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
