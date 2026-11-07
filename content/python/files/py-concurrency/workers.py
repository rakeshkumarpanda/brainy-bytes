# 5.1 Threads and processes
# Example "workers" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import queue
import threading

jobs = queue.Queue()
results = queue.Queue()


def worker():
    while True:
        n = jobs.get()                         # waits until there is a job
        if n is None:                          # the stop signal
            break
        results.put((n, n * n))


workers = [threading.Thread(target=worker) for _ in range(3)]
for w in workers:
    w.start()
for n in range(1, 8):
    jobs.put(n)
for _ in workers:
    jobs.put(None)                             # one stop signal for each worker
for w in workers:
    w.join()

answers = sorted(results.get() for _ in range(results.qsize()))
print(answers)
