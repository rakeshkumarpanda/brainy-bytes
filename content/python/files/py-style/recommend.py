# 3.1 Clean code: PEP 8, docstrings and type hints
# Example "recommend" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Weird:
    def __eq__(self, other):
        return True                            # claims to equal everything


w = Weird()
print(w == None, w is None)                    # == can be fooled, is cannot

items = []
if not items:                                  # empty things count as false
    print("empty list")
print(bool(""), bool(0), bool([0]), bool(" "))

print(isinstance(True, int), type(True) == int)   # isinstance respects inheritance

name = "report.csv"
print(name.endswith(".csv"), name[-4:] == ".csv")  # say what you mean


def add_item(item, basket=None):               # never use a list as a default
    if basket is None:
        basket = []
    basket.append(item)
    return basket


print(add_item("tea"), add_item("milk"))
