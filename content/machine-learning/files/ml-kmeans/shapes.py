# 1.1 k-means: grouping points around centres
# Example "shapes" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs, make_moons
from sklearn.metrics import adjusted_rand_score

X1, y1 = make_moons(n_samples=300, noise=0.05, random_state=0)
X2, y2 = make_blobs(n_samples=300, centers=[[0, 0], [3, 0]], cluster_std=[0.3, 1.5], random_state=0)
for name, X, y in [("two moons", X1, y1), ("blobs of very different size", X2, y2)]:
    labels = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(X)
    print(name.ljust(28), "ARI", round(adjusted_rand_score(y, labels), 3))
