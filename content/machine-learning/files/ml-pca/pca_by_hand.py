# 2.1 Principal component analysis (PCA)
# Example "pca_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Six students: hours studied and exam score move together
X = np.array([[2.0, 50], [3, 58], [4, 61], [5, 70], [6, 74], [7, 81]])
Xc = X - X.mean(axis=0)                          # 1. centre every feature at 0
C = Xc.T @ Xc / (len(X) - 1)                     # 2. covariance matrix
values, vectors = np.linalg.eigh(C)              # 3. eigenvalues come out smallest first
order = np.argsort(values)[::-1]
values, vectors = values[order], vectors[:, order]
vectors = vectors * np.sign(vectors[0])          # fix the sign so the output is stable
print("covariance matrix:", np.round(C, 2).tolist())
print("eigenvalues (variance along each component):", np.round(values, 3).tolist())
print("first component direction:", np.round(vectors[:, 0], 4).tolist())
print("share of variance kept by component 1:", round(float(values[0] / values.sum()), 4))
Z = Xc @ vectors[:, :1]                          # 4. project onto the first component
print("each student as one number:", np.round(Z[:, 0], 2).tolist())
