# 2.2 Real API work: pages, retries, limits and validation
# Example "httpx_async" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import asyncio
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx

# ---------- A tiny practice API where every answer takes 0.2 seconds ----------
class SlowAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(0.2)
        number = int(self.path.rsplit("/", 1)[1])
        body = json.dumps({"id": number, "square": number * number}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), SlowAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"

# ---------- The part to learn: the same 5 calls, one by one and at the same time ----------
NUMBERS = range(1, 6)

with httpx.Client(base_url=BASE, timeout=5) as client:          # works like requests.Session
    start = time.perf_counter()
    squares = [client.get(f"/numbers/{n}").json()["square"] for n in NUMBERS]
    print("one by one:     ", squares, f"{time.perf_counter() - start:.1f} s")


async def fetch_all(client, limit):
    gate = asyncio.Semaphore(limit)                # at most `limit` calls at the same time

    async def fetch(n):
        async with gate:
            r = await client.get(f"/numbers/{n}")
            r.raise_for_status()
            return r.json()["square"]

    return await asyncio.gather(*(fetch(n) for n in NUMBERS))


async def main():
    async with httpx.AsyncClient(base_url=BASE, timeout=5) as client:
        for limit in (5, 2):
            start = time.perf_counter()
            squares = await fetch_all(client, limit)
            print(f"async, {limit} at a time:", squares, f"{time.perf_counter() - start:.1f} s")


asyncio.run(main())
server.shutdown()
