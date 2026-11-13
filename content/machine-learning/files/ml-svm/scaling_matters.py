# 2.4 Support vector machines: the widest street
# Example "scaling_matters" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
print("feature maximums go from", round(float(X.max(axis=0).min()), 3), "to", round(float(X.max(axis=0).max()), 1))
raw = cross_val_score(SVC(kernel="rbf"), X, y, cv=5).mean()
scaled = cross_val_score(make_pipeline(StandardScaler(), SVC(kernel="rbf")), X, y, cv=5).mean()
print("without scaling:", round(raw, 3))
print("with StandardScaler:", round(scaled, 3))
