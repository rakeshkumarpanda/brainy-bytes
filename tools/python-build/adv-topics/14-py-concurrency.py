# Advanced Python 5.1: threads and processes. Checked against the Python 3.14 documentation of threading,
# queue, concurrent.futures, multiprocessing (forkserver became the default start method on Linux in 3.14),
# the glossary entry for the GIL, the free-threaded build (PEP 703, officially supported in 3.14 by PEP 779) and
# sys._is_gil_enabled(). The terminal runs below are real, on a 4 core Linux machine with CPython 3.14.6 and the
# free-threaded CPython 3.14.6t.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, lc, leet, files, grow, leet_items, show, term

chapter('py-concurrency')
K = Kit()

WHY = 'Browsers cannot start threads or processes, so the in page Python cannot run it.'

K.code('io_threads', r'''
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
''')

K.code('thread_basics', r'''
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
''')

K.code('race', r'''
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
''')

K.code('workers', r'''
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
''')

K.code('futures', r'''
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
''')

CPU = '''import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def count_primes(limit):
    count = 0
    for n in range(2, limit):
        is_prime = True
        d = 2
        while d * d <= n:
            if n % d == 0:
                is_prime = False
                break
            d += 1
        if is_prime:
            count += 1
    return count


def timed(label, run):
    start = time.perf_counter()
    results = run()
    print(f"{label:<12} {time.perf_counter() - start:5.2f} s  {results}")


if __name__ == "__main__":
    jobs = [200_000] * 4
    timed("one by one", lambda: [count_primes(n) for n in jobs])
    with ThreadPoolExecutor(max_workers=4) as pool:
        timed("4 threads", lambda: list(pool.map(count_primes, jobs)))
    with ProcessPoolExecutor(max_workers=4) as pool:
        timed("4 processes", lambda: list(pool.map(count_primes, jobs)))'''

SHARED = '''import multiprocessing as mp
import os


def square(n):
    return n * n


def report(q, name):
    q.put(f"{name} ran in its own process: {os.getpid() != os.getppid()}")


if __name__ == "__main__":                     # needed: child processes import this file again
    with mp.Pool(processes=4) as pool:
        print(pool.map(square, range(10)))

    q = mp.Queue()
    workers = [mp.Process(target=report, args=(q, f"worker {i}")) for i in range(2)]
    for w in workers:
        w.start()
    for w in workers:
        w.join()
    print(sorted(q.get() for _ in workers))
    print("start method:", mp.get_start_method())'''

K.lesson('idea', 'Doing many things at once', f'''
{src('Python 3.14 documentation of threading, queue, concurrent.futures and multiprocessing, the GIL, and the free-threaded build (PEP 703 and PEP 779). Terminal outputs are real runs on a 4 core machine.')}
{wwh('<b>Concurrency</b> means a program deals with several jobs during the same period, switching between them. <b>Parallelism</b> means jobs really run at the same moment on different CPU cores. A <b>thread</b> is a path of execution inside one process that shares its memory. A <b>process</b> is a separate running program with its own memory.',
     'Most programs spend time waiting: for the network, the disk or a database. While one job waits, the computer could do another. Other programs do heavy calculations, and a modern computer has 4 to 16 cores that sit idle if the program uses only one. Doing jobs one after another wastes both.',
     'Threads let other work run while one job waits for I/O. Processes run Python code on several cores at once. concurrent.futures gives both the same simple interface: a pool of workers, submit or map, and futures that hold results.')}
{viz('pygil')}
{local('io_threads', WHY)}
{note('Four downloads of 0.5 seconds take 2 seconds one by one but only 0.5 seconds with four threads, because the waiting happens at the same time. While a thread waits for I/O (sleep, network, files) it lets go of the GIL, so others can run.', 'tip')}
{table(['Kind of work', 'Example', 'Best tool'], [
    ['I/O bound: mostly waiting', 'Downloading pages, calling APIs, reading many files, database queries', 'Threads (or asyncio, chapter 5.2)'],
    ['CPU bound: mostly calculating', 'Image processing, prime numbers, simulations, parsing huge files', 'Processes (or the free-threaded build, or NumPy which releases the GIL)'],
    ['A mix', 'A web crawler that also parses pages', 'Threads or asyncio for I/O, a process pool for the heavy parts']])}
''', kw=['concurrency', 'parallelism', 'thread', 'process', 'I/O bound', 'CPU bound', 'ThreadPoolExecutor', 'GIL'])

