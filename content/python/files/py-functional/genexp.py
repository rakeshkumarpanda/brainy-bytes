# 4.3 lambda, map, filter and comprehensions
# Example "genexp" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import sys

as_list = [n * n for n in range(10_000)]
as_gen = (n * n for n in range(10_000))        # round brackets: a generator expression
print(sys.getsizeof(as_list) > 50_000, sys.getsizeof(as_gen) < 300)
print(sum(as_gen))                             # values are made one at a time
print(sum(as_gen))                             # a generator can be used only once

print(sum(n * n for n in range(1, 11)))        # no extra brackets needed in a call
print(any(n > 9 for n in [3, 12, 5]), all(n > 0 for n in [3, 12, 5]))
print(max(len(w) for w in ["a", "abc", "ab"]))
