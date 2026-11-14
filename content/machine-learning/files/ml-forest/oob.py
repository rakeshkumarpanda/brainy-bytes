# 3.2 Random forests: many trees vote
# Example "oob" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
forest = RandomForestClassifier(n_estimators=300, oob_score=True, random_state=0).fit(X_train, y_train)
print("out of bag accuracy:", round(forest.oob_score_, 3))
print("test accuracy:", round(forest.score(X_test, y_test), 3))
