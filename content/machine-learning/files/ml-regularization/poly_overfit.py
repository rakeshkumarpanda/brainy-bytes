# 1.2 Polynomial regression and regularisation: ridge, lasso, elastic net
# Example "poly_overfit" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

rng = np.random.default_rng(0)
x = np.sort(rng.uniform(0, 1, 15)).reshape(-1, 1)
y = np.sin(2 * np.pi * x.ravel()) + rng.normal(0, 0.2, 15)
x_test = rng.uniform(0, 1, 200).reshape(-1, 1)
y_test = np.sin(2 * np.pi * x_test.ravel()) + rng.normal(0, 0.2, 200)

for degree in [1, 3, 6, 9, 12]:
    model = make_pipeline(PolynomialFeatures(degree), LinearRegression()).fit(x, y)
    train = mean_squared_error(y, model.predict(x))
    test = mean_squared_error(y_test, model.predict(x_test))
    print("degree", str(degree).rjust(2), " train MSE", round(train, 3), " test MSE", round(test, 2))
