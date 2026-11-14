# 1.3 Gaussian mixture models and EM
# Example "bayesian_gmm" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import make_blobs
from sklearn.mixture import BayesianGaussianMixture

X, _ = make_blobs(n_samples=400, centers=3, cluster_std=0.8, random_state=5)
bgm = BayesianGaussianMixture(n_components=8, weight_concentration_prior=0.01, max_iter=500, random_state=0).fit(X)
print("weights of the 8 allowed components:", np.round(np.sort(bgm.weights_)[::-1], 3).tolist())
print("components really used (weight above 1%):", int((bgm.weights_ > 0.01).sum()))
