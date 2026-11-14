# 1.2 Multi armed bandits
# Example "ucb" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

true_means = np.array([0.2, 0.5, 0.8, 0.3, 0.6])
runs, steps = 500, 2000
rng = np.random.default_rng(1)
rows = np.arange(runs)

def play(rule, c=0.0, eps=0.0):
    Q, N, regret = np.zeros((runs, 5)), np.zeros((runs, 5)), 0.0
    for t in range(1, steps + 1):
        if rule == "ucb":
            bonus = np.where(N > 0, c * np.sqrt(np.log(t) / np.maximum(N, 1)), np.inf)   # untried arms first
            a = (Q + bonus).argmax(axis=1)
        else:
            a = np.where(rng.random(runs) < eps, rng.integers(0, 5, runs), Q.argmax(axis=1))
        r = rng.normal(true_means[a], 1.0)
        N[rows, a] += 1
        Q[rows, a] += (r - Q[rows, a]) / N[rows, a]
        regret += (true_means.max() - true_means[a]).sum()  # reward lost against always playing the best arm
    return regret / runs

print("average total regret over", steps, "pulls (lower is better)")
print("epsilon greedy, 0.1:", round(play("eps", eps=0.1), 1))
for c in [0.5, 1.0, 2.0]:
    print("UCB, c =", str(c).ljust(3), "      ", round(play("ucb", c=c), 1))
