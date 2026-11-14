# 2.4 Support vector machines: the widest street
# Example "margin_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.svm import SVC

X = np.array([[1, 1], [2, 1], [1, 2], [4, 4], [5, 4], [4, 5]])
y = np.array([0, 0, 0, 1, 1, 1])
model = SVC(kernel="linear", C=1000).fit(X, y)
w = model.coef_[0]
b = model.intercept_[0]
print("w =", np.round(w, 3).tolist(), " b =", round(float(b), 3))
print("support vectors:", model.support_vectors_.tolist())
print("margin width 2 / |w| =", round(float(2 / np.linalg.norm(w)), 3))
for point in X:
    print(point.tolist(), " w.x + b =", round(float(w @ point + b), 3))
