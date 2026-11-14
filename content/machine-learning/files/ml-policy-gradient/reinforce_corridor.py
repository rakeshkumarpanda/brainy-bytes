# 3.2 Policy gradients, actor critic and PPO
# Example "reinforce_corridor" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Sutton and Barto example 13.1: a short corridor with switched actions. Start in state 0, the goal is past state 2.
# In states 0 and 2, "right" moves right. In state 1 the actions are swapped: "right" moves left.
# The agent cannot tell the states apart (same features), so it must use one probability p of pressing "right" everywhere.
# Every step costs -1. A greedy, deterministic policy never finishes, but a stochastic one does.
def step(s, right):
    move = 1 if right else -1
    if s == 1:
        move = -move                                      # the switched state
    return max(0, s + move)

def true_value(p):                                        # solve the Bellman equations for the start value
    A = np.array([[p, -p, 0], [-p, 1, -(1 - p)], [0, -(1 - p), 1]])
    return np.linalg.solve(A, -np.ones(3))[0]

ps = np.linspace(0.05, 0.95, 91)
best = ps[np.argmax([true_value(p) for p in ps])]
print("best p(right) =", round(best, 2), " start value =", round(true_value(best), 2))

rng = np.random.default_rng(0)
theta = np.array([0.0, 0.0])                              # preferences for [left, right], policy = softmax(theta)
alpha = 2 ** -9
history = []
for ep in range(1, 2001):
    probs = np.exp(theta - theta.max()) / np.exp(theta - theta.max()).sum()
    s, actions, rewards = 0, [], []
    while s != 3 and len(actions) < 500:
        a = int(rng.random() < probs[1])                  # 1 means "right"
        actions.append(a)
        rewards.append(-1)
        s = step(s, a)
    history.append(probs[1])
    G = np.cumsum(rewards[::-1])[::-1]                    # return from every time step to the end
    for a, g in zip(actions, G):
        grad_log = -probs.copy()
        grad_log[a] += 1                                  # gradient of log softmax: one hot(a) - probs
        theta += alpha * g * grad_log                     # REINFORCE: theta += alpha * G_t * grad log pi(a|s)
    if ep in (1, 100, 500, 1000, 2000):
        print(f"episode {ep:4d}: p(right) = {probs[1]:.3f}, steps this episode = {len(actions):3d}, true value of this policy = {true_value(probs[1]):.2f}")
print("average p(right) over the last 500 episodes:", round(float(np.mean(history[-500:])), 3), " (single episodes are noisy, so p wanders around the best value)")
