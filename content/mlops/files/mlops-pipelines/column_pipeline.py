# 2.1 Pipelines and saving models
# Example "column_pipeline" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# One object for the whole recipe: fill gaps, scale numbers, one hot encode categories, then the model.
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

rng = np.random.default_rng(1)
n = 1000
df = pd.DataFrame({
    'tenure_months': rng.integers(1, 72, n).astype(float),
    'monthly_bill': rng.normal(60, 20, n).round(2),
    'support_calls': rng.poisson(1.5, n).astype(float),
    'plan': rng.choice(['basic', 'plus', 'premium'], n),
    'payment': rng.choice(['card', 'bank', 'cash'], n),
})
risk = -0.04 * df.tenure_months + 0.5 * df.support_calls + 0.8 * (df.plan == 'basic') + 0.02 * df.monthly_bill - 1
df['churned'] = (rng.random(n) < 1 / (1 + np.exp(-risk))).astype(int)
df.loc[rng.random(n) < 0.05, 'monthly_bill'] = np.nan       # 5 percent of bills are missing

numeric = ['tenure_months', 'monthly_bill', 'support_calls']
categorical = ['plan', 'payment']
prep = ColumnTransformer([
    ('num', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), numeric),
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical),
])
model = Pipeline([('prep', prep), ('clf', HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=0))])

X, y = df[numeric + categorical], df['churned']
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
print('5 fold ROC AUC on training data:', round(cross_val_score(model, X_tr, y_tr, cv=5, scoring='roc_auc').mean(), 3))
model.fit(X_tr, y_tr)
print('Test accuracy:', round(model.score(X_te, y_te), 3))
print('Columns after preprocessing:', list(model.named_steps['prep'].get_feature_names_out()))

new = pd.DataFrame([{'tenure_months': 3, 'monthly_bill': np.nan, 'support_calls': 4, 'plan': 'student', 'payment': 'card'}])
print('A new customer with a missing bill and an unseen plan "student":')
print('  churn probability', round(model.predict_proba(new)[0, 1], 3))
