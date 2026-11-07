# 5.1 Threads and processes
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: The speedup from Amdahl's law
# Write amdahl(p, n) that returns the speedup 1 / ((1 − p) + p / n), rounded to 2 decimals. p is the
# part of the work (0 to 1) that can run in parallel and n is the number of cores.
# Hint: The serial part (1 − p) takes the same time on any number of cores. Only p is divided by n.

def amdahl(p, n):
    return round(n * p, 2)


# ================================================================== task 2: A counter that always releases its lock
# Finish the class SafeCounter. add(amount) must change value while holding self.lock, and must
# raise ValueError for a negative amount. The starter forgets to release the lock when it raises, so
# the next add would wait for ever. Use with self.lock: so the lock is always released. (The tests
# run in one thread and check lock.locked().)
# Hint: Put the whole body of add inside with self.lock:. The with statement releases the lock when
# the block ends, also when it ends with an exception.

import threading


class SafeCounter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()

    def add(self, amount):
        self.lock.acquire()
        if amount < 0:
            raise ValueError("amount must not be negative")
        self.value += amount
        self.lock.release()


def try_negative(counter):
    try:
        counter.add(-1)
    except ValueError:
        return "ValueError"
    return "no error"


# ================================================================== task 3: Find the threads stuck in a deadlock
# waits is a dict: each thread name maps to the thread it is waiting for, or None. Write
# find_deadlock(waits) that returns the sorted names of the threads that form a cycle (they wait for
# each other in a ring), or [] if there is none. A thread that waits for a member of a cycle but is
# not in it is stuck too, but is not part of the cycle.
# Hint: From each thread follow the waits chain, remembering the order. If you meet a thread you
# have already seen, the part of the list from that thread on is the cycle.

def find_deadlock(waits):
    for name, other in waits.items():
        if other is not None and waits.get(other) == name:
            return sorted([name, other])
    return []


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The speedup from Amdahl's law", [('amdahl(0.9, 4)', 3.08), ('amdahl(0.5, 2)', 1.33), ('amdahl(1.0, 8)', 8.0), ('amdahl(0.0, 64)', 1.0), ('amdahl(0.95, 1000000)', 20.0)]))
    results.append(check("Task 2: A counter that always releases its lock", [('(lambda c: (c.add(2), c.add(3), c.value)[2])(SafeCounter())', 5), ('(lambda c: (c.add(1), c.lock.locked())[1])(SafeCounter())', False), ('(lambda c: (try_negative(c), c.lock.locked()))(SafeCounter())', ['ValueError', False]), ('(lambda c: (try_negative(c), c.lock.acquire(blocking=False)))(SafeCounter())', ['ValueError', True])]))
    results.append(check("Task 3: Find the threads stuck in a deadlock", [('find_deadlock({"T1": "T2", "T2": "T1"})', ['T1', 'T2']), ('find_deadlock({"A": "B", "B": "C", "C": None})', []), ('find_deadlock({"A": "B", "B": "C", "C": "B", "D": "A"})', ['B', 'C']), ('find_deadlock({"A": "B", "B": "C", "C": "A"})', ['A', 'B', 'C']), ('find_deadlock({})', [])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
