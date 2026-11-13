# 1.3 Gaussian mixture models and EM
# Example "sklearn_gmm" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score

rng = np.random.default_rng(0)
a = rng.multivariate_normal([0, 0], [[6, 0], [0, 0.3]], size=200)     # long, flat cluster
b = rng.multivariate_normal([0, 2.5], [[6, 0], [0, 0.3]], size=200)   # another one just above it
X, y = np.vstack([a, b]), np.repeat([0, 1], 200)

km = KMeans(n_clusters=2, n_init=10, random_state=0).fit(X)
one = GaussianMixture(n_components=2, covariance_type="full", n_init=1, random_state=0).fit(X)
gm = GaussianMixture(n_components=2, covariance_type="full", n_init=5, random_state=0).fit(X)
print("k-means ARI", round(adjusted_rand_score(y, km.labels_), 3))
print("GMM, 1 start  ARI", round(adjusted_rand_score(y, one.predict(X)), 3), " average log likelihood", round(float(one.score(X)), 3))
print("GMM, 5 starts ARI", round(adjusted_rand_score(y, gm.predict(X)), 3), " average log likelihood", round(float(gm.score(X)), 3))
print("weights", np.round(gm.weights_, 2).tolist())
print("means", np.round(gm.means_, 2).tolist())
print("probabilities for point [0, 1.25]:", np.round(gm.predict_proba([[0, 1.25]]), 3).tolist())
print("probabilities for point [4, 0]:", np.round(gm.predict_proba([[4, 0]]), 3).tolist())
