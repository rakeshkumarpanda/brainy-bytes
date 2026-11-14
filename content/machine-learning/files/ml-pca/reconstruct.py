# 2.1 Principal component analysis (PCA)
# Example "reconstruct" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

X, _ = load_digits(return_X_y=True)
for k in [2, 5, 10, 20, 40, 64]:
    pca = PCA(n_components=k).fit(X)
    back = pca.inverse_transform(pca.transform(X))
    err = np.mean((X - back) ** 2)
    print("keep", str(k).rjust(2), "of 64 numbers  mean squared error", round(float(err), 3) + 0.0)
