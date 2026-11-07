# 1.1 Special methods and operator overloading
# Example "vector" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import math


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other):                  # v + w
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):                  # v - w
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, k):                      # v * 3
        return Vector(self.x * k, self.y * k)

    def __rmul__(self, k):                     # 3 * v
        return self * k

    def __neg__(self):                         # -v
        return Vector(-self.x, -self.y)

    def __abs__(self):                         # abs(v)
        return math.hypot(self.x, self.y)

    def __eq__(self, other):                   # v == w
        return isinstance(other, Vector) and (self.x, self.y) == (other.x, other.y)

    def __bool__(self):                        # if v:
        return self.x != 0 or self.y != 0


a = Vector(3, 4)
b = Vector(1, 2)
print(a + b, a - b, a * 2, 2 * a, -a)
print(abs(a), a == Vector(3, 4), bool(Vector(0, 0)))
print(a.__add__(b))                            # what a + b really runs
