# 3.1 Decision trees: a chain of yes or no questions
# Example "gini_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

hours = [1, 2, 3, 4, 5, 6, 7, 8]
passed = ["no", "no", "no", "no", "yes", "no", "yes", "yes"]

def gini(labels):
    if not labels:
        return 0.0
    p = labels.count("yes") / len(labels)
    return 1 - p ** 2 - (1 - p) ** 2

print("Gini before any split:", round(gini(passed), 3))
best = None
for i in range(1, len(hours)):
    cut = (hours[i - 1] + hours[i]) / 2
    left = [passed[j] for j in range(len(hours)) if hours[j] < cut]
    right = [passed[j] for j in range(len(hours)) if hours[j] >= cut]
    weighted = (len(left) * gini(left) + len(right) * gini(right)) / len(hours)
    print("cut at", cut, " left", len(left), " right", len(right), " weighted Gini", round(weighted, 3))
    if best is None or weighted < best[1]:
        best = (cut, weighted)
print("best cut:", best[0], " Gini drops by", round(gini(passed) - best[1], 3))
