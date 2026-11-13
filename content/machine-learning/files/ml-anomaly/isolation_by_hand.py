# 3.1 Anomaly detection
# Example "isolation_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

rng = np.random.default_rng(0)
x = np.concatenate([rng.normal(50, 5, 99), [95.0]])    # 99 normal values and one far away
def depth(target, values, rng):
    steps = 0
    while len(values) > 1:
        cut = rng.uniform(values.min(), values.max())   # a random split between min and max
        values = values[values < cut] if target < cut else values[values >= cut]
        steps = steps + 1
    return steps
outlier = [depth(95.0, x, rng) for _ in range(200)]
normal = [depth(x[0], x, rng) for _ in range(200)]
print("average splits to isolate the far value 95:", round(float(np.mean(outlier)), 2))
print("average splits to isolate a normal value", round(float(x[0]), 1), ":", round(float(np.mean(normal)), 2))
n = len(x)
c = 2 * (np.log(n - 1) + 0.5772156649) - 2 * (n - 1) / n  # average depth of an unsuccessful search in a random tree
for name, h in [("far value", np.mean(outlier)), ("normal value", np.mean(normal))]:
    print(name.ljust(12), " anomaly score 2^(-h/c) =", round(float(2 ** (-h / c)), 3))
