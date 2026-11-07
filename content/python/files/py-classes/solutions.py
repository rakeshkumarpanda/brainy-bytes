# 6.1 Classes and objects: attributes, methods, self and encapsulation
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


# ================================================================== task 1: A Rectangle class
# Write a class Rectangle made with Rectangle(width, height). Give it the methods area(),
# perimeter() and is_square(), and a __str__ that returns text like "Rectangle 3 x 4".
# Why it works: The methods need no arguments apart from self, because the object already knows its
# own size.

class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def is_square(self):
        return self.width == self.height

    def __str__(self):
        return "Rectangle " + str(self.width) + " x " + str(self.height)


# ================================================================== task 2: A safe bank account
# Write a class Account(owner, balance=0). deposit(amount) adds money and returns the new balance,
# but raises ValueError if amount is not more than 0. withdraw(amount) takes money and returns the
# new balance, but raises ValueError if amount is more than the balance. The balance must not change
# when an error is raised. raises() is a test helper.
# Why it works: Checking before changing is what keeps the object valid. If you changed the balance
# first and checked after, a refused withdrawal would still have taken the money.

class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance = self.balance + amount
        return self.balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("not enough money")
        self.balance = self.balance - amount
        return self.balance


def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None


# ================================================================== task 3: A Stack class with its own list
# Write a class Stack with push(item), pop() (returns the top item, raises IndexError if empty),
# peek() (returns the top without removing it), __len__ so that len(stack) works, and __repr__ that
# returns text like "Stack([1, 2])". Two stacks must never share items.
# Why it works: The starter put the list on the class, so every stack would share it. That is the
# shared list trap from this chapter.

class Stack:
    def __init__(self):
        self.items = []         # a new list for every stack

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if len(self.items) == 0:
            raise IndexError("pop from empty stack")
        return self.items.pop()

    def peek(self):
        return self.items[-1]

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return "Stack(" + repr(self.items) + ")"


def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A Rectangle class", [('Rectangle(3, 4).area()', 12), ('Rectangle(3, 4).perimeter()', 14), ('Rectangle(3, 4).is_square()', False), ('Rectangle(5, 5).is_square()', True), ('str(Rectangle(3, 4))', 'Rectangle 3 x 4')]))
    results.append(check("Task 2: A safe bank account", [('Account("Asha", 100).deposit(50)', 150), ('Account("Asha", 100).withdraw(30)', 70), ('raises(Account("Asha").deposit, 0)', 'ValueError'), ('raises(Account("Asha", 10).withdraw, 11)', 'ValueError'), ('(lambda a: (raises(a.withdraw, 500), a.balance))(Account("Ravi", 100))', ['ValueError', 100])]))
    results.append(check("Task 3: A Stack class with its own list", [('(lambda s: (s.push(1), s.push(2), s.pop(), len(s), s.peek()))(Stack())', [None, None, 2, 1, 1]), ('raises(Stack().pop)', 'IndexError'), ('(lambda s: (s.push(1), s.push(2), repr(s))[2])(Stack())', 'Stack([1, 2])'), ('(lambda a, b: (a.push(1), len(b))[1])(Stack(), Stack())', 0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
