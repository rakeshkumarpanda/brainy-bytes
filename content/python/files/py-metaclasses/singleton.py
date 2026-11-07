# 1.5 Metaprogramming: type, class hooks and metaclasses
# Example "singleton" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Singleton(type):
    instances = {}

    def __call__(cls, *args, **kwargs):        # runs on Config(...)
        if cls not in Singleton.instances:
            print("creating", cls.__name__)
            Singleton.instances[cls] = super().__call__(*args, **kwargs)
        return Singleton.instances[cls]


class Config(metaclass=Singleton):
    def __init__(self, mode="dev"):
        self.mode = mode


a = Config("prod")
b = Config("test")                             # the same object comes back
print(a is b, a.mode, b.mode)
