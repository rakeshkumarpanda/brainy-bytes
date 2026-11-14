# 4.1 Metrics: measuring a model properly
# Example "accuracy_trap" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score

rng = np.random.default_rng(0)
y = (rng.random(10000) < 0.01).astype(int)          # 1% fraud
X = rng.normal(size=(10000, 3))
lazy = DummyClassifier(strategy="most_frequent").fit(X, y)
pred = lazy.predict(X)
print("fraud cases:", int(y.sum()), "of", len(y))
print("accuracy of 'never fraud':", round(accuracy_score(y, pred), 3))
print("recall:", recall_score(y, pred), " balanced accuracy:", balanced_accuracy_score(y, pred))
