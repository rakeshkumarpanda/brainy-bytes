# 1.4 Exceptions in depth, copying and serialisation
# Example "copying" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import copy

a = [[1, 2], [3, 4]]
b = a                                          # same object
c = a.copy()                                   # shallow: new outer, shared inner
d = copy.deepcopy(a)                           # deep: everything new

c[0].append(9)
c.append([5])
print(a)
print(c)
print(d)
print(b is a, c is a, c[0] is a[0], d[0] is a[0])

prices = {"pen": [10, 12], "ink": [5]}
shallow = dict(prices)                         # also shallow: dict(), list(), [:], copy.copy
shallow["pen"].append(15)
print(prices["pen"])

loop = [1, 2]
loop.append(loop)                              # a list that contains itself
twin = copy.deepcopy(loop)                     # deepcopy remembers what it already copied
print(twin[2] is twin, twin[2] is loop)
