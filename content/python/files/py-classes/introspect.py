# 6.1 Classes and objects: attributes, methods, self and encapsulation
# Example "introspect" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Point:
    """A point on a grid."""
    dims = 2

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy


p = Point(3, 4)
print(type(p).__name__, Point.__name__, Point.__module__)
print(isinstance(p, Point), isinstance(3, Point), p.__class__ is Point)
print(hasattr(p, "x"), hasattr(p, "z"), hasattr(p, "move"))
print(getattr(p, "y"), getattr(p, "z", "no z"))
setattr(p, "z", 5)                     # the same as p.z = 5
print(vars(p))                         # the same as p.__dict__
delattr(p, "z")                        # the same as del p.z
print(p.__dict__)
print(Point.__doc__, Point.__bases__)
print([name for name in Point.__dict__ if not name.startswith("__")])

field = "x"                            # the attribute name is only known at run time
print(getattr(p, field))
