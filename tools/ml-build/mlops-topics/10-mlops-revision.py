# MLOps 4.2: revision and certification practice. Pulls together chapters 1.1 to 4.1. Checked against Google Cloud,
# MLOps: continuous delivery and automation pipelines in machine learning (architecture guide) for maturity levels 0
# to 2, Google's Site Reliability Workbook (2018) chapter 5 for burn rate alerts, Mitchell and colleagues, Model cards
# for model reporting (2019), and the public product documentation of Vertex AI, Amazon SageMaker and Azure Machine
# Learning for the names of their tracking, registry, pipeline, monitoring, explainability and feature store services.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, term, show, leet_items
from mlkit import link, ossteps

chapter('mlops-revision')
K = Kit()
K.code('release_gate', r'''
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
''', long=True)

K.code('mlops_capstone', r'''
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
''', long=True)

WHY_CAP = 'It writes a project folder with a model file, a run log and a model card that you will want to open and keep, and it needs FastAPI.'
CAP_MAC = ('<ol><li>Make a fresh folder and environment for the capstone, so nothing from earlier chapters hides a missing package.</li>'
           '<li>Run the program. It creates the folder <code>capstone</code> next to itself.</li>'
           '<li>Open MODEL_CARD.md in any editor, or preview it in VS Code with Shift Command V.</li></ol>'
           + term(['mkdir ~/mlops-capstone && cd ~/mlops-capstone', 'python3 -m venv .venv && source .venv/bin/activate', 'pip install scikit-learn pandas joblib fastapi httpx',
                   'python mlops_capstone.py', 'cat capstone/MODEL_CARD.md', 'cat capstone/runs.jsonl'], 'Terminal (macOS)'))
CAP_WIN = ('<ol><li>Create the folder and environment in PowerShell. If activation is blocked, run <code>Set-ExecutionPolicy -Scope CurrentUser RemoteSigned</code> once (MLOps 1.1).</li>'
           '<li>Run the program, then read the files with <code>Get-Content</code>, or open the folder in VS Code and press Ctrl Shift V on the model card.</li></ol>'
           + term(['mkdir $HOME\\mlops-capstone; cd $HOME\\mlops-capstone', 'py -m venv .venv; .venv\\Scripts\\Activate.ps1', 'python -m pip install scikit-learn pandas joblib fastapi httpx',
                   'python mlops_capstone.py', 'Get-Content capstone\\MODEL_CARD.md', 'Get-Content capstone\\runs.jsonl'], 'PowerShell (Windows)'))
CAP_LINUX = ('<p>The same as macOS. On Debian and Ubuntu install the venv module first if <code>python3 -m venv</code> complains that ensurepip is not available.</p>'
             + term(['sudo apt install python3-venv          # Debian and Ubuntu, once', 'mkdir ~/mlops-capstone && cd ~/mlops-capstone', 'python3 -m venv .venv && source .venv/bin/activate',
                     'pip install scikit-learn pandas joblib fastapi httpx', 'python mlops_capstone.py', 'cat capstone/MODEL_CARD.md'], 'Terminal (Linux)'))
CAP_CHROME = ('<p>Run it in the Linux development environment. The capstone folder appears in the Files app under Linux files, where the Text app can open MODEL_CARD.md.</p>'
              + term(['mkdir ~/mlops-capstone && cd ~/mlops-capstone', 'python3 -m venv .venv && source .venv/bin/activate', 'uv pip install scikit-learn pandas joblib fastapi httpx',
                      'python mlops_capstone.py', 'cat capstone/MODEL_CARD.md'], 'Terminal (ChromeOS Linux)'))

