# 3.1 Data cleaning: missing values, types, outliers and joins
# Example "find_outliers" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
import pandas as pd

salary = pd.Series([32, 35, 36, 38, 40, 41, 43, 45, 47, 150])   # thousands per month

q1 = salary.quantile(0.25)
q3 = salary.quantile(0.75)
iqr = q3 - q1
low = q1 - 1.5 * iqr
high = q3 + 1.5 * iqr
print("Q1", q1, " Q3", q3, " IQR", iqr, " fences", low, "to", high)
print("IQR outliers:", salary[(salary < low) | (salary > high)].tolist())

z = (salary - salary.mean()) / salary.std(ddof=0)
print("z scores:", z.round(2).tolist())
print("z above 3:", salary[z.abs() > 3].tolist(), " (the outlier itself pulls the mean and std)")
print("mean with outlier:", salary.mean(), " median:", salary.median())
print("clipped to fences:", salary.clip(low, high).tolist())
