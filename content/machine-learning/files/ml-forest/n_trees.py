# 3.2 Random forests: many trees vote
# Example "n_trees" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
for n in [1, 5, 20, 100, 300]:
    forest = RandomForestClassifier(n_estimators=n, random_state=0).fit(X_train, y_train)
    print("trees", str(n).rjust(3), " train", round(forest.score(X_train, y_train), 3), " test", round(forest.score(X_test, y_test), 3))
