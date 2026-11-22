# 3.1 Blockchain security: hash chains, mining, consensus and wallets
# Example "hash_chain" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A tiny blockchain: every block stores the SHA-256 fingerprint of the block before it
import hashlib

def block_hash(number, prev, data):
    text = f"{number}|{prev}|{data}"
    return hashlib.sha256(text.encode()).hexdigest()

def make_chain(payments):
    chain = [{"n": 0, "prev": "0" * 64, "data": "genesis"}]
    chain[0]["hash"] = block_hash(0, chain[0]["prev"], "genesis")
    for i, p in enumerate(payments, start=1):
        prev = chain[-1]["hash"]
        chain.append({"n": i, "prev": prev, "data": p, "hash": block_hash(i, prev, p)})
    return chain

def check(chain):
    for i, b in enumerate(chain):
        if b["hash"] != block_hash(b["n"], b["prev"], b["data"]):
            return f"block {i}: its stored hash does not match its contents"
        if i and b["prev"] != chain[i - 1]["hash"]:
            return f"block {i}: the link to block {i - 1} is broken"
    return "valid"

chain = make_chain(["Asha pays Ravi 5", "Ravi pays Meena 2", "Meena pays Arjun 1"])
for b in chain:
    print(b["n"], b["hash"][:16], "<-", b["prev"][:16], "|", b["data"])
print("check:", check(chain))

chain[1]["data"] = "Asha pays Ravi 50"          # a cheater edits an old block
print("after editing block 1:", check(chain))
chain[1]["hash"] = block_hash(1, chain[1]["prev"], chain[1]["data"])   # and fixes its own hash
print("after fixing block 1's hash:", check(chain))
