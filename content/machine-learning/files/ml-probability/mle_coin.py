# 2.3 Probability and statistics for ML
# Example "mle_coin" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

flips = [1, 0, 1, 1, 0, 1, 1, 0, 1, 1]       # 7 heads in 10 flips
heads = sum(flips)
tails = len(flips) - heads

best_p = 0
best_ll = -1e9
for p in np.arange(0.05, 1.0, 0.05):
    log_likelihood = heads * np.log(p) + tails * np.log(1 - p)
    if log_likelihood > best_ll:
        best_ll = log_likelihood
        best_p = p
print("best p on the grid:", round(best_p, 2), " formula heads / n =", heads / len(flips))
print("log likelihood there:", round(best_ll, 3))
print("negative log likelihood per flip (log loss):", round(-best_ll / len(flips), 4))

data = np.array([4.0, 6.0, 5.5, 7.0, 4.5])
print("Gaussian MLE mean:", data.mean(), " MLE variance:", round(data.var(), 3))
