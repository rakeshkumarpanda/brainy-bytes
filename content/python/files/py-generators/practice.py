# 2.1 Iterators and generators
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


# ================================================================== task 1: Split items into chunks with a generator
# Write a generator function chunked(items, size) that yields lists of size items in order. The last
# chunk may be shorter. It must work for any iterable, including another generator, and must not
# build all chunks at once.
# Hint: Collect items in a list. When it reaches size, yield it and start a new list. After the
# loop, yield what is left if it is not empty.

import inspect


def chunked(items, size):
    return [list(items)]


# ================================================================== task 2: A FloatRange you can loop over again and again
# Write a class FloatRange(start, stop, step) that is an iterable (not a one shot iterator): every
# loop gives start, start + step, start + 2 × step, ... while the value is below stop. Work out each
# value as start + i × step so that rounding errors do not add up, and round it to 10 places.
# Hint: Make __iter__ a generator method. Each call of __iter__ then starts a new generator with its
# own i.

class FloatRange:
    def __init__(self, start, stop, step):
        self.start = start
        self.stop = stop
        self.step = step
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += self.step
        return value


# ================================================================== task 3: A running average coroutine
# Write a generator running_stats() that you prime with next() and then feed numbers with send().
# After each number it yields a tuple (count, average), with the average rounded to 2 places.
# Sending None resets it: count goes back to 0 and it yields (0, None).
# Hint: Keep total and count in local variables. value = yield result both hands out the last answer
# and receives the next number.

def running_stats():
    yield


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Split items into chunks with a generator", [('list(chunked(range(7), 3))', [[0, 1, 2], [3, 4, 5], [6]]), ('list(chunked([], 2))', []), ('inspect.isgenerator(chunked([1], 1))', True), ('list(chunked((x * x for x in range(4)), 2))', [[0, 1], [4, 9]])]))
    results.append(check("Task 2: A FloatRange you can loop over again and again", [('list(FloatRange(0, 1, 0.25))', [0.0, 0.25, 0.5, 0.75]), ('(lambda r: (list(r), list(r)))(FloatRange(0, 3, 1))', [[0, 1, 2], [0, 1, 2]]), ('list(FloatRange(0, 1, 0.1))[-1]', 0.9), ('len(list(FloatRange(5, 5, 1)))', 0)]))
    results.append(check("Task 3: A running average coroutine", [('(lambda g: (next(g), [g.send(v) for v in [10, 20, 60]])[1])(running_stats())', [[1, 10.0], [2, 15.0], [3, 30.0]]), ('(lambda g: (next(g), g.send(5), g.send(None), g.send(7))[1:])(running_stats())', [[1, 5.0], [0, None], [1, 7.0]]), ('(lambda g: (next(g), g.send(1), g.send(2))[2])(running_stats())', [2, 1.5])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
