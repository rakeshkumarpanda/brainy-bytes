# 5.2 asyncio: async and await
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
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


# ================================================================== 2621. Sleep (Easy)
# https://leetcode.com/problems/sleep/
# Pattern: await asyncio.sleep
# Idea: LeetCode asks this one in JavaScript. In Python asyncio the same idea is a coroutine that
# awaits asyncio.sleep(millis / 1000).

import asyncio
import time


async def sleep(millis):
    await asyncio.sleep(millis / 1000)
    return millis


async def timed_sleep(millis):
    start = time.perf_counter()
    await sleep(millis)
    elapsed = (time.perf_counter() - start) * 1000
    return millis - 5 <= elapsed <= millis + 200


# ================================================================== 2723. Add Two Promises (Easy)
# https://leetcode.com/problems/add-two-promises/
# Pattern: Await both at the same time
# Idea: A JavaScript problem. In Python, gather awaits both coroutines at the same time and returns
# their values, so the total wait is the longer one, not the sum.

import asyncio


async def add_two_promises(first, second):
    a, b = await asyncio.gather(first, second)
    return a + b


import asyncio


async def later(value, ms):
    """A small async helper: returns value after ms milliseconds."""
    await asyncio.sleep(ms / 1000)
    return value


async def try_call(func, *args):
    try:
        return await func(*args)
    except Exception as err:
        return str(err)


# ================================================================== 2648. Generate Fibonacci Sequence (Easy)
# https://leetcode.com/problems/generate-fibonacci-sequence/
# Pattern: An endless generator
# Idea: A JavaScript generator problem. In Python, a while True loop with yield gives the numbers
# one at a time, and itertools.islice takes as many as you need.

from itertools import islice


def fib_generator():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# ================================================================== 2649. Nested Array Generator (Medium)
# https://leetcode.com/problems/nested-array-generator/
# Pattern: yield from for the nested lists
# Idea: A JavaScript generator problem. Walk the list, and for a nested list hand over to a
# recursive generator with yield from.

def inorder_traversal(items):
    for item in items:
        if isinstance(item, list):
            yield from inorder_traversal(item)
        else:
            yield item


# ================================================================== 2637. Promise Time Limit (Medium)
# https://leetcode.com/problems/promise-time-limit/
# Pattern: asyncio.wait_for
# Idea: A JavaScript problem. Wrap the coroutine in asyncio.wait_for with the limit in seconds, and
# turn the TimeoutError into the message the problem asks for.

import asyncio


def time_limit(func, t):
    async def limited(*args):
        try:
            return await asyncio.wait_for(func(*args), t / 1000)
        except TimeoutError:
            raise TimeoutError("Time Limit Exceeded") from None
    return limited


async def slow_double(n, ms):
    await asyncio.sleep(ms / 1000)
    return n * 2


import asyncio


async def later(value, ms):
    """A small async helper: returns value after ms milliseconds."""
    await asyncio.sleep(ms / 1000)
    return value


async def try_call(func, *args):
    try:
        return await func(*args)
    except Exception as err:
        return str(err)


# ================================================================== 2721. Execute Asynchronous Functions in Parallel (Medium)
# https://leetcode.com/problems/execute-asynchronous-functions-in-parallel/
# Pattern: gather keeps the order
# Idea: A JavaScript problem (write Promise.all without Promise.all). In Python, gather starts all
# of them, keeps the results in the order given and raises the first error.

import asyncio


async def promise_all(functions):
    results = await asyncio.gather(*(f() for f in functions))
    return list(results)


async def fails():
    await asyncio.sleep(0.01)
    raise ValueError("Error")


import asyncio


async def later(value, ms):
    """A small async helper: returns value after ms milliseconds."""
    await asyncio.sleep(ms / 1000)
    return value


async def try_call(func, *args):
    try:
        return await func(*args)
    except Exception as err:
        return str(err)


# ================================================================== 2622. Cache With Time Limit (Medium)
# https://leetcode.com/problems/cache-with-time-limit/
# Pattern: Store the value with its end time
# Idea: A JavaScript design problem. Keep key: (value, expires_at). A key counts only while the
# clock is before its end time. The clock is passed in so the tests do not have to wait.

import time


class TimeLimitedCache:
    def __init__(self, clock=None):
        self.clock = clock or (lambda: time.monotonic() * 1000)
        self.items = {}

    def _alive(self, key):
        return key in self.items and self.items[key][1] > self.clock()

    def set(self, key, value, duration):
        existed = self._alive(key)
        self.items[key] = (value, self.clock() + duration)
        return existed

    def get(self, key):
        return self.items[key][0] if self._alive(key) else -1

    def count(self):
        return sum(1 for key in self.items if self._alive(key))


def demo_cache():
    now = [0]
    cache = TimeLimitedCache(clock=lambda: now[0])
    out = [cache.set(1, 42, 100)]
    now[0] = 50
    out += [cache.get(1), cache.count()]
    now[0] = 150
    out += [cache.get(1), cache.count()]
    return out


# ================================================================== 2627. Debounce (Medium)
# https://leetcode.com/problems/debounce/
# Pattern: Cancel the waiting call and schedule a new one
# Idea: A JavaScript problem. With asyncio, loop.call_later schedules the call. A new call cancels
# the handle of the one still waiting.

