# 3.2 Association rules and market basket analysis
# Example "apriori" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from itertools import combinations

baskets = [{"bread", "milk"}, {"bread", "butter", "milk"}, {"bread", "butter"}, {"milk", "tea"},
           {"bread", "butter", "jam"}, {"bread", "milk", "butter"}, {"tea", "biscuits"}, {"bread", "jam"},
           {"milk", "biscuits", "tea"}, {"bread", "butter", "milk", "jam"}]
min_count = 3                                              # an itemset must appear in at least 3 of 10 baskets
items = sorted(set().union(*baskets))
level = [frozenset([i]) for i in items]
frequent = {}
k = 1
while level:
    counts = {c: sum(1 for b in baskets if c <= b) for c in level}
    keep = {c: v for c, v in counts.items() if v >= min_count}
    print("size", k, ": counted", len(level), "candidates, kept", len(keep), sorted((sorted(c), v) for c, v in keep.items()))
    frequent.update(keep)
    k = k + 1
    # join frequent sets that differ in one item, then drop any candidate with an infrequent subset (Apriori rule)
    joined = {a | b for a in keep for b in keep if len(a | b) == k}
    level = [c for c in joined if all(frozenset(s) in keep for s in combinations(c, k - 1))]
print("frequent itemsets found:", len(frequent))
