# Chapter 8: gradient descent in one and two dimensions, the learning rate, stochastic and mini batch
# gradient descent, momentum, RMSProp and Adam, convexity and saddles, constrained optimisation with
# Lagrange multipliers, and learning rate schedules.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz, deep

K = Kit()

# ---------------------------------------------------------------- programs
K.code('gd_basic', py=r'''
def loss(w):
    return w * w - 4 * w + 5              # a bowl whose lowest point is at w = 2


def grad(w):
    return 2 * w - 4


w, lr = 0.0, 0.1
print(f"start: w = {w:.4f}, loss = {loss(w):.4f}")
for step in range(1, 6):
    w = w - lr * grad(w)                  # step against the slope
    print(f"step {step}: w = {w:.4f}, loss = {loss(w):.4f}")
''', js=r'''
function loss(w) {
  return w * w - 4 * w + 5;               // a bowl whose lowest point is at w = 2
}

function grad(w) {
  return 2 * w - 4;
}

let w = 0.0;
const lr = 0.1;
console.log(`start: w = ${w.toFixed(4)}, loss = ${loss(w).toFixed(4)}`);
for (let step = 1; step <= 5; step++) {
  w = w - lr * grad(w);                   // step against the slope
  console.log(`step ${step}: w = ${w.toFixed(4)}, loss = ${loss(w).toFixed(4)}`);
}
''', ts=r'''
function loss(w: number): number {
  return w * w - 4 * w + 5;               // a bowl whose lowest point is at w = 2
}

function grad(w: number): number {
  return 2 * w - 4;
}

let w: number = 0.0;
const lr: number = 0.1;
console.log(`start: w = ${w.toFixed(4)}, loss = ${loss(w).toFixed(4)}`);
for (let step = 1; step <= 5; step++) {
  w = w - lr * grad(w);                   // step against the slope
  console.log(`step ${step}: w = ${w.toFixed(4)}, loss = ${loss(w).toFixed(4)}`);
}
''', java=r'''
public class GdBasic {
    static double loss(double w) {
        return w * w - 4 * w + 5;             // a bowl whose lowest point is at w = 2
    }

    static double grad(double w) {
        return 2 * w - 4;
    }

    public static void main(String[] args) {
        double w = 0.0, lr = 0.1;
        System.out.println(String.format("start: w = %.4f, loss = %.4f", w, loss(w)));
        for (int step = 1; step <= 5; step++) {
            w = w - lr * grad(w);                 // step against the slope
            System.out.println(String.format("step %d: w = %.4f, loss = %.4f", step, w, loss(w)));
        }
    }
}
''')

K.code('sgd', py=r'''
xs = [1, 2, 3, 4, 5]
ys = [3, 5, 7, 9, 11]                     # the hidden rule is y = 2x + 1
w, b, lr = 0.0, 0.0, 0.02


def mse(w, b):
    return sum((w * x + b - y) ** 2 for x, y in zip(xs, ys)) / len(xs)


for epoch in range(1, 31):
    for x, y in zip(xs, ys):              # one example at a time: stochastic gradient descent
        err = w * x + b - y
        w -= lr * 2 * err * x             # dL/dw for this one example
        b -= lr * 2 * err                 # dL/db for this one example
    if epoch in (1, 10, 30):
        print(f"epoch {epoch:2}: w = {w:.3f}, b = {b:.3f}, mse = {mse(w, b):.4f}")
''', js=r'''
const xs = [1, 2, 3, 4, 5];
const ys = [3, 5, 7, 9, 11];              // the hidden rule is y = 2x + 1
let w = 0, b = 0;
const lr = 0.02;

function mse(w, b) {
  return xs.reduce((s, x, i) => s + (w * x + b - ys[i]) ** 2, 0) / xs.length;
}

for (let epoch = 1; epoch <= 30; epoch++) {
  for (let i = 0; i < xs.length; i++) {   // one example at a time: stochastic gradient descent
    const err = w * xs[i] + b - ys[i];
    w -= lr * 2 * err * xs[i];            // dL/dw for this one example
    b -= lr * 2 * err;                    // dL/db for this one example
  }
  if ([1, 10, 30].includes(epoch)) {
    console.log(`epoch ${String(epoch).padStart(2)}: w = ${w.toFixed(3)}, b = ${b.toFixed(3)}, mse = ${mse(w, b).toFixed(4)}`);
  }
}
''', ts=r'''
const xs: number[] = [1, 2, 3, 4, 5];
const ys: number[] = [3, 5, 7, 9, 11];    // the hidden rule is y = 2x + 1
let w: number = 0, b: number = 0;
const lr: number = 0.02;

function mse(w: number, b: number): number {
  return xs.reduce((s, x, i) => s + (w * x + b - ys[i]) ** 2, 0) / xs.length;
}

for (let epoch = 1; epoch <= 30; epoch++) {
  for (let i = 0; i < xs.length; i++) {   // one example at a time: stochastic gradient descent
    const err: number = w * xs[i] + b - ys[i];
    w -= lr * 2 * err * xs[i];            // dL/dw for this one example
    b -= lr * 2 * err;                    // dL/db for this one example
  }
  if ([1, 10, 30].includes(epoch)) {
    console.log(`epoch ${String(epoch).padStart(2)}: w = ${w.toFixed(3)}, b = ${b.toFixed(3)}, mse = ${mse(w, b).toFixed(4)}`);
  }
}
''', java=r'''
public class Sgd {
    static int[] xs = {1, 2, 3, 4, 5};
    static int[] ys = {3, 5, 7, 9, 11};       // the hidden rule is y = 2x + 1

    static double mse(double w, double b) {
        double s = 0;
        for (int i = 0; i < xs.length; i++) s += Math.pow(w * xs[i] + b - ys[i], 2);
        return s / xs.length;
    }

    public static void main(String[] args) {
        double w = 0, b = 0, lr = 0.02;
        for (int epoch = 1; epoch <= 30; epoch++) {
            for (int i = 0; i < xs.length; i++) { // one example at a time: stochastic gradient descent
                double err = w * xs[i] + b - ys[i];
                w -= lr * 2 * err * xs[i];        // dL/dw for this one example
                b -= lr * 2 * err;                // dL/db for this one example
            }
            if (epoch == 1 || epoch == 10 || epoch == 30) {
                System.out.println(String.format("epoch %2d: w = %.3f, b = %.3f, mse = %.4f", epoch, w, b, mse(w, b)));
            }
        }
    }
}
''')

K.code('optimisers', py=r'''
import math


def grad(x, y):                           # f = 0.5x^2 + 25y^2, a long narrow valley
    return x, 50 * y


def run(name, steps=40):
    x, y = -4.0, 1.0
    vx = vy = mx = my = sx = sy = 0.0
    for t in range(1, steps + 1):
        gx, gy = grad(x, y)
        if name == "plain GD":
            x, y = x - 0.035 * gx, y - 0.035 * gy
        elif name == "momentum":
            vx, vy = 0.7 * vx + gx, 0.7 * vy + gy         # a rolling average of past gradients
            x, y = x - 0.03 * vx, y - 0.03 * vy
        else:                                             # Adam
            mx, my = 0.9 * mx + 0.1 * gx, 0.9 * my + 0.1 * gy
            sx, sy = 0.999 * sx + 0.001 * gx * gx, 0.999 * sy + 0.001 * gy * gy
            c1, c2 = 1 - 0.9 ** t, 1 - 0.999 ** t
            x -= 0.5 * (mx / c1) / (math.sqrt(sx / c2) + 1e-8)
            y -= 0.5 * (my / c1) / (math.sqrt(sy / c2) + 1e-8)
    return x, y, 0.5 * x * x + 25 * y * y


for name in ["plain GD", "momentum", "Adam"]:
    x, y, f = run(name)
    print(f"{name:9}: after 40 steps at ({x:.3f}, {y:.3f}), loss = {f:.5f}")
''', js=r'''
function grad(x, y) {                     // f = 0.5x^2 + 25y^2, a long narrow valley
  return [x, 50 * y];
}

function run(name, steps = 40) {
  let x = -4, y = 1, vx = 0, vy = 0, mx = 0, my = 0, sx = 0, sy = 0;
  for (let t = 1; t <= steps; t++) {
    const [gx, gy] = grad(x, y);
    if (name === "plain GD") {
      x -= 0.035 * gx; y -= 0.035 * gy;
    } else if (name === "momentum") {
      vx = 0.7 * vx + gx; vy = 0.7 * vy + gy;            // a rolling average of past gradients
      x -= 0.03 * vx; y -= 0.03 * vy;
    } else {                                             // Adam
      mx = 0.9 * mx + 0.1 * gx; my = 0.9 * my + 0.1 * gy;
      sx = 0.999 * sx + 0.001 * gx * gx; sy = 0.999 * sy + 0.001 * gy * gy;
      const c1 = 1 - 0.9 ** t, c2 = 1 - 0.999 ** t;
      x -= 0.5 * (mx / c1) / (Math.sqrt(sx / c2) + 1e-8);
      y -= 0.5 * (my / c1) / (Math.sqrt(sy / c2) + 1e-8);
    }
  }
  return [x, y, 0.5 * x * x + 25 * y * y];
}

for (const name of ["plain GD", "momentum", "Adam"]) {
  const [x, y, f] = run(name);
  console.log(`${name.padEnd(9)}: after 40 steps at (${x.toFixed(3)}, ${y.toFixed(3)}), loss = ${f.toFixed(5)}`);
}
''', ts=r'''
function grad(x: number, y: number): [number, number] {   // f = 0.5x^2 + 25y^2, a long narrow valley
  return [x, 50 * y];
}

function run(name: string, steps: number = 40): [number, number, number] {
  let x = -4, y = 1, vx = 0, vy = 0, mx = 0, my = 0, sx = 0, sy = 0;
  for (let t = 1; t <= steps; t++) {
    const [gx, gy] = grad(x, y);
    if (name === "plain GD") {
      x -= 0.035 * gx; y -= 0.035 * gy;
    } else if (name === "momentum") {
      vx = 0.7 * vx + gx; vy = 0.7 * vy + gy;            // a rolling average of past gradients
      x -= 0.03 * vx; y -= 0.03 * vy;
    } else {                                             // Adam
      mx = 0.9 * mx + 0.1 * gx; my = 0.9 * my + 0.1 * gy;
      sx = 0.999 * sx + 0.001 * gx * gx; sy = 0.999 * sy + 0.001 * gy * gy;
      const c1: number = 1 - 0.9 ** t, c2: number = 1 - 0.999 ** t;
      x -= 0.5 * (mx / c1) / (Math.sqrt(sx / c2) + 1e-8);
      y -= 0.5 * (my / c1) / (Math.sqrt(sy / c2) + 1e-8);
    }
  }
  return [x, y, 0.5 * x * x + 25 * y * y];
}

for (const name of ["plain GD", "momentum", "Adam"]) {
  const [x, y, f] = run(name);
  console.log(`${name.padEnd(9)}: after 40 steps at (${x.toFixed(3)}, ${y.toFixed(3)}), loss = ${f.toFixed(5)}`);
}
''', java=r'''
public class Optimisers {
    static double[] run(String name, int steps) {
        double x = -4, y = 1, vx = 0, vy = 0, mx = 0, my = 0, sx = 0, sy = 0;
        for (int t = 1; t <= steps; t++) {
            double gx = x, gy = 50 * y;                    // f = 0.5x^2 + 25y^2, a long narrow valley
            if (name.equals("plain GD")) {
                x -= 0.035 * gx; y -= 0.035 * gy;
            } else if (name.equals("momentum")) {
                vx = 0.7 * vx + gx; vy = 0.7 * vy + gy;    // a rolling average of past gradients
                x -= 0.03 * vx; y -= 0.03 * vy;
            } else {                                       // Adam
                mx = 0.9 * mx + 0.1 * gx; my = 0.9 * my + 0.1 * gy;
                sx = 0.999 * sx + 0.001 * gx * gx; sy = 0.999 * sy + 0.001 * gy * gy;
                double c1 = 1 - Math.pow(0.9, t), c2 = 1 - Math.pow(0.999, t);
                x -= 0.5 * (mx / c1) / (Math.sqrt(sx / c2) + 1e-8);
                y -= 0.5 * (my / c1) / (Math.sqrt(sy / c2) + 1e-8);
            }
        }
        return new double[]{x, y, 0.5 * x * x + 25 * y * y};
    }

    public static void main(String[] args) {
        String[] names = {"plain GD", "momentum", "Adam"};
        for (String name : names) {
            double[] r = run(name, 40);
            System.out.println(String.format("%-9s: after 40 steps at (%.3f, %.3f), loss = %.5f", name, r[0], r[1], r[2]));
        }
    }
}
''')

