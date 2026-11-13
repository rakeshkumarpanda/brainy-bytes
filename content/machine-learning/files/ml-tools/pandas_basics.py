# 1.3 Python tools for ML: NumPy, pandas and scikit-learn
# Example "pandas_basics" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Meera", "John", "Sara"],
    "city": ["Pune", "Delhi", "Pune", "Chennai", "Delhi"],
    "age": [21, 25, 22, 30, 28],
    "score": [88, 72, 95, 64, 81],
})
print(df.shape)
print(df.head(3))
print(df.dtypes)
print("one column:", df["score"].tolist())
print("rows where score > 80:")
print(df[df["score"] > 80])
print("row with label 2 using loc:", df.loc[2, "name"], "| first row using iloc:", df.iloc[0]["name"])
