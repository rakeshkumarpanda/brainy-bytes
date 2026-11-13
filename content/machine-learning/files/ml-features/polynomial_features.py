# 3.2 Features: encoding, scaling, engineering and selection
# Example "polynomial_features" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

rng = np.random.default_rng(2)
x = rng.uniform(-3, 3, size=(80, 1))
y = 2 * x[:, 0] ** 2 - x[:, 0] + rng.normal(0, 1, size=80)    # a curve, not a line

line = LinearRegression().fit(x, y)
print("straight line R2:", round(line.score(x, y), 3))

poly = PolynomialFeatures(degree=2, include_bias=False)
x2 = poly.fit_transform(x)
print("new columns:", poly.get_feature_names_out(["x"]).tolist())
curve = LinearRegression().fit(x2, y)
print("with x squared R2:", round(curve.score(x2, y), 3))
print("learned weights:", np.round(curve.coef_, 2).tolist(), " true: [-1, 2]")

two = PolynomialFeatures(degree=2, include_bias=False).fit(np.zeros((1, 2)))
print("two features become:", two.get_feature_names_out(["a", "b"]).tolist())
