# 6.1 Classes and objects: attributes, methods, self and encapsulation
# Example "shared" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Bad:
    tricks = []                        # ONE list, shared by all objects

    def __init__(self, name):
        self.name = name

    def learn(self, trick):
        self.tricks.append(trick)


class Good:
    def __init__(self, name):
        self.name = name
        self.tricks = []               # a new list for every object

    def learn(self, trick):
        self.tricks.append(trick)


a, b = Bad("Rex"), Bad("Moti")
a.learn("sit")
print("Bad: ", b.tricks, a.tricks is b.tricks)

c, d = Good("Rex"), Good("Moti")
c.learn("sit")
print("Good:", d.tricks, c.tricks is d.tricks)
