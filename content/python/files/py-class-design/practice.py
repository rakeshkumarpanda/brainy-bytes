# 1.3 Class design: methods, properties, abstract classes and dataclasses
# Practice tasks. Fill in each function, then run this file.
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


# ================================================================== task 1: A bank account with a checked balance
# Write Account(owner, balance=0). Make balance a property whose setter raises ValueError for a
# negative value. Add a class method from_text("Asha:250") that returns an account, and a static
# method valid_owner(name) that returns True when name is not empty and only letters.
# Hint: Property with @balance.setter storing self._balance. from_text splits on ":" and returns
# cls(...). valid_owner can use str.isalpha (which is False for "").

class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    # your code here


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None


# ================================================================== task 2: An abstract Shape
# Shape is an abstract class with an abstract method area() and a normal method describe(). Write
# Circle(r) (use 3.14 for pi) and Square(side) as children. raises() is a test helper.
# Hint: Inherit from Shape and write __init__ and area in each child.

from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    def describe(self):
        return type(self).__name__ + " " + str(round(self.area(), 2))


class Circle:
    pass


class Square:
    pass


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None


# ================================================================== task 3: An Order dataclass
# Write a dataclass Order with fields customer (str), items (a list, default empty, never shared)
# and discount (float, default 0.0). Add a method add(name, price) that appends (name, price), and a
# property total that returns the sum of prices times (1 − discount), rounded to 2 places. In
# __post_init__, raise ValueError if discount is not between 0 and 1.
# Hint: Use @dataclass with field(default_factory=list). Check the discount in __post_init__. total
# loops over the (name, price) pairs.

from dataclasses import dataclass, field


class Order:
    pass


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A bank account with a checked balance", [('Account.from_text("Asha:250").balance', 250), ('Account.from_text("Asha:250").owner', 'Asha'), ('raises(Account, "Ravi", -5)', 'ValueError'), ('(lambda a: (raises(setattr, a, "balance", -1), a.balance))(Account("Meera", 10))', ['ValueError', 10]), ('(Account.valid_owner("Asha"), Account.valid_owner(""), Account.valid_owner("A1"))', [True, False, False])]))
    results.append(check("Task 2: An abstract Shape", [('Circle(1).describe()', 'Circle 3.14'), ('Square(3).area()', 9), ('raises(Shape)', 'TypeError'), ('isinstance(Square(1), Shape)', True)]))
    results.append(check("Task 3: An Order dataclass", [('(lambda o: (o.add("pen", 10), o.add("book", 90), o.total))(Order("Asha", discount=0.1))[2]', 90.0), ('(lambda a, b: (a.add("x", 1), len(b.items))[1])(Order("A"), Order("B"))', 0), ('raises(Order, "C", [], 1.5)', 'ValueError'), ('repr(Order("Ravi"))', "Order(customer='Ravi', items=[], discount=0.0)")]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