K.lesson('loop', 'The whole subject in one loop', f'''
{viz('mlrecap')}
{wwh('<b>Revision</b> here means seeing each chapter as one stage of a model&rsquo;s life, and knowing the one idea, the one number and the one trap that go with it.',
     'Exams and interviews rarely ask about one chapter alone. They describe a situation, such as a model that got worse, and expect you to pick the right tool from several chapters in the right order.',
     'Walk the loop chapter by chapter, then follow the incident path. For each stage, say the idea out loud, recall the number, and name the trap in the table below.')}
{table(['Chapter', 'Key idea', 'Classic trap'], [
    ['1.1 Setup', 'A venv per project, exact versions in requirements.txt', 'Installing into the system Python, committing .venv'],
    ['1.2 Lifecycle', 'Seeds, run records, data fingerprints', 'Reporting the best seed instead of the spread'],
    ['2.1 Pipelines', 'Fit on training rows only, save one pipeline', 'Scaling or selecting features before the split'],
    ['2.2 Serving', 'Validate input, 422 for bad requests', 'Loading the model inside the request handler'],
    ['2.3 Docker, CI/CD', 'Requirements before code, gate every release', 'Running as root, testing only the code and not the model'],
    ['3.1 Tracking', 'Log every run, aliases for promotion', 'Choosing the best of many runs on the validation set and reporting that score'],
    ['3.2 Monitoring', 'PSI for size, labels for accuracy', 'Trusting KS p values on huge samples, missing concept drift'],
    ['3.3 Explain, fair', 'Permutation importance on test data, rates by group', 'Thinking that dropping the group column removes bias'],
    ['4.1 System design', 'Numbers first, safe rollout, honest A/B test', 'Stopping a test the first day p &lt; 0.05']])}
''', kw=['revision', 'MLOps lifecycle', 'exam traps', 'incident'])

K.lesson('maturity', 'MLOps maturity levels', f'''
{src('Google Cloud, MLOps: continuous delivery and automation pipelines in machine learning.')}
{viz('mlmaturity')}
{wwh('A <b>maturity level</b> describes how much of the ML lifecycle runs automatically. At <b>level 0</b> people move data and models by hand. At <b>level 1</b> an automated pipeline retrains and delivers models (continuous training). At <b>level 2</b> CI/CD also tests, builds and deploys the pipeline code itself.',
     'It gives teams a shared way to say where they are and what to build next. Exams use it to test whether you know which tool solves which bottleneck.',
     'Move from level 0 to 1 when models go stale between manual retrains. Move from 1 to 2 when many people change the pipeline code and releases of the pipeline itself become risky.')}
{table(['Level', 'What is automated', 'What starts a new model', 'Tools from this subject'], [
    ['0 Manual', 'Only serving', 'A person, often months apart', 'Notebooks, a saved model file (2.1)'],
    ['1 Pipeline automation', 'Data checks, training, validation, delivery', 'Schedule, new data or a drift alert', 'Pipelines (2.1), tracking and registry (3.1), monitoring (3.2)'],
    ['2 CI/CD automation', 'Also testing, building and deploying the pipeline', 'Also every code change', 'Docker and GitHub Actions (2.3), registry gates (3.1)']])}
{note('Level 2 is not always the goal. A small team with one model retrained monthly may be well served by level 1. Match the automation to how often the data and the code change.', 'tip')}
''', kw=['maturity level', 'level 0', 'level 1', 'level 2', 'continuous training', 'CI/CD', 'pipeline automation'])

K.lesson('gate', 'One release gate that uses every chapter', f'''
{wwh('A <b>release gate</b> is the list of checks a new model must pass before it can replace the champion: feature parity, a quality gain on the same holdout, fairness limits, drift of its scores and practical limits such as file size.',
     'Each chapter adds a check. Putting them in one gate means no model reaches users without passing all of them, and the gate&rsquo;s output is the evidence for the model card.',
     'Run the gate in CI (MLOps 2.3) on every candidate, block promotion on any FAIL, and store the report with the registered version (MLOps 3.1).')}
{run('release_gate')}
{note('Challenger 1 has the higher AUC, 0.0498 above the champion, because it uses postcode and the past labels favoured group A. The gate blocks it: the equal opportunity gap is 0.227 and the disparate impact is 0.48. Challenger 2 drops postcode, still gains 0.0125 AUC, passes all six checks and is promoted. A higher score on biased labels is not a better model.', 'exam')}
{fxs(fx('PSI', 'PSI = &Sigma; (q &minus; p) ln(q / p)', '0.1 watch, 0.25 drift (3.2).', key=True),
     fx('Little&rsquo;s law', 'workers = request rate &times; latency', 'Sizing workers and replicas (2.2, 4.1).', key=True),
     fx('Disparate impact', 'DI = rate<sub>B</sub> / rate<sub>A</sub> &ge; 0.8', 'Four fifths rule (3.3).', key=True),
     fx('Error budget and burn rate', 'budget = (1 &minus; SLO) &times; requests, burn = actual / allowed', 'A burn rate of 14.4 spends 2 percent of a 30 day budget in an hour (3.2).', key=True),
     fx('Shapley efficiency', 'f(x) = &phi;<sub>0</sub> + &Sigma; &phi;<sub>j</sub>', 'Contributions add up to the prediction (3.3).'),
     fx('A/B sample size', 'n = (z<sub>a</sub> + z<sub>b</sub>)&sup2; 2p&#772;(1 &minus; p&#772;) / &delta;&sup2;', 'Fix n before the test (4.1).'))}
''', kw=['release gate', 'promotion', 'formula sheet', 'quality gate', 'fairness gate'])

