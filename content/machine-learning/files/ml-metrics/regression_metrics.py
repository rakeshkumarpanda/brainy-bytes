# 4.1 Metrics: measuring a model properly
# Example "regression_metrics" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score

y_true = np.array([100, 150, 200, 250, 300])
y_pred = np.array([110, 140, 210, 240, 400])        # the last prediction is far off
print("MAE ", mean_absolute_error(y_true, y_pred))
print("MSE ", mean_squared_error(y_true, y_pred))
print("RMSE", round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 2))
print("MAPE", round(mean_absolute_percentage_error(y_true, y_pred), 3))
print("R2  ", round(r2_score(y_true, y_pred), 3))
