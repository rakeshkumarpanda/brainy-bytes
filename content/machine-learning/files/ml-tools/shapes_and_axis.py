# 1.3 Python tools for ML: NumPy, pandas and scikit-learn
# Example "shapes_and_axis" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# 4 students (rows) x 3 tests (columns)
scores = np.array([[70, 80, 90],
                   [60, 65, 70],
                   [90, 85, 95],
                   [50, 55, 60]])
print("shape:", scores.shape, "number of values:", scores.size)
print("average of each test (down the rows, axis=0):", scores.mean(axis=0))
print("average of each student (across, axis=1):", scores.mean(axis=1))
print("reshape to 2 x 6:")
print(scores.reshape(2, 6))
print("transpose shape:", scores.T.shape)

# broadcasting: subtract each column's mean from that column
centred = scores - scores.mean(axis=0)
print("centred column means:", centred.mean(axis=0))