K.lesson('capstone', 'Capstone: the whole lifecycle on your computer', f'''
{wwh('The <b>capstone</b> program runs the subject end to end in one file: data with a fingerprint, a leak free pipeline, a tracked run, a registered model with a champion alias, a validated API tested with FastAPI&rsquo;s test client, a drift check and a model card.',
     'Reading about each step is not the same as wiring them together. Running the capstone on your own computer, then changing it, is the best revision for a practical exam or a take home task.',
     'Run it, read every file it writes, then try the changes listed under the panels: each one exercises a different chapter.')}
{local('mlops_capstone', WHY_CAP)}
{note('The test AUC is 0.7038 on synthetic data. The API returns 200 for a good request, 422 for a negative tenure and still 200 for the unseen plan family, because the encoder ignores unknown categories. After a 20 percent price rise the PSI of monthly_bill is 0.334, so the drift check says drift. The model card records all of it.', 'tip')}
{ossteps('Set up a fresh environment and run the capstone', CAP_MAC, CAP_WIN, CAP_LINUX, CAP_CHROME)}
{steps('Changes to try, one chapter each', [
    'Change SEED and run again: the data fingerprint and AUC change, and runs.jsonl now has two records to compare (1.2, 3.1).',
    'Train a second model with C = 0.1, save it as churn-v2.joblib and move the champion alias only if its AUC is higher (3.1).',
    'Add a test file that posts a request with a missing plan and checks for status 422 (2.2, 2.3).',
    'Write a Dockerfile for the API part, following MLOps 2.3, and run it with docker run -p 8000:8000.',
    'Change the price rise to 1.05 and see the drift verdict return to stable (3.2).'])}
''', kw=['capstone', 'end to end project', 'model card', 'TestClient', 'champion alias', 'data fingerprint'])

K.lesson('cloud', 'The same ideas on cloud platforms', f'''
{src('Public product documentation of Google Cloud Vertex AI, Amazon SageMaker and Azure Machine Learning.')}
{wwh('Cloud ML platforms offer managed versions of every tool in this subject. The names differ, but the ideas are the same ones you have practised with open source tools.',
     'Cloud certifications, such as Google Cloud&rsquo;s Professional Machine Learning Engineer, AWS&rsquo;s Machine Learning Engineer Associate and Microsoft&rsquo;s Azure Data Scientist Associate, ask you to pick the right managed service for a situation. Knowing the idea first makes the service names easy to learn.',
     'Learn the idea with the open source tool, then map it to the service of the platform you use. Exam guides and service names change, so always read the current official exam guide before you book.')}
{table(['Idea (chapter)', 'Open source here', 'Google Cloud', 'AWS', 'Azure'], [
    ['Pipelines (2.1, 2.3)', 'scikit-learn Pipeline, GitHub Actions', 'Vertex AI Pipelines', 'SageMaker Pipelines', 'Azure ML pipelines'],
    ['Serving (2.2)', 'FastAPI, Docker', 'Vertex AI endpoints', 'SageMaker endpoints', 'Azure ML online endpoints'],
    ['Tracking (3.1)', 'MLflow', 'Vertex AI Experiments', 'SageMaker with managed MLflow', 'Azure ML with MLflow'],
    ['Registry (3.1)', 'MLflow Model Registry', 'Vertex AI Model Registry', 'SageMaker Model Registry', 'Azure ML model registry'],
    ['Monitoring (3.2)', 'PSI job, cron', 'Vertex AI Model Monitoring', 'SageMaker Model Monitor', 'Azure ML model monitoring'],
    ['Explain and fairness (3.3)', 'SHAP, Fairlearn', 'Vertex Explainable AI', 'SageMaker Clarify', 'Responsible AI dashboard'],
    ['Feature store (4.1)', 'one shared feature function', 'Vertex AI Feature Store', 'SageMaker Feature Store', 'Azure ML managed feature store']])}
{note('A common exam pattern: a scenario with stale models and manual retraining, and four services to choose from. The answer is the pipeline plus monitoring service of that platform, because the problem is level 0 maturity, not the model.', 'exam')}
''', kw=['Vertex AI', 'SageMaker', 'Azure Machine Learning', 'certification', 'managed services', 'cloud MLOps'])

