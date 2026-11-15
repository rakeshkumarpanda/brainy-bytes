# 2.3 Diffie-Hellman, ElGamal and the discrete logarithm
# Example "pohlig_hellman" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Pohlig-Hellman: a discrete log is easy when p - 1 has only small prime factors
import random

p = 8608456956238879741                  # a 63 bit prime, and p - 1 is "smooth"
factors = [4, 3, 5, 49, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]   # prime powers whose product is p - 1
n = p - 1
check = 1
for f in factors:
    check = check * f
print("p - 1 is the product of the list:", check == n)

def is_generator(g):
    for r in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47):
        if pow(g, n // r, p) == 1:
            return False
    return True

g = 2
while not is_generator(g):
    g = g + 1
rng = random.Random(1)
secret = rng.randrange(2, n)
h = pow(g, secret, p)

# Solve x mod f in the small subgroup of size f, for each prime power f
remainders = []
for f in factors:
    g_small = pow(g, n // f, p)          # has order f
    h_small = pow(h, n // f, p)          # equals g_small ^ (x mod f)
    x_small = 0
    while pow(g_small, x_small, p) != h_small:
        x_small = x_small + 1            # at most f tries, f is tiny
    remainders.append(x_small)

# Join the small answers with the Chinese remainder theorem
x = 0
for r, f in zip(remainders, factors):
    Mi = n // f
    x = x + r * Mi * pow(Mi, -1, f)
x = x % n
print("generator g =", g, "| recovered the 63 bit secret:", x == secret)
print("work: about", sum(factors), "small steps. A safe prime of this size would need about 2^31.")
