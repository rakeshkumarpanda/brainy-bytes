# 1.3 Class design: methods, properties, abstract classes and dataclasses
# Example "slots" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import tracemalloc


class Plain:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Slotted:
    __slots__ = ("x", "y")                     # only these attributes, no __dict__

    def __init__(self, x, y):
        self.x = x
        self.y = y


def bytes_per_object(cls, n=10_000):
    tracemalloc.start()
    objects = [cls(i, i) for i in range(n)]
    used = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    return used // n


print("Plain:  ", bytes_per_object(Plain), "bytes per object")
print("Slotted:", bytes_per_object(Slotted), "bytes per object")

s = Slotted(1, 2)
try:
    s.z = 3
except AttributeError as err:
    print("AttributeError:", err)
