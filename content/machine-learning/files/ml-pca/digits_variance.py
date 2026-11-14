# 2.1 Principal component analysis (PCA)
# Example "digits_variance" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

X, y = load_digits(return_X_y=True)              # 1,797 images of 8 x 8 pixels = 64 features
pca = PCA().fit(X)
cum = np.cumsum(pca.explained_variance_ratio_)
for k in [1, 2, 5, 10, 20, 30, 40]:
    print("components", str(k).rjust(2), " variance kept", round(float(cum[k - 1]), 3))
print("components needed for 90%:", int(np.argmax(cum >= 0.90)) + 1, " for 95%:", int(np.argmax(cum >= 0.95)) + 1)
print("PCA(0.95) picks", PCA(n_components=0.95).fit(X).n_components_, "components by itself")
