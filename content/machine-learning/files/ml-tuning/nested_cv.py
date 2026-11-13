# 4.3 Tuning and calibration
# Example "nested_cv" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import GridSearchCV, KFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
X, y = X[:150], y[:150]                              # a small dataset makes the optimism visible
pipe = make_pipeline(StandardScaler(), SVC())
grid = {"svc__C": [0.01, 0.1, 1, 10, 100, 1000], "svc__gamma": [0.0001, 0.001, 0.01, 0.1, 1]}
inner = KFold(5, shuffle=True, random_state=1)
outer = KFold(5, shuffle=True, random_state=2)
search = GridSearchCV(pipe, grid, cv=inner).fit(X, y)
print("best inner score (used to choose):", round(search.best_score_, 3))
nested = cross_val_score(GridSearchCV(pipe, grid, cv=inner), X, y, cv=outer)
print("nested cross validation score:   ", round(nested.mean(), 3))