import asyncio


def debounce(func, t):
    handle = None

    def debounced(*args):
        nonlocal handle
        if handle is not None:
            handle.cancel()
        handle = asyncio.get_running_loop().call_later(t / 1000, func, *args)

    return debounced


async def demo_debounce():
    log = []
    typed = debounce(log.append, 50)
    typed("a")
    await asyncio.sleep(0.03)
    typed("b")                                 # "a" was still waiting, so it is cancelled
    await asyncio.sleep(0.12)
    typed("c")
    await asyncio.sleep(0.12)
    return log


# ================================================================== 2636. Promise Pool (Medium)
# https://leetcode.com/problems/promise-pool/
# Pattern: n workers share one iterator
# Idea: A JavaScript problem. Start n worker coroutines that all take the next function from the
# same iterator. At most n functions run at any moment.

import asyncio


async def promise_pool(functions, n):
    jobs = iter(functions)

    async def worker():
        for job in jobs:
            await job()

    await asyncio.gather(*(worker() for _ in range(n)))


async def demo_pool(n):
    running = 0
    peak = 0

    async def job():
        nonlocal running, peak
        running += 1
        peak = max(peak, running)
        await asyncio.sleep(0.01)
        running -= 1

    await promise_pool([job] * 5, n)
    return peak


# ================================================================== 2650. Design Cancellable Function (Hard)
# https://leetcode.com/problems/design-cancellable-function/
# Pattern: Drive a generator by hand, race each wait against cancel
# Idea: A JavaScript problem, and exactly how await works inside: send each result into the
# generator, throw errors into it, and throw a Cancelled error if cancel() wins the race.

import asyncio


class Cancelled(Exception):
    pass


def cancellable(gen):
    stop = asyncio.Event()

    def cancel():
        stop.set()

    async def run():
        value = None
        error = None
        while True:
            try:
                if error is not None:
                    awaitable = gen.throw(error)
                else:
                    awaitable = gen.send(value)
            except StopIteration as done:
                return done.value
            error = None
            value = None
            job = asyncio.ensure_future(awaitable)
            stopper = asyncio.ensure_future(stop.wait())
            finished, pending = await asyncio.wait({job, stopper}, return_when=asyncio.FIRST_COMPLETED)
            for other in pending:
                other.cancel()
            if stopper in finished and job not in finished:
                stop.clear()
                error = Cancelled("Cancelled")
            elif job.exception() is not None:
                error = job.exception()
            else:
                value = job.result()

    return cancel, run()


def adder():
    total = 0
    try:
        total += (yield later(1, 20))
        total += (yield later(2, 40))
        return total
    except Cancelled:
        return f"cancelled at {total}"


async def demo_cancellable(cancel_after):
    cancel, job = cancellable(adder())
    if cancel_after is not None:
        asyncio.get_running_loop().call_later(cancel_after / 1000, cancel)
    return await job


import asyncio


async def later(value, ms):
    """A small async helper: returns value after ms milliseconds."""
    await asyncio.sleep(ms / 1000)
    return value


async def try_call(func, *args):
    try:
        return await func(*args)
    except Exception as err:
        return str(err)


if __name__ == "__main__":
    results = []
    results.append(check("2621. Sleep", [('asyncio.run(timed_sleep(100))', True), ('asyncio.run(sleep(10))', 10)]))
    results.append(check("2723. Add Two Promises", [('asyncio.run(add_two_promises(later(2, 20), later(5, 60)))', 7), ('asyncio.run(add_two_promises(later(10, 50), later(-12, 30)))', -2)]))
    results.append(check("2648. Generate Fibonacci Sequence", [('list(islice(fib_generator(), 5))', [0, 1, 1, 2, 3]), ('list(islice(fib_generator(), 0))', [])]))
    results.append(check("2649. Nested Array Generator", [('list(inorder_traversal([[[6]], [1, 3], []]))', [6, 1, 3]), ('list(inorder_traversal([]))', []), ('list(inorder_traversal([1, [2, [3, [4]]], 5]))', [1, 2, 3, 4, 5])]))
    results.append(check("2637. Promise Time Limit", [('asyncio.run(try_call(time_limit(slow_double, 100), 5, 30))', 10), ('asyncio.run(try_call(time_limit(slow_double, 50), 5, 200))', 'Time Limit Exceeded')]))
    results.append(check("2721. Execute Asynchronous Functions in Parallel", [('asyncio.run(promise_all([lambda: later(1, 30), lambda: later(2, 10)]))', [1, 2]), ('asyncio.run(try_call(promise_all, [lambda: later(1, 30), fails]))', 'Error')]))
    results.append(check("2622. Cache With Time Limit", [('demo_cache()', [False, 42, 1, -1, 0])]))
    results.append(check("2627. Debounce", [('asyncio.run(demo_debounce())', ['b', 'c'])]))
    results.append(check("2636. Promise Pool", [('asyncio.run(demo_pool(2))', 2), ('asyncio.run(demo_pool(10))', 5), ('asyncio.run(demo_pool(1))', 1)]))
    results.append(check("2650. Design Cancellable Function", [('asyncio.run(demo_cancellable(None))', 3), ('asyncio.run(demo_cancellable(35))', 'cancelled at 1')]))
    if all(results):
        print("Every solution passes its tests.")
