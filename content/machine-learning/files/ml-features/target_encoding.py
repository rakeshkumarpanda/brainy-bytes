# 3.2 Features: encoding, scaling, engineering and selection
# Example "target_encoding" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
import pandas as pd
from sklearn.preprocessing import TargetEncoder

rng = np.random.default_rng(0)
shops = np.array(["shop" + str(i) for i in range(50)])
shop = rng.choice(shops, 1000)
rate = {s: rng.uniform(0.1, 0.9) for s in shops}           # each shop has its own buy rate
bought = (rng.uniform(size=1000) < np.array([rate[s] for s in shop])).astype(int)

df = pd.DataFrame({"shop": shop, "bought": bought})
print("one hot would make", df["shop"].nunique(), "columns")

enc = TargetEncoder(target_type="binary", random_state=0)
encoded = enc.fit_transform(df[["shop"]], df["bought"])
print("target encoding makes 1 column. First 3 rows:", np.round(encoded[:3, 0], 3).tolist())
means = df.groupby("shop")["bought"].mean()
print("plain shop means for those rows:", [round(float(means[s]), 3) for s in df["shop"][:3]])
