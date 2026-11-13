# 1.1 Linear regression: fit the best straight line
# Example "residual_check" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.linear_model import LinearRegression

rng = np.random.default_rng(1)
x = rng.uniform(1, 10, size=200)
fair = 3 * x + rng.normal(0, 1, 200)                 # same noise everywhere
growing = 3 * x + rng.normal(0, 1, 200) * x          # noise grows with x

for name, y in [("same noise", fair), ("growing noise", growing)]:
    model = LinearRegression().fit(x.reshape(-1, 1), y)
    resid = y - model.predict(x.reshape(-1, 1))
    small = resid[x < 4].std()
    big = resid[x > 7].std()
    print(name.ljust(14), "mean residual", round(resid.mean(), 3), " spread for small x", round(small, 2), " for big x", round(big, 2))
