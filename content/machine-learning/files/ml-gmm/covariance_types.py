# 1.3 Gaussian mixture models and EM
# Example "covariance_types" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.mixture import GaussianMixture

rng = np.random.default_rng(1)
X = np.vstack([rng.multivariate_normal([0, 0], [[3, 2.4], [2.4, 3]], 250),     # tilted
               rng.multivariate_normal([6, 0], [[0.4, 0], [0, 2.5]], 250)])    # tall
for cov in ["spherical", "diag", "tied", "full"]:
    gm = GaussianMixture(n_components=2, covariance_type=cov, random_state=0).fit(X)
    params = gm._n_parameters()                    # the same count that bic() uses
    print(cov.ljust(9), " parameters", str(params).rjust(2), " BIC", round(float(gm.bic(X)), 1))
