# 3.2 Policy gradients, actor critic and PPO
# Example "ppo_cartpole" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# PPO with the clipped objective on CartPole. Policy: pi(right | s) = sigmoid(theta . s), only 4 weights.
# Critic: a least squares fit of the return on simple features. Each batch of data is reused for several epochs.
def cart_step(s, a):                                      # the same physics as before
    x, v, th, om = s
    force = 10.0 if a == 1 else -10.0
    cos, sin = np.cos(th), np.sin(th)
    tmp = (force + 0.05 * om * om * sin) / 1.1
    alpha = (9.8 * sin - cos * tmp) / (0.5 * (4 / 3 - 0.1 * cos * cos / 1.1))
    acc = tmp - 0.05 * alpha * cos / 1.1
    s = np.array([x + 0.02 * v, v + 0.02 * acc, th + 0.02 * om, om + 0.02 * alpha])
    return s, abs(s[0]) > 2.4 or abs(s[2]) > 0.2095

feats = lambda S: np.hstack([np.ones((len(S), 1)), S, S ** 2])   # critic features: 1, s and s squared
sigmoid = lambda z: 1 / (1 + np.exp(-z))
def train(use_clip, seed=0, gamma=0.99, lam=0.95, clip=0.2, lr=2.0):
    rng = np.random.default_rng(seed)
    theta, w = np.zeros(4), np.zeros(9)
    for it in range(1, 16):
        S, A, R, D, lengths = [], [], [], [], []
        while len(S) < 1000:                                  # collect a batch of about 1000 steps with the current policy
            s, done, t = rng.uniform(-0.05, 0.05, 4), False, 0
            while not done and t < 200:
                a = int(rng.random() < sigmoid(theta @ s))
                s2, done = cart_step(s, a)
                S.append(s); A.append(a); R.append(1.0); D.append(done or t == 199)
                s, t = s2, t + 1
            lengths.append(t)
        S, A, R, D = np.array(S), np.array(A), np.array(R), np.array(D)
        V = feats(S) @ w
        adv, ret, gae = np.zeros(len(S)), np.zeros(len(S)), 0.0
        for t in reversed(range(len(S))):                     # generalised advantage estimation
            next_v = 0.0 if D[t] else V[t + 1]
            delta = R[t] + gamma * next_v - V[t]
            gae = delta + (0.0 if D[t] else gamma * lam * gae)
            adv[t], ret[t] = gae, gae + V[t]
        adv = (adv - adv.mean()) / (adv.std() + 1e-8)
        p_old = np.where(A == 1, sigmoid(S @ theta), 1 - sigmoid(S @ theta))
        for epoch in range(10):                               # reuse the same batch 10 times
            p1 = sigmoid(S @ theta)
            p_new = np.where(A == 1, p1, 1 - p1)
            ratio = p_new / p_old
            if use_clip:                                  # outside the clip range the gradient is 0
                active = ((adv > 0) & (ratio < 1 + clip)) | ((adv < 0) & (ratio > 1 - clip))
            else:
                active = np.ones(len(S))
            grad_logp = (A - p1)[:, None] * S
            theta += lr * ((active * adv * ratio)[:, None] * grad_logp).mean(axis=0)
        w = np.linalg.lstsq(feats(S), ret, rcond=None)[0]     # refit the critic
        if it in (1, 5, 10, 15):
            print(f"  iteration {it:2d}: average episode length {np.mean(lengths):6.1f}, ratios in the 10th epoch from {ratio.min():.2f} to {ratio.max():.2f}")

for use_clip in [True, False]:
    print("PPO with the clip (epsilon = 0.2):" if use_clip else "The same without the clip:")
    train(use_clip)
