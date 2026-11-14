# 1.2 The MLOps lifecycle and reproducible projects
# Example "run_record" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A run record: everything needed to explain, repeat or roll back one training run.
import hashlib
import json
import platform
from importlib.metadata import version

import numpy as np
from sklearn.datasets import load_wine
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_wine(return_X_y=True)
params = {'C': 0.5, 'max_iter': 500, 'test_size': 0.25, 'seed': 7}


def fingerprint(*arrays):
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()[:12]


X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=params['test_size'], random_state=params['seed'], stratify=y)
model = make_pipeline(StandardScaler(), LogisticRegression(C=params['C'], max_iter=params['max_iter']))
model.fit(X_tr, y_tr)

record = {
    'data': {'rows': len(X), 'features': X.shape[1], 'fingerprint': fingerprint(X, y)},
    'params': params,
    'metrics': {'train_accuracy': round(model.score(X_tr, y_tr), 4), 'test_accuracy': round(model.score(X_te, y_te), 4)},
    'environment': {'python': platform.python_version(), 'numpy': version('numpy'), 'scikit-learn': version('scikit-learn')},
}
print(json.dumps(record, indent=2))
