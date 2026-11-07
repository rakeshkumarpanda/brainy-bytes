# 4.1 Functions: def, return and every kind of argument
# Example "star" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def total(*numbers):               # any number of positional arguments
    print("numbers is", numbers)   # a tuple
    result = 0
    for n in numbers:
        result += n
    return result

print(total(), total(5), total(1, 2, 3, 4))

def profile(name, **details):      # any number of keyword arguments
    print(name, details)           # a dict

profile("Asha", age=21, city="Pune")

def order(item, *, qty=1, gift=False):     # after * every parameter is keyword-only
    return f"{qty} x {item}{' (gift)' if gift else ''}"

print(order("pen", qty=3, gift=True))

def power(base, exp, /):           # before / every parameter is positional-only
    return base ** exp

print(power(2, 10))
try:
    power(base=2, exp=10)
except TypeError as err:
    print("TypeError:", err)
