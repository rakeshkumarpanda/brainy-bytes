# 1.1 k-means: grouping points around centres
# Example "scaling" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(0)
group = np.repeat([0, 1], 100)
age = np.where(group == 0, 30, 50) + rng.normal(0, 4, 200)              # the real difference
income = rng.normal(50000, 15000, 200)                                  # big numbers, no group information
X = np.column_stack([age, income])
for name, data in [("raw", X), ("scaled", StandardScaler().fit_transform(X))]:
    labels = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(data)
    print(name.ljust(6), "agreement with the true groups (ARI):", round(adjusted_rand_score(group, labels), 3))
