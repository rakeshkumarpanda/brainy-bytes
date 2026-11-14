# 4.1 Metrics: measuring a model properly
# Example "thresholds" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                            # now 1 = malignant, the case we must not miss
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
model = make_pipeline(StandardScaler(), LogisticRegression(C=0.05, max_iter=1000)).fit(X_train, y_train)
prob = model.predict_proba(X_test)[:, 1]
for t in [0.1, 0.3, 0.5, 0.7, 0.9]:
    pred = (prob >= t).astype(int)
    print("threshold", t, " precision", round(precision_score(y_test, pred), 3), " recall", round(recall_score(y_test, pred), 3),
          " missed cancers", int(((pred == 0) & (y_test == 1)).sum()))
