# Advanced Python 5.2: asyncio. Checked against the Python 3.14 documentation of asyncio (coroutines and tasks,
# asyncio.run, gather, TaskGroup and except* from 3.11, asyncio.timeout from 3.11, wait_for, as_completed,
# Semaphore, Queue, to_thread, cancellation), PEP 492 (async and await), PEP 525 (async generators) and the httpx
# AsyncClient documentation. The httpx terminal run below is real, against a local test server that answers
# each request after 0.2 s.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, lc, leet, files, grow, leet_items, show, term

chapter('py-asyncio')
K = Kit()

WHY = 'The Python in this page lives inside the browser\'s own event loop, so asyncio.run cannot start a loop of its own here.'

K.code('async_basics', r'''
import asyncio
import time


async def make_tea(name, seconds):
    print(f"{name}: start")
    await asyncio.sleep(seconds)               # waiting: the loop may run other code now
    print(f"{name}: ready")
    return name


async def main():
    start = time.perf_counter()
    await make_tea("green", 0.3)               # one after the other
    await make_tea("black", 0.2)
    print(f"in a row: {round(time.perf_counter() - start, 1)} s")

    start = time.perf_counter()
    results = await asyncio.gather(make_tea("green", 0.3), make_tea("black", 0.2))
    print(results, f"together: {round(time.perf_counter() - start, 1)} s")


coro = make_tea("test", 0)
print(type(coro).__name__)                     # calling an async def does not run it yet
coro.close()
asyncio.run(main())
''')

K.code('tasks_demo', r'''
import asyncio


async def job(name, seconds, fail=False):
    await asyncio.sleep(seconds)
    if fail:
        raise ValueError(f"{name} failed")
    return name


async def main():
    task = asyncio.create_task(job("background", 0.1))   # scheduled, runs at the next await
    print("created, done yet?", task.done())
    print(await task)

    async with asyncio.TaskGroup() as group:   # the block waits for every task in it
        a = group.create_task(job("a", 0.2))
        b = group.create_task(job("b", 0.1))
    print(a.result(), b.result())

    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(job("slow", 1))
            group.create_task(job("bad", 0.1, fail=True))
    except* ValueError as errors:              # the slow task was cancelled for us
        print("caught:", [str(e) for e in errors.exceptions])

    for next_done in asyncio.as_completed([job("x", 0.3), job("y", 0.1)]):
        print("finished:", await next_done)


asyncio.run(main())
''')

K.code('timeouts', r'''
import asyncio


async def slow_answer():
    await asyncio.sleep(1)
    return 42


async def main():
    try:
        async with asyncio.timeout(0.2):       # Python 3.11+
            await slow_answer()
    except TimeoutError:
        print("gave up after 0.2 s")

    print(await asyncio.wait_for(slow_answer(), timeout=2))

    task = asyncio.create_task(slow_answer())
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("cancelled:", task.cancelled())

    limit = asyncio.Semaphore(2)               # at most 2 at a time
    running = 0
    peak = 0

    async def limited(n):
        nonlocal running, peak
        async with limit:
            running += 1
            peak = max(peak, running)
            await asyncio.sleep(0.05)
            running -= 1
        return n * 10

    print(await asyncio.gather(*(limited(n) for n in range(5))), "at most", peak, "at once")


asyncio.run(main())
''')

K.code('pipeline', r'''
import asyncio


async def producer(queue, n):
    for i in range(1, n + 1):
        await queue.put(i)                     # waits while the queue is full
        print("made", i)
    await queue.put(None)                      # the stop signal


async def consumer(queue, results):
    while True:
        item = await queue.get()               # waits while the queue is empty
        if item is None:
            break
        await asyncio.sleep(0.01)              # pretend each item takes some work
        results.append(item * item)


async def main():
    queue = asyncio.Queue(maxsize=2)
    results = []
    await asyncio.gather(producer(queue, 5), consumer(queue, results))
    print(results)


asyncio.run(main())
''')

K.code('mixing', r'''
import asyncio
import time


def blocking_read():
    time.sleep(0.3)                            # an old library that knows nothing about await
    return "data"


async def ticker():
    for i in range(3):
        print("tick", i)
        await asyncio.sleep(0.1)


async def main():
    start = time.perf_counter()
    results = await asyncio.gather(ticker(), asyncio.to_thread(blocking_read))
    print(results[1], f"after {round(time.perf_counter() - start, 1)} s, and the ticks kept going")


asyncio.run(main())
''')

SERVER = '''import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class SlowHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(0.2)                        # pretend the server needs 0.2 s
        body = f"page {self.path}".encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):              # keep the terminal quiet
        pass


class Server(ThreadingHTTPServer):
    request_queue_size = 64                    # accept many connections at once


Server(("127.0.0.1", 8001), SlowHandler).serve_forever()'''

