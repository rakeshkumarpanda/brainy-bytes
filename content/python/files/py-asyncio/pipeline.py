# 5.2 asyncio: async and await
# Example "pipeline" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import asyncio


async def producer(queue, n):
    for i in range(1, n + 1):
        await queue.put(i)                     # waits while the queue is full
        print("made", i)
    await queue.put(None)                      # the stop signal


async def consumer(queue, results):
    while True:
        item = await queue.get()               # waits while the queue is empty
        if item is None:
            break
        await asyncio.sleep(0.01)              # pretend each item takes some work
        results.append(item * item)


async def main():
    queue = asyncio.Queue(maxsize=2)
    results = []
    await asyncio.gather(producer(queue, 5), consumer(queue, results))
    print(results)


asyncio.run(main())
