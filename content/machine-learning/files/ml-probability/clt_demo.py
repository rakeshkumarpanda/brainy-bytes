# 2.3 Probability and statistics for ML
# Example "clt_demo" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

rng = np.random.default_rng(1)
for n in [1, 4, 16, 64]:
    rolls = rng.integers(1, 7, size=(20000, n))   # 20000 groups of n dice
    means = rolls.mean(axis=1)
    print("n =", n, " mean of means", round(means.mean(), 3), " std of means", round(means.std(), 3),
          " theory", round(1.7078 / np.sqrt(n), 3))
