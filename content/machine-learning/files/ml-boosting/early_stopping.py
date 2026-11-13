# 3.3 Boosting: small trees that fix each other
# Example "early_stopping" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
model = HistGradientBoostingClassifier(max_iter=1000, learning_rate=0.1, early_stopping=True,
                                       validation_fraction=0.2, n_iter_no_change=20, random_state=0)
model.fit(X_train, y_train)
print("trees actually built:", model.n_iter_, "of 1000 allowed")
print("test accuracy:", round(model.score(X_test, y_test), 3))
