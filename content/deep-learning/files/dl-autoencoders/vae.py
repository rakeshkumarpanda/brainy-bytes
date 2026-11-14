# 3.1 Autoencoders and variational autoencoders
# Example "vae" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A variational autoencoder (VAE) on 8 x 8 digits with a 2 number latent space, written in numpy.
import numpy as np
from sklearn.datasets import load_digits

digits = load_digits()
X = digits.data / 16.0
rng = np.random.default_rng(0)
H, Z = 64, 2
W1 = rng.normal(scale=0.1, size=(64, H)); b1 = np.zeros(H)
Wm = rng.normal(scale=0.1, size=(H, Z)); bm = np.zeros(Z)        # encoder mean
Wv = rng.normal(scale=0.1, size=(H, Z)); bv = np.zeros(Z)        # encoder log variance
W3 = rng.normal(scale=0.1, size=(Z, H)); b3 = np.zeros(H)
W4 = rng.normal(scale=0.1, size=(H, 64)); b4 = np.zeros(64)
params = [W1, b1, Wm, bm, Wv, bv, W3, b3, W4, b4]
m = [np.zeros_like(p) for p in params]
v = [np.zeros_like(p) for p in params]


def decode(z):
    h2 = np.tanh(z @ W3 + b3)
    return h2, 1 / (1 + np.exp(-(h2 @ W4 + b4)))


t = 0
for epoch in range(1, 201):
    order = rng.permutation(len(X))
    total_rec = total_kl = 0.0
    for start in range(0, len(X), 64):
        x = X[order[start:start + 64]]
        n = len(x)
        h = np.tanh(x @ W1 + b1)
        mu, logvar = h @ Wm + bm, h @ Wv + bv
        eps = rng.normal(size=mu.shape)
        z = mu + np.exp(0.5 * logvar) * eps                   # the reparameterisation trick
        h2, xhat = decode(z)
        rec = -np.sum(x * np.log(xhat + 1e-7) + (1 - x) * np.log(1 - xhat + 1e-7)) / n
        kl = -0.5 * np.sum(1 + logvar - mu ** 2 - np.exp(logvar)) / n
        total_rec += rec * n
        total_kl += kl * n
        d4 = (xhat - x) / n                                    # gradient of the reconstruction term
        dh2 = d4 @ W4.T * (1 - h2 ** 2)
        dz = dh2 @ W3.T
        dmu = dz + mu / n                                      # plus the KL gradient
        dlogvar = dz * eps * 0.5 * np.exp(0.5 * logvar) + 0.5 * (np.exp(logvar) - 1) / n
        dh = (dmu @ Wm.T + dlogvar @ Wv.T) * (1 - h ** 2)
        grads = [x.T @ dh, dh.sum(0), h.T @ dmu, dmu.sum(0), h.T @ dlogvar, dlogvar.sum(0),
                 z.T @ dh2, dh2.sum(0), h2.T @ d4, d4.sum(0)]
        t += 1
        for k, (p, g) in enumerate(zip(params, grads)):
            m[k] = 0.9 * m[k] + 0.1 * g
            v[k] = 0.999 * v[k] + 0.001 * g * g
            p -= 0.005 * (m[k] / (1 - 0.9 ** t)) / (np.sqrt(v[k] / (1 - 0.999 ** t)) + 1e-8)
    if epoch in (1, 10, 50, 100, 200):
        print(f'epoch {epoch:2d}: reconstruction {total_rec / len(X):6.2f}, KL {total_kl / len(X):5.2f}, '
              f'loss (negative ELBO) {(total_rec + total_kl) / len(X):6.2f}')

# where do the digits sit in the 2 number latent space?
mu_all = np.tanh(X @ W1 + b1) @ Wm + bm
for d in [0, 1, 6]:
    c = mu_all[digits.target == d].mean(axis=0)
    print(f'digit {d}: average code ({c[0]:5.2f}, {c[1]:5.2f})')

# walk through the latent space from the average code of a 1 to the average code of a 0
c1, c0 = mu_all[digits.target == 1].mean(axis=0), mu_all[digits.target == 0].mean(axis=0)
codes = np.array([c1, 0.5 * (c1 + c0), c0])
imgs = decode(codes)[1].reshape(3, 8, 8)
print('decoded from the code of a 1, the halfway point, and the code of a 0:')
for r in range(8):
    print('   '.join(''.join('#' if p > 0.5 else '+' if p > 0.25 else '.' for p in imgs[k, r]) for k in range(3)))