K.lesson('threads', 'Threads: start, join and share', f'''
{local('thread_basics', WHY)}
{table(['threading', 'Does'], [
    ['Thread(target=f, args=(...), name=...)', 'Makes a thread that will run f(*args)'],
    ['t.start()', 'Starts it. It runs next to the main thread'],
    ['t.join(timeout=None)', 'Waits until t has finished'],
    ['Thread(..., daemon=True)', 'A background thread that does not keep the program alive'],
    ['threading.current_thread(), active_count()', 'Which thread is running this line, how many threads exist']])}
{note('Every thread in a process shares the same global variables and objects. That makes it easy to pass data, and also easy to break data: two threads changing the same object at the same time is a race condition.', 'warn')}
''', kw=['threading', 'Thread', 'start', 'join', 'daemon', 'current_thread', 'shared memory'])

K.lesson('locks', 'Race conditions and locks', f'''
{local('race', WHY)}
{note('counter = counter + 1 is really three steps: read, add, write. If another thread writes between your read and your write, your write wipes out its update. time.sleep(0) here forces a switch at the worst moment, but real programs hit the same bug by chance, often only under heavy load.', 'warn')}
{table(['Tool', 'Use it to'], [
    ['Lock', 'Let only one thread at a time run a block (use with lock:)'],
    ['RLock', 'A lock the same thread may take again, for recursive code'],
    ['Semaphore(n)', 'Let at most n threads in at once, for example 5 connections'],
    ['Event', 'Let threads wait until one sets a flag: event.set(), event.wait()'],
    ['Condition', 'Wait until some state is true, with wait_for and notify_all'],
    ['Barrier(n)', 'Wait until n threads have all arrived'],
    ['queue.Queue', 'Pass data between threads safely, with no lock code of your own']])}
{note('A <b>deadlock</b> happens when thread 1 holds lock A and waits for lock B while thread 2 holds B and waits for A. Neither can go on. Prevent it by always taking locks in the same order, holding them briefly, or using a timeout.', 'exam')}
''', kw=['race condition', 'Lock', 'RLock', 'Semaphore', 'Event', 'Condition', 'Barrier', 'deadlock', 'thread safety'])

K.lesson('queues', 'Worker threads with queue and futures', f'''
{local('workers', WHY)}
{note('queue.Queue does the locking for you. Producers put jobs in, worker threads get them out. get() waits when the queue is empty. Putting one None per worker is a common way to tell workers to stop.', 'tip')}
{local('futures', WHY)}
{versus('Ways to run work in threads', ['', 'threading.Thread', 'queue.Queue + workers', 'ThreadPoolExecutor'], [
    ['Get results back', 'By hand (shared dict or list)', 'A results queue', 'Futures: result(), map, as_completed'],
    ['Errors in the thread', 'Printed and lost', 'You must catch them', 'Raised again by result()'],
    ['Limit how many run at once', 'By hand', 'Number of workers', 'max_workers'],
    ['Best for', 'One long background job', 'Long running pipelines', 'Most everyday jobs']],
    'start with ThreadPoolExecutor. Use queues for pipelines, and bare Thread objects only for one background job.')}
''', kw=['queue.Queue', 'producer consumer', 'worker threads', 'sentinel', 'concurrent.futures', 'submit', 'Future', 'as_completed', 'map'])

