# 1.1 Neural networks: from perceptrons to MLPs
# Example "mlp_xor" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# A tiny multilayer perceptron for XOR: 2 inputs, 3 hidden units with tanh, 1 output with a sigmoid.
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
y = np.array([[0], [1], [1], [0]], dtype=float)
rng = np.random.default_rng(1)
W1, b1 = rng.normal(0, 1, (2, 3)), np.zeros(3)
W2, b2 = rng.normal(0, 1, (3, 1)), np.zeros(1)
sigmoid = lambda z: 1 / (1 + np.exp(-z))
lr = 0.5
for step in range(1, 3001):
    h = np.tanh(X @ W1 + b1)                              # forward pass: hidden layer
    p = sigmoid(h @ W2 + b2)                              # output: probability of class 1
    loss = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    d_out = (p - y) / len(X)                              # backward pass (chapter 1.2 explains every line)
    dW2, db2 = h.T @ d_out, d_out.sum(0)
    d_h = (d_out @ W2.T) * (1 - h ** 2)
    dW1, db1 = X.T @ d_h, d_h.sum(0)
    W1 -= lr * dW1; b1 -= lr * db1; W2 -= lr * dW2; b2 -= lr * db2
    if step in (1, 100, 500, 3000):
        print(f"step {step:4d}: loss {loss:.4f}, outputs {p.ravel().round(3)}")
print("hidden layer values for the 4 inputs:")
print(np.tanh(X @ W1 + b1).round(2))
print("The hidden units turn the inputs into new features where one straight line can separate XOR.")
