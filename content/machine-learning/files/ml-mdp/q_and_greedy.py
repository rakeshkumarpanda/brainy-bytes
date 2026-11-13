# 1.3 Markov decision processes and Bellman equations
# Example "q_and_greedy" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

n, gamma = 16, 1.0
moves = {"up": -4, "down": 4, "left": -1, "right": 1}

def step(s, a):
    if s in (0, 15):
        return s, 0.0
    r, c = divmod(s, 4)
    if (a == "up" and r == 0) or (a == "down" and r == 3) or (a == "left" and c == 0) or (a == "right" and c == 3):
        return s, -1.0
    return s + moves[a], -1.0

P, R = np.zeros((n, n)), np.zeros(n)
for s in range(n):
    for a in moves:
        s2, r = step(s, a)
        P[s, s2] += 0.25
        R[s] += 0.25 * r
P[[0, 15]] = 0
V = np.linalg.solve(np.eye(n) - gamma * P, R)            # value of the random policy

s = 6                                                    # row 1, column 2
for a in moves:
    s2, r = step(s, a)
    print(f"Q(cell 6, {a.ljust(5)}) = r + gamma * V(next) = {r:.0f} + ({V[s2]:.1f}) = {r + gamma * V[s2]:.1f}")
arrows = {"up": "^", "down": "v", "left": "<", "right": ">"}
grid = []
for s in range(n):
    if s in (0, 15):
        grid.append("X")
        continue
    q = {a: step(s, a)[1] + gamma * V[step(s, a)[0]] for a in moves}
    grid.append(arrows[max(q, key=q.get)])               # greedy with respect to the random policy's values
print("greedy policy from those values:")
for r in range(4):
    print(" ".join(grid[4 * r:4 * r + 4]))
