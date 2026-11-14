# 2.3 Docker and CI/CD for models
# Example "model_tests" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Tests for a model, not only for code. Four kinds that CI can run on every push:
# a quality gate, known examples, invariance and a directional check. Run: python model_tests.py
import numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)


def train(labels):
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(X_train, labels)


def run_tests(model):
    results = {}
    results['accuracy gate (at least 0.90)'] = model.score(X_test, y_test) >= 0.90
    known = [([5.0, 3.4, 1.5, 0.2], 0), ([6.9, 3.1, 5.4, 2.1], 2)]             # flowers everyone agrees on
    results['known examples'] = all(model.predict([x])[0] == want for x, want in known)
    rng = np.random.default_rng(0)
    noisy = X_test + rng.normal(0, 0.02, X_test.shape)                          # tiny measuring noise
    results['invariance to tiny noise'] = (model.predict(noisy) == model.predict(X_test)).mean() >= 0.95
    small, large = [6.0, 3.0, 4.0, 1.2], [6.0, 3.0, 6.0, 2.2]
    results['longer petals raise P(virginica)'] = model.predict_proba([large])[0][2] > model.predict_proba([small])[0][2]
    return results


good = train(y_train)
print('Good model, test accuracy', round(good.score(X_test, y_test), 4))
for name, ok in run_tests(good).items():
    print(f'  {"PASS" if ok else "FAIL"}  {name}')

shuffled = np.random.default_rng(1).permutation(y_train)                       # a broken training run
bad = train(shuffled)
print('Broken model (shuffled labels), test accuracy', round(bad.score(X_test, y_test), 4))
for name, ok in run_tests(bad).items():
    print(f'  {"PASS" if ok else "FAIL"}  {name}')
print('CI would block the broken model:', not all(run_tests(bad).values()))
