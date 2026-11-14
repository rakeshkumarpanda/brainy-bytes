# MLOps 3.1: experiment tracking and the model registry. Checked against the MLflow 3 documentation (Tracking,
# search_runs, Model Registry, model aliases and models:/name@alias URIs, mlflow ui and mlflow server), Bergstra and
# Bengio, Random search for hyper-parameter optimization (JMLR 2012), Cawley and Talbot, On over-fitting in model
# selection (JMLR 2010), Sculley and colleagues, Hidden technical debt in machine learning systems (NeurIPS 2015), and
# Google's MLOps guide, Continuous delivery and automation pipelines in machine learning.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, term, leet_items
from mlkit import link, ossteps

chapter('mlops-tracking')
K = Kit()
K.code('tracker_lite', r'''
# A tiny experiment tracker in plain Python, to see what MLflow and similar tools store for every run:
# parameters, metrics, a fingerprint of the data, the code version and the time.
import hashlib
import json
import time

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

LOG = 'runs.jsonl'                                           # one JSON line per run
open(LOG, 'w').close()


def log_run(params, metrics, data_hash, code_version):
    run = {'id': len(open(LOG).readlines()) + 1, 'time': time.strftime('%Y-%m-%d %H:%M'),
           'params': params, 'metrics': metrics, 'data': data_hash, 'code': code_version}
    with open(LOG, 'a') as f:
        f.write(json.dumps(run) + '\n')


X, y = load_breast_cancer(return_X_y=True)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
data_hash = hashlib.sha256(X_train.tobytes() + y_train.tobytes()).hexdigest()[:12]

for C in [0.01, 0.1, 1.0, 10.0]:
    for weight in [None, 'balanced']:
        model = make_pipeline(StandardScaler(), LogisticRegression(C=C, class_weight=weight, max_iter=2000)).fit(X_train, y_train)
        auc = roc_auc_score(y_val, model.predict_proba(X_val)[:, 1])
        log_run({'C': C, 'class_weight': weight}, {'val_auc': round(auc, 4)}, data_hash, 'git:3f2a9c1')

runs = [json.loads(line) for line in open(LOG)]
print(len(runs), 'runs logged. One of them, exactly as stored:')
print(' ', json.dumps(runs[0]))
best = max(runs, key=lambda r: r['metrics']['val_auc'])
print('Best run:', best['id'], best['params'], best['metrics'])
same_data = all(r['data'] == data_hash for r in runs)
print('All runs used the same data:', same_data, '| so their scores can be compared fairly')
''', long=True)

K.code('winners_curse', r'''
# Why the best of many tracked runs looks better than it is. The labels here are pure coin flips, so every
# model is really 50 percent accurate. We still "tune" by picking the run with the best validation score.
import numpy as np

rng = np.random.default_rng(0)
n_val, n_test = 200, 200
y_val, y_test = rng.integers(0, 2, n_val), rng.integers(0, 2, n_test)

print(' runs   best validation accuracy   same model on a fresh test set')
for n_runs in [1, 10, 100, 1000]:
    best_val, best_test = -1, None
    for _ in range(n_runs):
        guess_val, guess_test = rng.integers(0, 2, n_val), rng.integers(0, 2, n_test)   # a "model" with no skill
        acc = np.mean(guess_val == y_val)
        if acc > best_val:
            best_val, best_test = acc, np.mean(guess_test == y_test)
    print(f'{n_runs:5d}   {best_val:24.3f}   {best_test:30.3f}')
print('The more runs you compare on one validation set, the more the winner flatters itself.')
print('Keep a test set that no run ever saw, and report the champion on it once.')
''', long=True)

