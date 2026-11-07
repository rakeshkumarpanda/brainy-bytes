# 5.2 Modules and packages: import, the standard library and pip
# Example "imports" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import math                       # the whole module, used as math.name
print(math.sqrt(16), math.pi)

from math import factorial, tau   # just some names, used without math.
print(factorial(5), tau)

import statistics as st           # a short alias
print(st.mean([2, 4, 9]))

from math import sqrt as root     # an alias for one name
print(root(81))

names = [n for n in dir(math) if not n.startswith("_")]
print(len(names), "public names in math, for example", names[:6])
