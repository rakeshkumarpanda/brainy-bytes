# 3.1 Data cleaning: missing values, types, outliers and joins
# Example "knn_vs_mean" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer

rng = np.random.default_rng(4)
size = rng.uniform(40, 150, size=60)
price = 0.8 * size + rng.normal(0, 5, size=60)       # price follows size
data = pd.DataFrame({"size": size, "price": price})

hidden = rng.choice(60, size=12, replace=False)       # hide 12 prices
truth = data.loc[hidden, "price"].copy()
holes = data.copy()
holes.loc[hidden, "price"] = np.nan

mean_fill = holes["price"].fillna(holes["price"].mean())
knn_fill = KNNImputer(n_neighbors=3).fit_transform(holes)[:, 1]

mean_error = np.mean(np.abs(mean_fill[hidden] - truth))
knn_error = np.mean(np.abs(knn_fill[hidden] - truth))
print("average error, mean fill:", round(mean_error, 2))
print("average error, KNN fill: ", round(knn_error, 2))
