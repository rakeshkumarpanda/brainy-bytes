# 1.1 Machine learning for security
# Example "detector_metrics" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Judging a detector: confusion matrix, precision, recall, F1 and ROC AUC on imbalanced data
scores = [0.95, 0.91, 0.88, 0.80, 0.72, 0.65, 0.61, 0.55, 0.43, 0.40, 0.33, 0.30, 0.22, 0.18, 0.10, 0.05]
labels = [1,    1,    0,    1,    0,    1,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0]
# 1 = real attack, 0 = normal

def confusion(threshold):
    tp = fp = fn = tn = 0
    for s, y in zip(scores, labels):
        alert = s >= threshold
        if alert and y == 1:
            tp += 1
        elif alert and y == 0:
            fp += 1
        elif not alert and y == 1:
            fn += 1
        else:
            tn += 1
    return tp, fp, fn, tn

print("thresh  TP FP FN TN  precision recall   F1    FPR")
for t in (0.9, 0.7, 0.5, 0.3):
    tp, fp, fn, tn = confusion(t)
    prec = tp / (tp + fp)
    rec = tp / (tp + fn)
    f1 = 2 * prec * rec / (prec + rec)
    print(f" {t:.1f}    {tp:2} {fp:2} {fn:2} {tn:2}    {prec:.3f}   {rec:.3f}  {f1:.3f}  {fp / (fp + tn):.3f}")

# AUC = chance that a random attack scores higher than a random normal event
pos = [s for s, y in zip(scores, labels) if y == 1]
neg = [s for s, y in zip(scores, labels) if y == 0]
wins = sum(1 for p in pos for n in neg if p > n)
print(f"\nROC AUC = {wins} / {len(pos) * len(neg)} = {wins / (len(pos) * len(neg)):.3f}")
print("Accuracy of 'never alert':", f"{len(neg) / len(labels):.3f}", " high, yet it catches nothing.")
