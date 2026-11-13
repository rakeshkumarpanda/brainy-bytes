# 3.3 Recommender systems
# Example "cold_start" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

R = np.array([[5, 4, 0, 1, 0],
              [4, 5, 1, 0, 1],
              [1, 0, 5, 4, 5],
              [0, 1, 4, 5, 4],
              [5, 5, 0, 2, 1]], dtype=float)
films = ["Space Race", "Star Siege", "Haunted Inn", "Ghost Camp", "Night Fog"]
count = (R > 0).sum(axis=0)
mean = R.sum(axis=0) / count
m, C = 3, float(R[R > 0].mean())                          # shrink films with few ratings towards the overall mean
score = (count * mean + m * C) / (count + m)
for i in np.argsort(-score, kind="stable"):
    print(films[i].ljust(11), " ratings", int(count[i]), " average", round(float(mean[i]), 2), " shrunk score", round(float(score[i]), 2))
print("a brand new user with no ratings gets this popularity list first")
