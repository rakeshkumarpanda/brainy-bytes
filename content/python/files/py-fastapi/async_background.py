# 5.2 FastAPI: fast, typed APIs with automatic docs
# Example "async_background" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import asyncio
import time
from contextlib import asynccontextmanager

import httpx
from fastapi import BackgroundTasks, FastAPI

EVENTS = []


@asynccontextmanager
async def lifespan(app):                                   # runs once at start up and once at shut down
    EVENTS.append("start: open the database pool")
    yield
    EVENTS.append("stop: close the pool")


app = FastAPI(lifespan=lifespan)


@app.get("/slow-async")
async def slow_async():
    await asyncio.sleep(0.2)                               # waiting on the network or a database, the right way
    return {"done": True}


@app.get("/slow-sync")
def slow_sync():
    time.sleep(0.2)                                        # a blocking call: FastAPI runs plain def endpoints in a thread pool
    return {"done": True}


@app.get("/blocking-async")
async def blocking_async():
    time.sleep(0.2)                                        # THE MISTAKE: a blocking call inside async def stops the event loop
    return {"done": True}


def send_email(address):
    EVENTS.append(f"email sent to {address}")


@app.post("/signup")
async def signup(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_email, email)                      # runs after the answer has been sent
    EVENTS.append("answer sent")
    return {"ok": True}


async def timed(client, path, n):
    start = time.perf_counter()
    await asyncio.gather(*[client.get(path) for _ in range(n)])
    return time.perf_counter() - start


async def main():
    transport = httpx.ASGITransport(app=app)               # call the app directly, no network
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            for path in ["/slow-async", "/slow-sync", "/blocking-async"]:
                seconds = await timed(client, path, 10)
                print(f"10 requests at once to {path:15}: {seconds:.1f} s (one alone takes 0.2 s)")
            await client.post("/signup", params={"email": "ann@example.com"})
    print(EVENTS)


asyncio.run(main())
