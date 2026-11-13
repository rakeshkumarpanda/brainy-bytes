# 2.3 Probability and statistics for ML
# Example "distributions" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from scipy import stats

rng = np.random.default_rng(0)
n = 100000

coin = rng.binomial(1, 0.3, size=n)            # Bernoulli: one yes or no
print("Bernoulli p=0.3   mean", round(coin.mean(), 3), " var", round(coin.var(), 3), " theory 0.3 and 0.21")

heads = rng.binomial(10, 0.5, size=n)          # Binomial: heads in 10 flips
print("Binomial 10, 0.5  mean", round(heads.mean(), 3), " var", round(heads.var(), 3), " theory 5 and 2.5")

calls = rng.poisson(4, size=n)                 # Poisson: calls per hour
print("Poisson rate 4    mean", round(calls.mean(), 3), " var", round(calls.var(), 3), " theory 4 and 4")

height = rng.normal(170, 8, size=n)            # Normal: heights in cm
print("Normal 170, 8     mean", round(height.mean(), 2), " std", round(height.std(), 2))

print("P(exactly 5 heads in 10) =", round(stats.binom.pmf(5, 10, 0.5), 4))
print("P(height below 186) =", round(stats.norm.cdf(186, 170, 8), 4))
print("share within 1, 2, 3 std:", [round(float(np.mean(abs(height - 170) < k * 8)), 3) for k in (1, 2, 3)])
