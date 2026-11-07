# 4.2 collections, heapq and bisect
# Example "counting" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from collections import Counter

votes = Counter(["tea", "coffee", "tea", "juice", "tea", "coffee"])
print(votes)
print(votes["tea"], votes["water"])            # a missing key counts as 0, no KeyError
print(votes.most_common(2))
print(votes.total())                           # the sum of all counts (Python 3.10+)

monday = Counter(apples=3, pears=1)
tuesday = Counter(apples=1, plums=2)
print(monday + tuesday)                        # add the counts
print(monday - tuesday)                        # subtract, and drop counts of 0 or less
print(monday & tuesday)                        # the smaller count of each item
print(monday | tuesday)                        # the bigger count of each item
print(sorted((monday + tuesday).elements()))   # each item repeated by its count
print(Counter("listen") == Counter("silent"))  # same letters, same counts: an anagram
