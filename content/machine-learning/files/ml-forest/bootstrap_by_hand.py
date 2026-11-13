# 3.2 Random forests: many trees vote
# Example "bootstrap_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import random

random.seed(3)
rows = list(range(1, 11))
for b in range(3):
    sample = [random.choice(rows) for _ in rows]           # draw 10 rows with replacement
    out_of_bag = [r for r in rows if r not in sample]
    print("sample", b + 1, sorted(sample), " unique", len(set(sample)), " out of bag", out_of_bag)

shares = []
for b in range(300):
    sample = [random.randrange(1000) for _ in range(1000)]
    shares.append(len(set(sample)) / 1000)
print("average share of unique rows (n = 1000):", round(sum(shares) / len(shares), 3))
print("theory 1 - 1/e =", round(1 - 2.718281828 ** -1, 3))
