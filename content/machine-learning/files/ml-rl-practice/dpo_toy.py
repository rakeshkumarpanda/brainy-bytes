# 3.3 RL in practice: models, offline data and RLHF
# Example "dpo_toy" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Direct preference optimisation (DPO, Rafailov and colleagues 2023) on the same toy problem, with honest labellers.
# DPO skips the reward model and the RL step: it trains the policy directly on the preference pairs.
quality = np.array([-2.0, -0.5, 1.0, 2.0, 0.0, -1.0])
pi_ref = np.array([0.15, 0.30, 0.25, 0.05, 0.20, 0.05])
sigmoid = lambda z: 1 / (1 + np.exp(-z))
rng = np.random.default_rng(1)
pairs = []
for _ in range(400):
    i, j = rng.choice(6, size=2, replace=False, p=pi_ref)
    pairs.append((i, j) if rng.random() < sigmoid(quality[i] - quality[j]) else (j, i))
W, L = np.array(pairs).T
beta = 1.0

# DPO loss: -log sigmoid(beta * [log pi(w)/pi_ref(w) - log pi(l)/pi_ref(l)]), with pi = softmax(theta).
theta = np.log(pi_ref).copy()                             # start from the reference policy
for _ in range(3000):
    logpi = theta - np.log(np.exp(theta).sum())
    margin = beta * ((logpi[W] - np.log(pi_ref[W])) - (logpi[L] - np.log(pi_ref[L])))
    g = beta * (1 - sigmoid(margin))                      # how much each pair still wants to move
    grad = np.zeros(6)
    np.add.at(grad, W, g)
    np.add.at(grad, L, -g)                                # the softmax normaliser cancels between winner and loser
    theta += 0.01 * grad
pi_dpo = np.exp(theta) / np.exp(theta).sum()

# The RLHF route for comparison: fit a Bradley-Terry reward, then pi is proportional to pi_ref * exp(r / beta).
r = np.zeros(6)
for _ in range(3000):
    p = sigmoid(r[W] - r[L])
    grad = np.zeros(6)
    np.add.at(grad, W, 1 - p)
    np.add.at(grad, L, -(1 - p))
    r += 0.01 * grad
pi_rlhf = pi_ref * np.exp(r / beta)
pi_rlhf /= pi_rlhf.sum()

print("reference policy:", pi_ref.round(3), " expected quality", round(float(pi_ref @ quality), 2))
print("DPO policy      :", pi_dpo.round(3), " expected quality", round(float(pi_dpo @ quality), 2))
print("RLHF policy     :", pi_rlhf.round(3), " expected quality", round(float(pi_rlhf @ quality), 2))
print("largest difference between DPO and RLHF probabilities:", round(float(np.abs(pi_dpo - pi_rlhf).max()), 4))
