# 2.1 Logistic regression: probabilities for classification
# Example "odds_ratio" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.linear_model import LogisticRegression

rng = np.random.default_rng(0)
n = 2000
smoker = rng.integers(0, 2, n)
age = rng.uniform(30, 70, n)
true_logit = -6 + 1.2 * smoker + 0.08 * age
sick = (rng.uniform(size=n) < 1 / (1 + np.exp(-true_logit))).astype(int)

X = np.column_stack([smoker, age])
model = LogisticRegression(C=1e6, max_iter=5000).fit(X, sick)     # almost no penalty
w_smoker, w_age = model.coef_[0]
print("weights: smoker", round(w_smoker, 3), " age", round(w_age, 3))
print("odds ratio for smoking:", round(np.exp(w_smoker), 2), " (true", round(np.exp(1.2), 2), ")")
print("odds ratio for 10 more years:", round(np.exp(10 * w_age), 2), " (true", round(np.exp(0.8), 2), ")")
