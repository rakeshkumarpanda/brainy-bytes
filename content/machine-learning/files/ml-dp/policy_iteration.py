# 2.1 Dynamic programming: policy and value iteration
# Example "policy_iteration" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# The 4 x 4 FrozenLake map from Gymnasium: S start, F frozen, H hole, G goal. The ice is slippery:
# the agent moves the way it chose with chance 1/3, and to each side of it with chance 1/3.
MAP = "SFFF" "FHFH" "FFFH" "HFFG"
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]                # left, down, right, up (Gymnasium order)

def model():
    P = {}
    for s in range(16):
        for a in range(4):
            P[s, a] = []
            if MAP[s] in "HG":
                P[s, a].append((1.0, s, 0.0, True))
                continue
            for b in (a - 1, a, a + 1):
                r, c = divmod(s, 4)
                dr, dc = DIRS[b % 4]
                r, c = min(max(r + dr, 0), 3), min(max(c + dc, 0), 3)
                s2 = 4 * r + c
                P[s, a].append((1 / 3, s2, 1.0 if MAP[s2] == "G" else 0.0, MAP[s2] in "HG"))
    return P

gamma, ARROWS = 0.99, "<v>^"

def evaluate(policy, theta=1e-8):
    V = np.zeros(16)
    while True:
        delta = 0.0
        for s in range(16):
            v = sum(p * (r + gamma * V[s2] * (not done)) for p, s2, r, done in P[s, policy[s]])
            delta, V[s] = max(delta, abs(v - V[s])), v      # update in place
        if delta < theta:
            return V

def q_values(V, s):
    return [sum(p * (r + gamma * V[s2] * (not done)) for p, s2, r, done in P[s, a]) for a in range(4)]

P = model()
policy = [0] * 16                                        # start: always go left
for it in range(1, 20):
    V = evaluate(policy)                                 # 1. policy evaluation
    new = [int(np.argmax(np.round(q_values(V, s), 10))) for s in range(16)]   # 2. greedy improvement
    print("iteration", it, " value of the start", round(V[0], 3), " policy", "".join(ARROWS[a] if MAP[s] in "SF" else MAP[s] for s, a in enumerate(policy)))
    if new == policy:
        print("policy is stable, so it is optimal")
        break
    policy = new
