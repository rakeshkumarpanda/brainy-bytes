# 1.1 Linear regression: fit the best straight line
# Example "statsmodels_ols" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
import statsmodels.api as sm

rng = np.random.default_rng(7)
n = 100
ads = rng.uniform(0, 10, n)
noise_feature = rng.uniform(0, 10, n)              # has nothing to do with sales
sales = 5 + 2.5 * ads + rng.normal(0, 3, n)

X = sm.add_constant(np.column_stack([ads, noise_feature]))
result = sm.OLS(sales, X).fit()
print("weights:      ", np.round(result.params, 3).tolist())
print("p values:     ", np.round(result.pvalues, 4).tolist())
low, high = result.conf_int()[1]
print("95% interval for the ads weight:", round(low, 3), "to", round(high, 3))
print("R2:", round(result.rsquared, 3), " adjusted R2:", round(result.rsquared_adj, 3))
