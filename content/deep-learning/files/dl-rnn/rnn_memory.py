# 2.2 Recurrent networks, LSTM and GRU
# Example "rnn_memory" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Train a vanilla RNN with backpropagation through time (BPTT) on a memory task:
# see a number at step 1, then noise, and output the first number at the last step.
import numpy as np


def make_batch(rng, n, T):
    x = np.zeros((n, T, 2))
    x[:, :, 0] = rng.normal(scale=1.0, size=(n, T))     # channel 0: noise as large as the signal
    first = rng.uniform(-1, 1, size=(n, 1))
    x[:, 0, 0] = first[:, 0]                            # the number to remember
    x[:, 0, 1] = 1.0                                    # channel 1: a marker that says "remember this"
    return x, first


def train_rnn(T, steps=1000, H=16, lr=0.01, seed=0):
    rng = np.random.default_rng(seed)
    Wx = rng.normal(scale=0.5, size=(2, H))
    Wh = rng.normal(scale=1 / np.sqrt(H), size=(H, H))
    b = np.zeros(H)
    Wy = rng.normal(scale=0.1, size=(H, 1))
    by = np.zeros(1)
    params = [Wx, Wh, b, Wy, by]
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    for step in range(1, steps + 1):
        x, target = make_batch(rng, 64, T)
        hs = [np.zeros((64, H))]
        for t in range(T):                               # forward through time
            hs.append(np.tanh(x[:, t] @ Wx + hs[-1] @ Wh + b))
        y = hs[-1] @ Wy + by
        dy = 2 * (y - target) / len(y)
        grads = [np.zeros_like(p) for p in params]
        grads[3] = hs[-1].T @ dy
        grads[4] = dy.sum(axis=0)
        dh = dy @ Wy.T
        for t in range(T, 0, -1):                        # backward through time
            dz = dh * (1 - hs[t] ** 2)
            grads[0] += x[:, t - 1].T @ dz
            grads[1] += hs[t - 1].T @ dz
            grads[2] += dz.sum(axis=0)
            dh = dz @ Wh.T
        for k, (p, g) in enumerate(zip(params, grads)):
            g = np.clip(g, -1, 1)                         # gradient clipping
            m[k] = 0.9 * m[k] + 0.1 * g
            v[k] = 0.999 * v[k] + 0.001 * g * g
            p -= lr * (m[k] / (1 - 0.9 ** step)) / (np.sqrt(v[k] / (1 - 0.999 ** step)) + 1e-8)
    x, target = make_batch(np.random.default_rng(99), 1000, T)
    h = np.zeros((1000, H))
    for t in range(T):
        h = np.tanh(x[:, t] @ Wx + h @ Wh + b)
    return np.mean((h @ Wy + by - target) ** 2)


print('always answering 0 gives an error of about 0.333')
for T in [5, 20, 40, 60]:
    print(f'remember across {T:2d} steps: test error {train_rnn(T):.4f}')
