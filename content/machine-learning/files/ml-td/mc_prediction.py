# 2.2 Monte Carlo and temporal difference learning
# Example "mc_prediction" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Random walk: states A to E (1 to 5) between two ends. Start in C, step left or right with chance 1/2.
# Reaching the right end gives reward 1, everything else 0. True values: 1/6, 2/6, 3/6, 4/6, 5/6.
rng = np.random.default_rng(0)
true_v = np.arange(1, 6) / 6

def episode():
    s, visited = 3, []
    while 1 <= s <= 5:
        visited.append(s)
        s += rng.choice([-1, 1])
    return visited, 1.0 if s == 6 else 0.0               # the states seen and the final reward

V, N = np.full(7, 0.5), np.zeros(7)                       # start every estimate at 0.5
for ep in range(1, 1001):
    visited, G = episode()                               # gamma = 1 and one final reward, so every state's return is G
    for s in set(visited):                               # first visit Monte Carlo: average the returns seen
        N[s] += 1
        V[s] += (G - V[s]) / N[s]
    if ep in (1, 10, 100, 1000):
        print("after", str(ep).rjust(4), "episodes:", V[1:6].round(3), " RMS error", round(float(np.sqrt(np.mean((V[1:6] - true_v) ** 2))), 3))
print("true values:              ", true_v.round(3))
