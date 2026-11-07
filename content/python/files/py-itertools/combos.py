# 2.2 itertools, functools and operator
# Example "combos" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from itertools import product, permutations, combinations, combinations_with_replacement
import math

items = "ABC"
print(["".join(t) for t in product(items, repeat=2)])
print(["".join(t) for t in permutations(items, 2)])
print(["".join(t) for t in combinations(items, 2)])
print(["".join(t) for t in combinations_with_replacement(items, 2)])
print(3 ** 2, math.perm(3, 2), math.comb(3, 2), math.comb(3 + 2 - 1, 2))

sizes = ["S", "M"]
colours = ["red", "blue", "black"]
shirts = list(product(sizes, colours))         # replaces two nested for loops
print(len(shirts), shirts[:2])

pins = 0
for p in product("0123456789", repeat=4):
    if len(set(p)) == 4:                       # no digit used twice
        pins += 1
print(pins, math.perm(10, 4))
