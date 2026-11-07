# 5.1 Exceptions: try, except, else, finally and raise
# Example "reraise" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

log = []

def withdraw(balance, amount):
    try:
        if amount > balance:
            raise ValueError("not enough money")
        return balance - amount
    except ValueError:
        log.append(f"failed withdraw of {amount}")
        raise                          # bare raise: log it, then pass the same exception on

try:
    withdraw(100, 500)
except ValueError as err:
    print("caller got:", err)
print(log)
