# 4.3 Tuning and calibration
# Example "random_search" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from scipy.stats import loguniform
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
pipe = make_pipeline(StandardScaler(), SVC())
space = {"svc__C": loguniform(0.01, 1000), "svc__gamma": loguniform(0.0001, 1)}
search = RandomizedSearchCV(pipe, space, n_iter=12, cv=5, random_state=0).fit(X, y)
best = search.best_params_
print("12 random settings, best C =", round(best["svc__C"], 2), " gamma =", round(best["svc__gamma"], 5))
print("best cross validated accuracy:", round(search.best_score_, 3))
