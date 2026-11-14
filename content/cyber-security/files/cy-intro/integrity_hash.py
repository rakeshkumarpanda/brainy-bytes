# 1.1 What cybersecurity is: goals, threats and layers
# Example "integrity_hash" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

import hashlib

# A hash is a short fingerprint of data. Change one letter and the fingerprint changes completely.
bill = "Pay 5000 rupees to account 1234 5678"
changed = "Pay 5000 rupees to account 1234 5679"

fingerprint_1 = hashlib.sha256(bill.encode()).hexdigest()
fingerprint_2 = hashlib.sha256(changed.encode()).hexdigest()

print("original:", fingerprint_1)
print("changed: ", fingerprint_2)

same = 0
for a, b in zip(fingerprint_1, fingerprint_2):
    if a == b:
        same = same + 1
print("matching characters:", same, "of", len(fingerprint_1))
print("is the bill unchanged?", fingerprint_1 == fingerprint_2)
