# 1.5 Metaprogramming: type, class hooks and metaclasses
# Example "introspect" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import inspect


class Account:
    bank = "City Bank"

    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount, note=""):
        self.balance += amount


acc = Account("Asha", 100)
print(getattr(acc, "owner"), getattr(acc, "pin", "no pin"))
print(hasattr(acc, "deposit"), callable(acc.deposit), callable(acc.owner))
setattr(acc, "branch", "Pune")                 # add an attribute by its name
print(vars(acc))
action = "deposit"                             # a method chosen while the program runs
getattr(acc, action)(50)
print(acc.balance)
print([name for name in dir(acc) if not name.startswith("_")])
print(inspect.signature(Account.deposit))
print(acc.__class__.__name__, Account.__dict__["bank"], [c.__name__ for c in Account.__mro__])
