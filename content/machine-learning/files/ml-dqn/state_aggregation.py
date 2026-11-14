# 3.1 Function approximation and deep Q networks
# Example "state_aggregation" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Sutton and Barto example 9.1: a random walk over 1000 states, starting in the middle (state 500).
# Each step jumps 1 to 100 states left or right at random. Falling off the left end gives -1, the right end +1.
# A table would need 1000 numbers. State aggregation uses only 10: one shared value per group of 100 states.
N, JUMP, GROUPS = 1000, 100, 10

def true_values():
    v = np.zeros(N)
    for _ in range(5000):                                 # dynamic programming, as in chapter 2.1, done with whole arrays
        padded = np.concatenate([-np.ones(JUMP), v, np.ones(JUMP)])   # jumping past an end counts as that end
        c = np.concatenate([[0], np.cumsum(padded)])
        idx = np.arange(N) + JUMP
        left = c[idx] - c[idx - JUMP]                     # sum of the 100 values just to the left
        right = c[idx + JUMP + 1] - c[idx + 1]            # sum of the 100 values just to the right
        new = (left + right) / (2 * JUMP)
        if np.abs(new - v).max() < 1e-7:
            break
        v = new
    return v

def episode(rng):
    s, states = 500, []
    while 1 <= s <= N:
        states.append(s)
        s += int(rng.integers(1, JUMP + 1)) * (1 if rng.random() < 0.5 else -1)
    return states, (1 if s > N else -1)

def group(s):
    return (s - 1) * GROUPS // N                          # states 1..100 share group 0, and so on

def gradient_mc(episodes, rng):
    w, visits = np.zeros(GROUPS), np.zeros(GROUPS)
    for _ in range(episodes):
        states, G = episode(rng)                          # no discount, reward only at the end, so G is the same for every state
        for s in states:
            g = group(s)
            visits[g] += 1
            w[g] += (G - w[g]) / visits[g]                # step size 1/n: the gradient of a one hot feature is 1 for its own group
    return w

def semi_gradient_td(episodes, alpha, rng):
    w = np.zeros(GROUPS)
    for _ in range(episodes):
        states, G = episode(rng)
        for i, s in enumerate(states):
            target = w[group(states[i + 1])] if i + 1 < len(states) else G
            w[group(s)] += alpha * (target - w[group(s)])  # the target uses w itself, but we do not differentiate it
    return w

v = true_values()
rng = np.random.default_rng(0)
w_mc = gradient_mc(2000, rng)
w_td = semi_gradient_td(2000, 0.01, rng)
truth = [v[g * 100:(g + 1) * 100].mean() for g in range(GROUPS)]
print("group   true average   gradient MC   semi gradient TD")
for g in range(GROUPS):
    print(f"{g * 100 + 1:4d}-{(g + 1) * 100:<4d}   {truth[g]:9.3f}   {w_mc[g]:11.3f}   {w_td[g]:14.3f}")
err = lambda w: np.sqrt(np.mean((np.repeat(w, 100) - v) ** 2))
print("root mean squared error over all 1000 states: MC", round(err(w_mc), 3), " TD", round(err(w_td), 3))
print("10 weights stand in for 1000 values. The values inside a group are forced to be equal, so some error always remains.")
