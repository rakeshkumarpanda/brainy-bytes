# 2.2 k nearest neighbours: learn from similar examples
# Example "similar_items" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.neighbors import NearestNeighbors

movies = np.array([[9, 1, 0], [8, 2, 1], [1, 9, 8], [0, 8, 9], [5, 5, 5]])   # action, romance, drama scores
names = ["Fast Cars", "Big Chase", "Love Letters", "Rainy Days", "Mixed Bag"]

nn = NearestNeighbors(n_neighbors=3).fit(movies)
dist, idx = nn.kneighbors([movies[0]])
print("most similar to", names[0], ":", [names[i] for i in idx[0][1:]], " distances", np.round(dist[0][1:], 2).tolist())
