# 2.2 itertools, functools and operator
# Example "combining" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from itertools import chain, zip_longest, pairwise, batched, starmap, accumulate, tee
import operator

print(list(chain([1, 2], (3, 4), "ab")))
print(list(chain.from_iterable([[1, 2], [3], []])))
print(list(zip_longest("abc", [1, 2], fillvalue="-")))
print(list(pairwise([10, 13, 19, 20])))        # neighbours: (a, b), (b, c), ...
print(list(batched(range(7), 3)))              # groups of 3 (Python 3.12 and later)
print(list(starmap(operator.mul, [(2, 5), (3, 4)])))
print(list(accumulate([3, 1, 4, 1, 5])))       # running totals
print(list(accumulate([3, 1, 4, 1, 5], max)))  # running maximum
print(list(accumulate([1, 2, 3, 4], operator.mul, initial=1)))
first, second = tee(iter([1, 2, 3]))           # two independent copies of one iterator
print(list(first), list(second))
