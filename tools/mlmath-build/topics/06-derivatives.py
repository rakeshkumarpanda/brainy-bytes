# Chapter 6: rates of change, limits and the derivative, the differentiation rules, the chain rule,
# maxima, minima and the second derivative, integrals as areas, and where derivatives drive learning.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz, deep

K = Kit()

# ---------------------------------------------------------------- programs
K.code('numdiff', py=r'''
def f(x):
    return x * x


x = 3
for h in [1, 0.1, 0.01, 0.001]:
    slope = (f(x + h) - f(x)) / h          # rise over run across a gap of h
    print(f"h = {h}: slope = {slope:.4f}")
central = (f(x + 0.001) - f(x - 0.001)) / 0.002   # look both ways
print(f"central difference: {central:.4f}")
print("exact answer from the rule 2x:", 2 * x)
''', js=r'''
function f(x) {
  return x * x;
}

const x = 3;
for (const h of [1, 0.1, 0.01, 0.001]) {
  const slope = (f(x + h) - f(x)) / h;     // rise over run across a gap of h
  console.log(`h = ${h}: slope = ${slope.toFixed(4)}`);
}
const central = (f(x + 0.001) - f(x - 0.001)) / 0.002;   // look both ways
console.log(`central difference: ${central.toFixed(4)}`);
console.log("exact answer from the rule 2x:", 2 * x);
''', ts=r'''
function f(x: number): number {
  return x * x;
}

const x: number = 3;
for (const h of [1, 0.1, 0.01, 0.001]) {
  const slope: number = (f(x + h) - f(x)) / h;   // rise over run across a gap of h
  console.log(`h = ${h}: slope = ${slope.toFixed(4)}`);
}
const central: number = (f(x + 0.001) - f(x - 0.001)) / 0.002;   // look both ways
console.log(`central difference: ${central.toFixed(4)}`);
console.log("exact answer from the rule 2x:", 2 * x);
''', java=r'''
public class NumDiff {
    static double f(double x) {
        return x * x;
    }

    public static void main(String[] args) {
        double x = 3;
        double[] hs = {1, 0.1, 0.01, 0.001};
        String[] names = {"1", "0.1", "0.01", "0.001"};
        for (int i = 0; i < hs.length; i++) {
            double slope = (f(x + hs[i]) - f(x)) / hs[i];   // rise over run across a gap of h
            System.out.println(String.format("h = %s: slope = %.4f", names[i], slope));
        }
        double central = (f(x + 0.001) - f(x - 0.001)) / 0.002;   // look both ways
        System.out.println(String.format("central difference: %.4f", central));
        System.out.println("exact answer from the rule 2x: " + (int) (2 * x));
    }
}
''')

K.code('rules', py=r'''
import math

h = 1e-5
x = 2.0
tests = [
    ("x^3", lambda t: t ** 3, lambda t: 3 * t ** 2),       # power rule
    ("e^x", math.exp, math.exp),                           # e^x is its own slope
    ("ln x", math.log, lambda t: 1 / t),
    ("sin x", math.sin, math.cos),
]
for label, f, rule in tests:
    numeric = (f(x + h) - f(x - h)) / (2 * h)
    print(f"{label:6}: rule says {rule(x):.4f}, numbers say {numeric:.4f}")
''', js=r'''
const h = 1e-5;
const x = 2.0;
const tests = [
  ["x^3", t => t ** 3, t => 3 * t ** 2],                   // power rule
  ["e^x", Math.exp, Math.exp],                             // e^x is its own slope
  ["ln x", Math.log, t => 1 / t],
  ["sin x", Math.sin, Math.cos],
];
for (const [label, f, rule] of tests) {
  const numeric = (f(x + h) - f(x - h)) / (2 * h);
  console.log(`${label.padEnd(6)}: rule says ${rule(x).toFixed(4)}, numbers say ${numeric.toFixed(4)}`);
}
''', ts=r'''
type Fn = (t: number) => number;
const h: number = 1e-5;
const x: number = 2.0;
const tests: [string, Fn, Fn][] = [
  ["x^3", t => t ** 3, t => 3 * t ** 2],                   // power rule
  ["e^x", Math.exp, Math.exp],                             // e^x is its own slope
  ["ln x", Math.log, t => 1 / t],
  ["sin x", Math.sin, Math.cos],
];
for (const [label, f, rule] of tests) {
  const numeric: number = (f(x + h) - f(x - h)) / (2 * h);
  console.log(`${label.padEnd(6)}: rule says ${rule(x).toFixed(4)}, numbers say ${numeric.toFixed(4)}`);
}
''', java=r'''
import java.util.function.DoubleUnaryOperator;

public class Rules {
    public static void main(String[] args) {
        double h = 1e-5, x = 2.0;
        String[] labels = {"x^3", "e^x", "ln x", "sin x"};
        DoubleUnaryOperator[] fs = {t -> t * t * t, Math::exp, Math::log, Math::sin};
        DoubleUnaryOperator[] rules = {t -> 3 * t * t, Math::exp, t -> 1 / t, Math::cos};   // power rule, e^x, 1/x, cos
        for (int i = 0; i < labels.length; i++) {
            double numeric = (fs[i].applyAsDouble(x + h) - fs[i].applyAsDouble(x - h)) / (2 * h);
            System.out.println(String.format("%-6s: rule says %.4f, numbers say %.4f", labels[i], rules[i].applyAsDouble(x), numeric));
        }
    }
}
''')

K.code('sigmoid_grad', py=r'''
import math


def sigmoid(z):
    return 1 / (1 + math.exp(-z))


for z in [-4, -2, 0, 2, 4]:
    s = sigmoid(z)
    slope = s * (1 - s)                   # chain rule result: sigma times (1 - sigma)
    print(f"z = {z:2}: sigmoid = {s:.4f}, slope = {slope:.4f}")
print("the slope is never more than 0.25, which is why deep sigmoid nets learn slowly")
''', js=r'''
function sigmoid(z) {
  return 1 / (1 + Math.exp(-z));
}

for (const z of [-4, -2, 0, 2, 4]) {
  const s = sigmoid(z);
  const slope = s * (1 - s);              // chain rule result: sigma times (1 - sigma)
  console.log(`z = ${String(z).padStart(2)}: sigmoid = ${s.toFixed(4)}, slope = ${slope.toFixed(4)}`);
}
console.log("the slope is never more than 0.25, which is why deep sigmoid nets learn slowly");
''', ts=r'''
function sigmoid(z: number): number {
  return 1 / (1 + Math.exp(-z));
}

for (const z of [-4, -2, 0, 2, 4]) {
  const s: number = sigmoid(z);
  const slope: number = s * (1 - s);      // chain rule result: sigma times (1 - sigma)
  console.log(`z = ${String(z).padStart(2)}: sigmoid = ${s.toFixed(4)}, slope = ${slope.toFixed(4)}`);
}
console.log("the slope is never more than 0.25, which is why deep sigmoid nets learn slowly");
''', java=r'''
public class SigmoidGrad {
    static double sigmoid(double z) {
        return 1 / (1 + Math.exp(-z));
    }

    public static void main(String[] args) {
        int[] zs = {-4, -2, 0, 2, 4};
        for (int z : zs) {
            double s = sigmoid(z);
            double slope = s * (1 - s);           // chain rule result: sigma times (1 - sigma)
            System.out.println(String.format("z = %2d: sigmoid = %.4f, slope = %.4f", z, s, slope));
        }
        System.out.println("the slope is never more than 0.25, which is why deep sigmoid nets learn slowly");
    }
}
''')

K.code('riemann', py=r'''
def f(x):
    return x * x


a, b = 0, 3
for n in [3, 6, 30]:
    width = (b - a) / n
    total = 0
    for i in range(n):
        mid = a + (i + 0.5) * width       # middle of strip i
        total += f(mid) * width           # area of one thin rectangle
    print(f"{n:2} strips: area = {total:.4f}")
print("exact: x^3 / 3 from 0 to 3 =", (b ** 3 - a ** 3) // 3)
''', js=r'''
function f(x) {
  return x * x;
}

const a = 0, b = 3;
for (const n of [3, 6, 30]) {
  const width = (b - a) / n;
  let total = 0;
  for (let i = 0; i < n; i++) {
    const mid = a + (i + 0.5) * width;    // middle of strip i
    total += f(mid) * width;              // area of one thin rectangle
  }
  console.log(`${String(n).padStart(2)} strips: area = ${total.toFixed(4)}`);
}
console.log("exact: x^3 / 3 from 0 to 3 =", (b ** 3 - a ** 3) / 3);
''', ts=r'''
function f(x: number): number {
  return x * x;
}

const a: number = 0, b: number = 3;
for (const n of [3, 6, 30]) {
  const width: number = (b - a) / n;
  let total: number = 0;
  for (let i = 0; i < n; i++) {
    const mid: number = a + (i + 0.5) * width;   // middle of strip i
    total += f(mid) * width;                     // area of one thin rectangle
  }
  console.log(`${String(n).padStart(2)} strips: area = ${total.toFixed(4)}`);
}
console.log("exact: x^3 / 3 from 0 to 3 =", (b ** 3 - a ** 3) / 3);
''', java=r'''
public class Riemann {
    static double f(double x) {
        return x * x;
    }

    public static void main(String[] args) {
        int a = 0, b = 3;
        int[] ns = {3, 6, 30};
        for (int n : ns) {
            double width = (double) (b - a) / n;
            double total = 0;
            for (int i = 0; i < n; i++) {
                double mid = a + (i + 0.5) * width;   // middle of strip i
                total += f(mid) * width;              // area of one thin rectangle
            }
            System.out.println(String.format("%2d strips: area = %.4f", n, total));
        }
        System.out.println("exact: x^3 / 3 from 0 to 3 = " + (b * b * b - a * a * a) / 3);
    }
}
''')

K.code('p_tangent', py=r'''
def f(x):
    return x ** 3 - 2 * x


def df(x):
    return 3 * x ** 2 - 2                 # power rule on each term


a = 2
slope = df(a)
c = f(a) - slope * a                      # the line y = slope * x + c passes through (a, f(a))
print(f"point: ({a}, {f(a)}), slope: {slope}")
print(f"tangent line: y = {slope}x + ({c})")
for x in [1.9, 2.1]:
    print(f"x = {x}: curve {f(x):.3f}, tangent {slope * x + c:.3f}")
''', js=r'''
function f(x) {
  return x ** 3 - 2 * x;
}

function df(x) {
  return 3 * x ** 2 - 2;                  // power rule on each term
}

const a = 2;
const slope = df(a);
const c = f(a) - slope * a;               // the line y = slope * x + c passes through (a, f(a))
console.log(`point: (${a}, ${f(a)}), slope: ${slope}`);
console.log(`tangent line: y = ${slope}x + (${c})`);
for (const x of [1.9, 2.1]) {
  console.log(`x = ${x}: curve ${f(x).toFixed(3)}, tangent ${(slope * x + c).toFixed(3)}`);
}
''', ts=r'''
function f(x: number): number {
  return x ** 3 - 2 * x;
}

function df(x: number): number {
  return 3 * x ** 2 - 2;                  // power rule on each term
}

const a: number = 2;
const slope: number = df(a);
const c: number = f(a) - slope * a;       // the line y = slope * x + c passes through (a, f(a))
console.log(`point: (${a}, ${f(a)}), slope: ${slope}`);
console.log(`tangent line: y = ${slope}x + (${c})`);
for (const x of [1.9, 2.1]) {
  console.log(`x = ${x}: curve ${f(x).toFixed(3)}, tangent ${(slope * x + c).toFixed(3)}`);
}
''', java=r'''
public class PracticeTangent {
    static double f(double x) {
        return x * x * x - 2 * x;
    }

    static double df(double x) {
        return 3 * x * x - 2;                 // power rule on each term
    }

    public static void main(String[] args) {
        int a = 2;
        int slope = (int) df(a);
        int c = (int) (f(a) - slope * a);     // the line y = slope * x + c passes through (a, f(a))
        System.out.println("point: (" + a + ", " + (int) f(a) + "), slope: " + slope);
        System.out.println("tangent line: y = " + slope + "x + (" + c + ")");
        double[] xs = {1.9, 2.1};
        for (double x : xs) {
            System.out.println(String.format("x = %s: curve %.3f, tangent %.3f", x, f(x), slope * x + c));
        }
    }
}
''')

