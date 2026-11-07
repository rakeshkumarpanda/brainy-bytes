# 1.2 Extended arguments, closures and decorators
# Example "wraps" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from functools import wraps


def plain(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def careful(func):
    @wraps(func)                         # copy name, docstring and more from func
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@plain
def area(w, h):
    """Return the area of a rectangle."""
    return w * h


@careful
def volume(w, h, d):
    """Return the volume of a box."""
    return w * h * d


print(area.__name__, area.__doc__)
print(volume.__name__, volume.__doc__)
print(volume.__wrapped__(1, 2, 3))       # wraps also keeps the original
