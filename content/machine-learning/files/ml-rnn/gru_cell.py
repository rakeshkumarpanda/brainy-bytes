# 2.2 Recurrent networks, LSTM and GRU
# Example "gru_cell" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A GRU cell by hand, and how many weights RNN, GRU and LSTM layers need.
import numpy as np


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


rng = np.random.default_rng(0)
n_in, H = 3, 4
W = {k: rng.normal(scale=0.5, size=(n_in, H)) for k in 'zrh'}
U = {k: rng.normal(scale=0.5, size=(H, H)) for k in 'zrh'}
b = {k: np.zeros(H) for k in 'zrh'}


def gru_step(x, h):
    z = sigmoid(x @ W['z'] + h @ U['z'] + b['z'])            # update gate: how much to change
    r = sigmoid(x @ W['r'] + h @ U['r'] + b['r'])            # reset gate: how much past to use
    h_new = np.tanh(x @ W['h'] + (r * h) @ U['h'] + b['h'])  # candidate state
    return (1 - z) * h + z * h_new, z


h = np.zeros(H)
for t, x in enumerate(rng.normal(size=(4, n_in)), start=1):
    h, z = gru_step(x, h)
    print(f't={t}: update gate {np.round(z, 2)}, h = {np.round(h, 3)}')

# if the update gate is pushed towards 0, the state is copied forward almost unchanged
b['z'][:] = -6
h0 = np.array([0.5, -0.5, 0.2, 0.9])
h = h0.copy()
for x in rng.normal(size=(50, n_in)):
    h, _ = gru_step(x, h)
print('update gate near 0 for 50 steps: start', h0, 'end', np.round(h, 2))


def n_weights(cell, n_in, H):
    gates = {'RNN': 1, 'GRU': 3, 'LSTM': 4}[cell]
    return gates * (n_in * H + H * H + H)


for cell in ['RNN', 'GRU', 'LSTM']:
    print(f'{cell:4s} layer, 100 inputs, 128 hidden units: {n_weights(cell, 100, 128):,} weights')
