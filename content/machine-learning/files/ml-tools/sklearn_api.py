# 1.3 Python tools for ML: NumPy, pandas and scikit-learn
# Example "sklearn_api" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

# hours studied, hours slept -> passed (1) or not (0)
X = [[1, 4], [2, 8], [3, 5], [5, 7], [6, 6], [8, 8]]
y = [0, 0, 0, 1, 1, 1]

scaler = StandardScaler()            # a transformer: fit learns the mean and std
scaler.fit(X)
print("learned means:", scaler.mean_.round(2))
print("first row scaled:", scaler.transform([X[0]]).round(2))

model = LogisticRegression()         # an estimator: fit learns the weights
model.fit(scaler.transform(X), y)
print("predict 4 hours study, 7 sleep:", model.predict(scaler.transform([[4, 7]])))

pipe = make_pipeline(StandardScaler(), LogisticRegression())   # both steps in one object
pipe.fit(X, y)
print("pipeline predicts:", pipe.predict([[4, 7]]), "| accuracy on training data:", pipe.score(X, y))
