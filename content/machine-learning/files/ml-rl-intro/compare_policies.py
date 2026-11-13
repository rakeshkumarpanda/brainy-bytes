# 1.1 Agents, rewards and returns
# Example "compare_policies" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import random

class Corridor:
    def reset(self):
        self.pos = 2
        return self.pos

    def step(self, action):
        self.pos += action
        if self.pos == 5:
            return self.pos, 10, True
        if self.pos == 0:
            return self.pos, -10, True
        return self.pos, -1, False

def run(policy, episodes=2000, max_steps=100):
    env, totals = Corridor(), []
    for _ in range(episodes):
        s, done, total, steps = env.reset(), False, 0, 0
        while not done and steps < max_steps:
            s, r, done = env.step(policy(s))
            total, steps = total + r, steps + 1
        totals.append(total)
    return sum(totals) / len(totals)

random.seed(0)
policies = {
    "random": lambda s: random.choice([-1, 1]),
    "always right": lambda s: 1,
    "always left": lambda s: -1,
    "right 80% of the time": lambda s: 1 if random.random() < 0.8 else -1,
}
for name, pi in policies.items():
    print(name.ljust(22), " average total reward", round(run(pi), 2))
