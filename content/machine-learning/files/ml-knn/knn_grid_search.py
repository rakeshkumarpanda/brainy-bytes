# 2.2 k nearest neighbours: learn from similar examples
# Example "knn_grid_search" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_wine
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_wine(return_X_y=True)
pipe = Pipeline([("scale", StandardScaler()), ("knn", KNeighborsClassifier())])
grid = GridSearchCV(pipe, {"knn__n_neighbors": [1, 3, 5, 7, 9, 15], "knn__weights": ["uniform", "distance"], "knn__p": [1, 2]}, cv=5)
grid.fit(X, y)
print("best settings:", grid.best_params_)
print("best cross validated accuracy:", round(grid.best_score_, 3))
