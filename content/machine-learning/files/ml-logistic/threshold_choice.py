# 2.1 Logistic regression: probabilities for classification
# Example "threshold_choice" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

data = load_breast_cancer()
y = 1 - data.target                      # now 1 means malignant (the case we must not miss)
X_train, X_test, y_train, y_test = train_test_split(data.data, y, test_size=0.25, random_state=0, stratify=y)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X_train, y_train)
prob = model.predict_proba(X_test)[:, 1]

for threshold in [0.2, 0.5, 0.8]:
    pred = (prob >= threshold).astype(int)
    missed = int(((pred == 0) & (y_test == 1)).sum())
    print("threshold", threshold, " precision", round(precision_score(y_test, pred), 3),
          " recall", round(recall_score(y_test, pred), 3), " missed cancers", missed)