FETCH = '''import asyncio
import time

import httpx

URLS = [f"http://127.0.0.1:8001/{n}" for n in range(20)]


def fetch_one_by_one():
    with httpx.Client() as client:
        return [client.get(url).text for url in URLS]


async def fetch_together():
    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(*(client.get(url) for url in URLS))
        return [r.text for r in responses]


start = time.perf_counter()
pages = fetch_one_by_one()
print(f"one by one: {time.perf_counter() - start:.2f} s for {len(pages)} pages")

start = time.perf_counter()
pages = asyncio.run(fetch_together())
print(f"asyncio:    {time.perf_counter() - start:.2f} s for {len(pages)} pages")
print(pages[:3])'''

K.lesson('idea', 'asyncio: many waits in one thread', f'''
{src('Python 3.14 documentation of asyncio, PEP 492 (async and await), PEP 525 (async generators) and httpx. The httpx run is real, against a local server that answers after 0.2 s.')}
{wwh('<b>asyncio</b> runs many tasks in <b>one thread</b>. A function written with <b>async def</b> is a <b>coroutine</b>: it can pause at every <b>await</b> while it waits for something, and an <b>event loop</b> runs another coroutine in the meantime.',
     'A web server or a crawler may have thousands of network connections open, each waiting most of the time. One thread per connection costs memory and needs locks. asyncio handles them all in one thread, and because a task can only be paused at an await, shared data cannot change in the middle of a line.',
     'You write normal looking code with await in front of anything that waits: await asyncio.sleep(1), await client.get(url). The event loop keeps a queue of tasks that are ready to run, and a list of tasks that wait for a time or for network data. asyncio.run(main()) starts the loop. asyncio.gather and TaskGroup run coroutines at the same time.')}
{viz('pyloop')}
{local('async_basics', WHY)}
{note('Calling make_tea(...) only creates a coroutine object, it runs nothing. The code runs when it is awaited, or when it is wrapped in a task (gather, create_task, TaskGroup). Forgetting await is the most common asyncio bug: Python warns "coroutine ... was never awaited".', 'warn')}
{table(['Word', 'Means'], [
    ['async def f()', 'Defines a coroutine function. Calling it gives a coroutine object'],
    ['await x', 'Pause this coroutine until x is done, and let the loop run others. Only allowed inside async def'],
    ['Task', 'A coroutine scheduled on the loop. It runs on its own, next to the others'],
    ['Event loop', 'The scheduler: runs ready tasks one at a time and wakes waiting ones'],
    ['asyncio.run(main())', 'Start a loop, run main until it finishes, close the loop. Call it once, at the top']])}
''', kw=['asyncio', 'async def', 'await', 'coroutine', 'event loop', 'asyncio.run', 'gather', 'never awaited'])

K.lesson('tasks', 'Tasks, TaskGroup and as_completed', f'''
{local('tasks_demo', WHY)}
{table(['Tool', 'Use it to'], [
    ['asyncio.create_task(coro)', 'Start a coroutine in the background and get a Task you can await later'],
    ['await asyncio.gather(a, b, ...)', 'Run several and get their results as a list, in the order given'],
    ['async with asyncio.TaskGroup() as g', 'Start tasks with g.create_task. If one fails, the others are cancelled and errors come out as an ExceptionGroup'],
    ['asyncio.as_completed(aws)', 'Get results in the order they finish'],
    ['asyncio.wait(aws, return_when=...)', 'Wait for the first one, the first error, or all, and get done and pending sets']])}
{note('Keep a reference to every task you create with create_task (in a list or a set), or use a TaskGroup. The loop holds tasks only weakly, so a task nobody refers to can disappear before it finishes.', 'warn')}
{versus('Running coroutines together', ['', 'gather', 'TaskGroup (3.11+)'], [
    ['Results', 'A list in order', 'task.result() for each task'],
    ['When one fails', 'The error is raised, the others keep running (unless you cancel them)', 'The others are cancelled and all errors arrive in an ExceptionGroup'],
    ['Catching errors', 'try / except', 'try / except*'],
    ['Best for', 'A fixed list of jobs, return_exceptions=True to collect errors', 'Structured code where no task may be left running']],
    'TaskGroup for new code, because no task can be forgotten. gather is still fine for a simple list of results.')}
''', kw=['create_task', 'Task', 'gather', 'TaskGroup', 'ExceptionGroup', 'except*', 'as_completed', 'asyncio.wait', 'structured concurrency'])

