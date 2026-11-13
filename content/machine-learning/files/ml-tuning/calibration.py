# 4.3 Tuning and calibration
# Example "calibration" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.datasets import make_classification
from sklearn.metrics import brier_score_loss
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB

X, y = make_classification(n_samples=6000, n_features=20, n_informative=4, n_redundant=10, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=0)
raw = GaussianNB().fit(X_train, y_train)
cal = CalibratedClassifierCV(GaussianNB(), method="isotonic", cv=5).fit(X_train, y_train)
for name, model in [("naive Bayes", raw), ("calibrated", cal)]:
    p = model.predict_proba(X_test)[:, 1]
    frac, mean = calibration_curve(y_test, p, n_bins=5)
    print(name.ljust(11), "Brier", round(brier_score_loss(y_test, p), 4))
    print("   predicted", np.round(mean, 2).tolist())
    print("   observed ", np.round(frac, 2).tolist())
