# 3.2 Policy gradients, actor critic and PPO
# Example "baseline_variance" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import math
import random

import numpy as np

# Does a baseline change the policy gradient? It should not change the average, only the noise.
# Short corridor again, with a fixed policy p(right) = 0.3 written as p = sigmoid(h).
def step(s, right):
    move = 1 if right else -1
    if s == 1:
        move = -move
    return max(0, s + move)

def values(p):                                            # v(0), v(1), v(2) from the Bellman equations
    A = np.array([[p, -p, 0], [-p, 1, -(1 - p)], [0, -(1 - p), 1]])
    return np.linalg.solve(A, -np.ones(3))

p = 0.3
h = math.log(p / (1 - p))
v = values(p)
eps = 1e-5                                                # the true gradient dJ/dh by a tiny finite difference
sig = lambda x: 1 / (1 + math.exp(-x))
true_grad = (values(sig(h + eps))[0] - values(sig(h - eps))[0]) / (2 * eps)

rnd = random.Random(0)
plain, with_base = [], []
for _ in range(20000):
    s, visits = 0, []
    while s != 3:
        a = 1 if rnd.random() < p else 0
        visits.append((s, a))
        s = step(s, a)
    T = len(visits)
    g1 = g2 = 0.0
    for t, (st, a) in enumerate(visits):
        G = -(T - t)
        g1 += G * (a - p)                                 # REINFORCE estimate of dJ/dh
        g2 += (G - v[st]) * (a - p)                       # the same with baseline b(s) = v(s)
    plain.append(g1)
    with_base.append(g2)

print("true gradient dJ/dh:", round(true_grad, 2))
print("without baseline: average", round(np.mean(plain), 2), " standard deviation", round(np.std(plain), 2))
print("with baseline   : average", round(np.mean(with_base), 2), " standard deviation", round(np.std(with_base), 2))
print("Both averages agree with the true gradient up to sampling error. The baseline only removes noise.")
