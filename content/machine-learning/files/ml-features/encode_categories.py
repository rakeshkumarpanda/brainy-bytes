# 3.2 Features: encoding, scaling, engineering and selection
# Example "encode_categories" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import pandas as pd
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

df = pd.DataFrame({"city": ["Delhi", "Pune", "Delhi", "Mumbai"],
                   "size": ["small", "large", "medium", "small"]})

print(pd.get_dummies(df["city"], dtype=int).to_string())

enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
enc.fit(df[["city"]])
print("columns:", enc.get_feature_names_out().tolist())
print("a new city, Chennai:", enc.transform(pd.DataFrame({"city": ["Chennai"]})).tolist())

order = OrdinalEncoder(categories=[["small", "medium", "large"]])
print("size as numbers:", order.fit_transform(df[["size"]]).ravel().tolist())
