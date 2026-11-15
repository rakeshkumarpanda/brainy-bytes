# 2.2 RSA: keys, proofs, signatures and attacks
# Example "rsa_proof_check" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Check RSA correctness for EVERY message, including ones that share a factor with n
from math import gcd, lcm

p, q, e = 5, 11, 3
n = p * q
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
print("n =", n, " phi =", phi, " e =", e, " d =", d)

works = 0
shared = []
for m in range(n):
    if pow(pow(m, e, n), d, n) == m:
        works = works + 1
    if gcd(m, n) != 1:
        shared.append(m)
print("messages that come back:", works, "of", n)
print("messages sharing a factor with n:", shared)
print("they still come back, for example 15 ->", pow(15, e, n), "->", pow(pow(15, e, n), d, n))

# The smaller exponent from the Carmichael function works as well
lam = lcm(p - 1, q - 1)
d_small = pow(e, -1, lam)
ok = all(pow(pow(m, e, n), d_small, n) == m for m in range(n))
print("lambda(n) =", lam, " d mod lambda =", d_small, " works for all:", ok)

# Why gcd(e, phi) must be 1: with e = 5 two messages share a ciphertext
e_bad = 5
seen = {}
for m in range(n):
    c = pow(m, e_bad, n)
    if c in seen:
        print("e = 5 is useless here:", seen[c], "and", m, "both encrypt to", c)
        break
    seen[c] = m
