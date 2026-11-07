# 5.1 Threads and processes
# Example "io_threads" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import time
from concurrent.futures import ThreadPoolExecutor


def download(page):
    time.sleep(0.5)                            # stands for waiting on the network
    return f"{page}: done"


pages = ["home", "shop", "cart", "help"]

start = time.perf_counter()
results = [download(p) for p in pages]
one_by_one = time.perf_counter() - start

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(download, pages))  # map keeps the order of the inputs
with_threads = time.perf_counter() - start

print(results)
print(f"one by one: about {round(one_by_one, 1)} s")
print(f"4 threads:  about {round(with_threads, 1)} s")