K.code('registry_lite', r'''
# A tiny model registry: numbered versions that never change, and aliases (champion, challenger) that move.
# A challenger becomes champion only if it beats the champion on held out data by a margin. Rollback = move the alias back.
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
X_train, X_hold, y_train, y_hold = train_test_split(X, y, test_size=0.3, random_state=1, stratify=y)

registry = {'versions': {}, 'aliases': {}, 'log': []}


def register(model, description):
    v = len(registry['versions']) + 1
    auc = roc_auc_score(y_hold, model.predict_proba(X_hold)[:, 1])
    registry['versions'][v] = {'model': model, 'description': description, 'auc': round(auc, 4)}
    registry['log'].append(f'registered v{v} ({description}), holdout AUC {auc:.4f}')
    return v


def set_alias(alias, v, reason):
    registry['aliases'][alias] = v
    registry['log'].append(f'{alias} -> v{v}: {reason}')


def try_promote(v, margin=0.002):
    champ = registry['aliases'].get('champion')
    new, old = registry['versions'][v]['auc'], registry['versions'][champ]['auc'] if champ else 0
    set_alias('challenger', v, 'under evaluation')
    if new >= old + margin:
        set_alias('champion', v, f'beats v{champ} ({new:.4f} against {old:.4f})' if champ else 'first model')
    else:
        registry['log'].append(f'v{v} not promoted: {new:.4f} is not at least {old:.4f} + {margin}')


v1 = register(DecisionTreeClassifier(max_depth=2, random_state=0).fit(X_train, y_train), 'decision tree depth 2')
try_promote(v1)
v2 = register(DecisionTreeClassifier(max_depth=1, random_state=0).fit(X_train, y_train), 'decision stump depth 1')
try_promote(v2)
v3 = register(make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000)).fit(X_train, y_train), 'logistic regression C=1')
try_promote(v3)
set_alias('champion', v1, 'incident: v3 misbehaves in production, roll back')   # one line, no retraining

for line in registry['log']:
    print(line)
served = registry['versions'][registry['aliases']['champion']]
print('The service now loads champion =', served['description'])
''', long=True)

K.code('mlflow_track', r'''
# Track experiments and register models with MLflow (pip install mlflow scikit-learn).
# Every run is stored in mlflow.db and the folder mlruns next to this file. See them with:
#   mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001
import logging
import warnings

import mlflow
from mlflow import MlflowClient
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')
logging.getLogger('mlflow').setLevel(logging.ERROR)

mlflow.set_tracking_uri('sqlite:///mlflow.db')
mlflow.set_experiment('breast-cancer')

X, y = load_breast_cancer(return_X_y=True)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)

for C in [0.01, 0.1, 1.0, 10.0]:
    with mlflow.start_run(run_name=f'logreg C={C}'):
        model = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=2000)).fit(X_train, y_train)
        auc = roc_auc_score(y_val, model.predict_proba(X_val)[:, 1])
        mlflow.log_params({'model': 'logistic regression', 'C': C})
        mlflow.log_metrics({'val_auc': auc, 'val_accuracy': accuracy_score(y_val, model.predict(X_val))})
        mlflow.set_tag('data', 'sklearn breast cancer, 25 percent validation, seed 0')
        mlflow.sklearn.log_model(model, name='model', input_example=X_val[:2])

runs = mlflow.search_runs(order_by=['metrics.val_auc DESC'])
print(runs[['tags.mlflow.runName', 'params.C', 'metrics.val_auc', 'metrics.val_accuracy']].round(4).to_string(index=False))

best = runs.iloc[0]
version = mlflow.register_model(f'runs:/{best.run_id}/model', 'breast-cancer-classifier')
client = MlflowClient()
client.set_registered_model_alias('breast-cancer-classifier', 'champion', version.version)
print('Registered version', version.version, 'from run', best['tags.mlflow.runName'], 'with alias champion')

served = mlflow.sklearn.load_model('models:/breast-cancer-classifier@champion')     # what a service would load
print('Loaded models:/breast-cancer-classifier@champion, validation AUC', round(roc_auc_score(y_val, served.predict_proba(X_val)[:, 1]), 4))
''', long=True)

WHY_MLFLOW = 'It needs the mlflow package and writes a database and model files, which the browser version of Python cannot install or keep.'
UI = 'mlflow ui --backend-store-uri sqlite:///mlflow.db --port {p}'

