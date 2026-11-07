# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
# Example "abstract" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from abc import ABC, abstractmethod


class Shape(ABC):                      # an abstract base class
    @abstractmethod
    def area(self):
        pass


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2


class Blob(Shape):                     # forgot area()
    pass


print(Square(3).area())
for cls in [Shape, Blob]:
    try:
        cls()
    except TypeError as err:
        print("TypeError:", err)
