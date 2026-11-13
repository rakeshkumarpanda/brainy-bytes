# 2.3 Naive Bayes: classify by counting clues
# Example "nb_vs_logistic" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
X_rest, X_test, y_rest, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
for size in [10, 30, 100, 398]:
    nb_scores = []
    lr_scores = []
    for seed in range(20):
        rng = np.random.default_rng(seed)
        idx = rng.choice(len(X_rest), size, replace=False)
        if len(set(y_rest[idx])) < 2:
            continue
        nb_scores.append(GaussianNB().fit(X_rest[idx], y_rest[idx]).score(X_test, y_test))
        lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
        lr_scores.append(lr.fit(X_rest[idx], y_rest[idx]).score(X_test, y_test))
    print("training rows", str(size).rjust(3), " naive Bayes", round(np.mean(nb_scores), 3), " logistic", round(np.mean(lr_scores), 3))