K.lesson('gil', 'The GIL and processes', f'''
<p>The <b>GIL</b> (global interpreter lock) lets only one thread run Python bytecode at a time in the normal CPython build. It keeps the interpreter simple and fast for one thread, but it means threads cannot use several cores for pure Python work. This file does the same CPU heavy work one by one, with threads and with processes:</p>
{show('cpu_bound.py', CPU, {26: 'Child processes import this file again, so the start code must sit under the if __name__ == "__main__" guard.', 31: 'A ProcessPoolExecutor has the same interface as the thread pool. The function and its arguments are pickled and sent to the child processes.'})}
{term(['$ python3.14 cpu_bound.py',
       'one by one    1.30 s  [17984, 17984, 17984, 17984]',
       '4 threads     1.37 s  [17984, 17984, 17984, 17984]',
       '4 processes   0.40 s  [17984, 17984, 17984, 17984]',
       '$ python3.14t -c "import sys; print(sys._is_gil_enabled())"',
       'False',
       '$ python3.14t cpu_bound.py',
       'one by one    1.16 s  [17984, 17984, 17984, 17984]',
       '4 threads     0.35 s  [17984, 17984, 17984, 17984]',
       '4 processes   0.41 s  [17984, 17984, 17984, 17984]'], 'Real runs: normal CPython and the free-threaded build')}
{note('With the GIL, 4 threads are no faster than one (1.37 s against 1.30 s). 4 processes are 3.3 times faster. The free-threaded build python3.14t (officially supported since 3.14) has no GIL, so there 4 threads are fast too.', 'exam')}
{show('shared.py', SHARED)}
{term(['$ python3.14 shared.py',
       '[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]',
       "['worker 0 ran in its own process: True', 'worker 1 ran in its own process: True']",
       'start method: forkserver'], 'multiprocessing (real run)')}
{versus('Threads or processes', ['', 'Threads', 'Processes'], [
    ['Memory', 'Shared: easy to pass data, easy to break it', 'Separate: data is pickled and copied'],
    ['Pure Python CPU work on many cores', 'No, with the GIL (yes in python3.14t)', 'Yes'],
    ['Start up cost', 'Small', 'Bigger (a new interpreter)'],
    ['A crash', 'Can take the whole program down', 'Stays inside one process'],
    ['Best for', 'I/O bound work', 'CPU bound work']],
    'threads for waiting, processes for calculating. Measure, because the overhead of processes can be bigger than the gain for small jobs.')}
{deep('Start methods and new options in 3.14', '<p>multiprocessing can start children by fork (copy the parent, Unix only), spawn (start a fresh Python, the default on Windows and macOS) or forkserver (ask a small clean server process to fork, the default on Linux since 3.14). With spawn and forkserver the child imports your main file, which is why the __main__ guard is required. Python 3.14 also added concurrent.interpreters and InterpreterPoolExecutor: several interpreters in one process, each with its own GIL (PEP 734).</p>')}
''', kw=['GIL', 'global interpreter lock', 'multiprocessing', 'ProcessPoolExecutor', 'Pool', '__main__ guard', 'pickle', 'free-threaded', 'python3.14t', 'fork', 'spawn', 'forkserver', 'subinterpreters'])

