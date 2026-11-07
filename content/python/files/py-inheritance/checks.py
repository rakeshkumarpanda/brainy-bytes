# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
# Example "checks" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Animal:
    pass


class Dog(Animal):
    pass


rex = Dog()
print(isinstance(rex, Dog), isinstance(rex, Animal), isinstance(rex, object))
print(type(rex) == Dog, type(rex) == Animal)      # type() ignores parents
print(issubclass(Dog, Animal), issubclass(Animal, Dog))
print(Dog.__bases__, Animal.__bases__)
print([c.__name__ for c in Dog.__mro__])
print(issubclass(bool, int), isinstance(True, int), True + True)
print(isinstance(3, (str, int)))                  # a tuple means "any of these"
