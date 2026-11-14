# 1.2 The MLOps lifecycle and reproducible projects
# Example "data_versions" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Data changes too. Version it by fingerprint, and record which data each model was trained on.
import hashlib

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)


def fingerprint(X, y):
    return hashlib.sha256(np.ascontiguousarray(X).tobytes() + np.ascontiguousarray(y).tobytes()).hexdigest()[:12]


rng = np.random.default_rng(3)
versions = {'v1 original': (X, y)}
y2 = y.copy()
flip = rng.choice(len(y), size=40, replace=False)        # v2: a labelling mistake flips 40 labels
y2[flip] = 1 - y2[flip]
versions['v2 with 40 wrong labels'] = (X, y2)
keep = rng.random(len(y)) > 0.3                           # v3: a new export loses about 30 percent of rows
versions['v3 missing rows'] = (X[keep], y[keep])

model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
for name, (Xv, yv) in versions.items():
    acc = cross_val_score(model, Xv, yv, cv=5).mean()
    print(f'{name:24s} rows {len(yv):3d}  fingerprint {fingerprint(Xv, yv)}  5 fold accuracy {acc:.3f}')
print('Same code, three data versions, three different models. Only the fingerprint tells you which one you have.')
