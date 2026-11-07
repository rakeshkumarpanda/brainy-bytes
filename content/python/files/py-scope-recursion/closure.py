# 4.2 Scope and recursion: LEGB, closures and the call stack
# Example "closure" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def make_counter():
    n = 0
    def step():
        nonlocal n        # change n of make_counter, not a new local
        n += 1
        return n
    return step

a = make_counter()
b = make_counter()        # a second, separate counter
print(a(), a(), a())
print(b())
print(a.__closure__[0].cell_contents)   # where a keeps its n

def multiplier(k):
    def times(x):
        return x * k      # reading k needs no nonlocal
    return times

double = multiplier(2)
triple = multiplier(3)
print(double(10), triple(10))
