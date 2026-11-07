# 8.1 Exam practice: PCPP1 style papers
# Example "bug_hunt" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

# Bug 1: a decorator that forgets to return the result
def timed(fn):
    def wrapper(*args):
        fn(*args)
    return wrapper


@timed
def add(a, b):
    return a + b


print("Bug 1:", add(2, 3))

# Bug 2: a generator used twice
squares = (n * n for n in range(4))
print("Bug 2:", sum(squares), sum(squares))


# Bug 3: __eq__ without __hash__
class Point:
    def __init__(self, x):
        self.x = x

    def __eq__(self, other):
        return self.x == other.x


try:
    print({Point(1)})
except TypeError as err:
    print("Bug 3:", err)


# Bug 4: a class attribute list shared by every object
class Basket:
    items = []

    def add(self, item):
        self.items.append(item)


first = Basket()
second = Basket()
first.add("apple")
print("Bug 4:", second.items)

# Bug 5: catching an error and hiding it
import json


def load(text):
    try:
        return json.loads(text)
    except Exception:
        pass


print("Bug 5:", load("{bad json}"))


# Bug 6: a context manager that swallows every exception
class Safe:
    def __enter__(self):
        return self

    def __exit__(self, *info):
        return True


with Safe():
    total = 1 / 0
print("Bug 6: still running, total exists:", "total" in globals())

# Bug 7: a regular expression without a raw string
import re

print("Bug 7:", re.findall("\bcat\b", "cat concat cat"), re.findall(r"\bcat\b", "cat concat cat"))
