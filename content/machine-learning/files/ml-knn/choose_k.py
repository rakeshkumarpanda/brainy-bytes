# 2.2 k nearest neighbours: learn from similar examples
# Example "choose_k" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import make_moons
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier

X, y = make_moons(n_samples=300, noise=0.35, random_state=0)
for k in [1, 3, 7, 15, 31, 101]:
    model = KNeighborsClassifier(n_neighbors=k)
    train = model.fit(X, y).score(X, y)
    cv = cross_val_score(model, X, y, cv=5).mean()
    print("k =", str(k).rjust(3), " training accuracy", round(train, 3), " cross validated", round(cv, 3))