MLF_MAC = ('<ol><li>Activate your project environment and install MLflow. It is a big package, so the install takes a minute.</li>'
           '<li>Run the program, then start the MLflow web page on port <b>5001</b>. On macOS 12 and later port 5000, the MLflow default, is taken by the AirPlay Receiver and answers 403.</li>'
           '<li>Open <code>http://127.0.0.1:5001</code>, click the breast-cancer experiment, tick the four runs and press Compare.</li></ol>'
           + term(['source .venv/bin/activate', 'pip install mlflow scikit-learn', 'python mlflow_track.py', UI.format(p=5001)], 'Terminal (macOS)'))
MLF_WIN = ('<ol><li>Activate the environment in PowerShell and install MLflow.</li>'
           '<li>If PowerShell says the word mlflow is not recognised, the Scripts folder is not on the path. <code>python -m mlflow</code> always works.</li>'
           '<li>Open <code>http://127.0.0.1:5000</code>. If Windows Defender Firewall asks, allow private networks only.</li></ol>'
           + term(['.venv\\Scripts\\Activate.ps1', 'pip install mlflow scikit-learn', 'python mlflow_track.py', 'python -m ' + UI.format(p=5000)], 'PowerShell (Windows)'))
MLF_LINUX = ('<p>The same as macOS, and port 5000 is usually free. On a shared server add <code>--host 0.0.0.0</code> only behind a login or a VPN, because the MLflow page has no password of its own.</p>'
             + term(['source .venv/bin/activate', 'pip install mlflow scikit-learn', 'python mlflow_track.py', UI.format(p=5000)], 'Terminal (Linux)'))
MLF_CHROME = ('<p>Run it in the Linux development environment and open <code>http://localhost:5000</code> in Chrome, which ChromeOS forwards from Linux. MLflow pulls in many packages, so allow about 1 GB of free Linux disk space.</p>'
              + term(['source .venv/bin/activate', 'uv pip install mlflow scikit-learn', 'python mlflow_track.py', UI.format(p=5000)], 'Terminal (ChromeOS Linux)'))

K.lesson('track', 'Experiment tracking: a record of every run', f'''
{src('MLflow documentation, Tracking. Sculley and colleagues, Hidden technical debt in machine learning systems (2015).')}
{wwh('An <b>experiment tracker</b> stores, for every training run, the <b>parameters</b> (settings such as C), the <b>metrics</b> (such as validation AUC), the <b>artifacts</b> (the model file, plots), and the context: code version, data fingerprint, time and who ran it. Runs are grouped into <b>experiments</b> and can be searched, sorted and compared.',
     'After a week of trying ideas nobody remembers which settings gave the good score, which data it used, or where the model file went. A spreadsheet of results drifts away from the real runs. A tracker records everything automatically, so any result can be found, compared and reproduced.',
     'Wrap each training run in a tracked run, log parameters before training and metrics after, save the model as an artifact, and tag the data version and the Git commit. Compare runs only when they used the same data and the same validation split.')}
{run('tracker_lite')}
{note('Each line of runs.jsonl is one complete record: settings, score, a 12 character fingerprint of the training data and the Git commit. Because every run has the same data fingerprint, their scores are comparable. MLflow stores the same facts in a database instead of a text file.', 'tip')}
{table(['What to log', 'Example', 'Why'], [
    ['Parameters', 'C = 1.0, class_weight = None', 'To know what produced the result'],
    ['Metrics', 'val_auc = 0.9952', 'To compare and rank runs'],
    ['Artifacts', 'model file, confusion matrix plot', 'To reuse the exact model later'],
    ['Data version', 'a hash of the training data, or a DVC tag', 'Scores on different data cannot be compared'],
    ['Code version', 'Git commit id', 'To rerun exactly the same code'],
    ['Environment', 'Python and package versions', 'The same code can behave differently with other versions']])}
''', kw=['experiment tracking', 'parameters', 'metrics', 'artifacts', 'run', 'experiment', 'data fingerprint', 'reproducibility'])

