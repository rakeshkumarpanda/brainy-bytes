# 2.1 Principal component analysis (PCA)
# Example "pca_sklearn" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.decomposition import PCA

X = np.array([[2.0, 50], [3, 58], [4, 61], [5, 70], [6, 74], [7, 81]])
pca = PCA(n_components=2).fit(X)
print("explained variance:", np.round(pca.explained_variance_, 3).tolist())
print("explained variance ratio:", np.round(pca.explained_variance_ratio_, 4).tolist())
print("component 1 (up to sign):", np.round(np.abs(pca.components_[0]), 4).tolist())

U, S, Vt = np.linalg.svd(X - X.mean(axis=0), full_matrices=False)   # PCA through the SVD
print("from the SVD, S squared / (n - 1):", np.round(S ** 2 / (len(X) - 1), 3).tolist())
one = PCA(n_components=1).fit(X)
approx = one.inverse_transform(one.transform(X))
print("rebuilt from 1 number each:", np.round(approx, 1).tolist())
