# 1.2 Hierarchical clustering and DBSCAN
# Example "dbscan_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

X = np.array([[1, 1], [1.5, 1], [1, 1.5], [1.5, 1.5], [2, 1.2],
              [6, 6], [6.5, 6], [6, 6.5], [6.4, 6.6],
              [4, 9], [9, 1]])
eps, min_pts = 0.8, 3
n = len(X)
near = [[j for j in range(n) if np.linalg.norm(X[i] - X[j]) <= eps] for i in range(n)]
core = [len(near[i]) >= min_pts for i in range(n)]       # neighbours include the point itself
print("core points:", [i for i in range(n) if core[i]])

label = [-1] * n
cluster = 0
for i in range(n):
    if not core[i] or label[i] != -1:
        continue
    label[i] = cluster
    queue = [i]
    while queue:                                         # grow the cluster through core points
        p = queue.pop()
        for q in near[p]:
            if label[q] == -1:
                label[q] = cluster
                if core[q]:
                    queue.append(q)
    cluster = cluster + 1
print("labels:", label)
print("clusters found:", cluster, " noise points:", [i for i in range(n) if label[i] == -1])
