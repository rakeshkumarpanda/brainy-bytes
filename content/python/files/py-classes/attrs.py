# 6.1 Classes and objects: attributes, methods, self and encapsulation
# Example "attrs" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Dog:
    species = "dog"

    def __init__(self, name):
        self.name = name


a = Dog("Rex")
b = Dog("Moti")
print(a.__dict__, b.__dict__)          # only instance attributes live here
print("species" in Dog.__dict__)       # the class attribute lives on the class

a.species = "wolf"                     # creates a NEW attribute on a only
print(a.species, b.species, Dog.species)
Dog.species = "canine"                 # changes the class attribute
print(a.species, b.species)
print(a.__dict__)

del a.species                          # remove a's own copy
print(a.species)                       # now found on the class again

a.color = "brown"                      # you may add attributes at any time
print(a.__dict__, hasattr(b, "color"))
