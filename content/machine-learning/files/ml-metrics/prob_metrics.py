# 4.1 Metrics: measuring a model properly
# Example "prob_metrics" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.metrics import brier_score_loss, log_loss

y = [1, 1, 0, 0]
careful = [0.7, 0.6, 0.4, 0.3]
bold = [0.99, 0.99, 0.01, 0.99]                     # sure about everything, wrong once
for name, p in [("careful", careful), ("bold", bold)]:
    acc = sum((pi >= 0.5) == yi for pi, yi in zip(p, y)) / len(y)
    print(name.ljust(8), "accuracy", acc, " log loss", round(log_loss(y, p), 3), " Brier", round(brier_score_loss(y, p), 3))
