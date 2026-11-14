# 4.1 Designing an ML system end to end
# Example "skew_check" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Training-serving skew: the same feature computed two different ways in training and in the live service.
import numpy as np
from sklearn.linear_model import LogisticRegression

rng = np.random.default_rng(1)
n = 20000
spend_30d = rng.gamma(2.0, 40.0, n)                                 # money spent in the last 30 days
visits_30d = rng.poisson(6, n)
missing = rng.random(n) < 0.15                                      # new customers have no spend history
churn = (rng.random(n) < 1 / (1 + np.exp(0.03 * (spend_30d - 60) + 0.25 * (visits_30d - 6)))).astype(int)


tr, te = slice(0, 15000), slice(15000, n)
FILL = np.median(spend_30d[tr][~missing[tr]])                      # learned once, from training rows only


def features_training(spend, visits, miss):
    """The data scientist's notebook: missing spend filled with the training median, spend in pounds."""
    s = np.where(miss, FILL, spend)
    return np.column_stack([s, visits])


def features_serving_buggy(spend, visits, miss):
    """The backend team's rewrite: missing spend becomes 0, and spend arrives in pence."""
    s = np.where(miss, 0.0, spend * 100)
    return np.column_stack([s, visits])


model = LogisticRegression(max_iter=1000).fit(features_training(spend_30d[tr], visits_30d[tr], missing[tr]), churn[tr])
offline = model.score(features_training(spend_30d[te], visits_30d[te], missing[te]), churn[te])
online = model.score(features_serving_buggy(spend_30d[te], visits_30d[te], missing[te]), churn[te])
print(f'offline accuracy (training features): {offline:.3f}')
print(f'online accuracy (serving features):   {online:.3f}')
p_off = model.predict_proba(features_training(spend_30d[te], visits_30d[te], missing[te]))[:, 1]
p_on = model.predict_proba(features_serving_buggy(spend_30d[te], visits_30d[te], missing[te]))[:, 1]
print(f'mean predicted churn: offline {p_off.mean():.3f}, online {p_on.mean():.3f}')
a = features_training(spend_30d[te], visits_30d[te], missing[te])
b = features_serving_buggy(spend_30d[te], visits_30d[te], missing[te])
differ = ~np.isclose(a, b).all(axis=1)
print(f'parity test (same raw rows through both paths): {differ.mean():.1%} of rows differ, so it fails before release')
print('Fix: one feature function, or a feature store, shared by training and serving.')
