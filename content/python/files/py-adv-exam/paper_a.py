# 8.1 Exam practice: PCPP1 style papers
# Example "paper_a" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class V:
    def __init__(self, x):
        self.x = x

    def __add__(self, other):
        return V(self.x + other.x)

    def __eq__(self, other):
        return self.x == other.x

    def __repr__(self):
        return f"V({self.x})"


print("Q1", V(1) + V(2), V(1) == V(1), V(1) is V(1))
try:
    print({V(1)})
except TypeError as err:
    print("Q2", type(err).__name__)


class A:
    def who(self):
        return "A"


class B(A):
    def who(self):
        return "B" + super().who()


class C(A):
    def who(self):
        return "C" + super().who()


class D(B, C):
    pass


print("Q3", D().who(), [k.__name__ for k in D.__mro__])


class Counter:
    count = 0

    def __init__(self):
        Counter.count += 1

    @classmethod
    def made(cls):
        return cls.count

    @staticmethod
    def hello():
        return "hi"


Counter()
Counter()
print("Q4", Counter.made(), Counter.hello())


class Temp:
    def __init__(self):
        self._c = 0

    @property
    def c(self):
        return self._c

    @c.setter
    def c(self, value):
        if value < -273.15:
            raise ValueError("too cold")
        self._c = value


t = Temp()
t.c = 25
try:
    t.c = -300
except ValueError as err:
    print("Q5", t.c, err)

from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self):
        ...


try:
    Shape()
except TypeError:
    print("Q6 cannot make a Shape")


def double(fn):
    def wrapper(*args):
        return fn(*args) * 2
    return wrapper


@double
def five():
    return 5


print("Q7", five(), five.__name__)


def repeat(n):
    def decorator(fn):
        def wrapper():
            return [fn() for _ in range(n)]
        return wrapper
    return decorator


@repeat(3)
def letter():
    return "x"


print("Q8", letter())


class Meta(type):
    def __new__(mcs, name, bases, namespace):
        namespace["tag"] = name.lower()
        return super().__new__(mcs, name, bases, namespace)


class Thing(metaclass=Meta):
    pass


print("Q9", Thing.tag, type(Thing).__name__, type(type).__name__)


class Slim:
    __slots__ = ("a",)


s = Slim()
s.a = 1
try:
    s.b = 2
except AttributeError:
    print("Q10", hasattr(s, "__dict__"))

import copy

data = [[1, 2], [3]]
shallow = copy.copy(data)
deep = copy.deepcopy(data)
data[0].append(9)
print("Q11", shallow[0], deep[0], shallow is data, shallow[0] is data[0])
