# 2.2 Recurrent networks, LSTM and GRU
# Example "lstm_memory" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# The same memory task with an LSTM: gates decide what to store, keep and output.
import numpy as np


def make_batch(rng, n, T):
    x = np.zeros((n, T, 2))
    x[:, :, 0] = rng.normal(scale=1.0, size=(n, T))     # channel 0: noise as large as the signal
    first = rng.uniform(-1, 1, size=(n, 1))
    x[:, 0, 0] = first[:, 0]                            # the number to remember
    x[:, 0, 1] = 1.0                                    # channel 1: a marker that says "remember this"
    return x, first


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def lstm_forward(x, Wx, Wh, b, H):
    n, T, _ = x.shape
    h, c = np.zeros((n, H)), np.zeros((n, H))
    cache = []
    for t in range(T):
        z = x[:, t] @ Wx + h @ Wh + b
        i, f, o = sigmoid(z[:, :H]), sigmoid(z[:, H:2 * H]), sigmoid(z[:, 2 * H:3 * H])
        g = np.tanh(z[:, 3 * H:])
        c_prev, h_prev = c, h
        c = f * c_prev + i * g                           # keep some old memory, add some new
        h = o * np.tanh(c)
        cache.append((x[:, t], h_prev, c_prev, i, f, o, g, c))
    return h, cache


def train_lstm(T, forget_bias, steps=1000, H=16, lr=0.01, seed=0):
    rng = np.random.default_rng(seed)
    Wx = rng.normal(scale=0.5, size=(2, 4 * H))
    Wh = rng.normal(scale=1 / np.sqrt(H), size=(H, 4 * H))
    b = np.zeros(4 * H)
    b[H:2 * H] = forget_bias                             # a positive bias keeps the forget gate open (remember)
    Wy = rng.normal(scale=0.1, size=(H, 1))
    by = np.zeros(1)
    params = [Wx, Wh, b, Wy, by]
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    for step in range(1, steps + 1):
        x, target = make_batch(rng, 64, T)
        h, cache = lstm_forward(x, Wx, Wh, b, H)
        y = h @ Wy + by
        dy = 2 * (y - target) / len(y)
        grads = [np.zeros_like(p) for p in params]
        grads[3] = h.T @ dy
        grads[4] = dy.sum(axis=0)
        dh, dc = dy @ Wy.T, np.zeros_like(h)
        for xt, h_prev, c_prev, i, f, o, g, c in reversed(cache):
            tc = np.tanh(c)
            dc = dc + dh * o * (1 - tc ** 2)
            dz = np.concatenate([dc * g * i * (1 - i), dc * c_prev * f * (1 - f),
                                 dh * tc * o * (1 - o), dc * i * (1 - g ** 2)], axis=1)
            grads[0] += xt.T @ dz
            grads[1] += h_prev.T @ dz
            grads[2] += dz.sum(axis=0)
            dh, dc = dz @ Wh.T, dc * f                    # the cell path is multiplied only by f
        for k, (p, gr) in enumerate(zip(params, grads)):
            gr = np.clip(gr, -1, 1)
            m[k] = 0.9 * m[k] + 0.1 * gr
            v[k] = 0.999 * v[k] + 0.001 * gr * gr
            p -= lr * (m[k] / (1 - 0.9 ** step)) / (np.sqrt(v[k] / (1 - 0.999 ** step)) + 1e-8)
    x, target = make_batch(np.random.default_rng(99), 1000, T)
    h, _ = lstm_forward(x, Wx, Wh, b, H)
    return np.mean((h @ Wy + by - target) ** 2)


print('always answering 0 gives an error of about 0.333')
for T, fb in [(20, 1.0), (60, 1.0), (60, 5.0)]:
    print(f'LSTM, forget bias {fb}, remember across {T} steps: test error {train_lstm(T, fb):.4f}')
