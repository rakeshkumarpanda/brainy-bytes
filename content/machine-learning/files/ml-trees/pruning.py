# 3.1 Decision trees: a chain of yes or no questions
# Example "pruning" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
path = DecisionTreeClassifier(random_state=0).cost_complexity_pruning_path(X_train, y_train)
alphas = path.ccp_alphas[:-1]
print("candidate alphas:", len(alphas), " from", round(float(alphas[0]), 4), "to", round(float(alphas[-1]), 4))
scores = [cross_val_score(DecisionTreeClassifier(ccp_alpha=a, random_state=0), X_train, y_train, cv=5).mean() for a in alphas]
best = float(alphas[int(np.argmax(scores))])
tree = DecisionTreeClassifier(ccp_alpha=best, random_state=0).fit(X_train, y_train)
print("best alpha:", round(best, 4), " leaves", tree.get_n_leaves(), " test accuracy", round(tree.score(X_test, y_test), 3))
