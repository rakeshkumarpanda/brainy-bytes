# 2.3 Attention and transformers
# Example "attention_memory" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# The memory task from chapter 2.2, solved with one attention head.
# Each token has (value, marker). The last token asks: which value carried the marker?
import numpy as np


def make_batch(rng, n, T):
    x = np.zeros((n, T, 2))
    x[:, :, 0] = rng.normal(scale=1.0, size=(n, T))     # noise as large as the signal
    first = rng.uniform(-1, 1, size=(n, 1))
    x[:, 0, 0] = first[:, 0]
    x[:, 0, 1] = 1.0                                    # the marker
    return x, first


def softmax(s):
    e = np.exp(s - s.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def train_attention(T, steps=600, d=8, lr=0.02, seed=0):
    rng = np.random.default_rng(seed)
    Wq, Wk, Wv = (rng.normal(scale=0.5, size=(2, d)) for _ in range(3))
    bq = np.zeros(d)
    Wo = rng.normal(scale=0.1, size=(d, 1))
    params = [Wq, bq, Wk, Wv, Wo]
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    for step in range(1, steps + 1):
        x, target = make_batch(rng, 64, T)
        q = x[:, -1] @ Wq + bq                           # the query comes from the last token
        K, V = x @ Wk, x @ Wv                            # every token offers a key and a value
        a = softmax(np.einsum('ntd,nd->nt', K, q) / np.sqrt(d))
        out = np.einsum('nt,ntd->nd', a, V)
        y = out @ Wo
        dy = 2 * (y - target) / len(y)
        dout = dy @ Wo.T
        da = np.einsum('nd,ntd->nt', dout, V)
        ds = a * (da - (a * da).sum(axis=1, keepdims=True)) / np.sqrt(d)
        dq = np.einsum('nt,ntd->nd', ds, K)
        dK = ds[:, :, None] * q[:, None, :]
        dV = a[:, :, None] * dout[:, None, :]
        grads = [x[:, -1].T @ dq, dq.sum(axis=0), np.einsum('nti,ntd->id', x, dK),
                 np.einsum('nti,ntd->id', x, dV), out.T @ dy]
        for k, (p, g) in enumerate(zip(params, grads)):
            m[k] = 0.9 * m[k] + 0.1 * g
            v[k] = 0.999 * v[k] + 0.001 * g * g
            p -= lr * (m[k] / (1 - 0.9 ** step)) / (np.sqrt(v[k] / (1 - 0.999 ** step)) + 1e-8)
    x, target = make_batch(np.random.default_rng(99), 1000, T)
    q = x[:, -1] @ Wq + bq
    a = softmax(np.einsum('ntd,nd->nt', x @ Wk, q) / np.sqrt(d))
    y = np.einsum('nt,ntd->nd', a, x @ Wv) @ Wo
    return np.mean((y - target) ** 2), a[:, 0].mean()


print('always answering 0 gives about 0.333. The plain RNN failed from 40 steps.')
for T in [20, 60, 200]:
    err, w0 = train_attention(T)
    print(f'attention, {T:3d} steps: test error {err:.1e}, weight on the marked token {w0:.3f}')
