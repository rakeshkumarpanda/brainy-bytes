# Chapter 7: functions of several variables, partial derivatives, the gradient, directional derivatives and
# linear approximation, the Jacobian and Hessian, the multivariable chain rule and backpropagation.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz, mat, vec, deep

K = Kit()

# ---------------------------------------------------------------- programs
K.code('partials', py=r'''
def f(x, y):
    return x * x * y + 3 * y


x, y, h = 2.0, 1.0, 1e-5
dfdx = (f(x + h, y) - f(x - h, y)) / (2 * h)   # move x only, keep y fixed
dfdy = (f(x, y + h) - f(x, y - h)) / (2 * h)   # move y only, keep x fixed
print(f"f(2, 1) = {f(x, y):.4f}")
print(f"df/dx: rule 2xy = {2 * x * y:.4f}, numbers say {dfdx:.4f}")
print(f"df/dy: rule x^2 + 3 = {x * x + 3:.4f}, numbers say {dfdy:.4f}")
''', js=r'''
function f(x, y) {
  return x * x * y + 3 * y;
}

const x = 2.0, y = 1.0, h = 1e-5;
const dfdx = (f(x + h, y) - f(x - h, y)) / (2 * h);   // move x only, keep y fixed
const dfdy = (f(x, y + h) - f(x, y - h)) / (2 * h);   // move y only, keep x fixed
console.log(`f(2, 1) = ${f(x, y).toFixed(4)}`);
console.log(`df/dx: rule 2xy = ${(2 * x * y).toFixed(4)}, numbers say ${dfdx.toFixed(4)}`);
console.log(`df/dy: rule x^2 + 3 = ${(x * x + 3).toFixed(4)}, numbers say ${dfdy.toFixed(4)}`);
''', ts=r'''
function f(x: number, y: number): number {
  return x * x * y + 3 * y;
}

const x: number = 2.0, y: number = 1.0, h: number = 1e-5;
const dfdx: number = (f(x + h, y) - f(x - h, y)) / (2 * h);   // move x only, keep y fixed
const dfdy: number = (f(x, y + h) - f(x, y - h)) / (2 * h);   // move y only, keep x fixed
console.log(`f(2, 1) = ${f(x, y).toFixed(4)}`);
console.log(`df/dx: rule 2xy = ${(2 * x * y).toFixed(4)}, numbers say ${dfdx.toFixed(4)}`);
console.log(`df/dy: rule x^2 + 3 = ${(x * x + 3).toFixed(4)}, numbers say ${dfdy.toFixed(4)}`);
''', java=r'''
public class Partials {
    static double f(double x, double y) {
        return x * x * y + 3 * y;
    }

    public static void main(String[] args) {
        double x = 2.0, y = 1.0, h = 1e-5;
        double dfdx = (f(x + h, y) - f(x - h, y)) / (2 * h);   // move x only, keep y fixed
        double dfdy = (f(x, y + h) - f(x, y - h)) / (2 * h);   // move y only, keep x fixed
        System.out.println(String.format("f(2, 1) = %.4f", f(x, y)));
        System.out.println(String.format("df/dx: rule 2xy = %.4f, numbers say %.4f", 2 * x * y, dfdx));
        System.out.println(String.format("df/dy: rule x^2 + 3 = %.4f, numbers say %.4f", x * x + 3, dfdy));
    }
}
''')

K.code('grad_field', py=r'''
import math


def grad(x, y):                           # f(x, y) = x^2 + 3y^2, a stretched bowl
    return [2 * x, 6 * y]


for x, y in [(1, 1), (2, 1), (-1, 0.5)]:
    g = grad(x, y)
    size = math.hypot(g[0], g[1])         # how steep the hill is here
    down = [-g[0] / size, -g[1] / size]   # the steepest way down, length 1
    print(f"at ({x:g}, {y:g}): gradient = [{g[0]:g}, {g[1]:g}], steepness = {size:.3f}, downhill = [{down[0]:.3f}, {down[1]:.3f}]")
''', js=r'''
function grad(x, y) {                     // f(x, y) = x^2 + 3y^2, a stretched bowl
  return [2 * x, 6 * y];
}

for (const [x, y] of [[1, 1], [2, 1], [-1, 0.5]]) {
  const g = grad(x, y);
  const size = Math.hypot(g[0], g[1]);    // how steep the hill is here
  const down = [-g[0] / size, -g[1] / size];   // the steepest way down, length 1
  console.log(`at (${x}, ${y}): gradient = [${g[0]}, ${g[1]}], steepness = ${size.toFixed(3)}, downhill = [${down[0].toFixed(3)}, ${down[1].toFixed(3)}]`);
}
''', ts=r'''
function grad(x: number, y: number): number[] {   // f(x, y) = x^2 + 3y^2, a stretched bowl
  return [2 * x, 6 * y];
}

for (const [x, y] of [[1, 1], [2, 1], [-1, 0.5]]) {
  const g: number[] = grad(x, y);
  const size: number = Math.hypot(g[0], g[1]);    // how steep the hill is here
  const down: number[] = [-g[0] / size, -g[1] / size];   // the steepest way down, length 1
  console.log(`at (${x}, ${y}): gradient = [${g[0]}, ${g[1]}], steepness = ${size.toFixed(3)}, downhill = [${down[0].toFixed(3)}, ${down[1].toFixed(3)}]`);
}
''', java=r'''
public class GradField {
    static double[] grad(double x, double y) {   // f(x, y) = x^2 + 3y^2, a stretched bowl
        return new double[]{2 * x, 6 * y};
    }

    static String n(double v) {
        return v == Math.rint(v) ? String.valueOf((long) v) : String.valueOf(v);
    }

    public static void main(String[] args) {
        double[][] pts = {{1, 1}, {2, 1}, {-1, 0.5}};
        for (double[] p : pts) {
            double[] g = grad(p[0], p[1]);
            double size = Math.hypot(g[0], g[1]);        // how steep the hill is here
            double[] down = {-g[0] / size, -g[1] / size}; // the steepest way down, length 1
            System.out.println("at (" + n(p[0]) + ", " + n(p[1]) + "): gradient = [" + n(g[0]) + ", " + n(g[1]) + "], "
                + String.format("steepness = %.3f, downhill = [%.3f, %.3f]", size, down[0], down[1]));
        }
    }
}
''')

K.code('graph_bp', py=r'''
# f = (x + y) * z as a tiny computational graph
x, y, z = 2, -1, 3
q = x + y                                 # forward pass, node 1
f = q * z                                 # forward pass, node 2
print("forward: q =", q, " f =", f)
df_df = 1                                 # backward pass starts with 1 at the output
df_dq = z * df_df                         # multiply node: the gradient is the other input
df_dz = q * df_df
df_dx = 1 * df_dq                         # add node: copies the gradient to both inputs
df_dy = 1 * df_dq
print("backward: df/dx =", df_dx, " df/dy =", df_dy, " df/dz =", df_dz)
''', js=r'''
// f = (x + y) * z as a tiny computational graph
const x = 2, y = -1, z = 3;
const q = x + y;                          // forward pass, node 1
const f = q * z;                          // forward pass, node 2
console.log("forward: q =", q, " f =", f);
const df_df = 1;                          // backward pass starts with 1 at the output
const df_dq = z * df_df;                  // multiply node: the gradient is the other input
const df_dz = q * df_df;
const df_dx = 1 * df_dq;                  // add node: copies the gradient to both inputs
const df_dy = 1 * df_dq;
console.log("backward: df/dx =", df_dx, " df/dy =", df_dy, " df/dz =", df_dz);
''', ts=r'''
// f = (x + y) * z as a tiny computational graph
const x: number = 2, y: number = -1, z: number = 3;
const q: number = x + y;                  // forward pass, node 1
const f: number = q * z;                  // forward pass, node 2
console.log("forward: q =", q, " f =", f);
const df_df: number = 1;                  // backward pass starts with 1 at the output
const df_dq: number = z * df_df;          // multiply node: the gradient is the other input
const df_dz: number = q * df_df;
const df_dx: number = 1 * df_dq;          // add node: copies the gradient to both inputs
const df_dy: number = 1 * df_dq;
console.log("backward: df/dx =", df_dx, " df/dy =", df_dy, " df/dz =", df_dz);
''', java=r'''
public class GraphBackprop {
    public static void main(String[] args) {
        // f = (x + y) * z as a tiny computational graph
        int x = 2, y = -1, z = 3;
        int q = x + y;                            // forward pass, node 1
        int f = q * z;                            // forward pass, node 2
        System.out.println("forward: q = " + q + "  f = " + f);
        int df_df = 1;                            // backward pass starts with 1 at the output
        int df_dq = z * df_df;                    // multiply node: the gradient is the other input
        int df_dz = q * df_df;
        int df_dx = 1 * df_dq;                    // add node: copies the gradient to both inputs
        int df_dy = 1 * df_dq;
        System.out.println("backward: df/dx = " + df_dx + "  df/dy = " + df_dy + "  df/dz = " + df_dz);
    }
}
''')

K.code('neuron_grad', py=r'''
import math


def forward(w, b, x, y):
    z = w[0] * x[0] + w[1] * x[1] + b     # weighted sum
    a = 1 / (1 + math.exp(-z))            # sigmoid
    return z, a, (a - y) ** 2             # squared error loss


x, y = [1.0, 2.0], 1.0
w, b = [0.5, -0.3], 0.1
z, a, L = forward(w, b, x, y)
print(f"z = {z:.4f}, a = {a:.4f}, loss = {L:.4f}")
dL_da = 2 * (a - y)                       # chain rule, link by link
da_dz = a * (1 - a)
dL_dz = dL_da * da_dz
grads = [dL_dz * x[0], dL_dz * x[1], dL_dz]   # dz/dw_i = x_i and dz/db = 1
print(f"dL/dw1 = {grads[0]:.4f}, dL/dw2 = {grads[1]:.4f}, dL/db = {grads[2]:.4f}")
h = 1e-5                                  # gradient check on w1
up = forward([w[0] + h, w[1]], b, x, y)[2]
dn = forward([w[0] - h, w[1]], b, x, y)[2]
print(f"numerical dL/dw1 = {(up - dn) / (2 * h):.4f}")
''', js=r'''
function forward(w, b, x, y) {
  const z = w[0] * x[0] + w[1] * x[1] + b;   // weighted sum
  const a = 1 / (1 + Math.exp(-z));          // sigmoid
  return [z, a, (a - y) ** 2];               // squared error loss
}

const x = [1.0, 2.0], y = 1.0;
const w = [0.5, -0.3], b = 0.1;
const [z, a, L] = forward(w, b, x, y);
console.log(`z = ${z.toFixed(4)}, a = ${a.toFixed(4)}, loss = ${L.toFixed(4)}`);
const dL_da = 2 * (a - y);                // chain rule, link by link
const da_dz = a * (1 - a);
const dL_dz = dL_da * da_dz;
const grads = [dL_dz * x[0], dL_dz * x[1], dL_dz];   // dz/dw_i = x_i and dz/db = 1
console.log(`dL/dw1 = ${grads[0].toFixed(4)}, dL/dw2 = ${grads[1].toFixed(4)}, dL/db = ${grads[2].toFixed(4)}`);
const h = 1e-5;                           // gradient check on w1
const up = forward([w[0] + h, w[1]], b, x, y)[2];
const dn = forward([w[0] - h, w[1]], b, x, y)[2];
console.log(`numerical dL/dw1 = ${((up - dn) / (2 * h)).toFixed(4)}`);
''', ts=r'''
function forward(w: number[], b: number, x: number[], y: number): [number, number, number] {
  const z: number = w[0] * x[0] + w[1] * x[1] + b;   // weighted sum
  const a: number = 1 / (1 + Math.exp(-z));          // sigmoid
  return [z, a, (a - y) ** 2];                       // squared error loss
}

const x: number[] = [1.0, 2.0], y: number = 1.0;
const w: number[] = [0.5, -0.3], b: number = 0.1;
const [z, a, L] = forward(w, b, x, y);
console.log(`z = ${z.toFixed(4)}, a = ${a.toFixed(4)}, loss = ${L.toFixed(4)}`);
const dL_da: number = 2 * (a - y);        // chain rule, link by link
const da_dz: number = a * (1 - a);
const dL_dz: number = dL_da * da_dz;
const grads: number[] = [dL_dz * x[0], dL_dz * x[1], dL_dz];   // dz/dw_i = x_i and dz/db = 1
console.log(`dL/dw1 = ${grads[0].toFixed(4)}, dL/dw2 = ${grads[1].toFixed(4)}, dL/db = ${grads[2].toFixed(4)}`);
const h: number = 1e-5;                   // gradient check on w1
const up: number = forward([w[0] + h, w[1]], b, x, y)[2];
const dn: number = forward([w[0] - h, w[1]], b, x, y)[2];
console.log(`numerical dL/dw1 = ${((up - dn) / (2 * h)).toFixed(4)}`);
''', java=r'''
public class NeuronGrad {
    static double[] forward(double[] w, double b, double[] x, double y) {
        double z = w[0] * x[0] + w[1] * x[1] + b;   // weighted sum
        double a = 1 / (1 + Math.exp(-z));          // sigmoid
        return new double[]{z, a, (a - y) * (a - y)};   // squared error loss
    }

    public static void main(String[] args) {
        double[] x = {1.0, 2.0};
        double y = 1.0;
        double[] w = {0.5, -0.3};
        double b = 0.1;
        double[] r = forward(w, b, x, y);
        double a = r[1];
        System.out.println(String.format("z = %.4f, a = %.4f, loss = %.4f", r[0], a, r[2]));
        double dL_da = 2 * (a - y);               // chain rule, link by link
        double da_dz = a * (1 - a);
        double dL_dz = dL_da * da_dz;
        double[] grads = {dL_dz * x[0], dL_dz * x[1], dL_dz};   // dz/dw_i = x_i and dz/db = 1
        System.out.println(String.format("dL/dw1 = %.4f, dL/dw2 = %.4f, dL/db = %.4f", grads[0], grads[1], grads[2]));
        double h = 1e-5;                          // gradient check on w1
        double up = forward(new double[]{w[0] + h, w[1]}, b, x, y)[2];
        double dn = forward(new double[]{w[0] - h, w[1]}, b, x, y)[2];
        System.out.println(String.format("numerical dL/dw1 = %.4f", (up - dn) / (2 * h)));
    }
}
''')

