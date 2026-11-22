# 4.2 Mobile security: sandboxes, permissions, signing and the OWASP Mobile Top 10
# Example "lock_maths" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# How strong is a phone lock? PINs, patterns, passwords and the lockout that saves weak ones
import math

def bits(n):
    return math.log2(n)

def count_patterns():
    # Android 3 x 3 pattern: 4 to 9 dots, no dot twice, cannot jump over an unused dot
    skip = {}
    for a, b, mid in [(1, 3, 2), (4, 6, 5), (7, 9, 8), (1, 7, 4), (2, 8, 5), (3, 9, 6), (1, 9, 5), (3, 7, 5)]:
        skip[(a, b)] = skip[(b, a)] = mid
    def walk(cur, used, length):
        if length == 1:
            return 1
        total = 0
        for nxt in range(1, 10):
            if nxt in used:
                continue
            mid = skip.get((cur, nxt))
            if mid and mid not in used:
                continue
            total += walk(nxt, used | {nxt}, length - 1)
        return total
    return sum(walk(s, {s}, L) for L in range(4, 10) for s in range(1, 10))

patterns = count_patterns()
for name, n in [("4 digit PIN", 10 ** 4), ("6 digit PIN", 10 ** 6), ("Android pattern", patterns),
                ("8 character password, 62 symbols", 62 ** 8)]:
    print(f"{name:34s} {n:>16,}  = {bits(n):5.1f} bits")

# with 10 tries before the phone wipes, the chance of guessing a random 6 digit PIN
print(f"\nchance to guess a random 6 digit PIN in 10 tries: {10 / 10 ** 6:.5%}")
# but people pick patterns: in studies, a large share start in the top left corner and use few dots
print("real choices are far from random, so avoid birthdays, 123456 and simple L or Z patterns")
