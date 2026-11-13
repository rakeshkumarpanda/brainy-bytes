# 1.2 Polynomial regression and regularisation: ridge, lasso, elastic net
# Example "ridge_formula" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.linear_model import Ridge

rng = np.random.default_rng(4)
X = rng.normal(0, 1, (20, 3))
y = X @ np.array([1.0, 2.0, -1.0]) + rng.normal(0, 0.3, 20)
lam = 5.0

w = np.linalg.solve(X.T @ X + lam * np.eye(3), X.T @ y)       # ridge closed form
print("by formula:", np.round(w, 4).tolist())
print("sklearn:   ", np.round(Ridge(alpha=lam, fit_intercept=False).fit(X, y).coef_, 4).tolist())
