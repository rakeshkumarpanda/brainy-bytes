# 1.3 Class design: methods, properties, abstract classes and dataclasses
# Example "dataclass" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from dataclasses import dataclass, field, asdict, astuple, replace


@dataclass
class Item:
    name: str
    price: float
    qty: int = 1                               # a default

    @property
    def total(self):
        return self.price * self.qty


@dataclass
class Cart:
    owner: str
    items: list = field(default_factory=list)  # NEVER items: list = []

    def add(self, item):
        self.items.append(item)


pen = Item("pen", 10.0, 3)
print(pen, pen.total)
print(pen == Item("pen", 10.0, 3))             # __eq__ compares the fields
print(asdict(pen), astuple(pen))
print(replace(pen, qty=5))                     # a changed copy

a, b = Cart("Asha"), Cart("Ravi")
a.add(pen)
print(len(a.items), len(b.items))              # separate lists
