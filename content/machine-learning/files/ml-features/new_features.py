# 3.2 Features: encoding, scaling, engineering and selection
# Example "new_features" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
import pandas as pd

sales = pd.DataFrame({
    "date": pd.to_datetime(["2024-01-06", "2024-01-08", "2024-03-15", "2024-12-25"]),
    "price": [5200000, 7100000, 4800000, 9900000],
    "size_m2": [80, 65, 60, 150],
    "age_years": [3, 12, 25, 1],
})
sales["month"] = sales["date"].dt.month
sales["weekday"] = sales["date"].dt.day_name()
sales["is_weekend"] = (sales["date"].dt.dayofweek >= 5).astype(int)
sales["price_per_m2"] = (sales["price"] / sales["size_m2"]).round()
sales["age_group"] = pd.cut(sales["age_years"], bins=[0, 5, 15, 100], labels=["new", "mid", "old"])
sales["log_price"] = np.log(sales["price"]).round(3)
print(sales.drop(columns=["date"]).to_string(index=False))
