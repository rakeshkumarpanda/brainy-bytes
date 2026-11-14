# 1.2 Hierarchical clustering and DBSCAN
# Example "scipy_tree" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster

x = np.array([[1.0], [2.0], [6.0], [7.0], [15.0], [18.0]])
Z = linkage(x, method="single")
print("each row: cluster a, cluster b, merge distance, size")
for row in Z:
    print([int(row[0]), int(row[1]), float(row[2]), int(row[3])])
print("cut the tree at height 3.5:", fcluster(Z, t=3.5, criterion="distance").tolist())
print("ask for exactly 2 clusters:", fcluster(Z, t=2, criterion="maxclust").tolist())
