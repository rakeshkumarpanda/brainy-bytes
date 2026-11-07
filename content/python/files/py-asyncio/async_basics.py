# 5.2 asyncio: async and await
# Example "async_basics" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import asyncio
import time


async def make_tea(name, seconds):
    print(f"{name}: start")
    await asyncio.sleep(seconds)               # waiting: the loop may run other code now
    print(f"{name}: ready")
    return name


async def main():
    start = time.perf_counter()
    await make_tea("green", 0.3)               # one after the other
    await make_tea("black", 0.2)
    print(f"in a row: {round(time.perf_counter() - start, 1)} s")

    start = time.perf_counter()
    results = await asyncio.gather(make_tea("green", 0.3), make_tea("black", 0.2))
    print(results, f"together: {round(time.perf_counter() - start, 1)} s")


coro = make_tea("test", 0)
print(type(coro).__name__)                     # calling an async def does not run it yet
coro.close()
asyncio.run(main())
