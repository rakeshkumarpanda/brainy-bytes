# 2.2 k nearest neighbours: learn from similar examples
# Example "knn_regression" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.model_selection import KFold, cross_val_score
from sklearn.neighbors import KNeighborsRegressor

rng = np.random.default_rng(0)
x = np.sort(rng.uniform(0, 10, 80)).reshape(-1, 1)
y = np.sin(x.ravel()) + rng.normal(0, 0.2, 80)

for weights in ["uniform", "distance"]:
    model = KNeighborsRegressor(n_neighbors=7, weights=weights)
    score = cross_val_score(model, x, y, cv=KFold(5, shuffle=True, random_state=0), scoring="r2").mean()
    print(weights.ljust(8), "weights, cross validated R2:", round(score, 3))
model = KNeighborsRegressor(n_neighbors=7).fit(x, y)
print("prediction at x = 1.6:", round(model.predict([[1.6]])[0], 3), " true sin(1.6) =", round(np.sin(1.6), 3))
