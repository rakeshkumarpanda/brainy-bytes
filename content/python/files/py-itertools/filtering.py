# 2.2 itertools, functools and operator
# Example "filtering" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from itertools import takewhile, dropwhile, compress, filterfalse

temps = [21, 23, 26, 31, 29, 24, 33]
print(list(takewhile(lambda t: t < 30, temps)))   # stop at the first hot day
print(list(dropwhile(lambda t: t < 30, temps)))   # skip until the first hot day
print(list(filter(lambda t: t < 30, temps)))      # check every single item
print(list(filterfalse(lambda t: t < 30, temps)))

days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
present = [1, 0, 1, 1, 0]
print(list(compress(days, present)))              # keep where the mask is true
