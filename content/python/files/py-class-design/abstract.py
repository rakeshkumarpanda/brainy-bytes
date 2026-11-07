# 1.3 Class design: methods, properties, abstract classes and dataclasses
# Example "abstract" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from abc import ABC, abstractmethod
from collections.abc import Sized


class Payment(ABC):                            # cannot be made directly
    @abstractmethod
    def pay(self, amount):
        """Every payment method must say how it pays."""

    @property
    @abstractmethod
    def name(self):
        ...

    def receipt(self, amount):                 # normal methods are shared
        return f"{self.name}: paid {amount} -> {self.pay(amount)}"


class Upi(Payment):
    name = "UPI"

    def pay(self, amount):
        return "ok"


class Card(Payment):
    name = "Card"                              # forgot pay()


print(Upi().receipt(250))
for cls in [Payment, Card]:
    try:
        cls()
    except TypeError as err:
        print("TypeError:", err)


class Box:
    def __len__(self):
        return 3


print(isinstance(Box(), Sized))                # collections.abc checks for __len__
