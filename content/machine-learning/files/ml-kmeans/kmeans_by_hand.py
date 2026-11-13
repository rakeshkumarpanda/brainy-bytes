# 1.1 k-means: grouping points around centres
# Example "kmeans_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

X = np.array([[1, 1], [1.5, 2], [2, 1], [6, 6], [7, 6.5], [6.5, 7], [1, 7], [2, 6.5], [1.5, 7.5]])
centres = X[[0, 1, 2]].astype(float)                 # a poor start: three points from the same group

for step in range(1, 5):
    dist = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)     # squared distance to each centre
    labels = dist.argmin(axis=1)                                        # assign: nearest centre
    inertia = dist.min(axis=1).sum()
    print("step", step, " labels", labels.tolist(), " inertia", round(float(inertia), 2))
    centres = np.array([X[labels == k].mean(axis=0) for k in range(3)])  # update: mean of each group
    print("   new centres", np.round(centres, 2).tolist())
