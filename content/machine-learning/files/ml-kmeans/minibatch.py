# 1.1 k-means: grouping points around centres
# Example "minibatch" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.datasets import make_blobs

X, _ = make_blobs(n_samples=20000, centers=5, cluster_std=1.0, random_state=1)
full = KMeans(n_clusters=5, n_init=3, random_state=0).fit(X)
mini = MiniBatchKMeans(n_clusters=5, batch_size=1024, n_init=3, random_state=0).fit(X)
print("KMeans inertia:         ", round(float(full.inertia_)))
print("MiniBatchKMeans inertia:", round(float(mini.inertia_)))
print("difference:", round(100 * (mini.inertia_ - full.inertia_) / full.inertia_, 2), "%")
