# 3.3 RL in practice: models, offline data and RLHF
# Example "rlhf_reward_model" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# A toy version of RLHF. A "prompt" has 6 possible answers. The reference model (after supervised fine tuning)
# picks them with probabilities pi_ref. Each answer has a hidden true quality that only the human labellers can sense.
answers = ["wrong", "vague", "correct", "correct and clear", "too long", "made up but confident"]
quality = np.array([-2.0, -0.5, 1.0, 2.0, 0.0, -1.0])
seems = quality.copy()
seems[5] = 3.0                                            # labellers cannot check facts, and a confident made up answer seems great
pi_ref = np.array([0.15, 0.30, 0.25, 0.05, 0.20, 0.05])
rng = np.random.default_rng(0)

# Step 1: collect preferences. Show labellers two answers sampled from pi_ref. They prefer i over j with
# probability sigmoid(seems_i - seems_j): the Bradley-Terry model, applied to how good each answer seems.
sigmoid = lambda z: 1 / (1 + np.exp(-z))
pairs = []
for _ in range(400):
    i, j = rng.choice(6, size=2, replace=False, p=pi_ref)
    pairs.append((i, j) if rng.random() < sigmoid(seems[i] - seems[j]) else (j, i))   # (winner, loser)
pairs = np.array(pairs)

# Step 2: fit a reward model r by maximising the log likelihood of the preferences, sum of log sigmoid(r_w - r_l).
r = np.zeros(6)
for _ in range(2000):
    p = sigmoid(r[pairs[:, 0]] - r[pairs[:, 1]])
    grad = np.zeros(6)
    np.add.at(grad, pairs[:, 0], 1 - p)
    np.add.at(grad, pairs[:, 1], -(1 - p))
    r += 0.01 * grad
    r -= r.mean()                                         # rewards are only defined up to a constant
times = np.bincount(pairs.ravel(), minlength=6)
print("answer                  seems to labellers  learned reward  true quality  times compared")
for k in range(6):
    print(f"{answers[k]:22s}  {seems[k] - seems.mean():18.2f}  {r[k]:14.2f}  {quality[k]:12.1f}  {times[k]:14d}")

# Step 3: the best policy for "maximise reward minus beta times KL from pi_ref" has a closed form:
# pi(y) is proportional to pi_ref(y) * exp(r(y) / beta). PPO in real RLHF approximates this with a network.
print()
for beta in [10.0, 2.0, 1.0, 0.1]:
    pi = pi_ref * np.exp(r / beta)
    pi /= pi.sum()
    kl = np.sum(pi * np.log(pi / pi_ref))
    print(f"beta = {beta:4.1f}: P(correct and clear) {pi[3]:.2f}, P(made up) {pi[5]:.2f}, expected true quality {pi @ quality:5.2f}, KL {kl:.2f}")
print(f"reference policy: expected true quality {pi_ref @ quality:5.2f}")
print("A small beta lets the policy chase the reward model wherever it is wrong: reward hacking.")
