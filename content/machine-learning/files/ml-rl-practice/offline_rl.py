# 3.3 RL in practice: models, offline data and RLHF
# Example "offline_rl" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Offline RL: learn only from a fixed log of past experience, with no new interaction.
# Gridworld 4 by 6: start bottom left, goal bottom right, -1 per move, a pit in the middle of the bottom row costs -50.
ROWS, COLS, START, GOAL, PITS = 4, 6, 18, 23, {20, 21}
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]               # up, down, left, right

def step(s, a):
    r, c = divmod(s, COLS)
    r = min(ROWS - 1, max(0, r + MOVES[a][0]))
    c = min(COLS - 1, max(0, c + MOVES[a][1]))
    s2 = r * COLS + c
    if s2 in PITS:
        return s2, -50.0, True
    return s2, -1.0, s2 == GOAL

# The log comes from a cautious behaviour policy: go up to row 1, walk right, come down. 30% of moves are random.
def behaviour(s, rng):
    if rng.random() < 0.3:
        return int(rng.integers(4))
    r, c = divmod(s, COLS)
    if c == COLS - 1:
        return 1                                          # last column: go down
    return 0 if r > 1 else 3                              # climb to row 1, then go right

rng = np.random.default_rng(0)
data = []
for _ in range(200):
    s = START
    for _ in range(100):
        a = behaviour(s, rng)
        s2, r, done = step(s, a)
        data.append((s, a, r, s2, done))
        s = s2
        if done:
            break
seen = {(s, a) for s, a, _, _, _ in data}
print("logged transitions:", len(data), " distinct state-action pairs seen:", len(seen), "of", ROWS * COLS * 4)

def fitted_q(penalty, sweeps=100, gamma=0.99):
    Q = np.zeros((ROWS * COLS, 4))
    for _ in range(sweeps):                               # repeated Q learning sweeps over the fixed log
        for s, a, r, s2, done in data:
            Q[s, a] += 0.1 * (r + (0 if done else gamma * Q[s2].max()) - Q[s, a])
        if penalty:                                       # conservative: push down actions the log never tried
            for s in range(ROWS * COLS):
                for a in range(4):
                    if (s, a) not in seen:
                        Q[s, a] = -100.0
    return Q

def evaluate(policy):
    s, total = START, 0.0
    for _ in range(50):
        s, r, done = step(s, policy(s))
        total += r
        if done:
            break
    return total

counts = np.zeros((ROWS * COLS, 4))
for s, a, _, _, _ in data:
    counts[s, a] += 1
results = {
    "behaviour cloning (copy the most common logged action)": lambda s: int(np.argmax(counts[s])),
    "naive offline Q learning                             ": lambda s, Q=fitted_q(False): int(np.argmax(Q[s])),
    "conservative offline Q learning                      ": lambda s, Q=fitted_q(True): int(np.argmax(Q[s])),
}
for name, pol in results.items():
    print(name, " return of its greedy policy:", evaluate(pol))
print("best possible return: -7 (up, five moves right, down)")
