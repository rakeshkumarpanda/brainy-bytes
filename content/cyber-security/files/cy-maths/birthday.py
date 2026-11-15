# 1.3 The maths for security: bits, XOR, mod, counting, probability and entropy
# Example "birthday" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

import math

# Chance that at least two of k people share a birthday (365 days)
def shared(k, days=365):
    all_different = 1.0
    for i in range(k):
        all_different = all_different * (days - i) / days
    return 1 - all_different

for k in [10, 23, 50, 70]:
    print(k, "people ->", round(shared(k), 4))

# The quick formula: about 1.1774 x sqrt(N) tries give a 50% chance of a repeat
N = 365
print("50% point estimate:", round(1.1774 * math.sqrt(N), 1))

# For a hash with b bits there are N = 2 ** b values. About 2 ** (b / 2) tries find a collision.
for b in [32, 64, 128, 256]:
    print(b, "bit hash -> about 2 **", b // 2, "tries for a collision")