K.lesson('mlflow', 'MLflow on your own computer', f'''
{src('MLflow 3 documentation: Tracking quickstart, mlflow.search_runs, mlflow.sklearn.log_model, Model Registry and model aliases.')}
{wwh('<b>MLflow</b> is an open source platform for tracking runs, packaging models and keeping a model registry. Runs go into a backend store (here a SQLite file) and model files into an artifact store (here the folder mlruns). <code>mlflow ui</code> shows them in the browser.',
     'It is free, works offline on one laptop, and grows into a shared team server without changing your training code. Many cloud platforms (Databricks, Azure ML) speak the same MLflow API.',
     'Point MLflow at a store, choose an experiment, and inside <code>with mlflow.start_run()</code> log parameters, metrics and the model. Then search the runs, register the best model and give it an alias.')}
{local('mlflow_track', WHY_MLFLOW)}
{note('Four runs were logged and sorted by validation AUC. C = 1.0 won with 0.9952, was registered as version 1 of breast-cancer-classifier with the alias champion, and loading models:/breast-cancer-classifier@champion gave back exactly the same AUC.', 'exam')}
{ossteps('Install MLflow, run the program and open the MLflow page', MLF_MAC, MLF_WIN, MLF_LINUX, MLF_CHROME)}
{deep('From one laptop to a team server', '<p>A team runs one tracking server with a real database and shared artifact storage, for example <code>mlflow server --backend-store-uri postgresql://... --artifacts-destination s3://bucket/mlflow --host 0.0.0.0</code>, behind a login. Everyone sets <code>MLFLOW_TRACKING_URI</code> to its address and the training code stays the same. The MLflow project also publishes an official Docker image (ghcr.io/mlflow/mlflow) for running that server in a container (MLOps 2.3).</p>')}
''', kw=['MLflow', 'mlflow ui', 'start_run', 'log_params', 'log_metrics', 'log_model', 'search_runs', 'tracking server', 'SQLite backend'])

K.lesson('curse', 'Choosing the best run without fooling yourself', f'''
{src('Cawley and Talbot, On over-fitting in model selection and subsequent selection bias in performance evaluation (2010), and Bergstra and Bengio, Random search for hyper-parameter optimization (2012).')}
{viz('mlruns')}
{wwh('When you compare many runs on one validation set and keep the best, part of its lead is luck. This <b>selection bias</b>, also called the winner&rsquo;s curse, makes the champion&rsquo;s validation score too optimistic.',
     'Trackers make it easy to try hundreds of runs. The more you try, the larger the bias, until a model that learned nothing can look good.',
     'Keep a <b>test set</b> that no run ever sees and score only the final champion on it, once. Use cross validation for the comparison, prefer simpler settings when scores are within noise, and report how many runs you tried.')}
{run('winners_curse')}
{note('The labels are coin flips, so every model is truly 50 percent accurate. The best of 1000 runs still showed 0.615 on validation, then 0.530 on fresh test data. With 200 validation rows one standard error is 0.035, and the best of 1000 lands about three standard errors above the truth.', 'warn')}
{fxs(fx('Random search coverage', 'P(at least one of n runs in the top q) = 1 &minus; (1 &minus; q)<sup>n</sup>', '60 random runs reach the top 5 percent with 95 percent chance.', key=True),
     fx('Expected best of n noisy scores', 'about &sigma; &radic;(2 ln n) above the mean', 'With &sigma; = 0.02 and n = 100: 0.061, close to the 0.064 drop in the animation.', key=True))}
''', kw=['selection bias', "winner's curse", 'test set', 'random search', 'model selection', 'multiple comparisons'])

