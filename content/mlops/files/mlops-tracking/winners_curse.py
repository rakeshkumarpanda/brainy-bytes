# 3.1 Experiment tracking and the model registry
# Example "winners_curse" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

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
