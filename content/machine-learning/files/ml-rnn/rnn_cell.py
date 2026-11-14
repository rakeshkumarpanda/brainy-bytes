# 2.2 Recurrent networks, LSTM and GRU
# Example "rnn_cell" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A recurrent neural network cell, unrolled by hand over a short sequence.
import numpy as np

rng = np.random.default_rng(0)
n_in, n_hidden = 3, 4
W_xh = rng.normal(scale=0.5, size=(n_in, n_hidden))     # input to hidden
W_hh = rng.normal(scale=0.5, size=(n_hidden, n_hidden)) # hidden to hidden: the memory
b_h = np.zeros(n_hidden)

sequence = rng.normal(size=(5, n_in))                    # 5 time steps, 3 features each
h = np.zeros(n_hidden)
for t, x in enumerate(sequence, start=1):
    h = np.tanh(x @ W_xh + h @ W_hh + b_h)               # the same weights at every step
    print(f't={t}: h = {np.round(h, 3)}')

# the same cell handles a sequence of any length
long = rng.normal(size=(100, n_in))
h = np.zeros(n_hidden)
for x in long:
    h = np.tanh(x @ W_xh + h @ W_hh + b_h)
print('after 100 steps the state is still 4 numbers:', np.round(h, 3))

# how much does the state at step 100 depend on the input at step t?
# backpropagate d h_100 / d h_t through the tanh and W_hh at every step
hs = [np.zeros(n_hidden)]
for x in long:
    hs.append(np.tanh(x @ W_xh + hs[-1] @ W_hh + b_h))
J = np.eye(n_hidden)
for t in range(100, 0, -1):
    J = J @ (np.diag(1 - hs[t] ** 2) @ W_hh.T)          # chain rule: one more step back
    if 100 - t + 1 in (1, 5, 10, 20, 50):
        print(f'size of d h_100 / d h_{t - 1}: {np.linalg.norm(J):.2e}')
