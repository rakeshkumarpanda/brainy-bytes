# 2.3 Naive Bayes: classify by counting clues
# Example "overconfident" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
prob = GaussianNB().fit(X_train, y_train).predict_proba(X_test)[:, 1]
extreme = np.mean((prob < 0.01) | (prob > 0.99))
print("share of predictions below 1% or above 99%:", round(float(extreme), 3))
wrong_and_sure = np.sum(((prob > 0.99) & (y_test == 0)) | ((prob < 0.01) & (y_test == 1)))
print("wrong but more than 99% sure:", int(wrong_and_sure), "of", len(y_test))
