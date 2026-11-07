# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
# Example "basic" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Animal:                          # the parent class (superclass, base class)
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

    def describe(self):
        return self.name + " says " + self.speak()


class Dog(Animal):                     # Dog inherits everything from Animal
    def speak(self):                   # and overrides speak
        return "woof"


class Cat(Animal):
    def speak(self):
        return "meow"


class Fish(Animal):                    # overrides nothing
    pass


for pet in [Dog("Rex"), Cat("Tom"), Fish("Nemo")]:
    print(pet.describe())              # describe is written once, in Animal
