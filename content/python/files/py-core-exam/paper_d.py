# 7.1 Exam practice: PCEP and PCAP style papers
# Example "paper_d" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class A:
    x = 1
a = A()
a.x = 2
print("Q1", A.x, a.x, "x" in a.__dict__)

class B:
    def __init__(self):
        self.__secret = 1
b = B()
print("Q2", hasattr(b, "__secret"), hasattr(b, "_B__secret"))

class P:
    def f(self):
        return "P"
class Q(P):
    def f(self):
        return "Q" + super().f()
print("Q3", Q().f(), isinstance(Q(), P), issubclass(P, Q))

print("Q4", "abc" < "abd", "Z" < "a", "10" < "9", ord("A"), chr(97))
print("Q5", "a,b,,c".split(","), " x  y ".split(), "-".join("abc"))
print("Q6", "Hello".center(9, "*"), "abc def".title(), "ab".isalpha(), "12".isdigit())

import math
print("Q7", math.floor(-2.5), math.ceil(-2.5), math.trunc(-2.5), math.sqrt(16))
print("Q8", __name__)

class C:
    def __str__(self):
        return "C!"
print("Q9", C(), str(C()) + "?", f"{C()}")

gen = (n * n for n in range(4))
print("Q10", next(gen), sum(gen))
print("Q11", [n for n in range(10) if n % 3 == 0], {n: n * n for n in range(3)})

def make(k):
    return lambda v: v * k
triple = make(3)
print("Q12", triple(4), make(2)("ab"))

class Base:
    def __init__(self):
        self.name = "base"
class Child(Base):
    def __init__(self):
        pass
try:
    print(Child().name)
except AttributeError as err:
    print("Q13", type(err).__name__)
