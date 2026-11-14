# 2.4 Support vector machines: the widest street
# Example "gamma_effect" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

X, y = make_moons(n_samples=300, noise=0.3, random_state=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0)
for gamma in [0.01, 0.1, 1, 10, 100]:
    model = SVC(kernel="rbf", C=1, gamma=gamma).fit(X_train, y_train)
    print("gamma", str(gamma).rjust(5), " train", round(model.score(X_train, y_train), 3),
          " test", round(model.score(X_test, y_test), 3), " support vectors", len(model.support_))
