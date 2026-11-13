# 4.2 Validation: honest estimates of performance
# Example "three_way" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
X_rest, X_test, y_rest, y_test = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_rest, y_rest, test_size=0.25, random_state=0, stratify=y_rest)
print("train", len(X_train), " validation", len(X_val), " test", len(X_test))

best_k, best_score = None, 0.0
for k in [1, 3, 5, 9, 15, 25]:
    model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k)).fit(X_train, y_train)
    score = model.score(X_val, y_val)
    print("k", str(k).rjust(2), " validation accuracy", round(score, 3))
    if score > best_score:
        best_k, best_score = k, score
final = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=best_k)).fit(X_rest, y_rest)
print("chosen k =", best_k, " test accuracy, measured once:", round(final.score(X_test, y_test), 3))
