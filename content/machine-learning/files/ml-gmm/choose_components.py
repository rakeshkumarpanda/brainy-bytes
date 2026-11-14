# 1.3 Gaussian mixture models and EM
# Example "choose_components" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import make_blobs
from sklearn.mixture import GaussianMixture

X, _ = make_blobs(n_samples=500, centers=4, cluster_std=[0.6, 1.0, 0.8, 1.4], random_state=3)
for k in range(1, 8):
    gm = GaussianMixture(n_components=k, random_state=0, n_init=3).fit(X)
    print("components", k, " BIC", str(round(float(gm.bic(X)), 1)).rjust(7), " AIC", str(round(float(gm.aic(X)), 1)).rjust(7))
