# 3.1 Anomaly detection
# Example "isolation_forest" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, roc_auc_score

rng = np.random.default_rng(1)
normal = rng.normal(0, 1, size=(980, 2))
odd = rng.uniform(-6, 6, size=(20, 2))
odd = odd[np.abs(odd).max(axis=1) > 3]                 # keep only points well outside the normal cloud
X = np.vstack([normal, odd])
y = np.r_[np.zeros(len(normal)), np.ones(len(odd))]   # 1 = anomaly, used only to check the result
iso = IsolationForest(n_estimators=200, contamination=len(odd) / len(X), random_state=0).fit(X)
flag = iso.predict(X) == -1                            # scikit-learn marks anomalies with -1
print("anomalies planted:", len(odd), " flagged:", int(flag.sum()))
print("precision", round(float(precision_score(y, flag)), 3), " recall", round(float(recall_score(y, flag)), 3))
print("ROC AUC of the anomaly score:", round(float(roc_auc_score(y, -iso.score_samples(X))), 3))
