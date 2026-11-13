# 2.1 Principal component analysis (PCA)
# Example "scaling_pca" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_wine
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

data = load_wine()
X, names = data.data, data.feature_names
for label, Z in [("raw", X), ("scaled", StandardScaler().fit_transform(X))]:
    pca = PCA(n_components=2).fit(Z)
    top = np.argsort(np.abs(pca.components_[0]))[::-1][:2]
    print(label.ljust(6), " variance in PC1", round(float(pca.explained_variance_ratio_[0]), 3),
          " biggest weights:", [names[i] for i in top])
print("proline ranges up to", int(X[:, 12].max()), "while hue stays below", round(float(X[:, 10].max()), 2))