K.code('p_box', py=r'''
# cut an x by x square from each corner of a 12 cm sheet and fold up the sides
def volume(x):
    return x * (12 - 2 * x) ** 2


best_x, best_v = 0, 0
for k in range(1, 12):
    x = k * 0.5
    v = volume(x)
    if v > best_v:
        best_x, best_v = x, v
print(f"by trying values: x = {best_x:.1f} gives V = {best_v:.1f}")
# calculus: V'(x) = (12 - 2x)(12 - 6x) = 0 gives x = 6 or x = 2
for x in [2, 6]:
    print(f"V'(x) = 0 at x = {x}: V = {volume(x)}")
''', js=r'''
// cut an x by x square from each corner of a 12 cm sheet and fold up the sides
function volume(x) {
  return x * (12 - 2 * x) ** 2;
}

let bestX = 0, bestV = 0;
for (let k = 1; k < 12; k++) {
  const x = k * 0.5;
  const v = volume(x);
  if (v > bestV) {
    bestX = x;
    bestV = v;
  }
}
console.log(`by trying values: x = ${bestX.toFixed(1)} gives V = ${bestV.toFixed(1)}`);
// calculus: V'(x) = (12 - 2x)(12 - 6x) = 0 gives x = 6 or x = 2
for (const x of [2, 6]) {
  console.log(`V'(x) = 0 at x = ${x}: V = ${volume(x)}`);
}
''', ts=r'''
// cut an x by x square from each corner of a 12 cm sheet and fold up the sides
function volume(x: number): number {
  return x * (12 - 2 * x) ** 2;
}

let bestX: number = 0, bestV: number = 0;
for (let k = 1; k < 12; k++) {
  const x: number = k * 0.5;
  const v: number = volume(x);
  if (v > bestV) {
    bestX = x;
    bestV = v;
  }
}
console.log(`by trying values: x = ${bestX.toFixed(1)} gives V = ${bestV.toFixed(1)}`);
// calculus: V'(x) = (12 - 2x)(12 - 6x) = 0 gives x = 6 or x = 2
for (const x of [2, 6]) {
  console.log(`V'(x) = 0 at x = ${x}: V = ${volume(x)}`);
}
''', java=r'''
public class PracticeBox {
    // cut an x by x square from each corner of a 12 cm sheet and fold up the sides
    static double volume(double x) {
        return x * (12 - 2 * x) * (12 - 2 * x);
    }

    public static void main(String[] args) {
        double bestX = 0, bestV = 0;
        for (int k = 1; k < 12; k++) {
            double x = k * 0.5;
            double v = volume(x);
            if (v > bestV) {
                bestX = x;
                bestV = v;
            }
        }
        System.out.println(String.format("by trying values: x = %.1f gives V = %.1f", bestX, bestV));
        // calculus: V'(x) = (12 - 2x)(12 - 6x) = 0 gives x = 6 or x = 2
        int[] xs = {2, 6};
        for (int x : xs) {
            System.out.println("V'(x) = 0 at x = " + x + ": V = " + (int) volume(x));
        }
    }
}
''')

K.code('p_newton', py=r'''
# Newton's method: follow the tangent line down to zero, again and again
def f(x):
    return x * x - 2                      # its root is the square root of 2


def df(x):
    return 2 * x


x = 1.0
for step in range(1, 6):
    x = x - f(x) / df(x)                  # where the tangent at x hits zero
    print(f"step {step}: x = {x:.6f}")
print(f"check: x * x = {x * x:.6f}")
''', js=r'''
// Newton's method: follow the tangent line down to zero, again and again
function f(x) {
  return x * x - 2;                       // its root is the square root of 2
}

function df(x) {
  return 2 * x;
}

let x = 1.0;
for (let step = 1; step <= 5; step++) {
  x = x - f(x) / df(x);                   // where the tangent at x hits zero
  console.log(`step ${step}: x = ${x.toFixed(6)}`);
}
console.log(`check: x * x = ${(x * x).toFixed(6)}`);
''', ts=r'''
// Newton's method: follow the tangent line down to zero, again and again
function f(x: number): number {
  return x * x - 2;                       // its root is the square root of 2
}

function df(x: number): number {
  return 2 * x;
}

let x: number = 1.0;
for (let step = 1; step <= 5; step++) {
  x = x - f(x) / df(x);                   // where the tangent at x hits zero
  console.log(`step ${step}: x = ${x.toFixed(6)}`);
}
console.log(`check: x * x = ${(x * x).toFixed(6)}`);
''', java=r'''
public class PracticeNewton {
    // Newton's method: follow the tangent line down to zero, again and again
    static double f(double x) {
        return x * x - 2;                     // its root is the square root of 2
    }

    static double df(double x) {
        return 2 * x;
    }

    public static void main(String[] args) {
        double x = 1.0;
        for (int step = 1; step <= 5; step++) {
            x = x - f(x) / df(x);             // where the tangent at x hits zero
            System.out.println(String.format("step %d: x = %.6f", step, x));
        }
        System.out.println(String.format("check: x * x = %.6f", x * x));
    }
}
''')

