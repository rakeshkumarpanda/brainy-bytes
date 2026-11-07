# 5.1 Threads and processes
# Example "thread_basics" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import threading
import time

results = {}


def worker(name, seconds):
    time.sleep(seconds)
    results[name] = threading.current_thread().name


threads = []
for i, seconds in enumerate([0.3, 0.1, 0.2]):
    t = threading.Thread(target=worker, args=(f"job{i}", seconds), name=f"T{i}")
    threads.append(t)
    t.start()                                  # it starts now and runs next to the main thread
print("the main thread goes on while the jobs sleep:", len(results))
for t in threads:
    t.join()                                   # wait until this thread has finished
print(sorted(results.items()))
print(threading.current_thread().name, threading.active_count())
