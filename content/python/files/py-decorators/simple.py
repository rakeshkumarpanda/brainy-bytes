# 1.2 Extended arguments, closures and decorators
# Example "simple" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def shout(func):
    def wrapper(*args, **kwargs):
        print("calling", func.__name__)
        result = func(*args, **kwargs)
        return result
    return wrapper


@shout                                   # the same as add = shout(add)
def add(a, b):
    return a + b


print(add(2, 3))
print(add.__name__)                      # the name is now wrapper: see the next program
