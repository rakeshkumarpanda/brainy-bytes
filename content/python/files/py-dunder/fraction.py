# 1.1 Special methods and operator overloading
# Example "fraction" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import math
from fractions import Fraction


class Frac:
    def __init__(self, top, bottom):
        if bottom == 0:
            raise ZeroDivisionError("bottom cannot be 0")
        g = math.gcd(top, bottom)              # keep it in lowest terms
        if bottom < 0:
            g = -g
        self.top = top // g
        self.bottom = bottom // g

    def __add__(self, other):                  # a/b + c/d = (ad + cb) / bd
        return Frac(self.top * other.bottom + other.top * self.bottom, self.bottom * other.bottom)

    def __mul__(self, other):                  # a/b * c/d = ac / bd
        return Frac(self.top * other.top, self.bottom * other.bottom)

    def __eq__(self, other):
        return (self.top, self.bottom) == (other.top, other.bottom)

    def __float__(self):
        return self.top / self.bottom

    def __repr__(self):
        return f"{self.top}/{self.bottom}"


print(Frac(1, 2) + Frac(1, 3), Frac(2, 4), Frac(3, -6))
print(Frac(2, 3) * Frac(9, 4), float(Frac(1, 8)))
print(Frac(1, 2) + Frac(1, 3) == Frac(5, 6))
print(Fraction(1, 2) + Fraction(1, 3))         # the standard library version
print(0.1 + 0.2, Fraction(1, 10) + Fraction(2, 10))
