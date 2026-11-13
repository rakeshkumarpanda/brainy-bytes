# 3.3 Boosting: small trees that fix each other
# Example "boost_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.tree import DecisionTreeRegressor

rng = np.random.default_rng(0)
x = np.sort(rng.uniform(0, 6, 80)).reshape(-1, 1)
y = np.sin(x).ravel() + rng.normal(0, 0.15, 80)

lr = 0.3
pred = np.full(len(y), y.mean())                  # round 0: predict the average
print("round  0  mean squared error", round(float(np.mean((y - pred) ** 2)), 4))
for m in range(1, 31):
    residual = y - pred                            # what is still wrong
    stump = DecisionTreeRegressor(max_depth=1).fit(x, residual)
    pred = pred + lr * stump.predict(x)            # take a small step towards it
    if m in (1, 2, 5, 10, 30):
        print("round", str(m).rjust(2), " mean squared error", round(float(np.mean((y - pred) ** 2)), 4))
