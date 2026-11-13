# 2.1 Linear algebra for ML: vectors, distances and matrices
# Example "norms_and_distances" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import math

def euclidean(u, v):
    total = 0
    for a, b in zip(u, v):
        total = total + (a - b) ** 2
    return math.sqrt(total)

def manhattan(u, v):
    total = 0
    for a, b in zip(u, v):
        total = total + abs(a - b)
    return total

def cosine_similarity(u, v):
    dot = 0
    size_u = 0
    size_v = 0
    for a, b in zip(u, v):
        dot = dot + a * b
        size_u = size_u + a * a
        size_v = size_v + b * b
    return dot / (math.sqrt(size_u) * math.sqrt(size_v))

a = [1, 2]
b = [4, 6]
print("Euclidean:", euclidean(a, b))
print("Manhattan:", manhattan(a, b))
print("length of b (L2 norm):", round(euclidean(b, [0, 0]), 4))
print("cosine(a, b):", round(cosine_similarity(a, b), 4))
print("cosine([1, 2], [2, 4]):", round(cosine_similarity([1, 2], [2, 4]), 4), "same direction")
