# 1.1 Neural networks: from perceptrons to MLPs
# Model solutions. Try practice.py first.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
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


# ================================================================== task 1: A single neuron
# Write neuron(x, w, b, act) that returns φ(w · x + b) rounded to 4 decimals, where act is
# "sigmoid", "tanh" or "relu".
# Why it works: Returning a float from ReLU keeps the output type the same for every activation.

import math


def neuron(x, w, b, act):
    z = sum(xi * wi for xi, wi in zip(x, w)) + b
    if act == "sigmoid":
        return round(1 / (1 + math.exp(-z)), 4)
    if act == "tanh":
        return round(math.tanh(z), 4)
    return round(float(max(0.0, z)), 4)


# ================================================================== task 2: Train a perceptron
# Write perceptron_train(X, y, epochs). Start from zero weights and bias, visit the points in order,
# predict 1 when w · x + b > 0, and on a mistake add (y − ŷ) times x to w and (y − ŷ) to b. Stop
# early after an epoch with no mistakes. Return the list w followed by b, as one list.
# Why it works: These are the AND and OR gates. Both are linearly separable, so training stops well
# before 20 epochs.

def perceptron_train(X, y, epochs):
    w, b = [0] * len(X[0]), 0
    for _ in range(epochs):
        mistakes = 0
        for xi, t in zip(X, y):
            pred = 1 if sum(a * c for a, c in zip(w, xi)) + b > 0 else 0
            if pred != t:
                w = [a + (t - pred) * c for a, c in zip(w, xi)]
                b += t - pred
                mistakes += 1
        if mistakes == 0:
            break
    return w + [b]


# ================================================================== task 3: Forward pass of a small MLP
# Write mlp_forward(x, W1, b1, W2, b2). W1 is a list of rows, one per hidden unit, and b1 a list of
# biases. Hidden units use ReLU. W2 is a list of rows, one per output, and b2 a list of biases, with
# no activation on the output. Return the outputs rounded to 4 decimals.
# Why it works: The first two tests are the hand built XOR network from the maths lesson.

def mlp_forward(x, W1, b1, W2, b2):
    h = [max(0.0, sum(w * xi for w, xi in zip(row, x)) + b) for row, b in zip(W1, b1)]
    return [round(float(sum(w * hi for w, hi in zip(row, h)) + b), 4) for row, b in zip(W2, b2)]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A single neuron", [('neuron([2, 1], [0.5, -1], 0.5, "sigmoid")', 0.6225), ('neuron([1, 1], [1, 1], -3, "relu")', 0.0), ('neuron([1, 0], [1, 0], 0, "tanh")', 0.7616)]))
    results.append(check("Task 2: Train a perceptron", [('perceptron_train([[0, 0], [0, 1], [1, 0], [1, 1]], [0, 0, 0, 1], 20)', [2, 1, -2]), ('perceptron_train([[0, 0], [0, 1], [1, 0], [1, 1]], [0, 1, 1, 1], 20)', [1, 1, 0])]))
    results.append(check("Task 3: Forward pass of a small MLP", [('mlp_forward([1, 1], [[1, 1], [1, 1]], [0, -1], [[1, -2]], [0])', [0.0]), ('mlp_forward([0, 1], [[1, 1], [1, 1]], [0, -1], [[1, -2]], [0])', [1.0]), ('mlp_forward([2, -1], [[1, 0], [0, 1]], [0, 0], [[1, 1], [2, -1]], [0.5, 0])', [2.5, 4.0])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
