# 8.1 Exam practice: PCPP1 style papers
# Example "paper_d" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache, partial, reduce, wraps


@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print("Q1", fib(30), fib.cache_info().misses)

square = partial(pow, exp=2)
print("Q2", square(5), reduce(lambda a, b: a * b, [1, 2, 3, 4]))


def logged(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


@logged
def greet():
    """Say hi."""


print("Q3", greet.__name__, greet.__doc__)


@dataclass(order=True)
class Card:
    rank: int
    suit: str = "hearts"
    tags: list = field(default_factory=list)


print("Q4", Card(2) < Card(3), Card(2), Card(2) == Card(2))


class Color(Enum):
    RED = 1
    GREEN = 2


print("Q5", Color.RED, Color(2).name, Color["RED"].value, len(Color))


def f(a, /, b, *, c):
    return a + b + c


try:
    f(a=1, b=2, c=3)
except TypeError:
    print("Q6 a is positional only")
print("Q6", f(1, b=2, c=3))


def hinted(x: int) -> str:
    return x * 2


print("Q7", hinted(3), hinted.__annotations__)
print("Q8", sorted(["b", "C", "a"]), sorted(["b", "C", "a"], key=str.lower), max([], default=0))
x = [1, 2, 3]
print("Q9", (y := len(x)) > 2, y, *x)
match {"type": "point", "x": 1}:
    case {"type": "point", "x": 0}:
        print("Q10 origin")
    case {"type": "point", "x": x0}:
        print("Q10 x is", x0)
