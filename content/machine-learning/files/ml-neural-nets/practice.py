# 1.1 Neural networks: from perceptrons to MLPs
# Practice tasks. Fill in each function, then run this file.
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


# ================================================================== task 1: A single neuron
# Write neuron(x, w, b, act) that returns φ(w · x + b) rounded to 4 decimals, where act is
# "sigmoid", "tanh" or "relu".
# Hint: Weighted sum plus bias, then the chosen activation.

def neuron(x, w, b, act):
    # your code here
    pass


# ================================================================== task 2: Train a perceptron
# Write perceptron_train(X, y, epochs). Start from zero weights and bias, visit the points in order,
# predict 1 when w · x + b > 0, and on a mistake add (y − ŷ) times x to w and (y − ŷ) to b. Stop
# early after an epoch with no mistakes. Return the list w followed by b, as one list.
# Hint: Loop over epochs and points, update only on mistakes, and stop after a clean epoch.

def perceptron_train(X, y, epochs):
    # your code here
    pass


# ================================================================== task 3: Forward pass of a small MLP
# Write mlp_forward(x, W1, b1, W2, b2). W1 is a list of rows, one per hidden unit, and b1 a list of
# biases. Hidden units use ReLU. W2 is a list of rows, one per output, and b2 a list of biases, with
# no activation on the output. Return the outputs rounded to 4 decimals.
# Hint: Compute the hidden layer with ReLU, then the output layer without an activation.

def mlp_forward(x, W1, b1, W2, b2):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A single neuron", [('neuron([2, 1], [0.5, -1], 0.5, "sigmoid")', 0.6225), ('neuron([1, 1], [1, 1], -3, "relu")', 0.0), ('neuron([1, 0], [1, 0], 0, "tanh")', 0.7616)]))
    results.append(check("Task 2: Train a perceptron", [('perceptron_train([[0, 0], [0, 1], [1, 0], [1, 1]], [0, 0, 0, 1], 20)', [2, 1, -2]), ('perceptron_train([[0, 0], [0, 1], [1, 0], [1, 1]], [0, 1, 1, 1], 20)', [1, 1, 0])]))
    results.append(check("Task 3: Forward pass of a small MLP", [('mlp_forward([1, 1], [[1, 1], [1, 1]], [0, -1], [[1, -2]], [0])', [0.0]), ('mlp_forward([0, 1], [[1, 1], [1, 1]], [0, -1], [[1, -2]], [0])', [1.0]), ('mlp_forward([2, -1], [[1, 0], [0, 1]], [0, 0], [[1, 1], [2, -1]], [0.5, 0])', [2.5, 4.0])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
