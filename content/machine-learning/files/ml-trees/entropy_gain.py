# 3.1 Decision trees: a chain of yes or no questions
# Example "entropy_gain" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import math

def entropy(counts):
    total = sum(counts)
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            h = h - p * math.log2(p)
    return h

parent = [9, 5]                       # 9 play, 5 do not play
children = {"sunny": [2, 3], "overcast": [4, 0], "rain": [3, 2]}
print("parent entropy:", round(entropy(parent), 3))
after = 0.0
for name, counts in children.items():
    share = sum(counts) / sum(parent)
    after = after + share * entropy(counts)
    print(name.ljust(8), counts, " entropy", round(entropy(counts), 3))
print("weighted entropy after the split:", round(after, 3))
print("information gain:", round(entropy(parent) - after, 3))