K.lesson('maths', 'The maths: speedup, Amdahl and pool sizes', f'''
{fxs(fx('Speedup and efficiency', 'S = T<sub>1</sub> / T<sub>n</sub>, E = S / n', '1.30 s alone, 0.40 s with 4 processes: S = 3.25, E = 0.8125 (about 81 %).', key=True),
     fx("Amdahl's law", 'S(n) = 1 / ((1 &minus; p) + p / n)', 'p = 0.9 of the work can run in parallel, n = 4: S = 1 / (0.1 + 0.225) &asymp; 3.08.', key=True),
     fx("The limit of Amdahl's law", 'S(&infin;) = 1 / (1 &minus; p)', 'With p = 0.9, even a million cores give at most 10 times.'),
     fx("Gustafson's law", 'S(n) = n &minus; (1 &minus; p)(n &minus; 1)', 'If the problem grows with the cores: n = 4, p = 0.9 gives 3.7.'),
     fx('Threads for I/O work', 'threads &asymp; cores &times; (1 + wait time / compute time)', '4 cores, 90 ms waiting and 10 ms computing per job: 4 &times; 10 = 40 threads.', key=True),
     fx("Little's law", 'L = &lambda; &times; W', '200 requests per second that each take 0.25 s: 50 requests in progress, so about 50 workers.'),
     fx('Lost updates', 'final = expected &minus; lost', '4 threads &times; 100 additions should give 400. Every overwrite loses one.'))}
{steps('Worked example: is it worth buying 8 more cores?', [
    'A job takes 100 s. Profiling shows 80 s can run in parallel, so p = 0.8.',
    'With 4 cores: S = 1 / (0.2 + 0.8 / 4) = 1 / 0.4 = 2.5, so 40 s.',
    'With 12 cores: S = 1 / (0.2 + 0.8 / 12) = 1 / 0.2667 &asymp; 3.75, so about 26.7 s.',
    'The 20 s serial part never shrinks. Making it faster helps more than more cores.',
    eq('8 more cores: from 40 s to about 26.7 s, never below 20 s')])}
''', kw=['speedup', 'efficiency', "Amdahl's law", "Gustafson's law", "Little's law", 'thread pool size', 'parallel fraction'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Run I/O jobs in a ThreadPoolExecutor and know that threads help with waiting, not with calculating.</p>',
    '<p>Start and join threads, protect shared data with a Lock, pass work through queue.Queue, use futures with as_completed, and use a ProcessPoolExecutor with the __main__ guard for CPU work.</p>',
    '<p>Explain the GIL, race conditions and deadlocks, choose between Event, Condition, Semaphore and Barrier, and size pools with Amdahl and Little.</p>',
    '<p>Use the free-threaded build and know which C extensions are ready for it, use subinterpreters, shared memory (multiprocessing.shared_memory) and lock free designs, and reason about memory ordering and contention.</p>')}
{grow('Use a thread pool for I/O.', 'Write correct threaded and multiprocess code.', 'Design and tune parallel systems.')}
''', kw=['beginner', 'expert', 'shared_memory', 'lock free', 'contention'])

RUNNER = '''

import threading


