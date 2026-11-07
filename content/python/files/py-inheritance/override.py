# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
# Example "override" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Animal:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "an animal called " + self.name

    def speak(self):
        return "..."


class Dog(Animal):
    def __str__(self):
        return "a dog called " + self.name     # replaces the parent version

    def speak(self):
        old = Animal.speak(self)               # call the parent by its name (works, but super() is better)
        return old + " woof!"


rex = Dog("Rex")
print(rex)
print(rex.speak())
print(Dog.speak is Animal.speak, "speak" in Dog.__dict__, "__init__" in Dog.__dict__)
