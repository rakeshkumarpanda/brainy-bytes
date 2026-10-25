# Chapter 1: numbers, order of operations, percentages, algebra, powers, sigma notation and absolute value.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz, deep

K = Kit()

# ---------------------------------------------------------------- programs
K.code('float_precision', py=r'''
a = 0.1 + 0.2
print("0.1 + 0.2 =", a)
print("equal to 0.3?", a == 0.3)
print("close to 0.3?", abs(a - 0.3) < 1e-9)
print("7 / 2 =", 7 / 2)
print("7 // 2 =", 7 // 2, "and 7 % 2 =", 7 % 2)
big = 10 ** 16
print("10^16 + 1 as a float:", int(float(big) + 1.0))
''', js=r'''
const a = 0.1 + 0.2;
console.log("0.1 + 0.2 =", a);
console.log("equal to 0.3?", a === 0.3);
console.log("close to 0.3?", Math.abs(a - 0.3) < 1e-9);
console.log("7 / 2 =", 7 / 2);
console.log("7 // 2 =", Math.floor(7 / 2), "and 7 % 2 =", 7 % 2);
const big = 10 ** 16;
console.log("10^16 + 1 as a float:", (big + 1).toString());
''', ts=r'''
const a: number = 0.1 + 0.2;
console.log("0.1 + 0.2 =", a);
console.log("equal to 0.3?", a === 0.3);
console.log("close to 0.3?", Math.abs(a - 0.3) < 1e-9);
console.log("7 / 2 =", 7 / 2);
console.log("7 // 2 =", Math.floor(7 / 2), "and 7 % 2 =", 7 % 2);
const big: number = 10 ** 16;
console.log("10^16 + 1 as a float:", (big + 1).toString());
''', java=r'''
public class FloatPrecision {
    public static void main(String[] args) {
        double a = 0.1 + 0.2;
        System.out.println("0.1 + 0.2 = " + a);
        System.out.println("equal to 0.3? " + (a == 0.3));
        System.out.println("close to 0.3? " + (Math.abs(a - 0.3) < 1e-9));
        System.out.println("7 / 2 = " + (7 / 2.0));
        System.out.println("7 // 2 = " + (7 / 2) + " and 7 % 2 = " + (7 % 2));
        double big = 1e16;
        System.out.println("10^16 + 1 as a float: " + (long) (big + 1.0));
    }
}
''')

K.code('percent', py=r'''
correct, total = 46, 50
accuracy = correct / total * 100
print(f"accuracy = {correct}/{total} x 100 = {accuracy:.1f}%")

old, new = 80, 92
change = (new - old) / old * 100
print(f"accuracy went from {old}% to {new}%: a change of {change:.1f}%")

price, off = 1200, 25
print(f"{off}% off {price} leaves {price * (1 - off / 100):.2f}")
''', js=r'''
const correct = 46, total = 50;
const accuracy = correct / total * 100;
console.log(`accuracy = ${correct}/${total} x 100 = ${accuracy.toFixed(1)}%`);

const oldA = 80, newA = 92;
const change = (newA - oldA) / oldA * 100;
console.log(`accuracy went from ${oldA}% to ${newA}%: a change of ${change.toFixed(1)}%`);

const price = 1200, off = 25;
console.log(`${off}% off ${price} leaves ${(price * (1 - off / 100)).toFixed(2)}`);
''', ts=r'''
const correct: number = 46, total: number = 50;
const accuracy: number = correct / total * 100;
console.log(`accuracy = ${correct}/${total} x 100 = ${accuracy.toFixed(1)}%`);

const oldA: number = 80, newA: number = 92;
const change: number = (newA - oldA) / oldA * 100;
console.log(`accuracy went from ${oldA}% to ${newA}%: a change of ${change.toFixed(1)}%`);

const price: number = 1200, off: number = 25;
console.log(`${off}% off ${price} leaves ${(price * (1 - off / 100)).toFixed(2)}`);
''', java=r'''
public class Percent {
    public static void main(String[] args) {
        int correct = 46, total = 50;
        double accuracy = (double) correct / total * 100;
        System.out.println(String.format("accuracy = %d/%d x 100 = %.1f%%", correct, total, accuracy));

        int oldA = 80, newA = 92;
        double change = (double) (newA - oldA) / oldA * 100;
        System.out.println(String.format("accuracy went from %d%% to %d%%: a change of %.1f%%", oldA, newA, change));

        int price = 1200, off = 25;
        System.out.println(String.format("%d%% off %d leaves %.2f", off, price, price * (1 - off / 100.0)));
    }
}
''')

K.code('solve_linear', py=r'''
def solve(a, b, c):
    # a*x + b = c
    print(f"{a}x + {b} = {c}")
    right = c - b               # take b away from both sides
    print(f"{a}x = {right}")
    x = right / a               # share both sides into a equal groups
    print(f"x = {right}/{a} = {x:g}")
    print("check:", a * x + b == c)


solve(3, 5, 20)
solve(4, -2, 10)
''', js=r'''
function solve(a, b, c) {
  // a*x + b = c
  console.log(`${a}x + ${b} = ${c}`);
  const right = c - b;          // take b away from both sides
  console.log(`${a}x = ${right}`);
  const x = right / a;          // share both sides into a equal groups
  console.log(`x = ${right}/${a} = ${x}`);
  console.log("check:", a * x + b === c);
}

solve(3, 5, 20);
solve(4, -2, 10);
''', ts=r'''
function solve(a: number, b: number, c: number): void {
  // a*x + b = c
  console.log(`${a}x + ${b} = ${c}`);
  const right: number = c - b;  // take b away from both sides
  console.log(`${a}x = ${right}`);
  const x: number = right / a;  // share both sides into a equal groups
  console.log(`x = ${right}/${a} = ${x}`);
  console.log("check:", a * x + b === c);
}

solve(3, 5, 20);
solve(4, -2, 10);
''', java=r'''
public class SolveLinear {
    static void solve(int a, int b, int c) {
        // a*x + b = c
        System.out.println(a + "x + " + b + " = " + c);
        int right = c - b;              // take b away from both sides
        System.out.println(a + "x = " + right);
        double x = (double) right / a;  // share both sides into a equal groups
        String xs = x == Math.floor(x) ? String.valueOf((long) x) : String.valueOf(x);
        System.out.println("x = " + right + "/" + a + " = " + xs);
        System.out.println("check: " + (a * x + b == c));
    }

    public static void main(String[] args) {
        solve(3, 5, 20);
        solve(4, -2, 10);
    }
}
''')

K.code('two_equations', py=r'''
# 2 burgers + 1 juice = 250, 1 burger + 3 juices = 250
a1, b1, c1 = 2, 1, 250
a2, b2, c2 = 1, 3, 250

# elimination: make the juice numbers match, then subtract
det = a1 * b2 - a2 * b1
x = (c1 * b2 - c2 * b1) / det
y = (a1 * c2 - a2 * c1) / det
print("burger =", x, "juice =", y)
print("check 1:", a1 * x + b1 * y, "check 2:", a2 * x + b2 * y)
''', js=r'''
// 2 burgers + 1 juice = 250, 1 burger + 3 juices = 250
const [a1, b1, c1] = [2, 1, 250];
const [a2, b2, c2] = [1, 3, 250];

// elimination: make the juice numbers match, then subtract
const det = a1 * b2 - a2 * b1;
const x = (c1 * b2 - c2 * b1) / det;
const y = (a1 * c2 - a2 * c1) / det;
console.log("burger =", x.toFixed(1), "juice =", y.toFixed(1));
console.log("check 1:", (a1 * x + b1 * y).toFixed(1), "check 2:", (a2 * x + b2 * y).toFixed(1));
''', ts=r'''
// 2 burgers + 1 juice = 250, 1 burger + 3 juices = 250
const [a1, b1, c1]: number[] = [2, 1, 250];
const [a2, b2, c2]: number[] = [1, 3, 250];

// elimination: make the juice numbers match, then subtract
const det: number = a1 * b2 - a2 * b1;
const x: number = (c1 * b2 - c2 * b1) / det;
const y: number = (a1 * c2 - a2 * c1) / det;
console.log("burger =", x.toFixed(1), "juice =", y.toFixed(1));
console.log("check 1:", (a1 * x + b1 * y).toFixed(1), "check 2:", (a2 * x + b2 * y).toFixed(1));
''', java=r'''
public class TwoEquations {
    public static void main(String[] args) {
        // 2 burgers + 1 juice = 250, 1 burger + 3 juices = 250
        double a1 = 2, b1 = 1, c1 = 250;
        double a2 = 1, b2 = 3, c2 = 250;

        // elimination: make the juice numbers match, then subtract
        double det = a1 * b2 - a2 * b1;
        double x = (c1 * b2 - c2 * b1) / det;
        double y = (a1 * c2 - a2 * c1) / det;
        System.out.println("burger = " + x + " juice = " + y);
        System.out.println("check 1: " + (a1 * x + b1 * y) + " check 2: " + (a2 * x + b2 * y));
    }
}
''')

K.code('powers', py=r'''
print("2^3 x 2^4 =", 2 ** 3 * 2 ** 4, "= 2^7 =", 2 ** 7)
print("2^10 / 2^7 =", 2 ** 10 // 2 ** 7, "= 2^3")
print("(2^3)^2 =", (2 ** 3) ** 2, "= 2^6")
print("5^0 =", 5 ** 0)
print("2^-3 =", 2 ** -3)
print("9^0.5 =", 9 ** 0.5)
lr = 3e-4
print("3e-4 =", f"{lr:.4f}")
''', js=r'''
console.log("2^3 x 2^4 =", 2 ** 3 * 2 ** 4, "= 2^7 =", 2 ** 7);
console.log("2^10 / 2^7 =", 2 ** 10 / 2 ** 7, "= 2^3");
console.log("(2^3)^2 =", (2 ** 3) ** 2, "= 2^6");
console.log("5^0 =", 5 ** 0);
console.log("2^-3 =", 2 ** -3);
console.log("9^0.5 =", (9 ** 0.5).toFixed(1));
const lr = 3e-4;
console.log("3e-4 =", lr.toFixed(4));
''', ts=r'''
console.log("2^3 x 2^4 =", 2 ** 3 * 2 ** 4, "= 2^7 =", 2 ** 7);
console.log("2^10 / 2^7 =", 2 ** 10 / 2 ** 7, "= 2^3");
console.log("(2^3)^2 =", (2 ** 3) ** 2, "= 2^6");
console.log("5^0 =", 5 ** 0);
console.log("2^-3 =", 2 ** -3);
console.log("9^0.5 =", (9 ** 0.5).toFixed(1));
const lr: number = 3e-4;
console.log("3e-4 =", lr.toFixed(4));
''', java=r'''
public class Powers {
    public static void main(String[] args) {
        System.out.println("2^3 x 2^4 = " + (int) (Math.pow(2, 3) * Math.pow(2, 4)) + " = 2^7 = " + (int) Math.pow(2, 7));
        System.out.println("2^10 / 2^7 = " + (int) (Math.pow(2, 10) / Math.pow(2, 7)) + " = 2^3");
        System.out.println("(2^3)^2 = " + (int) Math.pow(Math.pow(2, 3), 2) + " = 2^6");
        System.out.println("5^0 = " + (int) Math.pow(5, 0));
        System.out.println("2^-3 = " + Math.pow(2, -3));
        System.out.println("9^0.5 = " + Math.pow(9, 0.5));
        double lr = 3e-4;
        System.out.println("3e-4 = " + String.format("%.4f", lr));
    }
}
''')

K.code('sigma', py=r'''
x = [4, 8, 6, 2]
total = 0
for xi in x:                  # sigma is just a loop that keeps adding
    total += xi
n = len(x)
mean = total / n
print("sum of x =", total)
print("mean =", total, "/", n, "=", mean)

squares = 0
for xi in x:
    squares += (xi - mean) ** 2
print("sum of (x - mean)^2 =", squares)

product = 1
for xi in x:                  # capital pi multiplies instead
    product *= xi
print("product of x =", product)
''', js=r'''
const x = [4, 8, 6, 2];
let total = 0;
for (const xi of x) {         // sigma is just a loop that keeps adding
  total += xi;
}
const n = x.length;
const mean = total / n;
console.log("sum of x =", total);
console.log("mean =", total, "/", n, "=", mean.toFixed(1));

let squares = 0;
for (const xi of x) {
  squares += (xi - mean) ** 2;
}
console.log("sum of (x - mean)^2 =", squares.toFixed(1));

let product = 1;
for (const xi of x) {         // capital pi multiplies instead
  product *= xi;
}
console.log("product of x =", product);
''', ts=r'''
const x: number[] = [4, 8, 6, 2];
let total: number = 0;
for (const xi of x) {         // sigma is just a loop that keeps adding
  total += xi;
}
const n: number = x.length;
const mean: number = total / n;
console.log("sum of x =", total);
console.log("mean =", total, "/", n, "=", mean.toFixed(1));

let squares: number = 0;
for (const xi of x) {
  squares += (xi - mean) ** 2;
}
console.log("sum of (x - mean)^2 =", squares.toFixed(1));

let product: number = 1;
for (const xi of x) {         // capital pi multiplies instead
  product *= xi;
}
console.log("product of x =", product);
''', java=r'''
public class Sigma {
    public static void main(String[] args) {
        int[] x = {4, 8, 6, 2};
        int total = 0;
        for (int xi : x) {            // sigma is just a loop that keeps adding
            total += xi;
        }
        int n = x.length;
        double mean = (double) total / n;
        System.out.println("sum of x = " + total);
        System.out.println("mean = " + total + " / " + n + " = " + mean);

        double squares = 0;
        for (int xi : x) {
            squares += Math.pow(xi - mean, 2);
        }
        System.out.println("sum of (x - mean)^2 = " + squares);

        int product = 1;
        for (int xi : x) {            // capital pi multiplies instead
            product *= xi;
        }
        System.out.println("product of x = " + product);
    }
}
''')

