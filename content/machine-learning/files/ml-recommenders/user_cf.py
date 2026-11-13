# 3.3 Recommender systems
# Example "user_cf" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Ratings 1 to 5, 0 = not rated. Rows are users, columns are films.
R = np.array([[5, 4, 0, 1, 0],
              [4, 5, 1, 0, 1],
              [1, 0, 5, 4, 5],
              [0, 1, 4, 5, 4],
              [5, 5, 0, 2, 1]], dtype=float)
rated = R > 0
means = np.array([R[u, rated[u]].mean() for u in range(len(R))])
C = np.where(rated, R - means[:, None], 0.0)             # centre each user so harsh and generous raters compare fairly

def sim(a, b):
    both = rated[a] & rated[b]
    x, y = C[a, both], C[b, both]
    return float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-9))

user, film = 0, 2                                        # predict user 0's rating of film 2
others = [v for v in range(len(R)) if v != user and rated[v, film]]
sims = {v: round(sim(user, v), 3) for v in others}
print("similarity of user 0 to users who rated film 2:", sims)
top = sorted(others, key=lambda v: -sims[v])[:2]         # the 2 most similar users
pred = means[user] + sum(sims[v] * C[v, film] for v in top) / sum(abs(sims[v]) for v in top)
print("neighbours used:", top, " predicted rating:", round(float(pred), 2), " (user 0's average is", round(float(means[user]), 2), ")")
