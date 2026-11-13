# 4.2 Validation: honest estimates of performance
# Example "leakage" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline

rng = np.random.default_rng(0)
X = rng.normal(size=(100, 5000))                    # pure noise
y = rng.integers(0, 2, 100)                         # random labels: nothing to learn

X_leaky = SelectKBest(f_classif, k=20).fit_transform(X, y)      # chose features using ALL rows
wrong = cross_val_score(LogisticRegression(max_iter=1000), X_leaky, y, cv=5).mean()
pipe = make_pipeline(SelectKBest(f_classif, k=20), LogisticRegression(max_iter=1000))
right = cross_val_score(pipe, X, y, cv=5).mean()
print("selection before cross validation (leak):", round(wrong, 3))
print("selection inside a pipeline (honest):   ", round(right, 3))
