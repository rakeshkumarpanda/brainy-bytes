# 2.3 Naive Bayes: classify by counting clues
# Example "gaussian_iris" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import GaussianNB

X, y = load_iris(return_X_y=True)
print("cross validated accuracy:", round(cross_val_score(GaussianNB(), X, y, cv=5).mean(), 3))
model = GaussianNB().fit(X, y)
print("petal length mean per class:", np.round(model.theta_[:, 2], 2).tolist())
print("petal length variance per class:", np.round(model.var_[:, 2], 3).tolist())
print("a flower with petal length 4.8:", np.round(model.predict_proba([[6.0, 2.9, 4.8, 1.6]]), 3).tolist())
