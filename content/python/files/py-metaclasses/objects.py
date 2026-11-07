# 1.5 Metaprogramming: type, class hooks and metaclasses
# Example "objects" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Dog:
    sound = "woof"

    def speak(self):
        return self.sound


rex = Dog()
print(type(rex).__name__, type(Dog).__name__, type(type).__name__)
print(isinstance(Dog, type), isinstance(rex, object), isinstance(type, object))

animals = {"dog": Dog}                         # a class can live in a dict
make = animals["dog"]
print(make().speak())


def build(cls, times):                         # and can be passed to a function
    return [cls() for i in range(times)]


print(len(build(Dog, 3)), Dog.__name__, Dog.__bases__)
print(sorted(k for k in vars(Dog) if not k.startswith("__")))