K.code('schedule', py=r'''
import math

lr_max, warmup, total = 0.1, 10, 100


def lr_at(step):
    if step < warmup:                     # warm up: grow slowly from 0
        return lr_max * step / warmup
    p = (step - warmup) / (total - warmup)          # 0 at the end of warm up, 1 at the end
    return lr_max * 0.5 * (1 + math.cos(math.pi * p))   # cosine decay down to 0


for step in [0, 5, 10, 30, 55, 80, 100]:
    print(f"step {step:3}: lr = {lr_at(step):.4f}")
''', js=r'''
const lrMax = 0.1, warmup = 10, total = 100;

function lrAt(step) {
  if (step < warmup) {                    // warm up: grow slowly from 0
    return lrMax * step / warmup;
  }
  const p = (step - warmup) / (total - warmup);       // 0 at the end of warm up, 1 at the end
  return lrMax * 0.5 * (1 + Math.cos(Math.PI * p));   // cosine decay down to 0
}

for (const step of [0, 5, 10, 30, 55, 80, 100]) {
  console.log(`step ${String(step).padStart(3)}: lr = ${lrAt(step).toFixed(4)}`);
}
''', ts=r'''
const lrMax: number = 0.1, warmup: number = 10, total: number = 100;

function lrAt(step: number): number {
  if (step < warmup) {                    // warm up: grow slowly from 0
    return lrMax * step / warmup;
  }
  const p: number = (step - warmup) / (total - warmup);   // 0 at the end of warm up, 1 at the end
  return lrMax * 0.5 * (1 + Math.cos(Math.PI * p));       // cosine decay down to 0
}

for (const step of [0, 5, 10, 30, 55, 80, 100]) {
  console.log(`step ${String(step).padStart(3)}: lr = ${lrAt(step).toFixed(4)}`);
}
''', java=r'''
public class Schedule {
    static double lrMax = 0.1;
    static int warmup = 10, total = 100;

    static double lrAt(int step) {
        if (step < warmup) {                  // warm up: grow slowly from 0
            return lrMax * step / warmup;
        }
        double p = (double) (step - warmup) / (total - warmup);   // 0 at the end of warm up, 1 at the end
        return lrMax * 0.5 * (1 + Math.cos(Math.PI * p));         // cosine decay down to 0
    }

    public static void main(String[] args) {
        int[] steps = {0, 5, 10, 30, 55, 80, 100};
        for (int step : steps) {
            System.out.println(String.format("step %3d: lr = %.4f", step, lrAt(step)));
        }
    }
}
''')

K.code('p_mean', py=r'''
data = [2, 4, 9]


def grad(m):                              # loss = average of (x - m)^2
    return sum(2 * (m - x) for x in data) / len(data)


m, lr = 0.0, 0.25
for step in range(1, 7):
    m = m - lr * grad(m)
    print(f"step {step}: m = {m:.4f}")
print("the mean of the data is", sum(data) / len(data))
''', js=r'''
const data = [2, 4, 9];

function grad(m) {                        // loss = average of (x - m)^2
  return data.reduce((s, x) => s + 2 * (m - x), 0) / data.length;
}

let m = 0.0;
const lr = 0.25;
for (let step = 1; step <= 6; step++) {
  m = m - lr * grad(m);
  console.log(`step ${step}: m = ${m.toFixed(4)}`);
}
console.log("the mean of the data is", (data.reduce((s, x) => s + x, 0) / data.length).toFixed(1));
''', ts=r'''
const data: number[] = [2, 4, 9];

function grad(m: number): number {       // loss = average of (x - m)^2
  return data.reduce((s, x) => s + 2 * (m - x), 0) / data.length;
}

let m: number = 0.0;
const lr: number = 0.25;
for (let step = 1; step <= 6; step++) {
  m = m - lr * grad(m);
  console.log(`step ${step}: m = ${m.toFixed(4)}`);
}
console.log("the mean of the data is", (data.reduce((s, x) => s + x, 0) / data.length).toFixed(1));
''', java=r'''
public class PracticeMean {
    static int[] data = {2, 4, 9};

    static double grad(double m) {            // loss = average of (x - m)^2
        double s = 0;
        for (int x : data) s += 2 * (m - x);
        return s / data.length;
    }

    public static void main(String[] args) {
        double m = 0.0, lr = 0.25;
        for (int step = 1; step <= 6; step++) {
            m = m - lr * grad(m);
            System.out.println(String.format("step %d: m = %.4f", step, m));
        }
        System.out.println("the mean of the data is " + (2 + 4 + 9) / 3.0);
    }
}
''')

K.code('p_lr_sweep', py=r'''
# loss = w^2, gradient = 2w, so each step multiplies w by (1 - 2 * lr)
for lr in [0.1, 0.5, 0.9, 1.1]:
    w = 1.0
    for _ in range(6):
        w = w - lr * 2 * w
    factor = 1 - 2 * lr
    verdict = "converges" if abs(factor) < 1 else "diverges"
    print(f"lr = {lr}: factor = {factor:+.1f}, w after 6 steps = {w:+.4f}, {verdict}")
''', js=r'''
// loss = w^2, gradient = 2w, so each step multiplies w by (1 - 2 * lr)
const sign = (v, d) => (v >= 0 ? "+" : "-") + Math.abs(v).toFixed(d);
for (const lr of [0.1, 0.5, 0.9, 1.1]) {
  let w = 1.0;
  for (let k = 0; k < 6; k++) {
    w = w - lr * 2 * w;
  }
  const factor = 1 - 2 * lr;
  const verdict = Math.abs(factor) < 1 ? "converges" : "diverges";
  console.log(`lr = ${lr}: factor = ${sign(factor, 1)}, w after 6 steps = ${sign(w, 4)}, ${verdict}`);
}
''', ts=r'''
// loss = w^2, gradient = 2w, so each step multiplies w by (1 - 2 * lr)
const sign = (v: number, d: number): string => (v >= 0 ? "+" : "-") + Math.abs(v).toFixed(d);
for (const lr of [0.1, 0.5, 0.9, 1.1]) {
  let w: number = 1.0;
  for (let k = 0; k < 6; k++) {
    w = w - lr * 2 * w;
  }
  const factor: number = 1 - 2 * lr;
  const verdict: string = Math.abs(factor) < 1 ? "converges" : "diverges";
  console.log(`lr = ${lr}: factor = ${sign(factor, 1)}, w after 6 steps = ${sign(w, 4)}, ${verdict}`);
}
''', java=r'''
public class PracticeLrSweep {
    public static void main(String[] args) {
        // loss = w^2, gradient = 2w, so each step multiplies w by (1 - 2 * lr)
        double[] lrs = {0.1, 0.5, 0.9, 1.1};
        for (double lr : lrs) {
            double w = 1.0;
            for (int k = 0; k < 6; k++) {
                w = w - lr * 2 * w;
            }
            double factor = 1 - 2 * lr;
            String verdict = Math.abs(factor) < 1 ? "converges" : "diverges";
            System.out.println(String.format("lr = %s: factor = %+.1f, w after 6 steps = %+.4f, %s", lr, factor, w, verdict));
        }
    }
}
''')

K.code('p_lagrange', py=r'''
# fence a rectangle against a wall: x + 2y = 40 metres of fence, area = x * y
best = (0, 0, 0)
for y in range(1, 20):                    # try every whole number depth
    x = 40 - 2 * y
    if x * y > best[2]:
        best = (x, y, x * y)
print(f"by trying: x = {best[0]}, y = {best[1]}, area = {best[2]}")
# Lagrange: grad(area) = lam * grad(fence) gives y = lam and x = 2 lam
lam = 40 / 4                              # put x = 2 lam, y = lam into x + 2y = 40
print(f"Lagrange: lam = {lam}, x = {2 * lam}, y = {lam}, area = {2 * lam * lam}")
more = 41 / 2 * 41 / 4                    # same rule with 41 metres of fence
print(f"with 41 m of fence the area is {more:.3f}, about lam = {lam} more")
''', js=r'''
// fence a rectangle against a wall: x + 2y = 40 metres of fence, area = x * y
let best = [0, 0, 0];
for (let y = 1; y < 20; y++) {            // try every whole number depth
  const x = 40 - 2 * y;
  if (x * y > best[2]) {
    best = [x, y, x * y];
  }
}
console.log(`by trying: x = ${best[0]}, y = ${best[1]}, area = ${best[2]}`);
// Lagrange: grad(area) = lam * grad(fence) gives y = lam and x = 2 lam
const lam = 40 / 4;                       // put x = 2 lam, y = lam into x + 2y = 40
console.log(`Lagrange: lam = ${lam.toFixed(1)}, x = ${(2 * lam).toFixed(1)}, y = ${lam.toFixed(1)}, area = ${(2 * lam * lam).toFixed(1)}`);
const more = 41 / 2 * 41 / 4;             // same rule with 41 metres of fence
console.log(`with 41 m of fence the area is ${more.toFixed(3)}, about lam = ${lam.toFixed(1)} more`);
''', ts=r'''
// fence a rectangle against a wall: x + 2y = 40 metres of fence, area = x * y
let best: number[] = [0, 0, 0];
for (let y = 1; y < 20; y++) {            // try every whole number depth
  const x: number = 40 - 2 * y;
  if (x * y > best[2]) {
    best = [x, y, x * y];
  }
}
console.log(`by trying: x = ${best[0]}, y = ${best[1]}, area = ${best[2]}`);
// Lagrange: grad(area) = lam * grad(fence) gives y = lam and x = 2 lam
const lam: number = 40 / 4;               // put x = 2 lam, y = lam into x + 2y = 40
console.log(`Lagrange: lam = ${lam.toFixed(1)}, x = ${(2 * lam).toFixed(1)}, y = ${lam.toFixed(1)}, area = ${(2 * lam * lam).toFixed(1)}`);
const more: number = 41 / 2 * 41 / 4;     // same rule with 41 metres of fence
console.log(`with 41 m of fence the area is ${more.toFixed(3)}, about lam = ${lam.toFixed(1)} more`);
''', java=r'''
public class PracticeLagrange {
    public static void main(String[] args) {
        // fence a rectangle against a wall: x + 2y = 40 metres of fence, area = x * y
        int[] best = {0, 0, 0};
        for (int y = 1; y < 20; y++) {        // try every whole number depth
            int x = 40 - 2 * y;
            if (x * y > best[2]) {
                best = new int[]{x, y, x * y};
            }
        }
        System.out.println("by trying: x = " + best[0] + ", y = " + best[1] + ", area = " + best[2]);
        // Lagrange: grad(area) = lam * grad(fence) gives y = lam and x = 2 lam
        double lam = 40 / 4.0;                // put x = 2 lam, y = lam into x + 2y = 40
        System.out.println(String.format("Lagrange: lam = %.1f, x = %.1f, y = %.1f, area = %.1f", lam, 2 * lam, lam, 2 * lam * lam));
        double more = 41 / 2.0 * 41 / 4.0;    // same rule with 41 metres of fence
        System.out.println(String.format("with 41 m of fence the area is %.3f, about lam = %.1f more", more, lam));
    }
}
''')

