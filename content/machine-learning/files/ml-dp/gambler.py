# 2.1 Dynamic programming: policy and value iteration
# Example "gambler" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Sutton and Barto example 4.3: bet part of your money on coin flips until you reach 100 or lose it all.
# Heads (chance 0.4) wins the stake, tails loses it. Reward 1 only for reaching 100.
p_heads, goal = 0.4, 100
V = np.zeros(goal + 1)
V[goal] = 1.0                                            # reaching the goal is worth 1
for sweep in range(1, 1000):
    delta = 0.0
    for s in range(1, goal):
        stakes = range(1, min(s, goal - s) + 1)
        best = max(p_heads * V[s + b] + (1 - p_heads) * V[s - b] for b in stakes)
        delta, V[s] = max(delta, abs(best - V[s])), best
    if delta < 1e-10:
        break
print("value iteration converged after", sweep, "sweeps")
for s in [10, 25, 40, 50, 60, 75, 90]:
    stakes = list(range(1, min(s, goal - s) + 1))
    q = np.round([p_heads * V[s + b] + (1 - p_heads) * V[s - b] for b in stakes], 9)
    print("capital", str(s).rjust(2), " chance of winning", round(V[s], 4), " best stake", stakes[int(np.argmax(q))])
