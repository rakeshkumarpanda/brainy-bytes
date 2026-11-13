# 2.1 Linear algebra for ML: vectors, distances and matrices
# Example "linear_model_as_matrix" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# 3 houses, features: size in 100 m2, rooms, age in 10 years
X = np.array([[0.5, 1, 1.0],
              [0.8, 2, 0.5],
              [1.2, 3, 0.2]])
w = np.array([40.0, 5.0, -3.0])     # price change per unit of each feature
b = 4.0                              # base price

prices = X @ w + b                   # all predictions in one line
print("predicted prices:", prices)
print("shape of X:", X.shape, "shape of w:", w.shape, "shape of result:", prices.shape)
