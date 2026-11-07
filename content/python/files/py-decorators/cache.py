# 1.2 Extended arguments, closures and decorators
# Example "cache" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from functools import cache, lru_cache

calls = 0


def slow_fib(n):
    global calls
    calls += 1
    return n if n < 2 else slow_fib(n - 1) + slow_fib(n - 2)


print(slow_fib(25), calls, "calls without a cache")


@cache                                   # remember every answer
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print(fib(25), fib.cache_info())
print(fib(200))


@lru_cache(maxsize=2)                    # keep only the 2 most recently used answers
def square(n):
    return n * n


for n in [1, 2, 1, 3, 2]:
    square(n)
print(square.cache_info())