K.lesson('interview', 'Interview questions with model answers', f'''
{steps('Five classic MLOps interview questions', [
    '<b>Your model was great offline and poor online. Why?</b> Check training-serving skew first (feature parity test), then leakage in the offline evaluation (fitting on all rows), then a shift between the offline data and live traffic, and finally whether the offline metric matches the business goal.',
    '<b>How do you know when to retrain?</b> Monitor input PSI and the score distribution daily, accuracy when labels arrive, and the business metric. Retrain on a schedule for slow drift or on a trigger when performance drops past a limit, always through the tested pipeline and the registry gate.',
    '<b>How do you release a new model safely?</b> Shadow first, then a canary with guardrails on errors and latency, then an A/B test with a sample size fixed in advance, keeping the old version ready for a one step rollback.',
    '<b>How do you make results reproducible?</b> Pin package versions, fix seeds, fingerprint the data, track every run with code version and parameters, and build the serving image from the same requirements.',
    '<b>A regulator asks why someone was refused. What do you show?</b> The model card, the fairness audit by group, and the SHAP explanation of that decision with the background data used, plus the version and run that produced the model.'])}
{scene('A take home task in a hiring process', '<p>A company sends a CSV file and asks for a churn model served as an API, with tests and a short report, in one weekend. A strong answer is the capstone shape: a fingerprint of the data, one pipeline, a tracked run, a FastAPI service with an input contract and tests, a Dockerfile, a drift check, and a one page model card. Reviewers mostly read the tests and the report, so keep them clear.</p>')}
''', kw=['interview questions', 'take home task', 'offline online gap', 'reproducibility'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Name the stages of a model&rsquo;s life and the tool for each stage.</p>',
    '<p>Run the capstone, read its outputs, and explain each check of the release gate.</p>',
    '<p>Diagnose a failing model across chapters, place a team on the maturity levels, and map each tool to a cloud service.</p>',
    '<p>Design and defend a level 2 platform for many models and teams, with gates, monitoring and audits that regulators accept.</p>')}
{grow('Recall one idea and one number per chapter.',
      'Combine the chapters in a release gate and a capstone.',
      'Pass MLOps interviews and certification exams with confidence.')}
