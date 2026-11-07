# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
# Example "compose" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Engine:
    def __init__(self, power):
        self.power = power

    def start(self):
        return "engine with " + str(self.power) + " hp started"


class Car:                             # a car HAS an engine (composition)
    def __init__(self, model, power):
        self.model = model
        self.engine = Engine(power)

    def start(self):
        return self.model + ": " + self.engine.start()   # pass the work on (delegation)


class BadStack(list):                  # a stack IS a list: then it gets every list method
    def push(self, item):
        self.append(item)


class GoodStack:                       # a stack HAS a list
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()


print(Car("Nano", 37).start())
bad = BadStack()
bad.push(1)
bad.push(2)
bad.insert(0, 99)                      # allowed, but it breaks the stack rule
print(bad)
good = GoodStack()
good.push(1)
print(hasattr(good, "insert"))
