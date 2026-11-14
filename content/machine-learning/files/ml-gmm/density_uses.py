# 1.3 Gaussian mixture models and EM
# Example "density_uses" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.mixture import GaussianMixture

rng = np.random.default_rng(2)
normal_days = rng.normal([50, 200], [5, 20], size=(500, 2))     # temperature and power use of a machine
gm = GaussianMixture(n_components=3, random_state=0).fit(normal_days)
threshold = np.percentile(gm.score_samples(normal_days), 1)       # lowest 1% of log density
new = np.array([[51, 205], [49, 190], [70, 210], [50, 320]])
for p, s in zip(new.tolist(), gm.score_samples(new)):
    print(p, " log density", round(float(s), 2), " unusual" if s < threshold else " normal")
fake, _ = gm.sample(3)                                            # a GMM can also generate new data
print("three generated days:", np.round(fake, 1).tolist())
