# 1.1 Linear regression: fit the best straight line
# Example "sgd_vs_exact" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(3)
X = rng.uniform(0, 10, size=(200, 2))
y = 4 * X[:, 0] - 2 * X[:, 1] + 7 + rng.normal(0, 1, 200)

Xs = StandardScaler().fit_transform(X)
exact = LinearRegression().fit(Xs, y)
sgd = SGDRegressor(max_iter=1000, tol=1e-6, random_state=0).fit(Xs, y)
print("closed form:", round(exact.intercept_, 3), np.round(exact.coef_, 3).tolist())
print("SGD:        ", round(sgd.intercept_[0], 3), np.round(sgd.coef_, 3).tolist())
print("SGD needed", sgd.n_iter_, "passes over the data")