K.code('p_plane', py=r'''
import math


def f(x, y):
    return math.sqrt(x * x + y * y)       # distance from the origin


x0, y0 = 3, 4
gx, gy = x0 / f(x0, y0), y0 / f(x0, y0)   # gradient of the distance
print(f"f(3, 4) = {f(x0, y0):.4f}, gradient = [{gx:.4f}, {gy:.4f}]")
dx, dy = 0.1, -0.1
guess = f(x0, y0) + gx * dx + gy * dy     # tangent plane: f + grad . step
print(f"linear guess for f(3.1, 3.9) = {guess:.4f}")
print(f"true value                  = {f(x0 + dx, y0 + dy):.4f}")
''', js=r'''
function f(x, y) {
  return Math.sqrt(x * x + y * y);        // distance from the origin
}

const x0 = 3, y0 = 4;
const gx = x0 / f(x0, y0), gy = y0 / f(x0, y0);   // gradient of the distance
console.log(`f(3, 4) = ${f(x0, y0).toFixed(4)}, gradient = [${gx.toFixed(4)}, ${gy.toFixed(4)}]`);
const dx = 0.1, dy = -0.1;
const guess = f(x0, y0) + gx * dx + gy * dy;      // tangent plane: f + grad . step
console.log(`linear guess for f(3.1, 3.9) = ${guess.toFixed(4)}`);
console.log(`true value                  = ${f(x0 + dx, y0 + dy).toFixed(4)}`);
''', ts=r'''
function f(x: number, y: number): number {
  return Math.sqrt(x * x + y * y);        // distance from the origin
}

const x0: number = 3, y0: number = 4;
const gx: number = x0 / f(x0, y0), gy: number = y0 / f(x0, y0);   // gradient of the distance
console.log(`f(3, 4) = ${f(x0, y0).toFixed(4)}, gradient = [${gx.toFixed(4)}, ${gy.toFixed(4)}]`);
const dx: number = 0.1, dy: number = -0.1;
const guess: number = f(x0, y0) + gx * dx + gy * dy;   // tangent plane: f + grad . step
console.log(`linear guess for f(3.1, 3.9) = ${guess.toFixed(4)}`);
console.log(`true value                  = ${f(x0 + dx, y0 + dy).toFixed(4)}`);
''', java=r'''
public class PracticePlane {
    static double f(double x, double y) {
        return Math.sqrt(x * x + y * y);      // distance from the origin
    }

    public static void main(String[] args) {
        double x0 = 3, y0 = 4;
        double gx = x0 / f(x0, y0), gy = y0 / f(x0, y0);   // gradient of the distance
        System.out.println(String.format("f(3, 4) = %.4f, gradient = [%.4f, %.4f]", f(x0, y0), gx, gy));
        double dx = 0.1, dy = -0.1;
        double guess = f(x0, y0) + gx * dx + gy * dy;      // tangent plane: f + grad . step
        System.out.println(String.format("linear guess for f(3.1, 3.9) = %.4f", guess));
        System.out.println(String.format("true value                  = %.4f", f(x0 + dx, y0 + dy)));
    }
}
''')

K.code('p_hessian', py=r'''
def hessian(f, x, y, h=1e-3):
    fxx = (f(x + h, y) - 2 * f(x, y) + f(x - h, y)) / h ** 2
    fyy = (f(x, y + h) - 2 * f(x, y) + f(x, y - h)) / h ** 2
    fxy = (f(x + h, y + h) - f(x + h, y - h) - f(x - h, y + h) + f(x - h, y - h)) / (4 * h * h)
    return fxx, fxy, fyy


shapes = [("x^2 + xy + 2y^2", lambda x, y: x * x + x * y + 2 * y * y),
          ("x^2 - y^2", lambda x, y: x * x - y * y)]
for label, f in shapes:
    a, b, d = hessian(f, 0.0, 0.0)
    det = a * d - b * b
    kind = "minimum (bowl)" if det > 0 and a > 0 else "maximum (cap)" if det > 0 else "saddle"
    print(f"{label}: H = [[{a:.3f}, {b:.3f}], [{b:.3f}, {d:.3f}]], det = {det:.3f}, {kind}")
''', js=r'''
function hessian(f, x, y, h = 1e-3) {
  const fxx = (f(x + h, y) - 2 * f(x, y) + f(x - h, y)) / h ** 2;
  const fyy = (f(x, y + h) - 2 * f(x, y) + f(x, y - h)) / h ** 2;
  const fxy = (f(x + h, y + h) - f(x + h, y - h) - f(x - h, y + h) + f(x - h, y - h)) / (4 * h * h);
  return [fxx, fxy, fyy];
}

const shapes = [["x^2 + xy + 2y^2", (x, y) => x * x + x * y + 2 * y * y],
                ["x^2 - y^2", (x, y) => x * x - y * y]];
for (const [label, f] of shapes) {
  const [a, b, d] = hessian(f, 0.0, 0.0);
  const det = a * d - b * b;
  const kind = det > 0 && a > 0 ? "minimum (bowl)" : det > 0 ? "maximum (cap)" : "saddle";
  console.log(`${label}: H = [[${a.toFixed(3)}, ${b.toFixed(3)}], [${b.toFixed(3)}, ${d.toFixed(3)}]], det = ${det.toFixed(3)}, ${kind}`);
}
''', ts=r'''
type F2 = (x: number, y: number) => number;

function hessian(f: F2, x: number, y: number, h: number = 1e-3): number[] {
  const fxx: number = (f(x + h, y) - 2 * f(x, y) + f(x - h, y)) / h ** 2;
  const fyy: number = (f(x, y + h) - 2 * f(x, y) + f(x, y - h)) / h ** 2;
  const fxy: number = (f(x + h, y + h) - f(x + h, y - h) - f(x - h, y + h) + f(x - h, y - h)) / (4 * h * h);
  return [fxx, fxy, fyy];
}

const shapes: [string, F2][] = [["x^2 + xy + 2y^2", (x, y) => x * x + x * y + 2 * y * y],
                                ["x^2 - y^2", (x, y) => x * x - y * y]];
for (const [label, f] of shapes) {
  const [a, b, d] = hessian(f, 0.0, 0.0);
  const det: number = a * d - b * b;
  const kind: string = det > 0 && a > 0 ? "minimum (bowl)" : det > 0 ? "maximum (cap)" : "saddle";
  console.log(`${label}: H = [[${a.toFixed(3)}, ${b.toFixed(3)}], [${b.toFixed(3)}, ${d.toFixed(3)}]], det = ${det.toFixed(3)}, ${kind}`);
}
''', java=r'''
import java.util.function.DoubleBinaryOperator;

public class PracticeHessian {
    static double[] hessian(DoubleBinaryOperator f, double x, double y, double h) {
        double fxx = (f.applyAsDouble(x + h, y) - 2 * f.applyAsDouble(x, y) + f.applyAsDouble(x - h, y)) / (h * h);
        double fyy = (f.applyAsDouble(x, y + h) - 2 * f.applyAsDouble(x, y) + f.applyAsDouble(x, y - h)) / (h * h);
        double fxy = (f.applyAsDouble(x + h, y + h) - f.applyAsDouble(x + h, y - h) - f.applyAsDouble(x - h, y + h) + f.applyAsDouble(x - h, y - h)) / (4 * h * h);
        return new double[]{fxx, fxy, fyy};
    }

    public static void main(String[] args) {
        String[] labels = {"x^2 + xy + 2y^2", "x^2 - y^2"};
        DoubleBinaryOperator[] fs = {(x, y) -> x * x + x * y + 2 * y * y, (x, y) -> x * x - y * y};
        for (int i = 0; i < fs.length; i++) {
            double[] H = hessian(fs[i], 0.0, 0.0, 1e-3);
            double a = H[0], b = H[1], d = H[2];
            double det = a * d - b * b;
            String kind = det > 0 && a > 0 ? "minimum (bowl)" : det > 0 ? "maximum (cap)" : "saddle";
            System.out.println(String.format("%s: H = [[%.3f, %.3f], [%.3f, %.3f]], det = %.3f, %s", labels[i], a, b, b, d, det, kind));
        }
    }
}
''')

K.code('p_linreg_grad', py=r'''
# loss L(w) = mean of (Xw - y)^2, its gradient is (2/n) X^T (Xw - y)
X = [[1, 1], [1, 2], [1, 3]]              # a column of 1s for the bias, then x
y = [2, 3, 5]
w = [0.0, 1.0]
n = len(X)


def loss(w):
    return sum((r[0] * w[0] + r[1] * w[1] - t) ** 2 for r, t in zip(X, y)) / n


err = [r[0] * w[0] + r[1] * w[1] - t for r, t in zip(X, y)]
grad = [2 / n * sum(X[i][j] * err[i] for i in range(n)) for j in range(2)]
print("errors:", err)
print(f"loss = {loss(w):.4f}, gradient = [{grad[0]:.4f}, {grad[1]:.4f}]")
h = 1e-5
num = [(loss([w[0] + h, w[1]]) - loss([w[0] - h, w[1]])) / (2 * h),
       (loss([w[0], w[1] + h]) - loss([w[0], w[1] - h])) / (2 * h)]
print(f"numerical gradient = [{num[0]:.4f}, {num[1]:.4f}]")
''', js=r'''
// loss L(w) = mean of (Xw - y)^2, its gradient is (2/n) X^T (Xw - y)
const X = [[1, 1], [1, 2], [1, 3]];       // a column of 1s for the bias, then x
const y = [2, 3, 5];
const w = [0.0, 1.0];
const n = X.length;

function loss(w) {
  return X.reduce((s, r, i) => s + (r[0] * w[0] + r[1] * w[1] - y[i]) ** 2, 0) / n;
}

const err = X.map((r, i) => r[0] * w[0] + r[1] * w[1] - y[i]);
const grad = [0, 1].map(j => 2 / n * X.reduce((s, r, i) => s + r[j] * err[i], 0));
console.log("errors:", "[" + err.map(e => e.toFixed(1)).join(", ") + "]");
console.log(`loss = ${loss(w).toFixed(4)}, gradient = [${grad[0].toFixed(4)}, ${grad[1].toFixed(4)}]`);
const h = 1e-5;
const num = [(loss([w[0] + h, w[1]]) - loss([w[0] - h, w[1]])) / (2 * h),
             (loss([w[0], w[1] + h]) - loss([w[0], w[1] - h])) / (2 * h)];
console.log(`numerical gradient = [${num[0].toFixed(4)}, ${num[1].toFixed(4)}]`);
''', ts=r'''
// loss L(w) = mean of (Xw - y)^2, its gradient is (2/n) X^T (Xw - y)
const X: number[][] = [[1, 1], [1, 2], [1, 3]];   // a column of 1s for the bias, then x
const y: number[] = [2, 3, 5];
const w: number[] = [0.0, 1.0];
const n: number = X.length;

function loss(w: number[]): number {
  return X.reduce((s, r, i) => s + (r[0] * w[0] + r[1] * w[1] - y[i]) ** 2, 0) / n;
}

const err: number[] = X.map((r, i) => r[0] * w[0] + r[1] * w[1] - y[i]);
const grad: number[] = [0, 1].map(j => 2 / n * X.reduce((s, r, i) => s + r[j] * err[i], 0));
console.log("errors:", "[" + err.map(e => e.toFixed(1)).join(", ") + "]");
console.log(`loss = ${loss(w).toFixed(4)}, gradient = [${grad[0].toFixed(4)}, ${grad[1].toFixed(4)}]`);
const h: number = 1e-5;
const num: number[] = [(loss([w[0] + h, w[1]]) - loss([w[0] - h, w[1]])) / (2 * h),
                       (loss([w[0], w[1] + h]) - loss([w[0], w[1] - h])) / (2 * h)];
console.log(`numerical gradient = [${num[0].toFixed(4)}, ${num[1].toFixed(4)}]`);
''', java=r'''
public class PracticeLinRegGrad {
    // loss L(w) = mean of (Xw - y)^2, its gradient is (2/n) X^T (Xw - y)
    static double[][] X = {{1, 1}, {1, 2}, {1, 3}};   // a column of 1s for the bias, then x
    static double[] y = {2, 3, 5};
    static int n = X.length;

    static double loss(double[] w) {
        double s = 0;
        for (int i = 0; i < n; i++) s += Math.pow(X[i][0] * w[0] + X[i][1] * w[1] - y[i], 2);
        return s / n;
    }

    public static void main(String[] args) {
        double[] w = {0.0, 1.0};
        double[] err = new double[n];
        for (int i = 0; i < n; i++) err[i] = X[i][0] * w[0] + X[i][1] * w[1] - y[i];
        double[] grad = new double[2];
        for (int j = 0; j < 2; j++) {
            for (int i = 0; i < n; i++) grad[j] += X[i][j] * err[i];
            grad[j] *= 2.0 / n;
        }
        System.out.println("errors: " + java.util.Arrays.toString(err));
        System.out.println(String.format("loss = %.4f, gradient = [%.4f, %.4f]", loss(w), grad[0], grad[1]));
        double h = 1e-5;
        double n0 = (loss(new double[]{w[0] + h, w[1]}) - loss(new double[]{w[0] - h, w[1]})) / (2 * h);
        double n1 = (loss(new double[]{w[0], w[1] + h}) - loss(new double[]{w[0], w[1] - h})) / (2 * h);
        System.out.println(String.format("numerical gradient = [%.4f, %.4f]", n0, n1));
    }
}
''')

