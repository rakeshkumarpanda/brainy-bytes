# 2.2 itertools, functools and operator
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


# ================================================================== task 1: Run length encoding with groupby
# Write encode(text) that returns a list of (letter, count) tuples for each run, and decode(pairs)
# that turns such a list back into text. Use groupby for encode.
# Why it works: groupby is exactly the right tool here because run length encoding is about
# neighbours, not totals.

from itertools import groupby


def encode(text):
    pairs = []
    for letter, group in groupby(text):
        pairs.append((letter, len(list(group))))
    return pairs


def decode(pairs):
    text = ""
    for letter, count in pairs:
        text = text + letter * count
    return text


# ================================================================== task 2: A moving average over any iterable
# Write moving_average(values, k) that returns the average of every window of k neighbouring values,
# each rounded to 2 places. values may be any iterable, even a generator, so loop over it only once.
# If there are fewer than k values, return [].
# Why it works: The running total makes each step O(1), so the whole job is O(n) even for a big k,
# instead of summing k values every time.

from collections import deque


def moving_average(values, k):
    window = deque(maxlen=k)
    total = 0
    result = []
    for value in values:
        if len(window) == k:
            total -= window[0]                 # the oldest value is about to drop off
        window.append(value)
        total += value
        if len(window) == k:
            result.append(round(total / k, 2))
    return result


# ================================================================== task 3: A value formatter with singledispatch
# Write fmt(value) with functools.singledispatch: int gives thousands commas ("1,234"), float gives
# 2 decimal places ("3.14"), bool gives "yes" or "no", str gives the text in double quotes, list
# gives "[" + the items formatted and joined by ", " + "]", dict gives "{" + "key: value" pairs
# sorted by key, joined by ", " + "}" (keys as plain text, values formatted), and anything else
# gives "?".
# Why it works: bool needs its own version: without it True would use the int version and print 1.
# singledispatch picks the closest class in the MRO, and bool is closer than int.

from functools import singledispatch


@singledispatch
def fmt(value):
    return "?"


@fmt.register
def _(value: int):
    return format(value, ",")


@fmt.register
def _(value: bool):
    return "yes" if value else "no"


@fmt.register
def _(value: float):
    return format(value, ".2f")


@fmt.register
def _(value: str):
    return '"' + value + '"'


@fmt.register
def _(value: list):
    parts = []
    for item in value:
        parts.append(fmt(item))
    return "[" + ", ".join(parts) + "]"


@fmt.register
def _(value: dict):
    parts = []
    for key in sorted(value):
        parts.append(str(key) + ": " + fmt(value[key]))
    return "{" + ", ".join(parts) + "}"


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Run length encoding with groupby", [('encode("aaabcc")', [['a', 3], ['b', 1], ['c', 2]]), ('encode("")', []), ('decode([("x", 2), ("y", 1)])', 'xxy'), ('decode(encode("hello"))', 'hello')]))
    results.append(check("Task 2: A moving average over any iterable", [('moving_average([1, 2, 3, 4, 5], 3)', [2.0, 3.0, 4.0]), ('moving_average(iter([10, 20]), 3)', []), ('moving_average((x for x in [2, 4, 6, 8]), 2)', [3.0, 5.0, 7.0]), ('moving_average([5], 1)', [5.0])]))
    results.append(check("Task 3: A value formatter with singledispatch", [('fmt(1234567)', '1,234,567'), ('fmt(3.14159)', '3.14'), ('fmt([1, 2.5, "a"])', '[1, 2.50, "a"]'), ('fmt({"b": 2, "a": True})', '{a: yes, b: 2}'), ('fmt(None)', '?')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
