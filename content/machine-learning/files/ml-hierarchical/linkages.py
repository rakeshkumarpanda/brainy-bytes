# 1.2 Hierarchical clustering and DBSCAN
# Example "linkages" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.datasets import make_blobs, make_moons
from sklearn.metrics import adjusted_rand_score

moons, ym = make_moons(n_samples=300, noise=0.05, random_state=0)
blobs, yb = make_blobs(n_samples=300, centers=3, cluster_std=[1.0, 2.5, 0.5], random_state=170)
for method in ["single", "complete", "average", "ward"]:
    a = AgglomerativeClustering(n_clusters=2, linkage=method).fit_predict(moons)
    b = AgglomerativeClustering(n_clusters=3, linkage=method).fit_predict(blobs)
    print(method.ljust(8), " moons ARI", round(adjusted_rand_score(ym, a), 3), "  uneven blobs ARI", round(adjusted_rand_score(yb, b), 3), " blob sizes", sorted(np.bincount(b).tolist(), reverse=True))
