# 3.2 Policy gradients, actor critic and PPO
# Example "actor_critic_cliff" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# One step actor critic on the cliff walk from chapter 2.3 (4 by 12 grid, -1 per move, -100 and back to start for a fall).
# Actor: softmax preferences theta[s, a]. Critic: state values V[s]. The critic's TD error tells the actor how good the action was.
ROWS, COLS, START, GOAL = 4, 12, 36, 47
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]               # up, down, left, right

def step(s, a):
    r, c = divmod(s, COLS)
    r = min(ROWS - 1, max(0, r + MOVES[a][0]))
    c = min(COLS - 1, max(0, c + MOVES[a][1]))
    if r == ROWS - 1 and 1 <= c <= COLS - 2:
        return START, -100, False                         # fell off the cliff
    s2 = r * COLS + c
    return s2, -1, s2 == GOAL

rng = np.random.default_rng(0)
theta = np.zeros((ROWS * COLS, 4))
V = np.zeros(ROWS * COLS)
alpha_actor, alpha_critic = 0.1, 0.5
rewards = []
for ep in range(500):
    s, total = START, 0
    for t in range(1000):
        prefs = theta[s] - theta[s].max()
        pi = np.exp(prefs) / np.exp(prefs).sum()
        a = rng.choice(4, p=pi)
        s2, r, done = step(s, a)
        delta = r + (0 if done else V[s2]) - V[s]         # TD error: the advantage estimate
        V[s] += alpha_critic * delta                      # critic: TD(0)
        grad = -pi
        grad[a] += 1
        theta[s] += alpha_actor * delta * grad            # actor: policy gradient step with the TD error in place of G
        total += r
        s = s2
        if done:
            break
    rewards.append(total)

s, path = START, [START]
while s != GOAL and len(path) < 50:                       # follow the most likely action from each cell
    s = step(s, int(np.argmax(theta[s])))[0]
    path.append(s)
rows_used = sorted({p // COLS for p in path})
print("average reward per block of 100 episodes:", [round(float(np.mean(rewards[i:i + 100])), 1) for i in range(0, 500, 100)])
print("most likely path:", len(path) - 1, "moves, using rows", rows_used, "(row 3 is the bottom row with the cliff)")
