# 2.2 Monte Carlo and temporal difference learning
# Example "mc_vs_td" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

true_v = np.arange(1, 6) / 6
runs, episodes = 100, 100
rng = np.random.default_rng(1)

def run(method, alpha):
    err = np.zeros(episodes)
    for _ in range(runs):
        V = np.full(7, 0.5)
        V[0] = V[6] = 0.0
        for ep in range(episodes):
            s, path = 3, []
            while 1 <= s <= 5:
                s2 = s + (1 if rng.random() < 0.5 else -1)
                r = 1.0 if s2 == 6 else 0.0
                if method == "TD":
                    V[s] += alpha * (r + V[s2] - V[s])
                path.append(s)
                s = s2
            if method == "MC":
                G = 1.0 if s == 6 else 0.0
                for x in path:                           # every visit Monte Carlo with a constant step size
                    V[x] += alpha * (G - V[x])
            err[ep] += np.sqrt(np.mean((V[1:6] - true_v) ** 2))
    return err / runs

for method, alpha in [("MC", 0.01), ("MC", 0.03), ("TD", 0.05), ("TD", 0.15)]:
    e = run(method, alpha)
    print(method, "alpha", str(alpha).ljust(4), " RMS error after 10, 50, 100 episodes:", e[9].round(3), e[49].round(3), e[99].round(3))
