# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
# Example "nosuper" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary


class Intern(Employee):
    def __init__(self, name, school):  # overrides __init__ but forgets super()
        self.school = school


meera = Intern("Meera", "IIT")
print(meera.__dict__)
try:
    print(meera.name)
except AttributeError as err:
    print("AttributeError:", err)