K.code('p_adam', py=r'''
import math

w, lr = 1.0, 0.1                          # minimise w^2, gradient 2w
m = v = 0.0
for t in range(1, 4):
    g = 2 * w
    m = 0.9 * m + 0.1 * g                 # average of gradients (momentum)
    v = 0.999 * v + 0.001 * g * g         # average of squared gradients (size)
    m_hat = m / (1 - 0.9 ** t)            # fix the start up bias
    v_hat = v / (1 - 0.999 ** t)
    w = w - lr * m_hat / (math.sqrt(v_hat) + 1e-8)
    print(f"t = {t}: g = {g:.4f}, m_hat = {m_hat:.4f}, sqrt(v_hat) = {math.sqrt(v_hat):.4f}, w = {w:.4f}")
''', js=r'''
let w = 1.0;                              // minimise w^2, gradient 2w
const lr = 0.1;
let m = 0, v = 0;
for (let t = 1; t <= 3; t++) {
  const g = 2 * w;
  m = 0.9 * m + 0.1 * g;                  // average of gradients (momentum)
  v = 0.999 * v + 0.001 * g * g;          // average of squared gradients (size)
  const mHat = m / (1 - 0.9 ** t);        // fix the start up bias
  const vHat = v / (1 - 0.999 ** t);
  w = w - lr * mHat / (Math.sqrt(vHat) + 1e-8);
  console.log(`t = ${t}: g = ${g.toFixed(4)}, m_hat = ${mHat.toFixed(4)}, sqrt(v_hat) = ${Math.sqrt(vHat).toFixed(4)}, w = ${w.toFixed(4)}`);
}
''', ts=r'''
let w: number = 1.0;                      // minimise w^2, gradient 2w
const lr: number = 0.1;
let m: number = 0, v: number = 0;
for (let t = 1; t <= 3; t++) {
  const g: number = 2 * w;
  m = 0.9 * m + 0.1 * g;                  // average of gradients (momentum)
  v = 0.999 * v + 0.001 * g * g;          // average of squared gradients (size)
  const mHat: number = m / (1 - 0.9 ** t);   // fix the start up bias
  const vHat: number = v / (1 - 0.999 ** t);
  w = w - lr * mHat / (Math.sqrt(vHat) + 1e-8);
  console.log(`t = ${t}: g = ${g.toFixed(4)}, m_hat = ${mHat.toFixed(4)}, sqrt(v_hat) = ${Math.sqrt(vHat).toFixed(4)}, w = ${w.toFixed(4)}`);
}
''', java=r'''
public class PracticeAdam {
    public static void main(String[] args) {
        double w = 1.0, lr = 0.1;                 // minimise w^2, gradient 2w
        double m = 0, v = 0;
        for (int t = 1; t <= 3; t++) {
            double g = 2 * w;
            m = 0.9 * m + 0.1 * g;                // average of gradients (momentum)
            v = 0.999 * v + 0.001 * g * g;        // average of squared gradients (size)
            double mHat = m / (1 - Math.pow(0.9, t));   // fix the start up bias
            double vHat = v / (1 - Math.pow(0.999, t));
            w = w - lr * mHat / (Math.sqrt(vHat) + 1e-8);
            System.out.println(String.format("t = %d: g = %.4f, m_hat = %.4f, sqrt(v_hat) = %.4f, w = %.4f", t, g, mHat, Math.sqrt(vHat), w));
        }
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('idea', '⛷️', 'Gradient descent: walk downhill', f'''
<p>Training a model means finding the weights that make the loss as small as possible. <b>Gradient descent</b> does it the way a skier finds the bottom of a valley in fog: feel the slope under your feet, take a small step downhill, and repeat.</p>
{fx('The gradient descent update', 'w ← w − η ∇L(w)', 'w are the weights, ∇L is the gradient of the loss (Chapter 7) and η (eta) is the learning rate, the size of each step.')}
{viz('gd1d')}
{worked('Three steps on L(w) = w² − 4w + 5, starting at w = 0 with η = 0.1', [
        'Slope: <span class="eq">L′(w) = 2w − 4</span>. At w = 0 the slope is −4, so the bowl goes down to the right.',
        'Step 1: <span class="eq">w = 0 − 0.1 × (−4) = 0.4</span>',
        'Step 2: slope <span class="eq">2 × 0.4 − 4 = −3.2</span>, so <span class="eq">w = 0.4 + 0.32 = 0.72</span>',
        'Step 3: slope <span class="eq">2 × 0.72 − 4 = −2.56</span>, so <span class="eq">w = 0.72 + 0.256 = 0.976</span>',
        'The steps shrink as the slope flattens, and w heads for the bottom at w = 2.'])}
{code('gd_basic', 'Five steps of gradient descent')}
{trick('Gradient descent never needs to see the whole landscape. Like a ball rolling downhill, it only needs the slope where it is standing right now.')}
''', kw=['gradient descent', 'update rule', 'learning rate', 'eta', 'minimise loss', 'downhill']),

    part('lr', '🎛️', 'The learning rate: not too small, not too big', f'''
<p>The learning rate is the most important setting in training. Too small and training crawls. Too big and every step overshoots the valley floor, bouncing from side to side or flying off completely.</p>
{table(['Learning rate', 'What happens', 'Loss curve'], [
        ['far too small', 'tiny steps, training takes forever', 'falls very slowly'],
        ['about right', 'big steps at first, smaller near the bottom', 'falls fast, then flattens'],
        ['a bit too big', 'overshoots, zig zags across the valley', 'falls with wobbles'],
        ['far too big', 'every step lands higher than the last', 'shoots up, often to NaN'],
    ])}
{fx('Stability rule for a bowl L = ½ a w²', f'w ← (1 − ηa) w &nbsp;&nbsp; converges when 0 < η < {frac(2, "a")}', 'a is the curvature (second derivative). Steeper bowls need smaller steps. For many weights, a is the largest Hessian eigenvalue.')}
{code('p_lr_sweep', 'Four learning rates on the same bowl')}
<div class="tip">A common recipe: try learning rates spaced by factors of 10 (0.1, 0.01, 0.001), watch the loss for a few hundred steps, and keep the largest one that still falls smoothly. Adam usually starts at 0.001.</div>
{life('Adjusting a shower: turn the tap a tiny bit and you wait ages for the right temperature. Turn it a lot and you swing between freezing and scalding. A sensible turn gets you there in a couple of goes.')}
''', kw=['learning rate', 'step size', 'divergence', 'oscillation', 'convergence', 'stability', 'too large learning rate']),

    part('sgd', '🎲', 'Stochastic and mini batch gradient descent', f'''
<p>The true gradient averages over every training example. With a million examples, that is a million calculations for one step. <b>Stochastic gradient descent (SGD)</b> estimates the gradient from a small random sample instead, and takes many more, cheaper steps.</p>
{table(['Version', 'Examples per step', 'Pros', 'Cons'], [
        ['Batch GD', 'all n', 'exact gradient, smooth path', 'slow, needs all data in memory'],
        ['Stochastic GD', '1', 'very cheap steps, noise can escape bad spots', 'very noisy path'],
        ['Mini batch GD', 'typically 32 to 1024', 'fast on GPUs, mild noise', 'one more setting to choose'],
    ])}
{fxs(fx('Mini batch gradient', f'g = {frac(1, "B")} Σ<sub>i ∈ batch</sub> ∇Lᵢ(w)', 'An unbiased estimate of the full gradient. Its noise shrinks like 1/√B.'),
         fx('Epoch', f'updates per epoch = {frac("n", "B")}', 'One epoch is one full pass over the data. 50000 images with B = 100 gives 500 updates per epoch.'))}
{code('sgd', 'SGD learns y = 2x + 1 from five points')}
{ml('Shuffle the data every epoch. If the examples always come in the same order, for example all cats then all dogs, the weights get dragged back and forth and training suffers.')}
''', kw=['stochastic gradient descent', 'sgd', 'mini batch', 'batch size', 'epoch', 'shuffle', 'noise']),

    part('adam', '🚀', 'Momentum, RMSProp and Adam', f'''
<p>Plain gradient descent struggles in long narrow valleys. The steep walls make it zig zag while the gentle floor makes it crawl. Smarter optimisers fix this with two tricks: remember past directions (<b>momentum</b>), and give each weight its own step size (<b>adaptive learning rates</b>).</p>
{fxs(fx('Momentum', 'v ← β v + ∇L &nbsp;&nbsp; w ← w − η v', 'v is a running sum of gradients, like a heavy ball gathering speed. Zig zags cancel out, steady directions add up. β ≈ 0.9.'),
         fx('RMSProp', 's ← ρ s + (1 − ρ) g² &nbsp;&nbsp; w ← w − η g ÷ √s', 'Divide by the typical size of recent gradients, so steep directions get smaller steps and flat ones bigger.'),
         fx('Adam (momentum plus RMSProp)', 'm ← β₁m + (1 − β₁)g &nbsp; v ← β₂v + (1 − β₂)g² <br> w ← w − η m̂ ÷ (√v̂ + ε)', 'm̂ = m/(1 − β₁ᵗ) and v̂ = v/(1 − β₂ᵗ) fix the start up bias. Defaults: β₁ = 0.9, β₂ = 0.999, ε = 10⁻⁸.'))}
{viz('gd2d')}
{code('optimisers', 'Plain GD, momentum and Adam race through a narrow valley')}
{table(['Optimiser', 'Typical use'], [
        ['SGD with momentum', 'image models such as ResNets, often with the best final accuracy'],
        ['Adam', 'the default for most projects, quick to get working'],
        ['AdamW', 'Adam with weight decay done properly, standard for transformers and large language models'],
    ])}
{trick('The first Adam step always moves each weight by about η, whatever the size of the gradient, because m̂ ÷ √v̂ = g ÷ |g| = ±1 at t = 1.')}
''', kw=['momentum', 'rmsprop', 'adam', 'adamw', 'adaptive learning rate', 'narrow valley', 'zig zag', 'bias correction']),

    part('landscape', '🗺️', 'Convexity, local minima and saddles', f'''
<p>For a <b>convex</b> loss there is one valley, so gradient descent with a sensible learning rate always reaches the best answer. Linear regression, logistic regression and SVMs have convex losses. Neural networks do not: their landscapes have many valleys, plateaus and saddles.</p>
{table(['Feature', 'What it is', 'How training copes'], [
        ['Global minimum', 'the lowest point of all', 'the ideal, rarely guaranteed for neural networks'],
        ['Local minimum', 'a valley that is not the lowest', 'in big networks most are nearly as good as the global one'],
        ['Saddle point', 'flat, but downhill in some directions', 'noise from SGD and momentum push the weights off'],
        ['Plateau', 'a wide nearly flat region', 'Adam helps by enlarging tiny gradients'],
        ['Cliff', 'a sudden very steep wall', 'gradient clipping caps the step size'],
    ])}
{fx('Condition number of the loss', 'κ = λmax ÷ λmin of the Hessian', 'Large κ means a long narrow valley. Plain gradient descent needs roughly κ steps to make progress, which is why feature scaling and adaptive optimisers matter.')}
{worked('Why feature scaling speeds up training', [
        'House area in square feet (around 1000) and number of rooms (around 3) feed the same linear model.',
        'The loss curvature along each weight grows with the square of its feature size: roughly <span class="eq">1000² = 1000000</span> versus <span class="eq">3² = 9</span>',
        'Condition number: about <span class="eq">1000000 ÷ 9 ≈ 110000</span>. A very long narrow valley.',
        'After standardising both features to mean 0 and standard deviation 1, both curvatures are about 1 and <span class="eq">κ ≈ 1</span>: a round bowl that gradient descent crosses in a few steps.'])}
{ml('Good starting weights matter in non convex problems. Schemes like Xavier and He initialisation pick random starting values scaled so that signals neither explode nor vanish through the layers.')}
''', kw=['convex', 'non convex', 'local minimum', 'global minimum', 'saddle point', 'plateau', 'condition number', 'feature scaling', 'initialisation']),

    part('lagrange', '🔒', 'Optimising with constraints: Lagrange multipliers', f'''
<p>Sometimes the answer must obey a rule: a fixed budget, a fixed length of fence, probabilities that add to 1. At the best point on the constraint, you cannot do better by sliding along it, which happens exactly when the contour of the goal just touches the constraint. There, the two gradients are parallel.</p>
{fx('Lagrange condition', '∇f = λ ∇g &nbsp;&nbsp; together with &nbsp;&nbsp; g(x) = c', 'f is what you optimise, g(x) = c is the rule. The multiplier λ tells how much the best value of f improves per extra unit of c.')}
{viz('lagrange')}
{worked('Largest area xy with x + y = 10', [
        'Goal f = xy, rule g = x + y = 10',
        'Gradients: <span class="eq">∇f = [y, x]</span> and <span class="eq">∇g = [1, 1]</span>',
        'Lagrange: <span class="eq">y = λ</span> and <span class="eq">x = λ</span>, so <span class="eq">x = y</span>',
        'Put into the rule: <span class="eq">2x = 10, x = y = 5</span>. Area <span class="eq">5 × 5 = 25</span>',
        'λ = 5: with 11 instead of 10, the best area is 5.5² = 30.25, about 5 more, as λ predicts.'])}
{code('p_lagrange', 'A fence against a wall, by trying and by Lagrange')}
{ml('Support vector machines are found with Lagrange multipliers, and the training points with non zero multipliers are the "support vectors". L2 regularisation is the same as asking the weights to stay inside a ball, ‖w‖ ≤ r, and the regularisation strength plays the part of λ.')}
''', kw=['lagrange multiplier', 'constrained optimisation', 'constraint', 'parallel gradients', 'svm', 'regularisation as constraint']),

    part('practice', '🛠️', 'Training tricks: schedules, clipping and stopping', f'''
<p>Real training runs add a few simple tools around the optimiser.</p>
{table(['Tool', 'What it does', 'Why'], [
        ['Learning rate warm up', 'start with a tiny learning rate and grow it over the first steps', 'early gradients are wild while the Adam averages are still empty'],
        ['Step or cosine decay', 'lower the learning rate as training goes on', 'big steps to explore, small steps to settle into the valley'],
        ['Gradient clipping', 'if ‖g‖ > c, scale g down to length c', 'stops one huge gradient from wrecking the weights'],
        ['Early stopping', 'stop when the validation loss stops improving', 'prevents overfitting and saves time'],
        ['Weight decay', 'shrink every weight a little each step: w ← w − ηλw', 'the L2 regularisation of Chapter 12'],
    ])}
{fxs(fx('Cosine decay', f'η(t) = η<sub>max</sub> × ½ (1 + cos(π t ÷ T))', 'Starts at the maximum and glides smoothly to 0 at step T.'),
         fx('Gradient clipping by norm', f'g ← g × min(1, {frac("c", "‖g‖")})', 'Keeps the direction, caps the length at c.'))}
{code('schedule', 'Warm up followed by cosine decay')}
{trick('If the loss suddenly becomes NaN, the usual suspects are a learning rate that is too big, a missing gradient clip, or a log of zero somewhere in the loss.')}
''', kw=['learning rate schedule', 'warm up', 'cosine decay', 'gradient clipping', 'early stopping', 'weight decay', 'NaN loss']),
]

INFO = {
    'title': 'Optimisation is walking downhill wisely',
    'panels': [
        {'s': [['e', '⛷️'], ['t', 'w ← w − η∇L', {'b': 1}]], 'h': 'Gradient descent', 't': 'Step against the slope.', 'more': 'Repeat until the slope is about zero.'},
        {'s': [['e', '🎛️'], ['t', '0 < η < 2/a', {'b': 1}]], 'h': 'Learning rate', 't': 'Not too small, not too big.', 'more': 'Too big and the loss explodes.'},
        {'s': [['e', '🚀'], ['t', 'Adam = momentum + RMSProp', {'b': 1}]], 'h': 'Optimisers', 't': 'Remember direction, adapt size.', 'more': 'Adam is the usual default.'},
        {'s': [['e', '🔒'], ['t', '∇f = λ∇g', {'b': 1}]], 'h': 'Constraints', 't': 'Gradients line up at the best point.', 'more': 'λ is the price of the constraint.'},
    ],
    'remember': 'Gradient descent updates w ← w − η∇L. The learning rate must be below about 2 divided by the curvature, or training diverges. Mini batches make each step cheap. Momentum and Adam handle narrow valleys. Convex losses have one valley, neural networks have many plus saddles. With a constraint, the best point has ∇f = λ∇g.',
}

REAL = [
    ['🗺️', 'Delivery routes', 'Logistics companies tune route and timing choices by optimisation, often with constraints such as van capacity and driver hours.'],
    ['💰', 'Investment portfolios', 'Portfolio theory picks the mix of investments with the least risk for a target return. The budget constraint is handled with a Lagrange multiplier.'],
    ['🧠', 'Large language models', 'Models with billions of weights are trained with AdamW, a warm up and cosine decay schedule, and gradient clipping.'],
]

K.say('top', 'Welcome',
      'Training a model means finding the weights with the smallest loss. Gradient descent walks downhill one step at a time. In this chapter you will tune the learning rate, see why mini batches work, race plain gradient descent against momentum and Adam, and solve problems with constraints.',
      'Model को train करना मतलब सबसे कम loss वाले weights ढूँढना। Gradient descent एक एक कदम नीचे चलता है। इस अध्याय में learning rate, mini batches, momentum और Adam, और constraints वाले सवाल सीखेंगे।',
      'Model train ಮಾಡುವುದು ಎಂದರೆ ಕಡಿಮೆ loss ನ weights ಹುಡುಕುವುದು. Gradient descent ಒಂದೊಂದು ಹೆಜ್ಜೆ ಕೆಳಗೆ ಹೋಗುತ್ತದೆ. Learning rate, mini batch, Adam ಮತ್ತು constraints ಈ ಅಧ್ಯಾಯದಲ್ಲಿ.',
      'Model train କରିବା ମାନେ ସବୁଠୁ କମ loss ର weights ଖୋଜିବା। Gradient descent ଗୋଟିଏ ଗୋଟିଏ ପାଦ ତଳକୁ ଯାଏ। Learning rate, mini batch, Adam ଓ constraints ଏହି ଅଧ୍ୟାୟରେ।',
      'تدريب النموذج يعني إيجاد الأوزان ذات أقل خسارة. ينزل الانحدار التدرجي خطوة بخطوة. في هذا الفصل تضبط معدل التعلم، وترى لماذا تنجح الدفعات الصغيرة، وتقارن الانحدار البسيط بالزخم وآدم، وتحل مسائل بقيود.',
      'Ein Modell zu trainieren heißt, die Gewichte mit dem kleinsten Verlust zu finden. Gradientenabstieg geht Schritt für Schritt bergab. In diesem Kapitel stellst du die Lernrate ein, siehst, warum Mini Batches funktionieren, lässt einfachen Abstieg gegen Momentum und Adam antreten und löst Aufgaben mit Nebenbedingungen.')
K.say('idea', 'Gradient descent',
      'Feel the slope, take a small step downhill, and repeat. The new weight is the old weight minus the learning rate times the gradient. The steps shrink by themselves as the slope flattens near the bottom.',
      'Slope महसूस करें, नीचे की ओर छोटा कदम लें, और दोहराएँ। नया weight पुराना weight घटा learning rate गुणा gradient है। नीचे पहुँचते हुए कदम अपने आप छोटे होते हैं।',
      'Slope ಅನುಭವಿಸಿ, ಕೆಳಗೆ ಸಣ್ಣ ಹೆಜ್ಜೆ ಇಡಿ, ಪುನರಾವರ್ತಿಸಿ. ಹೊಸ weight ಹಳೆಯ weight ಕಳೆ learning rate ಗುಣಿಸು gradient.',
      'Slope ଅନୁଭବ କରି ତଳକୁ ଛୋଟ ପାଦ ପକାନ୍ତୁ, ପୁନରାବୃତ୍ତି କରନ୍ତୁ। ନୂଆ weight ପୁରୁଣା weight ବିୟୋଗ learning rate ଗୁଣନ gradient।',
      'تحسس الميل، وخذ خطوة صغيرة نزولًا، وكرر. الوزن الجديد هو القديم ناقص معدل التعلم في التدرج، والخطوات تصغر وحدها كلما استوى الميل قرب القاع.',
      'Spüre die Steigung, mache einen kleinen Schritt bergab und wiederhole. Das neue Gewicht ist das alte minus Lernrate mal Gradient. Die Schritte werden von selbst kleiner, wenn die Steigung unten flacher wird.')
K.say('lr', 'Learning rate',
      'A tiny learning rate crawls. A good one falls fast and settles. A big one zig zags, and a far too big one explodes. For a bowl with curvature a, the learning rate must stay below two divided by a.',
      'बहुत छोटा learning rate रेंगता है। अच्छा जल्दी गिरकर टिकता है। बड़ा zig zag करता है, और बहुत बड़ा फट जाता है। Curvature a वाले कटोरे के लिए learning rate दो बटा a से कम रहना चाहिए।',
      'ಚಿಕ್ಕ learning rate ನಿಧಾನ, ದೊಡ್ಡದು zig zag, ತುಂಬಾ ದೊಡ್ಡದು ಸ್ಫೋಟ. Learning rate ಎರಡು ಭಾಗಿಸು a ಗಿಂತ ಕಡಿಮೆ ಇರಬೇಕು.',
      'ଛୋଟ learning rate ଧୀର, ବଡ଼ zig zag, ବହୁତ ବଡ଼ ବିସ୍ଫୋରଣ। Learning rate ଦୁଇ ଭାଗ a ରୁ କମ ରହିବା ଦରକାର।',
      'معدل التعلم الصغير جدًا يزحف، والجيد ينزل بسرعة ويستقر، والكبير يتعرج، والكبير جدًا ينفجر. لوعاء انحناؤه a يجب أن يبقى المعدل أقل من اثنين على a.',
      'Eine winzige Lernrate kriecht, eine gute fällt schnell und kommt zur Ruhe, eine große springt hin und her, eine viel zu große explodiert. Für eine Schüssel mit Krümmung a muss die Lernrate unter zwei durch a bleiben.')
K.say('sgd', 'Mini batches',
      'Instead of averaging the gradient over every example, take a small random batch. Each step is cheaper and a little noisy, and the noise even helps escape flat spots. One full pass over the data is called an epoch.',
      'हर example पर gradient का औसत लेने के बजाय छोटा random batch लें। हर कदम सस्ता और थोड़ा noisy है, और noise समतल जगहों से निकलने में मदद करता है। Data का एक पूरा चक्कर epoch कहलाता है।',
      'ಪ್ರತಿ example ಬದಲಿಗೆ ಸಣ್ಣ random batch ತೆಗೆದುಕೊಳ್ಳಿ. ಪ್ರತಿ ಹೆಜ್ಜೆ ಅಗ್ಗ. Data ದ ಒಂದು ಪೂರ್ಣ ಸುತ್ತು epoch.',
      'ପ୍ରତ୍ୟେକ example ବଦଳରେ ଛୋଟ random batch ନିଅନ୍ତୁ। ପ୍ରତି ପାଦ ଶସ୍ତା। Data ର ଗୋଟିଏ ପୂର୍ଣ୍ଣ ଚକ୍କର epoch।',
      'بدل أخذ متوسط التدرج على كل الأمثلة، خذ دفعة عشوائية صغيرة. كل خطوة أرخص وفيها ضجيج قليل يساعد على الخروج من المناطق المستوية. والمرور الكامل على البيانات يسمى حقبة.',
      'Statt den Gradienten über alle Beispiele zu mitteln, nimm einen kleinen zufälligen Batch. Jeder Schritt ist billiger und etwas verrauscht, und das Rauschen hilft sogar aus flachen Stellen heraus. Ein voller Durchgang heißt Epoche.')
K.say('adam', 'Momentum and Adam',
      'Momentum keeps a running sum of gradients so zig zags cancel and steady directions speed up. RMSProp gives each weight its own step size. Adam combines both and is the usual default. Watch the three race through the narrow valley.',
      'Momentum gradients का चलता जोड़ रखता है, जिससे zig zag कटते हैं और स्थिर दिशाएँ तेज़ होती हैं। RMSProp हर weight को अपना step size देता है। Adam दोनों को जोड़ता है और आम default है।',
      'Momentum gradients ನ ಓಡುವ ಮೊತ್ತ ಇಡುತ್ತದೆ. RMSProp ಪ್ರತಿ weight ಗೆ ತನ್ನದೇ step size. Adam ಎರಡನ್ನೂ ಸೇರಿಸುತ್ತದೆ.',
      'Momentum gradients ର ଚାଲୁ ଯୋଗଫଳ ରଖେ। RMSProp ପ୍ରତ୍ୟେକ weight କୁ ନିଜ step size ଦିଏ। Adam ଦୁଇଟିକୁ ମିଶାଏ।',
      'الزخم يحتفظ بمجموع جارٍ للتدرجات فتلغي التعرجات بعضها وتتسارع الاتجاهات الثابتة. وآر إم إس بروب يعطي كل وزن حجم خطوة خاصًا. وآدم يجمع الاثنين وهو الخيار المعتاد.',
      'Momentum führt eine laufende Summe der Gradienten, so heben sich Zickzacks auf und stetige Richtungen werden schneller. RMSProp gibt jedem Gewicht seine eigene Schrittweite. Adam verbindet beides und ist der übliche Standard.')
K.say('landscape', 'Loss landscapes',
      'A convex loss has one valley, so training always finds the best answer. Neural networks have many valleys, saddles and plateaus. A large condition number means a long narrow valley, which feature scaling can turn into a round bowl.',
      'Convex loss में एक ही घाटी होती है। Neural networks में कई घाटियाँ, saddles और plateaus होते हैं। बड़ा condition number लंबी पतली घाटी है, जिसे feature scaling गोल कटोरा बना सकता है।',
      'Convex loss ಗೆ ಒಂದೇ ಕಣಿವೆ. Neural networks ಗೆ ಅನೇಕ ಕಣಿವೆ, saddles. Feature scaling ಕಿರಿದಾದ ಕಣಿವೆಯನ್ನು ದುಂಡಗಿನ ಬಟ್ಟಲು ಮಾಡುತ್ತದೆ.',
      'Convex loss ର ଗୋଟିଏ ଉପତ୍ୟକା। Neural networks ର ଅନେକ ଉପତ୍ୟକା ଓ saddles। Feature scaling ସରୁ ଉପତ୍ୟକାକୁ ଗୋଲ ବାଟି କରେ।',
      'الخسارة المحدبة لها وادٍ واحد فيجد التدريب أفضل إجابة دائمًا. أما الشبكات العصبية ففيها وديان كثيرة وسروج وهضاب. ورقم الحالة الكبير يعني واديًا طويلًا ضيقًا، يحوله توحيد المقاييس إلى وعاء مستدير.',
      'Ein konvexer Verlust hat ein Tal, also findet das Training immer die beste Lösung. Neuronale Netze haben viele Täler, Sättel und Plateaus. Eine große Konditionszahl bedeutet ein langes schmales Tal, das Merkmalsskalierung in eine runde Schüssel verwandeln kann.')
K.say('lagrange', 'Constraints',
      'When the answer must obey a rule, the best point is where the contour of the goal just touches the rule. There the two gradients are parallel: gradient of f equals lambda times gradient of g. Lambda is the value of loosening the rule by one unit.',
      'जब उत्तर को किसी नियम का पालन करना हो, तो सबसे अच्छा बिंदु वहाँ है जहाँ लक्ष्य की contour नियम को बस छूती है। वहाँ दोनों gradients समानांतर होते हैं। Lambda नियम को एक इकाई ढीला करने का मूल्य है।',
      'ಉತ್ತರ ನಿಯಮ ಪಾಲಿಸಬೇಕಾದಾಗ, ಉತ್ತಮ ಬಿಂದುವಿನಲ್ಲಿ ಎರಡು gradients ಸಮಾನಾಂತರ. Lambda ನಿಯಮ ಸಡಿಲಿಸುವ ಮೌಲ್ಯ.',
      'ଉତ୍ତର ନିୟମ ମାନିବାକୁ ପଡ଼ିଲେ, ଭଲ ବିନ୍ଦୁରେ ଦୁଇ gradients ସମାନ୍ତରାଳ। Lambda ନିୟମ ଢିଲା କରିବାର ମୂଲ୍ୟ।',
      'حين يجب أن يلتزم الحل بقاعدة، تكون أفضل نقطة حيث يلامس خط كنتور الهدف القاعدة بالكاد، وهناك يتوازى التدرجان. ولامدا هي قيمة تخفيف القاعدة بوحدة واحدة.',
      'Wenn die Lösung eine Regel einhalten muss, liegt der beste Punkt dort, wo die Höhenlinie des Ziels die Regel gerade berührt. Dort sind beide Gradienten parallel. Lambda ist der Wert, die Regel um eine Einheit zu lockern.')
K.say('practice', 'Training tricks and practice',
      'Real training adds warm up, a decaying learning rate, gradient clipping and early stopping. Then practise: find a mean with gradient descent, sweep learning rates, fence a field with Lagrange, and run Adam by hand.',
      'असली training में warm up, घटता learning rate, gradient clipping और early stopping जुड़ते हैं। फिर अभ्यास: gradient descent से mean, learning rates की तुलना, Lagrange से खेत की बाड़, और हाथ से Adam।',
      'ನಿಜ training ನಲ್ಲಿ warm up, decay, clipping, early stopping. ನಂತರ ಅಭ್ಯಾಸ: mean, learning rates, Lagrange, Adam.',
      'ପ୍ରକୃତ training ରେ warm up, decay, clipping, early stopping। ତାପରେ ଅଭ୍ୟାସ: mean, learning rates, Lagrange, Adam।',
      'التدريب الحقيقي يضيف الإحماء ومعدل تعلم متناقصًا وقص التدرجات والإيقاف المبكر. ثم تدرب: جد متوسطًا بالانحدار، وقارن معدلات التعلم، وسيّج حقلًا بلاغرانج، وطبق آدم يدويًا.',
      'Echtes Training ergänzt Aufwärmen, eine sinkende Lernrate, Gradientenbegrenzung und frühes Stoppen. Dann übe: einen Mittelwert per Gradientenabstieg finden, Lernraten vergleichen, ein Feld mit Lagrange einzäunen und Adam von Hand rechnen.')

# ---------------------------------------------------------------- practice
K.practice('mean', 'e', 'Gradient descent finds the mean', 'p_mean',
           '<p>The loss L(m) = average of (x − m)² over the data [2, 4, 9] measures how far a single guess m is from the points. Run gradient descent from m = 0 with η = 0.25 for six steps.</p>',
           'step 1: m = 2.5000\nstep 2: m = 3.7500\nstep 3: m = 4.3750\nstep 4: m = 4.6875\nstep 5: m = 4.8438\nstep 6: m = 4.9219\nthe mean of the data is 5.0',
           'The gradient is the average of 2(m − x), which equals 2(m − mean).',
           '<p>The gradient simplifies to 2(m − 5), so each update is m ← m − 0.25 × 2(m − 5) = m − 0.5(m − 5). Each step closes half of the remaining gap to 5: 0 → 2.5 → 3.75 → 4.375 and so on. This shows a deep fact: the mean is exactly the value that minimises the squared error, which is why linear regression with squared error predicts averages.</p>',
           'O(steps · n)', 'O(1)')
K.practice('lr-sweep', 'm', 'Four learning rates on one bowl', 'p_lr_sweep',
           '<p>For the loss w² starting at w = 1, run 6 steps of gradient descent with η = 0.1, 0.5, 0.9 and 1.1. Explain each result with the factor 1 − 2η.</p>',
           'lr = 0.1: factor = +0.8, w after 6 steps = +0.2621, converges\nlr = 0.5: factor = +0.0, w after 6 steps = +0.0000, converges\nlr = 0.9: factor = -0.8, w after 6 steps = +0.2621, converges\nlr = 1.1: factor = -1.2, w after 6 steps = +2.9860, diverges',
           'Each step multiplies w by the same factor 1 − 2η.',
           '<p>The gradient is 2w, so w ← w − η × 2w = (1 − 2η)w. With η = 0.1 the factor 0.8 shrinks w steadily. With η = 0.5 it is 0, which jumps straight to the answer in one step. With η = 0.9 the factor −0.8 flips the sign every step (a zig zag) but still shrinks. With η = 1.1 the factor −1.2 grows every step and the loss explodes. The boundary is η = 1 = 2 ÷ curvature, since the curvature of w² is 2.</p>',
           'O(steps)', 'O(1)')
K.practice('lagrange', 'h', 'The biggest field against a wall', 'p_lagrange',
           '<p>A farmer has 40 m of fence to make a rectangle against a long wall, so only three sides need fence: x + 2y = 40. Find the largest area by trying values and by Lagrange multipliers, and interpret λ.</p>',
           'by trying: x = 20, y = 10, area = 200\nLagrange: lam = 10.0, x = 20.0, y = 10.0, area = 200.0\nwith 41 m of fence the area is 210.125, about lam = 10.0 more',
           '∇(xy) = [y, x] and ∇(x + 2y) = [1, 2].',
           '<p>Setting [y, x] = λ[1, 2] gives y = λ and x = 2λ. Putting these into the fence rule: 2λ + 2λ = 40, so λ = 10, x = 20 and y = 10. The area is 200 m². λ = 10 means each extra metre of fence buys about 10 m² more, which the 41 m check confirms (210.125). Economists call λ a "shadow price".</p>',
           'O(1)', 'O(1)')
K.practice('adam', 'x', 'Adam by hand', 'p_adam',
           '<p>Run three steps of Adam (η = 0.1, β₁ = 0.9, β₂ = 0.999) on the loss w² from w = 1. Show the bias corrected averages at each step.</p>',
           't = 1: g = 2.0000, m_hat = 2.0000, sqrt(v_hat) = 2.0000, w = 0.9000\nt = 2: g = 1.8000, m_hat = 1.8947, sqrt(v_hat) = 1.9026, w = 0.8004\nt = 3: g = 1.6008, m_hat = 1.7863, sqrt(v_hat) = 1.8075, w = 0.7016',
           'At t = 1, m̂ = g and √v̂ = |g|, so the first step has size η.',
           '<p>Step 1: m = 0.1 × 2 = 0.2 and m̂ = 0.2 ÷ (1 − 0.9) = 2. v = 0.001 × 4 = 0.004 and v̂ = 0.004 ÷ 0.001 = 4, so √v̂ = 2. The update is 0.1 × 2 ÷ 2 = 0.1, giving w = 0.9. Without the bias correction m would be only 0.2 and the step ten times too small. Each step is close to η because m̂ ÷ √v̂ stays near 1 while the gradient keeps the same sign.</p>',
           'O(steps)', 'O(1)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In w ← w − η∇L, what is η?', ['the loss', 'the learning rate', 'the gradient', 'the number of epochs'], 1, 'The step size.', 'η (eta) scales how far each step goes.')
K.quiz('e', 'Why does gradient descent subtract the gradient?', ['to go uphill', 'because the gradient points uphill, so minus it goes downhill', 'to make weights negative', 'it is a convention only'], 1, 'Chapter 7.', '∇L points to the steepest increase, so −∇L reduces the loss fastest.')
K.quiz('e', 'What is one epoch?', ['one update step', 'one full pass over the training data', 'one mini batch', 'one layer'], 1, 'All examples seen once.', 'An epoch is n ÷ B mini batch updates.')
K.quiz('e', 'The loss shoots up to NaN after a few steps. What is the most likely cause?', ['learning rate too small', 'learning rate too large', 'too much data', 'too few epochs'], 1, 'Overshooting.', 'Steps that are too big land higher each time until the numbers overflow.')
K.quiz('m', 'For L = 5w², what is the largest learning rate that still converges?', ['0.1', '0.2', '0.4', '2'], 1, 'Curvature a = 10, need η < 2/a.', 'L″ = 10, so η must stay below 2 ÷ 10 = 0.2.')
K.quiz('m', 'What does momentum mainly fix?', ['too much data', 'zig zagging in narrow valleys and slow progress along flat floors', 'overfitting', 'missing labels'], 1, 'A heavy ball.', 'Opposite zig zag gradients cancel while consistent ones add up.')
K.quiz('m', 'What do the two moving averages in Adam track?', ['loss and accuracy', 'the gradient and the squared gradient', 'weights and biases', 'train and test loss'], 1, 'Momentum and RMSProp.', 'm averages g, v averages g², and the step is m̂ ÷ √v̂.')
K.quiz('m', 'Compared with full batch GD, mini batch SGD…', ['always reaches a lower loss', 'takes cheaper, noisier steps', 'needs no learning rate', 'cannot run on GPUs'], 1, 'Estimate the gradient from a sample.', 'Each step uses B examples, so it is fast but approximate.')
K.quiz('m', 'At a constrained optimum found by Lagrange multipliers…', ['∇f = 0', '∇f is parallel to ∇g', '∇g = 0', 'f = g'], 1, 'The contour just touches the constraint.', '∇f = λ∇g.')
K.quiz('h', 'Why does standardising features speed up gradient descent?', ['it removes outliers', 'it makes the loss bowl rounder, lowering the condition number', 'it adds data', 'it changes the labels'], 1, 'Long narrow valley versus round bowl.', 'Similar feature scales give similar curvatures, so one learning rate suits every direction.')
K.quiz('h', 'Gradient g = [6, 8] is clipped to norm 5. What is the clipped gradient?', ['[5, 5]', '[3, 4]', '[6, 5]', '[0.6, 0.8]'], 1, '‖g‖ = 10.', 'Scale by 5 ÷ 10: [3, 4].')
K.quiz('h', 'What is the main purpose of learning rate warm up?', ['to use more memory', 'to avoid huge unstable steps at the very start of training', 'to stop training early', 'to shuffle the data'], 1, 'The Adam averages are empty at first.', 'Early gradients and optimiser statistics are unreliable, so start gently.')
K.quiz('h', 'Which loss is convex in its weights?', ['a deep neural network with ReLU', 'linear regression with mean squared error', 'a GAN', 'a transformer'], 1, 'One valley.', 'MSE for linear regression is a quadratic bowl in the weights.')
K.quiz('x', 'The first Adam update (t = 1) for any single weight has size about…', ['η × |g|', 'η', 'η²', '|g|'], 1, 'm̂ = g, √v̂ = |g|.', 'm̂ ÷ √v̂ = ±1, so the step is about η regardless of the gradient size.')
K.quiz('x', 'What does the Lagrange multiplier λ tell you?', ['the learning rate', 'how much the best objective changes per unit change of the constraint', 'the number of constraints', 'the gradient norm'], 1, 'Shadow price.', 'λ = d(best f) ÷ dc for the constraint g = c.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'w = 5, the gradient is 4 and η = 0.5. What is w after one step?', '3', 'w − η × gradient.', [
    'Step size: <span class="eq">η × gradient = 0.5 × 4 = 2</span>',
    'Subtract: <span class="eq">5 − 2 = 3</span>',
    'The gradient was positive, so w moved down.',
], check=3)
K.calc('e', 'L(w) = w². From w = 3 with η = 0.1, what is w after one step?', '2.4', 'The gradient of w² is 2w.', [
    'Gradient at 3: <span class="eq">2 × 3 = 6</span>',
    'Step: <span class="eq">0.1 × 6 = 0.6</span>',
    'New w: <span class="eq">3 − 0.6 = 2.4</span>',
], check=2.4)
K.calc('e', 'L(w) = (w − 3)². What is the gradient at w = 0?', '-6', 'Chain rule: 2(w − 3).', [
    'Derivative: <span class="eq">L′(w) = 2(w − 3)</span>',
    'At w = 0: <span class="eq">2 × (0 − 3) = −6</span>',
    'Negative, so gradient descent will increase w towards 3.',
], check=-6, alt=['−6'])
K.calc('e', 'A dataset has 10000 examples and the batch size is 100. How many updates are in one epoch?', '100', 'Updates = n ÷ B.', [
    'One epoch uses every example once.',
    'Each update uses 100 examples.',
    '<span class="eq">10000 ÷ 100 = 100</span> updates',
], check=100)
K.calc('m', 'Momentum with β = 0.9: v = 2, the new gradient is 4, w = 1 and η = 0.1. What is the new w?', '0.42', 'v ← βv + g, then w ← w − ηv.', [
    'New velocity: <span class="eq">v = 0.9 × 2 + 4 = 1.8 + 4 = 5.8</span>',
    'Step: <span class="eq">0.1 × 5.8 = 0.58</span>',
    'New w: <span class="eq">1 − 0.58 = 0.42</span>',
], check=0.42)
K.calc('m', 'For L = 5w², what is the largest learning rate for which gradient descent converges?', '0.2', 'Each step multiplies w by (1 − η × curvature).', [
    'Gradient: <span class="eq">10w</span>, so <span class="eq">w ← w − 10ηw = (1 − 10η)w</span>',
    'Convergence needs <span class="eq">|1 − 10η| < 1</span>, so <span class="eq">0 < η < 0.2</span>',
    'The boundary is <span class="eq">η = 0.2</span>, which is 2 ÷ curvature with curvature 10.',
], check=0.2)
K.calc('m', 'Maximise xy subject to x + y = 10. What is the largest value?', '25', '∇(xy) = λ∇(x + y).', [
    '<span class="eq">[y, x] = λ[1, 1]</span>, so <span class="eq">x = y</span>',
    'Rule: <span class="eq">x + x = 10</span>, so <span class="eq">x = y = 5</span>',
    'Value: <span class="eq">5 × 5 = 25</span>',
], check=25)
K.calc('m', 'L(w) = (w − 3)². Starting at w = 0 with η = 0.25, what is w after two steps?', '2.25', 'Gradient 2(w − 3).', [
    'Step 1: gradient <span class="eq">2(0 − 3) = −6</span>, so <span class="eq">w = 0 + 0.25 × 6 = 1.5</span>',
    'Step 2: gradient <span class="eq">2(1.5 − 3) = −3</span>, so <span class="eq">w = 1.5 + 0.25 × 3 = 2.25</span>',
    'Each step halves the distance to 3: 3 → 1.5 → 0.75 left.',
], check=2.25)
K.calc('h', 'Adam with η = 0.001. Roughly how big is the very first update to a weight whose gradient is 250?', '0.001', 'At t = 1, m̂ = g and √v̂ = |g|.', [
    'Bias corrected: <span class="eq">m̂ = 250</span>, <span class="eq">√v̂ = √(250²) = 250</span>',
    'Ratio: <span class="eq">250 ÷ 250 = 1</span>',
    'Step: <span class="eq">η × 1 = 0.001</span>, whatever the size of the gradient.',
], check=0.001)
K.calc('h', 'Cosine decay with η_max = 0.1 over T steps (no warm up). What is the learning rate halfway, at t = T/2?', '0.05', 'η = η_max × ½(1 + cos(π t ÷ T)).', [
    'Halfway: <span class="eq">π t ÷ T = π ÷ 2</span>',
    '<span class="eq">cos(π ÷ 2) = 0</span>',
    '<span class="eq">η = 0.1 × ½ × (1 + 0) = 0.05</span>',
], check=0.05)
K.calc('h', 'A loss has Hessian diag(2, 200). What is its condition number?', '100', 'κ = λmax ÷ λmin.', [
    'The Hessian is diagonal, so its eigenvalues are <span class="eq">2</span> and <span class="eq">200</span>',
    '<span class="eq">κ = 200 ÷ 2 = 100</span>',
    'A long narrow valley: the steep direction limits η to below 2 ÷ 200 = 0.01, so the flat direction crawls.',
], check=100)
K.calc('x', 'With L2 regularisation the loss is (w − 3)² + 0.5w². Which w minimises it?', '2', 'Set the derivative to zero.', [
    'Derivative: <span class="eq">2(w − 3) + 0.5 × 2w = 2w − 6 + w = 3w − 6</span>',
    'Set to zero: <span class="eq">3w − 6 = 0</span>',
    '<span class="eq">w = 2</span>. The penalty pulls the answer from 3 towards 0.',
], check=2)
K.calc('x', 'Clip the gradient g = [6, 8] to a maximum norm of 5. What is the first component?', '3', 'Scale g by 5 ÷ ‖g‖ when ‖g‖ > 5.', [
    'Norm: <span class="eq">‖g‖ = √(36 + 64) = 10</span>',
    'It is above 5, so scale by <span class="eq">5 ÷ 10 = 0.5</span>',
    'Clipped: <span class="eq">[3, 4]</span>. Same direction, length 5. First component 3.',
], check=3)

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;

  /* ----- one dimensional gradient descent with a learning rate slider ----- */
  W.gd1d = el => {
    const b = shell(el, 'Gradient descent on a curve', 'Choose a loss curve, a starting point and a learning rate. Press Play: each step draws the tangent, then jumps by −η × slope. Try a big learning rate to see it overshoot.');
    const FN = {
      bowl: { f: w => (w - 2) ** 2 + 1, d: w => 2 * (w - 2), xr: [-3, 7], yr: [0, 20], name: '(w − 2)² + 1' },
      bumpy: { f: w => 0.05 * w ** 4 - 0.6 * w * w + 0.4 * w + 3, d: w => 0.2 * w ** 3 - 1.2 * w + 0.4, xr: [-4, 4], yr: [0, 8], name: '0.05w⁴ − 0.6w² + 0.4w + 3' },
      flat: { f: w => Math.log(1 + Math.exp(-(w - 1))) * 2 + 0.05 * (w - 4) ** 2, d: w => -2 / (1 + Math.exp(w - 1)) + 0.1 * (w - 4), xr: [-4, 8], yr: [0, 12], name: 'plateau then valley' },
    };
    b.innerHTML = `<div class="vz-row">${seg('fn', [['bowl', 'Bowl'], ['bumpy', 'Two valleys'], ['flat', 'Plateau']], 'bowl')}</div>
      <div class="mv-wrap"><div class="g1-plot"></div><div class="mv-side">${slider('lr', 'η', 0.01, 1.1, 0.1, 0.01)}${slider('w0', 'start w', -3, 6, -2, 0.1)}<div class="mv-read g1-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let F = FN.bowl, lr = 0.1, w0 = -2, path = [];
    function plan() {
      path = [w0];
      for (let k = 0; k < 30; k++) { const w = path[path.length - 1], nw = w - lr * F.d(w); path.push(nw); if (!isFinite(nw) || Math.abs(nw) > 1e3) break; }
      P.load(path.length, 0);
    }
    function show(t) {
      const G = MV.frame(440, 330, F.xr, F.yr);
      let s = MV.axes(G, { xl: 'w', yl: 'loss' }) + MV.curve(G, F.f);
      const inR = w => w >= F.xr[0] && w <= F.xr[1];
      for (let k = 0; k < t; k++) {
        const a = path[k], c = path[k + 1];
        if (inR(a) && inR(c)) s += MV.line(G, a, F.f(a), c, F.f(c), 'mv-v o dash');
      }
      for (let k = 0; k <= t; k++) if (inR(path[k])) s += MV.dot(G, path[k], F.f(path[k]), k === t ? 'o big' : 'o', k === t ? 7 : 4);
      const w = path[t];
      if (inR(w)) { const m = F.d(w), fw = F.f(w); s += MV.curve(G, x => fw + m * (x - w), 'c4 thin', { from: w - 1.5, to: w + 1.5 }); }
      $('.g1-plot', b).innerHTML = MV.svg(G, s, 'Gradient descent steps on a loss curve');
      const m = F.d(w);
      const diverged = !isFinite(w) || Math.abs(w) > 50;
      $('.g1-out', b).innerHTML = `loss = ${F.name}<br>step ${t}<br>w = <b>${diverged ? 'flew off' : MV.num(w, 4)}</b><br>loss = ${diverged ? '∞' : MV.num(F.f(w), 4)}<br>slope = ${diverged ? '?' : MV.num(m, 3)}<br>next step = −η × slope = ${diverged ? '?' : MV.num(-lr * m, 3)}` +
        (diverged ? '<br>⚠️ Diverged: the learning rate is too big.' : Math.abs(m) < 0.01 ? '<br>✅ The slope is about 0: we are at the bottom of a valley.' : '');
    }
    const P = Player($('.vz-p', b), show, 650);
    wireSeg(b, 'fn', k => { F = FN[k]; plan(); });
    wireSlider(b, 'lr', v => { lr = v; plan(); });
    wireSlider(b, 'w0', v => { w0 = v; plan(); });
    plan();
  };

  /* ----- GD, momentum and Adam race on a two dimensional valley ----- */
  W.gd2d = el => {
    const b = shell(el, 'Optimiser race in a narrow valley', 'Three optimisers start from the same point on f = 0.5x² + 25y². Press Play to step them together. Change the learning rates and momentum to see who wins.');
    b.innerHTML = `<div class="mv-wrap"><div class="g2-plot"></div><div class="mv-side">${slider('lr', 'GD η', 0.005, 0.045, 0.035, 0.001)}${slider('beta', 'momentum β', 0, 0.95, 0.7, 0.05)}${slider('alr', 'Adam η', 0.05, 1, 0.5, 0.05)}<div class="mv-legend"><span><i class="r"></i>plain GD</span><span><i class="g"></i>momentum</span><span><i class="p"></i>Adam</span></div><div class="mv-read g2-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const f = (x, y) => 0.5 * x * x + 25 * y * y;
    let lr = 0.035, beta = 0.7, alr = 0.5, paths = [];
    const G = MV.frame(440, 300, [-5, 5], [-1.5, 1.5]);
    const contours = (() => { let s = ''; [0.5, 2, 4.5, 8, 12.5].forEach(c => { const pts = []; for (let k = 0; k <= 120; k++) { const t = k / 120 * 2 * Math.PI; pts.push(G.sx(Math.sqrt(2 * c) * Math.cos(t)).toFixed(1) + ',' + G.sy(Math.sqrt(c / 25) * Math.sin(t)).toFixed(1)); } s += `<polyline class="mv-cont" points="${pts.join(' ')}"/>`; }); return s; })();
    function plan() {
      const N = 40;
      const run = kind => {
        let x = -4, y = 1, vx = 0, vy = 0, mx = 0, my = 0, sx = 0, sy = 0; const p = [[x, y]];
        for (let t = 1; t <= N; t++) {
          const gx = x, gy = 50 * y;
          if (kind === 0) { x -= lr * gx; y -= lr * gy; }
          else if (kind === 1) { vx = beta * vx + gx; vy = beta * vy + gy; x -= 0.03 * vx; y -= 0.03 * vy; }
          else { mx = 0.9 * mx + 0.1 * gx; my = 0.9 * my + 0.1 * gy; sx = 0.999 * sx + 0.001 * gx * gx; sy = 0.999 * sy + 0.001 * gy * gy; const c1 = 1 - 0.9 ** t, c2 = 1 - 0.999 ** t; x -= alr * (mx / c1) / (Math.sqrt(sx / c2) + 1e-8); y -= alr * (my / c1) / (Math.sqrt(sy / c2) + 1e-8); }
          if (!isFinite(x) || Math.abs(x) > 1e6 || Math.abs(y) > 1e6) { x = NaN; y = NaN; }
          p.push([x, y]);
        }
        return p;
      };
      paths = [run(0), run(1), run(2)];
      P.load(N + 1, 0);
    }
    function show(t) {
      let s = MV.axes(G, { labels: false }) + contours + MV.dot(G, 0, 0, 'k', 4);
      const cls = ['r', 'g', 'p'], names = ['plain GD', 'momentum', 'Adam'];
      const clip = ([x, y]) => [Math.max(-5, Math.min(5, x)), Math.max(-1.5, Math.min(1.5, y))];
      paths.forEach((p, k) => {
        const vis = p.slice(0, t + 1).filter(q => isFinite(q[0])).map(clip);
        if (vis.length > 1) s += `<polyline class="mv-v ${cls[k]}" stroke-width="2" points="${vis.map(q => G.sx(q[0]).toFixed(1) + ',' + G.sy(q[1]).toFixed(1)).join(' ')}"/>`;
        const last = vis[vis.length - 1]; if (last) s += MV.dot(G, last[0], last[1], cls[k], 5);
      });
      $('.g2-plot', b).innerHTML = MV.svg(G, s, 'Three optimiser paths on a contour map');
      $('.g2-out', b).innerHTML = `step ${t}<br>` + paths.map((p, k) => { const q = p[t]; return `${names[k]}: loss ${isFinite(q[0]) ? '<b>' + MV.num(f(q[0], q[1]), 4) + '</b>' : '<b>diverged</b>'}`; }).join('<br>') +
        (lr > 0.04 ? '<br>⚠️ GD η is above 2 ÷ 50 = 0.04, so it will bounce out along y.' : '');
    }
    const P = Player($('.vz-p', b), show, 220);
    wireSlider(b, 'lr', v => { lr = v; plan(); });
    wireSlider(b, 'beta', v => { beta = v; plan(); });
    wireSlider(b, 'alr', v => { alr = v; plan(); });
    plan();
  };

  /* ----- Lagrange: slide along the constraint until the gradients line up ----- */
  W.lagrange = el => {
    const b = shell(el, 'Where the contour touches the constraint', 'Maximise f = xy on the line x + y = s. The thin purple curves are contours xy = 4, 9, 16, 25 and 36, and the orange one passes through the point. Slide the point along the line, or press Play to sweep it. The purple arrow is ∇f and the green arrow is ∇g. At the best point they line up.');
    b.innerHTML = `<div class="mv-wrap"><div class="lg-plot"></div><div class="mv-side">${slider('s', 'budget s', 4, 12, 10, 1)}${slider('p', 'x on the line', 0.5, 11.5, 2, 0.1)}<div class="mv-read lg-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let s = 10, x = 2;
    const G = MV.frame(400, 400, [0, 12], [0, 12]);
    function draw() {
      x = Math.max(0.2, Math.min(s - 0.2, x));
      $('[data-sl="p"]', b).value = x; $('[data-slv="p"]', b).textContent = MV.num(x);
      const y = s - x, fv = x * y;
      let h = MV.axes(G, { xstep: 2, ystep: 2, xl: 'x', yl: 'y' });
      [4, 9, 16, 25, 36].forEach(c => { h += MV.curve(G, t => c / t, 'thin c4', { from: c / 12, to: 12 }); });
      h += MV.curve(G, t => fv / t, 'c2', { from: fv / 12, to: 12 });
      h += MV.line(G, 0, s, s, 0, 'mv-v k');
      const g = [y, x], gn = Math.hypot(...g), k = 1.6 / gn;
      h += MV.arrow(G, x, y, x + g[0] * k, y + g[1] * k, 'p') + MV.arrow(G, x, y, x + 1.6 / Math.SQRT2, y + 1.6 / Math.SQRT2, 'g');
      h += MV.dot(G, x, y, 'o', 7);
      $('.lg-plot', b).innerHTML = MV.svg(G, h, 'Contours of xy and the constraint line');
      const cos = (g[0] + g[1]) / (gn * Math.SQRT2), ang = Math.acos(Math.min(1, cos)) * 180 / Math.PI;
      $('.lg-out', b).innerHTML = `point (${MV.num(x)}, ${MV.num(y)})<br>f = xy = <b>${MV.num(fv, 3)}</b><br>∇f = [${MV.num(y)}, ${MV.num(x)}], ∇g = [1, 1]<br>angle between them: ${MV.num(ang, 1)}°<br>` +
        (ang < 1.5 ? `✅ Parallel! ∇f = ${MV.num(x)} × ∇g, so λ = ${MV.num(x)}. Best f = ${MV.num(s * s / 4, 2)}.` : `Not parallel yet. Slide ${x < y ? 'right' : 'left'} to raise f. The best is x = y = ${MV.num(s / 2)}.`);
    }
    const P = Player($('.vz-p', b), t => { x = 0.3 + (s - 0.6) * t / 40; draw(); }, 140);
    wireSlider(b, 's', v => { s = v; draw(); });
    wireSlider(b, 'p', v => { P.pause(); x = v; draw(); });
    P.load(41, 0);
    x = 2; draw();
  };
})();
'''

# ---------------------------------------------------------------- deeper explanations and extra animations
# Each lesson above gives the short version. DEEPER adds a slower, fuller explanation (and sometimes an
# animation) to the end of the lesson with the same id.
DEEPER = {
    'idea': deep('when to stop, and why the steps shrink on their own', f'''
<p>Gradient descent is a loop, so it needs a rule for when to stop. Real training code uses one or more of these.</p>
{table(['Stopping rule', 'Check', 'Typical setting'], [
        ['fixed budget', 'stop after a set number of steps or epochs', '10 epochs, or 100000 steps'],
        ['small gradient', 'stop when ‖∇L‖ is tiny, since that means the ground is flat', '‖∇L‖ &lt; 10⁻⁶'],
        ['small improvement', 'stop when the loss barely changes between checks', 'less than 0.01% better'],
        ['early stopping', 'stop when the validation loss has not improved for a while', 'patience of 5 epochs'],
    ])}
<p>Notice that the learning rate η stays the same in the worked example, yet the steps get smaller. That happens because the step is η × slope, and the slope itself shrinks near the bottom of a smooth bowl. Gradient descent slows down by itself exactly where caution is needed.</p>
{fx('Progress per step on a smooth loss', 'L(w − η∇L) ≈ L(w) − η ‖∇L‖²', 'From the linear approximation of Chapter 7. As long as η is small enough, every step lowers the loss by roughly η times the squared gradient length.')}
{life('Parking a car: you drive at normal speed down the street, slow as you near the space, and creep the last few centimetres. Gradient descent follows the same pattern because its steps are proportional to how far the slope says you still have to go.')}
'''),
    'lr': deep('see the loss curves for each learning rate', f'''
<p>Engineers rarely look at the weights directly. They watch the <b>loss curve</b>, the loss plotted against the step number, and read the learning rate from its shape. Compare four learning rates on the same bowl below, then add your own.</p>
{viz('lrcurve')}
{table(['Shape of the loss curve', 'Diagnosis', 'Action'], [
        ['almost flat from the start', 'learning rate far too small', 'multiply η by 10'],
        ['smooth fast drop, then flat', 'about right', 'keep it'],
        ['drops, but saw tooth wobbles', 'a little too big', 'halve η, or add momentum'],
        ['rises, or jumps to NaN', 'far too big, diverging', 'divide η by 10, add gradient clipping'],
    ])}
<p>A popular trick for finding a good starting value is the <b>learning rate range test</b>: run a few hundred steps while raising η exponentially from 10⁻⁷ to 1, and plot the loss against η. Pick a value a little below the point where the loss falls fastest, well before it shoots up.</p>
'''),
    'sgd': deep('watch full batch, mini batch and single example paths', f'''
<p>All three methods head for the same valley, but they take very different routes. The animation fits y = w x + b to 40 noisy points. Each dot on the contour map is one update. Full batch gradient descent glides smoothly. Single example SGD stumbles around, because each step listens to only one point. Mini batches are in between.</p>
{viz('sgdpath')}
<p>Why is the noisy path still useful? Each SGD step costs 1 ÷ n of a full batch step, so in the time a full batch takes one careful step, SGD takes n quick ones. Early in training, when you are far from the valley, rough directions are good enough and speed wins. Near the bottom, the noise makes SGD jitter around the best point instead of landing on it, which is why the learning rate is usually lowered later in training.</p>
{fx('Noise in a mini batch gradient', f'spread ∝ {frac("σ", "√B")}', 'σ is how much the per example gradients disagree. Four times the batch size halves the noise, the same √n rule as the standard error in Chapter 10.')}
'''),
    'landscape': deep('meeting a saddle point', f'''
<p>A saddle is flat in the middle, but it curves up in one direction and down in another, which is where the name comes from: the seat used for horse riding has exactly this shape. The simplest example is f(x, y) = x² − y².</p>
{worked('Why (0, 0) is a saddle of f = x² − y²', [
        'Gradient: <span class="eq">∇f = [2x, −2y]</span>, which is <span class="eq">[0, 0]</span> at the origin. So it is a flat point.',
        'Hessian: <span class="eq">H = [[2, 0], [0, −2]]</span>, with eigenvalues <span class="eq">2</span> and <span class="eq">−2</span>',
        'One positive eigenvalue: along x the surface is a valley.',
        'One negative eigenvalue: along y the surface is a hill.',
        'Mixed signs mean a saddle. A tiny push in y and gradient descent rolls away downhill.'])}
<p>In a network with millions of weights, a flat point is a minimum only if <b>every</b> one of millions of curvature directions bends upward. That is extremely unlikely, so most flat points are saddles. Plain gradient descent can crawl near them because the gradient is tiny, but the randomness of mini batches and the speed kept by momentum usually carry the weights past.</p>
'''),
    'lagrange': deep('inequality constraints and the KKT conditions in plain words', f'''
<p>Many real rules are limits rather than exact equalities: "spend at most 100", "the weights must have length at most 1", "a probability cannot be negative". These are <b>inequality constraints</b>, g(x) ≤ c. There are only two possibilities at the best point.</p>
{table(['Case', 'What happens', 'Multiplier'], [
        ['the limit is not reached', 'the best point is inside the allowed region, so ∇f = 0 there as usual', 'λ = 0, the rule costs nothing'],
        ['the limit is reached', 'the best point sits on the boundary, and the Lagrange rule ∇f = λ∇g holds', 'λ &gt; 0, loosening the rule would help'],
    ])}
<p>Both cases are captured in one line, called <b>complementary slackness</b>: λ × (g(x) − c) = 0. Either the multiplier is zero or the constraint is tight. Together with ∇f = λ∇g and λ ≥ 0 these are the <b>Karush Kuhn Tucker (KKT) conditions</b>, the rule book for constrained optimisation.</p>
{ml('In a support vector machine, every training point has its own multiplier. Points far from the boundary have λ = 0 and do not affect the answer at all. Only the points that sit right on the margin have λ &gt; 0. Those are the support vectors that give the method its name.')}
'''),
    'practice': deep('draw your own learning rate schedule', f'''
<p>A schedule is just a function η(t) of the step number. The most common one for large models has a short linear <b>warm up</b> followed by a <b>cosine decay</b>. Set the number of steps and the warm up below and press Play to move along the schedule.</p>
{viz('sched')}
{fx('Warm up then cosine', f'η(t) = η<sub>max</sub> × {frac("t", "T<sub>w</sub>")} for t &lt; T<sub>w</sub>, then η<sub>max</sub> × ½(1 + cos(π {frac("t − T<sub>w</sub>", "T − T<sub>w</sub>")}))', 'T<sub>w</sub> is the warm up length and T the total number of steps.')}
<p>Why warm up at all? At step 1 the weights are random and Adam has not yet seen enough gradients to estimate their typical size, so its step sizes can be wild. A gentle start for the first few hundred or thousand steps lets those statistics settle before the full learning rate is used.</p>
'''),
}
for _p in PARTS:
    _p['html'] += DEEPER.get(_p['id'], '')

VIZ_JS += r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;

  /* ----- loss curves for several learning rates ----- */
  W.lrcurve = el => {
    const b = shell(el, 'Loss curves for different learning rates', 'Gradient descent on L = w² from w = 1. Grey curves are fixed examples. Move the slider to draw your own curve in orange, then press Play to draw all of them step by step.');
    b.innerHTML = `<div class="mv-wrap"><div class="lc-plot"></div><div class="mv-side">${slider('lr', 'your η', 0.01, 1.05, 0.3, 0.01)}<div class="mv-legend"><span><i class="k"></i>η = 0.02, 0.2, 0.95</span><span><i class="o"></i>your η</span></div><div class="mv-read lc-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let lr = 0.3;
    const run = e => { let w = 1; const L = [1]; for (let k = 0; k < 20; k++) { w = (1 - 2 * e) * w; L.push(Math.min(3, w * w)); } return L; };
    const G = MV.frame(440, 300, [0, 20.5], [0, 1.6]);
    function show(t) {
      let s = MV.axes(G, { labels: false, xl: 'step', yl: 'loss' });
      for (let k = 5; k <= 20; k += 5) s += MV.text(G, k, 0, String(k), { dy: 14, anchor: 'middle', cls: 'sm' });
      [0.5, 1].forEach(y => { s += MV.text(G, 0, y, MV.num(y, 1), { dx: 3, dy: 4, cls: 'sm' }); });
      const line = (L, cls) => `<polyline class="mv-v ${cls}" stroke-width="2" points="${L.slice(0, t + 1).map((v, k) => G.sx(k).toFixed(1) + ',' + G.sy(Math.min(1.6, v)).toFixed(1)).join(' ')}"/>`;
      [0.02, 0.2, 0.95].forEach(e => { s += line(run(e), 'k'); });
      const mine = run(lr);
      s += line(mine, 'o');
      $('.lc-plot', b).innerHTML = MV.svg(G, s, 'Loss curves');
      const f = 1 - 2 * lr;
      $('.lc-out', b).innerHTML = `your η = <b>${MV.num(lr)}</b><br>each step multiplies w by 1 − 2η = <b>${MV.num(f, 2)}</b><br>loss at step ${t}: <b>${MV.num(mine[t], 5)}</b><br>` +
        (Math.abs(f) >= 1 ? '❌ |factor| ≥ 1: the loss never falls. Diverging.' : f < 0 ? '⚠️ Negative factor: w flips sign each step (zig zag), but it still shrinks.' : lr < 0.05 ? '🐢 Very slow.' : '✅ Smooth and steady.');
    }
    const P = Player($('.vz-p', b), show, 250);
    wireSlider(b, 'lr', v => { lr = v; P.load(21, 20); });
    P.load(21, 20);
  };

  /* ----- full batch, mini batch and single example paths on one contour map ----- */
  W.sgdpath = el => {
    const b = shell(el, 'Three ways down the same valley', 'Fitting y = w x + b to 40 noisy points from y = 2x + 1. Press Play to take updates. The purple dot marks the best (w, b).');
    b.innerHTML = `<div class="vz-row">${seg('m', [['all', 'All three'], ['full', 'Full batch'], ['mini', 'Mini batch of 8'], ['one', 'One example']], 'all')}</div><div class="mv-wrap"><div class="sg-plot"></div><div class="mv-side"><div class="mv-legend"><span><i class="g"></i>full batch</span><span><i class="a"></i>mini batch 8</span><span><i class="r"></i>one example</span></div><div class="mv-read sg-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let seed = 7;
    const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
    const xs = [], ys = [];
    for (let i = 0; i < 40; i++) { const x = -1 + 2 * i / 39; xs.push(x); ys.push(2 * x + 1 + (rnd() - 0.5) * 1.2); }
    const n = xs.length, mx = xs.reduce((a, c) => a + c) / n, my = ys.reduce((a, c) => a + c) / n;
    let sxy = 0, sxx = 0; for (let i = 0; i < n; i++) { sxy += (xs[i] - mx) * (ys[i] - my); sxx += (xs[i] - mx) ** 2; }
    const wB = sxy / sxx, bB = my - wB * mx;
    const loss = (w, bb) => { let s = 0; for (let i = 0; i < n; i++) s += (w * xs[i] + bb - ys[i]) ** 2; return s / n; };
    const N = 40, lr = 0.25;
    const run = B => {
      let w = -1, bb = -1.5, p = [[w, bb]], order = [];
      seed = 11;
      for (let t = 0; t < N; t++) {
        if (order.length < B) { const o = [...Array(n).keys()]; for (let i = n - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [o[i], o[j]] = [o[j], o[i]]; } order = order.concat(o); }
        const idx = order.splice(0, B);
        let gw = 0, gb = 0; idx.forEach(i => { const e = w * xs[i] + bb - ys[i]; gw += 2 * e * xs[i] / B; gb += 2 * e / B; });
        w -= lr * gw; bb -= lr * gb; p.push([w, bb]);
      }
      return p;
    };
    const paths = { full: run(n), mini: run(8), one: run(1) };
    const G = MV.frame(420, 380, [-1.5, 4], [-2, 3]);
    const cont = (() => { let s = ''; const lv = [0.3, 0.6, 1.2, 2.5, 5, 9]; for (let gx = 0; gx < 56; gx++) for (let gy = 0; gy < 50; gy++) { const w = -1.5 + gx * 0.1, bb = -2 + gy * 0.1; const v = loss(w, bb), k = lv.findIndex(l => v < l); const op = k < 0 ? 0.02 : 0.06 + (lv.length - k) * 0.035; s += `<rect class="mv-heat" x="${G.sx(w - 0.05).toFixed(1)}" y="${G.sy(bb + 0.05).toFixed(1)}" width="${(G.sx(0.1) - G.sx(0)).toFixed(1)}" height="${(G.sy(0) - G.sy(0.1)).toFixed(1)}" style="fill:var(--accent);opacity:${op.toFixed(3)}"/>`; } return s; })();
    let mode = 'all';
    function show(t) {
      let s = cont + MV.axes(G, { labels: false, xl: 'w', yl: 'b' }) + MV.dot(G, wB, bB, 'p', 7);
      const draw = (k, c) => { const p = paths[k].slice(0, t + 1); s += `<polyline class="mv-v ${c}" stroke-width="2" points="${p.map(q => G.sx(q[0]).toFixed(1) + ',' + G.sy(q[1]).toFixed(1)).join(' ')}"/>` + MV.dot(G, p[p.length - 1][0], p[p.length - 1][1], c, 5); };
      if (mode === 'all' || mode === 'full') draw('full', 'g');
      if (mode === 'all' || mode === 'mini') draw('mini', 'a');
      if (mode === 'all' || mode === 'one') draw('one', 'r');
      $('.sg-plot', b).innerHTML = MV.svg(G, s, 'Paths on the loss surface');
      const L = k => MV.num(loss(...paths[k][t]), 4);
      $('.sg-out', b).innerHTML = `update ${t}<br>best fit: w = ${MV.num(wB, 3)}, b = ${MV.num(bB, 3)}, loss ${MV.num(loss(wB, bB), 4)}<br>full batch loss: <b>${L('full')}</b> (uses 40 points per step)<br>mini batch loss: <b>${L('mini')}</b> (8 points per step)<br>one example loss: <b>${L('one')}</b> (1 point per step)`;
    }
    const P = Player($('.vz-p', b), show, 220);
    wireSeg(b, 'm', v => { mode = v; show(P.i); });
    P.load(N + 1, 0);
  };

  /* ----- warm up plus cosine (or step) learning rate schedule ----- */
  W.sched = el => {
    const b = shell(el, 'Learning rate schedules', 'Choose a schedule, the total number of steps and the warm up length. Press Play to walk along it and read η at each step.');
    b.innerHTML = `<div class="vz-row">${seg('k', [['cos', 'Warm up + cosine'], ['step', 'Step decay'], ['const', 'Constant']], 'cos')}</div><div class="mv-wrap"><div class="sc-plot"></div><div class="mv-side">${slider('T', 'total steps', 200, 2000, 1000, 100)}${slider('w', 'warm up steps', 0, 400, 100, 10)}<div class="mv-read sc-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let kind = 'cos', T = 1000, Tw = 100, cur = 0;
    const eta = t => { const m = 0.001; if (kind === 'const') return m; if (t < Tw) return m * (t + 1) / Tw; if (kind === 'step') return m * 0.1 ** Math.floor((t - Tw) / ((T - Tw) / 3)); return m * 0.5 * (1 + Math.cos(Math.PI * (t - Tw) / Math.max(1, T - Tw))); };
    function show(i) {
      cur = Math.round(i / 40 * T);
      const G = MV.frame(440, 280, [0, T], [0, 0.0011]);
      let s = MV.axes(G, { labels: false, xl: 'step', yl: 'η' });
      [0.0005, 0.001].forEach(y => { s += MV.text(G, 0, y, y.toString(), { dx: 3, dy: -3, cls: 'sm' }); });
      s += MV.text(G, T, 0, String(T), { dy: 14, anchor: 'end', cls: 'sm' });
      s += MV.curve(G, eta, '', { n: 400 }) + MV.dot(G, cur, eta(Math.min(T - 1, cur)), 'o', 7);
      if (Tw > 0 && kind !== 'const') s += MV.line(G, Tw, 0, Tw, 0.0011, 'mv-v k dash') + MV.text(G, Tw, 0.00105, 'end of warm up', { dx: 4, cls: 'sm' });
      $('.sc-plot', b).innerHTML = MV.svg(G, s, 'Learning rate against step');
      const e = eta(Math.min(T - 1, cur));
      $('.sc-out', b).innerHTML = `step <b>${cur}</b> of ${T}<br>η = <b>${e.toExponential(2)}</b><br>` + (kind !== 'const' && cur < Tw ? 'warming up: η grows in a straight line' : kind === 'cos' ? 'cosine decay: slow at first, fastest in the middle, gentle at the end' : kind === 'step' ? 'step decay: η drops by 10 times at fixed points' : 'constant: the same η all the way');
    }
    const P = Player($('.vz-p', b), show, 200);
    wireSeg(b, 'k', v => { kind = v; show(P.i); });
    wireSlider(b, 'T', v => { T = v; if (Tw > T / 2) Tw = Math.floor(T / 2); show(P.i); });
    wireSlider(b, 'w', v => { Tw = Math.min(v, T / 2); show(P.i); });
    P.load(41, 12);
  };
})();
'''
CSS = r'''
.sg-plot .mv-svg{max-height:400px}
'''

T = K.topic(
    slug='optimisation', topic='optimisation', prefix='mm08', short='Optimisation', emoji='⛷️',
    title='Gradient Descent and Optimisation',
    module=('📉', 'Calculus', 'calculus', 'Derivatives, gradients, the chain rule and optimisation: the maths that lets a model learn from its mistakes.'),
    minutes=60,
    lead='Training a model is walking downhill on its loss. Run gradient descent step by step, find the learning rate that is just right, see why mini batches work, race plain gradient descent against momentum and Adam, and solve problems with constraints using Lagrange multipliers.',
    desc='Optimisation for machine learning: gradient descent, the learning rate and stability, stochastic and mini batch gradient descent, momentum, RMSProp and Adam, convexity and saddle points, Lagrange multipliers and learning rate schedules.',
    summary='The gradient descent update, learning rates that crawl, converge, zig zag or diverge, SGD, mini batches and epochs, momentum, RMSProp and Adam with bias correction, convex and non convex landscapes, the condition number and feature scaling, Lagrange multipliers, warm up, cosine decay, clipping and early stopping.',
    keywords=['gradient descent', 'learning rate', 'sgd', 'mini batch', 'epoch', 'momentum', 'rmsprop', 'adam', 'adamw', 'convex', 'saddle point', 'condition number', 'lagrange multiplier', 'learning rate schedule', 'gradient clipping', 'early stopping'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
