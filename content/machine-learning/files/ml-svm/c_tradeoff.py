# 2.4 Support vector machines: the widest street
# Example "c_tradeoff" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

X, y = make_blobs(n_samples=300, centers=2, cluster_std=2.2, random_state=4)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0)
for C in [0.001, 0.01, 0.1, 1, 100]:
    model = SVC(kernel="linear", C=C).fit(X_train, y_train)
    width = 2 / np.linalg.norm(model.coef_[0])
    print("C", str(C).rjust(5), " margin", str(round(float(width), 2)).rjust(5), " support vectors", str(len(model.support_)).rjust(3),
          " train", round(model.score(X_train, y_train), 3), " test", round(model.score(X_test, y_test), 3))
