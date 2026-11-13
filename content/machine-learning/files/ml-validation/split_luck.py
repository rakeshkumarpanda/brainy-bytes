# 4.2 Validation: honest estimates of performance
# Example "split_luck" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
single = []
for seed in range(10):
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=seed)
    single.append(DecisionTreeClassifier(random_state=0).fit(X_tr, y_tr).score(X_te, y_te))
print("10 different single splits:", [round(s, 3) for s in single])
print("lowest", round(min(single), 3), " highest", round(max(single), 3))
cv = cross_val_score(DecisionTreeClassifier(random_state=0), X, y, cv=10)
print("10 fold cross validation: mean", round(cv.mean(), 3), " standard deviation", round(cv.std(), 3))
