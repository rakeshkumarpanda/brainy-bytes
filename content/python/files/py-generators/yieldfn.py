# 2.1 Iterators and generators
# Example "yieldfn" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import inspect


def countdown(n):
    print("  start")
    while n > 0:
        yield n                                # hand n over and pause here
        n -= 1
    print("  done")


g = countdown(2)                               # nothing printed yet
print(type(g).__name__, inspect.getgeneratorstate(g))
print(next(g))
print(inspect.getgeneratorstate(g))
print(next(g))
print(next(g, "no more"))
print(inspect.getgeneratorstate(g))
print(list(countdown(3)))
