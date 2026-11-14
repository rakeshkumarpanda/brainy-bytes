# 1.2 Backpropagation and automatic differentiation
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


# ================================================================== task 1: Gradients of (x + y) z
# Write add_mul_grads(x, y, z) that returns the list [∂f/∂x, ∂f/∂y, ∂f/∂z] for f = (x + y) z,
# computed with the backward pass rules.
# Why it works: Compare with the animation’s first graph: the same three numbers appear in red.

def add_mul_grads(x, y, z):
    q = x + y
    dq = z
    return [dq, dq, q]


# ================================================================== task 2: A numerical gradient
# Write numeric_grad(f, x, h=1e-5) that estimates f′(x) with the central difference (f(x + h) − f(x
# − h)) / 2h and rounds it to 4 decimals.
# Why it works: The central difference has error proportional to h2, much smaller than the one sided
# (f(x + h) − f(x)) / h with error proportional to h.

def numeric_grad(f, x, h=1e-5):
    return round((f(x + h) - f(x - h)) / (2 * h), 4)


# ================================================================== task 3: The softmax cross entropy gradient
# Write softmax_ce_grad(scores, label) that returns the gradient of the cross entropy loss with
# respect to the scores, softmax(scores) minus the one hot label, each rounded to 4 decimals.
# Why it works: The gradient entries always add up to 0, because the probabilities add up to 1 and
# the one hot label does too.

import math


def softmax_ce_grad(scores, label):
    m = max(scores)
    e = [math.exp(s - m) for s in scores]
    z = sum(e)
    return [round(v / z - (1.0 if i == label else 0.0), 4) for i, v in enumerate(e)]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Gradients of (x + y) z", [('add_mul_grads(-2, 5, -4)', [-4, -4, 3]), ('add_mul_grads(1, 1, 0)', [0, 0, 2])]))
    results.append(check("Task 2: A numerical gradient", [('numeric_grad(lambda v: v * v, 3.0)', 6.0), ('numeric_grad(lambda v: (2 * v + 1) ** 2, 1.0)', 12.0), ('numeric_grad(lambda v: v ** 3, 2.0)', 12.0)]))
    results.append(check("Task 3: The softmax cross entropy gradient", [('softmax_ce_grad([0.0, 0.0], 0)', [-0.5, 0.5]), ('softmax_ce_grad([2.0, 1.0, 0.0], 0)', [-0.3348, 0.2447, 0.09]), ('softmax_ce_grad([1.0, 1.0, 1.0, 1.0], 3)', [0.25, 0.25, 0.25, -0.75])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
