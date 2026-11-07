# 3.4 Dictionaries: keys, values and hash tables
# Example "group" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

words = ["apple", "avocado", "banana", "blueberry", "cherry"]

groups = {}
for w in words:
    first = w[0]
    if first not in groups:
        groups[first] = []
    groups[first].append(w)
print(groups)

from collections import defaultdict
groups = defaultdict(list)      # a missing key starts as an empty list
for w in words:
    groups[w[0]].append(w)
print(dict(groups))
