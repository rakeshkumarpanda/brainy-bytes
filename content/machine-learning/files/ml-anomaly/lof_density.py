# 3.1 Anomaly detection
# Example "lof_density" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

rng = np.random.default_rng(2)
dense = rng.normal([0, 0], 0.2, size=(200, 2))         # a very tight group
sparse = rng.normal([5, 5], 1.5, size=(200, 2))        # a loose group
local = np.array([[1.2, 0.0]])                         # just outside the tight group
X = np.vstack([dense, sparse, local])
lof = LocalOutlierFactor(n_neighbors=20).fit(X)
lof_score = -lof.negative_outlier_factor_
iso_score = -IsolationForest(random_state=0).fit(X).score_samples(X)
for name, s in [("LOF", lof_score), ("Isolation Forest", iso_score)]:
    rank = int((s > s[-1]).sum()) + 1
    print(name.ljust(16), " rank of the point next to the tight group:", rank, "of", len(X))
print("LOF of that point:", round(float(lof_score[-1]), 2), " typical LOF inside a group:", round(float(np.median(lof_score)), 2))
