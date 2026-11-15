# 2.3 Diffie-Hellman, ElGamal and the discrete logarithm
# Example "dlog_bsgs" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The discrete log: brute force against baby step giant step
from math import isqrt

def brute_force(g, h, p):
    value, x = 1, 0
    while value != h:
        value = value * g % p
        x = x + 1
    return x

def baby_giant(g, h, p, n):              # n = order of g
    m = isqrt(n) + 1
    table = {}
    value = 1
    for j in range(m):                   # baby steps: g^j
        table[value] = j
        value = value * g % p
    step = pow(g, -m, p)                 # g^(-m)
    y = h
    for i in range(m):                   # giant steps: h * g^(-m i)
        if y in table:
            return i * m + table[y]
        y = y * step % p
    return None

p, g = 101, 2
print("2^x = 48 mod 101: brute force", brute_force(g, 48, p), " BSGS", baby_giant(g, 48, p, 100))

# A 41 bit safe prime p = 2q + 1. g = 4 has prime order q.
p = 1099511628443
q = (p - 1) // 2
g = 4
secret = 123456789012
h = pow(g, secret, p)
x = baby_giant(g, h, p, q)
print("41 bit group: found x =", x, "correct:", x == secret)
print("about", 2 * (isqrt(q) + 1), "steps instead of up to", q)
print("for a 2048 bit group the same method needs about 2^1024 steps")
