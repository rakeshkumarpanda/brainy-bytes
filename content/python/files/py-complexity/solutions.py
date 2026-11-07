# 4.1 Complexity, timing and profiling
# Model solutions. Try practice.py first.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: Find a pair with a given sum in one pass
# Write has_pair_with_sum(nums, target) that returns True when two different positions in nums add
# up to target. Do it in O(n) with a set of the numbers seen so far, not with two nested loops. The
# starter looks fast but has a bug: it can use the same number twice.
# Why it works: One pass with a set is O(n) time and O(n) memory. Two nested loops would be O(n²)
# time and O(1) memory: the classic trade of memory for time.

def has_pair_with_sum(nums, target):
    seen = set()
    for x in nums:
        if target - x in seen:
            return True
        seen.add(x)
    return False


# ================================================================== task 2: Guess the Big O from step counts
# Write guess_big_o(steps_n, steps_2n). It gets the step count of an algorithm for some n and for
# 2n, and returns one of "O(1)", "O(log n)", "O(n)", "O(n^2)" or "O(2^n)". Use the ratio r =
# steps_2n / steps_n: r at most 1.05 is O(1), under 1.8 is O(log n), under 3 is O(n), under 6 is
# O(n^2), anything bigger is O(2^n).
# Why it works: This "doubling test" is a real technique: time a program at n and 2n and the ratio
# tells you its growth. Measure at large n, because small inputs hide the shape behind fixed costs.

def guess_big_o(steps_n, steps_2n):
    ratio = steps_2n / steps_n
    if ratio <= 1.05:
        return "O(1)"
    if ratio < 1.8:
        return "O(log n)"
    if ratio < 3:
        return "O(n)"
    if ratio < 6:
        return "O(n^2)"
    return "O(2^n)"


# ================================================================== task 3: A caching decorator that counts hits and misses
# Write a decorator memo(func) that stores results in a dict keyed by the positional arguments. The
# wrapper must have two attributes, hits (answer found in the cache) and misses (answer had to be
# computed), both starting at 0. fib is decorated with it so you can test.
# Why it works: functools.lru_cache and functools.cache do exactly this, written in C and with
# cache_info() to show hits and misses. Arguments must be hashable because they are dict keys.

def memo(func):
    cache = {}

    def wrapper(*args):
        if args in cache:
            wrapper.hits += 1
            return cache[args]
        wrapper.misses += 1
        result = func(*args)
        cache[args] = result
        return result

    wrapper.hits = 0
    wrapper.misses = 0
    return wrapper


@memo
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Find a pair with a given sum in one pass", [('has_pair_with_sum([2, 7, 11, 15], 9)', True), ('has_pair_with_sum([3], 6)', False), ('has_pair_with_sum([3, 3], 6)', True), ('has_pair_with_sum([1, 2, 4], 8)', False), ('has_pair_with_sum([], 0)', False)]))
    results.append(check("Task 2: Guess the Big O from step counts", [('guess_big_o(5, 5)', 'O(1)'), ('guess_big_o(10, 11)', 'O(log n)'), ('guess_big_o(100, 200)', 'O(n)'), ('guess_big_o(100, 400)', 'O(n^2)'), ('guess_big_o(1024, 1048576)', 'O(2^n)'), ('guess_big_o(1000, 1040)', 'O(1)')]))
    results.append(check("Task 3: A caching decorator that counts hits and misses", [('fib(30)', 832040), ('(fib(30), fib.misses)[1]', 31), ('(lambda f: [f(3), f(3), f(4), f.hits, f.misses])(memo(lambda x: x * 2))', [6, 6, 8, 1, 2]), ('(lambda f: [f(2, 3), f(2, 3), f.hits])(memo(pow))', [8, 8, 1])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