''', kw=['beginner', 'expert', 'MLOps platform'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Nine chapters form one loop: setup, lifecycle, pipelines, serving, Docker and CI/CD, tracking, monitoring, explainability and fairness, system design.',
    'Maturity: level 0 is manual, level 1 retrains through an automated pipeline, level 2 also tests and deploys the pipeline with CI/CD.',
    'One release gate combines parity, quality, fairness, drift and size checks. It blocked a higher AUC model that learned biased labels through postcode.',
    'The capstone wrote a run record, a registered model with an alias, a tested API, a drift report and a model card from one file.',
    'Cloud platforms rename the same ideas: Vertex AI, SageMaker and Azure ML each have pipelines, endpoints, tracking, a registry, monitoring and explainability.'],
    'You have finished the MLOps subject. Go back to any chapter through the loop above, or try the cheatsheet for a quick review before an exam.')}
{files('Three tasks: a release gate, the current champion after promotions and rollbacks, and how long an error budget lasts.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which file should you commit so others can rebuild your environment?', ['.venv', 'requirements.txt with exact versions', 'The pip cache', 'The model file only'], 1, 'Versions, not the folder.', 'MLOps 1.1.')
K.quiz('e', 'At MLOps maturity level 0', ['Everything is automated', 'People move data and models by hand and retrain rarely', 'CI/CD deploys the pipeline', 'There is no model'], 1, 'Manual process.', 'Only serving is automated.')
K.quiz('e', 'A release gate blocks a model when', ['Its file name is long', 'Any of its checks fails', 'It is trained on a laptop', 'Its AUC is above the champion'], 1, 'All checks must pass.', 'One FAIL is enough.')
K.quiz('e', 'An API receives a negative tenure. The right status code is', ['200', '422', '500', '301'], 1, 'Bad content.', 'MLOps 2.2.')
K.quiz('m', 'Level 1 maturity adds', ['A bigger GPU', 'An automated pipeline with continuous training', 'Manual handover', 'Only a Dockerfile'], 1, 'Continuous training.', 'Triggered by schedule, data or drift.')
K.quiz('m', 'Challenger 1 had a higher AUC but was blocked. Why?', ['It was too large', 'It failed the fairness checks, having learned biased labels through a proxy', 'It had drift', 'Parity failed'], 1, 'Biased labels.', 'DI 0.48, TPR gap 0.227.')
K.quiz('m', 'In the capstone the unseen plan family still got status 200 because', ['FastAPI ignores it', 'The one hot encoder uses handle_unknown=&apos;ignore&apos;', 'The plan field is optional', 'The model was retrained'], 1, 'Unknown categories.', 'MLOps 2.1.')
K.quiz('m', 'Docker builds slowly after every code change. The likely cause is', ['Too many tests', 'The code is copied before pip install, so the install layer rebuilds every time', 'The image is too small', 'Docker Desktop is old'], 1, 'Layer order.', 'MLOps 2.3.')
K.quiz('m', 'On AWS, the managed service for explainability and bias checks is', ['SageMaker Clarify', 'SageMaker Pipelines', 'SageMaker Feature Store', 'Amazon S3'], 0, 'Clarify.', 'Vertex Explainable AI on Google Cloud.')
K.quiz('h', 'Input PSI is 0.01 but accuracy fell from 0.95 to 0.57. This is', ['Data drift', 'Concept drift, visible only through labels', 'A server problem', 'Leakage'], 1, 'The rule changed.', 'MLOps 3.2.')
K.quiz('h', 'A team picks the best of 200 tracked runs by validation score and reports that score. The problem is', ['Too few runs', 'The score is optimistic because selection also picked luck', 'MLflow is wrong', 'Nothing'], 1, 'Winner&rsquo;s curse.', 'Report on an untouched test set.')
K.quiz('h', 'An A/B test is stopped on day 3 because p = 0.03. The best response is', ['Ship it', 'Keep the test running to the planned sample size, because early stopping inflates false alarms', 'Lower &alpha;', 'Switch metric'], 1, 'Peeking.', '22 percent false alarms in the simulation.')
K.quiz('x', 'In the style of a Google Cloud ML engineer exam: models go stale because retraining is manual and rare. The best fix is', ['A larger model', 'An automated training pipeline with monitoring based triggers (level 1)', 'More features', 'A new endpoint'], 1, 'Maturity, not modelling.', 'Vertex AI Pipelines plus Model Monitoring.')
K.quiz('x', 'In the style of an SRE interview: SLO 99.9 percent over 30 days. Which alert catches a fast outage without paging on small blips?', ['Any single error', 'Burn rate above 14.4 over one hour, confirmed over a short window', 'Monthly average only', 'CPU above 50 percent'], 1, 'Multiwindow burn rate.', '14.4 spends 2 percent of the budget in an hour.')

K.calc('e', 'One bin holds 20 percent of training values and 30 percent of live values. Its PSI term?', '0.0405', '(q &minus; p) ln(q / p).', ['q &minus; p = 0.3 &minus; 0.2 = 0.1.', 'ln(0.3 / 0.2) = ln 1.5 = 0.4055.', eq('0.1 &times; 0.4055 = 0.0405')], check=0.0405, tol=0.0005)
K.calc('e', 'An SLO of 99.5 percent on 200,000 requests a day. Error budget per day?', '1000', '(1 &minus; SLO) &times; requests.', ['1 &minus; 0.995 = 0.005.', 'Requests: 200,000.', eq('0.005 &times; 200,000 = 1,000 errors')], check=1000)
K.calc('e', 'Group A is approved 60 percent of the time and group B 45 percent. Disparate impact?', '0.75', 'B over A.', ['DI = 0.45 / 0.60.', '= 0.75.', eq('0.75 is below 0.8, so the four fifths rule fails')], check=0.75)
K.calc('m', 'A service gets 300 requests a second and each takes 50 ms. Workers needed by Little&rsquo;s law?', '15', 'Rate times time.', ['50 ms = 0.050 s.', 'L = &lambda; &times; W.', eq('300 &times; 0.050 = 15 workers')], check=15)
K.calc('m', 'Base value 0.30 and Shapley contributions +0.25, &minus;0.10 and +0.05. Prediction?', '0.5', 'Efficiency.', ['Sum: 0.25 &minus; 0.10 + 0.05 = 0.20.', 'Add the base value.', eq('0.30 + 0.20 = 0.50')], check=0.5)
K.calc('m', 'Scores over three seeds are 0.80, 0.84 and 0.82. Population standard deviation?', '0.0163', 'Mean, squared gaps, root.', ['Mean = 0.82.', 'Squared gaps: 0.0004, 0.0004, 0, mean 0.000267.', eq('&radic;0.000267 = 0.0163')], check=0.0163, tol=0.0005)
K.calc('m', 'You compare 10 models and want a 5 percent false alarm rate overall. Bonferroni level per comparison?', '0.005', '&alpha; / tests.', ['&alpha; = 0.05.', '10 comparisons.', eq('0.05 / 10 = 0.005')], check=0.005)
K.calc('h', 'A/B test from 10 to 12 percent conversion with z values 1.96 and 0.84. Users per group, before rounding?', '3837.68', 'p&#772; = 0.11, &delta; = 0.02.', ['(1.96 + 0.84)&sup2; = 7.84.', '2 &times; 0.11 &times; 0.89 = 0.1958, and &delta;&sup2; = 0.0004.', eq('7.84 &times; 0.1958 / 0.0004 = 3,837.68, so 3,838 users')], check=3837.68, tol=0.01)
K.calc('h', 'Peak 3,000 payments a second, one replica handles 250, target load 60 percent. Replicas?', '20', 'Usable capacity per replica first.', ['Usable: 250 &times; 0.6 = 150 per second.', '3,000 / 150 = 20.', eq('20 replicas')], check=20)
K.calc('x', 'In the style of the Google SRE workbook: a 30 day SLO window. What burn rate spends 2 percent of the budget in 1 hour?', '14.4', 'Compare with the even pace.', ['30 days = 720 hours, so an even pace spends 1/720 of the budget per hour.', '2 percent in one hour is 0.02 per hour.', eq('0.02 / (1/720) = 0.02 &times; 720 = 14.4')], check=14.4, tol=0.0005)

K.assign('gate_failures', 'm', 'A release gate',
         '<p>Write <code>gate_failures(metrics, rules)</code>. <code>metrics</code> maps a check name to its value. <code>rules</code> maps the same names to a pair (op, limit), where op is &apos;&gt;=&apos;, &apos;&lt;=&apos; or &apos;&lt;&apos;. Return the sorted list of names whose value breaks its rule. A name missing from metrics counts as a failure.</p>',
         """
def gate_failures(metrics, rules):
    # your code here
    pass
""", [("gate_failures({'auc_gain': 0.05, 'di': 0.48, 'tpr_gap': 0.23}, {'auc_gain': ('>=', 0.002), 'di': ('>=', 0.8), 'tpr_gap': ('<=', 0.1)})", ['di', 'tpr_gap']),
      ("gate_failures({'auc_gain': 0.0125, 'di': 0.87, 'psi': 0.008}, {'auc_gain': ('>=', 0.002), 'di': ('>=', 0.8), 'psi': ('<', 0.1)})", []),
      ("gate_failures({'di': 0.9}, {'di': ('>=', 0.8), 'psi': ('<', 0.1)})", ['psi']),
      ("gate_failures({'psi': 0.1}, {'psi': ('<', 0.1)})", ['psi'])],
         """
def gate_failures(metrics, rules):
    checks = {'>=': lambda v, t: v >= t, '<=': lambda v, t: v <= t, '<': lambda v, t: v < t}
    failed = []
    for name, (op, limit) in rules.items():
        if name not in metrics or not checks[op](metrics[name], limit):
            failed.append(name)
    return sorted(failed)
""", 'Keep a small dictionary from op to a comparison function, and treat a missing metric as a failure.', '<p>Failing on a missing metric is deliberate: a gate that silently skips a check it cannot compute lets unchecked models through.</p>')
K.assign('current_champion', 'm', 'Champion after promotions and rollbacks',
         '<p>Write <code>current_champion(events)</code>. Each event is either &apos;promote vN&apos; or &apos;rollback&apos;. A promotion makes vN the champion. A rollback returns to the champion before the current one. Return the champion at the end, or None if there is none.</p>',
         """
def current_champion(events):
    # your code here
    pass
""", [("current_champion(['promote v1', 'promote v3', 'rollback'])", 'v1'), ("current_champion(['promote v1'])", 'v1'), ('current_champion([])', None),
      ("current_champion(['promote v1', 'promote v2', 'promote v3', 'rollback', 'rollback'])", 'v1'), ("current_champion(['promote v1', 'rollback'])", None)],
         """
def current_champion(events):
    history = []
    for event in events:
        if event == 'rollback':
            if history:
                history.pop()
        else:
            history.append(event.split()[1])
    return history[-1] if history else None
""", 'Keep a stack of champions: push on promote, pop on rollback.', '<p>A registry keeps every version, so a rollback never needs retraining. The stack of past champions is exactly what the alias history in MLflow records.</p>')
K.assign('budget_days', 'e', 'How long an error budget lasts',
         '<p>Write <code>budget_days(slo, error_rate, window_days)</code>. The burn rate is error_rate / (1 &minus; slo). Return window_days / burn rate rounded to 2 decimals, or None when error_rate is 0.</p>',
         """
def budget_days(slo, error_rate, window_days):
    # your code here
    pass
""", [('budget_days(0.999, 0.005, 30)', 6.0), ('budget_days(0.999, 0.001, 30)', 30.0), ('budget_days(0.99, 0.02, 28)', 14.0), ('budget_days(0.999, 0, 30)', None)],
         """
def budget_days(slo, error_rate, window_days):
    if error_rate == 0:
        return None
    burn = error_rate / (1 - slo)
    return round(window_days / burn, 2)
""", 'Compute the burn rate, then divide the window by it.', '<p>A burn rate of 1 uses the budget exactly over the window. Above 1 the budget runs out early, which is what burn rate alerts watch.</p>')

K.must('The loop', 'Setup, lifecycle, pipelines, serving, Docker and CI/CD, tracking, monitoring, explain and fair, system design, then retrain.')
K.must('Maturity', 'Level 0 manual, level 1 continuous training through a pipeline, level 2 CI/CD for the pipeline itself.')
K.must('Release gate', 'Parity, quality gain on the same holdout, fairness (DI &ge; 0.8, TPR gap), score PSI, size. Any FAIL blocks promotion.')
K.must('Key numbers', 'PSI 0.1 and 0.25. DI 0.8. Burn rate 14.4 for 2 percent in an hour. Peeking 4.4 to 22 percent. Layer cache 2.2 s against 32 s.')
K.must('Capstone', 'Fingerprint, pipeline, tracked run, alias, tested API (200, 422), drift check, model card.')
K.must('Cloud mapping', 'Pipelines, endpoints, tracking, registry, monitoring, explainability and feature store exist on Vertex AI, SageMaker and Azure ML under their own names.')

T = K.topic(
    slug='mlops-revision', topic='mlops-revision', step=(4, 'Design and certify', 'mlops-s4', 'Design a complete ML system from requirements to rollout, and revise every MLOps chapter for interviews and certification exams.', 'Expert'),
    title='MLOps revision and certification practice', short='Revision and practice', badge='4.2', minutes=50,
    lead='Revise the whole subject as one loop, place teams on the MLOps maturity levels, combine every chapter in one release gate, run a capstone project on your own computer, map each tool to Google Cloud, AWS and Azure, and practise interview and exam questions.',
    desc='MLOps revision, lifecycle loop, maturity levels 0 1 2, continuous training, release gate, formula sheet, capstone project, model card, Vertex AI, SageMaker, Azure Machine Learning, certification practice, interview questions, burn rate alerts, champion rollback.',
    summary='The whole subject as one loop, maturity levels, a release gate across all chapters, a capstone, cloud service mapping and exam practice.',
    keywords=['MLOps revision', 'maturity levels', 'release gate', 'capstone', 'certification', 'Vertex AI', 'SageMaker', 'Azure ML', 'interview'],
    recap='<p>Every chapter is one stage of a model&rsquo;s life. Combine them in a gate and a capstone, and you can answer scenario questions in interviews and exams.</p>',
    added='2026-11-14', leet=leet_items())