K.lesson('registry', 'The model registry: versions, aliases and promotion', f'''
{src('MLflow documentation, Model Registry and model aliases. Google, MLOps: Continuous delivery and automation pipelines in machine learning.')}
{viz('mlregistry')}
{wwh('A <b>model registry</b> keeps every approved model as a numbered, unchangeable <b>version</b> with its lineage (which run, data and code made it). <b>Aliases</b> such as champion and challenger are movable labels, and services load a model by alias, for example <code>models:/breast-cancer-classifier@champion</code>.',
     'Without a registry, the model in production is a file somebody copied, and nobody can say which run made it or how to go back. With versions and aliases, promotion and rollback are one recorded action, and the service code never changes.',
     'Register candidates as new versions, evaluate a challenger against the champion on the same held out data, promote only past a margin and after review, and roll back by moving the alias. Never edit a version, register a new one.')}
{run('registry_lite')}
{note('v2 (AUC 0.8844) was kept but not promoted. v3 (0.9942) beat v1 (0.9555) and became champion. After the incident, champion moved back to v1 in one line, with no retraining and no rebuild.', 'exam')}
{steps('A promotion checklist', [
    'The challenger was trained by the pipeline from tracked code and data, not by hand.',
    'It beats the champion on the same held out data by more than the noise (the gate).',
    'It passes the behaviour tests of MLOps 2.3 and a fairness check by group (MLOps 3.3).',
    'Latency and memory fit the service.',
    'A person approves, the alias moves, and the change is logged with the reason.'])}
''', kw=['model registry', 'model version', 'alias', 'champion', 'challenger', 'promotion', 'rollback', 'lineage'])

K.lesson('versus', 'Tracking tools compared', f'''
{versus('Experiment tracking tools', ['', 'MLflow', 'Weights and Biases', 'DVC', 'TensorBoard'], [
    ['Type', 'Open source platform', 'Hosted service (also self hosted)', 'Open source, Git based', 'Open source viewer'],
    ['Strength', 'Tracking, registry and model packaging in one', 'Rich dashboards and team features', 'Versions data and pipelines next to Git', 'Training curves for deep learning'],
    ['Model registry', 'Yes', 'Yes', 'Through Git tags and its studio', 'No'],
    ['Works offline', 'Yes', 'Mostly needs its server', 'Yes', 'Yes'],
    ['Best for', 'A free, standard stack', 'Teams who want polish and hosting', 'Data versioning and reproducible pipelines', 'Watching one training run']],
    'MLflow is the common free default, DVC pairs well with it for data versions, and hosted tools trade money for convenience.')}
''', kw=['MLflow vs Weights and Biases', 'DVC', 'TensorBoard'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Write down every try: the settings, the score and where the model is saved, so you can always find the best one again.</p>',
    '<p>Log parameters, metrics, artifacts, data and code versions with MLflow, compare runs fairly, and register the champion with an alias.</p>',
    '<p>Guard against selection bias with an untouched test set, gate promotions on held out data, and run a shared tracking server with lineage.</p>',
    '<p>Automate promotion in pipelines with approvals and audit logs, track data lineage end to end, and design registries that serve many models across teams.</p>')}
{grow('Keep a record of every run.',
      'Choose and register the champion fairly.',
      'Automate safe promotion and rollback.')}
