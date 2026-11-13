# 1.2 The machine learning project: from a question to a working model
# Example "split_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import random

rows = list(range(20))        # pretend these are 20 examples, numbered 0 to 19
random.seed(42)
random.shuffle(rows)          # shuffle so every part is a fair sample

n = len(rows)
n_test = int(n * 0.2)         # 20% for the final test
n_val = int(n * 0.2)          # 20% to compare models

test_rows = rows[:n_test]
val_rows = rows[n_test:n_test + n_val]
train_rows = rows[n_test + n_val:]

print("train:", len(train_rows), sorted(train_rows))
print("val:  ", len(val_rows), sorted(val_rows))
print("test: ", len(test_rows), sorted(test_rows))
print("no overlap:", set(train_rows).isdisjoint(test_rows) and set(val_rows).isdisjoint(test_rows))
