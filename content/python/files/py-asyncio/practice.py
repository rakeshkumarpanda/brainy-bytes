# 5.2 asyncio: async and await
# Practice tasks. Fill in each function, then run this file.
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


# ================================================================== task 1: Fix the missing await
# add_tax is a coroutine. total must return the sum of add_tax(p) for every price, rounded to 2
# decimals, but the starter forgets to await, so it tries to add coroutine objects. Fix total. The
# tests run it with drive(), a tiny helper that runs a coroutine without an event loop.
# Hint: Write await in front of add_tax(p). Without it you get a coroutine object, not a number.

async def add_tax(price):
    return price * 1.2


async def total(prices):
    result = 0
    for p in prices:
        result = result + add_tax(p)
    return round(result, 2)


def drive(coro):
    """Run a coroutine that never really has to wait, without an event loop."""
    try:
        coro.send(None)
    except StopIteration as done:
        return done.value
    raise RuntimeError("the coroutine had to wait")


# ================================================================== task 2: An async generator and an async comprehension
# Write an async generator countdown(n) that yields n, n − 1, ..., 1, and an async function
# collect_squares(n) that returns the squares of the countdown values using an async comprehension:
# [x * x async for x in countdown(n)].
# Hint: An async def that contains yield is an async generator. Read it with async for, or with an
# async comprehension.

async def countdown(n):
    return list(range(n, 0, -1))


async def collect_squares(n):
    return [x * x for x in await countdown(n)]


def drive(coro):
    """Run a coroutine that never really has to wait, without an event loop."""
    try:
        coro.send(None)
    except StopIteration as done:
        return done.value
    raise RuntimeError("the coroutine had to wait")


# ================================================================== task 3: A tiny round robin scheduler
# An event loop switches between tasks at every await. Build the same idea with plain generators.
# round_robin(tasks) gets a list of generators. It runs the first one until its next yield, then the
# next one, and so on, round and round, dropping each generator when it is finished. Return the list
# of every value yielded, in that order. worker(name, steps) is a sample task. Use
# collections.deque.
# Hint: Keep the tasks in a deque. Take one from the front, run it to its next yield with next(),
# and put it at the back. If it raises StopIteration it is finished, so do not put it back.

from collections import deque


def worker(name, steps):
    for i in range(steps):
        yield f"{name}{i}"


def round_robin(tasks):
    log = []
    for task in tasks:
        for value in task:
            log.append(value)
    return log


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Fix the missing await", [('drive(total([10, 20]))', 36.0), ('drive(total([]))', 0), ('drive(total([0.5]))', 0.6)]))
    results.append(check("Task 2: An async generator and an async comprehension", [('drive(collect_squares(3))', [9, 4, 1]), ('drive(collect_squares(0))', []), ('type(countdown(2)).__name__', 'async_generator')]))
    results.append(check("Task 3: A tiny round robin scheduler", [('round_robin([worker("A", 2), worker("B", 3)])', ['A0', 'B0', 'A1', 'B1', 'B2']), ('round_robin([])', []), ('round_robin([worker("X", 1), worker("Y", 0), worker("Z", 2)])', ['X0', 'Z0', 'Z1'])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
