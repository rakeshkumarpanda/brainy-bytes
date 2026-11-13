# 3.2 Association rules and market basket analysis
# Example "matrix_counts" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
import pandas as pd

baskets = [{"bread", "milk"}, {"bread", "butter", "milk"}, {"bread", "butter"}, {"milk", "tea"},
           {"bread", "butter", "jam"}, {"bread", "milk", "butter"}, {"tea", "biscuits"}, {"bread", "jam"},
           {"milk", "biscuits", "tea"}, {"bread", "butter", "milk", "jam"}]
items = sorted(set().union(*baskets))
X = pd.DataFrame([[int(i in b) for i in items] for b in baskets], columns=items)   # one row per basket
pairs = X.T @ X                                             # item by item table: baskets containing both
print(pairs.to_string())
print("support(bread, butter) =", pairs.loc["bread", "butter"] / len(X))
