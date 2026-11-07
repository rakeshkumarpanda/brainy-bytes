# 5.2 Modules and packages: import, the standard library and pip
# Example "mathmod" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import math

print(math.ceil(4.2), math.floor(4.8), math.trunc(-4.8), round(4.5))
print(math.floor(-4.2), math.ceil(-4.2))
print(math.sqrt(2), math.isqrt(20), math.hypot(3, 4))
print(math.factorial(6), math.comb(5, 2), math.perm(5, 2))
print(math.gcd(84, 36), math.lcm(4, 6))
print(math.log(math.e), math.log10(1000), math.log2(1024), math.log(8, 2))
print(math.sin(math.pi / 2), math.degrees(math.pi), math.radians(180))
print(0.1 + 0.2 == 0.3, math.isclose(0.1 + 0.2, 0.3))
print(math.inf > 10 ** 100, math.isnan(math.nan))