K.code('p_twolayer', py=r'''
x, y = [1.0, 2.0], 1.0
W1 = [[0.1, 0.2], [-0.3, 0.4]]
b1 = [0.0, 0.1]
w2, b2 = [0.7, -0.2], 0.05
# forward pass
pre = [W1[i][0] * x[0] + W1[i][1] * x[1] + b1[i] for i in range(2)]
hid = [max(0.0, p) for p in pre]          # ReLU
out = w2[0] * hid[0] + w2[1] * hid[1] + b2
loss = (out - y) ** 2
print(f"hidden = [{hid[0]:.4f}, {hid[1]:.4f}], output = {out:.4f}, loss = {loss:.4f}")
# backward pass, from the loss to every weight
d_out = 2 * (out - y)
d_w2 = [d_out * hid[0], d_out * hid[1]]
d_hid = [d_out * w2[0], d_out * w2[1]]
d_pre = [d_hid[i] * (1.0 if pre[i] > 0 else 0.0) for i in range(2)]   # ReLU passes or blocks
d_W1 = [[d_pre[i] * x[j] for j in range(2)] for i in range(2)]
print(f"dL/db2 = {d_out:.4f}, dL/dw2 = [{d_w2[0]:.4f}, {d_w2[1]:.4f}]")
print(f"dL/dW1 = [[{d_W1[0][0]:.4f}, {d_W1[0][1]:.4f}], [{d_W1[1][0]:.4f}, {d_W1[1][1]:.4f}]]")
''', js=r'''
const x = [1.0, 2.0], y = 1.0;
const W1 = [[0.1, 0.2], [-0.3, 0.4]];
const b1 = [0.0, 0.1];
const w2 = [0.7, -0.2], b2 = 0.05;
// forward pass
const pre = [0, 1].map(i => W1[i][0] * x[0] + W1[i][1] * x[1] + b1[i]);
const hid = pre.map(p => Math.max(0, p)); // ReLU
const out = w2[0] * hid[0] + w2[1] * hid[1] + b2;
const loss = (out - y) ** 2;
console.log(`hidden = [${hid[0].toFixed(4)}, ${hid[1].toFixed(4)}], output = ${out.toFixed(4)}, loss = ${loss.toFixed(4)}`);
// backward pass, from the loss to every weight
const d_out = 2 * (out - y);
const d_w2 = [d_out * hid[0], d_out * hid[1]];
const d_hid = [d_out * w2[0], d_out * w2[1]];
const d_pre = [0, 1].map(i => d_hid[i] * (pre[i] > 0 ? 1 : 0));   // ReLU passes or blocks
const d_W1 = [0, 1].map(i => [0, 1].map(j => d_pre[i] * x[j]));
console.log(`dL/db2 = ${d_out.toFixed(4)}, dL/dw2 = [${d_w2[0].toFixed(4)}, ${d_w2[1].toFixed(4)}]`);
console.log(`dL/dW1 = [[${d_W1[0][0].toFixed(4)}, ${d_W1[0][1].toFixed(4)}], [${d_W1[1][0].toFixed(4)}, ${d_W1[1][1].toFixed(4)}]]`);
''', ts=r'''
const x: number[] = [1.0, 2.0], y: number = 1.0;
const W1: number[][] = [[0.1, 0.2], [-0.3, 0.4]];
const b1: number[] = [0.0, 0.1];
const w2: number[] = [0.7, -0.2], b2: number = 0.05;
// forward pass
const pre: number[] = [0, 1].map(i => W1[i][0] * x[0] + W1[i][1] * x[1] + b1[i]);
const hid: number[] = pre.map(p => Math.max(0, p));   // ReLU
const out: number = w2[0] * hid[0] + w2[1] * hid[1] + b2;
const loss: number = (out - y) ** 2;
console.log(`hidden = [${hid[0].toFixed(4)}, ${hid[1].toFixed(4)}], output = ${out.toFixed(4)}, loss = ${loss.toFixed(4)}`);
// backward pass, from the loss to every weight
const d_out: number = 2 * (out - y);
const d_w2: number[] = [d_out * hid[0], d_out * hid[1]];
const d_hid: number[] = [d_out * w2[0], d_out * w2[1]];
const d_pre: number[] = [0, 1].map(i => d_hid[i] * (pre[i] > 0 ? 1 : 0));   // ReLU passes or blocks
const d_W1: number[][] = [0, 1].map(i => [0, 1].map(j => d_pre[i] * x[j]));
console.log(`dL/db2 = ${d_out.toFixed(4)}, dL/dw2 = [${d_w2[0].toFixed(4)}, ${d_w2[1].toFixed(4)}]`);
console.log(`dL/dW1 = [[${d_W1[0][0].toFixed(4)}, ${d_W1[0][1].toFixed(4)}], [${d_W1[1][0].toFixed(4)}, ${d_W1[1][1].toFixed(4)}]]`);
''', java=r'''
public class PracticeTwoLayer {
    public static void main(String[] args) {
        double[] x = {1.0, 2.0};
        double y = 1.0;
        double[][] W1 = {{0.1, 0.2}, {-0.3, 0.4}};
        double[] b1 = {0.0, 0.1};
        double[] w2 = {0.7, -0.2};
        double b2 = 0.05;
        // forward pass
        double[] pre = new double[2], hid = new double[2];
        for (int i = 0; i < 2; i++) {
            pre[i] = W1[i][0] * x[0] + W1[i][1] * x[1] + b1[i];
            hid[i] = Math.max(0.0, pre[i]);           // ReLU
        }
        double out = w2[0] * hid[0] + w2[1] * hid[1] + b2;
        double loss = (out - y) * (out - y);
        System.out.println(String.format("hidden = [%.4f, %.4f], output = %.4f, loss = %.4f", hid[0], hid[1], out, loss));
        // backward pass, from the loss to every weight
        double d_out = 2 * (out - y);
        double[] d_w2 = {d_out * hid[0], d_out * hid[1]};
        double[][] d_W1 = new double[2][2];
        for (int i = 0; i < 2; i++) {
            double d_pre = d_out * w2[i] * (pre[i] > 0 ? 1.0 : 0.0);   // ReLU passes or blocks
            for (int j = 0; j < 2; j++) d_W1[i][j] = d_pre * x[j];
        }
        System.out.println(String.format("dL/db2 = %.4f, dL/dw2 = [%.4f, %.4f]", d_out, d_w2[0], d_w2[1]));
        System.out.println(String.format("dL/dW1 = [[%.4f, %.4f], [%.4f, %.4f]]", d_W1[0][0], d_W1[0][1], d_W1[1][0], d_W1[1][1]));
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('partial', '🎚️', 'Partial derivatives: one knob at a time', f'''
<p>Real things depend on many inputs. A house price depends on its size <b>and</b> its age. A model loss depends on millions of weights. A <b>partial derivative</b> asks how the output changes when you turn <b>one</b> input and hold every other input still.</p>
{fx('Partial derivative', f'{frac("∂f", "∂x")} = slope of f when only x moves', 'The curly ∂ means "partial". Treat every other letter as a fixed number, then use the ordinary rules from Chapter 6.')}
{viz('slice')}
{worked('Partials of f(x, y) = x²y + 3y at the point (2, 1)', [
        'For ∂f/∂x, treat y as a number: x²y has slope <span class="eq">2x × y</span>, and 3y is a constant with slope 0. So <span class="eq">∂f/∂x = 2xy</span>',
        'For ∂f/∂y, treat x as a number: x²y has slope <span class="eq">x²</span>, and 3y has slope 3. So <span class="eq">∂f/∂y = x² + 3</span>',
        'At (2, 1): <span class="eq">∂f/∂x = 2 × 2 × 1 = 4</span> and <span class="eq">∂f/∂y = 4 + 3 = 7</span>',
        'Meaning: a small step in y changes f about 7/4 times as much as the same step in x.'])}
{code('partials', 'Partial derivatives by rule and by numbers')}
{life('A baker finds that cake sales rise by 30 per week for each 1 degree warmer day (with price fixed), and fall by 50 for each extra rupee (with temperature fixed). Those two numbers are partial derivatives of sales.')}
''', kw=['partial derivative', 'multivariable function', 'hold constant', '∂f/∂x', 'slice']),

    part('gradient', '🧗', 'The gradient: the steepest way uphill', f'''
<p>Collect all the partial derivatives into one vector and you get the <b>gradient</b>, written ∇f (said "grad f" or "del f"). It is the most important object in machine learning.</p>
{fx('Gradient', f'∇f = {vec(["∂f/∂x₁", "∂f/∂x₂", "⋮", "∂f/∂xₙ"])}', 'It points in the direction of steepest increase. Its length says how steep that climb is. Minus the gradient is the steepest way down.')}
{viz('gradfield')}
{table(['Fact about ∇f', 'Why it matters'], [
        ['points straight uphill', 'so −∇f points straight downhill, the way to reduce a loss'],
        ['is perpendicular to the contour lines', 'contours are paths of equal height, and uphill is at right angles to them'],
        ['has length 0 at peaks, valleys and saddles', 'a zero gradient means training has stopped moving'],
        ['has one entry per input', 'a model with 7 billion weights has a gradient with 7 billion entries'],
    ])}
{code('grad_field', 'Gradient, steepness and the downhill direction at three points')}
{trick('Picture standing on a hillside in fog. You cannot see the valley, but you can feel which way the ground tilts under your feet. That tilt is the gradient, and gradient descent is taking a small step the other way.')}
''', kw=['gradient', 'nabla', '∇f', 'steepest ascent', 'steepest descent', 'contour lines', 'level curves']),

    part('approx', '📐', 'Directional derivatives and linear approximation', f'''
<p>The gradient answers "how fast does f change if I step in <b>any</b> direction u?" Just take a dot product. And near a point, every smooth surface looks almost flat, so a <b>tangent plane</b> predicts nearby values.</p>
{fxs(fx('Directional derivative', 'D<sub>u</sub> f = ∇f · u', 'u is a unit vector. It is largest when u points along ∇f, equal to ‖∇f‖, and zero along a contour.'),
         fx('Linear (first order) approximation', 'f(x + Δ) ≈ f(x) + ∇f(x) · Δ', 'The tangent plane. Good for small steps, which is why learning rates are kept small.'))}
{worked('Estimate √(3.1² + 3.9²) without a calculator', [
        'Let <span class="eq">f(x, y) = √(x² + y²)</span>. At (3, 4): <span class="eq">f = 5</span>',
        'Gradient: <span class="eq">∇f = [x/f, y/f] = [3/5, 4/5] = [0.6, 0.8]</span>',
        'Step: <span class="eq">Δ = [0.1, −0.1]</span>',
        'Estimate: <span class="eq">5 + 0.6 × 0.1 + 0.8 × (−0.1) = 5 + 0.06 − 0.08 = 4.98</span>',
        'True value: <span class="eq">4.9820</span>. The flat plane guess is off by only 0.002.'])}
{code('p_plane', 'Tangent plane guess against the true value')}
{ml('Every gradient descent step trusts this linear approximation: the loss should drop by about ‖∇L‖² × learning rate. If the learning rate is too large, the step leaves the region where the surface looks flat, and the loss can go up instead.')}
''', kw=['directional derivative', 'tangent plane', 'linear approximation', 'first order taylor', 'dot product with gradient']),

    part('jacobian', '🧮', 'Jacobian and Hessian matrices', f'''
<p>Two matrices organise all the derivatives of many inputs at once.</p>
{fxs(fx('Jacobian (first derivatives of many outputs)', f'J = {mat([["∂f₁/∂x₁", "∂f₁/∂x₂"], ["∂f₂/∂x₁", "∂f₂/∂x₂"]])}', 'Row i holds the gradient of output i. For a layer z = Wx + b the Jacobian ∂z/∂x is just W.'),
         fx('Hessian (second derivatives of one output)', f'H = {mat([["∂²f/∂x²", "∂²f/∂x∂y"], ["∂²f/∂y∂x", "∂²f/∂y²"]])}', 'It describes the curvature of the surface. It is symmetric, because the order of differentiating does not matter for smooth f.'))}
{table(['Hessian at a flat point', 'Shape', 'Test for 2 inputs'], [
        ['all eigenvalues positive', 'bowl: a minimum', 'det H > 0 and ∂²f/∂x² > 0'],
        ['all eigenvalues negative', 'cap: a maximum', 'det H > 0 and ∂²f/∂x² < 0'],
        ['mixed signs', 'saddle: up one way, down another', 'det H < 0'],
    ])}
{worked('Classify the flat point of f(x, y) = x² + xy + 2y² at (0, 0)', [
        'Second partials: <span class="eq">∂²f/∂x² = 2</span>, <span class="eq">∂²f/∂y² = 4</span>, <span class="eq">∂²f/∂x∂y = 1</span>',
        'Hessian: <span class="eq">H = [[2, 1], [1, 4]]</span>',
        'Determinant: <span class="eq">2 × 4 − 1 × 1 = 7 > 0</span>, and the top left entry 2 > 0',
        'So (0, 0) is a minimum, the bottom of a bowl.'])}
{code('p_hessian', 'A numerical Hessian classifies a bowl and a saddle')}
{ml('In high dimensions most flat points of a neural network loss are <b>saddles</b>, not bad minima. Gradient descent with a little noise slides off them. The eigenvalues of the Hessian also set the largest safe learning rate, roughly 2 ÷ λmax.')}
''', kw=['jacobian', 'hessian', 'second partial derivatives', 'saddle point', 'curvature', 'second derivative test']),

    part('chain', '🔗', 'The chain rule on a computational graph', f'''
<p>Any formula can be drawn as a <b>computational graph</b>: input boxes flow through small operations (add, multiply, sigmoid) to the output. The forward pass computes values left to right. The backward pass sends gradients right to left, and each node multiplies by its own local slope. That is the multivariable chain rule.</p>
{fx('Multivariable chain rule', f'{frac("∂L", "∂x")} = Σ<sub>paths</sub> (product of local slopes along the path)', 'If x affects L through several routes, add up the contributions of every route.')}
{viz('backprop')}
{table(['Node', 'Forward', 'Backward rule'], [
        ['add: q = a + b', 'adds', 'passes the incoming gradient unchanged to both inputs'],
        ['multiply: q = a × b', 'multiplies', 'sends gradient × b to a, and gradient × a to b (swap)'],
        ['max: q = max(a, b)', 'picks the bigger', 'sends the whole gradient to the winner only, like ReLU'],
        ['sigmoid: q = σ(a)', 'squashes', 'multiplies the gradient by q(1 − q)'],
    ])}
{code('graph_bp', 'Forward and backward pass on f = (x + y) × z')}
{trick('Add nodes copy, multiply nodes swap, max nodes route, and every node multiplies by its local slope.')}
''', kw=['computational graph', 'multivariable chain rule', 'forward pass', 'backward pass', 'local gradient', 'add node', 'multiply node']),

    part('backprop', '🧠', 'Backpropagation through a neuron', f'''
<p>Now put it all together for one neuron. Inputs x = [1, 2], weights w = [0.5, −0.3], bias b = 0.1, a sigmoid, and the squared error loss against the target y = 1.</p>
{worked('Forward pass', [
        'Weighted sum: <span class="eq">z = 0.5 × 1 + (−0.3) × 2 + 0.1 = 0.5 − 0.6 + 0.1 = 0</span>',
        'Activation: <span class="eq">a = σ(0) = 0.5</span>',
        'Loss: <span class="eq">L = (a − y)² = (0.5 − 1)² = 0.25</span>'], 'The forward pass computes the prediction and the loss.')}
{worked('Backward pass', [
        'Loss to activation: <span class="eq">∂L/∂a = 2(a − y) = 2 × (−0.5) = −1</span>',
        'Activation to sum: <span class="eq">∂a/∂z = a(1 − a) = 0.5 × 0.5 = 0.25</span>',
        'Chain: <span class="eq">∂L/∂z = −1 × 0.25 = −0.25</span>',
        'Sum to each weight: <span class="eq">∂z/∂w₁ = x₁ = 1</span>, <span class="eq">∂z/∂w₂ = x₂ = 2</span>, <span class="eq">∂z/∂b = 1</span>',
        'Gradients: <span class="eq">∂L/∂w₁ = −0.25</span>, <span class="eq">∂L/∂w₂ = −0.5</span>, <span class="eq">∂L/∂b = −0.25</span>',
        'All negative, so every one of them should increase. w₂ gets the biggest push because its input x₂ = 2 is the largest.'], 'The backward pass multiplies local slopes from the loss back to each weight.')}
{code('neuron_grad', 'One neuron: forward, backward and a gradient check')}
{ml('Backpropagation costs about the same as two forward passes, no matter how many weights there are. Computing each partial derivative separately with finite differences would need one extra forward pass per weight, millions of times slower. This efficiency is what made deep learning practical.')}
''', kw=['backpropagation', 'neuron gradient', 'sigmoid neuron', 'gradient check', 'chain rule example', 'weights and bias gradients']),

    part('ml', '🤖', 'Gradients for whole datasets', f'''
<p>A real loss is the <b>average</b> over many examples, so its gradient is the average of the per example gradients. With matrices, the whole batch is done in one line.</p>
{fxs(fx('Mean squared error for linear regression', f'L(w) = {frac(1, "n")} ‖Xw − y‖²', 'X holds one row per example, w the weights, y the targets.'),
         fx('Its gradient', f'∇L = {frac(2, "n")} Xᵀ(Xw − y)', 'Errors weighted by each feature, then averaged. Setting it to zero gives the normal equations of Chapter 4.'))}
{worked('Gradient of the MSE with X = [[1, 1], [1, 2], [1, 3]], y = [2, 3, 5], w = [0, 1]', [
        'Predictions: <span class="eq">Xw = [0 + 1, 0 + 2, 0 + 3] = [1, 2, 3]</span>',
        'Errors: <span class="eq">Xw − y = [1 − 2, 2 − 3, 3 − 5] = [−1, −1, −2]</span>',
        'Xᵀ times errors: <span class="eq">[−1 − 1 − 2, −1 × 1 − 1 × 2 − 2 × 3] = [−4, −9]</span>',
        'Scale by 2/n = 2/3: <span class="eq">∇L = [−2.667, −6]</span>',
        'Both parts are negative, so both the bias and the slope should increase.'])}
{code('p_linreg_grad', 'Vectorised gradient checked against numbers')}
{table(['Term', 'Meaning'], [
        ['Batch gradient', 'average gradient over the whole dataset, accurate but slow'],
        ['Mini batch gradient', 'average over 32 to 1024 random examples, the standard choice'],
        ['Stochastic gradient', 'gradient from one example, very noisy but cheap'],
        ['Autograd', 'the library builds the computational graph and runs backprop for you'],
    ])}
{trick('Shapes must match: the gradient of a loss with respect to a weight matrix always has the same shape as that weight matrix.')}
''', kw=['vectorised gradient', 'mse gradient', 'Xᵀ(Xw − y)', 'mini batch', 'stochastic gradient', 'autograd']),
]

INFO = {
    'title': 'The gradient points uphill, backprop finds it',
    'panels': [
        {'s': [['e', '🎚️'], ['t', '∂f/∂x', {'b': 1}]], 'h': 'Partial', 't': 'Turn one knob, hold the rest.', 'more': 'Use the usual rules, treating other inputs as numbers.'},
        {'s': [['e', '🧗'], ['t', '∇f = [∂f/∂x, ∂f/∂y]', {'b': 1}]], 'h': 'Gradient', 't': 'Steepest way uphill.', 'more': '−∇f is the steepest way down.'},
        {'s': [['e', '🔗'], ['t', 'local slope × incoming gradient', {'b': 1}]], 'h': 'Chain rule', 't': 'Backward through the graph.', 'more': 'Add copies, multiply swaps, max routes.'},
        {'s': [['e', '🧠'], ['t', '∂L/∂w = ∂L/∂a · ∂a/∂z · ∂z/∂w', {'b': 1}]], 'h': 'Backprop', 't': 'All gradients in one sweep.', 'more': 'Costs about two forward passes.'},
    ],
    'remember': 'A partial derivative moves one input and freezes the others. The gradient collects them and points straight uphill, so minus the gradient is the way down. The Jacobian holds first derivatives of many outputs and the Hessian holds the curvature. Backpropagation is the chain rule run backwards through a computational graph.',
}

REAL = [
    ['⛰️', 'Hiking maps', 'Contour lines join points of equal height. The steepest path up a hill always cuts across them at right angles, which is the direction of the gradient.'],
    ['🌡️', 'Weather maps', 'Wind blows roughly from high pressure to low pressure. Forecasters read the pressure gradient on a map to estimate wind speed.'],
    ['🤖', 'Every neural network', 'Training any modern model, from a spam filter to a chat assistant, runs backpropagation to get the gradient for every weight on every step.'],
]

K.say('top', 'Welcome',
      'A model has many weights, so its loss is a surface over many directions. In this chapter you will slice that surface with partial derivatives, collect them into the gradient that points uphill, and run the chain rule backwards through a graph. That is backpropagation, the engine of deep learning.',
      'Model के कई weights होते हैं, इसलिए उसका loss कई दिशाओं वाली सतह है। इस अध्याय में आप partial derivatives से उस सतह को काटेंगे, उन्हें gradient में जोड़ेंगे जो ऊपर की ओर इशारा करता है, और graph पर chain rule उल्टा चलाएँगे। यही backpropagation है।',
      'Model ಗೆ ಅನೇಕ weights, ಹಾಗಾಗಿ loss ಅನೇಕ ದಿಕ್ಕುಗಳ ಮೇಲ್ಮೈ. Partial derivatives, gradient ಮತ್ತು backpropagation ಈ ಅಧ್ಯಾಯದಲ್ಲಿ.',
      'Model ର ଅନେକ weights, ତେଣୁ loss ଅନେକ ଦିଗର ପୃଷ୍ଠ। Partial derivatives, gradient ଓ backpropagation ଏହି ଅଧ୍ୟାୟରେ।',
      'للنموذج أوزان كثيرة، فخسارته سطح في اتجاهات كثيرة. في هذا الفصل تقطع هذا السطح بالمشتقات الجزئية، وتجمعها في التدرج الذي يشير صعودًا، وتشغل قاعدة السلسلة عكسيًا عبر الرسم البياني. هذا هو الانتشار العكسي.',
      'Ein Modell hat viele Gewichte, also ist sein Verlust eine Fläche über vielen Richtungen. In diesem Kapitel schneidest du diese Fläche mit partiellen Ableitungen, sammelst sie im Gradienten, der bergauf zeigt, und lässt die Kettenregel rückwärts durch einen Graphen laufen. Das ist Backpropagation.')
K.say('partial', 'Partial derivatives',
      'A partial derivative turns one input and holds every other input still. Treat the other letters as fixed numbers and use the usual rules. The animation slices the surface along one direction so you can see that slope.',
      'Partial derivative एक input बदलता है और बाक़ी सबको स्थिर रखता है। बाक़ी अक्षरों को स्थिर संख्या मानें और सामान्य नियम लगाएँ। Animation सतह को एक दिशा में काटकर वह slope दिखाता है।',
      'Partial derivative ಒಂದು input ಬದಲಿಸಿ ಉಳಿದವನ್ನು ಸ್ಥಿರ ಇಡುತ್ತದೆ. ಉಳಿದ ಅಕ್ಷರಗಳನ್ನು ಸ್ಥಿರ ಸಂಖ್ಯೆ ಎಂದು ಭಾವಿಸಿ.',
      'Partial derivative ଗୋଟିଏ input ବଦଳାଏ ଓ ବାକି ସବୁ ସ୍ଥିର ରଖେ। ବାକି ଅକ୍ଷରକୁ ସ୍ଥିର ସଂଖ୍ୟା ଭାବନ୍ତୁ।',
      'المشتقة الجزئية تغير مدخلًا واحدًا وتثبت البقية. عامل الحروف الأخرى كأعداد ثابتة واستخدم القواعد المعتادة.',
      'Eine partielle Ableitung dreht an einer Eingabe und hält alle anderen fest. Behandle die anderen Buchstaben als feste Zahlen und nutze die üblichen Regeln.')
K.say('gradient', 'The gradient',
      'The gradient is the vector of all partial derivatives. It points in the direction of steepest climb and is at right angles to the contour lines. Minus the gradient is the fastest way down, and that is the direction training moves the weights.',
      'Gradient सभी partial derivatives का vector है। यह सबसे तेज़ चढ़ाई की दिशा दिखाता है और contour lines के लंबवत होता है। Minus gradient सबसे तेज़ उतराई है, और training weights को उसी ओर ले जाती है।',
      'Gradient ಎಲ್ಲಾ partial derivatives ನ vector. ಅದು ಅತಿ ಕಡಿದಾದ ಏರಿಕೆಯ ದಿಕ್ಕು. Minus gradient ಇಳಿಯುವ ವೇಗದ ದಾರಿ.',
      'Gradient ସମସ୍ତ partial derivatives ର vector। ଏହା ସବୁଠୁ ଖାଡ଼ା ଚଢ଼ାଇର ଦିଗ। Minus gradient ତଳକୁ ଯିବାର ଶୀଘ୍ର ବାଟ।',
      'التدرج متجه كل المشتقات الجزئية، يشير إلى اتجاه أشد صعود ويكون عموديًا على خطوط الكنتور. سالب التدرج أسرع طريق للنزول، وهو الاتجاه الذي يحرك فيه التدريب الأوزان.',
      'Der Gradient ist der Vektor aller partiellen Ableitungen. Er zeigt in die Richtung des steilsten Anstiegs und steht senkrecht auf den Höhenlinien. Minus der Gradient ist der schnellste Weg nach unten, und dorthin bewegt das Training die Gewichte.')
K.say('approx', 'Linear approximation',
      'The rate of change in any direction is the gradient dotted with that direction. Near a point a smooth surface looks flat, so f at a nearby point is about f here plus the gradient dotted with the step.',
      'किसी भी दिशा में बदलाव की दर gradient और उस दिशा का dot product है। किसी बिंदु के पास smooth सतह समतल दिखती है, इसलिए पास का मान लगभग यहाँ का मान जमा gradient dot step है।',
      'ಯಾವುದೇ ದಿಕ್ಕಿನ ಬದಲಾವಣೆ ದರ gradient dot ಆ ದಿಕ್ಕು. ಹತ್ತಿರದಲ್ಲಿ ಮೇಲ್ಮೈ ಸಮತಟ್ಟು ಕಾಣುತ್ತದೆ.',
      'ଯେକୌଣସି ଦିଗର ପରିବର୍ତ୍ତନ ହାର gradient dot ସେହି ଦିଗ। ପାଖରେ ପୃଷ୍ଠ ସମତଳ ଦେଖାଯାଏ।',
      'معدل التغير في أي اتجاه هو الضرب النقطي للتدرج مع ذلك الاتجاه. قرب نقطة ما يبدو السطح الأملس مستويًا، فقيمة نقطة قريبة تساوي تقريبًا القيمة هنا زائد التدرج نقطي الخطوة.',
      'Die Änderungsrate in jede Richtung ist der Gradient mal diese Richtung im Skalarprodukt. Nahe einem Punkt sieht eine glatte Fläche flach aus, also ist f in der Nähe etwa f hier plus Gradient mal Schritt.')
K.say('jacobian', 'Jacobian and Hessian',
      'The Jacobian holds the first derivatives of many outputs, one gradient per row. The Hessian holds the second derivatives of one output and describes curvature. Positive eigenvalues mean a bowl, negative mean a cap, and mixed signs mean a saddle.',
      'Jacobian कई outputs के first derivatives रखता है, हर row में एक gradient। Hessian एक output के second derivatives रखता है और वक्रता बताता है। Positive eigenvalues मतलब कटोरा, negative मतलब टोपी, मिले जुले मतलब saddle।',
      'Jacobian ಅನೇಕ outputs ನ first derivatives. Hessian second derivatives, ವಕ್ರತೆ. Positive eigenvalues ಬಟ್ಟಲು, mixed ಆದರೆ saddle.',
      'Jacobian ଅନେକ outputs ର first derivatives। Hessian second derivatives, ବକ୍ରତା। Positive eigenvalues ବାଟି, mixed ହେଲେ saddle।',
      'مصفوفة جاكوبي تحمل المشتقات الأولى لمخرجات كثيرة، وهيسيان تحمل المشتقات الثانية وتصف الانحناء. القيم الذاتية الموجبة تعني وعاءً، والسالبة قبة، والمختلطة سرجًا.',
      'Die Jacobi Matrix enthält die ersten Ableitungen vieler Ausgaben, die Hesse Matrix die zweiten Ableitungen einer Ausgabe und beschreibt die Krümmung. Positive Eigenwerte bedeuten eine Schüssel, negative eine Kappe, gemischte einen Sattel.')
K.say('chain', 'Computational graphs',
      'Draw the formula as a graph. The forward pass computes values from left to right. The backward pass sends gradients from right to left, and each node multiplies by its own local slope. Add nodes copy the gradient and multiply nodes swap their inputs.',
      'Formula को graph की तरह बनाएँ। Forward pass बाएँ से दाएँ मान निकालता है। Backward pass दाएँ से बाएँ gradients भेजता है, और हर node अपनी local slope से गुणा करता है।',
      'Formula ಅನ್ನು graph ಆಗಿ ಬರೆಯಿರಿ. Forward pass ಎಡದಿಂದ ಬಲಕ್ಕೆ, backward pass ಬಲದಿಂದ ಎಡಕ್ಕೆ gradients ಕಳುಹಿಸುತ್ತದೆ.',
      'Formula କୁ graph ଭାବେ ଆଙ୍କନ୍ତୁ। Forward pass ବାମରୁ ଡାହାଣ, backward pass ଡାହାଣରୁ ବାମ gradients ପଠାଏ।',
      'ارسم الصيغة كرسم بياني. التمرير الأمامي يحسب القيم من اليسار إلى اليمين، والتمرير الخلفي يرسل التدرجات من اليمين إلى اليسار، وكل عقدة تضرب في ميلها المحلي.',
      'Zeichne die Formel als Graph. Der Vorwärtsdurchlauf berechnet Werte von links nach rechts. Der Rückwärtsdurchlauf schickt Gradienten von rechts nach links, und jeder Knoten multipliziert mit seiner lokalen Steigung.')
K.say('backprop', 'Backpropagation',
      'For one neuron, go forward to get the prediction and the loss. Then go backward: loss to activation, activation to weighted sum, weighted sum to each weight. Multiply the slopes along the way to get every gradient.',
      'एक neuron के लिए आगे जाकर prediction और loss निकालें। फिर पीछे जाएँ: loss से activation, activation से weighted sum, weighted sum से हर weight। रास्ते की slopes गुणा करें।',
      'ಒಂದು neuron ಗೆ forward ನಲ್ಲಿ prediction ಮತ್ತು loss. ನಂತರ backward ನಲ್ಲಿ slopes ಗುಣಿಸಿ ಪ್ರತಿ gradient.',
      'ଗୋଟିଏ neuron ପାଇଁ forward ରେ prediction ଓ loss। ତାପରେ backward ରେ slopes ଗୁଣନ କରି gradient।',
      'لعصبون واحد، تقدم لتحصل على التنبؤ والخسارة، ثم ارجع من الخسارة إلى التفعيل، ومن التفعيل إلى المجموع الموزون، ومنه إلى كل وزن، واضرب الميول على الطريق.',
      'Für ein Neuron gehst du vorwärts zu Vorhersage und Verlust. Dann rückwärts: Verlust zur Aktivierung, Aktivierung zur gewichteten Summe, Summe zu jedem Gewicht. Multipliziere die Steigungen unterwegs.')
K.say('ml', 'Whole datasets',
      'The loss of a dataset is an average, so its gradient is the average of the example gradients. For linear regression it is two over n times X transpose times the errors. Mini batches average over a few dozen examples at a time.',
      'Dataset का loss औसत है, इसलिए उसका gradient examples के gradients का औसत है। Linear regression के लिए यह दो बटा n गुणा X transpose गुणा errors है।',
      'Dataset ನ loss ಸರಾಸರಿ, ಹಾಗಾಗಿ gradient ಕೂಡ ಸರಾಸರಿ. Linear regression ಗೆ ಎರಡು ಭಾಗಿಸು n ಗುಣಿಸು X transpose ಗುಣಿಸು errors.',
      'Dataset ର loss ହାରାହାରି, ତେଣୁ gradient ମଧ୍ୟ ହାରାହାରି। Linear regression ପାଇଁ ଦୁଇ ଭାଗ n ଗୁଣନ X transpose ଗୁଣନ errors।',
      'خسارة مجموعة البيانات متوسط، فتدرجها متوسط تدرجات الأمثلة. للانحدار الخطي هو اثنان على n في X منقول في الأخطاء.',
      'Der Verlust eines Datensatzes ist ein Mittelwert, also ist sein Gradient der Mittelwert der Beispielgradienten. Für lineare Regression ist er zwei durch n mal X transponiert mal die Fehler.')
K.say('practice', 'Practice',
      'Practice time. Use a tangent plane, classify flat points with the Hessian, compute a vectorised gradient, and backpropagate through a two layer network by hand.',
      'अभ्यास का समय। Tangent plane लगाएँ, Hessian से flat points पहचानें, vectorised gradient निकालें, और दो layer network में हाथ से backpropagation करें।',
      'ಅಭ್ಯಾಸದ ಸಮಯ. Tangent plane, Hessian, vectorised gradient ಮತ್ತು ಎರಡು layer network backprop.',
      'ଅଭ୍ୟାସ ସମୟ। Tangent plane, Hessian, vectorised gradient ଓ ଦୁଇ layer network backprop।',
      'وقت التدريب. استخدم المستوى المماس، وصنف النقاط المستوية بمصفوفة هيسيان، واحسب تدرجًا متجهًا، وطبق الانتشار العكسي على شبكة من طبقتين يدويًا.',
      'Zeit zum Üben. Nutze eine Tangentialebene, klassifiziere flache Punkte mit der Hesse Matrix, berechne einen vektorisierten Gradienten und führe Backpropagation durch ein zweischichtiges Netz von Hand aus.')

# ---------------------------------------------------------------- practice
K.practice('plane', 'e', 'Guess a value with the tangent plane', 'p_plane',
           '<p>Use the gradient of f(x, y) = √(x² + y²) at (3, 4) to estimate f(3.1, 3.9), then compare with the true value.</p>',
           'f(3, 4) = 5.0000, gradient = [0.6000, 0.8000]\nlinear guess for f(3.1, 3.9) = 4.9800\ntrue value                  = 4.9820',
           '∂f/∂x = x ÷ f and ∂f/∂y = y ÷ f.',
           '<p>The gradient of the distance from the origin is the unit vector pointing away from the origin, here [0.6, 0.8]. The step [0.1, −0.1] is mostly sideways to that direction, so the distance hardly changes: 5 + 0.06 − 0.08 = 4.98. The true 4.9820 is very close because the step is small.</p>',
           'O(1)', 'O(1)')
K.practice('hessian', 'm', 'Bowl or saddle?', 'p_hessian',
           '<p>Build the Hessian at (0, 0) numerically for f = x² + xy + 2y² and g = x² − y², and classify each flat point with the determinant test.</p>',
           'x^2 + xy + 2y^2: H = [[2.000, 1.000], [1.000, 4.000]], det = 7.000, minimum (bowl)\nx^2 - y^2: H = [[2.000, 0.000], [0.000, -2.000]], det = -4.000, saddle',
           'f_xx ≈ (f(x + h) − 2f(x) + f(x − h)) ÷ h².',
           '<p>The second difference formula measures how the slope itself changes. For f, det H = 2 × 4 − 1 = 7 > 0 with a positive corner, so it is a bowl. For g, the surface curves up along x and down along y, det H = −4 < 0, a saddle like a horse saddle or a Pringles crisp. Both have zero gradient at the origin, so the gradient alone cannot tell them apart.</p>',
           'O(1)', 'O(1)')
K.practice('linreg-grad', 'h', 'The gradient of mean squared error', 'p_linreg_grad',
           '<p>For X = [[1, 1], [1, 2], [1, 3]], y = [2, 3, 5] and w = [0, 1], compute the loss and its gradient with the formula (2/n)Xᵀ(Xw − y), and check it with finite differences.</p>',
           'errors: [-1.0, -1.0, -2.0]\nloss = 2.0000, gradient = [-2.6667, -6.0000]\nnumerical gradient = [-2.6667, -6.0000]',
           'Find the errors Xw − y first. Each gradient entry is a feature column dotted with the errors, times 2/n.',
           '<p>The errors are [−1, −1, −2] and the loss is (1 + 1 + 4) ÷ 3 = 2. The bias column of 1s gives (2/3)(−4) = −2.667 and the x column gives (2/3)(−1 − 2 − 6) = −6. The x weight gets the bigger push because the biggest error (−2) sits on the biggest x (3). The finite difference check agrees to four decimals.</p>',
           'O(n · d)', 'O(n)')
K.practice('twolayer', 'x', 'Backprop through a two layer network', 'p_twolayer',
           '<p>A network has 2 inputs, 2 ReLU hidden units and 1 output. With x = [1, 2], W1 = [[0.1, 0.2], [−0.3, 0.4]], b1 = [0, 0.1], w2 = [0.7, −0.2], b2 = 0.05 and target 1, run the forward pass and backpropagate to every weight.</p>',
           'hidden = [0.5000, 0.6000], output = 0.2800, loss = 0.5184\ndL/db2 = -1.4400, dL/dw2 = [-0.7200, -0.8640]\ndL/dW1 = [[-1.0080, -2.0160], [0.2880, 0.5760]]',
           'Go backwards one layer at a time: output, then w2 and the hidden units, then through ReLU to W1.',
           '<p>Forward: hidden pre activations are 0.1 + 0.4 = 0.5 and −0.3 + 0.8 + 0.1 = 0.6, both positive so ReLU keeps them. Output = 0.35 − 0.12 + 0.05 = 0.28 and the loss is (−0.72)² = 0.5184. Backward: ∂L/∂out = 2(−0.72) = −1.44, which is also ∂L/∂b2. Then ∂L/∂w2 = −1.44 × hidden and ∂L/∂hidden = −1.44 × w2 = [−1.008, 0.288]. ReLU passes these through because both units were active. Finally ∂L/∂W1 is each hidden gradient times each input, an outer product.</p>',
           'O(layer sizes²)', 'O(layer sizes)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'When taking ∂f/∂x, what do you do with y?', ['ignore f', 'treat it as a fixed number', 'set it to zero', 'differentiate it too'], 1, 'Hold every other input still.', 'All other variables are constants while you differentiate with respect to x.')
K.quiz('e', 'What is ∂/∂x of 3x + 5y?', ['3', '5', '8', '3x'], 0, '5y is a constant here.', 'The slope of 3x is 3 and the constant 5y has slope 0.')
K.quiz('e', 'In which direction does the gradient point?', ['steepest descent', 'steepest ascent', 'along the contour', 'towards the origin'], 1, 'Uphill.', 'It points to the fastest increase, so −∇f points to the fastest decrease.')
K.quiz('e', 'What does a zero gradient mean?', ['the function is zero', 'a flat point: a peak, valley or saddle', 'the step size is zero', 'the data is wrong'], 1, 'No tilt in any direction.', 'All partial derivatives are zero, so the surface is flat there.')
K.quiz('m', 'What is the gradient of f(x, y) = x² + y² at (1, 2)?', ['[1, 2]', '[2, 4]', '[2, 2]', '[1, 4]'], 1, '[2x, 2y].', '[2 × 1, 2 × 2] = [2, 4].')
K.quiz('m', 'How does the gradient relate to the contour lines?', ['parallel to them', 'at right angles to them', 'equal to them', 'unrelated'], 1, 'Contours have no change along them.', 'Moving along a contour changes nothing, so the gradient is perpendicular.')
K.quiz('m', 'In backprop, what does an add node do to the incoming gradient?', ['doubles it', 'copies it unchanged to both inputs', 'swaps it', 'sets it to zero'], 1, 'The local slope of a + b is 1 for each.', 'Each input gets the incoming gradient times 1.')
K.quiz('m', 'For a layer z = Wx + b, what is the Jacobian ∂z/∂x?', ['x', 'W', 'Wᵀ', 'b'], 1, 'Each output is a row of W dotted with x.', '∂zᵢ/∂xⱼ = Wᵢⱼ, so the Jacobian is W itself.')
K.quiz('m', 'A Hessian at a flat point has eigenvalues 3 and −2. What is the point?', ['minimum', 'maximum', 'saddle', 'cannot tell'], 2, 'Mixed signs.', 'Up in one direction, down in another: a saddle.')
K.quiz('h', 'What is ∂L/∂z for L = (σ(z) − y)² when σ(z) = 0.5 and y = 1?', ['−1', '−0.25', '0.25', '−0.5'], 1, '2(a − y) × a(1 − a).', '2 × (−0.5) × 0.25 = −0.25.')
K.quiz('h', 'Why is backpropagation so much faster than finite differences for a net with a million weights?', ['it uses less memory', 'it gets all gradients in about two forward passes instead of a million', 'it skips the loss', 'it uses integers'], 1, 'Count the forward passes.', 'Finite differences need an extra pass per weight. Backprop reuses the chain rule products.')
K.quiz('h', 'The directional derivative of f at a point is largest when u points…', ['along a contour', 'along ∇f', 'opposite ∇f', 'along the x axis'], 1, '∇f · u with ‖u‖ = 1.', 'A dot product with a unit vector is largest when they point the same way, giving ‖∇f‖.')
K.quiz('h', 'A weight matrix W is 64 × 128. What is the shape of ∂L/∂W?', ['128 × 64', '64 × 128', '64 × 1', '1 × 1'], 1, 'One partial per weight.', 'The gradient has the same shape as the parameter.')
K.quiz('x', 'In a ReLU unit whose input was negative on the forward pass, what gradient flows back through it?', ['the full gradient', 'zero', 'half the gradient', 'the negative gradient'], 1, 'The local slope of ReLU for negative inputs.', 'ReLU has slope 0 for negative inputs, so it blocks the gradient. If this always happens the unit is "dead".')
K.quiz('x', 'In high dimensional neural network losses, most points with zero gradient are…', ['global minima', 'saddle points', 'maxima', 'impossible'], 1, 'Think about eigenvalue signs among millions of directions.', 'With millions of directions it is very likely that some curve up and some curve down, so saddles dominate.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What is ∂/∂x of f(x, y) = 3x + 5y?', '3', 'Treat y as a fixed number.', [
    'The 3x term has slope <span class="eq">3</span> as x moves.',
    'The 5y term does not change when only x moves, so its slope is <span class="eq">0</span>.',
    'Total: <span class="eq">3 + 0 = 3</span>',
], check=3)
K.calc('e', 'f(x, y) = x²y. What is ∂f/∂x at (3, 2)?', '12', 'Treat y as a number: d/dx of x² × y.', [
    'Holding y fixed, <span class="eq">∂f/∂x = 2x × y = 2xy</span>',
    'Put in x = 3, y = 2: <span class="eq">2 × 3 × 2</span>',
    '<span class="eq">= 12</span>',
], check=12)
K.calc('e', 'What is the length of the gradient of f(x, y) = x² + y² at (3, 4)?', '10', 'Gradient = [2x, 2y], then use Pythagoras.', [
    'Gradient: <span class="eq">[2 × 3, 2 × 4] = [6, 8]</span>',
    'Length: <span class="eq">√(6² + 8²) = √(36 + 64) = √100</span>',
    '<span class="eq">= 10</span>. The surface rises 10 units per unit step in the steepest direction.',
], check=10)
K.calc('e', 'f(x, y) = x²y + 3y. What is ∂f/∂y at (2, 1)?', '7', 'Treat x as a number.', [
    'Holding x fixed: x²y has slope <span class="eq">x²</span> and 3y has slope <span class="eq">3</span>',
    'So <span class="eq">∂f/∂y = x² + 3</span>',
    'At x = 2: <span class="eq">4 + 3 = 7</span>',
], check=7)
K.calc('m', 'f(x, y) = x² + y². What is the rate of change at (1, 2) in the direction u = [0.6, 0.8]?', '4.4', 'Directional derivative = ∇f · u.', [
    'Gradient at (1, 2): <span class="eq">[2 × 1, 2 × 2] = [2, 4]</span>',
    'u is already a unit vector: <span class="eq">0.6² + 0.8² = 1</span>',
    'Dot product: <span class="eq">2 × 0.6 + 4 × 0.8 = 1.2 + 3.2 = 4.4</span>',
], check=4.4)
K.calc('m', 'Use the tangent plane of f = √(x² + y²) at (3, 4) to estimate f(3.1, 3.9).', '4.98', 'f(x + Δ) ≈ f(x) + ∇f · Δ.', [
    'At (3, 4): <span class="eq">f = 5</span> and <span class="eq">∇f = [3/5, 4/5] = [0.6, 0.8]</span>',
    'Step: <span class="eq">Δ = [0.1, −0.1]</span>',
    'Change: <span class="eq">0.6 × 0.1 + 0.8 × (−0.1) = 0.06 − 0.08 = −0.02</span>',
    'Estimate: <span class="eq">5 − 0.02 = 4.98</span>',
], check=4.98)
K.calc('m', 'For f = (x + y) × z with x = 2, y = −1, z = 3, what is ∂f/∂x?', '3', 'Backward: the multiply node swaps, the add node copies.', [
    'Forward: <span class="eq">q = x + y = 1</span>, <span class="eq">f = q × z = 3</span>',
    'Multiply node: <span class="eq">∂f/∂q = z = 3</span>',
    'Add node passes it to x unchanged: <span class="eq">∂f/∂x = 3 × 1 = 3</span>',
], check=3)
K.calc('m', 'The map (x, y) → (xy, x + y) has Jacobian [[y, x], [1, 1]]. What is its determinant at (2, 3)?', '1', 'Put in the numbers, then ad − bc.', [
    'At (2, 3): <span class="eq">J = [[3, 2], [1, 1]]</span>',
    'Determinant: <span class="eq">3 × 1 − 2 × 1</span>',
    '<span class="eq">= 3 − 2 = 1</span>. Near (2, 3) the map keeps areas the same size.',
], check=1)
K.calc('h', 'What is the determinant of the Hessian of f(x, y) = x² + xy + 2y²?', '7', 'Second partials: f_xx, f_yy and f_xy.', [
    '<span class="eq">f_xx = 2</span> (from x²), <span class="eq">f_yy = 4</span> (from 2y²)',
    '<span class="eq">f_xy = 1</span> (from xy)',
    'Hessian <span class="eq">[[2, 1], [1, 4]]</span>, determinant <span class="eq">2 × 4 − 1 × 1 = 7</span>',
    'Positive determinant and f_xx > 0, so the flat point is a minimum.',
], check=7)
K.calc('h', 'Neuron: x = [1, 2], w = [0.5, −0.3], b = 0.1, sigmoid, loss (a − 1)². What is ∂L/∂w₁?', '-0.25', 'z, then a, then multiply the three local slopes.', [
    '<span class="eq">z = 0.5 − 0.6 + 0.1 = 0</span>, so <span class="eq">a = σ(0) = 0.5</span>',
    '<span class="eq">∂L/∂a = 2(0.5 − 1) = −1</span> and <span class="eq">∂a/∂z = 0.5 × 0.5 = 0.25</span>',
    '<span class="eq">∂z/∂w₁ = x₁ = 1</span>',
    'Multiply: <span class="eq">−1 × 0.25 × 1 = −0.25</span>',
], check=-0.25, alt=['−0.25'])
K.calc('h', 'What is the determinant of the Hessian of f(x, y) = x² − 4xy + y²? (A negative value means a saddle.)', '-12', 'Find f_xx, f_yy and f_xy.', [
    '<span class="eq">f_xx = 2</span>, <span class="eq">f_yy = 2</span>',
    '<span class="eq">f_xy = −4</span>',
    'Determinant: <span class="eq">2 × 2 − (−4)² = 4 − 16 = −12</span>',
    'Negative, so (0, 0) is a saddle, even though both x² and y² curve upwards on their own.',
], check=-12, alt=['−12'])
K.calc('x', 'MSE with X = [[1, 1], [1, 2], [1, 3]], y = [2, 3, 5], w = [0, 1]. What is the gradient entry for the second weight?', '-6', '∇L = (2/n) Xᵀ(Xw − y).', [
    'Predictions <span class="eq">[1, 2, 3]</span>, errors <span class="eq">[−1, −1, −2]</span>',
    'Second column of X is [1, 2, 3]. Dot with errors: <span class="eq">−1 − 2 − 6 = −9</span>',
    'Multiply by 2/n = 2/3: <span class="eq">−9 × 2 ÷ 3 = −6</span>',
], check=-6, alt=['−6'])
K.calc('x', 'In the two layer net of practice problem 4 (output 0.28, target 1, squared error), what is ∂L/∂b₂?', '-1.44', 'The output bias has local slope 1.', [
    'Loss: <span class="eq">L = (out − y)²</span>',
    '<span class="eq">∂L/∂out = 2(0.28 − 1) = 2 × (−0.72) = −1.44</span>',
    '<span class="eq">∂out/∂b₂ = 1</span>, so <span class="eq">∂L/∂b₂ = −1.44</span>',
], check=-1.44, alt=['−1.44'])

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;
  const SURF = {
    bowl: { f: (x, y) => x * x + 3 * y * y, g: (x, y) => [2 * x, 6 * y], name: 'x² + 3y²', r: 3 },
    round: { f: (x, y) => x * x + y * y, g: (x, y) => [2 * x, 2 * y], name: 'x² + y²', r: 3 },
    saddle: { f: (x, y) => x * x - y * y, g: (x, y) => [2 * x, -2 * y], name: 'x² − y²', r: 3 },
    hills: { f: (x, y) => 3 * Math.exp(-((x - 1) ** 2 + (y - 1) ** 2)) + 2 * Math.exp(-((x + 1.3) ** 2 + (y + 1) ** 2) / 0.8), g: (x, y) => { const a = 3 * Math.exp(-((x - 1) ** 2 + (y - 1) ** 2)), c = 2 * Math.exp(-((x + 1.3) ** 2 + (y + 1) ** 2) / 0.8); return [-2 * (x - 1) * a - 2 * (x + 1.3) / 0.8 * c, -2 * (y - 1) * a - 2 * (y + 1) / 0.8 * c]; }, name: 'two hills', r: 3 },
  };
  /* colour map cells and contour lines (marching squares) for f over a square frame */
  function heat(G, f, levels) {
    const n = 36, [x0, x1] = G.xr, [y0, y1] = G.yr, dx = (x1 - x0) / n, dy = (y1 - y0) / n;
    const V = []; let lo = Infinity, hi = -Infinity;
    for (let i = 0; i <= n; i++) { V.push([]); for (let j = 0; j <= n; j++) { const v = f(x0 + i * dx, y0 + j * dy); V[i].push(v); lo = Math.min(lo, v); hi = Math.max(hi, v); } }
    let s = '';
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      const v = (V[i][j] + V[i + 1][j] + V[i][j + 1] + V[i + 1][j + 1]) / 4, p = Math.round(8 + 50 * (v - lo) / (hi - lo || 1));
      s += `<rect x="${G.sx(x0 + i * dx).toFixed(1)}" y="${G.sy(y0 + (j + 1) * dy).toFixed(1)}" width="${(G.sx(x0 + dx) - G.sx(x0) + 0.6).toFixed(1)}" height="${(G.sy(y0) - G.sy(y0 + dy) + 0.6).toFixed(1)}" style="fill:color-mix(in srgb, var(--accent) ${p}%, var(--surface))"/>`;
    }
    const L = levels || 8;
    for (let k = 1; k < L; k++) {
      const c = lo + (hi - lo) * k / L;
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
        const pts = [], corner = [[i, j], [i + 1, j], [i + 1, j + 1], [i, j + 1]];
        for (let e = 0; e < 4; e++) {
          const [a1, b1] = corner[e], [a2, b2] = corner[(e + 1) % 4], v1 = V[a1][b1], v2 = V[a2][b2];
          if ((v1 - c) * (v2 - c) < 0) { const t = (c - v1) / (v2 - v1); pts.push([x0 + (a1 + t * (a2 - a1)) * dx, y0 + (b1 + t * (b2 - b1)) * dy]); }
        }
        if (pts.length >= 2) s += MV.line(G, pts[0][0], pts[0][1], pts[1][0], pts[1][1], 'mv-cont');
        if (pts.length === 4) s += MV.line(G, pts[2][0], pts[2][1], pts[3][0], pts[3][1], 'mv-cont');
      }
    }
    return s;
  }

  /* ----- slice a surface to see one partial derivative ----- */
  W.slice = el => {
    const b = shell(el, 'Slice the surface: one partial at a time', 'The left map shows f(x, y) = x²y + 3y from above (darker is higher). Choose which input moves. The right graph is the slice through the purple point, and its tangent slope is the partial derivative.');
    b.innerHTML = `<div class="vz-row">${seg('dir', [['x', 'Move x, freeze y'], ['y', 'Move y, freeze x']], 'x')}</div>
      <div class="mv-wrap"><div class="pd-map"></div><div class="pd-cut"></div></div>
      <div class="vz-row">${slider('px', 'x', -2, 2, 2, 0.1)}${slider('py', 'y', -2, 2, 1, 0.1)}</div><div class="mv-read pd-out" aria-live="polite"></div>`;
    const f = (x, y) => x * x * y + 3 * y, fx = (x, y) => 2 * x * y, fy = x => x * x + 3;
    let dir = 'x', px = 2, py = 1;
    const GM = MV.frame(300, 300, [-2.2, 2.2], [-2.2, 2.2], 20), base = heat(GM, f, 10);
    function draw() {
      let s = base + MV.axes(GM, { labels: false });
      s += dir === 'x' ? MV.line(GM, -2.2, py, 2.2, py, 'mv-v o') : MV.line(GM, px, -2.2, px, 2.2, 'mv-v o');
      s += MV.dot(GM, px, py, 'p', 7);
      $('.pd-map', b).innerHTML = MV.svg(GM, s, 'Map of the surface from above');
      const g = dir === 'x' ? t => f(t, py) : t => f(px, t), t0 = dir === 'x' ? px : py, m = dir === 'x' ? fx(px, py) : fy(px);
      const GC = MV.frame(340, 300, [-2.2, 2.2], [-22, 22]);
      let c = MV.axes(GC, { ystep: 10, xl: dir, yl: 'f' }) + MV.curve(GC, g, 'c2') + MV.curve(GC, t => g(t0) + m * (t - t0), 'c4 thin dash') + MV.dot(GC, t0, g(t0), 'p');
      $('.pd-cut', b).innerHTML = MV.svg(GC, c, 'The slice through the point');
      $('.pd-out', b).innerHTML = dir === 'x'
        ? `With y frozen at ${MV.num(py)}, the slice is f = ${MV.num(py)}x² + ${MV.num(3 * py)}. Its slope at x = ${MV.num(px)} is <b>∂f/∂x = 2xy = ${MV.num(m)}</b>.`
        : `With x frozen at ${MV.num(px)}, the slice is f = (${MV.num(px * px)} + 3)y, a straight line. Its slope is <b>∂f/∂y = x² + 3 = ${MV.num(m)}</b>.`;
    }
    wireSeg(b, 'dir', v => { dir = v; draw(); });
    wireSlider(b, 'px', v => { px = v; draw(); });
    wireSlider(b, 'py', v => { py = v; draw(); });
    draw();
  };

  /* ----- gradient arrows on a contour map, and walking downhill ----- */
  W.gradfield = el => {
    const b = shell(el, 'Gradient arrows and the way down', 'Pick a surface. Small arrows show −∇f, the downhill direction, everywhere. Drag the orange point to read the gradient there. Press Play to take small steps against the gradient and watch the path.');
    b.innerHTML = `<div class="vz-row">${seg('sf', [['bowl', 'Stretched bowl'], ['round', 'Round bowl'], ['saddle', 'Saddle'], ['hills', 'Two hills']], 'bowl')}</div>
      <div class="mv-wrap"><div class="gf-plot"></div><div class="mv-side">${slider('lr', 'step size', 0.02, 0.3, 0.1, 0.01)}<div class="mv-read gf-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let S = SURF.bowl, key = 'bowl', start = [2.4, 1.6], path = [], lr = 0.1, base = '', svgEl;
    const G = MV.frame(420, 420, [-3, 3], [-3, 3]);
    function prep() {
      base = heat(G, S.f, 10);
      let s = '';
      for (let i = -2.5; i <= 2.51; i += 0.75) for (let j = -2.5; j <= 2.51; j += 0.75) {
        const g = S.g(i, j), m = Math.hypot(...g);
        if (m > 1e-6) { const k = 0.32 / m; s += MV.arrow(G, i, j, i - g[0] * k, j - g[1] * k, 'k'); }
      }
      base += s;
      $('.gf-plot', b).innerHTML = MV.svg(G, '<g class="gf-g"></g>', 'Contour map with gradient arrows');
      svgEl = $('.gf-plot svg', b);
      MV.drag(svgEl, G, [{ set: (x, y) => { start = [Math.round(x * 10) / 10, Math.round(y * 10) / 10]; } }], () => { plan(); P.load(path.length, 0); });
    }
    function plan() {
      path = [start.slice()];
      for (let k = 0; k < 30; k++) { const [x, y] = path[path.length - 1], g = S.g(x, y); const nx = x - lr * g[0], ny = y - lr * g[1]; if (Math.abs(nx) > 6 || Math.abs(ny) > 6) break; path.push([nx, ny]); }
    }
    function show(t) {
      const p = path[Math.min(t, path.length - 1)], g = S.g(p[0], p[1]), m = Math.hypot(...g);
      let s = base;
      const vis = path.slice(0, t + 1).filter(q => Math.abs(q[0]) <= 3 && Math.abs(q[1]) <= 3);
      if (vis.length > 1) s += `<polyline class="mv-curve c2" points="${vis.map(q => G.sx(q[0]).toFixed(1) + ',' + G.sy(q[1]).toFixed(1)).join(' ')}"/>`;
      vis.forEach(q => { s += MV.dot(G, q[0], q[1], 'o', 3); });
      const inside = Math.abs(p[0]) <= 3 && Math.abs(p[1]) <= 3;
      if (inside && m > 1e-6) { const k = Math.min(1.2, 0.5 * m) / m; s += MV.arrow(G, p[0], p[1], p[0] + g[0] * k, p[1] + g[1] * k, 'r') + MV.arrow(G, p[0], p[1], p[0] - g[0] * k, p[1] - g[1] * k, 'g'); }
      s += `<circle class="mv-pt o big mv-drag" data-h="0" cx="${G.sx(start[0])}" cy="${G.sy(start[1])}" r="10"/>`;
      $('.gf-g', svgEl).innerHTML = s;
      $('.gf-out', b).innerHTML = `f = ${S.name}<br>step ${t} of ${path.length - 1}<br>point = (${MV.num(p[0])}, ${MV.num(p[1])})<br>f = <b>${MV.num(S.f(p[0], p[1]), 3)}</b><br><span style="color:var(--red)">●</span> ∇f = [${MV.num(g[0])}, ${MV.num(g[1])}] (uphill)<br><span style="color:var(--green)">●</span> −∇f (downhill)<br>steepness ‖∇f‖ = ${MV.num(m, 3)}` +
        (inside ? '' : '<br>⚠️ The path has left the map. Try a smaller step size.') + (key === 'saddle' ? '<br>On a saddle the path slides away along y even though it starts close to the centre.' : '');
    }
    const P = Player($('.vz-p', b), show, 380);
    wireSeg(b, 'sf', v => { key = v; S = SURF[v]; start = v === 'hills' ? [0.2, 2.5] : v === 'saddle' ? [2.5, 0.15] : [2.4, 1.6]; prep(); plan(); P.load(path.length, 0); });
    wireSlider(b, 'lr', v => { lr = v; plan(); P.load(path.length, 0); });
    prep(); plan(); P.load(path.length, 0);
  };

  /* ----- forward and backward pass on a small graph ----- */
  W.backprop = el => {
    const b = shell(el, 'Backpropagation on a graph', 'f = (x + y) × z, then L = f². Type any inputs, then press Play. Values flow forward in blue, gradients flow backward in orange, one node at a time.');
    b.innerHTML = `<div class="mv-inp">x <input type="number" data-v="x" value="2" step="1"> y <input type="number" data-v="y" value="-1" step="1"> z <input type="number" data-v="z" value="3" step="1"></div>
      <div class="bp-host"></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const V = { x: 2, y: -1, z: 3 };
    const N = { x: [56, 45], y: [56, 165], z: [56, 285], q: [220, 105], f: [385, 195], L: [545, 195] };
    const E = [['x', 'q'], ['y', 'q'], ['q', 'f'], ['z', 'f'], ['f', 'L']];
    const OP = { q: '+', f: '×', L: '( )²' };
    let st = [];
    function plan() {
      const q = V.x + V.y, f = q * V.z, L = f * f, dL = 1, df = 2 * f, dq = df * V.z, dz = df * q, dx = dq, dy = dq;
      const val = { x: V.x, y: V.y, z: V.z, q, f, L }, grad = { L: dL, f: df, q: dq, z: dz, x: dx, y: dy };
      st = [
        { show: ['x', 'y', 'z'], g: [], msg: 'Inputs are ready. Nothing computed yet.' },
        { show: ['x', 'y', 'z', 'q'], g: [], msg: `Forward, add node: q = x + y = ${V.x} + (${V.y}) = ${q}` },
        { show: ['x', 'y', 'z', 'q', 'f'], g: [], msg: `Forward, multiply node: f = q × z = ${q} × ${V.z} = ${f}` },
        { show: ['x', 'y', 'z', 'q', 'f', 'L'], g: [], msg: `Forward, square node: L = f² = ${L}` },
        { show: 'all', g: ['L'], msg: 'Backward starts at the output with ∂L/∂L = 1.' },
        { show: 'all', g: ['L', 'f'], msg: `Square node: local slope 2f = ${2 * f}. So ∂L/∂f = 1 × ${2 * f} = ${df}` },
        { show: 'all', g: ['L', 'f', 'q', 'z'], msg: `Multiply node swaps: ∂L/∂q = ${df} × z = ${dq} and ∂L/∂z = ${df} × q = ${dz}` },
        { show: 'all', g: ['L', 'f', 'q', 'z', 'x', 'y'], msg: `Add node copies: ∂L/∂x = ${dq} × 1 = ${dx} and ∂L/∂y = ${dq} × 1 = ${dy}. Done: every input has its gradient.` },
      ];
      st.forEach(s => { s.val = val; s.grad = grad; });
      P.load(st.length, 0);
    }
    function show(t) {
      const s = st[t], on = k => s.show === 'all' || s.show.includes(k);
      let h = '';
      E.forEach(([a, c]) => { const [x1, y1] = N[a], [x2, y2] = N[c]; h += `<line x1="${x1 + 46}" y1="${y1}" x2="${x2 - 46}" y2="${y2}" class="mv-v k" stroke-width="2"/>`; });
      Object.entries(N).forEach(([k, [x, y]]) => {
        h += `<rect x="${x - 46}" y="${y - 32}" width="92" height="64" rx="10" class="bp-node ${on(k) ? 'on' : ''}"/>`;
        h += `<text x="${x}" y="${y - 8}" text-anchor="middle" class="mv-lab">${OP[k] ? k + ' ' + OP[k] : k}</text>`;
        h += `<text x="${x}" y="${y + 20}" text-anchor="middle" class="mv-lab bp-val">${on(k) ? s.val[k] : '?'}</text>`;
        if (s.g.includes(k)) h += `<text x="${x}" y="${y + 54}" text-anchor="middle" class="mv-lab bp-grad">∂L = ${s.grad[k]}</text>`;
      });
      $('.bp-host', b).innerHTML = `<svg class="mv-svg" viewBox="0 0 600 350" role="img" aria-label="Computational graph with forward values and backward gradients">${h}</svg>`;
      $('.vz-msg', b).innerHTML = s.msg;
    }
    const P = Player($('.vz-p', b), show, 1300);
    b.querySelectorAll('[data-v]').forEach(i => i.addEventListener('input', () => { const v = parseFloat(i.value); V[i.dataset.v] = isFinite(v) ? Math.round(v * 100) / 100 : 0; plan(); }));
    plan();
  };
})();
'''

CSS = r'''
.pd-map,.pd-cut{min-width:0}
.bp-node{fill:var(--surface2); stroke:var(--line); stroke-width:2}
.bp-node.on{fill:color-mix(in srgb, var(--accent) 14%, var(--surface)); stroke:var(--accent)}
.bp-host .mv-lab{font-size:19px}
.bp-val{fill:var(--accent); font-weight:800}
.bp-grad{fill:var(--orange); font-weight:800}
'''

# ---------------------------------------------------------------- deeper explanations and extra animations
# Each lesson above gives the short version. DEEPER adds a slower, fuller explanation (and sometimes an
# animation) to the end of the lesson with the same id.
DEEPER = {
    'partial': deep('a partial derivative worked slowly', f'''
<p>The only new skill is discipline: when you differentiate with respect to x, every other letter is treated as an ordinary fixed number, exactly like 7 or 3.</p>
{worked('f(x, y) = x²y + 3y at the point (2, 1)', [
        'For ∂f/∂x, freeze y. Then x²y is "a number times x²", whose slope is <span class="eq">2xy</span>, and 3y is a constant, whose slope is 0.',
        'So <span class="eq">∂f/∂x = 2xy</span>. At (2, 1): <span class="eq">2 × 2 × 1 = 4</span>',
        'For ∂f/∂y, freeze x. Then x²y is "a number times y" with slope <span class="eq">x²</span>, and 3y has slope 3.',
        'So <span class="eq">∂f/∂y = x² + 3</span>. At (2, 1): <span class="eq">4 + 3 = 7</span>',
        'Meaning: from (2, 1), nudging y up raises f almost twice as fast as nudging x up by the same amount.'])}
<p>A partial derivative is a slice. Cut the surface f(x, y) with a plane where y is fixed, and you get an ordinary curve in x. Its slope is ∂f/∂x. The animation at the top of this lesson shows exactly that slice.</p>
{table(['Function', '∂/∂x', '∂/∂y'], [
        ['3x + 5y', '3', '5'],
        ['xy', 'y', 'x'],
        ['x² + y²', '2x', '2y'],
        ['e^(xy)', 'y e^(xy)', 'x e^(xy)'],
        ['w₁x₁ + w₂x₂ + b (in w₁)', 'x₁ (the input that w₁ multiplies)', 'not used'],
    ])}
'''),
    'gradient': deep('why the gradient is the steepest direction', f'''
<p>The next lesson shows that the slope in a unit direction u is ∇f · u. From Chapter 3, a dot product equals ‖∇f‖ ‖u‖ cos θ, and ‖u‖ = 1. So the slope in direction u is simply <b>‖∇f‖ cos θ</b>, where θ is the angle between u and the gradient.</p>
<ul>
<li>cos θ is largest (equal to 1) when θ = 0, so the steepest climb is straight along ∇f, and its slope is ‖∇f‖.</li>
<li>cos θ = −1 when θ = 180°, so the steepest descent is along −∇f, with slope −‖∇f‖.</li>
<li>cos θ = 0 when θ = 90°, so walking at right angles to the gradient keeps you at the same height. That path is a contour line.</li>
</ul>
{worked('Steepest climb on f(x, y) = x² + 3y² at (1, 1)', [
        'Gradient: <span class="eq">∇f = [2x, 6y] = [2, 6]</span>',
        'Steepest slope: <span class="eq">‖∇f‖ = √(4 + 36) = √40 ≈ 6.32</span>',
        'Unit direction of steepest climb: <span class="eq">[2, 6] ÷ 6.32 ≈ [0.32, 0.95]</span>, mostly along y because the bowl is steeper in y.',
        'Walking along x only, u = [1, 0], gives slope <span class="eq">∇f · u = 2</span>, much gentler than 6.32.'])}
{life('Water on a hillside always runs along minus the gradient. That is why streams cross contour lines on a map at right angles.')}
'''),
    'approx': deep('how good is the tangent line guess', f'''
<p>The linear approximation replaces a curve by its tangent line. It is excellent very close to the point and gets worse as you move away. The error grows roughly with the <b>square</b> of the step: half the step, about a quarter of the error. That is why small learning rates make the "loss should drop by about η‖∇L‖²" promise come true.</p>
{worked('Estimate √4.1 without a calculator', [
        'f(x) = √x near a = 4, where we know f(4) = 2.',
        'Slope: <span class="eq">f′(x) = 1 ÷ (2√x)</span>, so <span class="eq">f′(4) = 1 ÷ 4 = 0.25</span>',
        'Tangent guess: <span class="eq">√4.1 ≈ 2 + 0.25 × 0.1 = 2.025</span>',
        'True value: <span class="eq">2.02485…</span>. The error is only about 0.00015.',
        'With a step of 1 instead (√5 ≈ 2 + 0.25 = 2.25, true 2.236) the error is about 0.014, roughly 100 times bigger for a 10 times bigger step.'])}
{viz('linapprox')}
{ml('Chapter 14 adds the next term, the curvature, to get a quadratic approximation. That is the idea behind Newton’s method, which can reach the bottom of a bowl in a single step.')}
'''),
    'jacobian': deep('the Jacobian is the local stretch of a map', f'''
<p>A function that takes a point (x, y) to a new point (u, v) bends the whole plane. Zoom in close enough and the bending looks straight: a tiny square turns into a tiny parallelogram. The Jacobian matrix is that local straight move, and its determinant says how much tiny areas are scaled at that spot.</p>
{worked('Jacobian of u = x + 0.5 sin y, v = y + 0.5 sin x at (0, 0)', [
        '∂u/∂x = <span class="eq">1</span>, ∂u/∂y = <span class="eq">0.5 cos y = 0.5</span>',
        '∂v/∂x = <span class="eq">0.5 cos x = 0.5</span>, ∂v/∂y = <span class="eq">1</span>',
        'So <span class="eq">J = [[1, 0.5], [0.5, 1]]</span>',
        'det J = <span class="eq">1 − 0.25 = 0.75</span>. Near the origin, small areas shrink to three quarters of their size.'])}
<p>Move the probe point below and watch the small square (in orange) change shape across the warped grid. The numbers show J and its determinant at that point.</p>
{viz('jacgrid')}
{ml('Normalising flows, a family of generative models, transform simple noise into data with a chain of invertible maps. To keep track of probability, they add up log |det J| of every step, so they are designed to have Jacobians whose determinants are cheap to compute.')}
'''),
    'backprop': deep('train the neuron yourself', f'''
<p>The worked example above computed one set of gradients. Training simply repeats it: compute the gradients, move every weight a little against its gradient, and go again. Each weight moves by <b>learning rate × gradient</b>.</p>
{worked('One update with learning rate η = 1', [
        'From above: <span class="eq">∂L/∂w₁ = −0.25</span>, <span class="eq">∂L/∂w₂ = −0.5</span>, <span class="eq">∂L/∂b = −0.25</span>',
        'New w₁ = <span class="eq">0.5 − 1 × (−0.25) = 0.75</span>',
        'New w₂ = <span class="eq">−0.3 − 1 × (−0.5) = 0.2</span>, new b = <span class="eq">0.1 + 0.25 = 0.35</span>',
        'New z = <span class="eq">0.75 × 1 + 0.2 × 2 + 0.35 = 1.5</span>, so a = σ(1.5) ≈ 0.818',
        'New loss = <span class="eq">(0.818 − 1)² ≈ 0.033</span>, down from 0.25 after a single step.'])}
<p>Use the playground below to run many steps. Change the inputs, the target or the learning rate, then press Play and watch the loss fall. Try a target of 0 to make the neuron learn to say "no", and try a learning rate of 20 to see training overshoot.</p>
{viz('neuron')}
'''),
    'ml': deep('the batch gradient in numbers', f'''
<p>The formula ∇L = (2 ÷ n) Xᵀ(Xw − y) looks dense, but it is only three small steps: predict, find the errors, and let each feature collect its share of the blame.</p>
{worked('Two examples, two weights', [
        'X = <span class="eq">[[1, 2], [1, 3]]</span> (a column of 1s for the bias, then the feature), y = <span class="eq">[5, 7]</span>, w = <span class="eq">[0, 2]</span>',
        'Predict: <span class="eq">Xw = [0 + 4, 0 + 6] = [4, 6]</span>',
        'Errors: <span class="eq">Xw − y = [−1, −1]</span>. Both predictions are 1 too low.',
        'Blame per feature: <span class="eq">Xᵀ[−1, −1] = [1×(−1) + 1×(−1), 2×(−1) + 3×(−1)] = [−2, −5]</span>',
        'Average and double: <span class="eq">∇L = (2 ÷ 2) × [−2, −5] = [−2, −5]</span>. Both weights should go up, the feature weight more.'])}
<p>Every deep learning library does exactly this, just with millions of rows and thousands of columns, and with the computational graph doing the bookkeeping instead of you.</p>
'''),
}
for _p in PARTS:
    _p['html'] += DEEPER.get(_p['id'], '')

VIZ_JS += r'''
(() => {
  const { $, shell, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;
  const sig = z => 1 / (1 + Math.exp(-z));

  /* ----- tangent line guess versus the true curve ----- */
  W.linapprox = el => {
    const b = shell(el, 'Tangent line guess for √x', 'Pick the point a you know well and how far away you want to guess. Press Play to grow the step and watch the error grow like the square of the step.');
    b.innerHTML = `<div class="mv-wrap"><div class="la-plot"></div><div class="mv-side">${slider('a', 'a', 1, 9, 4, 1)}${slider('d', 'step Δ', -3, 4, 0.5, 0.1)}<div class="mv-read la-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let a = 4, d = 0.5;
    const G = MV.frame(440, 300, [0, 13], [0, 4]);
    function draw() {
      const fa = Math.sqrt(a), m = 0.5 / fa, x = Math.max(0, a + d), guess = fa + m * d, tru = Math.sqrt(x);
      let s = MV.axes(G, { xstep: 1, ystep: 1, xl: 'x', yl: '√x' }) + MV.curve(G, t => Math.sqrt(Math.max(0, t)), '', { from: 0 }) + MV.curve(G, t => fa + m * (t - a), 'c2 thin');
      s += MV.line(G, x, Math.min(guess, tru), x, Math.max(guess, tru), 'mv-res');
      s += MV.dot(G, a, fa, 'k', 5) + MV.dot(G, x, tru, '', 6) + MV.dot(G, x, guess, 'o', 6);
      $('.la-plot', b).innerHTML = MV.svg(G, s, 'Square root and its tangent');
      $('.la-out', b).innerHTML = `at a = ${a}: √a = ${MV.num(fa, 4)}, slope = ${MV.num(m, 4)}<br>x = a + Δ = <b>${MV.num(x, 2)}</b><br>tangent guess = <b>${MV.num(guess, 5)}</b><br>true √x = <b>${MV.num(tru, 5)}</b><br>error = <b>${MV.num(Math.abs(guess - tru), 5)}</b>`;
    }
    const P = Player($('.vz-p', b), t => { d = [0.1, 0.2, 0.5, 1, 2, 4][t]; $('[data-sl="d"]', b).value = d; $('[data-slv="d"]', b).textContent = d; draw(); }, 1100);
    wireSlider(b, 'a', v => { a = v; draw(); });
    wireSlider(b, 'd', v => { P.pause(); d = v; draw(); });
    P.load(6, 2);
  };

  /* ----- a warped grid and the local parallelogram given by the Jacobian ----- */
  W.jacgrid = el => {
    const b = shell(el, 'The Jacobian as a local stretch', 'The map u = x + k sin y, v = y + k sin x bends the grid. Move the probe point and the bend strength k. Press Play to walk the probe across the plane.');
    b.innerHTML = `<div class="mv-wrap"><div class="jg-plot"></div><div class="mv-side">${slider('k', 'bend k', 0, 0.9, 0.5, 0.05)}${slider('px', 'probe x', -3, 3, 0, 0.1)}${slider('py', 'probe y', -3, 3, 0, 0.1)}<div class="mv-read jg-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let k = 0.5, px = 0, py = 0;
    const G = MV.frame(420, 420, [-4.2, 4.2], [-4.2, 4.2]);
    const F = (x, y) => [x + k * Math.sin(y), y + k * Math.sin(x)];
    function draw() {
      let s = '';
      for (let g = -3; g <= 3; g += 0.5) {
        const p1 = [], p2 = [];
        for (let t = -3; t <= 3.001; t += 0.1) { const A = F(g, t), B = F(t, g); p1.push(G.sx(A[0]).toFixed(1) + ',' + G.sy(A[1]).toFixed(1)); p2.push(G.sx(B[0]).toFixed(1) + ',' + G.sy(B[1]).toFixed(1)); }
        s += `<polyline class="mv-cont" points="${p1.join(' ')}"/><polyline class="mv-cont" points="${p2.join(' ')}"/>`;
      }
      const J = [[1, k * Math.cos(py)], [k * Math.cos(px), 1]], det = J[0][0] * J[1][1] - J[0][1] * J[1][0], h = 0.5;
      const c = F(px, py), sq = [[0, 0], [h, 0], [h, h], [0, h]].map(([dx, dy]) => F(px + dx, py + dy));
      s += `<polygon class="mv-poly o" points="${sq.map(p => G.sx(p[0]).toFixed(1) + ',' + G.sy(p[1]).toFixed(1)).join(' ')}"/>`;
      s += MV.arrow(G, c[0], c[1], c[0] + J[0][0] * h * 1.6, c[1] + J[1][0] * h * 1.6, 'a') + MV.arrow(G, c[0], c[1], c[0] + J[0][1] * h * 1.6, c[1] + J[1][1] * h * 1.6, 'g');
      s += MV.dot(G, c[0], c[1], 'r', 5);
      $('.jg-plot', b).innerHTML = MV.svg(G, s, 'Warped grid');
      $('.jg-out', b).innerHTML = `probe (x, y) = (${MV.num(px)}, ${MV.num(py)})<br>J = [[${MV.num(J[0][0], 3)}, ${MV.num(J[0][1], 3)}], [${MV.num(J[1][0], 3)}, ${MV.num(J[1][1], 3)}]]<br>det J = <span class="big">${MV.num(det, 3)}</span><br>` +
        (det > 1.02 ? 'Small areas grow here.' : det < 0.98 ? 'Small areas shrink here.' : 'Areas keep about the same size here.') + '<br><small>Blue arrow: where a step in x goes. Green: where a step in y goes.</small>';
    }
    const setS = (n, v) => { $(`[data-sl="${n}"]`, b).value = v; $(`[data-slv="${n}"]`, b).textContent = MV.num(v); };
    const P = Player($('.vz-p', b), t => { px = -3 + t * 0.3; py = 2.5 * Math.sin(t * 0.3); setS('px', px); setS('py', py); draw(); }, 300);
    wireSlider(b, 'k', v => { k = v; draw(); });
    wireSlider(b, 'px', v => { P.pause(); px = v; draw(); });
    wireSlider(b, 'py', v => { P.pause(); py = v; draw(); });
    P.load(21, 10);
  };

  /* ----- train one sigmoid neuron with squared error ----- */
  W.neuron = el => {
    const b = shell(el, 'Neuron training playground', 'Inputs x₁ and x₂, a target y and a learning rate. Each Play step runs a forward pass, a backward pass and one update. The chart shows the loss after each step.');
    b.innerHTML = `<div class="mv-wrap"><div class="nr-plot"></div><div class="mv-side">${slider('x1', 'x₁', -2, 2, 1, 0.5)}${slider('x2', 'x₂', -2, 2, 2, 0.5)}${slider('y', 'target y', 0, 1, 1, 1)}${slider('lr', 'learning rate η', 0.1, 20, 1, 0.1)}<div class="mv-read nr-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const V = { x1: 1, x2: 2, y: 1, lr: 1 };
    let hist = [];
    function plan() {
      let w1 = 0.5, w2 = -0.3, bb = 0.1;
      hist = [];
      for (let t = 0; t <= 25; t++) {
        const z = w1 * V.x1 + w2 * V.x2 + bb, a = sig(z), L = (a - V.y) ** 2, dz = 2 * (a - V.y) * a * (1 - a);
        hist.push({ w1, w2, b: bb, z, a, L, g: [dz * V.x1, dz * V.x2, dz] });
        w1 -= V.lr * dz * V.x1; w2 -= V.lr * dz * V.x2; bb -= V.lr * dz;
      }
      P.load(hist.length, 0);
    }
    function show(t) {
      const G = MV.frame(420, 280, [0, 25.5], [0, Math.max(0.3, Math.max(...hist.map(h => h.L)) * 1.1)]);
      let s = MV.axes(G, { labels: false, xl: 'step', yl: 'loss' });
      for (let k = 5; k <= 25; k += 5) s += MV.text(G, k, 0, String(k), { dy: 14, anchor: 'middle', cls: 'sm' });
      const pts = hist.slice(0, t + 1).map((h, k) => G.sx(k).toFixed(1) + ',' + G.sy(h.L).toFixed(1)).join(' ');
      s += `<polyline class="mv-v a" points="${pts}"/>` + MV.dot(G, t, hist[t].L, 'o', 6);
      $('.nr-plot', b).innerHTML = MV.svg(G, s, 'Loss during training');
      const h = hist[t], f = v => MV.num(v, 4);
      $('.nr-out', b).innerHTML = `step <b>${t}</b><br>w = [${f(h.w1)}, ${f(h.w2)}], b = ${f(h.b)}<br>z = ${f(h.z)}, a = σ(z) = <b>${f(h.a)}</b><br>loss = (a − y)² = <span class="big">${f(h.L)}</span><br>gradients: ∂L/∂w = [${f(h.g[0])}, ${f(h.g[1])}], ∂L/∂b = ${f(h.g[2])}`;
    }
    const P = Player($('.vz-p', b), show, 450);
    ['x1', 'x2', 'y', 'lr'].forEach(n => wireSlider(b, n, v => { V[n] = v; plan(); }));
    plan();
  };
})();
'''
CSS += r'''
.jg-plot .mv-svg{max-height:430px}
'''

T = K.topic(
    slug='gradients', topic='gradients', prefix='mm07', short='Gradients', emoji='🧗',
    title='Gradients and Backpropagation',
    module=('📉', 'Calculus', 'calculus', 'Derivatives, gradients, the chain rule and optimisation: the maths that lets a model learn from its mistakes.'),
    minutes=60,
    lead='A model has many weights, so its loss is a surface in many directions. Slice it with partial derivatives, follow gradient arrows downhill on a contour map, meet the Jacobian and Hessian, and run backpropagation through a graph one node at a time.',
    desc='Multivariable calculus for machine learning: partial derivatives, the gradient, directional derivatives, linear approximation, the Jacobian and Hessian, computational graphs, the multivariable chain rule and backpropagation.',
    summary='Partial derivatives as slices, the gradient as the steepest uphill direction, contour lines, directional derivatives and tangent planes, Jacobian and Hessian matrices with the bowl, cap and saddle test, computational graphs, backpropagation through a neuron and a two layer net, and the vectorised MSE gradient.',
    keywords=['partial derivative', 'gradient', 'nabla', 'contour', 'directional derivative', 'tangent plane', 'jacobian', 'hessian', 'saddle point', 'computational graph', 'chain rule', 'backpropagation', 'gradient check', 'mse gradient', 'autograd'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
