# 1.3 Class design: methods, properties, abstract classes and dataclasses
# Example "descriptor" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Positive:
    """A reusable rule: the attribute must be a number above 0."""

    def __set_name__(self, owner, name):       # told the attribute name when the class is made
        self.private = "_" + name

    def __get__(self, obj, owner):
        if obj is None:
            return self
        return getattr(obj, self.private)

    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(self.private[1:] + " must be positive")
        setattr(obj, self.private, value)


class Product:
    price = Positive()                         # one rule object per attribute
    stock = Positive()

    def __init__(self, price, stock):
        self.price = price
        self.stock = stock


p = Product(99.5, 10)
print(p.price, p.stock, vars(p))
for field_name, bad in [("price", 0), ("stock", -5)]:
    try:
        setattr(p, field_name, bad)
    except ValueError as err:
        print("ValueError:", err)
