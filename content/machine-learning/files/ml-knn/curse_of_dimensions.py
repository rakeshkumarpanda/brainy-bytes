# 2.2 k nearest neighbours: learn from similar examples
# Example "curse_of_dimensions" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

rng = np.random.default_rng(1)
for dims in [2, 10, 100, 1000]:
    points = rng.uniform(0, 1, (500, dims))
    query = rng.uniform(0, 1, dims)
    d = np.sqrt(((points - query) ** 2).sum(axis=1))
    print("dimensions", str(dims).rjust(4), " nearest", round(d.min(), 2), " farthest", round(d.max(), 2),
          " ratio", round(d.min() / d.max(), 3))
