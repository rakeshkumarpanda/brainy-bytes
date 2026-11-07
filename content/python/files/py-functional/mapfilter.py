# 4.3 lambda, map, filter and comprehensions
# Example "mapfilter" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

prices = [120, 45, 300, 80]

with_tax = map(lambda p: p * 1.18, prices)     # apply a function to every item
print(with_tax)                                # a lazy map object
print([round(p, 2) for p in with_tax])

cheap = filter(lambda p: p < 100, prices)      # keep items where the test is True
print(list(cheap))

print(list(map(str.upper, ["a", "b"])))        # any function works, not only lambdas
print(list(map(lambda a, b: a + b, [1, 2, 3], [10, 20, 30])))   # two lists at once
print(list(filter(None, [0, 1, "", "hi", None, []])))           # None keeps truthy items

from functools import reduce
print(reduce(lambda total, p: total + p, prices, 0))   # fold the list into one value
