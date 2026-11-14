# 3.1 Anomaly detection
# Example "compare_methods" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

rng = np.random.default_rng(3)
train = np.vstack([rng.normal([0, 0], 1, (500, 2)), rng.normal([6, 6], 1, (500, 2))])   # clean normal data
test_ok = np.vstack([rng.normal([0, 0], 1, (200, 2)), rng.normal([6, 6], 1, (200, 2))])
test_bad = rng.uniform(-4, 10, (60, 2))
test_bad = test_bad[np.minimum(np.linalg.norm(test_bad, axis=1), np.linalg.norm(test_bad - 6, axis=1)) > 3.5]
X_test = np.vstack([test_ok, test_bad])
y_test = np.r_[np.zeros(len(test_ok)), np.ones(len(test_bad))]
sc = StandardScaler().fit(train)
A, B = sc.transform(train), sc.transform(X_test)
models = {"Isolation Forest": IsolationForest(random_state=0),
          "LOF (novelty)": LocalOutlierFactor(n_neighbors=20, novelty=True),
          "One class SVM": OneClassSVM(nu=0.05, gamma=0.5),
          "Elliptic envelope": EllipticEnvelope(random_state=0),
          "Gaussian mixture": GaussianMixture(n_components=2, random_state=0)}
for name, m in models.items():
    m.fit(A)
    score = -m.score_samples(B)                         # higher = more unusual
    print(name.ljust(17), " ROC AUC", round(float(roc_auc_score(y_test, score)), 3), "  PR AUC", round(float(average_precision_score(y_test, score)), 3))
print("anomalies in the test set:", len(test_bad), "of", len(X_test))
