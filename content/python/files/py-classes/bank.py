# 6.1 Classes and objects: attributes, methods, self and encapsulation
# Example "bank" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class BankAccount:
    bank = "Brainy Bank"

    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
        self.history.append(("deposit", amount))

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("not enough money")
        self.balance -= amount
        self.history.append(("withdraw", amount))

    def __str__(self):
        return f"{self.owner} has {self.balance} at {self.bank}"


acc = BankAccount("Asha", 100)
acc.deposit(50)
acc.withdraw(30)
try:
    acc.withdraw(500)
except ValueError as err:
    print("refused:", err)
print(acc)
print(acc.history)
