# 3.1 Anomaly detection
# Example "evaluate" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

rng = np.random.default_rng(4)
y = np.r_[np.zeros(9900), np.ones(100)]                 # 1% anomalies
score = np.r_[rng.normal(0, 1, 9900), rng.normal(2.5, 1, 100)]
print("ROC AUC", round(float(roc_auc_score(y, score)), 3), "  PR AUC", round(float(average_precision_score(y, score)), 3), "  (PR AUC of random guessing = 0.01)")
order = np.argsort(-score)
for k in [50, 100, 500]:
    print("precision at top", str(k).rjust(3), round(float(y[order[:k]].mean()), 2), "  recall", round(float(y[order[:k]].sum() / 100), 2))
