# 2.1 Linear algebra for ML: vectors, distances and matrices
# Example "word_counts_cosine" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import math

# Two short reviews turned into word count vectors over the same word list
words = ["good", "great", "bad", "food", "service"]
review_1 = [2, 1, 0, 1, 1]       # "good good great food service"
review_2 = [1, 0, 0, 1, 0]       # "good food"
review_3 = [0, 0, 3, 1, 1]       # "bad bad bad food service"

def cosine(u, v):
    dot = sum(a * b for a, b in zip(u, v))
    return dot / (math.sqrt(sum(a * a for a in u)) * math.sqrt(sum(b * b for b in v)))

print("review 1 vs 2:", round(cosine(review_1, review_2), 3))
print("review 1 vs 3:", round(cosine(review_1, review_3), 3))
print("The short review 2 is closer to review 1 even though it is much shorter.")
