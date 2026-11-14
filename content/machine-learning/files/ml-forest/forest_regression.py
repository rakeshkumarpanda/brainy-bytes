# 3.2 Random forests: many trees vote
# Example "forest_regression" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_diabetes
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeRegressor

X, y = load_diabetes(return_X_y=True)
models = {
    "linear regression": LinearRegression(),
    "one tree": DecisionTreeRegressor(random_state=0),
    "random forest": RandomForestRegressor(n_estimators=200, min_samples_leaf=5, random_state=0),
    "extra trees": ExtraTreesRegressor(n_estimators=200, min_samples_leaf=5, random_state=0),
}
for name, model in models.items():
    print(name.ljust(17), "R2", round(cross_val_score(model, X, y, cv=5, scoring="r2").mean(), 3))
