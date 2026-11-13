# 2.1 Logistic regression: probabilities for classification
# Example "cancer_logistic" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.25, random_state=0, stratify=data.target)

model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X_train, y_train)
print("classes:", data.target_names.tolist(), " (1 means benign)")
print("test accuracy:", round(model.score(X_test, y_test), 3))
print("first 3 test rows, P(benign):", np.round(model.predict_proba(X_test[:3])[:, 1], 3).tolist())
print("predicted labels:", model.predict(X_test[:3]).tolist(), " true labels:", y_test[:3].tolist())
coef = model[-1].coef_[0]
order = np.argsort(np.abs(coef))[::-1][:3]
print("strongest features:", [(str(data.feature_names[i]), round(float(coef[i]), 2)) for i in order])
