# 3.3 Tuples and sets: fixed records and unique items
# Example "named" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p, p.x, p.y, p[0])
print((p.x ** 2 + p.y ** 2) ** 0.5)
x, y = p                # still a tuple, so it unpacks
print(x + y)
print(p._replace(x=10)) # a new tuple, p is unchanged
