# 2.3 SARSA and Q learning
# Example "compare_control" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Cliff walking (Sutton and Barto example 6.6): a 4 x 12 grid. Start bottom left, goal bottom right.
# The cells between them on the bottom row are a cliff: stepping in costs -100 and sends you back to the start.
# Every other move costs -1. Actions: 0 up, 1 down, 2 left, 3 right.
ROWS, COLS = 4, 12
START, GOAL = (3, 0), (3, 11)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def step(state, a):
    r, c = state[0] + MOVES[a][0], state[1] + MOVES[a][1]
    r, c = min(max(r, 0), ROWS - 1), min(max(c, 0), COLS - 1)
    if r == 3 and 1 <= c <= 10:
        return START, -100, False                        # fell off the cliff
    return (r, c), -1, (r, c) == GOAL

def eps_greedy(Q, s, eps, rng):
    if rng.random() < eps:
        return int(rng.integers(4))
    q = Q[s]
    return int(rng.choice(np.flatnonzero(q == q.max())))  # break ties at random

def run(method, episodes=200, alpha=0.5, eps=0.1, seed=0):
    rng = np.random.default_rng(seed)
    Q = np.zeros((ROWS, COLS, 4))
    totals = []
    for ep in range(episodes):
        s, done, total = START, False, 0
        a = eps_greedy(Q, s, eps, rng)
        while not done:
            s2, r, done = step(s, a)
            a2 = eps_greedy(Q, s2, eps, rng)
            if done:
                nxt = 0.0
            elif method == "Q learning":
                nxt = Q[s2].max()
            elif method == "SARSA":
                nxt = Q[s2][a2]
            else:                                        # expected SARSA: average over the epsilon greedy choice
                probs = np.full(4, eps / 4)
                probs[np.argmax(Q[s2])] += 1 - eps
                nxt = probs @ Q[s2]
            Q[s][a] += alpha * (r + nxt - Q[s][a])
            s, a, total = s2, a2, total + r
        totals.append(total)
    return np.mean(totals[-100:])

for method in ["Q learning", "SARSA", "Expected SARSA"]:
    scores = [run(method, seed=k) for k in range(5)]
    print(method.ljust(15), " average reward per episode while learning (last 100 of 200, 5 runs):", round(float(np.mean(scores)), 1))
