# 1.1 k-means: grouping points around centres
# Example "choose_k" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score

X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.9, random_state=2)
for k in range(2, 8):
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
    print("k", k, " inertia", str(round(float(km.inertia_))).rjust(5), " silhouette", round(float(silhouette_score(X, km.labels_)), 3))
