# 1.2 Hierarchical clustering and DBSCAN
# Example "choose_eps" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import make_moons
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN

X, _ = make_moons(n_samples=300, noise=0.06, random_state=1)
k = 5                                                   # same as min_samples
dist, _ = NearestNeighbors(n_neighbors=k).fit(X).kneighbors(X)
kth = np.sort(dist[:, -1])                              # distance to the 5th neighbour (itself counts as one)
for q in [50, 75, 90, 95, 99, 100]:
    print("percentile", str(q).rjust(3), " 5th neighbour distance", round(float(np.percentile(kth, q)), 3))
for eps in [0.05, 0.1, 0.2, 0.4, 1.0]:
    lab = DBSCAN(eps=eps, min_samples=k).fit_predict(X)
    print("eps", str(eps).ljust(4), " clusters", len(set(lab)) - (1 if -1 in lab else 0), " noise", int((lab == -1).sum()))
