# 3.3 Boosting: small trees that fix each other
# Example "adaboost_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import math

x = [1, 2, 3, 4, 5, 6, 7, 8]
y = [1, 1, -1, -1, 1, 1, -1, -1]
w = [1 / len(x)] * len(x)

def best_stump(w):
    best = None
    for cut in [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]:
        for sign in [1, -1]:
            pred = [sign if xi < cut else -sign for xi in x]
            err = sum(wi for wi, p, t in zip(w, pred, y) if p != t)
            if best is None or err < best[0] - 1e-12:
                best = (err, cut, sign, pred)
    return best

total = [0.0] * len(x)
for m in range(1, 4):
    err, cut, sign, pred = best_stump(w)
    alpha = 0.5 * math.log((1 - err) / err)
    print("round", m, " stump: x <", cut, "gives", sign, " weighted error", round(err, 3), " alpha", round(alpha, 3))
    w = [wi * math.exp(-alpha * t * p) for wi, t, p in zip(w, y, pred)]
    s = sum(w)
    w = [wi / s for wi in w]
    total = [tt + alpha * p for tt, p in zip(total, pred)]
    print("   new weights", [round(wi, 3) for wi in w])
final = [1 if t > 0 else -1 for t in total]
print("final predictions", final, " correct", sum(f == t for f, t in zip(final, y)), "of", len(y))
