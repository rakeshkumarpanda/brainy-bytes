# 1.2 Polynomial regression and regularisation: ridge, lasso, elastic net
# Example "lasso_sparse" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.linear_model import Lasso, Ridge

rng = np.random.default_rng(2)
X = rng.normal(0, 1, (100, 10))
true_w = np.array([4, -3, 2, 0, 0, 0, 0, 0, 0, 0])
y = X @ true_w + rng.normal(0, 1, 100)

for alpha in [0.01, 0.1, 0.5, 1.0]:
    w = Lasso(alpha=alpha).fit(X, y).coef_
    print("lasso alpha", str(alpha).ljust(4), " non zero:", int(np.sum(w != 0)), " weights:", (np.round(w, 1) + 0.0).tolist())
print("ridge alpha 10   non zero:", int(np.sum(Ridge(alpha=10).fit(X, y).coef_ != 0)))
