# 2.3 Probability and statistics for ML
# Example "ab_test" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from scipy import stats

clicks_a, users_a = 120, 2400     # old page
clicks_b, users_b = 156, 2400     # new page
pa = clicks_a / users_a
pb = clicks_b / users_b
pooled = (clicks_a + clicks_b) / (users_a + users_b)
se = np.sqrt(pooled * (1 - pooled) * (1 / users_a + 1 / users_b))
z = (pb - pa) / se
p_value = 2 * (1 - stats.norm.cdf(abs(z)))
print("rate A:", pa, " rate B:", pb)
print("z =", round(z, 3), " p value =", round(p_value, 4))
print("significant at 5%:", p_value < 0.05)

se_diff = np.sqrt(pa * (1 - pa) / users_a + pb * (1 - pb) / users_b)
low = (pb - pa) - 1.96 * se_diff
high = (pb - pa) + 1.96 * se_diff
print("95% confidence interval for B - A:", round(low, 4), "to", round(high, 4))
