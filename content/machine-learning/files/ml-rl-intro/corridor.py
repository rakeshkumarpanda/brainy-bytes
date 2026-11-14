# 1.1 Agents, rewards and returns
# Example "corridor" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import random

class Corridor:
    """Cells 0 to 5. Start in cell 2. Cell 5 holds treasure (+10), cell 0 a pit (-10). Each move costs 1."""
    def reset(self):
        self.pos = 2
        return self.pos

    def step(self, action):                              # action: -1 = left, +1 = right
        self.pos += action
        if self.pos == 5:
            return self.pos, 10, True                    # new state, reward, episode over
        if self.pos == 0:
            return self.pos, -10, True
        return self.pos, -1, False

random.seed(23)
env = Corridor()
state, done, total, t = env.reset(), False, 0, 0
while not done:
    action = random.choice([-1, 1])                      # a random policy
    new_state, reward, done = env.step(action)
    t += 1
    print("t", t, " state", state, " action", "right" if action == 1 else "left ", " reward", str(reward).rjust(3), " next", new_state)
    state, total = new_state, total + reward
print("episode over after", t, "steps, total reward", total)