K.lesson('control', 'Timeouts, cancelling and limits', f'''
{local('timeouts', WHY)}
{note('Cancelling a task raises CancelledError inside it at its current await. Clean up in finally blocks, and do not swallow CancelledError without raising it again, or the task cannot be stopped.', 'exam')}
{note('A Semaphore limits how many tasks do something at once. Without it, gathering 10,000 downloads opens 10,000 connections at the same moment, which servers often punish by refusing or blocking you.', 'tip')}
''', kw=['asyncio.timeout', 'wait_for', 'TimeoutError', 'cancel', 'CancelledError', 'Semaphore', 'rate limit'])

K.lesson('queues', 'Pipelines with asyncio.Queue', f'''
{local('pipeline', WHY)}
{note('asyncio.Queue is like queue.Queue, but put and get are awaited. With maxsize=2 the producer waits when two items are waiting. This <b>back pressure</b> stops a fast producer from filling memory while a slow consumer catches up.', 'tip')}
{deep('Async generators and async for', '<p>An async def with yield is an <b>async generator</b>: async for x in agen() awaits each value, and [x async for x in agen()] is an async comprehension. async with calls the awaitable methods __aenter__ and __aexit__, which is how httpx.AsyncClient and database connections clean up.</p>')}
''', kw=['asyncio.Queue', 'producer consumer', 'back pressure', 'async generator', 'async for', 'async with', 'async comprehension'])

K.lesson('real', 'Real network code, and blocking calls', f'''
<p>A small test server that answers every request after 0.2 seconds, and a client that fetches 20 pages one by one and then with asyncio and httpx (pip install httpx):</p>
{show('slow_server.py', SERVER)}
{show('fetch_all.py', FETCH, {14: 'One AsyncClient shares connections between all the requests.', 15: 'client.get(url) gives coroutines. gather runs all 20 at the same time and keeps the results in order.'})}
{term(['$ python3 slow_server.py &',
       '$ python3 fetch_all.py',
       'one by one: 4.09 s for 20 pages',
       'asyncio:    0.26 s for 20 pages',
       "['page /0', 'page /1', 'page /2']"], 'Real run (CPython 3.14, httpx 0.28)')}
{note('20 &times; 0.2 s = 4 s one by one. With asyncio all 20 waits overlap, so it takes about one wait: 0.26 s, 16 times faster, in one thread.', 'tip')}
{local('mixing', 'asyncio.to_thread starts a thread, which browsers do not allow.')}
{note('A normal blocking call (time.sleep, requests.get, a slow calculation) inside a coroutine freezes the whole loop. Use the async version (asyncio.sleep, httpx.AsyncClient, aiofiles), or push the blocking call to a thread with asyncio.to_thread, or to a process pool with loop.run_in_executor.', 'warn')}
{versus('Waiting for many things at once', ['', 'Threads', 'asyncio'], [
    ['Switches between jobs', 'Any time (the OS decides)', 'Only at await'],
    ['Shared data', 'Needs locks', 'Safe between awaits'],
    ['Cost of one job', 'A thread: about 8 MB of address space reserved for its stack', 'A task: a few KB'],
    ['Thousands of connections', 'Heavy', 'Easy'],
    ['Libraries', 'Any normal library', 'Needs async libraries (httpx, aiohttp, asyncpg)'],
    ['CPU heavy work', 'Not with the GIL', 'Never: it blocks the loop']],
    'asyncio for many network connections with async libraries, threads to speed up existing blocking code, processes for CPU work.')}
''', kw=['httpx', 'AsyncClient', 'aiohttp', 'blocking call', 'to_thread', 'run_in_executor', 'threads vs asyncio'])

K.lesson('maths', 'The maths: waits that overlap', f'''
{fxs(fx('Time one by one', 'T = n &times; t', '20 requests of 0.2 s: 4 s.', key=True),
     fx('Time with all at once', 'T &asymp; max(t<sub>i</sub>) + overhead', '20 requests of 0.2 s: about 0.2 s (measured 0.26 s).', key=True),
     fx('With a limit of k at once', 'T &asymp; &lceil;n / k&rceil; &times; t', '20 requests, at most 5 at once, 0.2 s each: 4 rounds, 0.8 s.', key=True),
     fx('Throughput', 'requests per second = k / t', '5 at once, 0.2 s each: 25 requests per second.'),
     fx("Little's law for open connections", 'L = &lambda; &times; W', '1000 requests per second with 0.5 s waits: 500 tasks waiting at any moment.'),
     fx('Memory for many waiters', 'memory &asymp; n &times; size of one waiter', '10,000 tasks of about 2 KB is about 20 MB. 10,000 threads reserve about 80 GB of address space for stacks.'))}
{steps('Worked example: how long do 1000 API calls take?', [
    'Each call waits 0.5 s for the server. One by one: 1000 &times; 0.5 = 500 s.',
    'The API allows at most 50 calls at a time, so use asyncio.Semaphore(50).',
    '&lceil;1000 / 50&rceil; = 20 rounds of 0.5 s.',
    eq('20 &times; 0.5 = 10 s, fifty times faster, in one thread')])}
''', kw=['latency', 'throughput', 'overlap', 'semaphore limit', "Little's law", 'C10k'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Write async def and await, start with asyncio.run, and run several coroutines with gather.</p>',
    '<p>Use create_task, TaskGroup and except*, timeouts, cancellation, Semaphore limits, asyncio.Queue pipelines, and httpx.AsyncClient for real requests.</p>',
    '<p>Explain how the event loop schedules tasks, find blocking calls, move them to to_thread or executors, write async generators and async context managers.</p>',
    '<p>Build servers with asyncio streams or protocols, tune with uvloop, design structured concurrency and cancellation safe code, and understand how await works on top of generators (send, throw and yield from).</p>')}
{grow('Await and gather.', 'Control tasks, limits and timeouts.', 'Design async systems.')}
''', kw=['beginner', 'expert', 'uvloop', 'streams', 'structured concurrency'])

HELP = '''

