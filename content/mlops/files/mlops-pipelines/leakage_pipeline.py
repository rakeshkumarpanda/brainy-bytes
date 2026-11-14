# 2.1 Pipelines and saving models
# Example "leakage_pipeline" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Data leakage: choosing features with ALL the data before cross validation makes pure noise look predictive.
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline

rng = np.random.default_rng(0)
X = rng.normal(size=(100, 5000))          # 100 rows of pure noise, 5000 columns
y = rng.integers(0, 2, size=100)          # random labels: the honest accuracy is 50 percent

# Wrong: pick the 20 columns most related to y using every row, then cross validate
X_picked = SelectKBest(f_classif, k=20).fit_transform(X, y)
wrong = cross_val_score(LogisticRegression(max_iter=1000), X_picked, y, cv=5).mean()

# Right: the selection is a step of the pipeline, so each fold picks columns from its own training rows only
pipe = make_pipeline(SelectKBest(f_classif, k=20), LogisticRegression(max_iter=1000))
right = cross_val_score(pipe, X, y, cv=5).mean()

print(f'Selection before cross validation (leak): accuracy {wrong:.2f}')
print(f'Selection inside the pipeline (honest):   accuracy {right:.2f}')