K.code('mae', py=r'''
actual = [300, 250, 410]       # real house prices, in thousands
guess = [280, 270, 400]        # what a model predicted
errors = []
for a, g in zip(actual, guess):
    errors.append(abs(a - g))  # distance, never negative
print("errors =", errors)
print(f"mean absolute error = {sum(errors) / len(errors):.2f}")
print("is every error at most 20?", all(e <= 20 for e in errors))
''', js=r'''
const actual = [300, 250, 410];    // real house prices, in thousands
const guess = [280, 270, 400];     // what a model predicted
const errors = [];
for (let i = 0; i < actual.length; i++) {
  errors.push(Math.abs(actual[i] - guess[i]));  // distance, never negative
}
console.log("errors =", "[" + errors.join(", ") + "]");
const mae = errors.reduce((s, e) => s + e, 0) / errors.length;
console.log("mean absolute error =", mae.toFixed(2));
console.log("is every error at most 20?", errors.every(e => e <= 20) ? "True" : "False");
''', ts=r'''
const actual: number[] = [300, 250, 410];  // real house prices, in thousands
const guess: number[] = [280, 270, 400];   // what a model predicted
const errors: number[] = [];
for (let i = 0; i < actual.length; i++) {
  errors.push(Math.abs(actual[i] - guess[i]));  // distance, never negative
}
console.log("errors =", "[" + errors.join(", ") + "]");
const mae: number = errors.reduce((s, e) => s + e, 0) / errors.length;
console.log("mean absolute error =", mae.toFixed(2));
console.log("is every error at most 20?", errors.every(e => e <= 20) ? "True" : "False");
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class Mae {
    public static void main(String[] args) {
        int[] actual = {300, 250, 410};    // real house prices, in thousands
        int[] guess = {280, 270, 400};     // what a model predicted
        List<Integer> errors = new ArrayList<>();
        for (int i = 0; i < actual.length; i++) {
            errors.add(Math.abs(actual[i] - guess[i]));  // distance, never negative
        }
        System.out.println("errors = " + errors);
        double sum = 0;
        boolean small = true;
        for (int e : errors) {
            sum += e;
            if (e > 20) small = false;
        }
        System.out.println(String.format("mean absolute error = %.2f", sum / errors.size()));
        System.out.println("is every error at most 20? " + (small ? "True" : "False"));
    }
}
''')

# ---------------------------------------------------------------- practice programs
K.code('p_linear', py=r'''
def solve(a, b, c):
    # returns x for a*x + b = c
    return (c - b) / a


for a, b, c in [(2, 3, 11), (5, -4, 21), (-3, 9, 0), (4, 1, 3)]:
    x = solve(a, b, c)
    print(f"{a}x + {b} = {c}  ->  x = {x:.2f}")
''', js=r'''
function solve(a, b, c) {
  // returns x for a*x + b = c
  return (c - b) / a;
}

for (const [a, b, c] of [[2, 3, 11], [5, -4, 21], [-3, 9, 0], [4, 1, 3]]) {
  const x = solve(a, b, c);
  console.log(`${a}x + ${b} = ${c}  ->  x = ${x.toFixed(2)}`);
}
''', ts=r'''
function solve(a: number, b: number, c: number): number {
  // returns x for a*x + b = c
  return (c - b) / a;
}

const cases: [number, number, number][] = [[2, 3, 11], [5, -4, 21], [-3, 9, 0], [4, 1, 3]];
for (const [a, b, c] of cases) {
  const x: number = solve(a, b, c);
  console.log(`${a}x + ${b} = ${c}  ->  x = ${x.toFixed(2)}`);
}
''', java=r'''
public class PracticeLinear {
    static double solve(double a, double b, double c) {
        // returns x for a*x + b = c
        return (c - b) / a;
    }

    public static void main(String[] args) {
        int[][] cases = {{2, 3, 11}, {5, -4, 21}, {-3, 9, 0}, {4, 1, 3}};
        for (int[] e : cases) {
            double x = solve(e[0], e[1], e[2]);
            System.out.println(String.format("%dx + %d = %d  ->  x = %.2f", e[0], e[1], e[2], x));
        }
    }
}
''')

K.code('p_compound', py=r'''
def grow(start, rate_percent, years):
    value = start
    for year in range(1, years + 1):
        value = value * (1 + rate_percent / 100)
        print(f"year {year}: {value:.2f}")
    return value


final = grow(1000, 10, 3)
print(f"formula 1000 x 1.1^3 = {1000 * 1.1 ** 3:.2f}")
''', js=r'''
function grow(start, ratePercent, years) {
  let value = start;
  for (let year = 1; year <= years; year++) {
    value = value * (1 + ratePercent / 100);
    console.log(`year ${year}: ${value.toFixed(2)}`);
  }
  return value;
}

const final = grow(1000, 10, 3);
console.log(`formula 1000 x 1.1^3 = ${(1000 * 1.1 ** 3).toFixed(2)}`);
''', ts=r'''
function grow(start: number, ratePercent: number, years: number): number {
  let value: number = start;
  for (let year = 1; year <= years; year++) {
    value = value * (1 + ratePercent / 100);
    console.log(`year ${year}: ${value.toFixed(2)}`);
  }
  return value;
}

const final: number = grow(1000, 10, 3);
console.log(`formula 1000 x 1.1^3 = ${(1000 * 1.1 ** 3).toFixed(2)}`);
''', java=r'''
public class PracticeCompound {
    static double grow(double start, double ratePercent, int years) {
        double value = start;
        for (int year = 1; year <= years; year++) {
            value = value * (1 + ratePercent / 100);
            System.out.println(String.format("year %d: %.2f", year, value));
        }
        return value;
    }

    public static void main(String[] args) {
        double fin = grow(1000, 10, 3);
        System.out.println(String.format("formula 1000 x 1.1^3 = %.2f", 1000 * Math.pow(1.1, 3)));
    }
}
''')

K.code('p_variance', py=r'''
def spread(x):
    n = len(x)
    mean = sum(x) / n
    total = 0
    for xi in x:
        total += (xi - mean) ** 2      # one sigma term
    return mean, total / n


m, v = spread([2, 4, 4, 4, 5, 5, 7, 9])
print("mean =", m)
print("average squared distance =", v)
print("square root of that =", v ** 0.5)
''', js=r'''
function spread(x) {
  const n = x.length;
  const mean = x.reduce((s, v) => s + v, 0) / n;
  let total = 0;
  for (const xi of x) {
    total += (xi - mean) ** 2;         // one sigma term
  }
  return [mean, total / n];
}

const [m, v] = spread([2, 4, 4, 4, 5, 5, 7, 9]);
console.log("mean =", m.toFixed(1));
console.log("average squared distance =", v.toFixed(1));
console.log("square root of that =", Math.sqrt(v).toFixed(1));
''', ts=r'''
function spread(x: number[]): [number, number] {
  const n: number = x.length;
  const mean: number = x.reduce((s, v) => s + v, 0) / n;
  let total: number = 0;
  for (const xi of x) {
    total += (xi - mean) ** 2;         // one sigma term
  }
  return [mean, total / n];
}

const [m, v] = spread([2, 4, 4, 4, 5, 5, 7, 9]);
console.log("mean =", m.toFixed(1));
console.log("average squared distance =", v.toFixed(1));
console.log("square root of that =", Math.sqrt(v).toFixed(1));
''', java=r'''
public class PracticeVariance {
    static double[] spread(int[] x) {
        int n = x.length;
        double sum = 0;
        for (int xi : x) sum += xi;
        double mean = sum / n;
        double total = 0;
        for (int xi : x) {
            total += Math.pow(xi - mean, 2);   // one sigma term
        }
        return new double[]{mean, total / n};
    }

    public static void main(String[] args) {
        double[] r = spread(new int[]{2, 4, 4, 4, 5, 5, 7, 9});
        System.out.println("mean = " + r[0]);
        System.out.println("average squared distance = " + r[1]);
        System.out.println("square root of that = " + Math.sqrt(r[1]));
    }
}
''')