import asyncio


async def later(value, ms):
    """A small async helper: returns value after ms milliseconds."""
    await asyncio.sleep(ms / 1000)
    return value


async def try_call(func, *args):
    try:
        return await func(*args)
    except Exception as err:
        return str(err)
'''

lc(2621, 'Sleep', 'sleep', 'e', 'await asyncio.sleep', 'LeetCode asks this one in JavaScript. In Python asyncio the same idea is a coroutine that awaits asyncio.sleep(millis / 1000).', r'''
import asyncio
import time


async def sleep(millis):
    await asyncio.sleep(millis / 1000)
    return millis


async def timed_sleep(millis):
    start = time.perf_counter()
    await sleep(millis)
    elapsed = (time.perf_counter() - start) * 1000
    return millis - 5 <= elapsed <= millis + 200
''', [('asyncio.run(timed_sleep(100))', True), ('asyncio.run(sleep(10))', 10)])
lc(2723, 'Add Two Promises', 'add-two-promises', 'e', 'Await both at the same time', 'A JavaScript problem. In Python, gather awaits both coroutines at the same time and returns their values, so the total wait is the longer one, not the sum.', r'''
import asyncio


async def add_two_promises(first, second):
    a, b = await asyncio.gather(first, second)
    return a + b
''' + HELP, [('asyncio.run(add_two_promises(later(2, 20), later(5, 60)))', 7), ('asyncio.run(add_two_promises(later(10, 50), later(-12, 30)))', -2)])
lc(2648, 'Generate Fibonacci Sequence', 'generate-fibonacci-sequence', 'e', 'An endless generator', 'A JavaScript generator problem. In Python, a while True loop with yield gives the numbers one at a time, and itertools.islice takes as many as you need.', r'''
from itertools import islice


def fib_generator():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
''', [('list(islice(fib_generator(), 5))', [0, 1, 1, 2, 3]), ('list(islice(fib_generator(), 0))', [])])
lc(2649, 'Nested Array Generator', 'nested-array-generator', 'm', 'yield from for the nested lists', 'A JavaScript generator problem. Walk the list, and for a nested list hand over to a recursive generator with yield from.', r'''
def inorder_traversal(items):
    for item in items:
        if isinstance(item, list):
            yield from inorder_traversal(item)
        else:
            yield item
''', [('list(inorder_traversal([[[6]], [1, 3], []]))', [6, 1, 3]), ('list(inorder_traversal([]))', []), ('list(inorder_traversal([1, [2, [3, [4]]], 5]))', [1, 2, 3, 4, 5])])
lc(2637, 'Promise Time Limit', 'promise-time-limit', 'm', 'asyncio.wait_for', 'A JavaScript problem. Wrap the coroutine in asyncio.wait_for with the limit in seconds, and turn the TimeoutError into the message the problem asks for.', r'''
import asyncio


def time_limit(func, t):
    async def limited(*args):
        try:
            return await asyncio.wait_for(func(*args), t / 1000)
        except TimeoutError:
            raise TimeoutError("Time Limit Exceeded") from None
    return limited


async def slow_double(n, ms):
    await asyncio.sleep(ms / 1000)
    return n * 2
''' + HELP, [('asyncio.run(try_call(time_limit(slow_double, 100), 5, 30))', 10), ('asyncio.run(try_call(time_limit(slow_double, 50), 5, 200))', 'Time Limit Exceeded')])
lc(2721, 'Execute Asynchronous Functions in Parallel', 'execute-asynchronous-functions-in-parallel', 'm', 'gather keeps the order', 'A JavaScript problem (write Promise.all without Promise.all). In Python, gather starts all of them, keeps the results in the order given and raises the first error.', r'''
import asyncio


