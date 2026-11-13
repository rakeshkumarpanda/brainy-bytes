# 3.1 Decision trees: a chain of yes or no questions
# Example "importance" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

data = load_breast_cancer()
rng = np.random.default_rng(0)
X = np.column_stack([data.data, rng.normal(size=len(data.data))])   # last column is pure noise
names = list(data.feature_names) + ["random noise"]
X_train, X_test, y_train, y_test = train_test_split(X, data.target, test_size=0.3, random_state=0)
tree = DecisionTreeClassifier(random_state=0).fit(X_train, y_train)
top = np.argsort(tree.feature_importances_)[::-1][:3]
print("top impurity importances:", [(str(names[i]), round(float(tree.feature_importances_[i]), 3)) for i in top])
print("impurity importance of noise:", round(float(tree.feature_importances_[-1]), 3))
perm = permutation_importance(tree, X_test, y_test, n_repeats=10, random_state=0)
print("permutation importance of noise:", round(float(perm.importances_mean[-1]), 3))
