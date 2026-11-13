# 3.2 Random forests: many trees vote
# Example "tree_vs_forest" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import BaggingClassifier, RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
models = {
    "one decision tree": DecisionTreeClassifier(random_state=0),
    "bagging 200 trees": BaggingClassifier(DecisionTreeClassifier(), n_estimators=200, random_state=0),
    "random forest 200": RandomForestClassifier(n_estimators=200, random_state=0),
}
for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=5)
    print(name.ljust(18), "accuracy", round(scores.mean(), 3), " spread", round(scores.std(), 3))