async def promise_all(functions):
    results = await asyncio.gather(*(f() for f in functions))
    return list(results)


async def fails():
    await asyncio.sleep(0.01)
    raise ValueError("Error")
''' + HELP, [('asyncio.run(promise_all([lambda: later(1, 30), lambda: later(2, 10)]))', [1, 2]), ('asyncio.run(try_call(promise_all, [lambda: later(1, 30), fails]))', 'Error')])
lc(2622, 'Cache With Time Limit', 'cache-with-time-limit', 'm', 'Store the value with its end time', 'A JavaScript design problem. Keep key: (value, expires_at). A key counts only while the clock is before its end time. The clock is passed in so the tests do not have to wait.', r'''
import time


class TimeLimitedCache:
    def __init__(self, clock=None):
        self.clock = clock or (lambda: time.monotonic() * 1000)
        self.items = {}

    def _alive(self, key):
        return key in self.items and self.items[key][1] > self.clock()

    def set(self, key, value, duration):
        existed = self._alive(key)
        self.items[key] = (value, self.clock() + duration)
        return existed

    def get(self, key):
        return self.items[key][0] if self._alive(key) else -1

    def count(self):
        return sum(1 for key in self.items if self._alive(key))


def demo_cache():
    now = [0]
    cache = TimeLimitedCache(clock=lambda: now[0])
    out = [cache.set(1, 42, 100)]
    now[0] = 50
    out += [cache.get(1), cache.count()]
    now[0] = 150
    out += [cache.get(1), cache.count()]
    return out
''', [('demo_cache()', [False, 42, 1, -1, 0])])
lc(2627, 'Debounce', 'debounce', 'm', 'Cancel the waiting call and schedule a new one', 'A JavaScript problem. With asyncio, loop.call_later schedules the call. A new call cancels the handle of the one still waiting.', r'''
import asyncio


def debounce(func, t):
    handle = None

    def debounced(*args):
        nonlocal handle
        if handle is not None:
            handle.cancel()
        handle = asyncio.get_running_loop().call_later(t / 1000, func, *args)

    return debounced


async def demo_debounce():
    log = []
    typed = debounce(log.append, 50)
    typed("a")
    await asyncio.sleep(0.03)
    typed("b")                                 # "a" was still waiting, so it is cancelled
    await asyncio.sleep(0.12)
    typed("c")
    await asyncio.sleep(0.12)
    return log
''', [('asyncio.run(demo_debounce())', ['b', 'c'])])
lc(2636, 'Promise Pool', 'promise-pool', 'm', 'n workers share one iterator', 'A JavaScript problem. Start n worker coroutines that all take the next function from the same iterator. At most n functions run at any moment.', r'''
import asyncio


async def promise_pool(functions, n):
    jobs = iter(functions)

    async def worker():
        for job in jobs:
            await job()

    await asyncio.gather(*(worker() for _ in range(n)))


async def demo_pool(n):
    running = 0
    peak = 0

    async def job():
        nonlocal running, peak
        running += 1
        peak = max(peak, running)
        await asyncio.sleep(0.01)
        running -= 1

    await promise_pool([job] * 5, n)
    return peak
''', [('asyncio.run(demo_pool(2))', 2), ('asyncio.run(demo_pool(10))', 5), ('asyncio.run(demo_pool(1))', 1)])
lc(2650, 'Design Cancellable Function', 'design-cancellable-function', 'h', 'Drive a generator by hand, race each wait against cancel', 'A JavaScript problem, and exactly how await works inside: send each result into the generator, throw errors into it, and throw a Cancelled error if cancel() wins the race.', r'''
import asyncio


class Cancelled(Exception):
    pass


def cancellable(gen):
    stop = asyncio.Event()

    def cancel():
        stop.set()

    async def run():
        value = None
        error = None
        while True:
            try:
                if error is not None:
                    awaitable = gen.throw(error)
                else:
                    awaitable = gen.send(value)
            except StopIteration as done:
                return done.value
            error = None
            value = None
            job = asyncio.ensure_future(awaitable)
            stopper = asyncio.ensure_future(stop.wait())
            finished, pending = await asyncio.wait({job, stopper}, return_when=asyncio.FIRST_COMPLETED)
            for other in pending:
                other.cancel()
            if stopper in finished and job not in finished:
                stop.clear()
                error = Cancelled("Cancelled")
            elif job.exception() is not None:
                error = job.exception()
            else:
                value = job.result()

    return cancel, run()


def adder():
    total = 0
    try:
        total += (yield later(1, 20))
        total += (yield later(2, 40))
        return total
    except Cancelled:
        return f"cancelled at {total}"


async def demo_cancellable(cancel_after):
    cancel, job = cancellable(adder())
    if cancel_after is not None:
        asyncio.get_running_loop().call_later(cancel_after / 1000, cancel)
    return await job
