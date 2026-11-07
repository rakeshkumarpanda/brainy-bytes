# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
# Example "mroerror" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class X: pass
class Y: pass
class A(X, Y): pass                    # A says: X before Y
class B(Y, X): pass                    # B says: Y before X

try:
    class C(A, B): pass                # no order can keep both promises
except TypeError as err:
    print("TypeError:", err)

try:
    class E(X, X): pass
except TypeError as err:
    print("TypeError:", err)
