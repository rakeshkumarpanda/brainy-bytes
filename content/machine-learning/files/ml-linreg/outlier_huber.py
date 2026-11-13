# 1.1 Linear regression: fit the best straight line
# Example "outlier_huber" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.linear_model import HuberRegressor, LinearRegression

x = np.arange(1, 11).reshape(-1, 1).astype(float)
y = 2 * x.ravel() + 1
y[9] = 60                                            # one bad value (should be 21)

ols = LinearRegression().fit(x, y)
huber = HuberRegressor().fit(x, y)
print("true line:   slope 2, intercept 1")
print("least squares slope", round(ols.coef_[0], 2), " intercept", round(ols.intercept_, 2))
print("Huber        slope", round(huber.coef_[0], 2), " intercept", round(huber.intercept_, 2))