''' + HELP, [('asyncio.run(demo_cancellable(None))', 3), ('asyncio.run(demo_cancellable(35))', 'cancelled at 1')])

K.lesson('leetcode', 'LeetCode practice', leet('<p>LeetCode has no asyncio problems in Python. Its async problems are in JavaScript (promises, sleep, time limits, debounce, pools and generators), and each one maps straight onto asyncio. The downloads solve them in Python with gather, wait_for, call_later, a shared iterator and a hand driven generator, and say so at the top of each problem.</p>'), kw=['LeetCode', 'promises', 'asyncio', 'debounce', 'promise pool', 'time limit', 'generators', 'cancellation'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'async def makes a coroutine. It runs only when awaited or wrapped in a task. await pauses it and lets the loop run others.',
    'asyncio.run(main()) once at the top. gather or TaskGroup to run coroutines at the same time. create_task for background work.',
    'Waits overlap: n waits of t seconds take about t, not n &times; t. A Semaphore limits how many run at once.',
    'asyncio.timeout and wait_for stop slow work. task.cancel() raises CancelledError at the current await.',
    'asyncio.Queue builds pipelines with back pressure. Async generators and async with exist too.',
    'Never block the loop: use async libraries such as httpx, or asyncio.to_thread for blocking calls.'],
    'Step 6 is the standard library toolbox: regular expressions, files and formats, sqlite3 and tkinter.')}
{files('Three tasks: fix a missing await, write an async generator with an async comprehension, and build a tiny round robin scheduler like the one inside an event loop.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does calling an async def function return?', ['Its result', 'A coroutine object that has not run yet', 'A thread', 'None'], 1, 'Nothing runs yet.', 'The body runs when the coroutine is awaited or turned into a task.')
K.quiz('e', 'Where may you write await?', ['Anywhere', 'Only inside an async def function (or at the top of the asyncio REPL)', 'Only in classes', 'Only in loops'], 1, 'Coroutines only.', 'await outside async def is a SyntaxError in normal code.')
K.quiz('e', 'How many threads does a normal asyncio program use for its tasks?', ['One per task', 'One', 'One per CPU core', 'Two'], 1, 'One loop.', 'The event loop runs every task in one thread, switching at each await.')
K.quiz('m', 'Two coroutines each await asyncio.sleep(1) and are run with gather. About how long does it take?', ['2 s', '1 s', '0 s', '0.5 s'], 1, 'The waits overlap.', 'Both sleep at the same time.')
K.quiz('m', 'What happens if a coroutine calls time.sleep(1)?', ['Only that task waits', 'The whole event loop is frozen for 1 second', 'Python raises an error', 'It is turned into asyncio.sleep'], 1, 'Blocking call.', 'time.sleep does not await, so no other task can run.')
K.quiz('m', 'In a TaskGroup, one task raises ValueError. What happens to the others?', ['They keep running', 'They are cancelled, and the error comes out in an ExceptionGroup', 'They are restarted', 'Nothing'], 1, 'Structured concurrency.', 'Catch it with except* ValueError.')
K.quiz('m', 'What does asyncio.Semaphore(5) do in a crawler?', ['Makes it 5 times faster', 'Lets at most 5 tasks into the protected block at once', 'Runs 5 threads', 'Retries 5 times'], 1, 'A limit.', 'Use async with sem: around the request.')
K.quiz('m', 'Which runs a blocking function without freezing the loop?', ['await blocking()', 'asyncio.to_thread(blocking)', 'asyncio.sleep(blocking)', 'gather(blocking)'], 1, 'Another thread.', 'to_thread runs it in a worker thread and gives an awaitable.')
K.quiz('h', 'What should a task do when it catches CancelledError?', ['Ignore it and continue', 'Clean up and raise it again', 'Return None quietly', 'Call cancel() on itself'], 1, 'Let it go on.', 'Swallowing it stops cancellation from working.')
K.quiz('h', 'What does asyncio.Queue(maxsize=2) do to a producer when 2 items are waiting?', ['Raises QueueFull at once', 'await queue.put() waits until the consumer takes one', 'Drops the oldest item', 'Grows the queue'], 1, 'Back pressure.', 'The producer is slowed down to the speed of the consumer.')
K.quiz('h', 'Why keep a reference to tasks made with create_task?', ['For speed', 'The loop holds tasks only weakly, so an unreferenced task may be garbage collected', 'To see their names', 'It is required syntax'], 1, 'Weak references.', 'Store them in a set or use a TaskGroup.')
K.quiz('x', 'In the style of a Stanford CS 144 interview: 10,000 slow clients each send one request every few seconds. Why does asyncio cope better than one thread per client?', ['asyncio uses more CPU cores', 'Each waiting task costs a few KB, and there is no thread switching or locking', 'Threads cannot do networking', 'asyncio removes network latency'], 1, 'The C10k problem.', 'Memory and context switches for 10,000 threads are large. Waiting tasks in one loop are cheap.')
K.quiz('x', 'In the style of a CMU 15-440 exam: under the hood, what is await most like?', ['A function call that blocks the thread', 'yield from: the coroutine gives control back to its driver and is resumed with send', 'A new process', 'A lock'], 1, 'Generators.', 'Coroutines are built on the same machinery as generators: the loop sends results in and the coroutine yields control at each await.')

K.calc('e', '20 requests of 0.2 s each are sent one by one. How many seconds?', '4', 'n &times; t.', ['20 &times; 0.2.', 'The waits add up.', eq('4 s')], check=4)
K.calc('e', 'The same 20 requests run all at once with gather. About how many seconds, ignoring overhead?', '0.2', 'The longest wait.', ['All 20 wait together.', 'Each waits 0.2 s.', eq('about 0.2 s')], check=0.2)
K.calc('e', 'gather(sleep(0.3), sleep(0.2), sleep(0.5)). About how many seconds?', '0.5', 'The maximum.', ['They overlap.', 'The longest is 0.5.', eq('0.5 s')], check=0.5)
K.calc('m', '20 requests of 0.2 s with a Semaphore(5). About how many seconds?', '0.8', '&lceil;n / k&rceil; &times; t.', ['20 / 5 = 4 rounds.', '4 &times; 0.2.', eq('0.8 s')], check=0.8)
K.calc('m', 'With Semaphore(5) and 0.2 s per request, how many requests per second?', '25', 'k / t.', ['5 at a time.', '5 / 0.2.', eq('25 per second')], check=25)
K.calc('m', 'Measured: 4.09 s one by one and 0.26 s with asyncio. What is the speedup, to 1 decimal?', '15.7', 'T<sub>1</sub> / T<sub>async</sub>.', ['4.09 / 0.26 &asymp; 15.73.', 'Round.', eq('&asymp; 15.7 times')], check=round(4.09 / 0.26, 1))
K.calc('m', 'awaits run in a row: sleep(0.3), then gather(sleep(0.2), sleep(0.4)). Total seconds?', '0.7', 'Sum of the steps, max inside gather.', ['First 0.3.', 'Then max(0.2, 0.4) = 0.4.', eq('0.7 s')], check=0.7)
K.calc('h', '1000 API calls of 0.5 s, at most 50 at a time. How many seconds?', '10', '&lceil;1000 / 50&rceil; &times; 0.5.', ['20 rounds.', '20 &times; 0.5.', eq('10 s')], check=10)
K.calc('h', "1000 requests per second, each waiting 0.5 s. By Little's law, how many tasks wait at any moment?", '500', 'L = &lambda; &times; W.', ['&lambda; = 1000, W = 0.5.', '1000 &times; 0.5.', eq('500')], check=500)
K.calc('x', 'In the style of a Google systems interview: 10,000 waiting connections at about 2 KB per task. How many MB of memory (1 MB = 1000 KB)?', '20', 'n &times; size.', ['10,000 &times; 2 KB = 20,000 KB.', 'Divide by 1000.', eq('20 MB')], check=20)

DRIVE = '''

