# 2.1 Dynamic programming: policy and value iteration
# Example "policy_evaluation" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# 4 x 4 gridworld: exits in cells 0 and 15, every move costs -1, the policy moves each way with chance 1/4
moves = [-4, 4, -1, 1]                                   # up, down, left, right

def step(s, m):
    r, c = divmod(s, 4)
    if (m == -4 and r == 0) or (m == 4 and r == 3) or (m == -1 and c == 0) or (m == 1 and c == 3):
        return s                                         # bumping a wall leaves you in place
    return s + m

V = np.zeros(16)
for k in range(1, 1000):
    new = np.zeros(16)
    for s in range(1, 15):                               # the exits keep value 0
        new[s] = sum(0.25 * (-1 + V[step(s, m)]) for m in moves)
    delta = np.abs(new - V).max()
    V = new
    if k in (1, 2, 3, 10):
        print("after sweep", k)
        print(V.reshape(4, 4).round(1))
    if delta < 1e-4:
        break
print("converged after", k, "sweeps (largest change below 0.0001)")
print(V.reshape(4, 4).round(1))
