# 1.3 The maths for security: bits, XOR, mod, counting, probability and entropy
# Example "entropy" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

import math
import random

# Shannon entropy: the average number of bits of surprise per symbol
def entropy(data):
    counts = {}
    for symbol in data:
        counts[symbol] = counts.get(symbol, 0) + 1
    total = len(data)
    h = 0.0
    for c in counts.values():
        p = c / total
        h = h - p * math.log2(p)
    return h

print("aaaaaaaa      ->", round(entropy("aaaaaaaa"), 3), "bits per symbol")
print("abababab      ->", round(entropy("abababab"), 3))
print("english text  ->", round(entropy("the quick brown fox jumps over the lazy dog"), 3))

random.seed(3)
noise = [random.randrange(256) for i in range(4096)]
print("random bytes  ->", round(entropy(noise), 3), "(the most is 8 bits per byte)")

# Strength of a random password: length x log2(number of symbols)
print("random 12 char password from 95 symbols:", round(12 * math.log2(95), 1), "bits")
