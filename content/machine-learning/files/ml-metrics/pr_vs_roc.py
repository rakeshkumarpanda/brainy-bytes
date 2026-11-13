# 4.1 Metrics: measuring a model properly
# Example "pr_vs_roc" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split

for share in [0.5, 0.05, 0.01]:
    X, y = make_classification(n_samples=20000, n_features=10, n_informative=4, weights=[1 - share], flip_y=0.01, random_state=0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=0, stratify=y)
    prob = LogisticRegression(max_iter=1000).fit(X_train, y_train).predict_proba(X_test)[:, 1]
    print("positives", str(share).ljust(4), " ROC AUC", round(roc_auc_score(y_test, prob), 3),
          " average precision (PR AUC)", round(average_precision_score(y_test, prob), 3))
