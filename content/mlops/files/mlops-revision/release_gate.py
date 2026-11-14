# 4.2 MLOps revision and certification practice
# Example "release_gate" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A release gate that combines the checks of the whole MLOps subject before a new model may replace the champion.
import io
import pickle

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

rng = np.random.default_rng(5)
n = 12000
group = np.where(rng.random(n) < 0.6, 'A', 'B')
income = rng.normal(np.where(group == 'A', 52, 48), 12)
debt = rng.uniform(0, 1, n)
history = rng.poisson(4, n)                                         # years of credit history
postcode = rng.normal(np.where(group == 'A', 0.7, 0.3), 0.1)        # a strong proxy for the group
bias = 2.0 * (postcode - 0.5)                                      # past decisions favoured group A, and labels kept that
y = (0.05 * (income - 50) - 2.0 * (debt - 0.5) + 0.15 * (history - 4) + bias + rng.normal(0, 1, n) > 0).astype(int)


def features(income, debt, history, postcode=None):
    """One feature function shared by training and serving (MLOps 4.1)."""
    cols = [income / 100, debt, np.log1p(history)]
    return np.column_stack(cols if postcode is None else cols + [postcode])


tr, te = slice(0, 8000), slice(8000, n)
champion = LogisticRegression().fit(features(income, debt, history)[tr][:, :2], y[tr])
champ_auc = roc_auc_score(y[te], champion.predict_proba(features(income, debt, history)[te][:, :2])[:, 1])


def psi(a, b, bins=10):
    edges = np.quantile(a, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    p = np.clip(np.histogram(a, edges)[0] / len(a), 1e-4, None)
    q = np.clip(np.histogram(b, edges)[0] / len(b), 1e-4, None)
    return float(np.sum((q - p) * np.log(q / p)))


def gate(name, use_postcode):
    X = features(income, debt, history, postcode if use_postcode else None)
    model = GradientBoostingClassifier(random_state=0).fit(X[tr], y[tr])
    score = model.predict_proba(X[te])[:, 1]
    approve, g, yt = score >= 0.5, group[te], y[te]
    tpr = {k: approve[(g == k) & (yt == 1)].mean() for k in 'AB'}
    sel = {k: approve[g == k].mean() for k in 'AB'}
    serve = model.predict_proba(features(income[te], debt[te], history[te], postcode[te] if use_postcode else None))[:, 1]
    live = model.predict_proba(features(income[te] * 1.03, debt[te], history[te], postcode[te] if use_postcode else None))[:, 1]
    checks = [
        ('training-serving parity', np.abs(score - serve).max(), lambda v: v < 1e-12, 'max difference 0'),
        ('AUC beats champion', roc_auc_score(yt, score) - champ_auc, lambda v: v >= 0.002, 'gain at least 0.002'),
        ('equal opportunity gap', abs(tpr['A'] - tpr['B']), lambda v: v <= 0.10, 'at most 0.10'),
        ('disparate impact', sel['B'] / sel['A'], lambda v: v >= 0.8, 'at least 0.8'),
        ('score PSI on last week', psi(score, live), lambda v: v < 0.1, 'below 0.1'),
        ('model file size MB', len(pickle.dumps(model)) / 1e6, lambda v: v < 50, 'below 50'),
    ]
    print(f'{name}  (champion AUC {champ_auc:.4f})')
    ok = True
    for label, value, rule, text in checks:
        passed = bool(rule(value))
        ok &= passed
        print(f'  {"PASS" if passed else "FAIL"}  {label:24s} {value:8.4f}   rule: {text}')
    print('  ->', 'promote to champion' if ok else 'blocked, champion stays')


gate('challenger 1: boosting with postcode', True)
gate('challenger 2: boosting without postcode', False)
