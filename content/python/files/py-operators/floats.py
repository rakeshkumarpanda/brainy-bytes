# 1.3 Operators, expressions and the order Python works them out
# Example "floats" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from decimal import Decimal
from fractions import Fraction
import math

print(0.1 + 0.2)
print(Decimal(0.1))               # the exact value stored for 0.1
print(Decimal("0.1") + Decimal("0.2"))
print(Fraction(1, 10) + Fraction(2, 10))
print(round(2.675, 2))            # 2.675 is stored as 2.67499...
print(math.floor(-2.5), math.ceil(-2.5), math.trunc(-2.5))
print(1e308 * 10, -1e308 * 10)    # too big: inf
print(math.sqrt(2) ** 2 == 2, math.isclose(math.sqrt(2) ** 2, 2))
