# 4.2 Validation: honest estimates of performance
# Example "stratified" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.model_selection import KFold, StratifiedKFold

y = np.array([0] * 90 + [1] * 10)                   # sorted labels, 10% positives
X = np.zeros((100, 1))
for name, cv in [("KFold", KFold(n_splits=5)), ("StratifiedKFold", StratifiedKFold(n_splits=5))]:
    shares = [int(y[val].sum()) for _, val in cv.split(X, y)]
    print(name.ljust(16), "positives in each validation fold:", shares)
