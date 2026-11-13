# 1.1 k-means: grouping points around centres
# Example "init_matters" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

X, _ = make_blobs(n_samples=500, centers=8, cluster_std=0.6, random_state=5)
for init in ["random", "k-means++"]:
    results = [round(float(KMeans(n_clusters=8, init=init, n_init=1, random_state=s).fit(X).inertia_)) for s in range(6)]
    print(init.ljust(9), "inertia over 6 starts:", results)
best = KMeans(n_clusters=8, n_init=10, random_state=0).fit(X)
print("k-means++ with n_init=10 keeps the best:", round(float(best.inertia_)))
