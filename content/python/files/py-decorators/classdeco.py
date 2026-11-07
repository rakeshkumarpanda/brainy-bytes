# 1.2 Extended arguments, closures and decorators
# Example "classdeco" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

PLUGINS = {}


def register(cls):                       # a decorator can take a class too
    PLUGINS[cls.__name__.lower()] = cls
    return cls                           # give the class back unchanged


@register
class Csv:
    pass


@register
class Json:
    pass


print(sorted(PLUGINS), PLUGINS["json"] is Json)


class CountCalls:                        # a class can BE a decorator, through __call__
    def __init__(self, func):
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)


@CountCalls                              # square = CountCalls(square)
def square(n):
    return n * n


print(square(3), square(4), square.calls, type(square).__name__)
