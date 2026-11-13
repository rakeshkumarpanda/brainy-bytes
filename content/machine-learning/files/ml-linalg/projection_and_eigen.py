# 2.1 Linear algebra for ML: vectors, distances and matrices
# Example "projection_and_eigen" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Project a point onto a direction (the idea behind PCA and least squares)
x = np.array([3.0, 4.0])
d = np.array([1.0, 0.0])            # the direction of the x axis
shadow = (x @ d) / (d @ d) * d
print("projection of (3, 4) on the x axis:", shadow)

# Eigenvectors: directions a matrix only stretches, never turns
S = np.array([[2.0, 1.0],
              [1.0, 2.0]])
values, vectors = np.linalg.eigh(S)  # eigh is for symmetric matrices
print("eigenvalues:", values.round(4))
print("eigenvectors (columns):")
print(vectors.round(4))
v = vectors[:, 1]
print("S @ v =", (S @ v).round(4), " = 3 x v =", (3 * v).round(4))
