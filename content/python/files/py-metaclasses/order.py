# 1.5 Metaprogramming: type, class hooks and metaclasses
# Example "order" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def decorate(cls):
    print("7. the class decorator gets the finished class")
    return cls


class Meta(type):
    @classmethod
    def __prepare__(mcs, name, bases):
        print("1. Meta.__prepare__ makes the namespace dict")
        return {}

    def __new__(mcs, name, bases, ns):
        print("3. Meta.__new__ starts building the class")
        return super().__new__(mcs, name, bases, ns)

    def __init__(cls, name, bases, ns):
        print("6. Meta.__init__ finishes it")
        super().__init__(name, bases, ns)

    def __call__(cls, *args):
        print("8. Meta.__call__ runs when you call the class")
        return super().__call__(*args)


class Base:
    def __init_subclass__(cls):
        print("5. Base.__init_subclass__ hears about the new child")


class Field:
    def __set_name__(self, owner, name):
        print("4. __set_name__ tells a descriptor its name:", name)


@decorate
class Dog(Base, metaclass=Meta):
    print("2. the class body runs")
    size = Field()

    def __init__(self, name):
        print("9. Dog.__init__ fills the new object")
        self.name = name


print("--- now make an object ---")
rex = Dog("Rex")
print(rex.name, type(rex).__name__, type(Dog).__name__)
