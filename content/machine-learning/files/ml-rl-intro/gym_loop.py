# 1.1 Agents, rewards and returns
# Example "gym_loop" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

class LineWorld:
    """A tiny environment with the same interface as Gymnasium: reset() and step() returning 5 values."""
    def __init__(self, size=7, max_steps=20):
        self.size, self.max_steps = size, max_steps
        self.rng = np.random.default_rng()

    def reset(self, seed=None):
        self.rng = np.random.default_rng(seed)
        self.pos, self.t = self.size // 2, 0
        return self.pos, {}                              # observation, info

    def step(self, action):                              # 0 = left, 1 = right
        self.pos = int(np.clip(self.pos + (1 if action == 1 else -1), 0, self.size - 1))
        self.t += 1
        terminated = self.pos == self.size - 1           # reached the goal: a real end
        truncated = self.t >= self.max_steps             # ran out of time: an artificial cut
        reward = 1.0 if terminated else -0.1
        return self.pos, reward, terminated, truncated, {}

env = LineWorld()
obs, info = env.reset(seed=42)
total, done = 0.0, False
while not done:
    action = int(env.rng.random() < 0.6)                 # lean right 60% of the time
    obs, reward, terminated, truncated, info = env.step(action)
    total += reward
    done = terminated or truncated
print("finished at step", env.t, " position", obs, " terminated", terminated, " truncated", truncated, " total", round(total, 2))
