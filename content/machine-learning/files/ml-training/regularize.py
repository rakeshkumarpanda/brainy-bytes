# 1.3 Training deep networks: optimisers, normalisation and regularisation
# Example "regularize" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Overfitting and four cures: weight decay, dropout and early stopping on a tiny regression.
import numpy as np

rng = np.random.default_rng(3)
x_train = np.sort(rng.uniform(-3, 3, 16)).reshape(-1, 1)
y_train = np.sin(x_train) + rng.normal(scale=0.3, size=x_train.shape)
x_val = np.linspace(-3, 3, 200).reshape(-1, 1)
y_val = np.sin(x_val) + rng.normal(scale=0.3, size=x_val.shape)


def train(decay=0.0, keep=1.0, patience=None, epochs=3000, lr=0.01, seed=0):
    r = np.random.default_rng(seed)
    sizes = [1, 64, 64, 1]
    W = [r.normal(scale=np.sqrt(1 / a), size=(a, b)) for a, b in zip(sizes, sizes[1:])]
    b = [np.zeros(s) for s in sizes[1:]]
    m = [np.zeros_like(p) for p in W + b]
    v = [np.zeros_like(p) for p in W + b]

    def forward(x, train_mode):
        hs, raw, masks = [x], [], []
        for i in range(2):
            h = np.tanh(hs[-1] @ W[i] + b[i])
            mask = (r.random(h.shape) < keep) / keep if train_mode else 1.0
            raw.append(h)
            masks.append(mask)
            hs.append(h * mask)
        return hs, raw, masks, hs[-1] @ W[2] + b[2]

    best, best_epoch, best_params = np.inf, 0, None
    for t in range(1, epochs + 1):
        hs, raw, masks, out = forward(x_train, True)
        g = 2 * (out - y_train) / len(x_train)
        grads_W, grads_b = [None] * 3, [None] * 3
        for i in (2, 1, 0):
            grads_W[i] = hs[i].T @ g + decay * W[i]
            grads_b[i] = g.sum(axis=0)
            if i > 0:
                g = (g @ W[i].T) * masks[i - 1] * (1 - raw[i - 1] ** 2)
        for j, (p, gr) in enumerate(zip(W + b, grads_W + grads_b)):
            m[j] = 0.9 * m[j] + 0.1 * gr
            v[j] = 0.999 * v[j] + 0.001 * gr * gr
            p -= lr * (m[j] / (1 - 0.9 ** t)) / (np.sqrt(v[j] / (1 - 0.999 ** t)) + 1e-8)
        if patience:
            val = np.mean((forward(x_val, False)[3] - y_val) ** 2)
            if val < best:
                best, best_epoch, best_params = val, t, ([w.copy() for w in W], [c.copy() for c in b])
            elif t - best_epoch >= patience:
                W[:], b[:] = best_params
                break
    train_mse = np.mean((forward(x_train, False)[3] - y_train) ** 2)
    val_mse = np.mean((forward(x_val, False)[3] - y_val) ** 2)
    return train_mse, val_mse, t


print('                  train MSE   validation MSE')
for name, kw in [('no regularisation', {}), ('weight decay', {'decay': 0.01}), ('dropout keep 0.8', {'keep': 0.8}), ('early stopping', {'patience': 200})]:
    tr, va, t = train(**kw)
    extra = f'   (stopped at epoch {t})' if 'patience' in kw else ''
    print(f'  {name:17s} {tr:.4f}      {va:.4f}{extra}')
