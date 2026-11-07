# 1.2 Extended arguments, closures and decorators
# Example "stack" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def tag(name):
    def decorate(func):
        def wrapper():
            print("enter", name)
            result = "<" + name + ">" + func() + "</" + name + ">"
            print("leave", name)
            return result
        return wrapper
    return decorate


@tag("b")                                # applied second, runs first
@tag("i")                                # applied first, runs second
def hello():
    return "hello"


print(hello())
