# 2.4 Support vector machines: the widest street
# Example "svr_tube" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.svm import SVR

rng = np.random.default_rng(0)
x = np.sort(rng.uniform(0, 6, 60)).reshape(-1, 1)
y = np.sin(x).ravel() + rng.normal(0, 0.1, 60)
for eps in [0.01, 0.1, 0.3]:
    model = SVR(kernel="rbf", C=10, epsilon=eps).fit(x, y)
    err = np.abs(model.predict(x) - y).mean()
    print("epsilon", str(eps).ljust(4), " support vectors", str(len(model.support_)).rjust(2), " mean error", round(float(err), 3))
