# 3.3 RL in practice: models, offline data and RLHF
# Example "dyna_maze" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import random

# Dyna-Q on the maze of Sutton and Barto example 8.1: 6 rows by 9 columns, walls marked #, start S, goal G.
# Reward 1 for reaching G, 0 otherwise, gamma = 0.95. Planning replays remembered transitions from a learned model.
MAZE = ["       #G",
        "  #    # ",
        "S #    # ",
        "  #      ",
        "     #   ",
        "         "]
ROWS, COLS = len(MAZE), len(MAZE[0])
START, GOAL = (2, 0), (0, 8)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def step(s, a):
    r, c = s[0] + MOVES[a][0], s[1] + MOVES[a][1]
    if not (0 <= r < ROWS and 0 <= c < COLS) or MAZE[r][c] == "#":
        r, c = s                                          # bump into a wall or the edge: stay put
    return (r, c), (1.0 if (r, c) == GOAL else 0.0)

def dyna_q(n_planning, episodes=30, alpha=0.1, gamma=0.95, eps=0.1, seed=0):
    rnd = random.Random(seed)
    Q, model, lengths = {}, {}, []
    q = lambda s: Q.setdefault(s, [0.0] * 4)
    def greedy(s):
        vals = q(s)
        best = max(vals)
        return rnd.choice([a for a in range(4) if vals[a] == best])
    for _ in range(episodes):
        s, t = START, 0
        while s != GOAL:
            a = rnd.randrange(4) if rnd.random() < eps else greedy(s)
            s2, r = step(s, a)
            target = r + (0 if s2 == GOAL else gamma * max(q(s2)))
            q(s)[a] += alpha * (target - q(s)[a])         # (a) direct RL: Q learning from the real step
            model[(s, a)] = (s2, r)                       # (b) model learning: remember what happened
            keys = list(model)
            for _ in range(n_planning):                   # (c) planning: replay random remembered steps
                ps, pa = rnd.choice(keys)
                ps2, pr = model[(ps, pa)]
                pt = pr + (0 if ps2 == GOAL else gamma * max(q(ps2)))
                q(ps)[pa] += alpha * (pt - q(ps)[pa])
            s, t = s2, t + 1
        lengths.append(t)
    return lengths

print("shortest path: 14 steps")
for n in [0, 5, 50]:
    runs = [dyna_q(n, seed=k) for k in range(5)]
    avg = [sum(r[i] for r in runs) / len(runs) for i in range(30)]
    print(f"planning steps n = {n:2d}: episode 1 {avg[0]:6.1f}, episode 2 {avg[1]:6.1f}, episode 5 {avg[4]:6.1f}, episodes 26 to 30 {sum(avg[25:]) / 5:5.1f}")
