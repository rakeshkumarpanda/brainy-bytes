# 3.1 Function approximation and deep Q networks
# Example "dqn_cartpole" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# CartPole: keep a pole balanced on a cart by pushing left or right. +1 reward per step, at most 200 steps.
# The physics follows the classic Barto, Sutton and Anderson (1983) task used by OpenAI Gym.
def cart_step(s, a):
    x, v, th, om = s
    force = 10.0 if a == 1 else -10.0
    cos, sin = np.cos(th), np.sin(th)
    tmp = (force + 0.05 * om * om * sin) / 1.1
    alpha = (9.8 * sin - cos * tmp) / (0.5 * (4 / 3 - 0.1 * cos * cos / 1.1))
    acc = tmp - 0.05 * alpha * cos / 1.1
    s = np.array([x + 0.02 * v, v + 0.02 * acc, th + 0.02 * om, om + 0.02 * alpha])
    return s, abs(s[0]) > 2.4 or abs(s[2]) > 0.2095     # fails if the cart leaves the track or the pole tilts past 12 degrees

# A small network: 4 inputs, 32 hidden units with ReLU, 2 outputs (one Q value per action).
def init(rng):
    return [rng.normal(0, 0.5, (4, 32)), np.zeros(32), rng.normal(0, 0.1, (32, 2)), np.zeros(2)]

SCALE = np.array([2.4, 3.0, 0.21, 3.0])                  # bring every input to roughly -1..1

def forward(p, X):
    h = np.maximum(0, (X / SCALE) @ p[0] + p[1])
    return h @ p[2] + p[3], h

def train_step(p, X, A, Y, lr, opt):
    q, h = forward(p, X)
    err = np.zeros_like(q)
    rows = np.arange(len(A))
    err[rows, A] = q[rows, A] - Y                         # only the action taken has a target
    err = np.clip(err, -1, 1) / len(A)                   # clipping the error is the Huber loss trick from DQN
    dh = (err @ p[2].T) * (h > 0)
    grads = [(X / SCALE).T @ dh, dh.sum(0), h.T @ err, err.sum(0)]
    opt["t"] += 1
    for k, (w, g) in enumerate(zip(p, grads)):           # Adam: a step size for each weight, from running averages of the gradient
        opt["m"][k] = 0.9 * opt["m"][k] + 0.1 * g
        opt["v"][k] = 0.999 * opt["v"][k] + 0.001 * g * g
        m_hat = opt["m"][k] / (1 - 0.9 ** opt["t"])
        v_hat = opt["v"][k] / (1 - 0.999 ** opt["t"])
        w -= lr * m_hat / (np.sqrt(v_hat) + 1e-8)

rng = np.random.default_rng(1)
online = init(rng)
opt = {"t": 0, "m": [np.zeros_like(w) for w in online], "v": [np.zeros_like(w) for w in online]}
target = [w.copy() for w in online]                       # the target network: a frozen copy, refreshed every 100 steps
buffer, CAP = [], 10000                                   # experience replay memory
gamma, lr, batch = 0.95, 0.003, 32
returns, steps = [], 0
for ep in range(150):
    s, total, done = rng.uniform(-0.05, 0.05, 4), 0, False
    while not done and total < 200:
        eps = max(0.05, 1 - ep / 60)                     # explore a lot at first, then less
        a = int(rng.integers(2)) if rng.random() < eps else int(np.argmax(forward(online, s[None])[0]))
        s2, done = cart_step(s, a)
        total += 1
        buffer.append((s, a, 1.0, s2, float(done)))
        if len(buffer) > CAP:
            buffer.pop(0)
        s = s2
        steps += 1
        if len(buffer) >= 200:
            idx = rng.integers(len(buffer), size=batch)   # a random minibatch breaks the link between neighbouring steps
            S, A, R, S2, D = (np.array(x) for x in zip(*[buffer[i] for i in idx]))
            Y = R + gamma * (1 - D) * forward(target, S2)[0].max(axis=1)
            train_step(online, S, A.astype(int), Y, lr, opt)
        if steps % 100 == 0:
            target = [w.copy() for w in online]
    returns.append(total)
for k in range(0, 150, 25):
    print(f"episodes {k + 1:3d} to {k + 25:3d}: average steps balanced {np.mean(returns[k:k + 25]):6.1f}")
print("total environment steps:", steps)

tests = []
for _ in range(10):                                       # test the greedy policy, with no exploring and no learning
    s, total, done = rng.uniform(-0.05, 0.05, 4), 0, False
    while not done and total < 200:
        s, done = cart_step(s, int(np.argmax(forward(online, s[None])[0])))
        total += 1
    tests.append(total)
print("greedy test episodes (200 is the maximum):", tests)
