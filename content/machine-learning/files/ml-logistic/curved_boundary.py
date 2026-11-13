# 2.1 Logistic regression: probabilities for classification
# Example "curved_boundary" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import make_circles
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

X, y = make_circles(n_samples=400, noise=0.1, factor=0.5, random_state=0)
straight = LogisticRegression()
curved = make_pipeline(PolynomialFeatures(2), StandardScaler(), LogisticRegression())
print("straight boundary accuracy:", round(cross_val_score(straight, X, y, cv=5).mean(), 3))
print("with squared features:     ", round(cross_val_score(curved, X, y, cv=5).mean(), 3))
curved.fit(X, y)
names = curved[0].get_feature_names_out(["x1", "x2"])
weights = curved[-1].coef_[0]
print("biggest weights:", sorted([(n, round(float(w), 2)) for n, w in zip(names, weights)], key=lambda t: -abs(t[1]))[:2])