''', kw=['beginner', 'expert', 'lineage', 'audit'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'An <b>experiment tracker</b> stores parameters, metrics, artifacts, data fingerprint and code version for every run.',
    '<b>MLflow</b> logs runs inside <code>mlflow.start_run()</code>, searches them with search_runs, and shows them with <code>mlflow ui</code> (port 5001 on macOS because of AirPlay).',
    'The best of many runs on one validation set is too optimistic: 0.615 against 0.530 for 1000 coin flip models. Keep an untouched <b>test set</b>.',
    'A <b>model registry</b> keeps frozen versions and movable <b>aliases</b>. Services load models:/name@champion.',
    'Promote a challenger only past a <b>gate</b> on the same held out data, and roll back by moving the alias.'],
    'Coming next: watching a model in production for drift and decay.')}
{files('Three tasks: pick the best run, decide a promotion, and work out how many random runs a search needs.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'An experiment tracker stores for each run', ['Only the final model', 'Parameters, metrics, artifacts and the data and code versions', 'Only the code', 'The user&rsquo;s password'], 1, 'Everything needed to reproduce it.', 'MLflow, W and B, DVC.')
K.quiz('e', 'In MLflow, val_auc = 0.9952 is logged as a', ['Parameter', 'Metric', 'Tag', 'Artifact'], 1, 'A measured result.', 'Parameters are settings.')
K.quiz('e', 'A model registry alias such as champion is', ['A copy of the model', 'A movable label pointing at one version', 'A metric', 'A Git branch'], 1, 'A pointer.', 'Moving it promotes or rolls back.')
K.quiz('e', 'Why log a fingerprint of the training data?', ['To compress it', 'So scores are only compared between runs on the same data', 'For speed', 'It is required by Python'], 1, 'Fair comparison.', 'Different data, different scores.')
K.quiz('m', 'On macOS, mlflow ui on port 5000 answers 403 Forbidden. Why?', ['MLflow is broken', 'AirPlay Receiver already uses port 5000', 'The database is empty', 'Python is too old'], 1, 'Port taken.', 'Use --port 5001.')
K.quiz('m', 'A service should load the production model by', ['A file path on a laptop', 'An alias such as models:/name@champion', 'The latest run', 'Retraining at start up'], 1, 'Stable address.', 'The alias moves, the code stays.')
K.quiz('m', 'Comparing 1000 runs on one validation set and keeping the best gives a score that is', ['Exact', 'Too optimistic because of selection bias', 'Too pessimistic', 'Random'], 1, 'Winner&rsquo;s curse.', 'Check on an untouched test set.')
K.quiz('m', 'A registered model version should be', ['Edited in place when fixed', 'Never changed: register a new version instead', 'Deleted after a week', 'Renamed each release'], 1, 'Immutable.', 'History stays trustworthy.')
K.quiz('m', 'Rollback with a registry means', ['Retraining the old model', 'Moving the champion alias back to the previous version', 'Restoring a backup of the database', 'Rewriting the service'], 1, 'One label.', 'No rebuild needed.')
K.quiz('h', 'Why might a challenger with 0.0001 higher AUC not be promoted?', ['Bad luck', 'The gain is within noise, so a margin gate rejects it', 'AUC cannot rise', 'Registries forbid it'], 1, 'Noise.', 'Gate on a margin larger than the standard error.')
K.quiz('h', 'Random search with 60 trials finds a setting in the top 5 percent with probability about', ['0.50', '0.95', '0.05', '1.00'], 1, '1 &minus; 0.95<sup>60</sup>.', '= 0.954.')
K.quiz('h', 'The MLflow page has no password of its own. On a shared server you should', ['Use --host 0.0.0.0 on the internet', 'Keep it behind a login, VPN or reverse proxy with authentication', 'Change the port only', 'Disable logging'], 1, 'Security.', 'Expose it only to the team.')
K.quiz('x', 'In the style of a Stanford CS329S question: training serving skew is easiest to trace when the registry stores', ['Only the model weights', 'Lineage: the run, data version and code version behind each model version', 'The model name', 'The alias history only'], 1, 'Lineage.', 'You can rebuild the exact features.')
K.quiz('x', 'In the style of a Google ML engineer exam: the best place to require human approval in an automated pipeline is', ['Before data collection', 'Before the champion alias moves to a new version', 'After users complain', 'Never'], 1, 'Promotion gate.', 'Automate training, gate releases.')

K.calc('e', 'C takes 4 values and class_weight takes 2. How many runs does the full grid log?', '8', 'Multiply.', ['4 values of C.', '2 values of class_weight.', eq('4 &times; 2 = 8 runs')], check=8)
K.calc('e', 'The best of 1000 runs scored 0.615 on validation and 0.530 on fresh test data. Size of the optimism?', '0.085', 'Subtract.', ['Validation: 0.615.', 'Test: 0.530.', eq('0.615 &minus; 0.530 = 0.085')], check=0.085)
K.calc('e', 'Champion AUC 0.9555 and challenger AUC 0.9942. Gain?', '0.0387', 'Subtract.', ['Challenger: 0.9942.', 'Champion: 0.9555.', eq('0.9942 &minus; 0.9555 = 0.0387')], check=0.0387)
K.calc('m', 'The champion has AUC 0.9943 and the gate margin is 0.002. Smallest challenger AUC that is promoted?', '0.9963', 'Champion plus margin.', ['Rule: challenger &ge; champion + margin.', '0.9943 + 0.002.', eq('0.9963')], check=0.9963)
K.calc('m', 'A grid of 5 learning rates, 4 depths and 3 subsample values, each with 5 fold cross validation. Model fits?', '300', 'Combinations times folds.', ['5 &times; 4 &times; 3 = 60 combinations.', 'Each is fitted 5 times.', eq('60 &times; 5 = 300 fits')], check=300)
K.calc('m', 'Random search: how many runs give at least 95 percent chance of one run in the top 5 percent?', '59', 'Solve 1 &minus; 0.95<sup>n</sup> &ge; 0.95.', ['0.95<sup>n</sup> &le; 0.05.', 'n &ge; ln 0.05 / ln 0.95 = 58.4.', eq('n = 59 runs')], check=59)
K.calc('m', 'The expected best of n random draws from a uniform 0 to 1 is n / (n + 1). For n = 19?', '0.95', 'Plug in.', ['n = 19.', 'n + 1 = 20.', eq('19 / 20 = 0.95')], check=0.95)
K.calc('h', 'Accuracy of a coin flip model (p = 0.5) on 200 validation rows. Standard error?', '0.0354', '&radic;(p(1 &minus; p) / n).', ['p(1 &minus; p) = 0.25.', '0.25 / 200 = 0.00125.', eq('&radic;0.00125 = 0.0354')], check=0.0354, tol=0.0005)
K.calc('h', 'You compare 20 models and want an overall 5 percent false alarm rate. Bonferroni level for each comparison?', '0.0025', 'Divide &alpha; by the number of tests.', ['&alpha; = 0.05.', '20 comparisons.', eq('0.05 / 20 = 0.0025')], check=0.0025)
K.calc('x', 'In the style of a statistics for ML exam: the best of n noisy scores sits about &sigma;&radic;(2 ln n) above the truth. &sigma; = 0.02 and n = 100?', '0.0607', 'Compute ln n first.', ['ln 100 = 4.605, so 2 ln n = 9.210.', '&radic;9.210 = 3.035.', eq('0.02 &times; 3.035 = 0.0607')], check=0.0607, tol=0.0005)

K.assign('pick_best', 'e', 'Pick the best run',
         '<p>Each run is a dict like <code>{\'id\': 3, \'metrics\': {\'val_auc\': 0.99}}</code>. Write <code>pick_best(runs, metric, higher=True)</code> that returns the id of the run with the highest value of <code>metric</code>, or the lowest when <code>higher</code> is False. Ignore runs that did not log the metric.</p>',
         """
def pick_best(runs, metric, higher=True):
    # your code here
    pass
""", [("pick_best([{'id': 1, 'metrics': {'auc': 0.9}}, {'id': 2, 'metrics': {'auc': 0.95}}], 'auc')", 2), ("pick_best([{'id': 1, 'metrics': {'loss': 0.3}}, {'id': 2, 'metrics': {'loss': 0.2}}], 'loss', False)", 2), ("pick_best([{'id': 1, 'metrics': {}}, {'id': 2, 'metrics': {'auc': 0.5}}], 'auc')", 2)],
         """
def pick_best(runs, metric, higher=True):
    scored = [r for r in runs if metric in r['metrics']]
    pick = max if higher else min
    return pick(scored, key=lambda r: r['metrics'][metric])['id']
""", 'Keep the runs that have the metric, then use max or min with a key.', '<p>mlflow.search_runs(order_by=[\'metrics.val_auc DESC\']) does the same on the server.</p>')
K.assign('should_promote', 'e', 'A promotion gate',
         '<p>Write <code>should_promote(champion, challenger, margin=0.002)</code> that returns True when the challenger&rsquo;s score is at least the champion&rsquo;s plus the margin. A champion of None means there is no champion yet, so any challenger is promoted.</p>',
         """
def should_promote(champion, challenger, margin=0.002):
    # your code here
    pass
""", [('should_promote(0.9555, 0.9942)', True), ('should_promote(0.9943, 0.9942)', False), ('should_promote(None, 0.7)', True), ('should_promote(0.9, 0.95, 0.1)', False)],
         """
def should_promote(champion, challenger, margin=0.002):
    if champion is None:
        return True
    return challenger >= champion + margin - 1e-12
""", 'Handle the empty registry first, then compare with the margin.', '<p>The tiny 1e-12 keeps a challenger that is exactly at the margin from failing because of float rounding.</p>')
K.assign('runs_needed', 'm', 'How many random runs?',
         '<p>Write <code>runs_needed(top_share, confidence)</code> that returns the smallest n with 1 &minus; (1 &minus; top_share)<sup>n</sup> &ge; confidence.</p>',
         """
def runs_needed(top_share, confidence):
    # your code here
    pass
""", [('runs_needed(0.05, 0.95)', 59), ('runs_needed(0.1, 0.9)', 22), ('runs_needed(0.5, 0.75)', 2), ('runs_needed(1.0, 0.99)', 1)],
         """
def runs_needed(top_share, confidence):
    n, miss = 1, 1 - top_share
    while 1 - miss ** n < confidence:
        n += 1
    return n
""", 'Increase n until the chance of at least one hit reaches the confidence.', '<p>The closed form is the ceiling of ln(1 &minus; confidence) / ln(1 &minus; top_share), but a loop avoids rounding traps.</p>')

K.must('Tracking', 'Every run: parameters, metrics, artifacts, data fingerprint, Git commit, environment. Compare only runs on the same data.')
K.must('MLflow', 'start_run, log_params, log_metrics, sklearn.log_model, search_runs. mlflow ui --backend-store-uri sqlite:///mlflow.db, port 5001 on macOS.')
K.must('Selection bias', 'Best of many on one validation set flatters itself (0.615 vs 0.530). Untouched test set, report once. Gap about &sigma;&radic;(2 ln n).')
K.must('Registry', 'Frozen numbered versions with lineage, movable aliases. Services load models:/name@champion.')
K.must('Promotion', 'Same held out data, margin gate above noise, behaviour and fairness tests, human approval, logged reason.')
K.must('Rollback', 'Move the alias back. No retraining, no rebuild.')

T = K.topic(
    slug='mlops-tracking', topic='mlops-tracking', step=(3, 'Operate and improve', 'mlops-s3', 'Track experiments, register model versions, watch for drift and decay, and explain and audit predictions.', 'Advanced'),
    title='Experiment tracking and the model registry', short='Tracking and registry', badge='3.1', minutes=50,
    lead='Record every training run with its parameters, metrics, data and code versions, run MLflow on your own computer, choose the champion without fooling yourself, and manage releases with a model registry of versions and aliases.',
    desc='Experiment tracking, parameters, metrics, artifacts, data fingerprint, MLflow, mlflow ui, search_runs, log_model, selection bias, winner\'s curse, random search, model registry, model version, alias, champion, challenger, promotion gate, rollback, lineage.',
    summary='Tracking runs, MLflow with per OS steps, the winner\'s curse, and a model registry with promotion and rollback.',
    keywords=['experiment tracking', 'MLflow', 'model registry', 'model alias', 'champion challenger', 'selection bias', 'random search', 'rollback', 'lineage', 'reproducibility'],
    recap='<p>Write down every run automatically, pick the winner on data it never saw, and give production a stable label that you can move forward or back in one step.</p>',
    added='2026-11-14', leet=leet_items())
