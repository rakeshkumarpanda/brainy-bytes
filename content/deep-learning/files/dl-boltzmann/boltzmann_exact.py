# 3.4 Energy based models: Hopfield networks, Boltzmann machines and RBMs
# Example "boltzmann_exact" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A tiny Boltzmann machine with 3 binary units: the exact probability of every state, and Gibbs sampling.
import itertools

import numpy as np

W = np.array([[0.0, 2.0, -1.0],
              [2.0, 0.0, 1.0],
              [-1.0, 1.0, 0.0]])                                    # symmetric weights, zero diagonal
b = np.array([-1.0, -0.5, 0.5])                                     # biases


def energy(s):
    return -0.5 * s @ W @ s - b @ s


states = np.array(list(itertools.product([0, 1], repeat=3)))       # all 2^3 = 8 states
for T in [1.0, 0.5, 4.0]:                                          # temperature
    weights = np.exp(-np.array([energy(s) for s in states]) / T)    # Boltzmann factor e^(-E/T)
    Z = weights.sum()                                               # partition function: the sum over every state
    p = weights / Z
    print(f'T = {T}: Z = {Z:.3f}, lowest energy states p = {p.max():.3f} each, highest energy state p = {p.min():.3f}')
    if T == 1.0:
        p_exact = p
        for s, e, q in zip(states, [energy(s) for s in states], p):
            print(f'   state {s}  energy {e:5.2f}  p {q:.3f}')

# Gibbs sampling: update one unit at a time from p(s_i = 1 | others) = sigmoid(sum_j w_ij s_j + b_i)
rng = np.random.default_rng(0)
s = np.zeros(3)
counts = np.zeros(8)
for step in range(60_000):
    i = step % 3
    s[i] = rng.random() < 1 / (1 + np.exp(-(W[i] @ s + b[i])))
    if step >= 3000:                                                # skip the burn in
        counts[int(s[0] * 4 + s[1] * 2 + s[2])] += 1
freq = counts / counts.sum()
print('Gibbs frequencies at T = 1:', np.round(freq, 3))
print('largest gap to the exact p:', round(float(np.abs(freq - p_exact).max()), 3))
