# 3.1 Data cleaning: missing values, types, outliers and joins
# Example "fill_missing" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

df = pd.DataFrame({
    "age": [25, np.nan, 35, 40, np.nan, 29],
    "city": ["Delhi", "Pune", None, "Delhi", "Delhi", "Pune"],
})
print("rows before dropna:", len(df), " after:", len(df.dropna()))

filled = df.copy()
filled["age_was_missing"] = filled["age"].isna().astype(int)
filled["age"] = filled["age"].fillna(filled["age"].median())
filled["city"] = filled["city"].fillna(filled["city"].mode()[0])
print(filled.to_string())

imp = SimpleImputer(strategy="mean")
print("SimpleImputer mean fill:", imp.fit_transform(df[["age"]]).ravel().tolist())