def drive(coro):
    """Run a coroutine that never really has to wait, without an event loop."""
    try:
        coro.send(None)
    except StopIteration as done:
        return done.value
    raise RuntimeError("the coroutine had to wait")
'''

K.assign('fixawait', 'e', 'Fix the missing await',
         '<p>add_tax is a coroutine. total must return the sum of add_tax(p) for every price, rounded to 2 decimals, but the starter forgets to await, so it tries to add coroutine objects. Fix total. The tests run it with drive(), a tiny helper that runs a coroutine without an event loop.</p>',
         '''
async def add_tax(price):
    return price * 1.2


async def total(prices):
    result = 0
    for p in prices:
        result = result + add_tax(p)
    return round(result, 2)
''' + DRIVE, [('drive(total([10, 20]))', 36.0), ('drive(total([]))', 0), ('drive(total([0.5]))', 0.6)],
         '''
async def add_tax(price):
    return price * 1.2


async def total(prices):
    result = 0
    for p in prices:
        result = result + await add_tax(p)
    return round(result, 2)
''' + DRIVE, 'Write await in front of add_tax(p). Without it you get a coroutine object, not a number.', '<p>Forgetting await is the most common asyncio bug. Python also warns: RuntimeWarning: coroutine \'add_tax\' was never awaited. Linters such as ruff can catch it too.</p>')
K.assign('agen', 'm', 'An async generator and an async comprehension',
         '<p>Write an async generator <code>countdown(n)</code> that yields n, n &minus; 1, ..., 1, and an async function <code>collect_squares(n)</code> that returns the squares of the countdown values using an async comprehension: [x * x async for x in countdown(n)].</p>',
         '''
