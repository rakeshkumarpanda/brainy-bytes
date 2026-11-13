# 3.2 Features: encoding, scaling, engineering and selection
# Example "scalers_compared" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

income = np.array([[30], [35], [40], [45], [50], [400]])   # thousands, one very rich person

for scaler in [StandardScaler(), MinMaxScaler(), RobustScaler()]:
    scaled = scaler.fit_transform(income).ravel()
    print(type(scaler).__name__.ljust(15), np.round(scaled, 2).tolist())

print("log1p:", np.round(np.log1p(income.ravel()), 2).tolist())
