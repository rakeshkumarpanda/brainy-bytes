# 4.1 Metrics: measuring a model properly
# Example "confusion_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

actual    = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
predicted = [1, 1, 1, 0, 1, 0, 0, 0, 0, 0]

tp = fp = fn = tn = 0
for a, p in zip(actual, predicted):
    if a == 1 and p == 1:
        tp = tp + 1
    elif a == 0 and p == 1:
        fp = fp + 1
    elif a == 1 and p == 0:
        fn = fn + 1
    else:
        tn = tn + 1
print("TP", tp, " FP", fp, " FN", fn, " TN", tn)
precision = tp / (tp + fp)
recall = tp / (tp + fn)
print("accuracy ", (tp + tn) / len(actual))
print("precision", precision, " (of the predicted positives, how many are real)")
print("recall   ", recall, " (of the real positives, how many we found)")
print("F1       ", round(2 * precision * recall / (precision + recall), 3))
