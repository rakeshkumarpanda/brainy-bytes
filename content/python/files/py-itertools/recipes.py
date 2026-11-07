# 2.2 itertools, functools and operator
# Example "recipes" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from collections import deque
from itertools import islice, chain


def sliding_window(iterable, n):
    it = iter(iterable)
    window = deque(islice(it, n - 1), maxlen=n)
    for x in it:
        window.append(x)                       # the oldest value drops off the left
        yield tuple(window)


def unique_everseen(iterable):
    seen = set()
    for item in iterable:
        if item not in seen:
            seen.add(item)
            yield item


def first_true(iterable, default=None, pred=None):
    return next(filter(pred, iterable), default)


print(list(sliding_window([1, 2, 3, 4, 5], 3)))
print(list(unique_everseen("abracadabra")))
print(first_true([0, "", 7, 9]), first_true([0, 0], default="none"))
print(list(chain.from_iterable(zip("abc", "123"))))
