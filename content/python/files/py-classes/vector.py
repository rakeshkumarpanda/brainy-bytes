# 6.1 Classes and objects: attributes, methods, self and encapsulation
# Example "vector" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import math


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def add(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"


a = Vector(3, 4)
b = Vector(1, 2)
print(a.length(), a.add(b), a.dot(b))
cos_angle = a.dot(b) / (a.length() * b.length())
print(round(math.degrees(math.acos(cos_angle)), 2), "degrees between a and b")
