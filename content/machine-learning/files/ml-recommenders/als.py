# 3.3 Recommender systems
# Example "als" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

rng = np.random.default_rng(0)
n_users, n_items, k = 60, 30, 2
U_true, V_true = rng.normal(0, 1, (n_users, k)), rng.normal(0, 1, (n_items, k))
full = np.clip(3 + U_true @ V_true.T, 1, 5)
mask = rng.random((n_users, n_items)) < 0.4
mu = full[mask].mean()
X = np.where(mask, full - mu, 0.0)                       # centred known ratings, 0 where unknown
P, Q = rng.normal(0, 0.1, (n_users, k)), rng.normal(0, 0.1, (n_items, k))
lam = 1.0
I = np.eye(k)
for sweep in range(1, 11):
    for u in range(n_users):                             # fix Q, solve each user exactly
        Qu = Q[mask[u]]
        P[u] = np.linalg.solve(Qu.T @ Qu + lam * I, Qu.T @ X[u, mask[u]])
    for i in range(n_items):                             # fix P, solve each item exactly
        Pi = P[mask[:, i]]
        Q[i] = np.linalg.solve(Pi.T @ Pi + lam * I, Pi.T @ X[mask[:, i], i])
    pred = mu + P @ Q.T
    if sweep in (1, 2, 3, 5, 10):
        tr = np.sqrt(np.mean((pred - full)[mask] ** 2))
        te = np.sqrt(np.mean((pred - full)[~mask] ** 2))
        print("sweep", str(sweep).rjust(2), " train RMSE", round(float(tr), 3), " test RMSE", round(float(te), 3))
print("always guessing the average:", round(float(np.sqrt(np.mean((mu - full)[~mask] ** 2))), 3))
