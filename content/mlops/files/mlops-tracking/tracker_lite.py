# 3.1 Experiment tracking and the model registry
# Example "tracker_lite" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

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
