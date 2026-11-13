# 3.1 Data cleaning: missing values, types, outliers and joins
# Example "inspect_data" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import io
import pandas as pd

raw = """id,city,size_m2,price,built,rooms
1,Delhi,80,52,2015-03-01,2
2, mumbai ,65,71,2018-07-15,2
3,DELHI,,48,2012-11-30,3
4,Pune,120,unknown,2020-01-10,4
5,Mumbai,70,75,2019-05-20,
5,Mumbai,70,75,2019-05-20,
6,pune,95,40,2016-08-08,3
7,Delhi,2000,60,2014-02-14,3
"""
houses = pd.read_csv(io.StringIO(raw))
print("shape:", houses.shape)
print(houses.dtypes.to_string())
print("missing per column:")
print(houses.isna().sum().to_string())
print("duplicate rows:", houses.duplicated().sum())
print("city values:", sorted(houses["city"].unique()))
