# 1.1 Classical ciphers: Caesar, substitution, Vigenère and the one time pad
# Example "keyspace_maths" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# How big are the key spaces, and how many letters does an attacker need?
import math

caesar_keys = 26
affine_keys = 0
for a in range(26):
    if math.gcd(a, 26) == 1:
        affine_keys = affine_keys + 26          # every good a with every b
substitution_keys = math.factorial(26)

print("Caesar keys      :", caesar_keys)
print("affine keys      :", affine_keys)
print("substitution keys:", substitution_keys)
bits = math.log2(substitution_keys)
print("that is about 2 to the power", round(bits, 1))

# Unicity distance: letters needed before only one key gives sensible English
redundancy = 3.2                                  # bits per English letter (textbook estimate)
print("unicity distance:", round(bits / redundancy, 1), "letters")

# A computer trying a billion keys per second against the substitution cipher
seconds = substitution_keys / 2 / 1e9
print("brute force years:", "%.1e" % (seconds / (365.25 * 24 * 3600)))
