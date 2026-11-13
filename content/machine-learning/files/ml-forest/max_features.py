# 3.2 Random forests: many trees vote
# Example "max_features" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
for mf in [1, "sqrt", 0.5, None]:
    forest = RandomForestClassifier(n_estimators=200, max_features=mf, random_state=0).fit(X_train, y_train)
    votes = np.array([tree.predict(X_test) for tree in forest.estimators_])
    agree = np.mean([np.mean(votes[i] == votes[j]) for i in range(20) for j in range(i + 1, 20)])
    print("max_features", str(mf).ljust(5), " trees agree", round(float(agree), 3), " test", round(forest.score(X_test, y_test), 3))
