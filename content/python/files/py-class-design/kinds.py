# 1.3 Class design: methods, properties, abstract classes and dataclasses
# Example "kinds" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from datetime import date


class Person:
    count = 0                                  # class attribute

    def __init__(self, name, born):
        self.name = name
        self.born = born
        Person.count += 1

    def age(self, today):                      # instance method: gets self
        return today.year - self.born

    @classmethod
    def from_text(cls, text):                  # class method: gets cls
        name, born = text.split(",")
        return cls(name.strip(), int(born))    # an alternative constructor

    @staticmethod
    def is_adult(age):                         # static method: gets nothing extra
        return age >= 18


class Student(Person):
    pass


asha = Person("Asha", 1996)
ravi = Person.from_text("Ravi, 2010")
meera = Student.from_text("Meera, 2001")       # cls is Student here
today = date(2026, 11, 7)
print(asha.age(today), ravi.age(today), type(meera).__name__)
print(Person.is_adult(ravi.age(today)), Person.count)
print(type(Person.__dict__["from_text"]).__name__, type(Person.__dict__["is_adult"]).__name__)
