# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
# Example "poly" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Robot:                           # NOT an Animal
    def speak(self):
        return "beep"


class Duck:
    def speak(self):
        return "quack"


def make_noise(thing):                 # works with anything that has speak()
    return thing.speak()


for thing in [Duck(), Robot()]:
    print(type(thing).__name__, make_noise(thing))

print(len("abc"), len([1, 2]), len({"a": 1}))   # built in polymorphism
print(3 + 4, "3" + "4", [3] + [4])               # one operator, many types

try:
    make_noise(42)
except AttributeError as err:
    print("AttributeError:", err)
