# 1.3 Python tools for ML: NumPy, pandas and scikit-learn
# Example "pandas_groupby" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import pandas as pd

df = pd.DataFrame({
    "city": ["Pune", "Delhi", "Pune", "Chennai", "Delhi", "Chennai", "Pune"],
    "temp": [31, 38, 29, 34, 41, 33, 30],
    "rain_mm": [0, 0, 12, 5, 0, 20, 3],
})
print(df.groupby("city")["temp"].mean().round(2))
print(df.groupby("city").agg(avg_temp=("temp", "mean"), total_rain=("rain_mm", "sum"), days=("temp", "count")))

# add a new feature: each row's temperature minus its city's average
df["temp_vs_city"] = df["temp"] - df.groupby("city")["temp"].transform("mean")
print(df.round(2))
