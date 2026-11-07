# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
# Model solutions. Try practice.py first.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: A shape family
# The class Shape is given. Write Square(side) and Rectangle(w, h) as children of Shape, each with
# its own area(). Do not write describe again: it is inherited. raises() is a test helper.
# Why it works: describe was written once in Shape, yet it prints the right name and area for every
# child. That is inheritance and polymorphism working together.

class Shape:
    def area(self):
        raise NotImplementedError("each shape must define area()")

    def describe(self):
        return type(self).__name__ + " with area " + str(self.area())


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side


class Rectangle(Shape):
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h


def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None


# ================================================================== task 2: Employee and Manager with super()
# Employee is given. Write Manager(name, salary, bonus) as a child of Employee. Its __init__ must
# use super() to set name and salary, and store bonus. Its pay() must return the Employee pay plus
# the bonus, using super().pay().
# Why it works: If the monthly pay rule in Employee ever changes, Manager follows it without any
# edit, because it never copied the rule.

class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def pay(self):
        return self.salary // 12


class Manager(Employee):
    def __init__(self, name, salary, bonus):
        super().__init__(name, salary)
        self.bonus = bonus

    def pay(self):
        return super().pay() + self.bonus


# ================================================================== task 3: A ReprMixin
# Write a mixin class ReprMixin with a __repr__ that shows the class name and every instance
# attribute in the order they were set, like Point(x=1, y=2) or Pet(name='Rex'). Use repr() for each
# value. Point and Pet are given and only inherit from the mixin.
# Why it works: type(self) is the real class of the object (Point or Pet), not ReprMixin, so one
# mixin serves every class. dataclasses (Advanced 1.3) generate a __repr__ just like this.

class ReprMixin:
    def __repr__(self):
        parts = []
        for key in self.__dict__:
            parts.append(key + "=" + repr(self.__dict__[key]))
        return type(self).__name__ + "(" + ", ".join(parts) + ")"


class Point(ReprMixin):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Pet(ReprMixin):
    def __init__(self, name):
        self.name = name


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A shape family", [('Square(3).area()', 9), ('Rectangle(2, 5).describe()', 'Rectangle with area 10'), ('isinstance(Square(1), Shape)', True), ('raises(Shape().area)', 'NotImplementedError'), ('Square(2).describe()', 'Square with area 4')]))
    results.append(check("Task 2: Employee and Manager with super()", [('Manager("Asha", 1200, 50).pay()', 150), ('Manager("Asha", 1200, 50).name', 'Asha'), ('Employee("Ravi", 1200).pay()', 100), ('isinstance(Manager("A", 12, 1), Employee)', True), ('Manager("B", 2400, 0).pay()', 200)]))
    results.append(check("Task 3: A ReprMixin", [('repr(Point(1, 2))', 'Point(x=1, y=2)'), ('repr(Pet("Rex"))', "Pet(name='Rex')"), ('str([Point(0, 0)])', '[Point(x=0, y=0)]')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
