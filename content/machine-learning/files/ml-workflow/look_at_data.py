# 1.2 The machine learning project: from a question to a working model
# Example "look_at_data" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import pandas as pd

orders = pd.DataFrame({
    "distance_km": [1.2, 3.5, 5.0, 2.2, 8.1, 4.4, 0.9, 6.3],
    "hour": [12, 13, 20, 9, 21, 19, 15, 13],
    "raining": [0, 0, 1, 0, 1, 0, 0, 1],
    "minutes": [14, 22, 38, 17, 51, 29, 12, 41],
})
print(orders.shape)                 # (rows, columns)
print(orders.head(3))               # the first rows
print(orders["minutes"].describe().round(1))
print("average minutes when raining:", round(orders[orders["raining"] == 1]["minutes"].mean(), 1))
print("average minutes when dry:    ", round(orders[orders["raining"] == 0]["minutes"].mean(), 1))
