# 1.1 What machine learning is: learning from examples
# Example "first_sklearn" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsClassifier

# Regression with scikit-learn: hours -> marks
X = [[1], [2], [3], [4], [5]]       # features: a list of rows, one row per example
y = [12, 19, 31, 38, 52]            # labels
model = LinearRegression()          # 1. choose a model
model.fit(X, y)                     # 2. learn from the examples
print("slope:", round(model.coef_[0], 2), "intercept:", round(model.intercept_, 2))
print("predict 6 hours:", round(model.predict([[6]])[0], 1))   # 3. predict

# Classification with scikit-learn: weight in grams, skin (0 smooth, 1 bumpy) -> fruit
X2 = [[150, 0], [170, 0], [130, 1], [140, 1]]
y2 = ["apple", "apple", "orange", "orange"]
clf = KNeighborsClassifier(n_neighbors=1)
clf.fit(X2, y2)
print("predict [160, 0]:", clf.predict([[160, 0]])[0])
print("predict [135, 1]:", clf.predict([[135, 1]])[0])
