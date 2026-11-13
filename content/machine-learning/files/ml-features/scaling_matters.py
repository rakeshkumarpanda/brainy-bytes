# 3.2 Features: encoding, scaling, engineering and selection
# Example "scaling_matters" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_wine
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_wine(return_X_y=True)
print("feature ranges: smallest max", round(X.max(axis=0).min(), 2), " largest max", round(X.max(axis=0).max(), 1))

raw = cross_val_score(KNeighborsClassifier(), X, y, cv=5).mean()
scaled = cross_val_score(make_pipeline(StandardScaler(), KNeighborsClassifier()), X, y, cv=5).mean()
print("KNN accuracy without scaling:", round(raw, 3))
print("KNN accuracy with scaling:   ", round(scaled, 3))
