# 3.1 Data cleaning: missing values, types, outliers and joins
# Example "fix_types_text" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import pandas as pd

df = pd.DataFrame({
    "city": [" Delhi", "DELHI", "delhi ", "Mumbai", "Bombay", "pune"],
    "price": ["52", "48", "unknown", "71", "75", "40"],
    "listed": ["2024-01-05", "2024-02-11", "2024-02-30", "2024-03-01", "2024-03-09", "2024-04-15"],
})
df["city"] = df["city"].str.strip().str.lower()
df["city"] = df["city"].replace({"bombay": "mumbai"})
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["listed"] = pd.to_datetime(df["listed"], errors="coerce")
print(df.to_string())
print(df.dtypes.to_string())
print("city counts:", df["city"].value_counts().to_dict())
