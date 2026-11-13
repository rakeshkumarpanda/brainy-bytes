# 1.2 Hierarchical clustering and DBSCAN
# Example "merge_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Six points on a line: two tight pairs, one loose pair
x = np.array([1.0, 2.0, 6.0, 7.0, 15.0, 18.0])
clusters = [[i] for i in range(len(x))]

def single_link(a, b):
    return min(abs(x[i] - x[j]) for i in a for j in b)

while len(clusters) > 1:
    best = None
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            d = single_link(clusters[i], clusters[j])
            if best is None or d < best[0]:
                best = (d, i, j)
    d, i, j = best
    merged = clusters[i] + clusters[j]
    print("merge", [x[k].item() for k in clusters[i]], "and", [x[k].item() for k in clusters[j]], "at distance", d.item())
    clusters = [c for k, c in enumerate(clusters) if k not in (i, j)] + [merged]
print("one cluster left with", len(clusters[0]), "points")
