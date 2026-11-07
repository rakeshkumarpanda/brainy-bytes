# 6.1 Classes and objects: attributes, methods, self and encapsulation
# Example "identity" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Box:
    def __init__(self, size):
        self.size = size


a = Box(5)
b = Box(5)
c = a                                  # c is another name for the SAME object
print(a == b, a is b, a is c)          # by default == means "is"
c.size = 9
print(a.size)                          # a changed too


class Coin:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):           # decide what "equal" means for coins
        return isinstance(other, Coin) and self.value == other.value


print(Coin(5) == Coin(5), Coin(5) is Coin(5), Coin(5) == 5)
print(Coin.__hash__)                   # None: a class with __eq__ but no __hash__ cannot go in a set
