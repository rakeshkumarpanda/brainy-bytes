# 3.1 Data cleaning: missing values, types, outliers and joins
# Example "merge_reshape" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import pandas as pd

customers = pd.DataFrame({"cust_id": [1, 2, 3], "name": ["Asha", "Ravi", "Meena"]})
orders = pd.DataFrame({"order_id": [10, 11, 12, 13], "cust_id": [1, 1, 3, 4], "amount": [250, 100, 400, 90]})

inner = customers.merge(orders, on="cust_id", how="inner")
left = customers.merge(orders, on="cust_id", how="left")
print("inner join rows:", len(inner), " left join rows:", len(left))
print(left.to_string())

wide = pd.DataFrame({"student": ["Asha", "Ravi"], "maths": [90, 72], "physics": [85, 80]})
long = wide.melt(id_vars="student", var_name="subject", value_name="marks")
print(long.to_string())
back = long.pivot(index="student", columns="subject", values="marks")
print(back.to_string())
