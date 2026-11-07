# 5.1 Threads and processes
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
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


# ================================================================== 1114. Print in Order (Easy)
# https://leetcode.com/problems/print-in-order/
# Pattern: Two Events
# Idea: second waits for an Event that first sets, and third waits for one that second sets. The
# threads may start in any order.

import threading


class Foo:
    def __init__(self):
        self.first_done = threading.Event()
        self.second_done = threading.Event()

    def first(self, printFirst):
        printFirst()
        self.first_done.set()

    def second(self, printSecond):
        self.first_done.wait()
        printSecond()
        self.second_done.set()

    def third(self, printThird):
        self.second_done.wait()
        printThird()


def run_foo(order):
    foo = Foo()
    out = []
    jobs = {1: lambda: foo.first(lambda: out.append("first")),
            2: lambda: foo.second(lambda: out.append("second")),
            3: lambda: foo.third(lambda: out.append("third"))}
    run_all([jobs[n] for n in order])
    return "".join(out)


import threading


def run_all(targets):
    """Start every target in its own thread, then wait for all of them."""
    threads = [threading.Thread(target=t) for t in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    return all(not t.is_alive() for t in threads)


# ================================================================== 1115. Print FooBar Alternately (Medium)
# https://leetcode.com/problems/print-foobar-alternately/
# Pattern: Two Semaphores take turns
# Idea: foo starts with one permit and bar with none. Each thread waits on its own semaphore and
# then gives a permit to the other one.

import threading


class FooBar:
    def __init__(self, n):
        self.n = n
        self.foo_turn = threading.Semaphore(1)
        self.bar_turn = threading.Semaphore(0)

    def foo(self, printFoo):
        for _ in range(self.n):
            self.foo_turn.acquire()
            printFoo()
            self.bar_turn.release()

    def bar(self, printBar):
        for _ in range(self.n):
            self.bar_turn.acquire()
            printBar()
            self.foo_turn.release()


def run_foobar(n):
    fb = FooBar(n)
    out = []
    run_all([lambda: fb.bar(lambda: out.append("bar")), lambda: fb.foo(lambda: out.append("foo"))])
    return "".join(out)


import threading


def run_all(targets):
    """Start every target in its own thread, then wait for all of them."""
    threads = [threading.Thread(target=t) for t in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    return all(not t.is_alive() for t in threads)


# ================================================================== 1116. Print Zero Even Odd (Medium)
# https://leetcode.com/problems/print-zero-even-odd/
# Pattern: Three Semaphores
# Idea: zero prints 0 and then wakes odd or even depending on the next number. odd and even print
# and wake zero again.

import threading


class ZeroEvenOdd:
    def __init__(self, n):
        self.n = n
        self.zero_turn = threading.Semaphore(1)
        self.odd_turn = threading.Semaphore(0)
        self.even_turn = threading.Semaphore(0)

    def zero(self, printNumber):
        for i in range(1, self.n + 1):
            self.zero_turn.acquire()
            printNumber(0)
            if i % 2 == 1:
                self.odd_turn.release()
            else:
                self.even_turn.release()

    def even(self, printNumber):
        for i in range(2, self.n + 1, 2):
            self.even_turn.acquire()
            printNumber(i)
            self.zero_turn.release()

    def odd(self, printNumber):
        for i in range(1, self.n + 1, 2):
            self.odd_turn.acquire()
            printNumber(i)
            self.zero_turn.release()


def run_zero_even_odd(n):
    zeo = ZeroEvenOdd(n)
    out = []
    run_all([lambda: zeo.even(out.append), lambda: zeo.odd(out.append), lambda: zeo.zero(out.append)])
    return "".join(str(x) for x in out)


import threading


def run_all(targets):
    """Start every target in its own thread, then wait for all of them."""
    threads = [threading.Thread(target=t) for t in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    return all(not t.is_alive() for t in threads)


# ================================================================== 1117. Building H2O (Medium)
# https://leetcode.com/problems/building-h2o/
# Pattern: Semaphores for places, a Barrier for the group
# Idea: A Semaphore(2) lets two hydrogen in, a Semaphore(1) one oxygen. A Barrier(3) makes the three
# wait for each other before they bond.

import threading


class H2O:
    def __init__(self):
        self.h_places = threading.Semaphore(2)
        self.o_places = threading.Semaphore(1)
        self.barrier = threading.Barrier(3)

    def hydrogen(self, releaseHydrogen):
        with self.h_places:
            self.barrier.wait()
            releaseHydrogen()

    def oxygen(self, releaseOxygen):
        with self.o_places:
            self.barrier.wait()
            releaseOxygen()


def run_h2o(water):
    h2o = H2O()
    out = []
    jobs = []
    for atom in water:
        if atom == "H":
            jobs.append(lambda: h2o.hydrogen(lambda: out.append("H")))
        else:
            jobs.append(lambda: h2o.oxygen(lambda: out.append("O")))
    run_all(jobs)
    return [sorted(out[i:i + 3]) for i in range(0, len(out), 3)]


import threading


def run_all(targets):
    """Start every target in its own thread, then wait for all of them."""
    threads = [threading.Thread(target=t) for t in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    return all(not t.is_alive() for t in threads)


# ================================================================== 1195. Fizz Buzz Multithreaded (Medium)
# https://leetcode.com/problems/fizz-buzz-multithreaded/
# Pattern: One Condition and a shared counter
# Idea: Every thread waits until the current number is its kind (or the end is reached), prints,
# moves the counter on and wakes the others with notify_all.

import threading


class FizzBuzz:
    def __init__(self, n):
        self.n = n
        self.current = 1
        self.turn = threading.Condition()

    def _run(self, mine, action):
        while True:
            with self.turn:
                self.turn.wait_for(lambda: self.current > self.n or mine(self.current))
                if self.current > self.n:
                    return
                action(self.current)
                self.current += 1
                self.turn.notify_all()

    def fizz(self, printFizz):
        self._run(lambda i: i % 3 == 0 and i % 5 != 0, lambda i: printFizz())

    def buzz(self, printBuzz):
        self._run(lambda i: i % 5 == 0 and i % 3 != 0, lambda i: printBuzz())

    def fizzbuzz(self, printFizzBuzz):
        self._run(lambda i: i % 15 == 0, lambda i: printFizzBuzz())

    def number(self, printNumber):
        self._run(lambda i: i % 3 != 0 and i % 5 != 0, printNumber)


def run_fizzbuzz(n):
    fb = FizzBuzz(n)
    out = []
    run_all([lambda: fb.fizz(lambda: out.append("fizz")), lambda: fb.buzz(lambda: out.append("buzz")),
             lambda: fb.fizzbuzz(lambda: out.append("fizzbuzz")), lambda: fb.number(out.append)])
    return out


import threading


def run_all(targets):
    """Start every target in its own thread, then wait for all of them."""
    threads = [threading.Thread(target=t) for t in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    return all(not t.is_alive() for t in threads)


# ================================================================== 1226. The Dining Philosophers (Medium)
# https://leetcode.com/problems/the-dining-philosophers/
# Pattern: Always take the lower numbered fork first
# Idea: A deadlock needs a cycle of waiting. If every philosopher takes the lower numbered fork
# first, no cycle can form, so somebody can always eat.

import threading


class DiningPhilosophers:
    def __init__(self):
        self.forks = [threading.Lock() for _ in range(5)]

    def wantsToEat(self, philosopher, pickLeftFork, pickRightFork, eat, putLeftFork, putRightFork):
        left = philosopher
        right = (philosopher + 1) % 5
        with self.forks[min(left, right)]:
            with self.forks[max(left, right)]:
                pickLeftFork()
                pickRightFork()
                eat()
                putLeftFork()
                putRightFork()


def run_dining(times):
    table = DiningPhilosophers()
    meals = [0] * 5
    eating = set()
    clashes = []
    guard = threading.Lock()

    def eat_as(p):
        with guard:
            if (p - 1) % 5 in eating or (p + 1) % 5 in eating:
                clashes.append(p)
            eating.add(p)
        meals[p] += 1
        with guard:
            eating.discard(p)

    def philosopher(p):
        for _ in range(times):
            table.wantsToEat(p, lambda: None, lambda: None, lambda: eat_as(p), lambda: None, lambda: None)

    finished = run_all([lambda p=p: philosopher(p) for p in range(5)])
    return [meals, len(clashes), finished]


import threading


def run_all(targets):
    """Start every target in its own thread, then wait for all of them."""
    threads = [threading.Thread(target=t) for t in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    return all(not t.is_alive() for t in threads)


# ================================================================== 1834. Single-Threaded CPU (Medium)
# https://leetcode.com/problems/single-threaded-cpu/
# Pattern: A heap of ready tasks
# Idea: Sort tasks by arrival. Push every task that has arrived into a heap of (time needed, index),
# run the shortest, and jump ahead in time when nothing is ready.

import heapq


def get_order(tasks):
    order = sorted(range(len(tasks)), key=lambda i: tasks[i][0])
    ready = []
    result = []
    time = 0
    i = 0
    while len(result) < len(tasks):
        if not ready and time < tasks[order[i]][0]:
            time = tasks[order[i]][0]
        while i < len(order) and tasks[order[i]][0] <= time:
            heapq.heappush(ready, (tasks[order[i]][1], order[i]))
            i += 1
        duration, index = heapq.heappop(ready)
        time += duration
        result.append(index)
    return result


# ================================================================== 1882. Process Tasks Using Servers (Medium)
# https://leetcode.com/problems/process-tasks-using-servers/
# Pattern: A heap of free servers and a heap of busy ones
# Idea: Free servers by (weight, index), busy servers by (free time, weight, index). Before each
# task, move servers that are free again. If none is free, jump to the time the first one is.

import heapq


def assign_tasks(servers, tasks):
    free = [(weight, i) for i, weight in enumerate(servers)]
    heapq.heapify(free)
    busy = []
    result = []
    time = 0
    for j, duration in enumerate(tasks):
        time = max(time, j)
        if not free:
            time = max(time, busy[0][0])
        while busy and busy[0][0] <= time:
            ends, weight, i = heapq.heappop(busy)
            heapq.heappush(free, (weight, i))
        weight, i = heapq.heappop(free)
        heapq.heappush(busy, (time + duration, weight, i))
        result.append(i)
    return result


# ================================================================== 2402. Meeting Rooms III (Hard)
# https://leetcode.com/problems/meeting-rooms-iii/
# Pattern: Free rooms and busy rooms in two heaps
# Idea: Take meetings by start time. Free every room whose meeting has ended. Use the lowest free
# room, or delay the meeting until the room that frees first is free.

import heapq


def most_booked(n, meetings):
    free = list(range(n))
    heapq.heapify(free)
    busy = []
    count = [0] * n
    for start, end in sorted(meetings):
        while busy and busy[0][0] <= start:
            ends, room = heapq.heappop(busy)
            heapq.heappush(free, room)
        if free:
            room = heapq.heappop(free)
            heapq.heappush(busy, (end, room))
        else:
            ends, room = heapq.heappop(busy)
            heapq.heappush(busy, (ends + end - start, room))
        count[room] += 1
    return count.index(max(count))


# ================================================================== 1094. Car Pooling (Medium)
# https://leetcode.com/problems/car-pooling/
# Pattern: Changes at each point, then a running total
# Idea: At each pickup the load goes up and at each drop it goes down. Sort the points and add up
# the changes. Too many people at any point means False.

def car_pooling(trips, capacity):
    change = {}
    for people, start, end in trips:
        change[start] = change.get(start, 0) + people
        change[end] = change.get(end, 0) - people
    load = 0
    for place in sorted(change):
        load += change[place]
        if load > capacity:
            return False
    return True


if __name__ == "__main__":
    results = []
    results.append(check("1114. Print in Order", [('run_foo([1, 2, 3])', 'firstsecondthird'), ('run_foo([1, 3, 2])', 'firstsecondthird'), ('run_foo([3, 2, 1])', 'firstsecondthird')]))
    results.append(check("1115. Print FooBar Alternately", [('run_foobar(1)', 'foobar'), ('run_foobar(3)', 'foobarfoobarfoobar')]))
    results.append(check("1116. Print Zero Even Odd", [('run_zero_even_odd(2)', '0102'), ('run_zero_even_odd(5)', '0102030405')]))
    results.append(check("1117. Building H2O", [('run_h2o("HOH")', [['H', 'H', 'O']]), ('run_h2o("OOHHHH")', [['H', 'H', 'O'], ['H', 'H', 'O']])]))
    results.append(check("1195. Fizz Buzz Multithreaded", [('run_fizzbuzz(15)', [1, 2, 'fizz', 4, 'buzz', 'fizz', 7, 8, 'fizz', 'buzz', 11, 'fizz', 13, 14, 'fizzbuzz']), ('run_fizzbuzz(5)', [1, 2, 'fizz', 4, 'buzz'])]))
    results.append(check("1226. The Dining Philosophers", [('run_dining(3)', [[3, 3, 3, 3, 3], 0, True]), ('run_dining(50)', [[50, 50, 50, 50, 50], 0, True])]))
    results.append(check("1834. Single-Threaded CPU", [('get_order([[1, 2], [2, 4], [3, 2], [4, 1]])', [0, 2, 3, 1]), ('get_order([[7, 10], [7, 12], [7, 5], [7, 4], [7, 2]])', [4, 3, 2, 0, 1])]))
    results.append(check("1882. Process Tasks Using Servers", [('assign_tasks([3, 3, 2], [1, 2, 3, 2, 1, 2])', [2, 2, 0, 2, 1, 2]), ('assign_tasks([5, 1, 4, 3, 2], [2, 1, 2, 4, 5, 2, 1])', [1, 4, 1, 4, 1, 3, 2])]))
    results.append(check("2402. Meeting Rooms III", [('most_booked(2, [[0, 10], [1, 5], [2, 7], [3, 4]])', 0), ('most_booked(3, [[1, 20], [2, 10], [3, 5], [4, 9], [6, 8]])', 1)]))
    results.append(check("1094. Car Pooling", [('car_pooling([[2, 1, 5], [3, 3, 7]], 4)', False), ('car_pooling([[2, 1, 5], [3, 3, 7]], 5)', True), ('car_pooling([[2, 1, 5], [3, 5, 7]], 3)', True)]))
    if all(results):
        print("Every solution passes its tests.")
