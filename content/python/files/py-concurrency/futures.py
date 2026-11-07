# 5.1 Threads and processes
# Example "futures" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch(site, delay):
    time.sleep(delay)
    if site == "broken.example":
        raise ConnectionError(f"{site} did not answer")
    return f"{site} ok"


sites = {"a.example": 0.3, "b.example": 0.1, "broken.example": 0.2}
with ThreadPoolExecutor() as pool:
    futures = {pool.submit(fetch, site, delay): site for site, delay in sites.items()}
    for future in as_completed(futures):       # in the order they FINISH
        try:
            print(future.result())             # result() raises the error from the thread
        except ConnectionError as err:
            print("failed:", err)
