# 3.1 Autoencoders and variational autoencoders
# Example "autoencoder" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# An autoencoder squeezes 64 pixel digits through a small code and rebuilds them.
# Compare it with PCA, which is the best possible linear compression.
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

X = load_digits().data / 16.0                        # 1797 images, 64 pixels in [0, 1]
rng = np.random.default_rng(0)
idx = rng.permutation(len(X))
X_tr, X_te = X[idx[:1400]], X[idx[1400:]]
mean = X_tr.mean(axis=0)


def train_autoencoder(k, hidden=64, epochs=200, lr=0.003, seed=0):
    r = np.random.default_rng(seed)
    sizes = [64, hidden, k, hidden, 64]
    W = [r.normal(scale=np.sqrt(1 / a), size=(a, b)) for a, b in zip(sizes, sizes[1:])]
    b = [np.zeros(s) for s in sizes[1:]]
    m = [np.zeros_like(p) for p in W + b]
    v = [np.zeros_like(p) for p in W + b]
    acts = [np.tanh, lambda z: z, np.tanh, lambda z: z]     # the code layer and output are linear
    t = 0

    def forward(x):
        hs = [x - mean]
        for Wi, bi, f in zip(W, b, acts):
            hs.append(f(hs[-1] @ Wi + bi))
        return hs

    for epoch in range(epochs):
        order = r.permutation(len(X_tr))
        for start in range(0, len(X_tr), 64):
            xb = X_tr[order[start:start + 64]]
            hs = forward(xb)
            g = 2 * (hs[-1] - (xb - mean)) / len(xb)
            gW, gb = [None] * 4, [None] * 4
            for i in (3, 2, 1, 0):
                gW[i], gb[i] = hs[i].T @ g, g.sum(axis=0)
                if i > 0:
                    g = g @ W[i].T
                    if acts[i - 1] is np.tanh:
                        g = g * (1 - hs[i] ** 2)
            t += 1
            for j, (p, gr) in enumerate(zip(W + b, gW + gb)):
                m[j] = 0.9 * m[j] + 0.1 * gr
                v[j] = 0.999 * v[j] + 0.001 * gr * gr
                p -= lr * (m[j] / (1 - 0.9 ** t)) / (np.sqrt(v[j] / (1 - 0.999 ** t)) + 1e-8)
    rec = forward(X_te)[-1] + mean
    return np.mean((rec - X_te) ** 2)


for k in [2, 8]:
    pca = PCA(n_components=k).fit(X_tr)
    pca_err = np.mean((pca.inverse_transform(pca.transform(X_te)) - X_te) ** 2)
    ae_err = train_autoencoder(k)
    print(f'code size {k}: PCA error {pca_err:.4f}, autoencoder error {ae_err:.4f}  (64 pixels -> {k} numbers)')
print(f'just predicting the average image: error {np.mean((mean - X_te) ** 2):.4f}')
