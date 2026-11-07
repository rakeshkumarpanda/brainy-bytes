# 1.2 Extended arguments, closures and decorators
# Example "count" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from functools import wraps


def count_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1               # a function can have its own attributes
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper


@count_calls
def greet(name):
    return "hi " + name


greet("Asha")
greet("Ravi")
print(greet("Meera"), greet.calls)
