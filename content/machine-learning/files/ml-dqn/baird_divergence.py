# 3.1 Function approximation and deep Q networks
# Example "baird_divergence" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Baird's counterexample (1995), Sutton and Barto section 11.2. 7 states, every reward is 0, so the true values are all 0.
# Behaviour policy: "dashed" (go to one of states 0..5 at random) with chance 6/7, "solid" (go to state 6) with chance 1/7.
# Target policy: always "solid". Learning about one policy from another's data is off policy learning.
X = np.zeros((7, 8))
for i in range(6):
    X[i, i], X[i, 7] = 2, 1                              # v(state i) = 2 w_i + w_7
X[6, 6], X[6, 7] = 1, 2                                  # v(state 6) = w_6 + 2 w_7

def run(features, steps=1000, alpha=0.01, gamma=0.99, seed=0):
    rng = np.random.default_rng(seed)
    w = np.ones(features.shape[1])
    if features.shape[1] == 8:
        w[6] = 10                                         # the starting weights used in the book
    s, norms = int(rng.integers(7)), []
    for t in range(steps + 1):
        if t % 200 == 0:
            norms.append(round(float(np.linalg.norm(w)), 2))
        solid = rng.random() < 1 / 7
        s2 = 6 if solid else int(rng.integers(6))
        rho = 7.0 if solid else 0.0                       # importance ratio pi / b: 1 / (1/7) for solid, 0 / (6/7) for dashed
        delta = 0 + gamma * features[s2] @ w - features[s] @ w
        w += alpha * rho * delta * features[s]            # semi gradient off policy TD(0)
        s = s2
    return norms

print("size of w at steps 0, 200, ..., 1000")
print("linear features, 8 weights :", run(X))
print("a table, 7 separate values :", run(np.eye(7)))
print("All three of function approximation, bootstrapping and off policy data together make the weights blow up.")
