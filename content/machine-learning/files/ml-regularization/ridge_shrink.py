# 1.2 Polynomial regression and regularisation: ridge, lasso, elastic net
# Example "ridge_shrink" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.linear_model import LinearRegression, Ridge

rng = np.random.default_rng(1)
n = 40
size = rng.normal(0, 1, n)
rooms = size + rng.normal(0, 0.05, n)          # almost a copy of size
y = 3 * size + rng.normal(0, 1, n)
X = np.column_stack([size, rooms])

print("plain least squares:", np.round(LinearRegression().fit(X, y).coef_, 2).tolist())
for alpha in [0.1, 1, 10, 100]:
    print("ridge alpha", str(alpha).rjust(5), ":", np.round(Ridge(alpha=alpha).fit(X, y).coef_, 2).tolist())
