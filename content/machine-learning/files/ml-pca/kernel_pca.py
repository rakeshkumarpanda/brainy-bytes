# 2.1 Principal component analysis (PCA)
# Example "kernel_pca" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import make_circles
from sklearn.decomposition import PCA, KernelPCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

X, y = make_circles(n_samples=400, factor=0.3, noise=0.05, random_state=0)
for name, model in [("PCA", PCA(n_components=1)),
                    ("kernel PCA gamma 2", KernelPCA(n_components=1, kernel="rbf", gamma=2)),
                    ("kernel PCA gamma 15", KernelPCA(n_components=1, kernel="rbf", gamma=15))]:
    Z = model.fit_transform(X)                     # keep only one number per point
    acc = cross_val_score(LogisticRegression(), Z, y, cv=5).mean()
    print(name.ljust(19), " accuracy from one component", round(float(acc), 3))
