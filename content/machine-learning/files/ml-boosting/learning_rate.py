# 3.3 Boosting: small trees that fix each other
# Example "learning_rate" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_diabetes
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

X, y = load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
for lr in [1.0, 0.1, 0.01]:
    model = GradientBoostingRegressor(learning_rate=lr, n_estimators=500, max_depth=2, random_state=0).fit(X_train, y_train)
    test_err = [mean_squared_error(y_test, p) for p in model.staged_predict(X_test)]
    best = min(range(len(test_err)), key=lambda i: test_err[i])
    print("learning rate", str(lr).ljust(4), " best test MSE", round(test_err[best]), "after", best + 1, "trees",
          " MSE after 500 trees", round(test_err[-1]))
