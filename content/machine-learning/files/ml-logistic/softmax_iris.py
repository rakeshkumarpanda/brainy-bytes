# 2.1 Logistic regression: probabilities for classification
# Example "softmax_iris" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

def softmax(scores):
    exps = [np.exp(s - max(scores)) for s in scores]
    total = sum(exps)
    return [round(float(e / total), 3) for e in exps]

print("softmax of scores [2.0, 1.0, 0.1]:", softmax([2.0, 1.0, 0.1]))

X, y = load_iris(return_X_y=True)
model = LogisticRegression(max_iter=1000)
print("iris 3 classes, cross validated accuracy:", round(cross_val_score(model, X, y, cv=5).mean(), 3))
model.fit(X, y)
print("one flower, class probabilities:", np.round(model.predict_proba(X[[60]]), 3).tolist())
print("weights shape (classes x features):", model.coef_.shape)
