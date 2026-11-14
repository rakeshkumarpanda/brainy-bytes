# 4.2 Validation: honest estimates of performance
# Example "kfold_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
folds = KFold(n_splits=5, shuffle=True, random_state=0)
scores = []
for i, (train_idx, val_idx) in enumerate(folds.split(X)):
    model.fit(X[train_idx], y[train_idx])
    s = model.score(X[val_idx], y[val_idx])
    scores.append(s)
    print("fold", i + 1, " train rows", len(train_idx), " validation rows", len(val_idx), " accuracy", round(s, 3))
print("mean", round(float(np.mean(scores)), 3), " standard deviation", round(float(np.std(scores)), 3))
print("cross_val_score gives the same:", round(cross_val_score(model, X, y, cv=folds).mean(), 3))
