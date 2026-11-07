# 8.1 Exam practice: PCPP1 style papers
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


# ================================================================== task 1: A Vector2 class with the right special methods
# Finish the class Vector2. It already adds vectors, multiplies by a number on the right and prints
# itself. Add: 3 * v (__rmul__), abs(v) for the length (math.hypot), a __hash__ that matches __eq__
# so vectors can go in sets, and make __eq__ return NotImplemented when the other object is not a
# Vector2.
# Hint: 3 * v asks int first, which returns NotImplemented, so Python calls v.__rmul__(3). Hash the
# same fields that __eq__ compares: hash((self.x, self.y)).

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __mul__(self, k):
        return Vector2(self.x * k, self.y * k)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"


# ================================================================== task 2: A retry decorator
# Write retry(times, exceptions=(Exception,)), a decorator with arguments. The decorated function is
# called up to times times while it raises one of exceptions. After the last failed try, the last
# error is raised again. Other exceptions are not retried. Keep the name of the function with
# functools.wraps. The helpers run(times, fails) and run_other() use it on a function that fails a
# given number of times.
# Hint: Loop attempt from 1 to times. Return at once on success. In except exceptions, re-raise with
# a bare raise when it was the last attempt. except accepts a tuple of exception classes.

def retry(times, exceptions=(Exception,)):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def run(times, fails):
    calls = []

    @retry(times, (ConnectionError,))
    def fetch():
        calls.append(1)
        if len(calls) <= fails:
            raise ConnectionError("server down")
        return "ok"

    try:
        result = fetch()
    except ConnectionError:
        result = "gave up"
    return [result, len(calls), fetch.__name__]


def run_other():
    calls = []

    @retry(5, (ConnectionError,))
    def parse():
        calls.append(1)
        raise ValueError("bad data")

    try:
        parse()
    except ValueError:
        return ["ValueError", len(calls)]
    return ["no error", len(calls)]


# ================================================================== task 3: An LRU cache on OrderedDict
# Write the class LRUCache(capacity). get(key, default=None) returns the value and marks the key as
# just used. put(key, value) adds or updates a key and marks it as just used. When there are more
# than capacity keys, the least recently used one leaves. A capacity of 0 stores nothing. len(cache)
# and key in cache work, and in does NOT count as a use. keys() lists the keys from least to most
# recently used. Use collections.OrderedDict with move_to_end and popitem(last=False). The helper
# play_lru(capacity, commands) runs commands.
# Hint: The starter forgets to move a key on get and on update, and crashes with capacity 0.
# move_to_end(key) marks a key as just used, popitem(last=False) removes the oldest.

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def put(self, key, value):
        if len(self.data) >= self.capacity:
            oldest = next(iter(self.data))
            del self.data[oldest]
        self.data[key] = value

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def keys(self):
        return list(self.data)


def play_lru(capacity, commands):
    cache = LRUCache(capacity)
    out = []
    for command in commands:
        if command[0] == "put":
            cache.put(command[1], command[2])
        elif command[0] == "get":
            out.append(cache.get(command[1]))
        else:
            out.append(command[1] in cache)
    return [out, cache.keys(), len(cache)]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A Vector2 class with the right special methods", [('repr(Vector2(1, 2) + Vector2(3, 4))', 'Vector2(4, 6)'), ('repr(Vector2(1, 2) * 3)', 'Vector2(3, 6)'), ('repr(3 * Vector2(1, 2))', 'Vector2(3, 6)'), ('abs(Vector2(3, 4))', 5.0), ('len({Vector2(1, 1), Vector2(1, 1), Vector2(2, 1)})', 2), ('Vector2(1, 2) == (1, 2)', False)]))
    results.append(check("Task 2: A retry decorator", [('run(3, 0)', ['ok', 1, 'fetch']), ('run(3, 2)', ['ok', 3, 'fetch']), ('run(3, 3)', ['gave up', 3, 'fetch']), ('run_other()', ['ValueError', 1])]))
    results.append(check("Task 3: An LRU cache on OrderedDict", [('play_lru(2, [("put", "a", 1), ("put", "b", 2), ("get", "a"), ("put", "c", 3), ("get", "b")])', [[1, None], ['a', 'c'], 2]), ('play_lru(2, [("put", "a", 1), ("put", "b", 2), ("put", "a", 10), ("get", "a"), ("get", "b")])', [[10, 2], ['a', 'b'], 2]), ('play_lru(1, [("put", "a", 1), ("in", "a"), ("put", "b", 2), ("in", "a"), ("get", "b")])', [[True, False, 2], ['b'], 1]), ('play_lru(0, [("put", "a", 1), ("get", "a")])', [[None], [], 0]), ('play_lru(2, [("put", "a", 1), ("put", "b", 2), ("in", "a"), ("put", "c", 3), ("get", "a")])', [[True, None], ['b', 'c'], 2])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
