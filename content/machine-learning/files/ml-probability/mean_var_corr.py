# 2.3 Probability and statistics for ML
# Example "mean_var_corr" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

hours = np.array([1, 2, 3, 4, 5, 6, 7, 8])
score = np.array([52, 55, 61, 64, 70, 71, 78, 95])

print("mean score:", score.mean(), " median:", np.median(score))
print("variance:", round(score.var(), 2), " std:", round(score.std(), 2))
print("sample std (ddof=1):", round(score.std(ddof=1), 2))
cov = np.mean((hours - hours.mean()) * (score - score.mean()))
corr = cov / (hours.std() * score.std())
print("covariance:", round(cov, 2), " correlation:", round(corr, 3))
print("numpy corrcoef:", round(np.corrcoef(hours, score)[0, 1], 3))
