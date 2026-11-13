# 2.1 Linear algebra for ML: vectors, distances and matrices
# Example "solve_system" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Find w1, w2 so that  2*w1 + 1*w2 = 5  and  1*w1 + 3*w2 = 10
A = np.array([[2.0, 1.0],
              [1.0, 3.0]])
y = np.array([5.0, 10.0])

w = np.linalg.solve(A, y)          # better than computing the inverse
print("w =", w)
print("check A @ w =", A @ w)
print("determinant:", round(np.linalg.det(A), 6))
print("inverse:")
print(np.linalg.inv(A).round(4))
print("rank:", np.linalg.matrix_rank(A))
