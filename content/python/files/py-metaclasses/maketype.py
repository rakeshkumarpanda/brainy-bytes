# 1.5 Metaprogramming: type, class hooks and metaclasses
# Example "maketype" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def init(self, name):
    self.name = name


def speak(self):
    return self.name + " says " + self.sound


# type(name, bases, namespace) builds a class without a class statement
Cat = type("Cat", (object,), {"sound": "meow", "__init__": init, "speak": speak})
print(Cat("Tom").speak(), Cat.__name__, Cat.__bases__)

Kitten = type("Kitten", (Cat,), {"sound": "mew"})   # inheritance works as usual
print(Kitten("Kit").speak(), [c.__name__ for c in Kitten.__mro__])


def make_record(name, fields):                 # build classes from data
    def __init__(self, *values):
        for field_name, value in zip(fields, values):
            setattr(self, field_name, value)

    def __repr__(self):
        parts = []
        for field_name in fields:
            parts.append(field_name + "=" + repr(getattr(self, field_name)))
        return name + "(" + ", ".join(parts) + ")"

    return type(name, (), {"__init__": __init__, "__repr__": __repr__, "fields": fields})


Point = make_record("Point", ["x", "y"])
print(Point(3, 4), Point.fields)
