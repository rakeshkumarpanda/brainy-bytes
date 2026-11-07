# 2.2 itertools, functools and operator
# Example "functools" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from functools import reduce, partial, singledispatch, lru_cache
import operator

print(reduce(operator.add, [1, 2, 3, 4]))      # ((1 + 2) + 3) + 4
print(reduce(lambda total, word: total + len(word), ["hi", "you"], 0))
print(reduce(max, [3, 9, 2]))


def power(base, exponent):
    return base ** exponent


square = partial(power, exponent=2)            # fix one argument, get a new function
cube = partial(power, exponent=3)
print(square(5), cube(2), square.func.__name__, square.keywords)
from_binary = partial(int, base=2)
print(from_binary("1011"))


@singledispatch                                # choose a version by the type of the first argument
def describe(value):
    return "something"


@describe.register
def _(value: int):
    return "an int, " + str(value * 2) + " when doubled"


@describe.register
def _(value: list):
    return "a list of " + str(len(value))


print(describe(21), "|", describe([1, 2]), "|", describe(2.5))


@lru_cache(maxsize=2)
def slow_square(n):
    return n * n


for n in [1, 2, 1, 3, 1]:
    slow_square(n)
print(slow_square.cache_info())
