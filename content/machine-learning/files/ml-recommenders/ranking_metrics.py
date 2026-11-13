# 3.3 Recommender systems
# Example "ranking_metrics" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

recommended = ["A", "B", "C", "D", "E"]                   # our top 5, best first
relevant = {"A", "C", "F"}                                # what the user actually liked later
k = 5
hits = [1 if item in relevant else 0 for item in recommended[:k]]
print("hits:", hits)
print("precision@5 =", sum(hits) / k, " recall@5 =", round(sum(hits) / len(relevant), 3))
dcg = sum(h / np.log2(i + 2) for i, h in enumerate(hits))
ideal = sum(1 / np.log2(i + 2) for i in range(min(k, len(relevant))))
print("DCG", round(float(dcg), 3), " ideal DCG", round(float(ideal), 3), " NDCG@5 =", round(float(dcg / ideal), 3))
first = next(i for i, h in enumerate(hits) if h) + 1
print("reciprocal rank of the first hit =", 1 / first)
