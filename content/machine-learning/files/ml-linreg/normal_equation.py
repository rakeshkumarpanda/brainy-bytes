# 1.1 Linear regression: fit the best straight line
# Example "normal_equation" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.linear_model import LinearRegression

# size_m2, rooms, age_years  ->  price (lakh)
X = np.array([[50, 1, 10], [70, 2, 5], [80, 2, 20], [100, 3, 2], [120, 3, 15], [150, 4, 8]])
y = np.array([40, 62, 60, 95, 98, 135])

ones = np.ones((len(X), 1))
Xb = np.hstack([ones, X])                         # add a column of 1s for the intercept
w = np.linalg.solve(Xb.T @ Xb, Xb.T @ y)           # normal equation
print("normal equation weights:", np.round(w, 3).tolist())

model = LinearRegression().fit(X, y)
print("sklearn intercept:", round(model.intercept_, 3), " coefficients:", np.round(model.coef_, 3).tolist())
print("predict a 90 m2, 2 room, 10 year old flat:", round(model.predict([[90, 2, 10]])[0], 2))
