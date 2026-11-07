# 5.2 asyncio: async and await
# Example "timeouts" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import asyncio


async def slow_answer():
    await asyncio.sleep(1)
    return 42


async def main():
    try:
        async with asyncio.timeout(0.2):       # Python 3.11+
            await slow_answer()
    except TimeoutError:
        print("gave up after 0.2 s")

    print(await asyncio.wait_for(slow_answer(), timeout=2))

    task = asyncio.create_task(slow_answer())
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("cancelled:", task.cancelled())

    limit = asyncio.Semaphore(2)               # at most 2 at a time
    running = 0
    peak = 0

    async def limited(n):
        nonlocal running, peak
        async with limit:
            running += 1
            peak = max(peak, running)
            await asyncio.sleep(0.05)
            running -= 1
        return n * 10

    print(await asyncio.gather(*(limited(n) for n in range(5))), "at most", peak, "at once")


asyncio.run(main())
