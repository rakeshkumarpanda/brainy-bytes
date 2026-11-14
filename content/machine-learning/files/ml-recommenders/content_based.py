# 3.3 Recommender systems
# Example "content_based" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

films = ["Space Race", "Robot Love", "Haunted Inn", "Laugh Lab", "Star Siege", "Ghost Camp"]
#                  sci-fi romance horror comedy action
features = np.array([[1, 0, 0, 0, 1],
                     [1, 1, 0, 0, 0],
                     [0, 0, 1, 0, 0],
                     [0, 0, 0, 1, 0],
                     [1, 0, 0, 0, 1],
                     [0, 0, 1, 1, 0]], dtype=float)
liked = [0, 1]                                           # the user liked Space Race and Robot Love
profile = features[liked].mean(axis=0)                   # the user's taste as a mix of features
cos = features @ profile / (np.linalg.norm(features, axis=1) * np.linalg.norm(profile))
order = [i for i in np.argsort(-cos, kind="stable") if i not in liked]
print("taste profile:", profile.tolist())
for i in order:
    print(films[i].ljust(11), " cosine similarity", round(float(cos[i]), 3))
