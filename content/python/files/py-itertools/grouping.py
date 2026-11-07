# 2.2 itertools, functools and operator
# Example "grouping" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from itertools import groupby

runs = []
for key, group in groupby("aaabccdd"):
    runs.append((key, len(list(group))))
print(runs)

orders = [("tea", 10), ("coffee", 25), ("tea", 12), ("juice", 30), ("coffee", 20)]
print([name for name, group in groupby(orders, key=lambda o: o[0])])   # NOT sorted

orders.sort(key=lambda o: o[0])                # sort by the same key first
for name, group in groupby(orders, key=lambda o: o[0]):
    amounts = [amount for item, amount in group]
    print(name, amounts, sum(amounts))
