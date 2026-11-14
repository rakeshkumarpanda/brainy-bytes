# 2.2 Manifold learning: t-SNE, UMAP, MDS and Isomap
# Example "tsne_pitfalls" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.manifold import TSNE

rng = np.random.default_rng(0)
tight = rng.normal(0, 0.5, size=(150, 10))               # a tight cluster
wide = rng.normal(0, 5.0, size=(150, 10)) + 40           # a wide cluster far away
far = rng.normal(0, 0.5, size=(150, 10)) + 400           # a tight cluster very far away
X = np.vstack([tight, wide, far])
Z = TSNE(n_components=2, perplexity=30, init="pca", random_state=0).fit_transform(X)
spread = lambda A: float(np.sqrt(((A - A.mean(axis=0)) ** 2).sum(axis=1)).mean())
print("spread in 10D:  tight", round(spread(X[:150]), 1), "  wide", round(spread(X[150:300]), 1))
print("spread in 2D:   tight", round(spread(Z[:150]), 1), "  wide", round(spread(Z[150:300]), 1))
gap = lambda A, B: float(np.linalg.norm(A.mean(axis=0) - B.mean(axis=0)))
print("gap in 10D:  tight to wide", round(gap(X[:150], X[150:300]), 0), "  tight to far", round(gap(X[:150], X[300:]), 0))
print("gap in 2D:   tight to wide", round(gap(Z[:150], Z[150:300]), 0), "  tight to far", round(gap(Z[:150], Z[300:]), 0))
