# 2.2 Calculus for ML: derivatives, gradients and gradient descent
# Model solutions. Try practice.py first.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: Derivative of a polynomial
# A polynomial is stored as its coefficients from the constant up: [c0, c1, c2] means c0 + c1 x + c2
# x2. Write poly_derivative(coeffs) that returns the coefficients of its derivative. The derivative
# of a constant is [0].
# Why it works: This is the power rule applied to every term, plus the sum rule that lets you do
# each term on its own.

def poly_derivative(coeffs):
    if len(coeffs) == 1:
        return [0]
    result = []
    for power in range(1, len(coeffs)):
        result.append(power * coeffs[power])
    return result


# ================================================================== task 2: Numeric slope with the central difference
# Write numeric_slope(f, x) that returns (f(x + h) − f(x − h)) / (2h) with h = 0.00001, rounded to 4
# decimals. f is any function of one number.
# Why it works: This is gradient checking: compare a hand derived gradient with this number. If they
# differ, the hand derivation has a bug.

def numeric_slope(f, x):
    h = 0.00001
    return round((f(x + h) - f(x - h)) / (2 * h), 4)


# ================================================================== task 3: Gradient descent on a bowl
# Write descend(target, start, rate, steps) that minimises f(x) = (x − target)2 with gradient
# descent. Start at start, take the given number of steps with x = x − rate × 2(x − target), and
# return x rounded to 4 decimals.
# Why it works: Each step multiplies the distance to the target by (1 − 2 × rate). With rate 0.5
# that factor is 0, so one step lands exactly on the target.

def descend(target, start, rate, steps):
    x = start
    for i in range(steps):
        slope = 2 * (x - target)
        x = x - rate * slope
    return round(x, 4)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Derivative of a polynomial", [('poly_derivative([7, 4, 1])', [4, 2]), ('poly_derivative([0, 0, 0, 2])', [0, 0, 6]), ('poly_derivative([5])', [0])]))
    results.append(check("Task 2: Numeric slope with the central difference", [('numeric_slope(lambda t: t * t, 3)', 6.0), ('numeric_slope(lambda t: t ** 3, 2)', 12.0), ('numeric_slope(lambda t: 5 * t + 1, 0)', 5.0)]))
    results.append(check("Task 3: Gradient descent on a bowl", [('descend(5, 1, 0.25, 3)', 4.5), ('descend(0, 10, 0.5, 1)', 0.0), ('descend(2, 0, 0.1, 10)', 1.7853)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
