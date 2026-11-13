# 1.1 k-means: grouping points around centres
# Example "sklearn_kmeans" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

X, true = make_blobs(n_samples=300, centers=4, cluster_std=0.9, random_state=2)
km = KMeans(n_clusters=4, n_init=10, random_state=0).fit(X)
print("points per cluster:", np.bincount(km.labels_).tolist())
print("centres:", np.round(km.cluster_centers_, 2).tolist())
print("inertia (sum of squared distances):", round(float(km.inertia_), 1))
print("new point [0, 0] goes to cluster", int(km.predict([[0, 0]])[0]))
