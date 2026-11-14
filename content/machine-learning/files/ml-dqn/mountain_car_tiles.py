# 3.1 Function approximation and deep Q networks
# Example "mountain_car_tiles" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Sutton and Barto example 10.1: an underpowered car must reach the top of a hill (position 0.5).
# State: position in [-1.2, 0.5] and velocity in [-0.07, 0.07], both continuous, so no table can list every state.
# Actions: push left, do nothing, push right. Every step costs -1 until the car reaches the top.
def step(pos, vel, a):
    vel = np.clip(vel + 0.001 * (a - 1) - 0.0025 * np.cos(3 * pos), -0.07, 0.07)
    pos = pos + vel
    if pos < -1.2:
        pos, vel = -1.2, 0.0                              # hitting the left wall stops the car
    return pos, vel, pos >= 0.5

# Tile coding: 8 grids of 8 by 8 tiles, each shifted a little. A state switches on exactly one tile in each grid.
TILINGS, SIZE = 8, 8

def active_tiles(pos, vel):
    x = (pos + 1.2) / 1.7 * SIZE                         # scale both numbers to the range 0..8
    y = (vel + 0.07) / 0.14 * SIZE
    tiles = []
    for t in range(TILINGS):
        dx, dy = t / TILINGS, (3 * t / TILINGS) % 1       # grid t is shifted by a different fraction of a tile in each direction
        i, j = int(x + dx), int(y + dy)                   # 0..8, so each grid has 9 by 9 tiles to cover the shift
        tiles.append(t * (SIZE + 1) ** 2 + i * (SIZE + 1) + j)
    return tiles

w = np.zeros((3, TILINGS * (SIZE + 1) ** 2))              # one weight vector per action
q = lambda tiles: w[:, tiles].sum(axis=1)                 # Q(s, a) = sum of the weights of the active tiles
alpha, gamma = 0.5 / TILINGS, 1.0
rng = np.random.default_rng(0)
lengths = []
for ep in range(60):
    pos, vel = rng.uniform(-0.6, -0.4), 0.0
    tiles = active_tiles(pos, vel)
    a = int(np.argmax(q(tiles)))                         # greedy: starting all weights at 0 is optimistic, so it explores
    for t in range(1, 5001):
        pos, vel, done = step(pos, vel, a)
        if done:
            w[a, tiles] += alpha * (-1 - q(tiles)[a])     # semi gradient SARSA, terminal target is just the reward
            break
        tiles2 = active_tiles(pos, vel)
        a2 = int(np.argmax(q(tiles2)))
        target = -1 + gamma * q(tiles2)[a2]
        w[a, tiles] += alpha * (target - q(tiles)[a])     # the gradient is 1 for each active tile, 0 elsewhere
        tiles, a = tiles2, a2
    lengths.append(t)
print("steps to reach the top in episodes 1 to 10:", lengths[:10])
print("average steps in episodes 51 to 60:", np.mean(lengths[50:]).round(1))
print("weights:", w.size, " active tiles per state:", TILINGS)
