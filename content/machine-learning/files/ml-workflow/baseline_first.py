# 1.2 The machine learning project: from a question to a working model
# Example "baseline_first" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

X_train = [[1.2], [3.5], [5.0], [2.2], [8.1], [4.4]]   # distance in km
y_train = [14, 22, 38, 17, 51, 29]                     # minutes
X_test = [[0.9], [6.3]]
y_test = [12, 41]

baseline = DummyRegressor(strategy="mean")    # always predicts the training average
baseline.fit(X_train, y_train)
print("baseline predicts:", baseline.predict(X_test))
print("baseline error:", round(mean_absolute_error(y_test, baseline.predict(X_test)), 2), "minutes")

model = LinearRegression()
model.fit(X_train, y_train)
print("model predicts:", model.predict(X_test).round(1))
print("model error:", round(mean_absolute_error(y_test, model.predict(X_test)), 2), "minutes")
