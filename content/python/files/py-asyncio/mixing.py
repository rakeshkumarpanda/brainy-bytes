# 5.2 asyncio: async and await
# Example "mixing" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import asyncio
import time


def blocking_read():
    time.sleep(0.3)                            # an old library that knows nothing about await
    return "data"


async def ticker():
    for i in range(3):
        print("tick", i)
        await asyncio.sleep(0.1)


async def main():
    start = time.perf_counter()
    results = await asyncio.gather(ticker(), asyncio.to_thread(blocking_read))
    print(results[1], f"after {round(time.perf_counter() - start, 1)} s, and the ticks kept going")


asyncio.run(main())
