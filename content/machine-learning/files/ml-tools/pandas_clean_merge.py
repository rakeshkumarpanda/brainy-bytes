# 1.3 Python tools for ML: NumPy, pandas and scikit-learn
# Example "pandas_clean_merge" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import pandas as pd
import numpy as np

orders = pd.DataFrame({"order_id": [1, 2, 3, 4], "customer_id": [10, 11, 10, 12], "amount": [250.0, np.nan, 120.0, 90.0]})
customers = pd.DataFrame({"customer_id": [10, 11, 12], "name": ["Asha", "Ravi", "Meera"]})

print("missing per column:")
print(orders.isna().sum())
orders["amount"] = orders["amount"].fillna(orders["amount"].median())   # fill the hole
joined = orders.merge(customers, on="customer_id", how="left")         # like a SQL join
print(joined)
print(joined.sort_values("amount", ascending=False)[["name", "amount"]])
