# 2.2 Manifold learning: t-SNE, UMAP, MDS and Isomap
# Example "perplexity" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_digits
from sklearn.manifold import TSNE, trustworthiness
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier

X, y = load_digits(return_X_y=True)
X, y = X[:400], y[:400]
for perp in [2, 10, 30, 100]:
    Z = TSNE(n_components=2, perplexity=perp, init="pca", random_state=0).fit_transform(X)
    acc = cross_val_score(KNeighborsClassifier(5), Z, y, cv=5).mean()
    print("perplexity", str(perp).rjust(3), " kNN accuracy", round(float(acc), 3), " trustworthiness", round(float(trustworthiness(X, Z, n_neighbors=10)), 3))
