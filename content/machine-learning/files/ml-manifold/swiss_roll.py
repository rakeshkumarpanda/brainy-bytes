# 2.2 Manifold learning: t-SNE, UMAP, MDS and Isomap
# Example "swiss_roll" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from scipy.stats import spearmanr
from sklearn.datasets import make_swiss_roll
from sklearn.decomposition import PCA
from sklearn.manifold import Isomap, LocallyLinearEmbedding, SpectralEmbedding

X, t = make_swiss_roll(n_samples=800, noise=0.05, random_state=0)   # a rolled up sheet in 3D, t = position along the roll
for name, model in [("PCA", PCA(n_components=2)),
                    ("Isomap", Isomap(n_neighbors=10, n_components=2)),
                    ("LLE", LocallyLinearEmbedding(n_neighbors=12, n_components=2, random_state=0)),
                    ("Spectral", SpectralEmbedding(n_neighbors=10, n_components=2, random_state=0))]:
    Z = model.fit_transform(X)
    rho = max(abs(spearmanr(Z[:, 0], t)[0]), abs(spearmanr(Z[:, 1], t)[0]))
    print(name.ljust(8), " how well one new axis follows the roll (rank correlation):", round(float(rho), 3))