K.code('p_sqrt', py=r'''
def my_sqrt(s, steps=5):
    guess = s / 2                       # any positive start works
    for k in range(1, steps + 1):
        guess = (guess + s / guess) / 2 # average the guess and s / guess
        print(f"step {k}: {guess:.6f}")
    return guess


my_sqrt(10)
print(f"true value: {10 ** 0.5:.6f}")
''', js=r'''
function mySqrt(s, steps = 5) {
  let guess = s / 2;                    // any positive start works
  for (let k = 1; k <= steps; k++) {
    guess = (guess + s / guess) / 2;    // average the guess and s / guess
    console.log(`step ${k}: ${guess.toFixed(6)}`);
  }
  return guess;
}

mySqrt(10);
console.log(`true value: ${Math.sqrt(10).toFixed(6)}`);
''', ts=r'''
function mySqrt(s: number, steps: number = 5): number {
  let guess: number = s / 2;            // any positive start works
  for (let k = 1; k <= steps; k++) {
    guess = (guess + s / guess) / 2;    // average the guess and s / guess
    console.log(`step ${k}: ${guess.toFixed(6)}`);
  }
  return guess;
}

mySqrt(10);
console.log(`true value: ${Math.sqrt(10).toFixed(6)}`);
''', java=r'''
public class PracticeSqrt {
    static double mySqrt(double s, int steps) {
        double guess = s / 2;                   // any positive start works
        for (int k = 1; k <= steps; k++) {
            guess = (guess + s / guess) / 2;    // average the guess and s / guess
            System.out.println(String.format("step %d: %.6f", k, guess));
        }
        return guess;
    }

    public static void main(String[] args) {
        mySqrt(10, 5);
        System.out.println(String.format("true value: %.6f", Math.sqrt(10)));
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('why', '🗺️', 'Why machine learning needs maths', f'''
<p>A machine learning model is a <b>function with knobs</b>. You give it numbers (the size of a house, the pixels of a photo, the words of a message) and it gives back a number (a price, the word "cat", the chance that a message is spam). Learning means turning the knobs until the answers come out right. Maths is the language that describes the knobs, the answers and the turning.</p>
<div class="grid2">
<div class="box"><h4>🏠 A tiny model</h4><p>price = 3 × area + 50. The numbers 3 and 50 are the knobs. If a house of 100 square metres really sold for 340, the model says 3 × 100 + 50 = 350, so it is 10 too high. Training nudges 3 and 50 until such errors become small.</p></div>
<div class="box"><h4>🧭 Four branches of maths</h4><p><b>Algebra</b> writes the model. <b>Linear algebra</b> handles thousands of inputs at once. <b>Calculus</b> tells each knob which way to turn. <b>Probability and statistics</b> measure how sure the model is.</p></div>
</div>
<p>This subject starts at school level and climbs to the level asked in machine learning interviews. Every idea comes with a picture or an animation, an everyday example, a program in four languages and problems with full working.</p>
<div class="roadmap">
<div>🌱 Numbers and algebra<small>Chapter 1</small></div><div>📈 Functions, exponents, logs<small>Chapter 2</small></div><div>➡️ Vectors<small>Chapter 3</small></div><div>🔢 Matrices<small>Chapter 4</small></div><div>🌀 Eigenvalues, SVD, PCA<small>Chapter 5</small></div><div>📉 Derivatives<small>Chapter 6</small></div><div>🧭 Gradients and chain rule<small>Chapter 7</small></div><div>⛰️ Gradient descent<small>Chapter 8</small></div><div>🎲 Probability and Bayes<small>Chapter 9</small></div><div>🔔 Distributions<small>Chapter 10</small></div><div>📊 Statistics<small>Chapter 11</small></div><div>🔥 Entropy and loss<small>Chapter 12</small></div><div>🧱 Decompositions and tensors<small>Chapter 13</small></div><div>🧠 Taylor, Newton, autodiff<small>Chapter 14</small></div><div>🎰 Bayesian inference and sampling<small>Chapter 15</small></div>
</div>
{ml('Every model you will meet later (linear regression, logistic regression, neural networks, transformers) is built from the same pieces in this list. When a paper writes a scary formula, it is almost always these pieces glued together.')}
''', kw=['why maths', 'roadmap', 'model', 'parameters', 'weights']),

    part('numbers', '🔢', 'Kinds of numbers and how computers store them', f'''
<p>Numbers come in families. Each family is bigger than the one before and contains it.</p>
{table(['Family', 'Symbol', 'Examples', 'Everyday use'], [
        ['Natural numbers', 'ℕ', '1, 2, 3, 4', 'Counting apples, number of rows in a dataset'],
        ['Whole numbers', '', '0, 1, 2, 3', 'Number of goals, zero included'],
        ['Integers', 'ℤ', '−3, −1, 0, 2', 'Temperature below zero, a bank balance'],
        ['Rational numbers', 'ℚ', '½, 0.75, −4/3', 'Any value you can write as one whole number over another'],
        ['Irrational numbers', '', '√2, π, e', 'Decimals that never end and never repeat'],
        ['Real numbers', 'ℝ', 'all of the above', 'Every point on the number line. Model inputs live here'],
    ])}
{viz('numline')}
<h3>Computers round real numbers</h3>
<p>A computer keeps a real number in a fixed number of binary digits, usually 64 bits. Most decimals, such as 0.1, cannot be written exactly in binary, just as ⅓ cannot be written exactly as a decimal (0.3333...). So the computer keeps the nearest value it can, and tiny rounding errors appear.</p>
{code('float_precision', 'Rounding in floating point numbers')}
<div class="warn">Never test two decimal results with <code>==</code>. Test whether they are close: <code>abs(a − b) &lt; 1e-9</code>. NumPy calls this <code>np.isclose</code>, and PyTorch calls it <code>torch.allclose</code>.</div>
{ml('Neural networks often train with 32 bit or even 16 bit numbers to save memory and time. Fewer bits means bigger rounding, which is why tricks such as loss scaling and the log sum exp trick (Chapter 12) exist.')}
''', kw=['natural numbers', 'integers', 'rational', 'irrational', 'real numbers', 'floating point', '0.1 + 0.2']),

    part('order', '➗', 'Order of operations, fractions and percentages', f'''
<p>When an expression mixes operations, everyone must work it out in the same order, or two people would get two different answers. The order is <b>B</b>rackets, <b>O</b>rders (powers and roots), <b>D</b>ivision and <b>M</b>ultiplication from left to right, then <b>A</b>ddition and <b>S</b>ubtraction from left to right.</p>
{fxs(fx('BODMAS (also called PEMDAS)', 'B → O → D·M → A·S', 'Division and multiplication have equal rank, so go left to right. The same is true for addition and subtraction.'),
         fx('Percentage', f'percent = {frac("part", "whole")} × 100', 'Accuracy of 46 correct out of 50 is 46 ÷ 50 × 100 = 92%.'),
         fx('Percentage change', f'change = {frac("new − old", "old")} × 100', 'Going from 80% to 92% accuracy is a 15% improvement, not 12%.'))}
{worked('Work out 8 + 2 × (7 − 3)² ÷ 4', [
        'Brackets first: <span class="eq">7 − 3 = 4</span> so the expression becomes 8 + 2 × 4² ÷ 4',
        'Orders (powers) next: <span class="eq">4² = 16</span> so it becomes 8 + 2 × 16 ÷ 4',
        'Multiplication and division from left to right: <span class="eq">2 × 16 = 32</span> then <span class="eq">32 ÷ 4 = 8</span>',
        'Addition last: <span class="eq">8 + 8 = 16</span>',
        'The answer is <b>16</b>. A calculator that works strictly left to right would wrongly give a different value.'])}
<h3>Fractions in one minute</h3>
<p>A fraction {frac('a', 'b')} means a parts out of b equal parts. To add fractions, make the bottoms (denominators) equal first: {frac(1, 2)} + {frac(1, 3)} = {frac(3, 6)} + {frac(2, 6)} = {frac(5, 6)}. To multiply, multiply tops and bottoms: {frac(2, 3)} × {frac(3, 4)} = {frac(6, 12)} = {frac(1, 2)}. To divide, flip the second fraction and multiply.</p>
{code('percent', 'Accuracy, percentage change and a discount')}
{life('A shop says "20% off, then another 10% off". That is not 30% off. You pay 0.8 × 0.9 = 0.72 of the price, which is 28% off. Percentages that follow each other multiply.')}
{trick('Percent means "per hundred". To find 15% of anything, find 10% (move the decimal point once) and add half of it. 15% of 240 is 24 + 12 = 36.')}
''', kw=['BODMAS', 'PEMDAS', 'order of operations', 'fractions', 'percentage', 'percentage change', 'accuracy']),

    part('algebra', '⚖️', 'Variables, expressions and equations', f'''
<p>A <b>variable</b> is a box with a name, such as x, that holds a number we do not know yet. An <b>expression</b> such as 3x + 5 is a recipe that uses the box. An <b>equation</b> such as 3x + 5 = 20 says two things are equal, and solving it means finding what is in the box.</p>
<p>The golden rule: an equation is a balanced scale. Whatever you do to one side, do to the other side, and it stays balanced.</p>
{viz('balance')}
{code('solve_linear', 'Solve a·x + b = c step by step')}
<h3>Two unknowns need two equations</h3>
<p>Two burgers and one juice cost 250. One burger and three juices also cost 250. Write b for a burger and j for a juice: 2b + j = 250 and b + 3j = 250. Multiply the first equation by 3 to get 6b + 3j = 750, subtract the second one, and the juices cancel: 5b = 500, so b = 100 and j = 50.</p>
{fx('Two equations, two unknowns (Cramer rule)', f'a₁x + b₁y = c₁ and a₂x + b₂y = c₂ give x = {frac("c₁b₂ − c₂b₁", "a₁b₂ − a₂b₁")} and y = {frac("a₁c₂ − a₂c₁", "a₁b₂ − a₂b₁")}', 'The bottom part a₁b₂ − a₂b₁ is called the determinant. If it is 0, the two lines are parallel and there is no single answer. Chapter 4 meets it again.')}
{code('two_equations', 'Burgers and juices with elimination')}
{ml('Linear regression with one input solves exactly this kind of problem. Its two knobs, the slope and the intercept, come from two equations called the normal equations. With many inputs, the same idea becomes a matrix equation, which Chapter 4 solves.')}
{trick('Think of "undoing" the steps in reverse order, like taking off socks and shoes. The equation 3x + 5 = 20 was built by "times 3, then plus 5". So undo it with "minus 5, then divide by 3".')}
''', kw=['variable', 'expression', 'equation', 'solve for x', 'linear equation', 'simultaneous equations', 'elimination', 'cramer rule']),

    part('powers', '⚡', 'Powers, roots and scientific notation', f'''
<p>A power is repeated multiplication: 2⁵ = 2 × 2 × 2 × 2 × 2 = 32. The small number 5 is the <b>exponent</b> and 2 is the <b>base</b>.</p>
{table(['Rule', 'In symbols', 'Example'], [
        ['Multiply, add the exponents', 'aᵐ × aⁿ = aᵐ⁺ⁿ', '2³ × 2⁴ = 2⁷ = 128'],
        ['Divide, subtract the exponents', 'aᵐ ÷ aⁿ = aᵐ⁻ⁿ', '2¹⁰ ÷ 2⁷ = 2³ = 8'],
        ['Power of a power, multiply', '(aᵐ)ⁿ = aᵐⁿ', '(2³)² = 2⁶ = 64'],
        ['Anything to the power 0', 'a⁰ = 1', '5⁰ = 1'],
        ['Negative exponent, flip it', f'a⁻ⁿ = {frac(1, "aⁿ")}', f'2⁻³ = {frac(1, 8)} = 0.125'],
        ['Fractional exponent, a root', 'a^(1/n) = ⁿ√a', '9^(1/2) = √9 = 3'],
    ])}
{code('powers', 'The exponent rules, checked by the computer')}
<h3>Scientific notation</h3>
<p>Very big and very small numbers are written as a number between 1 and 10 times a power of 10. The distance to the Sun is about 1.5 × 10⁸ km. A typical learning rate is 3 × 10⁻⁴ = 0.0003. Programs write this as <code>3e-4</code>, where e means "times ten to the power".</p>
{trick('The exponent of 10 tells you how many places to move the decimal point. Positive moves right (bigger), negative moves left (smaller). 2.5e3 = 2500 and 2.5e-3 = 0.0025.')}
{life('A virus that doubles every day turns 1 case into 2¹⁰ = 1024 cases in 10 days. Powers grow shockingly fast, which is why "exponential growth" became a household phrase in 2020.')}
{ml('Model sizes are counted with powers of ten: a model with 7 × 10⁹ parameters is a "7B" model. Learning rates such as 1e-3 and 1e-5 and the tiny epsilon 1e-8 that stops a division by zero are all scientific notation.')}
''', kw=['exponent', 'power', 'root', 'square root', 'scientific notation', 'exponent rules', '1e-3', 'learning rate']),

    part('sigma', 'Σ', 'Sigma and Pi notation: the maths shorthand', f'''
<p>Machine learning formulas add up many terms at once. Writing x₁ + x₂ + x₃ + ... + xₙ is slow, so mathematicians use the Greek capital letter sigma, Σ, which means "sum".</p>
{fxs(fx('Sigma means add them all', '<span class="sm">n</span><br>Σ xᵢ = x₁ + x₂ + ... + xₙ<br><span class="sm">i = 1</span>', 'i is a counter that starts at the number below and stops at the number on top. Read it as "the sum of x i, for i from 1 to n".'),
         fx('Mean (average)', f'x̄ = {frac(1, "n")} Σ xᵢ', 'Add everything and divide by how many there are. The bar on top of x is read "x bar".'),
         fx('Capital pi means multiply them all', 'Π xᵢ = x₁ × x₂ × ... × xₙ', 'Probabilities of independent events multiply, so Π appears in likelihoods (Chapter 11).'))}
{viz('sigma')}
{code('sigma', 'Sigma and pi are loops')}
<div class="rule">Σ is a for loop. The counter under the Σ is the loop variable, the numbers under and over it are where the loop starts and stops, and the expression after it is the loop body that gets added.</div>
{worked('Work out Σ (2i + 1) for i = 1 to 4', [
        'Write each term by putting i = 1, 2, 3, 4 into 2i + 1',
        'i = 1 gives <span class="eq">2 × 1 + 1 = 3</span>',
        'i = 2 gives <span class="eq">2 × 2 + 1 = 5</span>',
        'i = 3 gives <span class="eq">2 × 3 + 1 = 7</span>, and i = 4 gives <span class="eq">2 × 4 + 1 = 9</span>',
        'Add the terms: <span class="eq">3 + 5 + 7 + 9 = 24</span>',
        'Shortcut check: Σ 2i + Σ 1 = 2 × (1 + 2 + 3 + 4) + 4 = 20 + 4 = 24'])}
{trick('Gauss as a schoolboy added 1 + 2 + ... + 100 by pairing the first and last numbers: 1 + 100, 2 + 99 and so on make 50 pairs of 101, so the total is 5050. In general Σ i from 1 to n = n(n + 1) ÷ 2.')}
{ml('The mean squared error, the most common loss in regression, is (1/n) Σ (yᵢ − ŷᵢ)². It is only a sigma, a subtraction and a square. Once you can read Σ, half of every ML paper becomes readable.')}
''', kw=['sigma notation', 'summation', 'sum', 'mean', 'average', 'pi notation', 'product', 'gauss']),

    part('abs', '📏', 'Absolute value, inequalities and distance', f'''
<p>The <b>absolute value</b> |x| is the distance of x from zero, so it is never negative: |5| = 5 and |−5| = 5. The distance between two numbers a and b is |a − b|, whichever is bigger.</p>
{fxs(fx('Absolute value', '|x| = x if x ≥ 0, and −x if x &lt; 0', 'It removes the minus sign. |3 − 7| = |−4| = 4.'),
         fx('Mean absolute error', f'MAE = {frac(1, "n")} Σ |yᵢ − ŷᵢ|', 'y is the true value and ŷ (read "y hat") is the prediction. Average distance between them.'))}
<p>An <b>inequality</b> compares sizes: &lt; less than, ≤ less than or equal, &gt; greater than, ≥ greater than or equal. Solve it like an equation, with one twist: <b>multiplying or dividing both sides by a negative number flips the sign</b>. From −2x &lt; 6 we get x &gt; −3.</p>
{code('mae', 'Prediction errors as distances')}
{table(['Written', 'Meaning', 'On the number line'], [
        ['|x| &lt; 3', 'x is closer than 3 to zero', 'between −3 and 3, written (−3, 3)'],
        ['|x − 10| ≤ 2', 'x is within 2 of 10', 'from 8 to 10 inclusive, written [8, 12]'],
        ['x ≥ 0', 'x is not negative', 'zero and everything to its right'],
    ])}
<div class="exam">|x − 10| ≤ 2 means 8 ≤ x ≤ 12, not 8 ≤ x ≤ 10. Students often forget the right half of the interval.</div>
{life('A weather app that says "25 °C, give or take 2" is saying |true temperature − 25| ≤ 2. A cricket bowler is allowed to bend the elbow by at most 15 degrees: |bend| ≤ 15.')}
{ml('ReLU, the most used activation in neural networks, is max(0, x). The L1 penalty in Lasso regression adds Σ|wᵢ| to the loss. Both are close cousins of the absolute value.')}
''', kw=['absolute value', 'modulus', 'distance', 'inequality', 'interval', 'mean absolute error', 'MAE']),
]

INFO = {
    'title': 'Numbers are the language of models',
    'panels': [
        {'s': [['e', '🧮'], ['t', 'price = 3 × area + 50', {'b': 1}]], 'h': 'A model is a recipe', 't': 'Numbers in, a number out.', 'more': 'The 3 and the 50 are knobs that training adjusts until the predictions match real prices.'},
        {'s': [['e', '⚖️'], ['t', '3x + 5 = 20  →  x = 5', {'b': 1}]], 'h': 'Equations balance', 't': 'Do the same to both sides.', 'more': 'Undo the steps in reverse: subtract 5, then divide by 3.'},
        {'s': [['e', 'Σ'], ['c', [4, 8, 6, 2]], ['t', 'sum = 20, mean = 5']], 'h': 'Sigma is a loop', 't': 'Add every term.', 'more': 'Mean, variance and the mean squared error are all written with Σ.'},
        {'s': [['e', '📏'], ['t', '|300 − 280| = 20', {'b': 1}]], 'h': 'Errors are distances', 't': 'Absolute value drops the sign.', 'more': 'The mean absolute error averages these distances over all predictions.'},
    ],
    'remember': 'Brackets, then powers, then multiply and divide, then add and subtract. Keep equations balanced. Σ means add them all up, and |x| is a distance.',
}

REAL = [
    ['🛒', 'Shopping discounts', 'Two discounts of 20% and 10% give 28% off, not 30%, because percentages that follow each other multiply: 0.8 × 0.9 = 0.72.'],
    ['🏏', 'Cricket run rate', 'A run rate is total runs ÷ overs, a mean in disguise. Needing 60 runs from 8 overs means solving 8x = 60, so x = 7.5 runs per over.'],
    ['📱', 'Phone battery estimate', 'Your phone predicts hours left from recent use. Its error, |predicted − actual|, is exactly what engineers average to judge the estimate.'],
]

K.say('top', 'Welcome',
      'Welcome to maths for machine learning. A model is a function with knobs, and learning means turning those knobs. In this first chapter we build the base: numbers, percentages, equations, powers, the sigma sign and absolute value.',
      'मशीन लर्निंग के लिए गणित में आपका स्वागत है। मॉडल एक function है जिसमें knobs होते हैं, और सीखने का मतलब है उन knobs को घुमाना। इस पहले अध्याय में हम नींव बनाएँगे: संख्याएँ, प्रतिशत, समीकरण, घात, sigma चिह्न और absolute value।',
      'ಮೆಷಿನ್ ಲರ್ನಿಂಗ್‌ಗಾಗಿ ಗಣಿತಕ್ಕೆ ಸ್ವಾಗತ. ಮಾದರಿ ಎಂದರೆ knobs ಇರುವ ಒಂದು function, ಮತ್ತು ಕಲಿಕೆ ಎಂದರೆ ಆ knobs ತಿರುಗಿಸುವುದು. ಈ ಮೊದಲ ಅಧ್ಯಾಯದಲ್ಲಿ ಸಂಖ್ಯೆಗಳು, ಶೇಕಡಾ, ಸಮೀಕರಣಗಳು, ಘಾತಗಳು, sigma ಚಿಹ್ನೆ ಮತ್ತು absolute value ಕಲಿಯುತ್ತೇವೆ.',
      'ମେସିନ ଲର୍ନିଂ ପାଇଁ ଗଣିତକୁ ସ୍ୱାଗତ। ମଡେଲ ହେଉଛି knobs ଥିବା ଏକ function, ଏବଂ ଶିଖିବା ମାନେ ସେହି knobs ଘୁରାଇବା। ଏହି ପ୍ରଥମ ଅଧ୍ୟାୟରେ ଆମେ ସଂଖ୍ୟା, ପ୍ରତିଶତ, ସମୀକରଣ, ଘାତ, sigma ଚିହ୍ନ ଓ absolute value ଶିଖିବା।',
      'مرحبًا بك في الرياضيات لتعلم الآلة. النموذج دالة لها مقابض، والتعلم يعني تدوير هذه المقابض. في هذا الفصل الأول نبني الأساس: الأعداد والنسب المئوية والمعادلات والقوى وعلامة سيغما والقيمة المطلقة.',
      'Willkommen bei Mathematik für maschinelles Lernen. Ein Modell ist eine Funktion mit Reglern, und Lernen heißt, diese Regler zu drehen. In diesem ersten Kapitel legen wir die Basis: Zahlen, Prozente, Gleichungen, Potenzen, das Summenzeichen und den Betrag.')
K.say('why', 'Why maths',
      'Algebra writes the model, linear algebra handles many inputs at once, calculus tells each knob which way to turn, and probability says how sure the model is. This subject climbs from school level to interview level.',
      'Algebra मॉडल लिखता है, linear algebra एक साथ कई inputs संभालता है, calculus हर knob को बताता है किस ओर घूमना है, और probability बताती है मॉडल कितना पक्का है।',
      'Algebra ಮಾದರಿಯನ್ನು ಬರೆಯುತ್ತದೆ, linear algebra ಅನೇಕ inputs ನಿರ್ವಹಿಸುತ್ತದೆ, calculus ಪ್ರತಿ knob ಯಾವ ಕಡೆ ತಿರುಗಬೇಕು ಎಂದು ಹೇಳುತ್ತದೆ, probability ಮಾದರಿ ಎಷ್ಟು ಖಚಿತ ಎಂದು ತಿಳಿಸುತ್ತದೆ.',
      'Algebra ମଡେଲ ଲେଖେ, linear algebra ଏକାଥରେ ଅନେକ inputs ସମ୍ଭାଳେ, calculus ପ୍ରତ୍ୟେକ knob କୁ କେଉଁ ଦିଗରେ ଘୁରିବ କହେ, ଏବଂ probability କହେ ମଡେଲ କେତେ ନିଶ୍ଚିତ।',
      'الجبر يكتب النموذج، والجبر الخطي يتعامل مع مدخلات كثيرة معًا، والتفاضل يخبر كل مقبض بالاتجاه الصحيح، والاحتمال يقيس ثقة النموذج.',
      'Algebra schreibt das Modell, lineare Algebra verarbeitet viele Eingaben zugleich, Analysis sagt jedem Regler, wohin er sich drehen soll, und Wahrscheinlichkeit misst, wie sicher das Modell ist.')
K.say('numbers', 'Kinds of numbers',
      'Numbers come in families: natural numbers, integers, rationals, irrationals, and all of them together are the real numbers. Computers round real numbers, so 0.1 plus 0.2 is not exactly 0.3. Always compare decimals with a small tolerance.',
      'संख्याएँ परिवारों में आती हैं: natural, integers, rational, irrational, और सब मिलकर real numbers। कंप्यूटर real numbers को round करता है, इसलिए 0.1 और 0.2 का जोड़ ठीक 0.3 नहीं होता।',
      'ಸಂಖ್ಯೆಗಳು ಕುಟುಂಬಗಳಲ್ಲಿ ಬರುತ್ತವೆ: natural, integers, rational, irrational, ಎಲ್ಲವೂ ಸೇರಿ real numbers. ಕಂಪ್ಯೂಟರ್ round ಮಾಡುವುದರಿಂದ 0.1 ಮತ್ತು 0.2 ರ ಮೊತ್ತ ನಿಖರವಾಗಿ 0.3 ಅಲ್ಲ.',
      'ସଂଖ୍ୟା ପରିବାରରେ ଆସେ: natural, integers, rational, irrational, ଏବଂ ସବୁ ମିଶି real numbers। କମ୍ପ୍ୟୁଟର round କରେ, ତେଣୁ 0.1 ଓ 0.2 ର ଯୋଗ ଠିକ 0.3 ନୁହେଁ।',
      'الأعداد عائلات: الطبيعية والصحيحة والنسبية وغير النسبية، وكلها معًا الأعداد الحقيقية. الحاسوب يقرّب الأعداد، لذلك 0.1 زائد 0.2 لا يساوي 0.3 تمامًا.',
      'Zahlen bilden Familien: natürliche, ganze, rationale und irrationale Zahlen, zusammen die reellen Zahlen. Computer runden, darum ist 0,1 plus 0,2 nicht genau 0,3. Vergleiche Dezimalzahlen immer mit einer kleinen Toleranz.')
K.say('order', 'Order and percentages',
      'Work out brackets first, then powers, then multiplication and division from left to right, then addition and subtraction. A percentage is part over whole times one hundred, and a percentage change divides by the old value.',
      'पहले brackets, फिर powers, फिर बाएँ से दाएँ गुणा और भाग, फिर जोड़ और घटाव। प्रतिशत है भाग बटा पूरा गुणा सौ, और प्रतिशत बदलाव में पुराने मान से भाग देते हैं।',
      'ಮೊದಲು brackets, ನಂತರ powers, ನಂತರ ಎಡದಿಂದ ಬಲಕ್ಕೆ ಗುಣಾಕಾರ ಮತ್ತು ಭಾಗಾಕಾರ, ಕೊನೆಗೆ ಕೂಡಿಸು ಮತ್ತು ಕಳೆ. ಶೇಕಡಾ ಎಂದರೆ ಭಾಗ ಭಾಗಿಸು ಪೂರ್ಣ ಗುಣಿಸು ನೂರು.',
      'ପ୍ରଥମେ brackets, ପରେ powers, ତାପରେ ବାମରୁ ଡାହାଣକୁ ଗୁଣନ ଓ ହରଣ, ଶେଷରେ ଯୋଗ ଓ ବିୟୋଗ। ପ୍ରତିଶତ ହେଉଛି ଅଂଶ ହରଣ ପୂର୍ଣ୍ଣ ଗୁଣନ ଶହେ।',
      'نحسب الأقواس أولًا، ثم القوى، ثم الضرب والقسمة من اليسار إلى اليمين، ثم الجمع والطرح. النسبة المئوية هي الجزء على الكل ضرب مئة.',
      'Zuerst Klammern, dann Potenzen, dann Mal und Geteilt von links nach rechts, dann Plus und Minus. Ein Prozentsatz ist Teil durch Ganzes mal hundert, und eine prozentuale Änderung teilt durch den alten Wert.')
K.say('algebra', 'Equations',
      'An equation is a balanced scale. Whatever you do to one side, do to the other. To solve three x plus five equals twenty, subtract five from both sides, then divide both sides by three, and x is five.',
      'समीकरण एक संतुलित तराज़ू है। जो एक तरफ करें, वही दूसरी तरफ भी करें। तीन x जमा पाँच बराबर बीस में दोनों तरफ से पाँच घटाएँ, फिर तीन से भाग दें, तो x पाँच है।',
      'ಸಮೀಕರಣ ಒಂದು ಸಮತೋಲನದ ತಕ್ಕಡಿ. ಒಂದು ಕಡೆ ಮಾಡಿದುದನ್ನು ಇನ್ನೊಂದು ಕಡೆಯೂ ಮಾಡಿ. ಮೂರು x ಸೇರಿಸು ಐದು ಸಮ ಇಪ್ಪತ್ತು ಆದರೆ ಎರಡೂ ಕಡೆ ಐದು ಕಳೆದು ಮೂರರಿಂದ ಭಾಗಿಸಿ, x ಐದು.',
      'ସମୀକରଣ ଏକ ସନ୍ତୁଳିତ ତରାଜୁ। ଗୋଟିଏ ପାର୍ଶ୍ୱରେ ଯାହା କରିବେ, ଅନ୍ୟ ପାର୍ଶ୍ୱରେ ମଧ୍ୟ କରନ୍ତୁ। ତିନି x ଯୋଗ ପାଞ୍ଚ ସମାନ କୋଡ଼ିଏରେ ଦୁଇ ପାର୍ଶ୍ୱରୁ ପାଞ୍ଚ ବିୟୋଗ କରି ତିନିରେ ହରଣ କଲେ x ପାଞ୍ଚ।',
      'المعادلة ميزان متوازن. ما تفعله في طرف افعله في الطرف الآخر. لحل ثلاثة س زائد خمسة يساوي عشرين اطرح خمسة من الطرفين ثم اقسم على ثلاثة فيكون س خمسة.',
      'Eine Gleichung ist eine Waage im Gleichgewicht. Was du auf einer Seite tust, tust du auch auf der anderen. Bei drei x plus fünf gleich zwanzig ziehst du fünf ab und teilst durch drei, also ist x fünf.')
K.say('powers', 'Powers',
      'A power is repeated multiplication. Multiplying powers adds the exponents, dividing subtracts them, and a negative exponent flips the number into a fraction. Scientific notation writes three times ten to the minus four as three e minus four.',
      'घात बार बार गुणा है। घातों को गुणा करने पर exponents जुड़ते हैं, भाग देने पर घटते हैं, और negative exponent संख्या को भिन्न में उलट देता है। तीन गुणा दस की घात minus चार को three e minus four लिखते हैं।',
      'ಘಾತ ಎಂದರೆ ಮತ್ತೆ ಮತ್ತೆ ಗುಣಾಕಾರ. ಘಾತಗಳನ್ನು ಗುಣಿಸಿದಾಗ exponents ಕೂಡುತ್ತವೆ, ಭಾಗಿಸಿದಾಗ ಕಳೆಯುತ್ತವೆ, negative exponent ಸಂಖ್ಯೆಯನ್ನು ಭಿನ್ನರಾಶಿಯಾಗಿ ತಿರುಗಿಸುತ್ತದೆ.',
      'ଘାତ ହେଉଛି ବାରମ୍ବାର ଗୁଣନ। ଘାତ ଗୁଣନ କଲେ exponents ଯୋଗ ହୁଏ, ହରଣ କଲେ ବିୟୋଗ ହୁଏ, ଏବଂ negative exponent ସଂଖ୍ୟାକୁ ଭଗ୍ନାଂଶରେ ଓଲଟାଏ।',
      'القوة ضرب متكرر. عند ضرب القوى نجمع الأسس، وعند القسمة نطرحها، والأس السالب يقلب العدد إلى كسر. ونكتب ثلاثة في عشرة أس سالب أربعة هكذا 3e-4.',
      'Eine Potenz ist wiederholte Multiplikation. Beim Multiplizieren addiert man die Exponenten, beim Teilen subtrahiert man sie, und ein negativer Exponent macht einen Bruch daraus. Drei mal zehn hoch minus vier schreibt man 3e-4.')
K.say('sigma', 'Sigma',
      'The Greek letter sigma means add them all. The counter under it says where to start, the number on top says where to stop. Sigma is simply a for loop that keeps adding, and capital pi is a loop that keeps multiplying.',
      'ग्रीक अक्षर sigma का मतलब है सबको जोड़ो। नीचे का counter बताता है कहाँ से शुरू करें, ऊपर की संख्या बताती है कहाँ रुकें। Sigma बस एक for loop है जो जोड़ता रहता है।',
      'ಗ್ರೀಕ್ ಅಕ್ಷರ sigma ಎಂದರೆ ಎಲ್ಲವನ್ನೂ ಕೂಡಿಸು. ಕೆಳಗಿನ counter ಎಲ್ಲಿಂದ ಆರಂಭ, ಮೇಲಿನ ಸಂಖ್ಯೆ ಎಲ್ಲಿ ನಿಲ್ಲಬೇಕು ಎಂದು ಹೇಳುತ್ತದೆ. Sigma ಕೂಡಿಸುತ್ತಲೇ ಇರುವ ಒಂದು for loop.',
      'ଗ୍ରୀକ ଅକ୍ଷର sigma ର ଅର୍ଥ ସବୁକୁ ଯୋଗ କର। ତଳ counter କେଉଁଠୁ ଆରମ୍ଭ, ଉପର ସଂଖ୍ୟା କେଉଁଠି ଅଟକିବ କହେ। Sigma ହେଉଛି ଯୋଗ କରୁଥିବା ଏକ for loop।',
      'الحرف اليوناني سيغما يعني اجمعها كلها. العداد في الأسفل يحدد البداية والعدد في الأعلى يحدد النهاية. سيغما مجرد حلقة تكرار تواصل الجمع، وباي الكبيرة حلقة تواصل الضرب.',
      'Das griechische Sigma heißt: alles addieren. Der Zähler unten sagt, wo man beginnt, die Zahl oben, wo man aufhört. Sigma ist einfach eine Schleife, die immer weiter addiert, und das große Pi multipliziert.')
K.say('abs', 'Absolute value',
      'The absolute value of a number is its distance from zero, so it is never negative. The distance between a prediction and the truth is the absolute value of their difference. When you multiply an inequality by a negative number, flip the sign.',
      'किसी संख्या का absolute value उसकी शून्य से दूरी है, इसलिए यह कभी negative नहीं होता। prediction और सच्चाई के बीच की दूरी उनके अंतर का absolute value है। inequality को negative से गुणा करें तो चिह्न उलट दें।',
      'ಸಂಖ್ಯೆಯ absolute value ಅದರ ಸೊನ್ನೆಯಿಂದ ಇರುವ ದೂರ, ಆದ್ದರಿಂದ ಅದು ಎಂದೂ negative ಅಲ್ಲ. prediction ಮತ್ತು ಸತ್ಯದ ನಡುವಿನ ದೂರ ಅವುಗಳ ವ್ಯತ್ಯಾಸದ absolute value.',
      'ସଂଖ୍ୟାର absolute value ହେଉଛି ଶୂନରୁ ତାର ଦୂରତା, ତେଣୁ ଏହା କେବେ negative ନୁହେଁ। prediction ଓ ସତ୍ୟ ମଧ୍ୟରେ ଦୂରତା ସେମାନଙ୍କ ପାର୍ଥକ୍ୟର absolute value।',
      'القيمة المطلقة للعدد هي بعده عن الصفر، لذلك لا تكون سالبة أبدًا. والمسافة بين التنبؤ والحقيقة هي القيمة المطلقة للفرق بينهما. وعند ضرب المتباينة في عدد سالب نقلب الإشارة.',
      'Der Betrag einer Zahl ist ihr Abstand von null und daher nie negativ. Der Abstand zwischen Vorhersage und Wahrheit ist der Betrag ihrer Differenz. Multiplizierst du eine Ungleichung mit einer negativen Zahl, dreht sich das Zeichen um.')
K.say('practice', 'Practice',
      'Time to practise. Solve each problem on paper first, open the hint if you are stuck, and then compare with the full working. The programs are written in Python, JavaScript, TypeScript and Java, and you can run them line by line.',
      'अब अभ्यास का समय है। हर सवाल पहले कागज़ पर हल करें, अटकें तो hint खोलें, फिर पूरा हल देखें। Programs Python, JavaScript, TypeScript और Java में हैं और line by line चल सकते हैं।',
      'ಈಗ ಅಭ್ಯಾಸದ ಸಮಯ. ಪ್ರತಿ ಸಮಸ್ಯೆಯನ್ನು ಮೊದಲು ಕಾಗದದಲ್ಲಿ ಬಿಡಿಸಿ, ಸಿಲುಕಿದರೆ hint ತೆರೆಯಿರಿ, ನಂತರ ಪೂರ್ಣ ಪರಿಹಾರ ನೋಡಿ.',
      'ଏବେ ଅଭ୍ୟାସ ସମୟ। ପ୍ରତ୍ୟେକ ପ୍ରଶ୍ନ ପ୍ରଥମେ କାଗଜରେ ସମାଧାନ କରନ୍ତୁ, ଅଟକିଲେ hint ଖୋଲନ୍ତୁ, ତାପରେ ପୂର୍ଣ୍ଣ ସମାଧାନ ଦେଖନ୍ତୁ।',
      'حان وقت التدريب. حل كل مسألة على الورق أولًا، وافتح التلميح إن توقفت، ثم قارن بالحل الكامل. البرامج مكتوبة بأربع لغات ويمكن تشغيلها سطرًا بسطر.',
      'Zeit zum Üben. Löse jede Aufgabe zuerst auf Papier, öffne den Hinweis, wenn du feststeckst, und vergleiche dann mit dem vollständigen Lösungsweg. Die Programme gibt es in vier Sprachen, Zeile für Zeile ausführbar.')

# ---------------------------------------------------------------- practice
K.practice('solve-linear', 'e', 'Solve any a·x + b = c', 'p_linear',
           '<p>Write a function that returns x for the equation a·x + b = c. Test it on 2x + 3 = 11, 5x − 4 = 21, −3x + 9 = 0 and 4x + 1 = 3.</p>',
           '2x + 3 = 11  ->  x = 4.00\n5x + -4 = 21  ->  x = 5.00\n-3x + 9 = 0  ->  x = 3.00\n4x + 1 = 3  ->  x = 0.50',
           'Undo the "plus b" first, then undo the "times a".',
           '<p>Subtracting b from both sides leaves a·x = c − b. Dividing both sides by a leaves x = (c − b) ÷ a. One line of code does both steps. If a is 0 there is no x term at all, so a real program should check for that before dividing.</p>',
           'O(1)', 'O(1)')
K.practice('compound', 'm', 'Growth by a percentage every year', 'p_compound',
           '<p>Savings of 1000 grow by 10% every year. Print the value after each of 3 years, then check the answer with the formula start × (1 + r)ⁿ.</p>',
           'year 1: 1100.00\nyear 2: 1210.00\nyear 3: 1331.00',
           'Growing by 10% means multiplying by 1.1, not adding 100 every year.',
           '<p>Each year the value is multiplied by 1 + 10 ÷ 100 = 1.1. After n years that is 1.1 multiplied n times, which is the power 1.1ⁿ. So 1000 × 1.1³ = 1331. The loop and the formula agree, which shows why powers describe repeated growth.</p>',
           'O(n)', 'O(1)')
K.practice('spread', 'h', 'Average squared distance from the mean', 'p_variance',
           '<p>For the list 2, 4, 4, 4, 5, 5, 7, 9 compute the mean, then the average of (xᵢ − mean)² and its square root. Write it with one loop for each Σ.</p>',
           'mean = 5.0\naverage squared distance = 4.0\nsquare root of that = 2.0',
           'First Σ gives the mean. Second Σ adds the squared distances from that mean.',
           '<p>The mean is 40 ÷ 8 = 5. The distances from 5 are −3, −1, −1, −1, 0, 0, 2, 4. Their squares are 9, 1, 1, 1, 0, 0, 4, 16, which add to 32. Dividing by 8 gives 4, and √4 = 2. These two numbers are the <b>variance</b> and the <b>standard deviation</b>, which Chapter 10 explains in depth.</p>',
           'O(n)', 'O(1)')
K.practice('babylon', 'x', 'Square roots by repeated averaging', 'p_sqrt',
           '<p>Find √10 without a square root button. Start with a guess g, then repeat g ← (g + 10 ÷ g) ÷ 2. Print 5 steps and compare with the true value.</p>',
           'step 1: 3.500000\nstep 2: 3.178571\n...\nstep 5: 3.162278',
           'If g is too big, 10 ÷ g is too small. Their average is closer than either one.',
           '<p>This is the Babylonian method, 4000 years old, and it is a special case of Newton method. Each step roughly doubles the number of correct digits. It is also your first taste of an <b>iterative algorithm</b>: start somewhere, improve a little, repeat. Gradient descent in Chapter 8 trains models in exactly this spirit.</p>',
           'O(steps)', 'O(1)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What is 6 + 4 × 3?', ['30', '18', '13', '24'], 1, 'Multiplication comes before addition.', '4 × 3 = 12 first, then 6 + 12 = 18.')
K.quiz('e', 'Which of these is an irrational number?', ['0.75', '−4', '√2', '22/7'], 2, 'Irrational decimals never end and never repeat.', '√2 = 1.41421356... has no repeating pattern. 22/7 is only an approximation of π, and it is rational.')
K.quiz('e', 'A model gets 45 out of 60 test questions right. What is its accuracy?', ['45%', '60%', '75%', '80%'], 2, 'Part over whole, times 100.', '45 ÷ 60 = 0.75, and 0.75 × 100 = 75%.')
K.quiz('e', 'What is |−7|?', ['−7', '7', '0', '49'], 1, 'Distance from zero.', 'Absolute value removes the minus sign, so |−7| = 7.')
K.quiz('e', 'What does Σ tell you to do?', ['Multiply all the terms', 'Add all the terms', 'Take the square root', 'Find the biggest term'], 1, 'Sigma is the Greek S, for sum.', 'Σ means add the terms. Capital Π means multiply them.')
K.quiz('m', 'Solve 5x − 7 = 18.', ['x = 2.2', 'x = 5', 'x = 25', 'x = 3'], 1, 'Add 7 to both sides first.', '5x = 25, then x = 25 ÷ 5 = 5. Check: 5 × 5 − 7 = 18.')
K.quiz('m', 'What is 2⁻²?', ['−4', '−0.25', '0.25', '4'], 2, 'A negative exponent flips the number.', '2⁻² = 1 ÷ 2² = 1 ÷ 4 = 0.25. A negative exponent never makes the answer negative.')
K.quiz('m', 'Accuracy rises from 80% to 88%. What is the percentage change?', ['8%', '10%', '12%', '88%'], 1, 'Divide the rise by the old value.', '(88 − 80) ÷ 80 × 100 = 8 ÷ 80 × 100 = 10%. The rise of 8 is called 8 percentage points.')
K.quiz('m', 'Why does <code>0.1 + 0.2 == 0.3</code> print False in most languages?', ['The language has a bug', '0.1 and 0.2 cannot be stored exactly in binary', 'Addition is not allowed on decimals', 'The values are stored as text'], 1, 'Think of writing 1/3 as a decimal.', 'Binary cannot hold 0.1 exactly, just as decimal cannot hold 1/3 exactly. The stored sum is 0.30000000000000004.')
K.quiz('m', 'Which interval is the same as |x − 4| ≤ 3?', ['1 ≤ x ≤ 7', '−3 ≤ x ≤ 3', '4 ≤ x ≤ 7', 'x ≤ 7'], 0, 'x is within 3 of 4.', 'Go 3 left and 3 right of 4: from 1 to 7.')
K.quiz('h', 'What is Σ i for i = 1 to 50?', ['1250', '1275', '2500', '2550'], 1, 'Use n(n + 1) ÷ 2.', '50 × 51 ÷ 2 = 2550 ÷ 2 = 1275.')
K.quiz('h', 'Solve −3x + 4 &gt; 10.', ['x &gt; −2', 'x &lt; −2', 'x &gt; 2', 'x &lt; 2'], 1, 'Dividing by a negative number flips the sign.', '−3x &gt; 6. Divide by −3 and flip: x &lt; −2. Check with x = −3: 9 + 4 = 13, which is bigger than 10.')
K.quiz('h', 'Two prices fall by 20% and then rise by 20%. Compared with the start, the price is', ['the same', '4% lower', '4% higher', '20% lower'], 1, 'Multiply 0.8 by 1.2.', '0.8 × 1.2 = 0.96, which is 4% less than the start. A percentage of a smaller number is a smaller amount.')
K.quiz('x', 'In the formula (1/n) Σ (yᵢ − ŷᵢ)², what does ŷᵢ stand for?', ['The true value of example i', 'The prediction for example i', 'The average of all y', 'The number of examples'], 1, 'The hat means "estimated".', 'ŷ (y hat) is what the model predicted. y is the true value. This formula is the mean squared error.')
K.quiz('x', 'A dataset has 3 × 10⁶ rows and each row has 2 × 10² numbers. How many numbers is that?', ['5 × 10⁸', '6 × 10⁸', '6 × 10¹²', '5 × 10¹²'], 1, 'Multiply the front numbers and add the exponents.', '3 × 2 = 6 and 10⁶ × 10² = 10⁸, so 6 × 10⁸ = 600 million numbers.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Work out 18 − 12 ÷ 4 + 2 × 3.', '21', 'Do division and multiplication before subtraction and addition.', [
    'Look for brackets and powers. There are none.',
    'Division: <span class="eq">12 ÷ 4 = 3</span>',
    'Multiplication: <span class="eq">2 × 3 = 6</span>',
    'Now only plus and minus are left, so go left to right: <span class="eq">18 − 3 + 6 = 15 + 6 = 21</span>',
], check=18 - 12 / 4 + 2 * 3)
K.calc('e', 'A spam filter checks 200 emails and labels 186 correctly. What is its accuracy in percent?', '93', 'Percent = part ÷ whole × 100.', [
    'The part is the number of correct labels: 186. The whole is all emails: 200.',
    'Divide: <span class="eq">186 ÷ 200 = 0.93</span>',
    'Multiply by 100 to turn it into a percentage: <span class="eq">0.93 × 100 = 93</span>',
    'So the accuracy is 93%.',
], check=186 / 200 * 100, unit='%')
K.calc('e', 'Solve 4x + 6 = 30.', '6', 'Subtract 6 from both sides, then divide by 4.', [
    'Start: <span class="eq">4x + 6 = 30</span>',
    'Take 6 away from both sides so the scale stays balanced: <span class="eq">4x = 24</span>',
    'Share both sides into 4 equal groups: <span class="eq">x = 24 ÷ 4 = 6</span>',
    'Check by putting 6 back in: 4 × 6 + 6 = 24 + 6 = 30. It matches.',
], check=(30 - 6) / 4)
K.calc('e', 'What is the mean of 12, 15, 9, 20 and 14?', '14', 'Add them all, then divide by how many there are.', [
    'Count the numbers: there are 5.',
    'Add them: <span class="eq">12 + 15 + 9 + 20 + 14 = 70</span>',
    'Divide by the count: <span class="eq">70 ÷ 5 = 14</span>',
    'In sigma notation this is x̄ = (1/5) Σ xᵢ = 14.',
], check=(12 + 15 + 9 + 20 + 14) / 5)
K.calc('e', 'Write 0.00052 in scientific notation and give the exponent of 10.', '-4', 'Move the decimal point until one non zero digit is in front of it.', [
    'Move the decimal point to the right until you get a number between 1 and 10: 0.00052 becomes 5.2.',
    'Count the moves: 0.00052 → 0.0052 → 0.052 → 0.52 → 5.2 is 4 moves.',
    'Moving right means the original number was small, so the exponent is negative.',
    'So 0.00052 = 5.2 × 10⁻⁴, and the exponent is −4.',
], check=-4, alt=['−4'])
K.calc('m', 'Work out (2³ × 2⁵) ÷ 2⁶.', '4', 'Add exponents when multiplying, subtract when dividing.', [
    'Multiply first by adding exponents: <span class="eq">2³ × 2⁵ = 2³⁺⁵ = 2⁸</span>',
    'Divide by subtracting exponents: <span class="eq">2⁸ ÷ 2⁶ = 2⁸⁻⁶ = 2²</span>',
    'Work out the power: <span class="eq">2² = 4</span>',
    'Check the long way: 8 × 32 = 256 and 256 ÷ 64 = 4.',
], check=(2 ** 3 * 2 ** 5) / 2 ** 6)
K.calc('m', 'A phone costs 15000. It gets 20% off, then a further 5% off the new price. What is the final price?', '11400', 'Turn each discount into a multiplier: 20% off means × 0.8.', [
    '20% off leaves 80% of the price. 80% = 0.8.',
    'After the first discount: <span class="eq">15000 × 0.8 = 12000</span>',
    '5% off leaves 95% = 0.95 of the new price: <span class="eq">12000 × 0.95 = 11400</span>',
    'In one line: 15000 × 0.8 × 0.95 = 15000 × 0.76 = 11400. The total discount is 24%, not 25%.',
], check=15000 * 0.8 * 0.95)
K.calc('m', 'Solve the pair 3x + 2y = 16 and x − y = 2. Give x.', '4', 'From the second equation, x = y + 2. Put that into the first.', [
    'The second equation says <span class="eq">x = y + 2</span>',
    'Substitute into the first: <span class="eq">3(y + 2) + 2y = 16</span>',
    'Open the bracket: <span class="eq">3y + 6 + 2y = 16</span>, so <span class="eq">5y + 6 = 16</span>',
    'Subtract 6 and divide by 5: <span class="eq">5y = 10, y = 2</span>',
    'Then <span class="eq">x = y + 2 = 4</span>. Check: 3 × 4 + 2 × 2 = 12 + 4 = 16. It works.',
], check=4)
K.calc('m', 'Work out Σ i² for i = 1 to 5.', '55', 'Write every term, then add.', [
    'The terms are 1², 2², 3², 4², 5².',
    'Square each one: <span class="eq">1, 4, 9, 16, 25</span>',
    'Add them: <span class="eq">1 + 4 + 9 + 16 + 25 = 55</span>',
    'Formula check: n(n + 1)(2n + 1) ÷ 6 = 5 × 6 × 11 ÷ 6 = 55.',
], check=sum(i * i for i in range(1, 6)))
K.calc('h', 'True prices are 300, 250 and 410. A model predicts 280, 270 and 400. What is the mean absolute error?', '16.67', 'Find each distance |true − predicted|, then average them. Round to 2 decimals.', [
    'First distance: <span class="eq">|300 − 280| = 20</span>',
    'Second distance: <span class="eq">|250 − 270| = |−20| = 20</span>. The minus sign disappears.',
    'Third distance: <span class="eq">|410 − 400| = 10</span>',
    'Add them: <span class="eq">20 + 20 + 10 = 50</span>',
    'Divide by 3 predictions: <span class="eq">50 ÷ 3 ≈ 16.67</span>',
], check=50 / 3, tol=0.006)
K.calc('h', 'Solve |2x − 6| = 10. Give the larger answer.', '8', 'The inside can be +10 or −10.', [
    'An absolute value equal to 10 means the inside is 10 or −10.',
    'Case 1: <span class="eq">2x − 6 = 10 → 2x = 16 → x = 8</span>',
    'Case 2: <span class="eq">2x − 6 = −10 → 2x = −4 → x = −2</span>',
    'Both work: |16 − 6| = 10 and |−4 − 6| = |−10| = 10. The larger answer is 8.',
], check=8)
K.calc('h', 'Work out 8^(2/3).', '4', 'A fractional exponent: the bottom is a root, the top is a power.', [
    'Split the exponent: 8^(2/3) means take the cube root, then square it.',
    'Cube root of 8: <span class="eq">∛8 = 2</span> because 2 × 2 × 2 = 8',
    'Square it: <span class="eq">2² = 4</span>',
    'So 8^(2/3) = 4. Doing the power first also works: 8² = 64 and ∛64 = 4.',
], check=8 ** (2 / 3), tol=1e-9)
K.calc('x', 'For the numbers 3, 7, 7, 19, work out Σ (xᵢ − x̄)², where x̄ is their mean.', '144', 'First find the mean, then the four squared distances.', [
    'Mean: <span class="eq">x̄ = (3 + 7 + 7 + 19) ÷ 4 = 36 ÷ 4 = 9</span>',
    'Distances from the mean: <span class="eq">3 − 9 = −6, 7 − 9 = −2, 7 − 9 = −2, 19 − 9 = 10</span>',
    'Square them: <span class="eq">36, 4, 4, 100</span>',
    'Add them: <span class="eq">36 + 4 + 4 + 100 = 144</span>',
    'Dividing by n = 4 gives 36, the variance, and √36 = 6 is the standard deviation.',
], check=sum((v - 9) ** 2 for v in [3, 7, 7, 19]))
K.calc('x', 'Starting from g = 2, do two steps of g ← (g + 5 ÷ g) ÷ 2 to estimate √5. Round to 4 decimals.', '2.2361', 'Step 1 uses g = 2. Step 2 uses the result of step 1.', [
    'Step 1: <span class="eq">g = (2 + 5 ÷ 2) ÷ 2 = (2 + 2.5) ÷ 2 = 2.25</span>',
    'Step 2: <span class="eq">5 ÷ 2.25 = 2.2222...</span>',
    'Average: <span class="eq">(2.25 + 2.2222) ÷ 2 = 4.4722 ÷ 2 = 2.2361</span>',
    'The true value is √5 = 2.23607, so two steps already give 4 correct decimals.',
], check=(2.25 + 5 / 2.25) / 2, tol=0.00006)

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { esc, $, shell, seg, wireSeg, Player, cell } = VIZ.kit;
  const W = VIZ.widgets;

  /* ----- where does a number live on the number line ----- */
  W.numline = el => {
    const b = shell(el, 'Place any number on the number line', 'Type a number such as 3, −2, 0.75, 1/3 or sqrt(2). The widget says which families it belongs to.');
    b.innerHTML = `<div class="mv-inp">Number <input type="text" value="0.75" aria-label="A number"> <button type="button">Place it</button>
      <span class="mv-btns">${['3', '-2', '0', '1/3', 'sqrt(2)', 'pi'].map(v => `<button type="button" data-v="${v}">${v}</button>`).join('')}</span></div>
      <div class="nl-host"></div><div class="mv-read" aria-live="polite"></div>`;
    const inp = $('input', b), host = $('.nl-host', b), out = $('.mv-read', b);
    function parse(t) {
      t = t.trim().toLowerCase().replace('−', '-');
      if (t === 'pi' || t === 'π') return { v: Math.PI, irr: true, txt: 'π' };
      if (t === 'e') return { v: Math.E, irr: true, txt: 'e' };
      let m = t.match(/^(-?)sqrt\((\d+(?:\.\d+)?)\)$/);
      if (m) { const r = +m[2], v = Math.sqrt(r) * (m[1] ? -1 : 1); return { v, irr: !Number.isInteger(Math.sqrt(r)), txt: (m[1] ? '−' : '') + '√' + r }; }
      m = t.match(/^(-?\d+)\/(\d+)$/);
      if (m && +m[2]) return { v: +m[1] / +m[2], irr: false, txt: t };
      if (/^-?(\d+\.?\d*|\.\d+)$/.test(t)) return { v: +t, irr: false, txt: t };
      return null;
    }
    function place() {
      const p = parse(inp.value);
      if (!p) { out.innerHTML = 'Try a number like 4, −1.5, 2/3 or sqrt(5).'; return; }
      const v = p.v, F = MV.frame(560, 90, [-5, 5], [-1, 1], 22);
      const x = Math.max(-5, Math.min(5, v));
      let s = `<line class="mv-axis" x1="22" y1="50" x2="538" y2="50"/>`;
      for (let k = -5; k <= 5; k++) s += `<line class="mv-axis" x1="${F.sx(k)}" y1="44" x2="${F.sx(k)}" y2="56"/><text class="mv-tick" x="${F.sx(k)}" y="74" text-anchor="middle">${k < 0 ? '−' + -k : k}</text>`;
      s += `<circle class="mv-pt o big" cx="${F.sx(x)}" cy="50" r="8"/><text class="mv-lab" x="${F.sx(x)}" y="30" text-anchor="middle">${esc(p.txt)}${Math.abs(v) > 5 ? ' (off the scale)' : ''}</text>`;
      host.innerHTML = MV.svg(F, s, 'Number line');
      const fam = [];
      const isInt = !p.irr && Number.isInteger(v);
      if (isInt && v > 0) fam.push('natural number');
      if (isInt && v >= 0) fam.push('whole number');
      if (isInt) fam.push('integer');
      if (!p.irr) fam.push('rational number'); else fam.push('irrational number');
      fam.push('real number');
      out.innerHTML = `<b>${esc(p.txt)}</b> ≈ ${MV.num(v, 6)} is a ${fam.map(f => `<b>${f}</b>`).join(', ')}.${p.irr ? ' Its decimals never end and never repeat, so a computer can only store an approximation.' : !isInt ? ' It can be written as one whole number over another.' : ''}`;
    }
    $('.mv-inp > button', b).onclick = place;
    inp.addEventListener('keydown', e => { if (e.key === 'Enter') place(); });
    b.querySelectorAll('[data-v]').forEach(x => x.onclick = () => { inp.value = x.dataset.v; place(); });
    place();
  };

  /* ----- a balance scale that solves a*x + b = c ----- */
  W.balance = el => {
    const b = shell(el, 'Keep the scale balanced', 'Choose a, b and c for a·x + b = c. Each step does the same thing to both pans until x is alone.');
    b.innerHTML = `<div class="mv-inp">a <input type="number" data-k="a" value="3"> b <input type="number" data-k="b" value="5"> c <input type="number" data-k="c" value="20"> <button type="button">Solve it</button></div>
      <div class="bal-host"></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const host = $('.bal-host', b), msg = $('.vz-msg', b);
    let st = [];
    const P = Player($('.vz-p', b), show, 1300);
    const n = v => MV.num(v, 3);
    function scale(L, R, tilt, note) {
      const t = tilt * 9;
      return `<svg class="mv-svg bal" viewBox="0 0 560 210" role="img" aria-label="Balance scale"><polygon points="280,120 262,190 298,190" class="bal-stand"/>
        <g style="transform:rotate(${t}deg); transform-origin:280px 120px; transition:transform .6s">
          <line x1="90" y1="120" x2="470" y2="120" class="bal-beam"/>
          <g style="transform:rotate(${-t}deg); transform-origin:130px 120px; transition:transform .6s"><rect x="40" y="128" width="180" height="46" rx="12" class="bal-pan"/><text x="130" y="158" text-anchor="middle" class="bal-txt">${esc(L)}</text></g>
          <g style="transform:rotate(${-t}deg); transform-origin:430px 120px; transition:transform .6s"><rect x="340" y="128" width="180" height="46" rx="12" class="bal-pan"/><text x="430" y="158" text-anchor="middle" class="bal-txt">${esc(R)}</text></g>
        </g><text x="280" y="40" text-anchor="middle" class="mv-lab">${esc(note)}</text></svg>`;
    }
    function setup() {
      const v = k => +$(`[data-k="${k}"]`, b).value;
      const a = v('a'), bb = v('b'), c = v('c');
      if (!a) { st = [{ L: `0x + ${n(bb)}`, R: n(c), t: 0, m: 'With a = 0 there is no x left to find. Pick a value of a that is not zero.', note: '' }]; P.load(1); return; }
      const sb = bb < 0 ? `− ${n(-bb)}` : `+ ${n(bb)}`, x = (c - bb) / a;
      st = [
        { L: `${n(a)}x ${sb}`, R: n(c), t: 0, note: `${n(a)}x ${sb} = ${n(c)}`, m: 'The scale is balanced: both pans weigh the same.' },
        { L: `${n(a)}x`, R: n(c), t: bb > 0 ? 1 : -1, note: bb > 0 ? `take ${n(bb)} from the left pan only` : `add ${n(-bb)} to the left pan only`, m: 'Changing only one pan tips the scale. The equation would now be false.' },
        { L: `${n(a)}x`, R: n(c - bb), t: 0, note: `${n(a)}x = ${n(c)} ${bb > 0 ? '−' : '+'} ${n(Math.abs(bb))} = ${n(c - bb)}`, m: 'Do the same to the right pan, and the scale balances again.' },
        { L: 'x', R: n(x), t: 0, note: `divide both pans by ${n(a)}:  x = ${n(c - bb)} ÷ ${n(a)} = ${n(x)}`, m: 'Sharing both pans into the same number of equal groups keeps the balance.' },
        { L: `${n(a)} × ${n(x)} ${sb}`, R: n(c), t: 0, note: `check: ${n(a)} × ${n(x)} ${sb} = ${n(a * x + bb)}`, m: Math.abs(a * x + bb - c) < 1e-9 ? '✅ Putting x back into the first equation gives c. The answer is right.' : 'The check is off by a rounding error only.' },
      ];
      P.load(st.length);
    }
    function show(i) { const s = st[i]; host.innerHTML = scale(s.L, s.R, s.t, s.note); msg.innerHTML = s.m; }
    $('button', b).onclick = setup;
    b.querySelectorAll('input').forEach(x => x.addEventListener('change', setup));
    setup();
  };

  /* ----- sigma and pi as a running loop ----- */
  W.sigma = el => {
    const b = shell(el, 'Watch Σ add one term at a time', 'Type your own numbers, pick what to add up, and press Play. The counter i moves along and the running total grows.');
    b.innerHTML = `<div class="mv-inp">Numbers <input type="text" value="4, 8, 6, 2" aria-label="Numbers separated by commas"> <button type="button">Use them</button></div>
      <div class="vz-row">${seg('f', [['x', 'Σ xᵢ'], ['sq', 'Σ xᵢ²'], ['dev', 'Σ (xᵢ − x̄)²'], ['prod', 'Π xᵢ']], 'x')}</div>
      <div class="vz-cells vz-big sg-cells"></div><div class="mv-calc sg-calc"></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let xs = [4, 8, 6, 2], f = 'x';
    const P = Player($('.vz-p', b), show, 900);
    const term = (x, m) => f === 'x' ? x : f === 'sq' ? x * x : f === 'dev' ? (x - m) ** 2 : x;
    const tx = (x, m) => f === 'x' ? `${MV.num(x)}` : f === 'sq' ? `${MV.num(x)}²` : f === 'dev' ? `(${MV.num(x)} − ${MV.num(m)})²` : `${MV.num(x)}`;
    function read() {
      const v = $('input', b).value.split(/[,\s]+/).filter(Boolean).map(Number).filter(x => isFinite(x)).slice(0, 10);
      xs = v.length ? v : [4, 8, 6, 2];
      P.load(xs.length + 1);
    }
    function show(i) {
      const m = xs.reduce((s, x) => s + x, 0) / xs.length;
      $('.sg-cells', b).innerHTML = xs.map((x, k) => cell(x, k < i - 1 ? 'ok' : k === i - 1 ? 'hl' : '', 'i=' + (k + 1))).join('');
      let tot = f === 'prod' ? 1 : 0;
      const parts = [];
      for (let k = 0; k < i; k++) { tot = f === 'prod' ? tot * xs[k] : tot + term(xs[k], m); parts.push(tx(xs[k], m)); }
      const op = f === 'prod' ? ' × ' : ' + ';
      $('.sg-calc', b).innerHTML = i ? `${parts.join(op)} = <span class="t">${MV.num(tot, 4)}</span>` : (f === 'prod' ? 'Start the running product at 1.' : 'Start the running total at 0.');
      const done = i === xs.length;
      $('.vz-msg', b).innerHTML = !i ? 'i has not started yet.' : done
        ? (f === 'x' ? `Finished. The sum is ${MV.num(tot, 4)}, so the mean is ${MV.num(tot, 4)} ÷ ${xs.length} = <b>${MV.num(m, 4)}</b>.`
          : f === 'dev' ? `Finished. Dividing by n = ${xs.length} gives the variance <b>${MV.num(tot / xs.length, 4)}</b>.`
          : `Finished after ${xs.length} terms.`)
        : `i = ${i}: add the term for x<sub>${i}</sub> = ${MV.num(xs[i - 1])}.`;
    }
    $('.mv-inp button', b).onclick = read;
    wireSeg(b, 'f', v => { f = v; P.load(xs.length + 1); });
    read();
  };
})();
'''

CSS = r'''
.bal{max-height:240px}
.bal-beam{stroke:var(--ink2); stroke-width:6; stroke-linecap:round}
.bal-stand{fill:var(--ink2)}
.bal-pan{fill:var(--accent-soft); stroke:var(--accent); stroke-width:2}
.bal-txt{fill:var(--ink); font-family:var(--font-mono); font-weight:800; font-size:18px}
.nl-host .mv-svg{max-height:120px}
'''

# ---------------------------------------------------------------- deeper explanations and extra animations
# Each lesson above gives the short version. DEEPER adds a slower, fuller explanation (and sometimes an
# animation) to the end of the lesson with the same id.
DEEPER = {
    'numbers': deep('what is really inside a 64 bit number', f'''
<p>A computer does not store 0.1 as "zero point one". It stores three pieces, like a number written in scientific notation, but in base 2. This standard is called <b>IEEE 754</b>, and almost every chip in the world follows it.</p>
{table(['Format', 'Sign', 'Exponent bits', 'Fraction bits', 'Correct decimal digits', 'Where you meet it'], [
        ['float64 (double)', '1', '11', '52', 'about 15 to 16', 'Python float, JavaScript number, Java double'],
        ['float32 (single)', '1', '8', '23', 'about 7', 'the default in PyTorch and on most GPUs'],
        ['float16 (half)', '1', '5', '10', 'about 3', 'mixed precision training, largest value only 65504'],
        ['bfloat16', '1', '8', '7', 'about 2 to 3', 'Google TPUs and modern GPUs, same range as float32'],
    ])}
<p>Think of the fraction bits as the number of digits on a calculator screen. With 52 bits you get roughly 16 decimal digits, so anything after that is rounded away. That is why <code>0.1 + 0.2</code> prints <code>0.30000000000000004</code> in Python and JavaScript: 0.1 and 0.2 were each rounded a tiny bit when they were stored, and the tiny errors add up.</p>
{fx('Machine epsilon', 'ε = 2⁻⁵² ≈ 2.2 × 10⁻¹⁶ for float64', 'The gap between 1 and the next number a double can hold. Any relative error smaller than this is invisible to the computer.')}
<p>Three practical rules follow from this.</p>
<ol>
<li><b>Never compare decimals with ==.</b> Compare with a tolerance, such as |a − b| &lt; 10⁻⁹.</li>
<li><b>Adding a tiny number to a huge one can do nothing at all.</b> In float32, 100000000 + 1 is still 100000000, because 7 digits cannot show the 1. Summing millions of small losses in the wrong order can lose information this way.</li>
<li><b>Fewer bits means a smaller range.</b> float16 cannot hold anything above 65504, so a large logit or a big gradient becomes infinity. Mixed precision training multiplies the loss by a scale factor to keep small gradients from rounding to zero, then divides it back.</li>
</ol>
{life('A bank never stores rupees and paise as floats. It stores whole paise as integers, because rounding even 0.000001 on millions of payments adds up to real money.')}
'''),
    'order': deep('percent versus percentage points, and chains of changes', f'''
<p>Two words get mixed up in news headlines and in model reports all the time.</p>
{table(['Phrase', 'What it measures', 'Example: accuracy goes from 80% to 92%'], [
        ['percentage points', 'the plain difference between two percentages', '92 − 80 = 12 percentage points'],
        ['percent change', 'the difference as a share of the starting value', '12 ÷ 80 × 100 = 15% better'],
        ['error rate change', 'often the most honest view for good models', 'errors fell from 20% to 8%, a 60% cut in mistakes'],
    ])}
<p>The third row matters a lot in machine learning. Going from 98% to 99% accuracy sounds tiny, only 1 point. But the error rate falls from 2% to 1%, so the model makes <b>half as many mistakes</b>. For a fraud filter checking a million payments a day, that is 10000 fewer wrong answers every day.</p>
<p>Percentage changes that follow each other <b>multiply</b>. A rise of r% multiplies by (1 + r ÷ 100) and a fall of r% multiplies by (1 − r ÷ 100). A share that rises 50% and then falls 50% ends at 1.5 × 0.5 = 0.75 of where it began, a 25% loss, even though "+50 then −50" looks like it should cancel. Try it below with your own numbers.</p>
{viz('pctchain')}
{ml('Learning rate decay works the same way. Multiplying the learning rate by 0.9 every epoch for 10 epochs leaves 0.9¹⁰ ≈ 0.35 of it, not 0. Repeated percentage changes are powers, which the next lesson covers.')}
'''),
    'algebra': deep('rearranging a formula to make any letter the subject', f'''
<p>Most of the algebra used in machine learning is not "find x". It is "rearrange this formula so the thing I want is alone on one side". The balance rule is all you need. Here is the z-score formula from Chapter 10, rearranged to get back the original value.</p>
{worked('Make x the subject of z = (x − μ) ÷ σ', [
        'Start: <span class="eq">z = (x − μ) ÷ σ</span>. The last thing done to x was "divide by σ", so undo that first.',
        'Multiply both sides by σ: <span class="eq">zσ = x − μ</span>',
        'The first thing done to x was "subtract μ". Undo it by adding μ to both sides: <span class="eq">zσ + μ = x</span>',
        'So <span class="eq">x = μ + zσ</span>. With μ = 170 cm, σ = 10 cm and z = 2, the person is 170 + 20 = 190 cm tall.'])}
<p>A <b>linear</b> equation has the unknown only to the power 1 and never multiplied by itself, as in 3x + 5 = 20. Its graph is a straight line and it has one answer (or none, or infinitely many). A <b>non linear</b> equation, such as x² = 9 or eˣ = 5, can have several answers or need logs and roots to solve. Machine learning loves linear equations because they can be solved exactly and fast, even with millions of unknowns, which is why so many models start with a linear step.</p>
{trick('Undo the operations in the reverse order they were done, like unwrapping a gift: the last layer of paper comes off first.')}
'''),
    'powers': deep('why the rules work, and how fast powers really grow', f'''
<p>Every power rule comes from counting factors. 2³ × 2⁴ is (2 × 2 × 2) × (2 × 2 × 2 × 2), seven 2s in a row, so it is 2⁷. Dividing cancels factors, so 2⁵ ÷ 2³ leaves two 2s. Follow the pattern downwards and the strange rules explain themselves:</p>
{table(['Power', '2⁴', '2³', '2²', '2¹', '2⁰', '2⁻¹', '2⁻²'], [
        ['Value', '16', '8', '4', '2', '1', '½', '¼'],
        ['How you got there', '', '÷ 2', '÷ 2', '÷ 2', '÷ 2', '÷ 2', '÷ 2'],
    ])}
<p>Each step left divides by 2, so 2⁰ must be 1 and 2⁻¹ must be one half. Nothing magic, just the pattern carried on. A fractional power is a root because (9^½)² = 9^(½ × 2) = 9¹ = 9, so 9^½ is the number whose square is 9.</p>
<p>The animation below races four kinds of growth. A straight line n, a square n², a cube n³ and a doubling 2ⁿ. For small n the cube is ahead. Past n = 10 the doubling leaves everything behind, and by n = 30 it is over a billion. Switch to the log scale to see all four at once: on a log scale, doubling becomes a straight line.</p>
{viz('powgrow')}
{ml('The cost of some algorithms grows like a power of n, which is fine, and some grow like 2ⁿ, which is hopeless for large n. Trying every subset of 50 features means 2⁵⁰ ≈ 1.1 × 10¹⁵ models. That is why exhaustive search is never used for feature selection.')}
'''),
    'sigma': deep('the rules that let you move sums around', f'''
<p>Formulas in papers often look scary only because a Σ was moved, split or combined. Three rules cover nearly all of it. Each one is just a fact about adding lists of numbers.</p>
{table(['Rule', 'In symbols', 'Why it is true'], [
        ['Split a sum', 'Σ (aᵢ + bᵢ) = Σ aᵢ + Σ bᵢ', 'you can add the numbers in any order'],
        ['Pull out a constant', 'Σ c·aᵢ = c · Σ aᵢ', 'c(a₁ + a₂) = ca₁ + ca₂, the distributive law'],
        ['Sum of a constant', 'Σ from 1 to n of c = n · c', 'adding c to itself n times'],
        ['Sum of a log', 'Σ log aᵢ = log Π aᵢ', 'logs turn products into sums (Chapter 2)'],
    ])}
{worked('Show that the deviations from the mean always add to zero', [
        'We want <span class="eq">Σ (xᵢ − x̄)</span> for any data.',
        'Split the sum: <span class="eq">Σ xᵢ − Σ x̄</span>',
        'x̄ is the same for every i, so the second sum is <span class="eq">n · x̄</span>',
        'But <span class="eq">x̄ = Σ xᵢ ÷ n</span>, so <span class="eq">n · x̄ = Σ xᵢ</span>',
        'Therefore <span class="eq">Σ (xᵢ − x̄) = Σ xᵢ − Σ xᵢ = 0</span>. This is why variance squares the deviations, otherwise they would always cancel.'])}
<p>A <b>double sum</b> Σᵢ Σⱼ is two loops, one inside the other. Matrix multiplication (Chapter 4) is a double sum in disguise: entry (i, j) of AB is Σₖ aᵢₖbₖⱼ, and doing it for every i and j adds two more loops around it.</p>
'''),
    'abs': deep('distance rules and why the kink at zero matters', f'''
<p>The absolute value obeys one famous rule, the <b>triangle inequality</b>: |a + b| ≤ |a| + |b|. In words, a detour is never shorter than the direct route. If you walk 3 km east and then 5 km west, you end up only 2 km from home, even though you walked 8 km. The same rule holds for vector lengths in Chapter 3, and it is what makes a distance a "proper" distance.</p>
{fx('Triangle inequality', '|a + b| ≤ |a| + |b| &nbsp;&nbsp; and &nbsp;&nbsp; |a − c| ≤ |a − b| + |b − c|', 'Going from a to c directly is never longer than going through b.')}
<p>The graph of |x| is a V with a sharp corner at 0. The slope is −1 on the left and +1 on the right, so at the corner there is no single slope. Calculus calls this <b>not differentiable at 0</b>. Gradient based training still works, because libraries simply pick a slope of 0 at the corner. But the corner has a useful side effect: L1 regularisation can push a weight to exactly 0 and keep it there, which squared penalties never do (Chapter 12).</p>
<p>Use the widget to play with the most common shape in error bars and tolerances, |x − c| ≤ r. It always means "x is within r of c", which is the interval from c − r to c + r.</p>
{viz('absline')}
{life('A pharmacy label that says "500 mg ± 5%" means |dose − 500| ≤ 25, so any tablet from 475 mg to 525 mg passes the quality check.')}
'''),
}
for _p in PARTS:
    _p['html'] += DEEPER.get(_p['id'], '')

VIZ_JS += r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;

  /* ----- two percentage changes in a row ----- */
  W.pctchain = el => {
    const b = shell(el, 'Two percentage changes in a row', 'Set a starting price and two changes, then press Play to apply them one at a time. Watch why +50% then −50% does not bring you back.');
    b.innerHTML = `<div class="mv-wrap"><div class="pc-plot"></div><div class="mv-side">${slider('s', 'start', 100, 1000, 400, 50)}${slider('u', 'first change %', -90, 100, 50, 5)}${slider('d', 'second change %', -90, 100, -50, 5)}<div class="mv-read pc-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let s = 400, u = 50, d = -50;
    function show(t) {
      const v = [s, s * (1 + u / 100), s * (1 + u / 100) * (1 + d / 100)];
      const top = Math.max(...v) * 1.15, Wd = 420, H = 260, bw = 90;
      let g = `<line class="mv-axis" x1="30" y1="${H - 30}" x2="${Wd - 10}" y2="${H - 30}"/>`;
      ['start', 'after change 1', 'after change 2'].forEach((lab, k) => {
        const x = 50 + k * 125, h = k <= t ? v[k] / top * (H - 60) : 0;
        g += `<rect class="mv-bar ${k === 0 ? '' : k === 1 ? 'o' : 'g'}" x="${x}" y="${H - 30 - h}" width="${bw}" height="${h}" rx="6"/>`;
        g += `<text class="mv-lab sm" x="${x + bw / 2}" y="${H - 12}" text-anchor="middle">${lab}</text>`;
        if (k <= t) g += `<text class="mv-lab" x="${x + bw / 2}" y="${H - 36 - h}" text-anchor="middle">${MV.num(v[k], 2)}</text>`;
      });
      $('.pc-plot', b).innerHTML = `<svg class="mv-svg" viewBox="0 0 ${Wd} ${H}" role="img" aria-label="Bars for each price">${g}</svg>`;
      const m1 = 1 + u / 100, m2 = 1 + d / 100, tot = (m1 * m2 - 1) * 100;
      const lines = [`start = <b>${MV.num(s)}</b>`];
      if (t >= 1) lines.push(`change 1: × ${MV.num(m1, 2)} gives <b>${MV.num(v[1], 2)}</b>`);
      if (t >= 2) lines.push(`change 2: × ${MV.num(m2, 2)} gives <b>${MV.num(v[2], 2)}</b>`, `total multiplier ${MV.num(m1, 2)} × ${MV.num(m2, 2)} = <b>${MV.num(m1 * m2, 4)}</b>`, `overall change <b>${MV.num(tot, 2)}%</b>, not ${MV.num(u + d, 2)}%`);
      $('.pc-out', b).innerHTML = lines.join('<br>');
    }
    const P = Player($('.vz-p', b), show, 1100);
    const re = () => P.load(3, 2);
    wireSlider(b, 's', v => { s = v; re(); });
    wireSlider(b, 'u', v => { u = v; re(); });
    wireSlider(b, 'd', v => { d = v; re(); });
    re();
  };

  /* ----- n, n², n³ and 2ⁿ race ----- */
  W.powgrow = el => {
    const b = shell(el, 'The growth race: n, n², n³ and 2ⁿ', 'Move n or press Play to grow it from 1 to 30. Switch the scale to log to see all four curves at once.');
    b.innerHTML = `<div class="vz-row">${seg('sc', [['lin', 'Normal scale'], ['log', 'Log scale']], 'lin')}</div><div class="mv-wrap"><div class="pg-plot"></div><div class="mv-side">${slider('n', 'n', 1, 30, 8, 1)}<div class="mv-read pg-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let n = 8, sc = 'lin';
    const fs = [['n', k => k, 'a'], ['n²', k => k * k, 'o'], ['n³', k => k ** 3, 'g'], ['2ⁿ', k => 2 ** k, 'p']];
    const sci = v => v < 1e5 ? MV.num(v, 0) : v.toExponential(2).replace('e+', ' × 10^');
    function show() {
      const top = Math.max(...fs.map(f => f[1](n)));
      const G = sc === 'lin' ? MV.frame(440, 300, [0, n + 0.5], [0, top * 1.08]) : MV.frame(440, 300, [0, n + 0.5], [0, Math.log10(top) * 1.08 + 0.2]);
      const tf = v => sc === 'lin' ? v : Math.log10(v);
      let s = MV.axes(G, { labels: false, xl: 'n', yl: sc === 'lin' ? 'value' : 'log₁₀ of value' });
      for (let k = 5; k <= n; k += 5) s += MV.text(G, k, 0, MV.num(k), { dy: 14, anchor: 'middle', cls: 'sm' });
      if (sc === 'lin') s += MV.text(G, 0, top, 'top line = ' + sci(top), { dx: 56, dy: 4, cls: 'sm' });
      fs.forEach(([lab, f, c]) => {
        const pts = []; for (let k = 1; k <= n; k++) pts.push(G.sx(k).toFixed(1) + ',' + G.sy(tf(f(k))).toFixed(1));
        s += `<polyline class="mv-v ${c}" stroke-width="2.5" points="${pts.join(' ')}"/>` + MV.dot(G, n, tf(f(n)), c, 5);
      });
      if (sc === 'log') for (let p = 1; p <= Math.log10(top) + 0.2; p++) s += MV.text(G, 0, p, '10^' + p, { dx: 2, dy: 4, cls: 'sm' });
      $('.pg-plot', b).innerHTML = MV.svg(G, s, 'Four growth curves');
      $('.pg-out', b).innerHTML = `<div class="mv-legend"><span><i></i>n</span><span><i class="o"></i>n²</span><span><i class="g"></i>n³</span><span><i class="p"></i>2ⁿ</span></div>` +
        fs.map(([lab, f]) => `${lab} = <b>${sci(f(n))}</b>`).join('<br>') +
        (2 ** n > n ** 3 ? '<br>🚀 2ⁿ is in the lead.' : '<br>n³ is still ahead, keep going past n = 10.');
    }
    const P = Player($('.vz-p', b), t => { n = t + 1; $('[data-sl="n"]', b).value = n; $('[data-slv="n"]', b).textContent = n; show(); }, 450);
    wireSeg(b, 'sc', v => { sc = v; show(); });
    wireSlider(b, 'n', v => { P.pause(); n = v; show(); });
    P.load(30, 7);
  };

  /* ----- |x − c| ≤ r on the number line ----- */
  W.absline = el => {
    const b = shell(el, 'Within r of c: |x − c| ≤ r', 'Set the centre c and the allowed distance r. Move x yourself or press Play to sweep it from left to right, and watch the distance |x − c| and the verdict change.');
    b.innerHTML = `<div class="nl2-plot"></div><div class="mv-wrap"><div class="mv-side">${slider('c', 'centre c', -8, 8, 2, 0.5)}${slider('r', 'distance r', 0, 6, 3, 0.5)}${slider('x', 'x', -12, 12, -4, 0.5)}</div><div class="mv-read al-out" aria-live="polite"></div></div><div class="vz-p"></div>`;
    let c = 2, r = 3, x = -4;
    const G = MV.frame(400, 120, [-12.5, 12.5], [-1, 1], 14);
    function draw() {
      let s = `<line class="mv-axis" x1="${G.sx(-12.5)}" y1="${G.sy(0)}" x2="${G.sx(12.5)}" y2="${G.sy(0)}"/>`;
      for (let k = -12; k <= 12; k += 4) s += `<line class="mv-grid" x1="${G.sx(k)}" y1="${G.sy(0) - 5}" x2="${G.sx(k)}" y2="${G.sy(0) + 5}"/><text class="mv-tick" x="${G.sx(k)}" y="${G.sy(0) + 22}" text-anchor="middle">${MV.num(k)}</text>`;
      s += `<rect x="${G.sx(c - r)}" y="${G.sy(0) - 12}" width="${Math.max(1, G.sx(c + r) - G.sx(c - r))}" height="24" rx="8" class="mv-fill c3"/>`;
      s += MV.dot(G, c - r, 0, 'g', 6) + MV.dot(G, c + r, 0, 'g', 6) + MV.dot(G, c, 0, 'k', 5) + MV.text(G, c, 0, 'c', { dy: -18, anchor: 'middle' });
      s += `<line class="mv-v o dash" x1="${G.sx(c)}" y1="${G.sy(0) - 30}" x2="${G.sx(x)}" y2="${G.sy(0) - 30}"/>` + MV.dot(G, x, 0, 'o', 8) + MV.text(G, x, 0, 'x', { dy: -38, anchor: 'middle' });
      $('.nl2-plot', b).innerHTML = MV.svg(G, s, 'Number line with an interval');
      const dist = Math.abs(x - c), ok = dist <= r + 1e-9;
      $('.al-out', b).innerHTML = `interval: <b>[${MV.num(c - r)}, ${MV.num(c + r)}]</b><br>|x − c| = |${MV.num(x)} − ${MV.num(c)}| = <b>${MV.num(dist)}</b><br>` + (ok ? `✅ ${MV.num(dist)} ≤ ${MV.num(r)}, so x is inside.` : `❌ ${MV.num(dist)} &gt; ${MV.num(r)}, so x is outside.`);
    }
    const P = Player($('.vz-p', b), t => { x = -12 + t; $('[data-sl="x"]', b).value = x; $('[data-slv="x"]', b).textContent = x; draw(); }, 350);
    wireSlider(b, 'c', v => { c = v; draw(); });
    wireSlider(b, 'r', v => { r = v; draw(); });
    wireSlider(b, 'x', v => { P.pause(); x = v; draw(); });
    P.load(25, 8);
  };
})();
'''
CSS += r'''
.nl2-plot .mv-svg{max-height:150px}
.pc-plot .mv-svg,.pg-plot .mv-svg{max-height:340px}
'''

T = K.topic(
    slug='numbers-algebra', topic='numbers-algebra', prefix='mm01', short='Numbers and algebra', emoji='🌱',
    title='Numbers, Algebra and Equations',
    module=('🌱', 'School foundations', 'foundations', 'The school maths every model is written in: numbers, algebra, functions, exponents and logarithms.'),
    minutes=45,
    lead='The school maths underneath every model: kinds of numbers, the order of operations, percentages, equations that stay balanced, powers, the sigma sign and absolute value. Each idea is linked to how a machine learning model uses it.',
    desc='Numbers, order of operations, percentages, linear equations, exponents, sigma notation and absolute value for machine learning, with animations and worked problems.',
    summary='Number families and floating point, BODMAS, fractions and percentages, linear and simultaneous equations, exponent rules and scientific notation, sigma and pi notation, absolute value and the mean absolute error.',
    keywords=['numbers', 'algebra', 'BODMAS', 'percentage', 'linear equation', 'simultaneous equations', 'exponents', 'scientific notation', 'sigma notation', 'summation', 'absolute value', 'MAE', 'floating point'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={'float_precision': 1, 'solve_linear': 1},
)
