# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
# Example "diamond" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class A:
    def hello(self):
        return "A"


class B(A):
    def hello(self):
        return "B" + super().hello()


class C(A):
    def hello(self):
        return "C" + super().hello()


class D(B, C):
    def hello(self):
        return "D" + super().hello()


print([c.__name__ for c in D.__mro__])
print(D().hello())                     # each class runs once, A last
print(B().hello())                     # on a B object, super() in B goes to A
