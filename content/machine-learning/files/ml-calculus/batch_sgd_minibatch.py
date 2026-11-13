# 2.2 Calculus for ML: derivatives, gradients and gradient descent
# Example "batch_sgd_minibatch" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

rng = np.random.default_rng(0)
X = rng.uniform(0, 5, size=40)
y = 3 * X + 2 + rng.normal(0, 0.5, size=40)      # true rule y = 3x + 2 plus noise

def train(batch_size, epochs=20, lr=0.02):
    w, b = 0.0, 0.0
    order = np.arange(len(X))
    for epoch in range(epochs):
        rng2 = np.random.default_rng(epoch)
        rng2.shuffle(order)
        for start in range(0, len(X), batch_size):
            idx = order[start:start + batch_size]
            err = w * X[idx] + b - y[idx]
            w -= lr * 2 * np.mean(err * X[idx])
            b -= lr * 2 * np.mean(err)
    mse = np.mean((w * X + b - y) ** 2)
    return "w = " + str(round(float(w), 2)) + "  b = " + str(round(float(b), 2)) + "  mse = " + str(round(float(mse), 3))

print("true rule:  w = 3  b = 2")
print("batch      (40 rows, 20 steps): ", train(40))
print("mini-batch (8 rows, 100 steps): ", train(8))
print("stochastic (1 row, 800 steps):  ", train(1))
