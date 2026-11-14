# 1.2 The MLOps lifecycle and reproducible projects
# Example "seeds" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Same code, same data, different results? Randomness hides in the data split and in the model.
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)


def experiment(seed):
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=seed)
    model = RandomForestClassifier(n_estimators=50, random_state=seed).fit(X_tr, y_tr)
    return model.score(X_te, y_te)


print('No seed (a fresh random seed each run):')
rng = np.random.default_rng()
scores = [experiment(int(rng.integers(1_000_000))) for _ in range(5)]
print('  accuracies', [round(s, 3) for s in scores], ' spread', round(max(scores) - min(scores), 3))
print('Fixed seed 42, run 5 times:')
scores = [experiment(42) for _ in range(5)]
print('  accuracies', [round(s, 3) for s in scores], ' spread', round(max(scores) - min(scores), 3))
print('Ten different fixed seeds, to see the honest uncertainty:')
scores = np.array([experiment(s) for s in range(10)])
print(f'  mean {scores.mean():.3f}, standard deviation {scores.std():.3f}, min {scores.min():.3f}, max {scores.max():.3f}')
