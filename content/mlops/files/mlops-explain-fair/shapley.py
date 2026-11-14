# 3.3 Explainability and fairness
# Example "shapley" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Exact Shapley values for one prediction, by trying every order of adding the features.
# This is what the SHAP library estimates quickly for big models.
from itertools import permutations
from math import factorial

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier

rng = np.random.default_rng(0)
n = 3000
income = rng.normal(50, 15, n)                                      # thousands per year
debt = rng.uniform(0, 1, n)                                         # debt to income ratio
age = rng.integers(21, 70, n)
logit = 0.08 * (income - 50) - 4 * (debt - 0.5) + 0.02 * (age - 45)
y = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int)          # 1 = loan repaid
X = np.column_stack([income, debt, age])
names = ['income', 'debt_ratio', 'age']
model = GradientBoostingClassifier(random_state=0).fit(X, y)
background = X[rng.choice(n, 200, replace=False)]                   # stands for "a typical applicant"


def value(subset, x):
    """Average prediction when the features in subset take x's values and the rest come from the background."""
    Z = background.copy()
    for j in subset:
        Z[:, j] = x[j]
    return model.predict_proba(Z)[:, 1].mean()


def shapley(x):
    k = len(x)
    phi = np.zeros(k)
    for order in permutations(range(k)):                            # 3 features: 6 orders
        seen = []
        for j in order:
            phi[j] += value(seen + [j], x) - value(seen, x)         # what j adds when it joins
            seen.append(j)
    return phi / factorial(k)


x = np.array([38.0, 0.82, 29])                                      # one applicant
base, pred = value([], x), model.predict_proba([x])[0, 1]
phi = shapley(x)
print(f'Average prediction (base value): {base:.3f}')
for name, v, p in zip(names, x, phi):
    print(f'  {name:10s} = {v:6.2f}   contribution {p:+.3f}')
print(f'base + contributions = {base + phi.sum():.3f}   model says {pred:.3f}')
print('The contributions always add up exactly from the base value to the prediction.')
