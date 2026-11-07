# 5.1 Threads and processes
# Model solutions. Try practice.py first.
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
# Why it works: The starter assumes everything gets n times faster, which never happens. With p =
# 0.95 a million cores give only 20 times, which is why profiling the serial part matters so much.

def amdahl(p, n):
    return round(1 / ((1 - p) + p / n), 2)


# ================================================================== task 2: A counter that always releases its lock
# Finish the class SafeCounter. add(amount) must change value while holding self.lock, and must
# raise ValueError for a negative amount. The starter forgets to release the lock when it raises, so
# the next add would wait for ever. Use with self.lock: so the lock is always released. (The tests
# run in one thread and check lock.locked().)
# Why it works: A lock left locked after an error is a classic source of programs that freeze for no
# visible reason. with lock: (chapter 2.3, context managers) makes that impossible.

import threading


class SafeCounter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()

    def add(self, amount):
        with self.lock:
            if amount < 0:
                raise ValueError("amount must not be negative")
            self.value += amount


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
# Why it works: Real databases and operating systems do this: they build a wait-for graph and look
# for a cycle. When they find one, they cancel one transaction or thread so the others can go on.

def find_deadlock(waits):
    for start in waits:
        seen = []
        current = start
        while current is not None and current not in seen:
            seen.append(current)
            current = waits.get(current)
        if current is not None:
            cycle_start = seen.index(current)
            return sorted(seen[cycle_start:])
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
