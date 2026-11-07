# 2.1 Iterators and generators
# Example "lazy" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import random

prices = {"tea": 10, "coffee": 25}
names = prices.keys()                          # a live view, not a copy
prices["juice"] = 30
print(list(names))

pairs = zip("abc", [1, 2, 3])                  # zip is an iterator: used once
print(next(pairs), list(pairs), list(pairs))

r = range(0, 10 ** 12, 7)                      # range is lazy AND can be reused
print(len(r), r[3], 21 in r)

for number, word in enumerate(["x", "y"], start=1):
    print(number, word)

random.seed(4)
rolls = iter(lambda: random.randint(1, 6), 6)  # call again and again until it gives 6
print(list(rolls))
print(list(reversed([1, 2, 3])), list(map(abs, [-1, 2])))
