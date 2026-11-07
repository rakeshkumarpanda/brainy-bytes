# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
# Example "shapes" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import math


class Shape:
    def area(self):
        raise NotImplementedError("each shape must define area()")

    def describe(self):
        return type(self).__name__ + " with area " + str(round(self.area(), 2))


class Circle(Shape):
    def __init__(self, r):
        self.r = r

    def area(self):
        return math.pi * self.r ** 2


class Rectangle(Shape):
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h


class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c

    def area(self):                    # Heron's formula
        s = (self.a + self.b + self.c) / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))


shapes = [Circle(2), Rectangle(3, 4), Triangle(3, 4, 5)]
for shape in shapes:
    print(shape.describe())
print("total", round(sum(shape.area() for shape in shapes), 2))
try:
    Shape().area()
except NotImplementedError as err:
    print("NotImplementedError:", err)
