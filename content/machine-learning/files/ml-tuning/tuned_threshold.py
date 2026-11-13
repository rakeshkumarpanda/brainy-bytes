# 4.3 Tuning and calibration
# Example "tuned_threshold" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import TunedThresholdClassifierCV, train_test_split

X, y = make_classification(n_samples=5000, n_features=10, n_informative=3, weights=[0.95], flip_y=0.01, random_state=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0, stratify=y)
base = LogisticRegression(max_iter=1000).fit(X_train, y_train)
tuned = TunedThresholdClassifierCV(LogisticRegression(max_iter=1000), scoring="f1", cv=5).fit(X_train, y_train)
print("threshold 0.5:", " F1", round(f1_score(y_test, base.predict(X_test)), 3))
print("tuned threshold", round(float(tuned.best_threshold_), 3), " F1", round(f1_score(y_test, tuned.predict(X_test)), 3))
