# 4.1 Functions: def, return and every kind of argument
# Example "mutdef" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def add_bad(item, bag=[]):        # the default list is made ONCE, when def runs
    bag.append(item)
    return bag

print(add_bad("pen"))
print(add_bad("ink"))             # the same list again!

def add_good(item, bag=None):     # the usual fix
    if bag is None:
        bag = []                  # a new list on every call
    bag.append(item)
    return bag

print(add_good("pen"))
print(add_good("ink"))
print(add_bad.__defaults__)
