# 2.2 Manifold learning: t-SNE, UMAP, MDS and Isomap
# Example "mds_map" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.manifold import MDS

# Five towns: we only know the road distances between them, not where they are
names = ["A", "B", "C", "D", "E"]
true = np.array([[0, 0], [4, 0], [4, 3], [0, 3], [2, 6]], dtype=float)
D = np.sqrt(((true[:, None] - true[None]) ** 2).sum(axis=2))
print("distance matrix:", np.round(D, 1).tolist())
mds = MDS(n_components=2, metric="precomputed", metric_mds=True, init="classical_mds", n_init=1, random_state=0)
Z = mds.fit_transform(D)
Dz = np.sqrt(((Z[:, None] - Z[None]) ** 2).sum(axis=2))
print("largest error in any rebuilt distance:", round(float(np.abs(D - Dz).max()), 3))
print("A to E: true", round(float(D[0, 4]), 2), " rebuilt", round(float(Dz[0, 4]), 2))
