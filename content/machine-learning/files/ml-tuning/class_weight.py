# 4.3 Tuning and calibration
# Example "class_weight" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=5000, n_features=10, n_informative=3, weights=[0.95], flip_y=0.01, random_state=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0, stratify=y)
for cw in [None, "balanced"]:
    pred = LogisticRegression(class_weight=cw, max_iter=1000).fit(X_train, y_train).predict(X_test)
    print("class_weight", str(cw).ljust(8), " recall", round(recall_score(y_test, pred), 3), " precision", round(precision_score(y_test, pred), 3))
