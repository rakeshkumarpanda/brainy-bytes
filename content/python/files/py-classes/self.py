# 6.1 Classes and objects: attributes, methods, self and encapsulation
# Example "self" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        return self.name + " says woof"

    def hello():                       # a mistake: forgot self
        return "hi"


rex = Dog("Rex")
print(rex.bark())
print(Dog.bark(rex))                   # the same call, written the long way
print(type(Dog.bark).__name__, type(rex.bark).__name__)
print(rex.bark.__self__ is rex)        # the bound method remembers its object

try:
    Dog.bark()
except TypeError as err:
    print("TypeError:", err)

try:
    rex.hello()
except TypeError as err:
    print("TypeError:", err)
