# 3.2 Monitoring and drift
# Example "decay_sim" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Two kinds of drift over 12 months, and what retraining does.
# Concept drift: the inputs look the same but the rule linking them to the label slowly turns.
# Data drift: the inputs move but the rule stays the same.
import numpy as np
from sklearn.linear_model import LogisticRegression

rng = np.random.default_rng(1)


def month_data(month, kind, n=2000):
    X = rng.normal(0, 1, (n, 2))
    if kind == 'data':
        X[:, 0] += 0.25 * month                                       # customers change, the rule does not
    angle = np.radians(6 * month) if kind == 'concept' else 0.0       # the rule turns 6 degrees a month
    y = (X[:, 0] * np.cos(angle) + X[:, 1] * np.sin(angle) > 0).astype(int)
    flip = rng.random(n) < 0.05                                       # 5 percent label noise
    return X, np.where(flip, 1 - y, y)


def psi(ref, cur, bins=10):
    edges = np.quantile(ref, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    p = np.clip(np.histogram(ref, edges)[0] / len(ref), 1e-4, None)
    q = np.clip(np.histogram(cur, edges)[0] / len(cur), 1e-4, None)
    return float(np.sum((q - p) * np.log(q / p)))


for kind, retrain in [('concept', None), ('concept', 3), ('data', None)]:
    X0, y0 = month_data(0, kind)
    model = LogisticRegression().fit(X0, y0)
    label = f'{kind} drift, ' + ('never retrained' if retrain is None else f'retrained every {retrain} months')
    print(label)
    print('  month:   ' + ' '.join(f'{m:5d}' for m in range(0, 13, 2)))
    accs, psis = [], []
    for m in range(13):
        X, y = month_data(m, kind)
        if m % 2 == 0:
            accs.append(model.score(X, y))
            psis.append(psi(X0[:, 0], X[:, 0]))
        if retrain and m > 0 and m % retrain == 0:
            model = LogisticRegression().fit(X, y)                     # needs this month's true labels
    print('  accuracy ' + ' '.join(f'{a:5.2f}' for a in accs))
    print('  PSI x1   ' + ' '.join(f'{p:5.2f}' for p in psis))
print('Concept drift hides from input checks (PSI stays near 0) but shows in accuracy.')
print('Data drift sets off the PSI alarm, yet this model stays accurate because its rule still holds.')
