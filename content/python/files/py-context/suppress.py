# 2.3 Context managers and the with statement
# Example "suppress" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from contextlib import suppress


class IgnoreMissing:
    def __enter__(self):
        return self

    def __exit__(self, kind, err, tb):
        return kind is not None and issubclass(kind, KeyError)   # True hides the error


prices = {"tea": 10}
with IgnoreMissing():
    print(prices["coffee"])
print("carried on after a KeyError")

with suppress(FileNotFoundError):              # the ready made version
    open("no-such-file.txt")
print("carried on after FileNotFoundError")

try:
    with suppress(KeyError):
        print(1 / 0)                           # a different error is NOT hidden
except ZeroDivisionError as err:
    print("not suppressed:", err)