async def countdown(n):
    return list(range(n, 0, -1))


async def collect_squares(n):
    return [x * x for x in await countdown(n)]
''' + DRIVE, [('drive(collect_squares(3))', [9, 4, 1]), ('drive(collect_squares(0))', []), ('type(countdown(2)).__name__', 'async_generator')],
         '''
async def countdown(n):
    while n > 0:
        yield n
        n -= 1


async def collect_squares(n):
    return [x * x async for x in countdown(n)]
''' + DRIVE, 'An async def that contains yield is an async generator. Read it with async for, or with an async comprehension.', '<p>Async generators let you stream results from a database or a network as they arrive, instead of waiting for the whole list.</p>')
K.assign('scheduler', 'h', 'A tiny round robin scheduler',
         '<p>An event loop switches between tasks at every await. Build the same idea with plain generators. <code>round_robin(tasks)</code> gets a list of generators. It runs the first one until its next yield, then the next one, and so on, round and round, dropping each generator when it is finished. Return the list of every value yielded, in that order. worker(name, steps) is a sample task. Use collections.deque.</p>',
         '''
from collections import deque


def worker(name, steps):
    for i in range(steps):
        yield f"{name}{i}"


def round_robin(tasks):
    log = []
    for task in tasks:
        for value in task:
            log.append(value)
    return log
''', [('round_robin([worker("A", 2), worker("B", 3)])', ['A0', 'B0', 'A1', 'B1', 'B2']), ('round_robin([])', []), ('round_robin([worker("X", 1), worker("Y", 0), worker("Z", 2)])', ['X0', 'Z0', 'Z1'])],
         '''
from collections import deque


def worker(name, steps):
    for i in range(steps):
        yield f"{name}{i}"


def round_robin(tasks):
    ready = deque(tasks)
    log = []
    while ready:
        task = ready.popleft()
        try:
            log.append(next(task))
        except StopIteration:
            continue
        ready.append(task)
    return log
''', 'Keep the tasks in a deque. Take one from the front, run it to its next yield with next(), and put it at the back. If it raises StopIteration it is finished, so do not put it back.', '<p>This is the heart of every event loop. asyncio adds a list of tasks that wait for a time or for data, and wakes them up when they are ready.</p>')

K.must('Basics', 'async def, await (only inside async def), asyncio.run(main()) once. Calling a coroutine function does not run it.')
K.must('Together', 'gather (results in order), TaskGroup with except*, create_task (keep a reference), as_completed (finish order).')
K.must('Control', 'asyncio.timeout(s) and wait_for, task.cancel() and CancelledError (raise it again), Semaphore(k) to limit.')
K.must('Pipelines', 'asyncio.Queue(maxsize) with await put and get for back pressure. Async generators, async for, async with.')
K.must('Never block', 'No time.sleep or requests in coroutines. Use asyncio.sleep, httpx.AsyncClient, asyncio.to_thread or run_in_executor.')

T = K.topic(
    slug='py-asyncio', topic='py-asyncio', step=(5, 'Doing many things at once: threads, processes and asyncio', 'py-a5', 'Use waiting time and every CPU core: threads for I/O, processes for heavy work, and asyncio for thousands of connections.', 'Advanced'),
    title='asyncio: async and await', short='asyncio', badge='5.2', minutes=80,
    lead='Handle thousands of waiting jobs in one thread. Learn coroutines, async and await, the event loop, gather, tasks and TaskGroup, timeouts and cancelling, Semaphore limits, asyncio.Queue pipelines, async generators, real requests with httpx, and how to avoid blocking the loop.',
    desc='coroutines, async def and await, the event loop, asyncio.run, gather, create_task, TaskGroup and except*, as_completed, asyncio.wait, asyncio.timeout and wait_for, cancellation and CancelledError, Semaphore, asyncio.Queue and back pressure, async generators, async for and async with, httpx.AsyncClient, blocking calls, to_thread and run_in_executor, threads versus asyncio, latency and throughput maths.',
    summary='coroutines, the event loop, gather and TaskGroup, timeouts, limits, queues and httpx.',
    keywords=['asyncio', 'async', 'await', 'coroutine', 'event loop', 'gather', 'TaskGroup', 'Semaphore', 'asyncio.Queue', 'httpx', 'to_thread'],
    recap='<p>Put await in front of every wait, run waits together with gather or a TaskGroup, limit them with a Semaphore, and never block the loop.</p>',
    added='2026-11-07', leet=leet_items())
