# 3.1 Blockchain security: hash chains, mining, consensus and wallets
# Example "mine" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Proof of work: find a nonce so that the hash starts with enough zeros
import hashlib

def mine(data, zeros):
    target = "0" * zeros
    nonce = 0
    while True:
        h = hashlib.sha256(f"{data}|{nonce}".encode()).hexdigest()
        if h.startswith(target):
            return nonce, h
        nonce += 1

for zeros in (1, 2, 3):
    nonce, h = mine("Block 7: Asha pays Ravi 5", zeros)
    print(f"{zeros} zero(s): nonce {nonce:5d} after {nonce + 1:5d} tries (average {16 ** zeros:5d})  {h[:20]}")

# checking is one hash, whatever the difficulty
nonce, h = mine("Block 7: Asha pays Ravi 5", 3)
check = hashlib.sha256(f"Block 7: Asha pays Ravi 5|{nonce}".encode()).hexdigest()
print("anyone can check the work with one hash:", check == h)
