# 3.4 Energy based models: Hopfield networks, Boltzmann machines and RBMs
# Example "rbm_cd" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A restricted Boltzmann machine trained with contrastive divergence on 4x4 "bars and stripes" images.
# 16 pixels is small enough to compute the exact likelihood, so we can watch real learning, not a proxy.
import itertools

import numpy as np

rng = np.random.default_rng(0)
rows = np.array(list(itertools.product([0, 1], repeat=4)))
bars = np.array([np.repeat(r, 4) for r in rows])                    # each column all on or all off
stripes = np.array([np.tile(r, 4) for r in rows])                   # each row all on or all off
data = np.unique(np.vstack([bars, stripes]), axis=0).astype(float)  # 30 distinct images (empty and full appear in both)
print('training images:', len(data), '  best possible average log likelihood:', round(np.log(1 / len(data)), 3))

sig = lambda x: 1 / (1 + np.exp(-x))
ALL_V = np.array(list(itertools.product([0, 1], repeat=16)), dtype=float)   # all 65,536 images


def free_energy(v, W, a, b):
    """F(v) = -a.v - sum_j log(1 + e^(b_j + v.W_j)). Then p(v) = e^(-F(v)) / Z."""
    return -v @ a - np.logaddexp(0, v @ W + b).sum(axis=1)


def avg_log_lik(W, a, b):
    log_z = np.logaddexp.reduce(-free_energy(ALL_V, W, a, b))       # exact log Z over every image
    return float(np.mean(-free_energy(data, W, a, b) - log_z))


def train(k, epochs=5000, hidden=16, lr=0.2):
    W = rng.normal(0, 0.01, (16, hidden))
    a, b = np.zeros(16), np.zeros(hidden)
    for epoch in range(1, epochs + 1):
        v0 = data
        ph0 = sig(v0 @ W + b)                                       # positive phase: hidden given the data
        h = (rng.random(ph0.shape) < ph0).astype(float)
        for _ in range(k):                                          # k steps of Gibbs sampling
            v = (rng.random((len(data), 16)) < sig(h @ W.T + a)).astype(float)
            ph = sig(v @ W + b)
            h = (rng.random(ph.shape) < ph).astype(float)
        W += lr * (v0.T @ ph0 - v.T @ ph) / len(data)               # <v h>_data - <v h>_model
        a += lr * (v0 - v).mean(axis=0)
        b += lr * (ph0 - ph).mean(axis=0)
        if epoch in (1, 500, 2000, 5000):
            print(f'  CD-{k}  epoch {epoch:4d}: average log likelihood {avg_log_lik(W, a, b):.3f}')
    return W, a, b


W, a, b = train(k=1)
train(k=10)

# Generate: run Gibbs chains from random noise and check how many end on a real bar or stripe image
v = (rng.random((500, 16)) < 0.5).astype(float)
for _ in range(1000):
    h = (rng.random((500, W.shape[1])) < sig(v @ W + b)).astype(float)
    v = (rng.random((500, 16)) < sig(h @ W.T + a)).astype(float)
valid = {tuple(r) for r in data}
ok = np.mean([tuple(r) in valid for r in v])
print(f'CD-1 model: {ok:.0%} of 500 generated images are valid bars or stripes, '
      f'{len({tuple(r) for r in v if tuple(r) in valid})} of the 30 kinds appear')
