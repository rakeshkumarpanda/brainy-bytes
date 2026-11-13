# 2.2 Manifold learning: t-SNE, UMAP, MDS and Isomap
# Example "perplexity_sigma" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# How t-SNE turns one point's distances into neighbour probabilities with a chosen perplexity
d2 = np.array([1.0, 1.2, 1.5, 4.0, 9.0, 16.0, 25.0])     # squared distances to 7 other points
target = 3.0                                              # "about 3 effective neighbours"
lo, hi = 1e-3, 1e3
for step in range(50):                                    # binary search for the width sigma
    sigma = (lo + hi) / 2
    p = np.exp(-d2 / (2 * sigma ** 2))
    p = p / p.sum()
    perp = 2 ** (-(p * np.log2(p + 1e-300)).sum())        # perplexity = 2 to the entropy
    if perp > target:
        hi = sigma
    else:
        lo = sigma
print("sigma", round(float(sigma), 3), " perplexity", round(float(perp), 3))
print("neighbour probabilities:", np.round(p, 3).tolist())
