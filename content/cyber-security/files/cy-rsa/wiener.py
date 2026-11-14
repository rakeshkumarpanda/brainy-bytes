# 2.2 RSA: keys, proofs, signatures and attacks
# Example "wiener" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Wiener's attack: a small private exponent d falls out of the continued fraction of e / n
import random
from math import gcd, isqrt

def continued_fraction(a, b):            # the terms of a / b
    terms = []
    while b != 0:
        terms.append(a // b)
        a, b = b, a % b
    return terms

def convergents(terms):                  # the fractions k / d that the terms build, one by one
    h0, h1 = 0, 1
    k0, k1 = 1, 0
    for t in terms:
        h0, h1 = h1, t * h1 + h0
        k0, k1 = k1, t * k1 + k0
        yield h1, k1

def wiener(n, e):
    for k, d in convergents(continued_fraction(e, n)):
        if k == 0 or (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k           # a guess for phi(n)
        s = n - phi + 1                  # would be p + q
        disc = s * s - 4 * n             # (p - q)^2
        if disc >= 0 and isqrt(disc) ** 2 == disc:
            r = isqrt(disc)
            return d, (s + r) // 2, (s - r) // 2
    return None

print("small example:", wiener(90581, 17993))

# A 1024 bit key with a 200 bit private exponent: far too small
rng = random.Random(7)                   # toy demo only. Real keys use the secrets module.

def is_prime(n):
    if n % 2 == 0:
        return n == 2
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for j in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True

def prime(bits):
    while True:
        p = rng.getrandbits(bits) | (3 << (bits - 2)) | 1
        if is_prime(p):
            return p

p, q = prime(512), prime(512)
n, phi = p * q, (p - 1) * (q - 1)
while True:
    d = rng.getrandbits(200) | (1 << 199) | 1
    if gcd(d, phi) == 1:
        break
e = pow(d, -1, phi)                      # e is now huge and looks harmless
found = wiener(n, e)
print("n has", n.bit_length(), "bits, e has", e.bit_length(), "bits")
print("d recovered:", found[0] == d, " factors correct:", found[1] * found[2] == n)
print("terms in the continued fraction of e/n:", len(continued_fraction(e, n)))
