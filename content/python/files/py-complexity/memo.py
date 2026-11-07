# 4.1 Complexity, timing and profiling
# Example "memo" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from functools import lru_cache

calls = 0


def fib_slow(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)


print(fib_slow(20), "with", calls, "calls")

calls = 0


@lru_cache(maxsize=None)
def fib_fast(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib_fast(n - 1) + fib_fast(n - 2)


print(fib_fast(20), "with", calls, "calls")
print(fib_fast.cache_info())
