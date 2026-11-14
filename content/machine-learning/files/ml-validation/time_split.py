# 4.2 Validation: honest estimates of performance
# Example "time_split" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.model_selection import TimeSeriesSplit

days = np.arange(12)
for i, (train, val) in enumerate(TimeSeriesSplit(n_splits=4).split(days)):
    print("split", i + 1, " train on days", train.tolist(), " validate on days", val.tolist())
