# 4.2 Validation: honest estimates of performance
# Example "groups" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold, KFold, cross_val_score

rng = np.random.default_rng(1)
patients, rows_each = 40, 10
groups = np.repeat(np.arange(patients), rows_each)
person = rng.normal(size=(patients, 5))              # each patient has their own typical values
X = person[groups] + rng.normal(0, 0.3, (patients * rows_each, 5))
y = rng.integers(0, 2, patients)[groups]             # the label belongs to the patient and is random

model = RandomForestClassifier(n_estimators=100, random_state=0)
mixed = cross_val_score(model, X, y, cv=KFold(5, shuffle=True, random_state=0)).mean()
grouped = cross_val_score(model, X, y, cv=GroupKFold(5), groups=groups).mean()
print("KFold, same patient in train and validation:", round(mixed, 3))
print("GroupKFold, each patient in one fold only:   ", round(grouped, 3))
