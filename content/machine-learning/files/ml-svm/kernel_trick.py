# 2.4 Support vector machines: the widest street
# Example "kernel_trick" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import make_circles
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC

X, y = make_circles(n_samples=300, noise=0.1, factor=0.4, random_state=0)
for kernel in ["linear", "poly", "rbf"]:
    model = SVC(kernel=kernel, degree=2)
    print(kernel.ljust(6), "accuracy", round(cross_val_score(model, X, y, cv=5).mean(), 3))

# the same idea by hand: add the feature x1^2 + x2^2, then a straight line works
X_lifted = np.column_stack([X, X[:, 0] ** 2 + X[:, 1] ** 2])
print("linear on lifted data", round(cross_val_score(SVC(kernel="linear"), X_lifted, y, cv=5).mean(), 3))
