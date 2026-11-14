# 4.1 Metrics: measuring a model properly
# Example "roc_auc" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.metrics import roc_auc_score

y = [0, 0, 1, 0, 1, 1, 0, 1]
score = [0.1, 0.3, 0.35, 0.4, 0.6, 0.7, 0.8, 0.9]

pos = [s for s, t in zip(score, y) if t == 1]
neg = [s for s, t in zip(score, y) if t == 0]
wins = 0.0
for p in pos:
    for n in neg:
        if p > n:
            wins = wins + 1
        elif p == n:
            wins = wins + 0.5
print("pairs where the positive scores higher:", wins, "of", len(pos) * len(neg))
print("AUC by counting pairs:", wins / (len(pos) * len(neg)))
print("AUC from sklearn:     ", roc_auc_score(y, score))
