# 1.2 Multi armed bandits
# Example "epsilon_greedy" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

true_means = np.array([0.2, 0.5, 0.8, 0.3, 0.6])         # arm 2 is best, but the agent does not know
runs, steps = 500, 1000                                  # 500 separate experiments, played side by side
rng = np.random.default_rng(0)
rows = np.arange(runs)

def play(eps):
    Q, N = np.zeros((runs, 5)), np.zeros((runs, 5))
    total, best = 0.0, 0
    for t in range(steps):
        explore = rng.random(runs) < eps
        a = np.where(explore, rng.integers(0, 5, runs), Q.argmax(axis=1))
        r = rng.normal(true_means[a], 1.0)               # noisy reward
        N[rows, a] += 1
        Q[rows, a] += (r - Q[rows, a]) / N[rows, a]      # incremental average
        total += r.sum()
        best += (a == 2).sum()
    return total / (runs * steps), best / (runs * steps)

for eps in [0.0, 0.01, 0.1, 0.3]:
    avg, opt = play(eps)
    print("epsilon", str(eps).ljust(4), " average reward", round(avg, 3), " best arm chosen", str(round(100 * opt, 1)) + "%")
print("always picking the best arm would average", true_means.max())
