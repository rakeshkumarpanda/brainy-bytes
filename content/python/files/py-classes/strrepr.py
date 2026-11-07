# 6.1 Classes and objects: attributes, methods, self and encapsulation
# Example "strrepr" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Plain:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):                # for developers: looks like code
        return f"Point({self.x}, {self.y})"

    def __str__(self):                 # for users: nice to read
        return f"({self.x}, {self.y})"


p = Plain(3, 4)
print(repr(p).startswith("<__main__.Plain object at 0x"))   # the default: name and memory address

q = Point(3, 4)
print(q)                               # print uses __str__
print(repr(q))                         # repr uses __repr__
print([q, Point(0, 0)])                # a list shows the repr of its items
print(f"{q} and {q!r}")
print(str(q) + " is a point")
