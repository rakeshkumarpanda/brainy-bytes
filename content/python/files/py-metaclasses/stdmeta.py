# 1.5 Metaprogramming: type, class hooks and metaclasses
# Example "stdmeta" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from abc import ABC
from enum import Enum


class Shape(ABC):
    pass


class Colour(Enum):
    RED = 1
    GREEN = 2


print(type(Shape).__name__, type(Colour).__name__, type(int).__name__)
print(len(Colour), Colour["RED"], [c.name for c in Colour])   # len, [] and for on the CLASS
print(issubclass(type(Shape), type), type.__bases__)


class MetaA(type):
    pass


class MetaB(type):
    pass


class A(metaclass=MetaA):
    pass


class B(metaclass=MetaB):
    pass


try:
    class C(A, B):                             # two unrelated metaclasses
        pass
except TypeError as err:
    print("TypeError:", str(err).split(":")[0])
