# 5.1 Exceptions: try, except, else, finally and raise
# Example "custom" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class BankError(Exception):
    """Base class for every error of this bank program."""

class InsufficientFunds(BankError):
    def __init__(self, balance, amount):
        super().__init__(f"balance {balance} is less than {amount}")
        self.balance = balance
        self.amount = amount

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFunds(balance, amount)
    return balance - amount

try:
    withdraw(300, 1000)
except BankError as err:                 # catches every bank error
    print("Error:", err)
    print("short by", err.amount - err.balance)
print(InsufficientFunds.__mro__[1].__name__)
