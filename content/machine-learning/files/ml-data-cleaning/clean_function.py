# 3.1 Data cleaning: missing values, types, outliers and joins
# Example "clean_function" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import io
import numpy as np
import pandas as pd

raw = """id,city,size_m2,price,rooms
1,Delhi,80,52,2
2, mumbai ,65,71,2
3,DELHI,,48,3
4,Pune,120,unknown,4
5,Mumbai,70,75,
5,Mumbai,70,75,
6,pune,95,40,3
7,Delhi,2000,60,3
"""

def clean(df):
    df = df.drop_duplicates().copy()
    df["city"] = df["city"].str.strip().str.title()
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df.loc[df["size_m2"] > 1000, "size_m2"] = np.nan          # 2000 m2 flat is a typing mistake
    for col in ["size_m2", "price", "rooms"]:
        df[col] = df[col].fillna(df.groupby("city")[col].transform("median"))
    df["rooms"] = df["rooms"].astype(int)
    return df

houses = clean(pd.read_csv(io.StringIO(raw)))
print(houses.to_string(index=False))

assert houses["id"].is_unique, "ids must be unique"
assert houses.isna().sum().sum() == 0, "no missing values left"
assert houses["size_m2"].between(10, 1000).all(), "sizes must be sensible"
print("all checks pass")
