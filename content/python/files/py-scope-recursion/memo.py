# 4.2 Scope and recursion: LEGB, closures and the call stack
# Example "memo" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from functools import lru_cache

calls = 0
def fib(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print("fib(25) =", fib(25), "after", calls, "calls")

@lru_cache(maxsize=None)        # remember every answer (a decorator, Advanced 1.2)
def fast_fib(n):
    if n < 2:
        return n
    return fast_fib(n - 1) + fast_fib(n - 2)

print("fast_fib(25) =", fast_fib(25), fast_fib.cache_info())
print("fast_fib(300) =", fast_fib(300))

def loop_fib(n):                # the same answer with a loop and two names
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

print(loop_fib(25), loop_fib(300) == fast_fib(300))
