# 1.3 Advanced cryptography: secret sharing, zero knowledge, homomorphic encryption and MPC
# Example "paillier" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Paillier encryption (1999): add numbers while they stay encrypted
import random
from math import gcd, lcm

rng = random.Random(5)                   # repeatable demo. Real keys use the secrets module and 2048 bit n.

def is_prime(n):
    if n < 2 or n % 2 == 0:
        return n == 2
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1) or a % n == 0:
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
        c = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(c):
            return c

p, q = prime(256), prime(256)
n = p * q
n2 = n * n
g = n + 1                                # the standard simple choice
lam = lcm(p - 1, q - 1)
mu = pow(lam, -1, n)                     # works because g = n + 1

def encrypt(m):
    r = rng.randrange(1, n)
    while gcd(r, n) != 1:
        r = rng.randrange(1, n)
    return pow(g, m, n2) * pow(r, n, n2) % n2

def decrypt(c):
    L = (pow(c, lam, n2) - 1) // n
    return L * mu % n

salaries = [52000, 61000, 48500, 70500]
encrypted = [encrypt(s) for s in salaries]
total = 1
for c in encrypted:
    total = total * c % n2               # multiplying ciphertexts ADDS the hidden numbers
print("sum computed on encrypted data:", decrypt(total), "| real sum:", sum(salaries))
print("times 3 without decrypting:", decrypt(pow(encrypted[0], 3, n2)), "=", 3 * salaries[0])
print("same salary encrypts differently:", encrypt(52000) != encrypt(52000))
