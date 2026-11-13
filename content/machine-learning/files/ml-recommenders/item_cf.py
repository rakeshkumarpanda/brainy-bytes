# 3.3 Recommender systems
# Example "item_cf" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

R = np.array([[5, 4, 0, 1, 0],
              [4, 5, 1, 0, 1],
              [1, 0, 5, 4, 5],
              [0, 1, 4, 5, 4],
              [5, 5, 0, 2, 1]], dtype=float)
films = ["Space Race", "Star Siege", "Haunted Inn", "Ghost Camp", "Night Fog"]
norms = np.linalg.norm(R, axis=0)
S = (R.T @ R) / np.outer(norms, norms)                   # cosine similarity between film columns
np.fill_diagonal(S, 0)
for i, f in enumerate(films):
    j = int(np.argmax(S[i]))
    print(f.ljust(11), " most similar:", films[j].ljust(11), " cosine", round(float(S[i, j]), 3))
user = 0
seen = R[user] > 0
for i in np.where(~seen)[0]:
    w = S[i, seen]                                       # how close this film is to each film the user rated
    score = w @ R[user, seen] / w.sum()                  # weighted average of the user's own ratings
    print("for user 0, unseen", films[i].ljust(11), " predicted", round(float(score), 2))
