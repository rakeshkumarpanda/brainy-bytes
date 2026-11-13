# 3.2 Association rules and market basket analysis
# Example "rules_table" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from itertools import combinations
import numpy as np
import pandas as pd

rng = np.random.default_rng(0)
items = ["bread", "butter", "milk", "tea", "biscuits", "jam", "coffee", "sugar"]
rows = []
for _ in range(1000):                                      # simulate 1,000 shopping trips with some habits
    b = set(rng.choice(items, size=rng.integers(1, 4), replace=False))
    if "bread" in b and rng.random() < 0.6: b.add("butter")
    if "tea" in b and rng.random() < 0.5: b.add("biscuits")
    if "coffee" in b and rng.random() < 0.7: b.add("sugar")
    rows.append(b)
onehot = pd.DataFrame([[i in b for i in items] for b in rows], columns=items)
sup = onehot.mean()
out = []
for a, c in combinations(items, 2):
    for x, y in [(a, c), (c, a)]:
        s_xy = float((onehot[x] & onehot[y]).mean())
        if s_xy >= 0.05:
            conf = s_xy / sup[x]
            out.append((x, y, round(s_xy, 3), round(conf, 3), round(conf / sup[y], 2)))
rules = pd.DataFrame(out, columns=["if", "then", "support", "confidence", "lift"]).sort_values(["lift", "confidence"], ascending=False, kind="stable")
print(rules.head(6).to_string(index=False))
print("rules with lift below 1:", int((rules["lift"] < 1).sum()), "of", len(rules))
