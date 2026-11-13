# 2.3 SARSA and Q learning
# Example "double_q" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Sutton and Barto example 6.7. From A, "right" ends the episode with reward 0. "left" moves to B with reward 0,
# and every one of B's 10 actions ends the episode with a reward drawn from a normal curve with mean -0.1.
# So going left is a bad idea on average, but the max over noisy estimates of B's actions looks positive.
def run(double, episodes=300, alpha=0.1, eps=0.1, seed=0):
    rng = np.random.default_rng(seed)
    QA = [np.zeros(2), np.zeros(2)]                       # two tables for double Q learning (A: 0 left, 1 right)
    QB = [np.zeros(10), np.zeros(10)]
    lefts = []
    for ep in range(episodes):
        qa = QA[0] + QA[1] if double else QA[0]
        a = int(rng.integers(2)) if rng.random() < eps else int(rng.choice(np.flatnonzero(qa == qa.max())))
        lefts.append(a == 0)
        if a == 1:
            i = int(rng.integers(2)) if double else 0
            QA[i][1] += alpha * (0 - QA[i][1])
            continue
        i = int(rng.integers(2)) if double else 0           # update table i, using the other table to judge its best action
        j = 1 - i if double else 0
        best_b = int(np.argmax(QB[i]))
        QA[i][0] += alpha * (0 + QB[j][best_b] - QA[i][0])
        qb = QB[0] + QB[1] if double else QB[0]
        b = int(rng.integers(10)) if rng.random() < eps else int(np.argmax(qb))
        r = rng.normal(-0.1, 1.0)
        k = int(rng.integers(2)) if double else 0
        QB[k][b] += alpha * (r - QB[k][b])
    return np.array(lefts)

for double in [False, True]:
    lefts = np.mean([run(double, seed=s) for s in range(100)], axis=0)
    name = "Double Q learning" if double else "Q learning"
    print(name.ljust(18), " share of episodes going left at episodes 10, 50, 300:", lefts[9].round(2), lefts[49].round(2), lefts[299].round(2))
print("the best possible share is 0.05 (only the random epsilon moves go left)")
