# 1.3 The maths for security: bits, XOR, mod, counting, probability and entropy
# Example "key_space" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# How many passwords exist, and how long does trying them all take?
guesses_per_second = 1_000_000_000      # an assumed attacker speed: one billion guesses each second
seconds_per_year = 365 * 24 * 3600

choices = [
    ("4 digit PIN", 10, 4),
    ("8 lowercase letters", 26, 8),
    ("8 characters from 95 keyboard symbols", 95, 8),
    ("12 characters from 95 keyboard symbols", 95, 12),
]
for name, symbols, length in choices:
    space = symbols ** length
    worst = space / guesses_per_second               # seconds to try every one
    print(name, "| space", space, "| worst case", round(worst / seconds_per_year, 6), "years")

# Each extra bit of key doubles the work
print("2 ** 128 keys =", 2 ** 128)
