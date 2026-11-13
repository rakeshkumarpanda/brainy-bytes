# 2.1 Logistic regression: probabilities for classification
# Example "penalty_c" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
for C in [0.001, 0.01, 0.1, 1, 100]:
    model = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=5000))
    score = cross_val_score(model, X, y, cv=5).mean()
    size = abs(model.fit(X, y)[-1].coef_).sum()
    print("C =", str(C).ljust(5), " accuracy", round(score, 3), " total weight size", round(size, 1))
