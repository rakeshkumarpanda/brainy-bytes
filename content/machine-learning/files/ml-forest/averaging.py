# 3.2 Random forests: many trees vote
# Example "averaging" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

rng = np.random.default_rng(0)
sigma = 1.0
for rho in [0.0, 0.3, 0.7]:
    for B in [1, 10, 100]:
        shared = rng.normal(0, 1, 20000)                      # the part all trees share
        own = rng.normal(0, 1, (B, 20000))                    # each tree's own noise
        preds = np.sqrt(rho) * shared + np.sqrt(1 - rho) * own
        var = preds.mean(axis=0).var()
        theory = rho * sigma ** 2 + (1 - rho) * sigma ** 2 / B
        print("correlation", rho, " trees", str(B).rjust(3), " variance of the average", round(float(var), 3), " theory", round(theory, 3))
