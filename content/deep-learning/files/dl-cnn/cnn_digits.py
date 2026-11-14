# 2.1 Convolutional neural networks
# Example "cnn_digits" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A small convolutional network in numpy, trained on 8 x 8 handwritten digits.
# conv 3x3 (8 filters, padding 1) -> ReLU -> 2x2 max pool -> dense 10 -> softmax
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

digits = load_digits()
X = digits.images / 16.0                       # shape (1797, 8, 8), values 0 to 1
y = digits.target
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)

rng = np.random.default_rng(0)
F = 8
Wc = rng.normal(scale=np.sqrt(2 / 9), size=(9, F))     # each column is one 3x3 filter
bc = np.zeros(F)
Wd = rng.normal(scale=np.sqrt(2 / (4 * 4 * F)), size=(4 * 4 * F, 10))
bd = np.zeros(10)


def patches(imgs):
    # every 3x3 patch of the padded images as a row: (n, 8, 8, 9)
    p = np.pad(imgs, ((0, 0), (1, 1), (1, 1)))
    return np.stack([p[:, i:i + 8, j:j + 8] for i in range(3) for j in range(3)], axis=-1)


def forward(imgs):
    P = patches(imgs)
    z = P @ Wc + bc                                   # (n, 8, 8, F): the convolution
    a = np.maximum(z, 0)
    blocks = a.reshape(-1, 4, 2, 4, 2, F)
    pooled = blocks.max(axis=(2, 4))                  # (n, 4, 4, F)
    scores = pooled.reshape(len(imgs), -1) @ Wd + bd
    return P, z, a, blocks, pooled, scores


def accuracy(imgs, labels):
    return np.mean(forward(imgs)[-1].argmax(axis=1) == labels)


v = [np.zeros_like(p) for p in (Wc, bc, Wd, bd)]
lr = 0.05
for epoch in range(1, 9):
    order = rng.permutation(len(X_tr))
    for start in range(0, len(order), 32):
        idx = order[start:start + 32]
        imgs, labels = X_tr[idx], y_tr[idx]
        P, z, a, blocks, pooled, scores = forward(imgs)
        e = np.exp(scores - scores.max(axis=1, keepdims=True))
        prob = e / e.sum(axis=1, keepdims=True)
        prob[np.arange(len(idx)), labels] -= 1           # softmax cross entropy gradient
        g = prob / len(idx)
        gWd = pooled.reshape(len(idx), -1).T @ g
        gbd = g.sum(axis=0)
        gpool = (g @ Wd.T).reshape(pooled.shape)
        mask = blocks == pooled[:, :, None, :, None, :]  # where each max came from
        ga = (mask * gpool[:, :, None, :, None, :]).reshape(a.shape)
        gz = ga * (z > 0)
        gWc = P.reshape(-1, 9).T @ gz.reshape(-1, F)
        gbc = gz.reshape(-1, F).sum(axis=0)
        for k, (p, gr) in enumerate(zip((Wc, bc, Wd, bd), (gWc, gbc, gWd, gbd))):
            v[k] = 0.9 * v[k] + gr          # SGD with momentum
            p -= lr * v[k]
    if epoch in (1, 2, 4, 8):
        print(f'epoch {epoch}: train accuracy {accuracy(X_tr, y_tr):.3f}, test accuracy {accuracy(X_te, y_te):.3f}')

n_weights = Wc.size + bc.size + Wd.size + bd.size
print('weights in the network:', n_weights)
