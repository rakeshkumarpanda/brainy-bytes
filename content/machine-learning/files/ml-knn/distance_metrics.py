# 2.2 k nearest neighbours: learn from similar examples
# Example "distance_metrics" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

a = np.array([1.0, 2.0, 3.0])
b = np.array([2.0, 4.0, 6.5])

print("Euclidean (L2):", round(np.sqrt(np.sum((a - b) ** 2)), 3))
print("Manhattan (L1):", round(np.sum(np.abs(a - b)), 3))
print("Chebyshev (max):", round(np.max(np.abs(a - b)), 3))
for p in [1, 2, 3]:
    print("Minkowski p =", p, ":", round(np.sum(np.abs(a - b) ** p) ** (1 / p), 3))
print("cosine similarity:", round(cosine_similarity([a], [b])[0, 0], 4), " (same direction, so close to 1)")
