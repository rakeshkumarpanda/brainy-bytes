# 1.3 Hash functions, MACs and password storage
# Example "hash_props" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Collisions and preimages on SHORT hashes, to see the 2^(n/2) and 2^n rules in action
import hashlib

def short_hash(text, bits):              # keep only the first bits of SHA-256
    full = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    return full >> (256 - bits)

# Collision: any two different messages with the same 24 bit hash
seen = {}
i = 0
while True:
    msg = "text " + str(i)
    h = short_hash(msg, 24)
    if h in seen:
        print("24 bit collision after", i + 1, "tries:", repr(seen[h]), "and", repr(msg))
        break
    seen[h] = msg
    i = i + 1
print("birthday rule predicts about", round(1.1774 * 2 ** 12), "tries")

# Preimage: a message whose 16 bit hash equals a GIVEN target
target = short_hash("hello", 16)
j = 0
while short_hash("guess " + str(j), 16) != target:
    j = j + 1
print("16 bit preimage after", j + 1, "tries, the rule predicts about", 2 ** 16)
print("single runs vary a lot: the rules give the average over many runs")
