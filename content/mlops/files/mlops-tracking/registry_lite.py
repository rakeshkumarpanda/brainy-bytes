# 3.1 Experiment tracking and the model registry
# Example "registry_lite" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

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