K.code('p_simpson', py=r'''
import math


def bell(x):                              # the standard normal curve
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


a, b, n = -1, 1, 10
h = (b - a) / n
trap = bell(a) / 2 + bell(b) / 2
simp = bell(a) + bell(b)
for i in range(1, n):
    y = bell(a + i * h)
    trap += y                             # trapezoids: inside points count once
    simp += (4 if i % 2 else 2) * y       # Simpson: weights 4, 2, 4, 2, ...
print(f"trapezoid rule: {trap * h:.6f}")
print(f"Simpson's rule: {simp * h / 3:.6f}")
print(f"true value:     {math.erf(1 / math.sqrt(2)):.6f}")
''', js=r'''
function bell(x) {                        // the standard normal curve
  return Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI);
}

const a = -1, b = 1, n = 10;
const h = (b - a) / n;
let trap = bell(a) / 2 + bell(b) / 2;
let simp = bell(a) + bell(b);
for (let i = 1; i < n; i++) {
  const y = bell(a + i * h);
  trap += y;                              // trapezoids: inside points count once
  simp += (i % 2 ? 4 : 2) * y;            // Simpson: weights 4, 2, 4, 2, ...
}
console.log(`trapezoid rule: ${(trap * h).toFixed(6)}`);
console.log(`Simpson's rule: ${(simp * h / 3).toFixed(6)}`);
console.log(`true value:     ${(0.682689492137086).toFixed(6)}`);
''', ts=r'''
function bell(x: number): number {        // the standard normal curve
  return Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI);
}

const a: number = -1, b: number = 1, n: number = 10;
const h: number = (b - a) / n;
let trap: number = bell(a) / 2 + bell(b) / 2;
let simp: number = bell(a) + bell(b);
for (let i = 1; i < n; i++) {
  const y: number = bell(a + i * h);
  trap += y;                              // trapezoids: inside points count once
  simp += (i % 2 ? 4 : 2) * y;            // Simpson: weights 4, 2, 4, 2, ...
}
console.log(`trapezoid rule: ${(trap * h).toFixed(6)}`);
console.log(`Simpson's rule: ${(simp * h / 3).toFixed(6)}`);
console.log(`true value:     ${(0.682689492137086).toFixed(6)}`);
''', java=r'''
public class PracticeSimpson {
    static double bell(double x) {            // the standard normal curve
        return Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI);
    }

    public static void main(String[] args) {
        double a = -1, b = 1;
        int n = 10;
        double h = (b - a) / n;
        double trap = bell(a) / 2 + bell(b) / 2;
        double simp = bell(a) + bell(b);
        for (int i = 1; i < n; i++) {
            double y = bell(a + i * h);
            trap += y;                            // trapezoids: inside points count once
            simp += (i % 2 == 1 ? 4 : 2) * y;     // Simpson: weights 4, 2, 4, 2, ...
        }
        System.out.println(String.format("trapezoid rule: %.6f", trap * h));
        System.out.println(String.format("Simpson's rule: %.6f", simp * h / 3));
        System.out.println(String.format("true value:     %.6f", 0.682689492137086));
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('rate', '🚗', 'Rate of change and slope', f'''
<p>A <b>derivative</b> answers one question: <b>how fast is something changing right now?</b> A car that travels 120 km in 2 hours has an <b>average</b> speed of 60 km/h, but the speedometer shows the speed at this exact moment. The derivative is the speedometer.</p>
{fxs(fx('Average rate of change (slope of a secant)', f'{frac("f(b) − f(a)", "b − a")}', 'Rise over run between two points on the curve.'),
         fx('Instant rate of change (slope of the tangent)', f"f′(a) = lim<sub>h→0</sub> {frac('f(a + h) − f(a)', 'h')}", 'Slide the second point closer and closer to the first. The slope settles on one number.'))}
{viz('secant')}
{worked('Average speed of a ball dropped from a tower: distance d(t) = 5t² metres', [
        'From t = 1 to t = 3: <span class="eq">d(3) − d(1) = 45 − 5 = 40 m</span> in 2 s, average <span class="eq">40 ÷ 2 = 20 m/s</span>',
        'From t = 1 to t = 1.1: <span class="eq">d(1.1) = 5 × 1.21 = 6.05</span>, so <span class="eq">(6.05 − 5) ÷ 0.1 = 10.5 m/s</span>',
        'From t = 1 to t = 1.01: <span class="eq">(5.1005 − 5) ÷ 0.01 = 10.05 m/s</span>',
        'The values close in on <span class="eq">10 m/s</span>. That is the derivative d′(1), the speed at exactly one second.'])}
{table(['Notation', 'Read it as', 'Who uses it'], [
        ['f′(x)', 'f prime of x', 'Lagrange, most school books'],
        ['dy/dx', 'dee y by dee x', 'Leibniz, physics and machine learning papers'],
        ['∂L/∂w', 'partial L by partial w', 'when there are many inputs (Chapter 7)'],
    ])}
{life('Your phone map shows "12 minutes to arrive". It divides the distance left by your current rate of change of position. When traffic slows you, the rate drops and the estimate rises.')}
''', kw=['derivative', 'rate of change', 'slope', 'secant', 'tangent', 'average speed', 'instant speed']),

    part('limit', '🔬', 'Limits and the derivative from first principles', f'''
<p>A <b>limit</b> says what value a formula approaches as the input gets close to some number, even if you cannot plug that number in. You cannot set h = 0 in (f(a + h) − f(a)) ÷ h because that divides by zero, but you can ask what happens as h shrinks.</p>
{worked('Derivative of f(x) = x² from first principles', [
        'Start: <span class="eq">f(x + h) − f(x) = (x + h)² − x²</span>',
        'Expand: <span class="eq">x² + 2xh + h² − x² = 2xh + h²</span>',
        'Divide by h: <span class="eq">(2xh + h²) ÷ h = 2x + h</span>',
        'Let h shrink to 0: <span class="eq">2x + h → 2x</span>. So <span class="eq">f′(x) = 2x</span>. At x = 3 the slope is 6.'])}
{code('numdiff', 'The difference quotient as h shrinks')}
<div class="tip">The <b>central difference</b> (f(x + h) − f(x − h)) ÷ 2h looks both ways and is far more accurate than the one sided version. Machine learning engineers use it for <b>gradient checking</b>: comparing their hand written derivative with this numerical one to catch bugs.</div>
<div class="warn">Do not make h too tiny on a computer. With h = 10⁻¹⁵ the subtraction f(x + h) − f(x) loses almost all its digits to rounding. Something like h = 10⁻⁵ is a safe middle ground.</div>
{trick('A derivative is just "rise over run" for a run so short you cannot see it.')}
''', kw=['limit', 'first principles', 'difference quotient', 'central difference', 'gradient checking', 'numerical derivative']),

    part('rules', '📏', 'The rules of differentiation', f'''
<p>Nobody works from first principles every time. A small set of rules covers almost every function you will meet in machine learning.</p>
{fxs(fx('Power rule', 'd/dx xⁿ = n xⁿ⁻¹', 'Bring the power down, then lower it by one. x⁵ becomes 5x⁴.'),
         fx('Constant and sum rules', '(c·f)′ = c·f′ &nbsp;&nbsp; (f + g)′ = f′ + g′', 'Constants ride along. Differentiate each term on its own.'),
         fx('Product rule', '(f·g)′ = f′g + fg′', 'First times slope of second, plus second times slope of first.'),
         fx('Quotient rule', f'({frac("f", "g")})′ = {frac("f′g − fg′", "g²")}', '"Low d high minus high d low, over low squared".'))}
{table(['Function f(x)', 'Derivative f′(x)', 'Note'], [
        ['c (a constant)', '0', 'a flat line has no slope'],
        ['xⁿ', 'n xⁿ⁻¹', 'works for any power, also √x = x^(1/2)'],
        ['eˣ', 'eˣ', 'the only function that is its own slope'],
        ['aˣ', 'aˣ ln a', 'for example 2ˣ has slope 2ˣ × 0.693'],
        ['ln x', '1/x', 'used in every log loss'],
        ['sin x', 'cos x', ''],
        ['cos x', '−sin x', ''],
    ])}
{worked('Differentiate f(x) = 3x⁴ − 5x² + 7x − 2 and find f′(1)', [
        'Term by term: <span class="eq">3x⁴ → 12x³</span>, <span class="eq">−5x² → −10x</span>, <span class="eq">7x → 7</span>, <span class="eq">−2 → 0</span>',
        'So <span class="eq">f′(x) = 12x³ − 10x + 7</span>',
        'At x = 1: <span class="eq">12 − 10 + 7 = 9</span>'])}
{code('rules', 'Checking each rule against a numerical derivative')}
{trick('Product rule chant: "left d right plus right d left". Quotient rule chant: "low d high minus high d low, over the square of what is below".')}
''', kw=['power rule', 'product rule', 'quotient rule', 'sum rule', 'derivative of e^x', 'derivative of ln x', 'derivative table']),

    part('chain', '⛓️', 'The chain rule', f'''
<p>Most functions in machine learning are functions <b>inside</b> functions. A neuron computes z = wx + b, then a = σ(z), then a loss L(a). The <b>chain rule</b> says how a small change at the start ripples through every link.</p>
{fx('Chain rule', f'{frac("dy", "dx")} = {frac("dy", "du")} × {frac("du", "dx")}', 'If y depends on u and u depends on x, multiply the slopes along the chain. Outside slope times inside slope.')}
{worked('Differentiate y = (3x + 1)² at x = 1', [
        'Name the inside: <span class="eq">u = 3x + 1</span>, so <span class="eq">y = u²</span>',
        'Outside slope: <span class="eq">dy/du = 2u</span>. Inside slope: <span class="eq">du/dx = 3</span>',
        'Multiply: <span class="eq">dy/dx = 2u × 3 = 6(3x + 1)</span>',
        'At x = 1: <span class="eq">u = 4</span>, so <span class="eq">dy/dx = 6 × 4 = 24</span>'])}
{worked('The famous sigmoid derivative: σ(z) = 1 ÷ (1 + e⁻ᶻ)', [
        'Write it as <span class="eq">σ = u⁻¹</span> with <span class="eq">u = 1 + e⁻ᶻ</span>',
        'Outside: <span class="eq">dσ/du = −u⁻²</span>. Inside: <span class="eq">du/dz = −e⁻ᶻ</span> (chain rule again on e⁻ᶻ)',
        'Multiply: <span class="eq">σ′ = e⁻ᶻ ÷ (1 + e⁻ᶻ)²</span>',
        'Split it: <span class="eq">σ′ = [1 ÷ (1 + e⁻ᶻ)] × [e⁻ᶻ ÷ (1 + e⁻ᶻ)] = σ × (1 − σ)</span>',
        'At z = 0: <span class="eq">σ = 0.5</span>, so <span class="eq">σ′ = 0.5 × 0.5 = 0.25</span>, the largest it ever gets.'])}
{code('sigmoid_grad', 'Sigmoid and its slope at several inputs')}
{ml('<b>Backpropagation</b> is the chain rule applied over and over, from the loss back to every weight. Chapter 7 walks through it number by number. When many small slopes like 0.25 are multiplied along a deep chain, the product becomes tiny: the <b>vanishing gradient</b> problem. ReLU, whose slope is 1 for positive inputs, fixed much of this.')}
{trick('Peel an onion: differentiate the outside layer, keep the inside untouched, then multiply by the slope of the inside.')}
''', kw=['chain rule', 'composite function', 'sigmoid derivative', 'backpropagation', 'vanishing gradient', 'outside inside']),

    part('shape', '⛰️', 'Peaks, valleys and the second derivative', f'''
<p>Where a smooth curve reaches a peak or the bottom of a valley, it is flat for a moment, so its slope is 0. Setting f′(x) = 0 finds these <b>critical points</b>. The <b>second derivative</b> f″(x), the slope of the slope, tells which kind it is.</p>
{viz('slope')}
{table(['Sign', 'What the curve does', 'Picture'], [
        ['f′(x) > 0', 'rising', '↗'],
        ['f′(x) < 0', 'falling', '↘'],
        ['f′(x) = 0 and f″(x) > 0', 'local minimum, bends upward like a cup', '∪'],
        ['f′(x) = 0 and f″(x) < 0', 'local maximum, bends downward like a cap', '∩'],
        ['f″(x) changes sign', 'inflection point, the bend flips', '∫'],
    ])}
{worked('Find the peaks and valleys of f(x) = x³ − 3x', [
        'Slope: <span class="eq">f′(x) = 3x² − 3</span>',
        'Set it to zero: <span class="eq">3x² = 3</span>, so <span class="eq">x = 1</span> or <span class="eq">x = −1</span>',
        'Second derivative: <span class="eq">f″(x) = 6x</span>',
        'At x = 1: <span class="eq">f″ = 6 > 0</span>, a valley with <span class="eq">f(1) = 1 − 3 = −2</span>',
        'At x = −1: <span class="eq">f″ = −6 < 0</span>, a peak with <span class="eq">f(−1) = −1 + 3 = 2</span>'])}
{fx('Convex function', 'f″(x) ≥ 0 everywhere', 'The curve is a single bowl, so any valley you find is THE lowest point. Mean squared error for linear regression is convex, which is why it always trains to the same answer.')}
{life('A company finds that profit P(price) rises and then falls as the price goes up. Setting P′ = 0 finds the best price, and P″ < 0 there confirms it is a peak, not a dip.')}
''', kw=['critical point', 'maximum', 'minimum', 'second derivative', 'concave', 'convex', 'inflection point', 'optimisation']),

    part('integral', '📐', 'Integrals: adding up tiny pieces', f'''
<p>An <b>integral</b> is the opposite job of a derivative. A derivative turns distance into speed. An integral turns speed back into distance, by adding up "speed × tiny time" over and over. In pictures, it is the <b>area under a curve</b>.</p>
{viz('riemann')}
{fxs(fx('Definite integral as a sum of strips', '∫ₐᵇ f(x) dx ≈ Σ f(xᵢ) Δx', 'Cut [a, b] into thin strips of width Δx and add up height × width. More strips, better answer.'),
         fx('Fundamental theorem of calculus', '∫ₐᵇ f(x) dx = F(b) − F(a)', 'where F′ = f. Find a function whose slope is f, then subtract its values at the ends.'),
         fx('Power rule backwards', f'∫ xⁿ dx = {frac("xⁿ⁺¹", "n + 1")} + C', 'Raise the power by one, divide by the new power (n ≠ −1).'))}
{worked('Area under y = x² from 0 to 3', [
        'A function whose slope is x² is <span class="eq">F(x) = x³ ÷ 3</span> (check: F′ = 3x² ÷ 3 = x²)',
        'Top end: <span class="eq">F(3) = 27 ÷ 3 = 9</span>. Bottom end: <span class="eq">F(0) = 0</span>',
        'Area: <span class="eq">9 − 0 = 9</span> square units',
        'Rectangles agree: with 30 midpoint strips the sum is 8.9975, very close to 9.'])}
{code('riemann', 'Midpoint rectangles closing in on the exact area')}
{ml('Probabilities of continuous values are areas: the chance that a normal value lands between −1 and 1 is the area under the bell curve there, about 68%. Expected values (Chapter 10) are integrals, and the area under the ROC curve (AUC, Chapter 12) is an integral too.')}
''', kw=['integral', 'area under curve', 'riemann sum', 'antiderivative', 'fundamental theorem of calculus', 'definite integral', 'AUC']),

    part('ml', '🤖', 'Why derivatives make machines learn', f'''
<p>Training a model means making a <b>loss</b> number small. The derivative of the loss with respect to a weight says which way to nudge that weight and how strongly. If ∂L/∂w is positive, increasing w raises the loss, so decrease it. If it is negative, increase w.</p>
{worked('One weight, one example: predict y = 7 from x = 2 with ŷ = w × x, starting at w = 1', [
        'Prediction: <span class="eq">ŷ = 1 × 2 = 2</span>. Loss: <span class="eq">L = (ŷ − y)² = (2 − 7)² = 25</span>',
        'Chain rule: <span class="eq">dL/dw = 2(ŷ − y) × x = 2 × (−5) × 2 = −20</span>',
        'The slope is negative, so w should go <b>up</b>. With a learning rate of 0.05: <span class="eq">w = 1 − 0.05 × (−20) = 2</span>',
        'New prediction: <span class="eq">2 × 2 = 4</span>, new loss <span class="eq">(4 − 7)² = 9</span>. The loss fell from 25 to 9 in one step.'])}
{table(['Activation', 'Formula', 'Derivative', 'Comment'], [
        ['Sigmoid', 'σ(z) = 1 ÷ (1 + e⁻ᶻ)', 'σ(1 − σ)', 'at most 0.25, can vanish'],
        ['Tanh', 'tanh z', '1 − tanh² z', 'at most 1'],
        ['ReLU', 'max(0, z)', '1 if z > 0, else 0', 'cheap, does not vanish for positive z'],
        ['Softplus', 'ln(1 + eᶻ)', 'σ(z)', 'a smooth ReLU'],
    ])}
{code('p_newton', "Newton's method uses the derivative to find a root fast")}
{ml('Every deep learning library (PyTorch, TensorFlow, JAX) contains <b>automatic differentiation</b>: it records each operation and applies the chain rule backwards to get exact derivatives for millions of weights. You write the forward pass, the library writes the derivatives.')}
{trick('Slope positive, step left. Slope negative, step right. Slope zero, you are at the bottom (or a flat spot).')}
''', kw=['loss', 'gradient descent preview', 'learning rate', 'activation derivatives', 'relu derivative', 'automatic differentiation', 'newton method']),
]

INFO = {
    'title': 'A derivative is a speedometer for any function',
    'panels': [
        {'s': [['e', '🚗'], ['t', 'rise ÷ run', {'b': 1}]], 'h': 'Slope', 't': 'How fast it changes.', 'more': 'Shrink the run to zero for the exact slope.'},
        {'s': [['e', '📏'], ['t', 'xⁿ → n xⁿ⁻¹', {'b': 1}]], 'h': 'Rules', 't': 'Power, product, quotient.', 'more': 'eˣ stays eˣ, ln x becomes 1/x.'},
        {'s': [['e', '⛓️'], ['t', 'dy/dx = dy/du × du/dx', {'b': 1}]], 'h': 'Chain rule', 't': 'Outside slope times inside slope.', 'more': 'Backpropagation is this, over and over.'},
        {'s': [['e', '📐'], ['b', [2, 4, 6, 8, 10]]], 'h': 'Integral', 't': 'Area under the curve.', 'more': 'Add thin strips, or use F(b) − F(a).'},
    ],
    'remember': 'The derivative is the slope of the tangent: the limit of rise over run as the run shrinks. Use the power, product, quotient and chain rules. Set f′ = 0 to find peaks and valleys, and the sign of f″ tells which is which. An integral adds up tiny pieces and is the area under the curve. Learning nudges each weight against the slope of the loss.',
}

REAL = [
    ['🚀', 'Rocket launches', 'Engineers integrate the thrust and fuel burn over time to predict speed and height, and differentiate the path to get acceleration.'],
    ['📈', 'Business pricing', 'Setting the derivative of profit with respect to price to zero finds the price that earns the most.'],
    ['🩺', 'Medicine doses', 'The area under the drug concentration curve (AUC) measures how much medicine the body actually received over time.'],
]

K.say('top', 'Welcome',
      'Calculus starts here. A derivative tells you how fast something is changing at this exact moment, and an integral adds up tiny pieces to get a total. Machine learning uses derivatives to decide which way to nudge every weight. Watch the secant line turn into a tangent, trace a slope as you drag along a curve, and fill an area with rectangles.',
      'Calculus यहाँ से शुरू होता है। Derivative बताता है कि कोई चीज़ इसी पल कितनी तेज़ी से बदल रही है, और integral छोटे टुकड़े जोड़कर कुल निकालता है। Machine learning derivatives से तय करता है कि हर weight को किस ओर खिसकाना है।',
      'Calculus ಇಲ್ಲಿಂದ ಆರಂಭ. Derivative ಈ ಕ್ಷಣದಲ್ಲಿ ಎಷ್ಟು ವೇಗವಾಗಿ ಬದಲಾಗುತ್ತಿದೆ ಎಂದು ಹೇಳುತ್ತದೆ, integral ಸಣ್ಣ ತುಂಡುಗಳನ್ನು ಕೂಡಿಸುತ್ತದೆ. Machine learning derivatives ಬಳಸಿ weights ಸರಿಪಡಿಸುತ್ತದೆ.',
      'Calculus ଏଠାରୁ ଆରମ୍ଭ। Derivative କହେ ଏହି ମୁହୂର୍ତ୍ତରେ କେତେ ଶୀଘ୍ର ବଦଳୁଛି, integral ଛୋଟ ଖଣ୍ଡ ଯୋଗ କରେ। Machine learning derivatives ରେ weights ଠିକ୍ କରେ।',
      'هنا يبدأ التفاضل والتكامل. المشتقة تخبرك بسرعة تغير الشيء في هذه اللحظة بالضبط، والتكامل يجمع قطعًا صغيرة ليعطي المجموع. يستخدم التعلم الآلي المشتقات ليقرر اتجاه تعديل كل وزن.',
      'Hier beginnt die Analysis. Eine Ableitung sagt, wie schnell sich etwas genau in diesem Moment ändert, und ein Integral addiert winzige Stücke zu einer Summe. Maschinelles Lernen nutzt Ableitungen, um zu entscheiden, in welche Richtung jedes Gewicht geschoben wird.')
K.say('rate', 'Rate of change',
      'The average rate of change is rise over run between two points. Slide the second point towards the first and the slope settles on one number, the derivative. It is the speedometer reading at one exact moment.',
      'Average rate of change दो बिंदुओं के बीच rise बटा run है। दूसरे बिंदु को पहले की ओर खिसकाएँ तो slope एक संख्या पर टिक जाता है, यही derivative है।',
      'Average rate of change ಎರಡು ಬಿಂದುಗಳ ನಡುವೆ rise ಭಾಗಿಸು run. ಎರಡನೇ ಬಿಂದುವನ್ನು ಹತ್ತಿರ ತಂದರೆ slope ಒಂದು ಸಂಖ್ಯೆಗೆ ನೆಲೆಸುತ್ತದೆ, ಅದೇ derivative.',
      'Average rate of change ଦୁଇ ବିନ୍ଦୁ ମଧ୍ୟରେ rise ଭାଗ run। ଦ୍ୱିତୀୟ ବିନ୍ଦୁକୁ ପାଖକୁ ଆଣିଲେ slope ଗୋଟିଏ ସଂଖ୍ୟାରେ ସ୍ଥିର ହୁଏ, ତାହା derivative।',
      'معدل التغير المتوسط هو الارتفاع على المسافة بين نقطتين. حرك النقطة الثانية نحو الأولى فيستقر الميل على عدد واحد، وهو المشتقة.',
      'Die mittlere Änderungsrate ist Anstieg durch Strecke zwischen zwei Punkten. Schiebe den zweiten Punkt zum ersten, dann pendelt sich die Steigung auf eine Zahl ein, die Ableitung.')
K.say('limit', 'Limits',
      'A limit is the value a formula approaches as the input gets close to a number. The derivative is the limit of the difference quotient as h goes to zero. Computers estimate it with a small h, and the central difference is the most accurate simple way.',
      'Limit वह मान है जिसके पास formula पहुँचता है जब input किसी संख्या के क़रीब जाता है। Derivative difference quotient की limit है जब h शून्य की ओर जाए। Central difference सबसे सटीक सरल तरीका है।',
      'Limit ಎಂದರೆ input ಒಂದು ಸಂಖ್ಯೆಗೆ ಹತ್ತಿರವಾದಾಗ formula ಸಮೀಪಿಸುವ ಮೌಲ್ಯ. Derivative ಎಂದರೆ h ಸೊನ್ನೆಗೆ ಹೋದಾಗ difference quotient ನ limit.',
      'Limit ହେଉଛି input ଏକ ସଂଖ୍ୟା ପାଖକୁ ଗଲେ formula ଯେଉଁ ମୂଲ୍ୟ ପାଖକୁ ଯାଏ। Derivative ହେଉଛି h ଶୂନ ଆଡ଼କୁ ଗଲେ difference quotient ର limit।',
      'النهاية هي القيمة التي تقترب منها الصيغة حين يقترب المدخل من عدد ما. المشتقة هي نهاية خارج قسمة الفرق حين تقترب h من الصفر، والفرق المركزي أدق طريقة بسيطة لتقديرها.',
      'Ein Grenzwert ist der Wert, dem sich eine Formel nähert, wenn die Eingabe einer Zahl nahekommt. Die Ableitung ist der Grenzwert des Differenzenquotienten für h gegen null. Der zentrale Differenzenquotient ist die genaueste einfache Schätzung.')
K.say('rules', 'Rules',
      'Bring the power down and lower it by one. Differentiate a sum term by term. For a product, left times slope of right plus right times slope of left. e to the x is its own derivative and the natural log of x has derivative one over x.',
      'Power को नीचे लाएँ और उसे एक घटाएँ। जोड़ को हर term अलग से differentiate करें। Product के लिए product rule। e की घात x का derivative वही है और ln x का derivative एक बटा x है।',
      'Power ಅನ್ನು ಕೆಳಗೆ ತಂದು ಒಂದು ಕಡಿಮೆ ಮಾಡಿ. ಮೊತ್ತವನ್ನು term ಪ್ರಕಾರ differentiate ಮಾಡಿ. e ಘಾತ x ನ derivative ಅದೇ, ln x ನದು ಒಂದು ಭಾಗಿಸು x.',
      'Power କୁ ତଳକୁ ଆଣି ଏକ କମାନ୍ତୁ। ଯୋଗକୁ term ଅନୁସାରେ differentiate କରନ୍ତୁ। e ଘାତ x ର derivative ସେହି, ln x ର ଏକ ଭାଗ x।',
      'أنزل الأس واطرح منه واحدًا. اشتق المجموع حدًا حدًا. وللضرب استخدم قاعدة الضرب. مشتقة e أس x هي نفسها، ومشتقة اللوغاريتم الطبيعي واحد على x.',
      'Hole den Exponenten nach vorn und senke ihn um eins. Leite eine Summe Glied für Glied ab. Für Produkte gilt die Produktregel. e hoch x ist seine eigene Ableitung, und der natürliche Logarithmus hat die Ableitung eins durch x.')
K.say('chain', 'Chain rule',
      'For a function inside a function, multiply the outside slope by the inside slope. The sigmoid has the neat derivative sigma times one minus sigma, never more than a quarter. Backpropagation is the chain rule repeated from the loss back to every weight.',
      'Function के अंदर function हो तो बाहरी slope को अंदरूनी slope से गुणा करें। Sigmoid का derivative sigma गुणा एक घटा sigma है, जो कभी एक चौथाई से ज़्यादा नहीं। Backpropagation chain rule को बार बार लगाना है।',
      'Function ಒಳಗೆ function ಇದ್ದರೆ ಹೊರಗಿನ slope ಅನ್ನು ಒಳಗಿನ slope ನಿಂದ ಗುಣಿಸಿ. Sigmoid ನ derivative sigma ಗುಣಿಸು ಒಂದು ಕಳೆ sigma. Backpropagation chain rule ನ ಪುನರಾವರ್ತನೆ.',
      'Function ଭିତରେ function ଥିଲେ ବାହାର slope କୁ ଭିତର slope ରେ ଗୁଣନ କରନ୍ତୁ। Sigmoid ର derivative sigma ଗୁଣନ ଏକ ବିୟୋଗ sigma। Backpropagation chain rule ର ପୁନରାବୃତ୍ତି।',
      'للدالة داخل دالة اضرب ميل الخارج في ميل الداخل. مشتقة السيغمويد هي سيغما في واحد ناقص سيغما ولا تزيد عن الربع. والانتشار العكسي هو قاعدة السلسلة مكررة من الخسارة إلى كل وزن.',
      'Bei einer Funktion in einer Funktion multipliziert man die äußere mit der inneren Steigung. Die Sigmoidfunktion hat die Ableitung Sigma mal eins minus Sigma, nie mehr als ein Viertel. Backpropagation ist die Kettenregel, wiederholt vom Verlust zurück zu jedem Gewicht.')
K.say('shape', 'Peaks and valleys',
      'At a peak or a valley the slope is zero. The second derivative tells which one it is: positive means a valley shaped like a cup, negative means a peak shaped like a cap. A convex function has only one valley.',
      'Peak या valley पर slope शून्य होता है। Second derivative बताता है कौन सा है: positive मतलब कप जैसी valley, negative मतलब peak। Convex function में सिर्फ़ एक valley होती है।',
      'Peak ಅಥವಾ valley ಯಲ್ಲಿ slope ಸೊನ್ನೆ. Second derivative positive ಆದರೆ valley, negative ಆದರೆ peak. Convex function ಗೆ ಒಂದೇ valley.',
      'Peak କିମ୍ବା valley ରେ slope ଶୂନ। Second derivative positive ହେଲେ valley, negative ହେଲେ peak। Convex function ର କେବଳ ଗୋଟିଏ valley।',
      'عند القمة أو الوادي يكون الميل صفرًا. المشتقة الثانية تخبرك أيهما: موجبة تعني واديًا كالكوب، وسالبة تعني قمة. والدالة المحدبة لها وادٍ واحد فقط.',
      'An einem Gipfel oder Tal ist die Steigung null. Die zweite Ableitung sagt, was es ist: positiv bedeutet ein Tal wie eine Tasse, negativ einen Gipfel. Eine konvexe Funktion hat nur ein Tal.')
K.say('integral', 'Integrals',
      'An integral adds up tiny pieces. In a picture it is the area under a curve, which rectangles can estimate. The fundamental theorem says the exact area is F of b minus F of a, where F is a function whose slope is f.',
      'Integral छोटे टुकड़े जोड़ता है। चित्र में यह curve के नीचे का area है, जिसे rectangles से अनुमान लगा सकते हैं। Fundamental theorem कहता है सटीक area F of b घटा F of a है।',
      'Integral ಸಣ್ಣ ತುಂಡುಗಳನ್ನು ಕೂಡಿಸುತ್ತದೆ. ಚಿತ್ರದಲ್ಲಿ curve ಕೆಳಗಿನ area. ನಿಖರ area F of b ಕಳೆ F of a.',
      'Integral ଛୋଟ ଖଣ୍ଡ ଯୋଗ କରେ। ଚିତ୍ରରେ curve ତଳର area। ସଠିକ area F of b ବିୟୋଗ F of a।',
      'التكامل يجمع قطعًا صغيرة. في الرسم هو المساحة تحت المنحنى ويمكن تقديرها بالمستطيلات. والنظرية الأساسية تقول إن المساحة الدقيقة هي F عند b ناقص F عند a.',
      'Ein Integral addiert winzige Stücke. Im Bild ist es die Fläche unter einer Kurve, die man mit Rechtecken schätzen kann. Der Hauptsatz sagt, die genaue Fläche ist F von b minus F von a.')
K.say('ml', 'Learning with derivatives',
      'The derivative of the loss with respect to a weight says which way to move the weight. Positive slope, decrease the weight. Negative slope, increase it. Libraries compute these derivatives automatically with the chain rule.',
      'Weight के हिसाब से loss का derivative बताता है weight को किस ओर ले जाएँ। Positive slope हो तो weight घटाएँ, negative हो तो बढ़ाएँ। Libraries ये derivatives chain rule से अपने आप निकालती हैं।',
      'Weight ಗೆ ಸಂಬಂಧಿಸಿದ loss ನ derivative weight ಅನ್ನು ಯಾವ ಕಡೆ ಸರಿಸಬೇಕು ಎಂದು ಹೇಳುತ್ತದೆ. Positive ಆದರೆ ಕಡಿಮೆ, negative ಆದರೆ ಹೆಚ್ಚು ಮಾಡಿ.',
      'Weight ପ୍ରତି loss ର derivative କହେ weight କୁ କେଉଁ ଆଡ଼କୁ ନେବେ। Positive ହେଲେ କମାନ୍ତୁ, negative ହେଲେ ବଢ଼ାନ୍ତୁ।',
      'مشتقة الخسارة بالنسبة لوزن ما تخبرك باتجاه تحريكه. ميل موجب يعني إنقاص الوزن، وميل سالب يعني زيادته. والمكتبات تحسب هذه المشتقات تلقائيًا بقاعدة السلسلة.',
      'Die Ableitung des Verlusts nach einem Gewicht sagt, in welche Richtung das Gewicht wandern soll. Positive Steigung, Gewicht verkleinern. Negative Steigung, vergrößern. Bibliotheken berechnen diese Ableitungen automatisch mit der Kettenregel.')
K.say('practice', 'Practice',
      'Practice time. Find a tangent line, design the biggest box, find a square root with Newton\'s method, and measure the area under the bell curve with Simpson\'s rule.',
      'अभ्यास का समय। Tangent line निकालें, सबसे बड़ा box बनाएँ, Newton method से square root निकालें, और Simpson rule से bell curve के नीचे का area मापें।',
      'ಅಭ್ಯಾಸದ ಸಮಯ. Tangent line, ದೊಡ್ಡ box, Newton method ನಿಂದ square root, Simpson rule ನಿಂದ area.',
      'ଅଭ୍ୟାସ ସମୟ। Tangent line, ବଡ଼ box, Newton method ରେ square root, Simpson rule ରେ area।',
      'وقت التدريب. جد خط المماس، وصمم أكبر صندوق، واحسب جذرًا تربيعيًا بطريقة نيوتن، وقس المساحة تحت منحنى الجرس بقاعدة سيمبسون.',
      'Zeit zum Üben. Finde eine Tangente, entwirf die größte Schachtel, berechne eine Quadratwurzel mit dem Newton Verfahren und miss die Fläche unter der Glockenkurve mit der Simpsonregel.')

# ---------------------------------------------------------------- practice
K.practice('tangent', 'e', 'The tangent line to a cubic', 'p_tangent',
           '<p>Find the equation of the tangent line to f(x) = x³ − 2x at x = 2, then compare the curve and the line just either side of 2.</p>',
           'point: (2, 4), slope: 10\ntangent line: y = 10x + (-16)\nx = 1.9: curve 3.059, tangent 3.000\nx = 2.1: curve 5.061, tangent 5.000',
           'The tangent touches at (2, f(2)) and has slope f′(2).',
           '<p>f(2) = 8 − 4 = 4. By the power rule f′(x) = 3x² − 2, so f′(2) = 12 − 2 = 10. A line through (2, 4) with slope 10 is y − 4 = 10(x − 2), which is y = 10x − 16. Close to x = 2 the line and the curve agree to within about 0.06. This "the curve looks like its tangent up close" idea is what gradient descent relies on.</p>',
           'O(1)', 'O(1)')
K.practice('box', 'm', 'The biggest open box', 'p_box',
           '<p>Cut an x by x square from each corner of a 12 cm by 12 cm sheet and fold up the sides. Which x gives the largest volume? Try values, then solve V′(x) = 0.</p>',
           'by trying values: x = 2.0 gives V = 128.0\nV\'(x) = 0 at x = 2: V = 128\nV\'(x) = 0 at x = 6: V = 0',
           'V(x) = x(12 − 2x)². Use the product rule and the chain rule.',
           '<p>V′(x) = (12 − 2x)² + x × 2(12 − 2x)(−2) = (12 − 2x)[(12 − 2x) − 4x] = (12 − 2x)(12 − 6x). It is zero at x = 6 (the sheet is used up, V = 0) and at x = 2. V(2) = 2 × 8² = 128 cm³. The second derivative is negative there, so it is a maximum.</p>',
           'O(1)', 'O(1)')
K.practice('newton', 'h', "Square root of 2 with Newton's method", 'p_newton',
           "<p>Use Newton's method x ← x − f(x) ÷ f′(x) on f(x) = x² − 2, starting at x = 1. How many steps until six decimals stop changing?</p>",
           'step 1: x = 1.500000\nstep 2: x = 1.416667\nstep 3: x = 1.414216\nstep 4: x = 1.414214\nstep 5: x = 1.414214\ncheck: x * x = 2.000000',
           'The tangent at x crosses zero at x − f(x) ÷ f′(x).',
           '<p>Step 1: f(1) = −1 and f′(1) = 2, so x = 1 − (−1 ÷ 2) = 1.5. Step 2: f(1.5) = 0.25, f′(1.5) = 3, so x = 1.5 − 0.0833 = 1.41667. The number of correct digits roughly doubles each step, so after 4 steps it is right to 6 places. Second order optimisers in machine learning use the same idea with the second derivative.</p>',
           'O(steps)', 'O(1)')
K.practice('simpson', 'x', 'Area under the bell curve', 'p_simpson',
           "<p>Estimate the area under the standard normal curve from −1 to 1 with 10 strips, using the trapezoid rule and Simpson's rule. Compare both with the true value.</p>",
           "trapezoid rule: 0.681074\nSimpson's rule: 0.682698\ntrue value:     0.682689",
           "Simpson's rule weights the inside points 4, 2, 4, 2, … and multiplies by h ÷ 3.",
           "<p>The trapezoid rule joins neighbouring points with straight lines. Simpson's rule fits little parabolas through each three points, which follow a curve far better: its error here is about 0.00001 compared with 0.0016. The answer, 68.3%, is the famous share of normal data within one standard deviation of the mean (Chapter 10).</p>",
           'O(n)', 'O(1)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What does a derivative measure?', ['the total of a function', 'how fast a function is changing at a point', 'the largest value', 'the average of the inputs'], 1, 'Think of a speedometer.', 'It is the instant rate of change, the slope of the tangent line.')
K.quiz('e', 'What is the derivative of x⁵?', ['5x⁴', 'x⁴', '5x⁵', '4x⁵'], 0, 'Bring the power down, lower it by one.', 'Power rule: 5x⁴.')
K.quiz('e', 'What is the derivative of a constant like 7?', ['7', '1', '0', 'x'], 2, 'A flat line.', 'A constant never changes, so its slope is 0.')
K.quiz('e', 'Which function is its own derivative?', ['x²', 'ln x', 'eˣ', 'sin x'], 2, 'The special number e.', 'd/dx eˣ = eˣ.')
K.quiz('m', 'What is the derivative of ln x?', ['eˣ', '1/x', 'x', 'ln x / x'], 1, 'It is used in every log loss.', 'd/dx ln x = 1/x for x > 0.')
K.quiz('m', 'y = (2x + 3)⁵. What is dy/dx?', ['5(2x + 3)⁴', '10(2x + 3)⁴', '(2x + 3)⁴', '10x⁴'], 1, 'Outside slope times inside slope.', 'Outside: 5u⁴. Inside: 2. Multiply: 10(2x + 3)⁴.')
K.quiz('m', 'At a point f′(x) = 0 and f″(x) = 4. What is it?', ['a maximum', 'a minimum', 'an inflection point', 'nothing special'], 1, 'Positive second derivative bends like a cup.', 'Flat and curving up means a local minimum.')
K.quiz('m', 'What is the derivative of the sigmoid σ(z)?', ['σ(z)²', 'σ(z)(1 − σ(z))', '1 − σ(z)', 'e⁻ᶻ'], 1, 'Chain rule on (1 + e⁻ᶻ)⁻¹.', 'σ′ = σ(1 − σ), at most 0.25.')
K.quiz('m', 'What is ∫₀² 2x dx?', ['2', '4', '8', '1'], 1, 'x² has slope 2x.', 'F(x) = x², so F(2) − F(0) = 4 − 0 = 4.')
K.quiz('h', 'Using the product rule, what is d/dx (x² sin x)?', ['2x cos x', '2x sin x + x² cos x', 'x² cos x', '2x sin x − x² cos x'], 1, 'f′g + fg′.', '(x²)′ sin x + x² (sin x)′ = 2x sin x + x² cos x.')
K.quiz('h', 'Why do engineers compare analytic gradients with central differences?', ['to make training faster', 'to catch bugs in hand written derivatives', 'because analytic gradients are wrong', 'to pick the learning rate'], 1, 'Gradient checking.', 'If the two disagree, the backward pass has a bug.')
K.quiz('h', 'What is the derivative of ReLU(z) = max(0, z) for z = 3?', ['0', '1', '3', 'undefined'], 1, 'On the positive side it is the line y = z.', 'The slope of y = z is 1. For negative z it is 0.')
K.quiz('h', 'Why is a convex loss convenient for training?', ['it has no slope', 'any valley found is the lowest point', 'it is always zero', 'it needs no data'], 1, 'One bowl.', 'A convex function has a single minimum, so gradient descent cannot get stuck elsewhere.')
K.quiz('x', 'A deep net multiplies 10 sigmoid slopes, each at most 0.25. What is the largest possible product?', ['2.5', 'about 0.00000095', '0.25', '1'], 1, '0.25¹⁰.', '0.25¹⁰ ≈ 9.5 × 10⁻⁷. The gradient vanishes, which is why ReLU became the default.')
K.quiz('x', 'Which statement about the fundamental theorem of calculus is correct?', ['differentiation and integration are unrelated', 'integrating f from a to b equals F(b) − F(a) for any F with F′ = f', 'every function has an integral equal to its derivative', 'it only works for straight lines'], 1, 'Antiderivatives.', 'It links slopes and areas: the area is the change in an antiderivative.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What is the slope of f(x) = 5x³ at x = 2?', '60', 'Power rule, then put in x = 2.', [
    'Power rule: <span class="eq">f′(x) = 5 × 3x² = 15x²</span>',
    'Put in x = 2: <span class="eq">x² = 4</span>',
    '<span class="eq">15 × 4 = 60</span>',
], check=15 * 4)
K.calc('e', 'What is the average rate of change of f(x) = x² between x = 1 and x = 3?', '4', 'Rise over run.', [
    'Rise: <span class="eq">f(3) − f(1) = 9 − 1 = 8</span>',
    'Run: <span class="eq">3 − 1 = 2</span>',
    'Average rate: <span class="eq">8 ÷ 2 = 4</span>',
], check=(9 - 1) / 2)
K.calc('e', 'What is the derivative of f(x) = 7x + 4?', '7', 'A straight line has the same slope everywhere.', [
    'Derivative of 7x: <span class="eq">7 × 1 × x⁰ = 7</span>',
    'Derivative of the constant 4: <span class="eq">0</span>',
    'Total: <span class="eq">7 + 0 = 7</span>. The line rises 7 for every 1 step to the right.',
], check=7)
K.calc('e', 'f(x) = x⁴. What is f′(1)?', '4', 'Power rule.', [
    'Bring the 4 down and lower the power: <span class="eq">f′(x) = 4x³</span>',
    'At x = 1: <span class="eq">1³ = 1</span>',
    '<span class="eq">4 × 1 = 4</span>',
], check=4)
K.calc('m', 'Find the slope of f(x) = x² eˣ at x = 1. Give 2 decimal places.', '8.15', 'Product rule: f′g + fg′. Use e ≈ 2.71828.', [
    'f = x² so <span class="eq">f′ = 2x</span>. g = eˣ so <span class="eq">g′ = eˣ</span>',
    'Product rule: <span class="eq">(x² eˣ)′ = 2x eˣ + x² eˣ = eˣ(2x + x²)</span>',
    'At x = 1: <span class="eq">e × (2 + 1) = 3e</span>',
    '<span class="eq">3 × 2.71828 ≈ 8.15</span>',
], check=3 * 2.718281828, tol=0.01)
K.calc('m', 'What is the slope of y = (3x + 1)² at x = 1?', '24', 'Chain rule: outside slope × inside slope.', [
    'Inside: <span class="eq">u = 3x + 1</span>, slope <span class="eq">du/dx = 3</span>',
    'Outside: <span class="eq">y = u²</span>, slope <span class="eq">dy/du = 2u</span>',
    'At x = 1, <span class="eq">u = 4</span>, so <span class="eq">dy/dx = 2 × 4 × 3 = 24</span>',
], check=24)
K.calc('m', 'What is the slope of f(x) = x ÷ (x + 1) at x = 1?', '0.25', 'Quotient rule: (f′g − fg′) ÷ g².', [
    'Top f = x, <span class="eq">f′ = 1</span>. Bottom g = x + 1, <span class="eq">g′ = 1</span>',
    'Quotient rule: <span class="eq">(1 × (x + 1) − x × 1) ÷ (x + 1)² = 1 ÷ (x + 1)²</span>',
    'At x = 1: <span class="eq">1 ÷ 2² = 1 ÷ 4 = 0.25</span>',
], check=0.25)
K.calc('m', 'What is the slope of the sigmoid at z = 0?', '0.25', 'σ′ = σ(1 − σ).', [
    '<span class="eq">σ(0) = 1 ÷ (1 + e⁰) = 1 ÷ 2 = 0.5</span>',
    '<span class="eq">1 − σ(0) = 0.5</span>',
    '<span class="eq">σ′(0) = 0.5 × 0.5 = 0.25</span>. This is the steepest point of the S curve.',
], check=0.25)
K.calc('h', 'f(x) = x³ − 3x. What is the value of f at its local minimum?', '-2', 'Set f′ = 0, then use f″ to pick the valley.', [
    '<span class="eq">f′(x) = 3x² − 3 = 0</span> gives <span class="eq">x = ±1</span>',
    '<span class="eq">f″(x) = 6x</span>. At x = 1 it is 6, positive, so x = 1 is the valley.',
    '<span class="eq">f(1) = 1 − 3 = −2</span>',
], check=-2, alt=['−2'])
K.calc('h', 'What is ∫₀² 3x² dx?', '8', 'Find F with F′ = 3x², then F(2) − F(0).', [
    'Power rule backwards: <span class="eq">∫ 3x² dx = 3 × x³ ÷ 3 = x³</span>',
    'Top end: <span class="eq">F(2) = 2³ = 8</span>',
    'Bottom end: <span class="eq">F(0) = 0</span>',
    'Area: <span class="eq">8 − 0 = 8</span>',
], check=8)
K.calc('h', 'One Newton step for f(x) = x² − 2 from x = 1.5. What is the new x? Give 4 decimal places.', '1.4167', 'x_new = x − f(x) ÷ f′(x).', [
    '<span class="eq">f(1.5) = 2.25 − 2 = 0.25</span>',
    '<span class="eq">f′(x) = 2x</span>, so <span class="eq">f′(1.5) = 3</span>',
    '<span class="eq">x_new = 1.5 − 0.25 ÷ 3 = 1.5 − 0.0833 = 1.4167</span>',
    'The true √2 is 1.41421, so one step already gives 3 correct decimals.',
], check=1.5 - 0.25 / 3, tol=0.0001)
K.calc('x', 'Loss L = (w x − y)² with x = 2, y = 7, w = 1. What is dL/dw?', '-20', 'Chain rule: outside 2(wx − y), inside x.', [
    'Prediction: <span class="eq">wx = 1 × 2 = 2</span>, error <span class="eq">wx − y = 2 − 7 = −5</span>',
    'Outside slope: <span class="eq">2 × (−5) = −10</span>',
    'Inside slope: <span class="eq">d(wx − y)/dw = x = 2</span>',
    'Multiply: <span class="eq">−10 × 2 = −20</span>. Negative, so increase w to lower the loss.',
], check=-20, alt=['−20'])
K.calc('x', 'Softplus is s(x) = ln(1 + eˣ). What is its slope at x = 0?', '0.5', 'Chain rule. The answer is a famous function.', [
    'Outside: ln u has slope <span class="eq">1/u</span> with <span class="eq">u = 1 + eˣ</span>',
    'Inside: <span class="eq">du/dx = eˣ</span>',
    'Multiply: <span class="eq">s′(x) = eˣ ÷ (1 + eˣ)</span>, which is exactly the sigmoid σ(x)',
    'At x = 0: <span class="eq">1 ÷ (1 + 1) = 0.5</span>',
], check=0.5)

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;
  const FN = {
    sq: { f: x => x * x, d: x => 2 * x, dd: () => 2, xr: [-3, 3], yr: [-2, 9], name: 'x²', dn: '2x' },
    cube: { f: x => x * x * x - 3 * x, d: x => 3 * x * x - 3, dd: x => 6 * x, xr: [-2.6, 2.6], yr: [-5, 5], name: 'x³ − 3x', dn: '3x² − 3' },
    sin: { f: Math.sin, d: Math.cos, dd: x => -Math.sin(x), xr: [-4, 4], yr: [-2, 2], name: 'sin x', dn: 'cos x' },
    exp: { f: Math.exp, d: Math.exp, dd: Math.exp, xr: [-3, 2.2], yr: [-1, 9], name: 'eˣ', dn: 'eˣ' },
  };
  const segFns = [['sq', 'x²'], ['cube', 'x³ − 3x'], ['sin', 'sin x'], ['exp', 'eˣ']];

  /* ----- a secant line turns into the tangent ----- */
  W.secant = el => {
    const b = shell(el, 'From secant to tangent', 'Pick a curve and a point a. Press Play to shrink the gap h and watch the slope of the secant (orange) settle on the slope of the tangent (purple). You can also drag the h slider yourself.');
    b.innerHTML = `<div class="vz-row">${seg('fn', segFns, 'sq')}</div>
      <div class="mv-wrap"><div class="sc-plot"></div><div class="mv-side">${slider('a', 'a', -2, 2, 1, 0.1)}${slider('h', 'h', 0.01, 2, 2, 0.01)}<div class="mv-read sc-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let F = FN.sq, a = 1, h = 2;
    const draw = () => {
      const G = MV.frame(440, 360, F.xr, F.yr);
      const fa = F.f(a), fb = F.f(a + h), m = (fb - fa) / h, t = F.d(a);
      let s = MV.axes(G) + MV.curve(G, F.f);
      s += MV.curve(G, x => fa + m * (x - a), 'c2 thin') + MV.curve(G, x => fa + t * (x - a), 'c4 thin dash');
      s += MV.line(G, a, fa, a + h, fa, 'mv-res') + MV.line(G, a + h, fa, a + h, fb, 'mv-res');
      s += MV.dot(G, a, fa, 'p') + MV.dot(G, a + h, fb, 'o');
      $('.sc-plot', b).innerHTML = MV.svg(G, s, 'A curve with a secant line and a tangent line');
      $('.sc-out', b).innerHTML = `f(x) = ${F.name}<br>f(a) = ${MV.num(fa, 3)}, f(a + h) = ${MV.num(fb, 3)}<br><span style="color:var(--orange)">●</span> secant slope = ${frac(MV.num(fb - fa, 3), MV.num(h, 3))} = <b>${MV.num(m, 4)}</b><br><span style="color:var(--purple)">●</span> tangent slope f′(a) = ${F.dn} = <b>${MV.num(t, 4)}</b><br>gap = ${MV.num(Math.abs(m - t), 4)}`;
    };
    const frac = (p, q) => `(${p}) ÷ ${q}`;
    const P = Player($('.vz-p', b), k => { h = Math.max(0.01, Math.round(200 * Math.pow(0.7, k)) / 100); syncH(); draw(); }, 600);
    function syncH() { $('[data-sl="h"]', b).value = h; $('[data-slv="h"]', b).textContent = h; }
    wireSeg(b, 'fn', k => { F = FN[k]; draw(); });
    wireSlider(b, 'a', v => { a = v; draw(); });
    wireSlider(b, 'h', v => { P.pause(); h = v; draw(); });
    P.load(14, 0);
  };

  /* ----- drag along the curve and trace the derivative ----- */
  W.slope = el => {
    const b = shell(el, 'Drag along the curve, draw its slope', 'Drag the purple point, or press Play to sweep it from left to right. The top graph shows the tangent. The bottom graph plots the slope you measured at every x, which builds the curve of f′(x).');
    b.innerHTML = `<div class="vz-row">${seg('fn', segFns, 'cube')}</div>
      <div class="mv-wrap"><div><div class="sl-top"></div><div class="sl-bot"></div></div><div class="mv-side"><div class="mv-read sl-out" aria-live="polite"></div><div class="mv-legend"><span><i></i>f(x)</span><span><i class="p"></i>tangent</span><span><i class="g"></i>f′(x) traced</span></div></div></div><div class="vz-p"></div>`;
    let key = 'cube', F = FN.cube, x = -2, seen = [];
    let GT, GB, svgT;
    const N = 40;
    function build() {
      GT = MV.frame(440, 260, F.xr, F.yr);
      const ds = []; for (let k = 0; k <= 200; k++) { const t = F.xr[0] + (F.xr[1] - F.xr[0]) * k / 200; ds.push(F.d(t)); }
      const lo = Math.min(-1, ...ds), hi = Math.max(1, ...ds), pad = (hi - lo) * 0.1;
      GB = MV.frame(440, 200, F.xr, [lo - pad, hi + pad]);
      $('.sl-top', b).innerHTML = MV.svg(GT, '<g class="sl-g"></g>', 'The curve and its tangent line');
      svgT = $('.sl-top svg', b);
      MV.drag(svgT, GT, [{ set: (px) => { x = Math.round(px * 20) / 20; seen.push(x); } }], () => { P.pause(); draw(); });
    }
    function draw() {
      const y = F.f(x), m = F.d(x);
      let s = MV.axes(GT, { labels: false }) + MV.curve(GT, F.f) + MV.curve(GT, t => y + m * (t - x), 'c4 thin');
      s += `<circle class="mv-pt p big mv-drag" data-h="0" cx="${GT.sx(x)}" cy="${GT.sy(Math.max(GT.yr[0], Math.min(GT.yr[1], y)))}" r="10"/>`;
      $('.sl-g', svgT).innerHTML = s;
      const xs = [...new Set(seen.concat([x]))].sort((p, q) => p - q);
      let t = MV.axes(GB, { labels: false }) + MV.curve(GB, F.d, 'c3 thin dash');
      if (xs.length > 1) t += `<polyline class="mv-curve c3" points="${xs.map(u => GB.sx(u).toFixed(1) + ',' + GB.sy(F.d(u)).toFixed(1)).join(' ')}"/>`;
      t += MV.line(GB, x, 0, x, m, 'mv-v g') + MV.dot(GB, x, m, 'g');
      t += MV.text(GB, GB.xr[0], GB.yr[1], "f′(x)", { dx: 6, dy: 14 });
      $('.sl-bot', b).innerHTML = MV.svg(GB, t, 'The slope of the curve at each x');
      const dd = F.dd(x);
      const what = Math.abs(m) < 0.06 ? (dd > 0.05 ? '⬇️ Flat and bending up: a <b>valley</b> (local minimum).' : dd < -0.05 ? '⬆️ Flat and bending down: a <b>peak</b> (local maximum).' : 'Flat here.') : m > 0 ? '↗ Rising: the slope is positive.' : '↘ Falling: the slope is negative.';
      $('.sl-out', b).innerHTML = `x = ${MV.num(x)}<br>f(x) = ${MV.num(y, 3)}<br>slope f′(x) = <b>${MV.num(m, 3)}</b><br>bend f″(x) = ${MV.num(dd, 3)}<br>${what}`;
    }
    const P = Player($('.vz-p', b), k => { x = F.xr[0] + (F.xr[1] - F.xr[0]) * k / N; if (!k) seen = []; seen.push(x); draw(); }, 160);
    wireSeg(b, 'fn', k => { key = k; F = FN[k]; seen = []; build(); P.load(N + 1, 0); });
    build();
    P.load(N + 1, 0);
  };

  /* ----- rectangles under a curve ----- */
  W.riemann = el => {
    const b = shell(el, 'Fill the area with rectangles', 'Choose a rule and the number of strips. Press Play to add strips one at a time and watch the total close in on the exact area.');
    const RF = {
      sq: { f: x => x * x, F: x => x ** 3 / 3, a: 0, b: 3, yr: [-1, 10], name: 'x² from 0 to 3' },
      sin: { f: Math.sin, F: x => -Math.cos(x), a: 0, b: Math.PI, yr: [-0.3, 1.3], name: 'sin x from 0 to π' },
      bell: { f: x => Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI), F: null, a: -1, b: 1, yr: [-0.05, 0.5], name: 'bell curve from −1 to 1', exact: 0.682689 },
    };
    b.innerHTML = `<div class="vz-row">${seg('fn', [['sq', 'x²'], ['sin', 'sin x'], ['bell', 'Bell curve']], 'sq')}${seg('rule', [['left', 'Left'], ['right', 'Right'], ['mid', 'Midpoint'], ['trap', 'Trapezoid']], 'mid')}</div>
      <div class="mv-wrap"><div class="rm-plot"></div><div class="mv-side">${slider('n', 'strips', 1, 40, 6, 1)}<div class="mv-read rm-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let R = RF.sq, rule = 'mid', n = 6, shown = 6;
    function draw() {
      const G = MV.frame(440, 340, [R.a - (R.b - R.a) * 0.08, R.b + (R.b - R.a) * 0.08], R.yr);
      const w = (R.b - R.a) / n;
      let s = MV.axes(G), tot = 0;
      for (let i = 0; i < n; i++) {
        const x0 = R.a + i * w, x1 = x0 + w;
        const h0 = R.f(x0), h1 = R.f(x1), hm = R.f(x0 + w / 2);
        const area = rule === 'left' ? h0 * w : rule === 'right' ? h1 * w : rule === 'mid' ? hm * w : (h0 + h1) / 2 * w;
        if (i < shown) {
          tot += area;
          const pts = rule === 'trap' ? [[x0, 0], [x0, h0], [x1, h1], [x1, 0]] : (hh => [[x0, 0], [x0, hh], [x1, hh], [x1, 0]])(rule === 'left' ? h0 : rule === 'right' ? h1 : hm);
          s += `<polygon class="mv-bar ${i === shown - 1 ? 'o' : ''}" points="${pts.map(([p, q]) => G.sx(p).toFixed(1) + ',' + G.sy(q).toFixed(1)).join(' ')}"/>`;
        }
      }
      s += MV.curve(G, R.f, '', { from: G.xr[0], to: G.xr[1] });
      $('.rm-plot', b).innerHTML = MV.svg(G, s, 'Rectangles under a curve');
      const exact = R.F ? R.F(R.b) - R.F(R.a) : R.exact;
      $('.rm-out', b).innerHTML = `${R.name}<br>strip width Δx = ${MV.num(w, 4)}<br>strips added: ${shown} of ${n}<br>sum so far = <b>${MV.num(tot, 5)}</b><br>exact area = ${MV.num(exact, 5)}` + (shown === n ? `<br>error = ${MV.num(Math.abs(tot - exact), 5)}` : '');
    }
    const P = Player($('.vz-p', b), k => { shown = k; draw(); }, 350);
    const reset = () => { P.load(n + 1, n); };
    wireSeg(b, 'fn', k => { R = RF[k]; reset(); });
    wireSeg(b, 'rule', k => { rule = k; reset(); });
    wireSlider(b, 'n', v => { n = v; reset(); });
    reset();
  };
})();
'''

# ---------------------------------------------------------------- deeper explanations and extra animations
# Each lesson above gives the short version. DEEPER adds a slower, fuller explanation (and sometimes an
# animation) to the end of the lesson with the same id.
DEEPER = {
    'limit': deep('one sided limits, gaps and the shrinking h experiment', f'''
<p>A limit asks where a formula is heading, not what it equals at the point itself. Sometimes the formula cannot even be worked out at that point, and the limit still exists.</p>
{worked('The limit of (x² − 1) ÷ (x − 1) as x → 1', [
        'Plugging in x = 1 gives <span class="eq">0 ÷ 0</span>, which has no meaning.',
        'Factor the top: <span class="eq">x² − 1 = (x − 1)(x + 1)</span>',
        'For every x except 1 we can cancel: <span class="eq">(x − 1)(x + 1) ÷ (x − 1) = x + 1</span>',
        'As x gets close to 1, x + 1 gets close to <span class="eq">2</span>. Try x = 1.001: 2.001. Try x = 0.999: 1.999.',
        'So the limit is 2, even though the formula has a hole at exactly x = 1.'])}
<p>A limit only exists if you get the same answer coming from the left and from the right. The step function "0 for negatives, 1 for x ≥ 0" heads to 0 from the left and 1 from the right, so it has no limit at 0. A function with no jumps and no holes is called <b>continuous</b>, and continuous functions are the ones whose derivatives we can usually trust.</p>
<p>Now the computer experiment. The table below shrinks h by 10 each step and computes the derivative both ways, using real 64 bit numbers in your browser. At first the error falls, as calculus promises. Then, for very tiny h, rounding takes over (Chapter 1) and the error climbs again.</p>
{viz('limtable')}
{ml('This is exactly why gradient checking uses the central difference with h around 10⁻⁵. It is the sweet spot where the maths error is small and rounding has not yet wrecked the subtraction.')}
'''),
    'rules': deep('the rules at work: deriving the sigmoid slope', f'''
<p>The single most used derivative in classic neural networks is the slope of the sigmoid. It has a beautiful short form, and getting there uses the rules from this lesson.</p>
{worked('Show that σ′(z) = σ(z)(1 − σ(z))', [
        'Write <span class="eq">σ(z) = (1 + e⁻ᶻ)⁻¹</span>, a power of an inside function.',
        'Power rule and chain rule: <span class="eq">σ′(z) = −1 × (1 + e⁻ᶻ)⁻² × (−e⁻ᶻ) = e⁻ᶻ ÷ (1 + e⁻ᶻ)²</span>',
        'Split the fraction into two factors: <span class="eq">[1 ÷ (1 + e⁻ᶻ)] × [e⁻ᶻ ÷ (1 + e⁻ᶻ)]</span>',
        'The first factor is σ(z). The second is <span class="eq">1 − σ(z)</span>, because 1 − 1 ÷ (1 + e⁻ᶻ) = e⁻ᶻ ÷ (1 + e⁻ᶻ).',
        'So <span class="eq">σ′(z) = σ(z)(1 − σ(z))</span>. At z = 0 it is 0.5 × 0.5 = 0.25, its largest value.'])}
<p>Pick a function below and slide x along. The top picture shows f with its tangent line. The bottom picture draws the derivative f′. The height of the bottom curve at x is the slope of the top curve at x. Notice that f′ crosses zero exactly where f has a peak or a valley.</p>
{viz('derivplot')}
'''),
    'chain': deep('the chain rule with real numbers, and why deep chains fade', f'''
<p>The chain rule is easiest to trust once you have checked it with numbers. Take y = (3x + 1)³ at x = 1.</p>
{worked('Chain rule, then a numerical check', [
        'Inside: <span class="eq">u = 3x + 1 = 4</span>, with slope <span class="eq">du/dx = 3</span>',
        'Outside: <span class="eq">y = u³ = 64</span>, with slope <span class="eq">dy/du = 3u² = 48</span>',
        'Multiply: <span class="eq">dy/dx = 48 × 3 = 144</span>',
        'Check with a tiny step: at x = 1.001, u = 4.003 and y = 4.003³ ≈ 64.144. The rise 0.144 over the run 0.001 is <span class="eq">144</span> ✓'])}
<p>Now chain many links. If each link has slope 0.25 (the largest a sigmoid can give), ten links multiply to 0.25¹⁰ ≈ 0.00000095. A weight at the start of the chain gets almost no signal, so it barely learns. This is the <b>vanishing gradient</b> problem. If each link has slope 1.5 instead, ten links give 1.5¹⁰ ≈ 57.7, and the gradient <b>explodes</b>. Chapter 14 looks at the fixes.</p>
<p>Pick a chain below and move x. The widget shows the inside value, both local slopes, their product, and a numerical check of the answer.</p>
{viz('chainx')}
'''),
    'integral': deep('a full worked integral, negative areas and averages', f'''
{worked('∫ from 0 to 2 of x² dx, two ways', [
        'Antiderivative: raise the power and divide, <span class="eq">F(x) = x³ ÷ 3</span>',
        'Fundamental theorem: <span class="eq">F(2) − F(0) = 8 ÷ 3 − 0 ≈ 2.667</span>',
        'Strip check with 4 strips of width 0.5, heights at the midpoints 0.25, 0.75, 1.25, 1.75:',
        '<span class="eq">0.5 × (0.0625 + 0.5625 + 1.5625 + 3.0625) = 0.5 × 5.25 = 2.625</span>, already close to 2.667',
        'More strips get closer still. The animation above shows exactly this.'])}
<p>Two details trip people up. First, area <b>below</b> the x axis counts as negative. ∫ from −1 to 1 of x dx is 0, because the triangle below cancels the triangle above. Second, dividing an integral by the width of the interval gives the <b>average value</b> of the function there.</p>
{fx('Average value of f on [a, b]', f'{frac(1, "b − a")} ∫ₐᵇ f(x) dx', 'The average of x² from 0 to 2 is (8 ÷ 3) ÷ 2 = 4 ÷ 3 ≈ 1.333.')}
{ml('Expected value is an average, so for a continuous random variable it is an integral: E[X] = ∫ x f(x) dx. Most of these integrals are too hard to do by hand, so machine learning estimates them by averaging random samples instead (Monte Carlo, Chapter 15).')}
'''),
}
for _p in PARTS:
    _p['html'] += DEEPER.get(_p['id'], '')

VIZ_JS += r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;
  const sig = z => 1 / (1 + Math.exp(-z));

  /* ----- shrink h by 10 each step: forward versus central difference ----- */
  W.limtable = el => {
    const b = shell(el, 'Shrink h and watch the error', 'Each step makes h ten times smaller. The table compares the forward difference and the central difference with the true derivative, computed with real 64 bit numbers.');
    const FN = { sq: { f: x => x * x, a: 3, d: 6, n: 'x² at x = 3, true slope 6' }, ex: { f: Math.exp, a: 1, d: Math.E, n: 'eˣ at x = 1, true slope e' }, sn: { f: Math.sin, a: 1, d: Math.cos(1), n: 'sin x at x = 1, true slope cos 1' } };
    b.innerHTML = `<div class="vz-row">${seg('f', [['ex', 'eˣ'], ['sq', 'x²'], ['sn', 'sin x']], 'ex')}</div><div class="mv-wrap"><div class="lt-plot"></div><div class="mv-side"><div class="mv-legend"><span><i class="o"></i>forward error</span><span><i class="g"></i>central error</span></div><div class="mv-read lt-out" aria-live="polite"></div></div></div><div class="tw lt-tw"><table class="jt lt-tab"></table></div><div class="vz-p"></div>`;
    let F = FN.ex;
    const rows = () => { const r = []; for (let k = 1; k <= 15; k++) { const h = 10 ** -k, fw = (F.f(F.a + h) - F.f(F.a)) / h, ce = (F.f(F.a + h) - F.f(F.a - h)) / (2 * h); r.push({ k, fw, ce, ef: Math.abs(fw - F.d), ec: Math.abs(ce - F.d) }); } return r; };
    function show(t) {
      const R = rows(), G = MV.frame(420, 280, [0, 15.5], [-17, 1]);
      const lg = v => Math.max(-16.5, Math.log10(v || 1e-17));
      let s = MV.axes(G, { labels: false, xl: 'k in h = 10⁻ᵏ', yl: 'log₁₀ error' });
      for (let k = 3; k <= 12; k += 3) s += MV.text(G, k, 0, String(k), { dy: 14, anchor: 'middle', cls: 'sm' });
      for (let y = -15; y < 0; y += 5) s += MV.text(G, 0, y, String(y), { dx: 3, dy: 4, cls: "sm" });
      const pts = key => R.slice(0, t).map(r => G.sx(r.k).toFixed(1) + ',' + G.sy(lg(r[key])).toFixed(1)).join(' ');
      if (t > 1) s += `<polyline class="mv-v o" points="${pts('ef')}"/><polyline class="mv-v g" points="${pts('ec')}"/>`;
      R.slice(0, t).forEach(r => { s += MV.dot(G, r.k, lg(r.ef), 'o', 4) + MV.dot(G, r.k, lg(r.ec), 'g', 4); });
      $('.lt-plot', b).innerHTML = MV.svg(G, s, 'Error against step size');
      $('.lt-tab', b).innerHTML = '<tr><th>h</th><th>forward</th><th>central</th></tr>' + R.slice(0, t).map(r => `<tr><td>1e−${r.k}</td><td>${r.fw.toPrecision(10)}</td><td>${r.ce.toPrecision(10)}</td></tr>`).join('');
      let best = R[0]; R.forEach(r => { if (r.ec < best.ec) best = r; });
      $('.lt-out', b).innerHTML = `${F.n}<br>true value = <b>${F.d.toPrecision(10)}</b>` + (t ? `<br>now h = 1e−${t}` : '<br>Press Play to start.') + (t >= 15 ? `<br>best central h = 1e−${best.k}. Smaller h made it worse, because rounding swamped the tiny difference.` : '');
    }
    const P = Player($('.vz-p', b), show, 700);
    wireSeg(b, 'f', k => { F = FN[k]; P.load(16, 0); });
    P.load(16, 0);
  };

  /* ----- f on top, f′ underneath, sharing one x ----- */
  W.derivplot = el => {
    const b = shell(el, 'A function and its slope, side by side', 'Choose f. Move x or press Play. The tangent on the top graph has the slope shown by the dot on the bottom graph.');
    const FN = {
      cube: { f: x => x ** 3 - 3 * x, d: x => 3 * x * x - 3, xr: [-2.5, 2.5], yr: [-5, 5], dr: [-4, 12], n: 'x³ − 3x', dn: '3x² − 3' },
      sq: { f: x => x * x, d: x => 2 * x, xr: [-3, 3], yr: [-1, 9], dr: [-6, 6], n: 'x²', dn: '2x' },
      sin: { f: Math.sin, d: Math.cos, xr: [-6.3, 6.3], yr: [-1.5, 1.5], dr: [-1.5, 1.5], n: 'sin x', dn: 'cos x' },
      exp: { f: Math.exp, d: Math.exp, xr: [-3, 2], yr: [-0.5, 7.5], dr: [-0.5, 7.5], n: 'eˣ', dn: 'eˣ (itself)' },
      ln: { f: Math.log, d: x => 1 / x, xr: [0.05, 5], yr: [-3, 2], dr: [0, 5], n: 'ln x', dn: '1 ÷ x' },
      sig: { f: sig, d: x => sig(x) * (1 - sig(x)), xr: [-6, 6], yr: [-0.1, 1.1], dr: [-0.02, 0.3], n: 'σ(x)', dn: 'σ(x)(1 − σ(x))' },
    };
    b.innerHTML = `<div class="vz-row">${seg('f', [['cube', 'x³ − 3x'], ['sq', 'x²'], ['sin', 'sin x'], ['exp', 'eˣ'], ['ln', 'ln x'], ['sig', 'sigmoid']], 'cube')}</div><div class="mv-wrap"><div><div class="dp-top"></div><div class="dp-bot"></div></div><div class="mv-side">${slider('x', 'x (% of the range)', 0, 100, 30, 1)}<div class="mv-read dp-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let F = FN.cube, pct = 30;
    function draw() {
      const x = F.xr[0] + (F.xr[1] - F.xr[0]) * pct / 100, y = F.f(x), m = F.d(x);
      const G1 = MV.frame(440, 210, F.xr, F.yr), G2 = MV.frame(440, 170, F.xr, F.dr);
      let s1 = MV.axes(G1, { labels: false, yl: 'f(x)' }) + MV.curve(G1, F.f) + MV.curve(G1, t => y + m * (t - x), 'c2 thin', { from: x - 1.2, to: x + 1.2 }) + MV.dot(G1, x, y, 'o', 6);
      let s2 = MV.axes(G2, { labels: false, yl: 'f′(x)' }) + MV.curve(G2, F.d, 'c4') + MV.line(G2, x, F.dr[0], x, F.dr[1], 'mv-v k dash') + MV.dot(G2, x, Math.max(F.dr[0], Math.min(F.dr[1], m)), 'p', 6);
      $('.dp-top', b).innerHTML = MV.svg(G1, s1, 'The function with a tangent');
      $('.dp-bot', b).innerHTML = MV.svg(G2, s2, 'The derivative');
      $('.dp-out', b).innerHTML = `f(x) = ${F.n}<br>f′(x) = ${F.dn}<br>x = <b>${MV.num(x, 2)}</b><br>f(x) = <b>${MV.num(y, 3)}</b><br>slope f′(x) = <b>${MV.num(m, 3)}</b><br>` + (Math.abs(m) < 0.06 ? '➡️ Flat: a peak, a valley or a pause.' : m > 0 ? '↗ Rising here.' : '↘ Falling here.');
    }
    const P = Player($('.vz-p', b), t => { pct = t * 5; $('[data-sl="x"]', b).value = pct; $('[data-slv="x"]', b).textContent = pct; draw(); }, 350);
    wireSeg(b, 'f', k => { F = FN[k]; draw(); });
    wireSlider(b, 'x', v => { P.pause(); pct = v; draw(); });
    P.load(21, 6);
  };

  /* ----- the chain rule with numbers and a check ----- */
  W.chainx = el => {
    const b = shell(el, 'The chain rule, link by link', 'Choose a chain and an x. Press Play to reveal the inside value, the two local slopes, their product, and a numerical check.');
    const CH = {
      cube: { g: x => 3 * x + 1, dg: () => 3, f: u => u ** 3, df: u => 3 * u * u, n: 'y = (3x + 1)³', gn: 'u = 3x + 1', fn: 'y = u³', dgn: '3', dfn: '3u²' },
      sinsq: { g: x => x * x, dg: x => 2 * x, f: Math.sin, df: Math.cos, n: 'y = sin(x²)', gn: 'u = x²', fn: 'y = sin u', dgn: '2x', dfn: 'cos u' },
      sig: { g: x => 2 * x - 1, dg: () => 2, f: sig, df: u => sig(u) * (1 - sig(u)), n: 'y = σ(2x − 1)', gn: 'u = 2x − 1', fn: 'y = σ(u)', dgn: '2', dfn: 'σ(u)(1 − σ(u))' },
    };
    b.innerHTML = `<div class="vz-row">${seg('c', [['cube', '(3x + 1)³'], ['sinsq', 'sin(x²)'], ['sig', 'σ(2x − 1)']], 'cube')}</div><div class="mv-wrap"><div class="cx-plot"></div><div class="mv-side">${slider('x', 'x', -2, 2, 1, 0.1)}<div class="mv-read cx-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let C = CH.cube, x = 1, stage = 5;
    function draw() {
      const u = C.g(x), y = C.f(u), a = C.df(u), g = C.dg(x), d = a * g, h = 1e-5, num = (C.f(C.g(x + h)) - C.f(C.g(x - h))) / (2 * h);
      const ys = []; for (let k = 0; k <= 80; k++) ys.push(C.f(C.g(-2 + k / 20)));
      const lo = Math.min(...ys), hi = Math.max(...ys), pad = (hi - lo) * 0.1 || 1;
      const G = MV.frame(420, 300, [-2, 2], [lo - pad, hi + pad]);
      let s = MV.axes(G, { labels: false, xl: 'x', yl: 'y' }) + MV.curve(G, t => C.f(C.g(t)));
      if (stage >= 4) s += MV.curve(G, t => y + d * (t - x), 'c2 thin', { from: x - 0.5, to: x + 0.5 });
      s += MV.dot(G, x, y, 'o', 6);
      $('.cx-plot', b).innerHTML = MV.svg(G, s, 'The chained function');
      const L = [`${C.n}<br>x = <b>${MV.num(x, 2)}</b>`];
      if (stage >= 1) L.push(`inside: ${C.gn} = <b>${MV.num(u, 4)}</b>, y = <b>${MV.num(y, 4)}</b>`);
      if (stage >= 2) L.push(`outside slope dy/du = ${C.dfn} = <b>${MV.num(a, 4)}</b>`);
      if (stage >= 3) L.push(`inside slope du/dx = ${C.dgn} = <b>${MV.num(g, 4)}</b>`);
      if (stage >= 4) L.push(`chain: dy/dx = ${MV.num(a, 4)} × ${MV.num(g, 4)} = <span class="big">${MV.num(d, 4)}</span>`);
      if (stage >= 5) L.push(`numerical check: <b>${MV.num(num, 4)}</b> ✓`);
      $('.cx-out', b).innerHTML = L.join('<br>');
    }
    const P = Player($('.vz-p', b), t => { stage = t; draw(); }, 1000);
    wireSeg(b, 'c', k => { C = CH[k]; P.load(6, 5); });
    wireSlider(b, 'x', v => { x = v; draw(); });
    P.load(6, 5);
  };
})();
'''
CSS = r'''
.dp-top .mv-svg{max-height:240px; margin-bottom:6px} .dp-bot .mv-svg{max-height:200px}
.lt-tw{max-height:280px; overflow:auto}
.lt-tab td,.lt-tab th{font-family:var(--font-mono); font-size:13px}
'''

T = K.topic(
    slug='derivatives', topic='derivatives', prefix='mm06', short='Derivatives', emoji='📈',
    title='Derivatives and Integrals',
    module=('📉', 'Calculus', 'calculus', 'Derivatives, gradients, the chain rule and optimisation: the maths that lets a model learn from its mistakes.'),
    minutes=60,
    lead='A derivative is a speedometer for any function. Watch a secant line become a tangent, learn the rules that make derivatives quick, master the chain rule behind backpropagation, find peaks and valleys, and fill areas with rectangles to meet the integral.',
    desc='Calculus for machine learning: rate of change, limits, the derivative from first principles, power, product, quotient and chain rules, the sigmoid derivative, maxima and minima, convexity, integrals and numerical integration.',
    summary='Average and instant rate of change, limits and the difference quotient, numerical derivatives and gradient checking, the differentiation rules and table, the chain rule and the sigmoid derivative, critical points and the second derivative, convexity, Riemann sums, the fundamental theorem and how derivatives drive learning.',
    keywords=['derivative', 'slope', 'tangent', 'limit', 'power rule', 'product rule', 'quotient rule', 'chain rule', 'sigmoid derivative', 'second derivative', 'maximum', 'minimum', 'convex', 'integral', 'riemann sum', 'newton method'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
