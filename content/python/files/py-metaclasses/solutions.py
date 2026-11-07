# 1.5 Metaprogramming: type, class hooks and metaclasses
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


# ================================================================== task 1: A shape registry with __init_subclass__
# Make every child of Shape register itself in Shape.registry under the key given in its class line
# (for example class Circle(Shape, key="circle")). Then write make(key, *args) that builds the right
# shape, and raises KeyError for an unknown key. Circle uses 3.14 for pi. raises() is a test helper.
# Why it works: Adding a new shape now needs no change to make(): the new class registers itself the
# moment it is defined.

class Shape:
    registry = {}

    def __init_subclass__(cls, key, **kwargs):
        super().__init_subclass__(**kwargs)
        Shape.registry[key] = cls


class Circle(Shape, key="circle"):
    def __init__(self, r):
        self.r = r

    def area(self):
        return 3.14 * self.r * self.r


class Square(Shape, key="square"):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side


def make(key, *args):
    cls = Shape.registry[key]                  # KeyError for an unknown key
    return cls(*args)


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None


# ================================================================== task 2: A class factory with type()
# Write make_class(name, attrs) that uses type() to build a class called name, with the dict attrs
# as class attributes, and a method describe(self) that returns the class name, a colon, and the
# attribute names sorted and joined by ", ". Example: make_class("Car", {"wheels": 4, "doors":
# 2})().describe() gives "Car: doors, wheels".
# Why it works: describe remembers name and keys through its closure, so every class built by the
# factory describes itself correctly.

def make_class(name, attrs):
    keys = sorted(attrs)

    def describe(self):
        return name + ": " + ", ".join(keys)

    namespace = dict(attrs)
    namespace["describe"] = describe
    return type(name, (), namespace)


# ================================================================== task 3: A metaclass that demands docstrings
# Write a metaclass RequireDoc. When it builds a class, every public method (a callable whose name
# does not start with "_") must have a docstring, or it raises TypeError. It also adds a class
# attribute methods: the sorted list of public method names. The helper try_class(meta, name,
# namespace) builds a class or returns the error name. documented and bare are sample functions.
# Why it works: The rule runs once per class, when it is defined, so a missing docstring is caught
# as soon as the module is imported.

class RequireDoc(type):
    def __new__(mcs, name, bases, namespace):
        methods = []
        for key, value in namespace.items():
            if key.startswith("_") or not callable(value):
                continue
            if not value.__doc__:
                raise TypeError(name + "." + key + " has no docstring")
            methods.append(key)
        namespace["methods"] = sorted(methods)
        return super().__new__(mcs, name, bases, namespace)


def documented(self):
    """Does the work."""


def bare(self):
    pass


def try_class(meta, name, namespace):
    try:
        return meta(name, (), dict(namespace))
    except Exception as err:
        return type(err).__name__


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A shape registry with __init_subclass__", [('sorted(Shape.registry)', ['circle', 'square']), ('make("square", 3).area()', 9), ('make("circle", 1).area()', 3.14), ('raises(make, "hexagon", 2)', 'KeyError')]))
    results.append(check("Task 2: A class factory with type()", [('make_class("Car", {"wheels": 4, "doors": 2})().describe()', 'Car: doors, wheels'), ('make_class("Bike", {"wheels": 2}).wheels', 2), ('make_class("Box", {}).__name__', 'Box'), ('make_class("Tag", {"x": 1})().describe()', 'Tag: x')]))
    results.append(check("Task 3: A metaclass that demands docstrings", [('try_class(RequireDoc, "Good", {"run": documented, "stop": documented}).methods', ['run', 'stop']), ('try_class(RequireDoc, "Bad", {"run": bare})', 'TypeError'), ('try_class(RequireDoc, "Mixed", {"_helper": bare, "run": documented}).methods', ['run']), ('try_class(RequireDoc, "Data", {"size": 3}).methods', [])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
