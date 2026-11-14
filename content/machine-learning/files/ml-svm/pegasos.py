# 2.4 Support vector machines: the widest street
# Example "pegasos" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

rng = np.random.default_rng(0)
X = np.vstack([rng.normal([1, 1], 0.6, (40, 2)), rng.normal([3, 3], 0.6, (40, 2))])
y = np.array([-1] * 40 + [1] * 40)

w = np.zeros(2)
b = 0.0
lam = 0.01
for epoch in range(1, 31):
    lr = 0.1 / epoch
    for i in rng.permutation(len(X)):
        if y[i] * (X[i] @ w + b) < 1:          # inside the margin or wrong: push
            w = w - lr * (lam * w - y[i] * X[i])
            b = b + lr * y[i]
        else:                                  # safely outside: only shrink w
            w = w - lr * lam * w
    if epoch in (1, 10, 30):
        hinge = np.maximum(0, 1 - y * (X @ w + b)).mean()
        acc = np.mean(np.sign(X @ w + b) == y)
        print("epoch", str(epoch).rjust(2), " mean hinge loss", round(float(hinge), 3), " accuracy", round(float(acc), 3))
print("w =", np.round(w, 3).tolist(), " b =", round(float(b), 3))
