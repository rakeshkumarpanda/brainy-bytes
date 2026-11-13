# 1.2 Polynomial regression and regularisation: ridge, lasso, elastic net
# Example "choose_alpha" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_diabetes
from sklearn.linear_model import LassoCV, LinearRegression, RidgeCV
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

X, y = load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

def poly(model):
    return make_pipeline(PolynomialFeatures(2), StandardScaler(), model)

plain = poly(LinearRegression()).fit(X_train, y_train)
ridge = poly(RidgeCV(alphas=[0.1, 1, 10, 100, 1000])).fit(X_train, y_train)
lasso = poly(LassoCV(cv=5, random_state=0, max_iter=20000)).fit(X_train, y_train)
print("65 polynomial features")
print("plain    test R2:", round(plain.score(X_test, y_test), 3))
print("RidgeCV  test R2:", round(ridge.score(X_test, y_test), 3), " best alpha:", ridge[-1].alpha_)
print("LassoCV  test R2:", round(lasso.score(X_test, y_test), 3), " best alpha:", round(lasso[-1].alpha_, 3),
      " features kept:", int((lasso[-1].coef_ != 0).sum()))
