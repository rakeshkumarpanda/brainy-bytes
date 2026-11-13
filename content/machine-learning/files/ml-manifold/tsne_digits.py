# 2.2 Manifold learning: t-SNE, UMAP, MDS and Isomap
# Example "tsne_digits" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, trustworthiness
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier

X, y = load_digits(return_X_y=True)
X, y = X[:600], y[:600]                                  # 600 images keep it quick in the browser
for name, Z in [("PCA", PCA(n_components=2).fit_transform(X)),
                ("t-SNE", TSNE(n_components=2, perplexity=30, init="pca", random_state=0).fit_transform(X))]:
    acc = cross_val_score(KNeighborsClassifier(5), Z, y, cv=5).mean()
    print(name.ljust(5), " 5 nearest neighbours accuracy in 2D", round(float(acc), 3), "  trustworthiness", round(float(trustworthiness(X, Z, n_neighbors=5)), 3))
