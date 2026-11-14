# 2.2 k nearest neighbours: learn from similar examples
# Example "knn_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import math

# (height_cm, weight_kg) -> T-shirt size
people = [((158, 58), "M"), ((160, 59), "M"), ((163, 61), "M"), ((165, 64), "L"),
          ((168, 66), "L"), ((170, 68), "L"), ((160, 64), "L"), ((163, 59), "M")]
new = (161, 61)

distances = []
for (h, w), size in people:
    d = math.sqrt((h - new[0]) ** 2 + (w - new[1]) ** 2)
    distances.append((round(d, 2), size))
distances.sort()
print("sorted distances:", distances)

k = 3
votes = {}
for d, size in distances[:k]:
    votes[size] = votes.get(size, 0) + 1
print("votes of the", k, "nearest:", votes)
print("prediction:", max(votes, key=votes.get))
