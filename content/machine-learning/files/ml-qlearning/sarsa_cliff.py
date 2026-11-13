# 2.3 SARSA and Q learning
# Example "sarsa_cliff" from the lesson.
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

def greedy_path(Q):
    s, path = START, [START]
    for _ in range(50):
        s, _, done = step(s, int(np.argmax(Q[s])))
        path.append(s)
        if done:
            break
    rows = [["." for _ in range(COLS)] for _ in range(ROWS)]
    for c in range(1, 11):
        rows[3][c] = "C"
    for (r, c) in path:
        rows[r][c] = "o"
    return "\n".join("".join(row) for row in rows)

rng = np.random.default_rng(0)
Q = np.zeros((ROWS, COLS, 4))
alpha, gamma, eps = 0.5, 1.0, 0.1
totals = []
for ep in range(500):
    s, done, total = START, False, 0
    a = eps_greedy(Q, s, eps, rng)
    while not done:
        s2, r, done = step(s, a)
        a2 = eps_greedy(Q, s2, eps, rng)                  # SARSA: pick the next action first
        target = r + (0 if done else gamma * Q[s2][a2])   # and learn from the action it will really take
        Q[s][a] += alpha * (target - Q[s][a])
        s, a, total = s2, a2, total + r
    totals.append(total)
print("SARSA, average reward per episode over the last 100:", np.mean(totals[-100:]))
print("greedy path (o) after learning, C = cliff:")
print(greedy_path(Q))
