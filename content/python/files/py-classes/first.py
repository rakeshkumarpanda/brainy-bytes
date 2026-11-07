# 6.1 Classes and objects: attributes, methods, self and encapsulation
# Example "first" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Dog:
    species = "dog"                    # class attribute: shared by every dog

    def __init__(self, name, age):     # runs when a new dog is made
        self.name = name               # instance attributes: each dog has its own
        self.age = age

    def bark(self):                    # a method: a function that belongs to the class
        return self.name + " says woof"

    def birthday(self):
        self.age += 1


rex = Dog("Rex", 3)                    # make an object (an instance) of the class
moti = Dog("Moti", 5)
print(rex.name, rex.age, "|", moti.name, moti.age)
print(rex.bark())
rex.birthday()
print(rex.age, moti.age)               # only Rex got older
print(type(rex).__name__, isinstance(rex, Dog), rex.species)
