# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
# Example "multi" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import json


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age


class JsonMixin:                       # a small class that only adds one ability
    def to_json(self):
        return json.dumps(self.__dict__)


class Employee(Person, JsonMixin):     # two parents
    def __init__(self, name, age, job):
        super().__init__(name, age)
        self.job = job


asha = Employee("Asha", 30, "pilot")
print(asha.to_json())
print([c.__name__ for c in Employee.__mro__])
print(Employee.__bases__)
