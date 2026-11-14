# 3.1 Decision trees: a chain of yes or no questions
# Example "regression_tree" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.tree import DecisionTreeRegressor

rng = np.random.default_rng(0)
x = np.sort(rng.uniform(0, 6, 80)).reshape(-1, 1)
y = np.sin(x).ravel() + rng.normal(0, 0.15, 80)
for depth in [1, 2, 5]:
    tree = DecisionTreeRegressor(max_depth=depth, random_state=0).fit(x, y)
    preds = tree.predict([[0.5], [1.5], [3.0], [4.7]])
    print("depth", depth, " leaves", str(tree.get_n_leaves()).rjust(2), " predictions", np.round(preds, 2).tolist())
