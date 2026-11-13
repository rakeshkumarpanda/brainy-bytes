# 1.1 Linear regression: fit the best straight line
# Example "regression_metrics" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

y_true = np.array([3.0, 5.0, 7.0, 9.0])
y_pred = np.array([2.5, 5.5, 6.0, 9.5])

errors = y_true - y_pred
mae = np.mean(np.abs(errors))
mse = np.mean(errors ** 2)
rmse = np.sqrt(mse)
r2 = 1 - np.sum(errors ** 2) / np.sum((y_true - y_true.mean()) ** 2)
print("by hand  MAE", mae, " MSE", mse, " RMSE", round(rmse, 4), " R2", round(r2, 4))
print("sklearn  MAE", mean_absolute_error(y_true, y_pred), " MSE", mean_squared_error(y_true, y_pred),
      " R2", round(r2_score(y_true, y_pred), 4))
print("always predicting the mean gives R2 =", r2_score(y_true, np.full(4, y_true.mean())))
