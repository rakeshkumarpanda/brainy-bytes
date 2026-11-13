# 1.1 Linear regression: fit the best straight line
# Example "diabetes_regression" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

X, y = load_diabetes(return_X_y=True, as_frame=True)
print("rows:", X.shape[0], " features:", list(X.columns))
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

model = LinearRegression().fit(X_train, y_train)
pred = model.predict(X_test)
print("test MAE: ", round(mean_absolute_error(y_test, pred), 2))
print("test RMSE:", round(mean_squared_error(y_test, pred) ** 0.5, 2))
print("test R2:  ", round(r2_score(y_test, pred), 3))
top = sorted(zip(model.coef_, X.columns), key=lambda t: -abs(t[0]))[:3]
print("largest weights:", [(name, round(float(c), 1)) for c, name in top])
