# 3.1 Decision trees: a chain of yes or no questions
# Example "instability" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.tree import DecisionTreeClassifier

data = load_breast_cancer()
X, y = data.data, data.target
rng = np.random.default_rng(1)
for trial in range(5):
    idx = rng.choice(len(X), len(X), replace=True)       # a bootstrap sample
    tree = DecisionTreeClassifier(random_state=0).fit(X[idx], y[idx])
    root = tree.tree_.feature[0]
    print("sample", trial + 1, " root question:", str(data.feature_names[root]), "<=", round(float(tree.tree_.threshold[0]), 2),
          " leaves", tree.get_n_leaves())
