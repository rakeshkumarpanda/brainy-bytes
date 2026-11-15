# 2.2 Attacks and defences in federated learning
# Example "grad_leak" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Gradient leakage: why the server must not see one client's update. For a dense layer z = W x + b and one example,
# dL/dW = delta * x (an outer product) and dL/db = delta, so dividing a row of dL/dW by dL/db gives x back exactly.
import math
import random

random.seed(5)
x = [0.9, 0.1, 0.7, 0.3]                  # a private input: say four pixel brightnesses, or four health values
W = [[random.uniform(-1, 1) for _ in range(4)] for _ in range(2)]
b = [0.0, 0.0]
y = [1, 0]                                 # one hot label

def gradients(x, y):
    z = [sum(W[r][c] * x[c] for c in range(4)) + b[r] for r in range(2)]
    e = [math.exp(v) for v in z]
    p = [v / sum(e) for v in e]            # softmax
    delta = [p[r] - y[r] for r in range(2)] # dL/dz for cross entropy
    gW = [[delta[r] * x[c] for c in range(4)] for r in range(2)]
    return gW, delta

gW, gb = gradients(x, y)
recovered = [round(gW[0][c] / gb[0], 4) for c in range(4)]
print("private input:      ", x)
print("rebuilt from update:", recovered)

# a batch of 4 examples: the update is the average, so division gives a mix of the inputs
batch = [[0.9, 0.1, 0.7, 0.3], [0.2, 0.8, 0.4, 0.6], [0.5, 0.5, 0.9, 0.1], [0.1, 0.3, 0.2, 0.9]]
labels = [[1, 0], [0, 1], [1, 0], [0, 1]]
avgW = [[0.0] * 4 for _ in range(2)]
avgb = [0.0, 0.0]
for xi, yi in zip(batch, labels):
    g, d = gradients(xi, yi)
    for r in range(2):
        avgb[r] += d[r] / 4
        for c in range(4):
            avgW[r][c] += g[r][c] / 4
print("batch of 4, rebuilt: ", [round(avgW[0][c] / avgb[0], 4) for c in range(4)], " (a mix, not one person's input)")
print("\nDefences: secure aggregation (server sees only sums), bigger batches, and DP noise. Optimisation attacks")
print("such as Deep Leakage from Gradients (2019) can still separate small batches, so do not rely on batching alone.")