def run_all(targets):
    """Start every target in its own thread, then wait for all of them."""
    threads = [threading.Thread(target=t) for t in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    return all(not t.is_alive() for t in threads)
'''

lc(1114, 'Print in Order', 'print-in-order', 'e', 'Two Events', 'second waits for an Event that first sets, and third waits for one that second sets. The threads may start in any order.', r'''
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
''' + RUNNER, [('run_foo([1, 2, 3])', 'firstsecondthird'), ('run_foo([1, 3, 2])', 'firstsecondthird'), ('run_foo([3, 2, 1])', 'firstsecondthird')])
lc(1115, 'Print FooBar Alternately', 'print-foobar-alternately', 'm', 'Two Semaphores take turns', 'foo starts with one permit and bar with none. Each thread waits on its own semaphore and then gives a permit to the other one.', r'''
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
''' + RUNNER, [('run_foobar(1)', 'foobar'), ('run_foobar(3)', 'foobarfoobarfoobar')])
lc(1116, 'Print Zero Even Odd', 'print-zero-even-odd', 'm', 'Three Semaphores', 'zero prints 0 and then wakes odd or even depending on the next number. odd and even print and wake zero again.', r'''
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
''' + RUNNER, [('run_zero_even_odd(2)', '0102'), ('run_zero_even_odd(5)', '0102030405')])
lc(1117, 'Building H2O', 'building-h2o', 'm', 'Semaphores for places, a Barrier for the group', 'A Semaphore(2) lets two hydrogen in, a Semaphore(1) one oxygen. A Barrier(3) makes the three wait for each other before they bond.', r'''
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
''' + RUNNER, [('run_h2o("HOH")', [['H', 'H', 'O']]), ('run_h2o("OOHHHH")', [['H', 'H', 'O'], ['H', 'H', 'O']])])
lc(1195, 'Fizz Buzz Multithreaded', 'fizz-buzz-multithreaded', 'm', 'One Condition and a shared counter', 'Every thread waits until the current number is its kind (or the end is reached), prints, moves the counter on and wakes the others with notify_all.', r'''
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
''' + RUNNER, [('run_fizzbuzz(15)', [1, 2, 'fizz', 4, 'buzz', 'fizz', 7, 8, 'fizz', 'buzz', 11, 'fizz', 13, 14, 'fizzbuzz']), ('run_fizzbuzz(5)', [1, 2, 'fizz', 4, 'buzz'])])
lc(1226, 'The Dining Philosophers', 'the-dining-philosophers', 'm', 'Always take the lower numbered fork first', 'A deadlock needs a cycle of waiting. If every philosopher takes the lower numbered fork first, no cycle can form, so somebody can always eat.', r'''
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
''' + RUNNER, [('run_dining(3)', [[3, 3, 3, 3, 3], 0, True]), ('run_dining(50)', [[50, 50, 50, 50, 50], 0, True])])
lc(1834, 'Single-Threaded CPU', 'single-threaded-cpu', 'm', 'A heap of ready tasks', 'Sort tasks by arrival. Push every task that has arrived into a heap of (time needed, index), run the shortest, and jump ahead in time when nothing is ready.', r'''
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
''', [('get_order([[1, 2], [2, 4], [3, 2], [4, 1]])', [0, 2, 3, 1]), ('get_order([[7, 10], [7, 12], [7, 5], [7, 4], [7, 2]])', [4, 3, 2, 0, 1])])
lc(1882, 'Process Tasks Using Servers', 'process-tasks-using-servers', 'm', 'A heap of free servers and a heap of busy ones', 'Free servers by (weight, index), busy servers by (free time, weight, index). Before each task, move servers that are free again. If none is free, jump to the time the first one is.', r'''
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
''', [('assign_tasks([3, 3, 2], [1, 2, 3, 2, 1, 2])', [2, 2, 0, 2, 1, 2]), ('assign_tasks([5, 1, 4, 3, 2], [2, 1, 2, 4, 5, 2, 1])', [1, 4, 1, 4, 1, 3, 2])])
lc(2402, 'Meeting Rooms III', 'meeting-rooms-iii', 'h', 'Free rooms and busy rooms in two heaps', 'Take meetings by start time. Free every room whose meeting has ended. Use the lowest free room, or delay the meeting until the room that frees first is free.', r'''
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
''', [('most_booked(2, [[0, 10], [1, 5], [2, 7], [3, 4]])', 0), ('most_booked(3, [[1, 20], [2, 10], [3, 5], [4, 9], [6, 8]])', 1)])
lc(1094, 'Car Pooling', 'car-pooling', 'm', 'Changes at each point, then a running total', 'At each pickup the load goes up and at each drop it goes down. Sort the points and add up the changes. Too many people at any point means False.', r'''
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
''', [('car_pooling([[2, 1, 5], [3, 3, 7]], 4)', False), ('car_pooling([[2, 1, 5], [3, 3, 7]], 5)', True), ('car_pooling([[2, 1, 5], [3, 5, 7]], 3)', True)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>The first six are LeetCode\'s concurrency problems: they are solved with exactly the tools of this chapter (Event, Semaphore, Barrier, Condition and Lock), and each download has a small runner that starts the threads in different orders to test them. The last four simulate how a CPU or a pool of servers schedules jobs, using heaps.</p>'), kw=['LeetCode', 'concurrency', 'Event', 'Semaphore', 'Barrier', 'Condition', 'dining philosophers', 'scheduling'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Threads share memory inside one process. Processes have their own memory and their own interpreter.',
    'I/O bound work: threads (they let go of the GIL while waiting). CPU bound work: processes, or python3.14t without the GIL.',
    'ThreadPoolExecutor and ProcessPoolExecutor share one interface: submit, map, as_completed and futures whose result() raises errors.',
    'Shared data needs a Lock (use with lock:). queue.Queue passes work safely. Take locks in one order to avoid deadlocks.',
    'Process code needs the if __name__ == "__main__" guard, and its data must be picklable.',
    "Amdahl's law: the serial part limits the speedup, S(n) = 1 / ((1 &minus; p) + p / n)."],
    'Next, asyncio: thousands of waiting jobs in one thread with async and await.')}
{files('Three tasks: the speedup from Amdahl\'s law, a counter that always releases its lock, and finding threads stuck in a deadlock.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which kind of work do threads speed up in normal CPython?', ['Pure Python calculations', 'Work that waits for the network or disk', 'Neither', 'Only sorting'], 1, 'Waiting releases the GIL.', 'While a thread waits for I/O, other threads can run.')
K.quiz('e', 'What does t.join() do?', ['Starts the thread', 'Waits until the thread has finished', 'Stops the thread at once', 'Joins two threads into one'], 1, 'Wait.', 'join blocks until that thread ends.')
K.quiz('e', 'Which tool runs CPU heavy pure Python code on several cores in normal CPython?', ['ThreadPoolExecutor', 'ProcessPoolExecutor', 'time.sleep', 'queue.Queue'], 1, 'Separate interpreters.', 'Each process has its own GIL.')
K.quiz('m', 'Why can counter += 1 in several threads give a wrong total?', ['Python cannot add', 'Read, add and write are separate steps, so one thread can overwrite another\'s update', 'Threads use different counters', 'Integers are immutable'], 1, 'Race condition.', 'Protect the update with a Lock.')
K.quiz('m', 'What is the best way to use a Lock?', ['lock.acquire() alone', 'with lock:', 'lock.release() first', 'Make it global and never release it'], 1, 'Released even on errors.', 'The with block releases the lock even if an exception happens.')
K.quiz('m', 'Why must multiprocessing start code be under if __name__ == "__main__"?', ['It is faster', 'Child processes may import the main file again and would start new children forever', 'Style only', 'To use threads'], 1, 'spawn and forkserver.', 'The guard stops the import in the child from running the start code.')
K.quiz('m', 'In what order does as_completed give futures?', ['The order they were submitted', 'The order they finish', 'Random', 'Sorted by result'], 1, 'Completed.', 'Fastest first.')
K.quiz('m', 'What does future.result() do when the function raised an exception in the thread?', ['Returns None', 'Raises the same exception in your thread', 'Prints a warning', 'Hangs'], 1, 'Errors come back.', 'That is a big advantage of executors over bare threads.')
K.quiz('h', 'Thread 1 holds lock A and waits for B. Thread 2 holds B and waits for A. What is this?', ['A race condition', 'A deadlock', 'The GIL', 'Starvation'], 1, 'Nobody can move.', 'Taking locks in one fixed order prevents it.')
K.quiz('h', 'What does sys._is_gil_enabled() return in python3.14t by default?', ['True', 'False', 'None', 'It raises an error'], 1, 'Free-threaded.', 'The free-threaded build runs without the GIL unless a C extension needs it or PYTHON_GIL=1 is set.')
K.quiz('h', 'Which object lets at most 5 threads use a database at once?', ['Lock', 'Event', 'Semaphore(5)', 'Barrier(5)'], 2, 'A counter of permits.', 'Each acquire takes a permit, each release gives one back.')
K.quiz('x', "In the style of a CMU 15-418 exam: 95 % of a program can run in parallel. By Amdahl's law, what is the most speedup any number of cores can give?", ['95 times', '20 times', '100 times', 'No limit'], 1, '1 / (1 &minus; p).', '1 / 0.05 = 20. The serial 5 % always remains.')
K.quiz('x', 'In the style of an MIT 6.033 exam: the dining philosophers deadlock is prevented by numbering forks and always taking the lower number first. Which deadlock condition does this break?', ['Mutual exclusion', 'Hold and wait', 'No preemption', 'Circular wait'], 3, 'A cycle is impossible.', 'With a global lock order, a waiting chain can only go up in number, so it can never come back to its start.')

K.calc('e', 'Four downloads of 0.5 s each run one by one. How many seconds in total?', '2', '4 &times; 0.5.', ['The waits add up.', '4 &times; 0.5 = 2.', eq('2 s')], check=2)
K.calc('e', 'The same four downloads run in four threads at once. About how many seconds?', '0.5', 'The waits overlap.', ['All four wait at the same time.', 'The longest one decides.', eq('about 0.5 s')], check=0.5)
K.calc('e', 'A job takes 1.30 s alone and 0.40 s with 4 processes. What is the speedup, to 2 decimals?', '3.25', 'T<sub>1</sub> / T<sub>n</sub>.', ['1.30 / 0.40.', '= 3.25.', eq('S = 3.25')], check=round(1.30 / 0.40, 2))
K.calc('m', 'With that speedup of 3.25 on 4 cores, what is the efficiency in percent?', '81.25', 'E = S / n.', ['3.25 / 4 = 0.8125.', 'As a percentage.', eq('81.25 %')], check=3.25 / 4 * 100)
K.calc('m', "Amdahl's law with p = 0.9 and n = 4. What is the speedup, to 2 decimals?", '3.08', '1 / ((1 &minus; p) + p / n).', ['(1 &minus; 0.9) + 0.9 / 4 = 0.1 + 0.225 = 0.325.', '1 / 0.325.', eq('&asymp; 3.08')], check=round(1 / (0.1 + 0.9 / 4), 2))
K.calc('m', 'A pool on 4 cores: each job computes for 10 ms and waits 90 ms. How many threads does the rule of thumb suggest?', '40', 'cores &times; (1 + wait / compute).', ['90 / 10 = 9.', '4 &times; (1 + 9).', eq('40 threads')], check=4 * (1 + 90 // 10))
K.calc('m', "200 requests per second each take 0.25 s. By Little's law how many are in progress at once?", '50', 'L = &lambda; &times; W.', ['&lambda; = 200, W = 0.25.', '200 &times; 0.25.', eq('50')], check=int(200 * 0.25))
K.calc('h', 'Split range(10) into 3 parts as evenly as possible, in order. How many items has the first part?', '4', '10 = 3 &times; 3 + 1.', ['Each part gets 3.', 'The 1 left over goes to the first part.', eq('4, 3, 3')], check=4)
K.calc('h', "Amdahl's law with p = 0.8. What is the speedup on 12 cores, to 2 decimals?", '3.75', '1 / (0.2 + 0.8 / 12).', ['0.8 / 12 &asymp; 0.0667.', '1 / 0.2667.', eq('3.75')], check=round(1 / (0.2 + 0.8 / 12), 2))
K.calc('x', "In the style of a CMU 15-418 exam: by Gustafson's law, what is the scaled speedup on 16 cores with p = 0.95, to 2 decimals?", '15.25', 'n &minus; (1 &minus; p)(n &minus; 1).', ['(1 &minus; 0.95) &times; 15 = 0.75.', '16 &minus; 0.75.', eq('15.25')], check=round(16 - 0.05 * 15, 2))

K.assign('amdahl', 'e', "The speedup from Amdahl's law",
         "<p>Write <code>amdahl(p, n)</code> that returns the speedup 1 / ((1 &minus; p) + p / n), rounded to 2 decimals. p is the part of the work (0 to 1) that can run in parallel and n is the number of cores.</p>",
         '''
def amdahl(p, n):
    return round(n * p, 2)
''', [('amdahl(0.9, 4)', 3.08), ('amdahl(0.5, 2)', 1.33), ('amdahl(1.0, 8)', 8.0), ('amdahl(0.0, 64)', 1.0), ('amdahl(0.95, 1000000)', 20.0)],
         '''
def amdahl(p, n):
    return round(1 / ((1 - p) + p / n), 2)
''', 'The serial part (1 &minus; p) takes the same time on any number of cores. Only p is divided by n.', "<p>The starter assumes everything gets n times faster, which never happens. With p = 0.95 a million cores give only 20 times, which is why profiling the serial part matters so much.</p>")
K.assign('safe', 'm', 'A counter that always releases its lock',
         '<p>Finish the class <code>SafeCounter</code>. add(amount) must change value while holding self.lock, and must raise ValueError for a negative amount. The starter forgets to release the lock when it raises, so the next add would wait for ever. Use <code>with self.lock:</code> so the lock is always released. (The tests run in one thread and check lock.locked().)</p>',
         '''
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
''', [('(lambda c: (c.add(2), c.add(3), c.value)[2])(SafeCounter())', 5), ('(lambda c: (c.add(1), c.lock.locked())[1])(SafeCounter())', False), ('(lambda c: (try_negative(c), c.lock.locked()))(SafeCounter())', ['ValueError', False]), ('(lambda c: (try_negative(c), c.lock.acquire(blocking=False)))(SafeCounter())', ['ValueError', True])],
         '''
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
''', 'Put the whole body of add inside with self.lock:. The with statement releases the lock when the block ends, also when it ends with an exception.', '<p>A lock left locked after an error is a classic source of programs that freeze for no visible reason. with lock: (chapter 2.3, context managers) makes that impossible.</p>')
K.assign('deadlock', 'h', 'Find the threads stuck in a deadlock',
         '<p>waits is a dict: each thread name maps to the thread it is waiting for, or None. Write <code>find_deadlock(waits)</code> that returns the sorted names of the threads that form a cycle (they wait for each other in a ring), or [] if there is none. A thread that waits for a member of a cycle but is not in it is stuck too, but is not part of the cycle.</p>',
         '''
def find_deadlock(waits):
    for name, other in waits.items():
        if other is not None and waits.get(other) == name:
            return sorted([name, other])
    return []
''', [('find_deadlock({"T1": "T2", "T2": "T1"})', ['T1', 'T2']), ('find_deadlock({"A": "B", "B": "C", "C": None})', []), ('find_deadlock({"A": "B", "B": "C", "C": "B", "D": "A"})', ['B', 'C']), ('find_deadlock({"A": "B", "B": "C", "C": "A"})', ['A', 'B', 'C']), ('find_deadlock({})', [])],
         '''
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
''', 'From each thread follow the waits chain, remembering the order. If you meet a thread you have already seen, the part of the list from that thread on is the cycle.', '<p>Real databases and operating systems do this: they build a wait-for graph and look for a cycle. When they find one, they cancel one transaction or thread so the others can go on.</p>')

K.must('When to use what', 'I/O bound: threads or asyncio. CPU bound: processes (or python3.14t). Measure first.')
K.must('Threads', 'Thread(target, args), start, join, daemon. Shared memory means races: protect with with lock:.')
K.must('Sync tools', 'Lock, RLock, Semaphore(n), Event, Condition, Barrier, queue.Queue. Same lock order everywhere to avoid deadlock.')
K.must('Executors', 'ThreadPoolExecutor and ProcessPoolExecutor: submit, map (keeps order), as_completed (finish order), result() raises errors.')
K.must('Processes', 'if __name__ == "__main__" guard, picklable functions and data, start methods fork, spawn, forkserver (Linux default in 3.14).')

T = K.topic(
    slug='py-concurrency', topic='py-concurrency', step=(5, 'Doing many things at once: threads, processes and asyncio', 'py-a5', 'Use waiting time and every CPU core: threads for I/O, processes for heavy work, and asyncio for thousands of connections.', 'Advanced'),
    title='Threads and processes', short='Threads and processes', badge='5.1', minutes=80,
    lead='Make programs do several things at once. Learn concurrency and parallelism, threads and their races, locks and the other sync tools, worker queues, concurrent.futures, the GIL, multiprocessing, and the free-threaded build of Python 3.14.',
    desc='concurrency versus parallelism, I/O bound and CPU bound work, threading.Thread, start and join, race conditions, Lock, RLock, Semaphore, Event, Condition, Barrier, deadlock, queue.Queue workers, ThreadPoolExecutor, submit, map, as_completed, futures, the GIL, ProcessPoolExecutor, multiprocessing Pool, Process and Queue, the __main__ guard, start methods, free-threaded python3.14t, subinterpreters, Amdahl, Gustafson and Little.',
    summary='threads, races and locks, worker queues, futures, the GIL, processes and free-threaded Python.',
    keywords=['concurrency', 'parallelism', 'threading', 'Lock', 'race condition', 'deadlock', 'queue', 'concurrent.futures', 'GIL', 'multiprocessing', 'free-threaded'],
    recap='<p>Threads for waiting, processes for calculating, a lock around shared data, and Amdahl to know how much faster it can ever get.</p>',
    added='2026-11-07', leet=leet_items())
