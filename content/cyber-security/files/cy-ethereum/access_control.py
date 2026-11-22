# 3.2 Ethereum and smart contract security: reentrancy, overflow, oracles and MEV
# Example "access_control" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Missing access control: the Parity multisig mistake in miniature (July 2017)
class Wallet:
    def __init__(self):
        self.owners = set()
        self.funds = 0

    def init_wallet(self, caller, owners):
        # BUG: anyone may call this, at any time, and it replaces the owners
        self.owners = set(owners)

    def init_wallet_fixed(self, caller, owners):
        if self.owners:
            raise PermissionError("already initialised")
        self.owners = set(owners)

    def withdraw(self, caller, amount):
        if caller not in self.owners:
            raise PermissionError(f"{caller} is not an owner")
        self.funds -= amount
        return amount

w = Wallet()
w.init_wallet("deployer", {"alice", "bob"})
w.funds = 1000
w.init_wallet("mallory", {"mallory"})              # the attacker simply re initialises
print("stolen:", w.withdraw("mallory", 1000), " funds left:", w.funds)

v = Wallet()
v.init_wallet_fixed("deployer", {"alice", "bob"})
try:
    v.init_wallet_fixed("mallory", {"mallory"})
except PermissionError as e:
    print("fixed wallet:", e)

# tx.origin is the person who started the transaction, msg.sender is whoever called this contract
def is_owner_bad(tx_origin, msg_sender, owner):
    return tx_origin == owner                       # a malicious contract the owner calls passes this

def is_owner_good(tx_origin, msg_sender, owner):
    return msg_sender == owner

print("tx.origin check fooled by a phishing contract:", is_owner_bad("alice", "evil_contract", "alice"))
print("msg.sender check:", is_owner_good("alice", "evil_contract", "alice"))
