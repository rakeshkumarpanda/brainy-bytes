# 5.1 Threads and processes
# Example "race" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import threading
import time

counter = 0


def add_unsafe(times):
    global counter
    for _ in range(times):
        value = counter                        # 1. read
        time.sleep(0)                          # let another thread run right here
        counter = value + 1                    # 2. write: may wipe out another thread's update


threads = [threading.Thread(target=add_unsafe, args=(100,)) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("without a lock, updates were lost:", counter < 400)

counter = 0
lock = threading.Lock()


def add_safe(times):
    global counter
    for _ in range(times):
        with lock:                             # only one thread at a time inside this block
            value = counter
            time.sleep(0)
            counter = value + 1


threads = [threading.Thread(target=add_safe, args=(100,)) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("with a lock:", counter)
