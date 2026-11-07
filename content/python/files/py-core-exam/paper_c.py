# 7.1 Exam practice: PCEP and PCAP style papers
# Example "paper_c" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def f(a, b=2, *args, c, **kw):
    return a, b, args, c, kw
print("Q1", f(1, 3, 4, 5, c=6, d=7))

def add(item, items=[]):
    items.append(item)
    return items
add(1)
print("Q2", add(2))

x = 10
def g():
    print(x)
    x = 5
try:
    g()
except NameError as err:
    print("Q3", type(err).__name__)

funcs = [lambda: i for i in range(3)]
print("Q4", [fn() for fn in funcs])

def h():
    try:
        return "try"
    finally:
        print("Q5 finally runs")
print("Q5", h())

try:
    int("x")
except ValueError:
    print("Q6 V")
except Exception:
    print("Q6 E")
else:
    print("Q6 else")
finally:
    print("Q6 fin")

def nothing():
    pass
print("Q7", nothing())

try:
    raise KeyError("k")
except LookupError as err:
    print("Q8", type(err).__name__, err)

print("Q9", list(map(lambda n: n * 2, filter(lambda n: n % 2, range(6)))))

def outer():
    n = 0
    def inner():
        nonlocal n
        n += 1
        return n
    return inner
counter = outer()
counter()
print("Q10", counter())
