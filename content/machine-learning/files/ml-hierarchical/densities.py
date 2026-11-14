# 1.2 Hierarchical clustering and DBSCAN
# Example "densities" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.cluster import DBSCAN, HDBSCAN, OPTICS
from sklearn.datasets import make_blobs
from sklearn.metrics import adjusted_rand_score

# A tight group, a wide group and a medium group
X, y = make_blobs(n_samples=[200, 200, 100], centers=[[0, 0], [7, 0], [3, 6]], cluster_std=[0.25, 1.8, 0.5], random_state=4)
for name, model in [("DBSCAN eps 0.3", DBSCAN(eps=0.3, min_samples=5)),
                    ("DBSCAN eps 1.0", DBSCAN(eps=1.0, min_samples=5)),
                    ("DBSCAN eps 1.5", DBSCAN(eps=1.5, min_samples=5)),
                    ("HDBSCAN", HDBSCAN(min_cluster_size=20, copy=True)),
                    ("OPTICS", OPTICS(min_samples=20, xi=0.05, min_cluster_size=0.1))]:
    lab = model.fit_predict(X)
    k = len(set(lab)) - (1 if -1 in lab else 0)
    print(name.ljust(15), " clusters", k, " noise", str(int((lab == -1).sum())).rjust(3), " ARI", round(adjusted_rand_score(y, lab), 3))
