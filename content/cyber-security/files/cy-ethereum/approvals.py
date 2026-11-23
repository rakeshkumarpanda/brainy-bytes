# 3.2 Ethereum and smart contract security: reentrancy, overflow, oracles and MEV
# Example "approvals" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Token approvals: why "unlimited" approvals turn one bad signature into a total loss
MAX = 2 ** 256 - 1

class Token:
    def __init__(self):
        self.balance = {"you": 5000}
        self.allowance = {}

    def approve(self, owner, spender, amount):
        self.allowance[(owner, spender)] = amount

    def transfer_from(self, spender, owner, to, amount):
        if self.allowance.get((owner, spender), 0) < amount:
            raise PermissionError("not approved")
        if self.allowance[(owner, spender)] != MAX:
            self.allowance[(owner, spender)] -= amount
        self.balance[owner] -= amount
        self.balance[to] = self.balance.get(to, 0) + amount

t = Token()
t.approve("you", "dex", MAX)                       # the app asked for unlimited spending
t.transfer_from("dex", "you", "pool", 100)         # your real trade
print("after trade:", t.balance)
# months later the app's contract is hacked, or you signed for a look alike phishing site
t.transfer_from("dex", "you", "attacker", t.balance["you"])
print("after the hack:", t.balance)

t2 = Token()
t2.approve("you", "dex", 100)                      # approve only what this trade needs
t2.transfer_from("dex", "you", "pool", 100)
try:
    t2.transfer_from("dex", "you", "attacker", 4900)
except PermissionError as e:
    print("exact approval:", e, "| your balance stays", t2.balance["you"])
