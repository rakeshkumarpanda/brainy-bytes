# 3.1 Anomaly detection
# Example "robust_stats" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Daily orders for a small shop, with two very bad data entry days
x = np.array([52, 48, 50, 55, 47, 51, 49, 53, 50, 46, 54, 900, 950], dtype=float)
z = (x - x.mean()) / x.std()
print("mean", round(float(x.mean()), 1), " sd", round(float(x.std()), 1))
print("z scores of the two bad days:", np.round(z[-2:], 2).tolist(), " flagged with |z| > 3:", int((np.abs(z) > 3).sum()))

med = np.median(x)
mad = np.median(np.abs(x - med)) * 1.4826             # scaled so it matches the sd for normal data
robust = (x - med) / mad
print("median", med, " MAD", round(float(mad), 2))
print("robust scores of the two bad days:", np.round(robust[-2:], 1).tolist(), " flagged with |score| > 3.5:", int((np.abs(robust) > 3.5).sum()))

q1, q3 = np.percentile(x, [25, 75])
lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
print("IQR fences", lo, "to", hi, " flagged:", x[(x < lo) | (x > hi)].tolist())
