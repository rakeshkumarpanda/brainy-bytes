# 3.2 Ethereum and smart contract security: reentrancy, overflow, oracles and MEV
# Example "reentrancy_sim" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Reentrancy in Python: a bank that sends money before updating its ledger
class Bank:
    def __init__(self, safe, locked_style=False):
        self.balance = {}
        self.vault = 0
        self.safe = safe
        self.locked_style = locked_style
        self.lock = False

    def deposit(self, who, amount):
        self.balance[who] = self.balance.get(who, 0) + amount
        self.vault += amount

    def withdraw(self, who):
        if self.locked_style:
            if self.lock:
                raise RuntimeError("reentrant call refused")
            self.lock = True
        try:
            amount = self.balance.get(who, 0)
            if amount <= 0 or self.vault < amount:
                raise RuntimeError("nothing to withdraw")
            if self.safe:
                self.balance[who] = 0            # effect first
            self.vault -= amount
            who.receive(self, amount)             # interaction: control passes to the receiver
            self.balance[who] = 0                 # the buggy bank updates only now
        finally:
            if self.locked_style:
                self.lock = False

class Attacker:
    def __init__(self):
        self.wallet = 0
        self.calls = 0
    def receive(self, bank, amount):
        self.wallet += amount
        self.calls += 1
        try:
            bank.withdraw(self)                   # call straight back in
        except RuntimeError as e:
            if self.calls == 1:
                print("   second call stopped:", e)

for name, bank in [("buggy", Bank(safe=False)), ("checks effects interactions", Bank(safe=True)),
                   ("reentrancy lock", Bank(safe=False, locked_style=True))]:
    for i in range(10):
        bank.deposit(f"customer{i}", 1)
    evil = Attacker()
    bank.deposit(evil, 1)
    print(name)
    bank.withdraw(evil)
    print(f"   attacker put in 1, now holds {evil.wallet}, bank vault left {bank.vault}")
