# 3.3 Recommender systems
# Example "mf_sgd" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

rng = np.random.default_rng(0)
n_users, n_items, k = 60, 30, 2
U_true, V_true = rng.normal(0, 1, (n_users, k)), rng.normal(0, 1, (n_items, k))
full = np.clip(3 + U_true @ V_true.T, 1, 5)                # hidden "true" ratings
mask = rng.random((n_users, n_items)) < 0.4                # we only see 40% of them
train = [(u, i, full[u, i]) for u in range(n_users) for i in range(n_items) if mask[u, i]]
test = [(u, i, full[u, i]) for u in range(n_users) for i in range(n_items) if not mask[u, i]]
mu = np.mean([r for _, _, r in train])
P, Q = rng.normal(0, 0.1, (n_users, k)), rng.normal(0, 0.1, (n_items, k))
bu, bi = np.zeros(n_users), np.zeros(n_items)
lr, reg = 0.02, 0.1
def rmse(data):
    return float(np.sqrt(np.mean([(r - (mu + bu[u] + bi[i] + P[u] @ Q[i])) ** 2 for u, i, r in data])))
for epoch in range(1, 61):
    for idx in rng.permutation(len(train)):
        u, i, r = train[idx]
        e = r - (mu + bu[u] + bi[i] + P[u] @ Q[i])         # error on one known rating
        bu[u] += lr * (e - reg * bu[u])
        bi[i] += lr * (e - reg * bi[i])
        P[u], Q[i] = P[u] + lr * (e * Q[i] - reg * P[u]), Q[i] + lr * (e * P[u] - reg * Q[i])
    if epoch in (1, 5, 10, 20, 40, 60):
        print("epoch", str(epoch).rjust(2), " train RMSE", round(rmse(train), 3), " test RMSE", round(rmse(test), 3))
print("always guessing the average:", round(float(np.sqrt(np.mean([(r - mu) ** 2 for _, _, r in test]))), 3))
