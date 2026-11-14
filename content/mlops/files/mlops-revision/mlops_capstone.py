# 4.2 MLOps revision and certification practice
# Example "mlops_capstone" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# The whole MLOps subject in one program: a reproducible pipeline, a tracked run, a registry with an alias,
# a tested API, a drift check and a model card. Everything is written to the folder capstone/ next to this file.
#   pip install scikit-learn pandas joblib fastapi httpx
import hashlib
import json
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEED = 42
HERE = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
ROOT = HERE / 'capstone'
(ROOT / 'models').mkdir(parents=True, exist_ok=True)

# 1. Data with a fingerprint (MLOps 1.2)
rng = np.random.default_rng(SEED)
n = 4000
df = pd.DataFrame({'tenure_months': rng.integers(1, 72, n).astype(float),
                   'monthly_bill': rng.normal(60, 20, n).round(2),
                   'plan': rng.choice(['basic', 'plus', 'pro'], n, p=[0.5, 0.35, 0.15])})
df.loc[rng.random(n) < 0.05, 'monthly_bill'] = np.nan                # some bills are missing
logit = -0.04 * (df.tenure_months - 30) + 0.02 * (df.monthly_bill.fillna(60) - 60) + df.plan.map({'basic': 0.4, 'plus': 0, 'pro': -0.6})
df['churn'] = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
fingerprint = hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()[:12]

# 2. One leak free pipeline (MLOps 2.1)
X, y = df.drop(columns='churn'), df.churn
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=SEED, stratify=y)
prep = ColumnTransformer([('num', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), ['tenure_months', 'monthly_bill']),
                          ('cat', OneHotEncoder(handle_unknown='ignore'), ['plan'])])
pipe = Pipeline([('prep', prep), ('model', LogisticRegression(C=1.0, max_iter=1000))]).fit(X_tr, y_tr)
auc = roc_auc_score(y_te, pipe.predict_proba(X_te)[:, 1])

# 3. Track the run and register version 1 with the alias champion (MLOps 3.1)
run = {'params': {'C': 1.0, 'seed': SEED}, 'metrics': {'test_auc': round(auc, 4)}, 'data': fingerprint,
       'versions': {'sklearn': sklearn.__version__, 'pandas': pd.__version__}}
with open(ROOT / 'runs.jsonl', 'a') as f:
    f.write(json.dumps(run) + '\n')
joblib.dump(pipe, ROOT / 'models' / 'churn-v1.joblib')
(ROOT / 'models' / 'aliases.json').write_text(json.dumps({'champion': 'churn-v1.joblib'}))
print(f'1-3  data {fingerprint}, test AUC {auc:.4f}, registered churn-v1 as champion')

# 4. Serve it with an input contract and test the API (MLOps 2.2 and 2.3)
champion = joblib.load(ROOT / 'models' / json.loads((ROOT / 'models' / 'aliases.json').read_text())['champion'])
app = FastAPI()


class Customer(BaseModel):
    tenure_months: float = Field(ge=0, le=600)
    monthly_bill: float | None = Field(default=None, ge=0)
    plan: str


@app.post('/predict')
def predict(c: Customer):
    p = champion.predict_proba(pd.DataFrame([c.model_dump()]))[0, 1]
    return {'churn_probability': round(float(p), 4), 'model': 'churn-v1'}


client = TestClient(app)
ok = client.post('/predict', json={'tenure_months': 3, 'monthly_bill': 95.0, 'plan': 'basic'})
bad = client.post('/predict', json={'tenure_months': -5, 'plan': 'basic'})
new_plan = client.post('/predict', json={'tenure_months': 40, 'monthly_bill': None, 'plan': 'family'})
print(f'4    POST /predict {ok.status_code} {ok.json()}   bad input {bad.status_code}   unseen plan {new_plan.status_code}')

# 5. Drift check on this month's data (MLOps 3.2)
def psi(a, b, bins=10):
    edges = np.quantile(a, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    p = np.clip(np.histogram(a, edges)[0] / len(a), 1e-4, None)
    q = np.clip(np.histogram(b, edges)[0] / len(b), 1e-4, None)
    return float(np.sum((q - p) * np.log(q / p)))


month = X_te.copy()
month['monthly_bill'] = month.monthly_bill * 1.20                    # a 20 percent price rise
drift = {col: round(psi(X_tr[col].dropna(), month[col].dropna()), 3) for col in ['tenure_months', 'monthly_bill']}
verdict = {c: 'stable' if v < 0.1 else ('watch' if v < 0.25 else 'drift') for c, v in drift.items()}
print(f'5    PSI this month: {drift} -> {verdict}')

# 6. A model card next to the model (MLOps 3.3)
card = f"""# Model card: churn-v1

- Date: {date.today().isoformat()}
- Intended use: rank customers for a retention offer. Not for changing prices or refusing service.
- Training data: {len(X_tr)} customers, fingerprint {fingerprint}
- Model: scikit-learn {sklearn.__version__} pipeline (median impute, scale, one hot encode, logistic regression C=1.0)
- Test AUC: {auc:.4f} on {len(X_te)} held out customers
- Inputs: tenure_months (0 to 600), monthly_bill (may be missing), plan (unknown plans are allowed)
- Monitoring: PSI per feature every month, investigate above 0.25. Latest: {drift}
- Limits: synthetic data for teaching, not tested on business customers
"""
(ROOT / 'MODEL_CARD.md').write_text(card)
print('6    wrote', ', '.join(sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file())))
