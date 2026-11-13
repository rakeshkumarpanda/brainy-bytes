# 1.3 Python tools for ML: NumPy, pandas and scikit-learn
# Example "numpy_basics" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

marks = np.array([72, 45, 91, 38, 66])        # a 1D array (a vector)
print(marks, marks.dtype, marks.shape)
print("mean:", marks.mean(), "max:", marks.max(), "std:", round(marks.std(), 2))
print("plus 5 to everyone:", marks + 5)         # works on every item at once
print("passed?", marks >= 50)                   # a True or False for every item
print("only passed:", marks[marks >= 50])       # keep items where the test is True

table = np.array([[1, 2, 3],
                  [4, 5, 6]])                    # a 2D array (a matrix)
print(table.shape)                               # (rows, columns)
print("row 1:", table[1], "column 2:", table[:, 2])
print("zeros:", np.zeros(3), "range:", np.arange(0, 10, 3), "line:", np.linspace(0, 1, 5))
