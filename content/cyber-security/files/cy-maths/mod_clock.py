# 1.3 The maths for security: bits, XOR, mod, counting, probability and entropy
# Example "mod_clock" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Modular arithmetic: count on a clock with n positions
print("15 mod 12 =", 15 % 12)        # 15:00 is 3 o'clock
print("-3 mod 26 =", -3 % 26)        # Python gives a positive answer
print("(7 + 9) mod 10 =", (7 + 9) % 10)
print("(7 x 9) mod 10 =", (7 * 9) % 10)

# The rules: you may take mod at every step and the answer is the same
a, b, n = 1234, 5678, 97
print((a * b) % n, "==", ((a % n) * (b % n)) % n)

# Caesar shift: each letter moves 3 places on a clock of 26 letters
word = "ATTACK"
shift = 3
out = ""
for ch in word:
    position = ord(ch) - ord("A")             # A=0, B=1, ... Z=25
    out = out + chr((position + shift) % 26 + ord("A"))
print(word, "->", out)
