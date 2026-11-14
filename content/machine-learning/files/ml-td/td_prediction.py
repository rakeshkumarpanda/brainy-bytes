# 2.2 Monte Carlo and temporal difference learning
# Example "td_prediction" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

rng = np.random.default_rng(0)
true_v = np.arange(1, 6) / 6
V = np.full(7, 0.5)
V[0] = V[6] = 0.0                                        # the two ends are terminal: value 0
alpha = 0.1
for ep in range(1, 1001):
    s = 3
    while 1 <= s <= 5:
        s2 = s + rng.choice([-1, 1])
        r = 1.0 if s2 == 6 else 0.0
        td_error = r + V[s2] - V[s]                       # TD target r + gamma V(s'), with gamma = 1
        V[s] += alpha * td_error                          # update now, without waiting for the episode to end
        s = s2
    if ep in (1, 10, 100, 1000):
        print("after", str(ep).rjust(4), "episodes:", V[1:6].round(3), " RMS error", round(float(np.sqrt(np.mean((V[1:6] - true_v) ** 2))), 3))
print("true values:              ", true_v.round(3))
