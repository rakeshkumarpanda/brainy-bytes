# 3.2 Ethereum and smart contract security: reentrancy, overflow, oracles and MEV
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: A withdraw that cannot be re entered
# Complete withdraw(self, who) in the class. It must follow checks, effects, interactions: raise
# ValueError if the balance is 0, set the balance to 0 before calling who.receive(self, amount), and
# reduce vault. The test attacker calls withdraw again from receive and should get nothing extra.
# Hint: Read the amount, check it, set the balance to 0, reduce the vault, and only then call
# receive.

class Bank:
    def __init__(self):
        self.balance = {}
        self.vault = 0

    def deposit(self, who, amount):
        self.balance[who] = self.balance.get(who, 0) + amount
        self.vault += amount

    def withdraw(self, who):
        # your code here
        pass

class Evil:
    def __init__(self):
        self.got = 0
    def receive(self, bank, amount):
        self.got += amount
        try:
            bank.withdraw(self)
        except ValueError:
            pass

def run_attack():
    b = Bank()
    b.deposit("honest", 10)
    e = Evil()
    b.deposit(e, 1)
    b.withdraw(e)
    return e.got, b.vault


# ================================================================== task 2: Checked and unchecked uint8 maths
# Write add_u8(a, b, checked). With checked=False return the sum wrapped into 0 to 255. With
# checked=True raise OverflowError if the true sum is outside 0 to 255, otherwise return it. b may
# be negative.
# Hint: Compute the true sum first. Python’s % already gives 255 for -1 % 256.

def add_u8(a, b, checked):
    # your code here
    pass


# ================================================================== task 3: A constant product swap
# Write swap_out(x, y, dx, fee) for a pool with reserves x (token in) and y (token out). Apply the
# fee to the input, then return the output y − x y / (x + dx (1 − fee)) rounded to 4 decimals.
# Hint: k = x * y stays fixed. The new y is k divided by the new x.

def swap_out(x, y, dx, fee):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A withdraw that cannot be re entered", [('run_attack()', (1, 10))]))
    results.append(check("Task 2: Checked and unchecked uint8 maths", [('add_u8(250, 10, False)', 4), ('add_u8(0, -1, False)', 255), ('add_u8(7, -3, True)', 4), ('add_u8(200, 55, True)', 255)]))
    results.append(check("Task 3: A constant product swap", [('swap_out(200000, 100, 200000, 0)', 50.0), ('swap_out(200000, 100, 20000, 0)', 9.0909), ('swap_out(100, 100, 100, 0)', 50.0), ('swap_out(200000, 100, 200000, 0.003)', 49.9249)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
