# 2.1 Principal component analysis (PCA)
# Example "pca_pipeline" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_digits(return_X_y=True)
for k in [5, 10, 20, 30, None]:
    steps = [StandardScaler()] + ([PCA(n_components=k)] if k else []) + [LogisticRegression(max_iter=2000)]
    score = cross_val_score(make_pipeline(*steps), X, y, cv=5).mean()
    print(("PCA " + str(k) if k else "no PCA (64)").ljust(12), " accuracy", round(float(score), 3))
