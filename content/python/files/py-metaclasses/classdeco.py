# 1.5 Metaprogramming: type, class hooks and metaclasses
# Example "classdeco" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def auto_repr(cls):
    """Add a __repr__ that lists the attributes set in __init__."""
    def __repr__(self):
        parts = []
        for key, value in vars(self).items():
            parts.append(key + "=" + repr(value))
        return cls.__name__ + "(" + ", ".join(parts) + ")"

    cls.__repr__ = __repr__
    return cls                                 # hand the same class back


ROUTES = {}


def route(path):                               # a decorator factory for classes
    def register(cls):
        ROUTES[path] = cls.__name__
        return cls
    return register


@route("/books")
@auto_repr
class Book:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages


print(Book("Python", 320))
print(ROUTES)
