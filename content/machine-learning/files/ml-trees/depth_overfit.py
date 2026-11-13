# 3.1 Decision trees: a chain of yes or no questions
# Example "depth_overfit" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
for depth in [1, 2, 3, 5, 8, None]:
    tree = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(X_train, y_train)
    print("max_depth", str(depth).rjust(4), " leaves", str(tree.get_n_leaves()).rjust(2),
          " train", round(tree.score(X_train, y_train), 3), " test", round(tree.score(X_test, y_test), 3))
