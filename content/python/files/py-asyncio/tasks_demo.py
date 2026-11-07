# 5.2 asyncio: async and await
# Example "tasks_demo" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import asyncio


async def job(name, seconds, fail=False):
    await asyncio.sleep(seconds)
    if fail:
        raise ValueError(f"{name} failed")
    return name


async def main():
    task = asyncio.create_task(job("background", 0.1))   # scheduled, runs at the next await
    print("created, done yet?", task.done())
    print(await task)

    async with asyncio.TaskGroup() as group:   # the block waits for every task in it
        a = group.create_task(job("a", 0.2))
        b = group.create_task(job("b", 0.1))
    print(a.result(), b.result())

    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(job("slow", 1))
            group.create_task(job("bad", 0.1, fail=True))
    except* ValueError as errors:              # the slow task was cancelled for us
        print("caught:", [str(e) for e in errors.exceptions])

    for next_done in asyncio.as_completed([job("x", 0.3), job("y", 0.1)]):
        print("finished:", await next_done)


asyncio.run(main())
