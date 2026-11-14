# 3.3 Explainability and fairness
# Example "fairness_audit" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A fairness audit of a loan model, by group. The model never sees the group, but a postcode score is a proxy for it.
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(42)
n = 20000
group = np.where(rng.random(n) < 0.6, 'A', 'B')
income = rng.normal(np.where(group == 'A', 55, 45), 12)            # recorded income differs between groups
postcode = rng.normal(np.where(group == 'A', 0.6, 0.4), 0.1)       # a proxy: says a lot about the group
skill = rng.normal(0, 1, n)                                         # what really drives repayment, hidden
repaid = (0.05 * (income - 50) + skill + rng.normal(0, 0.8, n) > 0).astype(int)

X = np.column_stack([income, postcode])                             # no group column
X_tr, X_te, y_tr, y_te, g_tr, g_te = train_test_split(X, repaid, group, test_size=0.5, random_state=0)
score = LogisticRegression().fit(X_tr, y_tr).predict_proba(X_te)[:, 1]


def rates(approve, y, g):
    out = {}
    for name in ['A', 'B']:
        m = g == name
        out[name] = {'selection': approve[m].mean(), 'TPR': approve[m & (y == 1)].mean(),
                     'FPR': approve[m & (y == 0)].mean(), 'base rate': y[m].mean()}
    return out


def report(title, approve):
    r = rates(approve, y_te, g_te)
    print(title, f'(accuracy {np.mean(approve == y_te):.3f})')
    for name in ['A', 'B']:
        print(f'  group {name}: repaid {r[name]["base rate"]:.2f}  approved {r[name]["selection"]:.2f}  TPR {r[name]["TPR"]:.2f}  FPR {r[name]["FPR"]:.2f}')
    print(f'  disparate impact (B approved / A approved) {r["B"]["selection"] / r["A"]["selection"]:.2f}   '
          f'equal opportunity gap (TPR A - TPR B) {r["A"]["TPR"] - r["B"]["TPR"]:+.2f}')


report('One threshold of 0.5 for everyone', score >= 0.5)

# Equal opportunity: pick group B's threshold so that its TPR matches group A's
target = rates(score >= 0.5, y_te, g_te)['A']['TPR']
pos_b = np.sort(score[(g_te == 'B') & (y_te == 1)])
t_b = pos_b[int((1 - target) * len(pos_b))]
report(f'Group B threshold lowered to {t_b:.2f} (equal opportunity)', np.where(g_te == 'A', score >= 0.5, score >= t_b))
