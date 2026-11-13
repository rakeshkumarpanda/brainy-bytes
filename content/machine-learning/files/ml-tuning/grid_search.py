# 4.3 Tuning and calibration
# Example "grid_search" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
pipe = make_pipeline(StandardScaler(), SVC())
grid = {"svc__C": [0.1, 1, 10, 100], "svc__gamma": [0.001, 0.01, 0.1]}
search = GridSearchCV(pipe, grid, cv=5).fit(X, y)
print("settings tried:", len(search.cv_results_["params"]), " fits:", len(search.cv_results_["params"]) * 5)
print("best:", search.best_params_, " score", round(search.best_score_, 3))
table = pd.DataFrame(search.cv_results_)[["param_svc__C", "param_svc__gamma", "mean_test_score", "rank_test_score"]]
print(table.sort_values("rank_test_score", kind="stable").head(4).round(3).to_string(index=False))
