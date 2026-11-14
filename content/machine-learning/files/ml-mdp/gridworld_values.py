# 1.3 Markov decision processes and Bellman equations
# Example "gridworld_values" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# 4 x 4 grid, cells 0 to 15. Cells 0 and 15 are exits. Every move costs -1. Moves off the grid leave you in place.
n, gamma = 16, 1.0
moves = {"up": -4, "down": 4, "left": -1, "right": 1}

def step(s, a):
    if s in (0, 15):
        return s, 0.0
    r, c = divmod(s, 4)
    if (a == "up" and r == 0) or (a == "down" and r == 3) or (a == "left" and c == 0) or (a == "right" and c == 3):
        return s, -1.0
    return s + moves[a], -1.0

P, R = np.zeros((n, n)), np.zeros(n)                       # the random policy: each move with chance 1/4
for s in range(n):
    for a in moves:
        s2, r = step(s, a)
        P[s, s2] += 0.25
        R[s] += 0.25 * r
P[[0, 15]] = 0                                           # exits: no future
V = np.linalg.solve(np.eye(n) - gamma * P, R)
print("value of each cell under the random policy:")
print(V.reshape(4, 4).round(1))
