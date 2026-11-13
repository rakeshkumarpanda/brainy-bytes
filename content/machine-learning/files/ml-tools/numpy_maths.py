# 1.3 Python tools for ML: NumPy, pandas and scikit-learn
# Example "numpy_maths" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

w = np.array([0.5, -1.0, 2.0])      # weights of a model
x = np.array([4.0, 1.0, 3.0])       # one example with 3 features
print("dot product w . x =", np.dot(w, x))           # 0.5*4 - 1*1 + 2*3

X = np.array([[4.0, 1.0, 3.0],
              [1.0, 0.0, 2.0]])     # two examples
print("predictions for both rows:", X @ w)           # matrix times vector

rng = np.random.default_rng(seed=0)                  # repeatable random numbers
noise = rng.normal(loc=0, scale=1, size=3)
print("random normal numbers:", noise.round(3))
print("square roots:", np.sqrt([4, 9, 16]), "exp(0) =", np.exp(0))
