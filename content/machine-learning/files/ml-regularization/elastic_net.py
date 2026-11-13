# 1.2 Polynomial regression and regularisation: ridge, lasso, elastic net
# Example "elastic_net" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.linear_model import ElasticNet, Lasso

rng = np.random.default_rng(3)
n = 100
base = rng.normal(0, 1, n)
a = base + rng.normal(0, 0.1, n)               # three almost identical features
b = base + rng.normal(0, 0.1, n)
c = base + rng.normal(0, 0.1, n)
noise = rng.normal(0, 1, (n, 2))
X = np.column_stack([a, b, c, noise])
y = 3 * base + rng.normal(0, 0.5, n)

print("lasso:      ", (np.round(Lasso(alpha=0.1).fit(X, y).coef_, 2) + 0.0).tolist())
print("elastic net:", (np.round(ElasticNet(alpha=0.1, l1_ratio=0.3).fit(X, y).coef_, 2) + 0.0).tolist())
