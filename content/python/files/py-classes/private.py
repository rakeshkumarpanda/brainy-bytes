# 6.1 Classes and objects: attributes, methods, self and encapsulation
# Example "private" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Account:
    def __init__(self, owner, balance):
        self.owner = owner             # public
        self._note = "vip"             # one underscore: "internal, please do not touch"
        self.__balance = balance       # two underscores: name mangled

    def balance(self):
        return self.__balance          # inside the class the short name works


acc = Account("Asha", 500)
print(acc.owner, acc._note, acc.balance())
try:
    print(acc.__balance)
except AttributeError as err:
    print("AttributeError:", err)
print(acc.__dict__)                    # the real name is _Account__balance
print(acc._Account__balance)           # still reachable: mangling is not security
