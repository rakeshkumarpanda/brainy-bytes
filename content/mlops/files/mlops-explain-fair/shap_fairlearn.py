# 3.3 Explainability and fairness
# Example "shap_fairlearn" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# The same two checks with the standard libraries: SHAP for explanations, Fairlearn for a fairness audit.
# Install first:  pip install shap fairlearn scikit-learn
import numpy as np
import pandas as pd
import shap
from fairlearn.metrics import MetricFrame, demographic_parity_ratio, equal_opportunity_difference, selection_rate
from fairlearn.postprocessing import ThresholdOptimizer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(42)
n = 20000
group = np.where(rng.random(n) < 0.6, 'A', 'B')
income = rng.normal(np.where(group == 'A', 55, 45), 12)
postcode = rng.normal(np.where(group == 'A', 0.6, 0.4), 0.1)
debt = rng.uniform(0, 1, n)
skill = rng.normal(0, 1, n)
repaid = (0.05 * (income - 50) - 1.5 * (debt - 0.5) + skill + rng.normal(0, 0.8, n) > 0).astype(int)
X = np.column_stack([income, postcode, debt])
names = ['income', 'postcode', 'debt_ratio']
X_tr, X_te, y_tr, y_te, g_tr, g_te = train_test_split(X, repaid, group, test_size=0.5, random_state=0)
g_tr, g_te = pd.Series(g_tr, name='group'), pd.Series(g_te, name='group')
model = GradientBoostingClassifier(random_state=0).fit(X_tr, y_tr)

# 1. SHAP: TreeExplainer computes exact Shapley values for tree models in milliseconds
explainer = shap.TreeExplainer(model)
sv = explainer(X_te[:1000])                                        # values are in log odds for this model
print('Mean |SHAP| per feature (global importance, log odds):')
for name, v in sorted(zip(names, np.abs(sv.values).mean(axis=0)), key=lambda t: -t[1]):
    print(f'  {name:10s} {v:.3f}')
row = sv[0]
print('First applicant: base', round(float(row.base_values), 3), '+',
      ' + '.join(f'{name} {v:+.3f}' for name, v in zip(names, row.values)),
      '=', round(float(row.base_values + row.values.sum()), 3),
      ' model log odds', round(float(model.decision_function(X_te[:1])[0]), 3))

# 2. Fairlearn: metrics by group, then a post-processing fix with one threshold per group
pred = model.predict(X_te)
frame = MetricFrame(metrics={'accuracy': accuracy_score, 'selection': selection_rate, 'TPR': recall_score},
                    y_true=y_te, y_pred=pred, sensitive_features=g_te)
print(frame.by_group.round(3))
print('overall accuracy', round(accuracy_score(y_te, pred), 3))
print('demographic parity ratio', round(demographic_parity_ratio(y_te, pred, sensitive_features=g_te), 3),
      '  equal opportunity difference', round(equal_opportunity_difference(y_te, pred, sensitive_features=g_te), 3))

fixer = ThresholdOptimizer(estimator=model, constraints='true_positive_rate_parity', prefit=True, predict_method='predict_proba')
fixer.fit(X_tr, y_tr, sensitive_features=g_tr)
fair = fixer.predict(X_te, sensitive_features=g_te, random_state=0)
print('After ThresholdOptimizer: accuracy', round(accuracy_score(y_te, fair), 3),
      '  equal opportunity difference', round(equal_opportunity_difference(y_te, fair, sensitive_features=g_te), 3))
