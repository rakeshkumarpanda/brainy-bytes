# 1.2 Hierarchical clustering and DBSCAN
# Example "sklearn_dbscan" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.datasets import make_moons
from sklearn.metrics import adjusted_rand_score

X, y = make_moons(n_samples=300, noise=0.06, random_state=1)
rng = np.random.default_rng(0)
X = np.vstack([X, rng.uniform(-1.5, 2.5, size=(15, 2))])   # add 15 random noise points
y = np.concatenate([y, -np.ones(15, dtype=int)])

db = DBSCAN(eps=0.2, min_samples=5).fit(X)
lab = db.labels_
print("clusters:", len(set(lab)) - (1 if -1 in lab else 0), " points marked noise:", int((lab == -1).sum()))
print("core points:", len(db.core_sample_indices_))
real = y != -1
print("DBSCAN ARI on the moons:", round(adjusted_rand_score(y[real], lab[real]), 3))
km = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(X)
print("k-means ARI on the moons:", round(adjusted_rand_score(y[real], km[real]), 3))
